#!/usr/bin/env python3
"""
train_l1m2_multigeometry.py —— 1C-L1M2 多几何 OCS 主线训练

派生自 train_b6_circular_regression.py。复用：
  - 同容量 ImageEncoder / OCSEncoder
  - 4D circular regression 输出头 [yaw_sin,yaw_cos,pitch_sin,pitch_cos]
  - sin/cos MSE + 单位范数惩罚；circular MAE 指标；final + best-val 双口径

L1M2 改造：
  - OCS 输入 = 多几何总光度向量（维度 = group 几何数 1/3/5），非 4D per-part
  - split = P-INT（按 pitch 分层随机，插值/局部泛化），P-EXT 作为对照接口
  - 保存 R114 §8 置信一致性中间量：
      per-attitude predictions、top-k 候选、posterior-like score、entropy、margin
    posterior-like 在训练姿态网格上用预测角度到候选网格的 circular 距离构造，
    是工程候选分数，非真实 Bayesian posterior。

用法：
  python train_l1m2_multigeometry.py --train --geom-group G3 --mode ocs_only \
      --protocol P-INT --seed 42 --max-epochs 30
"""

import argparse
import copy
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from dataset_l1m2_multigeometry import (  # noqa: E402
    GEOM_GROUPS, build_multigeometry_table,
    fit_flux_transform, L1M2Dataset,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_OUTDIR = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
MAX_EPOCHS_HARD = 30
N_YAW, N_PITCH = 72, 37
YAW_STEP, PITCH_STEP = 5.0, 5.0


# ═══════ 编码器（沿用 B6 容量）═══════
class ImageEncoder(nn.Module):
    def __init__(self, in_channels=1, out_dim=256):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, 32, 4, 2, 1), nn.BatchNorm2d(32), nn.ReLU(True),
            nn.Conv2d(32, 64, 4, 2, 1), nn.BatchNorm2d(64), nn.ReLU(True),
            nn.Conv2d(64, 128, 4, 2, 1), nn.BatchNorm2d(128), nn.ReLU(True),
            nn.Conv2d(128, 256, 4, 2, 1), nn.BatchNorm2d(256), nn.ReLU(True),
            nn.Conv2d(256, 256, 4, 2, 1), nn.BatchNorm2d(256), nn.ReLU(True),
            nn.Conv2d(256, 256, 4, 2, 1), nn.BatchNorm2d(256), nn.ReLU(True),
        )
        self.fc = nn.Linear(256 * 4 * 4, out_dim)

    def forward(self, x):
        return self.fc(self.conv(x).view(x.size(0), -1))


class OCSEncoder(nn.Module):
    def __init__(self, in_dim, hidden=128, out_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(True),
            nn.Linear(hidden, hidden), nn.ReLU(True),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.net(x)


class L1M2RegModel(nn.Module):
    def __init__(self, mode, ocs_dim):
        super().__init__()
        self.mode = mode
        if mode in ("image_only", "joint"):
            self.image_encoder = ImageEncoder(1, 256)
        if mode in ("ocs_only", "joint"):
            self.ocs_encoder = OCSEncoder(ocs_dim, 128, 128)
        dims = {"image_only": 256, "ocs_only": 128, "joint": 384}
        self.head = nn.Linear(dims[mode], 4)

    def forward(self, batch):
        feats = []
        if self.mode in ("image_only", "joint"):
            feats.append(self.image_encoder(batch["image"]))
        if self.mode in ("ocs_only", "joint"):
            feats.append(self.ocs_encoder(batch["ocs"]))
        return torch.tanh(self.head(torch.cat(feats, dim=1)))


# ═══════ target / decode / loss / metrics（沿用 B6）═══════
def make_targets(yaw_deg, pitch_deg, device):
    yr = torch.deg2rad(yaw_deg.float()); pr = torch.deg2rad(pitch_deg.float())
    return torch.stack([torch.sin(yr), torch.cos(yr),
                        torch.sin(pr), torch.cos(pr)], dim=1).to(device)


def reg_loss(pred, target, norm_weight=0.1):
    mse = nn.functional.mse_loss(pred, target)
    yn = pred[:, 0] ** 2 + pred[:, 1] ** 2
    pn = pred[:, 2] ** 2 + pred[:, 3] ** 2
    norm_pen = ((yn - 1.0) ** 2 + (pn - 1.0) ** 2).mean()
    return mse + norm_weight * norm_pen


def decode_angles(pred):
    ys, yc, ps, pc = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    yaw = np.degrees(np.arctan2(ys, yc)) % 360.0
    pitch = np.clip(np.degrees(np.arctan2(ps, pc)), -90.0, 90.0)
    return yaw, pitch


def yaw_circ_err(pred, true):
    d = np.abs(pred - true) % 360.0
    return np.minimum(d, 360.0 - d)


def nearest_yaw_bin(y):
    return (np.round(y / YAW_STEP).astype(int)) % N_YAW


def nearest_pitch_bin(p):
    return np.clip(np.round((p + 90.0) / PITCH_STEP).astype(int), 0, N_PITCH - 1)


def compute_metrics(yp, pp, yt, pt):
    yce = yaw_circ_err(yp, yt); pae = np.abs(pp - pt)
    c45 = (np.floor((yp % 360) / 45.0) == np.floor((yt % 360) / 45.0))
    c90 = (np.floor((yp % 360) / 90.0) == np.floor((yt % 360) / 90.0))
    ypb, ytb = nearest_yaw_bin(yp), nearest_yaw_bin(yt)
    ybd = np.abs(ypb - ytb); ybc = np.minimum(ybd, N_YAW - ybd)
    return {
        "n": int(len(yp)),
        "yaw_circular_mae_deg": float(yce.mean()),
        "yaw_median_ae_deg": float(np.median(yce)),
        "yaw_p90_ae_deg": float(np.percentile(yce, 90)),
        "yaw_hit@5": float((yce <= 5).mean()),
        "yaw_hit@10": float((yce <= 10).mean()),
        "yaw_hit@30": float((yce <= 30).mean()),
        "yaw_coarse45_acc": float(c45.mean()),
        "yaw_coarse90_acc": float(c90.mean()),
        "yaw_within_1bin_sentinel": float((ybc <= 1).mean()),
        "pitch_mae_deg": float(pae.mean()),
        "pitch_median_ae_deg": float(np.median(pae)),
        "pitch_hit@5": float((pae <= 5).mean()),
        "pitch_hit@10": float((pae <= 10).mean()),
    }


# ═══════ posterior-like / 置信中间量 ═══════
def build_candidate_grid():
    """训练姿态网格的候选 (yaw,pitch)。72×37。"""
    yaws = np.arange(0, 360, 5).astype(float)
    pitches = np.arange(-90, 91, 5).astype(float)
    grid = np.array([(y, p) for y in yaws for p in pitches])  # [2664,2]
    return grid


def posterior_like_scores(yaw_pred, pitch_pred, grid, tau_yaw=20.0, tau_pitch=20.0):
    """用预测角到候选网格的 circular 距离构造 softmax 候选分布。

    这是【工程候选分数】，非真实 Bayesian posterior。
    返回: scores [N, G], top-k idx, entropy, margin。
    """
    gy = grid[:, 0][None, :]   # [1,G]
    gp = grid[:, 1][None, :]
    yp = yaw_pred[:, None]; pp = pitch_pred[:, None]
    dy = np.abs(yp - gy) % 360.0
    dy = np.minimum(dy, 360.0 - dy)
    dp = np.abs(pp - gp)
    # 负距离平方 -> softmax
    logits = -((dy / tau_yaw) ** 2 + (dp / tau_pitch) ** 2)
    logits -= logits.max(axis=1, keepdims=True)
    ex = np.exp(logits)
    scores = ex / ex.sum(axis=1, keepdims=True)   # [N,G]
    # entropy
    ent = -(scores * np.log(scores + 1e-12)).sum(axis=1)
    # top-k
    order = np.argsort(-scores, axis=1)
    top5 = order[:, :5]
    s_sorted = np.take_along_axis(scores, order, axis=1)
    margin = s_sorted[:, 0] - s_sorted[:, 1]
    return scores, top5, ent, margin


@torch.no_grad()
def collect_predictions(model, loader, device):
    model.eval()
    preds, yt, pt, rids = [], [], [], []
    for b in loader:
        bd = {}
        if "image" in b:
            bd["image"] = b["image"].to(device)
        if "ocs" in b:
            bd["ocs"] = b["ocs"].to(device)
        out = model(bd)
        preds.append(out.cpu().numpy())
        yt.append(b["yaw_deg"].numpy()); pt.append(b["pitch_deg"].numpy())
        rids.extend(list(b["record_id"]))
    preds = np.concatenate(preds, 0)
    yt = np.concatenate(yt, 0); pt = np.concatenate(pt, 0)
    yp, pp = decode_angles(preds)
    return yp, pp, yt, pt, rids


def evaluate(model, loader, device):
    yp, pp, yt, pt, _ = collect_predictions(model, loader, device)
    return compute_metrics(yp, pp, yt, pt)


def train_one_epoch(model, loader, opt, device, nw):
    model.train(); tot, nb = 0.0, 0
    for b in loader:
        bd = {}
        if "image" in b and model.mode in ("image_only", "joint"):
            bd["image"] = b["image"].to(device)
        if "ocs" in b and model.mode in ("ocs_only", "joint"):
            bd["ocs"] = b["ocs"].to(device)
        target = make_targets(b["yaw_deg"], b["pitch_deg"], device)
        out = model(bd); loss = reg_loss(out, target, nw)
        opt.zero_grad(); loss.backward(); opt.step()
        tot += loss.item(); nb += 1
    return tot / nb


# ═══════ P-INT split（按 pitch 分层随机）═══════
def split_pint(table, train_ratio=0.8, val_ratio=0.1, seed=42):
    rng = np.random.default_rng(seed)
    bins = {}
    for r in table:
        bins.setdefault(round(r["pitch_deg"], 3), []).append(r)
    tr, va, te = [], [], []
    for _, recs in sorted(bins.items()):
        idx = rng.permutation(len(recs))
        nt = max(1, int(len(recs) * train_ratio))
        nv = max(1, int(len(recs) * val_ratio))
        tr += [recs[i] for i in idx[:nt]]
        va += [recs[i] for i in idx[nt:nt + nv]]
        te += [recs[i] for i in idx[nt + nv:]]
    rng.shuffle(tr); rng.shuffle(va); rng.shuffle(te)
    return tr, va, te


def split_pext(table, train_ratio=0.8, val_ratio=0.1):
    """P-EXT yaw-block strict extrapolation：yaw 连续块切分（边界 stress test 对照）。

    与 single-frame B6 同口径：train/val/test 取互斥连续 yaw 弧段。
    """
    yaws = sorted(set(round(r["yaw_deg"], 3) for r in table))
    n = len(yaws)
    nt = max(1, int(n * train_ratio))
    nv = max(1, int(n * val_ratio))
    train_y = set(yaws[:nt]); val_y = set(yaws[nt:nt + nv]); test_y = set(yaws[nt + nv:])
    tr = [r for r in table if round(r["yaw_deg"], 3) in train_y]
    va = [r for r in table if round(r["yaw_deg"], 3) in val_y]
    te = [r for r in table if round(r["yaw_deg"], 3) in test_y]
    return tr, va, te


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="store_true")
    ap.add_argument("--geom-group", choices=["G1", "G3", "G5"], required=True)
    ap.add_argument("--mode", choices=["ocs_only", "image_only", "joint"], required=True)
    ap.add_argument("--protocol", choices=["P-INT", "P-EXT"], default="P-INT")
    ap.add_argument("--max-epochs", type=int, default=30)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--norm-weight", type=float, default=0.1)
    ap.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--smoke-n", type=int, default=200)
    args = ap.parse_args()

    if not args.train:
        print("[BLOCKED] 必须传 --train"); return 1
    if args.max_epochs > MAX_EPOCHS_HARD:
        print(f"[BLOCKED] max-epochs>{MAX_EPOCHS_HARD}"); return 1

    device = torch.device("cuda" if (args.device == "auto" and torch.cuda.is_available())
                          else (args.device if args.device != "auto" else "cpu"))
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    if device.type == "cuda":
        torch.cuda.manual_seed(args.seed)

    # 数据
    table, geoms = build_multigeometry_table(args.geom_group)
    ocs_dim = len(geoms)
    if args.protocol == "P-EXT":
        tr, va, te = split_pext(table)
    else:
        tr, va, te = split_pint(table, seed=args.seed)
    if args.smoke:
        tr, va, te = tr[:args.smoke_n], va[:args.smoke_n], te[:args.smoke_n]

    flux_tf = fit_flux_transform(tr) if args.mode in ("ocs_only", "joint") else None

    run_name = f"{args.protocol}_{args.geom_group}_{args.mode}_seed{args.seed}"
    if args.smoke:
        run_name = "smoke_" + run_name
    run_dir = args.outdir / "runs" / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    use_gpu = device.type == "cuda"
    nw_workers = 4 if (use_gpu and not args.smoke and args.mode != "ocs_only") else 0
    mk = lambda recs, shuf: DataLoader(
        L1M2Dataset(recs, args.mode, flux_tf), batch_size=args.batch_size,
        shuffle=shuf, num_workers=nw_workers, pin_memory=use_gpu)
    train_loader, val_loader, test_loader = mk(tr, True), mk(va, False), mk(te, False)

    model = L1M2RegModel(args.mode, ocs_dim).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = optim.Adam(model.parameters(), lr=args.lr)

    print(f"{'='*64}\nL1M2 | {run_name}")
    print(f"geoms={geoms} ocs_dim={ocs_dim} device={device} params={n_params:,}")
    print(f"train/val/test={len(tr)}/{len(va)}/{len(te)}\n{'='*64}")

    run_config = {
        "task": "1C-L1M2_multigeometry",
        "geom_group": args.geom_group, "geoms": geoms, "ocs_dim": ocs_dim,
        "mode": args.mode, "protocol": args.protocol, "smoke": args.smoke,
        "max_epochs": args.max_epochs, "lr": args.lr, "seed": args.seed,
        "batch_size": args.batch_size, "norm_weight": args.norm_weight,
        "split": "P-INT(pitch-stratified random)" if args.protocol == "P-INT" else "P-EXT",
        "flux_transform": flux_tf,
        "n_train": len(tr), "n_val": len(va), "n_test": len(te),
        "n_params": n_params, "device": str(device),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "note_posterior": "posterior_like = 工程候选分数(softmax of -circular dist^2)，非真实 Bayesian posterior",
    }
    json.dump(run_config, open(run_dir / "run_config.json", "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    log_rows = []
    best_cmae, best_epoch, best_state = float("inf"), -1, None
    t0 = time.time()
    for ep in range(1, args.max_epochs + 1):
        loss = train_one_epoch(model, train_loader, opt, device, args.norm_weight)
        vm = evaluate(model, val_loader, device)
        log_rows.append({"epoch": ep, "train_loss": loss,
                         "val_yaw_cmae_deg": vm["yaw_circular_mae_deg"],
                         "val_pitch_mae_deg": vm["pitch_mae_deg"],
                         "val_yaw_hit@10": vm["yaw_hit@10"]})
        is_best = vm["yaw_circular_mae_deg"] < best_cmae
        if is_best:
            best_cmae = vm["yaw_circular_mae_deg"]; best_epoch = ep
            best_state = copy.deepcopy({k: v.detach().cpu().clone()
                                        for k, v in model.state_dict().items()})
        print(f"  ep{ep:2d} loss={loss:.4f} val_cmae={vm['yaw_circular_mae_deg']:.1f} "
              f"pitch_mae={vm['pitch_mae_deg']:.1f} hit@10={vm['yaw_hit@10']:.3f}"
              f"{'  *best' if is_best else ''}")
    elapsed = time.time() - t0

    with open(run_dir / "train_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(log_rows[0].keys()))
        w.writeheader(); w.writerows(log_rows)

    grid = build_candidate_grid()

    def eval_dump(tag, ckpt):
        vmet = evaluate(model, val_loader, device)
        yp, pp, yt, pt, rids = collect_predictions(model, test_loader, device)
        tmet = compute_metrics(yp, pp, yt, pt)
        for m in (vmet, tmet):
            m["elapsed_s"] = elapsed; m["run"] = run_name
            m["select"] = tag; m["best_epoch"] = best_epoch
            m["geom_group"] = args.geom_group; m["mode"] = args.mode
            m["protocol"] = args.protocol
        json.dump(vmet, open(run_dir / f"metrics_val_{tag}.json", "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
        json.dump(tmet, open(run_dir / f"metrics_test_{tag}.json", "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
        # 置信中间量
        scores, top5, ent, margin = posterior_like_scores(yp, pp, grid)
        yce = yaw_circ_err(yp, yt); pae = np.abs(pp - pt)
        np.savez(run_dir / f"samples_test_{tag}.npz",
                 record_id=np.array(rids),
                 yaw_true_deg=yt, pitch_true_deg=pt,
                 yaw_pred_deg=yp, pitch_pred_deg=pp,
                 yaw_circular_error_deg=yce, pitch_abs_error_deg=pae,
                 geometry_group=np.array([args.geom_group] * len(rids)),
                 mode=np.array([args.mode] * len(rids)),
                 protocol=np.array([args.protocol] * len(rids)),
                 posterior_like_top5_idx=top5,
                 posterior_like_top5_score=np.take_along_axis(
                     scores, top5, axis=1),
                 entropy=ent, margin=margin,
                 candidate_grid=grid)
        with open(run_dir / f"samples_test_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["record_id", "yaw_true_deg", "pitch_true_deg",
                        "yaw_pred_deg", "pitch_pred_deg",
                        "yaw_circular_error_deg", "pitch_abs_error_deg",
                        "geometry_group", "mode", "protocol",
                        "top1_grid_idx", "top1_score", "entropy", "margin"])
            for i in range(len(rids)):
                w.writerow([rids[i], f"{yt[i]:.3f}", f"{pt[i]:.3f}",
                            f"{yp[i]:.3f}", f"{pp[i]:.3f}",
                            f"{yce[i]:.3f}", f"{pae[i]:.3f}",
                            args.geom_group, args.mode, args.protocol,
                            int(top5[i, 0]), f"{scores[i, top5[i,0]]:.5f}",
                            f"{ent[i]:.4f}", f"{margin[i]:.5f}"])
        torch.save({"model_state": model.state_dict(), "run_config": run_config,
                    "select": tag, "best_epoch": best_epoch}, run_dir / ckpt)
        return tmet

    tm_final = eval_dump("final", "checkpoint_final.pt")
    if best_state is not None:
        model.load_state_dict(best_state)
    tm_best = eval_dump("best", "checkpoint_best.pt")

    print(f"\n[TEST final] cmae={tm_final['yaw_circular_mae_deg']:.2f} "
          f"hit@30={tm_final['yaw_hit@30']:.3f} coarse90={tm_final['yaw_coarse90_acc']:.3f} "
          f"pitch_mae={tm_final['pitch_mae_deg']:.2f}")
    print(f"[TEST best ] (ep{best_epoch}) cmae={tm_best['yaw_circular_mae_deg']:.2f} "
          f"hit@30={tm_best['yaw_hit@30']:.3f} coarse90={tm_best['yaw_coarse90_acc']:.3f} "
          f"pitch_mae={tm_best['pitch_mae_deg']:.2f}")
    print(f"[DONE] {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

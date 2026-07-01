#!/usr/bin/env python3
"""
train_l1m3_degraded.py —— R116 子任务 B：M3 degraded 真实性轴训练

派生自 train_l1m2_multigeometry.py。完全复用其 model / split / metrics /
posterior-like / eval_dump 逻辑，只在 dataset 层注入【确定性物理退化】：
  - image_only/joint：对 phase63 图像施加 degrade_l1m3_images.degrade_image
  - ocs_only/joint  ：对多几何总光度向量施加 degrade_flux_vector（仅测光误差）

退化确定性按 record_id 派生种子，train/val/test 复用同一退化观测（模拟固定真实传感条件），
非 B6 train-only 粗增广。flux z-score transform 在【退化后的 train flux】上拟合，避免泄漏。

用法：
  # smoke
  python train_l1m3_degraded.py --train --level degraded-mild --geom-group G5 \
      --mode ocs_only --protocol P-INT --seed 42 --smoke
  # 正式
  python train_l1m3_degraded.py --train --level degraded-mild --geom-group G5 \
      --mode joint --protocol P-INT --seed 42 --max-epochs 30
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
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from dataset_l1m2_multigeometry import build_multigeometry_table, apply_flux_transform  # noqa: E402
from train_l1m2_multigeometry import (  # noqa: E402
    L1M2RegModel, collect_predictions, compute_metrics, make_targets, reg_loss,
    build_candidate_grid, posterior_like_scores, yaw_circ_err,
    split_pint, split_pext, MAX_EPOCHS_HARD,
)
from degrade_l1m3_images import (  # noqa: E402
    DEGRADE_LEVELS, degrade_image, degrade_flux_vector,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_OUTDIR = PROJECT_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" / "degraded"


def fit_flux_transform_degraded(train_recs, params):
    """在【退化后】的 train flux 上拟合 log1p+z-score（防泄漏，用退化后统计）。"""
    X = np.array([degrade_flux_vector(r["flux_vector"], params, r["record_id"])
                  for r in train_recs], dtype=np.float64)
    Xlog = np.log1p(X)
    mean = Xlog.mean(axis=0); std = Xlog.std(axis=0)
    std[std < 1e-8] = 1.0
    return {"method": "log1p_then_zscore_on_degraded", "log1p": True,
            "mean": mean.tolist(), "std": std.tolist(), "n_geom": X.shape[1]}


class DegradedL1M2Dataset(Dataset):
    """多几何 OCS + phase63 图像，注入确定性物理退化。"""

    def __init__(self, records, mode, flux_transform, params):
        self.records = records
        self.mode = mode
        self.flux_transform = flux_transform
        self.params = params
        self._root = PROJECT_ROOT

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        rec = self.records[idx]
        sample = {"record_id": str(rec["record_id"]),
                  "yaw_deg": float(rec["yaw_deg"]),
                  "pitch_deg": float(rec["pitch_deg"])}
        if self.mode in ("ocs_only", "joint"):
            dflux = degrade_flux_vector(rec["flux_vector"], self.params, rec["record_id"])
            ocs = apply_flux_transform(dflux, self.flux_transform)
            sample["ocs"] = torch.from_numpy(ocs)
        if self.mode in ("image_only", "joint"):
            png = self._root / rec["png_path"]
            img = Image.open(png)
            if img.mode != "L":
                img = img.convert("L")
            arr = np.array(img, dtype=np.float32) / 255.0
            deg = degrade_image(arr, self.params, rec["record_id"])
            sample["image"] = torch.from_numpy(deg).unsqueeze(0)
        return sample


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


def evaluate(model, loader, device):
    yp, pp, yt, pt, _ = collect_predictions(model, loader, device)
    return compute_metrics(yp, pp, yt, pt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="store_true")
    ap.add_argument("--level", choices=list(DEGRADE_LEVELS.keys()), required=True)
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
    ap.add_argument("--smoke-epochs", type=int, default=1)
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

    params = DEGRADE_LEVELS[args.level]
    table, geoms = build_multigeometry_table(args.geom_group)
    ocs_dim = len(geoms)
    if args.protocol == "P-EXT":
        tr, va, te = split_pext(table)
    else:
        tr, va, te = split_pint(table, seed=args.seed)
    max_ep = args.smoke_epochs if args.smoke else args.max_epochs
    if args.smoke:
        tr, va, te = tr[:args.smoke_n], va[:args.smoke_n], te[:args.smoke_n]

    # flux transform：clean 用 clean flux；degraded 用退化后 flux 拟合
    flux_tf = None
    if args.mode in ("ocs_only", "joint"):
        if params is None:
            from dataset_l1m2_multigeometry import fit_flux_transform
            flux_tf = fit_flux_transform(tr)
        else:
            flux_tf = fit_flux_transform_degraded(tr, params)

    run_name = f"{args.level}_{args.protocol}_{args.geom_group}_{args.mode}_seed{args.seed}"
    if args.smoke:
        run_name = "smoke_" + run_name
    run_dir = args.outdir / "runs" / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    use_gpu = device.type == "cuda"
    nw_workers = 4 if (use_gpu and not args.smoke and args.mode != "ocs_only") else 0
    mk = lambda recs, shuf: DataLoader(
        DegradedL1M2Dataset(recs, args.mode, flux_tf, params),
        batch_size=args.batch_size, shuffle=shuf,
        num_workers=nw_workers, pin_memory=use_gpu)
    train_loader, val_loader, test_loader = mk(tr, True), mk(va, False), mk(te, False)

    model = L1M2RegModel(args.mode, ocs_dim).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = optim.Adam(model.parameters(), lr=args.lr)

    print(f"{'='*64}\nL1M3-degraded | {run_name}")
    print(f"level={args.level} geoms={geoms} device={device} "
          f"train/val/test={len(tr)}/{len(va)}/{len(te)} epochs={max_ep}\n{'='*64}")

    run_config = {
        "task": "1C-L1M3_degraded", "degrade_level": args.level,
        "degrade_params": params,
        "geom_group": args.geom_group, "geoms": geoms, "ocs_dim": ocs_dim,
        "mode": args.mode, "protocol": args.protocol, "smoke": args.smoke,
        "max_epochs": max_ep, "lr": args.lr, "seed": args.seed,
        "batch_size": args.batch_size, "norm_weight": args.norm_weight,
        "split": "P-INT(pitch-stratified random)" if args.protocol == "P-INT" else "P-EXT",
        "flux_transform": flux_tf, "n_train": len(tr), "n_val": len(va), "n_test": len(te),
        "n_params": n_params, "device": str(device),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "degrade_note": ("确定性物理退化，按 record_id 派生种子，train/val/test 同一退化观测；"
                         "OCS 仅测光误差，不施加图像噪声；非 B6 train-only 增广"),
        "note_posterior": "posterior_like = 工程候选分数，非真实 Bayesian posterior",
    }
    json.dump(run_config, open(run_dir / "run_config.json", "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    log_rows = []
    best_cmae, best_epoch, best_state = float("inf"), -1, None
    t0 = time.time()
    for ep in range(1, max_ep + 1):
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
              f"hit@10={vm['yaw_hit@10']:.3f}{'  *best' if is_best else ''}")
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
            m["elapsed_s"] = elapsed; m["run"] = run_name; m["select"] = tag
            m["best_epoch"] = best_epoch; m["degrade_level"] = args.level
            m["geom_group"] = args.geom_group; m["mode"] = args.mode
            m["protocol"] = args.protocol
        json.dump(vmet, open(run_dir / f"metrics_val_{tag}.json", "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
        json.dump(tmet, open(run_dir / f"metrics_test_{tag}.json", "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
        for split_tag, (yy, ppr, ytt, ptt, rr) in [
                ("test", (yp, pp, yt, pt, rids))]:
            scores, top5, ent, margin = posterior_like_scores(yy, ppr, grid)
            yce = yaw_circ_err(yy, ytt); pae = np.abs(ppr - ptt)
            np.savez(run_dir / f"samples_{split_tag}_{tag}.npz",
                     record_id=np.array(rr), yaw_true_deg=ytt, pitch_true_deg=ptt,
                     yaw_pred_deg=yy, pitch_pred_deg=ppr,
                     yaw_circular_error_deg=yce, pitch_abs_error_deg=pae,
                     geometry_group=np.array([args.geom_group] * len(rr)),
                     mode=np.array([args.mode] * len(rr)),
                     protocol=np.array([args.protocol] * len(rr)),
                     degrade_level=np.array([args.level] * len(rr)),
                     posterior_like_top5_idx=top5,
                     posterior_like_top5_score=np.take_along_axis(scores, top5, axis=1),
                     entropy=ent, margin=margin, candidate_grid=grid)
            with open(run_dir / f"samples_{split_tag}_{tag}.csv", "w", newline="",
                      encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["record_id", "yaw_true_deg", "pitch_true_deg",
                            "yaw_pred_deg", "pitch_pred_deg",
                            "yaw_circular_error_deg", "pitch_abs_error_deg",
                            "geometry_group", "mode", "protocol", "degrade_level",
                            "top1_grid_idx", "top1_score", "entropy", "margin"])
                for i in range(len(rr)):
                    w.writerow([rr[i], f"{ytt[i]:.3f}", f"{ptt[i]:.3f}",
                                f"{yy[i]:.3f}", f"{ppr[i]:.3f}",
                                f"{yce[i]:.3f}", f"{pae[i]:.3f}",
                                args.geom_group, args.mode, args.protocol, args.level,
                                int(top5[i, 0]), f"{scores[i, top5[i,0]]:.5f}",
                                f"{ent[i]:.4f}", f"{margin[i]:.5f}"])
        # 同时补 val samples
        yvp, pvp, yvt, pvt, vrids = collect_predictions(model, val_loader, device)
        vsc, vtop5, vent, vmar = posterior_like_scores(yvp, pvp, grid)
        vyce = yaw_circ_err(yvp, yvt); vpae = np.abs(pvp - pvt)
        np.savez(run_dir / f"samples_val_{tag}.npz",
                 record_id=np.array(vrids), yaw_true_deg=yvt, pitch_true_deg=pvt,
                 yaw_pred_deg=yvp, pitch_pred_deg=pvp,
                 yaw_circular_error_deg=vyce, pitch_abs_error_deg=vpae,
                 geometry_group=np.array([args.geom_group] * len(vrids)),
                 mode=np.array([args.mode] * len(vrids)),
                 protocol=np.array([args.protocol] * len(vrids)),
                 degrade_level=np.array([args.level] * len(vrids)),
                 posterior_like_top5_idx=vtop5,
                 posterior_like_top5_score=np.take_along_axis(vsc, vtop5, axis=1),
                 entropy=vent, margin=vmar, candidate_grid=grid)
        torch.save({"model_state": model.state_dict(), "run_config": run_config,
                    "select": tag, "best_epoch": best_epoch}, run_dir / ckpt)
        return tmet

    tm_final = eval_dump("final", "checkpoint_final.pt")
    if best_state is not None:
        model.load_state_dict(best_state)
    tm_best = eval_dump("best", "checkpoint_best.pt")

    print(f"[TEST final] cmae={tm_final['yaw_circular_mae_deg']:.2f} hit@30={tm_final['yaw_hit@30']:.3f}")
    print(f"[TEST best ] (ep{best_epoch}) cmae={tm_best['yaw_circular_mae_deg']:.2f} hit@30={tm_best['yaw_hit@30']:.3f}")
    print(f"[DONE] {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

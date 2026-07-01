#!/usr/bin/env python3
"""
train_b6_circular_regression.py — 1C-B6 A类同门判据回归与噪声增广

派生自 train_baseline.py（E21）。核心改动：
  - 训练目标由 72-bin / 37-bin exact classification 改为
    continuous/circular regression：输出 4D 向量
      [yaw_sin, yaw_cos, pitch_sin, pitch_cos]
  - loss 为 sin/cos MSE + 单位范数惩罚（regression-only）
  - decode: yaw = atan2(sin,cos) mod 360；pitch = atan2(sin,cos) 裁剪到 [-90,90]
  - exact-bin 仍计算为 sentinel，用于和旧 baseline 对照
  - T1' 受控 train-time 图像 noise/augmentation（仅 train，仅图像通道）

FIX01 (R109) 增量：
  - 增加 best-val checkpoint：以 val_yaw_cmae_deg 最小为主选择指标，
    同时输出 final-epoch 与 best-val 两套 test/val/samples/checkpoint，文件名可区分：
      metrics_{val,test}_{final,best}.json
      samples_test_{final,best}.{npz,csv}
      checkpoint_{final,best}.pt
  - 默认输出目录改为 v0.4_results/10_b6_circular_regression_fix01/（不覆盖 101 fold0 原始结果）

不改 split / 姿态网格 / 几何采样 / backbone 容量 / 不新渲染 / 不做超参搜索。
不覆盖旧 R04/R21/E25/C2/C3 结果链；所有输出写入
  v0.4_results/10_b6_circular_regression_fix01/

用法：
  # smoke (1 epoch, subset)
  python train_b6_circular_regression.py --train --mode image_only --fold 0 \
      --aug none --max-epochs 1 --smoke

  # 正式 fold0
  python train_b6_circular_regression.py --train --mode joint --fold 0 \
      --aug none --max-epochs 20
  python train_b6_circular_regression.py --train --mode joint --fold 0 \
      --aug standard --max-epochs 20

红线：必须传 --train；--max-epochs 硬上限 30；不做超参搜索。
"""

import argparse
import copy
import csv
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code"))

from dataset import OCSImageDataset  # noqa: E402

# ── 路径 ────────────────────────────────────────────────
DEFAULT_SPLIT_DIR = (
    PROJECT_ROOT / "v0.4_results" / "03_training_baseline" / "e25_multifold_yawblock"
)
DEFAULT_OUTDIR = PROJECT_ROOT / "v0.4_results" / "10_b6_circular_regression_fix01"

MAX_EPOCHS_HARD = 30
N_YAW = 72       # 5° bins, circular
N_PITCH = 37     # 5° bins, -90..+90
YAW_STEP = 5.0
PITCH_STEP = 5.0

# T1' 受控增广参数（固定，不搜索）
AUG_PARAMS = {
    "gaussian_sigma": 0.01,
    "brightness_jitter": 0.10,   # ±10%
    "max_shift_px": 2,           # integer shift up to ±2 px
}


# ═══════════════════════════════════════════════════════
# 受控图像增广 transform（仅 train，仅图像通道）
# ═══════════════════════════════════════════════════════

class ControlledImageAug:
    """train-time 受控增广：gaussian noise + brightness jitter + integer shift。

    仅作用于 sample['image']（[1,H,W] float in [0,1]）。OCS 向量不参与。
    val/test 不应使用本 transform。
    """

    def __init__(self, sigma, brightness, max_shift, generator=None):
        self.sigma = sigma
        self.brightness = brightness
        self.max_shift = max_shift
        self.g = generator  # torch.Generator，用于可复现

    def __call__(self, sample):
        img = sample["image"]
        g = self.g
        # brightness jitter
        if self.brightness > 0:
            factor = 1.0 + (torch.rand(1, generator=g).item() * 2 - 1) * self.brightness
            img = img * factor
        # gaussian noise
        if self.sigma > 0:
            noise = torch.randn(img.shape, generator=g) * self.sigma
            img = img + noise
        # integer shift (wrap via roll；目标居中黑背景，2px wrap 影响可忽略)
        if self.max_shift > 0:
            sh = int(torch.randint(-self.max_shift, self.max_shift + 1, (1,), generator=g).item())
            sw = int(torch.randint(-self.max_shift, self.max_shift + 1, (1,), generator=g).item())
            if sh != 0 or sw != 0:
                img = torch.roll(img, shifts=(sh, sw), dims=(1, 2))
        img = img.clamp(0.0, 1.0)
        sample["image"] = img
        return sample


# ═══════════════════════════════════════════════════════
# 模型：编码器沿用 E21；输出头改为 4D 连续回归
# ═══════════════════════════════════════════════════════

class ImageEncoder(nn.Module):
    def __init__(self, in_channels=1, out_dim=256):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, 32, 4, stride=2, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, 4, stride=2, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            nn.Conv2d(64, 128, 4, stride=2, padding=1),
            nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, 4, stride=2, padding=1),
            nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 4, stride=2, padding=1),
            nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 4, stride=2, padding=1),
            nn.BatchNorm2d(256), nn.ReLU(inplace=True),
        )
        self.fc = nn.Linear(256 * 4 * 4, out_dim)

    def forward(self, x):
        return self.fc(self.conv(x).view(x.size(0), -1))


class OCSEncoder(nn.Module):
    def __init__(self, in_dim=4, hidden=128, out_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ReLU(inplace=True),
            nn.Linear(hidden, hidden), nn.ReLU(inplace=True),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.net(x)


class OCSImageRegModel(nn.Module):
    """与 E21 同容量编码器，输出头改为 4D 连续回归 [yaw_sin,yaw_cos,pitch_sin,pitch_cos]。"""

    def __init__(self, mode="joint", ocs_dim=4):
        super().__init__()
        self.mode = mode
        if mode in ("image_only", "joint"):
            self.image_encoder = ImageEncoder(in_channels=1, out_dim=256)
        if mode in ("ocs_only", "joint"):
            self.ocs_encoder = OCSEncoder(in_dim=ocs_dim, hidden=128, out_dim=128)
        dims = {"image_only": 256, "ocs_only": 128, "joint": 384}
        self.head = nn.Linear(dims[mode], 4)

    def forward(self, batch):
        feats = []
        if self.mode in ("image_only", "joint"):
            feats.append(self.image_encoder(batch["image"]))
        if self.mode in ("ocs_only", "joint"):
            feats.append(self.ocs_encoder(batch["ocs"]))
        # tanh 将 sin/cos 输出约束到 [-1,1]，配合单位范数惩罚稳定回归
        out = torch.tanh(self.head(torch.cat(feats, dim=1)))   # [B,4]
        return out


# ═══════════════════════════════════════════════════════
# target / decode / loss
# ═══════════════════════════════════════════════════════

def make_targets(yaw_deg, pitch_deg, device):
    """连续角度 -> [yaw_sin,yaw_cos,pitch_sin,pitch_cos]（float32）。"""
    yr = torch.deg2rad(yaw_deg.float())
    pr = torch.deg2rad(pitch_deg.float())
    return torch.stack([torch.sin(yr), torch.cos(yr),
                        torch.sin(pr), torch.cos(pr)], dim=1).to(device)


def reg_loss(pred, target, norm_weight=0.1):
    """sin/cos MSE + 单位范数惩罚（鼓励 (sin,cos) 落在单位圆上）。"""
    mse = nn.functional.mse_loss(pred, target)
    yaw_norm = pred[:, 0] ** 2 + pred[:, 1] ** 2
    pitch_norm = pred[:, 2] ** 2 + pred[:, 3] ** 2
    norm_pen = ((yaw_norm - 1.0) ** 2 + (pitch_norm - 1.0) ** 2).mean()
    return mse + norm_weight * norm_pen


def decode_angles(pred):
    """[B,4] -> yaw_deg in [0,360), pitch_deg clipped [-90,90]。numpy in/out。"""
    ys, yc, ps, pc = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    yaw = np.degrees(np.arctan2(ys, yc)) % 360.0
    pitch = np.degrees(np.arctan2(ps, pc))
    pitch = np.clip(pitch, -90.0, 90.0)
    return yaw, pitch


# ═══════════════════════════════════════════════════════
# 指标
# ═══════════════════════════════════════════════════════

def yaw_circular_err_deg(pred_deg, true_deg):
    d = np.abs(pred_deg - true_deg) % 360.0
    return np.minimum(d, 360.0 - d)


def nearest_yaw_bin(yaw_deg):
    return (np.round(yaw_deg / YAW_STEP).astype(int)) % N_YAW


def nearest_pitch_bin(pitch_deg):
    return np.clip(np.round((pitch_deg + 90.0) / PITCH_STEP).astype(int), 0, N_PITCH - 1)


def compute_metrics(yaw_pred, pitch_pred, yaw_true, pitch_true):
    """全部基于 decoded 连续角度。返回 dict。"""
    ycerr = yaw_circular_err_deg(yaw_pred, yaw_true)
    perr = np.abs(pitch_pred - pitch_true)

    # sentinel bins
    yp_bin = nearest_yaw_bin(yaw_pred)
    yt_bin = nearest_yaw_bin(yaw_true)
    pp_bin = nearest_pitch_bin(pitch_pred)
    pt_bin = nearest_pitch_bin(pitch_true)
    yaw_bin_diff = np.abs(yp_bin - yt_bin)
    yaw_bin_cdist = np.minimum(yaw_bin_diff, N_YAW - yaw_bin_diff)
    pitch_bin_diff = np.abs(pp_bin - pt_bin)

    # coarse direction
    coarse45_ok = (np.floor((yaw_pred % 360) / 45.0) == np.floor((yaw_true % 360) / 45.0))
    coarse90_ok = (np.floor((yaw_pred % 360) / 90.0) == np.floor((yaw_true % 360) / 90.0))

    return {
        "n": int(len(yaw_pred)),
        "yaw_circular_mae_deg": float(ycerr.mean()),
        "yaw_median_ae_deg": float(np.median(ycerr)),
        "yaw_p75_ae_deg": float(np.percentile(ycerr, 75)),
        "yaw_p90_ae_deg": float(np.percentile(ycerr, 90)),
        "yaw_hit@5": float((ycerr <= 5.0).mean()),
        "yaw_hit@10": float((ycerr <= 10.0).mean()),
        "yaw_hit@30": float((ycerr <= 30.0).mean()),
        "yaw_within_1bin_sentinel": float((yaw_bin_cdist <= 1).mean()),
        "yaw_within_2bin_sentinel": float((yaw_bin_cdist <= 2).mean()),
        "yaw_within_6bin_sentinel": float((yaw_bin_cdist <= 6).mean()),
        "yaw_exact_bin_sentinel": float((yaw_bin_cdist == 0).mean()),
        "yaw_coarse45_acc": float(coarse45_ok.mean()),
        "yaw_coarse90_acc": float(coarse90_ok.mean()),
        "pitch_mae_deg": float(perr.mean()),
        "pitch_median_ae_deg": float(np.median(perr)),
        "pitch_hit@5": float((perr <= 5.0).mean()),
        "pitch_hit@10": float((perr <= 10.0).mean()),
        "pitch_hit@30": float((perr <= 30.0).mean()),
        "pitch_exact_bin_sentinel": float((pitch_bin_diff == 0).mean()),
    }


# ═══════════════════════════════════════════════════════
# 训练 / 评估
# ═══════════════════════════════════════════════════════

@torch.no_grad()
def collect_predictions(model, loader, device):
    model.eval()
    preds, yaw_t, pitch_t, rec_ids = [], [], [], []
    for batch in loader:
        img = batch.get("image")
        ocs = batch.get("ocs")
        bd = {}
        if img is not None:
            bd["image"] = img.to(device)
        if ocs is not None:
            bd["ocs"] = ocs.to(device)
        out = model(bd)
        preds.append(out.cpu().numpy())
        yaw_t.append(batch["yaw_deg"].numpy())
        pitch_t.append(batch["pitch_deg"].numpy())
        rec_ids.extend(list(batch["record_id"]))
    preds = np.concatenate(preds, axis=0)
    yaw_true = np.concatenate(yaw_t, axis=0)
    pitch_true = np.concatenate(pitch_t, axis=0)
    yaw_pred, pitch_pred = decode_angles(preds)
    return yaw_pred, pitch_pred, yaw_true, pitch_true, rec_ids


def evaluate(model, loader, device):
    yaw_pred, pitch_pred, yaw_true, pitch_true, _ = collect_predictions(model, loader, device)
    return compute_metrics(yaw_pred, pitch_pred, yaw_true, pitch_true)


def train_one_epoch(model, loader, optimizer, device, norm_weight):
    model.train()
    total, nb, gns = 0.0, 0, []
    for batch in loader:
        bd = {}
        if "image" in batch and model.mode in ("image_only", "joint"):
            bd["image"] = batch["image"].to(device)
        if "ocs" in batch and model.mode in ("ocs_only", "joint"):
            bd["ocs"] = batch["ocs"].to(device)
        target = make_targets(batch["yaw_deg"], batch["pitch_deg"], device)
        out = model(bd)
        loss = reg_loss(out, target, norm_weight)
        optimizer.zero_grad()
        loss.backward()
        gn = sum(p.grad.data.norm(2).item() ** 2
                 for p in model.parameters() if p.grad is not None) ** 0.5
        gns.append(gn)
        optimizer.step()
        total += loss.item()
        nb += 1
    return {
        "loss": total / nb,
        "grad_norm_mean": float(np.mean(gns)),
        "grad_finite": bool(np.all(np.isfinite(gns))),
        "n_batches": nb,
    }


def main():
    ap = argparse.ArgumentParser(description="1C-B6 circular regression + 受控增广")
    ap.add_argument("--train", action="store_true", help="[REQUIRED] 放行训练")
    ap.add_argument("--mode", choices=["ocs_only", "image_only", "joint"], default="joint")
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--aug", choices=["none", "standard"], default="none")
    ap.add_argument("--max-epochs", type=int, default=20)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--norm-weight", type=float, default=0.1)
    ap.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    ap.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    ap.add_argument("--device", type=str, default="auto")
    ap.add_argument("--num-workers", type=int, default=4)
    ap.add_argument("--smoke", action="store_true",
                    help="subset smoke：train/val/test 各截断到 --smoke-n")
    ap.add_argument("--smoke-n", type=int, default=128)
    args = ap.parse_args()

    if not args.train:
        print("[BLOCKED] 必须传 --train。")
        sys.exit(1)
    if args.max_epochs > MAX_EPOCHS_HARD:
        print(f"[BLOCKED] --max-epochs={args.max_epochs} > {MAX_EPOCHS_HARD}")
        sys.exit(1)

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    use_gpu = device.type == "cuda"
    num_workers = args.num_workers if use_gpu else 0
    pin = use_gpu

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if use_gpu:
        torch.cuda.manual_seed(args.seed)

    manifest = args.split_dir / f"split_manifest_circ_yawblock_fold{args.fold}.json"
    if not manifest.exists():
        print(f"[ERROR] manifest not found: {manifest}")
        sys.exit(2)

    # run 目录
    run_name = f"{args.mode}_fold{args.fold}_aug-{args.aug}"
    if args.smoke:
        run_name = "smoke_" + run_name
    run_dir = args.outdir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    # 增广 transform（仅 train）
    train_transform = None
    if args.aug == "standard":
        g = torch.Generator()
        g.manual_seed(args.seed)
        train_transform = ControlledImageAug(
            AUG_PARAMS["gaussian_sigma"], AUG_PARAMS["brightness_jitter"],
            AUG_PARAMS["max_shift_px"], generator=g)

    train_ds = OCSImageDataset(str(manifest), split="train", mode=args.mode,
                               transform=train_transform)
    val_ds = OCSImageDataset(str(manifest), split="val", mode=args.mode)
    test_ds = OCSImageDataset(str(manifest), split="test", mode=args.mode)

    if args.smoke:
        train_ds = Subset(train_ds, list(range(min(args.smoke_n, len(train_ds)))))
        val_ds = Subset(val_ds, list(range(min(args.smoke_n, len(val_ds)))))
        test_ds = Subset(test_ds, list(range(min(args.smoke_n, len(test_ds)))))

    # smoke 模式 workers=0，避免 Windows 多进程 + Generator 复杂度
    nw = 0 if args.smoke else num_workers
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=nw, pin_memory=pin)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            num_workers=nw, pin_memory=pin)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False,
                             num_workers=nw, pin_memory=pin)

    model = OCSImageRegModel(mode=args.mode).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    print(f"{'='*60}")
    print(f"1C-B6 circular regression | {run_name}")
    print(f"manifest: {manifest.name}")
    print(f"device={device} params={n_params:,} aug={args.aug}")
    print(f"train/val/test = {len(train_ds)}/{len(val_ds)}/{len(test_ds)}")
    print(f"{'='*60}")

    run_config = {
        "task": "1C-B6_circular_regression",
        "mode": args.mode, "fold": args.fold, "aug": args.aug,
        "smoke": args.smoke,
        "max_epochs": args.max_epochs, "lr": args.lr, "seed": args.seed,
        "batch_size": args.batch_size, "norm_weight": args.norm_weight,
        "target": "[yaw_sin,yaw_cos,pitch_sin,pitch_cos]",
        "loss": "sincos_mse + unit_norm_penalty",
        "aug_params": AUG_PARAMS if args.aug == "standard" else None,
        "manifest": str(manifest),
        "n_params": n_params, "device": str(device),
        "n_train": len(train_ds), "n_val": len(val_ds), "n_test": len(test_ds),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    with open(run_dir / "run_config.json", "w", encoding="utf-8") as f:
        json.dump(run_config, f, indent=2, ensure_ascii=False)

    # 训练（含 best-val checkpoint 追踪）
    log_rows = []
    best_val_cmae = float("inf")
    best_epoch = -1
    best_state = None
    t0 = time.time()
    for epoch in range(1, args.max_epochs + 1):
        tr = train_one_epoch(model, train_loader, optimizer, device, args.norm_weight)
        vm = evaluate(model, val_loader, device)
        row = {
            "epoch": epoch, "train_loss": tr["loss"],
            "grad_norm_mean": tr["grad_norm_mean"], "grad_finite": tr["grad_finite"],
            "val_yaw_cmae_deg": vm["yaw_circular_mae_deg"],
            "val_yaw_hit@10": vm["yaw_hit@10"],
            "val_pitch_mae_deg": vm["pitch_mae_deg"],
            "val_yaw_exact_sentinel": vm["yaw_exact_bin_sentinel"],
        }
        log_rows.append(row)
        # best-val 选择：主指标 val_yaw_cmae_deg 最小（并行记录 val_pitch_mae，不参与选择）
        is_best = vm["yaw_circular_mae_deg"] < best_val_cmae
        if is_best:
            best_val_cmae = vm["yaw_circular_mae_deg"]
            best_epoch = epoch
            best_state = copy.deepcopy(
                {k: v.detach().cpu().clone() for k, v in model.state_dict().items()})
        print(f"  ep{epoch:2d}/{args.max_epochs} loss={tr['loss']:.4f} "
              f"grad={tr['grad_norm_mean']:.2f} | "
              f"val_yaw_cmae={vm['yaw_circular_mae_deg']:.1f} "
              f"hit@10={vm['yaw_hit@10']:.3f} "
              f"pitch_mae={vm['pitch_mae_deg']:.1f} "
              f"yaw_exact={vm['yaw_exact_bin_sentinel']:.3f}"
              f"{'  *best' if is_best else ''}")
    elapsed = time.time() - t0

    # train_log.csv
    with open(run_dir / "train_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(log_rows[0].keys()))
        w.writeheader()
        w.writerows(log_rows)

    def eval_and_dump(tag, ckpt_name):
        """评估当前 model 状态并写出 metrics_val_<tag>/metrics_test_<tag>/samples_test_<tag>/checkpoint_<tag>。"""
        vmet = evaluate(model, val_loader, device)
        yp, pp, yt, pt, rids = collect_predictions(model, test_loader, device)
        tmet = compute_metrics(yp, pp, yt, pt)
        vmet["elapsed_s"] = elapsed; vmet["run"] = run_name
        vmet["select"] = tag; vmet["best_epoch"] = best_epoch
        tmet["elapsed_s"] = elapsed; tmet["run"] = run_name
        tmet["select"] = tag; tmet["best_epoch"] = best_epoch
        with open(run_dir / f"metrics_val_{tag}.json", "w", encoding="utf-8") as f:
            json.dump(vmet, f, indent=2, ensure_ascii=False)
        with open(run_dir / f"metrics_test_{tag}.json", "w", encoding="utf-8") as f:
            json.dump(tmet, f, indent=2, ensure_ascii=False)
        # 样本级
        yce = yaw_circular_err_deg(yp, yt)
        pae = np.abs(pp - pt)
        ytb = nearest_yaw_bin(yt); ptb = nearest_pitch_bin(pt)
        ypb = nearest_yaw_bin(yp); ppb = nearest_pitch_bin(pp)
        np.savez(
            run_dir / f"samples_test_{tag}.npz",
            record_id=np.array(rids),
            yaw_true_deg=yt, pitch_true_deg=pt,
            yaw_pred_deg=yp, pitch_pred_deg=pp,
            yaw_true_bin=ytb, pitch_true_bin=ptb,
            yaw_pred_bin_sentinel=ypb, pitch_pred_bin_sentinel=ppb,
            yaw_circular_error_deg=yce, pitch_abs_error_deg=pae,
            fold=np.full(len(rids), args.fold),
            mode=np.array([args.mode] * len(rids)),
            augmentation=np.array([args.aug] * len(rids)),
        )
        with open(run_dir / f"samples_test_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["record_id", "yaw_true_deg", "pitch_true_deg",
                        "yaw_pred_deg", "pitch_pred_deg", "yaw_true_bin", "pitch_true_bin",
                        "yaw_pred_bin_sentinel", "pitch_pred_bin_sentinel",
                        "yaw_circular_error_deg", "pitch_abs_error_deg",
                        "fold", "mode", "augmentation"])
            for i in range(len(rids)):
                w.writerow([rids[i], f"{yt[i]:.3f}", f"{pt[i]:.3f}",
                            f"{yp[i]:.3f}", f"{pp[i]:.3f}",
                            int(ytb[i]), int(ptb[i]), int(ypb[i]), int(ppb[i]),
                            f"{yce[i]:.3f}", f"{pae[i]:.3f}",
                            args.fold, args.mode, args.aug])
        torch.save({"mode": args.mode, "fold": args.fold, "aug": args.aug,
                    "select": tag, "best_epoch": best_epoch,
                    "model_state": model.state_dict(), "run_config": run_config},
                   run_dir / ckpt_name)
        return tmet

    # ── final-epoch 口径（当前 model 即最后一轮权重）──
    test_metrics = eval_and_dump("final", "checkpoint_final.pt")

    # ── best-val 口径（载入 best epoch 权重再评估）──
    if best_state is not None:
        model.load_state_dict(best_state)
    test_metrics_best = eval_and_dump("best", "checkpoint_best.pt")

    print(f"\n[TEST final ] yaw_cmae={test_metrics['yaw_circular_mae_deg']:.2f}deg "
          f"hit@30={test_metrics['yaw_hit@30']:.3f} "
          f"coarse90={test_metrics['yaw_coarse90_acc']:.3f} | "
          f"pitch_mae={test_metrics['pitch_mae_deg']:.2f}")
    print(f"[TEST best  ] (ep{best_epoch}) yaw_cmae={test_metrics_best['yaw_circular_mae_deg']:.2f}deg "
          f"hit@30={test_metrics_best['yaw_hit@30']:.3f} "
          f"coarse90={test_metrics_best['yaw_coarse90_acc']:.3f} | "
          f"pitch_mae={test_metrics_best['pitch_mae_deg']:.2f}")
    print(f"[DONE] {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

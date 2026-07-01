#!/usr/bin/env python3
"""
train_baseline.py —— 1C-E21: 受控 baseline 训练与评估
                   + 1C-E21-FIX01: 严格 yaw_block holdout 支持

训练 ocs_only / image_only / joint 三模式 baseline。

E21 原始用法（random train）：
    python train_baseline.py --train --mode ocs_only --max-epochs 20
    python train_baseline.py --train --mode all --max-epochs 20

FIX01 严格 yaw_block 用法：
    python train_baseline.py --train --mode all --max-epochs 20 \
        --train-split-manifest <yaw_block_manifest> \
        --eval-random-manifest <random_manifest> \
        --outdir <fix01_outdir>

红线：
    - 必须传 --train 才启动训练
    - --max-epochs 硬上限 30
    - 不做大规模超参搜索
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset

# 项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code"))

from dataset import OCSImageDataset  # noqa: E402

# ═══════════════════════════════════════════════════════
# 路径
# ═══════════════════════════════════════════════════════
DEFAULT_SPLIT_RANDOM = str(
    PROJECT_ROOT / "v0.4_results" / "01_fullrun"
    / "postprocess" / "split_manifest.json"
)
DEFAULT_SPLIT_YAWB = str(
    PROJECT_ROOT / "v0.4_results" / "01_fullrun"
    / "postprocess" / "split_manifest_yaw_block.json"
)
DEFAULT_OUTDIR = str(
    PROJECT_ROOT / "v0.4_results" / "03_training_baseline"
    / "e21_controlled_baseline"
)
DEFAULT_OUTDIR_FIX01 = str(
    PROJECT_ROOT / "v0.4_results" / "03_training_baseline"
    / "e21_fix01_yawblock_strict"
)

MAX_EPOCHS_HARD = 30


# ═══════════════════════════════════════════════════════
# 模型定义
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


class OCSImageModel(nn.Module):
    def __init__(self, mode="joint", ocs_dim=4, n_yaw=72, n_pitch=37):
        super().__init__()
        self.mode = mode
        if mode in ("image_only", "joint"):
            self.image_encoder = ImageEncoder(in_channels=1, out_dim=256)
        if mode in ("ocs_only", "joint"):
            self.ocs_encoder = OCSEncoder(in_dim=ocs_dim, hidden=128, out_dim=128)
        dims = {"image_only": 256, "ocs_only": 128, "joint": 384}
        self.predictor = nn.Sequential(
            nn.Linear(dims[mode], n_yaw + n_pitch)
        )

    def forward(self, batch):
        feats = []
        if self.mode in ("image_only", "joint"):
            feats.append(self.image_encoder(batch["image"]))
        if self.mode in ("ocs_only", "joint"):
            feats.append(self.ocs_encoder(batch["ocs"]))
        logits = self.predictor(torch.cat(feats, dim=1))
        yaw_logits = logits[:, :72]
        pitch_logits = logits[:, 72:]
        return yaw_logits, pitch_logits


# ═══════════════════════════════════════════════════════
# 指标
# ═══════════════════════════════════════════════════════

def circular_yaw_mae(yaw_pred, yaw_true, n=72, s=5.0):
    d = (yaw_pred - yaw_true).abs()
    return torch.min(d, n - d).float().mean().item() * s


def compute_all_metrics(yaw_logits, pitch_logits, yaw_true, pitch_true):
    yp = yaw_logits.argmax(dim=1)
    pp = pitch_logits.argmax(dim=1)
    return {
        "yaw_acc": (yp == yaw_true).float().mean().item(),
        "pitch_acc": (pp == pitch_true).float().mean().item(),
        "yaw_circular_mae_deg": circular_yaw_mae(yp, yaw_true),
        "pitch_mae_deg": (pp - pitch_true).abs().float().mean().item() * 5.0,
    }


def per_bin_breakdown(yaw_logits, pitch_logits, yaw_true, pitch_true,
                      n_yaw=72, n_pitch=37):
    """Per-yaw 和 per-pitch 细分统计"""
    yp = yaw_logits.argmax(dim=1).cpu().numpy()
    pp = pitch_logits.argmax(dim=1).cpu().numpy()
    yt = yaw_true.cpu().numpy()
    pt = pitch_true.cpu().numpy()

    per_yaw = {}
    for b in range(n_yaw):
        mask = yt == b
        if mask.sum() > 0:
            diff = np.abs(yp[mask] - b)
            cd = np.minimum(diff, n_yaw - diff) * 5.0
            per_yaw[int(b)] = {
                "n": int(mask.sum()),
                "acc": float((yp[mask] == b).mean()),
                "circular_mae_deg": float(cd.mean()),
            }

    per_pitch = {}
    for b in range(n_pitch):
        mask = pt == b
        if mask.sum() > 0:
            per_pitch[int(b)] = {
                "n": int(mask.sum()),
                "acc": float((pp[mask] == b).mean()),
                "mae_deg": float(np.abs(pp[mask] - b).mean() * 5.0),
            }

    return per_yaw, per_pitch


def confusion_summary(yaw_logits, pitch_logits, yaw_true, pitch_true,
                      n_yaw=72, n_pitch=37):
    """混淆矩阵摘要（top-k 错误统计，避免完整 72×72 矩阵过大）"""
    yp = yaw_logits.argmax(dim=1).cpu().numpy()
    pp = pitch_logits.argmax(dim=1).cpu().numpy()
    yt = yaw_true.cpu().numpy()
    pt = pitch_true.cpu().numpy()

    # Yaw: 每个真实 bin 的 top-3 预测错误
    yaw_top_errors = {}
    for b in range(n_yaw):
        mask = yt == b
        if mask.sum() == 0:
            continue
        preds = yp[mask]
        err_bins = preds[preds != b]
        if len(err_bins) > 0:
            counts = np.bincount(err_bins, minlength=n_yaw)
            top3 = np.argsort(-counts)[:3]
            yaw_top_errors[int(b)] = [
                {"pred_bin": int(p), "count": int(counts[p])}
                for p in top3 if counts[p] > 0
            ]

    pitch_top_errors = {}
    for b in range(n_pitch):
        mask = pt == b
        if mask.sum() == 0:
            continue
        preds = pp[mask]
        err_bins = preds[preds != b]
        if len(err_bins) > 0:
            counts = np.bincount(err_bins, minlength=n_pitch)
            top3 = np.argsort(-counts)[:3]
            pitch_top_errors[int(b)] = [
                {"pred_bin": int(p), "count": int(counts[p])}
                for p in top3 if counts[p] > 0
            ]

    # 标量摘要
    yaw_diff = np.abs(yp - yt)
    yaw_cd = np.minimum(yaw_diff, n_yaw - yaw_diff)
    pitch_diff = np.abs(pp - pt)

    return {
        "yaw_error_bin_distribution": {
            "within_0_bins": int((yaw_cd == 0).sum()),
            "within_1_bin": int((yaw_cd <= 1).sum()),
            "within_3_bins": int((yaw_cd <= 3).sum()),
            "within_5_bins": int((yaw_cd <= 5).sum()),
            "total": int(len(yaw_cd)),
        },
        "pitch_error_bin_distribution": {
            "within_0_bins": int((pitch_diff == 0).sum()),
            "within_1_bin": int((pitch_diff <= 1).sum()),
            "within_3_bins": int((pitch_diff <= 3).sum()),
            "within_5_bins": int((pitch_diff <= 5).sum()),
            "total": int(len(pitch_diff)),
        },
    }


# ═══════════════════════════════════════════════════════
# 数据 overlap 检查 (FIX01)
# ═══════════════════════════════════════════════════════

def check_record_overlap(manifest_path):
    """检查一个 manifest 内 train/val/test 的 record_id 重叠。

    Args:
        manifest_path: split manifest JSON 路径

    Returns:
        dict: overlap 统计，包含 is_strict 布尔值
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    train_ids = set(r["record_id"] for r in manifest.get("train", []))
    val_ids = set(r["record_id"] for r in manifest.get("val", []))
    test_ids = set(r["record_id"] for r in manifest.get("test", []))

    train_val = len(train_ids & val_ids)
    train_test = len(train_ids & test_ids)
    val_test = len(val_ids & test_ids)

    result = {
        "manifest": manifest_path,
        "method": manifest.get("method", "unknown"),
        "train_n": len(train_ids),
        "val_n": len(val_ids),
        "test_n": len(test_ids),
        "train_val_overlap": train_val,
        "train_test_overlap": train_test,
        "val_test_overlap": val_test,
        "train_val_overlap_pct_val": train_val / max(len(val_ids), 1),
        "train_test_overlap_pct_test": train_test / max(len(test_ids), 1),
        "val_test_overlap_pct_test": val_test / max(len(test_ids), 1),
        "is_strict": (train_val == 0 and train_test == 0 and val_test == 0),
    }
    return result


def check_cross_manifest_overlap(manifest_a, manifest_b, label_a="A", label_b="B"):
    """检查两个 manifest 之间的 record_id 重叠。

    Returns:
        dict: 交叉重叠统计
    """
    with open(manifest_a, "r", encoding="utf-8") as f:
        a = json.load(f)
    with open(manifest_b, "r", encoding="utf-8") as f:
        b = json.load(f)

    a_all = set(r["record_id"] for r in (a.get("train", []) + a.get("val", []) + a.get("test", [])))
    b_all = set(r["record_id"] for r in (b.get("train", []) + b.get("val", []) + b.get("test", [])))

    # 重点是：manifest A 的 train 与 manifest B 各 split 的重叠
    a_train_ids = set(r["record_id"] for r in a.get("train", []))
    b_train_ids = set(r["record_id"] for r in b.get("train", []))
    b_val_ids = set(r["record_id"] for r in b.get("val", []))
    b_test_ids = set(r["record_id"] for r in b.get("test", []))

    return {
        f"{label_a}_train ∩ {label_b}_train": len(a_train_ids & b_train_ids),
        f"{label_a}_train ∩ {label_b}_val": len(a_train_ids & b_val_ids),
        f"{label_a}_train ∩ {label_b}_test": len(a_train_ids & b_test_ids),
        f"{label_a}_all ∩ {label_b}_all": len(a_all & b_all),
        f"{label_a}_n_total": len(a_all),
        f"{label_b}_n_total": len(b_all),
    }


def print_overlap_report(overlap):
    """Pretty-print overlap 检查结果"""
    print(f"\n{'='*50}")
    print(f"Record-ID Overlap Check: {overlap['manifest']}")
    print(f"  Method: {overlap['method']}")
    print(f"  Train: {overlap['train_n']}, Val: {overlap['val_n']}, Test: {overlap['test_n']}")
    print(f"  Train & Val:  {overlap['train_val_overlap']} "
          f"({overlap['train_val_overlap_pct_val']*100:.1f}% of val)")
    print(f"  Train & Test: {overlap['train_test_overlap']} "
          f"({overlap['train_test_overlap_pct_test']*100:.1f}% of test)")
    print(f"  Val & Test:   {overlap['val_test_overlap']} "
          f"({overlap['val_test_overlap_pct_test']*100:.1f}% of test)")
    if overlap["is_strict"]:
        print(f"  [PASS] STRICT: train/val/test 无重叠。")
    else:
        print(f"  [FAIL] NON-STRICT: 存在重叠！不可作为严格 holdout 泛化证据。")
    print(f"{'='*50}\n")


# ═══════════════════════════════════════════════════════
# 训练与评估
# ═══════════════════════════════════════════════════════

@torch.no_grad()
def evaluate(model, loader, device):
    """完整评估：返回 metrics dict + 所有 logits/labels（用于后续细分）"""
    model.eval()
    all_yaw_logits, all_pitch_logits = [], []
    all_yaw_true, all_pitch_true = [], []
    total_loss = 0.0
    n_batches = 0
    crit_yaw = nn.CrossEntropyLoss()
    crit_pitch = nn.CrossEntropyLoss()

    for batch in loader:
        batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v
                 for k, v in batch.items()}
        yl, pl = model(batch)
        loss = crit_yaw(yl, batch["yaw_bin"]) + crit_pitch(pl, batch["pitch_bin"])
        total_loss += loss.item()
        n_batches += 1
        all_yaw_logits.append(yl.cpu())
        all_pitch_logits.append(pl.cpu())
        all_yaw_true.append(batch["yaw_bin"].cpu())
        all_pitch_true.append(batch["pitch_bin"].cpu())

    yl = torch.cat(all_yaw_logits)
    pl = torch.cat(all_pitch_logits)
    yt = torch.cat(all_yaw_true)
    pt = torch.cat(all_pitch_true)

    metrics = compute_all_metrics(yl, pl, yt, pt)
    metrics["loss"] = total_loss / n_batches if n_batches else float("inf")
    metrics["n_samples"] = len(yt)

    # Per-bin breakdown
    per_yaw, per_pitch = per_bin_breakdown(yl, pl, yt, pt)
    conf = confusion_summary(yl, pl, yt, pt)

    return metrics, per_yaw, per_pitch, conf


def train_one_epoch(model, loader, optimizer, crit_yaw, crit_pitch, device):
    """单 epoch 训练"""
    model.train()
    total_loss = 0.0
    n_batches = 0
    grad_norms = []

    for batch in loader:
        batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v
                 for k, v in batch.items()}
        yl, pl = model(batch)
        loss = crit_yaw(yl, batch["yaw_bin"]) + crit_pitch(pl, batch["pitch_bin"])

        optimizer.zero_grad()
        loss.backward()

        gnorm = sum(p.grad.data.norm(2).item() ** 2
                    for p in model.parameters() if p.grad is not None) ** 0.5
        grad_norms.append(gnorm)

        grads_ok = all(p.grad is None or torch.isfinite(p.grad).all()
                       for p in model.parameters())
        if not grads_ok:
            print(f"  [WARN] Non-finite gradient at batch {n_batches}")

        optimizer.step()
        total_loss += loss.item()
        n_batches += 1

    return {
        "loss": total_loss / n_batches,
        "grad_norm_mean": float(np.mean(grad_norms)),
        "grad_norm_max": float(np.max(grad_norms)),
        "grad_finite": bool(all(np.isfinite(grad_norms))),
        "n_batches": n_batches,
    }


def run_training(mode, train_ds, val_loaders, test_loaders, device,
                 max_epochs, lr, seed, outdir, num_workers=4, pin_memory=True):
    """完整训练流程"""
    print(f"\n{'='*60}")
    print(f"Training: {mode}")
    print(f"{'='*60}")

    torch.manual_seed(seed)
    np.random.seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed(seed)

    model = OCSImageModel(mode=mode).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Parameters: {n_params:,}")

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True,
                               num_workers=num_workers, pin_memory=pin_memory)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    crit_yaw = nn.CrossEntropyLoss()
    crit_pitch = nn.CrossEntropyLoss()

    history = {"train": [], "val": {}}
    for vname in val_loaders:
        history["val"][vname] = []

    t0 = time.time()
    best_val_acc = 0.0
    best_epoch = 0

    for epoch in range(1, max_epochs + 1):
        train_r = train_one_epoch(model, train_loader, optimizer,
                                  crit_yaw, crit_pitch, device)
        train_r["epoch"] = epoch
        history["train"].append(train_r)

        val_line = f"  Epoch {epoch:2d}/{max_epochs}: train_loss={train_r['loss']:.4f}"
        for vname, vloader in val_loaders.items():
            vmet, _, _, _ = evaluate(model, vloader, device)
            vmet["epoch"] = epoch
            history["val"][vname].append(vmet)
            val_line += (f" | {vname}: loss={vmet['loss']:.4f} "
                         f"yaw_acc={vmet['yaw_acc']:.4f} "
                         f"pitch_acc={vmet['pitch_acc']:.4f}")
            # Track best
            avg_acc = (vmet["yaw_acc"] + vmet["pitch_acc"]) / 2
            if avg_acc > best_val_acc:
                best_val_acc = avg_acc
                best_epoch = epoch

        val_line += f" | grad={train_r['grad_norm_mean']:.1f}"
        print(val_line)

    elapsed = time.time() - t0
    print(f"\n  Best val avg_acc={best_val_acc:.4f} at epoch {best_epoch}")
    print(f"  Elapsed: {elapsed:.1f}s")

    # ── Final evaluation ──
    final_eval = {}
    for vname, vloader in val_loaders.items():
        met, per_yaw, per_pitch, conf = evaluate(model, vloader, device)
        final_eval[f"val_{vname}"] = {
            "metrics": met, "per_yaw": per_yaw,
            "per_pitch": per_pitch, "confusion_summary": conf,
        }

    for tname, tloader in test_loaders.items():
        met, per_yaw, per_pitch, conf = evaluate(model, tloader, device)
        final_eval[f"test_{tname}"] = {
            "metrics": met, "per_yaw": per_yaw,
            "per_pitch": per_pitch, "confusion_summary": conf,
        }

    # ── Checkpoint ──
    ckpt_path = os.path.join(outdir, f"checkpoint_{mode}.pt")
    torch.save({
        "mode": mode, "epoch": max_epochs, "seed": seed,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "history": history,
        "final_eval": final_eval,
    }, ckpt_path)
    ckpt_size_mb = os.path.getsize(ckpt_path) / (1024 * 1024)

    # ── NaN/Inf/过拟合检查 ──
    warnings = []
    final_train_loss = history["train"][-1]["loss"]
    for vname in val_loaders:
        vloss = history["val"][vname][-1]["loss"]
        if vloss > final_train_loss * 2:
            warnings.append(f"{vname} val_loss significantly larger than train_loss — possible overfit")
    if any(not r["grad_finite"] for r in history["train"]):
        warnings.append("non-finite gradients detected during training")

    result = {
        "mode": mode,
        "n_params": n_params,
        "max_epochs": max_epochs,
        "lr": lr, "seed": seed,
        "elapsed_s": elapsed,
        "best_epoch": best_epoch,
        "best_val_avg_acc": best_val_acc,
        "checkpoint_path": ckpt_path,
        "checkpoint_size_mb": ckpt_size_mb,
        "warnings": warnings,
        "final_train_loss": final_train_loss,
        "history": history,
        "final_eval": final_eval,
    }
    return result


def make_infinite(val_ds, max_n=200):
    """创建 val subset（最多 max_n 样本）以避免 val 过慢"""
    n = min(max_n, len(val_ds))
    return Subset(val_ds, list(range(n)))


# ═══════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="1C-E21 / FIX01 受控 baseline 训练与评估",
        epilog="FIX01: 使用 --train-split-manifest 指定训练用 manifest 以进行严格 holdout 评估。"
    )
    parser.add_argument("--train", action="store_true",
                        help="[REQUIRED] 显式放行训练")
    parser.add_argument("--mode", type=str, default="all",
                        choices=["ocs_only", "image_only", "joint", "all"])
    parser.add_argument("--max-epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--split-random", type=str, default=DEFAULT_SPLIT_RANDOM,
                        help="Random split manifest（E21 默认训练源）")
    parser.add_argument("--split-yawb", type=str, default=DEFAULT_SPLIT_YAWB,
                        help="Yaw_block split manifest（E21 补充评估）")
    parser.add_argument("--train-split-manifest", type=str, default=None,
                        help="[FIX01] 训练用 split manifest。指定后，train/val/test "
                             "均使用此 manifest，实现严格 holdout。")
    parser.add_argument("--eval-random-manifest", type=str, default=None,
                        help="[FIX01] 额外评估用 random split manifest")
    parser.add_argument("--eval-yaw-block-manifest", type=str, default=None,
                        help="[FIX01] 额外评估用 yaw_block split manifest")
    parser.add_argument("--outdir", type=str, default=None,
                        help="输出目录（默认：E21 -> e21_controlled_baseline；"
                             "FIX01 -> e21_fix01_yawblock_strict）")
    parser.add_argument("--device", type=str, default="auto",
                        help="设备：auto（自动检测GPU）/ cpu / cuda")
    parser.add_argument("--val-max", type=int, default=500,
                        help="Val/test subset max size (0=full)")
    parser.add_argument("--num-workers", type=int, default=4,
                        help="DataLoader worker 数 (0=单线程, 建议 4-8)")
    parser.add_argument("--skip-overlap-check", action="store_true",
                        help="跳过 record_id overlap 检查")
    args = parser.parse_args()

    if not args.train:
        print("[BLOCKED] 必须传 --train 才启动训练。")
        sys.exit(1)
    if args.max_epochs > MAX_EPOCHS_HARD:
        print(f"[BLOCKED] --max-epochs={args.max_epochs} > {MAX_EPOCHS_HARD}")
        sys.exit(1)

    # ── 设备选择 ──
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    use_gpu = (device.type == "cuda")
    num_workers = args.num_workers if use_gpu else min(args.num_workers, 0)
    pin_memory = use_gpu

    modes = ["ocs_only", "image_only", "joint"] if args.mode == "all" else [args.mode]

    # ── 确定训练协议：FIX01 还是 E21 ──
    is_fix01 = args.train_split_manifest is not None

    # 自动选择输出目录
    if args.outdir is None:
        args.outdir = DEFAULT_OUTDIR_FIX01 if is_fix01 else DEFAULT_OUTDIR

    train_manifest = args.train_split_manifest if is_fix01 else args.split_random

    print(f"{'='*60}")
    print(f"1C-E21{' FIX01' if is_fix01 else ''} Controlled Baseline Training")
    print(f"Protocol: {'STRICT yaw_block holdout' if is_fix01 else 'E21 random train'}")
    print(f"Train manifest: {train_manifest}")
    print(f"Modes: {modes}")
    print(f"Epochs: {args.max_epochs}, LR: {args.lr}, Seed: {args.seed}")
    print(f"Device: {device} (GPU={use_gpu}, workers={num_workers}, pin_memory={pin_memory})")
    print(f"Output: {args.outdir}")
    print(f"{'='*60}")

    # ═══════════════════════════════════════════════════════
    # Overlap 检查
    # ═══════════════════════════════════════════════════════
    overlap_report = {}
    if not args.skip_overlap_check:
        print("\n── Record-ID Overlap 检查 ──")

        # 1. 训练 manifest 内部 overlap
        train_overlap = check_record_overlap(train_manifest)
        print_overlap_report(train_overlap)
        overlap_report["train_manifest"] = train_overlap

        if not train_overlap["is_strict"]:
            print("[WARN] 训练 manifest 内部存在 record_id 重叠！")
            if is_fix01:
                print("[WARN] FIX01 要求严格无重叠 — 请检查 manifest 是否正确。")

        # 2. 交叉重叠：训练 manifest vs 额外评估 manifest
        for eval_label, eval_path in [
            ("random", args.eval_random_manifest or args.split_random),
            ("yaw_block", args.eval_yaw_block_manifest or args.split_yawb),
        ]:
            if eval_path and eval_path != train_manifest:
                cross = check_cross_manifest_overlap(
                    train_manifest, eval_path,
                    label_a="train_manifest", label_b=eval_label,
                )
                overlap_report[f"cross_train_vs_{eval_label}"] = cross
                print(f"  Cross: train_manifest vs {eval_label}:")
                for k, v in cross.items():
                    print(f"    {k}: {v}")

        # 3. 如果额外指定了 eval-random 和 eval-yaw-block，也检查它们的内部 overlap
        for eval_label, eval_path in [
            ("eval_random", args.eval_random_manifest),
            ("eval_yaw_block", args.eval_yaw_block_manifest),
        ]:
            if eval_path:
                eo = check_record_overlap(eval_path)
                overlap_report[eval_label] = eo
                print_overlap_report(eo)
    else:
        print("\n[SKIP] Overlap check skipped (--skip-overlap-check)")

    # ═══════════════════════════════════════════════════════
    # 数据加载
    # ═══════════════════════════════════════════════════════
    os.makedirs(args.outdir, exist_ok=True)

    # 保存 overlap 报告
    overlap_path = os.path.join(args.outdir, "e21_fix01_overlap_report.json")
    with open(overlap_path, "w", encoding="utf-8") as f:
        json.dump(overlap_report, f, indent=2, ensure_ascii=False)
    print(f"Overlap report -> {overlap_path}")

    all_results = {}
    for mode in modes:
        # ── 训练集：从 train_manifest 读取 ──
        train_ds = OCSImageDataset(train_manifest, split="train", mode=mode)

        # ── Val loaders ──
        val_loaders = {}

        # 主 val：始终从 train_manifest 读取（严格 holdout）
        val_loaders["primary"] = DataLoader(
            OCSImageDataset(train_manifest, split="val", mode=mode)
            if args.val_max == 0 else
            make_infinite(OCSImageDataset(train_manifest, split="val", mode=mode),
                          args.val_max),
            batch_size=32, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)

        # 补充 eval：random manifest
        random_eval_path = args.eval_random_manifest or args.split_random
        if random_eval_path and random_eval_path != train_manifest:
            val_loaders["random"] = DataLoader(
                OCSImageDataset(random_eval_path, split="val", mode=mode)
                if args.val_max == 0 else
                make_infinite(OCSImageDataset(random_eval_path, split="val", mode=mode),
                              args.val_max),
                batch_size=32, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)

        # 补充 eval：yaw_block manifest
        yawb_eval_path = args.eval_yaw_block_manifest or args.split_yawb
        if yawb_eval_path and yawb_eval_path != train_manifest:
            val_loaders["yaw_block"] = DataLoader(
                OCSImageDataset(yawb_eval_path, split="val", mode=mode)
                if args.val_max == 0 else
                make_infinite(OCSImageDataset(yawb_eval_path, split="val", mode=mode),
                              args.val_max),
                batch_size=32, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)

        # ── Test loaders ──
        test_loaders = {}

        # 主 test：始终从 train_manifest 读取
        test_loaders["primary"] = DataLoader(
            OCSImageDataset(train_manifest, split="test", mode=mode),
            batch_size=32, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)

        if random_eval_path and random_eval_path != train_manifest:
            test_loaders["random"] = DataLoader(
                OCSImageDataset(random_eval_path, split="test", mode=mode),
                batch_size=32, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)

        if yawb_eval_path and yawb_eval_path != train_manifest:
            test_loaders["yaw_block"] = DataLoader(
                OCSImageDataset(yawb_eval_path, split="test", mode=mode),
                batch_size=32, shuffle=False, num_workers=num_workers, pin_memory=pin_memory)

        print(f"\n  Train: {len(train_ds)} samples (from {Path(train_manifest).name})")
        for vn, vl in val_loaders.items():
            print(f"  Val/{vn}: {len(vl.dataset)} samples")
        for tn, tl in test_loaders.items():
            print(f"  Test/{tn}: {len(tl.dataset)} samples")

        result = run_training(mode, train_ds, val_loaders, test_loaders,
                              device, args.max_epochs, args.lr, args.seed,
                              args.outdir, num_workers=num_workers,
                              pin_memory=pin_memory)
        all_results[mode] = result

    # ── 汇总输出 ──
    print(f"\n{'='*60}")
    print(f"E21{' FIX01' if is_fix01 else ''} Baseline Summary")
    print(f"{'='*60}")

    summary = {}
    for mode, r in all_results.items():
        fe = r["final_eval"]
        sm = {
            "mode": mode,
            "n_params": r["n_params"],
            "elapsed_s": r["elapsed_s"],
            "best_epoch": r["best_epoch"],
            "best_val_avg_acc": r["best_val_avg_acc"],
            "final_train_loss": r["final_train_loss"],
            "checkpoint_mb": r["checkpoint_size_mb"],
            "warnings": r["warnings"],
            "test_metrics": {},
        }
        for tname in fe:
            if tname.startswith("test_"):
                sm["test_metrics"][tname] = fe[tname]["metrics"]

        summary[mode] = sm

        print(f"\n--- {mode} ({r['n_params']:,} params, {r['elapsed_s']:.0f}s) ---")
        if r["warnings"]:
            for w in r["warnings"]:
                print(f"  [WARN] {w}")
        else:
            print("  No training warnings.")
        print(f"  Best val avg_acc: {r['best_val_avg_acc']:.4f} (epoch {r['best_epoch']})")

        for tname, tdata in fe.items():
            if tname.startswith("test_"):
                m = tdata["metrics"]
                conf = tdata["confusion_summary"]
                yaw_within3 = conf["yaw_error_bin_distribution"].get("within_3_bins", 0)
                yaw_total = conf["yaw_error_bin_distribution"].get("total", 1)
                print(f"  {tname}: yaw_acc={m['yaw_acc']:.4f}, "
                      f"pitch_acc={m['pitch_acc']:.4f}, "
                      f"yaw_cmae={m['yaw_circular_mae_deg']:.1f}deg, "
                      f"pitch_mae={m['pitch_mae_deg']:.1f}deg, "
                      f"yaw_within3bins={yaw_within3}/{yaw_total} "
                      f"({100*yaw_within3/max(yaw_total,1):.0f}%)")

    # ── 写入结果 JSON ──
    result_basename = "e21_fix01_baseline_results" if is_fix01 else "e21_baseline_results"
    output_path = os.path.join(args.outdir, f"{result_basename}.json")
    output_data = {
        "task": f"1C-E21{' FIX01' if is_fix01 else ''} controlled baseline training",
        "protocol": "strict_yaw_block_holdout" if is_fix01 else "random_train",
        "train_manifest": train_manifest,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config": {
            "max_epochs": args.max_epochs, "lr": args.lr,
            "seed": args.seed, "device": str(device), "modes": modes,
        },
        "overlap_check": overlap_report,
        "summary": summary,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\nSummary -> {output_path}")

    # Per-mode detailed results
    detail_prefix = "e21_fix01_detail" if is_fix01 else "e21_detail"
    for mode, r in all_results.items():
        detail_path = os.path.join(args.outdir, f"{detail_prefix}_{mode}.json")
        detail = {k: v for k, v in r.items() if k != "history"}
        detail["train_loss_curve"] = [h["loss"] for h in r["history"]["train"]]
        detail["val_loss_curves"] = {
            vname: [h["loss"] for h in r["history"]["val"][vname]]
            for vname in r["history"]["val"]
        }
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump(detail, f, indent=2, ensure_ascii=False)
        print(f"Detail ({mode}) -> {detail_path}")

    print(f"\n[DONE] 1C-E21{' FIX01' if is_fix01 else ''} training complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

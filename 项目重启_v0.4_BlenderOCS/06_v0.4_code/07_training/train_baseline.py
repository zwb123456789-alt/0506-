#!/usr/bin/env python3
"""
train_baseline.py —— 1C-E21: 受控 baseline 训练与评估

训练 ocs_only / image_only / joint 三模式 baseline。
训练数据使用 random split，评估同时覆盖 random split 和 yaw_block split。

使用：
    python train_baseline.py --train --mode ocs_only --max-epochs 20
    python train_baseline.py --train --mode image_only --max-epochs 20
    python train_baseline.py --train --mode joint --max-epochs 20
    python train_baseline.py --train --mode all --max-epochs 20

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
                 max_epochs, lr, seed, outdir):
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

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=0)
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
    parser = argparse.ArgumentParser(description="1C-E21 受控 baseline 训练")
    parser.add_argument("--train", action="store_true",
                        help="[REQUIRED] 显式放行训练")
    parser.add_argument("--mode", type=str, default="all",
                        choices=["ocs_only", "image_only", "joint", "all"])
    parser.add_argument("--max-epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--split-random", type=str, default=DEFAULT_SPLIT_RANDOM)
    parser.add_argument("--split-yawb", type=str, default=DEFAULT_SPLIT_YAWB)
    parser.add_argument("--outdir", type=str, default=DEFAULT_OUTDIR)
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--val-max", type=int, default=500,
                        help="Val/test subset max size (0=full)")
    args = parser.parse_args()

    if not args.train:
        print("[BLOCKED] 必须传 --train 才启动训练。")
        sys.exit(1)
    if args.max_epochs > MAX_EPOCHS_HARD:
        print(f"[BLOCKED] --max-epochs={args.max_epochs} > {MAX_EPOCHS_HARD}")
        sys.exit(1)

    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    modes = ["ocs_only", "image_only", "joint"] if args.mode == "all" else [args.mode]

    print(f"1C-E21 Controlled Baseline Training")
    print(f"Modes: {modes}")
    print(f"Epochs: {args.max_epochs}, LR: {args.lr}, Seed: {args.seed}")
    print(f"Device: {device}")
    print(f"Output: {args.outdir}")

    os.makedirs(args.outdir, exist_ok=True)

    all_results = {}
    for mode in modes:
        # Datasets: train on random split
        train_ds = OCSImageDataset(args.split_random, split="train", mode=mode)

        # Val loaders: random + yaw_block
        val_loaders = {}
        val_loaders["random"] = DataLoader(
            OCSImageDataset(args.split_random, split="val", mode=mode)
            if args.val_max == 0 else
            make_infinite(OCSImageDataset(args.split_random, split="val", mode=mode),
                          args.val_max),
            batch_size=32, shuffle=False, num_workers=0)

        val_loaders["yaw_block"] = DataLoader(
            OCSImageDataset(args.split_yawb, split="val", mode=mode)
            if args.val_max == 0 else
            make_infinite(OCSImageDataset(args.split_yawb, split="val", mode=mode),
                          args.val_max),
            batch_size=32, shuffle=False, num_workers=0)

        # Test loaders: random + yaw_block
        test_loaders = {}
        test_loaders["random"] = DataLoader(
            OCSImageDataset(args.split_random, split="test", mode=mode),
            batch_size=32, shuffle=False, num_workers=0)

        test_loaders["yaw_block"] = DataLoader(
            OCSImageDataset(args.split_yawb, split="test", mode=mode),
            batch_size=32, shuffle=False, num_workers=0)

        print(f"\n  Train: {len(train_ds)} samples")
        for vn, vl in val_loaders.items():
            print(f"  Val/{vn}: {len(vl.dataset)} samples")
        for tn, tl in test_loaders.items():
            print(f"  Test/{tn}: {len(tl.dataset)} samples")

        result = run_training(mode, train_ds, val_loaders, test_loaders,
                              device, args.max_epochs, args.lr, args.seed,
                              args.outdir)
        all_results[mode] = result

    # ── 汇总输出 ──
    print(f"\n{'='*60}")
    print("E21 Baseline Summary")
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

    # ── 写入完整结果 ──
    output_path = os.path.join(args.outdir, "e21_baseline_results.json")
    # Convert history to lighter format for JSON
    output_data = {
        "task": "1C-E21 controlled baseline training",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config": {
            "max_epochs": args.max_epochs, "lr": args.lr,
            "seed": args.seed, "device": str(device), "modes": modes,
        },
        "summary": summary,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\nSummary -> {output_path}")

    # Per-mode detailed results (excluding full history for size)
    for mode, r in all_results.items():
        detail_path = os.path.join(args.outdir, f"e21_detail_{mode}.json")
        detail = {k: v for k, v in r.items() if k != "history"}
        # Convert history to minimal format
        detail["train_loss_curve"] = [h["loss"] for h in r["history"]["train"]]
        detail["val_loss_curves"] = {
            vname: [h["loss"] for h in r["history"]["val"][vname]]
            for vname in r["history"]["val"]
        }
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump(detail, f, indent=2, ensure_ascii=False)
        print(f"Detail ({mode}) -> {detail_path}")

    print(f"\n[DONE] 1C-E21 controlled baseline training complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

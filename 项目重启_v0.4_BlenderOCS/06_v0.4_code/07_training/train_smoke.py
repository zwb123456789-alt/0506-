#!/usr/bin/env python3
"""
train_smoke.py —— 1C-E20: 最小训练 smoke

受控训练 smoke：验证 loss 计算、反向传播、梯度有限性、参数更新、
val 指标。使用 small subset + 1-3 epoch，不生成论文级性能结论。

使用：
    # Default: 3 模式 x 1 epoch, subset=200
    python train_smoke.py --train-smoke

    # Custom
    python train_smoke.py --train-smoke --max-epochs 2 --subset-size 500

红线：
    - 必须传 --train-smoke 才启动训练循环
    - --max-epochs 硬上限 3
    - 不做完整训练、超参搜索
"""

import argparse
import json
import os
import sys
import time
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

# ── 路径 ──────────────────────────────────────────────
DEFAULT_SPLIT = str(
    PROJECT_ROOT / "v0.4_results" / "01_fullrun"
    / "postprocess" / "split_manifest.json"
)
DEFAULT_OUTDIR = str(
    PROJECT_ROOT / "v0.4_results" / "02_training_smoke"
    / "e20_min_train_smoke"
)

# ── 硬上限 ────────────────────────────────────────────
MAX_EPOCHS_HARD = 3
MAX_SUBSET_SIZE = 1024  # 防止误触全量


# ═══════════════════════════════════════════════════════
# 模型（复用 E19 的 ImageEncoder + OCSEncoder + AttitudePredictor）
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
        h = self.conv(x)
        h = h.view(h.size(0), -1)
        return self.fc(h)


class OCSEncoder(nn.Module):
    def __init__(self, in_dim=4, hidden=128, out_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(inplace=True),
            nn.Linear(hidden, hidden),
            nn.ReLU(inplace=True),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.net(x)


class AttitudePredictor(nn.Module):
    def __init__(self, in_dim, n_yaw=72, n_pitch=37):
        super().__init__()
        self.yaw_head = nn.Linear(in_dim, n_yaw)
        self.pitch_head = nn.Linear(in_dim, n_pitch)

    def forward(self, x):
        return self.yaw_head(x), self.pitch_head(x)


class OCSImageModel(nn.Module):
    def __init__(self, mode="joint", ocs_dim=4, n_yaw=72, n_pitch=37):
        super().__init__()
        self.mode = mode
        if mode in ("image_only", "joint"):
            self.image_encoder = ImageEncoder(in_channels=1, out_dim=256)
        if mode in ("ocs_only", "joint"):
            self.ocs_encoder = OCSEncoder(in_dim=ocs_dim, hidden=128, out_dim=128)
        if mode == "joint":
            fusion_dim = 256 + 128
        elif mode == "image_only":
            fusion_dim = 256
        else:
            fusion_dim = 128
        self.predictor = AttitudePredictor(fusion_dim, n_yaw, n_pitch)

    def forward(self, batch):
        features = []
        if self.mode in ("image_only", "joint"):
            features.append(self.image_encoder(batch["image"]))
        if self.mode in ("ocs_only", "joint"):
            features.append(self.ocs_encoder(batch["ocs"]))
        fused = torch.cat(features, dim=1)
        return self.predictor(fused)


# ═══════════════════════════════════════════════════════
# 评估指标（含 circular yaw）
# ═══════════════════════════════════════════════════════

def circular_yaw_error_deg(yaw_pred_bin, yaw_true_bin, n_bins=72, step_deg=5.0):
    """Circular yaw MAE: min(|diff|, n_bins - |diff|) * step_deg"""
    diff = (yaw_pred_bin - yaw_true_bin).abs()
    circular_diff = torch.min(diff, n_bins - diff)
    return (circular_diff.float().mean().item() * step_deg)


def linear_pitch_error_deg(pitch_pred_bin, pitch_true_bin, step_deg=5.0):
    """Linear pitch MAE"""
    return (pitch_pred_bin - pitch_true_bin).abs().float().mean().item() * step_deg


def compute_metrics(yaw_logits, pitch_logits, yaw_true, pitch_true,
                    n_yaw=72, n_pitch=37, step_deg=5.0):
    """返回完整指标 dict"""
    yaw_pred = yaw_logits.argmax(dim=1)
    pitch_pred = pitch_logits.argmax(dim=1)

    yaw_acc = (yaw_pred == yaw_true).float().mean().item()
    pitch_acc = (pitch_pred == pitch_true).float().mean().item()
    yaw_mae_circular = circular_yaw_error_deg(yaw_pred, yaw_true, n_yaw, step_deg)
    pitch_mae = linear_pitch_error_deg(pitch_pred, pitch_true, step_deg)

    return {
        "yaw_acc": yaw_acc,
        "pitch_acc": pitch_acc,
        "yaw_mae_circular_deg": yaw_mae_circular,
        "pitch_mae_deg": pitch_mae,
    }


# ═══════════════════════════════════════════════════════
# 训练 smoke 主函数
# ═══════════════════════════════════════════════════════

def train_smoke_epoch(model, loader, criterion_yaw, criterion_pitch,
                      optimizer, device, epoch_idx):
    """单 epoch 训练 smoke，返回 epoch 级指标和梯度信息"""
    model.train()
    total_loss = 0.0
    total_yaw_loss = 0.0
    total_pitch_loss = 0.0
    n_batches = 0
    grad_norms = []
    param_updates = []  # 记录第一层权重的变化

    # 记录初始参数
    initial_params = {}
    for name, p in model.named_parameters():
        initial_params[name] = p.detach().clone()

    for batch in loader:
        batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v
                 for k, v in batch.items()}

        yaw_logits, pitch_logits = model(batch)

        loss_yaw = criterion_yaw(yaw_logits, batch["yaw_bin"])
        loss_pitch = criterion_pitch(pitch_logits, batch["pitch_bin"])
        loss = loss_yaw + loss_pitch

        optimizer.zero_grad()
        loss.backward()

        # 梯度范数
        total_norm = 0.0
        for p in model.parameters():
            if p.grad is not None:
                total_norm += p.grad.data.norm(2).item() ** 2
        grad_norms.append(total_norm ** 0.5)

        # 检查梯度是否有限
        grads_finite = all(
            p.grad is None or torch.isfinite(p.grad).all()
            for p in model.parameters()
        )

        if not grads_finite:
            print(f"  [WARN] Non-finite gradient at epoch {epoch_idx}, "
                  f"batch {n_batches}")

        optimizer.step()

        total_loss += loss.item()
        total_yaw_loss += loss_yaw.item()
        total_pitch_loss += loss_pitch.item()
        n_batches += 1

    # 参数更新量
    param_update_norms = {}
    for name, p in model.named_parameters():
        if name in initial_params:
            delta = (p.detach() - initial_params[name]).norm().item()
            param_update_norms[name] = delta

    metrics = {
        "loss": total_loss / n_batches if n_batches else float("inf"),
        "loss_yaw": total_yaw_loss / n_batches if n_batches else float("inf"),
        "loss_pitch": total_pitch_loss / n_batches if n_batches else float("inf"),
        "grad_norm_mean": float(np.mean(grad_norms)) if grad_norms else 0.0,
        "grad_norm_max": float(np.max(grad_norms)) if grad_norms else 0.0,
        "grad_norm_min": float(np.min(grad_norms)) if grad_norms else 0.0,
        "grad_finite": all(np.isfinite(grad_norms)) if grad_norms else False,
        "param_update_total": float(sum(param_update_norms.values())),
        "n_batches": n_batches,
    }
    return metrics


@torch.no_grad()
def val_metrics(model, loader, device):
    """计算 val 指标"""
    model.eval()
    all_yaw_logits, all_pitch_logits = [], []
    all_yaw_true, all_pitch_true = [], []

    for batch in loader:
        batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v
                 for k, v in batch.items()}
        yaw_logits, pitch_logits = model(batch)
        all_yaw_logits.append(yaw_logits.cpu())
        all_pitch_logits.append(pitch_logits.cpu())
        all_yaw_true.append(batch["yaw_bin"].cpu())
        all_pitch_true.append(batch["pitch_bin"].cpu())

    yaw_logits = torch.cat(all_yaw_logits)
    pitch_logits = torch.cat(all_pitch_logits)
    yaw_true = torch.cat(all_yaw_true)
    pitch_true = torch.cat(all_pitch_true)

    return compute_metrics(yaw_logits, pitch_logits, yaw_true, pitch_true)


def run_mode_smoke(mode, train_loader, val_loader, device, max_epochs, lr, seed):
    """对单个 mode 执行完整训练 smoke"""
    print(f"\n{'='*60}")
    print(f"Mode: {mode}")
    print(f"{'='*60}")

    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed(seed)

    model = OCSImageModel(mode=mode).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Parameters: {n_params:,}")

    criterion_yaw = nn.CrossEntropyLoss()
    criterion_pitch = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    history = {"train": [], "val": []}

    t0 = time.time()
    for epoch in range(1, max_epochs + 1):
        train_result = train_smoke_epoch(
            model, train_loader, criterion_yaw, criterion_pitch,
            optimizer, device, epoch
        )
        train_result["epoch"] = epoch
        history["train"].append(train_result)

        val_result = val_metrics(model, val_loader, device)
        val_result["epoch"] = epoch
        history["val"].append(val_result)

        print(f"  Epoch {epoch}/{max_epochs}: "
              f"loss={train_result['loss']:.4f} "
              f"(yaw={train_result['loss_yaw']:.4f}, "
              f"pitch={train_result['loss_pitch']:.4f}), "
              f"grad_norm={train_result['grad_norm_mean']:.2f}, "
              f"val_yaw_acc={val_result['yaw_acc']:.4f}, "
              f"val_pitch_acc={val_result['pitch_acc']:.4f}, "
              f"val_yaw_circular_mae={val_result['yaw_mae_circular_deg']:.1f}deg, "
              f"val_pitch_mae={val_result['pitch_mae_deg']:.1f}deg")

    elapsed = time.time() - t0

    # ── Infrastructure checks（硬工程门禁）──
    infrastructure = {
        "loss_finite": bool(all(
            np.isfinite(r["loss"]) for r in history["train"]
        )),
        "grad_finite_all": bool(all(
            r["grad_finite"] for r in history["train"]
        )),
        "param_updated": bool(all(
            r["param_update_total"] > 0 for r in history["train"]
        )),
        "loss_decreasing": bool(history["train"][-1]["loss"] < history["train"][0]["loss"])
            if len(history["train"]) > 1 else None,
        "val_metric_finite": bool(all(
            np.isfinite(v) for v in [
                history["val"][-1].get("yaw_acc", float("nan")),
                history["val"][-1].get("pitch_acc", float("nan")),
                history["val"][-1].get("yaw_mae_circular_deg", float("nan")),
            ]
        )) if history["val"] else False,
    }

    infra_pass = all(
        v if v is not None else True for v in infrastructure.values()
    )

    # ── Performance diagnostics（信息性，不参与 smoke_pass）──
    diagnostics = {}
    if history["val"]:
        diag_yaw_gt = bool(history["val"][-1]["yaw_acc"] > 1.0 / 72)
        diag_pitch_gt = bool(history["val"][-1]["pitch_acc"] > 1.0 / 37)
        diagnostics = {
            "val_yaw_acc_gt_random": diag_yaw_gt,
            "val_pitch_acc_gt_random": diag_pitch_gt,
            "val_yaw_circular_mae_deg": history["val"][-1]["yaw_mae_circular_deg"],
            "val_pitch_mae_deg": history["val"][-1]["pitch_mae_deg"],
            "val_yaw_acc": history["val"][-1]["yaw_acc"],
            "val_pitch_acc": history["val"][-1]["pitch_acc"],
        }

    # ── Performance notes ──
    perf_notes = []
    if diagnostics:
        if not diagnostics.get("val_yaw_acc_gt_random", True):
            perf_notes.append(
                f"yaw_acc ({diagnostics['val_yaw_acc']:.4f}) below random "
                f"baseline (1/72={1/72:.4f}); expected for low-sample CNN smoke"
            )
        if not diagnostics.get("val_pitch_acc_gt_random", True):
            perf_notes.append(
                f"pitch_acc ({diagnostics['val_pitch_acc']:.4f}) below random "
                f"baseline (1/37={1/37:.4f})"
            )
    if len(history["train"]) <= 1:
        perf_notes.append(
            "single-epoch smoke: loss_decreasing=None, "
            "all diagnostics are informational only"
        )
    if history["train"] and history["train"][0].get("n_batches", 0) < 10:
        perf_notes.append("fewer than 10 batches in training; diagnostics are preliminary")

    overall_status = "INFRA_PASS" if infra_pass else "INFRA_FAIL"

    summary = {
        "mode": mode,
        "n_params": n_params,
        "max_epochs": max_epochs,
        "lr": lr,
        "seed": seed,
        "elapsed_s": elapsed,
        "final_train_loss": history["train"][-1]["loss"] if history["train"] else None,
        "final_val_yaw_acc": history["val"][-1]["yaw_acc"] if history["val"] else None,
        "final_val_pitch_acc": history["val"][-1]["pitch_acc"] if history["val"] else None,
        "final_val_yaw_circular_mae_deg": history["val"][-1]["yaw_mae_circular_deg"] if history["val"] else None,
        "final_val_pitch_mae_deg": history["val"][-1]["pitch_mae_deg"] if history["val"] else None,
        "infrastructure_checks": infrastructure,
        "infrastructure_pass": infra_pass,
        "overall_infrastructure_status": overall_status,
        "performance_diagnostics": diagnostics,
        "performance_notes": perf_notes,
        "history": history,
    }

    print(f"\n  Infrastructure checks: {json.dumps(infrastructure, indent=2)}")
    print(f"  Infrastructure PASS: {infra_pass}")
    if diagnostics:
        print(f"  Performance diagnostics: {json.dumps(diagnostics, indent=2)}")
    if perf_notes:
        for note in perf_notes:
            print(f"  Note: {note}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="1C-E20 最小训练 smoke")
    parser.add_argument("--train-smoke", action="store_true",
                        help="[REQUIRED] 显式放行训练 smoke")
    parser.add_argument("--max-epochs", type=int, default=1,
                        help=f"最大 epoch 数 (1-{MAX_EPOCHS_HARD}, default: 1)")
    parser.add_argument("--subset-size", type=int, default=200,
                        help=f"训练子集大小 (max: {MAX_SUBSET_SIZE}, default: 200)")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--modes", type=str, default="image_only,ocs_only,joint",
                        help="逗号分隔的 mode 列表")
    parser.add_argument("--split-manifest", type=str, default=DEFAULT_SPLIT)
    parser.add_argument("--outdir", type=str, default=DEFAULT_OUTDIR)
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()

    # ── 红线检查 ──
    if not args.train_smoke:
        print("[BLOCKED] 必须传 --train-smoke 才启动训练循环。")
        print("当前为 1C-E20 阶段：只允许受控最小训练 smoke。")
        sys.exit(1)

    if args.max_epochs > MAX_EPOCHS_HARD:
        print(f"[BLOCKED] --max-epochs={args.max_epochs} 超过硬上限 "
              f"{MAX_EPOCHS_HARD}。当前不允许多于 {MAX_EPOCHS_HARD} epoch。")
        sys.exit(1)

    if args.subset_size > MAX_SUBSET_SIZE:
        print(f"[BLOCKED] --subset-size={args.subset_size} 超过硬上限 "
              f"{MAX_SUBSET_SIZE}。当前不允许使用这么多样本。")
        sys.exit(1)

    if not os.path.exists(args.split_manifest):
        print(f"[ERROR] Split manifest not found: {args.split_manifest}")
        sys.exit(1)

    # ── Device ──
    if args.device == "cuda" and not torch.cuda.is_available():
        print("[INFO] CUDA not available, using CPU")
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # ── 输出目录 ──
    os.makedirs(args.outdir, exist_ok=True)

    # ── Dataset ──
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    print(f"\nModes to run: {modes}")
    print(f"Epochs: {args.max_epochs}")
    print(f"Subset size (train): {args.subset_size}")
    print(f"Batch size: {args.batch_size}")
    print(f"LR: {args.lr}")
    print(f"Seed: {args.seed}")
    print(f"Output: {args.outdir}")

    # ── 逐 mode 执行 smoke ──
    all_results = {}

    for mode in modes:
        # 每个 mode 独立 dataset（因为 mode 影响 collate 内容）
        train_ds = OCSImageDataset(args.split_manifest, split="train", mode=mode)
        val_ds = OCSImageDataset(args.split_manifest, split="val", mode=mode)

        # Subset（训练集）
        rng = np.random.default_rng(args.seed)
        train_indices = rng.choice(len(train_ds), size=min(args.subset_size, len(train_ds)),
                                   replace=False).tolist()
        train_subset = Subset(train_ds, train_indices)
        val_subset = Subset(val_ds, list(range(min(args.subset_size, len(val_ds)))))

        train_loader = DataLoader(train_subset, batch_size=args.batch_size,
                                  shuffle=True, num_workers=0)
        val_loader = DataLoader(val_subset, batch_size=args.batch_size,
                                shuffle=False, num_workers=0)

        print(f"\n  Train samples: {len(train_subset)}, "
              f"Val samples: {len(val_subset)}")

        result = run_mode_smoke(mode, train_loader, val_loader, device,
                                args.max_epochs, args.lr, args.seed)
        all_results[mode] = result

    # ── 汇总 ──
    print(f"\n{'='*60}")
    print("Smoke Summary")
    print(f"{'='*60}")

    smoke_summary = {}
    for mode, r in all_results.items():
        infra = r["infrastructure_checks"]
        diag = r["performance_diagnostics"]
        smoke_summary[mode] = {
            "infrastructure_pass": r["infrastructure_pass"],
            "overall_infrastructure_status": r["overall_infrastructure_status"],
            "infrastructure_checks": infra,
            "performance_diagnostics": diag,
            "performance_notes": r["performance_notes"],
            "final_loss": r["final_train_loss"],
            "val_yaw_acc": r["final_val_yaw_acc"],
            "val_pitch_acc": r["final_val_pitch_acc"],
            "val_yaw_circular_mae_deg": r["final_val_yaw_circular_mae_deg"],
            "val_pitch_mae_deg": r["final_val_pitch_mae_deg"],
            "elapsed_s": r["elapsed_s"],
            "n_params": r["n_params"],
        }
        infra_status = "[INFRA_PASS]" if r["infrastructure_pass"] else "[INFRA_FAIL]"
        yaw_gt = diag.get("val_yaw_acc_gt_random", None)
        diag_flag = f"yaw_gt_random={yaw_gt}" if yaw_gt is not None else ""
        print(f"\n{infra_status} {mode}: loss={r['final_train_loss']:.4f}, "
              f"yaw_acc={r['final_val_yaw_acc']:.4f}, "
              f"circular_yaw_mae={r['final_val_yaw_circular_mae_deg']:.1f}deg, "
              f"pitch_mae={r['final_val_pitch_mae_deg']:.1f}deg, "
              f"time={r['elapsed_s']:.1f}s, {diag_flag}")
        for note in r["performance_notes"]:
            print(f"         Note: {note}")

    # ── 输出 ──
    output_data = {
        "task": "1C-E20-FIX01 training smoke with separated checks",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config": {
            "max_epochs": args.max_epochs,
            "subset_size": args.subset_size,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "seed": args.seed,
            "device": str(device),
            "modes": modes,
        },
        "smoke_summary": smoke_summary,
        "details": {mode: {k: v for k, v in r.items() if k not in ("history",)}
                    for mode, r in all_results.items()},
    }

    # 精简结果（去掉每个 batch 的详细记录）
    output_path = os.path.join(args.outdir, "e20_smoke_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"\nResults -> {output_path}")

    # 逐 mode 详细 history
    for mode, r in all_results.items():
        hist_path = os.path.join(args.outdir, f"e20_history_{mode}.json")
        with open(hist_path, "w", encoding="utf-8") as f:
            json.dump(r["history"], f, indent=2, ensure_ascii=False)
        print(f"History ({mode}) -> {hist_path}")

    # ── 终检 ──
    all_infra_pass = all(r["infrastructure_pass"] for r in all_results.values())
    if all_infra_pass:
        print(f"\n[DONE] 1C-E20-FIX01 min training smoke: ALL INFRASTRUCTURE PASS")
    else:
        failed = [m for m, r in all_results.items() if not r["infrastructure_pass"]]
        print(f"\n[DONE] 1C-E20-FIX01 min training smoke: INFRA FAILED — {failed}")
    return 0 if all_infra_pass else 1


if __name__ == "__main__":
    sys.exit(main())

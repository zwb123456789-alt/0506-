#!/usr/bin/env python3
"""
train_c2_screening.py — 1C-E32: C2 OCS-only 筛选训练

对 13 个 c2_participant=true 配置进行 5-fold 交叉验证训练。
只使用 enhanced OCS features，不使用图像。

红线：
- 必须传 --train 才启动训练
- 使用预注册的训练协议，不做超参搜索
- 排除 constant_check_1d
- per fold/per config 使用 train-only mean/std 标准化

Author: 1C-E31 C2 preparation
Date: 2026-06-25
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

# 项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from enhanced_ocs_dataset import (
    EnhancedOCSDataset,
    compute_normalization_params,
    load_feature_definitions,
    get_c2_participant_configs,
)
from c2_screening_schema import (
    generate_per_config_result_template,
    generate_c2_summary_template,
)


# ══════════════════════════════════════════════════════════
# 默认配置
# ══════════════════════════════════════════════════════════

DEFAULT_NPZ_PATH = PROJECT_ROOT / "v0.4_results/04_ocs_features/enhanced_ocs_features.npz"
DEFAULT_DEFINITIONS_PATH = PROJECT_ROOT / "v0.4_results/04_ocs_features/feature_definitions.json"
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "v0.4_results/04_ocs_features/feature_extraction_run_summary.json"
DEFAULT_SPLIT_DIR = PROJECT_ROOT / "v0.4_results/03_training_baseline/e25_multifold_yawblock"
DEFAULT_OUTDIR = PROJECT_ROOT / "v0.4_results/05_c2_screening"

N_FOLDS = 5

# ══════════════════════════════════════════════════════════
# C2 训练协议（固定，不可通过 CLI 修改）
# ══════════════════════════════════════════════════════════
C2_FIXED_PROTOCOL = {
    "max_epochs": 30,
    "hidden_dim": 128,
    "lr": 1e-3,
    "batch_size": 32,
    "seed": 42,
    "optimizer": "Adam",
    "model_type": "MLP_3layer",
    "n_layers": 3,
}

# 说明：C2 筛选使用固定协议，不做超参搜索。
# 这些参数不得在正式训练时通过命令行修改。


# ══════════════════════════════════════════════════════════
# MLP 模型定义
# ══════════════════════════════════════════════════════════

class OCSOnlyMLP(nn.Module):
    """
    OCS-only MLP for yaw/pitch prediction.

    Architecture: input -> hidden -> hidden -> output
    Output: n_yaw + n_pitch logits
    """

    def __init__(self, in_dim: int, hidden_dim: int = 128, n_yaw: int = 72, n_pitch: int = 37):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, n_yaw + n_pitch),
        )
        self.n_yaw = n_yaw
        self.n_pitch = n_pitch

    def forward(self, x):
        """
        Args:
            x: (batch, in_dim) OCS features

        Returns:
            yaw_logits: (batch, n_yaw)
            pitch_logits: (batch, n_pitch)
        """
        logits = self.net(x)
        yaw_logits = logits[:, :self.n_yaw]
        pitch_logits = logits[:, self.n_yaw:]
        return yaw_logits, pitch_logits


# ══════════════════════════════════════════════════════════
# 训练与评估
# ══════════════════════════════════════════════════════════

def circular_yaw_mae(yaw_pred, yaw_true, n=72, step_deg=5.0):
    """计算循环 yaw MAE（度数）"""
    d = (yaw_pred - yaw_true).abs()
    return torch.min(d, n - d).float().mean().item() * step_deg


def compute_metrics(yaw_logits, pitch_logits, yaw_true, pitch_true, n_yaw=72, n_pitch=37):
    """
    计算评估指标，包含 C2 判据所需的 within_k 指标

    Returns:
        dict with keys:
            - yaw_acc, pitch_acc
            - yaw_circular_mae_deg, pitch_mae_deg
            - yaw_correct_count, pitch_correct_count
            - yaw_within_1_bin_count, yaw_within_1_bin_rate
            - yaw_within_3_bins_count, yaw_within_3_bins_rate
            - yaw_within_5_bins_count, yaw_within_5_bins_rate
            - pitch_within_1_bin_count, pitch_within_1_bin_rate
            - pitch_within_3_bins_count, pitch_within_3_bins_rate
            - pitch_within_5_bins_count, pitch_within_5_bins_rate
    """
    yp = yaw_logits.argmax(dim=1)
    pp = pitch_logits.argmax(dim=1)

    n_samples = len(yaw_true)

    # Yaw: circular distance
    yaw_diff = (yp - yaw_true).abs()
    yaw_circular_dist = torch.min(yaw_diff, n_yaw - yaw_diff)

    # Pitch: linear distance
    pitch_diff = (pp - pitch_true).abs()

    # Yaw metrics
    yaw_correct = (yaw_circular_dist == 0)
    yaw_within_1 = (yaw_circular_dist <= 1)
    yaw_within_3 = (yaw_circular_dist <= 3)
    yaw_within_5 = (yaw_circular_dist <= 5)

    # Pitch metrics
    pitch_correct = (pitch_diff == 0)
    pitch_within_1 = (pitch_diff <= 1)
    pitch_within_3 = (pitch_diff <= 3)
    pitch_within_5 = (pitch_diff <= 5)

    return {
        # Accuracy
        "yaw_acc": yaw_correct.float().mean().item(),
        "pitch_acc": pitch_correct.float().mean().item(),

        # MAE
        "yaw_circular_mae_deg": yaw_circular_dist.float().mean().item() * 5.0,
        "pitch_mae_deg": pitch_diff.float().mean().item() * 5.0,

        # Correct counts
        "yaw_correct_count": int(yaw_correct.sum().item()),
        "pitch_correct_count": int(pitch_correct.sum().item()),

        # Within-k bins (yaw)
        "yaw_within_1_bin_count": int(yaw_within_1.sum().item()),
        "yaw_within_1_bin_rate": yaw_within_1.float().mean().item(),
        "yaw_within_3_bins_count": int(yaw_within_3.sum().item()),
        "yaw_within_3_bins_rate": yaw_within_3.float().mean().item(),
        "yaw_within_5_bins_count": int(yaw_within_5.sum().item()),
        "yaw_within_5_bins_rate": yaw_within_5.float().mean().item(),

        # Within-k bins (pitch)
        "pitch_within_1_bin_count": int(pitch_within_1.sum().item()),
        "pitch_within_1_bin_rate": pitch_within_1.float().mean().item(),
        "pitch_within_3_bins_count": int(pitch_within_3.sum().item()),
        "pitch_within_3_bins_rate": pitch_within_3.float().mean().item(),
        "pitch_within_5_bins_count": int(pitch_within_5.sum().item()),
        "pitch_within_5_bins_rate": pitch_within_5.float().mean().item(),
    }


@torch.no_grad()
def evaluate(model, loader, device, crit_yaw, crit_pitch):
    """完整评估"""
    model.eval()

    all_yaw_logits = []
    all_pitch_logits = []
    all_yaw_true = []
    all_pitch_true = []
    total_loss = 0.0
    n_batches = 0

    for X, y in loader:
        X = X.to(device)
        yaw_true = (y[:, 0] / 5.0).long().to(device)  # yaw_deg -> bin
        pitch_true = ((y[:, 1] + 90.0) / 5.0).long().to(device)  # pitch_deg -> bin

        yaw_logits, pitch_logits = model(X)

        loss = crit_yaw(yaw_logits, yaw_true) + crit_pitch(pitch_logits, pitch_true)
        total_loss += loss.item()
        n_batches += 1

        all_yaw_logits.append(yaw_logits.cpu())
        all_pitch_logits.append(pitch_logits.cpu())
        all_yaw_true.append(yaw_true.cpu())
        all_pitch_true.append(pitch_true.cpu())

    yl = torch.cat(all_yaw_logits)
    pl = torch.cat(all_pitch_logits)
    yt = torch.cat(all_yaw_true)
    pt = torch.cat(all_pitch_true)

    metrics = compute_metrics(yl, pl, yt, pt)
    metrics["loss"] = total_loss / n_batches if n_batches else float("inf")
    metrics["n_samples"] = len(yt)

    return metrics


def train_one_epoch(model, loader, optimizer, crit_yaw, crit_pitch, device):
    """单 epoch 训练"""
    model.train()
    total_loss = 0.0
    n_batches = 0
    grad_norms = []

    for X, y in loader:
        X = X.to(device)
        yaw_true = (y[:, 0] / 5.0).long().to(device)
        pitch_true = ((y[:, 1] + 90.0) / 5.0).long().to(device)

        yaw_logits, pitch_logits = model(X)
        loss = crit_yaw(yaw_logits, yaw_true) + crit_pitch(pitch_logits, pitch_true)

        optimizer.zero_grad()
        loss.backward()

        gnorm = sum(p.grad.data.norm(2).item() ** 2
                   for p in model.parameters() if p.grad is not None) ** 0.5
        grad_norms.append(gnorm)

        optimizer.step()
        total_loss += loss.item()
        n_batches += 1

    return {
        "loss": total_loss / n_batches,
        "grad_norm_mean": float(np.mean(grad_norms)),
        "grad_norm_max": float(np.max(grad_norms)),
        "n_batches": n_batches,
    }


def train_single_config_fold(
    config: Dict,
    fold_id: int,
    npz_path: Path,
    split_manifest_path: Path,
    feature_definitions: Dict,
    training_protocol: Dict,
    device: torch.device,
    output_dir: Path,
    num_workers: int = 4,
    pin_memory: bool = True,
) -> Dict:
    """
    训练单个 config 的单个 fold

    Returns:
        result dict (per-config, per-fold)
    """
    config_name = config['config_name']

    print(f"\n{'='*60}")
    print(f"Training: {config_name} | Fold {fold_id}")
    print(f"{'='*60}")

    # 加载 split manifest
    with open(split_manifest_path, encoding='utf-8') as f:
        split_manifest = json.load(f)

    train_records = split_manifest['train']
    val_records = split_manifest['val']
    test_records = split_manifest['test']

    # 计算 normalization params（仅从 train）
    norm_params = compute_normalization_params(npz_path, config_name, train_records)

    # 创建 datasets
    train_dataset = EnhancedOCSDataset(
        npz_path, config_name, train_records, norm_params, feature_definitions
    )
    val_dataset = EnhancedOCSDataset(
        npz_path, config_name, val_records, norm_params, feature_definitions
    )
    test_dataset = EnhancedOCSDataset(
        npz_path, config_name, test_records, norm_params, feature_definitions
    )

    print(f"  Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
    print(f"  Feature dim: {train_dataset.get_feature_dim()}")

    # 创建 dataloaders
    batch_size = training_protocol['batch_size']
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size,
        shuffle=True, num_workers=num_workers, pin_memory=pin_memory
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size,
        shuffle=False, num_workers=num_workers, pin_memory=pin_memory
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size,
        shuffle=False, num_workers=num_workers, pin_memory=pin_memory
    )

    # 创建模型
    torch.manual_seed(training_protocol['seed'])
    np.random.seed(training_protocol['seed'])
    if device.type == 'cuda':
        torch.cuda.manual_seed(training_protocol['seed'])

    model = OCSOnlyMLP(
        in_dim=train_dataset.get_feature_dim(),
        hidden_dim=training_protocol['hidden_dim']
    ).to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"  Model params: {n_params:,}")

    # 优化器与损失函数
    optimizer = optim.Adam(model.parameters(), lr=training_protocol['lr'])
    crit_yaw = nn.CrossEntropyLoss()
    crit_pitch = nn.CrossEntropyLoss()

    # 训练循环
    t0 = time.time()
    best_val_avg_acc = 0.0
    best_epoch = 0
    history = {"train": [], "val": []}

    for epoch in range(1, training_protocol['max_epochs'] + 1):
        train_r = train_one_epoch(model, train_loader, optimizer, crit_yaw, crit_pitch, device)
        train_r["epoch"] = epoch
        history["train"].append(train_r)

        val_r = evaluate(model, val_loader, device, crit_yaw, crit_pitch)
        val_r["epoch"] = epoch
        history["val"].append(val_r)

        avg_acc = (val_r["yaw_acc"] + val_r["pitch_acc"]) / 2
        if avg_acc > best_val_avg_acc:
            best_val_avg_acc = avg_acc
            best_epoch = epoch

        if epoch % 5 == 0 or epoch == training_protocol['max_epochs']:
            print(f"  Epoch {epoch:2d}/{training_protocol['max_epochs']}: "
                  f"train_loss={train_r['loss']:.4f} | "
                  f"val_loss={val_r['loss']:.4f} "
                  f"yaw_acc={val_r['yaw_acc']:.4f} "
                  f"pitch_acc={val_r['pitch_acc']:.4f}")

    elapsed = time.time() - t0
    print(f"  Best val avg_acc={best_val_avg_acc:.4f} at epoch {best_epoch}")
    print(f"  Elapsed: {elapsed:.1f}s")

    # Final evaluation on test
    test_metrics = evaluate(model, test_loader, device, crit_yaw, crit_pitch)
    val_metrics = history["val"][-1]

    # 保存 checkpoint
    ckpt_path = output_dir / f"{config_name}_fold{fold_id}_checkpoint.pt"
    torch.save({
        "config_name": config_name,
        "fold_id": fold_id,
        "epoch": training_protocol['max_epochs'],
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "history": history,
    }, ckpt_path)
    ckpt_size_mb = ckpt_path.stat().st_size / (1024 * 1024)

    # 构建结果
    result = generate_per_config_result_template(
        config, fold_id, str(split_manifest_path),
        len(train_dataset), len(val_dataset), len(test_dataset),
        training_protocol
    )

    result["normalization_params"]["mean"] = norm_params['mean'].tolist()
    result["normalization_params"]["std"] = norm_params['std'].tolist()

    result["model_info"]["n_params"] = n_params
    result["model_info"]["checkpoint_path"] = str(ckpt_path)
    result["model_info"]["checkpoint_size_mb"] = ckpt_size_mb

    result["training_summary"]["best_epoch"] = best_epoch
    result["training_summary"]["best_val_avg_acc"] = best_val_avg_acc
    result["training_summary"]["final_train_loss"] = history["train"][-1]["loss"]
    result["training_summary"]["elapsed_s"] = elapsed

    result["final_metrics"]["val"] = val_metrics
    result["final_metrics"]["test"] = test_metrics

    result["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    return result


# ══════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="1C-E32: C2 OCS-only 筛选训练",
        epilog="对 13 个 c2_participant=true 配置进行 5-fold 交叉验证训练。"
    )
    parser.add_argument("--train", action="store_true",
                       help="[REQUIRED] 显式放行训练")
    parser.add_argument("--dry-run", action="store_true",
                       help="Dry-run：只做数据加载和单 batch 测试，不训练")
    parser.add_argument("--npz-path", type=Path, default=DEFAULT_NPZ_PATH)
    parser.add_argument("--definitions-path", type=Path, default=DEFAULT_DEFINITIONS_PATH)
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--device", type=str, default="auto",
                       help="设备：auto / cuda / cpu")
    parser.add_argument("--num-workers", type=int, default=4,
                       help="DataLoader worker 数量")

    args = parser.parse_args()

    if not args.train and not args.dry_run:
        print("[BLOCKED] 必须传 --train 或 --dry-run")
        sys.exit(1)

    # 设备选择
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    use_gpu = (device.type == "cuda")
    num_workers = args.num_workers if use_gpu else 0
    pin_memory = use_gpu

    print(f"{'='*60}")
    print(f"1C-E31/E32 C2 OCS-only Screening")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'TRAINING'}")
    print(f"Device: {device} (GPU={use_gpu}, workers={num_workers})")
    print(f"Output: {args.outdir}")
    print(f"{'='*60}")

    # 加载 feature definitions
    print("\nLoading feature definitions...")
    feature_defs = load_feature_definitions(args.definitions_path)
    c2_configs = get_c2_participant_configs(feature_defs)
    print(f"  Found {len(c2_configs)} C2 participant configs")

    # 训练协议（固定，不可修改）
    training_protocol = C2_FIXED_PROTOCOL.copy()

    print("\n[FIXED PROTOCOL - NO HYPERPARAM SEARCH]")
    for k, v in training_protocol.items():
        print(f"  {k}: {v}")

    # Dry-run 模式：只测试数据加载和单 batch
    if args.dry_run:
        print("\n[DRY-RUN MODE]")
        print("Testing data loading and single batch forward pass...\n")

        test_config = c2_configs[0]
        test_fold = 0
        split_manifest_path = args.split_dir / f"split_manifest_circ_yawblock_fold{test_fold}.json"

        print(f"Test config: {test_config['config_name']}")
        print(f"Test fold: {test_fold}")

        with open(split_manifest_path, encoding='utf-8') as f:
            split_manifest = json.load(f)

        train_records = split_manifest['train']

        # 计算 norm params
        print("Computing normalization params...")
        norm_params = compute_normalization_params(
            args.npz_path, test_config['config_name'], train_records
        )
        print(f"  Mean shape: {norm_params['mean'].shape}")
        print(f"  Std shape: {norm_params['std'].shape}")

        # 创建 dataset
        print("Creating dataset...")
        train_dataset = EnhancedOCSDataset(
            args.npz_path, test_config['config_name'], train_records,
            norm_params, feature_defs
        )
        print(f"  Dataset size: {len(train_dataset)}")
        print(f"  Feature dim: {train_dataset.get_feature_dim()}")

        # 测试单 batch
        print("Testing single batch...")
        train_loader = DataLoader(
            train_dataset, batch_size=C2_FIXED_PROTOCOL['batch_size'], shuffle=False,
            num_workers=0, pin_memory=False
        )
        X, y = next(iter(train_loader))
        print(f"  X shape: {X.shape}, dtype: {X.dtype}")
        print(f"  y shape: {y.shape}, dtype: {y.dtype}")
        print(f"  X finite: {torch.isfinite(X).all()}")
        print(f"  y finite: {torch.isfinite(y).all()}")

        # 测试模型 forward
        print("Testing model forward pass...")
        model = OCSOnlyMLP(in_dim=train_dataset.get_feature_dim(),
                          hidden_dim=C2_FIXED_PROTOCOL['hidden_dim'])
        model = model.to(device)
        X = X.to(device)

        yaw_logits, pitch_logits = model(X)
        print(f"  Yaw logits shape: {yaw_logits.shape}")
        print(f"  Pitch logits shape: {pitch_logits.shape}")
        print(f"  Yaw logits finite: {torch.isfinite(yaw_logits).all()}")
        print(f"  Pitch logits finite: {torch.isfinite(pitch_logits).all()}")

        print("\n[DRY-RUN COMPLETE] All checks passed.")
        return 0

    # 正式训练模式
    print("\n[TRAINING MODE]")
    print(f"Training {len(c2_configs)} configs × {N_FOLDS} folds = {len(c2_configs) * N_FOLDS} runs\n")

    args.outdir.mkdir(parents=True, exist_ok=True)

    # 准备 summary
    feature_source_info = {
        "npz_path": str(args.npz_path),
        "definitions_path": str(args.definitions_path),
        "summary_path": str(DEFAULT_SUMMARY_PATH),
        "n_records": 2664,
    }

    summary = generate_c2_summary_template(
        c2_configs, N_FOLDS, feature_source_info, training_protocol, args.outdir
    )
    summary["execution_date"] = time.strftime("%Y-%m-%d")

    # 训练所有 configs × folds
    all_results = []

    for config in c2_configs:
        config_name = config['config_name']
        config_dir = args.outdir / config_name
        config_dir.mkdir(parents=True, exist_ok=True)

        fold_results = []

        for fold_id in range(N_FOLDS):
            split_manifest_path = args.split_dir / f"split_manifest_circ_yawblock_fold{fold_id}.json"

            result = train_single_config_fold(
                config, fold_id, args.npz_path, split_manifest_path,
                feature_defs, training_protocol, device, config_dir,
                num_workers, pin_memory
            )

            # 保存 per-fold 结果
            result_path = config_dir / f"{config_name}_fold{fold_id}_result.json"
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            fold_results.append({
                "fold_id": fold_id,
                "result_path": str(result_path),
                "best_val_avg_acc": result["training_summary"]["best_val_avg_acc"],
                "test_yaw_acc": result["final_metrics"]["test"]["yaw_acc"],
                "test_pitch_acc": result["final_metrics"]["test"]["pitch_acc"],
            })

        # 计算 aggregate metrics
        val_accs = [r["best_val_avg_acc"] for r in fold_results]
        test_yaw_accs = [r["test_yaw_acc"] for r in fold_results]
        test_pitch_accs = [r["test_pitch_acc"] for r in fold_results]

        # 收集 C2 判据关键指标
        test_yaw_cmaes = []
        test_yaw_within_1_rates = []
        test_yaw_within_3_rates = []
        test_yaw_within_5_rates = []
        test_yaw_correct_counts = []
        test_pitch_within_1_rates = []
        test_pitch_within_3_rates = []
        test_pitch_within_5_rates = []
        test_pitch_correct_counts = []

        for r in fold_results:
            # 需要从 result JSON 中读取完整 metrics
            result_path = Path(r["result_path"])

            # 尝试不同的编码读取（兼容 Windows GBK 和 UTF-8）
            for encoding in ['utf-8', 'gbk', 'latin-1']:
                try:
                    with open(result_path, 'r', encoding=encoding) as f:
                        full_result = json.load(f)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            else:
                raise ValueError(f"Cannot decode {result_path} with utf-8, gbk, or latin-1")

            test_metrics = full_result["final_metrics"]["test"]
            test_yaw_cmaes.append(test_metrics["yaw_circular_mae_deg"])
            test_yaw_within_1_rates.append(test_metrics["yaw_within_1_bin_rate"])
            test_yaw_within_3_rates.append(test_metrics["yaw_within_3_bins_rate"])
            test_yaw_within_5_rates.append(test_metrics["yaw_within_5_bins_rate"])
            test_yaw_correct_counts.append(test_metrics["yaw_correct_count"])
            test_pitch_within_1_rates.append(test_metrics["pitch_within_1_bin_rate"])
            test_pitch_within_3_rates.append(test_metrics["pitch_within_3_bins_rate"])
            test_pitch_within_5_rates.append(test_metrics["pitch_within_5_bins_rate"])
            test_pitch_correct_counts.append(test_metrics["pitch_correct_count"])

        config_summary = {
            "config_name": config_name,
            "config_id": config['config_id'],
            "claim_class": config['claim_class'],
            "feature_dim": config['dim'],
            "feature_keys": config['feature_keys'],
            "fold_results": fold_results,
            "aggregate_metrics": {
                # Val metrics
                "mean_val_avg_acc": float(np.mean(val_accs)),
                "std_val_avg_acc": float(np.std(val_accs)),

                # Test accuracy
                "mean_test_yaw_acc": float(np.mean(test_yaw_accs)),
                "std_test_yaw_acc": float(np.std(test_yaw_accs)),
                "mean_test_pitch_acc": float(np.mean(test_pitch_accs)),
                "std_test_pitch_acc": float(np.std(test_pitch_accs)),

                # Test MAE
                "mean_test_yaw_circular_mae_deg": float(np.mean(test_yaw_cmaes)),
                "std_test_yaw_circular_mae_deg": float(np.std(test_yaw_cmaes)),

                # Test within-k rates (yaw)
                "mean_test_yaw_within_1_bin_rate": float(np.mean(test_yaw_within_1_rates)),
                "std_test_yaw_within_1_bin_rate": float(np.std(test_yaw_within_1_rates)),
                "mean_test_yaw_within_3_bins_rate": float(np.mean(test_yaw_within_3_rates)),
                "std_test_yaw_within_3_bins_rate": float(np.std(test_yaw_within_3_rates)),
                "mean_test_yaw_within_5_bins_rate": float(np.mean(test_yaw_within_5_rates)),
                "std_test_yaw_within_5_bins_rate": float(np.std(test_yaw_within_5_rates)),

                # Test correct counts
                "mean_test_yaw_correct_count": float(np.mean(test_yaw_correct_counts)),
                "std_test_yaw_correct_count": float(np.std(test_yaw_correct_counts)),
                "mean_test_pitch_correct_count": float(np.mean(test_pitch_correct_counts)),
                "std_test_pitch_correct_count": float(np.std(test_pitch_correct_counts)),

                # Test within-k rates (pitch)
                "mean_test_pitch_within_1_bin_rate": float(np.mean(test_pitch_within_1_rates)),
                "std_test_pitch_within_1_bin_rate": float(np.std(test_pitch_within_1_rates)),
                "mean_test_pitch_within_3_bins_rate": float(np.mean(test_pitch_within_3_rates)),
                "std_test_pitch_within_3_bins_rate": float(np.std(test_pitch_within_3_rates)),
                "mean_test_pitch_within_5_bins_rate": float(np.mean(test_pitch_within_5_rates)),
                "std_test_pitch_within_5_bins_rate": float(np.std(test_pitch_within_5_rates)),
            }
        }

        all_results.append(config_summary)

    # 更新 summary
    summary["results_summary"] = all_results

    # 保存 summary
    summary_path = args.outdir / "c2_screening_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"C2 Screening Complete")
    print(f"{'='*60}")
    print(f"Summary -> {summary_path}")

    # 打印汇总
    print("\nResults Summary:")
    for cfg_sum in all_results:
        agg = cfg_sum["aggregate_metrics"]
        print(f"  {cfg_sum['config_name']:30s} [{cfg_sum['claim_class']}]")
        print(f"    val_acc={agg['mean_val_avg_acc']:.4f}±{agg['std_val_avg_acc']:.4f}")
        print(f"    test_yaw_acc={agg['mean_test_yaw_acc']:.4f}±{agg['std_test_yaw_acc']:.4f} | "
              f"cmae={agg['mean_test_yaw_circular_mae_deg']:.2f}±{agg['std_test_yaw_circular_mae_deg']:.2f}deg | "
              f"within3={agg['mean_test_yaw_within_3_bins_rate']:.4f}±{agg['std_test_yaw_within_3_bins_rate']:.4f}")
        print(f"    test_pitch_acc={agg['mean_test_pitch_acc']:.4f}±{agg['std_test_pitch_acc']:.4f}")

    print("\n[DONE] 1C-E32 C2 screening complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

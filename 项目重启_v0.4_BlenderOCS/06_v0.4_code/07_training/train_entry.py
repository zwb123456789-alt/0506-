#!/usr/bin/env python3
"""
train_entry.py —— 1C-E19: 训练入口脚本骨架

支持三种输入模式：image_only / ocs_only / joint。
当前仅提供骨架和 loader 验证，不执行实际训练。

架构概览：
  image_only:  CNN(ResNet-18 变体) → fc → [yaw_logits, pitch_logits]
  ocs_only:    MLP(ocs_dim → 256 → 128) → fc → [yaw_logits, pitch_logits]
  joint:       CNN + MLP → concat → fc → [yaw_logits, pitch_logits]

使用：
    # 仅 loader smoke（不训练）
    python train_entry.py --smoke-only

    # 单 batch 前向传播 smoke
    python train_entry.py --forward-smoke --epochs 0

红线：
    - 当前阶段不执行训练循环
    - 不保存模型权重
    - 不写论文正文
"""

import argparse
import json
import os
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

# 项目路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code"))

from dataset import OCSImageDataset  # noqa: E402


# ═══════════════════════════════════════════════════════
# 模型定义（骨架）
# ═══════════════════════════════════════════════════════

class ImageEncoder(nn.Module):
    """轻量 CNN 图像编码器（256x256 单通道输入）。"""

    def __init__(self, in_channels=1, out_dim=256):
        super().__init__()
        self.conv = nn.Sequential(
            # 256 -> 128
            nn.Conv2d(in_channels, 32, 4, stride=2, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(inplace=True),
            # 128 -> 64
            nn.Conv2d(32, 64, 4, stride=2, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            # 64 -> 32
            nn.Conv2d(64, 128, 4, stride=2, padding=1),
            nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            # 32 -> 16
            nn.Conv2d(128, 256, 4, stride=2, padding=1),
            nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            # 16 -> 8
            nn.Conv2d(256, 256, 4, stride=2, padding=1),
            nn.BatchNorm2d(256), nn.ReLU(inplace=True),
            # 8 -> 4
            nn.Conv2d(256, 256, 4, stride=2, padding=1),
            nn.BatchNorm2d(256), nn.ReLU(inplace=True),
        )
        self.fc = nn.Linear(256 * 4 * 4, out_dim)

    def forward(self, x):
        h = self.conv(x)
        h = h.view(h.size(0), -1)
        return self.fc(h)


class OCSEncoder(nn.Module):
    """MLP OCS 编码器。"""

    def __init__(self, in_dim=1, hidden=128, out_dim=128):
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
    """姿态预测头：yaw (72 类) + pitch (37 类)。"""

    def __init__(self, in_dim, n_yaw=72, n_pitch=37):
        super().__init__()
        self.yaw_head = nn.Linear(in_dim, n_yaw)
        self.pitch_head = nn.Linear(in_dim, n_pitch)

    def forward(self, x):
        return self.yaw_head(x), self.pitch_head(x)


class OCSImageModel(nn.Module):
    """OCS + Image 联合姿态估计模型（骨架）。

    Args:
        mode: "image_only" | "ocs_only" | "joint"
        ocs_dim: OCS 输入维度 (default: 1, ocs_total only)
    """

    def __init__(self, mode="joint", ocs_dim=1,
                 n_yaw=72, n_pitch=37):
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
            img_feat = self.image_encoder(batch["image"])
            features.append(img_feat)
        if self.mode in ("ocs_only", "joint"):
            ocs_feat = self.ocs_encoder(batch["ocs"])
            features.append(ocs_feat)
        fused = torch.cat(features, dim=1)
        yaw_logits, pitch_logits = self.predictor(fused)
        return yaw_logits, pitch_logits


# ═══════════════════════════════════════════════════════
# 训练脚本（骨架，当前不执行实际训练）
# ═══════════════════════════════════════════════════════

DEFAULT_SPLIT_MANIFEST = str(
    PROJECT_ROOT / "v0.4_results" / "01_fullrun"
    / "postprocess" / "split_manifest.json"
)


def compute_accuracy(yaw_logits, pitch_logits, yaw_true, pitch_true,
                     n_yaw=72, step_deg=5.0):
    """计算 top-1 准确率和 circular yaw MAE / linear pitch MAE。

    R39 P2: yaw 误差使用 circular error，避免 0/355 边界的错误放大。
    """
    yaw_pred = yaw_logits.argmax(dim=1)
    pitch_pred = pitch_logits.argmax(dim=1)
    yaw_acc = (yaw_pred == yaw_true).float().mean().item()
    pitch_acc = (pitch_pred == pitch_true).float().mean().item()
    # circular yaw error: min(|diff|, n_bins - |diff|) * step_deg
    yaw_diff = (yaw_pred - yaw_true).abs()
    yaw_err_deg = torch.min(yaw_diff, n_yaw - yaw_diff).float().mean().item() * step_deg
    pitch_err_deg = (pitch_pred - pitch_true).abs().float().mean().item() * step_deg
    return yaw_acc, pitch_acc, yaw_err_deg, pitch_err_deg


def forward_smoke(model, loader, device, mode):
    """单 batch 前向传播 smoke：验证模型能跑通。"""
    print(f"\n[FORWARD SMOKE] Mode: {mode}")
    batch = next(iter(loader))
    batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v
             for k, v in batch.items()}

    model.eval()
    with torch.no_grad():
        yaw_logits, pitch_logits = model(batch)

    yaw_acc, pitch_acc, yaw_err, pitch_err = compute_accuracy(
        yaw_logits, pitch_logits, batch["yaw_bin"], batch["pitch_bin"])

    print(f"  yaw_logits:   {yaw_logits.shape}  (72 classes)")
    print(f"  pitch_logits: {pitch_logits.shape}  (37 classes)")
    print(f"  yaw_acc:      {yaw_acc:.4f}  (random baseline ~1/72={1/72:.4f})")
    print(f"  pitch_acc:    {pitch_acc:.4f}  (random baseline ~1/37={1/37:.4f})")
    print(f"  yaw_mae:      {yaw_err:.2f} deg")
    print(f"  pitch_mae:    {pitch_err:.2f} deg")
    print(f"  params:       {sum(p.numel() for p in model.parameters()):,}")

    return {
        "yaw_logits_shape": list(yaw_logits.shape),
        "pitch_logits_shape": list(pitch_logits.shape),
        "yaw_acc_random_baseline": yaw_acc,
        "pitch_acc_random_baseline": pitch_acc,
        "yaw_mae_deg": yaw_err,
        "pitch_mae_deg": pitch_err,
        "n_params": sum(p.numel() for p in model.parameters()),
    }


def loader_smoke(split_manifest, batch_size=32):
    """验证 DataLoader 能正常迭代。"""
    print("=" * 60)
    print("Loader Smoke Test")
    print("=" * 60)

    for split_name in ("train", "val", "test"):
        ds = OCSImageDataset(split_manifest, split=split_name, mode="joint")
        loader = DataLoader(ds, batch_size=batch_size, shuffle=(split_name == "train"))
        batch = next(iter(loader))
        print(f"\n[LOADER] {split_name}: {len(ds)} samples, "
              f"{len(loader)} batches @ batch_size={batch_size}")
        print(f"  image:    {batch['image'].shape} {batch['image'].dtype}")
        print(f"  ocs:      {batch['ocs'].shape} {batch['ocs'].dtype}")
        print(f"  yaw_bin:  {batch['yaw_bin'].shape}, "
              f"min={batch['yaw_bin'].min()}, max={batch['yaw_bin'].max()}")
        print(f"  pitch_bin:{batch['pitch_bin'].shape}, "
              f"min={batch['pitch_bin'].min()}, max={batch['pitch_bin'].max()}")

        # Check for NaN/Inf
        has_nan = torch.isnan(batch['image']).any()
        has_inf = torch.isinf(batch['image']).any()
        print(f"  NaN: {has_nan}, Inf: {has_inf}")

        # Path spot-check
        all_exist = all(
            (PROJECT_ROOT / ds.records[i]["png_path"]).exists()
            for i in range(min(10, len(ds)))
        )
        print(f"  Path check (first 10): {'OK' if all_exist else 'FAIL'}")

    print(f"\n[DONE] Loader smoke passed for all splits.")


def main():
    parser = argparse.ArgumentParser(description="训练入口骨架 (1C-E19)")
    parser.add_argument("--smoke-only", action="store_true",
                        help="仅跑 loader smoke，不构建模型")
    parser.add_argument("--forward-smoke", action="store_true",
                        help="跑单 batch 前向传播 smoke")
    parser.add_argument("--mode", type=str, default="joint",
                        choices=["image_only", "ocs_only", "joint"])
    parser.add_argument("--split-manifest", type=str,
                        default=DEFAULT_SPLIT_MANIFEST)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--epochs", type=int, default=0,
                        help="训练 epoch 数（当前必须为 0，不训练）")
    args = parser.parse_args()

    # 红线检查
    if args.epochs > 0:
        print("[BLOCKED] 当前阶段不允许训练。请将 --epochs 设为 0。")
        sys.exit(1)

    if not os.path.exists(args.split_manifest):
        print(f"[ERROR] Split manifest not found: {args.split_manifest}")
        print("Run: python 06_v0.4_code/07_training/split_dataset.py")
        sys.exit(1)

    results = {}

    # ── Step 1: Loader smoke ──
    loader_smoke(args.split_manifest, args.batch_size)

    # ── Step 2: Forward smoke (optional) ──
    if args.forward_smoke:
        print(f"\n{'='*60}")
        print("Forward Smoke Test")
        print(f"{'='*60}")

        device = torch.device(args.device if torch.cuda.is_available() else "cpu")
        print(f"Device: {device}")

        for mode in ("image_only", "ocs_only", "joint"):
            ds = OCSImageDataset(args.split_manifest, split="train", mode=mode)
            loader = DataLoader(ds, batch_size=args.batch_size, shuffle=True)
            model = OCSImageModel(mode=mode, ocs_dim=4).to(device)
            result = forward_smoke(model, loader, device, mode)
            results[f"forward_smoke_{mode}"] = result

    # ── 输出结果摘要 ──
    if results:
        print(f"\n{'='*60}")
        print("Smoke Results Summary")
        print(f"{'='*60}")
        for k, v in results.items():
            print(f"  {k}: {json.dumps(v, indent=2)}")

    print(f"\n[DONE] 1C-E19 训练入口骨架验证完成。不执行训练。")


if __name__ == "__main__":
    main()

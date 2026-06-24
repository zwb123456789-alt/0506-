#!/usr/bin/env python3
"""
dataset.py —— 1C-E19: OCS + Image 联合数据集

提供三种输入模式的 PyTorch Dataset：
  - "image_only": 仅图像 → CNN
  - "ocs_only":   仅 OCS 向量 → MLP
  - "joint":      图像 + OCS → 融合模型

标签方案（fixed-roll）：
  - yaw_bin:   0..71 (72 类，每类 5 deg)
  - pitch_bin: 0..36 (37 类，每类 5 deg, 对应 -90..+90)

使用：
    from dataset import OCSImageDataset
    ds = OCSImageDataset(split_manifest_path, split="train", mode="joint")
    sample = ds[0]
    # sample = {"image": Tensor[1,256,256], "ocs": Tensor[4],
    #           "yaw_bin": int, "pitch_bin": int,
    #           "yaw_deg": float, "pitch_deg": float, "record_id": str}
"""

import json
import os
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset
from PIL import Image


# ── 默认路径 ──────────────────────────────────────────
DEFAULT_SPLIT_MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "v0.4_results" / "01_fullrun" / "postprocess" / "split_manifest.json"
)


class OCSImageDataset(Dataset):
    """OCS + Image 联合数据集。

    Args:
        split_manifest_path: split_manifest.json 路径
        split: "train" | "val" | "test"
        mode: "image_only" | "ocs_only" | "joint"
        transform: 可选图像 transform（暂未实现，预留接口）
    """

    def __init__(self, split_manifest_path=None, split="train",
                 mode="joint", transform=None):
        if split_manifest_path is None:
            split_manifest_path = str(DEFAULT_SPLIT_MANIFEST)

        with open(split_manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        if split not in ("train", "val", "test"):
            raise ValueError(f"Unknown split: {split}, must be train/val/test")

        self.records = manifest[split]
        self.mode = mode
        self.transform = transform
        self.split = split
        self.manifest_meta = {k: v for k, v in manifest.items()
                              if k not in ("train", "val", "test")}

        # split_manifest at: v0.4_results/01_fullrun/postprocess/split_manifest.json
        # parents[0]=postprocess, [1]=01_fullrun, [2]=v0.4_results, [3]=V04_PROJECT
        self._data_root = Path(split_manifest_path).resolve().parents[3]

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        rec = self.records[idx]

        # ── 图像 ──
        png_path = self._data_root / rec["png_path"]
        if not png_path.exists():
            raise FileNotFoundError(f"Image not found: {png_path}")
        image = self._load_image(str(png_path))

        # ── OCS 向量 (4-dim: total + 3 per-part) ──
        ocs = torch.tensor([
            rec["ocs_total"],
            rec["ocs_jinshuzhuti"],
            rec["ocs_taiyangnengban"],
            rec["ocs_yinshenban"],
        ], dtype=torch.float32)

        # ── 标签 ──
        yaw_bin = int(rec["yaw_idx"])
        pitch_bin = int(rec["pitch_idx"])

        sample = {
            "image": image,
            "ocs": ocs,
            "yaw_bin": yaw_bin,
            "pitch_bin": pitch_bin,
            "yaw_deg": float(rec["yaw_deg"]),
            "pitch_deg": float(rec["pitch_deg"]),
            "record_id": str(rec["record_id"]),
        }

        if self.transform is not None:
            sample = self.transform(sample)

        return sample

    def _load_image(self, path):
        """加载 PNG 图像为 float32 tensor [1, 256, 256]（单通道灰度）。"""
        img = Image.open(path)
        # 统一为灰度单通道
        if img.mode != "L":
            img = img.convert("L")
        arr = np.array(img, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(arr).unsqueeze(0)  # [1, H, W]
        return tensor

    def get_ocs_full(self, idx, ocs_manifest_path=None):
        """获取完整 OCS 向量（含 per-part），需要访问 ocs_manifest。

        注意：此方法会额外加载 ocs_manifest，不适用于高频 dataloader 调用。
        推荐在 split manifest 构建时就将 per-part OCS 写入 split manifest。
        """
        rec = self.records[idx]
        if ocs_manifest_path is None:
            ocs_manifest_path = (
                self._data_root / "v0.4_results" / "01_fullrun"
                / "postprocess" / "ocs_manifest_v0_4_fullrun.json"
            )
        with open(ocs_manifest_path, "r", encoding="utf-8") as f:
            ocs_raw = json.load(f)

        # 按 record_id 查找
        for r in ocs_raw["records"]:
            if r["record_id"] == rec["record_id"]:
                return torch.tensor([
                    r["ocs_total"],
                    r["ocs_per_part"]["jinshuzhuti"],
                    r["ocs_per_part"]["taiyangnengban"],
                    r["ocs_per_part"]["yinshenban"],
                ], dtype=torch.float32)
        return torch.zeros(4, dtype=torch.float32)


def make_dataloaders(split_manifest_path=None, mode="joint",
                     batch_size=32, num_workers=0):
    """便捷函数：创建 train/val/test DataLoader。

    Returns:
        train_loader, val_loader, test_loader, dataset_info (dict)
    """
    train_ds = OCSImageDataset(split_manifest_path, split="train", mode=mode)
    val_ds = OCSImageDataset(split_manifest_path, split="val", mode=mode)
    test_ds = OCSImageDataset(split_manifest_path, split="test", mode=mode)

    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=True)
    val_loader = torch.utils.data.DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True)
    test_loader = torch.utils.data.DataLoader(
        test_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True)

    info = {
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "n_test": len(test_ds),
        "image_shape": tuple(train_ds[0]["image"].shape),
        "ocs_dim": int(train_ds[0]["ocs"].shape[0]),
        "n_yaw_classes": 72,
        "n_pitch_classes": 37,
        "mode": mode,
        "batch_size": batch_size,
        "split_meta": train_ds.manifest_meta,
    }
    return train_loader, val_loader, test_loader, info


# ── Smoke test ──
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dataset smoke test")
    parser.add_argument("--split-manifest", type=str,
                        default=str(DEFAULT_SPLIT_MANIFEST))
    parser.add_argument("--mode", type=str, default="joint",
                        choices=["image_only", "ocs_only", "joint"])
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()

    print("=" * 60)
    print("Dataset Loader Smoke Test")
    print(f"Split manifest: {args.split_manifest}")
    print(f"Mode: {args.mode}")
    print(f"Batch size: {args.batch_size}")
    print("=" * 60)

    if not os.path.exists(args.split_manifest):
        print(f"[ERROR] Split manifest not found: {args.split_manifest}")
        print("Run split_dataset.py first.")
        sys.exit(1)

    train_loader, val_loader, test_loader, info = make_dataloaders(
        args.split_manifest, mode=args.mode, batch_size=args.batch_size)

    print(f"\n[INFO] Dataset info:")
    for k, v in info.items():
        print(f"  {k}: {v}")

    # Train batch smoke
    print(f"\n[SMOKE] Train loader batches: {len(train_loader)}")
    batch = next(iter(train_loader))
    print(f"  image:    {batch['image'].shape} {batch['image'].dtype}")
    print(f"  ocs:      {batch['ocs'].shape} {batch['ocs'].dtype}")
    print(f"  yaw_bin:  {batch['yaw_bin'].shape}, "
          f"range=[{batch['yaw_bin'].min()}, {batch['yaw_bin'].max()}]")
    print(f"  pitch_bin:{batch['pitch_bin'].shape}, "
          f"range=[{batch['pitch_bin'].min()}, {batch['pitch_bin'].max()}]")
    print(f"  record_id[0]: {batch['record_id'][0]}")

    # Val batch smoke
    batch_val = next(iter(val_loader))
    print(f"\n[SMOKE] Val loader batches: {len(val_loader)}")
    print(f"  image: {batch_val['image'].shape}")

    # Test batch smoke
    batch_test = next(iter(test_loader))
    print(f"\n[SMOKE] Test loader batches: {len(test_loader)}")
    print(f"  image: {batch_test['image'].shape}")

    # Check for NaN / Inf
    has_nan = torch.isnan(batch['image']).any()
    has_inf = torch.isinf(batch['image']).any()
    print(f"\n[CHECK] Image NaN: {has_nan}, Inf: {has_inf}")

    # Path existence check (spot-check first 10)
    print(f"\n[CHECK] Path existence (first 10 train samples):")
    all_ok = True
    for i in range(min(10, len(train_loader.dataset))):
        rec = train_loader.dataset.records[i]
        png_path = (Path(args.split_manifest).resolve().parents[3]
                    / rec["png_path"])
        ok = png_path.exists()
        if not ok:
            print(f"  [MISSING] {png_path}")
            all_ok = False
    if all_ok:
        print(f"  All OK")

    print(f"\n[DONE] Loader smoke test passed.")

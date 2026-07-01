#!/usr/bin/env python3
"""
dataset_l1m2_multigeometry.py —— 1C-L1M2 多几何 OCS 数据集

核心：把"同一姿态在 G 个已知 sun/view 几何下的总光度标量"拼成长度 G 的
多观测光度向量（L1）。这是 simulated multi-view geometry，不是真实跨时间多几何。

输入对齐：
  - 各几何 OCS 来源：
      phase63 : v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json
      其它    : v0.4_results/11_l1m2_multigeometry_ocs/postprocess/<geom>/fullrun_postprocess_summary.json
  - 按 attitude key (yaw_deg,pitch_deg) 对齐（不同几何 record_id 前缀不同）。
  - 图像通道：image_only/joint 固定使用 phase63 (L1-G1) 图像（R114 §7）。

特征：L1 主线 = 多观测【总光度向量】 [total_flux_g for g in group]。
  不使用 per-part（F2 semi-oracle，禁止作主线输入）。
  标准化：log1p 后按 train 统计做 z-score，transform 参数随 split 保存（防泄漏）。

模式：
  ocs_only  : 只用多几何总光度向量
  image_only: 只用 phase63 图像
  joint     : phase63 图像 + 多几何总光度向量
"""

import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FULLRUN_POST = PROJECT_ROOT / "v0.4_results" / "01_fullrun" / "postprocess"
L1M2_POST = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs" / "postprocess"

# 实验组 -> geom_id 列表（与 registry 一致；按相位角排序使向量布局稳定）
GEOM_GROUPS = {
    "G1": ["phase63"],
    "G3": ["phase24", "phase63", "phase120"],
    "G5": ["phase24", "phase45", "phase63", "phase90", "phase120"],
}


def _attitude_key(yaw_deg, pitch_deg):
    return (int(round(float(yaw_deg))), int(round(float(pitch_deg))))


def load_geom_ocs(geom_id):
    """返回 {attitude_key: {'total':float,'yaw':float,'pitch':float}}。"""
    if geom_id == "phase63":
        path = FULLRUN_POST / "ocs_manifest_v0_4_fullrun.json"
        data = json.load(open(path, encoding="utf-8"))
        recs = data["records"]
        out = {}
        for r in recs:
            k = _attitude_key(r["yaw_deg"], r["pitch_deg"])
            out[k] = {"total": float(r["ocs_total"]),
                      "yaw": float(r["yaw_deg"]), "pitch": float(r["pitch_deg"])}
        return out
    else:
        path = L1M2_POST / geom_id / "fullrun_postprocess_summary.json"
        data = json.load(open(path, encoding="utf-8"))
        out = {}
        for r in data["records"]:
            if r.get("status") != "COMPLETE":
                continue
            k = _attitude_key(r["yaw_deg"], r["pitch_deg"])
            out[k] = {"total": float(r["ocs_total"]),
                      "yaw": float(r["yaw_deg"]), "pitch": float(r["pitch_deg"])}
        return out


def build_multigeometry_table(geom_group):
    """构建多几何对齐表。返回 list[dict]，每条含 attitude + flux_vector。

    只保留在【该 group 全部几何】下都有 COMPLETE OCS 的 attitude（内连接）。
    """
    geoms = GEOM_GROUPS[geom_group]
    geom_maps = {g: load_geom_ocs(g) for g in geoms}
    # 内连接 attitude keys
    common = None
    for g in geoms:
        keys = set(geom_maps[g].keys())
        common = keys if common is None else (common & keys)
    common = sorted(common)

    table = []
    for k in common:
        ref = geom_maps[geoms[0]][k]
        flux = [geom_maps[g][k]["total"] for g in geoms]
        yaw = ref["yaw"]
        pitch = ref["pitch"]
        table.append({
            "attitude_key": k,
            "record_id": f"{geom_group}_yaw{int(round(yaw)):03d}_pitch{int(round(pitch)):+04d}",
            "yaw_deg": yaw,
            "pitch_deg": pitch,
            "yaw_idx": int(round(yaw / 5.0)) % 72,
            "pitch_idx": int(round((pitch + 90.0) / 5.0)),
            "flux_vector": flux,             # 长度 = len(geoms)
            "geoms": geoms,
            # phase63 图像路径（image/joint 用）
            "png_path": f"v0.4_results/01_fullrun/postprocess/"
                        f"yaw{int(round(yaw)):03d}_pitch{int(round(pitch)):+04d}_roll+000_brdf.png",
        })
    return table, geoms


def fit_flux_transform(train_table):
    """在 train 上拟合 log1p + z-score 参数。返回 dict（防泄漏：只用 train）。"""
    X = np.array([r["flux_vector"] for r in train_table], dtype=np.float64)  # [N,G]
    Xlog = np.log1p(X)
    mean = Xlog.mean(axis=0)
    std = Xlog.std(axis=0)
    std[std < 1e-8] = 1.0
    return {"method": "log1p_then_zscore",
            "log1p": True,
            "mean": mean.tolist(), "std": std.tolist(),
            "n_geom": X.shape[1]}


def apply_flux_transform(flux_vec, transform):
    x = np.log1p(np.asarray(flux_vec, dtype=np.float64))
    x = (x - np.asarray(transform["mean"])) / np.asarray(transform["std"])
    return x.astype(np.float32)


class L1M2Dataset(Dataset):
    """多几何 OCS + (可选) phase63 图像数据集。

    Args:
        records: 已切分的 record 列表（含 flux_vector 等字段）
        mode: ocs_only | image_only | joint
        flux_transform: fit_flux_transform 的返回（ocs_only/joint 必需）
        image_transform: 可选图像增广 callable(sample)->sample
    """

    def __init__(self, records, mode, flux_transform=None, image_transform=None):
        self.records = records
        self.mode = mode
        self.flux_transform = flux_transform
        self.image_transform = image_transform
        self._data_root = PROJECT_ROOT

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        rec = self.records[idx]
        sample = {
            "record_id": str(rec["record_id"]),
            "yaw_deg": float(rec["yaw_deg"]),
            "pitch_deg": float(rec["pitch_deg"]),
        }
        if self.mode in ("ocs_only", "joint"):
            ocs = apply_flux_transform(rec["flux_vector"], self.flux_transform)
            sample["ocs"] = torch.from_numpy(ocs)
        if self.mode in ("image_only", "joint"):
            png = self._data_root / rec["png_path"]
            img = Image.open(png)
            if img.mode != "L":
                img = img.convert("L")
            arr = np.array(img, dtype=np.float32) / 255.0
            sample["image"] = torch.from_numpy(arr).unsqueeze(0)
        if self.image_transform is not None and "image" in sample:
            sample = self.image_transform(sample)
        return sample


# ── smoke ──
if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    for grp in ["G1", "G3", "G5"]:
        try:
            tbl, geoms = build_multigeometry_table(grp)
            fluxes = np.array([r["flux_vector"] for r in tbl])
            print(f"{grp}: n_attitude={len(tbl)} geoms={geoms} "
                  f"flux_shape={fluxes.shape} "
                  f"flux_mean={fluxes.mean(axis=0).round(5).tolist()}")
        except FileNotFoundError as e:
            print(f"{grp}: [缺数据] {e}")

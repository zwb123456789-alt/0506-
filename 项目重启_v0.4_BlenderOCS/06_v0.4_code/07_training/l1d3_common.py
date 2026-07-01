#!/usr/bin/env python3
"""
l1d3_common.py —— R118 子任务 A-E 的共享工具模块

集中封装：
  - 路径常量（11_l1m2 clean / 12_l1m3 degraded / 13_l1d3 输出）
  - 多几何表构建 + 确定性 split（复用 dataset/train_l1m2）
  - 退化 flux 向量构造（与 train_l1m3_degraded 同口径：按 record_id 派生种子）
  - neural samples_*.npz 加载
  - P-DB template retrieval 核心（neg-L2 / cosine / zscore-neg-L2）
  - yaw circular error / hit / 分层工具

严格口径：
  - template 只来自 train split，绝不混入 val/test。
  - clean 来自 11_l1m2；degraded 来自 12_l1m3；退化观测按 record_id 确定性复现。
  - posterior-like 是工程候选分数，不是真实 Bayesian posterior。
  - P-DB 是 model-known simulated template retrieval，不是真实反演成功率。
"""

import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from dataset_l1m2_multigeometry import (  # noqa: E402
    build_multigeometry_table,
    fit_flux_transform,
    apply_flux_transform,
)
from train_l1m2_multigeometry import split_pint, split_pext, yaw_circ_err  # noqa: E402
from degrade_l1m3_images import DEGRADE_LEVELS, degrade_flux_vector  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ═══════ 路径常量 ═══════
L1M2 = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
L1M3 = PROJECT_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll"
OUT = PROJECT_ROOT / "v0.4_results" / "13_l1d3_confidence_pdb"

GROUPS = ["G1", "G3", "G5"]
MODES = ["ocs_only", "image_only", "joint"]
DEGRADE_ALL = ["clean", "degraded-mild", "degraded-moderate"]
SIMILARITIES = ["neg-L2", "cosine", "zscore-neg-L2"]

# degrade_level -> DEGRADE_LEVELS key
_DEG_KEY = {"degraded-mild": "degraded-mild", "degraded-moderate": "degraded-moderate"}


# ═══════ 多几何表 + split ═══════
def get_split_tables(geom_group, protocol="P-INT", seed=42):
    """返回 (train, val, test) record list（含 flux_vector, record_id, yaw/pitch）。

    与训练时同一确定性 split（split_pint/split_pext）。
    """
    table, geoms = build_multigeometry_table(geom_group)
    if protocol == "P-INT":
        tr, va, te = split_pint(table, seed=seed)
    elif protocol == "P-EXT":
        tr, va, te = split_pext(table)
    else:
        raise ValueError(f"unknown protocol {protocol}")
    return tr, va, te, geoms


def flux_matrix(records, degrade_level="clean"):
    """从 record list 构造 [N, G] flux 矩阵。

    clean：直接用 record["flux_vector"]。
    degraded：按 record_id 确定性施加 degrade_flux_vector（与训练同口径）。
    """
    if degrade_level == "clean":
        return np.array([r["flux_vector"] for r in records], dtype=np.float64)
    params = DEGRADE_LEVELS[_DEG_KEY[degrade_level]]
    out = []
    for r in records:
        out.append(degrade_flux_vector(r["flux_vector"], params, r["record_id"]))
    return np.array(out, dtype=np.float64)


def record_ids(records):
    return np.array([r["record_id"] for r in records], dtype=object)


def yaws(records):
    return np.array([r["yaw_deg"] for r in records], dtype=np.float64)


def pitches(records):
    return np.array([r["pitch_deg"] for r in records], dtype=np.float64)


# ═══════ neural samples 加载 ═══════
def clean_run_dir(protocol, geom, mode, seed=42):
    return L1M2 / "runs" / f"{protocol}_{geom}_{mode}_seed{seed}"


def degraded_run_dir(degrade_level, protocol, geom, mode, seed=42):
    return L1M3 / "degraded" / "runs" / f"{degrade_level}_{protocol}_{geom}_{mode}_seed{seed}"


def run_dir(degrade_level, protocol, geom, mode, seed=42):
    if degrade_level == "clean":
        return clean_run_dir(protocol, geom, mode, seed)
    return degraded_run_dir(degrade_level, protocol, geom, mode, seed)


def load_neural_samples(degrade_level, protocol, geom, mode, split, select, seed=42):
    """加载 samples_{split}_{select}.npz -> dict of arrays；不存在返回 None。"""
    rd = run_dir(degrade_level, protocol, geom, mode, seed)
    npz = rd / f"samples_{split}_{select}.npz"
    if not npz.exists():
        return None
    d = np.load(npz, allow_pickle=True)
    return {k: d[k] for k in d.files}


# ═══════ P-DB template retrieval ═══════
def _log1p(x):
    return np.log1p(np.asarray(x, dtype=np.float64))


def retrieval_scores(X_query, X_template, similarity, transform=None):
    """返回 sim [Nq, Nt]，越大越相似。

    neg-L2       : -||log1p(q)-log1p(t)||^2
    cosine       : cos(log1p(q), log1p(t))
    zscore-neg-L2: 在 train 上拟合的 log1p+zscore 域做 neg-L2（transform 必须来自 train）
    """
    if similarity == "zscore-neg-L2":
        assert transform is not None, "zscore-neg-L2 需要 train-only transform"
        Q = np.array([apply_flux_transform(q, transform) for q in X_query], dtype=np.float64)
        T = np.array([apply_flux_transform(t, transform) for t in X_template], dtype=np.float64)
        d2 = (np.sum(Q**2, 1)[:, None] + np.sum(T**2, 1)[None, :] - 2 * Q @ T.T)
        return -d2
    Lq = _log1p(X_query)
    Lt = _log1p(X_template)
    if similarity == "neg-L2":
        d2 = (np.sum(Lq**2, 1)[:, None] + np.sum(Lt**2, 1)[None, :] - 2 * Lq @ Lt.T)
        return -d2
    if similarity == "cosine":
        def _n(a):
            return a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-12)
        return _n(Lq) @ _n(Lt).T
    raise ValueError(f"unknown similarity {similarity}")


def retrieve_topk(sim, k=10):
    """返回 top-k 索引 [Nq, k]（按 sim 降序）与对应 sim 值 [Nq, k]。"""
    kk = min(k, sim.shape[1])
    order = np.argsort(-sim, axis=1)[:, :kk]
    vals = np.take_along_axis(sim, order, axis=1)
    return order, vals


def retrieval_distance_stats(sim_topk):
    """由 top-k sim 值计算 nearest 相似度、margin(top1-top2)、rank gap 近似。

    sim 越大越相似；返回 dict of per-query arrays。
    nearest_sim = top1 sim；margin = top1 - top2；
    对 neg-L2/zscore，nearest_distance = -top1 sim（即 L2^2）。
    """
    top1 = sim_topk[:, 0]
    top2 = sim_topk[:, 1] if sim_topk.shape[1] > 1 else sim_topk[:, 0]
    return {
        "nearest_sim": top1,
        "margin_sim": top1 - top2,
        "nearest_distance": -top1,  # 对 neg-L2 家族即 squared-L2；cosine 时为 -cos
    }


# ═══════ 指标工具 ═══════
def hit_at(err, thr):
    return float((np.asarray(err) <= thr).mean())


def circ_mae(err):
    return float(np.mean(err))


def yaw_sector(yaw_deg):
    """0-90 / 90-180 / 180-270 / 270-360 分区标签。"""
    y = np.asarray(yaw_deg) % 360.0
    labels = np.empty(len(y), dtype=object)
    bins = [(0, 90), (90, 180), (180, 270), (270, 360)]
    for lo, hi in bins:
        mask = (y >= lo) & (y < hi)
        labels[mask] = f"{lo:03d}-{hi:03d}"
    return labels


def pitch_bin(pitch_deg, width=45):
    """按 pitch 分 bin（-90..90）。"""
    p = np.asarray(pitch_deg)
    lo = (np.floor((p + 90.0) / width) * width - 90.0).astype(int)
    return np.array([f"{v:+03d}..{v+width:+03d}" for v in lo], dtype=object)


def circ_err_between(yaw_a, yaw_b):
    """两组 yaw 的 circular error（复用 train yaw_circ_err）。"""
    return yaw_circ_err(np.asarray(yaw_a, dtype=np.float64), np.asarray(yaw_b, dtype=np.float64))

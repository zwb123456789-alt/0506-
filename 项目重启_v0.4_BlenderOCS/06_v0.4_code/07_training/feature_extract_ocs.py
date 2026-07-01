#!/usr/bin/env python3
"""
feature_extract_ocs.py —— 1C-E29: OCS 派生特征提取脚本

从 OCS manifest 计算增强特征，支持 E28-FIX01 预注册的 13 个 C2 配置
+ 1 个 constant sanity check。

设计原则：
  - 纯函数：输入 manifest record dict → 输出特征值
  - 所有 epsilon / clip / fallback 为预注册常数
  - 不做任何归一化（归一化留给训练时 per-fold）
  - 不做特征选择（所有配置全量导出）

重要说明（1C-E29-FIX01）：
  - feature_definitions.json 是预注册静态定义，由此脚本读取但不覆盖。
  - 脚本运行态信息（n_records、sanity_check、npz_path等）写入
    feature_extraction_run_summary.json，保持预注册证据链完整。

使用：
    python feature_extract_ocs.py
    python feature_extract_ocs.py --ocs-manifest <path> --output-dir <path>

输出：
    v0.4_results/04_ocs_features/enhanced_ocs_features.npz (运行产物)
    v0.4_results/04_ocs_features/feature_extraction_run_summary.json (运行态摘要)
    v0.4_results/04_ocs_features/feature_definitions.json (预注册定义，已存在，不覆盖)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from collections import OrderedDict

import numpy as np

# ── 路径默认值 ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "v0.4_results"
OCS_MANIFEST_DEFAULT = (
    RESULTS_DIR / "01_fullrun" / "postprocess" / "ocs_manifest_v0_4_fullrun.json"
)
OUTPUT_DIR_DEFAULT = RESULTS_DIR / "04_ocs_features"

# ── 预注册常数 ──────────────────────────────────────────
EPSILON = 1e-8
RATIO_CLIP_MIN = 1e-8
RATIO_CLIP_MAX = 1e8
LOG_CLIP_MIN = -18.4   # ln(1e-8)
LOG_CLIP_MAX = 18.4    # ln(1e8)
MIN_PIXELS = 1          # 像素数下限，用于 per-pixel density 计算
UNIFORM_PRIOR = 1.0 / 3.0  # ocs_total → 0 时比率回退到均匀分布

# ── 特征族：纯函数实现 ──────────────────────────────────

def compute_ocs_features_baseline(rec):
    """Baseline 4 维原始积分 OCS（对照）。

    Returns:
        dict: {"ocs_total", "ocs_jinshuzhuti", "ocs_taiyangnengban", "ocs_yinshenban"}
    """
    return {
        "ocs_total": float(rec["ocs_total"]),
        "ocs_jinshuzhuti": float(rec["ocs_per_part"]["jinshuzhuti"]),
        "ocs_taiyangnengban": float(rec["ocs_per_part"]["taiyangnengban"]),
        "ocs_yinshenban": float(rec["ocs_per_part"]["yinshenban"]),
    }


def compute_ocs_features_R_ratio(rec):
    """R 族：per-part / total 比率。

    Scale-invariant 变换。当 ocs_total < EPSILON 时回退到均匀分布 [1/3, 1/3, 1/3]。
    另附加 validity flag 标记是否使用了回退值。

    Returns:
        dict: {"r_jinshuzhuti", "r_taiyangnengban", "r_yinshenban", "r_valid"}
    """
    total = rec["ocs_total"]
    valid = 1 if total > EPSILON else 0
    if valid:
        ocs = rec["ocs_per_part"]
        r_jin = np.clip(ocs["jinshuzhuti"] / total, RATIO_CLIP_MIN, RATIO_CLIP_MAX)
        r_tai = np.clip(ocs["taiyangnengban"] / total, RATIO_CLIP_MIN, RATIO_CLIP_MAX)
        r_yin = np.clip(ocs["yinshenban"] / total, RATIO_CLIP_MIN, RATIO_CLIP_MAX)
    else:
        r_jin = UNIFORM_PRIOR
        r_tai = UNIFORM_PRIOR
        r_yin = UNIFORM_PRIOR
    return {"r_jinshuzhuti": r_jin, "r_taiyangnengban": r_tai,
            "r_yinshenban": r_yin, "r_valid": valid}


def compute_ocs_features_I_interpart(rec):
    """I 族：部件间 OCS 比值。

    Returns:
        dict: {"ratio_j_t"}
    """
    ocs = rec["ocs_per_part"]
    jin = max(ocs["jinshuzhuti"], EPSILON)
    tai = max(ocs["taiyangnengban"], EPSILON)
    ratio = np.clip(jin / tai, RATIO_CLIP_MIN, RATIO_CLIP_MAX)
    return {"ratio_j_t": ratio}


def compute_ocs_features_N_density(rec):
    """N 族：per-pixel 平均 OCS（OCS 光度经 visibility pixel counts 归一化）。

    注意：此族特征使用 visibility pixel counts 作为分母，因此
    正结果归因必须写成"OCS photometric values normalized by visibility pixel counts"，
    不得声称完全独立于 visibility information。

    当 n_pixels_part < MIN_PIXELS 时，density 置为 0。

    Returns:
        dict: {"ocs_density_total", "ocs_density_jinshuzhuti",
               "ocs_density_taiyangnengban", "ocs_density_yinshenban"}
    """
    npix = rec.get("n_pixels_contributing", 0)
    ocs_density_total = (
        rec["ocs_total"] / max(npix, MIN_PIXELS) if npix >= MIN_PIXELS else 0.0
    )

    parts = rec["ocs_per_part"]
    npix_parts = rec.get("n_pixels_per_part", {})
    densities = {}
    for part_name in ["jinshuzhuti", "taiyangnengban", "yinshenban"]:
        npix_p = npix_parts.get(part_name, 0)
        ocs_val = parts.get(part_name, 0.0)
        densities[f"ocs_density_{part_name}"] = (
            ocs_val / max(npix_p, MIN_PIXELS) if npix_p >= MIN_PIXELS else 0.0
        )

    return {
        "ocs_density_total": ocs_density_total,
        "ocs_density_jinshuzhuti": densities["ocs_density_jinshuzhuti"],
        "ocs_density_taiyangnengban": densities["ocs_density_taiyangnengban"],
        "ocs_density_yinshenban": densities["ocs_density_yinshenban"],
    }


def compute_ocs_features_P_pixelfrac(rec):
    """P 族：纯几何像素占比（visibility control）。

    不含任何 OCS 光度信息。用于区分"OCS 贡献"与"几何可见性贡献"。

    Returns:
        dict: {"frac_jinshuzhuti", "frac_taiyangnengban", "frac_yinshenban",
               "visibility_ratio", "sun_vis_ratio"}
    """
    n_contrib = max(rec.get("n_pixels_contributing", 0), MIN_PIXELS)
    n_camera = max(rec.get("n_pixels_camera_visible", 0), MIN_PIXELS)
    n_sun = max(rec.get("n_pixels_sun_visible", 0), MIN_PIXELS)

    npix_parts = rec.get("n_pixels_per_part", {})
    fracs = {}
    for part_name in ["jinshuzhuti", "taiyangnengban", "yinshenban"]:
        npix_p = npix_parts.get(part_name, 0)
        fracs[f"frac_{part_name}"] = npix_p / n_contrib

    return {
        "frac_jinshuzhuti": fracs["frac_jinshuzhuti"],
        "frac_taiyangnengban": fracs["frac_taiyangnengban"],
        "frac_yinshenban": fracs["frac_yinshenban"],
        "visibility_ratio": n_contrib / n_camera,
        "sun_vis_ratio": n_sun / n_camera,
    }


def compute_ocs_features_L_log(rec, ratio_features=None, density_features=None):
    """L 族：log / log-ratio 稳定化。

    依赖 R 族和 I 族的输出做 log 变换。压缩动态范围，对称化比值。

    Args:
        rec: manifest record
        ratio_features: compute_ocs_features_R_ratio 的输出（可选，避免重复计算）
        density_features: compute_ocs_features_N_density 的输出（可选）

    Returns:
        dict: {"log_r_jinshuzhuti", "log_r_taiyangnengban", "log_ratio_j_t",
               "log_ocs_total", "log_density_total"}
    """
    if ratio_features is None:
        ratio_features = compute_ocs_features_R_ratio(rec)
    if density_features is None:
        density_features = compute_ocs_features_N_density(rec)

    log_r_jin = np.clip(np.log(max(ratio_features["r_jinshuzhuti"], EPSILON)),
                         LOG_CLIP_MIN, LOG_CLIP_MAX)
    log_r_tai = np.clip(np.log(max(ratio_features["r_taiyangnengban"], EPSILON)),
                         LOG_CLIP_MIN, LOG_CLIP_MAX)

    ocs = rec["ocs_per_part"]
    jin = max(ocs["jinshuzhuti"], EPSILON)
    tai = max(ocs["taiyangnengban"], EPSILON)
    log_ratio_j_t = np.clip(np.log(jin / tai), LOG_CLIP_MIN, LOG_CLIP_MAX)

    log_ocs_total = np.clip(np.log(max(rec["ocs_total"], EPSILON)),
                             LOG_CLIP_MIN, LOG_CLIP_MAX)
    log_density_total = np.clip(
        np.log(max(density_features["ocs_density_total"], EPSILON)),
        LOG_CLIP_MIN, LOG_CLIP_MAX)

    return {
        "log_r_jinshuzhuti": log_r_jin,
        "log_r_taiyangnengban": log_r_tai,
        "log_ratio_j_t": log_ratio_j_t,
        "log_ocs_total": log_ocs_total,
        "log_density_total": log_density_total,
    }


def compute_ocs_features_G_constant(rec):
    """G 族（已降级为 constant sanity check）：phase_angle_cos。

    在 phase63 fixed-roll 数据中，sun_dir 和 det_dir 为全数据集常量，
    因此此特征为常量列。仅用于 C1 代码自检：若输出非常量，说明代码有 bug。

    Returns:
        dict: {"phase_angle_cos"}
    """
    sun = np.array(rec["sun_dir"])
    det = np.array(rec["det_dir"])
    cos_phase = np.clip(np.dot(sun, det), -1.0, 1.0)
    return {"phase_angle_cos": cos_phase}


# ── 全特征计算（单条 record） ───────────────────────────

def compute_all_raw_features(rec):
    """计算单条 record 的全部原始派生特征。

    Returns:
        OrderedDict: 所有特征名 → 值
    """
    feats = OrderedDict()

    # Baseline
    feats.update(compute_ocs_features_baseline(rec))

    # R 族
    r_feats = compute_ocs_features_R_ratio(rec)
    feats.update(r_feats)

    # I 族
    feats.update(compute_ocs_features_I_interpart(rec))

    # N 族
    n_feats = compute_ocs_features_N_density(rec)
    feats.update(n_feats)

    # P 族
    feats.update(compute_ocs_features_P_pixelfrac(rec))

    # L 族（使用已计算的 R 和 N）
    l_feats = compute_ocs_features_L_log(rec, ratio_features=r_feats,
                                         density_features=n_feats)
    feats.update(l_feats)

    # G 族（constant check）
    feats.update(compute_ocs_features_G_constant(rec))

    return feats


# ── 配置构建 ────────────────────────────────────────────

# 预注册 14 个特征配置（含 1 个常量自检）
# 格式：(config_name, claim_class, feature_keys)
CONFIGS = [
    # ── A 组：photometric OCS-derived ──
    ("baseline_4dim", "photometric OCS", [
        "ocs_total", "ocs_jinshuzhuti", "ocs_taiyangnengban", "ocs_yinshenban"]),
    ("R_ratio_2d", "photometric OCS", [
        "r_jinshuzhuti", "r_taiyangnengban"]),
    ("R_ratio_3d", "photometric OCS", [
        "r_jinshuzhuti", "r_taiyangnengban", "r_yinshenban"]),
    ("I_interpart_1d", "photometric OCS", [
        "ratio_j_t"]),
    ("N_density_3d", "photometric OCS", [
        "ocs_density_total", "ocs_density_jinshuzhuti", "ocs_density_taiyangnengban"]),
    ("L_logratio_3d", "photometric OCS", [
        "log_r_jinshuzhuti", "log_r_taiyangnengban", "log_ratio_j_t"]),
    ("M1_ratio_log_5d", "photometric OCS", [
        "r_jinshuzhuti", "r_taiyangnengban",
        "log_r_jinshuzhuti", "log_r_taiyangnengban", "log_ratio_j_t"]),
    ("M3_density_ratio_5d", "photometric OCS", [
        "ocs_density_total", "ocs_density_jinshuzhuti", "ocs_density_taiyangnengban",
        "r_jinshuzhuti", "r_taiyangnengban"]),
    ("M4_log_density_ratio_9d", "photometric OCS", [
        "log_r_jinshuzhuti", "log_r_taiyangnengban", "log_ratio_j_t",
        "log_ocs_total",
        "ocs_density_total", "ocs_density_jinshuzhuti", "ocs_density_taiyangnengban",
        "r_jinshuzhuti", "r_taiyangnengban"]),

    # ── B 组：visibility-derived control ──
    ("P_pixelfrac_3d", "visibility control", [
        "frac_jinshuzhuti", "frac_taiyangnengban", "visibility_ratio"]),
    ("M5_pixelfrac_only_4d", "visibility control", [
        "frac_jinshuzhuti", "frac_taiyangnengban", "frac_yinshenban",
        "visibility_ratio"]),

    # ── C 组：mixed OCS+visibility ──
    ("M2_ratio_pixelfrac_5d", "mixed OCS+visibility", [
        "r_jinshuzhuti", "r_taiyangnengban",
        "frac_jinshuzhuti", "frac_taiyangnengban", "visibility_ratio"]),
    ("M6_all_nongeo_13d", "mixed OCS+visibility", [
        "r_jinshuzhuti", "r_taiyangnengban",
        "ratio_j_t",
        "ocs_density_total", "ocs_density_jinshuzhuti", "ocs_density_taiyangnengban",
        "frac_jinshuzhuti", "frac_taiyangnengban", "visibility_ratio",
        "log_r_jinshuzhuti", "log_r_taiyangnengban", "log_ratio_j_t",
        "log_ocs_total"]),

    # ── D 组：constant sanity check（不参与 C2 评估） ──
    ("constant_check_1d", "constant sanity check", [
        "phase_angle_cos"]),
]


def build_config_matrix(config_name, feature_keys, all_raw_features):
    """从全特征 dict 列表构建指定配置的特征矩阵。

    Args:
        config_name: 配置名
        feature_keys: 该配置使用的特征键列表
        all_raw_features: list of OrderedDict, 每条 record 的全体原始特征

    Returns:
        np.ndarray, shape (n_records, len(feature_keys))
    """
    n = len(all_raw_features)
    d = len(feature_keys)
    mat = np.empty((n, d), dtype=np.float32)
    for i, feats in enumerate(all_raw_features):
        for j, key in enumerate(feature_keys):
            mat[i, j] = feats[key]
    return mat


# ── 常量自检 ────────────────────────────────────────────

def run_constant_sanity_check(all_raw_features):
    """验证 constant_check_1d 的 phase_angle_cos 是否为常量。

    Returns:
        dict: {"is_constant": bool, "unique_values": int,
               "value": float or None, "message": str}
    """
    vals = np.array([f["phase_angle_cos"] for f in all_raw_features], dtype=np.float32)
    unique = np.unique(vals)
    is_const = len(unique) == 1
    return {
        "is_constant": is_const,
        "unique_values": len(unique),
        "value": float(unique[0]) if is_const else None,
        "message": (
            "PASS: phase_angle_cos is constant (as expected in phase63 fixed-roll)."
            if is_const else
            f"WARNING: phase_angle_cos has {len(unique)} unique values. "
            f"Expected constant. Check sun_dir/det_dir extraction logic."
        ),
    }


# ── 主入口 ──────────────────────────────────────────────

def extract_all_candidate_features(ocs_manifest_path=None, output_dir=None,
                                   save_npz=True, save_summary=True):
    """从 OCS manifest 提取全部候选特征。

    注意（1C-E29-FIX01）：
      - 不再生成 feature_definitions.json（该文件为预注册静态定义，已存在于仓库）
      - 运行态信息写入 feature_extraction_run_summary.json

    Args:
        ocs_manifest_path: OCS manifest JSON 路径
        output_dir: 输出目录
        save_npz: 是否保存 .npz 特征矩阵文件
        save_summary: 是否保存运行态 summary JSON

    Returns:
        dict: {
            "n_records": int,
            "configs": list of config dicts,
            "record_ids": list of str,
            "features": {config_name: np.ndarray},
            "sanity_check": dict,
            "summary_path": str or None,
            "npz_path": str or None,
        }
    """
    if ocs_manifest_path is None:
        ocs_manifest_path = str(OCS_MANIFEST_DEFAULT)
    if output_dir is None:
        output_dir = str(OUTPUT_DIR_DEFAULT)

    # ── 加载 manifest ──
    print(f"[INFO] Loading OCS manifest: {ocs_manifest_path}")
    with open(ocs_manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    records = manifest["records"]
    n_records = len(records)
    print(f"[INFO] Records loaded: {n_records}")

    # ── 计算全体原始特征 ──
    print("[INFO] Computing raw features for all records...")
    all_raw_features = []
    record_ids = []
    for i, rec in enumerate(records):
        feats = compute_all_raw_features(rec)
        all_raw_features.append(feats)
        record_ids.append(rec["record_id"])
        if (i + 1) % 500 == 0:
            print(f"  ... {i+1}/{n_records}")

    print(f"[INFO] Raw features computed: {len(all_raw_features[0])} fields")

    # ── 构建各配置的特征矩阵 ──
    print("[INFO] Building config matrices...")
    features = OrderedDict()
    config_metas = []
    for config_name, claim_class, feature_keys in CONFIGS:
        mat = build_config_matrix(config_name, feature_keys, all_raw_features)
        features[config_name] = mat
        config_metas.append({
            "config_name": config_name,
            "claim_class": claim_class,
            "dim": len(feature_keys),
            "feature_keys": feature_keys,
            "c2_participant": claim_class != "constant sanity check",
        })
        status = "C2" if claim_class != "constant sanity check" else "CHECK"
        print(f"  [{status}] {config_name}: {mat.shape}")

    # ── 常量自检 ──
    print("[INFO] Running constant sanity check...")
    sanity_result = run_constant_sanity_check(all_raw_features)
    print(f"  {sanity_result['message']}")

    # ── 验证预注册 expected_n_records ──
    pre_registered_def_path = os.path.join(output_dir, "feature_definitions.json")
    expected_n_records = None
    if os.path.exists(pre_registered_def_path):
        with open(pre_registered_def_path, "r", encoding="utf-8") as f:
            pre_registered = json.load(f)
            expected_n_records = pre_registered.get("expected_n_records")
            if expected_n_records is not None and expected_n_records != n_records:
                print(f"[ERROR] Record count mismatch!")
                print(f"  Expected (pre-registered): {expected_n_records}")
                print(f"  Actual (from manifest):    {n_records}")
                print(f"  Pre-registered definitions file should not be auto-adjusted.")
                sys.exit(1)
            else:
                print(f"[INFO] Record count matches pre-registered: {n_records}")

    # ── 检查 record_id 唯一性 ──
    record_id_unique = len(set(record_ids)) == len(record_ids)
    print(f"[INFO] Record IDs unique: {record_id_unique} ({len(set(record_ids))}/{len(record_ids)})")

    # ── 导出运行态 summary ──
    summary_path = None
    if save_summary:
        os.makedirs(output_dir, exist_ok=True)
        summary_path = os.path.join(output_dir, "feature_extraction_run_summary.json")

        summary = {
            "task": "1C-E29 OCS feature extraction — runtime summary",
            "execution_date": "2026-06-25",
            "source_manifest": os.path.basename(ocs_manifest_path),
            "source_manifest_full_path": os.path.abspath(ocs_manifest_path),
            "n_records": n_records,
            "expected_n_records": expected_n_records,
            "record_count_match": expected_n_records == n_records if expected_n_records else None,
            "record_id_unique": record_id_unique,
            "record_id_count": len(set(record_ids)),
            "raw_feature_fields": list(all_raw_features[0].keys()),
            "sanity_check": sanity_result,
            "configs_summary": [],
            "npz_path": None,  # will be filled after npz save
            "pre_registered_definitions_path": pre_registered_def_path if os.path.exists(pre_registered_def_path) else None,
        }

        for config_name, claim_class, feature_keys in CONFIGS:
            summary["configs_summary"].append({
                "config_name": config_name,
                "claim_class": claim_class,
                "dim": len(feature_keys),
                "feature_keys": feature_keys,
                "c2_participant": claim_class != "constant sanity check",
                "n_records": n_records,
            })

        # Save preliminary summary (npz_path to be updated after)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Runtime summary saved: {summary_path}")

    # ── 导出 .npz ──
    npz_path = None
    if save_npz:
        os.makedirs(output_dir, exist_ok=True)
        npz_path = os.path.join(output_dir, "enhanced_ocs_features.npz")
        npz_data = {name: mat for name, mat in features.items()}
        # 也保存 record_ids 以便对齐
        npz_data["record_ids"] = np.array(record_ids)
        np.savez_compressed(npz_path, **npz_data)
        print(f"[INFO] Feature matrices saved: {npz_path}")

        # Update summary with npz_path
        if save_summary and summary_path:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
            summary["npz_path"] = os.path.abspath(npz_path)
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Runtime summary updated with npz_path")

    print("[DONE] Feature extraction complete.")
    return {
        "n_records": n_records,
        "configs": config_metas,
        "record_ids": record_ids,
        "features": features,
        "sanity_check": sanity_result,
        "summary_path": summary_path,
        "npz_path": npz_path,
    }


# ── 便捷加载函数（供 C2 训练使用） ───────────────────────

def load_enhanced_features(npz_path=None):
    """加载增强特征 .npz 文件。

    Args:
        npz_path: enhanced_ocs_features.npz 路径

    Returns:
        dict: config_name → np.ndarray, + "record_ids" → np.ndarray
    """
    if npz_path is None:
        npz_path = str(OUTPUT_DIR_DEFAULT / "enhanced_ocs_features.npz")
    data = np.load(npz_path, allow_pickle=False)
    result = {key: data[key] for key in data.files}
    return result


def load_feature_definitions(json_path=None):
    """加载特征定义文件。

    Args:
        json_path: feature_definitions.json 路径

    Returns:
        dict
    """
    if json_path is None:
        json_path = str(OUTPUT_DIR_DEFAULT / "feature_definitions.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── CLI ─────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="1C-E29: OCS 派生特征提取脚本")
    parser.add_argument("--ocs-manifest", type=str,
                        default=str(OCS_MANIFEST_DEFAULT))
    parser.add_argument("--output-dir", type=str,
                        default=str(OUTPUT_DIR_DEFAULT))
    parser.add_argument("--skip-npz", action="store_true",
                        help="Skip .npz export (only write summary)")
    parser.add_argument("--skip-summary", action="store_true",
                        help="Skip summary.json export (only write .npz)")
    args = parser.parse_args()

    print("=" * 60)
    print("OCS Feature Extraction — 1C-E29")
    print(f"OCS manifest: {args.ocs_manifest}")
    print(f"Output dir:   {args.output_dir}")
    print("=" * 60)

    if not os.path.exists(args.ocs_manifest):
        print(f"[ERROR] OCS manifest not found: {args.ocs_manifest}")
        sys.exit(1)

    result = extract_all_candidate_features(
        ocs_manifest_path=args.ocs_manifest,
        output_dir=args.output_dir,
        save_npz=not args.skip_npz,
        save_summary=not args.skip_summary,
    )

    print(f"\nSummary:")
    print(f"  Records:              {result['n_records']}")
    print(f"  C2 participant configs: {sum(1 for c in result['configs'] if c['c2_participant'])}")
    print(f"  Constant check configs: {sum(1 for c in result['configs'] if not c['c2_participant'])}")
    print(f"  Sanity check:         {result['sanity_check']['message']}")
    print(f"  Runtime summary:      {result['summary_path']}")
    print(f"  NPZ:                  {result['npz_path']}")

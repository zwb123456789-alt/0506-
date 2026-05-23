# -*- coding: utf-8 -*-
"""
diag_subface_adaptive.py —— Step 7a 诊断：A 端 sub-face 自适应积分 vs B 端
==========================================================================
3 个代表姿态 per-part 对比：
  - face-center OCS (no_occ) → 当前 A 端方法
  - adaptive OCS  (no_occ) → sub-face 自适应积分
  - B-side OCS (diffuse-only & full) → 从现有 EXR 读取

不含遮挡（比较 no_occ），隔离镜面峰采样问题。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/02_blender/diag_subface_adaptive.py
"""

import os, sys, json, time as time_module, io
import numpy as np

# Windows 控制台 UTF-8
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

# 路径设置
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from config import SUN_VECTOR, DET_VECTOR, PART_FILES
from geometry import load_meshes, euler_to_matrix
from materials import get_material
from adaptive_integration import compute_vertex_normals, compute_ocs_adaptive

# B 端后处理模块
from brdf_postprocess import (
    read_multilayer_exr, compute_radiance_image, integrate_ocs,
    PART_PASS_INDEX,
)

# ---- 3 个代表姿态 ----
ATTITUDES = [
    # (yaw, pitch, 标签) — 须对齐 B 端 10° 网格
    (0.0,   0.0,  "正照"),
    (90.0, -40.0,  "斜射"),
    (150.0, -80.0, "强镜面/阴影"),
]

# B 端 EXR 目录
EXR_DIR = os.path.normpath(os.path.join(
    PROJECT_ROOT, "结果", "模块B_渲染", "run_20260519_backface_fix"))
META_PATH = os.path.join(EXR_DIR, "render_metadata.json")

# 自适应积分参数
ADAPTIVE_KWARGS = {
    "max_depth": 5,
    "noh_high": 0.96,
    "noh_range_thr": 0.001,
    "min_area_mm2": 0.01,
}


def fmt_exr_name(yaw, pitch):
    """yaw, pitch → EXR 文件名"""
    return f"yaw{yaw:06.2f}_pitch{pitch:+06.2f}_0001.exr"


def compute_A_face_center(meshes, sun_norm, det_norm, R):
    """A 端现有方法：面中心采样，无遮挡。返回 per-part OCS_no_occ."""
    R_T = R.T
    scale_sq = 1e-6  # mm² → m²
    sun_dir_M = sun_norm @ R_T
    det_dir_M = det_norm @ R_T

    result = {}
    for pn, mesh in meshes.items():
        normals_M = mesh.face_normals
        normals_I = normals_M @ R
        dot_sun = np.dot(normals_I, sun_norm)
        dot_det = np.dot(normals_I, det_norm)
        idx = np.where((dot_sun > 0) & (dot_det > 0))[0]

        if len(idx) == 0:
            result[pn] = {"ocs": 0.0, "faces": 0}
            continue

        areas = mesh.area_faces[idx]
        cos_i = np.dot(normals_I[idx], sun_norm)
        cos_r = np.dot(normals_I[idx], det_norm)
        mat = get_material(pn)

        # BRDF（面中心法线）
        H = sun_norm + det_norm
        H /= np.linalg.norm(H)
        NoH = np.maximum(np.dot(normals_I[idx], H), 0.0)
        f_r = mat["rho_d"] / np.pi + mat["rho_s"] * (NoH ** mat["n"])

        ocs = float(np.sum(areas * scale_sq * f_r * cos_i * cos_r))
        result[pn] = {"ocs": ocs, "faces": len(idx)}

    return result


def compute_A_adaptive(meshes, vertex_normals, sun_norm, det_norm, R):
    """A 端自适应积分，无遮挡。返回 per-part OCS + 统计."""
    result = {}
    for pn, mesh in meshes.items():
        mat = get_material(pn)
        stats = compute_ocs_adaptive(
            mesh, vertex_normals[pn], sun_norm, det_norm, R, mat,
            **ADAPTIVE_KWARGS)
        result[pn] = stats
    return result


def compute_B_side(exr_path, meta, diffuse_only=False):
    """从 EXR 计算 B 端 OCS。返回 per-part OCS + 像素数."""
    layers = read_multilayer_exr(exr_path)

    materials_orig = meta["materials"]
    if diffuse_only:
        materials_use = {pn: {**m, "rho_s": 0.0} for pn, m in materials_orig.items()}
    else:
        materials_use = materials_orig

    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)

    rad, mask_obj, pp = compute_radiance_image(
        layers, sun_dir, det_dir, materials_use, PART_PASS_INDEX)

    res = meta["resolution"]
    r_max = meta["r_max"]
    ortho_scale = 2.2 * r_max
    pixel_area = (ortho_scale / res) ** 2

    ocs_total = integrate_ocs(rad, pixel_area)

    # per-part
    idx = layers["IndexOB"].astype(np.int32)
    part_ocs = {}
    for pn, pid in PART_PASS_INDEX.items():
        m = mask_obj & (idx == pid)
        part_ocs[pn] = float(np.sum(rad[m]) * pixel_area) if m.any() else 0.0

    return {"total": ocs_total, "parts": part_ocs, "pixels": pp}


def print_separator(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


if __name__ == "__main__":
    # ---- 加载 B 端元数据 ----
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    sun_norm = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
    det_norm = DET_VECTOR / np.linalg.norm(DET_VECTOR)

    # ---- 加载网格 + 顶点法线 ----
    t0 = time_module.perf_counter()
    print("加载网格 (full accuracy) ...")
    meshes, total_faces = load_meshes(accuracy_level="full", verbose=True)
    dt_load = time_module.perf_counter() - t0
    print(f"加载耗时: {dt_load:.1f}s, 总面元: {total_faces:,}")

    print("\n计算顶点法线 ...")
    t0 = time_module.perf_counter()
    vertex_normals = {}
    for pn, mesh in meshes.items():
        vertex_normals[pn] = compute_vertex_normals(mesh)
    dt_vn = time_module.perf_counter() - t0
    print(f"顶点法线耗时: {dt_vn:.1f}s")

    # ---- 逐姿态对比 ----
    all_rows = []

    for yaw, pitch, label in ATTITUDES:
        print_separator(f"姿态: yaw={yaw}°, pitch={pitch}° ({label})")
        R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)

        # A 端：面中心
        t0 = time_module.perf_counter()
        res_fc = compute_A_face_center(meshes, sun_norm, det_norm, R)
        dt_fc = time_module.perf_counter() - t0

        # A 端：自适应
        t0 = time_module.perf_counter()
        res_ad = compute_A_adaptive(meshes, vertex_normals, sun_norm, det_norm, R)
        dt_ad = time_module.perf_counter() - t0

        # B 端：EXR
        exr_path = os.path.join(EXR_DIR, fmt_exr_name(yaw, pitch))
        has_B = os.path.exists(exr_path)
        res_B_full = None
        res_B_diff = None
        if has_B:
            res_B_full = compute_B_side(exr_path, meta, diffuse_only=False)
            res_B_diff = compute_B_side(exr_path, meta, diffuse_only=True)
        else:
            print(f"  [警告] 缺少 EXR: {exr_path}")

        # ---- 逐部件输出 ----
        print(f"\n  {'Part':15s} {'A_fc':>10s} {'A_ad':>10s} "
              f"{'B_diff':>10s} {'B_full':>10s} "
              f"{'ad/fc':>8s} {'ad/Bd':>8s} {'ad/Bf':>8s}  "
              f"{'fc_faces':>8s} {'ad_sdiv':>8s} {'ad_leaf':>8s} {'B_pix':>7s}")
        print(f"  {'-'*15} {'-'*10} {'-'*10} {'-'*10} {'-'*10} "
              f"{'-'*8} {'-'*8} {'-'*8}  "
              f"{'-'*8} {'-'*8} {'-'*8} {'-'*7}")

        total_fc = 0.0
        total_ad = 0.0
        total_Bd = 0.0
        total_Bf = 0.0

        for pn in ["jinshuzhuti", "taiyangnengban", "yinshenban"]:
            fc_ocs = res_fc[pn]["ocs"]
            ad_ocs = res_ad[pn]["ocs_no_occ"]
            fc_faces = res_fc[pn]["faces"]
            ad_sdiv = res_ad[pn]["n_subdivisions"]
            ad_leaf = res_ad[pn]["n_leaf_samples"]

            bd_ocs = res_B_diff["parts"][pn] if res_B_diff else float("nan")
            bf_ocs = res_B_full["parts"][pn] if res_B_full else float("nan")
            b_pix = res_B_full["pixels"].get(pn, 0) if res_B_full else 0

            total_fc += fc_ocs
            total_ad += ad_ocs
            if res_B_diff:
                total_Bd += bd_ocs
            if res_B_full:
                total_Bf += bf_ocs

            ad_fc = ad_ocs / fc_ocs if fc_ocs > 0 else float("nan")
            ad_bd = ad_ocs / bd_ocs if bd_ocs > 0 else float("nan")
            ad_bf = ad_ocs / bf_ocs if bf_ocs > 0 else float("nan")

            print(f"  {pn:15s} {fc_ocs:10.6f} {ad_ocs:10.6f} "
                  f"{bd_ocs:10.6f} {bf_ocs:10.6f} "
                  f"{ad_fc:8.3f} {ad_bd:8.3f} {ad_bf:8.3f}  "
                  f"{fc_faces:8,} {ad_sdiv:8,} {ad_leaf:8,} {b_pix:7,}")

        # 总计
        ad_fc_t = total_ad / total_fc if total_fc > 0 else float("nan")
        ad_bd_t = total_ad / total_Bd if total_Bd > 0 else float("nan")
        ad_bf_t = total_ad / total_Bf if total_Bf > 0 else float("nan")
        print(f"  {'─'*100}")
        print(f"  {'TOTAL':15s} {total_fc:10.6f} {total_ad:10.6f} "
              f"{total_Bd:10.6f} {total_Bf:10.6f} "
              f"{ad_fc_t:8.3f} {ad_bd_t:8.3f} {ad_bf_t:8.3f}")

        # 耗时
        print(f"\n  耗时: A_fc={dt_fc:.2f}s  A_ad={dt_ad:.2f}s")

        # 收集行
        for pn in ["jinshuzhuti", "taiyangnengban", "yinshenban"]:
            all_rows.append({
                "yaw": yaw, "pitch": pitch, "label": label,
                "part": pn,
                "ocs_fc": res_fc[pn]["ocs"],
                "ocs_ad": res_ad[pn]["ocs_no_occ"],
                "ocs_B_diff": res_B_diff["parts"][pn] if res_B_diff else float("nan"),
                "ocs_B_full": res_B_full["parts"][pn] if res_B_full else float("nan"),
                "fc_faces": res_fc[pn]["faces"],
                "ad_subdiv": res_ad[pn]["n_subdivisions"],
                "ad_leaf": res_ad[pn]["n_leaf_samples"],
                "B_pixels": res_B_full["pixels"].get(pn, 0) if res_B_full else 0,
                "ad_n_visible": res_ad[pn]["n_faces_visible"],
                "ad_n_checked": res_ad[pn]["n_faces_checked"],
            })

    # ---- 汇总 ----
    print_separator("汇总")
    print(f"  参数: max_depth={ADAPTIVE_KWARGS['max_depth']}, "
          f"noh_high={ADAPTIVE_KWARGS['noh_high']}, "
          f"noh_range={ADAPTIVE_KWARGS['noh_range_thr']}, "
          f"min_area={ADAPTIVE_KWARGS['min_area_mm2']} mm²")

    # 写 CSV
    out_dir = os.path.normpath(os.path.join(
        PROJECT_ROOT, "结果", "BRDF验证", "subface_adaptive_diag"))
    os.makedirs(out_dir, exist_ok=True)
    import csv
    csv_path = os.path.join(out_dir, "subface_adaptive_comparison.csv")
    fieldnames = [
        "yaw", "pitch", "label", "part",
        "ocs_fc", "ocs_ad", "ocs_B_diff", "ocs_B_full",
        "fc_faces", "ad_subdiv", "ad_leaf", "B_pixels",
        "ad_n_visible", "ad_n_checked",
        "ratio_ad_fc", "ratio_ad_Bdiff", "ratio_ad_Bfull",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_rows:
            fc = r["ocs_fc"]
            bd = r["ocs_B_diff"]
            bf = r["ocs_B_full"]
            ad = r["ocs_ad"]
            row = {k: r.get(k, "") for k in fieldnames}
            row["ratio_ad_fc"] = ad / fc if fc > 0 else ""
            row["ratio_ad_Bdiff"] = ad / bd if bd > 0 else ""
            row["ratio_ad_Bfull"] = ad / bf if bf > 0 else ""
            w.writerow(row)
    print(f"  CSV → {csv_path}")

    print("\n完成。")

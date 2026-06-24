# -*- coding: utf-8 -*-
"""
validate_v_sun_macro_on_image.py —— Phase 0 Step 5 验证（1C-E10）
================================================================================
任务：在 5 个已渲染 Step 4 姿态上，验证 V_sun_macro 对图像响应的乘法影响。

依据：
    - R25 Codex 审阅裁决（Q1-Q5）
    - 13 号 §12.7（V_sun_macro 对图像的影响验证）、§9.2（有效像素规则）
    - §8.2：I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)

边界（不得越界）：
    - 只跑 5 个姿态，不进入全量 2664 姿态生成
    - 复用 Step 4 已有 camera/sun EXR，不重渲染
    - 本轮 f_r 使用 B0 phong_like_provisional_baseline，作为 Step 5 validation proxy，
      不声称完整 BRDF 后处理链路（不做 corpus I_scale / manifest 体系）
    - Step 5 只验证乘法影响，不自称完成 Step 6

V_sun_macro 生成：
    复用 validate_shadow_consistency_fixed 的 camera->sun reprojection + depth comparison，
    使用 DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m。
    某 camera 前景点 shadowed（V=0）当且仅当 sun-view 在该点投影处存在更靠近太阳的
    前景面，即 depth_sun_expected - depth_sun_actual > epsilon。
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    import OpenEXR
    import Imath
except ImportError:
    print("[ERROR] 需要安装 OpenEXR 库")
    sys.exit(1)

# 复用 Step 4 验证脚本的投影/读取逻辑
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from validate_shadow_consistency_fixed import (
    get_sun_camera_params,
    world_to_sun_pixel,
    read_exr_channel,
    read_position_pass,
    read_depth_pass,
    BLENDER_FAR_PLANE,
)

# 复用 B0 材料
_CONFIG_DIR = os.path.join(_THIS_DIR, "..", "00_config")
if _CONFIG_DIR not in sys.path:
    sys.path.insert(0, _CONFIG_DIR)
from materials_v0_4 import get_material_b0, brdf_b0_phong_like  # noqa: E402


# ============================================================
# 配置
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")
SHADOW_PASSES_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "shadow_passes")
SHADOW_SUMMARY = os.path.join(V04_PROJECT, "v0.4_results", "00_validation",
                              "shadow_validation", "shadow_validation_summary.json")
OUTPUT_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "v_sun_macro_image_check")

# 观测几何（与 Step 4 一致）
SUN_VECTOR = np.array([1.0, 0.0, 0.3])
DET_VECTOR = np.array([0.5, -1.0, 0.1])
SUN_DIR = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
DET_DIR = DET_VECTOR / np.linalg.norm(DET_VECTOR)

# Step 4 校准批准阈值
DEPTH_EPSILON_M_FINAL = 0.7952109582768545

# 有效像素 eps（13 §9.2 / CR4-004）
NOL_EPS = 1e-6
NOV_EPS = 1e-6

# 验收容差
SHADOW_ZERO_TOL = 1e-7
VISIBLE_PRESERVE_TOL = 1e-6

# log1p PNG 映射参数（D3 初始 alpha=10）
LOG1P_ALPHA = 10.0

# IndexOB -> 部件名（render_20_attitudes_shadow.py PART_PASS_INDEX）
INDEXOB_TO_PART = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}

# 固定 5 姿态（R25 Q2）
SELECTED_ATTITUDES = [
    "yaw180_pitch+000_roll+000",
    "yaw150_pitch+025_roll+000",
    "yaw000_pitch+000_roll+000",
    "yaw090_pitch+000_roll+000",
    "yaw300_pitch-025_roll+000",
]


# ============================================================
# EXR 读写工具
# ============================================================
def read_normal_pass(exr_file):
    nx = read_exr_channel(exr_file, "ViewLayer.Normal.X")
    ny = read_exr_channel(exr_file, "ViewLayer.Normal.Y")
    nz = read_exr_channel(exr_file, "ViewLayer.Normal.Z")
    return np.stack([nx, ny, nz], axis=-1)


def read_indexob_pass(exr_file):
    return read_exr_channel(exr_file, "ViewLayer.IndexOB.X")


def write_exr_single(path, arr):
    """写出单通道 (R) float32 EXR。arr: (H, W)。失败则抛异常。"""
    h, w = arr.shape
    header = OpenEXR.Header(w, h)
    header['channels'] = {'R': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))}
    out = OpenEXR.OutputFile(path, header)
    out.writePixels({'R': arr.astype(np.float32).tobytes()})
    out.close()


def write_png_gray(path, arr01):
    """写出 8-bit 灰度 PNG，arr01 in [0,1]。返回量化重建误差 max(|recon - arr01|)。"""
    from PIL import Image
    arr01 = np.clip(arr01, 0.0, 1.0)
    png8 = np.round(arr01 * 255.0).astype(np.uint8)
    Image.fromarray(png8, mode='L').save(path)
    recon = png8.astype(np.float64) / 255.0
    return float(np.max(np.abs(recon - arr01)))


# ============================================================
# V_sun_macro 生成（复用 Step 4 reprojection）
# ============================================================
def compute_v_sun_macro(position_camera, foreground_camera,
                        depth_sun_actual, position_sun, r_max, epsilon):
    """
    返回 (H, W) 的 V_sun_macro mask（仅 0/1，camera 前景内有效；背景填 0）。

    某 camera 前景点 shadowed (V=0) 当且仅当其投影到 sun-view 的像素处，
    存在更靠近太阳的前景面：depth_sun_expected - depth_sun_actual > epsilon。
    其余前景点（含投影出界、sun-view 背景、同面）判为 sun-visible (V=1)。
    """
    H, W = foreground_camera.shape
    V = np.zeros((H, W), dtype=np.float32)

    sun_cam_pos, sun_view_dir, ortho_scale, resolution = get_sun_camera_params(r_max)

    fg_idx = np.where(foreground_camera)
    if len(fg_idx[0]) == 0:
        return V

    positions_fg = position_camera[fg_idx]  # (N, 3)
    u_sun, v_sun, in_bounds = world_to_sun_pixel(
        positions_fg, sun_cam_pos, sun_view_dir, ortho_scale, resolution
    )

    # 默认全部 sun-visible
    v_fg = np.ones(len(fg_idx[0]), dtype=np.float32)

    # 只对投影在界内的点做遮挡判定
    ib = in_bounds
    if np.any(ib):
        u_in = u_sun[ib].astype(int)
        v_in = v_sun[ib].astype(int)
        pos_in = positions_fg[ib]

        depth_sun_at = depth_sun_actual[v_in, u_in]
        pos_sun_at = position_sun[v_in, u_in]
        r_sun_at = np.linalg.norm(pos_sun_at, axis=-1)
        sun_fg = (depth_sun_at < BLENDER_FAR_PLANE) & (r_sun_at > 0)

        # 预期 sun depth（同 Step 4 零点定义）
        depth_expected = np.dot(pos_in - sun_cam_pos, sun_view_dir)

        # shadowed: sun-view 该处有更靠近太阳的前景面
        shadowed_in = np.zeros(int(np.sum(ib)), dtype=bool)
        shadowed_in[sun_fg] = (depth_expected[sun_fg] - depth_sun_at[sun_fg]) > epsilon

        v_in_vals = np.ones(int(np.sum(ib)), dtype=np.float32)
        v_in_vals[shadowed_in] = 0.0

        v_fg[ib] = v_in_vals

    V[fg_idx] = v_fg
    return V


# ============================================================
# B0 f_r 逐像素计算（validation proxy）
# ============================================================
def compute_fr_map(normal_map, indexob_map, foreground_camera):
    """逐像素 B0 phong-like f_r。背景置 0。"""
    H, W = foreground_camera.shape
    fr = np.zeros((H, W), dtype=np.float64)
    fg_idx = np.where(foreground_camera)
    normals = normal_map[fg_idx]              # (N, 3)
    idx_vals = np.round(indexob_map[fg_idx]).astype(int)

    fr_fg = np.zeros(len(idx_vals), dtype=np.float64)
    for part_id in np.unique(idx_vals):
        part_name = INDEXOB_TO_PART.get(int(part_id))
        mat = get_material_b0(part_name) if part_name else get_material_b0("__fallback__")
        sel = idx_vals == part_id
        fr_fg[sel] = brdf_b0_phong_like(normals[sel], SUN_DIR, DET_DIR, mat)
    fr[fg_idx] = fr_fg
    return fr


# ============================================================
# 单姿态处理
# ============================================================
def process_attitude(label, r_max):
    camera_exr = os.path.join(SHADOW_PASSES_DIR, f"{label}_camera.exr")
    sun_exr = os.path.join(SHADOW_PASSES_DIR, f"{label}_sun.exr")
    for p in (camera_exr, sun_exr):
        if not os.path.isfile(p):
            raise FileNotFoundError(f"缺失 EXR: {p}")

    position_camera = read_position_pass(camera_exr)
    depth_camera = read_depth_pass(camera_exr)
    normal_map = read_normal_pass(camera_exr)
    indexob_map = read_indexob_pass(camera_exr)

    depth_sun_actual = read_depth_pass(sun_exr)
    position_sun = read_position_pass(sun_exr)

    H, W = depth_camera.shape
    r_camera = np.linalg.norm(position_camera, axis=-1)
    foreground_camera = (depth_camera < BLENDER_FAR_PLANE) & (r_camera > 0)

    # V_sun_macro
    V = compute_v_sun_macro(position_camera, foreground_camera,
                            depth_sun_actual, position_sun, r_max, DEPTH_EPSILON_M_FINAL)

    # NoL / NoV
    NoL = np.zeros((H, W), dtype=np.float64)
    NoV = np.zeros((H, W), dtype=np.float64)
    fg_idx = np.where(foreground_camera)
    n_fg = normal_map[fg_idx]
    NoL[fg_idx] = np.maximum(np.dot(n_fg, SUN_DIR), 0.0)
    NoV[fg_idx] = np.maximum(np.dot(n_fg, DET_DIR), 0.0)

    # 有效像素：camera fg AND NoV>eps AND NoL>eps
    valid = foreground_camera & (NoV > NOV_EPS) & (NoL > NOL_EPS)

    # f_r
    fr = compute_fr_map(normal_map, indexob_map, foreground_camera)

    # I_linear（只在有效像素非零）
    I_base = np.zeros((H, W), dtype=np.float64)
    I_base[valid] = fr[valid] * NoL[valid]
    I_without = I_base.copy()
    I_with = I_base * V  # V in {0,1}

    return {
        "label": label,
        "H": H, "W": W,
        "foreground_camera": foreground_camera,
        "valid": valid,
        "V": V,
        "NoL": NoL, "NoV": NoV,
        "fr": fr,
        "I_without": I_without,
        "I_with": I_with,
    }


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 80)
    print("Phase 0 Step 5: V_sun_macro 对图像影响验证 (1C-E10)")
    print("=" * 80)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # r_max（来自 Step 4 summary）
    with open(SHADOW_SUMMARY, 'r', encoding='utf-8') as f:
        summary4 = json.load(f)
    r_max = summary4["r_max"]
    print(f"r_max = {r_max}")
    print(f"DEPTH_EPSILON_M_FINAL = {DEPTH_EPSILON_M_FINAL}")

    # 选定姿态写出
    sel_path = os.path.join(OUTPUT_DIR, "selected_attitudes.json")
    with open(sel_path, 'w', encoding='utf-8') as f:
        json.dump({"selected": SELECTED_ATTITUDES, "r_max": r_max,
                   "depth_epsilon_m_final": DEPTH_EPSILON_M_FINAL}, f, indent=2, ensure_ascii=False)

    blockers = []

    # Pass 1：处理 5 姿态，收集 I_without 以确定固定 I_scale_step5
    processed = []
    for label in SELECTED_ATTITUDES:
        print(f"\n--- {label} ---")
        try:
            d = process_attitude(label, r_max)
        except Exception as e:
            blockers.append(f"{label}: 处理异常 {e}")
            import traceback; traceback.print_exc()
            continue
        # V_sun_macro 仅 0/1 检查
        uniq = np.unique(d["V"])
        if not np.all(np.isin(uniq, [0.0, 1.0])):
            blockers.append(f"{label}: V_sun_macro 含非 0/1 值 {uniq}")
        processed.append(d)
        print(f"  fg={int(d['foreground_camera'].sum())} valid={int(d['valid'].sum())} "
              f"I_without max={d['I_without'].max():.6e}")

    if len(processed) < len(SELECTED_ATTITUDES):
        blockers.append(f"仅完成 {len(processed)}/{len(SELECTED_ATTITUDES)} 姿态处理")

    # 固定 I_scale_step5 = 5 姿态 I_without 全局最大（禁止 per-frame 归一化）
    I_scale_step5 = max((float(d["I_without"].max()) for d in processed), default=0.0)
    if I_scale_step5 <= 0:
        blockers.append("I_scale_step5 <= 0，无法生成 log1p PNG")
        I_scale_step5 = 1.0
    print(f"\nI_scale_step5 (固定) = {I_scale_step5:.6e}")

    log1p_denom = np.log1p(LOG1P_ALPHA)

    def to_log1p_png01(I):
        return np.log1p(LOG1P_ALPHA * (I / I_scale_step5)) / log1p_denom

    # Pass 2：验收 + 写产物
    per_attitude = []
    for d in processed:
        label = d["label"]
        valid = d["valid"]
        V = d["V"]
        I_with = d["I_with"]
        I_without = d["I_without"]

        shadowed_valid = valid & (V == 0)
        sun_visible_valid = valid & (V == 1)

        # 验收 3: V==0 有效像素 I_with 必须归零
        shadow_zero_violation = int(np.sum(shadowed_valid & (np.abs(I_with) > SHADOW_ZERO_TOL)))
        # 验收 4: V==1 有效像素 I_with == I_without
        visible_preserve_violation = int(np.sum(
            sun_visible_valid & (np.abs(I_with - I_without) > VISIBLE_PRESERVE_TOL)))

        # 写产物
        np.save(os.path.join(OUTPUT_DIR, f"{label}_v_sun_macro.npy"), V.astype(np.float32))
        png_v_err = write_png_gray(os.path.join(OUTPUT_DIR, f"{label}_v_sun_macro.png"),
                                   V.astype(np.float64))

        exr_ok = True
        try:
            write_exr_single(os.path.join(OUTPUT_DIR, f"{label}_i_linear_without_vsun.exr"), I_without)
            write_exr_single(os.path.join(OUTPUT_DIR, f"{label}_i_linear_with_vsun.exr"), I_with)
        except Exception as e:
            exr_ok = False
            blockers.append(f"{label}: EXR 写出失败 {e}")

        # log1p PNG（固定 I_scale）
        l_without = to_log1p_png01(I_without)
        l_with = to_log1p_png01(I_with)
        png_sync_a = write_png_gray(os.path.join(OUTPUT_DIR, f"{label}_brdf_without_vsun.png"), l_without)
        png_sync_b = write_png_gray(os.path.join(OUTPUT_DIR, f"{label}_brdf_with_vsun.png"), l_with)
        png_sync_max_abs_diff = max(png_sync_a, png_sync_b)

        status = "PASS"
        if shadow_zero_violation > 0 or visible_preserve_violation > 0 or not exr_ok:
            status = "FAIL"
        # PNG 量化误差应 <= 0.5/255
        if png_sync_max_abs_diff > (0.5 / 255.0 + 1e-9):
            status = "FAIL"
            blockers.append(f"{label}: PNG/EXR log1p 映射量化误差超限 {png_sync_max_abs_diff}")

        rec = {
            "label": label,
            "foreground_count": int(d["foreground_camera"].sum()),
            "valid_response_count": int(valid.sum()),
            "shadowed_valid_count": int(shadowed_valid.sum()),
            "sun_visible_valid_count": int(sun_visible_valid.sum()),
            "shadow_zero_violation_count": shadow_zero_violation,
            "visible_preserve_violation_count": visible_preserve_violation,
            "png_sync_max_abs_diff": png_sync_max_abs_diff,
            "v_mask_png_quant_err": png_v_err,
            "exr_written": exr_ok,
            "status": status,
        }
        per_attitude.append(rec)
        print(f"  [{status}] valid={rec['valid_response_count']} "
              f"shadowed={rec['shadowed_valid_count']} visible={rec['sun_visible_valid_count']} "
              f"zero_viol={shadow_zero_violation} preserve_viol={visible_preserve_violation} "
              f"png_sync={png_sync_max_abs_diff:.2e}")

    all_pass = (len(per_attitude) == len(SELECTED_ATTITUDES)
                and all(r["status"] == "PASS" for r in per_attitude)
                and len(blockers) == 0)
    overall = "COMPLETE" if all_pass else "NOT_COMPLETE"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "task": "1C-E10 Phase0 Step5 V_sun_macro image impact validation",
        "overall_status": overall,
        "depth_epsilon_m_final": DEPTH_EPSILON_M_FINAL,
        "r_max": r_max,
        "sun_vector": SUN_VECTOR.tolist(),
        "det_vector": DET_VECTOR.tolist(),
        "i_scale_step5": I_scale_step5,
        "i_scale_policy": "fixed = max(I_without_vsun over 5 attitudes); no per-frame normalization",
        "log1p_alpha": LOG1P_ALPHA,
        "brdf_branch": "B0_phong_like_provisional_baseline",
        "brdf_proxy_note": "Step 5 validation proxy: B0 per-part f_r via IndexOB; NOT full BRDF post-processing chain (Step 6).",
        "valid_pixel_rule": "camera_foreground AND NoV>1e-6 AND NoL>1e-6",
        "shadow_zero_tol": SHADOW_ZERO_TOL,
        "visible_preserve_tol": VISIBLE_PRESERVE_TOL,
        "selected_attitudes": SELECTED_ATTITUDES,
        "per_attitude": per_attitude,
        "blockers": blockers,
    }
    with open(os.path.join(OUTPUT_DIR, "v_sun_macro_image_check_summary.json"),
              'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"OVERALL: {overall}")
    if blockers:
        print("阻断项:")
        for b in blockers:
            print("  -", b)
    print("=" * 80)
    return 0 if overall == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())

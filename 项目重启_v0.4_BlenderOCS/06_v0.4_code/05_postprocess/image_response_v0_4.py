# -*- coding: utf-8 -*-
"""
image_response_v0_4.py —— v0.4 图像响应后处理模块
====================================================
负责从 camera-view geometry pass 和 sun shadow pass 生成最终图像产物。

依据：
    - 13 号 §8.2：I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)
    - 13 号 §9.2：有效像素规则（NoV > eps 且 NoL > eps）
    - 14 号 §3.2：image_manifest 字段规范

输出：
    - I_linear.exr：线性辐亮度（float32，canonical raw data）
    - log1p PNG：训练输入（8-bit，按 log1p 映射）
    - 统计字段：n_pixels_camera_visible / n_pixels_nol_positive / n_pixels_contributing
"""

import os
import sys
import numpy as np

try:
    import OpenEXR
    import Imath
except ImportError:
    print("[ERROR] 需要安装 OpenEXR 库")
    sys.exit(1)

# 复用 validation 工具
_VALIDATION_DIR = os.path.join(os.path.dirname(__file__), "..", "10_validation")
if _VALIDATION_DIR not in sys.path:
    sys.path.insert(0, _VALIDATION_DIR)

from validate_shadow_consistency_fixed import (
    read_exr_channel,
    read_position_pass,
    read_depth_pass,
    BLENDER_FAR_PLANE,
)

# 复用 Step 5 的 V_sun_macro 生成
from validate_v_sun_macro_on_image import (
    compute_v_sun_macro,
    read_normal_pass,
    read_indexob_pass,
    get_sun_camera_params,
)

# 复用材料
_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "00_config")
if _CONFIG_DIR not in sys.path:
    sys.path.insert(0, _CONFIG_DIR)
from materials_v0_4 import get_material_b0, brdf_b0_phong_like


# ============================================================
# 配置常量
# ============================================================
NOL_EPS = 1e-6
NOV_EPS = 1e-6


# ============================================================
# EXR/PNG 写出
# ============================================================
def write_exr_single(path, arr):
    """写出单通道 (R) float32 EXR。arr: (H, W)。"""
    h, w = arr.shape
    header = OpenEXR.Header(w, h)
    header['channels'] = {'R': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))}
    out = OpenEXR.OutputFile(path, header)
    out.writePixels({'R': arr.astype(np.float32).tobytes()})
    out.close()


def write_png_gray(path, arr01):
    """写出 8-bit 灰度 PNG，arr01 in [0,1]。"""
    from PIL import Image
    arr01 = np.clip(arr01, 0.0, 1.0)
    png8 = np.round(arr01 * 255.0).astype(np.uint8)
    Image.fromarray(png8, mode='L').save(path)


# ============================================================
# BRDF 后处理核心函数
# ============================================================
def compute_brdf_response(
    camera_exr_path,
    sun_exr_path,
    sun_dir,
    det_dir,
    r_max,
    depth_epsilon_m,
    brdf_branch="B0",
    indexob_to_part=None,
):
    """
    计算单姿态的 BRDF 图像响应。

    参数:
        camera_exr_path: camera-view geometry pass EXR 路径
        sun_exr_path: sun-view depth EXR 路径
        sun_dir: 太阳方向（已归一化），shape (3,)
        det_dir: 探测器方向（已归一化），shape (3,)
        r_max: 模型包围球半径
        depth_epsilon_m: sun shadow 深度容差
        brdf_branch: BRDF 分支（"B0" | "GGX"）
        indexob_to_part: IndexOB -> 部件名映射，默认 {1: jinshuzhuti, 2: taiyangnengban, 3: yinshenban}

    返回:
        dict: {
            "I_linear": (H, W) 线性辐亮度，
            "V_sun_macro": (H, W) sun visibility mask (0/1),
            "foreground_camera": (H, W) bool，camera 前景,
            "valid_response": (H, W) bool，有效响应像素（NoV>eps AND NoL>eps）,
            "n_pixels_camera_visible": int,
            "n_pixels_nol_positive": int,
            "n_pixels_sun_visible": int,
            "n_pixels_contributing": int,
            "NoL": (H, W) 余弦项,
            "NoV": (H, W) 视角余弦,
            "fr": (H, W) BRDF 值,
        }
    """
    if indexob_to_part is None:
        indexob_to_part = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}

    # 读取 camera-view passes
    position_camera = read_position_pass(camera_exr_path)
    depth_camera = read_depth_pass(camera_exr_path)
    normal_map = read_normal_pass(camera_exr_path)
    indexob_map = read_indexob_pass(camera_exr_path)

    # 读取 sun-view passes
    depth_sun_actual = read_depth_pass(sun_exr_path)
    position_sun = read_position_pass(sun_exr_path)

    H, W = depth_camera.shape
    r_camera = np.linalg.norm(position_camera, axis=-1)
    foreground_camera = (depth_camera < BLENDER_FAR_PLANE) & (r_camera > 0)

    # 生成 V_sun_macro
    V_sun_macro = compute_v_sun_macro(
        position_camera, foreground_camera,
        depth_sun_actual, position_sun, r_max, depth_epsilon_m
    )

    # NoL / NoV
    NoL = np.zeros((H, W), dtype=np.float64)
    NoV = np.zeros((H, W), dtype=np.float64)
    fg_idx = np.where(foreground_camera)
    n_fg = normal_map[fg_idx]
    NoL[fg_idx] = np.maximum(np.dot(n_fg, sun_dir), 0.0)
    NoV[fg_idx] = np.maximum(np.dot(n_fg, det_dir), 0.0)

    # 有效响应像素：camera fg AND NoV>eps AND NoL>eps（13 §9.2）
    valid_response = foreground_camera & (NoV > NOV_EPS) & (NoL > NOL_EPS)

    # f_r（逐像素 BRDF）
    fr = np.zeros((H, W), dtype=np.float64)
    valid_idx = np.where(valid_response)
    normals_valid = normal_map[valid_idx]
    idx_vals = np.round(indexob_map[valid_idx]).astype(int)

    fr_valid = np.zeros(len(idx_vals), dtype=np.float64)
    for part_id in np.unique(idx_vals):
        part_name = indexob_to_part.get(int(part_id))
        if brdf_branch == "B0":
            mat = get_material_b0(part_name) if part_name else get_material_b0("__fallback__")
            sel = idx_vals == part_id
            fr_valid[sel] = brdf_b0_phong_like(normals_valid[sel], sun_dir, det_dir, mat)
        else:
            raise NotImplementedError(f"BRDF 分支 {brdf_branch} 尚未实现")
    fr[valid_idx] = fr_valid

    # I_linear = f_r · NoL · V_sun_macro（13 §8.2 / CR4-001）
    I_linear = np.zeros((H, W), dtype=np.float64)
    I_linear[valid_response] = fr[valid_response] * NoL[valid_response] * V_sun_macro[valid_response]

    # 统计字段（14 §3.1 / CR4-006）
    n_pixels_camera_visible = int(foreground_camera.sum())
    n_pixels_nol_positive = int((foreground_camera & (NoL > NOL_EPS)).sum())
    n_pixels_sun_visible = int((foreground_camera & (V_sun_macro == 1)).sum())
    n_pixels_contributing = int((valid_response & (V_sun_macro == 1)).sum())

    return {
        "I_linear": I_linear.astype(np.float32),
        "V_sun_macro": V_sun_macro.astype(np.float32),
        "foreground_camera": foreground_camera,
        "valid_response": valid_response,
        "n_pixels_camera_visible": n_pixels_camera_visible,
        "n_pixels_nol_positive": n_pixels_nol_positive,
        "n_pixels_sun_visible": n_pixels_sun_visible,
        "n_pixels_contributing": n_pixels_contributing,
        "NoL": NoL.astype(np.float32),
        "NoV": NoV.astype(np.float32),
        "fr": fr.astype(np.float32),
    }


def apply_log1p_transform(I_linear, I_scale, log1p_alpha=10.0):
    """
    应用 log1p 变换（13 §8.2 Step 3）。

    参数:
        I_linear: (H, W) 线性辐亮度
        I_scale: 全局归一化因子
        log1p_alpha: log1p 参数（默认 10.0）

    返回:
        (H, W) log1p 变换后的 [0, 1] 值
    """
    I_norm = I_linear / I_scale
    log1p_denom = np.log1p(log1p_alpha)
    return np.log1p(log1p_alpha * I_norm) / log1p_denom


def write_image_outputs(
    I_linear,
    output_prefix,
    I_scale,
    log1p_alpha=10.0,
):
    """
    写出图像产物：EXR + log1p PNG。

    参数:
        I_linear: (H, W) 线性辐亮度
        output_prefix: 输出路径前缀（不含扩展名）
        I_scale: 全局归一化因子
        log1p_alpha: log1p 参数

    返回:
        dict: {"exr_path": ..., "png_path": ...}
    """
    exr_path = f"{output_prefix}_linear.exr"
    png_path = f"{output_prefix}_brdf.png"

    write_exr_single(exr_path, I_linear)

    I_log = apply_log1p_transform(I_linear, I_scale, log1p_alpha)
    write_png_gray(png_path, I_log)

    return {"exr_path": exr_path, "png_path": png_path}

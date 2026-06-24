# -*- coding: utf-8 -*-
"""
ocs_integration_v0_4.py —— v0.4 OCS 积分后处理模块
==================================================
负责从 BRDF 响应图像积分出 per-frame OCS。

依据：
    - 13 号 §6.2：OCS = Σ A_pixel · f_r(p) · NoL(p) · V_sun_macro(p)
    - 13 号 §9.2：有效像素规则
    - 14 号 §3.1：ocs_manifest 字段规范（record_id / 四类像素统计 / per-part OCS）

输出：
    - per-frame OCS JSON：包含 ocs_total, ocs_per_part, 像素统计
"""

import numpy as np
import json


# ============================================================
# OCS 积分核心函数
# ============================================================
def compute_ocs_from_brdf_response(
    brdf_result,
    pixel_area_m2,
    indexob_map,
    indexob_to_part=None,
):
    """
    从 BRDF 响应结果积分出 OCS。

    参数:
        brdf_result: compute_brdf_response() 返回的字典
        pixel_area_m2: 单像素物理面积（m²）
        indexob_map: (H, W) IndexOB pass
        indexob_to_part: IndexOB -> 部件名映射

    返回:
        dict: {
            "ocs_total": float,
            "ocs_per_part": {part_name: float, ...},
            "n_pixels_per_part": {part_name: int, ...},
            "n_pixels_camera_visible": int,
            "n_pixels_nol_positive": int,
            "n_pixels_sun_visible": int,
            "n_pixels_contributing": int,
        }
    """
    if indexob_to_part is None:
        indexob_to_part = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}

    I_linear = brdf_result["I_linear"]
    valid_response = brdf_result["valid_response"]
    V_sun_macro = brdf_result["V_sun_macro"]

    # 贡献像素：valid_response AND V_sun_macro == 1
    contributing = valid_response & (V_sun_macro == 1)

    # OCS 总量（13 §6.2）
    ocs_total = float(pixel_area_m2 * I_linear[contributing].sum())

    # Per-part OCS
    ocs_per_part = {}
    n_pixels_per_part = {}

    idx_vals = np.round(indexob_map).astype(int)
    for part_id, part_name in indexob_to_part.items():
        part_mask = (idx_vals == part_id) & contributing
        ocs_per_part[part_name] = float(pixel_area_m2 * I_linear[part_mask].sum())
        n_pixels_per_part[part_name] = int(part_mask.sum())

    return {
        "ocs_total": ocs_total,
        "ocs_per_part": ocs_per_part,
        "n_pixels_per_part": n_pixels_per_part,
        "n_pixels_camera_visible": brdf_result["n_pixels_camera_visible"],
        "n_pixels_nol_positive": brdf_result["n_pixels_nol_positive"],
        "n_pixels_sun_visible": brdf_result["n_pixels_sun_visible"],
        "n_pixels_contributing": brdf_result["n_pixels_contributing"],
    }


def write_ocs_json(ocs_result, output_path, record_id, yaw_deg, pitch_deg, geom_id="phase63"):
    """
    写出 per-frame OCS JSON（符合 14 号 manifest record 格式）。

    参数:
        ocs_result: compute_ocs_from_brdf_response() 返回的字典
        output_path: 输出 JSON 路径
        record_id: 记录标识符（例如 "phase63_yaw000_pitch+000"）
        yaw_deg: yaw 角度
        pitch_deg: pitch 角度
        geom_id: 几何标识符（默认 "phase63"）
    """
    record = {
        "record_id": record_id,
        "yaw_deg": yaw_deg,
        "pitch_deg": pitch_deg,
        "geom_id": geom_id,
        "ocs_total": ocs_result["ocs_total"],
        "ocs_per_part": ocs_result["ocs_per_part"],
        "n_pixels_camera_visible": ocs_result["n_pixels_camera_visible"],
        "n_pixels_nol_positive": ocs_result["n_pixels_nol_positive"],
        "n_pixels_sun_visible": ocs_result["n_pixels_sun_visible"],
        "n_pixels_contributing": ocs_result["n_pixels_contributing"],
        "n_pixels_per_part": ocs_result["n_pixels_per_part"],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

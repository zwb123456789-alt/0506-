# -*- coding: utf-8 -*-
"""
materials.py —— BRDF 材料数据库
================================
统一的部件材料 BRDF 参数（Lambert + Phong 简化模型）。

【参数含义】
- rho_d : 漫反射系数（diffuse albedo）
- rho_s : 镜面反射系数（specular albedo）
- n     : Phong 指数（specular sharpness）

BRDF 公式：
    f_r = rho_d / π  +  rho_s * (cos α)^n
其中 α 为半程向量 h = (s + d)/|s + d| 与法向量的夹角。
"""

import numpy as np


MATERIAL_DB = {
    "jinshuzhuti": {
        "desc":   "卫星金属主体（铝合金/镀铝外壳）",
        "simple": {"brdf_model": "legacy_phong", "rho_d": 0.20, "rho_s": 0.60, "n": 80},
    },
    "taiyangnengban": {
        "desc":   "太阳能电池板（玻璃盖片+半导体）",
        "simple": {"brdf_model": "legacy_phong", "rho_d": 0.15, "rho_s": 0.10, "n": 20},
    },
    "yinshenban": {
        "desc":   "隐身/暗表面涂层（低反射率黑色涂层）",
        "simple": {"brdf_model": "legacy_phong", "rho_d": 0.08, "rho_s": 0.02, "n": 10},
    },
}

# 部件未在数据库中时的兜底参数
DEFAULT_MAT = {"brdf_model": "legacy_phong", "rho_d": 0.20, "rho_s": 0.30, "n": 30}


# GGX nominal 参数（与 ocs_project/07_brdf/brdf_models.py 的 MATERIAL_DB_GGX 一致）
_GGX_DB = {
    "jinshuzhuti":    {"brdf_model": "ggx", "base_color": 0.91, "metallic": 1.0, "roughness": 0.20, "F0": 0.91},
    "taiyangnengban": {"brdf_model": "ggx", "base_color": 0.15, "metallic": 0.0, "roughness": 0.40, "ior": 1.5},
    "yinshenban":     {"brdf_model": "ggx", "base_color": 0.08, "metallic": 0.0, "roughness": 0.90, "ior": 1.5},
}
_GGX_FALLBACK = {"brdf_model": "ggx", "base_color": 0.20, "metallic": 0.0, "roughness": 0.50, "ior": 1.5}


def get_material(part_name: str, use_ggx: bool = False) -> dict:
    """安全获取部件材料 BRDF 参数。use_ggx=True 返回 GGX nominal 参数。"""
    if use_ggx:
        return _GGX_DB.get(part_name, _GGX_FALLBACK).copy()
    return MATERIAL_DB.get(part_name, {}).get("simple", DEFAULT_MAT)


def brdf_value(normal, sun_dir, det_dir, mat: dict) -> np.ndarray:
    """
    标量/向量化 BRDF：支持 (3,) 单个法向量或 (N,3) 批量法向量。

    返回 (N,) 数组或标量。
    """
    h_vec = sun_dir + det_dir
    h_norm = np.linalg.norm(h_vec)
    if h_norm > 0:
        h_vec = h_vec / h_norm
    cos_alpha = np.maximum(np.dot(normal, h_vec), 0.0)
    return (mat["rho_d"] / np.pi) + mat["rho_s"] * (cos_alpha ** mat["n"])

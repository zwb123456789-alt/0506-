# -*- coding: utf-8 -*-
"""
materials_v0_4.py —— v0.4 BRDF 材料数据库
==========================================
统一的部件材料 BRDF 参数。

【版本说明】
本文件从历史 materials.py 迁移，主要改动：
1. 明确标注 Legacy Phong 参数为 B0 project provisional baseline
2. 不声称书中材料参数或书中五参数冯模型
3. GGX 保留为 mismatch_control 对照分支

【BRDF 分支规划】
B0：Legacy/simple Phong-like provisional baseline（当前主线）
    参数来自历史项目 nominal 值，用于 smoke test 和最小链路闭合

B1：书中改进冯模型（后续升级分支）
    对应第 3 章 56-59 页，式 (3.16)，参数 rho_d, rho_s, alpha, a, b
    需作者确认三部件材料与书中材料对应关系

B2：Torrance-Sparrow 五参数 / 改进六参数模型（后续专项分支）
    对应第 3 章 63-67 页，式 (3.18)、式 (3.23)
    不作为当前 smoke test 必要条件

【重要边界】
- B0 参数为项目 provisional 参数，不是书中材料参数
- B0 不等同于书中改进冯模型或 Torrance-Sparrow 五参数模型
- GGX 只作为 mismatch 对照分支，不进入 smoke test 主线
"""

import numpy as np


# ============================================================
# B0: Legacy/simple Phong-like provisional baseline
# ============================================================
# 参数来源：历史项目 nominal 值
# 不声称：书中材料参数、书中五参数冯、书中改进模型

BRDF_B0_PHONG_LIKE = {
    "jinshuzhuti": {
        "desc":   "卫星金属主体（铝合金/镀铝外壳）— project provisional params",
        "brdf_model": "phong_like_provisional_baseline",
        "rho_d": 0.20,  # 漫反射系数（diffuse albedo）
        "rho_s": 0.60,  # 镜面反射系数（specular albedo）
        "n": 80,        # Phong 指数（specular sharpness）
        "brdf_branch": "B0_baseline",
        "brdf_reference": "project_provisional_params_from_legacy_materials_py",
    },
    "taiyangnengban": {
        "desc":   "太阳能电池板（玻璃盖片+半导体）— project provisional params",
        "brdf_model": "phong_like_provisional_baseline",
        "rho_d": 0.15,
        "rho_s": 0.10,
        "n": 20,
        "brdf_branch": "B0_baseline",
        "brdf_reference": "project_provisional_params_from_legacy_materials_py",
    },
    "yinshenban": {
        "desc":   "隐身/暗表面涂层（低反射率黑色涂层）— project provisional params",
        "brdf_model": "phong_like_provisional_baseline",
        "rho_d": 0.08,
        "rho_s": 0.02,
        "n": 10,
        "brdf_branch": "B0_baseline",
        "brdf_reference": "project_provisional_params_from_legacy_materials_py",
    },
}

# 部件未在数据库中时的兜底参数
BRDF_B0_FALLBACK = {
    "brdf_model": "phong_like_provisional_baseline",
    "rho_d": 0.20,
    "rho_s": 0.30,
    "n": 30,
    "brdf_branch": "B0_baseline",
    "brdf_reference": "fallback_provisional_params",
}


# ============================================================
# B0 BRDF 公式
# ============================================================
# f_r = rho_d / π  +  rho_s * (N·H)^n
#
# 其中：
#   H = (S + D) / |S + D|  （半程向量）
#   α = arccos(N·H)        （半程向量与法向夹角）
#
# 这是 Legacy/simple Phong-like 公式，
# 不等同于书中第 56-59 页改进冯模型（式 3.16，参数 rho_d, rho_s, alpha, a, b）
# 不等同于书中第 63-64 页 Torrance-Sparrow 五参数模型（式 3.18）


# ============================================================
# GGX 对照分支（mismatch_control）
# ============================================================
# GGX 参数已与 13 号 §9.3 一致，可直接复用作为对照分支

BRDF_GGX_MISMATCH = {
    "jinshuzhuti": {
        "brdf_model": "ggx_cook_torrance",
        "base_color": 0.91,
        "metallic": 1.0,
        "roughness": 0.20,
        "F0": 0.91,
        "brdf_branch": "mismatch_control",
        "brdf_reference": "legacy_ggx_params_aligned_with_13_sec9_3",
    },
    "taiyangnengban": {
        "brdf_model": "ggx_cook_torrance",
        "base_color": 0.15,
        "metallic": 0.0,
        "roughness": 0.40,
        "ior": 1.5,
        "brdf_branch": "mismatch_control",
        "brdf_reference": "legacy_ggx_params_aligned_with_13_sec9_3",
    },
    "yinshenban": {
        "brdf_model": "ggx_cook_torrance",
        "base_color": 0.08,
        "metallic": 0.0,
        "roughness": 0.90,
        "ior": 1.5,
        "brdf_branch": "mismatch_control",
        "brdf_reference": "legacy_ggx_params_aligned_with_13_sec9_3",
    },
}

BRDF_GGX_FALLBACK = {
    "brdf_model": "ggx_cook_torrance",
    "base_color": 0.20,
    "metallic": 0.0,
    "roughness": 0.50,
    "ior": 1.5,
    "brdf_branch": "mismatch_control",
    "brdf_reference": "fallback_ggx_params",
}


# ============================================================
# 材料获取函数
# ============================================================
def get_material_b0(part_name: str) -> dict:
    """
    获取 B0 baseline 材料参数（phong_like_provisional_baseline）。

    参数:
        part_name: 部件名称（jinshuzhuti / taiyangnengban / yinshenban）

    返回:
        dict: BRDF 参数字典，含 brdf_model, rho_d, rho_s, n, brdf_branch, brdf_reference
    """
    return BRDF_B0_PHONG_LIKE.get(part_name, BRDF_B0_FALLBACK).copy()


def get_material_ggx(part_name: str) -> dict:
    """
    获取 GGX mismatch 对照分支材料参数。

    参数:
        part_name: 部件名称

    返回:
        dict: GGX 参数字典
    """
    return BRDF_GGX_MISMATCH.get(part_name, BRDF_GGX_FALLBACK).copy()


def get_material(part_name: str, branch: str = "B0") -> dict:
    """
    统一材料获取接口。

    参数:
        part_name: 部件名称
        branch: BRDF 分支，"B0" | "GGX" | "B1" | "B2"

    返回:
        dict: BRDF 参数字典

    说明:
        - B0: phong_like_provisional_baseline（默认主线）
        - GGX: ggx_cook_torrance（mismatch 对照分支）
        - B1/B2: 待实现（需书中材料对应关系确认）
    """
    if branch == "B0":
        return get_material_b0(part_name)
    elif branch == "GGX":
        return get_material_ggx(part_name)
    elif branch == "B1":
        raise NotImplementedError("B1 (书中改进冯模型) 待实现，需确认三部件材料对应关系")
    elif branch == "B2":
        raise NotImplementedError("B2 (Torrance-Sparrow 五参数/六参数) 待实现")
    else:
        raise ValueError(f"未知 BRDF 分支: {branch}")


# ============================================================
# B0 BRDF 计算函数
# ============================================================
def brdf_b0_phong_like(normal, sun_dir, det_dir, mat: dict) -> np.ndarray:
    """
    B0 Legacy/simple Phong-like BRDF 计算。

    公式: f_r = rho_d / π + rho_s * (N·H)^n

    参数:
        normal: 法向量，shape (3,) 或 (N, 3)
        sun_dir: 太阳方向（已归一化），shape (3,)
        det_dir: 探测器方向（已归一化），shape (3,)
        mat: 材料参数字典，需含 rho_d, rho_s, n

    返回:
        BRDF 值，shape () 或 (N,)

    注意:
        - 支持标量（单个法向）或向量化（批量法向）
        - 半程向量 H = (S + D) / |S + D|
        - cos(α) = max(N·H, 0)
    """
    # 计算半程向量
    h_vec = sun_dir + det_dir
    h_norm = np.linalg.norm(h_vec)
    if h_norm > 0:
        h_vec = h_vec / h_norm

    # 计算 cos(α) = N·H
    cos_alpha = np.maximum(np.dot(normal, h_vec), 0.0)

    # BRDF = rho_d / π + rho_s * (cos α)^n
    return (mat["rho_d"] / np.pi) + mat["rho_s"] * (cos_alpha ** mat["n"])


# ============================================================
# 版本记录
# ============================================================
MATERIALS_VERSION = "v0.4.0"
MATERIALS_CREATED = "2026-06-23"
MATERIALS_NOTES = """
v0.4 材料数据库主要改动：
1. 明确标注 B0 为 project provisional Phong-like baseline
2. 不声称书中材料参数或书中五参数冯模型
3. GGX 保留为 mismatch_control 对照分支
4. B1/B2 预留为后续升级分支（需书中材料对应关系确认）
5. 提供统一 get_material(part_name, branch) 接口

当前执行边界：
- B0 用于 smoke test 和最小链路闭合
- GGX 只作为 mismatch 对照，不进入 smoke test 主线
- B1/B2 不阻塞 Phase 0
"""

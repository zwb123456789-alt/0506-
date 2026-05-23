# -*- coding: utf-8 -*-
"""
brdf_models.py —— Canonical BRDF 模块
=========================
统一 BRDF 计算接口，供模块 A（OCS）、模块 B（图像渲染）、验证套件共用。

【设计原则】
1. 所有 BRDF 函数支持 numpy 批量计算（N/L/V 可以是 (3,) 或 (N,3)）
2. 所有方向向量假定已归一化（调用方负责）
3. 对 NoL <= 0 或 NoV <= 0 返回 0（物理不可见）
4. 防止 NaN / Inf（除零保护、roughness 下限）
5. 返回值非负

【参考文档】
- ocs_project/07_brdf/brdf_precision_design.md
"""

import numpy as np


# ====================================
# 常量
# =====================================
PI = np.pi
EPS = 1e-8  # 除零保护
ROUGHNESS_MIN = 0.02  # 粗糙度下限（避免数值不稳定）


# =============================================
# 辅助函数
# ===================================
def safe_normalize(v):
    """安全归一化向量，避免零向量。"""
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    safe_norm = np.where(norm > EPS, norm, 1.0)
    return np.where(norm > EPS, v / safe_norm, 0.0)


def safe_dot(a, b):
    """安全点积，支持 (3,) 或 (N,3)。"""
    return np.sum(a * b, axis=-1)


def clamp(x, min_val, max_val):
    """截断到 [min_val, max_val]。"""
    return np.clip(x, min_val, max_val)


# ===================================
# 1. LegacyPhong（历史 baseline）
# ====================================
def eval_legacy_phong(N, L, V, rho_d, rho_s, n):
    """
    LegacyPhong BRDF：冻结当前模块 A 公式。

    公式：f_r = (rho_d / π) + rho_s * (NoH)^n

    参数：
        N: 法向量（单位向量），shape (3,) 或 (N,3)
        L: 太阳方向（单位向量），shape (3,) 或 (N,3)
        V: 探测器方向（单位向量），shape (3,) 或 (N,3)
        rho_d: 漫反射系数 [0, 1]
        rho_s: 镜面反射系数 [0, 1]
        n: Phong 指数 [1, 1000]

    返回：
        f_r: BRDF 值，shape () 或 (N,)

    注意：
        - 调用方负责确保 N/L/V 已归一化
        - 对 NoL <= 0 或 NoV <= 0 返回 0
        - OCS 积分时需额外乘 NoL * NoV
    """
    # 半程向量
    H = safe_normalize(L + V)

    # 角度余弦
    NoL = np.maximum(safe_dot(N, L), 0.0)
    NoV = np.maximum(safe_dot(N, V), 0.0)
    NoH = np.maximum(safe_dot(N, H), 0.0)

    # 可见性掩码
    visible = (NoL > 0) & (NoV > 0)

    # BRDF 计算
    f_diffuse = rho_d / PI
    f_specular = rho_s * np.power(NoH, n)
    f_r = f_diffuse + f_specular

    # 不可见面元返回 0
    f_r = np.where(visible, f_r, 0.0)

    return f_r


# ==================================
# 2. NormalizedPhong（可选过渡）
# ===========================================
def eval_normalized_phong(N, L, V, rho_d, rho_s, n):
    """
    NormalizedPhong BRDF：在 LegacyPhong 基础上加能量守恒归一化。

    公式：
      f_diffuse  = rho_d / π
        f_specular = rho_s * ((n + 2) / (2 * π)) * (NoH)^n
        f_r = f_diffuse + f_specular

    参数：同 eval_legacy_phong

    返回：同 eval_legacy_phong
    """
    # 半程向量
    H = safe_normalize(L + V)

    # 角度余弦
    NoL = np.maximum(safe_dot(N, L), 0.0)
    NoV = np.maximum(safe_dot(N, V), 0.0)
    NoH = np.maximum(safe_dot(N, H), 0.0)

    # 可见性掩码
    visible = (NoL > 0) & (NoV > 0)

    # BRDF 计算（加归一化项）
    f_diffuse = rho_d / PI
    normalization = (n + 2.0) / (2.0 * PI)
    f_specular = rho_s * normalization * np.power(NoH, n)
    f_r = f_diffuse + f_specular

    # 不可见面元返回 0
    f_r = np.where(visible, f_r, 0.0)

    return f_r


# ============================================
# 3. GGX / Cook-Torrance（论文主模型）
# ====================================
def D_GGX(NoH, alpha):
    """
    GGX 法向分布函数。

    公式：D = α² / (π * ((NoH)² * (α² - 1) + 1)²)

    参数：
     NoH: 法向与半程向量夹角余弦，shape () 或 (N,)
    alpha: GGX 粗糙度参数（roughness²）

    返回：
        D: 法向分布值，shape () 或 (N,)
    """
    a2 = alpha * alpha
    denom = NoH * NoH * (a2 - 1.0) + 1.0
    denom = np.maximum(denom, EPS)  # 防止除零
    return a2 / (PI * denom * denom)


def G1_GGX(NoX, alpha):
    """
    Smith-GGX 单向几何遮蔽项。

    公式：G1 = 2 * NoX / (NoX + sqrt(α² + (1 - α²) * (NoX)²))

    参数：
        NoX: 法向与方向（L 或 V）夹角余弦，shape () 或 (N,)
        alpha: GGX 粗糙度参数

    返回：
     G1: 几何遮蔽值，shape () 或 (N,)
    """
    a2 = alpha * alpha
    NoX2 = NoX * NoX
    denom = NoX + np.sqrt(a2 + (1.0 - a2) * NoX2)
    denom = np.maximum(denom, EPS)
    return 2.0 * NoX / denom


def G_Smith_GGX(NoL, NoV, alpha):
    """
    Smith-GGX 双向几何遮蔽项。

    公式：G = G1(NoL) * G1(NoV)

    参数：
        NoL: 法向与太阳方向夹角余弦
        NoV: 法向与探测器方向夹角余弦
        alpha: GGX 粗糙度参数

    返回：
        G: 几何遮蔽值
    """
    return G1_GGX(NoL, alpha) * G1_GGX(NoV, alpha)

def F_Schlick(VoH, F0):
    """
    Schlick Fresnel 近似。

    公式：F = F0 + (1 - F0) * (1 - VoH)^5

    参数：
        VoH: 探测器方向与半程向量夹角余弦
        F0: 垂直入射时的反射率（标量或 RGB）

    返回：
        F: Fresnel 反射率
    """
    return F0 + (1.0 - F0) * np.power(1.0 - VoH, 5.0)


def eval_ggx_cook_torrance(N, L, V, base_color, metallic, roughness, F0=None, ior=None):
    """
    GGX / Cook-Torrance 微表面 BRDF。

    公式：
        f_r = f_diffuse + f_specular
        f_diffuse = (1 - metallic) * (base_color / π)
        f_specular = (D * G * F) / max(4 * NoL * NoV, eps)

    参数：
        N: 法向量（单位向量），shape (3,) 或 (N,3)
        L: 太阳方向（单位向量），shape (3,) 或 (N,3)
        V: 探测器方向（单位向量），shape (3,) 或 (N,3)
        base_color: 基础颜色（灰度或 RGB），标量或 shape (3,) 或 (N,3)
        metallic: 金属度 [0, 1]
        roughness: 粗糙度 [0.02, 1]
        F0: 垂直入射反射率（可选，金属用）
      ior: 折射率（可选，电介质用，默认 1.5）

    返回：
        f_r: BRDF 值，shape () 或 (N,)

    注意：
        - F0 和 ior 至少提供一个
        - 电介质：F0 从 ior 计算，F0 = ((ior - 1) / (ior + 1))^2
        - 金属：直接使用 F0（如铝 F0=0.91）
    """
    # 粗糙度下限
    roughness = np.maximum(roughness, ROUGHNESS_MIN)
    alpha = roughness * roughness

    # 半程向量
    H = safe_normalize(L + V)

    # 角度余弦
    NoL = np.maximum(safe_dot(N, L), 0.0)
    NoV = np.maximum(safe_dot(N, V), 0.0)
    NoH = np.maximum(safe_dot(N, H), 0.0)
    VoH = np.maximum(safe_dot(V, H), 0.0)

    # 可见性掩码
    visible = (NoL > 0) & (NoV > 0)

    # 计算 F0
    if F0 is None:
        if ior is None:
            ior = 1.5  # 默认玻璃折射率
        F0_calc = ((ior - 1.0) / (ior + 1.0)) ** 2
    else:
      F0_calc = F0

    # 漫反射项
    f_diffuse = (1.0 - metallic) * (base_color / PI)

    # 镜面项：D * G * F / (4 * NoL * NoV)
    D = D_GGX(NoH, alpha)
    G = G_Smith_GGX(NoL, NoV, alpha)
    F = F_Schlick(VoH, F0_calc)

    denom = 4.0 * NoL * NoV
    denom = np.maximum(denom, EPS)
    f_specular = (D * G * F) / denom

    # 总 BRDF
    f_r = f_diffuse + f_specular

    # 不可见面元返回 0
    f_r = np.where(visible, f_r, 0.0)

    return f_r


# ====================================
# 4. 统一入口
# =================================
def eval_brdf(N, L, V, material):
    """
    统一 BRDF 计算入口，根据 material["brdf_model"] 分发。

    参数：
        N: 法向量（单位向量），shape (3,) 或 (N,3)
        L: 太阳方向（单位向量），shape (3,) 或 (N,3)
        V: 探测器方向（单位向量），shape (3,) 或 (N,3)
      material: 材料参数字典，必须包含 "brdf_model" 字段

    返回：
        f_r: BRDF 值，shape () 或 (N,)

    支持的 brdf_model：
        - "legacy_phong": LegacyPhong（需 rho_d, rho_s, n）
        - "normalized_phong": NormalizedPhong（需 rho_d, rho_s, n）
        - "ggx": GGX/Cook-Torrance（需 base_color, metallic, roughness, F0 或 ior）

    示例：
        material = {
            "brdf_model": "legacy_phong",
         "rho_d": 0.20,
            "rho_s": 0.60,
            "n": 80,
        }
        f_r = eval_brdf(N, L, V, material)
    """
    model = material.get("brdf_model")

    if model == "legacy_phong":
        return eval_legacy_phong(
            N, L, V,
        material["rho_d"],
            material["rho_s"],
            material["n"]
        )

    elif model == "normalized_phong":
        return eval_normalized_phong(
            N, L, V,
            material["rho_d"],
            material["rho_s"],
        material["n"]
        )

    elif model == "ggx":
        return eval_ggx_cook_torrance(
            N, L, V,
            material["base_color"],
            material["metallic"],
          material["roughness"],
          F0=material.get("F0"),
            ior=material.get("ior")
        )

    else:
      raise ValueError(f"Unknown BRDF model: {model}")


# =============================================
# 5. 材料数据库（兼容旧 materials.py）
# ====================================
MATERIAL_DB_LEGACY = {
    "jinshuzhuti": {
        "desc": "卫星金属主体（铝合金/镀铝外壳）",
        "brdf_model": "legacy_phong",
        "rho_d": 0.20,
        "rho_s": 0.60,
        "n": 80,
    },
    "taiyangnengban": {
        "desc": "太阳能电池板（玻璃盖片+半导体）",
        "brdf_model": "legacy_phong",
        "rho_d": 0.15,
      "rho_s": 0.10,
        "n": 20,
    },
    "yinshenban": {
        "desc": "隐身/暗表面涂层（低反射率黑色涂层）",
        "brdf_model": "legacy_phong",
        "rho_d": 0.08,
        "rho_s": 0.02,
        "n": 10,
    },
}

MATERIAL_DB_GGX = {
    "jinshuzhuti": {
        "desc": "卫星金属主体（铝合金/镀铝外壳）",
        "brdf_model": "ggx",
        "base_color": 0.91,  # 铝反照率
        "metallic": 1.0,
      "roughness": 0.20,  # nominal 值
    "F0": 0.91,  # 铝垂直入射反射率
    },
    "taiyangnengban": {
        "desc": "太阳能电池板（玻璃盖片+半导体）",
        "brdf_model": "ggx",
        "base_color": 0.15,
        "metallic": 0.0,
     "roughness": 0.40,  # nominal 值
     "ior": 1.5,  # 玻璃折射率
    },
    "yinshenban": {
        "desc": "隐身/暗表面涂层（低反射率黑色涂层）",
        "brdf_model": "ggx",
        "base_color": 0.08,
        "metallic": 0.0,
        "roughness": 0.90,  # nominal 值
        "ior": 1.5,
    },
}

# 默认使用 LegacyPhong（保持向后兼容）
MATERIAL_DB = MATERIAL_DB_LEGACY


def get_material(part_name, use_ggx=False):
    """
    安全获取部件材料 BRDF 参数。

    参数：
      part_name: 部件名称
        use_ggx: 是否使用 GGX 材料库（默认 False，使用 LegacyPhong）

    返回：
        material: 材料参数字典
    """
    db = MATERIAL_DB_GGX if use_ggx else MATERIAL_DB_LEGACY

    if part_name not in db:
        # 兜底参数
        if use_ggx:
            return {
                "brdf_model": "ggx",
                "base_color": 0.20,
                "metallic": 0.0,
                "roughness": 0.50,
                "ior": 1.5,
            }
        else:
            return {
                "brdf_model": "legacy_phong",
                "rho_d": 0.20,
                "rho_s": 0.30,
                "n": 30,
            }

    return db[part_name].copy()

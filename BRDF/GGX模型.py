# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 16:15:23 2026

@author: 97466
"""

"""
GGX (Trowbridge-Reitz) 微表面 BRDF
现代PBR标准,Disney、Unreal Engine使用
"""

import numpy as np

def calculate_brdf_ggx(material_name, sun_vec, obs_vec, normal, material_db=None):
    """
    GGX/Trowbridge-Reitz 微表面 BRDF
    
    相比Cook-Torrance的改进:
    • 更准确的长尾分布 (高光更真实)
    • Smith联合遮蔽阴影项 (更物理准确)
    • 工业界广泛验证
    
    参数:
        material_name: 材质名称
        sun_vec: 太阳方向向量
        obs_vec: 观测方向向量
        normal: 表面法向量
        material_db: 材质参数数据库
    
    返回:
        brdf: BRDF值 (sr^-1)
    """
    
    # ========================================
    # 材质参数数据库 (与Cook-Torrance相同)
    # ========================================
    if material_db is None:
        material_db = {
            "dulvmo": {
                "roughness": 0.15,
                "metallic": 0.95,
                "base_color": [0.91, 0.92, 0.92],
                "F0": 0.91
            },
            "qita": {
                "roughness": 0.50,
                "metallic": 0.0,
                "base_color": [0.40, 0.40, 0.40],
                "F0": 0.04
            },
            "solar_panel": {
                "roughness": 0.10,
                "metallic": 0.0,
                "base_color": [0.08, 0.10, 0.15],
                "F0": 0.04
            }
        }
    
    if material_name not in material_db:
        print(f"警告: 使用默认材质参数")
        material = {
            "roughness": 0.4,
            "metallic": 0.0,
            "base_color": [0.5, 0.5, 0.5],
            "F0": 0.04
        }
    else:
        material = material_db[material_name]
    
    roughness = material["roughness"]
    metallic = material["metallic"]
    base_color = np.array(material["base_color"])
    F0 = material["F0"]
    
    # ========================================
    # 向量计算
    # ========================================
    L = sun_vec / (np.linalg.norm(sun_vec) + 1e-10)
    V = obs_vec / (np.linalg.norm(obs_vec) + 1e-10)
    N = normal / (np.linalg.norm(normal) + 1e-10)
    H = (L + V) / (np.linalg.norm(L + V) + 1e-10)
    
    NdotL = max(np.dot(N, L), 0.0)
    NdotV = max(np.dot(N, V), 0.0)
    NdotH = max(np.dot(N, H), 0.0)
    VdotH = max(np.dot(V, H), 0.0)
    
    if NdotL < 1e-6 or NdotV < 1e-6:
        return 0.0
    
    # ========================================
    # 1. GGX 法线分布函数 D
    # ========================================
    """
    GGX/Trowbridge-Reitz 分布
    
    公式:
                  α²
    D = ─────────────────────────
        π[(NdotH)²(α²-1)+1]²
    
    优势:
    • 长尾特性 (相比Beckmann更真实)
    • 数值稳定性好
    • 高光边缘过渡自然
    """
    alpha = roughness * roughness  # 使用α²映射(Disney做法)
    alpha_sq = alpha * alpha
    
    NdotH_sq = NdotH * NdotH
    denom = NdotH_sq * (alpha_sq - 1.0) + 1.0
    D = alpha_sq / (np.pi * denom * denom + 1e-7)
    
    # ========================================
    # 2. Smith 联合遮蔽阴影函数 G
    # ========================================
    """
    Smith 模型 (分离遮蔽近似)
    
    G(L,V,H) = G1(L) × G1(V)
    
    其中 G1 使用 GGX 形式:
    
              2(NdotX)
    G1(X) = ──────────────────
            NdotX + √(α²+(1-α²)(NdotX)²)
    
    物理意义:
    • 同时考虑入射和出射的遮挡
    • 能量守恒
    """
    def smith_ggx_g1(NdotX, alpha):
        """单方向遮蔽函数"""
        k = alpha / 2.0  # 直接光照用 k=α/2
        return NdotX / (NdotX * (1.0 - k) + k + 1e-7)
    
    G1_L = smith_ggx_g1(NdotL, alpha)
    G1_V = smith_ggx_g1(NdotV, alpha)
    G = G1_L * G1_V
    
    # ========================================
    # 3. Fresnel 反射 F
    # ========================================
    """
    Schlick 近似 (与Cook-Torrance相同)
    """
    F = F0 + (1.0 - F0) * ((1.0 - VdotH) ** 5)
    
    # ========================================
    # 4. 镜面反射项
    # ========================================
    f_specular = (D * G * F) / (4.0 * NdotL * NdotV + 1e-7)
    
    # ========================================
    # 5. 漫反射项 (Disney Diffuse - 可选升级)
    # ========================================
    """
    选项A: 标准Lambertian (简单)
    """
    albedo = np.mean(base_color)
    f_diffuse_lambert = (1.0 - F) * (1.0 - metallic) * albedo / np.pi
    
    """
    选项B: Disney Diffuse (更精确,考虑粗糙度)
    """
    # Burley 2012 漫反射模型
    FL = (1.0 - NdotL) ** 5
    FV = (1.0 - NdotV) ** 5
    Fd90 = 0.5 + 2.0 * roughness * VdotH * VdotH
    f_diffuse_disney = (albedo / np.pi) * (1.0 + (Fd90 - 1.0) * FL) * (1.0 + (Fd90 - 1.0) * FV)
    f_diffuse_disney *= (1.0 - F) * (1.0 - metallic)
    
    # 选择使用哪个漫反射模型
    USE_DISNEY_DIFFUSE = True  # 设为False使用标准Lambert
    
    if USE_DISNEY_DIFFUSE:
        f_diffuse = f_diffuse_disney
    else:
        f_diffuse = f_diffuse_lambert
    
    # ========================================
    # 6. 总BRDF
    # ========================================
    brdf = f_diffuse + f_specular
    
    return brdf
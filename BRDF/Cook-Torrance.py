# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 16:14:34 2026

@author: 97466
"""

"""
Cook-Torrance 微表面 BRDF 模型
物理基础,能量守恒,适用于科研
"""

import numpy as np

def calculate_brdf_cook_torrance(material_name, sun_vec, obs_vec, normal, material_db=None):
    """
    Cook-Torrance 微表面 BRDF
    
    参数:
        material_name: 材质名称
        sun_vec: 太阳方向向量 (未归一化也可)
        obs_vec: 观测方向向量
        normal: 表面法向量
        material_db: 材质参数数据库字典 (可选)
    
    返回:
        brdf: BRDF值 (sr^-1)
    
    物理模型:
        BRDF = f_diffuse + f_specular
        
        f_diffuse = (1 - F) × (1 - metallic) × albedo / π
        
        f_specular = D × G × F / (4 × NdotL × NdotV)
    """
    
    # ========================================
    # 材质参数数据库
    # ========================================
    if material_db is None:
        material_db = {
            # ===== 金属材料 =====
            "dulvmo": {  # 镀铝膜
                "roughness": 0.15,      # 粗糙度 α
                "metallic": 0.95,       # 金属度 (接近纯金属)
                "base_color": [0.91, 0.92, 0.92],  # RGB基础色(铝的反射光谱)
                "F0": 0.91              # 0度反射率
            },
            "aluminum_polished": {  # 抛光铝
                "roughness": 0.05,
                "metallic": 1.0,
                "base_color": [0.91, 0.92, 0.92],
                "F0": 0.91
            },
            "aluminum_anodized": {  # 阳极氧化铝
                "roughness": 0.35,
                "metallic": 0.7,
                "base_color": [0.85, 0.86, 0.86],
                "F0": 0.85
            },
            
            # ===== 非金属材料 =====
            "qita": {  # 其他部件 (假设为工程塑料)
                "roughness": 0.50,
                "metallic": 0.0,
                "base_color": [0.40, 0.40, 0.40],
                "F0": 0.04  # 塑料典型值
            },
            "white_paint": {  # 白色涂层
                "roughness": 0.60,
                "metallic": 0.0,
                "base_color": [0.85, 0.85, 0.85],
                "F0": 0.04
            },
            "carbon_fiber": {  # 碳纤维
                "roughness": 0.25,
                "metallic": 0.3,
                "base_color": [0.05, 0.05, 0.05],
                "F0": 0.06
            },
            "solar_panel": {  # 太阳能板
                "roughness": 0.10,
                "metallic": 0.0,
                "base_color": [0.08, 0.10, 0.15],
                "F0": 0.04
            },
            "kapton_film": {  # Kapton聚酰亚胺膜
                "roughness": 0.20,
                "metallic": 0.0,
                "base_color": [0.70, 0.55, 0.20],  # 金黄色
                "F0": 0.05
            }
        }
    
    # 获取材质参数
    if material_name not in material_db:
        print(f"警告: 材质'{material_name}'不在数据库中,使用默认值")
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
    # 向量归一化与点积计算
    # ========================================
    L = sun_vec / (np.linalg.norm(sun_vec) + 1e-10)  # 光源方向
    V = obs_vec / (np.linalg.norm(obs_vec) + 1e-10)  # 观察方向
    N = normal / (np.linalg.norm(normal) + 1e-10)    # 法向量
    H = L + V
    H = H / (np.linalg.norm(H) + 1e-10)              # 半角向量
    
    NdotL = max(np.dot(N, L), 0.0)
    NdotV = max(np.dot(N, V), 0.0)
    NdotH = max(np.dot(N, H), 0.0)
    VdotH = max(np.dot(V, H), 0.0)
    
    # 提前终止无效配置
    if NdotL < 1e-6 or NdotV < 1e-6:
        return 0.0
    
    # ========================================
    # 1. 法线分布函数 D (Beckmann分布)
    # ========================================
    """
    Beckmann-Spizzichino 分布 (Cook-Torrance原始版本)
    
    公式:
              1                 -(tan²θh / α²)
    D = ──────────── × exp( ─────────────── )
        π α² cos⁴θh              1
    
    其中: cos θh = NdotH
    """
    alpha = roughness
    alpha_sq = alpha * alpha
    NdotH_sq = NdotH * NdotH
    
    if NdotH_sq < 1e-6:
        D = 0.0
    else:
        tan_theta_h_sq = (1.0 - NdotH_sq) / NdotH_sq
        D = np.exp(-tan_theta_h_sq / alpha_sq) / (np.pi * alpha_sq * NdotH_sq * NdotH_sq)
    
    # ========================================
    # 2. 几何遮蔽函数 G (Cook-Torrance原始)
    # ========================================
    """
    Cook-Torrance 几何衰减因子
    
    考虑三种遮蔽情况:
    1. 入射光被遮挡 (Shadowing)
    2. 反射光被遮挡 (Masking)
    3. 完全可见
    
    G = min(1, G1, G2)
    
    G1 = 2(NdotH)(NdotV) / VdotH
    G2 = 2(NdotH)(NdotL) / VdotH
    """
    G1 = (2.0 * NdotH * NdotV) / (VdotH + 1e-7)
    G2 = (2.0 * NdotH * NdotL) / (VdotH + 1e-7)
    G = min(1.0, G1, G2)
    
    # ========================================
    # 3. Fresnel反射 F (Schlick近似)
    # ========================================
    """
    Schlick近似 (计算效率高,精度足够)
    
    F(θ) = F0 + (1 - F0)(1 - cosθ)^5
    
    其中:
    • F0: 0度入射反射率
    • cosθ = VdotH
    """
    F = F0 + (1.0 - F0) * ((1.0 - VdotH) ** 5)
    
    # ========================================
    # 4. 镜面反射项 (Specular)
    # ========================================
    """
    Cook-Torrance 镜面 BRDF:
    
              D × G × F
    f_spec = ─────────────
             4 NdotL NdotV
    """
    denominator = 4.0 * NdotL * NdotV + 1e-7
    f_specular = (D * G * F) / denominator
    
    # ========================================
    # 5. 漫反射项 (Diffuse - Lambertian)
    # ========================================
    """
    能量守恒的漫反射:
    
    f_diffuse = (1 - F) × (1 - metallic) × albedo / π
    
    说明:
    • (1 - F): 未被镜面反射的能量
    • (1 - metallic): 金属没有漫反射
    • albedo: 漫反射反照率
    """
    # 使用base_color的亮度作为albedo
    albedo = np.mean(base_color)  # 简化:取RGB平均
    
    f_diffuse = (1.0 - F) * (1.0 - metallic) * albedo / np.pi
    
    # ========================================
    # 6. 总BRDF
    # ========================================
    brdf = f_diffuse + f_specular
    
    return brdf
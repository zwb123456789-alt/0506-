# -*- coding: utf-8 -*-
"""
config.py —— 全局配置区
=======================
统一管理：路径、模式开关、扫描参数、Blender 路径、双语标签。
其它模块一律 `from config import *` 获取常量。

【设计原则】
1. 任何"魔法字符串/路径"都集中在这里。
2. 中英双语标签集中维护，方便论文/汇报切换。
3. 当前阶段 ENABLE_RENDER = False，渲染交给 Blender 阶段（模块 B）。
"""

import os
import numpy as np


# ============================================================
# 1. 路径配置
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
STL_DIR      = os.path.join(PROJECT_ROOT, "建模")
OCS_PROJECT  = os.path.join(PROJECT_ROOT, "ocs_project")
# 所有运行产物统一落到 0506新/结果/模块A_重构/ 下，按 mode_tag/run_id 分子目录
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "结果", "模块A_重构")

PART_FILES = {
    "jinshuzhuti":    os.path.join(STL_DIR, "真实模型", "jinshuzhuti.stl"),
    "taiyangnengban": os.path.join(STL_DIR, "真实模型", "taiyangnengban.stl"),
    "yinshenban":     os.path.join(STL_DIR, "真实模型", "yinshenban.stl"),
}

# Blender 5.0 可执行文件（按用户机器实际位置；模块 B 阶段才会用到）
BLENDER_EXE = r"D:\Program Files\Blender Foundation\Blender 5.0\blender.exe"


# ============================================================
# 2. 物理参数
# ============================================================
UNIT_SCALE = 1e-3        # mm → m
EPSILON    = 1.0         # 法向偏移（mm），避免射线起点自交
RAY_BATCH  = 5000        # 光线追踪每次处理的光线数

SUN_VECTOR = np.array([1.0,  0.0, 0.3])   # 太阳方向（惯性系，将归一化）
DET_VECTOR = np.array([0.5, -1.0, 0.1])   # 探测器方向（惯性系，将归一化）

# 多观测几何定义（Step 10d）：覆盖不同太阳-探测器相位角
# 每个条目 = (sun_vector, det_vector, label)
OBS_GEOMETRIES = [
    (np.array([1.0,  0.0, 0.3]),   np.array([0.5, -1.0, 0.1]),   "phase63_backscatter"),       # G0 baseline, ~63°
    (np.array([0.5, -1.0, 0.5]),   np.array([0.2, -1.0, 0.1]),   "phase24_near_backscatter"),   # G1 ~24°
    (np.array([1.0,  0.0, 0.0]),   np.array([-0.5, 0.866, 0.0]), "phase120_forward_scatter"),   # G2 ~120°
    (np.array([1.0,  0.0, 0.0]),   np.array([0.0, 1.0, 0.0]),    "phase90_side"),               # G3 ~90°
    (np.array([0.707, 0.0, 0.707]), np.array([0.0, 0.0, 1.0]),   "phase45_overhead"),           # G4 ~45°
]


# ============================================================
# 3. 扫描参数
# ============================================================
SCAN_2D     = True         # True = 2D 网格(yaw×pitch); False = 1D 纯 yaw
YAW_RANGE   = (0, 360)
NUM_YAW     = 37           # (360/10)+1 = 37 → 10° 间隔
PITCH_RANGE = (-90, 90)
NUM_PITCH   = 19           # (180/10)+1 = 19 → 10° 间隔

# 精度级别（控制速度/精度平衡）
#   fast   : 保留 20% 面元，秒级/姿态
#   medium : 保留 50% 面元，十几秒/姿态
#   full   : 不抽稀，分钟级/姿态（论文级精度）
ACCURACY_LEVEL = "fast"

# BRDF 模型选择（"legacy_phong" | "ggx"）
# legacy_phong: frozen baseline, ρ_d/π + ρ_s·(N·H)^n
# ggx: Cook-Torrance GGX, D·G·F/(4·NoL·NoV) + (1-metallic)·base_color/π
BRDF_MODEL = "legacy_phong"


# ============================================================
# 4. 渲染开关（模块 A 阶段强制关闭，交由 Blender）
# ============================================================
ENABLE_RENDER = False    # 当前阶段不在 Python 端做图像渲染


# ============================================================
# 5. 图表样式
# ============================================================
FIG_DPI   = 300
LANG_MODE = "bilingual"   # "zh" | "en" | "bilingual"

# 双语标签字典（一处改全图同步）
LABELS = {
    "xlabel_yaw":   "Yaw / 偏航角 (°)",
    "ylabel_pitch": "Pitch / 俯仰角 (°)",
    "zlabel_ocs":   "OCS / 光学散射截面 (m²)",
    "label_occ":    "Occlusion ratio / 遮挡率 (%)",
    "label_loss":   "OCS loss / OCS 损失 (m²)",
    "label_ocs":    "OCS (m²)",
    "label_face":   "Faces / 面元数",
}

# 图编号 → (英文, 中文) 标题
TITLES = {
    "fig01": ("OCS 3D surface (with occlusion)", "OCS 三维曲面（含遮挡）"),
    "fig02": ("OCS heatmap (with occlusion)",    "OCS 俯视热图（含遮挡）"),
    "fig03": ("Part contribution heatmap",       "各部件 OCS 贡献热图"),
    "fig04": ("Occlusion ratio heatmap",         "遮挡率热图"),
    "fig05": ("OCS loss heatmap",                "OCS 损失热图"),
    "fig06": ("Satellite model (body frame)",    "卫星模型（本体坐标系）"),
}

# 部件名称双语
PART_LABELS = {
    "jinshuzhuti":    ("Metal body",  "金属主体"),
    "taiyangnengban": ("Solar panel", "太阳能板"),
    "yinshenban":     ("Dark panel",  "隐身板"),
}

# 部件配色（图 03/06 共用）
PART_COLORS = {
    "jinshuzhuti":    "silver",
    "taiyangnengban": "steelblue",
    "yinshenban":     "dimgray",
}


# ============================================================
# 6. 精度抽稀比例
# ============================================================
DECIMATE_RATIO = {
    "fast":   0.20,
    "medium": 0.50,
    "full":   1.00,
}


def get_bilingual_title(key: str) -> str:
    """根据 LANG_MODE 返回单语 / 双语标题。"""
    en, zh = TITLES[key]
    if LANG_MODE == "en":
        return en
    if LANG_MODE == "zh":
        return zh
    return f"{en} / {zh}"


def get_part_label(part_name: str) -> str:
    """根据 LANG_MODE 返回部件名。"""
    if part_name not in PART_LABELS:
        return part_name
    en, zh = PART_LABELS[part_name]
    if LANG_MODE == "en":
        return en
    if LANG_MODE == "zh":
        return zh
    return f"{en} / {zh}"


def dump_config() -> dict:
    """把当前配置序列化为 dict，供 config_used.json 落盘。"""
    return {
        "project_root":   PROJECT_ROOT,
        "stl_dir":        STL_DIR,
        "output_dir":     OUTPUT_DIR,
        "blender_exe":    BLENDER_EXE,
        "unit_scale":     UNIT_SCALE,
        "epsilon":        EPSILON,
        "ray_batch":      RAY_BATCH,
        "sun_vector":     SUN_VECTOR.tolist(),
        "det_vector":     DET_VECTOR.tolist(),
        "scan_2d":        SCAN_2D,
        "yaw_range":      list(YAW_RANGE),
        "num_yaw":        NUM_YAW,
        "pitch_range":    list(PITCH_RANGE),
        "num_pitch":      NUM_PITCH,
        "accuracy_level": ACCURACY_LEVEL,
        "enable_render":  ENABLE_RENDER,
        "lang_mode":      LANG_MODE,
        "fig_dpi":        FIG_DPI,
    }

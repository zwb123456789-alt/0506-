# -*- coding: utf-8 -*-
"""
config_v0_4.py —— v0.4 全局配置
================================
统一管理：路径、模式开关、扫描参数、Blender 路径、双语标签。

【版本说明】
本文件从历史 config.py 迁移，主要改动：
1. yaw 网格改为 72 个（0°-355°，步长 5°，不含 360°）
2. BRDF 主线改为 phong_like_provisional_baseline
3. epsilon 语义分离：NoL/NoV eps 与 depth_epsilon_m
4. 输出目录改为 v0.4_results/

【设计原则】
1. 任何"魔法字符串/路径"都集中在这里
2. 中英双语标签集中维护，方便论文/汇报切换
3. 当前阶段 ENABLE_RENDER = False，渲染交给 Blender 阶段
"""

import os
import numpy as np


# ============================================================
# 1. 路径配置
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
STL_DIR      = os.path.join(PROJECT_ROOT, "建模")
V04_PROJECT  = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")

# v0.4 输出根目录（与 14 号规范一致）
OUTPUT_DIR   = os.path.join(V04_PROJECT, "v0.4_results")

# v0.4 代码根目录
CODE_DIR     = os.path.join(V04_PROJECT, "06_v0.4_code")

PART_FILES = {
    "jinshuzhuti":    os.path.join(STL_DIR, "真实模型", "jinshuzhuti.stl"),
    "taiyangnengban": os.path.join(STL_DIR, "真实模型", "taiyangnengban.stl"),
    "yinshenban":     os.path.join(STL_DIR, "真实模型", "yinshenban.stl"),
}

# Blender 4.2 可执行文件
BLENDER_EXE = r"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe"


# ============================================================
# 2. 物理参数
# ============================================================
UNIT_SCALE = 1e-3        # mm → m

# epsilon 语义分离（v0.4 修正）
EPS_NOL_NOV = 1e-6                    # NoL/NoV 有效像素阈值（13 号 §6.4）
DEPTH_EPSILON_M_INITIAL = 1e-3        # depth 比较初始容差（m），最终值由 20 姿态校准
DEPTH_EPSILON_M_FINAL = None          # 待 20 姿态 shadow validation 校准后填入

RAY_BATCH  = 5000        # 光线追踪每次处理的光线数（若使用）

# 单几何基线配置（phase63）
SUN_VECTOR = np.array([1.0,  0.0, 0.3])   # 太阳方向（惯性系，将归一化）
DET_VECTOR = np.array([0.5, -1.0, 0.1])   # 探测器方向（惯性系，将归一化）

# 多观测几何定义：覆盖不同太阳-探测器相位角
# 每个条目 = (sun_vector, det_vector, label)
OBS_GEOMETRIES = [
    (np.array([1.0,  0.0, 0.3]),   np.array([0.5, -1.0, 0.1]),   "phase63_backscatter"),       # G0 baseline, ~63°
    (np.array([0.5, -1.0, 0.5]),   np.array([0.2, -1.0, 0.1]),   "phase24_near_backscatter"),   # G1 ~24°
    (np.array([1.0,  0.0, 0.0]),   np.array([-0.5, 0.866, 0.0]), "phase120_forward_scatter"),   # G2 ~120°
    (np.array([1.0,  0.0, 0.0]),   np.array([0.0, 1.0, 0.0]),    "phase90_side"),               # G3 ~90°
    (np.array([0.707, 0.0, 0.707]), np.array([0.0, 0.0, 1.0]),   "phase45_overhead"),           # G4 ~45°
]


# ============================================================
# 3. 扫描参数（v0.4 冻结规范）
# ============================================================
SCAN_2D     = True         # True = 2D 网格(yaw×pitch); False = 1D 纯 yaw

# yaw 网格：0°-355°，步长 5°，共 72 个（不含 360°）
YAW_RANGE   = (0, 355)     # [0, 355] inclusive
NUM_YAW     = 72           # 360 / 5 = 72
YAW_STEP    = 5

# pitch 网格：-90°-90°，步长 5°，共 37 个
PITCH_RANGE = (-90, 90)
NUM_PITCH   = 37           # (180 / 5) + 1 = 37
PITCH_STEP  = 5

# 姿态总数：72 × 37 = 2664
TOTAL_ATTITUDES = NUM_YAW * NUM_PITCH

# 渲染分辨率（13 号冻结规范）
RESOLUTION = 256           # 256×256

# ortho_scale（13 号冻结规范）
ORTHO_SCALE_FACTOR = 2.2   # ortho_scale = 2.2 × r_max


# ============================================================
# 4. BRDF 模型选择（v0.4 路线一 C 主线）
# ============================================================
# BRDF 主线：B0 project provisional Phong-like baseline
# 不等同于书中改进冯或 Torrance-Sparrow 五参数模型
BRDF_MODEL = "phong_like_provisional_baseline"

# GGX 作为 mismatch 对照分支，不进入 smoke test 主线
BRDF_BRANCH_GGX = "mismatch_control"


# ============================================================
# 5. 精度级别
# ============================================================
# 精度级别（控制速度/精度平衡）
#   fast   : 保留 20% 面元，秒级/姿态
#   medium : 保留 50% 面元，十几秒/姿态
#   full   : 不抽稀，分钟级/姿态（论文级精度）
ACCURACY_LEVEL = "full"    # Phase 0 使用 full（不抽稀）

# 精度抽稀比例
DECIMATE_RATIO = {
    "fast":   0.20,
    "medium": 0.50,
    "full":   1.00,
}


# ============================================================
# 6. sun visibility 与 shadow mapping
# ============================================================
# sun_visibility 主线：Level 2（优先实现，降级预案为 Level 1）
SUN_VISIBILITY_LEVEL = "camera_visible_nol_plus_sun_shadow_pass"  # Level 2
# 降级预案：SUN_VISIBILITY_LEVEL = "camera_visible_nol"          # Level 1

# shadow_mapping_method（Level 2 时使用）
SHADOW_MAPPING_METHOD = "depth_reprojection"

# v_sun_macro_mode（与 sun_visibility 对应）
# Level 2: "shadow_mask"
# Level 1: "identity"
V_SUN_MACRO_MODE = "shadow_mask"


# ============================================================
# 7. 图像预处理参数
# ============================================================
# log1p alpha（初始值，quick ablation 时测试 {5, 10, 20} + raw）
LOG1P_ALPHA = 10.0

# corpus-level I_scale（两阶段流程，CR-CODE-002）
# Pass 1: 统计全局 I_scale = max(I_linear)
# Pass 2: 使用统一 I_scale 生成 log1p PNG
CORPUS_LEVEL_I_SCALE = None  # 待 Pass 1 统计后填入


# ============================================================
# 8. 渲染开关（v0.4 阶段强制关闭，交由 Blender）
# ============================================================
ENABLE_RENDER = False    # 当前阶段不在 Python 端做图像渲染


# ============================================================
# 9. 图表样式与双语标签
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

# 部件配色
PART_COLORS = {
    "jinshuzhuti":    "silver",
    "taiyangnengban": "steelblue",
    "yinshenban":     "dimgray",
}


# ============================================================
# 10. 辅助函数
# ============================================================
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
        "project_root":         PROJECT_ROOT,
        "stl_dir":              STL_DIR,
        "output_dir":           OUTPUT_DIR,
        "code_dir":             CODE_DIR,
        "blender_exe":          BLENDER_EXE,
        "unit_scale":           UNIT_SCALE,
        "eps_nol_nov":          EPS_NOL_NOV,
        "depth_epsilon_m_initial": DEPTH_EPSILON_M_INITIAL,
        "depth_epsilon_m_final":   DEPTH_EPSILON_M_FINAL,
        "ray_batch":            RAY_BATCH,
        "sun_vector":           SUN_VECTOR.tolist(),
        "det_vector":           DET_VECTOR.tolist(),
        "scan_2d":              SCAN_2D,
        "yaw_range":            list(YAW_RANGE),
        "num_yaw":              NUM_YAW,
        "yaw_step":             YAW_STEP,
        "pitch_range":          list(PITCH_RANGE),
        "num_pitch":            NUM_PITCH,
        "pitch_step":           PITCH_STEP,
        "total_attitudes":      TOTAL_ATTITUDES,
        "resolution":           RESOLUTION,
        "ortho_scale_factor":   ORTHO_SCALE_FACTOR,
        "brdf_model":           BRDF_MODEL,
        "brdf_branch_ggx":      BRDF_BRANCH_GGX,
        "accuracy_level":       ACCURACY_LEVEL,
        "sun_visibility_level": SUN_VISIBILITY_LEVEL,
        "shadow_mapping_method": SHADOW_MAPPING_METHOD,
        "v_sun_macro_mode":     V_SUN_MACRO_MODE,
        "log1p_alpha":          LOG1P_ALPHA,
        "corpus_level_i_scale": CORPUS_LEVEL_I_SCALE,
        "enable_render":        ENABLE_RENDER,
        "lang_mode":            LANG_MODE,
        "fig_dpi":              FIG_DPI,
    }


# ============================================================
# 11. 版本记录
# ============================================================
CONFIG_VERSION = "v0.4.0"
CONFIG_CREATED = "2026-06-23"
CONFIG_NOTES = """
v0.4 配置主要改动：
1. yaw 网格从 73 改为 72（不含 360°），姿态总数 2664
2. BRDF 主线从 GGX 改为 phong_like_provisional_baseline（B0）
3. epsilon 语义分离：EPS_NOL_NOV 与 DEPTH_EPSILON_M
4. 输出目录改为 v0.4_results/（与 14 号规范一致）
5. sun_visibility 主线为 Level 2（camera_visible_nol_plus_sun_shadow_pass）
6. 明确 corpus-level I_scale 两阶段流程（CR-CODE-002）
"""

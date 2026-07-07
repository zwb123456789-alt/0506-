# -*- coding: utf-8 -*-
"""
p4physD_config.py —— P4-PHYS-D sun/view 小矩阵本轮局部配置（单一真源）
================================================================================
R153 任务单执行的本包配置。定义：
    - sun/view 小矩阵几何 registry（5 个几何，baseline + 4 个 ±7° 扰动）
    - 姿态候选清单（14 个，来自 20/21/23A/23B/01 baseline，不新增姿态搜索）
    - baseline EXR/ocs.json 复用路径解析
    - 冻结物理常量（r_max/pixel_area/epsilon/i_scale，均为 model-only 常量）

坐标口径与归一化：
    - SUN/DET 向量为惯性系方向向量，渲染与后处理端统一做 L2 归一化后使用。
    - baseline: SUN=[1,0,0.3], DET=[0.5,-1,0.1]（phase63/L1-G1，与 24/25 包一致）。
    - 扰动几何由 baseline 单位方向绕指定轴做 Rodrigues 旋转 ±7° 得到，角距 baseline 恰为 7°。
        * 太阳扰动 G1/G2：绕世界 Y 轴旋转 SUN（sun_dir.y=0，旋转轴与 sun 垂直，角距=7°）。
        * 探测器扰动 G3/G4：绕 (det_dir × Z) 归一化轴旋转 DET（与 det 垂直，角距=7°）。

渲染复用原则（物理精确，非近似）：
    - camera 几何 pass（Normal/Depth/IndexOB/Position）只依赖姿态与探测器方向，与太阳无关
      => 太阳扰动几何（G1/G2）复用 baseline camera EXR，只新渲染 sun EXR。
    - sun 几何 pass（Depth/Position，太阳视角）只依赖姿态与太阳方向，与探测器无关
      => 探测器扰动几何（G3/G4）复用 baseline sun EXR，只新渲染 camera EXR。
    - G0 baseline 两视角全复用，不新渲染（用于复现既有 ocs.json 作为一致性锚点）。

边界：
    - 本轮不做全 sun/view 全局最亮搜索；几何数=5，姿态数=14，新增渲染单元受控。
    - material 仍为 B0 proxy；不改 20/21/23A/23B/24/25 源包。
"""

import numpy as np
from pathlib import Path

# ------------------------------------------------------------------
# 路径
# ------------------------------------------------------------------
THIS_DIR = Path(__file__).resolve().parent          # 26/scripts
PKG26    = THIS_DIR.parent                           # 26 包根
V04_ROOT = THIS_DIR.parents[2]                       # 项目根
RESULTS  = V04_ROOT / "v0.4_results"
CODE     = V04_ROOT / "06_v0.4_code"

RENDER_BASE = PKG26 / "render"
POST_BASE   = PKG26 / "postprocess"

# ------------------------------------------------------------------
# 冻结物理常量（model-only，与几何无关；与 24/25/run_full_postprocess 一致）
# ------------------------------------------------------------------
R_MAX = 1.4726051706213208
ORTHO_SCALE_M = 2.2 * R_MAX
PIXEL_AREA_M2 = (ORTHO_SCALE_M / 256) ** 2
DEPTH_EPSILON_M_FINAL = 0.7952109582768545
I_SCALE = 0.5444863931551639
LOG1P_ALPHA = 10.0
NOL_EPS = 1e-6
NOV_EPS = 1e-6
PHONG_N = 80  # B0 metal specular exponent
INDEXOB_TO_PART = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}

# ------------------------------------------------------------------
# baseline 几何（phase63 / L1-G1）
# ------------------------------------------------------------------
SUN_BASE = np.array([1.0, 0.0, 0.3])
DET_BASE = np.array([0.5, -1.0, 0.1])
SUN_DIR_BASE = SUN_BASE / np.linalg.norm(SUN_BASE)
DET_DIR_BASE = DET_BASE / np.linalg.norm(DET_BASE)

PERTURB_DEG = 7.0  # baseline 角距（5°–10° 区间内）


def _rodrigues(v, axis, deg):
    """绕单位轴 axis 将向量 v 旋转 deg 度（Rodrigues）。"""
    v = np.asarray(v, float)
    axis = np.asarray(axis, float)
    axis = axis / np.linalg.norm(axis)
    t = np.radians(deg)
    return (v * np.cos(t)
            + np.cross(axis, v) * np.sin(t)
            + axis * np.dot(axis, v) * (1.0 - np.cos(t)))


def angle_deg(a, b):
    a = np.asarray(a, float); a = a / np.linalg.norm(a)
    b = np.asarray(b, float); b = b / np.linalg.norm(b)
    return float(np.degrees(np.arccos(np.clip(a @ b, -1.0, 1.0))))


# 扰动向量（在归一化 baseline 方向上旋转 ±7°）
_SUN_Y_AXIS = np.array([0.0, 1.0, 0.0])                    # 与 sun_dir 垂直
_DET_AXIS = np.cross(DET_DIR_BASE, np.array([0.0, 0.0, 1.0]))
_DET_AXIS = _DET_AXIS / np.linalg.norm(_DET_AXIS)         # 与 det_dir 垂直

SUN_DIR_G1 = _rodrigues(SUN_DIR_BASE, _SUN_Y_AXIS, +PERTURB_DEG)
SUN_DIR_G2 = _rodrigues(SUN_DIR_BASE, _SUN_Y_AXIS, -PERTURB_DEG)
DET_DIR_G3 = _rodrigues(DET_DIR_BASE, _DET_AXIS, +PERTURB_DEG)
DET_DIR_G4 = _rodrigues(DET_DIR_BASE, _DET_AXIS, -PERTURB_DEG)


# ------------------------------------------------------------------
# 几何 registry
#   render_view: 'none' | 'sun' | 'camera'  —— 本几何需要新渲染的视角
#   reuse_view : baseline 复用的视角来源
# ------------------------------------------------------------------
GEOMETRIES = [
    {
        "geom_id": "G0_baseline", "kind": "baseline",
        "sun_dir": SUN_DIR_BASE, "det_dir": DET_DIR_BASE,
        "sun_ang_from_base": 0.0, "det_ang_from_base": 0.0,
        "render_view": "none", "camera_source": "baseline", "sun_source": "baseline",
        "note": "phase63/L1-G1 baseline，两视角全复用，用于复现 ocs.json",
    },
    {
        "geom_id": "G1_sun_plus", "kind": "sun_perturb",
        "sun_dir": SUN_DIR_G1, "det_dir": DET_DIR_BASE,
        "sun_ang_from_base": angle_deg(SUN_DIR_G1, SUN_DIR_BASE), "det_ang_from_base": 0.0,
        "render_view": "sun", "camera_source": "baseline", "sun_source": "new_26",
        "note": "太阳方向绕世界Y +7°；camera 复用 baseline，sun 新渲染",
    },
    {
        "geom_id": "G2_sun_minus", "kind": "sun_perturb",
        "sun_dir": SUN_DIR_G2, "det_dir": DET_DIR_BASE,
        "sun_ang_from_base": angle_deg(SUN_DIR_G2, SUN_DIR_BASE), "det_ang_from_base": 0.0,
        "render_view": "sun", "camera_source": "baseline", "sun_source": "new_26",
        "note": "太阳方向绕世界Y -7°；camera 复用 baseline，sun 新渲染",
    },
    {
        "geom_id": "G3_view_plus", "kind": "view_perturb",
        "sun_dir": SUN_DIR_BASE, "det_dir": DET_DIR_G3,
        "sun_ang_from_base": 0.0, "det_ang_from_base": angle_deg(DET_DIR_G3, DET_DIR_BASE),
        "render_view": "camera", "camera_source": "new_26", "sun_source": "baseline",
        "note": "探测器方向绕(det×Z) +7°；sun 复用 baseline，camera 新渲染",
    },
    {
        "geom_id": "G4_view_minus", "kind": "view_perturb",
        "sun_dir": SUN_DIR_BASE, "det_dir": DET_DIR_G4,
        "sun_ang_from_base": 0.0, "det_ang_from_base": angle_deg(DET_DIR_G4, DET_DIR_BASE),
        "render_view": "camera", "camera_source": "new_26", "sun_source": "baseline",
        "note": "探测器方向绕(det×Z) -7°；sun 复用 baseline，camera 新渲染",
    },
]
GEOM_BY_ID = {g["geom_id"]: g for g in GEOMETRIES}


# ------------------------------------------------------------------
# 姿态候选（14 个，全部来自既有 baseline 渲染，不新增姿态搜索）
#   src_dir 相对 RESULTS，用于解析 baseline camera/sun EXR 与 ocs.json
# ------------------------------------------------------------------
def _p(rel):  # baseline 源目录（相对 RESULTS）
    return rel

POSES = [
    # --- 必选 ---
    {"pose_id": "A_top1", "group": "mandatory", "label": "yaw2450_pitchp0275_roll+015",
     "yaw": 245.0, "pitch": 27.5, "roll": 15.0, "role": "top1",
     "src": "23A_three_axis_p4phys_top1_roll_confirmation/render/shadow_passes/phase63/roll+015",
     "post": "23A_three_axis_p4phys_top1_roll_confirmation/postprocess/phase63/roll+015"},
    {"pose_id": "B_R4", "group": "mandatory", "label": "yaw1475_pitchp0125_roll+000",
     "yaw": 147.5, "pitch": 12.5, "roll": 0.0, "role": "R4_robust",
     "src": "21_three_axis_p3_local_refinement/render/shadow_passes/phase63/roll+000",
     "post": "21_three_axis_p3_local_refinement/postprocess/phase63/roll+000"},
    {"pose_id": "C_R3", "group": "mandatory", "label": "yaw055_pitch+060_roll+000",
     "yaw": 55.0, "pitch": 60.0, "roll": 0.0, "role": "R3_negative",
     "src": "01_fullrun/shadow_passes",
     "post": "01_fullrun/postprocess"},
    # --- D: top-1 邻域（roll +12.5/+15/+17.5 与 pitch/yaw 邻点）---
    {"pose_id": "D1", "group": "top1_neighbor", "label": "yaw2450_pitchp0300_roll+015",
     "yaw": 245.0, "pitch": 30.0, "roll": 15.0, "role": "top1_neighbor",
     "src": "21_three_axis_p3_local_refinement/render/shadow_passes/phase63/roll+015",
     "post": "21_three_axis_p3_local_refinement/postprocess/phase63/roll+015"},
    {"pose_id": "D2", "group": "top1_neighbor", "label": "yaw2450_pitchp0325_roll+015",
     "yaw": 245.0, "pitch": 32.5, "roll": 15.0, "role": "top1_neighbor",
     "src": "21_three_axis_p3_local_refinement/render/shadow_passes/phase63/roll+015",
     "post": "21_three_axis_p3_local_refinement/postprocess/phase63/roll+015"},
    {"pose_id": "D3", "group": "top1_neighbor", "label": "yaw2475_pitchp0375_roll+015",
     "yaw": 247.5, "pitch": 37.5, "roll": 15.0, "role": "top1_neighbor",
     "src": "21_three_axis_p3_local_refinement/render/shadow_passes/phase63/roll+015",
     "post": "21_three_axis_p3_local_refinement/postprocess/phase63/roll+015"},
    {"pose_id": "D4", "group": "top1_neighbor", "label": "yaw2425_pitchp0225_roll+015",
     "yaw": 242.5, "pitch": 22.5, "roll": 15.0, "role": "top1_neighbor",
     "src": "23B_three_axis_p4phys_pitch_boundary_followup/render/shadow_passes/phase63/roll+015",
     "post": "23B_three_axis_p4phys_pitch_boundary_followup/postprocess/phase63/roll+015"},
    {"pose_id": "D5_roll125", "group": "top1_neighbor", "label": "yaw2450_pitchp0275_roll+0125",
     "yaw": 245.0, "pitch": 27.5, "roll": 12.5, "role": "top1_neighbor_roll125",
     "src": "23A_three_axis_p4phys_top1_roll_confirmation/render/shadow_passes/phase63/roll+0125",
     "post": "23A_three_axis_p4phys_top1_roll_confirmation/postprocess/phase63/roll+0125"},
    {"pose_id": "D6_roll175", "group": "top1_neighbor", "label": "yaw2475_pitchp0300_roll+0175",
     "yaw": 247.5, "pitch": 30.0, "roll": 17.5, "role": "top1_neighbor_roll175",
     "src": "23A_three_axis_p4phys_top1_roll_confirmation/render/shadow_passes/phase63/roll+0175",
     "post": "23A_three_axis_p4phys_top1_roll_confirmation/postprocess/phase63/roll+0175"},
    # --- E: R4 同簇（near_specular_metal=1）---
    {"pose_id": "E1_R4roll-15", "group": "R4_cluster", "label": "yaw1475_pitchp0125_roll-015",
     "yaw": 147.5, "pitch": 12.5, "roll": -15.0, "role": "R4_cluster_nsm1",
     "src": "21_three_axis_p3_local_refinement/render/shadow_passes/phase63/roll-015",
     "post": "21_three_axis_p3_local_refinement/postprocess/phase63/roll-015"},
    {"pose_id": "E2_R4roll+15", "group": "R4_cluster", "label": "yaw1475_pitchp0125_roll+015",
     "yaw": 147.5, "pitch": 12.5, "roll": 15.0, "role": "R4_cluster_nsm1",
     "src": "21_three_axis_p3_local_refinement/render/shadow_passes/phase63/roll+015",
     "post": "21_three_axis_p3_local_refinement/postprocess/phase63/roll+015"},
    # --- F: non-mechanism bright-edge（near_specular_metal=0 但 OCS 高）---
    {"pose_id": "F1_edge", "group": "bright_edge", "label": "yaw2425_pitchp0275_roll+015",
     "yaw": 242.5, "pitch": 27.5, "roll": 15.0, "role": "bright_edge_nsm0",
     "src": "23A_three_axis_p4phys_top1_roll_confirmation/render/shadow_passes/phase63/roll+015",
     "post": "23A_three_axis_p4phys_top1_roll_confirmation/postprocess/phase63/roll+015"},
    {"pose_id": "F2_edge", "group": "bright_edge", "label": "yaw2475_pitchp0300_roll+015",
     "yaw": 247.5, "pitch": 30.0, "roll": 15.0, "role": "bright_edge_nsm0",
     "src": "21_three_axis_p3_local_refinement/render/shadow_passes/phase63/roll+015",
     "post": "21_three_axis_p3_local_refinement/postprocess/phase63/roll+015"},
    {"pose_id": "F3_edge", "group": "bright_edge", "label": "yaw240_pitch+015_roll+015",
     "yaw": 240.0, "pitch": 15.0, "roll": 15.0, "role": "bright_edge_nsm0",
     "src": "20_three_axis_p2_sparse_grid/render/shadow_passes/phase63/roll+015",
     "post": "20_three_axis_p2_sparse_grid/postprocess/phase63/roll+015"},
]
POSE_BY_ID = {p["pose_id"]: p for p in POSES}

# smoke 用姿态（top1/R4/R3）与几何（探测器扰动，需新渲染 camera）
SMOKE_GEOM = "G3_view_plus"
SMOKE_POSES = ["A_top1", "B_R4", "C_R3"]


# ------------------------------------------------------------------
# baseline EXR / ocs.json 路径解析
# ------------------------------------------------------------------
def baseline_camera_exr(pose):
    return RESULTS / pose["src"] / f"{pose['label']}_camera.exr"

def baseline_sun_exr(pose):
    return RESULTS / pose["src"] / f"{pose['label']}_sun.exr"

def baseline_ocs_json(pose):
    return RESULTS / pose["post"] / f"{pose['label']}_ocs.json"


# 26 新渲染视角输出路径
def new_render_exr(geom_id, pose, view):
    d = RENDER_BASE / geom_id
    return d / f"{pose['label']}_{view}.exr"


def resolve_exr_pair(geom, pose):
    """按几何解析 (camera_exr, sun_exr) 实际使用路径与来源标签。"""
    gid = geom["geom_id"]
    if geom["camera_source"] == "baseline":
        cam = baseline_camera_exr(pose); cam_src = "REUSED_BASELINE"
    else:
        cam = new_render_exr(gid, pose, "camera"); cam_src = "NEW_26"
    if geom["sun_source"] == "baseline":
        sun = baseline_sun_exr(pose); sun_src = "REUSED_BASELINE"
    else:
        sun = new_render_exr(gid, pose, "sun"); sun_src = "NEW_26"
    return cam, cam_src, sun, sun_src


if __name__ == "__main__":
    print("=== P4-PHYS-D config self-check ===")
    print(f"n_geometries={len(GEOMETRIES)}  n_poses={len(POSES)}")
    for g in GEOMETRIES:
        print(f"  {g['geom_id']:14s} sun={np.round(g['sun_dir'],4)} det={np.round(g['det_dir'],4)} "
              f"d_sun={g['sun_ang_from_base']:.2f} d_det={g['det_ang_from_base']:.2f} render={g['render_view']}")
    # new render unit count
    n_new = 0
    for g in GEOMETRIES:
        if g["render_view"] != "none":
            n_new += len(POSES)
    print(f"formal new render units (1 view × {len(POSES)} poses × 4 geoms) = {n_new}")
    # baseline availability
    miss = 0
    for pose in POSES:
        for f in (baseline_camera_exr(pose), baseline_sun_exr(pose), baseline_ocs_json(pose)):
            if not f.is_file():
                print(f"  [MISSING] {pose['pose_id']}: {f}"); miss += 1
    print(f"baseline availability: {'ALL OK' if miss==0 else str(miss)+' MISSING'}")

# -*- coding: utf-8 -*-
"""
p4physF_config.py —— P4-PHYS-F Hsp_vm 角落局部姿态与几何加密 本轮局部配置（单一真源）
================================================================================
R157 任务单执行的本包配置。两阶段：
    Stage B：固定 Hsp_vm(sun+7, view-7)，围绕 C_R3(yaw=55,pitch=60,roll=0) 做 3×3×3 局部姿态网格
             （27 姿态；中心=既有 C_R3 复用，26 个新姿态 × 2 视角 = 52 新渲染单元上限）。
    Stage C：对 ≤6 个姿态（C_R3 / Stage1_best / A_top1 / D5 / D6 / R4，去重）做 sun/view microgrid
             sun_offset ∈ {+5,+7,+9} × view_offset ∈ {-9,-7,-5}（中心 = Hsp_vm）。
             每姿态只需新增 cam_vm5/cam_vm9/sun_sp5/sun_sp9 共 4 单元（≤24 单元上限）。

EXR 复用原理（与 26/27 完全一致，物理精确）：
    camera EXR 只由 view_offset 与姿态决定；sun EXR 只由 sun_offset 与姿态决定。
    - 旧姿态（26 包 14 姿态集内）@ view-7 / sun+7：复用 26/render/G4_view_minus 与 G1_sun_plus。
    - 新姿态（Stage B 网格）@ view-7 / sun+7：渲染进 28/render/cam_vm7 与 sun_sp7。
    - 任意姿态 @ view-5/-9、sun+5/+9：渲染进 28/render/cam_vm5|cam_vm9|sun_sp5|sun_sp9。

坐标口径：直接 import 26 包 config（Rodrigues 旋转、baseline 向量、物理常量），保证同源无漂移。
    sun ±deg：绕世界 Y 轴旋转归一化 SUN_DIR_BASE；view ±deg：绕 (det×Z) 归一化轴旋转 DET_DIR_BASE。

红线：新增渲染硬上限 ≤80；不改 20/21/23A/23B/24/25/26/27 源包；不训练；material 仍为 B0 proxy。
"""

import importlib.util
from pathlib import Path

import numpy as np

# ------------------------------------------------------------------
# 路径
# ------------------------------------------------------------------
THIS_DIR = Path(__file__).resolve().parent          # 28/scripts
PKG28    = THIS_DIR.parent                           # 28 包根
V04_ROOT = THIS_DIR.parents[2]                       # 项目根
RESULTS  = V04_ROOT / "v0.4_results"

PKG26 = RESULTS / "26_three_axis_p4phys_d_sunview_small_matrix"
PKG27 = RESULTS / "27_three_axis_p4phys_e_sunview_3x3_cross_grid"

RENDER_BASE = PKG28 / "render"
POST_BASE   = PKG28 / "postprocess"

# ------------------------------------------------------------------
# 复用 26 包 config（常量 / 旧姿态 / 方向构造），保证同源无漂移
# ------------------------------------------------------------------
_spec26 = importlib.util.spec_from_file_location(
    "p4physD_config", str(PKG26 / "scripts" / "p4physD_config.py"))
cfg26 = importlib.util.module_from_spec(_spec26)
_spec26.loader.exec_module(cfg26)

R_MAX = cfg26.R_MAX
PIXEL_AREA_M2 = cfg26.PIXEL_AREA_M2
DEPTH_EPSILON_M_FINAL = cfg26.DEPTH_EPSILON_M_FINAL
I_SCALE = cfg26.I_SCALE
NOL_EPS = cfg26.NOL_EPS
NOV_EPS = cfg26.NOV_EPS
PHONG_N = cfg26.PHONG_N
INDEXOB_TO_PART = cfg26.INDEXOB_TO_PART

SUN_DIR_BASE = cfg26.SUN_DIR_BASE
DET_DIR_BASE = cfg26.DET_DIR_BASE
angle_deg = cfg26.angle_deg

_SUN_Y_AXIS = np.array([0.0, 1.0, 0.0])
_DET_AXIS = np.cross(DET_DIR_BASE, np.array([0.0, 0.0, 1.0]))
_DET_AXIS = _DET_AXIS / np.linalg.norm(_DET_AXIS)


def _rodrigues(v, axis, deg):
    v = np.asarray(v, float)
    axis = np.asarray(axis, float); axis = axis / np.linalg.norm(axis)
    t = np.radians(deg)
    return (v * np.cos(t) + np.cross(axis, v) * np.sin(t)
            + axis * np.dot(axis, v) * (1.0 - np.cos(t)))


# sun/view 方向 registry（+7/-7 直接取 26 包向量，保证与 26/27 逐位一致）
SUN_DIR = {
    5: _rodrigues(SUN_DIR_BASE, _SUN_Y_AXIS, +5.0),
    7: cfg26.SUN_DIR_G1,
    9: _rodrigues(SUN_DIR_BASE, _SUN_Y_AXIS, +9.0),
}
DET_DIR = {
    -5: _rodrigues(DET_DIR_BASE, _DET_AXIS, -5.0),
    -7: cfg26.DET_DIR_G4,
    -9: _rodrigues(DET_DIR_BASE, _DET_AXIS, -9.0),
}

SUN_OFFSETS = [5, 7, 9]
VIEW_OFFSETS = [-9, -7, -5]
CENTER_SO, CENTER_VO = 7, -7   # Hsp_vm


def geom_id(so, vo):
    return f"sp{so}_vm{abs(vo)}"


GEOMETRIES_C = []
for so in SUN_OFFSETS:
    for vo in VIEW_OFFSETS:
        GEOMETRIES_C.append({
            "geom_id": geom_id(so, vo), "sun_offset": so, "view_offset": vo,
            "sun_dir": SUN_DIR[so], "det_dir": DET_DIR[vo],
            "is_center": (so == CENTER_SO and vo == CENTER_VO),
            "sun_ang_from_base": angle_deg(SUN_DIR[so], SUN_DIR_BASE),
            "det_ang_from_base": angle_deg(DET_DIR[vo], DET_DIR_BASE),
        })
GEOM_BY_ID_C = {g["geom_id"]: g for g in GEOMETRIES_C}

# ------------------------------------------------------------------
# Stage B 局部姿态网格（R157 §5）
# ------------------------------------------------------------------
YAW_GRID = [35, 55, 75]
PITCH_GRID = [45, 60, 75]
ROLL_GRID = [-20, 0, 20]


def pose_label(yaw, pitch, roll):
    return f"yaw{int(yaw):03d}_pitch{int(pitch):+04d}_roll{int(roll):+04d}"


# 旧姿态（26 包 14 姿态集内，@sun+7/view-7 可复用 26 render）
OLD_POSE_IDS_STAGEC = ["C_R3", "A_top1", "D5_roll125", "D6_roll175", "B_R4"]
OLD_POSES = {pid: cfg26.POSE_BY_ID[pid] for pid in OLD_POSE_IDS_STAGEC}

C_R3_LABEL = cfg26.POSE_BY_ID["C_R3"]["label"]   # yaw055_pitch+060_roll+000


def build_stageB_poses():
    """27 个网格姿态；中心 = C_R3（复用，is_new=False），其余 26 个为新姿态。"""
    poses = []
    for yaw in YAW_GRID:
        for pitch in PITCH_GRID:
            for roll in ROLL_GRID:
                is_center = (yaw == 55 and pitch == 60 and roll == 0)
                lab = C_R3_LABEL if is_center else pose_label(yaw, pitch, roll)
                on_edge = (yaw in (YAW_GRID[0], YAW_GRID[-1])
                           or pitch in (PITCH_GRID[0], PITCH_GRID[-1])
                           or roll in (ROLL_GRID[0], ROLL_GRID[-1]))
                poses.append({
                    "pose_id": f"B_y{yaw}_p{pitch}_r{roll:+d}" if not is_center else "C_R3",
                    "label": lab, "yaw": float(yaw), "pitch": float(pitch), "roll": float(roll),
                    "is_new": (not is_center), "is_center": is_center, "on_grid_edge": on_edge,
                })
    return poses


STAGEB_POSES = build_stageB_poses()
STAGEB_NEW = [p for p in STAGEB_POSES if p["is_new"]]      # 26 个

# smoke 姿态（R157 §4：yaw=55, pitch=60, roll=+20，属 Stage B 网格点）
SMOKE_POSE = next(p for p in STAGEB_POSES
                  if p["yaw"] == 55 and p["pitch"] == 60 and p["roll"] == 20)

# ------------------------------------------------------------------
# EXR 路径解析
# ------------------------------------------------------------------
def camera_exr(pose_label_, is_new_pose, vo):
    """camera EXR 只由 view_offset 与姿态决定。"""
    if vo == -7 and not is_new_pose:
        return cfg26.RENDER_BASE / "G4_view_minus" / f"{pose_label_}_camera.exr", "REUSED_26/G4_view_minus"
    return RENDER_BASE / f"cam_vm{abs(vo)}" / f"{pose_label_}_camera.exr", f"28/cam_vm{abs(vo)}"


def sun_exr(pose_label_, is_new_pose, so):
    """sun EXR 只由 sun_offset 与姿态决定。"""
    if so == 7 and not is_new_pose:
        return cfg26.RENDER_BASE / "G1_sun_plus" / f"{pose_label_}_sun.exr", "REUSED_26/G1_sun_plus"
    return RENDER_BASE / f"sun_sp{so}" / f"{pose_label_}_sun.exr", f"28/sun_sp{so}"


def anchor_27_ocs_json(pose_label_, so, vo):
    """(sun+7,view-7) 且旧姿态：27 包 Hsp_vm 已有 ocs.json，作数值一致性锚点。"""
    if so == 7 and vo == -7:
        p = PKG27 / "postprocess" / "Hsp_vm" / f"{pose_label_}_ocs.json"
        return p if p.is_file() else None
    return None


# ------------------------------------------------------------------
# 渲染预算（R157 硬上限）
# ------------------------------------------------------------------
STAGEB_RENDER_CAP = 52
STAGEC_RENDER_CAP = 24
TOTAL_RENDER_CAP = 80

STAGEC_POSES_JSON = PKG28 / "audit" / "stagec_poses.json"   # Stage B 后由 postprocess 写出


if __name__ == "__main__":
    print("=== P4-PHYS-F config self-check ===")
    print(f"StageB poses={len(STAGEB_POSES)} (new={len(STAGEB_NEW)}, center reuse=1)")
    print(f"StageB new render units = {len(STAGEB_NEW) * 2} (cap {STAGEB_RENDER_CAP})")
    print(f"StageC geometries = {len(GEOMETRIES_C)}; per-pose new units = 4; cap {STAGEC_RENDER_CAP}")
    print(f"smoke pose: {SMOKE_POSE['label']}")
    for g in GEOMETRIES_C:
        print(f"  {g['geom_id']:10s} d_sun={g['sun_ang_from_base']:.2f} d_det={g['det_ang_from_base']:.2f}"
              f"{'  <== center Hsp_vm' if g['is_center'] else ''}")
    # 旧姿态复用可达性
    miss = 0
    for pid, pose in OLD_POSES.items():
        for f, src in (camera_exr(pose["label"], False, -7), sun_exr(pose["label"], False, 7)):
            pass
        cam, _ = camera_exr(pose["label"], False, -7)
        sun, _ = sun_exr(pose["label"], False, 7)
        for f in (cam, sun):
            if not f.is_file():
                print(f"  [MISSING] {pid}: {f}"); miss += 1
    print(f"old-pose reuse availability: {'ALL OK' if miss == 0 else str(miss) + ' MISSING'}")

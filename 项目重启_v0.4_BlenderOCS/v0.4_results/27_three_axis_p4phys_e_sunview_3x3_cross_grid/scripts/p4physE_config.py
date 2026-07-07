# -*- coding: utf-8 -*-
"""
p4physE_config.py —— P4-PHYS-E sun/view 3×3 组合小网格本轮局部配置（单一真源）
================================================================================
R155 任务单执行的本包配置。在 R153/26 包 baseline ±7° 基础上，补齐 sun 与 view
**同时**扰动的 3×3 组合几何小网格（9 个组合几何 × 14 个姿态候选 = 126 组合）。

核心复用原理（沿用并复用 26 包，0 新增渲染）：
    - camera 几何 pass（Normal/Depth/IndexOB/Position）只依赖姿态与探测器方向，与太阳无关
        => camera EXR 只由 view_offset 决定。
    - sun 几何 pass（Depth/Position，太阳视角）只依赖姿态与太阳方向，与探测器无关
        => sun EXR 只由 sun_offset 决定。
    因此 3×3 组合的每个格点都能从 26 包已渲染 EXR 中拼出：
        camera: view0 复用 baseline camera；view+7 复用 26/G3_view_plus；view-7 复用 26/G4_view_minus
        sun   : sun0  复用 baseline sun；   sun+7  复用 26/G1_sun_plus； sun-7  复用 26/G2_sun_minus
    9 组合中：
        5 个（H00 / pure sun±7 / pure view±7）在数值上应精确复现 26 包 G0/G1/G2/G3/G4；
        4 个角落（sun±7 & view±7 同时扰动）是 26 已有 sun/camera EXR 的新组合，仍 0 新渲染。

坐标口径与常量：直接 import 26 包 config，保证与 24/25/26 完全同源、无漂移。

边界：
    - 本轮不做全 sun/view 全姿态搜索；几何=9，姿态=14（复用同源），新增渲染=0。
    - material 仍为 B0 proxy；不改 20/21/23A/23B/24/25/26 源包。
"""

import sys
import importlib.util
from pathlib import Path

import numpy as np

# ------------------------------------------------------------------
# 路径
# ------------------------------------------------------------------
THIS_DIR = Path(__file__).resolve().parent          # 27/scripts
PKG27    = THIS_DIR.parent                           # 27 包根
V04_ROOT = THIS_DIR.parents[2]                       # 项目根
RESULTS  = V04_ROOT / "v0.4_results"
CODE     = V04_ROOT / "06_v0.4_code"

PKG26    = RESULTS / "26_three_axis_p4phys_d_sunview_small_matrix"
PKG26_SCRIPTS = PKG26 / "scripts"
PKG26_RENDER  = PKG26 / "render"

POST_BASE = PKG27 / "postprocess"

# ------------------------------------------------------------------
# 复用 26 包 config（常量 / 姿态候选 / baseline 路径解析 / 扰动方向），保证同源无漂移
# ------------------------------------------------------------------
_spec26 = importlib.util.spec_from_file_location(
    "p4physD_config", str(PKG26_SCRIPTS / "p4physD_config.py"))
cfg26 = importlib.util.module_from_spec(_spec26)
_spec26.loader.exec_module(cfg26)

# 冻结物理常量（model-only，直接沿用 26 包）
R_MAX = cfg26.R_MAX
PIXEL_AREA_M2 = cfg26.PIXEL_AREA_M2
DEPTH_EPSILON_M_FINAL = cfg26.DEPTH_EPSILON_M_FINAL
I_SCALE = cfg26.I_SCALE
NOL_EPS = cfg26.NOL_EPS
NOV_EPS = cfg26.NOV_EPS
PHONG_N = cfg26.PHONG_N
INDEXOB_TO_PART = cfg26.INDEXOB_TO_PART

# baseline / 扰动方向向量（与 26 包完全一致）
SUN_DIR_BASE = cfg26.SUN_DIR_BASE
DET_DIR_BASE = cfg26.DET_DIR_BASE
SUN_DIR_SUN_PLUS  = cfg26.SUN_DIR_G1   # sun +7
SUN_DIR_SUN_MINUS = cfg26.SUN_DIR_G2   # sun -7
DET_DIR_VIEW_PLUS  = cfg26.DET_DIR_G3  # view +7
DET_DIR_VIEW_MINUS = cfg26.DET_DIR_G4  # view -7
PERTURB_DEG = cfg26.PERTURB_DEG        # 7.0

# 姿态候选（14 个，与 26 完全一致，不新增姿态搜索）
POSES = cfg26.POSES
POSE_BY_ID = cfg26.POSE_BY_ID

angle_deg = cfg26.angle_deg


# ------------------------------------------------------------------
# sun / view 轴定义：sun_offset 决定 sun_dir + sun EXR；view_offset 决定 det_dir + camera EXR
#   sun_source / camera_source 指向 26 包已渲染 EXR 或 baseline 源
# ------------------------------------------------------------------
SUN_AXIS = {
    0:  {"tag": "sun0",  "sun_dir": SUN_DIR_BASE,      "sun_source": "baseline",       "ang": 0.0},
    +7: {"tag": "sunp7", "sun_dir": SUN_DIR_SUN_PLUS,  "sun_source": "26_G1_sun_plus", "ang": PERTURB_DEG},
    -7: {"tag": "sunm7", "sun_dir": SUN_DIR_SUN_MINUS, "sun_source": "26_G2_sun_minus","ang": PERTURB_DEG},
}
VIEW_AXIS = {
    0:  {"tag": "view0",  "det_dir": DET_DIR_BASE,       "camera_source": "baseline",         "ang": 0.0},
    +7: {"tag": "viewp7", "det_dir": DET_DIR_VIEW_PLUS,  "camera_source": "26_G3_view_plus",  "ang": PERTURB_DEG},
    -7: {"tag": "viewm7", "det_dir": DET_DIR_VIEW_MINUS, "camera_source": "26_G4_view_minus", "ang": PERTURB_DEG},
}

# 26 render 子目录名（用于复用 EXR）
SUN_SRC_DIR = {"26_G1_sun_plus": "G1_sun_plus", "26_G2_sun_minus": "G2_sun_minus"}
CAM_SRC_DIR = {"26_G3_view_plus": "G3_view_plus", "26_G4_view_minus": "G4_view_minus"}

# 组合几何命名（R155 §4 建议）
GEOM_NAME = {
    (0, 0):   "H00_baseline",
    (+7, 0):  "Hsp_v0",
    (-7, 0):  "Hsm_v0",
    (0, +7):  "Hs0_vp",
    (0, -7):  "Hs0_vm",
    (+7, +7): "Hsp_vp",
    (+7, -7): "Hsp_vm",
    (-7, +7): "Hsm_vp",
    (-7, -7): "Hsm_vm",
}

# 5 个组合几何与 26 包 G0-G4 一一对应（数值一致性锚点）
#   (sun_off, view_off) -> 26 geom_id
ANCHOR_26 = {
    (0, 0):  "G0_baseline",
    (+7, 0): "G1_sun_plus",
    (-7, 0): "G2_sun_minus",
    (0, +7): "G3_view_plus",
    (0, -7): "G4_view_minus",
}


def _build_geometries():
    geoms = []
    # 顺序：先 baseline，再 pure sun，再 pure view，最后 4 角落
    order = [(0, 0), (+7, 0), (-7, 0), (0, +7), (0, -7),
             (+7, +7), (+7, -7), (-7, +7), (-7, -7)]
    for (so, vo) in order:
        sa = SUN_AXIS[so]; va = VIEW_AXIS[vo]
        is_corner = (so != 0 and vo != 0)
        geoms.append({
            "geom_id": GEOM_NAME[(so, vo)],
            "sun_offset": so, "view_offset": vo,
            "kind": "baseline" if (so == 0 and vo == 0)
                    else ("pure_sun" if vo == 0 else ("pure_view" if so == 0 else "cross_corner")),
            "sun_dir": sa["sun_dir"], "det_dir": va["det_dir"],
            "sun_source": sa["sun_source"], "camera_source": va["camera_source"],
            "sun_ang_from_base": sa["ang"], "det_ang_from_base": va["ang"],
            "is_corner": is_corner,
            "anchor_26": ANCHOR_26.get((so, vo), ""),
            "note": f"sun_offset={so:+d} view_offset={vo:+d}; "
                    f"cam<-{va['camera_source']} sun<-{sa['sun_source']}",
        })
    return geoms


GEOMETRIES = _build_geometries()
GEOM_BY_ID = {g["geom_id"]: g for g in GEOMETRIES}


# ------------------------------------------------------------------
# EXR 路径解析（全部指向 26 包已渲染 EXR 或 baseline 源；0 新增渲染）
# ------------------------------------------------------------------
def resolve_camera_exr(geom, pose):
    src = geom["camera_source"]
    if src == "baseline":
        return cfg26.baseline_camera_exr(pose), "REUSED_BASELINE"
    d = PKG26_RENDER / CAM_SRC_DIR[src]
    return d / f"{pose['label']}_camera.exr", f"REUSED_26/{CAM_SRC_DIR[src]}"


def resolve_sun_exr(geom, pose):
    src = geom["sun_source"]
    if src == "baseline":
        return cfg26.baseline_sun_exr(pose), "REUSED_BASELINE"
    d = PKG26_RENDER / SUN_SRC_DIR[src]
    return d / f"{pose['label']}_sun.exr", f"REUSED_26/{SUN_SRC_DIR[src]}"


def resolve_exr_pair(geom, pose):
    cam, cam_src = resolve_camera_exr(geom, pose)
    sun, sun_src = resolve_sun_exr(geom, pose)
    return cam, cam_src, sun, sun_src


def anchor_ocs_json(geom, pose):
    """26 包中对应锚点几何的 ocs.json（用于 5 个可锚点组合的数值一致性核验）。"""
    aid = geom["anchor_26"]
    if not aid:
        return None
    return PKG26 / "postprocess" / aid / f"{pose['label']}_ocs.json"


if __name__ == "__main__":
    print("=== P4-PHYS-E config self-check ===")
    print(f"n_geometries={len(GEOMETRIES)}  n_poses={len(POSES)}  combos={len(GEOMETRIES)*len(POSES)}")
    for g in GEOMETRIES:
        print(f"  {g['geom_id']:14s} sun_off={g['sun_offset']:+d} view_off={g['view_offset']:+d} "
              f"d_sun={g['sun_ang_from_base']:.2f} d_det={g['det_ang_from_base']:.2f} "
              f"kind={g['kind']:12s} anchor26={g['anchor_26']}")
    # EXR 可达性核验（应全部存在；0 新增渲染）
    miss = 0; n_reuse_base = 0; n_reuse_26 = 0
    for g in GEOMETRIES:
        for pose in POSES:
            cam, cam_src, sun, sun_src = resolve_exr_pair(g, pose)
            for f, s in ((cam, cam_src), (sun, sun_src)):
                if not f.is_file():
                    print(f"  [MISSING] {g['geom_id']}/{pose['pose_id']} {s}: {f}"); miss += 1
                elif s == "REUSED_BASELINE":
                    n_reuse_base += 1
                else:
                    n_reuse_26 += 1
    print(f"EXR availability: {'ALL OK' if miss==0 else str(miss)+' MISSING'}  "
          f"(reuse_baseline={n_reuse_base}, reuse_26={n_reuse_26}, new_render=0)")

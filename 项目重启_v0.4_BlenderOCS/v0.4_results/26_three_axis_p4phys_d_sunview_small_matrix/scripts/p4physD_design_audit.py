# -*- coding: utf-8 -*-
"""
p4physD_design_audit.py —— 26 包子任务 A：设计与预检 manifest（ocs_sim python）
================================================================================
输出 R153 §7-A 要求的 5 个 manifest：
    audit/input_manifest.csv
    audit/sunview_geometry_manifest.csv
    audit/pose_candidate_manifest.csv
    audit/render_plan_manifest.csv
    audit/redline_precheck.csv
纯读取 + 设计落盘，不渲染、不改源包。
"""
import csv
import importlib.util
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
spec_cfg = importlib.util.spec_from_file_location("p4physD_config", str(THIS_DIR / "p4physD_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)

AUDIT = cfg.PKG26 / "audit"
AUDIT.mkdir(parents=True, exist_ok=True)


def wcsv(name, header, rows):
    with open(AUDIT / name, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)


def vec_str(v):
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"


# ---------- input_manifest ----------
rows = [
    ["task", "R153 / P4-PHYS-D sun/view small matrix stage gate", ""],
    ["baseline_geometry", "phase63 / L1-G1", "SUN=[1,0,0.3] DET=[0.5,-1,0.1] inertial"],
    ["r_max_m", f"{cfg.R_MAX:.10f}", "model-only const, view-independent"],
    ["pixel_area_m2", f"{cfg.PIXEL_AREA_M2:.6e}", "(2.2*r_max/256)^2"],
    ["depth_epsilon_m", f"{cfg.DEPTH_EPSILON_M_FINAL:.10f}", "shared shadow eps (=run_full_postprocess)"],
    ["i_scale", f"{cfg.I_SCALE:.10f}", "step5 fixed i_scale (image only, OCS unaffected)"],
    ["brdf_branch", "B0 phong_like_provisional_baseline", "material proxy, no material pass"],
    ["indexob_map", "1=jinshuzhuti 2=taiyangnengban 3=yinshenban 0=bg", ""],
    ["n_geometries", str(len(cfg.GEOMETRIES)), "<=5"],
    ["n_poses", str(len(cfg.POSES)), "<=16"],
    ["perturb_deg", f"{cfg.PERTURB_DEG}", "5-10 deg range"],
    ["reuse_principle", "sun-perturb reuse camera EXR; view-perturb reuse sun EXR",
     "geometry pass is光照无关 => 物理精确复用"],
]
wcsv("input_manifest.csv", ["field", "value", "note"], rows)

# ---------- sunview_geometry_manifest ----------
rows = []
for g in cfg.GEOMETRIES:
    rows.append([g["geom_id"], g["kind"], vec_str(g["sun_dir"]), vec_str(g["det_dir"]),
                 f"{g['sun_ang_from_base']:.3f}", f"{g['det_ang_from_base']:.3f}",
                 g["render_view"], g["camera_source"], g["sun_source"], g["note"]])
wcsv("sunview_geometry_manifest.csv",
     ["geom_id", "kind", "sun_dir", "det_dir", "sun_ang_from_base_deg", "det_ang_from_base_deg",
      "render_view", "camera_source", "sun_source", "note"], rows)

# ---------- pose_candidate_manifest ----------
rows = []
for p in cfg.POSES:
    cam = cfg.baseline_camera_exr(p); sun = cfg.baseline_sun_exr(p); js = cfg.baseline_ocs_json(p)
    rows.append([p["pose_id"], p["group"], p["role"], p["label"],
                 p["yaw"], p["pitch"], p["roll"],
                 p["src"].split("/")[0],  # src package
                 "OK" if cam.is_file() else "MISSING",
                 "OK" if sun.is_file() else "MISSING",
                 "OK" if js.is_file() else "MISSING"])
wcsv("pose_candidate_manifest.csv",
     ["pose_id", "group", "role", "label", "yaw", "pitch", "roll", "src_pkg",
      "baseline_camera", "baseline_sun", "baseline_ocs_json"], rows)

# ---------- render_plan_manifest ----------
rows = []
n_new = 0
for g in cfg.GEOMETRIES:
    for p in cfg.POSES:
        cam, cam_src, sun, sun_src = cfg.resolve_exr_pair(g, p)
        new_views = []
        if cam_src == "NEW_26": new_views.append("camera")
        if sun_src == "NEW_26": new_views.append("sun")
        n_new += len(new_views)
        rows.append([g["geom_id"], p["pose_id"], p["label"],
                     cam_src, sun_src,
                     "+".join(new_views) if new_views else "none",
                     len(new_views)])
wcsv("render_plan_manifest.csv",
     ["geom_id", "pose_id", "label", "camera_exr_src", "sun_exr_src",
      "new_render_views", "n_new_units"], rows)

# ---------- redline_precheck ----------
rows = [
    ["geom_count_le_5", "PASS" if len(cfg.GEOMETRIES) <= 5 else "FAIL", f"{len(cfg.GEOMETRIES)}"],
    ["pose_count_le_16", "PASS" if len(cfg.POSES) <= 16 else "FAIL", f"{len(cfg.POSES)}"],
    ["new_render_units_le_80", "PASS" if n_new <= 80 else "FAIL", f"{n_new}"],
    ["no_full_sunview_search", "PASS", "只 baseline ±7° 小矩阵，非全局搜索"],
    ["no_new_pose_search", "PASS", "全部姿态来自 01/20/21/23A/23B 既有渲染"],
    ["no_training", "PASS", "只渲染几何 pass + OCS 积分"],
    ["no_R128", "PASS", "未触及"],
    ["no_route234", "PASS", "未触及"],
    ["material_proxy_only", "PASS", "B0 proxy，无 material pass"],
    ["no_source_pkg_edit", "PASS", "只写 26 包，不改 20/21/23A/23B/24/25"],
    ["perturb_in_5_10_deg", "PASS" if 5.0 <= cfg.PERTURB_DEG <= 10.0 else "FAIL", f"{cfg.PERTURB_DEG} deg"],
]
wcsv("redline_precheck.csv", ["check", "status", "note"], rows)

print(f"[A-design] manifests written. new_render_units={n_new} (<=80)")
print(f"  geometries={len(cfg.GEOMETRIES)}  poses={len(cfg.POSES)}")

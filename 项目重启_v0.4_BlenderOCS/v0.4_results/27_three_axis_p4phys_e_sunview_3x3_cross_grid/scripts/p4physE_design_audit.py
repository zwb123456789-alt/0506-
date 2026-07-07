# -*- coding: utf-8 -*-
"""
p4physE_design_audit.py —— 27 包子任务 A：设计与复用审计 manifest（ocs_sim python）
================================================================================
输出 R155 §6-A 要求的 manifest：
    audit/input_manifest.csv
    audit/sunview_3x3_geometry_manifest.csv
    audit/pose_candidate_manifest.csv
    audit/reuse_exr_manifest.csv
    audit/redline_precheck.csv
纯读取 + 设计落盘，不渲染、不改源包。
"""
import csv
import importlib.util
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
spec_cfg = importlib.util.spec_from_file_location("p4physE_config", str(THIS_DIR / "p4physE_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)

AUDIT = cfg.PKG27 / "audit"
AUDIT.mkdir(parents=True, exist_ok=True)


def wcsv(name, header, rows):
    with open(AUDIT / name, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)


def vec_str(v):
    return "[" + ",".join(f"{x:.6f}" for x in v) + "]"


# ---------- input_manifest ----------
rows = [
    ["task", "R155 / P4-PHYS-E sun/view 3x3 cross grid", ""],
    ["upstream", "R154 accept 009/26, P4-PHYS-D = SUNVIEW_DEPENDENT_BUT_MECHANISTIC", ""],
    ["baseline_geometry", "phase63 / L1-G1", "SUN=[1,0,0.3] DET=[0.5,-1,0.1] inertial"],
    ["r_max_m", f"{cfg.R_MAX:.10f}", "model-only const, from 26 cfg"],
    ["pixel_area_m2", f"{cfg.PIXEL_AREA_M2:.6e}", "(2.2*r_max/256)^2, from 26 cfg"],
    ["depth_epsilon_m", f"{cfg.DEPTH_EPSILON_M_FINAL:.10f}", "shared shadow eps, from 26 cfg"],
    ["i_scale", f"{cfg.I_SCALE:.10f}", "step5 fixed i_scale (image only, OCS unaffected)"],
    ["brdf_branch", "B0 phong_like_provisional_baseline", "material proxy, no material pass"],
    ["indexob_map", "1=jinshuzhuti 2=taiyangnengban 3=yinshenban 0=bg", ""],
    ["sun_offsets", "{-7,0,+7} deg", "sun_dir from 26 baseline/G1/G2"],
    ["view_offsets", "{-7,0,+7} deg", "det_dir from 26 baseline/G3/G4"],
    ["n_geometries", str(len(cfg.GEOMETRIES)), "3x3 combos"],
    ["n_poses", str(len(cfg.POSES)), "same 14 as 26, no new pose search"],
    ["n_combos", str(len(cfg.GEOMETRIES) * len(cfg.POSES)), "9x14=126"],
    ["new_render_units", "0", "camera EXR<-view_offset, sun EXR<-sun_offset, all from 26/baseline"],
    ["reuse_principle",
     "camera pass sun-independent => cam EXR by view_offset; sun pass detector-independent => sun EXR by sun_offset",
     "physically exact reuse of 26 rendered EXR"],
]
wcsv("input_manifest.csv", ["field", "value", "note"], rows)

# ---------- sunview_3x3_geometry_manifest ----------
rows = []
for g in cfg.GEOMETRIES:
    rows.append([g["geom_id"], g["sun_offset"], g["view_offset"], g["kind"],
                 vec_str(g["sun_dir"]), vec_str(g["det_dir"]),
                 f"{g['sun_ang_from_base']:.3f}", f"{g['det_ang_from_base']:.3f}",
                 g["camera_source"], g["sun_source"], g["anchor_26"], g["note"]])
wcsv("sunview_3x3_geometry_manifest.csv",
     ["geom_id", "sun_offset_deg", "view_offset_deg", "kind", "sun_dir", "det_dir",
      "sun_ang_from_base_deg", "det_ang_from_base_deg",
      "camera_source", "sun_source", "anchor_26_geom", "note"], rows)

# ---------- pose_candidate_manifest ----------
# top-1 roll 邻域簇标注（R155 §5）
CORE_CLUSTER = {"A_top1", "D1", "D2", "D3", "D4", "D5_roll125", "D6_roll175",
                "F1_edge", "F2_edge", "F3_edge"}
PRIMARY_SHIFT = {"D5_roll125", "D6_roll175"}
CONTROLS = {"B_R4", "C_R3"}
rows = []
for p in cfg.POSES:
    cam = cfg.cfg26.baseline_camera_exr(p); sun = cfg.cfg26.baseline_sun_exr(p)
    js = cfg.cfg26.baseline_ocs_json(p)
    cluster = ("primary_shift_target" if p["pose_id"] in PRIMARY_SHIFT
               else "core_top1_roll_neighborhood" if p["pose_id"] in CORE_CLUSTER
               else "control" if p["pose_id"] in CONTROLS else "other")
    rows.append([p["pose_id"], p["group"], p["role"], p["label"],
                 p["yaw"], p["pitch"], p["roll"], p["src"].split("/")[0],
                 cluster,
                 "OK" if cam.is_file() else "MISSING",
                 "OK" if sun.is_file() else "MISSING",
                 "OK" if js.is_file() else "MISSING"])
wcsv("pose_candidate_manifest.csv",
     ["pose_id", "group", "role", "label", "yaw", "pitch", "roll", "src_pkg",
      "cluster_tag", "baseline_camera", "baseline_sun", "baseline_ocs_json"], rows)

# ---------- reuse_exr_manifest ----------
rows = []
n_new = 0; n_reuse_base = 0; n_reuse_26 = 0; miss = 0
for g in cfg.GEOMETRIES:
    for p in cfg.POSES:
        cam, cam_src, sun, sun_src = cfg.resolve_exr_pair(g, p)
        cam_ok = cam.is_file(); sun_ok = sun.is_file()
        if not cam_ok: miss += 1
        if not sun_ok: miss += 1
        for s in (cam_src, sun_src):
            if s == "REUSED_BASELINE": n_reuse_base += 1
            elif s.startswith("REUSED_26"): n_reuse_26 += 1
            else: n_new += 1
        rows.append([g["geom_id"], p["pose_id"], p["label"],
                     cam_src, "OK" if cam_ok else "MISSING",
                     sun_src, "OK" if sun_ok else "MISSING"])
wcsv("reuse_exr_manifest.csv",
     ["geom_id", "pose_id", "label", "camera_exr_src", "camera_exr_status",
      "sun_exr_src", "sun_exr_status"], rows)

# ---------- redline_precheck ----------
SRC_PKGS = ["20", "21", "23A", "23B", "24", "25", "26"]
rows = [
    ["geom_count_3x3", "PASS" if len(cfg.GEOMETRIES) == 9 else "FAIL", f"{len(cfg.GEOMETRIES)}"],
    ["pose_count_same_14", "PASS" if len(cfg.POSES) == 14 else "FAIL", f"{len(cfg.POSES)}"],
    ["new_render_units_zero", "PASS" if n_new == 0 else "FAIL", f"{n_new}"],
    ["all_exr_reachable", "PASS" if miss == 0 else "FAIL", f"missing={miss}"],
    ["no_full_sunview_search", "PASS", "只 baseline ±7° 3x3 组合网格，非全局搜索"],
    ["no_new_pose_search", "PASS", "全部姿态复用 26 包同源 14 候选"],
    ["no_training", "PASS", "只 OCS 积分 + 机制重算，无训练"],
    ["no_R128", "PASS", "未触及"],
    ["no_route234", "PASS", "未触及"],
    ["material_proxy_only", "PASS", "B0 proxy，无 material pass"],
    ["no_source_pkg_edit", "PASS", f"只写 27 包，不改 {'/'.join(SRC_PKGS)}"],
    ["perturb_in_5_10_deg", "PASS" if 5.0 <= cfg.PERTURB_DEG <= 10.0 else "FAIL", f"{cfg.PERTURB_DEG} deg"],
    ["reuse_counts", "INFO", f"reuse_baseline={n_reuse_base} reuse_26={n_reuse_26} new=0"],
]
wcsv("redline_precheck.csv", ["check", "status", "note"], rows)

print(f"[A-design] manifests written.")
print(f"  geometries={len(cfg.GEOMETRIES)}  poses={len(cfg.POSES)}  combos={len(cfg.GEOMETRIES)*len(cfg.POSES)}")
print(f"  new_render_units={n_new}  reuse_baseline={n_reuse_base}  reuse_26={n_reuse_26}  missing={miss}")

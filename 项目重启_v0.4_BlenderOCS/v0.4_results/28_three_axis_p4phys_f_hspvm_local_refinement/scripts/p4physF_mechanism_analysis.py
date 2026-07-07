# -*- coding: utf-8 -*-
"""
p4physF_mechanism_analysis.py —— 28 包机制分析（ocs_sim python 运行）
================================================================================
R157 §7。复用 24/25/26/27 机制签名口径（阈值原样沿用 25 包），并按 R157 追加
几何因子诊断：weighted_NoL / weighted_NoV / weighted_NoL_NoV（金属贡献像素 I 加权）。

覆盖组合：Stage1（27 姿态 @ sp7_vm7）∪ Stage2（6 姿态 × 9 组合几何），去重后 75 组合。

输出：
    tables/p4physF_mechanism_signature.csv
    tables/p4physF_control_boundary_table.csv
    audit/numeric_consistency_check.csv
"""
import sys
import csv
import json
import importlib.util
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
V04_ROOT = THIS_DIR.parents[2]
CODE_VALID = V04_ROOT / "06_v0.4_code" / "10_validation"
CODE_CONFIG = V04_ROOT / "06_v0.4_code" / "00_config"
for p in (str(CODE_VALID), str(CODE_CONFIG)):
    if p not in sys.path:
        sys.path.insert(0, p)

from validate_shadow_consistency_fixed import read_position_pass, read_depth_pass, BLENDER_FAR_PLANE
from validate_v_sun_macro_on_image import read_normal_pass, read_indexob_pass
from materials_v0_4 import get_material_b0, brdf_b0_phong_like

spec_cfg = importlib.util.spec_from_file_location("p4physF_config", str(THIS_DIR / "p4physF_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)

# 25 包机制判据阈值（原样沿用）
NSM_METAL_PCT = 80.0
NSM_AVGN_H_DEG = 2.0
NSM_REFLECT_DET_DEG = 4.0
SSH_PCT_NOH = 50.0
SSH_MEAN_NOH_N = 0.5
DPI_DARK_CONTRIB = 0.004
DPI_DARK_PCT = 2.0
PHONG_N = cfg.PHONG_N


def angle_deg(a, b):
    a = np.asarray(a, float); a = a / np.linalg.norm(a)
    b = np.asarray(b, float); b = b / np.linalg.norm(b)
    return float(np.degrees(np.arccos(np.clip(a @ b, -1.0, 1.0))))


def analyze(cam_exr, sun_exr, sun_dir, det_dir, vsun_path):
    sun_dir = np.asarray(sun_dir, float); sun_dir = sun_dir / np.linalg.norm(sun_dir)
    det_dir = np.asarray(det_dir, float); det_dir = det_dir / np.linalg.norm(det_dir)
    Hspec = sun_dir + det_dir; Hspec = Hspec / np.linalg.norm(Hspec)

    position = read_position_pass(cam_exr)
    depth = read_depth_pass(cam_exr)
    normal = read_normal_pass(cam_exr)
    indexob = np.round(read_indexob_pass(cam_exr)).astype(int)

    H, W = depth.shape
    r_cam = np.linalg.norm(position, axis=-1)
    foreground = (depth < BLENDER_FAR_PLANE) & (r_cam > 0)

    NoL = np.zeros((H, W)); NoV = np.zeros((H, W))
    fg = np.where(foreground)
    n_fg = normal[fg]
    NoL[fg] = np.maximum(n_fg @ sun_dir, 0.0)
    NoV[fg] = np.maximum(n_fg @ det_dir, 0.0)
    valid = foreground & (NoV > cfg.NOV_EPS) & (NoL > cfg.NOL_EPS)

    fr = np.zeros((H, W))
    vi = np.where(valid)
    idx_v = indexob[vi]; normals_v = normal[vi]
    fr_v = np.zeros(len(idx_v))
    for pid in np.unique(idx_v):
        name = cfg.INDEXOB_TO_PART.get(int(pid))
        mat = get_material_b0(name) if name else get_material_b0("__fallback__")
        sel = idx_v == pid
        fr_v[sel] = brdf_b0_phong_like(normals_v[sel], sun_dir, det_dir, mat)
    fr[vi] = fr_v

    V = np.load(str(vsun_path)).astype(np.float64)
    I = np.zeros_like(fr)
    I[valid] = fr[valid] * NoL[valid] * V[valid]
    contributing = valid & (V == 1)

    per_part = {}
    for pid, name in cfg.INDEXOB_TO_PART.items():
        m = (indexob == pid) & contributing
        per_part[name] = float(cfg.PIXEL_AREA_M2 * I[m].sum())
    ocs_total = float(cfg.PIXEL_AREA_M2 * I[contributing].sum())
    metal = per_part["jinshuzhuti"]; dark = per_part["yinshenban"]
    metal_pct = 100.0 * metal / ocs_total if ocs_total > 0 else 0.0
    dark_pct = 100.0 * dark / ocs_total if ocs_total > 0 else 0.0

    mm = (indexob == 1) & contributing
    out = dict(ocs_total=ocs_total, metal=metal, dark=dark,
               metal_pct=metal_pct, dark_pct=dark_pct, n_metal_px=int(mm.sum()),
               dominant_part=max(per_part, key=per_part.get) if ocs_total > 0 else "none")
    if mm.sum() > 0:
        w_ = I[mm]; n_m = normal[mm]
        navg = (n_m * w_[:, None]).sum(0); navg = navg / (np.linalg.norm(navg) + 1e-12)
        NoH = np.clip(n_m @ Hspec, 0, 1)
        refl = 2 * np.dot(navg, sun_dir) * navg - sun_dir
        refl = refl / (np.linalg.norm(refl) + 1e-12)
        NoL_m = NoL[mm]; NoV_m = NoV[mm]
        out.update(
            avgN_vs_H_deg=angle_deg(navg, Hspec),
            reflect_vs_det_deg=angle_deg(refl, det_dir),
            pct_NoH_ge_099=float((NoH >= 0.99).mean() * 100.0),
            mean_NoH_pow_n=float((NoH ** PHONG_N).mean()),
            weighted_NoL=float(np.average(NoL_m, weights=w_)),
            weighted_NoV=float(np.average(NoV_m, weights=w_)),
            weighted_NoL_NoV=float(np.average(NoL_m * NoV_m, weights=w_)),
        )
    else:
        out.update(avgN_vs_H_deg=180.0, reflect_vs_det_deg=180.0,
                   pct_NoH_ge_099=0.0, mean_NoH_pow_n=0.0,
                   weighted_NoL=0.0, weighted_NoV=0.0, weighted_NoL_NoV=0.0)

    nsm = int(out["metal_pct"] >= NSM_METAL_PCT and out["avgN_vs_H_deg"] <= NSM_AVGN_H_DEG
              and out["reflect_vs_det_deg"] <= NSM_REFLECT_DET_DEG)
    ssh = int(out["pct_NoH_ge_099"] >= SSH_PCT_NOH or out["mean_NoH_pow_n"] >= SSH_MEAN_NOH_N)
    dpi = int(out["dark"] >= DPI_DARK_CONTRIB or out["dark_pct"] >= DPI_DARK_PCT)
    out.update(near_specular_metal=nsm, strong_surface_highlight=ssh, dark_panel_increment=dpi)
    return out


def enumerate_combos():
    """Stage1 ∪ Stage2 组合，去重 (geom_id, label)。"""
    combos = {}
    for p in cfg.STAGEB_POSES:
        combos[("sp7_vm7", p["label"])] = (p, 7, -7)
    with open(cfg.STAGEC_POSES_JSON, encoding="utf-8") as f:
        stagec = json.load(f)["poses"]
    for p in stagec:
        for g in cfg.GEOMETRIES_C:
            key = (g["geom_id"], p["label"])
            if key not in combos:
                combos[key] = (p, g["sun_offset"], g["view_offset"])
    return combos


def main():
    combos = enumerate_combos()
    print(f"[F-analysis] combos={len(combos)}")

    sig_rows, consist_rows = [], []
    all_recs = []
    for (gid, label), (pose, so, vo) in sorted(combos.items()):
        cam, _ = cfg.camera_exr(label, pose.get("is_new", False), vo)
        sun, _ = cfg.sun_exr(label, pose.get("is_new", False), so)
        vsun = cfg.POST_BASE / gid / f"{label}_v_sun_macro.npy"
        ocs_json = cfg.POST_BASE / gid / f"{label}_ocs.json"
        s = analyze(str(cam), str(sun), cfg.SUN_DIR[so], cfg.DET_DIR[vo], vsun)
        with open(ocs_json, encoding="utf-8") as f:
            ref = json.load(f)
        ref_tot = float(ref["ocs_total"])
        rel = abs(s["ocs_total"] - ref_tot) / max(ref_tot, 1e-12)
        consist_rows.append([gid, pose["pose_id"], label, f"{s['ocs_total']:.10f}",
                             f"{ref_tot:.10f}", f"{rel:.3e}", "OK" if rel < 1e-4 else "MISMATCH"])
        rec = dict(s, geom_id=gid, sun_offset=so, view_offset=vo,
                   pose_id=pose["pose_id"], label=label,
                   yaw=pose["yaw"], pitch=pose["pitch"], roll=pose["roll"])
        all_recs.append(rec)
        sig_rows.append([gid, so, vo, pose["pose_id"], label,
                         pose["yaw"], pose["pitch"], pose["roll"],
                         f"{s['ocs_total']:.8f}", s["dominant_part"],
                         f"{s['metal_pct']:.2f}", f"{s['dark_pct']:.3f}",
                         f"{s['avgN_vs_H_deg']:.3f}", f"{s['reflect_vs_det_deg']:.3f}",
                         f"{s['pct_NoH_ge_099']:.2f}", f"{s['mean_NoH_pow_n']:.4e}",
                         f"{s['weighted_NoL']:.4f}", f"{s['weighted_NoV']:.4f}",
                         f"{s['weighted_NoL_NoV']:.4f}",
                         s["near_specular_metal"], s["strong_surface_highlight"],
                         s["dark_panel_increment"]])

    T = cfg.PKG28 / "tables"
    with open(T / "p4physF_mechanism_signature.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["geom_id", "sun_offset", "view_offset", "pose_id", "label",
                     "yaw", "pitch", "roll", "ocs_total", "dominant_part",
                     "metal_pct", "dark_pct", "avgN_vs_H_deg", "reflect_vs_det_deg",
                     "pct_NoH_ge_0.99", "mean_NoH_pow_n",
                     "weighted_NoL", "weighted_NoV", "weighted_NoL_NoV",
                     "near_specular_metal", "strong_surface_highlight", "dark_panel_increment"])
        wr.writerows(sig_rows)

    with open(cfg.PKG28 / "audit" / "numeric_consistency_check.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["geom_id", "pose_id", "label", "recomputed_ocs_total", "ref_ocs_total",
                     "rel_diff", "verdict"])
        wr.writerows(consist_rows)

    # ---- control boundary table：6 个 Stage C 姿态 × 9 几何的对照状态 ----
    with open(cfg.STAGEC_POSES_JSON, encoding="utf-8") as f:
        stagec = json.load(f)["poses"]
    by_key = {(r["geom_id"], r["label"]): r for r in all_recs}
    geom_order = [g["geom_id"] for g in cfg.GEOMETRIES_C]
    ctrl_rows = []
    for g in geom_order:
        recs_g = [by_key[(g, p["label"])] for p in stagec]
        recs_g.sort(key=lambda r: -r["ocs_total"])
        rankmap = {r["label"]: i + 1 for i, r in enumerate(recs_g)}
        for p in stagec:
            r = by_key[(g, p["label"])]
            ctrl_rows.append([g, r["sun_offset"], r["view_offset"], p["pose_id"], p["label"],
                              f"{r['ocs_total']:.8f}", rankmap[p["label"]],
                              f"{r['metal_pct']:.2f}", r["near_specular_metal"],
                              f"{r['weighted_NoL_NoV']:.4f}",
                              f"{r['avgN_vs_H_deg']:.2f}", f"{r['reflect_vs_det_deg']:.2f}"])
    with open(T / "p4physF_control_boundary_table.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["geom_id", "sun_offset", "view_offset", "pose_id", "label", "ocs_total",
                     "rank_in_geom", "metal_pct", "near_specular_metal",
                     "weighted_NoL_NoV", "avgN_vs_H_deg", "reflect_vs_det_deg"])
        wr.writerows(ctrl_rows)

    n_ok = sum(1 for c in consist_rows if c[-1] == "OK")
    max_rel = max(float(c[5]) for c in consist_rows)
    print(f"[F-analysis] DONE consistency={n_ok}/{len(consist_rows)} max_rel={max_rel:.2e}")

    # 关键点摘要
    best = max(all_recs, key=lambda r: r["ocs_total"])
    print(f"  GLOBAL_BEST: {best['geom_id']} / {best['pose_id']} OCS={best['ocs_total']:.8f} "
          f"nsm={best['near_specular_metal']} metal_pct={best['metal_pct']:.1f} "
          f"wNoLNoV={best['weighted_NoL_NoV']:.4f} avgNH={best['avgN_vs_H_deg']:.2f}deg "
          f"refl_det={best['reflect_vs_det_deg']:.2f}deg")
    for key in [("sp7_vm7", cfg.C_R3_LABEL)]:
        r = by_key.get(key)
        if r:
            print(f"  C_R3@center: OCS={r['ocs_total']:.6f} nsm={r['near_specular_metal']} "
                  f"metal_pct={r['metal_pct']:.1f} wNoLNoV={r['weighted_NoL_NoV']:.4f} "
                  f"avgNH={r['avgN_vs_H_deg']:.2f} refl={r['reflect_vs_det_deg']:.2f}")
    return 0 if n_ok == len(consist_rows) else 1


if __name__ == "__main__":
    sys.exit(main())

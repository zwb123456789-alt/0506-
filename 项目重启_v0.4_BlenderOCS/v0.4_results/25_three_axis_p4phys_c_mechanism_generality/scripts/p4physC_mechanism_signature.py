# -*- coding: utf-8 -*-
"""
p4physC_mechanism_signature.py —— P4-PHYS-C 子任务 B：机制签名批量计算
================================================================================
R151 任务单执行脚本（第 2 步）。复用 24 包（p4physB_light_path_attribution.py）
的官方口径，对候选池每个候选计算机制签名。不重渲染、不改 24 包。

每个候选（从 audit/candidate_pool_manifest.csv 读取三文件路径）计算：
    ocs_total（逐像素重算，与 ocs.json 一致性核验）
    dominant_part / metal_body / dark_panel / solar_panel per-part OCS 与占比
    weighted_metal_NH / avgN_vs_H_deg / reflect_vs_det_deg
    pct_NoH_ge_0.99 / mean_NoH_pow_n_metal
    saturation_flag / glint_flag（若可从 metrics 表读到）
"""

import os
import sys
import csv
import json
import numpy as np
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PKG25    = THIS_DIR.parent
V04_ROOT = THIS_DIR.parents[2]
RESULTS  = V04_ROOT / "v0.4_results"
CODE     = V04_ROOT / "06_v0.4_code"

sys.path.insert(0, str(CODE / "10_validation"))
sys.path.insert(0, str(CODE / "00_config"))

from validate_shadow_consistency_fixed import (
    read_position_pass, read_depth_pass, BLENDER_FAR_PLANE,
)
from validate_v_sun_macro_on_image import read_normal_pass, read_indexob_pass
from materials_v0_4 import get_material_b0, brdf_b0_phong_like

# ---- 冻结常量（与 24 包一致） ----
SUN_VECTOR = np.array([1.0, 0.0, 0.3])
DET_VECTOR = np.array([0.5, -1.0, 0.1])
SUN_DIR = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
DET_DIR = DET_VECTOR / np.linalg.norm(DET_VECTOR)
HSPEC = (SUN_DIR + DET_DIR) / np.linalg.norm(SUN_DIR + DET_DIR)

R_MAX = 1.4726051706213208
PIXEL_AREA_M2 = (2.2 * R_MAX / 256) ** 2
NOL_EPS = 1e-6
NOV_EPS = 1e-6
PHONG_N = 80  # B0 metal

INDEXOB_TO_PART = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}

OUT = {k: PKG25 / k for k in ("audit", "tables", "figures", "text", "logs")}


def angle_deg(a, b):
    return float(np.degrees(np.arccos(np.clip(np.dot(a, b), -1.0, 1.0))))


def compute_signature(exr, vsun, ocs_json):
    """复用 24 包 load_pose + ocs_breakdown + 几何分析，返回 signature dict。"""
    position = read_position_pass(exr)
    depth    = read_depth_pass(exr)
    normal   = read_normal_pass(exr)
    indexob  = np.round(read_indexob_pass(exr)).astype(int)
    V        = np.load(vsun).astype(np.float64)

    H, W = depth.shape
    r_cam = np.linalg.norm(position, axis=-1)
    foreground = (depth < BLENDER_FAR_PLANE) & (r_cam > 0)

    NoL = np.zeros((H, W)); NoV = np.zeros((H, W))
    fg = np.where(foreground)
    n_fg = normal[fg]
    NoL[fg] = np.maximum(n_fg @ SUN_DIR, 0.0)
    NoV[fg] = np.maximum(n_fg @ DET_DIR, 0.0)
    valid = foreground & (NoV > NOV_EPS) & (NoL > NOL_EPS)

    fr = np.zeros((H, W))
    vi = np.where(valid)
    idx_v = indexob[vi]; normals_v = normal[vi]
    fr_v = np.zeros(len(idx_v))
    for pid in np.unique(idx_v):
        name = INDEXOB_TO_PART.get(int(pid))
        mat = get_material_b0(name) if name else get_material_b0("__fallback__")
        sel = idx_v == pid
        fr_v[sel] = brdf_b0_phong_like(normals_v[sel], SUN_DIR, DET_DIR, mat)
    fr[vi] = fr_v

    I_linear = np.zeros((H, W))
    I_linear[valid] = fr[valid] * NoL[valid] * V[valid]
    contributing = valid & (V == 1)

    # per-part
    per_part, npix_part = {}, {}
    for pid, name in INDEXOB_TO_PART.items():
        m = (indexob == pid) & contributing
        per_part[name] = float(PIXEL_AREA_M2 * I_linear[m].sum())
        npix_part[name] = int(m.sum())
    ocs_total = float(PIXEL_AREA_M2 * I_linear[contributing].sum())

    dom = max(per_part, key=per_part.get) if ocs_total > 0 else "none"
    metal = per_part["jinshuzhuti"]; dark = per_part["yinshenban"]; solar = per_part["taiyangnengban"]
    metal_pct = 100.0 * metal / ocs_total if ocs_total > 0 else 0.0
    dark_pct = 100.0 * dark / ocs_total if ocs_total > 0 else 0.0
    solar_pct = 100.0 * solar / ocs_total if ocs_total > 0 else 0.0

    # 金属主体贡献像素的几何签名（I_linear 加权）
    mm = (indexob == 1) & contributing
    sig = dict(ocs_total=ocs_total, dominant_part=dom,
               metal_body=metal, dark_panel=dark, solar_panel=solar,
               metal_pct=metal_pct, dark_pct=dark_pct, solar_pct=solar_pct,
               n_metal_px=int(mm.sum()))
    if mm.sum() > 0:
        w_ = I_linear[mm]; n_m = normal[mm]
        navg = (n_m * w_[:, None]).sum(0)
        navg = navg / (np.linalg.norm(navg) + 1e-12)
        NoH = np.clip(n_m @ HSPEC, 0, 1)
        refl = 2 * np.dot(navg, SUN_DIR) * navg - SUN_DIR
        refl = refl / (np.linalg.norm(refl) + 1e-12)
        sig.update(
            weighted_metal_NH=float(np.average(NoH, weights=w_)),
            avgN_vs_H_deg=angle_deg(navg, HSPEC),
            avgN_vs_sun_deg=angle_deg(navg, SUN_DIR),
            avgN_vs_det_deg=angle_deg(navg, DET_DIR),
            reflect_vs_det_deg=angle_deg(refl, DET_DIR),
            pct_NoH_ge_0_99=float((NoH >= 0.99).mean() * 100.0),
            mean_NoH_pow_n_metal=float((NoH ** PHONG_N).mean()),
        )
    else:
        sig.update(weighted_metal_NH=0.0, avgN_vs_H_deg=180.0, avgN_vs_sun_deg=180.0,
                   avgN_vs_det_deg=180.0, reflect_vs_det_deg=180.0,
                   pct_NoH_ge_0_99=0.0, mean_NoH_pow_n_metal=0.0)

    # 一致性
    with open(ocs_json, encoding="utf-8") as f:
        ref = json.load(f)
    ref_tot = float(ref["ocs_total"])
    sig["json_ocs_total"] = ref_tot
    sig["ocs_rel_diff"] = abs(ocs_total - ref_tot) / max(ref_tot, 1e-12)
    return sig


def load_flags():
    """从 P2/P3 metrics + 23A topN 读取 glint/saturation flag，键为 pose_key。"""
    flags = {}

    def pk(y, p, r):
        return (round(float(y), 3), round(float(p), 3), round(float(r), 3))

    for f, cols in [
        (RESULTS / "21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv",
         ("yaw_deg", "pitch_deg", "roll")),
        (RESULTS / "20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv",
         ("yaw", "pitch", "roll")),
    ]:
        if f.is_file():
            with open(f, encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    try:
                        k = pk(row[cols[0]], row[cols[1]], row[cols[2]])
                        flags.setdefault(k, (row.get("glint_flag", ""), row.get("saturation_flag", "")))
                    except Exception:
                        continue
    f23a = RESULTS / "23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_refined_topN.csv"
    if f23a.is_file():
        with open(f23a, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    k = pk(row["yaw_deg"], row["pitch_deg"], row["roll"])
                    flags.setdefault(k, (row.get("glint_flag", ""), row.get("saturation_flag", "")))
                except Exception:
                    continue
    return flags


def main():
    manifest = OUT["audit"] / "candidate_pool_manifest.csv"
    rows = list(csv.DictReader(open(manifest, encoding="utf-8")))
    flags = load_flags()

    # 亮度排序
    pool = []
    for r in rows:
        pool.append(r)
    pool_sorted = sorted(pool, key=lambda x: -float(_ocs_from_json(V04_ROOT / x["json_rel"])))

    sig_rows, part_rows, geo_rows, consist_rows = [], [], [], []
    n_total = len(pool_sorted)
    for rank, r in enumerate(pool_sorted, 1):
        label = r["pose_label"]
        exr = str(V04_ROOT / r["exr_rel"])
        vsun = str(V04_ROOT / r["vsun_rel"])
        ocs_json = str(V04_ROOT / r["json_rel"])
        yaw, pitch, roll = float(r["yaw"]), float(r["pitch"]), float(r["roll"])
        s = compute_signature(exr, vsun, ocs_json)
        pkk = (round(yaw, 3), round(pitch, 3), round(roll, 3))
        gl, sat = flags.get(pkk, ("", ""))

        sig_rows.append([label, yaw, pitch, roll, f"{s['ocs_total']:.8f}", rank,
                         s["dominant_part"],
                         f"{s['metal_body']:.8f}", f"{s['dark_panel']:.8f}", f"{s['solar_panel']:.8f}",
                         f"{s['metal_pct']:.3f}", f"{s['dark_pct']:.3f}", f"{s['solar_pct']:.3f}",
                         f"{s['weighted_metal_NH']:.5f}", f"{s['avgN_vs_H_deg']:.3f}",
                         f"{s['reflect_vs_det_deg']:.3f}", f"{s['pct_NoH_ge_0_99']:.3f}",
                         f"{s['mean_NoH_pow_n_metal']:.5e}", gl, sat, r["src_pkg"]])
        part_rows.append([label, yaw, pitch, roll, f"{s['ocs_total']:.8f}",
                          s["n_metal_px"], f"{s['metal_body']:.8f}", f"{s['dark_panel']:.8f}",
                          f"{s['solar_panel']:.8f}", f"{s['metal_pct']:.3f}",
                          f"{s['dark_pct']:.3f}", f"{s['solar_pct']:.3f}"])
        geo_rows.append([label, yaw, pitch, roll, f"{s['ocs_total']:.8f}",
                         f"{s['avgN_vs_sun_deg']:.3f}", f"{s['avgN_vs_det_deg']:.3f}",
                         f"{s['avgN_vs_H_deg']:.3f}", f"{s['weighted_metal_NH']:.5f}",
                         f"{s['reflect_vs_det_deg']:.3f}", f"{s['pct_NoH_ge_0_99']:.3f}",
                         f"{s['mean_NoH_pow_n_metal']:.5e}"])
        consist_rows.append([label, f"{s['ocs_total']:.10f}", f"{s['json_ocs_total']:.10f}",
                             f"{s['ocs_rel_diff']:.3e}",
                             "OK" if s["ocs_rel_diff"] < 1e-4 else "MISMATCH"])
        if rank % 25 == 0:
            print(f"  ... {rank}/{n_total}")

    _wcsv(OUT["tables"] / "p4physC_mechanism_signature_table.csv",
          ["pose_label", "yaw", "pitch", "roll", "ocs_total", "ocs_rank", "dominant_part",
           "metal_body_contrib", "dark_panel_contrib", "solar_panel_contrib",
           "metal_body_pct", "dark_panel_pct", "solar_panel_pct",
           "weighted_metal_NH", "avgN_vs_H_deg", "reflect_vs_det_deg",
           "pct_NoH_ge_0.99", "mean_NoH_pow_n_metal", "glint_flag", "saturation_flag",
           "src_pkg"], sig_rows)
    _wcsv(OUT["tables"] / "p4physC_part_contribution_table.csv",
          ["pose_label", "yaw", "pitch", "roll", "ocs_total", "n_metal_px",
           "metal_body_contrib", "dark_panel_contrib", "solar_panel_contrib",
           "metal_body_pct", "dark_panel_pct", "solar_panel_pct"], part_rows)
    _wcsv(OUT["tables"] / "p4physC_geometry_signature_table.csv",
          ["pose_label", "yaw", "pitch", "roll", "ocs_total",
           "avgN_vs_sun_deg", "avgN_vs_det_deg", "avgN_vs_H_deg", "weighted_metal_NH",
           "reflect_vs_det_deg", "pct_NoH_ge_0.99", "mean_NoH_pow_n_metal"], geo_rows)

    # 抽样一致性检查（前5+中5+后5）
    idxs = list(range(min(5, n_total))) + \
           list(range(n_total // 2 - 2, n_total // 2 + 3)) + \
           list(range(max(0, n_total - 5), n_total))
    idxs = sorted(set(i for i in idxs if 0 <= i < n_total))
    sample_rows = [consist_rows[i] for i in idxs]
    _wcsv(OUT["audit"] / "numeric_consistency_sample_check.csv",
          ["pose_label", "recomputed_ocs_total", "json_ocs_total", "rel_diff", "verdict"],
          sample_rows)

    n_ok = sum(1 for c in consist_rows if c[-1] == "OK")
    max_rel = max(float(c[3]) for c in consist_rows)
    log = {"n_candidates": n_total, "n_consistency_ok": n_ok,
           "max_rel_diff": max_rel, "phong_n": PHONG_N}
    with open(OUT["logs"] / "p4physC_signature_log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"[p4physC signature] DONE  n={n_total}  consistency_ok={n_ok}/{n_total}  max_rel_diff={max_rel:.2e}")


def _ocs_from_json(p):
    try:
        with open(p, encoding="utf-8") as f:
            return float(json.load(f)["ocs_total"])
    except Exception:
        return 0.0


def _wcsv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(rows)


if __name__ == "__main__":
    main()

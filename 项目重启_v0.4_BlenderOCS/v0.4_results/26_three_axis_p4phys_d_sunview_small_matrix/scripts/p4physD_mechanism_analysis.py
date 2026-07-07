# -*- coding: utf-8 -*-
"""
p4physD_mechanism_analysis.py —— 26 包子任务 D：跨几何 top-1 与机制迁移分析
================================================================================
复用 24/25 包机制签名算法（逐像素 I 加权代表法向 → avgN_vs_H / reflect_vs_det /
pct_NoH>=0.99 / mean_NoH^n / metal_pct），但把 SUN/DET/H 改为"每几何"取值，
因为半程向量 H=(S+D)/|S+D| 随 sun/view 改变。

对每个 (geometry, pose)：
    - 解析该几何应使用的 camera/sun EXR（baseline 复用或 26 新渲染）
    - 用该几何 sun_dir/det_dir 重算像素级 I_linear、OCS、机制签名
    - 用与 25 包同口径的三判据打机制标签（near_specular_metal 等），
      阈值沿用 25 包：metal_pct>=80 且 avgN_vs_H<=2° 且 reflect_vs_det<=4°。

输出：
    tables/p4physD_cross_geometry_rank_table.csv
    tables/p4physD_top1_stability_table.csv
    tables/p4physD_mechanism_signature_by_geometry.csv
    audit/numeric_consistency_check.csv
    text/p4physD_sunview_stability_result.md（正文结论，另由报告引用）
"""
import csv
import json
import importlib.util
from pathlib import Path
from collections import defaultdict

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
V04_ROOT = THIS_DIR.parents[2]
CODE_VALID = V04_ROOT / "06_v0.4_code" / "10_validation"
CODE_CONFIG = V04_ROOT / "06_v0.4_code" / "00_config"
import sys
for p in (str(CODE_VALID), str(CODE_CONFIG)):
    if p not in sys.path:
        sys.path.insert(0, p)

from validate_shadow_consistency_fixed import read_position_pass, read_depth_pass, BLENDER_FAR_PLANE
from validate_v_sun_macro_on_image import read_normal_pass, read_indexob_pass
from materials_v0_4 import get_material_b0, brdf_b0_phong_like

spec_cfg = importlib.util.spec_from_file_location("p4physD_config", str(THIS_DIR / "p4physD_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)

# 25 包机制判据阈值（原样沿用，非本轮重定制）
NSM_METAL_PCT = 80.0
NSM_AVGN_H_DEG = 2.0
NSM_REFLECT_DET_DEG = 4.0
SSH_PCT_NOH = 50.0        # pct_NoH>=0.99 的百分比阈值
SSH_MEAN_NOH_N = 0.5      # mean_NoH^80 阈值
DPI_DARK_CONTRIB = 0.004
DPI_DARK_PCT = 2.0
PHONG_N = cfg.PHONG_N


def angle_deg(a, b):
    a = np.asarray(a, float); a = a / np.linalg.norm(a)
    b = np.asarray(b, float); b = b / np.linalg.norm(b)
    return float(np.degrees(np.arccos(np.clip(a @ b, -1.0, 1.0))))


def signature(cam_exr, sun_exr, sun_dir, det_dir):
    """逐像素重算 OCS + 机制签名（几何相关 H）。返回 dict。"""
    sun_dir = np.asarray(sun_dir, float); sun_dir = sun_dir / np.linalg.norm(sun_dir)
    det_dir = np.asarray(det_dir, float); det_dir = det_dir / np.linalg.norm(det_dir)
    Hspec = sun_dir + det_dir; Hspec = Hspec / np.linalg.norm(Hspec)

    position = read_position_pass(cam_exr)
    depth = read_depth_pass(cam_exr)
    normal = read_normal_pass(cam_exr)
    indexob = np.round(read_indexob_pass(cam_exr)).astype(int)

    # V_sun_macro：用 26/postprocess 已落盘（与 OCS 口径一致）
    H, W = depth.shape
    r_cam = np.linalg.norm(position, axis=-1)
    foreground = (depth < BLENDER_FAR_PLANE) & (r_cam > 0)

    # 直接读官方 compute_brdf_response 复现的 V_sun_macro（若无则重算 shadow）
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

    return dict(fr=fr, NoL=NoL, valid=valid, normal=normal, indexob=indexob,
                foreground=foreground, Hspec=Hspec, sun_dir=sun_dir, det_dir=det_dir)


def mechanism_from_ocsjson(base, sig):
    """结合 26/postprocess 已落盘的 V_sun_macro 与 ocs.json，算机制签名字段。"""
    V = np.load(str(base["vsun"])).astype(np.float64)
    fr = sig["fr"]; NoL = sig["NoL"]; valid = sig["valid"]
    idx = sig["indexob"]; normal = sig["normal"]; Hspec = sig["Hspec"]
    sun_dir = sig["sun_dir"]; det_dir = sig["det_dir"]

    I = np.zeros_like(fr)
    I[valid] = fr[valid] * NoL[valid] * V[valid]
    contributing = valid & (V == 1)

    per_part = {}
    for pid, name in cfg.INDEXOB_TO_PART.items():
        m = (idx == pid) & contributing
        per_part[name] = float(cfg.PIXEL_AREA_M2 * I[m].sum())
    ocs_total = float(cfg.PIXEL_AREA_M2 * I[contributing].sum())
    metal = per_part["jinshuzhuti"]; dark = per_part["yinshenban"]; solar = per_part["taiyangnengban"]
    metal_pct = 100.0 * metal / ocs_total if ocs_total > 0 else 0.0
    dark_pct = 100.0 * dark / ocs_total if ocs_total > 0 else 0.0

    mm = (idx == 1) & contributing
    sig_out = dict(ocs_total=ocs_total, metal=metal, dark=dark, solar=solar,
                   metal_pct=metal_pct, dark_pct=dark_pct, n_metal_px=int(mm.sum()),
                   dominant_part=max(per_part, key=per_part.get) if ocs_total > 0 else "none")
    if mm.sum() > 0:
        w_ = I[mm]; n_m = normal[mm]
        navg = (n_m * w_[:, None]).sum(0); navg = navg / (np.linalg.norm(navg) + 1e-12)
        NoH = np.clip(n_m @ Hspec, 0, 1)
        refl = 2 * np.dot(navg, sun_dir) * navg - sun_dir
        refl = refl / (np.linalg.norm(refl) + 1e-12)
        sig_out.update(
            avgN_vs_H_deg=angle_deg(navg, Hspec),
            reflect_vs_det_deg=angle_deg(refl, det_dir),
            weighted_metal_NH=float(np.average(NoH, weights=w_)),
            pct_NoH_ge_099=float((NoH >= 0.99).mean() * 100.0),
            mean_NoH_pow_n=float((NoH ** PHONG_N).mean()),
        )
    else:
        sig_out.update(avgN_vs_H_deg=180.0, reflect_vs_det_deg=180.0, weighted_metal_NH=0.0,
                       pct_NoH_ge_099=0.0, mean_NoH_pow_n=0.0)

    # 三判据（25 包口径）
    nsm = int(sig_out["metal_pct"] >= NSM_METAL_PCT and sig_out["avgN_vs_H_deg"] <= NSM_AVGN_H_DEG
              and sig_out["reflect_vs_det_deg"] <= NSM_REFLECT_DET_DEG)
    ssh = int(sig_out["pct_NoH_ge_099"] >= SSH_PCT_NOH or sig_out["mean_NoH_pow_n"] >= SSH_MEAN_NOH_N)
    dpi = int(sig_out["dark"] >= DPI_DARK_CONTRIB or sig_out["dark_pct"] >= DPI_DARK_PCT)
    sig_out.update(near_specular_metal=nsm, strong_surface_highlight=ssh, dark_panel_increment=dpi)
    return sig_out


def main():
    # 载 metrics 得到 OCS（与逐像素一致性核验用）
    metrics = {}
    for r in csv.DictReader(open(cfg.PKG26 / "tables" / "p4physD_metrics.csv", encoding="utf-8")):
        metrics[(r["geom_id"], r["pose_id"])] = r

    sig_rows, consist_rows = [], []
    data = defaultdict(dict)  # data[geom][pose] = sig_out

    for g in cfg.GEOMETRIES:
        for pose in cfg.POSES:
            cam, cam_src, sun, sun_src = cfg.resolve_exr_pair(g, pose)
            vsun = cfg.POST_BASE / g["geom_id"] / f"{pose['label']}_v_sun_macro.npy"
            sig = signature(str(cam), str(sun), g["sun_dir"], g["det_dir"])
            s = mechanism_from_ocsjson({"vsun": vsun}, sig)
            data[g["geom_id"]][pose["pose_id"]] = dict(s, role=pose["role"], group=pose["group"],
                                                       label=pose["label"], yaw=pose["yaw"],
                                                       pitch=pose["pitch"], roll=pose["roll"])
            # 一致性：逐像素 OCS vs metrics/ocs.json
            ref = float(metrics[(g["geom_id"], pose["pose_id"])]["ocs_total"])
            rel = abs(s["ocs_total"] - ref) / max(ref, 1e-12)
            consist_rows.append([g["geom_id"], pose["pose_id"], f"{s['ocs_total']:.10f}",
                                 f"{ref:.10f}", f"{rel:.3e}", "OK" if rel < 1e-4 else "MISMATCH"])
            sig_rows.append([g["geom_id"], pose["pose_id"], pose["role"], pose["group"], pose["label"],
                             f"{s['ocs_total']:.8f}", s["dominant_part"],
                             f"{s['metal_pct']:.2f}", f"{s['dark_pct']:.3f}",
                             f"{s['avgN_vs_H_deg']:.3f}", f"{s['reflect_vs_det_deg']:.3f}",
                             f"{s['pct_NoH_ge_099']:.2f}", f"{s['mean_NoH_pow_n']:.4e}",
                             s["near_specular_metal"], s["strong_surface_highlight"],
                             s["dark_panel_increment"]])

    T = cfg.PKG26 / "tables"
    with open(T / "p4physD_mechanism_signature_by_geometry.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["geom_id", "pose_id", "role", "group", "label", "ocs_total", "dominant_part",
                     "metal_pct", "dark_pct", "avgN_vs_H_deg", "reflect_vs_det_deg",
                     "pct_NoH_ge_0.99", "mean_NoH_pow_n", "near_specular_metal",
                     "strong_surface_highlight", "dark_panel_increment"])
        wr.writerows(sig_rows)

    with open(cfg.PKG26 / "audit" / "numeric_consistency_check.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["geom_id", "pose_id", "recomputed_ocs_total", "ref_ocs_total", "rel_diff", "verdict"])
        wr.writerows(consist_rows)

    # ---- cross_geometry_rank_table：每几何按 OCS 排名 ----
    rank_rows = []
    per_geom_top = {}
    for gid in [g["geom_id"] for g in cfg.GEOMETRIES]:
        lst = sorted(data[gid].items(), key=lambda kv: -kv[1]["ocs_total"])
        per_geom_top[gid] = lst[0]
        for rank, (pid, s) in enumerate(lst, 1):
            rank_rows.append([gid, rank, pid, s["role"], s["group"], f"{s['ocs_total']:.8f}",
                              f"{s['metal_pct']:.2f}", s["near_specular_metal"]])
    with open(T / "p4physD_cross_geometry_rank_table.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["geom_id", "rank", "pose_id", "role", "group", "ocs_total", "metal_pct",
                     "near_specular_metal"])
        wr.writerows(rank_rows)

    # ---- top1_stability_table：A_top1/R4/R3 每几何 OCS、rank、机制标签 + 每几何最亮 ----
    stab_rows = []
    for gid in [g["geom_id"] for g in cfg.GEOMETRIES]:
        lst = sorted(data[gid].items(), key=lambda kv: -kv[1]["ocs_total"])
        rankmap = {pid: i + 1 for i, (pid, _) in enumerate(lst)}
        gtop_pid, gtop = per_geom_top[gid]
        for pid in ["A_top1", "B_R4", "C_R3"]:
            s = data[gid][pid]
            stab_rows.append([gid, pid, s["role"], f"{s['ocs_total']:.8f}", rankmap[pid],
                              f"{s['metal_pct']:.2f}", s["near_specular_metal"], s["dark_panel_increment"],
                              f"{s['dark']:.6f}",
                              gtop_pid, gtop["role"], f"{gtop['ocs_total']:.8f}",
                              gtop["near_specular_metal"]])
    with open(T / "p4physD_top1_stability_table.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["geom_id", "pose_id", "role", "ocs_total", "rank_in_geom", "metal_pct",
                     "near_specular_metal", "dark_panel_increment", "dark_panel_contrib",
                     "geom_brightest_pose", "geom_brightest_role", "geom_brightest_ocs",
                     "geom_brightest_nsm"])
        wr.writerows(stab_rows)

    n_ok = sum(1 for c in consist_rows if c[-1] == "OK")
    max_rel = max(float(c[4]) for c in consist_rows)
    print(f"[D-analysis] DONE  consistency_ok={n_ok}/{len(consist_rows)}  max_rel_diff={max_rel:.2e}")
    for gid, (pid, s) in per_geom_top.items():
        print(f"  {gid:14s} brightest={pid:12s} OCS={s['ocs_total']:.5f} nsm={s['near_specular_metal']} metal%={s['metal_pct']:.1f}")

    # 返回 data 供上层图/文本使用
    return data, per_geom_top


if __name__ == "__main__":
    main()

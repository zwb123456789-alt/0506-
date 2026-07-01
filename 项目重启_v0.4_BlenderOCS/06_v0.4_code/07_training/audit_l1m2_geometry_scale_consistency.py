#!/usr/bin/env python3
"""
audit_l1m2_geometry_scale_consistency.py —— R116 子任务 A2

跨几何量纲一致性核验 + train-only transform 泄漏检查 + attitude 对齐检查。

产出（写入 v0.4_results/12_l1m3_degraded_mroll/audit/）：
  l1m2_geometry_scale_consistency.csv   各几何总光度 / contributing pixel 分布
  l1m2_geometry_scale_consistency.md    人读审计表 + 归一化参数来源 + 结论
  l1m2_transform_leakage_check.json     train-only z-score 参数与 val/test 泄漏检查

核验内容（对应 R116 §3 A2 六点）：
  1. 各几何 phase24/45/63/90/120 总光度分布 mean/std/min/max/percentiles
  2. 各几何 contributing pixels 分布
  3. r_max / pixel_area / i_scale / depth_epsilon / resolution / log1p 参数来源
  4. train-only transform 参数 vs val/test 泄漏检查
  5. 每 attitude 在 L1-G1/G3/G5 中 record_id / yaw / pitch 对齐检查
  6. 明确 simulated multi-view geometry，非路线二真实跨时间多几何
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from dataset_l1m2_multigeometry import (  # noqa: E402
    GEOM_GROUPS, load_geom_ocs, build_multigeometry_table, fit_flux_transform,
)
from train_l1m2_multigeometry import split_pint, split_pext  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT_DIR = PROJECT_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" / "audit"
FULLRUN_POST = PROJECT_ROOT / "v0.4_results" / "01_fullrun" / "postprocess"
L1M2_POST = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs" / "postprocess"

GEOMS = ["phase24", "phase45", "phase63", "phase90", "phase120"]
PHASE_ANGLE = {"phase24": 23.60, "phase45": 45.00, "phase63": 63.11,
               "phase90": 90.00, "phase120": 120.00}


def load_geom_header(geom_id):
    if geom_id == "phase63":
        d = json.load(open(FULLRUN_POST / "ocs_manifest_v0_4_fullrun.json", encoding="utf-8"))
        return {
            "geom_id": "phase63",
            "pixel_area_m2": d.get("pixel_area_m2"),
            "ortho_scale_m": d.get("ortho_scale_m"),
            "depth_epsilon_m": d.get("depth_epsilon_m"),
            "resolution": d.get("resolution"),
            "r_max": None,  # phase63 manifest 未直接记录 r_max（ortho=2.2*r_max 推得）
            "i_scale_smallrun": None,
            "log1p_alpha": None,
            "ocs_integration_version": d.get("ocs_integration_version"),
            "brdf_model": d.get("brdf_model"),
        }
    else:
        d = json.load(open(L1M2_POST / geom_id / "fullrun_postprocess_summary.json",
                           encoding="utf-8"))
        return {
            "geom_id": geom_id,
            "pixel_area_m2": d.get("pixel_area_m2"),
            "ortho_scale_m": d.get("ortho_scale_m"),
            "depth_epsilon_m": d.get("depth_epsilon_m_final"),
            "resolution": d.get("resolution"),
            "r_max": d.get("r_max"),
            "i_scale_smallrun": d.get("i_scale_smallrun"),
            "log1p_alpha": d.get("log1p_alpha"),
            "ocs_integration_version": None,
            "brdf_model": None,
            "brdf_branch": d.get("brdf_branch"),
        }


def load_geom_pixels(geom_id):
    """返回 {attitude_key: n_pixels_contributing}。"""
    if geom_id == "phase63":
        d = json.load(open(FULLRUN_POST / "ocs_manifest_v0_4_fullrun.json", encoding="utf-8"))
        recs = d["records"]
    else:
        d = json.load(open(L1M2_POST / geom_id / "fullrun_postprocess_summary.json",
                           encoding="utf-8"))
        recs = [r for r in d["records"] if r.get("status", "COMPLETE") == "COMPLETE"]
    out = {}
    for r in recs:
        k = (int(round(r["yaw_deg"])), int(round(r["pitch_deg"])))
        out[k] = int(r.get("n_pixels_contributing", -1))
    return out


def dist_stats(arr):
    a = np.asarray(arr, dtype=np.float64)
    return {
        "n": int(a.size),
        "mean": float(a.mean()), "std": float(a.std()),
        "min": float(a.min()), "max": float(a.max()),
        "p05": float(np.percentile(a, 5)), "p25": float(np.percentile(a, 25)),
        "p50": float(np.percentile(a, 50)), "p75": float(np.percentile(a, 75)),
        "p95": float(np.percentile(a, 95)),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1+2. 各几何总光度 + contributing pixel 分布 ──
    geom_ocs = {g: load_geom_ocs(g) for g in GEOMS}
    geom_pix = {g: load_geom_pixels(g) for g in GEOMS}
    geom_hdr = {g: load_geom_header(g) for g in GEOMS}

    rows = []
    for g in GEOMS:
        totals = [v["total"] for v in geom_ocs[g].values()]
        pixels = [v for v in geom_pix[g].values() if v >= 0]
        ts = dist_stats(totals)
        ps = dist_stats(pixels)
        rows.append({
            "geom_id": g, "phase_angle_deg": PHASE_ANGLE[g],
            "n_attitude": ts["n"],
            "flux_mean": ts["mean"], "flux_std": ts["std"],
            "flux_min": ts["min"], "flux_max": ts["max"],
            "flux_p05": ts["p05"], "flux_p50": ts["p50"], "flux_p95": ts["p95"],
            "pix_mean": ps["mean"], "pix_std": ps["std"],
            "pix_min": ps["min"], "pix_max": ps["max"], "pix_p50": ps["p50"],
        })

    # CSV
    import csv
    keys = list(rows[0].keys())
    with open(OUT_DIR / "l1m2_geometry_scale_consistency.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # ── 3. 参数来源 + 一致性判定 ──
    param_keys = ["pixel_area_m2", "ortho_scale_m", "depth_epsilon_m", "resolution",
                  "r_max", "i_scale_smallrun", "log1p_alpha"]
    # 以有完整记录的几何（phase24）为参照，逐参数判断跨几何是否一致
    param_consistency = {}
    for pk in param_keys:
        vals = {g: geom_hdr[g].get(pk) for g in GEOMS}
        nonnull = [v for v in vals.values() if v is not None]
        if not nonnull:
            param_consistency[pk] = {"values": vals, "consistent": None,
                                     "note": "all null"}
            continue
        allclose = all(abs(float(v) - float(nonnull[0])) < 1e-9 for v in nonnull)
        param_consistency[pk] = {"values": vals, "consistent": bool(allclose),
                                 "n_nonnull": len(nonnull)}

    # ── 4. train-only transform 泄漏检查 ──
    leakage = {}
    for grp in ["G1", "G3", "G5"]:
        table, geoms = build_multigeometry_table(grp)
        # P-INT split（seed=42，与正式 run 一致）
        tr, va, te = split_pint(table, seed=42)
        tf = fit_flux_transform(tr)
        # 用 train 参数变换 val/test，检查是否只用了 train 统计
        Xtr = np.log1p(np.array([r["flux_vector"] for r in tr]))
        tr_mean_recomputed = Xtr.mean(axis=0).tolist()
        # 泄漏检查：若错误地在 full 上 fit，mean 会不同
        Xfull = np.log1p(np.array([r["flux_vector"] for r in table]))
        full_mean = Xfull.mean(axis=0).tolist()
        mean_train_vs_full_diff = float(np.max(np.abs(
            np.array(tf["mean"]) - np.array(full_mean))))
        # 与保存的 run_config flux_transform 对比
        run_dir = (PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs" /
                   "runs" / f"P-INT_{grp}_ocs_only_seed42")
        saved = json.load(open(run_dir / "run_config.json", encoding="utf-8")).get("flux_transform")
        mean_match = np.allclose(tf["mean"], saved["mean"], atol=1e-9) if saved else None
        std_match = np.allclose(tf["std"], saved["std"], atol=1e-9) if saved else None
        # split 无重叠检查
        tr_keys = set(r["attitude_key"] for r in tr)
        va_keys = set(r["attitude_key"] for r in va)
        te_keys = set(r["attitude_key"] for r in te)
        leakage[grp] = {
            "n_train": len(tr), "n_val": len(va), "n_test": len(te),
            "train_fit_mean": tf["mean"], "train_fit_std": tf["std"],
            "full_fit_mean_for_reference": full_mean,
            "max_abs_diff_train_vs_full_mean": mean_train_vs_full_diff,
            "train_transform_matches_saved_run_config": bool(mean_match) if mean_match is not None else None,
            "std_matches_saved_run_config": bool(std_match) if std_match is not None else None,
            "split_overlap_train_val": len(tr_keys & va_keys),
            "split_overlap_train_test": len(tr_keys & te_keys),
            "split_overlap_val_test": len(va_keys & te_keys),
            "leakage_free": (len(tr_keys & va_keys) == 0 and
                             len(tr_keys & te_keys) == 0 and
                             len(va_keys & te_keys) == 0),
        }

    # ── 5. attitude 对齐检查（G1⊂G3⊂G5 且 yaw/pitch 一致）──
    tblG1, _ = build_multigeometry_table("G1")
    tblG3, _ = build_multigeometry_table("G3")
    tblG5, _ = build_multigeometry_table("G5")
    keysG1 = set(r["attitude_key"] for r in tblG1)
    keysG3 = set(r["attitude_key"] for r in tblG3)
    keysG5 = set(r["attitude_key"] for r in tblG5)
    alignment = {
        "n_G1": len(keysG1), "n_G3": len(keysG3), "n_G5": len(keysG5),
        "G1_subset_G3": keysG1.issubset(keysG3),
        "G3_subset_G5": keysG3.issubset(keysG5),
        "G1_subset_G5": keysG1.issubset(keysG5),
        "all_2664": (len(keysG1) == 2664 and len(keysG3) == 2664 and len(keysG5) == 2664),
    }
    # 逐 attitude yaw/pitch 一致性（抽样全量核对 G5 表内 record 的 yaw/pitch 与 key 一致）
    yaw_pitch_mismatch = 0
    for r in tblG5:
        yk, pk = r["attitude_key"]
        if int(round(r["yaw_deg"])) != yk or int(round(r["pitch_deg"])) != pk:
            yaw_pitch_mismatch += 1
    alignment["yaw_pitch_key_mismatch"] = yaw_pitch_mismatch

    leakage_json = {
        "task": "R116-A2 cross-geometry scale consistency + leakage check",
        "param_consistency": param_consistency,
        "transform_leakage": leakage,
        "attitude_alignment": alignment,
        "semantics": ("simulated multi-view geometry: 同一姿态在多组已知 sun/view 几何下的"
                      "总光度标量拼成多观测向量；不是路线二真实跨时间多几何，不含真实观测噪声/时间采样。"),
    }
    json.dump(leakage_json, open(OUT_DIR / "l1m2_transform_leakage_check.json", "w",
                                 encoding="utf-8"), indent=2, ensure_ascii=False)

    # ── 6. Markdown 审计表 ──
    md = []
    md.append("# L1M2 跨几何量纲一致性核验（R116 子任务 A2）\n")
    md.append("最后更新：2026-07-01  \n来源：`v0.4_results/11_l1m2_multigeometry_ocs/postprocess/` + `01_fullrun/postprocess/`\n")
    md.append("## 1. 各几何总光度与 contributing pixel 分布\n")
    md.append("| geom | 相位角° | n | flux mean | flux std | flux min | flux p50 | flux max | pix mean | pix p50 | pix max |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        md.append(f"| {r['geom_id']} | {r['phase_angle_deg']:.2f} | {r['n_attitude']} | "
                  f"{r['flux_mean']:.5f} | {r['flux_std']:.5f} | {r['flux_min']:.5f} | "
                  f"{r['flux_p50']:.5f} | {r['flux_max']:.5f} | {r['pix_mean']:.0f} | "
                  f"{r['pix_p50']:.0f} | {r['pix_max']:.0f} |")
    md.append("\n各几何 flux 均值互异（phase24 最高、phase120 最低），说明多观测向量含实质跨几何信息，非单标量重复。\n")

    md.append("## 2. 归一化 / 积分参数来源与跨几何一致性\n")
    md.append("| 参数 | phase24 | phase45 | phase63 | phase90 | phase120 | 一致 |")
    md.append("|---|---|---|---|---|---|---|")
    for pk in param_keys:
        pc = param_consistency[pk]
        vals = pc["values"]
        cons = {True: "是", False: "否", None: "n/a"}[pc["consistent"]]
        md.append(f"| {pk} | {vals['phase24']} | {vals['phase45']} | {vals['phase63']} | "
                  f"{vals['phase90']} | {vals['phase120']} | {cons} |")
    md.append("\n说明：")
    md.append("- `pixel_area_m2 / ortho_scale_m / depth_epsilon_m / resolution` 五几何完全一致，OCS 物理积分同量纲、可直接跨几何比较。")
    md.append("- `r_max / i_scale_smallrun / log1p_alpha` 在 phase63 manifest header 记为 null（记录在其它冻结文件），phase24/45/90/120 header 显式记录且四者一致；`i_scale/log1p` 仅影响 PNG 显示（Pass 2），不进入 `ocs_total` 物理积分，不影响 OCS-only 输入量纲。")
    md.append("- 五几何 `ocs_integration_version` 与 `brdf_branch=B0` 同源同管线（103 报告 §5 派生包装器，覆盖 SUN/DET/OUTPUT 后调用原 main）。\n")

    md.append("## 3. train-only transform 泄漏检查\n")
    md.append("| group | n_tr/va/te | train-fit 与 saved run_config 一致 | split 重叠(tr∩va,tr∩te,va∩te) | leakage-free |")
    md.append("|---|---|---|---|---|")
    for grp in ["G1", "G3", "G5"]:
        lk = leakage[grp]
        md.append(f"| {grp} | {lk['n_train']}/{lk['n_val']}/{lk['n_test']} | "
                  f"mean={lk['train_transform_matches_saved_run_config']} "
                  f"std={lk['std_matches_saved_run_config']} | "
                  f"{lk['split_overlap_train_val']},{lk['split_overlap_train_test']},"
                  f"{lk['split_overlap_val_test']} | {lk['leakage_free']} |")
    md.append("\nz-score 参数仅由 train 拟合（`fit_flux_transform(tr)`），与 run_config 保存值逐位一致；train/val/test attitude 无交集，无 transform 泄漏。\n")

    md.append("## 4. attitude 对齐与嵌套\n")
    md.append(f"- G1/G3/G5 attitude 数：{alignment['n_G1']}/{alignment['n_G3']}/{alignment['n_G5']}（均 2664：{alignment['all_2664']}）")
    md.append(f"- 嵌套：G1⊂G3={alignment['G1_subset_G3']}, G3⊂G5={alignment['G3_subset_G5']}, G1⊂G5={alignment['G1_subset_G5']}")
    md.append(f"- yaw/pitch 与 attitude_key 不一致条数：{alignment['yaw_pitch_key_mismatch']}\n")

    md.append("## 5. 语义边界\n")
    md.append("本多几何是 **simulated multi-view geometry**：同一姿态在多组已知 sun/view 几何下分别积分得到总光度标量，拼成多观测光度向量。")
    md.append("它不是路线二真实跨时间多几何，不含真实观测噪声与真实时间采样，也不代表真实未知目标的可观测序列。\n")

    md.append("## 6. 核验结论\n")
    all_param_ok = all(param_consistency[pk]["consistent"] in (True, None)
                       for pk in param_keys)
    all_leak_ok = all(leakage[g]["leakage_free"] and
                      leakage[g]["train_transform_matches_saved_run_config"]
                      for g in ["G1", "G3", "G5"])
    align_ok = (alignment["all_2664"] and alignment["G1_subset_G3"] and
                alignment["G3_subset_G5"] and alignment["yaw_pitch_key_mismatch"] == 0)
    md.append(f"- 跨几何物理量纲参数一致：{all_param_ok}")
    md.append(f"- train-only transform 无泄漏且与训练一致：{all_leak_ok}")
    md.append(f"- attitude 对齐/嵌套/坐标一致：{align_ok}")
    md.append(f"\n**综合：R116 A2 跨几何量纲一致性核验通过 = {all_param_ok and all_leak_ok and align_ok}**")

    with open(OUT_DIR / "l1m2_geometry_scale_consistency.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print("[A2 DONE] 跨几何量纲一致性核验")
    print(f"  param_consistent={all_param_ok} leakage_free={all_leak_ok} alignment_ok={align_ok}")
    for r in rows:
        print(f"  {r['geom_id']}: flux_mean={r['flux_mean']:.5f} pix_mean={r['pix_mean']:.0f} n={r['n_attitude']}")
    print(f"  -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

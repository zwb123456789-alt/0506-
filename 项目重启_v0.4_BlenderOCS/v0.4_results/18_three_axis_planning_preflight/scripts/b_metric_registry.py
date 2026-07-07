#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
18 号三轴准备包 - 子任务B：三轴指标 registry（只读）

输出：
  tables/three_axis_metric_registry.csv
  同时把 §3.1/§3.2 派生指标（local_contrast, glint_flag）写回一个扩展主表
  seeds/attitude_master_derived.csv 供后续复用（只读计算，不新渲染）。
"""
import csv
import os
import numpy as np

V04 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(V04, "v0.4_results", "18_three_axis_planning_preflight")

REGISTRY = [
    # metric_id, concept, formula_or_field, source_pack, availability, roll_extend, risk_or_info
    ("brightness", "OCS magnitude / 最亮最暗", "ocs_total (per geom)",
     "01_fullrun; 11_l1m2", "A-direct", "needs roll render", "brightness (not information)"),
    ("local_contrast", "姿态邻域可区分性", "mean|ocs_total(a)-ocs_total(nbr)| over yaw/pitch +-5",
     "derived in 18", "B-derived", "needs roll neighbors", "information"),
    ("nn_ambiguity", "最近邻光度混淆", "pdb nearest_distance / margin",
     "13_l1d3 pdb", "A-direct", "needs roll retrieval", "information(low=ambiguous)"),
    ("candidate_entropy", "候选分布集中度", "neural_entropy",
     "13_l1d3 joined", "A-direct", "needs roll-aware model", "information"),
    ("candidate_margin", "top1-top2 间隔", "neural_margin",
     "13_l1d3 joined", "A-direct", "needs roll-aware model", "information"),
    ("topk_stability", "扰动下最优候选稳定性", "topk10_idx overlap under perturb",
     "13_l1d3 pdb", "A-direct(prior)", "needs roll perturb", "information"),
    ("ocs_image_overlap", "通道 top-k 一致", "d2_pairwise_topk_overlap",
     "16_closure d2", "A-direct", "needs roll predictions", "consistency"),
    ("ocs_image_js", "通道分布冲突", "d2_pairwise_disagreement (JS/disagree)",
     "16_closure d2", "A-direct", "needs roll predictions", "consistency"),
    ("glint_flag", "亮但不可用风险", "ocs_total>=P99 AND n_contrib<=P10",
     "derived in 18", "B-derived", "needs roll render", "risk"),
    ("geometry_utility", "几何是否值得观测", "d4 gain_g1_to_g5 / region frac_low",
     "16_closure d4", "A-direct", "recompute with roll", "planning"),
    ("roll_sensitivity", "fixed-roll 结论 roll 迁移", "mroll yaw_err(+-30) - yaw_err(+-15)",
     "17_postclosure mroll", "A-direct(prior)", "P1 densify", "roll-migration"),
]


def fnum(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return np.nan


def main():
    with open(os.path.join(OUT, "tables", "three_axis_metric_registry.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric_id", "concept", "formula_or_field", "source_pack",
                    "availability", "roll_extend_need", "info_class"])
        w.writerows(REGISTRY)

    # ---- 派生 local_contrast 与 glint_flag，扩展主表 ----
    master_path = os.path.join(OUT, "seeds", "attitude_master_fixedroll.csv")
    rows = list(csv.DictReader(open(master_path, encoding="utf-8")))
    bright = {}
    for r in rows:
        bright[(int(round(fnum(r["yaw"]))), int(round(fnum(r["pitch"]))))] = fnum(r["ocs_total_phase63"])

    bvals = np.array([v for v in bright.values() if v > 0])
    p99 = np.percentile(bvals, 99)
    contrib_vals = np.array([fnum(r["n_pix_contrib"]) for r in rows
                             if fnum(r["ocs_total_phase63"]) >= p99])
    p10_contrib = np.percentile(contrib_vals, 10) if len(contrib_vals) else 0

    out_rows = []
    for r in rows:
        y = int(round(fnum(r["yaw"]))); p = int(round(fnum(r["pitch"])))
        b0 = bright.get((y, p), np.nan)
        # 8 邻域
        diffs = []
        for dy in (-5, 0, 5):
            for dp in (-5, 0, 5):
                if dy == 0 and dp == 0:
                    continue
                yn = (y + dy) % 360
                pn = p + dp
                if (yn, pn) in bright and not np.isnan(b0):
                    diffs.append(abs(b0 - bright[(yn, pn)]))
        lc = float(np.mean(diffs)) if diffs else ""
        glint = 1 if (not np.isnan(b0) and b0 >= p99 and fnum(r["n_pix_contrib"]) <= p10_contrib) else 0
        nr = dict(r)
        nr["local_contrast"] = lc
        nr["glint_flag"] = glint
        out_rows.append(nr)

    fields = list(rows[0].keys()) + ["local_contrast", "glint_flag"]
    with open(os.path.join(OUT, "seeds", "attitude_master_derived.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    nglint = sum(r["glint_flag"] for r in out_rows)
    print("[B] metric registry + derived done.")
    print(f"  registry metrics: {len(REGISTRY)}")
    print(f"  P99 brightness = {p99:.4g}, P10 contrib(among bright) = {p10_contrib:.1f}")
    print(f"  glint_flag=1 count: {nglint}")


if __name__ == "__main__":
    main()

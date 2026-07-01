#!/usr/bin/env python3
"""
eval_l1d3_confidence_consistency.py —— R118 子任务 C：neural vs P-DB 一致性/互补/置信排序

目标不是证明 joint 强互补，而是比较不同证据链在同一 test split 上的
错误、置信、候选排序是否一致。

评估对象：
  neural: ocs_only/image_only/joint × final/best × clean/mild/moderate × G1/G3/G5
  P-DB  : clean/mild/moderate × G1/G3/G5 × neg-L2/cosine/zscore-neg-L2

输出：
  consistency/l1d3_neural_pdb_joined_per_attitude.csv
  consistency/l1d3_error_correlation_summary.csv
  consistency/l1d3_complementarity_cases.csv
  consistency/l1d3_confidence_deciles.csv
  consistency/l1d3_risk_coverage.csv
  consistency/l1d3_consistency_key_findings.md

置信定义（均为工程分数，非真实 posterior）：
  neural   : confidence = margin（top1-top2 posterior_like score）；越大越自信。
  P-DB     : confidence = retrieval margin（top1-top2 sim）；越大越自信。
  correct 判据：yaw circular error <= 30°（hit@30）。
"""

import csv

import numpy as np

import l1d3_common as C

HIT_THR = 30.0


def pdb_per_query(geom, deg_level, split, similarity):
    """返回按 record_id 索引的 P-DB top1 结果 dict。"""
    tr, va, te, _ = C.get_split_tables(geom, "P-INT")
    queries = va if split == "val" else te
    X_tmpl = C.flux_matrix(tr, deg_level)      # matched-degraded
    X_qry = C.flux_matrix(queries, deg_level)
    yaw_tr, pit_tr = C.yaws(tr), C.pitches(tr)
    yaw_q, pit_q = C.yaws(queries), C.pitches(queries)
    rid_q = C.record_ids(queries)

    transform = None
    if similarity == "zscore-neg-L2":
        transform = C.fit_flux_transform([{"flux_vector": X_tmpl[i]} for i in range(len(X_tmpl))])
    sim = C.retrieval_scores(X_qry, X_tmpl, similarity, transform=transform)
    order, vals = C.retrieve_topk(sim, k=10)
    dist = C.retrieval_distance_stats(vals)
    top1 = order[:, 0]
    yce1 = C.circ_err_between(yaw_tr[top1], yaw_q)
    # top-k candidate yaw spread（ambiguity 指标）
    cand_yaw = yaw_tr[order]  # [Nq,10]
    out = {}
    for i in range(len(queries)):
        # candidate yaw 分散度：相对 top1 的 circular spread std
        cy = cand_yaw[i]
        spread = float(np.std(C.circ_err_between(cy, np.full_like(cy, cy[0]))))
        out[str(rid_q[i])] = {
            "pdb_top1_yaw_err": float(yce1[i]),
            "pdb_nearest_distance": float(dist["nearest_distance"][i]),
            "pdb_margin": float(dist["margin_sim"][i]),
            "pdb_cand_yaw_spread": spread,
        }
    return out


def neural_per_query(deg_level, geom, mode, split, select):
    """返回按 record_id 索引的 neural 结果 dict（含 margin/entropy 置信）。"""
    s = C.load_neural_samples(deg_level, "P-INT", geom, mode, split, select)
    if s is None:
        return None
    rid = s["record_id"]
    out = {}
    for i in range(len(rid)):
        out[str(rid[i])] = {
            "neural_yaw_err": float(s["yaw_circular_error_deg"][i]),
            "neural_pitch_err": float(s["pitch_abs_error_deg"][i]),
            "neural_yaw_pred": float(s["yaw_pred_deg"][i]),
            "neural_margin": float(s["margin"][i]),
            "neural_entropy": float(s["entropy"][i]),
            "yaw_true": float(s["yaw_true_deg"][i]),
            "pitch_true": float(s["pitch_true_deg"][i]),
        }
    return out


def deciles_curve(conf, err, n_bins=10):
    """按 confidence 从高到低分 decile；返回每桶 MAE/hit@30/n。

    conf 越大越自信。返回 list（decile 1=最自信）。
    """
    order = np.argsort(-conf)
    err_sorted = np.asarray(err)[order]
    N = len(err_sorted)
    rows = []
    for d in range(n_bins):
        lo = d * N // n_bins
        hi = (d + 1) * N // n_bins
        if hi <= lo:
            continue
        seg = err_sorted[lo:hi]
        rows.append({
            "decile": d + 1,  # 1 = 最自信
            "n": int(hi - lo),
            "yaw_cmae": round(float(seg.mean()), 4),
            "yaw_hit@30": round(float((seg <= HIT_THR).mean()), 4),
        })
    return rows


def risk_coverage(conf, err, steps=20):
    """按 confidence 从高到低保留样本，报告 coverage 比例与保留集合 MAE/hit@30。"""
    order = np.argsort(-conf)
    err_sorted = np.asarray(err)[order]
    N = len(err_sorted)
    rows = []
    for s in range(1, steps + 1):
        frac = s / steps
        k = max(1, int(round(frac * N)))
        seg = err_sorted[:k]
        rows.append({
            "coverage": round(frac, 3),
            "n_kept": int(k),
            "yaw_cmae": round(float(seg.mean()), 4),
            "yaw_hit@30": round(float((seg <= HIT_THR).mean()), 4),
        })
    return rows


def main():
    cons = C.OUT / "consistency"
    cons.mkdir(parents=True, exist_ok=True)

    joined_rows = []
    corr_rows = []
    comp_rows = []
    decile_rows = []
    rc_rows = []

    # 评估矩阵：neural 三模式 × best/final × 三退化 × 三几何（存在的）
    for deg in C.DEGRADE_ALL:
        for geom in C.GROUPS:
            pdb = pdb_per_query(geom, deg, "test", "neg-L2")
            for mode in C.MODES:
                for select in ("best", "final"):
                    neu = neural_per_query(deg, geom, mode, "test", select)
                    if neu is None:
                        continue
                    # join by record_id（交集）
                    keys = [k for k in neu if k in pdb]
                    if not keys:
                        continue
                    n_err = np.array([neu[k]["neural_yaw_err"] for k in keys])
                    p_err = np.array([pdb[k]["pdb_top1_yaw_err"] for k in keys])
                    n_margin = np.array([neu[k]["neural_margin"] for k in keys])
                    p_margin = np.array([pdb[k]["pdb_margin"] for k in keys])

                    # per-attitude 合并行
                    for k in keys:
                        joined_rows.append({
                            "degrade_level": deg, "geom": geom, "mode": mode, "select": select,
                            "record_id": k,
                            "yaw_true": round(neu[k]["yaw_true"], 3),
                            "pitch_true": round(neu[k]["pitch_true"], 3),
                            "neural_yaw_pred": round(neu[k]["neural_yaw_pred"], 3),
                            "neural_yaw_err": round(neu[k]["neural_yaw_err"], 4),
                            "neural_pitch_err": round(neu[k]["neural_pitch_err"], 4),
                            "neural_margin": round(neu[k]["neural_margin"], 6),
                            "neural_entropy": round(neu[k]["neural_entropy"], 6),
                            "pdb_top1_yaw_err": round(pdb[k]["pdb_top1_yaw_err"], 4),
                            "pdb_nearest_distance": round(pdb[k]["pdb_nearest_distance"], 6),
                            "pdb_margin": round(pdb[k]["pdb_margin"], 6),
                            "pdb_cand_yaw_spread": round(pdb[k]["pdb_cand_yaw_spread"], 4),
                        })

                    # 错误相关性
                    def _safe_corr(a, b):
                        if np.std(a) < 1e-12 or np.std(b) < 1e-12:
                            return float("nan")
                        return float(np.corrcoef(a, b)[0, 1])
                    # spearman via rank
                    def _spearman(a, b):
                        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
                        return _safe_corr(ra.astype(float), rb.astype(float))
                    corr_rows.append({
                        "degrade_level": deg, "geom": geom, "mode": mode, "select": select,
                        "n": len(keys),
                        "pearson_neural_pdb_yawerr": round(_safe_corr(n_err, p_err), 4),
                        "spearman_neural_pdb_yawerr": round(_spearman(n_err, p_err), 4),
                        "neural_yaw_cmae": round(float(n_err.mean()), 4),
                        "pdb_yaw_cmae": round(float(p_err.mean()), 4),
                        "neural_hit@30": round(float((n_err <= HIT_THR).mean()), 4),
                        "pdb_hit@30": round(float((p_err <= HIT_THR).mean()), 4),
                    })

                    # 互补四象限
                    n_ok = n_err <= HIT_THR
                    p_ok = p_err <= HIT_THR
                    comp_rows.append({
                        "degrade_level": deg, "geom": geom, "mode": mode, "select": select,
                        "n": len(keys),
                        "both_correct": int((n_ok & p_ok).sum()),
                        "neural_only": int((n_ok & ~p_ok).sum()),
                        "pdb_only": int((~n_ok & p_ok).sum()),
                        "both_wrong": int((~n_ok & ~p_ok).sum()),
                        "either_correct": int((n_ok | p_ok).sum()),
                        "oracle_hit@30": round(float((n_ok | p_ok).mean()), 4),
                    })

                    # 置信 decile / risk-coverage（用 neural margin）
                    for r in deciles_curve(n_margin, n_err):
                        r.update({"degrade_level": deg, "geom": geom, "mode": mode,
                                  "select": select, "conf_source": "neural_margin"})
                        decile_rows.append(r)
                    for r in risk_coverage(n_margin, n_err):
                        r.update({"degrade_level": deg, "geom": geom, "mode": mode,
                                  "select": select, "conf_source": "neural_margin"})
                        rc_rows.append(r)
                    # P-DB margin risk-coverage（仅 ocs_only 代表，避免重复；对每 mode 用同一 pdb）
                    if mode == "ocs_only":
                        pdb_err_arr = np.array([pdb[k]["pdb_top1_yaw_err"] for k in keys])
                        pdb_margin_arr = np.array([pdb[k]["pdb_margin"] for k in keys])
                        for r in deciles_curve(pdb_margin_arr, pdb_err_arr):
                            r.update({"degrade_level": deg, "geom": geom, "mode": "pdb",
                                      "select": "-", "conf_source": "pdb_margin"})
                            decile_rows.append(r)
                        for r in risk_coverage(pdb_margin_arr, pdb_err_arr):
                            r.update({"degrade_level": deg, "geom": geom, "mode": "pdb",
                                      "select": "-", "conf_source": "pdb_margin"})
                            rc_rows.append(r)

    # 写文件
    with open(cons / "l1d3_neural_pdb_joined_per_attitude.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["degrade_level", "geom", "mode", "select", "record_id", "yaw_true", "pitch_true",
                "neural_yaw_pred", "neural_yaw_err", "neural_pitch_err", "neural_margin",
                "neural_entropy", "pdb_top1_yaw_err", "pdb_nearest_distance", "pdb_margin",
                "pdb_cand_yaw_spread"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(joined_rows)

    with open(cons / "l1d3_error_correlation_summary.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["degrade_level", "geom", "mode", "select", "n",
                "pearson_neural_pdb_yawerr", "spearman_neural_pdb_yawerr",
                "neural_yaw_cmae", "pdb_yaw_cmae", "neural_hit@30", "pdb_hit@30"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(corr_rows)

    with open(cons / "l1d3_complementarity_cases.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["degrade_level", "geom", "mode", "select", "n", "both_correct",
                "neural_only", "pdb_only", "both_wrong", "either_correct", "oracle_hit@30"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(comp_rows)

    with open(cons / "l1d3_confidence_deciles.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["degrade_level", "geom", "mode", "select", "conf_source",
                "decile", "n", "yaw_cmae", "yaw_hit@30"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(decile_rows)

    with open(cons / "l1d3_risk_coverage.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["degrade_level", "geom", "mode", "select", "conf_source",
                "coverage", "n_kept", "yaw_cmae", "yaw_hit@30"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rc_rows)

    # key findings
    md = ["# R118 子任务 C：neural vs P-DB 一致性 / 互补 / 置信排序关键结论\n",
          "最后更新：2026-07-01  \n",
          "**置信为工程分数（neural margin / P-DB retrieval margin），非真实 Bayesian posterior。"
          "correct 判据 = yaw circular error ≤ 30°。**\n"]

    def _corr(deg, geom, mode, select="best"):
        for r in corr_rows:
            if (r["degrade_level"] == deg and r["geom"] == geom and r["mode"] == mode
                    and r["select"] == select):
                return r
        return None

    md.append("## 1. neural vs P-DB yaw error 相关性（test, best, G5）\n")
    md.append("| degrade_level | mode | neural cMAE | pdb cMAE | pearson | spearman |")
    md.append("|:--|:--|--:|--:|--:|--:|")
    for deg in C.DEGRADE_ALL:
        for mode in C.MODES:
            r = _corr(deg, "G5", mode)
            if r:
                md.append(f"| {deg} | {mode} | {r['neural_yaw_cmae']:.2f} | {r['pdb_yaw_cmae']:.2f} | "
                          f"{r['pearson_neural_pdb_yawerr']:.3f} | {r['spearman_neural_pdb_yawerr']:.3f} |")
    md.append("")

    md.append("## 2. 互补四象限（test, best, G5, neural vs P-DB neg-L2）\n")
    md.append("| degrade_level | mode | both✓ | neural_only | pdb_only | both✗ | oracle_hit@30 |")
    md.append("|:--|:--|--:|--:|--:|--:|--:|")
    for deg in C.DEGRADE_ALL:
        for mode in C.MODES:
            for r in comp_rows:
                if (r["degrade_level"] == deg and r["geom"] == "G5" and r["mode"] == mode
                        and r["select"] == "best"):
                    md.append(f"| {deg} | {mode} | {r['both_correct']} | {r['neural_only']} | "
                              f"{r['pdb_only']} | {r['both_wrong']} | {r['oracle_hit@30']:.3f} |")
    md.append("")

    md.append("## 3. 置信排序有效性（risk-coverage，test G5 ocs_only best, neural margin）\n")
    md.append("| coverage | yaw cMAE | yaw hit@30 |")
    md.append("|--:|--:|--:|")
    for r in rc_rows:
        if (r["degrade_level"] == "clean" and r["geom"] == "G5" and r["mode"] == "ocs_only"
                and r["select"] == "best" and r["coverage"] in (0.2, 0.5, 0.8, 1.0)):
            md.append(f"| {r['coverage']:.1f} | {r['yaw_cmae']:.2f} | {r['yaw_hit@30']:.3f} |")
    md.append("")

    md.append("## 4. 读法与口径\n")
    md.append("```text")
    md.append("- 相关性/互补是同一 test split 上不同证据链的一致性分析，不是 joint 强互补性证明。")
    md.append("- oracle_hit@30（either_correct）是 neural∪P-DB 的上界，代表两条证据链的潜在互补空间，")
    md.append("  不代表可无监督地选中正确一方。")
    md.append("- risk-coverage：若 cMAE 随 coverage 降低而下降、hit@30 上升，说明该置信分数可用于选择性预测。")
    md.append("- 置信是工程分数，不是真实概率；不写成 Bayesian posterior 或真实观测不确定度。")
    md.append("```")
    open(cons / "l1d3_consistency_key_findings.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

    print(f"[C] joined={len(joined_rows)} corr={len(corr_rows)} comp={len(comp_rows)} "
          f"decile={len(decile_rows)} risk_cov={len(rc_rows)}")
    # 打印几条
    for mode in C.MODES:
        r = _corr("clean", "G5", mode)
        if r:
            print(f"  clean G5 {mode}: neural cmae={r['neural_yaw_cmae']:.2f} pdb cmae={r['pdb_yaw_cmae']:.2f} "
                  f"spearman={r['spearman_neural_pdb_yawerr']:.3f}")
    print(f"  -> {cons}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

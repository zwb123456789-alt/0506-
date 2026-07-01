#!/usr/bin/env python3
"""
eval_l1d3_pdb_retrieval.py —— R118 子任务 B：P-DB / template retrieval 正式评估

把 R117 的 P-DB smoke 升级为正式评估包。

Template 库：train split 多观测总光度向量（只来自 train，不混 val/test）。
评估范围：
  protocol      : P-INT
  degrade_level : clean, degraded-mild, degraded-moderate
  geometry_group: G1, G3, G5
  query_split   : val, test
  similarity    : neg-L2, cosine, zscore-neg-L2
  top_k         : 1, 3, 5, 10

退化口径（两种，分开标注）：
  matched-degraded : template 与 query 使用同一 degrade_level（含 clean 自身）
  clean-template   : template clean，query degraded（退化迁移探针，optional）

严格口径：
  P-DB 是 model-known simulated template retrieval，不是真实反演系统。
  P-DB top-k 是候选姿态检索，不是 Bayesian posterior，也不是真实观测成功率。

输出：
  13_l1d3/pdb/l1d3_pdb_template_manifest.csv
  13_l1d3/pdb/l1d3_pdb_retrieval_summary.csv
  13_l1d3/pdb/l1d3_pdb_retrieval_per_query.csv
  13_l1d3/pdb/l1d3_pdb_retrieval_strata.csv
  13_l1d3/pdb/l1d3_pdb_key_findings.md
"""

import csv

import numpy as np

import l1d3_common as C

TOP_KS = [1, 3, 5, 10]
DEG_LEVELS = C.DEGRADE_ALL          # clean, degraded-mild, degraded-moderate
SIMS = C.SIMILARITIES               # neg-L2, cosine, zscore-neg-L2
HIT_THRS = [15, 30, 45]


def eval_one(geom, deg_level, query_split, similarity, template_mode):
    """单组合评估。template_mode: 'matched-degraded' | 'clean-template'。

    返回 (summary_dict, per_query_rows, strata_rows)。
    """
    tr, va, te, geoms = C.get_split_tables(geom, protocol="P-INT")
    queries = va if query_split == "val" else te

    # template flux（train）；query flux
    tmpl_deg = "clean" if template_mode == "clean-template" else deg_level
    X_tmpl = C.flux_matrix(tr, tmpl_deg)
    X_qry = C.flux_matrix(queries, deg_level)
    yaw_tr, pit_tr = C.yaws(tr), C.pitches(tr)
    yaw_q, pit_q = C.yaws(queries), C.pitches(queries)
    rid_q = C.record_ids(queries)

    # zscore transform 必须在 train（对应 template 域）上拟合
    transform = None
    if similarity == "zscore-neg-L2":
        transform = C.fit_flux_transform(
            [{"flux_vector": X_tmpl[i]} for i in range(len(X_tmpl))])

    sim = C.retrieval_scores(X_qry, X_tmpl, similarity, transform=transform)
    order, vals = C.retrieve_topk(sim, k=max(TOP_KS))
    dist = C.retrieval_distance_stats(vals)

    # top1 指标
    top1 = order[:, 0]
    yce1 = C.circ_err_between(yaw_tr[top1], yaw_q)
    pae1 = np.abs(pit_tr[top1] - pit_q)

    summ = {
        "geom": geom, "degrade_level": deg_level, "query_split": query_split,
        "similarity": similarity, "template_mode": template_mode,
        "n_template": len(tr), "n_query": len(queries),
        "top1_yaw_cmae": round(C.circ_mae(yce1), 4),
        "top1_pitch_mae": round(float(pae1.mean()), 4),
        "nn_distance_mean": round(float(dist["nearest_distance"].mean()), 6),
        "margin_mean": round(float(dist["margin_sim"].mean()), 6),
    }
    for thr in HIT_THRS:
        summ[f"top1_yaw_hit@{thr}"] = round(C.hit_at(yce1, thr), 4)
    # top-k-best（oracle over candidates）
    for k in TOP_KS:
        yce_k = np.min(np.stack([C.circ_err_between(yaw_tr[order[:, j]], yaw_q)
                                 for j in range(k)], axis=1), axis=1)
        summ[f"topk{k}_best_yaw_cmae"] = round(C.circ_mae(yce_k), 4)
        summ[f"topk{k}_best_yaw_hit@30"] = round(C.hit_at(yce_k, 30), 4)

    # per-query 行
    pq_rows = []
    for i in range(len(queries)):
        pq_rows.append({
            "geom": geom, "degrade_level": deg_level, "query_split": query_split,
            "similarity": similarity, "template_mode": template_mode,
            "record_id": rid_q[i],
            "yaw_true": round(float(yaw_q[i]), 3), "pitch_true": round(float(pit_q[i]), 3),
            "top1_yaw_pred": round(float(yaw_tr[top1[i]]), 3),
            "top1_pitch_pred": round(float(pit_tr[top1[i]]), 3),
            "top1_yaw_err": round(float(yce1[i]), 4),
            "top1_pitch_err": round(float(pae1[i]), 4),
            "nearest_distance": round(float(dist["nearest_distance"][i]), 6),
            "margin": round(float(dist["margin_sim"][i]), 6),
            "topk10_idx": ";".join(str(int(x)) for x in order[i]),
        })

    # 分层（yaw-sector, pitch-bin）——仅 top1
    strata_rows = []
    sec = C.yaw_sector(yaw_q)
    for s in sorted(set(sec)):
        mask = sec == s
        strata_rows.append({
            "geom": geom, "degrade_level": deg_level, "query_split": query_split,
            "similarity": similarity, "template_mode": template_mode,
            "stratum_type": "yaw_sector", "stratum": s, "n": int(mask.sum()),
            "top1_yaw_cmae": round(C.circ_mae(yce1[mask]), 4),
            "top1_yaw_hit@30": round(C.hit_at(yce1[mask], 30), 4),
        })
    pb = C.pitch_bin(pit_q, width=45)
    for b in sorted(set(pb)):
        mask = pb == b
        strata_rows.append({
            "geom": geom, "degrade_level": deg_level, "query_split": query_split,
            "similarity": similarity, "template_mode": template_mode,
            "stratum_type": "pitch_bin", "stratum": b, "n": int(mask.sum()),
            "top1_yaw_cmae": round(C.circ_mae(yce1[mask]), 4),
            "top1_yaw_hit@30": round(C.hit_at(yce1[mask], 30), 4),
        })
    return summ, pq_rows, strata_rows


def main():
    pdb_dir = C.OUT / "pdb"
    pdb_dir.mkdir(parents=True, exist_ok=True)

    summaries, per_query, strata = [], [], []
    tmpl_manifest = []

    for deg in DEG_LEVELS:
        for geom in C.GROUPS:
            # template_mode: matched-degraded 全部；clean-template 只对 degraded query
            modes = ["matched-degraded"]
            if deg != "clean":
                modes.append("clean-template")
            for tmode in modes:
                for split in ("val", "test"):
                    for sim in SIMS:
                        s, pq, st = eval_one(geom, deg, split, sim, tmode)
                        summaries.append(s)
                        per_query.extend(pq)
                        strata.extend(st)
            # template manifest（每 geom×deg 一条）
            tr, _, _, geoms = C.get_split_tables(geom, "P-INT")
            tmpl_manifest.append({
                "geom": geom, "degrade_level": deg, "n_template": len(tr),
                "geoms": ";".join(geoms), "flux_dim": len(geoms),
                "template_source": "train split only (no val/test leak)",
            })

    # 写 summary
    scols = (["geom", "degrade_level", "query_split", "similarity", "template_mode",
              "n_template", "n_query", "top1_yaw_cmae"]
             + [f"top1_yaw_hit@{t}" for t in HIT_THRS]
             + ["top1_pitch_mae", "nn_distance_mean", "margin_mean"]
             + [f"topk{k}_best_yaw_cmae" for k in TOP_KS]
             + [f"topk{k}_best_yaw_hit@30" for k in TOP_KS])
    with open(pdb_dir / "l1d3_pdb_retrieval_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=scols)
        w.writeheader()
        w.writerows(summaries)

    with open(pdb_dir / "l1d3_pdb_retrieval_per_query.csv", "w", newline="", encoding="utf-8") as f:
        pqcols = ["geom", "degrade_level", "query_split", "similarity", "template_mode",
                  "record_id", "yaw_true", "pitch_true", "top1_yaw_pred", "top1_pitch_pred",
                  "top1_yaw_err", "top1_pitch_err", "nearest_distance", "margin", "topk10_idx"]
        w = csv.DictWriter(f, fieldnames=pqcols)
        w.writeheader()
        w.writerows(per_query)

    with open(pdb_dir / "l1d3_pdb_retrieval_strata.csv", "w", newline="", encoding="utf-8") as f:
        stcols = ["geom", "degrade_level", "query_split", "similarity", "template_mode",
                  "stratum_type", "stratum", "n", "top1_yaw_cmae", "top1_yaw_hit@30"]
        w = csv.DictWriter(f, fieldnames=stcols)
        w.writeheader()
        w.writerows(strata)

    with open(pdb_dir / "l1d3_pdb_template_manifest.csv", "w", newline="", encoding="utf-8") as f:
        tcols = ["geom", "degrade_level", "n_template", "geoms", "flux_dim", "template_source"]
        w = csv.DictWriter(f, fieldnames=tcols)
        w.writeheader()
        w.writerows(tmpl_manifest)

    # key findings
    md = ["# R118 子任务 B：P-DB / template retrieval 正式评估关键结论\n",
          "最后更新：2026-07-01  \n",
          "**P-DB 是 model-known simulated template retrieval，不是真实反演系统；"
          "top-k 是候选姿态检索，不是 Bayesian posterior，也不是真实观测成功率。**\n"]

    def _get(deg, geom, split, sim, tmode="matched-degraded"):
        for s in summaries:
            if (s["geom"] == geom and s["degrade_level"] == deg and s["query_split"] == split
                    and s["similarity"] == sim and s["template_mode"] == tmode):
                return s
        return None

    md.append("## 1. 多几何单调性（test, matched-degraded, neg-L2, top1 yaw hit@30）\n")
    md.append("| degrade_level | G1 | G3 | G5 |")
    md.append("|:--|--:|--:|--:|")
    for deg in DEG_LEVELS:
        vals = []
        for g in C.GROUPS:
            s = _get(deg, g, "test", "neg-L2")
            vals.append(f"{s['top1_yaw_hit@30']:.3f}" if s else "—")
        md.append(f"| {deg} | " + " | ".join(vals) + " |")
    md.append("")

    md.append("## 2. 相似度对比（test G5 matched-degraded, top1 yaw cMAE° / hit@30）\n")
    md.append("| degrade_level | neg-L2 | cosine | zscore-neg-L2 |")
    md.append("|:--|:--|:--|:--|")
    for deg in DEG_LEVELS:
        cells = []
        for sim in SIMS:
            s = _get(deg, "G5", "test", sim)
            cells.append(f"{s['top1_yaw_cmae']:.2f} / {s['top1_yaw_hit@30']:.3f}" if s else "—")
        md.append(f"| {deg} | " + " | ".join(cells) + " |")
    md.append("")

    md.append("## 3. top-k-best 上界（test G5 matched-degraded, neg-L2, yaw hit@30）\n")
    md.append("| degrade_level | " + " | ".join(f"top{k}" for k in TOP_KS) + " |")
    md.append("|:--|" + "--:|" * len(TOP_KS))
    for deg in DEG_LEVELS:
        s = _get(deg, "G5", "test", "neg-L2")
        if s:
            md.append(f"| {deg} | " + " | ".join(f"{s[f'topk{k}_best_yaw_hit@30']:.3f}" for k in TOP_KS) + " |")
    md.append("")

    md.append("## 4. clean-template 退化迁移探针（test G5, neg-L2, top1 yaw hit@30）\n")
    md.append("template=clean，query=degraded，检验退化观测检索 clean 模板的稳健性。\n")
    md.append("| degrade_level | matched-degraded | clean-template |")
    md.append("|:--|--:|--:|")
    for deg in ["degraded-mild", "degraded-moderate"]:
        sm = _get(deg, "G5", "test", "neg-L2", "matched-degraded")
        sc = _get(deg, "G5", "test", "neg-L2", "clean-template")
        md.append(f"| {deg} | {sm['top1_yaw_hit@30']:.3f} | "
                  f"{sc['top1_yaw_hit@30']:.3f} |" if (sm and sc) else f"| {deg} | — | — |")
    md.append("")

    md.append("## 5. 严格口径与读法\n")
    md.append("```text")
    md.append("- template 只来自 train split，val/test 不进 template 库（无检索泄漏）。")
    md.append("- matched-degraded：template 与 query 同 degrade_level；clean-template：template clean、query degraded。")
    md.append("- zscore-neg-L2 的 z-score 参数仅在 train（template 域）上拟合。")
    md.append("- top1 是单候选检索误差；topk-best 是候选集合内 oracle 上界，不代表可无监督选中。")
    md.append("- 结论只能写为：多观测总光度向量在 model-known 模拟条件下含可检索 yaw 信息，")
    md.append("  且该信息随几何数增加、随退化优雅收缩；不得写成真实观测反演成功率。")
    md.append("```")

    open(pdb_dir / "l1d3_pdb_key_findings.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

    print(f"[B] summary rows={len(summaries)} per_query={len(per_query)} strata={len(strata)}")
    # 打印关键几条
    for deg in DEG_LEVELS:
        s = _get(deg, "G5", "test", "neg-L2")
        if s:
            print(f"  G5 {deg} test neg-L2: top1 cmae={s['top1_yaw_cmae']:.2f} "
                  f"hit@30={s['top1_yaw_hit@30']:.3f} topk10-best hit@30={s['topk10_best_yaw_hit@30']:.3f}")
    print(f"  -> {pdb_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

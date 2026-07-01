#!/usr/bin/env python3
"""
eval_l1d3_conformal.py —— R118 子任务 D：Conformal 正式评估

把 R117 conformal smoke 升级为正式 split-conformal + 分层 Mondrian conformal。
只用 val 校准，test 评估。

评估对象：
  neural: G1/G3/G5 × ocs_only/image_only/joint × clean/mild/moderate × final/best
  P-DB  : G1/G3/G5 × clean/mild/moderate × neg-L2 / zscore-neg-L2

方法：
  1. split-conformal：val yaw circular error 的 (1-α) quantile q；
     test 区间 = pred ± q（角度对称集）；coverage = test true 命中比例；set_size = 2q。
     （有限样本修正 quantile level = ceil((n+1)(1-α))/n）
  2. Mondrian conformal：按 yaw-sector 分层校准；层内 val 样本 < MIN_STRATUM 回退 pooled 并标注。
  3. α ∈ {0.05, 0.10, 0.20}。

严格口径：
  conformal 输出是当前 simulated split 的误差覆盖区间，不是真实天文观测不确定度。
  coverage 接近 target 只说明该 split 下校准自洽，不写成最终概率校准完成。

输出：
  conformal/l1d3_conformal_summary.csv
  conformal/l1d3_conformal_per_sample.csv
  conformal/l1d3_mondrian_summary.csv
  conformal/l1d3_conformal_key_findings.md
"""

import csv

import numpy as np

import l1d3_common as C

ALPHAS = [0.05, 0.10, 0.20]
MIN_STRATUM = 10  # 层内 val 少于此值回退 pooled


def conformal_q(val_err, alpha):
    """有限样本 split-conformal quantile。"""
    n = len(val_err)
    if n == 0:
        return float("nan")
    level = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    return float(np.quantile(val_err, level, method="higher"))


def neural_errors(deg, geom, mode, select):
    """返回 (val_err, test_err, test_yaw_true) 或 None。"""
    v = C.load_neural_samples(deg, "P-INT", geom, mode, "val", select)
    t = C.load_neural_samples(deg, "P-INT", geom, mode, "test", select)
    if v is None or t is None:
        return None
    return (np.asarray(v["yaw_circular_error_deg"]),
            np.asarray(t["yaw_circular_error_deg"]),
            np.asarray(t["yaw_true_deg"]),
            np.asarray(t["record_id"], dtype=object))


def pdb_errors(geom, deg, similarity):
    """P-DB val/test top1 yaw error（matched-degraded）。"""
    tr, va, te, _ = C.get_split_tables(geom, "P-INT")
    X_tmpl = C.flux_matrix(tr, deg)
    yaw_tr = C.yaws(tr)
    transform = None
    if similarity == "zscore-neg-L2":
        transform = C.fit_flux_transform([{"flux_vector": X_tmpl[i]} for i in range(len(X_tmpl))])

    def _err(queries):
        Xq = C.flux_matrix(queries, deg)
        sim = C.retrieval_scores(Xq, X_tmpl, similarity, transform=transform)
        order, _ = C.retrieve_topk(sim, k=1)
        return C.circ_err_between(yaw_tr[order[:, 0]], C.yaws(queries))
    val_err = _err(va)
    test_err = _err(te)
    return val_err, test_err, C.yaws(te), C.record_ids(te)


def main():
    conf_dir = C.OUT / "conformal"
    conf_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    per_sample_rows = []
    mondrian_rows = []

    def _process(tag, deg, geom, mode, select, val_err, test_err, test_yaw, test_rid):
        if val_err is None or len(val_err) == 0 or len(test_err) == 0:
            return
        for a in ALPHAS:
            q = conformal_q(val_err, a)
            cov = float((test_err <= q).mean())
            summary_rows.append({
                "method": tag, "degrade_level": deg, "geom": geom, "mode": mode,
                "select": select, "alpha": a, "q_deg": round(q, 4),
                "val_n": int(len(val_err)), "test_n": int(len(test_err)),
                "coverage": round(cov, 4), "target": round(1 - a, 3),
                "set_size_deg": round(2 * q, 4),
            })
        # per-sample（只存 α=0.10 覆盖标记，控制体积）
        a = 0.10
        q = conformal_q(val_err, a)
        for i in range(len(test_err)):
            per_sample_rows.append({
                "method": tag, "degrade_level": deg, "geom": geom, "mode": mode,
                "select": select, "record_id": test_rid[i],
                "yaw_true": round(float(test_yaw[i]), 3),
                "yaw_err": round(float(test_err[i]), 4),
                "q_deg_a010": round(q, 4),
                "covered_a010": int(test_err[i] <= q),
            })

    # neural
    for deg in C.DEGRADE_ALL:
        for geom in C.GROUPS:
            for mode in C.MODES:
                for select in ("best", "final"):
                    res = neural_errors(deg, geom, mode, select)
                    if res is None:
                        continue
                    val_err, test_err, test_yaw, test_rid = res
                    _process("neural", deg, geom, mode, select, val_err, test_err, test_yaw, test_rid)
                    # Mondrian：需要 val 的 yaw sector -> 重新取 val yaw
                    v = C.load_neural_samples(deg, "P-INT", geom, mode, "val", select)
                    val_yaw = np.asarray(v["yaw_true_deg"])
                    _mondrian("neural", deg, geom, mode, select, val_err, val_yaw,
                              test_err, test_yaw, mondrian_rows)

    # P-DB
    for deg in C.DEGRADE_ALL:
        for geom in C.GROUPS:
            for sim in ["neg-L2", "zscore-neg-L2"]:
                _, va, te, _ = C.get_split_tables(geom, "P-INT")
                val_err, test_err, test_yaw, test_rid = pdb_errors(geom, deg, sim)
                val_yaw = C.yaws(va)
                _process("pdb-" + sim, deg, geom, sim, "-", val_err, test_err, test_yaw, test_rid)
                _mondrian("pdb-" + sim, deg, geom, sim, "-", val_err, val_yaw,
                          test_err, test_yaw, mondrian_rows)

    # 写文件
    with open(conf_dir / "l1d3_conformal_summary.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["method", "degrade_level", "geom", "mode", "select", "alpha", "q_deg",
                "val_n", "test_n", "coverage", "target", "set_size_deg"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(summary_rows)

    with open(conf_dir / "l1d3_conformal_per_sample.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["method", "degrade_level", "geom", "mode", "select", "record_id",
                "yaw_true", "yaw_err", "q_deg_a010", "covered_a010"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(per_sample_rows)

    with open(conf_dir / "l1d3_mondrian_summary.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["method", "degrade_level", "geom", "mode", "select", "alpha", "stratum",
                "val_n", "test_n", "q_deg", "coverage", "target", "set_size_deg", "fallback_pooled"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(mondrian_rows)

    # key findings
    md = ["# R118 子任务 D：Conformal 正式评估关键结论\n",
          "最后更新：2026-07-01  \n",
          "**conformal 输出是当前 simulated split 的误差覆盖区间，不是真实天文观测不确定度；"
          "coverage≈target 只说明该 split 下校准自洽，不是最终概率校准完成。**\n"]

    def _s(method, deg, geom, mode, a, select="best"):
        for r in summary_rows:
            if (r["method"] == method and r["degrade_level"] == deg and r["geom"] == geom
                    and r["mode"] == mode and r["select"] == select and abs(r["alpha"] - a) < 1e-9):
                return r
        return None

    md.append("## 1. split-conformal（test, best, α=0.10）coverage / set_size(°)\n")
    md.append("| method | degrade | G1 | G3 | G5 |")
    md.append("|:--|:--|:--|:--|:--|")
    for method, mode in [("neural", "ocs_only"), ("neural", "image_only"),
                         ("neural", "joint"), ("pdb-neg-L2", None)]:
        for deg in C.DEGRADE_ALL:
            cells = []
            for g in C.GROUPS:
                mm = mode if method == "neural" else "neg-L2"
                sel = "best" if method == "neural" else "-"
                r = _s(method, deg, g, mm, 0.10, sel)
                cells.append(f"{r['coverage']:.3f}/{r['set_size_deg']:.0f}" if r else "—")
            label = f"{method}/{mode}" if mode else method
            md.append(f"| {label} | {deg} | " + " | ".join(cells) + " |")
    md.append("")
    md.append("读法：coverage 应接近 target=0.90；set_size 越小表示该证据链区间越紧（信息量越高）。\n")

    md.append("## 2. set_size 随几何 / 退化变化（neural ocs_only best, α=0.10, set_size°）\n")
    md.append("| degrade | G1 | G3 | G5 |")
    md.append("|:--|--:|--:|--:|")
    for deg in C.DEGRADE_ALL:
        cells = []
        for g in C.GROUPS:
            r = _s("neural", deg, g, "ocs_only", 0.10)
            cells.append(f"{r['set_size_deg']:.1f}" if r else "—")
        md.append(f"| {deg} | " + " | ".join(cells) + " |")
    md.append("")

    md.append("## 3. Mondrian 分层回退情况\n")
    n_fallback = sum(1 for r in mondrian_rows if r["fallback_pooled"])
    md.append(f"- Mondrian 行数：{len(mondrian_rows)}；其中回退 pooled 校准（层内 val<{MIN_STRATUM}）：{n_fallback}\n")
    md.append("详见 `l1d3_mondrian_summary.csv`。\n")

    md.append("## 4. 严格口径\n")
    md.append("```text")
    md.append("- 只用 val 校准 quantile，test 仅评估；有限样本修正 level=ceil((n+1)(1-α))/n。")
    md.append("- coverage 接近 target 只代表该 simulated split 下 conformal 自洽。")
    md.append("- set_size 是 yaw 对称角度区间宽度（2q），不是真实观测置信度。")
    md.append("- P-DB conformal 用 top1 检索误差做 nonconformity，同样只是 split 内覆盖评估。")
    md.append("```")
    open(conf_dir / "l1d3_conformal_key_findings.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

    print(f"[D] summary={len(summary_rows)} per_sample={len(per_sample_rows)} mondrian={len(mondrian_rows)}")
    for mode in C.MODES:
        r = _s("neural", "clean", "G5", mode, 0.10)
        if r:
            print(f"  neural clean G5 {mode} a=0.10: cov={r['coverage']:.3f} set_size={r['set_size_deg']:.1f}")
    r = _s("pdb-neg-L2", "clean", "G5", "neg-L2", 0.10, "-")
    if r:
        print(f"  pdb clean G5 neg-L2 a=0.10: cov={r['coverage']:.3f} set_size={r['set_size_deg']:.1f}")
    print(f"  -> {conf_dir}")
    return 0


def _mondrian(method, deg, geom, mode, select, val_err, val_yaw, test_err, test_yaw, out_rows):
    """按 yaw-sector 分层 Mondrian conformal（α=0.10 与 0.20）。"""
    val_sec = C.yaw_sector(val_yaw)
    test_sec = C.yaw_sector(test_yaw)
    for a in [0.10, 0.20]:
        for s in ["000-090", "090-180", "180-270", "270-360"]:
            vmask = val_sec == s
            tmask = test_sec == s
            if tmask.sum() == 0:
                continue
            fallback = vmask.sum() < MIN_STRATUM
            cal_err = val_err if fallback else val_err[vmask]
            q = conformal_q(cal_err, a)
            cov = float((test_err[tmask] <= q).mean())
            out_rows.append({
                "method": method, "degrade_level": deg, "geom": geom, "mode": mode,
                "select": select, "alpha": a, "stratum": s,
                "val_n": int(vmask.sum()), "test_n": int(tmask.sum()),
                "q_deg": round(q, 4), "coverage": round(cov, 4), "target": round(1 - a, 3),
                "set_size_deg": round(2 * q, 4), "fallback_pooled": fallback,
            })


if __name__ == "__main__":
    raise SystemExit(main())

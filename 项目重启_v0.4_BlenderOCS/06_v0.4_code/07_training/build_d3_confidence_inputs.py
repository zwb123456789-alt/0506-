#!/usr/bin/env python3
"""
build_d3_confidence_inputs.py —— R116 子任务 D：D3/P-DB/conformal 准备

本轮不做正式概率校准，只准备可审计输入 + 两个 smoke：
  1. 置信一致性输入索引：val/test 分开，列出每个 run 的 samples 路径与字段。
  2. P-DB template retrieval smoke：
       - template 库 = train grid 的 L1-G5 多几何总光度向量（clean）
       - query = test 集向量；cosine / L2 相似度 top-k
       - 只报告 top-k candidate 姿态与 yaw/pitch 误差，不写反演成功率
  3. conformal smoke：
       - 用 val 集 yaw circular error 校准 quantile（1-alpha）
       - 在 test 报告 coverage 与 set-size（这里用对称角度区间近似）
       - 明确 smoke，不是最终置信校准

posterior-like 是工程候选分数，不是真实 Bayesian posterior。

输出：
  d3/l1m3_confidence_inputs_index.csv
  d3/pdb_template_retrieval_smoke.csv
  d3/conformal_smoke_summary.md
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from dataset_l1m2_multigeometry import build_multigeometry_table  # noqa: E402
from train_l1m2_multigeometry import split_pint, yaw_circ_err  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

L1M2 = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
BASE = PROJECT_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll"
D3 = BASE / "d3"

GROUPS = ["G1", "G3", "G5"]
MODES = ["ocs_only", "image_only", "joint"]


# ═══════ 1. 置信一致性输入索引 ═══════
def build_index():
    rows = []
    # L1M2 clean runs（val 已由 A1 补齐）
    for prot in ["P-INT", "P-EXT"]:
        for g in GROUPS:
            for m in MODES:
                rd = L1M2 / "runs" / f"{prot}_{g}_{m}_seed42"
                if not rd.exists():
                    continue
                for split in ("val", "test"):
                    for tag in ("final", "best"):
                        npz = rd / f"samples_{split}_{tag}.npz"
                        if npz.exists():
                            rows.append({
                                "source": "R115-clean(11_l1m2)",
                                "protocol": prot, "geom_group": g, "mode": m,
                                "degrade_level": "clean", "split": split, "select": tag,
                                "path": str(npz.relative_to(PROJECT_ROOT)),
                                "fields": "record_id,yaw/pitch true/pred/error,"
                                          "posterior_like_top5,entropy,margin,candidate_grid",
                            })
    # degraded runs
    deg_runs = BASE / "degraded" / "runs"
    if deg_runs.exists():
        for rd in sorted(deg_runs.iterdir()):
            if not rd.is_dir() or rd.name.startswith("smoke"):
                continue
            cfg = json.load(open(rd / "run_config.json", encoding="utf-8"))
            for split in ("val", "test"):
                for tag in ("final", "best"):
                    npz = rd / f"samples_{split}_{tag}.npz"
                    if npz.exists():
                        rows.append({
                            "source": "R116-degraded(12_l1m3)",
                            "protocol": cfg.get("protocol"), "geom_group": cfg.get("geom_group"),
                            "mode": cfg.get("mode"), "degrade_level": cfg.get("degrade_level"),
                            "split": split, "select": tag,
                            "path": str(npz.relative_to(PROJECT_ROOT)),
                            "fields": "record_id,yaw/pitch true/pred/error,"
                                      "posterior_like_top5,entropy,margin,candidate_grid,degrade_level",
                        })
    D3.mkdir(parents=True, exist_ok=True)
    cols = ["source", "protocol", "geom_group", "mode", "degrade_level",
            "split", "select", "path", "fields"]
    with open(D3 / "l1m3_confidence_inputs_index.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    return rows


# ═══════ 2. P-DB template retrieval smoke ═══════
def pdb_smoke():
    """train grid L1-G5 clean 多几何向量作 template；test 向量检索 top-k。"""
    table, geoms = build_multigeometry_table("G5")
    tr, va, te = split_pint(table, seed=42)
    X_tr = np.array([r["flux_vector"] for r in tr], dtype=np.float64)   # [Ntr,5]
    yaw_tr = np.array([r["yaw_deg"] for r in tr])
    pit_tr = np.array([r["pitch_deg"] for r in tr])
    X_te = np.array([r["flux_vector"] for r in te], dtype=np.float64)
    yaw_te = np.array([r["yaw_deg"] for r in te])
    pit_te = np.array([r["pitch_deg"] for r in te])

    # log1p 稳定尺度后做相似度（与训练输入域一致）
    Ltr = np.log1p(X_tr); Lte = np.log1p(X_te)

    def topk_metrics(sim, k=5):
        # sim: [Nte, Ntr]，越大越相似
        order = np.argsort(-sim, axis=1)[:, :k]
        # top-1 姿态误差
        top1 = order[:, 0]
        yce1 = yaw_circ_err(yaw_tr[top1], yaw_te)
        pae1 = np.abs(pit_tr[top1] - pit_te)
        # top-k 内最优（oracle over candidates）
        yce_k = np.min(np.stack([yaw_circ_err(yaw_tr[order[:, j]], yaw_te)
                                 for j in range(k)], axis=1), axis=1)
        return {
            "top1_yaw_cmae": float(yce1.mean()),
            "top1_yaw_hit@30": float((yce1 <= 30).mean()),
            "top1_pitch_mae": float(pae1.mean()),
            "topk_best_yaw_cmae": float(yce_k.mean()),
            "topk_best_yaw_hit@30": float((yce_k <= 30).mean()),
        }

    # cosine
    def norm(a): return a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-12)
    cos = norm(Lte) @ norm(Ltr).T
    # negative L2
    l2 = -(np.sum(Lte**2, 1)[:, None] + np.sum(Ltr**2, 1)[None, :]
           - 2 * Lte @ Ltr.T)

    rows = []
    for name, sim in [("cosine", cos), ("neg_L2", l2)]:
        m = topk_metrics(sim, k=5)
        m["similarity"] = name
        m["n_template"] = len(tr)
        m["n_query_test"] = len(te)
        rows.append(m)

    cols = ["similarity", "n_template", "n_query_test",
            "top1_yaw_cmae", "top1_yaw_hit@30", "top1_pitch_mae",
            "topk_best_yaw_cmae", "topk_best_yaw_hit@30"]
    with open(D3 / "pdb_template_retrieval_smoke.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c) for c in cols})
    return rows


# ═══════ 3. conformal smoke ═══════
def conformal_smoke():
    """用 val yaw circular error 校准 quantile，在 test 报告 coverage/set-size。

    最简单 split conformal：对回归器的 yaw circular error 取 (1-alpha) 分位 q，
    预测区间 = [yaw_pred - q, yaw_pred + q]（角度对称集）。
    coverage = test 中 true 落入区间比例；set_size = 2q。
    使用 L1-G5 ocs_only best（val 已由 A1 补齐）。
    """
    md = ["# Conformal / P-DB 置信一致性 smoke（R116 子任务 D）\n",
          "最后更新：2026-07-01  \n",
          "**这是 smoke，不是最终置信校准。posterior-like 是工程候选分数，非真实 Bayesian posterior。**\n"]

    md.append("## 1. Split-conformal smoke（yaw circular error 区间）\n")
    md.append("方法：val 集校准 yaw circular error 的 (1−α) 分位 q，test 预测区间 = pred ± q，"
              "coverage = test true 命中比例，set_size = 2q（°）。\n")
    md.append("| run | α | q(°) | val_n | test_n | test_coverage | target(1−α) | set_size(°) |")
    md.append("|:--|--:|--:|--:|--:|--:|--:|--:|")

    alphas = [0.1, 0.2]
    targets = [("G5", "ocs_only"), ("G5", "joint"), ("G1", "ocs_only")]
    rows_conf = []
    for g, m in targets:
        rd = L1M2 / "runs" / f"P-INT_{g}_{m}_seed42"
        vp = rd / "samples_val_best.npz"
        tp = rd / "samples_test_best.npz"
        if not (vp.exists() and tp.exists()):
            continue
        val = np.load(vp, allow_pickle=True)
        tst = np.load(tp, allow_pickle=True)
        val_err = val["yaw_circular_error_deg"]
        tst_err = tst["yaw_circular_error_deg"]
        for a in alphas:
            q = float(np.quantile(val_err, 1 - a))
            cov = float((tst_err <= q).mean())
            rows_conf.append({"run": f"P-INT_{g}_{m}", "alpha": a, "q_deg": q,
                              "val_n": int(len(val_err)), "test_n": int(len(tst_err)),
                              "coverage": cov, "target": 1 - a, "set_size_deg": 2 * q})
            md.append(f"| P-INT_{g}_{m} | {a:.2f} | {q:.2f} | {len(val_err)} | "
                      f"{len(tst_err)} | {cov:.3f} | {1-a:.2f} | {2*q:.2f} |")
    md.append("\n读法：coverage 接近 target(1−α) 即 split-conformal 区间在本 smoke 下自洽；"
              "set_size 越小表示该通道置信区间越紧。这是最简单的 split-conformal，"
              "未做条件覆盖、mondrian 分层或 posterior 校准，仅为 D3 后续正式阶段准备接口。\n")

    # P-DB smoke 表引用
    md.append("## 2. P-DB template retrieval smoke\n")
    md.append("见 `pdb_template_retrieval_smoke.csv`：以 train grid L1-G5 clean 多几何总光度向量为 template 库，"
              "test 向量按 cosine / neg-L2 检索 top-k，仅报告 top-1 与 top-k-best 的姿态误差，"
              "不写真实未知目标反演成功率。\n")

    D3.mkdir(parents=True, exist_ok=True)
    open(D3 / "conformal_smoke_summary.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    return rows_conf


def main():
    idx = build_index()
    pdb = pdb_smoke()
    conf = conformal_smoke()
    summary = {
        "task": "R116-D D3/P-DB/conformal preparation + smoke",
        "n_index_rows": len(idx),
        "pdb_smoke": pdb,
        "n_conformal_rows": len(conf),
        "note": "posterior-like 是工程候选分数；conformal/P-DB 均为 smoke，非最终置信校准",
    }
    json.dump(summary, open(D3 / "d3_prep_summary.json", "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"[D3] index_rows={len(idx)} pdb_smoke={len(pdb)} conformal_rows={len(conf)}")
    for r in pdb:
        print(f"  P-DB {r['similarity']}: top1 yaw_cmae={r['top1_yaw_cmae']:.2f} "
              f"hit@30={r['top1_yaw_hit@30']:.3f} | topk-best hit@30={r['topk_best_yaw_hit@30']:.3f}")
    print(f"  -> {D3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
postprocess_l1m2_metrics.py —— 1C-L1M2 矩阵汇总与分析维生成

读取 v0.4_results/11_l1m2_multigeometry_ocs/runs/*/ 下各 run 的
metrics_test_{final,best}.json 与 samples_test_{final,best}.npz，生成 R114 §8 交付：
  l1m2_run_matrix.csv / .json
  l1m2_metrics_summary_final.csv / _best.csv
  l1m2_gain_curve_G1_G3_G5.csv / .md
  l1m2_confidence_consistency_summary.csv
  l1m2_complementarity_summary.csv   (image vs ocs vs joint top-k overlap / disagreement)
  l1m2_postprocess_summary.json

分析维（执行框架 §3）：
  D2 互补性：同 split 下 image/ocs/joint 的 per-attitude 误差与 top-1 overlap、disagreement
  D3 置信一致性：entropy/margin 与 error 的关系（按分位）
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
RUNS = BASE / "runs"

GROUPS = ["G1", "G3", "G5"]
MODES = ["ocs_only", "image_only", "joint"]
PROTOCOL = "P-INT"

METRIC_KEYS = ["yaw_circular_mae_deg", "yaw_median_ae_deg", "yaw_p90_ae_deg",
               "yaw_hit@5", "yaw_hit@10", "yaw_hit@30",
               "yaw_coarse45_acc", "yaw_coarse90_acc", "yaw_within_1bin_sentinel",
               "pitch_mae_deg", "pitch_median_ae_deg", "pitch_hit@5", "pitch_hit@10"]


def run_name(group, mode, seed=42):
    return f"{PROTOCOL}_{group}_{mode}_seed{seed}"


def load_metrics(group, mode, tag, seed=42):
    p = RUNS / run_name(group, mode, seed) / f"metrics_test_{tag}.json"
    if not p.exists():
        return None
    return json.load(open(p, encoding="utf-8"))


def load_samples(group, mode, tag, seed=42):
    p = RUNS / run_name(group, mode, seed) / f"samples_test_{tag}.npz"
    if not p.exists():
        return None
    return np.load(p, allow_pickle=True)


def build_run_matrix(seed=42):
    rows = []
    for tag in ("final", "best"):
        for g in GROUPS:
            for m in MODES:
                met = load_metrics(g, m, tag, seed)
                if met is None:
                    rows.append({"select": tag, "geom_group": g, "mode": m,
                                 "status": "MISSING"})
                    continue
                row = {"select": tag, "geom_group": g, "mode": m, "status": "OK"}
                for k in METRIC_KEYS:
                    row[k] = met.get(k)
                rows.append(row)
    return rows


def write_run_matrix(rows):
    cols = ["select", "geom_group", "mode", "status"] + METRIC_KEYS
    with open(BASE / "l1m2_run_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    json.dump(rows, open(BASE / "l1m2_run_matrix.json", "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    # 分 final/best summary
    for tag in ("final", "best"):
        with open(BASE / f"l1m2_metrics_summary_{tag}.csv", "w", newline="",
                  encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                if r["select"] == tag:
                    w.writerow({c: r.get(c, "") for c in cols})


def write_gain_curve(rows):
    """G1->G3->G5 增益曲线，每 mode 一行块。主指标 yaw_circular_mae_deg。"""
    gain_rows = []
    for tag in ("final", "best"):
        for m in MODES:
            entry = {"select": tag, "mode": m}
            base = None
            for g in GROUPS:
                r = next((x for x in rows if x["select"] == tag and
                          x["geom_group"] == g and x["mode"] == m and
                          x.get("status") == "OK"), None)
                cmae = r["yaw_circular_mae_deg"] if r else None
                entry[f"{g}_cmae"] = cmae
                if g == "G1":
                    base = cmae
            # 增益 = G1 - Gx（cMAE 下降为正增益）
            for g in GROUPS:
                cx = entry.get(f"{g}_cmae")
                entry[f"{g}_gain_vs_G1"] = (round(base - cx, 3)
                                            if (base is not None and cx is not None)
                                            else None)
            gain_rows.append(entry)
    cols = ["select", "mode", "G1_cmae", "G3_cmae", "G5_cmae",
            "G1_gain_vs_G1", "G3_gain_vs_G1", "G5_gain_vs_G1"]
    with open(BASE / "l1m2_gain_curve_G1_G3_G5.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in gain_rows:
            w.writerow({c: r.get(c, "") for c in cols})
    # md
    md = ["# L1(M2) G1→G3→G5 增益曲线（yaw circular MAE，单位°）\n",
          "增益 = G1_cMAE − Gx_cMAE（正值=多几何降低误差）\n"]
    for tag in ("final", "best"):
        md.append(f"## {tag}\n")
        md.append("| mode | G1 | G3 | G5 | G3增益 | G5增益 |")
        md.append("|:--|--:|--:|--:|--:|--:|")
        for m in MODES:
            e = next(x for x in gain_rows if x["select"] == tag and x["mode"] == m)
            def fmt(v): return f"{v:.2f}" if isinstance(v, (int, float)) else "—"
            md.append(f"| {m} | {fmt(e.get('G1_cmae'))} | {fmt(e.get('G3_cmae'))} | "
                      f"{fmt(e.get('G5_cmae'))} | {fmt(e.get('G3_gain_vs_G1'))} | "
                      f"{fmt(e.get('G5_gain_vs_G1'))} |")
        md.append("")
    open(BASE / "l1m2_gain_curve_G1_G3_G5.md", "w", encoding="utf-8").write("\n".join(md))
    return gain_rows


def write_confidence_consistency(seed=42):
    """D3：每 run 的 entropy/margin 分位 vs error 关系。"""
    rows = []
    for tag in ("final", "best"):
        for g in GROUPS:
            for m in MODES:
                s = load_samples(g, m, tag, seed)
                if s is None:
                    continue
                yce = s["yaw_circular_error_deg"]
                ent = s["entropy"]; mar = s["margin"]
                # 低/高 margin 半区误差对比
                med_m = np.median(mar)
                hi = mar >= med_m; lo = mar < med_m
                med_e = np.median(ent)
                lo_ent = ent < med_e; hi_ent = ent >= med_e
                rows.append({
                    "select": tag, "geom_group": g, "mode": m,
                    "n": int(len(yce)),
                    "entropy_mean": round(float(ent.mean()), 4),
                    "margin_mean": round(float(mar.mean()), 5),
                    "yaw_cmae_all": round(float(yce.mean()), 3),
                    "yaw_cmae_high_margin": round(float(yce[hi].mean()), 3) if hi.any() else None,
                    "yaw_cmae_low_margin": round(float(yce[lo].mean()), 3) if lo.any() else None,
                    "yaw_cmae_low_entropy": round(float(yce[lo_ent].mean()), 3) if lo_ent.any() else None,
                    "yaw_cmae_high_entropy": round(float(yce[hi_ent].mean()), 3) if hi_ent.any() else None,
                })
    if not rows:
        return rows
    cols = list(rows[0].keys())
    with open(BASE / "l1m2_confidence_consistency_summary.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    return rows


def write_complementarity(seed=42):
    """D2：同 split / 同几何组下，image vs ocs vs joint 的 per-attitude 比较。

    用 record_id 对齐 test 集，计算：
      - 各通道 top-1 命中（yaw_circular_error<=30）比例
      - image vs ocs 的 disagreement（一个对一个错）
      - joint 是否优于 max(image,ocs)
    """
    rows = []
    for tag in ("final", "best"):
        for g in GROUPS:
            chan = {}
            for m in MODES:
                s = load_samples(g, m, tag, seed)
                if s is None:
                    continue
                d = {rid: err for rid, err in
                     zip(s["record_id"], s["yaw_circular_error_deg"])}
                chan[m] = d
            if len(chan) < 2:
                continue
            common = set.intersection(*[set(d.keys()) for d in chan.values()])
            common = sorted(common)
            def hit(m): return np.array([chan[m][r] <= 30 for r in common])
            entry = {"select": tag, "geom_group": g, "n_common": len(common)}
            for m in MODES:
                if m in chan:
                    entry[f"{m}_hit30"] = round(float(hit(m).mean()), 4)
            if "image_only" in chan and "ocs_only" in chan:
                hi, ho = hit("image_only"), hit("ocs_only")
                entry["img_only_correct_ocs_wrong"] = round(float((hi & ~ho).mean()), 4)
                entry["ocs_only_correct_img_wrong"] = round(float((ho & ~hi).mean()), 4)
                entry["both_correct"] = round(float((hi & ho).mean()), 4)
                entry["both_wrong"] = round(float((~hi & ~ho).mean()), 4)
            if "joint" in chan and "image_only" in chan and "ocs_only" in chan:
                hj = hit("joint")
                best_single = np.maximum(hit("image_only"), hit("ocs_only"))
                entry["joint_hit30"] = round(float(hj.mean()), 4)
                entry["joint_minus_best_single_hit30"] = round(
                    float(hj.mean() - best_single.mean()), 4)
            rows.append(entry)
    if not rows:
        return rows
    # 列并集
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(BASE / "l1m2_complementarity_summary.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    return rows


def main():
    rows = build_run_matrix()
    write_run_matrix(rows)
    gain = write_gain_curve(rows)
    cc = write_confidence_consistency()
    comp = write_complementarity()

    n_ok = sum(1 for r in rows if r.get("status") == "OK")
    summary = {
        "task": "1C-L1M2 postprocess metrics aggregation",
        "n_run_rows": len(rows),
        "n_ok": n_ok,
        "n_missing": len(rows) - n_ok,
        "groups": GROUPS, "modes": MODES, "protocol": PROTOCOL,
        "outputs": [
            "l1m2_run_matrix.csv", "l1m2_run_matrix.json",
            "l1m2_metrics_summary_final.csv", "l1m2_metrics_summary_best.csv",
            "l1m2_gain_curve_G1_G3_G5.csv", "l1m2_gain_curve_G1_G3_G5.md",
            "l1m2_confidence_consistency_summary.csv",
            "l1m2_complementarity_summary.csv",
        ],
        "n_confidence_rows": len(cc),
        "n_complementarity_rows": len(comp),
    }
    json.dump(summary, open(BASE / "l1m2_postprocess_summary.json", "w",
                            encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"[OK] run_matrix rows={len(rows)} ok={n_ok} missing={len(rows)-n_ok}")
    print(f"[OK] gain curve / confidence({len(cc)}) / complementarity({len(comp)}) 已生成")
    print(f"[OK] summary -> {BASE / 'l1m2_postprocess_summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

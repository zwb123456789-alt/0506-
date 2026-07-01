#!/usr/bin/env python3
"""
postprocess_l1m3_mroll_metrics.py —— R116 子任务 B/C 汇总

聚合 v0.4_results/12_l1m3_degraded_mroll/ 下 degraded 与 mroll 的 run 结果。

degraded 部分：
  - l1m3_degraded_run_matrix.csv
  - l1m3_degraded_metrics_summary_final.csv / _best.csv
  - l1m3_degraded_gain_and_drop_summary.md
      clean 引用 R115（11_l1m2 的 metrics_test），degraded 为本轮 12_l1m3 新跑。
      标注每个 clean 数字的来源路径。

mroll 部分（若存在 run）：
  - mroll_run_matrix.csv
  - mroll_metrics_summary_best.csv
  - mroll_roll_sensitivity_summary.md

用法：
  python postprocess_l1m3_mroll_metrics.py            # 全部
  python postprocess_l1m3_mroll_metrics.py --degraded-only
  python postprocess_l1m3_mroll_metrics.py --mroll-only
"""

import argparse
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
L1M2 = ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
BASE = ROOT / "v0.4_results" / "12_l1m3_degraded_mroll"
DEG = BASE / "degraded"
MROLL = BASE / "mroll"

GROUPS = ["G1", "G3", "G5"]
MODES = ["ocs_only", "image_only", "joint"]
LEVELS = ["degraded-mild", "degraded-moderate"]

METRIC_KEYS = ["yaw_circular_mae_deg", "yaw_median_ae_deg", "yaw_p90_ae_deg",
               "yaw_hit@5", "yaw_hit@10", "yaw_hit@30",
               "yaw_coarse45_acc", "yaw_coarse90_acc",
               "pitch_mae_deg", "pitch_hit@10"]


def load_metrics(run_dir, tag):
    p = run_dir / f"metrics_test_{tag}.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def clean_ref(group, mode, tag):
    """R115 clean 基线（来源 11_l1m2）。"""
    p = L1M2 / "runs" / f"P-INT_{group}_{mode}_seed42" / f"metrics_test_{tag}.json"
    if not p.exists():
        return None, str(p)
    return json.load(open(p, encoding="utf-8")), str(p.relative_to(ROOT))


# ═══════ degraded ═══════
def degraded_matrix():
    rows = []
    for tag in ("final", "best"):
        for lvl in ["clean"] + LEVELS:
            for g in GROUPS:
                for m in MODES:
                    if lvl == "clean":
                        met, src = clean_ref(g, m, tag)
                        status = "OK(R115-ref)" if met else "MISSING"
                    else:
                        rd = DEG / "runs" / f"{lvl}_P-INT_{g}_{m}_seed42"
                        met = load_metrics(rd, tag)
                        src = str(rd.relative_to(ROOT)) if met else "not-run"
                        status = "OK" if met else "not-run"
                    row = {"select": tag, "degrade_level": lvl, "geom_group": g,
                           "mode": m, "status": status, "source": src}
                    if met:
                        for k in METRIC_KEYS:
                            row[k] = met.get(k)
                    rows.append(row)
    return rows


def write_degraded(rows):
    DEG.mkdir(parents=True, exist_ok=True)
    cols = ["select", "degrade_level", "geom_group", "mode", "status",
            "source"] + METRIC_KEYS
    with open(DEG / "l1m3_degraded_run_matrix.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    for tag in ("final", "best"):
        with open(DEG / f"l1m3_degraded_metrics_summary_{tag}.csv", "w",
                  newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                if r["select"] == tag and r.get("status", "").startswith("OK"):
                    w.writerow({c: r.get(c, "") for c in cols})

    # gain-and-drop md
    md = ["# L1M3 degraded 真实性轴：增益与退化 drop 汇总（R116 子任务 B）\n",
          "最后更新：2026-07-01  \n",
          "口径：yaw circular MAE（°）与 hit@30。clean 引用 R115（`11_l1m2`），",
          "degraded 为本轮 `12_l1m3_degraded_mroll` 新跑。\n"]
    for tag in ("best", "final"):
        md.append(f"## {tag} 口径\n")
        # OCS-only 多几何增益（各 level 下 G1->G3->G5）
        md.append("### OCS-only 多几何增益（各退化等级下 G1→G3→G5 yaw cMAE）\n")
        md.append("| 退化等级 | G1 | G3 | G5 | G5相对G1增益 | 来源 |")
        md.append("|:--|--:|--:|--:|--:|:--|")
        for lvl in ["clean"] + LEVELS:
            vals = {}
            for g in GROUPS:
                r = next((x for x in rows if x["select"] == tag and
                          x["degrade_level"] == lvl and x["geom_group"] == g and
                          x["mode"] == "ocs_only" and str(x.get("status","")).startswith("OK")), None)
                vals[g] = r.get("yaw_circular_mae_deg") if r else None
            def f2(v): return f"{v:.2f}" if isinstance(v, (int, float)) else "—"
            gain = (round(vals["G1"] - vals["G5"], 2)
                    if vals["G1"] is not None and vals["G5"] is not None else None)
            src = "R115 11_l1m2" if lvl == "clean" else "12_l1m3"
            md.append(f"| {lvl} | {f2(vals['G1'])} | {f2(vals['G3'])} | {f2(vals['G5'])} | "
                      f"{f2(gain)} | {src} |")
        md.append("")
        # image/joint clean vs degraded drop（G1/G5）
        md.append("### image_only / joint 退化 drop（clean→degraded，yaw hit@30）\n")
        md.append("| geom | mode | clean hit@30 | mild hit@30 | moderate hit@30 |")
        md.append("|:--|:--|--:|--:|--:|")
        for g in ["G1", "G5"]:
            for m in ["image_only", "joint"]:
                def gethit(lvl):
                    r = next((x for x in rows if x["select"] == tag and
                              x["degrade_level"] == lvl and x["geom_group"] == g and
                              x["mode"] == m and str(x.get("status","")).startswith("OK")), None)
                    return r.get("yaw_hit@30") if r else None
                def f3(v): return f"{v:.3f}" if isinstance(v, (int, float)) else "—"
                md.append(f"| {g} | {m} | {f3(gethit('clean'))} | "
                          f"{f3(gethit('degraded-mild'))} | {f3(gethit('degraded-moderate'))} |")
        md.append("")
    open(DEG / "l1m3_degraded_gain_and_drop_summary.md", "w",
         encoding="utf-8").write("\n".join(md) + "\n")


# ═══════ M-roll ═══════
def mroll_matrix():
    runs_dir = MROLL / "runs"
    if not runs_dir.exists():
        return []
    rows = []
    for rd in sorted(runs_dir.iterdir()):
        if not rd.is_dir() or rd.name.startswith("smoke"):
            continue
        cfg_p = rd / "run_config.json"
        if not cfg_p.exists():
            continue
        cfg = json.load(open(cfg_p, encoding="utf-8"))
        for tag in ("final", "best"):
            met = load_metrics(rd, tag)
            if met is None:
                continue
            row = {"select": tag, "run": rd.name,
                   "roll_deg": cfg.get("roll_deg"),
                   "geom_group": cfg.get("geom_group"),
                   "mode": cfg.get("mode"),
                   "protocol": cfg.get("protocol"),
                   "n_test": cfg.get("n_test"),
                   "subset": cfg.get("subset_note", "")}
            for k in METRIC_KEYS:
                row[k] = met.get(k)
            rows.append(row)
    return rows


def write_mroll(rows):
    MROLL.mkdir(parents=True, exist_ok=True)
    if not rows:
        # 生成占位说明（未跑正式 M-roll 训练）
        return False
    cols = ["select", "run", "roll_deg", "geom_group", "mode", "protocol",
            "n_test", "subset"] + METRIC_KEYS
    with open(MROLL / "mroll_run_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    with open(MROLL / "mroll_metrics_summary_best.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            if r["select"] == "best":
                w.writerow({c: r.get(c, "") for c in cols})
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--degraded-only", action="store_true")
    ap.add_argument("--mroll-only", action="store_true")
    args = ap.parse_args()

    do_deg = not args.mroll_only
    do_mroll = not args.degraded_only

    summary = {"task": "R116 B/C postprocess"}
    if do_deg:
        drows = degraded_matrix()
        write_degraded(drows)
        n_ok = sum(1 for r in drows if str(r.get("status", "")).startswith("OK"))
        summary["degraded_rows"] = len(drows)
        summary["degraded_ok"] = n_ok
        print(f"[degraded] rows={len(drows)} ok={n_ok}")
    if do_mroll:
        mrows = mroll_matrix()
        has = write_mroll(mrows)
        summary["mroll_rows"] = len(mrows)
        summary["mroll_has_runs"] = has
        print(f"[mroll] rows={len(mrows)} has_runs={has}")

    json.dump(summary, open(BASE / "l1m3_mroll_postprocess_summary.json", "w",
                            encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"[OK] -> {BASE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

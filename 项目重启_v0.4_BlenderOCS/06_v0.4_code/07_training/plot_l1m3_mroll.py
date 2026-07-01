#!/usr/bin/env python3
"""
plot_l1m3_mroll.py —— R116 B/C 图表生成

生成：
  degraded/figures/l1m3_degraded_ocs_gain_curve.png   各退化等级 OCS-only G1/G3/G5 增益
  degraded/figures/l1m3_degraded_hit30_bars.png       clean vs degraded hit@30
  mroll/figures/mroll_roll_sensitivity.png            image_only roll 敏感性（若有数据）

只依赖已生成的 CSV，不重训。
"""

import csv
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "v0.4_results" / "12_l1m3_degraded_mroll"
DEG = BASE / "degraded"
MROLL = BASE / "mroll"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def read_csv(p):
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plot_degraded_gain():
    rows = read_csv(DEG / "l1m3_degraded_metrics_summary_best.csv")
    if not rows:
        print("[skip] degraded best summary 不存在")
        return
    levels = ["clean", "degraded-mild", "degraded-moderate"]
    groups = ["G1", "G3", "G5"]
    gx = [1, 3, 5]
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = {"clean": "tab:blue", "degraded-mild": "tab:orange",
              "degraded-moderate": "tab:red"}
    for lvl in levels:
        ys = []
        for g in groups:
            r = next((x for x in rows if x["degrade_level"] == lvl and
                      x["geom_group"] == g and x["mode"] == "ocs_only"), None)
            ys.append(float(r["yaw_circular_mae_deg"]) if r and r.get("yaw_circular_mae_deg") else np.nan)
        ax.plot(gx, ys, "o-", label=lvl, color=colors.get(lvl), linewidth=2, markersize=8)
    ax.set_xlabel("观测几何数 (L1-G1 / G3 / G5)")
    ax.set_ylabel("yaw circular MAE (°)")
    ax.set_title("OCS-only 多几何增益 × 退化等级 (P-INT, best-val)")
    ax.set_xticks(gx); ax.set_xticklabels(["G1", "G3", "G5"])
    ax.legend(); ax.grid(alpha=0.3)
    (DEG / "figures").mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(DEG / "figures" / "l1m3_degraded_ocs_gain_curve.png", dpi=130)
    plt.close(fig)
    print("[OK] degraded gain curve")


def plot_degraded_hit30():
    rows = read_csv(DEG / "l1m3_degraded_metrics_summary_best.csv")
    if not rows:
        return
    levels = ["clean", "degraded-mild", "degraded-moderate"]
    configs = [("G1", "image_only"), ("G5", "image_only"),
               ("G1", "joint"), ("G5", "joint"),
               ("G1", "ocs_only"), ("G5", "ocs_only")]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(configs))
    w = 0.25
    for i, lvl in enumerate(levels):
        ys = []
        for g, m in configs:
            r = next((x for x in rows if x["degrade_level"] == lvl and
                      x["geom_group"] == g and x["mode"] == m), None)
            ys.append(float(r["yaw_hit@30"]) if r and r.get("yaw_hit@30") else np.nan)
        ax.bar(x + (i - 1) * w, ys, w, label=lvl)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{g}\n{m}" for g, m in configs], fontsize=8)
    ax.set_ylabel("yaw hit@30")
    ax.set_title("clean vs degraded：yaw hit@30 (P-INT, best-val)")
    ax.legend(); ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(DEG / "figures" / "l1m3_degraded_hit30_bars.png", dpi=130)
    plt.close(fig)
    print("[OK] degraded hit30 bars")


def plot_mroll():
    rows = read_csv(MROLL / "mroll_metrics_summary_best.csv")
    rows = [r for r in rows if r.get("n") and int(r["n"]) > 0]
    if not rows:
        print("[skip] mroll summary 无数据")
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    for g in ["G1", "G5"]:
        gr = [r for r in rows if r["geom_group"] == g]
        gr = sorted(gr, key=lambda r: int(r["roll_deg"]))
        xs = [int(r["roll_deg"]) for r in gr]
        ys = [float(r["yaw_cmae"]) for r in gr]
        ax.plot(xs, ys, "o-", label=f"{g} image_only", linewidth=2, markersize=8)
    ax.set_xlabel("roll (°)")
    ax.set_ylabel("yaw circular MAE (°)")
    ax.set_title("M-roll 边界探针：image_only clean 模型 roll 敏感性")
    ax.legend(); ax.grid(alpha=0.3)
    (MROLL / "figures").mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(MROLL / "figures" / "mroll_roll_sensitivity.png", dpi=130)
    plt.close(fig)
    print("[OK] mroll sensitivity")


def main():
    plot_degraded_gain()
    plot_degraded_hit30()
    plot_mroll()
    return 0


if __name__ == "__main__":
    sys.exit(main())

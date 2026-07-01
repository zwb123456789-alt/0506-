# -*- coding: utf-8 -*-
"""
plot_l1m2_gain_curve.py —— G1->G3->G5 增益曲线与互补性可视化（英文标注，论文级）
输出 PNG 到 11_l1m2_multigeometry_ocs/figures/
"""
import csv
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
FIG = BASE / "figures"
FIG.mkdir(parents=True, exist_ok=True)

GROUPS = ["G1", "G3", "G5"]
NGEOM = {"G1": 1, "G3": 3, "G5": 5}
MODES = ["ocs_only", "image_only", "joint"]
COLORS = {"ocs_only": "#d62728", "image_only": "#1f77b4", "joint": "#2ca02c"}


def load_matrix(tag):
    rows = list(csv.DictReader(open(BASE / f"l1m2_metrics_summary_{tag}.csv", encoding="utf-8")))
    d = {}
    for r in rows:
        if r.get("status") != "OK":
            continue
        d[(r["geom_group"], r["mode"])] = r
    return d


def fig_gain(tag):
    d = load_matrix(tag)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    # (a) yaw circular MAE
    ax = axes[0]
    x = [NGEOM[g] for g in GROUPS]
    for m in MODES:
        y = [float(d[(g, m)]["yaw_circular_mae_deg"]) for g in GROUPS if (g, m) in d]
        ax.plot(x[:len(y)], y, "o-", color=COLORS[m], label=m, lw=2, ms=7)
    ax.set_xlabel("Number of observation geometries (G)")
    ax.set_ylabel("Yaw circular MAE (deg)")
    ax.set_title(f"(a) Yaw error vs geometry count [{tag}]")
    ax.set_xticks([1, 3, 5]); ax.grid(alpha=0.3); ax.legend()
    # (b) yaw hit@30
    ax = axes[1]
    for m in MODES:
        y = [float(d[(g, m)]["yaw_hit@30"]) for g in GROUPS if (g, m) in d]
        ax.plot(x[:len(y)], y, "s-", color=COLORS[m], label=m, lw=2, ms=7)
    ax.set_xlabel("Number of observation geometries (G)")
    ax.set_ylabel("Yaw hit@30deg (fraction)")
    ax.set_title(f"(b) Yaw hit@30 vs geometry count [{tag}]")
    ax.set_xticks([1, 3, 5]); ax.grid(alpha=0.3); ax.legend()
    fig.suptitle(f"L1(M2) multi-geometry OCS gain curve (clean / P-INT), select={tag}",
                 fontsize=12)
    fig.tight_layout()
    out = FIG / f"l1m2_gain_curve_{tag}.png"
    fig.savefig(out, dpi=200); plt.close(fig)
    return out


def fig_complementarity():
    rows = list(csv.DictReader(open(BASE / "l1m2_complementarity_summary.csv", encoding="utf-8")))
    sel = [r for r in rows if r["select"] == "best"]
    fig, ax = plt.subplots(figsize=(7, 4.3))
    x = np.arange(len(GROUPS)); w = 0.25
    for i, m in enumerate(MODES):
        key = f"{m}_hit30"
        y = []
        for g in GROUPS:
            r = next((rr for rr in sel if rr["geom_group"] == g), None)
            y.append(float(r[key]) if (r and r.get(key)) else 0.0)
        ax.bar(x + (i - 1) * w, y, w, color=COLORS[m], label=m)
    ax.set_xticks(x); ax.set_xticklabels([f"{g}\n(G={NGEOM[g]})" for g in GROUPS])
    ax.set_ylabel("Yaw hit@30deg (fraction)")
    ax.set_title("Channel complementarity: hit@30 by channel x geometry group (best)")
    ax.set_ylim(0, 1.05); ax.grid(alpha=0.3, axis="y"); ax.legend()
    fig.tight_layout()
    out = FIG / "l1m2_complementarity_hit30.png"
    fig.savefig(out, dpi=200); plt.close(fig)
    return out


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    outs = [fig_gain("final"), fig_gain("best"), fig_complementarity()]
    for o in outs:
        print(f"[OK] {o}")

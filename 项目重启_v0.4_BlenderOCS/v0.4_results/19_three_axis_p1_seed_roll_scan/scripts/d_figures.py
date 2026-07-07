# -*- coding: utf-8 -*-
"""
d_figures.py —— R131 子任务 D：P1 seed-roll scan smoke 图表
产出（png+pdf）：
  figures/p1_seed_roll_brightness_curves —— 每 seed 的 OCS(roll) 曲线
  figures/p1_category_roll_sensitivity_panel —— 类别 × roll_sensitivity 条形
  figures/p1_roll_heatmap_seed_by_roll —— seed×roll 的 rel_delta 热图
"""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PKG = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\v0.4_results\19_three_axis_p1_seed_roll_scan")
T = PKG / "tables"
FIG = PKG / "figures"
ALL_ROLLS = [-60, -45, -30, -15, 0, 15, 30, 45, 60]

# 读 roll_curve
curve = list(csv.DictReader(open(T / "p1_roll_curve_metrics.csv", encoding="utf-8")))
sens = list(csv.DictReader(open(T / "p1_roll_sensitivity_summary.csv", encoding="utf-8")))

seeds_order = []
for r in curve:
    key = (r["seed_record_id"], r["category"])
    if key not in seeds_order:
        seeds_order.append(key)

def seed_label(rid):
    return rid.split("__")[-1] if "__" in rid else rid

# --- Fig 1: OCS(roll) curves ---
fig, ax = plt.subplots(figsize=(9, 5.5))
cmap = plt.get_cmap("tab20")
for i, (rid, cat) in enumerate(seeds_order):
    xs, ys = [], []
    for r in curve:
        if r["seed_record_id"] == rid:
            xs.append(int(r["roll"])); ys.append(float(r["ocs_total"]))
    order = np.argsort(xs); xs = np.array(xs)[order]; ys = np.array(ys)[order]
    ax.plot(xs, ys, "-o", ms=3, color=cmap(i % 20), label=f"{cat}:{seed_label(rid)}")
ax.set_xlabel("roll (deg)"); ax.set_ylabel("OCS total")
ax.set_title("P1 smoke: OCS total vs roll (phase63/L1-G1, roll=0 reuses 01_fullrun)")
ax.axvline(0, color="gray", ls="--", lw=0.8)
ax.legend(fontsize=6, ncol=2, loc="upper right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "p1_seed_roll_brightness_curves.png", dpi=140)
fig.savefig(FIG / "p1_seed_roll_brightness_curves.pdf")
plt.close(fig)

# --- Fig 2: category roll sensitivity panel ---
cats, scores, ocs0s = [], [], []
for r in sens:
    cats.append(f"{r['category']}\n{seed_label(r['seed_record_id'])}")
    scores.append(float(r["roll_sensitivity_score"]))
    ocs0s.append(float(r["ocs_roll0"]))
order = np.argsort(scores)
cats = [cats[i] for i in order]; scores = [scores[i] for i in order]; ocs0s = [ocs0s[i] for i in order]
fig, ax = plt.subplots(figsize=(9, 6))
colors = plt.get_cmap("viridis")(np.array(ocs0s) / max(ocs0s))
bars = ax.barh(range(len(cats)), scores, color=colors)
ax.set_yticks(range(len(cats))); ax.set_yticklabels(cats, fontsize=7)
ax.set_xlabel("roll_sensitivity_score = (max-min)/mean of OCS over rolls")
ax.set_title("P1 smoke: roll sensitivity by seed (bar color = OCS at roll0)")
sm = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(vmin=0, vmax=max(ocs0s)))
fig.colorbar(sm, ax=ax, label="OCS(roll=0)")
ax.grid(alpha=0.3, axis="x")
fig.tight_layout()
fig.savefig(FIG / "p1_category_roll_sensitivity_panel.png", dpi=140)
fig.savefig(FIG / "p1_category_roll_sensitivity_panel.pdf")
plt.close(fig)

# --- Fig 3: heatmap seed × roll (rel_delta_pct) ---
mat = np.full((len(seeds_order), len(ALL_ROLLS)), np.nan)
ridx = {rid: i for i, (rid, _) in enumerate(seeds_order)}
cidx = {roll: j for j, roll in enumerate(ALL_ROLLS)}
for r in curve:
    i = ridx[r["seed_record_id"]]; j = cidx[int(r["roll"])]
    mat[i, j] = float(r["rel_delta_pct"])
fig, ax = plt.subplots(figsize=(8, 6.5))
vmax = np.nanmax(np.abs(mat))
im = ax.imshow(mat, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
ax.set_xticks(range(len(ALL_ROLLS))); ax.set_xticklabels(ALL_ROLLS)
ax.set_yticks(range(len(seeds_order)))
ax.set_yticklabels([f"{c}:{seed_label(rid)}" for rid, c in seeds_order], fontsize=7)
ax.set_xlabel("roll (deg)"); ax.set_title("P1 smoke: OCS rel change vs roll=0 (%)")
for i in range(len(seeds_order)):
    for j in range(len(ALL_ROLLS)):
        if not np.isnan(mat[i, j]):
            ax.text(j, i, f"{mat[i,j]:.0f}", ha="center", va="center", fontsize=5.5,
                    color="black")
fig.colorbar(im, ax=ax, label="rel delta OCS (%)")
fig.tight_layout()
fig.savefig(FIG / "p1_roll_heatmap_seed_by_roll.png", dpi=140)
fig.savefig(FIG / "p1_roll_heatmap_seed_by_roll.pdf")
plt.close(fig)

print("[OK] 3 figures written (png+pdf)")

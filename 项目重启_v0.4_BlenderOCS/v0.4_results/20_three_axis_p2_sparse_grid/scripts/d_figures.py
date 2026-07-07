# -*- coding: utf-8 -*-
"""
d_figures.py —— R133 子任务 D：P2 sparse 3-axis grid 图表

产出（png+pdf）：
  figures/p2_sparse_grid_brightness_map        —— 各区域 yaw×pitch 亮度图(roll=0)+roll稳健性
  figures/p2_sparse_grid_information_proxy_map  —— 各区域 yaw×pitch neighbor_contrast 信息图
  figures/p2_region_roll_sensitivity_panel      —— 区域×roll敏感度面板 + 效用条形
  figures/p2_brightness_vs_information_scatter   —— 亮度 vs 信息 proxy 散点(解耦可视化)

只读 tables/ 下已生成的指标表，不重算渲染。
"""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PKG = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\v0.4_results\20_three_axis_p2_sparse_grid")
T = PKG / "tables"
FIG = PKG / "figures"
ROLLS = [-60, -45, -30, -15, 0, 15, 30, 45, 60]

metrics = list(csv.DictReader(open(T / "p2_sparse_grid_metrics.csv", encoding="utf-8")))
region_sum = list(csv.DictReader(open(T / "p2_region_summary.csv", encoding="utf-8")))

# 组织 pose 级数据
REGIONS = []
for r in metrics:
    if r["region"] not in REGIONS:
        REGIONS.append(r["region"])
REGIONS = sorted(REGIONS)  # 稳定顺序


def pose_map(region, roll, field):
    """返回 {(yaw,pitch): value} for one region & roll."""
    d = {}
    for r in metrics:
        if r["region"] == region and int(r["roll"]) == roll:
            try:
                d[(int(r["yaw"]), int(r["pitch"]))] = float(r[field])
            except ValueError:
                d[(int(r["yaw"]), int(r["pitch"]))] = np.nan
    return d


def pose_mean_field(region, field):
    """pose 级：对 9 roll 取均值，返回 {(yaw,pitch): mean}."""
    acc = {}
    for r in metrics:
        if r["region"] == region:
            k = (int(r["yaw"]), int(r["pitch"]))
            try:
                v = float(r[field])
            except ValueError:
                v = np.nan
            acc.setdefault(k, []).append(v)
    return {k: np.nanmean(v) for k, v in acc.items()}


def grid_from_dict(d):
    """把 {(yaw,pitch):val} 排成 pitch(行)×yaw(列) 网格。"""
    yaws = sorted(set(k[0] for k in d))
    pitches = sorted(set(k[1] for k in d))
    mat = np.full((len(pitches), len(yaws)), np.nan)
    for (y, p), v in d.items():
        mat[pitches.index(p), yaws.index(y)] = v
    return mat, yaws, pitches


# ============================================================
# Fig 1: brightness map（5 区域 yaw×pitch, roll=0 OCS）
# ============================================================
fig, axes = plt.subplots(1, 5, figsize=(20, 4.2))
for ax, rg in zip(axes, REGIONS):
    d = pose_map(rg, 0, "ocs_total")
    mat, yaws, pitches = grid_from_dict(d)
    im = ax.imshow(mat, aspect="auto", origin="lower", cmap="inferno")
    ax.set_xticks(range(len(yaws)))
    ax.set_xticklabels(yaws, fontsize=7, rotation=45)
    ax.set_yticks(range(len(pitches)))
    ax.set_yticklabels(pitches, fontsize=7)
    ax.set_xlabel("yaw", fontsize=8)
    ax.set_ylabel("pitch", fontsize=8)
    ax.set_title(rg, fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
fig.suptitle("P2 sparse grid: OCS total map at roll=0 (per region, phase63/L1-G1, roll=0 reuses 01_fullrun)",
             fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIG / "p2_sparse_grid_brightness_map.png", dpi=140)
fig.savefig(FIG / "p2_sparse_grid_brightness_map.pdf")
plt.close(fig)

# ============================================================
# Fig 2: information proxy map（neighbor_contrast_ypr, pose 均值）
# ============================================================
fig, axes = plt.subplots(1, 5, figsize=(20, 4.2))
# 统一色标范围
allv = []
for rg in REGIONS:
    allv += list(pose_mean_field(rg, "neighbor_contrast_ypr").values())
vmax = np.nanpercentile(allv, 98)
for ax, rg in zip(axes, REGIONS):
    d = pose_mean_field(rg, "neighbor_contrast_ypr")
    mat, yaws, pitches = grid_from_dict(d)
    im = ax.imshow(mat, aspect="auto", origin="lower", cmap="viridis", vmin=0, vmax=vmax)
    ax.set_xticks(range(len(yaws)))
    ax.set_xticklabels(yaws, fontsize=7, rotation=45)
    ax.set_yticks(range(len(pitches)))
    ax.set_yticklabels(pitches, fontsize=7)
    ax.set_xlabel("yaw", fontsize=8)
    ax.set_ylabel("pitch", fontsize=8)
    ax.set_title(rg, fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
fig.suptitle("P2 sparse grid: neighbor_contrast_ypr (3-axis local information proxy, pose-mean over rolls)",
             fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(FIG / "p2_sparse_grid_information_proxy_map.png", dpi=140)
fig.savefig(FIG / "p2_sparse_grid_information_proxy_map.pdf")
plt.close(fig)

# ============================================================
# Fig 3: region roll sensitivity panel + utility bars
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))

# 左：每区域 roll_sensitivity 分布（箱线）+ pose 散点
data_by_region = []
labels = []
for rg in REGIONS:
    rs_vals = list(pose_mean_field(rg, "roll_sensitivity_score").values())
    data_by_region.append([v for v in rs_vals if np.isfinite(v)])
    labels.append(rg)
bp = ax1.boxplot(data_by_region, labels=labels, showfliers=False, patch_artist=True)
cmap = plt.get_cmap("tab10")
for i, box in enumerate(bp["boxes"]):
    box.set_facecolor(cmap(i))
    box.set_alpha(0.5)
for i, dvals in enumerate(data_by_region):
    xs = np.random.default_rng(0).normal(i + 1, 0.05, len(dvals))
    ax1.scatter(xs, dvals, s=10, color=cmap(i), alpha=0.6, edgecolors="none")
ax1.set_ylabel("roll_sensitivity_score = (max-min)/mean of OCS over 9 rolls")
ax1.set_title("P2: roll sensitivity by region (per-pose)")
ax1.tick_params(axis="x", labelsize=8, rotation=20)
ax1.grid(alpha=0.3, axis="y")

# 右：region_utility_score 条形
rg_names = [r["region"] for r in region_sum]
util = [float(r["region_utility_score"]) for r in region_sum]
info = [float(r["norm_info"]) for r in region_sum]
rolls_ = [float(r["norm_roll_sens"]) for r in region_sum]
bright = [float(r["norm_brightness"]) for r in region_sum]
risk = [float(r["risk_frac"]) for r in region_sum]
order = np.argsort(util)
rg_names = [rg_names[i] for i in order]
util = [util[i] for i in order]
colors = ["tab:green" if u > 0 else "tab:red" for u in util]
ax2.barh(range(len(rg_names)), util, color=colors, alpha=0.7)
ax2.set_yticks(range(len(rg_names)))
ax2.set_yticklabels(rg_names, fontsize=8)
ax2.set_xlabel("region_utility_score (0.4*info + 0.3*rollsens + 0.3*bright - 0.2*risk)")
ax2.set_title("P2: region utility ranking")
ax2.axvline(0, color="gray", lw=0.8)
ax2.grid(alpha=0.3, axis="x")
fig.tight_layout()
fig.savefig(FIG / "p2_region_roll_sensitivity_panel.png", dpi=140)
fig.savefig(FIG / "p2_region_roll_sensitivity_panel.pdf")
plt.close(fig)

# ============================================================
# Fig 4: brightness vs information scatter（解耦可视化）
# ============================================================
fig, ax = plt.subplots(figsize=(9, 6.5))
for i, rg in enumerate(REGIONS):
    ocs = pose_mean_field(rg, "ocs_total")
    nc = pose_mean_field(rg, "neighbor_contrast_ypr")
    rs = pose_mean_field(rg, "roll_sensitivity_score")
    xs = [ocs[k] for k in ocs]
    ys = [nc[k] for k in ocs]
    ss = [30 + 200 * (rs[k] if np.isfinite(rs[k]) else 0) / 4.0 for k in ocs]
    ax.scatter(xs, ys, s=ss, color=cmap(i), alpha=0.6, edgecolors="k", linewidths=0.3, label=rg)
ax.set_xlabel("OCS total (pose-mean over rolls) — brightness")
ax.set_ylabel("neighbor_contrast_ypr (pose-mean) — 3-axis information proxy")
ax.set_title("P2: brightness vs information proxy (marker size ∝ roll_sensitivity)\n"
             "brightest ≠ most-informative — decoupling persists in local 3-axis neighborhoods")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "p2_brightness_vs_information_scatter.png", dpi=140)
fig.savefig(FIG / "p2_brightness_vs_information_scatter.pdf")
plt.close(fig)

print("[OK] 4 figures written (png+pdf)")

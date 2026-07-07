# -*- coding: utf-8 -*-
"""
d_figures.py —— R135 子任务 D：P3 local refinement 图表

产出（png+pdf）：
  figures/p3_refined_brightness_map        —— primary 区域 2.5度加密 yaw×pitch 亮度图(roll=0/均值)
  figures/p3_refined_information_proxy_map  —— primary 区域 neighbor_contrast 信息 proxy 加密图
  figures/p3_peak_migration_panel           —— 最亮点/高信息点在加密网格中的位置与迁移
  figures/p3_low_info_connectivity_panel     —— R3 低信息区连通性面板
  figures/p3_planning_candidate_scatter      —— 亮度 vs 信息 proxy 散点 + P4 候选高亮

只读 tables/ 下已生成的指标表，不重算渲染。
"""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PKG = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\v0.4_results\21_three_axis_p3_local_refinement")
T = PKG / "tables"
FIG = PKG / "figures"

metrics = list(csv.DictReader(open(T / "p3_local_refinement_metrics.csv", encoding="utf-8")))
region_sum = list(csv.DictReader(open(T / "p3_region_summary.csv", encoding="utf-8")))
p4_cand = list(csv.DictReader(open(T / "p3_p4_planning_candidates.csv", encoding="utf-8")))

REGIONS = []
for r in metrics:
    if r["region"] not in REGIONS:
        REGIONS.append(r["region"])
PRIMARY = [r["region"] for r in region_sum if r["priority"] == "primary"]
PRIMARY = [rg for rg in REGIONS if rg in PRIMARY]  # 稳定顺序


def fval(r, k):
    try:
        return float(r[k])
    except (ValueError, KeyError):
        return np.nan


def pose_map(region, roll, field):
    d = {}
    for r in metrics:
        if r["region"] == region and int(r["roll"]) == roll:
            d[(float(r["yaw_deg"]), float(r["pitch_deg"]))] = fval(r, field)
    return d


def pose_mean_field(region, field):
    acc = {}
    for r in metrics:
        if r["region"] == region:
            k = (float(r["yaw_deg"]), float(r["pitch_deg"]))
            acc.setdefault(k, []).append(fval(r, field))
    return {k: np.nanmean(v) for k, v in acc.items()}


def grid_from_dict(d):
    yaws = sorted(set(k[0] for k in d))
    pitches = sorted(set(k[1] for k in d))
    mat = np.full((len(pitches), len(yaws)), np.nan)
    for (y, p), v in d.items():
        mat[pitches.index(p), yaws.index(y)] = v
    return mat, yaws, pitches


# ============================================================
# Fig 1: refined brightness map（primary 区域 yaw×pitch, roll=0）
# ============================================================
n = len(PRIMARY)
fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 4.5))
if n == 1:
    axes = [axes]
for ax, rg in zip(axes, PRIMARY):
    d = pose_map(rg, 0, "ocs_total")
    mat, yaws, pitches = grid_from_dict(d)
    im = ax.imshow(mat, aspect="auto", origin="lower", cmap="inferno")
    ax.set_xticks(range(len(yaws)))
    ax.set_xticklabels([f"{y:.1f}" for y in yaws], fontsize=7, rotation=45)
    ax.set_yticks(range(len(pitches)))
    ax.set_yticklabels([f"{p:+.1f}" for p in pitches], fontsize=7)
    ax.set_xlabel("yaw (deg)", fontsize=8)
    ax.set_ylabel("pitch (deg)", fontsize=8)
    ax.set_title(rg, fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
fig.suptitle("P3 local refinement: OCS total map at roll=0 (2.5° grid, primary regions; "
             "integer pts reuse 01_fullrun, half-deg pts newly rendered)", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(FIG / "p3_refined_brightness_map.png", dpi=140)
fig.savefig(FIG / "p3_refined_brightness_map.pdf")
plt.close(fig)

# ============================================================
# Fig 2: refined information proxy map（neighbor_contrast_ypr, pose 均值）
# ============================================================
fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 4.5))
if n == 1:
    axes = [axes]
allv = []
for rg in PRIMARY:
    allv += list(pose_mean_field(rg, "neighbor_contrast_ypr").values())
vmax = np.nanpercentile([v for v in allv if np.isfinite(v)], 98)
for ax, rg in zip(axes, PRIMARY):
    d = pose_mean_field(rg, "neighbor_contrast_ypr")
    mat, yaws, pitches = grid_from_dict(d)
    im = ax.imshow(mat, aspect="auto", origin="lower", cmap="viridis", vmin=0, vmax=vmax)
    ax.set_xticks(range(len(yaws)))
    ax.set_xticklabels([f"{y:.1f}" for y in yaws], fontsize=7, rotation=45)
    ax.set_yticks(range(len(pitches)))
    ax.set_yticklabels([f"{p:+.1f}" for p in pitches], fontsize=7)
    ax.set_xlabel("yaw (deg)", fontsize=8)
    ax.set_ylabel("pitch (deg)", fontsize=8)
    ax.set_title(rg, fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
fig.suptitle("P3 local refinement: neighbor_contrast_ypr (3-axis local information proxy, "
             "pose-mean over rolls, 2.5° grid)", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(FIG / "p3_refined_information_proxy_map.png", dpi=140)
fig.savefig(FIG / "p3_refined_information_proxy_map.pdf")
plt.close(fig)

# ============================================================
# Fig 3: peak migration panel（最亮点/高信息点在加密网格中的位置）
# ============================================================
fig, axes = plt.subplots(1, n, figsize=(5.5 * n, 4.5))
if n == 1:
    axes = [axes]
for ax, rg in zip(axes, PRIMARY):
    ocs = pose_mean_field(rg, "ocs_total")
    nc = pose_mean_field(rg, "neighbor_contrast_ypr")
    mat, yaws, pitches = grid_from_dict(ocs)
    im = ax.imshow(mat, aspect="auto", origin="lower", cmap="inferno", alpha=0.85)
    # 最亮点
    bk = max(ocs, key=lambda k: ocs[k] if np.isfinite(ocs[k]) else -1)
    # 最高信息点
    ik = max(nc, key=lambda k: nc[k] if np.isfinite(nc[k]) else -1)
    bx, by = yaws.index(bk[0]), pitches.index(bk[1])
    ix, iy = yaws.index(ik[0]), pitches.index(ik[1])
    ax.scatter([bx], [by], marker="*", s=280, c="cyan", edgecolors="k",
               linewidths=0.8, label=f"brightest {bk[0]:.1f}/{bk[1]:+.1f}", zorder=5)
    ax.scatter([ix], [iy], marker="D", s=120, c="lime", edgecolors="k",
               linewidths=0.8, label=f"max-info {ik[0]:.1f}/{ik[1]:+.1f}", zorder=5)
    ax.set_xticks(range(len(yaws)))
    ax.set_xticklabels([f"{y:.1f}" for y in yaws], fontsize=7, rotation=45)
    ax.set_yticks(range(len(pitches)))
    ax.set_yticklabels([f"{p:+.1f}" for p in pitches], fontsize=7)
    ax.set_xlabel("yaw (deg)", fontsize=8)
    ax.set_ylabel("pitch (deg)", fontsize=8)
    ax.set_title(rg, fontsize=9)
    ax.legend(fontsize=6.5, loc="best")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
fig.suptitle("P3 peak migration: brightest (★) vs most-informative (◆) pose in refined 2.5° grid\n"
             "brightness ≠ information persists under local refinement", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig(FIG / "p3_peak_migration_panel.png", dpi=140)
fig.savefig(FIG / "p3_peak_migration_panel.pdf")
plt.close(fig)

# ============================================================
# Fig 4: low-info connectivity panel（R3）
# ============================================================
r3 = [rg for rg in REGIONS if rg.startswith("R3")]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
if r3:
    rg = r3[0]
    ncd = pose_mean_field(rg, "neighbor_contrast_ypr")
    mat, yaws, pitches = grid_from_dict(ncd)
    im = ax1.imshow(mat, aspect="auto", origin="lower", cmap="viridis")
    ax1.set_xticks(range(len(yaws)))
    ax1.set_xticklabels([f"{y:.1f}" for y in yaws], fontsize=7, rotation=45)
    ax1.set_yticks(range(len(pitches)))
    ax1.set_yticklabels([f"{p:+.1f}" for p in pitches], fontsize=7)
    ax1.set_xlabel("yaw (deg)", fontsize=8)
    ax1.set_ylabel("pitch (deg)", fontsize=8)
    ax1.set_title(f"{rg}: neighbor_contrast_ypr (low & connected?)", fontsize=9)
    fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    # 全局阈值下的低信息掩膜
    global_med = np.nanmedian([fval(r, "neighbor_contrast_ypr") for r in metrics])
    lowmask = (mat < global_med).astype(float)
    ax2.imshow(lowmask, aspect="auto", origin="lower", cmap="Greys", vmin=0, vmax=1)
    ax2.set_xticks(range(len(yaws)))
    ax2.set_xticklabels([f"{y:.1f}" for y in yaws], fontsize=7, rotation=45)
    ax2.set_yticks(range(len(pitches)))
    ax2.set_yticklabels([f"{p:+.1f}" for p in pitches], fontsize=7)
    ax2.set_xlabel("yaw (deg)", fontsize=8)
    ax2.set_ylabel("pitch (deg)", fontsize=8)
    frac = np.nanmean(lowmask)
    ax2.set_title(f"{rg}: low-info mask (< global median={global_med:.3f})\n"
                  f"connected low-info fraction = {frac:.2f}", fontsize=9)
fig.suptitle("P3 low-information connectivity (R3): is the low-info region contiguous?", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(FIG / "p3_low_info_connectivity_panel.png", dpi=140)
fig.savefig(FIG / "p3_low_info_connectivity_panel.pdf")
plt.close(fig)

# ============================================================
# Fig 5: planning candidate scatter（亮度 vs 信息 + P4 候选高亮）
# ============================================================
cmap = plt.get_cmap("tab10")
fig, ax = plt.subplots(figsize=(9.5, 6.8))
p4_keys = set((round(float(r["yaw_deg"]), 1), round(float(r["pitch_deg"]), 1)) for r in p4_cand)
for i, rg in enumerate(REGIONS):
    ocs = pose_mean_field(rg, "ocs_total")
    nc = pose_mean_field(rg, "neighbor_contrast_ypr")
    rs = pose_mean_field(rg, "roll_sensitivity_score")
    xs = [ocs[k] for k in ocs]
    ys = [nc[k] for k in ocs]
    ss = [30 + 200 * (rs[k] if np.isfinite(rs[k]) else 0) / 4.0 for k in ocs]
    ax.scatter(xs, ys, s=ss, color=cmap(i), alpha=0.55, edgecolors="k", linewidths=0.3, label=rg)
    # P4 候选描边
    for k in ocs:
        if (round(k[0], 1), round(k[1], 1)) in p4_keys:
            ax.scatter([ocs[k]], [nc[k]], s=260, facecolors="none",
                       edgecolors="red", linewidths=1.4, zorder=6)
ax.scatter([], [], s=120, facecolors="none", edgecolors="red", linewidths=1.4,
           label="P4 planning candidate")
ax.set_xlabel("OCS total (pose-mean over rolls) — brightness")
ax.set_ylabel("neighbor_contrast_ypr (pose-mean) — 3-axis information proxy")
ax.set_title("P3 planning candidates: brightness vs information proxy (marker size ∝ roll_sensitivity)\n"
             "red-ringed = P4 observation planning candidates")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "p3_planning_candidate_scatter.png", dpi=140)
fig.savefig(FIG / "p3_planning_candidate_scatter.pdf")
plt.close(fig)

print("[OK] 5 figures written (png+pdf)")

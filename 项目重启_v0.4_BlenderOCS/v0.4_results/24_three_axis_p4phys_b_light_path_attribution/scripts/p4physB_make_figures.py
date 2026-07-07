# -*- coding: utf-8 -*-
"""
p4physB_make_figures.py —— P4-PHYS-B 图件生成
从核心分析脚本 import 复用加载与分解逻辑，输出 png+pdf。
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
import p4physB_light_path_attribution as A

FIG = A.PKG24 / "figures"
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 10, "figure.dpi": 150})

poses = {k: A.load_pose(k) for k in A.POSES}
Hspec = A.specular_axis()
PART_ORDER = ["jinshuzhuti", "yinshenban", "taiyangnengban"]
PART_LBL = {"jinshuzhuti": "Metal body",
            "yinshenban": "Dark panel",
            "taiyangnengban": "Solar panel"}
COL = {"jinshuzhuti": "silver", "yinshenban": "dimgray", "taiyangnengban": "steelblue"}


def savefig(fig, stem):
    fig.savefig(FIG / f"{stem}.png", bbox_inches="tight", dpi=300)
    fig.savefig(FIG / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


# ---- Fig 1: top-1 part contribution ----
_, per_part, npix, _ = A.ocs_breakdown(poses["R1_top1"])
tot = sum(per_part.values())
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
vals = [per_part[p] for p in PART_ORDER]
cols = [COL[p] for p in PART_ORDER]
ax1.bar(range(3), vals, color=cols, edgecolor="k")
ax1.set_xticks(range(3)); ax1.set_xticklabels([PART_LBL[p] for p in PART_ORDER])
ax1.set_ylabel("OCS per part (m²)")
ax1.set_title("top-1 OCS per-part\nyaw245/pitch27.5/roll+15")
for i, v in enumerate(vals):
    ax1.text(i, v, f"{v:.4f}\n{v/tot*100:.1f}%", ha="center", va="bottom", fontsize=8)
ax1.set_ylim(0, max(vals) * 1.25)
ax2.pie(vals, labels=[PART_LBL[p].split(chr(10))[0] for p in PART_ORDER],
        colors=cols, autopct="%1.1f%%", startangle=90, wedgeprops={"edgecolor": "k"})
ax2.set_title(f"Contribution share (total={tot:.4f} m²)")
savefig(fig, "p4physB_top1_part_contribution")

# ---- Fig 2: NoH histogram (metal contrib px) top-1 vs R4 vs R3 ----
fig, ax = plt.subplots(figsize=(7, 4.5))
for k, c in (("R1_top1", "C3"), ("R4_robust", "C0"), ("R3_neg", "C1")):
    pz = poses[k]
    m = (pz["indexob"] == 1) & pz["contributing"]
    NoH = np.clip(pz["normal"][m] @ Hspec, 0, 1)
    ax.hist(NoH, bins=60, range=(0, 1), histtype="step", linewidth=1.8,
            color=c, label=f'{k} ({A.POSES[k]["role"][:22]})')
ax.axvline(np.cos(np.radians(0)), ls=":", color="gray")
ax.set_xlabel("N·H  (normal vs half-vector; →1 = specular aligned)")
ax.set_ylabel("metal-body contributing pixels")
ax.set_title("Specular alignment N·H distribution\n(phase63/L1-G1, half-vec H=(S+D)/|S+D|)")
ax.legend(fontsize=8); ax.set_yscale("log")
savefig(fig, "p4physB_top1_normal_view_sun_angle_hist")

# ---- Fig 3: top-1 vs R4 vs R3 per-part compare (grouped bar) ----
fig, ax = plt.subplots(figsize=(8, 4.5))
keys = ["R1_top1", "R4_robust", "R3_neg"]
x = np.arange(len(keys)); wbar = 0.25
for j, p in enumerate(PART_ORDER):
    vals = []
    for k in keys:
        _, pp, _, _ = A.ocs_breakdown(poses[k])
        vals.append(pp[p])
    ax.bar(x + (j - 1) * wbar, vals, wbar, color=COL[p], edgecolor="k",
           label=PART_LBL[p].split(chr(10))[0])
ax.set_xticks(x); ax.set_xticklabels(
    [f'{k}\n{A.POSES[k]["label"]}' for k in keys], fontsize=7)
ax.set_ylabel("OCS per part (m²)")
ax.set_title("top-1 vs R4 vs R3 per-part OCS contribution")
ax.legend(fontsize=8)
savefig(fig, "p4physB_top1_vs_R4_R3_contribution_compare")

# ---- Fig 4: spatial I_linear maps (top-1, R4, R3) ----
fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
for ax, k in zip(axes, keys):
    pz = poses[k]
    img = np.where(pz["contributing"], pz["I_linear"], np.nan)
    im = ax.imshow(img, cmap="inferno")
    ax.set_title(f'{k}\n{A.POSES[k]["label"]}\nOCS={A.POSES[k]["ocs_ref"]:.4f}', fontsize=8)
    ax.axis("off")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
fig.suptitle("Per-pixel I_linear (contributing pixels) — fixed phase63/L1-G1")
savefig(fig, "p4physB_I_linear_maps")

print("[figures] done ->", FIG)

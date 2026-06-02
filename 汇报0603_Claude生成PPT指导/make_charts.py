# -*- coding: utf-8 -*-
"""为汇报 PPT 生成两张与模板配色一致的自定义图表。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

OUT = r"d:\我的文件\研究生学术\光学项目\0506新\汇报0603_Claude生成PPT指导"

# 模板配色
GREEN = "#016A3F"      # accent1 深绿
LGREEN = "#75BD42"     # accent4 亮绿
TEAL = "#30C0B4"       # accent5 青
GRAY = "#808080"
DARK = "#333333"

# ---------- 图 A：ResNet 图像退化鲁棒性（noise vs brightness） ----------
fig, ax = plt.subplots(figsize=(7.6, 4.3), dpi=200)
labels = ["clean", "噪声\n1%", "噪声\n3%", "噪声\n5%", "噪声\n10%",
          "亮度\n×0.5", "亮度\n×0.75", "亮度\n×1.25", "亮度\n×1.5"]
vals = [1.69, 85.85, 85.49, 85.97, 87.92, 3.45, 2.03, 1.77, 2.00]
colors = [GREEN, "#C0392B", "#C0392B", "#C0392B", "#C0392B",
          LGREEN, LGREEN, LGREEN, LGREEN]
x = np.arange(len(labels))
bars = ax.bar(x, vals, color=colors, width=0.66, edgecolor="white", linewidth=0.8)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + 1.5, f"{v:.1f}°",
            ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=DARK)
ax.axhline(5.91, color=TEAL, lw=2.0, ls="--", zorder=0)
ax.text(8.45, 8.5, "OCS-only 5.91°\n(不受图像退化影响)", color=TEAL,
        fontsize=9.5, ha="right", va="bottom", fontweight="bold")
ax.set_ylabel("平均姿态误差 (°)", fontsize=12)
ax.set_title("ResNet 图像反演：干净上界 1.69° vs 1% 噪声崩溃 85.9°",
             fontsize=12.5, fontweight="bold", color=GREEN, pad=10)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9.5)
ax.set_ylim(0, 100)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_resnet_robust.png"), dpi=200, bbox_inches="tight")
plt.close(fig)
print("saved chart_resnet_robust.png")

# ---------- 图 B：OCS 噪声鲁棒性 —— 图像补偿增益随噪声递增 ----------
fig, ax = plt.subplots(figsize=(7.6, 4.3), dpi=200)
nlev = [0, 1, 5, 10, 20]
ocs = [5.91, 5.50, 7.27, 9.99, 17.25]
fus = [3.93, 3.77, 4.65, 6.69, 10.96]
xi = np.arange(len(nlev))
ax.plot(xi, ocs, "-o", color=TEAL, lw=2.6, ms=8, label="OCS-only MLP")
ax.plot(xi, fus, "-s", color=GREEN, lw=2.6, ms=8, label="OCS+图像 融合")
ax.fill_between(xi, fus, ocs, color=LGREEN, alpha=0.20)
# 标注增益
for i in range(len(nlev)):
    gain = ocs[i] - fus[i]
    ax.annotate(f"+{gain:.1f}°", (xi[i], (ocs[i]+fus[i])/2),
                fontsize=9.5, ha="center", va="center", color=GREEN, fontweight="bold")
for i, v in enumerate(ocs):
    ax.text(xi[i], v + 0.6, f"{v:.1f}", ha="center", fontsize=9, color=TEAL)
for i, v in enumerate(fus):
    ax.text(xi[i], v - 1.2, f"{v:.1f}", ha="center", fontsize=9, color=GREEN)
ax.set_xticks(xi); ax.set_xticklabels([f"{n}%" for n in nlev], fontsize=10.5)
ax.set_xlabel("OCS 测量噪声水平", fontsize=12)
ax.set_ylabel("平均姿态误差 (°)", fontsize=12)
ax.set_title("OCS 含噪时图像补偿增益单调递增：+1.97° → +6.29°",
             fontsize=12.5, fontweight="bold", color=GREEN, pad=10)
ax.legend(fontsize=11, loc="upper left", frameon=False)
ax.set_ylim(0, 20)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "chart_ocs_noise.png"), dpi=200, bbox_inches="tight")
plt.close(fig)
print("saved chart_ocs_noise.png")

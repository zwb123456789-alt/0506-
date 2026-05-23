# -*- coding: utf-8 -*-
"""
visualization.py —— 中英双语可视化
====================================
按模块 A 规范输出 6 张独立图：
    fig01_ocs_3d_surface.png          OCS 三维曲面（含遮挡）
    fig02_ocs_heatmap.png             OCS 俯视热图（含遮挡）
    fig03_parts_heatmap.png           各部件 OCS 贡献热图
    fig04_occlusion_ratio_heatmap.png 遮挡率热图
    fig05_ocs_loss_heatmap.png        OCS 损失热图
    fig06_satellite_model.png         卫星模型 3D 示意图

修复点：
- 中文字体统一加载，避免方框
- 2D 模式不再生成 1D 三曲线图
- 遮挡率 clip 到 [0,100]，OCS 损失 clip ≥ 0
- 每张图独立保存，命名 fig0X_*.png
- colorbar 强制带单位
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from config import (
    FIG_DPI, LABELS,
    PART_COLORS,
    get_bilingual_title, get_part_label,
)


# ============================================================
# 中文字体设置（避免方框）
# ============================================================
def setup_matplotlib_style():
    """统一 matplotlib 中英双语字体与排版。"""
    plt.rcParams["font.sans-serif"] = [
        "SimHei",
        "Microsoft YaHei",
        "Noto Sans CJK SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"]    = 120
    plt.rcParams["savefig.dpi"]   = FIG_DPI
    plt.rcParams["axes.labelsize"]  = 13
    plt.rcParams["axes.titlesize"]  = 15
    plt.rcParams["legend.fontsize"] = 11
    plt.rcParams["xtick.labelsize"] = 11
    plt.rcParams["ytick.labelsize"] = 11


# ============================================================
# 工具：把 scan_data 整理成 yaw × pitch 网格
# ============================================================
def _to_grid(scan_data, key, part_name=None):
    """
    将 scan_data 整成 (n_pitch, n_yaw) 网格。
    part_name 非空时取 part_contrib[part_name][key]。
    """
    yaw_angles   = np.array(sorted(set(d["yaw"]   for d in scan_data)))
    pitch_angles = np.array(sorted(set(d["pitch"] for d in scan_data)))
    ny, npn = len(yaw_angles), len(pitch_angles)
    dy = yaw_angles[1]   - yaw_angles[0]   if ny  > 1 else 1.0
    dp = pitch_angles[1] - pitch_angles[0] if npn > 1 else 1.0

    arr = np.zeros((npn, ny))
    for d in scan_data:
        yi = int(np.round((d["yaw"]   - yaw_angles[0])   / dy))
        pi = int(np.round((d["pitch"] - pitch_angles[0]) / dp))
        if part_name is None:
            arr[pi, yi] = d[key]
        else:
            arr[pi, yi] = d["part_contrib"][part_name][key]
    return yaw_angles, pitch_angles, arr


# ============================================================
# fig01: OCS 三维曲面（含遮挡）
# ============================================================
def plot_fig01_ocs_3d_surface(scan_data, output_dir):
    yaws, pitches, ocs_with = _to_grid(scan_data, "ocs_with_occ")
    Y, P = np.meshgrid(yaws, pitches)

    fig = plt.figure(figsize=(11, 8))
    ax  = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(Y, P, ocs_with, cmap="viridis", alpha=0.9, linewidth=0)
    ax.set_xlabel(LABELS["xlabel_yaw"],   fontsize=12, labelpad=10)
    ax.set_ylabel(LABELS["ylabel_pitch"], fontsize=12, labelpad=10)
    ax.set_zlabel(LABELS["zlabel_ocs"],   fontsize=12, labelpad=10)
    ax.set_title(get_bilingual_title("fig01"), fontsize=14, fontweight="bold", pad=15)
    ax.view_init(elev=30, azim=-60)

    cbar = fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.10)
    cbar.set_label(LABELS["zlabel_ocs"], fontsize=11)

    path = os.path.join(output_dir, "fig01_ocs_3d_surface.png")
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 已保存: {path}")


# ============================================================
# fig02: OCS 俯视热图（含遮挡）
# ============================================================
def plot_fig02_ocs_heatmap(scan_data, output_dir):
    yaws, pitches, ocs_with = _to_grid(scan_data, "ocs_with_occ")

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.contourf(yaws, pitches, ocs_with, levels=30, cmap="plasma")
    ax.set_xlabel(LABELS["xlabel_yaw"],   fontsize=13)
    ax.set_ylabel(LABELS["ylabel_pitch"], fontsize=13)
    ax.set_title(get_bilingual_title("fig02"), fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.2, linestyle="--")

    cbar = fig.colorbar(im, ax=ax, shrink=0.95)
    cbar.set_label(LABELS["label_ocs"], fontsize=11)

    path = os.path.join(output_dir, "fig02_ocs_heatmap.png")
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 已保存: {path}")


# ============================================================
# fig03: 各部件 OCS 贡献热图（3 子图）
# ============================================================
def plot_fig03_parts_heatmap(scan_data, output_dir):
    part_names = ["jinshuzhuti", "taiyangnengban", "yinshenban"]
    part_cmaps = {"jinshuzhuti": "Blues", "taiyangnengban": "Oranges", "yinshenban": "Purples"}

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    fig.suptitle(get_bilingual_title("fig03"), fontsize=15, fontweight="bold")

    for ax, pn in zip(axes, part_names):
        yaws, pitches, arr = _to_grid(scan_data, "ocs_with_occ", part_name=pn)
        im = ax.contourf(yaws, pitches, arr, levels=30, cmap=part_cmaps.get(pn, "Greys"))
        ax.set_xlabel(LABELS["xlabel_yaw"],   fontsize=12)
        ax.set_ylabel(LABELS["ylabel_pitch"], fontsize=12)
        ax.set_title(get_part_label(pn), fontsize=13, fontweight="bold")
        ax.grid(True, alpha=0.2, linestyle="--")
        cbar = fig.colorbar(im, ax=ax, shrink=0.9)
        cbar.set_label(LABELS["label_ocs"], fontsize=10)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    path = os.path.join(output_dir, "fig03_parts_heatmap.png")
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 已保存: {path}")


# ============================================================
# fig04: 遮挡率热图
# ============================================================
def plot_fig04_occlusion_ratio_heatmap(scan_data, output_dir):
    yaws, pitches, occ = _to_grid(scan_data, "occlusion_ratio")
    occ_pct = np.clip(occ * 100.0, 0.0, 100.0)

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.contourf(yaws, pitches, occ_pct, levels=np.linspace(0, 100, 31), cmap="Reds")
    ax.set_xlabel(LABELS["xlabel_yaw"],   fontsize=13)
    ax.set_ylabel(LABELS["ylabel_pitch"], fontsize=13)
    ax.set_title(get_bilingual_title("fig04"), fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.2, linestyle="--")

    cbar = fig.colorbar(im, ax=ax, shrink=0.95, ticks=np.linspace(0, 100, 6))
    cbar.set_label(LABELS["label_occ"], fontsize=11)

    path = os.path.join(output_dir, "fig04_occlusion_ratio_heatmap.png")
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 已保存: {path}")


# ============================================================
# fig05: OCS 损失热图
# ============================================================
def plot_fig05_ocs_loss_heatmap(scan_data, output_dir):
    yaws, pitches, ocs_no   = _to_grid(scan_data, "ocs_no_occ")
    _,    _,       ocs_with = _to_grid(scan_data, "ocs_with_occ")
    ocs_loss = np.maximum(ocs_no - ocs_with, 0.0)

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.contourf(yaws, pitches, ocs_loss, levels=30, cmap="coolwarm")
    ax.set_xlabel(LABELS["xlabel_yaw"],   fontsize=13)
    ax.set_ylabel(LABELS["ylabel_pitch"], fontsize=13)
    ax.set_title(get_bilingual_title("fig05"), fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.2, linestyle="--")

    cbar = fig.colorbar(im, ax=ax, shrink=0.95)
    cbar.set_label(LABELS["label_loss"], fontsize=11)

    path = os.path.join(output_dir, "fig05_ocs_loss_heatmap.png")
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 已保存: {path}")


# ============================================================
# fig06: 卫星 3D 模型示意
# ============================================================
def plot_fig06_satellite_model(meshes, sun_dir, output_dir):
    fig = plt.figure(figsize=(12, 9))
    ax  = fig.add_subplot(111, projection="3d")

    for name, mesh in meshes.items():
        tris = [mesh.vertices[f] for f in mesh.faces]
        poly = Poly3DCollection(
            tris, alpha=0.75,
            facecolor=PART_COLORS.get(name, "gray"),
            edgecolor="none",
        )
        ax.add_collection3d(poly)
        c = mesh.vertices.mean(axis=0)
        ax.text(
            c[0], c[1], c[2],
            f'{get_part_label(name)}\n({len(mesh.faces):,} faces)',
            fontsize=9, color="white", ha="center",
            bbox=dict(boxstyle="round", facecolor=PART_COLORS.get(name, "gray"), alpha=0.8),
        )

    if sun_dir is not None:
        sn  = sun_dir / np.linalg.norm(sun_dir)
        cen = np.mean(np.vstack([m.vertices for m in meshes.values()]), axis=0)
        sc  = np.max([
            np.linalg.norm(m.vertices.max(0) - m.vertices.min(0))
            for m in meshes.values()
        ]) * 0.6
        ax.quiver(
            cen[0], cen[1], cen[2],
            sn[0] * sc, sn[1] * sc, sn[2] * sc,
            color="gold", linewidth=3, arrow_length_ratio=0.3,
        )
        ax.text(
            cen[0] + sn[0] * sc * 1.2,
            cen[1] + sn[1] * sc * 1.2,
            cen[2] + sn[2] * sc * 1.2,
            "Sun / 太阳", color="gold", fontsize=12, fontweight="bold",
        )

    av = np.vstack([m.vertices for m in meshes.values()])
    ax.set_xlim(av[:, 0].min(), av[:, 0].max())
    ax.set_ylim(av[:, 1].min(), av[:, 1].max())
    ax.set_zlim(av[:, 2].min(), av[:, 2].max())
    ax.set_xlabel("X (mm)", fontsize=12)
    ax.set_ylabel("Y (mm)", fontsize=12)
    ax.set_zlabel("Z (mm)", fontsize=12)
    ax.set_title(get_bilingual_title("fig06"), fontsize=15, fontweight="bold")

    path = os.path.join(output_dir, "fig06_satellite_model.png")
    plt.tight_layout()
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 已保存: {path}")


# ============================================================
# 一键导出全部 2D 模式图
# ============================================================
def plot_all_2d(scan_data, meshes, sun_dir, output_dir):
    """2D 扫描模式下输出 fig01~fig05；fig06 由 main 直接调。"""
    plot_fig01_ocs_3d_surface(scan_data,         output_dir)
    plot_fig02_ocs_heatmap(scan_data,            output_dir)
    plot_fig03_parts_heatmap(scan_data,          output_dir)
    plot_fig04_occlusion_ratio_heatmap(scan_data, output_dir)
    plot_fig05_ocs_loss_heatmap(scan_data,        output_dir)


# ============================================================
# 1D 模式专用：三曲线图（保留以备 1D 扫描使用）
# ============================================================
def plot_three_curves_1d(scan_data, output_dir):
    """1D yaw-only 模式专用，避免与 2D 模式混用。"""
    yaws         = np.array([d["yaw"]            for d in scan_data])
    ocs_no_occ   = np.array([d["ocs_no_occ"]     for d in scan_data])
    ocs_with_occ = np.array([d["ocs_with_occ"]   for d in scan_data])
    occ_ratio    = np.array([d["occlusion_ratio"] for d in scan_data])
    occ_pct      = np.clip(occ_ratio * 100.0, 0.0, 100.0)

    fig, axes = plt.subplots(3, 1, figsize=(14, 14))

    axes[0].plot(yaws, ocs_no_occ, "b-", linewidth=2, marker="o", ms=4,
                 label="No occlusion / 无遮挡")
    axes[0].set_ylabel(LABELS["label_ocs"], fontsize=13)
    axes[0].set_title("OCS (no occlusion) / OCS 无遮挡 vs Yaw", fontsize=14, fontweight="bold")
    axes[0].grid(True, alpha=0.3, linestyle="--")
    axes[0].legend(fontsize=11)

    axes[1].plot(yaws, ocs_with_occ, "g-", linewidth=2, marker="s", ms=4,
                 label="With occlusion / 含遮挡")
    axes[1].set_ylabel(LABELS["label_ocs"], fontsize=13)
    axes[1].set_title("OCS (with occlusion) / OCS 含遮挡 vs Yaw", fontsize=14, fontweight="bold")
    axes[1].grid(True, alpha=0.3, linestyle="--")
    axes[1].legend(fontsize=11)

    axes[2].plot(yaws, occ_pct, "r-", linewidth=2, marker="^", ms=4)
    axes[2].fill_between(yaws, 0, occ_pct, alpha=0.15, color="red")
    axes[2].set_xlabel(LABELS["xlabel_yaw"], fontsize=13)
    axes[2].set_ylabel(LABELS["label_occ"],  fontsize=13)
    axes[2].set_title("Occlusion ratio / 遮挡率 vs Yaw", fontsize=14, fontweight="bold")
    axes[2].grid(True, alpha=0.3, linestyle="--")
    axes[2].set_ylim(0, 100)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig01_ocs_yaw_three_curves.png")
    plt.savefig(path, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 已保存: {path}")

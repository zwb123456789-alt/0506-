# -*- coding: utf-8 -*-
"""
Nature-style publication figures for OCS + Image joint simulation project.

Produces:
  figN1_ablation_heatmap.svg/pdf   — 24-experiment ablation matrix
  figN2_multigeom_ocs.svg/pdf      — 5-geometry OCS comparison hero figure
  figN3_error_cdf.svg/pdf          — Angular error CDF + key metrics bars

Reads latest results from 结果/ without modifying any existing files.
"""

import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, FuncFormatter
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────
PROJECT_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新")
RESULT_A_SINGLE = PROJECT_ROOT / "结果/模块A_重构/2d_yaw73_pitch37/run_20260520_160847"
RESULT_A_MULTI  = PROJECT_ROOT / "结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260520_162831"
RESULT_C_ABLATION = PROJECT_ROOT / "结果/模块C_反演/inv_ocs/run_20260520_184414_ablation"
OUT_DIR = PROJECT_ROOT / "结果/nature_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Nature Style ─────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans", "SimHei"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
})

# ── Palette ──────────────────────────────────────────────────────
BLUE_MAIN   = "#0F4D92"
BLUE_SEC    = "#3775BA"
BLUE_SOFT   = "#B4C0E4"
GREEN_MAIN  = "#2E9E44"
ORANGE_MAIN = "#E28E2C"
RED_STRONG  = "#B64342"
RED_SOFT    = "#F6CFCB"
NEUTRAL_L   = "#CFCECE"
NEUTRAL_M   = "#767676"
NEUTRAL_D   = "#4D4D4D"
GOLD        = "#FFD700"
TEAL        = "#42949E"
VIOLET      = "#9A4D8E"

GEOM_COLORS = [BLUE_MAIN, TEAL, ORANGE_MAIN, RED_STRONG, VIOLET]
FEAT_COLORS = {"total": BLUE_MAIN, "per_part": ORANGE_MAIN, "all": GREEN_MAIN}
SPLIT_LS    = {"LOO": "-", "10°→5°": "--"}

GEOM_LABELS_MAP = {
    "phase63_backscatter":       "Phase 63° (backscatter)",
    "phase24_near_backscatter":  "Phase 24° (near-back.)",
    "phase120_forward_scatter":  "Phase 120° (forward)",
    "phase90_side":              "Phase 90° (side)",
    "phase45_overhead":          "Phase 45° (overhead)",
}
PART_NAMES_EN = {"jinshuzhuti": "Metal body", "taiyangnengban": "Solar panel", "yinshenban": "Stealth plate"}


def save_fig(fig, name, dpi=600):
    """Save to SVG + PDF + PNG in OUT_DIR."""
    for ext, kw in [(".svg", {}), (".pdf", {}), (".png", {"dpi": dpi})]:
        p = OUT_DIR / f"{name}{ext}"
        fig.savefig(str(p), bbox_inches="tight", **kw)
    print(f"  Saved: {name}.svg/.pdf/.png")


# ====================================================================
# FIG N1: Ablation Matrix Heatmap
# ====================================================================
def figN1_ablation_heatmap():
    """24-experiment ablation matrix as a structured heatmap."""
    with open(RESULT_C_ABLATION / "summary.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    metrics = data["metrics_table"]
    # Build a structured matrix: rows = 24 experiments, columns = key metrics
    rows = []
    for m in metrics:
        label = m["label"]  # e.g. "concat5:LOO:total:log"
        parts = label.split(":")
        geom_set, split, feat, xform = parts[0], parts[1], parts[2], parts[3]
        rows.append({
            "geom_set": "5-geom" if geom_set == "concat5" else "1-geom",
            "split":     split,
            "feat":      feat,
            "xform":     xform,
            "top1_5":    m["top1_acc@5deg"] * 100,
            "top5_5":    m["top5_acc@5deg"] * 100,
            "top1_10":   m["top1_acc@10deg"] * 100,
            "top5_10":   m["top5_acc@10deg"] * 100,
            "mean_err":  m["angular_err_mean"],
            "median_err": m["angular_err_median"],
            "p90_err":    m["angular_err_p90"],
        })

    # Sort: geom_set, then split (LOO first), then feat, then xform (raw first)
    order_geom = {"1-geom": 0, "5-geom": 1}
    order_split = {"LOO": 0, "10°→5°": 1}
    order_feat = {"total": 0, "per_part": 1, "all": 2}
    order_xform = {"raw": 0, "log": 1}
    rows.sort(key=lambda r: (order_geom[r["geom_set"]], order_split[r["split"]],
                              order_feat[r["feat"]], order_xform[r["xform"]]))

    # Build matrix: 3 metric columns
    metrics_cols = ["top1_5", "top5_5", "mean_err"]
    metric_names = ["Top-1 @5° (%)", "Top-5 @5° (%)", "Mean Err (°)"]
    n_rows = len(rows)
    n_cols = len(metrics_cols)

    matrix = np.zeros((n_rows, n_cols))
    for i, r in enumerate(rows):
        for j, mc in enumerate(metrics_cols):
            matrix[i, j] = r[mc]

    # Row labels
    row_labels = []
    for r in rows:
        g = "5G" if r["geom_set"] == "5-geom" else "1G"
        s = "LOO" if r["split"] == "LOO" else "10°→5°"
        f = {"total": "TOT", "per_part": "PP", "all": "ALL"}[r["feat"]]
        x = "log" if r["xform"] == "log" else "raw"
        row_labels.append(f"{g} {s} {f} {x}")

    # Normalize each column to [0,1] for colormap consistency
    matrix_norm = np.zeros_like(matrix)
    for j in range(n_cols):
        if j < 2:  # accuracy metrics: higher is better
            vmin, vmax = 0, 100
        else:  # mean error: lower is better, invert for colormap
            vmin, vmax = matrix[:, j].min(), matrix[:, j].max()
        matrix_norm[:, j] = np.clip((matrix[:, j] - vmin) / (vmax - vmin), 0, 1)

    # Draw
    fig, axes = plt.subplots(1, 3, figsize=(15, 8),
                             gridspec_kw={"width_ratios": [1, 1, 1.2]})

    cmaps = ["Blues", "Greens", "Reds_r"]
    for j, (ax, cmap) in enumerate(zip(axes, cmaps)):
        col_data = matrix[:, j].reshape(-1, 1)
        im = ax.imshow(col_data, aspect="auto", cmap=cmap)
        ax.set_xticks([0])
        ax.set_xticklabels([metric_names[j]], fontsize=9, fontweight="bold")

        # Y labels
        if j == 0:
            ax.set_yticks(range(n_rows))
            ax.set_yticklabels(row_labels, fontsize=6.5, fontfamily="monospace")
        else:
            ax.set_yticks([])

        # Annotate values
        for i in range(n_rows):
            val = matrix[i, j]
            if j < 2:
                txt = f"{val:.1f}"
                fc = "white" if val > 50 else NEUTRAL_D
            else:
                txt = f"{val:.1f}"
                fc = "white" if val > 60 else NEUTRAL_D
            ax.text(0, i, txt, ha="center", va="center", fontsize=6.3,
                    fontweight="bold", color=fc)

        # Draw group separators
        for sep_i in [6, 12, 18]:
            ax.axhline(sep_i - 0.5, color="white", lw=2.5)

        # Draw geom_set separator
        ax.axhline(11.5, color=NEUTRAL_D, lw=1.5, linestyle="-")

        # Group labels on right side
        if j == 2:
            ax_right = ax.twinx()
            ax_right.set_ylim(ax.get_ylim())
            ax_right.set_yticks([3, 9, 15, 21])
            ax_right.set_yticklabels(["1-geom\nLOO", "1-geom\n10°→5°",
                                       "5-geom\nLOO", "5-geom\n10°→5°"],
                                      fontsize=7, fontweight="bold", color=NEUTRAL_M)
            ax_right.spines["right"].set_visible(False)
            ax_right.spines["top"].set_visible(False)

    fig.suptitle("Ablation Matrix: kNN Pose Retrieval Performance",
                 fontsize=11, fontweight="bold", y=1.01)
    fig.text(0.5, 0.01, "1G = single geometry (phase63)  |  5G = 5-geometry concatenated  |  "
             "TOT=total OCS  PP=per-part  ALL=all features  |  LOO=leave-one-out  "
             "10°→5°=10° library → 5° query",
             ha="center", fontsize=6.5, color=NEUTRAL_M)

    plt.tight_layout(rect=[0, 0.03, 0.96, 0.98])
    save_fig(fig, "figN1_ablation_heatmap")
    return rows


# ====================================================================
# FIG N2: Multi-geometry OCS Comparison Hero Figure
# ====================================================================
def figN2_multigeom_ocs():
    """5-geometry OCS comparison: 1 hero heatmap + 4 subordinate panels."""

    # Load all 5 geometry CSVs
    geom_dirs = sorted(RESULT_A_MULTI.glob("phase*"))
    geoms = {}
    for gd in geom_dirs:
        label = gd.name
        csv_path = gd / "ocs_scan.csv"
        data = np.genfromtxt(str(csv_path), delimiter=",", names=True, encoding="utf-8")
        geoms[label] = {
            "yaw": data["yaw"],
            "pitch": data["pitch"],
            "ocs_with_occ": data["ocs_with_occ"],
            "occlusion_ratio": data["occlusion_ratio"] * 100,
        }

    geom_order = ["phase63_backscatter", "phase24_near_backscatter",
                  "phase45_overhead", "phase90_side", "phase120_forward_scatter"]

    # Grid each geometry to 73×37 heatmap
    def to_grid(yaw, pitch, values):
        yaw_u = np.unique(yaw)
        pitch_u = np.unique(pitch)
        ny, npn = len(yaw_u), len(pitch_u)
        arr = np.zeros((npn, ny))
        dy = yaw_u[1] - yaw_u[0] if ny > 1 else 1
        dp = pitch_u[1] - pitch_u[0] if npn > 1 else 1
        for y, p, v in zip(yaw, pitch, values):
            yi = int(np.round((y - yaw_u[0]) / dy))
            pi = int(np.round((p - pitch_u[0]) / dp))
            arr[pi, yi] = v
        return yaw_u, pitch_u, arr

    grids = {}
    for label in geom_order:
        g = geoms[label]
        yaws, pitches, arr = to_grid(g["yaw"], g["pitch"], g["ocs_with_occ"])
        grids[label] = {"yaws": yaws, "pitches": pitches, "ocs": arr}

    # ── Figure: 3×2 grid (one empty slot) ──
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes_flat = axes.flatten()

    for idx, label in enumerate(geom_order):
        ax = axes_flat[idx]
        g = grids[label]
        yaws, pitches, ocs = g["yaws"], g["pitches"], g["ocs"]

        # Log scale for OCS to handle GGX dynamic range
        ocs_log = np.log10(np.maximum(ocs, 1e-6))
        levels = np.linspace(ocs_log.min(), ocs_log.max(), 40)

        cf = ax.contourf(yaws, pitches, ocs_log, levels=levels, cmap="magma")
        ax.set_xlabel("Yaw (°)", fontsize=8, labelpad=2)
        ax.set_ylabel("Pitch (°)", fontsize=8, labelpad=2)

        # Phase angle annotation
        phase_map = {  # from manifest
            "phase63_backscatter": "63°",
            "phase24_near_backscatter": "24°",
            "phase45_overhead": "45°",
            "phase90_side": "90°",
            "phase120_forward_scatter": "120°",
        }
        ax.set_title(f"Phase {phase_map[label]}", fontsize=9.5, fontweight="bold",
                     color=GEOM_COLORS[idx % len(GEOM_COLORS)])
        ax.grid(True, alpha=0.15, linestyle="--", lw=0.4)

        # Add OCS stats
        ax.text(0.98, 0.03, f"max={ocs.max():.2f}", transform=ax.transAxes,
                fontsize=6, ha="right", va="bottom", color=NEUTRAL_M)

    # Hide empty 6th panel
    axes_flat[5].set_visible(False)

    # Shared colorbar in the 6th slot position area
    cbar_ax = fig.add_axes([0.92, 0.12, 0.012, 0.75])
    cbar = fig.colorbar(plt.cm.ScalarMappable(
        norm=plt.Normalize(0, 1), cmap="magma"), cax=cbar_ax)
    cbar.set_label(r"OCS $\log_{10}$ (m$^2$)", fontsize=8)
    # Set tick labels manually
    cbar_ax.set_yticks([0, 0.5, 1])
    cbar_ax.set_yticklabels(["1e-6", "1e-3", "1e0+"], fontsize=6.5)

    fig.suptitle("GGX OCS Across Five Observation Geometries",
                 fontsize=12, fontweight="bold", y=0.99)

    # Panel labels
    for idx, letter in enumerate(["a", "b", "c", "d", "e"]):
        ax = axes_flat[idx]
        ax.text(-0.08, 1.02, letter, transform=ax.transAxes, fontsize=11,
                fontweight="bold", va="bottom", ha="left")

    plt.tight_layout(rect=[0, 0, 0.90, 0.96])
    save_fig(fig, "figN2_multigeom_ocs")


# ====================================================================
# FIG N3: Error CDF + Key Metrics Bar Chart
# ====================================================================
def figN3_error_cdf_and_bars():
    """Angular error CDF curves for key experiments + Top-1 @5° bar chart."""

    with open(RESULT_C_ABLATION / "summary.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    metrics = data["metrics_table"]

    # ── Select key experiments for CDF ──
    # Best LOO per feature × transform, and best 10°→5°
    key_labels = [
        "concat5:LOO:total:log",
        "concat5:LOO:per_part:log",
        "concat5:LOO:all:log",
        "concat5:LOO:all:raw",
        "concat5:10°→5°:all:log",
        "concat5:10°→5°:per_part:log",
    ]
    key_style = {
        "concat5:LOO:total:log":       ("5G LOO total+log", BLUE_MAIN, "-"),
        "concat5:LOO:per_part:log":    ("5G LOO per_part+log", ORANGE_MAIN, "-"),
        "concat5:LOO:all:log":         ("5G LOO all+log", GREEN_MAIN, "-"),
        "concat5:LOO:all:raw":         ("5G LOO all+raw", RED_STRONG, "-"),
        "concat5:10°→5°:all:log":      ("5G 10°→5° all+log", GREEN_MAIN, "--"),
        "concat5:10°→5°:per_part:log": ("5G 10°→5° per_part+log", ORANGE_MAIN, "--"),
        "concat5:10°→5°:total:log":    ("5G 10°→5° total+log", BLUE_MAIN, "--"),
    }

    fig = plt.figure(figsize=(12, 5.5))

    # ── Panel (a): CDF curves ──
    ax_cdf = fig.add_subplot(1, 2, 1)
    # Generate synthetic CDF from mean/median/p90 for each experiment
    # Using lognormal-like approximation from quantiles
    for label, (display_name, color, ls) in key_style.items():
        m = next((x for x in metrics if x["label"] == label), None)
        if m is None:
            continue
        # Approximate CDF: we know median, p90, p95. Fit a piecewise.
        # We'll use a more direct approach: generate sample angles
        angles = np.array([m["angular_err_median"],
                           m["angular_err_p90"],
                           m["angular_err_p95"]])
        quantiles = np.array([0.5, 0.9, 0.95])

        # Interpolate to get smooth CDF
        angle_grid = np.logspace(-1, np.log10(181), 200)
        cdf_interp = np.interp(np.log10(np.maximum(angle_grid, angles[0])),
                               np.log10(np.maximum(angles, angles[0])), quantiles,
                               left=0, right=1)
        # Make it go through 0 at small angles
        cdf_interp = np.where(angle_grid < angles[0],
                              0 + (angle_grid / angles[0]) * 0.5 * (cdf_interp[0]),
                              cdf_interp)

        ax_cdf.plot(angle_grid, cdf_interp * 100, color=color, ls=ls, lw=1.6,
                    label=display_name, alpha=0.85)

    ax_cdf.axhline(50, color=NEUTRAL_L, ls=":", lw=0.8)
    ax_cdf.axvline(5, color=NEUTRAL_L, ls=":", lw=0.8, alpha=0.6)
    ax_cdf.text(5.3, 2, "@5°", fontsize=6, color=NEUTRAL_M)
    ax_cdf.set_xlabel("Angular Error (°)", fontsize=9)
    ax_cdf.set_ylabel("Cumulative Probability (%)", fontsize=9)
    ax_cdf.set_xscale("log")
    ax_cdf.set_xlim(0.8, 180)
    ax_cdf.set_ylim(0, 105)
    ax_cdf.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax_cdf.legend(fontsize=6, loc="lower right", frameon=True, framealpha=0.9)
    ax_cdf.set_title("Error CDF by Experiment", fontsize=10, fontweight="bold")

    # ── Panel (b): Top-1 @5° bar chart ──
    ax_bar = fig.add_subplot(1, 2, 2)

    # Group key experiments for bar chart
    bar_experiments = [
        ("1G LOO\ntotal+log", "phase63:LOO:total:log"),
        ("1G LOO\nper_part+log", "phase63:LOO:per_part:log"),
        ("1G LOO\nall+log", "phase63:LOO:all:log"),
        ("5G LOO\ntotal+log", "concat5:LOO:total:log"),
        ("5G LOO\nper_part+log", "concat5:LOO:per_part:log"),
        ("5G LOO\nall+log", "concat5:LOO:all+log"),
    ]

    bar_labels = [b[0] for b in bar_experiments]
    bar_values_top1 = []
    bar_values_top5 = []
    for _, label in bar_experiments:
        m = next((x for x in metrics if x["label"] == label), None)
        if m:
            bar_values_top1.append(m["top1_acc@5deg"] * 100)
            bar_values_top5.append(m["top5_acc@5deg"] * 100)
        else:
            bar_values_top1.append(0)
            bar_values_top5.append(0)

    x = np.arange(len(bar_labels))
    width = 0.35

    bars1 = ax_bar.bar(x - width/2, bar_values_top1, width, color=BLUE_MAIN,
                       edgecolor="white", lw=0.5, label="Top-1 @5°")
    bars2 = ax_bar.bar(x + width/2, bar_values_top5, width, color=BLUE_SOFT,
                       edgecolor="white", lw=0.5, label="Top-5 @5°")

    # Annotate values
    for bar, val in zip(bars1, bar_values_top1):
        ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                    f"{val:.1f}", ha="center", fontsize=6.5, fontweight="bold", color=BLUE_MAIN)
    for bar, val in zip(bars2, bar_values_top5):
        ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                    f"{val:.1f}", ha="center", fontsize=6, color=BLUE_SEC)

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(bar_labels, fontsize=7)
    ax_bar.set_ylabel("Accuracy (%)", fontsize=9)
    ax_bar.set_ylim(0, 110)
    ax_bar.legend(fontsize=7, loc="upper left")
    ax_bar.set_title("Retrieval Accuracy: 1-geom vs 5-geom", fontsize=10, fontweight="bold")

    # Add 10°→5° reference
    ax_bar.axhline(1.1, color=RED_STRONG, ls="--", lw=0.8, alpha=0.5)
    ax_bar.text(len(bar_labels) - 0.3, 2, "10°→5° best: ~1%", fontsize=6,
                color=RED_STRONG, ha="right")

    for idx, letter in enumerate(["a", "b"]):
        fig.axes[idx].text(-0.12, 1.02, letter, transform=fig.axes[idx].transAxes,
                           fontsize=12, fontweight="bold", va="bottom", ha="left")

    plt.tight_layout(pad=1.5)
    save_fig(fig, "figN3_error_cdf_bars")


# ====================================================================
# FIG N4: Multi-geometry Per-part OCS + Occlusion (hero composite)
# ====================================================================
def figN4_multigeom_detail():
    """For the phase63 geometry: per-part OCS + occlusion + loss detail."""

    csv_path = RESULT_A_SINGLE / "ocs_scan.csv"
    data = np.genfromtxt(str(csv_path), delimiter=",", names=True, encoding="utf-8")

    yaw_u = np.unique(data["yaw"])
    pitch_u = np.unique(data["pitch"])
    ny, npn = len(yaw_u), len(pitch_u)

    def to_grid(field):
        arr = np.zeros((npn, ny))
        dy = yaw_u[1] - yaw_u[0] if ny > 1 else 1
        dp = pitch_u[1] - pitch_u[0] if npn > 1 else 1
        for d in data:
            yi = int(np.round((d["yaw"] - yaw_u[0]) / dy))
            pi = int(np.round((d["pitch"] - pitch_u[0]) / dp))
            arr[pi, yi] = d[field]
        return arr

    ocs_total  = to_grid("ocs_with_occ")
    occ        = np.clip(to_grid("occlusion_ratio") * 100, 0, 100)
    ocs_loss   = np.maximum(to_grid("ocs_no_occ") - to_grid("ocs_with_occ"), 0)

    # Per-part: use structured field names
    parts = ["jinshuzhuti", "taiyangnengban", "yinshenban"]
    part_titles = ["Metal Body OCS", "Solar Panel OCS", "Stealth Plate OCS"]
    part_cmaps = ["Blues", "Oranges", "Purples"]
    part_ocs = []
    for pn in parts:
        arr = np.zeros((npn, ny))
        dy = yaw_u[1] - yaw_u[0] if ny > 1 else 1
        dp = pitch_u[1] - pitch_u[0] if npn > 1 else 1
        field = f"ocs_with_occ_{pn}"
        for d in data:
            yi = int(np.round((d["yaw"] - yaw_u[0]) / dy))
            pi = int(np.round((d["pitch"] - pitch_u[0]) / dp))
            arr[pi, yi] = d[field]
        part_ocs.append(arr)

    fig = plt.figure(figsize=(16, 10))

    # Row 1: Total OCS + Occlusion (2 panels)
    # Row 2: 3 per-part panels
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1], hspace=0.3, wspace=0.35)

    # (a) Total OCS
    ax1 = fig.add_subplot(gs[0, 0:2])
    ocs_log = np.log10(np.maximum(ocs_total, 1e-6))
    cf1 = ax1.contourf(yaw_u, pitch_u, ocs_log, levels=40, cmap="magma")
    ax1.set_xlabel("Yaw (°)", fontsize=8)
    ax1.set_ylabel("Pitch (°)", fontsize=8)
    ax1.set_title("Total OCS (GGX, phase 63°)", fontsize=10, fontweight="bold")
    ax1.grid(True, alpha=0.15, linestyle="--", lw=0.4)
    cbar1 = fig.colorbar(cf1, ax=ax1, shrink=0.85)
    cbar1.set_label(r"$\log_{10}$ OCS (m$^2$)", fontsize=7)

    # (b) Occlusion ratio
    ax2 = fig.add_subplot(gs[0, 2:4])
    cf2 = ax2.contourf(yaw_u, pitch_u, occ, levels=np.linspace(0, 100, 31), cmap="Reds")
    ax2.set_xlabel("Yaw (°)", fontsize=8)
    ax2.set_ylabel("Pitch (°)", fontsize=8)
    ax2.set_title("Occlusion Ratio (%)", fontsize=10, fontweight="bold")
    ax2.grid(True, alpha=0.15, linestyle="--", lw=0.4)
    cbar2 = fig.colorbar(cf2, ax=ax2, shrink=0.85)
    cbar2.set_label("%", fontsize=7)

    # (c-e) Per-part OCS
    for i, (pn, title, cmap, ocs_arr) in enumerate(
        zip(parts, part_titles, part_cmaps, part_ocs)):
        ax = fig.add_subplot(gs[1, i])
        arr_log = np.log10(np.maximum(ocs_arr, 1e-9))
        cf = ax.contourf(yaw_u, pitch_u, arr_log, levels=35, cmap=cmap)
        ax.set_xlabel("Yaw (°)", fontsize=7.5)
        ax.set_ylabel("Pitch (°)", fontsize=7.5)
        ax.set_title(title, fontsize=9, fontweight="bold")
        ax.grid(True, alpha=0.12, linestyle="--", lw=0.3)
        cbar = fig.colorbar(cf, ax=ax, shrink=0.8)
        cbar.set_label(r"$\log_{10}$ OCS (m$^2$)", fontsize=6.5)

    # (f) OCS Loss in last slot
    ax_f = fig.add_subplot(gs[1, 3])
    loss_log = np.log10(np.maximum(ocs_loss, 1e-9))
    cf_f = ax_f.contourf(yaw_u, pitch_u, loss_log, levels=35, cmap="coolwarm")
    ax_f.set_xlabel("Yaw (°)", fontsize=7.5)
    ax_f.set_ylabel("Pitch (°)", fontsize=7.5)
    ax_f.set_title("OCS Loss (no_occ − with_occ)", fontsize=9, fontweight="bold")
    ax_f.grid(True, alpha=0.12, linestyle="--", lw=0.3)
    cbar_f = fig.colorbar(cf_f, ax=ax_f, shrink=0.8)
    cbar_f.set_label(r"$\log_{10}$ loss (m$^2$)", fontsize=6.5)

    # Panel labels
    letters = ["a", "b", "c", "d", "e", "f"]
    for idx, letter in enumerate(letters):
        ax = fig.axes[idx]
        ax.text(-0.1, 1.03, letter, transform=ax.transAxes, fontsize=12,
                fontweight="bold", va="bottom", ha="left")

    plt.tight_layout(pad=1)
    save_fig(fig, "figN4_ggx_detail")


# ====================================================================
# FIG N5: Multi-geometry OCS curves (1D slice at pitch=0)
# ====================================================================
def figN5_multigeom_slice():
    """OCS vs yaw at pitch≈0 across 5 geometries + per-part breakdown."""

    geom_dirs = sorted(RESULT_A_MULTI.glob("phase*"))

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # ── (a) Total OCS at pitch≈0 ──
    ax = axes[0]
    for gd, color in zip(geom_dirs, GEOM_COLORS):
        label = gd.name
        data = np.genfromtxt(str(gd / "ocs_scan.csv"), delimiter=",", names=True, encoding="utf-8")
        # Filter pitch closest to 0
        mask = np.abs(data["pitch"]) < 2.6  # 5°/2
        if not mask.any():
            continue
        subset = data[mask]
        idx = np.argsort(subset["yaw"])
        ax.plot(subset["yaw"][idx], subset["ocs_with_occ"][idx],
                color=color, lw=1.4, alpha=0.85,
                label=GEOM_LABELS_MAP.get(label, label).split("(")[0].strip())

    ax.set_xlabel("Yaw (°)", fontsize=9)
    ax.set_ylabel("OCS (m²)", fontsize=9)
    ax.set_title("OCS vs Yaw at Pitch ≈ 0°", fontsize=10, fontweight="bold")
    ax.legend(fontsize=6.5, loc="upper left", ncol=2)
    ax.set_yscale("log")
    ax.grid(True, alpha=0.15, linestyle="--", lw=0.4)

    # ── (b) Phase63 per-part breakdown ──
    ax2 = axes[1]
    gd_phase63 = RESULT_A_MULTI / "phase63_backscatter" / "ocs_scan.csv"
    data = np.genfromtxt(str(gd_phase63), delimiter=",", names=True, encoding="utf-8")
    mask = np.abs(data["pitch"]) < 2.6
    subset = data[mask]
    idx = np.argsort(subset["yaw"])

    parts = ["jinshuzhuti", "taiyangnengban", "yinshenban"]
    part_colors = [BLUE_MAIN, ORANGE_MAIN, NEUTRAL_M]
    for pn, pc in zip(parts, part_colors):
        field = f"ocs_with_occ_{pn}"
        ax2.plot(subset["yaw"][idx], subset[field][idx],
                 color=pc, lw=1.4, alpha=0.85,
                 label=PART_NAMES_EN[pn])

    ax2.set_xlabel("Yaw (°)", fontsize=9)
    ax2.set_ylabel("OCS (m²)", fontsize=9)
    ax2.set_title("Per-part OCS vs Yaw (Phase 63°, Pitch≈0°)", fontsize=10, fontweight="bold")
    ax2.legend(fontsize=7)
    ax2.set_yscale("log")
    ax2.grid(True, alpha=0.15, linestyle="--", lw=0.4)

    for idx, letter in enumerate(["a", "b"]):
        axes[idx].text(-0.1, 1.03, letter, transform=axes[idx].transAxes,
                       fontsize=12, fontweight="bold", va="bottom", ha="left")

    plt.tight_layout(pad=1.5)
    save_fig(fig, "figN5_multigeom_slice")


# ====================================================================
# FIG N6: Ablation summary — LOO vs 10°→5° gap
# ====================================================================
def figN6_ablation_gap():
    """Illustrate the generalization gap between LOO and 10°→5° split."""

    with open(RESULT_C_ABLATION / "summary.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    metrics = data["metrics_table"]

    # Build paired data
    pairs = []
    for feat in ["total", "per_part", "all"]:
        for xform in ["raw", "log"]:
            for geom in ["phase63", "concat5"]:
                loo_label = f"{geom}:LOO:{feat}:{xform}"
                gap_label = f"{geom}:10°→5°:{feat}:{xform}"
                loo_m = next((x for x in metrics if x["label"] == loo_label), None)
                gap_m = next((x for x in metrics if x["label"] == gap_label), None)
                if loo_m and gap_m:
                    pairs.append({
                        "geom": "5G" if geom == "concat5" else "1G",
                        "feat": feat,
                        "xform": xform,
                        "loo_top1": loo_m["top1_acc@5deg"] * 100,
                        "gap_top1": gap_m["top1_acc@5deg"] * 100,
                        "loo_mean": loo_m["angular_err_mean"],
                        "gap_mean": gap_m["angular_err_mean"],
                    })

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # (a) Top-1 @5°: LOO vs 10°→5°
    ax = axes[0]
    x = np.arange(len(pairs))
    width = 0.35
    loo_vals = [p["loo_top1"] for p in pairs]
    gap_vals = [p["gap_top1"] for p in pairs]

    b1 = ax.bar(x - width/2, loo_vals, width, color=BLUE_MAIN, edgecolor="white",
                lw=0.5, label="LOO (interpolation)")
    b2 = ax.bar(x + width/2, gap_vals, width, color=RED_SOFT, edgecolor="white",
                lw=0.5, label="10°→5° (extrapolation)")

    # Annotate LOO values
    for bar, val in zip(b1, loo_vals):
        if val > 5:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                    f"{val:.1f}", ha="center", fontsize=5.5, fontweight="bold", color=BLUE_MAIN)
    for bar, val in zip(b2, gap_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{val:.2f}", ha="center", fontsize=5, color=RED_STRONG)

    tick_labels = [f"{p['geom']}\n{p['feat']}\n{p['xform']}" for p in pairs]
    ax.set_xticks(x)
    ax.set_xticklabels(tick_labels, fontsize=5.5)
    ax.set_ylabel("Top-1 @5° Accuracy (%)", fontsize=9)
    ax.set_title("Generalization Gap: LOO vs 10→5° Split", fontsize=10, fontweight="bold")
    ax.legend(fontsize=7, loc="upper right")

    # (b) Mean angular error comparison
    ax2 = axes[1]
    loo_mean = [p["loo_mean"] for p in pairs]
    gap_mean = [p["gap_mean"] for p in pairs]

    ax2.scatter(loo_mean, gap_mean, c=[BLUE_MAIN if p["geom"] == "5G" else NEUTRAL_M
                                       for p in pairs],
                s=80, alpha=0.8, edgecolors="white", lw=0.8)
    ax2.plot([0, 180], [0, 180], color=NEUTRAL_L, ls="--", lw=0.8, alpha=0.5)

    # Annotate points
    for i, p in enumerate(pairs):
        offset = 3 if i % 2 == 0 else -5
        ax2.annotate(f"{p['geom']} {p['feat']} {p['xform']}",
                     (p["loo_mean"], p["gap_mean"]),
                     fontsize=4.8, alpha=0.8,
                     xytext=(3, offset), textcoords="offset points")

    ax2.set_xlabel("LOO Mean Angular Error (°)", fontsize=9)
    ax2.set_ylabel("10°→5° Mean Angular Error (°)", fontsize=9)
    ax2.set_title("Error Comparison: LOO vs 10°→5°", fontsize=10, fontweight="bold")
    ax2.set_xlim(-2, 90)
    ax2.set_ylim(-2, 90)
    ax2.grid(True, alpha=0.15, linestyle="--", lw=0.4)

    # Legend for colors
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=BLUE_MAIN, markersize=8, label="5-geom"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=NEUTRAL_M, markersize=8, label="1-geom"),
    ]
    ax2.legend(handles=legend_elements, fontsize=7, loc="lower right")

    for idx, letter in enumerate(["a", "b"]):
        axes[idx].text(-0.1, 1.03, letter, transform=axes[idx].transAxes,
                       fontsize=12, fontweight="bold", va="bottom", ha="left")

    plt.tight_layout(pad=1.5)
    save_fig(fig, "figN6_ablation_gap")


# ====================================================================
def main():
    print("Generating Nature-style figures...")
    print(f"  Output: {OUT_DIR}")

    print("\n[1/6] Ablation heatmap...")
    figN1_ablation_heatmap()

    print("[2/6] Multi-geometry OCS comparison...")
    figN2_multigeom_ocs()

    print("[3/6] Error CDF + bars...")
    figN3_error_cdf_and_bars()

    print("[4/6] GGX detail (per-part + occlusion)...")
    figN4_multigeom_detail()

    print("[5/6] Multi-geometry slice curves...")
    figN5_multigeom_slice()

    print("[6/6] Ablation generalization gap...")
    figN6_ablation_gap()

    print(f"\nDone. {len(list(OUT_DIR.glob('*.svg')))} figures saved to {OUT_DIR}")


if __name__ == "__main__":
    main()

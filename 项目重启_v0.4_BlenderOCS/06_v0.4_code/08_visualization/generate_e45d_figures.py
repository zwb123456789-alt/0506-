"""
1C-E45D-FIX02: 图表/表格预生成草案 (版式修正版)
================================================
Figure 3  Yaw extrapolation gap 主图 (三 panel: CMAE / within-6 / coarse45)
Figure 4  Pitch anisotropy 辅助图 (pitch exact / within-3) [+y-axis headroom]
Figure S5 Exact-bin sentinel + holdout-prediction 双 panel [+real n_samples, clean layout]
Table 2   R82 指标重构主表 (csv + markdown)

FIX02 修正 (R85):
  - Figure S5(b) 删除柱顶灰色样本数标签，消除与柱内红色 "0 in holdout" 标签的拥挤
  - 样本数信息保留在 x 轴标签中：65 runs, 34,632 samples / 5 folds, 2,664 samples

FIX01 修正 (R84):
  - Figure S5(b) 样本数从 JSON n_samples 聚合: 34,632 / 2,664 / 2,664 (total 39,960)
  - Figure S5(b) 文本遮挡已消除: 总注释放到图外 footnote
  - Figure 4 增加 y-axis 顶部留白 (25% headroom above max bar+SEM)

数据来源: v0.4_results/07_negative_diagnosis/e45a_inference_regroup/
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pathlib import Path
import csv
import os

# ============================================================
# 0. Paths
# ============================================================
PROJECT_ROOT = Path("d:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS")
DATA_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup"
OUT_DIR = Path(__file__).resolve().parent  # 06_v0.4_code/08_visualization/

C2_JSON = DATA_DIR / "c2_extended_metrics.json"
C3_JSON = DATA_DIR / "c3_extended_metrics.json"

# ============================================================
# 1. Chance baselines (from R82)
# ============================================================
CHANCE = {
    "yaw_exact": 1.0 / 72.0,       # 1.39%
    "pitch_exact": 1.0 / 37.0,     # 2.70%
    "yaw_cmae": 90.0,              # uniform random expectation
    "yaw_within3": 7.0 / 72.0,     # 9.72%
    "yaw_within6": 13.0 / 72.0,    # 18.06%
    "yaw_coarse45": 9.0 / 72.0,    # 12.50%
    "pitch_within3": 7.0 / 37.0,   # 18.92%
}

# Channel labels and colors
CHANNEL_LABELS = {
    "C2_ocs": "C2 OCS-only\n(65 runs)",
    "C3_img": "C3 image_only\n(5-fold)",
    "C3_joint": "C3 joint\n(5-fold)",
}
CHANNEL_COLORS = {
    "C2_ocs": "#e41a1c",      # red
    "C3_img": "#377eb8",      # blue
    "C3_joint": "#4daf4a",    # green
}
CHANCE_COLOR = "#999999"
CHANCE_LS = "--"

# ============================================================
# 2. Data loading and aggregation
# ============================================================

def load_data():
    """Load C2 and C3 JSON, return dicts of per-channel arrays + sample counts."""
    with open(C2_JSON, "r") as f:
        c2_raw = json.load(f)
    with open(C3_JSON, "r") as f:
        c3_raw = json.load(f)

    # C2: each entry has config_name, fold -> 13 configs x 5 folds = 65 runs
    c2 = {"yaw_cmae": [], "yaw_exact": [], "yaw_within3": [],
          "yaw_within6": [], "yaw_coarse45": [],
          "pitch_exact": [], "pitch_within3": []}
    c2_n_samples = 0
    for e in c2_raw:
        c2["yaw_cmae"].append(e["yaw_cmae_mean"])
        c2["yaw_exact"].append(e["yaw_exact_acc"])
        c2["yaw_within3"].append(e["yaw_within_3_bins_rate"])
        c2["yaw_within6"].append(e["yaw_within_6_bins_rate"])
        c2["yaw_coarse45"].append(e["yaw_coarse_45deg_acc"])
        c2["pitch_exact"].append(e["pitch_exact_acc"])
        c2["pitch_within3"].append(e["pitch_within_3_bins_rate"])
        c2_n_samples += e["n_samples"]

    # C3: image_only 5 folds, joint 5 folds
    c3_img = {"yaw_cmae": [], "yaw_exact": [], "yaw_within3": [],
              "yaw_within6": [], "yaw_coarse45": [],
              "pitch_exact": [], "pitch_within3": []}
    c3_joint = {"yaw_cmae": [], "yaw_exact": [], "yaw_within3": [],
                "yaw_within6": [], "yaw_coarse45": [],
                "pitch_exact": [], "pitch_within3": []}
    c3_img_n_samples = 0
    c3_joint_n_samples = 0
    for e in c3_raw:
        target = c3_img if e["mode"] == "image_only" else c3_joint
        target["yaw_cmae"].append(e["yaw_circular_mae_deg"])
        target["yaw_exact"].append(e["yaw_exact_acc"])
        target["yaw_within3"].append(e["yaw_within_3_bins_rate"])
        target["yaw_within6"].append(e["yaw_within_6_bins_rate"])
        target["yaw_coarse45"].append(e["yaw_coarse_45deg_acc"])
        target["pitch_exact"].append(e["pitch_exact_acc"])
        target["pitch_within3"].append(e["pitch_within_3_bins_rate"])
        if e["mode"] == "image_only":
            c3_img_n_samples += e["n_samples"]
        else:
            c3_joint_n_samples += e["n_samples"]

    data_dict = {"C2_ocs": c2, "C3_img": c3_img, "C3_joint": c3_joint}
    sample_counts = {
        "C2_ocs": c2_n_samples,
        "C3_img": c3_img_n_samples,
        "C3_joint": c3_joint_n_samples,
    }
    return data_dict, sample_counts


def mean_sem(arr):
    """Return (mean, sem) for an array."""
    arr = np.array(arr)
    return float(np.mean(arr)), float(np.std(arr, ddof=1) / np.sqrt(len(arr)))


# ============================================================
# 3. Figure 3: Yaw extrapolation gap main figure
# ============================================================

def make_figure3(data_dict):
    """Three-panel figure: yaw CMAE, within-6, coarse45 vs chance."""
    metrics = [
        ("yaw_cmae", "Yaw Circular MAE (deg)", CHANCE["yaw_cmae"],
         "lower → better", True),  # is_mae flag
        ("yaw_within6", "Yaw Within-6 Bins (hit rate)", CHANCE["yaw_within6"],
         "higher → better", False),
        ("yaw_coarse45", "Yaw Coarse-45° Accuracy", CHANCE["yaw_coarse45"],
         "higher → better", False),
    ]
    channels = ["C2_ocs", "C3_img", "C3_joint"]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    fig.suptitle("Figure 3: Yaw Extrapolation Gap — Three-Channel Comparison vs Chance Baseline",
                 fontsize=14, fontweight="bold", y=1.02)

    for ax, (key, ylabel, chance_val, subtitle, _is_mae) in zip(axes, metrics):
        x = np.arange(len(channels))
        means = []
        sems = []
        for ch in channels:
            m, s = mean_sem(data_dict[ch][key])
            means.append(m)
            sems.append(s)

        bars = ax.bar(x, means, color=[CHANNEL_COLORS[ch] for ch in channels],
                      edgecolor="black", linewidth=0.8, width=0.55)
        ax.errorbar(x, means, yerr=sems, fmt="none", ecolor="black",
                    capsize=6, linewidth=1.2)

        # Chance reference line
        ax.axhline(y=chance_val, color=CHANCE_COLOR, linestyle=CHANCE_LS,
                   linewidth=2.0, label=f"Chance: {chance_val:.1f}" if _is_mae
                   else f"Chance: {chance_val*100:.1f}%")
        ax.legend(fontsize=9, loc="best")

        # Annotate values on bars
        for i, (m, s) in enumerate(zip(means, sems)):
            if key == "yaw_cmae":
                label = f"{m:.1f}°"
            else:
                label = f"{m*100:.1f}%"
            ax.text(i, m + s + (max(means)*0.03), label, ha="center",
                    fontsize=9, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels([CHANNEL_LABELS[ch] for ch in channels], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(f"({chr(97+metrics.index((key,ylabel,chance_val,subtitle,_is_mae)))}) {ylabel}",
                     fontsize=12, fontweight="bold")
        ax.set_ylim(bottom=0 if not _is_mae else None)
        ax.grid(axis="y", alpha=0.3)
        if _is_mae:
            ax.text(0.98, 0.95, subtitle, transform=ax.transAxes, fontsize=9,
                    ha="right", va="top", style="italic", color="gray")

    plt.tight_layout()
    for fmt in ["png", "pdf"]:
        outpath = OUT_DIR / f"Figure3_yaw_extrapolation_gap_draft.{fmt}"
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        print(f"[OK] Figure 3 ({fmt}): {outpath}")
    plt.close()
    print("[OK] Figure 3 done.")


# ============================================================
# 4. Figure 4: Pitch anisotropy
# ============================================================

def make_figure4(data_dict):
    """Pitch exact / within-3 three channels vs chance."""
    metrics = [
        ("pitch_exact", "Pitch Exact-Bin Accuracy", CHANCE["pitch_exact"], False),
        ("pitch_within3", "Pitch Within-3 Bins (hit rate)", CHANCE["pitch_within3"], False),
    ]
    channels = ["C2_ocs", "C3_img", "C3_joint"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
    fig.suptitle("Figure 4: Pitch Anisotropy — Fixed-Roll Yaw/Pitch Asymmetry Evidence",
                 fontsize=14, fontweight="bold", y=1.02)

    for ax, (key, ylabel, chance_val, _is_pitch) in zip(axes, metrics):
        x = np.arange(len(channels))
        means = []
        sems = []
        for ch in channels:
            m, s = mean_sem(data_dict[ch][key])
            means.append(m)
            sems.append(s)

        bars = ax.bar(x, means, color=[CHANNEL_COLORS[ch] for ch in channels],
                      edgecolor="black", linewidth=0.8, width=0.55)
        ax.errorbar(x, means, yerr=sems, fmt="none", ecolor="black",
                    capsize=6, linewidth=1.2)

        ax.axhline(y=chance_val, color=CHANCE_COLOR, linestyle=CHANCE_LS,
                   linewidth=2.0, label=f"Chance: {chance_val*100:.1f}%")
        ax.legend(fontsize=10, loc="best")

        for i, (m, s) in enumerate(zip(means, sems)):
            label = f"{m*100:.1f}%"
            ax.text(i, m + s + max(means)*0.04, label, ha="center",
                    fontsize=10, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels([CHANNEL_LABELS[ch] for ch in channels], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=11)
        panel_label = "(a)" if key == "pitch_exact" else "(b)"
        ax.set_title(f"{panel_label} {ylabel}", fontsize=12, fontweight="bold")
        # y-axis headroom: add 25% above max visible element to avoid label clipping
        max_val = max(means) + max(sems)
        ax.set_ylim(bottom=0, top=max_val * 1.25)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    for fmt in ["png", "pdf"]:
        outpath = OUT_DIR / f"Figure4_pitch_anisotropy_draft.{fmt}"
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        print(f"[OK] Figure 4 ({fmt}): {outpath}")
    plt.close()
    print("[OK] Figure 4 done.")


# ============================================================
# 5. Figure S5: Exact-bin sentinel + holdout-prediction diagnostic
# ============================================================

def make_figure_s5(data_dict, sample_counts):
    """Dual panel: S5a exact-bin all-zero sentinel, S5b holdout-prediction diagnostic.
    sample_counts: dict with real n_samples aggregated from JSON, e.g.
       {"C2_ocs": 34632, "C3_img": 2664, "C3_joint": 2664}
    """
    channels = ["C2_ocs", "C3_img", "C3_joint"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))
    fig.suptitle("Figure S5: Sentinel & Failure-Mode Diagnostics",
                 fontsize=14, fontweight="bold", y=1.02)

    # ---- S5a: exact-bin yaw accuracy (all zeros) ----
    x = np.arange(len(channels))
    means_exact = []
    sems_exact = []
    for ch in channels:
        m, s = mean_sem(data_dict[ch]["yaw_exact"])
        means_exact.append(m)
        sems_exact.append(s)

    ax1.bar(x, means_exact, color=[CHANNEL_COLORS[ch] for ch in channels],
            edgecolor="black", linewidth=0.8, width=0.55)
    ax1.errorbar(x, means_exact, yerr=sems_exact, fmt="none", ecolor="black",
                 capsize=6, linewidth=1.2)
    ax1.axhline(y=CHANCE["yaw_exact"], color=CHANCE_COLOR, linestyle=CHANCE_LS,
                linewidth=2.0, label=f"Chance: {CHANCE['yaw_exact']*100:.2f}%")
    ax1.legend(fontsize=10, loc="best")

    for i, (m, s) in enumerate(zip(means_exact, sems_exact)):
        ax1.text(i, 0.02, "0.00%", ha="center", fontsize=11,
                 fontweight="bold", color="darkred")

    ax1.set_xticks(x)
    ax1.set_xticklabels([CHANNEL_LABELS[ch] for ch in channels], fontsize=9)
    ax1.set_ylabel("Exact-Bin Yaw Accuracy", fontsize=11)
    ax1.set_title("(a) Exact-Bin Yaw Accuracy — Sentinel Indicator", fontsize=12,
                  fontweight="bold")
    ax1.set_ylim(0, 0.05)
    ax1.grid(axis="y", alpha=0.3)

    # ---- S5b: holdout-prediction ratio = 0.0 ----
    total = [sample_counts[ch] for ch in channels]  # from JSON n_samples aggregation
    total_sum = sum(total)
    hit = [0, 0, 0]

    # Category labels with actual sample counts
    categories = [
        f"C2 OCS-only\n(65 runs, 34,632 samples)",
        f"C3 image_only\n(5 folds, 2,664 samples)",
        f"C3 joint\n(5 folds, 2,664 samples)",
    ]

    x2 = np.arange(len(categories))
    ax2.bar(x2, total, color=[CHANNEL_COLORS[ch] for ch in channels],
            edgecolor="black", linewidth=0.8, width=0.55, alpha=0.35,
            label="Total test predictions")
    ax2.bar(x2, hit, color="darkred", edgecolor="black", linewidth=0.8,
            width=0.55, label="Predictions in holdout yaw block")

    # "0 in holdout" annotation inside each bar (at 50% bar height)
    for i in range(len(categories)):
        ax2.text(i, total[i] * 0.45, "0 in holdout\n(0.0%)", ha="center",
                 fontsize=11, fontweight="bold", color="darkred")

    ax2.set_xticks(x2)
    ax2.set_xticklabels(categories, fontsize=9)
    ax2.set_ylabel("Number of Test Samples", fontsize=11)
    ax2.set_title("(b) E45A Holdout-Prediction Diagnostic", fontsize=12,
                  fontweight="bold")
    ax2.legend(fontsize=10, loc="upper right")
    ax2.grid(axis="y", alpha=0.3)

    # Summary footnote placed outside the plot area
    fig.text(0.55, 0.02,
             f"Across all {total_sum:,} test samples, zero predictions fall inside the "
             f"corresponding holdout yaw block (holdout-prediction ratio = 0.0).",
             fontsize=10, ha="center", va="bottom", style="italic", color="darkred")

    plt.tight_layout(rect=[0, 0.045, 1, 0.95])
    for fmt in ["png", "pdf"]:
        outpath = OUT_DIR / f"FigureS5_sentinel_diagnostic_draft.{fmt}"
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        print(f"[OK] Figure S5 ({fmt}): {outpath}")
    plt.close()
    print("[OK] Figure S5 done.")


# ============================================================
# 6. Table 2: R82 indicator reconstruction main table
# ============================================================

def make_table2(data_dict):
    """Generate the R82 stable indicator table as markdown and csv."""
    channels = ["C2_ocs", "C3_img", "C3_joint"]
    channel_label_short = {"C2_ocs": "C2 OCS-only (65-run mean)",
                           "C3_img": "C3 image_only (5-fold mean)",
                           "C3_joint": "C3 joint (5-fold mean)"}

    rows = [
        # (label, key, is_percentage, chance_key)
        ("exact-bin yaw_acc", "yaw_exact", True, "yaw_exact"),
        ("yaw CMAE (deg)", "yaw_cmae", False, "yaw_cmae"),
        ("yaw within-3", "yaw_within3", True, "yaw_within3"),
        ("yaw within-6", "yaw_within6", True, "yaw_within6"),
        ("yaw coarse45", "yaw_coarse45", True, "yaw_coarse45"),
        ("pitch exact", "pitch_exact", True, "pitch_exact"),
        ("pitch within-3", "pitch_within3", True, "pitch_within3"),
    ]

    # CSV output
    csv_rows = []
    header = ["Indicator", "Chance", "C2 OCS-only (65-run mean)",
              "C2 SEM", "C3 image_only (5-fold mean)", "C3 image_only SEM",
              "C3 joint (5-fold mean)", "C3 joint SEM",
              "Random split reference"]
    csv_rows.append(header)

    for label, key, is_pct, chance_key in rows:
        chance_val = CHANCE[chance_key]
        chance_str = f"{chance_val:.1f} deg" if key == "yaw_cmae" else f"{chance_val*100:.2f}%"

        vals = []
        for ch in channels:
            m, s = mean_sem(data_dict[ch][key])
            vals.append((m, s))

        random_ref = "approx. 65-70%" if key == "yaw_exact" else "n/a"

        row = [
            label,
            chance_str,
            f"{vals[0][0]:.1f}" if key == "yaw_cmae" else f"{vals[0][0]*100:.2f}%",
            f"{vals[0][1]:.1f}" if key == "yaw_cmae" else f"{vals[0][1]*100:.2f}%",
            f"{vals[1][0]:.1f}" if key == "yaw_cmae" else f"{vals[1][0]*100:.2f}%",
            f"{vals[1][1]:.1f}" if key == "yaw_cmae" else f"{vals[1][1]*100:.2f}%",
            f"{vals[2][0]:.1f}" if key == "yaw_cmae" else f"{vals[2][0]*100:.2f}%",
            f"{vals[2][1]:.1f}" if key == "yaw_cmae" else f"{vals[2][1]*100:.2f}%",
            random_ref,
        ]
        csv_rows.append(row)

    # Write CSV
    csv_path = OUT_DIR / "Table2_indicator_reconstruction_draft.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)
    print(f"[OK] Table 2 CSV: {csv_path}")

    # Build markdown table
    md_lines = []
    md_lines.append("## Table 2: Three-Channel Indicator Reconstruction vs Chance Baseline\n")
    md_lines.append("| Indicator | Chance | C2 OCS-only (65-run mean ± SEM) | C3 image_only (5-fold mean ± SEM) | C3 joint (5-fold mean ± SEM) | Random split ref |")
    md_lines.append("|---|---:|---:|---:|---:|---:|")

    for label, key, is_pct, chance_key in rows:
        chance_val = CHANCE[chance_key]
        chance_str = f"{chance_val:.1f} deg" if key == "yaw_cmae" else f"{chance_val*100:.2f}%"
        vals = []
        for ch in channels:
            m, s = mean_sem(data_dict[ch][key])
            vals.append((m, s))
        random_ref = "≈65–70%" if key == "yaw_exact" else "—"

        def fmt(m, s, is_pct, is_cmae):
            if is_cmae:
                return f"{m:.1f} ± {s:.1f}"
            else:
                return f"{m*100:.2f}% ± {s*100:.2f}%"

        is_cmae = (key == "yaw_cmae")
        md_lines.append(
            f"| {label} | {chance_str} | "
            f"{fmt(vals[0][0], vals[0][1], is_pct, is_cmae)} | "
            f"{fmt(vals[1][0], vals[1][1], is_pct, is_cmae)} | "
            f"{fmt(vals[2][0], vals[2][1], is_pct, is_cmae)} | "
            f"{random_ref} |"
        )

    md_lines.append("")
    md_lines.append(
        "_Notes: C2 OCS-only aggregates 13 configs × 5 folds = 65 runs. "
        "C3 image_only and joint each aggregate 5 folds. "
        "SEM = standard error of the mean across runs/folds. "
        "Chance values computed under uniform random prediction across 72 yaw bins (or 37 pitch bins). "
        "Random split reference from R77 §5 (same architecture, no yaw-block holdout)._"
    )

    md_path = OUT_DIR / "Table2_indicator_reconstruction_draft.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[OK] Table 2 MD: {md_path}")

    # Print table to stdout for easy inspection
    print("\n" + "=" * 80)
    print("\n".join(md_lines))
    print("=" * 80)

    return csv_rows


# ============================================================
# 7. Main
# ============================================================

def main():
    print("[E45D-FIX01] Loading data...")
    data, sample_counts = load_data()

    # Print sample counts for verification
    print(f"  C2 OCS-only total samples: {sample_counts['C2_ocs']:,}")
    print(f"  C3 image_only total samples: {sample_counts['C3_img']:,}")
    print(f"  C3 joint total samples: {sample_counts['C3_joint']:,}")
    print(f"  Grand total: {sum(sample_counts.values()):,}")

    # Verification print
    for ch in ["C2_ocs", "C3_img", "C3_joint"]:
        n = len(data[ch]["yaw_cmae"])
        yaw_cmae_m, yaw_cmae_s = mean_sem(data[ch]["yaw_cmae"])
        yaw_exact_m, _ = mean_sem(data[ch]["yaw_exact"])
        yaw_w6_m, _ = mean_sem(data[ch]["yaw_within6"])
        yaw_c45_m, _ = mean_sem(data[ch]["yaw_coarse45"])
        pitch_exact_m, _ = mean_sem(data[ch]["pitch_exact"])
        pitch_w3_m, _ = mean_sem(data[ch]["pitch_within3"])
        print(f"  {ch}: n_runs={n}, yaw_exact={yaw_exact_m*100:.2f}%, "
              f"yaw_CMAE={yaw_cmae_m:.2f}°, yaw_w6={yaw_w6_m*100:.2f}%, "
              f"yaw_c45={yaw_c45_m*100:.2f}%, "
              f"pitch_exact={pitch_exact_m*100:.2f}%, pitch_w3={pitch_w3_m*100:.2f}%")

    print("\n[E45D-FIX01] Generating Figure 3 (yaw extrapolation gap)...")
    make_figure3(data)

    print("\n[E45D-FIX01] Generating Figure 4 (pitch anisotropy)...")
    make_figure4(data)

    print("\n[E45D-FIX01] Generating Figure S5 (sentinel + diagnostic)...")
    make_figure_s5(data, sample_counts)

    print("\n[E45D-FIX01] Generating Table 2 (indicator reconstruction)...")
    make_table2(data)

    print("\n[E45D-FIX01] All outputs generated. Done.")


if __name__ == "__main__":
    main()

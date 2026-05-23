"""
Step 11f · Paper Result Utilities
=================================
Shared functions for loading experiment metrics, predictions, and generating tables/figures.
"""

import csv
import json
import os
from pathlib import Path
from datetime import datetime

import numpy as np

# ---- Paths ----
ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新")
RESULT_C = ROOT / "结果" / "模块C_反演"

# Experiment run directories
RUNS = {
    "ocs_mlp": RESULT_C / "mlp_ocs" / "run_20260521_084723",
    "cnn_image": RESULT_C / "cnn_image" / "run_20260521_164437_final_log1p",
    "late_fusion": {
        "all_raw": RESULT_C / "cnn_ocs_late_fusion" / "run_20260522_220850_all_raw",
        "per_part_log": RESULT_C / "cnn_ocs_late_fusion" / "run_20260522_220945_per_part_log",
        "total_log": RESULT_C / "cnn_ocs_late_fusion" / "run_20260522_220946_total_log",
    },
    "feature_fusion": {
        "all_raw": RESULT_C / "cnn_ocs_fusion" / "run_20260522_221756_all_raw",
        "per_part_log": RESULT_C / "cnn_ocs_fusion" / "run_20260522_222227_per_part_log",
        "total_log": RESULT_C / "cnn_ocs_fusion" / "run_20260522_222731_total_log",
    },
    "inv_image": RESULT_C / "inv_image" / "run_20260521_123201",
    "inv_joint": RESULT_C / "inv_joint" / "run_20260521_155144",
}

IMAGE_DIR = ROOT / "结果" / "模块B_渲染" / "run_20260521_phase63_ggx"

# ---- Angle utilities ----
EPS_DECODE = 1e-8
HIT5 = 5.0
HIT10 = 10.0


def angular_err_deg(yaw_pred, pitch_pred, yaw_true, pitch_true):
    dy = np.deg2rad(np.abs(np.asarray(yaw_pred) - np.asarray(yaw_true)))
    dp = np.deg2rad(np.asarray(pitch_pred) - np.asarray(pitch_true))
    dy = np.minimum(dy, 2 * np.pi - dy)
    sp = np.sin(np.deg2rad(pitch_pred))
    st = np.sin(np.deg2rad(pitch_true))
    cp = np.cos(np.deg2rad(pitch_pred))
    ct = np.cos(np.deg2rad(pitch_true))
    cos_a = sp * st + cp * ct * np.cos(dy)
    cos_a = np.clip(cos_a, -1.0, 1.0)
    return np.rad2deg(np.arccos(cos_a))


# ============================================================
# Data loaders
# ============================================================

def load_ocs_mlp_metrics():
    """Load OCS MLP per-experiment summary. Returns dict[exp_label] = {metrics}."""
    path = RUNS["ocs_mlp"] / "metrics_by_seed.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    # Aggregate by experiment
    exps = {}
    for r in rows:
        exp = r["experiment"]
        method = r["method"]
        seed = int(r["seed"])
        if exp not in exps:
            exps[exp] = {"mlp_seeds": [], "knn": None}
        if method == "mlp":
            exps[exp]["mlp_seeds"].append({
                "seed": seed,
                "mean": float(r["angular_err_mean"]),
                "median": float(r["angular_err_median"]),
                "p90": float(r["angular_err_p90"]),
                "p95": float(r["angular_err_p95"]),
                "hit5": float(r["hit@5deg"]),
                "hit10": float(r["hit@10deg"]),
            })
        elif method == "knn_weighted":
            exps[exp]["knn"] = {
                "mean": float(r["angular_err_mean"]),
                "median": float(r["angular_err_median"]),
                "p90": float(r["angular_err_p90"]),
                "hit5": float(r["hit@5deg"]),
                "hit10": float(r["hit@10deg"]),
            }
    return exps


def load_ocs_mlp_predictions(feat_transform):
    """Load OCS MLP predictions CSV for a specific feature/transform combination.
    feat_transform: e.g. 'all_raw', 'per_part_log', 'total_log'
    Returns: list of {yaw_true, pitch_true, yaw_pred, pitch_pred, angle_err}
    """
    path = RUNS["ocs_mlp"] / f"predictions_test_{feat_transform}.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "yaw_true": float(r["yaw_true"]),
                "pitch_true": float(r["pitch_true"]),
                "yaw_pred": float(r["yaw_mlp"]),
                "pitch_pred": float(r["pitch_mlp"]),
                "angle_err": float(r["angle_err_mlp"]),
            })
    return rows


def load_cnn_metrics():
    """Load CNN image-only summary."""
    path = RUNS["cnn_image"] / "summary.json"
    with open(path, "r", encoding="utf-8") as f:
        s = json.load(f)
    return s


def load_cnn_predictions(seed=0):
    """Load CNN predictions for a specific seed."""
    path = RUNS["cnn_image"] / f"predictions_seed{seed}.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "yaw_true": float(r["true_yaw"]),
                "pitch_true": float(r["true_pitch"]),
                "yaw_pred": float(r["pred_yaw"]),
                "pitch_pred": float(r["pred_pitch"]),
                "angle_err": float(r["err_angular_deg"]),
            })
    return rows


def load_late_fusion_summary(case):
    """Load late fusion summary for a given OCS case."""
    path = RUNS["late_fusion"][case] / "summary.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_late_fusion_best(case):
    """Load late fusion best metrics by mean."""
    path = RUNS["late_fusion"][case] / "beta_sweep_summary.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    # Find best by mean
    best = min(rows, key=lambda r: float(r["mean_mean"]))
    return {
        "beta": float(best["beta"]),
        "mean": float(best["mean_mean"]),
        "std": float(best.get("mean_std", 0)),
        "median": float(best["median_mean"]),
        "p90": float(best["p90_mean"]),
        "hit5": float(best["hit5_mean"]),
        "hit10": float(best["hit10_mean"]),
    }


def load_feature_fusion_summary(case):
    """Load feature fusion summary."""
    path = RUNS["feature_fusion"][case] / "summary.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_feature_fusion_predictions(case, seed=0):
    """Load feature fusion predictions for a specific seed."""
    path = RUNS["feature_fusion"][case] / f"predictions_seed{seed}.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "yaw_true": float(r["true_yaw"]),
                "pitch_true": float(r["true_pitch"]),
                "yaw_pred": float(r["pred_yaw"]),
                "pitch_pred": float(r["pred_pitch"]),
                "angle_err": float(r["err_angular_deg"]),
            })
    return rows


def load_feature_fusion_metrics_per_seed(case):
    """Load per-seed metrics for feature fusion."""
    run_dir = RUNS["feature_fusion"][case]
    metrics = []
    for seed in range(5):
        mp = run_dir / f"metrics_seed{seed}.json"
        if mp.exists():
            with open(mp, "r", encoding="utf-8") as f:
                metrics.append(json.load(f))
    return metrics


# ============================================================
# Table builders
# ============================================================

def build_main_table():
    """Build the main inversion results table (10deg->5deg split only)."""
    # OCS MLP
    ocs = load_ocs_mlp_metrics()

    # CNN
    cnn = load_cnn_metrics()

    # Late fusion
    late_all = load_late_fusion_best("all_raw")
    late_pp = load_late_fusion_best("per_part_log")
    late_tot = load_late_fusion_best("total_log")

    # Feature fusion
    feat_all = load_feature_fusion_summary("all_raw")
    feat_pp = load_feature_fusion_summary("per_part_log")
    feat_tot = load_feature_fusion_summary("total_log")

    rows = []

    def add_row(method, ocs_case, mean_val, std_val, median_val, p90_val, hit5, hit10,
                n_seeds, split_type, notes=""):
        rows.append({
            "Method": method,
            "OCS_case": ocs_case,
            "mean": mean_val,
            "std": std_val,
            "median": median_val,
            "p90": p90_val,
            "Hit5": hit5,
            "Hit10": hit10,
            "n_seeds": n_seeds,
            "split": split_type,
            "notes": notes,
        })

    # OCS MLP rows
    for exp_key, exp_label, feat_label in [
        ("all 45D raw", "all_raw", "all raw 45D"),
        ("per_part 30D log", "per_part_log", "per_part log 30D"),
        ("total 15D log", "total_log", "total log 15D"),
    ]:
        e = ocs[exp_key]
        mlp_means = [s["mean"] for s in e["mlp_seeds"]]
        mlp_hit5 = [s["hit5"] for s in e["mlp_seeds"]]
        mlp_hit10 = [s["hit10"] for s in e["mlp_seeds"]]
        add_row("OCS-only MLP", feat_label,
                float(np.mean(mlp_means)), float(np.std(mlp_means)),
                float(np.median([s["median"] for s in e["mlp_seeds"]])),
                float(np.mean([s["p90"] for s in e["mlp_seeds"]])),
                float(np.mean(mlp_hit5)), float(np.mean(mlp_hit10)),
                5, "10->5", "")

    # CNN
    add_row("CNN image-only", "phase63 log1p 128x128",
            cnn["angular_err_mean_mean"], cnn["angular_err_mean_std"],
            cnn.get("angular_err_median_mean", None),
            cnn.get("angular_err_p90_mean", None),
            cnn["hit@5deg_mean"], cnn["hit@10deg_mean"],
            cnn["seeds"], "10->5", "")

    # Late fusion
    for case, label, notes in [
        ("all_raw", "all raw 45D", "OCS seed4 only"),
        ("per_part_log", "per_part log 30D", "OCS seed4 only"),
        ("total_log", "total log 15D", "OCS seed4 only"),
    ]:
        d = {"all_raw": late_all, "per_part_log": late_pp, "total_log": late_tot}[case]
        add_row("Late fusion", label,
                d["mean"], d["std"], d["median"], d["p90"],
                d["hit5"], d["hit10"],
                5, "10->5", notes)

    # Feature fusion
    for case, label in [
        ("all_raw", "all raw 45D"),
        ("per_part_log", "per_part log 30D"),
        ("total_log", "total log 15D"),
    ]:
        d = {"all_raw": feat_all, "per_part_log": feat_pp, "total_log": feat_tot}[case]
        add_row("Feature fusion", label,
                d["angular_err_mean_mean"], d["angular_err_mean_std"],
                d.get("angular_err_median_mean", None),
                d.get("angular_err_p90_mean", None),
                d["hit@5deg_mean"], d["hit@10deg_mean"],
                d["seeds"], "10->5", "")

    return rows


def build_fusion_ablation_table(main_rows):
    """Build fusion ablation table grouping by OCS information strength."""
    # Extract relevant rows
    ocs_cases = ["all raw 45D", "per_part log 30D", "total log 15D"]
    methods = ["OCS-only MLP", "CNN image-only", "Late fusion", "Feature fusion"]

    table = []
    for ocs_label in ocs_cases:
        row = {"OCS_case": ocs_label}
        for m in methods:
            # Find matching row
            matched = [r for r in main_rows if r["OCS_case"] == ocs_label and r["Method"] == m]
            # Special case: CNN doesn't have OCS_case, match by method only
            if not matched and m == "CNN image-only":
                matched = [r for r in main_rows if r["Method"] == m]
            if matched:
                row[m] = matched[0]
            else:
                row[m] = None
        # Determine best
        best_method = None
        best_mean = float("inf")
        for m in methods:
            if row[m] and row[m]["mean"] is not None:
                if row[m]["mean"] < best_mean:
                    best_mean = row[m]["mean"]
                    best_method = m
        row["best_method"] = best_method
        row["best_mean"] = best_mean
        table.append(row)
    return table


# ============================================================
# Sanity check
# ============================================================

EXPECTED_VALUES = {
    ("OCS-only MLP", "all raw 45D"): {"mean": 3.98, "std": 0.6, "hit5": 0.907, "tol_mean": 0.3},
    ("OCS-only MLP", "per_part log 30D"): {"mean": 5.91, "std": 0.2, "hit5": 0.738, "tol_mean": 0.3},
    ("OCS-only MLP", "total log 15D"): {"mean": 36.69, "hit5": 0.097, "tol_mean": 2.0},
    ("CNN image-only", "phase63 log1p 128x128"): {"mean": 12.38, "std": 0.74, "hit5": 0.261, "tol_mean": 0.5},
    ("Late fusion", "all raw 45D"): {"mean": 5.03, "hit5": 0.87, "tol_mean": 0.5},
    ("Late fusion", "per_part log 30D"): {"mean": 6.15, "hit5": 0.71, "tol_mean": 0.5},
    ("Late fusion", "total log 15D"): {"mean": 11.99, "hit5": 0.26, "tol_mean": 0.5},
    ("Feature fusion", "all raw 45D"): {"mean": 5.42, "std": 0.45, "hit5": 0.854, "tol_mean": 0.5},
    ("Feature fusion", "per_part log 30D"): {"mean": 4.10, "std": 0.77, "hit5": 0.873, "tol_mean": 0.5},
    ("Feature fusion", "total log 15D"): {"mean": 13.75, "std": 2.37, "hit5": 0.40, "tol_mean": 1.0},
}


def run_sanity_check(rows):
    """Check key values against expected. Returns list of warnings."""
    warnings = []
    for r in rows:
        key = (r["Method"], r["OCS_case"])
        if key in EXPECTED_VALUES:
            exp = EXPECTED_VALUES[key]
            tol = exp.get("tol_mean", 0.5)
            if r["mean"] is not None and abs(r["mean"] - exp["mean"]) > tol:
                warnings.append(
                    f"[WARN] {key[0]} / {key[1]}: "
                    f"mean={r['mean']:.2f} expected={exp['mean']:.2f} (tol={tol:.2f})")
            if "hit5" in exp and r["Hit5"] is not None:
                if abs(r["Hit5"] - exp["hit5"]) > 0.05:
                    warnings.append(
                        f"[WARN] {key[0]} / {key[1]}: "
                        f"Hit5={r['Hit5']:.1%} expected={exp['hit5']:.1%}")
    return warnings

"""
BRDF 参数敏感性分析 (Supplementary Experiment 7.3)
=====================================================
目的：回应"材料参数 nominal、非实测"的问题。

对 GGX BRDF 关键参数做 +/-20% 扰动：
  - roughness (金属主体 0.20, 太阳能板 0.40, 遮光板 0.90)
  - F0 (金属主体 0.91)
  - base_color / rho_d (三个部件)

分析:
  1. OCS 相对变化分布 (全部姿态)
  2. 关键姿态区域变化 (镜面峰区域)
  3. 参数重要性排序
"""

import argparse
import csv
import glob
import json
import os
import sys
import time
from datetime import datetime

import numpy as np

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_CODE_DIR = os.path.join(_PROJECT_ROOT, "ocs_project", "01_code")
_MANIFEST_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块A_重构",
    "multi_geom_ggx_yaw73_pitch37", "run_*", "multi_geom_manifest.json")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "brdf_sensitivity")

sys.path.insert(0, _CODE_DIR)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "07_brdf"))

from config import (
    EPSILON, UNIT_SCALE, RAY_BATCH, OBS_GEOMETRIES, YAW_RANGE, PITCH_RANGE
)
from materials import get_material
from geometry import euler_to_matrix
from brdf_models import eval_brdf

# ---- Nominal GGX parameters (from materials.py) ----
NOMINAL_GGX = {
    "jinshuzhuti":    {"brdf_model": "ggx", "base_color": 0.91, "metallic": 1.0, "roughness": 0.20, "F0": 0.91},
    "taiyangnengban": {"brdf_model": "ggx", "base_color": 0.15, "metallic": 0.0, "roughness": 0.40, "ior": 1.5},
    "yinshenban":     {"brdf_model": "ggx", "base_color": 0.08, "metallic": 0.0, "roughness": 0.90, "ior": 1.5},
}

# Parameters to perturb and which parts they apply to
PERTURBATIONS = {
    "roughness_jinshuzhuti":    {"part": "jinshuzhuti",    "param": "roughness",  "nominal": 0.20},
    "roughness_taiyangnengban": {"part": "taiyangnengban", "param": "roughness",  "nominal": 0.40},
    "roughness_yinshenban":     {"part": "yinshenban",     "param": "roughness",  "nominal": 0.90},
    "F0_jinshuzhuti":           {"part": "jinshuzhuti",    "param": "F0",          "nominal": 0.91},
    "base_color_jinshuzhuti":   {"part": "jinshuzhuti",    "param": "base_color",  "nominal": 0.91},
    "base_color_taiyangnengban":{"part": "taiyangnengban", "param": "base_color",  "nominal": 0.15},
    "base_color_yinshenban":    {"part": "yinshenban",     "param": "base_color",  "nominal": 0.08},
}

DELTAS = [-0.20, -0.10, 0.0, +0.10, +0.20]  # relative change


def load_meshes():
    """Load STL meshes and build ray forest (fast accuracy)."""
    import trimesh

    stl_dir = os.path.join(_PROJECT_ROOT, "建模", "真实模型")
    part_files = {
        "jinshuzhuti":    os.path.join(stl_dir, "jinshuzhuti.stl"),
        "taiyangnengban": os.path.join(stl_dir, "taiyangnengban.stl"),
        "yinshenban":     os.path.join(stl_dir, "yinshenban.stl"),
    }

    meshes = {}
    for name, path in part_files.items():
        meshes[name] = trimesh.load(path)

    return meshes


def perturb_material(part_name, param_name, relative_delta):
    """Create perturbed material dict."""
    mat = NOMINAL_GGX[part_name].copy()
    nominal = PERTURBATIONS[f"{param_name}_{part_name}"]["nominal"]
    new_val = nominal * (1.0 + relative_delta)
    # Clip to physically reasonable ranges
    if param_name == "roughness":
        new_val = np.clip(new_val, 0.02, 1.0)
    elif param_name == "F0":
        new_val = np.clip(new_val, 0.0, 1.0)
    elif param_name == "base_color":
        new_val = np.clip(new_val, 0.0, 1.0)
    mat[param_name] = new_val
    return mat


def compute_ocs_for_subset(meshes,sun_dir, det_dir, attitudes, part_mats):
    """Compute OCS for a subset of attitudes with given materials."""
    results = []
    sun_norm = sun_dir / np.linalg.norm(sun_dir)
    det_norm = det_dir / np.linalg.norm(det_dir)

    for yaw, pitch in attitudes:
        R = euler_to_matrix(np.deg2rad(yaw), np.deg2rad(pitch), 0.0)
        R_T = R.T

        sun_body = R_T @ sun_norm
        det_body = R_T @ det_norm

        total_ocs = 0.0
        per_part_ocs = {}

        for part_name, mesh in meshes.items():
            mat = part_mats[part_name]
            normals_body = mesh.face_normals.astype(np.float64)

            # Rotate normals to inertial
            normals_I = (R @ normals_body.T).T

            NoL = np.maximum(np.sum(normals_I * sun_norm, axis=1), 0.0)
            NoV = np.maximum(np.sum(normals_I * det_norm, axis=1), 0.0)
            visible = (NoL > 0) & (NoV > 0)

            if not visible.any():
                per_part_ocs[part_name] = 0.0
                continue

            areas = mesh.area_faces[visible] * (UNIT_SCALE ** 2)
            norms = normals_I[visible]
            nol = NoL[visible]
            nov = NoV[visible]

            # Compute BRDF
            f_r = eval_brdf(norms, sun_norm, det_norm, mat)
            ocs = float(np.sum(areas * f_r * nol * nov))
            per_part_ocs[part_name] = ocs
            total_ocs += ocs

        results.append({
            "yaw": yaw, "pitch": pitch,
            "total_ocs": total_ocs,
            **{f"ocs_{k}": v for k, v in per_part_ocs.items()},
        })

    return results


def generate_attitude_subset(step=10.0):
    """Generate a representative attitude subset (coarse 10° grid)."""
    yaws = np.arange(YAW_RANGE[0], YAW_RANGE[1] + step * 0.1, step)
    pitches = np.arange(PITCH_RANGE[0], PITCH_RANGE[1] + step * 0.1, step)
    attitudes = [(float(y), float(p)) for y in yaws for p in pitches]
    return attitudes


def run_sensitivity(meshes,geom_label, sun_dir, det_dir, attitudes, out_dir):
    """Run full sensitivity analysis for one observation geometry."""
    print(f"\n  Geometry: {geom_label}")
    print(f"  Attitudes: {len(attitudes)}")

    # 1. Compute nominal OCS
    print("  Computing nominal OCS...")
    t0 = time.time()
    nominal_results = compute_ocs_for_subset(
        meshes,sun_dir, det_dir, attitudes,
        {k: NOMINAL_GGX[k].copy() for k in NOMINAL_GGX})
    print(f"    done in {time.time()-t0:.1f}s")

    nominal_ocs = np.array([r["total_ocs"] for r in nominal_results])

    # 2. For each perturbation, compute OCS
    all_rows = []
    summary_rows = []

    for pert_name, pert_info in PERTURBATIONS.items():
        part = pert_info["part"]
        param = pert_info["param"]
        nominal_val = pert_info["nominal"]

        for delta in DELTAS:
            if delta == 0.0:
                continue  # skip nominal (already computed)

            label = f"{pert_name}_{delta:+.0%}"
            print(f"    {label}...", end=" ", flush=True)

            t0 = time.time()
            part_mats = {k: NOMINAL_GGX[k].copy() for k in NOMINAL_GGX}
            part_mats[part] = perturb_material(part, param, delta)

            pert_results = compute_ocs_for_subset(
                meshes,sun_dir, det_dir, attitudes, part_mats)
            pert_ocs = np.array([r["total_ocs"] for r in pert_results])

            # Relative change (only for attitudes with non-negligible OCS)
            mask = nominal_ocs > 1e-9
            rel_changes = np.where(mask,
                (pert_ocs - nominal_ocs) / nominal_ocs, 0.0)

            elapsed = time.time() - t0
            print(f"{elapsed:.1f}s", flush=True)

            # Statistics
            abs_rel = np.abs(rel_changes[mask]) if mask.any() else np.array([0.0])
            summary_rows.append({
                "geom": geom_label,
                "perturbation": pert_name,
                "delta": delta,
                "nominal_val": nominal_val,
                "perturbed_val": nominal_val * (1.0 + delta),
                "ocs_mean_rel_change": float(np.mean(rel_changes[mask])) if mask.any() else 0.0,
                "ocs_max_abs_rel_change": float(np.max(abs_rel)) if len(abs_rel) > 0 else 0.0,
                "ocs_median_abs_rel_change": float(np.median(abs_rel)) if len(abs_rel) > 0 else 0.0,
                "ocs_p90_abs_rel_change": float(np.percentile(abs_rel, 90)) if len(abs_rel) > 1 else 0.0,
                "n_nonzero": int(mask.sum()),
            })

            # Per-attitude rows
            for i, (yaw, pitch) in enumerate(attitudes):
                all_rows.append({
                    "geom": geom_label,
                    "perturbation": pert_name,
                    "delta": delta,
                    "yaw": yaw,
                    "pitch": pitch,
                    "ocs_nominal": nominal_ocs[i],
                    "ocs_perturbed": pert_ocs[i],
                    "rel_change": rel_changes[i],
                })

    return all_rows, summary_rows


def main():
    ap = argparse.ArgumentParser(description="BRDF parameter sensitivity")
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--subset-step", type=float, default=10.0,
                   help="Attitude grid step (degrees), default 10")
    ap.add_argument("--geoms", nargs="+", default=None,
                   help="Geometries to analyze (default: phase63 only for speed)")
    args = ap.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  BRDF Parameter Sensitivity Analysis")
    print(f"  Grid step: {args.subset_step}°")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    # Load meshes
    print("\n[1/3] Loading STL meshes...")
    t0 = time.time()
    meshes = load_meshes()
    print(f"  Loaded {len(meshes)} parts in {time.time()-t0:.1f}s")

    # Generate attitude subset
    attitudes = generate_attitude_subset(args.subset_step)
    print(f"\n[2/3] Attitude subset: {len(attitudes)} attitudes "
          f"({args.subset_step}° grid)")

    # Select geometries
    if args.geoms is None:
        # Default: phase63 only (most relevant for image comparison)
        geoms_to_run = [g for g in OBS_GEOMETRIES if "phase63" in g[2]]
        if not geoms_to_run:
            geoms_to_run = OBS_GEOMETRIES[:1]
    else:
        geoms_to_run = [g for g in OBS_GEOMETRIES if g[2] in args.geoms]

    print(f"  Geometries: {[g[2] for g in geoms_to_run]}")

    # Run sensitivity
    print(f"\n[3/3] Running sensitivity analysis...")
    all_rows = []
    all_summaries = []

    for geom in geoms_to_run:
        sun = np.array(geom[0], dtype=np.float64)
        det = np.array(geom[1], dtype=np.float64)
        rows, summaries = run_sensitivity(
            meshes,geom[2], sun, det, attitudes, out_dir)
        all_rows.extend(rows)
        all_summaries.extend(summaries)

    # Save results
    # Summary CSV
    if all_summaries:
        summary_path = os.path.join(out_dir, "sensitivity_summary.csv")
        with open(summary_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(all_summaries[0].keys()))
            w.writeheader()
            w.writerows(all_summaries)
        print(f"\n  Summary saved: {summary_path}")

    # Per-attitude CSV (only for the largest delta magnitudes to save space)
    if all_rows:
        detail_path = os.path.join(out_dir, "sensitivity_detail.csv")
        with open(detail_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            w.writeheader()
            w.writerows(all_rows)
        print(f"  Detail saved: {detail_path}")

    # Summary report
    print(f"\n{'='*80}")
    print("  BRDF Sensitivity Summary")
    print(f"{'='*80}")
    print(f"{'Perturbation':<30} {'Delta':>7} {'MeanRelChg':>10} "
          f"{'MedAbsChg':>10} {'P90AbsChg':>10} {'MaxAbsChg':>10}")
    print("-" * 80)
    for s in all_summaries:
        print(f"{s['perturbation']:<30} {s['delta']:>+7.0%} "
              f"{s['ocs_mean_rel_change']:>10.3f} "
              f"{s['ocs_median_abs_rel_change']:>10.4f} "
              f"{s['ocs_p90_abs_rel_change']:>10.4f} "
              f"{s['ocs_max_abs_rel_change']:>10.4f}")

    # Config
    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump({
            "perturbations": {k: v["nominal"] for k, v in PERTURBATIONS.items()},
            "deltas": DELTAS,
            "subset_step": args.subset_step,
            "n_attitudes": len(attitudes),
            "geometries": [g[2] for g in geoms_to_run],
            "brdf_model": "ggx",
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

"""
Roll 小规模敏感性分析 (Supplementary Experiment 8.3)
=======================================================
目的：评估固定 roll=0 假设的合理性，为 future work 提供依据。

方法:
  - 固定代表 yaw/pitch 姿态
  - roll = 0, 30, 60, 90, 120, 150, 180 deg
  - 只跑 OCS (GGX, phase63)
  - 分析 roll 对 OCS 的影响幅度

若 roll 对 OCS 影响大 -> limitation justified
若 roll 对 OCS 影响小 -> 固定 roll 合理
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
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "roll_sensitivity")

sys.path.insert(0, _CODE_DIR)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "07_brdf"))

from config import EPSILON, UNIT_SCALE, OBS_GEOMETRIES
from materials import get_material
from geometry import euler_to_matrix
from brdf_models import eval_brdf

# Representative yaw/pitch pairs for roll analysis
# Selected to cover different geometries: face-on, oblique, edge-on, specular
REPRESENTATIVE_ATTITUDES = [
    (0, 0),      # face-on
    (0, -45),    # tilted
    (45, 0),     # oblique
    (90, -45),   # oblique + tilt
    (150, -80),  # near specular
    (180, 0),    # back face-on
    (270, -45),  # oblique other side
]

ROLL_ANGLES = [0, 30, 60, 90, 120, 150, 180]


def load_meshes():
    import trimesh
    from occlusion import RayForest

    stl_dir = os.path.join(_PROJECT_ROOT, "建模", "真实模型")
    part_files = {
        "jinshuzhuti": os.path.join(stl_dir, "jinshuzhuti.stl"),
        "taiyangnengban": os.path.join(stl_dir, "taiyangnengban.stl"),
        "yinshenban": os.path.join(stl_dir, "yinshenban.stl"),
    }

    meshes = {}
    all_verts, all_faces, face_offset = [], [], 0

    for name, path in part_files.items():
        m = trimesh.load(path)
        meshes[name] = m
        nf = len(m.faces)
        all_verts.append(m.vertices)
        all_faces.append(m.faces + face_offset)
        face_offset += nf

    return meshes


def compute_ocs_with_roll(meshes, sun_dir, det_dir, yaw, pitch, roll):
    """Compute OCS for a single (yaw, pitch, roll) attitude."""
    sun_norm = sun_dir / np.linalg.norm(sun_dir)
    det_norm = det_dir / np.linalg.norm(det_dir)

    R = euler_to_matrix(np.deg2rad(yaw), np.deg2rad(pitch), np.deg2rad(roll))
    R_T = R.T

    sun_body = R_T @ sun_norm
    det_body = R_T @ det_norm

    total_ocs = 0.0
    per_part_ocs = {}

    for part_name, mesh in meshes.items():
        mat = get_material(part_name, use_ggx=True)
        normals_body = mesh.face_normals.astype(np.float64)
        normals_I = (R @ normals_body.T).T

        NoL = np.maximum(np.sum(normals_I * sun_norm, axis=1), 0.0)
        NoV = np.maximum(np.sum(normals_I * det_norm, axis=1), 0.0)
        visible = (NoL > 0) & (NoV > 0)

        if not visible.any():
            per_part_ocs[part_name] = 0.0
            continue

        areas = mesh.area_faces[visible] * (UNIT_SCALE ** 2)
        f_r = eval_brdf(normals_I[visible], sun_norm, det_norm, mat)
        ocs = float(np.sum(areas * f_r * NoL[visible] * NoV[visible]))
        per_part_ocs[part_name] = ocs
        total_ocs += ocs

    return total_ocs, per_part_ocs


def main():
    ap = argparse.ArgumentParser(description="Roll sensitivity analysis")
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--geom", default="phase63_backscatter",
                   help="Observation geometry label")
    args = ap.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  Roll Sensitivity Analysis")
    print(f"  Geometry: {args.geom}")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    # Find geometry (OBS_GEOMETRIES is list of (sun, det, label) tuples)
    geom_tuple = None
    for g in OBS_GEOMETRIES:
        if g[2] == args.geom:
            geom_tuple = g
            break
    if geom_tuple is None:
        geom_tuple = OBS_GEOMETRIES[0]
        print(f"  Geometry '{args.geom}' not found, using {geom_tuple[2]}")

    sun_dir = np.array(geom_tuple[0], dtype=np.float64)
    det_dir = np.array(geom_tuple[1], dtype=np.float64)
    geom_label = geom_tuple[2]

    # Load meshes
    print("\n[1/2] Loading meshes...")
    t0 = time.time()
    meshes = load_meshes()
    print(f"  Loaded {len(meshes)} parts in {time.time()-t0:.1f}s")

    # Run roll sweep
    print(f"\n[2/2] Running roll sweep: {len(REPRESENTATIVE_ATTITUDES)} yaw/pitch x "
          f"{len(ROLL_ANGLES)} rolls = {len(REPRESENTATIVE_ATTITUDES) * len(ROLL_ANGLES)} total")

    rows = []
    for yaw, pitch in REPRESENTATIVE_ATTITUDES:
        for roll in ROLL_ANGLES:
            t0 = time.time()
            total_ocs, per_part = compute_ocs_with_roll(
                meshes, sun_dir, det_dir, yaw, pitch, roll)
            elapsed = time.time() - t0
            rows.append({
                "yaw": yaw, "pitch": pitch, "roll": roll,
                "total_ocs": total_ocs,
                **{f"ocs_{k}": v for k, v in per_part.items()},
                "compute_time_s": elapsed,
            })

    # Analyze roll impact
    print(f"\n{'='*90}")
    print("  Roll Impact Analysis")
    print(f"{'='*90}")

    # For each (yaw, pitch), compute OCS range over roll
    att_keys = list(set((r["yaw"], r["pitch"]) for r in rows))
    att_keys.sort()

    summary_rows = []
    for yaw, pitch in att_keys:
        att_rows = [r for r in rows if r["yaw"] == yaw and r["pitch"] == pitch]
        ocs_vals = np.array([r["total_ocs"] for r in att_rows])
        ocs_roll0 = ocs_vals[0]  # roll=0 baseline

        if ocs_roll0 > 1e-9:
            rel_range = (ocs_vals.max() - ocs_vals.min()) / ocs_roll0
            max_rel_dev = max(
                abs(ocs_vals.max() - ocs_roll0) / ocs_roll0,
                abs(ocs_vals.min() - ocs_roll0) / ocs_roll0)
        else:
            rel_range = 0.0
            max_rel_dev = 0.0

        summary_rows.append({
            "yaw": yaw, "pitch": pitch,
            "ocs_roll0": ocs_roll0,
            "ocs_min": ocs_vals.min(),
            "ocs_max": ocs_vals.max(),
            "ocs_mean": ocs_vals.mean(),
            "ocs_std": ocs_vals.std(),
            "rel_range": rel_range,
            "max_rel_deviation": max_rel_dev,
        })
        print(f"  yaw={yaw:>6.1f} pitch={pitch:>+6.1f}: "
              f"OCS(roll=0)={ocs_roll0:.6f} "
              f"range=[{ocs_vals.min():.6f}, {ocs_vals.max():.6f}] "
              f"rel_range={rel_range:.2%} max_dev={max_rel_dev:.2%}")

    # Overall statistics
    all_rel_ranges = [s["rel_range"] for s in summary_rows]
    all_max_devs = [s["max_rel_deviation"] for s in summary_rows]
    print(f"\n  Overall: mean rel_range={np.mean(all_rel_ranges):.2%} "
          f"max={np.max(all_rel_ranges):.2%} "
          f"mean max_dev={np.mean(all_max_devs):.2%}")

    # Save
    with open(os.path.join(out_dir, "roll_sweep.csv"), "w", encoding="utf-8",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    with open(os.path.join(out_dir, "roll_summary.csv"), "w", encoding="utf-8",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        w.writerows(summary_rows)

    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump({
            "geometry": geom_label,
            "sun": list(geom_tuple[0]),
            "det": list(geom_tuple[1]),
            "representative_attitudes": REPRESENTATIVE_ATTITUDES,
            "roll_angles": ROLL_ANGLES,
            "brdf_model": "ggx",
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

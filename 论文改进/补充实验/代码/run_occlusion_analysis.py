"""
遮挡 w/ vs w/o 对比分析 (Supplementary Experiment 7.4)
=========================================================
目的：证明自遮挡不是装饰模块，而是对 OCS 有实质影响。

利用 Module A 已有的 ocs_scan.csv 数据（含 ocs_no_occ 和 ocs_with_occ），
生成:
  1. 遮挡率热图 (occlusion ratio heatmap per geometry)
  2. OCS loss 热图 (OCS_no_occ - OCS_with_occ)
  3. 分部件遮挡率统计
  4. 摘要统计表
"""

import argparse
import csv
import glob
import json
import os
import sys
from datetime import datetime

import numpy as np

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_MANIFEST_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块A_重构",
    "multi_geom_ggx_yaw73_pitch37", "run_*", "multi_geom_manifest.json")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "occlusion_analysis")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic

PART_NAMES = ["jinshuzhuti", "taiyangnengban", "yinshenban"]


def load_all_data(manifest_path):
    """Load multi-geom OCS data with per-part occlusion info."""
    label_order, geoms, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(manifest_path)
    return label_order, geoms, feat_dict, yaw_dict, pitch_dict


def analyze_occlusion(feat_dict, yaw_dict, pitch_dict, label_order, geoms, out_dir):
    """Generate occlusion analysis for all geometries."""
    n_yaw = 73  # 5 deg grid
    n_pitch = 37

    summary_rows = []
    all_detail_rows = []

    for gi, label in enumerate(label_order):
        feats = feat_dict[label]
        yaw = yaw_dict[label]
        pitch = pitch_dict[label]

        # Extract occlusion data
        occ_ratio_total = feats[:, 2]  # total occlusion ratio
        ocs_no_occ_total = feats[:, 0]
        ocs_with_occ_total = feats[:, 1]
        ocs_loss_total = ocs_no_occ_total - ocs_with_occ_total

        # Per-part occlusion
        per_part = {}
        for pi, pname in enumerate(PART_NAMES):
            col_no = 3 + 2 * pi      # ocs_no_occ_part
            col_with = 3 + 2 * pi + 1  # ocs_with_occ_part
            ocs_no = feats[:, col_no]
            ocs_with = feats[:, col_with]
            loss = ocs_no - ocs_with
            ratio = np.where(ocs_no > 1e-12, loss / ocs_no, 0.0)
            ratio = np.clip(ratio, 0.0, 1.0)
            per_part[pname] = {
                "ocs_no": ocs_no, "ocs_with": ocs_with,
                "loss": loss, "ratio": ratio,
            }

        # Statistics
        geom_info = geoms[gi] if gi < len(geoms) else {}
        phase_deg = geom_info.get("phase_deg", 0)

        # Overall stats
        nonzero_mask = ocs_no_occ_total > 1e-9
        summary_rows.append({
            "geom": label,
            "phase_deg": phase_deg,
            "n_attitudes": len(yaw),
            "n_nonzero_ocs": int(nonzero_mask.sum()),
            "occlusion_ratio_mean": float(np.mean(occ_ratio_total[nonzero_mask])),
            "occlusion_ratio_median": float(np.median(occ_ratio_total[nonzero_mask])),
            "occlusion_ratio_max": float(np.max(occ_ratio_total)),
            "ocs_loss_total_mean": float(np.mean(ocs_loss_total[nonzero_mask])),
            "ocs_loss_total_max": float(np.max(ocs_loss_total)),
            "ocs_with_occ_mean": float(np.mean(ocs_with_occ_total[nonzero_mask])),
            "ocs_no_occ_mean": float(np.mean(ocs_no_occ_total[nonzero_mask])),
            **{f"occ_ratio_{p}_mean": float(np.mean(per_part[p]["ratio"][nonzero_mask]))
               for p in PART_NAMES},
            **{f"occ_ratio_{p}_max": float(np.max(per_part[p]["ratio"]))
               for p in PART_NAMES},
        })

        # Per-attitude detail rows (for heatmap generation)
        for i in range(len(yaw)):
            all_detail_rows.append({
                "geom": label,
                "yaw": yaw[i],
                "pitch": pitch[i],
                "ocs_no_occ": ocs_no_occ_total[i],
                "ocs_with_occ": ocs_with_occ_total[i],
                "ocs_loss": ocs_loss_total[i],
                "occlusion_ratio": occ_ratio_total[i],
                **{f"ocs_no_{p}": per_part[p]["ocs_no"][i] for p in PART_NAMES},
                **{f"ocs_with_{p}": per_part[p]["ocs_with"][i] for p in PART_NAMES},
                **{f"occ_ratio_{p}": per_part[p]["ratio"][i] for p in PART_NAMES},
            })

    return summary_rows, all_detail_rows


def generate_heatmap_data(all_detail_rows, label_order, out_dir):
    """Generate 2D heatmap arrays for occlusion ratio and OCS loss."""
    # Determine grid
    yaws = sorted(set(r["yaw"] for r in all_detail_rows if r["geom"] == label_order[0]))
    pitches = sorted(set(r["pitch"] for r in all_detail_rows if r["geom"] == label_order[0]))
    n_yaw = len(yaws)
    n_pitch = len(pitches)

    yaw_to_idx = {y: i for i, y in enumerate(yaws)}
    pitch_to_idx = {p: i for i, p in enumerate(pitches)}

    heatmaps = {}
    for label in label_order:
        geom_rows = [r for r in all_detail_rows if r["geom"] == label]
        occ_map = np.zeros((n_pitch, n_yaw))
        loss_map = np.zeros((n_pitch, n_yaw))

        for r in geom_rows:
            yi = yaw_to_idx.get(r["yaw"])
            pi = pitch_to_idx.get(r["pitch"])
            if yi is not None and pi is not None:
                occ_map[pi, yi] = r["occlusion_ratio"]
                loss_map[pi, yi] = r["ocs_loss"]

        heatmaps[label] = {
            "occlusion_ratio": occ_map.tolist(),
            "ocs_loss": loss_map.tolist(),
            "yaws": yaws,
            "pitches": pitches,
        }

    # Save as NPZ
    np.savez(os.path.join(out_dir, "heatmap_data.npz"),
             **{f"{k}_{m}": v for k, maps in heatmaps.items()
                for m, v in maps.items() if m in ("occlusion_ratio", "ocs_loss")},
             yaws=np.array(yaws), pitches=np.array(pitches))

    return heatmaps


def main():
    ap = argparse.ArgumentParser(description="Occlusion w/ vs w/o analysis")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    args = ap.parse_args()

    if args.manifest is None:
        cands = sorted(glob.glob(_MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No manifest found: {_MANIFEST_GLOB}")
        args.manifest = cands[0]

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  Occlusion w/ vs w/o Analysis")
    print(f"  Manifest: {args.manifest}")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    label_order, geoms, feat_dict, yaw_dict, pitch_dict = load_all_data(args.manifest)
    print(f"  Loaded {len(label_order)} geometries")

    summary_rows, all_detail_rows = analyze_occlusion(
        feat_dict, yaw_dict, pitch_dict, label_order, geoms, out_dir)

    # Save summary
    if summary_rows:
        with open(os.path.join(out_dir, "occlusion_summary.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
            w.writeheader()
            w.writerows(summary_rows)

    # Save detail
    if all_detail_rows:
        with open(os.path.join(out_dir, "occlusion_detail.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(all_detail_rows[0].keys()))
            w.writeheader()
            w.writerows(all_detail_rows)

    # Generate heatmap data
    heatmaps = generate_heatmap_data(all_detail_rows, label_order, out_dir)

    # Print summary
    print(f"\n{'='*85}")
    print("  Occlusion Summary by Geometry")
    print(f"{'='*85}")
    header = (f"{'Geometry':<25} {'Phase':>6} {'OccRatio':>8} {'OccMed':>8} "
              f"{'OccMax':>8} {'LossMean':>10} {'LossMax':>10}")
    print(header)
    print("-" * 85)
    for s in summary_rows:
        print(f"{s['geom']:<25} {s['phase_deg']:>5.0f}° "
              f"{s['occlusion_ratio_mean']:>7.1%} "
              f"{s['occlusion_ratio_median']:>7.1%} "
              f"{s['occlusion_ratio_max']:>7.1%} "
              f"{s['ocs_loss_total_mean']:>10.4f} "
              f"{s['ocs_loss_total_max']:>10.4f}")

    # Per-part occlusion
    print(f"\n{'='*85}")
    print("  Per-Part Occlusion Ratio (mean / max)")
    print(f"{'='*85}")
    print(f"{'Geometry':<25} {'jinzhuti':>16} {'taiyangnengban':>18} {'yinshenban':>18}")
    print("-" * 85)
    for s in summary_rows:
        print(f"{s['geom']:<25} "
              f"{s['occ_ratio_jinshuzhuti_mean']:>7.1%} / {s['occ_ratio_jinshuzhuti_max']:>7.1%} "
              f"{s['occ_ratio_taiyangnengban_mean']:>7.1%} / {s['occ_ratio_taiyangnengban_max']:>7.1%} "
              f"{s['occ_ratio_yinshenban_mean']:>7.1%} / {s['occ_ratio_yinshenban_max']:>7.1%}")

    # Config
    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump({
            "manifest": args.manifest,
            "n_geometries": len(label_order),
            "geometries": label_order,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

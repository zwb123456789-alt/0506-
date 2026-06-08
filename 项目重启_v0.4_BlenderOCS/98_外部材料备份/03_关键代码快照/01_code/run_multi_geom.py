# -*- coding: utf-8 -*-
"""
run_multi_geom.py —— 多观测几何批量扫描（Step 10d）
====================================================
对 OBS_GEOMETRIES 中定义的每组 sun/det 方向，独立执行完整的
姿态扫描 + 出图 + 落盘流程。每组几何产出一个子目录。
"""

import os
import sys
import csv
import json
import time as time_module
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    OUTPUT_DIR, SCAN_2D,
    YAW_RANGE, PITCH_RANGE, NUM_YAW, NUM_PITCH,
    UNIT_SCALE, RAY_BATCH, ACCURACY_LEVEL, BRDF_MODEL,
    OBS_GEOMETRIES, dump_config,
)

_USE_GGX_DEFAULT = (BRDF_MODEL == "ggx")
from materials      import MATERIAL_DB
from geometry       import load_meshes
from ocs_core       import scan_attitude
from occlusion      import embree_available
from visualization  import (
    setup_matplotlib_style,
    plot_all_2d, plot_three_curves_1d,
    plot_fig06_satellite_model,
)


def _serialize_scan_data(scan_data):
    rows = []
    for d in scan_data:
        row = {k: v for k, v in d.items() if k not in ("part_contrib",)}
        row["part_contrib"] = {
            pn: {
                "ocs_no_occ":            vc["ocs_no_occ"],
                "ocs_with_occ":          vc["ocs_with_occ"],
                "visible_faces_no_occ":  vc["visible_faces_no_occ"],
                "visible_faces_with_occ": vc["visible_faces_with_occ"],
            }
            for pn, vc in d["part_contrib"].items()
        }
        rows.append(row)
    return rows


def _save_csv(scan_data, csv_path):
    part_names = list(next(iter(scan_data))["part_contrib"].keys())
    headers = [
        "yaw", "pitch", "roll",
        "ocs_no_occ", "ocs_with_occ", "occlusion_ratio",
        "visible_faces_no_occ", "visible_faces_with_occ",
    ]
    headers += [f"ocs_no_occ_{pn}"   for pn in part_names]
    headers += [f"ocs_with_occ_{pn}" for pn in part_names]
    headers += [f"visible_faces_no_occ_{pn}"  for pn in part_names]
    headers += [f"visible_faces_with_occ_{pn}" for pn in part_names]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for d in scan_data:
            row = {k: d[k] for k in headers if k in d}
            for pn in part_names:
                pc = d["part_contrib"][pn]
                row[f"ocs_no_occ_{pn}"]            = pc["ocs_no_occ"]
                row[f"ocs_with_occ_{pn}"]          = pc["ocs_with_occ"]
                row[f"visible_faces_no_occ_{pn}"]  = pc["visible_faces_no_occ"]
                row[f"visible_faces_with_occ_{pn}"] = pc["visible_faces_with_occ"]
            w.writerow(row)
    print(f"  ✓ CSV 已保存: {csv_path}")


def _save_config_used(run_dir, sun_norm, det_norm, n_workers, embree_on, use_ggx=False):
    cfg = dump_config()
    cfg["sun_vector_normalized"] = sun_norm.tolist()
    cfg["det_vector_normalized"] = det_norm.tolist()
    cfg["n_workers"]             = n_workers
    cfg["embree_backend"]        = bool(embree_on)
    cfg["materials"] = {n: m["desc"] for n, m in MATERIAL_DB.items()}
    cfg["brdf_model"] = "ggx" if use_ggx else BRDF_MODEL
    p = os.path.join(run_dir, "config_used.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"  ✓ 配置快照已保存: {p}")


def _resolve_workers(n: int) -> int:
    if n > 0:
        return n
    cpu = os.cpu_count() or 1
    return max(1, cpu - 1)


def _compute_phase_angle(sun_norm, det_norm):
    """返回太阳-探测器相位角（度）。"""
    cos_phase = np.clip(np.dot(sun_norm, det_norm), -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_phase)))


def run_one_geometry(sun_vec, det_vec, geom_label, meshes, total_faces,
                     run_id, n_workers, use_ggx, num_yaw, num_pitch,
                     parent_out_dir):
    """对单组观测几何执行完整扫描流程。返回耗时和统计摘要。"""
    t0 = time_module.time()

    sun_norm = sun_vec / np.linalg.norm(sun_vec)
    det_norm = det_vec / np.linalg.norm(det_vec)
    phase = _compute_phase_angle(sun_norm, det_norm)

    geom_dir = os.path.join(parent_out_dir, geom_label)
    os.makedirs(geom_dir, exist_ok=True)

    print("\n" + "=" * 80)
    print(f"  观测几何: {geom_label}")
    print(f"  太阳方向: {sun_norm}")
    print(f"  探测器方向: {det_norm}")
    print(f"  相位角: {phase:.1f}°")
    print(f"  输出目录: {geom_dir}")
    print("=" * 80)

    # fig06: 卫星模型示意
    plot_fig06_satellite_model(meshes, sun_dir=sun_norm, output_dir=geom_dir)

    # 姿态扫描
    scan_data = scan_attitude(
        meshes, sun_norm, det_norm,
        scan_mode=None,
        yaw_range=YAW_RANGE,   num_yaw=num_yaw,
        pitch_range=PITCH_RANGE, num_pitch=num_pitch,
        n_workers=n_workers,
        use_ggx=use_ggx,
    )

    # 出图
    if SCAN_2D:
        plot_all_2d(scan_data, meshes, sun_dir=sun_norm, output_dir=geom_dir)
    else:
        plot_three_curves_1d(scan_data, output_dir=geom_dir)

    # JSON
    results = {
        "timestamp":     datetime.now().isoformat(),
        "run_id":        run_id,
        "geom_label":    geom_label,
        "scan_mode":     "2d" if SCAN_2D else "1d",
        "sun_direction": sun_norm.tolist(),
        "det_direction": det_norm.tolist(),
        "phase_angle_deg": phase,
        "yaw_range":     list(YAW_RANGE),
        "num_yaw":       num_yaw,
        "pitch_range":   list(PITCH_RANGE),
        "num_pitch":     num_pitch,
        "total_faces":   total_faces,
        "unit_scale":    UNIT_SCALE,
        "ray_batch":     RAY_BATCH,
        "accuracy_level": ACCURACY_LEVEL,
        "materials":      {n: m["desc"] for n, m in MATERIAL_DB.items()},
        "brdf_model":     "ggx" if use_ggx else BRDF_MODEL,
        "scan_data":     _serialize_scan_data(scan_data),
    }
    json_path = os.path.join(geom_dir, "ocs_scan.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  ✓ JSON 已保存: {json_path}")

    _save_csv(scan_data, os.path.join(geom_dir, "ocs_scan.csv"))
    _save_config_used(geom_dir, sun_norm, det_norm, n_workers, embree_available(), use_ggx=use_ggx)

    elapsed = time_module.time() - t0
    occ_arr   = np.array([d["ocs_with_occ"]   for d in scan_data])
    ratio_arr = np.array([d["occlusion_ratio"] for d in scan_data])

    summary = {
        "label":         geom_label,
        "phase_deg":     phase,
        "sun":           sun_norm.tolist(),
        "det":           det_norm.tolist(),
        "elapsed_sec":   round(elapsed, 1),
        "ocs_max":       float(occ_arr.max()),
        "ocs_min":       float(occ_arr.min()),
        "ocs_mean":      float(occ_arr.mean()),
        "occ_ratio_max": float(ratio_arr.max()),
        "occ_ratio_min": float(ratio_arr.min()),
        "occ_ratio_mean": float(ratio_arr.mean()),
    }

    print(f"  [{geom_label}] 耗时: {elapsed:.1f}s  "
          f"OCS max={occ_arr.max():.3e}  mean={occ_arr.mean():.3e}  "
          f"occ mean={ratio_arr.mean():.2%}")
    return summary


def main():
    import argparse
    p = argparse.ArgumentParser(description="模块 A · 多观测几何批量扫描")
    p.add_argument("--workers", type=int, default=0,
                   help="并行进程数：0=自动(cpu-1)，1=串行，>1=指定")
    p.add_argument("--ggx", action="store_true", default=_USE_GGX_DEFAULT,
                   help=f"使用 GGX/Cook-Torrance BRDF（默认按 config.BRDF_MODEL={BRDF_MODEL}）")
    p.add_argument("--legacy-phong", dest="ggx", action="store_false",
                   help="使用 LegacyPhong BRDF")
    p.add_argument("--num-yaw", type=int, default=None,
                   help="yaw 点数（默认 NUM_YAW=37）")
    p.add_argument("--num-pitch", type=int, default=None,
                   help="pitch 点数（默认 NUM_PITCH=19）")
    p.add_argument("--geoms", type=str, default="all",
                   help="几何索引，逗号分隔（0-4）或 'all'（默认 all）")
    args = p.parse_args()

    n_workers = _resolve_workers(args.workers)
    num_yaw   = args.num_yaw if args.num_yaw is not None else NUM_YAW
    num_pitch = args.num_pitch if args.num_pitch is not None else NUM_PITCH

    # 解析几何选择
    if args.geoms == "all":
        geom_indices = list(range(len(OBS_GEOMETRIES)))
    else:
        geom_indices = [int(x.strip()) for x in args.geoms.split(",")]

    selected = [OBS_GEOMETRIES[i] for i in geom_indices]

    t_global = time_module.time()
    setup_matplotlib_style()

    run_id   = datetime.now().strftime("%Y%m%d_%H%M%S")
    brdf_tag  = "ggx" if args.ggx else BRDF_MODEL
    mode_tag  = f"multi_geom_{brdf_tag}_yaw{num_yaw}"
    if SCAN_2D:
        mode_tag += f"_pitch{num_pitch}"
    parent_out_dir = os.path.join(OUTPUT_DIR, mode_tag, f"run_{run_id}")
    os.makedirs(parent_out_dir, exist_ok=True)

    print("=" * 80)
    print("  空间目标 OCS 多观测几何批量扫描 (Step 10d)")
    print(f"  遮挡检测: AABB 粗筛 + face-level 光追 (hybrid)")
    print(f"  扫描模式: {'2D (yaw × pitch)' if SCAN_2D else '1D (yaw-only)'}")
    print(f"  精度级别: {ACCURACY_LEVEL}")
    print(f"  BRDF 模型: {brdf_tag}")
    print(f"  观测几何: {len(selected)} 组 (索引 {geom_indices})")
    print(f"  并行进程: {n_workers}")
    print(f"  Embree 后端: {'ON' if embree_available() else 'OFF (纯 Python BVH)'}")
    print(f"  输出根目录: {parent_out_dir}")
    print("=" * 80)

    # ---- 加载 STL（只做一次） ----
    print("\n【步骤 1/3】加载 STL 模型...")
    meshes, total_faces = load_meshes()

    # ---- 逐几何扫描 ----
    print(f"\n【步骤 2/3】逐观测几何扫描 ({len(selected)} 组)...")
    print("-" * 70)

    summaries = []
    for idx, (sun_vec, det_vec, geom_label) in enumerate(selected):
        print(f"\n>>> 几何 [{idx+1}/{len(selected)}]: {geom_label}")
        summary = run_one_geometry(
            sun_vec, det_vec, geom_label, meshes, total_faces,
            run_id, n_workers, args.ggx, num_yaw, num_pitch,
            parent_out_dir,
        )
        summaries.append(summary)

    # ---- 全局汇总 ----
    print("\n" + "=" * 80)
    print("【步骤 3/3】多观测几何汇总")
    print("=" * 80)

    total_elapsed = time_module.time() - t_global
    print(f"\n{'几何':<30} {'相位角':>7} {'OCS max':>10} {'OCS mean':>10} {'occ mean':>9} {'耗时':>8}")
    print("-" * 80)
    for s in summaries:
        print(f"{s['label']:<30} {s['phase_deg']:>6.1f}° {s['ocs_max']:>10.3e} "
              f"{s['ocs_mean']:>10.3e} {s['occ_ratio_mean']:>8.2%} {s['elapsed_sec']:>7.1f}s")

    # 保存全局汇总
    manifest = {
        "run_id":           run_id,
        "timestamp":        datetime.now().isoformat(),
        "brdf_model":       brdf_tag,
        "num_yaw":          num_yaw,
        "num_pitch":        num_pitch,
        "n_workers":        n_workers,
        "total_elapsed_sec": round(total_elapsed, 1),
        "n_geometries":     len(summaries),
        "summaries":        summaries,
    }
    manifest_path = os.path.join(parent_out_dir, "multi_geom_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n  全局汇总已保存: {manifest_path}")
    print(f"  总耗时: {total_elapsed:.1f}s ({total_elapsed/60:.1f}min)")
    print(f"  输出根目录: {parent_out_dir}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

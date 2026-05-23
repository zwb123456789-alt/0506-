# -*- coding: utf-8 -*-
"""
main_run.py —— 模块 A 主入口
===============================
流程:
    1. 设置 matplotlib 双语字体
    2. 加载 STL（按 ACCURACY_LEVEL 抽稀）
    3. 输出卫星模型 3D 示意图（fig06）
    4. 姿态扫描（1D 或 2D）
    5. 出图：1D → 三曲线图；2D → fig01~fig05
    6. 保存 ocs_scan.json / ocs_scan.csv / config_used.json
    7. ENABLE_RENDER=False 时跳过 Python 端渲染

【相对原版的修复】
- 2D 模式不再误生成 1D 三曲线图
- 中英双语字体统一加载
- 遮挡率 / OCS 损失浮点 clip
- 每张图独立保存且 fig01~fig06 命名规范
- 落盘 config_used.json 便于复现
"""

import os
import sys
import csv
import json
import argparse
import time as time_module
from datetime import datetime

import numpy as np

# 让脚本可在 01_code/ 内直接 python main_run.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    OUTPUT_DIR, SUN_VECTOR, DET_VECTOR,
    SCAN_2D, NUM_YAW, NUM_PITCH,
    YAW_RANGE, PITCH_RANGE,
    UNIT_SCALE, RAY_BATCH, ACCURACY_LEVEL, BRDF_MODEL,
    ENABLE_RENDER, dump_config,
)
from materials      import MATERIAL_DB
from geometry       import load_meshes
from ocs_core       import scan_attitude
from occlusion      import embree_available
from visualization  import (
    setup_matplotlib_style,
    plot_all_2d, plot_three_curves_1d,
    plot_fig06_satellite_model,
)


# ============================================================
# 工具：JSON / CSV 序列化
# ============================================================
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


def _parse_args():
    p = argparse.ArgumentParser(description="模块 A · OCS 姿态扫描")
    p.add_argument(
        "--workers", type=int, default=0,
        help="并行进程数：0=自动(cpu-1)，1=串行（原行为），>1=指定"
    )
    p.add_argument(
        "--ggx", action="store_true", default=(BRDF_MODEL == "ggx"),
        help=f"使用 GGX/Cook-Torrance BRDF（默认按 config.BRDF_MODEL={BRDF_MODEL}）"
    )
    p.add_argument(
        "--legacy-phong", dest="ggx", action="store_false",
        help="使用 LegacyPhong BRDF"
    )
    p.add_argument(
        "--num-yaw", type=int, default=None,
        help="yaw 点数（默认 NUM_YAW=37，5° 网格用 73）"
    )
    p.add_argument(
        "--num-pitch", type=int, default=None,
        help="pitch 点数（默认 NUM_PITCH=19，5° 网格用 37）"
    )
    return p.parse_args()


def _resolve_workers(n: int) -> int:
    if n > 0:
        return n
    cpu = os.cpu_count() or 1
    return max(1, cpu - 1)


# ============================================================
# 主流程
# ============================================================
def main():
    args = _parse_args()
    n_workers = _resolve_workers(args.workers)
    num_yaw   = args.num_yaw if args.num_yaw is not None else NUM_YAW
    num_pitch = args.num_pitch if args.num_pitch is not None else NUM_PITCH

    t0 = time_module.time()
    setup_matplotlib_style()

    # 输出目录
    run_id   = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode_tag = f"{'2d' if SCAN_2D else '1d'}_yaw{num_yaw}"
    if SCAN_2D:
        mode_tag += f"_pitch{num_pitch}"
    run_dir = os.path.join(OUTPUT_DIR, mode_tag, f"run_{run_id}")
    os.makedirs(run_dir, exist_ok=True)

    print("=" * 80)
    print("  空间目标 OCS 姿态分析系统 (模块 A · 重构版)")
    print("  遮挡检测: AABB 粗筛 + face-level 光追 (hybrid)")
    print(f"  扫描模式: {'2D (yaw × pitch)' if SCAN_2D else '1D (yaw-only)'}")
    print(f"  精度级别: {ACCURACY_LEVEL}")
    brdf_label = "GGX (Cook-Torrance)" if args.ggx else f"LegacyPhong ({BRDF_MODEL})"
    print(f"  BRDF 模型: {brdf_label}")
    print(f"  光线批次: {RAY_BATCH}")
    print(f"  并行进程: {n_workers}")
    print(f"  Embree 后端: {'ON (embreex/pyembree)' if embree_available() else 'OFF (纯 Python BVH)'}")
    print(f"  输出目录: {run_dir}")
    print("=" * 80)

    # ---- 步骤 1: 加载 STL ----
    print("\n【步骤 1/4】加载 STL 模型 (本体坐标系)...")
    print("-" * 70)
    meshes, total_faces = load_meshes()

    # ---- 步骤 2: 卫星 3D 模型示意（fig06） ----
    print("\n【步骤 2/4】卫星模型示意图...")
    print("-" * 70)
    sun_norm = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
    det_norm = DET_VECTOR / np.linalg.norm(DET_VECTOR)
    plot_fig06_satellite_model(meshes, sun_dir=sun_norm, output_dir=run_dir)

    # ---- 步骤 3: 姿态扫描 ----
    mode_label = "2D (yaw × pitch)" if SCAN_2D else "1D (yaw-only)"
    print(f"\n【步骤 3/4】姿态扫描 ({mode_label})...")
    print("-" * 70)
    scan_data = scan_attitude(
        meshes, sun_norm, det_norm,
        scan_mode=None,
        yaw_range=YAW_RANGE,   num_yaw=num_yaw,
        pitch_range=PITCH_RANGE, num_pitch=num_pitch,
        n_workers=n_workers,
        use_ggx=args.ggx,
    )

    # ---- 步骤 4: 出图 + 落盘 ----
    print("\n【步骤 4/4】生成图表并保存结果...")
    print("-" * 70)

    if SCAN_2D:
        plot_all_2d(scan_data, meshes, sun_dir=sun_norm, output_dir=run_dir)
    else:
        plot_three_curves_1d(scan_data, output_dir=run_dir)

    # 保存 JSON
    results = {
        "timestamp":     datetime.now().isoformat(),
        "run_id":        run_id,
        "scan_mode":     "2d" if SCAN_2D else "1d",
        "sun_direction": sun_norm.tolist(),
        "det_direction": det_norm.tolist(),
        "yaw_range":     list(YAW_RANGE),
        "num_yaw":       num_yaw,
        "pitch_range":   list(PITCH_RANGE),
        "num_pitch":     num_pitch,
        "total_faces":   total_faces,
        "unit_scale":    UNIT_SCALE,
        "ray_batch":     RAY_BATCH,
        "accuracy_level": ACCURACY_LEVEL,
        "materials":      {n: m["desc"] for n, m in MATERIAL_DB.items()},
        "brdf_model":     "ggx" if args.ggx else BRDF_MODEL,
        "scan_data":     _serialize_scan_data(scan_data),
    }
    json_path = os.path.join(run_dir, "ocs_scan.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  ✓ JSON 已保存: {json_path}")

    # 保存 CSV + config_used.json
    _save_csv(scan_data, os.path.join(run_dir, "ocs_scan.csv"))
    _save_config_used(run_dir, sun_norm, det_norm, n_workers, embree_available(), use_ggx=args.ggx)

    # 渲染当前关闭（交给 Blender 阶段）
    if ENABLE_RENDER:
        print("\n[注意] ENABLE_RENDER=True，但模块 A 默认不在 Python 端渲染。")
        print("       请在 02_blender/ 下用 Blender headless 渲染。")

    # ---- 统计 ----
    elapsed = time_module.time() - t0
    occ_arr   = np.array([d["ocs_with_occ"]   for d in scan_data])
    ratio_arr = np.array([d["occlusion_ratio"] for d in scan_data])

    print("\n" + "=" * 80)
    print(f"  分析完成! 耗时: {elapsed:.1f} 秒 ({elapsed / 60:.2f} 分钟)")
    print("=" * 80)
    print(f"  OCS (含遮挡):  max={occ_arr.max():.4e}  "
          f"min={occ_arr.min():.4e}  mean={occ_arr.mean():.4e}")
    print(f"  遮挡率:        max={ratio_arr.max():.2%}  "
          f"min={ratio_arr.min():.2%}  mean={ratio_arr.mean():.2%}")
    print(f"  输出目录: {run_dir}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

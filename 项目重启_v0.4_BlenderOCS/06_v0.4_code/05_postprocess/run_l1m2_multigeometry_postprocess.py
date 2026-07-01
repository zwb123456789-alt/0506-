# -*- coding: utf-8 -*-
"""
run_l1m2_multigeometry_postprocess.py —— 1C-L1M2 多几何后处理（派生包装器）

派生自 run_full_postprocess.py（不修改原脚本）。导入原 driver 模块，
按 --geom 覆盖其几何相关全局，再调用原 main()。

覆盖的全局：
  SUN_VECTOR/DET_VECTOR/SUN_DIR/DET_DIR  ← 来自 config_v0_4.OBS_GEOMETRIES
  SHADOW_PASSES_DIR                       ← 11/shadow_passes/<geom_id>
  OUTPUT_DIR                              ← 11/postprocess/<geom_id>
  GEOM_ID                                 ← geom_id

关键不变量：
  - r_max / i_scale / pixel_area / depth_epsilon / log1p_alpha 全部沿用 phase63 fullrun，
    保证跨几何 OCS 量纲与图像归一一致、可比。
  - OCS 物理积分 = pixel_area * I_linear.sum()，与 i_scale 无关；i_scale 只影响 PNG。

用法：
  python run_l1m2_multigeometry_postprocess.py --geom phase24 --all
  python run_l1m2_multigeometry_postprocess.py --geom phase24 --attitudes yaw000_pitch+000_roll+000

红线：不改原 driver；不处理 phase63（L1-G1 复用 01_fullrun）。
"""

import os
import sys
import argparse
import importlib.util
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
V04_ROOT = THIS_DIR.parents[1]
CONFIG_DIR = V04_ROOT / "06_v0.4_code" / "00_config"
DRIVER_PATH = THIS_DIR / "run_full_postprocess.py"

LABEL_TO_GEOMID = {
    "phase63_backscatter": "phase63",
    "phase24_near_backscatter": "phase24",
    "phase120_forward_scatter": "phase120",
    "phase90_side": "phase90",
    "phase45_overhead": "phase45",
}
GEOMID_TO_LABEL = {v: k for k, v in LABEL_TO_GEOMID.items()}


def load_config_geometry(geom_id):
    spec = importlib.util.spec_from_file_location(
        "config_v0_4", str(CONFIG_DIR / "config_v0_4.py"))
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    target_label = GEOMID_TO_LABEL.get(geom_id, geom_id)
    for sun, det, label in cfg.OBS_GEOMETRIES:
        if label == target_label or label == geom_id:
            return np.array(sun, dtype=float), np.array(det, dtype=float), label
    raise ValueError(f"geom '{geom_id}' 不在 OBS_GEOMETRIES 中")


def load_driver():
    spec = importlib.util.spec_from_file_location(
        "run_full_postprocess", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom", required=True,
                    help="phase24|phase45|phase90|phase120")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--attitudes", default=None)
    ap.add_argument("--resume", default=None)
    args, _ = ap.parse_known_args()

    geom_id = args.geom
    if geom_id == "phase63":
        print("[BLOCKED] phase63 = L1-G1，复用 01_fullrun，不在本脚本重算。")
        return 3

    sun, det, label = load_config_geometry(geom_id)
    print(f"[L1M2-POST] geom_id={geom_id} label={label} sun={sun.tolist()} det={det.tolist()}")

    mod = load_driver()

    # 覆盖几何全局
    mod.SUN_VECTOR = sun
    mod.DET_VECTOR = det
    mod.SUN_DIR = sun / np.linalg.norm(sun)
    mod.DET_DIR = det / np.linalg.norm(det)
    mod.GEOM_ID = geom_id
    mod.SHADOW_PASSES_DIR = str(
        V04_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs" / "shadow_passes" / geom_id)
    out_dir = V04_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs" / "postprocess" / geom_id
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.OUTPUT_DIR = str(out_dir)

    # 改写 process_one_attitude 写 summary 时的相对路径基准沿用原模块（V04_PROJECT 不变）
    # 透传 sys.argv 给原 main()
    new_argv = [sys.argv[0]]
    if args.all:
        new_argv.append("--all")
    if args.attitudes:
        new_argv += ["--attitudes", args.attitudes]
    if args.resume:
        new_argv += ["--resume", args.resume]
    else:
        # 默认 resume 自身 summary，支持断点续跑
        self_summary = out_dir / "fullrun_postprocess_summary.json"
        if self_summary.exists():
            new_argv += ["--resume", str(self_summary)]
    sys.argv = new_argv

    print(f"  SHADOW_PASSES_DIR={mod.SHADOW_PASSES_DIR}")
    print(f"  OUTPUT_DIR={mod.OUTPUT_DIR}")
    print(f"  argv -> {new_argv[1:]}")
    return mod.main()


if __name__ == "__main__":
    sys.exit(main())

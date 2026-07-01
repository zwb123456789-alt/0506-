# -*- coding: utf-8 -*-
"""
run_mroll_probe_postprocess.py —— R116 子任务 C：M-roll 探针后处理（派生包装器）

派生自 run_full_postprocess.py（不改原脚本）。处理 M-roll 探针渲染的 EXR：
  - 支持 phase63（M-roll 探针主用，图像通道），也支持其它几何（joint OCS）
  - 覆盖 SHADOW_PASSES_DIR / OUTPUT_DIR / GEOM_ID / SUN/DET
  - --roll 指定 roll 角，--attitudes-file 给 attitude 子集（yaw/pitch label，不含 roll 后缀）

关键不变量：r_max / i_scale / pixel_area / depth_epsilon 沿用 phase63 fullrun，量纲可比。

用法：
  python run_mroll_probe_postprocess.py --geom phase63 --roll 15 --attitudes-file <subset.json>
"""

import sys
import json
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
    target = GEOMID_TO_LABEL.get(geom_id, geom_id)
    for sun, det, label in cfg.OBS_GEOMETRIES:
        if label == target or label == geom_id:
            return np.array(sun, float), np.array(det, float), label
    raise ValueError(f"geom '{geom_id}' 不在 OBS_GEOMETRIES 中")


def load_driver():
    spec = importlib.util.spec_from_file_location(
        "run_full_postprocess", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom", required=True)
    ap.add_argument("--roll", type=int, required=True)
    ap.add_argument("--attitudes-file", required=True)
    args, _ = ap.parse_known_args()

    geom_id = args.geom
    roll = args.roll
    roll_tag = f"roll{roll:+04d}"
    sun, det, label = load_config_geometry(geom_id)
    print(f"[MROLL-POST] geom={geom_id} roll={roll:+d}")

    mod = load_driver()
    mod.SUN_VECTOR = sun
    mod.DET_VECTOR = det
    mod.SUN_DIR = sun / np.linalg.norm(sun)
    mod.DET_DIR = det / np.linalg.norm(det)
    mod.GEOM_ID = geom_id
    mod.SHADOW_PASSES_DIR = str(V04_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" /
                                "mroll" / "shadow_passes" / geom_id / roll_tag)
    out_dir = (V04_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" / "mroll" /
               "postprocess" / geom_id / roll_tag)
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.OUTPUT_DIR = str(out_dir)

    # attitude 子集 -> 带 roll 后缀 label
    subset = json.load(open(args.attitudes_file, encoding="utf-8"))
    labels = [f"{a}_{roll_tag}" for a in subset]

    new_argv = [sys.argv[0], "--attitudes", ",".join(labels)]
    self_summary = out_dir / "fullrun_postprocess_summary.json"
    if self_summary.exists():
        new_argv += ["--resume", str(self_summary)]
    sys.argv = new_argv
    print(f"  SHADOW={mod.SHADOW_PASSES_DIR}")
    print(f"  OUTPUT={mod.OUTPUT_DIR}")
    print(f"  n_labels={len(labels)}")
    return mod.main()


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
render_l1m2_multigeometry.py —— 1C-L1M2 多几何 shadow pass 渲染（派生包装器）

派生自 render_full_2664_shadow.py（不修改原脚本）。
做法：导入原 driver 模块，按 --geom 覆盖其 SUN_VECTOR/DET_VECTOR/OUTPUT_DIR 三个全局，
再调用原 main()。所有渲染/跳过/分批/元数据逻辑完全复用原脚本，保证与
phase63 fullrun 同管线、同分辨率、同 pass、同 SAMPLES。

几何参数来源：config_v0_4.OBS_GEOMETRIES（与 l1m2_geometry_registry 一致）。
输出目录：v0.4_results/11_l1m2_multigeometry_ocs/shadow_passes/<geom_id>/

用法（Blender）：
  # 实测 3 姿态
  blender --background --python render_l1m2_multigeometry.py -- --geom phase24 --smoke 3
  # 分批
  blender --background --python render_l1m2_multigeometry.py -- --geom phase24 --start-index 0 --count 200

红线：不重渲已存在 phase63（L1-G1 复用 01_fullrun）；不改原 driver；不改姿态网格。
"""

import os
import sys
import importlib.util
from pathlib import Path

import numpy as np

try:
    import bpy  # noqa: F401
except ImportError:
    print("[ERROR] 必须用 blender --background --python 运行")
    sys.exit(1)

THIS_DIR = Path(__file__).resolve().parent
V04_ROOT = THIS_DIR.parents[1]            # 项目重启_v0.4_BlenderOCS
CONFIG_DIR = V04_ROOT / "06_v0.4_code" / "00_config"
DRIVER_PATH = THIS_DIR / "render_full_2664_shadow.py"

# label -> geom_id（与 registry 一致）
LABEL_TO_GEOMID = {
    "phase63_backscatter": "phase63",
    "phase24_near_backscatter": "phase24",
    "phase120_forward_scatter": "phase120",
    "phase90_side": "phase90",
    "phase45_overhead": "phase45",
}
GEOMID_TO_LABEL = {v: k for k, v in LABEL_TO_GEOMID.items()}


def parse_geom_arg():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    geom = None
    for i, a in enumerate(argv):
        if a == "--geom" and i + 1 < len(argv):
            geom = argv[i + 1].strip()
    return geom


def load_config_geometry(geom_id):
    """从 config_v0_4.OBS_GEOMETRIES 取出指定 geom 的 sun/det。"""
    spec = importlib.util.spec_from_file_location(
        "config_v0_4", str(CONFIG_DIR / "config_v0_4.py"))
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    target_label = GEOMID_TO_LABEL.get(geom_id, geom_id)
    for sun, det, label in cfg.OBS_GEOMETRIES:
        if label == target_label or label == geom_id:
            return list(map(float, sun)), list(map(float, det)), label
    raise ValueError(f"geom '{geom_id}' 不在 OBS_GEOMETRIES 中")


def load_driver():
    spec = importlib.util.spec_from_file_location(
        "render_full_2664_shadow", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    geom_id = parse_geom_arg()
    if geom_id is None:
        print("[ERROR] 必须传 --geom <phase24|phase45|phase90|phase120|phase63>")
        return 2

    if geom_id == "phase63":
        print("[BLOCKED] phase63 = L1-G1，直接复用 01_fullrun，不在本脚本重渲。")
        return 3

    sun, det, label = load_config_geometry(geom_id)
    print(f"[L1M2-RENDER] geom_id={geom_id} label={label}")
    print(f"  SUN_VECTOR={sun}  DET_VECTOR={det}")

    mod = load_driver()
    # 覆盖三个全局（main() 按名引用）
    mod.SUN_VECTOR = sun
    mod.DET_VECTOR = det
    out_dir = V04_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs" / "shadow_passes" / geom_id
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.OUTPUT_DIR = str(out_dir)
    print(f"  OUTPUT_DIR={out_dir}")

    return mod.main()


if __name__ == "__main__":
    sys.exit(main())

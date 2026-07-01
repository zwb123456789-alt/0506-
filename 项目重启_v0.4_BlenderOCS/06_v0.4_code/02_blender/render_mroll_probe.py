# -*- coding: utf-8 -*-
"""
render_mroll_probe.py —— R116 子任务 C：M-roll fixed-roll 边界探针渲染（派生包装器）

派生自 render_full_2664_shadow.py（不改原脚本）。在原 driver 上覆盖：
  - generate_full_attitude_list：注入非零 roll（label 用 roll{+/-NNN}）
  - SUN_VECTOR/DET_VECTOR：可选按 --geom 覆盖（默认 phase63，图像通道用）
  - OUTPUT_DIR：v0.4_results/12_l1m3_degraded_mroll/mroll/shadow_passes/<geom>/roll<±NNN>/

M-roll 只是 fixed-roll 边界探针：检验少量 roll 扰动是否推翻 clean/P-INT 结论。
不是三轴小项目。roll=0 复用现有数据（不在此重渲）。

用法（Blender）：
  # smoke：1 姿态 × roll+15，phase63
  blender --background --python render_mroll_probe.py -- --geom phase63 --roll 15 --smoke 1
  # 分批：phase63 roll+15 全量
  blender --background --python render_mroll_probe.py -- --geom phase63 --roll 15 --start-index 0 --count 200
  # 覆盖多几何（joint 的 OCS 需要 5 几何）：
  blender --background --python render_mroll_probe.py -- --geom phase24 --roll 15 ...

红线：roll=0 不重渲；不改原 driver；不改 yaw/pitch 网格步长。
"""

import sys
import importlib.util
from pathlib import Path

try:
    import bpy  # noqa: F401
except ImportError:
    print("[ERROR] 必须用 blender --background --python 运行")
    sys.exit(1)

THIS_DIR = Path(__file__).resolve().parent
V04_ROOT = THIS_DIR.parents[1]
CONFIG_DIR = V04_ROOT / "06_v0.4_code" / "00_config"
DRIVER_PATH = THIS_DIR / "render_full_2664_shadow.py"

LABEL_TO_GEOMID = {
    "phase63_backscatter": "phase63",
    "phase24_near_backscatter": "phase24",
    "phase120_forward_scatter": "phase120",
    "phase90_side": "phase90",
    "phase45_overhead": "phase45",
}
GEOMID_TO_LABEL = {v: k for k, v in LABEL_TO_GEOMID.items()}


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    geom, roll = "phase63", None
    for i, a in enumerate(argv):
        if a == "--geom" and i + 1 < len(argv):
            geom = argv[i + 1].strip()
        if a == "--roll" and i + 1 < len(argv):
            roll = int(argv[i + 1])
    return geom, roll


def load_config_geometry(geom_id):
    spec = importlib.util.spec_from_file_location(
        "config_v0_4", str(CONFIG_DIR / "config_v0_4.py"))
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    target = GEOMID_TO_LABEL.get(geom_id, geom_id)
    for sun, det, label in cfg.OBS_GEOMETRIES:
        if label == target or label == geom_id:
            return list(map(float, sun)), list(map(float, det)), label
    raise ValueError(f"geom '{geom_id}' 不在 OBS_GEOMETRIES 中")


def load_driver():
    spec = importlib.util.spec_from_file_location(
        "render_full_2664_shadow", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    geom_id, roll = parse_args()
    if roll is None:
        print("[ERROR] 必须传 --roll <int deg>（非 0）")
        return 2
    if roll == 0:
        print("[BLOCKED] roll=0 复用现有 fixed-roll 数据，不在 M-roll 探针重渲。")
        return 3

    sun, det, label = load_config_geometry(geom_id)
    print(f"[MROLL-RENDER] geom_id={geom_id} label={label} roll={roll:+d}")

    mod = load_driver()
    mod.SUN_VECTOR = sun
    mod.DET_VECTOR = det

    roll_tag = f"roll{roll:+04d}"
    out_dir = (V04_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" / "mroll" /
               "shadow_passes" / geom_id / roll_tag)
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.OUTPUT_DIR = str(out_dir)
    print(f"  OUTPUT_DIR={out_dir}")

    # 覆盖姿态生成：注入 roll
    def gen_roll_attitudes():
        atts = []
        for yaw in range(0, 360, 5):
            for pitch in range(-90, 91, 5):
                lb = f"yaw{yaw:03d}_pitch{pitch:+04d}_roll{roll:+04d}"
                atts.append({"yaw": yaw, "pitch": pitch, "roll": roll, "label": lb})
        return atts

    mod.generate_full_attitude_list = gen_roll_attitudes
    return mod.main()


if __name__ == "__main__":
    sys.exit(main())

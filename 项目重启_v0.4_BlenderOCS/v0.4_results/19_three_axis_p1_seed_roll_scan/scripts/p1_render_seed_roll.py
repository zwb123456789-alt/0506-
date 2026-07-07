# -*- coding: utf-8 -*-
"""
p1_render_seed_roll.py —— 三轴小项目 P1 seed-roll scan smoke 渲染（派生包装器）

R131 P1 smoke 专用。派生自 06_v0.4_code/02_blender/render_full_2664_shadow.py，
覆盖 driver 的姿态生成与输出目录，只渲染 12 个预注册 seed 点 × 指定非零 roll，
写入 19 号包 render 目录。不改任何旧脚本、不写旧目录、roll=0 不重渲。

对齐 baseline：几何 phase63（L1-G1），SUN=[1,0,0.3] DET=[0.5,-1,0.1]，
与 01_fullrun 一致，量纲可比。

用法（Blender）：
  # 单个 roll 批次（12 seed）
  blender --background --python p1_render_seed_roll.py -- --roll 15
  # smoke：只渲前 N 个 seed
  blender --background --python p1_render_seed_roll.py -- --roll 15 --smoke 1

红线：roll=0 不重渲（复用 01_fullrun）；不改原 driver；不改 yaw/pitch 网格步长；
只做 phase63 / L1-G1；只做 P1 smoke，不训练、不启动 P2/P3/P4。
"""

import sys
import csv
import importlib.util
from pathlib import Path

try:
    import bpy  # noqa: F401
except ImportError:
    print("[ERROR] 必须用 blender --background --python 运行")
    sys.exit(1)

THIS_DIR = Path(__file__).resolve().parent                      # 19_.../scripts
V04_ROOT = THIS_DIR.parents[2]                                  # 项目重启_v0.4_BlenderOCS
CODE_BLENDER = V04_ROOT / "06_v0.4_code" / "02_blender"
DRIVER_PATH = CODE_BLENDER / "render_full_2664_shadow.py"
MATRIX_CSV = (V04_ROOT / "v0.4_results" / "18_three_axis_planning_preflight" /
              "tables" / "p1_seed_roll_pre_registered_matrix.csv")
OUT_BASE = (V04_ROOT / "v0.4_results" / "19_three_axis_p1_seed_roll_scan" /
            "render" / "shadow_passes" / "phase63")

# phase63 / L1-G1 观测几何（与 01_fullrun baseline 一致）
PHASE63_SUN = [1.0, 0.0, 0.3]
PHASE63_DET = [0.5, -1.0, 0.1]


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    roll, smoke_n = None, None
    for i, a in enumerate(argv):
        if a == "--roll" and i + 1 < len(argv):
            roll = int(argv[i + 1])
        if a == "--smoke" and i + 1 < len(argv):
            smoke_n = int(argv[i + 1])
    return roll, smoke_n


def load_seed_points():
    """从预注册矩阵读取 12 个唯一 seed 点 (yaw, pitch)，保持出现顺序。"""
    seeds = []
    seen = set()
    with open(MATRIX_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rid = row["record_id"]
            if rid in seen:
                continue
            seen.add(rid)
            seeds.append({
                "record_id": rid,
                "yaw": int(round(float(row["yaw"]))),
                "pitch": int(round(float(row["pitch"]))),
                "category": row["category"],
            })
    return seeds


def load_driver():
    spec = importlib.util.spec_from_file_location(
        "render_full_2664_shadow", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    roll, smoke_n = parse_args()
    if roll is None:
        print("[ERROR] 必须传 --roll <int deg>（非 0）")
        return 2
    if roll == 0:
        print("[BLOCKED] roll=0 复用 01_fullrun，不在 P1 seed-roll scan 重渲。")
        return 3

    seeds = load_seed_points()
    if smoke_n is not None:
        seeds = seeds[:smoke_n]
    print(f"[P1-RENDER] geom=phase63/L1-G1 roll={roll:+d} n_seed={len(seeds)}")

    mod = load_driver()
    mod.SUN_VECTOR = PHASE63_SUN
    mod.DET_VECTOR = PHASE63_DET

    roll_tag = f"roll{roll:+04d}"
    out_dir = OUT_BASE / roll_tag
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.OUTPUT_DIR = str(out_dir)
    print(f"  OUTPUT_DIR={out_dir}")

    # 覆盖姿态生成：只生成 12 个 seed 点在指定 roll 的姿态
    def gen_seed_roll_attitudes():
        atts = []
        for s in seeds:
            yaw, pitch = s["yaw"], s["pitch"]
            lb = f"yaw{yaw:03d}_pitch{pitch:+04d}_roll{roll:+04d}"
            atts.append({"yaw": yaw, "pitch": pitch, "roll": roll, "label": lb})
        return atts

    mod.generate_full_attitude_list = gen_seed_roll_attitudes
    return mod.main()


if __name__ == "__main__":
    sys.exit(main())

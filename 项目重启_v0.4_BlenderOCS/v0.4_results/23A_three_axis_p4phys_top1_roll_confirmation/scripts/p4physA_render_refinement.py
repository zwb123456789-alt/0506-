# -*- coding: utf-8 -*-
"""
p4physA_render_refinement.py —— 23A 局部加密渲染脚本

派生自 P3 p3_render_local_refinement.py。
从 23A/tables/p4physA_refinement_render_manifest.csv 读取 render_needed=YES 的点，
按 --roll 批次渲染，写入 23A/render/shadow_passes/phase63/。

几何固定为 phase63/L1-G1: SUN=[1,0,0.3] DET=[0.5,-1,0.1]
支持浮点 roll（如 +12.5, +17.5）。

用法：
  blender --background --python p4physA_render_refinement.py -- --roll 5
  blender --background --python p4physA_render_refinement.py -- --roll 12.5
  blender --background --python p4physA_render_refinement.py -- --roll 15 --smoke 3

红线：不改 19/20/21/22 号包；不训练；只做 phase63/L1-G1。
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

THIS_DIR = Path(__file__).resolve().parent      # 23A/scripts
V04_ROOT = THIS_DIR.parents[2]                  # project root
CODE_BLENDER = V04_ROOT / "06_v0.4_code" / "02_blender"
DRIVER_PATH  = CODE_BLENDER / "render_full_2664_shadow.py"
MATRIX_CSV   = (V04_ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation" /
                "tables" / "p4physA_refinement_render_manifest.csv")
OUT_BASE     = (V04_ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation" /
                "render" / "shadow_passes" / "phase63")

PHASE63_SUN = [1.0, 0.0, 0.3]
PHASE63_DET = [0.5, -1.0, 0.1]


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    roll, smoke_n = None, None
    for i, a in enumerate(argv):
        if a == "--roll" and i + 1 < len(argv):
            try:
                roll = float(argv[i + 1])
            except ValueError:
                print(f"[ERROR] --roll 参数非法: {argv[i+1]}")
                sys.exit(1)
        if a == "--smoke" and i + 1 < len(argv):
            smoke_n = int(argv[i + 1])
    return roll, smoke_n


def load_render_units(roll_target):
    """从矩阵CSV读取指定 roll 下 render_needed=YES 的单位。"""
    units = []
    with open(MATRIX_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["render_needed"] != "YES":
                continue
            r = float(row["roll"])
            if abs(r - roll_target) > 0.01:
                continue
            units.append({
                "yaw":   float(row["yaw_deg"]),
                "pitch": float(row["pitch_deg"]),
                "roll":  r,
                "label": row["label"],
                "cluster": row["cluster"],
            })
    return units


def load_driver():
    spec = importlib.util.spec_from_file_location(
        "render_full_2664_shadow", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    roll, smoke_n = parse_args()
    if roll is None:
        print("[ERROR] 必须传 --roll <deg>，可为浮点 (如 12.5)")
        return 2

    units = load_render_units(roll)
    if smoke_n is not None:
        units = units[:smoke_n]
        print(f"[23A-RENDER SMOKE] n_smoke={smoke_n}")
    if not units:
        print(f"[INFO] roll={roll:+g} 无需渲染（全部复用 P3 或无该 roll 档）。")
        return 0

    print(f"[23A-RENDER] geom=phase63/L1-G1 roll={roll:+g} n_units={len(units)}")
    for u in units[:5]:
        print(f"  yaw={u['yaw']} pitch={u['pitch']} roll={u['roll']} label={u['label']}")
    if len(units) > 5:
        print(f"  ... +{len(units)-5} more")

    mod = load_driver()
    mod.SUN_VECTOR = PHASE63_SUN
    mod.DET_VECTOR = PHASE63_DET

    # roll tag: 整数用 +015，半整数用 +0125
    if roll == int(roll):
        roll_tag = f"roll{int(roll):+04d}"
    else:
        roll_tag = f"roll+{int(round(abs(roll)*10)):04d}" if roll > 0 else f"roll-{int(round(abs(roll)*10)):04d}"
    out_dir = OUT_BASE / roll_tag
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.OUTPUT_DIR = str(out_dir)
    print(f"  OUTPUT_DIR={out_dir}")

    captured_roll = roll

    def gen_23A_attitudes():
        return [{"yaw": u["yaw"], "pitch": u["pitch"],
                 "roll": captured_roll, "label": u["label"]}
                for u in units]

    mod.generate_full_attitude_list = gen_23A_attitudes
    return mod.main()


if __name__ == "__main__":
    sys.exit(main())

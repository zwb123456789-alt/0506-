# -*- coding: utf-8 -*-
"""
p3_render_local_refinement.py —— 三轴小项目 P3 local refinement 渲染（派生包装器）

R135 P3 专用。派生自 06_v0.4_code/02_blender/render_full_2664_shadow.py，
覆盖 driver 的姿态生成与输出目录，渲染 P3 预注册矩阵中 render_needed=YES 的
(yaw,pitch,roll) 单位，写入 21 号包 render 目录。

与 P2 的差异：P3 含 2.5 度半整数姿态（fullrun 无此网格），因此
  - 整数 5 度点：roll=0 复用 01_fullrun，只渲染非零 roll。
  - 半整数点：fullrun 无网格，roll=0 与非零 roll 全部新渲染。
driver 的 euler_to_matrix4 用 math.radians(float)，浮点角度可直接渲染。

对齐 baseline：几何 phase63（L1-G1），SUN=[1,0,0.3] DET=[0.5,-1,0.1]，
与 01_fullrun/P2 一致，量纲可比。

用法（Blender）：
  # 单个 roll 批次
  blender --background --python p3_render_local_refinement.py -- --roll 15
  # roll=0（只渲半度点）
  blender --background --python p3_render_local_refinement.py -- --roll 0
  # smoke：只渲该 roll 下前 N 个待渲 pose
  blender --background --python p3_render_local_refinement.py -- --roll 15 --smoke 2

红线：整数点 roll=0 不重渲（复用 fullrun）；不改原 driver；只做 phase63/L1-G1；
只做 P3 local refinement，不训练、不启动 P4/R128。
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

THIS_DIR = Path(__file__).resolve().parent                      # 21_.../scripts
V04_ROOT = THIS_DIR.parents[2]
CODE_BLENDER = V04_ROOT / "06_v0.4_code" / "02_blender"
DRIVER_PATH = CODE_BLENDER / "render_full_2664_shadow.py"
MATRIX_CSV = (V04_ROOT / "v0.4_results" / "21_three_axis_p3_local_refinement" /
              "tables" / "p3_local_refinement_pre_registered_matrix.csv")
OUT_BASE = (V04_ROOT / "v0.4_results" / "21_three_axis_p3_local_refinement" /
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


def load_render_units(roll):
    """从 P3 预注册矩阵读取指定 roll 下 render_needed=YES 的单位，保持出现顺序去重。"""
    units, seen = [], set()
    with open(MATRIX_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if int(row["roll"]) != roll:
                continue
            if row["render_needed"] != "YES":
                continue
            key = row["label"]
            if key in seen:
                continue
            seen.add(key)
            units.append({
                "yaw": float(row["yaw_deg"]),
                "pitch": float(row["pitch_deg"]),
                "roll": roll,
                "label": row["label"],
                "region": row["region"],
                "grid_type": row["grid_type"],
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
        print("[ERROR] 必须传 --roll <int deg>")
        return 2

    units = load_render_units(roll)
    if smoke_n is not None:
        units = units[:smoke_n]
    if not units:
        print(f"[INFO] roll={roll:+d} 无待渲单位（整数点 roll=0 复用 fullrun）。")
        return 0
    print(f"[P3-RENDER] geom=phase63/L1-G1 roll={roll:+d} n_units={len(units)} "
          f"(half2p5={sum(1 for u in units if u['grid_type']=='half2p5')}, "
          f"integer5={sum(1 for u in units if u['grid_type']=='integer5')})")

    mod = load_driver()
    mod.SUN_VECTOR = PHASE63_SUN
    mod.DET_VECTOR = PHASE63_DET

    roll_tag = f"roll{roll:+04d}"
    out_dir = OUT_BASE / roll_tag
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.OUTPUT_DIR = str(out_dir)
    print(f"  OUTPUT_DIR={out_dir}")

    def gen_p3_attitudes():
        atts = []
        for u in units:
            atts.append({"yaw": u["yaw"], "pitch": u["pitch"], "roll": float(roll),
                         "label": u["label"]})
        return atts

    mod.generate_full_attitude_list = gen_p3_attitudes
    return mod.main()


if __name__ == "__main__":
    sys.exit(main())

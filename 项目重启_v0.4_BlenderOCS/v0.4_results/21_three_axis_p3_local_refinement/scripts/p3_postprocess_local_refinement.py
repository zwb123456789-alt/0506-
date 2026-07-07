# -*- coding: utf-8 -*-
"""
p3_postprocess_local_refinement.py —— 三轴小项目 P3 local refinement 后处理（派生包装器）

R135 P3 专用。派生自 06_v0.4_code/05_postprocess/run_full_postprocess.py，
覆盖 driver 的 SHADOW_PASSES_DIR / OUTPUT_DIR / GEOM_ID，处理 21 号包 render 目录中
指定 roll 的 render_needed=YES 单位，产出 *_ocs.json / linear.exr / png，写入 21 号包
postprocess 目录。不改任何旧脚本、不写旧目录。

关键不变量：r_max / i_scale / pixel_area / depth_epsilon / SUN/DET 全部沿用 phase63
fullrun（driver 默认即 phase63），量纲与 01_fullrun / P2 baseline 可比。

process_one_attitude 用 label 定位并命名所有输出（label 由 deci-degree 唯一编码），
半度姿态不会与整数姿态碰撞；driver 内部 record_id 的 int() 截断仅为 ocs.json 元数据，
不影响输出文件名与指标读取。

用法（ocs_sim python）：
  python p3_postprocess_local_refinement.py --roll 15
  python p3_postprocess_local_refinement.py --roll 0     # 只处理半度点

红线：只做 phase63 / L1-G1；只做 P3 local refinement；不训练；
整数点 roll=0 不重处理（复用 01_fullrun）。
"""
import sys
import csv
import json
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime

THIS_DIR = Path(__file__).resolve().parent                      # 21_.../scripts
V04_ROOT = THIS_DIR.parents[2]
CODE_POST = V04_ROOT / "06_v0.4_code" / "05_postprocess"
DRIVER_PATH = CODE_POST / "run_full_postprocess.py"
MATRIX_CSV = (V04_ROOT / "v0.4_results" / "21_three_axis_p3_local_refinement" /
              "tables" / "p3_local_refinement_pre_registered_matrix.csv")
RENDER_BASE = (V04_ROOT / "v0.4_results" / "21_three_axis_p3_local_refinement" /
               "render" / "shadow_passes" / "phase63")
POST_BASE = (V04_ROOT / "v0.4_results" / "21_three_axis_p3_local_refinement" /
             "postprocess" / "phase63")


def load_units(roll):
    """指定 roll 下 render_needed=YES 的单位（去重，保持顺序）。"""
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
            units.append({"yaw": float(row["yaw_deg"]), "pitch": float(row["pitch_deg"]),
                          "label": row["label"], "region": row["region"],
                          "category": row["category"], "grid_type": row["grid_type"]})
    return units


def load_driver():
    if str(CODE_POST) not in sys.path:
        sys.path.insert(0, str(CODE_POST))
    spec = importlib.util.spec_from_file_location(
        "run_full_postprocess", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roll", type=int, required=True)
    ap.add_argument("--smoke", type=int, default=None)
    args, _ = ap.parse_known_args()

    roll = args.roll
    roll_tag = f"roll{roll:+04d}"
    units = load_units(roll)
    if args.smoke is not None:
        units = units[:args.smoke]
    if not units:
        print(f"[INFO] roll={roll:+d} 无待处理单位（整数点 roll=0 复用 01_fullrun）。")
        return 0

    mod = load_driver()
    shadow_dir = RENDER_BASE / roll_tag
    out_dir = POST_BASE / roll_tag
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.SHADOW_PASSES_DIR = str(shadow_dir)
    mod.OUTPUT_DIR = str(out_dir)
    mod.GEOM_ID = "phase63"

    with open(mod.SHADOW_SUMMARY, "r", encoding="utf-8") as f:
        r_max = json.load(f)["r_max"]
    with open(mod.STEP5_SUMMARY, "r", encoding="utf-8") as f:
        i_scale = json.load(f)["i_scale_step5"]
    ortho_scale_m = 2.2 * r_max
    pixel_area_m2 = (ortho_scale_m / 256) ** 2

    print(f"[P3-POST] geom=phase63 roll={roll:+d} n_units={len(units)}")
    print(f"  SHADOW={shadow_dir}")
    print(f"  OUTPUT={out_dir}")
    print(f"  r_max={r_max:.6f} i_scale={i_scale:.6e} pixel_area={pixel_area_m2:.6e}")

    records, blockers = [], []
    for u in units:
        label = u["label"]
        try:
            record, err = mod.process_one_attitude(
                label, float(u["yaw"]), float(u["pitch"]), r_max, i_scale, pixel_area_m2)
            if record:
                record["region"] = u["region"]
                record["category"] = u["category"]
                record["roll_deg"] = roll
                record["grid_type"] = u["grid_type"]
                records.append(record)
            else:
                blockers.append(err)
                records.append({"label": label, "region": u["region"],
                                "category": u["category"], "roll_deg": roll,
                                "grid_type": u["grid_type"], "status": "MISSING", "error": err})
                print(f"  [MISSING] {err}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            blockers.append(f"{label}: {e}")
            records.append({"label": label, "region": u["region"],
                            "category": u["category"], "roll_deg": roll,
                            "grid_type": u["grid_type"], "status": "FAILED", "error": str(e)})

    n_complete = sum(1 for r in records if r.get("status") == "COMPLETE")
    overall = "COMPLETE" if n_complete == len(units) and not blockers else "NOT_COMPLETE"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "task": "R135 P3 local refinement postprocess",
        "geom_id": "phase63",
        "roll_deg": roll,
        "overall_status": overall,
        "r_max": r_max,
        "ortho_scale_m": ortho_scale_m,
        "pixel_area_m2": pixel_area_m2,
        "i_scale": i_scale,
        "depth_epsilon_m_final": mod.DEPTH_EPSILON_M_FINAL,
        "n_total_units": len(units),
        "n_completed": n_complete,
        "records": records,
        "blockers": blockers,
    }
    summary_path = out_dir / "p3_postprocess_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 72)
    print(f"OVERALL(roll{roll:+d}): {overall}  {n_complete}/{len(units)}")
    if blockers:
        for b in blockers[:20]:
            print("  blocker:", b)
    print(f"Summary: {summary_path}")
    return 0 if overall == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())

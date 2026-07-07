# -*- coding: utf-8 -*-
"""
p1_postprocess_seed_roll.py —— 三轴小项目 P1 seed-roll scan smoke 后处理（派生包装器）

R131 P1 smoke 专用。派生自 06_v0.4_code/05_postprocess/run_full_postprocess.py，
覆盖 driver 的 SHADOW_PASSES_DIR / OUTPUT_DIR / GEOM_ID，处理 19 号包 render 目录里
指定 roll 的 12 个 seed 点 EXR，产出 *_ocs.json / linear.exr / png，写入 19 号包
postprocess 目录。不改任何旧脚本、不写旧目录。

关键不变量：r_max / i_scale / pixel_area / depth_epsilon / SUN/DET 全部沿用 phase63
fullrun（driver 默认即 phase63），量纲与 01_fullrun baseline 可比。

用法（ocs_sim python）：
  python p1_postprocess_seed_roll.py --roll 15

红线：只做 phase63 / L1-G1；只做 P1 smoke；不训练；roll=0 不重处理（复用 01_fullrun）。
"""

import sys
import csv
import json
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime

THIS_DIR = Path(__file__).resolve().parent                      # 19_.../scripts
V04_ROOT = THIS_DIR.parents[2]
CODE_POST = V04_ROOT / "06_v0.4_code" / "05_postprocess"
DRIVER_PATH = CODE_POST / "run_full_postprocess.py"
MATRIX_CSV = (V04_ROOT / "v0.4_results" / "18_three_axis_planning_preflight" /
              "tables" / "p1_seed_roll_pre_registered_matrix.csv")
RENDER_BASE = (V04_ROOT / "v0.4_results" / "19_three_axis_p1_seed_roll_scan" /
               "render" / "shadow_passes" / "phase63")
POST_BASE = (V04_ROOT / "v0.4_results" / "19_three_axis_p1_seed_roll_scan" /
             "postprocess" / "phase63")


def load_seed_points():
    seeds, seen = [], set()
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
    # driver 依赖 sys.path 注入自身目录，先确保可导入其兄弟模块
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
    if roll == 0:
        print("[BLOCKED] roll=0 复用 01_fullrun，不在 P1 重处理。")
        return 3

    roll_tag = f"roll{roll:+04d}"
    seeds = load_seed_points()
    if args.smoke is not None:
        seeds = seeds[:args.smoke]

    mod = load_driver()
    # 覆盖输入/输出目录到 19 号包；GEOM_ID 保持 phase63（driver 默认）
    shadow_dir = RENDER_BASE / roll_tag
    out_dir = POST_BASE / roll_tag
    out_dir.mkdir(parents=True, exist_ok=True)
    mod.SHADOW_PASSES_DIR = str(shadow_dir)
    mod.OUTPUT_DIR = str(out_dir)
    mod.GEOM_ID = "phase63"

    # 复用 driver 的参数装载（r_max / i_scale / pixel_area）
    with open(mod.SHADOW_SUMMARY, "r", encoding="utf-8") as f:
        r_max = json.load(f)["r_max"]
    with open(mod.STEP5_SUMMARY, "r", encoding="utf-8") as f:
        i_scale = json.load(f)["i_scale_step5"]
    ortho_scale_m = 2.2 * r_max
    pixel_area_m2 = (ortho_scale_m / 256) ** 2

    print(f"[P1-POST] geom=phase63 roll={roll:+d} n_seed={len(seeds)}")
    print(f"  SHADOW={shadow_dir}")
    print(f"  OUTPUT={out_dir}")
    print(f"  r_max={r_max:.6f} i_scale={i_scale:.6e} pixel_area={pixel_area_m2:.6e}")

    records, blockers = [], []
    for s in seeds:
        yaw, pitch = s["yaw"], s["pitch"]
        label = f"yaw{yaw:03d}_pitch{pitch:+04d}_{roll_tag}"
        print(f"\n--- {label} ({s['category']}) ---")
        try:
            record, err = mod.process_one_attitude(
                label, float(yaw), float(pitch), r_max, i_scale, pixel_area_m2)
            if record:
                record["category"] = s["category"]
                record["roll_deg"] = roll
                records.append(record)
                print(f"  [COMPLETE] OCS_total={record['ocs_total']:.6e} "
                      f"visible={record['n_pixels_camera_visible']} "
                      f"contrib={record['n_pixels_contributing']}")
            else:
                blockers.append(err)
                records.append({"label": label, "category": s["category"],
                                "roll_deg": roll, "status": "MISSING", "error": err})
                print(f"  [MISSING] {err}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            blockers.append(f"{label}: {e}")
            records.append({"label": label, "category": s["category"],
                            "roll_deg": roll, "status": "FAILED", "error": str(e)})

    n_complete = sum(1 for r in records if r.get("status") == "COMPLETE")
    overall = "COMPLETE" if n_complete == len(seeds) and not blockers else "NOT_COMPLETE"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "task": "R131 P1 seed-roll scan smoke postprocess",
        "geom_id": "phase63",
        "roll_deg": roll,
        "overall_status": overall,
        "r_max": r_max,
        "ortho_scale_m": ortho_scale_m,
        "pixel_area_m2": pixel_area_m2,
        "i_scale": i_scale,
        "depth_epsilon_m_final": mod.DEPTH_EPSILON_M_FINAL,
        "n_total_seeds": len(seeds),
        "n_completed": n_complete,
        "records": records,
        "blockers": blockers,
    }
    summary_path = out_dir / "p1_postprocess_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 72)
    print(f"OVERALL(roll{roll:+d}): {overall}  {n_complete}/{len(seeds)}")
    if blockers:
        for b in blockers:
            print("  blocker:", b)
    print(f"Summary: {summary_path}")
    return 0 if overall == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())

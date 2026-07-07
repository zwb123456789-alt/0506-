# -*- coding: utf-8 -*-
"""
p2_postprocess_sparse_grid.py —— 三轴小项目 P2 sparse 3-axis grid 后处理（派生包装器）

R133 P2 专用。派生自 06_v0.4_code/05_postprocess/run_full_postprocess.py，
覆盖 driver 的 SHADOW_PASSES_DIR / OUTPUT_DIR / GEOM_ID，处理 20 号包 render 目录里
指定 roll 的 125 个 pose EXR，产出 *_ocs.json / linear.exr / png，写入 20 号包
postprocess 目录。不改任何旧脚本、不写旧目录。

关键不变量：r_max / i_scale / pixel_area / depth_epsilon / SUN/DET 全部沿用 phase63
fullrun（driver 默认即 phase63），量纲与 01_fullrun baseline 可比（与 P1 wrapper 相同）。

用法（ocs_sim python）：
  python p2_postprocess_sparse_grid.py --roll 15

红线：只做 phase63 / L1-G1；只做 P2 sparse grid；不训练；roll=0 不重处理（复用 01_fullrun）。
"""
import sys
import csv
import json
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime

THIS_DIR = Path(__file__).resolve().parent                      # 20_.../scripts
V04_ROOT = THIS_DIR.parents[2]
CODE_POST = V04_ROOT / "06_v0.4_code" / "05_postprocess"
DRIVER_PATH = CODE_POST / "run_full_postprocess.py"
MATRIX_CSV = (V04_ROOT / "v0.4_results" / "20_three_axis_p2_sparse_grid" /
              "tables" / "p2_sparse_grid_pre_registered_matrix.csv")
RENDER_BASE = (V04_ROOT / "v0.4_results" / "20_three_axis_p2_sparse_grid" /
               "render" / "shadow_passes" / "phase63")
POST_BASE = (V04_ROOT / "v0.4_results" / "20_three_axis_p2_sparse_grid" /
             "postprocess" / "phase63")


def load_unique_poses():
    poses, seen = [], set()
    with open(MATRIX_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (int(row["yaw"]), int(row["pitch"]))
            if key in seen:
                continue
            seen.add(key)
            poses.append({"yaw": key[0], "pitch": key[1],
                          "region": row["region"], "category": row["category"]})
    return poses


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
        print("[BLOCKED] roll=0 复用 01_fullrun，不在 P2 重处理。")
        return 3

    roll_tag = f"roll{roll:+04d}"
    poses = load_unique_poses()
    if args.smoke is not None:
        poses = poses[:args.smoke]

    mod = load_driver()
    # 覆盖输入/输出目录到 20 号包；GEOM_ID 保持 phase63（driver 默认）
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

    print(f"[P2-POST] geom=phase63 roll={roll:+d} n_pose={len(poses)}")
    print(f"  SHADOW={shadow_dir}")
    print(f"  OUTPUT={out_dir}")
    print(f"  r_max={r_max:.6f} i_scale={i_scale:.6e} pixel_area={pixel_area_m2:.6e}")

    records, blockers = [], []
    for pp in poses:
        yaw, pitch = pp["yaw"], pp["pitch"]
        label = f"yaw{yaw:03d}_pitch{pitch:+04d}_{roll_tag}"
        try:
            record, err = mod.process_one_attitude(
                label, float(yaw), float(pitch), r_max, i_scale, pixel_area_m2)
            if record:
                record["region"] = pp["region"]
                record["category"] = pp["category"]
                record["roll_deg"] = roll
                records.append(record)
            else:
                blockers.append(err)
                records.append({"label": label, "region": pp["region"],
                                "category": pp["category"], "roll_deg": roll,
                                "status": "MISSING", "error": err})
                print(f"  [MISSING] {err}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            blockers.append(f"{label}: {e}")
            records.append({"label": label, "region": pp["region"],
                            "category": pp["category"], "roll_deg": roll,
                            "status": "FAILED", "error": str(e)})

    n_complete = sum(1 for r in records if r.get("status") == "COMPLETE")
    overall = "COMPLETE" if n_complete == len(poses) and not blockers else "NOT_COMPLETE"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "task": "R133 P2 sparse 3-axis grid postprocess",
        "geom_id": "phase63",
        "roll_deg": roll,
        "overall_status": overall,
        "r_max": r_max,
        "ortho_scale_m": ortho_scale_m,
        "pixel_area_m2": pixel_area_m2,
        "i_scale": i_scale,
        "depth_epsilon_m_final": mod.DEPTH_EPSILON_M_FINAL,
        "n_total_poses": len(poses),
        "n_completed": n_complete,
        "records": records,
        "blockers": blockers,
    }
    summary_path = out_dir / "p2_postprocess_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 72)
    print(f"OVERALL(roll{roll:+d}): {overall}  {n_complete}/{len(poses)}")
    if blockers:
        for b in blockers[:20]:
            print("  blocker:", b)
    print(f"Summary: {summary_path}")
    return 0 if overall == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
p4physA_postprocess_refinement.py —— 23A 局部加密后处理（派生 driver 方式）

派生自 p3_postprocess_local_refinement.py。
加载 run_full_postprocess.py driver，覆盖目录，处理 23A 新渲染点。
支持浮点 roll（+12.5, +17.5 等）。

用法：
  python p4physA_postprocess_refinement.py --roll 5
  python p4physA_postprocess_refinement.py --roll 12.5
  python p4physA_postprocess_refinement.py --roll all  # 处理所有roll
"""
import sys, csv, json, argparse, importlib.util
from pathlib import Path
from datetime import datetime

THIS_DIR  = Path(__file__).resolve().parent   # 23A/scripts
V04_ROOT  = THIS_DIR.parents[2]               # project root
CODE_POST = V04_ROOT / "06_v0.4_code" / "05_postprocess"
DRIVER_PATH = CODE_POST / "run_full_postprocess.py"

PKG23      = V04_ROOT / "v0.4_results" / "23B_three_axis_p4phys_pitch_boundary_followup"
MATRIX_CSV = PKG23 / "tables" / "p4physA2_render_manifest.csv"
RENDER_BASE = PKG23 / "render" / "shadow_passes" / "phase63"
POST_BASE   = PKG23 / "postprocess" / "phase63"


def roll_tag(r):
    if r == int(r):
        return f"roll{int(r):+04d}"
    return f"roll+{int(round(abs(r)*10)):04d}" if r > 0 else f"roll-{int(round(abs(r)*10)):04d}"


def load_units(roll_target):
    units, seen = [], set()
    with open(MATRIX_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["render_needed"] != "YES":
                continue
            r = float(row["roll"])
            if abs(r - roll_target) > 0.01:
                continue
            key = row["label"]
            if key in seen:
                continue
            seen.add(key)
            units.append({
                "yaw":   float(row["yaw_deg"]),
                "pitch": float(row["pitch_deg"]),
                "roll":  r,
                "label": row["label"],
                "cluster": row["cluster"],
            })
    return units


def load_driver():
    if str(CODE_POST) not in sys.path:
        sys.path.insert(0, str(CODE_POST))
    spec = importlib.util.spec_from_file_location("run_full_postprocess", str(DRIVER_PATH))
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def process_roll(roll_val, smoke_n=None):
    units = load_units(roll_val)
    if smoke_n is not None:
        units = units[:smoke_n]
    if not units:
        print(f"[INFO] roll={roll_val:+g} 无待处理新渲染单位。")
        return []

    mod = load_driver()
    rt      = roll_tag(roll_val)
    shd_dir = RENDER_BASE / rt
    out_dir = POST_BASE / rt
    out_dir.mkdir(parents=True, exist_ok=True)

    mod.SHADOW_PASSES_DIR = str(shd_dir)
    mod.OUTPUT_DIR        = str(out_dir)
    mod.GEOM_ID           = "phase63"

    # 参数
    with open(mod.SHADOW_SUMMARY, encoding="utf-8") as f:
        shadow_data = json.load(f)
    r_max = shadow_data.get("r_max") or 1.4726051706213208

    with open(mod.STEP5_SUMMARY, encoding="utf-8") as f:
        step5_data = json.load(f)
    i_scale = step5_data.get("i_scale_step5", 0.5444863931551639)

    ortho_scale_m = 2.2 * r_max
    pixel_area_m2 = (ortho_scale_m / 256) ** 2

    print(f"[23B-POST] roll={roll_val:+g}  n={len(units)}")
    print(f"  SHADOW={shd_dir}")
    print(f"  OUTPUT={out_dir}")
    print(f"  r_max={r_max:.4f}  i_scale={i_scale:.4e}  pixel_area={pixel_area_m2:.4e}")

    records, blockers = [], []
    for u in units:
        label = u["label"]
        try:
            record, err = mod.process_one_attitude(
                label, u["yaw"], u["pitch"], r_max, i_scale, pixel_area_m2)
            if record:
                record["roll_deg"] = roll_val
                record["cluster"]  = u["cluster"]
                records.append(record)
            else:
                blockers.append(err)
                records.append({"label": label, "roll_deg": roll_val,
                                 "status": "MISSING", "error": err})
                print(f"  [MISSING] {err}")
        except Exception as e:
            import traceback; traceback.print_exc()
            blockers.append(f"{label}: {e}")
            records.append({"label": label, "roll_deg": roll_val,
                             "status": "FAILED", "error": str(e)})

    n_ok = sum(1 for r in records if r.get("status") == "COMPLETE")
    print(f"  COMPLETE={n_ok}/{len(units)}, blockers={len(blockers)}")
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roll", default="all",
                    help="roll值（如 5, 12.5）或 'all' 处理所有新渲染批次")
    ap.add_argument("--smoke", type=int, default=None)
    args, _ = ap.parse_known_args()

    ROLL_LIST = [15.0]  # 23B pitch边界追加只用 roll=+15

    if args.roll == "all":
        rolls_to_process = ROLL_LIST
    else:
        rolls_to_process = [float(args.roll)]

    all_records = []
    for rv in rolls_to_process:
        recs = process_roll(rv, smoke_n=args.smoke)
        all_records.extend(recs)

    # 汇总
    total = len(all_records)
    ok    = sum(1 for r in all_records if r.get("status") == "COMPLETE")
    fail  = total - ok
    print(f"\n[23B-POST 全部完成] COMPLETE={ok}/{total}  FAILED={fail}")

    # 写汇总日志
    summ_path = PKG23 / "logs" / "p4physA2_postprocess.log"
    summ_path.parent.mkdir(exist_ok=True)
    with open(summ_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": total, "complete": ok, "failed": fail,
            "records": all_records,
        }, f, ensure_ascii=False, indent=2)
    print(f"  汇总日志: {summ_path}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

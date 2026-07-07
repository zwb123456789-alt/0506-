# -*- coding: utf-8 -*-
"""
p4physF_postprocess.py —— 28 包后处理（ocs_sim python 运行）
================================================================================
R157 子任务。三种阶段：
    --stage smoke  ：只处理 R3L_smoke @ Hsp_vm（sp7_vm7），验证 EXR 通道、OCS 积分、
                     并与逐像素机制重算做一致性核验。
    --stage stageB ：处理 27 个网格姿态 @ Hsp_vm（中心 C_R3 有 27 包锚点核验），
                     输出 stage1 排名表 + 最优摘要，并写 audit/stagec_poses.json。
    --stage stageC ：处理 Stage C 姿态集 × 9 组合几何（54 组合），
                     (sun+7,view-7)&旧姿态 与 27 包 Hsp_vm 数值锚点核验，
                     输出 stage2 microgrid 排名表。

官方口径复用：compute_brdf_response / compute_ocs_from_brdf_response（与 26/27 完全一致）。
"""
import sys
import csv
import json
import argparse
import importlib.util
from pathlib import Path
from datetime import datetime

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
V04_ROOT = THIS_DIR.parents[2]
CODE_POST = V04_ROOT / "06_v0.4_code" / "05_postprocess"
CODE_VALID = V04_ROOT / "06_v0.4_code" / "10_validation"
for p in (str(CODE_POST), str(CODE_VALID)):
    if p not in sys.path:
        sys.path.insert(0, p)

from image_response_v0_4 import compute_brdf_response
from ocs_integration_v0_4 import compute_ocs_from_brdf_response
from validate_v_sun_macro_on_image import read_indexob_pass

spec_cfg = importlib.util.spec_from_file_location("p4physF_config", str(THIS_DIR / "p4physF_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)


def process_unit(pose, so, vo):
    gid = cfg.geom_id(so, vo)
    cam, cam_src = cfg.camera_exr(pose["label"], pose.get("is_new", False), vo)
    sun, sun_src = cfg.sun_exr(pose["label"], pose.get("is_new", False), so)
    rec = {
        "geom_id": gid, "sun_offset": so, "view_offset": vo,
        "pose_id": pose["pose_id"], "label": pose["label"],
        "yaw": pose["yaw"], "pitch": pose["pitch"], "roll": pose["roll"],
        "is_new_pose": pose.get("is_new", False),
        "on_grid_edge": pose.get("on_grid_edge", ""),
        "camera_exr_src": cam_src, "sun_exr_src": sun_src,
    }
    if not cam.is_file():
        rec.update(status="FAILED", failed_reason=f"camera EXR missing: {cam}"); return rec
    if not sun.is_file():
        rec.update(status="FAILED", failed_reason=f"sun EXR missing: {sun}"); return rec

    sun_dir = np.asarray(cfg.SUN_DIR[so], float)
    det_dir = np.asarray(cfg.DET_DIR[vo], float)

    brdf = compute_brdf_response(
        camera_exr_path=str(cam), sun_exr_path=str(sun),
        sun_dir=sun_dir, det_dir=det_dir,
        r_max=cfg.R_MAX, depth_epsilon_m=cfg.DEPTH_EPSILON_M_FINAL,
        brdf_branch="B0", indexob_to_part=cfg.INDEXOB_TO_PART,
    )
    indexob_map = read_indexob_pass(str(cam))
    ocs = compute_ocs_from_brdf_response(
        brdf_result=brdf, pixel_area_m2=cfg.PIXEL_AREA_M2,
        indexob_map=indexob_map, indexob_to_part=cfg.INDEXOB_TO_PART,
    )

    out_dir = cfg.POST_BASE / gid
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(str(out_dir / f"{pose['label']}_v_sun_macro.npy"), brdf["V_sun_macro"].astype(np.float32))
    ocs_json = {
        "record_id": f"{gid}_{pose['label']}",
        "geom_id": gid, "pose_id": pose["pose_id"], "label": pose["label"],
        "sun_offset": so, "view_offset": vo,
        "yaw_deg": pose["yaw"], "pitch_deg": pose["pitch"], "roll_deg": pose["roll"],
        "sun_dir": list(map(float, sun_dir)), "det_dir": list(map(float, det_dir)),
        "ocs_total": ocs["ocs_total"], "ocs_per_part": ocs["ocs_per_part"],
        "n_pixels_camera_visible": ocs["n_pixels_camera_visible"],
        "n_pixels_nol_positive": ocs["n_pixels_nol_positive"],
        "n_pixels_sun_visible": ocs["n_pixels_sun_visible"],
        "n_pixels_contributing": ocs["n_pixels_contributing"],
        "n_pixels_per_part": ocs["n_pixels_per_part"],
    }
    with open(out_dir / f"{pose['label']}_ocs.json", "w", encoding="utf-8") as f:
        json.dump(ocs_json, f, ensure_ascii=False, indent=2)

    rec.update(
        status="COMPLETE",
        ocs_total=ocs["ocs_total"],
        ocs_metal=ocs["ocs_per_part"]["jinshuzhuti"],
        ocs_dark=ocs["ocs_per_part"]["yinshenban"],
        ocs_solar=ocs["ocs_per_part"]["taiyangnengban"],
        n_pixels_contributing=ocs["n_pixels_contributing"],
        image_usable=bool(ocs["n_pixels_contributing"] > 0),
        failed_reason="",
    )
    # 27 包 Hsp_vm 锚点核验
    ref_path = cfg.anchor_27_ocs_json(pose["label"], so, vo)
    if ref_path is not None:
        with open(ref_path, encoding="utf-8") as f:
            ref = json.load(f)
        ref_tot = float(ref["ocs_total"])
        rec["anchor_ref"] = "27/Hsp_vm"
        rec["anchor_ref_ocs_total"] = ref_tot
        rec["anchor_rel_diff"] = abs(ocs["ocs_total"] - ref_tot) / max(ref_tot, 1e-12)
    return rec


def write_csv(path, cols, records):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f); wr.writerow(cols)
        for r in records:
            wr.writerow([r.get(c, "") for c in cols])


COLS = ["geom_id", "sun_offset", "view_offset", "pose_id", "label", "yaw", "pitch", "roll",
        "is_new_pose", "on_grid_edge", "camera_exr_src", "sun_exr_src",
        "ocs_total", "ocs_metal", "ocs_dark", "ocs_solar",
        "n_pixels_contributing", "image_usable",
        "anchor_ref", "anchor_ref_ocs_total", "anchor_rel_diff",
        "status", "failed_reason"]


def run_smoke():
    rec = process_unit(cfg.SMOKE_POSE, 7, -7)
    write_csv(cfg.PKG28 / "tables" / "p4physF_smoke_metrics.csv", COLS, [rec])
    print(f"[SMOKE] {rec['status']} OCS={rec.get('ocs_total', '')} "
          f"contrib={rec.get('n_pixels_contributing', '')}")
    return [rec]


def run_stageB():
    records = [process_unit(p, 7, -7) for p in cfg.STAGEB_POSES]
    for r in records:
        extra = (f"OCS={r['ocs_total']:.6f}" if r["status"] == "COMPLETE" else r["failed_reason"])
        if "anchor_rel_diff" in r:
            extra += f" [anchor rel_diff={r['anchor_rel_diff']:.2e}]"
        print(f"  [{r['status']}] {r['pose_id']:16s} {extra}")

    ok = [r for r in records if r["status"] == "COMPLETE"]
    ok.sort(key=lambda r: -r["ocs_total"])
    for rank, r in enumerate(ok, 1):
        r["rank"] = rank
    write_csv(cfg.PKG28 / "tables" / "p4physF_stage1_pose_local_rank.csv",
              ["rank"] + COLS, ok)

    best = ok[0]
    c_r3 = next(r for r in ok if r["pose_id"] == "C_R3")
    summary = {
        "stage1_best_pose_id": best["pose_id"], "stage1_best_label": best["label"],
        "yaw": best["yaw"], "pitch": best["pitch"], "roll": best["roll"],
        "ocs_total": best["ocs_total"],
        "on_grid_edge": bool(best["on_grid_edge"]),
        "exceeds_C_R3": best["ocs_total"] > c_r3["ocs_total"],
        "C_R3_ocs_total": c_r3["ocs_total"],
        "rel_gain_vs_C_R3": (best["ocs_total"] - c_r3["ocs_total"]) / c_r3["ocs_total"],
        "A_top1_baseline_ocs": 0.2088904828,
        "exceeds_A_top1_baseline": best["ocs_total"] > 0.2088904828,
    }
    with open(cfg.PKG28 / "tables" / "p4physF_stage1_best_summary.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(list(summary.keys())); wr.writerow(list(summary.values()))

    # Stage C 姿态集：S0=C_R3, S1=Stage1_best, S2=A_top1, S3=D5, S4=D6, S5=B_R4（去重）
    stagec = []
    seen = set()

    def add_pose(pid, label, yaw, pitch, roll, is_new):
        if label in seen:
            return
        seen.add(label)
        stagec.append({"pose_id": pid, "label": label, "yaw": yaw, "pitch": pitch,
                       "roll": roll, "is_new": is_new})

    add_pose("C_R3", c_r3["label"], c_r3["yaw"], c_r3["pitch"], c_r3["roll"], False)
    add_pose(f"S1_best[{best['pose_id']}]", best["label"], best["yaw"], best["pitch"],
             best["roll"], bool(best["is_new_pose"]))
    for pid in ["A_top1", "D5_roll125", "D6_roll175", "B_R4"]:
        p = cfg.OLD_POSES[pid]
        add_pose(pid, p["label"], p["yaw"], p["pitch"], p["roll"], False)

    cfg.STAGEC_POSES_JSON.parent.mkdir(exist_ok=True)
    with open(cfg.STAGEC_POSES_JSON, "w", encoding="utf-8") as f:
        json.dump({"timestamp": datetime.now().isoformat(),
                   "n_poses": len(stagec),
                   "new_render_units_estimate": 4 * len(stagec),
                   "poses": stagec}, f, ensure_ascii=False, indent=2)

    print(f"\n[STAGE-B DONE] best={best['pose_id']} OCS={best['ocs_total']:.8f} "
          f"edge={best['on_grid_edge']} exceeds_C_R3={summary['exceeds_C_R3']} "
          f"exceeds_A_top1={summary['exceeds_A_top1_baseline']}")
    print(f"  StageC poses={len(stagec)} -> est. new units={4 * len(stagec)} (cap {cfg.STAGEC_RENDER_CAP})")
    return records


def run_stageC():
    with open(cfg.STAGEC_POSES_JSON, encoding="utf-8") as f:
        stagec = json.load(f)["poses"]
    records = []
    for pose in stagec:
        for g in cfg.GEOMETRIES_C:
            records.append(process_unit(pose, g["sun_offset"], g["view_offset"]))
    n_ok = sum(1 for r in records if r["status"] == "COMPLETE")
    ok = [r for r in records if r["status"] == "COMPLETE"]
    ok.sort(key=lambda r: -r["ocs_total"])
    for rank, r in enumerate(ok, 1):
        r["rank"] = rank
    write_csv(cfg.PKG28 / "tables" / "p4physF_stage2_sunview_microgrid_rank.csv",
              ["rank"] + COLS, ok)

    best = ok[0]
    edge_geom = (best["sun_offset"] in (5, 9)) or (best["view_offset"] in (-5, -9))
    top_rows = [
        ["stage2_best_geom", best["geom_id"]],
        ["stage2_best_sun_offset", best["sun_offset"]],
        ["stage2_best_view_offset", best["view_offset"]],
        ["stage2_best_pose_id", best["pose_id"]],
        ["stage2_best_label", best["label"]],
        ["stage2_best_ocs_total", f"{best['ocs_total']:.10f}"],
        ["stage2_best_on_geom_edge", edge_geom],
        ["hsp_vm_center_is_geom_best", best["geom_id"] == "sp7_vm7"],
    ]
    with open(cfg.PKG28 / "tables" / "p4physF_stage2_top_candidate_summary.csv", "w",
              newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["key", "value"]); wr.writerows(top_rows)

    print(f"\n[STAGE-C DONE] COMPLETE={n_ok}/{len(records)}")
    print(f"  best: {best['geom_id']} / {best['pose_id']} OCS={best['ocs_total']:.8f} "
          f"geom_edge={edge_geom}")
    anchors = [r for r in records if "anchor_rel_diff" in r]
    if anchors:
        print(f"  anchors: {sum(1 for r in anchors if r['anchor_rel_diff'] < 1e-4)}/{len(anchors)} OK "
              f"max={max(r['anchor_rel_diff'] for r in anchors):.2e}")
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["smoke", "stageB", "stageC"])
    args = ap.parse_args()

    print("=" * 78)
    print(f"[28-POST] stage={args.stage}")
    print("=" * 78)
    if args.stage == "smoke":
        records = run_smoke()
    elif args.stage == "stageB":
        records = run_stageB()
    else:
        records = run_stageC()

    log_path = cfg.PKG28 / "logs" / f"p4physF_{args.stage}_postprocess.log"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "stage": args.stage,
                   "n_total": len(records),
                   "n_complete": sum(1 for r in records if r["status"] == "COMPLETE"),
                   "records": records}, f, ensure_ascii=False, indent=2)
    n_fail = sum(1 for r in records if r["status"] != "COMPLETE")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
p4physE_postprocess.py —— 27 包 sun/view 3×3 组合网格后处理（ocs_sim python 运行）
================================================================================
R155 子任务 B。对每个 (geometry, pose) 组合（9×14=126）：
    - 解析该几何应使用的 camera EXR（由 view_offset 决定）与 sun EXR（由 sun_offset 决定），
      全部来自 26 包已渲染 EXR 或 baseline 源（0 新增渲染）
    - 用该几何的 sun_dir/det_dir 调 06_v0.4_code 官方 compute_brdf_response
    - 积分 OCS_total / ocs_per_part，写入 27/postprocess/<geom_id>/<label>_ocs.json
    - 对 5 个可锚点组合（H00/pure sun/pure view）与 26 包对应 G0-G4 ocs.json 做数值一致性核验

复用官方口径（无自定义 BRDF）：
    compute_brdf_response / compute_ocs_from_brdf_response（image_response_v0_4 / ocs_integration_v0_4）

用法：
    python p4physE_postprocess.py
"""
import sys
import csv
import json
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

spec_cfg = importlib.util.spec_from_file_location("p4physE_config", str(THIS_DIR / "p4physE_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)


def process_unit(geom, pose):
    cam, cam_src, sun, sun_src = cfg.resolve_exr_pair(geom, pose)
    rec = {
        "geom_id": geom["geom_id"], "pose_id": pose["pose_id"], "label": pose["label"],
        "role": pose["role"], "group": pose["group"],
        "sun_offset": geom["sun_offset"], "view_offset": geom["view_offset"],
        "yaw": pose["yaw"], "pitch": pose["pitch"], "roll": pose["roll"],
        "sun_dir": list(map(float, geom["sun_dir"])),
        "det_dir": list(map(float, geom["det_dir"])),
        "camera_exr_src": cam_src, "sun_exr_src": sun_src,
    }
    if not cam.is_file():
        rec.update(status="FAILED", failed_reason=f"camera EXR missing: {cam}"); return rec
    if not sun.is_file():
        rec.update(status="FAILED", failed_reason=f"sun EXR missing: {sun}"); return rec

    sun_dir = np.asarray(geom["sun_dir"], float)
    det_dir = np.asarray(geom["det_dir"], float)

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

    out_dir = cfg.POST_BASE / geom["geom_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(str(out_dir / f"{pose['label']}_v_sun_macro.npy"), brdf["V_sun_macro"].astype(np.float32))
    ocs_json = {
        "record_id": f"{geom['geom_id']}_{pose['label']}",
        "geom_id": geom["geom_id"], "pose_id": pose["pose_id"], "label": pose["label"],
        "sun_offset": geom["sun_offset"], "view_offset": geom["view_offset"],
        "yaw_deg": pose["yaw"], "pitch_deg": pose["pitch"], "roll_deg": pose["roll"],
        "sun_dir": rec["sun_dir"], "det_dir": rec["det_dir"],
        "ocs_total": ocs["ocs_total"], "ocs_per_part": ocs["ocs_per_part"],
        "n_pixels_camera_visible": ocs["n_pixels_camera_visible"],
        "n_pixels_nol_positive": ocs["n_pixels_nol_positive"],
        "n_pixels_sun_visible": ocs["n_pixels_sun_visible"],
        "n_pixels_contributing": ocs["n_pixels_contributing"],
        "n_pixels_per_part": ocs["n_pixels_per_part"],
    }
    with open(out_dir / f"{pose['label']}_ocs.json", "w", encoding="utf-8") as f:
        json.dump(ocs_json, f, ensure_ascii=False, indent=2)

    image_usable = ocs["n_pixels_contributing"] > 0
    rec.update(
        status="COMPLETE",
        ocs_total=ocs["ocs_total"],
        ocs_metal=ocs["ocs_per_part"]["jinshuzhuti"],
        ocs_dark=ocs["ocs_per_part"]["yinshenban"],
        ocs_solar=ocs["ocs_per_part"]["taiyangnengban"],
        n_pixels_camera_visible=ocs["n_pixels_camera_visible"],
        n_pixels_contributing=ocs["n_pixels_contributing"],
        image_usable=bool(image_usable),
        failed_reason="",
    )

    # 5 个可锚点组合：与 26 包对应 G0-G4 ocs.json 数值一致性核验
    ref_path = cfg.anchor_ocs_json(geom, pose)
    if ref_path is not None and ref_path.is_file():
        with open(ref_path, encoding="utf-8") as f:
            ref = json.load(f)
        ref_tot = float(ref["ocs_total"])
        rec["anchor_26_geom"] = geom["anchor_26"]
        rec["anchor_ref_ocs_total"] = ref_tot
        rec["anchor_rel_diff"] = abs(ocs["ocs_total"] - ref_tot) / max(ref_tot, 1e-12)
    return rec


def main():
    geoms = cfg.GEOMETRIES
    poses = cfg.POSES

    print("=" * 78)
    print(f"[27-POST] n_geom={len(geoms)}  n_pose={len(poses)}  combos={len(geoms)*len(poses)}")
    print(f"  r_max={cfg.R_MAX:.6f}  pixel_area={cfg.PIXEL_AREA_M2:.6e}  eps={cfg.DEPTH_EPSILON_M_FINAL:.4f}")
    print("=" * 78)

    records = []
    for g in geoms:
        for pose in poses:
            rec = process_unit(g, pose)
            records.append(rec)
            tag = rec["status"]
            if tag == "COMPLETE":
                extra = f"OCS={rec['ocs_total']:.6f} contrib={rec['n_pixels_contributing']}"
                if "anchor_rel_diff" in rec:
                    extra += f" [anchor {rec['anchor_26_geom']} rel_diff={rec['anchor_rel_diff']:.2e}]"
            else:
                extra = rec.get("failed_reason", "")
            print(f"  [{tag}] {g['geom_id']:14s} {pose['pose_id']:12s} {extra}")

    # metrics CSV
    metrics_path = cfg.PKG27 / "tables" / "p4physE_metrics.csv"
    metrics_path.parent.mkdir(exist_ok=True)
    cols = ["geom_id", "pose_id", "label", "role", "group", "sun_offset", "view_offset",
            "yaw", "pitch", "roll", "sun_dir", "det_dir", "camera_exr_src", "sun_exr_src",
            "ocs_total", "ocs_metal", "ocs_dark", "ocs_solar",
            "n_pixels_camera_visible", "n_pixels_contributing", "image_usable",
            "status", "failed_reason"]
    with open(metrics_path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f); wr.writerow(cols)
        for r in records:
            wr.writerow([r.get(c, "") for c in cols])

    # postprocess_status.csv
    status_path = cfg.PKG27 / "audit" / "postprocess_status.csv"
    with open(status_path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["geom_id", "pose_id", "label", "camera_exr_src", "sun_exr_src",
                     "ocs_total", "image_usable", "status", "failed_reason"])
        for r in records:
            wr.writerow([r["geom_id"], r["pose_id"], r["label"], r["camera_exr_src"],
                         r["sun_exr_src"], r.get("ocs_total", ""), r.get("image_usable", ""),
                         r["status"], r.get("failed_reason", "")])

    # log
    log_path = cfg.PKG27 / "logs" / "p4physE_postprocess.log"
    n_ok = sum(1 for r in records if r["status"] == "COMPLETE")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({"timestamp": datetime.now().isoformat(),
                   "n_total": len(records), "n_complete": n_ok,
                   "records": records}, f, ensure_ascii=False, indent=2)

    print(f"\n[27-POST DONE] COMPLETE={n_ok}/{len(records)}")
    # anchor consistency summary
    anchors = [r for r in records if "anchor_rel_diff" in r]
    if anchors:
        max_rel = max(r["anchor_rel_diff"] for r in anchors)
        n_anchor_ok = sum(1 for r in anchors if r["anchor_rel_diff"] < 1e-4)
        print(f"  anchor consistency: {n_anchor_ok}/{len(anchors)} OK  max_rel_diff={max_rel:.3e}")
    print(f"  metrics={metrics_path}")
    return 0 if n_ok == len(records) else 1


if __name__ == "__main__":
    sys.exit(main())

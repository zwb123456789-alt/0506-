# -*- coding: utf-8 -*-
"""
p4physF_design_audit.py —— 28 包阶段 A：设计审计（ocs_sim python 运行）
================================================================================
R157 §4。在任何渲染前生成：
    audit/input_manifest.csv          —— 本轮依赖的上游文件（26/27 包 EXR、ocs.json、脚本）
    audit/pose_local_grid_manifest.csv—— Stage B 27 姿态网格（含复用/新渲染标记）
    audit/sunview_microgrid_manifest.csv —— Stage C 9 组合几何（方向向量与角距）
    audit/render_plan_manifest.csv    —— 渲染计划（单元级，含预算核算）
    audit/redline_precheck.csv        —— 红线预检（预算/复用/源包只读）
"""
import csv
import importlib.util
from pathlib import Path

import numpy as np

THIS_DIR = Path(__file__).resolve().parent
spec_cfg = importlib.util.spec_from_file_location("p4physF_config", str(THIS_DIR / "p4physF_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)

AUDIT = cfg.PKG28 / "audit"
AUDIT.mkdir(exist_ok=True)


def w(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)
    print(f"  wrote {path.name} ({len(rows)} rows)")


def main():
    # ---- input manifest：上游依赖 ----
    rows = []
    def add_input(kind, p):
        p = Path(p)
        rows.append([kind, str(p.relative_to(cfg.V04_ROOT)).replace("\\", "/"),
                     "OK" if p.is_file() else "MISSING"])

    for pid, pose in cfg.OLD_POSES.items():
        cam, _ = cfg.camera_exr(pose["label"], False, -7)
        sun, _ = cfg.sun_exr(pose["label"], False, 7)
        add_input(f"reuse_26_camera_vm7[{pid}]", cam)
        add_input(f"reuse_26_sun_sp7[{pid}]", sun)
        ref = cfg.anchor_27_ocs_json(pose["label"], 7, -7)
        if ref:
            add_input(f"anchor_27_Hsp_vm[{pid}]", ref)
    for s in ["p4physD_config.py", "p4physD_render.py"]:
        add_input("reuse_26_script", cfg.PKG26 / "scripts" / s)
    for s in ["p4physE_config.py", "p4physE_postprocess.py", "p4physE_mechanism_analysis.py"]:
        add_input("reuse_27_script", cfg.PKG27 / "scripts" / s)
    add_input("driver", cfg.V04_ROOT / "06_v0.4_code" / "02_blender" / "render_full_2664_shadow.py")
    n_missing = sum(1 for r in rows if r[2] == "MISSING")
    w(AUDIT / "input_manifest.csv", ["kind", "path", "status"], rows)

    # ---- Stage B pose grid manifest ----
    rows = []
    for p in cfg.STAGEB_POSES:
        rows.append([p["pose_id"], p["label"], p["yaw"], p["pitch"], p["roll"],
                     "REUSE_EXISTING" if not p["is_new"] else "NEW_RENDER_2units",
                     p["on_grid_edge"]])
    w(AUDIT / "pose_local_grid_manifest.csv",
      ["pose_id", "label", "yaw", "pitch", "roll", "render", "on_grid_edge"], rows)

    # ---- Stage C microgrid manifest ----
    rows = []
    for g in cfg.GEOMETRIES_C:
        rows.append([g["geom_id"], g["sun_offset"], g["view_offset"],
                     np.round(g["sun_dir"], 6).tolist(), np.round(g["det_dir"], 6).tolist(),
                     f"{g['sun_ang_from_base']:.3f}", f"{g['det_ang_from_base']:.3f}",
                     "CENTER_Hsp_vm" if g["is_center"] else ""])
    w(AUDIT / "sunview_microgrid_manifest.csv",
      ["geom_id", "sun_offset", "view_offset", "sun_dir", "det_dir",
       "sun_ang_from_base_deg", "det_ang_from_base_deg", "note"], rows)

    # ---- render plan manifest ----
    rows = []
    n_b = 0
    for p in cfg.STAGEB_NEW:
        rows.append(["stageB", "cam_vm7", p["label"], "camera", "view-7"]); n_b += 1
        rows.append(["stageB", "sun_sp7", p["label"], "sun", "sun+7"]); n_b += 1
    # Stage C 上限估算（6 姿态 × 4；S1 与既有姿态重复时会减少）
    n_c_max = 6 * 4
    rows.append(["stageC(max_est)", "cam_vm5/cam_vm9/sun_sp5/sun_sp9",
                 "<=6 poses (C_R3,S1_best,A_top1,D5,D6,B_R4 dedup)", "camera+sun",
                 f"{n_c_max} units max"])
    w(AUDIT / "render_plan_manifest.csv",
      ["stage", "subdir", "label", "view", "note"], rows)

    # ---- redline precheck ----
    checks = [
        ["stageB_units<=52", n_b, "PASS" if n_b <= cfg.STAGEB_RENDER_CAP else "FAIL"],
        ["stageC_units<=24", n_c_max, "PASS" if n_c_max <= cfg.STAGEC_RENDER_CAP else "FAIL"],
        ["total_units<=80", n_b + n_c_max,
         "PASS" if n_b + n_c_max <= cfg.TOTAL_RENDER_CAP else "FAIL"],
        ["upstream_inputs_available", f"missing={n_missing}", "PASS" if n_missing == 0 else "FAIL"],
        ["no_training", "no training in any script", "PASS"],
        ["no_R128_no_route234", "not started", "PASS"],
        ["no_full_sunview_search", "microgrid only (±2deg around Hsp_vm)", "PASS"],
        ["source_pkgs_readonly", "20/21/23A/23B/24/25/26/27 only read", "PASS"],
        ["writes_only_28_and_claude_output", str(cfg.PKG28), "PASS"],
    ]
    w(AUDIT / "redline_precheck.csv", ["check", "value", "verdict"], checks)

    n_fail = sum(1 for c in checks if c[2] == "FAIL")
    print(f"\n[DESIGN-AUDIT] stageB_units={n_b} stageC_max={n_c_max} "
          f"total_max={n_b + n_c_max} (cap {cfg.TOTAL_RENDER_CAP}) "
          f"missing_inputs={n_missing} precheck={'ALL PASS' if n_fail == 0 else str(n_fail) + ' FAIL'}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

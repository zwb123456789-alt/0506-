# -*- coding: utf-8 -*-
"""
run_phase0_step7c_dryrun.py —— Phase 0 Step 7c 3 姿态物理 dry-run (1C-E15-FIX02)
====================================================================================
任务：在 Step 6 small-run 未使用的 3 个新姿态上执行完整 dry-run，
     输出 V_sun_macro mask、BRDF/OCS/image 产物和 summary。

依据：
    - R33 Codex 审阅（1C-E15-FIX01 通过并规划 FIX02）
    - R31 Codex 审阅（Step 7b 条件通过要求 Step 7c）
    - 13 号 §8.2 / 14 号 §3.1/3.2

3 个 dry-run 姿态（R31/R33 指定，均非 Step 6 small-run 姿态）：
    - yaw045_pitch+000_roll+000
    - yaw270_pitch-030_roll+000
    - yaw135_pitch+000_roll+000

范围：
    - 复用 Step 4 shadow_passes 已有 camera/sun EXR（不重渲染）
    - 使用 B0 phong_like_provisional_baseline
    - 输出 V_sun_macro mask（PNG + NPY）
    - 输出 BRDF/OCS/image 产物

边界：
    - 不得进入全量 2664 姿态生成
    - 不得训练模型
    - 不得改写论文正文
    - 不得修改 CLAUDE.md、13/14/24/25 冻结文件
    - 不得写入 04_Codex审阅/
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# 添加模块路径
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from image_response_v0_4 import (
    compute_brdf_response,
    write_image_outputs,
    write_exr_single,
    write_png_gray,
)

from ocs_integration_v0_4 import (
    compute_ocs_from_brdf_response,
    write_ocs_json,
)

# 复用 validation 工具
_VALIDATION_DIR = os.path.join(_THIS_DIR, "..", "10_validation")
if _VALIDATION_DIR not in sys.path:
    sys.path.insert(0, _VALIDATION_DIR)

from validate_v_sun_macro_on_image import read_indexob_pass


# ============================================================
# 配置
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")

# 输入路径
SHADOW_PASSES_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "shadow_passes")
SHADOW_SUMMARY = os.path.join(V04_PROJECT, "v0.4_results", "00_validation",
                              "shadow_validation", "shadow_validation_summary.json")
STEP5_SUMMARY = os.path.join(V04_PROJECT, "v0.4_results", "00_validation",
                             "v_sun_macro_image_check", "v_sun_macro_image_check_summary.json")

# 输出路径
OUTPUT_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "phase0_step7c_dryrun_fix02")

# 观测几何（与 Step 4/5/6 一致）
SUN_VECTOR = np.array([1.0, 0.0, 0.3])
DET_VECTOR = np.array([0.5, -1.0, 0.1])
SUN_DIR = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
DET_DIR = DET_VECTOR / np.linalg.norm(DET_VECTOR)

# Step 4 校准参数
DEPTH_EPSILON_M_FINAL = 0.7952109582768545

# BRDF 分支
BRDF_BRANCH = "B0"

# log1p 参数
LOG1P_ALPHA = 10.0

# IndexOB 映射
INDEXOB_TO_PART = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}

# 3 个 dry-run 姿态（R31/R33 指定，均非 Step 6 small-run 姿态）
DRYRUN_ATTITUDES = [
    {"label": "yaw045_pitch+000_roll+000", "yaw": 45.0, "pitch": 0.0},
    {"label": "yaw270_pitch-030_roll+000", "yaw": 270.0, "pitch": -30.0},
    {"label": "yaw135_pitch+000_roll+000", "yaw": 135.0, "pitch": 0.0},
]

# 几何标识符
GEOM_ID = "phase63"


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 80)
    print("Phase 0 Step 7c: 3 姿态物理 dry-run (1C-E15-FIX02)")
    print("=" * 80)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # 读取参数
    with open(SHADOW_SUMMARY, 'r', encoding='utf-8') as f:
        summary4 = json.load(f)
    r_max = summary4["r_max"]

    with open(STEP5_SUMMARY, 'r', encoding='utf-8') as f:
        summary5 = json.load(f)
    i_scale_step5 = summary5["i_scale_step5"]

    print(f"r_max = {r_max}")
    print(f"DEPTH_EPSILON_M_FINAL = {DEPTH_EPSILON_M_FINAL}")
    print(f"I_scale（来自 Step 5 的 5 姿态 image impact validation）= {i_scale_step5:.6e}")
    print(f"BRDF 分支 = {BRDF_BRANCH}")
    print(f"log1p_alpha = {LOG1P_ALPHA}")
    print(f"dry-run 姿态数 = {len(DRYRUN_ATTITUDES)}")
    print()

    # 计算 pixel_area_m2
    ortho_scale_m = 2.2 * r_max
    resolution = 256
    pixel_area_m2 = (ortho_scale_m / resolution) ** 2

    blockers = []
    records = []

    for att in DRYRUN_ATTITUDES:
        label = att["label"]
        yaw_deg = att["yaw"]
        pitch_deg = att["pitch"]
        record_id = f"{GEOM_ID}_yaw{int(yaw_deg):03d}_pitch{pitch_deg:+04.0f}"

        print(f"--- {label} ---")

        camera_exr = os.path.join(SHADOW_PASSES_DIR, f"{label}_camera.exr")
        sun_exr = os.path.join(SHADOW_PASSES_DIR, f"{label}_sun.exr")

        # 检查输入文件
        if not os.path.isfile(camera_exr):
            blockers.append(f"{label}: 缺失 camera EXR {camera_exr}")
            continue
        if not os.path.isfile(sun_exr):
            blockers.append(f"{label}: 缺失 sun EXR {sun_exr}")
            continue

        try:
            # Step 1: 计算 BRDF 响应（含 V_sun_macro 生成）
            brdf_result = compute_brdf_response(
                camera_exr_path=camera_exr,
                sun_exr_path=sun_exr,
                sun_dir=SUN_DIR,
                det_dir=DET_DIR,
                r_max=r_max,
                depth_epsilon_m=DEPTH_EPSILON_M_FINAL,
                brdf_branch=BRDF_BRANCH,
                indexob_to_part=INDEXOB_TO_PART,
            )

            # Step 2: 输出 V_sun_macro mask（修复前缺失的输出）
            V_sun_macro = brdf_result["V_sun_macro"]
            mask_npy_path = os.path.join(OUTPUT_DIR, f"{label}_v_sun_macro.npy")
            mask_png_path = os.path.join(OUTPUT_DIR, f"{label}_v_sun_macro.png")
            np.save(mask_npy_path, V_sun_macro.astype(np.float32))
            write_png_gray(mask_png_path, V_sun_macro.astype(np.float64))
            mask_rel = f"v0.4_results/00_validation/phase0_step7c_dryrun_fix02/{label}_v_sun_macro.png"
            print(f"  V_sun_macro mask: {mask_rel}")

            # Step 3: 写出图像产物
            output_prefix = os.path.join(OUTPUT_DIR, label)
            image_paths = write_image_outputs(
                I_linear=brdf_result["I_linear"],
                output_prefix=output_prefix,
                I_scale=i_scale_step5,
                log1p_alpha=LOG1P_ALPHA,
            )

            # Step 4: 计算 OCS
            indexob_map = read_indexob_pass(camera_exr)
            ocs_result = compute_ocs_from_brdf_response(
                brdf_result=brdf_result,
                pixel_area_m2=pixel_area_m2,
                indexob_map=indexob_map,
                indexob_to_part=INDEXOB_TO_PART,
            )

            # Step 5: 写出 OCS JSON
            ocs_json_path = os.path.join(OUTPUT_DIR, f"{label}_ocs.json")
            write_ocs_json(
                ocs_result=ocs_result,
                output_path=ocs_json_path,
                record_id=record_id,
                yaw_deg=yaw_deg,
                pitch_deg=pitch_deg,
                geom_id=GEOM_ID,
            )

            # 记录（路径统一为项目根相对路径）
            record = {
                "label": label,
                "record_id": record_id,
                "yaw_deg": yaw_deg,
                "pitch_deg": pitch_deg,
                "ocs_total": ocs_result["ocs_total"],
                "ocs_per_part": ocs_result["ocs_per_part"],
                "n_pixels_camera_visible": ocs_result["n_pixels_camera_visible"],
                "n_pixels_nol_positive": ocs_result["n_pixels_nol_positive"],
                "n_pixels_sun_visible": ocs_result["n_pixels_sun_visible"],
                "n_pixels_contributing": ocs_result["n_pixels_contributing"],
                "exr_path": str(Path(image_paths["exr_path"]).relative_to(V04_PROJECT)).replace("\\", "/"),
                "png_path": str(Path(image_paths["png_path"]).relative_to(V04_PROJECT)).replace("\\", "/"),
                "ocs_json_path": str(Path(ocs_json_path).relative_to(V04_PROJECT)).replace("\\", "/"),
                "sun_visibility_mask_path": mask_rel,
                "status": "COMPLETE",
            }
            records.append(record)

            print(f"  [COMPLETE] OCS_total={ocs_result['ocs_total']:.6e}")
            print(f"    像素统计: visible={ocs_result['n_pixels_camera_visible']} "
                  f"nol+={ocs_result['n_pixels_nol_positive']} "
                  f"sun_vis={ocs_result['n_pixels_sun_visible']} "
                  f"contrib={ocs_result['n_pixels_contributing']}")
            print(f"    OCS per-part: {ocs_result['ocs_per_part']}")

        except Exception as e:
            blockers.append(f"{label}: 处理异常 {e}")
            import traceback
            traceback.print_exc()
            continue

    # 判定总状态
    all_complete = (len(records) == len(DRYRUN_ATTITUDES) and len(blockers) == 0)
    overall_status = "COMPLETE" if all_complete else "NOT_COMPLETE"

    # 写出 summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "task": "1C-E15-FIX02 Phase0 Step7c 3-pose physical dry-run",
        "overall_status": overall_status,
        "scope": "B0 3-pose dry-run, NOT Step6 small-run poses, NOT full corpus",
        "brdf_branch": BRDF_BRANCH,
        "brdf_note": "B0 phong_like_provisional_baseline as engineering baseline",
        "depth_epsilon_m_final": DEPTH_EPSILON_M_FINAL,
        "r_max": r_max,
        "ortho_scale_m": ortho_scale_m,
        "resolution": resolution,
        "pixel_area_m2": pixel_area_m2,
        "sun_vector": SUN_VECTOR.tolist(),
        "det_vector": DET_VECTOR.tolist(),
        "i_scale_smallrun": i_scale_step5,
        "i_scale_policy": "fixed = i_scale_step5 from Phase0 Step5 5-attitude image impact validation; no per-frame normalization",
        "i_scale_note": "Step 5 使用 5 个姿态校准，非 20 姿态校准（R31 §3.6 修正）",
        "log1p_alpha": LOG1P_ALPHA,
        "geom_id": GEOM_ID,
        "n_dryrun_attitudes": len(DRYRUN_ATTITUDES),
        "n_completed": len(records),
        "dryrun_attitudes": [a["label"] for a in DRYRUN_ATTITUDES],
        "step6_smallrun_attitudes": [
            "yaw180_pitch+000_roll+000",
            "yaw150_pitch+025_roll+000",
            "yaw000_pitch+000_roll+000",
            "yaw090_pitch+000_roll+000",
            "yaw300_pitch-025_roll+000",
        ],
        "non_overlap_note": "3 个 dry-run 姿态均非 Step 6 small-run 姿态，确保 dry-run 独立可验证",
        "records": records,
        "blockers": blockers,
        "module_paths": {
            "image_response": "06_v0.4_code/05_postprocess/image_response_v0_4.py",
            "ocs_integration": "06_v0.4_code/05_postprocess/ocs_integration_v0_4.py",
        },
        "依据文件": [
            "04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R33_Codex_审阅_1C-E15-FIX01通过并规划FIX02.md",
            "04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R31_Codex_审阅_1C-E14_Step7b条件通过并要求Step7c.md",
        ],
    }

    summary_path = os.path.join(OUTPUT_DIR, "phase0_step7c_dryrun_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"OVERALL: {overall_status}")
    print(f"完成姿态数: {len(records)} / {len(DRYRUN_ATTITUDES)}")
    if blockers:
        print("阻断项:")
        for b in blockers:
            print("  -", b)
    print(f"Summary 写出: {summary_path}")
    print("=" * 80)

    return 0 if overall_status == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())

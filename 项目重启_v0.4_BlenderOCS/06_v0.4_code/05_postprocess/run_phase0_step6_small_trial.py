# -*- coding: utf-8 -*-
"""
run_phase0_step6_small_trial.py —— Phase 0 Step 6 小规模试跑（1C-E11）
========================================================================
任务：正式 BRDF/OCS/image 后处理模块化小规模试跑。

依据：
    - R26 Codex 审阅（Phase 0 Step 5 通过并放行 Step 6）
    - 13 号 §8.2（图像响应链）、§9.2（有效像素规则）、§11（single-geom 主线）
    - 14 号 §3.1/3.2（manifest 字段规范）

范围：
    - 复用 Step 5 的 5 个姿态（或缩减为 3 个代表姿态）
    - 不重渲染 EXR，复用 Step 4 shadow_passes
    - 使用 B0 phong_like_provisional_baseline 作为工程 baseline
    - 输出：I_linear EXR + log1p PNG + per-frame OCS JSON + 统计字段

边界（禁止越界）：
    - 不得进入全量 2664 姿态生成
    - 不得训练模型
    - 不得改写论文正文
    - 不得修改 CLAUDE.md、13/14 冻结文件或路线文件
    - 不得写入 04_Codex审阅/
    - 不得生成 Codex、验收、最终放行等名义文件
    - 明确标注本轮是 B0 small-run，不是全量 corpus，不是训练输入最终 manifest
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
OUTPUT_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "phase0_step6_small_trial")

# 观测几何（与 Step 4/5 一致）
SUN_VECTOR = np.array([1.0, 0.0, 0.3])
DET_VECTOR = np.array([0.5, -1.0, 0.1])
SUN_DIR = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
DET_DIR = DET_VECTOR / np.linalg.norm(DET_VECTOR)

# Step 4/5 校准参数
DEPTH_EPSILON_M_FINAL = 0.7952109582768545

# BRDF 分支
BRDF_BRANCH = "B0"

# log1p 参数（D3 初始）
LOG1P_ALPHA = 10.0

# IndexOB 映射
INDEXOB_TO_PART = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}

# 试跑姿态（复用 Step 5 的 5 个，或可缩减为 3 个代表姿态）
TRIAL_ATTITUDES = [
    {"label": "yaw180_pitch+000_roll+000", "yaw": 180.0, "pitch": 0.0},
    {"label": "yaw150_pitch+025_roll+000", "yaw": 150.0, "pitch": 25.0},
    {"label": "yaw000_pitch+000_roll+000", "yaw": 0.0, "pitch": 0.0},
    {"label": "yaw090_pitch+000_roll+000", "yaw": 90.0, "pitch": 0.0},
    {"label": "yaw300_pitch-025_roll+000", "yaw": 300.0, "pitch": -25.0},
]

# 几何标识符
GEOM_ID = "phase63"


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 80)
    print("Phase 0 Step 6: BRDF/OCS/image 后处理模块化小规模试跑 (1C-E11)")
    print("=" * 80)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # 读取 Step 4/5 参数
    with open(SHADOW_SUMMARY, 'r', encoding='utf-8') as f:
        summary4 = json.load(f)
    r_max = summary4["r_max"]

    with open(STEP5_SUMMARY, 'r', encoding='utf-8') as f:
        summary5 = json.load(f)
    i_scale_step5 = summary5["i_scale_step5"]

    print(f"r_max = {r_max}")
    print(f"DEPTH_EPSILON_M_FINAL = {DEPTH_EPSILON_M_FINAL}")
    print(f"I_scale_smallrun (来自 Step 5) = {i_scale_step5:.6e}")
    print(f"BRDF 分支 = {BRDF_BRANCH}")
    print(f"log1p_alpha = {LOG1P_ALPHA}")
    print(f"试跑姿态数 = {len(TRIAL_ATTITUDES)}")
    print()

    # 计算 pixel_area_m2（与 Step 4 一致：ortho_scale / resolution）
    # 13 号规范和 config_v0_4.py: ORTHO_SCALE_FACTOR = 2.2
    ortho_scale_m = 2.2 * r_max
    resolution = 256
    pixel_area_m2 = (ortho_scale_m / resolution) ** 2

    blockers = []
    records = []

    # 处理每个姿态
    for att in TRIAL_ATTITUDES:
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
            # Step 1: 计算 BRDF 响应
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

            # Step 2: 写出图像产物
            output_prefix = os.path.join(OUTPUT_DIR, label)
            image_paths = write_image_outputs(
                I_linear=brdf_result["I_linear"],
                output_prefix=output_prefix,
                I_scale=i_scale_step5,
                log1p_alpha=LOG1P_ALPHA,
            )

            # Step 3: 计算 OCS
            indexob_map = read_indexob_pass(camera_exr)
            ocs_result = compute_ocs_from_brdf_response(
                brdf_result=brdf_result,
                pixel_area_m2=pixel_area_m2,
                indexob_map=indexob_map,
                indexob_to_part=INDEXOB_TO_PART,
            )

            # Step 4: 写出 OCS JSON
            ocs_json_path = os.path.join(OUTPUT_DIR, f"{label}_ocs.json")
            write_ocs_json(
                ocs_result=ocs_result,
                output_path=ocs_json_path,
                record_id=record_id,
                yaw_deg=yaw_deg,
                pitch_deg=pitch_deg,
                geom_id=GEOM_ID,
            )

            # 记录
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
                "exr_path": os.path.relpath(image_paths["exr_path"], V04_PROJECT),
                "png_path": os.path.relpath(image_paths["png_path"], V04_PROJECT),
                "ocs_json_path": os.path.relpath(ocs_json_path, V04_PROJECT),
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
    all_complete = (len(records) == len(TRIAL_ATTITUDES) and len(blockers) == 0)
    overall_status = "COMPLETE" if all_complete else "NOT_COMPLETE"

    # 写出 summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "task": "1C-E11 Phase0 Step6 BRDF/OCS/image postprocessing small trial",
        "overall_status": overall_status,
        "scope": "B0 small-run, NOT full corpus, NOT training input final manifest",
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
        "i_scale_policy": "fixed = i_scale_step5 from Phase0 Step5; no per-frame normalization",
        "log1p_alpha": LOG1P_ALPHA,
        "geom_id": GEOM_ID,
        "n_trial_attitudes": len(TRIAL_ATTITUDES),
        "n_completed": len(records),
        "records": records,
        "blockers": blockers,
        "module_paths": {
            "image_response": "06_v0.4_code/05_postprocess/image_response_v0_4.py",
            "ocs_integration": "06_v0.4_code/05_postprocess/ocs_integration_v0_4.py",
        },
        "依据文件": [
            "04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/13_v0.4前向模型冻结规范_最终冻结版.md",
            "04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/14_v0.4数据与manifest字段规范_最终冻结版.md",
            "04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R26_Codex_审阅_1C-E10通过并放行Phase0_Step5.md",
        ],
    }

    summary_path = os.path.join(OUTPUT_DIR, "phase0_step6_small_trial_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"OVERALL: {overall_status}")
    print(f"完成姿态数: {len(records)} / {len(TRIAL_ATTITUDES)}")
    if blockers:
        print("阻断项:")
        for b in blockers:
            print("  -", b)
    print(f"Summary 写出: {summary_path}")
    print("=" * 80)

    return 0 if overall_status == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())

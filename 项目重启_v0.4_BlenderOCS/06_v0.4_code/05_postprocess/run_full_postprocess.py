# -*- coding: utf-8 -*-
"""
run_full_postprocess.py —— 全量 BRDF/OCS/image 后处理 driver (1C-E17)
========================================================================
任务：为 1-N 个姿态执行完整后处理链：BRDF → V_sun_macro mask → OCS → image outputs。
支持 checkpoint/resume，可作为全量 2664 的 driver。

使用方式：
    # Smoke 测试（3 姿态）
    python run_full_postprocess.py --attitudes yaw010_pitch+000_roll+000,yaw225_pitch+000_roll+000,yaw315_pitch+000_roll+000

    # 全量（不在此阶段执行）
    python run_full_postprocess.py --all

    # 从已有 summary resume
    python run_full_postprocess.py --resume <fullrun_summary.json>

边界：
    - 当前只用于 smoke 测试
    - 不在此阶段执行全量 2664
    - 不训练模型
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# 模块路径
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

_VALIDATION_DIR = os.path.join(_THIS_DIR, "..", "10_validation")
if _VALIDATION_DIR not in sys.path:
    sys.path.insert(0, _VALIDATION_DIR)
from validate_v_sun_macro_on_image import read_indexob_pass


# ============================================================
# 配置
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")

# 全量 shadow passes 目录
SHADOW_PASSES_DIR = os.path.join(V04_PROJECT, "v0.4_results", "01_fullrun", "shadow_passes")

# 全量后处理输出目录
OUTPUT_DIR = os.path.join(V04_PROJECT, "v0.4_results", "01_fullrun", "postprocess")

# 参数来源（从 Step 5 继承）
STEP5_SUMMARY = os.path.join(V04_PROJECT, "v0.4_results", "00_validation",
                             "v_sun_macro_image_check", "v_sun_macro_image_check_summary.json")
SHADOW_SUMMARY = os.path.join(V04_PROJECT, "v0.4_results", "00_validation",
                              "shadow_validation", "shadow_validation_summary.json")

SUN_VECTOR = np.array([1.0, 0.0, 0.3])
DET_VECTOR = np.array([0.5, -1.0, 0.1])
SUN_DIR = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
DET_DIR = DET_VECTOR / np.linalg.norm(DET_VECTOR)
DEPTH_EPSILON_M_FINAL = 0.7952109582768545
LOG1P_ALPHA = 10.0
INDEXOB_TO_PART = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}
GEOM_ID = "phase63"
BRDF_BRANCH = "B0"


def generate_full_attitude_labels():
    """生成 2664 全量姿态 label 列表"""
    labels = []
    for yaw in range(0, 360, 5):
        for pitch in range(-90, 91, 5):
            labels.append(f"yaw{yaw:03d}_pitch{pitch:+04d}_roll+000")
    return labels


def process_one_attitude(label, yaw_deg, pitch_deg, r_max, i_scale, pixel_area_m2):
    """处理单个姿态：BRDF → mask → OCS → image outputs。返回 record dict 或抛异常。"""
    record_id = f"{GEOM_ID}_yaw{int(yaw_deg):03d}_pitch{pitch_deg:+04.0f}"

    camera_exr = os.path.join(SHADOW_PASSES_DIR, f"{label}_camera.exr")
    sun_exr = os.path.join(SHADOW_PASSES_DIR, f"{label}_sun.exr")

    if not os.path.isfile(camera_exr):
        return None, f"{label}: 缺失 camera EXR"
    if not os.path.isfile(sun_exr):
        return None, f"{label}: 缺失 sun EXR"

    # BRDF 响应
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

    # V_sun_macro mask
    V_sun_macro = brdf_result["V_sun_macro"]
    mask_npy_path = os.path.join(OUTPUT_DIR, f"{label}_v_sun_macro.npy")
    mask_png_path = os.path.join(OUTPUT_DIR, f"{label}_v_sun_macro.png")
    np.save(mask_npy_path, V_sun_macro.astype(np.float32))
    write_png_gray(mask_png_path, V_sun_macro.astype(np.float64))
    mask_rel = f"v0.4_results/01_fullrun/postprocess/{label}_v_sun_macro.png"

    # 图像产物
    output_prefix = os.path.join(OUTPUT_DIR, label)
    image_paths = write_image_outputs(
        I_linear=brdf_result["I_linear"],
        output_prefix=output_prefix,
        I_scale=i_scale,
        log1p_alpha=LOG1P_ALPHA,
    )

    # OCS
    indexob_map = read_indexob_pass(camera_exr)
    ocs_result = compute_ocs_from_brdf_response(
        brdf_result=brdf_result,
        pixel_area_m2=pixel_area_m2,
        indexob_map=indexob_map,
        indexob_to_part=INDEXOB_TO_PART,
    )

    ocs_json_path = os.path.join(OUTPUT_DIR, f"{label}_ocs.json")
    write_ocs_json(
        ocs_result=ocs_result,
        output_path=ocs_json_path,
        record_id=record_id,
        yaw_deg=yaw_deg,
        pitch_deg=pitch_deg,
        geom_id=GEOM_ID,
    )

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
    return record, None


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Full-run BRDF/OCS/image postprocess driver")
    parser.add_argument("--attitudes", default=None,
                        help="逗号分隔的姿态 label 列表（用于 smoke 测试）")
    parser.add_argument("--all", action="store_true",
                        help="全量 2664 模式（[WARN] 此阶段不应执行）")
    parser.add_argument("--resume", default=None,
                        help="从已有 summary JSON resume（跳过已 COMPLETE 的 record）")
    args = parser.parse_args()

    print("=" * 80)
    print("全量 BRDF/OCS/image 后处理 driver (1C-E17)")
    print("=" * 80)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # 参数
    with open(SHADOW_SUMMARY, 'r', encoding='utf-8') as f:
        r_max = json.load(f)["r_max"]
    with open(STEP5_SUMMARY, 'r', encoding='utf-8') as f:
        i_scale = json.load(f)["i_scale_step5"]

    ortho_scale_m = 2.2 * r_max
    pixel_area_m2 = (ortho_scale_m / 256) ** 2

    print(f"r_max = {r_max:.6f}")
    print(f"I_scale = {i_scale:.6e}（来自 Step 5 的 5 姿态 image impact validation）")
    print(f"pixel_area_m2 = {pixel_area_m2:.6e}")

    # 确定姿态列表
    if args.attitudes:
        labels = [l.strip() for l in args.attitudes.split(",")]
    elif args.all:
        labels = generate_full_attitude_labels()
        print(f"[WARN] 全量模式: {len(labels)} 姿态（此阶段不应执行）")
    else:
        print("[ERROR] 需要 --attitudes 或 --all")
        return 1

    # Resume 逻辑
    completed_labels = set()
    if args.resume and os.path.isfile(args.resume):
        with open(args.resume, 'r', encoding='utf-8') as f:
            prev = json.load(f)
        for rec in prev.get("records", []):
            if rec.get("status") == "COMPLETE":
                completed_labels.add(rec["label"])
        print(f"Resume: 已有 {len(completed_labels)} 个 COMPLETE 记录")

    # 过滤已完成
    pending_labels = [l for l in labels if l not in completed_labels]
    print(f"本次待处理: {len(pending_labels)} 个姿态")

    # 处理
    blockers = []
    records = list(completed_labels)  # placeholder, 下面会重建

    # 重新构建 records 列表
    all_records = []
    if args.resume and os.path.isfile(args.resume):
        with open(args.resume, 'r', encoding='utf-8') as f:
            prev = json.load(f)
        all_records = prev.get("records", [])

    for label in pending_labels:
        # 解析 yaw/pitch
        parts = label.split("_")
        yaw_str = parts[0].replace("yaw", "")
        pitch_str = parts[1].replace("pitch", "")
        yaw_deg = float(yaw_str)
        pitch_deg = float(pitch_str)

        print(f"\n--- {label} ---")
        try:
            record, err = process_one_attitude(label, yaw_deg, pitch_deg, r_max, i_scale, pixel_area_m2)
            if record:
                # 更新或追加
                existing = [i for i, r in enumerate(all_records) if r.get("label") == label]
                if existing:
                    all_records[existing[0]] = record
                else:
                    all_records.append(record)
                print(f"  [COMPLETE] OCS_total={record['ocs_total']:.6e} "
                      f"visible={record['n_pixels_camera_visible']} contrib={record['n_pixels_contributing']}")
            else:
                blockers.append(err)
                all_records.append({"label": label, "status": "MISSING", "error": err})
                print(f"  [MISSING] {err}")
        except Exception as e:
            blockers.append(f"{label}: {e}")
            all_records.append({"label": label, "status": "FAILED", "error": str(e)})
            import traceback
            traceback.print_exc()

    n_complete = sum(1 for r in all_records if r.get("status") == "COMPLETE")
    overall = "COMPLETE" if n_complete == len(labels) and len(blockers) == 0 else "NOT_COMPLETE"

    summary = {
        "timestamp": datetime.now().isoformat(),
        "task": "1C-E17 full-run postprocess driver smoke test",
        "overall_status": overall,
        "brdf_branch": BRDF_BRANCH,
        "depth_epsilon_m_final": DEPTH_EPSILON_M_FINAL,
        "r_max": r_max,
        "ortho_scale_m": ortho_scale_m,
        "resolution": 256,
        "pixel_area_m2": pixel_area_m2,
        "i_scale_smallrun": i_scale,
        "i_scale_policy": "fixed = i_scale_step5; no per-frame normalization",
        "log1p_alpha": LOG1P_ALPHA,
        "geom_id": GEOM_ID,
        "n_total_labels": len(labels),
        "n_completed": n_complete,
        "records": all_records,
        "blockers": blockers,
    }

    summary_path = os.path.join(OUTPUT_DIR, "fullrun_postprocess_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"OVERALL: {overall}")
    print(f"完成: {n_complete} / {len(labels)}")
    if blockers:
        print("阻断项:")
        for b in blockers:
            print("  -", b)
    print(f"Summary: {summary_path}")
    print("=" * 80)

    return 0 if overall == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
build_image_manifest_v0_4.py —— Image Manifest Builder
========================================================
任务：从 Phase 0 Step 6 / Step 7c 的产物构建 image manifest v0.4

依据：
    - 14 号 §3.2（Image manifest schema）
    - R28 Codex 审阅（1C-E13 Phase 0 Step 7a）
    - R31 Codex 审阅（Step 7b 条件通过要求 Step 7c）
    - R33 Codex 审阅（1C-E15-FIX02 builder/matrix/mask 修复）

修改记录（1C-E15-FIX02）：
    - 新增 --data-root 参数，所有 record 路径统一为 data_root 相对路径

输入：
    - Step summary JSON（含 records 列表）

输出：
    - image_manifest_v0_4_*.json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


def build_image_manifest(
    step_summary_path,
    step_output_dir,
    output_path,
    data_root=".",
):
    """
    构建 image manifest v0.4

    Args:
        step_summary_path: Step summary JSON 路径
        step_output_dir: 输出目录（包含 EXR/PNG）
        output_path: 输出 manifest 路径
        data_root: 所有 record 路径的解析根（项目根目录）
    """
    print("=" * 80)
    print("Image Manifest Builder v0.4 (FIX02 路径基准统一版)")
    print("=" * 80)

    data_root_resolved = str(Path(data_root).resolve()).replace("\\", "/")
    print(f"data_root              : {data_root}")
    print(f"data_root_resolved     : {data_root_resolved}")

    # 读取 Step summary
    with open(step_summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    print(f"读取 Step summary: {step_summary_path}")
    print(f"  姿态数: {summary.get('n_completed', len(summary.get('records', [])))}")
    print(f"  I_scale: {summary.get('i_scale_smallrun', summary.get('i_scale_step5', 'N/A'))}")

    # 提取全局参数
    resolution = summary.get("resolution")
    i_scale = summary.get("i_scale_smallrun", summary.get("i_scale_step5"))
    log1p_alpha = summary.get("log1p_alpha", 10.0)
    geom_id = summary.get("geom_id", "phase63")
    brdf_branch = summary.get("brdf_branch", "B0")

    # 版本字段
    geometry_version = "v0.4_phase0_step7c_dryrun"
    brdf_version = f"v0.4_{brdf_branch}_phong_like_provisional"
    visibility_version = "v0.4_level2_sun_shadow_reprojection_step7c"
    image_preprocess_version = "v0.4_log1p_step7c"

    # 构建 records
    records = []
    for rec in summary["records"]:
        label = rec["label"]
        record_id = rec["record_id"]
        yaw_deg = rec["yaw_deg"]
        pitch_deg = rec["pitch_deg"]

        # 路径基准统一：所有路径为 data_root 相对路径，使用 POSIX "/"
        png_raw = rec.get("png_path", "")
        exr_raw = rec.get("exr_path", "")

        try:
            png_abs = os.path.join(data_root, png_raw) if not os.path.isabs(png_raw) else png_raw
            png_rel = str(Path(png_abs).relative_to(data_root_resolved)).replace("\\", "/")
        except (ValueError, TypeError):
            png_rel = png_raw.replace("\\", "/")

        try:
            exr_abs = os.path.join(data_root, exr_raw) if not os.path.isabs(exr_raw) else exr_raw
            exr_rel = str(Path(exr_abs).relative_to(data_root_resolved)).replace("\\", "/")
        except (ValueError, TypeError):
            exr_rel = exr_raw.replace("\\", "/")

        record = {
            "record_id": record_id,
            "yaw_deg": yaw_deg,
            "pitch_deg": pitch_deg,
            "geom_id": geom_id,
            "png_path": png_rel,
            "exr_linear_path": exr_rel,
            "is_clean": True,
            "I_scale_record": i_scale,
        }

        records.append(record)
        print(f"  添加 record: {record_id}")

    # 确定 brdf_model（R34 §5.1 小修：优先匹配 B1/improved_phong 再匹配泛化 phong/provisional）
    # 顺序重要：B1 的 brdf_version 可能包含 "phong"，必须优先于泛化 phong 匹配
    if "B1" in brdf_version or "improved_phong" in brdf_version:
        brdf_model = "improved_phong_book_model_pending_author_confirmation"
    elif "GGX" in brdf_version or "ggx" in brdf_version:
        brdf_model = "ggx_cook_torrance"
    elif "B0" in brdf_version or "phong" in brdf_version or "provisional" in brdf_version:
        brdf_model = "phong_like_provisional_baseline"
    else:
        brdf_model = "unknown"
        print(f"  警告：无法从 brdf_version={brdf_version} 推断 brdf_model，使用 'unknown'")

    # 构建 manifest
    manifest = {
        "geometry_version": geometry_version,
        "brdf_version": brdf_version,
        "visibility_version": visibility_version,
        "image_preprocess_version": image_preprocess_version,
        "brdf_model": brdf_model,
        "sun_visibility": "camera_visible_nol_plus_sun_shadow_pass",
        "shadow_mapping_method": "sun_view_depth_reprojection",
        "image_source": "Blender-derived pixel-level BRDF image v0.4",
        "preprocessing": {
            "log1p_alpha": log1p_alpha,
            "I_scale": i_scale,
            "input_range": [0.0, 1.0],
            "v_sun_macro_mode": "shadow_mask",
            "v_sun_macro_applied_to_image": True,
        },
        "resolution": resolution,
        "data_root": data_root_resolved,
        "records": records,
    }

    # 写出
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n写出 image manifest: {output_path}")
    print(f"  records 数量: {len(records)}")
    print("=" * 80)

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Build image manifest v0.4 from trial summary")
    parser.add_argument("--step-summary", required=True, help="Step summary JSON 路径")
    parser.add_argument("--step-output-dir", required=True, help="输出目录")
    parser.add_argument("--output", required=True, help="输出 manifest 路径")
    parser.add_argument(
        "--data-root", default=".",
        help="所有 manifest record 路径的解析根（默认当前工作目录 '.'）",
    )

    args = parser.parse_args()

    build_image_manifest(
        step_summary_path=args.step_summary,
        step_output_dir=args.step_output_dir,
        output_path=args.output,
        data_root=args.data_root,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

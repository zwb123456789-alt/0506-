# -*- coding: utf-8 -*-
"""
build_ocs_manifest_v0_4.py —— OCS Manifest Builder
====================================================
任务：从 Phase 0 Step 6 / Step 7c 的产物构建 OCS manifest v0.4

依据：
    - 14 号 §3.1（OCS manifest schema）
    - R28 Codex 审阅（1C-E13 Phase 0 Step 7a）
    - R31 Codex 审阅（Step 7b 条件通过要求 Step 7c）
    - R33 Codex 审阅（1C-E15-FIX02 builder/matrix/mask 修复）

修改记录（1C-E15-FIX02）：
    - 新增 --data-root 参数，所有 record 路径统一为 data_root 相对路径
    - camera_matrix_world / sun_camera_matrix_world 从外部 JSON 读取
    - sun_visibility_mask_path 现在可接受外部传入
    - position_exr_path 保持 null（Phase 0 暂未独立输出）

输入：
    - Step summary JSON（含 records 列表）
    - Shadow passes 目录
    - 相机矩阵 JSON（来自 Blender log_camera_matrices.py）
    - 可选 sun_visibility_mask 目录

输出：
    - ocs_manifest_v0_4_*.json
"""

import os
import sys
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime


def build_ocs_manifest(
    step_summary_path,
    step_output_dir,
    shadow_passes_dir,
    output_path,
    data_root=".",
    camera_matrix_json=None,
    sun_visibility_mask_dir=None,
):
    """
    构建 OCS manifest v0.4

    Args:
        step_summary_path: Step summary JSON 路径
        step_output_dir: 输出目录（包含 OCS JSON 和 EXR/PNG）
        shadow_passes_dir: shadow_passes 目录（包含 camera/sun EXR）
        output_path: 输出 manifest 路径
        data_root: 所有 record 路径的解析根（项目根目录）
        camera_matrix_json: 相机矩阵 JSON 路径（来自 Blender matrix_world 日志）
        sun_visibility_mask_dir: V_sun_macro mask 目录（可选）
    """
    print("=" * 80)
    print("OCS Manifest Builder v0.4 (FIX02 路径基准统一版)")
    print("=" * 80)

    data_root_resolved = str(Path(data_root).resolve()).replace("\\", "/")
    print(f"data_root              : {data_root}")
    print(f"data_root_resolved     : {data_root_resolved}")

    # 读取 Step summary
    with open(step_summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    print(f"读取 Step summary: {step_summary_path}")
    print(f"  姿态数: {summary.get('n_completed', len(summary.get('records', [])))}")
    print(f"  BRDF 分支: {summary.get('brdf_branch', 'unknown')}")

    # 加载相机矩阵
    camera_matrix_world = None
    sun_camera_matrix_world = None

    if camera_matrix_json and os.path.isfile(camera_matrix_json):
        with open(camera_matrix_json, 'r', encoding='utf-8') as f:
            mat_data = json.load(f)
        camera_matrix_world = mat_data.get("camera_matrix_world")
        sun_camera_matrix_world = mat_data.get("sun_camera_matrix_world")
        print(f"从 Blender 日志读取相机矩阵: {camera_matrix_json}")
        if camera_matrix_world:
            print(f"  camera_matrix_world: 4x4, 来源=Camera_Detector.matrix_world")
        if sun_camera_matrix_world:
            print(f"  sun_camera_matrix_world: 4x4, 来源=Camera_Sun.matrix_world")
    else:
        print("警告：未提供 camera_matrix_json 或文件不存在，矩阵字段将置 null")
        if camera_matrix_json:
            print(f"  期望路径: {camera_matrix_json}")

    # 提取全局参数
    r_max = summary.get("r_max")
    ortho_scale_m = summary.get("ortho_scale_m")
    resolution = summary.get("resolution")
    pixel_area_m2 = summary.get("pixel_area_m2")
    depth_epsilon_m = summary.get("depth_epsilon_m_final")
    sun_vector = np.array(summary.get("sun_vector", [1.0, 0.0, 0.3]))
    det_vector = np.array(summary.get("det_vector", [0.5, -1.0, 0.1]))
    sun_dir = (sun_vector / np.linalg.norm(sun_vector)).tolist()
    det_dir = (det_vector / np.linalg.norm(det_vector)).tolist()
    geom_id = summary.get("geom_id", "phase63")

    # 版本字段
    brdf_branch = summary.get("brdf_branch", "B0")
    geometry_version = f"v0.4_phase0_step7c_dryrun"
    brdf_version = f"v0.4_{brdf_branch}_phong_like_provisional"
    visibility_version = "v0.4_level2_sun_shadow_reprojection_step7c"
    ocs_integration_version = "v0.4_pixel_level_step7c"

    # 构建 records
    records = []
    for rec in summary["records"]:
        label = rec["label"]
        record_id = rec["record_id"]
        yaw_deg = rec["yaw_deg"]
        pitch_deg = rec["pitch_deg"]

        # OCS JSON 路径验证
        ocs_json_path = rec.get("ocs_json_path")
        if ocs_json_path:
            # 路径可能相对于 data_root 或绝对路径；统一转为 data_root 相对
            ocs_json_abs = os.path.join(data_root, ocs_json_path) if not os.path.isabs(ocs_json_path) else ocs_json_path
        else:
            ocs_json_abs = None

        if ocs_json_abs and os.path.isfile(ocs_json_abs):
            with open(ocs_json_abs, 'r', encoding='utf-8') as f:
                ocs_data = json.load(f)
        else:
            ocs_data = {}
            if ocs_json_abs:
                print(f"  警告：OCS JSON 不存在 {ocs_json_abs}")

        # 路径基准统一：所有路径为 data_root 相对路径，使用 POSIX "/"
        camera_exr_abs = os.path.join(shadow_passes_dir, f"{label}_camera.exr")
        sun_exr_abs = os.path.join(shadow_passes_dir, f"{label}_sun.exr")

        try:
            camera_exr_rel = str(Path(camera_exr_abs).relative_to(data_root_resolved)).replace("\\", "/")
        except ValueError:
            camera_exr_rel = camera_exr_abs.replace("\\", "/")

        try:
            sun_exr_rel = str(Path(sun_exr_abs).relative_to(data_root_resolved)).replace("\\", "/")
        except ValueError:
            sun_exr_rel = sun_exr_abs.replace("\\", "/")

        # exr_path / png_path（来自 summary，需要转为 data_root 相对）
        exr_raw = rec.get("exr_path", "")
        png_raw = rec.get("png_path", "")

        try:
            exr_abs_check = os.path.join(data_root, exr_raw) if not os.path.isabs(exr_raw) else exr_raw
            exr_rel = str(Path(exr_abs_check).relative_to(data_root_resolved)).replace("\\", "/")
        except (ValueError, TypeError):
            exr_rel = exr_raw.replace("\\", "/")

        try:
            png_abs_check = os.path.join(data_root, png_raw) if not os.path.isabs(png_raw) else png_raw
            png_rel = str(Path(png_abs_check).relative_to(data_root_resolved)).replace("\\", "/")
        except (ValueError, TypeError):
            png_rel = png_raw.replace("\\", "/")

        position_exr_rel = None  # Phase 0 暂未独立输出 Position pass

        # sun_visibility_mask_path
        sun_visibility_mask_rel = None
        if sun_visibility_mask_dir:
            # 先尝试 .png
            mask_png = os.path.join(sun_visibility_mask_dir, f"{label}_v_sun_macro.png")
            if os.path.isfile(mask_png):
                try:
                    sun_visibility_mask_rel = str(Path(mask_png).relative_to(data_root_resolved)).replace("\\", "/")
                except ValueError:
                    sun_visibility_mask_rel = mask_png.replace("\\", "/")
            else:
                # 尝试 .npy
                mask_npy = os.path.join(sun_visibility_mask_dir, f"{label}_v_sun_macro.npy")
                if os.path.isfile(mask_npy):
                    try:
                        sun_visibility_mask_rel = str(Path(mask_npy).relative_to(data_root_resolved)).replace("\\", "/")
                    except ValueError:
                        sun_visibility_mask_rel = mask_npy.replace("\\", "/")

        record = {
            "record_id": record_id,
            "yaw_deg": yaw_deg,
            "pitch_deg": pitch_deg,
            "geom_id": geom_id,
            "sun_dir": sun_dir,
            "det_dir": det_dir,
            "ocs_total": rec.get("ocs_total", 0.0),
            "ocs_per_part": rec.get("ocs_per_part", {}),
            "n_pixels_camera_visible": rec.get("n_pixels_camera_visible", 0),
            "n_pixels_nol_positive": rec.get("n_pixels_nol_positive", 0),
            "n_pixels_sun_visible": rec.get("n_pixels_sun_visible", 0),
            "n_pixels_contributing": rec.get("n_pixels_contributing", 0),
            "n_pixels_per_part": ocs_data.get("n_pixels_per_part", rec.get("n_pixels_per_part", {})),
            "camera_exr_path": camera_exr_rel,
            "position_exr_path": position_exr_rel,
            "sun_depth_exr_path": sun_exr_rel,
            "sun_visibility_mask_path": sun_visibility_mask_rel,
            "exr_path": exr_rel,
            "png_path": png_rel,
            "camera_matrix_world": camera_matrix_world,
            "sun_camera_matrix_world": sun_camera_matrix_world,
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
        "ocs_integration_version": ocs_integration_version,
        "ocs_source": "Blender-derived pixel-level OCS v0.4",
        "brdf_model": brdf_model,
        "sampling": f"Blender Cycles orthogonal projection, {resolution}x{resolution}",
        "ortho_scale_m": ortho_scale_m,
        "pixel_area_m2": pixel_area_m2,
        "resolution": resolution,
        "sun_visibility": "camera_visible_nol_plus_sun_shadow_pass",
        "shadow_mapping_method": "sun_view_depth_reprojection",
        "depth_epsilon_m": depth_epsilon_m,
        "data_root": data_root_resolved,
        "records": records,
    }

    # 写出
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n写出 OCS manifest: {output_path}")
    print(f"  records 数量: {len(records)}")
    print("=" * 80)

    return manifest


def main():
    parser = argparse.ArgumentParser(description="Build OCS manifest v0.4 from trial summary")
    parser.add_argument("--step-summary", required=True, help="Step summary JSON 路径")
    parser.add_argument("--step-output-dir", required=True, help="输出目录（包含 OCS JSON 和 EXR/PNG）")
    parser.add_argument("--shadow-passes-dir", required=True, help="shadow_passes 目录")
    parser.add_argument("--output", required=True, help="输出 manifest 路径")
    parser.add_argument(
        "--data-root", default=".",
        help="所有 manifest record 路径的解析根（默认当前工作目录 '.'）",
    )
    parser.add_argument(
        "--camera-matrix-json", default=None,
        help="Blender 相机矩阵 JSON 路径（来自 log_camera_matrices.py）",
    )
    parser.add_argument(
        "--sun-visibility-mask-dir", default=None,
        help="V_sun_macro mask 输出目录（可选）",
    )

    args = parser.parse_args()

    build_ocs_manifest(
        step_summary_path=args.step_summary,
        step_output_dir=args.step_output_dir,
        shadow_passes_dir=args.shadow_passes_dir,
        output_path=args.output,
        data_root=args.data_root,
        camera_matrix_json=args.camera_matrix_json,
        sun_visibility_mask_dir=args.sun_visibility_mask_dir,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

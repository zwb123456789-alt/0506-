# -*- coding: utf-8 -*-
"""
check_manifest_consistency_v0_4.py —— Manifest Consistency Checker
===================================================================
任务：检查 OCS manifest 和 image manifest 的一致性

依据：
    - 14 号 §8.1（一致性规则）
    - R28 Codex 审阅（1C-E13 Phase 0 Step 7a）
    - R31 Codex 审阅（1C-E14 Step 7b，新增检查 12-17）
    - R32 Codex 返工单（1C-E15-FIX01，路径解析与门禁修复）

检查项（共 17 项）：
    1.  geometry_version_match
    2.  brdf_version_match
    3.  visibility_version_match
    4.  sun_visibility_match
    5.  shadow_mapping_method_match
    6.  brdf_model_match
    7.  brdf_model_vs_brdf_version_consistency
    8.  v_sun_macro_mode_consistency
    9.  i_scale_match
    10. record_id_set_match
    11. per_record_consistency
    12. path_base_consistency        —— R31/R32：结构 + 可选 --require-prefix
    13. ocs_paths_exist              —— R32：相对 --data-root 解析，区分基准不一致与真实缺失
    14. image_paths_exist           —— R32：同上
    15. camera_matrix_non_null_and_valid —— R31/R32：4x4 结构 + 16 元素 float 可转性
    16. sun_visibility_mask_path_non_null_and_exists
    17. records_completeness        —— R32：可选 --expected-record-count gate

路径解析说明（R32-B1）：
    所有 record 路径一律相对 --data-root 解析（默认当前工作目录 "."），
    不再从 manifest 文件路径反推项目根，避免真实存在文件被误报 missing。

输出：
    - consistency_check_report.json（包含 PASS/NOT_COMPLETE 状态）
"""

import os
import sys
import json
import argparse
from pathlib import Path, PurePosixPath
from datetime import datetime


def _normalize_rel_path(path):
    """将 manifest 中的路径规范化为 POSIX 风格（允许 Windows 反斜杠输入）。"""
    return str(path).replace("\\", "/")


def _resolve_under_root(data_root, path):
    """统一使用 Path(data_root) / 规范化后的相对路径解析。"""
    return Path(data_root) / _normalize_rel_path(path)


def _path_structure_issue(path, require_prefix=None):
    """
    检查路径结构是否合法（R32-B2）：
        - 必须为相对路径（不含盘符、不以 / 开头）
        - 不含 .. 越界段
        - 若指定 require_prefix，则必须以该前缀开头
    返回 None 表示合法，否则返回问题描述字符串。
    """
    norm = _normalize_rel_path(path)

    # 绝对盘符（Windows: C:/...）或 POSIX 绝对路径
    if len(norm) >= 2 and norm[1] == ":":
        return f"absolute drive path not allowed: {norm}"
    if norm.startswith("/"):
        return f"absolute path not allowed: {norm}"

    parts = PurePosixPath(norm).parts
    if ".." in parts:
        return f"path escapes data_root via '..': {norm}"

    if require_prefix and not norm.startswith(require_prefix):
        return f"path does not start with required prefix '{require_prefix}': {norm}"

    return None


def check_consistency(
    ocs_manifest_path,
    image_manifest_path,
    step6_summary_path,
    output_path,
    data_root=".",
    require_prefix=None,
    expected_record_count=None,
):
    """
    检查 OCS manifest 和 image manifest 的一致性

    Args:
        ocs_manifest_path: OCS manifest 路径
        image_manifest_path: Image manifest 路径
        step6_summary_path: Step 6 summary 路径
        output_path: 输出报告路径
        data_root: 所有 record 路径的解析根（默认当前工作目录 "."）
        require_prefix: 可选，当前数据布局约束要求的路径前缀（如 "v0.4_results/"）
        expected_record_count: 可选，启用 completeness gate 的期望记录数

    Returns:
        dict: 检查报告
    """
    print("=" * 80)
    print("Manifest Consistency Checker v0.4")
    print("=" * 80)

    data_root_resolved = str(Path(data_root).resolve()).replace("\\", "/")
    print(f"data_root             : {data_root}")
    print(f"data_root_resolved    : {data_root_resolved}")
    print(f"require_prefix        : {require_prefix}")
    print(f"expected_record_count : {expected_record_count}")
    print()

    # 读取 manifests
    with open(ocs_manifest_path, 'r', encoding='utf-8') as f:
        ocs_manifest = json.load(f)

    with open(image_manifest_path, 'r', encoding='utf-8') as f:
        image_manifest = json.load(f)

    with open(step6_summary_path, 'r', encoding='utf-8') as f:
        step6_summary = json.load(f)

    print(f"读取 OCS manifest: {ocs_manifest_path}")
    print(f"  records 数量: {len(ocs_manifest['records'])}")
    print(f"读取 Image manifest: {image_manifest_path}")
    print(f"  records 数量: {len(image_manifest['records'])}")
    print(f"读取 Step 6 summary: {step6_summary_path}")
    print()

    # 检查项列表
    checks = []
    all_pass = True

    # 检查 1: geometry_version 一致
    check_name = "geometry_version_match"
    ocs_geom = ocs_manifest.get("geometry_version")
    img_geom = image_manifest.get("geometry_version")
    status = "PASS" if ocs_geom == img_geom else "FAIL"
    if ocs_geom is None or img_geom is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "ocs_value": ocs_geom,
        "image_value": img_geom,
    })
    print(f"[{status}] {check_name}: OCS={ocs_geom}, Image={img_geom}")

    # 检查 2: brdf_version 一致
    check_name = "brdf_version_match"
    ocs_brdf = ocs_manifest.get("brdf_version")
    img_brdf = image_manifest.get("brdf_version")
    status = "PASS" if ocs_brdf == img_brdf else "FAIL"
    if ocs_brdf is None or img_brdf is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "ocs_value": ocs_brdf,
        "image_value": img_brdf,
    })
    print(f"[{status}] {check_name}: OCS={ocs_brdf}, Image={img_brdf}")

    # 检查 3: visibility_version 一致
    check_name = "visibility_version_match"
    ocs_vis = ocs_manifest.get("visibility_version")
    img_vis = image_manifest.get("visibility_version")
    status = "PASS" if ocs_vis == img_vis else "FAIL"
    if ocs_vis is None or img_vis is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "ocs_value": ocs_vis,
        "image_value": img_vis,
    })
    print(f"[{status}] {check_name}: OCS={ocs_vis}, Image={img_vis}")

    # 检查 4: sun_visibility 一致
    check_name = "sun_visibility_match"
    ocs_sun_vis = ocs_manifest.get("sun_visibility")
    img_sun_vis = image_manifest.get("sun_visibility")
    status = "PASS" if ocs_sun_vis == img_sun_vis else "FAIL"
    if ocs_sun_vis is None or img_sun_vis is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "ocs_value": ocs_sun_vis,
        "image_value": img_sun_vis,
    })
    print(f"[{status}] {check_name}: OCS={ocs_sun_vis}, Image={img_sun_vis}")

    # 检查 5: shadow_mapping_method 一致
    check_name = "shadow_mapping_method_match"
    ocs_shadow = ocs_manifest.get("shadow_mapping_method")
    img_shadow = image_manifest.get("shadow_mapping_method")
    status = "PASS" if ocs_shadow == img_shadow else "FAIL"
    if ocs_shadow is None or img_shadow is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "ocs_value": ocs_shadow,
        "image_value": img_shadow,
    })
    print(f"[{status}] {check_name}: OCS={ocs_shadow}, Image={img_shadow}")

    # 检查 6: brdf_model 一致（R29-B2 新增）
    check_name = "brdf_model_match"
    ocs_brdf_model = ocs_manifest.get("brdf_model")
    img_brdf_model = image_manifest.get("brdf_model")
    status = "PASS" if ocs_brdf_model == img_brdf_model else "FAIL"
    if ocs_brdf_model is None or img_brdf_model is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "ocs_value": ocs_brdf_model,
        "image_value": img_brdf_model,
    })
    print(f"[{status}] {check_name}: OCS={ocs_brdf_model}, Image={img_brdf_model}")

    # 检查 7: brdf_model 与 brdf_version 一致性（R29-B2 新增）
    check_name = "brdf_model_vs_brdf_version_consistency"

    # 检查 OCS manifest 的 brdf_model 与 brdf_version 是否一致
    ocs_brdf_version_lower = (ocs_brdf or "").lower()
    ocs_brdf_model_lower = (ocs_brdf_model or "").lower()

    ocs_consistency = True
    ocs_issue = None

    # 规则：brdf_version 包含 B0/phong/provisional 时，brdf_model 不能是 ggx_cook_torrance
    if any(keyword in ocs_brdf_version_lower for keyword in ["b0", "phong", "provisional"]):
        if ocs_brdf_model_lower == "ggx_cook_torrance":
            ocs_consistency = False
            ocs_issue = "brdf_version contains B0/phong/provisional but brdf_model is ggx_cook_torrance"

    # 规则：brdf_version 包含 GGX 时，brdf_model 不应是 phong
    if any(keyword in ocs_brdf_version_lower for keyword in ["ggx"]):
        if "phong" in ocs_brdf_model_lower:
            ocs_consistency = False
            ocs_issue = "brdf_version contains GGX but brdf_model is phong_like"

    # 检查 Image manifest 的 brdf_model 与 brdf_version 是否一致
    img_brdf_version_lower = (img_brdf or "").lower()
    img_brdf_model_lower = (img_brdf_model or "").lower()

    img_consistency = True
    img_issue = None

    if any(keyword in img_brdf_version_lower for keyword in ["b0", "phong", "provisional"]):
        if img_brdf_model_lower == "ggx_cook_torrance":
            img_consistency = False
            img_issue = "brdf_version contains B0/phong/provisional but brdf_model is ggx_cook_torrance"

    if any(keyword in img_brdf_version_lower for keyword in ["ggx"]):
        if "phong" in img_brdf_model_lower:
            img_consistency = False
            img_issue = "brdf_version contains GGX but brdf_model is phong_like"

    if ocs_brdf_model is None or img_brdf_model is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif ocs_consistency and img_consistency:
        status = "PASS"
    else:
        status = "FAIL"
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "ocs_consistency": ocs_consistency,
        "ocs_issue": ocs_issue,
        "img_consistency": img_consistency,
        "img_issue": img_issue,
    })
    print(f"[{status}] {check_name}: OCS_consistency={ocs_consistency}, Image_consistency={img_consistency}")

    # 检查 8: v_sun_macro_mode 与 sun_visibility 对应
    check_name = "v_sun_macro_mode_consistency"
    v_sun_mode = image_manifest.get("preprocessing", {}).get("v_sun_macro_mode")
    v_sun_applied = image_manifest.get("preprocessing", {}).get("v_sun_macro_applied_to_image")

    if ocs_sun_vis == "camera_visible_nol":
        expected_mode = "identity"
    elif ocs_sun_vis in ["camera_visible_nol_plus_sun_shadow_pass", "camera_visible_nol_plus_python_raycast"]:
        expected_mode = "shadow_mask"
    else:
        expected_mode = None

    if v_sun_mode is None or expected_mode is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif v_sun_mode == expected_mode and v_sun_applied is True:
        status = "PASS"
    else:
        status = "FAIL"
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "sun_visibility": ocs_sun_vis,
        "v_sun_macro_mode": v_sun_mode,
        "expected_mode": expected_mode,
        "v_sun_macro_applied_to_image": v_sun_applied,
    })
    print(f"[{status}] {check_name}: sun_visibility={ocs_sun_vis}, mode={v_sun_mode}, expected={expected_mode}")

    # 检查 9: I_scale 与 Step 6 summary 一致
    check_name = "i_scale_match"
    img_i_scale = image_manifest.get("preprocessing", {}).get("I_scale")
    step6_i_scale = step6_summary.get("i_scale_smallrun")

    if img_i_scale is None or step6_i_scale is None:
        status = "NOT_COMPLETE"
        all_pass = False
    elif abs(img_i_scale - step6_i_scale) < 1e-9:
        status = "PASS"
    else:
        status = "FAIL"
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "image_i_scale": img_i_scale,
        "step6_i_scale": step6_i_scale,
    })
    print(f"[{status}] {check_name}: Image={img_i_scale}, Step6={step6_i_scale}")

    # 检查 10: record_id 集合一致
    check_name = "record_id_set_match"
    ocs_record_ids = set(r["record_id"] for r in ocs_manifest["records"])
    img_record_ids = set(r["record_id"] for r in image_manifest["records"])

    if ocs_record_ids == img_record_ids:
        status = "PASS"
    else:
        status = "FAIL"
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "ocs_record_ids": sorted(ocs_record_ids),
        "image_record_ids": sorted(img_record_ids),
        "only_in_ocs": sorted(ocs_record_ids - img_record_ids),
        "only_in_image": sorted(img_record_ids - ocs_record_ids),
    })
    print(f"[{status}] {check_name}: OCS={len(ocs_record_ids)}, Image={len(img_record_ids)}")

    # 检查 11: 每个 record 的 yaw/pitch/geom_id 一致
    check_name = "per_record_consistency"
    ocs_records = {r["record_id"]: r for r in ocs_manifest["records"]}
    img_records = {r["record_id"]: r for r in image_manifest["records"]}

    per_record_checks = []
    for record_id in ocs_record_ids & img_record_ids:
        ocs_rec = ocs_records[record_id]
        img_rec = img_records[record_id]

        yaw_match = abs(ocs_rec["yaw_deg"] - img_rec["yaw_deg"]) < 1e-6
        pitch_match = abs(ocs_rec["pitch_deg"] - img_rec["pitch_deg"]) < 1e-6
        geom_match = ocs_rec["geom_id"] == img_rec["geom_id"]

        rec_status = "PASS" if (yaw_match and pitch_match and geom_match) else "FAIL"
        if rec_status == "FAIL":
            all_pass = False

        per_record_checks.append({
            "record_id": record_id,
            "status": rec_status,
            "yaw_match": yaw_match,
            "pitch_match": pitch_match,
            "geom_match": geom_match,
        })

    overall_per_record = "PASS" if all(c["status"] == "PASS" for c in per_record_checks) else "FAIL"
    checks.append({
        "check": check_name,
        "status": overall_per_record,
        "per_record_details": per_record_checks,
    })
    print(f"[{overall_per_record}] {check_name}: {len(per_record_checks)} records checked")

    # 检查 12: 路径基准一致性（R31 §3.1 / R32-B2 修正）
    # 说明：检查路径结构合法性（相对、无盘符、无 .. 越界），并在指定 --require-prefix
    #       时要求该前缀。require_prefix 是「当前 Phase0 数据布局约束」，不是永久 schema 规则。
    check_name = "path_base_consistency"
    inconsistent_paths = []

    ocs_path_keys = ["camera_exr_path", "sun_depth_exr_path", "exr_path", "png_path"]
    img_path_keys = ["png_path", "exr_linear_path"]

    for rec in ocs_manifest["records"]:
        for path_key in ocs_path_keys:
            path = rec.get(path_key)
            if path:
                issue = _path_structure_issue(path, require_prefix)
                if issue:
                    inconsistent_paths.append(f"OCS {rec['record_id']}.{path_key}: {issue}")

    for rec in image_manifest["records"]:
        for path_key in img_path_keys:
            path = rec.get(path_key)
            if path:
                issue = _path_structure_issue(path, require_prefix)
                if issue:
                    inconsistent_paths.append(f"Image {rec['record_id']}.{path_key}: {issue}")

    status = "PASS" if not inconsistent_paths else "FAIL"
    if status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "require_prefix": require_prefix,
        "note": (
            "require_prefix 为当前 Phase0 数据布局约束（relative to v0.4 data root），"
            "非永久 schema 规则；通过 --require-prefix 配置或留空禁用前缀约束。"
        ),
        "inconsistent_paths": inconsistent_paths,
    })
    print(f"[{status}] {check_name}: {len(inconsistent_paths)} inconsistencies")

    # 检查 13: OCS manifest 路径存在性（R31 §3.1 / R32-B1 修正）
    # 相对 data_root 解析；区分「基准不一致」（交由 check 12 拦截）与「文件真实缺失」。
    check_name = "ocs_paths_exist"
    missing_ocs = []
    base_inconsistent_ocs = []

    for rec in ocs_manifest["records"]:
        for path_key in ocs_path_keys:
            path = rec.get(path_key)
            if not path:
                continue
            issue = _path_structure_issue(path, require_prefix)
            if issue:
                # 基准/结构不一致：不当作真实缺失，留给 path_base_consistency 拦截
                base_inconsistent_ocs.append(f"{rec['record_id']}.{path_key}: {_normalize_rel_path(path)}")
                continue
            full_path = _resolve_under_root(data_root, path)
            if not full_path.is_file():
                missing_ocs.append(f"{rec['record_id']}.{path_key}: {_normalize_rel_path(path)}")

    status = "PASS" if not missing_ocs else "FAIL"
    if status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "data_root_resolved": data_root_resolved,
        "missing_paths": missing_ocs,
        "base_inconsistent_paths": base_inconsistent_ocs,
    })
    print(f"[{status}] {check_name}: {len(missing_ocs)} missing, {len(base_inconsistent_ocs)} base-inconsistent")

    # 检查 14: Image manifest 路径存在性（R31 §3.1 / R32-B1 修正）
    check_name = "image_paths_exist"
    missing_img = []
    base_inconsistent_img = []

    for rec in image_manifest["records"]:
        for path_key in img_path_keys:
            path = rec.get(path_key)
            if not path:
                continue
            issue = _path_structure_issue(path, require_prefix)
            if issue:
                base_inconsistent_img.append(f"{rec['record_id']}.{path_key}: {_normalize_rel_path(path)}")
                continue
            full_path = _resolve_under_root(data_root, path)
            if not full_path.is_file():
                missing_img.append(f"{rec['record_id']}.{path_key}: {_normalize_rel_path(path)}")

    status = "PASS" if not missing_img else "FAIL"
    if status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "data_root_resolved": data_root_resolved,
        "missing_paths": missing_img,
        "base_inconsistent_paths": base_inconsistent_img,
    })
    print(f"[{status}] {check_name}: {len(missing_img)} missing, {len(base_inconsistent_img)} base-inconsistent")

    # 检查 15: camera_matrix_world 非空、4x4 结构、16 元素 float 可转性（R31 §3.2 / R32-B3）
    check_name = "camera_matrix_non_null_and_valid"
    invalid_matrix_records = []

    def _matrix_issues(field_name, mat):
        """返回该矩阵字段的问题列表（结构 + 元素 float 可转性）。"""
        issues = []
        if mat is None:
            issues.append(f"{field_name} is null")
            return issues
        if not isinstance(mat, list) or len(mat) != 4:
            issues.append(
                f"{field_name} shape invalid: {type(mat).__name__}, "
                f"len={len(mat) if isinstance(mat, list) else 'N/A'}"
            )
            return issues
        if not all(isinstance(row, list) and len(row) == 4 for row in mat):
            issues.append(f"{field_name} not 4x4")
            return issues
        # 逐元素 float 可转性校验（R32-B3）
        for i, row in enumerate(mat):
            for j, val in enumerate(row):
                try:
                    float(val)
                except (TypeError, ValueError):
                    issues.append(f"{field_name}[{i}][{j}] not float-convertible: {val!r}")
        return issues

    # 当 sun_visibility 需要 shadow reprojection 时，矩阵必须非空且有效
    if ocs_sun_vis in ["camera_visible_nol_plus_sun_shadow_pass", "camera_visible_nol_plus_python_raycast"]:
        for rec in ocs_manifest["records"]:
            issues = []
            issues += _matrix_issues("camera_matrix_world", rec.get("camera_matrix_world"))
            issues += _matrix_issues("sun_camera_matrix_world", rec.get("sun_camera_matrix_world"))

            if issues:
                invalid_matrix_records.append({
                    "record_id": rec["record_id"],
                    "issues": issues,
                })

    status = "PASS" if not invalid_matrix_records else "FAIL"
    if status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "invalid_matrix_records": invalid_matrix_records,
    })
    print(f"[{status}] {check_name}: {len(invalid_matrix_records)} invalid")

    # 检查 16: sun_visibility_mask_path 非空与存在（R31 §3.3 新增）
    check_name = "sun_visibility_mask_path_non_null_and_exists"
    missing_mask_records = []

    if ocs_sun_vis in ["camera_visible_nol_plus_sun_shadow_pass", "camera_visible_nol_plus_python_raycast"]:
        for rec in ocs_manifest["records"]:
            mask_path = rec.get("sun_visibility_mask_path")

            if mask_path is None:
                missing_mask_records.append({
                    "record_id": rec["record_id"],
                    "issue": "sun_visibility_mask_path is null",
                })
            else:
                issue = _path_structure_issue(mask_path, require_prefix)
                if issue:
                    missing_mask_records.append({
                        "record_id": rec["record_id"],
                        "issue": f"base_inconsistent: {issue}",
                    })
                elif not _resolve_under_root(data_root, mask_path).is_file():
                    missing_mask_records.append({
                        "record_id": rec["record_id"],
                        "issue": f"mask file not found: {_normalize_rel_path(mask_path)}",
                    })

    status = "PASS" if not missing_mask_records else "FAIL"
    if status == "FAIL":
        all_pass = False

    checks.append({
        "check": check_name,
        "status": status,
        "missing_mask_records": missing_mask_records,
    })
    print(f"[{status}] {check_name}: {len(missing_mask_records)} missing")

    # 检查 17: Records 完整性 gate（R31 §3.5 / R32-B4）
    # 期望数来源优先级：CLI --expected-record-count > manifest 顶层 n_total_expected。
    # 二者都没有时保持 INFO（gate 未启用），不影响 overall_status。
    check_name = "records_completeness"

    n_ocs = len(ocs_manifest["records"])
    n_img = len(image_manifest["records"])

    manifest_expected = ocs_manifest.get("n_total_expected")
    if expected_record_count is not None:
        n_expected = expected_record_count
        expected_source = "cli:--expected-record-count"
    elif manifest_expected is not None:
        n_expected = manifest_expected
        expected_source = "manifest:n_total_expected"
    else:
        n_expected = None
        expected_source = None

    gate_enabled = n_expected is not None

    if gate_enabled:
        if n_ocs < n_expected or n_img < n_expected:
            status = "NOT_COMPLETE"
            all_pass = False
        else:
            status = "PASS"
        note = "completeness gate 已启用：记录数不足期望值则 FAIL / NOT_COMPLETE。"
    else:
        status = "INFO"
        note = "completeness gate 未启用（未提供 --expected-record-count，manifest 也无 n_total_expected）。"

    checks.append({
        "check": check_name,
        "status": status,
        "gate_enabled": gate_enabled,
        "expected_source": expected_source,
        "n_total_expected": n_expected,
        "n_records_ocs": n_ocs,
        "n_records_image": n_img,
        "note": note,
    })
    print(f"[{status}] {check_name}: OCS={n_ocs}, Image={n_img}, expected={n_expected}, gate={gate_enabled}")

    # 总状态
    overall_status = "PASS" if all_pass else "NOT_COMPLETE"

    # 构建报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "task": "v0.4 manifest consistency check (17 checks)",
        "overall_status": overall_status,
        "ocs_manifest_path": ocs_manifest_path,
        "image_manifest_path": image_manifest_path,
        "step6_summary_path": step6_summary_path,
        "data_root": data_root,
        "data_root_resolved": data_root_resolved,
        "require_prefix": require_prefix,
        "expected_record_count": expected_record_count,
        "check_count": len(checks),
        "checks": checks,
        "依据文件": [
            "04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/14_v0.4数据与manifest字段规范_最终冻结版.md §8.1",
            "04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R31_Codex_审阅_1C-E14_Step7b条件通过并要求Step7c.md",
            "04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R32_Codex_审阅_1C-E15_Step7c未通过返工单.md",
        ],
    }

    # 写出
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 80)
    print(f"总状态: {overall_status}")
    print(f"检查项数: {len(checks)}")
    print(f"报告写出: {output_path}")
    print("=" * 80)

    return report


def main():
    parser = argparse.ArgumentParser(description="Check OCS/Image manifest consistency")
    parser.add_argument("--ocs-manifest", required=True, help="OCS manifest 路径")
    parser.add_argument("--image-manifest", required=True, help="Image manifest 路径")
    parser.add_argument("--step6-summary", required=True, help="Step 6 summary 路径")
    parser.add_argument("--output", required=True, help="输出报告路径")
    parser.add_argument(
        "--data-root", default=".",
        help="所有 manifest record 路径的解析根（默认当前工作目录 '.'）；不从 manifest 路径反推",
    )
    parser.add_argument(
        "--require-prefix", default=None,
        help="可选，当前数据布局约束要求的路径前缀（如 v0.4_results/）；留空则不做前缀约束",
    )
    parser.add_argument(
        "--expected-record-count", type=int, default=None,
        help="可选，启用 completeness gate 的期望记录数；不足则 FAIL / NOT_COMPLETE",
    )

    args = parser.parse_args()

    report = check_consistency(
        ocs_manifest_path=args.ocs_manifest,
        image_manifest_path=args.image_manifest,
        step6_summary_path=args.step6_summary,
        output_path=args.output,
        data_root=args.data_root,
        require_prefix=args.require_prefix,
        expected_record_count=args.expected_record_count,
    )

    # 返回状态码
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

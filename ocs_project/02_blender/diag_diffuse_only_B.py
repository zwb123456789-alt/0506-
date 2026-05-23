# -*- coding: utf-8 -*-
"""
diag_diffuse_only_B.py —— B 端 diffuse-only OCS
================================================
读单帧 EXR，用 rho_s=0 重算 OCS，与 A 端 diffuse-only 对比。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/02_blender/diag_diffuse_only_B.py
"""
import os, sys, json, time as time_module
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from brdf_postprocess import (
    read_multilayer_exr, compute_radiance_image, integrate_ocs,
    PART_PASS_INDEX,
)

EXR_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块B_渲染", "run_20260519_backface_fix",
    "yaw150.00_pitch-80.00_0001.exr",
))
META_PATH = os.path.join(os.path.dirname(EXR_PATH), "render_metadata.json")

# A 端 diffuse-only 结果（上一步）
A_DIFFUSE_NO_OCC = 0.076627

if __name__ == "__main__":
    print("=" * 60)
    print("  B 端 diffuse-only 验证 (rho_s=0)")
    print(f"  EXR: {EXR_PATH}")
    print("=" * 60)

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    res = meta["resolution"]
    r_max = meta["r_max"]
    ortho_scale = 2.2 * r_max
    pixel_area_m2 = (ortho_scale / res) ** 2
    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)
    materials_flat = meta["materials"]  # flat: {part: {rho_d, rho_s, n}}

    print(f"  r_max={r_max:.4f}m  ortho_scale={ortho_scale:.4f}m  "
          f"res={res}  pixel_area={pixel_area_m2:.6e} m²")

    layers = read_multilayer_exr(EXR_PATH)
    H, W = layers["_size"]
    print(f"  EXR: {H}×{W}")

    # ---- B 含镜面 ----
    print("\n--- B 含镜面 (flat materials from metadata) ---")
    r_full, mask_full, pp_full = compute_radiance_image(
        layers, sun_dir, det_dir, materials_flat, PART_PASS_INDEX)
    ocs_full = integrate_ocs(r_full, pixel_area_m2)
    print(f"  OCS_image = {ocs_full:.6f}")
    for pn, cnt in pp_full.items():
        print(f"    [{pn:15s}] pixels={cnt}")

    # ---- B diffuse-only ----
    print("\n--- B diffuse-only (rho_s=0) ---")
    mat_diff = {}
    for name, m in materials_flat.items():
        mat_diff[name] = {**m, "rho_s": 0.0}

    r_diff, mask_diff, pp_diff = compute_radiance_image(
        layers, sun_dir, det_dir, mat_diff, PART_PASS_INDEX)
    ocs_diff = integrate_ocs(r_diff, pixel_area_m2)
    print(f"  OCS_image_diffuse = {ocs_diff:.6f}")
    for pn, cnt in pp_diff.items():
        print(f"    [{pn:15s}] pixels={cnt}")

    # ---- 对比 ----
    print(f"\n{'='*60}")
    print(f"  Diffuse-only 验证总结 (yaw=150/pitch=-80)")
    print(f"  {'':30s} {'OCS':>12s}")
    print(f"  {'B (含镜面)':30s} {ocs_full:12.6f}")
    print(f"  {'B (diffuse-only)':30s} {ocs_diff:12.6f}")
    print(f"  {'A_full (diffuse-only)':30s} {A_DIFFUSE_NO_OCC:12.6f}")
    if ocs_diff > 0:
        print(f"  {'A/B diffuse ratio':30s} {A_DIFFUSE_NO_OCC/ocs_diff:12.2%}")
    print(f"  {'B specular contrib':30s} {ocs_full - ocs_diff:12.6f} ({(ocs_full-ocs_diff)/ocs_full*100:.1f}%)" if ocs_full > 0 else "")
    print("=" * 60)

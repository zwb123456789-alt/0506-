# -*- coding: utf-8 -*-
"""
diag_per_part_reconcile.py —— diffuse-only per-part 对账
=========================================================
逐部件对比 A_full diffuse-only vs B diffuse-only OCS，
同时输出几何面积、NoL·NoV 均值等中间量。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/02_blender/diag_per_part_reconcile.py
"""
import os, sys, json, time as time_module
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from config import SUN_VECTOR, DET_VECTOR, UNIT_SCALE, RAY_BATCH
from geometry import load_meshes, euler_to_matrix
from ocs_core import compute_single_attitude
from occlusion import RayForest
import materials as materials_mod
from brdf_postprocess import (
    read_multilayer_exr, compute_radiance_image, integrate_ocs,
    PART_PASS_INDEX,
)

YAW, PITCH = 150.0, -80.0
EXR_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块B_渲染", "run_20260519_backface_fix",
    "yaw150.00_pitch-80.00_0001.exr",
))
META_PATH = os.path.join(os.path.dirname(EXR_PATH), "render_metadata.json")


def run_A_diffuse_per_part():
    """A 端 full 精度 diffuse-only，返回 per-part 详细数据"""
    orig_get = materials_mod.get_material
    def diffuse_get(name):
        mat = orig_get(name).copy()
        mat["rho_s"] = 0.0
        return mat
    materials_mod.get_material = diffuse_get

    try:
        sun_norm = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
        det_norm = DET_VECTOR / np.linalg.norm(DET_VECTOR)
        meshes, total_faces = load_meshes(accuracy_level="full", verbose=False)
        R = euler_to_matrix(yaw=YAW, pitch=PITCH, roll=0.0, degrees=True)
        ray_forest = RayForest(meshes, batch_size=RAY_BATCH)
        result = compute_single_attitude(meshes, ray_forest, sun_norm, det_norm, R)
        return result, sun_norm, det_norm, meshes
    finally:
        materials_mod.get_material = orig_get


def run_B_diffuse_per_part():
    """B 端 diffuse-only，返回 per-part 详细数据"""
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
    materials_flat = meta["materials"]

    layers = read_multilayer_exr(EXR_PATH)

    # diffuse-only materials
    mat_diff = {name: {**m, "rho_s": 0.0} for name, m in materials_flat.items()}

    rad, mask_obj, pp = compute_radiance_image(
        layers, sun_dir, det_dir, mat_diff, PART_PASS_INDEX)
    ocs_total = integrate_ocs(rad, pixel_area_m2)

    # Per-part OCS
    idx = layers["IndexOB"].astype(np.int32)
    part_ocs = {}
    for pn, pid in PART_PASS_INDEX.items():
        m = mask_obj & (idx == pid)
        if m.any():
            part_ocs[pn] = float(np.sum(rad[m]) * pixel_area_m2)
        else:
            part_ocs[pn] = 0.0

    return {
        "ocs_total": ocs_total,
        "part_ocs": part_ocs,
        "part_pixels": pp,
        "pixel_area_m2": pixel_area_m2,
        "ortho_scale": ortho_scale,
        "r_max": r_max,
        "res": res,
        "sun_dir": sun_dir,
        "det_dir": det_dir,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("  Diffuse-only per-part 对账 (yaw=150/pitch=-80)")
    print("=" * 70)

    # ---- A 端 ----
    print("\n--- A 端 diffuse-only ---")
    res_A, sun_A, det_A, meshes_A = run_A_diffuse_per_part()
    print(f"  OCS_no_occ  = {res_A['ocs_no_occ']:.6f}")
    print(f"  OCS_with_occ= {res_A['ocs_with_occ']:.6f}")
    print(f"  occ_ratio   = {res_A['occlusion_ratio']:.2%}")
    for pn, pc in res_A["part_contrib"].items():
        m = meshes_A[pn]
        total_area_mm2 = float(m.area_faces.sum()) if hasattr(m, 'area_faces') else float(m.area)
        # Per-face visible area in m²
        print(f"    [{pn:15s}] OCS_no={pc['ocs_no_occ']:.6f}  "
              f"OCS_with={pc['ocs_with_occ']:.6f}  "
              f"faces_no={pc['visible_faces_no_occ']:,}  "
              f"faces_with={pc['visible_faces_with_occ']:,}  "
              f"geom_area={total_area_mm2*1e-6:.3f}m²")

    # ---- B 端 ----
    print("\n--- B 端 diffuse-only ---")
    res_B = run_B_diffuse_per_part()
    print(f"  pixel_area  = {res_B['pixel_area_m2']:.6e} m²")
    print(f"  ortho_scale = {res_B['ortho_scale']:.4f} m")
    print(f"  r_max       = {res_B['r_max']:.4f} m")
    print(f"  OCS_total   = {res_B['ocs_total']:.6f}")
    for pn, ocs in res_B['part_ocs'].items():
        print(f"    [{pn:15s}] OCS={ocs:.6f}  pixels={res_B['part_pixels'][pn]}")

    # ---- 逐部件对比 ----
    print(f"\n{'='*70}")
    print(f"  逐部件对账 (diffuse-only with_occ)")
    print(f"  {'Part':15s} {'A_OCS':>10s} {'B_OCS':>10s} {'A/B':>8s}  "
          f"{'A_faces':>8s} {'B_pix':>7s}")
    print(f"  {'-'*65}")
    for pn in ["jinshuzhuti", "taiyangnengban", "yinshenban"]:
        a_ocs = res_A["part_contrib"][pn]["ocs_with_occ"]
        b_ocs = res_B["part_ocs"].get(pn, 0)
        ratio = a_ocs / b_ocs if b_ocs > 0 else float("inf")
        a_faces = res_A["part_contrib"][pn]["visible_faces_with_occ"]
        b_pix = res_B["part_pixels"].get(pn, 0)
        print(f"  {pn:15s} {a_ocs:10.6f} {b_ocs:10.6f} {ratio:8.2%}  "
              f"{a_faces:8,} {b_pix:7,}")

    # ---- 核查基础参数 ----
    print(f"\n{'='*70}")
    print(f"  基础参数核查")
    print(f"  A sun_dir: {sun_A}")
    print(f"  B sun_dir: {res_B['sun_dir']}")
    print(f"  A det_dir: {det_A}")
    print(f"  B det_dir: {res_B['det_dir']}")
    print(f"  sun cos dist: {np.dot(sun_A, res_B['sun_dir']):.10f}")
    print(f"  det cos dist: {np.dot(det_A, res_B['det_dir']):.10f}")

    # UNIT_SCALE check
    print(f"\n  A UNIT_SCALE = {UNIT_SCALE} (scale_sq = {UNIT_SCALE**2:.1e})")
    print(f"  B pixel_area = {res_B['pixel_area_m2']:.6e} m²")
    total_B_pix_area = sum(res_B['part_pixels'].values()) * res_B['pixel_area_m2']
    print(f"  B total pixel projected area = {total_B_pix_area:.4f} m²")

    # A visible geometric area estimate (with_occ faces)
    a_visible_area_m2 = 0
    for pn in ["jinshuzhuti", "taiyangnengban", "yinshenban"]:
        m = meshes_A[pn]
        # We can't easily get which specific faces are visible_with_occ,
        # but we can estimate from the OCS formula
        rho_d = materials_mod.MATERIAL_DB[pn]["simple"]["rho_d"]
        f_r_diff = rho_d / np.pi
        # OCS = area * f_r * avg(NoL*NoV) for visible faces
        # This is approximate
        pass
    print(f"  (需要深入 per-face 数据才能算可见面积)")

    print("=" * 70)

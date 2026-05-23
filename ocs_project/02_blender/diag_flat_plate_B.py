# -*- coding: utf-8 -*-
"""
diag_flat_plate_B.py —— B 端平板 OCS 验证
===========================================
读 Blender 渲染的平板 EXR，计算 OCS_image，与解析解和 A 端对比。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/02_blender/diag_flat_plate_B.py
"""
import os, sys, json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from brdf_postprocess import (
    read_multilayer_exr, compute_radiance_image, integrate_ocs,
    PART_PASS_INDEX,
)
from brdf_models import eval_legacy_phong
from geometry import euler_to_matrix

# EXR 路径
EXR_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块B_渲染", "flat_plate_yaw000.00_pitch+00.00"))
EXR_PATH = os.path.join(EXR_DIR, "flat_plate_0001.exr")
META_PATH = os.path.join(EXR_DIR, "render_metadata.json")

# A 端解析值
YAW, PITCH = 0.0, 0.0
SUN_VEC = np.array([1.0, 0.0, 0.3])
DET_VEC = np.array([0.5, -1.0, 0.1])
MAT = {"rho_d": 0.20, "rho_s": 0.60, "n": 80, "brdf_model": "legacy_phong"}

def analytical_ocs(yaw, pitch, rho_d, rho_s, n, area_m2=1.0):
    sun_norm = SUN_VEC / np.linalg.norm(SUN_VEC)
    det_norm = DET_VEC / np.linalg.norm(DET_VEC)
    R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
    N_body = np.array([0.0, 0.0, 1.0])
    N = N_body @ R
    NoL = float(np.dot(N, sun_norm))
    NoV = float(np.dot(N, det_norm))
    if NoL <= 0 or NoV <= 0:
        return 0.0, NoL, NoV, 0.0
    f_r = float(eval_legacy_phong(N, sun_norm, det_norm, rho_d, rho_s, n))
    return area_m2 * f_r * NoL * NoV, NoL, NoV, f_r


if __name__ == "__main__":
    print("=" * 60)
    print("  单平板三端闭合验证 (yaw=0/pitch=0)")
    print("=" * 60)

    # ---- 解析解 ----
    ocs_analyt, NoL_a, NoV_a, f_r_a = analytical_ocs(
        YAW, PITCH, MAT["rho_d"], MAT["rho_s"], MAT["n"])
    print(f"\n  解析解: OCS={ocs_analyt:.6f}  NoL={NoL_a:.4f}  "
          f"NoV={NoV_a:.4f}  f_r={f_r_a:.4f}")

    # ---- B 端 ----
    with open(META_PATH, "r") as f:
        meta = json.load(f)

    res = meta["resolution"]
    ortho_scale = meta["ortho_scale"]
    r_max = meta["r_max"]
    pixel_area_m2 = (ortho_scale / res) ** 2
    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)
    mat_B = meta["materials"]["flat_plate"]

    print(f"\n  B 端参数: r_max={r_max:.4f}m  ortho_scale={ortho_scale:.4f}m  "
          f"res={res}  pixel_area={pixel_area_m2:.6e} m²")

    layers = read_multilayer_exr(EXR_PATH)
    H, W = layers["_size"]
    print(f"  EXR: {H}×{W}")

    # IndexOB mapping - flat plate is IndexOB=1
    flat_materials = {"flat_plate": mat_B}
    flat_pass_index = {"flat_plate": 1}

    rad, mask_obj, pp = compute_radiance_image(
        layers, sun_dir, det_dir, flat_materials, flat_pass_index)
    ocs_B = integrate_ocs(rad, pixel_area_m2)

    # Per-part breakdown
    idx = layers["IndexOB"].astype(np.int32)
    m_plate = mask_obj & (idx == 1)
    n_pix = m_plate.sum()
    N_pix = layers["Normal"].astype(np.float64)[m_plate]
    nn = np.linalg.norm(N_pix, axis=-1, keepdims=True)
    N_pix = N_pix / np.where(nn > 1e-8, nn, 1.0)
    NoL_pix = np.clip(np.einsum("ij,j->i", N_pix, sun_dir), 0, None)
    NoV_pix = np.clip(np.einsum("ij,j->i", N_pix, det_dir), 0, None)
    H_vec = sun_dir + det_dir
    H_vec /= np.linalg.norm(H_vec)
    NoH_pix = np.clip(np.einsum("ij,j->i", N_pix, H_vec), 0, None)
    f_r_pix = np.array([float(eval_legacy_phong(n, sun_dir, det_dir,
                                                mat_B["rho_d"], mat_B["rho_s"], mat_B["n"]))
                        for n in N_pix])

    print(f"\n  B 端: OCS_image={ocs_B:.6f}  物体像素={n_pix}")
    print(f"    NoL: mean={NoL_pix.mean():.4f}  median={np.median(NoL_pix):.4f}")
    print(f"    NoV: mean={NoV_pix.mean():.4f}  median={np.median(NoV_pix):.4f}")
    print(f"    f_r: mean={f_r_pix.mean():.4f}  median={np.median(f_r_pix):.4f}")
    print(f"    NoH: mean={NoH_pix.mean():.4f}  max={NoH_pix.max():.4f}")
    print(f"    法线均值: [{N_pix[:,0].mean():+.4f} {N_pix[:,1].mean():+.4f} {N_pix[:,2].mean():+.4f}]")
    print(f"    NoL>0 像素: {(NoL_pix>0).sum()}/{n_pix}")

    # 用 B 端实际 NoL/NoV/f_r 均值反推有效面积
    eff_area_from_B = ocs_B / (f_r_pix.mean() * NoL_pix[NoL_pix>0].mean() * NoV_pix.mean()) if n_pix > 0 else 0
    print(f"    B有效面积反推: {eff_area_from_B:.4f} m²")

    # ---- 三端对比 ----
    print(f"\n{'='*60}")
    print(f"  三端对比")
    print(f"  {'':20s} {'OCS':>10s} {'vs解析':>10s}")
    print(f"  {'解析解':20s} {ocs_analyt:10.6f}")
    print(f"  {'A端 (trimesh)':20s} {0.001630:10.6f} {'0.00%':>10s}")
    print(f"  {'B端 (Blender+PP)':20s} {ocs_B:10.6f} {abs(ocs_B-ocs_analyt)/max(ocs_analyt,1e-30)*100:9.2f}%")
    print("=" * 60)

# -*- coding: utf-8 -*-
"""
run_material_sweep.py —— 单平板材料 sweep 三端闭合验证
=========================================================
复用已有 EXR（几何缓冲与材质无关），分别验证 jinshuzhuti / taiyangnengban /
yinshenban 三种材料在 5 个姿态上的三端闭合。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/06_brdf_validation/run_material_sweep.py
"""
import os, sys, json, time as time_module
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新")
PYTHON_EXE = r"C:\Users\97466\.conda\envs\ocs_sim\python.exe"

sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/01_code"))
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/07_brdf"))
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/02_blender"))

from config import SUN_VECTOR, DET_VECTOR
from geometry import euler_to_matrix, load_meshes
from brdf_models import eval_legacy_phong
from brdf_postprocess import read_multilayer_exr, compute_radiance_image, integrate_ocs, PART_PASS_INDEX
import materials as materials_mod

# ---- 材料定义 ----
MATERIALS = {
    "jinshuzhuti":    {"rho_d": 0.20, "rho_s": 0.60, "n": 80, "brdf_model": "legacy_phong"},
    "taiyangnengban": {"rho_d": 0.15, "rho_s": 0.10, "n": 20, "brdf_model": "legacy_phong"},
    "yinshenban":     {"rho_d": 0.08, "rho_s": 0.02, "n": 10, "brdf_model": "legacy_phong"},
}

ATTITUDES = [
    (0.0, 0.0), (0.0, -30.0), (90.0, -45.0), (150.0, -80.0), (180.0, 0.0),
]
EXR_DIR = PROJECT_ROOT / "结果/BRDF验证/plane_batch_20260519_204323"
STL_PATH = PROJECT_ROOT / "建模/flat_plate_1m2.stl"
SUN_VEC = np.array(SUN_VECTOR, dtype=np.float64)
DET_VEC = np.array(DET_VECTOR, dtype=np.float64)
SUN_N = SUN_VEC / np.linalg.norm(SUN_VEC)
DET_N = DET_VEC / np.linalg.norm(DET_VEC)


def analytical_ocs(yaw, pitch, mat):
    """解析解（已修复 R @ N_body）"""
    R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
    N_body = np.array([0.0, 0.0, 1.0])
    N = R @ N_body
    NoL = float(np.dot(N, SUN_N))
    NoV = float(np.dot(N, DET_N))
    if NoL <= 0 or NoV <= 0:
        return 0.0, NoL, NoV, 0.0
    f_r = float(eval_legacy_phong(N, SUN_N, DET_N, mat["rho_d"], mat["rho_s"], mat["n"]))
    return 1.0 * f_r * NoL * NoV, NoL, NoV, f_r


def a_side_ocs(yaw, pitch, mat):
    """A 端 trimesh 逐面元 OCS"""
    orig_get = materials_mod.get_material
    def plate_get(name):
        if name == "flat_plate":
            return mat.copy()
        return orig_get(name)
    materials_mod.get_material = plate_get
    try:
        part_files = {"flat_plate": str(STL_PATH)}
        meshes, _ = load_meshes(part_files=part_files, accuracy_level="full", verbose=False)
        R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
        mesh = meshes["flat_plate"]
        if hasattr(mesh, 'face_normals'):
            normals = np.array(mesh.face_normals, dtype=np.float64)
        else:
            v = np.array(mesh.vertices); f = np.array(mesh.faces)
            e1 = v[f[:,1]] - v[f[:,0]]; e2 = v[f[:,2]] - v[f[:,0]]
            normals = np.cross(e1, e2)
            nn = np.linalg.norm(normals, axis=1, keepdims=True)
            normals = normals / np.where(nn > 1e-12, nn, 1.0)
        N = normals @ R.T
        nn = np.linalg.norm(N, axis=1, keepdims=True)
        N = N / np.where(nn > 1e-12, nn, 1.0)
        if hasattr(mesh, 'area_faces'):
            area_m2 = np.array(mesh.area_faces, dtype=np.float64) * 1e-6
        else:
            area_m2 = np.full(len(N), 2.0 / len(N), dtype=np.float64)
        L_bc = np.broadcast_to(SUN_N, N.shape).copy()
        V_bc = np.broadcast_to(DET_N, N.shape).copy()
        f_r = eval_legacy_phong(N, L_bc, V_bc, mat["rho_d"], mat["rho_s"], mat["n"])
        NoL = np.maximum(np.einsum("ij,j->i", N, SUN_N), 0.0)
        NoV = np.maximum(np.einsum("ij,j->i", N, DET_N), 0.0)
        visible = (NoL > 0) & (NoV > 0)
        return float(np.sum(area_m2[visible] * f_r[visible] * NoL[visible] * NoV[visible]))
    finally:
        materials_mod.get_material = orig_get


def b_side_ocs(exr_path, meta, mat_full, mat_diffuse):
    """B 端 EXR 后处理"""
    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)
    r_max = meta["r_max"]; res = meta["resolution"]
    ortho_scale = 2.2 * r_max; pixel_area = (ortho_scale / res) ** 2
    layers = read_multilayer_exr(str(exr_path))
    flat_mats = {"flat_plate": mat_full}
    flat_pass = {"flat_plate": 1}
    rad_full, _, _ = compute_radiance_image(layers, sun_dir, det_dir, flat_mats, flat_pass)
    ocs_full = integrate_ocs(rad_full, pixel_area)
    rad_diff, _, _ = compute_radiance_image(
        layers, sun_dir, det_dir, {"flat_plate": mat_diffuse}, flat_pass)
    ocs_diff = integrate_ocs(rad_diff, pixel_area)
    return ocs_full, ocs_diff


def main():
    print("=" * 70)
    print("  单平板材料 Sweep：三端闭合验证")
    print("=" * 70)
    meta_path = EXR_DIR / "render_metadata.json"
    with open(meta_path, "r") as f:
        meta = json.load(f)

    rows = []
    for mat_name, mat in MATERIALS.items():
        mat_diff = {**mat, "rho_s": 0.0}
        print(f"\n{'='*70}")
        print(f"  材料: {mat_name}  rho_d={mat['rho_d']}  rho_s={mat['rho_s']}  n={mat['n']}")
        print(f"{'yaw':>6s} {'pitch':>7s} {'analyt':>12s} {'A_full':>12s} {'B_full':>12s} "
              f"{'rel_A%':>8s} {'rel_B%':>8s} {'analyt_d':>12s} {'A_d':>12s} {'B_d':>12s} "
              f"{'rel_Ad%':>8s} {'rel_Bd%':>8s}")
        print("-" * 120)

        for yaw, pitch in ATTITUDES:
            exr_path = EXR_DIR / f"yaw{yaw:06.2f}_pitch{pitch:+06.2f}_0001.exr"
            ocs_an_full, NoL, NoV, f_r = analytical_ocs(yaw, pitch, mat)
            ocs_an_diff, _, _, _ = analytical_ocs(yaw, pitch, mat_diff)
            ocs_a_full = a_side_ocs(yaw, pitch, mat)
            ocs_a_diff = a_side_ocs(yaw, pitch, mat_diff)
            ocs_b_full, ocs_b_diff = b_side_ocs(exr_path, meta, mat, mat_diff)

            def rel(v, ref):
                d = max(abs(ref), 1e-30)
                return abs(v - ref) / d if d > 1e-30 else float("nan")

            ra = rel(ocs_a_full, ocs_an_full) if ocs_an_full > 0 else float("nan")
            rb = rel(ocs_b_full, ocs_an_full) if ocs_an_full > 0 else float("nan")
            rad = rel(ocs_a_diff, ocs_an_diff) if ocs_an_diff > 0 else float("nan")
            rbd = rel(ocs_b_diff, ocs_an_diff) if ocs_an_diff > 0 else float("nan")

            print(f"{yaw:6.0f} {pitch:+7.0f} {ocs_an_full:12.6e} {ocs_a_full:12.6e} {ocs_b_full:12.6e} "
                  f"{ra*100:7.3f}% {rb*100:7.3f}% {ocs_an_diff:12.6e} {ocs_a_diff:12.6e} {ocs_b_diff:12.6e} "
                  f"{rad*100:7.3f}% {rbd*100:7.3f}%")

            rows.append({
                "material": mat_name, "yaw": yaw, "pitch": pitch,
                "ocs_analyt_full": ocs_an_full, "ocs_A_full": ocs_a_full, "ocs_B_full": ocs_b_full,
                "rel_A_full": ra, "rel_B_full": rb,
                "ocs_analyt_diff": ocs_an_diff, "ocs_A_diff": ocs_a_diff, "ocs_B_diff": ocs_b_diff,
                "rel_A_diff": rad, "rel_B_diff": rbd,
                "NoL": NoL, "NoV": NoV, "f_r": f_r,
            })

    # 汇总
    print(f"\n{'='*70}")
    print("  汇总")
    for mat_name in MATERIALS:
        mr = [r for r in rows if r["material"] == mat_name]
        valid_full = [r["rel_B_full"] for r in mr if r["ocs_analyt_full"] > 0]
        valid_diff = [r["rel_B_diff"] for r in mr if r["ocs_analyt_diff"] > 0]
        if valid_full:
            print(f"  {mat_name:15s}  Full: mean_rel={np.mean(valid_full)*100:.3f}%  "
                  f"max={np.max(valid_full)*100:.3f}%  "
                  f"Diffuse: mean_rel={np.mean(valid_diff)*100:.3f}%  max={np.max(valid_diff)*100:.3f}%")
        else:
            print(f"  {mat_name:15s}  (无有效 NoL>0 姿态)")

    # CSV
    out_dir = PROJECT_ROOT / "结果/BRDF验证" / f"material_sweep_{time_module.strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "material_sweep.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n  CSV: {csv_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

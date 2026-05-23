# -*- coding: utf-8 -*-
"""
flat_plate_closure.py —— 单平板解析闭合验证
=============================================
1m×1m 平板，LegacyPhong BRDF，无遮挡、无自交。
对比：解析解 vs A 端 OCS，多 yaw/pitch 角度。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/02_blender/flat_plate_closure.py
"""
import os, sys, json, tempfile, time as time_module
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from config import SUN_VECTOR, DET_VECTOR, UNIT_SCALE
from geometry import load_meshes, euler_to_matrix
from ocs_core import compute_single_attitude
from occlusion import RayForest
from brdf_models import eval_legacy_phong
import materials as materials_mod

# ---- 建 1m×1m 平板 STL (mm 单位: 1000×1000 mm²) ----
def make_flat_plate_stl():
    """返回临时 STL 文件路径（1m×1m 正方形，法线 +Z）"""
    # ASCII STL: 2 triangles, 1000mm×1000mm in XY plane
    stl_content = """solid flat_plate_1m2
facet normal 0 0 1
  outer loop
    vertex 0 0 0
    vertex 1000 0 0
    vertex 0 1000 0
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex 1000 0 0
    vertex 1000 1000 0
    vertex 0 1000 0
  endloop
endfacet
endsolid flat_plate_1m2
"""
    tmp = tempfile.NamedTemporaryFile(suffix=".stl", delete=False, mode="w", encoding="ascii")
    tmp.write(stl_content)
    tmp.close()
    return tmp.name


def analytical_ocs(yaw, pitch, sun_dir, det_dir, rho_d, rho_s, n, area_m2=1.0):
    """单平板解析 OCS（假设平板法线本体系 +Z）"""
    sun_norm = sun_dir / np.linalg.norm(sun_dir)
    det_norm = det_dir / np.linalg.norm(det_dir)

    R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
    # 本体系法线 [0,0,1] 旋转到惯性系
    N_body = np.array([0.0, 0.0, 1.0])
    N = N_body @ R  # = R[:, 2] (第三列)

    NoL = float(np.dot(N, sun_norm))
    NoV = float(np.dot(N, det_norm))

    if NoL <= 0 or NoV <= 0:
        return 0.0, {"NoL": NoL, "NoV": NoV, "f_r": 0.0}

    f_r = float(eval_legacy_phong(N, sun_norm, det_norm, rho_d, rho_s, n))
    ocs = area_m2 * f_r * NoL * NoV
    return ocs, {"NoL": NoL, "NoV": NoV, "f_r": f_r, "N": N.tolist()}


if __name__ == "__main__":
    print("=" * 70)
    print("  单平板闭合验证: 1m×1m LegacyPhong")
    print("=" * 70)

    sun_norm = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
    det_norm = DET_VECTOR / np.linalg.norm(DET_VECTOR)
    print(f"  sun: {sun_norm}")
    print(f"  det: {det_norm}")

    # 用 jinshuzhuti 材料 (n=80, rho_d=0.2, rho_s=0.6)
    mat = {"rho_d": 0.20, "rho_s": 0.60, "n": 80, "brdf_model": "legacy_phong"}
    print(f"  材料: rho_d={mat['rho_d']}, rho_s={mat['rho_s']}, n={mat['n']}")

    # 建平板 STL
    stl_path = make_flat_plate_stl()
    part_files = {"flat_plate": stl_path}

    # 测试角度
    test_angles = [
        (0, 0),      # 平板正对相机（接近）
        (0, -30),    # 俯仰
        (45, 0),     # 偏航
        (90, -45),   # 混合
        (150, -80),  # 复现问题姿态
        (180, 0),    # 背对太阳
    ]

    print(f"\n{'yaw':>6s} {'pitch':>7s} {'analyt':>10s} {'A_OCS':>10s} "
          f"{'rel_err':>8s} {'NoL':>8s} {'NoV':>8s} {'f_r':>10s}")
    print("-" * 70)

    errors = []
    # monkey-patch: "flat_plate" → jinshuzhuti 材料
    orig_get = materials_mod.get_material
    def plate_get(name):
        if name == "flat_plate":
            return {"brdf_model": "legacy_phong", "rho_d": 0.20, "rho_s": 0.60, "n": 80}
        return orig_get(name)
    materials_mod.get_material = plate_get

    try:
        for yaw, pitch in test_angles:
            # 解析解
            ocs_a, info = analytical_ocs(yaw, pitch, SUN_VECTOR, DET_VECTOR,
                                         mat["rho_d"], mat["rho_s"], mat["n"])
            # A 端
            meshes, _ = load_meshes(part_files=part_files, accuracy_level="full", verbose=False)
            R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
            rf = RayForest(meshes, batch_size=10)
            result = compute_single_attitude(meshes, rf, sun_norm, det_norm, R)

            a_ocs = result["ocs_no_occ"]
            # rel_err: relative to max of the two, handles zero case
            denom = max(abs(ocs_a), abs(a_ocs), 1e-30)
            rel_err = abs(ocs_a - a_ocs) / denom if denom > 1e-30 else 0

            print(f"{yaw:6.1f} {pitch:7.1f} {ocs_a:10.6f} {a_ocs:10.6f} "
                  f"{rel_err:8.2%} {info.get('NoL', 0):8.4f} {info.get('NoV', 0):8.4f} "
                  f"{info.get('f_r', 0):10.4f}")

            if ocs_a > 0 or a_ocs > 0:
                errors.append(rel_err)
    finally:
        materials_mod.get_material = orig_get

    # 清理
    try:
        os.unlink(stl_path)
    except OSError:
        pass

    print("-" * 70)
    if errors:
        print(f"  rel_err mean={np.mean(errors):.2%}  max={np.max(errors):.2%}  "
              f"min={np.min(errors):.2%}")
    else:
        print("  (所有姿态 OCS 均为 0)")
    print("=" * 70)

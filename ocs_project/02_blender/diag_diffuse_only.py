# -*- coding: utf-8 -*-
"""
diag_diffuse_only.py —— diffuse-only 验证 (A端)
================================================
临时设 rho_s=0 关闭镜面项，隔离采样差异。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/02_blender/diag_diffuse_only.py
"""
import os, sys, json, time as time_module
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from config import SUN_VECTOR, DET_VECTOR, UNIT_SCALE, RAY_BATCH, OUTPUT_DIR
from geometry import load_meshes, euler_to_matrix
from ocs_core import compute_single_attitude
from occlusion import RayForest
import materials

YAW, PITCH = 150.0, -80.0

def run_A_diffuse_only():
    """A 端 full 精度，monkey-patch get_material 返回 rho_s=0"""
    orig_get = materials.get_material
    def diffuse_get(name):
        mat = orig_get(name).copy()
        mat["rho_s"] = 0.0
        return mat
    materials.get_material = diffuse_get

    try:
        t0 = time_module.time()
        sun_norm = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
        det_norm = DET_VECTOR / np.linalg.norm(DET_VECTOR)

        meshes, total_faces = load_meshes(accuracy_level="full", verbose=True)
        R = euler_to_matrix(yaw=YAW, pitch=PITCH, roll=0.0, degrees=True)
        ray_forest = RayForest(meshes, batch_size=RAY_BATCH)
        result = compute_single_attitude(meshes, ray_forest, sun_norm, det_norm, R)
        elapsed = time_module.time() - t0

        print(f"\n  [A_full_diffuse] OCS_no_occ={result['ocs_no_occ']:.6f}  "
              f"OCS_with_occ={result['ocs_with_occ']:.6f}  "
              f"occ_ratio={result['occlusion_ratio']:.2%}  "
              f"耗时={elapsed:.1f}s")
        for pn, pc in result["part_contrib"].items():
            print(f"    [{pn:15s}] OCS_no={pc['ocs_no_occ']:.6f}  "
                  f"OCS_with={pc['ocs_with_occ']:.6f}")
        return result
    finally:
        materials.get_material = orig_get


if __name__ == "__main__":
    print("=" * 60)
    print("  Diffuse-only 验证 (A端, rho_s=0)")
    print(f"  目标姿态: yaw={YAW}°  pitch={PITCH}°")
    print("=" * 60)

    res_A = run_A_diffuse_only()

    # 对比上次 A_full 含镜面结果
    A_FULL_WITH_SPEC = 0.076627  # 上次 full run 的 OCS_no_occ
    B_EXACT = 0.171

    print(f"\n{'='*60}")
    print(f"  对比总结")
    print(f"  {'':30s} {'OCS_no_occ':>12s} {'vs B(0.171)':>12s}")
    print(f"  {'A_full (含镜面)':30s} {A_FULL_WITH_SPEC:12.6f} {A_FULL_WITH_SPEC/B_EXACT:12.2%}")
    print(f"  {'A_full (diffuse-only)':30s} {res_A['ocs_no_occ']:12.6f} {res_A['ocs_no_occ']/B_EXACT:12.2%}")
    spec_contrib = A_FULL_WITH_SPEC - res_A['ocs_no_occ']
    print(f"  {'  其中镜面贡献':30s} {spec_contrib:12.6f}")
    print(f"  {'B_exact (含镜面 ref)':30s} {B_EXACT:12.6f}")
    print("=" * 60)

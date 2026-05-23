# -*- coding: utf-8 -*-
"""
diag_geometry_accuracy.py —— 几何精度假说诊断
==============================================
单帧 yaw=150°/pitch=-80°，A 端 full 精度 vs fast 精度对比，
验证网格简化是否为 A/B OCS 差异根因。

用法:
    conda activate ocs_sim
    python ocs_project/02_blender/diag_geometry_accuracy.py
"""
import os, sys, json, time as time_module
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from config import SUN_VECTOR, DET_VECTOR, UNIT_SCALE, RAY_BATCH, OUTPUT_DIR
from geometry import load_meshes, euler_to_matrix
from ocs_core import compute_single_attitude
from occlusion import RayForest

YAW, PITCH = 150.0, -80.0
B_OCS_IMAGE = 0.171  # B 端 exact BRDF 后处理结果（CLAUDE.md 记录）

def run_one(accuracy_level, label):
    t0 = time_module.time()
    sun_norm = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
    det_norm = DET_VECTOR / np.linalg.norm(DET_VECTOR)

    meshes, total_faces = load_meshes(accuracy_level=accuracy_level, verbose=True)
    R = euler_to_matrix(yaw=YAW, pitch=PITCH, roll=0.0, degrees=True)
    ray_forest = RayForest(meshes, batch_size=RAY_BATCH)

    result = compute_single_attitude(meshes, ray_forest, sun_norm, det_norm, R)
    elapsed = time_module.time() - t0

    print(f"\n{'='*60}")
    print(f"  [{label}] yaw={YAW}°  pitch={PITCH}°  (accuracy={accuracy_level})")
    print(f"  总面元: {total_faces:,}  耗时: {elapsed:.1f}s")
    print(f"  OCS_no_occ:    {result['ocs_no_occ']:.6f}")
    print(f"  OCS_with_occ:  {result['ocs_with_occ']:.6f}")
    print(f"  occlusion_ratio: {result['occlusion_ratio']:.2%}")
    print(f"  可见面(无遮挡): {result['visible_faces_no_occ']:,}")
    print(f"  可见面(有遮挡): {result['visible_faces_with_occ']:,}")
    print(f"\n  逐部件:")
    for pn, pc in result["part_contrib"].items():
        print(f"    [{pn:15s}] OCS_no={pc['ocs_no_occ']:.6f}  "
              f"OCS_with={pc['ocs_with_occ']:.6f}  "
              f"faces_no={pc['visible_faces_no_occ']:,}  "
              f"faces_with={pc['visible_faces_with_occ']:,}")

    return {
        "label": label,
        "accuracy": accuracy_level,
        "yaw": YAW, "pitch": PITCH,
        "total_faces": total_faces,
        "elapsed_s": round(elapsed, 2),
        "ocs_no_occ": result["ocs_no_occ"],
        "ocs_with_occ": result["ocs_with_occ"],
        "occlusion_ratio": result["occlusion_ratio"],
        "visible_faces_no_occ": result["visible_faces_no_occ"],
        "visible_faces_with_occ": result["visible_faces_with_occ"],
        "part_contrib": {
            pn: {k: v for k, v in pc.items()}
            for pn, pc in result["part_contrib"].items()
        },
    }

if __name__ == "__main__":
    print("=" * 60)
    print("  几何精度假说诊断: A_fast vs A_full vs B_exact")
    print(f"  目标姿态: yaw={YAW}°  pitch={PITCH}°")
    print(f"  B 端 OCS_image = {B_OCS_IMAGE}")
    print("=" * 60)

    fast = run_one("fast", "A_fast")
    full = run_one("full", "A_full")

    print(f"\n{'='*60}")
    print(f"  对比总结")
    print(f"  {'':20s} {'OCS_no_occ':>12s} {'OCS_with_occ':>12s} {'occ_ratio':>10s}")
    for r in [fast, full]:
        print(f"  {r['label']:20s} {r['ocs_no_occ']:12.6f} {r['ocs_with_occ']:12.6f} {r['occlusion_ratio']:10.2%}")
    print(f"  {'B_exact (ref)':20s} {B_OCS_IMAGE:12.6f} {'—':>12s} {'—':>10s}")
    print(f"\n  A_full/B ratio: {full['ocs_no_occ']/B_OCS_IMAGE:.2%}")
    print(f"  A_fast/B ratio: {fast['ocs_no_occ']/B_OCS_IMAGE:.2%}")
    print("=" * 60)

    # 保存
    out = {
        "target": {"yaw": YAW, "pitch": PITCH},
        "B_ocs_image": B_OCS_IMAGE,
        "fast": fast,
        "full": full,
    }
    out_path = os.path.join(OUTPUT_DIR, "diag_geometry_accuracy.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\n  结果已保存: {out_path}")

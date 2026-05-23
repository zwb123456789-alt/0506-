# -*- coding: utf-8 -*-
"""
test_module_a_smoke.py —— 模块 A 冒烟测试
==========================================
最小规模运行：5 yaw × 3 pitch = 15 姿态。
验证：
    1. STL 能加载
    2. RayForest 可初始化
    3. scan_attitude 能返回完整 scan_data
    4. 任意一帧 occlusion_ratio 在 [0, 1]
    5. ocs_with_occ <= ocs_no_occ (容忍 1e-6)

不出图、不落盘，只控制台报告。
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01_code"))

import numpy as np

from config    import SUN_VECTOR, DET_VECTOR
from geometry  import load_meshes
from ocs_core  import scan_attitude


def main():
    print("=" * 60)
    print("  模块 A 冒烟测试 (5 yaw × 3 pitch)")
    print("=" * 60)

    meshes, total_faces = load_meshes(verbose=True)
    sun_norm = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
    det_norm = DET_VECTOR / np.linalg.norm(DET_VECTOR)

    scan = scan_attitude(
        meshes, sun_norm, det_norm,
        scan_mode=True,
        yaw_range=(0, 360),   num_yaw=5,
        pitch_range=(-90, 90), num_pitch=3,
    )

    assert len(scan) == 15, f"应该有 15 个姿态，实际 {len(scan)}"

    # 一致性检查
    bad = 0
    for d in scan:
        if not (0.0 <= d["occlusion_ratio"] <= 1.0):
            print(f"  [!] 遮挡率越界: yaw={d['yaw']}, pitch={d['pitch']}, ratio={d['occlusion_ratio']}")
            bad += 1
        if d["ocs_with_occ"] > d["ocs_no_occ"] * (1 + 1e-6):
            print(f"  [!] OCS 反常: yaw={d['yaw']}, pitch={d['pitch']}, "
                  f"with={d['ocs_with_occ']:.4e} > no={d['ocs_no_occ']:.4e}")
            bad += 1

    print("\n" + "=" * 60)
    if bad == 0:
        print(f"  [OK] 15/15 姿态全部通过物理一致性检查。")
    else:
        print(f"  [WARN] 发现 {bad} 处异常，建议查看。")
    print("=" * 60)


if __name__ == "__main__":
    main()

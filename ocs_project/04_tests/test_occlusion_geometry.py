# -*- coding: utf-8 -*-
"""
test_occlusion_geometry.py —— 遮挡几何专项验证（新 API）
=======================================================
对齐 occlusion.py 的 batch_occlusion_dual(min_hit_distance=...) 语义：
    1. 单平板：EPSILON 偏移 + min_hit_distance 过滤，无自相交误报
    2. 双平板：不同部件之间应能检测遮挡
    3. 同部件 U 型：新逻辑应直接检出，不再漏检

此脚本用于快速冒烟验证；完整矩阵见 05_occlusion_validation/run_occlusion_validation.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "01_code"))

import numpy as np
import trimesh

from config import EPSILON
from occlusion import RayForest


def make_box(center, extents):
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def check(name, condition, detail):
    status = "OK" if condition else "FAIL"
    print(f"  [{status}] {name}: {detail}")
    return condition


def test_single_plate_no_false_occlusion():
    """起点 = 上表面 + normal·EPSILON；min_hit_distance=EPSILON。应无命中。"""
    meshes = {"plate": make_box([0.0, 0.0, 0.0], [40.0, 40.0, 1.0])}
    forest = RayForest(meshes)
    origins = np.array([[0.0, 0.0, 0.5 + EPSILON]])  # 上表面 z=0.5，加 EPSILON 偏移
    direction = np.array([0.0, 0.0, 1.0])
    occ, _ = forest.batch_occlusion_dual(
        origins, direction, direction, min_hit_distance=EPSILON)
    return check(
        "单平板无误遮挡",
        not bool(occ[0]),
        f"origin={origins[0].tolist()}, mhd={EPSILON}, occ={bool(occ[0])}",
    )


def test_two_part_occlusion_detected():
    """下板 → +Z → 上板。应命中上板。"""
    meshes = {
        "lower": make_box([0.0, 0.0, 0.0], [40.0, 40.0, 1.0]),
        "upper": make_box([0.0, 0.0, 20.0], [40.0, 40.0, 1.0]),
    }
    forest = RayForest(meshes)
    origins = np.array([[0.0, 0.0, 0.5 + EPSILON]])
    direction = np.array([0.0, 0.0, 1.0])
    occ, _ = forest.batch_occlusion_dual(
        origins, direction, direction, min_hit_distance=EPSILON)
    return check(
        "双平板跨部件遮挡",
        bool(occ[0]),
        f"起点在下板上表面，沿 +Z 应命中上板，occ={bool(occ[0])}",
    )


def test_u_block_same_part_occlusion_detected():
    """U 型块内部 → +Y → 背墙。新逻辑应命中（而非漏检）。"""
    left_wall  = make_box([-15.0, 0.0, 15.0], [4.0, 30.0, 30.0])
    right_wall = make_box([ 15.0, 0.0, 15.0], [4.0, 30.0, 30.0])
    back_wall  = make_box([  0.0, 14.0, 15.0], [34.0, 4.0, 30.0])
    bottom     = make_box([  0.0, 0.0,  0.0], [34.0, 30.0, 4.0])
    u_block = trimesh.util.concatenate([left_wall, right_wall, back_wall, bottom])
    meshes = {"u_block": u_block}
    forest = RayForest(meshes)
    origins = np.array([[0.0, 0.0, 15.0]])   # 凹槽内部
    direction = np.array([0.0, 1.0, 0.0])
    occ, _ = forest.batch_occlusion_dual(
        origins, direction, direction, min_hit_distance=EPSILON)
    return check(
        "U 型块同部件遮挡（新逻辑应命中）",
        bool(occ[0]),
        f"起点在凹槽内部，+Y 方向背墙应命中，occ={bool(occ[0])}",
    )


def main():
    print("=" * 60)
    print("  遮挡几何专项验证（新 API：min_hit_distance）")
    print("=" * 60)

    results = [
        test_single_plate_no_false_occlusion(),
        test_two_part_occlusion_detected(),
        test_u_block_same_part_occlusion_detected(),
    ]

    print("\n" + "=" * 60)
    if all(results):
        print("  [OK] 全部通过：min_hit_distance 机制在三类几何下均符合预期。")
    else:
        print("  [FAIL] 存在异常，请检查输出。")
        raise SystemExit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

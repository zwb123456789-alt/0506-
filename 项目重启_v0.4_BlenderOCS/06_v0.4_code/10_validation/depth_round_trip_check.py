# -*- coding: utf-8 -*-
"""
depth_round_trip_check.py —— 1C-E06 Phase 0 Step 2: Depth Round-Trip Sanity Check
==================================================================================
验证 camera/sun depth 的双向 round-trip 一致性（纯数学验证）

任务边界（R10 Codex）：
- 只验证 3 个已知点的 depth round-trip
- 确认 Blender depth 符号、单位、local z 映射的数学约定
- 只做数学计算验证，不实际调用 Blender 渲染
- 不生成 EXR/PNG/npy 文件
- 不进入 20 姿态 shadow validation
- 不校准 DEPTH_EPSILON_M_FINAL
- 不运行全量 2664 姿态
- 不训练模型

验证方法：
1. 定义 3 个已知点（本体坐标系）
2. 计算 camera depth（正交投影沿 -z_camera 方向的距离）
3. 计算 sun depth（沿 sun 方向的距离）
4. 反向计算：从 depth 恢复 3D 位置
5. 比较 round-trip 误差
6. 确认符号、单位、坐标系约定
"""

import sys
import os
import time
import json
from pathlib import Path

# 添加代码路径
project_root = Path(__file__).resolve().parents[2]
config_dir = project_root / "06_v0.4_code" / "00_config"
geometry_dir = project_root / "06_v0.4_code" / "01_geometry"

sys.path.insert(0, str(config_dir))
sys.path.insert(0, str(geometry_dir))

import numpy as np
from config_v0_4 import (
    SUN_VECTOR, DET_VECTOR, UNIT_SCALE,
    DEPTH_EPSILON_M_INITIAL, OUTPUT_DIR
)
from geometry_loader import euler_to_matrix


def normalize(v):
    """归一化向量"""
    return v / np.linalg.norm(v)


def compute_camera_depth(point_world, camera_z_world):
    """
    计算 camera depth（正交投影）

    参数:
        point_world: 点的世界坐标（惯性系）[3]，单位：m
        camera_z_world: camera z 轴方向（惯性系，指向远离相机）[3]

    返回:
        depth: camera depth（m），沿 -z_camera 方向的距离

    说明:
        - Blender 正交相机：depth = 点到相机平面的距离
        - 相机看向 -z 方向，所以 depth = -dot(point, z_camera)
        - 在 Blender Depth pass 中，depth 是正值（距离）
        - depth 的符号约定：正值表示在相机前方
    """
    camera_z_world = normalize(camera_z_world)

    # camera depth = 点沿 -z_camera 方向投影的距离
    # 由于相机看向 -z，depth = -dot(point, z_camera)
    depth = -np.dot(point_world, camera_z_world)

    return depth


def compute_sun_depth(point_world, sun_dir_world):
    """
    计算 sun depth（沿太阳方向）

    参数:
        point_world: 点的世界坐标（惯性系）[3]，单位：m
        sun_dir_world: 太阳方向（惯性系，指向太阳）[3]

    返回:
        sun_depth: sun depth（m），沿 sun 方向的距离

    说明:
        - sun depth = 点沿 sun 方向的投影距离
        - sun_depth = dot(point, sun_dir)
        - 用于 shadow mapping 的 depth reprojection
        - sun_depth 可以为负（点在 sun 方向的反向）
    """
    sun_dir_world = normalize(sun_dir_world)

    # sun depth = 点沿 sun 方向投影的距离
    sun_depth = np.dot(point_world, sun_dir_world)

    return sun_depth


def camera_depth_to_world(depth, pixel_xy_ndc, camera_z_world, ortho_scale):
    """
    从 camera depth 和像素坐标恢复世界坐标（正交投影）

    参数:
        depth: camera depth（m）
        pixel_xy_ndc: 像素坐标 [x, y]，归一化到 [-1, 1]（NDC坐标）
        camera_z_world: camera z 轴方向（惯性系）[3]
        ortho_scale: 正交投影的缩放因子（m）

    返回:
        point_world: 恢复的世界坐标 [3]（m）

    说明:
        - 正交投影：x_world = pixel_x_ndc * ortho_scale / 2
        - y_world = pixel_y_ndc * ortho_scale / 2
        - z_world = -depth（相机看向 -z）
    """
    camera_z_world = normalize(camera_z_world)

    # 构造相机坐标系的 x, y 轴
    # 假设相机 up 为世界 +y（简化处理）
    world_up = np.array([0.0, 1.0, 0.0])

    # 处理特殊情况：camera_z 与 world_up 平行
    if np.abs(np.dot(camera_z_world, world_up)) > 0.99:
        world_up = np.array([1.0, 0.0, 0.0])

    camera_x = normalize(np.cross(world_up, camera_z_world))
    camera_y = normalize(np.cross(camera_z_world, camera_x))

    # 正交投影恢复
    # NDC [-1, 1] → 世界坐标偏移
    x_offset = pixel_xy_ndc[0] * ortho_scale / 2.0
    y_offset = pixel_xy_ndc[1] * ortho_scale / 2.0
    z_offset = -depth  # 相机看向 -z

    point_world = (x_offset * camera_x +
                   y_offset * camera_y +
                   z_offset * camera_z_world)

    return point_world


def sun_depth_to_world(sun_depth, point_xy_perp, sun_dir_world):
    """
    从 sun depth 和横向坐标恢复世界坐标

    参数:
        sun_depth: sun depth（m）
        point_xy_perp: 点在垂直于 sun 方向平面上的坐标 [x, y]（m）
        sun_dir_world: 太阳方向（惯性系）[3]

    返回:
        point_world: 恢复的世界坐标 [3]（m）

    说明:
        - 这是简化验证，实际 shadow mapping 更复杂
        - point_world = sun_depth * sun_dir + point_xy_perpendicular
    """
    sun_dir_world = normalize(sun_dir_world)

    # 构造垂直于 sun 的坐标系
    world_up = np.array([0.0, 1.0, 0.0])
    if np.abs(np.dot(sun_dir_world, world_up)) > 0.99:
        world_up = np.array([1.0, 0.0, 0.0])

    sun_x = normalize(np.cross(world_up, sun_dir_world))
    sun_y = normalize(np.cross(sun_dir_world, sun_x))

    # 恢复世界坐标
    point_world = (sun_depth * sun_dir_world +
                   point_xy_perp[0] * sun_x +
                   point_xy_perp[1] * sun_y)

    return point_world


def main():
    """执行 depth round-trip sanity check"""

    print("=" * 80)
    print("1C-E06 Phase 0 Step 2: Depth Round-Trip Sanity Check")
    print("=" * 80)
    print()

    # ============================================================
    # 1. 定义 3 个已知点（本体坐标系，单位：mm）
    # ============================================================
    print("[1/6] 定义已知点")

    # 选择 3 个代表性点：
    # P1: 金属主体前端（x 正向）
    # P2: 太阳能板中心（y 负向）
    # P3: 隐身板顶部（z 正向）
    test_points_body_mm = {
        "P1_metal_front":  np.array([700.0,   0.0,   0.0]),
        "P2_solar_center": np.array([  0.0, -300.0,  0.0]),
        "P3_dark_top":     np.array([  0.0,   0.0, 400.0]),
    }

    # 转换为米
    test_points_body_m = {
        name: pt * UNIT_SCALE
        for name, pt in test_points_body_mm.items()
    }

    print("  测试点（本体坐标系）：")
    for name, pt_mm in test_points_body_mm.items():
        pt_m = test_points_body_m[name]
        print(f"    {name:18s}: [{pt_mm[0]:7.1f}, {pt_mm[1]:7.1f}, {pt_mm[2]:7.1f}] mm"
              f"  = [{pt_m[0]:7.4f}, {pt_m[1]:7.4f}, {pt_m[2]:7.4f}] m")

    print()

    # ============================================================
    # 2. 设置姿态和几何
    # ============================================================
    print("[2/6] 设置姿态和观测几何")

    # 使用单姿态 yaw=0, pitch=0, roll=0
    yaw, pitch, roll = 0, 0, 0
    R = euler_to_matrix(yaw, pitch, roll, degrees=True)

    print(f"  姿态: yaw={yaw}°, pitch={pitch}°, roll={roll}°")
    print(f"  旋转矩阵 R (M→I): 单位阵")

    # 观测几何（phase63 baseline）
    sun_dir = normalize(SUN_VECTOR)
    det_dir = normalize(DET_VECTOR)

    print(f"  太阳方向（惯性系）: [{sun_dir[0]:6.3f}, {sun_dir[1]:6.3f}, {sun_dir[2]:6.3f}]")
    print(f"  探测器方向（惯性系）: [{det_dir[0]:6.3f}, {det_dir[1]:6.3f}, {det_dir[2]:6.3f}]")

    # 计算 camera z 方向（探测器看向目标，z 指向远离相机）
    camera_z = -det_dir  # Blender 相机 z 轴指向远离相机

    print(f"  camera z 方向（惯性系）: [{camera_z[0]:6.3f}, {camera_z[1]:6.3f}, {camera_z[2]:6.3f}]")

    # 正交投影缩放（简化：使用固定值）
    # 实际应该是 ORTHO_SCALE_FACTOR * r_max，这里简化验证
    ortho_scale = 2.0  # m

    print(f"  正交投影缩放: {ortho_scale:.2f} m")
    print()

    # ============================================================
    # 3. Camera Depth Round-Trip
    # ============================================================
    print("[3/6] Camera Depth Round-Trip 验证")
    print()

    camera_results = {}

    for name, pt_body_m in test_points_body_m.items():
        # 本体 → 惯性（世界）
        pt_world = R @ pt_body_m

        # 正向：计算 camera depth
        depth_forward = compute_camera_depth(pt_world, camera_z)

        # 反向：从 depth 恢复世界坐标
        # 需要知道点在 camera xy 平面的位置
        # 构造 camera 坐标系
        world_up = np.array([0, 1, 0])
        if np.abs(np.dot(camera_z, world_up)) > 0.99:
            world_up = np.array([1, 0, 0])

        camera_x = normalize(np.cross(world_up, camera_z))
        camera_y = normalize(np.cross(camera_z, camera_x))

        # 计算点在 camera xy 平面的投影（NDC 坐标）
        pixel_x_ndc = 2.0 * np.dot(pt_world, camera_x) / ortho_scale
        pixel_y_ndc = 2.0 * np.dot(pt_world, camera_y) / ortho_scale
        pixel_xy_ndc = np.array([pixel_x_ndc, pixel_y_ndc])

        pt_recovered = camera_depth_to_world(depth_forward, pixel_xy_ndc, camera_z, ortho_scale)

        # 计算误差
        error = np.linalg.norm(pt_world - pt_recovered)
        error_xyz = pt_world - pt_recovered

        camera_results[name] = {
            "point_world": pt_world,
            "depth_forward": depth_forward,
            "pixel_xy_ndc": pixel_xy_ndc,
            "point_recovered": pt_recovered,
            "error": error,
            "error_xyz": error_xyz,
        }

        print(f"  {name}:")
        print(f"    原始世界坐标: [{pt_world[0]:8.5f}, {pt_world[1]:8.5f}, {pt_world[2]:8.5f}] m")
        print(f"    camera depth: {depth_forward:8.5f} m")
        print(f"    像素坐标 (NDC): [{pixel_xy_ndc[0]:7.4f}, {pixel_xy_ndc[1]:7.4f}]")
        print(f"    恢复世界坐标: [{pt_recovered[0]:8.5f}, {pt_recovered[1]:8.5f}, {pt_recovered[2]:8.5f}] m")
        print(f"    Round-trip 误差: {error:.2e} m")

        if error < 1e-10:
            print(f"    [OK] 误差 < 1e-10 m（数值精度范围内）")
        elif error < DEPTH_EPSILON_M_INITIAL:
            print(f"    [OK] 误差 < DEPTH_EPSILON_M_INITIAL ({DEPTH_EPSILON_M_INITIAL:.2e} m)")
        else:
            print(f"    [WARN] 误差 > DEPTH_EPSILON_M_INITIAL")

        print()

    # ============================================================
    # 4. Sun Depth Round-Trip
    # ============================================================
    print("[4/6] Sun Depth Round-Trip 验证")
    print()

    sun_results = {}

    for name, pt_body_m in test_points_body_m.items():
        # 本体 → 惯性（世界）
        pt_world = R @ pt_body_m

        # 正向：计算 sun depth
        sun_depth_forward = compute_sun_depth(pt_world, sun_dir)

        # 反向：从 sun depth 恢复世界坐标
        # 需要知道点在垂直于 sun 的平面上的位置
        world_up = np.array([0, 1, 0])
        if np.abs(np.dot(sun_dir, world_up)) > 0.99:
            world_up = np.array([1, 0, 0])

        sun_x = normalize(np.cross(world_up, sun_dir))
        sun_y = normalize(np.cross(sun_dir, sun_x))

        sun_xy = np.array([
            np.dot(pt_world, sun_x),
            np.dot(pt_world, sun_y),
        ])

        pt_recovered = sun_depth_to_world(sun_depth_forward, sun_xy, sun_dir)

        # 计算误差
        error = np.linalg.norm(pt_world - pt_recovered)
        error_xyz = pt_world - pt_recovered

        sun_results[name] = {
            "point_world": pt_world,
            "sun_depth_forward": sun_depth_forward,
            "sun_xy": sun_xy,
            "point_recovered": pt_recovered,
            "error": error,
            "error_xyz": error_xyz,
        }

        print(f"  {name}:")
        print(f"    原始世界坐标: [{pt_world[0]:8.5f}, {pt_world[1]:8.5f}, {pt_world[2]:8.5f}] m")
        print(f"    sun depth: {sun_depth_forward:8.5f} m")
        print(f"    sun xy 坐标: [{sun_xy[0]:8.5f}, {sun_xy[1]:8.5f}] m")
        print(f"    恢复世界坐标: [{pt_recovered[0]:8.5f}, {pt_recovered[1]:8.5f}, {pt_recovered[2]:8.5f}] m")
        print(f"    Round-trip 误差: {error:.2e} m")

        if error < 1e-10:
            print(f"    [OK] 误差 < 1e-10 m（数值精度范围内）")
        elif error < DEPTH_EPSILON_M_INITIAL:
            print(f"    [OK] 误差 < DEPTH_EPSILON_M_INITIAL ({DEPTH_EPSILON_M_INITIAL:.2e} m)")
        else:
            print(f"    [WARN] 误差 > DEPTH_EPSILON_M_INITIAL")

        print()

    # ============================================================
    # 5. 符号和坐标系检查
    # ============================================================
    print("[5/6] 符号和坐标系一致性检查")
    print()

    print("  Camera Depth 符号约定：")
    print("    - Blender 相机看向 -z 方向")
    print("    - camera depth = 点到相机平面的距离（正值）")
    print("    - depth = -dot(point, z_camera)（z_camera 指向远离相机）")
    print()

    all_camera_depths_positive = all(r["depth_forward"] > 0 for r in camera_results.values())
    if all_camera_depths_positive:
        print("    [OK] 所有测试点的 camera depth 均为正值")
    else:
        print("    [WARN] 存在负值 camera depth")

    print()

    print("  Sun Depth 符号约定：")
    print("    - sun depth = 点沿 sun 方向的投影距离")
    print("    - sun_depth = dot(point, sun_dir)（sun_dir 指向太阳）")
    print("    - 测试点的 sun depth 可能为正或负（取决于相对位置）")
    print()

    for name, result in sun_results.items():
        sun_depth = result["sun_depth_forward"]
        sign_str = "正值" if sun_depth > 0 else "负值"
        print(f"    {name}: {sun_depth:8.5f} m ({sign_str})")

    print()

    print("  Local Z 映射：")
    print("    - 本体坐标系 +z 通过旋转矩阵 R 映射到惯性系")
    print("    - 对于单位阵姿态（yaw=0, pitch=0, roll=0）：本体 +z = 惯性 +z")
    print("    - camera z = -det_dir（相机看向探测器反方向）")
    print("    - Blender depth pass 使用 camera local z")
    print("    - 本轮验证使用数学计算，未实际调用 Blender [OK]")
    print()

    print("  单位一致性：")
    print("    - 输入：本体坐标 mm -> 转换为 m")
    print("    - depth 计算：m")
    print("    - 输出：恢复世界坐标 m")
    print("    - Blender 实际渲染时：STL 单位为 mm，depth 单位也为 mm")
    print("    - 本轮验证统一使用 m 单位")
    print()

    # ============================================================
    # 6. 总结
    # ============================================================
    print("=" * 80)
    print("[6/6] Depth Round-Trip Sanity Check 完成")
    print("=" * 80)

    # 检查所有误差是否在容忍范围内
    camera_errors = [r["error"] for r in camera_results.values()]
    sun_errors = [r["error"] for r in sun_results.values()]

    max_camera_error = max(camera_errors)
    max_sun_error = max(sun_errors)

    print()
    print(f"  Camera Round-Trip 最大误差: {max_camera_error:.2e} m")
    print(f"  Sun Round-Trip 最大误差: {max_sun_error:.2e} m")
    print(f"  DEPTH_EPSILON_M_INITIAL: {DEPTH_EPSILON_M_INITIAL:.2e} m")
    print()

    if max_camera_error < 1e-10 and max_sun_error < 1e-10:
        print("  [OK] 所有 round-trip 误差在数值精度范围内（< 1e-10 m）")
        overall_status = "PASS"
    elif max_camera_error < DEPTH_EPSILON_M_INITIAL and max_sun_error < DEPTH_EPSILON_M_INITIAL:
        print(f"  [OK] 所有 round-trip 误差 < DEPTH_EPSILON_M_INITIAL")
        overall_status = "PASS"
    else:
        print(f"  [WARN] 存在 round-trip 误差 > DEPTH_EPSILON_M_INITIAL")
        overall_status = "WARNING"

    print()

    # ============================================================
    # 7. 重要说明
    # ============================================================
    print("  重要说明：")
    print("    1. [OK] 本轮只做数学验证，未实际调用 Blender 渲染")
    print("    2. [OK] 未生成 Blender Depth pass EXR 文件")
    print("    3. [OK] 未进入 20 姿态 shadow validation")
    print("    4. [OK] 未校准 DEPTH_EPSILON_M_FINAL")
    print("    5. [OK] 未运行全量 2664 姿态")
    print("    6. [OK] 未训练模型")
    print("    7. [WARN] Blender 实际 depth 可能有不同的符号/单位约定，需在后续验证")
    print("    8. [WARN] 后续需要实际 Blender 渲染来验证 depth pass 的实际输出")
    print()

    # 返回结果
    return {
        "overall_status": overall_status,
        "test_points_body_mm": {k: v.tolist() for k, v in test_points_body_mm.items()},
        "test_points_body_m": {k: v.tolist() for k, v in test_points_body_m.items()},
        "camera_results": {
            k: {
                "point_world": v["point_world"].tolist(),
                "depth_forward": float(v["depth_forward"]),
                "pixel_xy_ndc": v["pixel_xy_ndc"].tolist(),
                "point_recovered": v["point_recovered"].tolist(),
                "error": float(v["error"]),
                "error_xyz": v["error_xyz"].tolist(),
            }
            for k, v in camera_results.items()
        },
        "sun_results": {
            k: {
                "point_world": v["point_world"].tolist(),
                "sun_depth_forward": float(v["sun_depth_forward"]),
                "sun_xy": v["sun_xy"].tolist(),
                "point_recovered": v["point_recovered"].tolist(),
                "error": float(v["error"]),
                "error_xyz": v["error_xyz"].tolist(),
            }
            for k, v in sun_results.items()
        },
        "max_camera_error": float(max_camera_error),
        "max_sun_error": float(max_sun_error),
        "depth_epsilon_m_initial": DEPTH_EPSILON_M_INITIAL,
        "notes": [
            "本轮只做数学验证，未实际调用 Blender",
            "未生成 EXR/PNG/npy 数据",
            "未进入 20 姿态 shadow validation",
            "未校准 DEPTH_EPSILON_M_FINAL",
            "未运行全量 2664 姿态",
            "未训练模型",
            "Blender 实际 depth 符号/单位需在后续验证",
        ]
    }


if __name__ == "__main__":
    result = main()

    # 保存结果到 JSON
    output_dir = Path(OUTPUT_DIR) / "00_validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "depth_round_trip_result.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  结果已保存: {json_path}")
    print()

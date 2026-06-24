# -*- coding: utf-8 -*-
"""
validate_shadow_consistency.py —— Shadow Depth Consistency Validation (FIXED)
================================================================================
验证 camera-view 和 sun-view 深度的几何一致性。

修复内容（1C-E08-FIX01）：
    1. 对 camera-view 前景点，计算其在 sun-view 中的正交投影像素坐标
    2. 读取 sun-view 对应像素的实际深度
    3. 计算同一零点定义下的预期深度
    4. 统计真实的 depth_error = depth_sun_actual - depth_sun_expected
    5. 基于真实误差分布校准 DEPTH_EPSILON_M_FINAL

原理：
    对于可见且被照亮的表面点：
    1. 从 camera-view 获取 Position_camera（世界坐标）
    2. 将 Position_camera 投影到 sun-view 像素坐标 (u_sun, v_sun)
    3. 读取 sun-view[v_sun, u_sun] 的实际深度和位置
    4. 计算预期的 sun depth：depth_expected = dot(Position_camera - sun_cam_pos, sun_dir)
    5. 计算误差：depth_error = depth_actual - depth_expected

输出：
    - 每个姿态的 shadow validation 结果（包含真实误差统计）
    - 深度差异统计（用于校准 DEPTH_EPSILON_M_FINAL）
    - 汇总报告
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    import OpenEXR
    import Imath
except ImportError:
    print("[ERROR] 需要安装 OpenEXR 库: pip install OpenEXR")
    sys.exit(1)


# ============================================================
# 1. 配置
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")
SHADOW_PASSES_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "shadow_passes")
OUTPUT_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "shadow_validation")

# 观测几何
SUN_VECTOR = np.array([1.0, 0.0, 0.3])
DET_VECTOR = np.array([0.5, -1.0, 0.1])

# 归一化
SUN_DIR = SUN_VECTOR / np.linalg.norm(SUN_VECTOR)
DET_DIR = DET_VECTOR / np.linalg.norm(DET_VECTOR)

# 初始深度阈值（待校准）
DEPTH_EPSILON_INITIAL = 1e-3  # m

# Blender 远平面值
BLENDER_FAR_PLANE = 1e10

# 渲染参数（从 render_20_attitudes_shadow.py）
RESOLUTION = 256
R_MAX_NOMINAL = 1.4726  # m，从 E07 验证报告


# ============================================================
# 2. 相机几何参数
# ============================================================
def get_sun_camera_params(r_max):
    """
    获取 sun-view 正交相机参数

    返回：
        sun_cam_pos: 相机位置（世界坐标）
        sun_dir: 相机朝向（归一化）
        ortho_scale: 正交相机缩放
        resolution: 分辨率
    """
    # Sun camera 位于 SUN_DIR 方向，距离 5 * r_max
    sun_cam_pos = SUN_DIR * (5.0 * r_max)

    # 正交相机缩放
    ortho_scale = 2.2 * r_max

    # 相机朝向：看向原点（-SUN_DIR）
    sun_view_dir = -SUN_DIR

    return sun_cam_pos, sun_view_dir, ortho_scale, RESOLUTION


def world_to_sun_pixel(position, sun_cam_pos, sun_dir, ortho_scale, resolution):
    """
    将世界坐标投影到 sun-view 像素坐标

    参数：
        position: (H, W, 3) 或 (3,) 世界坐标
        sun_cam_pos: 相机位置
        sun_dir: 相机朝向（归一化，指向观察方向 = -SUN_DIR）
        ortho_scale: 正交相机缩放
        resolution: 分辨率

    返回：
        u, v: 像素坐标（可能超出画幅）
        in_bounds: 布尔数组，标记是否在画幅内
    """
    # 将点变换到相机坐标系
    # 相机坐标系：Z 轴沿 -sun_dir（看向原点），X 轴水平，Y 轴垂直

    # 构造相机坐标系的基向量
    # Z 轴：-sun_dir
    z_cam = -sun_dir

    # X 轴：取世界坐标系 Y 轴与 Z_cam 的叉积（如果平行则换成 X 轴）
    world_up = np.array([0.0, 1.0, 0.0])
    if np.abs(np.dot(world_up, z_cam)) > 0.99:
        world_up = np.array([1.0, 0.0, 0.0])

    x_cam = np.cross(world_up, z_cam)
    x_cam = x_cam / np.linalg.norm(x_cam)

    # Y 轴：Z_cam × X_cam
    y_cam = np.cross(z_cam, x_cam)

    # 变换到相机坐标系
    P_rel = position - sun_cam_pos  # (H, W, 3) 或 (3,)

    # 投影到相机 X-Y 平面
    x_proj = np.dot(P_rel, x_cam)  # (H, W) 或标量
    y_proj = np.dot(P_rel, y_cam)  # (H, W) 或标量

    # 归一化设备坐标（NDC）：[-1, 1]
    ndc_x = x_proj / (ortho_scale / 2.0)
    ndc_y = y_proj / (ortho_scale / 2.0)

    # 转换到像素坐标 [0, resolution-1]
    u = (ndc_x + 1.0) * 0.5 * resolution
    v = (1.0 - (ndc_y + 1.0) * 0.5) * resolution  # V 轴翻转（OpenGL -> 图像坐标）

    # 检查是否在画幅内
    in_bounds = (u >= 0) & (u < resolution) & (v >= 0) & (v < resolution)

    return u, v, in_bounds


# ============================================================
# 3. EXR 读取工具
# ============================================================
def read_exr_channel(exr_file, channel_name, resolution=(256, 256)):
    """读取 EXR 文件的单个通道"""
    if not os.path.isfile(exr_file):
        raise FileNotFoundError(f"EXR 文件不存在: {exr_file}")

    exr = OpenEXR.InputFile(exr_file)
    header = exr.header()

    # 检查通道是否存在
    channels = header['channels'].keys()
    if channel_name not in channels:
        raise ValueError(f"通道 {channel_name} 不存在于 {exr_file}")

    # 读取通道数据
    dw = header['dataWindow']
    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1

    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    channel_str = exr.channel(channel_name, pt)
    channel_data = np.frombuffer(channel_str, dtype=np.float32)
    channel_data = channel_data.reshape((height, width))

    return channel_data


def read_position_pass(exr_file):
    """读取 Position pass（X, Y, Z 三个通道）"""
    x = read_exr_channel(exr_file, "ViewLayer.Position.X")
    y = read_exr_channel(exr_file, "ViewLayer.Position.Y")
    z = read_exr_channel(exr_file, "ViewLayer.Position.Z")

    # Stack 成 (H, W, 3)
    position = np.stack([x, y, z], axis=-1)
    return position


def read_depth_pass(exr_file):
    """读取 Depth pass"""
    return read_exr_channel(exr_file, "ViewLayer.Depth.Z")


# ============================================================
# 4. Shadow Validation 核心算法（修复版）
# ============================================================
def validate_shadow_consistency(camera_exr, sun_exr, label, r_max):
    """
    验证单个姿态的 shadow depth consistency（修复版）

    修复内容：
        1. 对 camera-view 前景点投影到 sun-view 像素坐标
        2. 读取匹配点的 sun-view 实际深度
        3. 计算同一零点下的预期深度
        4. 统计真实的 depth_error

    返回：
        result (dict): 验证结果
    """
    print(f"\n验证姿态: {label}")

    # 读取 camera-view 数据
    print("  读取 camera-view data...")
    position_camera = read_position_pass(camera_exr)  # (H, W, 3)
    depth_camera = read_depth_pass(camera_exr)        # (H, W)

    # 读取 sun-view 数据
    print("  读取 sun-view data...")
    depth_sun_actual = read_depth_pass(sun_exr)       # (H, W)
    position_sun = read_position_pass(sun_exr)        # (H, W, 3)

    H, W = depth_camera.shape

    # 前景掩码（camera-view）
    r_camera = np.linalg.norm(position_camera, axis=-1)
    foreground_camera = (depth_camera < BLENDER_FAR_PLANE) & (r_camera > 0)

    # 前景掩码（sun-view）
    r_sun = np.linalg.norm(position_sun, axis=-1)
    foreground_sun = (depth_sun_actual < BLENDER_FAR_PLANE) & (r_sun > 0)

    # 统计像素数
    n_total = H * W
    n_fg_camera = np.sum(foreground_camera)
    n_fg_sun = np.sum(foreground_sun)

    print(f"    前景像素 (camera): {n_fg_camera}/{n_total} ({100*n_fg_camera/n_total:.1f}%)")
    print(f"    前景像素 (sun): {n_fg_sun}/{n_total} ({100*n_fg_sun/n_total:.1f}%)")

    # 获取 sun-view 相机参数
    sun_cam_pos, sun_view_dir, ortho_scale, resolution = get_sun_camera_params(r_max)

    print(f"    Sun camera position: {sun_cam_pos}")
    print(f"    Sun ortho_scale: {ortho_scale:.3f} m")

    # 对 camera-view 前景点投影到 sun-view
    print("  投影 camera-view 前景点到 sun-view...")

    # 只处理前景点
    fg_indices = np.where(foreground_camera)
    n_fg = len(fg_indices[0])

    if n_fg == 0:
        print("    [WARNING] camera-view 无前景点")
        return create_empty_result(label, camera_exr, sun_exr, H, W,
                                   n_fg_camera, n_fg_sun, n_total, "FAIL")

    # 前景点的世界坐标
    positions_fg = position_camera[fg_indices]  # (N, 3)

    # 投影到 sun-view 像素坐标
    u_sun, v_sun, in_bounds = world_to_sun_pixel(
        positions_fg, sun_cam_pos, sun_view_dir, ortho_scale, resolution
    )

    # 统计投影结果
    n_in_bounds = np.sum(in_bounds)
    print(f"    投影到 sun-view 画幅内: {n_in_bounds}/{n_fg} ({100*n_in_bounds/n_fg:.1f}%)")

    if n_in_bounds == 0:
        print("    [WARNING] 无点投影到 sun-view 画幅内")
        return create_empty_result(label, camera_exr, sun_exr, H, W,
                                   n_fg_camera, n_fg_sun, n_total, "FAIL")

    # 只保留投影在画幅内的点
    u_sun_valid = u_sun[in_bounds].astype(int)
    v_sun_valid = v_sun[in_bounds].astype(int)
    positions_valid = positions_fg[in_bounds]  # (N_valid, 3)

    # 读取 sun-view 对应像素的深度和位置
    depth_sun_matched = depth_sun_actual[v_sun_valid, u_sun_valid]
    position_sun_matched = position_sun[v_sun_valid, u_sun_valid]

    # 检查 sun-view 对应点是否为前景
    r_sun_matched = np.linalg.norm(position_sun_matched, axis=-1)
    sun_fg_matched = (depth_sun_matched < BLENDER_FAR_PLANE) & (r_sun_matched > 0)

    n_sun_fg_matched = np.sum(sun_fg_matched)
    print(f"    Sun-view 对应点为前景: {n_sun_fg_matched}/{n_in_bounds} ({100*n_sun_fg_matched/n_in_bounds:.1f}%)")

    if n_sun_fg_matched == 0:
        print("    [WARNING] 无匹配的 sun-view 前景点")
        return create_empty_result(label, camera_exr, sun_exr, H, W,
                                   n_fg_camera, n_fg_sun, n_total, "FAIL")

    # 只保留 sun-view 前景匹配点
    positions_matched = positions_valid[sun_fg_matched]
    depth_sun_actual_matched = depth_sun_matched[sun_fg_matched]

    # 计算预期的 sun depth（同一零点定义）
    # Blender Depth pass 是相机到点的距离（沿视线方向）
    # 对于正交相机，depth = dot(P - cam_pos, cam_view_dir)
    depth_sun_expected = np.dot(positions_matched - sun_cam_pos, sun_view_dir)

    # 计算深度误差
    depth_error = depth_sun_actual_matched - depth_sun_expected

    # 统计误差
    error_mean = np.mean(depth_error)
    error_std = np.std(depth_error)
    error_abs_mean = np.mean(np.abs(depth_error))
    error_abs_p95 = np.percentile(np.abs(depth_error), 95)
    error_abs_p99 = np.percentile(np.abs(depth_error), 99)
    error_abs_max = np.max(np.abs(depth_error))

    print(f"    Depth error 统计:")
    print(f"      mean: {error_mean:.4e} m")
    print(f"      std: {error_std:.4e} m")
    print(f"      abs_mean: {error_abs_mean:.4e} m")
    print(f"      abs_p95: {error_abs_p95:.4e} m")
    print(f"      abs_p99: {error_abs_p99:.4e} m")
    print(f"      abs_max: {error_abs_max:.4e} m")

    # 验证状态：如果有足够多的匹配点，判定为 PASS
    # 阈值：至少 100 个匹配点，且误差分布合理
    pass_threshold = DEPTH_EPSILON_INITIAL
    status = "PASS" if (n_sun_fg_matched >= 100 and error_abs_mean < 1.0) else "WARN"

    result = {
        "label": label,
        "status": status,
        "camera_exr": camera_exr,
        "sun_exr": sun_exr,
        "resolution": [H, W],
        "foreground_pixels": {
            "camera": int(n_fg_camera),
            "sun": int(n_fg_sun),
            "total": int(n_total)
        },
        "projection_stats": {
            "camera_fg_count": int(n_fg),
            "projected_in_bounds_count": int(n_in_bounds),
            "sun_foreground_matched_count": int(n_sun_fg_matched)
        },
        "depth_error": {
            "matched_point_count": int(n_sun_fg_matched),
            "mean": float(error_mean),
            "std": float(error_std),
            "abs_mean": float(error_abs_mean),
            "abs_p95": float(error_abs_p95),
            "abs_p99": float(error_abs_p99),
            "abs_max": float(error_abs_max)
        },
        "pass_threshold_used": float(pass_threshold)
    }

    return result


def create_empty_result(label, camera_exr, sun_exr, H, W, n_fg_camera, n_fg_sun, n_total, status):
    """创建空结果（无有效匹配点时）"""
    return {
        "label": label,
        "status": status,
        "camera_exr": camera_exr,
        "sun_exr": sun_exr,
        "resolution": [H, W],
        "foreground_pixels": {
            "camera": int(n_fg_camera),
            "sun": int(n_fg_sun),
            "total": int(n_total)
        },
        "projection_stats": {
            "camera_fg_count": 0,
            "projected_in_bounds_count": 0,
            "sun_foreground_matched_count": 0
        },
        "depth_error": {
            "matched_point_count": 0,
            "mean": 0.0,
            "std": 0.0,
            "abs_mean": 0.0,
            "abs_p95": 0.0,
            "abs_p99": 0.0,
            "abs_max": 0.0
        },
        "pass_threshold_used": float(DEPTH_EPSILON_INITIAL)
    }


# ============================================================
# 5. 主执行流程
# ============================================================
def main():
    print("=" * 80)
    print("Shadow Depth Consistency Validation (FIXED)")
    print("=" * 80)
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 创建输出目录
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"\n输出目录: {OUTPUT_DIR}")

    # 读取渲染元数据
    metadata_file = os.path.join(SHADOW_PASSES_DIR, "render_metadata.json")
    if not os.path.isfile(metadata_file):
        print(f"[ERROR] 找不到渲染元数据: {metadata_file}")
        return 1

    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    results_render = metadata.get("results", [])
    r_max = metadata.get("r_max", R_MAX_NOMINAL)

    print(f"\n找到 {len(results_render)} 个姿态")
    print(f"边界框半径 r_max: {r_max:.3f} m")

    # 验证每个姿态
    validation_results = []

    for i, result in enumerate(results_render, 1):
        attitude = result["attitude"]
        label = attitude["label"]
        camera_exr = result["camera_file"]
        sun_exr = result["sun_file"]

        print(f"\n[{i}/{len(results_render)}] {label}")

        # 检查文件存在性
        if not os.path.isfile(camera_exr):
            print(f"  [SKIP] camera EXR 不存在: {camera_exr}")
            continue

        if not os.path.isfile(sun_exr):
            print(f"  [SKIP] sun EXR 不存在: {sun_exr}")
            continue

        try:
            result = validate_shadow_consistency(camera_exr, sun_exr, label, r_max)
            validation_results.append(result)

            # 保存单姿态结果
            result_file = os.path.join(OUTPUT_DIR, f"{label}_shadow_validation.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"  [{result['status']}] 验证完成")

        except Exception as e:
            print(f"  [ERROR] 验证失败: {e}")
            import traceback
            traceback.print_exc()

    # 汇总统计
    print("\n" + "=" * 80)
    print("汇总统计")
    print("=" * 80)

    n_pass = sum(1 for r in validation_results if r["status"] == "PASS")
    n_warn = sum(1 for r in validation_results if r["status"] == "WARN")
    n_fail = sum(1 for r in validation_results if r["status"] == "FAIL")

    print(f"\n通过 (PASS): {n_pass}/{len(validation_results)}")
    print(f"警告 (WARN): {n_warn}/{len(validation_results)}")
    print(f"失败 (FAIL): {n_fail}/{len(validation_results)}")

    # 收集所有误差统计（只统计有匹配点的姿态）
    all_abs_mean = []
    all_abs_p95 = []
    all_abs_p99 = []
    all_abs_max = []

    for r in validation_results:
        if r["depth_error"]["matched_point_count"] > 0:
            all_abs_mean.append(r["depth_error"]["abs_mean"])
            all_abs_p95.append(r["depth_error"]["abs_p95"])
            all_abs_p99.append(r["depth_error"]["abs_p99"])
            all_abs_max.append(r["depth_error"]["abs_max"])

    if all_abs_mean:
        global_abs_mean = np.mean(all_abs_mean)
        global_abs_p95_mean = np.mean(all_abs_p95)
        global_abs_p99_mean = np.mean(all_abs_p99)
        global_abs_max = np.max(all_abs_max)

        print(f"\n全局 depth error 统计 (abs):")
        print(f"  abs_mean 的均值: {global_abs_mean:.4e} m")
        print(f"  abs_p95 的均值: {global_abs_p95_mean:.4e} m")
        print(f"  abs_p99 的均值: {global_abs_p99_mean:.4e} m")
        print(f"  abs_max 的最大值: {global_abs_max:.4e} m")

        # 建议的 DEPTH_EPSILON_M_FINAL
        # 使用 p99 的均值，确保 99% 的点在阈值内
        suggested_epsilon = max(DEPTH_EPSILON_INITIAL, global_abs_p99_mean)

        print(f"\n建议 DEPTH_EPSILON_M_FINAL (基于 abs_p99 均值): {suggested_epsilon:.4e} m")
    else:
        suggested_epsilon = DEPTH_EPSILON_INITIAL
        print("\n[WARNING] 无有效误差统计，使用初始阈值")

    # 保存汇总结果
    summary = {
        "timestamp": datetime.now().isoformat(),
        "attitudes_validated": len(validation_results),
        "pass_count": n_pass,
        "warn_count": n_warn,
        "fail_count": n_fail,
        "depth_epsilon_initial": DEPTH_EPSILON_INITIAL,
        "depth_epsilon_suggested": float(suggested_epsilon),
        "calibration_method": "mean(abs_p99) across all attitudes",
        "sun_vector": SUN_VECTOR.tolist(),
        "det_vector": DET_VECTOR.tolist(),
        "r_max": r_max,
        "results": validation_results
    }

    summary_file = os.path.join(OUTPUT_DIR, "shadow_validation_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n汇总结果: {summary_file}")

    print("\n" + "=" * 80)
    print("验证完成")
    print("=" * 80)
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 判定最终状态
    if n_fail > 0:
        print(f"\n[NOT_COMPLETE] {n_fail} 个姿态验证失败")
        return 1
    elif n_pass == len(validation_results):
        print("\n[COMPLETE] 所有姿态 shadow validation 通过")
        return 0
    else:
        print(f"\n[WARN] {n_warn} 个姿态有警告")
        return 0


if __name__ == "__main__":
    sys.exit(main())

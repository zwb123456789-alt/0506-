# -*- coding: utf-8 -*-
"""
diagnose_position_coordinates.py —— 诊断 Position 坐标范围问题
================================================================================
读取 Position pass 并分析坐标系定义
"""

import os
import sys
import json
import numpy as np
from pathlib import Path

# ============================================================
# 1. 配置
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
GEOMETRY_DIR = PROJECT_ROOT / "v0.4_results" / "00_validation" / "geometry_passes"
METADATA_FILE = GEOMETRY_DIR / "render_metadata.json"

# ============================================================
# 2. 读取 EXR
# ============================================================
def read_exr_position(exr_file):
    """读取 Position 通道"""
    try:
        import OpenEXR
        import Imath

        exr = OpenEXR.InputFile(str(exr_file))
        header = exr.header()

        dw = header['dataWindow']
        width = dw.max.x - dw.min.x + 1
        height = dw.max.y - dw.min.y + 1

        FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)

        # 读取 Position X/Y/Z
        px_str = exr.channel('ViewLayer.Position.X', FLOAT)
        py_str = exr.channel('ViewLayer.Position.Y', FLOAT)
        pz_str = exr.channel('ViewLayer.Position.Z', FLOAT)

        px = np.frombuffer(px_str, dtype=np.float32).reshape(height, width)
        py = np.frombuffer(py_str, dtype=np.float32).reshape(height, width)
        pz = np.frombuffer(pz_str, dtype=np.float32).reshape(height, width)

        position = np.stack([px, py, pz], axis=-1)

        exr.close()
        return position
    except Exception as e:
        print(f"[ERROR] 读取 Position 失败: {e}")
        return None


def main():
    print("=" * 80)
    print("Position 坐标诊断")
    print("=" * 80)

    # 读取 metadata
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    r_max = metadata["r_max"]
    sun_vector = metadata["sun_vector"]
    det_vector = metadata["det_vector"]

    print(f"\n[INFO] 配置参数:")
    print(f"  r_max: {r_max:.4f} m")
    print(f"  sun_vector: {sun_vector}")
    print(f"  det_vector: {det_vector}")

    # 计算理论相机位置
    det_norm = np.linalg.norm(det_vector)
    det_dir = np.array(det_vector) / det_norm
    camera_dist = 5.0 * r_max
    camera_pos_theory = det_dir * camera_dist

    print(f"\n[INFO] 理论相机位置:")
    print(f"  det_dir (normalized): {det_dir}")
    print(f"  camera_dist: {camera_dist:.4f} m")
    print(f"  camera_pos: {camera_pos_theory}")

    # 读取姿态 1 的 Position
    label = "yaw000_pitch+000_roll+000"
    exr_file = GEOMETRY_DIR / f"{label}.exr"

    print(f"\n[INFO] 读取 Position: {exr_file.name}")
    position = read_exr_position(exr_file)

    if position is None:
        return 1

    # 分析 Position 坐标
    print(f"\n[INFO] Position 统计:")
    print(f"  shape: {position.shape}")

    # 有效像素（非零坐标）
    valid_mask = np.any(position != 0, axis=-1)
    valid_count = np.sum(valid_mask)
    print(f"  valid_pixel_count: {valid_count}")

    if valid_count == 0:
        print("  [ERROR] 无有效 Position 像素")
        return 1

    valid_pos = position[valid_mask]

    # 坐标统计
    x = valid_pos[:, 0]
    y = valid_pos[:, 1]
    z = valid_pos[:, 2]

    print(f"  x: [{x.min():.4f}, {x.max():.4f}], mean={x.mean():.4f}")
    print(f"  y: [{y.min():.4f}, {y.max():.4f}], mean={y.mean():.4f}")
    print(f"  z: [{z.min():.4f}, {z.max():.4f}], mean={z.mean():.4f}")

    # 距离原点
    r = np.sqrt(x**2 + y**2 + z**2)
    print(f"  r: [{r.min():.4f}, {r.max():.4f}], mean={r.mean():.4f}")

    # 检查 Position 是否相对于相机位置
    print(f"\n[INFO] 检查坐标系:")

    # 假设 Position 是世界坐标，计算相对于原点的方向
    pos_mean = valid_pos.mean(axis=0)
    pos_dir = pos_mean / np.linalg.norm(pos_mean)
    print(f"  平均 Position: {pos_mean}")
    print(f"  平均方向: {pos_dir}")

    # 检查是否与探测器方向相反（目标在相机后方）
    dot_with_det = np.dot(pos_dir, det_dir)
    print(f"  dot(pos_dir, det_dir): {dot_with_det:.4f}")

    if dot_with_det > 0.9:
        print("  [结论] Position 方向与探测器方向一致 → Position 可能是相对于原点的世界坐标")
        print("         但距离远大于 r_max，可能包含相机偏移")
    elif dot_with_det < -0.9:
        print("  [结论] Position 方向与探测器方向相反 → Position 可能是相对于相机的局部坐标")
    else:
        print("  [结论] Position 方向不明确")

    # 检查 Position - camera_pos 是否回到目标范围
    print(f"\n[INFO] 尝试坐标变换:")
    print(f"  假设 Position 包含相机偏移，尝试减去相机位置...")

    # 相机位置的多种可能形式
    test_transforms = [
        ("Position - camera_pos", pos_mean - camera_pos_theory),
        ("Position + camera_pos", pos_mean + camera_pos_theory),
        ("Position (原始)", pos_mean),
    ]

    for name, transformed in test_transforms:
        r_transformed = np.linalg.norm(transformed)
        print(f"  {name}: r={r_transformed:.4f} m")
        if 0.5 * r_max < r_transformed < 2.0 * r_max:
            print(f"    [OK] 在合理范围内 (0.5-2.0 × r_max)")
        else:
            print(f"    [X] 超出合理范围")

    # Blender Position pass 文档说明
    print(f"\n[INFO] Blender Position pass 定义:")
    print(f"  官方文档：Position pass 输出世界空间坐标（world space coordinates）")
    print(f"  预期行为：每个像素包含其在世界坐标系中的 3D 位置")
    print(f"  当前观察：Position 值约为 r_max 的 70-150 倍")

    print(f"\n[INFO] 可能原因分析:")
    print(f"  1. Position 输出的是相机空间坐标而非世界空间")
    print(f"  2. Position 包含了相机到目标的偏移")
    print(f"  3. 单位缩放 (UNIT_SCALE=1e-3) 未应用到 Position pass")
    print(f"  4. Blender 4.x 的 Position pass 行为可能与文档不符")

    print(f"\n[INFO] 建议:")
    print(f"  1. 检查 Blender 4.x Position pass 的实际定义")
    print(f"  2. 如果 Position 是相对坐标，需要应用变换")
    print(f"  3. 对于当前任务（sun-view depth），相对坐标已足够")
    print(f"  4. 如需绝对世界坐标（BRDF 计算），需要进一步校准")

    return 0


if __name__ == "__main__":
    sys.exit(main())

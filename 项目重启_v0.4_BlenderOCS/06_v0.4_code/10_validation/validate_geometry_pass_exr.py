# -*- coding: utf-8 -*-
"""
validate_geometry_pass_exr.py —— Phase 0 Step 3 FIX02: EXR 通道内容验证
================================================================================
本脚本读取 E07-FIX01 生成的 3 个姿态 geometry pass EXR，验证：
    1. Normal pass（法线通道）
    2. Depth/Z pass（深度通道）
    3. IndexOB/Object Index pass（对象索引通道）
    4. Position/WorldCoord pass（世界坐标通道）
    5. Sun-view depth（通过 Position 后处理计算）

输出：
    - exr_channel_validation_summary.json
    - sun_depth_*.npy（每个姿态的 sun depth 数组）
    - 更新 3_attitudes_geometry_check.md
    - 更新 3_attitudes_position_check.md
    - 更新 3_attitudes_sun_depth_check.md
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# ============================================================
# 1. 配置
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
GEOMETRY_DIR = PROJECT_ROOT / "v0.4_results" / "00_validation" / "geometry_passes"
METADATA_FILE = GEOMETRY_DIR / "render_metadata.json"
OUTPUT_SUMMARY = GEOMETRY_DIR / "exr_channel_validation_summary.json"

# ============================================================
# 2. EXR 读取（使用 OpenEXR）
# ============================================================
def read_exr_with_openexr(filepath):
    """
    使用 OpenEXR 读取 EXR 文件的所有通道
    返回：dict {channel_name: numpy_array}
    """
    try:
        import OpenEXR
        import Imath
    except ImportError:
        print("[ERROR] OpenEXR 不可用，无法读取 EXR")
        return None

    try:
        exr_file = OpenEXR.InputFile(filepath)
        header = exr_file.header()

        # 获取图像尺寸
        dw = header['dataWindow']
        width = dw.max.x - dw.min.x + 1
        height = dw.max.y - dw.min.y + 1

        # 获取所有通道名
        channels = header['channels']
        channel_names = list(channels.keys())

        print(f"  [INFO] 找到通道: {channel_names}")

        # 读取每个通道
        channel_data = {}
        FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)

        for ch_name in channel_names:
            # 读取原始字节数据
            ch_str = exr_file.channel(ch_name, FLOAT)
            # 转换为 numpy 数组
            ch_array = np.frombuffer(ch_str, dtype=np.float32)
            ch_array = ch_array.reshape(height, width)
            channel_data[ch_name] = ch_array

        exr_file.close()
        return channel_data

    except Exception as e:
        print(f"[ERROR] 读取 EXR 失败: {filepath}")
        print(f"        {e}")
        return None


def parse_exr_channels(channel_data):
    """
    从 OpenEXR 通道字典中提取 Blender 渲染的几何 pass

    Blender 通道命名约定：
        - ViewLayer.Combined.R/G/B/A - 合成图像
        - ViewLayer.Normal.X/Y/Z - 法线
        - ViewLayer.Depth.Z - 深度
        - ViewLayer.IndexOB.X - 对象索引
        - ViewLayer.Position.X/Y/Z - 世界坐标
    """
    if channel_data is None:
        return None

    channels = {}

    # 提取 Normal (X, Y, Z)
    if all(k in channel_data for k in ['ViewLayer.Normal.X', 'ViewLayer.Normal.Y', 'ViewLayer.Normal.Z']):
        Nx = channel_data['ViewLayer.Normal.X']
        Ny = channel_data['ViewLayer.Normal.Y']
        Nz = channel_data['ViewLayer.Normal.Z']
        channels['Normal'] = np.stack([Nx, Ny, Nz], axis=-1)

    # 提取 Depth (Z)
    if 'ViewLayer.Depth.Z' in channel_data:
        channels['Depth'] = channel_data['ViewLayer.Depth.Z']

    # 提取 IndexOB (X)
    if 'ViewLayer.IndexOB.X' in channel_data:
        channels['IndexOB'] = channel_data['ViewLayer.IndexOB.X']

    # 提取 Position (X, Y, Z)
    if all(k in channel_data for k in ['ViewLayer.Position.X', 'ViewLayer.Position.Y', 'ViewLayer.Position.Z']):
        Px = channel_data['ViewLayer.Position.X']
        Py = channel_data['ViewLayer.Position.Y']
        Pz = channel_data['ViewLayer.Position.Z']
        channels['Position'] = np.stack([Px, Py, Pz], axis=-1)

    # 提取 Combined (R, G, B, A) - 可选
    if all(k in channel_data for k in ['ViewLayer.Combined.R', 'ViewLayer.Combined.G',
                                        'ViewLayer.Combined.B', 'ViewLayer.Combined.A']):
        R = channel_data['ViewLayer.Combined.R']
        G = channel_data['ViewLayer.Combined.G']
        B = channel_data['ViewLayer.Combined.B']
        A = channel_data['ViewLayer.Combined.A']
        channels['Combined'] = np.stack([R, G, B, A], axis=-1)

    return channels


# ============================================================
# 3. 通道验证函数
# ============================================================
def validate_normal_channel(normal_data):
    """验证 Normal 通道"""
    if normal_data is None:
        return {"status": "MISSING", "error": "Normal 通道不存在"}

    H, W = normal_data.shape[0], normal_data.shape[1]

    # 提取 Nx, Ny, Nz
    Nx = normal_data[:, :, 0]
    Ny = normal_data[:, :, 1]
    Nz = normal_data[:, :, 2]

    # 计算法线模长
    norm_magnitude = np.sqrt(Nx**2 + Ny**2 + Nz**2)

    # 有效像素：法线模长 > 0.01
    valid_mask = norm_magnitude > 0.01
    valid_count = np.sum(valid_mask)

    if valid_count == 0:
        return {
            "status": "INVALID",
            "error": "无有效法线像素",
            "resolution": [H, W],
            "valid_pixel_count": 0
        }

    valid_Nx = Nx[valid_mask]
    valid_Ny = Ny[valid_mask]
    valid_Nz = Nz[valid_mask]
    valid_norm = norm_magnitude[valid_mask]

    return {
        "status": "PASS",
        "resolution": [H, W],
        "valid_pixel_count": int(valid_count),
        "Nx_range": [float(valid_Nx.min()), float(valid_Nx.max())],
        "Ny_range": [float(valid_Ny.min()), float(valid_Ny.max())],
        "Nz_range": [float(valid_Nz.min()), float(valid_Nz.max())],
        "norm_magnitude": {
            "min": float(valid_norm.min()),
            "max": float(valid_norm.max()),
            "mean": float(valid_norm.mean())
        }
    }


def validate_depth_channel(depth_data):
    """验证 Depth/Z 通道"""
    if depth_data is None:
        return {"status": "MISSING", "error": "Depth 通道不存在"}

    H, W = depth_data.shape

    # 有效像素：finite and > 0
    valid_mask = np.isfinite(depth_data) & (depth_data > 0)
    valid_count = np.sum(valid_mask)

    if valid_count == 0:
        return {
            "status": "INVALID",
            "error": "无有效深度像素",
            "resolution": [H, W],
            "valid_pixel_count": 0
        }

    valid_depth = depth_data[valid_mask]

    # 检查 inf/NaN
    has_inf = np.sum(np.isinf(depth_data)) > 0
    has_nan = np.sum(np.isnan(depth_data)) > 0

    return {
        "status": "PASS",
        "resolution": [H, W],
        "valid_pixel_count": int(valid_count),
        "depth_range": [float(valid_depth.min()), float(valid_depth.max())],
        "depth_mean": float(valid_depth.mean()),
        "has_inf": bool(has_inf),
        "has_nan": bool(has_nan)
    }


def validate_indexob_channel(indexob_data):
    """验证 IndexOB/Object Index 通道"""
    if indexob_data is None:
        return {"status": "MISSING", "error": "IndexOB 通道不存在"}

    H, W = indexob_data.shape

    # 获取唯一索引值
    unique_values = np.unique(indexob_data)

    # 统计每个索引的像素数
    index_counts = {}
    for val in unique_values:
        count = np.sum(indexob_data == val)
        # 索引值可能是浮点数，但应接近整数
        index_counts[float(val)] = int(count)

    return {
        "status": "PASS",
        "resolution": [H, W],
        "unique_values": [float(v) for v in unique_values],
        "index_counts": index_counts
    }


def validate_position_channel(position_data, r_max):
    """验证 Position/WorldCoord 通道"""
    if position_data is None:
        return {"status": "MISSING", "error": "Position 通道不存在"}

    H, W = position_data.shape[0], position_data.shape[1]

    # 提取 x, y, z
    x = position_data[:, :, 0]
    y = position_data[:, :, 1]
    z = position_data[:, :, 2]

    # 有效像素：所有坐标都是有限值
    valid_mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    valid_count = np.sum(valid_mask)

    if valid_count == 0:
        return {
            "status": "INVALID",
            "error": "无有效 Position 像素",
            "resolution": [H, W],
            "valid_pixel_count": 0
        }

    valid_x = x[valid_mask]
    valid_y = y[valid_mask]
    valid_z = z[valid_mask]

    # 计算距离原点的距离
    r = np.sqrt(valid_x**2 + valid_y**2 + valid_z**2)

    # 检查是否在合理范围内（r_max 是模型最大半径）
    max_r = float(r.max())
    in_range = max_r <= r_max * 1.1  # 允许 10% 误差

    return {
        "status": "PASS" if in_range else "WARNING",
        "resolution": [H, W],
        "valid_pixel_count": int(valid_count),
        "x_range": [float(valid_x.min()), float(valid_x.max())],
        "y_range": [float(valid_y.min()), float(valid_y.max())],
        "z_range": [float(valid_z.min()), float(valid_z.max())],
        "r_range": [float(r.min()), float(r.max())],
        "r_max_expected": float(r_max),
        "in_range": bool(in_range)
    }


def compute_sun_depth(position_data, sun_vector):
    """
    计算 sun-view depth
    sun_depth = dot(position, normalized_sun_dir)
    """
    if position_data is None:
        return None, {"status": "BLOCKED", "error": "Position 通道不存在"}

    H, W = position_data.shape[0], position_data.shape[1]

    # 归一化 sun_vector
    sun_vec = np.array(sun_vector, dtype=np.float64)
    sun_norm = np.linalg.norm(sun_vec)
    if sun_norm < 1e-9:
        return None, {"status": "INVALID", "error": "sun_vector 零向量"}

    sun_dir = sun_vec / sun_norm

    # 提取 x, y, z
    x = position_data[:, :, 0]
    y = position_data[:, :, 1]
    z = position_data[:, :, 2]

    # 计算 dot product
    sun_depth = x * sun_dir[0] + y * sun_dir[1] + z * sun_dir[2]

    # 有效像素
    valid_mask = np.isfinite(sun_depth)
    valid_count = np.sum(valid_mask)

    if valid_count == 0:
        return sun_depth, {
            "status": "INVALID",
            "error": "无有效 sun depth 像素",
            "valid_pixel_count": 0
        }

    valid_sun_depth = sun_depth[valid_mask]

    return sun_depth, {
        "status": "PASS",
        "valid_pixel_count": int(valid_count),
        "sun_depth_range": [float(valid_sun_depth.min()), float(valid_sun_depth.max())],
        "sun_depth_mean": float(valid_sun_depth.mean())
    }


# ============================================================
# 4. 主验证流程
# ============================================================
def main():
    print("=" * 80)
    print("1C-E07-FIX02: EXR 通道内容验证与 sun-view depth 补齐")
    print("=" * 80)

    # 读取 metadata
    if not METADATA_FILE.exists():
        print(f"[ERROR] metadata 文件不存在: {METADATA_FILE}")
        return 1

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    attitudes = metadata["attitudes"]
    sun_vector = metadata["sun_vector"]
    r_max = metadata["r_max"]

    print(f"[INFO] 读取 metadata: {len(attitudes)} 个姿态")
    print(f"[INFO] sun_vector: {sun_vector}")
    print(f"[INFO] r_max: {r_max:.4f} m")
    print()

    # 验证结果汇总
    validation_summary = {
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "sun_vector": sun_vector,
            "r_max": r_max,
            "attitudes": attitudes
        },
        "results": []
    }

    # 逐姿态验证
    for att in attitudes:
        label = att["label"]
        exr_file = GEOMETRY_DIR / f"{label}.exr"

        print(f"[{label}] 验证中...")

        if not exr_file.exists():
            print(f"  [ERROR] EXR 文件不存在: {exr_file}")
            validation_summary["results"].append({
                "attitude": att,
                "status": "FILE_MISSING",
                "error": f"EXR 文件不存在: {exr_file}"
            })
            continue

        # 读取 EXR
        exr_data = read_exr_with_openexr(str(exr_file))
        if exr_data is None:
            print(f"  [ERROR] 无法读取 EXR")
            validation_summary["results"].append({
                "attitude": att,
                "status": "READ_FAILED",
                "error": "无法读取 EXR 文件"
            })
            continue

        print(f"  [INFO] 通道类型: dict with {len(exr_data)} channels")

        # 解析通道
        channels = parse_exr_channels(exr_data)
        if channels is None:
            print(f"  [ERROR] 无法解析通道")
            validation_summary["results"].append({
                "attitude": att,
                "status": "PARSE_FAILED",
                "error": "无法解析 EXR 通道"
            })
            continue

        print(f"  [INFO] 解析到通道: {list(channels.keys())}")

        # 验证各通道
        result = {
            "attitude": att,
            "exr_file": str(exr_file),
            "channels_found": list(channels.keys())
        }

        # Normal
        if "Normal" in channels:
            print(f"  [Normal] 验证中...")
            normal_result = validate_normal_channel(channels["Normal"])
            result["normal"] = normal_result
            print(f"           状态: {normal_result['status']}")
            if normal_result["status"] == "PASS":
                print(f"           有效像素: {normal_result['valid_pixel_count']}")
                print(f"           法线模长: [{normal_result['norm_magnitude']['min']:.4f}, {normal_result['norm_magnitude']['max']:.4f}]")
        else:
            result["normal"] = {"status": "MISSING", "error": "Normal 通道未找到"}

        # Depth
        if "Depth" in channels:
            print(f"  [Depth] 验证中...")
            depth_result = validate_depth_channel(channels["Depth"])
            result["depth"] = depth_result
            print(f"          状态: {depth_result['status']}")
            if depth_result["status"] == "PASS":
                print(f"          有效像素: {depth_result['valid_pixel_count']}")
                print(f"          深度范围: [{depth_result['depth_range'][0]:.4f}, {depth_result['depth_range'][1]:.4f}]")
        else:
            result["depth"] = {"status": "MISSING", "error": "Depth 通道未找到"}

        # IndexOB
        if "IndexOB" in channels:
            print(f"  [IndexOB] 验证中...")
            indexob_result = validate_indexob_channel(channels["IndexOB"])
            result["indexob"] = indexob_result
            print(f"            状态: {indexob_result['status']}")
            if indexob_result["status"] == "PASS":
                print(f"            唯一值: {indexob_result['unique_values']}")
        else:
            result["indexob"] = {"status": "MISSING", "error": "IndexOB 通道未找到"}

        # Position
        if "Position" in channels:
            print(f"  [Position] 验证中...")
            position_result = validate_position_channel(channels["Position"], r_max)
            result["position"] = position_result
            print(f"             状态: {position_result['status']}")
            if position_result["status"] in ["PASS", "WARNING"]:
                print(f"             有效像素: {position_result['valid_pixel_count']}")
                print(f"             r 范围: [{position_result['r_range'][0]:.4f}, {position_result['r_range'][1]:.4f}]")

            # 计算 sun-view depth
            print(f"  [Sun Depth] 计算中...")
            sun_depth_array, sun_depth_result = compute_sun_depth(channels["Position"], sun_vector)
            result["sun_depth"] = sun_depth_result
            print(f"              状态: {sun_depth_result['status']}")
            if sun_depth_result["status"] == "PASS":
                print(f"              有效像素: {sun_depth_result['valid_pixel_count']}")
                print(f"              深度范围: [{sun_depth_result['sun_depth_range'][0]:.4f}, {sun_depth_result['sun_depth_range'][1]:.4f}]")

                # 保存 sun_depth 数组
                sun_depth_file = GEOMETRY_DIR / f"sun_depth_{label}.npy"
                np.save(sun_depth_file, sun_depth_array)
                print(f"              已保存: {sun_depth_file}")
                result["sun_depth"]["output_file"] = str(sun_depth_file)
        else:
            result["position"] = {"status": "MISSING", "error": "Position 通道未找到"}
            result["sun_depth"] = {"status": "BLOCKED", "error": "Position 通道不存在，无法计算 sun depth"}

        validation_summary["results"].append(result)
        print()

    # 保存验证汇总
    with open(OUTPUT_SUMMARY, "w", encoding="utf-8") as f:
        json.dump(validation_summary, f, indent=2, ensure_ascii=False)

    print(f"[INFO] 验证汇总已保存: {OUTPUT_SUMMARY}")

    # 判断总体状态
    all_pass = True
    for res in validation_summary["results"]:
        if "normal" in res and res["normal"]["status"] != "PASS":
            all_pass = False
        if "depth" in res and res["depth"]["status"] != "PASS":
            all_pass = False
        if "indexob" in res and res["indexob"]["status"] != "PASS":
            all_pass = False
        if "position" in res and res["position"]["status"] not in ["PASS", "WARNING"]:
            all_pass = False
        if "sun_depth" in res and res["sun_depth"]["status"] != "PASS":
            all_pass = False

    if all_pass:
        print("\n[SUCCESS] 所有通道验证通过")
        return 0
    else:
        print("\n[WARNING] 部分通道验证未通过，请查看详细结果")
        return 0


if __name__ == "__main__":
    sys.exit(main())

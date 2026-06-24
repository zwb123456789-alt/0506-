# -*- coding: utf-8 -*-
"""
attitude_grid.py —— v0.4 姿态网格生成
=====================================
生成 72 yaw × 37 pitch 姿态网格，构建 record_id，处理绘图 seam。

【版本说明】
v0.4 冻结规范：
- yaw ∈ [0°, 355°]，步长 5°，共 72 个（不含 360°）
- pitch ∈ [-90°, 90°]，步长 5°，共 37 个
- 姿态总数：72 × 37 = 2664

【绘图 seam 处理】
- 训练/反演/manifest 使用 72 yaw（0°-355°）
- 绘图 heatmap 时复制 0° 为 360°，得到 73 yaw（0°-360°），避免 seam
- 绘图 seam 只用于画图，不进入训练或 manifest

【record_id 格式】
- 格式：yaw{yyy}_pitch{ppp}，如 yaw045_pitch-030
- yaw 为 3 位无符号整数（000-355）
- pitch 为 4 位有符号整数（-090 到 +090）
"""

import numpy as np
from typing import List, Tuple


# ============================================================
# 1. 姿态网格生成
# ============================================================
def generate_attitude_grid(
    yaw_range: Tuple[int, int] = (0, 355),
    yaw_step: int = 5,
    pitch_range: Tuple[int, int] = (-90, 90),
    pitch_step: int = 5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    生成 yaw×pitch 姿态网格（训练/反演/manifest 用）。

    参数:
        yaw_range: yaw 范围 (start, stop)，inclusive
        yaw_step: yaw 步长
        pitch_range: pitch 范围 (start, stop)，inclusive
        pitch_step: pitch 步长

    返回:
        yaw_grid: 1D array，shape (num_yaw,)
        pitch_grid: 1D array，shape (num_pitch,)

    说明:
        - 默认生成 72 yaw × 37 pitch = 2664 姿态
        - yaw 不含 360°（避免重复）
        - pitch 含 -90° 和 +90°
    """
    yaw_grid = np.arange(yaw_range[0], yaw_range[1] + 1, yaw_step)
    pitch_grid = np.arange(pitch_range[0], pitch_range[1] + 1, pitch_step)

    return yaw_grid, pitch_grid


def generate_attitude_list(
    yaw_range: Tuple[int, int] = (0, 355),
    yaw_step: int = 5,
    pitch_range: Tuple[int, int] = (-90, 90),
    pitch_step: int = 5
) -> List[Tuple[int, int]]:
    """
    生成姿态列表（yaw, pitch）对，用于循环遍历。

    参数:
        同 generate_attitude_grid()

    返回:
        attitudes: List[(yaw, pitch), ...]

    示例:
        ```python
        attitudes = generate_attitude_list()
        print(f"姿态总数: {len(attitudes)}")  # 2664

        for yaw, pitch in attitudes:
            record_id = build_record_id(yaw, pitch)
            # 处理该姿态...
        ```
    """
    yaw_grid, pitch_grid = generate_attitude_grid(yaw_range, yaw_step, pitch_range, pitch_step)

    attitudes = [(int(yaw), int(pitch)) for pitch in pitch_grid for yaw in yaw_grid]

    return attitudes


# ============================================================
# 2. record_id 构建
# ============================================================
def build_record_id(yaw: int, pitch: int) -> str:
    """
    构建 record_id 字符串。

    参数:
        yaw: 偏航角（0-355）
        pitch: 俯仰角（-90 到 90）

    返回:
        record_id: 格式 "yaw{yyy}_pitch{ppp}"

    示例:
        ```python
        build_record_id(45, -30)   # "yaw045_pitch-030"
        build_record_id(0, 0)      # "yaw000_pitch+000"
        build_record_id(355, 90)   # "yaw355_pitch+090"
        ```
    """
    return f"yaw{yaw:03d}_pitch{pitch:+04d}"


def parse_record_id(record_id: str) -> Tuple[int, int]:
    """
    从 record_id 解析出 yaw 和 pitch。

    参数:
        record_id: 格式 "yaw{yyy}_pitch{ppp}"

    返回:
        (yaw, pitch)

    示例:
        ```python
        parse_record_id("yaw045_pitch-030")  # (45, -30)
        parse_record_id("yaw000_pitch+000")  # (0, 0)
        ```
    """
    parts = record_id.split("_")
    yaw = int(parts[0].replace("yaw", ""))
    pitch = int(parts[1].replace("pitch", ""))
    return yaw, pitch


# ============================================================
# 3. 绘图 seam 处理
# ============================================================
def generate_heatmap_grid_with_seam(
    yaw_range: Tuple[int, int] = (0, 355),
    yaw_step: int = 5,
    pitch_range: Tuple[int, int] = (-90, 90),
    pitch_step: int = 5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    生成带 seam 的姿态网格（绘图专用）。

    参数:
        同 generate_attitude_grid()

    返回:
        yaw_grid_with_seam: 1D array，shape (num_yaw + 1,)，含 360°
        pitch_grid: 1D array，shape (num_pitch,)

    说明:
        - 在 yaw 末尾追加 360°（与 0° 相同），用于 heatmap 无缝拼接
        - 绘图时 yaw 从 0° 到 360°（73 个点）
        - 这只用于画图，不进入训练/manifest 姿态网格

    示例:
        ```python
        yaw_grid, pitch_grid = generate_heatmap_grid_with_seam()
        print(len(yaw_grid))  # 73（含 360°）
        print(yaw_grid[-1])   # 360
        ```
    """
    yaw_grid, pitch_grid = generate_attitude_grid(yaw_range, yaw_step, pitch_range, pitch_step)

    # 追加 360° = 0°（绘图 seam）
    yaw_grid_with_seam = np.append(yaw_grid, 360)

    return yaw_grid_with_seam, pitch_grid


def pad_heatmap_data_for_seam(data: np.ndarray, axis: int = 1) -> np.ndarray:
    """
    为 heatmap 数据填充 seam（复制第一列到末尾）。

    参数:
        data: 2D array，shape (num_pitch, num_yaw) 或 (num_yaw, num_pitch)
        axis: yaw 轴的索引（默认 1，即第二个维度）

    返回:
        padded_data: shape (num_pitch, num_yaw + 1) 或 (num_yaw + 1, num_pitch)

    说明:
        - 用于 matplotlib pcolormesh / imshow 绘图
        - 复制第一列（yaw=0°）到末尾（作为 yaw=360°）
        - 避免 heatmap 在 0°-360° 边界处出现 seam

    示例:
        ```python
        # data shape: (37 pitch, 72 yaw)
        ocs_matrix = ...  # shape (37, 72)
        ocs_padded = pad_heatmap_data_for_seam(ocs_matrix, axis=1)
        print(ocs_padded.shape)  # (37, 73)

        # 绘图
        yaw_grid, pitch_grid = generate_heatmap_grid_with_seam()
        plt.pcolormesh(yaw_grid, pitch_grid, ocs_padded)
        ```
    """
    if axis == 1:
        # 复制第一列到末尾
        return np.concatenate([data, data[:, :1]], axis=1)
    elif axis == 0:
        # 复制第一行到末尾
        return np.concatenate([data, data[:1, :]], axis=0)
    else:
        raise ValueError(f"axis 必须为 0 或 1，当前为 {axis}")


# ============================================================
# 4. 姿态网格统计
# ============================================================
def get_attitude_grid_info() -> dict:
    """
    获取当前姿态网格的统计信息。

    返回:
        info: dict，含以下字段:
            - yaw_range: (0, 355)
            - yaw_step: 5
            - num_yaw: 72
            - pitch_range: (-90, 90)
            - pitch_step: 5
            - num_pitch: 37
            - total_attitudes: 2664
            - heatmap_num_yaw_with_seam: 73

    示例:
        ```python
        info = get_attitude_grid_info()
        print(f"姿态总数: {info['total_attitudes']}")
        print(f"绘图 yaw 点数: {info['heatmap_num_yaw_with_seam']}")
        ```
    """
    yaw_grid, pitch_grid = generate_attitude_grid()

    return {
        "yaw_range": (0, 355),
        "yaw_step": 5,
        "num_yaw": len(yaw_grid),
        "pitch_range": (-90, 90),
        "pitch_step": 5,
        "num_pitch": len(pitch_grid),
        "total_attitudes": len(yaw_grid) * len(pitch_grid),
        "heatmap_num_yaw_with_seam": len(yaw_grid) + 1,
    }


# ============================================================
# 5. 便捷函数（使用 config_v0_4）
# ============================================================
def generate_attitude_grid_from_config():
    """
    从 config_v0_4 读取参数，生成姿态网格。

    返回:
        yaw_grid: 1D array
        pitch_grid: 1D array

    说明:
        需要先导入 config_v0_4:
        ```python
        import sys
        sys.path.append("path/to/06_v0.4_code/00_config")
        from attitude_grid import generate_attitude_grid_from_config

        yaw_grid, pitch_grid = generate_attitude_grid_from_config()
        ```
    """
    try:
        from config_v0_4 import YAW_RANGE, YAW_STEP, PITCH_RANGE, PITCH_STEP
    except ImportError:
        raise ImportError(
            "无法导入 config_v0_4。请确保 config_v0_4.py 在 Python 路径中。"
        )

    return generate_attitude_grid(YAW_RANGE, YAW_STEP, PITCH_RANGE, PITCH_STEP)


def generate_attitude_list_from_config():
    """
    从 config_v0_4 读取参数，生成姿态列表。

    返回:
        attitudes: List[(yaw, pitch), ...]
    """
    try:
        from config_v0_4 import YAW_RANGE, YAW_STEP, PITCH_RANGE, PITCH_STEP
    except ImportError:
        raise ImportError(
            "无法导入 config_v0_4。请确保 config_v0_4.py 在 Python 路径中。"
        )

    return generate_attitude_list(YAW_RANGE, YAW_STEP, PITCH_RANGE, PITCH_STEP)


# ============================================================
# 6. 版本记录
# ============================================================
ATTITUDE_GRID_VERSION = "v0.4.0"
ATTITUDE_GRID_CREATED = "2026-06-23"
ATTITUDE_GRID_NOTES = """
v0.4 姿态网格生成工具：
1. 姿态网格：72 yaw × 37 pitch = 2664 姿态（不含 360°）
2. record_id 格式：yaw{yyy}_pitch{ppp}
3. 绘图 seam：复制 0° 为 360°，用于 heatmap 无缝拼接
4. 绘图 seam 只用于画图，不进入训练/manifest

关键函数：
- generate_attitude_grid(): 生成训练/manifest 用姿态网格（72×37）
- generate_attitude_list(): 生成姿态列表，用于循环遍历
- build_record_id(): 构建 record_id 字符串
- generate_heatmap_grid_with_seam(): 生成绘图用姿态网格（73×37）
- pad_heatmap_data_for_seam(): 为 heatmap 数据填充 seam
"""

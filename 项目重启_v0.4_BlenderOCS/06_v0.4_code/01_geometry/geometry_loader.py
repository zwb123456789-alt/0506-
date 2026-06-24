# -*- coding: utf-8 -*-
"""
geometry_loader.py —— v0.4 几何加载工具
=========================================
- 欧拉角 → 旋转矩阵（Z-Y-X 内旋）
- STL 加载与精度抽稀
- 兼容不同 trimesh 版本

【版本说明】
本文件从历史 geometry.py 迁移，保持核心逻辑不变：
1. euler_to_matrix() 函数：Z-Y-X 内旋（M→I）
2. STL 加载：兼容 trimesh.Scene 和 trimesh.Trimesh
3. 网格抽稀：兼容不同 trimesh 版本的 simplify_quadric_decimation 接口

主要改动：
1. 导入路径改为从 config_v0_4 读取
2. 明确 Phase 0 使用 accuracy_level="full"（不抽稀）
"""

import numpy as np
import trimesh
from tqdm import tqdm


# ============================================================
# 1. 欧拉角转旋转矩阵
# ============================================================
def euler_to_matrix(yaw=0.0, pitch=0.0, roll=0.0, degrees=True) -> np.ndarray:
    """
    欧拉角 → 3×3 旋转矩阵（M→I, 内旋 Z-Y-X 顺序）。

    参数:
        yaw: 偏航角（绕 Z 轴旋转）
        pitch: 俯仰角（绕 Y 轴旋转）
        roll: 滚转角（绕 X 轴旋转）
        degrees: True=角度输入，False=弧度输入

    返回:
        R: 3×3 旋转矩阵，从本体坐标系到惯性系的变换 (M→I)

    说明:
        - 内旋顺序：Z-Y-X（yaw → pitch → roll）
        - R = Rz(yaw) @ Ry(pitch) @ Rx(roll)
        - 应用：v_inertial = R @ v_body
    """
    if degrees:
        yaw = np.deg2rad(yaw)
        pitch = np.deg2rad(pitch)
        roll = np.deg2rad(roll)

    # 绕 Z 轴旋转（yaw）
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0.0],
        [np.sin(yaw),  np.cos(yaw), 0.0],
        [0.0,          0.0,         1.0],
    ])

    # 绕 Y 轴旋转（pitch）
    Ry = np.array([
        [np.cos(pitch), 0.0, np.sin(pitch)],
        [0.0,           1.0, 0.0],
        [-np.sin(pitch), 0.0, np.cos(pitch)],
    ])

    # 绕 X 轴旋转（roll）
    Rx = np.array([
        [1.0, 0.0,          0.0],
        [0.0, np.cos(roll), -np.sin(roll)],
        [0.0, np.sin(roll),  np.cos(roll)],
    ])

    return Rz @ Ry @ Rx


# ============================================================
# 2. STL 加载
# ============================================================
def _load_as_mesh(filepath):
    """
    加载 STL/mesh 文件。

    trimesh.load() 有时会返回 trimesh.Scene，
    这里统一转换为 trimesh.Trimesh。

    参数:
        filepath: STL 文件路径

    返回:
        mesh: trimesh.Trimesh 对象

    异常:
        ValueError: 文件中没有可用几何体
        TypeError: 无法将文件加载为 Trimesh
    """
    obj = trimesh.load(filepath, force="mesh")

    if isinstance(obj, trimesh.Scene):
        if len(obj.geometry) == 0:
            raise ValueError(f"文件中没有可用几何体: {filepath}")

        mesh = trimesh.util.concatenate(tuple(obj.geometry.values()))
    else:
        mesh = obj

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"无法将文件加载为 Trimesh: {filepath}")

    return mesh


def _simplify_mesh(mesh, target_faces):
    """
    网格抽稀，兼容不同版本 trimesh 的 simplify_quadric_decimation 接口。

    参数:
        mesh: trimesh.Trimesh 对象
        target_faces: 目标面元数

    返回:
        简化后的 mesh（若失败则返回原 mesh）

    说明:
        不同 trimesh 版本的 API 差异：
        - 部分版本支持位置参数：simplify_quadric_decimation(target_faces)
        - 部分版本要求关键字参数：simplify_quadric_decimation(face_count=target_faces)
        - 部分版本使用 faces 参数：simplify_quadric_decimation(faces=target_faces)
    """
    target_faces = int(target_faces)

    if target_faces <= 0:
        return mesh

    if target_faces >= len(mesh.faces):
        return mesh

    try:
        # 尝试位置参数
        return mesh.simplify_quadric_decimation(target_faces)
    except TypeError:
        try:
            # 尝试 face_count 关键字参数
            return mesh.simplify_quadric_decimation(face_count=target_faces)
        except TypeError:
            try:
                # 尝试 faces 关键字参数
                return mesh.simplify_quadric_decimation(faces=target_faces)
            except Exception as e:
                print(f"\n  [警告] 网格抽稀失败，使用原始网格。原因: {e}")
                return mesh
    except Exception as e:
        print(f"\n  [警告] 网格抽稀失败，使用原始网格。原因: {e}")
        return mesh


# ============================================================
# 3. 批量加载 STL 部件
# ============================================================
def load_meshes(part_files: dict, decimate_ratio: float = 1.0, verbose: bool = True):
    """
    加载 STL 部件并按精度抽稀。

    参数:
        part_files:
            部件 STL 文件字典，格式:
            {
                "part_name": "/path/to/xxx.stl",
                ...
            }

        decimate_ratio:
            面元保留比例（0.0-1.0）
            1.0 = 不抽稀（full accuracy）
            0.5 = 保留 50% 面元
            0.2 = 保留 20% 面元

        verbose:
            是否打印加载过程

    返回:
        meshes: dict[str, trimesh.Trimesh]
            部件名 → mesh 对象

        total_faces: int
            总面元数量

    说明:
        - Phase 0 建议使用 decimate_ratio=1.0（不抽稀）
        - 抽稀只在原始面元数 > 500 且 decimate_ratio < 1.0 时执行
    """
    if verbose:
        print(f"  面元保留比例: {decimate_ratio:.0%}")

    meshes = {}

    iterator = tqdm(part_files.items(), desc="加载STL", ncols=80) if verbose else part_files.items()

    for part_name, filepath in iterator:
        mesh = _load_as_mesh(filepath)

        orig_faces = len(mesh.faces)

        # 按精度抽稀
        if decimate_ratio < 1.0 and orig_faces > 500:
            n_keep = max(10, int(orig_faces * decimate_ratio))
            mesh = _simplify_mesh(mesh, n_keep)

        meshes[part_name] = mesh

        if verbose:
            vr = mesh.vertices.max(axis=0) - mesh.vertices.min(axis=0)

            # iterator 是 tqdm 对象时才有 set_postfix_str
            if hasattr(iterator, "set_postfix_str"):
                iterator.set_postfix_str(
                    f"{len(mesh.faces):,}面(/{orig_faces:,}) "
                    f"{vr.max():.0f}×{vr.min():.0f}mm"
                )

    total_faces = sum(len(m.faces) for m in meshes.values())

    if verbose:
        print(f"\n  [OK] Total faces: {total_faces:,}")
        for name, m in meshes.items():
            print(f"    [{name:15s}] {len(m.faces):,} faces")

    return meshes, total_faces


# ============================================================
# 4. 便捷加载函数（使用 config_v0_4）
# ============================================================
def load_meshes_from_config(accuracy_level: str = "full", verbose: bool = True):
    """
    从 config_v0_4 读取路径和精度级别，加载 STL 部件。

    参数:
        accuracy_level: 精度级别（"fast" | "medium" | "full"）
        verbose: 是否打印加载过程

    返回:
        meshes: dict[str, trimesh.Trimesh]
        total_faces: int

    说明:
        需要先导入 config_v0_4:
        ```python
        import sys
        sys.path.append("path/to/06_v0.4_code/00_config")
        from config_v0_4 import PART_FILES, DECIMATE_RATIO
        from geometry_loader import load_meshes_from_config

        meshes, total_faces = load_meshes_from_config(accuracy_level="full")
        ```
    """
    # 延迟导入，避免循环依赖
    try:
        from config_v0_4 import PART_FILES, DECIMATE_RATIO
    except ImportError:
        raise ImportError(
            "无法导入 config_v0_4。请确保 config_v0_4.py 在 Python 路径中，"
            "或使用 sys.path.append() 添加 00_config 目录。"
        )

    decimate_ratio = DECIMATE_RATIO.get(accuracy_level, 1.0)

    if verbose:
        print(f"  精度级别: {accuracy_level}")

    return load_meshes(PART_FILES, decimate_ratio, verbose)


# ============================================================
# 5. 版本记录
# ============================================================
GEOMETRY_LOADER_VERSION = "v0.4.0"
GEOMETRY_LOADER_CREATED = "2026-06-23"
GEOMETRY_LOADER_NOTES = """
v0.4 几何加载工具主要改动：
1. 从历史 geometry.py 迁移核心加载逻辑
2. euler_to_matrix() 保持不变（Z-Y-X 内旋）
3. load_meshes() 保持 trimesh Scene/Trimesh 兼容和抽稀兼容
4. 新增 load_meshes_from_config() 便捷加载函数
5. Phase 0 建议使用 accuracy_level="full"（不抽稀）
"""

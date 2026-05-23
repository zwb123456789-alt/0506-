# -*- coding: utf-8 -*-
"""
geometry.py —— 几何工具
=========================
- 欧拉角 → 旋转矩阵（Z-Y-X 内旋）
- STL 加载与精度抽稀
"""

import numpy as np
import trimesh
from tqdm import tqdm

from config import PART_FILES, DECIMATE_RATIO, ACCURACY_LEVEL


def euler_to_matrix(yaw=0.0, pitch=0.0, roll=0.0, degrees=True) -> np.ndarray:
    """欧拉角 → 3×3 旋转矩阵（M→I, 内旋 Z-Y-X 顺序）。"""
    if degrees:
        yaw = np.deg2rad(yaw)
        pitch = np.deg2rad(pitch)
        roll = np.deg2rad(roll)

    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0.0],
        [np.sin(yaw),  np.cos(yaw), 0.0],
        [0.0,          0.0,         1.0],
    ])

    Ry = np.array([
        [np.cos(pitch), 0.0, np.sin(pitch)],
        [0.0,           1.0, 0.0],
        [-np.sin(pitch), 0.0, np.cos(pitch)],
    ])

    Rx = np.array([
        [1.0, 0.0,          0.0],
        [0.0, np.cos(roll), -np.sin(roll)],
        [0.0, np.sin(roll),  np.cos(roll)],
    ])

    return Rz @ Ry @ Rx


def _load_as_mesh(filepath):
    """
    加载 STL/mesh 文件。

    trimesh.load() 有时会返回 trimesh.Scene，
    这里统一转换为 trimesh.Trimesh。
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
    """
    target_faces = int(target_faces)

    if target_faces <= 0:
        return mesh

    if target_faces >= len(mesh.faces):
        return mesh

    try:
        # 部分 trimesh 版本支持位置参数
        return mesh.simplify_quadric_decimation(target_faces)
    except TypeError:
        try:
            # 部分 trimesh 版本要求 face_count 关键字参数
            return mesh.simplify_quadric_decimation(face_count=target_faces)
        except TypeError:
            # 部分版本可能叫 faces
            return mesh.simplify_quadric_decimation(faces=target_faces)
    except Exception as e:
        print(f"\n  [警告] 网格抽稀失败，使用原始网格。原因: {e}")
        return mesh


def load_meshes(part_files=None, accuracy_level=None, verbose=True):
    """
    加载 STL 部件并按精度抽稀。

    参数:
        part_files:
            部件 STL 文件字典，格式:
            {
                "part_name": "xxx.stl",
                ...
            }

        accuracy_level:
            精度级别，对应 config.py 中 DECIMATE_RATIO 的键。

        verbose:
            是否打印加载过程。

    返回:
        meshes:
            dict[str, trimesh.Trimesh]

        total_faces:
            int，总面元数量。
    """
    part_files = part_files or PART_FILES
    accuracy_level = accuracy_level or ACCURACY_LEVEL
    dec_ratio = DECIMATE_RATIO.get(accuracy_level, 1.0)

    if verbose:
        print(f"  精度级别: {accuracy_level} | 面元保留: {dec_ratio:.0%}")

    meshes = {}

    iterator = tqdm(part_files.items(), desc="加载STL", ncols=80) if verbose else part_files.items()

    for part_name, filepath in iterator:
        mesh = _load_as_mesh(filepath)

        orig_faces = len(mesh.faces)

        # 按精度抽稀
        if dec_ratio < 1.0 and orig_faces > 500:
            n_keep = max(10, int(orig_faces * dec_ratio))
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
        print(f"\n  ✓ 总面元: {total_faces:,}")
        for name, m in meshes.items():
            print(f"    [{name:15s}] {len(m.faces):,} 面")

    return meshes, total_faces
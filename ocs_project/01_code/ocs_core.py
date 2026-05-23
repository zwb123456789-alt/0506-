# -*- coding: utf-8 -*-
"""
ocs_core.py —— 单姿态 OCS 计算 + 姿态扫描
============================================
- compute_single_attitude: 单姿态 OCS_no_occ / OCS_with_occ
- scan_attitude          : 1D（yaw 一维）/ 2D（yaw×pitch 网格）扫描

【几何约定】
- mesh 保持在本体坐标系 M（不复制、不变换）
- 旋转矩阵 R: M→I；R.T: I→M
- 太阳/探测器方向固定在惯性系 I；扫描时把方向 I→M 反向变换后做射线查询
"""

import numpy as np
from tqdm import tqdm
import sys
import os

# 添加 07_brdf 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from config import (
    EPSILON, UNIT_SCALE, RAY_BATCH,
    SCAN_2D, YAW_RANGE, NUM_YAW, PITCH_RANGE, NUM_PITCH,
    BRDF_MODEL,
)
from materials import get_material
from geometry  import euler_to_matrix
from occlusion import RayForest
from brdf_models import eval_brdf


def compute_single_attitude(original_meshes, ray_forest,
                            sun_dir, det_dir, R,
                            unit_scale=UNIT_SCALE, use_ggx=False):
    """
    单姿态 OCS 计算。

    返回 dict:
        ocs_no_occ, ocs_with_occ, occlusion_ratio,
        visible_faces_no_occ, visible_faces_with_occ,
        part_contrib (按部件细分)
    """
    sun_norm = sun_dir / np.linalg.norm(sun_dir)
    det_norm = det_dir / np.linalg.norm(det_dir)
    R_T = R.T

    part_res = {name: {
        "ocs_no_occ": 0.0, "ocs_with_occ": 0.0,
      "visible_faces_no_occ": 0, "visible_faces_with_occ": 0,
    } for name in original_meshes}

    scale_sq = unit_scale * unit_scale
    sun_dir_M = sun_norm @ R_T
    det_dir_M = det_norm @ R_T

    for mat_name, part_mesh in original_meshes.items():
        normals_M = part_mesh.face_normals
        centers_M = part_mesh.triangles_center

        # ---- 可见性筛选：法向旋到 I 系后与太阳/探测器方向点积 ----
        normals_I = normals_M @ R
        dot_sun   = np.dot(normals_I, sun_norm)
        dot_det   = np.dot(normals_I, det_norm)
        primary_idx = np.where((dot_sun > 0) & (dot_det > 0))[0]
        if len(primary_idx) == 0:
            continue

        normals_PI = normals_I[primary_idx]
        areas_PI   = part_mesh.area_faces[primary_idx]
        cos_i_vec  = np.dot(normals_PI, sun_norm)
        cos_r_vec  = np.dot(normals_PI, det_norm)
        mat        = get_material(mat_name, use_ggx=use_ggx)

        # BRDF 计算（调用统一模块）
        brdf_vec = eval_brdf(normals_PI, sun_norm, det_norm, mat)

        ocs_no = float(np.sum(areas_PI * scale_sq * brdf_vec * cos_i_vec * cos_r_vec))

        # ---- 有遮挡 OCS：射线在 M 系做双向查询 ----
        origins_M = centers_M[primary_idx] + normals_M[primary_idx] * EPSILON
        occ_sun, occ_det = ray_forest.batch_occlusion_dual(
            origins_M, sun_dir_M, det_dir_M, min_hit_distance=EPSILON)
        final_idx = primary_idx[~(occ_sun | occ_det)]

        ocs_with = 0.0
        if len(final_idx) > 0:
            sort_pm = np.sort(primary_idx)
            pos_in_pm = np.searchsorted(sort_pm, final_idx)
            idx_in_pm = np.clip(pos_in_pm, 0, len(primary_idx) - 1)
            valid_mask = (sort_pm[idx_in_pm] == final_idx)

            normals_with   = normals_PI[idx_in_pm[valid_mask]]
            areas_with     = part_mesh.area_faces[final_idx[valid_mask]]
            cos_i_with     = np.dot(normals_with, sun_norm)
            cos_r_with     = np.dot(normals_with, det_norm)

            # BRDF 计算（调用统一模块）
            brdf_with = eval_brdf(normals_with, sun_norm, det_norm, mat)

            ocs_with = float(np.sum(areas_with * scale_sq * brdf_with * cos_i_with * cos_r_with))

        part_res[mat_name]["ocs_no_occ"]            = ocs_no
        part_res[mat_name]["ocs_with_occ"]          = ocs_with
        part_res[mat_name]["visible_faces_no_occ"]  = int(len(primary_idx))
        part_res[mat_name]["visible_faces_with_occ"] = int(len(final_idx))

    total_no   = sum(v["ocs_no_occ"]   for v in part_res.values())
    total_with = sum(v["ocs_with_occ"] for v in part_res.values())
    total_faces_no   = sum(v["visible_faces_no_occ"]   for v in part_res.values())
    total_faces_with = sum(v["visible_faces_with_occ"] for v in part_res.values())

    # 浮点误差保护：遮挡率严格夹到 [0, 1]；ocs_with 不应超过 ocs_no（容忍 1e-6）
    if total_no > 0:
        occ_ratio = 1.0 - (total_with / total_no)
    else:
        occ_ratio = 0.0
    occ_ratio = float(np.clip(occ_ratio, 0.0, 1.0))

    if total_with > total_no * (1.0 + 1e-6) and total_no > 0:
        # 物理不一致警告，但不阻断流程
        print(f"  [警告] OCS_with_occ > OCS_no_occ: with={total_with:.4e}, no={total_no:.4e}")

    return {
        "ocs_no_occ":            total_no,
        "ocs_with_occ":          total_with,
        "occlusion_ratio":       occ_ratio,
        "visible_faces_no_occ":  total_faces_no,
        "visible_faces_with_occ": total_faces_with,
        "part_contrib":          part_res,
    }


# ============================================================
# 多进程 worker（模块级函数，Windows spawn 需要）
# ============================================================
_WORKER_MESHES = None
_WORKER_FOREST = None
_WORKER_SUN    = None
_WORKER_DET    = None


_WORKER_USE_GGX = False


def _worker_init(meshes, sun_norm, det_norm, ray_batch, use_ggx=False):
    """子进程初始化：每进程构建自己的 RayForest（BVH）。"""
    global _WORKER_MESHES, _WORKER_FOREST, _WORKER_SUN, _WORKER_DET, _WORKER_USE_GGX
    _WORKER_MESHES = meshes
    _WORKER_FOREST = RayForest(meshes, batch_size=ray_batch)
    _WORKER_SUN    = sun_norm
    _WORKER_DET    = det_norm
    _WORKER_USE_GGX = use_ggx


def _worker_compute(yp):
    """子进程计算：传入 (yaw, pitch)，返回单姿态结果 dict。"""
    yaw, pitch = yp
    R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0)
    result = compute_single_attitude(
        _WORKER_MESHES, _WORKER_FOREST, _WORKER_SUN, _WORKER_DET, R,
        use_ggx=_WORKER_USE_GGX)
    result["yaw"]   = round(float(yaw),   4)
    result["pitch"] = round(float(pitch), 4)
    result["roll"]  = 0.0
    return result


def scan_attitude(original_meshes, sun_dir, det_dir,
                  scan_mode=None,
                  yaw_range=YAW_RANGE,   num_yaw=NUM_YAW,
                  pitch_range=PITCH_RANGE, num_pitch=NUM_PITCH,
                  n_workers=1, use_ggx=False):
    """
    姿态扫描。
        scan_mode = None  → 用全局 SCAN_2D
        scan_mode = True  → 强制 2D yaw×pitch
        scan_mode = False → 强制 1D yaw-only
        n_workers = 1     → 串行（原行为）
        n_workers > 1     → 多进程并行（每进程自建 BVH）
    """
    scan_2d = scan_mode if scan_mode is not None else SCAN_2D
    sun_norm = sun_dir / np.linalg.norm(sun_dir)
    det_norm = det_dir / np.linalg.norm(det_dir)

    if not scan_2d:
        yaw_angles   = np.linspace(yaw_range[0], yaw_range[1], num_yaw)
        pitch_angles = np.array([0.0])
        mode_tag = f"1D yaw {yaw_range[0]}°–{yaw_range[1]}°, {num_yaw}点"
    else:
        yaw_angles   = np.linspace(yaw_range[0], yaw_range[1], num_yaw)
        pitch_angles = np.linspace(pitch_range[0], pitch_range[1], num_pitch)
        mode_tag = (f"2D yaw {yaw_range[0]}°–{yaw_range[1]}°({num_yaw}点)"
                    f" × pitch {pitch_range[0]}°–{pitch_range[1]}°({num_pitch}点)"
                    f" = {num_yaw * num_pitch} 姿态")

    total_points = len(yaw_angles) * len(pitch_angles)
    print(f"\n  太阳方向: {sun_norm}")
    print(f"  探测器方向: {det_norm}")
    print(f"  扫描模式: {mode_tag}")
    print(f"  遮挡检测: AABB 粗筛 + face-level 光追 (batch={RAY_BATCH})")
    print(f"  并行进程: {n_workers}")
    print("-" * 70)

    pose_list = list(zip(
        np.repeat(yaw_angles, len(pitch_angles)),
        np.tile(pitch_angles, len(yaw_angles)),
    ))

    # ---- 串行路径（保留原行为，便于对照 / 调试） ----
    if n_workers <= 1:
        ray_forest = RayForest(original_meshes, batch_size=RAY_BATCH)
        scan_data = []
        pbar = tqdm(
            pose_list,
            desc=f"{'2D' if scan_2d else '1D'} 姿态扫描",
            ncols=100,
            total=total_points,
        )
        for yaw, pitch in pbar:
            R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0)
            result = compute_single_attitude(
                original_meshes, ray_forest, sun_norm, det_norm, R,
                use_ggx=use_ggx)
            result["yaw"]   = round(float(yaw),   4)
            result["pitch"] = round(float(pitch), 4)
            result["roll"]  = 0.0
            scan_data.append(result)
            pbar.set_postfix_str(
                f"OCS={result['ocs_with_occ']:.3e}  "
                f"ratio={result['occlusion_ratio']:.1%}  "
                f"面={result['visible_faces_with_occ']:,}"
            )
        return scan_data

    # ---- 多进程路径 ----
    from multiprocessing import Pool

    # chunksize 取每进程约 4 批，摊薄 IPC 开销
    chunksize = max(1, total_points // (n_workers * 4))

    scan_data = []
    with Pool(
        processes=n_workers,
        initializer=_worker_init,
        initargs=(original_meshes, sun_norm, det_norm, RAY_BATCH, use_ggx),
    ) as pool:
        pbar = tqdm(
            pool.imap(_worker_compute, pose_list, chunksize=chunksize),
            desc=f"{'2D' if scan_2d else '1D'} 姿态扫描×{n_workers}",
            ncols=100,
            total=total_points,
        )
        for result in pbar:
            scan_data.append(result)
            pbar.set_postfix_str(
                f"OCS={result['ocs_with_occ']:.3e}  "
                f"ratio={result['occlusion_ratio']:.1%}  "
                f"面={result['visible_faces_with_occ']:,}"
            )

    return scan_data

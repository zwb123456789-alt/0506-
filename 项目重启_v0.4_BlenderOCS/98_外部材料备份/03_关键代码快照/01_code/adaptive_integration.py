# -*- coding: utf-8 -*-
"""
adaptive_integration.py —— A 端 sub-face 自适应 BRDF 积分
==========================================================
解决 face-center 采样对窄镜面峰（n=80）的结构性缺陷。

方法：
1. 计算顶点法线（相邻面面积加权平均）
2. 面内用重心坐标插值顶点法线，模拟曲面法线场
3. 自适应剖分：检测面内 NoH 变幅，在镜面峰区域递归细分
4. 子面中心用插值法线评估 BRDF，面积加权求和

判据（可调）：
- max(NoH_vertices) > NOH_HIGH (默认 0.96) 且 range > NOH_RANGE (默认 0.001) → 剖分
- 最大深度 MAX_DEPTH (默认 5，4^5=1024 子面/原面)
- 最小面积 MIN_AREA_MM2 (默认 0.01 mm²)，小于此面积不再剖分

用法：
    from adaptive_integration import compute_vertex_normals, compute_ocs_adaptive
"""

import numpy as np


# ---- 默认阈值 ----
DEFAULT_MAX_DEPTH      = 5
DEFAULT_NOH_HIGH       = 0.96
DEFAULT_NOH_RANGE      = 0.001
DEFAULT_MIN_AREA_MM2   = 0.01


def compute_vertex_normals(mesh):
    """
    面积加权平均相邻面法线，得到顶点法线（本体系 M）。

    参数:
        mesh: trimesh.Trimesh

    返回:
        (V, 3) float64 单位法线
    """
    vertices = mesh.vertices
    faces = mesh.faces
    face_normals = mesh.face_normals.astype(np.float64)
    face_areas = mesh.area_faces.astype(np.float64)

    n_vertices = len(vertices)
    vn = np.zeros((n_vertices, 3), dtype=np.float64)

    for fi in range(len(faces)):
        f = faces[fi]
        w = face_areas[fi]
        wn = face_normals[fi] * w
        vn[f[0]] += wn
        vn[f[1]] += wn
        vn[f[2]] += wn

    norms = np.linalg.norm(vn, axis=1, keepdims=True)
    norms = np.where(norms > 1e-10, norms, 1.0)
    return vn / norms


# ============================================================
# 递归自适应积分
# ============================================================
def _midpoint(va, vb, na, nb):
    """边中点位置 + 插值法线（归一化）。"""
    vm = (va + vb) * 0.5
    nm = na + nb
    n = np.linalg.norm(nm)
    if n > 1e-10:
        nm /= n
    else:
        nm = na.copy()
    return vm, nm


def _integrate_face_recursive(v0, v1, v2, n0, n1, n2, area_mm2,
                               sun, det, half, mat,
                               depth, max_depth, noh_high, noh_range_thr, min_area):
    """
    递归自适应 BRDF 积分。

    返回:
        (ocs_mm2, n_subdivisions): ocs 贡献（mm² 单位）与本面及其子树中的剖分次数
    """
    # ---- 顶点 NoH ----
    noh0 = max(float(np.dot(n0, half)), 0.0)
    noh1 = max(float(np.dot(n1, half)), 0.0)
    noh2 = max(float(np.dot(n2, half)), 0.0)
    noh_max = max(noh0, noh1, noh2)
    noh_rng = noh_max - min(noh0, noh1, noh2)

    # ---- 剖分判据 ----
    if (depth < max_depth
            and area_mm2 > min_area
            and noh_max > noh_high
            and noh_rng > noh_range_thr):

        v01, n01 = _midpoint(v0, v1, n0, n1)
        v12, n12 = _midpoint(v1, v2, n1, n2)
        v20, n20 = _midpoint(v2, v0, n2, n0)
        sub_a = area_mm2 * 0.25
        d_next = depth + 1
        nd = 1  # 本次剖分

        o0, s0 = _integrate_face_recursive(v0,  v01, v20, n0,  n01, n20, sub_a,
                                            sun, det, half, mat,
                                            d_next, max_depth, noh_high, noh_range_thr, min_area)
        o1, s1 = _integrate_face_recursive(v1,  v12, v01, n1,  n12, n01, sub_a,
                                            sun, det, half, mat,
                                            d_next, max_depth, noh_high, noh_range_thr, min_area)
        o2, s2 = _integrate_face_recursive(v2,  v20, v12, n2,  n20, n12, sub_a,
                                            sun, det, half, mat,
                                            d_next, max_depth, noh_high, noh_range_thr, min_area)
        o3, s3 = _integrate_face_recursive(v01, v12, v20, n01, n12, n20, sub_a,
                                            sun, det, half, mat,
                                            d_next, max_depth, noh_high, noh_range_thr, min_area)
        return (o0 + o1 + o2 + o3, nd + s0 + s1 + s2 + s3)

    # ---- 叶节点：面中心 + 插值法线 ----
    nc = n0 + n1 + n2
    nn = np.linalg.norm(nc)
    if nn > 1e-10:
        nc = nc / nn
    else:
        nc = n0.copy()

    NoL = max(float(np.dot(nc, sun)), 0.0)
    NoV = max(float(np.dot(nc, det)), 0.0)

    if NoL <= 0.0 or NoV <= 0.0:
        return (0.0, 0)

    NoH = max(float(np.dot(nc, half)), 0.0)
    f_r = mat["rho_d"] / np.pi + mat["rho_s"] * (NoH ** mat["n"])

    return (float(area_mm2 * f_r * NoL * NoV), 0)


# ============================================================
# 顶层接口
# ============================================================
def compute_ocs_adaptive(mesh, vertex_normals_M, sun_norm, det_norm, R, mat,
                          max_depth=DEFAULT_MAX_DEPTH,
                          noh_high=DEFAULT_NOH_HIGH,
                          noh_range_thr=DEFAULT_NOH_RANGE,
                          min_area_mm2=DEFAULT_MIN_AREA_MM2):
    """
    对单个部件做自适应 BRDF 积分（无遮挡）。

    参数:
        mesh:              trimesh.Trimesh
        vertex_normals_M:  (V, 3) 顶点法线（本体坐标系 M）
        sun_norm, det_norm: 惯性系单位方向 (3,)
        R:                 (3,3) 旋转矩阵 M→I
        mat:               材料参数 dict
        max_depth:         最大递归深度
        noh_high:          NoH 上阈值
        noh_range_thr:     NoH 变幅阈值
        min_area_mm2:      最小剖分面积 (mm²)

    返回 dict:
        ocs_no_occ, n_faces_visible, n_faces_checked,
        n_subdivisions, n_leaf_samples
    """
    faces = mesh.faces
    face_areas_mm2 = mesh.area_faces
    face_normals_M = mesh.face_normals
    vertices_M = mesh.vertices

    # 半程向量（惯性系）
    half_vec = sun_norm + det_norm
    hn = np.linalg.norm(half_vec)
    half_vec = half_vec / hn if hn > 1e-10 else sun_norm.copy()

    # ---- 可见性初筛（面中心法线） ----
    normals_I = face_normals_M @ R
    dot_sun = np.dot(normals_I, sun_norm)
    dot_det = np.dot(normals_I, det_norm)
    visible_idx = np.where((dot_sun > 0) & (dot_det > 0))[0]

    n_visible = len(visible_idx)
    if n_visible == 0:
        return {"ocs_no_occ": 0.0, "n_faces_visible": 0,
                "n_faces_checked": 0, "n_subdivisions": 0,
                "n_leaf_samples": 0}

    # ---- 变换顶点位置 & 法线到惯性系 ----
    vertices_I = vertices_M @ R                           # (V, 3)
    vertex_normals_I = vertex_normals_M @ R               # (V, 3)
    vn_norm = np.linalg.norm(vertex_normals_I, axis=1, keepdims=True)
    vn_norm = np.where(vn_norm > 1e-10, vn_norm, 1.0)
    vertex_normals_I = vertex_normals_I / vn_norm

    ocs_mm2 = 0.0
    n_checked = 0
    n_subdiv = 0
    n_leaf = 0

    for fi in visible_idx:
        fv = faces[fi]
        area = float(face_areas_mm2[fi])

        v0, v1, v2 = vertices_I[fv]
        n0, n1, n2 = vertex_normals_I[fv]

        ocs_f, ns = _integrate_face_recursive(
            v0, v1, v2, n0, n1, n2, area,
            sun_norm, det_norm, half_vec, mat,
            0, max_depth, noh_high, noh_range_thr, min_area_mm2)

        ocs_mm2 += ocs_f
        n_subdiv += ns
        # 叶节点数 = 1 + 3*剖分次数（每剖分一次 1 面 → 4 面，净增 3）
        n_leaf += 1 + 3 * ns
        n_checked += 1

    ocs_m2 = ocs_mm2 * 1e-6  # mm² → m²

    return {
        "ocs_no_occ":          float(ocs_m2),
        "n_faces_visible":    n_visible,
        "n_faces_checked":    n_checked,
        "n_subdivisions":     n_subdiv,
        "n_leaf_samples":     n_leaf,
    }


# ============================================================
# Step 7b：EXR pixel-level 统一积分（A/B 共享几何源）
# ============================================================
def compute_ocs_from_exr(exr_path, sun_dir, det_dir, materials,
                          part_pass_index, resolution, r_max):
    """
    从 Blender MULTILAYER EXR 逐像素计算 per-part OCS。

    与 brdf_postprocess.py 使用完全相同的几何数据（法线/深度/IndexOB），
    因此 A/B 两端可见性语义完全一致。

    参数:
        exr_path:         EXR 文件路径
        sun_dir, det_dir: 惯性系单位方向 (3,)
        materials:        {part_name: {rho_d, rho_s, n}}
        part_pass_index:  {part_name: pass_index}
        resolution:       渲染分辨率
        r_max:            包围球半径 (m)

    返回:
        dict: {
            ocs_total: float,
            parts: {part_name: float},
            pixels: {part_name: int},
            radiance: (H, W) 数组（不含 pixel_area 的 f_r * NoL）,
        }
    """
    import os as _os
    import sys as _sys

    # 延迟导入 brdf_postprocess（避免循环依赖，此函数仅在需要 EXR 路径时调用）
    _brdf_pp_dir = _os.path.join(_os.path.dirname(__file__), "..", "02_blender")
    _brdf_pp_dir = _os.path.abspath(_brdf_pp_dir)
    if _brdf_pp_dir not in _sys.path:
        _sys.path.insert(0, _brdf_pp_dir)

    from brdf_postprocess import (
        read_multilayer_exr, compute_radiance_image, integrate_ocs,
    )

    ortho_scale = 2.2 * r_max
    pixel_area = (ortho_scale / resolution) ** 2

    layers = read_multilayer_exr(exr_path)
    rad, mask_obj, part_pixels = compute_radiance_image(
        layers, sun_dir, det_dir, materials, part_pass_index)
    ocs_total = integrate_ocs(rad, pixel_area)

    # per-part OCS
    idx = layers["IndexOB"].astype(np.int32)
    part_ocs = {}
    for pn, pid in part_pass_index.items():
        m = mask_obj & (idx == pid)
        part_ocs[pn] = float(np.sum(rad[m]) * pixel_area) if m.any() else 0.0

    return {
        "ocs_total": ocs_total,
        "parts": part_ocs,
        "pixels": part_pixels,
        "radiance": rad,
    }

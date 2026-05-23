# -*- coding: utf-8 -*-
"""
occlusion.py —— 遮挡检测
========================
两层混合策略：
    第一层  AABB 包围盒批量预过滤（O(1)，极小内存）
    第二层  单部件 mesh 光线追踪精检（face-level, intersects_location + hit distance 过滤）

【性能要点】
- BVH 与 AABB 只在 RayForest.__init__ 时构建一次，全姿态复用。
- mesh 始终保持在本体坐标系（M），扫描循环只对射线做 I→M 反向变换。
- 使用 hit distance 过滤起始点自相交，允许同部件内真实遮挡检测。
"""

import numpy as np

from config import RAY_BATCH

# ---- Embree 加速后端（可选）----
# 安装：pip install embreex   （或旧版 pyembree）
# 未装时回退到 trimesh 默认纯 Python BVH，语义完全一致，仅速度差异。
try:
    from trimesh.ray.ray_pyembree import RayMeshIntersector as _EmbreeIntersector
    _HAS_EMBREE = True
except Exception:
    _EmbreeIntersector = None
    _HAS_EMBREE = False


def embree_available() -> bool:
    """外部可查询当前是否启用 Embree（用于日志打印）。"""
    return _HAS_EMBREE


class AABBOccluder:
    """单部件 AABB 包围盒，Slab Method。"""

    def __init__(self, vertices, padding=2.0):
        self.min_pt = vertices.min(axis=0) - padding
        self.max_pt = vertices.max(axis=0) + padding

    def batch_aabb_check(self, origins, direction):
        """批量 AABB 预判：(N,3) origins → (N,) bool。"""
        inv_d = 1.0 / (direction + 1e-10)
        t1 = (self.min_pt - origins) * inv_d
        t2 = (self.max_pt - origins) * inv_d
        t_enter = np.max(np.minimum(t1, t2), axis=1)
        t_exit  = np.min(np.maximum(t1, t2), axis=1)
        return (t_exit >= t_enter) & (t_exit >= 0.0)


class RayTester:
    """对单个部件 mesh 做 face-level 光线追踪，BVH 预构建一次。

    若环境存在 embreex/pyembree，则走 Embree C++ 光追（10~100× 加速）；
    否则回退 trimesh 默认纯 Python BVH。两者返回语义一致。
    """

    def __init__(self, mesh, batch_size=RAY_BATCH):
        self.mesh = mesh
        self.batch_size = batch_size
        if _HAS_EMBREE:
            self.ray = _EmbreeIntersector(mesh)
        else:
            self.ray = mesh.ray
        # 用 dummy ray 触发 BVH 构建
        _ = self.ray.intersects_any(
            ray_origins=np.zeros((1, 3)),
            ray_directions=np.array([[1.0, 0.0, 0.0]]),
        )


class RayForest:
    """
    多部件光线追踪森林。BVH/AABB 全部预构建，仅做查询。

    接口约定：所有射线必须与 mesh 处于同一坐标系（本体 M 系）。
    调用方负责把惯性系方向通过 R.T 反向变换到 M 系。
    """

    def __init__(self, meshes, batch_size=RAY_BATCH):
        self.meshes = meshes
        self.batch_size = batch_size
        self.ray_testers = {}
        self._aabbs = {}
        for name, mesh in meshes.items():
            self.ray_testers[name] = RayTester(mesh, batch_size=batch_size)
            self._aabbs[name]      = AABBOccluder(mesh.vertices)

    def batch_occlusion_dual(self, origins, dir1, dir2, min_hit_distance=1e-3):
        """
        同时检测两个方向的遮挡，部件循环只走一次（节省一半开销）。
        使用 hit distance 过滤起始点自相交。

        参数:
            origins: (N,3) 射线起点（单位：mm，本体坐标系 M）
            dir1, dir2: (3,) 两个方向向量（归一化，本体坐标系 M）
            min_hit_distance: 最小命中距离（单位：mm），小于此距离视为自相交

        返回 (N,) bool1, (N,) bool2
        """
        n = len(origins)
        if n == 0:
            return np.zeros(0, dtype=bool), np.zeros(0, dtype=bool)

        # ---- 两方向并行 AABB 粗筛 ----
        aabb_hit1 = np.zeros(n, dtype=bool)
        aabb_hit2 = np.zeros(n, dtype=bool)
        for name, aabb in self._aabbs.items():
            aabb_hit1 = aabb_hit1 | aabb.batch_aabb_check(origins, dir1)
            aabb_hit2 = aabb_hit2 | aabb.batch_aabb_check(origins, dir2)

        if not (np.any(aabb_hit1) or np.any(aabb_hit2)):
            return np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)

        occ1 = np.zeros(n, dtype=bool)
        occ2 = np.zeros(n, dtype=bool)
        bs = self.batch_size

        for name, tester in self.ray_testers.items():
            ah1 = self._aabbs[name].batch_aabb_check(origins, dir1)
            ah2 = self._aabbs[name].batch_aabb_check(origins, dir2)
            if not (np.any(ah1) or np.any(ah2)):
                continue

            cand1 = np.where(ah1)[0]
            cand2 = np.where(ah2)[0]
            n1, n2 = len(cand1), len(cand2)

            r1 = np.zeros(n1, dtype=bool)
            if n1 > 0:
                o1 = origins[cand1]
                d1 = np.broadcast_to(dir1, (n1, 3))
                for ck in range((n1 + bs - 1) // bs):
                    s = ck * bs; e = min(s + bs, n1)
                    try:
                        hit_locs, idx_ray, _ = tester.ray.intersects_location(
                            ray_origins=o1[s:e], ray_directions=d1[s:e])
                        if len(hit_locs) > 0:
                            dists = np.linalg.norm(hit_locs - o1[s:e][idx_ray], axis=1)
                            valid = dists > min_hit_distance
                            if np.any(valid):
                                chunk_occ = np.zeros(e - s, dtype=bool)
                                chunk_occ[idx_ray[valid]] = True
                                r1[s:e] = chunk_occ
                    except Exception:
                        r1[s:e] = False
            occ1[cand1] = r1

            r2 = np.zeros(n2, dtype=bool)
            if n2 > 0:
                o2 = origins[cand2]
                d2 = np.broadcast_to(dir2, (n2, 3))
                for ck in range((n2 + bs - 1) // bs):
                    s = ck * bs; e = min(s + bs, n2)
                    try:
                        hit_locs, idx_ray, _ = tester.ray.intersects_location(
                            ray_origins=o2[s:e], ray_directions=d2[s:e])
                        if len(hit_locs) > 0:
                            dists = np.linalg.norm(hit_locs - o2[s:e][idx_ray], axis=1)
                            valid = dists > min_hit_distance
                            if np.any(valid):
                                chunk_occ = np.zeros(e - s, dtype=bool)
                                chunk_occ[idx_ray[valid]] = True
                                r2[s:e] = chunk_occ
                    except Exception:
                        r2[s:e] = False
            occ2[cand2] = r2

        return occ1, occ2

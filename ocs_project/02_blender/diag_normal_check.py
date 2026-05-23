# -*- coding: utf-8 -*-
"""诊断脚本：对比 EXR Normal pass 法线与 A端预期法线（单帧 yaw=150/pitch=-80）"""

import os
import sys
import io
import json
import numpy as np

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

# --- 路径 ---
PROJECT = r"D:\我的文件\研究生学术\光学项目\0506新"
EXR_PATH = os.path.join(PROJECT, r"结果\模块B_渲染\run_20260518_200741_exact_brdf\yaw150.00_pitch-80.00_0001.exr")
SCAN_JSON = os.path.join(PROJECT, r"结果\模块A_重构\2d_yaw37_pitch19\run_20260512_210716\ocs_scan.json")
STL_DIR = os.path.join(PROJECT, "建模", "真实模型")

# 加 A端模块路径
sys.path.insert(0, os.path.join(PROJECT, "ocs_project", "01_code"))
sys.path.insert(0, os.path.join(PROJECT, "ocs_project", "07_brdf"))

# --- 读 EXR ---
import OpenEXR
import Imath

print("=" * 70)
print("读取 EXR ...")
f = OpenEXR.InputFile(EXR_PATH)
h = f.header()
dw = h["dataWindow"]
W = dw.max.x - dw.min.x + 1
H = dw.max.y - dw.min.y + 1
print(f"  分辨率: {W} × {H}")
print(f"  通道: {list(h['channels'].keys())}")

raw = {}
for ch in h["channels"].keys():
    buf = f.channel(ch, Imath.PixelType(Imath.PixelType.FLOAT))
    raw[ch] = np.frombuffer(buf, dtype=np.float32).reshape(H, W)

N_img = np.stack([raw["Normal.X"], raw["Normal.Y"], raw["Normal.Z"]], axis=-1).astype(np.float64)
depth = raw["Depth.V"].astype(np.float64)
idx   = raw["IndexOB.V"].astype(np.int32)

# 法线归一化
n_norm = np.linalg.norm(N_img, axis=-1, keepdims=True)
n_norm = np.where(n_norm > 1e-8, n_norm, 1.0)
N_img = N_img / n_norm

# 物体像素
mask_obj = (depth < 1e9) & (idx > 0)
N_obj = N_img[mask_obj]
idx_obj = idx[mask_obj]
print(f"  物体像素数: {len(N_obj)}")

# --- 读 metadata ---
meta_path = os.path.join(os.path.dirname(EXR_PATH), "render_metadata.json")
with open(meta_path, "r", encoding="utf-8") as f:
    meta = json.load(f)
sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
det_dir = np.array(meta["det_direction"], dtype=np.float64)
sun_dir /= np.linalg.norm(sun_dir)
det_dir /= np.linalg.norm(det_dir)
r_max = float(meta["r_max"])
res = int(meta["resolution"])

print(f"\n  sun_dir = {sun_dir}")
print(f"  det_dir = {det_dir}")
print(f"  r_max   = {r_max:.4f} m")
print(f"  res     = {res}")

# --- 每部件法线统计 ---
PART_NAMES = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}
MATERIALS = {
    "jinshuzhuti":    {"rho_d": 0.20, "rho_s": 0.60, "n": 80},
    "taiyangnengban": {"rho_d": 0.15, "rho_s": 0.10, "n": 20},
    "yinshenban":     {"rho_d": 0.08, "rho_s": 0.02, "n": 10},
}

print("\n" + "=" * 70)
print("EXR Normal 统计（按部件）")
print("-" * 70)

for pid, pname in PART_NAMES.items():
    m = idx_obj == pid
    if m.sum() == 0:
        print(f"\n  [{pname}] 无像素")
        continue
    Np = N_obj[m]
    # 平均法线方向
    avg_N = Np.mean(axis=0)
    avg_N /= np.linalg.norm(avg_N)
    # 主导方向（直方图峰值对应的方向，用球坐标近似）
    # 转为球坐标 (theta, phi)
    theta = np.arccos(np.clip(Np[:, 2], -1, 1))  # polar angle from +Z
    phi   = np.arctan2(Np[:, 1], Np[:, 0])        # azimuth from +X
    # 找到 theta/phi 的众数区域（最密集的 10% 区域）
    # 简单方法：用均值方向和散布
    dot_avg = np.abs(np.dot(Np, avg_N))

    print(f"\n  [{pname}] 像素数={m.sum()}")
    print(f"    平均法线: [{avg_N[0]:+.4f}, {avg_N[1]:+.4f}, {avg_N[2]:+.4f}]")
    print(f"    法线散布 (std): X={Np[:,0].std():.3f}, Y={Np[:,1].std():.3f}, Z={Np[:,2].std():.3f}")
    print(f"    与均值的内积: mean={dot_avg.mean():.4f}, median={np.median(dot_avg):.4f}")

    # 法线方向球坐标统计
    print(f"    theta (from +Z): mean={np.degrees(theta.mean()):.1f}°,  std={np.degrees(theta.std()):.1f}°")
    print(f"    phi   (from +X): mean={np.degrees(phi.mean()):.1f}°,  std={np.degrees(phi.std()):.1f}°")

# --- 全局法线分布：用少量 bin 找主要方向 ---
print("\n" + "=" * 70)
print("全物体法线球坐标分布（前 10 bin）")
print("-" * 70)
theta_all = np.arccos(np.clip(N_obj[:, 2], -1, 1))
phi_all   = np.arctan2(N_obj[:, 1], N_obj[:, 0])
# 将 theta/phi 离散化
n_bins_t = 18  # 每 10°
n_bins_p = 36  # 每 10°
t_edges = np.linspace(0, np.pi, n_bins_t + 1)
p_edges = np.linspace(-np.pi, np.pi, n_bins_p + 1)
H2d, _, _ = np.histogram2d(theta_all, phi_all, bins=[t_edges, p_edges])
# 找 top bin
flat_idx = np.argsort(H2d.ravel())[::-1]
for rank, fi in enumerate(flat_idx[:10]):
    ti, pi = np.unravel_index(fi, H2d.shape)
    count = int(H2d[ti, pi])
    t_c = 0.5 * (t_edges[ti] + t_edges[ti+1])
    p_c = 0.5 * (p_edges[pi] + p_edges[pi+1])
    # 转回直角坐标
    nx = np.sin(t_c) * np.cos(p_c)
    ny = np.sin(t_c) * np.sin(p_c)
    nz = np.cos(t_c)
    pct = 100.0 * count / len(N_obj)
    print(f"  #{rank+1}: N=[{nx:+.3f}, {ny:+.3f}, {nz:+.3f}]  "
          f"theta={np.degrees(t_c):5.1f}°  phi={np.degrees(p_c):+6.1f}°  "
          f"pixels={count} ({pct:.1f}%)")

# --- A端：计算同姿态下的预期法线 ---
print("\n" + "=" * 70)
print("A端：加载 STL，计算 yaw=150/pitch=-80 预期法线")
print("-" * 70)

import trimesh
from geometry import euler_to_matrix

R = euler_to_matrix(yaw=150.0, pitch=-80.0, roll=0.0)
print(f"  R @ yaw=150/pitch=-80:")
print(f"    [{R[0,0]:+.4f} {R[0,1]:+.4f} {R[0,2]:+.4f}]")
print(f"    [{R[1,0]:+.4f} {R[1,1]:+.4f} {R[1,2]:+.4f}]")
print(f"    [{R[2,0]:+.4f} {R[2,1]:+.4f} {R[2,2]:+.4f}]")

# 验证 sun/det 方向旋转到 M 系
sun_n = sun_dir
det_n = det_dir
R_T = R.T
sun_M = sun_n @ R_T
det_M = det_n @ R_T
print(f"\n  sun 在 M 系: [{sun_M[0]:+.4f}, {sun_M[1]:+.4f}, {sun_M[2]:+.4f}]")
print(f"  det 在 M 系: [{det_M[0]:+.4f}, {det_M[1]:+.4f}, {det_M[2]:+.4f}]")

for part_name, fname in [("jinshuzhuti", "jinshuzhuti.stl"),
                          ("taiyangnengban", "taiyangnengban.stl"),
                          ("yinshenban", "yinshenban.stl")]:
    path = os.path.join(STL_DIR, fname)
    mesh = trimesh.load(path)
    N_M = mesh.face_normals  # (F, 3)
    areas = mesh.area_faces
    N_I = N_M @ R  # 模型系 → 惯性系

    # 可见性筛选（与 ocs_core.py 一致）
    dot_sun = np.dot(N_I, sun_n)
    dot_det = np.dot(N_I, det_n)
    vis = (dot_sun > 0) & (dot_det > 0)

    if vis.sum() == 0:
        print(f"\n  [{part_name}] 无可见面元")
        continue

    N_vis = N_I[vis]
    areas_vis = areas[vis]

    # 面积加权平均法线
    avg_N = np.average(N_vis, axis=0, weights=areas_vis)
    avg_N /= np.linalg.norm(avg_N)

    # 主导法线方向（面积加权）
    theta_a = np.arccos(np.clip(N_vis[:, 2], -1, 1))
    phi_a   = np.arctan2(N_vis[:, 1], N_vis[:, 0])

    # 面积加权直方图
    H2d_a, _, _ = np.histogram2d(theta_a, phi_a, bins=[t_edges, p_edges], weights=areas_vis)

    print(f"\n  [{part_name}] 面元数={len(N_M)}, 可见={vis.sum()}")
    print(f"    面积加权平均法线: [{avg_N[0]:+.4f}, {avg_N[1]:+.4f}, {avg_N[2]:+.4f}]")
    print(f"    theta (from +Z): mean={np.degrees(np.average(theta_a, weights=areas_vis)):.1f}°")
    print(f"    phi   (from +X): mean={np.degrees(np.average(phi_a, weights=areas_vis)):.1f}°")

    # Top 3 方向 bin
    flat_idx_a = np.argsort(H2d_a.ravel())[::-1]
    for rank, fi in enumerate(flat_idx_a[:3]):
        ti, pi = np.unravel_index(fi, H2d_a.shape)
        area_in_bin = H2d_a[ti, pi]
        pct = 100.0 * area_in_bin / areas_vis.sum()
        t_c = 0.5 * (t_edges[ti] + t_edges[ti+1])
        p_c = 0.5 * (p_edges[pi] + p_edges[pi+1])
        nx = np.sin(t_c) * np.cos(p_c)
        ny = np.sin(t_c) * np.sin(p_c)
        nz = np.cos(t_c)
        print(f"    #{rank+1}: N=[{nx:+.3f}, {ny:+.3f}, {nz:+.3f}]  "
              f"theta={np.degrees(t_c):5.1f}°  phi={np.degrees(p_c):+6.1f}°  "
              f"area_pct={pct:.1f}%")

# --- 交叉对比：B端像素 vs A端面元，BRDF 等价性检查 ---
print("\n" + "=" * 70)
print("交叉对比：抽取 EXR 20 个随机像素做法线-面元匹配")
print("-" * 70)

from brdf_models import eval_legacy_phong

# 从 EXR 随机取物体像素
rng = np.random.RandomState(42)
sample_idx = rng.choice(len(N_obj), min(20, len(N_obj)), replace=False)

for i, si in enumerate(sample_idx):
    N_pix = N_obj[si]
    pid = idx_obj[si]
    pname = PART_NAMES.get(pid, "?")
    mat = MATERIALS[pname]
    f_r_pix = eval_legacy_phong(N_pix.reshape(1,3), sun_dir.reshape(1,3), det_dir.reshape(1,3),
                                 mat["rho_d"], mat["rho_s"], mat["n"])[0]
    NoL_pix = max(np.dot(N_pix, sun_dir), 0)
    NoV_pix = max(np.dot(N_pix, det_dir), 0)
    rad_pix = f_r_pix * NoL_pix

    # 找 A端最近面元
    pname_a = {"jinshuzhuti": "jinshuzhuti", "taiyangnengban": "taiyangnengban", "yinshenban": "yinshenban"}[pname]
    # 只对比同部件
    mesh_a = trimesh.load(os.path.join(STL_DIR, f"{pname_a}.stl"))
    N_M_a = mesh_a.face_normals
    N_I_a = N_M_a @ R
    # 找与 N_pix 最近的法线
    dots = np.abs(np.dot(N_I_a, N_pix))
    best = int(np.argmax(dots))
    N_best = N_I_a[best]
    f_r_a = eval_legacy_phong(N_best.reshape(1,3), sun_dir.reshape(1,3), det_dir.reshape(1,3),
                               mat["rho_d"], mat["rho_s"], mat["n"])[0]
    NoL_a = max(np.dot(N_best, sun_dir), 0)
    NoV_a = max(np.dot(N_best, det_dir), 0)
    rad_a = f_r_a * NoL_a

    angle = np.degrees(np.arccos(np.clip(np.dot(N_pix, N_best), -1, 1)))
    print(f"  pix#{i:2d} [{pname:15s}] N_pix=[{N_pix[0]:+.3f},{N_pix[1]:+.3f},{N_pix[2]:+.3f}]  "
          f"N_A_best=[{N_best[0]:+.3f},{N_best[1]:+.3f},{N_best[2]:+.3f}]  angle={angle:5.1f}°  "
          f"rad_pix={rad_pix:.4f} rad_A={rad_a:.4f}")

print("\n" + "=" * 70)
print("完成")

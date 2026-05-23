# -*- coding: utf-8 -*-
"""诊断 Normal pass 是世界空间还是视图空间。

测试姿态 yaw=0, pitch=-90, sun=(1,0,0.3) det=(0.5,-1,0.1)。
卫星绕 Y 轴 -90° 后，原 +Z 方向法线在世界空间 → +X。
模块 A 的 OCS 用的是世界空间法线（与 sun/det 都在惯性系点积）。

判定：
  若 Normal pass 是世界空间，主导法线应靠近 (+1,0,0) / (-1,0,0)
  若 Normal pass 是视图空间（相机局部 -Z），需用相机旋转回算

相机方向：det=(0.5,-1,0.1).normalize()，相机位置 = det*5*r_max，朝向 origin
  → 相机本地 -Z = -det_norm
  → 世界 +X 方向，在相机本地坐标 = R_cam_inv @ (1,0,0)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import OpenEXR, Imath
import numpy as np
from collections import Counter

p = sys.argv[1] if len(sys.argv) > 1 else r"d:\我的文件\研究生学术\光学项目\0506新\结果\模块B_渲染\run_20260518_193837_exact_brdf\yaw000.00_pitch-90.00_0001.exr"

f = OpenEXR.InputFile(p)
h = f.header()
dw = h["dataWindow"]
W = dw.max.x - dw.min.x + 1
H = dw.max.y - dw.min.y + 1

def ch(name):
    raw = f.channel(name, Imath.PixelType(Imath.PixelType.FLOAT))
    return np.frombuffer(raw, dtype=np.float32).reshape(H, W)

nx = ch("Normal.X")
ny = ch("Normal.Y")
nz = ch("Normal.Z")
idxob = ch("IndexOB.V")
depth = ch("Depth.V")

# 物体像素掩码（IndexOB > 0 或 Normal 非零）
mask = (idxob > 0)
print(f"object pixels = {mask.sum()} / {mask.size}")

if mask.sum() == 0:
    print("no object pixels -- abort")
    sys.exit(1)

N = np.stack([nx[mask], ny[mask], nz[mask]], axis=-1)  # (M, 3)
norm = np.linalg.norm(N, axis=-1)
print(f"|N| min={norm.min():.4f} max={norm.max():.4f} mean={norm.mean():.4f}")

# 离散化看主导方向
bins = np.round(N * 4) / 4  # 0.25 步长
keys = [tuple(b) for b in bins]
ctr = Counter(keys)
print("\n=== 主导法线方向（前 8） ===")
for v, c in ctr.most_common(8):
    print(f"  N≈{v}  count={c}")

# 分部件统计
print("\n=== 按部件 ===")
for pid in sorted(set(idxob[mask].astype(int).tolist())):
    pmask = mask & (idxob.astype(int) == pid)
    if pmask.sum() == 0:
        continue
    Np = np.stack([nx[pmask], ny[pmask], nz[pmask]], axis=-1)
    Np_mean = Np.mean(axis=0)
    print(f"  part_id={pid}: count={pmask.sum()}  mean_N={Np_mean}")

# 期望（世界空间）
print("\n=== 期望 ===")
print("  yaw=0 / pitch=-90 / Z-Y-X 内旋下：")
print("  原始 +Z 面 → 世界 +X")
print("  原始 +X 面 → 世界 -Z")
print("  原始 +Y 面 → 世界 +Y")
print("  → 若世界空间，主导法线 N 应包含 (+1,0,0)")
print("  → 若视图空间（cam 朝 -det）需要补 R_cam @ N_view")

# 相机参数
det = np.array([0.5, -1.0, 0.1])
det = det / np.linalg.norm(det)
print(f"\n  det_norm = {det}")
print(f"  cam 朝 -det = {-det}")
print(f"  若 Normal 是 view space，世界 +X 对应 view space N = R_cam_inv @ (1,0,0)")

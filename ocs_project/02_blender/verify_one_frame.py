# -*- coding: utf-8 -*-
"""手动重算 yaw=150/pitch=-80 的 OCS_image，并与 module A 对比"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, os.path.abspath(r"d:\我的文件\研究生学术\光学项目\0506新\ocs_project\07_brdf"))
from brdf_models import eval_legacy_phong

import OpenEXR, Imath
import numpy as np

EXR = r"d:\我的文件\研究生学术\光学项目\0506新\结果\模块B_渲染\run_20260518_195501_exact_brdf\yaw180.00_pitch-30.00_0001.exr"
META = r"d:\我的文件\研究生学术\光学项目\0506新\结果\模块B_渲染\run_20260518_195501_exact_brdf\render_metadata.json"

with open(META, encoding="utf-8") as f:
    m = json.load(f)
sun = np.array(m["sun_direction"])
det = np.array(m["det_direction"])
sun /= np.linalg.norm(sun); det /= np.linalg.norm(det)
materials = m["materials"]
r_max = m["r_max"]
res = m["resolution"]
ortho = 2.2 * r_max
pixel_area = (ortho/res)**2
print(f"pixel_area = {pixel_area:.4e} m²")
print(f"sun = {sun}")
print(f"det = {det}")

f = OpenEXR.InputFile(EXR)
h = f.header()
W = h["dataWindow"].max.x - h["dataWindow"].min.x + 1
H = h["dataWindow"].max.y - h["dataWindow"].min.y + 1

def ch(n):
    raw = f.channel(n, Imath.PixelType(Imath.PixelType.FLOAT))
    return np.frombuffer(raw, dtype=np.float32).reshape(H, W).astype(np.float64)

N = np.stack([ch("Normal.X"), ch("Normal.Y"), ch("Normal.Z")], axis=-1)
idx = ch("IndexOB.V").astype(int)
depth = ch("Depth.V")
combined_R = ch("Combined.R")
combined_G = ch("Combined.G")
combined_B = ch("Combined.B")

mask_obj = (depth < 1e9) & (idx > 0)
print(f"\n物体像素 = {int(mask_obj.sum())}")

# 法线归一化
nn = np.linalg.norm(N, axis=-1, keepdims=True)
nn = np.where(nn > 1e-8, nn, 1.0)
N = N / nn

# 按部件分别计算
PART_PASS_INDEX = {"jinshuzhuti":1, "taiyangnengban":2, "yinshenban":3}
ocs_total = 0.0
for pname, pid in PART_PASS_INDEX.items():
    mp = mask_obj & (idx == pid)
    n = int(mp.sum())
    if n == 0:
        print(f"  {pname}: 0 px")
        continue
    Np = N[mp]
    L = np.broadcast_to(sun, Np.shape).copy()
    V = np.broadcast_to(det, Np.shape).copy()
    mat = materials[pname]
    f_r = eval_legacy_phong(Np, L, V, mat["rho_d"], mat["rho_s"], mat["n"])
    NoL = np.maximum(np.einsum("ij,j->i", Np, sun), 0.0)
    NoV = np.maximum(np.einsum("ij,j->i", Np, det), 0.0)
    cos_check = (NoL > 0) & (NoV > 0)
    ocs_part = np.sum(f_r * NoL) * pixel_area  # 当前公式（NoV 抵消）
    # 检查：如果 NoV 不抵消（A 公式直接套）
    ocs_part_fr_NoL_NoV = np.sum(f_r * NoL * NoV) * pixel_area
    print(f"\n  {pname} pid={pid}:")
    print(f"    px={n}, NoL>0&NoV>0={int(cos_check.sum())}")
    print(f"    NoL: min={NoL.min():.3f} max={NoL.max():.3f} mean={NoL.mean():.3f}")
    print(f"    NoV: min={NoV.min():.3f} max={NoV.max():.3f} mean={NoV.mean():.3f}")
    print(f"    f_r: min={f_r.min():.3f} max={f_r.max():.3f} mean={f_r.mean():.3f}")
    print(f"    OCS_part (f_r*NoL*A_pix)        = {ocs_part:.4e}")
    print(f"    OCS_part (f_r*NoL*NoV*A_pix)    = {ocs_part_fr_NoL_NoV:.4e}")
    ocs_total += ocs_part

print(f"\n=== TOTAL ===")
print(f"OCS_image (current) = {ocs_total:.4e}")
print(f"OCS_module_A_occ    = 1.629e-02 (from CSV)")

# 检查 NoL=0 比例（与模块 A vis_no_occ 的关系）
print("\n=== NoL/NoV 分布 ===")
N_all = N[mask_obj]
NoL_all = np.einsum("ij,j->i", N_all, sun)
NoV_all = np.einsum("ij,j->i", N_all, det)
print(f"  全部物体像素: NoL>0 比例={(NoL_all>0).mean():.3f}  NoV>0 比例={(NoV_all>0).mean():.3f}")
print(f"  NoL>0 & NoV>0 比例: {((NoL_all>0)&(NoV_all>0)).mean():.3f}")

# 与 Combined 对比（Cycles 渲染图像应反映 BRDF*光照）
# 注：Cycles 已通过 Principled BSDF 算了一份，但材料映射不同
print("\n=== Combined channel ===")
ratio_test = combined_R[mask_obj].sum() * pixel_area
print(f"  Σ Combined.R · A_pix = {ratio_test:.4e}")
print(f"  这量纲不直接是 OCS，但能粗略判断渲染是否有亮度")

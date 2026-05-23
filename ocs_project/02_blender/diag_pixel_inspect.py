# -*- coding: utf-8 -*-
"""
diag_pixel_inspect.py —— B 端 per-part 像素深度检查
=====================================================
输出每部件像素的法线、NoL、位置等统计，验证 IndexOB 标签合理性。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/02_blender/diag_pixel_inspect.py
"""
import os, sys, json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from brdf_postprocess import read_multilayer_exr, PART_PASS_INDEX, DEPTH_BG_THRESHOLD

EXR_PATH = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块B_渲染", "run_20260519_backface_fix",
    "yaw150.00_pitch-80.00_0001.exr",
))
META_PATH = os.path.join(os.path.dirname(EXR_PATH), "render_metadata.json")

if __name__ == "__main__":
    print("=" * 60)
    print("  B 端 per-part 像素检查")
    print("=" * 60)

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)

    layers = read_multilayer_exr(EXR_PATH)
    N = layers["Normal"].astype(np.float64)
    depth = layers["Depth"]
    idx = layers["IndexOB"].astype(np.int32)
    H, W = N.shape[:2]

    # 归一化法线
    nn = np.linalg.norm(N, axis=-1, keepdims=True)
    nn = np.where(nn > 1e-8, nn, 1.0)
    N = N / nn

    mask_obj = (depth < DEPTH_BG_THRESHOLD) & (idx > 0)
    print(f"  总物体像素: {mask_obj.sum()}")
    print(f"  sun_dir: {sun_dir}")
    print(f"  det_dir: {det_dir}")

    PART_NAMES = {1: "jinshuzhuti", 2: "taiyangnengban", 3: "yinshenban"}

    for pid in [1, 2, 3]:
        pn = PART_NAMES[pid]
        m = mask_obj & (idx == pid)
        n_pix = m.sum()
        if n_pix == 0:
            print(f"\n  [{pn}] 0 pixels")
            continue

        N_part = N[m]  # (M, 3)
        NoL = np.clip(np.einsum("ij,j->i", N_part, sun_dir), 0, None)
        NoV = np.clip(np.einsum("ij,j->i", N_part, det_dir), 0, None)
        H_vec = sun_dir + det_dir
        H_vec /= np.linalg.norm(H_vec)
        NoH = np.clip(np.einsum("ij,j->i", N_part, H_vec), 0, None)

        # 像素在图像中的位置
        yi, xi = np.where(m)
        x_center, y_center = xi.mean(), yi.mean()

        print(f"\n  [{pn}] {n_pix} pixels")
        print(f"    图像质心: x={x_center:.1f} y={y_center:.1f} (of {W}×{H})")
        print(f"    NoL: mean={NoL.mean():.4f} median={np.median(NoL):.4f} "
              f"min={NoL.min():.4f} max={NoL.max():.4f}")
        print(f"    NoV: mean={NoV.mean():.4f} median={np.median(NoV):.4f} "
              f"min={NoV.min():.4f} max={NoV.max():.4f}")
        print(f"    NoH: mean={NoH.mean():.4f} median={np.median(NoH):.4f} "
              f"max={NoH.max():.4f}")
        print(f"    NoL>0 像素: {(NoL>0).sum()} / {n_pix}")
        print(f"    NoV>0 像素: {(NoV>0).sum()} / {n_pix}")
        print(f"    法线均值: [{N_part[:,0].mean():+.3f} {N_part[:,1].mean():+.3f} {N_part[:,2].mean():+.3f}]")
        print(f"    法线标准差: [{N_part[:,0].std():.3f} {N_part[:,1].std():.3f} {N_part[:,2].std():.3f}]")

        # 像素坐标跨度
        print(f"    x范围: [{xi.min()}, {xi.max()}]  y范围: [{yi.min()}, {yi.max()}]")

    # ---- 全局：IndexOB 值分布 ----
    print(f"\n--- IndexOB 值分布 ---")
    obj_pix = idx[mask_obj]
    for v in sorted(set(obj_pix.flatten().tolist())):
        cnt = (obj_pix == v).sum()
        name = PART_NAMES.get(v, f"未知({v})")
        print(f"  IndexOB={v} ({name}): {cnt} pixels")

    print("=" * 60)

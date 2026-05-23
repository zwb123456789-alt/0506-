# -*- coding: utf-8 -*-
"""
verify_pixel_unified.py —— 验证 compute_ocs_from_exr 与 brdf_postprocess 一致
==============================================================================
3 姿态 diffuse-only & full BRDF 对比。

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/02_blender/verify_pixel_unified.py
"""
import os, sys, json, io
import numpy as np

try:
    if sys.stdout.encoding != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from adaptive_integration import compute_ocs_from_exr
from brdf_postprocess import (
    read_multilayer_exr, compute_radiance_image, integrate_ocs,
    PART_PASS_INDEX,
)

EXR_DIR = os.path.normpath(os.path.join(
    PROJECT_ROOT, "结果", "模块B_渲染", "run_20260519_backface_fix"))
META_PATH = os.path.join(EXR_DIR, "render_metadata.json")

ATTITUDES = [(0.0, 0.0), (90.0, -40.0), (150.0, -80.0)]


def fmt_exr_name(yaw, pitch):
    return f"yaw{yaw:06.2f}_pitch{pitch:+06.2f}_0001.exr"


def run_brdf_pp(exr_path, sun_dir, det_dir, materials, res, r_max):
    """使用 brdf_postprocess 现有函数计算"""
    ortho_scale = 2.2 * r_max
    pixel_area = (ortho_scale / res) ** 2
    layers = read_multilayer_exr(exr_path)
    rad, mask_obj, pp = compute_radiance_image(
        layers, sun_dir, det_dir, materials, PART_PASS_INDEX)
    ocs_total = integrate_ocs(rad, pixel_area)
    idx = layers["IndexOB"].astype(np.int32)
    part_ocs = {}
    for pn, pid in PART_PASS_INDEX.items():
        m = mask_obj & (idx == pid)
        part_ocs[pn] = float(np.sum(rad[m]) * pixel_area) if m.any() else 0.0
    return ocs_total, part_ocs, pp


with open(META_PATH, "r", encoding="utf-8") as f:
    meta = json.load(f)

res = meta["resolution"]
r_max = meta["r_max"]
sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
det_dir = np.array(meta["det_direction"], dtype=np.float64)
sun_dir /= np.linalg.norm(sun_dir)
det_dir /= np.linalg.norm(det_dir)
materials_full = meta["materials"]
materials_diff = {pn: {**m, "rho_s": 0.0} for pn, m in materials_full.items()}

print("=" * 80)
print("  compute_ocs_from_exr vs brdf_postprocess 一致性验证")
print("=" * 80)

all_ok = True
for yaw, pitch in ATTITUDES:
    exr_path = os.path.join(EXR_DIR, fmt_exr_name(yaw, pitch))
    print(f"\n--- yaw={yaw}°, pitch={pitch}° ---")

    for tag, mats in [("diffuse", materials_diff), ("full", materials_full)]:
        # 新函数
        r1 = compute_ocs_from_exr(
            exr_path, sun_dir, det_dir, mats, PART_PASS_INDEX, res, r_max)

        # 旧函数
        ocs_total_old, part_ocs_old, pp_old = run_brdf_pp(
            exr_path, sun_dir, det_dir, mats, res, r_max)

        diff_total = abs(r1["ocs_total"] - ocs_total_old)
        ok = diff_total < 1e-12
        if not ok:
            all_ok = False

        print(f"  [{tag:7s}] total: new={r1['ocs_total']:.10f}  "
              f"old={ocs_total_old:.10f}  diff={diff_total:.2e}  {'OK' if ok else 'FAIL'}")

        for pn in ["jinshuzhuti", "taiyangnengban", "yinshenban"]:
            diff_p = abs(r1["parts"][pn] - part_ocs_old[pn])
            if diff_p >= 1e-12:
                all_ok = False
                print(f"           [{pn}] diff={diff_p:.2e} FAIL")

if all_ok:
    print("\n" + "=" * 80)
    print("  全部通过：compute_ocs_from_exr ≡ brdf_postprocess")
    print("=" * 80)
else:
    print("\n  存在差异！")

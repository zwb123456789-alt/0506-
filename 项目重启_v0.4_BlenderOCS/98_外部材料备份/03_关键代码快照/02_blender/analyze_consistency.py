# -*- coding: utf-8 -*-
"""统计 703 帧 OCS_image vs OCS_A_occ 一致性"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import csv
import numpy as np
import json

CSV = r"d:\我的文件\研究生学术\光学项目\0506新\结果\模块B_渲染\run_20260518_200741_exact_brdf\ocs_comparison.csv"

rows = []
with open(CSV, "r", encoding="utf-8") as f:
    rd = csv.DictReader(f)
    for r in rd:
        rows.append(r)

n = len(rows)
ocs_img = np.array([float(r["ocs_image"]) for r in rows])
ocs_a   = np.array([float(r["ocs_module_a"]) for r in rows])
ocs_a_no_occ = np.array([float(r["ocs_module_a_no_occ"]) for r in rows])
rel_err = np.array([float(r["rel_err"]) for r in rows])
abs_err = np.array([float(r["abs_err"]) for r in rows])
occ = np.array([float(r["occlusion_ratio_a"]) for r in rows])
obj_px = np.array([int(r["obj_pixels"]) for r in rows])

print(f"N = {n}")
print(f"\n=== OCS_image (B) ===")
print(f"  min={ocs_img.min():.4e}  max={ocs_img.max():.4e}  mean={ocs_img.mean():.4e}  std={ocs_img.std():.4e}")
print(f"\n=== OCS_module_A (with_occ) ===")
print(f"  min={ocs_a.min():.4e}  max={ocs_a.max():.4e}  mean={ocs_a.mean():.4e}  std={ocs_a.std():.4e}")
print(f"\n=== relative error ===")
qs = [0.05, 0.25, 0.5, 0.75, 0.95]
for q in qs:
    print(f"  q{int(q*100):02d}: {np.quantile(rel_err, q)*100:7.3f}%")
print(f"  mean: {rel_err.mean()*100:7.3f}%")
print(f"  max:  {rel_err.max()*100:7.3f}%")
print(f"  min:  {rel_err.min()*100:7.3f}%")

print(f"\n=== correlation ===")
pearson = np.corrcoef(ocs_img, ocs_a)[0,1]
print(f"  Pearson(OCS_img, OCS_A_occ)    = {pearson:.4f}")
pearson_noocc = np.corrcoef(ocs_img, ocs_a_no_occ)[0,1]
print(f"  Pearson(OCS_img, OCS_A_noocc)  = {pearson_noocc:.4f}")
# Spearman 等价：用 rank
def spearman(x, y):
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    return np.corrcoef(rx, ry)[0,1]
print(f"  Spearman(OCS_img, OCS_A_occ)   = {spearman(ocs_img, ocs_a):.4f}")
print(f"  Spearman(OCS_img, OCS_A_noocc) = {spearman(ocs_img, ocs_a_no_occ):.4f}")

# 比例（B/A）
ratio = ocs_img / np.maximum(ocs_a, 1e-15)
print(f"\n=== ratio OCS_img / OCS_A_occ ===")
print(f"  min={ratio.min():.3f}  max={ratio.max():.3f}  mean={ratio.mean():.3f}  median={np.median(ratio):.3f}")

# 误差与遮挡率的相关
print(f"\n=== rel_err vs occlusion_ratio ===")
mask_valid = ~np.isnan(occ)
print(f"  Pearson(rel_err, occ_ratio) = {np.corrcoef(rel_err[mask_valid], occ[mask_valid])[0,1]:.4f}")

# 写 summary
out = {
    "n": int(n),
    "ocs_image":   {"min": float(ocs_img.min()), "max": float(ocs_img.max()), "mean": float(ocs_img.mean())},
    "ocs_module_a_with_occ": {"min": float(ocs_a.min()), "max": float(ocs_a.max()), "mean": float(ocs_a.mean())},
    "rel_err": {f"q{int(q*100):02d}": float(np.quantile(rel_err, q)) for q in qs} | {
        "mean": float(rel_err.mean()),
        "max": float(rel_err.max()),
        "min": float(rel_err.min()),
    },
    "pearson_with_occ": float(pearson),
    "pearson_no_occ":   float(pearson_noocc),
    "spearman_with_occ": float(spearman(ocs_img, ocs_a)),
    "spearman_no_occ":   float(spearman(ocs_img, ocs_a_no_occ)),
    "ratio_B_over_A_with_occ": {
        "min": float(ratio.min()), "max": float(ratio.max()),
        "mean": float(ratio.mean()), "median": float(np.median(ratio)),
    },
}
import os
out_path = os.path.join(os.path.dirname(CSV), "consistency_summary.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nWrote {out_path}")

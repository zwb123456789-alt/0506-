"""
run_centered_control_12e.py — 实验12e：质心居中控制实验
================================================================================
目的（指导文件 §6）：
  回应 audit（实验10）中 centroid_x 与 yaw 相关 r=0.66 的潜在质疑——
  ResNet image-only 的强性能是否部分依赖目标在画面中的固定框定/质心漂移线索。

设计：
  - 对 phase63 图像按强度质心居中（intensity-weighted centroid），重训 ResNet image-only。
  - 同管线、同 split、同 seeds 同时训练原始（非居中）ResNet image-only 作对照。
  - 5 seeds（>=3）。

不变口径（指导文件 §3）：
  - split 10°→5°（ic.split_coarse_to_fine, coarse_step=10）
  - target encoding [sin(yaw),cos(yaw),sin(pitch),cos(pitch)]
  - great-circle angular error；mean/median/p90/p95/worst/Hit@5/Hit@10
  - OCS 标准化统计只从 train 拟合（本实验为 image-only，无 OCS）

质心实现要求（指导文件 §6）：
  质心必须在线性强度域计算。训练图像存储为 normalized-log1p:
      norm = log1p(10 * raw01) / log1p(10)
  反演线性强度：
      linear = expm1(norm * log1p(10)) / 10
  再做 intensity-weighted centroid，禁止直接在 log1p 图像上算质心解释为强度质心。

判读（不预设结论）：
  - 居中后仍强：clean-image upper bound 不只是质心漂移。
  - 居中后退化：clean-image 性能部分依赖固定框定 → 写入 limitation。

红线：不写 real telescope / operational robustness / fully robust。
"""

import argparse
import csv
import glob
import json
import os
import sys
import time
from datetime import datetime

import numpy as np

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic
import run_resnet_fusion as rf

_IMAGE_DIR = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染",
                          "run_20260528_101944_exact_brdf")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "centered_control_12e")

_LOG10_DEN = np.log1p(10.0)  # 训练图像 log1p 归一化常数


def to_linear(norm_img):
    """normalized-log1p -> 线性强度（与 rf.load_image_array 的逆变换一致）。"""
    return np.expm1(np.clip(norm_img, 0.0, 1.0) * _LOG10_DEN) / 10.0


def compute_centroid_linear(norm_img2d):
    """对单张 (H,W) normalized-log1p 图像，返回线性强度域 intensity-weighted centroid (cx,cy)。"""
    lin = to_linear(norm_img2d)
    total = lin.sum()
    H, W = lin.shape
    if total < 1e-12:
        return (W - 1) / 2.0, (H - 1) / 2.0
    yy, xx = np.indices(lin.shape)
    cx = float((lin * xx).sum() / total)
    cy = float((lin * yy).sum() / total)
    return cx, cy


def shift_to_center(norm_img2d, cx, cy):
    """整数像素平移，使质心 (cx,cy) 移到画面中心；暴露区域填 0（背景）。"""
    H, W = norm_img2d.shape
    dx = int(round((W - 1) / 2.0 - cx))
    dy = int(round((H - 1) / 2.0 - cy))
    out = np.zeros_like(norm_img2d)
    # 源区间 / 目标区间
    xs0, xs1 = max(0, -dx), min(W, W - dx)
    ys0, ys1 = max(0, -dy), min(H, H - dy)
    xd0, xd1 = max(0, dx), min(W, W + dx)
    yd0, yd1 = max(0, dy), min(H, H + dy)
    out[yd0:yd1, xd0:xd1] = norm_img2d[ys0:ys1, xs0:xs1]
    return out, dx, dy


def center_images(images):
    """对 (N,1,H,W) 批量居中。返回 (centered_images, centroids[N,2], shifts[N,2])。"""
    N = images.shape[0]
    out = np.zeros_like(images)
    centroids = np.zeros((N, 2), dtype=np.float64)
    shifts = np.zeros((N, 2), dtype=np.int32)
    for i in range(N):
        cx, cy = compute_centroid_linear(images[i, 0])
        shifted, dx, dy = shift_to_center(images[i, 0], cx, cy)
        out[i, 0] = shifted
        centroids[i] = (cx, cy)
        shifts[i] = (dx, dy)
    return out, centroids, shifts


def summarize_per_seed(per_seed):
    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "angular_err_worst", "hit@5deg", "hit@10deg"]
    s = {}
    for k in keys:
        vals = [m[k] for m in per_seed]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s


def save_seed_csv(out_dir, case, per_seed):
    keys = ["seed", "angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "angular_err_worst", "hit@5deg", "hit@10deg"]
    with open(os.path.join(out_dir, f"{case}_per_seed.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for m in per_seed:
            w.writerow(m)


def centroid_yaw_corr(centroids, yaw, pitch, test_idx):
    """报告 centroid_x/centroid_y 与 yaw/pitch 的 Pearson 相关（验证质心-yaw 线索）。"""
    cx = centroids[test_idx, 0]; cy = centroids[test_idx, 1]
    y = yaw[test_idx]; p = pitch[test_idx]
    def corr(a, b):
        a = a - a.mean(); b = b - b.mean()
        d = np.sqrt((a * a).sum() * (b * b).sum())
        return float((a * b).sum() / d) if d > 1e-12 else 0.0
    return {
        "corr_centroidx_yaw": corr(cx, y),
        "corr_centroidx_pitch": corr(cx, p),
        "corr_centroidy_yaw": corr(cy, y),
        "corr_centroidy_pitch": corr(cy, p),
        "centroid_x_mean": float(cx.mean()), "centroid_x_std": float(cx.std()),
        "centroid_y_mean": float(cy.mean()), "centroid_y_std": float(cy.std()),
    }


def main():
    ap = argparse.ArgumentParser(description="Exp12e: centered-image control")
    ap.add_argument("--image-dir", default=_IMAGE_DIR)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--image-size", type=int, default=128)
    ap.add_argument("--intensity", default="log1p")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--patience", type=int, default=100)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--dropout", type=float, default=0.10)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        args.seeds = [0]
        args.epochs = 6
        args.patience = 4
    rf.SEEDS = args.seeds

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    log_f = open(os.path.join(out_dir, "run.log"), "w", encoding="utf-8", buffering=1)

    class Tee:
        def __init__(self, *s): self.s = s
        def write(self, x):
            for st in self.s:
                try: st.write(x); st.flush()
                except Exception: pass
        def flush(self):
            for st in self.s:
                try: st.flush()
                except Exception: pass
    sys.stdout = Tee(sys.__stdout__, log_f)
    sys.stderr = Tee(sys.__stderr__, log_f)

    print("=" * 70)
    print("  实验12e：质心居中控制实验")
    print(f"  Image dir: {args.image_dir}")
    print(f"  Output:    {out_dir}")
    print(f"  Seeds: {args.seeds}  epochs={args.epochs} patience={args.patience}")
    print("=" * 70)

    t_all = time.time()
    images, yaw, pitch = rf.load_images(args.image_dir, args.image_size, args.intensity)
    split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    test_idx = split["test_idx"]
    print(f"  Split: train_pool={split['n_train']} test={split['n_test']}")

    print("\n  [居中] 计算线性强度质心并整数平移...")
    t0 = time.time()
    images_centered, centroids, shifts = center_images(images)
    print(f"    居中完成 {time.time()-t0:.0f}s；"
          f"质心 x mean={centroids[:,0].mean():.1f} std={centroids[:,0].std():.1f}，"
          f"平移 |dx| mean={np.abs(shifts[:,0]).mean():.1f} |dy| mean={np.abs(shifts[:,1]).mean():.1f}")

    corr_orig = centroid_yaw_corr(centroids, yaw, pitch, test_idx)
    # 居中后质心应回到中心：再算一次验证
    cen2 = np.array([compute_centroid_linear(images_centered[i, 0]) for i in test_idx])
    corr_after = {
        "corr_centroidx_yaw_after_centering":
            float(np.corrcoef(cen2[:, 0], yaw[test_idx])[0, 1]),
        "centroid_x_std_after": float(cen2[:, 0].std()),
        "centroid_y_std_after": float(cen2[:, 1].std()),
    }
    print(f"    原始 corr(centroid_x, yaw)={corr_orig['corr_centroidx_yaw']:.3f}；"
          f"居中后={corr_after['corr_centroidx_yaw_after_centering']:.3f}，"
          f"居中后 centroid_x std={corr_after['centroid_x_std_after']:.2f}")

    # ---- 训练原始 image-only ----
    print(f"\n{'='*64}\n  原始（非居中）ResNet image-only（{len(args.seeds)} seeds）\n{'='*64}")
    t0 = time.time()
    s_orig, ps_orig, _, _ = rf.run_image_only(
        images, yaw, pitch, split, args, out_dir, "image_only_original")
    print(f"  原始训练耗时 {time.time()-t0:.0f}s")

    # ---- 训练居中 image-only ----
    print(f"\n{'='*64}\n  居中 ResNet image-only（{len(args.seeds)} seeds）\n{'='*64}")
    t0 = time.time()
    s_cen, ps_cen, _, _ = rf.run_image_only(
        images_centered, yaw, pitch, split, args, out_dir, "image_only_centered")
    print(f"  居中训练耗时 {time.time()-t0:.0f}s")

    save_seed_csv(out_dir, "image_only_original", ps_orig)
    save_seed_csv(out_dir, "image_only_centered", ps_cen)

    # ---- 汇总 ----
    sum_orig = summarize_per_seed(ps_orig)
    sum_cen = summarize_per_seed(ps_cen)

    results = {
        "config": vars(args),
        "seeds": args.seeds,
        "centroid_correlations_original": corr_orig,
        "centroid_after_centering": corr_after,
        "shift_stats": {
            "abs_dx_mean": float(np.abs(shifts[:, 0]).mean()),
            "abs_dy_mean": float(np.abs(shifts[:, 1]).mean()),
            "abs_dx_max": int(np.abs(shifts[:, 0]).max()),
            "abs_dy_max": int(np.abs(shifts[:, 1]).max()),
        },
        "image_only_original": sum_orig,
        "image_only_centered": sum_cen,
        "elapsed_sec": time.time() - t_all,
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(os.path.join(out_dir, "summary.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", "mean", "std", "median", "p90", "p95", "worst", "hit5", "hit10"])
        for name, s in [("image_only_original", sum_orig), ("image_only_centered", sum_cen)]:
            w.writerow([name, f"{s['angular_err_mean_mean']:.3f}", f"{s['angular_err_mean_std']:.3f}",
                        f"{s['angular_err_median_mean']:.3f}", f"{s['angular_err_p90_mean']:.3f}",
                        f"{s['angular_err_p95_mean']:.3f}", f"{s['angular_err_worst_mean']:.3f}",
                        f"{s['hit@5deg_mean']:.4f}", f"{s['hit@10deg_mean']:.4f}"])

    # markdown
    d_mean = sum_cen["angular_err_mean_mean"] - sum_orig["angular_err_mean_mean"]
    L = [
        "# 实验12e：质心居中控制实验 — 结果", "",
        f"> 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"> Split 10°→5°，{len(args.seeds)} seeds；ResNet image-only；phase63 exact BRDF log1p 128×128。  ",
        "> 质心在线性强度域计算（expm1 反归一化后 intensity-weighted），整数平移居中，背景填 0。", "",
        "## 主结果表", "",
        "| case | mean±std | median | p90 | worst | Hit@5° | Hit@10° |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for name, s in [("original (non-centered)", sum_orig), ("centered", sum_cen)]:
        L.append(f"| {name} | {s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° | "
                 f"{s['angular_err_median_mean']:.2f}° | {s['angular_err_p90_mean']:.2f}° | "
                 f"{s['angular_err_worst_mean']:.1f}° | {s['hit@5deg_mean']:.1%} | {s['hit@10deg_mean']:.1%} |")
    L += [
        "", f"> Δmean(centered − original) = {d_mean:+.2f}°", "",
        "## 质心-姿态相关（验证 centroid_x ~ yaw 线索）", "",
        f"- 原始 corr(centroid_x, yaw) = {corr_orig['corr_centroidx_yaw']:.3f}",
        f"- 原始 corr(centroid_x, pitch) = {corr_orig['corr_centroidx_pitch']:.3f}",
        f"- 居中后 corr(centroid_x, yaw) = {corr_after['corr_centroidx_yaw_after_centering']:.3f}"
        f"（centroid_x std {corr_orig['centroid_x_std']:.2f} → {corr_after['centroid_x_std_after']:.2f}）",
        f"- 平移幅度 |dx| mean={results['shift_stats']['abs_dx_mean']:.1f}px, "
        f"|dy| mean={results['shift_stats']['abs_dy_mean']:.1f}px", "",
        "## 判读（按数据，不预设结论）", "",
    ]
    if abs(d_mean) < 0.5:
        L.append(f"- 居中前后 mean 几乎不变（Δ={d_mean:+.2f}°）→ **clean-image upper bound 不只是质心漂移**；"
                 "ResNet 主要依赖目标形状/朝向特征，而非固定框定。质心-yaw 相关是物理副产物，非主要捷径。")
    elif d_mean > 1.0:
        L.append(f"- 居中后明显退化（Δ={d_mean:+.2f}°）→ **clean-image 性能部分依赖固定框定/质心线索**，"
                 "应写入 limitation：性能上限部分来自一致的图像框定假设。")
    else:
        L.append(f"- 居中后轻微变化（Δ={d_mean:+.2f}°）→ 质心线索贡献有限但非零，"
                 "诚实报告：clean-image 性能主要来自目标外观，质心框定提供小幅辅助。")
    L += ["", "## 写作红线", "",
          "禁止写：real telescope validation / operational robustness / fully robust。",
          "本实验仅为合成 clean 图像的内部控制，不构成真实观测泛化证据。"]

    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    print("\n  主结果：")
    print(f"    original mean={sum_orig['angular_err_mean_mean']:.2f}±{sum_orig['angular_err_mean_std']:.2f}° "
          f"Hit5={sum_orig['hit@5deg_mean']:.1%}")
    print(f"    centered mean={sum_cen['angular_err_mean_mean']:.2f}±{sum_cen['angular_err_mean_std']:.2f}° "
          f"Hit5={sum_cen['hit@5deg_mean']:.1%}")
    print(f"    Δmean(centered−original) = {d_mean:+.2f}°")
    print(f"\n  完成，总耗时 {time.time()-t_all:.0f}s。输出: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

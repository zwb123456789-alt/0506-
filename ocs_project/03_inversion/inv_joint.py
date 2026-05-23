"""
模块 C · 反演脚本 3：OCS + 图像联合 kNN 检索（Step 11d）

融合方式：
  1) OCS：多几何特征，zscore → 欧氏距离
  2) 图像：HOG 特征，zscore → 欧氏距离
  3) 两个距离矩阵分别按非对角 min-max 归一到 [0,1]
  4) D_joint = alpha * D_ocs + (1 - alpha) * D_img
  5) alpha sweep 0:0.05:1 + 局部精扫 0.01

输入：
  OCS: 模块 A 多几何输出（multi_geom_manifest.json + */ocs_scan.csv）
  图像: 模块 B 渲染输出（render_log.csv + *_brdf.png）

输出：结果/模块C_反演/inv_joint/run_YYYYMMDD_HHMMSS/
  - alpha_sweep.csv
  - predictions_best.csv
  - summary.json
  - ablation_table.md
  - config_used.json
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime

import numpy as np
from PIL import Image
from skimage.feature import hog

# 复用 inv_common 共享工具
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as IC

# ── HOG 参数（与 inv_image.py 保持一致）──────────────────────────
HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (16, 16)
HOG_CELLS_PER_BLOCK = (2, 2)
HOG_BLOCK_NORM = "L2-Hys"

# ── 默认路径 ────────────────────────────────────────────────────
DEFAULT_OCS_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块A_重构", "multi_geom_ggx_yaw73_pitch37", "run_20260520_162831"
))
DEFAULT_IMAGE_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块B_渲染", "run_20260521_phase63_ggx"
))
DEFAULT_OUT_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块C_反演", "inv_joint"
))


# ── 辅助：log 变换跳过遮挡率列 ──────────────────────────────────
def get_log_skip_cols(feat_mode, n_geoms):
    """返回 concat 后需跳过 log 变换的列索引（遮挡率列）。"""
    if feat_mode == "all":
        cols_per_geom, occ_offset = 9, 2
    elif feat_mode == "total":
        cols_per_geom, occ_offset = 3, 2
    else:
        return None  # per_part / obs_total 无遮挡率列
    return [occ_offset + g * cols_per_geom for g in range(n_geoms)]


# ── OCS 数据加载 ────────────────────────────────────────────────
def load_ocs_data(ocs_root, geom_set, feat_mode, transform):
    """加载多几何 OCS 数据，返回 (feats, yaw, pitch, n_geoms)。"""
    manifest_path = os.path.join(ocs_root, "multi_geom_manifest.json")
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"manifest 不存在: {manifest_path}")
    label_order, geoms, feat_dict, yaw_dict, pitch_dict = IC.load_multi_geom(manifest_path)

    if geom_set == "concat5":
        feats, yaw, pitch, _ = IC.build_concat_features_with_mode(
            feat_dict, yaw_dict, pitch_dict, label_order, feat_mode)
        n_geoms = len(label_order)
    else:
        if geom_set not in feat_dict:
            raise ValueError(f"几何 '{geom_set}' 不在 manifest 中，可选: {label_order}")
        feats = IC.select_features(feat_dict[geom_set], feat_mode)
        yaw = yaw_dict[geom_set]
        pitch = pitch_dict[geom_set]
        n_geoms = 1

    if transform == "log":
        skip_cols = get_log_skip_cols(feat_mode, n_geoms)
        feats = IC.log_transform(feats, skip_cols=skip_cols)

    return feats.astype(np.float64), yaw, pitch, n_geoms


# ── 图像数据加载 ────────────────────────────────────────────────
def load_image_data(image_dir, image_subdir):
    """读取 render_log.csv，返回 (yaw, pitch, paths)。

    自动适配两种 CSV 格式：
      - 旧格式含 'filename' 列
      - 新格式含 'out_prefix' 列 → 拼接 '_brdf.png'
    """
    csv_path = os.path.join(image_dir, "render_log.csv")
    img_dir = os.path.join(image_dir, image_subdir)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"render_log.csv 不存在: {csv_path}")

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for r in reader:
            if "filename" in fieldnames:
                fname = r["filename"]
            else:
                fname = r.get("out_prefix", "") + "_brdf.png"
            path = os.path.join(img_dir, fname)
            if not os.path.exists(path):
                raise FileNotFoundError(f"图像缺失: {path}")
            rows.append({
                "yaw": float(r["yaw"]),
                "pitch": float(r["pitch"]),
                "path": path,
            })
    yaw = np.array([r["yaw"] for r in rows], dtype=np.float64)
    pitch = np.array([r["pitch"] for r in rows], dtype=np.float64)
    return yaw, pitch, rows


# ── HOG 特征提取 ────────────────────────────────────────────────
def extract_hog_features(rows, verbose=True):
    """逐图读取灰度 → HOG 向量，返回 (N, D) float32（Step 11d 减半内存）。"""
    t0 = time.time()
    N = len(rows)
    feats = None
    for i, r in enumerate(rows):
        img = Image.open(r["path"]).convert("L")
        arr = np.asarray(img, dtype=np.float32) / 255.0
        v = hog(arr,
                orientations=HOG_ORIENTATIONS,
                pixels_per_cell=HOG_PIXELS_PER_CELL,
                cells_per_block=HOG_CELLS_PER_BLOCK,
                block_norm=HOG_BLOCK_NORM,
                feature_vector=True)
        if feats is None:
            feats = np.zeros((N, v.shape[0]), dtype=np.float32)
        feats[i] = v
        if verbose and (i + 1) % 200 == 0:
            print(f"          HOG {i+1}/{N}  ({(i+1)/(time.time()-t0):.1f} 图/秒)")
    if verbose:
        print(f"          HOG 完成：{N} 图，{time.time()-t0:.1f}s，维度={feats.shape[1]}  "
              f"dtype={feats.dtype}  nbytes={feats.nbytes/1024/1024:.1f} MB")
    return feats  # 保持 float32


# ── 距离归一化 ──────────────────────────────────────────────────
def pairwise_euclidean(X):
    """计算成对欧氏距离矩阵。"""
    x2 = np.sum(X ** 2, axis=1, keepdims=True)
    d2 = np.maximum(x2 + x2.T - 2 * (X @ X.T), 0.0)
    return np.sqrt(d2)


def normalize_distance_matrix(D):
    """对非对角元素 min-max 归一到 [0,1]，对角置 0。"""
    mask = ~np.eye(D.shape[0], dtype=bool)
    vals = D[mask]
    lo, hi = vals.min(), vals.max()
    if hi - lo < 1e-12:
        return np.zeros_like(D)
    out = (D - lo) / (hi - lo)
    np.fill_diagonal(out, 0.0)
    return out


# ── kNN 检索 ────────────────────────────────────────────────────
def topk_from_distance(D, k_max, leave_self=True):
    """从距离矩阵中取 k 个最近邻索引（已排序）。

    leave_self=True 时对角置 inf（LOO）。
    """
    D2 = D.copy()
    if leave_self:
        np.fill_diagonal(D2, np.inf)
    k = min(k_max, D2.shape[1])
    idx = np.argpartition(D2, kth=k - 1, axis=1)[:, :k]
    rows_arr = np.arange(D2.shape[0])[:, None]
    sub = D2[rows_arr, idx]
    order = np.argsort(sub, axis=1)
    return idx[rows_arr, order]


# ── 样本对齐 ────────────────────────────────────────────────────
def align_samples(ocs_yaw, ocs_pitch, img_yaw, img_pitch):
    """验证 OCS 与图像样本的 yaw/pitch 顺序一致，返回公共索引。"""
    if len(ocs_yaw) != len(img_yaw):
        raise ValueError(f"样本数不一致：OCS={len(ocs_yaw)} vs Image={len(img_yaw)}")
    if not (np.allclose(ocs_yaw, img_yaw) and np.allclose(ocs_pitch, img_pitch)):
        raise ValueError("OCS/Image yaw-pitch 顺序不一致，请检查数据来源")
    return len(ocs_yaw)


# ── alpha sweep ─────────────────────────────────────────────────
def run_alpha_sweep(D_ocs, D_img, yaw, pitch, alphas, verbose=True):
    """遍历 alpha 列表，返回 [(alpha, metrics, detail), ...] 按 angular_err_mean 排序。"""
    results = []
    for alpha in alphas:
        D = alpha * D_ocs + (1.0 - alpha) * D_img
        idx = topk_from_distance(D, max(IC.TOP_K_LIST), leave_self=True)
        pred_yaw = yaw[idx[:, 0]]
        pred_pitch = pitch[idx[:, 0]]
        metrics, detail = IC.evaluate_predictions(
            pred_yaw, pred_pitch, yaw, pitch, pred_idx=idx)
        metrics["alpha"] = alpha
        results.append((alpha, metrics, detail))
        if verbose:
            print(f"          a={alpha:.2f}  mean={metrics['angular_err_mean']:.2f}°  "
                  f"med={metrics['angular_err_median']:.2f}°  "
                  f"p90={metrics['angular_err_p90']:.2f}°  "
                  f"Top1@5°={metrics.get('top1_acc@5deg', 0)*100:.2f}%  "
                  f"Top5@5°={metrics.get('top5_acc@5deg', 0)*100:.2f}%")
    return results


# ── 输出 ────────────────────────────────────────────────────────
def write_outputs(out_dir, all_results, best_alpha, best_metrics, best_detail,
                  yaw, pitch, args, ocs_dim, img_dim, n_geoms):
    os.makedirs(out_dir, exist_ok=True)

    # --- alpha_sweep.csv ---
    csv_path = os.path.join(out_dir, "alpha_sweep.csv")
    all_sorted = sorted(all_results, key=lambda r: r[0])  # by alpha
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        fields = ["alpha", "angular_err_mean", "angular_err_median",
                  "angular_err_p90", "angular_err_p95",
                  "yaw_err_mean", "yaw_err_median", "yaw_err_p95",
                  "pitch_err_mean", "pitch_err_median", "pitch_err_p95",
                  "top1_acc@5deg", "top5_acc@5deg",
                  "top1_acc@10deg", "top5_acc@10deg"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for _, m, _ in all_sorted:
            w.writerow(m)
    print(f"  [OK] alpha_sweep.csv")

    # --- summary.json ---
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "best_alpha": best_alpha,
            "best_metrics": best_metrics,
            "all_alphas": [{"alpha": a, "angular_err_mean": m["angular_err_mean"]}
                          for a, m, _ in all_sorted],
        }, f, indent=2, ensure_ascii=False)
    print(f"  [OK] summary.json")

    # --- predictions_best.csv ---
    pred_csv = os.path.join(out_dir, "predictions_best.csv")
    with open(pred_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["idx", "true_yaw", "true_pitch",
                    "pred_yaw", "pred_pitch",
                    "err_yaw_deg", "err_pitch_deg", "err_angular_deg"])
        for i in range(len(yaw)):
            w.writerow([i,
                        f"{yaw[i]:.4f}", f"{pitch[i]:.4f}",
                        f"{best_detail['pred_yaw'][i]:.4f}",
                        f"{best_detail['pred_pitch'][i]:.4f}",
                        f"{best_detail['err_yaw'][i]:.4f}",
                        f"{best_detail['err_pitch'][i]:.4f}",
                        f"{best_detail['err_angular'][i]:.4f}"])
    print(f"  [OK] predictions_best.csv")

    # --- config_used.json ---
    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump({
            "fusion_formula": "D_joint = alpha * D_ocs + (1-alpha) * D_img",
            "distance_normalization": "each D min-max over non-diagonal → [0,1]",
            "ocs_root": args.ocs_root,
            "geom_set": args.geom_set,
            "ocs_feat": args.ocs_feat,
            "ocs_transform": args.ocs_transform,
            "ocs_dim": ocs_dim,
            "image_dir": args.image_dir,
            "image_subdir": args.image_subdir,
            "image_feature": "HOG",
            "image_dim": img_dim,
            "hog_params": {
                "orientations": HOG_ORIENTATIONS,
                "pixels_per_cell": list(HOG_PIXELS_PER_CELL),
                "cells_per_block": list(HOG_CELLS_PER_BLOCK),
                "block_norm": HOG_BLOCK_NORM,
            },
            "feature_normalization": "zscore before pairwise euclidean distance",
            "split": "loo",
            "coarse_sweep": f"{args.alpha_start}:{args.alpha_step}:{args.alpha_end}",
            "fine_sweep": f"{args.alpha_start}:{args.alpha_step}:{args.alpha_end}" if not args.no_fine else "skipped",
            "n_geometries": n_geoms,
            "n_samples": int(len(yaw)),
        }, f, indent=2, ensure_ascii=False)
    print(f"  [OK] config_used.json")

    # --- ablation_table.md ---
    # 提取 alpha=0, alpha=1, best_alpha 三行
    def find_result(a):
        for alpha, m, d in all_results:
            if abs(alpha - a) < 1e-9:
                return m
        return None

    r_img = find_result(0.0)
    r_ocs = find_result(1.0)
    r_joint = best_metrics

    md_path = os.path.join(out_dir, "ablation_table.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# OCS+Image 联合反演消融表\n\n")
        f.write("| 方法 | OCS 输入 | Image 输入 | split | alpha | Top1@5° | Top5@5° | mean |\n")
        f.write("|---|---|---|---:|---:|---:|---:|\n")
        if r_ocs:
            f.write(f"| OCS-only kNN | {args.geom_set} {args.ocs_feat} {args.ocs_transform} | - | LOO | 1.00 | "
                    f"{r_ocs.get('top1_acc@5deg',0)*100:.2f}% | "
                    f"{r_ocs.get('top5_acc@5deg',0)*100:.2f}% | "
                    f"{r_ocs['angular_err_mean']:.2f}° |\n")
        if r_img:
            f.write(f"| HOG image-only | - | phase63 GGX PNG | LOO | 0.00 | "
                    f"{r_img.get('top1_acc@5deg',0)*100:.2f}% | "
                    f"{r_img.get('top5_acc@5deg',0)*100:.2f}% | "
                    f"{r_img['angular_err_mean']:.2f}° |\n")
        f.write(f"| **OCS+HOG joint** | {args.geom_set} {args.ocs_feat} {args.ocs_transform} | phase63 GGX PNG | LOO | "
                f"{best_alpha:.2f} | "
                f"**{r_joint.get('top1_acc@5deg',0)*100:.2f}%** | "
                f"**{r_joint.get('top5_acc@5deg',0)*100:.2f}%** | "
                f"**{r_joint['angular_err_mean']:.2f}°** |\n")
        f.write(f"| OCS-only MLP | {args.geom_set} {args.ocs_feat} {args.ocs_transform} | - | 10°→5° | - | 90.7% | - | 3.98° |\n")
        f.write("\n> 注：MLP 行来自 Step 11c (`train_mlp.py`)，使用 10°→5° split（非 LOO），不可直接对比 LOO 指标。\n")
    print(f"  [OK] ablation_table.md")


# ── 主流程 ──────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="OCS + Image 联合 kNN 检索 · alpha sweep")
    # OCS
    ap.add_argument("--ocs-root", default=DEFAULT_OCS_ROOT,
                    help="模块 A 多几何输出目录（含 multi_geom_manifest.json）")
    ap.add_argument("--geom-set", default="concat5",
                    help="几何集：concat5（全部拼接）或单个几何标签如 phase63")
    ap.add_argument("--ocs-feat", default="all", choices=["total", "obs_total", "per_part", "all"],
                    help="OCS 特征模式")
    ap.add_argument("--ocs-transform", default="raw", choices=["raw", "log"],
                    help="特征变换：raw=无变换, log=log10")
    # 图像
    ap.add_argument("--image-dir", default=DEFAULT_IMAGE_DIR,
                    help="模块 B 渲染 run 目录（含 render_log.csv）")
    ap.add_argument("--image-subdir", default="images",
                    help="图像子目录名（images 或 brdf_images）")
    # alpha sweep
    ap.add_argument("--alpha-start", type=float, default=0.0)
    ap.add_argument("--alpha-end", type=float, default=1.0)
    ap.add_argument("--alpha-step", type=float, default=0.05)
    ap.add_argument("--no-fine", action="store_true",
                    help="跳过局部精扫")
    # 输出
    ap.add_argument("--out-root", default=DEFAULT_OUT_ROOT)
    args = ap.parse_args()

    # ── 1. 加载 OCS 数据 ──
    print(f"[inv_joint] 加载 OCS：{args.ocs_root}")
    print(f"            geom_set={args.geom_set}  feat={args.ocs_feat}  transform={args.ocs_transform}")
    ocs_feat, yaw_ocs, pitch_ocs, n_geoms = load_ocs_data(
        args.ocs_root, args.geom_set, args.ocs_feat, args.ocs_transform)
    print(f"            OCS 特征维度={ocs_feat.shape[1]}  样本数={len(yaw_ocs)}")

    # ── 2. 加载图像数据 ──
    print(f"[inv_joint] 加载图像：{args.image_dir}")
    print(f"            subdir={args.image_subdir}")
    yaw_img, pitch_img, img_rows = load_image_data(args.image_dir, args.image_subdir)
    print(f"            图像样本数={len(yaw_img)}")

    # ── 3. 样本对齐 ──
    print("[inv_joint] 样本对齐检查 ...")
    N = align_samples(yaw_ocs, pitch_ocs, yaw_img, pitch_img)
    print(f"            [OK] OCS={len(yaw_ocs)}  Image={len(yaw_img)}  Matched={N}")

    # ── 4. 提取 HOG 特征 ──
    print("[inv_joint] 提取 HOG ...")
    img_feat_raw = extract_hog_features(img_rows)

    # ── 5. 计算 zscore + 距离矩阵 + 归一化 ──
    print("[inv_joint] 计算距离矩阵 ...")
    # OCS 端：45D 小矩阵，沿用 float64 全矩阵 GEMM
    ocs_z = IC.zscore(ocs_feat)
    D_ocs_raw = pairwise_euclidean(ocs_z)

    # 图像端：HOG (N, 8100) float32 + chunked GEMM（Step 11d 修复）
    print(f"            HOG 端: float32 zscore + chunked pairwise (N={len(img_feat_raw)}, "
          f"D={img_feat_raw.shape[1]}, nbytes={img_feat_raw.nbytes/1024/1024:.1f} MB)")
    img_z = IC.zscore_float32(img_feat_raw)
    print(f"            HOG zscore 完成: dtype={img_z.dtype}  nbytes={img_z.nbytes/1024/1024:.1f} MB")
    D_img_raw = IC.pairwise_euclidean_chunked(img_z, batch_size=128, verbose=False)
    print(f"            HOG D 完成: shape={D_img_raw.shape}  dtype={D_img_raw.dtype}  "
          f"nbytes={D_img_raw.nbytes/1024/1024:.1f} MB")

    D_ocs = normalize_distance_matrix(D_ocs_raw)
    D_img = normalize_distance_matrix(D_img_raw)
    print(f"            OCS 距离范围: [{D_ocs[~np.eye(N, dtype=bool)].min():.4f}, "
          f"{D_ocs[~np.eye(N, dtype=bool)].max():.4f}]")
    print(f"            Image 距离范围: [{D_img[~np.eye(N, dtype=bool)].min():.4f}, "
          f"{D_img[~np.eye(N, dtype=bool)].max():.4f}]")

    # ── 6. alpha sweep ──
    coarse_alphas = np.arange(args.alpha_start, args.alpha_end + 1e-9, args.alpha_step)
    print(f"[inv_joint] 粗扫 alpha: {len(coarse_alphas)} 个值 "
          f"({args.alpha_start}:{args.alpha_step}:{args.alpha_end})")
    all_results = run_alpha_sweep(D_ocs, D_img, yaw_ocs, pitch_ocs, coarse_alphas)

    # ── 7. 局部精扫 ──
    best_alpha, best_metrics, best_detail = min(all_results, key=lambda r: (
        r[1]["angular_err_mean"], r[1].get("angular_err_p95", 999)))
    print(f"\n[inv_joint] 粗扫最佳 a={best_alpha:.2f}  "
          f"mean={best_metrics['angular_err_mean']:.2f}°  "
          f"Top1@5°={best_metrics.get('top1_acc@5deg',0)*100:.2f}%")

    if not args.no_fine and 0.01 < best_alpha < 0.99:
        fine_start = max(0.0, best_alpha - 0.05)
        fine_end = min(1.0, best_alpha + 0.05)
        # 生成精扫 alpha 列表，绕过已算的 coarse 值
        fine_step = 0.01
        fine_alphas = []
        v = fine_start
        while v <= fine_end + 1e-9:
            # 跳过与 coarse 重合的值
            if min(abs(v - a) for a in coarse_alphas) > 1e-9:
                fine_alphas.append(round(v, 6))
            v += fine_step
        if fine_alphas:
            print(f"[inv_joint] 局部精扫 alpha: {len(fine_alphas)} 个值 "
                  f"({fine_start}:{fine_step}:{fine_end})")
            fine_results = run_alpha_sweep(D_ocs, D_img, yaw_ocs, pitch_ocs, fine_alphas)
            all_results.extend(fine_results)
            # 重新选最佳
            best_alpha, best_metrics, best_detail = min(all_results, key=lambda r: (
                r[1]["angular_err_mean"], r[1].get("angular_err_p95", 999)))

    print(f"\n[inv_joint] 最终最佳 a={best_alpha:.4f}  "
          f"mean={best_metrics['angular_err_mean']:.2f}°  "
          f"med={best_metrics['angular_err_median']:.2f}°  "
          f"p90={best_metrics['angular_err_p90']:.2f}°  "
          f"Top1@5°={best_metrics.get('top1_acc@5deg',0)*100:.2f}%  "
          f"Top5@5°={best_metrics.get('top5_acc@5deg',0)*100:.2f}%")

    # ── 8. 端点 sanity check ──
    print("\n[inv_joint] Sanity check — 端点对比：")
    for a, m, _ in sorted(all_results, key=lambda r: r[0]):
        if abs(a) < 1e-9 or abs(a - 1.0) < 1e-9:
            tag = "image-only" if abs(a) < 1e-9 else "OCS-only kNN"
            print(f"  a={a:.2f} ({tag}): Top1@5°={m.get('top1_acc@5deg',0)*100:.2f}%  "
                  f"Top5@5°={m.get('top5_acc@5deg',0)*100:.2f}%  "
                  f"mean={m['angular_err_mean']:.2f}°")

    # ── 9. 输出 ──
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    write_outputs(out_dir, all_results, best_alpha, best_metrics, best_detail,
                  yaw_ocs, pitch_ocs, args, ocs_feat.shape[1], img_feat_raw.shape[1], n_geoms)
    print(f"\n[inv_joint] 输出已写入：{out_dir}")


if __name__ == "__main__":
    main()

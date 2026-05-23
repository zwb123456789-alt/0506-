"""
模块 C · 反演脚本 2：纯图像 kNN 检索（HOG + 欧氏距离）

用途：以 HOG 特征为指纹，在姿态库中检索查询样本的 yaw/pitch。
MVP 选择 HOG 因其纯 numpy/scikit-image 即可、对二维剪影/边缘敏感、对光照鲁棒。
论文期升级方向：CNN embedding（ResNet / DINOv2 等）。

验证：
  Step 1 · 全表自查询（Top-1 应 == 自身）
  Step 2 · 留一法 LOO

输入：模块 B 输出 `结果/模块B_渲染/run_*/`：render_log.csv + images/*.png
输出：`结果/模块C_反演/inv_image/run_YYYYMMDD_HHMMSS/`：
  - loo_predictions.csv / summary.json / config_used.json
"""

import argparse
import csv
import json
import os
import time
from datetime import datetime

import numpy as np
from PIL import Image
from skimage.feature import hog

# ---------------------------------------------------------------- 默认路径

DEFAULT_RENDER_RUN = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块B_渲染", "run_20260511_193251"
))
DEFAULT_OUT_ROOT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "结果", "模块C_反演", "inv_image"
))

# HOG 参数（256×256 灰度图 → 维度 = 9 * 4 * 15^2 = 8100）
HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (16, 16)
HOG_CELLS_PER_BLOCK = (2, 2)
HOG_BLOCK_NORM = "L2-Hys"

TOP_K_LIST = [1, 3, 5]
HIT_THRESHOLD_DEG = 5.0


# ---------------------------------------------------------------- 数据加载

def load_render_log(run_dir, image_dir="images"):
    csv_path = os.path.join(run_dir, "render_log.csv")
    img_dir = os.path.join(run_dir, image_dir)
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for r in reader:
            if "filename" in fieldnames:
                fname = r["filename"]
            else:
                fname = r.get("out_prefix", "") + "_brdf.png"
            rows.append({
                "yaw": float(r["yaw"]),
                "pitch": float(r["pitch"]),
                "filename": fname,
                "path": os.path.join(img_dir, fname),
            })
    return rows


def extract_hog_features(rows, verbose=True):
    """逐图读取 → 灰度 → HOG 向量。"""
    feats = None
    t0 = time.time()
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
            feats = np.zeros((len(rows), v.shape[0]), dtype=np.float32)
        feats[i] = v
        if verbose and (i + 1) % 100 == 0:
            print(f"          HOG 进度 {i+1}/{len(rows)}  "
                  f"({(i+1)/(time.time()-t0):.1f} 图/秒)")
    if verbose:
        print(f"          HOG 完成：{len(rows)} 图，耗时 {time.time()-t0:.1f}s，"
              f"特征维度 = {feats.shape[1]}")
    return feats


def zscore(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    return (X - mu) / sd, mu, sd


# ---------------------------------------------------------------- 误差度量

def yaw_err(a, b):
    d = np.abs(a - b) % 360.0
    return np.minimum(d, 360.0 - d)


def angular_err_deg(yaw1, pitch1, yaw2, pitch2):
    y1, p1 = np.deg2rad(yaw1), np.deg2rad(pitch1)
    y2, p2 = np.deg2rad(yaw2), np.deg2rad(pitch2)
    v1 = np.stack([np.cos(p1) * np.cos(y1), np.cos(p1) * np.sin(y1), np.sin(p1)], axis=-1)
    v2 = np.stack([np.cos(p2) * np.cos(y2), np.cos(p2) * np.sin(y2), np.sin(p2)], axis=-1)
    cos = np.clip(np.sum(v1 * v2, axis=-1), -1.0, 1.0)
    return np.rad2deg(np.arccos(cos))


# ---------------------------------------------------------------- kNN

def knn_topk(X_query, X_db, k_max):
    q2 = np.sum(X_query ** 2, axis=1, keepdims=True)
    d2 = np.sum(X_db ** 2, axis=1, keepdims=True).T
    cross = X_query @ X_db.T
    dist2 = np.maximum(q2 + d2 - 2 * cross, 0.0)
    k = min(k_max, dist2.shape[1])
    idx = np.argpartition(dist2, kth=k - 1, axis=1)[:, :k]
    rows = np.arange(dist2.shape[0])[:, None]
    sub = dist2[rows, idx]
    order = np.argsort(sub, axis=1)
    idx_sorted = idx[rows, order]
    dist_sorted = np.sqrt(sub[rows, order])
    return idx_sorted, dist_sorted


# ---------------------------------------------------------------- Step 1 / 2

def step1_self_query(X):
    idx, _ = knn_topk(X, X, k_max=1)
    pred = idx[:, 0]
    self_idx = np.arange(len(X))
    rate = float(np.mean(pred == self_idx))
    return {
        "top1_is_self": rate,
        "n_samples": int(len(X)),
        "passed": rate >= 0.999,
    }


def step2_loo(X, yaw, pitch, k_max=max(TOP_K_LIST)):
    idx, dist = knn_topk(X, X, k_max=k_max + 1)
    N = X.shape[0]
    rows = np.arange(N)[:, None]
    self_mask = (idx == rows)
    new_idx = np.zeros((N, k_max), dtype=idx.dtype)
    new_dist = np.zeros((N, k_max), dtype=dist.dtype)
    for i in range(N):
        keep = idx[i][~self_mask[i]][:k_max]
        keep_d = dist[i][~self_mask[i]][:k_max]
        if len(keep) < k_max:
            keep = np.concatenate([keep, np.full(k_max - len(keep), keep[-1])])
            keep_d = np.concatenate([keep_d, np.full(k_max - len(keep_d), keep_d[-1])])
        new_idx[i] = keep
        new_dist[i] = keep_d

    pred_yaw = yaw[new_idx[:, 0]]
    pred_pitch = pitch[new_idx[:, 0]]
    err_y = yaw_err(pred_yaw, yaw)
    err_p = np.abs(pred_pitch - pitch)
    err_a = angular_err_deg(pred_yaw, pred_pitch, yaw, pitch)

    topk_acc = {}
    for k in TOP_K_LIST:
        sub = new_idx[:, :k]
        hit_any = np.zeros(N, dtype=bool)
        for kk in range(k):
            ea = angular_err_deg(yaw[sub[:, kk]], pitch[sub[:, kk]], yaw, pitch)
            hit_any |= (ea < HIT_THRESHOLD_DEG)
        topk_acc[f"top{k}_acc@{int(HIT_THRESHOLD_DEG)}deg"] = float(np.mean(hit_any))

    summary = {
        "n_samples": int(N),
        "yaw_err_mean":   float(err_y.mean()),
        "yaw_err_median": float(np.median(err_y)),
        "yaw_err_p95":    float(np.percentile(err_y, 95)),
        "pitch_err_mean":   float(err_p.mean()),
        "pitch_err_median": float(np.median(err_p)),
        "pitch_err_p95":    float(np.percentile(err_p, 95)),
        "angular_err_mean":   float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p95":    float(np.percentile(err_a, 95)),
        **topk_acc,
    }
    return summary, {
        "pred_idx": new_idx[:, 0],
        "pred_yaw": pred_yaw,
        "pred_pitch": pred_pitch,
        "err_yaw": err_y,
        "err_pitch": err_p,
        "err_angular": err_a,
    }


# ---------------------------------------------------------------- 输出

def write_outputs(out_dir, render_run, step1, step2_summary, step2_detail,
                  yaw, pitch, feat_dim):
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "source_render_run": render_run,
            "feature_type": "HOG",
            "feature_dim": int(feat_dim),
            "step1_self_query": step1,
            "step2_loo": step2_summary,
        }, f, indent=2, ensure_ascii=False)

    with open(os.path.join(out_dir, "loo_predictions.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["idx", "true_yaw", "true_pitch",
                    "pred_yaw", "pred_pitch",
                    "err_yaw_deg", "err_pitch_deg", "err_angular_deg"])
        for i in range(len(yaw)):
            w.writerow([
                i, f"{yaw[i]:.4f}", f"{pitch[i]:.4f}",
                f"{step2_detail['pred_yaw'][i]:.4f}",
                f"{step2_detail['pred_pitch'][i]:.4f}",
                f"{step2_detail['err_yaw'][i]:.4f}",
                f"{step2_detail['err_pitch'][i]:.4f}",
                f"{step2_detail['err_angular'][i]:.4f}",
            ])

    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump({
            "source_render_run": render_run,
            "feature_type": "HOG",
            "hog": {
                "orientations": HOG_ORIENTATIONS,
                "pixels_per_cell": list(HOG_PIXELS_PER_CELL),
                "cells_per_block": list(HOG_CELLS_PER_BLOCK),
                "block_norm": HOG_BLOCK_NORM,
            },
            "preprocess": "PIL convert L; arr/255.0",
            "normalization": "zscore",
            "distance": "euclidean",
            "top_k_list": TOP_K_LIST,
            "topk_hit_threshold_deg": HIT_THRESHOLD_DEG,
        }, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------- 主流程

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-run", default=DEFAULT_RENDER_RUN,
                    help="模块 B 输出 run 目录（含 render_log.csv + images/）")
    ap.add_argument("--out-root", default=DEFAULT_OUT_ROOT)
    ap.add_argument("--image-dir", default="images",
                    help="图像子目录名（默认 images，GGX 管线用 brdf_images）")
    args = ap.parse_args()

    print(f"[inv_image] 加载渲染日志：{args.render_run}")
    rows = load_render_log(args.render_run, image_dir=args.image_dir)
    N = len(rows)
    yaw = np.array([r["yaw"] for r in rows], dtype=np.float64)
    pitch = np.array([r["pitch"] for r in rows], dtype=np.float64)
    print(f"[inv_image] 样本数 N={N}")

    print("[inv_image] 提取 HOG ...")
    feats = extract_hog_features(rows)
    X, _, _ = zscore(feats.astype(np.float64))

    print("[inv_image] Step 1 · 全表自查询 sanity check ...")
    step1 = step1_self_query(X)
    print(f"          Top-1 命中自身率 = {step1['top1_is_self']*100:.2f}%  "
          f"{'PASS' if step1['passed'] else 'FAIL'}")

    print("[inv_image] Step 2 · 留一法 ...")
    s, d = step2_loo(X, yaw, pitch)
    print(f"          yaw   误差: mean={s['yaw_err_mean']:.2f}°  "
          f"med={s['yaw_err_median']:.2f}°  p95={s['yaw_err_p95']:.2f}°")
    print(f"          pitch 误差: mean={s['pitch_err_mean']:.2f}°  "
          f"med={s['pitch_err_median']:.2f}°  p95={s['pitch_err_p95']:.2f}°")
    print(f"          角距 误差: mean={s['angular_err_mean']:.2f}°  "
          f"med={s['angular_err_median']:.2f}°  p95={s['angular_err_p95']:.2f}°")
    for k in TOP_K_LIST:
        print(f"          Top-{k}@{int(HIT_THRESHOLD_DEG)}°  = "
              f"{s[f'top{k}_acc@{int(HIT_THRESHOLD_DEG)}deg']*100:.2f}%")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    write_outputs(out_dir, args.render_run, step1, s, d, yaw, pitch, feats.shape[1])
    print(f"[inv_image] 输出已写入：{out_dir}")


if __name__ == "__main__":
    main()

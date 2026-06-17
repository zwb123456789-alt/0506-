# -*- coding: utf-8 -*-
"""
inv_common.py —— Step 11a：反演公共工具
========================================
- 读取 multi_geom_manifest.json
- 合并多个几何的 ocs_scan.csv
- 生成特征矩阵 / yaw/pitch 标签
- split 生成：LOO / coarse-to-fine (10°→5°) / random
- 姿态误差度量

设计原则：不依赖 torch/tf，仅 numpy + 标准库，供 kNN baseline 和后续 CNN 共用。
"""

import csv
import json
import os
import numpy as np

PART_NAMES = ["jinshuzhuti", "taiyangnengban", "yinshenban"]
TOP_K_LIST = [1, 3, 5]
TOP_K_10_LIST = [1, 5]
HIT_THRESHOLD_DEG = 5.0
HIT_THRESHOLD_10DEG = 10.0


# ============================================================
# 数据加载
# ============================================================

def _csv_rows(csv_path):
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def load_single_csv(csv_path):
    """返回 (features[N,9], yaw[N], pitch[N])。"""
    rows = _csv_rows(csv_path)
    N = len(rows)
    yaw = np.array([float(r["yaw"]) for r in rows], dtype=np.float64)
    pitch = np.array([float(r["pitch"]) for r in rows], dtype=np.float64)

    feats = np.zeros((N, 9), dtype=np.float64)
    for i, r in enumerate(rows):
        feats[i, 0] = float(r["ocs_no_occ"])
        feats[i, 1] = float(r["ocs_with_occ"])
        feats[i, 2] = float(r["occlusion_ratio"])
        for j, name in enumerate(PART_NAMES):
            feats[i, 3 + 2 * j]     = float(r[f"ocs_no_occ_{name}"])
            feats[i, 3 + 2 * j + 1] = float(r[f"ocs_with_occ_{name}"])
    return feats, yaw, pitch


def load_multi_geom(manifest_path):
    """加载多观测几何数据。

    返回:
        label_order:       [str × G]
        geoms:             [{"label","phase_deg","sun","det",...}]  每个几何的元信息
        feat_dict:         {label: features[N,9]}
        yaw_dict/pitch_dict: {label: array[N]}
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    base_dir = os.path.dirname(manifest_path)
    label_order = []
    geoms = []
    feat_dict = {}
    yaw_dict = {}
    pitch_dict = {}

    for s in manifest["summaries"]:
        label = s["label"]
        csv_path = os.path.join(base_dir, label, "ocs_scan.csv")
        if not os.path.exists(csv_path):
            print(f"  [跳过] {csv_path} 不存在")
            continue
        f, y, p = load_single_csv(csv_path)
        label_order.append(label)
        geoms.append(s)
        feat_dict[label] = f
        yaw_dict[label] = y
        pitch_dict[label] = p
        print(f"  [OK] 加载 {label}: {f.shape[0]} 样本, {f.shape[1]} 维特征")

    return label_order, geoms, feat_dict, yaw_dict, pitch_dict


def build_concat_features(feat_dict, yaw_dict, pitch_dict, label_order):
    """将多个几何的 OCS 特征按姿态对齐后横向拼接。

    假设所有几何共享同一 yaw/pitch 网格。
    返回:
        features[N, 9*G]
        yaw[N], pitch[N]
        geom_labels: list of geom labels (same order as features)
    """
    first_label = label_order[0]
    yaw0 = yaw_dict[first_label]
    pitch0 = pitch_dict[first_label]

    # 验证所有几何的 yaw/pitch 一致
    for label in label_order[1:]:
        if not (np.allclose(yaw_dict[label], yaw0) and
                np.allclose(pitch_dict[label], pitch0)):
            raise ValueError(f"[{label}] yaw/pitch 与 [{first_label}] 不一致")

    feats = np.hstack([feat_dict[label] for label in label_order])
    return feats, yaw0, pitch0, label_order


def select_features(feats, mode="all"):
    """从 9 维特征中选择子集。
    col: 0=ocs_no_occ, 1=ocs_with_occ, 2=occlusion_ratio,
         3/4=jinshuzhuti no/with, 5/6=taiyangnengban no/with, 7/8=yinshenban no/with
    """
    if mode == "total":
        return feats[:, :3]
    elif mode == "obs_total":
        return feats[:, 1:2]  # 仅 ocs_with_occ，最接近真实观测
    elif mode == "per_part":
        return feats[:, 3:]
    return feats


def build_concat_features_with_mode(feat_dict, yaw_dict, pitch_dict, label_order, feat_mode):
    """先按 feat_mode 对每个几何单独选特征，再横向拼接。"""
    first_label = label_order[0]
    yaw0 = yaw_dict[first_label]
    pitch0 = pitch_dict[first_label]

    for label in label_order[1:]:
        if not (np.allclose(yaw_dict[label], yaw0) and
                np.allclose(pitch_dict[label], pitch0)):
            raise ValueError(f"[{label}] yaw/pitch 与 [{first_label}] 不一致")

    feats = np.hstack([select_features(feat_dict[label], feat_mode) for label in label_order])
    return feats, yaw0, pitch0, label_order


# ============================================================
# 特征变换
# ============================================================

def zscore(X, return_params=False):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    out = (X - mu) / sd
    if return_params:
        return out, mu, sd
    return out


def zscore_float32(X, eps=1e-6):
    """float32 安全版 zscore：mu/std 用 float64 累计，输出 float32。

    Step 11d 修复（202605211536.md）：
      - HOG (2701, 8100) 用 float32 减半内存（~87 MB vs ~175 MB）
      - mu/std 用 float64 累计避免高维和的精度损失
      - NaN / 全零方差列处理：std=0 时置 1.0，结果置 0.0
    """
    X = np.asarray(X, dtype=np.float32, order="C")
    mu = X.mean(axis=0, dtype=np.float64)
    sd = X.std(axis=0, dtype=np.float64)
    bad = (~np.isfinite(sd)) | (sd < eps)
    sd[bad] = 1.0
    out = (X - mu.astype(np.float32)) / sd.astype(np.float32)
    out[~np.isfinite(out)] = 0.0
    return np.ascontiguousarray(out, dtype=np.float32)


def pairwise_euclidean_chunked(X, Y=None, batch_size=256, verbose=False):
    """分块 GEMM 计算欧氏距离矩阵，避免三维广播 OOM。

    Step 11d 修复（202605211536.md）：
      原广播实现 `(X[:,None,:] - X[None,:,:])**2` 在 (2701, 8100) 上
      需要 ~473 GB 临时数组，Windows numpy/MKL 下静默退出。
      本实现内存：X float32 ~87 MB + D float32 ~29 MB + chunk 临时 <5 MB。

    若 Y is None，做 X 自身距离矩阵；对角填 inf 便于 LOO 检索。
    """
    X = np.asarray(X, dtype=np.float32, order="C")
    if Y is None:
        Y = X
        same = True
    else:
        Y = np.asarray(Y, dtype=np.float32, order="C")
        same = False

    n = X.shape[0]
    m = Y.shape[0]
    YT = np.ascontiguousarray(Y.T, dtype=np.float32)

    x2 = np.sum(X * X, axis=1, dtype=np.float64).astype(np.float32)
    y2 = np.sum(Y * Y, axis=1, dtype=np.float64).astype(np.float32)

    D = np.empty((n, m), dtype=np.float32)
    for i in range(0, n, batch_size):
        j = min(i + batch_size, n)
        D2 = -2.0 * (X[i:j] @ YT)
        D2 += x2[i:j, None]
        D2 += y2[None, :]
        np.maximum(D2, 0.0, out=D2)
        np.sqrt(D2, out=D2)
        D[i:j] = D2
        if verbose:
            print(f"[pairwise] rows {i}:{j} / {n} done", flush=True)

    if same:
        np.fill_diagonal(D, np.inf)
    return D


def log_transform(X, eps=1e-6, skip_cols=None):
    """log10 变换，处理零/负值。skip_cols 指定不参与 log 的列索引。"""
    X_out = X.copy()
    if skip_cols is None:
        X_out = np.log10(np.maximum(X_out, eps))
    else:
        n_cols = X.shape[1]
        for c in range(n_cols):
            if c in skip_cols:
                continue
            X_out[:, c] = np.log10(np.maximum(X_out[:, c], eps))
    return X_out


# ============================================================
# Split 生成
# ============================================================

def split_loo(N):
    """留一法：每个样本依次做查询，库为其余 N-1。"""
    return {"type": "loo", "train_idx": np.arange(N), "test_idx": np.arange(N),
            "description": "每个样本依次做查询，库为其余 N-1"}


def split_coarse_to_fine(yaw, pitch, coarse_step=10.0, fine_step=5.0):
    """10° 网格 train → 5° 插值 test。

    返回:
        train_mask: 落在 coarse 网格上的点
        test_mask:  落在 fine 网格但不在 coarse 网格上的点
    """
    yaw_on_grid = np.abs(yaw % coarse_step) < 0.01
    yaw_on_grid |= np.abs((yaw % coarse_step) - coarse_step) < 0.01
    pitch_on_grid = np.abs(pitch % coarse_step) < 0.01
    pitch_on_grid |= np.abs((pitch % coarse_step) - coarse_step) < 0.01
    train_mask = yaw_on_grid & pitch_on_grid
    test_mask = ~train_mask
    return {
        "type": "coarse_to_fine",
        "coarse_step": coarse_step,
        "fine_step": fine_step,
        "train_idx": np.where(train_mask)[0],
        "test_idx": np.where(test_mask)[0],
        "n_train": int(train_mask.sum()),
        "n_test": int(test_mask.sum()),
        "description": f"{coarse_step}°网格→{fine_step}°插值 held-out test"
    }


def split_random(N, train_ratio=0.80, val_ratio=0.10, seed=42):
    """随机切分 train / val / test。"""
    rng = np.random.RandomState(seed)
    perm = rng.permutation(N)
    n_train = int(N * train_ratio)
    n_val = int(N * val_ratio)
    return {
        "type": "random",
        "seed": seed,
        "train_idx": perm[:n_train],
        "val_idx":   perm[n_train:n_train + n_val],
        "test_idx":  perm[n_train + n_val:],
        "n_train": n_train,
        "n_val": n_val,
        "n_test": N - n_train - n_val,
        "description": f"random split {train_ratio:.0%}/{val_ratio:.0%}/{(1-train_ratio-val_ratio):.0%}"
    }


# ============================================================
# 误差度量
# ============================================================

def yaw_err(a, b):
    """环形 yaw 误差，∈[0, 180]，单位度。"""
    d = np.abs(a - b) % 360.0
    return np.minimum(d, 360.0 - d)


def angular_err_deg(yaw1, pitch1, yaw2, pitch2):
    """两个 yaw/pitch 方向的角距（球面），单位度。"""
    y1, p1 = np.deg2rad(yaw1), np.deg2rad(pitch1)
    y2, p2 = np.deg2rad(yaw2), np.deg2rad(pitch2)
    v1 = np.stack([np.cos(p1) * np.cos(y1), np.cos(p1) * np.sin(y1), np.sin(p1)], axis=-1)
    v2 = np.stack([np.cos(p2) * np.cos(y2), np.cos(p2) * np.sin(y2), np.sin(p2)], axis=-1)
    cos_a = np.clip(np.sum(v1 * v2, axis=-1), -1.0, 1.0)
    return np.rad2deg(np.arccos(cos_a))


def evaluate_predictions(pred_yaw, pred_pitch, true_yaw, true_pitch, pred_idx=None):
    """计算全部误差指标。

    返回:
        metrics: dict
        details: {pred_yaw, pred_pitch, err_yaw, err_pitch, err_angular}
    """
    err_y = yaw_err(pred_yaw, true_yaw)
    err_p = np.abs(pred_pitch - true_pitch)
    err_a = angular_err_deg(pred_yaw, pred_pitch, true_yaw, true_pitch)

    N = len(true_yaw)
    metrics = {
        "n_samples": N,
        "yaw_err_mean":   float(err_y.mean()),
        "yaw_err_median": float(np.median(err_y)),
        "yaw_err_p95":    float(np.percentile(err_y, 95)),
        "pitch_err_mean":   float(err_p.mean()),
        "pitch_err_median": float(np.median(err_p)),
        "pitch_err_p95":    float(np.percentile(err_p, 95)),
        "angular_err_mean":   float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p90":    float(np.percentile(err_a, 90)),
        "angular_err_p95":    float(np.percentile(err_a, 95)),
    }

    # Top-K 准确率（使用 pred_idx 如果提供）
    if pred_idx is not None:
        for k in TOP_K_LIST:
            hit = np.zeros(N, dtype=bool)
            for kk in range(min(k, pred_idx.shape[1])):
                ea = angular_err_deg(true_yaw[pred_idx[:, kk]],
                                     true_pitch[pred_idx[:, kk]],
                                     true_yaw, true_pitch)
                hit |= (ea <= HIT_THRESHOLD_DEG + 1e-6)
            metrics[f"top{k}_acc@5deg"] = float(np.mean(hit))
        for k in TOP_K_10_LIST:
            hit = np.zeros(N, dtype=bool)
            for kk in range(min(k, pred_idx.shape[1])):
                ea = angular_err_deg(true_yaw[pred_idx[:, kk]],
                                     true_pitch[pred_idx[:, kk]],
                                     true_yaw, true_pitch)
                hit |= (ea <= HIT_THRESHOLD_10DEG + 1e-6)
            metrics[f"top{k}_acc@10deg"] = float(np.mean(hit))

    details = {
        "pred_yaw": pred_yaw,
        "pred_pitch": pred_pitch,
        "err_yaw": err_y,
        "err_pitch": err_p,
        "err_angular": err_a,
    }
    if pred_idx is not None:
        details["pred_idx"] = pred_idx

    return metrics, details


# ============================================================
# kNN
# ============================================================

class KNN:
    """欧氏距离 kNN，支持 zscore 归一化。"""
    def __init__(self, X_db, normalize=True):
        if normalize:
            self.mu = X_db.mean(axis=0)
            self.sd = X_db.std(axis=0)
            self.sd = np.where(self.sd < 1e-12, 1.0, self.sd)
            self.X = (X_db - self.mu) / self.sd
        else:
            self.X = X_db
        self._x2 = np.sum(self.X ** 2, axis=1)

    def _transform(self, X_query):
        if hasattr(self, 'mu'):
            return (X_query - self.mu) / self.sd
        return X_query

    def query(self, X_query, k=1, leave_self=False, self_indices=None):
        """查询 k 个最近邻。

        leave_self=True 时，self_indices 指定查询样本在库中的索引。
        """
        Xq = self._transform(X_query)
        q2 = np.sum(Xq ** 2, axis=1)
        cross = Xq @ self.X.T
        d2 = np.maximum(q2[:, None] + self._x2[None, :] - 2 * cross, 0.0)
        if leave_self and self_indices is not None:
            d2[np.arange(len(d2)), self_indices] = np.inf
        kk = min(k, d2.shape[1])
        idx = np.argpartition(d2, kth=kk - 1, axis=1)[:, :kk]
        rows = np.arange(len(idx))[:, None]
        sub = d2[rows, idx]
        order = np.argsort(sub, axis=1)
        idx_sorted = idx[rows, order]
        dist_sorted = np.sqrt(sub[rows, order])
        return idx_sorted, dist_sorted


# ============================================================
# 实验运行工具
# ============================================================

def run_knn_experiment(db_X, db_yaw, db_pitch, q_X, q_yaw, q_pitch,
                       query_self_indices=None, label="", log_transform_feats=False,
                       log_skip_cols=None):
    """运行一次 kNN 实验。

    db_X / q_X: 可以是相同的（LOO）或不同的（train→test split）。
    query_self_indices: q_X 中每个样本在 db_X 中的索引（用于 LOO 排除自身）。
    log_skip_cols: log 变换时跳过的列索引（如遮挡率列），仅当 log_transform_feats=True 时生效。
    """
    if log_transform_feats:
        db_X = log_transform(db_X, skip_cols=log_skip_cols)
        q_X  = log_transform(q_X, skip_cols=log_skip_cols)
    knn = KNN(db_X, normalize=True)
    if query_self_indices is not None:
        idx, dist = knn.query(q_X, k=max(TOP_K_LIST), leave_self=True,
                              self_indices=query_self_indices)
    else:
        idx, dist = knn.query(q_X, k=max(TOP_K_LIST), leave_self=False)
    pred_yaw = db_yaw[idx[:, 0]]
    pred_pitch = db_pitch[idx[:, 0]]
    metrics, details = evaluate_predictions(pred_yaw, pred_pitch, q_yaw, q_pitch, pred_idx=idx)
    if label:
        metrics["label"] = label
    return metrics, details, idx, dist


# ============================================================
# 结果保存
# ============================================================

def save_metrics(out_dir, metrics_list, split_info=None, extra_config=None, yaw=None, pitch=None, details=None, split_indices=None):
    """保存实验结果为 summary.json + 可选 CSV。"""
    os.makedirs(out_dir, exist_ok=True)
    result = {"metrics_table": metrics_list}
    if split_info:
        result["split"] = split_info
    if extra_config:
        result["config"] = extra_config

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"  [OK] summary 已保存: {out_dir}/summary.json")

    # 保存最佳行的详细预测 CSV
    if yaw is not None and pitch is not None and details is not None:
        csv_path = os.path.join(out_dir, "predictions.csv")
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["idx", "true_yaw", "true_pitch",
                        "pred_yaw", "pred_pitch",
                        "err_yaw_deg", "err_pitch_deg", "err_angular_deg"])
            for i in range(len(yaw)):
                w.writerow([
                    i, f"{yaw[i]:.4f}", f"{pitch[i]:.4f}",
                    f"{details['pred_yaw'][i]:.4f}",
                    f"{details['pred_pitch'][i]:.4f}",
                    f"{details['err_yaw'][i]:.4f}",
                    f"{details['err_pitch'][i]:.4f}",
                    f"{details['err_angular'][i]:.4f}",
                ])
        print(f"  [OK] CSV 已保存: {csv_path}")

    # split indices
    if split_indices:
        with open(os.path.join(out_dir, "split_indices.json"), "w", encoding="utf-8") as f:
            json.dump({k: v.tolist() if isinstance(v, np.ndarray) else v
                       for k, v in split_indices.items()}, f, indent=2)
        print(f"  [OK] split_indices 已保存: {out_dir}/split_indices.json")


def format_metrics_table(metrics_list):
    """格式化打印指标表。"""
    keys = ["label", "n_samples", "angular_err_mean", "angular_err_median",
            "angular_err_p90", "angular_err_p95", "yaw_err_mean", "pitch_err_mean",
            "top1_acc@5deg", "top5_acc@5deg", "top1_acc@10deg", "top5_acc@10deg"]
    header = (f"{'实验':<35} {'样本':>6} {'角距mean':>8} {'角距med':>8} "
              f"{'角距p90':>8} {'角距p95':>8} {'yaw mean':>8} {'pitch mean':>9} "
              f"{'Top1@5°':>8} {'Top5@5°':>8} {'Top1@10°':>9} {'Top5@10°':>9}")
    sep = "-" * len(header)
    lines = [sep, header, sep]
    for m in metrics_list:
        def g(k): return m.get(k, float('nan'))
        line = (f"{g('label'):<35} {g('n_samples'):>6} {g('angular_err_mean'):>8.2f}° "
                f"{g('angular_err_median'):>8.2f}° {g('angular_err_p90'):>8.2f}° "
                f"{g('angular_err_p95'):>8.2f}° "
                f"{g('yaw_err_mean'):>8.2f}° {g('pitch_err_mean'):>9.2f}° "
                f"{g('top1_acc@5deg'):>8.2%} {g('top5_acc@5deg'):>8.2%} "
                f"{g('top1_acc@10deg'):>9.2%} {g('top5_acc@10deg'):>9.2%}")
        lines.append(line)
    lines.append(sep)
    return "\n".join(lines)

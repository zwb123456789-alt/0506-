"""
Phase63 公平消融实验 (Supplementary Experiment 7.1)
====================================================
目的：回应"OCS 用 5 几何，图像只用 phase63，融合是否不公平"。

对比维度:
  - phase63 OCS-only MLP (feat: total/per_part/all)
  - phase63 image-only CNN (已有)
  - phase63 OCS + image feature fusion
  - concat5 OCS-only MLP (已有)
  - concat5 OCS + phase63 image fusion (已有)

只跑 OCS MLP 和 feature fusion 的新组合，其余引用已有结果。
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
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "01_code"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic
_MANIFEST_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块A_重构",
    "multi_geom_ggx_yaw73_pitch37", "run_*", "multi_geom_manifest.json")
_IMAGE_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染", "run_*", "render_log.csv")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "phase63_ablation")

EPS_DECODE = 1e-8
SEEDS = [0, 1, 2, 3, 4]

# ---- Tensor / model imports ----
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ============================================================
# 目标编码/解码 (与 train_mlp.py 一致)
# ============================================================

def encode_target(yaw_deg, pitch_deg):
    y = np.deg2rad(np.asarray(yaw_deg, dtype=float) % 360.0)
    p = np.deg2rad(np.asarray(pitch_deg, dtype=float))
    return np.stack([np.sin(y), np.cos(y), np.sin(p), np.cos(p)], axis=1).astype(np.float32)


def decode_pred(pred):
    ys, yc, ps, pc = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    yr = np.sqrt(ys ** 2 + yc ** 2) + EPS_DECODE
    pr = np.sqrt(ps ** 2 + pc ** 2) + EPS_DECODE
    yaw = (np.rad2deg(np.arctan2(ys / yr, yc / yr)) + 360.0) % 360.0
    pitch = np.rad2deg(np.arctan2(ps / pr, pc / pr))
    pitch = np.clip(pitch, -90.0, 90.0)
    return yaw, pitch


# ============================================================
# OCS MLP 模型 (与 train_mlp.py 一致)
# ============================================================

class OCSMLP(nn.Module):
    def __init__(self, input_dim, hidden=[128, 128, 64], dropout=0.10):
        super().__init__()
        layers = []
        d_in = input_dim
        for h in hidden:
            layers.append(nn.Linear(d_in, h))
            layers.append(nn.LayerNorm(h))
            layers.append(nn.SiLU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            d_in = h
        layers.append(nn.Linear(d_in, 4))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss, n = 0.0, 0
    for Xb, yb in loader:
        Xb, yb = Xb.to(device), yb.to(device)
        optimizer.zero_grad()
        loss = criterion(model(Xb), yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(Xb)
        n += len(Xb)
    return total_loss / max(n, 1)


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, n = 0.0, 0
    all_pred, all_y = [], []
    for Xb, yb in loader:
        Xb, yb = Xb.to(device), yb.to(device)
        pred = model(Xb)
        loss = criterion(pred, yb)
        total_loss += loss.item() * len(Xb)
        n += len(Xb)
        all_pred.append(pred.cpu().numpy())
        all_y.append(yb.cpu().numpy())
    return total_loss / max(n, 1), np.concatenate(all_pred), np.concatenate(all_y)


def compute_metrics(yaw_pred, pitch_pred, yaw_true, pitch_true):
    err_a = ic.angular_err_deg(yaw_pred, pitch_pred, yaw_true, pitch_true)
    return {
        "n_samples": len(yaw_true),
        "angular_err_mean": float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p90": float(np.percentile(err_a, 90)),
        "angular_err_p95": float(np.percentile(err_a, 95)),
        "hit@5deg": float(np.mean(err_a <= ic.HIT_THRESHOLD_DEG + 1e-6)),
        "hit@10deg": float(np.mean(err_a <= ic.HIT_THRESHOLD_10DEG + 1e-6)),
    }, err_a


# ============================================================
# Phase63 OCS-only MLP
# ============================================================

def train_ocs_mlp_phase63(manifest_path, feat_mode, use_log, out_dir):
    """用 phase63 单几何数据训练 OCS MLP。"""
    label_order, _, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(manifest_path)

    # 找到 phase63 几何
    phase63_label = None
    for lbl in label_order:
        if "phase63" in lbl:
            phase63_label = lbl
            break
    if phase63_label is None:
        raise RuntimeError(f"未找到 phase63 几何，可用: {label_order}")

    print(f"  使用几何: {phase63_label}")

    # 选特征
    feats_full = feat_dict[phase63_label]  # (N, 9)
    feats = ic.select_features(feats_full, feat_mode)
    yaw = yaw_dict[phase63_label]
    pitch = pitch_dict[phase63_label]

    # 10°→5° split
    split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    train_idx = split["train_idx"]
    test_idx = split["test_idx"]

    X_all = feats[train_idx]
    y_all = encode_target(yaw[train_idx], pitch[train_idx])
    X_test_raw = feats[test_idx]
    y_test = encode_target(yaw[test_idx], pitch[test_idx])

    # train 内 80/20 val
    rng = np.random.RandomState(42)
    N_train = len(X_all)
    perm = rng.permutation(N_train)
    n_val = int(N_train * 0.20)
    val_idx = perm[:n_val]
    tr_idx = perm[n_val:]

    X_train_raw, y_train = X_all[tr_idx], y_all[tr_idx]
    X_val_raw, y_val = X_all[val_idx], y_all[val_idx]

    # log transform
    if feat_mode in ("per_part", "obs_total"):
        log_skip = None
    else:
        log_skip = {2}

    if use_log:
        X_train_raw = ic.log_transform(X_train_raw, skip_cols=log_skip)
        X_val_raw = ic.log_transform(X_val_raw, skip_cols=log_skip)
        X_test_raw = ic.log_transform(X_test_raw, skip_cols=log_skip)

    # zscore (fit on train only)
    X_train, mu, sd = ic.zscore(X_train_raw, return_params=True)
    X_val = (X_val_raw - mu) / sd
    X_test = (X_test_raw - mu) / sd

    input_dim = X_train.shape[1]
    print(f"  input_dim={input_dim} train={len(X_train)} val={len(X_val)} test={len(X_test)}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    X_tr_t = torch.FloatTensor(X_train).to(device)
    y_tr_t = torch.FloatTensor(y_train).to(device)
    X_va_t = torch.FloatTensor(X_val).to(device)
    y_va_t = torch.FloatTensor(y_val).to(device)
    X_te_t = torch.FloatTensor(X_test).to(device)
    y_te_t = torch.FloatTensor(y_test).to(device)

    all_metrics = []
    for seed in SEEDS:
        torch.manual_seed(seed)
        np.random.seed(seed)

        model = OCSMLP(input_dim).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.MSELoss()

        tr_loader = DataLoader(TensorDataset(X_tr_t, y_tr_t), batch_size=64, shuffle=True)
        va_loader = DataLoader(TensorDataset(X_va_t, y_va_t), batch_size=128)

        best_val_loss = float("inf")
        best_state = None
        wait = 0

        for ep in range(1, 2001):
            tr_loss = train_epoch(model, tr_loader, optimizer, criterion, device)
            va_loss, _, _ = evaluate(model, va_loader, criterion, device)

            if va_loss < best_val_loss - 1e-8:
                best_val_loss = va_loss
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1

            if wait >= 150:
                break

        model.load_state_dict(best_state)
        te_loader = DataLoader(TensorDataset(X_te_t, y_te_t), batch_size=128)
        _, te_pred, _ = evaluate(model, te_loader, criterion, device)

        yaw_pred, pitch_pred = decode_pred(te_pred)
        m, err_a = compute_metrics(yaw_pred, pitch_pred, yaw[test_idx], pitch[test_idx])
        m["seed"] = seed
        all_metrics.append(m)

        print(f"    seed={seed}: mean={m['angular_err_mean']:.2f}° "
              f"Hit5={m['hit@5deg']:.1%} Hit10={m['hit@10deg']:.1%}")

        # save predictions
        tag = f"{feat_mode}_{'log' if use_log else 'raw'}"
        with open(os.path.join(out_dir, f"predictions_ocs_{tag}_seed{seed}.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["true_yaw", "true_pitch", "pred_yaw", "pred_pitch", "err_angular_deg"])
            for i in range(len(test_idx)):
                w.writerow([f"{yaw[test_idx[i]]:.4f}", f"{pitch[test_idx[i]]:.4f}",
                           f"{yaw_pred[i]:.4f}", f"{pitch_pred[i]:.4f}", f"{err_a[i]:.4f}"])

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # summary
    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "hit@5deg", "hit@10deg"]
    summary = {"feat": feat_mode, "transform": "log" if use_log else "raw",
               "input_dim": input_dim, "geom": phase63_label, "n_seeds": len(SEEDS)}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        summary[f"{k}_mean"] = float(np.mean(vals))
        summary[f"{k}_std"] = float(np.std(vals))

    return summary, all_metrics


# ============================================================
# Phase63 Feature Fusion (复用 train_fusion.py 模型)
# ============================================================

from train_fusion import (ImageBranch, OCSBranch, FusionHead, FusionModel,
                          load_image_array, load_image_dataset, train_epoch as fusion_train_epoch,
                          evaluate as fusion_evaluate)

# 重映射以避免与上方同名函数冲突
_fusion_train_epoch = fusion_train_epoch
_fusion_evaluate = fusion_evaluate


def train_fusion_phase63(manifest_path, image_dir, ocs_feat_mode, ocs_use_log, out_dir):
    """Phase63 OCS + Phase63 image feature fusion."""
    label_order, _, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(manifest_path)

    phase63_label = None
    for lbl in label_order:
        if "phase63" in lbl:
            phase63_label = lbl
            break

    print(f"  使用几何: {phase63_label}")

    # Load OCS
    feats_full = feat_dict[phase63_label]
    ocs_raw = ic.select_features(feats_full, ocs_feat_mode)
    yaw_ocs = yaw_dict[phase63_label]
    pitch_ocs = pitch_dict[phase63_label]

    # Load images
    print(f"  加载图像: {image_dir}")
    images, yaw_img, pitch_img = load_image_dataset(image_dir, 128, "log1p")
    print(f"  images={images.shape}")

    # Align
    img_key_to_idx = {}
    for i in range(len(yaw_img)):
        img_key_to_idx[(round(yaw_img[i], 6), round(pitch_img[i], 6))] = i

    ocs_key_to_idx = {}
    for i in range(len(yaw_ocs)):
        ocs_key_to_idx[(round(yaw_ocs[i], 6), round(pitch_ocs[i], 6))] = i

    common_keys = sorted(set(img_key_to_idx.keys()) & set(ocs_key_to_idx.keys()))
    N = len(common_keys)
    print(f"  对齐样本: {N}")

    aligned_yaw = np.array([k[0] for k in common_keys], dtype=np.float64)
    aligned_pitch = np.array([k[1] for k in common_keys], dtype=np.float64)
    aligned_images = np.zeros((N,) + images.shape[1:], dtype=np.float32)
    aligned_ocs = np.zeros((N, ocs_raw.shape[1]), dtype=np.float64)

    for i, key in enumerate(common_keys):
        aligned_images[i] = images[img_key_to_idx[key]]
        aligned_ocs[i] = ocs_raw[ocs_key_to_idx[key]]

    # Split
    split = ic.split_coarse_to_fine(aligned_yaw, aligned_pitch, coarse_step=10.0)
    train_pool_idx = split["train_idx"]
    test_idx = split["test_idx"]

    # zscore OCS (fit on train pool)
    if ocs_feat_mode in ("per_part", "obs_total"):
        log_skip = None
    else:
        log_skip = {2}

    ocs_pool = aligned_ocs[train_pool_idx].copy()
    if ocs_use_log:
        ocs_pool = ic.log_transform(ocs_pool, skip_cols=log_skip)
    ocs_pool_zs, ocs_mu, ocs_sd = ic.zscore(ocs_pool, return_params=True)

    ocs_all = aligned_ocs.copy()
    if ocs_use_log:
        ocs_all = ic.log_transform(ocs_all, skip_cols=log_skip)
    ocs_all_zs = (ocs_all - ocs_mu) / ocs_sd

    # Train/val split from train pool
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_pool_idx))
    n_val = int(len(train_pool_idx) * 0.20)
    val_local = perm[:n_val]
    tr_local = perm[n_val:]
    tr_idx = train_pool_idx[tr_local]
    val_idx = train_pool_idx[val_local]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    # Prepare tensors
    X_img_tr = torch.FloatTensor(aligned_images[tr_idx]).to(device)
    X_ocs_tr = torch.FloatTensor(ocs_all_zs[tr_idx]).to(device)
    y_tr = torch.FloatTensor(encode_target(aligned_yaw[tr_idx], aligned_pitch[tr_idx])).to(device)

    X_img_va = torch.FloatTensor(aligned_images[val_idx]).to(device)
    X_ocs_va = torch.FloatTensor(ocs_all_zs[val_idx]).to(device)
    y_va = torch.FloatTensor(encode_target(aligned_yaw[val_idx], aligned_pitch[val_idx])).to(device)

    X_img_te = torch.FloatTensor(aligned_images[test_idx]).to(device)
    X_ocs_te = torch.FloatTensor(ocs_all_zs[test_idx]).to(device)
    y_te = torch.FloatTensor(encode_target(aligned_yaw[test_idx], aligned_pitch[test_idx])).to(device)

    class FusionDataset(torch.utils.data.Dataset):
        def __init__(self, img, ocs, y):
            self.img, self.ocs, self.y = img, ocs, y
        def __len__(self):
            return len(self.img)
        def __getitem__(self, idx):
            return self.img[idx], self.ocs[idx], self.y[idx]

    tr_loader = DataLoader(FusionDataset(X_img_tr, X_ocs_tr, y_tr),
                          batch_size=32, shuffle=True)
    va_loader = DataLoader(FusionDataset(X_img_va, X_ocs_va, y_va),
                          batch_size=64)
    te_loader = DataLoader(FusionDataset(X_img_te, X_ocs_te, y_te),
                          batch_size=64)

    ocs_dim = ocs_all_zs.shape[1]
    all_metrics = []

    for seed in SEEDS:
        torch.manual_seed(seed)
        np.random.seed(seed)

        model = FusionModel(ocs_dim=ocs_dim, dropout=0.10).to(device)
        n_params = sum(p.numel() for p in model.parameters())
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.MSELoss()

        best_val_loss = float("inf")
        best_state = None
        wait = 0

        for ep in range(1, 501):
            tr_loss = _fusion_train_epoch(model, tr_loader, optimizer, criterion, device)
            va_loss, _, _ = _fusion_evaluate(model, va_loader, criterion, device)

            if va_loss < best_val_loss - 1e-8:
                best_val_loss = va_loss
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1

            if wait >= 100:
                break

        model.load_state_dict(best_state)
        _, te_pred, _ = _fusion_evaluate(model, te_loader, criterion, device)
        yaw_pred, pitch_pred = decode_pred(te_pred)
        m, err_a = compute_metrics(yaw_pred, pitch_pred,
                                   aligned_yaw[test_idx], aligned_pitch[test_idx])
        m["seed"] = seed
        m["n_params"] = n_params
        all_metrics.append(m)

        print(f"    seed={seed}: mean={m['angular_err_mean']:.2f}° "
              f"Hit5={m['hit@5deg']:.1%} Hit10={m['hit@10deg']:.1%}")

        tag = f"{ocs_feat_mode}_{'log' if ocs_use_log else 'raw'}"
        with open(os.path.join(out_dir, f"predictions_fusion_{tag}_seed{seed}.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["true_yaw", "true_pitch", "pred_yaw", "pred_pitch", "err_angular_deg"])
            for i in range(len(test_idx)):
                w.writerow([f"{aligned_yaw[test_idx[i]]:.4f}",
                           f"{aligned_pitch[test_idx[i]]:.4f}",
                           f"{yaw_pred[i]:.4f}", f"{pitch_pred[i]:.4f}",
                           f"{err_a[i]:.4f}"])

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "hit@5deg", "hit@10deg"]
    summary = {"ocs_feat": ocs_feat_mode, "ocs_transform": "log" if ocs_use_log else "raw",
               "ocs_dim": ocs_dim, "intensity": "log1p", "image_size": 128,
               "n_seeds": len(SEEDS), "geom": phase63_label}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        summary[f"{k}_mean"] = float(np.mean(vals))
        summary[f"{k}_std"] = float(np.std(vals))

    return summary, all_metrics


# ============================================================
# 主入口
# ============================================================

def _find(path_glob):
    cands = sorted(glob.glob(path_glob), key=os.path.getmtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"No match: {path_glob}")
    return cands[0]


def main():
    ap = argparse.ArgumentParser(description="Phase63 fair ablation")
    ap.add_argument("--manifest", default=None, help="multi_geom_manifest.json")
    ap.add_argument("--image-dir", default=None, help="Module B render dir")
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    if args.manifest is None:
        args.manifest = _find(_MANIFEST_GLOB)
    if args.image_dir is None:
        args.image_dir = os.path.dirname(_find(_IMAGE_GLOB))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  Phase63 公平消融实验")
    print(f"  Manifest: {args.manifest}")
    print(f"  Image dir: {args.image_dir}")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    all_summaries = {}

    # ---- A. Phase63 OCS-only MLP ----
    ocs_configs = [
        ("total", True, "total log 3D"),
        ("per_part", True, "per_part log 6D"),
        ("all", True, "all log 9D"),
        ("all", False, "all raw 9D"),
    ]

    for feat_mode, use_log, label in ocs_configs:
        print(f"\n{'='*60}")
        print(f"  [OCS-MLP] Phase63 {label}")
        print(f"{'='*60}")
        try:
            s, metrics = train_ocs_mlp_phase63(args.manifest, feat_mode, use_log, out_dir)
            all_summaries[f"ocs_mlp_phase63_{label}"] = s
            print(f"  -> mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
                  f"Hit5={s['hit@5deg_mean']:.1%}")
        except Exception as e:
            print(f"  [FAIL] {e}")
            import traceback
            traceback.print_exc()

    # ---- B. Phase63 OCS + Image Feature Fusion ----
    fusion_configs = [
        ("per_part", True, "per_part log 6D"),
        ("total", True, "total log 3D"),
    ]

    for feat_mode, use_log, label in fusion_configs:
        print(f"\n{'='*60}")
        print(f"  [Fusion] Phase63 OCS({label}) + Image")
        print(f"{'='*60}")
        try:
            s, metrics = train_fusion_phase63(args.manifest, args.image_dir,
                                              feat_mode, use_log, out_dir)
            all_summaries[f"fusion_phase63_{label}"] = s
            print(f"  -> mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
                  f"Hit5={s['hit@5deg_mean']:.1%}")
        except Exception as e:
            print(f"  [FAIL] {e}")
            import traceback
            traceback.print_exc()

    # ---- C. Save summary ----
    with open(os.path.join(out_dir, "ablation_summary.json"), "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2, ensure_ascii=False)

    # Print final comparison table
    print(f"\n{'='*90}")
    print("  Phase63 Fair Ablation - Final Comparison")
    print(f"{'='*90}")
    print(f"{'Experiment':<40} {'mean':>8} {'std':>6} {'Hit5':>8} {'Hit10':>8}")
    print("-" * 75)
    for name, s in all_summaries.items():
        print(f"{name:<40} {s['angular_err_mean_mean']:>7.2f}° "
              f"{s['angular_err_mean_std']:>5.2f} "
              f"{s['hit@5deg_mean']:>7.1%} {s['hit@10deg_mean']:>7.1%}")

    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

"""
随机 80/20 Split 实验 (Supplementary Experiment 7.2)
=====================================================
目的：回应数据量小和 10°->5° split 是否特殊的质疑。

跑 4 个关键模型:
  - OCS MLP all_raw (45D)
  - OCS MLP per_part_log (30D)
  - CNN image-only (log1p, 128x128)
  - Feature fusion per_part_log

每个模型 5 seeds, random 80/10/10 split, 报告 mean/std.
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
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "random_split")

EPS_DECODE = 1e-8
SEEDS = [0, 1, 2, 3, 4]

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ============================================================
# 目标编码/解码
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
# OCS MLP 模型
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
    for batch in loader:
        if len(batch) == 2:
            Xb, yb = batch
            Xb, yb = Xb.to(device), yb.to(device)
            pred = model(Xb)
        else:
            X_img, X_ocs, yb = batch
            X_img, X_ocs, yb = X_img.to(device), X_ocs.to(device), yb.to(device)
            pred = model(X_img, X_ocs)
        optimizer.zero_grad()
        loss = criterion(pred, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(yb)
        n += len(yb)
    return total_loss / max(n, 1)


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, n = 0.0, 0
    all_pred, all_y = [], []
    for batch in loader:
        if len(batch) == 2:
            Xb, yb = batch
            Xb, yb = Xb.to(device), yb.to(device)
            pred = model(Xb)
        else:
            X_img, X_ocs, yb = batch
            X_img, X_ocs, yb = X_img.to(device), X_ocs.to(device), yb.to(device)
            pred = model(X_img, X_ocs)
        loss = criterion(pred, yb)
        total_loss += loss.item() * len(yb)
        n += len(yb)
        all_pred.append(pred.cpu().numpy())
        all_y.append(yb.cpu().numpy())
    return total_loss / max(n, 1), np.concatenate(all_pred), np.concatenate(all_y)


# ============================================================
# 1. OCS MLP with random split
# ============================================================

def run_ocs_mlp_random(manifest_path, feat_mode, use_log, out_dir):
    label_order, _, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(manifest_path)
    feats, yaw, pitch, _ = ic.build_concat_features_with_mode(
        feat_dict, yaw_dict, pitch_dict, label_order, feat_mode)

    N = len(yaw)
    split = ic.split_random(N, train_ratio=0.80, val_ratio=0.10, seed=42)
    train_idx = split["train_idx"]
    val_idx = split["val_idx"]
    test_idx = split["test_idx"]

    print(f"  Random split: train={len(train_idx)} val={len(val_idx)} test={len(test_idx)}")

    X_train_raw = feats[train_idx]
    y_train = encode_target(yaw[train_idx], pitch[train_idx])
    X_val_raw = feats[val_idx]
    y_val = encode_target(yaw[val_idx], pitch[val_idx])
    X_test_raw = feats[test_idx]
    y_test = encode_target(yaw[test_idx], pitch[test_idx])

    if feat_mode in ("per_part", "obs_total"):
        log_skip = None
    else:
        log_skip = {2}

    if use_log:
        X_train_raw = ic.log_transform(X_train_raw, skip_cols=log_skip)
        X_val_raw = ic.log_transform(X_val_raw, skip_cols=log_skip)
        X_test_raw = ic.log_transform(X_test_raw, skip_cols=log_skip)

    X_train, mu, sd = ic.zscore(X_train_raw, return_params=True)
    X_val = (X_val_raw - mu) / sd
    X_test = (X_test_raw - mu) / sd

    input_dim = X_train.shape[1]
    print(f"  input_dim={input_dim}")

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
        m, err_a = compute_metrics(yaw_pred, pitch_pred,
                                   yaw[test_idx], pitch[test_idx])
        m["seed"] = seed
        all_metrics.append(m)

        print(f"    seed={seed}: mean={m['angular_err_mean']:.2f}° "
              f"Hit5={m['hit@5deg']:.1%} Hit10={m['hit@10deg']:.1%}")

        tag = f"{feat_mode}_{'log' if use_log else 'raw'}"
        with open(os.path.join(out_dir, f"pred_ocs_{tag}_seed{seed}.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["true_yaw","true_pitch","pred_yaw","pred_pitch","err_angular_deg"])
            for i in range(len(test_idx)):
                w.writerow([f"{yaw[test_idx[i]]:.4f}", f"{pitch[test_idx[i]]:.4f}",
                           f"{yaw_pred[i]:.4f}", f"{pitch_pred[i]:.4f}", f"{err_a[i]:.4f}"])

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "hit@5deg", "hit@10deg"]
    s = {"feat": feat_mode, "transform": "log" if use_log else "raw",
         "input_dim": input_dim, "split": "random_80_10_10", "n_seeds": len(SEEDS)}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s, all_metrics


# ============================================================
# 2. CNN image-only with random split
# ============================================================

from PIL import Image

def load_image_array(path, img_size, intensity_mode):
    img = Image.open(path).convert("L")
    if img.size != (img_size, img_size):
        img = img.resize((img_size, img_size), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    if intensity_mode == "log1p":
        arr = np.log1p(10.0 * arr) / np.log1p(10.0)
    return arr[None, :, :]


def load_images(image_dir, img_size, intensity_mode):
    csv_path = os.path.join(image_dir, "render_log.csv")
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            prefix = r.get("out_prefix", r.get("filename", ""))
            fname = prefix + "_brdf.png"
            path = os.path.join(image_dir, "brdf_images", fname)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image missing: {path}")
            rows.append({"yaw": float(r["yaw"]), "pitch": float(r["pitch"]), "path": path})

    N = len(rows)
    yaw = np.array([r["yaw"] for r in rows], dtype=np.float64)
    pitch = np.array([r["pitch"] for r in rows], dtype=np.float64)

    first = load_image_array(rows[0]["path"], img_size, intensity_mode)
    C, H, W = first.shape
    images = np.zeros((N, C, H, W), dtype=np.float32)
    images[0] = first
    for i in range(1, N):
        images[i] = load_image_array(rows[i]["path"], img_size, intensity_mode)
    print(f"  Loaded {N} images, shape={images.shape}")
    return images, yaw, pitch


class TinyCNN(nn.Module):
    def __init__(self, in_ch=1):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_ch, 16, 3, padding=1), nn.GroupNorm(4, 16), nn.SiLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.GroupNorm(8, 32), nn.SiLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.GroupNorm(8, 64), nn.SiLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.GroupNorm(16, 128), nn.SiLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.SiLU(),
            nn.Linear(64, 4),
        )

    def forward(self, x):
        return self.head(self.features(x))


def run_cnn_random(image_dir, out_dir):
    images, yaw, pitch = load_images(image_dir, 128, "log1p")

    split = ic.split_random(len(yaw), train_ratio=0.80, val_ratio=0.10, seed=42)
    train_idx = split["train_idx"]
    val_idx = split["val_idx"]
    test_idx = split["test_idx"]

    print(f"  Random split: train={len(train_idx)} val={len(val_idx)} test={len(test_idx)}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    all_metrics = []
    for seed in SEEDS:
        torch.manual_seed(seed)
        np.random.seed(seed)

        X_tr = torch.FloatTensor(images[train_idx]).to(device)
        y_tr = torch.FloatTensor(encode_target(yaw[train_idx], pitch[train_idx])).to(device)
        X_va = torch.FloatTensor(images[val_idx]).to(device)
        y_va = torch.FloatTensor(encode_target(yaw[val_idx], pitch[val_idx])).to(device)
        X_te = torch.FloatTensor(images[test_idx]).to(device)
        y_te = torch.FloatTensor(encode_target(yaw[test_idx], pitch[test_idx])).to(device)

        model = TinyCNN().to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.MSELoss()

        tr_loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=32, shuffle=True)
        va_loader = DataLoader(TensorDataset(X_va, y_va), batch_size=64)

        best_val_loss = float("inf")
        best_state = None
        wait = 0

        for ep in range(1, 501):
            tr_loss = train_epoch(model, tr_loader, optimizer, criterion, device)
            va_loss, _, _ = evaluate(model, va_loader, criterion, device)
            if va_loss < best_val_loss - 1e-8:
                best_val_loss = va_loss
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
            if wait >= 100:
                break

        model.load_state_dict(best_state)
        te_loader = DataLoader(TensorDataset(X_te, y_te), batch_size=64)
        _, te_pred, _ = evaluate(model, te_loader, criterion, device)
        yaw_pred, pitch_pred = decode_pred(te_pred)
        m, err_a = compute_metrics(yaw_pred, pitch_pred,
                                   yaw[test_idx], pitch[test_idx])
        m["seed"] = seed
        all_metrics.append(m)
        print(f"    seed={seed}: mean={m['angular_err_mean']:.2f}° "
              f"Hit5={m['hit@5deg']:.1%} Hit10={m['hit@10deg']:.1%}")

        with open(os.path.join(out_dir, f"pred_cnn_seed{seed}.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["true_yaw","true_pitch","pred_yaw","pred_pitch","err_angular_deg"])
            for i in range(len(test_idx)):
                w.writerow([f"{yaw[test_idx[i]]:.4f}", f"{pitch[test_idx[i]]:.4f}",
                           f"{yaw_pred[i]:.4f}", f"{pitch_pred[i]:.4f}", f"{err_a[i]:.4f}"])

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "hit@5deg", "hit@10deg"]
    s = {"model": "TinyCNN", "intensity": "log1p", "image_size": 128,
         "split": "random_80_10_10", "n_seeds": len(SEEDS)}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s, all_metrics


# ============================================================
# 3. Feature Fusion with random split
# ============================================================

from train_fusion import (ImageBranch, OCSBranch, FusionHead, FusionModel)

def run_fusion_random(manifest_path, image_dir, ocs_feat_mode, ocs_use_log, out_dir):
    # Load OCS
    label_order, _, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(manifest_path)
    ocs_raw, yaw_ocs, pitch_ocs, _ = ic.build_concat_features_with_mode(
        feat_dict, yaw_dict, pitch_dict, label_order, ocs_feat_mode)

    # Load images
    images, yaw_img, pitch_img = load_images(image_dir, 128, "log1p")

    # Align
    img_key = {(round(yaw_img[i],6), round(pitch_img[i],6)): i for i in range(len(yaw_img))}
    ocs_key = {(round(yaw_ocs[i],6), round(pitch_ocs[i],6)): i for i in range(len(yaw_ocs))}
    common = sorted(set(img_key.keys()) & set(ocs_key.keys()))
    N = len(common)
    print(f"  Aligned: {N}")

    aligned_yaw = np.array([k[0] for k in common], dtype=np.float64)
    aligned_pitch = np.array([k[1] for k in common], dtype=np.float64)
    aligned_img = np.zeros((N,) + images.shape[1:], dtype=np.float32)
    aligned_ocs = np.zeros((N, ocs_raw.shape[1]), dtype=np.float64)
    for i, k in enumerate(common):
        aligned_img[i] = images[img_key[k]]
        aligned_ocs[i] = ocs_raw[ocs_key[k]]

    # Random split
    split = ic.split_random(N, train_ratio=0.80, val_ratio=0.10, seed=42)
    train_idx = split["train_idx"]
    val_idx = split["val_idx"]
    test_idx = split["test_idx"]

    # zscore OCS (fit train only)
    if ocs_feat_mode in ("per_part", "obs_total"):
        log_skip = None
    else:
        log_skip = {2}

    ocs_train = aligned_ocs[train_idx].copy()
    if ocs_use_log:
        ocs_train = ic.log_transform(ocs_train, skip_cols=log_skip)
    ocs_train_zs, ocs_mu, ocs_sd = ic.zscore(ocs_train, return_params=True)

    ocs_all = aligned_ocs.copy()
    if ocs_use_log:
        ocs_all = ic.log_transform(ocs_all, skip_cols=log_skip)
    ocs_all_zs = (ocs_all - ocs_mu) / ocs_sd

    ocs_dim = ocs_all_zs.shape[1]
    print(f"  OCS dim={ocs_dim}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    X_img_tr = torch.FloatTensor(aligned_img[train_idx]).to(device)
    X_ocs_tr = torch.FloatTensor(ocs_all_zs[train_idx]).to(device)
    y_tr = torch.FloatTensor(encode_target(aligned_yaw[train_idx],
                                           aligned_pitch[train_idx])).to(device)
    X_img_va = torch.FloatTensor(aligned_img[val_idx]).to(device)
    X_ocs_va = torch.FloatTensor(ocs_all_zs[val_idx]).to(device)
    y_va = torch.FloatTensor(encode_target(aligned_yaw[val_idx],
                                           aligned_pitch[val_idx])).to(device)
    X_img_te = torch.FloatTensor(aligned_img[test_idx]).to(device)
    X_ocs_te = torch.FloatTensor(ocs_all_zs[test_idx]).to(device)
    y_te = torch.FloatTensor(encode_target(aligned_yaw[test_idx],
                                           aligned_pitch[test_idx])).to(device)

    class FD(torch.utils.data.Dataset):
        def __init__(self, img, ocs, y):
            self.img, self.ocs, self.y = img, ocs, y
        def __len__(self): return len(self.img)
        def __getitem__(self, idx): return self.img[idx], self.ocs[idx], self.y[idx]

    all_metrics = []
    for seed in SEEDS:
        torch.manual_seed(seed)
        np.random.seed(seed)

        model = FusionModel(ocs_dim=ocs_dim, dropout=0.10).to(device)
        n_params = sum(p.numel() for p in model.parameters())
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.MSELoss()

        tr_loader = DataLoader(FD(X_img_tr, X_ocs_tr, y_tr), batch_size=32, shuffle=True)
        va_loader = DataLoader(FD(X_img_va, X_ocs_va, y_va), batch_size=64)

        best_val_loss = float("inf")
        best_state = None
        wait = 0

        for ep in range(1, 501):
            tr_loss = train_epoch(model, tr_loader, optimizer, criterion, device)
            va_loss, _, _ = evaluate(model, va_loader, criterion, device)
            if va_loss < best_val_loss - 1e-8:
                best_val_loss = va_loss
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
            if wait >= 100:
                break

        model.load_state_dict(best_state)
        te_loader = DataLoader(FD(X_img_te, X_ocs_te, y_te), batch_size=64)
        _, te_pred, _ = evaluate(model, te_loader, criterion, device)
        yaw_pred, pitch_pred = decode_pred(te_pred)
        m, err_a = compute_metrics(yaw_pred, pitch_pred,
                                   aligned_yaw[test_idx], aligned_pitch[test_idx])
        m["seed"] = seed
        m["n_params"] = n_params
        all_metrics.append(m)

        print(f"    seed={seed}: mean={m['angular_err_mean']:.2f}° "
              f"Hit5={m['hit@5deg']:.1%} Hit10={m['hit@10deg']:.1%}")

        tag = f"{ocs_feat_mode}_{'log' if ocs_use_log else 'raw'}"
        with open(os.path.join(out_dir, f"pred_fusion_{tag}_seed{seed}.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["true_yaw","true_pitch","pred_yaw","pred_pitch","err_angular_deg"])
            for i in range(len(test_idx)):
                w.writerow([f"{aligned_yaw[test_idx[i]]:.4f}",
                           f"{aligned_pitch[test_idx[i]]:.4f}",
                           f"{yaw_pred[i]:.4f}", f"{pitch_pred[i]:.4f}",
                           f"{err_a[i]:.4f}"])

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "hit@5deg", "hit@10deg"]
    s = {"ocs_feat": ocs_feat_mode, "ocs_transform": "log" if ocs_use_log else "raw",
         "ocs_dim": ocs_dim, "split": "random_80_10_10", "n_seeds": len(SEEDS)}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s, all_metrics


# ============================================================
# 主入口
# ============================================================

def _find(pat):
    cands = sorted(glob.glob(pat), key=os.path.getmtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"No match: {pat}")
    return cands[0]


def main():
    ap = argparse.ArgumentParser(description="Random 80/20 split experiments")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--image-dir", default=None)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    args = ap.parse_args()

    if args.manifest is None:
        args.manifest = _find(_MANIFEST_GLOB)
    if args.image_dir is None:
        args.image_dir = os.path.dirname(_find(_IMAGE_GLOB))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  Random 80/20 Split Experiments")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    all_summaries = {}

    # ---- OCS MLP all_raw ----
    print(f"\n{'='*60}")
    print("  [1/4] OCS MLP all_raw 45D (random split)")
    print(f"{'='*60}")
    try:
        s, _ = run_ocs_mlp_random(args.manifest, "all", False, out_dir)
        all_summaries["ocs_mlp_all_raw"] = s
        print(f"  -> mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
              f"Hit5={s['hit@5deg_mean']:.1%}")
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback; traceback.print_exc()

    # ---- OCS MLP per_part_log ----
    print(f"\n{'='*60}")
    print("  [2/4] OCS MLP per_part_log 30D (random split)")
    print(f"{'='*60}")
    try:
        s, _ = run_ocs_mlp_random(args.manifest, "per_part", True, out_dir)
        all_summaries["ocs_mlp_per_part_log"] = s
        print(f"  -> mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
              f"Hit5={s['hit@5deg_mean']:.1%}")
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback; traceback.print_exc()

    # ---- CNN image-only ----
    print(f"\n{'='*60}")
    print("  [3/4] CNN image-only (random split)")
    print(f"{'='*60}")
    try:
        s, _ = run_cnn_random(args.image_dir, out_dir)
        all_summaries["cnn_image_only"] = s
        print(f"  -> mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
              f"Hit5={s['hit@5deg_mean']:.1%}")
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback; traceback.print_exc()

    # ---- Feature fusion per_part_log ----
    print(f"\n{'='*60}")
    print("  [4/4] Feature Fusion per_part_log (random split)")
    print(f"{'='*60}")
    try:
        s, _ = run_fusion_random(args.manifest, args.image_dir, "per_part", True, out_dir)
        all_summaries["fusion_per_part_log"] = s
        print(f"  -> mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
              f"Hit5={s['hit@5deg_mean']:.1%}")
    except Exception as e:
        print(f"  [FAIL] {e}")
        import traceback; traceback.print_exc()

    # ---- Save ----
    with open(os.path.join(out_dir, "random_split_summary.json"), "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print("  Random Split - Final")
    print(f"{'='*80}")
    print(f"{'Experiment':<35} {'mean':>8} {'std':>6} {'Hit5':>8} {'Hit10':>8}")
    print("-" * 65)
    for name, s in all_summaries.items():
        print(f"{name:<35} {s['angular_err_mean_mean']:>7.2f}° "
              f"{s['angular_err_mean_std']:>5.2f} "
              f"{s['hit@5deg_mean']:>7.1%} {s['hit@10deg_mean']:>7.1%}")

    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

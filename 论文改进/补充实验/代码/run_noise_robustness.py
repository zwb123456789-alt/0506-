"""
OCS 噪声鲁棒性实验 (Supplementary Experiment 8.2)
=====================================================
目的：贴近真实观测噪声，测试模型对 OCS 测量噪声的鲁棒性。

噪声设置:
  - relative Gaussian noise: 0% (clean), 1%, 5%, 10%, 20%
  - 加在 ocs_with_occ 上 (最接近真实观测值)
  - 训练时加噪 (模拟有噪训练数据)，测试时也加噪 (模拟有噪观测)

模型:
  - OCS MLP per_part_log (30D) - 最实用的 OCS-only 模型
  - Feature fusion per_part_log - 融合模型，测试图像能否补偿 OCS 噪声
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
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "noise_robustness")

EPS_DECODE = 1e-8
SEEDS = [0, 1, 2, 3, 4]
NOISE_LEVELS = [0.0, 0.01, 0.05, 0.10, 0.20]

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from PIL import Image


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
        "angular_err_mean": float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p90": float(np.percentile(err_a, 90)),
        "hit@5deg": float(np.mean(err_a <= 5.0 + 1e-6)),
        "hit@10deg": float(np.mean(err_a <= 10.0 + 1e-6)),
    }, err_a


def add_ocs_noise(feats, noise_level, seed, skip_cols={2}):
    """Add relative Gaussian noise to OCS features.

    Noise is only added to OCS value columns (not occlusion ratio columns).
    For concat5 features, skip_cols are the occlusion ratio columns for each geom.
    """
    rng = np.random.RandomState(seed)
    noisy = feats.copy()
    n_cols = feats.shape[1]

    for c in range(n_cols):
        if c in skip_cols:
            continue
        col = feats[:, c]
        # Relative noise: sigma = noise_level * abs(value)
        # Clip to avoid zero-sigma for zero values
        sigma = noise_level * np.maximum(np.abs(col), 1e-9)
        noise = rng.randn(len(col)) * sigma
        noisy[:, c] = col + noise

    return noisy


class OCSMLP(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        layers = []
        d_in = input_dim
        for h in [128, 128, 64]:
            layers.append(nn.Linear(d_in, h))
            layers.append(nn.LayerNorm(h))
            layers.append(nn.SiLU())
            layers.append(nn.Dropout(0.10))
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


def run_ocs_mlp_noise(ocs_feats, yaw, pitch, split, noise_level, out_dir, feat_mode):
    """Train OCS MLP with noise at given level."""
    train_idx = split["train_idx"]
    test_idx = split["test_idx"]

    # Train pool -> 80/20
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_idx))
    n_val = int(len(train_idx) * 0.20)
    val_local = perm[:n_val]
    tr_local = perm[n_val:]
    tr_idx = train_idx[tr_local]
    val_idx = train_idx[val_local]

    X_train = ocs_feats[tr_idx].copy()
    X_val = ocs_feats[val_idx].copy()
    X_test = ocs_feats[test_idx].copy()

    # Add noise to all splits (different seeds for each)
    if noise_level > 0:
        X_train = add_ocs_noise(X_train, noise_level, seed=100, skip_cols={2})
        X_val = add_ocs_noise(X_val, noise_level, seed=200, skip_cols={2})
        X_test = add_ocs_noise(X_test, noise_level, seed=300, skip_cols={2})

    # Log transform + zscore
    X_train, mu, sd = ic.zscore(ic.log_transform(X_train, skip_cols={2}), return_params=True)
    X_val = (ic.log_transform(X_val, skip_cols={2}) - mu) / sd
    X_test_zs = (ic.log_transform(X_test, skip_cols={2}) - mu) / sd

    y_tr = encode_target(yaw[tr_idx], pitch[tr_idx])
    y_va = encode_target(yaw[val_idx], pitch[val_idx])
    y_te = encode_target(yaw[test_idx], pitch[test_idx])

    device = "cuda" if torch.cuda.is_available() else "cpu"

    X_tr_t = torch.FloatTensor(X_train).to(device)
    y_tr_t = torch.FloatTensor(y_tr).to(device)
    X_va_t = torch.FloatTensor(X_val).to(device)
    y_va_t = torch.FloatTensor(y_va).to(device)
    X_te_t = torch.FloatTensor(X_test_zs).to(device)
    y_te_t = torch.FloatTensor(y_te).to(device)

    all_metrics = []
    for seed in SEEDS:
        torch.manual_seed(seed)
        np.random.seed(seed)

        model = OCSMLP(X_train.shape[1]).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.MSELoss()

        tr_loader = DataLoader(TensorDataset(X_tr_t, y_tr_t), batch_size=64, shuffle=True)
        va_loader = DataLoader(TensorDataset(X_va_t, y_va_t), batch_size=128)

        best_va = float("inf")
        best_state = None
        wait = 0
        for ep in range(1, 2001):
            tr_loss = train_epoch(model, tr_loader, optimizer, criterion, device)
            va_loss, _, _ = evaluate(model, va_loader, criterion, device)
            if va_loss < best_va - 1e-8:
                best_va = va_loss
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

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90", "hit@5deg", "hit@10deg"]
    s = {"noise_level": noise_level, "model": "OCS MLP per_part_log", "feat": feat_mode}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s


def main():
    ap = argparse.ArgumentParser(description="OCS noise robustness")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    args = ap.parse_args()

    if args.manifest is None:
        cands = sorted(glob.glob(_MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No manifest: {_MANIFEST_GLOB}")
        args.manifest = cands[0]

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  OCS Noise Robustness")
    print(f"  Manifest: {args.manifest}")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    # Load OCS data (per_part mode, concat5)
    label_order, _, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(args.manifest)
    ocs_feats, yaw, pitch, _ = ic.build_concat_features_with_mode(
        feat_dict, yaw_dict, pitch_dict, label_order, "per_part")
    print(f"  OCS dim={ocs_feats.shape[1]}, N={len(yaw)}")

    # Split 10->5
    split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    print(f"  Split: train={split['n_train']} test={split['n_test']}")

    # Run for each noise level
    all_summaries = []
    for nl in NOISE_LEVELS:
        print(f"\n  Noise level: {nl:.0%}")
        s = run_ocs_mlp_noise(ocs_feats, yaw, pitch, split, nl, out_dir, "per_part")
        all_summaries.append(s)
        print(f"    mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
              f"Hit5={s['hit@5deg_mean']:.1%} Hit10={s['hit@10deg_mean']:.1%}")

    # Print summary table
    print(f"\n{'='*80}")
    print("  Noise Robustness Summary")
    print(f"{'='*80}")
    print(f"{'Noise':>7} {'mean':>8} {'std':>6} {'p90':>8} {'Hit5':>8} {'Hit10':>8}")
    print("-" * 55)
    for s in all_summaries:
        print(f"{s['noise_level']:>6.0%} "
              f"{s['angular_err_mean_mean']:>7.2f}° {s['angular_err_mean_std']:>5.2f} "
              f"{s['angular_err_p90_mean']:>7.2f}° "
              f"{s['hit@5deg_mean']:>7.1%} {s['hit@10deg_mean']:>7.1%}")

    with open(os.path.join(out_dir, "noise_summary.json"), "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

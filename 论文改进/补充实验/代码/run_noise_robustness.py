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


def add_ocs_noise(feats, noise_level, seed, skip_cols=None):
    """Add relative Gaussian noise to OCS features.

    concat5 per_part (feats[:, 3:]) 全部为 OCS 值列, 无遮挡率列, 故 skip_cols=None。
    若将来用 total/all 模式, 需传入遮挡率列索引以跳过。
    """
    if skip_cols is None:
        skip_cols = set()
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


# ---- Fusion 模型 (复用 train_fusion.py 结构) -----------------------------

class ImageBranch(nn.Module):
    """TinyCNN backbone: Conv/GN/SiLU/Pool x4 -> AdaptiveAvgPool -> Linear->64."""
    def __init__(self, in_ch=1):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, 16, 3, padding=1), nn.GroupNorm(4, 16), nn.SiLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.GroupNorm(8, 32), nn.SiLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.GroupNorm(8, 64), nn.SiLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.GroupNorm(16, 128), nn.SiLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.proj = nn.Sequential(nn.Flatten(), nn.Linear(128, 64), nn.SiLU())

    def forward(self, x):
        return self.proj(self.conv(x))


class OCSBranch(nn.Module):
    def __init__(self, input_dim, dropout=0.10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128), nn.LayerNorm(128), nn.SiLU(), nn.Dropout(dropout),
            nn.Linear(128, 64), nn.LayerNorm(64), nn.SiLU(),
        )

    def forward(self, x):
        return self.net(x)


class FusionModel(nn.Module):
    def __init__(self, ocs_dim, dropout=0.10):
        super().__init__()
        self.img_branch = ImageBranch()
        self.ocs_branch = OCSBranch(ocs_dim, dropout)
        self.fusion_head = nn.Sequential(
            nn.Linear(128, 128), nn.LayerNorm(128), nn.SiLU(), nn.Dropout(dropout),
            nn.Linear(128, 64), nn.SiLU(),
            nn.Linear(64, 4),
        )

    def forward(self, img, ocs):
        f_img = self.img_branch(img)
        f_ocs = self.ocs_branch(ocs)
        return self.fusion_head(torch.cat([f_img, f_ocs], dim=1))


def load_image_array(path, img_size, intensity_mode):
    img = Image.open(path).convert("L")
    if img.size != (img_size, img_size):
        img = img.resize((img_size, img_size), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    if intensity_mode == "log1p":
        arr = np.log1p(10.0 * arr) / np.log1p(10.0)
    return arr[None, :, :]


def load_images(image_dir, img_size=128, intensity_mode="log1p"):
    """加载全部图像, 返回 images(N,1,H,W), yaw(N,), pitch(N,)."""
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
    images = np.zeros((N,) + first.shape, dtype=np.float32)
    images[0] = first
    for i in range(1, N):
        images[i] = load_image_array(rows[i]["path"], img_size, intensity_mode)
    return images, yaw, pitch


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
        X_train = add_ocs_noise(X_train, noise_level, seed=100, skip_cols=None)
        X_val = add_ocs_noise(X_val, noise_level, seed=200, skip_cols=None)
        X_test = add_ocs_noise(X_test, noise_level, seed=300, skip_cols=None)

    # Log transform + zscore (per_part 全为 OCS 值列, 不跳过任何列)
    X_train, mu, sd = ic.zscore(ic.log_transform(X_train, skip_cols=None), return_params=True)
    X_val = (ic.log_transform(X_val, skip_cols=None) - mu) / sd
    X_test_zs = (ic.log_transform(X_test, skip_cols=None) - mu) / sd

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


def run_fusion_noise(images, ocs_feats, yaw, pitch, split, noise_level, feat_mode="per_part",
                     epochs=500, patience=100):
    """Train Feature-fusion model with OCS noise (images stay clean).

    测试图像能否补偿 OCS 测量噪声。OCS per_part log + zscore，图像 log1p。
    """
    train_idx = split["train_idx"]
    test_idx = split["test_idx"]

    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_idx))
    n_val = int(len(train_idx) * 0.20)
    tr_idx = train_idx[perm[n_val:]]
    val_idx = train_idx[perm[:n_val]]

    # OCS: copy → noise → log → zscore (fit on train)
    X_tr_ocs = ocs_feats[tr_idx].copy()
    X_va_ocs = ocs_feats[val_idx].copy()
    X_te_ocs = ocs_feats[test_idx].copy()
    if noise_level > 0:
        X_tr_ocs = add_ocs_noise(X_tr_ocs, noise_level, seed=100, skip_cols=None)
        X_va_ocs = add_ocs_noise(X_va_ocs, noise_level, seed=200, skip_cols=None)
        X_te_ocs = add_ocs_noise(X_te_ocs, noise_level, seed=300, skip_cols=None)
    X_tr_ocs, mu, sd = ic.zscore(ic.log_transform(X_tr_ocs, skip_cols=None), return_params=True)
    X_va_ocs = (ic.log_transform(X_va_ocs, skip_cols=None) - mu) / sd
    X_te_ocs = (ic.log_transform(X_te_ocs, skip_cols=None) - mu) / sd

    y_tr = encode_target(yaw[tr_idx], pitch[tr_idx])
    y_va = encode_target(yaw[val_idx], pitch[val_idx])
    y_te = encode_target(yaw[test_idx], pitch[test_idx])

    device = "cuda" if torch.cuda.is_available() else "cpu"

    X_img_tr = torch.FloatTensor(images[tr_idx]).to(device)
    X_img_va = torch.FloatTensor(images[val_idx]).to(device)
    X_img_te = torch.FloatTensor(images[test_idx]).to(device)
    X_ocs_tr = torch.FloatTensor(X_tr_ocs).to(device)
    X_ocs_va = torch.FloatTensor(X_va_ocs).to(device)
    X_ocs_te = torch.FloatTensor(X_te_ocs).to(device)
    y_tr_t = torch.FloatTensor(y_tr).to(device)
    y_va_t = torch.FloatTensor(y_va).to(device)
    y_te_t = torch.FloatTensor(y_te).to(device)

    def make_loader(img, ocs, y, bs, shuffle):
        return DataLoader(TensorDataset(img, ocs, y), batch_size=bs, shuffle=shuffle)

    all_metrics = []
    for seed in SEEDS:
        torch.manual_seed(seed)
        np.random.seed(seed)

        model = FusionModel(ocs_dim=ocs_feats.shape[1]).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.MSELoss()

        tr_loader = make_loader(X_img_tr, X_ocs_tr, y_tr_t, 32, True)
        va_loader = make_loader(X_img_va, X_ocs_va, y_va_t, 64, False)

        best_va, best_state, wait = float("inf"), None, 0
        for ep in range(1, epochs + 1):
            train_epoch(model, tr_loader, optimizer, criterion, device)
            va_loss, _, _ = evaluate(model, va_loader, criterion, device)
            if va_loss < best_va - 1e-8:
                best_va = va_loss
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
            if wait >= patience:
                break

        model.load_state_dict(best_state)
        te_loader = make_loader(X_img_te, X_ocs_te, y_te_t, 64, False)
        _, te_pred, _ = evaluate(model, te_loader, criterion, device)
        yaw_pred, pitch_pred = decode_pred(te_pred)
        m, _ = compute_metrics(yaw_pred, pitch_pred, yaw[test_idx], pitch[test_idx])
        m["seed"] = seed
        all_metrics.append(m)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90", "hit@5deg", "hit@10deg"]
    s = {"noise_level": noise_level, "model": "Feature Fusion per_part_log", "feat": feat_mode}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s


def main():
    ap = argparse.ArgumentParser(description="OCS noise robustness")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--image-dir", default=None)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--no-fusion", action="store_true",
                    help="只跑 OCS-only, 跳过 fusion 补偿实验")
    args = ap.parse_args()

    if args.manifest is None:
        cands = sorted(glob.glob(_MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No manifest: {_MANIFEST_GLOB}")
        args.manifest = cands[0]
    if args.image_dir is None:
        cands = sorted(glob.glob(_IMAGE_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No image dir: {_IMAGE_GLOB}")
        args.image_dir = os.path.dirname(cands[0])

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  OCS Noise Robustness")
    print(f"  Manifest: {args.manifest}")
    print(f"  Image dir: {args.image_dir}")
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

    # ---- OCS-only noise sweep ----
    print(f"\n{'='*70}\n  [1/2] OCS-only MLP noise sweep\n{'='*70}")
    ocs_summaries = []
    for nl in NOISE_LEVELS:
        print(f"\n  Noise level: {nl:.0%}")
        s = run_ocs_mlp_noise(ocs_feats, yaw, pitch, split, nl, out_dir, "per_part")
        ocs_summaries.append(s)
        print(f"    mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
              f"Hit5={s['hit@5deg_mean']:.1%} Hit10={s['hit@10deg_mean']:.1%}")

    # ---- Fusion noise sweep (images clean, OCS noisy) ----
    fusion_summaries = []
    if not args.no_fusion:
        print(f"\n{'='*70}\n  [2/2] Feature Fusion noise sweep (image clean, OCS noisy)\n{'='*70}")
        # Load + align images to OCS by (yaw, pitch)
        images, yaw_img, pitch_img = load_images(args.image_dir)
        print(f"  Loaded {len(yaw_img)} images, shape={images.shape}")

        img_key = {(round(yaw_img[i], 6), round(pitch_img[i], 6)): i for i in range(len(yaw_img))}
        ocs_key = {(round(yaw[i], 6), round(pitch[i], 6)): i for i in range(len(yaw))}
        common = sorted(set(img_key) & set(ocs_key))
        print(f"  Aligned N_common={len(common)} (img={len(yaw_img)} ocs={len(yaw)})")

        a_yaw = np.array([k[0] for k in common], dtype=np.float64)
        a_pitch = np.array([k[1] for k in common], dtype=np.float64)
        a_images = np.stack([images[img_key[k]] for k in common]).astype(np.float32)
        a_ocs = np.stack([ocs_feats[ocs_key[k]] for k in common]).astype(np.float64)

        a_split = ic.split_coarse_to_fine(a_yaw, a_pitch, coarse_step=10.0)
        print(f"  Fusion split: train={a_split['n_train']} test={a_split['n_test']}")

        for nl in NOISE_LEVELS:
            print(f"\n  Noise level: {nl:.0%}")
            s = run_fusion_noise(a_images, a_ocs, a_yaw, a_pitch, a_split, nl, "per_part")
            fusion_summaries.append(s)
            print(f"    mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
                  f"Hit5={s['hit@5deg_mean']:.1%} Hit10={s['hit@10deg_mean']:.1%}")

    # ---- Print combined summary table ----
    def print_table(title, summaries):
        print(f"\n{'='*80}\n  {title}\n{'='*80}")
        print(f"{'Noise':>7} {'mean':>9} {'std':>6} {'p90':>8} {'Hit5':>8} {'Hit10':>8}")
        print("-" * 55)
        for s in summaries:
            print(f"{s['noise_level']:>6.0%} "
                  f"{s['angular_err_mean_mean']:>8.2f}° {s['angular_err_mean_std']:>5.2f} "
                  f"{s['angular_err_p90_mean']:>7.2f}° "
                  f"{s['hit@5deg_mean']:>7.1%} {s['hit@10deg_mean']:>7.1%}")

    print_table("OCS-only MLP per_part_log", ocs_summaries)
    if fusion_summaries:
        print_table("Feature Fusion per_part_log (image compensates OCS noise)", fusion_summaries)
        # 互补性诊断: 各噪声级 fusion vs ocs-only 的 mean 改善
        print(f"\n{'='*60}\n  Fusion improvement over OCS-only\n{'='*60}")
        print(f"{'Noise':>7} {'OCS-only':>10} {'Fusion':>10} {'Δmean':>9}")
        for so, sf in zip(ocs_summaries, fusion_summaries):
            do = so['angular_err_mean_mean']
            df = sf['angular_err_mean_mean']
            print(f"{so['noise_level']:>6.0%} {do:>9.2f}° {df:>9.2f}° {do-df:>+8.2f}°")

    out = {"ocs_only": ocs_summaries, "fusion": fusion_summaries,
           "noise_levels": NOISE_LEVELS, "seeds": SEEDS,
           "manifest": args.manifest, "image_dir": args.image_dir}
    with open(os.path.join(out_dir, "noise_summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

"""
Step 11e-B2 · Feature-level CNN+OCS 双流联合训练
================================================
- CNN image backbone (TinyCNN.features) → 64D img_feat
- OCS MLP branch → 64D ocs_feat
- concat → fusion head → [sin(yaw), cos(yaw), sin(pitch), cos(pitch)]
- 10°→5° split, 5 seeds, end-to-end training
"""

import argparse
import csv
import glob
import json
import os
import sys
import time
import warnings
from datetime import datetime

import numpy as np
from PIL import Image

warnings.filterwarnings("ignore", category=UserWarning)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic

# ---- 默认路径（自动检测最新 run 目录）------------------------------
_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
_MANIFEST_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块A_重构", "multi_geom_ggx_yaw73_pitch37", "run_*", "multi_geom_manifest.json")
_IMAGE_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染", "run_*", "render_log.csv")
_OUT_ROOT_DEFAULT = os.path.join(_PROJECT_ROOT, "结果", "模块C_反演", "cnn_ocs_fusion")


def _find_latest(glob_pattern, label):
    cands = sorted(glob.glob(glob_pattern), key=os.path.getmtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"未找到 {label}，glob: {glob_pattern}")
    return cands[0]


def _default_ocs_root():
    return os.path.dirname(_find_latest(_MANIFEST_GLOB, "multi_geom_manifest.json"))


def _default_image_dir():
    return os.path.dirname(_find_latest(_IMAGE_GLOB, "模块B render_log.csv"))

# ---- 目标编码/解码 -------------------------------------------------------
EPS_DECODE = 1e-8


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


# ---- 图像加载 (复用 train_cnn.py 逻辑) -----------------------------------

def load_image_array(path, img_size, intensity_mode):
    img = Image.open(path).convert("L")
    if img.size != (img_size, img_size):
        img = img.resize((img_size, img_size), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    if intensity_mode == "log1p":
        arr = np.log1p(10.0 * arr) / np.log1p(10.0)
    return arr[None, :, :]


def load_image_dataset(image_dir, img_size, intensity_mode):
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
            rows.append({
                "yaw": float(r["yaw"]),
                "pitch": float(r["pitch"]),
                "path": path,
            })

    N = len(rows)
    yaw = np.array([r["yaw"] for r in rows], dtype=np.float64)
    pitch = np.array([r["pitch"] for r in rows], dtype=np.float64)

    first = load_image_array(rows[0]["path"], img_size, intensity_mode)
    C, H, W = first.shape
    images = np.zeros((N, C, H, W), dtype=np.float32)
    images[0] = first

    t0 = time.time()
    for i in range(1, N):
        images[i] = load_image_array(rows[i]["path"], img_size, intensity_mode)
        if (i + 1) % 500 == 0:
            print(f"     load images {i+1}/{N}  ({(i+1)/(time.time()-t0):.0f} img/s)")
    print(f"     images loaded: {N}, {time.time()-t0:.1f}s, shape={images.shape}")
    return images, yaw, pitch


# ---- PyTorch 模型 --------------------------------------------------------

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class ImageBranch(nn.Module):
    """TinyCNN backbone 去头: Conv/GN/SiLU/Pool x4 → AdaptiveAvgPool → Linear→64."""
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
        self.proj = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.SiLU(),
        )

    def forward(self, x):
        return self.proj(self.conv(x))


class OCSBranch(nn.Module):
    """OCS encoder: Linear→128→LN→SiLU→Dropout→Linear→64→LN→SiLU → 64D."""
    def __init__(self, input_dim, dropout=0.10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.LayerNorm(128),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.SiLU(),
        )

    def forward(self, x):
        return self.net(x)


class FusionHead(nn.Module):
    """Concat img+ocs → 128→128→LN→SiLU→Dropout→128→64→SiLU→64→4."""
    def __init__(self, dropout=0.10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(128, 128),
            nn.LayerNorm(128),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.SiLU(),
            nn.Linear(64, 4),
        )

    def forward(self, x):
        return self.net(x)


class FusionModel(nn.Module):
    def __init__(self, ocs_dim, dropout=0.10):
        super().__init__()
        self.img_branch = ImageBranch()
        self.ocs_branch = OCSBranch(ocs_dim, dropout)
        self.fusion_head = FusionHead(dropout)

    def forward(self, img, ocs):
        f_img = self.img_branch(img)
        f_ocs = self.ocs_branch(ocs)
        fused = torch.cat([f_img, f_ocs], dim=1)
        return self.fusion_head(fused)


# ---- 训练辅助 -----------------------------------------------------------

def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss, n = 0.0, 0
    for X_img, X_ocs, yb in loader:
        X_img, X_ocs, yb = X_img.to(device), X_ocs.to(device), yb.to(device)
        optimizer.zero_grad()
        loss = criterion(model(X_img, X_ocs), yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(X_img)
        n += len(X_img)
    return total_loss / max(n, 1)


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, n = 0.0, 0
    all_pred, all_y = [], []
    for X_img, X_ocs, yb in loader:
        X_img, X_ocs, yb = X_img.to(device), X_ocs.to(device), yb.to(device)
        pred = model(X_img, X_ocs)
        loss = criterion(pred, yb)
        total_loss += loss.item() * len(X_img)
        n += len(X_img)
        all_pred.append(pred.cpu().numpy())
        all_y.append(yb.cpu().numpy())
    return total_loss / max(n, 1), np.concatenate(all_pred), np.concatenate(all_y)


def compute_metrics(yaw_pred, pitch_pred, yaw_true, pitch_true):
    err_a = ic.angular_err_deg(yaw_pred, pitch_pred, yaw_true, pitch_true)
    err_y = ic.yaw_err(yaw_pred, yaw_true)
    err_p = np.abs(np.asarray(pitch_pred) - np.asarray(pitch_true))
    N = len(yaw_true)
    return {
        "n_samples": N,
        "angular_err_mean": float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p90": float(np.percentile(err_a, 90)),
        "angular_err_p95": float(np.percentile(err_a, 95)),
        "hit@5deg": float(np.mean(err_a <= ic.HIT_THRESHOLD_DEG + 1e-6)),
        "hit@10deg": float(np.mean(err_a <= ic.HIT_THRESHOLD_10DEG + 1e-6)),
        "yaw_err_mean": float(err_y.mean()),
        "pitch_err_mean": float(err_p.mean()),
    }, err_a


# ---- 单 seed 训练 -------------------------------------------------------

def train_one_seed(images, ocs_feats, yaw, pitch, split_info, args, seed, out_dir, ocs_mu, ocs_sd):
    torch.manual_seed(seed)
    np.random.seed(seed)

    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    # Split
    train_pool_idx = split_info["train_idx"]
    test_idx = split_info["test_idx"]

    # Train pool -> 80/20 train/val (same random seed 42 as train_cnn/train_mlp)
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_pool_idx))
    n_val = int(len(train_pool_idx) * 0.20)
    val_idx = train_pool_idx[perm[:n_val]]
    tr_idx = train_pool_idx[perm[n_val:]]

    print(f"    seed={seed}: train={len(tr_idx)} val={len(val_idx)} test={len(test_idx)}")

    # Prepare tensors
    X_img_tr = torch.FloatTensor(images[tr_idx]).to(device)
    X_ocs_tr = torch.FloatTensor(ocs_feats[tr_idx]).to(device)
    y_tr = torch.FloatTensor(encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)

    X_img_va = torch.FloatTensor(images[val_idx]).to(device)
    X_ocs_va = torch.FloatTensor(ocs_feats[val_idx]).to(device)
    y_va = torch.FloatTensor(encode_target(yaw[val_idx], pitch[val_idx])).to(device)

    X_img_te = torch.FloatTensor(images[test_idx]).to(device)
    X_ocs_te = torch.FloatTensor(ocs_feats[test_idx]).to(device)
    y_te = torch.FloatTensor(encode_target(yaw[test_idx], pitch[test_idx])).to(device)

    # DataLoader with combined dataset
    class FusionDataset(torch.utils.data.Dataset):
        def __init__(self, img, ocs, y):
            self.img = img
            self.ocs = ocs
            self.y = y

        def __len__(self):
            return len(self.img)

        def __getitem__(self, idx):
            return self.img[idx], self.ocs[idx], self.y[idx]

    tr_ds = FusionDataset(X_img_tr, X_ocs_tr, y_tr)
    va_ds = FusionDataset(X_img_va, X_ocs_va, y_va)

    tr_loader = DataLoader(tr_ds, batch_size=args.batch_size, shuffle=True,
                           num_workers=args.num_workers)
    va_loader = DataLoader(va_ds, batch_size=args.batch_size * 2,
                           num_workers=args.num_workers)

    model = FusionModel(ocs_dim=ocs_feats.shape[1], dropout=args.dropout).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"    model params: {n_params:,}  device: {device}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr,
                                  weight_decay=args.weight_decay)
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    best_state = None
    wait = 0
    curve = []

    t0 = time.time()
    for ep in range(1, args.epochs + 1):
        tr_loss = train_epoch(model, tr_loader, optimizer, criterion, device)
        va_loss, va_pred, va_y = evaluate(model, va_loader, criterion, device)
        curve.append({"epoch": ep, "train_loss": tr_loss, "val_loss": va_loss})

        if va_loss < best_val_loss - 1e-8:
            best_val_loss = va_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            wait = 0
        else:
            wait += 1

        if ep % 50 == 0 or wait >= args.patience:
            print(f"      ep={ep:4d}  tr_loss={tr_loss:.6f}  va_loss={va_loss:.6f}  "
                  f"best={best_val_loss:.6f}  wait={wait}", flush=True)

        if wait >= args.patience:
            print(f"      early stop at epoch {ep}")
            break

    train_time = time.time() - t0

    # Evaluate test
    model.load_state_dict(best_state)
    te_ds = FusionDataset(X_img_te, X_ocs_te, y_te)
    te_loader = DataLoader(te_ds, batch_size=args.batch_size * 2,
                           num_workers=args.num_workers)
    te_loss, te_pred, te_y = evaluate(model, te_loader, criterion, device)

    yaw_pred, pitch_pred = decode_pred(te_pred)
    metrics, err_a = compute_metrics(yaw_pred, pitch_pred,
                                     yaw[test_idx], pitch[test_idx])

    # Save model
    torch.save(best_state, os.path.join(out_dir, f"best_model_seed{seed}.pt"))

    # Save training curve
    with open(os.path.join(out_dir, f"training_curve_seed{seed}.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["epoch", "train_loss", "val_loss"])
        w.writeheader()
        w.writerows(curve)

    # Save predictions
    with open(os.path.join(out_dir, f"predictions_seed{seed}.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["idx", "true_yaw", "true_pitch", "pred_yaw", "pred_pitch",
                    "err_angular_deg"])
        for i in range(len(test_idx)):
            w.writerow([test_idx[i],
                        f"{yaw[test_idx[i]]:.4f}",
                        f"{pitch[test_idx[i]]:.4f}",
                        f"{yaw_pred[i]:.4f}",
                        f"{pitch_pred[i]:.4f}",
                        f"{err_a[i]:.4f}"])

    # Save metrics
    with open(os.path.join(out_dir, f"metrics_seed{seed}.json"), "w",
              encoding="utf-8") as f:
        json.dump({
            "seed": seed,
            "train_time_s": round(train_time, 1),
            "best_epoch": len(curve),
            "best_val_loss": float(best_val_loss),
            "test_loss": float(te_loss),
            "n_params": n_params,
            **metrics,
        }, f, indent=2, ensure_ascii=False)

    return metrics, yaw_pred, pitch_pred, yaw[test_idx], pitch[test_idx], test_idx


# ---- 主流程 -------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Feature-level CNN+OCS fusion (Step 11e-B2)")
    # Data
    ap.add_argument("--ocs-root", default=None,
                    help="multi_geom 目录（含 manifest），默认自动检测最新")
    ap.add_argument("--image-dir", default=None,
                    help="模块B渲染目录（含 render_log.csv + brdf_images/），默认自动检测最新")
    ap.add_argument("--out-root", default=None,
                    help="输出根目录，默认 结果/模块C_反演/cnn_ocs_fusion/")
    # OCS features
    ap.add_argument("--geom-set", default="concat5")
    ap.add_argument("--ocs-feat", default="all", choices=["all", "per_part", "total", "obs_total"])
    ap.add_argument("--ocs-transform", default="raw", choices=["raw", "log"])
    # Image
    ap.add_argument("--image-size", type=int, default=128)
    ap.add_argument("--intensity", default="log1p", choices=["raw", "log1p"])
    # Split
    ap.add_argument("--split", default="10to5")
    # Training
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--patience", type=int, default=100)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--dropout", type=float, default=0.10)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0])
    ap.add_argument("--num-workers", type=int, default=0)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    # 自动检测默认路径
    if args.ocs_root is None:
        args.ocs_root = _default_ocs_root()
    if args.image_dir is None:
        args.image_dir = _default_image_dir()
    if args.out_root is None:
        args.out_root = _OUT_ROOT_DEFAULT

    # ---- 1. Load images ----
    print(f"[Fusion] Loading images: {args.image_dir}")
    print(f"    image_size={args.image_size}  intensity={args.intensity}")
    images, yaw_img, pitch_img = load_image_dataset(
        args.image_dir, args.image_size, args.intensity)
    print(f"    images={images.shape}  nbytes={images.nbytes/1024/1024:.1f} MB")
    N_img = len(yaw_img)

    # ---- 2. Load OCS ----
    manifest_path = os.path.join(args.ocs_root, "multi_geom_manifest.json")
    print(f"\n[Fusion] Loading OCS: {manifest_path}")
    print(f"    geom_set={args.geom_set}  feat={args.ocs_feat}  transform={args.ocs_transform}")

    label_order, geom_labels, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(manifest_path)
    if not label_order:
        raise RuntimeError("No geometry data found in manifest")

    # Build concat features
    ocs_feats_raw, yaw_ocs, pitch_ocs, col_meta = ic.build_concat_features_with_mode(
        feat_dict, yaw_dict, pitch_dict, label_order, args.ocs_feat)

    N_ocs = len(yaw_ocs)
    print(f"    OCS raw dim={ocs_feats_raw.shape[1]}  N_ocs={N_ocs}")

    # ---- 3. Align images and OCS by (yaw, pitch) ----
    img_key_to_idx = {}
    for i in range(N_img):
        key = (round(yaw_img[i], 6), round(pitch_img[i], 6))
        img_key_to_idx[key] = i

    ocs_key_to_idx = {}
    for i in range(N_ocs):
        key = (round(yaw_ocs[i], 6), round(pitch_ocs[i], 6))
        ocs_key_to_idx[key] = i

    common_keys = sorted(set(img_key_to_idx.keys()) & set(ocs_key_to_idx.keys()))
    if not common_keys:
        raise RuntimeError(f"No common (yaw,pitch) between images ({N_img}) and OCS ({N_ocs})")

    N_aligned = len(common_keys)
    print(f"\n[Fusion] Aligned: N_img={N_img} N_ocs={N_ocs} N_common={N_aligned}")

    # Build aligned arrays
    aligned_yaw = np.array([k[0] for k in common_keys], dtype=np.float64)
    aligned_pitch = np.array([k[1] for k in common_keys], dtype=np.float64)
    aligned_images = np.zeros((N_aligned,) + images.shape[1:], dtype=np.float32)
    aligned_ocs_raw = np.zeros((N_aligned, ocs_feats_raw.shape[1]), dtype=np.float64)

    for i, key in enumerate(common_keys):
        aligned_images[i] = images[img_key_to_idx[key]]
        aligned_ocs_raw[i] = ocs_feats_raw[ocs_key_to_idx[key]]

    print(f"    aligned images: {aligned_images.shape}")
    print(f"    aligned OCS raw: {aligned_ocs_raw.shape}")

    # ---- 4. Split (10°->5°) ----
    split_info = ic.split_coarse_to_fine(aligned_yaw, aligned_pitch, coarse_step=10.0)
    print(f"\n[Fusion] split: {split_info['description']}")
    print(f"    train pool={split_info['n_train']}  test={split_info['n_test']}")

    # ---- 5. zscore OCS (fit on train pool only) ----
    train_pool_idx = split_info["train_idx"]

    # Determine which columns to skip for log transform
    if args.ocs_feat in ("per_part", "obs_total"):
        log_skip = None
    else:
        log_skip = {2}  # skip occlusion rate columns

    ocs_train_pool_raw = aligned_ocs_raw[train_pool_idx]
    if args.ocs_transform == "log":
        ocs_train_transformed = ic.log_transform(ocs_train_pool_raw, skip_cols=log_skip)
    else:
        ocs_train_transformed = ocs_train_pool_raw.copy()

    ocs_train_zs, ocs_mu, ocs_sd = ic.zscore(ocs_train_transformed, return_params=True)

    # Apply same transform to all data
    if args.ocs_transform == "log":
        ocs_all_transformed = ic.log_transform(aligned_ocs_raw, skip_cols=log_skip)
    else:
        ocs_all_transformed = aligned_ocs_raw.copy()

    ocs_all_zs = (ocs_all_transformed - ocs_mu) / ocs_sd

    print(f"    OCS zscore: mu range [{ocs_mu.min():.3f}, {ocs_mu.max():.3f}] "
          f"sd range [{ocs_sd.min():.3f}, {ocs_sd.max():.3f}]")
    print(f"    OCS final dim={ocs_all_zs.shape[1]}")

    # ---- 6. Output dir ----
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag_str = f"_{args.tag}" if args.tag else ""
    out_dir = os.path.join(args.out_root, f"run_{stamp}{tag_str}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"\n[Fusion] Output: {out_dir}")

    # ---- 7. Multi-seed training ----
    all_metrics = []
    for seed in args.seeds:
        print(f"\n{'='*60}")
        print(f"[Fusion] seed={seed} (ocs={args.ocs_feat}_{args.ocs_transform}, "
              f"img={args.intensity}, dim={ocs_all_zs.shape[1]})")
        print(f"{'='*60}")
        metrics, yaw_pred, pitch_pred, yaw_test, pitch_test, test_idx = train_one_seed(
            aligned_images, ocs_all_zs, aligned_yaw, aligned_pitch,
            split_info, args, seed, out_dir, ocs_mu, ocs_sd)

        metrics["seed"] = seed
        metrics["ocs_feat"] = args.ocs_feat
        metrics["ocs_transform"] = args.ocs_transform
        metrics["intensity"] = args.intensity
        metrics["image_size"] = args.image_size
        all_metrics.append(metrics)

        print(f"     mean={metrics['angular_err_mean']:.2f}°  "
              f"med={metrics['angular_err_median']:.2f}°  "
              f"p90={metrics['angular_err_p90']:.2f}°  "
              f"Hit5={metrics['hit@5deg']:.1%}  Hit10={metrics['hit@10deg']:.1%}")

    # ---- 8. Summary ----
    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "hit@5deg", "hit@10deg",
            "yaw_err_mean", "pitch_err_mean"]
    summary = {
        "seeds": args.seeds,
        "ocs_feat": args.ocs_feat,
        "ocs_transform": args.ocs_transform,
        "ocs_dim": int(ocs_all_zs.shape[1]),
        "intensity": args.intensity,
        "image_size": args.image_size,
        "tag": args.tag,
        "n_aligned": N_aligned,
        "n_train_pool": int(split_info["n_train"]),
        "n_test": int(split_info["n_test"]),
    }
    for k in keys:
        vals = [m[k] for m in all_metrics]
        summary[f"{k}_mean"] = float(np.mean(vals))
        summary[f"{k}_std"] = float(np.std(vals)) if len(vals) > 1 else 0.0

    print(f"\n{'='*70}")
    print(f"[Fusion] Summary (ocs={args.ocs_feat}_{args.ocs_transform}, "
          f"img={args.intensity}, seeds={args.seeds})")
    print(f"     mean={summary['angular_err_mean_mean']:.2f}±"
          f"{summary['angular_err_mean_std']:.2f}°  "
          f"Hit5={summary['hit@5deg_mean']:.1%}±{summary['hit@5deg_std']:.1%}  "
          f"Hit10={summary['hit@10deg_mean']:.1%}")

    # Save summary.json
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Save summary.csv
    with open(os.path.join(out_dir, "summary.csv"), "w", encoding="utf-8",
              newline="") as f:
        csv_keys = ["seed"] + keys + ["best_epoch", "n_params"]
        w = csv.DictWriter(f, fieldnames=csv_keys)
        w.writeheader()
        for m in all_metrics:
            w.writerow({k: m.get(k, "") for k in csv_keys})

    # Save config_used.json
    config_out = vars(args).copy()
    config_out["output_encoding"] = "[sin(yaw),cos(yaw),sin(pitch),cos(pitch)]"
    config_out["loss"] = "MSE"
    config_out["model"] = "ImageBranch(TinyCNN->64D) + OCSBranch(MLP->64D) + FusionHead(128->4)"
    config_out["ocs_mu_stats"] = {"min": float(ocs_mu.min()), "max": float(ocs_mu.max())}
    config_out["ocs_sd_stats"] = {"min": float(ocs_sd.min()), "max": float(ocs_sd.max())}
    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump(config_out, f, indent=2, ensure_ascii=False)

    print(f"\n[Fusion] Done. Output: {out_dir}")
    return out_dir, summary


if __name__ == "__main__":
    main()

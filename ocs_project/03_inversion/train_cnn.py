"""
模块 C · CNN image-only 连续姿态回归（Step 11e）

架构：Conv/GN/SiLU/Pool × 4 → AdaptiveAvgPool → MLP head → 4
输出编码：[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]（同 train_mlp.py）
Split：10°→5° 插值（同 train_mlp.py）

用法：
  python train_cnn.py --scan-json ... --image-dir ... --out-root ... [args]
"""
import argparse
import csv
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

# ---- 目标编码/解码（与 train_mlp.py 一致）---------------------------
EPS_DECODE = 1e-8


def encode_target(yaw_deg, pitch_deg):
    y = np.deg2rad(yaw_deg % 360.0)
    p = np.deg2rad(pitch_deg)
    return np.stack([np.sin(y), np.cos(y), np.sin(p), np.cos(p)], axis=1).astype(np.float32)


def decode_pred(pred):
    """pred: (N,4) array, 返回 yaw[N], pitch[N] 单位度."""
    ys, yc, ps, pc = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    yr = np.sqrt(ys ** 2 + yc ** 2) + EPS_DECODE
    pr = np.sqrt(ps ** 2 + pc ** 2) + EPS_DECODE
    yaw = (np.rad2deg(np.arctan2(ys / yr, yc / yr)) + 360.0) % 360.0
    pitch = np.rad2deg(np.arctan2(ps / pr, pc / pr))
    pitch = np.clip(pitch, -90.0, 90.0)
    return yaw, pitch


# ---- 图像加载 -------------------------------------------------------

def load_image_array(path, img_size, intensity_mode):
    """读取单张 PNG → (1, H, W) float32 array."""
    img = Image.open(path).convert("L")
    if img.size != (img_size, img_size):
        img = img.resize((img_size, img_size), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    if intensity_mode == "log1p":
        arr = np.log1p(10.0 * arr) / np.log1p(10.0)
    return arr[None, :, :]  # (1, H, W)


def load_image_dataset(scan_json, image_dir, img_size, intensity_mode):
    """从 scan JSON + render_log.csv 加载全部图像和标签。

    返回:
        images:  (N, 1, H, W) float32
        yaw:     (N,) float64
        pitch:   (N,) float64
    """
    # 读 render_log.csv 获取 out_prefix → yaw/pitch 映射
    csv_path = os.path.join(image_dir, "render_log.csv")
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            prefix = r.get("out_prefix", r.get("filename", ""))
            fname = prefix + "_brdf.png"
            path = os.path.join(image_dir, "brdf_images", fname)
            if not os.path.exists(path):
                raise FileNotFoundError(f"图像缺失: {path}")
            rows.append({
                "yaw": float(r["yaw"]),
                "pitch": float(r["pitch"]),
                "path": path,
            })

    N = len(rows)
    yaw = np.array([r["yaw"] for r in rows], dtype=np.float64)
    pitch = np.array([r["pitch"] for r in rows], dtype=np.float64)

    # 读第一个图确定尺寸
    first = load_image_array(rows[0]["path"], img_size, intensity_mode)
    C, H, W = first.shape
    images = np.zeros((N, C, H, W), dtype=np.float32)
    images[0] = first

    t0 = time.time()
    for i in range(1, N):
        images[i] = load_image_array(rows[i]["path"], img_size, intensity_mode)
        if (i + 1) % 500 == 0:
            print(f"    加载图像 {i+1}/{N}  ({(i+1)/(time.time()-t0):.0f} 图/秒)")
    print(f"    加载完成: {N} 图, {time.time()-t0:.1f}s, shape={images.shape}")
    return images, yaw, pitch


# ---- PyTorch 模型 ----------------------------------------------------

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class TinyCNN(nn.Module):
    """小 CNN：4 个 Conv/GN/SiLU/Pool → AdaptiveAvgPool → MLP head → 4."""

    def __init__(self, in_ch=1, img_size=128):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_ch, 16, 3, padding=1), nn.GroupNorm(4, 16), nn.SiLU(),
            nn.MaxPool2d(2),  # → /2
            nn.Conv2d(16, 32, 3, padding=1), nn.GroupNorm(8, 32), nn.SiLU(),
            nn.MaxPool2d(2),  # → /4
            nn.Conv2d(32, 64, 3, padding=1), nn.GroupNorm(8, 64), nn.SiLU(),
            nn.MaxPool2d(2),  # → /8
            nn.Conv2d(64, 128, 3, padding=1), nn.GroupNorm(16, 128), nn.SiLU(),
            nn.AdaptiveAvgPool2d(1),  # → (128, 1, 1)
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.SiLU(),
            nn.Linear(64, 4),
        )

    def forward(self, x):
        return self.head(self.features(x))


# ---- 训练辅助 -------------------------------------------------------

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
    err_y = ic.yaw_err(yaw_pred, yaw_true)
    err_p = np.abs(pitch_pred - pitch_true)
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


# ---- 单 seed 训练 ---------------------------------------------------

def train_one_seed(images, yaw, pitch, split_info, args, seed, out_dir):
    """训练单个 seed，返回 metrics dict 和预测."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    # Split
    train_pool_idx = split_info["train_idx"]
    test_idx = split_info["test_idx"]

    # Train pool → 80/20 train/val
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_pool_idx))
    n_val = int(len(train_pool_idx) * 0.20)
    val_idx = train_pool_idx[perm[:n_val]]
    tr_idx = train_pool_idx[perm[n_val:]]

    print(f"    seed={seed}: train={len(tr_idx)} val={len(val_idx)} test={len(test_idx)}")

    X_tr = torch.FloatTensor(images[tr_idx]).to(device)
    y_tr = torch.FloatTensor(encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    X_va = torch.FloatTensor(images[val_idx]).to(device)
    y_va = torch.FloatTensor(encode_target(yaw[val_idx], pitch[val_idx])).to(device)
    X_te = torch.FloatTensor(images[test_idx]).to(device)
    y_te = torch.FloatTensor(encode_target(yaw[test_idx], pitch[test_idx])).to(device)

    tr_loader = DataLoader(TensorDataset(X_tr, y_tr),
                           batch_size=args.batch_size, shuffle=True,
                           num_workers=args.num_workers)
    va_loader = DataLoader(TensorDataset(X_va, y_va),
                           batch_size=args.batch_size * 2,
                           num_workers=args.num_workers)

    model = TinyCNN(in_ch=images.shape[1], img_size=images.shape[2]).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"    model params: {n_params:,}  device: {device}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
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

    # 加载最佳模型评估 test
    model.load_state_dict(best_state)
    te_loader = DataLoader(TensorDataset(X_te, y_te),
                           batch_size=args.batch_size * 2,
                           num_workers=args.num_workers)
    te_loss, te_pred, te_y = evaluate(model, te_loader, criterion, device)

    yaw_pred, pitch_pred = decode_pred(te_pred)
    metrics, err_a = compute_metrics(yaw_pred, pitch_pred,
                                     yaw[test_idx], pitch[test_idx])

    # 保存模型
    torch.save(best_state, os.path.join(out_dir, f"best_model_seed{seed}.pt"))

    # 保存训练曲线
    with open(os.path.join(out_dir, f"train_curve_seed{seed}.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["epoch", "train_loss", "val_loss"])
        w.writeheader()
        w.writerows(curve)

    # 保存预测
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

    # 保存 metrics
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


# ---- 主流程 ---------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="CNN image-only 连续姿态回归 (Step 11e)")
    # 数据
    ap.add_argument("--scan-json", required=True)
    ap.add_argument("--image-dir", required=True)
    ap.add_argument("--out-root", required=True)
    # 超参
    ap.add_argument("--split", default="10to5")
    ap.add_argument("--image-size", type=int, default=128)
    ap.add_argument("--intensity", default="log1p", choices=["raw", "log1p"])
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=300)
    ap.add_argument("--patience", type=int, default=60)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0])
    ap.add_argument("--num-workers", type=int, default=0)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    # ---- 1. 加载数据 ----
    print(f"[CNN] 加载图像: {args.image_dir}")
    print(f"     image_size={args.image_size}  intensity={args.intensity}")
    images, yaw, pitch = load_image_dataset(
        args.scan_json, args.image_dir, args.image_size, args.intensity)
    print(f"     images={images.shape}  dtype={images.dtype}  "
          f"nbytes={images.nbytes/1024/1024:.1f} MB")
    print(f"     yaw/pitch={len(yaw)} samples")

    # ---- 2. Split ----
    split_info = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    print(f"[CNN] split: {split_info['description']}")
    print(f"     train pool={split_info['n_train']}  test={split_info['n_test']}")

    # ---- 3. 输出目录 ----
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag_str = f"_{args.tag}" if args.tag else ""
    out_dir = os.path.join(args.out_root, f"run_{stamp}{tag_str}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"[CNN] 输出: {out_dir}")

    # ---- 4. 多 seed 训练 ----
    all_metrics = []
    for seed in args.seeds:
        print(f"\n{'='*60}")
        print(f"[CNN] seed={seed} ({args.intensity}, img={args.image_size})")
        print(f"{'='*60}")
        metrics, yaw_pred, pitch_pred, yaw_test, pitch_test, test_idx = train_one_seed(
            images, yaw, pitch, split_info, args, seed, out_dir)

        metrics["seed"] = seed
        metrics["intensity"] = args.intensity
        metrics["image_size"] = args.image_size
        all_metrics.append(metrics)

        print(f"     mean={metrics['angular_err_mean']:.2f}°  "
              f"med={metrics['angular_err_median']:.2f}°  "
              f"p90={metrics['angular_err_p90']:.2f}°  "
              f"Hit5={metrics['hit@5deg']:.1%}  Hit10={metrics['hit@10deg']:.1%}")

    # ---- 5. 总结 ----
    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "hit@5deg", "hit@10deg",
            "yaw_err_mean", "pitch_err_mean"]
    summary = {"seeds": len(args.seeds), "intensity": args.intensity,
               "image_size": args.image_size, "tag": args.tag}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        summary[f"{k}_mean"] = float(np.mean(vals))
        summary[f"{k}_std"] = float(np.std(vals)) if len(vals) > 1 else 0.0
        for m in all_metrics:
            m[f"{k}_per_seed"] = m[k]

    # 打印
    print(f"\n{'='*70}")
    print(f"[CNN] 总结 (intensity={args.intensity}, img={args.image_size}, "
          f"seeds={args.seeds})")
    print(f"     mean={summary['angular_err_mean_mean']:.2f}±"
          f"{summary['angular_err_mean_std']:.2f}°  "
          f"Hit5={summary['hit@5deg_mean']:.1%}±{summary['hit@5deg_std']:.1%}  "
          f"Hit10={summary['hit@10deg_mean']:.1%}")

    # 保存 summary.json
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # 保存 summary.csv
    with open(os.path.join(out_dir, "summary.csv"), "w", encoding="utf-8",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=["seed"] + keys + ["best_epoch", "n_params"])
        w.writeheader()
        for m in all_metrics:
            w.writerow({k: m.get(k, "") for k in w.fieldnames})

    # 保存 config_used.json
    config_out = vars(args).copy()
    config_out["output_encoding"] = "[sin(yaw),cos(yaw),sin(pitch),cos(pitch)]"
    config_out["loss"] = "MSE"
    config_out["model"] = "TinyCNN: Conv/GN/SiLU/Pool×4 → AdaptiveAvgPool → MLP→4"
    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump(config_out, f, indent=2, ensure_ascii=False)

    print(f"\n[CNN] 输出已写入: {out_dir}")
    return out_dir, summary


if __name__ == "__main__":
    main()

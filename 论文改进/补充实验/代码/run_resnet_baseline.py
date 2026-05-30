"""
ResNet-18 image-only baseline (Supplementary Experiment 8.1)
==============================================================
目的：回应 TinyCNN 是否太弱的质疑。

对比:
  - TinyCNN image-only (已有, 106k params, mean=12.38 deg)
  - ResNet-18 image-only (11M params, 标准 backbone)

训练配置与 TinyCNN 一致: 10 deg->5 deg split, 5 seeds, log1p, 128x128.
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
_IMAGE_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染", "run_*", "render_log.csv")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "resnet_baseline")

EPS_DECODE = 1e-8
SEEDS = [0, 1, 2, 3, 4]

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
        "n_samples": len(yaw_true),
        "angular_err_mean": float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p90": float(np.percentile(err_a, 90)),
        "angular_err_p95": float(np.percentile(err_a, 95)),
        "hit@5deg": float(np.mean(err_a <= ic.HIT_THRESHOLD_DEG + 1e-6)),
        "hit@10deg": float(np.mean(err_a <= ic.HIT_THRESHOLD_10DEG + 1e-6)),
    }, err_a


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
    return images, yaw, pitch


class ResNet18SingleChannel(nn.Module):
    """ResNet-18 adapted for single-channel 128x128 input."""

    def __init__(self, out_dim=4):
        super().__init__()
        self.inplanes = 64
        self.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.layer1 = self._make_layer(64, 2, stride=1)
        self.layer2 = self._make_layer(128, 2, stride=2)
        self.layer3 = self._make_layer(256, 2, stride=2)
        self.layer4 = self._make_layer(512, 2, stride=2)

        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(512, out_dim)

    def _make_layer(self, planes, blocks, stride):
        downsample = None
        if stride != 1 or self.inplanes != planes * 1:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes),
            )

        layers = []
        layers.append(BasicBlock(self.inplanes, planes, stride, downsample))
        self.inplanes = planes
        for _ in range(1, blocks):
            layers.append(BasicBlock(self.inplanes, planes))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=3, stride=stride,
                               padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        out = self.relu(out)
        return out


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


def main():
    ap = argparse.ArgumentParser(description="ResNet-18 image-only baseline")
    ap.add_argument("--image-dir", default=None)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--image-size", type=int, default=128)
    ap.add_argument("--intensity", default="log1p")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--patience", type=int, default=100)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    if args.image_dir is None:
        cands = sorted(glob.glob(_IMAGE_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No image dir: {_IMAGE_GLOB}")
        args.image_dir = os.path.dirname(cands[0])

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    print("=" * 70)
    print("  ResNet-18 Image-only Baseline")
    print(f"  Image dir: {args.image_dir}")
    print(f"  Device: {device}")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    # Load images
    images, yaw, pitch = load_images(args.image_dir, args.image_size, args.intensity)
    print(f"  Loaded {len(yaw)} images, shape={images.shape}")

    # Split 10->5
    split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    train_pool_idx = split["train_idx"]
    test_idx = split["test_idx"]

    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_pool_idx))
    n_val = int(len(train_pool_idx) * 0.20)
    val_idx = train_pool_idx[perm[:n_val]]
    tr_idx = train_pool_idx[perm[n_val:]]

    print(f"  Split: train={len(tr_idx)} val={len(val_idx)} test={len(test_idx)}")

    X_tr = torch.FloatTensor(images[tr_idx]).to(device)
    y_tr = torch.FloatTensor(encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    X_va = torch.FloatTensor(images[val_idx]).to(device)
    y_va = torch.FloatTensor(encode_target(yaw[val_idx], pitch[val_idx])).to(device)
    X_te = torch.FloatTensor(images[test_idx]).to(device)
    y_te = torch.FloatTensor(encode_target(yaw[test_idx], pitch[test_idx])).to(device)

    all_metrics = []
    for seed in SEEDS:
        torch.manual_seed(seed)
        np.random.seed(seed)

        model = ResNet18SingleChannel(out_dim=4).to(device)
        n_params = sum(p.numel() for p in model.parameters())
        print(f"\n  seed={seed}: params={n_params:,}")

        optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr,
                                      weight_decay=args.weight_decay)
        criterion = nn.MSELoss()

        tr_loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=args.batch_size,
                               shuffle=True)
        va_loader = DataLoader(TensorDataset(X_va, y_va), batch_size=args.batch_size * 2)

        best_val_loss = float("inf")
        best_state = None
        wait = 0

        for ep in range(1, args.epochs + 1):
            tr_loss = train_epoch(model, tr_loader, optimizer, criterion, device)
            va_loss, _, _ = evaluate(model, va_loader, criterion, device)

            if va_loss < best_val_loss - 1e-8:
                best_val_loss = va_loss
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1

            if ep % 50 == 0 or wait >= args.patience:
                print(f"    ep={ep:4d} tr={tr_loss:.6f} va={va_loss:.6f} "
                      f"best={best_val_loss:.6f} wait={wait}")

            if wait >= args.patience:
                print(f"    early stop at epoch {ep}")
                break

        model.load_state_dict(best_state)
        te_loader = DataLoader(TensorDataset(X_te, y_te), batch_size=args.batch_size * 2)
        _, te_pred, _ = evaluate(model, te_loader, criterion, device)

        yaw_pred, pitch_pred = decode_pred(te_pred)
        m, err_a = compute_metrics(yaw_pred, pitch_pred, yaw[test_idx], pitch[test_idx])
        m["seed"] = seed
        m["n_params"] = n_params
        m["best_epoch"] = len(best_state)  # approximate
        all_metrics.append(m)

        print(f"    mean={m['angular_err_mean']:.2f} deg  "
              f"Hit5={m['hit@5deg']:.1%}  Hit10={m['hit@10deg']:.1%}")

        # Save predictions
        with open(os.path.join(out_dir, f"predictions_seed{seed}.csv"), "w",
                  encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["true_yaw","true_pitch","pred_yaw","pred_pitch","err_angular_deg"])
            for i in range(len(test_idx)):
                w.writerow([f"{yaw[test_idx[i]]:.4f}", f"{pitch[test_idx[i]]:.4f}",
                           f"{yaw_pred[i]:.4f}", f"{pitch_pred[i]:.4f}", f"{err_a[i]:.4f}"])

        # Save model
        torch.save(best_state, os.path.join(out_dir, f"best_model_seed{seed}.pt"))

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Summary
    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "hit@5deg", "hit@10deg"]
    summary = {"model": "ResNet-18 (1ch)", "intensity": args.intensity,
               "image_size": args.image_size, "n_seeds": len(SEEDS)}
    for k in keys:
        vals = [m[k] for m in all_metrics]
        summary[f"{k}_mean"] = float(np.mean(vals))
        summary[f"{k}_std"] = float(np.std(vals))

    print(f"\n{'='*70}")
    print(f"  ResNet-18 Summary")
    print(f"  mean={summary['angular_err_mean_mean']:.2f}±{summary['angular_err_mean_std']:.2f} deg  "
          f"Hit5={summary['hit@5deg_mean']:.1%}±{summary['hit@5deg_std']:.1%}")
    print(f"  (cf. TinyCNN: mean=12.38±0.74 deg, Hit5=26.1±0.9%)")

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump(vars(args), f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

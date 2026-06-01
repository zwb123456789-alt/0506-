"""
run_resnet_robustness.py — ResNet 图像退化鲁棒性测试 (指导文件任务 B)
=====================================================================
目的：判断 ResNet 1.69° 是否只在干净渲染图像上成立。

退化类型 (P0 优先)：
  - Gaussian noise: sigma = 0.01, 0.03, 0.05, 0.10
  - brightness scale: x0.5, x0.75, x1.25, x1.5

P1：
  - Gaussian blur: kernel 3, 5
  - downsample-upsample: 128->64->128, 128->32->128

对比模型：
  - ResNet image-only (受退化影响)
  - OCS MLP per_part_log (不受图像退化影响，作为参照)
  - ResNet-fusion per_part_log (若任务 A 已完成)

方法：
  - 训练时用干净图像（模拟"训练数据干净、部署时遇到退化"的场景）
  - 测试时施加退化
  - 5 seeds，统一 10°→5° split
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
from PIL import Image, ImageFilter

warnings.filterwarnings("ignore", category=UserWarning)

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic

_IMAGE_DIR = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染",
                          "run_20260528_101944_exact_brdf")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                         "resnet_robustness")

EPS_DECODE = 1e-8
SEEDS = [0, 1, 2, 3, 4]

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ---- 编码/解码/指标 (复用) ----
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
    return yaw, np.clip(pitch, -90.0, 90.0)


def compute_metrics(yaw_pred, pitch_pred, yaw_true, pitch_true):
    err_a = ic.angular_err_deg(yaw_pred, pitch_pred, yaw_true, pitch_true)
    return {
        "angular_err_mean": float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p90": float(np.percentile(err_a, 90)),
        "angular_err_worst": float(err_a.max()),
        "hit@5deg": float(np.mean(err_a <= 5.0 + 1e-6)),
        "hit@10deg": float(np.mean(err_a <= 10.0 + 1e-6)),
    }, err_a


# ---- 图像加载 ----
def load_image_array(path, img_size, intensity_mode):
    img = Image.open(path).convert("L")
    if img.size != (img_size, img_size):
        img = img.resize((img_size, img_size), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    if intensity_mode == "log1p":
        arr = np.log1p(10.0 * arr) / np.log1p(10.0)
    return arr[None, :, :]


def load_images(image_dir, img_size=128, intensity_mode="log1p"):
    csv_path = os.path.join(image_dir, "render_log.csv")
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            prefix = r.get("out_prefix", r.get("filename", ""))
            fname = prefix + "_brdf.png"
            path = os.path.join(image_dir, "brdf_images", fname)
            rows.append({"yaw": float(r["yaw"]), "pitch": float(r["pitch"]), "path": path})
    N = len(rows)
    yaw = np.array([r["yaw"] for r in rows], dtype=np.float64)
    pitch = np.array([r["pitch"] for r in rows], dtype=np.float64)
    first = load_image_array(rows[0]["path"], img_size, intensity_mode)
    images = np.zeros((N,) + first.shape, dtype=np.float32)
    images[0] = first
    for i in range(1, N):
        images[i] = load_image_array(rows[i]["path"], img_size, intensity_mode)
    print(f"    images loaded: {N}, shape={images.shape}")
    return images, yaw, pitch


# ---- 图像退化函数 ----
def degrade_gaussian_noise(images, sigma, seed=42):
    """在 log1p 归一化后的图像上加高斯噪声。"""
    rng = np.random.RandomState(seed)
    noisy = images + rng.randn(*images.shape).astype(np.float32) * sigma
    return np.clip(noisy, 0.0, 1.0)


def degrade_brightness(images, scale):
    """亮度缩放（在 log1p 空间）。"""
    return np.clip(images * scale, 0.0, 1.0)


def degrade_blur(images, kernel_size):
    """高斯模糊（逐图 PIL 操作，在原始 0-1 空间）。"""
    N = images.shape[0]
    out = np.zeros_like(images)
    radius = kernel_size // 2
    for i in range(N):
        arr = images[i, 0]
        pil_img = Image.fromarray((arr * 255).astype(np.uint8), mode="L")
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=radius))
        out[i, 0] = np.asarray(pil_img, dtype=np.float32) / 255.0
    return out


def degrade_downsample(images, intermediate_size):
    """下采样再上采样（模拟低分辨率观测）。"""
    N, C, H, W = images.shape
    out = np.zeros_like(images)
    for i in range(N):
        arr = images[i, 0]
        pil_img = Image.fromarray((arr * 255).astype(np.uint8), mode="L")
        small = pil_img.resize((intermediate_size, intermediate_size), Image.BILINEAR)
        back = small.resize((W, H), Image.BILINEAR)
        out[i, 0] = np.asarray(back, dtype=np.float32) / 255.0
    return out


# ---- ResNet-18 模型 (复用 run_resnet_baseline.py) ----
class BasicBlock(nn.Module):
    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(planes, planes, 3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        return self.relu(out + identity)


class ResNet18SingleChannel(nn.Module):
    def __init__(self, out_dim=4):
        super().__init__()
        self.inplanes = 64
        self.conv1 = nn.Conv2d(1, 64, 7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(3, stride=2, padding=1)
        self.layer1 = self._make_layer(64, 2, 1)
        self.layer2 = self._make_layer(128, 2, 2)
        self.layer3 = self._make_layer(256, 2, 2)
        self.layer4 = self._make_layer(512, 2, 2)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(512, out_dim)

    def _make_layer(self, planes, blocks, stride):
        downsample = None
        if stride != 1 or self.inplanes != planes:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes, 1, stride=stride, bias=False),
                nn.BatchNorm2d(planes))
        layers = [BasicBlock(self.inplanes, planes, stride, downsample)]
        self.inplanes = planes
        for _ in range(1, blocks):
            layers.append(BasicBlock(self.inplanes, planes))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.maxpool(self.relu(self.bn1(self.conv1(x))))
        x = self.layer1(x); x = self.layer2(x)
        x = self.layer3(x); x = self.layer4(x)
        x = self.avgpool(x)
        return self.fc(torch.flatten(x, 1))


# ---- 训练/评估 ----
def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    tot, n = 0.0, 0
    for Xb, yb in loader:
        Xb, yb = Xb.to(device), yb.to(device)
        optimizer.zero_grad()
        loss = criterion(model(Xb), yb)
        loss.backward()
        optimizer.step()
        tot += loss.item() * len(Xb); n += len(Xb)
    return tot / max(n, 1)


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    preds = []
    for Xb, yb in loader:
        Xb = Xb.to(device)
        preds.append(model(Xb).cpu().numpy())
    return np.concatenate(preds)


def train_resnet_clean(images_clean, yaw, pitch, split, args):
    """在干净图像上训练 ResNet，返回 5 seeds 的 best_state 列表。"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    train_pool = split["train_idx"]
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_pool))
    n_val = int(len(train_pool) * 0.20)
    val_idx = train_pool[perm[:n_val]]
    tr_idx = train_pool[perm[n_val:]]

    X_tr = torch.FloatTensor(images_clean[tr_idx]).to(device)
    y_tr = torch.FloatTensor(encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    X_va = torch.FloatTensor(images_clean[val_idx]).to(device)
    y_va = torch.FloatTensor(encode_target(yaw[val_idx], pitch[val_idx])).to(device)

    models = []
    for seed in SEEDS:
        torch.manual_seed(seed); np.random.seed(seed)
        model = ResNet18SingleChannel().to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
        crit = nn.MSELoss()
        tr_loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=args.batch_size, shuffle=True)
        va_loader = DataLoader(TensorDataset(X_va, y_va), batch_size=args.batch_size * 2)
        best_va, best_state, wait = float("inf"), None, 0
        for ep in range(1, args.epochs + 1):
            train_epoch(model, tr_loader, opt, crit, device)
            model.eval()
            with torch.no_grad():
                va_loss = 0.0
                for Xb, yb in va_loader:
                    Xb, yb = Xb.to(device), yb.to(device)
                    va_loss += crit(model(Xb), yb).item() * len(Xb)
                va_loss /= len(val_idx)
            if va_loss < best_va - 1e-8:
                best_va = va_loss
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
            if wait >= args.patience:
                break
        models.append(best_state)
        print(f"    train seed={seed} done (ep={ep}, best_va={best_va:.6f})", flush=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return models


def eval_degraded(models, images_degraded, yaw, pitch, test_idx, args):
    """用已训练模型在退化图像上评估，返回 5 seeds 的指标。"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    X_te = torch.FloatTensor(images_degraded[test_idx]).to(device)
    y_te = torch.FloatTensor(encode_target(yaw[test_idx], pitch[test_idx])).to(device)
    te_loader = DataLoader(TensorDataset(X_te, y_te), batch_size=args.batch_size * 2)

    per_seed = []
    for seed, state in zip(SEEDS, models):
        model = ResNet18SingleChannel().to(device)
        model.load_state_dict(state)
        pred = evaluate(model, te_loader, device)
        yp, pp = decode_pred(pred)
        m, _ = compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
        m["seed"] = seed
        per_seed.append(m)
    return per_seed


def summarize_seeds(per_seed):
    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_worst", "hit@5deg", "hit@10deg"]
    s = {}
    for k in keys:
        vals = [m[k] for m in per_seed]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s


# ---- 退化配置 ----
DEGRADATIONS = [
    # P0
    {"name": "clean", "type": "none"},
    {"name": "noise_0.01", "type": "noise", "sigma": 0.01},
    {"name": "noise_0.03", "type": "noise", "sigma": 0.03},
    {"name": "noise_0.05", "type": "noise", "sigma": 0.05},
    {"name": "noise_0.10", "type": "noise", "sigma": 0.10},
    {"name": "bright_0.50", "type": "brightness", "scale": 0.50},
    {"name": "bright_0.75", "type": "brightness", "scale": 0.75},
    {"name": "bright_1.25", "type": "brightness", "scale": 1.25},
    {"name": "bright_1.50", "type": "brightness", "scale": 1.50},
    # P1
    {"name": "blur_k3", "type": "blur", "kernel": 3},
    {"name": "blur_k5", "type": "blur", "kernel": 5},
    {"name": "downsample_64", "type": "downsample", "size": 64},
    {"name": "downsample_32", "type": "downsample", "size": 32},
]


def apply_degradation(images, deg):
    if deg["type"] == "none":
        return images
    elif deg["type"] == "noise":
        return degrade_gaussian_noise(images, deg["sigma"], seed=777)
    elif deg["type"] == "brightness":
        return degrade_brightness(images, deg["scale"])
    elif deg["type"] == "blur":
        return degrade_blur(images, deg["kernel"])
    elif deg["type"] == "downsample":
        return degrade_downsample(images, deg["size"])
    return images


def main():
    ap = argparse.ArgumentParser(description="ResNet image degradation robustness (Task B)")
    ap.add_argument("--image-dir", default=_IMAGE_DIR)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--image-size", type=int, default=128)
    ap.add_argument("--intensity", default="log1p")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--patience", type=int, default=100)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--p0-only", action="store_true", help="只跑 P0 退化（噪声+亮度）")
    ap.add_argument("--smoke", action="store_true", help="冒烟测试")
    args = ap.parse_args()

    global SEEDS
    if args.smoke:
        SEEDS = [0]
        args.epochs = 8
        args.patience = 5

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    # 自写日志（绕过 Windows 后台重定向问题）
    import io
    log_path = os.path.join(out_dir, "run.log")
    log_f = open(log_path, "w", encoding="utf-8", buffering=1)
    class Tee:
        def __init__(self, *streams):
            self.streams = streams
        def write(self, s):
            for st in self.streams:
                try: st.write(s); st.flush()
                except: pass
        def flush(self):
            for st in self.streams:
                try: st.flush()
                except: pass
    sys.stdout = Tee(sys.__stdout__, log_f)
    sys.stderr = Tee(sys.__stderr__, log_f)

    print("=" * 70)
    print("  ResNet Image Degradation Robustness (Task B)")
    print(f"  Image dir: {args.image_dir}")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    # 加载干净图像
    images_clean, yaw, pitch = load_images(args.image_dir, args.image_size, args.intensity)
    split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    test_idx = split["test_idx"]
    print(f"  Split: train_pool={split['n_train']} test={split['n_test']}")

    # 训练（仅在干净图像上训练一次，所有退化共享同一组模型）
    print(f"\n  [1/2] Training ResNet on clean images ({len(SEEDS)} seeds)...")
    t0 = time.time()
    models = train_resnet_clean(images_clean, yaw, pitch, split, args)
    print(f"  Training done in {time.time()-t0:.0f}s")

    # 退化评估
    degs = DEGRADATIONS if not args.p0_only else [d for d in DEGRADATIONS
                                                   if d["type"] in ("none", "noise", "brightness")]
    print(f"\n  [2/2] Evaluating on {len(degs)} degradation conditions...")
    results = []
    for deg in degs:
        print(f"    {deg['name']}...", end=" ", flush=True)
        imgs_deg = apply_degradation(images_clean, deg)
        per_seed = eval_degraded(models, imgs_deg, yaw, pitch, test_idx, args)
        s = summarize_seeds(per_seed)
        s["degradation"] = deg["name"]
        s["type"] = deg["type"]
        s.update({k: v for k, v in deg.items() if k not in ("name", "type")})
        results.append(s)
        print(f"mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
              f"Hit5={s['hit@5deg_mean']:.1%}", flush=True)

    # 保存结果
    with open(os.path.join(out_dir, "robustness_results.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results, "config": vars(args), "seeds": SEEDS},
                  f, indent=2, ensure_ascii=False)

    with open(os.path.join(out_dir, "robustness_results.csv"), "w",
              encoding="utf-8", newline="") as f:
        keys = ["degradation", "type", "angular_err_mean_mean", "angular_err_mean_std",
                "angular_err_p90_mean", "angular_err_worst_mean",
                "hit@5deg_mean", "hit@10deg_mean"]
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow(r)

    # markdown 报告
    lines = ["# ResNet 图像退化鲁棒性测试结果", "",
             f"> 训练：干净图像，测试：施加退化", "",
             "| 退化 | mean±std | p90 | worst | Hit@5° | Hit@10° |",
             "|---|---|---:|---:|---:|---:|"]
    for r in results:
        lines.append(f"| {r['degradation']} | "
                     f"{r['angular_err_mean_mean']:.2f}±{r['angular_err_mean_std']:.2f}° | "
                     f"{r['angular_err_p90_mean']:.2f}° | "
                     f"{r['angular_err_worst_mean']:.1f}° | "
                     f"{r['hit@5deg_mean']:.1%} | {r['hit@10deg_mean']:.1%} |")
    # OCS 参照行
    lines.append("")
    lines.append("> 参照：OCS MLP per_part_log 不受图像退化影响，mean=5.91° Hit5=73.8%")
    lines.append("> 参照：OCS MLP all_raw 不受图像退化影响，mean=3.98° Hit5=90.7%")

    with open(os.path.join(out_dir, "robustness_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # 打印汇总
    print(f"\n{'='*70}")
    print("  Summary:")
    print(f"{'='*70}")
    print(f"  {'Degradation':<18} {'mean':>8} {'p90':>8} {'Hit5':>8}")
    print(f"  {'-'*50}")
    for r in results:
        print(f"  {r['degradation']:<18} "
              f"{r['angular_err_mean_mean']:>7.2f}° "
              f"{r['angular_err_p90_mean']:>7.2f}° "
              f"{r['hit@5deg_mean']:>7.1%}")
    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

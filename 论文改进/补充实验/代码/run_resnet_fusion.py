"""
run_resnet_fusion.py — ResNet 图像分支版 Fusion (指导文件任务 A)
==================================================================
旧 fusion 用的是弱 TinyCNN 图像分支。本脚本把图像分支换成强 ResNet-18，
公平回答“强图像模型下 OCS 是否仍提供融合增益”。

模型组合 (指导文件 §4.2)：
  A1  ResNet image-only                         (复现 baseline, 同管线)
  A2  ResNet-fusion + concat5 per_part_log 30D  (强 OCS 中等信息 + 强图像)
  A3  ResNet-fusion + phase63 per_part_log 6D   (公平单几何融合)
  A4  ResNet-fusion + concat5 all_raw 45D       (强 OCS 上界, 可选)
  A5  Late fusion: ResNet pred + OCS MLP pred   (sin/cos 空间 beta sweep)

统一评价 (指导文件 §4.3)：mean / std(5 seeds) / median / p90 / Hit@5 / Hit@10 / worst
Split: 10°→5°, 5 seeds, log1p 128×128, 与 baseline 完全一致。
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

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic

_IMAGE_DIR = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染",
                          "run_20260528_101944_exact_brdf")
_MANIFEST_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块A_重构",
    "multi_geom_ggx_yaw73_pitch37", "run_*", "multi_geom_manifest.json")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "resnet_fusion")

EPS_DECODE = 1e-8
SEEDS = [0, 1, 2, 3, 4]
PHASE63_LABEL = "phase63_backscatter"

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ---- 目标编码/解码 ----
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
        "n_samples": int(len(yaw_true)),
        "angular_err_mean": float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p90": float(np.percentile(err_a, 90)),
        "angular_err_p95": float(np.percentile(err_a, 95)),
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
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image missing: {path}")
            rows.append({"yaw": float(r["yaw"]), "pitch": float(r["pitch"]), "path": path})
    N = len(rows)
    yaw = np.array([r["yaw"] for r in rows], dtype=np.float64)
    pitch = np.array([r["pitch"] for r in rows], dtype=np.float64)
    first = load_image_array(rows[0]["path"], img_size, intensity_mode)
    images = np.zeros((N,) + first.shape, dtype=np.float32)
    images[0] = first
    t0 = time.time()
    for i in range(1, N):
        images[i] = load_image_array(rows[i]["path"], img_size, intensity_mode)
    print(f"    images loaded: {N}, {time.time()-t0:.1f}s, shape={images.shape}")
    return images, yaw, pitch


# ---- ResNet-18 (1ch) backbone, 复用 run_resnet_baseline.py 结构 ----
class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, 3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(planes, planes, 3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        out += identity
        return self.relu(out)


class ResNet18Backbone(nn.Module):
    """ResNet-18 (1ch) 输出 512D 特征（去掉最后 fc）。"""

    def __init__(self):
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
        self.out_dim = 512

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
        x = self.layer1(x); x = self.layer2(x); x = self.layer3(x); x = self.layer4(x)
        x = self.avgpool(x)
        return torch.flatten(x, 1)


class ResNetImageOnly(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = ResNet18Backbone()
        self.fc = nn.Linear(512, 4)

    def forward(self, x):
        return self.fc(self.backbone(x))


class OCSBranch(nn.Module):
    def __init__(self, input_dim, dropout=0.10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128), nn.LayerNorm(128), nn.SiLU(), nn.Dropout(dropout),
            nn.Linear(128, 64), nn.LayerNorm(64), nn.SiLU())

    def forward(self, x):
        return self.net(x)


class ResNetFusionModel(nn.Module):
    """ResNet-18 image branch (512→128) + OCS branch (→64) → fusion head → 4."""

    def __init__(self, ocs_dim, dropout=0.10):
        super().__init__()
        self.backbone = ResNet18Backbone()
        self.img_proj = nn.Sequential(nn.Linear(512, 128), nn.SiLU())
        self.ocs_branch = OCSBranch(ocs_dim, dropout)
        self.fusion_head = nn.Sequential(
            nn.Linear(128 + 64, 128), nn.LayerNorm(128), nn.SiLU(), nn.Dropout(dropout),
            nn.Linear(128, 64), nn.SiLU(),
            nn.Linear(64, 4))

    def forward(self, img, ocs):
        f_img = self.img_proj(self.backbone(img))
        f_ocs = self.ocs_branch(ocs)
        return self.fusion_head(torch.cat([f_img, f_ocs], dim=1))


# ---- 训练 / 评估 (支持二元/三元 batch) ----
def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    tot, n = 0.0, 0
    for batch in loader:
        if len(batch) == 2:
            Xb, yb = batch
            Xb, yb = Xb.to(device), yb.to(device)
            pred = model(Xb)
            bs = len(Xb)
        else:
            Xi, Xo, yb = batch
            Xi, Xo, yb = Xi.to(device), Xo.to(device), yb.to(device)
            pred = model(Xi, Xo)
            bs = len(Xi)
        optimizer.zero_grad()
        loss = criterion(pred, yb)
        loss.backward()
        optimizer.step()
        tot += loss.item() * bs
        n += bs
    return tot / max(n, 1)


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    tot, n = 0.0, 0
    preds = []
    for batch in loader:
        if len(batch) == 2:
            Xb, yb = batch
            Xb, yb = Xb.to(device), yb.to(device)
            pred = model(Xb)
            bs = len(Xb)
        else:
            Xi, Xo, yb = batch
            Xi, Xo, yb = Xi.to(device), Xo.to(device), yb.to(device)
            pred = model(Xi, Xo)
            bs = len(Xi)
        tot += criterion(pred, yb).item() * bs
        n += bs
        preds.append(pred.cpu().numpy())
    return tot / max(n, 1), np.concatenate(preds)


def make_train_val_idx(train_pool_idx):
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_pool_idx))
    n_val = int(len(train_pool_idx) * 0.20)
    return train_pool_idx[perm[n_val:]], train_pool_idx[perm[:n_val]]


def prep_ocs(ocs_raw, tr_idx, val_idx, test_idx, transform, log_skip):
    """log(可选) + zscore（仅 fit train pool=tr+val 的 train 部分）。返回三split变换后矩阵。"""
    if transform == "log":
        tr = ic.log_transform(ocs_raw[tr_idx], skip_cols=log_skip)
        all_t = ic.log_transform(ocs_raw, skip_cols=log_skip)
    else:
        tr = ocs_raw[tr_idx].copy()
        all_t = ocs_raw.copy()
    _, mu, sd = ic.zscore(tr, return_params=True)
    out = (all_t - mu) / sd
    return out[tr_idx], out[val_idx], out[test_idx]


def run_image_only(images, yaw, pitch, split, args, out_dir, case_name):
    """A1: ResNet image-only。返回 (summary, per_seed_metrics, predictions[seed->...])."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    tr_idx, val_idx = make_train_val_idx(split["train_idx"])
    test_idx = split["test_idx"]

    X_tr = torch.FloatTensor(images[tr_idx]).to(device)
    y_tr = torch.FloatTensor(encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    X_va = torch.FloatTensor(images[val_idx]).to(device)
    y_va = torch.FloatTensor(encode_target(yaw[val_idx], pitch[val_idx])).to(device)
    X_te = torch.FloatTensor(images[test_idx]).to(device)
    y_te = torch.FloatTensor(encode_target(yaw[test_idx], pitch[test_idx])).to(device)

    per_seed, seed_preds = [], {}
    for seed in SEEDS:
        torch.manual_seed(seed); np.random.seed(seed)
        model = ResNetImageOnly().to(device)
        n_params = sum(p.numel() for p in model.parameters())
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
        crit = nn.MSELoss()
        tr_loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=args.batch_size, shuffle=True)
        va_loader = DataLoader(TensorDataset(X_va, y_va), batch_size=args.batch_size * 2)
        best_va, best_state, wait = float("inf"), None, 0
        for ep in range(1, args.epochs + 1):
            train_epoch(model, tr_loader, opt, crit, device)
            va, _ = evaluate(model, va_loader, crit, device)
            if va < best_va - 1e-8:
                best_va = va
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
            if wait >= args.patience:
                break
        model.load_state_dict(best_state)
        te_loader = DataLoader(TensorDataset(X_te, y_te), batch_size=args.batch_size * 2)
        _, te_pred = evaluate(model, te_loader, crit, device)
        yp, pp = decode_pred(te_pred)
        m, err_a = compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
        m["seed"] = seed; m["n_params"] = n_params
        per_seed.append(m)
        seed_preds[seed] = (yp, pp, err_a)
        print(f"    [{case_name}] seed={seed} mean={m['angular_err_mean']:.2f}° "
              f"Hit5={m['hit@5deg']:.1%} worst={m['angular_err_worst']:.1f}°", flush=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return summarize(case_name, "ResNet image-only", per_seed), per_seed, seed_preds, test_idx


def run_fusion(images, ocs_zs, yaw, pitch, split, args, case_name, ocs_desc):
    """A2/A3/A4: ResNet-fusion。OCS 已 zscore。返回 summary, per_seed, preds, test_idx。"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    tr_idx, val_idx = make_train_val_idx(split["train_idx"])
    test_idx = split["test_idx"]

    Xi_tr = torch.FloatTensor(images[tr_idx]).to(device)
    Xo_tr = torch.FloatTensor(ocs_zs[tr_idx]).to(device)
    y_tr = torch.FloatTensor(encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    Xi_va = torch.FloatTensor(images[val_idx]).to(device)
    Xo_va = torch.FloatTensor(ocs_zs[val_idx]).to(device)
    y_va = torch.FloatTensor(encode_target(yaw[val_idx], pitch[val_idx])).to(device)
    Xi_te = torch.FloatTensor(images[test_idx]).to(device)
    Xo_te = torch.FloatTensor(ocs_zs[test_idx]).to(device)
    y_te = torch.FloatTensor(encode_target(yaw[test_idx], pitch[test_idx])).to(device)

    per_seed, seed_preds = [], {}
    for seed in SEEDS:
        torch.manual_seed(seed); np.random.seed(seed)
        model = ResNetFusionModel(ocs_dim=ocs_zs.shape[1], dropout=args.dropout).to(device)
        n_params = sum(p.numel() for p in model.parameters())
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
        crit = nn.MSELoss()
        tr_loader = DataLoader(TensorDataset(Xi_tr, Xo_tr, y_tr),
                               batch_size=args.batch_size, shuffle=True)
        va_loader = DataLoader(TensorDataset(Xi_va, Xo_va, y_va), batch_size=args.batch_size * 2)
        best_va, best_state, wait = float("inf"), None, 0
        for ep in range(1, args.epochs + 1):
            train_epoch(model, tr_loader, opt, crit, device)
            va, _ = evaluate(model, va_loader, crit, device)
            if va < best_va - 1e-8:
                best_va = va
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                wait = 0
            else:
                wait += 1
            if wait >= args.patience:
                break
        model.load_state_dict(best_state)
        te_loader = DataLoader(TensorDataset(Xi_te, Xo_te, y_te), batch_size=args.batch_size * 2)
        _, te_pred = evaluate(model, te_loader, crit, device)
        yp, pp = decode_pred(te_pred)
        m, err_a = compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
        m["seed"] = seed; m["n_params"] = n_params
        per_seed.append(m)
        seed_preds[seed] = (yp, pp, err_a)
        print(f"    [{case_name}] seed={seed} mean={m['angular_err_mean']:.2f}° "
              f"Hit5={m['hit@5deg']:.1%} worst={m['angular_err_worst']:.1f}°", flush=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return summarize(case_name, f"ResNet-fusion ({ocs_desc})", per_seed), per_seed, seed_preds, test_idx


def summarize(case_name, model_name, per_seed):
    keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "angular_err_worst", "hit@5deg", "hit@10deg"]
    s = {"case": case_name, "model": model_name, "n_seeds": len(per_seed),
         "seeds": [m["seed"] for m in per_seed],
         "n_params": per_seed[0].get("n_params")}
    for k in keys:
        vals = [m[k] for m in per_seed]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s


def late_fusion_sweep(img_preds, ocs_preds, yaw_t, pitch_t):
    """A5: sin/cos 空间预测级融合 beta sweep。
    img_preds/ocs_preds: dict[seed] -> (yaw, pitch, err). 对齐相同 test_idx。
    对每个 beta，对 5 个 image seed 取均值（OCS 用单一 MLP 预测，broadcast）。"""
    betas = np.round(np.arange(0.0, 1.0001, 0.01), 2)
    oy, op = ocs_preds  # 单一 OCS 预测 (yaw, pitch)
    ovec = np.stack([np.sin(np.deg2rad(oy)), np.cos(np.deg2rad(oy)),
                     np.sin(np.deg2rad(op)), np.cos(np.deg2rad(op))], axis=1)
    results = []
    for b in betas:
        seed_means = []
        for seed, (iy, ip, _) in img_preds.items():
            ivec = np.stack([np.sin(np.deg2rad(iy)), np.cos(np.deg2rad(iy)),
                             np.sin(np.deg2rad(ip)), np.cos(np.deg2rad(ip))], axis=1)
            fused = b * ovec + (1.0 - b) * ivec
            fy, fp = decode_pred(fused)
            err = ic.angular_err_deg(fy, fp, yaw_t, pitch_t)
            seed_means.append(err.mean())
        results.append({"beta": float(b),
                        "mean": float(np.mean(seed_means)),
                        "std": float(np.std(seed_means))})
    best = min(results, key=lambda r: r["mean"])
    return results, best


def load_ocs_features(manifest_path, feat_mode, geom_subset=None):
    """加载 OCS 特征。geom_subset=None 用全部几何(concat5)；否则仅取指定 label。"""
    label_order, _, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(manifest_path)
    if geom_subset is not None:
        label_order = [l for l in label_order if l in geom_subset]
        if not label_order:
            raise RuntimeError(f"geom_subset {geom_subset} not found")
    feats, yaw, pitch, _ = ic.build_concat_features_with_mode(
        feat_dict, yaw_dict, pitch_dict, label_order, feat_mode)
    return feats, yaw, pitch, label_order


def align_to_images(ocs_feats, ocs_yaw, ocs_pitch, img_yaw, img_pitch):
    """按 (yaw,pitch) 对齐 OCS 到图像顺序，返回与图像同序的 OCS 矩阵 + 公共 mask。"""
    ocs_key = {(round(ocs_yaw[i], 4), round(ocs_pitch[i], 4)): i for i in range(len(ocs_yaw))}
    aligned = np.full((len(img_yaw), ocs_feats.shape[1]), np.nan)
    ok = np.zeros(len(img_yaw), dtype=bool)
    for i in range(len(img_yaw)):
        k = (round(img_yaw[i], 4), round(img_pitch[i], 4))
        if k in ocs_key:
            aligned[i] = ocs_feats[ocs_key[k]]
            ok[i] = True
    return aligned, ok


def main():
    ap = argparse.ArgumentParser(description="ResNet-branch fusion (Task A)")
    ap.add_argument("--image-dir", default=_IMAGE_DIR)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--image-size", type=int, default=128)
    ap.add_argument("--intensity", default="log1p")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--patience", type=int, default=100)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--dropout", type=float, default=0.10)
    ap.add_argument("--cases", default="A1,A2,A3,A4,A5",
                    help="逗号分隔的 case 列表")
    ap.add_argument("--seeds", type=int, nargs="+", default=None,
                    help="覆盖默认 5 seeds（用于 smoke test）")
    ap.add_argument("--smoke", action="store_true",
                    help="冒烟测试：1 seed + 少 epoch，验证管线")
    args = ap.parse_args()

    global SEEDS
    if args.smoke:
        SEEDS = [0]
        args.epochs = 8
        args.patience = 5
    elif args.seeds is not None:
        SEEDS = args.seeds

    if args.manifest is None:
        cands = sorted(glob.glob(_MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No manifest: {_MANIFEST_GLOB}")
        args.manifest = cands[0]

    cases = [c.strip() for c in args.cases.split(",") if c.strip()]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  ResNet-branch Fusion (Task A)")
    print(f"  Image dir: {args.image_dir}")
    print(f"  Manifest:  {args.manifest}")
    print(f"  Cases: {cases}")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    # 加载图像
    images, img_yaw, img_pitch = load_images(args.image_dir, args.image_size, args.intensity)
    split_img = ic.split_coarse_to_fine(img_yaw, img_pitch, coarse_step=10.0)
    print(f"  Image split: train_pool={split_img['n_train']} test={split_img['n_test']}")

    all_summaries = []
    late_data = {}  # 保存 A1 image preds + OCS MLP preds 用于 late fusion

    # ---- A1: ResNet image-only ----
    if "A1" in cases:
        print(f"\n{'='*60}\n  A1: ResNet image-only\n{'='*60}")
        s1, ps1, preds1, test_idx1 = run_image_only(
            images, img_yaw, img_pitch, split_img, args, out_dir, "A1")
        all_summaries.append(s1)
        late_data["img_preds"] = preds1
        late_data["test_idx"] = test_idx1
        late_data["yaw_t"] = img_yaw[test_idx1]
        late_data["pitch_t"] = img_pitch[test_idx1]
        save_seed_csv(out_dir, "A1", ps1)

    # ---- A2: ResNet-fusion + concat5 per_part_log 30D ----
    if "A2" in cases:
        print(f"\n{'='*60}\n  A2: ResNet-fusion + concat5 per_part_log 30D\n{'='*60}")
        feats, oy, op, labels = load_ocs_features(args.manifest, "per_part", geom_subset=None)
        aligned, ok = align_to_images(feats, oy, op, img_yaw, img_pitch)
        assert ok.all(), f"A2 对齐缺失 {(~ok).sum()} 个样本"
        sp = ic.split_coarse_to_fine(img_yaw, img_pitch, coarse_step=10.0)
        tr_idx, val_idx = make_train_val_idx(sp["train_idx"])
        ocs_zs_tr, ocs_zs_va, ocs_zs_te = prep_ocs(
            aligned, tr_idx, val_idx, sp["test_idx"], "log", log_skip=None)
        ocs_zs = np.full_like(aligned, 0.0)
        ocs_zs[tr_idx] = ocs_zs_tr; ocs_zs[val_idx] = ocs_zs_va; ocs_zs[sp["test_idx"]] = ocs_zs_te
        s2, ps2, _, _ = run_fusion(images, ocs_zs, img_yaw, img_pitch, sp, args,
                                   "A2", f"concat5 per_part_log {aligned.shape[1]}D")
        all_summaries.append(s2)
        save_seed_csv(out_dir, "A2", ps2)

    # ---- A3: ResNet-fusion + phase63 per_part_log 6D ----
    if "A3" in cases:
        print(f"\n{'='*60}\n  A3: ResNet-fusion + phase63 per_part_log 6D\n{'='*60}")
        feats, oy, op, labels = load_ocs_features(args.manifest, "per_part",
                                                  geom_subset={PHASE63_LABEL})
        aligned, ok = align_to_images(feats, oy, op, img_yaw, img_pitch)
        assert ok.all(), f"A3 对齐缺失 {(~ok).sum()} 个样本"
        sp = ic.split_coarse_to_fine(img_yaw, img_pitch, coarse_step=10.0)
        tr_idx, val_idx = make_train_val_idx(sp["train_idx"])
        ocs_zs_tr, ocs_zs_va, ocs_zs_te = prep_ocs(
            aligned, tr_idx, val_idx, sp["test_idx"], "log", log_skip=None)
        ocs_zs = np.full_like(aligned, 0.0)
        ocs_zs[tr_idx] = ocs_zs_tr; ocs_zs[val_idx] = ocs_zs_va; ocs_zs[sp["test_idx"]] = ocs_zs_te
        s3, ps3, _, _ = run_fusion(images, ocs_zs, img_yaw, img_pitch, sp, args,
                                   "A3", f"phase63 per_part_log {aligned.shape[1]}D")
        all_summaries.append(s3)
        save_seed_csv(out_dir, "A3", ps3)

    # ---- A4: ResNet-fusion + concat5 all_raw 45D ----
    if "A4" in cases:
        print(f"\n{'='*60}\n  A4: ResNet-fusion + concat5 all_raw 45D\n{'='*60}")
        feats, oy, op, labels = load_ocs_features(args.manifest, "all", geom_subset=None)
        aligned, ok = align_to_images(feats, oy, op, img_yaw, img_pitch)
        assert ok.all(), f"A4 对齐缺失 {(~ok).sum()} 个样本"
        sp = ic.split_coarse_to_fine(img_yaw, img_pitch, coarse_step=10.0)
        tr_idx, val_idx = make_train_val_idx(sp["train_idx"])
        # all_raw: raw transform, zscore only; 遮挡率列在 zscore 下无需特别处理
        ocs_zs_tr, ocs_zs_va, ocs_zs_te = prep_ocs(
            aligned, tr_idx, val_idx, sp["test_idx"], "raw", log_skip=None)
        ocs_zs = np.full_like(aligned, 0.0)
        ocs_zs[tr_idx] = ocs_zs_tr; ocs_zs[val_idx] = ocs_zs_va; ocs_zs[sp["test_idx"]] = ocs_zs_te
        s4, ps4, _, _ = run_fusion(images, ocs_zs, img_yaw, img_pitch, sp, args,
                                   "A4", f"concat5 all_raw {aligned.shape[1]}D")
        all_summaries.append(s4)
        save_seed_csv(out_dir, "A4", ps4)

    # ---- A5: Late fusion (ResNet image preds + OCS MLP preds) ----
    if "A5" in cases and "img_preds" in late_data:
        print(f"\n{'='*60}\n  A5: Late fusion (ResNet pred + OCS MLP pred)\n{'='*60}")
        ocs_mlp = load_existing_ocs_mlp_preds(late_data["yaw_t"], late_data["pitch_t"])
        if ocs_mlp is not None:
            sweep, best = late_fusion_sweep(
                late_data["img_preds"], ocs_mlp, late_data["yaw_t"], late_data["pitch_t"])
            print(f"    A5 best beta={best['beta']:.2f} mean={best['mean']:.2f}±{best['std']:.2f}°")
            with open(os.path.join(out_dir, "A5_late_fusion_sweep.csv"), "w",
                      encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["beta", "mean", "std"])
                w.writeheader(); w.writerows(sweep)
            all_summaries.append({"case": "A5", "model": "Late fusion ResNet+OCS-MLP",
                                  "best_beta": best["beta"],
                                  "angular_err_mean_mean": best["mean"],
                                  "angular_err_mean_std": best["std"]})
        else:
            print("    [A5 skip] 未找到可用的 OCS MLP 预测文件")

    # ---- 保存汇总 ----
    save_summary(out_dir, all_summaries, args)
    print(f"\n  Output: {out_dir}")
    return out_dir


def save_seed_csv(out_dir, case, per_seed):
    with open(os.path.join(out_dir, f"{case}_per_seed.csv"), "w",
              encoding="utf-8", newline="") as f:
        keys = ["seed", "n_params", "angular_err_mean", "angular_err_median",
                "angular_err_p90", "angular_err_p95", "angular_err_worst",
                "hit@5deg", "hit@10deg"]
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for m in per_seed:
            w.writerow({k: m.get(k, "") for k in keys})


def load_existing_ocs_mlp_preds(yaw_t, pitch_t):
    """尝试加载已有 OCS MLP 预测 (mlp_ocs run)，按 (yaw,pitch) 对齐到当前 test。
    用 all_raw 45D 的预测（最强 OCS 模型）。找不到返回 None。"""
    glob_pat = os.path.join(_PROJECT_ROOT, "结果", "模块C_反演", "mlp_ocs",
                            "run_*", "predictions_*all*raw*.csv")
    cands = sorted(glob.glob(glob_pat), key=os.path.getmtime, reverse=True)
    if not cands:
        # 退而求其次：任意 predictions csv
        glob_pat2 = os.path.join(_PROJECT_ROOT, "结果", "模块C_反演", "mlp_ocs",
                                 "run_*", "predictions*.csv")
        cands = sorted(glob.glob(glob_pat2), key=os.path.getmtime, reverse=True)
    if not cands:
        return None
    path = cands[0]
    pred_map = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                ty = float(r.get("true_yaw", r.get("yaw_true", "nan")))
                tp = float(r.get("true_pitch", r.get("pitch_true", "nan")))
                py = float(r.get("pred_yaw", r.get("yaw_mlp", "nan")))
                pp = float(r.get("pred_pitch", r.get("pitch_mlp", "nan")))
                pred_map[(round(ty, 4), round(tp, 4))] = (py, pp)
    except Exception:
        return None
    oy = np.full(len(yaw_t), np.nan); op = np.full(len(yaw_t), np.nan)
    miss = 0
    for i in range(len(yaw_t)):
        k = (round(yaw_t[i], 4), round(pitch_t[i], 4))
        if k in pred_map:
            oy[i], op[i] = pred_map[k]
        else:
            miss += 1
    if miss > len(yaw_t) * 0.5:
        print(f"    [A5] OCS MLP 对齐缺失 {miss}/{len(yaw_t)}，放弃 late fusion")
        return None
    # 缺失的用图像自身（不影响：填 nan→用最近，简单填均值方向）
    if miss > 0:
        print(f"    [A5] OCS MLP 对齐缺失 {miss} 个，用最近邻填充")
        good = np.isfinite(oy)
        oy[~good] = np.nanmean(oy[good]); op[~good] = np.nanmean(op[good])
    print(f"    [A5] 使用 OCS MLP 预测: {os.path.relpath(path, _PROJECT_ROOT)}")
    return oy, op


def save_summary(out_dir, summaries, args):
    # markdown 表
    lines = ["# ResNet-branch Fusion 结果 (Task A)", "",
             f"> Image dir: `{os.path.relpath(args.image_dir, _PROJECT_ROOT)}`",
             f"> Split: 10°→5°, {len(SEEDS)} seeds, log1p 128×128", "",
             "| Case | Model | mean±std | median | p90 | worst | Hit@5° | Hit@10° |",
             "|---|---|---|---:|---:|---:|---:|---:|"]
    for s in summaries:
        mean = s.get("angular_err_mean_mean", float("nan"))
        std = s.get("angular_err_mean_std", 0.0)
        med = s.get("angular_err_median_mean", float("nan"))
        p90 = s.get("angular_err_p90_mean", float("nan"))
        worst = s.get("angular_err_worst_mean", float("nan"))
        h5 = s.get("hit@5deg_mean", float("nan"))
        h10 = s.get("hit@10deg_mean", float("nan"))
        beta = f" (β={s['best_beta']:.2f})" if "best_beta" in s else ""
        lines.append(f"| {s['case']} | {s['model']}{beta} | "
                     f"{mean:.2f}±{std:.2f}° | "
                     f"{med:.2f}° | {p90:.2f}° | {worst:.1f}° | "
                     f"{h5:.1%} | {h10:.1%} |")
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"summaries": summaries, "config": vars(args), "seeds": SEEDS},
                  f, indent=2, ensure_ascii=False)
    # csv
    with open(os.path.join(out_dir, "summary.csv"), "w", encoding="utf-8", newline="") as f:
        keys = ["case", "model", "angular_err_mean_mean", "angular_err_mean_std",
                "angular_err_median_mean", "angular_err_p90_mean",
                "angular_err_worst_mean", "hit@5deg_mean", "hit@10deg_mean"]
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for s in summaries:
            w.writerow(s)
    print("\n  Summary table:")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

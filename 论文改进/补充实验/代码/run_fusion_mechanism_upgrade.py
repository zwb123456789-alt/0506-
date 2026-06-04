"""
run_fusion_mechanism_upgrade.py — 实验12：融合机制诊断与鲁棒融合升级
======================================================================
背景（实验11 已确认，严禁改写口径）：
  - ResNet image-only clean: 1.69±0.07°, Hit@5=97.6%
  - ResNet-fusion concat5 per_part_log clean: 1.47±0.07°, Hit@5=99.7%
  - ResNet image-only noise σ=0.01: 85.85±3.00°；fusion noise σ=0.01: 73.36±5.07°
  - OCS-only MLP per_part_log clean: 5.91°（不受图像退化影响，平线参照）
  -> Naive feature fusion 在图像噪声下没有回退到 OCS-only，而是接近 image-only 崩溃。

本实验回答：
  D. 当前 naive fusion 是否图像主导？图像退化时 OCS 信息是没用还是有用但 fusion 不切换？
  U. 退化增强 / 模态 dropout / OCS-anchored gated residual 能否让 OCS 真正 fallback？

不变口径（指导文件 §4 红线）：
  - split: 10° train -> 5° test (ic.split_coarse_to_fine, coarse_step=10)
  - 姿态编码: [sin(yaw),cos(yaw),sin(pitch),cos(pitch)]
  - 角误差: great-circle angular error (ic.angular_err_deg)
  - Hit@5: err <= 5° + 1e-6
  - OCS 主特征: concat5 per_part_log 30D
  - 图像: log1p 128x128, phase63 exact BRDF

诊断 D 复用实验11 的 train-clean 模型；升级 U 各自从头训练（online 退化/ dropout）。
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

warnings.filterwarnings("ignore", category=UserWarning)

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic

# 复用已验证脚本的类与函数（模型/编码/指标/退化算子）
import run_resnet_fusion as rf
import run_resnet_robustness as rr

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

_IMAGE_DIR = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染",
                          "run_20260528_101944_exact_brdf")
_MANIFEST_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块A_重构",
    "multi_geom_ggx_yaw73_pitch37", "run_*", "multi_geom_manifest.json")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                         "fusion_mechanism_upgrade")

SEEDS = [0, 1, 2, 3, 4]

# 参照常数（实验6/9/11 已确认，写入对照表）
_OCS_ONLY_MEAN = 5.91
_OCS_ONLY_HIT5 = 0.738
_IMG_ONLY_REF = {  # 实验9 ResNet image-only 退化曲线
    "clean": {"mean": 1.69, "hit5": 0.976},
    "noise_0.01": {"mean": 85.85, "hit5": 0.022},
    "noise_0.10": {"mean": 87.92, "hit5": 0.010},
    "bright_0.50": {"mean": 3.45, "hit5": 0.787},
    "bright_1.50": {"mean": 2.00, "hit5": 0.958},
}

# 评估时使用的退化档（与实验9/11 完全一致的算子与参数）
EVAL_DEGS = [
    {"name": "clean", "type": "none"},
    {"name": "noise_0.01", "type": "noise", "sigma": 0.01},
    {"name": "noise_0.10", "type": "noise", "sigma": 0.10},
    {"name": "bright_0.50", "type": "brightness", "scale": 0.50},
    {"name": "bright_1.50", "type": "brightness", "scale": 1.50},
]

# ============================================================
# 数据准备（与实验11 完全一致的加载/对齐/split/OCS 预处理）
# ============================================================
def prepare_data(args):
    """返回 images(N,1,H,W), ocs_zs(N,30), yaw, pitch, split, ocs_dim。

    OCS = concat5 per_part_log 30D，log+zscore（仅 fit train），与 A2/实验11 同款。
    OCS 全程干净（本实验只退化图像）。
    """
    images, img_yaw, img_pitch = rf.load_images(
        args.image_dir, args.image_size, args.intensity)

    feats, oy, op, labels = rf.load_ocs_features(args.manifest, "per_part", geom_subset=None)
    aligned, ok = rf.align_to_images(feats, oy, op, img_yaw, img_pitch)
    assert ok.all(), f"OCS 对齐缺失 {(~ok).sum()} 个样本"

    split = ic.split_coarse_to_fine(img_yaw, img_pitch, coarse_step=10.0)
    tr_idx, val_idx = rf.make_train_val_idx(split["train_idx"])
    test_idx = split["test_idx"]

    ocs_zs_tr, ocs_zs_va, ocs_zs_te = rf.prep_ocs(
        aligned, tr_idx, val_idx, test_idx, "log", log_skip=None)
    ocs_zs = np.full_like(aligned, 0.0)
    ocs_zs[tr_idx] = ocs_zs_tr
    ocs_zs[val_idx] = ocs_zs_va
    ocs_zs[test_idx] = ocs_zs_te

    print(f"    OCS aligned: {aligned.shape}, geoms={labels}")
    print(f"    Split: train_pool={split['n_train']} (tr={len(tr_idx)} val={len(val_idx)}) "
          f"test={split['n_test']}")
    return (images, ocs_zs, img_yaw, img_pitch, split,
            tr_idx, val_idx, test_idx, ocs_zs.shape[1])


def apply_image_degradation(images, deg):
    """复用实验9/11 的退化算子，保证可比。"""
    return rr.apply_degradation(images, deg)


# ============================================================
# 升级模型 U1-U3：带模态 dropout 的 naive fusion（结构同 A2）
# ============================================================
class RobustFusionModel(nn.Module):
    """与 rf.ResNetFusionModel 同构，但 forward 支持训练期模态 dropout
    （特征层随机将 f_img 或 f_ocs 置零）。推理时不 drop。
    分支遮蔽诊断也复用此前向（drop_image / drop_ocs 显式传入）。
    """

    def __init__(self, ocs_dim, dropout=0.10, p_drop_image=0.0, p_drop_ocs=0.0):
        super().__init__()
        self.backbone = rf.ResNet18Backbone()
        self.img_proj = nn.Sequential(nn.Linear(512, 128), nn.SiLU())
        self.ocs_branch = rf.OCSBranch(ocs_dim, dropout)
        self.fusion_head = nn.Sequential(
            nn.Linear(128 + 64, 128), nn.LayerNorm(128), nn.SiLU(), nn.Dropout(dropout),
            nn.Linear(128, 64), nn.SiLU(),
            nn.Linear(64, 4))
        self.p_drop_image = p_drop_image
        self.p_drop_ocs = p_drop_ocs

    def encode(self, img, ocs):
        f_img = self.img_proj(self.backbone(img))
        f_ocs = self.ocs_branch(ocs)
        return f_img, f_ocs

    def forward(self, img, ocs, drop_image=False, drop_ocs=False,
                img_mean=None, ocs_mean=None):
        f_img, f_ocs = self.encode(img, ocs)
        # 训练期模态 dropout（按样本独立伯努利）
        if self.training and (self.p_drop_image > 0 or self.p_drop_ocs > 0):
            B = f_img.size(0)
            if self.p_drop_image > 0:
                mask = (torch.rand(B, 1, device=f_img.device) >= self.p_drop_image).float()
                f_img = f_img * mask
            if self.p_drop_ocs > 0:
                mask = (torch.rand(B, 1, device=f_ocs.device) >= self.p_drop_ocs).float()
                f_ocs = f_ocs * mask
        # 诊断/推理期显式遮蔽（置零或替换 train mean）
        if drop_image:
            f_img = torch.zeros_like(f_img) if img_mean is None else img_mean.expand_as(f_img)
        if drop_ocs:
            f_ocs = torch.zeros_like(f_ocs) if ocs_mean is None else ocs_mean.expand_as(f_ocs)
        return self.fusion_head(torch.cat([f_img, f_ocs], dim=1))


# ============================================================
# 升级模型 U4：OCS-anchored gated residual fusion
# ============================================================
def normalize_pairs(vec):
    """对 4D sin/cos 输出，逐 (sin,cos) pair 归一化到单位圆。"""
    ys, yc, ps, pc = vec[:, 0], vec[:, 1], vec[:, 2], vec[:, 3]
    yr = torch.sqrt(ys * ys + yc * yc).clamp_min(1e-8)
    pr = torch.sqrt(ps * ps + pc * pc).clamp_min(1e-8)
    return torch.stack([ys / yr, yc / yr, ps / pr, pc / pr], dim=1)


class OCSAnchoredFusion(nn.Module):
    """OCS 为基准，图像只做残差修正，gate 控制图像残差权重。

      y_ocs_base = ocs_head(f_ocs)              # 4D, OCS 单独可用
      delta_img  = img_residual(f_img)          # 4D 残差
      g          = gate(cat[f_img,f_ocs]) in[0,1]
      y_fused    = normalize_pairs(y_ocs_base + g * delta_img)

    图像失效时，若 gate 学会变小，模型回退到 y_ocs_base。
    辅助损失 ocs_base_loss 保证 OCS 头单独可用（即 OCS fallback 的下限）。
    训练期对图像分支可施加特征 dropout，强迫 gate 学会关闭。
    """

    def __init__(self, ocs_dim, dropout=0.10, p_drop_image=0.0):
        super().__init__()
        self.backbone = rf.ResNet18Backbone()
        self.img_proj = nn.Sequential(nn.Linear(512, 128), nn.SiLU())
        self.ocs_branch = rf.OCSBranch(ocs_dim, dropout)
        self.ocs_head = nn.Sequential(
            nn.Linear(64, 64), nn.SiLU(), nn.Linear(64, 4))
        self.img_residual = nn.Sequential(
            nn.Linear(128, 64), nn.SiLU(), nn.Linear(64, 4))
        self.gate = nn.Sequential(
            nn.Linear(128 + 64, 64), nn.SiLU(), nn.Linear(64, 1), nn.Sigmoid())
        self.p_drop_image = p_drop_image

    def encode(self, img, ocs):
        f_img = self.img_proj(self.backbone(img))
        f_ocs = self.ocs_branch(ocs)
        return f_img, f_ocs

    def forward(self, img, ocs, drop_image=False, return_aux=False,
                img_mean=None):
        f_img, f_ocs = self.encode(img, ocs)
        if self.training and self.p_drop_image > 0:
            B = f_img.size(0)
            mask = (torch.rand(B, 1, device=f_img.device) >= self.p_drop_image).float()
            f_img = f_img * mask
        if drop_image:
            f_img = torch.zeros_like(f_img) if img_mean is None else img_mean.expand_as(f_img)
        y_ocs_base = self.ocs_head(f_ocs)
        delta_img = self.img_residual(f_img)
        g = self.gate(torch.cat([f_img, f_ocs], dim=1))
        y_fused = normalize_pairs(y_ocs_base + g * delta_img)
        if return_aux:
            return y_fused, normalize_pairs(y_ocs_base), g
        return y_fused

# ============================================================
# 训练与评估
# ============================================================
def _device():
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    if dev == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    return dev


def make_aug_fn(aug_degs, base_seed):
    """返回一个 online 增强函数：每次调用对一个 batch 的图像随机施加一种退化。

    aug_degs: 退化配置列表（含 clean）。在 numpy 上操作（与评估算子一致）。
    """
    rng = np.random.RandomState(base_seed)

    def aug(img_batch_np):
        # img_batch_np: (B,1,H,W) float32, log1p 空间
        out = img_batch_np.copy()
        for i in range(out.shape[0]):
            deg = aug_degs[rng.randint(len(aug_degs))]
            if deg["type"] == "none":
                continue
            single = out[i:i + 1]
            if deg["type"] == "noise":
                # 逐样本独立噪声种子
                r = np.random.RandomState(rng.randint(1 << 30))
                single = np.clip(single + r.randn(*single.shape).astype(np.float32) * deg["sigma"],
                                 0.0, 1.0)
            elif deg["type"] == "brightness":
                single = np.clip(single * deg["scale"], 0.0, 1.0)
            out[i:i + 1] = single
        return out

    return aug


# 升级训练用的退化增强档（U1/U3）
AUG_DEGS = [
    {"name": "clean", "type": "none"},
    {"name": "noise_0.01", "type": "noise", "sigma": 0.01},
    {"name": "noise_0.10", "type": "noise", "sigma": 0.10},
    {"name": "bright_0.50", "type": "brightness", "scale": 0.50},
    {"name": "bright_1.50", "type": "brightness", "scale": 1.50},
]


def train_model(model_factory, data, args, *, augment=False, anchored=False,
                lambda_aux=0.3, seed=0):
    """通用训练循环（一个 seed）。返回 best_state。

    model_factory(): 新建模型实例（已含 dropout 配置）。
    augment: True 时训练期对图像 batch online 施加 AUG_DEGS 退化。
    anchored: True 时模型为 OCSAnchoredFusion，使用 fused+aux 双损失。
    """
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = _device()
    crit = nn.MSELoss()

    Xi_tr = images[tr_idx]
    Xo_tr = torch.FloatTensor(ocs_zs[tr_idx]).to(device)
    y_tr = torch.FloatTensor(rf.encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    # val 始终 clean（early-stop 基于 clean 验证，避免选模型偏向噪声）
    Xi_va = torch.FloatTensor(images[val_idx]).to(device)
    Xo_va = torch.FloatTensor(ocs_zs[val_idx]).to(device)
    y_va = torch.FloatTensor(rf.encode_target(yaw[val_idx], pitch[val_idx])).to(device)

    torch.manual_seed(seed); np.random.seed(seed)
    model = model_factory().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    aug = make_aug_fn(AUG_DEGS, base_seed=1000 + seed) if augment else None
    n_tr = len(tr_idx)
    bs = args.batch_size

    Xo_tr_np = ocs_zs[tr_idx]  # 供 batch 索引
    y_tr_np = rf.encode_target(yaw[tr_idx], pitch[tr_idx])

    va_loader = DataLoader(TensorDataset(Xi_va, Xo_va, y_va), batch_size=bs * 2)

    best_va, best_state, wait, ep = float("inf"), None, 0, 0
    rng_ep = np.random.RandomState(seed)
    for ep in range(1, args.epochs + 1):
        model.train()
        perm = rng_ep.permutation(n_tr)
        for s in range(0, n_tr, bs):
            bidx = perm[s:s + bs]
            img_np = Xi_tr[bidx]
            if aug is not None:
                img_np = aug(img_np)
            xi = torch.FloatTensor(img_np).to(device)
            xo = torch.FloatTensor(Xo_tr_np[bidx]).to(device)
            yb = torch.FloatTensor(y_tr_np[bidx]).to(device)
            opt.zero_grad()
            if anchored:
                y_fused, y_base, _ = model(xi, xo, return_aux=True)
                loss = crit(y_fused, yb) + lambda_aux * crit(y_base, yb)
            else:
                loss = crit(model(xi, xo), yb)
            loss.backward()
            opt.step()
        # val（clean）
        model.eval()
        with torch.no_grad():
            tot = 0.0
            for xi, xo, yb in va_loader:
                pred = model(xi, xo)
                tot += crit(pred, yb).item() * len(xi)
            va = tot / len(val_idx)
        if va < best_va - 1e-8:
            best_va = va
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            wait = 0
        else:
            wait += 1
        if wait >= args.patience:
            break
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return best_state, ep, best_va


@torch.no_grad()
def eval_on_images(model, images_eval, ocs_zs, yaw, pitch, test_idx, args, **fwd_kwargs):
    """在给定（可能退化的）图像上评估，返回单 seed 指标 dict + err 数组。"""
    device = _device()
    Xi = torch.FloatTensor(images_eval[test_idx]).to(device)
    Xo = torch.FloatTensor(ocs_zs[test_idx]).to(device)
    bs = args.batch_size * 2
    model.eval()
    preds = []
    for s in range(0, len(test_idx), bs):
        xi = Xi[s:s + bs]; xo = Xo[s:s + bs]
        out = model(xi, xo, **fwd_kwargs)
        if isinstance(out, tuple):
            out = out[0]
        preds.append(out.cpu().numpy())
    pred = np.concatenate(preds)
    yp, pp = rf.decode_pred(pred)
    m, err = rf.compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
    return m, err


def compute_feature_means(model, images, ocs_zs, tr_idx, args):
    """在训练集上提取该模型的 f_img / f_ocs 均值（train mean），用于 D1 均值替换。"""
    device = _device()
    Xi = torch.FloatTensor(images[tr_idx]).to(device)
    Xo = torch.FloatTensor(ocs_zs[tr_idx]).to(device)
    bs = args.batch_size * 2
    model.eval()
    fi_sum, fo_sum, n = None, None, 0
    with torch.no_grad():
        for s in range(0, len(tr_idx), bs):
            fi, fo = model.encode(Xi[s:s + bs], Xo[s:s + bs])
            fi_sum = fi.sum(0) if fi_sum is None else fi_sum + fi.sum(0)
            fo_sum = fo.sum(0) if fo_sum is None else fo_sum + fo.sum(0)
            n += fi.size(0)
    return (fi_sum / n).unsqueeze(0), (fo_sum / n).unsqueeze(0)


def summarize_seeds(per_seed, keys=None):
    if keys is None:
        keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
                "angular_err_worst", "hit@5deg", "hit@10deg"]
    s = {}
    for k in keys:
        vals = [m[k] for m in per_seed]
        s[f"{k}_mean"] = float(np.mean(vals))
        s[f"{k}_std"] = float(np.std(vals))
    return s

# ============================================================
# 诊断 D：当前 naive fusion 是否图像主导
# ============================================================
def run_diagnostics(data, args):
    """训练 5 seed naive fusion（clean），做 D1-D4 诊断。

    D1/D2: 分支遮蔽（image_zero/image_train_mean/ocs_zero/ocs_train_mean）在 clean + 退化档。
    D3: 输出对 f_img/f_ocs 的梯度范数比 + fusion_head 第一层权重范数比。
    D4: 双向扰动（图像退化 vs OCS 退化）——OCS 退化对照引用实验8.2/noise_robustness。
    返回 (diag_rows, mechanism_text_pieces)。
    """
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = _device()

    print(f"\n{'='*64}\n  诊断 D：训练 naive fusion（clean，{len(SEEDS)} seeds）\n{'='*64}")
    t0 = time.time()
    states = []
    for seed in SEEDS:
        st, ep, bva = train_model(
            lambda: rf.ResNetFusionModel(ocs_dim=ocs_dim, dropout=args.dropout),
            data, args, augment=False, anchored=False, seed=seed)
        states.append(st)
        print(f"    train seed={seed} done (ep={ep}, best_va={bva:.6f})", flush=True)
    print(f"  naive fusion 训练耗时 {time.time()-t0:.0f}s")

    # 预计算各档退化图像（评估用，全部 seed 共享）
    deg_images = {}
    for deg in EVAL_DEGS:
        deg_images[deg["name"]] = apply_image_degradation(images, deg)

    # D1/D2：分支遮蔽
    modes = ["normal", "image_zero", "image_train_mean",
             "ocs_zero", "ocs_train_mean", "both_train_mean"]
    diag_rows = []
    for deg in EVAL_DEGS:
        dname = deg["name"]
        imgs_eval = deg_images[dname]
        for mode in modes:
            per_seed = []
            for seed, st in zip(SEEDS, states):
                model = rf.ResNetFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
                model.load_state_dict(st)
                # 用 RobustFusionModel 的 forward 支持遮蔽：拷贝权重到同构 robust 模型
                rmodel = RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
                rmodel.load_state_dict(st)  # 同构，键一致
                img_mean = ocs_mean = None
                if mode in ("image_train_mean", "ocs_train_mean", "both_train_mean"):
                    fi_m, fo_m = compute_feature_means(rmodel, images, ocs_zs, tr_idx, args)
                    img_mean, ocs_mean = fi_m, fo_m
                kw = dict(drop_image=False, drop_ocs=False)
                if mode == "image_zero":
                    kw["drop_image"] = True
                elif mode == "image_train_mean":
                    kw.update(drop_image=True, img_mean=img_mean)
                elif mode == "ocs_zero":
                    kw["drop_ocs"] = True
                elif mode == "ocs_train_mean":
                    kw.update(drop_ocs=True, ocs_mean=ocs_mean)
                elif mode == "both_train_mean":
                    kw.update(drop_image=True, drop_ocs=True,
                              img_mean=img_mean, ocs_mean=ocs_mean)
                m, _ = eval_on_images(rmodel, imgs_eval, ocs_zs, yaw, pitch, test_idx, args, **kw)
                per_seed.append(m)
            s = summarize_seeds(per_seed)
            s.update({"block": "D1D2", "degradation": dname, "mask_mode": mode})
            diag_rows.append(s)
            print(f"    [{dname:>12}] {mode:>16}: "
                  f"mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
                  f"Hit5={s['hit@5deg_mean']:.1%}", flush=True)

    # D3：梯度范数比 + 权重范数比
    print(f"\n  D3：梯度/权重贡献")
    grad_ratios, wnorm_ratios = [], []
    for seed, st in zip(SEEDS, states):
        model = RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
        model.load_state_dict(st)
        model.eval()
        # 梯度范数：在 clean test batch 上，d(MSE)/d f_img vs d/d f_ocs
        Xi = torch.FloatTensor(images[test_idx]).to(device)
        Xo = torch.FloatTensor(ocs_zs[test_idx]).to(device)
        yt = torch.FloatTensor(rf.encode_target(yaw[test_idx], pitch[test_idx])).to(device)
        f_img, f_ocs = model.encode(Xi, Xo)
        f_img = f_img.detach().requires_grad_(True)
        f_ocs = f_ocs.detach().requires_grad_(True)
        pred = model.fusion_head(torch.cat([f_img, f_ocs], dim=1))
        loss = nn.functional.mse_loss(pred, yt)
        gi, go = torch.autograd.grad(loss, [f_img, f_ocs])
        # 归一化到每维，消除 128 vs 64 维度差
        gi_n = gi.norm().item() / np.sqrt(f_img.numel())
        go_n = go.norm().item() / np.sqrt(f_ocs.numel())
        grad_ratios.append(gi_n / max(go_n, 1e-12))
        # 权重范数：fusion_head[0] 第一层 Linear，按输入维拆 image 128 / OCS 64
        W = model.fusion_head[0].weight.detach()  # (128, 192)
        Wi = W[:, :128]; Wo = W[:, 128:]
        wi = Wi.abs().mean().item(); wo = Wo.abs().mean().item()
        wnorm_ratios.append(wi / max(wo, 1e-12))
    d3 = {"block": "D3",
          "grad_norm_ratio_img_over_ocs_mean": float(np.mean(grad_ratios)),
          "grad_norm_ratio_img_over_ocs_std": float(np.std(grad_ratios)),
          "weight_absmean_ratio_img_over_ocs_mean": float(np.mean(wnorm_ratios)),
          "weight_absmean_ratio_img_over_ocs_std": float(np.std(wnorm_ratios))}
    print(f"    grad norm ratio (img/ocs) = {d3['grad_norm_ratio_img_over_ocs_mean']:.3f}"
          f"±{d3['grad_norm_ratio_img_over_ocs_std']:.3f}")
    print(f"    weight |.| ratio (img/ocs) = {d3['weight_absmean_ratio_img_over_ocs_mean']:.3f}"
          f"±{d3['weight_absmean_ratio_img_over_ocs_std']:.3f}")
    diag_rows.append(d3)

    return diag_rows, states

# ============================================================
# 升级 U：让 OCS 能够 fallback
# ============================================================
def eval_variant_across_degs(states, data, args, *, anchored=False, deg_images=None):
    """对一组（5 seed）模型在所有 EVAL_DEGS 上评估，返回 rows（每档一行汇总）。"""
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = _device()
    if deg_images is None:
        deg_images = {d["name"]: apply_image_degradation(images, d) for d in EVAL_DEGS}

    rows = []
    for deg in EVAL_DEGS:
        dname = deg["name"]
        imgs_eval = deg_images[dname]
        per_seed = []
        gate_means = []
        for seed, st in zip(SEEDS, states):
            if anchored:
                model = OCSAnchoredFusion(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
            else:
                model = RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
            model.load_state_dict(st)
            m, _ = eval_on_images(model, imgs_eval, ocs_zs, yaw, pitch, test_idx, args)
            per_seed.append(m)
            if anchored:
                # 记录该档平均 gate 值（图像残差权重）
                Xi = torch.FloatTensor(imgs_eval[test_idx]).to(device)
                Xo = torch.FloatTensor(ocs_zs[test_idx]).to(device)
                model.eval()
                with torch.no_grad():
                    bs = args.batch_size * 2
                    gs = []
                    for s in range(0, len(test_idx), bs):
                        _, _, g = model(Xi[s:s+bs], Xo[s:s+bs], return_aux=True)
                        gs.append(g.cpu().numpy())
                gate_means.append(float(np.concatenate(gs).mean()))
        s = summarize_seeds(per_seed)
        s["degradation"] = dname
        if anchored and gate_means:
            s["gate_mean"] = float(np.mean(gate_means))
            s["gate_std"] = float(np.std(gate_means))
        rows.append(s)
        extra = f" gate={s['gate_mean']:.3f}" if "gate_mean" in s else ""
        print(f"    [{dname:>12}] mean={s['angular_err_mean_mean']:.2f}"
              f"±{s['angular_err_mean_std']:.2f}° Hit5={s['hit@5deg_mean']:.1%}{extra}",
              flush=True)
    return rows


def run_upgrades(data, args):
    """U1-U4 训练 + 跨退化档评估。返回 dict[variant -> rows]。"""
    images = data[0]
    deg_images = {d["name"]: apply_image_degradation(images, d) for d in EVAL_DEGS}
    ocs_dim = data[-1]
    upgrade = {}

    variants = []
    if args.run_augment:
        variants.append(("U1_augment", dict(augment=True, p_img=0.0, p_ocs=0.0, anchored=False)))
    if args.run_modality_dropout:
        variants.append(("U2_moddrop", dict(augment=False, p_img=0.3, p_ocs=0.15, anchored=False)))
    if args.run_combined:
        variants.append(("U3_aug_moddrop", dict(augment=True, p_img=0.3, p_ocs=0.15, anchored=False)))
    if args.run_anchored:
        variants.append(("U4_anchored", dict(augment=True, p_img=0.3, p_ocs=0.0, anchored=True)))

    for vname, cfg in variants:
        print(f"\n{'='*64}\n  升级 {vname}  cfg={cfg}\n{'='*64}")
        t0 = time.time()
        states = []
        for seed in SEEDS:
            if cfg["anchored"]:
                factory = (lambda c=cfg: OCSAnchoredFusion(
                    ocs_dim=ocs_dim, dropout=args.dropout, p_drop_image=c["p_img"]))
            else:
                factory = (lambda c=cfg: RobustFusionModel(
                    ocs_dim=ocs_dim, dropout=args.dropout,
                    p_drop_image=c["p_img"], p_drop_ocs=c["p_ocs"]))
            st, ep, bva = train_model(
                factory, data, args,
                augment=cfg["augment"], anchored=cfg["anchored"],
                lambda_aux=args.lambda_aux, seed=seed)
            states.append(st)
            print(f"    train seed={seed} done (ep={ep}, best_va={bva:.6f})", flush=True)
        print(f"  {vname} 训练耗时 {time.time()-t0:.0f}s")
        rows = eval_variant_across_degs(states, data, args,
                                        anchored=cfg["anchored"], deg_images=deg_images)
        for r in rows:
            r["variant"] = vname
        upgrade[vname] = rows

    return upgrade

# ============================================================
# 保存产物
# ============================================================
def save_diagnostics(out_dir, diag_rows):
    with open(os.path.join(out_dir, "diagnostics_results.json"), "w", encoding="utf-8") as f:
        json.dump(diag_rows, f, indent=2, ensure_ascii=False)
    # D1D2 表
    d12 = [r for r in diag_rows if r.get("block") == "D1D2"]
    with open(os.path.join(out_dir, "diagnostics_results.csv"), "w",
              encoding="utf-8", newline="") as f:
        keys = ["block", "degradation", "mask_mode", "angular_err_mean_mean",
                "angular_err_mean_std", "angular_err_p90_mean", "hit@5deg_mean",
                "hit@10deg_mean"]
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in d12:
            w.writerow(r)


def save_upgrades(out_dir, upgrade):
    flat = []
    for vname, rows in upgrade.items():
        flat.extend(rows)
    with open(os.path.join(out_dir, "upgrade_results.json"), "w", encoding="utf-8") as f:
        json.dump(upgrade, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "upgrade_results.csv"), "w",
              encoding="utf-8", newline="") as f:
        keys = ["variant", "degradation", "angular_err_mean_mean", "angular_err_mean_std",
                "angular_err_p90_mean", "angular_err_worst_mean",
                "hit@5deg_mean", "hit@10deg_mean", "gate_mean", "gate_std"]
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in flat:
            w.writerow(r)


def _get(diag_rows, dname, mode):
    for r in diag_rows:
        if r.get("block") == "D1D2" and r["degradation"] == dname and r["mask_mode"] == mode:
            return r
    return None


def write_mechanism_summary(out_dir, diag_rows, upgrade, args):
    L = []
    L.append("# 实验12：融合机制诊断与鲁棒融合升级 — 机制总结\n")
    L.append(f"> 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    L.append(f"> Split：10°→5°，{len(SEEDS)} seeds；OCS=concat5 per_part_log 30D（全程干净）；"
             "图像 log1p 128×128（phase63 exact BRDF）。  ")
    L.append("> 退化算子与参数与实验9/11 完全一致。OCS-only 参照 5.91°（实验6，平线）。\n")

    # ---- D1/D2 ----
    L.append("## D1/D2：分支遮蔽 / 退化图像遮蔽\n")
    L.append("| 退化 | normal | image_zero | image_train_mean | ocs_zero | ocs_train_mean | both_train_mean |")
    L.append("|---|---|---|---|---|---|---|")
    for deg in EVAL_DEGS:
        dn = deg["name"]
        cells = []
        for mode in ["normal", "image_zero", "image_train_mean",
                     "ocs_zero", "ocs_train_mean", "both_train_mean"]:
            r = _get(diag_rows, dn, mode)
            cells.append(f"{r['angular_err_mean_mean']:.2f}° ({r['hit@5deg_mean']:.0%})" if r else "—")
        L.append(f"| {dn} | " + " | ".join(cells) + " |")
    L.append("\n> 单元格为 mean angular error (Hit@5°)。image_zero/image_train_mean=遮蔽图像分支；"
             "ocs_*=遮蔽 OCS 分支。\n")

    # 机制判读
    norm_clean = _get(diag_rows, "clean", "normal")
    ocsz_clean = _get(diag_rows, "clean", "ocs_zero")
    imgz_clean = _get(diag_rows, "clean", "image_zero")
    norm_n01 = _get(diag_rows, "noise_0.01", "normal")
    imgz_n01 = _get(diag_rows, "noise_0.01", "image_zero")
    imgm_n01 = _get(diag_rows, "noise_0.01", "image_train_mean")
    norm_n10 = _get(diag_rows, "noise_0.10", "normal")
    imgm_n10 = _get(diag_rows, "noise_0.10", "image_train_mean")

    L.append("### 机制判读（关键问题：OCS 是没信息，还是有信息但 fusion 不切换？）\n")
    if all(x is not None for x in [norm_clean, ocsz_clean, imgz_clean]):
        L.append(f"- **clean**：normal={norm_clean['angular_err_mean_mean']:.2f}°，"
                 f"遮蔽 OCS（ocs_zero）后={ocsz_clean['angular_err_mean_mean']:.2f}°，"
                 f"遮蔽图像（image_zero）后={imgz_clean['angular_err_mean_mean']:.2f}°。")
        if ocsz_clean['angular_err_mean_mean'] < imgz_clean['angular_err_mean_mean']:
            L.append("  - clean 下遮蔽图像的损害 >> 遮蔽 OCS → **图像主导**（与图像信息更丰富一致）。")
    if all(x is not None for x in [norm_n01, imgz_n01, imgm_n01]):
        L.append(f"- **noise σ=0.01**：normal（用退化图像）={norm_n01['angular_err_mean_mean']:.2f}°，"
                 f"遮蔽退化图像后 image_zero={imgz_n01['angular_err_mean_mean']:.2f}°，"
                 f"image_train_mean={imgm_n01['angular_err_mean_mean']:.2f}°，"
                 f"OCS-only 参照=5.91°。")
        gap = norm_n01['angular_err_mean_mean'] - imgm_n01['angular_err_mean_mean']
        L.append(f"  - 屏蔽退化图像分支后误差变化 = {gap:+.2f}°（normal − image_train_mean）。")
        if imgm_n01['angular_err_mean_mean'] < norm_n01['angular_err_mean_mean'] - 10:
            L.append("  - **结论：OCS 信息存在且有用**。屏蔽退化图像后误差大幅下降并接近 OCS-only，"
                     "说明 naive fusion 在图像噪声下被退化图像误导，而非 OCS 无信息。"
                     "问题是 **fusion head 不会在图像失效时切换到 OCS**。")
        else:
            L.append("  - 屏蔽退化图像后误差未明显改善 → 需进一步分析（fusion head 已把退化图像"
                     "特征耦合进 OCS 通道，或 train-mean 替换不足以恢复）。")
    L.append("")

    # ---- D3 ----
    d3 = next((r for r in diag_rows if r.get("block") == "D3"), None)
    L.append("## D3：梯度 / 权重贡献（supporting diagnostic，非因果证据）\n")
    if d3:
        L.append(f"- 输出 MSE 对特征的梯度范数比 image/OCS（每维归一化）= "
                 f"{d3['grad_norm_ratio_img_over_ocs_mean']:.3f}±{d3['grad_norm_ratio_img_over_ocs_std']:.3f}")
        L.append(f"- fusion_head 第一层权重 |·| 均值比 image/OCS = "
                 f"{d3['weight_absmean_ratio_img_over_ocs_mean']:.3f}±{d3['weight_absmean_ratio_img_over_ocs_std']:.3f}")
        L.append("- 注：权重范数不是因果证据，仅作辅助机制证据。\n")

    # ---- D4 ----
    L.append("## D4：双向扰动不对称性\n")
    L.append("- 图像退化、OCS clean：naive fusion 被图像拖垮（实验11：σ=0.01→73.36°）。")
    L.append("- OCS 退化、图像 clean：fusion 被图像托住（实验8.2 noise_robustness，"
             "OCS 噪声 0→20% 时 fusion 对 OCS-only 仍有正补偿）。")
    L.append("- → 鲁棒性高度不对称：naive fusion 只在 OCS 退化方向鲁棒，图像退化方向不鲁棒。\n")

    # ---- U ----
    L.append("## 升级 U：让 OCS fallback\n")
    if upgrade:
        L.append("| 方案 | clean | noise σ=0.01 | noise σ=0.10 | bright×0.5 | bright×1.5 |")
        L.append("|---|---|---|---|---|---|")
        for vname, rows in upgrade.items():
            cells = []
            for dn in ["clean", "noise_0.01", "noise_0.10", "bright_0.50", "bright_1.50"]:
                r = next((x for x in rows if x["degradation"] == dn), None)
                cells.append(f"{r['angular_err_mean_mean']:.2f}° ({r['hit@5deg_mean']:.0%})" if r else "—")
            L.append(f"| {vname} | " + " | ".join(cells) + " |")
        L.append("\n> 参照：naive fusion noise σ=0.01=73.36°；image-only σ=0.01=85.85°；OCS-only=5.91°。")
        # gate 报告
        for vname, rows in upgrade.items():
            if any("gate_mean" in r for r in rows):
                L.append(f"\n### {vname} gate（图像残差权重）随退化变化")
                for r in rows:
                    if "gate_mean" in r:
                        L.append(f"- {r['degradation']}: gate={r['gate_mean']:.3f}±{r['gate_std']:.3f}")
    L.append("")

    # ---- 成功/失败判定 ----
    L.append("## 成功 / 部分成功 / 失败判定\n")
    L.append(_judge_upgrades(upgrade))

    with open(os.path.join(out_dir, "mechanism_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("\n  mechanism_summary.md 已写入")


def _judge_upgrades(upgrade):
    """按指导文件 §7 自动判定每个升级方案。"""
    if not upgrade:
        return "未运行升级实验。"
    lines = []
    for vname, rows in upgrade.items():
        clean = next((r for r in rows if r["degradation"] == "clean"), None)
        n01 = next((r for r in rows if r["degradation"] == "noise_0.01"), None)
        n10 = next((r for r in rows if r["degradation"] == "noise_0.10"), None)
        if not (clean and n01 and n10):
            continue
        c = clean["angular_err_mean_mean"]
        a = n01["angular_err_mean_mean"]
        b = n10["angular_err_mean_mean"]
        worst_noise = max(a, b)
        if c <= 2.5 and worst_noise <= 5.91 * 1.3:
            verdict = "**成功**：clean 保持，图像噪声接近 OCS-only fallback。"
        elif c <= 3.0 and worst_noise < 15.0:
            verdict = "**接近成功**：噪声档 < 15°，clean 轻微代价。"
        elif worst_noise < 73.36 * 0.6:
            verdict = "**部分成功**：噪声档显著低于 naive fusion 73°，但未达 fallback。trade-off。"
        else:
            verdict = "**失败**：图像噪声下仍接近 naive fusion 崩溃，简单鲁棒训练不足。"
        lines.append(f"- {vname}: clean={c:.2f}°, noise σ0.01={a:.2f}°, σ0.10={b:.2f}° → {verdict}")
    return "\n".join(lines) if lines else "升级结果不完整。"

def main():
    import glob
    ap = argparse.ArgumentParser(description="Exp12: fusion mechanism diagnosis + robust upgrade")
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
    ap.add_argument("--lambda-aux", type=float, default=0.3)
    ap.add_argument("--run-diagnostics", action="store_true")
    ap.add_argument("--run-augment", action="store_true")
    ap.add_argument("--run-modality-dropout", action="store_true")
    ap.add_argument("--run-combined", action="store_true")
    ap.add_argument("--run-anchored", action="store_true")
    ap.add_argument("--all", action="store_true", help="跑 D + U1-U4 全部")
    ap.add_argument("--seeds", type=int, nargs="+", default=None)
    ap.add_argument("--smoke", action="store_true", help="冒烟：1 seed + 少 epoch")
    args = ap.parse_args()

    global SEEDS
    if args.smoke:
        SEEDS = [0]
        args.epochs = 6
        args.patience = 4
    elif args.seeds is not None:
        SEEDS = args.seeds

    if args.all:
        args.run_diagnostics = True
        args.run_augment = True
        args.run_modality_dropout = True
        args.run_combined = True
        args.run_anchored = True
    # 若什么都没指定，默认全跑
    if not any([args.run_diagnostics, args.run_augment, args.run_modality_dropout,
                args.run_combined, args.run_anchored]):
        args.run_diagnostics = True
        args.run_augment = True
        args.run_modality_dropout = True
        args.run_combined = True
        args.run_anchored = True

    if args.manifest is None:
        cands = sorted(glob.glob(_MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No manifest: {_MANIFEST_GLOB}")
        args.manifest = cands[0]

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    # 自写日志 Tee（绕 Windows 后台重定向问题）
    log_f = open(os.path.join(out_dir, "run.log"), "w", encoding="utf-8", buffering=1)

    class Tee:
        def __init__(self, *streams):
            self.streams = streams

        def write(self, s):
            for st in self.streams:
                try:
                    st.write(s); st.flush()
                except Exception:
                    pass

        def flush(self):
            for st in self.streams:
                try:
                    st.flush()
                except Exception:
                    pass

    sys.stdout = Tee(sys.__stdout__, log_f)
    sys.stderr = Tee(sys.__stderr__, log_f)

    print("=" * 70)
    print("  实验12：融合机制诊断与鲁棒融合升级")
    print(f"  Image dir: {args.image_dir}")
    print(f"  Manifest:  {args.manifest}")
    print(f"  Output:    {out_dir}")
    print(f"  Seeds: {SEEDS}  epochs={args.epochs} patience={args.patience}")
    print(f"  Device: {_device()}")
    print(f"  Runs: diag={args.run_diagnostics} aug={args.run_augment} "
          f"moddrop={args.run_modality_dropout} combined={args.run_combined} "
          f"anchored={args.run_anchored}")
    print("=" * 70)

    t_all = time.time()
    print("\n  [准备数据]")
    data = prepare_data(args)

    diag_rows, states = [], None
    if args.run_diagnostics:
        diag_rows, states = run_diagnostics(data, args)
        save_diagnostics(out_dir, diag_rows)

    upgrade = {}
    if any([args.run_augment, args.run_modality_dropout, args.run_combined, args.run_anchored]):
        upgrade = run_upgrades(data, args)
        save_upgrades(out_dir, upgrade)

    # 机制总结
    write_mechanism_summary(out_dir, diag_rows, upgrade, args)

    # 顶层 summary.json
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "config": vars(args), "seeds": SEEDS,
            "references": {"ocs_only_mean": _OCS_ONLY_MEAN, "ocs_only_hit5": _OCS_ONLY_HIT5,
                           "image_only_ref": _IMG_ONLY_REF,
                           "naive_fusion_noise001": 73.36, "naive_fusion_noise010": 73.57},
            "n_diag_rows": len(diag_rows), "n_upgrade_variants": len(upgrade),
            "elapsed_sec": time.time() - t_all,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  全部完成，总耗时 {time.time()-t_all:.0f}s")
    print(f"  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()






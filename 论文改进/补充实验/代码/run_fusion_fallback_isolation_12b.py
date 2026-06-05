"""
run_fusion_fallback_isolation_12b.py — 实验12b：融合 fallback 因果隔离与鲁棒性补强
================================================================================
背景（实验12 已确认，严禁改写口径）：
  - Naive clean-trained feature fusion 图像主导，图像噪声下崩溃（σ=0.01→75.08°）。
  - 屏蔽退化图像→52.84°（改善但远高于 OCS-only 5.91°）；屏蔽 OCS→88.88°（更差）。
    => OCS 信息存在且有用，但 naive fusion head 没有学会 OCS-standalone fallback。
  - U1 图像退化增强将 fusion 在已测试退化下 mean/p90/Hit@5 拉回强水平（~2°），
    但**尚未隔离**：U1 的成功是 image-only 增强就能解释，还是 fusion 真的用了 OCS？

本脚本回答（指导文件 §3 五组实验）：
  12b-1  ResNet image-only + 与 U1 完全相同的图像增强 → U1 优势是否仅由图像增强解释。
  12b-2  U1 augmented fusion 分支遮蔽（image/OCS × zero/train_mean）→ 图像退化时是否用 OCS。
  12b-3  U1 的 OCS 噪声 × 图像退化双扰动 → 扰动 OCS 是否影响 U1。
  12b-4  U1 大离群样本审计（>30/60/90°）→ 解释 mean/p90 好但 worst>100° 的矛盾。
  12b-5  未见退化泛化（noise 0.03/0.05, blur k3/k5, downsample 64/32）→ matched vs broader robustness。

不变口径（指导文件 §2 红线）：
  - split: 10° train -> 5° test
  - target encoding: [sin(yaw),cos(yaw),sin(pitch),cos(pitch)]
  - 角误差: great-circle；Hit@5/10: err <= 阈值 + 1e-6
  - OCS: concat5 per_part_log 30D（全程干净，除 12b-3 显式扰动）
  - image: phase63 exact BRDF, log1p 128x128
  - seeds: 与实验12 一致，优先 5 seeds

复用实验12/既有脚本组件，不破坏实验12 入口，不覆盖 run_20260604_092041。
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

# 实验12 主脚本：复用 RobustFusionModel / make_aug_fn / AUG_DEGS / EVAL_DEGS /
#                train_model / eval_on_images / compute_feature_means / summarize_seeds /
#                apply_image_degradation / _device / prepare_data 同款数据管线
import run_fusion_mechanism_upgrade as up
import run_resnet_fusion as rf
import run_resnet_robustness as rr

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

_IMAGE_DIR = up._IMAGE_DIR
_MANIFEST_GLOB = up._MANIFEST_GLOB
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                         "fusion_fallback_isolation_12b")

SEEDS = [0, 1, 2, 3, 4]

# 汇总统计键（含 p95，满足指导 §4 “mean/median/p90/p95或worst/Hit@5/Hit@10”）
SUM_KEYS = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "angular_err_worst", "hit@5deg", "hit@10deg"]

# 参照常数（实验6/9/11/12，已确认口径，仅作对照，非本脚本产物）
REF = {
    "ocs_only_mean": 5.91, "ocs_only_hit5": 0.738,
    "image_only_clean": {"clean": 1.69, "noise_0.01": 85.85, "noise_0.10": 87.92,
                         "bright_0.50": 3.45, "bright_1.50": 2.00},
    "naive_fusion": {"clean": 1.47, "noise_0.01": 73.36, "noise_0.10": 73.57,
                     "bright_0.50": 1.86, "bright_1.50": 1.49},
}

# 12b-5 未见退化（不进训练增强）。算子/参数复用 run_resnet_robustness。
HELDOUT_DEGS = [
    {"name": "noise_0.03", "type": "noise", "sigma": 0.03},
    {"name": "noise_0.05", "type": "noise", "sigma": 0.05},
    {"name": "blur_k3", "type": "blur", "kernel": 3},
    {"name": "blur_k5", "type": "blur", "kernel": 5},
    {"name": "downsample_64", "type": "downsample", "size": 64},
    {"name": "downsample_32", "type": "downsample", "size": 32},
]

# 12b-3 OCS 噪声 × 图像退化矩阵（指导 §3 12b-3）
OCS_NOISE_MATRIX = [
    ("clean", [0.01, 0.05, 0.10, 0.20]),
    ("noise_0.01", [0.01, 0.05, 0.10, 0.20]),
    ("noise_0.10", [0.01, 0.05, 0.10, 0.20]),
    ("bright_0.50", [0.05, 0.10]),
    ("bright_1.50", [0.05, 0.10]),
]


# ============================================================
# 数据准备（与实验12/A2 完全一致，额外返回 raw OCS 与 log-zscore 统计量供 12b-3 加噪）
# ============================================================
def prepare_data_ext(args):
    """返回 (data, aligned_raw, log_mu, log_sd)。

    data 与 up.prepare_data 同结构：
      (images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim)
    aligned_raw: 与图像同序的原始 per_part OCS 30D（log/zscore 之前），供 12b-3 在
                 标准化前加相对噪声后再用 train 统计量标准化。
    log_mu/log_sd: 在 log10(train) 上拟合的标准化参数（与 rf.prep_ocs 一致）。
    """
    images, img_yaw, img_pitch = rf.load_images(
        args.image_dir, args.image_size, args.intensity)

    feats, oy, op, labels = rf.load_ocs_features(args.manifest, "per_part", geom_subset=None)
    aligned, ok = rf.align_to_images(feats, oy, op, img_yaw, img_pitch)
    assert ok.all(), f"OCS 对齐缺失 {(~ok).sum()} 个样本"

    split = ic.split_coarse_to_fine(img_yaw, img_pitch, coarse_step=10.0)
    tr_idx, val_idx = rf.make_train_val_idx(split["train_idx"])
    test_idx = split["test_idx"]

    # log10 -> zscore（仅 fit train），与 rf.prep_ocs / 实验11 A2 同款
    log_all = ic.log_transform(aligned, skip_cols=None)
    _, log_mu, log_sd = ic.zscore(log_all[tr_idx], return_params=True)
    ocs_zs = ((log_all - log_mu) / log_sd).astype(np.float32)

    print(f"    OCS aligned: {aligned.shape}, geoms={labels}")
    print(f"    Split: train_pool={split['n_train']} (tr={len(tr_idx)} val={len(val_idx)}) "
          f"test={split['n_test']}")
    data = (images, ocs_zs, img_yaw, img_pitch, split,
            tr_idx, val_idx, test_idx, ocs_zs.shape[1])
    return data, aligned, log_mu, log_sd


def make_ocs_noisy_zs(aligned_raw, log_mu, log_sd, noise_level, seed):
    """对原始 OCS 特征加相对噪声，再用 train 统计量标准化。

    方法（指导 §3 12b-3 首选项）：raw-feature relative perturbation, re-standardized。
      noisy = raw + noise_level * |raw| * N(0,1)   （与实验6 乘性相对噪声同形）
      zs    = (log10(max(noisy,eps)) - log_mu) / log_sd  （train 统计量，不改 OCS-only 基准）
    注意：这是对 raw per_part 特征加噪后再标准化，**不是**对 ocs_zs 直接加噪，
          也不等同实验6 的端到端 OCS-only 评估口径（此处 OCS 进的是 fusion head）。
    """
    rng = np.random.RandomState(seed)
    noisy = aligned_raw + noise_level * np.abs(aligned_raw) * rng.randn(*aligned_raw.shape)
    log_noisy = ic.log_transform(noisy, skip_cols=None)
    return ((log_noisy - log_mu) / log_sd).astype(np.float32)


# ============================================================
# image-only 训练 / 评估（12b-1）
# ============================================================
def train_image_only(data, args, seed, augment=True):
    """训练 ResNet image-only（可选与 U1 完全相同的在线图像增强）。返回 best_state。"""
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = up._device()
    crit = nn.MSELoss()

    Xi_tr_np = images[tr_idx]
    y_tr_np = rf.encode_target(yaw[tr_idx], pitch[tr_idx])
    Xi_va = torch.FloatTensor(images[val_idx]).to(device)   # val 始终 clean
    y_va = torch.FloatTensor(rf.encode_target(yaw[val_idx], pitch[val_idx])).to(device)

    torch.manual_seed(seed); np.random.seed(seed)
    model = rf.ResNetImageOnly().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)

    # 与 up.train_model 完全一致的增强源（AUG_DEGS + base_seed=1000+seed）
    aug = up.make_aug_fn(up.AUG_DEGS, base_seed=1000 + seed) if augment else None
    n_tr = len(tr_idx); bs = args.batch_size
    va_loader = DataLoader(TensorDataset(Xi_va, y_va), batch_size=bs * 2)

    best_va, best_state, wait, ep = float("inf"), None, 0, 0
    rng_ep = np.random.RandomState(seed)
    for ep in range(1, args.epochs + 1):
        model.train()
        perm = rng_ep.permutation(n_tr)
        for s in range(0, n_tr, bs):
            bidx = perm[s:s + bs]
            img_np = Xi_tr_np[bidx]
            if aug is not None:
                img_np = aug(img_np)
            xi = torch.FloatTensor(img_np).to(device)
            yb = torch.FloatTensor(y_tr_np[bidx]).to(device)
            opt.zero_grad()
            loss = crit(model(xi), yb)
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            tot = 0.0
            for xi, yb in va_loader:
                tot += crit(model(xi), yb).item() * len(xi)
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
def eval_image_only(state, images_eval, yaw, pitch, test_idx, args):
    device = up._device()
    model = rf.ResNetImageOnly().to(device)
    model.load_state_dict(state); model.eval()
    Xi = torch.FloatTensor(images_eval[test_idx]).to(device)
    bs = args.batch_size * 2
    preds = []
    for s in range(0, len(test_idx), bs):
        preds.append(model(Xi[s:s + bs]).cpu().numpy())
    pred = np.concatenate(preds)
    yp, pp = rf.decode_pred(pred)
    m, err = rf.compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
    return m, err, yp, pp


# ============================================================
# fusion 评估（带预测，支持分支遮蔽）—— 12b-2/3/4/5 共用
# ============================================================
@torch.no_grad()
def eval_fusion_with_preds(state, images_eval, ocs_zs, yaw, pitch, test_idx,
                           args, ocs_dim, **fwd):
    device = up._device()
    model = up.RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
    model.load_state_dict(state); model.eval()
    Xi = torch.FloatTensor(images_eval[test_idx]).to(device)
    Xo = torch.FloatTensor(ocs_zs[test_idx]).to(device)
    bs = args.batch_size * 2
    preds = []
    for s in range(0, len(test_idx), bs):
        out = model(Xi[s:s + bs], Xo[s:s + bs], **fwd)
        if isinstance(out, tuple):
            out = out[0]
        preds.append(out.cpu().numpy())
    pred = np.concatenate(preds)
    yp, pp = rf.decode_pred(pred)
    m, err = rf.compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
    return m, err, yp, pp


def summarize(per_seed):
    return up.summarize_seeds(per_seed, keys=SUM_KEYS)


# ============================================================
# 12b-1：image-only + same augmentation vs U1 augmented fusion
# ============================================================
def run_12b1(states_img, states_u1, data, deg_images, args):
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    print(f"\n{'='*64}\n  12b-1：image-only + same augmentation  vs  U1 augmented fusion\n{'='*64}")
    img_rows, u1_rows = [], []
    for deg in up.EVAL_DEGS:
        dn = deg["name"]
        imgs_eval = deg_images[dn]
        ps_img, ps_u1 = [], []
        for st in states_img:
            m, _, _, _ = eval_image_only(st, imgs_eval, yaw, pitch, test_idx, args)
            ps_img.append(m)
        for st in states_u1:
            m, _, _, _ = eval_fusion_with_preds(st, imgs_eval, ocs_zs, yaw, pitch,
                                                test_idx, args, ocs_dim)
            ps_u1.append(m)
        ri = summarize(ps_img); ri["degradation"] = dn; ri["model"] = "image_only_aug"
        ru = summarize(ps_u1); ru["degradation"] = dn; ru["model"] = "U1_aug_fusion"
        img_rows.append(ri); u1_rows.append(ru)
        print(f"    [{dn:>12}] image_only_aug={ri['angular_err_mean_mean']:.2f}"
              f"±{ri['angular_err_mean_std']:.2f}° (Hit5={ri['hit@5deg_mean']:.1%}) | "
              f"U1_fusion={ru['angular_err_mean_mean']:.2f}"
              f"±{ru['angular_err_mean_std']:.2f}° (Hit5={ru['hit@5deg_mean']:.1%})",
              flush=True)
    return img_rows, u1_rows


# ============================================================
# 12b-2：U1 augmented fusion 分支遮蔽
# ============================================================
def run_12b2(states_u1, data, deg_images, args):
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = up._device()
    print(f"\n{'='*64}\n  12b-2：U1 augmented fusion 分支遮蔽\n{'='*64}")
    modes = ["normal", "image_zero", "image_train_mean",
             "ocs_zero", "ocs_train_mean", "both_train_mean"]
    rows = []
    # 预计算每个 seed 的 train-mean 特征（clean 输入）
    feat_means = []
    for st in states_u1:
        model = up.RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
        model.load_state_dict(st)
        fi_m, fo_m = up.compute_feature_means(model, images, ocs_zs, tr_idx, args)
        feat_means.append((fi_m, fo_m))

    for deg in up.EVAL_DEGS:
        dn = deg["name"]
        imgs_eval = deg_images[dn]
        for mode in modes:
            ps = []
            for st, (fi_m, fo_m) in zip(states_u1, feat_means):
                kw = {}
                if mode == "image_zero":
                    kw = dict(drop_image=True)
                elif mode == "image_train_mean":
                    kw = dict(drop_image=True, img_mean=fi_m)
                elif mode == "ocs_zero":
                    kw = dict(drop_ocs=True)
                elif mode == "ocs_train_mean":
                    kw = dict(drop_ocs=True, ocs_mean=fo_m)
                elif mode == "both_train_mean":
                    kw = dict(drop_image=True, drop_ocs=True, img_mean=fi_m, ocs_mean=fo_m)
                m, _, _, _ = eval_fusion_with_preds(
                    st, imgs_eval, ocs_zs, yaw, pitch, test_idx, args, ocs_dim, **kw)
                ps.append(m)
            s = summarize(ps); s["degradation"] = dn; s["mask_mode"] = mode
            rows.append(s)
            print(f"    [{dn:>12}] {mode:>16}: "
                  f"mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
                  f"Hit5={s['hit@5deg_mean']:.1%}", flush=True)
    return rows


# ============================================================
# 12b-3：U1 的 OCS 噪声 × 图像退化双扰动
# ============================================================
def run_12b3(states_u1, data, aligned_raw, log_mu, log_sd, deg_images, args):
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    print(f"\n{'='*64}\n  12b-3：U1 OCS 噪声 × 图像退化（standardized via train stats，raw-feature perturbation）\n{'='*64}")
    rows = []
    # OCS 噪声=0 基线（每个图像档），便于判读 ΔOCS-noise 效应
    for img_deg, levels in OCS_NOISE_MATRIX:
        imgs_eval = deg_images[img_deg]
        # baseline: clean OCS
        ps0 = []
        for st in states_u1:
            m, _, _, _ = eval_fusion_with_preds(st, imgs_eval, ocs_zs, yaw, pitch,
                                                test_idx, args, ocs_dim)
            ps0.append(m)
        s0 = summarize(ps0); s0["image_deg"] = img_deg; s0["ocs_noise"] = 0.0
        rows.append(s0)
        print(f"    [{img_deg:>12}] ocs_noise=0.00: "
              f"mean={s0['angular_err_mean_mean']:.2f}° Hit5={s0['hit@5deg_mean']:.1%}", flush=True)
        for lv in levels:
            ps = []
            for si, st in enumerate(states_u1):
                # OCS 噪声种子随 seed+level 决定，保证可复现且各 seed 独立
                ocs_zs_noisy = make_ocs_noisy_zs(
                    aligned_raw, log_mu, log_sd, lv,
                    seed=20000 + int(lv * 1000) + si)
                m, _, _, _ = eval_fusion_with_preds(
                    st, imgs_eval, ocs_zs_noisy, yaw, pitch, test_idx, args, ocs_dim)
                ps.append(m)
            s = summarize(ps); s["image_deg"] = img_deg; s["ocs_noise"] = lv
            rows.append(s)
            print(f"    [{img_deg:>12}] ocs_noise={lv:.2f}: "
                  f"mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
                  f"Hit5={s['hit@5deg_mean']:.1%}", flush=True)
    return rows


# ============================================================
# 12b-4：U1 大离群样本审计
# ============================================================
def run_12b4(states_u1, data, deg_images, args):
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    print(f"\n{'='*64}\n  12b-4：U1 大离群样本审计（>30/60/90°）\n{'='*64}")
    audit = []  # 每条 = 一个 (seed, sample, deg) 的离群记录（error>30°）
    # 先收集所有 (seed,deg) 的逐样本 err / pred，统计跨退化重复离群
    per_sample_err = {}  # key=(seed, global_idx) -> {deg: err}
    for deg in up.EVAL_DEGS:
        dn = deg["name"]
        imgs_eval = deg_images[dn]
        for seed, st in zip(SEEDS, states_u1):
            m, err, yp, pp = eval_fusion_with_preds(
                st, imgs_eval, ocs_zs, yaw, pitch, test_idx, args, ocs_dim)
            for i, gidx in enumerate(test_idx):
                per_sample_err.setdefault((seed, int(gidx)), {})[dn] = float(err[i])
                if err[i] > 30.0:
                    audit.append({
                        "seed": seed, "sample_index": int(gidx),
                        "yaw_true": float(yaw[gidx]), "pitch_true": float(pitch[gidx]),
                        "degradation": dn, "error_deg": float(err[i]),
                        "pred_yaw": float(yp[i]), "pred_pitch": float(pp[i]),
                    })
    # 标记跨退化重复离群（同 seed 同样本在 >=2 个退化档 err>30）
    repeat_keys = set()
    for k, dd in per_sample_err.items():
        if sum(1 for v in dd.values() if v > 30.0) >= 2:
            repeat_keys.add(k)
    for r in audit:
        r["is_repeated_outlier_across_degs"] = (r["seed"], r["sample_index"]) in repeat_keys

    # 阈值统计（占比基于 seed×deg×test 总评估数）
    n_eval = len(SEEDS) * len(up.EVAL_DEGS) * len(test_idx)
    thr_stats = {}
    for thr in (30.0, 60.0, 90.0):
        cnt = sum(1 for dd in per_sample_err.values() for v in dd.values() if v > thr)
        thr_stats[f"gt_{int(thr)}"] = {"count": cnt, "frac": cnt / max(n_eval, 1)}
    # 离群姿态分布（pitch 极区 / yaw 边界）
    if audit:
        pit = np.array([r["pitch_true"] for r in audit])
        yw = np.array([r["yaw_true"] for r in audit])
        pose_dist = {
            "pitch_abs_gt_60_frac": float(np.mean(np.abs(pit) > 60)),
            "pitch_abs_gt_75_frac": float(np.mean(np.abs(pit) > 75)),
            "yaw_near_0_or_360_frac": float(np.mean((yw < 10) | (yw > 350))),
            "pitch_min": float(pit.min()), "pitch_max": float(pit.max()),
        }
        per_seed_cnt = {int(s): int(sum(1 for r in audit if r["seed"] == s)) for s in SEEDS}
    else:
        pose_dist = {}
        per_seed_cnt = {int(s): 0 for s in SEEDS}
    summary = {"n_eval_total": n_eval, "thresholds": thr_stats,
               "n_outlier_gt30_records": len(audit),
               "n_unique_repeated_outliers": len(repeat_keys),
               "pose_distribution": pose_dist, "per_seed_outlier_count": per_seed_cnt}
    print(f"    >30°: {thr_stats['gt_30']['count']} ({thr_stats['gt_30']['frac']:.2%})  "
          f">60°: {thr_stats['gt_60']['count']} ({thr_stats['gt_60']['frac']:.2%})  "
          f">90°: {thr_stats['gt_90']['count']} ({thr_stats['gt_90']['frac']:.2%})")
    print(f"    跨退化重复离群(同seed同样本>=2档): {len(repeat_keys)}")
    print(f"    离群 per-seed: {per_seed_cnt}")
    if pose_dist:
        print(f"    离群姿态: |pitch|>60° {pose_dist['pitch_abs_gt_60_frac']:.1%}, "
              f"|pitch|>75° {pose_dist['pitch_abs_gt_75_frac']:.1%}, "
              f"yaw 近 0/360° {pose_dist['yaw_near_0_or_360_frac']:.1%}")
    return audit, summary


# ============================================================
# 12b-5：未见退化泛化
# ============================================================
def run_12b5(states_u1, states_img, data, args):
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    print(f"\n{'='*64}\n  12b-5：未见退化泛化（U1 fusion + image-only-aug 对照）\n{'='*64}")
    rows = []
    for deg in HELDOUT_DEGS:
        dn = deg["name"]
        imgs_eval = up.apply_image_degradation(images, deg)
        ps_u1, ps_img = [], []
        for st in states_u1:
            m, _, _, _ = eval_fusion_with_preds(st, imgs_eval, ocs_zs, yaw, pitch,
                                                test_idx, args, ocs_dim)
            ps_u1.append(m)
        for st in states_img:
            m, _, _, _ = eval_image_only(st, imgs_eval, yaw, pitch, test_idx, args)
            ps_img.append(m)
        su = summarize(ps_u1); su["degradation"] = dn; su["model"] = "U1_aug_fusion"
        si = summarize(ps_img); si["degradation"] = dn; si["model"] = "image_only_aug"
        rows.append(su); rows.append(si)
        print(f"    [{dn:>14}] U1_fusion={su['angular_err_mean_mean']:.2f}"
              f"±{su['angular_err_mean_std']:.2f}° (Hit5={su['hit@5deg_mean']:.1%}) | "
              f"image_only_aug={si['angular_err_mean_mean']:.2f}"
              f"±{si['angular_err_mean_std']:.2f}° (Hit5={si['hit@5deg_mean']:.1%})",
              flush=True)
        del imgs_eval
    return rows


# ============================================================
# 保存
# ============================================================
def _save_csv(path, rows, keys):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


_METRIC_COLS = ["angular_err_mean_mean", "angular_err_mean_std",
                "angular_err_median_mean", "angular_err_p90_mean",
                "angular_err_p95_mean", "angular_err_worst_mean",
                "hit@5deg_mean", "hit@10deg_mean"]


def save_all(out_dir, b1_img, b1_u1, b2, b3, b4_audit, b4_sum, b5):
    # 12b-1
    _save_csv(os.path.join(out_dir, "image_only_aug_results.csv"),
              b1_img + b1_u1, ["model", "degradation"] + _METRIC_COLS)
    _save_json(os.path.join(out_dir, "image_only_aug_results.json"),
               {"image_only_aug": b1_img, "U1_aug_fusion": b1_u1})
    # 12b-2
    _save_csv(os.path.join(out_dir, "u1_branch_mask_results.csv"),
              b2, ["degradation", "mask_mode"] + _METRIC_COLS)
    _save_json(os.path.join(out_dir, "u1_branch_mask_results.json"), b2)
    # 12b-3
    _save_csv(os.path.join(out_dir, "u1_ocs_noise_both_degraded_results.csv"),
              b3, ["image_deg", "ocs_noise"] + _METRIC_COLS)
    _save_json(os.path.join(out_dir, "u1_ocs_noise_both_degraded_results.json"), b3)
    # 12b-4
    _save_csv(os.path.join(out_dir, "u1_outlier_audit.csv"), b4_audit,
              ["seed", "sample_index", "yaw_true", "pitch_true", "degradation",
               "error_deg", "pred_yaw", "pred_pitch", "is_repeated_outlier_across_degs"])
    _save_json(os.path.join(out_dir, "u1_outlier_audit.json"),
               {"summary": b4_sum, "records": b4_audit})
    # 12b-5
    _save_csv(os.path.join(out_dir, "heldout_degradation_results.csv"),
              b5, ["model", "degradation"] + _METRIC_COLS)
    _save_json(os.path.join(out_dir, "heldout_degradation_results.json"), b5)


def _row(rows, **cond):
    for r in rows:
        if all(r.get(k) == v for k, v in cond.items()):
            return r
    return None


def _fmt(r):
    return ("—" if r is None
            else f"{r['angular_err_mean_mean']:.2f}° ({r['hit@5deg_mean']:.0%})")


def write_mechanism_summary(out_dir, b1_img, b1_u1, b2, b3, b4_sum, b5):
    L = []
    L.append("# 实验12b：融合 fallback 因果隔离 — 机制总结\n")
    L.append(f"> 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    L.append(f"> Split 10°→5°，{len(SEEDS)} seeds；OCS=concat5 per_part_log 30D；"
             "image=phase63 exact BRDF log1p 128×128。  ")
    L.append("> 参照：OCS-only 5.91°；naive fusion noise σ=0.01=73.36°；"
             "image-only clean-trained noise σ=0.01=85.85°。\n")

    # Table 12b-1
    L.append("## Table 12b-1：image-only + same augmentation vs U1 augmented fusion\n")
    L.append("| 退化 | image-only+aug | U1 aug fusion | image-only clean(参照) | naive fusion(参照) | OCS-only(参照) |")
    L.append("|---|---|---|---|---|---|")
    for deg in up.EVAL_DEGS:
        dn = deg["name"]
        L.append(f"| {dn} | {_fmt(_row(b1_img, degradation=dn))} | "
                 f"{_fmt(_row(b1_u1, degradation=dn))} | "
                 f"{REF['image_only_clean'].get(dn, '—')}° | "
                 f"{REF['naive_fusion'].get(dn, '—')}° | {REF['ocs_only_mean']}° |")
    L.append("\n> 单元格=mean (Hit@5°)。判读：若 image-only+aug ≈ U1，则 U1 主要由图像增强解释；"
             "若 U1 在噪声/未见退化下持续更优，则 OCS 可能提供补充。\n")

    # Table 12b-2
    L.append("## Table 12b-2：U1 分支遮蔽矩阵\n")
    L.append("| 退化 | normal | image_zero | image_train_mean | ocs_zero | ocs_train_mean | both_train_mean |")
    L.append("|---|---|---|---|---|---|---|")
    for deg in up.EVAL_DEGS:
        dn = deg["name"]
        cells = [_fmt(_row(b2, degradation=dn, mask_mode=mm)) for mm in
                 ["normal", "image_zero", "image_train_mean",
                  "ocs_zero", "ocs_train_mean", "both_train_mean"]]
        L.append(f"| {dn} | " + " | ".join(cells) + " |")
    L.append("\n> 判读：图像退化下遮蔽 OCS 明显变差→OCS 分支活跃；"
             "图像退化下遮蔽图像后接近 5.91°→强 OCS fallback；遮蔽 OCS 几乎无影响→仍依赖图像。\n")

    # Table 12b-3
    L.append("## Table 12b-3：U1 OCS 噪声 × 图像退化矩阵\n")
    L.append("| 图像退化 \\ OCS 噪声 | 0% | 1% | 5% | 10% | 20% |")
    L.append("|---|---|---|---|---|---|")
    for img_deg, _levels in OCS_NOISE_MATRIX:
        cells = []
        for lv in [0.0, 0.01, 0.05, 0.10, 0.20]:
            cells.append(_fmt(_row(b3, image_deg=img_deg, ocs_noise=lv)))
        L.append(f"| {img_deg} | " + " | ".join(cells) + " |")
    L.append("\n> OCS 噪声=raw-feature relative perturbation 后用 train 统计标准化（非实验6 端到端口径）。"
             "判读：OCS 噪声越大、图像退化下 U1 越差→OCS 参与恢复；几乎无影响→主要靠图像增强。\n")

    # Table 12b-4
    L.append("## Table 12b-4：U1 离群样本审计\n")
    ts = b4_sum["thresholds"]
    L.append(f"- 评估总数（seed×deg×test）= {b4_sum['n_eval_total']}")
    L.append(f"- error>30°: {ts['gt_30']['count']} ({ts['gt_30']['frac']:.2%})；"
             f">60°: {ts['gt_60']['count']} ({ts['gt_60']['frac']:.2%})；"
             f">90°: {ts['gt_90']['count']} ({ts['gt_90']['frac']:.2%})")
    L.append(f"- 跨退化重复离群（同 seed 同样本 ≥2 档 >30°）: {b4_sum['n_unique_repeated_outliers']}")
    L.append(f"- per-seed 离群计数: {b4_sum['per_seed_outlier_count']}")
    if b4_sum.get("pose_distribution"):
        pd = b4_sum["pose_distribution"]
        L.append(f"- 离群姿态分布: |pitch|>60° {pd['pitch_abs_gt_60_frac']:.1%}, "
                 f"|pitch|>75° {pd['pitch_abs_gt_75_frac']:.1%}, "
                 f"yaw 近 0/360° {pd['yaw_near_0_or_360_frac']:.1%}")
    L.append("\n> 写作边界：worst 仍极大时不能写 fully robust，只能写 mean/p90/Hit@5 stabilized, rare large outliers remain。\n")

    # Table 12b-5
    L.append("## Table 12b-5：未见退化泛化\n")
    L.append("| 未见退化 | U1 aug fusion | image-only+aug |")
    L.append("|---|---|---|")
    for deg in HELDOUT_DEGS:
        dn = deg["name"]
        L.append(f"| {dn} | {_fmt(_row(b5, degradation=dn, model='U1_aug_fusion'))} | "
                 f"{_fmt(_row(b5, degradation=dn, model='image_only_aug'))} |")
    L.append("\n> 判读：仅训练见过退化稳定=matched augmentation；未见 noise/blur/downsample 也稳定=更广 degradation-aware robustness。\n")

    # 机制判读总表
    L.append("## Table 12b-final：机制判读（是否支持 OCS fallback）\n")
    L.append(_judge(b1_img, b1_u1, b2, b3))

    with open(os.path.join(out_dir, "mechanism_12b_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("\n  mechanism_12b_summary.md 已写入")


def _judge(b1_img, b1_u1, b2, b3):
    """基于数据给出审慎机制判读（不预设结论）。"""
    lines = []
    # 判据1：image-only+aug vs U1（噪声档）
    out = []
    for dn in ["noise_0.01", "noise_0.10"]:
        ri = _row(b1_img, degradation=dn); ru = _row(b1_u1, degradation=dn)
        if ri and ru:
            gap = ri["angular_err_mean_mean"] - ru["angular_err_mean_mean"]
            out.append(f"{dn}: image-only+aug={ri['angular_err_mean_mean']:.2f}°, "
                       f"U1={ru['angular_err_mean_mean']:.2f}°, Δ(img-U1)={gap:+.2f}°")
    lines.append("**判据1（U1 是否优于 image-only+aug）**：" + "；".join(out))
    # 判据2：噪声下遮蔽 OCS 是否变差
    out = []
    for dn in ["noise_0.01", "noise_0.10"]:
        rn = _row(b2, degradation=dn, mask_mode="normal")
        ro = _row(b2, degradation=dn, mask_mode="ocs_train_mean")
        ri = _row(b2, degradation=dn, mask_mode="image_train_mean")
        if rn and ro and ri:
            out.append(f"{dn}: normal={rn['angular_err_mean_mean']:.2f}°, "
                       f"ocs_masked={ro['angular_err_mean_mean']:.2f}°, "
                       f"image_masked={ri['angular_err_mean_mean']:.2f}°")
    lines.append("**判据2（U1 噪声下遮蔽分支）**：" + "；".join(out))
    # 判据3：OCS 噪声效应（噪声图像档）
    out = []
    for dn in ["noise_0.01", "noise_0.10"]:
        r0 = _row(b3, image_deg=dn, ocs_noise=0.0)
        r20 = _row(b3, image_deg=dn, ocs_noise=0.20)
        if r0 and r20:
            d = r20["angular_err_mean_mean"] - r0["angular_err_mean_mean"]
            out.append(f"{dn}: ocs0%={r0['angular_err_mean_mean']:.2f}°→"
                       f"ocs20%={r20['angular_err_mean_mean']:.2f}° (Δ={d:+.2f}°)")
    lines.append("**判据3（OCS 噪声对 U1 的影响）**：" + "；".join(out))
    lines.append("\n> 综合判读由 Claude/Codex 结合上述判据与红线撰写，本自动判据仅汇总关键数值。")
    return "\n".join(lines)


# ============================================================
def main():
    import glob
    ap = argparse.ArgumentParser(description="Exp12b: fusion fallback causal isolation")
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
    up.SEEDS = SEEDS  # 与实验12 主脚本对齐（train_model 内部不依赖，但保持一致）

    if args.manifest is None:
        cands = sorted(glob.glob(_MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No manifest: {_MANIFEST_GLOB}")
        args.manifest = cands[0]

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    log_f = open(os.path.join(out_dir, "run.log"), "w", encoding="utf-8", buffering=1)

    class Tee:
        def __init__(self, *s): self.s = s
        def write(self, x):
            for st in self.s:
                try: st.write(x); st.flush()
                except Exception: pass
        def flush(self):
            for st in self.s:
                try: st.flush()
                except Exception: pass

    sys.stdout = Tee(sys.__stdout__, log_f)
    sys.stderr = Tee(sys.__stderr__, log_f)

    print("=" * 70)
    print("  实验12b：融合 fallback 因果隔离与鲁棒性补强")
    print(f"  Image dir: {args.image_dir}")
    print(f"  Manifest:  {args.manifest}")
    print(f"  Output:    {out_dir}")
    print(f"  Seeds: {SEEDS}  epochs={args.epochs} patience={args.patience}")
    print(f"  Device: {up._device()}")
    print("=" * 70)

    t_all = time.time()
    print("\n  [准备数据]")
    data, aligned_raw, log_mu, log_sd = prepare_data_ext(args)
    images = data[0]

    # 训练：image-only + aug 与 U1 augmented fusion（各 5 seed）
    print(f"\n{'='*64}\n  训练 image-only + same augmentation（{len(SEEDS)} seeds）\n{'='*64}")
    t0 = time.time()
    states_img = []
    for seed in SEEDS:
        st, ep, bva = train_image_only(data, args, seed, augment=True)
        states_img.append(st)
        print(f"    [image-only-aug] seed={seed} done (ep={ep}, best_va={bva:.6f})", flush=True)
    print(f"  image-only-aug 训练耗时 {time.time()-t0:.0f}s")

    print(f"\n{'='*64}\n  训练 U1 augmented fusion（{len(SEEDS)} seeds）\n{'='*64}")
    t0 = time.time()
    states_u1 = []
    ocs_dim = data[-1]
    for seed in SEEDS:
        st, ep, bva = up.train_model(
            lambda: up.RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout,
                                         p_drop_image=0.0, p_drop_ocs=0.0),
            data, args, augment=True, anchored=False, seed=seed)
        states_u1.append(st)
        print(f"    [U1-aug-fusion] seed={seed} done (ep={ep}, best_va={bva:.6f})", flush=True)
    print(f"  U1-aug-fusion 训练耗时 {time.time()-t0:.0f}s")

    # 预计算 EVAL_DEGS 退化图像（多组复用）
    deg_images = {d["name"]: up.apply_image_degradation(images, d) for d in up.EVAL_DEGS}

    # 五组实验
    b1_img, b1_u1 = run_12b1(states_img, states_u1, data, deg_images, args)
    b2 = run_12b2(states_u1, data, deg_images, args)
    b3 = run_12b3(states_u1, data, aligned_raw, log_mu, log_sd, deg_images, args)
    b4_audit, b4_sum = run_12b4(states_u1, data, deg_images, args)
    b5 = run_12b5(states_u1, states_img, data, args)

    # 保存
    save_all(out_dir, b1_img, b1_u1, b2, b3, b4_audit, b4_sum, b5)
    write_mechanism_summary(out_dir, b1_img, b1_u1, b2, b3, b4_sum, b5)

    _save_json(os.path.join(out_dir, "summary.json"), {
        "config": vars(args), "seeds": SEEDS, "references": REF,
        "heldout_degs": [d["name"] for d in HELDOUT_DEGS],
        "ocs_noise_method": "raw per_part feature relative perturbation "
                            "(raw + level*|raw|*N(0,1)), re-standardized with train log-zscore stats",
        "elapsed_sec": time.time() - t_all,
    })

    print(f"\n  全部完成，总耗时 {time.time()-t_all:.0f}s")
    print(f"  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

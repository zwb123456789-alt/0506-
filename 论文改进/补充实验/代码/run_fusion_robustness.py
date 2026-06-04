"""
run_fusion_robustness.py — ResNet-fusion 图像退化鲁棒性测试 (实验 11)
=====================================================================
目的：填补论文承重墙。已有证据：
  - 实验9: ResNet image-only 在图像退化下崩溃 (1% 噪声 → 85.85°)
  - 实验6: OCS-only MLP 不受图像退化影响 (干净 5.91°，平线)
  - 缺口: ResNet-FUSION 在图像退化下，是被拖垮(≈image-only) 还是被 OCS 托住(≈OCS-only)？

本实验回答：当图像退化时，融合能否靠干净 OCS 分支保持鲁棒。
若 fusion 退化误差 ≈ OCS-only 而非 ≈ image-only，则直接证明
"融合在图像失效时回退到 OCS 模态"，与实验6(OCS退化时图像托住)对称。

方法（与实验8/9 严格对齐，保证可比）：
  - 模型: ResNetFusionModel (ResNet-18 图像分支 + OCS 分支 + fusion head)，复用 run_resnet_fusion.py
  - OCS: concat5 per_part_log 30D（对齐图像顺序），与 A2 同款，OCS 始终干净
  - 退化算子: 复用 run_resnet_robustness.py 的 noise/brightness 函数，仅施加于图像
  - 训练: 干净图像+干净OCS 训练一次(5 seeds)，所有退化档共享同一组模型（train-clean/test-degraded 范式）
  - 退化档: noise σ∈{0,0.01,0.03,0.05,0.10} + brightness{0.5,0.75,1.25,1.5}，与实验9 完全一致
  - Split: 10°→5°, 5 seeds, log1p 128×128
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

warnings.filterwarnings("ignore", category=UserWarning)

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic

# 复用已验证的两个脚本的类与函数
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
                         "resnet_fusion_robustness")

SEEDS = [0, 1, 2, 3, 4]

# 退化档（与实验9 一致，仅 P0：噪声+亮度）
DEGRADATIONS = [
    {"name": "clean", "type": "none"},
    {"name": "noise_0.01", "type": "noise", "sigma": 0.01},
    {"name": "noise_0.03", "type": "noise", "sigma": 0.03},
    {"name": "noise_0.05", "type": "noise", "sigma": 0.05},
    {"name": "noise_0.10", "type": "noise", "sigma": 0.10},
    {"name": "bright_0.50", "type": "brightness", "scale": 0.50},
    {"name": "bright_0.75", "type": "brightness", "scale": 0.75},
    {"name": "bright_1.25", "type": "brightness", "scale": 1.25},
    {"name": "bright_1.50", "type": "brightness", "scale": 1.50},
]


def train_fusion_clean(images_clean, ocs_zs, yaw, pitch, split, args):
    """在干净图像+干净OCS上训练 ResNetFusionModel，返回 5 seeds 的 best_state 列表。"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    tr_idx, val_idx = rf.make_train_val_idx(split["train_idx"])

    Xi_tr = torch.FloatTensor(images_clean[tr_idx]).to(device)
    Xo_tr = torch.FloatTensor(ocs_zs[tr_idx]).to(device)
    y_tr = torch.FloatTensor(rf.encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    Xi_va = torch.FloatTensor(images_clean[val_idx]).to(device)
    Xo_va = torch.FloatTensor(ocs_zs[val_idx]).to(device)
    y_va = torch.FloatTensor(rf.encode_target(yaw[val_idx], pitch[val_idx])).to(device)

    models = []
    for seed in SEEDS:
        torch.manual_seed(seed); np.random.seed(seed)
        model = rf.ResNetFusionModel(ocs_dim=ocs_zs.shape[1], dropout=args.dropout).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
        crit = nn.MSELoss()
        tr_loader = DataLoader(TensorDataset(Xi_tr, Xo_tr, y_tr),
                               batch_size=args.batch_size, shuffle=True)
        va_loader = DataLoader(TensorDataset(Xi_va, Xo_va, y_va), batch_size=args.batch_size * 2)
        best_va, best_state, wait, ep = float("inf"), None, 0, 0
        for ep in range(1, args.epochs + 1):
            rf.train_epoch(model, tr_loader, opt, crit, device)
            va, _ = rf.evaluate(model, va_loader, crit, device)
            if va < best_va - 1e-8:
                best_va = va
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


def eval_fusion_degraded(models, images_degraded, ocs_zs, yaw, pitch, test_idx, ocs_dim, args):
    """用已训练 fusion 模型在退化图像(OCS干净)上评估，返回 5 seeds 指标。"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    Xi_te = torch.FloatTensor(images_degraded[test_idx]).to(device)
    Xo_te = torch.FloatTensor(ocs_zs[test_idx]).to(device)
    y_te = torch.FloatTensor(rf.encode_target(yaw[test_idx], pitch[test_idx])).to(device)
    te_loader = DataLoader(TensorDataset(Xi_te, Xo_te, y_te), batch_size=args.batch_size * 2)
    crit = nn.MSELoss()

    per_seed = []
    for seed, state in zip(SEEDS, models):
        model = rf.ResNetFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
        model.load_state_dict(state)
        _, te_pred = rf.evaluate(model, te_loader, crit, device)
        yp, pp = rf.decode_pred(te_pred)
        m, _ = rf.compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
        m["seed"] = seed
        per_seed.append(m)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
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


# 实验9 ResNet image-only 退化参照（canonical run_20260601_143957，已确认入进度文档）
# OCS-only MLP per_part_log 干净基线 5.91°（不受图像退化影响，平线参照）
_EXP9_RUN = "run_20260601_143957"
_OCS_ONLY_MEAN = 5.91
_OCS_ONLY_HIT5 = 0.738


def load_image_only_reference():
    """读取实验9 ResNet image-only 退化曲线作参照行；找不到则回退已确认硬编码值。"""
    csv_path = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                            "resnet_robustness", _EXP9_RUN, "robustness_results.csv")
    ref = {}
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                ref[r["degradation"]] = {
                    "mean": float(r["angular_err_mean_mean"]),
                    "std": float(r["angular_err_mean_std"]),
                    "hit5": float(r["hit@5deg_mean"]),
                }
    if not ref:  # 回退：进度文档已确认值
        ref = {
            "clean": {"mean": 1.69, "std": 0.07, "hit5": 0.976},
            "noise_0.01": {"mean": 85.85, "std": 3.00, "hit5": 0.022},
            "noise_0.03": {"mean": 85.49, "std": 4.59, "hit5": 0.015},
            "noise_0.05": {"mean": 85.97, "std": 4.48, "hit5": 0.012},
            "noise_0.10": {"mean": 87.92, "std": 2.36, "hit5": 0.010},
            "bright_0.50": {"mean": 3.45, "std": 0.27, "hit5": 0.787},
            "bright_0.75": {"mean": 2.03, "std": 0.13, "hit5": 0.948},
            "bright_1.25": {"mean": 1.77, "std": 0.05, "hit5": 0.975},
            "bright_1.50": {"mean": 2.00, "std": 0.03, "hit5": 0.958},
        }
    return ref


def save_results(out_dir, results, args, img_ref):
    """保存 json/csv/md。md 含 fusion + image-only(实验9) + OCS-only 三线对照。"""
    with open(os.path.join(out_dir, "fusion_robustness_results.json"), "w",
              encoding="utf-8") as f:
        json.dump({"results": results, "image_only_ref": img_ref,
                   "ocs_only_ref": {"mean": _OCS_ONLY_MEAN, "hit5": _OCS_ONLY_HIT5},
                   "config": vars(args), "seeds": SEEDS}, f, indent=2, ensure_ascii=False)

    with open(os.path.join(out_dir, "fusion_robustness_results.csv"), "w",
              encoding="utf-8", newline="") as f:
        keys = ["degradation", "type", "angular_err_mean_mean", "angular_err_mean_std",
                "angular_err_p90_mean", "angular_err_worst_mean",
                "hit@5deg_mean", "hit@10deg_mean"]
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in results:
            w.writerow(r)

    lines = ["# 实验11：ResNet-fusion 图像退化鲁棒性", "",
             "> 范式：train-clean / test-degraded。训练用干净图+干净OCS（5 seeds 共享），",
             "> 测试时**仅图像退化，OCS 始终干净**。Split 10°→5°，log1p 128×128。",
             "> OCS 特征：concat5 per_part_log 30D（与 A2 同款）。", "",
             "## 三线对照（同一退化档）", "",
             "| 退化 | **Fusion** mean±std | Fusion Hit@5° | image-only (实验9) | OCS-only (5.91°平线) |",
             "|---|---|---:|---|---|"]
    for r in results:
        deg = r["degradation"]
        ir = img_ref.get(deg)
        ir_str = f"{ir['mean']:.2f}±{ir['std']:.2f}° (Hit5={ir['hit5']:.1%})" if ir else "—"
        lines.append(
            f"| {deg} | {r['angular_err_mean_mean']:.2f}±{r['angular_err_mean_std']:.2f}° "
            f"| {r['hit@5deg_mean']:.1%} | {ir_str} "
            f"| {_OCS_ONLY_MEAN:.2f}° (Hit5={_OCS_ONLY_HIT5:.1%}) |")
    lines += ["",
              "> OCS-only 列为常数：OCS 分支不受图像退化影响（实验6 已证），列出干净基线供对照。",
              "> 结论判据：若 Fusion 在图像噪声档误差 ≈ OCS-only（5.91°）而非 ≈ image-only（85°），",
              "> 则证明融合在图像失效时回退到 OCS 模态，与实验6 构成对称双向鲁棒性证据。"]
    with open(os.path.join(out_dir, "fusion_robustness_report.md"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n  Report:")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description="ResNet-fusion image degradation robustness (Exp 11)")
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
    ap.add_argument("--p0-only", action="store_true",
                    help="只跑噪声档（去掉亮度档）")
    ap.add_argument("--smoke", action="store_true",
                    help="冒烟测试：1 seed + 少 epoch")
    args = ap.parse_args()

    global SEEDS
    if args.smoke:
        SEEDS = [0]
        args.epochs = 8
        args.patience = 5

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
    print("  实验11：ResNet-fusion 图像退化鲁棒性 (train-clean / test-degraded)")
    print(f"  Image dir: {args.image_dir}")
    print(f"  Manifest:  {args.manifest}")
    print(f"  Output:    {out_dir}")
    print(f"  Seeds: {SEEDS}  epochs={args.epochs} patience={args.patience}")
    print("=" * 70)

    # 1) 加载干净图像
    images_clean, img_yaw, img_pitch = rf.load_images(
        args.image_dir, args.image_size, args.intensity)

    # 2) 加载并对齐 OCS（concat5 per_part_log 30D，与 A2 同款）
    feats, oy, op, labels = rf.load_ocs_features(args.manifest, "per_part", geom_subset=None)
    aligned, ok = rf.align_to_images(feats, oy, op, img_yaw, img_pitch)
    assert ok.all(), f"OCS 对齐缺失 {(~ok).sum()} 个样本"
    print(f"    OCS aligned: {aligned.shape}, geoms={labels}")

    # 3) split + OCS 预处理（log + zscore，仅 fit train）
    split = ic.split_coarse_to_fine(img_yaw, img_pitch, coarse_step=10.0)
    test_idx = split["test_idx"]
    tr_idx, val_idx = rf.make_train_val_idx(split["train_idx"])
    print(f"    Split: train_pool={split['n_train']} (tr={len(tr_idx)} val={len(val_idx)}) "
          f"test={split['n_test']}")
    ocs_zs_tr, ocs_zs_va, ocs_zs_te = rf.prep_ocs(
        aligned, tr_idx, val_idx, test_idx, "log", log_skip=None)
    ocs_zs = np.full_like(aligned, 0.0)
    ocs_zs[tr_idx] = ocs_zs_tr
    ocs_zs[val_idx] = ocs_zs_va
    ocs_zs[test_idx] = ocs_zs_te
    ocs_dim = ocs_zs.shape[1]

    # 4) 干净训练一次（5 seeds 共享，供所有退化档评估）
    print(f"\n  [1/2] Training ResNet-fusion on clean images+OCS ({len(SEEDS)} seeds)...")
    t0 = time.time()
    models = train_fusion_clean(images_clean, ocs_zs, img_yaw, img_pitch, split, args)
    print(f"  Training done in {time.time()-t0:.0f}s")

    # 5) 循环退化档评估（仅图像退化，OCS 干净）
    degs = DEGRADATIONS if not args.p0_only else [
        d for d in DEGRADATIONS if d["type"] in ("none", "noise")]
    print(f"\n  [2/2] Evaluating on {len(degs)} degradation conditions...")
    results = []
    for deg in degs:
        print(f"    {deg['name']}...", end=" ", flush=True)
        imgs_deg = rr.apply_degradation(images_clean, deg)
        per_seed = eval_fusion_degraded(
            models, imgs_deg, ocs_zs, img_yaw, img_pitch, test_idx, ocs_dim, args)
        s = summarize_seeds(per_seed)
        s["degradation"] = deg["name"]
        s["type"] = deg["type"]
        s.update({k: v for k, v in deg.items() if k not in ("name", "type")})
        results.append(s)
        print(f"mean={s['angular_err_mean_mean']:.2f}±{s['angular_err_mean_std']:.2f}° "
              f"Hit5={s['hit@5deg_mean']:.1%}", flush=True)

    # 6) 保存（三线对照）
    img_ref = load_image_only_reference()
    save_results(out_dir, results, args, img_ref)
    print(f"\n  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

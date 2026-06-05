"""
run_observation_style_degradation_12c.py — 实验12c：Observation-style 图像退化压力测试
================================================================================
目的（指导文件 §4）：
  补齐 observation-chain-inspired synthetic degradation stress test。
  这是合成退化压力测试，**不是真实望远镜验证**。

核心要求（指导文件 §4，红线）：
  退化必须在近似线性强度域施加。训练图像存储为 normalized-log1p：
      norm = log1p(10 * raw01) / log1p(10)
  退化算子流程：
      lin   = expm1(norm * log1p(10)) / 10        # 反归一化到线性强度 ∈[0,1]
      lin'  = _apply_degradation_in_linear_domain(lin, cfg)
      lin'  = clip(lin', 0, None)
      norm' = log1p(10 * lin') / log1p(10)         # 回到训练 normalized-log1p
  禁止直接复用 run_resnet_robustness.py 的 log1p 域退化作为 observation-style 物理解释。

实现的退化算子（指导 §4 至少 7 项）：
  1. PSF / defocus blur（线性域高斯模糊）
  2. photon noise:   lin' = Poisson(lin * gain) / gain
  3. read noise:     lin' = lin + N(0, sigma_read)
  4. background:     lin' = lin + bg_level（+ 可选 sparse star-like 亮点污染）
  5. clipping/saturation: lin' = min(lin, sat_level)
  6. downsample / low-resolution
  7. mild / medium / severe combined degradation

参数均相对 train split 线性强度统计（max(lin_train)）定义，输出 degradation_config 表。

最低模型（指导 §4）：
  - ResNet image-only clean-trained
  - image-only same augmentation（与 U1 同款 AUG_DEGS）
  - U1 simple-degradation-aware fusion（AUG_DEGS）
  - OCS-only MLP per_part_log 30D（退化无关，平线参照）
  - 资源允许（--with-obs-aug）：image-only obs-aug + U2 fusion obs-aug

不变口径：split 10°→5°；target [sin,cos,sin,cos]；great-circle err；
          OCS=concat5 per_part_log 30D 始终 clean；seeds 0-4。

红线：不写 real telescope / operational robustness / fully robust / near-perfect /
      fusion automatically robust / OCS standalone fallback。
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
from PIL import Image, ImageFilter

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic
import run_resnet_fusion as rf
import run_fusion_mechanism_upgrade as up
import run_late_fusion_beta_sweep_12f as lf  # 复用 OCSMLP / train_ocs_mlp / ocs_pred4d

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                         "observation_style_degradation_12c")
SEEDS = [0, 1, 2, 3, 4]
_LOG10_DEN = np.log1p(10.0)
SUM_KEYS = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "angular_err_worst", "hit@5deg", "hit@10deg"]


# ============================================================
# 线性域转换
# ============================================================
def to_linear(norm_img):
    return np.expm1(np.clip(norm_img, 0.0, 1.0) * _LOG10_DEN) / 10.0


def to_norm(lin_img):
    return (np.log1p(10.0 * np.clip(lin_img, 0.0, None)) / _LOG10_DEN).astype(np.float32)


# ============================================================
# 线性域退化算子
# ============================================================
def _blur_linear(lin, sigma_px):
    """线性域高斯模糊（PIL，逐图）。lin: (N,1,H,W) ∈[0, lmax]。"""
    out = np.zeros_like(lin)
    lmax = max(lin.max(), 1e-6)
    for i in range(lin.shape[0]):
        a = (lin[i, 0] / lmax * 255.0).clip(0, 255).astype(np.uint8)
        pil = Image.fromarray(a).filter(ImageFilter.GaussianBlur(radius=sigma_px))
        out[i, 0] = np.asarray(pil, dtype=np.float32) / 255.0 * lmax
    return out


def _photon_noise(lin, gain, rng):
    """lin' = Poisson(lin*gain)/gain。gain 大=光子多=噪声小。"""
    lam = np.clip(lin * gain, 0.0, None)
    return (rng.poisson(lam).astype(np.float32)) / gain


def _read_noise(lin, sigma_read, rng):
    return lin + rng.normal(0.0, sigma_read, size=lin.shape).astype(np.float32)


def _background(lin, bg_level, rng, star_density=0.0, star_level=0.0):
    out = lin + bg_level
    if star_density > 0:
        mask = rng.random(lin.shape) < star_density
        out = out + mask.astype(np.float32) * star_level
    return out


def _saturate(lin, sat_level):
    return np.minimum(lin, sat_level)


def _downsample(lin, size):
    N, C, H, W = lin.shape
    out = np.zeros_like(lin)
    lmax = max(lin.max(), 1e-6)
    for i in range(N):
        a = (lin[i, 0] / lmax * 255.0).clip(0, 255).astype(np.uint8)
        pil = Image.fromarray(a)
        small = pil.resize((size, size), Image.BILINEAR).resize((W, H), Image.BILINEAR)
        out[i, 0] = np.asarray(small, dtype=np.float32) / 255.0 * lmax
    return out


def apply_obs_degradation(images_norm, cfg, stats, seed=12345):
    """在线性强度域施加 observation-style 退化，返回 normalized-log1p 图像。"""
    rng = np.random.RandomState(seed)
    lin = to_linear(images_norm)
    lmax = stats["lin_train_max"]
    for op in cfg["ops"]:
        t = op["type"]
        if t == "blur":
            lin = _blur_linear(lin, op["sigma_px"])
        elif t == "photon":
            lin = _photon_noise(lin, op["gain"], rng)
        elif t == "read":
            lin = _read_noise(lin, op["sigma_frac"] * lmax, rng)
        elif t == "background":
            lin = _background(lin, op["bg_frac"] * lmax, rng,
                              star_density=op.get("star_density", 0.0),
                              star_level=op.get("star_frac", 0.0) * lmax)
        elif t == "saturate":
            lin = _saturate(lin, op["sat_frac"] * lmax)
        elif t == "downsample":
            lin = _downsample(lin, op["size"])
    lin = np.clip(lin, 0.0, None)
    return to_norm(lin)


def build_obs_degs():
    """单算子（medium 档）+ combined mild/medium/severe。参数相对 lin_train_max。"""
    degs = [
        {"name": "clean", "ops": []},
        # 单算子（medium）
        {"name": "blur_sig1.5", "ops": [{"type": "blur", "sigma_px": 1.5}]},
        {"name": "photon_g100", "ops": [{"type": "photon", "gain": 100.0}]},
        {"name": "read_0.005", "ops": [{"type": "read", "sigma_frac": 0.005}]},
        {"name": "background_0.005", "ops": [{"type": "background", "bg_frac": 0.005}]},
        {"name": "starfield", "ops": [{"type": "background", "bg_frac": 0.002,
                                       "star_density": 0.003, "star_frac": 0.6}]},
        {"name": "saturate_0.8", "ops": [{"type": "saturate", "sat_frac": 0.8}]},
        {"name": "downsample_64", "ops": [{"type": "downsample", "size": 64}]},
        # combined
        {"name": "combined_mild", "ops": [
            {"type": "blur", "sigma_px": 0.5},
            {"type": "photon", "gain": 1000.0},
            {"type": "read", "sigma_frac": 0.001},
            {"type": "background", "bg_frac": 0.001},
        ]},
        {"name": "combined_medium", "ops": [
            {"type": "blur", "sigma_px": 1.0},
            {"type": "photon", "gain": 100.0},
            {"type": "read", "sigma_frac": 0.005},
            {"type": "background", "bg_frac": 0.005},
            {"type": "saturate", "sat_frac": 0.9},
        ]},
        {"name": "combined_severe", "ops": [
            {"type": "blur", "sigma_px": 2.0},
            {"type": "photon", "gain": 10.0},
            {"type": "read", "sigma_frac": 0.01},
            {"type": "background", "bg_frac": 0.02, "star_density": 0.003, "star_frac": 0.8},
            {"type": "saturate", "sat_frac": 0.8},
            {"type": "downsample", "size": 64},
        ]},
    ]
    return degs


def _device():
    return "cuda" if torch.cuda.is_available() else "cpu"


# ============================================================
# image-only 训练（clean 或带 online 增强 aug_fn）
# ============================================================
def train_image_only(data, args, seed, aug_fn=None):
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = _device()
    Xi_tr_np = images[tr_idx]
    y_tr_np = rf.encode_target(yaw[tr_idx], pitch[tr_idx])
    Xi_va = torch.FloatTensor(images[val_idx]).to(device)
    y_va = torch.FloatTensor(rf.encode_target(yaw[val_idx], pitch[val_idx])).to(device)
    torch.manual_seed(seed); np.random.seed(seed)
    model = rf.ResNetImageOnly().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    crit = nn.MSELoss()
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
            if aug_fn is not None:
                img_np = aug_fn(img_np)
            xi = torch.FloatTensor(img_np).to(device)
            yb = torch.FloatTensor(y_tr_np[bidx]).to(device)
            opt.zero_grad(); loss = crit(model(xi), yb); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            tot = sum(crit(model(xi), yb).item() * len(xi) for xi, yb in va_loader)
        va = tot / len(val_idx)
        if va < best_va - 1e-8:
            best_va, best_state, wait = va, {k: v.cpu().clone() for k, v in model.state_dict().items()}, 0
        else:
            wait += 1
        if wait >= args.patience:
            break
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return best_state, ep, best_va


@torch.no_grad()
def eval_image_only(state, images_eval, yaw, pitch, test_idx, args):
    device = _device()
    model = rf.ResNetImageOnly().to(device)
    model.load_state_dict(state); model.eval()
    Xi = torch.FloatTensor(images_eval[test_idx]).to(device)
    bs = args.batch_size * 2
    preds = [model(Xi[s:s + bs]).cpu().numpy() for s in range(0, len(test_idx), bs)]
    yp, pp = rf.decode_pred(np.concatenate(preds))
    m, err = rf.compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
    return m


@torch.no_grad()
def eval_fusion(state, images_eval, ocs_zs, yaw, pitch, test_idx, args, ocs_dim):
    device = _device()
    model = up.RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
    model.load_state_dict(state); model.eval()
    m, _ = up.eval_on_images(model, images_eval, ocs_zs, yaw, pitch, test_idx, args)
    return m


def make_obs_aug_fn(obs_degs_for_aug, stats, base_seed):
    """online observation-style 增强：每 batch 随机选一种 obs 退化（含 clean）。"""
    rng = np.random.RandomState(base_seed)
    pool = obs_degs_for_aug

    def aug(img_batch_np):
        deg = pool[rng.randint(len(pool))]
        if not deg["ops"]:
            return img_batch_np
        return apply_obs_degradation(img_batch_np, deg, stats, seed=rng.randint(1 << 30))
    return aug


def summarize(per_seed):
    s = {}
    for k in SUM_KEYS:
        vals = [m[k] for m in per_seed]
        s[f"{k}_mean"] = float(np.mean(vals)); s[f"{k}_std"] = float(np.std(vals))
    return s


def main():
    ap = argparse.ArgumentParser(description="Exp12c: observation-style degradation stress test")
    ap.add_argument("--image-dir", default=up._IMAGE_DIR)
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
    ap.add_argument("--with-obs-aug", action="store_true",
                    help="额外训练 image-only obs-aug + U2 fusion obs-aug（资源允许时）")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    global SEEDS
    if args.smoke:
        SEEDS = [0]; args.epochs = 6; args.patience = 4
    elif args.seeds is not None:
        SEEDS = args.seeds
    up.SEEDS = SEEDS; lf.SEEDS = SEEDS

    if args.manifest is None:
        cands = sorted(glob.glob(up._MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No manifest: {up._MANIFEST_GLOB}")
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
    print("  实验12c：Observation-style 图像退化压力测试")
    print(f"  Output: {out_dir}")
    print(f"  Seeds: {SEEDS}  with_obs_aug={args.with_obs_aug}")
    print(f"  Device: {_device()}")
    print("=" * 70)

    t_all = time.time()
    print("\n  [准备数据]")
    data = up.prepare_data(args)
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data

    # train 线性强度统计
    lin_tr = to_linear(images[tr_idx])
    stats = {"lin_train_max": float(lin_tr.max()),
             "lin_train_mean": float(lin_tr.mean()),
             "lin_train_p99": float(np.percentile(lin_tr, 99))}
    print(f"  train 线性强度: max={stats['lin_train_max']:.4f} "
          f"mean={stats['lin_train_mean']:.4f} p99={stats['lin_train_p99']:.4f}")

    obs_degs = build_obs_degs()
    print(f"  observation-style 退化档: {[d['name'] for d in obs_degs]}")

    # 预计算退化图像（每档固定 seed，保证各模型同输入）
    print("\n  [预计算 observation-style 退化图像]")
    t0 = time.time()
    deg_images = {}
    for d in obs_degs:
        deg_images[d["name"]] = (images if not d["ops"]
                                 else apply_obs_degradation(images, d, stats, seed=20260604))
    print(f"    退化图像预计算耗时 {time.time()-t0:.0f}s")

    # ---- 训练模型 ----
    print(f"\n{'='*64}\n  训练 ResNet image-only clean（{len(SEEDS)} seeds）\n{'='*64}")
    t0 = time.time(); st_img_clean = []
    for s in SEEDS:
        st, ep, bva = train_image_only(data, args, s, aug_fn=None)
        st_img_clean.append(st); print(f"    [img-clean] seed={s} ep={ep} va={bva:.6f}", flush=True)
    print(f"  耗时 {time.time()-t0:.0f}s")

    print(f"\n{'='*64}\n  训练 ResNet image-only same-aug（AUG_DEGS，与 U1 同款）\n{'='*64}")
    t0 = time.time(); st_img_aug = []
    for s in SEEDS:
        aug = up.make_aug_fn(up.AUG_DEGS, base_seed=1000 + s)
        st, ep, bva = train_image_only(data, args, s, aug_fn=aug)
        st_img_aug.append(st); print(f"    [img-sameaug] seed={s} ep={ep} va={bva:.6f}", flush=True)
    print(f"  耗时 {time.time()-t0:.0f}s")

    print(f"\n{'='*64}\n  训练 U1 degradation-aware fusion（AUG_DEGS）\n{'='*64}")
    t0 = time.time(); st_u1 = []
    for s in SEEDS:
        st, ep, bva = up.train_model(
            lambda: up.RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout,
                                         p_drop_image=0.0, p_drop_ocs=0.0),
            data, args, augment=True, anchored=False, seed=s)
        st_u1.append(st); print(f"    [U1] seed={s} ep={ep} va={bva:.6f}", flush=True)
    print(f"  耗时 {time.time()-t0:.0f}s")

    print(f"\n{'='*64}\n  训练 OCS-only MLP per_part_log 30D\n{'='*64}")
    t0 = time.time(); st_ocs = []
    for s in SEEDS:
        st, ep, bva = lf.train_ocs_mlp(data, args, s)
        st_ocs.append(st); print(f"    [ocs-mlp] seed={s} ep={ep} va={bva:.6f}", flush=True)
    print(f"  耗时 {time.time()-t0:.0f}s")

    # OCS-only 评估（退化无关，平线）
    ocs_per_seed = []
    for st in st_ocs:
        p4 = lf.ocs_pred4d(st, ocs_zs, test_idx, ocs_dim, args)
        yp, pp = rf.decode_pred(p4)
        m, _ = rf.compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
        ocs_per_seed.append(m)
    ocs_flat = summarize(ocs_per_seed)
    print(f"  OCS-only(平线) mean={ocs_flat['angular_err_mean_mean']:.2f}"
          f"±{ocs_flat['angular_err_mean_std']:.2f}° Hit5={ocs_flat['hit@5deg_mean']:.1%}")

    # 可选 obs-aug 模型
    st_img_obsaug, st_u2_obsaug = None, None
    if args.with_obs_aug:
        # 仅用 mild/medium 级别 + 单算子做训练增强（避免把 severe 当 oracle）
        aug_pool = [d for d in obs_degs if d["name"] in
                    ("clean", "blur_sig1.5", "photon_g100", "read_0.005",
                     "background_0.005", "downsample_64", "combined_mild", "combined_medium")]
        print(f"\n{'='*64}\n  [obs-aug] image-only obs-aug + U2 fusion obs-aug\n{'='*64}")
        t0 = time.time(); st_img_obsaug = []
        for s in SEEDS:
            aug = make_obs_aug_fn(aug_pool, stats, base_seed=3000 + s)
            st, ep, bva = train_image_only(data, args, s, aug_fn=aug)
            st_img_obsaug.append(st); print(f"    [img-obsaug] seed={s} ep={ep} va={bva:.6f}", flush=True)
        # U2 fusion obs-aug：用 RobustFusionModel + 自定义 obs-aug 训练循环
        st_u2_obsaug = train_fusion_obs_aug(data, args, aug_pool, stats)
        print(f"  obs-aug 训练耗时 {time.time()-t0:.0f}s")

    # ---- 评估全部模型 × obs 退化 ----
    print(f"\n{'='*64}\n  评估各模型 × observation-style 退化\n{'='*64}")
    rows = []
    model_evals = [
        ("image_only_clean", st_img_clean, "image"),
        ("image_only_same_aug", st_img_aug, "image"),
        ("U1_aug_fusion", st_u1, "fusion"),
    ]
    if args.with_obs_aug:
        model_evals.append(("image_only_obs_aug", st_img_obsaug, "image"))
        model_evals.append(("U2_fusion_obs_aug", st_u2_obsaug, "fusion"))

    for d in obs_degs:
        dn = d["name"]
        imgs_eval = deg_images[dn]
        for mname, states, kind in model_evals:
            ps = []
            for st in states:
                if kind == "image":
                    ps.append(eval_image_only(st, imgs_eval, yaw, pitch, test_idx, args))
                else:
                    ps.append(eval_fusion(st, imgs_eval, ocs_zs, yaw, pitch, test_idx, args, ocs_dim))
            srow = summarize(ps); srow["degradation"] = dn; srow["model"] = mname
            rows.append(srow)
        # OCS-only 平线
        oc = dict(ocs_flat); oc["degradation"] = dn; oc["model"] = "OCS_only_mlp"
        rows.append(oc)
        # 打印
        def gm(mn):
            r = next((x for x in rows if x["degradation"] == dn and x["model"] == mn), None)
            return f"{r['angular_err_mean_mean']:.2f}°" if r else "—"
        print(f"    [{dn:>16}] img_clean={gm('image_only_clean')} "
              f"img_aug={gm('image_only_same_aug')} U1={gm('U1_aug_fusion')} "
              f"OCS={gm('OCS_only_mlp')}", flush=True)

    # ---- 保存 ----
    save_all(out_dir, rows, obs_degs, stats, ocs_flat, args, t_all)
    print(f"\n  完成，总耗时 {time.time()-t_all:.0f}s。输出: {out_dir}")
    return out_dir


def train_fusion_obs_aug(data, args, aug_pool, stats):
    """U2: RobustFusionModel + online observation-style 图像增强（OCS 始终 clean）。"""
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = _device()
    crit = nn.MSELoss()
    Xi_tr_np = images[tr_idx]; Xo_tr_np = ocs_zs[tr_idx]
    y_tr_np = rf.encode_target(yaw[tr_idx], pitch[tr_idx])
    Xi_va = torch.FloatTensor(images[val_idx]).to(device)
    Xo_va = torch.FloatTensor(ocs_zs[val_idx]).to(device)
    y_va = torch.FloatTensor(rf.encode_target(yaw[val_idx], pitch[val_idx])).to(device)
    va_loader = DataLoader(TensorDataset(Xi_va, Xo_va, y_va), batch_size=args.batch_size * 2)
    states = []
    for seed in SEEDS:
        torch.manual_seed(seed); np.random.seed(seed)
        model = up.RobustFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
        aug = make_obs_aug_fn(aug_pool, stats, base_seed=4000 + seed)
        n_tr = len(tr_idx); bs = args.batch_size
        best_va, best_state, wait, ep = float("inf"), None, 0, 0
        rng_ep = np.random.RandomState(seed)
        for ep in range(1, args.epochs + 1):
            model.train()
            perm = rng_ep.permutation(n_tr)
            for s in range(0, n_tr, bs):
                bidx = perm[s:s + bs]
                img_np = aug(Xi_tr_np[bidx])
                xi = torch.FloatTensor(img_np).to(device)
                xo = torch.FloatTensor(Xo_tr_np[bidx]).to(device)
                yb = torch.FloatTensor(y_tr_np[bidx]).to(device)
                opt.zero_grad(); loss = crit(model(xi, xo), yb); loss.backward(); opt.step()
            model.eval()
            with torch.no_grad():
                tot = sum(crit(model(xi, xo), yb).item() * len(xi) for xi, xo, yb in va_loader)
            va = tot / len(val_idx)
            if va < best_va - 1e-8:
                best_va, best_state, wait = va, {k: v.cpu().clone() for k, v in model.state_dict().items()}, 0
            else:
                wait += 1
            if wait >= args.patience:
                break
        states.append(best_state)
        print(f"    [U2-obsaug] seed={seed} ep={ep} va={best_va:.6f}", flush=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return states


def save_all(out_dir, rows, obs_degs, stats, ocs_flat, args, t_all):
    cols = ["model", "degradation"] + [f"{k}_mean" for k in SUM_KEYS] + [f"{k}_std" for k in SUM_KEYS]
    with open(os.path.join(out_dir, "obs_degradation_results.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    with open(os.path.join(out_dir, "obs_degradation_results.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    # degradation_config 表
    cfg_rows = []
    for d in obs_degs:
        cfg_rows.append({"name": d["name"],
                         "ops": json.dumps(d["ops"], ensure_ascii=False)})
    with open(os.path.join(out_dir, "degradation_config.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "ops"])
        w.writeheader()
        for r in cfg_rows:
            w.writerow(r)
    with open(os.path.join(out_dir, "degradation_config.json"), "w", encoding="utf-8") as f:
        json.dump({"degs": obs_degs, "train_linear_stats": stats,
                   "param_definition": "read sigma / background / saturation 均相对 lin_train_max；"
                                       "photon gain 为期望光子计数尺度；blur sigma 单位像素；"
                                       "downsample 为中间分辨率"},
                  f, indent=2, ensure_ascii=False)

    # markdown
    models = sorted({r["model"] for r in rows},
                    key=lambda m: ["image_only_clean", "image_only_same_aug", "image_only_obs_aug",
                                   "U1_aug_fusion", "U2_fusion_obs_aug", "OCS_only_mlp"].index(m)
                    if m in ["image_only_clean", "image_only_same_aug", "image_only_obs_aug",
                             "U1_aug_fusion", "U2_fusion_obs_aug", "OCS_only_mlp"] else 99)
    degs = [d["name"] for d in obs_degs]
    L = ["# 实验12c：Observation-style 图像退化压力测试 — 结果", "",
         f"> 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
         f"> Split 10°→5°，{len(SEEDS)} seeds；OCS=per_part_log 30D（始终 clean）；"
         "image=phase63 exact BRDF log1p 128×128。  ",
         f"> 退化在线性强度域施加（expm1 反归一化→退化→log1p）。"
         f"train 线性 max={stats['lin_train_max']:.3f}。  ",
         "> **合成退化压力测试，非真实望远镜验证。**", "",
         "## 主结果表：mean angular error (Hit@5°)", "",
         "| 退化档 | " + " | ".join(models) + " |",
         "|---|" + "---|" * len(models)]

    def cell(dn, mn):
        r = next((x for x in rows if x["degradation"] == dn and x["model"] == mn), None)
        if not r:
            return "—"
        return f"{r['angular_err_mean_mean']:.2f}° ({r['hit@5deg_mean']:.0%})"
    for dn in degs:
        L.append(f"| {dn} | " + " | ".join(cell(dn, mn) for mn in models) + " |")

    L += ["", "## 判读（按数据，不预设结论）", ""]
    # clean baseline vs severe
    def get(dn, mn):
        r = next((x for x in rows if x["degradation"] == dn and x["model"] == mn), None)
        return r["angular_err_mean_mean"] if r else float("nan")
    for mn in models:
        if mn == "OCS_only_mlp":
            continue
        c = get("clean", mn); sev = get("combined_severe", mn)
        L.append(f"- **{mn}**：clean={c:.2f}° → combined_severe={sev:.2f}°（OCS-only 平线"
                 f"={ocs_flat['angular_err_mean_mean']:.2f}°）。")
    L += ["",
          "> 关键观察须由 Codex/Claude 结合曲线撰写。允许写：observation-style 合成退化下，"
          "退化感知 U1 比 clean-trained image-only 更稳；OCS-only 不受图像退化影响。",
          "> 禁止写：fusion automatically robust / OCS standalone fallback / fully robust / "
          "near-perfect / real telescope / operational robustness。", "",
          "## 退化算子定义（相对 train 线性强度统计）", "",
          "见 `degradation_config.json` / `degradation_config.csv`。"]
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"config": vars(args), "seeds": SEEDS,
                   "train_linear_stats": stats, "ocs_only_flat": ocs_flat,
                   "elapsed_sec": time.time() - t_all}, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()

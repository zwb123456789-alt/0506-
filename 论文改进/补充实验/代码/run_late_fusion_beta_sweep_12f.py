"""
run_late_fusion_beta_sweep_12f.py — 实验12f：Late-fusion beta sweep 图像退化对照
================================================================================
目的（指导文件 §7）：
  检验显式推理端加权（late fusion）是否能提供比 naive feature fusion（实验11）
  更清晰的鲁棒路径。这是 inference-time 显式加权，不是自动 fallback。

设计：
  - 重训 ResNet image-only（clean，5 seeds）与 OCS-only MLP per_part_log 30D（5 seeds）。
    12b 结果目录未保存权重，故本脚本重训并保存 per-sample predictions（可复算）。
  - 退化条件：clean / noise 0.01 / noise 0.10 / brightness 0.50 / brightness 1.50。
  - beta grid：0, 0.1, ..., 1.0（beta=image 权重）。
        pred_blend = beta * pred_image + (1-beta) * pred_ocs
        beta=1.0 -> image-only ; beta=0.0 -> OCS-only ; beta=0.5 -> equal
  - 融合在单位 sin-cos 4D 空间（解码→单位重编码→beta 混合→逐对归一化解码），
    与既有 A5 late_fusion 口径一致。
  - 与实验11 naive feature fusion、实验12 U1 对比。

不变口径：split 10°→5°；target [sin,cos,sin,cos]；great-circle err；
          OCS=concat5 per_part_log 30D（始终 clean，OCS 不受图像退化影响）；
          image=phase63 exact BRDF log1p 128×128；seeds 0-4。

红线（指导文件 §7/§10）：
  - late fusion 表现好，也只能写 "explicit weighting can provide an inference-time
    robustness path"；不得写 U1 自动 fallback / automatic switching to OCS。
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic
import run_resnet_fusion as rf
import run_fusion_mechanism_upgrade as up

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                         "late_fusion_beta_sweep_12f")
SEEDS = [0, 1, 2, 3, 4]
BETAS = [round(b, 2) for b in np.arange(0.0, 1.0001, 0.1)]

# 对照参照（实验11 naive feature fusion / 实验12 U1，已确认口径）
REF_NAIVE_FUSION = {"clean": 1.47, "noise_0.01": 73.36, "noise_0.10": 73.57,
                    "bright_0.50": 1.86, "bright_1.50": 1.49}
REF_U1 = {"clean": 1.95, "noise_0.01": 1.95, "noise_0.10": 2.31,
          "bright_0.50": 1.98, "bright_1.50": 2.00}

SUM_KEYS = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "angular_err_worst", "hit@5deg", "hit@10deg"]


# ============================================================
# OCS-only MLP（架构同 train_mlp.OCSMLP：in->128->128->64->4，复现 ~5.91°）
# ============================================================
class OCSMLP(nn.Module):
    def __init__(self, input_dim, hidden=(128, 128, 64), dropout=0.10):
        super().__init__()
        layers = []
        d = input_dim
        for h in hidden:
            layers += [nn.Linear(d, h), nn.LayerNorm(h), nn.SiLU(), nn.Dropout(dropout)]
            d = h
        layers.append(nn.Linear(d, 4))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def _device():
    return "cuda" if torch.cuda.is_available() else "cpu"


def train_ocs_mlp(data, args, seed):
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = _device()
    Xo_tr = torch.FloatTensor(ocs_zs[tr_idx]).to(device)
    y_tr = torch.FloatTensor(rf.encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    Xo_va = torch.FloatTensor(ocs_zs[val_idx]).to(device)
    y_va = torch.FloatTensor(rf.encode_target(yaw[val_idx], pitch[val_idx])).to(device)
    torch.manual_seed(seed); np.random.seed(seed)
    model = OCSMLP(ocs_dim, dropout=args.dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    crit = nn.MSELoss()
    tr_loader = DataLoader(TensorDataset(Xo_tr, y_tr), batch_size=args.batch_size, shuffle=True)
    va_loader = DataLoader(TensorDataset(Xo_va, y_va), batch_size=args.batch_size * 2)
    best_va, best_state, wait, ep = float("inf"), None, 0, 0
    for ep in range(1, args.epochs + 1):
        model.train()
        for xb, yb in tr_loader:
            opt.zero_grad(); loss = crit(model(xb), yb); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            tot = sum(crit(model(xb), yb).item() * len(xb) for xb, yb in va_loader)
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
def ocs_pred4d(state, ocs_zs, test_idx, ocs_dim, args):
    device = _device()
    model = OCSMLP(ocs_dim, dropout=args.dropout).to(device)
    model.load_state_dict(state); model.eval()
    Xo = torch.FloatTensor(ocs_zs[test_idx]).to(device)
    bs = args.batch_size * 2
    out = [model(Xo[s:s + bs]).cpu().numpy() for s in range(0, len(test_idx), bs)]
    return np.concatenate(out)


# ============================================================
# ResNet image-only（clean 训练）
# ============================================================
def train_image_only_clean(data, args, seed):
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    device = _device()
    X_tr = torch.FloatTensor(images[tr_idx]).to(device)
    y_tr = torch.FloatTensor(rf.encode_target(yaw[tr_idx], pitch[tr_idx])).to(device)
    X_va = torch.FloatTensor(images[val_idx]).to(device)
    y_va = torch.FloatTensor(rf.encode_target(yaw[val_idx], pitch[val_idx])).to(device)
    torch.manual_seed(seed); np.random.seed(seed)
    model = rf.ResNetImageOnly().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    crit = nn.MSELoss()
    tr_loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=args.batch_size, shuffle=True)
    va_loader = DataLoader(TensorDataset(X_va, y_va), batch_size=args.batch_size * 2)
    best_va, best_state, wait, ep = float("inf"), None, 0, 0
    for ep in range(1, args.epochs + 1):
        model.train()
        for xb, yb in tr_loader:
            opt.zero_grad(); loss = crit(model(xb), yb); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            tot = sum(crit(model(xb), yb).item() * len(xb) for xb, yb in va_loader)
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
def image_pred4d(state, images_eval, test_idx, args):
    device = _device()
    model = rf.ResNetImageOnly().to(device)
    model.load_state_dict(state); model.eval()
    Xi = torch.FloatTensor(images_eval[test_idx]).to(device)
    bs = args.batch_size * 2
    out = [model(Xi[s:s + bs]).cpu().numpy() for s in range(0, len(test_idx), bs)]
    return np.concatenate(out)


# ============================================================
# beta 混合（A5 口径：解码 -> 单位 sin-cos 重编码 -> beta 混合 -> 逐对归一化解码）
# ============================================================
def unit_encode(pred4d):
    yaw, pitch = rf.decode_pred(pred4d)
    y = np.deg2rad(yaw); p = np.deg2rad(pitch)
    return np.stack([np.sin(y), np.cos(y), np.sin(p), np.cos(p)], axis=1)


def blend_metrics(img4d, ocs4d, beta, yaw_t, pitch_t):
    iv = unit_encode(img4d)
    ov = unit_encode(ocs4d)
    fused = beta * iv + (1.0 - beta) * ov
    fy, fp = rf.decode_pred(fused)
    m, err = rf.compute_metrics(fy, fp, yaw_t, pitch_t)
    return m, err


def summarize(per_seed):
    s = {}
    for k in SUM_KEYS:
        vals = [m[k] for m in per_seed]
        s[f"{k}_mean"] = float(np.mean(vals)); s[f"{k}_std"] = float(np.std(vals))
    return s


def main():
    ap = argparse.ArgumentParser(description="Exp12f: late-fusion beta sweep under degradation")
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
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    global SEEDS
    if args.smoke:
        SEEDS = [0]; args.epochs = 6; args.patience = 4
    elif args.seeds is not None:
        SEEDS = args.seeds
    up.SEEDS = SEEDS

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
    print("  实验12f：Late-fusion beta sweep 图像退化对照")
    print(f"  Output: {out_dir}")
    print(f"  Seeds: {SEEDS}  betas={BETAS}")
    print(f"  Device: {_device()}")
    print("=" * 70)

    t_all = time.time()
    print("\n  [准备数据]（检查既有权重/预测：12b 未保存权重，按协议重训）")
    data = up.prepare_data(args)
    images, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data
    yaw_t, pitch_t = yaw[test_idx], pitch[test_idx]

    # 训练 image-only clean + OCS MLP
    print(f"\n{'='*64}\n  训练 ResNet image-only clean（{len(SEEDS)} seeds）\n{'='*64}")
    t0 = time.time(); img_states = []
    for s in SEEDS:
        st, ep, bva = train_image_only_clean(data, args, s)
        img_states.append(st)
        print(f"    [image-only] seed={s} ep={ep} best_va={bva:.6f}", flush=True)
    print(f"  image-only 训练耗时 {time.time()-t0:.0f}s")

    print(f"\n{'='*64}\n  训练 OCS-only MLP per_part_log 30D（{len(SEEDS)} seeds）\n{'='*64}")
    t0 = time.time(); ocs_states = []
    for s in SEEDS:
        st, ep, bva = train_ocs_mlp(data, args, s)
        ocs_states.append(st)
        print(f"    [ocs-mlp] seed={s} ep={ep} best_va={bva:.6f}", flush=True)
    print(f"  OCS MLP 训练耗时 {time.time()-t0:.0f}s")

    # OCS 4D 预测（与图像退化无关，每 seed 一份）
    ocs4d_by_seed = [ocs_pred4d(st, ocs_zs, test_idx, ocs_dim, args) for st in ocs_states]

    # 退化图像预计算
    deg_images = {d["name"]: up.apply_image_degradation(images, d) for d in up.EVAL_DEGS}

    # 逐退化、逐 seed 的 image 4D 预测
    print(f"\n{'='*64}\n  推理 image 4D 预测（各退化档）\n{'='*64}")
    img4d = {}  # deg -> [seed](N,4)
    for deg in up.EVAL_DEGS:
        dn = deg["name"]
        img4d[dn] = [image_pred4d(st, deg_images[dn], test_idx, args) for st in img_states]
        print(f"    [{dn}] image 4D preds done", flush=True)

    # beta sweep
    print(f"\n{'='*64}\n  beta sweep（{len(BETAS)} betas × {len(up.EVAL_DEGS)} 退化档）\n{'='*64}")
    sweep_rows = []     # 聚合：每 (deg, beta) 一行（over seeds）
    per_seed_rows = []  # 每 (deg, beta, seed) 一行
    for deg in up.EVAL_DEGS:
        dn = deg["name"]
        for beta in BETAS:
            per_seed_m = []
            for si in range(len(SEEDS)):
                m, _ = blend_metrics(img4d[dn][si], ocs4d_by_seed[si], beta, yaw_t, pitch_t)
                per_seed_m.append(m)
                row = {"degradation": dn, "beta": beta, "seed": SEEDS[si]}
                row.update({k: m[k] for k in SUM_KEYS})
                per_seed_rows.append(row)
            s = summarize(per_seed_m)
            s["degradation"] = dn; s["beta"] = beta
            sweep_rows.append(s)
        # 打印该退化档关键 beta
        def getmean(b):
            r = next(x for x in sweep_rows if x["degradation"] == dn and x["beta"] == b)
            return r["angular_err_mean_mean"]
        best = min((x for x in sweep_rows if x["degradation"] == dn),
                   key=lambda x: x["angular_err_mean_mean"])
        print(f"    [{dn:>12}] beta0(OCS)={getmean(0.0):.2f}° "
              f"beta1(img)={getmean(1.0):.2f}° best beta={best['beta']:.1f}→"
              f"{best['angular_err_mean_mean']:.2f}°", flush=True)

    # ---- 保存 ----
    # per-(deg,beta) 聚合
    _save_csv(os.path.join(out_dir, "beta_sweep_summary.csv"), sweep_rows,
              ["degradation", "beta"] + [f"{k}_mean" for k in SUM_KEYS]
              + [f"{k}_std" for k in SUM_KEYS])
    # per-seed
    _save_csv(os.path.join(out_dir, "beta_sweep_per_seed.csv"), per_seed_rows,
              ["degradation", "beta", "seed"] + SUM_KEYS)
    # per-sample 可复算基预测（npz）：img4d[deg][seed], ocs4d[seed], true
    np.savez_compressed(
        os.path.join(out_dir, "per_sample_base_predictions.npz"),
        test_idx=np.array(test_idx),
        yaw_true=yaw_t, pitch_true=pitch_t,
        ocs4d=np.stack(ocs4d_by_seed),  # (S,N,4)
        **{f"img4d__{dn}": np.stack(img4d[dn]) for dn in img4d},  # (S,N,4)
        betas=np.array(BETAS), seeds=np.array(SEEDS),
    )

    write_summary(out_dir, sweep_rows, args, t_all)

    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"config": vars(args), "seeds": SEEDS, "betas": BETAS,
                   "ref_naive_fusion": REF_NAIVE_FUSION, "ref_U1": REF_U1,
                   "beta_definition": "pred_blend = beta*pred_image + (1-beta)*pred_ocs; "
                                      "beta=1 image-only, beta=0 OCS-only",
                   "fusion_space": "unit sin-cos 4D, per-pair renormalized (A5 convention)",
                   "elapsed_sec": time.time() - t_all}, f, indent=2, ensure_ascii=False)

    print(f"\n  完成，总耗时 {time.time()-t_all:.0f}s。输出: {out_dir}")
    return out_dir


def _save_csv(path, rows, keys):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _cell(sweep, dn, beta):
    r = next((x for x in sweep if x["degradation"] == dn and x["beta"] == beta), None)
    return r["angular_err_mean_mean"] if r else float("nan")


def write_summary(out_dir, sweep, args, t_all):
    degs = [d["name"] for d in up.EVAL_DEGS]
    L = ["# 实验12f：Late-fusion beta sweep 图像退化对照 — 结果", "",
         f"> 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
         f"> Split 10°→5°，{len(SEEDS)} seeds；image=ResNet clean-trained；"
         "OCS=MLP per_part_log 30D（始终 clean）。  ",
         "> beta=image 权重；融合在单位 sin-cos 4D（A5 口径）。  ",
         "> pred_blend = beta·pred_image + (1−beta)·pred_ocs（beta=1 image-only，beta=0 OCS-only）。", "",
         "## 主结果表：各退化档 beta sweep（mean angular error）", "",
         "| 退化 | β=0 (OCS) | β=0.3 | β=0.5 | β=0.7 | β=1 (img) | best β | best mean | naive fusion(参照) | U1(参照) |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for dn in degs:
        best = min((x for x in sweep if x["degradation"] == dn),
                   key=lambda x: x["angular_err_mean_mean"])
        L.append(f"| {dn} | {_cell(sweep,dn,0.0):.2f}° | {_cell(sweep,dn,0.3):.2f}° | "
                 f"{_cell(sweep,dn,0.5):.2f}° | {_cell(sweep,dn,0.7):.2f}° | "
                 f"{_cell(sweep,dn,1.0):.2f}° | {best['beta']:.1f} | "
                 f"{best['angular_err_mean_mean']:.2f}° | "
                 f"{REF_NAIVE_FUSION.get(dn,'—')}° | {REF_U1.get(dn,'—')}° |")
    L += ["", "## 判读（按数据，不预设结论）", ""]
    # 关键：噪声档 best-beta 是否偏向 OCS（小 beta），且优于 naive fusion
    for dn in ["noise_0.01", "noise_0.10"]:
        best = min((x for x in sweep if x["degradation"] == dn),
                   key=lambda x: x["angular_err_mean_mean"])
        nf = REF_NAIVE_FUSION.get(dn)
        L.append(f"- **{dn}**：best β={best['beta']:.1f}（{best['angular_err_mean_mean']:.2f}°）"
                 f"，naive feature fusion={nf}°。"
                 + ("噪声下最优 β 偏向 OCS（小 β），且显式 late fusion 可远低于 naive feature fusion；"
                    "说明 **inference-time 显式加权能提供一条鲁棒路径**（非自动 fallback）。"
                    if best["beta"] <= 0.5 and best["angular_err_mean_mean"] < (nf or 1e9)
                    else "best β 仍偏向图像或未超过 naive fusion，需结合曲线讨论。"))
    L += ["",
          "## 写作红线", "",
          "- late fusion 表现好，只能写 *explicit inference-time weighting can provide a robustness path*；",
          "- 不得写 U1 / fusion automatically switches to OCS / automatic fallback；",
          "- 不得写 real telescope / operational robustness / fully robust。",
          "- best β 是 oracle（用 test 选出），论文须注明这是 inference-time 上界，"
          "真实部署需独立的退化检测/加权策略。"]
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()

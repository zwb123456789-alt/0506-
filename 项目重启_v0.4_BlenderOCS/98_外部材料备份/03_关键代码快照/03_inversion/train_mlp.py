"""
模块 C · OCS-only MLP 连续回归 + 加权 kNN baseline（Step 11c）
=============================================================
- 10° 网格 train → 5° 插值 test
- sin/cos 周期编码输出
- 特征预设：obs_total(5D) / total(15D) / per_part(30D) / all(45D)
- 预处理：log10 + zscore（scaler 仅 fit train）
- 多 seed 评估 + 加权 kNN regression baseline
"""

import argparse
import csv
import glob
import json
import os
import sys
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import inv_common as ic

# ---- 默认路径（自动检测最新 run 目录）------------------------------
_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
_MANIFEST_GLOB = os.path.join(_PROJECT_ROOT, "结果", "模块A_重构", "multi_geom_ggx_yaw73_pitch37", "run_*", "multi_geom_manifest.json")
_OUT_ROOT_DEFAULT = os.path.join(_PROJECT_ROOT, "结果", "模块C_反演", "mlp_ocs")


def _find_manifest():
    cands = sorted(glob.glob(_MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"未找到 multi_geom_manifest.json，glob: {_MANIFEST_GLOB}")
    return cands[0]


# ============================================================
# 目标编码 / 解码
# ============================================================

def encode_target(yaw_deg, pitch_deg):
    y = np.deg2rad(yaw_deg % 360.0)
    p = np.deg2rad(pitch_deg)
    return np.stack([np.sin(y), np.cos(y), np.sin(p), np.cos(p)], axis=1)


EPS_DECODE = 1e-8


def decode_pred(pred):
    ys, yc, ps, pc = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    yr = np.sqrt(ys ** 2 + yc ** 2) + EPS_DECODE
    pr = np.sqrt(ps ** 2 + pc ** 2) + EPS_DECODE
    ys, yc = ys / yr, yc / yr
    ps, pc = ps / pr, pc / pr
    yaw = (np.rad2deg(np.arctan2(ys, yc)) + 360.0) % 360.0
    pitch = np.rad2deg(np.arctan2(ps, pc))
    pitch = np.clip(pitch, -90.0, 90.0)
    return yaw, pitch


# ============================================================
# 数据准备
# ============================================================

def prepare_data(manifest_path, feat_mode, use_log):
    """加载多几何数据 → 10°→5° split → 预处理 → train/val/test。"""
    label_order, _, feat_dict, yaw_dict, pitch_dict = ic.load_multi_geom(manifest_path)
    if not label_order:
        raise RuntimeError("无几何数据")

    # 拼接多几何特征（每几何先选特征模式再拼接）
    feats, yaw, pitch, _ = ic.build_concat_features_with_mode(
        feat_dict, yaw_dict, pitch_dict, label_order, feat_mode)

    # 10°→5° split
    split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    train_idx = split["train_idx"]
    test_idx = split["test_idx"]

    X_all = feats[train_idx]
    y_all = encode_target(yaw[train_idx], pitch[train_idx])
    X_test = feats[test_idx]
    y_test = encode_target(yaw[test_idx], pitch[test_idx])

    # train 内切 80/20 val
    rng = np.random.RandomState(42)
    N_train = len(X_all)
    perm = rng.permutation(N_train)
    n_val = int(N_train * 0.20)
    val_idx = perm[:n_val]
    tr_idx = perm[n_val:]

    X_train_raw, y_train = X_all[tr_idx], y_all[tr_idx]
    X_val_raw, y_val = X_all[val_idx], y_all[val_idx]

    # log 变换（仅对 OCS 列，skip 遮挡率列）
    if feat_mode in ("per_part", "obs_total"):
        log_skip = None
    else:
        log_skip = {2}

    X_test_raw = X_test.copy()
    if use_log:
        X_train_raw = ic.log_transform(X_train_raw, skip_cols=log_skip)
        X_val_raw   = ic.log_transform(X_val_raw, skip_cols=log_skip)
        X_test_raw  = ic.log_transform(X_test_raw, skip_cols=log_skip)

    # zscore（仅 fit train）
    X_train, mu, sd = ic.zscore(X_train_raw, return_params=True)
    X_val = (X_val_raw - mu) / sd
    X_test_zs = (X_test_raw - mu) / sd

    return {
        "X_train": X_train, "y_train": y_train,
        "X_val": X_val, "y_val": y_val,
        "X_test": X_test_zs, "y_test": y_test,
        "yaw_test": yaw[test_idx], "pitch_test": pitch[test_idx],
        "yaw_train": yaw[train_idx][tr_idx], "pitch_train": pitch[train_idx][tr_idx],
        "yaw_val": yaw[train_idx][val_idx], "pitch_val": pitch[train_idx][val_idx],
        "train_idx": train_idx[tr_idx], "val_idx": train_idx[val_idx],
        "test_idx": test_idx,
        "input_dim": X_train.shape[1],
        "mu": mu, "sd": sd,
    }


# ============================================================
# PyTorch MLP 模型
# ============================================================

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


class OCSMLP(nn.Module):
    def __init__(self, input_dim, hidden=[128, 128, 64], dropout=0.10,
                 activation="silu", norm="layernorm"):
        super().__init__()
        layers = []
        d_in = input_dim
        for h in hidden:
            layers.append(nn.Linear(d_in, h))
            if norm == "batchnorm":
                layers.append(nn.BatchNorm1d(h))
            elif norm == "layernorm":
                layers.append(nn.LayerNorm(h))
            if activation == "silu":
                layers.append(nn.SiLU())
            else:
                layers.append(nn.ReLU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            d_in = h
        layers.append(nn.Linear(d_in, 4))  # sin_yaw, cos_yaw, sin_pitch, cos_pitch
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def train_epoch(model, loader, optimizer, criterion):
    model.train()
    total_loss, n = 0.0, 0
    for Xb, yb in loader:
        optimizer.zero_grad()
        pred = model(Xb)
        loss = criterion(pred, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(Xb)
        n += len(Xb)
    return total_loss / n


def eval_model(model, loader, criterion):
    model.eval()
    total_loss, n = 0.0, 0
    all_pred, all_y = [], []
    with torch.no_grad():
        for Xb, yb in loader:
            pred = model(Xb)
            loss = criterion(pred, yb)
            total_loss += loss.item() * len(Xb)
            n += len(Xb)
            all_pred.append(pred.cpu().numpy())
            all_y.append(yb.cpu().numpy())
    return total_loss / n, np.concatenate(all_pred), np.concatenate(all_y)


def train_mlp(data, seed, device="cpu", epochs=2000, patience=150,
              lr=1e-3, wd=1e-4, batch_size=64):
    """训练 MLP，返回最佳模型和训练曲线。"""
    torch.manual_seed(seed)
    np.random.seed(seed)

    X_tr = torch.FloatTensor(data["X_train"]).to(device)
    y_tr = torch.FloatTensor(data["y_train"]).to(device)
    X_va = torch.FloatTensor(data["X_val"]).to(device)
    y_va = torch.FloatTensor(data["y_val"]).to(device)
    X_te = torch.FloatTensor(data["X_test"]).to(device)
    y_te = torch.FloatTensor(data["y_test"]).to(device)

    tr_loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=batch_size, shuffle=True)
    va_loader = DataLoader(TensorDataset(X_va, y_va), batch_size=batch_size * 2)

    model = OCSMLP(data["input_dim"]).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    criterion = nn.MSELoss()

    best_val_loss = float("inf")
    best_state = None
    wait = 0
    curve = []

    for ep in range(1, epochs + 1):
        tr_loss = train_epoch(model, tr_loader, optimizer, criterion)
        va_loss, va_pred, va_y = eval_model(model, va_loader, criterion)
        curve.append({"epoch": ep, "train_loss": tr_loss, "val_loss": va_loss})

        if va_loss < best_val_loss - 1e-8:
            best_val_loss = va_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            wait = 0
        else:
            wait += 1

        if wait >= patience:
            break

    # 加载最佳模型
    model.load_state_dict(best_state)
    te_loss, te_pred, te_y = eval_model(model, DataLoader(
        TensorDataset(X_te, y_te), batch_size=batch_size * 2), criterion)
    return model, te_pred, te_y, tr_loss, best_val_loss, te_loss, curve


# ============================================================
# kNN 加权回归 baseline
# ============================================================

from sklearn.neighbors import KNeighborsRegressor


def run_knn_regression(data):
    """距离加权 kNN 回归：在 sin/cos 空间平均邻居。"""
    knn = KNeighborsRegressor(n_neighbors=5, weights="distance", metric="euclidean")
    knn.fit(data["X_train"], data["y_train"])
    pred = knn.predict(data["X_test"])
    return pred


# ============================================================
# 指标
# ============================================================

def compute_metrics(yaw_pred, pitch_pred, yaw_true, pitch_true):
    """计算全部指标。"""
    err_a = ic.angular_err_deg(yaw_pred, pitch_pred, yaw_true, pitch_true)
    N = len(yaw_true)

    m = {
        "n_samples": N,
        "angular_err_mean": float(err_a.mean()),
        "angular_err_median": float(np.median(err_a)),
        "angular_err_p90": float(np.percentile(err_a, 90)),
        "angular_err_p95": float(np.percentile(err_a, 95)),
    }

    # Hit@5° / Hit@10°（单预测无 Top-K，直接算）
    m["hit@5deg"] = float(np.mean(err_a <= ic.HIT_THRESHOLD_DEG + 1e-6))
    m["hit@10deg"] = float(np.mean(err_a <= ic.HIT_THRESHOLD_10DEG + 1e-6))

    return m, err_a


# ============================================================
# 实验矩阵
# ============================================================

EXPERIMENTS = [
    ("obs_total", True,  "obs_total 5D log"),
    ("total",     True,  "total 15D log"),
    ("per_part",  True,  "per_part 30D log"),
    ("all",       True,  "all 45D log"),
    ("all",       False, "all 45D raw"),
]

SEEDS = [0, 1, 2, 3, 4]


def run_experiment_matrix(data_dict, out_dir):
    """运行完整实验矩阵。"""
    os.makedirs(out_dir, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  设备: {device}")

    all_seed_rows = []
    summary = {}

    for feat_mode, use_log, exp_label in EXPERIMENTS:
        print(f"\n{'=' * 70}")
        print(f"  {exp_label}")
        print(f"{'=' * 70}")

        # 准备数据
        data = prepare_data(data_dict["manifest_path"], feat_mode, use_log)
        print(f"  input_dim={data['input_dim']} "
              f"train={len(data['X_train'])} val={len(data['X_val'])} "
              f"test={len(data['X_test'])}")

        # 加权 kNN baseline（只跑一次，不依赖 seed）
        knn_pred_raw = run_knn_regression(data)
        yaw_knn, pitch_knn = decode_pred(knn_pred_raw)
        knn_metrics, knn_err = compute_metrics(
            yaw_knn, pitch_knn, data["yaw_test"], data["pitch_test"])
        print(f"  kNN-w: mean={knn_metrics['angular_err_mean']:.2f}° "
              f"med={knn_metrics['angular_err_median']:.2f}° "
              f"Hit5={knn_metrics['hit@5deg']:.1%} "
              f"Hit10={knn_metrics['hit@10deg']:.1%}")

        knn_row = {
            "experiment": exp_label, "method": "knn_weighted",
            "feat": feat_mode, "transform": "log" if use_log else "raw",
            "seed": -1,
            "input_dim": data["input_dim"],
            **knn_metrics,
        }
        all_seed_rows.append(knn_row)

        # MLP × 5 seeds
        mlp_metrics_list = []
        for seed in SEEDS:
            print(f"    seed={seed} ...", end=" ", flush=True)
            model, te_pred, te_y, tr_loss, va_loss, te_loss, curve = train_mlp(
                data, seed, device=device)
            yaw_mlp, pitch_mlp = decode_pred(te_pred)
            mlp_m, mlp_err = compute_metrics(
                yaw_mlp, pitch_mlp, data["yaw_test"], data["pitch_test"])
            print(f"mean={mlp_m['angular_err_mean']:.2f}° "
                  f"Hit5={mlp_m['hit@5deg']:.1%} Hit10={mlp_m['hit@10deg']:.1%} "
                  f"best_epoch={len(curve)-150 if len(curve)>150 else len(curve)}")

            mlp_metrics_list.append(mlp_m)

            mlp_row = {
                "experiment": exp_label, "method": "mlp",
                "feat": feat_mode, "transform": "log" if use_log else "raw",
                "seed": seed,
                "input_dim": data["input_dim"],
                "train_loss_final": tr_loss,
                "val_loss_best": va_loss,
                "test_loss": te_loss,
                "best_epoch": len(curve),
                **mlp_m,
            }
            all_seed_rows.append(mlp_row)

            # 保存训练曲线
            curve_path = os.path.join(
                out_dir, f"train_curve_{feat_mode}_{'log' if use_log else 'raw'}_seed{seed}.csv")
            with open(curve_path, "w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["epoch", "train_loss", "val_loss"])
                w.writeheader()
                w.writerows(curve)

        # 各指标 mean ± std
        keys = ["angular_err_mean", "angular_err_median", "angular_err_p90",
                "angular_err_p95", "hit@5deg", "hit@10deg"]
        mlp_summary = {"knn_weighted": {k: knn_metrics[k] for k in keys}}
        for k in keys:
            vals = [m[k] for m in mlp_metrics_list]
            mlp_summary[f"mlp_{k}_mean"] = float(np.mean(vals))
            mlp_summary[f"mlp_{k}_std"] = float(np.std(vals))

        summary[exp_label] = {
            "feat": feat_mode, "transform": "log" if use_log else "raw",
            "input_dim": data["input_dim"],
            **mlp_summary,
        }

        print(f"  ---> MLP mean±std: {mlp_summary['mlp_angular_err_mean_mean']:.2f}°"
              f"±{mlp_summary['mlp_angular_err_mean_std']:.2f}° "
              f"Hit5={mlp_summary['mlp_hit@5deg_mean']:.1%}"
              f"±{mlp_summary['mlp_hit@5deg_std']:.1%} "
              f"| kNN-w: {knn_metrics['angular_err_mean']:.2f}°")

        # 保存测试预测
        pred_csv = os.path.join(
            out_dir, f"predictions_test_{feat_mode}_{'log' if use_log else 'raw'}.csv")
        with open(pred_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["yaw_true", "pitch_true", "yaw_mlp", "pitch_mlp",
                        "angle_err_mlp", "yaw_knn", "pitch_knn", "angle_err_knn"])
            for i in range(len(data["yaw_test"])):
                w.writerow([
                    f"{data['yaw_test'][i]:.4f}", f"{data['pitch_test'][i]:.4f}",
                    f"{yaw_mlp[i]:.4f}", f"{pitch_mlp[i]:.4f}", f"{mlp_err[i]:.4f}",
                    f"{yaw_knn[i]:.4f}", f"{pitch_knn[i]:.4f}", f"{knn_err[i]:.4f}",
                ])

    # ---- 保存 ----
    # metrics_by_seed.csv
    # 确保所有行有统一字段
    all_field_names = set()
    for r in all_seed_rows:
        all_field_names.update(r.keys())
    for r in all_seed_rows:
        for k in all_field_names:
            r.setdefault(k, None)
    seed_fields = sorted(all_field_names)
    seed_csv = os.path.join(out_dir, "metrics_by_seed.csv")
    with open(seed_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=seed_fields)
        w.writeheader()
        w.writerows(all_seed_rows)

    # metrics_summary.json
    with open(os.path.join(out_dir, "metrics_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # config_used.json
    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump({
            "model": "MLP 128→128→64 SiLU LayerNorm Dropout0.10",
            "output_encoding": "[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]",
            "loss": "MSE",
            "optimizer": "AdamW lr=1e-3 wd=1e-4",
            "batch_size": 64,
            "max_epochs": 2000,
            "early_stopping_patience": 150,
            "split": "10° grid train → 5° held-out test",
            "train_val_split": "80/20 from train (seed=42)",
            "seeds": SEEDS,
            "baselines": ["kNN weighted regression (K=5, distance weight)"],
            "preprocessing": "log10(zscore(X_ocs)), scaler fit on train only",
            "experiments": EXPERIMENTS,
            "manifest": data_dict["manifest_path"],
        }, f, indent=2, ensure_ascii=False)

    # 打印最终汇总
    print(f"\n{'=' * 90}")
    print("  最终汇总")
    print(f"{'=' * 90}")
    header = f"{'实验':<25} {'方法':<12} {'mean':>8} {'med':>8} {'p90':>8} {'Hit5':>8} {'Hit10':>8}"
    print(header)
    print("-" * len(header))
    for exp_label, s in summary.items():
        knn = s["knn_weighted"]
        print(f"{exp_label:<25} {'kNN-w':<12} {knn['angular_err_mean']:>8.2f}° "
              f"{knn['angular_err_median']:>8.2f}° {knn['angular_err_p90']:>8.2f}° "
              f"{knn['hit@5deg']:>8.1%} {knn['hit@10deg']:>8.1%}")
        print(f"{exp_label:<25} {'MLP (5seeds)':<12} "
              f"{s['mlp_angular_err_mean_mean']:>7.2f}±{s['mlp_angular_err_mean_std']:.1f}° "
              f"{s['mlp_angular_err_median_mean']:>7.2f}° "
              f"{s['mlp_angular_err_p90_mean']:>7.2f}° "
              f"{s['mlp_hit@5deg_mean']:>7.1%} "
              f"{s['mlp_hit@10deg_mean']:>7.1%}")

    print(f"\n  输出目录: {out_dir}")
    return summary


# ============================================================
# 主入口
# ============================================================

def parse_args():
    p = argparse.ArgumentParser(description="OCS-only MLP 连续回归 + kNN baseline")
    p.add_argument("--manifest", default=None,
                   help="multi_geom_manifest.json 路径，默认自动检测最新")
    p.add_argument("--out-root", default=None,
                   help="输出根目录，默认 结果/模块C_反演/mlp_ocs/")
    args = p.parse_args()
    if args.manifest is None:
        args.manifest = _find_manifest()
    if args.out_root is None:
        args.out_root = _OUT_ROOT_DEFAULT
    return args


def main():
    args = parse_args()

    print("=" * 80)
    print("  模块 C · OCS-only MLP 连续回归 + 加权 kNN baseline (Step 11c)")
    print(f"  数据源: {args.manifest}")
    print("=" * 80)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    run_experiment_matrix({"manifest_path": args.manifest}, out_dir)


if __name__ == "__main__":
    main()

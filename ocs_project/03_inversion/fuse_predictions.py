"""
Step 11e-B1 · CNN+OCS 预测级 late fusion 消融
=============================================
- 读取已训练的 OCS MLP 和 CNN 预测结果
- 按 (yaw_true, pitch_true) 对齐 test 样本
- 在 sin/cos 空间做预测级融合
- sweep beta 得到最佳 OCS 权重
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np


# ============================================================
# 角度 <-> sin/cos 向量
# ============================================================

def angle_to_vec(yaw_deg, pitch_deg):
    y = np.deg2rad(np.asarray(yaw_deg, dtype=float) % 360.0)
    p = np.deg2rad(np.asarray(pitch_deg, dtype=float))
    return np.stack([
        np.sin(y), np.cos(y),
        np.sin(p), np.cos(p),
    ], axis=1)


def vec_to_angle(vec):
    yaw = (np.rad2deg(np.arctan2(vec[:, 0], vec[:, 1])) + 360.0) % 360.0
    pitch = np.rad2deg(np.arctan2(vec[:, 2], vec[:, 3]))
    pitch = np.clip(pitch, -90.0, 90.0)
    return yaw, pitch


# ============================================================
# 指标
# ============================================================

HIT5 = 5.0
HIT10 = 10.0


def angular_err_deg(yaw_pred, pitch_pred, yaw_true, pitch_true):
    dy = np.deg2rad(np.abs(np.asarray(yaw_pred) - np.asarray(yaw_true)))
    dp = np.deg2rad(np.asarray(pitch_pred) - np.asarray(pitch_true))
    dy = np.minimum(dy, 2 * np.pi - dy)
    sp = np.sin(np.deg2rad(pitch_pred))
    st = np.sin(np.deg2rad(pitch_true))
    cp = np.cos(np.deg2rad(pitch_pred))
    ct = np.cos(np.deg2rad(pitch_true))
    cos_a = sp * st + cp * ct * np.cos(dy)
    cos_a = np.clip(cos_a, -1.0, 1.0)
    return np.rad2deg(np.arccos(cos_a))


def compute_metrics(yaw_pred, pitch_pred, yaw_true, pitch_true):
    err = angular_err_deg(yaw_pred, pitch_pred, yaw_true, pitch_true)
    return {
        "mean": float(np.mean(err)),
        "std": float(np.std(err)),
        "median": float(np.median(err)),
        "p90": float(np.percentile(err, 90)),
        "p95": float(np.percentile(err, 95)),
        "hit5": float(np.mean(err <= HIT5 + 1e-6)),
        "hit10": float(np.mean(err <= HIT10 + 1e-6)),
        "yaw_mean": float(np.mean(angular_err_deg(yaw_pred, pitch_true, yaw_true, pitch_true))),
        "pitch_mean": float(np.mean(np.abs(np.asarray(pitch_pred) - np.asarray(pitch_true)))),
    }, err


# ============================================================
# 加载预测
# ============================================================

def load_ocs_predictions(path):
    """OCS MLP CSV: yaw_true, pitch_true, yaw_mlp, pitch_mlp, ..."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "yaw_true": float(r["yaw_true"]),
                "pitch_true": float(r["pitch_true"]),
                "yaw_pred": float(r["yaw_mlp"]),
                "pitch_pred": float(r["pitch_mlp"]),
            })
    print(f"  [OCS] {len(rows)} predictions ({Path(path).name})")
    return rows


def load_cnn_predictions(path):
    """CNN CSV: idx, true_yaw, true_pitch, pred_yaw, pred_pitch, err_angular_deg"""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "yaw_true": float(r["true_yaw"]),
                "pitch_true": float(r["true_pitch"]),
                "yaw_pred": float(r["pred_yaw"]),
                "pitch_pred": float(r["pred_pitch"]),
            })
    return rows


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="CNN+OCS late fusion")
    parser.add_argument("--ocs-run", required=True)
    parser.add_argument("--cnn-run", required=True)
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--ocs-case", default=None)
    parser.add_argument("--ocs-glob", default=None)
    parser.add_argument("--cnn-glob", default="predictions_seed*.csv")
    parser.add_argument("--beta-sweep", default="0:0.01:1")
    parser.add_argument("--tag", default="fusion")
    args = parser.parse_args()

    ocs_run = Path(args.ocs_run)
    cnn_run = Path(args.cnn_run)
    out_root = Path(args.out_root)

    # ---- 找 OCS 文件 ----
    if args.ocs_glob:
        ocs_files = sorted(ocs_run.glob(args.ocs_glob))
    elif args.ocs_case:
        ocs_files = sorted(ocs_run.glob(f"predictions_test_{args.ocs_case}.csv"))
    else:
        ocs_files = sorted(ocs_run.glob("predictions_test_*.csv"))

    if not ocs_files:
        print(f"[ERROR] 无 OCS 预测文件")
        print("  候选:")
        for p in sorted(ocs_run.glob("*.csv")):
            print(f"    {p.name}")
        sys.exit(1)

    ocs_path = ocs_files[0]
    print(f"OCS 文件: {ocs_path.name}")

    # ---- 找 CNN 文件 ----
    cnn_files = sorted(cnn_run.glob(args.cnn_glob))
    if not cnn_files:
        print(f"[ERROR] 无 CNN 预测文件 (glob={args.cnn_glob})")
        sys.exit(1)
    print(f"CNN 文件: {len(cnn_files)} 个 ({cnn_files[0].name} ...)")

    # ---- 加载 OCS ----
    ocs_rows = load_ocs_predictions(ocs_path)
    ocs_map = {(round(r["yaw_true"], 6), round(r["pitch_true"], 6)): r for r in ocs_rows}

    # ---- 解析 beta ----
    parts = args.beta_sweep.split(":")
    beta_start, beta_step, beta_end = float(parts[0]), float(parts[1]), float(parts[2])
    betas = np.round(np.arange(beta_start, beta_end + beta_step * 0.5, beta_step), 6)

    # ---- 逐 seed 处理 ----
    all_seeds = []  # [{seed, sweep_rows, pred_data}]

    for cnn_path in cnn_files:
        # 提取 seed
        fname = cnn_path.stem
        seed = None
        for part in fname.split("_"):
            if part.startswith("seed") and part[4:].isdigit():
                seed = int(part[4:])
                break
        if seed is None:
            seed = fname

        cnn_rows = load_cnn_predictions(cnn_path)
        cnn_map = {(round(r["yaw_true"], 6), round(r["pitch_true"], 6)): r for r in cnn_rows}

        # 对齐：取两个 map 的公共 key
        common_keys = sorted(set(ocs_map.keys()) & set(cnn_map.keys()))
        if not common_keys:
            print(f"  [SKIP] seed={seed}: 无公共样本")
            continue

        yaw_true = np.array([ocs_map[k]["yaw_true"] for k in common_keys])
        pitch_true = np.array([ocs_map[k]["pitch_true"] for k in common_keys])
        vec_ocs = angle_to_vec(
            [ocs_map[k]["yaw_pred"] for k in common_keys],
            [ocs_map[k]["pitch_pred"] for k in common_keys])
        vec_cnn = angle_to_vec(
            [cnn_map[k]["yaw_pred"] for k in common_keys],
            [cnn_map[k]["pitch_pred"] for k in common_keys])

        print(f"  seed={seed}: {len(common_keys)} matched")

        # beta sweep
        sweep_rows = []
        for beta in betas:
            vec_fused = beta * vec_ocs + (1.0 - beta) * vec_cnn
            yaw_pred, pitch_pred = vec_to_angle(vec_fused)
            m, _ = compute_metrics(yaw_pred, pitch_pred, yaw_true, pitch_true)
            m["beta"] = round(beta, 4)
            sweep_rows.append(m)

        # 计算 beta=0 和 beta=1 的 sanity
        m_cnn, _ = compute_metrics(
            *vec_to_angle(vec_cnn), yaw_true, pitch_true)
        m_ocs, _ = compute_metrics(
            *vec_to_angle(vec_ocs), yaw_true, pitch_true)

        all_seeds.append({
            "seed": seed,
            "n_match": len(common_keys),
            "sweep": sweep_rows,
            "yaw_true": yaw_true,
            "pitch_true": pitch_true,
            "vec_ocs": vec_ocs,
            "vec_cnn": vec_cnn,
            "m_cnn": m_cnn,
            "m_ocs": m_ocs,
        })

    if not all_seeds:
        print("[ERROR] 无可用 seed")
        sys.exit(1)

    N = len(all_seeds)
    print(f"\n处理 {N} 个 seeds, {len(betas)} betas each")

    # ---- 输出目录 ----
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = out_root / f"run_{stamp}_{args.tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"输出: {out_dir}")

    # ---- 保存 per-seed sweep CSV ----
    for e in all_seeds:
        seed = e["seed"]
        with open(out_dir / f"beta_sweep_seed{seed}.csv", "w", encoding="utf-8", newline="") as f:
            fields = ["beta", "mean", "std", "median", "p90", "p95",
                       "hit5", "hit10", "yaw_mean", "pitch_mean"]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in e["sweep"]:
                w.writerow({k: r[k] for k in fields})

    # ---- 汇总 ----
    metric_keys = ["mean", "std", "median", "p90", "p95",
                   "hit5", "hit10", "yaw_mean", "pitch_mean"]
    summary_rows = []
    for i_beta, beta in enumerate(betas):
        row = {"beta": round(beta, 4)}
        for k in metric_keys:
            vals = [e["sweep"][i_beta][k] for e in all_seeds]
            row[f"{k}_mean"] = float(np.mean(vals))
            row[f"{k}_std"] = float(np.std(vals))
        summary_rows.append(row)

    with open(out_dir / "beta_sweep_summary.csv", "w", encoding="utf-8", newline="") as f:
        fields = list(summary_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(summary_rows)

    # ---- 最佳 beta ----
    best_mean_idx = int(np.argmin([r["mean_mean"] for r in summary_rows]))
    best_hit5_idx = int(np.argmax([r["hit5_mean"] for r in summary_rows]))
    best_mean = summary_rows[best_mean_idx]
    best_hit5 = summary_rows[best_hit5_idx]

    print(f"\nBest beta (mean): {best_mean['beta']:.2f}  "
          f"mean={best_mean['mean_mean']:.2f}±{best_mean['mean_std']:.2f}°  "
          f"Hit5={best_mean['hit5_mean']:.1%}")
    print(f"Best beta (Hit5): {best_hit5['beta']:.2f}  "
          f"mean={best_hit5['mean_mean']:.2f}±{best_hit5['mean_std']:.2f}°  "
          f"Hit5={best_hit5['hit5_mean']:.1%}")

    # ---- Endpoint sanity ----
    beta0_idx = int(np.argmin(np.abs(betas - 0.0)))
    beta1_idx = int(np.argmin(np.abs(betas - 1.0)))
    s0 = summary_rows[beta0_idx]
    s1 = summary_rows[beta1_idx]
    print(f"\n[Sanity] beta=0.00 (CNN-only): mean={s0['mean_mean']:.2f}° Hit5={s0['hit5_mean']:.1%}")
    print(f"[Sanity] beta=1.00 (OCS-only): mean={s1['mean_mean']:.2f}° Hit5={s1['hit5_mean']:.1%}")

    # ---- Sanity 对照已知基线 ----
    # CNN image-only: mean=12.38, Hit5=26.1%
    # OCS MLP all_raw: mean=3.98, Hit5=90.7%
    print(f"[Sanity-expected] CNN image-only: mean=12.38° Hit5=26.1%")
    print(f"[Sanity-expected] OCS MLP all_raw: mean=3.98° Hit5=90.7%")

    # ---- 保存最佳融合预测 (per seed) ----
    for e in all_seeds:
        seed = e["seed"]
        vec_fused = best_mean["beta"] * e["vec_ocs"] + (1.0 - best_mean["beta"]) * e["vec_cnn"]
        yaw_pred, pitch_pred = vec_to_angle(vec_fused)
        err = angular_err_deg(yaw_pred, pitch_pred, e["yaw_true"], e["pitch_true"])
        with open(out_dir / f"predictions_best_seed{seed}.csv", "w", encoding="utf-8",
                  newline="") as f:
            w = csv.writer(f)
            w.writerow(["yaw_true", "pitch_true", "yaw_fused", "pitch_fused",
                         "yaw_ocs", "pitch_ocs", "yaw_cnn", "pitch_cnn",
                         "angle_err_fused", "angle_err_ocs", "angle_err_cnn"])
            ocs_pred_yaw, ocs_pred_pitch = vec_to_angle(e["vec_ocs"])
            cnn_pred_yaw, cnn_pred_pitch = vec_to_angle(e["vec_cnn"])
            err_ocs = angular_err_deg(ocs_pred_yaw, ocs_pred_pitch, e["yaw_true"], e["pitch_true"])
            err_cnn = angular_err_deg(cnn_pred_yaw, cnn_pred_pitch, e["yaw_true"], e["pitch_true"])
            for i in range(e["n_match"]):
                w.writerow([
                    f"{e['yaw_true'][i]:.4f}", f"{e['pitch_true'][i]:.4f}",
                    f"{yaw_pred[i]:.4f}", f"{pitch_pred[i]:.4f}",
                    f"{ocs_pred_yaw[i]:.4f}", f"{ocs_pred_pitch[i]:.4f}",
                    f"{cnn_pred_yaw[i]:.4f}", f"{cnn_pred_pitch[i]:.4f}",
                    f"{err[i]:.4f}", f"{err_ocs[i]:.4f}", f"{err_cnn[i]:.4f}",
                ])

    # ---- config_used.json ----
    config = {
        "description": "CNN+OCS prediction-level late fusion (Step 11e-B1)",
        "ocs_run": str(ocs_run),
        "ocs_file": ocs_path.name,
        "cnn_run": str(cnn_run),
        "cnn_glob": args.cnn_glob,
        "n_seeds": N,
        "n_test_per_seed": all_seeds[0]["n_match"],
        "fusion_formula": "vec_fused = beta * vec_ocs + (1-beta) * vec_img",
        "beta_sweep": args.beta_sweep,
        "best_beta_by_mean": best_mean["beta"],
        "best_mean": best_mean["mean_mean"],
        "best_hit5_by_mean": best_mean["hit5_mean"],
        "best_beta_by_hit5": best_hit5["beta"],
        "best_hit5": best_hit5["hit5_mean"],
    }
    with open(out_dir / "config_used.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # ---- summary.json ----
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "best_by_mean": {
                "beta": best_mean["beta"],
                "mean": f"{best_mean['mean_mean']:.2f}±{best_mean['mean_std']:.2f}°",
                "p90": f"{best_mean['p90_mean']:.2f}°",
                "hit5": f"{best_mean['hit5_mean']:.1%}",
                "hit10": f"{best_mean['hit10_mean']:.1%}",
            },
            "endpoints": {
                "cnn_only_beta0": {
                    "mean": f"{s0['mean_mean']:.2f}°",
                    "hit5": f"{s0['hit5_mean']:.1%}",
                },
                "ocs_only_beta1": {
                    "mean": f"{s1['mean_mean']:.2f}°",
                    "hit5": f"{s1['hit5_mean']:.1%}",
                },
            },
            "seeds": [e["seed"] for e in all_seeds],
        }, f, indent=2, ensure_ascii=False)

    # ---- ablation_table.md ----
    lines = [
        "# CNN+OCS Late Fusion · Ablation Table",
        "",
        f"| beta | mean | median | p90 | Hit5 | Hit10 | yaw_mean | pitch_mean |",
        f"|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary_rows:
        lines.append(
            f"| {r['beta']:.2f} "
            f"| {r['mean_mean']:.2f}±{r['mean_std']:.2f}° "
            f"| {r['median_mean']:.2f}° "
            f"| {r['p90_mean']:.2f}° "
            f"| {r['hit5_mean']:.1%} "
            f"| {r['hit10_mean']:.1%} "
            f"| {r['yaw_mean_mean']:.2f}° "
            f"| {r['pitch_mean_mean']:.2f}° |")
    lines += [
        "",
        "## Endpoint Sanity",
        f"- beta=0.00 (CNN-only): mean={s0['mean_mean']:.2f}°, Hit5={s0['hit5_mean']:.1%}",
        f"- beta=1.00 (OCS-only): mean={s1['mean_mean']:.2f}°, Hit5={s1['hit5_mean']:.1%}",
        f"- Expected CNN-only: mean=12.38°, Hit5=26.1%",
        f"- Expected OCS all_raw: mean=3.98°, Hit5=90.7%",
        "",
        "## Best",
        f"- Best by mean: beta={best_mean['beta']:.2f}, mean={best_mean['mean_mean']:.2f}°, Hit5={best_mean['hit5_mean']:.1%}",
        f"- Best by Hit5: beta={best_hit5['beta']:.2f}, mean={best_hit5['mean_mean']:.2f}°, Hit5={best_hit5['hit5_mean']:.1%}",
        "",
    ]
    with open(out_dir / "ablation_table.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[OK] 完成")
    print(f"  beta_sweep_summary.csv")
    print(f"  ablation_table.md")
    print(f"  summary.json")


if __name__ == "__main__":
    main()

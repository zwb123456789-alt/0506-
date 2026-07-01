#!/usr/bin/env python3
"""
e45a_recompute_c2.py — 1C-E45a: C2 只读推理复算（13 configs × 5 fold = 65 runs）

目的
----
在已训练的 C2 OCS-only checkpoint 上，1:1 复现训练时的 strict-holdout test
评估口径，收集逐样本预测，并设置"先行门"：用 train_c2_screening 里**原始**
compute_metrics 复算 exact-bin yaw_acc / pitch_acc / yaw_circular_mae，与各折
result.json 的 final_metrics['test'] 对齐。先行门未过则不写扩展判据。

本脚本只读 + 只写新结果文件，**不训练**。

复算口径（照抄训练代码，勿改）
------------------------------
- 模型：train_c2_screening.OCSOnlyMLP(in_dim=feature_dim, hidden_dim=128)。
  feature_dim 取自该折 result.json 顶层 'feature_dim'（已核验 baseline_4dim=4，
  net.0.weight=(128,4)）。
- 特征：enhanced_ocs_dataset.EnhancedOCSDataset(npz, config_name, test_records,
  normalize_params, feature_defs)。
  · 特征列 = npz[config_name]（已按 config 存好），不手动选列。
  · 归一化 = 该折 result.json 的 normalization_params.mean/std（train-only），
    应用 (X-mean)/(std+1e-8)。checkpoint 不含 norm，必须从 result.json 取。
  · 真值 bin 不在 manifest，而在 evaluate 内由 (yaw_deg/5).long()、
    ((pitch_deg+90)/5).long() **截断**得到（与 C3 的 round 不同）。
- DataLoader：batch_size=32, shuffle=False。
- 指标：直接复用 train_c2_screening.evaluate / compute_metrics。
- 13 个 c2_participant=True config × 5 fold = 65（排除 constant_check_1d）。
- 每折 split = e25_multifold_yawblock/split_manifest_circ_yawblock_fold{k}.json，
  test split 即 result.json split_info 记录的 manifest（已核验 n_test=555 等）。

依赖
----
- 运行环境：ocs_sim（含 torch / numpy）。
- import：把 06_v0.4_code/07_training 加入 sys.path。

运行示例（由主控执行，本脚本不自跑）
------------------------------------
    ocs_sim/python e45a_recompute_c2.py --gate-only
    ocs_sim/python e45a_recompute_c2.py
    ocs_sim/python e45a_recompute_c2.py --configs baseline_4dim R_ratio_2d --folds 0
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

# ── 路径 ──────────────────────────────────────────────
THIS = Path(__file__).resolve()
PROJECT_ROOT = THIS.parents[2]
TRAINING_DIR = PROJECT_ROOT / "06_v0.4_code" / "07_training"
sys.path.insert(0, str(TRAINING_DIR))

import train_c2_screening as tc        # noqa: E402  复用 OCSOnlyMLP/evaluate/metrics
from enhanced_ocs_dataset import (     # noqa: E402
    EnhancedOCSDataset,
    load_feature_definitions,
    get_c2_participant_configs,
)

NPZ_PATH = PROJECT_ROOT / "v0.4_results/04_ocs_features/enhanced_ocs_features.npz"
DEFINITIONS_PATH = PROJECT_ROOT / "v0.4_results/04_ocs_features/feature_definitions.json"
C2_DIR = PROJECT_ROOT / "v0.4_results/05_c2_screening"
E25_DIR = PROJECT_ROOT / "v0.4_results/03_training_baseline/e25_multifold_yawblock"
OUT_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup"

N_FOLDS = 5
GATE_ATOL_ACC = 1e-3
GATE_ATOL_MAE = 5e-2


def resolve_manifest_path(raw, fold):
    """优先用 result.json 记录的 split_manifest_path（Windows 反斜杠相对路径，
    相对 PROJECT_ROOT 解析），回退到 E25 约定路径。"""
    if raw:
        rel = raw.replace("\\", "/")
        # split_info 里通常是绝对 Windows 路径；取末段相对片段兜底
        p = (PROJECT_ROOT / rel).resolve()
        if p.exists():
            return p
        # 兜底：从字符串里截 e25.../split_manifest_circ_yawblock_foldK.json
        marker = "e25_multifold_yawblock"
        if marker in rel:
            tail = rel[rel.index(marker):]
            p2 = (PROJECT_ROOT / "v0.4_results/03_training_baseline" / tail).resolve()
            if p2.exists():
                return p2
    return (E25_DIR / f"split_manifest_circ_yawblock_fold{fold}.json").resolve()


def recompute_one(config_name, fold, feature_defs, device):
    """复算单个 (config, fold)。返回 (gate_row, samples_dict)。"""
    result_path = C2_DIR / config_name / f"{config_name}_fold{fold}_result.json"
    with open(result_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    feature_dim = int(result["feature_dim"])
    norm = result["normalization_params"]
    norm_params = {
        "mean": np.asarray(norm["mean"], dtype=np.float32),
        "std": np.asarray(norm["std"], dtype=np.float32),
    }
    target = result["final_metrics"]["test"]

    manifest_path = resolve_manifest_path(
        result.get("split_info", {}).get("split_manifest_path"), fold)
    with open(manifest_path, "r", encoding="utf-8") as f:
        test_records = json.load(f)["test"]

    # 模型重建 + 加载 checkpoint
    ckpt_path = C2_DIR / config_name / f"{config_name}_fold{fold}_checkpoint.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = tc.OCSOnlyMLP(in_dim=feature_dim,
                          hidden_dim=tc.C2_FIXED_PROTOCOL["hidden_dim"]).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    # test dataset（用该折 train-only mean/std 归一化）
    test_ds = EnhancedOCSDataset(NPZ_PATH, config_name, test_records,
                                 norm_params, feature_defs)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False,
                             num_workers=0, pin_memory=(device.type == "cuda"))

    crit_yaw = torch.nn.CrossEntropyLoss()
    crit_pitch = torch.nn.CrossEntropyLoss()

    # ── 先行门：复用原始 evaluate（内部做 (deg/5).long() 截断）──
    metrics = tc.evaluate(model, test_loader, device, crit_yaw, crit_pitch)

    # ── 逐样本收集（顺序对齐 test_records；真值 bin 与 evaluate 同口径）──
    yaw_pred, yaw_true, pitch_pred, pitch_true = [], [], [], []
    with torch.no_grad():
        for X, y in test_loader:
            X = X.to(device)
            yt = (y[:, 0] / 5.0).long()
            pt = ((y[:, 1] + 90.0) / 5.0).long()
            yl, pl = model(X)
            yaw_pred.append(yl.argmax(dim=1).cpu().numpy())
            pitch_pred.append(pl.argmax(dim=1).cpu().numpy())
            yaw_true.append(yt.numpy())
            pitch_true.append(pt.numpy())

    record_ids = np.array([r["record_id"] for r in test_records], dtype=object)
    samples = {
        "record_id": record_ids,
        "yaw_pred_bin": np.concatenate(yaw_pred).astype(np.int64),
        "yaw_true_bin": np.concatenate(yaw_true).astype(np.int64),
        "pitch_pred_bin": np.concatenate(pitch_pred).astype(np.int64),
        "pitch_true_bin": np.concatenate(pitch_true).astype(np.int64),
    }

    def cmp(a, b, atol):
        return abs(float(a) - float(b)) <= atol

    pass_yaw = cmp(metrics["yaw_acc"], target["yaw_acc"], GATE_ATOL_ACC)
    pass_pit = cmp(metrics["pitch_acc"], target["pitch_acc"], GATE_ATOL_ACC)
    pass_mae = cmp(metrics["yaw_circular_mae_deg"],
                   target["yaw_circular_mae_deg"], GATE_ATOL_MAE)
    gate_pass = bool(pass_yaw and pass_pit and pass_mae)

    gate_row = {
        "channel": "C2",
        "config_name": config_name,
        "fold": fold,
        "feature_dim": feature_dim,
        "manifest": str(manifest_path),
        "n_samples_recomputed": int(metrics["n_samples"]),
        "n_samples_target": target.get("n_samples"),
        "recomp_yaw_acc": float(metrics["yaw_acc"]),
        "target_yaw_acc": float(target["yaw_acc"]),
        "recomp_pitch_acc": float(metrics["pitch_acc"]),
        "target_pitch_acc": float(target["pitch_acc"]),
        "recomp_yaw_cmae": float(metrics["yaw_circular_mae_deg"]),
        "target_yaw_cmae": float(target["yaw_circular_mae_deg"]),
        "pass_yaw_acc": pass_yaw,
        "pass_pitch_acc": pass_pit,
        "pass_yaw_cmae": pass_mae,
        "gate_pass": gate_pass,
    }
    return gate_row, samples


def main():
    ap = argparse.ArgumentParser(description="1C-E45a C2 只读推理复算（不训练）")
    ap.add_argument("--configs", nargs="+", default=None,
                    help="指定 config_name 子集（默认全部 13 个 c2_participant）")
    ap.add_argument("--folds", nargs="+", type=int, default=list(range(N_FOLDS)))
    ap.add_argument("--gate-only", action="store_true")
    ap.add_argument("--device", type=str, default="auto",
                    choices=["auto", "cpu", "cuda"])
    ap.add_argument("--outdir", type=str, default=str(OUT_DIR))
    args = ap.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    feature_defs = load_feature_definitions(DEFINITIONS_PATH)
    c2_configs = get_c2_participant_configs(feature_defs)
    config_names = [c["config_name"] for c in c2_configs]  # 13 个，按 config_id 排序
    if args.configs:
        config_names = [c for c in config_names if c in args.configs]

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    samples_dir = outdir / "c2_samples"
    if not args.gate_only:
        samples_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 64)
    print("1C-E45a C2 recompute (READ-ONLY, no training)")
    print(f"Device: {device} | configs={len(config_names)} folds={args.folds} "
          f"gate_only={args.gate_only}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"Output: {outdir}")
    print("=" * 64)

    gate_rows = []
    all_pass = True
    for config_name in config_names:
        for fold in args.folds:
            t0 = time.time()
            gate_row, samples = recompute_one(config_name, fold, feature_defs, device)
            gate_rows.append(gate_row)
            mark = "PASS" if gate_row["gate_pass"] else "*** FAIL ***"
            print(f"[{mark}] C2 {config_name:24s} fold{fold} "
                  f"yaw {gate_row['recomp_yaw_acc']:.4f}/{gate_row['target_yaw_acc']:.4f} "
                  f"pit {gate_row['recomp_pitch_acc']:.4f}/{gate_row['target_pitch_acc']:.4f} "
                  f"cmae {gate_row['recomp_yaw_cmae']:.3f}/{gate_row['target_yaw_cmae']:.3f} "
                  f"({time.time()-t0:.1f}s)")
            if not gate_row["gate_pass"]:
                all_pass = False
            if not args.gate_only:
                npz_path = samples_dir / f"c2_{config_name}_fold{fold}_samples.npz"
                np.savez_compressed(npz_path, **samples)

    gate_json = outdir / "c2_gate_alignment.json"
    with open(gate_json, "w", encoding="utf-8") as f:
        json.dump({"all_pass": all_pass, "n_runs": len(gate_rows),
                   "rows": gate_rows, "atol_acc": GATE_ATOL_ACC,
                   "atol_mae": GATE_ATOL_MAE,
                   "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
                  f, indent=2, ensure_ascii=False)
    gate_csv = outdir / "c2_gate_alignment.csv"
    with open(gate_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(gate_rows[0].keys()))
        w.writeheader()
        w.writerows(gate_rows)

    print("-" * 64)
    print(f"C2 gate ALL_PASS={all_pass}  ({len(gate_rows)} runs)  -> {gate_json}")
    if not all_pass:
        print("[BLOCK] 先行门未全部通过：扩展判据不应在此基础上生成。")
        return 2
    if args.gate_only:
        print("[gate-only] 逐样本未落盘。")
    else:
        print(f"逐样本 npz -> {samples_dir}")
    print("[DONE] C2 recompute complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
e45a_recompute_c3.py — 1C-E45a: C3 只读推理复算（image_only / joint × 5 fold）

目的
----
在已训练的 C3 checkpoint 上，1:1 复现训练时的 strict-holdout test 评估口径，
收集逐样本预测，并设置"先行门"：用训练脚本里**原始** compute_all_metrics
复算 exact-bin yaw_acc / pitch_acc / yaw_circular_mae，与 detail JSON 的
final_eval['test_primary'] 对齐。先行门未过则不写扩展判据。

本脚本只读 + 只写新结果文件，**不训练**。

复算口径（照抄训练代码，勿改）
------------------------------
- 模型：train_baseline.OCSImageModel，结构由 checkpoint['mode'] 决定；
  joint 的 ocs_dim=4（已核验 ocs_encoder.net.0.weight=(128,4)）。
- 数据：dataset.OCSImageDataset(train_manifest, split="test", mode=mode)
  · 图像走 PNG（rec["png_path"]，转灰度 /255），不是 EXR。
  · OCS 4-dim 直接取 manifest 字段，**不归一化**。
  · 真值 bin = manifest 的 yaw_idx / pitch_idx（split 阶段 round 得来）。
- DataLoader：batch_size=32, shuffle=False（与训练 test_loaders 一致）。
- 指标：直接复用 train_baseline.evaluate / compute_all_metrics / circular_yaw_mae。
- 每折 train_manifest = e25_multifold_yawblock/split_manifest_circ_yawblock_fold{k}.json
  （已从各折 e21_fix01_baseline_results.json 的 train_manifest 字段核验）。
  test_primary 即来自该 manifest 的 split="test"（strict holdout）。

依赖
----
- 运行环境：ocs_sim（含 torch / numpy / pillow）。
- 训练模块可 import：通过把 06_v0.4_code/07_training 加入 sys.path
  （train_baseline.py 顶层有 `from dataset import ...`，必须 07_training 在 path 上）。

运行示例（由主控执行，本脚本不自跑）
------------------------------------
    # 仅先行门（对齐校验，不写扩展逐样本/汇总）
    ocs_sim/python e45a_recompute_c3.py --gate-only

    # 全量复算（先行门 + 逐样本落盘）
    ocs_sim/python e45a_recompute_c3.py

    # 只跑某些 mode / fold
    ocs_sim/python e45a_recompute_c3.py --modes image_only --folds 0 1
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
# 09_diagnostics -> parents[1] = 06_v0.4_code ; parents[2] = V04_PROJECT
THIS = Path(__file__).resolve()
PROJECT_ROOT = THIS.parents[2]
TRAINING_DIR = PROJECT_ROOT / "06_v0.4_code" / "07_training"

# 关键：把 07_training 放在 sys.path 前部，使 train_baseline 顶层
# `from dataset import OCSImageDataset` 能解析（dataset.py 在 07_training）。
sys.path.insert(0, str(TRAINING_DIR))

import train_baseline as tb            # noqa: E402  复用模型/evaluate/metrics
from dataset import OCSImageDataset    # noqa: E402  复用 C3 Dataset

# C3 五折 checkpoint 根目录
C3_IMAGE_DIR = PROJECT_ROOT / "v0.4_results/06_c3_preflight/c3_image_formal_5fold"
C3_JOINT_DIR = PROJECT_ROOT / "v0.4_results/06_c3_preflight/c3_joint_formal_5fold"

# 每折 strict-holdout manifest（已核验 = 各折 train_manifest）
E25_DIR = PROJECT_ROOT / "v0.4_results/03_training_baseline/e25_multifold_yawblock"

OUT_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup"

MODE_TO_DIR = {"image_only": C3_IMAGE_DIR, "joint": C3_JOINT_DIR}

# 先行门容差（acc/cmae 复算与 JSON 记录的绝对差阈值）
GATE_ATOL_ACC = 1e-3
GATE_ATOL_MAE = 5e-2


def resolve_manifest_path(raw, fold):
    """优先用各折 baseline_results.json 记录的 train_manifest；
    其 Windows 反斜杠相对路径相对 PROJECT_ROOT 解析。回退到 E25 约定路径。"""
    if raw:
        rel = raw.replace("\\", "/")
        p = (PROJECT_ROOT / rel).resolve()
        if p.exists():
            return p
    p2 = E25_DIR / f"split_manifest_circ_yawblock_fold{fold}.json"
    return p2.resolve()


def load_fold_target(mode, fold):
    """读该折 detail JSON 的 final_eval['test_primary']['metrics'] 作为先行门目标，
    并读 baseline_results.json 拿 train_manifest。"""
    fold_dir = MODE_TO_DIR[mode] / f"fold{fold}"
    detail_name = f"e21_fix01_detail_{mode}.json"
    with open(fold_dir / detail_name, "r", encoding="utf-8") as f:
        detail = json.load(f)
    target = detail["final_eval"]["test_primary"]["metrics"]

    train_manifest = None
    br = fold_dir / "e21_fix01_baseline_results.json"
    if br.exists():
        with open(br, "r", encoding="utf-8") as f:
            train_manifest = json.load(f).get("train_manifest")
    return target, train_manifest, fold_dir


def recompute_one(mode, fold, device):
    """复算单个 (mode, fold)。返回 (gate_row, samples_dict)。"""
    target, train_manifest_raw, fold_dir = load_fold_target(mode, fold)
    manifest_path = resolve_manifest_path(train_manifest_raw, fold)

    ckpt_path = fold_dir / f"checkpoint_{mode}.pt"
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    ckpt_mode = ckpt.get("mode", mode)
    if ckpt_mode != mode:
        print(f"  [WARN] checkpoint mode={ckpt_mode} != requested {mode}")

    # 重建模型（ocs_dim=4 与 checkpoint 权重一致）
    model = tb.OCSImageModel(mode=ckpt_mode, ocs_dim=4).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    # strict-holdout test split
    test_ds = OCSImageDataset(str(manifest_path), split="test", mode=ckpt_mode)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False,
                             num_workers=0, pin_memory=(device.type == "cuda"))

    # ── 先行门：复用训练脚本原始 evaluate（口径完全一致）──
    metrics, _per_yaw, _per_pitch, _conf = tb.evaluate(model, test_loader, device)

    # ── 逐样本收集（再跑一遍，shuffle=False 顺序稳定）──
    yaw_pred, yaw_true, pitch_pred, pitch_true, record_ids = [], [], [], [], []
    with torch.no_grad():
        for batch in test_loader:
            ids = batch["record_id"]  # list[str]
            b = {k: (v.to(device) if isinstance(v, torch.Tensor) else v)
                 for k, v in batch.items()}
            yl, pl = model(b)
            yaw_pred.append(yl.argmax(dim=1).cpu().numpy())
            pitch_pred.append(pl.argmax(dim=1).cpu().numpy())
            yaw_true.append(b["yaw_bin"].cpu().numpy())
            pitch_true.append(b["pitch_bin"].cpu().numpy())
            record_ids.extend(list(ids))

    samples = {
        "record_id": np.array(record_ids, dtype=object),
        "yaw_pred_bin": np.concatenate(yaw_pred).astype(np.int64),
        "yaw_true_bin": np.concatenate(yaw_true).astype(np.int64),
        "pitch_pred_bin": np.concatenate(pitch_pred).astype(np.int64),
        "pitch_true_bin": np.concatenate(pitch_true).astype(np.int64),
    }

    # ── 先行门对齐 ──
    def cmp(a, b, atol):
        return abs(float(a) - float(b)) <= atol

    pass_yaw = cmp(metrics["yaw_acc"], target["yaw_acc"], GATE_ATOL_ACC)
    pass_pit = cmp(metrics["pitch_acc"], target["pitch_acc"], GATE_ATOL_ACC)
    pass_mae = cmp(metrics["yaw_circular_mae_deg"],
                   target["yaw_circular_mae_deg"], GATE_ATOL_MAE)
    gate_pass = bool(pass_yaw and pass_pit and pass_mae)

    gate_row = {
        "channel": "C3",
        "mode": mode,
        "fold": fold,
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
    ap = argparse.ArgumentParser(description="1C-E45a C3 只读推理复算（不训练）")
    ap.add_argument("--modes", nargs="+", default=["image_only", "joint"],
                    choices=["image_only", "joint"])
    ap.add_argument("--folds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    ap.add_argument("--gate-only", action="store_true",
                    help="只跑先行门对齐，不写逐样本 npz")
    ap.add_argument("--device", type=str, default="auto",
                    choices=["auto", "cpu", "cuda"])
    ap.add_argument("--outdir", type=str, default=str(OUT_DIR))
    args = ap.parse_args()

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    samples_dir = outdir / "c3_samples"
    if not args.gate_only:
        samples_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 64)
    print("1C-E45a C3 recompute (READ-ONLY, no training)")
    print(f"Device: {device} | modes={args.modes} folds={args.folds} "
          f"gate_only={args.gate_only}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"Output: {outdir}")
    print("=" * 64)

    gate_rows = []
    all_pass = True
    for mode in args.modes:
        for fold in args.folds:
            t0 = time.time()
            gate_row, samples = recompute_one(mode, fold, device)
            gate_rows.append(gate_row)
            mark = "PASS" if gate_row["gate_pass"] else "*** FAIL ***"
            print(f"[{mark}] C3 {mode} fold{fold} "
                  f"yaw_acc {gate_row['recomp_yaw_acc']:.4f}/{gate_row['target_yaw_acc']:.4f} "
                  f"pitch_acc {gate_row['recomp_pitch_acc']:.4f}/{gate_row['target_pitch_acc']:.4f} "
                  f"cmae {gate_row['recomp_yaw_cmae']:.3f}/{gate_row['target_yaw_cmae']:.3f} "
                  f"({time.time()-t0:.1f}s)")
            if not gate_row["gate_pass"]:
                all_pass = False

            if not args.gate_only:
                npz_path = samples_dir / f"c3_{mode}_fold{fold}_samples.npz"
                np.savez_compressed(npz_path, **samples)

    # 先行门对齐表落盘
    gate_json = outdir / "c3_gate_alignment.json"
    with open(gate_json, "w", encoding="utf-8") as f:
        json.dump({"all_pass": all_pass, "rows": gate_rows,
                   "atol_acc": GATE_ATOL_ACC, "atol_mae": GATE_ATOL_MAE,
                   "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")},
                  f, indent=2, ensure_ascii=False)
    gate_csv = outdir / "c3_gate_alignment.csv"
    with open(gate_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(gate_rows[0].keys()))
        w.writeheader()
        w.writerows(gate_rows)

    print("-" * 64)
    print(f"C3 gate ALL_PASS={all_pass}  -> {gate_json}")
    if not all_pass:
        print("[BLOCK] 先行门未全部通过：扩展判据不应在此基础上生成。")
        return 2
    if args.gate_only:
        print("[gate-only] 逐样本未落盘（去掉 --gate-only 以收集逐样本）。")
    else:
        print(f"逐样本 npz -> {samples_dir}")
    print("[DONE] C3 recompute complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

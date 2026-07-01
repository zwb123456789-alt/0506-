#!/usr/bin/env python3
"""
e45a_postprocess.py — 1C-E45a: 逐样本预测的扩展判据后处理（只读 npz + 只写汇总）

输入
----
e45a_recompute_c3.py / e45a_recompute_c2.py 落盘的逐样本 npz：
  <outdir>/c3_samples/c3_{mode}_fold{k}_samples.npz
  <outdir>/c2_samples/c2_{config}_fold{k}_samples.npz
每个 npz 含 record_id, yaw_pred_bin, yaw_true_bin, pitch_pred_bin, pitch_true_bin。

扩展判据（在 exact-bin 先行门已 PASS 的前提下才有意义）
--------------------------------------------------------
- coarse-bin accuracy：把 5°/bin 的预测/真值映射到 30°(=6 bins) 与 45°(=9 bins)
  的粗 bin，yaw 用 circular 折叠，pitch 线性，算 coarse 命中率。
- within-k（k=1,2,3,6 bins）：yaw 用 circular 距离 min(d,72-d)，pitch 用线性距离。
- yaw circular MAE（度）：min(d,72-d)*5 的均值；并给分位数分布。
- yaw confusion matrix：完整 72×72（true×pred），circular 边界天然正确
  （bin 索引本身已是 0..71 的环；矩阵按整数 bin 计数即可）。

口径说明
--------
- yaw n_bins=72, step=5°；pitch n_bins=37, step=5°（对应 -90..+90）。
- coarse yaw: 30° -> 每粗 bin 6 个细 bin，共 12 粗 bin（circular）；
  45° -> 每粗 bin 9 个细 bin，共 8 粗 bin（circular）。
  采用 coarse = (fine_bin // width) 并对 yaw 取模 (72//width)。
- coarse pitch: 同样 floor 除，但不取模（线性）。

本脚本只读 npz + 只写汇总，**不加载任何模型、不做推理**。

运行示例（由主控执行）
----------------------
    ocs_sim/python e45a_postprocess.py                  # C2+C3 全部
    ocs_sim/python e45a_postprocess.py --channels C3
    ocs_sim/python e45a_postprocess.py --no-confusion   # 跳过 72x72 矩阵落盘
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

THIS = Path(__file__).resolve()
PROJECT_ROOT = THIS.parents[2]
OUT_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup"

N_YAW = 72
N_PITCH = 37
STEP_DEG = 5.0
WITHIN_KS = [1, 2, 3, 6]
COARSE_YAW_WIDTHS = {"30deg": 6, "45deg": 9}   # 细 bin 数 / 粗 bin
COARSE_PITCH_WIDTHS = {"30deg": 6, "45deg": 9}


def circular_dist(pred, true, n=N_YAW):
    d = np.abs(pred - true)
    return np.minimum(d, n - d)


def compute_extended(yp, yt, pp, pt):
    """从逐样本 bin 数组算扩展判据（不含混淆矩阵）。"""
    n = len(yt)
    yaw_cd = circular_dist(yp, yt, N_YAW)
    pitch_d = np.abs(pp - pt)

    out = {
        "n_samples": int(n),
        "yaw_exact_acc": float((yaw_cd == 0).mean()),
        "pitch_exact_acc": float((pitch_d == 0).mean()),
        "yaw_circular_mae_deg": float(yaw_cd.mean() * STEP_DEG),
        "pitch_mae_deg": float(pitch_d.mean() * STEP_DEG),
    }

    # within-k
    for k in WITHIN_KS:
        out[f"yaw_within_{k}_bins_rate"] = float((yaw_cd <= k).mean())
        out[f"pitch_within_{k}_bins_rate"] = float((pitch_d <= k).mean())

    # yaw CMAE 分布（度）
    cmae_deg = yaw_cd * STEP_DEG
    out["yaw_cmae_deg_distribution"] = {
        "min": float(cmae_deg.min()),
        "p25": float(np.percentile(cmae_deg, 25)),
        "median": float(np.percentile(cmae_deg, 50)),
        "p75": float(np.percentile(cmae_deg, 75)),
        "p90": float(np.percentile(cmae_deg, 90)),
        "max": float(cmae_deg.max()),
        "mean": float(cmae_deg.mean()),
        "std": float(cmae_deg.std()),
    }

    # coarse-bin accuracy
    for name, w in COARSE_YAW_WIDTHS.items():
        n_coarse = N_YAW // w
        cyp = (yp // w) % n_coarse
        cyt = (yt // w) % n_coarse
        out[f"yaw_coarse_{name}_acc"] = float((cyp == cyt).mean())
    for name, w in COARSE_PITCH_WIDTHS.items():
        cpp = pp // w
        cpt = pt // w
        out[f"pitch_coarse_{name}_acc"] = float((cpp == cpt).mean())

    return out, yaw_cd


def yaw_confusion_matrix(yp, yt):
    """完整 72×72 true×pred 计数矩阵（bin 已是 0..71 的环，直接计数即 circular 正确）。"""
    cm = np.zeros((N_YAW, N_YAW), dtype=np.int64)
    np.add.at(cm, (yt, yp), 1)
    return cm


def load_samples(npz_path):
    d = np.load(npz_path, allow_pickle=True)
    return (d["yaw_pred_bin"], d["yaw_true_bin"],
            d["pitch_pred_bin"], d["pitch_true_bin"])


C3_RE = re.compile(r"c3_(?P<mode>image_only|joint)_fold(?P<fold>\d+)_samples\.npz")
C2_RE = re.compile(r"c2_(?P<config>.+)_fold(?P<fold>\d+)_samples\.npz")


def process_channel(channel, samples_dir, write_confusion, outdir):
    rows = []
    cm_dir = outdir / f"{channel.lower()}_confusion"
    if write_confusion:
        cm_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(samples_dir.glob("*.npz"))
    if not files:
        print(f"[WARN] {channel}: 未找到逐样本 npz（{samples_dir}）。"
              f"请先运行复算脚本（去掉 --gate-only）。")
        return rows

    for npz_path in files:
        m = (C3_RE.match(npz_path.name) if channel == "C3"
             else C2_RE.match(npz_path.name))
        if not m:
            continue
        yp, yt, pp, pt = load_samples(npz_path)
        ext, yaw_cd = compute_extended(yp, yt, pp, pt)

        row = {"channel": channel}
        if channel == "C3":
            row["mode"] = m.group("mode")
            tag = f"c3_{m.group('mode')}_fold{m.group('fold')}"
        else:
            row["config_name"] = m.group("config")
            tag = f"c2_{m.group('config')}_fold{m.group('fold')}"
        row["fold"] = int(m.group("fold"))

        # 展平扩展指标（嵌套分布单独存）
        dist = ext.pop("yaw_cmae_deg_distribution")
        row.update(ext)
        for k, v in dist.items():
            row[f"yaw_cmae_{k}"] = v
        rows.append(row)

        if write_confusion:
            cm = yaw_confusion_matrix(yp, yt)
            np.savez_compressed(cm_dir / f"{tag}_yaw_cm.npz",
                                confusion=cm, n_yaw=N_YAW)
    return rows


def write_table(rows, outdir, channel):
    if not rows:
        return
    base = outdir / f"{channel.lower()}_extended_metrics"
    with open(str(base) + ".json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    # CSV：用所有 row 的 key 并集
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(str(base) + ".csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  {channel} extended -> {base}.json / .csv ({len(rows)} runs)")


def main():
    ap = argparse.ArgumentParser(description="1C-E45a 扩展判据后处理（只读 npz）")
    ap.add_argument("--channels", nargs="+", default=["C2", "C3"],
                    choices=["C2", "C3"])
    ap.add_argument("--no-confusion", action="store_true",
                    help="不落盘 72x72 yaw 混淆矩阵")
    ap.add_argument("--indir", type=str, default=str(OUT_DIR),
                    help="复算脚本的输出根目录（含 c2_samples/ c3_samples/）")
    ap.add_argument("--outdir", type=str, default=str(OUT_DIR))
    args = ap.parse_args()

    indir = Path(args.indir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print("=" * 64)
    print("1C-E45a postprocess (READ-ONLY samples -> extended metrics)")
    print(f"In:  {indir}")
    print(f"Out: {outdir}  | channels={args.channels} "
          f"confusion={not args.no_confusion}")
    print("=" * 64)

    for ch in args.channels:
        samples_dir = indir / ("c3_samples" if ch == "C3" else "c2_samples")
        rows = process_channel(ch, samples_dir, not args.no_confusion, outdir)
        write_table(rows, outdir, ch)

    print("[DONE] postprocess complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

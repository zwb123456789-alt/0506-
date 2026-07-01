#!/usr/bin/env python3
"""
split_dataset.py —— 1C-E19: train/val/test 数据切分脚本

功能：从 fullrun OCS manifest 生成可复现的 train/val/test split manifest，
      记录各切分的姿态分布，输出 split manifest JSON。

使用：
    python split_dataset.py
    python split_dataset.py --seed 42 --train-ratio 0.8 --val-ratio 0.1
    python split_dataset.py --method yaw_block  # 备选：按 yaw 块切分

输出：
    v0.4_results/01_fullrun/postprocess/split_manifest.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

# ── 路径 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "v0.4_results" / "01_fullrun" / "postprocess"
OCS_MANIFEST_PATH = RESULTS_DIR / "ocs_manifest_v0_4_fullrun.json"
IMAGE_MANIFEST_PATH = RESULTS_DIR / "image_manifest_v0_4_fullrun.json"
SPLIT_OUTPUT_PATH = RESULTS_DIR / "split_manifest.json"


def load_manifests():
    """加载 OCS 和 image manifest"""
    with open(OCS_MANIFEST_PATH, "r", encoding="utf-8") as f:
        ocs = json.load(f)
    with open(IMAGE_MANIFEST_PATH, "r", encoding="utf-8") as f:
        img = json.load(f)
    return ocs, img


def build_record_table(ocs_manifest, img_manifest):
    """从两个 manifest 构建统一的 record 表（按 record_id 对齐）"""
    ocs_records = {r["record_id"]: r for r in ocs_manifest["records"]}
    img_records = {r["record_id"]: r for r in img_manifest["records"]}

    common_ids = sorted(set(ocs_records.keys()) & set(img_records.keys()))
    if len(common_ids) != len(ocs_records) or len(common_ids) != len(img_records):
        print(f"[WARNING] record_id mismatch: OCS={len(ocs_records)}, "
              f"image={len(img_records)}, common={len(common_ids)}")

    table = []
    for rid in common_ids:
        o = ocs_records[rid]
        i = img_records[rid]
        table.append({
            "record_id": rid,
            "yaw_deg": o["yaw_deg"],
            "pitch_deg": o["pitch_deg"],
            "yaw_idx": int(round(o["yaw_deg"] / 5.0)),
            "pitch_idx": int(round((o["pitch_deg"] + 90.0) / 5.0)),
            "ocs_total": o["ocs_total"],
            "ocs_jinshuzhuti": o["ocs_per_part"]["jinshuzhuti"],
            "ocs_taiyangnengban": o["ocs_per_part"]["taiyangnengban"],
            "ocs_yinshenban": o["ocs_per_part"]["yinshenban"],
            "png_path": i["png_path"],
            "exr_linear_path": i["exr_linear_path"],
            "is_clean": i["is_clean"],
        })
    return table


def split_random(table, train_ratio=0.8, val_ratio=0.1, seed=42):
    """
    随机分层切分：按 pitch 分层以维持俯仰分布，固定 seed。
    返回 (train, val, test) 三个 record 列表。
    """
    rng = np.random.default_rng(seed)
    pitch_bins = {}
    for rec in table:
        pitch_bins.setdefault(rec["pitch_deg"], []).append(rec)

    train, val, test = [], [], []
    for pitch, recs in sorted(pitch_bins.items()):
        idx = rng.permutation(len(recs))
        n_train = max(1, int(len(recs) * train_ratio))
        n_val = max(1, int(len(recs) * val_ratio))
        train.extend([recs[i] for i in idx[:n_train]])
        val.extend([recs[i] for i in idx[n_train:n_train + n_val]])
        test.extend([recs[i] for i in idx[n_train + n_val:]])

    # Shuffle each split
    rng.shuffle(train)
    rng.shuffle(val)
    rng.shuffle(test)
    return train, val, test


def split_yaw_block(table, train_ratio=0.8, val_ratio=0.1):
    """
    按 yaw 连续块切分：将 yaw 排序后按比例分为 train/val/test 连续块。
    用于测试对未见几何方向的泛化能力。
    """
    yaw_sorted = sorted(set(r["yaw_deg"] for r in table))
    n_yaw = len(yaw_sorted)
    n_train_yaw = max(1, int(n_yaw * train_ratio))
    n_val_yaw = max(1, int(n_yaw * val_ratio))

    train_yaws = set(yaw_sorted[:n_train_yaw])
    val_yaws = set(yaw_sorted[n_train_yaw:n_train_yaw + n_val_yaw])
    test_yaws = set(yaw_sorted[n_train_yaw + n_val_yaw:])

    train = [r for r in table if r["yaw_deg"] in train_yaws]
    val = [r for r in table if r["yaw_deg"] in val_yaws]
    test = [r for r in table if r["yaw_deg"] in test_yaws]
    return train, val, test


def split_circ_yaw_block(table, n_folds=5, fold=0, val_size=7):
    """
    k-fold circular yaw_block split (E24/E25)。

    将全部 72 个 yaw bin 在圆上等距分布为 k 个 test 窗口，每折 test
    窗口互斥、合计覆盖全部 yaw bin。val 取 test 窗口低 yaw 侧相邻的
    val_size 个 yaw bin。train 为其余 yaw bin。

    Args:
        table: record 列表
        n_folds: 折数 (default 5)
        fold: 当前折编号 (0..n_folds-1)
        val_size: val yaw bin 数 (default 7)

    Returns:
        (train, val, test) 三个 record 列表
    """
    yaw_sorted = sorted(set(r["yaw_idx"] for r in table))  # 0..71
    n_yaw = len(yaw_sorted)

    if n_yaw != 72:
        raise ValueError(f"Expected 72 yaw bins, got {n_yaw}")

    # 每折 test bin 分配：尽量均匀，前 (n_yaw % n_folds) 折多 1 个
    test_sizes = [n_yaw // n_folds + (1 if i < n_yaw % n_folds else 0)
                  for i in range(n_folds)]

    # Fold 的 test 起始 bin
    start_bin = sum(test_sizes[:fold]) % n_yaw
    end_bin = (start_bin + test_sizes[fold]) % n_yaw

    # 构建 test yaw bin 集合 (circular)
    if end_bin > start_bin:
        test_bins = set(range(start_bin, end_bin))
    else:
        test_bins = set(range(start_bin, n_yaw)) | set(range(0, end_bin))

    # val yaw bin 集合: test 窗口低 yaw 侧相邻 val_size 个 bin (circular)
    val_start = (start_bin - val_size) % n_yaw
    if val_start < start_bin:
        val_bins = set(range(val_start, start_bin))
    else:
        val_bins = set(range(val_start, n_yaw)) | set(range(0, start_bin))

    train_bins = set(yaw_sorted) - test_bins - val_bins

    # 按 yaw_idx 筛选
    train = [r for r in table if r["yaw_idx"] in train_bins]
    val = [r for r in table if r["yaw_idx"] in val_bins]
    test = [r for r in table if r["yaw_idx"] in test_bins]

    return train, val, test


def compute_split_stats(train, val, test):
    """计算各切分的分布统计"""
    def stats(recs, name):
        yaws = [r["yaw_deg"] for r in recs]
        pitches = [r["pitch_deg"] for r in recs]
        return {
            "split": name,
            "n": len(recs),
            "yaw_min": float(np.min(yaws)),
            "yaw_max": float(np.max(yaws)),
            "yaw_unique": len(set(yaws)),
            "pitch_min": float(np.min(pitches)),
            "pitch_max": float(np.max(pitches)),
            "pitch_unique": len(set(pitches)),
            "n_non_clean": sum(1 for r in recs if not r["is_clean"]),
        }
    return [stats(train, "train"), stats(val, "val"), stats(test, "test")]


def build_split_manifest(train, val, test, method, seed, stats_list):
    """构建输出 manifest 结构"""
    def slim(rec):
        return {
            "record_id": rec["record_id"],
            "yaw_deg": rec["yaw_deg"],
            "pitch_deg": rec["pitch_deg"],
            "yaw_idx": rec["yaw_idx"],
            "pitch_idx": rec["pitch_idx"],
            "ocs_total": rec["ocs_total"],
            "ocs_jinshuzhuti": rec["ocs_jinshuzhuti"],
            "ocs_taiyangnengban": rec["ocs_taiyangnengban"],
            "ocs_yinshenban": rec["ocs_yinshenban"],
            "png_path": rec["png_path"],
            "exr_linear_path": rec["exr_linear_path"],
        }

    return {
        "version": "v0.4_1C-E19_split_manifest",
        "method": method,
        "seed": seed,
        "train_ratio": len(train) / (len(train) + len(val) + len(test)),
        "val_ratio": len(val) / (len(train) + len(val) + len(test)),
        "test_ratio": len(test) / (len(train) + len(val) + len(test)),
        "n_total": len(train) + len(val) + len(test),
        "split_stats": stats_list,
        "train": [slim(r) for r in train],
        "val": [slim(r) for r in val],
        "test": [slim(r) for r in test],
    }


def main():
    parser = argparse.ArgumentParser(description="1C-E19/E25 数据切分")
    parser.add_argument("--method", choices=["random", "yaw_block", "circ_yaw_block"],
                        default="random",
                        help="切分方法 (default: random; E25: circ_yaw_block)")
    parser.add_argument("--seed", type=int, default=42, help="随机种子 (default: 42)")
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--n-folds", type=int, default=5,
                        help="circ_yaw_block 折数 (default: 5)")
    parser.add_argument("--fold", type=int, default=0,
                        help="circ_yaw_block 当前折编号 0..n_folds-1")
    parser.add_argument("--output", type=str, default=str(SPLIT_OUTPUT_PATH))
    args = parser.parse_args()

    if args.method == "circ_yaw_block":
        is_circ = True
        out_dir = (RESULTS_DIR.parents[1] / "03_training_baseline"
                   / "e25_multifold_yawblock")
        os.makedirs(out_dir, exist_ok=True)
        output_path = str(
            out_dir / f"split_manifest_circ_yawblock_fold{args.fold}.json"
        )
    else:
        is_circ = False
        assert args.train_ratio + args.val_ratio < 1.0, \
            "train_ratio + val_ratio must be < 1.0"
        output_path = args.output

    print("=" * 60)
    print("1C-E19/E25 数据切分脚本")
    print(f"方法: {args.method}")
    if is_circ:
        print(f"折数: {args.n_folds}, 当前折: {args.fold}")
    else:
        print(f"种子: {args.seed}")
        print(f"比例: train={args.train_ratio}, val={args.val_ratio}, "
              f"test={1 - args.train_ratio - args.val_ratio:.2f}")
    print("=" * 60)

    # 加载
    ocs, img = load_manifests()
    table = build_record_table(ocs, img)
    print(f"\n[LOAD] OCS records: {len(ocs['records'])}")
    print(f"[LOAD] Image records: {len(img['records'])}")
    print(f"[LOAD] Aligned table: {len(table)}")

    # 切分
    if args.method == "random":
        train, val, test = split_random(table, args.train_ratio,
                                        args.val_ratio, args.seed)
    elif args.method == "yaw_block":
        train, val, test = split_yaw_block(table, args.train_ratio,
                                           args.val_ratio)
    else:  # circ_yaw_block
        train, val, test = split_circ_yaw_block(table, args.n_folds, args.fold)

    print(f"\n[SPLIT] train: {len(train)}")
    print(f"[SPLIT] val:   {len(val)}")
    print(f"[SPLIT] test:  {len(test)}")
    print(f"[SPLIT] sum:   {len(train) + len(val) + len(test)}")

    # 统计
    stats_list = compute_split_stats(train, val, test)
    print("\n[STATS]")
    for s in stats_list:
        print(f"  {s['split']}: n={s['n']}, "
              f"yaw=[{s['yaw_min']:.0f}, {s['yaw_max']:.0f}] "
              f"({s['yaw_unique']} unique), "
              f"pitch=[{s['pitch_min']:.0f}, {s['pitch_max']:.0f}] "
              f"({s['pitch_unique']} unique), "
              f"non_clean={s['n_non_clean']}")

    # 输出
    manifest = build_split_manifest(train, val, test, args.method,
                                    args.seed, stats_list)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[DONE] Split manifest -> {output_path}")
    print(f"[DONE] 总切分数: {manifest['n_total']}")


if __name__ == "__main__":
    main()

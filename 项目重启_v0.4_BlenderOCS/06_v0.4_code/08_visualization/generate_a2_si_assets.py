"""
1C-A2-GEN: P0 必要 SI 资产生成脚本
====================================
生成 Figure S3（Training curves）、Figure S4（Overlap diagnostic）和 Table S3（C3 per-fold detail）

数据源：
- C2: v0.4_results/05_c2_screening/*/checkpoint.pt (history)
- C3: v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold*/checkpoint_*.pt (history)
- Split: v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_*.json
- C3 metrics: v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
import torch
import csv

# ============================================================
# 0. Paths
# ============================================================
PROJECT_ROOT = Path("d:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS")
C2_DIR = PROJECT_ROOT / "v0.4_results/05_c2_screening"
C3_DIR = PROJECT_ROOT / "v0.4_results/06_c3_preflight"
SPLIT_DIR = PROJECT_ROOT / "v0.4_results/03_training_baseline/e25_multifold_yawblock"
C3_METRICS = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json"
OUT_DIR = PROJECT_ROOT / "06_v0.4_code/08_visualization"

# ============================================================
# 1. Figure S3: Training Curves
# ============================================================

def load_c2_history(config_names):
    """Load training history from C2 checkpoints for selected configs."""
    histories = {}
    for cfg in config_names:
        cfg_dir = C2_DIR / cfg
        cfg_histories = []
        for fold_id in range(5):
            ckpt_path = cfg_dir / f"{cfg}_fold{fold_id}_checkpoint.pt"
            if ckpt_path.exists():
                ckpt = torch.load(ckpt_path, map_location='cpu')
                cfg_histories.append(ckpt['history'])
        histories[cfg] = cfg_histories
    return histories


def load_c3_history():
    """Load training history from C3 checkpoints (image_only and joint)."""
    histories = {'image_only': [], 'joint': []}

    # C3 image_only 5 folds
    img_dir = C3_DIR / "c3_image_formal_5fold"
    for fold_id in range(5):
        ckpt_path = img_dir / f"fold{fold_id}" / "checkpoint_image_only.pt"
        if ckpt_path.exists():
            ckpt = torch.load(ckpt_path, map_location='cpu')
            print(f"  DEBUG C3 image fold{fold_id} checkpoint keys: {list(ckpt.keys())}")
            if 'history' in ckpt:
                print(f"  DEBUG C3 image fold{fold_id} history type: {type(ckpt['history'])}")
            histories['image_only'].append(ckpt['history'])
        else:
            print(f"  WARNING: C3 image fold{fold_id} checkpoint not found at {ckpt_path}")

    # C3 joint 5 folds
    joint_dir = C3_DIR / "c3_joint_formal_5fold"
    for fold_id in range(5):
        ckpt_path = joint_dir / f"fold{fold_id}" / "checkpoint_joint.pt"
        if ckpt_path.exists():
            ckpt = torch.load(ckpt_path, map_location='cpu')
            print(f"  DEBUG C3 joint fold{fold_id} checkpoint keys: {list(ckpt.keys())}")
            if 'history' in ckpt:
                print(f"  DEBUG C3 joint fold{fold_id} history type: {type(ckpt['history'])}")
            histories['joint'].append(ckpt['history'])
        else:
            print(f"  WARNING: C3 joint fold{fold_id} checkpoint not found at {ckpt_path}")

    return histories


def make_figure_s3():
    """Generate Figure S3: Training curves for C2 representative configs + C3 all folds."""
    # 选择代表性 C2 configs
    c2_configs = ["baseline_4dim", "M6_all_nongeo_13d", "L_logratio_3d"]
    c2_labels = {
        "baseline_4dim": "C2 baseline (4-dim)",
        "M6_all_nongeo_13d": "C2 M6 all-nongeo (13-dim)",
        "L_logratio_3d": "C2 L logratio (3-dim)"
    }

    print("[S3] Loading C2 training histories...")
    c2_hist = load_c2_history(c2_configs)

    # Debug: check structure
    for cfg in c2_configs:
        if cfg in c2_hist and len(c2_hist[cfg]) > 0:
            hist = c2_hist[cfg][0]
            print(f"  DEBUG {cfg} fold0 history type: {type(hist)}")
            if isinstance(hist, dict):
                print(f"  DEBUG {cfg} fold0 history keys: {list(hist.keys())}")
                if 'val' in hist:
                    print(f"  DEBUG {cfg} fold0 val type: {type(hist['val'])}")
                    if isinstance(hist['val'], list) and len(hist['val']) > 0:
                        print(f"  DEBUG {cfg} fold0 val[0] type: {type(hist['val'][0])}")

    print("[S3] Loading C3 training histories...")
    c3_hist = load_c3_history()

    # 创建 2x2 子图：C2 loss, C2 acc, C3 loss, C3 acc
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Figure S3: Training Curves — Convergence Evidence",
                 fontsize=14, fontweight="bold", y=0.995)

    # --- C2 Training Loss ---
    ax = axes[0, 0]
    for cfg in c2_configs:
        for fold_idx, hist in enumerate(c2_hist[cfg]):
            train_hist = hist['train']
            epochs = [h['epoch'] for h in train_hist]
            losses = [h['loss'] for h in train_hist]
            ax.plot(epochs, losses, alpha=0.6, linewidth=1.0,
                   label=f"{c2_labels[cfg]} fold{fold_idx}" if fold_idx == 0 else "")
    ax.set_xlabel("Epoch", fontsize=10)
    ax.set_ylabel("Training Loss", fontsize=10)
    ax.set_title("(a) C2 OCS-only Training Loss", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)

    # --- C2 Validation Accuracy (pitch) ---
    ax = axes[0, 1]
    for cfg in c2_configs:
        for fold_idx, hist in enumerate(c2_hist[cfg]):
            val_hist = hist['val']
            epochs = [h['epoch'] for h in val_hist]
            pitch_acc = [h['pitch_acc'] * 100 for h in val_hist]
            ax.plot(epochs, pitch_acc, alpha=0.6, linewidth=1.0,
                   label=f"{c2_labels[cfg]} fold{fold_idx}" if fold_idx == 0 else "")
    ax.set_xlabel("Epoch", fontsize=10)
    ax.set_ylabel("Validation Pitch Accuracy (%)", fontsize=10)
    ax.set_title("(b) C2 OCS-only Validation Pitch Accuracy", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)

    # --- C3 Training Loss ---
    ax = axes[1, 0]
    for fold_idx, hist in enumerate(c3_hist['image_only']):
        train_hist = hist['train']
        epochs = [h['epoch'] for h in train_hist]
        losses = [h['loss'] for h in train_hist]
        ax.plot(epochs, losses, alpha=0.6, linewidth=1.0, color='blue',
               label="C3 image_only" if fold_idx == 0 else "")
    for fold_idx, hist in enumerate(c3_hist['joint']):
        train_hist = hist['train']
        epochs = [h['epoch'] for h in train_hist]
        losses = [h['loss'] for h in train_hist]
        ax.plot(epochs, losses, alpha=0.6, linewidth=1.0, color='green',
               label="C3 joint" if fold_idx == 0 else "")
    ax.set_xlabel("Epoch", fontsize=10)
    ax.set_ylabel("Training Loss", fontsize=10)
    ax.set_title("(c) C3 Image/Joint Training Loss", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)

    # --- C3 Validation Accuracy (pitch) ---
    ax = axes[1, 1]
    for fold_idx, hist in enumerate(c3_hist['image_only']):
        # C3 val history 是 dict，需要使用 'primary' 键
        val_hist = hist['val']['primary'] if isinstance(hist['val'], dict) else hist['val']
        epochs = [h['epoch'] for h in val_hist]
        pitch_acc = [h['pitch_acc'] * 100 for h in val_hist]
        ax.plot(epochs, pitch_acc, alpha=0.6, linewidth=1.0, color='blue',
               label="C3 image_only" if fold_idx == 0 else "")
    for fold_idx, hist in enumerate(c3_hist['joint']):
        val_hist = hist['val']['primary'] if isinstance(hist['val'], dict) else hist['val']
        epochs = [h['epoch'] for h in val_hist]
        pitch_acc = [h['pitch_acc'] * 100 for h in val_hist]
        ax.plot(epochs, pitch_acc, alpha=0.6, linewidth=1.0, color='green',
               label="C3 joint" if fold_idx == 0 else "")
    ax.set_xlabel("Epoch", fontsize=10)
    ax.set_ylabel("Validation Pitch Accuracy (%)", fontsize=10)
    ax.set_title("(d) C3 Image/Joint Validation Pitch Accuracy", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.3)

    plt.tight_layout()
    for fmt in ["png", "pdf"]:
        outpath = OUT_DIR / f"FigureS3_training_curves_draft.{fmt}"
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        print(f"[OK] Figure S3 ({fmt}): {outpath}")
    plt.close()
    print("[OK] Figure S3 done.")


# ============================================================
# 2. Figure S4: Overlap Diagnostic
# ============================================================

def load_split_metadata(fold_id):
    """Load split metadata for one fold."""
    split_path = SPLIT_DIR / f"split_manifest_circ_yawblock_fold{fold_id}.json"
    with open(split_path, 'r') as f:
        return json.load(f)


def make_figure_s4():
    """Generate Figure S4: Overlap diagnostic showing train/test yaw-bin holdout."""
    print("[S4] Loading split metadata...")

    # 加载 fold 0 作为代表
    meta = load_split_metadata(0)

    # 提取 train/val/test yaw bin coverage
    train_yaws = set()
    val_yaws = set()
    test_yaws = set()

    for item in meta['train']:
        train_yaws.add(item['yaw_idx'])
    for item in meta['val']:
        val_yaws.add(item['yaw_idx'])
    for item in meta['test']:
        test_yaws.add(item['yaw_idx'])

    # 创建 72 bins 的覆盖矩阵
    n_yaw = 72
    coverage = np.zeros((3, n_yaw))  # 3 rows: train, val, test

    for yaw_bin in range(n_yaw):
        if yaw_bin in train_yaws:
            coverage[0, yaw_bin] = 1
        if yaw_bin in val_yaws:
            coverage[1, yaw_bin] = 2
        if yaw_bin in test_yaws:
            coverage[2, yaw_bin] = 3

    # 绘制热图
    fig, ax = plt.subplots(figsize=(16, 4))
    im = ax.imshow(coverage, aspect='auto', cmap='tab10', vmin=0, vmax=3)

    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['Train', 'Val', 'Test'], fontsize=11)
    ax.set_xlabel('Yaw Bin (0-71, 5° per bin)', fontsize=11)
    ax.set_title('Figure S4: Overlap Diagnostic — Train/Val/Test Yaw-Bin Strict Holdout (Fold 0)',
                 fontsize=12, fontweight='bold')

    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2, 3])
    cbar.set_ticklabels(['None', 'Train', 'Val', 'Test'])

    # 标注统计
    ax.text(0.5, -0.25,
            f"Train: {len(train_yaws)} bins | Val: {len(val_yaws)} bins | Test: {len(test_yaws)} bins | "
            f"Union: {len(train_yaws | val_yaws | test_yaws)} bins (expected: 72)",
            transform=ax.transAxes, ha='center', fontsize=10, style='italic')

    plt.tight_layout()
    for fmt in ["png", "pdf"]:
        outpath = OUT_DIR / f"FigureS4_overlap_diagnostic_draft.{fmt}"
        plt.savefig(outpath, dpi=300, bbox_inches="tight")
        print(f"[OK] Figure S4 ({fmt}): {outpath}")
    plt.close()
    print("[OK] Figure S4 done.")


# ============================================================
# 3. Table S3: C3 Per-Fold Detail
# ============================================================

def make_table_s3():
    """Generate Table S3: C3 per-fold detail (10 rows)."""
    print("[S3] Loading C3 extended metrics...")

    with open(C3_METRICS, 'r') as f:
        c3_data = json.load(f)

    # 提取 10 rows: image_only 5 folds + joint 5 folds
    rows = []
    for entry in c3_data:
        row = {
            'fold_id': entry['fold'],
            'mode': entry['mode'],
            'yaw_exact_acc': entry['yaw_exact_acc'],
            'yaw_circular_mae_deg': entry['yaw_circular_mae_deg'],
            'yaw_within_3_bins_rate': entry['yaw_within_3_bins_rate'],
            'yaw_within_6_bins_rate': entry['yaw_within_6_bins_rate'],
            'yaw_coarse_45deg_acc': entry['yaw_coarse_45deg_acc'],
            'pitch_exact_acc': entry['pitch_exact_acc'],
            'pitch_within_3_bins_rate': entry['pitch_within_3_bins_rate'],
            'n_samples': entry['n_samples']
        }
        rows.append(row)

    # 排序：image_only 0-4, joint 0-4
    rows_sorted = sorted(rows, key=lambda x: (x['mode'], x['fold_id']))

    # 写 CSV
    csv_path = OUT_DIR / "TableS3_c3_per_fold_detail_draft.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_sorted[0].keys()))
        writer.writeheader()
        writer.writerows(rows_sorted)
    print(f"[OK] Table S3 CSV: {csv_path}")

    # 写 Markdown preview (first 10 rows)
    md_lines = []
    md_lines.append("## Table S3: C3 Per-Fold Detail (10 folds)\n")
    md_lines.append("| Fold | Mode | Yaw Exact (%) | Yaw CMAE (deg) | Yaw Within-3 (%) | Yaw Within-6 (%) | Yaw Coarse45 (%) | Pitch Exact (%) | Pitch Within-3 (%) | N Samples |")
    md_lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for row in rows_sorted:
        md_lines.append(
            f"| {row['fold_id']} | {row['mode']} | "
            f"{row['yaw_exact_acc']*100:.2f} | {row['yaw_circular_mae_deg']:.1f} | "
            f"{row['yaw_within_3_bins_rate']*100:.2f} | {row['yaw_within_6_bins_rate']*100:.2f} | "
            f"{row['yaw_coarse_45deg_acc']*100:.2f} | {row['pitch_exact_acc']*100:.2f} | "
            f"{row['pitch_within_3_bins_rate']*100:.2f} | {row['n_samples']} |"
        )

    md_lines.append("")
    md_lines.append("_Note: This table provides per-fold variability details for C3 image_only and joint modes._")

    md_path = OUT_DIR / "TableS3_c3_per_fold_detail_draft.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
    print(f"[OK] Table S3 MD: {md_path}")

    print("\n" + "=" * 80)
    print("\n".join(md_lines[:15]))  # 打印前 15 行预览
    print("=" * 80)


# ============================================================
# 4. Main
# ============================================================

def main():
    print("[A2-GEN] Starting P0 SI asset generation...")

    print("\n[A2-GEN] Generating Figure S3 (Training curves)...")
    make_figure_s3()

    print("\n[A2-GEN] Generating Figure S4 (Overlap diagnostic)...")
    make_figure_s4()

    print("\n[A2-GEN] Generating Table S3 (C3 per-fold detail)...")
    make_table_s3()

    print("\n[A2-GEN] All P0 SI assets generated. Done.")


if __name__ == "__main__":
    main()

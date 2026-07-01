"""
P0 FIX02: 补齐图表与表格化产物
R97 要求：
1. OCS yaw-yaw cosine distance heatmap
2. C3 image_only/joint 聚合 confusion map
3. pitch=0 pseudo-light-curve probe 图
4. 将 json 产物转为 csv/md 表格
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import json
import csv
from pathlib import Path

# 路径
PROJECT_ROOT = Path("d:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS")
DIAG_DIR = PROJECT_ROOT / "v0.4_results/08_p0_diagnostics"
OUTPUT_DIR = DIAG_DIR

print(f"Working directory: {DIAG_DIR}")

# ============================================================
# 1. OCS yaw-yaw cosine distance heatmap
# ============================================================
print("\n=== Generating OCS distance heatmap ===")

data = np.load(DIAG_DIR / "ocs_yaw_distance_matrices.npz")
cos_dist = data['cos_dist']
yaw_counts = data['yaw_counts']

fig, ax = plt.subplots(figsize=(12, 10))
im = ax.imshow(cos_dist, cmap='viridis', aspect='auto', origin='lower')
ax.set_xlabel('Yaw bin (0-71, 0°-355°)', fontsize=12)
ax.set_ylabel('Yaw bin (0-71, 0°-355°)', fontsize=12)
ax.set_title('OCS 4D Signature: Yaw-Yaw Cosine Distance Matrix', fontsize=14)
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Cosine Distance (1 - cos_sim)', fontsize=11)

# 标注统计
valid_dists = cos_dist[~np.isnan(cos_dist)]
stats_text = f"mean={valid_dists.mean():.4f}, min={valid_dists.min():.4f}, max={valid_dists.max():.4f}"
ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "p0_ocs_yaw_distance_heatmap.png", dpi=150)
plt.close()
print(f"Saved: p0_ocs_yaw_distance_heatmap.png")

# ============================================================
# 2. C3 confusion maps (image_only + joint)
# ============================================================
print("\n=== Generating C3 confusion maps ===")

C3_CONFUSION_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_confusion"

def load_aggregate_confusion(conf_dir, pattern, n_folds=5):
    cms = []
    for fold in range(n_folds):
        fname = pattern.format(fold=fold)
        fpath = conf_dir / fname
        if fpath.exists():
            d = np.load(fpath, allow_pickle=True)
            cm = d['confusion']
            cms.append(cm)
    if not cms:
        return None
    total = np.stack(cms).sum(axis=0)
    return total

c3_img_cm = load_aggregate_confusion(C3_CONFUSION_DIR, "c3_image_only_fold{fold}_yaw_cm.npz")
c3_joint_cm = load_aggregate_confusion(C3_CONFUSION_DIR, "c3_joint_fold{fold}_yaw_cm.npz")

# 绘制两个 confusion map
fig, axes = plt.subplots(1, 2, figsize=(20, 9))

for ax, cm, title in zip(axes, [c3_img_cm, c3_joint_cm],
                          ['C3 image_only (5-fold aggregated)',
                           'C3 joint (5-fold aggregated)']):
    # 对数尺度以增强可视化
    cm_log = np.log10(cm + 1)
    im = ax.imshow(cm_log, cmap='Blues', aspect='auto', origin='lower')
    ax.set_xlabel('Predicted yaw bin (0-71)', fontsize=11)
    ax.set_ylabel('True yaw bin (0-71)', fontsize=11)
    ax.set_title(title, fontsize=13)
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('log10(count + 1)', fontsize=10)

    # 标注对角线统计
    diag_sum = np.diag(cm).sum()
    total_samples = cm.sum()
    diag_nonzero = (np.diag(cm) > 0).sum()
    stats = f"total={int(total_samples)}\ndiag_sum={int(diag_sum)}\ndiag_nonzero_bins={diag_nonzero}/72"
    ax.text(0.02, 0.98, stats, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6))

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "p0_c3_confusion_maps.png", dpi=150)
plt.close()
print(f"Saved: p0_c3_confusion_maps.png")

# ============================================================
# 3. Pitch=0 pseudo-light-curve 图
# ============================================================
print("\n=== Generating pitch=0 pseudo-light-curve plot ===")

lc_data = np.load(DIAG_DIR / "pseudo_light_curve_pitch0.npz")
yaw_deg = lc_data['yaw_deg']
ocs_total = lc_data['ocs_total']
ocs_jinshuzhuti = lc_data['ocs_jinshuzhuti']
ocs_taiyangnengban = lc_data['ocs_taiyangnengban']
ocs_yinshenban = lc_data['ocs_yinshenban']

fig, axes = plt.subplots(2, 1, figsize=(14, 8))

# 上图：总强度
ax = axes[0]
ax.plot(yaw_deg, ocs_total, marker='o', markersize=3, linewidth=1.5, label='OCS Total')
ax.set_xlabel('Yaw (deg)', fontsize=11)
ax.set_ylabel('OCS Total Intensity', fontsize=11)
ax.set_title('Pitch=0° Pseudo-Light-Curve: OCS Total', fontsize=13)
ax.grid(True, alpha=0.3)
ax.legend()

# 下图：三个分量
ax = axes[1]
ax.plot(yaw_deg, ocs_jinshuzhuti, marker='s', markersize=2, linewidth=1, label='Jinshuzhuti', alpha=0.8)
ax.plot(yaw_deg, ocs_taiyangnengban, marker='^', markersize=2, linewidth=1, label='Taiyangnengban', alpha=0.8)
ax.plot(yaw_deg, ocs_yinshenban, marker='v', markersize=2, linewidth=1, label='Yinshenban', alpha=0.8)
ax.set_xlabel('Yaw (deg)', fontsize=11)
ax.set_ylabel('OCS Component Intensity', fontsize=11)
ax.set_title('Pitch=0° Pseudo-Light-Curve: OCS Components', fontsize=13)
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "p0_pseudo_light_curve_pitch0.png", dpi=150)
plt.close()
print(f"Saved: p0_pseudo_light_curve_pitch0.png")

# ============================================================
# 4. 表格化产物：JSON -> CSV/MD
# ============================================================
print("\n=== Converting JSON to CSV/MD ===")

# 4.1 nearest_yaw_pairs.json -> csv
with open(DIAG_DIR / "nearest_yaw_pairs.json", 'r') as f:
    nearest_pairs = json.load(f)

with open(OUTPUT_DIR / "nearest_yaw_pairs.csv", 'w', newline='', encoding='utf-8') as csvf:
    if nearest_pairs:
        writer = csv.DictWriter(csvf, fieldnames=nearest_pairs[0].keys())
        writer.writeheader()
        writer.writerows(nearest_pairs)
print(f"Saved: nearest_yaw_pairs.csv ({len(nearest_pairs)} rows)")

# 4.2 top_confusion_pairs.json -> csv
with open(DIAG_DIR / "top_confusion_pairs.json", 'r') as f:
    confusion_data = json.load(f)

for key in ['c3_image_only', 'c3_joint', 'c2_baseline_4dim']:
    pairs = confusion_data[key]
    fname = f"top_confusion_pairs_{key}.csv"
    with open(OUTPUT_DIR / fname, 'w', newline='', encoding='utf-8') as csvf:
        if pairs:
            writer = csv.DictWriter(csvf, fieldnames=pairs[0].keys())
            writer.writeheader()
            writer.writerows(pairs)
    print(f"Saved: {fname} ({len(pairs)} rows)")

# 4.3 distance_confusion_overlap.json -> csv
with open(DIAG_DIR / "distance_confusion_overlap.json", 'r') as f:
    overlap = json.load(f)

with open(OUTPUT_DIR / "distance_confusion_overlap.csv", 'w', newline='', encoding='utf-8') as csvf:
    if overlap:
        writer = csv.DictWriter(csvf, fieldnames=overlap[0].keys())
        writer.writeheader()
        writer.writerows(overlap)
print(f"Saved: distance_confusion_overlap.csv ({len(overlap)} rows)")

# 4.4 pseudo_sequence_similarity.json -> md 表格
with open(DIAG_DIR / "pseudo_sequence_similarity.json", 'r') as f:
    seq_sim = json.load(f)

md_lines = ["# Pseudo-Sequence Similarity Summary", "", "## Sequence 5-frame window", ""]
md_lines.append("| Yaw Distance Group | N Samples | Mean Cosine Similarity | Std |")
md_lines.append("|---|---|---|---|")
for group, stats in seq_sim['sequence_5frame_window'].items():
    n = stats['n']
    mean_sim = f"{stats['mean_cos_sim']:.4f}" if stats['mean_cos_sim'] is not None else "N/A"
    std_sim = f"{stats['std_cos_sim']:.4f}" if stats['std_cos_sim'] is not None else "N/A"
    md_lines.append(f"| {group} | {n} | {mean_sim} | {std_sim} |")

md_lines.append("")
md_lines.append("## Single-frame baseline")
md_lines.append("")
md_lines.append("| Group | N Samples | Mean Cosine Similarity |")
md_lines.append("|---|---|---|")
for group, stats in seq_sim['single_frame'].items():
    md_lines.append(f"| {group} | {stats['n']} | {stats['mean_cos_sim']:.4f} |")

md_lines.append("")
md_lines.append(f"**Note**: {seq_sim['note']}")

with open(OUTPUT_DIR / "pseudo_sequence_similarity.md", 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))
print(f"Saved: pseudo_sequence_similarity.md")

# ============================================================
# 5. 补充统计：对角线 exact count 明确
# ============================================================
print("\n=== Computing exact diagonal statistics ===")

diag_stats = []
for name, cm in [('C3_image_only', c3_img_cm), ('C3_joint', c3_joint_cm)]:
    diag = np.diag(cm)
    diag_stats.append({
        'config': name,
        'total_samples': int(cm.sum()),
        'diag_sum': int(diag.sum()),
        'diag_nonzero_bins': int((diag > 0).sum()),
        'diag_exact_yaw_accuracy': float(diag.sum() / cm.sum()) if cm.sum() > 0 else 0.0
    })

with open(OUTPUT_DIR / "diagonal_exact_stats.csv", 'w', newline='', encoding='utf-8') as csvf:
    writer = csv.DictWriter(csvf, fieldnames=diag_stats[0].keys())
    writer.writeheader()
    writer.writerows(diag_stats)
print(f"Saved: diagonal_exact_stats.csv")

for s in diag_stats:
    print(f"  {s['config']}: total={s['total_samples']}, diag_sum={s['diag_sum']}, diag_nonzero_bins={s['diag_nonzero_bins']}")

print("\n=== FIX02 visualization complete ===")

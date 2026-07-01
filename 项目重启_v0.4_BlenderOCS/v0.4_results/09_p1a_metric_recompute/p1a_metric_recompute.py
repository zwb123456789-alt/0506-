"""
P1-A 只读指标重算脚本 (1C-B4)
依据：R99 Codex 裁决
输入：既有 C2/C3 samples (argmax predictions)
输出：v0.4_results/09_p1a_metric_recompute/
操作：只读指标重算，不训练、不推理、不改模型
"""
import numpy as np
import pandas as pd
import json
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 路径配置
PROJECT_ROOT = Path("d:/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS")
C2_SAMPLES_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_samples"
C3_SAMPLES_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_samples"
SPLIT_DIR = PROJECT_ROOT / "v0.4_results/03_training_baseline/e25_multifold_yawblock"
OUTPUT_DIR = PROJECT_ROOT / "v0.4_results/09_p1a_metric_recompute"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Working directory: {OUTPUT_DIR}")

# ============================================================
# 1. 加载数据
# ============================================================
print("\n=== Loading predictions and splits ===")

def load_samples(samples_dir, pattern, n_folds=5):
    """加载 samples.npz 文件"""
    all_samples = []
    for fold in range(n_folds):
        fname = pattern.format(fold=fold)
        fpath = samples_dir / fname
        if not fpath.exists():
            print(f"  Warning: {fname} not found")
            continue
        data = np.load(fpath, allow_pickle=True)
        samples = {
            'fold': fold,
            'record_id': data['record_id'],
            'yaw_pred_bin': data['yaw_pred_bin'],
            'yaw_true_bin': data['yaw_true_bin'],
            'pitch_pred_bin': data['pitch_pred_bin'],
            'pitch_true_bin': data['pitch_true_bin']
        }
        all_samples.append(samples)
        print(f"  Loaded {fname}: {len(data['record_id'])} samples")
    return all_samples

# C2 baseline_4dim (OCS-only)
c2_baseline = load_samples(C2_SAMPLES_DIR, "c2_baseline_4dim_fold{fold}_samples.npz")

# C3 image_only
c3_image = load_samples(C3_SAMPLES_DIR, "c3_image_only_fold{fold}_samples.npz")

# C3 joint
c3_joint = load_samples(C3_SAMPLES_DIR, "c3_joint_fold{fold}_samples.npz")

# ============================================================
# 2. 定义循环角度指标
# ============================================================

def circular_error(pred_bin, true_bin, n_bins=72):
    """计算循环角度误差（单位：bins）
    考虑 0-71 bins 的循环性质，最大误差为 n_bins//2
    """
    diff = np.abs(pred_bin - true_bin)
    circular_diff = np.minimum(diff, n_bins - diff)
    return circular_diff

def circular_mae(pred_bin, true_bin, n_bins=72):
    """循环平均绝对误差（bins）"""
    errors = circular_error(pred_bin, true_bin, n_bins)
    return errors.mean()

def circular_median_ae(pred_bin, true_bin, n_bins=72):
    """循环中位绝对误差（bins）"""
    errors = circular_error(pred_bin, true_bin, n_bins)
    return np.median(errors)

def within_k_bins(pred_bin, true_bin, k, n_bins=72):
    """预测在真值±k bins内的比例"""
    errors = circular_error(pred_bin, true_bin, n_bins)
    return (errors <= k).mean()

def coarse_bin_accuracy(pred_bin, true_bin, bin_width, n_bins=72):
    """粗粒度分类准确率
    bin_width: 粗化后每个bin的宽度（原始bins数）
    例如 bin_width=9 对应 45° (9*5°=45°)
    """
    coarse_pred = pred_bin // bin_width
    coarse_true = true_bin // bin_width
    return (coarse_pred == coarse_true).mean()

def random_baseline_circular_mae(n_bins=72, n_samples=10000):
    """随机预测的循环MAE基线"""
    pred_random = np.random.randint(0, n_bins, n_samples)
    true_random = np.random.randint(0, n_bins, n_samples)
    return circular_mae(pred_random, true_random, n_bins)

def random_baseline_within_k(k, n_bins=72):
    """随机预测的within-k基线（理论值）"""
    # 在循环空间中，within-k 的概率为 (2*k+1)/n_bins
    return (2 * k + 1) / n_bins

def random_baseline_coarse(bin_width, n_bins=72):
    """随机预测的粗粒度准确率基线（理论值）"""
    n_coarse_bins = n_bins // bin_width
    return 1.0 / n_coarse_bins

# ============================================================
# 3. 计算所有指标
# ============================================================
print("\n=== Computing P1-A metrics ===")

def compute_metrics(samples_list, channel_name):
    """计算单个channel的所有指标"""
    results = []

    for sample in samples_list:
        fold = sample['fold']
        yaw_pred = sample['yaw_pred_bin']
        yaw_true = sample['yaw_true_bin']
        n_samples = len(yaw_pred)

        # Circular metrics
        circ_mae = circular_mae(yaw_pred, yaw_true)
        circ_median = circular_median_ae(yaw_pred, yaw_true)

        # Within-k metrics
        within_1 = within_k_bins(yaw_pred, yaw_true, 1)
        within_2 = within_k_bins(yaw_pred, yaw_true, 2)
        within_3 = within_k_bins(yaw_pred, yaw_true, 3)
        within_6 = within_k_bins(yaw_pred, yaw_true, 6)

        # Coarse-bin metrics
        coarse45 = coarse_bin_accuracy(yaw_pred, yaw_true, bin_width=9)  # 9*5°=45°
        coarse90 = coarse_bin_accuracy(yaw_pred, yaw_true, bin_width=18)  # 18*5°=90°

        # Exact-bin (reference)
        exact = (yaw_pred == yaw_true).mean()

        results.append({
            'channel': channel_name,
            'fold': fold,
            'n_samples': n_samples,
            'exact_bin': exact,
            'circular_mae_bins': circ_mae,
            'circular_median_ae_bins': circ_median,
            'within_1bin': within_1,
            'within_2bins': within_2,
            'within_3bins': within_3,
            'within_6bins': within_6,
            'coarse45': coarse45,
            'coarse90': coarse90
        })

    return results

# 计算三个channel
metrics_c2_baseline = compute_metrics(c2_baseline, 'C2_baseline_4dim')
metrics_c3_image = compute_metrics(c3_image, 'C3_image_only')
metrics_c3_joint = compute_metrics(c3_joint, 'C3_joint')

# 合并所有结果
all_metrics = metrics_c2_baseline + metrics_c3_image + metrics_c3_joint

# 转为DataFrame
df_metrics = pd.DataFrame(all_metrics)

# 保存per-fold结果
df_metrics.to_csv(OUTPUT_DIR / "p1a_channel_fold_metrics.csv", index=False)
print(f"Saved: p1a_channel_fold_metrics.csv ({len(df_metrics)} rows)")

# ============================================================
# 4. 聚合统计
# ============================================================
print("\n=== Aggregating statistics ===")

# 按channel聚合（跨fold的mean和std）
agg_stats = df_metrics.groupby('channel').agg({
    'n_samples': 'sum',
    'exact_bin': ['mean', 'std'],
    'circular_mae_bins': ['mean', 'std'],
    'circular_median_ae_bins': ['mean', 'std'],
    'within_1bin': ['mean', 'std'],
    'within_2bins': ['mean', 'std'],
    'within_3bins': ['mean', 'std'],
    'within_6bins': ['mean', 'std'],
    'coarse45': ['mean', 'std'],
    'coarse90': ['mean', 'std']
}).reset_index()

# 展平列名
agg_stats.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in agg_stats.columns.values]

agg_stats.to_csv(OUTPUT_DIR / "p1a_channel_aggregated_stats.csv", index=False)
print(f"Saved: p1a_channel_aggregated_stats.csv")

# ============================================================
# 5. 计算random/naive baseline
# ============================================================
print("\n=== Computing random/naive baselines ===")

n_bins = 72
baseline_metrics = {
    'random_circular_mae_bins': random_baseline_circular_mae(n_bins),
    'random_within_1bin': random_baseline_within_k(1, n_bins),
    'random_within_2bins': random_baseline_within_k(2, n_bins),
    'random_within_3bins': random_baseline_within_k(3, n_bins),
    'random_within_6bins': random_baseline_within_k(6, n_bins),
    'random_coarse45': random_baseline_coarse(9, n_bins),
    'random_coarse90': random_baseline_coarse(18, n_bins),
    'random_exact_bin': 1.0 / n_bins
}

# 保存baseline
with open(OUTPUT_DIR / "p1a_random_baseline.json", 'w') as f:
    json.dump(baseline_metrics, f, indent=2)

baseline_md = ["# P1-A Random Baseline", "", "## Random prediction baseline (theoretical)", ""]
baseline_md.append("| Metric | Random Baseline | Note |")
baseline_md.append("|---|---|---|")
baseline_md.append(f"| Exact-bin (72 classes) | {baseline_metrics['random_exact_bin']:.4f} (1.39%) | 1/72 |")
baseline_md.append(f"| Circular MAE (bins) | {baseline_metrics['random_circular_mae_bins']:.2f} | Monte Carlo |")
baseline_md.append(f"| Within-1 bin | {baseline_metrics['random_within_1bin']:.4f} ({baseline_metrics['random_within_1bin']*100:.2f}%) | (2*1+1)/72 |")
baseline_md.append(f"| Within-2 bins | {baseline_metrics['random_within_2bins']:.4f} ({baseline_metrics['random_within_2bins']*100:.2f}%) | (2*2+1)/72 |")
baseline_md.append(f"| Within-3 bins | {baseline_metrics['random_within_3bins']:.4f} ({baseline_metrics['random_within_3bins']*100:.2f}%) | (2*3+1)/72 |")
baseline_md.append(f"| Within-6 bins | {baseline_metrics['random_within_6bins']:.4f} ({baseline_metrics['random_within_6bins']*100:.2f}%) | (2*6+1)/72 |")
baseline_md.append(f"| Coarse45 (8 classes) | {baseline_metrics['random_coarse45']:.4f} (12.5%) | 1/8 |")
baseline_md.append(f"| Coarse90 (4 classes) | {baseline_metrics['random_coarse90']:.4f} (25.0%) | 1/4 |")

with open(OUTPUT_DIR / "p1a_random_baseline.md", 'w', encoding='utf-8') as f:
    f.write('\n'.join(baseline_md))
print(f"Saved: p1a_random_baseline.md")

# ============================================================
# 6. 生成circular error分布（按channel）
# ============================================================
print("\n=== Computing circular error distributions ===")

def compute_circular_error_dist(samples_list):
    """计算循环误差分布"""
    all_errors = []
    for sample in samples_list:
        errors = circular_error(sample['yaw_pred_bin'], sample['yaw_true_bin'])
        all_errors.extend(errors)
    return np.array(all_errors)

c2_baseline_errors = compute_circular_error_dist(c2_baseline)
c3_image_errors = compute_circular_error_dist(c3_image)
c3_joint_errors = compute_circular_error_dist(c3_joint)

# 统计分布（0-36 bins，因为最大循环误差为36）
def error_histogram(errors, max_bins=37):
    hist = np.zeros(max_bins)
    for e in errors:
        if 0 <= e < max_bins:
            hist[int(e)] += 1
    hist = hist / hist.sum()  # normalize
    return hist

c2_hist = error_histogram(c2_baseline_errors)
c3_img_hist = error_histogram(c3_image_errors)
c3_joint_hist = error_histogram(c3_joint_errors)

# 保存为CSV
error_dist_data = []
for i in range(37):
    error_dist_data.append({
        'error_bins': i,
        'C2_baseline_4dim': c2_hist[i],
        'C3_image_only': c3_img_hist[i],
        'C3_joint': c3_joint_hist[i]
    })

df_error_dist = pd.DataFrame(error_dist_data)
df_error_dist.to_csv(OUTPUT_DIR / "p1a_circular_error_distribution.csv", index=False)
print(f"Saved: p1a_circular_error_distribution.csv")

# ============================================================
# 7. Within-k curve（按channel）
# ============================================================
print("\n=== Computing within-k curves ===")

within_k_data = []
for k in range(0, 37):
    row = {'k_bins': k}
    for sample_list, name in [(c2_baseline, 'C2_baseline_4dim'),
                               (c3_image, 'C3_image_only'),
                               (c3_joint, 'C3_joint')]:
        # 跨fold聚合
        within_k_vals = []
        for sample in sample_list:
            within_k_vals.append(within_k_bins(sample['yaw_pred_bin'], sample['yaw_true_bin'], k))
        row[name] = np.mean(within_k_vals)

    # Random baseline
    row['random_baseline'] = random_baseline_within_k(k, n_bins)

    within_k_data.append(row)

df_within_k = pd.DataFrame(within_k_data)
df_within_k.to_csv(OUTPUT_DIR / "p1a_within_k_curve.csv", index=False)
print(f"Saved: p1a_within_k_curve.csv")

# ============================================================
# 8. Coarse-bin metrics
# ============================================================
print("\n=== Computing coarse-bin metrics ===")

coarse_bins_configs = [
    {'name': 'coarse15', 'bin_width': 3, 'n_classes': 24},   # 3*5°=15°
    {'name': 'coarse30', 'bin_width': 6, 'n_classes': 12},   # 6*5°=30°
    {'name': 'coarse45', 'bin_width': 9, 'n_classes': 8},    # 9*5°=45°
    {'name': 'coarse60', 'bin_width': 12, 'n_classes': 6},   # 12*5°=60°
    {'name': 'coarse90', 'bin_width': 18, 'n_classes': 4},   # 18*5°=90°
]

coarse_data = []
for cfg in coarse_bins_configs:
    row = {
        'coarse_name': cfg['name'],
        'bin_width': cfg['bin_width'],
        'n_classes': cfg['n_classes'],
        'random_baseline': random_baseline_coarse(cfg['bin_width'], n_bins)
    }

    for sample_list, name in [(c2_baseline, 'C2_baseline_4dim'),
                               (c3_image, 'C3_image_only'),
                               (c3_joint, 'C3_joint')]:
        acc_vals = []
        for sample in sample_list:
            acc_vals.append(coarse_bin_accuracy(sample['yaw_pred_bin'], sample['yaw_true_bin'], cfg['bin_width']))
        row[f'{name}_mean'] = np.mean(acc_vals)
        row[f'{name}_std'] = np.std(acc_vals)

    coarse_data.append(row)

df_coarse = pd.DataFrame(coarse_data)
df_coarse.to_csv(OUTPUT_DIR / "p1a_coarse_bin_metrics.csv", index=False)
print(f"Saved: p1a_coarse_bin_metrics.csv")

# ============================================================
# 9. 生成汇总表格
# ============================================================
print("\n=== Generating summary ===")

summary_lines = ["# P1-A Metric Recompute Summary", "", "## Key Findings", ""]

# 提取关键数值
c2_mae = agg_stats[agg_stats['channel'] == 'C2_baseline_4dim']['circular_mae_bins_mean'].values[0]
c3_img_mae = agg_stats[agg_stats['channel'] == 'C3_image_only']['circular_mae_bins_mean'].values[0]
c3_joint_mae = agg_stats[agg_stats['channel'] == 'C3_joint']['circular_mae_bins_mean'].values[0]
random_mae = baseline_metrics['random_circular_mae_bins']

c2_w6 = agg_stats[agg_stats['channel'] == 'C2_baseline_4dim']['within_6bins_mean'].values[0]
c3_img_w6 = agg_stats[agg_stats['channel'] == 'C3_image_only']['within_6bins_mean'].values[0]
c3_joint_w6 = agg_stats[agg_stats['channel'] == 'C3_joint']['within_6bins_mean'].values[0]
random_w6 = baseline_metrics['random_within_6bins']

c2_c45 = agg_stats[agg_stats['channel'] == 'C2_baseline_4dim']['coarse45_mean'].values[0]
c3_img_c45 = agg_stats[agg_stats['channel'] == 'C3_image_only']['coarse45_mean'].values[0]
c3_joint_c45 = agg_stats[agg_stats['channel'] == 'C3_joint']['coarse45_mean'].values[0]
random_c45 = baseline_metrics['random_coarse45']

summary_lines.append(f"- **Circular MAE**: C2={c2_mae:.2f} bins, C3_img={c3_img_mae:.2f}, C3_joint={c3_joint_mae:.2f}, random={random_mae:.2f}")
summary_lines.append(f"- **Within-6 bins**: C2={c2_w6:.2%}, C3_img={c3_img_w6:.2%}, C3_joint={c3_joint_w6:.2%}, random={random_w6:.2%}")
summary_lines.append(f"- **Coarse45**: C2={c2_c45:.2%}, C3_img={c3_img_c45:.2%}, C3_joint={c3_joint_c45:.2%}, random={random_c45:.2%}")
summary_lines.append("")

with open(OUTPUT_DIR / "p1a_metric_recompute_summary.md", 'w', encoding='utf-8') as f:
    f.write('\n'.join(summary_lines))
print(f"Saved: p1a_metric_recompute_summary.md")

print("\n=== P1-A metric recompute complete ===")
print(f"All outputs saved to: {OUTPUT_DIR}")

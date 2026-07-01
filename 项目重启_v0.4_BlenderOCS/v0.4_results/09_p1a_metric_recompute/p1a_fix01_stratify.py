"""
P1-A FIX01: 分层指标与baseline口径修正 (1C-B4-FIX01)
依据：R100 Codex 审阅
修正项：
1. pitch 分层指标（用 pitch_true_bin / record_id 解析）
2. yaw-block 分层指标（读取 split manifest）
3. random circular MAE baseline 改为理论值 18.0
4. pooled weighted metrics（与 per-fold unweighted mean 并列）
输入：既有 samples.npz + split manifest
输出：v0.4_results/09_p1a_metric_recompute/
操作：只读，不训练、不推理、不改模型
"""
import numpy as np
import pandas as pd
import json
import os
import re
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

N_BINS = 72  # yaw bins

# ============================================================
# 0. 循环角度指标定义
# ============================================================
def circular_error(pred_bin, true_bin, n_bins=N_BINS):
    diff = np.abs(np.asarray(pred_bin) - np.asarray(true_bin))
    return np.minimum(diff, n_bins - diff)

def circular_mae(pred_bin, true_bin, n_bins=N_BINS):
    return circular_error(pred_bin, true_bin, n_bins).mean()

def circular_median_ae(pred_bin, true_bin, n_bins=N_BINS):
    return np.median(circular_error(pred_bin, true_bin, n_bins))

def within_k_bins(pred_bin, true_bin, k, n_bins=N_BINS):
    return (circular_error(pred_bin, true_bin, n_bins) <= k).mean()

def coarse_bin_accuracy(pred_bin, true_bin, bin_width, n_bins=N_BINS):
    cp = np.asarray(pred_bin) // bin_width
    ct = np.asarray(true_bin) // bin_width
    return (cp == ct).mean()

# 理论 random baseline（R100 要求）
def theoretical_random_circular_mae(n_bins=N_BINS):
    """对 n_bins circular distance，random circular MAE 的理论值。
    circular distance d 取值 0..n/2，d=1..(n/2-1) 各出现2次，d=0和d=n/2各出现1次。
    期望 = sum(d * count(d)) / n_bins
    n_bins=72: d=0..36; d=1..35各2次, d=0一次, d=36一次。
    """
    n = n_bins
    half = n // 2
    total = 0.0
    for d in range(0, half + 1):
        if d == 0 or d == half:
            count = 1
        else:
            count = 2
        total += d * count
    return total / n  # = 18.0 for n=72

def theoretical_random_within_k(k, n_bins=N_BINS):
    return (2 * k + 1) / n_bins

def theoretical_random_coarse(bin_width, n_bins=N_BINS):
    return 1.0 / (n_bins // bin_width)

# ============================================================
# 1. 加载 samples
# ============================================================
print("\n=== Loading samples ===")

def load_samples(samples_dir, pattern, n_folds=5):
    out = []
    for fold in range(n_folds):
        fpath = samples_dir / pattern.format(fold=fold)
        if not fpath.exists():
            print(f"  Warning: {fpath.name} not found")
            continue
        d = np.load(fpath, allow_pickle=True)
        out.append({
            'fold': fold,
            'record_id': d['record_id'],
            'yaw_pred_bin': d['yaw_pred_bin'],
            'yaw_true_bin': d['yaw_true_bin'],
            'pitch_pred_bin': d['pitch_pred_bin'],
            'pitch_true_bin': d['pitch_true_bin'],
        })
    return out

c2_baseline = load_samples(C2_SAMPLES_DIR, "c2_baseline_4dim_fold{fold}_samples.npz")
c3_image = load_samples(C3_SAMPLES_DIR, "c3_image_only_fold{fold}_samples.npz")
c3_joint = load_samples(C3_SAMPLES_DIR, "c3_joint_fold{fold}_samples.npz")

CHANNELS = [
    ('C2_baseline_4dim', c2_baseline),
    ('C3_image_only', c3_image),
    ('C3_joint', c3_joint),
]

# ============================================================
# 2. 解析 pitch（从 record_id）+ 核对 pitch_true_bin
# ============================================================
print("\n=== Parsing pitch from record_id ===")

def parse_pitch_deg(rid):
    """phase63_yawNNN_pitch±NNN -> pitch_deg"""
    m = re.match(r'phase63_yaw(\d+)_pitch([+-]\d+)', str(rid))
    if m:
        return int(m.group(2))
    return None

# 核对：record_id 解析的 pitch 与 pitch_true_bin 是否一致
sample0 = c3_image[0]
parsed_pitch = np.array([parse_pitch_deg(r) for r in sample0['record_id']])
ptb = sample0['pitch_true_bin']
print(f"  pitch_true_bin range: [{ptb.min()}, {ptb.max()}]")
print(f"  parsed pitch_deg range: [{parsed_pitch.min()}, {parsed_pitch.max()}]")
# pitch_true_bin 可能是 0-36 的索引（pitch_deg = -90 + bin*5）
recon = parsed_pitch
print(f"  Using record_id-parsed pitch_deg for stratification.")

# ============================================================
# 3. 读取 split manifest，建立 record_id -> (fold, split, yaw_block) 映射
# ============================================================
print("\n=== Loading split manifests ===")

fold_test_yaw_range = {}  # fold -> (yaw_min, yaw_max)
record_to_meta = {}  # record_id -> {fold, split, yaw_deg, pitch_deg}

manifest_paths_tried = []
manifest_fields = None
for fold in range(5):
    mpath = SPLIT_DIR / f"split_manifest_circ_yawblock_fold{fold}.json"
    manifest_paths_tried.append(str(mpath))
    if not mpath.exists():
        print(f"  Warning: manifest fold{fold} not found")
        continue
    with open(mpath, 'r', encoding='utf-8') as f:
        m = json.load(f)
    if manifest_fields is None and m['test']:
        manifest_fields = list(m['test'][0].keys())
    # test yaw block range
    test_yaws = [r['yaw_deg'] for r in m['test']]
    fold_test_yaw_range[fold] = (min(test_yaws), max(test_yaws))
    # record -> meta (only need test for stratification of evaluation)
    for r in m['test']:
        record_to_meta[r['record_id']] = {
            'fold': fold, 'split': 'test',
            'yaw_deg': r['yaw_deg'], 'pitch_deg': r['pitch_deg']
        }

print(f"  Manifest fields: {manifest_fields}")
print(f"  Test yaw blocks per fold:")
for fold, (ymin, ymax) in fold_test_yaw_range.items():
    print(f"    fold{fold}: [{ymin:.0f}, {ymax:.0f}]")

# ============================================================
# 4. Pooled weighted metrics（R100 3.4）
# ============================================================
print("\n=== Computing pooled (sample-level weighted) metrics ===")

pooled_rows = []
for cname, slist in CHANNELS:
    # pool所有fold的样本
    all_pred = np.concatenate([s['yaw_pred_bin'] for s in slist])
    all_true = np.concatenate([s['yaw_true_bin'] for s in slist])
    pooled_rows.append({
        'channel': cname,
        'n_samples_pooled': len(all_pred),
        'exact_bin': (all_pred == all_true).mean(),
        'circular_mae_bins': circular_mae(all_pred, all_true),
        'circular_median_ae_bins': circular_median_ae(all_pred, all_true),
        'within_1bin': within_k_bins(all_pred, all_true, 1),
        'within_2bins': within_k_bins(all_pred, all_true, 2),
        'within_3bins': within_k_bins(all_pred, all_true, 3),
        'within_6bins': within_k_bins(all_pred, all_true, 6),
        'coarse45': coarse_bin_accuracy(all_pred, all_true, 9),
        'coarse90': coarse_bin_accuracy(all_pred, all_true, 18),
        'aggregation': 'pooled_sample_weighted'
    })

df_pooled = pd.DataFrame(pooled_rows)
df_pooled.to_csv(OUTPUT_DIR / "p1a_channel_pooled_metrics.csv", index=False)
print(f"Saved: p1a_channel_pooled_metrics.csv")
for r in pooled_rows:
    print(f"  {r['channel']}: circ_MAE={r['circular_mae_bins']:.2f}, within6={r['within_6bins']:.3f}, coarse45={r['coarse45']:.3f}")

# ============================================================
# 5. Pitch 分层指标（R100 3.1）
# ============================================================
print("\n=== Computing pitch-stratified metrics ===")

# pitch bands: 用 record_id 解析的 pitch_deg
def pitch_band(pitch_deg):
    if pitch_deg <= -30:
        return 'negative(<=-30)'
    elif pitch_deg < 30:
        return 'near_zero(-25..25)'
    else:
        return 'positive(>=30)'

pitch_rows = []
for cname, slist in CHANNELS:
    # pool样本并解析pitch
    all_pred = np.concatenate([s['yaw_pred_bin'] for s in slist])
    all_true = np.concatenate([s['yaw_true_bin'] for s in slist])
    all_rid = np.concatenate([s['record_id'] for s in slist])
    all_pitch = np.array([parse_pitch_deg(r) for r in all_rid])

    for band in ['negative(<=-30)', 'near_zero(-25..25)', 'positive(>=30)']:
        mask = np.array([pitch_band(p) == band for p in all_pitch])
        if mask.sum() == 0:
            continue
        pred_b = all_pred[mask]
        true_b = all_true[mask]
        pitch_rows.append({
            'channel': cname,
            'pitch_band': band,
            'n_samples': int(mask.sum()),
            'circular_mae_bins': circular_mae(pred_b, true_b),
            'within_3bins': within_k_bins(pred_b, true_b, 3),
            'within_6bins': within_k_bins(pred_b, true_b, 6),
            'coarse45': coarse_bin_accuracy(pred_b, true_b, 9),
        })

df_pitch = pd.DataFrame(pitch_rows)
df_pitch.to_csv(OUTPUT_DIR / "p1a_pitch_stratified_metrics.csv", index=False)
print(f"Saved: p1a_pitch_stratified_metrics.csv ({len(df_pitch)} rows)")

# ============================================================
# 6. Yaw-block 分层指标（R100 3.2）
# ============================================================
print("\n=== Computing yaw-block-stratified metrics ===")

# 每个fold的test集就是一个yaw block（连续弧段）
yaw_block_rows = []
for cname, slist in CHANNELS:
    for s in slist:
        fold = s['fold']
        pred = s['yaw_pred_bin']
        true = s['yaw_true_bin']
        ymin, ymax = fold_test_yaw_range.get(fold, (None, None))
        yaw_block_rows.append({
            'channel': cname,
            'fold': fold,
            'test_yaw_block': f"[{ymin:.0f},{ymax:.0f}]" if ymin is not None else "unknown",
            'n_samples': len(pred),
            'circular_mae_bins': circular_mae(pred, true),
            'within_3bins': within_k_bins(pred, true, 3),
            'within_6bins': within_k_bins(pred, true, 6),
            'coarse45': coarse_bin_accuracy(pred, true, 9),
        })

df_yaw_block = pd.DataFrame(yaw_block_rows)
df_yaw_block.to_csv(OUTPUT_DIR / "p1a_yaw_block_stratified_metrics.csv", index=False)
print(f"Saved: p1a_yaw_block_stratified_metrics.csv ({len(df_yaw_block)} rows)")

# ============================================================
# 7. 修正 baseline 为理论值（R100 3.3）
# ============================================================
print("\n=== Correcting baseline to theoretical values ===")

theoretical_baseline = {
    'random_circular_mae_bins': theoretical_random_circular_mae(N_BINS),  # 18.0
    'random_exact_bin': 1.0 / N_BINS,
    'random_within_1bin': theoretical_random_within_k(1),
    'random_within_2bins': theoretical_random_within_k(2),
    'random_within_3bins': theoretical_random_within_k(3),
    'random_within_6bins': theoretical_random_within_k(6),
    'random_coarse45': theoretical_random_coarse(9),
    'random_coarse90': theoretical_random_coarse(18),
}

with open(OUTPUT_DIR / "p1a_random_baseline_theoretical.json", 'w') as f:
    json.dump(theoretical_baseline, f, indent=2)

bl = theoretical_baseline
bl_md = ["# P1-A Random Baseline (Theoretical, Corrected)", "",
         "R100 3.3: 改用理论值，避免 Monte Carlo 漂移。", "",
         "## 理论 random prediction baseline", "",
         "| Metric | Theoretical Value | Derivation |", "|---|---|---|"]
bl_md.append(f"| Exact-bin (72 类) | {bl['random_exact_bin']:.4f} (1.39%) | 1/72 |")
bl_md.append(f"| Circular MAE (bins) | {bl['random_circular_mae_bins']:.1f} | sum(d*count(d))/72 = 18.0 |")
bl_md.append(f"| Within-1 bin | {bl['random_within_1bin']:.4f} ({bl['random_within_1bin']*100:.2f}%) | 3/72 |")
bl_md.append(f"| Within-2 bins | {bl['random_within_2bins']:.4f} ({bl['random_within_2bins']*100:.2f}%) | 5/72 |")
bl_md.append(f"| Within-3 bins | {bl['random_within_3bins']:.4f} ({bl['random_within_3bins']*100:.2f}%) | 7/72 |")
bl_md.append(f"| Within-6 bins | {bl['random_within_6bins']:.4f} ({bl['random_within_6bins']*100:.2f}%) | 13/72 |")
bl_md.append(f"| Coarse45 (8 类) | {bl['random_coarse45']:.4f} (12.5%) | 1/8 |")
bl_md.append(f"| Coarse90 (4 类) | {bl['random_coarse90']:.4f} (25.0%) | 1/4 |")
bl_md.append("")
bl_md.append("**注**：先前 FIX01 报告中 circular MAE baseline = 18.0528（Monte Carlo, 未固定 seed），")
bl_md.append("理论值为 18.0，差异 0.05 bins，不改变任何结论。后续材料统一使用理论值 18.0。")

with open(OUTPUT_DIR / "p1a_baseline_corrected.md", 'w', encoding='utf-8') as f:
    f.write('\n'.join(bl_md))
print(f"Saved: p1a_baseline_corrected.md (theoretical circular MAE = {bl['random_circular_mae_bins']:.1f})")

print("\n=== FIX01 stratification complete ===")

"""
P0 只读诊断补齐脚本 (1C-B3-FIX01)
只读分析：不训练、不推理、不生成新预测、不改任何已有文件。
输入：已有 npz/json 文件
输出：v0.4_results/08_p0_diagnostics/
"""
import numpy as np
import json
import os
import re
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 路径配置
PROJECT_ROOT = Path(os.getcwd())
print(f"PROJECT_ROOT = {PROJECT_ROOT}")
OCS_NPZ = PROJECT_ROOT / "v0.4_results/04_ocs_features/enhanced_ocs_features.npz"
C2_CONFUSION_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_confusion"
C3_CONFUSION_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_confusion"
C2_SAMPLES_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_samples"
C3_SAMPLES_DIR = PROJECT_ROOT / "v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_samples"
SPLIT_DIR = PROJECT_ROOT / "v0.4_results/03_training_baseline/e25_multifold_yawblock"
OUTPUT_DIR = PROJECT_ROOT / "v0.4_results/08_p0_diagnostics"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 1. 加载数据
# ============================================================
print("=== Loading data ===")

# OCS 特征
ocs_data = np.load(OCS_NPZ, allow_pickle=True)
record_ids = ocs_data['record_ids']  # shape (2664,)
baseline_4dim = ocs_data['baseline_4dim']  # shape (2664, 4)
print(f"OCS loaded: {len(record_ids)} records, baseline_4dim shape={baseline_4dim.shape}")

# 解析 record_id -> {yaw_deg, pitch_deg, yaw_bin, pitch_bin}
def parse_record_id(rid):
    """phase63_yawNNN_pitch±NNN -> {yaw_deg, pitch_deg, yaw_bin, pitch_bin}"""
    m = re.match(r'phase63_yaw(\d+)_pitch([+-]\d+)', str(rid))
    if m:
        yaw_deg = int(m.group(1))
        pitch_deg = int(m.group(2))
        yaw_bin = yaw_deg // 5  # 72 bins, 0-71
        pitch_bin = pitch_deg // 5  # adjust for negative
        return {'yaw_deg': yaw_deg, 'pitch_deg': pitch_deg, 'yaw_bin': yaw_bin, 'pitch_bin': pitch_bin}
    return None

parsed = [parse_record_id(r) for r in record_ids]
yaw_bins_all = np.array([p['yaw_bin'] for p in parsed])
pitch_degs_all = np.array([p['pitch_deg'] for p in parsed])
yaw_degs_all = np.array([p['yaw_deg'] for p in parsed])
print(f"Parsed: yaw_bins range [{yaw_bins_all.min()}, {yaw_bins_all.max()}], pitch_degs range [{pitch_degs_all.min()}, {pitch_degs_all.max()}]")

# ============================================================
# 2. P0-2: OCS yaw-yaw distance matrix
# ============================================================
print("\n=== P0-2: OCS yaw-yaw distance matrix ===")

N_YAWS = 72  # 0-355 deg, 5 deg steps

# 对每个 yaw bin 聚合 baseline_4dim
yaw_means = np.zeros((N_YAWS, 4))
yaw_stds = np.zeros((N_YAWS, 4))
yaw_counts = np.zeros(N_YAWS, dtype=int)
for yb in range(N_YAWS):
    mask = yaw_bins_all == yb
    yaw_counts[yb] = mask.sum()
    if mask.sum() > 0:
        yaw_means[yb] = baseline_4dim[mask].mean(axis=0)
        yaw_stds[yb] = baseline_4dim[mask].std(axis=0)

# Cosine distance matrix
from numpy.linalg import norm
cos_dist = np.zeros((N_YAWS, N_YAWS))
for i in range(N_YAWS):
    for j in range(N_YAWS):
        if yaw_counts[i] == 0 or yaw_counts[j] == 0:
            cos_dist[i, j] = np.nan
        else:
            a, b = yaw_means[i], yaw_means[j]
            na, nb = norm(a), norm(b)
            if na < 1e-12 or nb < 1e-12:
                cos_dist[i, j] = np.nan
            else:
                cos_sim = np.dot(a, b) / (na * nb)
                cos_dist[i, j] = 1.0 - cos_sim  # cosine distance = 1 - cosine similarity

# Euclidean distance matrix (normalized per dimension)
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
baseline_scaled = scaler.fit_transform(baseline_4dim)
yaw_means_scaled = np.zeros((N_YAWS, 4))
for yb in range(N_YAWS):
    mask = yaw_bins_all == yb
    if mask.sum() > 0:
        yaw_means_scaled[yb] = baseline_scaled[mask].mean(axis=0)

eucl_dist = np.zeros((N_YAWS, N_YAWS))
for i in range(N_YAWS):
    for j in range(N_YAWS):
        eucl_dist[i, j] = norm(yaw_means_scaled[i] - yaw_means_scaled[j])

# 保存距离矩阵
np.savez(OUTPUT_DIR / "ocs_yaw_distance_matrices.npz",
         cos_dist=cos_dist, eucl_dist=eucl_dist,
         yaw_counts=yaw_counts, yaw_means=yaw_means,
         n_yaws=N_YAWS)

# 找最近邻对 (每个 test yaw 到所有其他 yaw 的距离排序)
# 排除自己
nearest_pairs = []
for i in range(N_YAWS):
    if yaw_counts[i] == 0:
        continue
    dists = [(j, cos_dist[i, j]) for j in range(N_YAWS) if j != i and not np.isnan(cos_dist[i, j])]
    dists.sort(key=lambda x: x[1])
    for j, d in dists[:3]:
        nearest_pairs.append({
            'yaw_i': i, 'yaw_i_deg': i*5, 'count_i': int(yaw_counts[i]),
            'yaw_j': j, 'yaw_j_deg': j*5, 'count_j': int(yaw_counts[j]),
            'cos_dist': float(d)
        })

# 保存最近邻
with open(OUTPUT_DIR / "nearest_yaw_pairs.json", 'w') as f:
    json.dump(nearest_pairs, f, indent=2, ensure_ascii=False)

# 统计
valid_dists = cos_dist[~np.isnan(cos_dist)]
print(f"Cosine distance: min={valid_dists.min():.6f}, max={valid_dists.max():.6f}, mean={valid_dists.mean():.6f}")
print(f"Nearest pairs saved: {len(nearest_pairs)}")

# ============================================================
# 3. P0-3: Confusion cluster aggregation
# ============================================================
print("\n=== P0-3: Confusion cluster aggregation ===")

def aggregate_confusions(conf_dir, pattern, n_folds=5):
    """聚合混淆矩阵"""
    cms = []
    for fold in range(n_folds):
        fname = pattern.format(fold=fold)
        fpath = conf_dir / fname
        if fpath.exists():
            d = np.load(fpath, allow_pickle=True)
            cm = d['confusion']  # shape (72, 72)
            cms.append(cm)
    if not cms:
        return None
    stacked = np.stack(cms)  # (n_folds, 72, 72)
    total = stacked.sum(axis=0)
    mean_cm = stacked.mean(axis=0)
    return {'stacked': stacked, 'total': total, 'mean': mean_cm, 'n_folds': len(cms)}

# C3 image_only
c3_img = aggregate_confusions(C3_CONFUSION_DIR, "c3_image_only_fold{fold}_yaw_cm.npz")
c3_joint = aggregate_confusions(C3_CONFUSION_DIR, "c3_joint_fold{fold}_yaw_cm.npz")
# C2 baseline_4dim
c2_base = aggregate_confusions(C2_CONFUSION_DIR, "c2_baseline_4dim_fold{fold}_yaw_cm.npz")
# C2 M6_all
c2_m6 = aggregate_confusions(C2_CONFUSION_DIR, "c2_M6_all_nongeo_13d_fold{fold}_yaw_cm.npz")

print(f"C3 image_only: {c3_img['n_folds']} folds, total samples={c3_img['total'].sum()}")
print(f"C3 joint: {c3_joint['n_folds']} folds, total samples={c3_joint['total'].sum()}")
print(f"C2 baseline_4dim: {c2_base['n_folds']} folds, total samples={c2_base['total'].sum()}")
print(f"C2 M6_all: {c2_m6['n_folds']} folds, total samples={c2_m6['total'].sum()}")

# 提取高频混淆对 (非对角线 top-K)
def top_confusion_pairs(total_cm, k=30):
    pairs = []
    n = total_cm.shape[0]
    for i in range(n):
        for j in range(n):
            if i != j:
                pairs.append({
                    'true_yaw_bin': i, 'true_yaw_deg': i*5,
                    'pred_yaw_bin': j, 'pred_yaw_deg': j*5,
                    'count': int(total_cm[i, j])
                })
    pairs.sort(key=lambda x: x['count'], reverse=True)
    return pairs[:k]

c3_img_pairs = top_confusion_pairs(c3_img['total'])
c3_joint_pairs = top_confusion_pairs(c3_joint['total'])
c2_base_pairs = top_confusion_pairs(c2_base['total'])

# 保存
with open(OUTPUT_DIR / "top_confusion_pairs.json", 'w') as f:
    json.dump({
        'c3_image_only': c3_img_pairs,
        'c3_joint': c3_joint_pairs,
        'c2_baseline_4dim': c2_base_pairs
    }, f, indent=2, ensure_ascii=False)

# Per-yaw 预测坍缩分析
def yaw_pred_distribution(total_cm):
    """每个 true_yaw 的 top-3 pred_yaw 及其占比"""
    results = []
    n = total_cm.shape[0]
    for i in range(n):
        row = total_cm[i]
        row_sum = row.sum()
        if row_sum == 0:
            continue
        top_idx = np.argsort(row)[::-1][:5]
        top_info = []
        for idx in top_idx:
            top_info.append({
                'pred_yaw_bin': int(idx), 'pred_yaw_deg': int(idx)*5,
                'count': int(row[idx]),
                'frac': float(row[idx] / row_sum)
            })
        # 检查对角线是否在 top-5
        diag_in_top5 = i in top_idx
        results.append({
            'true_yaw_bin': i, 'true_yaw_deg': i*5,
            'total_samples': int(row_sum),
            'diag_in_top5': diag_in_top5,
            'diag_rank': int(np.where(np.argsort(row)[::-1] == i)[0][0]) + 1 if row[i] > 0 else None,
            'top5_preds': top_info
        })
    return results

c3_img_yaw_dist = yaw_pred_distribution(c3_img['total'])
c3_joint_yaw_dist = yaw_pred_distribution(c3_joint['total'])

with open(OUTPUT_DIR / "per_yaw_pred_distribution.json", 'w') as f:
    json.dump({
        'c3_image_only': c3_img_yaw_dist,
        'c3_joint': c3_joint_yaw_dist
    }, f, indent=2, ensure_ascii=False)

# 统计对角线命中率
diag_in_top5_img = sum(1 for r in c3_img_yaw_dist if r['diag_in_top5'])
diag_in_top5_joint = sum(1 for r in c3_joint_yaw_dist if r['diag_in_top5'])
print(f"C3 image: diag in top5 = {diag_in_top5_img}/{len(c3_img_yaw_dist)}")
print(f"C3 joint: diag in top5 = {diag_in_top5_joint}/{len(c3_joint_yaw_dist)}")

# ============================================================
# 4. P0-4: Pseudo-light-curve probe
# ============================================================
print("\n=== P0-4: Pseudo-light-curve probe ===")

# 选 pitch=0 作为示例
pitch0_mask = pitch_degs_all == 0
pitch0_ids = record_ids[pitch0_mask]
pitch0_ocs = baseline_4dim[pitch0_mask]  # (n, 4)
pitch0_yaw_degs = yaw_degs_all[pitch0_mask]
pitch0_yaw_bins = yaw_bins_all[pitch0_mask]

# 按 yaw 排序
sort_idx = np.argsort(pitch0_yaw_degs)
pitch0_ocs_sorted = pitch0_ocs[sort_idx]
pitch0_yaw_sorted = pitch0_yaw_degs[sort_idx]

print(f"Pitch=0 samples: {len(pitch0_ocs)}")

# 保存伪光变曲线数据
np.savez(OUTPUT_DIR / "pseudo_light_curve_pitch0.npz",
         yaw_deg=pitch0_yaw_sorted,
         ocs_total=pitch0_ocs_sorted[:, 0],
         ocs_jinshuzhuti=pitch0_ocs_sorted[:, 1],
         ocs_taiyangnengban=pitch0_ocs_sorted[:, 2],
         ocs_yinshenban=pitch0_ocs_sorted[:, 3])

# 序列形态相似性：滑动窗口比较
def sliding_window_similarity(yaw_seq, ocs_seq, window=5):
    """计算相邻 yaw 间的滑动窗口 cosine 相似性"""
    n = len(yaw_seq)
    similarities = []
    for i in range(n - window):
        seg_i = ocs_seq[i:i+window].flatten()
        for j in range(i + window, n - window, window):
            seg_j = ocs_seq[j:j+window].flatten()
            norm_i, norm_j = norm(seg_i), norm(seg_j)
            if norm_i > 1e-12 and norm_j > 1e-12:
                sim = np.dot(seg_i, seg_j) / (norm_i * norm_j)
                similarities.append({
                    'yaw_i': float(yaw_seq[i]), 'yaw_j': float(yaw_seq[j]),
                    'yaw_i_deg': float(yaw_seq[i]), 'yaw_j_deg': float(yaw_seq[j]),
                    'cos_sim': float(sim),
                    'yaw_dist_deg': float(min(abs(yaw_seq[i] - yaw_seq[j]), 360 - abs(yaw_seq[i] - yaw_seq[j])))
                })
    return similarities

seq_sims = sliding_window_similarity(pitch0_yaw_sorted, pitch0_ocs_sorted, window=5)
# 按 yaw 距离分组统计
dist_groups = {'near(<=15)': [], 'mid(20-45)': [], 'far(>=50)': []}
for s in seq_sims:
    d = s['yaw_dist_deg']
    if d <= 15:
        dist_groups['near(<=15)'].append(s['cos_sim'])
    elif d <= 45:
        dist_groups['mid(20-45)'].append(s['cos_sim'])
    else:
        dist_groups['far(>=50)'].append(s['cos_sim'])

seq_summary = {}
for k, v in dist_groups.items():
    if v:
        seq_summary[k] = {'n': len(v), 'mean_cos_sim': float(np.mean(v)), 'std_cos_sim': float(np.std(v))}
    else:
        seq_summary[k] = {'n': 0, 'mean_cos_sim': None, 'std_cos_sim': None}
print(f"Pseudo-sequence similarity summary: {json.dumps(seq_summary, indent=2)}")

# 单帧最近邻基线对比
single_nn_sims = []
for i in range(len(pitch0_ocs_sorted)):
    for j in range(i+1, len(pitch0_ocs_sorted)):
        a, b = pitch0_ocs_sorted[i], pitch0_ocs_sorted[j]
        na, nb = norm(a), norm(b)
        if na > 1e-12 and nb > 1e-12:
            sim = np.dot(a, b) / (na * nb)
            yaw_d = min(abs(pitch0_yaw_sorted[i] - pitch0_yaw_sorted[j]),
                       360 - abs(pitch0_yaw_sorted[i] - pitch0_yaw_sorted[j]))
            single_nn_sims.append({'cos_sim': float(sim), 'yaw_dist': float(yaw_d)})

single_near = [s['cos_sim'] for s in single_nn_sims if s['yaw_dist'] <= 15]
single_far = [s['cos_sim'] for s in single_nn_sims if s['yaw_dist'] >= 50]
print(f"Single-frame: near(<=15) mean_cos_sim={np.mean(single_near):.4f}, far(>=50) mean_cos_sim={np.mean(single_far):.4f}")

# 保存
with open(OUTPUT_DIR / "pseudo_sequence_similarity.json", 'w') as f:
    json.dump({
        'sequence_5frame_window': seq_summary,
        'single_frame': {
            'near_15': {'n': len(single_near), 'mean_cos_sim': float(np.mean(single_near))},
            'far_50': {'n': len(single_far), 'mean_cos_sim': float(np.mean(single_far))}
        },
        'note': 'pseudo-light-curve probe only; not a light-curve experiment'
    }, f, indent=2, ensure_ascii=False)

# ============================================================
# 5. distance vs confusion overlap 交叉比对
# ============================================================
print("\n=== P0 cross-check: distance vs confusion overlap ===")

# 对 C3 image_only 高频混淆对，检查其 cosine distance
overlap_data = []
for pair in c3_img_pairs[:20]:
    ti, pj = pair['true_yaw_bin'], pair['pred_yaw_bin']
    cd = float(cos_dist[ti, pj]) if not np.isnan(cos_dist[ti, pj]) else None
    ed = float(eucl_dist[ti, pj])
    overlap_data.append({
        'true_yaw': ti, 'pred_yaw': pj,
        'true_deg': ti*5, 'pred_deg': pj*5,
        'angular_dist_deg': min(abs(ti-pj)*5, 360-abs(ti-pj)*5),
        'confusion_count': pair['count'],
        'cos_dist': cd,
        'eucl_dist': ed
    })

with open(OUTPUT_DIR / "distance_confusion_overlap.json", 'w') as f:
    json.dump(overlap_data, f, indent=2, ensure_ascii=False)

# 统计
has_cos = [o for o in overlap_data if o['cos_dist'] is not None]
if has_cos:
    cos_vals = [o['cos_dist'] for o in has_cos]
    print(f"Top-20 confusion pairs: cos_dist mean={np.mean(cos_vals):.4f}, min={np.min(cos_vals):.4f}")
    print(f"(smaller cos_dist = more signature overlap = expected to cause confusion)")

# ============================================================
# 6. 汇总输出
# ============================================================
print(f"\n=== All outputs saved to {OUTPUT_DIR} ===")
print("Files:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    fpath = OUTPUT_DIR / f
    size = fpath.stat().st_size
    print(f"  {f} ({size} bytes)")

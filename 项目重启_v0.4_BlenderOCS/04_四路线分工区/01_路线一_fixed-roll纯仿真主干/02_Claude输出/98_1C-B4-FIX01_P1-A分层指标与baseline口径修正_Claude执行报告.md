# 98_1C-B4-FIX01 P1-A分层指标与baseline口径修正 Claude 执行报告

最后更新：2026-06-29
执行端：Claude
性质：头B-B4/P1-A 只读分层指标修正（FIX01）。不是训练、不是模型改进、不是外推补救成功。
依据：R100 Codex 审阅
输出目录：`v0.4_results/09_p1a_metric_recompute/`

## 0. 执行摘要

```text
R100 判定 97 合规但 P1-A 第一阶段未闭口，需 FIX01 完成分层与 baseline 修正。
本轮完成五项：
1. pitch 分层指标（用 record_id 解析 pitch_deg）
2. yaw-block 分层指标（读取 split manifest）
3. random circular MAE baseline 改为理论值 18.0
4. pooled weighted metrics（与 per-fold unweighted mean 并列）
5. claim 收窄（图像通道信息量表述降级）

核心新发现：yaw-block 强异质性。
- C2 best block (fold3, [220,285°]): MAE=7.5 bins, within-6=42.9%
- C2 worst block (fold4, [290,355°]): MAE=26.6 bins, coarse45=0%
- pitch 影响远小于 yaw-block（pitch MAE 跨度 2.6 vs yaw-block 跨度 19 bins）

结论方向不变：不支持训练侧改进，P1-A 作为论文指标重构 + 异质性诊断材料。
```

## 1. R100 问题逐项修正

### 1.1 Pitch 分层（R100 3.1）✅ 已完成

确认 pitch 信息可用：
- `samples.npz` 含 `pitch_true_bin`（范围 0-36）
- `record_id` 可解析 pitch_deg（范围 -90 到 +90），二者一致

按 pitch band 分层（negative ≤-30°、near_zero -25..25°、positive ≥30°）重算每 channel 的 circular MAE、within-3、within-6、coarse45。

| Channel | Pitch Band | N | Circular MAE | Within-6 | Coarse45 |
|---|---|---|---|---|---|
| C2 | negative(≤-30°) | 936 | 18.61 | 15.5% | 12.0% |
| C2 | near_zero | 792 | 18.72 | 14.4% | 10.9% |
| C2 | positive(≥30°) | 936 | **16.20** | **17.9%** | 12.5% |
| C3_img | negative(≤-30°) | 936 | 16.15 | 28.1% | 19.0% |
| C3_img | near_zero | 792 | 16.07 | 26.1% | 18.4% |
| C3_img | positive(≥30°) | 936 | 16.72 | 22.5% | 16.9% |
| C3_joint | negative(≤-30°) | 936 | 16.15 | 29.1% | 18.5% |
| C3_joint | near_zero | 792 | 16.14 | 24.7% | 18.3% |
| C3_joint | positive(≥30°) | 936 | 16.63 | 25.4% | 18.2% |

**发现**：
- C2 在 positive pitch（≥30°）略优（MAE=16.2 vs 18.6-18.7），可能高 pitch 下太阳能板朝向变化使 OCS 略可分。
- C3 pitch 间较均匀（MAE 16.1-16.7），pitch 不是 C3 主导分层因素。
- pitch MAE 跨度仅 2.6 bins，远小于 yaw-block。

产物：`p1a_pitch_stratified_metrics.csv`

### 1.2 Yaw-block 分层（R100 3.2）✅ 已完成

**Split manifest 读取成功**：
- 路径：`v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold{0-4}.json`
- 字段：`record_id, yaw_deg, pitch_deg, yaw_idx, pitch_idx, ocs_total, ..., png_path, exr_linear_path`
- method = `circ_yaw_block`, seed = 42, n_total = 2664

**确认 circular yaw-block 结构**：每 fold 的 test 集是一段连续 yaw 弧段：

| Fold | Test Yaw Block | N |
|---|---|---|
| 0 | [0, 70°] | 555 |
| 1 | [75, 145°] | 555 |
| 2 | [150, 215°] | 518 |
| 3 | [220, 285°] | 518 |
| 4 | [290, 355°] | 518 |

按 yaw-block 分层重算（每 fold 的 test 集即一个 block）：

| Channel | Fold | Test Yaw Block | Circular MAE | Within-6 | Coarse45 |
|---|---|---|---|---|---|
| C2 | 0 | [0,70°] | 15.12 | 13.3% | 13.3% |
| C2 | 1 | [75,145°] | 16.46 | 16.0% | 16.8% |
| C2 | 2 | [150,215°] | **23.58** | **0.0%** | **0.0%** |
| C2 | 3 | [220,285°] | **7.50** | **42.9%** | **28.6%** |
| C2 | 4 | [290,355°] | **26.59** | 8.1% | **0.0%** |
| C3_img | 0 | [0,70°] | 20.89 | 31.5% | 31.5% |
| C3_img | 1 | [75,145°] | 14.43 | 18.9% | 14.1% |
| C3_img | 2 | [150,215°] | 21.57 | 16.4% | 20.7% |
| C3_img | 3 | [220,285°] | 14.69 | 26.1% | 23.6% |
| C3_img | 4 | [290,355°] | 9.86 | 34.9% | **0.0%** |
| C3_joint | 0 | [0,70°] | 20.16 | 34.2% | 34.2% |
| C3_joint | 1 | [75,145°] | 15.15 | 18.0% | 13.7% |
| C3_joint | 2 | [150,215°] | 19.03 | 17.6% | 19.5% |
| C3_joint | 3 | [220,285°] | 17.71 | 27.2% | 23.4% |
| C3_joint | 4 | [290,355°] | 9.34 | 35.5% | **0.0%** |

**关键发现（最重要）**：
1. **C2 yaw-block 异质性极强**：fold3 [220,285°] MAE 仅 7.5 bins（within-6=42.9%，远优于 random），但 fold2/fold4 退化到 23-27 bins（差于 random=18）。
2. **C3 异质性较弱但仍明显**：MAE 在 9.3-21.6 bins 间波动。
3. **某些 block coarse45=0**：C2 fold2/fold4、C3 fold4 连 45° 粗粒度都完全错。
4. **诊断意义**：yaw-block 外推失败不是均匀的，取决于 test 弧段相对 train 弧段位置和该弧段 OCS 局部可分性。这强化 P0 的"输入签名重叠 + 协议性外推鸿沟"叙事，而非"yaw 物理普遍不可观测"。

产物：`p1a_yaw_block_stratified_metrics.csv`

### 1.3 Baseline 改理论值（R100 3.3）✅ 已完成

| Metric | 修正前 (Monte Carlo) | 修正后 (理论值) |
|---|---|---|
| Circular MAE (bins) | 18.0528 | **18.0** |

理论推导：72-bin circular distance d 取值 0-36，d=1..35 各 2 次、d=0 和 d=36 各 1 次，期望 = Σ(d·count)/72 = 18.0。

差异 0.05 bins，不改变任何结论。后续材料统一使用 18.0。

产物：`p1a_random_baseline_theoretical.json`、`p1a_baseline_corrected.md`

### 1.4 Pooled weighted metrics（R100 3.4）✅ 已完成

| Channel | Pooled MAE | Per-fold mean MAE | 差异 |
|---|---|---|---|
| C2_baseline_4dim | 17.79 | 17.85 | -0.06 |
| C3_image_only | 16.33 | 16.29 | +0.04 |
| C3_joint | 16.32 | 16.28 | +0.04 |

**口径说明**：
- 主表（97 号）用 **per-fold unweighted mean ± fold std**。
- FIX01 新增 **pooled sample-level weighted metrics**。
- 两者差异 < 0.1 bins（fold 样本数 555/555/518/518/518 接近），不改变结论。

产物：`p1a_channel_pooled_metrics.csv`

### 1.5 Claim 收窄（R100 3.5）✅ 已完成

97 号原表述（已收窄）：
- ❌ 原："图像通道携带更多姿态信息" / "确实携带更多姿态信息"
- ✅ 改："C3 image-based 模型输出在 circular/within-k/coarse45 指标上弱优于 C2 OCS-only；这提示图像通道在当前模型输出中保留了更多可用姿态线索。"

不写成对图像通道信息量的强证明（未做 embedding/logit/输入信息量分析）。

## 2. 更新后的核心结论

### 2.1 整体指标（pooled，理论 baseline）

| Channel | Exact | Circular MAE | Within-6 | Coarse45 | Coarse90 |
|---|---|---|---|---|---|
| C2_baseline_4dim | 0.00% | 17.79 | 16.0% | 11.8% | ~24% |
| C3_image_only | 0.00% | 16.33 | 25.6% | 18.1% | ~25% |
| C3_joint | 0.00% | 16.32 | 26.5% | 18.3% | ~25% |
| **Random (理论)** | 1.39% | **18.0** | 18.1% | 12.5% | 25.0% |

### 2.2 分层揭示的新结构

```text
1. Yaw-block 是主导异质性来源（MAE 跨度 7.5-26.6 bins, 跨度 19 bins）。
2. Pitch 影响小（MAE 跨度 16.1-18.7 bins, 跨度 2.6 bins）。
3. 某些 yaw 弧段（C2 fold3）OCS 几乎可用，另一些（C2 fold2/fold4）完全失败。
4. 这证明外推失败是协议性、位置依赖的，而非 yaw 物理普遍不可观测。
```

## 3. 阶段门判断（FIX01 后）

```text
✅ P1-A 第一阶段（含分层）只读指标重算完成。
❌ 不支持进入 P1-A 第二阶段（训练侧 continuous/circular head）：
   - 整体 circular MAE 仅优 random 1-2 bins；
   - 分层显示异质性来自输入/协议（yaw-block 位置），非判据；
   - 改判据不改变输入可辨识性不足。
✅ 建议 P1-A 作为论文指标重构 + 异质性诊断材料，停止 P1-A 训练侧改进。
⚠️ 条件允许后续 D 类只读导出（logits/embedding），但不阻塞主链。
```

详见 `p1a_stage_gate_matrix_FIX01.md`。

## 4. 未触碰声明

```text
✅ 未训练模型
✅ 未新渲染
✅ 未推理生成新预测（只读取已有 samples.npz + split manifest）
✅ 未加载 checkpoint forward（logits 仍缺失，按 R100 要求未导出）
✅ 未改 split / 模型 / loss / head / 超参 / seed
✅ 未覆盖 R04 负结果链
✅ 未改论文正文
✅ 未改 CLAUDE.md
✅ 未触发头A/头B大合并裁决
✅ 未写入成果区
✅ 未启动 P1-B / P2

只做了：
- 读取既有 C2/C3 samples.npz + split manifest
- numpy/pandas 分层指标重算（pitch band、yaw-block）
- 理论 baseline 计算、pooled weighted metrics
- claim 文本收窄
```

## 5. 产出文件清单

### 5.1 报告
- `98_1C-B4-FIX01_P1-A分层指标与baseline口径修正_Claude执行报告.md`（本文件）

### 5.2 脚本
- `v0.4_results/09_p1a_metric_recompute/p1a_fix01_stratify.py`

### 5.3 新增/更新产物（R100 5 最低产物要求）

| 文件 | 内容 | R100 要求 |
|---|---|---|
| `p1a_channel_pooled_metrics.csv` | Pooled sample-weighted 指标 | ✅ 要求 |
| `p1a_pitch_stratified_metrics.csv` | Pitch band 分层指标 | ✅ 要求 |
| `p1a_yaw_block_stratified_metrics.csv` | Yaw-block 分层指标 | ✅ 要求 |
| `p1a_baseline_corrected.md` | 理论 baseline 修正说明 | ✅ 要求 |
| `p1a_stage_gate_matrix_FIX01.md` | FIX01 阶段门矩阵 | ✅ 要求 |
| `p1a_random_baseline_theoretical.json` | 理论 baseline 数值 | 附加 |

### 5.4 保留产物（97 号 FIX01 前）
- `p1a_channel_fold_metrics.csv`、`p1a_channel_aggregated_stats.csv`
- `p1a_coarse_bin_metrics.csv`、`p1a_circular_error_distribution.csv`
- `p1a_within_k_curve.csv`、`p1a_random_baseline.json/md`
- `p1a_metric_recompute_summary.md`、`p1a_stage_gate_matrix.md`
- `p1a_metric_recompute.py`

## 6. 给 Codex/作者的待确认问题

```text
Q1. P1-A 第一阶段是否闭口？
   FIX01 已完成 pitch/yaw-block 分层、理论 baseline、pooled metrics、claim 收窄。
   yaw-block 分层成功读取 split manifest 并映射。是否接收 P1-A 第一阶段闭口？

Q2. 是否同意不进入 P1-A 第二阶段（训练侧改进）？
   整体 MAE 仅优 random 1-2 bins，分层显示异质性来自 yaw-block 位置而非判据。
   是否同意停止 P1-A 训练侧改进？

Q3. yaw-block 强异质性是否纳入论文叙事？
   C2 fold3 MAE=7.5（可用）vs fold2/fold4 MAE=23-27（失败）的强异质性
   是否作为 extrapolation gap 的位置依赖证据写入论文？

Q4. 是否进入头A/头B大合并裁决？
   头A R90 闭口，头B-B3/P0 闭口，P1-A 第一阶段（含分层）完成。
   是否可触发头A/头B大合并裁决，或继续暂缓？

Q5. P1-A 产物是否需同步到成果区？
   当前所有产出在 v0.4_results/09_p1a_metric_recompute/（诊断区）。
   是否作为头B材料同步到成果区？
```

## 7. 关联文件

```text
R100_Codex_审阅_1C-B4_P1-A初版合规但需FIX01分层与baseline修正.md
R99_Codex_裁决_1C-B3闭口后放行P1-A只读指标重算.md
97_1C-B4_P1-A只读指标重算与阶段门判断_Claude执行报告.md
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold{0-4}.json
v0.4_results/09_p1a_metric_recompute/ （所有产物）
```

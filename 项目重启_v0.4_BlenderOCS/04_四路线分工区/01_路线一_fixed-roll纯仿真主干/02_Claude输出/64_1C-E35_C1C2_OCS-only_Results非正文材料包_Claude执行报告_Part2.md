## 5. Figure Plans

### 5.1 Figure 1: OCS Feature Extraction Pipeline

**用途**: 展示从 OCS manifest 到 13 个特征配置的完整流程。

**内容设计**:
```text
[Flowchart]
Input: ocs_manifest_v0_4_fullrun.json (2664 records)
  ↓
Extract raw fields (24 fields):
  - OCS photometric: ocs_total, ocs_jinshuzhuti, ocs_taiyangnengban, ocs_yinshenban
  - Ratios: r_jinshuzhuti, r_taiyangnengban, r_yinshenban, ratio_j_t
  - Densities: ocs_density_* (OCS / pixel_count)
  - Visibility: frac_*, visibility_ratio
  - Log transforms: log_r_*, log_ratio_*, log_ocs_*, log_density_*
  - Sanity check: phase_angle_cos (constant in phase63)
  ↓
Pre-registered constants:
  epsilon=1e-8, ratio_clip=[1e-8, 1e8], log_clip=[-18.4, 18.4]
  ↓
Group into 14 pre-registered configs:
  Group A: Photometric OCS (9 configs: baseline, R, I, N, L, M1, M3, M4)
  Group B: Visibility control (2 configs: P, M5)
  Group C: Mixed OCS+visibility (2 configs: M2, M6)
  Group D: Constant sanity check (1 config: constant_check_1d)
  ↓
C1: Pre-registration integrity check
  - Constant sanity check: PASS (phase_angle_cos is constant)
  - 14 configs complete
  ↓
C2: OCS-only screening
  - 13 configs enter C2 (exclude constant_check_1d)
  - 5-fold circular yaw-block holdout
  - Fixed MLP protocol
```

**数据来源**:
- feature_definitions.json
- feature_extraction_run_summary.json (若可用)
- c2_screening_summary.json

**Caption 草案**:

**Figure 1. Pre-registered OCS feature extraction pipeline.**

From OCS manifest to 14 feature configurations. All feature definitions, constants, and claim class boundaries were pre-registered before feature extraction. The constant sanity check (phase_angle_cos) passed in C1, confirming code correctness. 13 configurations entered C2 OCS-only screening; constant_check_1d was excluded as designed.

**图注要点**:
- Pre-registration prevents data-driven feature tuning
- 24 raw feature fields computed from OCS manifest
- Claim class assignment: photometric OCS / visibility control / mixed / sanity check
- C1 = integrity check, C2 = screening evaluation
- Pipeline is deterministic and reproducible

---

### 5.2 Figure 2: Circular Yaw-Block Holdout Strategy

**用途**: 说明 5-fold circular yaw-block holdout 的跨 yaw 泛化测试设计。

**内容设计**:
```text
[Diagram: Circular yaw grid]

72-bin yaw grid (5° resolution, 0°-360°)
Arranged in circular layout:
  Bin 0 (0°-5°) → Bin 1 (5°-10°) → ... → Bin 71 (355°-360°) → [wraps to Bin 0]

5-Fold Circular Yaw-Block Holdout:

Fold 0:
  Train: Bins 15-71 (57 bins)
  Val:   Bins 0-7 (8 bins, adjacent to test)
  Test:  Bins 8-14 (7 bins)

Fold 1:
  Train: Bins 0-14, 30-71 (57 bins)
  Val:   Bins 15-22 (8 bins)
  Test:  Bins 23-29 (7 bins)

Fold 2:
  Train: Bins 0-29, 45-71 (57 bins)
  Val:   Bins 30-37 (8 bins)
  Test:  Bins 38-44 (7 bins)

Fold 3:
  Train: Bins 0-44, 60-71 (57 bins)
  Val:   Bins 45-52 (8 bins)
  Test:  Bins 53-59 (7 bins)

Fold 4:
  Train: Bins 0-59, 8-71 (wraps, 57 bins)
  Val:   Bins 60-67 (8 bins)
  Test:  Bins 68-71, 0-2 (7 bins, wraps)

Key properties:
- Each fold tests a non-overlapping 7-bin yaw block
- Validation bins are adjacent to test (local interpolation check)
- Training bins exclude test and val (strict holdout)
- Circular wrapping ensures coverage of 0°/360° boundary
- Total: 5 × 7 = 35 test bins (covers ~49% of yaw space)
```

**数据来源**:
- split_dataset.py circular_yaw_block_holdout logic
- c2_screening_summary.json fold definitions

**Caption 草案**:

**Figure 2. Five-fold circular yaw-block holdout strategy.**

The yaw space (72 bins, 5° resolution) is partitioned into 5 non-overlapping test blocks of 7 bins each. Each fold trains on 57 bins, validates on 8 adjacent bins, and tests on 7 holdout bins. This design evaluates cross-yaw generalization under strict block holdout, preventing the model from seeing nearby yaw angles during training. Fold 4 wraps across the 0°/360° boundary to ensure circular coverage.

**图注要点**:
- Strict yaw holdout: no test yaw seen during training
- Adjacent validation bins: local interpolation diagnostic
- Circular wrapping: handles 0°/360° boundary
- 5-fold coverage: 35/72 bins tested
- Design rationale: tests whether OCS features generalize across unseen yaw blocks

---

### 5.3 Figure 3: Yaw CMAE vs Within-3-Bins Rate (Scatter Plot)

**用途**: 展示 C2 结果的 yaw CMAE 和 within-3 分布，按 claim class 着色分组。

**内容设计**:
```text
[Scatter plot]
X-axis: Yaw CMAE (deg), range [0, 130]
Y-axis: Within-3-bins rate (%), range [0, 20]

Data points: 13 configs, each plotted as (mean_yaw_cmae, mean_within_3_bins_rate)

Color coding by claim class:
  - Blue circles: Photometric OCS sub-type (a) (6 points)
  - Green triangles: Photometric OCS sub-type (b) (3 points)
  - Orange squares: Visibility control (2 points)
  - Red diamonds: Mixed OCS+visibility (2 points)

Horizontal reference line:
  y = 9.72% (within-3 chance-level, dashed gray line)

Annotations:
  - Label key configs: baseline_4dim, M6_all_nongeo_13d, P_pixelfrac_3d, M5_pixelfrac_only_4d
  - Region interpretation:
      Low CMAE + Low within-3 = weak signal
      High CMAE + Low within-3 = poor localization
      Low CMAE + High within-3 = coarse localization, no exact hit
      High CMAE + High within-3 = mixed signal

Legend:
  - Photometric OCS (a): pure photometric
  - Photometric OCS (b): visibility-normalized
  - Visibility control: geometry only
  - Mixed: OCS + visibility
```

**数据来源**:
- c2_screening_summary.json:
  - mean_test_yaw_circular_mae_deg
  - mean_test_yaw_within_3_bins_rate × 100 (convert to %)

**具体数据**:

| Config | Claim Class | CMAE (deg) | Within-3 (%) |
|--------|------------|-----------|--------------|
| baseline_4dim | Photometric OCS (a) | 89.25 | 8.16 |
| R_ratio_2d | Photometric OCS (a) | 84.15 | 6.31 |
| R_ratio_3d | Photometric OCS (a) | 80.36 | 10.45 |
| I_interpart_1d | Photometric OCS (a) | 107.78 | 2.75 |
| N_density_3d | Photometric OCS (b) | 120.26 | 3.96 |
| L_logratio_3d | Photometric OCS (a) | 83.17 | 7.70 |
| M1_ratio_log_5d | Photometric OCS (a) | 83.05 | 7.83 |
| M3_density_ratio_5d | Photometric OCS (b) | 97.47 | 10.51 |
| M4_log_density_ratio_9d | Photometric OCS (b) | 115.74 | 12.05 |
| P_pixelfrac_3d | Visibility control | 98.15 | 14.79 |
| M5_pixelfrac_only_4d | Visibility control | 95.75 | 15.57 |
| M2_ratio_pixelfrac_5d | Mixed | 98.25 | 14.74 |
| M6_all_nongeo_13d | Mixed | 107.18 | 14.60 |

**Caption 草案**:

**Figure 3. Yaw circular mean absolute error (CMAE) vs within-3-bins rate for 13 C2 configurations.**

Each point represents the mean across 5 folds. The dashed horizontal line marks the within-3 chance-level baseline (9.72%). Visibility control and mixed configs cluster in the high within-3 region (14.6%-15.6%), indicating coarse localization from geometry features. Pure photometric OCS configs (sub-type a) show lower within-3 rates (2.8%-10.5%) and variable CMAE, suggesting weaker localization signal. Despite some configs exceeding chance-level within-3, all configs achieved 0.00% exact-bin yaw accuracy, indicating that coarse neighborhood clustering did not translate to exact-bin generalization.

**图注要点**:
- Chance-level within-3 = 9.72% (7/72, FIX01 corrected)
- Visibility features → higher within-3, but still no exact-bin hits
- Photometric OCS (a) → lower within-3, weaker localization
- Photometric OCS (b) → intermediate, density normalization effect
- Key insight: coarse localization ≠ exact-bin generalization

---

### 5.4 Figure 4: Pitch Accuracy by Config (Grouped Bar Chart)

**用途**: 展示 13 个配置的 pitch exact-bin accuracy，作为二级诊断指标。

**内容设计**:
```text
[Grouped bar chart]
X-axis: Config name (grouped by claim class)
Y-axis: Pitch exact-bin accuracy (%), range [0, 5]

Groups (x-axis):
  Group 1: Photometric OCS (a) — 6 bars
    baseline_4dim, R_ratio_2d, R_ratio_3d, I_interpart_1d, L_logratio_3d, M1_ratio_log_5d
  Group 2: Photometric OCS (b) — 3 bars
    N_density_3d, M3_density_ratio_5d, M4_log_density_ratio_9d
  Group 3: Visibility control — 2 bars
    P_pixelfrac_3d, M5_pixelfrac_only_4d
  Group 4: Mixed OCS+visibility — 2 bars
    M2_ratio_pixelfrac_5d, M6_all_nongeo_13d

Bar colors: match Figure 3 color scheme

Error bars: ± std across 5 folds

Horizontal reference lines:
  - No obvious chance-level for pitch (different from yaw)
  - But note: pitch range 2.56%-4.37%, all below 5%

Annotations:
  - Highest: M4_log_density_ratio_9d (4.37%)
  - Lowest: R_ratio_2d, baseline_4dim (2.56%)
```

**数据来源**:
- c2_screening_summary.json:
  - mean_test_pitch_acc × 100 (convert to %)
  - std_test_pitch_acc × 100

**具体数据**:

| Config | Pitch Acc (%) | Std (%) |
|--------|--------------|---------|
| baseline_4dim | 2.56 | 1.05 |
| R_ratio_2d | 2.56 | 0.53 |
| R_ratio_3d | 2.62 | 1.11 |
| I_interpart_1d | 2.69 | 1.33 |
| N_density_3d | 3.41 | 1.55 |
| L_logratio_3d | 3.18 | 0.39 |
| M1_ratio_log_5d | 3.07 | 0.41 |
| M3_density_ratio_5d | 3.15 | 1.21 |
| M4_log_density_ratio_9d | 4.37 | 1.22 |
| P_pixelfrac_3d | 2.66 | 0.69 |
| M5_pixelfrac_only_4d | 2.59 | 0.44 |
| M2_ratio_pixelfrac_5d | 3.23 | 1.00 |
| M6_all_nongeo_13d | 3.30 | 1.33 |

**Caption 草案**:

**Figure 4. Pitch exact-bin accuracy by configuration, grouped by claim class.**

Pitch accuracy serves as a secondary diagnostic metric. All configs show low pitch accuracy (2.56%-4.37%), with no clear separation between claim classes. The highest-dimensional config (M4_log_density_ratio_9d, 9D) reached 4.37%, but this does not constitute strong pitch generalization and does not alter the C2 null verdict. Pitch results are reported for completeness but do not change the primary conclusion based on yaw holdout generalization.

**图注要点**:
- Pitch is secondary diagnostic, not primary success criterion
- Range: 2.56%-4.37%, all low
- No claim class shows strong pitch signal
- M4 (9D) slightly higher, but not significant positive
- Pitch does not compensate for yaw null result

---

## 6. Results Skeleton (Chapter Structure Only)

### 6.1 用途

提供 Results 章节的骨架结构与 bullet 要点，**不写完整正文段落**。

### 6.2 Results 章节结构

```markdown
3. Results

3.1 C1: Pre-Registration and Feature Extraction Integrity

**Bullet points (NOT full prose):**
- 14 feature configs pre-registered before data extraction
- Claim class definitions: photometric OCS (sub-type a/b), visibility control, mixed, sanity check
- Constant sanity check (phase_angle_cos) passed: confirms code correctness
- All 24 raw feature fields extracted from 2664 OCS manifest records
- Pre-registered constants applied: epsilon, ratio clipping, log clipping
- Output: 13 configs enter C2, 1 config (constant_check_1d) excluded as designed
- **Figure 1**: Feature extraction pipeline
- **Table 1**: Configuration overview

3.2 C2: Fixed-Protocol OCS-Only Screening

**Bullet points:**
- Protocol: 5-fold circular yaw-block holdout, fixed MLP (3-layer, hidden_dim=128)
- No hyperparameter search, max_epochs=30, Adam (lr=1e-3)
- Primary criterion: exact-bin yaw accuracy (72-bin grid, 5° resolution)
- **Table 2**: C2 screening results
- **Figure 2**: Circular yaw-block holdout design

**C2 Verdict:**
- All 13 configs: yaw_acc = 0.00% (mean ± std = 0.00 ± 0.00 across 5 folds)
- mean_test_yaw_correct_count = 0.0 for all configs
- **Null result**: No config achieved exact-bin yaw generalization under fixed-protocol yaw-block holdout

3.3 Diagnostic Observations

**3.3.1 Within-3-Bins Coarse Localization**

**Bullet points:**
- within-3-bins: circular distance ≤3 bins (including exact bin)
- Chance-level = 7/72 = 9.72% (FIX01 corrected)
- Range across configs: 2.75% - 15.57%
- Visibility control configs: 14.79%, 15.57% (above chance)
- Mixed configs: 14.60%, 14.74% (above chance)
- Photometric OCS (a): 2.75% - 10.45% (mostly near or below chance)
- Photometric OCS (b): 3.96% - 12.05% (near or slightly above chance)
- Interpretation: some coarse neighborhood clustering from visibility features, but no exact-bin hits
- **Figure 3**: Yaw CMAE vs within-3 scatter

**3.3.2 Pitch Accuracy (Secondary Diagnostic)**

**Bullet points:**
- Pitch exact-bin accuracy: secondary diagnostic, not primary criterion
- Range: 2.56% - 4.37%
- Highest: M4_log_density_ratio_9d (4.37%)
- No clear separation by claim class
- Does not alter C2 null verdict
- **Figure 4**: Pitch accuracy grouped bar chart

3.4 Failure Mode Analysis by Claim Class

**Bullet points:**
- **Table 3**: C2 results grouped by claim class
- Photometric OCS (a) — 6 configs: pure photometric, all null
- Photometric OCS (b) — 3 configs: visibility-normalized photometric, all null
- Visibility control — 2 configs: geometry-only, all null
- Mixed OCS+visibility — 2 configs: combined, all null
- Key observation: no claim class succeeded, ruling out single-channel dominance hypothesis
- Dimensionality (1D-13D) did not drive success

3.5 Observability Boundary Interpretation

**Bullet points (NOT full prose):**
- C2 establishes a controlled null baseline for OCS-only low-dim features (1-13D)
- Fixed-protocol negative result: pre-registered, no post-hoc tuning
- Scope: phase63 fixed-roll, circular yaw-block holdout, MLP architecture
- Does NOT claim: OCS is physically uninformative in general
- Does NOT claim: all architectures / feature engineering / tasks will fail
- Sets baseline for future image-only and joint-channel comparisons
- Observability boundary: current feature set + MLP + yaw-block holdout → no exact-bin generalization
```

### 6.3 重要说明

以上是 **骨架结构与 bullet 要点**，不是完整 Results 正文段落。实际论文写作时需将 bullet 展开为完整句子和段落，但当前阶段不放行该步骤（R63 红线）。

---

## 7. Supplementary Material Checklist

### 7.1 用途

列出需要准备的 Supplementary Material 清单，支持 Results 主文的数据透明度。

### 7.2 Supplementary Material 清单

**Supplementary Table S1: Raw Feature Definitions**
- 24 个 raw feature fields 的完整定义
- 公式、clipping 范围、epsilon 值
- 来源：feature_definitions.json

**Supplementary Table S2: Per-Fold Results (13 configs × 5 folds)**
- 每个 config 每个 fold 的完整指标
- 指标：yaw_acc, yaw_cmae, within_1/3/5, pitch_acc, yaw_correct_count, pitch_correct_count
- 来源：c2_screening_summary.json fold_results

**Supplementary Table S3: Training Curves Summary**
- 每个 config 每个 fold 的 best_val_avg_acc, final_epoch, early_stop 状态（若可用）
- 来源：各 fold result JSON 文件

**Supplementary Figure S1: All-Zero Yaw Accuracy Bar Chart**
- 13 configs 的 yaw_acc bar chart（全 0）
- 原计划作为主图，FIX01 后降级为 supplementary
- 用途：直观展示 null result

**Supplementary Figure S2: Yaw Within-1/3/5 Comparison**
- 13 configs 的 within-1-bin, within-3-bins, within-5-bins 比较
- Grouped bar chart 或 stacked bar
- 展示 coarse localization 梯度

**Supplementary Figure S3: Pitch Within-3-Bins**
- 与 pitch exact-bin 类似，展示 pitch 的 within-3 指标
- 用途：完整 pitch 诊断

**Supplementary Figure S4: Validation Accuracy Distribution**
- 13 configs 的 best_val_avg_acc 分布
- Box plot 或 violin plot
- 用途：检查训练稳定性与 overfitting

**Supplementary Data S1: Full Feature Matrix**
- enhanced_ocs_features.npz 的访问说明或摘要统计
- 不上传原始 .npz（文件大），提供统计描述

**Supplementary Data S2: Split Indices**
- 5-fold 的 train/val/test split indices
- 用于结果复现

**Supplementary Code: Training Script**
- train_baseline.py 的代码副本或链接
- 展示固定协议实现细节

### 7.3 优先级排序

**High priority (必须有)**:
- S1: Raw feature definitions
- S2: Per-fold results
- S1 (Fig): All-zero yaw accuracy bar chart

**Medium priority (建议有)**:
- S3: Training curves summary
- S2 (Fig): Within-1/3/5 comparison
- S4 (Fig): Validation accuracy distribution

**Low priority (可选)**:
- S3 (Fig): Pitch within-3
- Data S1/S2: Full data access
- Code: Training script (可以作为 GitHub repo 链接)

---

（待续 Part 3：Claim Boundary Checklist 与总结）

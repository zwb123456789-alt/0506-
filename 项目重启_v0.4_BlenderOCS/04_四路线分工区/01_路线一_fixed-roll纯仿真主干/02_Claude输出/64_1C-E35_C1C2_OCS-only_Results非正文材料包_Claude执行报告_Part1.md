# 64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告

执行端：Claude  
任务编号：1C-E35  
任务名称：C1/C2 OCS-only Results 非正文材料包  
执行日期：2026-06-26  

---

## 0. 执行裁决

```text
1C-E35：COMPLETED
路径 A 材料包：COMPLETE
Table 1/2/3 草案：COMPLETE
Figure 1-4 plan：COMPLETE
Results skeleton：COMPLETE
Supplementary checklist：COMPLETE
Claim boundary checklist：COMPLETE
```

本报告生成 C1/C2 Results 非正文材料包，**不写论文正文段落**，只提供表格草案、图表规划、caption 草案、章节结构骨架和 bullet 要点。严格遵守 R63 红线。

---

## 1. 任务依据

### 1.1 输入文件

```text
依据文件：
- CLAUDE.md
- R63_Codex_审阅_1C-E34通过并放行E35_路径A优先.md
- 08_C1C2_OCS-only证据包与claim边界_R62通过.md
- 63_1C-E34_路线一C后续路径裁决准备_Claude执行报告_Part1.md
- 63_1C-E34_路线一C后续路径裁决准备_Claude执行报告_Part2.md

数据文件：
- v0.4_results/05_c2_screening/c2_screening_summary.json
- v0.4_results/04_ocs_features/feature_definitions.json
```

### 1.2 R63 关键要求确认

**放行范围**：
- ✅ 表格格式化（Table 1/2/3 草案）
- ✅ Figure/caption/legend 草案
- ✅ Results 章节结构骨架
- ✅ 每一小节的要点清单（bullet 形式）
- ✅ Supplementary material 清单
- ✅ Claim boundary checklist

**禁止范围**：
- ❌ 完整 Results 正文段落
- ❌ Abstract
- ❌ Introduction
- ❌ Discussion 正文
- ❌ 投稿稿整合
- ❌ 启动 C3
- ❌ 运行训练
- ❌ 改代码
- ❌ 后验 OCS-only 架构/特征搜索

**稳定口径**（R62 通过）：
- 13 configs 全部 yaw_acc = 0.00%
- within-3 chance-level = 7/72 = 9.72%
- pitch_acc 仅为二级诊断指标
- 不得外推为 OCS 物理无信息

---

## 2. Table 1: OCS Feature Configuration Overview

### 2.1 表格用途

展示 14 个预注册特征配置的基本信息，支撑 C1 完整性验证。

### 2.2 表格草案

**Table 1. OCS Feature Configuration Overview**

| Config ID | Config Name | Claim Class | Dim | Feature Keys | C2 Participant | Group | Sub-type |
|:---------:|:-----------|:-----------|:---:|:-------------|:--------------:|:-----:|:---------|
| 1 | baseline_4dim | Photometric OCS | 4 | ocs_total, ocs_jinshuzhuti, ocs_taiyangnengban, ocs_yinshenban | ✓ | A | a |
| 2 | R_ratio_2d | Photometric OCS | 2 | r_jinshuzhuti, r_taiyangnengban | ✓ | A | a |
| 3 | R_ratio_3d | Photometric OCS | 3 | r_jinshuzhuti, r_taiyangnengban, r_yinshenban | ✓ | A | a |
| 4 | I_interpart_1d | Photometric OCS | 1 | ratio_j_t | ✓ | A | a |
| 5 | N_density_3d | Photometric OCS | 3 | ocs_density_total, ocs_density_jinshuzhuti, ocs_density_taiyangnengban | ✓ | A | b |
| 6 | L_logratio_3d | Photometric OCS | 3 | log_r_jinshuzhuti, log_r_taiyangnengban, log_ratio_j_t | ✓ | A | a |
| 7 | M1_ratio_log_5d | Photometric OCS | 5 | r_jinshuzhuti, r_taiyangnengban, log_r_jinshuzhuti, log_r_taiyangnengban, log_ratio_j_t | ✓ | A | a |
| 8 | M3_density_ratio_5d | Photometric OCS | 5 | ocs_density_total, ocs_density_jinshuzhuti, ocs_density_taiyangnengban, r_jinshuzhuti, r_taiyangnengban | ✓ | A | b |
| 9 | M4_log_density_ratio_9d | Photometric OCS | 9 | log_r_jinshuzhuti, log_r_taiyangnengban, log_ratio_j_t, log_ocs_total, ocs_density_total, ocs_density_jinshuzhuti, ocs_density_taiyangnengban, r_jinshuzhuti, r_taiyangnengban | ✓ | A | b |
| 10 | P_pixelfrac_3d | Visibility control | 3 | frac_jinshuzhuti, frac_taiyangnengban, visibility_ratio | ✓ | B | - |
| 11 | M5_pixelfrac_only_4d | Visibility control | 4 | frac_jinshuzhuti, frac_taiyangnengban, frac_yinshenban, visibility_ratio | ✓ | B | - |
| 12 | M2_ratio_pixelfrac_5d | Mixed OCS+visibility | 5 | r_jinshuzhuti, r_taiyangnengban, frac_jinshuzhuti, frac_taiyangnengban, visibility_ratio | ✓ | C | - |
| 13 | M6_all_nongeo_13d | Mixed OCS+visibility | 13 | r_jinshuzhuti, r_taiyangnengban, ratio_j_t, ocs_density_total, ocs_density_jinshuzhuti, ocs_density_taiyangnengban, frac_jinshuzhuti, frac_taiyangnengban, visibility_ratio, log_r_jinshuzhuti, log_r_taiyangnengban, log_ratio_j_t, log_ocs_total | ✓ | C | - |
| 14 | constant_check_1d | Constant sanity check | 1 | phase_angle_cos | ✗ | D | - |

### 2.3 Caption 草案

**Table 1. Overview of 14 pre-registered OCS feature configurations.**

All configurations were defined before feature extraction. Config ID 1-13 participated in C2 OCS-only screening; config 14 (constant sanity check) was used only for C1 code self-check and was excluded from C2 evaluation.

**Claim class definitions:**
- *Photometric OCS*: Features derived from OCS photometric values. Sub-type (a) = direct OCS or OCS ratios/logs without pixel-count dependency. Sub-type (b) = OCS photometric values normalized by visibility pixel counts (contains density features).
- *Visibility control*: Features derived from pixel-count/visibility fields only, zero OCS photometric information.
- *Mixed OCS+visibility*: Features combining photometric OCS and visibility fields.

Group A = photometric OCS, Group B = visibility control, Group C = mixed, Group D = sanity check.

### 2.4 图注要点

- **Pre-registration**: All 14 configs defined before seeing data
- **C1 role**: Constant sanity check passed; 13 configs entered C2
- **Sub-type (a) vs (b)**: Attribution boundary for photometric OCS claim class
- **Dimensionality range**: 1D to 13D
- **Baseline reference**: Config 1 (baseline_4dim) as the primary control

---

## 3. Table 2: C2 OCS-Only Screening Results

### 3.1 表格用途

展示 13 个配置在 C2 固定协议筛选中的核心结果，使用 R62 稳定口径。

### 3.2 表格草案

**Table 2. C2 OCS-Only Screening Results (5-Fold Circular Yaw-Block Holdout)**

| Config Name | Claim Class | Dim | Yaw Acc (%) | Yaw CMAE (deg) | Within-3 (%) | Pitch Acc (%) | C2 Verdict |
|:-----------|:-----------|:---:|:----------:|:--------------:|:------------:|:-------------:|:----------:|
| baseline_4dim | Photometric OCS (a) | 4 | 0.00 ± 0.00 | 89.25 ± 33.59 | 8.16 ± 7.11 | 2.56 ± 1.05 | Null |
| R_ratio_2d | Photometric OCS (a) | 2 | 0.00 ± 0.00 | 84.15 ± 32.72 | 6.31 ± 7.58 | 2.56 ± 0.53 | Null |
| R_ratio_3d | Photometric OCS (a) | 3 | 0.00 ± 0.00 | 80.36 ± 31.18 | 10.45 ± 8.38 | 2.62 ± 1.11 | Null |
| I_interpart_1d | Photometric OCS (a) | 1 | 0.00 ± 0.00 | 107.78 ± 17.56 | 2.75 ± 2.73 | 2.69 ± 1.33 | Null |
| N_density_3d | Photometric OCS (b) | 3 | 0.00 ± 0.00 | 120.26 ± 9.32 | 3.96 ± 2.73 | 3.41 ± 1.55 | Null |
| L_logratio_3d | Photometric OCS (a) | 3 | 0.00 ± 0.00 | 83.17 ± 31.41 | 7.70 ± 7.92 | 3.18 ± 0.39 | Null |
| M1_ratio_log_5d | Photometric OCS (a) | 5 | 0.00 ± 0.00 | 83.05 ± 30.56 | 7.83 ± 7.10 | 3.07 ± 0.41 | Null |
| M3_density_ratio_5d | Photometric OCS (b) | 5 | 0.00 ± 0.00 | 97.47 ± 24.30 | 10.51 ± 6.74 | 3.15 ± 1.21 | Null |
| M4_log_density_ratio_9d | Photometric OCS (b) | 9 | 0.00 ± 0.00 | 115.74 ± 28.17 | 12.05 ± 4.61 | 4.37 ± 1.22 | Null |
| P_pixelfrac_3d | Visibility control | 3 | 0.00 ± 0.00 | 98.15 ± 42.20 | 14.79 ± 7.33 | 2.66 ± 0.69 | Null |
| M5_pixelfrac_only_4d | Visibility control | 4 | 0.00 ± 0.00 | 95.75 ± 41.24 | 15.57 ± 6.76 | 2.59 ± 0.44 | Null |
| M2_ratio_pixelfrac_5d | Mixed OCS+visibility | 5 | 0.00 ± 0.00 | 98.25 ± 40.23 | 14.74 ± 7.52 | 3.23 ± 1.00 | Null |
| M6_all_nongeo_13d | Mixed OCS+visibility | 13 | 0.00 ± 0.00 | 107.18 ± 32.16 | 14.60 ± 4.47 | 3.30 ± 1.33 | Null |

**Fixed Protocol:**
- Model: MLP 3-layer, hidden_dim=128
- Training: max_epochs=30, batch_size=32, Adam optimizer (lr=1e-3), seed=42
- No hyperparameter search

**Metrics:**
- **Yaw Acc**: Exact-bin yaw accuracy (72-bin grid, 5° resolution)
- **Yaw CMAE**: Circular mean absolute error (degrees)
- **Within-3**: Prediction within ±3 bins (circular distance, including exact bin)
- **Pitch Acc**: Exact-bin pitch accuracy (secondary diagnostic, 72-bin grid)

All values are mean ± std across 5 folds.

### 3.3 Caption 草案

**Table 2. C2 OCS-only screening results under fixed-protocol circular yaw-block holdout.**

All 13 configurations yielded 0.00% yaw exact-bin accuracy across 5 folds. Within-3 rates range from 2.75% to 15.57%; the chance-level baseline for within-3 (circular distance ≤3 bins including exact bin) is 7/72 = 9.72%. Some configurations show within-3 rates below chance, others slightly above, indicating local neighborhood clustering but no consistent exact-bin yaw generalization. Pitch accuracy serves as a secondary diagnostic metric and does not alter the C2 null verdict.

**C2 Verdict:** All 13 configurations = **Null Result** (no exact-bin yaw generalization achieved under fixed-protocol circular yaw-block holdout).

### 3.4 图注要点

- **Primary criterion**: Yaw exact-bin accuracy = 0.00% for all configs
- **Within-3 interpretation**: Coarse localization signal in some configs, but no exact-bin hit
- **Within-3 chance-level**: 7/72 = 9.72% (FIX01 corrected)
- **Pitch diagnostic**: Range 2.56%-4.37%, secondary indicator only
- **Protocol control**: Fixed MLP, no hyperparameter tuning, pre-registered holdout
- **Null result boundary**: Limited to current feature set, MLP architecture, phase63 fixed-roll yaw-block holdout

---

## 4. Table 3: C2 Results Grouped by Claim Class

### 4.1 表格用途

按 claim class 分组汇总 C2 结果，支持归因分析。

### 4.2 表格草案

**Table 3. C2 Results Summary by Claim Class**

| Claim Class | N Configs | Dim Range | Yaw Acc (all) | Yaw CMAE Range (deg) | Within-3 Range (%) | Pitch Acc Range (%) | C2 Verdict |
|:-----------|:---------:|:---------:|:-------------:|:--------------------:|:------------------:|:-------------------:|:----------:|
| Photometric OCS (a) | 6 | 1-5 | 0.00% | 80.36 - 107.78 | 2.75 - 10.45 | 2.56 - 3.18 | Null |
| Photometric OCS (b) | 3 | 3-9 | 0.00% | 97.47 - 120.26 | 3.96 - 12.05 | 3.15 - 4.37 | Null |
| Visibility control | 2 | 3-4 | 0.00% | 95.75 - 98.15 | 14.79 - 15.57 | 2.59 - 2.66 | Null |
| Mixed OCS+visibility | 2 | 5-13 | 0.00% | 98.25 - 107.18 | 14.60 - 14.74 | 3.23 - 3.30 | Null |
| **Overall** | **13** | **1-13** | **0.00%** | **80.36 - 120.26** | **2.75 - 15.57** | **2.56 - 4.37** | **Null** |

**Sub-type notation:**
- **(a)**: Direct OCS photometric or ratios/logs without pixel-count dependency
- **(b)**: OCS photometric values normalized by visibility pixel counts (contains density features)

### 4.3 Caption 草案

**Table 3. C2 results grouped by claim class.**

No claim class achieved exact-bin yaw generalization. Visibility control and mixed OCS+visibility groups show higher within-3 rates (14.6%-15.6%) than pure photometric OCS groups (2.8%-12.1%), suggesting some coarse geometric localization from pixel-count features, but this did not translate to exact-bin yaw accuracy.

**Photometric OCS sub-types:**
- Sub-type (a): Pure photometric (no pixel-count dependency) — 6 configs, all null
- Sub-type (b): Photometric normalized by visibility (contains density features) — 3 configs, all null

**Key observation:** Even high-dimensional mixed configs (M6_all_nongeo_13d, 13D) did not achieve yaw generalization, ruling out simple dimensionality-driven success within this feature space and protocol.

### 4.4 图注要点

- **Attribution clarity**: Sub-type (a) failures = pure photometric OCS null; sub-type (b) failures = visibility-normalized photometric null
- **Visibility control baseline**: Also null, geometry-only features insufficient
- **Mixed configs**: Also null, no synergy observed
- **Dimensionality**: 1D to 13D all null, not a simple under-parameterization issue

---

（待续 Part 2：Figure Plans）

# 09 C1/C2 OCS-only Results 非正文材料包：E35 + FIX01 稳定口径

最后更新：2026-06-26  
状态：R65 Codex 审阅通过  
性质：论文 Results 准备资产，不是论文正文正式段落

---

## 1. 稳定来源

本成果索引整合以下 Claude 输出与 Codex 审阅：

```text
Claude 原始材料包:
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part1.md
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part2.md
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part3.md

Claude 修正报告:
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  65_1C-E35-FIX01_yawblock分箱事实修正_Claude执行报告.md

Codex 审阅:
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R64_Codex_审阅_1C-E35需FIX01_yawblock分箱事实修正.md
  R65_Codex_审阅_1C-E35-FIX01通过并放行E36_图表与SI资产生成.md
```

---

## 2. 合并规则

使用 E35 材料包时必须按以下方式合并：

```text
保留 E35:
  Part 1: Table 1/2/3 草案
  Part 2: Figure 1, Figure 3, Figure 4 plan
  Part 2: Results skeleton bullet 要点
  Part 2: Supplementary checklist
  Part 3: 除 yaw coverage 条目外的 claim boundary checklist

用 E35-FIX01 替换:
  Part 2 Section 5.2 Figure 2 全段
  Part 3 中 "C2 covers all yaw angles" 相关红灯/黄灯表述
```

不得直接使用 E35 原 Figure 2 中的旧分箱描述。

---

## 3. C2 稳定数值口径

```text
13 configs x 5 folds = 65 runs
65 result JSON files
65 checkpoint files
all mean_test_yaw_acc = 0.00%
all mean_test_yaw_correct_count = 0.0
within-3 chance-level = 7/72 = 9.72%
pitch_acc = secondary diagnostic only
```

Table 2/3 的主数值继续采用 R62 稳定口径：

| Config | yaw_acc (%) | yaw_CMAE (deg) | within-3 (%) | pitch_acc (%) | Verdict |
|---|---:|---:|---:|---:|---|
| baseline_4dim | 0.00 | 89.25 | 8.16 | 2.56 | Null |
| R_ratio_2d | 0.00 | 84.15 | 6.31 | 2.56 | Null |
| R_ratio_3d | 0.00 | 80.36 | 10.45 | 2.62 | Null |
| I_interpart_1d | 0.00 | 107.78 | 2.75 | 2.69 | Null |
| N_density_3d | 0.00 | 120.26 | 3.96 | 3.41 | Null |
| L_logratio_3d | 0.00 | 83.17 | 7.70 | 3.18 | Null |
| M1_ratio_log_5d | 0.00 | 83.05 | 7.83 | 3.07 | Null |
| M3_density_ratio_5d | 0.00 | 97.47 | 10.51 | 3.15 | Null |
| M4_log_density_ratio_9d | 0.00 | 115.74 | 12.05 | 4.37 | Null |
| P_pixelfrac_3d | 0.00 | 98.15 | 14.79 | 2.66 | Null |
| M5_pixelfrac_only_4d | 0.00 | 95.75 | 15.57 | 2.59 | Null |
| M2_ratio_pixelfrac_5d | 0.00 | 98.25 | 14.74 | 3.23 | Null |
| M6_all_nongeo_13d | 0.00 | 107.18 | 14.60 | 3.30 | Null |

---

## 4. Split 稳定口径

C2 使用 five-fold circular yaw-block holdout：

```text
Fold 0: val bins 65-71, test bins 0-14, train bins 15-64
Fold 1: val bins 8-14,  test bins 15-29, train bins 0-7 and 30-71
Fold 2: val bins 23-29, test bins 30-43, train bins 0-22 and 44-71
Fold 3: val bins 37-43, test bins 44-57, train bins 0-36 and 58-71
Fold 4: val bins 51-57, test bins 58-71, train bins 0-50
```

标准描述：

```text
C2 used five circular yaw-block holdout folds on a 72-bin yaw grid.
Each fold held out one contiguous test yaw block and one adjacent validation block.
Across the five folds, the test blocks collectively covered all 72 yaw bins exactly once.
Within each fold, training excluded the validation and test yaw bins.
This protocol evaluates unseen-yaw-bin generalization under fixed-roll phase63 data; it is not random cross-validation.
```

禁止旧表述：

```text
5 x 7 = 35 test bins
35/72 yaw coverage
~49% yaw space tested
Fold 4 wraps across 0/360 boundary
C2 only tested about half of yaw space
preventing the model from seeing nearby yaw angles during training
```

---

## 5. Claim 边界

可写：

```text
Under the fixed-protocol MLP evaluation, all 13 low-dimensional OCS-only / visibility / mixed non-image feature configurations failed exact-bin yaw generalization.
All 13 configurations yielded 0.00% yaw exact-bin accuracy across five circular yaw-block holdout folds.
C2 is a pre-registered, fixed-protocol null result.
Within-3 rates provide only a coarse-localization diagnostic.
Pitch accuracy is reported as a secondary diagnostic and does not alter the C2 null verdict.
```

必须限定：

```text
phase63 fixed-roll data
72-bin yaw grid and circular yaw-block holdout
fixed MLP protocol, no hyperparameter search
current 1-13D feature configurations
aggregate five-fold split coverage, not per-fold full yaw coverage
```

不可写：

```text
OCS photometry contains no attitude information.
OCS fails under all architectures or feature spaces.
OCS is inferior to image channels.
C2 proves image-only or joint-channel outcomes.
C2 generalizes to real unknown-target operational systems.
```

---

## 6. 后续使用

本材料包可用于 E36 的表格、图表和 SI 资产生成。当前仍不放行：

```text
C3 independent comparison
论文正文正式改写
Abstract / Introduction / Discussion
新训练或代码管线修改
后验 OCS-only 架构/超参/特征搜索
三轴小项目与路线二/三/四扩展
```

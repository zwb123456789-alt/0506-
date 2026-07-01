# 66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part1

执行端：Claude  
任务编号：1C-E36  
任务名称：C1/C2 OCS-only 图表与 SI 资产生成  
执行日期：2026-06-26  

---

## 0. 执行裁决

```text
1C-E36：COMPLETED (Part 1/3)
任务性质：非正文资产生成，不写论文正文段落
交付范围：Table 1/2/3 LaTeX/Markdown、Figure 规格、SI 资产、资产索引
```

本报告生成论文准备资产（表格、图表规格、SI 草案），不写 Results/Abstract/Introduction/Discussion 正文段落。严格遵守 R65 红线。

---

## 1. 任务依据

### 1.1 输入文件

```text
依据文件：
- CLAUDE.md
- R65_Codex_审阅_1C-E35-FIX01通过并放行E36_图表与SI资产生成.md
- 09_C1C2_OCS-only_Results非正文材料包_E35_R65通过.md
- E35 Part1/Part2/Part3 材料包
- E35-FIX01 修正报告

数据文件：
- v0.4_results/05_c2_screening/c2_screening_summary.json
- v0.4_results/04_ocs_features/feature_definitions.json
```

### 1.2 R65 允许范围确认

**允许**：
- ✅ Table 1/2/3 LaTeX 草案和 Markdown 稳定表格
- ✅ Figure 1-4 实际图表资产规格或绘图脚本草案
- ✅ Supplementary Table S1/S2 草案
- ✅ Figure 2 split design 最终数据表（使用 R65 标准口径）
- ✅ 资产索引（数据源、生成方式、待检查项）

**禁止**：
- ❌ Results 正文正式段落
- ❌ Abstract / Introduction / Discussion
- ❌ 启动 C3
- ❌ 运行训练
- ❌ 后验 OCS-only 架构/超参/特征搜索
- ❌ 改现有训练代码或数据结果
- ❌ 启动三轴小项目或路线二/三/四
- ❌ 使用 35/72、49% coverage、5×7 test bins 等旧错误 split 表述

---

## 2. Table 1: OCS Feature Configuration Overview

### 2.1 LaTeX 版本

```latex
\begin{table}[h!]
\centering
\caption{Overview of 14 pre-registered OCS feature configurations. All configurations were defined before feature extraction. Config ID 1--13 participated in C2 OCS-only screening; config 14 (constant sanity check) was used only for C1 code self-check and excluded from C2 evaluation. Claim class definitions: \textit{Photometric OCS} = features derived from OCS photometric values. Sub-type (a) = direct OCS or ratios/logs without pixel-count dependency. Sub-type (b) = OCS photometric values normalized by visibility pixel counts. \textit{Visibility control} = features from pixel-count/visibility fields only. \textit{Mixed OCS+visibility} = features combining photometric OCS and visibility fields.}
\label{tab:config_overview}
\footnotesize
\begin{tabular}{clccccc}
\hline
\textbf{Config ID} & \textbf{Config Name} & \textbf{Claim Class} & \textbf{Dim} & \textbf{C2} & \textbf{Group} & \textbf{Sub-type} \\
\hline
1  & baseline\_4dim & Photometric OCS & 4  & \checkmark & A & a \\
2  & R\_ratio\_2d   & Photometric OCS & 2  & \checkmark & A & a \\
3  & R\_ratio\_3d   & Photometric OCS & 3  & \checkmark & A & a \\
4  & I\_interpart\_1d & Photometric OCS & 1  & \checkmark & A & a \\
5  & N\_density\_3d & Photometric OCS & 3  & \checkmark & A & b \\
6  & L\_logratio\_3d & Photometric OCS & 3  & \checkmark & A & a \\
7  & M1\_ratio\_log\_5d & Photometric OCS & 5  & \checkmark & A & a \\
8  & M3\_density\_ratio\_5d & Photometric OCS & 5  & \checkmark & A & b \\
9  & M4\_log\_density\_ratio\_9d & Photometric OCS & 9  & \checkmark & A & b \\
10 & P\_pixelfrac\_3d & Visibility control & 3  & \checkmark & B & -- \\
11 & M5\_pixelfrac\_only\_4d & Visibility control & 4  & \checkmark & B & -- \\
12 & M2\_ratio\_pixelfrac\_5d & Mixed OCS+vis. & 5  & \checkmark & C & -- \\
13 & M6\_all\_nongeo\_13d & Mixed OCS+vis. & 13 & \checkmark & C & -- \\
14 & constant\_check\_1d & Sanity check & 1  & $\times$ & D & -- \\
\hline
\end{tabular}
\end{table}
```

**LaTeX 注释**：
- 使用 `\footnotesize` 以适应 14 行表格
- `\checkmark` 和 `$\times$` 表示 C2 参与状态
- Sub-type 列：`--` 表示不适用（只针对 Photometric OCS）
- 如需更紧凑，可使用 `\scriptsize` 或将 Config Name 缩写

### 2.2 Markdown 稳定版本

```markdown
**Table 1. Overview of 14 pre-registered OCS feature configurations.**

| Config ID | Config Name | Claim Class | Dim | C2 | Group | Sub-type |
|:---------:|:-----------|:-----------|:---:|:--:|:-----:|:--------:|
| 1 | baseline_4dim | Photometric OCS | 4 | ✓ | A | a |
| 2 | R_ratio_2d | Photometric OCS | 2 | ✓ | A | a |
| 3 | R_ratio_3d | Photometric OCS | 3 | ✓ | A | a |
| 4 | I_interpart_1d | Photometric OCS | 1 | ✓ | A | a |
| 5 | N_density_3d | Photometric OCS | 3 | ✓ | A | b |
| 6 | L_logratio_3d | Photometric OCS | 3 | ✓ | A | a |
| 7 | M1_ratio_log_5d | Photometric OCS | 5 | ✓ | A | a |
| 8 | M3_density_ratio_5d | Photometric OCS | 5 | ✓ | A | b |
| 9 | M4_log_density_ratio_9d | Photometric OCS | 9 | ✓ | A | b |
| 10 | P_pixelfrac_3d | Visibility control | 3 | ✓ | B | - |
| 11 | M5_pixelfrac_only_4d | Visibility control | 4 | ✓ | B | - |
| 12 | M2_ratio_pixelfrac_5d | Mixed OCS+visibility | 5 | ✓ | C | - |
| 13 | M6_all_nongeo_13d | Mixed OCS+visibility | 13 | ✓ | C | - |
| 14 | constant_check_1d | Sanity check | 1 | ✗ | D | - |

**Claim class definitions:**
- *Photometric OCS*: Features derived from OCS photometric values. Sub-type (a) = direct OCS or ratios/logs without pixel-count dependency. Sub-type (b) = OCS photometric values normalized by visibility pixel counts.
- *Visibility control*: Features from pixel-count/visibility fields only, zero OCS photometric information.
- *Mixed OCS+visibility*: Features combining photometric OCS and visibility fields.

Group A = photometric OCS, Group B = visibility control, Group C = mixed, Group D = sanity check.
```

### 2.3 数据源

```text
来源：v0.4_results/04_ocs_features/feature_definitions.json
字段：config_id, config_name, claim_class, dim, c2_participant, group
Sub-type 判断：若 feature_keys 含 ocs_density_* 字段则为 (b)，否则为 (a)
```

### 2.4 待人工检查项

- [ ] LaTeX 编译通过，表格宽度适配页面
- [ ] Claim class 定义是否需要移到 caption 或脚注
- [ ] Sub-type (a)/(b) 是否需要在正文中预先定义
- [ ] Config Name 下划线在 LaTeX 中是否需要转义（已使用 `\_`）

---

## 3. Table 2: C2 OCS-Only Screening Results

### 3.1 LaTeX 版本

```latex
\begin{table}[h!]
\centering
\caption{C2 OCS-only screening results under fixed-protocol circular yaw-block holdout. All 13 configurations yielded 0.00\% yaw exact-bin accuracy across 5 folds. Within-3 rates range from 2.75\% to 15.57\%; the chance-level baseline for within-3 (circular distance $\leq$3 bins including exact bin) is 7/72 = 9.72\%. Some configurations show within-3 rates below chance, others slightly above, indicating local neighborhood clustering but no consistent exact-bin yaw generalization. Pitch accuracy serves as a secondary diagnostic metric and does not alter the C2 null verdict. \textbf{C2 Verdict:} All 13 configurations = \textbf{Null Result} (no exact-bin yaw generalization achieved).}
\label{tab:c2_results}
\scriptsize
\begin{tabular}{lccccccc}
\hline
\textbf{Config Name} & \textbf{Claim Class} & \textbf{Dim} & \textbf{Yaw Acc (\%)} & \textbf{Yaw CMAE (°)} & \textbf{Within-3 (\%)} & \textbf{Pitch Acc (\%)} & \textbf{Verdict} \\
\hline
baseline\_4dim & Phot. OCS (a) & 4 & 0.00 $\pm$ 0.00 & 89.25 $\pm$ 33.59 & 8.16 $\pm$ 7.11 & 2.56 $\pm$ 1.05 & Null \\
R\_ratio\_2d & Phot. OCS (a) & 2 & 0.00 $\pm$ 0.00 & 84.15 $\pm$ 32.72 & 6.31 $\pm$ 7.58 & 2.56 $\pm$ 0.53 & Null \\
R\_ratio\_3d & Phot. OCS (a) & 3 & 0.00 $\pm$ 0.00 & 80.36 $\pm$ 31.18 & 10.45 $\pm$ 8.38 & 2.62 $\pm$ 1.11 & Null \\
I\_interpart\_1d & Phot. OCS (a) & 1 & 0.00 $\pm$ 0.00 & 107.78 $\pm$ 17.56 & 2.75 $\pm$ 2.73 & 2.69 $\pm$ 1.33 & Null \\
N\_density\_3d & Phot. OCS (b) & 3 & 0.00 $\pm$ 0.00 & 120.26 $\pm$ 9.32 & 3.96 $\pm$ 2.73 & 3.41 $\pm$ 1.55 & Null \\
L\_logratio\_3d & Phot. OCS (a) & 3 & 0.00 $\pm$ 0.00 & 83.17 $\pm$ 31.41 & 7.70 $\pm$ 7.92 & 3.18 $\pm$ 0.39 & Null \\
M1\_ratio\_log\_5d & Phot. OCS (a) & 5 & 0.00 $\pm$ 0.00 & 83.05 $\pm$ 30.56 & 7.83 $\pm$ 7.10 & 3.07 $\pm$ 0.41 & Null \\
M3\_density\_ratio\_5d & Phot. OCS (b) & 5 & 0.00 $\pm$ 0.00 & 97.47 $\pm$ 24.30 & 10.51 $\pm$ 6.74 & 3.15 $\pm$ 1.21 & Null \\
M4\_log\_density\_ratio\_9d & Phot. OCS (b) & 9 & 0.00 $\pm$ 0.00 & 115.74 $\pm$ 28.17 & 12.05 $\pm$ 4.61 & 4.37 $\pm$ 1.22 & Null \\
P\_pixelfrac\_3d & Vis. control & 3 & 0.00 $\pm$ 0.00 & 98.15 $\pm$ 42.20 & 14.79 $\pm$ 7.33 & 2.66 $\pm$ 0.69 & Null \\
M5\_pixelfrac\_only\_4d & Vis. control & 4 & 0.00 $\pm$ 0.00 & 95.75 $\pm$ 41.24 & 15.57 $\pm$ 6.76 & 2.59 $\pm$ 0.44 & Null \\
M2\_ratio\_pixelfrac\_5d & Mixed & 5 & 0.00 $\pm$ 0.00 & 98.25 $\pm$ 40.23 & 14.74 $\pm$ 7.52 & 3.23 $\pm$ 1.00 & Null \\
M6\_all\_nongeo\_13d & Mixed & 13 & 0.00 $\pm$ 0.00 & 107.18 $\pm$ 32.16 & 14.60 $\pm$ 4.47 & 3.30 $\pm$ 1.33 & Null \\
\hline
\multicolumn{8}{l}{\textit{Fixed Protocol:} MLP 3-layer, hidden\_dim=128, max\_epochs=30, batch\_size=32, Adam (lr=1e-3), seed=42, no hyperparameter search} \\
\multicolumn{8}{l}{\textit{Metrics:} Yaw Acc = exact-bin yaw accuracy (72-bin grid, 5° resolution); Yaw CMAE = circular mean absolute error (degrees);} \\
\multicolumn{8}{l}{Within-3 = prediction within $\pm$3 bins (circular distance, including exact bin); Pitch Acc = exact-bin pitch accuracy (secondary diagnostic).} \\
\multicolumn{8}{l}{All values are mean $\pm$ std across 5 folds.} \\
\hline
\end{tabular}
\end{table}
```

**LaTeX 注释**：
- 使用 `\scriptsize` 以适应 13 行 + 8 列表格
- 缩写：Phot. OCS = Photometric OCS, Vis. = Visibility
- Sub-type (a)/(b) 直接嵌入 Claim Class 列
- Protocol 和 Metrics 说明放在表格底部作为多列脚注

### 3.2 Markdown 稳定版本

```markdown
**Table 2. C2 OCS-only screening results under fixed-protocol circular yaw-block holdout.**

| Config Name | Claim Class | Dim | Yaw Acc (%) | Yaw CMAE (°) | Within-3 (%) | Pitch Acc (%) | C2 Verdict |
|:-----------|:-----------|:---:|:-----------:|:------------:|:------------:|:-------------:|:----------:|
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

**C2 Verdict:** All 13 configurations = **Null Result** (no exact-bin yaw generalization achieved under fixed-protocol circular yaw-block holdout).

**Within-3 interpretation:** The chance-level baseline for within-3 (circular distance ≤3 bins including exact bin) is 7/72 = 9.72%. Within-3 rates range from 2.75% to 15.57%, indicating local neighborhood clustering in some configs, but no exact-bin hits.
```

### 3.3 数据源

```text
来源：v0.4_results/05_c2_screening/c2_screening_summary.json
字段（per config）：
  - mean_test_yaw_acc, std_test_yaw_acc
  - mean_test_yaw_circular_mae_deg, std_test_yaw_circular_mae_deg
  - mean_test_yaw_within_3_bins_rate × 100, std_test_yaw_within_3_bins_rate × 100
  - mean_test_pitch_acc × 100, std_test_pitch_acc × 100
```

### 3.4 待人工检查项

- [ ] LaTeX 表格宽度是否需要 `\resizebox` 或横向排版
- [ ] 数值精度：当前保留 2 位小数，yaw_acc 保留到 0.00
- [ ] Within-3 chance-level 9.72% 是否需要在表格中用星号或脚注标记
- [ ] Sub-type (a)/(b) 标注是否清晰，是否需要额外说明

---

## 4. Table 3: C2 Results Grouped by Claim Class

### 4.1 LaTeX 版本

```latex
\begin{table}[h!]
\centering
\caption{C2 results summary by claim class. No claim class achieved exact-bin yaw generalization. Visibility control and mixed OCS+visibility groups show higher within-3 rates (14.6\%--15.6\%) than pure photometric OCS groups (2.8\%--12.1\%), suggesting some coarse geometric localization from pixel-count features, but this did not translate to exact-bin yaw accuracy. Photometric OCS sub-types: (a) = pure photometric (no pixel-count dependency); (b) = photometric normalized by visibility (contains density features).}
\label{tab:c2_by_class}
\small
\begin{tabular}{lcccccc}
\hline
\textbf{Claim Class} & \textbf{N} & \textbf{Dim} & \textbf{Yaw Acc} & \textbf{Yaw CMAE} & \textbf{Within-3} & \textbf{Pitch Acc} \\
 & \textbf{Configs} & \textbf{Range} & \textbf{(all)} & \textbf{Range (°)} & \textbf{Range (\%)} & \textbf{Range (\%)} \\
\hline
Phot. OCS (a) & 6 & 1--5 & 0.00\% & 80.36--107.78 & 2.75--10.45 & 2.56--3.18 \\
Phot. OCS (b) & 3 & 3--9 & 0.00\% & 97.47--120.26 & 3.96--12.05 & 3.15--4.37 \\
Vis. control & 2 & 3--4 & 0.00\% & 95.75--98.15 & 14.79--15.57 & 2.59--2.66 \\
Mixed & 2 & 5--13 & 0.00\% & 98.25--107.18 & 14.60--14.74 & 3.23--3.30 \\
\hline
\textbf{Overall} & \textbf{13} & \textbf{1--13} & \textbf{0.00\%} & \textbf{80.36--120.26} & \textbf{2.75--15.57} & \textbf{2.56--4.37} \\
\hline
\multicolumn{7}{l}{\textit{All C2 verdicts = Null}} \\
\hline
\end{tabular}
\end{table}
```

**LaTeX 注释**：
- 使用 `\small` 字号，5 行数据 + 1 行总计
- 缩写：Phot. OCS = Photometric OCS, Vis. = Visibility
- Range 列使用 `--` 连接最小值和最大值

### 4.2 Markdown 稳定版本

```markdown
**Table 3. C2 results summary by claim class.**

| Claim Class | N Configs | Dim Range | Yaw Acc (all) | Yaw CMAE Range (°) | Within-3 Range (%) | Pitch Acc Range (%) |
|:-----------|:---------:|:---------:|:-------------:|:------------------:|:------------------:|:-------------------:|
| Photometric OCS (a) | 6 | 1-5 | 0.00% | 80.36 - 107.78 | 2.75 - 10.45 | 2.56 - 3.18 |
| Photometric OCS (b) | 3 | 3-9 | 0.00% | 97.47 - 120.26 | 3.96 - 12.05 | 3.15 - 4.37 |
| Visibility control | 2 | 3-4 | 0.00% | 95.75 - 98.15 | 14.79 - 15.57 | 2.59 - 2.66 |
| Mixed OCS+visibility | 2 | 5-13 | 0.00% | 98.25 - 107.18 | 14.60 - 14.74 | 3.23 - 3.30 |
| **Overall** | **13** | **1-13** | **0.00%** | **80.36 - 120.26** | **2.75 - 15.57** | **2.56 - 4.37** |

**C2 Verdict:** All claim classes = **Null**

**Sub-type notation:**
- **(a)**: Direct OCS photometric or ratios/logs without pixel-count dependency
- **(b)**: OCS photometric values normalized by visibility pixel counts (contains density features)

**Key observation:** No claim class achieved exact-bin yaw generalization. Visibility control and mixed groups show higher within-3 rates (14.6%-15.6%) than pure photometric OCS groups (2.8%-12.1%), suggesting some coarse geometric localization from pixel-count features, but this did not translate to exact-bin yaw accuracy. Even high-dimensional mixed configs (M6_all_nongeo_13d, 13D) did not achieve yaw generalization, ruling out simple dimensionality-driven success within this feature space and protocol.
```

### 4.3 数据源

```text
来源：对 c2_screening_summary.json 的 13 个 configs 按 claim class 分组后统计
分组规则：
  - Photometric OCS (a): config_id 1, 2, 3, 4, 6, 7
  - Photometric OCS (b): config_id 5, 8, 9
  - Visibility control: config_id 10, 11
  - Mixed OCS+visibility: config_id 12, 13

Range 计算：取各组内 mean 值的 min/max
```

### 4.4 待人工检查项

- [ ] Sub-type (a)/(b) 说明是否需要在正文中预先定义
- [ ] Range 值是否需要保留更多小数位
- [ ] 是否需要额外列出各组的平均值（而不只是 range）

---

（待续 Part 2：Figure 规格与绘图脚本）

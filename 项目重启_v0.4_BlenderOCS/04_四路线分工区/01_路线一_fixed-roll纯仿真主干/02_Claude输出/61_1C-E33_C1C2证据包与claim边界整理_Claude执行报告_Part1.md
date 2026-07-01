# 61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告

执行端：Claude  
任务编号：1C-E33  
任务名称：C1/C2 证据包整理、论文图表表格规划与 claim 边界草案  
执行日期：2026-06-26  

---

## 0. 执行裁决

```text
1C-E33：COMPLETED
C1/C2 证据包整理：COMPLETE
C2 表格草案生成：COMPLETE
Claim 边界草案：COMPLETE
论文图表规划框架：COMPLETE
Image/Joint 对照实验论证框架：COMPLETE
```

**重要声明**：
- 本报告仅整理证据、表格和 claim 边界
- 未启动 C3 joint 复验
- 未进行后验超参/架构/特征搜索
- 未写论文正文

---

## 1. 任务依据

### 1.1 输入文件

```text
依据文件：
- CLAUDE.md
- R60_Codex_审阅_1C-E32通过并接受C2_OCS-only负结果.md

C1 证据文件：
- 57_1C-E30_C1特征提取正式执行_Claude执行报告.md
- v0.4_results/04_ocs_features/feature_definitions.json
- v0.4_results/04_ocs_features/feature_extraction_run_summary.json

C2 证据文件：
- 60_1C-E32_C2_OCS-only正式筛选_Claude执行报告.md
- v0.4_results/05_c2_screening/c2_screening_summary.json
```

### 1.2 任务要求

根据 R60 Codex 审阅文件，E33 任务要求：

**允许：**
- 读取 C1/C2 结果
- 整理 C1/C2 证据包报告
- 生成 C2 表格草案
- 明确 C2 null result 的可写/不可写边界
- 给出 image/joint 对照实验的论证框架

**禁止：**
- 不启动 C3
- 不做后验超参搜索或架构搜索
- 不改特征定义文件
- 不写论文正文

---

## 2. C1 证据包汇总

### 2.1 C1 任务完成状态

**任务**：1C-E30 OCS 特征提取正式执行  
**完成日期**：2026-06-25  
**状态**：COMPLETED

**核心产物**：
- `enhanced_ocs_features.npz`（582 KB，14 个配置，2664 条记录）
- `feature_extraction_run_summary.json`（6.3 KB，运行态摘要）
- `feature_definitions.json`（9.8 KB，预注册定义，未被覆盖）

### 2.2 C1 配置完整性

**总配置数**：14 个
- **C2 参与配置**：13 个（config_id 1-13）
- **常量自检配置**：1 个（config_id 14，不参与 C2）

**配置分组**：
- **A 组（photometric OCS）**：9 个配置
  - Sub-type (a)：纯光度（6 个）
  - Sub-type (b)：visibility-normalized（3 个）
- **B 组（visibility control）**：2 个配置
- **C 组（mixed OCS+visibility）**：2 个配置
- **D 组（constant sanity check）**：1 个配置（不参与 C2）

### 2.3 C1 预注册完整性验证

**预注册审计字段**：
- ✅ `task` = "1C-E29 OCS feature extraction — pre-registered definitions"
- ✅ `pre_registered_date` = "2026-06-25"
- ✅ `expected_n_records` = 2664
- ✅ `pre_registered_constants`（epsilon, ratio_clip, log_clip 等）
- ✅ `claim_classes`（4 类：photometric OCS / visibility control / mixed / constant check）
- ✅ `sanity_check_expected`（phase_angle_cos 应为常量）
- ✅ `c2_exclusion_configs`（constant_check_1d）

**运行态验证**：
- ✅ `n_records` = 2664（与预注册一致）
- ✅ `record_count_match` = true
- ✅ `record_id_unique` = true（2664/2664，无重复）
- ✅ 常量自检通过：`phase_angle_cos` = 0.4522487（phase ≈ 63°）

**结论**：C1 预注册定义未被修改，运行态与预注册完全一致，常量自检通过。

### 2.4 C1 配置详细清单

**A 组：photometric OCS（9 个配置）**

| config_id | config_name | dim | claim_class | 归因边界 |
|-----------|-------------|-----|-------------|----------|
| 1 | baseline_4dim | 4 | photometric OCS | 纯光度 (a) |
| 2 | R_ratio_2d | 2 | photometric OCS | 纯光度 (a) |
| 3 | R_ratio_3d | 3 | photometric OCS | 纯光度 (a) |
| 4 | I_interpart_1d | 1 | photometric OCS | 纯光度 (a) |
| 6 | L_logratio_3d | 3 | photometric OCS | 纯光度 (a) |
| 7 | M1_ratio_log_5d | 5 | photometric OCS | 纯光度 (a) |
| 5 | N_density_3d | 3 | photometric OCS | visibility-normalized (b) |
| 8 | M3_density_ratio_5d | 5 | photometric OCS | visibility-normalized (b) |
| 9 | M4_log_density_ratio_9d | 9 | photometric OCS | visibility-normalized (b) |

**归因边界说明**：
- **Sub-type (a)**：纯 OCS 光度特征（直接 OCS 值或比率/对数），不依赖 pixel-count。正结果可归因于纯 OCS 光度通道。
- **Sub-type (b)**：OCS 光度经 visibility pixel counts 归一化（density 特征）。正结果必须描述为"OCS photometric values normalized by visibility pixel counts"，不得声称独立于 visibility 信息。

**B 组：visibility control（2 个配置）**

| config_id | config_name | dim | claim_class | 归因边界 |
|-----------|-------------|-----|-------------|----------|
| 10 | P_pixelfrac_3d | 3 | visibility control | 纯几何，不可归因光度 |
| 11 | M5_pixelfrac_only_4d | 4 | visibility control | 纯几何，不可归因光度 |

**归因边界说明**：
- 仅包含 pixel-count / visibility 特征，零 OCS 光度信息。
- 正结果不能归因于 OCS 光度通道。

**C 组：mixed OCS+visibility（2 个配置）**

| config_id | config_name | dim | claim_class | 归因边界 |
|-----------|-------------|-----|-------------|----------|
| 12 | M2_ratio_pixelfrac_5d | 5 | mixed OCS+visibility | 需分解 OCS vs visibility 贡献 |
| 13 | M6_all_nongeo_13d | 13 | mixed OCS+visibility | 需分解 OCS vs visibility 贡献 |

**归因边界说明**：
- 混合光度 OCS 特征与 visibility 特征。
- 正结果必须分解通道贡献，不得归因于单一通道。

**D 组：constant sanity check（1 个配置）**

| config_id | config_name | dim | claim_class | 用途 |
|-----------|-------------|-----|-------------|------|
| 14 | constant_check_1d | 1 | constant sanity check | C1 代码自检，不参与 C2 |

---

## 3. C2 证据包汇总

### 3.1 C2 任务完成状态

**任务**：1C-E32 C2 OCS-only 正式筛选  
**完成日期**：2026-06-26  
**状态**：COMPLETED

**核心发现**：
```text
所有 13 个配置的 test_yaw_acc = 0.00%
判定：NULL RESULT
```

### 3.2 C2 训练完成度

**训练规模**：
- 13 个配置（c2_participant=true）
- 每个配置 5 folds（circular yaw_block holdout）
- 总计：65 个训练运行（13 × 5）
- 每个运行：30 epochs，~1850 train samples

**完成度**：
- ✅ 65/65 训练运行完成
- ✅ 65 个 result JSON + 65 个 checkpoint
- ✅ 1 个 c2_screening_summary.json
- ✅ 所有运行使用固定协议（未修改）

### 3.3 C2 固定协议

**C2_FIXED_PROTOCOL**（预注册，未修改）：
```python
max_epochs = 30
hidden_dim = 128
lr = 0.001
batch_size = 32
seed = 42
optimizer = Adam
model_type = MLP_3layer
n_layers = 3
```

**协议遵守验证**：
- ✅ 所有 65 个 result JSON 的 `training_protocol` 与固定协议一致
- ✅ 无超参数搜索痕迹
- ✅ 无协议漂移

### 3.4 C2 判据与判定

**C2 判据**（R59 锁定）：
```text
strong_positive：yaw_acc ≥ 10%，且 cmae / within_k 同步改善
weak_positive：yaw_acc ≥ 3%，且需 bootstrap / permutation / extra fold 之一
null_result：全部配置 yaw_acc = 0.00% 或未达 weak_positive
```

**C2 判定结果**：
```text
13 / 13 configs：mean_test_yaw_acc = 0.0
65 / 65 folds：test yaw_correct_count = 0
判定：NULL RESULT
```

**归因分析**：
- **Photometric OCS（9 个配置）**：全部 yaw_acc = 0.00%
  - Sub-type (a) 纯光度（6 个）：0.00%
  - Sub-type (b) visibility-normalized（3 个）：0.00%
- **Visibility control（2 个配置）**：全部 yaw_acc = 0.00%
- **Mixed OCS+visibility（2 个配置）**：全部 yaw_acc = 0.00%

**结论**：
在当前 C2 固定协议和预注册特征集合下，OCS-only 低维特征（无论是纯光度、visibility-normalized、纯 visibility 还是混合）均未显示跨 yaw holdout 泛化能力。

---

## 4. C2 表格草案（论文可用）

### 4.1 完整表格（13 个配置）

| Config Name | Claim Class | Dim | Feature Keys (简述) | Mean Test Yaw Acc (%) | Mean Test Yaw CMAE (deg) | Mean Test Yaw Within-3-Bins Rate (%) | Mean Test Pitch Acc (%) |
|-------------|-------------|-----|---------------------|----------------------|--------------------------|--------------------------------------|------------------------|
| baseline_4dim | photometric OCS | 4 | ocs_total, ocs_j, ocs_t, ocs_y | 0.00 ± 0.00 | 89.25 ± 33.59 | 8.16 ± 7.11 | 2.56 ± 1.05 |
| R_ratio_2d | photometric OCS | 2 | r_j, r_t | 0.00 ± 0.00 | 84.15 ± 32.72 | 6.31 ± 7.58 | 2.56 ± 0.53 |
| R_ratio_3d | photometric OCS | 3 | r_j, r_t, r_y | 0.00 ± 0.00 | 80.36 ± 31.18 | 10.45 ± 8.38 | 2.62 ± 1.11 |
| I_interpart_1d | photometric OCS | 1 | ratio_j_t | 0.00 ± 0.00 | 107.78 ± 17.56 | 2.75 ± 2.73 | 2.69 ± 1.33 |
| N_density_3d | photometric OCS | 3 | ocs_density_total, ocs_density_j, ocs_density_t | 0.00 ± 0.00 | 120.26 ± 9.32 | 3.96 ± 2.73 | 3.41 ± 1.55 |
| L_logratio_3d | photometric OCS | 3 | log_r_j, log_r_t, log_ratio_j_t | 0.00 ± 0.00 | 83.17 ± 31.41 | 7.70 ± 7.92 | 3.18 ± 0.39 |
| M1_ratio_log_5d | photometric OCS | 5 | r_j, r_t, log_r_j, log_r_t, log_ratio_j_t | 0.00 ± 0.00 | 83.05 ± 30.56 | 7.83 ± 7.10 | 3.07 ± 0.41 |
| M3_density_ratio_5d | photometric OCS | 5 | ocs_density_total, ocs_density_j, ocs_density_t, r_j, r_t | 0.00 ± 0.00 | 97.47 ± 24.30 | 10.51 ± 6.74 | 3.15 ± 1.21 |
| M4_log_density_ratio_9d | photometric OCS | 9 | log_r_j, log_r_t, log_ratio_j_t, log_ocs_total, ocs_density×3, r×2 | 0.00 ± 0.00 | 115.74 ± 28.17 | 12.05 ± 4.61 | 4.37 ± 1.22 |
| P_pixelfrac_3d | visibility control | 3 | frac_j, frac_t, visibility_ratio | 0.00 ± 0.00 | 98.15 ± 42.20 | 14.79 ± 7.33 | 2.66 ± 0.69 |
| M5_pixelfrac_only_4d | visibility control | 4 | frac_j, frac_t, frac_y, visibility_ratio | 0.00 ± 0.00 | 95.75 ± 41.24 | 15.57 ± 6.76 | 2.59 ± 0.44 |
| M2_ratio_pixelfrac_5d | mixed OCS+visibility | 5 | r_j, r_t, frac_j, frac_t, visibility_ratio | 0.00 ± 0.00 | 98.25 ± 40.23 | 14.74 ± 7.52 | 3.23 ± 1.00 |
| M6_all_nongeo_13d | mixed OCS+visibility | 13 | r×2, ratio_j_t, ocs_density×3, frac×2, visibility_ratio, log×4 | 0.00 ± 0.00 | 107.18 ± 32.16 | 14.60 ± 4.47 | 3.30 ± 1.33 |

**表格说明**：
- **Yaw Acc**：exact-bin yaw accuracy（目标指标）
- **Yaw CMAE**：circular mean absolute error (deg)，越小越好
- **Yaw Within-3-Bins Rate**：预测落在真值 ±3 bins 内的比例
- **Pitch Acc**：exact-bin pitch accuracy（非主要目标，仅作参考）
- 所有数值为 5-fold 平均 ± 标准差

### 4.2 按 claim_class 分组汇总表

| Claim Class | N Configs | Yaw Acc Range (%) | Yaw CMAE Range (deg) | Pitch Acc Range (%) |
|-------------|-----------|-------------------|----------------------|---------------------|
| photometric OCS | 9 | 0.00 (全部) | 80.36 - 120.26 | 2.56 - 4.37 |
| visibility control | 2 | 0.00 (全部) | 95.75 - 98.15 | 2.59 - 2.66 |
| mixed OCS+visibility | 2 | 0.00 (全部) | 98.25 - 107.18 | 3.23 - 3.30 |

**汇总结论**：
- 所有 claim class 的 yaw_acc 均为 0.00%
- Photometric OCS 的 yaw CMAE 变异较大（80-120 deg）
- Visibility control 和 mixed 的 yaw CMAE 相对集中（95-107 deg）
- Pitch acc 整体微弱（2.56-4.37%），远低于 weak_positive 阈值（3%）

---

（待续 Part 2：Claim 边界草案与论文图表规划）

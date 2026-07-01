# R60 Codex 审阅：1C-E32 通过并接受 C2 OCS-only 负结果

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  60_1C-E32_C2_OCS-only正式筛选_Claude执行报告.md

v0.4_results/05_c2_screening/
  c2_screening_summary.json
  <13 configs>/<config>_fold<0-4>_result.json
  <13 configs>/<config>_fold<0-4>_checkpoint.pt
```

---

## 0. 裁决

```text
1C-E32：PASS
C2 OCS-only 正式筛选：COMPLETE
C2 判定：NULL RESULT，接受为固定协议下的有效负结果
C3 joint 复验：NOT RELEASED
后验 OCS-only 架构搜索 / 特征工程补救：NOT RELEASED
论文正文正式改写：NOT RELEASED
下一步：RELEASE E33，整理 C1/C2 证据包、图表表格与论文 claim 边界
```

E32 已按 R59 放行范围完成 13 个 `c2_participant=true` 配置 × 5 folds，共 65 个正式训练运行。Codex 复核结果支持 Claude 的核心结论：在当前 `phase63 fixed-roll` 数据、5-fold `circular yaw_block` holdout、C2 固定 MLP 协议和预注册特征集合下，OCS-only 特征没有达到 weak positive，更没有达到 strong positive；所有配置的 test yaw exact-bin accuracy 均为 0。

该负结果可以进入路线一 C 的证据链，但解释边界必须收窄为：

```text
在当前固定协议和当前 C2 特征集合下，OCS-only 低维特征未表现出可用于跨 yaw holdout 泛化的姿态反演能力。
```

不得外推为：

```text
OCS 光度在所有模型、所有特征、所有架构和所有观测几何下都不含姿态信息。
```

---

## 1. 上下文恢复

本轮已按 `CLAUDE.md` 完成轻量上下文恢复，并读取：

```text
CLAUDE.md
03_项目说明与规划材料/00_本区总览_项目说明与规划材料导航.md
04_四路线分工区/00_四路线分工区总览.md
04_四路线分工区/00_总览与裁决/00_路线总览.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/00_路线总览.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R59_Codex_审阅_1C-E31-FIX01通过并放行E32_C2正式筛选.md
```

本轮红线：

- 只审阅 `1C-E32`，不自动启动 C3。
- 不根据 E32 负结果后验改协议、删配置或换架构补救。
- 不把 OCS-only 负结果写成真实未知目标姿态反演的终局判断。
- 不放行 B1/GGX、三轴小项目、路线二/三/四扩展。
- 不直接写论文正文。

---

## 2. Codex 机器复核

Codex 使用 `ocs_sim` 环境对 `v0.4_results/05_c2_screening/` 进行结构化复核。

### 2.1 输出完整性

```text
c2_screening_summary.json：存在，约 49 KB
results_summary：13 configs
result JSON：65
checkpoint：65
每个 config：5 result JSON + 5 checkpoint
n_configs / n_folds：13 / 5
```

13 个配置为：

```text
baseline_4dim
R_ratio_2d
R_ratio_3d
I_interpart_1d
N_density_3d
L_logratio_3d
M1_ratio_log_5d
M3_density_ratio_5d
M4_log_density_ratio_9d
P_pixelfrac_3d
M5_pixelfrac_only_4d
M2_ratio_pixelfrac_5d
M6_all_nongeo_13d
```

### 2.2 协议一致性

所有 65 个 result JSON 的 `training_protocol` 均与固定协议一致：

```text
max_epochs = 30
hidden_dim = 128
lr = 0.001
batch_size = 32
seed = 42
optimizer = Adam
model_type = MLP_3layer
n_layers = 3
```

未发现超参数搜索或协议漂移痕迹。

### 2.3 字段完整性

所有 65 个 result JSON 均包含：

```text
claim_class
feature_keys
feature_dim
training_protocol
final_metrics.val / final_metrics.test
yaw_acc / pitch_acc
yaw_circular_mae_deg / pitch_mae_deg
yaw_correct_count / pitch_correct_count
yaw_within_1/3/5_bin_count + rate
pitch_within_1/3/5_bin_count + rate
loss
n_samples
```

未发现缺失字段。

### 2.4 Summary 聚合一致性

Codex 重新从 per-fold result JSON 计算：

```text
mean_test_yaw_acc
mean_test_yaw_circular_mae_deg
mean_test_yaw_within_1/3/5_bin_rate
mean_test_yaw_correct_count
```

与 `c2_screening_summary.json` 中 aggregate metrics 完全一致：

```text
aggregate_mismatch_count = 0
```

### 2.5 小问题

`c2_screening_summary.json` 当前为 GBK 编码，而 65 个 per-fold result JSON 为 UTF-8。该问题不影响本轮数值读取和判定，但建议后续若要做跨平台共享、论文制表或自动化汇总，优先转换为 UTF-8 或在脚本中显式指定输出编码。

该项为 Minor，不阻塞 E32 通过。

---

## 3. 结果判读

### 3.1 核心数值

Codex 直接复核全部 65 个 test fold：

```text
test yaw_acc unique values：0.0
test yaw_correct_count unique values：0
test pitch_acc range：0.0036 - 0.0631
test pitch_acc mean：0.0303
test yaw circular MAE range：37.5 - 158.7 deg
test yaw circular MAE mean：96.97 deg
test yaw within_3_bin_rate range：0.0 - 0.2143
test yaw within_3_bin_rate mean：0.0996
```

配置级均值中，所有 `mean_test_yaw_acc = 0.0` 且 `std_test_yaw_acc = 0.0`。

### 3.2 判据应用

R59 锁定的 C2 判据为：

```text
strong_positive：yaw_acc >= 10%，且 cmae / within_k 同步改善
weak_positive：yaw_acc >= 3%，且需要 bootstrap / permutation / extra fold 之一
null_result：全部配置 yaw_acc = 0.00% 或未达到 weak_positive
```

E32 结果：

```text
13 / 13 configs：mean_test_yaw_acc = 0.0
65 / 65 folds：test yaw_correct_count = 0
```

因此 C2 判定为：

```text
NULL RESULT
```

### 3.3 归因边界

可以归因：

- `photometric OCS` 配置在当前 C2 协议下未显示跨 yaw holdout 泛化能力。
- `visibility control` 配置在当前 C2 协议下也未显示跨 yaw holdout 泛化能力。
- `mixed OCS+visibility` 配置没有把 weak localization 转化为 exact-bin yaw accuracy。
- 低维 OCS-only 特征在严格 `circular yaw_block` 下不足以支撑当前形式的姿态反演头。

不能归因：

- 不能说 OCS 光度通道物理上完全无姿态信息。
- 不能说所有 OCS 特征工程、所有架构、所有观测几何均必然失败。
- 不能据此证明 image-only 或 joint 通道失败。
- 不能把该结果写成真实未知目标在轨姿态反演结论。

---

## 4. 科学审阅意见

E32 的科学价值在于它是一个受控、完整、预注册口径下的负结果。它对路线一 C 很有用，因为它给出了清晰的边界：

```text
OCS-only 低维光度/可见性特征不足以单独承担跨 yaw block 的姿态分类；
如果 image 或 joint 后续表现更好，互补性论证应建立在“OCS-alone weak / image or joint stronger”的对照上；
如果 joint 未来也不显著，则路线一 C 应转向“受控同源仿真下的可观测性边界与失败模式”。
```

当前不建议立刻做后验的 OCS-only CNN、Transformer、深 MLP 或新增特征搜索。原因是：

- E32 原本是固定协议筛选，不是开放优化赛道。
- 在全部 13 个配置均为 exact yaw zero 的情况下，后验架构搜索更像补救性探索，论文中需要单独标为 exploratory。
- 当前路线更需要把 C1/C2 已完成证据链收束成清晰的 claim 边界，而不是继续扩大 OCS-only 搜索空间。

若作者未来仍希望探索其他 OCS-only 架构，应另立任务，明确写成 exploratory / ablation，不得回填到 C2 预注册筛选结论。

---

## 5. 阶段门判断

```text
E32 执行完整性：PASS
E32 指标完整性：PASS
E32 协议遵守：PASS
C2 判据应用：PASS
C2 结论：NULL RESULT ACCEPTED
C3 触发条件：NOT MET
```

C3 不放行，理由：

- R59 要求 C3 触发需另经 Codex 审阅。
- 当前 C2 未达到 weak_positive。
- 所有配置 exact yaw accuracy 均为 0，没有足够理由把 joint 复验作为 C2 正向结果的延伸。

后续如果要做 C3，必须先给出新的任务理由，例如：

```text
不是因为 C2 触发 C3，
而是作为路线一 C 论文中 OCS-only negative 与 image/joint complementarity 的独立对照实验。
```

该理由需另行 Codex 审阅和放行。

---

## 6. 放行下一步

放行：

```text
1C-E33：C1/C2 证据包整理、论文图表表格规划与 claim 边界草案
```

E33 目标：

1. 汇总 C1 特征诊断与 C2 OCS-only 筛选结果。
2. 形成论文可用的表格草案：config、claim_class、feature_dim、mean yaw_acc、yaw CMAE、within_3、pitch_acc。
3. 形成结果解释边界：哪些可以写，哪些必须避免。
4. 给出是否需要独立 image/joint 对照实验的论证框架，但不得启动训练。

仍不放行：

```text
C3 joint 训练
B1/GGX
三轴小项目
路线二/三/四扩展
论文正文正式改写
```

---

## 7. 给 Claude 的 E33 短提示词

```text
执行 1C-E33：C1/C2 证据包整理、论文图表表格规划与 claim 边界草案。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R60_Codex_审阅_1C-E32通过并接受C2_OCS-only负结果.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/57_1C-E30_C1特征提取正式执行_Claude执行报告.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/60_1C-E32_C2_OCS-only正式筛选_Claude执行报告.md
- v0.4_results/04_ocs_features/feature_definitions.json
- v0.4_results/05_c2_screening/c2_screening_summary.json

任务：
1. 不运行训练，不改代码，不启动 C3。
2. 读取 C1/C2 结果，整理一个 C1/C2 证据包报告。
3. 生成 C2 表格草案：config_name、claim_class、feature_dim、feature_keys 简述、mean_test_yaw_acc、mean_test_yaw_circular_mae_deg、mean_test_yaw_within_3_bin_rate、mean_test_pitch_acc。
4. 明确写出 C2 null result 的论文可写边界：
   - 可写：当前固定协议下 OCS-only 低维特征未达到跨 yaw holdout 泛化。
   - 不可写：OCS 光度在所有条件下完全无姿态信息。
5. 给出是否需要后续 image/joint 对照实验的“论证框架”，但不得放行或执行任何训练。
6. 输出报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告.md

红线：
- 不启动 C3。
- 不做后验超参搜索或架构搜索。
- 不改 feature_definitions.json / enhanced_ocs_features.npz / split manifests。
- 不写论文正文，只整理证据、表格和 claim 边界。
- 若输出过长，按 Part 1/2/3 分段写入，直到文件完整。
```

---

## 8. 结论

E32 可以通过。C2 OCS-only 负结果可信、完整、可用于论文证据链，但必须以固定协议和当前特征集合为边界进行表述。当前最稳妥的路线不是继续追打 OCS-only，而是先把 C1/C2 收束为可审阅的证据包和 claim 边界；C3 若未来启动，应作为独立对照实验重新放行，而不是由 C2 自动触发。

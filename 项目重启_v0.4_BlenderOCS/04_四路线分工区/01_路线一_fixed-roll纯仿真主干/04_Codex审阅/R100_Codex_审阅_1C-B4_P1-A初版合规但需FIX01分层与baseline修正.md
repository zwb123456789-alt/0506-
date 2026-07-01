# R100 Codex 审阅：1C-B4/P1-A 初版合规但需 FIX01 分层与 baseline 修正

最后更新：2026-06-29
审阅端：Codex
对象：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
97_1C-B4_P1-A只读指标重算与阶段门判断_Claude执行报告.md
```

依据：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R99_Codex_裁决_1C-B3闭口后放行P1-A只读指标重算.md
```

## 0. 裁决

```text
97 可接收为 P1-A 第一阶段只读指标重算初版。
但 P1-A 第一阶段尚未闭口，需执行 FIX01。
```

本轮未发现 Claude 训练、新渲染、修改 split、修改模型/loss/head/超参/seed、写入成果区、改论文正文、启动 P1-B/P2 或触发头A/头B大合并裁决。97 的主要结论方向基本稳：C3 在 circular/within-k/coarse45 上仅有弱于随机基线的边际改善，image_only 与 joint 基本无差异，不支持进入训练侧 P1-A 第二阶段。

但 R99 明确要求回答 fold/channel/pitch/yaw-block 分层和 baseline 口径，97 对 pitch/yaw-block 直接列为缺口；其中 pitch 信息已经存在于 `samples.npz` 的 `pitch_true_bin` 或可由 `record_id` 解析，yaw-block 也应优先尝试读取既有 split manifest。因此当前不能判定 P1-A 第一阶段完全闭口。

## 1. 合规检查

| 项目 | 检查结果 | 说明 |
|---|---|---|
| 输出位置 | 通过 | 报告位于路线一 `02_Claude输出/` |
| 产物位置 | 通过 | 产物位于 `v0.4_results/09_p1a_metric_recompute/` |
| 不训练/不推理 | 通过 | 只读取既有 `samples.npz` argmax predictions |
| 不改模型/split/loss/head | 通过 | 脚本仅计算指标 |
| 不写成果区 | 通过 | 未同步成果区 |
| 不启动 P1-B/P2 | 通过 | 报告明确未启动 |
| R99 最低产物 | 基本通过 | 产物齐全，但文件名有一处与 R99 建议不完全一致 |
| R99 必答问题 | 部分通过 | pitch/yaw-block 分层未完成 |

## 2. 已完成内容

97 已完成以下有效工作：

```text
1. 读取 C2 baseline_4dim、C3 image_only、C3 joint 的既有 samples.npz。
2. 重算 exact-bin、circular MAE、circular median AE、within-1/2/3/6、coarse45/coarse90。
3. 生成 within-k curve、coarse15/30/45/60/90、circular error distribution。
4. 记录 logits/probabilities 缺失，并遵守 R99 要求未加载 checkpoint forward。
5. 明确 P1-A 初版不支持训练侧 continuous/circular head。
```

主要数值方向可接收：

```text
C2 baseline_4dim: circular MAE 约 17.85 bins, within-6 约 16.1%, coarse45 约 11.7%
C3 image_only:    circular MAE 约 16.29 bins, within-6 约 25.6%, coarse45 约 18.0%
C3 joint:         circular MAE 约 16.28 bins, within-6 约 26.5%, coarse45 约 18.2%
```

这些数值支持：

```text
1. exact-bin 0% 仍为严格负结果。
2. C3 相比 C2 有弱的 circular/within-k/coarse45 改善。
3. image_only 与 joint 几乎无差异，early concat 仍无可用互补增益。
4. 当前指标重构只可作为 extrapolation gap 叙事材料，不能写成外推成功。
```

## 3. 需修正问题

### 3.1 R99 要求的 pitch 分层未完成

97 第 51-52 行写“pitch 分层统计当前未完成，需后续扩展”。但抽查 `samples.npz` 可见：

```text
fields = ['record_id', 'yaw_pred_bin', 'yaw_true_bin', 'pitch_pred_bin', 'pitch_true_bin']
```

因此 pitch 分层不应作为不可做缺口。FIX01 至少应按 `pitch_true_bin` 或由 `record_id` 解析出的 pitch degree 分组，重算每个 channel 的：

```text
circular MAE
within-3 / within-6
coarse45
sample count
```

分组可采用轻量口径，例如：

```text
pitch exact bins: 37 个 pitch bin
或 coarse pitch bands: negative / zero-near / positive
或 30°/45° pitch bands
```

### 3.2 yaw-block 分层应先尝试读取 split manifest

97 第 47-50 行称 samples 未包含 yaw block 标签，因此无法分层。R99 允许读取 split manifest；当前项目中存在：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest*.*
```

FIX01 应先只读尝试：

```text
1. 读取每 fold split manifest；
2. 将 samples 的 record_id 或 yaw_true_bin 映射到 fold/test yaw block；
3. 若 manifest schema 不足，再列出具体缺失字段。
```

不能只因为 `samples.npz` 未内嵌 block 标签就直接跳过 R99 的 yaw-block 分层要求。

### 3.3 random circular MAE baseline 应改为理论值或固定 seed

脚本中 `random_baseline_circular_mae()` 使用 Monte Carlo 且未固定 seed，因此 `p1a_random_baseline.json` 中 circular MAE 为 18.0528。对于 72-bin circular distance，理论 random circular MAE 为：

```text
18.0 bins
```

当前 18.0528 与理论值差异很小，不改变结论，但后续材料应使用理论值 18.0，或至少固定 seed 并注明 Monte Carlo sampling error。建议 FIX01 改为理论值，避免每次重跑基线轻微漂移。

### 3.4 weighted / unweighted fold 聚合口径需注明

当前跨 fold 聚合使用 per-fold unweighted mean。由于 fold 样本数为 555/555/518/518/518，加权与非加权差异很小，不改变结论。但报告第 114 行用 “N Samples=2664” 呈现聚合统计，容易让读者误以为所有指标均为 pooled sample-level 加权结果。

FIX01 应明确：

```text
当前主表为 per-fold unweighted mean ± fold std；
可另附 pooled sample-level weighted metrics 作为核对。
```

建议新增：

```text
p1a_channel_pooled_metrics.csv
```

### 3.5 claim 强度需再收窄

97 第 139-140 行写“图像通道携带更多姿态信息”，第 239 行写“确实携带更多姿态信息”。鉴于当前只是 argmax 预测指标且未做 embedding/logit/输入信息量分析，更稳口径应为：

```text
C3 image-based 模型输出在 circular/within-k/coarse45 指标上弱优于 C2 OCS-only；
这提示图像通道在当前模型输出中保留了更多可用姿态线索。
```

不要写成对图像通道信息量的强证明。

## 4. FIX01 放行范围

当前只放行：

```text
1C-B4-FIX01_P1-A分层指标与baseline口径修正
```

允许事项：

```text
1. 读取既有 samples.npz。
2. 读取既有 split manifest。
3. 基于 record_id / yaw_true_bin / pitch_true_bin 做只读分层指标重算。
4. 修正 random circular MAE baseline 为理论值 18.0 或固定 seed Monte Carlo。
5. 新增 pooled weighted metrics，与现有 fold mean metrics 并列。
6. 修改报告口径，不做新训练结论。
```

禁止事项：

```text
不得训练或重训练。
不得新渲染。
不得生成新数据集。
不得修改 split。
不得修改模型结构。
不得修改 loss、output head、超参或 seed。
不得加载 checkpoint forward 导出 logits/probabilities。
不得写入成果区。
不得改论文正文。
不得启动 P1-B 或 P2。
不得触发头A/头B大合并裁决。
```

## 5. FIX01 最低产物要求

Claude 下一轮至少输出：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
98_1C-B4-FIX01_P1-A分层指标与baseline口径修正_Claude执行报告.md
```

以及在：

```text
v0.4_results/09_p1a_metric_recompute/
```

新增或更新：

```text
p1a_channel_pooled_metrics.csv
p1a_pitch_stratified_metrics.csv
p1a_yaw_block_stratified_metrics.csv
p1a_baseline_corrected.md
p1a_stage_gate_matrix_FIX01.md
```

若 yaw-block 分层无法完成，必须写明：

```text
尝试读取的 split manifest 路径；
manifest 实际字段；
无法映射的具体原因；
是否需要单独阶段门。
```

## 6. 当前阶段判断

当前不能裁决：

```text
P1-A 第一阶段完全闭口
停止 P1-A
进入头A/头B大合并裁决
成果区归档
论文正文正式改写
```

当前可以暂定但需 FIX01 后确认：

```text
P1-A 不进入训练侧第二阶段。
P1-A 主要作为论文指标重构材料。
```

换句话说，97 的主方向是对的，但分层与 baseline 口径还差一小步。FIX01 完成后，如数值方向不变，可直接裁决 P1-A 第一阶段闭口，并决定是否停止 P1-A 后进入头A/头B合并裁决。

## 7. 给 Claude 的最短提示词

```text
请严格按 Codex R100 审阅执行：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R100_Codex_审阅_1C-B4_P1-A初版合规但需FIX01分层与baseline修正.md

输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
98_1C-B4-FIX01_P1-A分层指标与baseline口径修正_Claude执行报告.md

只做 P1-A 只读修正：
1. 用 samples.npz 中 pitch_true_bin 或 record_id 解析 pitch，补 pitch 分层 circular/within/coarse 指标；
2. 读取 e25_multifold_yawblock 的 split manifest，尝试补 yaw-block 分层；若失败，列出 manifest 路径、字段和失败原因；
3. random circular MAE baseline 改为理论值 18.0 bins，或固定 seed 并注明；
4. 新增 pooled weighted metrics，明确现有主表是 per-fold unweighted mean；
5. 收窄“图像通道携带更多姿态信息”为“C3 image-based 输出在当前指标上弱优于 C2 OCS-only，提示更多可用姿态线索”。

不得训练、不得新渲染、不得生成新数据集、不得改 split、不得改模型/loss/output head/超参/seed、不得 checkpoint forward、不得写成果区、不得改论文正文、不得启动 P1-B/P2、不得触发头A/头B大合并裁决。
```


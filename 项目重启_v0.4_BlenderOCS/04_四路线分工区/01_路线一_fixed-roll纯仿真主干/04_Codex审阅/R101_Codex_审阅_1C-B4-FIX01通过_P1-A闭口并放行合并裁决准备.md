# R101 Codex 审阅：1C-B4-FIX01 通过，P1-A 闭口并放行合并裁决准备

最后更新：2026-06-29
审阅端：Codex
对象：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
98_1C-B4-FIX01_P1-A分层指标与baseline口径修正_Claude执行报告.md
```

依据：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R100_Codex_审阅_1C-B4_P1-A初版合规但需FIX01分层与baseline修正.md
R99_Codex_裁决_1C-B3闭口后放行P1-A只读指标重算.md
R98_Codex_审阅_1C-B3-FIX02通过_P0只读诊断闭口.md
```

## 0. 裁决

```text
98_1C-B4-FIX01 通过。
P1-A 第一阶段只读指标重算闭口。
不进入 P1-A 第二阶段训练侧改进。
放行下一步：头A/头B合并裁决准备。
```

本裁决不等同于写论文正文、不等同于成果区归档、不等同于放行 P1-B/P2、不等同于模型补救成功，也不触发任何新训练、checkpoint forward、embedding/logits 导出或三轴扩展。

## 1. R100 五项要求核对

| R100 要求 | 检查结果 | 说明 |
|---|---|---|
| Pitch 分层 | 通过 | 已用 `record_id`/`pitch_true_bin` 补齐 pitch band 分层 |
| Yaw-block 分层 | 通过 | 已读取 `split_manifest_circ_yawblock_fold{0-4}.json` 并确认每 fold 连续 test yaw block |
| Baseline 理论值 | 通过 | circular random MAE 已改为理论值 18.0 bins |
| Pooled weighted metrics | 通过 | 已新增 sample-level pooled metrics，并说明与 fold mean 差异很小 |
| Claim 收窄 | 通过 | 已将“图像通道信息量”强 claim 降级为“C3 输出弱优于 C2，提示更多可用姿态线索” |

新增产物已确认位于：

```text
v0.4_results/09_p1a_metric_recompute/
```

关键文件：

```text
p1a_channel_pooled_metrics.csv
p1a_pitch_stratified_metrics.csv
p1a_yaw_block_stratified_metrics.csv
p1a_baseline_corrected.md
p1a_stage_gate_matrix_FIX01.md
p1a_random_baseline_theoretical.json
p1a_fix01_stratify.py
```

## 2. 关键数值复核

### 2.1 Pooled 指标

```text
C2_baseline_4dim: n=2664, exact=0.00%, circular MAE=17.79, within-6=16.0%, coarse45=11.8%
C3_image_only:    n=2664, exact=0.00%, circular MAE=16.33, within-6=25.6%, coarse45=18.1%
C3_joint:         n=2664, exact=0.00%, circular MAE=16.32, within-6=26.5%, coarse45=18.3%
Random baseline:  exact=1.39%, circular MAE=18.0, within-6=18.1%, coarse45=12.5%
```

复核结论：

```text
1. exact-bin 仍为严格负结果。
2. C3 image/joint 相比 C2 有弱的 circular/within/coarse45 改善。
3. C3 joint 相比 C3 image_only 无实质增益。
4. C3 指标仍不足以写成成功外推。
```

### 2.2 Pitch 分层

Pitch 分层可接收：

```text
C2: positive pitch 略优于 negative/near-zero。
C3: pitch 间整体较均匀。
pitch 不是当前误差结构的主导分层因素。
```

### 2.3 Yaw-block 分层

Yaw-block 分层是本轮最重要补充：

```text
C2 fold3 [220,285]: circular MAE=7.50, within-6=42.9%, coarse45=28.6%
C2 fold2 [150,215]: circular MAE=23.58, within-6=0.0%, coarse45=0.0%
C2 fold4 [290,355]: circular MAE=26.59, within-6=8.1%, coarse45=0.0%

C3 image/joint 也存在 block 异质性，但整体比 C2 稳定。
```

该结果支持：

```text
yaw-block 外推失败具有强位置依赖；
外推鸿沟不是均匀的；
不能写 yaw 物理普遍不可观测；
也不能把少数 block 的弱可用信号写成整体可用。
```

## 3. 保留边界

后续使用 P1-A/FIX01 结果时必须保留以下边界：

```text
1. “证明外推失败是协议性、位置依赖”应改写为“支持外推失败具有协议性、位置依赖特征”。
2. “某些弧段 OCS 几乎可用”应改写为“某些弧段出现局部弱可用信号”。
3. C3 优于 C2 只能说明当前模型输出指标弱优，不得写成图像通道信息量的直接证明。
4. early concat 无增益只限定于当前 C3 early concat 设计，不否定所有 fusion 策略。
5. P1-A 是指标重构与诊断材料，不是模型补救成功。
```

以上边界不阻止 P1-A 第一阶段闭口，但必须随材料保留。

## 4. 对 Claude/作者问题的裁决

| 问题 | 裁决 | 说明 |
|---|---|---|
| Q1. P1-A 第一阶段是否闭口 | 是 | FIX01 已补齐分层、baseline、pooled metrics 与 claim 收窄 |
| Q2. 是否停止 P1-A 第二阶段训练侧改进 | 是 | 指标仅弱优于 random，异质性主要来自 yaw-block 位置与输入/协议，不支持改 head/loss 重训 |
| Q3. yaw-block 强异质性是否纳入论文叙事 | 是，但降级措辞 | 可作为 extrapolation gap 的位置依赖证据，不写成“证明”或“局部成功” |
| Q4. 是否进入头A/头B大合并裁决 | 是，放行准备任务 | 当前只放行合并裁决准备，不直接写论文正文 |
| Q5. P1-A 产物是否同步成果区 | 暂不 | 先进入合并裁决准备，成果区同步由合并裁决后决定 |

## 5. 当前阶段状态

当前状态更新为：

```text
头A：R90 已闭口。
头B-B3/P0：R98 已闭口。
头B-B4/P1-A 第一阶段：R101 判定闭口。
P1-A 第二阶段训练侧改进：不放行。
P1-B 非朴素 fusion：不放行。
P2 formal light-curve sequence：不放行。
成果区归档：暂缓。
论文正文正式改写：暂缓。
```

## 6. 下一步放行范围

放行下一步：

```text
1C-B5_头A头B合并裁决准备
```

建议 Claude 输出：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
99_1C-B5_头A头B合并裁决准备_Claude执行报告.md
```

允许事项：

```text
1. 汇总头A R90 后桥接材料的稳定结论。
2. 汇总头B B1/B2/B3/P0/P1-A 的稳定结论。
3. 建立“可进入论文叙事 / 只作诊断材料 / 禁止 claim / 暂缓路线”的四列表。
4. 给出 Figure/SI/Results 材料如何承接的候选，不正式改写论文正文。
5. 给出是否需要成果区同步的建议清单，不自行同步。
```

禁止事项：

```text
不得训练或重训练。
不得新渲染。
不得生成新数据集。
不得修改 split。
不得修改模型/loss/head/超参/seed。
不得 checkpoint forward。
不得启动 P1-B/P2。
不得进入论文正文正式改写。
不得写入成果区。
不得把任何结果写成真实目标/望远镜/operational-ready 验证。
```

## 7. 给 Claude 的最短提示词

```text
请严格按 Codex R101 审阅执行：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R101_Codex_审阅_1C-B4-FIX01通过_P1-A闭口并放行合并裁决准备.md

输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
99_1C-B5_头A头B合并裁决准备_Claude执行报告.md

只做头A/头B合并裁决准备：汇总头A R90 稳定结论、头B B1/B2/B3/P0/P1-A 稳定结论，形成“可进入论文叙事 / 只作诊断材料 / 禁止 claim / 暂缓路线”四列表，并给出 Figure/SI/Results 候选承接关系和成果区同步建议。

不得训练、不得新渲染、不得生成新数据集、不得改 split、不得改模型/loss/head/超参/seed、不得 checkpoint forward、不得启动 P1-B/P2、不得写成果区、不得正式改写论文正文、不得触发真实目标/望远镜/operational-ready claim。
```


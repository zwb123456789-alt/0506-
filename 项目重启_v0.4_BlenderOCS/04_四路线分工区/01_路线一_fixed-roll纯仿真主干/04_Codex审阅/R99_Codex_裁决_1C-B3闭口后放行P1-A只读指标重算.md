# R99 Codex 裁决：1C-B3 闭口后放行 P1-A 只读指标重算

最后更新：2026-06-29
裁决端：Codex
依据：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R98_Codex_审阅_1C-B3-FIX02通过_P0只读诊断闭口.md

04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
96_1C-B3-FIX02_P0只读诊断图表与口径修正_Claude执行报告.md
```

## 0. 总裁决

```text
头B-B3/P0 已闭口。
放行下一步：1C-B4 / P1-A 只读指标重算任务。
```

本裁决只放行 `P1-A 第一阶段：只读/推理侧指标重算`，不放行训练、不放行模型结构修改、不放行 loss/output head 修改、不放行 split 修改、不放行 P1-B、不放行 P2、不放行成果区归档、不放行论文正文正式改写、不触发头A/头B大合并裁决。

## 1. 对 96 提出问题的裁决

| 问题 | 裁决 | 说明 |
|---|---|---|
| Q1. P0 是否可判定闭口 | 是 | R98 已判定 96_FIX02 通过，P0 只读诊断闭口 |
| Q2. 是否放行 P1-A 推理侧先行 | 是，限第一阶段 | 仅放行只读指标重算，不训练、不改模型、不改 split |
| Q3. Image/Joint embedding 导出是否仍需要 | 暂缓 | P1-A 第一阶段优先使用已有 predictions/logits/metrics；embedding 导出另设阶段门 |
| Q4. FIX02 口径修正是否合规 | 接收 | top-5、V0.3 split、sequence near 组、diagonal count 口径已修正 |
| Q5. 产出文件是否需同步到成果区 | 否 | 当前仍停留在诊断区，不写入成果区 |

## 2. 放行 P1-A 的理由

P0 已经稳定支持以下判断：

```text
1. exact-bin 0% 不能读成 yaw 信息完全不存在。
2. exact-bin 5 deg 分类判据在 yaw-block 外推协议下显著放大失败。
3. coarse-bin / within-k / circular MAE 一类指标更适合承接 R82/E45B 的 extrapolation gap 叙事。
4. C2/C3 exact diagonal count 为 0，但 P0 诊断仍显示粗粒度和连续角度口径值得重算。
```

因此 P1-A 的合理目标不是“补救模型”，而是：

```text
在不改变模型、不重训、不改 split 的前提下，
用连续/圆周角度指标重新刻画已存在预测输出中的外推误差结构，
判断 exact-bin 0% 下是否仍存在可报告的 coarse/circular 信号。
```

## 3. P1-A 第一阶段允许范围

允许 Claude 下一步执行：

```text
任务名：
1C-B4_P1-A只读指标重算与阶段门判断

建议输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
97_1C-B4_P1-A只读指标重算与阶段门判断_Claude执行报告.md
```

允许操作：

```text
1. 读取既有 C2/C3 per-sample predictions、confusion matrices、logits/probabilities、metrics、split manifest。
2. 若已有 logits/probabilities，计算 circular expected yaw、top-k circular alternatives 或 soft circular MAE。
3. 若只有 predicted bin/argmax，计算 circular MAE、median circular AE、within-1/2/3/6 bins、coarse45/coarse90、fold-wise mean/std。
4. 对 C2 OCS-only、C3 image_only、C3 joint 分别重算同一组指标。
5. 输出按 fold、channel、true yaw block、pitch 分层的表格。
6. 生成只读图表：circular error distribution、within-k curve、coarse-bin confusion、fold-wise summary。
7. 写出 P1-A 是否值得进入第二阶段的判定矩阵。
```

## 4. P1-A 第一阶段禁止事项

禁止 Claude 下一步执行：

```text
不得训练或重训练。
不得新渲染。
不得生成新数据集。
不得修改 split。
不得修改模型结构。
不得修改 loss、output head、超参或 seed。
不得把 P1-A 写成模型补救已经成功。
不得写入成果区。
不得改论文正文。
不得启动 P1-B 非朴素 fusion。
不得启动 P2 formal light-curve sequence。
不得触发头A/头B大合并裁决。
```

如果现有文件中没有 logits/probabilities：

```text
不得为了补 logits 直接加载 checkpoint 做 forward。
本轮只记录“logits/probabilities 缺失”，并基于已有 argmax/bin 预测重算 circular 与 coarse 指标。
checkpoint forward / embedding 或 logits 导出需另设 D 类只读导出阶段门。
```

## 5. P1-A 必须回答的问题

Claude 执行报告必须回答：

```text
1. exact-bin 0% 下，circular MAE / median AE 是否仍明显优于 random 或 naive baseline？
2. within-1/2/3/6 bins 是否高于 chance/random baseline？
3. coarse45/coarse90 是否稳定高于 chance/random baseline？
4. C3 image_only 与 joint 相比 C2 OCS-only 是否有任何一致提升？
5. 错误是否集中在特定 yaw block、pitch 或 fold？
6. P1-A 结果是否足以支持后续第二阶段：
   a. 仅作为论文指标重构材料；
   b. 申请 logits/checkpoint 只读导出；
   c. 申请真正训练侧 continuous/circular head；
   d. 或停止 P1-A，不再补救。
```

## 6. 最低产物要求

Claude 至少输出：

```text
1. p1a_metric_recompute_summary.md
2. p1a_channel_fold_metrics.csv
3. p1a_circular_error_by_channel.csv
4. p1a_within_k_curve.csv
5. p1a_coarse_bin_metrics.csv
6. p1a_random_or_naive_baseline.md
7. p1a_stage_gate_matrix.md
8. 若生成图件，统一放在 v0.4_results/09_p1a_metric_recompute/
```

若某些输入缺失，必须输出缺口清单：

```text
缺失文件是什么；
预期位置是什么；
本轮采用了什么替代口径；
是否需要后续单独阶段门。
```

## 7. 判据边界

P1-A 允许使用的论文叙事边界：

```text
可以写：
- exact-bin 是哨兵指标；
- circular/coarse/within-k 指标用于刻画 extrapolation gap；
- P1-A 是对既有负结果的指标重构，不是新成功实验。

不得写：
- yaw 信息已经恢复；
- 模型已经解决外推；
- joint fusion 已证明互补；
- V0.3 与 V0.4 可以直接横向比较；
- sequence 已被否定或替代；
- 真实目标/望远镜/operation-ready 相关 claim。
```

## 8. 给 Claude 的最短提示词

```text
请严格按 Codex R99 裁决执行：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R99_Codex_裁决_1C-B3闭口后放行P1-A只读指标重算.md

输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
97_1C-B4_P1-A只读指标重算与阶段门判断_Claude执行报告.md

只做 P1-A 第一阶段只读指标重算：读取既有 predictions/confusion/logits/metrics/split，重算 circular MAE、within-k、coarse45/coarse90、random/naive baseline、fold/channel/pitch/yaw-block 分层结果和阶段门矩阵。

不得训练、不得新渲染、不得生成新数据集、不得改 split、不得改模型/loss/output head/超参/seed、不得写成果区、不得改论文正文、不得启动 P1-B/P2、不得触发头A/头B大合并裁决。若 logits/probabilities 缺失，不得直接 forward，先记录缺口并用已有 argmax/bin 预测完成可做部分。
```


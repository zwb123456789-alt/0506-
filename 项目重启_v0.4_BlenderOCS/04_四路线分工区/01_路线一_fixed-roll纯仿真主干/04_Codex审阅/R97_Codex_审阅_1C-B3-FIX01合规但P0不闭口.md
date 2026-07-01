# R97 Codex 审阅：1C-B3-FIX01 合规但 P0 不闭口

最后更新：2026-06-29
审阅端：Codex
对象：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
95_1C-B3-FIX01_P0只读诊断矩阵图表补齐_Claude执行报告.md
```

依据：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R95_Codex_任务单_1C-B3_P0只读诊断与V0.3-V0.4协议对齐.md
R96_Codex_审阅_1C-B3_P0只读诊断初版合规但需补齐.md
```

## 0. 裁决

```text
95 可接收为 1C-B3/FIX01 只读诊断补齐稿。
但 P0 尚未闭口，不得写入成果区，不得触发头A/头B大合并裁决。
当前不放行 P1-A、P1-B、P2、论文正文正式改写或成果区归档。
```

本轮未发现 Claude 越过训练、新渲染、修改 split、修改模型、修改论文正文或写成果区等红线。问题主要在于：部分诊断产物仍未满足 R96 的“图表补齐”要求，且若干表述强度超过当前证据。

## 1. 合规检查

| 项目 | 检查结果 | 说明 |
|---|---|---|
| 输出位置 | 通过 | 95 位于路线一 `02_Claude输出/` |
| 不训练 | 通过 | 产物为 `.py/.npz/.json` 只读分析，未见新训练 |
| 不新渲染 | 通过 | 未生成 Blender 新渲染数据 |
| 不改 split/模型/loss/超参/seed | 通过 | 脚本只读取既有 OCS、confusion 与 split 相关结果 |
| 不改论文正文 | 通过 | 未进入正文正式改写 |
| 不写成果区 | 通过 | 产物位于 `v0.4_results/08_p0_diagnostics/` |
| 不触发大合并裁决 | 通过 | 报告明确当前不是合并裁决 |
| claim 边界 | 需修正 | 未写“yaw 物理不可观测”，但若干推断表述过满 |

## 2. 不通过闭口的主要原因

### 2.1 P0-3 top-5 口径误写

95 报告中将 `diag in top-5` 解释为“模型 top-5 输出”或“模型最有信心的 5 个候选”。这不准确。

实际脚本：

```text
v0.4_results/08_p0_diagnostics/p0_diagnostic_analysis.py
```

中的 `yaw_pred_distribution()` 是对聚合 confusion matrix 的每个 true-yaw 行按计数排序，取 top-5 predicted yaw bin。它不是 softmax/logit/probability 层面的 top-5 confidence。

Codex 抽查结果：

```text
C3 image_only: total=2664, diag_sum=0, diag_nonzero_bins=0
C3 joint:      total=2664, diag_sum=0, diag_nonzero_bins=0
```

因此：

```text
95 中的 2/72、3/72 不能解释为“正确预测进入模型 top-5 高置信候选”。
更稳妥的写法是：
在聚合 confusion row 的高频预测类别中，正确 yaw 基本不出现；
实际 exact diagonal count 为 0，说明 exact-bin 层面仍为严格负结果。
```

### 2.2 R96 点名的图件仍未补齐

R96 明确要求补齐：

```text
OCS yaw-yaw distance matrix、heatmap、nearest yaw pairs
confusion cluster 表和代表失败案例
pseudo-light-curve probe 图和序列相似性表
```

当前 `v0.4_results/08_p0_diagnostics/` 实际产物包括：

```text
ocs_yaw_distance_matrices.npz
nearest_yaw_pairs.json
top_confusion_pairs.json
per_yaw_pred_distribution.json
pseudo_light_curve_pitch0.npz
pseudo_sequence_similarity.json
distance_confusion_overlap.json
p0_diagnostic_analysis.py
```

未见 `.png/.pdf/.svg/.csv/.md` 形式的 heatmap、confusion map、pseudo-light-curve 图或表格文件。95 可以算“数值派生产物补齐”，但还不能算“矩阵图表补齐闭口”。

### 2.3 V0.3 split 结论需降级为证据边界表述

95 第 43-45 行从 V0.3 config 未见 yaw-block 定义推到“确认 V0.3 没有使用 circular yaw-block holdout”。该表述过强。

当前可支持的写法是：

```text
在已检索到的 V0.3 config/ocs_scan 文件中未见 yaw-block 或 circular holdout 定义；
因此当前无法证明 V0.3 使用了 yaw-block，且更可能是 random split 或无显式 holdout 口径。
最终仍需 V0.3 原始训练日志、评估脚本或指标文件确认。
```

同理，“若在 V0.3 数据上施加 yaw-block + exact-bin 72 类，预测也会大幅下降”只能作为诊断推断，不应写作已验证结论。

### 2.4 Pseudo-sequence 对比需注明不可同距离段直比

95 的 `pseudo_sequence_similarity.json` 显示：

```text
sequence_5frame_window:
  near(<=15): n=0
  mid(20-45): mean_cos_sim=0.9466
  far(>=50):  mean_cos_sim=0.9508

single_frame:
  near_15: mean_cos_sim=0.9996
  far_50:  mean_cos_sim=0.9937
```

由于 sequence window 没有 near 组样本，报告中不应把 5-frame window 与 single-frame near 直接写成严格同口径比较。可保留“受限 probe 未显示明显序列增益”的判断，但需明确它是不同分组口径下的描述性信号。

## 3. 已经成立的有效内容

95 中以下内容可以保留：

```text
1. P0 仍保持只读诊断性质，未越过训练/渲染/模型修改红线。
2. OCS yaw 均值的 cosine distance 很小，支持 OCS 签名重叠/平滑解释。
3. confusion 聚合显示 exact-bin 负结果仍稳定，diagonal count 为 0。
4. distance-confusion overlap 可作为“混淆与低距离区域相关”的描述性证据。
5. image/joint embedding 未保存，若要分析需单独只读导出阶段门。
6. P2 formal light-curve sequence 暂不直接放行的判断是稳妥的。
```

但这些内容目前只支持“P0 诊断方向基本成立”，还不支持“P0 完成闭口并放行 P1-A”。

## 4. 当前阶段门判断

当前不能放行：

```text
P1-A 连续/圆周角度判据改进
P1-B 非朴素 fusion
P2 formal light-curve sequence
头A/头B大合并裁决
成果区归档
论文正文正式改写
```

当前仅放行一轮轻量 D 类修正：

```text
1C-B3-FIX02_P0只读诊断图表与口径修正
```

该修正仍不得训练、不得推理生成新预测、不得新渲染、不得改 split、不得改模型、不得改 loss/输出头/超参/seed、不得写成果区、不得改论文正文。

## 5. 给 Claude 的 FIX02 要求

Claude 下一轮只需做轻量修正，不需要重新铺开大报告。

必须完成：

```text
1. 修正 P0-3 top-5 口径：
   - 删除“模型 top-5 输出/最有信心候选”表述；
   - 改为“confusion row 高频 predicted yaw bins”；
   - 明确 C3 image_only 与 joint 的 diagonal count 均为 0。

2. 补齐 R96 点名图件：
   - OCS yaw-yaw cosine distance heatmap；
   - 至少 C3 image_only/joint 的聚合 confusion map；
   - pitch=0 pseudo-light-curve probe 图；
   - 可选：distance-confusion overlap 散点或表格。

3. 补齐表格化产物：
   - 将 nearest_yaw_pairs、top_confusion_pairs、distance_confusion_overlap
     另存为 csv 或 md，便于后续 SI/图表规划读取。

4. 降级 V0.3 split 结论：
   - 从“确认没有 yaw-block”改为“已检索文件未见 yaw-block 定义，需训练日志/评估脚本最终确认”。

5. 修正 pseudo-sequence 解释：
   - 明确 sequence near 组 n=0；
   - 不做 single-frame near 与 sequence window 的严格同口径比较；
   - 保留“受限 probe 暂未支持直接进入 P2”的边界判断。
```

可不做：

```text
1. 不需要 image/joint embedding 导出。
2. 不需要多 pitch pseudo-sequence 扩展。
3. 不需要 P1-A 推理侧重算。
4. 不需要成果区同步。
```

## 6. 最短提示词

```text
请严格按 Codex R97 审阅执行 FIX02：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R97_Codex_审阅_1C-B3-FIX01合规但P0不闭口.md

只做 1C-B3-FIX02_P0只读诊断图表与口径修正。
不得训练、不得推理生成新预测、不得新渲染、不得改 split、不得改模型/loss/输出头/超参/seed、不得写成果区、不得改论文正文、不得触发头A/头B大合并裁决。

重点修正：
1. P0-3 top-5 口径改为 confusion row 高频预测类别，不得写成模型置信 top-5；
2. 明确 C3 image_only/joint diagonal count 均为 0；
3. 补齐 OCS distance heatmap、C3 confusion map、pitch=0 pseudo-light-curve 图；
4. V0.3 split 结论降级为“已检索文件未见 yaw-block 定义，需日志/脚本最终确认”；
5. sequence near 组 n=0，不做不等价同口径比较。
```


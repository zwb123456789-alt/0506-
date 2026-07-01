# R98 Codex 审阅：1C-B3-FIX02 通过，P0 只读诊断闭口

最后更新：2026-06-29
审阅端：Codex
对象：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
96_1C-B3-FIX02_P0只读诊断图表与口径修正_Claude执行报告.md
```

依据：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R95_Codex_任务单_1C-B3_P0只读诊断与V0.3-V0.4协议对齐.md
R96_Codex_审阅_1C-B3_P0只读诊断初版合规但需补齐.md
R97_Codex_审阅_1C-B3-FIX01合规但P0不闭口.md
```

## 0. 裁决

```text
96_1C-B3-FIX02 通过。
头B-B3/P0 只读诊断可判定闭口。
```

本轮只确认 P0 只读诊断闭口，不等同于放行训练、不等同于放行 P1-A 执行、不等同于成果区归档、不触发头A/头B大合并裁决。

当前可进入的下一步是：由 Codex/作者另行裁定是否写 `P1-A 连续/圆周角度判据改进` 的阶段门任务单。未有新任务单前，Claude 不得自行启动 P1-A、P1-B、P2 或成果区同步。

## 1. R97 要求核对

| R97 要求 | 检查结果 | 说明 |
|---|---|---|
| 修正 P0-3 top-5 口径 | 通过但需边界保留 | 96 已改为 confusion row 高频预测类别，并说明不是模型置信 top-5 |
| 明确 C3 image/joint diagonal count | 通过 | `diagonal_exact_stats.csv` 显示两者 diag_sum 均为 0 |
| 补齐 OCS distance heatmap | 通过 | 已生成 `p0_ocs_yaw_distance_heatmap.png` |
| 补齐 C3 confusion map | 通过 | 已生成 `p0_c3_confusion_maps.png` |
| 补齐 pitch=0 pseudo-light-curve 图 | 通过 | 已生成 `p0_pseudo_light_curve_pitch0.png` |
| 表格化 json 产物 | 通过 | 已生成 nearest/confusion/overlap/diagonal csv 与 pseudo sequence md |
| V0.3 split 结论降级 | 通过 | 已改为“已检索文件未见定义，需日志确认” |
| pseudo-sequence near 组 n=0 | 通过 | 已明确不同分组口径不可直接横比 |

## 2. 产物抽查

新增产物位于：

```text
v0.4_results/08_p0_diagnostics/
```

已确认存在：

```text
p0_ocs_yaw_distance_heatmap.png
p0_c3_confusion_maps.png
p0_pseudo_light_curve_pitch0.png
nearest_yaw_pairs.csv
top_confusion_pairs_c3_image_only.csv
top_confusion_pairs_c3_joint.csv
top_confusion_pairs_c2_baseline_4dim.csv
distance_confusion_overlap.csv
diagonal_exact_stats.csv
pseudo_sequence_similarity.md
p0_fix02_visualize.py
```

图件尺寸抽查：

```text
p0_ocs_yaw_distance_heatmap.png: 1800 x 1500
p0_c3_confusion_maps.png:       3000 x 1350
p0_pseudo_light_curve_pitch0.png: 2100 x 1200
```

脚本 `p0_fix02_visualize.py` 只读取既有 `.npz/.json` 与既有 confusion matrix，执行 matplotlib 可视化与 json-to-csv/md 转换，未见训练、新渲染、模型推理、split 修改或正文修改。

关键数值抽查：

```text
C3_image_only,total_samples=2664,diag_sum=0,diag_nonzero_bins=0,diag_exact_yaw_accuracy=0.0
C3_joint,total_samples=2664,diag_sum=0,diag_nonzero_bins=0,diag_exact_yaw_accuracy=0.0
```

## 3. 残余边界

96 已修正大部分口径，但仍需在后续使用中保留以下边界：

```text
1. 2/72 与 3/72 不得写成模型 top-5 confidence，也不宜作为主证据。
   因为 exact diagonal count 为 0，这两个数只能作为 confusion row 排序副产物或频次描述。

2. P0-2 的 OCS distance 只证明当前 4D OCS 聚合签名在 yaw 维度高度重叠。
   不得写成 yaw 物理不可观测，也不得泛化到所有 image/joint embedding。

3. V0.3 split 只能写作“已检索文件未见 yaw-block 定义，需日志/脚本最终确认”。
   不得恢复为“确认 V0.3 没有 yaw-block”。

4. P0-4 pseudo-sequence 是 single-pitch、no-evolution、pseudo probe。
   可用于暂缓 P2，不能用于证明 formal light-curve sequence 无价值。
```

以上边界不阻止 P0 闭口，但必须随 P0 材料一起保留，防止后续论文叙事或阶段门申请出现过度 claim。

## 4. P0 闭口后的稳定判断

P0 当前可稳定支持：

```text
1. R04/C2/C3 的 exact-bin 0% 不是“yaw 信息完全不存在”的证据。
2. exact-bin 5 deg 分类判据在 yaw-block 外推协议下显著放大失败。
3. 当前 4D OCS yaw 签名存在强重叠和平滑性，支持输入签名/几何可辨识性不足解释。
4. C3 image_only 与 joint 在当前 early concat/当前判据下未改善 exact-bin diagonal，不能支持 naive fusion 互补增益。
5. Pseudo-light-curve probe 暂未给出足够证据直接进入 P2 formal sequence。
6. V0.3/V0.4 因 split、bin、判据、前向模型口径不同，不可直接横向写成同一成功/失败链。
```

## 5. 后续阶段门建议

当前仍不得直接执行：

```text
P1-A 推理侧重算或重训练
P1-B 非朴素 fusion
P2 formal light-curve sequence
image/joint embedding 导出
成果区归档
论文正文正式改写
头A/头B大合并裁决
```

但可以由 Codex/作者下一步另行起草并审定：

```text
1C-B4 / P1-A 连续/圆周角度判据改进任务单
```

建议 P1-A 若被放行，应先限定为：

```text
1. 优先 D 类/轻 C 类：在既有 C3/C2 输出或 checkpoint 基础上重算 circular MAE、within-k、coarse-bin、sin-cos/circular 口径。
2. 不直接重训练。
3. 不改 split。
4. 不改论文正文。
5. 若推理侧重算显示有价值，再另设逐 fold 重训练阶段门。
```

## 6. 最短状态更新

```text
头B-B3/P0 已闭口。
96_FIX02 合规通过，补齐 R97 要求的图件、表格与口径修正。
下一步不自动进入 P1-A；仅允许 Codex/作者另行决定是否起草 P1-A 阶段门任务单。
```


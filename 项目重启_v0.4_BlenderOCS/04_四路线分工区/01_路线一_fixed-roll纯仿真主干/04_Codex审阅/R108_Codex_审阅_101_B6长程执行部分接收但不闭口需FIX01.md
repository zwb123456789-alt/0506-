# R108 Codex 审阅：101 B6 长程执行部分接收，但不支持阶段闭口，需 FIX01

最后更新：2026-06-30  
审阅端：Codex  
被审阅报告：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/101_1C-B6_A类同门判据回归与噪声增广真改进长程执行_Claude执行报告.md
```

相关产物：

```text
06_v0.4_code/07_training/train_b6_circular_regression.py
06_v0.4_code/07_training/postprocess_b6_circular_metrics.py
v0.4_results/10_b6_circular_regression/
v0.4_results/09_p1a_metric_recompute/p1a_channel_fold_metrics.csv
```

## 0. 裁决

**101 部分通过：接收为 B6 fold0 pilot 与代码初版。**

**101 不通过：不能作为 B6 阶段门闭口，不能据此放行 T2/T3，也不能进入头A/头B合并裁决。**

原因不是“没有结果”，而是结果目前仍是 **fold0 单折 + pooled baseline 对照 + final-epoch 评估**。它已经提供了真实技术信号，但证据强度不足以支撑报告中若干较强判断，尤其是：

```text
“circular regression 比 baseline 更差”
“训练判据非主因已被证伪”
“augmentation 显著负面可作为正式结论”
“下一步可直接裁定进入 T3”
```

更稳妥的阶段判断是：

```text
B6 已经证明：把 exact-bin 分类头替换为 sin/cos circular regression 后，
fold0 上 yaw block 外推仍未被实质解决；pitch 明显改善，说明回归头不是整体无效。

但 B6 尚未证明：训练判据/输出头不是主因，也尚未完成对 augmentation 的正式否定。
```

## 1. 合规与正向价值

101 有实质推进，不能当成普通叙事报告打回。

已通过项：

- 新建 `train_b6_circular_regression.py`，使用同门编码器容量，仅改变输出头与损失。
- 新建 `postprocess_b6_circular_metrics.py`，生成 run summary、baseline comparison、yaw-block/pitch-band 分层。
- fold0 跑通 5 个正式 run：`image_only none`、`joint none`、`ocs_only none`、`image_only standard`、`joint standard`。
- smoke、日志、checkpoint、samples、metrics 均落盘。
- 未新渲染、未改 split、未覆盖旧结果链、未写成果区、未改论文正文。

最有价值的技术信号：

- yaw 仍困难：fold0 no-aug 的 yaw cMAE 约 96.3°/99.6°，hit@30 约 0.28/0.23，coarse90 约 0.27，说明 single-frame yaw-block 外推没有被回归头自然修复。
- pitch 明显改善：image/joint no-aug pitch MAE 约 14.9°/15.7°，说明 continuous head 对可内插的姿态量有效，问题集中在 yaw 外推，而不是训练脚本完全失效。
- yaw-block 分层有诊断价值：同为 fold0 test，`[45,90)` 明显优于 `[0,45)`，强化“位置/外推距离依赖”而非“yaw 完全不可观测”的判断。

## 2. 主要问题

### 2.1 只跑 fold0，不能支持 B6 闭口

101 明确只完成 fold0，没有完成 5-fold。R107 允许先交 fold0 pilot，但没有授权用单折结果完成阶段门裁决。

fold0 的结果可以回答：

```text
在 fold0 上，circular regression 没有把 yaw 外推救回来。
```

但不能回答：

```text
在整个 yaw-block 协议下，训练判据/输出头不是主因。
```

原因是前序 P1-A 已经证明 yaw-block 间差异很强；单折结果不能代表所有 holdout 弧段。

### 2.2 baseline 对照口径错误，导致“更差于 baseline”的强结论不成立

101 的 `b6_vs_p1a_baseline_summary.csv` 用的是：

```text
B6 fold0
vs
P1-A 5-fold pooled baseline
```

这是 apples-to-oranges。更合理的初步对照应使用 P1-A fold0：

```text
p1a_channel_fold_metrics.csv
```

fold0 对齐后，关键值如下：

| 通道 | P1-A fold0 cMAE | B6 fold0 no-aug cMAE | 初步读法 |
|---|---:|---:|---|
| C3 image_only | 20.8919 bins = 104.46° | 96.26° | cMAE 略好，但 within/coarse 未同步改善 |
| C3 joint | 20.1586 bins = 100.79° | 99.63° | cMAE 基本持平 |
| C2 ocs_only | 15.1207 bins = 75.60° | 112.06° | B6 明显更差 |

因此，101 中“image/joint B6 比 P1-A baseline 更差”的表述需要撤回或改写。更准确的是：

```text
在 fold0 的 image/joint 上，circular regression 没有形成稳定、全面的 yaw 改善；
cMAE 可能略好或持平，但 within-k / coarse direction 指标没有同步改善，
ocs_only 明显退化。
```

这个修正很重要，因为它直接影响“训练判据是否主因”的因果判断。

### 2.3 final-epoch 评估不足以支撑“回归头无效”

`train_b6_circular_regression.py` 当前在最后一轮训练结束后直接评估并保存 checkpoint，没有按验证集 best epoch 选择模型。

训练日志显示验证集波动很大：

- image_only none：val yaw cMAE 从 125.6° 降到 44.4°，最后 epoch 为 48.3°。
- joint none：val yaw cMAE 从 152.8° 降到 47.2°，最后 epoch 为 48.7°。
- augmentation run 波动更剧烈，部分 epoch 短暂出现较好验证值后又崩。

这说明 B6 当前可作为 pilot，但正式裁决需要至少补充：

```text
final-epoch test
best-val checkpoint test
```

或者明确证明 final epoch 与 best-val epoch 的结论一致。

### 2.4 augmentation 结论应保留为 fold0 现象

101 的 augmentation 结果确实很差，尤其 image/joint standard 的 yaw 指标几乎归零。但目前不能把它写成“噪声增广正式无效/有害”的全局结论。

限制包括：

- 只有 fold0。
- augmentation 是固定组合包：Gaussian + brightness + torch.roll shift，无法区分哪个因素导致退化。
- `torch.roll` 是 wrap shift，在边界引入非物理环绕；即使黑背景下影响可能小，也不应作为正式否定噪声建模的唯一依据。

可以保留的表述是：

```text
在 fold0、当前固定 augmentation 包下，增广没有改善 yaw 外推，且明显恶化。
```

不能写成：

```text
噪声/光照扰动作为方向已被否定。
```

### 2.5 T3 方向优先级上升，但不能由 101 直接放行

R105/R106 已经把真实场景主线提升为：

```text
稀疏 GEO 光度时序 / 多帧多几何 photometric sequence
```

101 的 fold0 结果确实让 T3 更有吸引力：single-frame 的 yaw-block 外推仍然难，且 pitch 可内插、yaw 不可稳定外推，符合“需要时序/多几何约束”的直觉。

但 101 不能直接放行 T3。B6 至少需要一个 FIX01，把 A 类同门真改进做成可审计的多折结果，否则又会从一个未闭合技术试验跳到下一段叙事。

## 3. 对 101 问题的回答

### Q1：fold0 是否足以支撑“训练判据非主因”？

**不足以。**

fold0 支持较弱说法：

```text
仅替换成 circular regression，在 fold0 上没有修复 yaw-block 外推。
```

fold0 不支持较强说法：

```text
训练判据/输出头不是主因。
```

必须补 5-fold，至少补齐 no-aug 的 image_only/joint/ocs_only 三通道；若资源允许，再补 augmentation。

### Q2：augmentation 负面是否能保留为正式结论？

**只能保留为 fold0 现象，不能作为正式全局结论。**

正式结论需要 5-fold 或至少在多个 fold 上复核；更理想的是拆分：

```text
noise-only
brightness-only
shift-only / no-wrap-shift
combined
```

当前阶段若资源有限，不要求立刻拆全套 ablation，但报告必须收窄措辞。

### Q3：是否据此放行 T3？

**不放行。**

T3 的优先级继续上升，但 B6 还没有完成阶段门。下一步应是 B6-FIX01 长程补齐，而不是启动 T3 或合并裁决。

## 4. B6-FIX01 必做项

下一轮不要再做小盘点，直接给 Claude 下达一个长程执行任务。

必须完成：

1. 补齐 5-fold no-aug：

```text
image_only / joint / ocs_only
fold 0..4
aug none
```

2. augmentation 至少完成一档可审计复核：

```text
优先 image_only / joint, fold 0..4, aug standard
若资源不足，必须明确记录只完成哪些 fold，不能写全局结论。
```

3. 后处理必须新增 fold-matched baseline：

```text
B6 fold k vs P1-A fold k
per-fold mean
pooled
best/worst yaw-block
```

不能再只用 B6 fold0 对 P1-A pooled。

4. 训练脚本必须加入或补算 best-val 口径：

```text
保存 best-val checkpoint，或至少从每 epoch checkpoint 中取 best-val 模型评估 test。
若不保存每 epoch checkpoint，则下一轮脚本需实现 save-best。
```

5. 结论措辞必须分级：

```text
已确认：exact-bin 作为评价指标过严。
B6 fold0 支持：换 circular regression 不足以解决 yaw 外推。
待确认：训练判据/输出头是否非主因。
待确认：augmentation 是否全局有害。
```

## 5. 给 Claude 的 FIX01 长程提示词

可直接复制给 Claude：

```text
你现在执行 1C-B6-FIX01：B6 circular regression 多折补齐与 fold-matched baseline 修正。必须先读取：

04_Codex审阅/R104_Codex_审阅_100通过_头B转入A类同门真改进阶段.md
04_Codex审阅/R105_Codex_补充裁决_光变曲线上调为头B真实场景主线.md
04_Codex审阅/R106_Codex_数据核验_GEO真实光度库支持稀疏光度时序主线.md
04_Codex审阅/R107_Codex_任务单_1C-B6_A类同门判据回归与噪声增广长程执行.md
04_Codex审阅/R108_Codex_审阅_101_B6长程执行部分接收但不闭口需FIX01.md
02_Claude输出/101_1C-B6_A类同门判据回归与噪声增广真改进长程执行_Claude执行报告.md

任务目标：
不要再写方案盘点。直接在现有 B6 代码基础上补齐可审计结果，用于判断 A 类同门判据回归是否真的不能解决 yaw-block 外推。

执行内容：

1. 修改或扩展 train_b6_circular_regression.py：
   - 保持同门编码器容量、split、数据、图像、OCS 输入不变。
   - 增加 best-val checkpoint 保存，主选择指标优先 val_yaw_cmae_deg；若你认为应同时记录 val_pitch_mae，可并列记录但不得改成调参搜索。
   - 最终同时输出 final-epoch test 与 best-val test，文件名必须可区分。

2. 补齐正式多折：
   - 必跑：mode=image_only/joint/ocs_only, aug=none, fold=0..4。
   - 尽量跑：mode=image_only/joint, aug=standard, fold=0..4。
   - 如果算力不足，至少先完成 no-aug 5-fold，并把 augmentation 明确降级为 fold0 pilot，不得写全局结论。

3. 修改 postprocess_b6_circular_metrics.py：
   - 新增 b6_foldmatched_vs_p1a.csv：每个 B6 run 必须和 P1-A 相同 fold、相同对应通道对比。
   - 同时保留 pooled 对照，但 pooled 只能作为补充。
   - 输出 per-fold mean、pooled、best/worst fold、best/worst yaw-block。
   - 明确区分 final-epoch 与 best-val 两套结果。

4. 产物目录：
   - 可继续写入 v0.4_results/10_b6_circular_regression/，但不得覆盖旧 fold0 原始结果；若会覆盖，改写到 v0.4_results/10_b6_circular_regression_fix01/。

5. 报告必须提交：
   - 02_Claude输出/102_1C-B6-FIX01_多折补齐与fold-matched baseline修正_Claude执行报告.md
   - 列出所有命令、退出码、运行时长、失败/跳过项。
   - 给出阶段门矩阵，但不得自行放行 T2/T3/头A头B合并裁决。

红线：
不新渲染；不改 split；不改姿态网格；不改旧结果链；不写成果区；不进入 T3；不写论文正文；不把 GEO 库写成 supervised attitude truth；不把 fold0 现象写成全局结论。

最终你必须回答：
1. 5-fold 下 circular regression 相对 fold-matched P1-A 是否有稳定 yaw 改善？
2. best-val 与 final-epoch 是否改变结论？
3. pitch 改善是否稳定存在？
4. augmentation 是否仍然负面，还是只是 fold0/实现包现象？
5. B6 是否可以闭口；如果不能，缺口是什么？
```

## 6. 当前阶段门状态

```text
B6 状态：pilot 有效，阶段未闭口。
T1 circular regression：fold0 不足以解决 yaw 外推，5-fold 待确认。
T1' augmentation：fold0 当前包明显负面，全局待确认。
T2 非朴素 fusion：暂不放行。
T3 稀疏 GEO 光度时序 / 多帧多几何：方向优先级上升，但暂不放行。
头A/头B合并裁决：暂不放行。
```

一句话结论：

```text
101 终于拿出了真训练结果，这是进步；但它只能把 B6 推入 FIX01，
不能把 B6 直接写成闭口，也不能把“负结果困境”提前转成 T3 叙事。
```

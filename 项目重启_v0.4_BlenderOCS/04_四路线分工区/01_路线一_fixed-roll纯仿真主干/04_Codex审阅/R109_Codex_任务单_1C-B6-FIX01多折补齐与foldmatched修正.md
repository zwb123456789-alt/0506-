# R109 Codex 任务单：1C-B6-FIX01 多折补齐与 fold-matched baseline 修正

最后更新：2026-06-30  
下达端：Codex  
执行端：Claude  
任务性质：长程执行任务，必须产生可审计训练结果、日志、指标表和报告；禁止只写方案或叙事盘点。

## 0. 先读文件

执行前必须读取：

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R104_Codex_审阅_100通过_头B转入A类同门真改进阶段.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R105_Codex_补充裁决_光变曲线上调为头B真实场景主线.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R106_Codex_数据核验_GEO真实光度库支持稀疏光度时序主线.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R107_Codex_任务单_1C-B6_A类同门判据回归与噪声增广长程执行.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R108_Codex_审阅_101_B6长程执行部分接收但不闭口需FIX01.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/101_1C-B6_A类同门判据回归与噪声增广真改进长程执行_Claude执行报告.md
```

## 1. 背景裁决

101 已被 Codex 裁定为：

```text
接收为 B6 fold0 pilot 与代码初版。
不通过为 B6 阶段门闭口。
不放行 T2/T3/头A头B合并裁决。
```

主要原因：

```text
1. 只完成 fold0，不能代表 5-fold yaw-block 协议。
2. B6 fold0 对比 P1-A 5-fold pooled baseline，口径不匹配。
3. 当前脚本只评估 final epoch，没有 best-val checkpoint/test 口径。
4. augmentation 只能算 fold0 现象，不能作为全局结论。
```

## 2. 任务目标

本轮目标不是继续论证“为什么负结果合理”，而是用真实训练和对齐指标回答：

```text
在同一 yaw-block 协议、同门编码器容量、fold-matched baseline 下，
把 exact-bin 分类头改为 sin/cos circular regression，
是否能稳定改善 yaw 外推？
```

必须产出可审计结果，并给出是否允许 B6 闭口的技术依据。

## 3. 代码要求

在现有 B6 代码基础上扩展，不要重写整套训练框架。

目标脚本：

```text
06_v0.4_code/07_training/train_b6_circular_regression.py
06_v0.4_code/07_training/postprocess_b6_circular_metrics.py
```

### 3.1 train 脚本必须补充 best-val 口径

要求：

```text
1. 保持同门编码器容量、split、数据、图像、OCS 输入不变。
2. 保持 circular regression 输出 [yaw_sin, yaw_cos, pitch_sin, pitch_cos]。
3. 增加 best-val checkpoint 保存。
4. 主 best 指标优先 val_yaw_cmae_deg 最小。
5. 输出 final-epoch test 与 best-val test，两者文件名必须可区分。
```

推荐输出命名：

```text
metrics_val_final.json
metrics_test_final.json
metrics_val_best.json
metrics_test_best.json
samples_test_final.npz
samples_test_best.npz
checkpoint_final.pt
checkpoint_best.pt
train_log.csv
```

如果为了兼容旧后处理保留原名 `metrics_test.json`，必须在报告中说明它对应 final 还是 best，不得含混。

### 3.2 postprocess 必须修正 baseline 对照

必须新增：

```text
b6_foldmatched_vs_p1a.csv
```

要求：

```text
1. 每个 B6 run 只和相同 fold 的 P1-A baseline 对比。
2. image_only 对 C3_image_only。
3. joint 对 C3_joint。
4. ocs_only 对 C2_baseline_4dim。
5. cMAE 单位必须统一为 degree。
6. 同时输出 delta：B6 - P1A，负值表示 B6 更好。
```

同时保留 pooled 对照，但 pooled 只能作为补充，不能作为主裁决依据。

## 4. 必跑实验矩阵

### 4.1 必跑 no-aug 5-fold

必须完成：

```text
mode=image_only, aug=none, fold=0..4
mode=joint,      aug=none, fold=0..4
mode=ocs_only,   aug=none, fold=0..4
```

fold0 已有结果可以复用，但若脚本新增 best-val 口径后无法从旧 checkpoint 补算 best，则需要重新跑 fold0。

### 4.2 augmentation 复核

尽量完成：

```text
mode=image_only, aug=standard, fold=0..4
mode=joint,      aug=standard, fold=0..4
```

如果算力不足，优先级如下：

```text
第一优先级：no-aug 5-fold 三通道完整。
第二优先级：image_only/joint standard 5-fold。
第三优先级：augmentation 拆分 ablation。
```

若 augmentation 未完成 5-fold，必须在报告中把 augmentation 降级为 pilot 现象，不能写成全局结论。

## 5. 指标与表格

至少输出以下文件：

```text
b6_run_metrics_summary_final.csv
b6_run_metrics_summary_best.csv
b6_foldmatched_vs_p1a_final.csv
b6_foldmatched_vs_p1a_best.csv
b6_pooled_vs_p1a_final.csv
b6_pooled_vs_p1a_best.csv
b6_yawblock_stratified_final.csv
b6_yawblock_stratified_best.csv
b6_pitchband_stratified_final.csv
b6_pitchband_stratified_best.csv
b6_fix01_postprocess_summary.json
```

必须包含指标：

```text
yaw_cmae_deg
yaw_median_deg
yaw_p90_deg
yaw_hit@5
yaw_hit@10
yaw_hit@30
yaw_within_1bin
yaw_within_2bin
yaw_within_6bin
yaw_exact_sentinel
yaw_coarse45
yaw_coarse90
pitch_mae_deg
pitch_hit@5
pitch_hit@10
pitch_hit@30
```

必须给出：

```text
per-fold 结果
per-fold delta vs P1-A fold-matched baseline
pooled 结果
best fold / worst fold
best yaw-block / worst yaw-block
final vs best-val 差异
```

## 6. 阶段门回答

报告最后必须逐条回答：

```text
1. 5-fold 下 circular regression 相对 fold-matched P1-A 是否有稳定 yaw 改善？
2. best-val 与 final-epoch 是否改变结论？
3. pitch 改善是否稳定存在？
4. augmentation 是否仍然负面，还是只是 fold0/实现包现象？
5. “训练判据/输出头不是主因”是否可以从待确认改为较稳定判断？
6. B6 是否可以闭口；如果不能，缺口是什么？
7. 是否建议进入 T2 或 T3；注意只能建议，不能自行放行。
```

允许的结论强度：

```text
已确认：exact-bin 作为评价指标过严。
已确认/待确认：按 FIX01 结果决定。
禁止：用 fold0 现象写全局结论。
禁止：用 pooled baseline 替代 fold-matched 主裁决。
```

## 7. 输出位置

结果目录：

```text
v0.4_results/10_b6_circular_regression_fix01/
```

如果复用原目录，也必须保证不覆盖 101 已有 fold0 原始结果。推荐直接使用新目录。

报告文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/102_1C-B6-FIX01_多折补齐与foldmatched修正_Claude执行报告.md
```

报告必须列出：

```text
命令
退出码
运行时长
GPU/环境
完成矩阵
跳过项及原因
全部产物清单
关键指标表
阶段门判断
红线自检
```

## 8. 红线

```text
不新渲染。
不改 split。
不改姿态网格。
不改旧结果链。
不写成果区。
不写论文正文。
不进入 T2/T3 正式执行。
不触发头A/头B合并裁决。
不把 GEO 库写成 supervised attitude truth。
不把 augmentation fold0 现象写成全局结论。
不把 pooled baseline 当作主对照。
```

## 9. 完成标准

本任务完成的最低标准：

```text
no-aug image_only/joint/ocs_only 5-fold 全部完成；
final 与 best-val 两套口径可审计；
fold-matched P1-A 对照表生成；
报告能够判断 B6 是否闭口。
```

若只完成 fold0 或只补叙事，本任务视为未完成。

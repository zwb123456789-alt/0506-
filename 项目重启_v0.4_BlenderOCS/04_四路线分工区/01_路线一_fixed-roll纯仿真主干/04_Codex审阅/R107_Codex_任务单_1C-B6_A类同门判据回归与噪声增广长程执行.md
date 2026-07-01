# R107 Codex 任务单：1C-B6 A类同门判据回归与噪声增广长程执行

最后更新：2026-06-30
下达端：Codex
执行端：Claude
任务性质：长程执行任务，不是方案盘点，不是叙事闭口，不是合并裁决准备。

## 0. 交给 Claude 的任务提示词

请按本任务单执行：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R107_Codex_任务单_1C-B6_A类同门判据回归与噪声增广长程执行.md
```

本轮目标是完成：

```text
1C-B6_A类同门判据回归与噪声增广真改进长程执行
```

本任务不是让你再写一份路线建议，而是要求你交付能被 Codex 审阅的完整执行包：

```text
读取上下文 -> 定位训练代码和 split -> 副本实现 -> smoke -> 至少一个正式 fold 结果 -> 指标/分层表 -> 执行报告。
```

如果训练因环境、依赖或算力失败，必须给出可复现命令、错误日志、已生成文件和技术阻塞说明。不得把失败转写为“阶段闭口”或“叙事收口”。

---

## 1. 必读上下文

先读以下文件，不要凭记忆执行：

```text
CLAUDE.md

04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R104_Codex_审阅_100通过_头B转入A类同门真改进阶段.md
R106_Codex_数据核验_GEO真实光度库支持稀疏光度时序主线.md
```

若需要理解为什么本轮不能继续写叙事报告，可读：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R105_Codex_补充裁决_光变曲线上调为头B真实场景主线.md
```

本轮必须记住：

```text
1. 100/R104 不是头B闭口，而是把头B推进到 B6 真改进。
2. exact-bin 作为评价口径太严苛已经确认。
3. exact-bin/classification 作为训练判据是否是失败主因尚未确认，需本轮 B6/T1 实测。
4. 本轮不能只交“方案/盘点/暂缓解释/合并准备”。
5. 本轮输出必须能让 Codex 看见技术实施结果或明确技术阻塞。
```

---

## 2. 本轮要回答的技术问题

本轮要回答：

```text
Q1. 如果把训练目标从 72-bin exact classification 改为 continuous/circular regression，
    yaw-block 外推是否出现实质改善？

Q2. 如果对图像通道加入受控 train-time noise/augmentation，
    image_only / joint 的 yaw-block 外推是否更稳？

Q3. 若仍失败，失败更像训练判据问题、图像干净伪捷径问题，还是 single-frame 信息形态不足？
```

注意：

```text
本轮不是要证明真实 GEO 反演成功。
本轮不是要启动光变曲线/真实数据 T3。
本轮只是 B6：single-frame benchmark 内的低成本混杂项清理。
```

---

## 3. 允许读取和派生的代码

必须先定位并读取当前训练相关文件：

```text
06_v0.4_code/07_training/train_baseline.py
06_v0.4_code/07_training/train_c2_screening.py
06_v0.4_code/07_training/dataset.py
06_v0.4_code/07_training/enhanced_ocs_dataset.py
```

可按需读取诊断/后处理口径：

```text
06_v0.4_code/09_diagnostics/e45a_postprocess.py
v0.4_results/09_p1a_metric_recompute/p1a_metric_recompute.py
```

可按需读取当前 split 和结果目录：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/
v0.4_results/06_c3_preflight/
v0.4_results/05_c2_screening/
v0.4_results/08_p0_diagnostics/
v0.4_results/09_p1a_metric_recompute/
```

必须以副本或新脚本方式实现，不得原地破坏旧链。推荐新脚本名：

```text
06_v0.4_code/07_training/train_b6_circular_regression.py
06_v0.4_code/07_training/postprocess_b6_circular_metrics.py
```

若你选择其他文件名，必须在报告中说明原因和文件清单。

---

## 4. 结果目录和报告路径

所有新结果写入：

```text
v0.4_results/10_b6_circular_regression/
```

Claude 执行报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
101_1C-B6_A类同门判据回归与噪声增广真改进长程执行_Claude执行报告.md
```

禁止写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
论文正文目录
旧 R04/R21/E25/C2/C3 结果链目录
```

---

## 5. 模型与训练目标要求

### 5.1 必做 T1：continuous/circular regression

最低实现：

```text
输入模式沿用现有 mode：
  ocs_only
  image_only
  joint

split 沿用现有 circular yaw-block 5-fold。
数据、姿态网格、几何采样、backbone 容量不作为主变量修改。
```

推荐 target：

```text
yaw target:
  [sin(yaw_rad), cos(yaw_rad)]

pitch target:
  [sin(pitch_rad), cos(pitch_rad)]

输出为 4D continuous vector。
```

推荐 decode：

```text
yaw_pred_deg = atan2(yaw_sin, yaw_cos) mod 360
pitch_pred_deg = atan2(pitch_sin, pitch_cos)，并裁剪到 [-90, 90]
```

推荐 loss：

```text
MSE on normalized sin/cos pairs
或 MSE + unit-norm penalty
```

如果你选择 regression + classification sentinel 双头：

```text
classification head 只作 sentinel 或辅助损失；
不得让 exact-bin 重新成为主训练目标；
必须报告 loss 权重。
```

如果你选择 regression-only：

```text
仍必须通过 decoded angle -> nearest 5° bin 计算 exact-bin sentinel，
以便和旧 baseline 对照。
```

### 5.2 必做 T1'：受控图像 noise/augmentation 对照

必须实现一个受控、固定、不调参的 train-time augmentation 开关。

建议设置：

```text
gaussian noise sigma = 0.01
brightness jitter = ±10%
integer shift = up to 2 px
```

要求：

```text
1. 只在 train split 启用。
2. val/test 不启用。
3. ocs_only 不参与图像 augmentation 轴。
4. 参数固定写入 run config，不做搜索。
5. 若某项 augmentation 实现风险高，可先只实现 gaussian noise + brightness jitter，但必须说明原因。
```

---

## 6. 最小实验矩阵

本轮必须至少完成 smoke，并尽力完成正式 fold0。不能只停在代码实现。

### 6.1 Smoke

必须跑：

```text
mode=image_only, fold=0, no_aug, max_epochs=1 或 subset smoke
mode=joint, fold=0, no_aug, max_epochs=1 或 subset smoke
```

smoke 验收：

```text
loader 正常；
forward 正常；
loss finite；
参数更新非零；
decode 正常；
metrics JSON 能落盘。
```

### 6.2 正式最小结果

至少跑出以下正式 fold0 结果：

```text
M1: circular regression, no augmentation
  - image_only, fold0
  - joint, fold0

M2: circular regression, augmentation-on
  - image_only, fold0
  - joint, fold0
```

建议额外跑：

```text
M1: circular regression, no augmentation
  - ocs_only, fold0
```

如果资源允许，扩展到 5-fold：

```text
fold0-fold4:
  image_only M1/M2
  joint M1/M2
  ocs_only M1
```

若无法完成 5-fold，不得伪装成正式 5-fold；必须在报告中明确：

```text
本轮完成 fold0 正式结果；
5-fold 未完成的原因；
预计运行命令和剩余计算量。
```

---

## 7. 指标与输出要求

每个 run 必须输出：

```text
run_config.json
train_log.csv
metrics_val.json
metrics_test.json
samples_test.npz 或 samples_test.csv
```

样本级预测至少包含：

```text
record_id
yaw_true_deg
pitch_true_deg
yaw_pred_deg
pitch_pred_deg
yaw_true_bin
pitch_true_bin
yaw_pred_bin_sentinel
pitch_pred_bin_sentinel
yaw_circular_error_deg
pitch_abs_error_deg
fold
mode
augmentation
```

必须计算：

```text
yaw circular MAE
yaw median / p75 / p90
yaw Hit@5 / Hit@10 / Hit@30
yaw within-1-bin / within-2-bin / within-6-bin
yaw exact-bin sentinel
yaw coarse45 / coarse90 accuracy
pitch MAE
pitch Hit@5 / Hit@10 / Hit@30
pitch exact-bin sentinel
per-fold summary
yaw-block stratified summary
pitch-band stratified summary
```

必须和旧 baseline 对照。至少引用旧结果表路径：

```text
v0.4_results/09_p1a_metric_recompute/
```

如果能自动读取旧 baseline，则输出：

```text
b6_vs_p1a_baseline_summary.csv
```

如果不能自动读取，也必须在报告中手工列出旧 P1-A 关键对照数值来源路径。

---

## 8. 阶段门判断要求

报告最后必须回答：

```text
1. B6 是否成功运行？
2. continuous/circular regression 相比 exact-bin baseline 是否有实质改善？
3. augmentation-on 相比 no_aug 是否有边际改善？
4. yaw-block worst cases 是否改善？
5. 失败若仍存在，更像：
   a) 训练判据问题；
   b) 图像干净伪捷径问题；
   c) single-frame 信息不足；
   d) fusion 结构问题；
   e) split/yaw-block 外推协议问题。
6. 下一步建议：
   - B6 可否进入 Codex 审阅；
   - 是否需要 FIX；
   - 是否应启动 T2 非朴素 fusion；
   - 是否应准备 T3 稀疏 GEO 光度时序 / 多帧多几何阶段门。
```

不得自行宣布：

```text
头B闭口；
头A/头B合并裁决开始；
论文正文可改；
成果区可归档。
```

这些只能由 Codex 审阅后裁定。

---

## 9. 红线

本轮禁止：

```text
不新渲染。
不改 split。
不改姿态网格。
不改几何采样。
不把 backbone 容量升级作为主变量。
不做超参搜索。
不覆盖旧 R04/R21/E25/C2/C3 结果链。
不写论文正文。
不写成果区。
不触发头A/头B合并裁决。
不启动路线二/路线三正式数据线。
不把 GEO 真实光度库写成监督姿态反演数据集。
不把 smoke 当正式结论。
```

允许：

```text
复制/派生训练脚本；
新增 B6 后处理脚本；
写入 v0.4_results/10_b6_circular_regression/；
在 B6 范围内训练/评估/保存 checkpoint；
在 B6 报告中提出下一步建议，但不得自行放行。
```

---

## 10. 执行报告结构

执行报告必须使用以下结构，避免长篇叙事：

```text
# 101_1C-B6 A类同门判据回归与噪声增广真改进长程执行报告

## 0. 结论先行
写明：完成 / 部分完成 / 技术阻塞。

## 1. 输入与上下文
列出读取的关键文件。

## 2. 代码改动
列出新增/派生脚本，不贴长代码。

## 3. 实验矩阵
列出 mode/fold/augmentation/epochs/seed。

## 4. 运行命令与日志
列出实际命令、运行状态、失败命令。

## 5. 结果文件清单
列出 v0.4_results/10_b6_circular_regression/ 下关键文件。

## 6. 指标结果
表格列出 baseline vs B6。

## 7. yaw-block / pitch-band 分层
列出关键 block 变化。

## 8. 阶段门判断
回答本任务单第 8 节问题。

## 9. 红线自检
逐条确认。

## 10. 交给 Codex 的待审问题
只列真正需要裁决的问题。
```

---

## 11. 最短执行提醒

```text
不要再只写方案。
不要再只写“建议暂缓”。
不要自行合并裁决。
本轮必须交代码、命令、日志、指标和结果；否则就是技术阻塞，不是闭口。
```


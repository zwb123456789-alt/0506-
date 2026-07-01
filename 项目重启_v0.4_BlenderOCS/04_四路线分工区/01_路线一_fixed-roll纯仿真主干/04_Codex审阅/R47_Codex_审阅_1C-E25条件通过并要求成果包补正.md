# R47 Codex 审阅：1C-E25 多折 yaw_block 训练结果

最后更新：2026-06-25  
审阅端：Codex  
被审阅报告：`02_Claude输出/48_1C-E25_多折yaw_block训练结果_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E25 主结果：CONDITIONAL PASS
5-fold strict yaw_block 结论：PASS
路径 B 科学结论：基本闭合
成果包状态：NEEDS ARTIFACT FIX
论文正文改写：NOT RELEASED
B1 / GGX / 三轴 / 其他路线：NOT RELEASED
下一步：1C-E25-FIX01，只做成果包补正，不重训
```

Codex 复核后确认，E25 的核心科学结果成立：5 折 `circ_yaw_block` strict holdout 下，全部 fold 的 `test_primary.yaw_acc = 0.00%`，跨折 test yaw bin 覆盖 `72/72` 且重复为 `0`。这足以把 FIX01 单折负结果升级为 5-fold cross-validation 级别的稳健负结果。

但 E25 产物尚不能直接作为最终闭合包归档，原因是总汇总 JSON、overlap 证据文件和报告统计口径存在可追溯性问题。该问题不推翻训练结果，但必须通过一个轻量 FIX 补齐。

---

## 1. 已复核通过的内容

### 1.1 Split 覆盖与互斥性

Codex 读取并复核：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold0.json
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold1.json
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold2.json
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold3.json
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold4.json
```

复核结果：

| Fold | Test yaw | Test bins | Train bins | Val bins | Test samples | Pitch test |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 0-70 deg | 15 | 50 | 7 | 555 | 37/37 |
| 1 | 75-145 deg | 15 | 50 | 7 | 555 | 37/37 |
| 2 | 150-215 deg | 14 | 51 | 7 | 518 | 37/37 |
| 3 | 220-285 deg | 14 | 51 | 7 | 518 | 37/37 |
| 4 | 290-355 deg | 14 | 51 | 7 | 518 | 37/37 |

跨折 test yaw：

```text
unique test yaw bins = 72
total test yaw bins  = 72
duplicates           = 0
```

每折内部 record overlap：

| Fold | train-val | train-test | val-test | Train N | Val N | Test N |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 1850 | 259 | 555 |
| 1 | 0 | 0 | 0 | 1850 | 259 | 555 |
| 2 | 0 | 0 | 0 | 1887 | 259 | 518 |
| 3 | 0 | 0 | 0 | 1887 | 259 | 518 |
| 4 | 0 | 0 | 0 | 1887 | 259 | 518 |

结论：split gate 实质通过。

### 1.2 训练结果复核

Codex 读取每折：

```text
fold*/e21_fix01_baseline_results.json
fold*/e21_fix01_detail_image_only.json
```

`test_primary` 结果如下：

| Fold | yaw_acc | pitch_acc | yaw_cmae | pitch_mae | N |
|---|---:|---:|---:|---:|---:|
| 0 | 0.00% | 22.52% | 105.5 deg | 36.2 deg | 555 |
| 1 | 0.00% | 13.51% | 71.2 deg | 37.2 deg | 555 |
| 2 | 0.00% | 18.53% | 114.9 deg | 44.9 deg | 518 |
| 3 | 0.00% | 18.34% | 80.7 deg | 35.9 deg | 518 |
| 4 | 0.00% | 30.50% | 45.2 deg | 26.5 deg | 518 |

聚合值：

```text
yaw_acc mean = 0.00%, std = 0.00%
pitch_acc mean = 20.68%
yaw_cmae mean = 83.48 deg
pitch_mae mean = 36.14 deg
```

若使用总体标准差：

```text
pitch_acc std = 5.68%
yaw_cmae std  = 24.88 deg
pitch_mae std = 5.82 deg
```

若使用样本标准差：

```text
pitch_acc std = 6.35%
yaw_cmae std  = 27.82 deg
pitch_mae std = 6.50 deg
```

E25 报告中 `pitch_acc std = 5.80%` 与原始 JSON 复算不完全一致，疑似混用了 `pitch_mae` 的总体标准差。该误差不影响 yaw 泛化失败结论，但需要补正或明确统计口径。

### 1.3 Random split 对照复核

每折 `test_random` 结果与报告一致：

| Fold | random yaw_acc | random pitch_acc | N |
|---|---:|---:|---:|
| 0 | 67.91% | 75.68% | 296 |
| 1 | 67.91% | 71.28% | 296 |
| 2 | 57.77% | 69.59% | 296 |
| 3 | 68.92% | 76.69% | 296 |
| 4 | 64.53% | 76.35% | 296 |

该对照支持核心解释：模型在 in-distribution/random test 上可以学习，但在 strict unseen yaw holdout 上 yaw 泛化失败。

---

## 2. 主要问题

### Finding 1：缺少 E25 总汇总 JSON

R46 要求 E25 最终输出 5 折汇总 JSON。当前目录：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/
```

只包含：

```text
split_manifest_circ_yawblock_fold0.json
...
split_manifest_circ_yawblock_fold4.json
fold0/
...
fold4/
```

未发现：

```text
e25_multifold_summary.json
```

影响：报告中已有聚合表，但机器可读汇总产物缺失，后续成果归档、论文表格生成和复核会变弱。

处理：需要补生成 `e25_multifold_summary.json`，不得重训。

### Finding 2：训练脚本保存的 overlap report 为空

每折目录中存在：

```text
fold*/e21_fix01_overlap_report.json
```

但文件长度为 2 字节，内容为 `{}`。同时每折 `e21_fix01_baseline_results.json` 中：

```json
"overlap_check": {}
```

这说明训练脚本保存的 overlap 证据为空，疑似执行时使用了 `--skip-overlap-check` 或未保留检查结果。

Codex 已从 manifest 独立复核 overlap gate 通过，所以这不是数据泄漏问题；但作为成果包，overlap 证据必须落地。

处理：补写一个总 overlap report，或重新运行只读 overlap 检查并写入每折 overlap report；不得重训。

### Finding 3：报告代码改动清单不完整

E25 报告的产物清单只写：

```text
06_v0.4_code/07_training/split_dataset.py -> circ_yaw_block 方法新增
```

但当前工作树显示：

```text
M 06_v0.4_code/07_training/split_dataset.py
M 06_v0.4_code/07_training/train_baseline.py
```

`train_baseline.py` 中包含 device auto、DataLoader workers、strict holdout manifest、额外 eval manifest、overlap check 输出等修改。E25 训练结果依赖这些改动，报告必须补写该文件的改动范围，否则审计链不完整。

处理：E25-FIX01 报告中补充 `train_baseline.py` 改动说明，尤其说明该改动是复用 FIX01 支持而非本轮新方案扩展。

### Finding 4：报告文本存在编码/统计口径问题

当前 E25 报告在终端读取时存在若干乱码，关键位置包括：

```text
72/72 被显示为 2/72
37/37 被显示为 7/37
角度范围中的连接符与度符号显示异常
```

如果原文件在编辑器中显示正常，可只在 FIX01 中说明终端编码问题；如果文件本身已经乱码，应重写一个 UTF-8 正常显示版报告或补充清洁版附录。

统计口径方面，`pitch_acc std` 需要按原始 JSON 修正为：

```text
population std = 5.68%
sample std     = 6.35%
```

并在报告中明确采用哪一种。

---

## 3. 科学结论边界

本轮可以引用的结论：

```text
在 B0 fixed-roll image_only baseline 上，5-fold circular yaw_block strict holdout
评估显示，跨未见 yaw 区间的 yaw 分类准确率稳定为 0.00%。
这说明当前 CNN + B0 图像通道不具备 zero-shot unseen-yaw 泛化能力。
```

可以作为消融章 strong negative evidence 的口径：

```text
5-fold circular yaw-block cross-validation:
mean yaw_acc = 0.00%, std = 0.00%.
```

需要谨慎的口径：

```text
pitch_acc 在 strict yaw holdout 下仍显著高于 1/37 随机水平，
但相比 random split 大幅下降，说明 yaw 分布缺失会连带削弱 pitch 估计。
```

不能写：

```text
不能写成真实未知目标姿态反演系统失败或成功。
不能外推到 B1/GGX、OCS-only、joint 或三轴。
不能据此启动论文正文改写。
不能据此跳过 B1/GGX 或路线 C/D 的后续裁决。
```

---

## 4. E25-FIX01 执行要求

E25-FIX01 只允许做成果包补正，不允许重训。

允许：

1. 从现有 `fold*/e21_fix01_baseline_results.json` 与 `fold*/e21_fix01_detail_image_only.json` 聚合生成：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_multifold_summary.json
```

2. 从现有 5 个 split manifest 重新计算并写入：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_overlap_report.json
```

3. 如需，也可补写每折：

```text
fold*/e21_fix01_overlap_report.json
```

4. 修正或补充 E25 报告：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/49_1C-E25-FIX01_成果包补正_Claude执行报告.md
```

禁止：

- 不重训任何 fold。
- 不修改训练结果数值。
- 不运行 `ocs_only` 或 `joint`。
- 不做超参搜索。
- 不启动 B1/GGX/三轴/路线二/路线三/路线四。
- 不写论文正文。
- 不修改冻结文件 13/14/24/25。
- 不写 `04_Codex审阅/`。

---

## 5. 给 Claude 的下一步短提示词

```text
执行 1C-E25-FIX01：只做 E25 成果包补正，不重训。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R47_Codex_审阅_1C-E25条件通过并要求成果包补正.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/48_1C-E25_多折yaw_block训练结果_Claude执行报告.md
- v0.4_results/03_training_baseline/e25_multifold_yawblock/

任务：
1. 不重训，从现有 fold0..fold4 JSON 汇总生成：
   v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_multifold_summary.json
2. 从 5 个 split_manifest_circ_yawblock_fold*.json 重新计算 overlap gate，生成：
   v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_overlap_report.json
3. 如方便，补写每折 fold*/e21_fix01_overlap_report.json，使其不再是空 JSON。
4. 写执行报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/49_1C-E25-FIX01_成果包补正_Claude执行报告.md
5. 报告中必须补充：
   - split_dataset.py 改动说明
   - train_baseline.py 改动说明
   - pitch_acc std 的统计口径修正：population std=5.68%，sample std=6.35%
   - 说明 E25 主结论仍为 yaw_acc mean=0.00%, std=0.00%

红线：
- 不重训。
- 不改原始训练结果。
- 不跑 ocs_only/joint。
- 不做超参搜索。
- 不写论文正文。
- 不启动 B1/GGX/三轴/路线二/路线三/路线四。
- 不改冻结文件。
- 不写 04_Codex审阅/。
- 若输出过长，按 Part 1/2/3 分段写入，直到文件完整。
```

---

## 6. 对红线的同步建议

本轮作者已明确：Codex 审阅文件不需要逐次询问，可以直接写入。建议后续在 `CLAUDE.md` 中把原红线修订为：

```text
Codex 审阅文件、返工单、阶段门判断和给 Claude 的下一步提示词，
属于 Codex 审阅端职责内产物，可直接写入对应路线 04_Codex审阅/。
但修改 CLAUDE.md、冻结文件、成果区、代码、数据结果或论文正文前，
仍需先列出拟修改文件、目的和范围，等待作者明确确认。
```

该同步建议本轮只记录在审阅文件中，尚未修改 `CLAUDE.md`。


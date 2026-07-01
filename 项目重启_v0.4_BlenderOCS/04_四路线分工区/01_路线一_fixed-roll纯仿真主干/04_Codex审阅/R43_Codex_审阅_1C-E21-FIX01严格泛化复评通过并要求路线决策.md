# R43 Codex 审阅：1C-E21-FIX01 yaw_block 严格泛化复评

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/44_1C-E21-FIX01_yawblock严格泛化复评_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E21-FIX01：PASS
严格 yaw_block holdout 协议：PASS
E21 泄漏诊断：CONFIRMED
跨未见 yaw 泛化：FAIL
论文正文改写：NOT RELEASED
下一步：1C-E22，路线一 C 结果边界与后续路径裁决准备
```

结论：E21-FIX01 严格复评成立。`split_manifest_yaw_block.json` 的 train/val/test record_id 无重叠，三模式在严格未见 yaw test 上 yaw accuracy 均为 0%。这确认 R42 的判断：E21 原 “yaw_block 泛化”结果是 train-test overlap 造成的伪影，不能作为泛化证据引用。

本轮接受的结论是负结果：当前 fixed-roll / B0 / 单视图图像 + 4 维 OCS baseline 不具备跨未见 yaw 区间的零样本泛化能力。该结果对路线一 C 很重要，但还不能直接写入论文正文；下一步应先做路线级边界整理与后续路径裁决。

---

## 1. Codex 核验证据

### 1.1 文件在位

```text
v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/
  e21_fix01_overlap_report.json
  e21_fix01_baseline_results.json
  e21_fix01_detail_ocs_only.json
  e21_fix01_detail_image_only.json
  e21_fix01_detail_joint.json
  checkpoint_ocs_only.pt
  checkpoint_image_only.pt
  checkpoint_joint.pt
```

代码：

```text
06_v0.4_code/07_training/train_baseline.py
```

### 1.2 Overlap 复核

Codex 读取 `e21_fix01_overlap_report.json`：

```text
train_manifest = split_manifest_yaw_block.json
method = yaw_block
train_n = 2109
val_n = 259
test_n = 296
train ∩ val = 0
train ∩ test = 0
val ∩ test = 0
is_strict = true
```

同时确认与 R42 诊断一致：

```text
yaw_block_train ∩ random_train = 1672
yaw_block_train ∩ random_val   = 207
yaw_block_train ∩ random_test  = 230
```

这说明 E21 原协议确实存在交叉污染；FIX01 协议本身严格。

### 1.3 训练结果复核

Codex 读取 `e21_fix01_baseline_results.json`：

严格 yaw_block test，即 `test_primary/test_yaw_block`：

```text
ocs_only:
  yaw_acc = 0.00%
  pitch_acc = 1.01%
  yaw_circular_mae = 98.26 deg

image_only:
  yaw_acc = 0.00%
  pitch_acc = 56.42%
  yaw_circular_mae = 41.03 deg

joint:
  yaw_acc = 0.00%
  pitch_acc = 44.26%
  yaw_circular_mae = 41.55 deg
```

random test 对照：

```text
ocs_only:
  yaw_acc = 10.47%
  pitch_acc = 4.39%

image_only:
  yaw_acc = 74.66%
  pitch_acc = 89.86%

joint:
  yaw_acc = 75.34%
  pitch_acc = 86.15%
```

### 1.4 脚本能力复核

`train_baseline.py` 已新增：

```text
--train-split-manifest
--eval-random-manifest
--eval-yaw-block-manifest
check_record_overlap()
check_cross_manifest_overlap()
```

Codex 检查到主训练集来自 `train_manifest`，主 val/test 也来自同一 manifest 的 val/test；额外 random/yaw_block 评估作为对照输出。

`py_compile train_baseline.py` 通过。

---

## 2. 通过范围

本轮确认：

- yaw_block strict holdout 复评协议成立；
- E21 原 yaw_block “泛化”结果不可作为泛化证据；
- 当前 baseline 的跨未见 yaw 泛化失败；
- pitch 仍可部分迁移，因为 pitch 在 train yaw 区间内全覆盖；
- checkpoint、metrics、detail JSON 已落盘；
- 未做大规模超参搜索；
- 未写论文正文；
- 未启动 B1/GGX/三轴/其他路线。

---

## 3. 必须撤回或降级的说法

以下说法在当前证据下不得继续使用：

```text
OCS 显著提升跨 yaw 几何泛化
joint 在 yaw_block 上优于 image_only，证明 OCS-image 互补泛化
E21 yaw_block 结果证明未见 yaw 泛化能力
```

可以保留但必须限定的说法：

```text
random split 下，image_only 与 joint 可在同分布/近邻姿态上取得较高精度。
严格 yaw holdout 下，当前 baseline 无法泛化到未见 yaw 区间。
当前 4 维 OCS 特征不提供足够跨 yaw 不变性。
pitch 在严格 yaw holdout 中仍有部分可迁移能力。
```

---

## 4. 路线含义

该负结果不等于路线一 C 失败。它说明路线一 C 的当前 B0 baseline 证据边界应改写为：

```text
在 full yaw 覆盖或 random split 的工程条件下，图像通道与 joint 模型可以学习 fixed-roll 姿态映射；
但当前单视图 CNN + 4 维 OCS 不能对完全未见 yaw 区间做零样本泛化。
```

这对 v0.4 主线是有价值的边界证据：它约束了“互补性” claim 的强度，也提示后续如果要主张跨几何泛化，需要新的协议或架构，而不是继续在当前 random split 上堆训练。

---

## 5. 下一步：1C-E22

下一步不应直接写论文正文，也不应立刻做大规模训练。建议执行：

```text
1C-E22：路线一 C 结果边界与后续路径裁决准备
```

目标：

1. 汇总 R38-R43 的数据与训练证据；
2. 区分：
   - fullrun corpus 生成成果；
   - random split 工程 baseline；
   - strict yaw_block 负结果；
3. 明确哪些结果可进入后续论文“实验设计/消融/负结果边界”，哪些不能；
4. 提出后续路径候选：
   - A：承认 fixed-roll random/in-distribution 训练为主，不主张未见 yaw 泛化；
   - B：设计多折/circular yaw block，更稳健描述泛化失败；
   - C：启动架构/特征改进专项，但不得无审阅直接进入大规模实验；
   - D：回到 B1/GGX/三轴之前先整理当前 B0 baseline 的科学边界。

---

## 6. 给 Claude 的下一步指令摘要

```text
执行 1C-E22：路线一 C 结果边界与后续路径裁决准备。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R43_Codex_审阅_1C-E21-FIX01严格泛化复评通过并要求路线决策.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R42_Codex_审阅_1C-E21工程baseline通过但泛化结论需返工.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/44_1C-E21-FIX01_yawblock严格泛化复评_Claude执行报告.md
- v0.4_results/03_training_baseline/e21_controlled_baseline/
- v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/

任务：
1. 汇总 R38-R43 的关键证据和路径。
2. 明确 E21 原 random-trained yaw_block 结果为何不可作为泛化证据。
3. 明确 E21-FIX01 strict yaw_block 的负结果边界。
4. 给出 2-4 条后续路线选择，每条写清目的、代价、风险和是否需要 Codex 再放行。
5. 不写论文正文，只写路线裁决准备材料。

输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/45_1C-E22_路线一C结果边界与后续路径裁决准备_Claude执行报告.md

红线：
- 不写论文正文。
- 不启动新训练或大规模实验。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不改冻结文件 13/14/24/25。
- 不写 04_Codex审阅/。
- 不把 E21 泄漏结果当作泛化证据。
```


# R42 Codex 审阅：1C-E21 受控 baseline 训练与评估

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/43_1C-E21_受控baseline训练与评估_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E21 工程训练执行：PASS
random split baseline：PASS
checkpoint / metrics 落盘：PASS
yaw_block “泛化”结论：FAIL / INVALID AS CLAIMED
论文级结论：NOT RELEASED
下一步：1C-E21-FIX01，修正泛化评估协议并复跑严格 yaw_block baseline
```

结论：E21 的训练基础设施和 random split 工程 baseline 成立，三模式训练、checkpoint、metrics JSON 和 per-bin/confusion 摘要均已落盘。但报告中的核心说法“yaw_block split 泛化”目前不成立。原因是训练使用的是 random train，而 yaw_block test 与 random train 大量 record_id 重叠，导致所谓 yaw_block test 并非未见样本评估。

因此，本轮不放行“跨 yaw 几何泛化”“OCS 显著提升泛化”等论文级或阶段性科学结论。下一步必须修正评估协议，用 yaw_block train 训练，再在 yaw_block val/test 上评估。

---

## 1. Codex 核验证据

### 1.1 文件在位

```text
06_v0.4_code/07_training/train_baseline.py
v0.4_results/03_training_baseline/e21_controlled_baseline/e21_baseline_results.json
v0.4_results/03_training_baseline/e21_controlled_baseline/e21_detail_ocs_only.json
v0.4_results/03_training_baseline/e21_controlled_baseline/e21_detail_image_only.json
v0.4_results/03_training_baseline/e21_controlled_baseline/e21_detail_joint.json
v0.4_results/03_training_baseline/e21_controlled_baseline/checkpoint_ocs_only.pt
v0.4_results/03_training_baseline/e21_controlled_baseline/checkpoint_image_only.pt
v0.4_results/03_training_baseline/e21_controlled_baseline/checkpoint_joint.pt
```

### 1.2 结果 JSON 与报告一致

Codex 读取 `e21_baseline_results.json`，关键指标与报告一致：

```text
random split:
  ocs_only    yaw_acc=8.78%,  pitch_acc=4.39%
  image_only  yaw_acc=81.76%, pitch_acc=88.51%
  joint       yaw_acc=88.51%, pitch_acc=93.58%

yaw_block reported:
  ocs_only    yaw_acc=5.41%,  pitch_acc=4.05%
  image_only  yaw_acc=77.36%, pitch_acc=97.64%
  joint       yaw_acc=85.14%, pitch_acc=97.30%
```

### 1.3 Checkpoint 可读取

Codex 读取 3 个 checkpoint，均包含：

```text
mode
epoch=20
seed=42
model_state
optimizer_state
history
final_eval
```

`model_state` 非空，checkpoint 可作为工程训练产物。

### 1.4 训练脚本语法检查

Codex 对 `train_baseline.py` 执行 `py_compile`，通过。

---

## 2. 阻断问题：yaw_block 泛化评估污染

### 2.1 脚本训练协议

`train_baseline.py` 当前逻辑：

```text
train_ds = split_manifest.json 的 train split，即 random train
val_random = split_manifest.json 的 val
val_yaw_block = split_manifest_yaw_block.json 的 val
test_random = split_manifest.json 的 test
test_yaw_block = split_manifest_yaw_block.json 的 test
```

也就是说，模型始终在 random train 上训练，然后额外评估 yaw_block val/test。

### 2.2 Codex overlap 检查

Codex 检查 record_id overlap：

```text
random_train ∩ yaw_block_train = 1672 / 2109
random_train ∩ yaw_block_val   = 204 / 259
random_train ∩ yaw_block_test  = 233 / 296
```

因此 yaw_block test 中约 78.7% 样本已经出现在训练集 random_train 中。该结果不能称为“未见 yaw 泛化”或“跨几何泛化”。

### 2.3 影响

以下报告表述必须降级或撤回：

```text
OCS 显著提升跨几何泛化
joint 比 image_only 在 yaw_block 上高 7.78 pp，证明跨 yaw 泛化互补
yaw_block split 为严格泛化评估
```

这些说法需要在无 overlap 的严格训练协议下重新验证。

---

## 3. 本轮通过范围

本轮可接受：

- random split 工程 baseline 已跑通；
- 三模式训练脚本可工作；
- checkpoint、metrics、per-bin、confusion 摘要已落盘；
- circular yaw MAE 已使用；
- 无大规模超参搜索；
- 未写论文正文；
- 未启动 B1/GGX/三轴/其他路线。

本轮不接受：

- yaw_block test 作为泛化证据；
- OCS 对跨 yaw 几何泛化提升的定量结论；
- 将 E21 结果写入论文正文；
- 进入下一轮大规模训练或超参搜索。

---

## 4. 1C-E21-FIX01 要求

下一步执行：

```text
1C-E21-FIX01：严格 yaw_block baseline 复评
```

必须完成：

1. 修改或新增训练入口，使训练 split 可显式选择  
   例如：

```text
--train-split-manifest split_manifest_yaw_block.json
--eval-random-manifest split_manifest.json
--eval-yaw-block-manifest split_manifest_yaw_block.json
```

2. 严格 yaw_block 训练协议  

```text
train = split_manifest_yaw_block.json / train
val   = split_manifest_yaw_block.json / val
test  = split_manifest_yaw_block.json / test
```

3. 验证无 overlap  

报告必须列出：

```text
yaw_block_train ∩ yaw_block_val = 0
yaw_block_train ∩ yaw_block_test = 0
yaw_block_val ∩ yaw_block_test = 0
```

4. 复跑三模式 baseline  

允许沿用 E21 的受控边界：

```text
mode = ocs_only / image_only / joint
epochs <= 20 或 R41 上限 <=30
lr = 1e-3
seed = 42
单一主配置，不做超参搜索
```

5. 输出路径不得覆盖 E21 原结果  

建议：

```text
v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/
```

6. 报告中必须明确区分：

```text
E21 random-trained baseline：工程 sanity
E21-FIX01 yaw_block-trained baseline：严格 yaw holdout 泛化
```

---

## 5. 给 Claude 的下一步指令摘要

```text
执行 1C-E21-FIX01：严格 yaw_block baseline 复评。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R42_Codex_审阅_1C-E21工程baseline通过但泛化结论需返工.md
- 06_v0.4_code/07_training/train_baseline.py
- v0.4_results/01_fullrun/postprocess/split_manifest.json
- v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json

任务：
1. 修改或新增训练入口，支持显式指定 train/eval manifest。
2. 用 split_manifest_yaw_block.json 的 train split 训练三模式 baseline。
3. 用 split_manifest_yaw_block.json 的 val/test 做严格 holdout 评估。
4. 计算并报告 train/val/test record_id overlap，必须为 0。
5. 输出 checkpoint、metrics JSON、per-yaw/per-pitch、confusion/error summary。
6. 结果写入：
   v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/
7. 报告写入：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/44_1C-E21-FIX01_yawblock严格泛化复评_Claude执行报告.md

红线：
- 不做大规模超参搜索。
- 不写论文正文。
- 不改冻结文件 13/14/24/25。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不写 04_Codex审阅/。
- 不把 E21 原 yaw_block 结果称为严格泛化证据。
```


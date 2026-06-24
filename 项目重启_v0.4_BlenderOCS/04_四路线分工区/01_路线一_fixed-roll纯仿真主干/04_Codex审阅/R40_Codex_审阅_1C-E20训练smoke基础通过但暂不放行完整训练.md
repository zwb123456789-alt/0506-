# R40 Codex 审阅：1C-E20 最小训练 smoke

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/41_1C-E20_最小训练smoke_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E20：CONDITIONAL PASS
训练基础设施 smoke：PASS
训练保护：PASS
circular yaw MAE 修正：PASS
三模式性能 smoke：PARTIAL
完整训练：NOT RELEASED
下一步：1C-E20-FIX01，修正 smoke 判据/结果结构并准备 E21 训练协议
```

结论：E20 已证明训练基础设施可运行：loss 可计算、反向传播正常、梯度有限、参数更新发生、val 指标可计算，`ocs_only` 与 `joint` 的 smoke 检查通过，训练保护也有效。  

但本轮不能放行完整训练。核心原因是 `train_smoke.py` 将 `val_yaw_acc_gt_random` 设为三模式的硬检查，导致 `image_only` 在 200 samples / 3 epochs 下 `smoke_pass=false`，脚本整体自动化语义不是全 PASS。这个失败更像“性能信号不足”，不是“训练管线失败”；但在训练流水线进入下一阶段前，必须把 infrastructure hard gates 与 performance diagnostic 分开。

---

## 1. Codex 核验证据

### 1.1 文件在位

```text
06_v0.4_code/07_training/train_smoke.py
06_v0.4_code/07_training/train_entry.py
v0.4_results/02_training_smoke/e20_min_train_smoke/e20_smoke_results.json
v0.4_results/02_training_smoke/e20_min_train_smoke/e20_history_image_only.json
v0.4_results/02_training_smoke/e20_min_train_smoke/e20_history_ocs_only.json
v0.4_results/02_training_smoke/e20_min_train_smoke/e20_history_joint.json
```

### 1.2 结果 JSON

Codex 读取 `e20_smoke_results.json`：

```text
config:
  max_epochs=3
  subset_size=200
  batch_size=32
  lr=0.001
  seed=42
  device=cpu
  modes=image_only, ocs_only, joint
```

三模式摘要：

```text
image_only:
  smoke_pass=false
  final_loss=6.9703
  val_yaw_acc=0.0050
  val_pitch_acc=0.0150
  val_yaw_circular_mae=92.80 deg
  failed_check=val_yaw_acc_gt_random

ocs_only:
  smoke_pass=true
  final_loss=7.8131
  val_yaw_acc=0.0200
  val_pitch_acc=0.0200

joint:
  smoke_pass=true
  final_loss=6.7484
  val_yaw_acc=0.0150
  val_pitch_acc=0.0300
```

### 1.3 训练保护复核

Codex 验证以下保护均生效：

```powershell
python train_smoke.py --max-epochs 1
# exit 1, blocked: 必须传 --train-smoke

python train_smoke.py --train-smoke --max-epochs 10
# exit 1, blocked: 超过 max epoch 硬上限 3

python train_smoke.py --train-smoke --subset-size 2048
# exit 1, blocked: 超过 subset 硬上限 1024
```

### 1.4 circular yaw 修正

Codex 检查 `train_entry.py`，确认 `compute_accuracy()` 已使用：

```text
min(abs(pred-true), n_yaw - abs(pred-true)) * 5 deg
```

`train_smoke.py` 也已实现 `circular_yaw_error_deg()`。

### 1.5 语法检查

Codex 对 `train_smoke.py` 和 `train_entry.py` 执行 `py_compile`，通过。

---

## 2. 审阅判断

### 2.1 训练基础设施通过

以下硬工程目标已达成：

- loss finite；
- backward 可执行；
- grad finite；
- param updated；
- val metric 可计算；
- 训练输出 JSON/history 可落盘；
- 训练保护参数有效；
- 不保存模型权重；
- 未做完整训练或超参搜索。

因此，E20 的“最小训练 smoke”目标可判为条件通过。

### 2.2 image_only 未超随机不是管线 bug

`image_only` 使用 3.87M 参数 CNN，在 200 samples / 3 epochs 下 yaw acc 低于随机基线。考虑到：

- 样本量极小；
- yaw 为 72 类；
- 图像 CNN 参数量远大于 OCS MLP；
- 训练目标是 smoke，不是性能训练；
- image_only 的 loss 有限、下降、梯度有限且参数更新；

Codex 判定这不是训练管线失败，也不能作为“图像通道无效”的科学结论。

### 2.3 但当前 smoke 判据不适合进入正式流水线

`val_yaw_acc_gt_random` 被设为三模式硬检查，会让正常的低样本 CNN smoke 以失败退出。这会混淆两类问题：

```text
infrastructure failure：loss/grad/param/NaN/path/device 等工程错误
performance diagnostic：是否超过随机基线、是否收敛、是否有早期信号
```

正式训练前必须把这两类结果拆开，避免后续自动化把“性能未达预期”误判为“训练脚本坏了”。

---

## 3. 本轮通过范围

通过：

- 1C-E20 最小训练 smoke 执行完成；
- 训练保护有效；
- ocs_only 与 joint 的 early signal 可作为工程观察；
- circular yaw MAE 已修正；
- 输出 JSON/history 可审计。

不通过/不放行：

- 完整训练；
- 正式性能结论；
- 论文正文引用；
- 超参搜索；
- 直接扩展 B1/GGX/三轴/路线二三四；
- 把 random split 结果作为泛化能力证据。

---

## 4. 下一步：1C-E20-FIX01

下一步不是完整训练，而是修正训练 smoke 判据并准备 E21 协议。

要求：

1. 修改 `train_smoke.py` 的结果结构  
   必须拆分：

```text
infrastructure_checks:
  loss_finite
  grad_finite_all
  param_updated
  loss_decreasing
  val_metric_finite

performance_diagnostics:
  val_yaw_acc_gt_random
  val_pitch_acc_gt_random
  yaw_circular_mae
  pitch_mae
```

2. `smoke_pass` 只能代表 infrastructure pass  
   不得因为 image_only 未超随机而让训练脚本整体失败。

3. 增加 `overall_infrastructure_status` 与 `performance_notes`  
   结果 JSON 必须明确说明 image_only 的低样本未超随机只是 diagnostic。

4. 生成 `yaw_block` split manifest  
   R39 已指出 random split 不能作为正式泛化证据。E20-FIX01 需至少生成：

```text
v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json
```

并报告 train/val/test 数量、yaw 覆盖、pitch 覆盖。

5. 只做必要 smoke 复跑  
   可以复跑 1 epoch / subset 200，用于验证新结果结构和保护逻辑；不得进入完整训练。

---

## 5. 给 Claude 的下一步指令摘要

```text
执行 1C-E20-FIX01：训练 smoke 判据修正与 yaw_block split 准备。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R40_Codex_审阅_1C-E20训练smoke基础通过但暂不放行完整训练.md
- 06_v0.4_code/07_training/train_smoke.py
- 06_v0.4_code/07_training/split_dataset.py

任务：
1. 修改 train_smoke.py，把 infrastructure_checks 与 performance_diagnostics 分开。
2. smoke_pass 只表示训练基础设施通过，不把 image_only 未超随机作为硬失败。
3. e20_smoke_results JSON 增加 overall_infrastructure_status、performance_notes。
4. 生成 split_manifest_yaw_block.json，并报告 yaw/pitch 覆盖与样本数。
5. 复跑最小验证：建议 --train-smoke --max-epochs 1 --subset-size 200。
6. 确认保护仍有效：缺 --train-smoke、epoch 超限、subset 超限均应阻断。

输出报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/42_1C-E20-FIX01_训练smoke判据修正_Claude执行报告.md

红线：
- 不做完整训练。
- 不做超参搜索。
- 不写论文正文。
- 不改冻结文件 13/14/24/25。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不写 04_Codex审阅/。
```


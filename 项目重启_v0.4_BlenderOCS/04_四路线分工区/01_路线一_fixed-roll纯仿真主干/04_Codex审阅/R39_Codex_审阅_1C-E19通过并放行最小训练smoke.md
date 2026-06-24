# R39 Codex 审阅：1C-E19 训练入口与数据切分准备

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/40_1C-E19_训练入口与数据切分准备_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E19：PASS
数据切分方案：PASS
Dataset / DataLoader：PASS
训练入口骨架：PASS
Loader / forward smoke：PASS
训练红线保护：PASS
完整训练：NOT RELEASED
下一步：1C-E20，最小训练 smoke，受控 1-3 epoch，不进入完整训练
```

结论：E19 已完成 R38 要求的训练准备工作。Codex 已核验 `07_training/` 代码、`split_manifest.json`、loader smoke、forward smoke 和 `--epochs>0` 阻断逻辑。当前可以放行下一步“最小训练 smoke”，用于验证训练循环、loss、optimizer、日志和结果落盘能否正常工作；但不得直接进入完整训练或正式性能结论。

---

## 1. Codex 核验证据

### 1.1 文件在位

```text
06_v0.4_code/07_training/__init__.py
06_v0.4_code/07_training/split_dataset.py
06_v0.4_code/07_training/dataset.py
06_v0.4_code/07_training/train_entry.py
v0.4_results/01_fullrun/postprocess/split_manifest.json
```

### 1.2 Split manifest

Codex 读取 `split_manifest.json`：

```text
method=random
seed=42
n_total=2664
train=2109
val=259
test=296
unique_record_ids=2664
duplicates=0
```

覆盖情况：

```text
train yaw=72/72, pitch=37/37
val   yaw=70/72, pitch=37/37
test  yaw=71/72, pitch=37/37
```

随机按 pitch 分层切分适合作为训练 smoke 与初轮工程验证。注意：该切分不用于严肃泛化结论，因为相邻 yaw/pitch 姿态会跨 split 分布；后续正式评估必须同时引入 `yaw_block` 或更严格的几何留出切分。

### 1.3 Loader smoke 复跑

Codex 运行：

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code\07_training\train_entry.py --smoke-only --batch-size 32
```

结果：

```text
train: 2109 samples, image=[32,1,256,256], ocs=[32,4], NaN=False, Inf=False, path OK
val:   259 samples,  image=[32,1,256,256], ocs=[32,4], NaN=False, Inf=False, path OK
test:  296 samples,  image=[32,1,256,256], ocs=[32,4], NaN=False, Inf=False, path OK
```

### 1.4 Forward smoke 复跑

Codex 运行：

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code\07_training\train_entry.py --forward-smoke --batch-size 32
```

三模式均跑通：

```text
image_only: yaw_logits=[32,72], pitch_logits=[32,37], params=3,865,613
ocs_only:   yaw_logits=[32,72], pitch_logits=[32,37], params=47,725
joint:      yaw_logits=[32,72], pitch_logits=[32,37], params=3,913,229
```

随机权重精度接近随机水平，符合 smoke 预期。

### 1.5 训练红线保护

Codex 运行：

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code\07_training\train_entry.py --epochs 1
```

结果：脚本以 code 1 退出，并输出当前阶段不允许训练的阻断提示。说明 E19 阶段确实没有启动训练。

### 1.6 语法与 GBK 清理

Codex 对三个训练脚本执行 `py_compile`，通过。  
Codex 对 Claude 声明清理的 3 个文件搜索 `⚠✅✓✗❌`，未发现残留。

---

## 2. 审阅发现

### P1：正式泛化评估不能只使用 random split

当前 random stratified-by-pitch split 会让相邻 yaw/pitch 的高度相似样本分布在 train/val/test 中。它适合 loader、训练循环和过拟合 sanity check，但不能单独作为论文级泛化证据。

要求：E20 只能使用 random split 做最小训练 smoke；E21 或正式训练评估前，必须生成并审阅 `yaw_block` 或更严格的几何留出 split，并把 random split 与 block split 的用途分开。

### P2：yaw 误差后续必须使用 circular error

`compute_accuracy()` 当前用 `abs(yaw_pred - yaw_true) * 5` 计算 yaw MAE。对于 yaw=0 和 yaw=355 的边界，这会错误放大误差。

要求：E20 若输出 yaw MAE，必须改为 circular yaw error：

```text
min(abs(pred-true), 72-abs(pred-true)) * 5 deg
```

pitch MAE 可继续使用普通绝对误差。

### P2：训练入口仍是骨架，不得直接升格为正式训练

`train_entry.py` 当前没有训练循环、optimizer、loss、checkpoint、日志、评估落盘和固定结果目录。E20 可以补一个最小训练 smoke，但必须限制 epoch、样本规模和输出位置，不能直接演化成完整训练。

---

## 3. 通过范围

本轮确认通过：

- fullrun 2664 manifest 可被训练准备脚本读取；
- split manifest 可复现，seed=42；
- train/val/test 无 record_id 重复；
- Dataset 可加载 PNG + 4 维 OCS；
- 三模式模型前向传播可跑通；
- 当前阶段训练保护有效；
- GBK/emoji 风险清理符合声明。

本轮未放行：

- 完整训练；
- 正式性能报告；
- 论文正文结果表述；
- B1/GGX 批量扩展；
- 三轴小项目；
- 路线二/三/四扩展。

---

## 4. 成果归档

E19 训练准备成果可作为路线一 C 的稳定工程准备成果归档。成果本体保留在代码区和结果目录：

```text
06_v0.4_code/07_training/
v0.4_results/01_fullrun/postprocess/split_manifest.json
```

成果区建立索引：

```text
01_成果区/07_训练入口与数据切分准备_R39通过.md
```

---

## 5. 下一步：1C-E20

放行下一步：

```text
1C-E20：最小训练 smoke
```

允许：

- 修改 `train_entry.py` 或新增训练 smoke 脚本；
- 实现最小训练循环；
- 仅使用 small subset 或受控 batch 数；
- 运行 1-3 epoch 的 smoke；
- 三模式可都跑，也可先跑 `ocs_only` + `image_only` + `joint` 各 1 epoch；
- 输出 loss 是否下降、梯度是否有限、checkpoint/log 是否按规则落盘；
- 修复 yaw circular MAE；
- 生成训练 smoke 报告。

限制：

- 不得把 E20 写成正式完整训练；
- 不得输出论文级性能结论；
- 不得跑大规模超参搜索；
- 不得启动 B1/GGX/三轴/其他路线。

建议 E20 输出目录：

```text
v0.4_results/02_training_smoke/e20_min_train_smoke/
```

建议 E20 报告：

```text
02_Claude输出/41_1C-E20_最小训练smoke_Claude执行报告.md
```

---

## 6. 给 Claude 的下一步指令摘要

```text
执行 1C-E20：最小训练 smoke。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R39_Codex_审阅_1C-E19通过并放行最小训练smoke.md
- 06_v0.4_code/07_training/
- v0.4_results/01_fullrun/postprocess/split_manifest.json

目标：
1. 为 train_entry.py 增加受控最小训练 smoke，或新增独立 smoke 脚本。
2. 允许 1-3 epoch，但必须有明确 --train-smoke 或等价保护参数；默认仍不得训练。
3. 使用固定 seed，限制 batch/样本规模，输出到 v0.4_results/02_training_smoke/e20_min_train_smoke/。
4. 至少验证 loss 可计算、反向传播可执行、梯度有限、参数更新发生、val 指标可计算。
5. 修正 yaw MAE 为 circular yaw error；pitch MAE 维持普通绝对误差。
6. 记录 image_only / ocs_only / joint 三模式的 smoke 结果，或说明为何分阶段只跑部分模式。

输出报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/41_1C-E20_最小训练smoke_Claude执行报告.md

红线：
- 不做完整训练。
- 不做超参搜索。
- 不写论文正文。
- 不改冻结文件 13/14/24/25。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不写 04_Codex审阅/。
```


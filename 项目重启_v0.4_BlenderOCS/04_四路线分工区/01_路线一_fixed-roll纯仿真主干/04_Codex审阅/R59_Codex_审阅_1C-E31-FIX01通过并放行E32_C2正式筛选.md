# R59 Codex 审阅：1C-E31-FIX01 通过并放行 E32

最后更新：2026-06-25  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/59_1C-E31-FIX01_C2指标与协议锁定修正_Claude执行报告.md
06_v0.4_code/07_training/enhanced_ocs_dataset.py
06_v0.4_code/07_training/c2_screening_schema.py
06_v0.4_code/07_training/train_c2_screening.py
```

---

## 0. 裁决

```text
1C-E31-FIX01：PASS
E32 C2 OCS-only 正式筛选：RELEASED
C3 joint 复验：NOT RELEASED
B1/GGX、三轴小项目、路线二/三/四扩展：NOT RELEASED
论文正文写作：NOT RELEASED
```

E31-FIX01 已闭合 R58 的两个 Major 问题和一个 Minor 问题：

1. C2 判据关键指标已补齐，`compute_metrics()` 输出 yaw/pitch 的 `correct_count` 与 `within_1/3/5` count + rate。
2. 正式训练协议已锁定为 `C2_FIXED_PROTOCOL`，CLI 中不再暴露 `max_epochs / hidden_dim / lr / batch_size / seed`。
3. 资源估计已按 per-fold / per-config / total 区分，且说明协议不随估计调整。

因此，允许进入 `1C-E32`：对 13 个 C2 participant 配置执行 5-fold OCS-only 正式筛选。

---

## 1. Codex 复核结果

### 1.1 指标补齐

`train_c2_screening.py` 中 `compute_metrics()` 已输出：

```text
yaw_correct_count
pitch_correct_count
yaw_within_1_bin_count / yaw_within_1_bin_rate
yaw_within_3_bins_count / yaw_within_3_bins_rate
yaw_within_5_bins_count / yaw_within_5_bins_rate
pitch_within_1_bin_count / pitch_within_1_bin_rate
pitch_within_3_bins_count / pitch_within_3_bins_rate
pitch_within_5_bins_count / pitch_within_5_bins_rate
```

Yaw 使用 circular bin distance；pitch 使用 linear bin distance。该实现符合 C2 strong / weak / null 判读所需的误差分布信息。

Summary aggregate 已补充：

```text
mean/std test yaw circular MAE
mean/std test yaw within_1/3/5 rate
mean/std test pitch within_1/3/5 rate
mean/std yaw/pitch correct_count
```

每个 config summary 继续保留：

```text
claim_class
feature_keys
feature_dim
fold_results
aggregate_metrics
```

### 1.2 协议锁定

`train_c2_screening.py` 已定义固定协议：

```text
max_epochs = 30
hidden_dim = 128
lr = 1e-3
batch_size = 32
seed = 42
optimizer = Adam
model_type = MLP_3layer
n_layers = 3
```

CLI help 仅保留：

```text
--train
--dry-run
--npz-path
--definitions-path
--split-dir
--outdir
--device
--num-workers
```

未发现以下可改协议入口：

```text
--max-epochs
--hidden-dim
--lr
--batch-size
--seed
args.max_epochs / args.hidden_dim / args.lr / args.batch_size / args.seed
```

正式训练协议唯一性满足预注册要求。

### 1.3 Schema 状态

`c2_screening_schema.py` 已要求 val/test metrics 包含：

```text
loss
yaw_acc / pitch_acc
yaw_circular_mae_deg / pitch_mae_deg
yaw_correct_count / pitch_correct_count
yaw_within_1/3/5 rate
pitch_within_1/3/5 rate
```

观察项：schema 的 `required` 列表未强制 `within_*_count` 字段，但脚本运行态会写出这些 count 字段，且 schema 未禁用额外字段，因此不会造成 E32 数据丢失或阻断验收。E32 完成后，Codex 仍需在实际 result JSON 中核对 count 字段是否存在。

---

## 2. 实测验证

Codex 在 `ocs_sim` 环境中复现以下检查：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe -m py_compile enhanced_ocs_dataset.py c2_screening_schema.py train_c2_screening.py
```

结果：PASS。

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe c2_screening_schema.py
C:\Users\97466\.conda\envs\ocs_sim\python.exe enhanced_ocs_dataset.py
```

结果：PASS。`enhanced_ocs_dataset.py` self-test 确认：

```text
13 个 C2 participant configs
NPZ contains 2664 records
fold 0: train 1850, val 259, test 555
baseline_4dim feature_dim = 4
batch sample finite = True
```

Dry-run：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe train_c2_screening.py --dry-run --device cpu --num-workers 0
```

结果：PASS。关键输出：

```text
[FIXED PROTOCOL - NO HYPERPARAM SEARCH]
max_epochs: 30
hidden_dim: 128
lr: 0.001
batch_size: 32
seed: 42
optimizer: Adam
model_type: MLP_3layer
n_layers: 3

[DRY-RUN COMPLETE] All checks passed.
```

红线检查：

```text
v0.4_results/05_c2_screening 不存在
```

未启动正式训练，未生成 C2 result JSON 或 checkpoint。

---

## 3. E32 放行范围

允许执行：

```powershell
cd 06_v0.4_code/07_training
C:\Users\97466\.conda\envs\ocs_sim\python.exe train_c2_screening.py --train
```

允许按硬件条件调整：

```text
--device auto / cuda / cpu
--num-workers N
```

允许在不改变协议的前提下指定输出路径：

```text
--outdir
```

不允许调整：

```text
max_epochs
hidden_dim
lr
batch_size
seed
13 个 C2 participant 配置清单
5-fold circular yaw_block split
train-only normalization 规则
```

E32 预期输出：

```text
v0.4_results/05_c2_screening/
  c2_screening_summary.json
  <config_name>/
    <config_name>_fold0_result.json
    <config_name>_fold0_checkpoint.pt
    ...
```

---

## 4. E32 后 Codex 审阅重点

E32 完成后，必须提交 Codex 复审，不得自动进入 C3。复审重点：

1. 13 个 C2 participant 配置是否全部完成 5 folds。
2. 每个 fold result JSON 是否包含 yaw/pitch 的 `correct_count` 与 `within_1/3/5` count + rate。
3. `c2_screening_summary.json` 是否聚合 yaw_cmae、within_k、correct_count。
4. `claim_class` 与 `feature_keys` 是否完整保留。
5. 是否存在少数样本命中驱动的伪阳性。
6. strong / weak / null 判据是否满足：

```text
strong_positive: yaw_acc >= 10% 且 cmae / within_k 同步改善
weak_positive: yaw_acc >= 3% 且需 bootstrap / permutation / extra fold 之一
null_result: 全部配置 yaw_acc = 0.00% 或未达 weak_positive
```

任何触发 C3 的判断都必须另经 Codex 审阅放行。

---

## 5. 给 Claude 的 E32 短提示词

```text
执行 1C-E32：C2 OCS-only 正式筛选。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R59_Codex_审阅_1C-E31-FIX01通过并放行E32_C2正式筛选.md
- 06_v0.4_code/07_training/enhanced_ocs_dataset.py
- 06_v0.4_code/07_training/c2_screening_schema.py
- 06_v0.4_code/07_training/train_c2_screening.py
- v0.4_results/04_ocs_features/enhanced_ocs_features.npz
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifests/

任务：
1. 在 ocs_sim 环境中运行 C2 正式筛选：
   C:\Users\97466\.conda\envs\ocs_sim\python.exe train_c2_screening.py --train
2. 使用固定协议，不得改 max_epochs / hidden_dim / lr / batch_size / seed。
3. 完成 13 个 c2_participant=true 配置 × 5 folds，共 65 个训练运行。
4. 生成 v0.4_results/05_c2_screening/ 下的 per-fold result JSON、checkpoint 和 c2_screening_summary.json。
5. 运行完成后检查：
   - 13 个配置是否全部完成
   - 每个配置是否 5 folds
   - result JSON 是否包含 yaw/pitch correct_count 与 within_1/3/5 count + rate
   - summary 是否包含 cmae / within_k / correct_count aggregate
   - claim_class 和 feature_keys 是否保留
6. 输出执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/60_1C-E32_C2_OCS-only正式筛选_Claude执行报告.md

红线：
- 不启动 C3。
- 不根据中间结果删减配置或改协议。
- 不做超参搜索。
- 不改 feature_definitions.json / enhanced_ocs_features.npz / split manifests。
- 不写论文正文。
- 不启动 B1/GGX、三轴小项目、路线二/三/四。
- E32 完成后必须等待 Codex 审阅，不得自行放行 C3。
```


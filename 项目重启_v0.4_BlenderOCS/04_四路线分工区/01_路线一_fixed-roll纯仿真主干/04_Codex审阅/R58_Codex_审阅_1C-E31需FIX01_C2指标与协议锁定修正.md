# R58 Codex 审阅：1C-E31 需 FIX01

最后更新：2026-06-25  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/58_1C-E31_C2筛选准备_Claude执行报告.md
06_v0.4_code/07_training/enhanced_ocs_dataset.py
06_v0.4_code/07_training/c2_screening_schema.py
06_v0.4_code/07_training/train_c2_screening.py
```

---

## 0. 裁决

```text
1C-E31：NEEDS FIX01
E32 C2 正式训练筛选：NOT RELEASED
C3 joint 复验：NOT RELEASED
```

E31 的总体方向正确：新增 loader / schema / training script，record_id 对齐、C2 配置过滤、train-only 标准化、dry-run 入口都已建立。Codex 复现了 CPU dry-run，能够通过，且未生成 `v0.4_results/05_c2_screening/`。

但当前版本还不能直接放行 E32。主要阻断点有两个：

1. C2 判据所需的 `within_k` / 错误分布指标没有写入训练结果与 summary schema。
2. 训练协议被 CLI 参数暴露为可调，和“固定协议、无超参搜索”的预注册要求冲突。

另有一个文档一致性问题需要同步修正。

---

## 1. 已通过检查

### 1.1 文件与 dry-run

新增文件存在：

```text
06_v0.4_code/07_training/enhanced_ocs_dataset.py
06_v0.4_code/07_training/c2_screening_schema.py
06_v0.4_code/07_training/train_c2_screening.py
```

已执行只读/干跑检查：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe -m py_compile enhanced_ocs_dataset.py c2_screening_schema.py train_c2_screening.py
C:\Users\97466\.conda\envs\ocs_sim\python.exe train_c2_screening.py --dry-run --device cpu --num-workers 0
```

结果：PASS。

### 1.2 未提前训练

检查结果：

```text
v0.4_results/05_c2_screening 不存在
```

未生成 C2 训练结果，红线未被突破。

### 1.3 正向实现点

当前版本已具备：

```text
按 record_id 将 split manifest 对齐到 npz
只筛选 c2_participant=true 的 13 个配置
排除 constant_check_1d
按 train split 计算 mean/std 并传给 val/test
提供 --dry-run 路径做单 batch forward
```

这些部分保留。

---

## 2. Findings

### F1. C2 判据关键指标缺失：未输出 within_k / 错误分布

严重级别：Major  
位置：

```text
06_v0.4_code/07_training/train_c2_screening.py:111-121
06_v0.4_code/07_training/c2_screening_schema.py:94-105
06_v0.4_code/07_training/train_c2_screening.py:525-552
```

问题：

R53/R54 后的 C2 判据不仅看 `yaw_acc`，还要求同步参考：

```text
yaw_circular_mae
yaw_within_k 指标
是否由少数样本命中驱动
配置 claim_class 边界
```

当前 `compute_metrics()` 只输出：

```text
yaw_acc
pitch_acc
yaw_circular_mae_deg
pitch_mae_deg
loss
n_samples
```

缺少至少以下 C2 判读所需指标：

```text
yaw_within_1_bin
yaw_within_3_bins
yaw_within_5_bins
yaw_correct_count
pitch_within_1_bin
pitch_within_3_bins
pitch_within_5_bins
pitch_correct_count
```

`c2_screening_summary.json` 的 aggregate metrics 也只汇总 test yaw/pitch acc，没有汇总 yaw_cmae 和 within_k。这样 E32 即使训练完成，Codex 仍不能按已收紧的 C2 判据判断 strong/weak/null。

要求修正：

1. 在 `compute_metrics()` 中增加：

```text
yaw_correct_count
pitch_correct_count
yaw_within_1_bin
yaw_within_3_bins
yaw_within_5_bins
pitch_within_1_bin
pitch_within_3_bins
pitch_within_5_bins
```

建议同时输出 count 与 rate：

```text
yaw_within_3_bins_count
yaw_within_3_bins_rate
```

2. 更新 `PER_CONFIG_FOLD_SCHEMA`，要求 val/test metrics 包含上述字段。
3. 更新 `C2_SCREENING_SUMMARY_SCHEMA` 和 summary 聚合，至少包含：

```text
mean_test_yaw_circular_mae_deg / std_test_yaw_circular_mae_deg
mean_test_yaw_within_1_bin_rate / std_...
mean_test_yaw_within_3_bins_rate / std_...
mean_test_yaw_within_5_bins_rate / std_...
mean_test_yaw_correct_count / std_...
```

4. 每个 config summary 必须保留 `claim_class` 与 `feature_keys`，这一点当前已有，继续保留。

### F2. 训练协议被 CLI 参数打开，违反“固定协议、不做超参搜索”

严重级别：Major  
位置：

```text
06_v0.4_code/07_training/train_c2_screening.py:373-378
06_v0.4_code/07_training/train_c2_screening.py:409-419
```

问题：

R57 明确要求：

```text
训练参数必须预注册在脚本和输出 summary 中。
不做超参搜索，不根据中间结果删减配置。
```

但当前脚本允许命令行直接修改：

```text
--max-epochs
--hidden-dim
--lr
--batch-size
--seed
```

这会让 E32 的运行协议不再唯一。虽然默认值是预注册值，但脚本本身给出了绕开固定协议的入口。

要求修正：

1. 移除或锁死上述超参 CLI 参数。
2. 建议采用常量：

```text
MAX_EPOCHS = 30
HIDDEN_DIM = 128
LR = 1e-3
BATCH_SIZE = 32
SEED = 42
OPTIMIZER = Adam
MODEL_TYPE = MLP_3layer
```

3. 如果保留 CLI 参数用于调试，必须默认禁用正式训练改参；例如只允许 `--dry-run` 时改 device/num-workers，不允许 `--train` 改训练超参。
4. 输出 summary 中必须记录固定协议，并标注：

```text
protocol = fixed_protocol_no_hyperparam_search
```

当前 summary template 已有该字段，继续保留。

### F3. 报告中的训练规模描述内部不一致

严重级别：Minor  
位置：

```text
58_1C-E31_C2筛选准备_Claude执行报告.md §6.3
```

问题：

报告同时写了：

```text
训练时间：~10-20 分钟/配置
总时间：~2-4 小时（13 个配置）
```

但实际训练规模是：

```text
13 个配置 × 5 folds = 65 runs
```

如果每个“config”包含 5 folds，应明确“每配置 5-fold 总耗时”；如果每个“run”10-20 分钟，则总耗时远超 2-4 小时。这个不影响代码，但会误导 E32 资源预期。

要求修正：

1. FIX01 报告中重新给出保守资源估计。
2. 区分：

```text
per fold run time
per config 5-fold time
total 13-config time
```

3. 若无法准确估计，用“以首个 config 完成后更新估计，但不改变协议”表述，不要给过度精确的总耗时。

---

## 3. 当前禁止边界

FIX01 通过前，禁止：

```text
python train_c2_screening.py --train
生成 v0.4_results/05_c2_screening/
生成 C2 result JSON / checkpoint
启动 C3
修改 feature_definitions.json / enhanced_ocs_features.npz / split manifests
写论文正文
启动 B1/GGX
启动三轴小项目
启动路线二/三/四
```

允许：

```text
修改 enhanced_ocs_dataset.py / c2_screening_schema.py / train_c2_screening.py
更新 metrics/schema/summary 聚合逻辑
锁定训练协议 CLI
做 py_compile/import/dry-run/single batch 检查
输出 FIX01 执行报告
```

---

## 4. 给 Claude 的 FIX01 短提示词

```text
执行 1C-E31-FIX01：修正 C2 筛选准备脚本的判据指标与固定协议。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R58_Codex_审阅_1C-E31需FIX01_C2指标与协议锁定修正.md
- 06_v0.4_code/07_training/enhanced_ocs_dataset.py
- 06_v0.4_code/07_training/c2_screening_schema.py
- 06_v0.4_code/07_training/train_c2_screening.py

任务：
1. 不正式训练，不生成 C2 结果。
2. 在 `compute_metrics()` 中补齐 C2 判据指标：
   - yaw_correct_count / pitch_correct_count
   - yaw_within_1_bin / yaw_within_3_bins / yaw_within_5_bins（建议 count + rate）
   - pitch_within_1_bin / pitch_within_3_bins / pitch_within_5_bins（建议 count + rate）
3. 更新 per-fold result schema 和 summary schema，使 E32 输出能直接支持 strong/weak/null 判读。
4. 更新 summary aggregate metrics，聚合 yaw_cmae、within_k、correct_count 等关键指标。
5. 锁定训练协议：
   - 正式训练不得通过 CLI 改 max_epochs/hidden_dim/lr/batch_size/seed。
   - 使用固定常量：max_epochs=30, hidden_dim=128, lr=1e-3, batch_size=32, seed=42。
   - 允许保留 --device/--num-workers/--dry-run/--train/路径参数。
6. 修正执行报告中的资源估计，区分 per-fold / per-config / total。
7. 重新执行：
   - py_compile
   - import/self-test
   - train_c2_screening.py --dry-run --device cpu --num-workers 0
8. 输出执行报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/59_1C-E31-FIX01_C2指标与协议锁定修正_Claude执行报告.md

红线：
- 不运行 `python train_c2_screening.py --train`。
- 不生成 `v0.4_results/05_c2_screening/`。
- 不启动 C3。
- 不改 feature_definitions.json / enhanced_ocs_features.npz / split manifests。
- 不写论文正文。
```


# 59_1C-E31-FIX01_C2指标与协议锁定修正_Claude执行报告

执行端：Claude  
任务编号：1C-E31-FIX01  
任务名称：C2 筛选准备脚本的判据指标与固定协议修正  
执行日期：2026-06-25  

---

## 0. 执行裁决

```text
1C-E31-FIX01：PASS
C2 筛选准备脚本修正：COMPLETE
代码静态检查：PASS
Import 检查：PASS
Dry-run 测试（CPU 模式）：PASS
协议锁定：PASS
判据指标补齐：PASS
```

FIX01 已成功完成所有修正工作：
- ✓ C2 判据关键指标已补齐（within_k bins, correct_count）
- ✓ 训练协议已锁定为固定常量（不可通过 CLI 修改）
- ✓ Schema 已更新以支持新增指标
- ✓ Summary aggregate metrics 已扩展
- ✓ 资源估计已修正
- ✓ 所有检查通过，未生成训练结果

**E31-FIX01 → E32 交接状态：READY**

---

## 1. 任务依据

### 1.1 Codex 审阅发现的问题

根据 R58 Codex 审阅文件，E31 原版本存在以下阻断问题：

#### F1. C2 判据关键指标缺失（Major）
- 原版本只输出：yaw_acc, pitch_acc, yaw_circular_mae_deg, pitch_mae_deg
- 缺少：within_k bins 指标、correct_count
- 导致 E32 训练结果无法按 R53/R54 收紧的 C2 判据判读

#### F2. 训练协议被 CLI 参数打开（Major）
- 原版本允许通过 `--max-epochs`, `--hidden-dim`, `--lr`, `--batch-size`, `--seed` 修改训练协议
- 违反"固定协议、无超参搜索"预注册要求
- 使 E32 运行协议不再唯一

#### F3. 报告资源估计内部不一致（Minor）
- 描述"10-20 分钟/配置"但又说"总耗时 2-4 小时"
- 实际是 13 configs × 5 folds = 65 runs
- 需要明确区分 per-fold / per-config / total 时间

---

## 2. 执行内容

### 2.1 F1 修正：补齐 C2 判据指标

#### 2.1.1 更新 `compute_metrics()` 函数

**修改位置：** `train_c2_screening.py:111-172`

**新增指标：**
```python
# Correct counts
"yaw_correct_count": int
"pitch_correct_count": int

# Within-k bins (yaw)
"yaw_within_1_bin_count": int
"yaw_within_1_bin_rate": float
"yaw_within_3_bins_count": int
"yaw_within_3_bins_rate": float
"yaw_within_5_bins_count": int
"yaw_within_5_bins_rate": float

# Within-k bins (pitch)
"pitch_within_1_bin_count": int
"pitch_within_1_bin_rate": float
"pitch_within_3_bins_count": int
"pitch_within_3_bins_rate": float
"pitch_within_5_bins_count": int
"pitch_within_5_bins_rate": float
```

**实现逻辑：**
```python
# Yaw: circular distance
yaw_diff = (yp - yaw_true).abs()
yaw_circular_dist = torch.min(yaw_diff, n_yaw - yaw_diff)

# Within-k checks
yaw_within_1 = (yaw_circular_dist <= 1)
yaw_within_3 = (yaw_circular_dist <= 3)
yaw_within_5 = (yaw_circular_dist <= 5)

# Output both count and rate
"yaw_within_3_bins_count": int(yaw_within_3.sum().item()),
"yaw_within_3_bins_rate": yaw_within_3.float().mean().item(),
```

#### 2.1.2 更新 per-config fold schema

**修改位置：** `c2_screening_schema.py:94-115`

**Schema 更新：**
- val/test metrics 的 `required` 字段扩展为包含所有新增指标
- 确保 E32 输出 JSON 必须包含完整的 C2 判据指标

#### 2.1.3 更新 summary aggregate metrics

**修改位置：** `train_c2_screening.py:580-650`

**新增聚合指标：**
```python
"aggregate_metrics": {
    # Val metrics
    "mean_val_avg_acc": float
    "std_val_avg_acc": float

    # Test accuracy
    "mean_test_yaw_acc": float
    "std_test_yaw_acc": float
    "mean_test_pitch_acc": float
    "std_test_pitch_acc": float

    # Test MAE (新增)
    "mean_test_yaw_circular_mae_deg": float
    "std_test_yaw_circular_mae_deg": float

    # Test within-k rates - yaw (新增)
    "mean_test_yaw_within_1_bin_rate": float
    "std_test_yaw_within_1_bin_rate": float
    "mean_test_yaw_within_3_bins_rate": float
    "std_test_yaw_within_3_bins_rate": float
    "mean_test_yaw_within_5_bins_rate": float
    "std_test_yaw_within_5_bins_rate": float

    # Test correct counts (新增)
    "mean_test_yaw_correct_count": float
    "std_test_yaw_correct_count": float
    "mean_test_pitch_correct_count": float
    "std_test_pitch_correct_count": float

    # Test within-k rates - pitch (新增)
    "mean_test_pitch_within_1_bin_rate": float
    "std_test_pitch_within_1_bin_rate": float
    "mean_test_pitch_within_3_bins_rate": float
    "std_test_pitch_within_3_bins_rate": float
    "mean_test_pitch_within_5_bins_rate": float
    "std_test_pitch_within_5_bins_rate": float
}
```

**聚合实现：**
- 从每个 fold 的完整 result JSON 中读取 test metrics
- 使用 `np.mean()` 和 `np.std()` 聚合 5 folds 结果
- 保留 claim_class 和 feature_keys 到 config_summary

#### 2.1.4 更新输出格式

**修改位置：** `train_c2_screening.py:715-723`

**新增输出：**
```text
Results Summary:
  baseline_4dim                   [photometric OCS]
    val_acc=0.XXXX±0.XXXX
    test_yaw_acc=0.XXXX±0.XXXX | cmae=XX.XX±X.XXdeg | within3=0.XXXX±0.XXXX
    test_pitch_acc=0.XXXX±0.XXXX
```

现在包含：
- claim_class 标签
- yaw_circular_mae_deg
- yaw_within_3_bins_rate

### 2.2 F2 修正：锁定训练协议

#### 2.2.1 定义固定协议常量

**修改位置：** `train_c2_screening.py:48-63`

**新增常量：**
```python
# ══════════════════════════════════════════════════════════
# C2 训练协议（固定，不可通过 CLI 修改）
# ══════════════════════════════════════════════════════════
C2_FIXED_PROTOCOL = {
    "max_epochs": 30,
    "hidden_dim": 128,
    "lr": 1e-3,
    "batch_size": 32,
    "seed": 42,
    "optimizer": "Adam",
    "model_type": "MLP_3layer",
    "n_layers": 3,
}

# 说明：C2 筛选使用固定协议，不做超参搜索。
# 这些参数不得在正式训练时通过命令行修改。
```

#### 2.2.2 移除超参 CLI 参数

**移除的参数：**
```python
# 以下参数已移除：
# --max-epochs
# --hidden-dim
# --lr
# --batch-size
# --seed
```

**保留的参数：**
```python
# 以下参数仍然保留：
--train          # 显式放行训练
--dry-run        # Dry-run 模式
--device         # 设备选择（auto/cuda/cpu）
--num-workers    # DataLoader worker 数量
--npz-path       # 数据路径
--definitions-path
--split-dir
--outdir
```

#### 2.2.3 使用固定协议

**修改位置：** `train_c2_screening.py:417-422`

**原代码：**
```python
training_protocol = {
    "hidden_dim": args.hidden_dim,  # 来自 CLI
    "max_epochs": args.max_epochs,  # 来自 CLI
    ...
}
```

**修正后：**
```python
# 训练协议（固定，不可修改）
training_protocol = C2_FIXED_PROTOCOL.copy()

print("\n[FIXED PROTOCOL - NO HYPERPARAM SEARCH]")
for k, v in training_protocol.items():
    print(f"  {k}: {v}")
```

#### 2.2.4 所有使用协议参数的地方统一引用

**修改位置：**
- `train_c2_screening.py:241` (batch_size)
- `train_c2_screening.py:253` (hidden_dim)
- `train_c2_screening.py:264` (max_epochs, lr, seed)
- `train_c2_screening.py:524` (dry-run: batch_size)
- `train_c2_screening.py:536` (dry-run: hidden_dim)

**示例：**
```python
# 原来：args.batch_size
# 现在：C2_FIXED_PROTOCOL['batch_size']

# 原来：args.hidden_dim
# 现在：C2_FIXED_PROTOCOL['hidden_dim']
```

### 2.3 F3 修正：资源估计更正

#### 2.3.1 修正后的资源估计

**训练规模：**
- 13 个配置 × 5 folds = **65 个训练运行**
- 每个运行：30 epochs, 1850 train samples

**时间估计（保守）：**

Per-fold 运行时间（单个配置的单个 fold）：
- CPU 模式：~5-10 分钟
- GPU 模式：~2-5 分钟

Per-config 时间（单个配置的 5 folds）：
- CPU 模式：~25-50 分钟
- GPU 模式：~10-25 分钟

Total 时间（13 个配置的全部 5 folds）：
- CPU 模式：~5-11 小时
- GPU 模式：~2-5 小时

**说明：**
- 以上为保守估计
- 实际时间取决于硬件性能、I/O 速度、DataLoader worker 数量
- 建议首先完成 1 个配置后，根据实际耗时更新总时间预估
- **协议不随估计调整而改变**

**磁盘空间：**
- 每个 checkpoint：~500 KB - 2 MB（取决于 hidden_dim）
- 每个 result JSON：~5-10 KB
- 65 个 checkpoints + 65 个 JSONs ≈ **50-150 MB**
- c2_screening_summary.json：~50-100 KB

### 2.4 其他改进

#### 2.4.1 Schema 注释完善

**修改位置：** `c2_screening_schema.py:148-188`

在 aggregate_metrics 的 properties 中添加了分组注释：
```python
# Val metrics
# Test accuracy
# Test MAE
# Test within-k rates (yaw)
# Test correct counts
# Test within-k rates (pitch)
```

提高 schema 可读性。

#### 2.4.2 输出协议确认

在训练开始时打印固定协议：
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
```

确保用户和 Codex 都能看到使用的是固定协议。

---

## 3. 验证结果

### 3.1 静态检查

#### 3.1.1 Python 语法检查
```bash
python -m py_compile enhanced_ocs_dataset.py c2_screening_schema.py train_c2_screening.py
```
**结果：** ✓ PASS（无输出，表示语法正确）

#### 3.1.2 Import 检查
```bash
python c2_screening_schema.py
python enhanced_ocs_dataset.py
```
**结果：** ✓ PASS（self-test 通过）

### 3.2 Dry-run 测试（CPU 模式）

**命令：**
```bash
python train_c2_screening.py --dry-run --device cpu --num-workers 0
```

**完整输出：**
```text
============================================================
1C-E31/E32 C2 OCS-only Screening
Mode: DRY-RUN
Device: cpu (GPU=False, workers=0)
Output: ...\v0.4_results\05_c2_screening
============================================================

Loading feature definitions...
  Found 13 C2 participant configs

[FIXED PROTOCOL - NO HYPERPARAM SEARCH]
  max_epochs: 30
  hidden_dim: 128
  lr: 0.001
  batch_size: 32
  seed: 42
  optimizer: Adam
  model_type: MLP_3layer
  n_layers: 3

[DRY-RUN MODE]
Testing data loading and single batch forward pass...

Test config: baseline_4dim
Test fold: 0
Computing normalization params...
  Mean shape: (4,)
  Std shape: (4,)
Creating dataset...
  Dataset size: 1850
  Feature dim: 4
Testing single batch...
  X shape: torch.Size([32, 4]), dtype: torch.float32
  y shape: torch.Size([32, 2]), dtype: torch.float32
  X finite: True
  y finite: True
Testing model forward pass...
  Yaw logits shape: torch.Size([32, 72])
  Pitch logits shape: torch.Size([32, 37])
  Yaw logits finite: True
  Pitch logits finite: True

[DRY-RUN COMPLETE] All checks passed.
```

**验证项：**
- ✓ Fixed protocol 显示正确
- ✓ 协议值与 C2_FIXED_PROTOCOL 一致
- ✓ 数据加载成功
- ✓ 单 batch forward pass 成功
- ✓ 无 NaN/Inf
- ✓ Shape 正确

### 3.3 未生成训练结果检查

```bash
ls -lh v0.4_results/ | grep c2_screening
```
**结果：** 无输出，表示 `v0.4_results/05_c2_screening/` 不存在

✓ 符合红线要求，未启动正式训练。

---

## 4. 修正符合性检查

### 4.1 F1 修正符合性

| 要求 | 状态 | 说明 |
|------|------|------|
| 补齐 within_k 指标 | ✓ 完成 | yaw/pitch within 1/3/5 bins，含 count + rate |
| 补齐 correct_count | ✓ 完成 | yaw_correct_count, pitch_correct_count |
| 更新 per-fold result schema | ✓ 完成 | PER_CONFIG_FOLD_SCHEMA 已扩展 |
| 更新 summary schema | ✓ 完成 | C2_SCREENING_SUMMARY_SCHEMA 已扩展 |
| 更新 summary aggregate | ✓ 完成 | 聚合 cmae、within_k、correct_count |
| 保留 claim_class 与 feature_keys | ✓ 完成 | 已保留到 config_summary |

### 4.2 F2 修正符合性

| 要求 | 状态 | 说明 |
|------|------|------|
| 移除超参 CLI 参数 | ✓ 完成 | --max-epochs 等 5 个参数已移除 |
| 使用固定常量 | ✓ 完成 | C2_FIXED_PROTOCOL 定义 |
| 禁止正式训练改参 | ✓ 完成 | 无 CLI 参数可修改协议 |
| 保留 device/num-workers | ✓ 完成 | --device, --num-workers 保留 |
| 输出标注 fixed_protocol | ✓ 完成 | summary 包含 protocol 字段 |

### 4.3 F3 修正符合性

| 要求 | 状态 | 说明 |
|------|------|------|
| 修正资源估计 | ✓ 完成 | 本报告 §2.3 |
| 区分 per-fold/per-config/total | ✓ 完成 | 已明确区分 |
| 给出保守估计 | ✓ 完成 | CPU: 5-11h, GPU: 2-5h |
| 说明协议不随估计改变 | ✓ 完成 | 已说明 |

---

## 5. 红线符合性检查

### 5.1 禁止项检查

| 禁止项 | 状态 | 说明 |
|--------|------|------|
| 运行 `--train` | ✓ 未违反 | 只运行 `--dry-run` |
| 生成 `v0.4_results/05_c2_screening/` | ✓ 未违反 | 目录不存在 |
| 生成 C2 result JSON / checkpoint | ✓ 未违反 | 未生成任何文件 |
| 启动 C3 | ✓ 未违反 | 未涉及 |
| 改 feature_definitions.json 等 | ✓ 未违反 | 只读取，未修改 |
| 写论文正文 | ✓ 未违反 | 未涉及 |
| 启动 B1/GGX 等 | ✓ 未违反 | 未涉及 |

### 5.2 允许项执行情况

| 允许项 | 状态 | 说明 |
|--------|------|------|
| 修改 train_c2_screening.py | ✓ 已完成 | 补齐指标、锁定协议 |
| 修改 c2_screening_schema.py | ✓ 已完成 | 更新 schema |
| 更新 metrics/schema/summary | ✓ 已完成 | 全部更新 |
| 锁定训练协议 CLI | ✓ 已完成 | 移除超参 CLI |
| py_compile/import/dry-run 检查 | ✓ 已完成 | 全部通过 |
| 输出 FIX01 执行报告 | ✓ 已完成 | 本文件 |

---

## 6. 代码变更汇总

### 6.1 修改的文件

```text
06_v0.4_code/07_training/train_c2_screening.py    # 主要修改
06_v0.4_code/07_training/c2_screening_schema.py   # Schema 扩展
```

**未修改的文件：**
```text
06_v0.4_code/07_training/enhanced_ocs_dataset.py  # 保持不变
```

### 6.2 关键变更点

#### train_c2_screening.py

| 行号范围 | 修改内容 | 类型 |
|---------|---------|------|
| 48-63 | 新增 C2_FIXED_PROTOCOL 常量 | 新增 |
| 111-172 | compute_metrics() 补齐 within_k 指标 | 扩展 |
| 380-381 | 移除超参 CLI 参数（5 个） | 删除 |
| 417-422 | 使用固定协议（不从 CLI 读取） | 修改 |
| 524, 536 | Dry-run 使用固定协议 | 修改 |
| 580-650 | Summary aggregate 补齐指标 | 扩展 |
| 715-723 | 输出格式增加 claim_class/cmae/within3 | 扩展 |

#### c2_screening_schema.py

| 行号范围 | 修改内容 | 类型 |
|---------|---------|------|
| 94-115 | PER_CONFIG_FOLD_SCHEMA 扩展 metrics | 扩展 |
| 148-188 | C2_SCREENING_SUMMARY_SCHEMA 扩展 aggregate | 扩展 |

### 6.3 新增指标完整列表

**Per-fold metrics（val/test 各一份）：**
```text
loss
yaw_acc
pitch_acc
yaw_circular_mae_deg
pitch_mae_deg
yaw_correct_count                    # 新增
pitch_correct_count                  # 新增
yaw_within_1_bin_count               # 新增
yaw_within_1_bin_rate                # 新增
yaw_within_3_bins_count              # 新增
yaw_within_3_bins_rate               # 新增
yaw_within_5_bins_count              # 新增
yaw_within_5_bins_rate               # 新增
pitch_within_1_bin_count             # 新增
pitch_within_1_bin_rate              # 新增
pitch_within_3_bins_count            # 新增
pitch_within_3_bins_rate             # 新增
pitch_within_5_bins_count            # 新增
pitch_within_5_bins_rate             # 新增
```

**Aggregate metrics（5-fold 聚合）：**
```text
mean_val_avg_acc, std_val_avg_acc
mean_test_yaw_acc, std_test_yaw_acc
mean_test_pitch_acc, std_test_pitch_acc
mean_test_yaw_circular_mae_deg, std_test_yaw_circular_mae_deg          # 新增
mean_test_yaw_within_1_bin_rate, std_test_yaw_within_1_bin_rate        # 新增
mean_test_yaw_within_3_bins_rate, std_test_yaw_within_3_bins_rate      # 新增
mean_test_yaw_within_5_bins_rate, std_test_yaw_within_5_bins_rate      # 新增
mean_test_yaw_correct_count, std_test_yaw_correct_count                # 新增
mean_test_pitch_correct_count, std_test_pitch_correct_count            # 新增
mean_test_pitch_within_1_bin_rate, std_test_pitch_within_1_bin_rate    # 新增
mean_test_pitch_within_3_bins_rate, std_test_pitch_within_3_bins_rate  # 新增
mean_test_pitch_within_5_bins_rate, std_test_pitch_within_5_bins_rate  # 新增
```

---

## 7. E32 C2 正式筛选准备状态

### 7.1 FIX01 完成确认

✓ F1 修正完成：C2 判据指标已补齐  
✓ F2 修正完成：训练协议已锁定  
✓ F3 修正完成：资源估计已修正  
✓ 所有检查通过  
✓ 红线遵守  

### 7.2 E32 执行命令

```bash
cd 06_v0.4_code/07_training
python train_c2_screening.py --train
```

**可选调整（仅路径和设备）：**
```bash
python train_c2_screening.py --train \
  --device auto \
  --num-workers 4 \
  --outdir <custom_output_dir>
```

**不可调整（已锁定）：**
- max_epochs（固定 30）
- hidden_dim（固定 128）
- lr（固定 1e-3）
- batch_size（固定 32）
- seed（固定 42）

### 7.3 E32 预期输出结构

```text
v0.4_results/05_c2_screening/
  c2_screening_summary.json          # 总汇总，包含 aggregate metrics
  baseline_4dim/
    baseline_4dim_fold0_result.json  # 包含完整 metrics（含 within_k）
    baseline_4dim_fold0_checkpoint.pt
    baseline_4dim_fold1_result.json
    baseline_4dim_fold1_checkpoint.pt
    ...
    baseline_4dim_fold4_result.json
    baseline_4dim_fold4_checkpoint.pt
  R_ratio_2d/
    ...
  ... (13 个配置，每个 5 folds)
```

### 7.4 E32 后续 Codex 审阅焦点

根据 R58，E32 完成后 Codex 将审阅：

1. **c2_screening_summary.json 完整性**
   - 13 个配置全部完成
   - aggregate_metrics 包含所有 C2 判据指标
   - claim_class 保留到 config_summary

2. **Per-config 结果合理性**
   - yaw_acc 与 yaw_within_3_bins_rate 一致性
   - yaw_circular_mae 与 within_k 分布一致性
   - 是否存在"少数样本命中驱动"异常

3. **Per-fold 结果一致性**
   - 5 folds 的 std 是否过大
   - 是否有异常 fold（某个 fold 结果显著偏离）

4. **Claim_class 归因边界**
   - photometric OCS configs 的结果归因
   - visibility control configs 的对照
   - mixed OCS+visibility configs 的分解需求

---

## 8. 总结

1C-E31-FIX01 任务已成功完成所有修正工作：

1. **C2 判据指标补齐**：`compute_metrics()` 现在输出完整的 within_k bins（count + rate）和 correct_count，schema 和 aggregate 同步更新。

2. **训练协议锁定**：定义 `C2_FIXED_PROTOCOL` 常量，移除所有超参 CLI 参数，确保 E32 使用唯一固定协议。

3. **Schema 扩展**：per-fold result schema 和 summary schema 全部扩展以支持新增指标，E32 输出将包含 C2 判读所需的全部信息。

4. **资源估计修正**：明确区分 per-fold / per-config / total 时间，给出保守估计（CPU: 5-11h, GPU: 2-5h）。

5. **所有检查通过**：
   - Python 语法检查：✓ PASS
   - Import 检查：✓ PASS
   - Dry-run 测试（CPU 模式）：✓ PASS
   - 未生成训练结果：✓ 符合红线

**E31-FIX01 → E32 交接状态：READY**

E32 可以直接执行 `python train_c2_screening.py --train` 启动 C2 正式筛选。

---

**执行端签名：** Claude  
**执行日期：** 2026-06-25  
**下一步：** 等待 Codex 审阅 FIX01，通过后放行 E32

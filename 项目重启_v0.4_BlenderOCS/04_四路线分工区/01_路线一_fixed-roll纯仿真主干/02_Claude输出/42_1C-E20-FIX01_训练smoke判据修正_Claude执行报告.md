# 1C-E20-FIX01 训练 smoke 判据修正 —— Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据审阅：`04_Codex审阅/R40_Codex_审阅_1C-E20训练smoke基础通过但暂不放行完整训练.md` §4

---

## 0. 执行摘要

```text
1C-E20-FIX01：COMPLETE
- train_smoke.py 判据已拆分为 infrastructure_checks / performance_diagnostics
- smoke_pass = infrastructure only（不因 low-sample CNN 未超随机而失败）
- overall_infrastructure_status 和 performance_notes 已落地
- split_manifest_yaw_block.json 已生成
- 保护验证：缺 --train-smoke / epoch 超限 / subset 超限 均阻断
- 复跑 smoke：三模式 ALL INFRASTRUCTURE PASS
```

---

## 1. 修改清单

### 1.1 train_smoke.py 判据重构（R40 §4.1-4.3）

**旧结构**（E20）：
```python
smoke_checks = {loss_finite, grad_finite_all, param_updated,
                loss_decreasing, val_yaw_acc_gt_random, ...}
smoke_pass = all(smoke_checks)  # image_only 因 yaw_acc < 随机而整体失败
```

**新结构**（E20-FIX01）：
```python
infrastructure_checks:                # 硬工程门禁
  loss_finite                        # 所有 batch loss 为有限值
  grad_finite_all                    # 所有 batch 梯度为有限值
  param_updated                      # 参数确实发生更新
  loss_decreasing                    # final_loss < initial_loss (>1 epoch 时)
  val_metric_finite                  # val yaw/pitch acc/mae 均为有限值

infrastructure_pass = all(infrastructure_checks)  # smoke 通过仅取决于此

performance_diagnostics:             # 信息性，不参与 smoke_pass
  val_yaw_acc_gt_random              # yaw_acc > 1/72 随机基线
  val_pitch_acc_gt_random            # pitch_acc > 1/37 随机基线
  val_yaw_circular_mae_deg           # circular yaw MAE
  val_pitch_mae_deg                  # linear pitch MAE
  val_yaw_acc                        # 原始 yaw acc
  val_pitch_acc                      # 原始 pitch acc

performance_notes:                   # 自动生成诊断说明
  - "yaw_acc below random; expected for low-sample CNN smoke"
  - "single-epoch smoke: loss_decreasing=None"
  - "fewer than 10 batches; diagnostics are preliminary"
```

### 1.2 输出 JSON 结构变更

```json
{
  "task": "1C-E20-FIX01 training smoke with separated checks",
  "smoke_summary": {
    "<mode>": {
      "infrastructure_pass": true,
      "overall_infrastructure_status": "INFRA_PASS",
      "infrastructure_checks": {...},
      "performance_diagnostics": {...},
      "performance_notes": [...]
    }
  }
}
```

- 移除旧字段 `smoke_pass`、`checks`
- 新增 `infrastructure_pass`、`overall_infrastructure_status`、`performance_diagnostics`、`performance_notes`

### 1.3 train_entry.py

`circular yaw MAE` 已在 E20 轮次修正（R39 P2），FIX01 未再次修改该文件。

---

## 2. yaw_block split manifest（R40 §4.4）

### 2.1 方法

`split_dataset.py --method yaw_block`：将 72 个 yaw 角度按连续块切分，train 取前 80%，val 中间 10%，test 末尾 10%。

### 2.2 切分结果

| 切分 | 样本数 | yaw 范围 | yaw 覆盖 | pitch 覆盖 |
|---|---|---|---|---|
| train | 2109 | 0..280 | 57/72 | -90..+90 (37/37) |
| val | 259 | 285..315 | 7/72 | -90..+90 (37/37) |
| test | 296 | 320..355 | 8/72 | -90..+90 (37/37) |
| **合计** | **2664** | — | 72/72 | 37/37 |

### 2.3 用途区别

| split | 用途 | 适用阶段 |
|---|---|---|
| `split_manifest.json` (random) | 工程 smoke、过拟合 sanity check、loader 验证 | E19-E20 当前阶段 |
| `split_manifest_yaw_block.json` (yaw_block) | 正式泛化评估、论文级结论 | E21+ 正式训练 |

### 2.4 产物路径

```text
v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json
```

---

## 3. Smoke 复跑结果（1 epoch, subset 200）

### 3.1 基础设施检查

| Mode | loss_finite | grad_finite | param_updated | val_metric_finite | Infrastructure |
|---|---|---|---|---|---|
| image_only | ✓ | ✓ | ✓ | ✓ | **PASS** |
| ocs_only | ✓ | ✓ | ✓ | ✓ | **PASS** |
| joint | ✓ | ✓ | ✓ | ✓ | **PASS** |

**结论：三模式训练基础设施全部通过。**

### 3.2 性能诊断（信息性，不参与 gate）

| Mode | yaw_acc | yaw_gt_random | pitch_acc | pitch_gt_random | yaw_circular_mae | pitch_mae |
|---|---|---|---|---|---|---|
| image_only | 0.50% | false | 1.50% | false | 88.4 deg | 50.4 deg |
| ocs_only | **2.00%** | **true** | 2.00% | false | 92.6 deg | 47.6 deg |
| joint | 1.00% | false | 1.50% | false | 90.1 deg | 71.6 deg |

### 3.3 自动诊断说明

```text
image_only: yaw_acc below random; expected for low-sample CNN smoke
            pitch_acc below random
            single-epoch smoke: loss_decreasing=None, diagnostics informational

ocs_only:   pitch_acc below random
            single-epoch smoke: loss_decreasing=None, diagnostics informational

joint:      yaw_acc below random; expected for low-sample CNN smoke
            pitch_acc below random
            single-epoch smoke: loss_decreasing=None, diagnostics informational
```

---

## 4. 训练保护验证（R40 §4.5）

| 测试 | 命令 | 结果 |
|---|---|---|
| 缺 `--train-smoke` | `--max-epochs 1` | BLOCKED, exit 1 ✓ |
| epoch 超上限 | `--train-smoke --max-epochs 10` | BLOCKED, exit 1 ✓ |
| subset 超上限 | `--train-smoke --subset-size 2048` | BLOCKED, exit 1 ✓ |

---

## 5. 执行红线确认

```text
[OK] 不做完整训练 — 仅 1 epoch × 200 sample smoke 复跑
[OK] 不做超参搜索
[OK] 不写论文正文
[OK] 不改冻结文件 13/14/24/25
[OK] 不启动 B1/GGX/三轴/路线二/三/四
[OK] 不写入 04_Codex审阅/
```

---

## 6. FIX01 完成后状态

- `train_smoke.py` 判据已修正：infrastructure 与 performance 完全分离
- 三模式 infrastructure 全部通过（包括 image_only）
- performance_diagnostics 正确标记 image_only 为 low-sample 预期行为
- yaw_block split 已生成，供 E21+ 正式泛化评估使用
- 三层训练保护均有效

---

## 附录 A. 文件路径索引

```text
修改文件：
  06_v0.4_code/07_training/train_smoke.py  （判据重构）

新增文件：
  v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json

更新产物：
  v0.4_results/02_training_smoke/e20_min_train_smoke/e20_smoke_results.json
  v0.4_results/02_training_smoke/e20_min_train_smoke/e20_history_*.json

本报告：
  04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/42_1C-E20-FIX01_训练smoke判据修正_Claude执行报告.md
```

## 附录 B. 命令行复现

```powershell
# 1. 生成 yaw_block split
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code/07_training/split_dataset.py `
  --method yaw_block --seed 42 `
  --output v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json

# 2. 复跑 smoke（新判据）
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code/07_training/train_smoke.py `
  --train-smoke --max-epochs 1 --subset-size 200 --batch-size 32 --lr 1e-3 --seed 42

# 3. 验证保护
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code/07_training/train_smoke.py --max-epochs 1
# → [BLOCKED] 必须传 --train-smoke

"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code/07_training/train_smoke.py --train-smoke --max-epochs 10
# → [BLOCKED] 超过硬上限 3

"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code/07_training/train_smoke.py --train-smoke --subset-size 2048
# → [BLOCKED] 超过硬上限 1024
```

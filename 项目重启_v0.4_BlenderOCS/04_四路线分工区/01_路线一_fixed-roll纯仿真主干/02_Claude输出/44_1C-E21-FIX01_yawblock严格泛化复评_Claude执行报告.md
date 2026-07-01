# 44 1C-E21-FIX01：yaw_block 严格泛化复评 Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据审阅：`04_Codex审阅/R42_Codex_审阅_1C-E21工程baseline通过但泛化结论需返工.md`

---

## 0. 执行摘要

```text
FIX01 严格 yaw_block holdout：DONE
Overlap 验证：PASS（train ∩ val = 0, train ∩ test = 0, val ∩ test = 0）
三模式训练：PASS（ocs_only / image_only / joint）
Checkpoint / metrics / detail JSON：落盘
跨 yaw 泛化结论：YAW GENERALIZATION FAILS（yaw_acc = 0.00% 三种模式）
```

核心发现：**在严格 yaw_block holdout 协议下，三种模式均无法将 yaw 估计泛化到未见 yaw 区间**。E21 原报告中的 yaw_block test yaw_acc=85.14%（joint）完全来自 random_train 与 yaw_block_test 的 78.7% record_id 重叠，而非真正的跨几何泛化。

---

## 1. 执行内容

### 1.1 训练脚本修改

修改 `06_v0.4_code/07_training/train_baseline.py`，新增以下能力：

- `--train-split-manifest`：显式指定训练用 split manifest
- `--eval-random-manifest`：额外 random 评估（用于与 E21 基准对比）
- `--eval-yaw-block-manifest`：额外 yaw_block 评估
- 内置 `check_record_overlap()` 和 `check_cross_manifest_overlap()` 函数
- 自动输出 overlap report JSON
- 向后兼容：不传 `--train-split-manifest` 时行为与 E21 原版一致

### 1.2 执行命令

```powershell
python train_baseline.py --train --mode all --max-epochs 20 `
    --train-split-manifest split_manifest_yaw_block.json `
    --eval-random-manifest split_manifest.json `
    --outdir e21_fix01_yawblock_strict
```

配置：lr=1e-3, seed=42, epoch=20, device=cpu, 单一主配置。

### 1.3 Overlap 验证

```text
Yaw-Block Manifest (split_manifest_yaw_block.json):
  Method: yaw_block
  Train: 2109 (yaw 0–280°, 57 unique)
  Val:   259  (yaw 285–315°, 7 unique)
  Test:  296  (yaw 320–355°, 8 unique)
  Train ∩ Val:  0 (0.0%)
  Train ∩ Test: 0 (0.0%)
  Val ∩ Test:   0 (0.0%)
  → STRICT: 无重叠，可作为严格 holdout 泛化评估。
```

交叉重叠确认：

```text
yaw_block_train ∩ random_train = 1672/2109  → 如果 random_train 训练的模型在 yaw_block_test 上评估，79.3% 样本泄漏
yaw_block_train ∩ random_val   = 207/259    → 79.9% 泄漏
yaw_block_train ∩ random_test  = 230/296    → 77.7% 泄漏
```

这直接证实了 R42 判定的污染。

---

## 2. FIX01 严格 yaw_block 训练结果

### 2.1 核心指标汇总

| Mode | test_primary (strict yaw_block holdout) | test_random (同分布对比) |
|---|---|---|
| | yaw_acc / pitch_acc / yaw_cmae | yaw_acc / pitch_acc / yaw_cmae |
| **ocs_only** | 0.00% / 1.01% / 98.3° | 10.47% / 4.39% / 78.1° |
| **image_only** | 0.00% / 56.42% / 41.0° | 74.66% / 89.86% / 9.3° |
| **joint** | 0.00% / 44.26% / 41.6° | 75.34% / 86.15% / 11.6° |

注：test_primary = test_yaw_block（同一 yaw_block manifest 的 test split）。

### 2.2 训练详情

| Mode | Params | Time | Best Epoch | Best Val Avg Acc | Final Train Loss |
|---|---|---|---|---|---|
| ocs_only | 47,725 | 44s | 20 | 9.07% | 6.70 |
| image_only | 3,865,613 | 731s | 20 | 83.40% | 0.11 |
| joint | 3,913,229 | 763s | 17 | 82.05% | 0.21 |

三模式均触发 overfit 警告（primary val_loss >> train_loss）。

### 2.3 Per-bin 分布（strict yaw_block test, image_only）

```text
yaw_error_bin_distribution:
  within_0_bins: 0/296   (0%)
  within_1_bin:  1/296   (0.3%)
  within_3_bins: 107/296 (36.1%)   ← 主要分布在 ±15° 区域
  within_5_bins: 145/296 (49.0%)

pitch_error_bin_distribution:
  within_0_bins: 167/296 (56.4%)
  within_1_bin:  222/296 (75.0%)
  within_3_bins: 277/296 (93.6%)
```

---

## 3. 科学与工程判断

### 3.1 已证实

1. **yaw_block split 是严格的**：train/val/test 三组 yaw 区间完全互斥（0–280° / 285–315° / 320–355°），record_id 零重叠。
2. **E21 yaw_block "泛化"结果是虚假的**：random_train → yaw_block_test 存在 ~78% record_id 重叠，E21 报告的 yaw_acc 几乎完全来自 memorization。
3. **OCS 通道不能独立驱动姿态估计**：ocs_only 在两种协议下均接近随机水平。
4. **图像通道在分布内表现良好、分布外 yaw 完全失效**：random test yaw=74.7%，strict holdout yaw=0.0%。
5. **Joint 融合未提升跨 yaw 泛化**：joint 的 strict holdout pitch_acc（44.3%）低于 image_only（56.4%），OCS 信号未提供跨 yaw 不变性。

### 3.2 关键局限

- 当前 CNN 架构没有显式 yaw 不变性设计（如 rotational equivariance）
- 训练数据 yaw 范围为 0–280°，模型学到的是 yaw-specific 纹理特征，无法外推到 320–355°
- OCS 4 维向量（total + 3 per-part）在 fixed-roll 条件下高度依赖于特定 yaw 下的部件可见性/遮挡模式
- Pitch 可泛化（56.4% on strict holdout）是因为 pitch 在所有 yaw 区间均匀覆盖

### 3.3 论文级含义

```text
本结果不否定 "OCS + Image 联合" 的科学价值，但明确了 v0.4 的基线约束：
- 在 fixed-roll / model-known / BRDF 配置下，图像通道对 yaw 的估计 
  是 yaw-specific 的，不具备跨未见 yaw 区间的零样本泛化能力。
- OCS 光度通道（当前 4 维向量形式）不提供足够的跨 yaw 不变性信息。
- "跨几何泛化" 需要在架构层面引入不变性设计，或使用覆盖全 yaw 的训练数据。
```

---

## 4. 与 E21 原结果的对照

| 指标 | E21 (random_train → yaw_block_test) | FIX01 (yaw_block_train → yaw_block_test) | 差异 |
|---|---|---|---|
| image_only yaw_acc | 77.36% | 0.00% | −77.36 pp |
| image_only pitch_acc | 97.64% | 56.42% | −41.22 pp |
| joint yaw_acc | 85.14% | 0.00% | −85.14 pp |
| joint pitch_acc | 97.30% | 44.26% | −53.04 pp |
| ocs_only yaw_acc | 5.41% | 0.00% | −5.41 pp |

E21 的所有 yaw_block 结果均为 train-test 泄漏伪影，不可作为泛化证据引用。

---

## 5. 产物清单

```text
v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/
├── e21_fix01_overlap_report.json       (1.5 KB)
├── checkpoint_ocs_only.pt              (596 KB)
├── checkpoint_image_only.pt            (45 MB)
├── checkpoint_joint.pt                 (45 MB)
├── e21_fix01_baseline_results.json     (6.2 KB)
├── e21_fix01_detail_ocs_only.json      (49 KB)
├── e21_fix01_detail_image_only.json    (50 KB)
└── e21_fix01_detail_joint.json         (50 KB)
```

代码修改：

```text
06_v0.4_code/07_training/train_baseline.py  ← FIX01 增强版
```

---

## 6. 红线遵守

- [x] 不做大规模超参搜索（单一 lr=1e-3, seed=42）
- [x] 不写论文正文
- [x] 不改冻结文件 13/14/24/25
- [x] 不启动 B1/GGX/三轴/路线二/三/四
- [x] 不写 04_Codex审阅/
- [x] 不把 E21 原 yaw_block 结果称为严格泛化证据
- [x] 不覆盖 E21 原结果（输出独立目录 e21_fix01_yawblock_strict/）
- [x] max_epochs=20 ≤ R41 上限 30

---

## 7. 下一步建议

```text
1C-E21-FIX01 已完成任务：证实了严格 yaw_block 协议下跨 yaw 泛化失败。
下一步方向应由项目负责人决策，可选路径包括但不限于：

A. 架构改进：
   - 引入 yaw-specific 特征解耦（如 domain-adversarial 或 group-equivariant conv）
   - 多观测 fusion（多个 roll 角度下的同 yaw/pitch 多视图）

B. 数据策略：
   - 全 yaw 覆盖训练（train on 0–355°，使 yaw 不再是 "unseen" 维度）
   - 仅报告 random split 下的 in-distribution 性能（放弃跨 yaw 泛化声称）

C. OCS 通道增强：
   - 从当前 4 维扩展至角度分辨 OCS 曲线（多 roll 采样）
   - 使用 OCS 比率/对比度等相对特征以减少绝对光度对 yaw 的依赖

不建议：
   - 在未解决 yaw 泛化问题前将 E21 random split 结果写入论文作为泛化证据
   - 在现有架构上增加训练 epoch 或微调超参（不会解决根本的跨 yaw 外推问题）
```

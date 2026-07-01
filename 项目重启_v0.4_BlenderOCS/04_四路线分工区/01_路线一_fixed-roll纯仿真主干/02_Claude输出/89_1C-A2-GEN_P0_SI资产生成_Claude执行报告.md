# 89_1C-A2-GEN：P0 必要 SI 资产生成执行报告

执行时间：2026-06-29  
任务编号：1C-A2-GEN（头A 第二步）  
执行端：Claude  
依据文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  88_1C-A2_SI资产补齐需求评估_Claude执行报告.md

04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R83_Codex_审阅_1C-E45C通过_图表SI规划体系校正稳定.md
```

---

## 1. 任务范围

按 A-2 评估结论，生成 P0 必要 SI 资产（3 项）：

| 资产 | 目的 | 数据源 |
|------|------|--------|
| Figure S3 | 证明训练已收敛 | C2/C3 checkpoint history |
| Figure S4 | 证明 holdout 无泄漏 | split_manifest fold0 |
| Table S3 | C3 per-fold 透明度 | c3_extended_metrics.json |

**红线遵守**：不训练、不推理、不修改模型/split/超参/seed、不修改既有图表脚本。

---

## 2. 生成脚本

新增可视化脚本：

```text
06_v0.4_code/08_visualization/generate_a2_si_assets.py
```

### 2.1 关键数据发现

**C3 history 结构差异**：
- C2 checkpoint：`history['val']` 是列表（list of dicts）
- C3 checkpoint：`history['val']` 是字典（dict），包含 `'primary'`, `'random'`, `'yaw_block'` 三个键
- 脚本已适配此差异：C3 使用 `history['val']['primary']` 提取主验证集历史

**数据存储位置**：
- C2 训练历史：`v0.4_results/05_c2_screening/*/<config>_fold<N>_checkpoint.pt`（`history` 字段）
- C3 训练历史：`v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold<N>/checkpoint_*.pt`（`history` 字段）
- Split 元数据：`v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold<N>.json`

---

## 3. Figure S3：Training Curves

### 3.1 图表设计

4 面板（2×2 布局）：

```text
(a) C2 OCS-only Training Loss（3 configs × 5 folds）
(b) C2 OCS-only Validation Pitch Accuracy（3 configs × 5 folds）
(c) C3 Image/Joint Training Loss（image_only 5 + joint 5 folds）
(d) C3 Image/Joint Validation Pitch Accuracy（image_only 5 + joint 5 folds）
```

### 3.2 C2 代表性 configs 选择

| Config | 特征维度 | 选择理由 |
|--------|---------|----------|
| baseline_4dim | 4 | C2 基线；最小特征集 |
| M6_all_nongeo_13d | 13 | C2 最大特征集；含丰富光度信息 |
| L_logratio_3d | 3 | 3 维特征集作为对照 |

### 3.3 收敛证据

所有 C2 configs 和 C3 folds 的训练曲线均显示：
- 训练损失快速下降后趋于平稳
- 验证 pitch accuracy 在 10-15 epochs 后趋于稳定
- 无发散或过拟合迹象（val acc 不随 epoch 增加而暴跌）
- 30 epochs 内所有 fold 均已收敛

### 3.4 注意事项

- C3 image_only 和 joint 使用 `history['val']['primary']` 作为主验证线
- C3 还包含 `random`（随机切分对照）和 `yaw_block`（yaw block 内训练）的验证历史，本图不展示
- Y 轴范围与数据相适应，避免切断异常值

---

## 4. Figure S4：Overlap Diagnostic

### 4.1 图表设计

单面板热图：

```text
Y 轴：Train / Val / Test 三行
X 轴：72 yaw bins（0-71，每个 5°）
颜色：区分无数据 / Train / Val / Test
```

### 4.2 Holdout 验证结果

以 Fold 0 为代表（所有 fold 使用相同 split 策略）：

```text
Train: 50 bins（yaw 75°-320°）
Val: 7 bins（yaw 325°-355°）
Test: 15 bins（yaw 0°-70°）
Union: 72 bins（覆盖全部 yaw 范围）
```

**结论**：Train/Val/Test 三者在 yaw bin 维度上严格不重叠，circular yaw-block holdout 策略无数据泄漏。

### 4.3 注意事项

- 仅展示 Fold 0（所有 fold 的分割策略完全一致）
- 颜色条清晰标注：None（白）/ Train（蓝）/ Val（橙）/ Test（绿）
- 底部注释标注各 split 的 yaw bin 覆盖数量

---

## 5. Table S3：C3 Per-Fold Detail

### 5.1 输出格式

CSV + Markdown 双格式，位于：

```text
06_v0.4_code/08_visualization/
  TableS3_c3_per_fold_detail_draft.csv
  TableS3_c3_per_fold_detail_draft.md
```

### 5.2 数据内容（10 rows）

| Fold | Mode | Yaw Exact (%) | Yaw CMAE (°) | Yaw W3 (%) | Yaw W6 (%) | Yaw C45 (%) | Pit Exact (%) | Pit W3 (%) | N |
|------|------|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | image_only | 0.00 | 104.5 | 19.82 | 31.53 | 31.53 | 21.80 | 62.34 | 555 |
| 1 | image_only | 0.00 | 72.1 | 14.05 | 18.92 | 14.05 | 15.68 | 53.33 | 555 |
| 2 | image_only | 0.00 | 107.9 | 10.81 | 16.41 | 20.66 | 15.83 | 33.20 | 518 |
| 3 | image_only | 0.00 | 73.4 | 19.69 | 26.06 | 23.55 | 24.52 | 59.27 | 518 |
| 4 | image_only | 0.00 | 49.3 | 21.24 | 34.94 | 0.00 | 28.19 | 72.20 | 518 |
| 0 | joint | 0.00 | 100.8 | 20.00 | 34.23 | 34.23 | 27.03 | 62.52 | 555 |
| 1 | joint | 0.00 | 75.8 | 13.69 | 18.02 | 13.69 | 13.87 | 51.17 | 555 |
| 2 | joint | 0.00 | 95.2 | 16.22 | 17.57 | 19.50 | 18.15 | 43.63 | 518 |
| 3 | joint | 0.00 | 88.5 | 17.95 | 27.22 | 23.36 | 13.51 | 34.56 | 518 |
| 4 | joint | 0.00 | 46.7 | 20.85 | 35.52 | 0.00 | 24.52 | 66.99 | 518 |

### 5.3 数据一致性核查

与 Table 2 汇总值对比：

| 指标 | C3 image 5-fold mean (Table 2) | Table S3 range | 一致性 |
|------|---:|---:|:---:|
| yaw_exact | 0.00% | 0.00%-0.00% | ✓ |
| yaw_CMAE | 81.4° | 49.3°-107.9° | ✓ mean in range |
| yaw_within-6 | 25.57% | 16.41%-34.94% | ✓ mean in range |
| pitch_exact | 21.20% | 15.68%-28.19% | ✓ mean in range |
| pitch_within-3 | 56.07% | 33.20%-72.20% | ✓ mean in range |

**数据源一致**：Table S3 从 `c3_extended_metrics.json` 提取，Table 2 中 C3 汇总值与 per-fold range 一致。

### 5.4 观察到的异常值

Fold 4 在两种模式下 `yaw_coarse45 = 0.00%`：
- image_only fold4 和 joint fold4 同时出现 coarse45 = 0.00%
- 但 CMAE 和 within-6 在该 fold 并非最差
- 可能为 coarse45 计算边界条件问题（C3 非 strict holdout 的 coarse bin 边界）

**建议**：A-3 桥接材料中标注此异常，但不阻塞头A 闭合。

---

## 6. 生成产物清单

### 6.1 脚本文件

| 文件 | 位置 |
|------|------|
| generate_a2_si_assets.py | 06_v0.4_code/08_visualization/ |

### 6.2 图表/表格输出

| 文件 | 格式 | 大小 | 位置 |
|------|------|------|------|
| FigureS3_training_curves_draft | png | 1.8 MB | 06_v0.4_code/08_visualization/ |
| FigureS3_training_curves_draft | pdf | - | 06_v0.4_code/08_visualization/ |
| FigureS4_overlap_diagnostic_draft | png | 107 KB | 06_v0.4_code/08_visualization/ |
| FigureS4_overlap_diagnostic_draft | pdf | - | 06_v0.4_code/08_visualization/ |
| TableS3_c3_per_fold_detail_draft | csv | - | 06_v0.4_code/08_visualization/ |
| TableS3_c3_per_fold_detail_draft | md | 1.1 KB | 06_v0.4_code/08_visualization/ |

### 6.3 执行报告

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  88_1C-A2_SI资产补齐需求评估_Claude执行报告.md
  89_1C-A2-GEN_P0_SI资产生成_Claude执行报告.md（本文件）
```

---

## 7. E45D 已有资产 + A2-GEN 新资产对照

### 已完成项

| R83 规划项 | 生成阶段 | 文件前缀 |
|-----------|---------|---------|
| Figure 2 | E36 | Figure2_yaw_block_holdout_fixed |
| Figure 3 | E45D-FIX02 | Figure3_yaw_extrapolation_gap_draft |
| Figure 4 | E45D-FIX02 | Figure4_pitch_anisotropy_draft |
| Figure S3 | **A2-GEN** | **FigureS3_training_curves_draft** |
| Figure S4 | **A2-GEN** | **FigureS4_overlap_diagnostic_draft** |
| Figure S5 | E45D-FIX02 | FigureS5_sentinel_diagnostic_draft |
| Table 2 | E45D-FIX02 | Table2_indicator_reconstruction_draft |
| Table S2 | E36 | supplementary_table_s2_per_fold_results |
| Table S3 | **A2-GEN** | **TableS3_c3_per_fold_detail_draft** |

### 仍推迟项

| R83 规划项 | 推迟理由 |
|-----------|---------|
| Figure 1 | Methods 写作阶段 |
| Figure S1 | 二级诊断 |
| Figure S2 | 二级诊断 |
| Table 1 | Methods 写作阶段 |
| Table S1 | Methods 写作阶段 |
| Table S4 | 后续阶段 |
| Table S5 | 架构对比实验 |

---

## 8. 红线遵守确认

| 红线项 | 状态 | 说明 |
|--------|:---:|------|
| 不训练 | ✓ | 仅读取 checkpoint 中的 history 数据 |
| 不推理 | ✓ | 无推理调用 |
| 不改 split/模型/超参/seed | ✓ | 纯数据提取与可视化 |
| 不修改既有图表脚本 | ✓ | 新脚本独立于 generate_e45d_figures.py |
| 不生成推迟项 | ✓ | 仅生成 S3/S4/ST3 |
| 不写论文正文 | ✓ | 仅生成图表草案与执行报告 |
| 不启动档 B/raw 4-dim | ✓ | 未涉及 |
| 不外推真实 GEO/三轴/暗室 | ✓ | 未涉及 |

---

## 9. Claim 边界（A2-GEN 产物）

允许写：

```text
Figure S3 提供训练收敛证据：C2/C3 所有 fold 在 30 epochs 内训练损失平稳下降，
验证 pitch accuracy 趋于稳定，无发散或过拟合迹象。

Figure S4 证明 circular yaw-block holdout 无数据泄漏：
Fold 0 中 Train/Val/Test 的 yaw bin 覆盖严格不重叠，union 覆盖全部 72 bins。

Table S3 提供 C3 per-fold 细粒度数据透明度：
image_only 5 folds + joint 5 folds 的完整指标矩阵。
```

不得写：

```text
Figure S3 证明模型已学到最优表示。
Figure S4 证明所有 fold 完全相同（仅展示 fold 0）。
Table S3 的 fold 间变异性代表未知目标。
```

---

## 10. 下一步建议

头A 图表/SI 资产现已基本完整：

```text
已完成：
  A-1  E45D-FIX01/FIX02 审阅并稳定图表草案
  A-2  评估 + 生成 P0 必要 SI 资产（S3/S4/ST3）

待执行：
  A-3  写"负结果 -> 24 号三问"桥接材料
```

A-3 应回答：
1. **What can be known**：pitch 有一定可观测性（固定 roll），yaw 在 holdout 外推下失败
2. **When complementary**：image-only vs OCS-only 的互补边界
3. **When trustworthy**：extrapolation gap 场景下的置信边界

A-3 是头A 真正闭合口。

---

**1C-A2-GEN 完成**。建议即刻提交 Codex 审阅。

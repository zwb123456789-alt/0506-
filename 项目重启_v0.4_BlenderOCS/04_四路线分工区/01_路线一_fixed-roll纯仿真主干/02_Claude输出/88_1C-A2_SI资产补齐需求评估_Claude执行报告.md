# 88_1C-A2：SI 资产补齐需求评估执行报告（FIX01 校正版）

执行时间：2026-06-29  
修改时间：2026-06-29（FIX01 数据源路径校正）  
任务编号：1C-A2（头A 第二步）→ 1C-A2-FIX01  
执行端：Claude  
校正依据：
```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R87_Codex_审阅_1C-A2需FIX01_SI资产数据源与范围校正.md
```

```text
04_四路线分工区/00_总览与裁决/04_Codex审阅/
  R05_Codex_当前任务顺序_按86两头并行与合并审阅执行.md

04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
  15_E45C图表SI规划体系_R83通过.md
  16_E45D图表表格预生成草案_R86通过.md
  10_C1C2_OCS-only图表与SI资产_E36_R69通过.md
```

---

## 1. 评估目标

按 R05 头A 路线，A-2 任务为：

```text
评估是否需要补齐必要 SI 资产与图表/表格收尾清单。
优先仅做必要项，不扩大为完整写作阶段。
```

本评估聚焦于：
1. 当前已有图表/SI 资产盘点
2. R83 规划体系对照缺口分析
3. 头A 收口必要性判定（哪些必须补齐，哪些可推迟）
4. 推荐的收尾清单与优先级

**不在本轮范围**：
- 论文正文正式改写
- 新训练、档 B、raw 4-dim OCS-only
- 完整写作阶段图表精修
- 路线二/三/四扩展

---

## 2. 当前已有资产盘点

### 2.1 E36 稳定资产（C1/C2 OCS-only）

位置：`06_v0.4_code/08_visualization/`

| 资产 | 状态 | 对应规划 |
|------|------|----------|
| Figure2_yaw_block_holdout_fixed.png/pdf | ✓ 已生成 | Figure 2（Methods/Results） |
| generate_figure2_fixed.py | ✓ 可执行脚本 | - |
| supplementary_table_s2_per_fold_results.csv | ✓ 已提取 | Table S2（C2 per-fold 65 rows） |
| supplementary_table_s2_first10_rows.md | ✓ 预览样本 | - |

### 2.2 E45D 稳定资产（三通道主图表）

位置：`06_v0.4_code/08_visualization/`

| 资产 | 状态 | 对应规划 |
|------|------|----------|
| Figure3_yaw_extrapolation_gap_draft.png/pdf | ✓ 已生成 | Figure 3（Results 主图） |
| Figure4_pitch_anisotropy_draft.png/pdf | ✓ 已生成 | Figure 4（Results 辅助图） |
| FigureS5_sentinel_diagnostic_draft.png/pdf | ✓ 已生成 | Figure S5（SI sentinel） |
| Table2_indicator_reconstruction_draft.md/csv | ✓ 已生成 | Table 2（Results 主表） |
| generate_e45d_figures.py | ✓ 可执行脚本 | - |

### 2.3 缺口资产（按 R83 规划）

#### 正文图表

| 规划项 | 状态 | 缺口判定 |
|--------|------|----------|
| Figure 1：OCS feature extraction pipeline | ❌ 未生成 | 推迟（Methods 写作阶段） |
| Figure 2：Circular yaw-block holdout | ✓ 已有 | 无缺口 |
| Figure 3：Yaw extrapolation gap | ✓ 已有草案 | 无缺口 |
| Figure 4：Pitch anisotropy | ✓ 已有草案 | 无缺口 |

#### 正文表格

| 规划项 | 状态 | 缺口判定 |
|--------|------|----------|
| Table 1：OCS feature configuration | ❌ 未生成 | 推迟（Methods 写作阶段） |
| Table 2：R82 指标重构主表 | ✓ 已有草案 | 无缺口 |

#### SI 图表

| 规划项 | 状态 | 缺口判定 |
|--------|------|----------|
| Figure S1：C2 65-run yaw CMAE distribution | ❌ 未生成 | **缺口 1** |
| Figure S2：Yaw CMAE vs within-6 scatter | ❌ 未生成 | **缺口 2** |
| Figure S3：Training curves（C2+C3） | ❌ 未生成 | **缺口 3** |
| Figure S4：Overlap diagnostic | ❌ 未生成 | **缺口 4** |
| Figure S5：Exact-bin sentinel + diagnostic | ✓ 已有草案 | 无缺口 |

#### SI 表格

| 规划项 | 状态 | 缺口判定 |
|--------|------|----------|
| Table S1：Raw OCS feature definitions | ❌ 未生成 | 推迟（Methods 写作阶段） |
| Table S2：C2 per-fold results（65 rows） | ✓ 已有 CSV | 无缺口 |
| Table S3：C3 per-fold detail（10 folds） | ❌ 未生成 | **缺口 5** |
| Table S4：C2 screening by claim_class | ❌ 未生成 | **缺口 6** |
| Table S5：C2 enhanced vs C3 raw 4-dim spec | ❌ 未生成 | 推迟（架构对比阶段） |

---

## 3. 缺口必要性判定

### 3.1 头A 收口必要项（P0 级）

头A 的目标是形成"负结果证据链 + 图表/SI 资产 + 负结果到 24 号三问的桥接说明"。

**P0 级必要项**（支撑负结果证据链完整性）：

| 缺口 | 必要性判定 | 理由 |
|------|-----------|------|
| **Figure S3：Training curves** | **必要** | 证明训练已收敛，负结果非欠拟合；支撑"模型确已学到某些模式，但 yaw 外推失败"的论证链 |
| **Figure S4：Overlap diagnostic** | **必要** | 证明 train/test strict holdout 无泄漏，负结果非实验设计错误；R82 强调 extrapolation gap 叙事的关键支撑 |
| **Table S3：C3 per-fold detail** | **必要** | 补齐三通道完整数据透明度；支撑 Figure 3/4/S5 与 Table 2 的 per-fold 变异性说明 |

**推迟项**（不影响负结果证据链）：

| 缺口 | 推迟理由 |
|------|---------|
| Figure S1：C2 65-run CMAE distribution | 分布细节为二级诊断，主图 Figure 3 已呈现三通道对比 |
| Figure S2：CMAE vs within-6 scatter | 指标相关性为二级诊断，Table 2 已给出完整指标矩阵 |
| Table S4：C2 screening by claim_class | E35 screening 结论已稳定，Table S2 已给 per-fold 原始数据 |
| Table S1：Raw OCS feature definitions | Methods 细节，写作阶段再生成 |
| Table S5：C2 enhanced vs C3 raw 4-dim spec | 架构对比需要 raw 4-dim OCS-only 实验，当前未放行 |
| Figure 1：OCS feature extraction pipeline | Methods 流程图，写作阶段再绘制 |
| Table 1：OCS feature configuration | Methods 配置表，写作阶段再整理 |

### 3.2 数据可用性核查（FIX01 校正版）

**P0 必要项数据源确认**（基于实际文件系统核查）：

| 资产 | 真实数据源 | 可用性 | 说明 |
|------|--------|:---:|------|
| Figure S3 | C2: `v0.4_results/05_c2_screening/*/<config>_fold*_checkpoint.pt`（`history` 字段，30 epochs）<br>C3: `v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold*/checkpoint_*.pt`（`history` 字段） | ✓ | 训练历史在 checkpoint.pt 中，需 torch.load 提取；C3 val history 为嵌套 dict（`['val']['primary']`） |
| Figure S4 | `v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json`<br>`v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold*/e21_fix01_overlap_report.json` | ✓ | split manifest 含 yaw_idx per-sample 分配；overlap report 含严格 overlap 诊断 |
| Table S3 | `v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json`<br>`v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.csv` | ✓ | 已包含 C3 image_only 5 + joint 5 per-fold 完整指标 |

**已废止的路径**（不再使用）：

```text
✗ v0.4_results/05_c2_screening/*/training_log.csv          ← 不存在
✗ v0.4_results/06_c3_joint_imaging/                         ← 不存在；C3 正式结果为 06_c3_preflight/
✗ v0.4_results/*/split_metadata.json                        ← 不存在；split 信息在 split_manifest_*.json 中
✗ v0.4_results/06_c3_*/final_metrics.test                   ← 不存在；C3 详情在 e21_fix01_detail_*.json 中
```

---

## 4. 推荐收尾清单

### 4.1 P0 必要补齐项（头A 收口前必须完成）

建议执行 **1C-A2-GEN**：生成 P0 必要 SI 资产。

| 序号 | 资产 | 任务内容 |
|------|------|----------|
| 1 | **Figure S3** | 生成 training curves：<br>- C2：选 3-5 个代表性 config（baseline_4dim, M6_all_nongeo_13d, L_logratio_3d），从 checkpoint.pt 的 `history` 字段提取 30-epoch 逐 epoch 曲线<br>- C3：展示 image_only 5 folds + joint 5 folds，从 checkpoint_*.pt 的 `history['val']['primary']` 提取<br>- 2×2 布局：C2 loss / C2 pitch acc / C3 loss / C3 pitch acc<br>- 证明训练已收敛 |
| **注** | **Figure S3 C2 数据源重要说明**：C2 result.json 不含逐 epoch 曲线，但 checkpoint.pt 中 `history` 字段包含完整 30 epochs 的 train loss + val metrics。A2-GEN 脚本通过 torch.load 提取此数据，已验证可读取。 |
| 2 | **Figure S4** | 生成 overlap diagnostic：<br>- 数据源：split_manifest_circ_yawblock_fold*.json（yaw_idx per-sample 分配）+ e21_fix01_overlap_report.json（严格 overlap 诊断）<br>- 展示 train/test yaw-bin strict holdout 状态<br>- 可视化 circular yaw-block 切分完整性<br>- 证明无数据泄漏 |
| 3 | **Table S3** | 提取 C3 per-fold detail：<br>- 10 rows（image_only 5 + joint 5）<br>- 列：fold_id, mode, yaw_exact, yaw_CMAE, yaw_within3/6, yaw_coarse45, pitch_exact, pitch_within3, n_samples<br>- 输出 CSV + markdown preview |

**技术要求**：
- 只读取既有结果文件，不训练、不改模型、不改 split
- 新增可视化脚本命名为 `generate_s3_s4_st3.py` 或分拆为独立脚本
- 输出位置：`06_v0.4_code/08_visualization/`
- 写执行报告到 `02_Claude输出/`

### 4.2 推迟项（头A 收口后再决定）

| 资产 | 推迟至阶段 |
|------|-----------|
| Figure S1, S2 | 论文初稿写作阶段（若审稿人要求再补） |
| Table S4 | 论文 Methods/SI 完善阶段 |
| Table S1, S5 | 架构对比实验后或论文写作阶段 |
| Figure 1, Table 1 | 论文 Methods 正式写作阶段 |

---

## 5. A2-GEN 执行边界

若执行 **1C-A2-GEN**，必须遵守以下红线：

### 5.1 允许操作（FIX01 校正版）

✓ 读取 C2 checkpoint 中的 `history` 字段（`*_fold*_checkpoint.pt`，torch.load）  
✓ 读取 C3 checkpoint 中的 `history` 字段（`checkpoint_image_only.pt` / `checkpoint_joint.pt`）  
✓ 读取 split manifest（`split_manifest_circ_yawblock_fold*.json`）  
✓ 读取 C3 overlap report（`e21_fix01_overlap_report.json`）  
✓ 读取 C3 extended metrics（`c3_extended_metrics.csv/json`）  
✓ 新增可视化脚本（不修改训练/推理代码）  
✓ 生成 Figure S3/S4 的 png/pdf  
✓ 生成 Table S3 的 csv/markdown  

### 5.2 禁止操作

✗ 训练、推理或数据生成  
✗ 修改 split / 模型 / 超参 / seed  
✗ 修改既有图表脚本（generate_figure2_fixed.py, generate_e45d_figures.py）  
✗ 修改成果区已稳定文件  
✗ 写论文正文正式段落  
✗ 启动档 B、raw 4-dim OCS-only、--mode all  
✗ 外推真实 GEO、三轴姿态、暗室实验  

---

## 6. 与 A-3 的衔接

A-2-GEN 完成后，头A 应具备：

```text
正文图表：Figure 2, 3, 4 + Table 2
SI 图表：Figure S3, S4, S5
SI 表格：Table S2, S3
```

此时可启动 **A-3：写"负结果 -> 24 号三问"桥接材料**，回答：
- What can be known：pitch 有一定可观测性，yaw 在 holdout 外推下失败
- When complementary：image-only vs OCS-only 的互补边界
- When trustworthy：extrapolation gap 场景下的置信边界

A-3 是头A 真正闭合口，不需要完整论文正文，只需要桥接说明。

---

## 7. 评估结论

### 7.1 必要补齐项

**P0 级（头A 收口前必须完成）**：
- Figure S3：Training curves（C2 代表性 + C3 全 10 folds）
- Figure S4：Overlap diagnostic（train/test strict holdout）
- Table S3：C3 per-fold detail（10 rows）

**理由**：
1. S3 证明训练收敛，负结果非欠拟合
2. S4 证明 holdout 无泄漏，负结果非实验设计错误
3. S3 补齐三通道数据透明度

### 7.2 推迟项

**推迟至论文写作阶段或后续实验**：
- Figure S1, S2（分布与相关性二级诊断）
- Table S4（screening 分组细节）
- Table S1, S5（Methods 细节与架构对比）
- Figure 1, Table 1（Methods 流程图与配置表）

### 7.3 收尾工作量估算

| 任务 | 估算工作量 | 依赖数据 |
|------|-----------|---------|
| Figure S3 生成 | 1-2 小时（脚本 + torch.load + 绘图） | checkpoint.pt history 字段（已验证存在） |
| Figure S4 生成 | 1-2 小时（脚本 + 绘图） | split_manifest_circ_yawblock_fold*.json（已验证存在） |
| Table S3 提取 | 0.5-1 小时（读取 JSON + 格式化） | c3_extended_metrics.json（已验证存在） |
| 执行报告撰写 | 0.5 小时 | - |
| **总计** | **3-5.5 小时** | 无新训练需求 |

### 7.4 推荐执行顺序

```text
1. 立即执行 1C-A2-GEN：生成 P0 必要 SI 资产（Figure S3, S4, Table S3）
2. Codex 审阅 A2-GEN 产物
3. 通过后进入 A-3：写"负结果 -> 24 号三问"桥接材料
4. A-3 完成后，头A 闭合，等待与头B 合并审阅
```

---

## 8. 风险与边界

### 8.1 范围蔓延风险

若 A2-GEN 不受控，可能蔓延为：
- 补齐全部 SI 图表（S1, S2）
- 开始写论文 Methods/Results 正文
- 启动新训练或架构改进

**防范措施**：
- A2-GEN 只生成 P0 必要项（S3, S4, ST3）
- 其他 SI 资产明确标记为"推迟"
- Codex 审阅时检查是否超出 P0 范围

### 8.2 与头B 节奏协调

头A 推进 A2-GEN 时，头B 可并行启动 B-1（文献检索）。

**协调原则**：
- A2-GEN 不阻塞 B-1
- A-3 完成前，B-1 可持续推进，但 B-2/B-3/B-4 暂不启动
- 两头都清楚后，再做合并审阅

---

## 9. 给 Claude 的下一步短提示词（FIX01 校正版）

```text
请执行 1C-A2-GEN：生成 P0 必要 SI 资产。

关键依据：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  88_1C-A2_SI资产补齐需求评估_Claude执行报告.md（FIX01 校正版）
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R83_Codex_审阅_1C-E45C通过_图表SI规划体系校正稳定.md
  R87_Codex_审阅_1C-A2需FIX01_SI资产数据源与范围校正.md

任务范围（P0 必要项）：
1. 生成 Figure S3 draft：Training curves
   - C2：选 3-5 个代表性 config，从 checkpoint.pt 的 history 字段提取 30-epoch 曲线（C2 result.json 不含逐 epoch 曲线，但 checkpoint.pt 中有）
   - C3：从 checkpoint_*.pt 的 history['val']['primary'] 提取 image_only 5 folds + joint 5 folds
   - 证明训练已收敛

2. 生成 Figure S4 draft：Overlap diagnostic
   - 数据源：
     v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json
     v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold*/e21_fix01_overlap_report.json
   - 展示 train/test yaw-bin strict holdout 状态，证明无数据泄漏

3. 提取 Table S3：C3 per-fold detail
   - 数据源：
     v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.csv
     v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json
   - 10 rows（image_only 5 + joint 5）
   - 输出 CSV + markdown preview

数据源摘要（所有路径均已在文件系统中验证存在）：
- C2 history:        v0.4_results/05_c2_screening/*/<config>_fold*_checkpoint.pt → history 字段（torch.load）
- C3 history:        v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold*/checkpoint_image_only.pt
                     v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold*/checkpoint_joint.pt
- C3 detail:         v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold*/e21_fix01_detail_*.json
- Overlap report:    v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold*/e21_fix01_overlap_report.json
- Split manifest:    v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json
- C3 extended:       v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.csv

输出位置：
- 06_v0.4_code/08_visualization/
- 执行报告：02_Claude输出/

红线：
- 不训练、不推理、不生成数据。
- 不改 split / 模型 / 超参 / seed。
- 不修改既有图表脚本（generate_figure2_fixed.py, generate_e45d_figures.py）。
- 不生成 Figure S1, S2, Table S4（推迟项）。
- 不写论文正文正式段落。
- 不启动档 B、raw 4-dim OCS-only、--mode all。
- 不外推真实 GEO、三轴姿态、暗室实验。
```

---

## 10. 附录：R83 规划体系完整对照

| R83 规划项 | 当前状态 | A2 判定 |
|-----------|---------|---------|
| **正文 Figures** | | |
| Figure 1 | 未生成 | 推迟（Methods 写作阶段） |
| Figure 2 | ✓ E36 已稳定 | 无缺口 |
| Figure 3 | ✓ E45D 已稳定 | 无缺口 |
| Figure 4 | ✓ E45D 已稳定 | 无缺口 |
| **正文 Tables** | | |
| Table 1 | 未生成 | 推迟（Methods 写作阶段） |
| Table 2 | ✓ E45D 已稳定 | 无缺口 |
| **SI Figures** | | |
| Figure S1 | 未生成 | 推迟（二级诊断） |
| Figure S2 | 未生成 | 推迟（二级诊断） |
| Figure S3 | 未生成 | **P0 必要** |
| Figure S4 | 未生成 | **P0 必要** |
| Figure S5 | ✓ E45D 已稳定 | 无缺口 |
| **SI Tables** | | |
| Table S1 | 未生成 | 推迟（Methods 写作阶段） |
| Table S2 | ✓ E36 已稳定 | 无缺口 |
| Table S3 | 未生成 | **P0 必要** |
| Table S4 | 未生成 | 推迟（screening 细节） |
| Table S5 | 未生成 | 推迟（架构对比实验） |

**P0 必要项总计**：3 项（Figure S3, S4, Table S3）  
**已完成项总计**：5 项（Figure 2, 3, 4, S5, Table 2, S2）  
**推迟项总计**：7 项（Figure 1, S1, S2, Table 1, S1, S4, S5）

---

**评估完成**。建议立即执行 1C-A2-GEN，补齐 P0 必要 SI 资产后进入 A-3 桥接材料撰写。

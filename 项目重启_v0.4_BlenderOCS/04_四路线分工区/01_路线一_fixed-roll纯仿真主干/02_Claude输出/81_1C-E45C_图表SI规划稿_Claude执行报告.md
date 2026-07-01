# 1C-E45C 图表/SI 规划稿 — Claude 执行报告

最后更新：2026-06-27
执行端：Claude
依据审阅：R82 Codex 审阅（E45B 通过，指标重构与外推鸿沟叙事稳定）
性质：D 类只读规划（不训练、不生成图、不写论文正文）

## 0. 执行声明

本报告只读取 R77/R78/R80/R82 已稳定成果和 E44 Results 总材料包，做图表/SI 编号体系规划。未触发训练、代码修改、图表生成或论文正文正式改写。

## 1. 规划原则

R82 确立的证据层级决定图表优先级：

```text
主叙事证据（承担论文核心论证）：
  yaw circular MAE、within-k、coarse-bin 与 chance/random baseline 的对照

辅助哨兵指标（说明严格分类命中失败，不单独承载物理 claim）：
  exact-bin yaw accuracy = 0.00%

机制解释证据（定位失败模式）：
  E45A holdout-prediction ratio = 0.0
```

图表规划遵循：
- 正文主图优先展示主叙事证据，exact-bin 0% 最多作为 compact inset 或 SI。
- 正文主表采用 R82 §3 指标重构表结构。
- Pitch 独立作为 yaw/pitch anisotropy 辅助图。
- SI 承载 per-fold 详情、训练曲线、overlap 诊断和已降级图表。

## 2. 当前体系回顾（E44/R78 候选编号）

| 编号 | 内容 | 状态 |
|---|---|---|
| Table 1 | OCS feature configuration overview | E35 草案 |
| Table 2 | C2 OCS-only screening results | E35 草案 |
| Table 3 | C2 grouped results by claim_class | E35 草案 |
| Table 4 | C3 formal per-fold results | E43 草案 |
| Table 5 | C2/C3 three-channel comparison with OCS input spec | E43 草案 |
| Figure 1 | Feature extraction pipeline | 待生成 |
| Figure 2 | Circular yaw-block holdout strategy | ✅ 已生成 PNG/PDF |
| Figure 3 | Yaw CMAE vs within-3 scatter | 待生成 |
| Figure 4 | Pitch accuracy by config grouped bar chart | 待生成 |
| Figure 5 | C2/C3 three-channel yaw_acc comparison | 待决定（E44 已建议降级） |
| S1 | Raw feature definitions and pre-registered constants | E35 已有 |
| S2 | C2 per-fold results table, 65 rows | ✅ 已生成 CSV |
| S3 | C3 per-fold detail, 10 folds × key fields | 待提取 |
| S4 | Training curves, C2 65 runs + C3 10 runs | 待提取 |
| S5 | Overlap reports, C2 + C3 strict status | JSON 已有，待整理 |

## 3. R82 后编号体系重排

### 3.1 正文 Figure（5 个）

| 编号 | 内容 | 数据来源 | 状态 | 位置 |
|---|---|---|---|---|
| Figure 1 | OCS feature extraction pipeline | feature_definitions.json | 待生成 | Methods |
| Figure 2 | Circular yaw-block holdout strategy | split_manifest | ✅ 已生成 | Methods/Results |
| Figure 3 | **Yaw extrapolation gap 主面板**：CMAE / within-6 / coarse45 三通道分组柱状图 vs chance baseline，附 random split reference 注释 | E45A JSON + R82 §3 表 | **待生成（P0 主图）** | Results |
| Figure 4 | **Pitch yaw/pitch anisotropy**：pitch exact / within-3 三通道分组柱状图 vs chance baseline | E45A JSON + R82 §3 表 | **待生成（P1）** | Results |
| Figure 5 | **Exact-bin sentinel + holdout-prediction 诊断**（compact，可拆为 a/b 双 panel 或单 panel + 正文一句话引用） | E45A JSON | **待生成（compact/SI 候选）** | Results/SI |

**Figure 5 详细方案（三选一，待作者/Codex 确认）：**

```text
方案 A（推荐）：Figure 5 不进正文。正文一句话 "exact-bin yaw accuracy was 0.00%
  across all three channels" 替代。原 exact-bin 全 0 对比图进 SI 作为 S5。

方案 B：Figure 5 作为正文 compact single-panel，只展示 exact-bin 0% 三通道 +
  chance 1.39% 参考线，附 "see SI Figure S5 for E45A holdout-prediction diagnostic"。

方案 C：Figure 5 保留为正文双 panel：(a) exact-bin 0% sentinel，(b) E45A
  holdout-prediction ratio = 0.0 机制诊断。两个 subpanel 均 compact。
```

### 3.2 正文 Table（3 个）

| 编号 | 内容 | 数据来源 | 状态 | 位置 |
|---|---|---|---|---|
| Table 1 | OCS feature configuration overview（13 configs 的 dim、特征名、物理含义） | feature_definitions.json | E35 草案，待精修 | Methods |
| Table 2 | **R82 指标重构主表**：yaw + pitch 全指标 × 三通道 vs chance baseline（即 R82 §3 表，含 random split reference 列） | E45A JSON + R80/R82 摘要 | **已有数值，待格式化为投稿表** | Results |
| Table 3 | C3 formal 5-fold per-fold 摘要（image_only / joint 各 5 折 × 关键指标） | C3 per-fold JSON | 待提取 | Results/SI 候选 |

**合并说明**：E44 时代的 Table 2（C2 screening）、Table 3（C2 grouped）、Table 5（C2/C3 three-channel comparison）的内容已被 R82 Table 2 覆盖或降级为 SI 详表。E44 Table 4（C3 per-fold）保留为 Table 3。如需 C2 screening 细节，进 SI Table。

### 3.3 SI Figures（5 个）

| 编号 | 内容 | 数据来源 | 状态 |
|---|---|---|---|
| S1 | C2 65-run yaw CMAE 分布（小提琴/箱线图，按 13 configs 分组）+ chance 90 deg 参考线 | c2_extended_metrics.json | 待生成 |
| S2 | Yaw CMAE vs within-6 散点图（C2 65 points + C3 10 points，按通道着色，叠加 chance 参考十字线） | E45A JSON per-fold | 待生成 |
| S3 | Training curves：C2 65 runs + C3 10 runs 的 train/val loss 曲线（代表性选例或全部） | training log CSV/JSON | 待提取 |
| S4 | Overlap 诊断：C2 + C3 strict holdout status 汇总（每 fold 的 train/yaw-block/test yaw 覆盖热图或表） | overlap JSON / split_manifest | JSON 已有，待整理 |
| S5 | **旧 Figure 5 归档**：exact-bin yaw_acc = 0.00% 三通道全 0 对比柱状图（从正文降级，compact 保留作为哨兵参考） | E45A JSON | 待生成（compact 版） |

### 3.4 SI Tables（5 个）

| 编号 | 内容 | 数据来源 | 状态 |
|---|---|---|---|
| ST1 | Raw OCS feature definitions and pre-registered constants（13 configs 的完整特征名、公式、常数） | feature_definitions.json | E35 已有草案 |
| ST2 | C2 per-fold results, 65 rows × key metrics | c2 per-fold JSON | ✅ 已生成 CSV |
| ST3 | C3 per-fold detail：10 folds（image_only 5 + joint 5）× key metrics（含 yaw/pitch exact, within-k, coarse, CMAE） | C3 per-fold JSON | 待提取 |
| ST4 | C2 screening grouped results by claim_class（13 configs 按 claim 分组汇总） | c2_screening_summary.json | E35 草案 |
| ST5 | C2 enhanced OCS vs C3 raw 4-dim OCS 输入规格对照（防混用速查） | E44 §6 + manifest JSONL | E44 已有文本 |

## 4. Figure 5 处理（待确认）

```text
当前状态：E44 时代 Figure 5 = C2/C3 three-channel yaw_acc comparison（全 0）
R82 裁决：降级为 SI 或正文小 inset，不再作为正文主图
E45B Claude 报告：给出 A（SI）/ B（compact inset）/ C（移除）三方案

本规划稿建议：
- 若走方案 A：正文 Figure 5 改为 exact-bin sentinel + holdout-prediction diagnostic
  compact panel（§3.1 方案 C），旧 Figure 5 进 SI 作为 S5。
- 若走方案 B：正文 Figure 5 保留为 compact exact-bin sentinel only，holdout-prediction
  进 SI S5。
- 若走方案 C：正文只有 Figure 1-4，Figure 5 编号空缺或留给未来补充图。

推荐：方案 A，即 Figure 5 = compact 双 panel (a) exact-bin sentinel (b) holdout-prediction
diagnostic。既有哨兵又有机制，信息密度合理，不占用主图位置。
```

## 5. S3/S4/S5 内容定义

R82 后重新确认：

### S3（SI Figure）— Training curves

```text
内容：C2 65 runs + C3 10 runs 的 train/val loss 曲线
范围建议：
  - C2：选 3-5 个代表性 config（best/mid/worst yaw CMAE）各展示 1 条 loss 曲线
  - C3：image_only 5 folds + joint 5 folds，各展示 1 条 loss 曲线
  - 不逐 run 全展（65+10=75 条曲线不可读）
形式：多 panel 小图（C2 代表性 config × 1 fold + C3 全 10 folds）
用途：支撑 "possible overfit" 诊断措辞（train/val loss separation 与 cross-yaw domain shift 相容）
```

### S4（SI Figure）— Overlap diagnostic

```text
内容：C2 + C3 的 train / test yaw-bin overlap 状态
范围：
  - 每 fold 的 train yaw bins vs holdout yaw block 覆盖矩阵或简洁热图
  - 确认所有 test yaw bin 均不在 train set 中（strict cross-yaw extrapolation 验证）
形式：紧凑热图或 0/1 矩阵（fold × yaw bin），或简化为 per-fold 汇总表
用途：方法透明性 — 证明 circular yaw-block split 确实产生了 strict holdout
```

### S5（SI Figure）— 旧 Figure 5 归档

```text
内容：旧 Figure 5 的 exact-bin yaw_acc = 0.00% 三通道全 0 柱状图（compact 版）
形式：单 panel 分组柱状图，C2/C3 image_only/C3 joint 三根柱均为 0，叠加 chance 1.39% 虚线
用途：哨兵指标归档，正文引用 "exact-bin yaw accuracy was 0.00% across all three channels (Figure S5)"
```

## 6. 已生成 vs 待生成汇总

### 已生成（可直接引用）

| 资产 | 路径 | 对应编号 |
|---|---|---|
| Figure 2 PNG/PDF | `06_v0.4_code/08_visualization/Figure2_yaw_block_holdout_fixed.png/.pdf` | Figure 2 |
| S2 per-fold CSV | `v0.4_results/05_c2_screening/supplementary_table_s2_per_fold_results.csv` | ST2 |
| S2 first 10 rows MD | `v0.4_results/05_c2_screening/supplementary_table_s2_first10_rows.md` | ST2 |

### 待生成（E45C 不放行生成，仅规划）

| 优先级 | 资产 | 对应编号 | 所需数据 |
|---|---|---|---|
| P0 | Yaw extrapolation gap 主图 | Figure 3 | E45A JSON (c2_extended_metrics.json + c3_extended_metrics.json) |
| P0 | R82 指标重构主表 | Table 2 | 同上 + R82 §3 已算好的数值 |
| P1 | Pitch anisotropy 图 | Figure 4 | E45A JSON |
| P1 | Exact-bin sentinel 图 | Figure 5 / S5 | E45A JSON |
| P2 | C2 yaw CMAE 分布箱线图 | S1 | c2_extended_metrics.json |
| P2 | CMAE vs within-6 散点图 | S2 | E45A JSON per-fold |
| P2 | Training curves | S3 | training log 文件 |
| P2 | Overlap 热图 | S4 | split_manifest / overlap JSON |
| P2 | C3 per-fold 详表 | ST3 | C3 per-fold JSON |
| P3 | Figure 1 pipeline 图 | Figure 1 | feature_definitions.json |
| P3 | Table 1 OCS config 表 | Table 1 | feature_definitions.json |
| P3 | Table 3 C3 per-fold 摘要 | Table 3 | C3 per-fold JSON |
| P3 | ST4 C2 screening grouped | ST4 | c2_screening_summary.json |
| P3 | ST5 OCS 输入规格对照 | ST5 | E44 §6 文本 |

### 不需要重新生成的现有资产

```text
- Figure 2（yaw-block holdout strategy）：已稳定，直接引用
- ST2（C2 per-fold 65-row CSV）：已稳定，直接引用
- ST1（OCS feature definitions）：E35 草案已有，需精修但不需重新提取数据
```

## 7. 完整编号体系一览

```text
=== 正文 ===
Figure 1   OCS feature extraction pipeline                              Methods
Figure 2   Circular yaw-block holdout strategy                         Methods/Results ✅
Figure 3   Yaw extrapolation gap: CMAE/within-6/coarse45 vs chance     Results (主图)
Figure 4   Pitch anisotropy: exact/within-3 vs chance                  Results
Figure 5   Exact-bin sentinel + holdout-prediction diagnostic           Results (compact)

Table 1    OCS feature configuration overview                          Methods
Table 2    Indicator reconstruction: three-channel yaw/pitch vs chance Results (主表)
Table 3    C3 formal per-fold summary                                  Results

=== SI Figures ===
S1         C2 65-run yaw CMAE distribution by config (violin/box)
S2         Yaw CMAE vs within-6 scatter by channel + chance reference
S3         Training curves (C2 representative + C3 full)
S4         Overlap diagnostic: train/test yaw-bin coverage
S5         Old Figure 5 archive: exact-bin all-0 sentinel

=== SI Tables ===
ST1        Raw OCS feature definitions and pre-registered constants
ST2        C2 per-fold results, 65 rows ✅
ST3        C3 per-fold detail, 10 folds × key metrics
ST4        C2 screening grouped results by claim_class
ST5        C2 enhanced OCS vs C3 raw 4-dim OCS input spec comparison
```

## 8. 与 E44 作者待确认事项的对应

E44 §8 列出的三个待确认事项，本规划稿的回应：

```text
1. Figure 5 处理：
   → 推荐 §4 方案 A：正文 Figure 5 = compact exact-bin + holdout-prediction 双 panel，
     旧 Figure 5 进 SI S5。待作者/Codex 从三个方案中确认其一。

2. S3/S4 是否现在提取：
   → E45C 不生成图。S3/S4 内容定义已在 §5 完成，实际提取在后续放行后执行。
     S3（training curves）优先级 P2，S4（overlap diagnostic）优先级 P2。

3. 编号体系统一：
   → 已在 §7 给出完整编号体系。正文 Figure 1-5 + Table 1-3，SI Figure S1-S5 +
     SI Table ST1-ST5。C2/C3 不再分组编号。
```

## 9. 解耦说明：哪些是"论文写作时才需要"的

以下资产建议推迟到论文正文写作阶段再生成，E45C 后不需要立即执行：

```text
- Figure 1（pipeline 图）：需要作者确定最终 pipeline 边界和标注
- Table 1（OCS config 表）：依赖 Methods 章节最终措辞
- ST4（C2 screening grouped）：辅助材料，不影响主叙事
- ST5（OCS 输入规格对照）：E44 §6 文本已可直接用
```

以下资产建议在论文写作前的"图表预生成阶段"优先执行：

```text
P0: Figure 3（yaw extrapolation gap 主图）
P0: Table 2（指标重构主表，数值已有，只需格式化）
P1: Figure 4（pitch anisotropy）
P1: Figure 5 / S5（exact-bin sentinel）
```

## 10. 红线确认

```text
✅ 未训练
✅ 未改任何代码、split、模型、超参、seed
✅ 未生成任何新图/新表
✅ 未写论文正文正式段落
✅ 未改成果区
✅ 未外推真实 GEO、三轴姿态、暗室实验或所有模型
✅ 输出位置：02_Claude输出/（非 04_Codex审阅/、非 01_成果区/）
✅ E45C 不放行图表生成，只做规划
```

## 11. 待 Codex/作者确认

1. **Figure 5 方案选择**：§4 方案 A / B / C 选其一。
2. **Figure 3 具体面板设计**：单 panel 多指标分组柱状图 vs 多 panel（CMAE / within-6 / coarse45 各一 panel）。
3. **Table 2 vs Table 3 的正文/SI 归属**：Table 3（C3 per-fold 摘要）当前标记为 Results/SI 候选，是否进正文取决于作者对正文表数量的偏好。
4. **S3 training curves 范围**：C2 选代表性 config 还是全 65 runs？
5. **S1/S2 是否必要**：S1（C2 CMAE 分布）和 S2（CMAE vs within-6 散点）是否为 Figure 3 主图的冗余？如是可合并或取消。
6. **编号前缀**：SI Tables 使用 "ST1-ST5" 还是 "Table S1-S5"（目标期刊惯例）？

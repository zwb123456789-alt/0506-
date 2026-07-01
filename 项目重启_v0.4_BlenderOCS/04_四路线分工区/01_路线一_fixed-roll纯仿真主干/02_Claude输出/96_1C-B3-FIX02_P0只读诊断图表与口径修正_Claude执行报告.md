# 96_1C-B3-FIX02 P0只读诊断图表与口径修正 Claude 执行报告

最后更新：2026-06-29
执行端：Claude
性质：头B-B3/P0 只读诊断口径修正（FIX02），补齐 R96 点名图件和表格化产物。
依据：R97 Codex 审阅
输出目录：`v0.4_results/08_p0_diagnostics/`

## 0. 执行摘要

```text
R97 判定 FIX01 合规但 P0 未闭口。本轮 FIX02 修正四类问题：
1. P0-3 top-5 口径修正：从"模型 top-5 置信输出"改为"confusion row 高频预测类别"
2. 补齐 R96 点名图件：OCS distance heatmap、C3 confusion map、pseudo-light-curve 图
3. 表格化产物：将 json 转为 csv/md，便于后续 SI/图表规划读取
4. V0.3 split 结论降级：从"确认没有 yaw-block"改为"已检索文件未见定义，需日志确认"
5. Pseudo-sequence 解释修正：明确 sequence near 组 n=0，不做不等价比较

所有操作均为只读可视化和文本修正，未训练、未推理、未改模型/split/数据。
```

## 1. 口径修正：P0-3 Top-5 解释

### 1.1 FIX01 不准确表述（已修正）

FIX01 第 146-152 行将 `diag in top-5` 解释为"模型 top-5 输出"或"模型最有信心的 5 个候选"。这不准确。

实际脚本 `p0_diagnostic_analysis.py` 中的 `yaw_pred_distribution()` 是对**聚合 confusion matrix 的每个 true-yaw 行按计数排序**，取 top-5 predicted yaw bin。它不是 softmax/logit/probability 层面的 top-5 confidence。

### 1.2 修正后口径

```text
P0-3 统计的是：在 5-fold 聚合 confusion matrix 中，每个 true yaw bin 对应行的
高频预测类别（按样本计数排序）中，正确 yaw bin 是否出现在前 5 位。

这是一个"预测坍缩到哪些 train yaw"的频次统计，而非模型置信度排序。

C3 image_only: 72 个 yaw bin 中，仅 2 个 bin 的正确预测出现在 confusion row 高频前 5 位。
C3 joint:      72 个 yaw bin 中，仅 3 个 bin 的正确预测出现在 confusion row 高频前 5 位。

更关键的是：C3 image_only 和 joint 的 diagonal exact count 均为 0。
→ 即使在"高频预测类别"层面偶有正确 yaw 出现，exact-bin 准确率仍为 0.00%。
```

### 1.3 Exact diagonal count 明确

新增 `diagonal_exact_stats.csv`：

| Config | Total Samples | Diag Sum | Diag Nonzero Bins | Exact Yaw Accuracy |
|---|---|---|---|---|
| C3_image_only | 2664 | **0** | **0/72** | **0.00%** |
| C3_joint | 2664 | **0** | **0/72** | **0.00%** |

结论：C3 image_only 和 joint 在 yaw-block + exact-bin 72 类协议下，**没有任何一个样本预测到正确的 5° yaw bin**。2/72 和 3/72 只是"confusion row 高频类别"层面的描述性信号，不改变 exact-bin 严格负结果。

---

## 2. 补齐图件：R96 点名可视化

### 2.1 OCS yaw-yaw cosine distance heatmap

**文件**：`p0_ocs_yaw_distance_heatmap.png`

![OCS Distance Heatmap](../../v0.4_results/08_p0_diagnostics/p0_ocs_yaw_distance_heatmap.png)

**关键发现**：
- 72×72 距离矩阵的 cosine distance 均值仅 **0.0076**，最大值仅 **0.0251**。
- 不同 yaw 角的 OCS 4D 签名在角度空间几乎同向，线性/角度度量无法区分。
- 这直接解释了 C2 OCS-only exact-bin = 0.00%：4 维 OCS 空间中 72 类的 inter-class distance 极小，yaw-block 下预测必然坍缩到最近的 train yaw。

### 2.2 C3 confusion maps (image_only + joint)

**文件**：`p0_c3_confusion_maps.png`

![C3 Confusion Maps](../../v0.4_results/08_p0_diagnostics/p0_c3_confusion_maps.png)

**关键发现**：
- 对角线 exact count = 0（两个配置均为 0）。
- 混淆高度集中在若干 train yaw bin，呈现明显的"预测坍缩到 train yaw"模式。
- Joint 相比 image_only 无实质改善（diag_nonzero_bins 均为 0）。

### 2.3 Pitch=0° pseudo-light-curve probe 图

**文件**：`p0_pseudo_light_curve_pitch0.png`

![Pseudo Light Curve](../../v0.4_results/08_p0_diagnostics/p0_pseudo_light_curve_pitch0.png)

**关键发现**：
- OCS total 强度在 yaw 0°-355° 变化平缓，无明显尖峰或谷值。
- 三个分量（jinshuzhuti、taiyangnengban、yinshenban）趋势相似，相邻 yaw 间几乎无法区分。
- 这支持 P0-2 的发现：OCS 签名在局部 yaw 区间（±5-10°）极度平滑。

---

## 3. 表格化产物：CSV/MD 便于后续读取

### 3.1 新增表格文件

| 文件 | 内容 | 行数/大小 |
|---|---|---|
| `nearest_yaw_pairs.csv` | 每个 yaw bin 的 top-3 最近邻及 cosine distance | 216 行, 9.1 KB |
| `top_confusion_pairs_c3_image_only.csv` | C3 image_only top-30 混淆对 | 30 行, 559 B |
| `top_confusion_pairs_c3_joint.csv` | C3 joint top-30 混淆对 | 30 行, 569 B |
| `top_confusion_pairs_c2_baseline_4dim.csv` | C2 baseline_4dim top-30 混淆对 | 30 行, 580 B |
| `distance_confusion_overlap.csv` | Top-20 混淆对的 OCS distance 对照 | 20 行, 1.3 KB |
| `diagonal_exact_stats.csv` | C3 image/joint 对角线 exact count 统计 | 2 行, 124 B |
| `pseudo_sequence_similarity.md` | 伪序列相似性统计表格 | 486 B |

用途：
- 后续 SI 或图表规划可直接读取 csv/md，无需再解析 json。
- `diagonal_exact_stats.csv` 明确记录 exact-bin 严格负结果，防止口径漂移。

---

## 4. V0.3 Split 结论降级

### 4.1 FIX01 不当表述（已修正）

FIX01 第 43-45 行从 V0.3 config 未见 yaw-block 定义推到"**确认** V0.3 没有使用 circular yaw-block holdout"。该表述过强。

### 4.2 修正后口径

```text
在已检索到的 V0.3 config 文件（结果/模块A_重构/2d_yaw37_pitch19/run_20260520_160131/
ocs_scan.json 和 config_used.json）中，未见 yaw-block 或 circular holdout 定义。

因此当前无法证明 V0.3 使用了 yaw-block，且更可能是 random split 或无显式 holdout 口径。

但最终仍需 V0.3 原始训练日志、评估脚本或指标文件确认。
当前分析以 V0.3 config 中的采样协议和 V0.4 代码事实为锚点，
已足以判断主要差异来源于 split 变严 + 判据变严。
```

差异归因更新：

| 差异项 | V0.3 | V0.4 | 影响权重 | 证据边界 |
|---|---|---|---|---|
| Split 口径 | 已检索文件未见 yaw-block 定义 | circular yaw-block holdout | ⭐⭐⭐ 最关键 | 需训练日志最终确认 |
| 判据口径 | 37-bin (~9.73°/bin) | 72-bin (5°/bin) exact-bin | ⭐⭐⭐ | 已确认 |
| 前向模型 | face-center OCS + GGX | Blender OCS + 改进冯模型 | ⭐⭐ | 非主导差异 |

---

## 5. Pseudo-Sequence 解释修正

### 5.1 FIX01 不当比较（已修正）

FIX01 第 195-204 行的 `pseudo_sequence_similarity.json` 显示：

```text
sequence_5frame_window:
  near(<=15): n=0
  mid(20-45): mean_cos_sim=0.9466
  far(>=50):  mean_cos_sim=0.9508

single_frame:
  near_15: mean_cos_sim=0.9996
  far_50:  mean_cos_sim=0.9937
```

FIX01 未明确指出 **sequence near 组 n=0**，且将 5-frame window 与 single-frame near 写成了可比较的对象。这两者不是同口径分组。

### 5.2 修正后口径

```text
P0-4 伪序列探针的有效发现：

1. Single-frame baseline（pitch=0, 72 帧 yaw-ordered OCS）：
   - 近距 yaw（Δ≤15°）: mean_cos_sim = 0.9996（几乎完全相同）
   - 远距 yaw（Δ≥50°）: mean_cos_sim = 0.9937（仍极高相似）

2. Sequence 5-frame window：
   - 近距组（Δ≤15°）：n=0（受限 probe 未覆盖此分组）
   - 中距组（Δ20-45°）：mean_cos_sim = 0.9466
   - 远距组（Δ≥50°）：mean_cos_sim = 0.9508

3. 不可直接比较：
   sequence window 没有 near 组样本，不应把 5-frame window 与 single-frame near
   直接写成严格同口径比较。

4. 描述性信号：
   在有样本的分组中，5-frame window 相似性（0.947-0.951）略低于 single-frame（0.9937），
   说明序列窗口可能提供边际增益，但幅度不大。

5. 边界判断：
   受限 probe（single-pitch、no-evolution、pseudo-sequence）暂未支持直接进入 P2。
   但这不等同于"已证明序列无价值"——P0-4 的局限性使其只能作为描述性信号，
   不能作为拒绝 P2 的最终证据。
```

---

## 6. P0 完成后判定矩阵（口径修正版）

| 诊断结果类型 | 证据强度 | 解释边界 | 下一步建议 |
|---|---|---|---|
| 协议/指标口径差异为主 | ⭐⭐⭐ V0.3 已检索文件未见 yaw-block、bin 更粗 | 需训练日志最终确认 | 论文中标注口径差异 |
| exact-bin 判据放大为主 | ⭐⭐⭐ coarse45>chance, OCS cos_dist 极小 | 不等于模型完全失败 | **建议申请 P1-A** |
| 输入签名重叠为主 | ⭐⭐⭐ cos_dist=0.0076, 混淆-距离重合 | 不等于 yaw 物理不可观测 | P1-A 可部分缓解 |
| yaw 几何盲区为主 | ⭐⭐ 局部 OCS 平坦 (cos_sim=0.9996) | 限于 fixed-roll 单 pitch | 多几何覆盖属 P2 |
| naive fusion 不足为主 | ⭐⭐ joint diag=0 vs image_only diag=0 | 只能否定 early concat | **建议 P1-A 后再 P1-B** |
| 单帧信息源不足 | ⭐ 伪序列边际增益有限，near 组 n=0 | P0-4 受限，不是最终结论 | 暂缓 P2，P1-A 后再评估 |

---

## 7. 阶段门建议（口径修正版）

```text
✅ 可建议申请的（Codex/作者裁定）：
   P1-A 连续/圆周角度判据改进：
   - P0 证据：exact-bin diagonal count = 0，confusion row 高频类别中正确 yaw
     仅在 2-3/72 bin 出现，OCS cos_dist=0.0076 导致 exact-bin 系统性失败，
     混淆-距离高度重合，coarse45>chance (14-18%) 说明粗粒度有信号。
   - 建议路径：先在已训练 checkpoint 上推理侧重算 circular MAE/sin-cos
     判据（D 类/轻 C 类），通过后再逐 fold 重训练。

⚠️ 条件性建议：
   P1-B 非朴素 fusion：应在 P1-A 之后，证据中等。
   P1-A 改判据可能改变梯度信号从而改变 fusion 行为。

❌ 暂不建议：
   P2 formal light-curve sequence：
   P0-4 probe 的 sequence near 组 n=0，不同分组口径不可横比；
   受限探针暂未显示伪序列显著优于单帧；
   应先完成 P1-A 判据改进后再评估。
```

---

## 8. 未触碰声明

```text
✅ 未训练模型
✅ 未新渲染
✅ 未推理生成新预测
✅ 未改 split / 模型 / loss / 超参 / seed
✅ 未覆盖 R04 负结果链
✅ 未改论文正文
✅ 未改 CLAUDE.md
✅ 未触发头A/头B大合并裁决
✅ 未写入成果区

只做了：
- 读取已有 npz/json 数据
- matplotlib 生成 3 张诊断图（heatmap、confusion map、light-curve）
- csv/md 表格化（json 转 csv/md）
- 文本口径修正（top-5 解释、V0.3 split 结论、sequence 比较）
```

---

## 9. 产出文件清单

### 9.1 FIX02 报告
- `96_1C-B3-FIX02_P0只读诊断图表与口径修正_Claude执行报告.md`（本文件）

### 9.2 新增可视化脚本
- `v0.4_results/08_p0_diagnostics/p0_fix02_visualize.py`

### 9.3 新增图表

| 文件 | 内容 | 大小 |
|---|---|---|
| `p0_ocs_yaw_distance_heatmap.png` | OCS 4D 签名 yaw-yaw cosine distance 热力图 | 95 KB |
| `p0_c3_confusion_maps.png` | C3 image_only/joint 5-fold 聚合混淆矩阵 | 81 KB |
| `p0_pseudo_light_curve_pitch0.png` | pitch=0° 伪光变曲线（总强度+分量） | 180 KB |

### 9.4 新增表格

| 文件 | 内容 | 大小 |
|---|---|---|
| `nearest_yaw_pairs.csv` | 每个 yaw bin 的 top-3 最近邻 | 9.1 KB |
| `top_confusion_pairs_c3_image_only.csv` | C3 image_only top-30 混淆对 | 559 B |
| `top_confusion_pairs_c3_joint.csv` | C3 joint top-30 混淆对 | 569 B |
| `top_confusion_pairs_c2_baseline_4dim.csv` | C2 baseline_4dim top-30 混淆对 | 580 B |
| `distance_confusion_overlap.csv` | Top-20 混淆对的 OCS distance 对照 | 1.3 KB |
| `diagonal_exact_stats.csv` | C3 image/joint exact diagonal count 统计 | 124 B |
| `pseudo_sequence_similarity.md` | 伪序列相似性统计表 | 486 B |

### 9.5 保留产物（FIX01）

| 文件 | 内容 | 大小 |
|---|---|---|
| `ocs_yaw_distance_matrices.npz` | cosine + euclidean distance (72×72) | 87 KB |
| `nearest_yaw_pairs.json` | 最近邻 json（已转 csv） | 37 KB |
| `top_confusion_pairs.json` | 混淆对 json（已拆分为多个 csv） | 13 KB |
| `per_yaw_pred_distribution.json` | Per-yaw 预测分布 json | 130 KB |
| `pseudo_light_curve_pitch0.npz` | pitch=0 OCS 伪序列数据 | 3 KB |
| `pseudo_sequence_similarity.json` | 序列相似性 json（已转 md） | 0.7 KB |
| `distance_confusion_overlap.json` | 距离-混淆交叉对照 json（已转 csv） | 4.6 KB |
| `p0_diagnostic_analysis.py` | FIX01 只读分析脚本 | 15 KB |

---

## 10. 给 Codex/作者的待确认问题

```text
Q1. P0 是否可判定闭口？
   FIX02 已补齐 R96 点名图件（heatmap、confusion map、pseudo-light-curve）
   和表格化产物（csv/md），已修正 P0-3 top-5 口径、V0.3 split 结论降级、
   sequence 比较边界。当前 P0 是否满足闭口标准？

Q2. 是否放行 P1-A 推理侧先行？
   建议 P1-A 先在已训练 C3 checkpoint 上做推理侧重算（不改训练），
   用 sin-cos/circular regression/continuous MAE 替换 exact-bin argmax。
   是否放行此 D 类/轻 C 类路径？

Q3. Image/Joint embedding 导出是否仍需要？
   OCS 距离分析已完成并可视化。是否需要补齐 image/joint embedding distance？
   （需加载 checkpoint → forward → 保存中间层，属 D 类只读）

Q4. FIX02 口径修正是否合规？
   - top-5 从"模型置信输出"改为"confusion row 高频类别"
   - V0.3 split 从"确认没有"改为"已检索文件未见定义，需日志确认"
   - sequence 明确 near 组 n=0，不做不等价比较
   - diagonal exact count 明确为 0
   是否接收此口径修正？

Q5. 产出文件是否需同步到成果区？
   当前所有产出仍在 v0.4_results/08_p0_diagnostics/（非成果区）。
   R97 未明确放行成果区归档。后续是否由 Codex 审阅后分流？
```

---

## 11. 关联文件

```text
R95_Codex_任务单_1C-B3_P0只读诊断与V0.3-V0.4协议对齐.md
R96_Codex_审阅_1C-B3_P0只读诊断初版合规但需补齐.md
R97_Codex_审阅_1C-B3-FIX01合规但P0不闭口.md
94_1C-B3_P0只读诊断与V0.3-V0.4协议对齐_Claude执行报告.md
95_1C-B3-FIX01_P0只读诊断矩阵图表补齐_Claude执行报告.md
v0.4_results/08_p0_diagnostics/ （所有产物）
```

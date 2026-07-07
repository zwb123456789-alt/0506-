# 三轴指标规格说明（three_axis_metric_spec）

最后更新：2026-07-01
来源：R129 任务单子任务 B；字段可追溯至路线一 C 结果包 11/13/16/17。

本文件把三轴小项目指导文件中的概念指标，落为可计算字段。所有指标目前只在
**fixed-roll (roll=0)** 基线上可直接计算；roll 维度需 P1 seed-roll scan 新渲染后补齐。
本文件不定义、也不承诺真实未知目标姿态反演成功率——那不是本小项目指标。

## 1. 指标总览与数据源

| 指标 | 定义 | 现有字段来源 | roll 扩展需求 |
|---|---|---|---|
| brightness / OCS magnitude | 单几何总光度 `ocs_total` | `01_fullrun`(phase63) + `11_.../postprocess/{phase24,45,90,120}` 的 `_ocs.json` | 需对种子点 roll≠0 新渲染 |
| local contrast | 姿态邻域（±5° yaw/pitch）内 OCS 或签名的可区分度 | 由 master 表邻域差分计算 | roll 邻域需新采样 |
| nearest-neighbor ambiguity | 光度/图像签名最近邻混淆 | `13_.../pdb/l1d3_pdb_retrieval_per_query.csv`: `nearest_distance`,`margin` | roll 需新检索库 |
| candidate entropy / margin | 候选分布集中程度 | `13_.../consistency/l1d3_neural_pdb_joined_per_attitude.csv`: `neural_entropy`,`neural_margin` | roll-aware 模型（不在本轮） |
| top-k stability | 局部扰动下最优候选是否稳定 | `13_.../pdb/...`: `topk10_idx` | roll 扰动需新预测 |
| OCS-image overlap / JS | 通道一致或冲突 | `16_.../tables/d2_pairwise_topk_overlap.csv`,`d2_pairwise_disagreement.csv` | roll 需新预测 |
| saturation / glint flag | 亮但不可用风险 | 由 `ocs_total` 分位 + `n_pixels_contributing` 派生（见 §3） | roll 需新渲染 |
| geometry utility score | 观测几何是否值得投入 | `16_.../tables/d4_geometry_gain_by_attitude.csv`,`d4_observability_region_stats.csv` | 组合 roll 后重算 |
| roll sensitivity score | fixed-roll 结论在 roll 方向是否迁移 | `17_.../mroll_full2664/predictions_*` 的 `yaw_err`（±15/±30） | 已有 ±15/±30 先验；P1 加密 |

## 2. 可直接计算 vs 需新增字段

**A 类：现有字段可直接映射（本轮已用于 seed 提取）**
- brightness（phase63/24/45/90/120 均已渲染 roll=0，各 2664）。
- geometry utility（D4 gain / region stats）。
- nearest-neighbor ambiguity（pdb nearest_distance / margin）。
- candidate entropy/margin（neural_pdb_joined）。
- roll sensitivity 先验（mroll ±15/±30）。
- OCS-image overlap/JS（D2 pairwise 表）。

**B 类：需在本包内派生（只读计算，不新渲染）**
- local contrast：邻域差分，见 §3.1。
- saturation/glint flag：亮度分位 + 贡献像素比，见 §3.2。

**C 类：需 roll≠0 新渲染或 roll-aware 训练才能补齐（本轮不做）**
- roll 维度上的 brightness、contrast、entropy、overlap、top-k stability。
- roll-aware candidate distribution。

## 3. 派生指标定义

### 3.1 local contrast（本包可算）
对姿态 (yaw,pitch)，取 8 邻域（yaw±5, pitch±5）内 `ocs_total` 与自身之差的均值绝对值：
```
local_contrast(a) = mean_{n in neighbors(a)} |ocs_total(a) - ocs_total(n)|
```
高 contrast = 姿态在邻域中亮度签名可区分；低 contrast = 平台区，易混淆。

### 3.2 saturation / glint flag（本包可算）
```
glint_flag = (ocs_total >= P99) AND (n_pixels_contributing <= P10_of_contrib_among_bright)
```
即亮度极高但贡献像素极少 → 由少数镜面高光主导 → 亮但不稳定/不可用风险。

## 4. 关键边界（写入 registry 的 notes）

- 最亮姿态 != 高信息姿态：本包实测 `corr(log10 brightness, G1->G5 gain) ≈ -0.09`，
  亮度与多几何可救回性几乎无正相关（见 `figures/brightness_vs_information.png`）。
- 高亮但饱和/glint/局部不稳定 → 标 high-risk，不进入高信息候选。
- 低亮但局部可分性强（高 contrast + 低 entropy）→ 可为高信息候选。
- 真实未知目标姿态反演成功率不是本小项目指标；P-EXT 仍坍缩、joint 强互补性未证明的边界继续保留。

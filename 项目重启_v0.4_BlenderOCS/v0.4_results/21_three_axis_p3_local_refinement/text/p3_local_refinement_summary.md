# P3 local refinement 可解释摘要

最后更新：2026-07-03
任务：R135 P3 local refinement
结果包：`v0.4_results/21_three_axis_p3_local_refinement/`
上游：R134 接收 P2 sparse grid，放行 P3 local refinement

---

## 1. 链路是否跑通

**是。** 在 P2 sparse 3-axis grid（5 度）基础上，对 primary 区域 R1/R4/R3 做 **2.5 度局部加密**，
R2/R5 保留少量 5 度对照点。

- 唯一 pose：107（整数 5 度点 42 + 半度 2.5 点 65）× 9 roll = 963 pose-roll 单位。
- 新渲染：非零 roll 856 + 半度点 roll=0 65 = **921 单位**（< 2000 上限），camera/sun/ocs/linear 各 921/921 完成。
- 整数点 roll=0：42 点复用 `01_fullrun`（不重渲）。
- 半度点 fullrun 无网格，roll=0 与非零 roll 全部新渲染，manifest 明确标注 source=21_pack，不静默缺失。
- 量纲：r_max/i_scale/pixel_area/depth_epsilon/SUN/DET 全部沿用 phase63 fullrun，与 P1/P2 可比。
- 图像可用性：963/963 pose-roll 单位 image_usable=1，指标无 nan。

---

## 2. R135 §5 五问回答

### Q1. R4 最亮点是否迁移？

**在 2.5 度加密下轻微迁移。** P2（5 度）最亮点为 yaw150/+15；P3 加密后区域内最亮 pose 迁移到
**yaw147.5/+12.5**（ocs_mean=1.98e-01），相对 P2 整数峰迁移 **3.54 度**（更低 yaw / 更低 pitch 的角落）。
最亮前 5 名全部落在 yaw145-150 × pitch+10~15 的半度点上，说明 5 度网格低估了亮度峰的确切位置，
但迁移幅度小（~3.5 度），最亮簇仍连成一片。

### Q2. R4 高信息边界点是否稳定，可作亮-信息折中候选？

**稳定。** info rank=1 仍在 **yaw155/+20**（neighbor_contrast=1.198），且相邻半度点
yaw155/+22.5(rank2)、yaw157.5/+20(rank3)、yaw152.5/+22.5(rank4)紧随其后，nc≈1.13-1.20 成片。
该点 brightness_rank=31（中等亮度）、无 glint/saturation，可作为**亮-信息折中候选**纳入 P4。

### Q3. R1 roll-sensitive peak 是否稳定？

**完全稳定（迁移 0.0 度）。** R1 区域内最亮/最敏感峰稳定在 yaw245-247.5 × pitch+30~40，
roll_sensitivity_score≈3.69-3.85，mean_roll_sensitivity=3.497（全区最高）。加密确认高 |pitch| /
yaw240 系 roll 敏感峰在 2.5 度邻域中稳定存在，local_information_stability=0.947。

### Q4. R3 低信息区是否连通，可作负面对照？

**较连通。** R3 low_info_connectivity=0.60（60% pose 的 neighbor_contrast 低于全局中位数），
local_information_stability=0.92（结构均匀），mean_nc=0.771（primary 区最低）。
适合作为观测规划**负面对照**（低信息、成片、结构稳定）。

### Q5. R2/R5 是否仅支持对照定位？

**是，应从 P4 主规划降权。** R2 utility=0.001、R5 utility=-0.162，均为对照级；
low_info_connectivity=1.0（全部低信息），仅用于 dark/neutral 对照定位，不作为 P4 主规划落点。

---

## 3. 区域特征（P3 加密后）

| 区域 | priority | mean_ocs | mean_nc | mean_rs | risk | utility | 加密结论 |
|------|----------|----------|---------|---------|------|---------|---------|
| R1_high_info | primary | 4.56e-02 | 1.036 | 3.497 | 1.00 | 0.457 | roll-sensitive peak 稳定(迁移0°) |
| R4_bright_info_boundary | primary | 9.76e-02 | 0.714 | 0.093 | 0.24 | 0.302 | 最亮点迁移3.5°；info边界稳定 |
| R3_low_info_connectivity | primary | 2.77e-02 | 0.771 | 1.841 | 1.00 | 0.195 | 低信息连通(0.60)，负面对照 |
| R2_control | control | 2.21e-02 | 0.469 | 0.982 | 1.00 | 0.001 | dark 对照，降权 |
| R5_control | control | 1.85e-02 | 0.167 | 0.451 | 1.00 | -0.162 | neutral 对照，降权 |

utility 排名 **R1 > R4 > R3 > R2 > R5**，与 P2 一致（P3 归一化基准为 P3 pose 分布，数值上移但序不变）。
注：R4 的 region-level mean_nc 偏低是因区域覆盖了大片亮而低对比的核心，而其 info-boundary 角点
(yaw155/+20)才是高信息点——这正是 brightness≠information 的体现，不能只看区域均值。

---

## 4. brightness ≠ information 在加密下更尖锐

- R4 最亮点 yaw147.5/+12.5 的 info_rank = **104/107**（几乎最低信息）。
- info rank=1 在 yaw155/+20，其 brightness_rank = 31/107。
- 二者在加密网格中分处 R4 区不同角落（yaw 相差 7.5 度、pitch 相差 7.5 度）。
**brightness ≠ information 边界在 2.5 度局部加密下不仅维持，且比 5 度网格更清晰地分离。**

---

## 5. P4 planning candidates

P4 候选 16 个（受控），按 p4_planning_utility_score 排序，覆盖：
- **high-info-roll-sensitive**（R1，8 个）：yaw245-247.5 × pitch+30~40，p4_utility 0.44-0.46。
- **bright-info-tradeoff**（R4，2 个）：yaw155/+20（info峰）、yaw152.5/+20，亮度中等+信息高。
- **low-info-negative-control**（R3，2 个）：yaw55-57.5 × pitch+60~62.5，负面对照。
- **dark/neutral-control**（R2/R5，4 个）：降权对照。

供 Codex 裁决是否放行 P4 observation planning synthesis。

---

## 6. 信息 proxy 边界

`neighbor_contrast_ypr` 在 P3 使用 2.5 度邻域步长（P2 为 5 度），更接近三轴局部可观测性概念，
但仍是 **smoke/proxy 级**。与模型级指标（P-DB / margin / entropy / conformal set_size /
roll-aware neural model）的关系需单独阶段门确认，不在 P3 内启动。本结论不能写成三轴最终可观测性结论。

---

## 7. 红线自检

- 未启动 P4/R128/训练：✓
- 未改旧脚本/旧目录 10-20：✓（只读 fullrun/P2，输出仅写 21 号包）
- 整数点 roll=0 复用 fullrun、半度点 roll=0 新渲染不静默缺失：✓
- 未写成果区/未生成 Codex 审阅文件/未改 CLAUDE.md：✓
- 未把 P3 写成三轴小项目完成：✓
- 未声称真实未知目标反演系统：✓（model-known simulated）
- 最亮构型未写成最优观测姿态：✓（brightness ≠ information 边界在加密下维持并更尖锐）

---

*本摘要供 Codex 004 审阅裁决是否放行 P4 observation planning synthesis。*

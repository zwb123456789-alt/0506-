# R154 Codex 审阅：009 通过，P4-PHYS-D 小矩阵接收并放行 P4-PHYS-E

最后更新：2026-07-06  
审阅对象：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/009_P4PHYS_D_sunview_small_matrix_Claude执行报告.md
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/
```

## 1. 裁决

009 / 26 包 **接收，达到强接收标准**。R153 要求的 `phase63/L1-G1` baseline 邻域 `sun±7° / view±7°` 小矩阵已完成，正式接收结论标签为：

```text
SUNVIEW_DEPENDENT_BUT_MECHANISTIC
```

含义：

```text
最亮姿态会随小幅 sun/view 几何变化迁移；
但迁移仍被金属主体近镜面对齐探测器的连续机制解释；
迁移目标落在 top-1 roll 邻域候选，而不是跳到暗区或无关机制。
```

本接收只关闭 P4-PHYS-D 阶段门，不关闭整个三轴小项目，不写成所有 sun/view 几何下的全局最亮结论。

## 2. 接收证据

产物完整：

```text
26 包存在，8 个顶层子目录；
009 报告存在；
generated_files_manifest.csv 记录 232 个文件，文件系统实有 233 个文件，差异为清单未计入自身，不影响接收；
figures/tables/audit/logs/text/scripts/render/postprocess 均存在。
```

设计与规模满足 R153：

```text
几何数 = 5 <= 5；
姿态数 = 14 <= 16；
新增渲染单元 = 56 <= 80；
smoke 为 G3_view_plus × top1/R4/R3，3/3 通过后才跑正式矩阵；
正式后处理 70/70 COMPLETE。
```

数值链路可审计：

```text
G0 baseline 逐像素 OCS 复现既有 ocs.json；
A_top1 = 0.2088904942，和 R148 的 0.2088904828 相对差约 5.5e-8；
全 70 个组合机制重算 vs metrics/ocs.json 均 OK；
max rel_diff = 1.443e-7。
```

渲染复用口径可接受：

```text
sun 扰动只新渲 sun EXR，复用 baseline camera EXR；
view 扰动只新渲 camera EXR，复用 baseline sun EXR；
后处理端按每个 geometry 的 sun_dir / det_dir 重新计算 OCS 和机制签名；
机制分析脚本明确令 H=(S+D)/|S+D| 随几何变化，而不是复用 baseline H。
```

## 3. 接收的科学结论

可以接收为当前阶段稳定结论：

```text
1. 在 5 几何 × 14 姿态的小矩阵内，G0 baseline 的 A_top1 仍是全表最高值：
   yaw=245.0, pitch=27.5, roll=+15, OCS=0.20889049。
2. 但 A_top1 在扰动几何下不再逐几何最亮：
   G1/G2/G3/G4 rank 分别为 7/4/4/6，OCS 降到约 0.164-0.188。
3. 扰动几何下的逐几何最亮点发生迁移：
   G1_sun_plus -> D5_roll125, OCS=0.19528240；
   G2_sun_minus -> D6_roll175, OCS=0.19493062；
   G3_view_plus -> D6_roll175, OCS=0.20491531；
   G4_view_minus -> D5_roll125, OCS=0.18548740。
4. 迁移目标均属于 top-1 roll 邻域簇，未跳到 R3 或暗区。
5. 全 70 个组合均为金属主体主导，metal% 范围约 92.71-99.26。
6. 严格二值 near_specular_metal 只在 9/70 个组合为 1，说明 25 包阈值对 ±7° 几何扰动敏感；但连续机制量支持“近镜面对齐机制分级平移”，不是机制消失。
7. R3 在 5 个几何下均为 near_specular_metal=0 且 rank=14，可继续作为负面对照；但 G1/G4 中 R3 绝对 OCS 上升到约 0.13，写作时只能说相对候选集仍最低，不能写成绝对黑暗。
```

## 4. 必须保留的限定

必须保留以下边界：

```text
1. 本结论只覆盖 baseline 附近 5 个几何和 14 个固定候选姿态，不是全 sun/view 全姿态搜索。
2. “机制稳定”应写成连续量意义下的金属主体近镜面对齐分级平移；不得写成严格 near_specular_metal 二值标签在所有几何稳定。
3. R4 在扰动几何下是金属主导的高亮/中高亮对照，但严格 near_specular_metal 多数为 0；不得写成 R4 在所有几何均满足二值同机制标签。
4. 隐身板增量仍只作为 top-1 roll 簇相对 R4 的排序特征，不是普遍高亮机制。
5. material-level 仍为 B0 proxy；未完成真实 material pass。
6. 不能启动 R128、训练、路线二/三/四或论文正文最终改写。
```

## 5. 阶段判断与下一步

P4-PHYS-D 通过，但三轴小项目不在此处闭口。理由：

```text
1. 小矩阵显示最亮姿态随 sun/view 迁移，不能把 fixed baseline top-1 写成几何稳定的唯一最亮姿态。
2. 当前只做了 pure sun±7° 与 pure view±7°，尚未检验 sun 与 view 同时扰动时是否仍落在同一 top-1 roll 邻域机制。
3. 26 包已经提供可复用的 sun pass 与 camera pass，适合低成本补齐一个 3×3 组合几何小网格，而不是扩大成全局搜索。
```

据此放行下一阶段：

```text
R155 / P4-PHYS-E：sun/view 3×3 组合小网格补齐
```

P4-PHYS-E 的原则：

```text
优先复用 26 包已有 EXR；
补齐 sun_offset ∈ {-7,0,+7} 与 view_offset ∈ {-7,0,+7} 的组合几何；
继续使用同一 14 个姿态候选，或只读复用同源候选；
原则上不新增渲染；
只判断局部组合几何下的 top 候选、机制连续性和是否可进入三轴小项目收口裁决；
不得做全 sun/view 全姿态搜索。
```

## 6. 成果区分流

009/26 的稳定成果摘要进入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/09_P4PHYS-D_sunview小矩阵扩展_R154通过.md
```

下一步任务单进入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R155_Codex_任务单_P4PHYS-E_sunview3x3组合小网格补齐.md
```


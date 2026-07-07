# R138 Codex 补充校正：三轴小项目唯一最高标准为最亮构型与光路解释

最后更新：2026-07-06  
性质：对 R136/R137 的口径校正，不推翻 004/P3 通过结论  
触发原因：作者指定三轴小项目唯一且最高标准为“找最亮姿态-观测几何构型，并解释入射-表面-探测器光路”。

## 1. 校正结论

作者判断正确。按 2026-07-06 修订后的三轴小项目冻结指导文件，唯一且最高目标是：

```text
在已知卫星模型和前向光学模型下，找出卫星在哪个 yaw / pitch / roll 姿态、
哪个太阳入射几何和哪个探测器观测几何下最亮，
并解释这束光从哪里入射、照到卫星哪个部位/材料/表面，
再沿哪个方向进入探测器。
```

因此，**找最亮构型时 roll、sun/view 几何和探测器观测方向都必须进入口径**。不能只给 yaw/pitch 的 roll 平均亮度峰，也不能把“亮-信息折中”“高信息姿态”或“观测规划”替代“最亮构型与光路解释”。

补充顺序要求：P4 必须先确定 single-pose top-1 最亮点，再检验该 top-1 的入射-表面/材料-探测器光路机制是否能解释一类普遍高亮的邻近姿态或候选簇。不能先用某个预设“高亮信念”反推 top-1，也不能只解释单个峰值而不检查同类机制的普遍性。

## 2. 已发现的口径偏差

R136/R137 中“R4 最亮点 yaw147.5/+12.5”主要来自 P3 的 `p3_high_brightness_refined_candidates.csv`，该表按 yaw/pitch pose 的 `ocs_mean` 排名，代表 roll 维度聚合后的高亮 yaw/pitch 区域。

但若按 `p3_local_refinement_metrics.csv` 中单个 yaw/pitch/roll 的 `ocs_total` 排名，当前 P3 明细表的最高值出现在：

```text
region = R1_high_info
yaw = 245.0
pitch = +30.0
roll = +15
ocs_total ≈ 2.083770e-01
```

这说明需要严格区分两种“最亮”：

```text
1. roll-aggregated brightest yaw/pitch region：
   用于判断某个 yaw/pitch 区域整体是否高亮、是否 roll 稳健。

2. single-pose brightest yaw/pitch/roll configuration：
   用于回答三轴小项目“最亮构型”主目标。
```

## 3. 对既有结论的影响

不推翻：

```text
P3 链路完成；
2.5 度加密方案有效；
R4 亮-信息边界稳定；
R1 roll-sensitive peak 稳定；
R3 低信息区较连通；
brightness != information 成立；
P4 综合阶段仍应执行。
```

必须修正：

```text
P4 的第一目标必须先输出三轴 single-pose brightest configuration；
P4 必须解释该最亮构型对应的入射方向、受光部位、材料/表面响应和探测器接收方向；
P4 必须在 top-1 确认后检验同类光路机制是否普遍对应高亮候选簇；
R4 不应被无条件写成“全局最亮构型”；
R4 更准确的角色是 roll-aggregated bright/robust region 与 bright-info tradeoff 区；
R1 需要作为 single-pose brightness peak 候选纳入 P4；
高信息/低信息/观测规划只保留为辅助标注。
```

## 4. 给 R137/P4 的补充要求

R137 后续执行必须增加并优先输出：

```text
tables/p4_global_brightest_pose_table.csv
tables/p4_brightest_roll_profile.csv
tables/p4_brightest_light_path_trace.csv
tables/p4_brightest_surface_material_trace.csv
tables/p4_bright_mechanism_generality_check.csv
figures/p4_global_brightest_pose_panel.png/.pdf
figures/p4_bright_mechanism_consistency_map.png/.pdf
text/p4_brightest_configuration_summary.md
text/p4_bright_mechanism_generality_summary.md
```

这些材料必须回答：

```text
1. 当前 P1/P2/P3 范围内 single-pose 最亮 yaw/pitch/roll 是什么。
2. roll-aggregated 最亮 yaw/pitch 区域是什么。
3. 最亮 single-pose 与 roll 稳健高亮区域是否一致。
4. 最亮 single-pose 的光从哪里入射、照到哪个部位/材料/表面、沿哪个方向进入探测器。
5. 与最亮 single-pose 共享同类光路机制的姿态/几何候选是否普遍高亮。
6. 若同类机制不普遍高亮，top-1 是否更可能是局部 glint、饱和、遮挡边界或数值偶然峰。
7. 最亮 single-pose 是否伴随 glint/saturation 风险。
8. 高信息/低信息只作为辅助标注，不改变最亮构型主结论。
```

## 5. 当前临时判断

基于 P3 明细表，当前临时最亮 single-pose 候选为：

```text
yaw=245.0, pitch=+30.0, roll=+15, ocs_total≈2.083770e-01
```

但该判断必须在 P4 中由 Claude 对 P1/P2/P3 明细表统一重聚合后正式确认，并补充光路、受光表面/材料与探测器接收路径解释。P4 不新增渲染，不训练，只做口径正确的综合与收口。

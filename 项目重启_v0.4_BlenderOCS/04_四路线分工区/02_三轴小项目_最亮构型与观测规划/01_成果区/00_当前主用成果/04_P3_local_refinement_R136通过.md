# P3 local refinement 说明（R136 通过，R138 后按最亮构型口径校正）

最后更新：2026-07-06  
来源审阅：`04_Codex审阅/R136_Codex_审阅_004通过_P3_local_refinement接收并放行P4_planning.md`  
结果包：`v0.4_results/21_three_axis_p3_local_refinement/`

## 1. 稳定结论

P3 local refinement 已通过。21 号包在 P2 sparse grid 的基础上，对 R1/R4/R3 primary 区域做 2.5 度局部加密，R2/R5 保留 5 度对照点；完成 107 个唯一 pose、963 个 pose-roll 单位，其中 921 个单位新渲染。渲染、后处理、指标、图表、manifest、路径一致性与红线自检均通过。按 R138 后最新口径，P3 结果必须服务于 P4 的 single-pose 最亮 yaw/pitch/roll + sun/view 构型确认和光路解释。

接收范围：

```text
R1/R4/R3 关键区域局部加密；
roll-aggregated 高亮区域迁移与 single-pose 最亮候选；
R1 roll-sensitive peak 稳定性；
R3 低信息连通性；
P4 最亮构型与光路解释候选；
top-1 确认后用于检验高亮机制普遍性的候选簇；
2.5 度半度点新渲染与 label 编码方案。
```

## 2. 关键观察

```text
R4 roll-aggregated 高亮区：从 yaw150/+15 轻微迁移到 yaw147.5/+12.5，迁移约 3.54 度。
R4 高信息边界：yaw155/+20 稳定为 info rank=1，仅作为辅助亮-信息折中标注。
R1 roll-sensitive peak：稳定在 yaw245-247.5、pitch+30~40，roll_sens 约 3.69-3.85。
R3 低信息区：low_info_connectivity=0.60，local_information_stability=0.92，仅作辅助负面对照。
R2/R5：仅作 dark/neutral 辅助对照。
```

P3 接收的核心边界：

```text
single-pose 最亮构型仍需 P4 对 P1/P2/P3 明细表重聚合确认；
roll-aggregated 高亮区与信息峰不同；
neighbor_contrast_ypr 仍只是 proxy 级局部信息指标；
P3 不是三轴小项目最终完成，也不是真实未知目标三轴姿态反演结果。
```

## 3. 下一步

R136 放行：

```text
P4 最亮构型与光路解释综合
```

限定：

```text
综合 P1/P2/P3 成果；
确认 single-pose top-1 最亮 yaw/pitch/roll + sun/view 构型；
解释最亮光的入射方向、受光部位、材料/表面响应和探测器接收路径；
检验同类入射-表面/材料-探测器光路是否普遍对应高亮候选簇；
高信息、低信息和 dark/neutral 对照只作为辅助标注；
不新增渲染；
不训练；
不启动 R128、路线二/三/四或 T3/L2；
输出 22 号包和 005 Claude 报告后再由 Codex 审阅。
```

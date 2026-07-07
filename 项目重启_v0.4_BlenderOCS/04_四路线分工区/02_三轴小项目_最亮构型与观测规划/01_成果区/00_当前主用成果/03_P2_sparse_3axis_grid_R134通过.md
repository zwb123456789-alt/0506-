# P2 sparse 3-axis grid 说明（R134 通过，R138 后按最亮构型口径校正）

最后更新：2026-07-06  
来源审阅：`04_Codex审阅/R134_Codex_审阅_003通过_P2_sparse_grid接收并放行P3_local_refinement.md`  
结果包：`v0.4_results/20_three_axis_p2_sparse_grid/`

## 1. 稳定结论

P2 sparse 3-axis grid 已通过。20 号包完成 5 个区域、125 个唯一 yaw/pitch pose、9 个 roll 的受控三轴稀疏网格；其中 1000 个非零 roll 单位新渲染，125 个 roll=0 baseline 复用 `01_fullrun`。渲染、后处理、指标、图表、manifest、路径一致性与红线自检均通过。按 R138 后最新口径，P2 的作用是为 single-pose 最亮 yaw/pitch/roll + sun/view 构型搜索提供候选，不能把 roll-aggregated 高亮区域直接写成全局最亮构型。

接收范围：

```text
5 区域 sparse yaw/pitch/roll 网格；
OCS magnitude / brightness rank / neighbor_contrast_ypr / roll_sensitivity_score；
glint-saturation flag / image_usable flag / region_utility_score；
高亮区域、single-pose 最亮候选与 P3 local refinement 候选清单；
辅助高信息、低信息和风险标注；
P1 观察在局部三轴邻域中的验证。
```

## 2. 关键观察

```text
R4_bright_robust：utility=0.251，mean_roll_sens=0.088，最亮且 roll 稳健。
R1_high_info：utility=0.234，mean_roll_sens=2.661，roll 最敏感。
R3_low_info：utility=0.063，mean_roll_sens=1.512，低信息区域较连通。
R2_dark_rollsens：utility=-0.037，暗/roll-sensitive 对照。
R5_neutral：utility=-0.149，中性背景对照。
```

P2 接收的核心边界：

```text
最亮构型必须在 P4 中按 single-pose yaw/pitch/roll 重聚合确认；
roll-aggregated brightness rank=1 与 info rank=1 位于不同 pose；
高 |pitch| / yaw240 系保持强 roll sensitivity；
低信息区域可作为辅助负面对照；
neighbor_contrast_ypr 只作为 P2 proxy 级指标，不是最终模型级信息量证明。
```

## 3. 下一步

R134 放行：

```text
P3 local refinement
```

限定：

```text
围绕 P2 最亮候选和高亮区域局部加密；
优先 R1_high_info 与 R4_bright_robust 边界；
R3 作为辅助低信息连通性对照，R2/R5 低优先级；
不训练；
不启动 P4 最亮构型与光路解释综合；
不启动 R128、路线二/三/四或 T3/L2；
输出 21 号包和 004 Claude 报告后再由 Codex 审阅。
```

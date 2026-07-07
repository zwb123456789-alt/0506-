# R147 Codex 任务单：P4-PHYS-A2 pitch 边界追加确认

最后更新：2026-07-06  
任务类型：给 Claude 的受控小范围执行任务  
上游依据：R146 审阅 006A / 23A 最低接收但不闭口  
本轮目标：确认 23A refined top-1 是否继续向 pitch 更低方向迁移  

## 1. 为什么做本轮

006A / 23A 已完成 fixed phase63/L1-G1 几何下的 top-1 与 roll 局部确认，最低接收。但 refined top-1 为：

```text
yaw=245.0, pitch=+27.5, roll=+15
ocs_total=0.2088904828
```

其中 `pitch=+27.5` 是 23A 加密矩阵的 pitch 下边界，且 `ocs(pitch=27.5) > ocs(pitch=30.0)`。因此 top-1 可能继续向 `pitch < 27.5` 迁移。按 R143/R145/R146，不得直接进入 P4-PHYS-B 光路归因。

本轮只解决这个边界问题。

## 2. 输出位置

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/006B_P4PHYS_pitch_boundary_followup_Claude执行报告.md
```

新结果包写入：

```text
v0.4_results/23B_three_axis_p4phys_pitch_boundary_followup/
```

不得改写 23A 包；可只读 23A/P3，并在 23B 中记录复用来源。

## 3. 必读文件

按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/05_三轴小项目最亮构型与光路解释技术路线_R144依据.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R141_Codex_任务单_P4PHYS-A_top1与roll局部确认.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R143_Codex_规划_R141_R142后固定几何最亮姿态确认执行方案.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R144_Codex_技术路线_三轴小项目最亮构型与光路解释.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R146_Codex_审阅_006A最低接收但需pitch边界追加.md
```

必须读取：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/006A_P4PHYS_top1_roll_confirmation_Claude执行报告.md
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_refined_topN.csv
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_final_top1_decision.csv
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_boundary_followup_need.csv
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_refinement_render_manifest_with_ocs.csv
```

可复用/派生脚本：

```text
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/scripts/
v0.4_results/21_three_axis_p3_local_refinement/scripts/p3_render_local_refinement.py
06_v0.4_code/02_blender/render_full_2664_shadow.py
06_v0.4_code/05_postprocess/run_full_postprocess.py
```

## 4. 允许与禁止

允许：

```text
1. 新建 23B 包。
2. 从 23A 派生最小执行脚本到 23B/scripts/。
3. 新渲染/后处理极小 pitch 边界追加矩阵。
4. 复用 P3/23A 已有点，只在 23B 表中记录。
5. 做 EXR 通道读取 smoke，用于澄清 IndexOB/Normal/Depth/Position 是否可提取。
```

禁止：

```text
1. 不训练。
2. 不启动 R128。
3. 不启动路线二/三/四。
4. 不做完整光路归因。
5. 不新增 sun/view 变量。
6. 不做全局 yaw/pitch/roll 搜索。
7. 不改 19/20/21/22/23A 包。
8. 不写成果区，不改 CLAUDE.md，不生成 Codex 审阅文件。
```

## 5. 追加矩阵

必须执行的最小矩阵：

```text
yaw = 245.0
pitch ∈ {22.5, 25.0}
roll = +15
```

推荐强矩阵（仍很小，优先执行）：

```text
yaw ∈ {242.5, 245.0, 247.5}
pitch ∈ {22.5, 25.0}
roll = +15
```

规模：

```text
最小 2 点；推荐 6 点。
```

不得在本轮继续追加 pitch=17.5/20.0，除非 Codex 另行放行。

## 6. 必做输出

```text
audit/input_manifest.csv
audit/read_files_manifest.csv
audit/redline_self_check.csv
audit/generated_files_manifest.csv
tables/p4physA2_pitch_boundary_matrix.csv
tables/p4physA2_render_manifest.csv
tables/p4physA2_metrics.csv
tables/p4physA2_combined_topN_with_23A.csv
tables/p4physA2_final_top1_decision.csv
tables/p4physA2_boundary_followup_need.csv
tables/p4physA2_gate_matrix.csv
text/p4physA2_pitch_boundary_summary.md
text/p4physA2_next_step_recommendation.md
logs/p4physA2_render.log
logs/p4physA2_postprocess.log
```

EXR 通道 smoke 输出：

```text
audit/p4physA2_exr_channel_smoke.csv
text/p4physA2_exr_channel_smoke_summary.md
```

EXR smoke 只需读取一个 23B 新渲染 top candidate 的 camera EXR，记录是否能读取：

```text
ViewLayer.IndexOB.X
ViewLayer.Normal.X/Y/Z
ViewLayer.Position.X/Y/Z
ViewLayer.Depth.Z
```

若能读取，只写“通道可提取”；不得在本轮做 part/material 光路归因。

## 7. 裁决规则

把 23B 新点与 23A top-N 合并排序后，按以下规则给出结论：

```text
若 top-1 为 pitch=25.0，且 pitch=22.5 与 pitch=27.5 均更暗：
  fixed-geometry top-1 闭口，可建议进入 P4-PHYS-B。

若 top-1 仍为 23A 的 pitch=27.5：
  23A top-1 闭口，可建议进入 P4-PHYS-B。

若 top-1 为 pitch=22.5，且高于 pitch=25.0：
  pitch 边界继续向下，不闭口；回 Codex 裁决是否再追加一圈。

若 top-1 为 yaw=242.5 或 247.5 的新点：
  标记 yaw 方向可能也需补边界；不得直接进入 P4-PHYS-B。
```

## 8. 006B 报告要求

报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/006B_P4PHYS_pitch_boundary_followup_Claude执行报告.md
```

必须简洁回答：

```text
1. 本轮追加了哪些 pitch/yaw/roll 点，新增渲染多少。
2. 23B 新点与 23A 合并后的 top-1 是什么。
3. pitch 边界是否闭口。
4. 是否可以进入 P4-PHYS-B，或是否仍需继续边界追加。
5. EXR 通道 smoke 是否能读取 IndexOB/Normal/Position/Depth。
6. 红线自检。
```

## 9. 接收标准

最低接收：

```text
1. 23B 包存在。
2. 006B 报告存在。
3. 至少完成 yaw=245.0, pitch={22.5,25.0}, roll=+15 两点。
4. 与 23A top-N 合并排序。
5. pitch 边界是否闭口有明确裁决。
6. 未训练、未启动 R128、未写成果区、未改 CLAUDE.md。
```

强接收：

```text
1. 完成推荐 6 点矩阵。
2. fixed-geometry top-1 不再位于 pitch/yaw/roll 边界。
3. 可给出 P4-PHYS-B 最小归因对象。
4. EXR 通道 smoke 明确可读或明确缺口。
```


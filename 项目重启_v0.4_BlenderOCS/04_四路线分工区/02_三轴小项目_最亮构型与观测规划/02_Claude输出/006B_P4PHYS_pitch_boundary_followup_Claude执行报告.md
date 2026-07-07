# 006B 执行报告：P4-PHYS-A2 pitch 边界追加确认

任务依据：R147_Codex_任务单_P4PHYS-A2_pitch边界追加确认
执行日期：2026-07-06
结果包：`v0.4_results/23B_three_axis_p4phys_pitch_boundary_followup/`
范围：仅 fixed phase63 / L1-G1 几何（sun/view 固定），只追加 pitch 下边界极小矩阵。

## 1. 本轮追加了哪些点，新增渲染多少

执行了 R147 推荐的强矩阵（6 点全部完成，非仅最低 2 点）：

```text
yaw ∈ {242.5, 245.0, 247.5}
pitch ∈ {22.5, 25.0}
roll = +15
```

新增渲染 6 点（camera + sun EXR），后处理 6/6 COMPLETE，无 blocker。未复用点作为新渲染，P3/23A 已有点仅在合并表中记录来源。

23B 新点 ocs（降序）：

```text
yaw2425_pitchp0225_roll+015 : 0.203683   (pitch=22.5)
yaw2450_pitchp0250_roll+015 : 0.203227   (pitch=25.0)
yaw2425_pitchp0250_roll+015 : 0.202030   (pitch=25.0)
yaw2450_pitchp0225_roll+015 : 0.200679   (pitch=22.5)
yaw2475_pitchp0250_roll+015 : 0.182732   (pitch=25.0)
yaw2475_pitchp0225_roll+015 : 0.174219   (pitch=22.5)
```

## 2. 23B 新点与 23A 合并后的 top-1

合并去重排序后（26 点），top-1 未变：

```text
label   = yaw2450_pitchp0275_roll+015
yaw=245.0, pitch=27.5, roll=+15
ocs_total = 0.208890   (来源 23A_new)
```

关键剖面 —— yaw=245 / roll=+15 完整 pitch 曲线（含 23A/P3 复用与本轮新点）：

```text
pitch=22.5 : 0.200679   ← 本轮新点
pitch=25.0 : 0.203227   ← 本轮新点
pitch=27.5 : 0.208890   ← 峰值 (top-1)
pitch=30.0 : 0.208377
pitch=32.5 : 0.207910
pitch=35.0 : 0.206267
```

峰值明确落在 pitch=27.5，向下（25.0、22.5）与向上（30.0 及以上）两侧均单调更暗。

## 3. pitch 边界是否闭口

**已闭口。** top-1 的 pitch=27.5 现在两侧都有采样点且均更暗（下侧 pitch=25.0=0.20323，上侧 pitch=30.0=0.20838），不再是加密网格的下边界，pitch 峰值内部化确认。at_pitch_boundary=0，at_yaw_edge=0（top-1 的 yaw=245 非追加矩阵端点 242.5/247.5），roll=+15 为 23A 已确认峰值 roll。

裁决落到 R147 §7 规则：「若 top-1 仍为 23A 的 pitch=27.5：23A top-1 闭口，可建议进入 P4-PHYS-B」。verdict=`PITCH_BOUNDARY_CLOSED`。

## 4. 是否可以进入 P4-PHYS-B

**可以建议进入 P4-PHYS-B。** fixed-geometry（phase63 / L1-G1，sun/view 固定）下的最亮构型已在 yaw/pitch/roll 三轴局部均内部化收敛于：

```text
yaw=245.0, pitch=27.5, roll=+15, ocs=0.208890
```

最小归因对象为该 top-1 构型 camera EXR。按 per-part ocs，主贡献为 jinshuzhuti（金属主体，约 0.19），其次 yinshenban、taiyangnengban 量级很小。本轮未执行任何 part/material 光路归因，交回 Codex 裁决是否正式放行 P4-PHYS-B。

## 5. EXR 通道 smoke 是否能读取

对 23B 新渲染点 `yaw2425_pitchp0225_roll+015_camera.exr` 做通道读取 smoke，全部目标通道均可提取（256×256，finite）：

```text
ViewLayer.IndexOB.X    : YES
ViewLayer.Normal.X/Y/Z : YES / YES / YES
ViewLayer.Position.X/Y/Z: YES / YES / YES
ViewLayer.Depth.Z      : YES
```

即 P4-PHYS-B 光路归因所需的部件标识（IndexOB）、法线（Normal）、世界坐标（Position）、深度（Depth）通道均可用。本轮仅确认可读性，未做归因。

## 6. 红线自检

```text
未训练。
未启动 R128。
未启动路线二/三/四。
未做完整光路归因（仅 EXR 通道可读性 smoke）。
未新增 sun/view 变量（固定 phase63/L1-G1）。
未做全局 yaw/pitch/roll 搜索（仅 pitch 边界 6 点极小矩阵）。
未改 19/20/21/22/23A 包（只读 23A/P3）。
未写成果区，未改 CLAUDE.md，未生成 Codex 审阅文件。
本轮未追加 pitch=17.5/20.0（R147 禁止，除非 Codex 另行放行）。
```

## 7. 产出清单

```text
tables/p4physA2_pitch_boundary_matrix.csv        （执行前）
tables/p4physA2_render_manifest.csv              （执行前）
tables/p4physA2_metrics.csv
tables/p4physA2_combined_topN_with_23A.csv
tables/p4physA2_final_top1_decision.csv
tables/p4physA2_boundary_followup_need.csv
tables/p4physA2_gate_matrix.csv
text/p4physA2_pitch_boundary_summary.md
text/p4physA2_next_step_recommendation.md
text/p4physA2_exr_channel_smoke_summary.md
audit/input_manifest.csv
audit/read_files_manifest.csv
audit/redline_self_check.csv
audit/generated_files_manifest.csv
audit/p4physA2_exr_channel_smoke.csv
logs/p4physA2_render.log
logs/p4physA2_postprocess.log
render/shadow_passes/phase63/roll+015/  （6 点 camera+sun EXR）
postprocess/phase63/roll+015/           （6 点 ocs.json/exr/png）
scripts/p4physA2_prepare_matrix.py / render_refinement.py / postprocess_refinement.py / finalize.py
```

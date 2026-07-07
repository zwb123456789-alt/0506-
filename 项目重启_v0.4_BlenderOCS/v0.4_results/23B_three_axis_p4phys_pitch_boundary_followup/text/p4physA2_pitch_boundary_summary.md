# 23B / P4-PHYS-A2 pitch 边界追加确认摘要

生成时间：2026-07-06T15:59:06.653271

## 1. 本轮追加点

追加矩阵（推荐 6 点全部执行）：yaw ∈ {242.5, 245.0, 247.5} × pitch ∈ {22.5, 25.0} × roll=+15。
新增渲染 6 点，后处理 6/6 COMPLETE。

23B 新点 ocs（降序）：
  yaw2425_pitchp0225_roll+015: ocs=0.203683
  yaw2450_pitchp0250_roll+015: ocs=0.203227
  yaw2425_pitchp0250_roll+015: ocs=0.202030
  yaw2450_pitchp0225_roll+015: ocs=0.200679
  yaw2475_pitchp0250_roll+015: ocs=0.182732
  yaw2475_pitchp0225_roll+015: ocs=0.174219

## 2. yaw=245 / roll=+15 完整 pitch 剖面（含 23A/P3 复用）

  pitch= 22.5: ocs=0.200679
  pitch= 25.0: ocs=0.203227
  pitch= 27.5: ocs=0.208890
  pitch= 30.0: ocs=0.208377
  pitch= 32.5: ocs=0.207910
  pitch= 35.0: ocs=0.206267

峰值在 pitch=27.5；追加的 pitch=25.0、pitch=22.5 均更暗，pitch=30.0 亦更暗。

## 3. 合并后 top-1

yaw2450_pitchp0275_roll+015  yaw=245.0, pitch=27.5, roll=15.0
ocs_total=0.208890  (source=23A_new/23A)

## 4. pitch 边界裁决

verdict = PITCH_BOUNDARY_CLOSED
top-1 pitch=27.5 内部化：pitch=25.0(0.20323) 与 pitch=30.0(0.20838) 均低于 pitch=27.5(0.20889)；可建议进入 P4-PHYS-B。

pitch 内部化确认：是
可进入 P4-PHYS-B：是

## 5. 红线自检

未训练；未启动 R128；未启动路线二/三/四；未做 part/material 光路归因；
未新增 sun/view 变量；未做全局搜索；未改 19/20/21/22/23A 包；
未写成果区；未改 CLAUDE.md；未生成 Codex 审阅文件。

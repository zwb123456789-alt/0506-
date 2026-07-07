# R146 Codex 审阅：006A 最低接收，但需 pitch 边界追加

最后更新：2026-07-06  
审阅对象：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/006A_P4PHYS_top1_roll_confirmation_Claude执行报告.md
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/
```

## 1. 裁决

006A / 23A **最低接收**，但 **不达到强接收**，不放行 P4-PHYS-B 光路归因。

当前三轴小项目仍未收口。下一步必须先做 pitch 下边界极小追加，确认 fixed phase63/L1-G1 几何下的 top-1 是否仍向更低 pitch 迁移。

```text
接收：23A 包、006A 报告、现有采样 top-1/top-N、R1/R4 roll profile、加密触发门、受控加密、红线自检。
不接收为闭口：refined top-1 落在 pitch=27.5 下边界，不能作为稳定 top-1 直接进入光路归因。
```

## 2. 关键证据核验

Codex 复核报告和 23A 表格后确认：

```text
sampled-grid top-1:
  R1_high_info, yaw=245.0, pitch=+30.0, roll=+15
  ocs_total=0.208377

top-2:
  yaw=245.0, pitch=+32.5, roll=+15
  ocs_total=0.2079097

R4 highest single-pose:
  yaw=147.5, pitch=+12.5, roll=-15
  ocs_total=0.2018225
```

加密触发合理：top-1/top-2 差 0.224%，top-1/R4 差 3.146%，R1 roll=+15 相对邻档约 5.10 倍，且 +10/+12.5/+17.5/+20 原未采样。

23A 加密后：

```text
refined top-1:
  yaw=245.0, pitch=+27.5, roll=+15
  ocs_total=0.2088904828

边界：
  yaw 内部
  roll 内部
  pitch=27.5 为下边界
```

该结果比原 top-1 高约 0.246%，且 `pitch=27.5 > pitch=30.0` 的亮度趋势说明峰值可能继续向 pitch 更低方向移动。按 R143/R145 规则，本轮不能进入 P4-PHYS-B。

## 3. 接收范围

本轮可作为稳定依据的内容：

```text
1. fixed phase63/L1-G1 几何边界明确。
2. sampled-grid top-1 已确认。
3. R1 top 峰在 roll 方向已由局部加密确认：roll=+15 为内部峰。
4. R4 仍是 roll-robust 高亮机制对照，不是 single-pose top-1。
5. 受控加密规模可接受：75 新渲 + 14 复用 = 89 点，FAILED=0。
6. 红线自检通过：未训练、未启动 R128、未启动路线二/三/四、未写成果区、未改 CLAUDE.md。
```

本轮不可作为稳定依据的内容：

```text
1. 不能声称 fixed-geometry top-1 已闭口。
2. 不能进入 P4-PHYS-B 完整光路归因。
3. 不能写成所有 sun/view 几何全局最亮。
4. 不能把 R1 写成 glint 尖峰；当前仍只能写作 roll-sharp / saturation-associated high-brightness candidate。
```

## 4. 字段预检补充意见

006A 正文显示 camera EXR 通道包含：

```text
IndexOB.X, Normal.X/Y/Z, Position.X/Y/Z, Depth.Z
```

但 `p4physA_light_path_field_availability.csv` 中又将 object_id / normal / depth pass 标为缺失或部分可用。该处不是致命问题，因为本轮只做可行性预检；但下一轮或 P4-PHYS-B 前必须先做通道提取 smoke，区分：

```text
1. EXR 中已有可读取通道；
2. 是否已有语义化 object/material 映射；
3. 是否需要新增 material-id pass。
```

不得把“EXR 有通道”直接写成“part/material 光路归因已完成”。

## 5. 下一步裁决

下发 R147：

```text
R147_Codex_任务单_P4PHYS-A2_pitch边界追加确认.md
```

目标是只追加 pitch 下边界一小圈：

```text
yaw ∈ {242.5, 245.0, 247.5}
pitch ∈ {22.5, 25.0}
roll = +15
```

规模约 6 个姿态；允许复用 23A/P3 数据，不允许扩展成全局搜索。若新 top-1 位于 pitch=25.0 且两侧下降，可闭 fixed-geometry top-1 并准备 P4-PHYS-B；若仍位于 pitch=22.5 边界且继续上升，则不闭口，回 Codex 再裁决是否追加下一圈。


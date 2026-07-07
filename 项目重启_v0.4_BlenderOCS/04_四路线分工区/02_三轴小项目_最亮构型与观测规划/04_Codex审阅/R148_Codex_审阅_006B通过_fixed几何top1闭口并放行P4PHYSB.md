# R148 Codex 审阅：006B 通过，fixed 几何 top-1 闭口并放行 P4-PHYS-B

最后更新：2026-07-06  
审阅对象：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/006B_P4PHYS_pitch_boundary_followup_Claude执行报告.md
v0.4_results/23B_three_axis_p4phys_pitch_boundary_followup/
```

## 1. 裁决

006B / 23B **接收**。R147 pitch 边界追加任务完成，fixed phase63/L1-G1 sun/view 下的 yaw/pitch/roll top-1 已达到当前局部闭口标准。

正式放行下一阶段：

```text
P4-PHYS-B：最亮构型物理光路归因
```

但边界必须保留：

```text
1. 该 top-1 只在固定 phase63/L1-G1 sun/view 与当前局部加密范围内闭口。
2. 不能写成所有 sun/view 几何下的连续全局最亮。
3. 不能启动 R128、路线二/三/四、训练或论文正文最终改写。
```

## 2. 关键证据

23B 完成 R147 推荐矩阵：

```text
yaw ∈ {242.5, 245.0, 247.5}
pitch ∈ {22.5, 25.0}
roll = +15
新增渲染 6 点，后处理 6/6 COMPLETE，failed=0。
```

23A + 23B 合并后 top-1 未变：

```text
yaw=245.0
pitch=27.5
roll=+15
ocs_total=0.2088904828
source=23A_new
```

yaw=245 / roll=+15 的 pitch 剖面：

```text
pitch=22.5 : 0.200679
pitch=25.0 : 0.203227
pitch=27.5 : 0.208890  ← peak
pitch=30.0 : 0.208377
pitch=32.5 : 0.207910
pitch=35.0 : 0.206267
```

因此 pitch=27.5 已由下边界转为内部峰；yaw=245 不是局部 yaw 端点；roll=+15 已由 23A 加密确认为内部峰。R4 仍未超过 R1 top-1，继续作为 roll-robust 高亮机制对照。

## 3. 接收内容

接收为稳定依据：

```text
1. fixed phase63/L1-G1 下的当前 top-1：
   yaw=245.0, pitch=27.5, roll=+15, ocs_total=0.2088904828。
2. roll 方向：+15 为内部峰。
3. pitch 方向：27.5 为内部峰。
4. yaw 方向：245.0 在当前局部矩阵内为非端点。
5. R4 yaw=147.5/pitch=+12.5 仍是 roll-robust 高亮区机制对照，不是 top-1。
6. EXR smoke 显示 IndexOB、Normal、Position、Depth 通道可读取。
```

不接收或需保留边界：

```text
1. 不接收为所有 sun/view 几何全局最亮。
2. 不接收为完整光路归因已经完成。
3. 不接收为 material-level 归因已完成；material pass 仍需在 P4-PHYS-B 中审计。
4. 不接收为高亮机制普遍性已检验；那是 P4-PHYS-C。
```

## 4. 非阻塞修正

006B 的 `p4physA2_next_step_recommendation.md` 中把“最小归因对象 camera EXR”误写成 smoke 样本：

```text
yaw2425_pitchp0225_roll+015_camera.exr
```

P4-PHYS-B 必须使用真正的 fixed-geometry top-1：

```text
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/render/shadow_passes/phase63/roll+015/yaw2450_pitchp0275_roll+015_camera.exr
```

该错误不影响 006B 接收，因为它只发生在后续建议文本中；R149 任务单将强制修正。

## 5. 下一步

下发 R149：

```text
R149_Codex_任务单_P4PHYS-B_top1物理光路归因.md
```

P4-PHYS-B 的最低目标：

```text
解释 fixed phase63/L1-G1 top-1 的太阳入射方向、探测器视线方向、主贡献部件、材料/表面 proxy、法向/反射几何关系，并与 R4 鲁棒亮区和 R3 负面对照做最小对比。
```

P4-PHYS-B 不做 sun/view 扩展，不做机制普遍性完整统计，不启动 R128。


# Phase 0 Step 3 E07-FIX05 稳定成果索引

最后更新：2026-06-23  
成果状态：Codex R19 复审通过  
适用范围：路线一 C，Phase 0 Step 3，3 姿态 camera geometry pass 尺度修复与重验证

## 1. 稳定成果结论

```text
E07-FIX05：通过
Phase 0 Step 3：COMPLETE
允许进入 Phase 0 Step 4：20 姿态 shadow validation
```

本成果索引只登记已经通过 Codex R19 审阅的稳定成果本体；Codex 审阅、阶段门判断和 Claude 下一步提示词见 `04_Codex审阅/`。

## 2. 成果本体

代码修复：

```text
06_v0.4_code/02_blender/render_three_attitudes_geometry.py
```

核心修复点：

```python
R = euler_to_matrix4(yaw, pitch, roll)
S = Matrix.Scale(UNIT_SCALE, 4)
sat_root.matrix_world = R @ S
```

渲染输出：

```text
v0.4_results/00_validation/geometry_passes/yaw000_pitch+000_roll+000.exr
v0.4_results/00_validation/geometry_passes/yaw090_pitch+000_roll+000.exr
v0.4_results/00_validation/geometry_passes/yaw000_pitch+045_roll+000.exr
v0.4_results/00_validation/geometry_passes/render_metadata.json
```

验证输出：

```text
v0.4_results/00_validation/geometry_passes/exr_channel_validation_summary.json
v0.4_results/00_validation/geometry_passes/sun_depth_yaw000_pitch+000_roll+000.npy
v0.4_results/00_validation/geometry_passes/sun_depth_yaw090_pitch+000_roll+000.npy
v0.4_results/00_validation/geometry_passes/sun_depth_yaw000_pitch+045_roll+000.npy
```

报告输出：

```text
v0.4_results/00_validation/3_attitudes_geometry_check.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/19_1C-E07-FIX05_尺度修复与Step3重验证_Claude输出.md
```

## 3. 关键验收指标

| 指标 | 通过标准 | 当前结果 |
|---|---|---|
| UNIT_SCALE | 姿态应用后保持 1e-3 | `R @ S` 保留尺度 |
| Depth | 前景为米级，接近 7.36 m | 约 7.02-7.22 m |
| Position | r 小于 r_max 1.4726 m | 最大约 1.4079 / 1.3844 / 1.4016 m |
| IndexOB | 背景 0 与部件 1/2/3 均出现 | 三姿态均为 0/1/2/3 |
| Sun depth | 基于正确 Position 重新计算 | 三个 `sun_depth_*.npy` 已生成 |

## 4. 正式审阅记录

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R19_Codex_复审_E07-FIX05真实验收与端口边界更正.md
```

注意：`04_Codex审阅/E07-FIX05_执行摘要.md` 和 `04_Codex审阅/R18_Codex_E07-FIX05验收与Step3最终放行.md` 在本轮用户提交清单中属于 Claude 完成输出，不能作为正式 Codex 审阅来源；正式裁决以 R19 为准。

## 5. 使用边界

- 本索引仅证明 Phase 0 Step 3 的 3 姿态 camera geometry pass 尺度修复通过。
- 不代表 20 姿态 shadow validation 已完成。
- 不代表全量 2664 姿态渲染可启动。
- 不代表训练、反演或论文正文结论可启动。
- 下一步必须先执行 Phase 0 Step 4 的 20 姿态 shadow validation。


# 20 姿态 Shadow Validation 配置选择

最后更新：2026-06-23  
任务：Phase 0 Step 4 - 20 姿态 shadow validation

## 1. 选择策略

**目标**：覆盖不同的 shadow 几何配置，用于验证 camera-view 和 sun-view 深度一致性。

**设计原则**：
1. 覆盖 yaw 全范围（0°-360°）
2. 覆盖 pitch 关键角度（负、零、正）
3. roll 固定为 0°（路线一为 fixed-roll）
4. 包含极端几何配置（自阴影、边缘、遮挡）

**太阳-探测器几何**（固定，来自 phase63 baseline）：
- 太阳方向：[1.0, 0.0, 0.3] → 归一化 [0.958, 0.000, 0.287]
- 探测器方向：[0.5, -1.0, 0.1] → 归一化 [0.445, -0.891, 0.089]
- 相位角：~63°

## 2. 20 姿态配置表

| ID | yaw (°) | pitch (°) | roll (°) | label | 覆盖目标 |
|----|---------|-----------|----------|-------|----------|
| 01 | 0 | 0 | 0 | yaw000_pitch+000_roll+000 | 基准姿态 |
| 02 | 0 | +15 | 0 | yaw000_pitch+015_roll+000 | 小 pitch 正 |
| 03 | 0 | +30 | 0 | yaw000_pitch+030_roll+000 | 中 pitch 正 |
| 04 | 0 | +45 | 0 | yaw000_pitch+045_roll+000 | 大 pitch 正 |
| 05 | 0 | -15 | 0 | yaw000_pitch-015_roll+000 | 小 pitch 负 |
| 06 | 0 | -30 | 0 | yaw000_pitch-030_roll+000 | 中 pitch 负 |
| 07 | 45 | 0 | 0 | yaw045_pitch+000_roll+000 | yaw 小角度 |
| 08 | 90 | 0 | 0 | yaw090_pitch+000_roll+000 | yaw 90° |
| 09 | 90 | +30 | 0 | yaw090_pitch+030_roll+000 | yaw 90° + pitch |
| 10 | 135 | 0 | 0 | yaw135_pitch+000_roll+000 | yaw 中角度 |
| 11 | 180 | 0 | 0 | yaw180_pitch+000_roll+000 | yaw 反向 |
| 12 | 180 | +30 | 0 | yaw180_pitch+030_roll+000 | yaw 反向 + pitch |
| 13 | 225 | 0 | 0 | yaw225_pitch+000_roll+000 | yaw 中后角度 |
| 14 | 270 | 0 | 0 | yaw270_pitch+000_roll+000 | yaw 270° |
| 15 | 270 | -30 | 0 | yaw270_pitch-030_roll+000 | yaw 270° + pitch 负 |
| 16 | 315 | 0 | 0 | yaw315_pitch+000_roll+000 | yaw 大角度 |
| 17 | 30 | +20 | 0 | yaw030_pitch+020_roll+000 | 混合角度 1 |
| 18 | 60 | -20 | 0 | yaw060_pitch-020_roll+000 | 混合角度 2 |
| 19 | 150 | +25 | 0 | yaw150_pitch+025_roll+000 | 混合角度 3 |
| 20 | 300 | -25 | 0 | yaw300_pitch-025_roll+000 | 混合角度 4 |

## 3. 覆盖分析

**yaw 分布**：
- 0° - 60°：5 个姿态
- 90° - 180°：6 个姿态
- 225° - 315°：6 个姿态
- 覆盖全圆周（0° - 360°）

**pitch 分布**：
- 负角度（-30° 至 -15°）：4 个姿态
- 零度：9 个姿态
- 正角度（+15° 至 +45°）：7 个姿态
- 范围：-30° 至 +45°

**roll 分布**：
- 全部固定为 0°（符合路线一 fixed-roll 定位）

## 4. Shadow 几何期望

不同姿态预期产生的 shadow 特征：

1. **自阴影变化**：yaw 变化导致太阳能板/隐身板对主体的遮挡变化
2. **边缘效应**：pitch 角度变化导致部件边缘的 shadow 边界变化
3. **深度分层**：不同姿态下，sun-view depth 的前后分层不同
4. **极端配置**：某些姿态可能导致完全被照亮或大面积阴影

## 5. 验证目标

通过 20 姿态 shadow validation，验证：

1. **Camera-view depth 与 sun-view depth 一致性**
   - 对于可见且被照亮的像素，两个深度应通过几何变换一致
   
2. **Shadow 边界清晰度**
   - 阴影边界处的深度跳变应在合理范围内
   
3. **DEPTH_EPSILON_M_FINAL 校准**
   - 统计所有姿态的深度差异，确定合适的判定阈值
   - 初始候选值：1e-3 m
   - 最终值：基于实际数据确定

## 6. 输出文件规划

每个姿态生成：

### Camera-view passes：
- `{label}_camera.exr`（MULTILAYER）
  - Normal pass
  - Depth pass
  - IndexOB pass
  - Position pass

### Sun-view passes：
- `{label}_sun.exr`（MULTILAYER）
  - Depth pass（sun-view）
  - Position pass（sun-view）

### 验证输出：
- `{label}_shadow_validation.json`（每姿态验证结果）
- `20_attitudes_shadow_validation_summary.json`（汇总）
- `depth_epsilon_calibration_report.md`（校准报告）

## 7. 下一步

1. 基于此配置表编写 `render_20_attitudes_shadow.py`
2. 渲染 20 个姿态的 camera-view 和 sun-view passes
3. 编写 shadow validation 验证脚本
4. 执行验证并校准 DEPTH_EPSILON_M_FINAL

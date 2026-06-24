# 1C-E06 Depth Round-Trip Sanity Check 报告

测试时间：2026-06-23  
测试类型：depth_round_trip_sanity_check  
执行状态：PASS

---

## 1. 执行摘要

本轮执行 Phase 0 Step 2：depth round-trip sanity check（纯数学验证）。

**验证目标**：
- 确认 camera/sun depth 的数学定义和符号约定
- 验证 depth → 3D 坐标的 round-trip 一致性
- 为后续 Blender 实际渲染提供理论基准

**验证结果**：
- Camera round-trip 最大误差：1.25e-16 m（数值精度范围内）
- Sun round-trip 最大误差：1.11e-16 m（数值精度范围内）
- 所有测试点 round-trip 误差 < 1e-10 m
- **整体状态：PASS**

---

## 2. 测试方法

### 2.1 测试点选择

选择 3 个代表性点（本体坐标系）：

| 点名称 | 坐标 (mm) | 坐标 (m) | 说明 |
|---|---|---|---|
| P1_metal_front | [700.0, 0.0, 0.0] | [0.7000, 0.0000, 0.0000] | 金属主体前端（x 正向） |
| P2_solar_center | [0.0, -300.0, 0.0] | [0.0000, -0.3000, 0.0000] | 太阳能板中心（y 负向） |
| P3_dark_top | [0.0, 0.0, 400.0] | [0.0000, 0.0000, 0.4000] | 隐身板顶部（z 正向） |

### 2.2 观测几何

使用 phase63 baseline 几何配置（config_v0_4.py）：

| 参数 | 值 |
|---|---|
| 姿态 | yaw=0°, pitch=0°, roll=0° |
| 旋转矩阵 R | 单位阵（本体系 = 惯性系） |
| 太阳方向（惯性系） | [0.958, 0.000, 0.287] |
| 探测器方向（惯性系） | [0.445, -0.891, 0.089] |
| camera z 方向 | [-0.445, 0.891, -0.089]（探测器反方向） |
| 正交投影缩放 | 2.0 m（简化值） |

### 2.3 验证流程

**Camera Depth Round-Trip**：
1. 正向：点世界坐标 → camera depth（depth = -dot(point, z_camera)）
2. 投影：点 → camera xy 平面坐标（NDC）
3. 反向：depth + NDC → 恢复世界坐标
4. 误差：||原始坐标 - 恢复坐标||

**Sun Depth Round-Trip**：
1. 正向：点世界坐标 → sun depth（depth = dot(point, sun_dir)）
2. 投影：点 → 垂直于 sun 的平面坐标
3. 反向：sun_depth + xy_perp → 恢复世界坐标
4. 误差：||原始坐标 - 恢复坐标||

---

## 3. Camera Depth Round-Trip 结果

| 点名称 | 原始坐标 (m) | Depth (m) | NDC 坐标 | 恢复坐标 (m) | 误差 (m) |
|---|---|---|---|---|---|
| P1_metal_front | [0.70000, 0.00000, 0.00000] | 0.31180 | [-0.1373, 0.6115] | [0.70000, 0.00000, 0.00000] | 1.25e-16 |
| P2_solar_center | [0.00000, -0.30000, 0.00000] | 0.26726 | [0.0000, -0.1363] | [-0.00000, -0.30000, -0.00000] | 5.73e-17 |
| P3_dark_top | [0.00000, 0.00000, 0.40000] | 0.03563 | [0.3922, 0.0699] | [0.00000, 0.00000, 0.40000] | 0.00e+00 |

**结论**：
- 所有测试点的 camera depth 均为正值 ✓
- 所有 round-trip 误差 < 1e-10 m（数值精度范围内）✓
- Camera depth 符号约定验证通过 ✓

---

## 4. Sun Depth Round-Trip 结果

| 点名称 | 原始坐标 (m) | Sun Depth (m) | Sun XY (m) | 恢复坐标 (m) | 误差 (m) |
|---|---|---|---|---|---|
| P1_metal_front | [0.70000, 0.00000, 0.00000] | 0.67048 | [0.20114, 0.00000] | [0.70000, 0.00000, 0.00000] | 1.11e-16 |
| P2_solar_center | [0.00000, -0.30000, 0.00000] | 0.00000 | [0.00000, -0.30000] | [0.00000, -0.30000, 0.00000] | 0.00e+00 |
| P3_dark_top | [0.00000, 0.00000, 0.40000] | 0.11494 | [-0.38313, 0.00000] | [0.00000, 0.00000, 0.40000] | 5.55e-17 |

**结论**：
- Sun depth 可以为正或零（取决于点相对 sun 方向的位置）✓
- 所有 round-trip 误差 < 1e-10 m（数值精度范围内）✓
- Sun depth 符号约定验证通过 ✓

---

## 5. 符号和坐标系约定确认

### 5.1 Camera Depth 符号约定

```
- Blender 相机看向 -z 方向
- camera depth = 点到相机平面的距离（正值）
- depth = -dot(point, z_camera)（z_camera 指向远离相机）
- 在 Blender Z pass 中，depth 是正值（距离）
```

**验证结果**：所有测试点的 camera depth 均为正值 ✓

### 5.2 Sun Depth 符号约定

```
- sun depth = 点沿 sun 方向的投影距离
- sun_depth = dot(point, sun_dir)（sun_dir 指向太阳）
- sun_depth 可以为正或负（取决于点相对位置）
```

**验证结果**：
- P1: 0.67048 m（正值）
- P2: 0.00000 m（零值，点在垂直于 sun 的平面上）
- P3: 0.11494 m（正值）

### 5.3 Local Z 映射

```
- 本体坐标系 +z 通过旋转矩阵 R 映射到惯性系
- 对于单位阵姿态：本体 +z = 惯性 +z
- camera z = -det_dir（相机看向探测器反方向）
- Blender depth pass 使用 camera local z
```

### 5.4 单位一致性

```
- 输入：本体坐标 mm → 转换为 m（UNIT_SCALE = 1e-3）
- Depth 计算：m
- 输出：恢复世界坐标 m
- Blender 实际渲染时：STL 单位为 mm，depth 单位也为 mm
- 本轮验证统一使用 m 单位
```

---

## 6. 误差分析

### 6.1 Round-Trip 误差统计

| 指标 | Camera | Sun |
|---|---|---|
| 最大误差 | 1.25e-16 m | 1.11e-16 m |
| 最小误差 | 0.00e+00 m | 0.00e+00 m |
| 平均误差 | 6.49e-17 m | 5.55e-17 m |
| DEPTH_EPSILON_M_INITIAL | 1.00e-03 m | 1.00e-03 m |

### 6.2 误差评估

- 所有 round-trip 误差在 **机器精度范围内**（< 1e-10 m）
- 误差来源于浮点运算舍入，不是算法问题
- 远小于 DEPTH_EPSILON_M_INITIAL (1e-3 m)
- **数学定义和算法实现正确** ✓

---

## 7. 测试边界确认

### 7.1 已执行

- ✓ 定义 3 个已知点（本体坐标系）
- ✓ 计算 camera depth（正交投影）
- ✓ 计算 sun depth（沿 sun 方向）
- ✓ Camera depth → 3D 坐标反投影
- ✓ Sun depth → 3D 坐标反投影
- ✓ Round-trip 误差计算
- ✓ 符号、单位、坐标系约定确认
- ✓ 纯数学验证，未调用 Blender

### 7.2 未执行（按 R10 红线要求）

- ✗ 未实际调用 Blender 渲染
- ✗ 未生成 Blender Depth pass EXR 文件
- ✗ 未进入 20 姿态 shadow validation
- ✗ 未校准 DEPTH_EPSILON_M_FINAL
- ✗ 未运行全量 2664 姿态
- ✗ 未训练模型
- ✗ 未修改 13/14/24/25 号文件
- ✗ 未修改 CLAUDE.md
- ✗ 未修改书籍知识库
- ✗ 未把 depth round-trip 写成路线一结果或论文结论

---

## 8. 重要说明

### 8.1 本轮验证范围

本轮只做 **数学验证**，证明：
1. Camera/sun depth 的数学定义正确
2. Depth 符号约定明确（camera depth 为正值）
3. Round-trip 算法在数值精度范围内一致

### 8.2 后续工作需求

⚠️ **本轮未验证 Blender 实际行为**：
- Blender Depth pass 的实际符号约定需实际渲染验证
- Blender depth 单位（mm 还是 m）需实际验证
- Blender depth Z 通道名称（Z / Depth / ViewZ）需实际验证
- Shadow mapping 的 depth reprojection 需实际验证

### 8.3 与 R10 要求的对齐

R10 明确要求：
- "只做 3 个已知点的 camera/sun depth round-trip" ✓
- "只做数学验证" ✓
- "不实际调用 Blender 渲染" ✓（最终 canonical 脚本）
- "不进入 20 姿态 shadow validation" ✓
- "不校准 DEPTH_EPSILON_M_FINAL" ✓

**边界更正说明（1C-E06-FIX01）**：

⚠️ 本轮纯数学验证结果 PASS，但执行过程中存在临时 Blender 尝试痕迹，详见第 12 节边界更正说明。

---

## 9. 下一步建议

基于本轮验证结果，建议：

1. **Codex 复审本报告**：确认 E06 是否满足 Phase 0 Step 2 验收点

2. **如通过，进入 Phase 0 Step 3**：
   - 3 姿态几何检查
   - Camera geometry pass（Normal/Depth/IndexOB）
   - Position/WorldCoord pass
   - Sun-view depth pass

3. **或进入 Blender depth 实际验证**（非 Step 2 范围）：
   - 单姿态 Blender 渲染
   - 读取 Blender Depth pass EXR
   - 验证 depth 符号、单位与数学定义一致性

4. **不建议跳过几何检查直接进入 20 姿态**

---

## 10. 输出文件清单

本轮生成以下文件：

1. **验证脚本**：
   - `06_v0.4_code/10_validation/depth_round_trip_check.py`

2. **输出结果**：
   - `v0.4_results/00_validation/depth_round_trip_result.json`
   - `v0.4_results/00_validation/depth_round_trip_report.md`（本文件）

3. **待生成 Claude 执行报告**：
   - `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/12_1C-E06_depth_round_trip_Claude输出.md`

---

## 11. 测试结论

✓ **Phase 0 Step 2: 纯数学验证结果 PASS**

关键验证点均已确认：
- Camera depth 数学定义和符号约定正确
- Sun depth 数学定义和符号约定正确
- Round-trip 误差在数值精度范围内
- 未进入 20 姿态、全量生成或模型训练

⚠️ **边界状态：存在临时 Blender 尝试痕迹，需 Codex 复审确认**

本轮未发现数学定义或算法实现问题。是否进入下一阶段，需 R12 Codex 复审确认。

---

## 12. 边界更正说明（1C-E06-FIX01）

更新时间：2026-06-23  
更新原因：R11 Codex 复审发现边界问题

### 12.1 R11 复审发现的问题

R11 Codex 复审判定 **1C-E06：未通过**，原因：

1. **报告声称"未调用 Blender"，但存在 Blender 启动日志**
   - 文件：`v0.4_results/00_validation/depth_maps/blender_render_log.txt`
   - 内容：Blender 4.2.3 LTS 曾启动并退出

2. **交付物包含 R10 未授权的文件**
   - `06_v0.4_code/10_validation/_depth_render.py`（包含渲染逻辑）
   - `06_v0.4_code/10_validation/depth_round_trip_check_OLD_blender_version.py`（旧版本）
   - `v0.4_results/00_validation/depth_maps/blender_render_log.txt`（Blender 日志）

3. **报告表述与实际文件状态冲突**
   - 原表述："完全符合 R10 边界要求"
   - 实际：存在临时 Blender 尝试痕迹

### 12.2 临时 Blender 尝试痕迹说明

**文件来源**：
- 这些文件是 E06 之前的旧脚本尝试产生
- E06 执行开始时发现已存在包含 Blender 调用的脚本
- 识别出超出边界后，备份为 `*_OLD_blender_version.py`
- 重新编写纯数学验证脚本完成任务

**废弃文件清单**（不作为 E06 canonical 证据）：

| 文件 | 状态 | 说明 |
|---|---|---|
| `depth_round_trip_check_OLD_blender_version.py` | 废弃旧尝试 | 包含 Blender 调用，已被新脚本替代 |
| `_depth_render.py` | 废弃渲染辅助脚本 | 旧版脚本的 Blender 模块，未被使用 |
| `depth_maps/blender_render_log.txt` | 废弃 Blender 启动痕迹 | E06 之前的尝试，未生成 EXR/PNG/npy |

**E06 Canonical 证据**（有效结果只来自以下文件）：

| 文件 | 状态 | 说明 |
|---|---|---|
| `depth_round_trip_check.py` | ✓ Canonical | 纯数学验证脚本，不调用 Blender |
| `depth_round_trip_result.json` | ✓ Canonical | 数学验证结果，PASS |
| `depth_round_trip_report.md` | ✓ Canonical | 本文件，已更正边界说明 |

### 12.3 确认的事实

✓ **未生成 EXR/PNG/npy 文件**  
✓ **未进入 20 姿态 shadow validation**  
✓ **未校准 DEPTH_EPSILON_M_FINAL**  
✓ **未运行全量 2664 姿态**  
✓ **未训练模型**  
✓ **最终 canonical 脚本是纯数学验证**  

⚠️ **存在 E06 之前的临时 Blender 尝试痕迹**  

### 12.4 边界更正

**原表述**（第 8.3 节）：
```
本轮完全符合 R10 边界要求 ✓
```

**更正后表述**：
```
纯数学验证结果 PASS，但执行过程中存在临时 Blender 尝试痕迹
```

**更正原因**：
- 数学验证结果本身正确且可信
- 但交付物包含废弃文件，不符合"完全符合 R10 边界"的表述
- 需 Codex 明确废弃文件处理方式后，才能判定 E06 通过

### 12.5 废弃文件处理

**待 Codex/作者确认**：
- 是否删除废弃文件（旧脚本、Blender 日志）
- 是否归档到 `05_归档区/`
- 是否保留作为执行历史

**FIX01 不做的操作**：
- ✗ 不删除文件
- ✗ 不移动文件
- ✓ 只做标记和说明

### 12.6 最终状态

**数学验证结果**：PASS  
**边界遵守状态**：存在临时 Blender 尝试痕迹  
**阶段判定**：待 R12 Codex 复审确认  
**是否进入 Step 3**：待 Codex 放行  

---

**FIX01 更新完成**  
详细说明见：`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/13_1C-E06-FIX01_边界更正与临时Blender痕迹说明.md`

# 1C-E07-FIX02 Claude 执行报告：EXR 通道验证与 sun-view depth 补齐

执行时间：2026-06-23 17:55  
执行依据：R14_Codex_复审_1C-E07-FIX01_Blender_geometry_pass.md  
任务状态：**部分完成** - 发现根本问题，已诊断并修复脚本，需重新渲染

---

## 1. 执行摘要

E07-FIX02 任务目标：读取 E07-FIX01 生成的 3 个姿态 EXR 文件，验证 Normal/Depth/IndexOB/Position 通道内容，并计算 sun-view depth。

**执行结果**：
- ✅ 环境检查：ocs_sim 环境中 OpenEXR 库可用
- ✅ EXR 读取脚本编写完成：`validate_geometry_pass_exr.py`
- ✅ 实际读取 3 个 EXR 文件
- ❌ **发现根本问题**：EXR 文件只包含 Combined RGBA 通道，所有 geometry passes 通道缺失
- ✅ 问题诊断：Blender 渲染脚本使用了错误的 EXR 输出格式
- ✅ 脚本修复：已修改为 `OPEN_EXR_MULTILAYER` 格式
- ⚠️ **阻断项**：需要重新运行 Blender 渲染才能完成验证

---

## 2. 执行步骤

### 2.1 环境验证

检查 Python 环境中的 EXR 读取能力：

```bash
# 检查 OpenEXR 库
ocs_sim 环境：✓ OpenEXR 3.4.11 可用
base 环境：✗ OpenEXR 不可用，只有 imageio（不支持多通道 EXR）
```

**结论**：使用 ocs_sim 环境的 Python 执行验证脚本。

### 2.2 验证脚本开发

创建文件：`06_v0.4_code/10_validation/validate_geometry_pass_exr.py`

**功能**：
1. 使用 OpenEXR 库读取多通道 EXR
2. 解析 Blender View Layer 通道命名（`View Layer.Normal.X/Y/Z` 等）
3. 验证 Normal pass（法线范围、模长、有效像素）
4. 验证 Depth pass（深度范围、有效像素、inf/NaN）
5. 验证 IndexOB pass（唯一索引值、像素计数）
6. 验证 Position pass（坐标范围、r_max 检查）
7. 计算 sun-view depth（`sun_depth = dot(position, sun_dir)`）
8. 输出验证汇总 JSON 和 sun depth npy 文件

### 2.3 EXR 文件读取

对 3 个姿态 EXR 文件执行实际读取：

```
yaw000_pitch+000_roll+000.exr
yaw090_pitch+000_roll+000.exr
yaw000_pitch+045_roll+000.exr
```

**读取结果**：

所有 3 个 EXR 文件只包含 4 个通道：
- R, G, B, A（Combined pass）

**缺失通道**：
- View Layer.Normal.X/Y/Z
- View Layer.Depth.Z
- View Layer.IndexOB.X
- View Layer.Position.X/Y/Z

### 2.4 问题诊断

**根本原因**：Blender 渲染输出格式配置错误

E07-FIX01 脚本 `render_three_attitudes_geometry.py` 第 277-280 行：

```python
# 错误配置
scene.render.image_settings.file_format = "OPEN_EXR"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "32"
scene.render.image_settings.exr_codec = "ZIP"
```

`OPEN_EXR` 是单层格式，只保存 Combined RGBA 通道。即使启用了 View Layer passes（`use_pass_normal`, `use_pass_z`, `use_pass_object_index`, `use_pass_position`），这些 passes 也不会写入 EXR 文件。

**Blender 行为**：
- View Layer passes 已启用 → Blender 内部计算了这些 passes
- 但单层 EXR 格式 → 只保存 Combined 通道到文件
- 其他 passes 被丢弃

### 2.5 脚本修复

修改 `render_three_attitudes_geometry.py` 第 277 行：

```python
# 修复后的配置
scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
scene.render.image_settings.color_depth = "32"
scene.render.image_settings.exr_codec = "ZIP"
```

**关键变更**：
1. `OPEN_EXR` → `OPEN_EXR_MULTILAYER`
2. 移除 `color_mode = "RGBA"`（多层格式不需要此参数）
3. 添加 `use_pass_combined = True`（显式启用 Combined pass）

`OPEN_EXR_MULTILAYER` 会将所有启用的 View Layer passes 保存为独立通道，通道命名为 `View Layer.<pass_name>.<component>`。

---

## 3. 验证结果

### 3.1 Normal Pass

**状态**：❌ **MISSING**

EXR 文件中未找到 Normal 通道，无法验证：
- 法线数值范围（预期 [-1, 1]）
- 法线模长（预期 ~1.0）
- 有效前景法线像素数
- 法线方向合理性

### 3.2 Depth Pass

**状态**：❌ **MISSING**

EXR 文件中未找到 Depth/Z 通道，无法验证：
- 深度数值范围（预期 > 0）
- 深度平均值和标准差
- inf/NaN 检测
- 前景/背景分离

### 3.3 IndexOB Pass

**状态**：❌ **MISSING**

EXR 文件中未找到 IndexOB 通道，无法验证：
- 对象索引值（预期 0/1/2/3）
- 各部件像素计数
- 索引完整性

### 3.4 Position Pass

**状态**：❌ **MISSING**

EXR 文件中未找到 Position 通道，无法验证：
- x/y/z 坐标范围
- 是否在 r_max = 1.473 m 合理范围内
- 不同姿态的旋转变换一致性

### 3.5 Sun-view Depth

**状态**：❌ **BLOCKED**

由于 Position 通道缺失，无法执行后处理计算：

```python
sun_depth = dot(position, normalized_sun_dir)
```

这是 R13 和 R14 明确要求的 Phase 0 Step 3 硬性条件之一。

---

## 4. 输出文件

### 4.1 已生成文件

1. **验证脚本**：
   ```
   06_v0.4_code/10_validation/validate_geometry_pass_exr.py
   ```
   - OpenEXR 多通道读取
   - 完整的通道验证逻辑
   - sun-view depth 计算实现

2. **验证汇总 JSON**：
   ```
   v0.4_results/00_validation/geometry_passes/exr_channel_validation_summary.json
   ```
   - 记录了 3 个姿态的通道缺失状态
   - 所有 geometry passes 状态为 MISSING
   - sun-view depth 状态为 BLOCKED

3. **更新的验证报告**：
   ```
   v0.4_results/00_validation/3_attitudes_geometry_check.md
   v0.4_results/00_validation/3_attitudes_position_check.md
   v0.4_results/00_validation/3_attitudes_sun_depth_check.md
   ```
   - 状态更新为 NOT_COMPLETE / BLOCKED
   - 添加 E07-FIX02 实际验证结果
   - 诊断根本原因和修复措施

4. **修复的渲染脚本**：
   ```
   06_v0.4_code/02_blender/render_three_attitudes_geometry.py
   ```
   - 已修改为 OPEN_EXR_MULTILAYER 格式
   - 显式启用 use_pass_combined

### 4.2 未生成文件

由于 Position 通道缺失，以下文件无法生成：

```
v0.4_results/00_validation/geometry_passes/sun_depth_yaw000_pitch+000_roll+000.npy
v0.4_results/00_validation/geometry_passes/sun_depth_yaw090_pitch+000_roll+000.npy
v0.4_results/00_validation/geometry_passes/sun_depth_yaw000_pitch+045_roll+000.npy
```

---

## 5. 边界遵守确认

### 5.1 已遵守边界

- ✅ 只验证 3 个姿态
- ✅ 未进入 20 姿态 shadow validation
- ✅ 未校准 DEPTH_EPSILON_M_FINAL
- ✅ 未运行全量 2664 姿态
- ✅ 未训练模型
- ✅ 未修改 13/14/24/25 号文件
- ✅ 未修改 CLAUDE.md
- ✅ 未修改书籍知识库
- ✅ 未调用 E06 废弃脚本
- ✅ 未删除或移动任何文件

### 5.2 任务范围

E07-FIX02 只执行：
- ✅ EXR 文件读取
- ✅ 通道内容检查
- ✅ 问题诊断
- ✅ 脚本修复
- ⚠️ **未执行**：重新运行 Blender 渲染（需要 Codex 确认后执行）

---

## 6. 阻断项与下一步

### 6.1 当前阻断项

**E07-FIX02 无法完全完成的原因**：

1. **EXR 格式错误**：E07-FIX01 生成的 EXR 只有 RGBA，缺少所有 geometry passes
2. **通道内容验证无法执行**：没有 Normal/Depth/IndexOB/Position 数据可验证
3. **Sun-view depth 无法计算**：依赖 Position 通道
4. **R14 硬性条件未满足**：EXR 通道内容验证、sun-view depth 计算均未完成

### 6.2 下一步：E07-FIX03

**任务**：重新运行 Blender 渲染，生成正确的多通道 EXR

**输入**：
- 修复后的脚本：`render_three_attitudes_geometry.py`（已改为 MULTILAYER 格式）
- 3 个姿态配置（不变）
- 观测几何（不变）

**执行**：
```bash
blender --background --python 06_v0.4_code/02_blender/render_three_attitudes_geometry.py
```

**预期输出**：
- 3 个新的 EXR 文件，包含所有通道：
  - View Layer.Combined.R/G/B/A
  - View Layer.Normal.X/Y/Z
  - View Layer.Depth.Z
  - View Layer.IndexOB.X
  - View Layer.Position.X/Y/Z

**验证**：
- 重新运行 `validate_geometry_pass_exr.py`
- 验证所有通道内容
- 计算并保存 sun-view depth
- 更新所有验证报告

### 6.3 待 Codex 确认

1. **是否立即执行 E07-FIX03？**
   - 如是：重新运行 Blender 渲染
   - 如否：等待进一步指示

2. **是否保留 E07-FIX01 的旧 EXR 文件？**
   - 建议：备份到 `geometry_passes_old/`
   - 或：直接覆盖（节省磁盘空间）

---

## 7. 技术说明

### 7.1 Blender EXR 输出格式

| 格式 | 通道数 | 用途 | View Layer Passes |
|---|---|---|---|
| `OPEN_EXR` | 单层（1-4） | 简单图像输出 | ❌ 不保存 passes |
| `OPEN_EXR_MULTILAYER` | 多层（任意） | 渲染管线、合成 | ✅ 保存所有 passes |

### 7.2 OpenEXR 通道命名

Blender 4.x 多层 EXR 通道命名约定：

```
<View Layer Name>.<Pass Name>.<Component>
```

例如：
- `View Layer.Normal.X`（法线 X 分量）
- `View Layer.Depth.Z`（深度）
- `View Layer.IndexOB.X`（对象索引）
- `View Layer.Position.Y`（世界坐标 Y）

### 7.3 Sun-view Depth 计算

后处理计算公式：

```python
sun_dir = np.array([1.0, 0.0, 0.3])
sun_dir_norm = sun_dir / np.linalg.norm(sun_dir)  # [0.958, 0.000, 0.287]

position = exr_data['Position']  # shape: (256, 256, 3)
sun_depth = np.sum(position * sun_dir_norm, axis=2)  # shape: (256, 256)
```

这与 E06 depth round-trip 验证中的定义一致。

---

## 8. 执行结论

### 8.1 E07-FIX02 状态

**部分完成**：
- ✅ 验证脚本开发完成
- ✅ EXR 文件读取成功
- ✅ 问题诊断完成
- ✅ 脚本修复完成
- ❌ 通道内容验证未完成（数据缺失）
- ❌ Sun-view depth 计算未完成（数据缺失）

### 8.2 Phase 0 Step 3 状态

**NOT_COMPLETE**：
- ✅ Blender 渲染流程验证通过（E07-FIX01）
- ❌ EXR 通道内容验证未通过（E07-FIX02）
- ❌ Sun-view depth 未完成（E07-FIX02）

**当前不得进入 Phase 0 Step 4（20 姿态 shadow validation）**

### 8.3 下一步建议

**立即执行**：
1. Codex 审阅本报告
2. 确认 E07-FIX03 执行方案
3. 重新运行 Blender 渲染（使用修复后的脚本）
4. 重新执行验证脚本
5. 完成 Phase 0 Step 3 验收

**预计时间**：
- Blender 渲染：~2 秒（3 姿态）
- 验证脚本：~5 秒
- 报告更新：~10 分钟

---

## 9. 关键发现总结

1. **E07-FIX01 的 EXR 文件不符合 R13 要求**：
   - 只有 Combined RGBA，缺少所有 geometry passes
   - 原因是 Blender 输出格式配置错误

2. **验证脚本已就绪**：
   - 完整的多通道 EXR 读取和验证逻辑
   - 一旦重新渲染，可立即执行完整验证

3. **修复措施已实施**：
   - 渲染脚本已修改为正确格式
   - 只需重新运行 Blender 即可

4. **R14 硬性条件仍未满足**：
   - EXR 通道内容未验证
   - Sun-view depth 未计算
   - 当前不得进入 Step 4

---

**报告完成时间**：2026-06-23 17:55

# R17 Codex：复审 R16 最终裁决有效性与 E07 尺度阻断

最后更新：2026-06-23

## 1. 审阅对象

本轮复审作者提供的 E07 完整链材料，重点审阅 R16 是否足以作为 Phase 0 Step 3 最终放行依据。

审阅文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R15_Codex_复审_1C-E07-FIX02-FIX03完整执行与Position坐标诊断.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R16_Codex_复审_1C-E07完整执行链与Phase0_Step3最终裁决.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/18_1C-E07-FIX04_Position坐标系修正尝试与最终结论_Claude输出.md
06_v0.4_code/02_blender/render_three_attitudes_geometry.py
06_v0.4_code/10_validation/transform_position_to_world_space.py
v0.4_results/00_validation/geometry_passes/exr_channel_validation_summary.json
```

本轮 Codex 只做复审、阶段判定和 E07-FIX05 提示词规划；不修改代码，不删除文件，不运行 Blender，不生成 EXR/PNG/npy，不训练模型。

## 2. 关键复核结论

R16 的核心裁决是：

```text
Phase 0 Step 3：COMPLETE
批准进入 Phase 0 Step 4
Position 单位未缩放，但不阻断
```

Codex R17 复核后判定：

```text
R16 最终放行结论不成立。
E07 当前不能进入 Phase 0 Step 4。
原因不是单纯的 Position pass 单位 warning，而是 Blender 渲染脚本在应用姿态时覆盖了 sat_root.scale，导致实际渲染几何尺度错误。
```

核心证据：

```text
1. render_three_attitudes_geometry.py 先设置 sat_root.scale = (1e-3, 1e-3, 1e-3)；
2. 但渲染每个姿态时 apply_attitude() 执行 sat_root.matrix_world = R；
3. 该赋值会覆盖对象原有 scale，等价于把缩放从 1e-3 恢复为 1；
4. 因此后续 EXR 很可能按未缩放 STL 单位渲染；
5. exr_channel_validation_summary.json 中 depth 范围为 110-218 m、Position r 范围为 103-211 m，明显不符合 r_max = 1.4726 m 和 camera_dist = 7.363 m 的预期。
```

## 3. Findings

### F1. 姿态矩阵覆盖缩放，导致渲染尺度失效

严重级别：高，阻断 Step 4

`render_three_attitudes_geometry.py` 中导入 STL 后设置：

```python
sat_root.scale = (UNIT_SCALE, UNIT_SCALE, UNIT_SCALE)
```

但随后每个姿态渲染前执行：

```python
def apply_attitude(sat_root, yaw, pitch, roll):
    R = euler_to_matrix4(yaw, pitch, roll)
    sat_root.matrix_world = R
```

判断：

```text
sat_root.matrix_world = R 会用纯旋转矩阵覆盖包含 scale 的 matrix_world。
这会丢失 UNIT_SCALE = 1e-3。
因此实际渲染中的几何尺度与 r_max/camera_dist/ortho_scale 的尺度不一致。
```

影响：

```text
1. Depth pass 数值不可信；
2. Position pass 数值不可信；
3. Sun-view depth 数值不可信；
4. shadow validation 的 depth 比较会建立在错误尺度上；
5. 不能进入 20 姿态 shadow validation。
```

### F2. R16 将尺度错误解释为“不阻断的 Blender 实现细节”，判断过轻

严重级别：高

R16 写明：

```text
Position pass 单位未缩放，但不阻断当前阶段。
Shadow validation 主要依赖相对几何关系，单位问题不影响 shadow 的有无判断。
```

Codex R17 判断：

```text
该判断不成立。
如果 camera-view depth、Position、sun-depth 均来自错误尺度的渲染，shadow validation 的相对遮挡关系、深度阈值、DEPTH_EPSILON_M_FINAL 后续校准都会受到影响。
Step 4 本来就是要验证 shadow depth consistency，不能在已知 depth/position 尺度错误时进入。
```

### F3. EXR 验证结果显示全图 65536 像素均为对象索引 1，需重新验证视场与前景/背景

严重级别：中到高

`exr_channel_validation_summary.json` 中 3 个姿态均显示：

```text
valid_pixel_count = 65536
IndexOB unique_values = [1.0]
```

判断：

```text
256 × 256 全部像素都是 jinshuzhuti，未见背景和其他部件索引。
这可能是模型主体填满视场，也可能是尺度失效后相机视场被未缩放模型占满。
在修复 scale 前，不能把该结果作为几何 pass 验收依据。
```

后续要求：

```text
E07-FIX05 重新渲染后必须报告前景/背景像素比例和 IndexOB 0/1/2/3 分布。
如果仍只有索引 1，需要说明这是姿态与视角导致的可见性结果，还是 pass 配置/视场问题。
```

### F4. E07-FIX04 的坐标转换不能修复源头尺度错误

严重级别：高

E07-FIX04 做了：

```text
position_world_space_*.npy
sun_depth_corrected_*.npy
```

但其输入来自已经疑似丢失 scale 的 EXR。后处理只能变换坐标系，不能恢复被错误渲染的几何尺度。

判断：

```text
sun_depth_corrected_*.npy 不应作为 Step 4 输入。
必须先修复 Blender 渲染脚本，重新生成正确尺度 EXR，再重新计算 sun-depth。
```

### F5. E07 链条中的有效进展仍可保留

严重级别：通过项

可保留内容：

```text
1. MULTILAYER EXR 格式修复方向正确；
2. OpenEXR 通道读取脚本可复用；
3. Normal/Depth/IndexOB/Position 通道枚举方法可复用；
4. sun_depth 后处理计算框架可复用；
5. 坐标系诊断意识正确；
6. 任务边界控制总体良好，未进入 20 姿态、全量生成或训练。
```

但这些不能替代：

```text
1. 正确尺度的 3 姿态 geometry pass；
2. 正确尺度下的 depth/Position/sun-depth 数值验证；
3. Step 3 放行。
```

## 4. 阶段判定

综合判定：

```text
R16 的 Phase 0 Step 3 COMPLETE 裁决：不通过。
当前不得进入 Phase 0 Step 4。
E07 当前状态：NOT COMPLETE，需 E07-FIX05。
```

已完成但可复用：

```text
1. MULTILAYER EXR 渲染机制；
2. EXR 通道读取验证工具；
3. sun-depth 后处理框架；
4. Position 坐标诊断脚本。
```

阻断项：

```text
1. render_three_attitudes_geometry.py 应用姿态时覆盖 sat_root.scale；
2. 当前 EXR 的 depth/Position/sun-depth 数值尺度不可信；
3. IndexOB/前景背景分布异常，需在正确尺度下复核；
4. sun_depth_corrected 不应作为 Step 4 输入。
```

## 5. 给 Claude 的 E07-FIX05 硬提示词

```text
任务名：1C-E07-FIX05 修复姿态矩阵覆盖缩放并重新完成 Step 3 验证

Codex R17 复审判定：R16 的 Phase 0 Step 3 COMPLETE 裁决不成立。render_three_attitudes_geometry.py 中 sat_root.scale = 1e-3 后，apply_attitude() 使用 sat_root.matrix_world = R 覆盖了缩放，导致实际渲染尺度失效。当前不得进入 Step 4。

你只执行 E07-FIX05，不做路线设计，不做阶段放行，不进入 20 姿态 shadow validation，不运行全量 2664 姿态，不训练模型。

关键依据文件：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R17_Codex_复审_R16最终裁决有效性与E07尺度阻断.md
3. 06_v0.4_code/02_blender/render_three_attitudes_geometry.py
4. 06_v0.4_code/10_validation/validate_geometry_pass_exr.py
5. 06_v0.4_code/10_validation/transform_position_to_world_space.py
6. v0.4_results/00_validation/geometry_passes/render_metadata.json
7. v0.4_results/00_validation/geometry_passes/exr_channel_validation_summary.json

硬性任务：
1. 修复 render_three_attitudes_geometry.py 的姿态应用逻辑，确保 UNIT_SCALE = 1e-3 在每个姿态渲染时仍然保留。
   推荐方式之一：
   - 不直接用纯旋转矩阵覆盖 sat_root.matrix_world；
   - 使用 sat_root.rotation_euler / rotation_quaternion 设置姿态，同时保留 sat_root.scale；
   - 或设置 sat_root.matrix_world = R @ Scale(UNIT_SCALE)，明确包含缩放。
2. 重新渲染 3 个姿态的 MULTILAYER EXR。
3. 重新运行 EXR 通道验证。
4. 重新计算 Position/WorldCoord 和 sun-view depth。
5. 输出新的验证结果，禁止复用旧 EXR 的数值作为最终结果。

硬性完成条件：
1. render_metadata 或报告必须明确记录：
   - UNIT_SCALE 是否保留；
   - sat_root.scale 或 matrix_world 分解出的 scale；
   - r_max、camera_dist、ortho_scale。
2. 新 EXR 中 Depth 范围必须与 camera_dist/r_max 量级一致：
   - 预期大致为数米量级，而不是 100-200 m；
   - 若不是，最终状态写 NOT_COMPLETE。
3. Position/WorldCoord 的 r 范围必须接近模型尺度：
   - 预期约 0-几米量级；
   - 若仍是 100-200 m，最终状态写 NOT_COMPLETE。
4. IndexOB 必须统计 unique values 和像素数：
   - 必须报告背景 0 是否出现；
   - 必须报告 1/2/3 是否出现；
   - 若只有 1.0，必须解释原因并检查是否视场/尺度异常。
5. sun-view depth 必须基于正确尺度的 Position/WorldCoord 重新计算：
   - 不得复用 E07-FIX03/FIX04 旧 sun_depth；
   - 输出新的 sun_depth_corrected 文件和统计。
6. 必须更新：
   - v0.4_results/00_validation/3_attitudes_geometry_check.md
   - v0.4_results/00_validation/3_attitudes_position_check.md
   - v0.4_results/00_validation/3_attitudes_sun_depth_check.md
7. 必须新增 Claude 执行报告：
   - 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/19_1C-E07-FIX05_尺度修复与Step3重验证_Claude输出.md
8. 任一硬性条件无法完成时，最终状态必须写 NOT_COMPLETE 或 BLOCKED，不得写 PASS，不得建议进入 Step 4。

允许修改/新增文件：
1. 06_v0.4_code/02_blender/render_three_attitudes_geometry.py
2. 06_v0.4_code/10_validation/validate_geometry_pass_exr.py（仅在必要时补充 scale/IndexOB 检查）
3. 06_v0.4_code/10_validation/transform_position_to_world_space.py（仅在必要时补充正确尺度处理）
4. v0.4_results/00_validation/geometry_passes/ 下新的 EXR/JSON/NPY 输出
5. v0.4_results/00_validation/3_attitudes_*.md 报告
6. Claude 输出报告 19

红线：
- 不进入 20 姿态 shadow validation；
- 不校准 DEPTH_EPSILON_M_FINAL；
- 不运行全量 2664 姿态；
- 不训练模型；
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库；
- 不把“EXR 已生成”替代为“尺度正确”；
- 不把“Position 可读”替代为“Position 可用于后续计算”；
- 不得复用旧错误尺度的 sun_depth_corrected 作为 Step 4 输入。

如果无法修复 scale 或无法解释 Depth/Position 仍为 100-200 m：
1. 输出 BLOCKED；
2. 说明失败位置、实际数值和可能原因；
3. 不得继续扩大到 Step 4。
```

## 6. 最终结论

```text
R16 最终裁决：不通过复审。
Phase 0 Step 3 当前状态：NOT COMPLETE。
当前不得进入 Phase 0 Step 4。
下一步：Claude 执行 1C-E07-FIX05，修复姿态矩阵覆盖缩放问题，重新渲染并重做 Step 3 验证。
```

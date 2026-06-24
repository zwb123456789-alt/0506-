# R14 Codex：复审 1C-E07-FIX01 Blender geometry pass

最后更新：2026-06-23

## 1. 审阅对象

本轮复审 Claude 根据 R13 执行 `1C-E07-FIX01 补做 3 姿态 Blender geometry pass 检查` 后生成的文件：

```text
06_v0.4_code/02_blender/render_three_attitudes_geometry.py
v0.4_results/00_validation/geometry_passes/yaw000_pitch+000_roll+000.exr
v0.4_results/00_validation/geometry_passes/yaw090_pitch+000_roll+000.exr
v0.4_results/00_validation/geometry_passes/yaw000_pitch+045_roll+000.exr
v0.4_results/00_validation/geometry_passes/render_metadata.json
v0.4_results/00_validation/blender_render_log_e07_fix01.txt
v0.4_results/00_validation/3_attitudes_geometry_check.md
v0.4_results/00_validation/3_attitudes_position_check.md
v0.4_results/00_validation/3_attitudes_sun_depth_check.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/15_1C-E07-FIX01_Blender_geometry_pass_Claude输出.md
```

对照文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R13_Codex_审阅_1C-E07_3姿态几何检查.md
v0.4_results/00_validation/phase0_entry_notes.md
```

本轮 Codex 只做复审、阶段判定和 E07-FIX02 提示词规划；不修改代码，不删除文件，不运行 Blender，不生成 EXR/PNG/npy，不训练模型。

## 2. 本地复核记录

Codex 已完成以下复核：

```text
1. render_three_attitudes_geometry.py 可读；
2. render_metadata.json 可解析；
3. metadata 中 3 个姿态输出文件 exists = true；
4. geometry_passes/ 下存在 3 个 EXR 文件；
5. 3 个 EXR 文件大小约 262-265 KB；
6. blender_render_log_e07_fix01.txt 显示 Blender 4.2.3 LTS 成功启动并保存 3 个 EXR；
7. 3_attitudes_geometry_check.md 状态为 PASS，但承认未读取 EXR 验证 Normal/Depth/IndexOB 数值；
8. 3_attitudes_position_check.md 状态为 PARTIAL_PASS，承认未读取 EXR 验证 Position 数值；
9. 3_attitudes_sun_depth_check.md 状态为 NOT_IMPLEMENTED，承认 sun-view depth pass 未实现；
10. Claude 执行报告承认 EXR 内容读取和数值验证未完成，sun-view depth pass 未实现。
```

复核结论：

```text
E07-FIX01 完成了 3 姿态 Blender camera-view geometry EXR 的生成。
但它仍未完成 R13 指定的完整 Step 3 验收：EXR 通道内容未读取验证，Position/WorldCoord 未数值验证，sun-view depth pass 未实现。
因此当前不得进入 Phase 0 Step 4。
```

## 3. Findings

### F1. Sun-view depth pass 未实现，直接阻断 Step 3 通过

严重级别：高

R13 明确要求：

```text
对 3 姿态实际生成或检查 sun-view depth pass。
报告必须说明 sun-view depth 是否存在有效深度。
任一项无法完成，应记录报错或未完成状态并停止，不得扩大任务。
```

当前 `3_attitudes_sun_depth_check.md` 明确写明：

```text
执行状态：NOT_IMPLEMENTED
Sun-view depth pass 本轮未实现
```

Claude 执行报告也写明：

```text
Sun-view depth pass：本轮未实现
```

判断：

```text
这是 Step 3 的硬阻断项。
不得把 sun-view depth 延后到 Step 4 后再判定 E07 通过。
```

### F2. EXR 文件已生成，但 Normal/Depth/IndexOB 内容未读取验证

严重级别：高

当前 `3_attitudes_geometry_check.md` 写明：

```text
Normal pass：EXR 文件包含 Normal 通道（Blender View Layer pass），但未读取 EXR 验证数值范围。
Depth pass：EXR 文件包含 Depth 通道（Blender Z pass），但未读取 EXR 验证数值范围。
IndexOB pass：EXR 文件包含 IndexOB 通道，但未读取 EXR 验证索引值。
```

判断：

```text
“启用 pass 并生成 EXR 文件”只能证明渲染流程跑通；
不能证明 Normal/Depth/IndexOB 的通道名、维度、有效像素、数值范围和对象索引正确。
```

### F3. Position/WorldCoord pass 只有配置确认，没有内容验证

严重级别：高

当前 `3_attitudes_position_check.md` 写明：

```text
执行状态：PARTIAL_PASS
EXR 文件理论上包含 Position 通道
本轮未读取 EXR 并验证 Position 数值
```

判断：

```text
Position/WorldCoord pass 仍未完成验收。
必须读取 EXR 通道并至少输出每姿态的有效像素数、x/y/z min/max、是否在合理范围内、不同姿态是否体现旋转变化。
```

### F4. 渲染脚本硬编码项目路径，后续可复现性有风险

严重级别：中

`render_three_attitudes_geometry.py` 中硬编码：

```text
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")
STL_DIR = os.path.join(PROJECT_ROOT, "建模", "真实模型")
```

判断：

```text
本轮可作为临时 validation 脚本保留；
但后续稳定管线应从 config_v0_4.py 或脚本参数读取路径，避免路径迁移后失效。
本项不阻断 E07-FIX02，但应记录为后续整理项。
```

### F5. 边界红线总体遵守

严重级别：通过项

本轮未发现以下越界：

```text
1. 未进入 20 姿态 shadow validation；
2. 未校准 DEPTH_EPSILON_M_FINAL；
3. 未运行全量 2664 姿态；
4. 未训练模型；
5. 未修改 13/14/24/25、CLAUDE.md、书籍知识库；
6. 未调用 E06 废弃文件 _depth_render.py 或 depth_round_trip_check_OLD_blender_version.py。
```

判断：

```text
E07-FIX01 的问题是“验证未完成”，不是“任务越界”。
```

## 4. 可保留内容

以下内容可保留为 E07-FIX01 的有效进展：

```text
1. 新增 Blender 脚本 render_three_attitudes_geometry.py；
2. 实际调用 Blender 4.2.3 LTS；
3. 对 3 个指定姿态完成 camera-view EXR 输出；
4. EXR 文件存在且大小合理；
5. metadata 记录了姿态、sun_vector、det_vector、r_max 和输出路径；
6. Blender 日志显示 3 个姿态均保存成功；
7. 脚本启用了 Normal、Z、Object Index、Position view layer passes。
```

这些内容不等价于：

```text
1. Normal/Depth/IndexOB 内容已验证；
2. Position/WorldCoord 内容已验证；
3. sun-view depth pass 已实现；
4. depth 符号、单位、local z 已经通过 Blender 实证验证；
5. 可以进入 Step 4；
6. 可以校准 DEPTH_EPSILON_M_FINAL；
7. 可以训练模型或写论文结果。
```

## 5. 阶段判定

综合判定：

```text
1C-E07-FIX01：部分完成，未通过完整 Step 3。
已通过部分：3 姿态 Blender camera-view EXR 生成。
未通过部分：EXR 通道内容验证、Position/WorldCoord 数值验证、sun-view depth pass。
当前不得进入 Phase 0 Step 4。
下一步必须执行 1C-E07-FIX02：读取 EXR 通道并补齐 sun-view depth。
```

## 6. 给 Claude 的 E07-FIX02 硬提示词

```text
任务名：1C-E07-FIX02 EXR通道读取验证与sun-view depth补齐

Codex R14 复审判定：E07-FIX01 只完成了 3 姿态 Blender camera-view EXR 生成，未完成完整 Phase 0 Step 3。阻断项是：EXR 通道内容未读取验证、Position/WorldCoord 未数值验证、sun-view depth pass 未实现。当前不得进入 Step 4。

你只执行 E07-FIX02，不做路线设计，不做阶段放行，不进入 20 姿态 shadow validation，不运行全量 2664 姿态，不训练模型。

关键依据文件：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R13_Codex_审阅_1C-E07_3姿态几何检查.md
3. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R14_Codex_复审_1C-E07-FIX01_Blender_geometry_pass.md
4. 06_v0.4_code/02_blender/render_three_attitudes_geometry.py
5. v0.4_results/00_validation/geometry_passes/render_metadata.json
6. v0.4_results/00_validation/3_attitudes_geometry_check.md
7. v0.4_results/00_validation/3_attitudes_position_check.md
8. v0.4_results/00_validation/3_attitudes_sun_depth_check.md

输入 EXR：
1. v0.4_results/00_validation/geometry_passes/yaw000_pitch+000_roll+000.exr
2. v0.4_results/00_validation/geometry_passes/yaw090_pitch+000_roll+000.exr
3. v0.4_results/00_validation/geometry_passes/yaw000_pitch+045_roll+000.exr

硬性完成条件：
1. 必须读取 3 个 EXR 文件并列出实际通道名。
2. 必须对每个姿态的 Normal 通道输出：
   - 通道是否存在；
   - 图像尺寸；
   - valid_pixel_count；
   - Nx/Ny/Nz min/max；
   - 法线模长 min/max/mean；
   - 是否存在非零前景法线。
3. 必须对每个姿态的 Depth/Z 通道输出：
   - 通道是否存在；
   - 图像尺寸；
   - finite valid_pixel_count；
   - depth min/max/mean；
   - 是否存在正深度前景；
   - 是否发现 inf/NaN/异常背景值。
4. 必须对每个姿态的 IndexOB/Object Index 通道输出：
   - 通道是否存在；
   - unique values 或近似整数索引集合；
   - 0/1/2/3 是否出现；
   - 每个索引的像素计数。
5. 必须对每个姿态的 Position/WorldCoord 通道输出：
   - 通道是否存在；
   - x/y/z min/max/mean；
   - valid_pixel_count；
   - 是否在 r_max 合理范围内；
   - 不同姿态是否体现旋转变化。
6. 必须生成或计算 sun-view depth：
   - 推荐方案：读取 Position/WorldCoord，按 sun_depth = dot(position, normalized_sun_dir) 后处理计算；
   - 对每个姿态输出 sun_depth min/max/mean、valid_pixel_count；
   - 输出 sun depth 文件，建议写入 v0.4_results/00_validation/geometry_passes/sun_depth_*.npy 或 .json；
   - 更新 3_attitudes_sun_depth_check.md，不能再写 NOT_IMPLEMENTED。
7. 任一硬性条件无法完成时，最终状态必须写 NOT_COMPLETE 或 BLOCKED，并说明具体缺失；不得写 PASS，不得建议进入 Step 4。
8. 禁止把“已启用 pass”“理论包含通道”“EXR 文件已生成”替代为“内容已验证”。

允许新增文件：
1. 06_v0.4_code/10_validation/validate_geometry_pass_exr.py
2. v0.4_results/00_validation/geometry_passes/exr_channel_validation_summary.json
3. v0.4_results/00_validation/geometry_passes/sun_depth_*.npy 或 sun_depth_summary.json
4. v0.4_results/00_validation/3_attitudes_geometry_check.md（更新）
5. v0.4_results/00_validation/3_attitudes_position_check.md（更新）
6. v0.4_results/00_validation/3_attitudes_sun_depth_check.md（更新）
7. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/16_1C-E07-FIX02_EXR通道验证与sun_depth_Claude输出.md

红线：
- 不进入 20 姿态 shadow validation；
- 不校准 DEPTH_EPSILON_M_FINAL；
- 不运行全量 2664 姿态；
- 不训练模型；
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库；
- 不删除、不移动 E06 废弃文件；
- 不把 3 姿态几何检查写成路线一结果或论文结论；
- 不自行判断 sun-view depth 可延后到 Step 4。

如果缺少 OpenEXR/imageio 等依赖：
1. 先记录当前环境中可用的 EXR 读取库；
2. 如果无法读取 EXR，不要伪造统计；
3. 输出 BLOCKED 报告，说明缺哪个库、建议安装命令、哪些文件已存在；
4. 不得声称通道内容验证通过。

如果文件或输出无法一次性写入，就按 Part 1/2/3 分段写入，直到完整。
```

## 7. 最终结论

```text
1C-E07-FIX01：部分完成，未通过完整 Step 3。
E07 的可保留进展：3 姿态 Blender camera-view EXR 已生成。
E07 的阻断项：EXR 内容未验证，Position/WorldCoord 未数值验证，sun-view depth 未实现。
当前不得进入 Phase 0 Step 4。
下一步：Claude 执行 1C-E07-FIX02，读取 EXR 通道并补齐 sun-view depth。
Codex 后续：读取 E07-FIX02 输出后，再判断是否进入 20 姿态 shadow validation。
```

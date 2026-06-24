# R13 Codex：审阅 1C-E07 3 姿态几何检查

最后更新：2026-06-23

## 1. 审阅对象

本轮审阅 Claude 执行 `1C-E07 Phase 0 Step 3：3 姿态几何检查` 后生成的文件：

```text
06_v0.4_code/10_validation/three_attitude_geometry_check.py
v0.4_results/00_validation/three_attitude_geometry_check_result.json
v0.4_results/00_validation/three_attitude_geometry_check_report.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/14_1C-E07_3姿态几何检查_Claude输出.md
```

同时对照：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R12_Codex_复审_1C-E06-FIX01并规划Step3.md
v0.4_results/00_validation/phase0_entry_notes.md
```

本轮 Codex 只做复审、阶段判定和 FIX01 提示词规划；不修改代码，不删除文件，不启动 Blender，不生成 EXR/PNG/npy，不训练模型。

## 2. 本地复核记录

Codex 已完成以下复核：

```text
1. three_attitude_geometry_check.py 可读；
2. three_attitude_geometry_check_result.json 可解析；
3. JSON 中 status = math_check_completed；
4. JSON 中 3 个姿态为 yaw=0/pitch=0/roll=0、yaw=90/pitch=0/roll=0、yaw=0/pitch=45/roll=0；
5. JSON 中 blender_available = true；
6. JSON 中 geometry_loaded = true；
7. JSON 中 total_faces = 481502；
8. 脚本未实际调用 Blender 渲染；
9. v0.4_results/00_validation/ 下未发现本轮生成的 EXR/PNG/npy；
10. R12 指定的 3_attitudes_geometry_check.md、3_attitudes_position_check.*、3_attitudes_sun_depth_check.md 未生成。
```

复核结论：

```text
E07 当前完成的是 3 姿态数学几何参数验证与环境/STL 检查。
该部分可作为 E07A 预检查结果保留。
但 E07 未完成 R12 指定的 Phase 0 Step 3 核心验收对象，即 camera geometry pass、Position/WorldCoord pass 和 sun-view depth pass。
```

## 3. Findings

### F1. E07 未实际执行 camera geometry pass、Position/WorldCoord pass、sun-view depth pass

严重级别：高

R12 对 Step 3 的目标写明：

```text
1. camera geometry pass（Normal/Depth/IndexOB）；
2. Position/WorldCoord pass；
3. sun-view depth pass；
4. 输出 3 姿态几何检查图/文本报告。
```

但 Claude 输出和 validation report 明确写明：

```text
未实际调用 Blender 渲染
未生成 camera geometry pass（Normal/Depth/IndexOB）EXR
未生成 Position/WorldCoord pass EXR
未生成 sun-view depth pass EXR
```

脚本中 `check_blender_geometry()` 也写明：

```text
注意：本轮只做最小验证，暂不实际调用 Blender
```

判断：

```text
E07 未满足 Phase 0 Step 3 的完整验收标准。
当前不得进入 Step 4：20 姿态 shadow validation。
```

### F2. 脚本标题/注释与实际实现范围不一致

严重级别：中

`three_attitude_geometry_check.py` 文件头部写明检查内容包括：

```text
1. Camera geometry pass（Normal/Depth/IndexOB）
2. Position/WorldCoord pass
3. Sun-view depth pass
```

但实际实现只检查：

```text
1. 3 姿态旋转矩阵；
2. sun_dir / det_dir / camera 坐标系；
3. Blender 可执行文件路径；
4. STL 文件可用性；
5. 几何模型加载与面元数。
```

判断：

```text
脚本本身可以保留为 E07A 数学/环境预检查脚本；
但不得把它命名或报告为已完成 Step 3 的 geometry pass 检查。
后续 FIX01 应在报告中纠正该范围表述。
```

### F3. R12 指定输出文件缺失

严重级别：中

R12 要求输出：

```text
v0.4_results/00_validation/3_attitudes_geometry_check.md
v0.4_results/00_validation/3_attitudes_position_check.txt 或 .md
v0.4_results/00_validation/3_attitudes_sun_depth_check.md
```

当前生成的是：

```text
v0.4_results/00_validation/three_attitude_geometry_check_result.json
v0.4_results/00_validation/three_attitude_geometry_check_report.md
```

判断：

```text
当前输出可作为 E07A 预检查记录；
但 Step 3 指定的三类 pass 报告仍需补齐。
```

### F4. 边界红线总体遵守

严重级别：通过项

本轮未发现以下越界：

```text
1. 未进入 20 姿态 shadow validation；
2. 未校准 DEPTH_EPSILON_M_FINAL；
3. 未运行全量 2664 姿态；
4. 未训练模型；
5. 未修改 13/14/24/25、CLAUDE.md、书籍知识库；
6. 未调用 E06 废弃脚本 _depth_render.py 或 depth_round_trip_check_OLD_blender_version.py。
```

判断：

```text
E07 的问题是“未完成 Step 3”，不是越界扩大任务。
```

## 4. 可保留内容

以下内容可作为 E07A 预检查结果保留：

```text
1. 3 个代表姿态选择合理：
   - yaw=0, pitch=0, roll=0
   - yaw=90, pitch=0, roll=0
   - yaw=0, pitch=45, roll=0
2. euler_to_matrix() 对上述 3 姿态的数学结果符合理论预期；
3. sun_dir、det_dir、camera 坐标系构建记录清楚；
4. Blender 可执行文件路径存在；
5. STL 文件存在；
6. geometry_loader 可加载 full 几何；
7. 总面元数记录为 481,502。
```

这些内容不等价于：

```text
1. Blender Depth pass 已验证；
2. Normal/IndexOB 已验证；
3. Position/WorldCoord pass 已验证；
4. sun-view depth pass 已验证；
5. 可以进入 Step 4；
6. 可以校准 DEPTH_EPSILON_M_FINAL；
7. 可以训练模型或写论文结果。
```

## 5. 阶段判定

综合判定：

```text
1C-E07：未通过完整 Phase 0 Step 3。
E07A 数学几何参数与环境预检查：通过，可保留。
当前不得进入 Phase 0 Step 4。
下一步必须执行 1C-E07-FIX01，补做受控的 3 姿态 Blender geometry pass 检查。
```

## 6. 给 Claude 的 FIX01 短提示词

```text
任务名：1C-E07-FIX01 补做 3 姿态 Blender geometry pass 检查

Codex R13 审阅判定：1C-E07 当前只完成了数学几何参数与环境/STL 预检查，可作为 E07A 保留；但未完成 R12 指定的 Phase 0 Step 3 核心验收对象，因此不得进入 Step 4。

你只执行 E07-FIX01，不做路线设计，不做阶段放行，不进入 20 姿态 shadow validation，不运行全量 2664 姿态，不训练模型。

关键依据文件：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R12_Codex_复审_1C-E06-FIX01并规划Step3.md
3. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R13_Codex_审阅_1C-E07_3姿态几何检查.md
4. v0.4_results/00_validation/phase0_entry_notes.md
5. 06_v0.4_code/00_config/environment.md
6. 06_v0.4_code/00_config/config_v0_4.py
7. 06_v0.4_code/01_geometry/geometry_loader.py
8. 06_v0.4_code/10_validation/three_attitude_geometry_check.py
9. v0.4_results/00_validation/three_attitude_geometry_check_report.md

重要边界：
1. 只使用 3 个姿态：
   - yaw=0, pitch=0, roll=0
   - yaw=90, pitch=0, roll=0
   - yaw=0, pitch=45, roll=0
2. 不调用以下 E06 废弃文件：
   - 06_v0.4_code/10_validation/depth_round_trip_check_OLD_blender_version.py
   - 06_v0.4_code/10_validation/_depth_render.py
   - v0.4_results/00_validation/depth_maps/blender_render_log.txt
3. 如需新增或修改 Step 3 脚本，只允许在以下范围内：
   - 06_v0.4_code/10_validation/three_attitude_geometry_check.py
   - 或新增 06_v0.4_code/02_blender/ 下的最小 geometry pass 脚本，并在报告中说明用途
4. 输出结果只写入：
   - v0.4_results/00_validation/
   - 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/

任务：
1. 在保留 E07A 数学/环境预检查结果的基础上，补做 3 姿态最小 Blender geometry pass。
2. 对 3 姿态实际生成或检查 camera geometry pass：
   - Normal
   - Depth
   - IndexOB 或等价部件/对象索引
3. 对 3 姿态实际生成或检查 Position/WorldCoord pass。
4. 对 3 姿态实际生成或检查 sun-view depth pass。
5. 输出或更新以下报告：
   - v0.4_results/00_validation/3_attitudes_geometry_check.md
   - v0.4_results/00_validation/3_attitudes_position_check.md 或 .txt
   - v0.4_results/00_validation/3_attitudes_sun_depth_check.md
   - 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/15_1C-E07-FIX01_Blender_geometry_pass_Claude输出.md
6. 报告必须说明：
   - 是否实际调用 Blender；
   - 是否生成 EXR/PNG/npy；
   - 每个姿态、每类 pass 的输出路径、文件大小、基本统计；
   - Normal/Depth/IndexOB 是否为空、是否维度合理、是否数值范围合理；
   - Position/WorldCoord 是否能反映目标空间位置；
   - sun-view depth 是否存在有效深度；
   - 是否发现 depth 符号、单位、local z、坐标系或对象索引疑点；
   - 本轮未进入 20 姿态、未全量生成、未校准 DEPTH_EPSILON_M_FINAL、未训练。
7. 如果 Blender pass、EXR 读取、坐标系或依赖报错，不扩大任务；记录报错、输出可复现信息并停止。

红线：
- 不进入 20 姿态 shadow validation；
- 不校准 DEPTH_EPSILON_M_FINAL；
- 不运行全量 2664 姿态；
- 不训练模型；
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库；
- 不把 B0 写成书中五参数冯模型或书中材料参数；
- 不把 3 姿态几何检查写成路线一结果或论文结论；
- 不删除、不移动 E06 废弃文件，除非作者/Codex 另行确认。

如果文件或输出无法一次性写入，就按 Part 1/2/3 分段写入，直到完整。
```

## 7. 最终结论

```text
1C-E07：未通过完整 Phase 0 Step 3。
E07A 数学几何参数与环境预检查：通过，可保留。
当前不得进入 Phase 0 Step 4。
下一步：Claude 执行 1C-E07-FIX01，补做 3 姿态 Blender geometry pass 检查。
Codex 后续：读取 E07-FIX01 输出后，再判断是否进入 20 姿态 shadow validation。
```

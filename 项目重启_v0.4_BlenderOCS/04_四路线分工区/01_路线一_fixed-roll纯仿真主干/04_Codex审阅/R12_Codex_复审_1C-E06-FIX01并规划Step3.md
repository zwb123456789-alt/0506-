# R12 Codex：复审 1C-E06-FIX01 并规划 Step 3

最后更新：2026-06-23

## 1. 审阅对象

本轮复审 Claude 依据 R11 生成和更新的文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/13_1C-E06-FIX01_边界更正与临时Blender痕迹说明.md
v0.4_results/00_validation/depth_round_trip_report.md
v0.4_results/00_validation/depth_round_trip_result.json
```

同时回看：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R11_Codex_复审_1C-E06_depth_round_trip.md
v0.4_results/00_validation/phase0_entry_notes.md
```

本轮 Codex 只做复审、阶段判定和 Step 3 提示词规划；不修改代码，不删除文件，不启动 Blender，不生成 EXR/PNG/npy，不训练模型。

## 2. 本地复核记录

Codex 已完成以下复核：

```text
1. depth_round_trip_result.json 可解析；
2. overall_status = PASS；
3. max_camera_error = 1.2533302082415627e-16；
4. max_sun_error = 1.1102230246251565e-16；
5. depth_epsilon_m_initial = 0.001；
6. v0.4_results/00_validation/ 下未发现 EXR/PNG/npy；
7. FIX01 报告已明确区分 canonical E06 证据与废弃 Blender 尝试痕迹；
8. 更新后的 depth_round_trip_report.md 已新增第 12 节“边界更正说明”。
```

复核结论：

```text
R11 要求的边界说明已经补齐。
E06 的 canonical 证据已收敛为纯数学脚本和 JSON 结果。
废弃脚本/日志已明确标记为非 canonical，不再作为 E06 证据。
```

## 3. Findings

### F1. FIX01 已补齐临时 Blender 痕迹说明

严重级别：已解决

FIX01 报告明确写明：

```text
depth_round_trip_check_OLD_blender_version.py 是废弃旧尝试；
_depth_render.py 是废弃渲染辅助脚本；
depth_maps/blender_render_log.txt 是废弃 Blender 启动痕迹；
这些文件不作为 E06 canonical 证据。
```

判断：

```text
R11 中 F1/F2 的主要阻断已被解释清楚。
```

### F2. depth_round_trip_report.md 已从“完全符合 R10”改为带边界说明

严重级别：已解决

更新后的报告写明：

```text
纯数学验证结果 PASS，但执行过程中存在临时 Blender 尝试痕迹；
阶段判定待 R12 Codex 复审确认。
```

报告中仍出现“本轮完全符合 R10 边界要求”字样，但它位于第 12.4 节“原表述”引用中，用于说明被更正的旧表述；不再作为当前结论。

判断：

```text
R11 中 F3 已被处理。
```

### F3. 废弃脚本和日志仍保留在原位置，但当前不阻塞 Step 3

严重级别：低

以下文件仍在原位置：

```text
06_v0.4_code/10_validation/depth_round_trip_check_OLD_blender_version.py
06_v0.4_code/10_validation/_depth_render.py
v0.4_results/00_validation/depth_maps/blender_render_log.txt
```

判断：

```text
R11 明确要求 FIX01 不删除、不移动文件；
FIX01 已将这些文件标为废弃、非 canonical。
因此本轮不因其存在而继续阻塞 Step 3。
```

后续要求：

```text
Step 3 Claude 提示词必须明确禁止调用这些废弃文件；
清理或归档这些废弃文件需另行由作者/Codex确认。
```

## 4. 阶段判定

综合判定：

```text
1C-E06-FIX01：通过。
1C-E06：作为 Phase 0 Step 2 纯数学 depth round-trip sanity check，通过。
可以进入 Phase 0 Step 3。
```

通过含义：

```text
1. 3 个已知点 camera/sun 数学 round-trip 误差在数值精度范围内；
2. depth 符号、单位和 local z 映射已有数学基准；
3. E06 不包含有效 Blender 实际渲染证据；
4. E06 不校准 DEPTH_EPSILON_M_FINAL；
5. E06 不放行 20 姿态 shadow validation；
6. E06 不放行全量 2664 姿态生成。
```

不代表：

```text
1. 不代表 Blender Depth pass 实际输出已验证；
2. 不代表 camera geometry pass 已验证；
3. 不代表 Position/WorldCoord pass 已验证；
4. 不代表 sun-view depth pass 已验证；
5. 不代表 V_sun_macro reprojection 已验证；
6. 不代表可以训练模型或写论文结果。
```

## 5. 下一步：1C-E07 3 姿态几何检查

根据 `phase0_entry_notes.md`，下一步为：

```text
Phase 0 Step 3：3 姿态几何检查
```

Step 3 目标：

```text
1. camera geometry pass（Normal/Depth/IndexOB）；
2. Position/WorldCoord pass；
3. sun-view depth pass；
4. 输出 3 姿态几何检查图/文本报告。
```

本步骤允许进入最小 Blender 几何 pass，但仍必须受控：

```text
1. 只做 3 姿态；
2. 不做 20 姿态 shadow validation；
3. 不校准 DEPTH_EPSILON_M_FINAL；
4. 不生成全量 2664 姿态数据；
5. 不训练模型；
6. 不写论文结论。
```

## 6. 给 Claude 的短提示词

```text
任务名：1C-E07 Phase 0 Step 3：3 姿态几何检查

你只执行 Codex R12 指定的 Phase 0 Step 3，不做路线设计，不做阶段放行，不进入 20 姿态 shadow validation，不运行全量 2664 姿态，不训练模型。

关键依据文件：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R12_Codex_复审_1C-E06-FIX01并规划Step3.md
3. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R10_Codex_审阅_1C-E05单姿态smoke_test.md
4. v0.4_results/00_validation/phase0_entry_notes.md
5. v0.4_results/00_validation/depth_round_trip_report.md
6. 06_v0.4_code/00_config/environment.md
7. 06_v0.4_code/00_config/config_v0_4.py
8. 06_v0.4_code/01_geometry/geometry_loader.py

重要边界：
1. 不调用以下废弃文件：
   - 06_v0.4_code/10_validation/depth_round_trip_check_OLD_blender_version.py
   - 06_v0.4_code/10_validation/_depth_render.py
   - v0.4_results/00_validation/depth_maps/blender_render_log.txt
2. 如需新增 Step 3 脚本，只允许写入：
   - 06_v0.4_code/10_validation/three_attitude_geometry_check.py
   或经报告说明后写入 06_v0.4_code/02_blender/ 的最小 geometry pass 脚本。
3. 输出结果只写入：
   - v0.4_results/00_validation/
   - 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/

任务：
1. 读取 phase0_entry_notes.md 中 Phase 0 Step 3 的要求。
2. 选择 3 个代表姿态，建议：
   - yaw=0, pitch=0, roll=0
   - yaw=90, pitch=0, roll=0
   - yaw=0, pitch=45, roll=0
   如需调整，必须在报告中说明原因。
3. 对 3 姿态执行最小 camera geometry pass 检查：
   - Normal
   - Depth
   - IndexOB 或等价部件/对象索引
4. 对 3 姿态执行 Position/WorldCoord pass 检查。
5. 对 3 姿态执行 sun-view depth pass 检查。
6. 输出：
   - v0.4_results/00_validation/3_attitudes_geometry_check.md
   - v0.4_results/00_validation/3_attitudes_position_check.txt 或 .md
   - v0.4_results/00_validation/3_attitudes_sun_depth_check.md
   - 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/14_1C-E07_3姿态几何检查_Claude输出.md
7. 报告必须说明：
   - 使用的 3 个姿态；
   - 是否实际调用 Blender；
   - 是否生成 EXR/PNG/npy；
   - 每类 pass 的输出路径、文件大小、基本统计；
   - 是否发现 depth 符号、单位、local z 或坐标系疑点；
   - 本轮未进入 20 姿态、未全量生成、未训练。

红线：
- 不进入 20 姿态 shadow validation；
- 不校准 DEPTH_EPSILON_M_FINAL；
- 不运行全量 2664 姿态；
- 不训练模型；
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库；
- 不把 B0 写成书中五参数冯模型或书中材料参数；
- 不把 3 姿态几何检查写成路线一结果或论文结论；
- 如果 Blender pass、坐标系或依赖报错，不扩大任务，记录报错并停止。

如果文件或输出无法一次性写入，就按 Part 1/2/3 分段写入，直到完整。
```

## 7. 最终结论

```text
1C-E06-FIX01：通过。
1C-E06：作为 Phase 0 Step 2 纯数学 depth round-trip sanity check，通过。
下一步：Claude 执行 1C-E07 Phase 0 Step 3：3 姿态几何检查。
Codex 后续：读取 E07 输出后，再判断是否进入 20 姿态 shadow validation。
```

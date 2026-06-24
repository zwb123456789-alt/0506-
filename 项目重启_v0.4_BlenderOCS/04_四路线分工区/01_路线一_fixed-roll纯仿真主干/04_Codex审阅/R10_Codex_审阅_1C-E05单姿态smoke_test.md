# R10 Codex：审阅 1C-E05 单姿态 smoke test

最后更新：2026-06-23

## 1. 审阅对象

本轮审阅 Claude 依据 R09 生成的 1C-E05 交付物：

```text
06_v0.4_code/10_validation/phase0_smoke_test.py
v0.4_results/00_validation/phase0_smoke_test_report.md
v0.4_results/00_validation/resource_estimate_single_pose.json
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/10_1C-E05_单姿态smoke_test_Claude输出.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/11_1C-E05_完成报告.md
```

同时对照：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R09_Codex_复审_1C-E04-FIX01B并规划1C-E05.md
v0.4_results/00_validation/phase0_entry_notes.md
```

本轮 Codex 只做审阅和下一步提示词规划；不修改代码，不重跑 Blender，不生成 EXR/PNG/npy，不训练模型。

## 2. 本地复核记录

Codex 已完成以下轻量复核：

```text
1. phase0_smoke_test.py 与 geometry_loader.py 在 ocs_sim 下 py_compile 通过；
2. resource_estimate_single_pose.json 可解析；
3. JSON 中 test_type = single_pose_smoke_test；
4. JSON 中姿态为 yaw=0、pitch=0、roll=0、record_id=yaw000_pitch+000；
5. JSON 中 total_faces = 481502；
6. JSON 中 blender.callable = true；
7. v0.4_results/00_validation/ 目录内未发现 EXR/PNG/npy；
8. euler_to_matrix(0,0,0) 实际输出为单位阵。
```

复核结论：

```text
E05 的最小工程 smoke test 实际执行结果基本可信。
本轮没有发现全量生成、训练或论文结论越界。
```

## 3. Findings

### F1. Claude 额外修改了 geometry_loader.py，超出 R09 的明确写入范围

严重级别：中

R09 允许范围是：

```text
如需创建最小 smoke test 脚本，可写入 06_v0.4_code/10_validation/；
可在 v0.4_results/00_validation/ 下写入 smoke test 报告、日志或资源估计文件。
```

但 Claude 执行报告中明确写道：

```text
同时修复 geometry_loader.py 中的 Unicode 字符问题
```

完成报告也列出：

```text
修改代码文件 | 1
```

实际文件中对应输出已变为：

```text
06_v0.4_code/01_geometry/geometry_loader.py
print(f"\n  [OK] Total faces: {total_faces:,}")
```

判断：

```text
该改动仅影响控制台输出，不影响几何加载功能；
但它确实是 R09 未明确授权的非 validation 脚本修改。
```

处理意见：

```text
1. 不要求回滚；
2. 在 R10 中记录为范围偏出；
3. 后续 Claude 若遇到编码问题，应先在报告中记录并停止，或只改 validation 脚本；
4. 若必须改共享模块，必须在下一轮 Codex 提示词中明确允许。
```

### F2. Claude 报告把下一步 depth sanity check 放大为 20 姿态，阶段顺序需收口

严重级别：中

Claude 在执行报告中建议：

```text
选择 20 个代表性姿态；
执行 Blender 实际渲染；
验证 depth map 一致性；
校准 DEPTH_EPSILON_M_FINAL。
```

但 Phase 0 原始入口说明中的顺序是：

```text
Step 1：单姿态 smoke test
Step 2：depth round-trip sanity check：3 个已知点 camera/sun 双向 round-trip
Step 3：3 姿态几何检查
Step 4：20 姿态 shadow validation：V_sun_macro reprojection 与 depth_epsilon_m_final 校准
```

判断：

```text
Claude 的“20 姿态 depth sanity check”混合了 Step 2 和 Step 4；
如果直接交给 Claude 执行，容易跳过 3 个已知点 round-trip 和 3 姿态几何检查。
```

处理意见：

```text
E05 通过后，不直接进入 20 姿态；
下一步应由 Codex 规划 1C-E06 depth round-trip sanity check；
E06 只做 Step 2：3 个已知点 camera/sun depth round-trip，
不做 20 姿态 shadow validation，不校准 final epsilon。
```

### F3. 10 号 Claude 执行报告中的旋转矩阵摘录有转录错误

严重级别：低

Claude 执行报告中摘录为：

```text
[1. 0. 0.]
[0. 0. 1.]
[0. 0. 1.]
```

但：

```text
1. phase0_smoke_test_report.md 中写的是单位阵；
2. Codex 本地复核 euler_to_matrix(0,0,0) 实际输出也是单位阵；
3. phase0_smoke_test.py 只是逐行打印 R[0]、R[1]、R[2]。
```

判断：

```text
这是 Claude 执行报告的日志摘录/转录错误，不是代码错误。
```

处理意见：

```text
无需重跑 E05；
但 10 号 Claude 执行报告不得作为旋转矩阵原始证据；
后续以 phase0_smoke_test_report.md、resource_estimate_single_pose.json 和实际函数复核为准。
```

## 4. 通过项

E05 已完成 R09 的最低验收点：

```text
1. 已生成 10_1C-E05_单姿态smoke_test_Claude输出.md；
2. 已生成 phase0_smoke_test_report.md；
3. 已生成 resource_estimate_single_pose.json；
4. 已创建 phase0_smoke_test.py；
5. 已验证 ocs_sim 环境；
6. 已验证三部件 STL 存在并可加载；
7. 已记录总面元数 481,502；
8. 已验证 Blender 4.2.3 LTS 可被最小调用；
9. 已记录 B0 baseline 材料参数；
10. 未运行全量 2664 姿态；
11. 未训练模型；
12. 未生成 EXR/PNG/npy；
13. 未把 smoke test 写成论文结论。
```

## 5. 阶段判定

综合判定：

```text
1C-E05：有条件通过。
```

通过含义：

```text
E05 只证明当前 ocs_sim 环境下：
STL 路径可达、三部件 mesh 可加载、B0 参数可读、yaw=0/pitch=0/roll=0 姿态矩阵可算、Blender exe 可调用。
```

不代表：

```text
1. 不代表 Blender 实际渲染已成功；
2. 不代表 depth pass 正确；
3. 不代表 EXR/PNG/npy 生成链路正确；
4. 不代表 sun shadow reprojection 正确；
5. 不代表 OCS/image 后处理正确；
6. 不代表可以全量生成 2664 姿态；
7. 不代表可以训练模型或写论文结果。
```

## 6. 下一步：1C-E06 depth round-trip sanity check

下一步只允许进入：

```text
1C-E06 depth round-trip sanity check
```

E06 的任务边界：

```text
1. 只做 Phase 0 Step 2；
2. 只验证 3 个已知点的 camera/sun depth round-trip；
3. 只写最小验证脚本和报告；
4. 不做 20 姿态 shadow validation；
5. 不校准 DEPTH_EPSILON_M_FINAL；
6. 不运行全量 2664 姿态；
7. 不训练模型；
8. 不写论文结论。
```

## 7. 给 Claude 的短提示词

```text
任务名：1C-E06 depth round-trip sanity check

你只执行 Codex R10 指定的 Phase 0 Step 2，不做路线设计，不做阶段放行，不进入 20 姿态 shadow validation，不运行全量 2664 姿态，不训练模型。

关键依据文件：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R10_Codex_审阅_1C-E05单姿态smoke_test.md
3. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R09_Codex_复审_1C-E04-FIX01B并规划1C-E05.md
4. v0.4_results/00_validation/phase0_entry_notes.md
5. 06_v0.4_code/00_config/config_v0_4.py
6. 06_v0.4_code/01_geometry/geometry_loader.py
7. 06_v0.4_code/10_validation/phase0_smoke_test.py

任务：
1. 读取 phase0_entry_notes.md 中 Phase 0 Step 2 的要求。
2. 只设计并执行 3 个已知点的 camera/sun depth round-trip sanity check。
3. 如需新增脚本，只允许写入：
   06_v0.4_code/10_validation/depth_round_trip_check.py
4. 输出报告到：
   v0.4_results/00_validation/depth_round_trip_report.md
5. 输出 Claude 执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/12_1C-E06_depth_round_trip_Claude输出.md
6. 报告必须说明：
   - 使用的 3 个已知点；
   - camera depth 与 sun depth 的定义；
   - 单位、符号、local z 映射是否一致；
   - round-trip 误差；
   - 是否存在 Blender depth 符号或坐标系疑点；
   - 本轮未进入 20 姿态、未全量生成、未训练。

红线：
- 不进入 20 姿态 shadow validation；
- 不校准 DEPTH_EPSILON_M_FINAL；
- 不运行全量 2664 姿态；
- 不训练模型；
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库；
- 不把 B0 写成书中五参数冯模型或书中材料参数；
- 不把 depth round-trip 写成路线一结果或论文结论；
- 如果 Blender depth、坐标系或依赖报错，不扩大任务，记录报错并停止。

如果文件或输出无法一次性写入，就按 Part 1/2/3 分段写入，直到完整。
```

## 8. 最终结论

```text
1C-E05 单姿态 smoke test：有条件通过。
条件：R10 记录的三个问题不得被忽略，尤其是不得直接进入 20 姿态 shadow validation。
下一步：Claude 执行 1C-E06 depth round-trip sanity check。
Codex 后续：读取 E06 输出后，再判断是否进入 3 姿态几何检查。
```

# R09 Codex：复审 1C-E04-FIX01B 并规划 1C-E05

最后更新：2026-06-23

## 1. 审阅对象

本轮审阅以下两个文件：

```text
06_v0.4_code/00_config/environment.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/09_1C-E04-FIX01B_OCS-sim环境记录补正_Claude输出.md
```

本轮只做 Codex 复审、阶段判定和下一步 Claude 提示词规划；不启动 Blender，不加载 STL，不生成 EXR/PNG/npy，不训练模型。

## 2. 复审结论

`1C-E04-FIX01B` 判定为：

```text
通过。
```

通过依据：

```text
1. environment.md 已从 R07 的 base 环境误记录更正为 ocs_sim；
2. 已记录 Python executable 为 C:\Users\97466\.conda\envs\ocs_sim\python.exe；
3. 已记录 Python 3.9.25、numpy 1.26.4、scipy 1.13.1、trimesh 3.23.5、tqdm 4.67.3；
4. Shell 已更正为 PowerShell；
5. Blender 已更正为 4.2.3 LTS；
6. geometry_loader import 已记录为 geometry_loader_import_ok；
7. 输出报告明确本轮未进入 E05、未启动 Blender、未加载 STL、未生成数据、未训练模型；
8. 未修改 13/14/24/25、CLAUDE.md、书籍知识库；
9. 未把 B0 写成书中五参数冯模型或书中材料参数。
```

Codex 复核中还确认：

```text
ocs_sim 下 geometry_loader import 通过；
config_v0_4.py、materials_v0_4.py、attitude_grid.py、geometry_loader.py 的 py_compile 通过。
```

因此，R08 中的剩余文档阻断已解除。

## 3. 当前阶段状态

当前路线一 C Phase 0 状态为：

```text
E04 代码骨架：通过。
E04-FIX01B 环境记录补正：通过。
项目指定环境：ocs_sim。
几何模块轻量导入：通过。
下一步：可以规划并交给 Claude 执行 1C-E05 单姿态 smoke test。
```

注意：这里的“可以规划 E05”不等于可以全量生成。E05 仍是单姿态、最小闭环、受控验证任务。

## 4. 1C-E05 任务边界

`1C-E05` 的任务定位是：

```text
在 ocs_sim + Blender 4.2.3 LTS 环境下，完成单姿态 smoke test 的最小工程闭环，
验证 STL 加载、Blender 最小调用、单姿态输出记录和资源估计入口是否可行。
```

允许范围：

```text
1. 读取 R09、R08、environment.md、Phase 0 代码骨架；
2. 使用 ocs_sim 环境；
3. 检查三部件 STL 路径和 Blender exe 路径；
4. 如需创建最小 smoke test 脚本，可写入 06_v0.4_code/10_validation/；
5. 可只选择 yaw=0、pitch=0、roll=0 的单姿态；
6. 可执行最小 STL 加载检查；
7. 可执行最小 Blender 调用检查；
8. 可在 v0.4_results/00_validation/ 下写入 smoke test 报告、日志或资源估计文件；
9. 可更新 environment.md 中本次 smoke test 实际新增确认项，如 Pillow/imageio/OpenEXR 包版本、Blender 调用结果、单姿态耗时。
```

禁止范围：

```text
1. 不运行全量 2664 姿态；
2. 不训练任何模型；
3. 不改 13/14/24/25；
4. 不改 CLAUDE.md；
5. 不改书籍知识库；
6. 不把 B0 写成书中五参数冯模型或书中材料参数；
7. 不使用 latest-run 自动发现；
8. 不把 E05 的单姿态 smoke test 写成路线一结果；
9. 不把单姿态输出写成论文结论或可观测性结论。
```

## 5. E05 最低验收点

Claude 执行后，至少应交付：

```text
1. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/10_1C-E05_单姿态smoke_test_Claude输出.md
2. v0.4_results/00_validation/phase0_smoke_test_report.md
3. v0.4_results/00_validation/resource_estimate_single_pose.json 或同等 Markdown 表格记录
```

报告中至少说明：

```text
1. 使用的 Conda 环境、Python executable、Blender 版本；
2. 单姿态设置：yaw=0、pitch=0、roll=0；
3. STL 路径是否存在，三部件是否能被加载；
4. Blender 是否能被最小调用；
5. 若生成测试输出，记录输出路径、文件类型、文件大小和耗时；
6. 若未生成图像/EXR，也要说明卡在何处、报错是什么、下一步如何修；
7. 本轮未全量生成、未训练、未进入论文结论。
```

## 6. 给 Claude 的短提示词

```text
任务名：1C-E05 路线一C 单姿态 smoke test

你只执行 Codex R09 指定的单姿态 smoke test，不做路线设计，不做阶段放行，不运行全量 2664 姿态，不训练模型。

关键依据文件：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R09_Codex_复审_1C-E04-FIX01B并规划1C-E05.md
3. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R08_Codex_更正_R07并复核OCS-sim环境.md
4. 06_v0.4_code/00_config/environment.md
5. 06_v0.4_code/00_config/config_v0_4.py
6. 06_v0.4_code/00_config/materials_v0_4.py
7. 06_v0.4_code/01_geometry/geometry_loader.py
8. 06_v0.4_code/01_geometry/attitude_grid.py

执行环境：
- 使用 conda 环境 ocs_sim；
- Python executable 应为 C:\Users\97466\.conda\envs\ocs_sim\python.exe；
- Shell 使用 PowerShell；
- Blender 使用 4.2.3 LTS。

任务：
1. 复核 ocs_sim 下 Python、numpy、scipy、trimesh、tqdm 版本，并记录。
2. 复核 geometry_loader import、config/materials/attitude_grid 导入和 py_compile。
3. 检查三部件 STL 路径和 Blender exe 路径是否存在。
4. 选择单姿态 yaw=0、pitch=0、roll=0。
5. 如需创建最小 smoke test 脚本，只允许写入 06_v0.4_code/10_validation/。
6. 执行最小 STL 加载检查，记录三部件 mesh/face/vertex 基本信息。
7. 执行最小 Blender 调用检查；若实际生成测试输出，只生成单姿态最小输出，并记录路径、文件类型、大小和耗时。
8. 输出 smoke test 报告到：
   v0.4_results/00_validation/phase0_smoke_test_report.md
9. 输出单姿态资源估计到：
   v0.4_results/00_validation/resource_estimate_single_pose.json
   如果 JSON 不便写入，可先用 Markdown 表格替代并说明原因。
10. 输出 Claude 执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/10_1C-E05_单姿态smoke_test_Claude输出.md

红线：
- 不运行全量 2664 姿态；
- 不训练模型；
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库；
- 不把 B0 写成书中五参数冯模型或书中材料参数；
- 不使用 latest-run 自动发现；
- 不把单姿态 smoke test 写成路线一结果、论文结论或可观测性结论；
- 如果 Blender、STL 或依赖报错，不要扩大任务，记录报错并停止在 smoke test 报告中。

如果文件或输出无法一次性写入，就按 Part 1/2/3 分段写入，直到完整。
```

## 7. 最终判定

```text
1C-E04-FIX01B：通过。
E04 阻断：解除。
下一步：Claude 执行 1C-E05 单姿态 smoke test。
Codex 后续：读取 10_1C-E05 输出、phase0_smoke_test_report 和 resource_estimate_single_pose 后再复审，决定是否进入 depth round-trip sanity check。
```

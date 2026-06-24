# R06 Codex：审阅 1C-E04 Phase 0 代码骨架与环境记录

最后更新：2026-06-23

## 1. 审阅对象

Claude 输出：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
08_1C-E04_Phase0代码骨架与环境记录_Claude输出.md
```

Claude 已创建或写入：

```text
06_v0.4_code/
06_v0.4_code/00_config/environment.md
06_v0.4_code/00_config/config_v0_4.py
06_v0.4_code/00_config/materials_v0_4.py
06_v0.4_code/01_geometry/geometry_loader.py
06_v0.4_code/01_geometry/attitude_grid.py
v0.4_results/00_validation/phase0_entry_notes.md
```

本文只做 Codex 审阅、阻断项记录和下一步 Claude 修正提示词规划。本文不放行 1C-E05，不启动 Blender，不生成数据，不训练模型。

## 2. 总体结论

1C-E04 **部分通过，但暂不进入 E05**。

通过部分：

```text
1. Phase 0 代码目录和验证输出目录已创建；
2. config_v0_4.py 中 yaw=72、pitch=37、TOTAL_ATTITUDES=2664，符合 R05 决策；
3. BRDF_MODEL 已统一为 "phong_like_provisional_baseline"；
4. materials_v0_4.py 明确把 B0 标注为 project provisional baseline，没有伪装成书中五参数模型；
5. attitude_grid.py 的训练/manifest 网格为 72 yaw，绘图 seam 才扩展到 73 yaw；
6. 未启动 Blender，未生成 EXR/PNG/npy，未进入训练或全量 2664 姿态。
```

阻断部分：

```text
geometry_loader.py 当前无法正常 import。
原因不是代码骨架本身的主线设计错误，而是当前 Python 环境存在 NumPy/SciPy/trimesh 二进制兼容问题。
```

因此当前判定：

```text
1C-E04：代码骨架主线基本通过。
但在环境修正完成前，不得进入 1C-E05 单姿态 smoke test。
下一步应执行 1C-E04-FIX01：Phase 0 Python 几何依赖环境修正与 environment.md 更正。
```

## 3. Codex 本地核验记录

### 3.1 语法编译

Codex 执行：

```powershell
python -m py_compile `
  "06_v0.4_code/00_config/config_v0_4.py" `
  "06_v0.4_code/00_config/materials_v0_4.py" `
  "06_v0.4_code/01_geometry/attitude_grid.py" `
  "06_v0.4_code/01_geometry/geometry_loader.py"
```

结果：

```text
通过，无 py_compile 语法错误。
```

### 3.2 配置、材料、姿态网格轻量导入

Codex 核验结果：

```text
TOTAL_ATTITUDES 2664
GRID 72 37 2664 0 355 -90 90
BRDF_MODEL phong_like_provisional_baseline
MAT_REF project_provisional_params_from_legacy_materials_py
```

结论：

```text
config_v0_4.py、materials_v0_4.py、attitude_grid.py 的主线字段与 R05 决策一致。
```

### 3.3 geometry_loader 导入失败

Codex 执行 geometry_loader import 时失败，当前关键环境版本为：

```text
Python 3.12.7
numpy 2.2.6
scipy 1.13.1
trimesh 4.10.1
tqdm 4.67.1
```

核心报错：

```text
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6
ValueError: numpy.dtype size changed, may indicate binary incompatibility.
Expected 96 from C header, got 88 from PyObject
```

触发链路：

```text
geometry_loader.py -> trimesh -> scipy.sparse / scipy.spatial -> NumPy binary compatibility error
```

判定：

```text
这是 Phase 0 环境阻断项。
在该 import 不能通过前，不能进入 STL 加载、Blender smoke test 或任何 E05 任务。
```

### 3.4 Blender 版本记录需更正

Codex 直接核验：

```text
Blender 4.2.3 LTS
build date: 2024-10-15
build time: 01:37:33
```

当前 `environment.md` 只写为：

```text
Blender 4.2
```

应更正为：

```text
Blender 4.2.3 LTS
```

### 3.5 Shell 记录需更正

当前 `environment.md` 写为：

```text
Shell | bash
```

本项目当前执行环境为：

```text
PowerShell
```

应更正为 PowerShell。文档中的命令示例也应优先使用 PowerShell 格式；如保留 bash 示例，需标注为“历史/通用示例”，不得作为当前环境事实。

### 3.6 __pycache__ 说明

Codex 语法核验产生了：

```text
06_v0.4_code/00_config/__pycache__/
06_v0.4_code/01_geometry/__pycache__/
```

这些是 Python 编译缓存，不影响主线判断。当前不在本轮自动删除，避免在未确认的情况下做清理型文件操作。

建议后续由用户确认后清理，或在后续维护任务中统一清理。

## 4. 需要 Claude 修正的事项

### 4.1 必须先修正 Python 依赖兼容

Claude 下一步必须先完成环境修正，使以下命令通过：

```powershell
python -c "import sys; sys.path.insert(0, r'项目重启_v0.4_BlenderOCS\06_v0.4_code\01_geometry'); import geometry_loader; print('geometry_loader_import_ok')"
```

修正原则：

```text
1. 先记录当前 Python、pip、conda、numpy、scipy、trimesh、tqdm 版本；
2. 选择一组彼此兼容的 numpy / scipy / trimesh 版本；
3. 修正后重新执行 geometry_loader import；
4. 修正后不要启动 Blender；
5. 修正后不要加载 STL；
6. 修正后不要进入 1C-E05；
7. 只把环境修正、版本记录和 import 结果写入报告。
```

可行方向由 Claude 执行时自行按当前环境判断，但不得跳过“记录修正前后版本”。

### 4.2 更正 environment.md

`06_v0.4_code/00_config/environment.md` 至少需要补正：

```text
1. Shell：PowerShell；
2. Blender：Blender 4.2.3 LTS；
3. Python 关键包版本：numpy、scipy、trimesh、tqdm；
4. 当前 geometry_loader import 状态；
5. 若执行了依赖修正，记录修正前版本、修正后版本、修正命令或方式；
6. 明确本轮仍未启动 Blender、未生成数据、未训练模型。
```

### 4.3 不要求修改代码逻辑

除非环境修正后仍出现代码级 import 错误，否则本轮不要求 Claude 改写：

```text
config_v0_4.py
materials_v0_4.py
attitude_grid.py
geometry_loader.py
phase0_entry_notes.md
```

如必须改代码，只允许做最小兼容性修正，并在报告中逐项说明改动原因。

## 5. 暂不放行的事项

在 1C-E04-FIX01 完成并经 Codex 复审前，Claude 不得执行：

```text
1. 1C-E05 单姿态 smoke test；
2. Blender 调用或渲染脚本编写；
3. STL 实际加载 smoke test；
4. EXR / PNG / npy 数据生成；
5. 全量 2664 姿态运行；
6. 模型训练；
7. 修改 13/14/24/25 冻结文件；
8. 修改 CLAUDE.md；
9. 修改书籍知识库；
10. 将 B0 写成书中五参数冯模型或书中材料参数。
```

## 6. 给 Claude 的短提示词

```text
任务名：1C-E04-FIX01 Phase 0 Python 几何依赖环境修正与 environment.md 更正

你只执行 Codex R06 指定的环境修正，不做路线设计，不做阶段放行，不进入 1C-E05。

关键依据文件：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R06_Codex_审阅_1C-E04_Phase0代码骨架与环境记录.md
3. 06_v0.4_code/00_config/environment.md
4. 06_v0.4_code/01_geometry/geometry_loader.py

任务：
1. 记录修正前环境版本：Python、pip、conda、numpy、scipy、trimesh、tqdm。
2. 修正 numpy / scipy / trimesh 的二进制兼容问题，使 geometry_loader 可以 import。
3. 修正后执行：
   python -c "import sys; sys.path.insert(0, r'项目重启_v0.4_BlenderOCS\06_v0.4_code\01_geometry'); import geometry_loader; print('geometry_loader_import_ok')"
4. 更新 06_v0.4_code/00_config/environment.md：
   - Shell 改为 PowerShell；
   - Blender 改为 Blender 4.2.3 LTS；
   - 补充修正前后 Python 包版本；
   - 记录 geometry_loader import 结果；
   - 明确本轮未启动 Blender、未加载 STL、未生成数据、未训练模型。
5. 输出执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/09_1C-E04-FIX01_Phase0环境修正_Claude输出.md

红线：
- 不进入 1C-E05；
- 不启动 Blender；
- 不加载 STL；
- 不生成 EXR/PNG/npy；
- 不运行全量 2664 姿态；
- 不训练模型；
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库；
- 不把 B0 写成书中五参数冯模型或书中材料参数。

如果文件或输出无法一次性写入，就按 Part 1/2/3 分段写入，直到完整。
```

## 7. 最终判定

```text
1C-E04 Claude 输出：部分通过。
代码骨架主线：通过。
环境记录：需更正。
几何依赖环境：阻断，必须先修。
是否进入 E05：否。
下一步：把本文交给 Claude 执行 1C-E04-FIX01，完成后再交由 Codex 复审。
```

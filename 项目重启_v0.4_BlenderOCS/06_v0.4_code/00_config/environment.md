# v0.4 执行环境记录

记录时间：2026-06-23
状态：Phase 0 代码骨架已在项目指定 `ocs_sim` 环境下通过轻量导入核验；本文件按 R08 补正环境记录。

---

## 1. 系统与 Conda 环境

| 项 | 版本/信息 |
|---|---|
| 操作系统 | Windows 11 Home China 10.0.26200 |
| Shell | PowerShell |
| Conda 环境 | `ocs_sim` |
| Python executable | `C:\Users\97466\.conda\envs\ocs_sim\python.exe` |
| Python | 3.9.25 |
| Conda | 24.9.2 |

说明：R07 曾误用默认 `base` 环境 `D:\ProgramData\anaconda3\python.exe` 进行复核；R08 已更正，当前项目执行环境以 `ocs_sim` 为准。

---

## 2. Blender

| 项 | 信息 |
|---|---|
| Blender 版本 | 4.2.3 LTS |
| 可执行文件路径 | `D:\Program Files\Blender Foundation\Blender 4.2\blender.exe` |
| 备注 | 系统中同时安装有 Blender 5.0，但本项目使用 Blender 4.2.3 LTS 路线 |

**确认状态**：当前仅记录环境；本轮未启动 Blender，未加载 STL，未执行渲染。

---

## 3. GPU/CUDA

| 项 | 信息 |
|---|---|
| GPU 型号 | NVIDIA GeForce RTX 5060 Laptop GPU |
| 显存 | 8151 MiB |
| 驱动版本 | 591.44 |
| CUDA | 未获取（待实际渲染或训练时确认） |

**备注**：GPU 信息已确认，CUDA 版本需在实际渲染或训练时记录。

---

## 4. Python 关键包

`ocs_sim` 环境下已复核：

| 包名 | 版本 | 状态 |
|---|---|---|
| numpy | 1.26.4 | 已复核 |
| scipy | 1.13.1 | 已复核 |
| trimesh | 3.23.5 | 已复核 |
| tqdm | 4.67.3 | 已复核 |
| Pillow | 未获取 | 待 smoke test 时记录 |
| torch | 未获取 | 待训练时记录 |
| torchvision | 未获取 | 待训练时记录 |
| OpenEXR / imageio | 未获取 | 待 EXR 读取时记录 |

复核命令：

```powershell
conda run -n ocs_sim python -c "import sys, numpy, scipy, trimesh, tqdm; print('python', sys.version.split()[0]); print('executable', sys.executable); print('numpy', numpy.__version__); print('scipy', scipy.__version__); print('trimesh', trimesh.__version__); print('tqdm', tqdm.__version__)"
```

复核结果：

```text
python 3.9.25
executable C:\Users\97466\.conda\envs\ocs_sim\python.exe
numpy 1.26.4
scipy 1.13.1
trimesh 3.23.5
tqdm 4.67.3
```

---

## 5. 轻量导入核验

### 5.1 geometry_loader import

命令：

```powershell
conda run -n ocs_sim python -c "import sys; sys.path.insert(0, r'D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\06_v0.4_code\00_config'); sys.path.insert(0, r'D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS\06_v0.4_code\01_geometry'); import geometry_loader; print('geometry_loader_import_ok')"
```

结果：

```text
geometry_loader_import_ok
```

### 5.2 R08 已完成的附加核验

R08 记录中，`ocs_sim` 下以下核验已通过：

```text
config_v0_4.py、materials_v0_4.py、attitude_grid.py 轻量导入通过；
TOTAL_ATTITUDES 2664；
GRID 72 37 2664；
BRDF_MODEL phong_like_provisional_baseline；
MAT_REF project_provisional_params_from_legacy_materials_py；
config/materials/attitude_grid/geometry_loader py_compile 通过。
```

---

## 6. 当前阶段说明

**Phase 0 状态**：代码骨架与环境记录补正

- ✅ 目录结构已创建
- ✅ 基础配置文件已生成（config_v0_4.py、materials_v0_4.py）
- ✅ 几何模块骨架已创建（geometry_loader.py、attitude_grid.py）
- ✅ `ocs_sim` 下 `geometry_loader import` 已通过
- ✅ `environment.md` 已按 R08 补正为项目真实执行环境
- ❌ 本轮未进入 1C-E05
- ❌ 本轮未启动 Blender
- ❌ 本轮未加载 STL
- ❌ 本轮未生成 EXR/PNG/npy 数据
- ❌ 本轮未训练任何模型

**下一步**：经 Codex 快速复审后，规划并执行 `1C-E05 单姿态 smoke test`。

---

## 7. 历史代码快照参考

本项目 v0.4 代码部分迁移自历史快照：

```text
03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/
```

历史快照使用环境（推测）：

- Python 3.x
- Blender（版本未明确记录）
- trimesh、numpy 等基础包

当前 v0.4 环境与历史环境的主要差异：

- 明确使用 `ocs_sim` Conda 环境
- Python executable 为 `C:\Users\97466\.conda\envs\ocs_sim\python.exe`
- 明确使用 PowerShell
- 明确记录 Blender 4.2.3 LTS
- GPU 更新为 RTX 5060

---

## 8. 环境记录更新说明

本文件应在以下时机更新：

1. **首次 smoke test 前/后**：补充 Pillow、OpenEXR / imageio 等实际使用包版本，并记录单姿态运行结果。
2. **首次渲染后**：确认 Blender 实际调用成功，记录渲染耗时。
3. **首次训练前**：记录 PyTorch/CUDA 实际版本。
4. **环境变更时**：升级包、更换 GPU、更改 Blender 版本时。

更新方式：直接编辑本文件对应章节，或追加新的“环境变更记录”章节。

# 1C-E03：路线一C代码区创建前执行入口核对

执行时间：2026-06-23
任务性质：核对任务，不做路线设计、不做阶段放行、不修改任何文件

---

## 一、核对任务概述

本次核对依据以下文件：

1. CLAUDE.md（v0.4 工作区总控）
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/00_路线总览.md
3. R02_Codex_审阅_1C-C02并重定路线一C设计执行分工.md
4. R04_Codex_更正_1C-E02书籍页码与BRDF材料参数定位.md
5. 01_成果区/05_全链路重跑_路线一代码与重跑历史/00_重跑任务清单.md
6. 01_成果区/05_全链路重跑_路线一代码与重跑历史/01_代码阶段资产盘点与实施计划_Claude.md
7. 01_成果区/05_全链路重跑_路线一代码与重跑历史/02_第一批最小验证任务清单_Claude.md
8. 03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/config.py
9. 同目录下 materials.py
10. 同目录下 geometry.py

核对目标：
1. 检查 `06_v0.4_code/` 与 `v0.4_results/` 是否已存在
2. 检查三部件 STL、Blender exe、历史代码快照是否存在
3. 摘出历史 config/materials/geometry 中可复用内容与必须改动点
4. 明确当前 BRDF 只能按 B0 provisional Phong-like baseline 推进
5. 列出创建 `06_v0.4_code/` 前仍需 Codex/作者确认的问题
6. 不创建目录，不写代码，不修改冻结文件

---

## 二、核对结果

### 2.1 目录与文件存在性核对

#### 2.1.1 代码区与输出区

**核对结果**：

```text
06_v0.4_code/      ❌ 不存在
v0.4_results/      ❌ 不存在
```

**说明**：两个目录均未创建，符合当前阶段预期。根据 R02 §9 待作者确认事项，需要先确认：

1. 是否创建新代码区 `项目重启_v0.4_BlenderOCS/06_v0.4_code/`
2. 输出根目录采用哪个方案：
   - 方案 A：`v0.4_results/`（与 14 号一致）
   - 方案 B：`07_v0.4_results/`（与当前顶层编号结构更一致，但需小修 14 号）

#### 2.1.2 三部件 STL 文件

**核对结果**：

```text
路径：D:\我的文件\研究生学术\光学项目\0506新\建模\真实模型\

✅ jinshuzhuti.stl       存在（22.98 MB，2026-05-06）
✅ taiyangnengban.stl    存在（841 KB，2026-05-06）
✅ yinshenban.stl        存在（252 KB，2026-05-06）
```

**说明**：三部件 STL 文件完整存在，与历史快照 config.py 中定义的路径一致。

#### 2.1.3 Blender 可执行文件

**核对结果**：

```text
路径：D:\Program Files\Blender Foundation\Blender 4.2\

✅ blender.exe           存在（Blender 4.2）
```

**说明**：Blender 4.2 可执行文件存在，与历史快照 config.py 中定义的路径一致。同时发现系统中还安装有 Blender 5.0，但历史代码使用 4.2 版本。

#### 2.1.4 历史代码快照

**核对结果**：

```text
路径：03_项目说明与规划材料/05_参考材料/01_关键代码快照/

✅ 01_code/            存在（含 config.py, materials.py, geometry.py）
✅ 02_blender/         存在
✅ 03_inversion/       存在
✅ 补充实验代码/       存在
```

**说明**：历史代码快照完整保存，可作为 v0.4 代码复用参考。

---

### 2.2 历史代码可复用内容与必须改动点

#### 2.2.1 config.py

**可复用内容**：

1. **路径配置结构**：
   - `PROJECT_ROOT`、`STL_DIR`、`PART_FILES` 字典结构
   - `BLENDER_EXE` 路径定义
   - 三部件 STL 路径映射（路径已确认存在）

2. **物理参数**：
   - `UNIT_SCALE = 1e-3`（mm → m）
   - `SUN_VECTOR`、`DET_VECTOR` 方向定义结构
   - `OBS_GEOMETRIES` 多几何定义结构（5 组 sun/det 配置）

3. **图表样式与双语标签**：
   - `FIG_DPI`、`LANG_MODE`、`LABELS`、`TITLES`、`PART_LABELS`、`PART_COLORS`
   - `get_bilingual_title()`、`get_part_label()`、`dump_config()` 函数

**必须改动点**：

| 项 | 历史值 | v0.4 冻结值 | 依据 |
|---|---|---|---|
| `NUM_YAW` | 73 | **72** | 13 号冻结规范；yaw ∈ [0°, 355°]，步长 5°，不含 360° |
| `YAW_RANGE` | (0, 360) | **(0, 355)** | 同上；72 yaw × 37 pitch = 2664 姿态 |
| `SCAN_2D` | True | 保持 True | 继续 2D 网格扫描 |
| `PITCH_RANGE` | (-90, 90) | 保持 (-90, 90) | 37 pitch，步长 5° |
| `NUM_PITCH` | 37 | 保持 37 | 冻结值 |
| `ACCURACY_LEVEL` | "fast" | **待定**（smoke test 用 256×256 full） | Phase 0 不抽稀 |
| `BRDF_MODEL` | "ggx" | **"phong_like_five_param"** | R02/R04：路线一 C 主线为 Phong-like，GGX 作为对照分支 |
| `EPSILON` | 1.0 (mm) | **待定**（depth_epsilon_m 与 NoL/NoV eps 需分离）| 13 号：NoL/NoV eps = 1e-6；depth_epsilon_m_initial = 1e-3 m |
| `ENABLE_RENDER` | False | 保持 False | v0.4 渲染交由 Blender，Python 只做后处理 |
| `OUTPUT_DIR` | `结果/模块A_重构` | **`v0.4_results/`** | 14 号规范；待作者确认方案 A 或 B |

**关键冲突点**：

1. **yaw 网格**：历史 73 yaw（含 360°）必须改为 72 yaw（不含 360°），否则产生 2701 姿态而非冻结的 2664 姿态
2. **BRDF 主线**：历史默认 GGX，但 R02/R04 明确路线一 C 主线为 Phong-like / 五参数冯，GGX 只作为 mismatch 对照分支
3. **epsilon 语义**：历史 `EPSILON = 1.0 mm` 用于法向偏移，但 v0.4 需要区分：
   - NoL/NoV 有效像素阈值：`eps = 1e-6`（13 号 §6.4）
   - depth_epsilon_m：`initial = 1e-3 m`，`final` 由 20 姿态校准确定（13 号 §7.3.3）

---

#### 2.2.2 materials.py

**可复用内容**：

1. **数据库结构**：
   - `MATERIAL_DB` 字典格式（部件名 → BRDF 参数）
   - `_GGX_DB` 字典（GGX 材料参数）
   - `get_material()` 函数结构（use_ggx 开关）

2. **GGX 材料参数**（对照分支用）：
   ```python
   _GGX_DB = {
       "jinshuzhuti":    {"brdf_model": "ggx", "base_color": 0.91, "metallic": 1.0, "roughness": 0.20, "F0": 0.91},
       "taiyangnengban": {"brdf_model": "ggx", "base_color": 0.15, "metallic": 0.0, "roughness": 0.40, "ior": 1.5},
       "yinshenban":     {"brdf_model": "ggx", "base_color": 0.08, "metallic": 0.0, "roughness": 0.90, "ior": 1.5},
   }
   ```

   **注意**：根据 01_代码阶段资产盘点，这些参数已与 13 号 §9.3 一致，可直接复用作为 GGX 对照分支。

3. **Legacy Phong 参数**（作为 B0 baseline 候选）：
   ```python
   MATERIAL_DB = {
       "jinshuzhuti":    {"brdf_model": "legacy_phong", "rho_d": 0.20, "rho_s": 0.60, "n": 80},
       "taiyangnengban": {"brdf_model": "legacy_phong", "rho_d": 0.15, "rho_s": 0.10, "n": 20},
       "yinshenban":     {"brdf_model": "legacy_phong", "rho_d": 0.08, "rho_s": 0.02, "n": 10},
   }
   ```

   **关键公式**（代码注释中）：
   ```python
   f_r = rho_d / π  +  rho_s * (cos α)^n
   ```
   其中 α 为半程向量 h = (s + d)/|s + d| 与法向量的夹角。

4. **brdf_value() 函数**：
   - 标量/向量化 BRDF 计算
   - 支持 (3,) 单个法向量或 (N,3) 批量法向量

**必须改动点与关键判断**：

| 项 | 历史状态 | v0.4 路线一 C 要求 | 依据 |
|---|---|---|---|
| **主线 BRDF** | Legacy Phong（simple） | **B0: Legacy/simple Phong-like baseline** | R04 §5.2：路线一 C 可用 Legacy Phong 作为 B0 provisional baseline |
| **参数来源** | 代码内置 nominal 值 | **项目 provisional 参数，不得称为书中参数** | R04 §4、§5.1：书中三部件对应材料参数尚未可靠定位 |
| **书中模型关系** | 注释称 "Phong 简化模型" | **禁止等同于书中改进冯或 Torrance-Sparrow 五参数模型** | R04 §4 表格、§5.2：Legacy Phong 与书中模型不等同 |
| **后续分支** | 只有 GGX | **B0→B1→B2 三层分支** | R04 §5.3：B0=baseline，B1=书中改进冯，B2=T-S 五参数/六参数 |

**关键结论**：

根据 R04 §5.2、§8 最终判定：

```text
路线一 C 当前不得声称已经获得书中三部件材料参数。
路线一 C 可继续用 Legacy/simple Phong-like provisional baseline 推进最小链路，
但必须标注边界：project provisional Phong-like baseline (B0)，
不得称为"完整书中五参数冯模型实现"。
```

历史 materials.py 中的 `MATERIAL_DB` 参数：

- `rho_d`、`rho_s`、`n` 为项目早期 nominal 参数
- **不是**书中第 3 章 56-59 页改进冯模型的 `rho_d, rho_s, alpha, a, b`
- **不是**书中第 3 章 63-64 页 Torrance-Sparrow 五参数模型的 `k_b, k_r, b, a, k_d`
- **不是**书中材料表中的实测参数（表未定位到）

因此，v0.4 执行口径必须为：

```text
1. B0 阶段：使用历史 MATERIAL_DB 中的 Legacy Phong 参数作为 provisional baseline
2. 标注为：project provisional Phong-like baseline，参数来自历史项目 nominal 值
3. 不声称：书中材料参数主锚点、书中五参数冯、书中改进模型
4. manifest 字段：brdf_model = "phong_like_provisional_baseline"（或类似明确标注）
5. 后续升级：B1（书中改进冯）、B2（T-S 五参数）需作者确认材料对应关系后实现
```

---

#### 2.2.3 geometry.py

**可复用内容**：

1. **欧拉角转旋转矩阵**：
   - `euler_to_matrix(yaw, pitch, roll, degrees=True)` 函数
   - Z-Y-X 内旋顺序（M→I）
   - 支持角度/弧度输入

2. **STL 加载与抽稀**：
   - `_load_as_mesh(filepath)`：兼容 trimesh.Scene 和 trimesh.Trimesh
   - `_simplify_mesh(mesh, target_faces)`：兼容不同 trimesh 版本的 API
   - `load_meshes(part_files, accuracy_level, verbose)`：批量加载与抽稀

3. **精度抽稀逻辑**：
   - 按 `DECIMATE_RATIO` 控制面元保留比例
   - fast=20%，medium=50%，full=100%

**必须改动点**：

| 项 | 历史状态 | v0.4 要求 | 说明 |
|---|---|---|---|
| **姿态生成** | 无专门函数 | **需新增 `attitude_grid.py`** | 生成 72×37 姿态网格、record_id 构建 |
| **ortho_scale** | 未体现 | **需整合 `ortho_scale = 2.2 × r_max`** | 13 号冻结规范 |
| **resolution** | 未体现 | **需整合 `resolution = 256×256`** | 13 号冻结规范 |
| **世界坐标系约定** | 隐含在代码中 | **需明确记录并与 Blender 对齐** | 避免 sun shadow reprojection 系统性错位 |

**可直接复用**：

- `euler_to_matrix()` 函数无需修改，已符合 13 号世界坐标系约定
- `load_meshes()` 结构可复用，但 Phase 0 smoke test 应使用 `accuracy_level = "full"`（不抽稀）

**需要补充**：

根据 01_代码阶段资产盘点 §2.2，v0.4 需要在 `06_v0.4_code/01_geometry/` 中新增：

```text
attitude_grid.py：
  - 生成 72 yaw × 37 pitch 姿态网格
  - 构建 record_id = f"yaw{yaw:03d}_pitch{pitch:+04d}"
  - 支持绘图时 yaw 复制 0° 为 360°（heatmap seam）
```

---

### 2.3 BRDF 执行口径核对

#### 2.3.1 当前 BRDF 主线判定

根据 R02 §3.2、R04 §5.2、R04 §8 最终判定：

```text
路线一 C BRDF 主线 = B0: Legacy/simple Phong-like provisional baseline
```

**B0 定义**：

- 公式：`f_r = rho_d / π + rho_s * (N·H)^n`
- 参数来源：历史 materials.py 中的 `MATERIAL_DB`（项目 provisional 参数）
- 不等同于：
  - 书中第 56-59 页改进冯模型（式 3.16，参数 rho_d, rho_s, alpha, a, b）
  - 书中第 63-64 页 Torrance-Sparrow 五参数模型（式 3.18，参数 k_b, k_r, b, a, k_d）
  - 书中第 67 页改进六参数模型（式 3.23，参数 k_b, k_r, k_d, a, b, c）

**执行边界**：

| 允许 | 禁止 |
|---|---|
| ✅ 使用历史 Legacy Phong 参数作为 B0 baseline | ❌ 声称"已采用书中材料参数" |
| ✅ 标注为 "project provisional Phong-like baseline" | ❌ 声称"完整书中五参数冯模型实现" |
| ✅ 用于 smoke test 和最小链路闭合 | ❌ 等同于书中改进冯或 T-S 五参数 |
| ✅ 后续升级为 B1（书中改进冯）、B2（T-S） | ❌ 混用 Legacy Phong 与书中模型名称 |

#### 2.3.2 GGX 分支定位

根据 R02 §3.2、§5.5：

```text
GGX/Cook-Torrance = mismatch 对照分支，不进入 smoke test 主线成功判据
```

**GGX 执行策略**：

- 保留历史 `_GGX_DB` 参数（已与 13 号 §9.3 一致）
- 作为后续 mismatch、现代 PBR 对照和鲁棒性分支
- 不作为路线一 C smoke test 的主线 BRDF
- manifest 字段：`brdf_branch = "mismatch_control"`

#### 2.3.3 BRDF 三层分支规划（R04 §5.3）

```text
B0：Legacy/simple Phong-like baseline
    参数来自历史 materials.py 或作者给定 provisional 参数
    用于路线一 C smoke test 和最小链路闭合

B1：书中改进冯模型
    对应第 3 章 56-59 页，式 (3.16)，参数 rho_d, rho_s, alpha, a, b
    作为后续升级分支
    需作者确认三部件材料与书中材料对应关系

B2：Torrance-Sparrow 五参数 / 改进六参数模型
    对应第 3 章 63-67 页，式 (3.18)、式 (3.23)
    作为后续材料 BRDF 专项分支
    不作为当前最小 smoke test 的必要条件
```

**当前阶段**：只实现 B0，B1/B2 待作者确认后作为独立分支。

---

### 2.4 manifest 字段与 13/14 冲突核对

#### 2.4.1 BRDF 主线字段冲突

根据 R02 §3.2、§5.5：

**13/14 冻结规范现状**：

- 13 号 §9：主模型示例为 `GGX/Cook-Torrance BRDF`
- 14 号 OCS manifest：`brdf_model = "ggx_cook_torrance"`
- 14 号 source_data：`brdf_model = "ggx_cook_torrance"`

**路线一 C 新裁决**：

- 主线：Phong-like / 五参数冯
- GGX：mismatch / 对照分支

**冲突判定**：

```text
这是 2026-06-22 路线一 C 新裁决与旧 13/14 方法冻结文件之间的明确冲突。
```

**R02 §3.2 临时执行口径**：

```text
执行路线一 C 时，BRDF 主线按路线一 C 新裁决采用 Phong-like / 五参数冯；
GGX 保留为 mismatch / 对照分支；
13/14 中以 GGX 为主模型的字段和文字暂记为待受控小修冲突点；
未经作者确认，不直接改 13/14。
```

**R02 §5.5 临时 manifest 字段策略**：

```python
brdf_model = "phong_like_five_param"    # 路线一 C 主线（注意：实际为 B0 baseline）
brdf_branch = "main_anchor"
brdf_reference = "project_provisional_params"  # 不写 "book_material_params"
ggx_branch = "mismatch_control"         # 后续对照分支
```

**待作者确认**：是否后续受控小修 13/14 的 BRDF 主线字段。

#### 2.4.2 输出目录冲突

根据 R02 §5.6：

**14 号规范**：
```text
v0.4_results/
```

**前期讨论与 Claude 输出**：
```text
07_v0.4_results/
```

**R02 判定**：

```text
在未小修 14 号前，正式执行优先沿用 14 号的 v0.4_results/；
若作者更希望使用 07_v0.4_results/ 以匹配当前顶层编号结构，应作为受控小修点列出；
Claude 不得自行选择输出根目录。
```

**待作者确认**：方案 A（`v0.4_results/`）或方案 B（`07_v0.4_results/`）。

---

## 三、创建代码区前待确认问题清单

根据本次核对，创建 `06_v0.4_code/` 前仍需 Codex/作者确认以下问题：

### 3.1 目录创建与命名（优先级 P0）

**问题 1**：是否创建新代码区？

```text
拟议路径：项目重启_v0.4_BlenderOCS/06_v0.4_code/
```

**依据**：R02 §9 待作者确认事项第 1 条。

---

**问题 2**：输出根目录采用哪个方案？

```text
方案 A：v0.4_results/      （与 14 号一致，R02 推荐）
方案 B：07_v0.4_results/   （与当前顶层编号结构更一致，但需小修 14 号）
```

**依据**：R02 §5.6、§9 待作者确认事项第 2 条。

**影响**：所有 manifest 中的输出路径、代码中的 OUTPUT_DIR 定义、14 号示例路径。

---

### 3.2 BRDF 执行口径（优先级 P0）

**问题 3**：是否同意路线一 C 执行层临时覆盖 13/14 的 GGX 主线字段？

```text
路线一 C 执行口径：
  主线：Phong-like / 五参数冯（实际为 B0 provisional baseline）
  GGX：mismatch / 对照分支

13/14 冻结规范现状：
  主线：GGX/Cook-Torrance
```

**依据**：R02 §3.2、§9 待作者确认事项第 3 条。

**临时策略**（R02 建议）：
- 执行时按路线一 C 新裁决，使用 B0 Phong-like baseline
- 13/14 中以 GGX 为主模型的字段暂记为待受控小修冲突点
- 未经确认，不直接改 13/14

---

**问题 4**：是否接受路线一 C 先用 B0 Legacy/simple Phong-like provisional baseline 推进 smoke test？

```text
B0 定义：
  公式：f_r = rho_d / π + rho_s * (N·H)^n
  参数来源：历史 materials.py 中的项目 provisional 参数
  标注为：project provisional Phong-like baseline
  不声称：书中材料参数、书中五参数冯、书中改进模型
```

**依据**：R04 §6 待作者确认事项第 1 条、R04 §8 最终判定。

**边界声明**：
- 当前不得声称已经获得书中三部件材料参数
- 必须标注为 project provisional Phong-like baseline (B0)
- 不得称为"完整书中五参数冯模型实现"

---

**问题 5**：是否需要后续把第 59 页式 (3.16) 作为 B1 实现目标？

```text
B1：书中改进冯模型
  对应第 3 章 56-59 页，式 (3.16)
  参数：rho_d, rho_s, alpha, a, b
```

**依据**：R04 §6 待作者确认事项第 2 条。

**前置条件**：需要作者提供或确认三部件材料与书中材料的对应关系。

---

**问题 6**：是否需要后续把第 64 页式 (3.18) 或第 67 页式 (3.23) 作为独立 BRDF 对照分支？

```text
B2：Torrance-Sparrow 五参数 / 改进六参数模型
  对应第 3 章 63-67 页
  式 (3.18)：k_b, k_r, b, a, k_d
  式 (3.23)：k_b, k_r, k_d, a, b, c
```

**依据**：R04 §6 待作者确认事项第 3 条。

**定位**：作为后续材料 BRDF 专项分支，不作为当前最小 smoke test 的必要条件。

---

**问题 7**：是否能提供或确认三部件材料与书中材料的对应关系？

```text
三部件：jinshuzhuti、taiyangnengban、yinshenban

书中第 3 章材料（已确认有参数反演样例）：
  - 有机黑漆（60 页，改进冯参数）
  - 环氧漆（63 页，五参数；68 页，六参数）
  - 银色聚酰亚胺薄膜（69 页，六参数）
  - 有机白漆（70 页，六参数）

书中表 3.1（55 页，BRDF 峰值表）材料：
  - 有机黑漆
  - 环氧漆
  - 金色聚酰亚胺薄膜
  - 银色聚酰亚胺薄膜

未在本次原图中确认的材料：
  - 太阳能电池阵
  - 铝合金表面
  - MLI / 多层隔热膜
  - 隐身板 / 吸波材料 / 低反射率涂层
```

**依据**：R04 §3.5、§6 待作者确认事项第 4 条。

**影响**：若无对应关系，B1/B2 分支只能作为方法对照，不能声称"采用书中三部件材料参数"。

---

**问题 8**：是否需要把外部原始图片复制进项目内部证据区，作为后续知识库小修依据？

```text
外部原始图片路径：
  D:\我的文件\研究生学术\光学项目\书籍工作\书籍\第三章\

拟议项目内部证据区：
  03_项目说明与规划材料/05_参考材料/02_书籍证据/第三章原始图片/
```

**依据**：R04 §6 待作者确认事项第 5 条。

**目的**：避免后续依赖外部路径，保持项目自包含。

---

### 3.3 manifest 字段与 13/14 小修（优先级 P1）

**问题 9**：是否后续受控小修 13/14 中的 BRDF 主线字段和输出目录字段？

```text
待小修内容（如采用方案 B 和路线一 C BRDF 主线）：
  
  13 号 §9：GGX/Cook-Torrance BRDF 主模型
    → 改为：Phong-like / 五参数冯主模型，GGX 作为对照分支
  
  14 号 OCS manifest：brdf_model = "ggx_cook_torrance"
    → 改为：brdf_model = "phong_like_provisional_baseline"（或类似）
  
  14 号输出根目录示例：v0.4_results/
    → 改为：07_v0.4_results/（如采用方案 B）
```

**依据**：R02 §9 待作者确认事项第 4 条。

**时机**：路线一 C 代码任务清单确认后，另行受控处理。

---

### 3.4 环境依赖与资源估算（优先级 P0）

**问题 10**：单姿态 smoke test 前是否需要先记录环境依赖？

```text
拟议记录位置：
  06_v0.4_code/00_config/environment.md
  06_v0.4_code/00_config/environment.yml
```

**记录内容**：
- Blender 版本（当前确认为 4.2）
- Python / conda 环境名
- PyTorch / CUDA / GPU 型号
- 关键 Python 包版本（trimesh, numpy, PIL 等）

**依据**：01_代码阶段资产盘点 §四.0、00_重跑任务清单 §2.1 阶段 0。

---

**问题 11**：smoke test 资源估算的输出格式？

```text
拟议输出位置：
  v0.4_results/00_validation/phase0_smoke_test_report.md
  v0.4_results/00_validation/resource_estimate.json
```

**记录内容**：
- 单姿态耗时（camera/sun geometry pass + reprojection + BRDF 后处理）
- 单姿态存储体量（EXR/PNG/npy 总大小）
- single-geom 2664 姿态粗估（耗时/存储）
- multi-geom 额外 4 组粗估

**依据**：01_代码阶段资产盘点 §四.0、02_第一批最小验证任务清单 §2.1。

---

### 3.5 Phase 0 gate 执行顺序（优先级 P0）

**问题 12**：是否按以下顺序执行 Phase 0 gate？

```text
Step 0：环境记录 + 单姿态 smoke test（0.5-1 天）
  ↓
Step 1：depth round-trip sanity check（必须通过）
  ↓
Step 2：3 姿态 camera geometry / Position / sun depth 检查（辅助诊断）
  ↓
Step 3：20 姿态 shadow validation + depth_epsilon_m_final 校准（必须通过）
  ↓
Step 4：5 姿态 V_sun_macro 对图像影响检查（辅助诊断）
  ↓
Step 5：BRDF/OCS/image 后处理 3 姿态试跑（必须通过）
  ↓
【gate 通过，进入全量生成】
```

**依据**：02_第一批最小验证任务清单 §五、01_代码阶段资产盘点 §四。

**硬 gate 失败处理**（CR-CODE-001 修正）：
- 任一硬 gate 失败：不进入全量生成
- 20 姿态中任一姿态失败：整体降级为 Level 1，或修正实现并重测全部 20 姿态
- 不允许排除失败姿态后继续以 Level 2 通过

---

### 3.6 历史代码复用策略（优先级 P1）

**问题 13**：历史代码复用时是否采用以下策略？

```text
可直接复用（结构/逻辑层）：
  - geometry.py：euler_to_matrix(), load_meshes()
  - materials.py：_GGX_DB（GGX 对照分支），MATERIAL_DB（B0 baseline）
  - config.py：路径配置、双语标签、图表样式函数

必须改动：
  - config.py：NUM_YAW = 72（不是 73）
  - config.py：BRDF_MODEL = "phong_like_provisional_baseline"（不是 "ggx"）
  - config.py：epsilon 语义分离（NoL/NoV eps vs depth_epsilon_m）
  - config.py：OUTPUT_DIR = "v0.4_results/" 或 "07_v0.4_results/"

必须重写：
  - ocs_core.py：改为从 Blender EXR pixel-level 读取 V_sun_macro 后计算 OCS
  - run_multi_geom.py：改为 72 yaw、每个 geom 生成 camera/sun geometry pass
  - render_geometry_passes.py：新增 Position/WorldCoord pass、sun-view depth 渲染
  - train_*.py：新增 14 号 §8.1 一致性检查、source_data.json 生成

不可复用（已废弃）：
  - adaptive_integration.py：face-level adaptive 已废弃
  - diag_subface_adaptive.py：诊断旧口径差异，已完成历史任务
```

**依据**：01_代码阶段资产盘点 §一。

---

## 四、核对总结

### 4.1 资源就绪状态

| 资源类型 | 状态 | 说明 |
|---|---|---|
| 三部件 STL | ✅ 就绪 | jinshuzhuti.stl、taiyangnengban.stl、yinshenban.stl 存在 |
| Blender 4.2 | ✅ 就绪 | blender.exe 存在，路径与历史代码一致 |
| 历史代码快照 | ✅ 就绪 | config.py、materials.py、geometry.py 完整保存 |
| 06_v0.4_code/ | ❌ 未创建 | 待作者确认后创建 |
| v0.4_results/ | ❌ 未创建 | 待作者确认命名方案后创建 |

### 4.2 关键改动点汇总

| 模块 | 必须改动项 | 冻结依据 |
|---|---|---|
| config.py | NUM_YAW = 72（不是 73） | 13 号冻结规范，72×37=2664 姿态 |
| config.py | BRDF_MODEL 主线改为 Phong-like | R02/R04：路线一 C 主线 |
| materials.py | 标注为 B0 provisional baseline | R04 §5.2、§8：不声称书中参数 |
| 新增模块 | attitude_grid.py、sun_shadow_reprojection.py 等 | 01_代码阶段资产盘点 §2.2 |

### 4.3 BRDF 执行口径确认

根据 R04 §8 最终判定：

```text
✅ 当前只能按 B0 provisional Phong-like baseline 推进
✅ 必须标注为 project provisional baseline
❌ 不得声称已采用书中材料参数
❌ 不得声称完整书中五参数冯模型实现
⏸  B1（书中改进冯）、B2（T-S 五参数）待作者确认材料对应关系
```

**manifest 字段建议**：

```json
{
  "brdf_model": "phong_like_provisional_baseline",
  "brdf_branch": "B0_baseline",
  "brdf_reference": "project_provisional_params_from_legacy_materials_py",
  "brdf_parameters": {
    "jinshuzhuti": {"rho_d": 0.20, "rho_s": 0.60, "n": 80},
    "taiyangnengban": {"rho_d": 0.15, "rho_s": 0.10, "n": 20},
    "yinshenban": {"rho_d": 0.08, "rho_s": 0.02, "n": 10}
  },
  "brdf_caveat": "Provisional baseline parameters, not from book material tables"
}
```

### 4.4 待确认问题优先级

**P0（必须确认才能创建代码区）**：
1. 是否创建 `06_v0.4_code/`
2. 输出目录方案 A 或 B
3. 是否接受 B0 baseline 推进 smoke test
4. Phase 0 gate 执行顺序
5. 环境依赖记录

**P1（可在代码区创建后、实施前确认）**：
6. 是否后续实现 B1/B2 分支
7. 三部件与书中材料对应关系
8. 是否复制外部原始图片进项目
9. 是否小修 13/14
10. 历史代码复用策略

### 4.5 红线确认

本次核对过程严格遵守以下红线：

- ✅ 只执行核对，未做路线设计
- ✅ 未做阶段放行判定
- ✅ 未修改任何文件（包括冻结文件）
- ✅ 未创建 06_v0.4_code/ 或 v0.4_results/ 目录
- ✅ 未写代码实现
- ✅ 明确当前 BRDF 只能按 B0 provisional baseline 推进
- ✅ 列出所有待 Codex/作者确认的问题

---

## 五、下一步建议

根据本次核对结果，建议下一步由 Codex 执行：

1. **审阅本核对报告**，确认核对结论是否准确
2. **裁决待确认问题**，特别是 P0 优先级问题（问题 1-5、10-12）
3. **生成 Claude 执行提示词**，指导创建代码区、环境记录和单姿态 smoke test
4. **若需要小修 13/14**，列出具体修改范围并另行提交作者确认

本核对报告不进入执行阶段，不创建任何目录或代码文件，等待 Codex 审阅与作者确认。

---

**核对完成时间**：2026-06-23
**核对执行者**：Claude（按 1C-E03 任务要求）
**核对范围**：代码区创建前执行入口、资源就绪性、BRDF 口径、待确认问题清单
**核对结论**：资源就绪，BRDF 口径明确为 B0 baseline，13 个待确认问题已列出，等待 Codex/作者裁决


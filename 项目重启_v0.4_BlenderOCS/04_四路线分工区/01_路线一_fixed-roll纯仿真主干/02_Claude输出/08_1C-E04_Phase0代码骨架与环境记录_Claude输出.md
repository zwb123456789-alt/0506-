# 1C-E04：路线一C Phase 0 代码骨架与环境记录创建

执行时间：2026-06-23
任务性质：执行型任务，按 Codex 指定创建代码骨架与环境记录

---

## 一、任务概述

本次任务依据 R05 Codex 审阅第 6 节提示词，执行以下工作：

1. 创建 `06_v0.4_code/` 目录结构
2. 创建 `v0.4_results/00_validation/` 验证输出目录
3. 创建基础配置文件（environment.md、config_v0_4.py、materials_v0_4.py）
4. 创建几何加载模块（geometry_loader.py、attitude_grid.py）
5. 记录环境依赖与 Phase 0 入口说明

**严格遵守红线**：
- 不修改 13/14/24/25 冻结文件
- 不修改 CLAUDE.md 或书籍知识库
- 不启动 Blender 渲染
- 不生成任何数据
- 不训练任何模型
- 不把 B0 写成书中五参数冯

---

## 二、执行结果

### 2.1 目录结构创建

✅ **已创建以下目录**：

```text
06_v0.4_code/
├── 00_config/
├── 01_geometry/
├── 02_blender/
├── 03_brdf/
├── 04_sun_shadow/
├── 05_postprocess/
├── 06_manifest/
└── 10_validation/

v0.4_results/
└── 00_validation/
```

所有目录均创建成功，符合 R05 §5 允许创建范围。

---

### 2.2 配置文件创建

#### 2.2.1 environment.md

✅ **已创建**：`06_v0.4_code/00_config/environment.md`

**记录内容**：
- 操作系统：Windows 11 Home China 10.0.26200
- Python：3.12.7
- Conda：24.9.2
- Blender：4.2（路径已验证存在）
- GPU：NVIDIA GeForce RTX 5060 Laptop GPU，8151 MiB，驱动 591.44
- CUDA：未获取（待实际运行时确认）
- Python 关键包：待 smoke test 时记录

**状态说明**：
- 基础环境信息已记录
- 依赖包版本待后续补充（当前未安装实际依赖）
- 提供了依赖包安装建议和环境更新说明

#### 2.2.2 config_v0_4.py

✅ **已创建**：`06_v0.4_code/00_config/config_v0_4.py`

**主要配置**：

| 配置项 | 值 | 说明 |
|---|---|---|
| `NUM_YAW` | 72 | 0°-355°，步长 5°，**不含 360°** |
| `NUM_PITCH` | 37 | -90°-90°，步长 5° |
| `TOTAL_ATTITUDES` | 2664 | 72 × 37 |
| `RESOLUTION` | 256 | 256×256 |
| `ORTHO_SCALE_FACTOR` | 2.2 | 2.2 × r_max |
| `BRDF_MODEL` | "phong_like_provisional_baseline" | **B0 主线** |
| `EPS_NOL_NOV` | 1e-6 | NoL/NoV 有效像素阈值 |
| `DEPTH_EPSILON_M_INITIAL` | 1e-3 | depth 比较初始容差（m） |
| `DEPTH_EPSILON_M_FINAL` | None | 待 20 姿态校准 |
| `SUN_VISIBILITY_LEVEL` | "camera_visible_nol_plus_sun_shadow_pass" | Level 2 |
| `SHADOW_MAPPING_METHOD` | "depth_reprojection" | |
| `V_SUN_MACRO_MODE` | "shadow_mask" | Level 2 对应 |
| `LOG1P_ALPHA` | 10.0 | 初始值 |
| `CORPUS_LEVEL_I_SCALE` | None | 待 Pass 1 统计 |
| `OUTPUT_DIR` | `v0.4_results/` | 与 14 号一致 |

**关键改动确认**：
- yaw 从历史 73 改为 72（符合 R05 §4 决策）
- BRDF 主线从 GGX 改为 phong_like_provisional_baseline
- epsilon 语义分离为 EPS_NOL_NOV 和 DEPTH_EPSILON_M
- 输出目录采用 v0.4_results/（与 14 号一致，R05 §4 决策）

#### 2.2.3 materials_v0_4.py

✅ **已创建**：`06_v0.4_code/00_config/materials_v0_4.py`

**BRDF 分支结构**：

```python
# B0: Legacy/simple Phong-like provisional baseline（当前主线）
BRDF_B0_PHONG_LIKE = {
    "jinshuzhuti": {
        "brdf_model": "phong_like_provisional_baseline",
        "rho_d": 0.20, "rho_s": 0.60, "n": 80,
        "brdf_branch": "B0_baseline",
        "brdf_reference": "project_provisional_params_from_legacy_materials_py",
    },
    "taiyangnengban": {
        "brdf_model": "phong_like_provisional_baseline",
        "rho_d": 0.15, "rho_s": 0.10, "n": 20,
        "brdf_branch": "B0_baseline",
        "brdf_reference": "project_provisional_params_from_legacy_materials_py",
    },
    "yinshenban": {
        "brdf_model": "phong_like_provisional_baseline",
        "rho_d": 0.08, "rho_s": 0.02, "n": 10,
        "brdf_branch": "B0_baseline",
        "brdf_reference": "project_provisional_params_from_legacy_materials_py",
    },
}

# GGX 对照分支（mismatch_control）
BRDF_GGX_MISMATCH = {
    "jinshuzhuti": {
        "brdf_model": "ggx_cook_torrance",
        "base_color": 0.91, "metallic": 1.0, "roughness": 0.20, "F0": 0.91,
        "brdf_branch": "mismatch_control",
        "brdf_reference": "legacy_ggx_params_aligned_with_13_sec9_3",
    },
    # ... 其他部件
}
```

**边界标注确认**：
- ✅ 明确标注为 "project_provisional_params_from_legacy_materials_py"
- ✅ 不声称书中材料参数
- ✅ 不等同于书中改进冯或 Torrance-Sparrow 五参数模型
- ✅ GGX 标注为 mismatch_control 对照分支
- ✅ B1/B2 预留但未实现（待书中材料对应关系确认）

**BRDF 公式**：
```python
# B0 公式：f_r = rho_d / π + rho_s * (N·H)^n
def brdf_b0_phong_like(normal, sun_dir, det_dir, mat: dict) -> np.ndarray:
    h_vec = (sun_dir + det_dir) / |sun_dir + det_dir|
    cos_alpha = max(N·H, 0)
    return (mat["rho_d"] / np.pi) + mat["rho_s"] * (cos_alpha ** mat["n"])
```

---

### 2.3 几何模块创建

#### 2.3.1 geometry_loader.py

✅ **已创建**：`06_v0.4_code/01_geometry/geometry_loader.py`

**主要功能**：

1. **euler_to_matrix(yaw, pitch, roll, degrees=True)**
   - Z-Y-X 内旋（M→I）
   - 从历史 geometry.py 直接迁移，无修改

2. **_load_as_mesh(filepath)**
   - STL 加载，兼容 trimesh.Scene 和 trimesh.Trimesh
   - 从历史 geometry.py 直接迁移

3. **_simplify_mesh(mesh, target_faces)**
   - 网格抽稀，兼容不同 trimesh 版本的 API
   - 尝试位置参数 / face_count / faces 三种接口

4. **load_meshes(part_files, decimate_ratio, verbose)**
   - 批量加载 STL 部件
   - Phase 0 建议使用 decimate_ratio=1.0（不抽稀）

5. **load_meshes_from_config(accuracy_level, verbose)**
   - 从 config_v0_4 读取参数的便捷函数

**兼容性**：
- 兼容不同 trimesh 版本
- 支持 Phase 0 全精度加载（accuracy_level="full"）

#### 2.3.2 attitude_grid.py

✅ **已创建**：`06_v0.4_code/01_geometry/attitude_grid.py`

**主要功能**：

1. **generate_attitude_grid(yaw_range, yaw_step, pitch_range, pitch_step)**
   - 生成 72 yaw × 37 pitch 姿态网格（训练/manifest 用）
   - 返回 yaw_grid、pitch_grid

2. **generate_attitude_list(...)**
   - 生成姿态列表 [(yaw, pitch), ...]，用于循环遍历
   - 默认生成 2664 个姿态

3. **build_record_id(yaw, pitch)**
   - 构建 record_id 字符串："yaw{yyy}_pitch{ppp}"
   - 示例：`build_record_id(45, -30)` → `"yaw045_pitch-030"`

4. **parse_record_id(record_id)**
   - 从 record_id 解析出 yaw 和 pitch

5. **generate_heatmap_grid_with_seam(...)**
   - 生成带 seam 的姿态网格（绘图专用）
   - 追加 360° = 0°，得到 73 yaw（0°-360°）

6. **pad_heatmap_data_for_seam(data, axis)**
   - 为 heatmap 数据填充 seam（复制第一列到末尾）
   - 避免 heatmap 在 0°-360° 边界处出现断裂

7. **get_attitude_grid_info()**
   - 获取姿态网格统计信息

**关键设计**：
- 训练/manifest 使用 72 yaw（不含 360°）
- 绘图使用 73 yaw（含 360°），seam 只用于画图
- record_id 格式统一为 yaw{yyy}_pitch{ppp}

---

### 2.4 验证输出说明

✅ **已创建**：`v0.4_results/00_validation/phase0_entry_notes.md`

**内容概要**：
- 当前阶段：Phase 0 代码骨架创建完成
- 已完成工作：目录结构、配置文件、几何模块
- 未执行工作：未启动渲染、未生成数据、未训练模型
- 关键配置确认：姿态网格 72×37、BRDF B0 baseline、输出目录 v0.4_results/
- 下一步工作：Step 1 单姿态 smoke test → Step 2 depth round-trip → ... → Phase 0 gate 通过
- 待实现模块：Blender 渲染脚本、sun shadow reprojection、BRDF 模型、后处理、manifest 生成
- 依赖包安装提醒：待 smoke test 前安装 trimesh、numpy、Pillow、OpenEXR 等
- 参考文档：列出执行依据、冻结规范和路线指导文档

---

## 三、关键执行确认

### 3.1 yaw 网格修正

✅ **已修正**：
- 历史 config.py：`NUM_YAW = 73`（含 360°）
- v0.4 config_v0_4.py：`NUM_YAW = 72`（不含 360°）
- 姿态总数：从 2701 修正为 2664

### 3.2 BRDF 主线修正

✅ **已修正**：
- 历史 config.py：`BRDF_MODEL = "ggx"`
- v0.4 config_v0_4.py：`BRDF_MODEL = "phong_like_provisional_baseline"`

✅ **边界标注**：
- 明确为 B0 project provisional baseline
- 不声称书中材料参数或书中五参数冯
- GGX 保留为 mismatch_control 对照分支

### 3.3 epsilon 语义分离

✅ **已分离**：
- 历史 config.py：`EPSILON = 1.0`（mm，法向偏移）
- v0.4 config_v0_4.py：
  - `EPS_NOL_NOV = 1e-6`（NoL/NoV 有效像素阈值）
  - `DEPTH_EPSILON_M_INITIAL = 1e-3`（m，depth 比较初始容差）
  - `DEPTH_EPSILON_M_FINAL = None`（待 20 姿态校准）

### 3.4 输出目录确认

✅ **已确认**：
- 采用 `v0.4_results/`（与 14 号一致，R05 §4 决策）
- 未使用 `07_v0.4_results/`

---

## 四、红线遵守情况

### 4.1 未修改冻结文件

✅ **确认未修改**：
- 13_v0.4前向模型冻结规范_最终冻结版.md
- 14_v0.4数据与manifest字段规范_最终冻结版.md
- 24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
- 25_v0.4主线冻结原因备案_为什么采用24号.md

### 4.2 未修改入口文件

✅ **确认未修改**：
- CLAUDE.md
- 书籍知识库任何文件

### 4.3 未执行禁止操作

✅ **确认未执行**：
- 未启动 Blender 渲染
- 未生成 EXR/PNG/npy 数据
- 未运行全量 2664 姿态
- 未训练任何模型
- 未把 B0 写成书中五参数冯或书中材料参数
- 未使用 latest-run 自动发现

---

## 五、环境依赖记录

### 5.1 已获取信息

| 项 | 信息 | 获取方式 |
|---|---|---|
| Python | 3.12.7 | `python --version` |
| Conda | 24.9.2 | `conda --version` |
| GPU | NVIDIA GeForce RTX 5060 Laptop GPU, 8151 MiB | `nvidia-smi` |
| GPU 驱动 | 591.44 | `nvidia-smi` |
| Blender | 4.2 | 文件路径验证 |
| 操作系统 | Windows 11 Home China 10.0.26200 | 系统环境变量 |

### 5.2 未获取信息

以下信息待 smoke test 时补充：
- CUDA 版本
- Python 包版本（numpy、trimesh、Pillow、OpenEXR、torch 等）
- 单姿态渲染耗时
- 单姿态文件体量

---

## 六、下一步建议

### 6.1 立即可执行

**1C-E05：单姿态 smoke test**（待 Codex 提示词）

建议内容：
1. 安装依赖包（trimesh、numpy、Pillow、OpenEXR、imageio、tqdm、matplotlib）
2. 更新 environment.md 中的包版本信息
3. 选择简单姿态（如 yaw=0°, pitch=0°）
4. 编写 Blender 渲染脚本（camera geometry pass 最小版本）
5. 测试 STL 加载、Blender 调用、EXR 读取
6. 记录单姿态耗时和文件体量
7. 输出：`phase0_smoke_test_report.md`、`resource_estimate.json`

### 6.2 后续 Phase 0 gate 顺序

按 02_第一批最小验证任务清单.md 执行：

```text
Step 1：单姿态 smoke test（1C-E05）
  ↓
Step 2：depth round-trip sanity check
  ↓
Step 3：3 姿态几何检查
  ↓
Step 4：20 姿态 shadow validation + depth_epsilon_m_final 校准
  ↓
Step 5：5 姿态 V_sun_macro 对图像影响检查
  ↓
Step 6：BRDF/OCS/image 后处理 3 姿态试跑
  ↓
【Phase 0 gate 通过】
  ↓
Step 7：进入全量生成
```

---

## 七、执行总结

### 7.1 任务完成情况

✅ **已完成**：
1. 创建 `06_v0.4_code/` 目录结构（8 个子目录）
2. 创建 `v0.4_results/00_validation/` 验证输出目录
3. 创建 `environment.md`（环境记录）
4. 创建 `config_v0_4.py`（72 yaw、B0 BRDF 主线）
5. 创建 `materials_v0_4.py`（B0 baseline + GGX 对照分支）
6. 创建 `geometry_loader.py`（STL 加载、euler_to_matrix）
7. 创建 `attitude_grid.py`（72×37 姿态网格、record_id）
8. 创建 `phase0_entry_notes.md`（Phase 0 入口说明）

✅ **红线遵守**：
- 未修改任何冻结文件
- 未启动任何渲染或训练
- 未把 B0 写成书中参数

### 7.2 关键改动确认

| 项 | 历史值 | v0.4 值 | 状态 |
|---|---|---|---|
| yaw 网格 | 73（含 360°） | 72（不含 360°） | ✅ 已修正 |
| 姿态总数 | 2701 | 2664 | ✅ 已修正 |
| BRDF 主线 | GGX | phong_like_provisional_baseline | ✅ 已修正 |
| epsilon | 单一 1.0 mm | EPS_NOL_NOV + DEPTH_EPSILON_M | ✅ 已分离 |
| 输出目录 | `结果/模块A_重构` | `v0.4_results/` | ✅ 已修正 |

### 7.3 当前状态

**Phase 0 状态**：代码骨架与环境记录创建完成

- 目录结构：✅ 完整
- 配置文件：✅ 完整
- 几何模块：✅ 完整
- 待实现模块：Blender 渲染、sun shadow、BRDF 模型、后处理、manifest 生成
- 下一步：单姿态 smoke test（1C-E05）

---

**执行完成时间**：2026-06-23  
**执行者**：Claude（按 R05 §6 提示词）  
**执行范围**：Phase 0 代码骨架与环境记录创建  
**执行结论**：任务完成，红线遵守，等待下一步 1C-E05 单姿态 smoke test

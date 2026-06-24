# Phase 0 入口说明

创建时间：2026-06-23
状态：代码骨架与环境记录创建完成

---

## 1. 当前阶段

**Phase 0：代码骨架与环境记录创建**

本阶段只创建目录结构、基础配置文件和几何加载模块骨架，不启动任何实际渲染、数据生成或训练。

---

## 2. 已完成工作

### 2.1 目录结构创建

```text
06_v0.4_code/
├── 00_config/          ✅ 已创建
│   ├── environment.md
│   ├── config_v0_4.py
│   └── materials_v0_4.py
├── 01_geometry/        ✅ 已创建
│   ├── geometry_loader.py
│   └── attitude_grid.py
├── 02_blender/         ✅ 已创建（空目录）
├── 03_brdf/            ✅ 已创建（空目录）
├── 04_sun_shadow/      ✅ 已创建（空目录）
├── 05_postprocess/     ✅ 已创建（空目录）
├── 06_manifest/        ✅ 已创建（空目录）
└── 10_validation/      ✅ 已创建（空目录）

v0.4_results/
└── 00_validation/      ✅ 已创建
    └── phase0_entry_notes.md（本文件）
```

### 2.2 配置文件

| 文件 | 状态 | 说明 |
|---|---|---|
| `environment.md` | ✅ 已创建 | 记录 Python 3.12.7、Conda 24.9.2、Blender 4.2、GPU RTX 5060 |
| `config_v0_4.py` | ✅ 已创建 | yaw=72、pitch=37、BRDF=phong_like_provisional_baseline |
| `materials_v0_4.py` | ✅ 已创建 | B0 baseline 参数，标注为 project provisional params |

### 2.3 几何模块

| 文件 | 状态 | 说明 |
|---|---|---|
| `geometry_loader.py` | ✅ 已创建 | STL 加载、euler_to_matrix()、网格抽稀 |
| `attitude_grid.py` | ✅ 已创建 | 72×37 姿态网格、record_id 构建、绘图 seam 处理 |

---

## 3. 未执行工作

### 3.1 未启动的操作

❌ 未启动 Blender 渲染
❌ 未生成 EXR/PNG/npy 数据
❌ 未执行单姿态 smoke test
❌ 未执行 depth round-trip sanity check
❌ 未执行 20 姿态 shadow validation
❌ 未训练任何模型
❌ 未生成 OCS/image manifest
❌ 未执行全量 2664 姿态生成

### 3.2 未创建的模块

以下模块目录已创建，但内部文件待后续实现：

- `02_blender/`：Blender 渲染脚本（camera/sun geometry pass）
- `03_brdf/`：BRDF 模型实现（B0 Phong-like、GGX）
- `04_sun_shadow/`：sun shadow reprojection、depth round-trip
- `05_postprocess/`：OCS 积分、image 后处理
- `06_manifest/`：OCS/image manifest 生成、一致性检查
- `10_validation/`：Phase 0 gate 验证脚本

---

## 4. 关键配置确认

### 4.1 姿态网格

- yaw: 0°-355°，步长 5°，**共 72 个**（不含 360°）
- pitch: -90°-90°，步长 5°，**共 37 个**
- **姿态总数: 72 × 37 = 2664**

### 4.2 BRDF 主线

- **B0: phong_like_provisional_baseline**
- 参数来源：项目 provisional 参数（历史 materials.py）
- **不声称**：书中材料参数、书中五参数冯、书中改进模型
- GGX：保留为 mismatch_control 对照分支

### 4.3 输出目录

- 输出根目录：`v0.4_results/`（与 14 号规范一致）
- 代码根目录：`06_v0.4_code/`

### 4.4 epsilon 语义

- NoL/NoV 有效像素阈值：`EPS_NOL_NOV = 1e-6`
- depth 比较初始容差：`DEPTH_EPSILON_M_INITIAL = 1e-3 m`
- depth 比较最终容差：`DEPTH_EPSILON_M_FINAL`（待 20 姿态校准）

### 4.5 sun visibility

- 主线：Level 2 (`camera_visible_nol_plus_sun_shadow_pass`)
- 降级预案：Level 1 (`camera_visible_nol`)
- shadow_mapping_method: `depth_reprojection`
- v_sun_macro_mode: `shadow_mask`（Level 2）或 `identity`（Level 1）

---

## 5. 下一步工作

### 5.1 Phase 0 后续步骤（按顺序）

**Step 1：单姿态 smoke test**
- 选择简单姿态（如 yaw=0°, pitch=0°）
- 测试 Blender 调用、EXR 读取、基础后处理
- 记录单姿态耗时和文件体量
- 输出：`phase0_smoke_test_report.md`

**Step 2：depth round-trip sanity check**
- 3 个已知点 camera/sun 双向 round-trip
- 确认 Blender depth 符号、单位、local z 映射
- 输出：`depth_round_trip_report.txt`

**Step 3：3 姿态几何检查**
- camera geometry pass（Normal/Depth/IndexOB）
- Position/WorldCoord pass
- sun-view depth pass
- 输出：`3_attitudes_geometry_check.png`、`3_attitudes_position_check.txt`、`3_attitudes_sun_depth_check.png`

**Step 4：20 姿态 shadow validation**
- V_sun_macro reprojection 物理合理性检查
- depth_epsilon_m_final 校准
- 输出：`20_attitudes_shadow_validation_report.md`

**Step 5：5 姿态 V_sun_macro 对图像影响检查**
- sun-shadowed 像素归零验证
- EXR/PNG 同步检查
- 输出：`5_attitudes_v_sun_macro_on_image_comparison.png`

**Step 6：BRDF/OCS/image 后处理 3 姿态试跑**
- B0 Phong-like BRDF 计算
- OCS 积分
- image linear response + log1p PNG
- 输出：试跑成功记录

**【Phase 0 gate 通过】**
- 所有硬 gate 验证通过
- depth_epsilon_m_final 确定
- 输出：`validation_summary.json`

**Step 7：进入全量生成**
- single-geom 2664 姿态
- multi-geom 4 组额外几何
- corpus-level I_scale 统计（Pass 1）
- 统一 log1p PNG 生成（Pass 2）

### 5.2 待实现模块

按 Step 顺序，需要实现以下模块：

1. `02_blender/render_camera_geometry.py`（Step 1）
2. `02_blender/render_sun_depth.py`（Step 1）
3. `04_sun_shadow/depth_round_trip_check.py`（Step 2）
4. `04_sun_shadow/sun_shadow_reprojection.py`（Step 4）
5. `03_brdf/brdf_models_v0_4.py`（Step 6）
6. `05_postprocess/ocs_integration_v0_4.py`（Step 6）
7. `05_postprocess/image_response_v0_4.py`（Step 6）
8. `06_manifest/ocs_manifest_builder.py`（Step 7）
9. `06_manifest/image_manifest_builder.py`（Step 7）
10. `06_manifest/consistency_checker.py`（Step 7）

---

## 6. 红线确认

本阶段严格遵守以下红线：

- ✅ 未修改 13/14/24/25 冻结文件
- ✅ 未修改 CLAUDE.md
- ✅ 未修改书籍知识库
- ✅ 未把 B0 写成书中五参数冯
- ✅ 未使用 latest-run 自动发现
- ✅ 未启动 Blender 渲染
- ✅ 未生成任何数据
- ✅ 未训练任何模型

---

## 7. 依赖包安装提醒

**待 Step 1（单姿态 smoke test）前安装**：

```bash
# 几何与渲染
pip install trimesh numpy pillow

# EXR 读取
pip install OpenEXR imageio imageio-ffmpeg

# 进度条与可视化
pip install tqdm matplotlib
```

**待训练阶段前安装**：

```bash
# 深度学习
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

安装后需更新 `00_config/environment.md` 中的版本信息。

---

## 8. 参考文档

**执行依据**：
- R05 Codex 审阅：1C-E03 代码区创建前执行入口核对
- 1C-E03 Claude 输出：代码区创建前执行入口核对
- 01_代码阶段资产盘点与实施计划_Claude.md
- 02_第一批最小验证任务清单_Claude.md
- 00_重跑任务清单.md

**冻结规范**：
- 13_v0.4前向模型冻结规范_最终冻结版.md
- 14_v0.4数据与manifest字段规范_最终冻结版.md
- 24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md

**路线指导**：
- 01_路线一_fixed-roll大论文主线与发刊答辩定位.md
- R02_Codex_审阅_1C-C02并重定路线一C设计执行分工.md
- R04_Codex_更正_1C-E02书籍页码与BRDF材料参数定位.md

---

**Phase 0 状态**：代码骨架创建完成，等待 Step 1（单姿态 smoke test）

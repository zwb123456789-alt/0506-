# 路线一 C 代码入口盘点清单 R1 修正版（Claude 输出）

生成时间：2026-06-22
任务编号：1C-C01-R1
执行者：Claude
修正原因：Codex 审阅指出初版对当前代码入口判断过强，需区分历史快照、待确认路径与实际可运行入口

## 0. 上下文恢复确认

已完成轻量上下文恢复，确认以下要点：

1. **当前科学主线**：model-known 条件下，独立 OCS 光度通道与图像成像通道共享同一物理前向模型时，跨几何 OCS 多观测光度向量与图像通道对姿态信息的可观测性、互补性和置信一致性研究。

2. **路线一 C 定位**：保留 v0.4 pixel-level OCS-image 同源前向架构；以五参数冯 / Phong-like BRDF 与书中典型材料参数作为主 BRDF 锚点；以 GGX / Cook-Torrance 作为 BRDF mismatch、现代 PBR 对照和鲁棒性分支；主实验仍为 fixed-roll yaw-pitch controlled benchmark。

3. **当前阶段**：路线一 C 代码入口盘点阶段，Phase 0 门控验证前的准备工作。

## 1. 修正后一句话结论

**当前没有确认的正式 v0.4 可运行代码主入口。**

**已有的是：**
- 历史关键代码快照（位于 `03_项目说明与规划材料/05_参考材料/01_关键代码快照/`）
- 路线一成果区中的代码阶段规划文件（位于 `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/05_全链路重跑_路线一代码与重跑历史/`）
- 13/14 方法与字段冻结规范（位于 `04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/`）

**路线一 C 下一步应：**
1. 先把历史快照中的可复用资产、禁用资产、待新建资产分清楚
2. 由作者/Codex 确认是否创建新的 v0.4 代码区（如 `06_v0.4_code/`）和输出根目录（如 `07_v0.4_results/`）
3. 若确认创建，再按分类表逐步迁移可复用模块、新建缺失模块

**不应再声称"当前主入口清楚"或"可直接运行"。**


## 2. 当前真实文件位置核对表

### 2.1 历史关键代码快照（参考资产，不直接运行）

**位置**：`03_项目说明与规划材料/05_参考材料/01_关键代码快照/`

| 文件路径 | 功能 | 资产类型 |
|---|---|---|
| `01_code/config.py` | 全局配置：路径、姿态网格、几何参数 | 可复用参考 |
| `01_code/materials.py` | 材料 BRDF 参数数据库（_GGX_DB） | 可复用参考 |
| `01_code/geometry.py` | STL 加载、姿态旋转、坐标系 | 可复用参考 |
| `01_code/ocs_core.py` | 模块 A face-center OCS 采样 | 历史禁用 |
| `01_code/main_run.py` | 模块 A 主入口（face-center 链路） | 历史禁用 |
| `01_code/run_multi_geom.py` | 多观测几何批量扫描（旧链路） | 可复用参考（需大幅改造） |
| `01_code/adaptive_integration.py` | face-level adaptive 采样 | 历史禁用 |
| `02_blender/render_batch.py` | Blender headless 批量渲染 | 可复用参考（需升级） |
| `02_blender/brdf_postprocess.py` | BRDF 后处理与 OCS 积分 | 可复用参考（需修改） |
| `02_blender/render_geometry_passes.py` | 几何通道渲染 | 可复用参考（需升级） |
| `02_blender/diag_subface_adaptive.py` | face-center vs pixel-level 对比诊断 | 历史禁用 |
| `02_blender/analyze_consistency.py` | 旧 A/B 一致性检查 | 历史禁用 |
| `03_inversion/inv_common.py` | 反演公共工具：manifest 加载、split 生成 | 可复用参考（需升级） |
| `03_inversion/train_mlp.py` | OCS-only MLP 训练 | 可复用参考（需升级） |
| `03_inversion/train_cnn.py` | image-only CNN 训练 | 可复用参考（需升级） |
| `03_inversion/train_fusion.py` | fusion 训练 | 可复用参考（需升级） |

### 2.2 路线一成果区规划文件（指导文档，非代码）

**位置**：`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/05_全链路重跑_路线一代码与重跑历史/`

| 文件名 | 功能 | 文件类型 |
|---|---|---|
| `00_重跑任务清单.md` | v0.4 全链路重跑任务清单（代码阶段入口版） | 规划文档 |
| `01_代码阶段资产盘点与实施计划_Claude.md` | 代码阶段资产盘点与实施预案 | 规划文档 |
| `02_第一批最小验证任务清单_Claude.md` | Phase 0 gate 验证任务规划 | 规划文档 |
| `03_代码前待决_roll轴与更多几何讨论记录.md` | roll 轴处理与多几何讨论 | 讨论记录 |
| `04_v0.4信息量与置信指标实现规范_最终冻结版.md` | 信息量与置信指标规范 | 冻结规范 |

### 2.3 方法与字段冻结规范文件（方法依据，非代码）

**位置**：`04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/`

| 文件名 | 功能 | 文件类型 |
|---|---|---|
| `13_v0.4前向模型冻结规范_最终冻结版.md` | v0.4 前向模型方法规范 | 冻结规范 |
| `14_v0.4数据与manifest字段规范_最终冻结版.md` | v0.4 数据与 manifest 字段规范 | 冻结规范 |

### 2.4 当前尚未确认/尚未创建的新代码区

**[待作者/Codex确认]** 以下路径尚未确认或创建：

| 拟议路径 | 拟议功能 | 状态 |
|---|---|---|
| `06_v0.4_code/` | v0.4 新代码根目录 | **待确认是否创建** |
| `07_v0.4_results/` | v0.4 运行产物根目录 | **待确认是否创建** |


## 3. 可复用资产、禁用资产、待新建资产三分表

### 3.1 可复用参考资产（来自历史快照，需迁移/改造后才可成为路线一 C 正式入口）

| 历史快照路径 | 功能 | 复用方式 | 需要的改造 |
|---|---|---|---|
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/materials.py` | 材料 BRDF 参数数据库 | **可较直接复用** | [待确认] 检查 _GGX_DB 参数是否与书中材料参数对齐；若对齐可直接迁移 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/geometry.py` | STL 加载、姿态旋转、坐标系 | **可较直接复用** | [待确认] 检查坐标系约定与 13 号规范一致性 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/config.py` | 全局配置 | **需修改后复用** | 必修：NUM_YAW 从 73 改为 72；BRDF_MODEL 支持五参数冯主锚点 + GGX 对照双模式 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/render_geometry_passes.py` | 几何通道渲染 | **需大幅升级** | 必加：Position AOV、sun-view depth 渲染、camera/sun 矩阵记录 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/brdf_postprocess.py` | BRDF 后处理与 OCS 积分 | **需大幅修改** | 必加：V_sun_macro 到 OCS 和图像计算；corpus-level I_scale 两阶段流程 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/render_batch.py` | Blender headless 批量渲染 | **需升级** | 必加：调用新的 camera geometry pass、sun-view depth pass |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/run_multi_geom.py` | 多观测几何批量扫描 | **需大幅改造** | 必改：从 face-center 采样改为调用 Blender 渲染 + Python 后处理流程 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/03_inversion/inv_common.py` | 反演公共工具 | **需升级** | 必升：manifest schema 升级到 14 号规范；新增一致性检查 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/03_inversion/train_mlp.py` | OCS-only MLP 训练 | **需升级** | 必加：生成 source_data.json、六子版本记录 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/03_inversion/train_cnn.py` | image-only CNN 训练 | **需升级** | 必加：生成 source_data.json、六子版本记录 |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/03_inversion/train_fusion.py` | fusion 训练 | **需升级** | 必加：生成 source_data.json、六子版本记录 |

### 3.2 禁用/历史风险资产（不并入路线一 C 主链）

| 历史快照路径 | 功能 | 禁用原因 | 处理方式 |
|---|---|---|---|
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/ocs_core.py` | 模块 A face-center OCS 采样 | 旧版 face-center 采样已废弃，v0.4 改为 pixel-level | **不迁移，保留为历史参考** |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/main_run.py` | 模块 A 主入口（face-center 链路） | 调用旧 ocs_core.py | **不迁移，保留为历史参考** |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/adaptive_integration.py` | face-level adaptive 采样 | 已废弃 | **不迁移，保留为历史参考** |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/diag_subface_adaptive.py` | face-center vs pixel-level 对比诊断 | 历史诊断任务已完成 | **不迁移，保留为历史参考** |
| `03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/analyze_consistency.py` | 旧 A/B 一致性检查 | v0.4 改为 manifest schema 一致性 | **不迁移，保留为历史参考** |

### 3.3 待新建/待确认资产（当前不存在，需从头编写或由作者确认）

| 建议新建模块 | 拟议路径 | 功能 | 必要性 | 依据 |
|---|---|---|---|---|
| sun-view depth 渲染脚本 | **[待确认路径]** `06_v0.4_code/02_blender/render_sun_depth.py` | 渲染 sun-view depth pass | **P0 必做** | 13 号规范 §7.3 |
| sun shadow reprojection 脚本 | **[待确认路径]** `06_v0.4_code/04_sun_shadow/sun_shadow_reprojection.py` | camera depth → world → sun depth 比较，生成 V_sun_macro_mask | **P0 必做** | 13 号规范 §7.3.2 |
| depth round-trip 校验脚本 | **[待确认路径]** `06_v0.4_code/10_validation/depth_round_trip_check.py` | 3 已知点 camera/sun 双向 round-trip 校验 | **P0 gate** | 13 号规范 §7.4.2 |
| 20 姿态 shadow validation 脚本 | **[待确认路径]** `06_v0.4_code/10_validation/validate_20_attitudes.py` | 20 姿态 shadow 物理合理性 + depth_epsilon 校准 | **P0 gate** | 13 号规范 §12.6 |
| 五参数冯 BRDF 主锚点模块 | **[待确认路径]** `06_v0.4_code/03_brdf/phong_five_param.py` | pixel-level 五参数冯公式：f_r = rho_d/π + rho_s·(N·H)^n | **P0 必做** | 书籍知识库 §4.1 |
| GGX BRDF 对照模块 | **[待确认路径]** `06_v0.4_code/03_brdf/ggx_cook_torrance.py` | GGX / Cook-Torrance 作为 mismatch 对照 | **P0 必做** | 可从历史快照 brdf_postprocess.py 提取 |
| OCS manifest builder (v0.4) | **[待确认路径]** `06_v0.4_code/06_manifest/ocs_manifest_builder.py` | 生成符合 14 号规范的 OCS manifest | **P1 必做** | 14 号规范 §3.1 |
| image manifest builder (v0.4) | **[待确认路径]** `06_v0.4_code/06_manifest/image_manifest_builder.py` | 生成符合 14 号规范的 image manifest | **P1 必做** | 14 号规范 §3.2 |
| manifest 一致性检查器 | **[待确认路径]** `06_v0.4_code/06_manifest/consistency_checker.py` | OCS + image manifest 一致性检查 | **P1 必做** | 14 号规范 §8.1 |
| corpus-level I_scale 统计脚本 | **[待确认路径]** `06_v0.4_code/05_postprocess/compute_corpus_i_scale.py` | 两阶段流程第一阶段：统计全局 I_scale | **P1 必做** | 00_重跑任务清单 §1.2 |


## 4. 单姿态 smoke test 概念调用链（非实际可运行命令）

### 4.1 说明

以下是概念性调用链，用于说明路线一 C 的最小验证流程。**所有路径均为拟议路径，当前不存在或未确认，不可直接运行。**

### 4.2 最小输入配置（概念）

```python
# [概念配置，非实际文件]
TARGET_MODEL = "真实模型"  # jinshuzhuti + taiyangnengban + yinshenban
TEST_ATTITUDE = {"yaw": 45.0, "pitch": 30.0, "roll": 0.0}  # fixed-roll
TEST_GEOMETRY = "phase63_backscatter"  # G1 baseline
BRDF_MODE = "phong_five_param"  # 主锚点 [待确认实现]
RESOLUTION = 256
ORTHO_SCALE = 2.2  # × r_max
SUN_VECTOR = [1.0, 0.0, 0.3]
DET_VECTOR = [0.5, -1.0, 0.1]
```

### 4.3 概念调用流程

```text
步骤 1：Blender camera-view geometry pass 渲染
    功能：渲染 Normal/Depth/IndexOB/Position 通道
    输入：STL + TEST_ATTITUDE + DET_VECTOR + RESOLUTION + ORTHO_SCALE
    输出：yaw045_pitch030_0001.exr (Normal, Depth, IndexOB, Position)
    调用：[拟议路径，待确认] 06_v0.4_code/02_blender/render_camera_geometry.py
         [历史快照参考，需升级] 03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/render_geometry_passes.py

步骤 2：Blender sun-view depth pass 渲染
    功能：渲染 sun-view depth 通道
    输入：STL + TEST_ATTITUDE + SUN_VECTOR + RESOLUTION + ORTHO_SCALE
    输出：yaw045_pitch030_sun_depth.exr
    调用：[拟议路径，待新建] 06_v0.4_code/02_blender/render_sun_depth.py

步骤 3：sun shadow reprojection
    功能：生成 V_sun_macro 可见性 mask
    输入：步骤 1/2 输出 EXR + camera/sun 矩阵 + depth_epsilon_m (初始 0.05m)
    输出：yaw045_pitch030_v_sun_macro.npy + .png
    调用：[拟议路径，待新建] 06_v0.4_code/04_sun_shadow/sun_shadow_reprojection.py

步骤 4：BRDF 后处理与 OCS 积分
    功能：计算 pixel-level BRDF，积分得 OCS，生成图像
    输入：步骤 1 EXR + 步骤 3 V_sun_macro + 五参数冯材料参数 [待确认]
    输出：yaw045_pitch030_linear.exr + _brdf.png + per-frame OCS JSON
    调用：[拟议路径，需改造] 06_v0.4_code/05_postprocess/ocs_integration_v0.4.py
         [拟议路径，需改造] 06_v0.4_code/05_postprocess/image_response_v0.4.py
         [历史快照参考，需修改] 03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/brdf_postprocess.py

步骤 5：manifest 最小条目生成
    功能：生成单条 manifest record 用于校验
    输入：步骤 4 输出 + 路径/矩阵/参数
    输出：单条 manifest record（JSON）
    调用：[拟议路径，待新建] 06_v0.4_code/06_manifest/ocs_manifest_builder.py (单条模式)
```

### 4.4 预期输出文件清单（拟议结构）

```text
[待确认路径] 07_v0.4_results/00_smoke_test/
├── yaw045_pitch030_0001.exr              # camera geometry pass
├── yaw045_pitch030_position.exr          # Position AOV (若 Blender 支持)
├── yaw045_pitch030_sun_depth.exr         # sun-view depth
├── yaw045_pitch030_v_sun_macro.npy       # V_sun_macro mask (binary)
├── yaw045_pitch030_v_sun_macro.png       # V_sun_macro 可视化
├── yaw045_pitch030_linear.exr            # I_linear (float32)
├── yaw045_pitch030_brdf.png              # log1p 归一化图像 (uint8)
├── yaw045_pitch030_ocs.json              # per-frame OCS (total + per_part)
├── smoke_test_manifest_ocs.json          # 单条 OCS manifest
├── smoke_test_manifest_image.json        # 单条 image manifest
└── smoke_test_report.md                  # 通过/失败判据与诊断
```

### 4.5 通过/失败判据（概念标准）

| 检查项 | 通过标准 | 失败处理 |
|---|---|---|
| camera EXR 生成 | 文件存在，Normal/Depth/IndexOB 通道完整 | 检查 Blender 版本、STL 路径、渲染脚本 |
| sun_depth EXR 生成 | 文件存在，Depth 通道完整 | 检查 sun-view 相机设置 |
| V_sun_macro 生成 | npy 文件存在，shape = (256, 256)，dtype = uint8，值为 0 或 1 | 检查 reprojection 算法、depth_epsilon |
| V_sun_macro 物理合理性 | sun-shadowed 像素被正确标记为 0；目视检查 png 可视化 | 调整 depth_epsilon_m 或检查矩阵变换 |
| OCS 数值范围 | ocs_total > 0，ocs_per_part 合理（主体 > 帆板 > 遮阳板） | 检查 BRDF 参数、NoL 有效性、V_sun_macro 应用 |
| 图像数值范围 | I_linear 最大值在合理范围（如 0.1-10.0），PNG 非全黑/全白 | 检查 BRDF 计算、log1p alpha、归一化流程 |
| manifest 字段完整性 | 所有必需字段存在，符合 14 号规范 | 补充缺失字段 |


## 5. 待作者/Codex 确认的问题清单

### 5.1 v0.4 代码区与输出区创建确认

**Q1. v0.4 新代码根目录**：是否创建 `项目重启_v0.4_BlenderOCS/06_v0.4_code/` 作为路线一 C 正式代码区？还是使用其他路径？

**Q2. v0.4 运行产物根目录**：是否创建 `项目重启_v0.4_BlenderOCS/07_v0.4_results/` 作为路线一 C 输出根目录？还是使用其他路径？

**Q3. 历史快照迁移策略**：若确认创建新代码区，历史快照中的可复用模块（materials.py, geometry.py 等）是：
   - A. 复制到新代码区并改造
   - B. 建立符号链接或引用
   - C. 完全重写，只参考思路
   - 需要作者明确选择哪种方式

### 5.2 BRDF 主锚点实现确认

**Q4. 五参数冯模型实现来源**：
   - 历史快照中 `ocs_core.py` 有 legacy_phong 公式 `f_r = rho_d/π + rho_s·(N·H)^n`
   - 书籍知识库提到五参数冯 / Phong-like BRDF
   - 这两者是否同一模型？是否可基于旧公式改造为 pixel-level 实现？还是需要重新对照书中公式编写？

**Q5. materials.py 参数对齐确认**：
   - 历史快照 `materials.py` 中的 `_GGX_DB` 是否已与书中材料参数对齐？
   - 若未对齐，需要提供书中材料参数表的具体来源页码或参数值

**Q6. GGX 对照分支代码组织**：
   - 五参数冯主锚点与 GGX 对照分支，是作为独立函数放在同一文件（如 `03_brdf/brdf_models_v0.4.py`），还是分为两个独立脚本？
   - 如何通过配置切换？

### 5.3 sun visibility 实现确认

**Q7. depth_epsilon_m 初始值**：建议从 0.05m 开始，经 20 姿态 shadow validation 校准后冻结。是否同意该初始值？

**Q8. sun-view 相机设置**：当前历史快照中只有 camera-view 渲染。sun-view 渲染脚本是否有已有参考代码，还是需要从头编写？

**Q9. V_sun_macro reprojection 算法验证顺序**：是否需要先完成 depth round-trip 验证（3 已知点），确认坐标变换正确后，再实现完整的 reprojection？

### 5.4 数据流程确认

**Q10. corpus-level I_scale 两阶段流程**：
   - 历史快照 `brdf_postprocess.py` 可能是 per-frame normalization
   - 需改为两阶段流程：Pass 1 统计全局 I_scale，Pass 2 统一归一化
   - 是否需要先实现独立的 dry-run 统计脚本（如 `compute_corpus_i_scale.py`），还是直接在 BRDF 后处理中增加两阶段逻辑？

**Q11. manifest 生成时机**：
   - 建议在所有姿态 BRDF 后处理完成后统一生成 manifest
   - 还是边生成边写入（streaming 模式）？

**Q12. 历史数据保留策略**：
   - 当前项目根目录下 `ocs_project/` 和 `结果/` 目录中有大量历史产物
   - 这些是否保留为参考？还是可以清理或移动到归档区？

### 5.5 Phase 0 gate 确认

**Q13. 20 姿态 shadow validation 的姿态选择**：
   - 建议覆盖高/低/边缘/典型姿态
   - 具体姿态列表（20 个 yaw/pitch 组合）是否需要先规划？还是由 Claude 在 1C-C03 任务中提出候选清单？

**Q14. depth round-trip 的 3 已知点选择**：
   - 建议选择模型中心点 + 两个边界点
   - 这些点是否需要先手动标注（如从 STL 中读取特定顶点坐标）？还是用程序自动选择？

**Q15. smoke test 通过后的后续步骤**：
   - smoke test 通过后，是否立即进入全量生成？
   - 还是需要先完成其他 P1 验证任务（如 3 姿态 camera geometry pass 检查）？

### 5.6 路线一 C 与三轴小项目接口确认

**Q16. roll sensitivity 实现时机**：
   - 路线一 C 主实验为 fixed-roll，roll sensitivity 作为探针实验
   - 是否在主实验完成后再规划？还是在代码框架设计时就预留三轴姿态网格的扩展接口？

**Q17. 三轴小项目的代码复用**：
   - 三轴小项目是否会复用路线一 C 的代码框架？
   - 是否需要在当前代码设计中考虑三轴扩展性（如姿态网格生成、roll 参数支持）？


## 6. 拟议后续操作清单（需作者确认后才能执行）

### 6.1 若确认创建 v0.4 新代码区，拟议操作如下

**操作 A1：创建代码区目录结构**

```text
拟创建路径：项目重启_v0.4_BlenderOCS/06_v0.4_code/
拟创建子目录：
├── 00_config/
├── 01_geometry/
├── 02_blender/
├── 03_brdf/
├── 04_sun_shadow/
├── 05_postprocess/
├── 06_manifest/
├── 07_dataset/
├── 08_inversion/
├── 09_experiments/
└── 10_validation/

待确认：目录结构是否需要调整？
```

**操作 A2：迁移可直接复用模块**

```text
拟复制：03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/materials.py
    → 06_v0.4_code/00_config/materials_v0.4.py

拟复制：03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/geometry.py
    → 06_v0.4_code/01_geometry/geometry_loader.py

待确认：是否直接复制？还是复制后需要立即检查/修改？
```

**操作 A3：改造需修改模块**

```text
拟复制并修改：03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/config.py
    → 06_v0.4_code/00_config/config_v0.4.py
    必修项：NUM_YAW = 72（不含 360°）
           BRDF_MODEL 支持双模式
           其他参数与 13/14 规范对齐

拟复制并大幅改造：03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/brdf_postprocess.py
    → 06_v0.4_code/05_postprocess/ocs_integration_v0.4.py
       06_v0.4_code/05_postprocess/image_response_v0.4.py
    必修项：加入 V_sun_macro 到 OCS 和图像计算
           实现 corpus-level I_scale 两阶段流程

待确认：这些改造是否在本次操作中完成，还是先复制占位，后续再逐步改造？
```

**操作 A4：创建新模块（从头编写）**

```text
拟新建：06_v0.4_code/02_blender/render_sun_depth.py
拟新建：06_v0.4_code/04_sun_shadow/sun_shadow_reprojection.py
拟新建：06_v0.4_code/04_sun_shadow/depth_round_trip_check.py
拟新建：06_v0.4_code/10_validation/validate_20_attitudes.py
拟新建：06_v0.4_code/03_brdf/phong_five_param.py
拟新建：06_v0.4_code/06_manifest/ocs_manifest_builder.py
拟新建：06_v0.4_code/06_manifest/image_manifest_builder.py
拟新建：06_v0.4_code/06_manifest/consistency_checker.py

待确认：这些模块是否在 1C-C02/C03 任务中设计后再创建？还是先创建空文件占位？
```

**操作 A5：创建输出根目录**

```text
拟创建路径：项目重启_v0.4_BlenderOCS/07_v0.4_results/
拟创建子目录：
├── 00_smoke_test/           # 单姿态 smoke test 输出
├── 00_geometry_passes/      # camera geometry pass
├── 00b_sun_depth_passes/    # sun-view depth pass
├── 01_sun_shadow_reprojection/  # V_sun_macro mask
├── 02_brdf_postprocess/     # BRDF 后处理与 OCS
├── 03_manifests/            # OCS/image manifest
├── 04_splits/               # dataset split
└── 05_runs/                 # 训练运行产物

待确认：输出目录结构是否需要调整？
```

**操作 A6：创建环境记录文件**

```text
拟新建：06_v0.4_code/00_config/environment.md
    记录：Blender 版本、Python 版本、conda 环境、CUDA、PyTorch、硬件配置

待确认：是否立即记录？还是在实际运行环境确定后再记录？
```

### 6.2 操作执行前必须确认

**所有上述操作（A1-A6）在执行前，必须由作者明确确认：**
1. 是否同意创建 `06_v0.4_code/` 和 `07_v0.4_results/`
2. 目录结构是否需要调整
3. 文件迁移/复制的范围和时机
4. 新模块创建的时机（立即创建还是后续任务中创建）

**未经确认，本轮不执行任何文件创建、复制、修改操作。**


## 7. 是否可以进入 1C-C02 的判定

### 7.1 可以进入 1C-C02 的条件

**1C-C02 任务是"设计单姿态 smoke test 与资源估计"**，属于设计阶段，不涉及代码执行或文件创建。

**判定：可以进入 1C-C02，前提是：**

1. **只要求"设计 smoke test"**：
   - 设计最小输入配置
   - 设计调用流程（概念性）
   - 估计资源需求（单姿态耗时、存储、显存等）
   - 列出通过/失败判据
   - **不要求实际运行或创建代码**

2. **Codex 需要先审阅本 R1 修正版**：
   - 确认对代码入口的判断修正是否准确
   - 确认三分表（可复用/禁用/待新建）是否合理
   - 确认待确认问题清单（Q1-Q17）是否覆盖关键点

### 7.2 不能进入 1C-C02 的条件

**若 1C-C02 要求"执行 smoke test 或创建代码区"，则必须先完成：**

1. 作者/Codex 确认 §5 待确认问题清单（Q1-Q17）
2. 作者/Codex 确认 §6 拟议操作清单（A1-A6）
3. 若同意创建新代码区，先执行 A1-A6 操作
4. 环境准备（Blender、Python、依赖库安装）
5. 才能进入实际的 smoke test 执行

### 7.3 1C-C03 任务的前置条件

**1C-C03 任务是"设计前向模型几何/可见性校验"**，同样属于设计阶段。

**判定：可以在 1C-C02 之后进入 1C-C03，前提是：**

1. 只要求"设计校验任务"（depth round-trip、20 姿态 shadow validation 等）
2. 不要求实际执行校验
3. Codex 审阅通过 1C-C02 输出

### 7.4 进入代码执行阶段（Phase 0 gate）的前置条件

**只有满足以下所有条件，才能进入实际的代码执行和 Phase 0 gate 验证：**

1. ✅ 1C-C01-R1 Codex 审阅通过
2. ✅ 1C-C02 smoke test 设计 Codex 审阅通过
3. ✅ 1C-C03 几何/可见性校验设计 Codex 审阅通过
4. ⬜ 作者/Codex 确认创建 v0.4 代码区和输出区（§6 操作 A1-A6）
5. ⬜ 环境准备完成（Blender、Python、依赖库）
6. ⬜ 可复用模块迁移完成（materials.py、geometry.py 等）
7. ⬜ 关键新模块实现完成（sun-view depth 渲染、reprojection 等）
8. ⬜ 单姿态 smoke test 实际执行并通过
9. ⬜ depth round-trip 验证通过
10. ⬜ 20 姿态 shadow validation 通过，depth_epsilon_m 校准完成

**只有完成上述所有条件，才能通过 Phase 0 gate，进入全量 2664 姿态数据生成。**

## 8. 修正总结

### 8.1 本次修正的关键变更

1. **修正过强判断**：从"当前主入口清楚"改为"当前没有确认的正式 v0.4 可运行代码主入口"
2. **区分路径类型**：明确历史快照、规划文档、冻结规范、待确认路径的区别
3. **三分表重构**：将代码资产分为可复用、禁用、待新建三类，每类标注当前状态
4. **概念调用链**：smoke test 调用链改为概念性说明，所有路径标注为拟议或待确认
5. **删除立即操作**：将"立即可做"改为"拟议后续操作，需作者确认"
6. **明确进入条件**：清晰说明何时可以进入 1C-C02，何时可以进入代码执行

### 8.2 当前代码库真实状态

- **有**：历史关键代码快照（部分可复用、部分禁用）
- **有**：路线一成果区规划文档（指导性，非可执行代码）
- **有**：13/14 方法与字段冻结规范（方法依据）
- **无**：确认的 v0.4 正式代码区
- **无**：确认的 v0.4 运行产物输出区
- **无**：可直接运行的路线一 C 入口脚本

### 8.3 下一步建议

**立即可做（设计阶段，无需确认）：**
- 进入 1C-C02：设计单姿态 smoke test 与资源估计
- 进入 1C-C03：设计前向模型几何/可见性校验

**需作者确认后才能做（实施阶段）：**
- 创建 v0.4 代码区和输出区（§6 操作 A1-A6）
- 迁移/改造历史快照中的可复用模块
- 新建缺失模块
- 实际执行 smoke test 和 Phase 0 gate 验证

**不应做（违反红线）：**
- 未经确认直接创建目录或文件
- 未经确认直接修改任何现有代码或配置
- 未经确认直接进入全量数据生成或训练

## 9. 红线遵守确认

本 R1 修正版严格遵守以下红线：

✅ 只修正文档判断，不创建目录
✅ 不复制文件，不修改代码
✅ 不修改 CLAUDE.md，不修改冻结文件
✅ 不进入全量生成，不训练模型
✅ 所有拟议操作均标注为"待作者确认"
✅ 明确区分历史快照、规划文档、待确认路径
✅ 不声称任何未确认的路径或资产"已存在"或"可直接运行"

---

**本文件完成。等待 Codex 审阅后，可进入 1C-C02 设计阶段。**

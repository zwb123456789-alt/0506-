# 路线一 C 代码入口盘点清单（Claude 输出）

生成时间：2026-06-22
任务编号：1C-C01
执行者：Claude

## 0. 上下文恢复确认

已完成轻量上下文恢复，确认以下要点：

1. **当前科学主线**：model-known 条件下，独立 OCS 光度通道与图像成像通道共享同一物理前向模型时，跨几何 OCS 多观测光度向量与图像通道对姿态信息的可观测性、互补性和置信一致性研究。

2. **路线一 C 定位**：保留 v0.4 pixel-level OCS-image 同源前向架构；以五参数冯 / Phong-like BRDF 与书中典型材料参数作为主 BRDF 锚点；以 GGX / Cook-Torrance 作为 BRDF mismatch、现代 PBR 对照和鲁棒性分支；主实验仍为 fixed-roll yaw-pitch controlled benchmark。

3. **当前阶段**：路线一 C 代码入口盘点阶段，Phase 0 门控验证前的准备工作。

## 1. 一句话结论

**当前主入口清楚，但需要区分旧 v0.3 禁用入口与 v0.4 主链。当前代码库中存在旧模块 A face-center OCS 链路（`ocs_project/01_code/ocs_core.py`），已被标记为历史禁用；v0.4 主链应基于 Blender pixel-level 渲染输出进行 BRDF 后处理和 OCS 积分，当前代码资产可部分复用但需要按路线一 C 要求进行升级改造。**

## 2. 代码/脚本入口表

### 2.1 v0.4 主链可复用入口

| 路径 | 功能 | 输入 | 输出 | 当前可信度 | 风险备注 |
|---|---|---|---|---|---|
| `ocs_project/01_code/config.py` | 全局配置：路径、姿态网格、几何参数 | — | 配置常量 | ★★★★☆ | **需修改**：yaw 网格必须改为 72（不含 360°），当前为 73；BRDF_MODEL 当前默认 ggx，需改为支持五参数冯主锚点 + GGX 对照 |
| `ocs_project/01_code/materials.py` | 材料 BRDF 参数数据库 | — | MATERIAL_DB 字典 | ★★★★★ | 可直接复用，参数与书中材料参数对齐 |
| `ocs_project/01_code/geometry.py` | STL 加载、姿态旋转、坐标系 | STL 路径、姿态角 | mesh 数据、旋转矩阵 | ★★★★★ | 可直接复用 |
| `ocs_project/01_code/run_multi_geom.py` | 多观测几何批量扫描 | OBS_GEOMETRIES 配置 | 多几何 OCS 结果 | ★★★☆☆ | **需大幅修改**：当前为旧模块 A face-center 采样链路；需改为调用 Blender 渲染 + Python 后处理流程 |
| `ocs_project/02_blender/render_batch.py` | Blender headless 批量渲染 | ocs_scan.json（旧） | 渲染图像 | ★★★☆☆ | **需升级**：需新增 camera geometry pass、sun-view depth pass、Position/WorldCoord pass |
| `ocs_project/02_blender/brdf_postprocess.py` | BRDF 后处理与 OCS 积分 | EXR geometry pass | OCS + 图像 | ★★★★☆ | **需修改**：必须加入 V_sun_macro 到 OCS 和图像计算；需支持 corpus-level I_scale 两阶段流程 |
| `ocs_project/02_blender/render_geometry_passes.py` | 几何通道渲染 | 姿态、几何配置 | Normal/Depth/IndexOB EXR | ★★★☆☆ | **需升级**：需新增 Position AOV、sun-view depth 渲染、矩阵记录 |
| `ocs_project/03_inversion/inv_common.py` | 反演公共工具：manifest 加载、split 生成 | manifest JSON | 特征矩阵、split | ★★★☆☆ | **需升级**：manifest schema 必须升级到 14 号规范；需新增一致性检查 |
| `ocs_project/03_inversion/train_mlp.py` | OCS-only MLP 训练 | OCS manifest + split | 训练结果 | ★★★☆☆ | **需升级**：需生成 source_data.json、六子版本记录 |
| `ocs_project/03_inversion/train_cnn.py` | image-only CNN 训练 | image manifest + split | 训练结果 | ★★★☆☆ | **需升级**：同上 |
| `ocs_project/03_inversion/train_fusion.py` | fusion 训练 | OCS + image manifest | 训练结果 | ★★★☆☆ | **需升级**：同上 |

### 2.2 v0.3 历史/禁用入口（不并入路线一 C 主链）

| 路径 | 功能 | 禁用原因 | 处理方式 |
|---|---|---|---|
| `ocs_project/01_code/ocs_core.py` | 模块 A face-center OCS 采样 | 旧版 face-center 采样已废弃，v0.4 改为 pixel-level | **历史归档**，不作为路线一 C 入口 |
| `ocs_project/01_code/main_run.py` | 模块 A 主入口（face-center 链路） | 调用旧 ocs_core.py | **历史归档** |
| `ocs_project/01_code/adaptive_integration.py` | face-level adaptive 采样 | 已废弃 | **历史归档** |
| `ocs_project/02_blender/diag_subface_adaptive.py` | face-center vs pixel-level 对比诊断 | 历史诊断任务已完成 | **历史归档** |
| `ocs_project/02_blender/analyze_consistency.py` | 旧 A/B 一致性检查 | v0.4 改为 manifest schema 一致性 | **历史归档** |

### 2.3 当前缺失但路线一 C 必须新增的入口

| 功能模块 | 必要性 | 建议路径 | 输入 | 输出 |
|---|---|---|---|---|
| sun-view depth 渲染 | **P0 必做** | `06_v0.4_code/02_blender/render_sun_depth.py` | 姿态、sun 方向 | sun_depth EXR + sun_camera_matrix |
| sun shadow reprojection | **P0 必做** | `06_v0.4_code/04_sun_shadow/sun_shadow_reprojection.py` | camera depth + sun depth + 矩阵 | V_sun_macro_mask (npy + png) |
| depth round-trip 校验 | **P0 gate** | `06_v0.4_code/10_validation/depth_round_trip_check.py` | 3 已知点 | round-trip 误差报告 |
| 20 姿态 shadow validation | **P0 gate** | `06_v0.4_code/10_validation/validate_20_attitudes.py` | 20 代表姿态 | shadow 物理合理性 + depth_epsilon 校准 |
| 五参数冯 BRDF 主锚点模块 | **P0 必做** | `06_v0.4_code/03_brdf/phong_five_param.py` | 书中材料参数 | BRDF 计算函数 |
| OCS manifest builder (v0.4) | **P1 必做** | `06_v0.4_code/06_manifest/ocs_manifest_builder.py` | per-frame OCS JSON | 符合 14 号规范的 manifest |
| image manifest builder (v0.4) | **P1 必做** | `06_v0.4_code/06_manifest/image_manifest_builder.py` | EXR + PNG 路径 | 符合 14 号规范的 manifest |
| manifest 一致性检查器 | **P1 必做** | `06_v0.4_code/06_manifest/consistency_checker.py` | OCS + image manifest | 一致性检查报告 |

## 3. 配置/数据入口表

### 3.1 当前配置文件

| 路径 | 功能 | 关键字段 | 风险备注 |
|---|---|---|---|
| `ocs_project/01_code/config.py` | 全局配置 | `YAW_RANGE`, `NUM_YAW`, `NUM_PITCH`, `BRDF_MODEL`, `OBS_GEOMETRIES` | **需修改**：NUM_YAW 当前 73，需改为 72；BRDF_MODEL 需支持五参数冯 + GGX 双模式 |
| `ocs_project/01_code/materials.py` | 材料参数 | `MATERIAL_DB` = {part_name: {rho_d, rho_s, n}} | 可复用，参数已对齐 |

### 3.2 当前数据产物位置

| 路径 | 功能 | 风险备注 |
|---|---|---|
| `结果/模块A_重构/` | 旧模块 A face-center OCS 输出 | **历史产物**，不作为路线一 C 输入 |
| `结果/模块B_渲染/` | 旧 Blender 渲染输出 | **历史产物**，缺少 sun-view depth pass 和 V_sun_macro |
| `ocs_project/03_results/` | 旧反演结果 | **历史产物** |

### 3.3 路线一 C 必须新增的数据结构

| 数据类型 | 建议路径 | 关键字段 |
|---|---|---|
| v0.4 运行产物根目录 | `项目重启_v0.4_BlenderOCS/07_v0.4_results/` | — |
| camera geometry pass | `07_v0.4_results/00_geometry_passes/{geom_id}/yaw{yyy}_pitch{ppp}_0001.exr` | Normal, Depth, IndexOB, Position |
| sun-view depth pass | `07_v0.4_results/00b_sun_depth_passes/{geom_id}/yaw{yyy}_pitch{ppp}_sun_depth.exr` | sun_depth |
| V_sun_macro mask | `07_v0.4_results/01_sun_shadow_reprojection/{geom_id}/yaw{yyy}_pitch{ppp}_v_sun_macro.npy` | uint8 0/1 mask |
| BRDF 后处理输出 | `07_v0.4_results/02_brdf_postprocess/{geom_id}/` | linear EXR + log1p PNG + per-frame OCS JSON |
| OCS manifest | `07_v0.4_results/03_manifests/ocs_manifest_v0.4_{single/multi}_geom_{geom_id}.json` | 符合 14 号规范 |
| image manifest | `07_v0.4_results/03_manifests/image_manifest_v0.4_{single/multi}_geom_{geom_id}.json` | 符合 14 号规范 |

## 4. v0.4 主链与旧 v0.3 禁用/风险入口区分表

| 类别 | v0.3 旧链路 | v0.4 主链 | 区分标志 |
|---|---|---|---|
| **OCS 采样方式** | face-center 采样（`ocs_core.py`） | pixel-level 从 Blender EXR 积分 | v0.3 调用 `scan_attitude()`；v0.4 读取 EXR + V_sun_macro |
| **姿态网格** | yaw 73（含 360°） | yaw 72（不含 360°） | `NUM_YAW = 73` vs `NUM_YAW = 72` |
| **BRDF 主锚点** | GGX 唯一 | 五参数冯主锚点 + GGX 对照 | `BRDF_MODEL = "ggx"` vs 双模式支持 |
| **sun visibility** | 无或简化 | Level 2: camera_visible_nol_plus_sun_shadow_pass | 有无 `sun_depth.exr` 和 `v_sun_macro.npy` |
| **manifest schema** | 旧版无 source_data.json | 14 号规范 + source_data.json | 有无 `sun_visibility`, `shadow_mapping_method`, `depth_epsilon_m` 字段 |
| **图像归一化** | per-frame I_scale | corpus-level I_scale 两阶段流程 | 有无 corpus-level `I_scale` 统一值 |
| **模块入口** | `main_run.py` → `ocs_core.py` | Blender 渲染 → Python 后处理 | 是否调用 `ocs_core.scan_attitude()` |

## 5. 单姿态 smoke test 最小调用链草案

### 5.1 目标

验证 v0.4 pixel-level OCS-image 同源前向链路能否端到端跑通，不进入全量 yaw-pitch 网格。

### 5.2 最小输入配置

```python
# 单姿态 smoke test 配置
TARGET_MODEL = "真实模型"  # jinshuzhuti + taiyangnengban + yinshenban
TEST_ATTITUDE = {"yaw": 45.0, "pitch": 30.0, "roll": 0.0}  # fixed-roll
TEST_GEOMETRY = "phase63_backscatter"  # G1 baseline
BRDF_MODE = "phong_five_param"  # 主锚点
RESOLUTION = 256
ORTHO_SCALE = 2.2  # × r_max
SUN_VECTOR = [1.0, 0.0, 0.3]
DET_VECTOR = [0.5, -1.0, 0.1]
```

### 5.3 最小运行流程

```text
步骤 1：Blender camera-view geometry pass 渲染
    输入：STL + TEST_ATTITUDE + DET_VECTOR + RESOLUTION + ORTHO_SCALE
    输出：yaw045_pitch030_0001.exr (Normal, Depth, IndexOB, Position)
    调用：06_v0.4_code/02_blender/render_camera_geometry.py

步骤 2：Blender sun-view depth pass 渲染
    输入：STL + TEST_ATTITUDE + SUN_VECTOR + RESOLUTION + ORTHO_SCALE
    输出：yaw045_pitch030_sun_depth.exr
    调用：06_v0.4_code/02_blender/render_sun_depth.py

步骤 3：sun shadow reprojection
    输入：步骤 1/2 输出 EXR + camera/sun 矩阵 + depth_epsilon_m (初始 0.05m)
    输出：yaw045_pitch030_v_sun_macro.npy + .png
    调用：06_v0.4_code/04_sun_shadow/sun_shadow_reprojection.py

步骤 4：BRDF 后处理与 OCS 积分
    输入：步骤 1 EXR + 步骤 3 V_sun_macro + 五参数冯材料参数
    输出：yaw045_pitch030_linear.exr + _brdf.png + per-frame OCS JSON
    调用：06_v0.4_code/05_postprocess/ocs_integration_v0.4.py
           06_v0.4_code/05_postprocess/image_response_v0.4.py

步骤 5：manifest 最小条目生成
    输入：步骤 4 输出 + 路径/矩阵/参数
    输出：单条 manifest record（JSON）
    调用：06_v0.4_code/06_manifest/ocs_manifest_builder.py (单条模式)
```

### 5.4 预期输出文件清单

```text
07_v0.4_results/00_smoke_test/
├── yaw045_pitch030_0001.exr              # camera geometry pass
├── yaw045_pitch030_position.exr          # Position AOV (若支持)
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

### 5.5 通过/失败判据

| 检查项 | 通过标准 | 失败处理 |
|---|---|---|
| camera EXR 生成 | 文件存在，Normal/Depth/IndexOB 通道完整 | 检查 Blender 版本、STL 路径、渲染脚本 |
| sun_depth EXR 生成 | 文件存在，Depth 通道完整 | 检查 sun-view 相机设置 |
| V_sun_macro 生成 | npy 文件存在，shape = (256, 256)，dtype = uint8，值为 0 或 1 | 检查 reprojection 算法、depth_epsilon |
| V_sun_macro 物理合理性 | sun-shadowed 像素被正确标记为 0；目视检查 png 可视化 | 调整 depth_epsilon_m 或检查矩阵变换 |
| OCS 数值范围 | ocs_total > 0，ocs_per_part 合理（主体 > 帆板 > 遮阳板） | 检查 BRDF 参数、NoL 有效性、V_sun_macro 应用 |
| 图像数值范围 | I_linear 最大值在合理范围（如 0.1-10.0），PNG 非全黑/全白 | 检查 BRDF 计算、log1p alpha、归一化流程 |
| manifest 字段完整性 | 所有必需字段存在，符合 14 号规范 | 补充缺失字段 |

## 6. 待作者/Codex 确认的问题清单

### 6.1 代码结构确认

1. **v0.4 代码根目录位置**：建议为 `项目重启_v0.4_BlenderOCS/06_v0.4_code/`，是否确认？
2. **旧代码复用策略**：`materials.py`、`geometry.py` 可直接复制到 v0.4 代码区，其他模块需改造，是否同意？
3. **模块划分**：建议按 §2.2 的 10 个子目录划分（00_config ~ 10_validation），是否需要调整？

### 6.2 BRDF 主锚点实现确认

4. **五参数冯模型实现**：当前 `materials.py` 中有 `_GGX_DB`，但旧 `ocs_core.py` 使用 legacy_phong 公式 `f_r = rho_d/π + rho_s·(N·H)^n`。路线一 C 需要 pixel-level 实现该公式，是否可基于旧公式改造，还是需要重新对照书中公式编写？
5. **GGX 对照分支**：当前 `brdf_postprocess.py` 中有 GGX 实现，是否可直接复用为 mismatch 对照分支？
6. **BRDF 主线与对照的代码组织**：建议两者作为独立函数放在 `06_v0.4_code/03_brdf/` 中，由配置选择，还是作为两套独立脚本？

### 6.3 sun visibility 实现确认

7. **depth_epsilon_m 初始值**：建议从 0.05m 开始，经 20 姿态 shadow validation 校准后冻结，是否同意？
8. **sun-view 相机设置**：当前 `render_geometry_passes.py` 只有 camera-view 渲染，需新增 sun-view 渲染脚本，是否需要参考已有代码还是从头编写？
9. **V_sun_macro reprojection 算法**：13 号规范 §7.3.2 描述的算法已明确，是否需要先做 depth round-trip 验证再实现完整 reprojection？

### 6.4 数据流程确认

10. **corpus-level I_scale 两阶段流程**：当前 `brdf_postprocess.py` 可能是 per-frame normalization，需改为两阶段流程（先统计全局 I_scale，再统一归一化）。是否需要先实现 dry-run 统计脚本？
11. **manifest 生成时机**：建议在所有姿态 BRDF 后处理完成后统一生成 manifest，还是边生成边写入？
12. **历史数据保留**：旧 `结果/` 目录中的历史产物是否保留为参考，还是可以清理？

### 6.5 Phase 0 gate 确认

13. **20 姿态 shadow validation 的姿态选择**：建议覆盖高/低/边缘/典型姿态，具体姿态列表是否需要先规划？
14. **depth round-trip 的 3 已知点选择**：建议选择模型中心点 + 两个边界点，是否需要先手动标注？
15. **smoke test 通过后是否立即进入全量生成**：还是需要先完成其他 P1 验证任务（如 3 姿态 camera geometry pass 检查）？

### 6.6 路线一 C 与三轴小项目接口确认

16. **roll sensitivity 实现时机**：当前路线一 C 主实验为 fixed-roll，roll sensitivity 作为探针实验，是否在主实验完成后再规划？
17. **三轴小项目的 roll-aware 搜索**：是否需要在路线一 C 代码框架中预留三轴姿态网格的扩展接口？

## 7. 下一步建议

根据当前代码入口盘点结果，建议下一步执行顺序：

### 7.1 立即可做（不需要等待确认）

1. 复制 `materials.py` 和 `geometry.py` 到 `06_v0.4_code/00_config/` 和 `06_v0.4_code/01_geometry/`。
2. 创建 `06_v0.4_code/` 目录结构骨架（00-10 子目录）。
3. 编写 `environment.md` 记录当前 Blender / Python / PyTorch 版本。

### 7.2 需要作者确认后执行

1. 确认问题清单 §6.1-6.6 中的 17 个问题。
2. 根据确认结果，进入 1C-C02 任务：设计单姿态 smoke test 与资源估计。
3. 根据 smoke test 结果，进入 1C-C03 任务：设计前向模型几何/可见性校验。

### 7.3 暂不执行（需 Phase 0 gate 通过后）

1. 全量 2664 姿态数据生成。
2. manifest 一致性检查。
3. 反演训练与实验。

## 8. 总结

**当前代码库状态**：
- 旧模块 A face-center OCS 链路（v0.3）已明确为历史禁用入口，不并入路线一 C。
- v0.4 pixel-level 主链的部分模块可复用（materials, geometry），但多数模块需要升级改造（render, brdf_postprocess, inv_common）。
- 当前缺失路线一 C 必须的关键模块：sun-view depth 渲染、sun shadow reprojection、20 姿态 shadow validation、五参数冯主锚点实现、manifest v0.4 builder。

**风险点**：
- yaw 网格从 73 改为 72 可能影响旧结果对比（已明确为红线，必须改）。
- BRDF 主锚点从 GGX 唯一改为五参数冯主 + GGX 对照，需确认实现方式。
- corpus-level I_scale 两阶段流程需改造当前 per-frame normalization 逻辑。
- sun visibility Level 2 实现是全新模块，需从头编写并通过 Phase 0 gate。

**可行性判断**：
- 单姿态 smoke test 可行，最小调用链已明确。
- 需要先完成 §6 问题清单确认，再进入 smoke test 实现。
- Phase 0 gate（20 姿态 shadow validation + depth round-trip）是全量生成前的硬门控，必须通过。

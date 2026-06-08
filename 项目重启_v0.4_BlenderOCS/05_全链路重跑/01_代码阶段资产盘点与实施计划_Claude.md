# 01 代码阶段资产盘点与实施计划

生成时间：2026-06-08
依据：方法冻结通过（`04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md` + `14_v0.4数据与manifest字段规范_最终冻结版.md`）

---

## 一、旧代码资产分类判断

### 1.1 可直接参考的模块（结构/逻辑可复用）

| 旧文件 | 位置 | 可复用内容 | 不可复用内容 |
|---|---|---|---|
| `materials.py` | `98_外部材料备份/03_关键代码快照/01_code/` | `_GGX_DB` 材料参数字典、GGX 公式结构 | 无（参数已与 `13` §9.3 一致）|
| `geometry.py` | 同上 | STL 加载、姿态旋转矩阵、世界坐标系约定 | 无 |
| `config.py` | 同上 | ortho_scale、resolution、yaw/pitch 网格定义结构 | yaw 网格必须改为 72（不含 360°）|
| `brdf_postprocess.py` | `98_外部材料备份/03_关键代码快照/02_blender/` | EXR 读取、Normal/Depth/IndexOB 解析结构 | BRDF 计算必须加 `V_sun_macro`；图像响应链必须同步 |
| `inv_common.py` | `98_外部材料备份/03_关键代码快照/03_inversion/` | per_part_log 特征构建、dataset split 加载结构 | manifest schema 必须升级到 `14` 定义 |

### 1.2 必须重写或大幅修改的模块

| 旧文件 | 原因 | 重写要点 |
|---|---|---|
| `ocs_core.py` | 旧版为 face-center 采样，已禁用 | 改为从 Blender EXR pixel-level 读取 `V_sun_macro` 后计算 OCS |
| `run_multi_geom.py` | 旧版 yaw73 网格、无 sun shadow pass | 改为 72 yaw、每个 geom 生成 camera/sun geometry pass + reprojection |
| `render_geometry_passes.py` | 旧版无 Position AOV、无 sun-view 渲染 | 新增 Position/WorldCoord pass；新增 sun-view depth 渲染；记录 camera/sun 矩阵 |
| `train_mlp.py` / `train_cnn.py` / `train_fusion.py` | 旧版 manifest schema、无 source_data.json、无一致性检查 | 新增 `14` §8.1 一致性检查；生成 source_data.json；记录六子版本 |
| 补充实验代码（12b/12c/12f/12g）| 基于旧 OCS/image | 全部基于新 manifest 重写 |

### 1.3 不可复用的旧代码

| 类别 | 原因 |
|---|---|
| `adaptive_integration.py` | face-level adaptive 已废弃 |
| `diag_subface_adaptive.py` | 诊断 face-center 与 pixel-level 差异，已完成历史任务 |
| `analyze_consistency.py` | 旧 A/B 一致性检查，v0.4 改为 manifest schema 一致性 |

---

## 二、v0.4 代码模块结构（建议）

### 2.1 根目录

```
项目重启_v0.4_BlenderOCS/06_v0.4_code/
```

所有新代码放在此目录，不写外部旧目录。

### 2.2 模块划分

```text
06_v0.4_code/
├── 00_config/
│   ├── config_v0.4.py              # 冻结参数：yaw72/pitch37/ortho_scale/resolution/eps
│   ├── materials_v0.4.py           # _GGX_DB 材料参数（复用旧 materials.py 结构）
│   ├── geom_multi_config.py        # 5 组 sun/det 几何配置
│   ├── environment.md              # Blender/Python/conda/CUDA/PyTorch/硬件版本记录
│   └── environment.yml             # 可选：conda 环境导出或最小依赖文件
├── 01_geometry/
│   ├── geometry_loader.py          # STL 加载、姿态旋转、世界坐标（复用旧 geometry.py）
│   └── attitude_grid.py            # 72×37 姿态网格生成、record_id 构建
├── 02_blender/
│   ├── render_camera_geometry.py  # camera-view Normal/Depth/IndexOB/Position 渲染
│   ├── render_sun_depth.py        # sun-view depth 渲染
│   └── blender_utils.py            # 矩阵导出、scene 管理
├── 03_brdf/
│   ├── brdf_models_v0.4.py         # GGX/Cook-Torrance 公式（复用旧结构，加 eps 边界）
│   └── brdf_eval.py                # 逐像素 f_r 计算
├── 04_sun_shadow/
│   ├── depth_round_trip_check.py  # §7.4.2 三已知点 round-trip 校验
│   ├── sun_shadow_reprojection.py # camera pixel → world → sun-view depth comparison
│   └── v_sun_macro_generator.py   # 生成 V_sun_macro_mask，写入 .npy + 可视化 PNG
├── 05_postprocess/
│   ├── ocs_integration_v0.4.py    # OCS 积分：Σ A_pix·f_r·NoL·V_sun_macro
│   ├── image_response_v0.4.py     # I_linear = f_r·NoL·V_sun_macro；log1p；PNG
│   └── per_frame_stats.py         # n_pixels_camera_visible / nol_positive / sun_visible / contributing
├── 06_manifest/
│   ├── ocs_manifest_builder.py    # 生成 `14` §3.1 schema OCS manifest
│   ├── image_manifest_builder.py  # 生成 `14` §3.2 schema image manifest
│   └── consistency_checker.py     # `14` §8.1 一致性检查
├── 07_dataset/
│   ├── split_generator.py         # coarse_to_fine / random split 生成
│   └── split_loader.py            # split 文件加载与验证
├── 08_inversion/
│   ├── train_ocs_mlp_v0.4.py      # OCS-only MLP，生成 source_data.json
│   ├── train_image_resnet_v0.4.py # image-only ResNet-18
│   ├── train_fusion_v0.4.py       # late fusion concat1/concat5
│   └── inv_common_v0.4.py         # 共享：特征构建、manifest 加载、一致性检查、source_data 生成
├── 09_experiments/
│   ├── run_noise_robustness_v0.4.py
│   ├── run_fusion_upgrade_v0.4.py  # U1/U2 退化感知训练
│   ├── run_12b_fallback_isolation_v0.4.py
│   ├── run_12c_obs_degradation_v0.4.py
│   ├── run_12d_cross_phase_v0.4.py
│   ├── run_12f_beta_sweep_v0.4.py
│   └── build_12g_gallery_v0.4.py
└── 10_validation/
    ├── validate_20_attitudes.py   # §12.6 二十姿态 shadow validation + depth_epsilon 校准
    ├── validate_v_sun_macro_on_image.py  # §12.7 五姿态 V_sun_macro 对图像影响检查
    └── sanity_checks.py           # §12.1-12.5 其他 sanity checks
```

### 2.3 每个模块的输入/输出/manifest 字段

#### 2.3.1 `02_blender/render_camera_geometry.py`

| 项 | 内容 |
|---|---|
| 输入 | STL 路径、(yaw, pitch)、camera_matrix_world、ortho_scale、resolution |
| 输出 | `00_geometry_passes/{geom_id}/yaw{yyy}_pitch{ppp}_0001.exr`（Normal/Depth/IndexOB）；若支持则输出 `_position.exr` |
| manifest 字段 | `camera_exr_path`, `position_exr_path`, `camera_matrix_world` |

#### 2.3.2 `02_blender/render_sun_depth.py`

| 项 | 内容 |
|---|---|
| 输入 | STL 路径、(yaw, pitch)、sun_camera_matrix_world（look_at(sun_dir)）、同 ortho_scale/resolution |
| 输出 | `00b_sun_depth_passes/{geom_id}/yaw{yyy}_pitch{ppp}_sun_depth.exr` |
| manifest 字段 | `sun_depth_exr_path`, `sun_camera_matrix_world` |

#### 2.3.3 `04_sun_shadow/sun_shadow_reprojection.py`

| 项 | 内容 |
|---|---|
| 输入 | camera_exr（depth/IndexOB）、position_exr 或 depth+camera_matrix、sun_depth_exr、camera/sun 矩阵、depth_epsilon_m |
| 输出 | `01_sun_shadow_reprojection/{geom_id}/yaw{yyy}_pitch{ppp}_v_sun_macro.npy`（uint8 0/1）+ `_v_sun_macro.png`（可视化）|
| manifest 字段 | `sun_visibility_mask_path` |
| 关键算法 | 见 `13` §7.3.2：world_to_sun_camera = inverse(sun_camera_matrix_world)；最近邻采样 sun_depth |

#### 2.3.4 `05_postprocess/ocs_integration_v0.4.py`

| 项 | 内容 |
|---|---|
| 输入 | camera_exr（Normal/Depth/IndexOB）、V_sun_macro_mask、sun_dir、det_dir、材料参数、A_pix |
| 输出 | per-frame OCS JSON（ocs_total, ocs_per_part）；写入 `02_brdf_postprocess/{geom_id}/ocs_scan_v0.4.json` |
| manifest 字段 | `ocs_total`, `ocs_per_part`, `n_pixels_*` 四类统计 |
| 关键算法 | 有效像素：`NoV > eps` 且 `NoL > eps`；OCS = Σ A_pix·f_r·NoL·V_sun_macro |

#### 2.3.5 `05_postprocess/image_response_v0.4.py`

| 项 | 内容 |
|---|---|
| 输入 | 同上（camera_exr + V_sun_macro_mask）+ **corpus-level I_scale（预先计算）** |
| 输出 | `02_brdf_postprocess/{geom_id}/brdf_images/yaw{yyy}_pitch{ppp}_linear.exr`（I_linear float32）+ `_brdf.png`（log1p 8-bit）|
| manifest 字段 | `exr_path`, `png_path` |
| 关键算法 | **Two-pass 流程**（CR-CODE-002 修正）：<br>**Pass 1**：生成或 dry-run 统计全部 clean I_linear EXR，计算并冻结 corpus-level `I_scale = max(I_linear)` 全局最大值<br>**Pass 2**：使用同一个 I_scale 统一生成 log1p PNG：`I_norm = I_linear / I_scale`；`I_log = log1p(α·I_norm)/log1p(α)`；PNG = clip(round(I_log·255), 0, 255)<br>**禁止 per-frame normalization** 作为主线训练输入；若保留 `I_scale_record` 只作为审计或可选对照字段 |

#### 2.3.6 `06_manifest/ocs_manifest_builder.py`

| 项 | 内容 |
|---|---|
| 输入 | 所有 per-frame OCS JSON、四类像素统计、camera/sun 矩阵、路径 |
| 输出 | `03_manifests/ocs_manifest_v0.4_{single/multi}_geom_{geom_id}.json` |
| schema | 见 `14` §3.1（含 sun_visibility/shadow_mapping_method/depth_epsilon_m/record_id）|

#### 2.3.7 `06_manifest/image_manifest_builder.py`

| 项 | 内容 |
|---|---|
| 输入 | 所有 linear EXR + PNG 路径、log1p_alpha、I_scale、sun_visibility/shadow_mapping_method |
| 输出 | `03_manifests/image_manifest_v0.4_{single/multi}_geom_{geom_id}.json` |
| schema | 见 `14` §3.2（含 v_sun_macro_mode/v_sun_macro_applied_to_image）|

#### 2.3.8 `08_inversion/train_*_v0.4.py`

| 项 | 内容 |
|---|---|
| 输入 | OCS/image manifest、split 文件、超参 |
| 输出 | `05_runs/run_{id}/`（source_data.json + summary.json + model_best.pt + per_attitude_errors.csv + train_history.csv）|
| 必做 | `14` §8.1 一致性检查通过；生成 source_data.json 含六子版本；禁止 latest-run 自动发现 |

---

## 三、第一批最小验证任务（代码阶段 gate）

### 3.1 优先级 P0（必须通过才能全量生成）

| 任务 | 模块 | 通过标准 | 详见 |
|---|---|---|---|
| depth round-trip sanity check | `10_validation/` + `04_sun_shadow/depth_round_trip_check.py` | 3 已知点 camera/sun 双向 round-trip 误差 < 数值容差 | `13` §7.4.2 |
| 20 姿态 shadow validation | `10_validation/validate_20_attitudes.py` | 高/低/边缘/典型姿态覆盖；V_sun_macro_mask 物理合理；depth_epsilon_m_final 校准 | `13` §12.6 |

### 3.2 优先级 P1（建议在小规模验证中完成）

| 任务 | 模块 | 通过标准 | 详见 |
|---|---|---|---|
| 3 姿态 camera geometry pass 检查 | `02_blender/render_camera_geometry.py` | Normal/Depth/IndexOB 物理合理 | `13` §12.1 |
| 3 姿态 Position/WorldCoord 检查 | 同上 | P_world 与已知几何比对 | — |
| 3 姿态 sun-view depth 检查 | `02_blender/render_sun_depth.py` | sun_depth 完整、深度合理 | — |
| 5 姿态 V_sun_macro 对图像影响检查 | `10_validation/validate_v_sun_macro_on_image.py` | sun-shadowed 像素归零，EXR/PNG 同步 | `13` §12.7 |

### 3.3 可选（可在全量生成后做）

- per-part OCS 比例审计（`13` §12.4）
- log1p α quick ablation（`13` §12.5）
- 薄板 depth-buffer 审计（`13` §12.2）

---

## 四、实施顺序建议

### 4.0 第零步：环境记录与单姿态 smoke test（0.5-1 天）

1. 在 `06_v0.4_code/00_config/environment.md` 记录实际执行环境：
   - Blender 版本。
   - Python / conda 环境名。
   - PyTorch / CUDA / GPU 型号。
   - 关键 Python 包版本。
2. 如环境稳定，导出 `environment.yml` 或 `requirements.txt`。
3. 用 1 个简单姿态（建议 yaw=0°, pitch=0°）跑最小链路 smoke test：
   - camera geometry pass。
   - Position AOV 可用性检查；不可用则记录 depth+matrix 重建路径。
   - sun-view depth pass。
   - 单姿态 V_sun_macro reprojection。
   - 单姿态 BRDF/OCS/image 后处理试跑。
4. 记录单姿态耗时、EXR/PNG/npy 文件体量和全量生成粗估：
   - single-geom 2664 姿态耗时/存储。
   - multi-geom 额外 4 组的耗时/存储。
5. 产物写入：

```text
v0.4_results/00_validation/phase0_smoke_test_report.md
v0.4_results/00_validation/resource_estimate.json
```

### 4.1 第一步：复用旧代码搭建骨架（1-2 天）

1. 复制 `materials.py` / `geometry.py` / `config.py` 到 `06_v0.4_code/00_config/`，修改 yaw 网格为 72
2. 复制 `brdf_postprocess.py` EXR 读取部分到 `06_v0.4_code/03_brdf/`
3. 搭建 `06_v0.4_code/` 目录结构

### 4.2 第二步：实现 depth round-trip（2-3 天）

1. 实现 `02_blender/render_camera_geometry.py`（先不含 Position AOV）
2. 实现 `04_sun_shadow/depth_round_trip_check.py`
3. 用 3 个已知点验证 depth→camera_local→world→camera_local 闭环
4. 确定 Blender depth 符号/单位/local-z 映射

### 4.3 第三步：实现 Position + sun-view + reprojection（3-5 天）

1. 尝试 Blender Position AOV 输出；不可行则用 depth+matrix 重建
2. 实现 `02_blender/render_sun_depth.py`
3. 实现 `04_sun_shadow/sun_shadow_reprojection.py`（矩阵方向按 `13` §7.3.1）
4. 最近邻采样 sun_depth（避免轮廓插值误判）

### 4.4 第四步：20 姿态 shadow validation（2-3 天）

1. 先用 3 个代表姿态（低遮挡 / 高遮挡 / 边缘）快速迭代 shadow reprojection 实现
2. 稳定后再进入正式 20 姿态 gate
3. 实现 `10_validation/validate_20_attitudes.py`
4. 扫描 depth_epsilon_m 候选，选出不误判不漏判的最终值
5. 若验证失败，根据失败模式降级为 Level 1（`camera_visible_nol`），或修正实现后重测全部 20 姿态
6. 失败时使用 `02_第一批最小验证任务清单_Claude.md` 中的失败诊断记录字段，避免只保留口头判断

### 4.5 第五步：BRDF/OCS/image 后处理（3-4 天）

1. 实现 `03_brdf/brdf_models_v0.4.py`（eps 边界）
2. 实现 `05_postprocess/ocs_integration_v0.4.py`
3. 实现 `05_postprocess/image_response_v0.4.py`（**two-pass 流程，CR-CODE-002**）：
   - **Pass 1**：生成或 dry-run 统计全部 clean I_linear EXR（至少覆盖 single-geom 2664 姿态）
   - 计算并冻结 corpus-level `I_scale = max(I_linear)` 全局最大值
   - **Pass 2**：使用同一个 I_scale 统一生成所有 log1p PNG
   - **禁止 per-frame normalization** 作为主线；若保留 `I_scale_record`，只作为 manifest 审计字段
4. 5 姿态 V_sun_macro 对图像影响检查通过

### 4.6 第六步：manifest 生成与一致性检查（2 天）

1. 实现 `06_manifest/ocs_manifest_builder.py`
2. 实现 `06_manifest/image_manifest_builder.py`（写入 corpus-level `I_scale`，见 `14` §3.2）
3. 实现 `06_manifest/consistency_checker.py`

### 4.7 第七步（gate 通过）：全量生成（视硬件，5-10 天）

1. 根据 Phase 0 的 `resource_estimate.json` 确认磁盘空间和预计耗时
2. 渲染 2664 × 1 camera/sun geometry pass（single-geom phase63）
3. 生成 2664 V_sun_macro_mask
4. **Pass 1**：BRDF 后处理生成全部 2664 I_linear EXR，统计 corpus-level I_scale
5. **Pass 2**：使用统一 I_scale 生成全部 2664 log1p PNG（**CR-CODE-002 two-pass**）
6. OCS 积分全部 2664 姿态
7. 生成 single-geom OCS/image manifest

### 4.8 第八步：反演训练与补充实验（10-15 天）

1. split 生成
2. OCS-only / image-only / fusion (single-geom)（**训练前必须通过 `14` §8.1 一致性检查，确认 OCS/image manifest 使用同一 I_scale、同一 visibility 版本**）
3. multi-geom 扩展（2664 × 4 额外 geom，每个 geom 独立 I_scale 计算或复用 phase63 I_scale，见 manifest 定义）
4. 退化与补充实验（12b/12c/12f/12g）

---

## 五、进入全量重跑的 gate 条件

**必须全部通过才能进入 §四.7 全量生成**：

1. ✅ depth round-trip sanity check（3 已知点通过）
2. ✅ 20 姿态 shadow validation（V_sun_macro_mask 物理合理、depth_epsilon_m_final 确定）—— **CR-CODE-001 修正：任一姿态失败必须修正重测或整体降级，不允许排除失败姿态后继续 Level 2**
3. ✅ 3 姿态 camera geometry pass 物理检查通过
4. ✅ 3 姿态 sun-view depth 完整性检查通过
5. ✅ 5 姿态 V_sun_macro 对图像影响检查通过（sun-shadowed 像素归零）
6. ✅ BRDF/OCS/image 后处理 3 姿态试跑成功
7. ✅ OCS/image manifest 生成成功、schema 符合 `14` 定义
8. ✅ 一致性检查脚本实现并通过测试
9. ✅ **I_scale two-pass 流程实现完成**（CR-CODE-002 修正：Pass 1 统计全局 I_scale → Pass 2 统一生成 PNG）

**任一 gate 失败处置**：
- 若 sun shadow reprojection 不可行：降级为 Level 1（`camera_visible_nol`，`V_sun_macro ≡ 1`），manifest 记录降级原因
- 若 Position AOV 不可用：改用 depth+matrix 重建，manifest 中 `position_exr_path = null`
- 其他失败：诊断根因、修正实现、重测，不跳过 gate

---

## 六、风险与不确定性

| 风险 | 可能性 | 缓解措施 |
|---|---|---|
| Blender Position AOV 不支持 | 中 | 预备 depth+matrix 重建方案（已写入 `13` §7.4.1）|
| sun shadow reprojection 系统性错位 | 低 | depth round-trip + 20 姿态验证可提前发现 |
| depth_epsilon_m 难以校准（误判/漏判 trade-off 无解）| 低 | 降级为 Level 1，论文写作边界诚实声明 |
| 全量生成耗时超预期（2664×5 EXR）| 中 | 可先完成 single-geom 2664，multi-geom 延后 |
| 旧补充实验代码复用度低于预期 | 高 | 已标记必须重写，实施顺序放在反演主线之后 |
| 环境依赖未记录导致复现困难 | 中 | Phase 0 写入 `environment.md` / `environment.yml` |
| 中间产物体量过大 | 中 | Phase 0 先做资源估算；single-geom 复核前不自动清理关键 EXR/npy |

---

## 七、实施阶段辅助文件建议（非 gate）

这些文件不阻塞代码启动，但建议在 Phase 0 或首次失败时补齐：

```text
06_v0.4_code/00_config/environment.md
06_v0.4_code/00_config/environment.yml
v0.4_results/00_validation/phase0_smoke_test_report.md
v0.4_results/00_validation/resource_estimate.json
v0.4_results/00_validation/failure_diagnosis_template.md
```

`failure_diagnosis_template.md` 建议包含：

- 失败任务名称。
- 姿态与 geom_id。
- 输入文件路径。
- 失败现象截图或统计。
- 矩阵方向检查。
- depth 符号/单位检查。
- 最近邻采样与边缘误判检查。
- 修正动作。
- 重测结果。

---

## 八、需要 Codex 审阅的位置（可选）

如果后续实施过程中遇到以下情况，可请 Codex 短审：

1. sun shadow reprojection 实现后发现矩阵方向或 depth 定义仍有歧义
2. 20 姿态验证失败，需要判断是降级还是修正
3. manifest schema 实现与 `14` 定义不一致
4. 一致性检查逻辑有遗漏

否则按本计划推进即可，不需要逐步审阅。

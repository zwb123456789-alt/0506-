# 32 1C-E14 Phase 0 Step 7b 全量前入口检查与字段补齐规划（Claude执行报告）

执行时间：2026-06-24  
执行端：Claude  
任务：Phase 0 Step 7b 全量前最后入口检查与 manifest 字段补齐规划  
依据文件：R30_Codex_审阅_1C-E13-FIX01通过并放行Phase0_Step7a.md

---

## 1. 执行摘要

本轮任务对 Phase 0 Step 7a 的 manifest 试运行结果进行了全量前最后入口检查，重点分析了仍为 `null` 或未展开的字段，并对 manifest builder/checker 进行了缺失功能排查。

**核心发现**：
- 5 个字段在 Phase 0 trial 中为 `null`，其中 4 个必须在全量生成前补齐，1 个可选
- manifest builder 缺少 BRDF 正式命名检查、路径存在性检查
- consistency checker 缺少全量前必须的路径存在性验证
- 缺少断点续跑和失败恢复标识机制

**风险等级**：中等（全量前必须修复）

---

## 2. Phase 0 Step 7a Manifest 字段状态分析

### 2.1 当前为 `null` 的字段

从 `ocs_manifest_v0_4_step6trial.json` 中检测到以下字段在所有 5 个 record 中均为 `null`：

| 字段 | 当前状态 | 规范要求 | 全量前处理裁决 |
|---|---|---|---|
| `camera_matrix_world` | `null` | float[4][4] | **必须补齐** |
| `sun_camera_matrix_world` | `null` | float[4][4] | **必须补齐** |
| `position_exr_path` | `null` | string or null | **可选（允许 null）** |
| `sun_visibility_mask_path` | `null` | string or null | **必须补齐** |
| `n_pixels_per_part` | 已有值 | dict | 已完整，无需处理 |

### 2.2 字段裁决详细说明

#### 2.2.1 `camera_matrix_world` 和 `sun_camera_matrix_world`

**现状**：
- 两个字段在所有 record 中均为 `null`
- `build_ocs_manifest_v0_4.py` 的 `main()` 函数中硬编码为 `None`（第 209-210 行）
- 源码注释："Phase 0 使用固定相机矩阵（identity 或从配置读取）"

**规范要求**（14号 §3.1）：
- `camera_matrix_world`：camera local → world，4x4 变换矩阵
- `sun_camera_matrix_world`：sun camera local → world，4x4 变换矩阵
- 这两个矩阵是 sun shadow reprojection 的必要输入（13号 §7.3）

**风险分析**：
- **高风险**：sun shadow reprojection 依赖这两个矩阵将 sun-view depth 重投影到 camera-view，如果矩阵为 `null`，全量渲染的 shadow validation 无法验证正确性
- **全量前阻断**：必须从 Blender 渲染脚本记录中提取实际矩阵

**处理裁决**：
```text
状态：全量前必须补齐
来源：Blender Python 渲染脚本记录（或从 EXR metadata 提取）
方式：
  1. 在 Blender 渲染脚本中输出 camera.matrix_world 和 sun_camera.matrix_world 到 JSON
  2. manifest builder 从 JSON 读取并填入每个 record
  3. 如果 Blender 未记录，从 shadow_passes EXR metadata 提取（需验证 Blender 是否写入）
时机：全量 2664 姿态生成脚本启动前
```

#### 2.2.2 `position_exr_path`

**现状**：
- 所有 record 中均为 `null`
- `build_ocs_manifest_v0_4.py` 第 128 行注释："Phase 0 暂未独立输出 Position pass"

**规范要求**（14号 §3.1）：
- `string or null`：Position/WorldCoord EXR 路径，`null` 表示由 depth + 矩阵重建
- 规范明确允许 `null`

**风险分析**：
- **低风险**：规范允许 `null`，shadow reprojection 可以从 depth + camera_matrix_world 重建世界坐标
- **性能考虑**：独立输出 Position pass 可避免重复计算，但非阻断项

**处理裁决**：
```text
状态：可选（允许 null）
建议：保持 null，由 shadow reprojection 脚本从 depth + camera_matrix_world 重建
理由：
  1. 规范明确允许 null
  2. 减少存储开销（256x256x3 float32 per frame = ~0.8 MB/frame，2664 姿态 ~2.1 GB）
  3. 重建计算量可接受
时机：如需优化性能，可在 Phase 1 考虑输出独立 Position pass
```

#### 2.2.3 `sun_visibility_mask_path`

**现状**：
- 所有 record 中均为 `null`
- `build_ocs_manifest_v0_4.py` 第 129 行注释："Phase 0 暂未独立输出 V_sun_macro mask"

**规范要求**（14号 §3.1）：
- `string or null`：V_sun_macro_mask 路径
- `null if sun_visibility == "camera_visible_nol"`
- 当前 `sun_visibility = "camera_visible_nol_plus_sun_shadow_pass"`，应有路径

**风险分析**：
- **中等风险**：虽然 shadow reprojection 脚本可实时计算 V_sun_macro，但独立存储 mask 可用于：
  - 审计和可视化验证
  - 避免重复计算（训练时多次读取）
  - 与 image 预处理流程解耦

**处理裁决**：
```text
状态：全量前必须补齐
来源：Python sun shadow reprojection 脚本输出
方式：
  1. shadow reprojection 脚本计算 V_sun_macro 后，输出为独立 PNG/NPY 文件
  2. manifest builder 记录路径到 sun_visibility_mask_path
  3. consistency checker 验证路径存在性
时机：全量 2664 姿态 shadow reprojection 完成时同步输出
存储格式：建议 uint8 PNG（256x256，~16 KB/frame，2664 姿态 ~43 MB）
```

---

## 3. Manifest Builder/Checker 缺失功能排查

### 3.1 `build_ocs_manifest_v0_4.py` 缺失功能

| 缺失项 | 当前状态 | 全量前必要性 | 建议修复 |
|---|---|---|---|
| **BRDF 正式命名检查** | 使用 `brdf_version` 推断 `brdf_model`（第 160-166 行），无验证 | **必须** | 添加 BRDF 参数文件校验 |
| **相机矩阵来源** | 硬编码为 `None`（第 209-210 行） | **必须** | 从 Blender 脚本记录或 EXR metadata 读取 |
| **路径存在性检查** | 无 | **必须** | 添加 EXR 路径检查，全量前拦截缺失文件 |

#### 3.1.1 BRDF 正式命名检查

**当前逻辑**（第 158-166 行）：
```python
if "B0" in brdf_version or "phong" in brdf_version or "provisional" in brdf_version:
    brdf_model = "phong_like_provisional_baseline"
elif "GGX" in brdf_version or "ggx" in brdf_version:
    brdf_model = "ggx_cook_torrance"
else:
    brdf_model = "unknown"
```

**问题**：
- 仅从 `brdf_version` 字符串推断，未验证实际 BRDF 参数文件
- Phase 0 使用 `B0_phong_like_provisional`，但全量前需要正式 BRDF branch 命名

**建议修复**：
```python
# 添加 BRDF 参数文件验证
def validate_brdf_branch(brdf_version, brdf_params_path):
    """验证 brdf_version 与实际 BRDF 参数文件一致"""
    if not os.path.isfile(brdf_params_path):
        raise FileNotFoundError(f"BRDF params file not found: {brdf_params_path}")
    
    with open(brdf_params_path, 'r') as f:
        params = json.load(f)
    
    # 检查 brdf_version 是否匹配参数文件的 version 字段
    if params.get("version") != brdf_version:
        raise ValueError(f"brdf_version mismatch: manifest={brdf_version}, file={params.get('version')}")
    
    return params.get("model_type")  # 返回实际 model_type
```

#### 3.1.2 相机矩阵来源

**建议修复**：
```python
# 添加矩阵读取函数
def read_camera_matrices_from_blender_log(log_path, label):
    """从 Blender 渲染脚本记录的 JSON 中读取相机矩阵"""
    log_file = os.path.join(log_path, f"{label}_camera_matrices.json")
    if not os.path.isfile(log_file):
        return None, None
    
    with open(log_file, 'r') as f:
        data = json.load(f)
    
    return np.array(data["camera_matrix_world"]), np.array(data["sun_camera_matrix_world"])
```

#### 3.1.3 路径存在性检查

**建议修复**：
```python
# 在 build_ocs_manifest() 函数末尾添加
def check_exr_paths_exist(manifest, base_dir):
    """检查 manifest 中所有 EXR 路径是否存在"""
    missing = []
    for rec in manifest["records"]:
        for path_key in ["camera_exr_path", "sun_depth_exr_path", "exr_path"]:
            path = rec.get(path_key)
            if path and not os.path.isfile(os.path.join(base_dir, path)):
                missing.append(f"{rec['record_id']}: {path_key}={path}")
    
    if missing:
        raise FileNotFoundError(f"Missing EXR files:\n" + "\n".join(missing))
```

### 3.2 `build_image_manifest_v0_4.py` 缺失功能

| 缺失项 | 当前状态 | 全量前必要性 | 建议修复 |
|---|---|---|---|
| **路径存在性检查** | 无 | **必须** | 添加 PNG/EXR 路径检查 |
| **I_scale 全量策略** | 使用 Step 6 summary 的 `i_scale_smallrun`（第 56 行） | **必须明确** | 全量前决定是否沿用 Step 5 校准值 |

#### 3.2.1 路径存在性检查

**建议修复**（同 OCS manifest）：
```python
def check_image_paths_exist(manifest, base_dir):
    """检查 manifest 中所有图像路径是否存在"""
    missing = []
    for rec in manifest["records"]:
        for path_key in ["png_path", "exr_linear_path"]:
            path = rec.get(path_key)
            if path and not os.path.isfile(os.path.join(base_dir, path)):
                missing.append(f"{rec['record_id']}: {path_key}={path}")
    
    if missing:
        raise FileNotFoundError(f"Missing image files:\n" + "\n".join(missing))
```

#### 3.2.2 I_scale 全量策略

**当前策略**（从 Step 6 summary）：
```json
"i_scale_policy": "fixed = i_scale_step5 from Phase0 Step5; no per-frame normalization"
"i_scale_smallrun": 0.5444863931551639
```

**全量前决策**：
- **选项 A**：沿用 Phase 0 Step 5 校准的 `i_scale_step5 = 0.5445`（当前策略）
- **选项 B**：全量 2664 姿态渲染完成后重新计算 `global max I_linear`

**建议**：沿用选项 A，理由：
1. Step 5 已用 20 姿态校准，覆盖了 yaw/pitch 多样性
2. 避免全量渲染完成后才能确定 I_scale（影响流程）
3. 如发现全量中有极端高亮帧，可在 Phase 1 重新校准

### 3.3 `check_manifest_consistency_v0_4.py` 缺失功能

| 缺失项 | 当前状态 | 全量前必要性 | 建议修复 |
|---|---|---|---|
| **路径存在性验证** | 无 | **必须** | 添加跨 manifest 路径存在性检查 |
| **相机矩阵非空检查** | 无 | **必须** | 当 `sun_visibility != "camera_visible_nol"` 时检查矩阵非 `null` |
| **sun_visibility_mask_path 非空检查** | 无 | **必须** | 当 `sun_visibility` 包含 shadow 时检查路径非 `null` |

#### 3.3.1 路径存在性验证

**建议新增检查**：
```python
# 检查 12: OCS manifest 路径存在性
check_name = "ocs_exr_paths_exist"
missing_ocs = []
for rec in ocs_manifest["records"]:
    for path_key in ["camera_exr_path", "sun_depth_exr_path", "exr_path"]:
        path = rec.get(path_key)
        if path and not os.path.isfile(path):
            missing_ocs.append(f"{rec['record_id']}: {path_key}")

status = "PASS" if not missing_ocs else "FAIL"
checks.append({
    "check": check_name,
    "status": status,
    "missing_paths": missing_ocs,
})

# 检查 13: Image manifest 路径存在性
check_name = "image_paths_exist"
missing_img = []
for rec in image_manifest["records"]:
    for path_key in ["png_path", "exr_linear_path"]:
        path = rec.get(path_key)
        if path and not os.path.isfile(path):
            missing_img.append(f"{rec['record_id']}: {path_key}")

status = "PASS" if not missing_img else "FAIL"
checks.append({
    "check": check_name,
    "status": status,
    "missing_paths": missing_img,
})
```

#### 3.3.2 相机矩阵非空检查

**建议新增检查**：
```python
# 检查 14: camera_matrix_world 非空（当需要 shadow reprojection 时）
check_name = "camera_matrix_world_non_null"
null_records = []
if ocs_sun_vis in ["camera_visible_nol_plus_sun_shadow_pass", "camera_visible_nol_plus_python_raycast"]:
    for rec in ocs_manifest["records"]:
        if rec.get("camera_matrix_world") is None or rec.get("sun_camera_matrix_world") is None:
            null_records.append(rec["record_id"])

status = "PASS" if not null_records else "FAIL"
checks.append({
    "check": check_name,
    "status": status,
    "null_matrix_records": null_records,
})
```

#### 3.3.3 sun_visibility_mask_path 非空检查

**建议新增检查**：
```python
# 检查 15: sun_visibility_mask_path 非空（当需要 sun shadow 时）
check_name = "sun_visibility_mask_path_non_null"
null_mask_records = []
if ocs_sun_vis in ["camera_visible_nol_plus_sun_shadow_pass", "camera_visible_nol_plus_python_raycast"]:
    for rec in ocs_manifest["records"]:
        if rec.get("sun_visibility_mask_path") is None:
            null_mask_records.append(rec["record_id"])

status = "PASS" if not null_mask_records else "FAIL"
checks.append({
    "check": check_name,
    "status": status,
    "null_mask_records": null_mask_records,
})
```

---

## 4. 全量失败恢复与断点续跑策略

### 4.1 当前缺失

manifest builder/checker 当前无断点续跑和失败恢复机制。全量 2664 姿态渲染/后处理如果中途失败，无法从断点恢复，必须重新开始。

### 4.2 建议策略

#### 4.2.1 渲染阶段断点续跑

**机制**：
```text
1. Blender 渲染脚本在每个姿态完成后立即记录到 checkpoint.json
2. 重启时读取 checkpoint.json，跳过已完成的姿态
3. manifest builder 只处理 checkpoint.json 中标记为 COMPLETE 的记录
```

**checkpoint.json 格式**：
```json
{
  "last_completed_index": 42,
  "completed_records": [
    {"record_id": "phase63_yaw000_pitch+000", "status": "COMPLETE", "timestamp": "..."},
  ],
  "failed_records": [
    {"record_id": "phase63_yaw090_pitch+000", "status": "FAILED", "error": "...", "timestamp": "..."}
  ]
}
```

#### 4.2.2 Manifest 增量更新

**机制**：
```text
1. manifest builder 支持 --append 模式，追加新 record 而非覆盖
2. consistency checker 支持 --partial 模式，只检查新增 record
3. 全量完成后执行 --finalize 模式，生成最终 manifest 并做完整一致性检查
```

#### 4.2.3 失败恢复标识

**在 manifest 顶层添加字段**：
```json
{
  "build_status": "complete",
  "n_total_expected": 2664,
  "n_records_current": 2664,
  "build_history": [
    {"timestamp": "2026-06-24T10:00:00", "action": "init", "n_records": 0},
    {"timestamp": "2026-06-24T15:00:00", "action": "append", "n_records": 1000},
    {"timestamp": "2026-06-24T20:00:00", "action": "finalize", "n_records": 2664}
  ]
}
```

---

## 5. 可执行风险清单

### 5.1 全量前阻断风险（必须修复）

| 风险ID | 风险描述 | 影响 | 修复优先级 | 预计修复工作量 |
|---|---|---|---|---|
| **R1** | `camera_matrix_world` 和 `sun_camera_matrix_world` 为 `null` | shadow reprojection 无法执行 | **P0** | 1-2 小时 |
| **R2** | `sun_visibility_mask_path` 为 `null` | 缺少审计和验证依据 | **P0** | 0.5-1 小时 |
| **R3** | manifest builder 缺少路径存在性检查 | 全量运行到一半才发现文件缺失 | **P0** | 1 小时 |
| **R4** | consistency checker 缺少相机矩阵非空检查 | 无法拦截矩阵缺失的 manifest | **P0** | 0.5 小时 |
| **R5** | 缺少断点续跑机制 | 2664 姿态渲染失败后必须重新开始 | **P1** | 2-3 小时 |

### 5.2 全量前建议修复（非阻断）

| 建议ID | 建议描述 | 收益 | 优先级 | 预计工作量 |
|---|---|---|---|---|
| **S1** | 添加 BRDF 参数文件验证 | 避免 BRDF branch 不一致 | **P1** | 1 小时 |
| **S2** | 明确全量 I_scale 策略 | 避免全量后重新归一化 | **P1** | 决策 10 分钟 |
| **S3** | 添加 manifest 增量更新模式 | 灵活应对全量过程变更 | **P2** | 2 小时 |

---

## 6. 最小修复建议（全量前必须）

### 6.1 修复清单

按执行顺序：

```text
1. [R1] 从 Blender 渲染脚本记录中提取相机矩阵
   - 修改 Blender Python 脚本，输出 camera.matrix_world 和 sun_camera.matrix_world 到 JSON
   - 修改 build_ocs_manifest_v0_4.py，从 JSON 读取矩阵并填入 manifest
   - 小规模验证：重跑 Phase 0 Step 7a trial，检查矩阵非 null

2. [R2] 独立输出 sun_visibility_mask
   - 修改 sun shadow reprojection 脚本，计算 V_sun_macro 后输出为 PNG
   - 修改 build_ocs_manifest_v0_4.py，记录 mask 路径到 sun_visibility_mask_path
   - 小规模验证：检查 mask 文件存在且与 OCS n_pixels_sun_visible 一致

3. [R3] 添加路径存在性检查到 manifest builder
   - 在 build_ocs_manifest_v0_4.py 和 build_image_manifest_v0_4.py 末尾添加路径检查
   - 小规模验证：故意删除一个 EXR，检查是否报错

4. [R4] 添加相机矩阵和 mask 路径非空检查到 consistency checker
   - 在 check_manifest_consistency_v0_4.py 添加检查 14 和检查 15
   - 小规模验证：故意将矩阵设为 null，检查是否 FAIL

5. [S1] 添加 BRDF 参数文件验证（建议）
   - 创建正式 BRDF 参数文件 JSON（如 brdf_params_B1_ggx_cook_torrance.json）
   - 修改 manifest builder 从参数文件推断 brdf_model
   - 小规模验证：检查 brdf_model 与参数文件一致

6. [S2] 明确全量 I_scale 策略（决策）
   - 裁决：沿用 Phase 0 Step 5 校准值 i_scale = 0.5445
   - 在 image manifest builder 中固化此值
   - 记录到文档：如发现全量中有极端高亮帧，Phase 1 重新校准
```

### 6.2 小规模验证流程（Step 7c 候选）

修复完成后，建议执行 **Phase 0 Step 7c：全量前最后 dry-run**：

```text
1. 选择 3 个新姿态（Phase 0 Step 6 未包含的）
2. 完整执行：Blender 渲染 → shadow reprojection → BRDF 后处理 → manifest 构建 → consistency check
3. 验证：
   - camera_matrix_world 和 sun_camera_matrix_world 非 null 且合理
   - sun_visibility_mask_path 指向存在的文件
   - mask 文件与 n_pixels_sun_visible 一致
   - consistency check 全部 PASS
   - 路径存在性检查全部 PASS
4. 如 Step 7c 通过，放行全量 2664 生成
```

---

## 7. 边界确认

本轮执行严格遵守 R30 指定边界：

```text
✓ 未进入全量 2664 姿态生成
✓ 未重渲染全量 EXR
✓ 未训练模型
✓ 未修改论文正文
✓ 未修改冻结文件 13/14/24/25
✓ 未写入 04_Codex审阅/
✓ 未生成 Codex 裁决文件
```

---

## 8. 下一步建议

建议 Codex 审阅本报告后，裁决：

```text
1. 是否认可上述字段处理裁决和风险清单
2. 是否需要 Phase 0 Step 7c 小规模 dry-run 验证修复
3. 何时、以何种边界放行全量 2664 生成
4. 是否要求断点续跑机制（R5）必须在全量前完成
```

本报告已完整覆盖 R30 指定的六项任务，可交回 Codex 审阅。

---

## 附录：字段补齐规划总表

| 字段 | 当前状态 | 规范要求 | 全量前裁决 | 来源 | 修复优先级 |
|---|---|---|---|---|---|
| `camera_matrix_world` | `null` | float[4][4] | 必须补齐 | Blender 脚本记录 | P0 |
| `sun_camera_matrix_world` | `null` | float[4][4] | 必须补齐 | Blender 脚本记录 | P0 |
| `position_exr_path` | `null` | string or null | 可选（保持 null） | - | - |
| `sun_visibility_mask_path` | `null` | string or null | 必须补齐 | Python shadow reprojection | P0 |
| `n_pixels_per_part` | 已有值 | dict | 无需处理 | - | - |
| builder 路径检查 | 缺失 | 必须 | 必须添加 | 代码修改 | P0 |
| checker 矩阵检查 | 缺失 | 必须 | 必须添加 | 代码修改 | P0 |
| checker mask 检查 | 缺失 | 必须 | 必须添加 | 代码修改 | P0 |
| 断点续跑机制 | 缺失 | 建议 | 建议添加 | 代码修改 | P1 |
| BRDF 参数验证 | 缺失 | 建议 | 建议添加 | 代码修改 | P1 |
| I_scale 策略 | 已明确 | 必须 | 沿用 Step 5 值 | 决策 | P1 |

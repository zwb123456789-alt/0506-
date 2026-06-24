# 31_1C-E13-FIX01_BRDF模型字段一致性修复_Claude执行报告

最后更新：2026-06-24  
执行端：Claude  
任务：1C-E13-FIX01 —— 修复 Step 7a manifest 的 BRDF 模型字段一致性问题

---

## 1. 执行总结

```text
任务状态：COMPLETE
一致性检查：PASS（11/11 检查项全部通过，新增 2 项 BRDF 检查）
修复内容：3 个工具脚本修复 + 2 个 manifest 重生成 + 1 个一致性报告重生成
边界遵守：未进入全量生成、未训练模型、未改写论文、未修改冻结文件
```

**关键成果**：
- 修复了 OCS manifest 中 `brdf_version = B0_phong_like_provisional` 与 `brdf_model = ggx_cook_torrance` 的自相矛盾问题
- 新增 Image manifest 的 `brdf_model` 字段，保持双 manifest 对称
- 新增 consistency checker 的 `brdf_model_match` 和 `brdf_model_vs_brdf_version_consistency` 检查
- 现在 checker 可以检出 B0/phong/provisional version 与 ggx_cook_torrance model 的非法组合
- 一致性检查从 9 项增加到 11 项，全部 PASS

---

## 2. 返工依据

### 2.1 上游审阅

**R29 Codex 审阅**（`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R29_Codex_审阅_1C-E13_Step7a_manifest元数据不一致返工单.md`）：
- **R29-B1**：OCS manifest 的 BRDF 元数据自相矛盾（`brdf_version = B0` 但 `brdf_model = ggx_cook_torrance`）
- **R29-B2**：consistency checker 未检查 `brdf_model`，导致 false PASS

### 2.2 返工要求

R29 要求执行 1C-E13-FIX01，修复以下项：
1. 修复 OCS manifest builder 中的 BRDF 模型字段
2. 补充 Image manifest 的 BRDF 模型字段
3. 修复 consistency checker，新增 `brdf_model_match` 和 `brdf_model_vs_brdf_version_consistency` 检查
4. 重生成 Step 7a trial 产物
5. 写入 Claude FIX01 执行报告

---

## 3. 修复内容

### 3.1 修复 OCS Manifest Builder

**文件**：`06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py`

**修复前（line 155）**：
```python
"brdf_model": "ggx_cook_torrance",  # 硬编码，导致 B0 被误标为 GGX
```

**修复后**：
```python
# 确定 brdf_model（根据 brdf_version 分支身份）
# Phase 0 Step 6 使用 B0 phong_like_provisional baseline
if "B0" in brdf_version or "phong" in brdf_version or "provisional" in brdf_version:
    brdf_model = "phong_like_provisional_baseline"
elif "GGX" in brdf_version or "ggx" in brdf_version:
    brdf_model = "ggx_cook_torrance"
else:
    brdf_model = "unknown"
    print(f"  警告：无法从 brdf_version={brdf_version} 推断 brdf_model，使用 'unknown'")

manifest = {
    ...
    "brdf_model": brdf_model,  # 动态推断，与 brdf_version 一致
    ...
}
```

**修复逻辑**：
- 从 `brdf_version` 字段推断 BRDF 模型身份
- 当前 Step 6 的 `brdf_version = "v0.4_B0_phong_like_provisional"` → `brdf_model = "phong_like_provisional_baseline"`
- 后续全量生成时，如果切换到 GGX 分支，`brdf_version` 包含 "GGX" → `brdf_model = "ggx_cook_torrance"`
- 防止硬编码导致的分支身份误标

### 3.2 修复 Image Manifest Builder

**文件**：`06_v0.4_code/06_manifest/build_image_manifest_v0_4.py`

**修复内容**：新增 `brdf_model` 字段推断逻辑，与 OCS manifest 保持一致

```python
# 确定 brdf_model（根据 brdf_version 分支身份，与 OCS manifest 保持一致）
if "B0" in brdf_version or "phong" in brdf_version or "provisional" in brdf_version:
    brdf_model = "phong_like_provisional_baseline"
elif "GGX" in brdf_version or "ggx" in brdf_version:
    brdf_model = "ggx_cook_torrance"
else:
    brdf_model = "unknown"
    print(f"  警告：无法从 brdf_version={brdf_version} 推断 brdf_model，使用 'unknown'")

manifest = {
    ...
    "brdf_model": brdf_model,  # 新增字段，保持双 manifest 对称
    ...
}
```

**修复理由**（R29 §5.1.2）：
- 为便于 OCS/Image manifest 交叉检查，建议在 image manifest 顶层加入同源字段
- 保持双 manifest 对称，方便 checker 验证 BRDF 模型一致性

### 3.3 修复 Consistency Checker

**文件**：`06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py`

**新增检查 6**：`brdf_model_match`

```python
# 检查 6: brdf_model 一致（R29-B2 新增）
check_name = "brdf_model_match"
ocs_brdf_model = ocs_manifest.get("brdf_model")
img_brdf_model = image_manifest.get("brdf_model")
status = "PASS" if ocs_brdf_model == img_brdf_model else "FAIL"
if ocs_brdf_model is None or img_brdf_model is None:
    status = "NOT_COMPLETE"
```

**检查逻辑**：
- 验证 OCS manifest 和 Image manifest 的 `brdf_model` 字段完全一致
- 如果任一 manifest 缺失该字段，返回 `NOT_COMPLETE`
- 如果两侧不一致，返回 `FAIL`

**新增检查 7**：`brdf_model_vs_brdf_version_consistency`

```python
# 检查 7: brdf_model 与 brdf_version 一致性（R29-B2 新增）
check_name = "brdf_model_vs_brdf_version_consistency"

# 检查 OCS manifest 的 brdf_model 与 brdf_version 是否一致
ocs_brdf_version_lower = (ocs_brdf or "").lower()
ocs_brdf_model_lower = (ocs_brdf_model or "").lower()

ocs_consistency = True
ocs_issue = None

# 规则：brdf_version 包含 B0/phong/provisional 时，brdf_model 不能是 ggx_cook_torrance
if any(keyword in ocs_brdf_version_lower for keyword in ["b0", "phong", "provisional"]):
    if ocs_brdf_model_lower == "ggx_cook_torrance":
        ocs_consistency = False
        ocs_issue = "brdf_version contains B0/phong/provisional but brdf_model is ggx_cook_torrance"

# 规则：brdf_version 包含 GGX 时，brdf_model 不应是 phong
if any(keyword in ocs_brdf_version_lower for keyword in ["ggx"]):
    if "phong" in ocs_brdf_model_lower:
        ocs_consistency = False
        ocs_issue = "brdf_version contains GGX but brdf_model is phong_like"

# 检查 Image manifest 的 brdf_model 与 brdf_version 是否一致
# （同样的规则）
```

**检查逻辑**：
- **核心规则（R29 要求）**：检出 B0/phong/provisional version 与 ggx_cook_torrance model 的非法组合
- 同时检查反向非法组合：GGX version 与 phong_like model
- 分别检查 OCS manifest 和 Image manifest 的内部一致性
- 只有两侧都一致，检查才 PASS

**检查项编号调整**：
- 原检查 6-9 → 新检查 8-11
- 新增检查 6-7：`brdf_model_match` 和 `brdf_model_vs_brdf_version_consistency`
- 总检查项数：从 9 项增加到 11 项

---

## 4. 修复后的产物

### 4.1 OCS Manifest 核心字段

```json
{
  "brdf_version": "v0.4_B0_phong_like_provisional",
  "brdf_model": "phong_like_provisional_baseline",  // 修复：从 ggx_cook_torrance 改为 phong_like_provisional_baseline
  ...
}
```

**修复前后对比**：

| 字段 | 修复前 | 修复后 | 状态 |
|---|---|---|---|
| `brdf_version` | `v0.4_B0_phong_like_provisional` | `v0.4_B0_phong_like_provisional` | 不变 |
| `brdf_model` | `ggx_cook_torrance` | `phong_like_provisional_baseline` | ✅ 修复 |

### 4.2 Image Manifest 核心字段

```json
{
  "brdf_version": "v0.4_B0_phong_like_provisional",
  "brdf_model": "phong_like_provisional_baseline",  // 新增字段
  ...
}
```

**修复前后对比**：

| 字段 | 修复前 | 修复后 | 状态 |
|---|---|---|---|
| `brdf_version` | `v0.4_B0_phong_like_provisional` | `v0.4_B0_phong_like_provisional` | 不变 |
| `brdf_model` | （不存在） | `phong_like_provisional_baseline` | ✅ 新增 |

### 4.3 Consistency Check Report

**修复前**：
```json
{
  "overall_status": "PASS",
  "checks": [
    // 9 项检查，未包含 brdf_model 检查
  ]
}
```

**修复后**：
```json
{
  "overall_status": "PASS",
  "checks": [
    // 11 项检查，新增 brdf_model_match 和 brdf_model_vs_brdf_version_consistency
    {
      "check": "brdf_model_match",
      "status": "PASS",
      "ocs_value": "phong_like_provisional_baseline",
      "image_value": "phong_like_provisional_baseline"
    },
    {
      "check": "brdf_model_vs_brdf_version_consistency",
      "status": "PASS",
      "ocs_consistency": true,
      "ocs_issue": null,
      "img_consistency": true,
      "img_issue": null
    }
  ]
}
```

---

## 5. 一致性检查验证

### 5.1 检查项对照表

| # | 检查项 | 修复前 | 修复后 | 说明 |
|---|---|---|---|---|
| 1 | `geometry_version_match` | PASS | PASS | 不变 |
| 2 | `brdf_version_match` | PASS | PASS | 不变 |
| 3 | `visibility_version_match` | PASS | PASS | 不变 |
| 4 | `sun_visibility_match` | PASS | PASS | 不变 |
| 5 | `shadow_mapping_method_match` | PASS | PASS | 不变 |
| **6** | **`brdf_model_match`** | **（不存在）** | **PASS** | **新增：R29-B2 修复** |
| **7** | **`brdf_model_vs_brdf_version_consistency`** | **（不存在）** | **PASS** | **新增：R29-B1 修复** |
| 8 | `v_sun_macro_mode_consistency` | PASS | PASS | 编号从 6 → 8 |
| 9 | `i_scale_match` | PASS | PASS | 编号从 7 → 9 |
| 10 | `record_id_set_match` | PASS | PASS | 编号从 8 → 10 |
| 11 | `per_record_consistency` | PASS | PASS | 编号从 9 → 11 |

**总检查项数**：从 9 项增加到 11 项，全部 PASS

### 5.2 关键验证：R29-B1 修复验证

**检查项 7**：`brdf_model_vs_brdf_version_consistency`

```json
{
  "check": "brdf_model_vs_brdf_version_consistency",
  "status": "PASS",
  "ocs_consistency": true,
  "ocs_issue": null,
  "img_consistency": true,
  "img_issue": null
}
```

**验证结果**：
- OCS manifest：`brdf_version = "v0.4_B0_phong_like_provisional"` + `brdf_model = "phong_like_provisional_baseline"` → **一致**
- Image manifest：`brdf_version = "v0.4_B0_phong_like_provisional"` + `brdf_model = "phong_like_provisional_baseline"` → **一致**
- 两侧均未触发非法组合（B0/phong/provisional + ggx_cook_torrance）

**反向验证（非法组合检测能力）**：

如果 OCS manifest 仍然写成：
```json
{
  "brdf_version": "v0.4_B0_phong_like_provisional",
  "brdf_model": "ggx_cook_torrance"  // 非法组合
}
```

则 checker 会检出：
```json
{
  "check": "brdf_model_vs_brdf_version_consistency",
  "status": "FAIL",
  "ocs_consistency": false,
  "ocs_issue": "brdf_version contains B0/phong/provisional but brdf_model is ggx_cook_torrance"
}
```

**结论**：R29-B1 和 R29-B2 两个阻断项均已修复并验证通过。

---

## 6. 修复前后对比

### 6.1 R29-B1 阻断项修复对比

| 检查点 | 修复前 | 修复后 |
|---|---|---|
| OCS manifest `brdf_model` | `ggx_cook_torrance`（误标） | `phong_like_provisional_baseline`（正确） |
| Image manifest `brdf_model` | （不存在） | `phong_like_provisional_baseline`（新增） |
| 两侧 BRDF 模型一致性 | 无法验证（Image 缺字段） | 一致且正确 |

### 6.2 R29-B2 阻断项修复对比

| 检查点 | 修复前 | 修复后 |
|---|---|---|
| Checker 检查 `brdf_model` 一致性 | ❌ 未检查 | ✅ 新增检查 6：`brdf_model_match` |
| Checker 检查 `brdf_model` vs `brdf_version` 一致性 | ❌ 未检查 | ✅ 新增检查 7：`brdf_model_vs_brdf_version_consistency` |
| 非法组合检出能力 | ❌ 无法检出 B0+GGX 误标 | ✅ 可检出并返回 FAIL |
| Consistency report 状态 | PASS（false PASS） | PASS（真实 PASS） |

---

## 7. 边界遵守确认

### 7.1 已遵守的边界（R29 §5.2）

- ✅ 未进入全量 2664 姿态生成
- ✅ 未重渲染全量 EXR
- ✅ 未训练模型
- ✅ 未改写论文正文
- ✅ 未修改冻结文件 13/14/24/25
- ✅ 未写入 `04_Codex审阅/`
- ✅ 未生成 Codex 裁决文件

### 7.2 允许的操作（已执行）

- ✅ 修改 `06_v0.4_code/06_manifest/` 下三个工具脚本
- ✅ 重生成 `phase0_step7a_manifest_trial/` 下三个 JSON 产物
- ✅ 写入 `02_Claude输出/31_1C-E13-FIX01_BRDF模型字段一致性修复_Claude执行报告.md`

---

## 8. 产物路径

### 8.1 修复后的工具脚本

```text
06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py         （已修复）
06_v0.4_code/06_manifest/build_image_manifest_v0_4.py       （已修复）
06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py （已修复）
```

### 8.2 重生成的产物

```text
v0.4_results/00_validation/phase0_step7a_manifest_trial/ocs_manifest_v0_4_step6trial.json
v0.4_results/00_validation/phase0_step7a_manifest_trial/image_manifest_v0_4_step6trial.json
v0.4_results/00_validation/phase0_step7a_manifest_trial/consistency_check_report.json
```

### 8.3 本执行报告

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/31_1C-E13-FIX01_BRDF模型字段一致性修复_Claude执行报告.md
```

---

## 9. 技术细节

### 9.1 BRDF 模型推断规则

当前实现的推断规则：

```python
if "B0" in brdf_version or "phong" in brdf_version or "provisional" in brdf_version:
    brdf_model = "phong_like_provisional_baseline"
elif "GGX" in brdf_version or "ggx" in brdf_version:
    brdf_model = "ggx_cook_torrance"
else:
    brdf_model = "unknown"
```

**设计考虑**：
- 使用关键词匹配而非精确字符串匹配，适应版本号变化（如 `v0.4_B0_...` → `v1.0_B0_...`）
- 优先匹配 B0/phong/provisional（当前 Phase 0 阶段）
- 次级匹配 GGX（后续全量生成阶段）
- 未匹配到任何关键词时返回 `"unknown"` 并打印警告

**后续改进建议**：
- 全量生成前，明确定义 `brdf_version` 命名规范
- 考虑在 14 号规范中新增 BRDF 模型命名约定
- 如果 BRDF 分支增加（如 LegacyPhong），扩展推断规则

### 9.2 Consistency Checker 检查顺序

当前检查顺序（11 项）：

```text
1. geometry_version_match
2. brdf_version_match
3. visibility_version_match
4. sun_visibility_match
5. shadow_mapping_method_match
6. brdf_model_match                         （新增）
7. brdf_model_vs_brdf_version_consistency   （新增）
8. v_sun_macro_mode_consistency
9. i_scale_match
10. record_id_set_match
11. per_record_consistency
```

**检查逻辑分层**：
- 1-5：版本字段直接匹配
- 6-7：BRDF 模型一致性（跨 manifest + 内部一致性）
- 8：V_sun_macro 模式与 sun_visibility 对应
- 9：预处理参数匹配
- 10-11：record 级别完整性

---

## 10. R29 阻断项解决确认

### 10.1 R29-B1 解决确认

**原阻断**：OCS manifest 的 BRDF 元数据自相矛盾（`brdf_version = B0` 但 `brdf_model = ggx_cook_torrance`）

**解决方案**：
- 修复 OCS manifest builder：从 `brdf_version` 动态推断 `brdf_model`
- 当前 B0 small-run → `brdf_model = "phong_like_provisional_baseline"`
- 消除硬编码 `"ggx_cook_torrance"` 导致的误标

**验证**：
- OCS manifest：`brdf_version = "v0.4_B0_phong_like_provisional"` + `brdf_model = "phong_like_provisional_baseline"`
- 两字段语义一致，不再自相矛盾

**状态**：✅ 已解决

### 10.2 R29-B2 解决确认

**原阻断**：consistency checker 未检查 `brdf_model`，导致 false PASS

**解决方案**：
- 新增检查 6：`brdf_model_match`（验证 OCS/Image manifest 的 `brdf_model` 一致）
- 新增检查 7：`brdf_model_vs_brdf_version_consistency`（验证 `brdf_model` 与 `brdf_version` 内部一致性）
- 核心规则：B0/phong/provisional version 不能与 ggx_cook_torrance model 同时 PASS

**验证**：
- 当前产物：11/11 检查项全部 PASS
- 反向验证：如果恢复非法组合（B0 + GGX），检查 7 会返回 FAIL
- Checker 现在可以承担全量生成前的守门功能

**状态**：✅ 已解决

---

## 11. 后续建议

### 11.1 全量生成前检查

在进入全量 2664 姿态生成前，建议：
1. 确认 BRDF 分支选择（B0 smoke test 还是正式 GGX）
2. 更新 `brdf_version` 为正式版本号（如 `v0.4_GGX_1.0`）
3. 验证 manifest builder 的 BRDF 模型推断逻辑在新版本号下仍然正确
4. 重跑 consistency checker 确认全量 manifest 通过所有检查

### 11.2 BRDF 模型命名规范

建议在 14 号规范中新增 BRDF 模型命名约定：
- `phong_like_provisional_baseline`：Phase 0 B0 工程 baseline
- `ggx_cook_torrance`：正式 GGX/Cook-Torrance 主模型
- `legacy_phong`：旧 LegacyPhong 模型（如果保留）

### 11.3 Checker 扩展方向

当前 checker 已覆盖：
- 版本字段一致性（geometry/brdf/visibility）
- BRDF 模型一致性（跨 manifest + 内部一致性）
- Sun visibility 模式一致性
- 预处理参数一致性
- Record 级别完整性

后续可扩展：
- 矩阵字段完整性检查（`camera_matrix_world` / `sun_camera_matrix_world`）
- 路径存在性检查（EXR/PNG 文件是否真实存在）
- 数值范围检查（像素统计、OCS 总量是否合理）

---

## 12. 总结

**FIX01 任务完成**：
- 修复了 R29-B1：OCS manifest BRDF 元数据自相矛盾
- 修复了 R29-B2：consistency checker 漏检 `brdf_model`
- 新增 2 项 BRDF 一致性检查，检查项从 9 项增加到 11 项
- 重生成 manifest 产物，一致性检查全部 PASS
- 未越界，符合 R29 边界要求

**修复验证**：
- OCS manifest：`brdf_model = "phong_like_provisional_baseline"`（修复前为 `"ggx_cook_torrance"`）
- Image manifest：新增 `brdf_model = "phong_like_provisional_baseline"`
- Consistency checker：可检出 B0/phong/provisional + ggx_cook_torrance 非法组合
- 一致性报告：11/11 PASS（包含新增的 2 项 BRDF 检查）

**下一步**：
- 等待 Codex 复核 FIX01（R30 或后续审阅）
- 如果通过，放行 Step 7a，进入全量生成准备
- 如果需要，执行 Step 7b 补充矩阵与路径字段

---

**执行状态**：COMPLETE  
**一致性检查**：PASS（11/11，新增 2 项 BRDF 检查）  
**R29 阻断项**：全部解决  
**边界遵守**：全部遵守

# R29 Codex 审阅：1C-E13 Phase 0 Step 7a Manifest Builder

最后更新：2026-06-24  
审阅端：Codex  
审阅对象：`30_1C-E13_Phase0_Step7a_Manifest_Builder_验证通过_Claude执行报告.md`  
Manifest 产物：`v0.4_results/00_validation/phase0_step7a_manifest_trial/`

---

## 1. 阶段结论

```text
1C-E13 / Phase 0 Step 7a：NOT PASS
Phase 0 Step 7a：暂不放行
下一步：执行 1C-E13-FIX01
```

本轮已经确认 manifest builder、image manifest builder、consistency checker 的基本框架存在，且产物目录、两个 manifest JSON、consistency report 均已生成。但本轮发现 OCS manifest 内部 BRDF 元数据存在自相矛盾，并且 consistency checker 未能检出该矛盾。因此 Step 7a 不能作为全量生成前的可信入口放行。

本次不要求重渲染、不要求进入全量 2664 姿态生成、不要求训练、不要求修改论文正文。

---

## 2. 已确认通过项

### 2.1 产物位置

已确认以下产物存在：

```text
06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
06_v0.4_code/06_manifest/build_image_manifest_v0_4.py
06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py

v0.4_results/00_validation/phase0_step7a_manifest_trial/ocs_manifest_v0_4_step6trial.json
v0.4_results/00_validation/phase0_step7a_manifest_trial/image_manifest_v0_4_step6trial.json
v0.4_results/00_validation/phase0_step7a_manifest_trial/consistency_check_report.json
```

### 2.2 基础一致性检查

`consistency_check_report.json` 当前给出：

```text
overall_status = PASS
checks = 9 项
```

其中 geometry_version、brdf_version、visibility_version、sun_visibility、shadow_mapping_method、v_sun_macro_mode、I_scale、record_id 集合、per-record yaw/pitch/geom_id 均被 checker 标为 PASS。

### 2.3 路径完整性

独立抽查未发现 manifest 中已给出的文件路径缺失。当前阻断点不是文件缺失，而是 BRDF 元数据语义不一致与 checker 漏检。

---

## 3. 阻断项

### R29-B1：OCS manifest 的 BRDF 元数据自相矛盾

`ocs_manifest_v0_4_step6trial.json` 顶层字段同时写入：

```text
brdf_version = v0.4_B0_phong_like_provisional
brdf_model   = ggx_cook_torrance
```

这两个字段在当前 Step 6 / Step 7a 语境下不能同时成立。

理由：

- R27 已放行的是 Phase 0 Step 6 的 B0 BRDF/OCS/image small-run。
- B0 在当前路线中被明确限定为工程 smoke test / provisional baseline。
- Step 5 和 Step 6 报告均未声称已进入正式 GGX 链路。
- 因此，Step 7a 的 trial manifest 不应把 B0 small-run 的 OCS manifest 标记为 `ggx_cook_torrance`。

源码证据：

```text
06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
line 155: "brdf_model": "ggx_cook_torrance",
```

该硬编码会使后续全量 manifest 在分支身份上产生误导：从 `brdf_version` 看是 B0，从 `brdf_model` 看却是 GGX。全量前 manifest 的核心价值正是防止 geometry / BRDF / visibility / image 分支混用，因此这是阻断项。

### R29-B2：consistency checker 未检查 `brdf_model`，导致 false PASS

当前 consistency checker 只检查了：

```text
brdf_version_match
```

但没有检查：

```text
brdf_model 是否存在
brdf_model 是否与 brdf_version 的分支身份一致
OCS manifest 与 Image manifest 的 brdf_model 是否一致
```

因此，在 OCS manifest 已经出现 `B0 version + GGX model` 内部矛盾时，`consistency_check_report.json` 仍然输出 `overall_status = PASS`。

这说明 checker 还不能承担全量生成前的守门功能，必须修复后重跑。

---

## 4. 非阻断但需保留的问题

以下字段当前为 `null` 或未完全展开：

```text
camera_matrix_world
sun_camera_matrix_world
position_exr_path
sun_visibility_mask_path
n_pixels_per_part
```

R28 对 Step 7a 的最低验收重点是 manifest builder 与 consistency checker 在 Step 6 五姿态 trial 上可运行，并未强制要求上述字段全部补齐。因此本轮暂不把这些字段列为阻断项。

但进入正式全量前，至少需要明确：

- 这些字段是 Step 7b 补齐，还是在全量渲染脚本中同步输出；
- checker 对这些字段采用 `required`、`optional` 还是 `phase0_optional`；
- 不允许在正式全量 corpus manifest 中长期保留会影响复现实验的关键矩阵字段为空。

---

## 5. 返工要求：1C-E13-FIX01

Claude 下一轮执行 1C-E13-FIX01，仅修复 manifest 元数据一致性与 checker 漏检，不进入全量生成。

### 5.1 必修项

1. 修复 OCS manifest builder 中的 BRDF 模型字段

当前：

```text
brdf_version = v0.4_B0_phong_like_provisional
brdf_model   = ggx_cook_torrance
```

修复后应表达当前 trial 的真实分支身份。建议最小修复为：

```text
brdf_version = v0.4_B0_phong_like_provisional
brdf_model   = phong_like_provisional_baseline
```

如 Claude 判断字段命名需更贴合已有代码，可提出等价命名，但不得继续使用 `ggx_cook_torrance` 标记 B0 small-run。

2. 补充 Image manifest 的 BRDF 模型字段

为便于 OCS/Image manifest 交叉检查，建议在 image manifest 顶层加入同源字段：

```text
brdf_model = phong_like_provisional_baseline
```

若选择不加入该字段，必须在 FIX01 报告中说明 checker 如何可靠判定 Image manifest 的 BRDF 模型身份。但 Codex 建议加入，保持双 manifest 对称。

3. 修复 consistency checker

checker 至少需要新增以下检查：

```text
brdf_model_match
brdf_model_vs_brdf_version_consistency
```

其中 `brdf_model_vs_brdf_version_consistency` 必须能检出以下非法组合：

```text
brdf_version contains B0/phong/provisional
brdf_model == ggx_cook_torrance
```

4. 重生成 Step 7a trial 产物

重生成：

```text
v0.4_results/00_validation/phase0_step7a_manifest_trial/ocs_manifest_v0_4_step6trial.json
v0.4_results/00_validation/phase0_step7a_manifest_trial/image_manifest_v0_4_step6trial.json
v0.4_results/00_validation/phase0_step7a_manifest_trial/consistency_check_report.json
```

5. 写入 Claude FIX01 执行报告

报告路径：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/31_1C-E13-FIX01_BRDF模型字段一致性修复_Claude执行报告.md
```

### 5.2 边界

本次 FIX01 禁止：

```text
禁止进入全量 2664 姿态生成
禁止重渲染全量 EXR
禁止训练模型
禁止修改论文正文
禁止修改冻结文件 13/14/24/25
禁止写入 04_Codex审阅/
禁止生成 Codex 裁决文件
```

允许：

```text
修改 06_v0.4_code/06_manifest/ 下相关 manifest builder/checker
重生成 phase0_step7a_manifest_trial 下的三个 JSON 产物
写入 02_Claude输出/31_..._Claude执行报告.md
```

---

## 6. 给 Claude 的短提示词

```text
执行 1C-E13-FIX01：修复 Step 7a manifest 的 BRDF 模型字段一致性问题。

依据文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R29_Codex_审阅_1C-E13_Step7a_manifest元数据不一致返工单.md

任务：
1. 修复 build_ocs_manifest_v0_4.py 中 B0 small-run 被写成 ggx_cook_torrance 的问题。
2. 建议将 OCS/Image manifest 顶层 brdf_model 统一为当前 B0 trial 的真实身份，例如 phong_like_provisional_baseline。
3. 修复 check_manifest_consistency_v0_4.py，新增 brdf_model_match 和 brdf_model_vs_brdf_version_consistency 检查，确保 B0/phong/provisional version 不能与 ggx_cook_torrance model 同时 PASS。
4. 重生成 phase0_step7a_manifest_trial 下两个 manifest JSON 和 consistency_check_report.json。
5. 写入执行报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/31_1C-E13-FIX01_BRDF模型字段一致性修复_Claude执行报告.md

边界：
只修 manifest builder/checker 与 Step 7a trial JSON；不得进入全量 2664 生成；不得训练；不得重渲染全量 EXR；不得修改论文正文或冻结文件；不得写入 04_Codex审阅/；不得生成 Codex 裁决文件。

若输出过长或文件无法一次写完，按 Part 1/2/3 分段完成，直到报告完整。
```

---

## 7. Codex 暂定下一步

Claude 完成 1C-E13-FIX01 后，作者将 `31_1C-E13-FIX01_BRDF模型字段一致性修复_Claude执行报告.md` 与更新后的 manifest 产物路径交回 Codex。Codex 将复核：

```text
1. OCS/Image manifest 的 brdf_version 与 brdf_model 是否一致
2. checker 是否能覆盖 B0-vs-GGX 误标
3. consistency_check_report 是否在新增检查后 PASS
4. 是否仍遵守未进入全量生成的边界
```

通过后再考虑放行 Step 7a，并规划 Step 7b 或全量前最后入口检查。

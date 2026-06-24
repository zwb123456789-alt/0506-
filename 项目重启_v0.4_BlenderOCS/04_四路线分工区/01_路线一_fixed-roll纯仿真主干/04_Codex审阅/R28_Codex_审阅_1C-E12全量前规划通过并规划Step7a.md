# R28 Codex 审阅：1C-E12 全量前规划通过并规划 Step 7a

最后更新：2026-06-24  
审阅端：Codex  
审阅对象：Claude 提交的 `29_1C-E12_Phase0_Step7_全量前规划与风险清单_Claude执行报告.md`

## 1. 审阅结论

```text
1C-E12：PASS
Phase 0 Step 7 规划：ACCEPTED
下一步：1C-E13 / Phase 0 Step 7a manifest builder + consistency checker
不得进入全量 2664 姿态生成
```

E12 报告完成了全量前规划与风险清单：列出了数据生成缺口、工具链缺口、BRDF 分支缺口、multi-geom 缺口、训练链缺口，并明确指出 manifest builder / consistency checker 必须在全量生成前先用 Step 6 的 5 姿态产物验证。该判断符合 14 号 manifest/source_data 规范的可追踪性要求。

## 2. 核验证据

### 2.1 Claude 报告路径

标准目录中已存在：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/29_1C-E12_Phase0_Step7_全量前规划与风险清单_Claude执行报告.md
```

### 2.2 未发现实质越界

本轮核验发现存在空目录：

```text
v0.4_results/00_validation/phase0_step7a_manifest_trial/
```

但未发现该目录下已有 manifest 产物，也未发现 `06_v0.4_code/06_manifest/` 中新增 Step 7a 工具脚本。因此本轮不判定为实质越界；后续 E13 可复用或覆盖该空目录。

### 2.3 E12 内容覆盖度

E12 已覆盖 Codex 要求的关键项：

- 全量前缺口清单。
- Step 7 候选任务拆分。
- manifest builder / consistency checker 必须先做的判断。
- corpus-level `I_scale` 计算流程。
- B0/B1/GGX 分支顺序建议。
- 全量生成资源与失败恢复策略。
- 不进入全量生成的边界声明。

## 3. Codex 更正与边界

### 3.1 关于“Claude 可先执行 Step 7a”

E12 报告第 9.1 节写到“在 Codex 审阅本报告前，Claude 可先执行 Step 7a”。该表述不符合当前闭环规则。正确边界是：

```text
Claude 必须等待 Codex 审阅 E12 并给出下一步提示词后，才能执行 Step 7a。
```

本 R28 即为该审阅与放行文件。因此从 R28 起，允许进入 Step 7a。

### 3.2 关于全量生成

E12 通过不等于全量生成放行。全量 2664 姿态仍需至少满足：

- Step 7a manifest builder / consistency checker 在 5 姿态上通过 Codex 审阅。
- 全量资源、目录、断点续传与失败恢复策略经 Codex/作者确认。
- 作者明确放行。

## 4. 下一步：1C-E13 / Phase 0 Step 7a

下一步任务定位：

```text
使用 Step 6 的 5 姿态 small-run 产物，实现并验证 OCS manifest builder、image manifest builder 和 consistency checker。
```

该任务仍属于 Phase 0 小规模工具链验证，不进入全量数据生成。

## 5. 给 Claude 的下一步短提示词

```text
你是 Claude 执行端，只执行，不做 Codex 审阅或阶段裁决。

任务：执行 1C-E13 / Phase 0 Step 7a，在 Step 6 的 5 姿态 small-run 产物上实现并验证 manifest builder + consistency checker。不得进入全量 2664 姿态生成。

必须读取：
1. CLAUDE.md 的 1.1 执行环境与命令规则
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R28_Codex_审阅_1C-E12全量前规划通过并规划Step7a.md
3. 04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/14_v0.4数据与manifest字段规范_最终冻结版.md 的 manifest 字段和一致性检查章节
4. 04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/13_v0.4前向模型冻结规范_最终冻结版.md 的 visibility / BRDF / image response 相关章节
5. v0.4_results/00_validation/phase0_step6_small_trial/phase0_step6_small_trial_summary.json
6. 06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py

必须实现：
1. OCS manifest builder：
   06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
2. Image manifest builder：
   06_v0.4_code/06_manifest/build_image_manifest_v0_4.py
3. Consistency checker：
   06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py

输入：
- Step 6 的 5 个 OCS JSON
- Step 6 的 5 个 linear EXR + PNG
- Step 6 summary 中的 r_max、ortho_scale_m、pixel_area_m2、i_scale_smallrun、depth_epsilon_m_final

输出目录：
v0.4_results/00_validation/phase0_step7a_manifest_trial/

必须输出：
1. ocs_manifest_v0_4_step6trial.json
2. image_manifest_v0_4_step6trial.json
3. consistency_check_report.json
4. 一份 Claude 执行报告，写入：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/

最低验收标准：
- 两个 manifest 均包含 5 条 records。
- record_id 在 OCS/image 两侧完全一致。
- 两个 manifest 顶层版本字段、geometry_version、brdf_version、visibility_version、sun_visibility、shadow_mapping_method、v_sun_macro_mode 等一致性字段完整。
- consistency checker 至少检查：
  geometry_version 一致；
  brdf_version 一致；
  visibility_version 一致；
  sun_visibility 一致；
  shadow_mapping_method 一致；
  v_sun_macro_mode 与 sun_visibility 对应；
  preprocessing.I_scale 与 Step 6 summary 一致；
  record_id 集合一致；
  每个 record 的 yaw/pitch/geom_id 一致。
- 检查结果必须 PASS；若字段缺失或无法确认，写 NOT_COMPLETE。

禁止：
- 不得进入全量 2664 姿态生成。
- 不得重渲染 EXR。
- 不得训练模型。
- 不得改写论文正文。
- 不得修改 CLAUDE.md、13/14/24/25、路线冻结文件或书籍知识库。
- 不得写入 04_Codex审阅/。
- 不得生成 Codex、验收、最终放行等名义文件。
```

## 6. 本轮分流

Codex 审阅记录：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R28_Codex_审阅_1C-E12全量前规划通过并规划Step7a.md
```

本轮不更新 `CLAUDE.md`，因为当前阶段状态仍是“Step 6 已通过，下一步执行 Step 7a”，该信息已在 R27 中同步；R28 作为 Step 7a 的具体执行裁决。


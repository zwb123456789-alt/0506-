# R35 Codex 审阅：1C-E16 通过但暂不放行全量

最后更新：2026-06-24  
审阅端：Codex  
审阅对象：`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/36_1C-E16_全量前最终放行准备_Claude执行报告.md`  
关联依据：`R34_Codex_审阅_1C-E15-FIX02通过并完成Step7c.md`

---

## 1. 阶段判定

```text
1C-E16：PASS
Phase 0 Step 7c：COMPLETE（沿用 R34）
全量 2664 姿态生成：NOT RELEASED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：1C-E17，全量 driver 脚本补齐与 launch smoke check
```

E16 完成了 R34 要求的两项全量前小修、Step7c checker 复跑、full-run 输出目录建议、门禁参数和失败恢复策略说明。  
但本轮仍不能正式放行全量 2664 姿态生成，因为 E16 报告给出的正式 full-run 命令依赖尚不存在的可执行 driver 脚本。

---

## 2. 已通过项

### 2.1 BRDF 分支判断小修

已确认以下两个 builder 的 BRDF 判断顺序已调整为：

```text
B1 / improved_phong -> improved_phong_book_model_pending_author_confirmation
GGX / ggx           -> ggx_cook_torrance
B0 / phong / provisional -> phong_like_provisional_baseline
```

涉及文件：

```text
06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
06_v0.4_code/06_manifest/build_image_manifest_v0_4.py
```

说明：当前 builder 的 `brdf_version` 仍固定拼接 `_phong_like_provisional`，因此本轮只认可其对 **B0 full-run** 的放行准备；B1/GGX 正式分支仍需后续独立参数化和审阅，不随本轮放行。

### 2.2 Checker task 标签中性化

已确认 `check_manifest_consistency_v0_4.py` 的 report task 已改为：

```text
v0.4 manifest consistency check (17 checks)
```

不再固定写 `1C-E15-FIX01`。

### 2.3 Step7c dry-run 复跑

Codex 复跑 Step7c checker：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results\00_validation\phase0_step7c_dryrun_fix02\ocs_manifest_v0_4_step7c_dryrun.json `
  --image-manifest v0.4_results\00_validation\phase0_step7c_dryrun_fix02\image_manifest_v0_4_step7c_dryrun.json `
  --step6-summary v0.4_results\00_validation\phase0_step6_small_trial\phase0_step6_small_trial_summary.json `
  --data-root . `
  --require-prefix v0.4_results/ `
  --expected-record-count 3 `
  --output v0.4_results\00_validation\phase0_step7c_dryrun_fix02\codex_rerun_after_e16_consistency_check_report.json
```

结果：

```text
overall_status = PASS
check_count = 17
checks 1-17 = PASS
records_completeness = PASS, expected = 3, OCS = 3, Image = 3
```

---

## 3. 阻断项

### 3.1 R35-B1：E16 full-run 命令引用的 driver 脚本尚不存在

E16 报告建议的正式 full-run 命令包含：

```text
06_v0.4_code/02_blender/render_full_2664_shadow.py
06_v0.4_code/05_postprocess/run_phase1_fullrun.py
```

Codex 本地检查结果：

```text
06_v0.4_code/02_blender/render_full_2664_shadow.py exists=False
06_v0.4_code/05_postprocess/run_phase1_fullrun.py exists=False
```

因此当前还没有可直接执行的全量渲染脚本和全量后处理脚本。若此时放行“启动全量 2664”，Claude 仍需临场编写核心 driver，这会绕过阶段门审阅。

裁决：

```text
全量 2664 生成不得启动。
必须先补齐并审阅 full-run driver 脚本。
```

### 3.2 R35-B2：Checkpoint / 失败恢复仍是策略说明，不是已实现门禁

E16 给出的 checkpoint 策略是合理的最小设计：

```text
record-level status = COMPLETE / MISSING / FAILED
fullrun_summary.json 作为 checkpoint
重跑跳过已完成 record
checker --expected-record-count 2664 作为最终门禁
```

但目前尚未在 full-run driver 中实现，因为 full-run driver 脚本本身尚不存在。  
因此该策略不能被视为“已可执行的恢复机制”。

### 3.3 R35-B3：CLAUDE.md 当前状态仍停留在 Step7b

当前 `CLAUDE.md` 的下一步仍写为：

```text
执行 1C-E14：Phase 0 Step 7b / 全量前入口检查与 manifest 字段补齐规划
```

这不影响本轮 R35 审阅文件本身，但在后续全量真正放行前，必须受控同步到最新阶段状态。由于本轮未正式放行全量，暂不由 Codex 自动改写 `CLAUDE.md`。

---

## 4. 本轮裁决表

| 审阅项 | 裁决 |
|---|---|
| BRDF 分支判断顺序小修 | PASS |
| Checker task 标签中性化 | PASS |
| Step7c dry-run checker 复跑 | PASS |
| Full-run 输出目录建议 | PASS |
| expected-record-count = 2664 门禁说明 | PASS |
| checkpoint / 失败恢复策略说明 | 方向通过，但未实现 |
| full-run shadow driver 是否存在 | FAIL |
| full-run postprocess driver 是否存在 | FAIL |
| 是否正式放行全量 2664 | NO |

---

## 5. 给 Claude 的下一步短提示词

```text
执行 1C-E17：全量 2664 driver 脚本补齐与 launch smoke check。

依据文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R35_Codex_审阅_1C-E16通过但暂不放行全量.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/36_1C-E16_全量前最终放行准备_Claude执行报告.md
06_v0.4_code/02_blender/render_20_attitudes_shadow.py
06_v0.4_code/05_postprocess/run_phase0_step7c_dryrun.py
06_v0.4_code/01_geometry/attitude_grid.py
06_v0.4_code/06_manifest/

任务：
1. 不启动全量 2664 渲染，只补齐全量 driver 脚本和 launch smoke check。
2. 新增或改造：
   - 06_v0.4_code/02_blender/render_full_2664_shadow.py
   - 06_v0.4_code/05_postprocess/run_phase1_fullrun.py
3. 两个脚本必须支持 dry-run / limit 参数，例如：
   - --limit 3 或 --attitudes <labels>
   - --skip-existing
   - --output-dir
   - --summary-path
4. full-run shadow driver 必须：
   - 使用 attitude_grid.py 的 72×37 = 2664 姿态网格；
   - 输出 camera.exr + sun.exr；
   - 写 render_metadata.json；
   - 记录每个 record 的 status；
   - 支持跳过已存在文件，不覆盖无关产物。
5. full-run postprocess driver 必须：
   - 读取 shadow_passes；
   - 输出 linear EXR、log1p PNG、OCS JSON、V_sun_macro PNG/NPY；
   - 写 fullrun_summary.json；
   - 支持 COMPLETE / MISSING / FAILED status；
   - 支持按 status 续跑。
6. 用 --limit 3 或指定 3 个姿态做 launch smoke check，输出到：
   v0.4_results/00_validation/phase0_fullrun_driver_smoke/
7. 对 smoke 产物构建 OCS/Image manifest，并运行 17 项 checker：
   --data-root .
   --require-prefix v0.4_results/
   --expected-record-count 3
8. 输出报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/37_1C-E17_fullrun_driver脚本与smoke_Claude执行报告.md
9. 报告必须明确：
   - 未启动全量 2664；
   - smoke 只验证 driver 可启动、status/checkpoint/checker 链路；
   - 若 smoke 通过，交回 Codex 做 R36 是否放行全量。

边界：
不得启动全量 2664 姿态生成；不得训练；不得修改论文正文；不得修改冻结文件 13/14/24/25；不得写入 04_Codex审阅/；不得生成 Codex 裁决文件。
若输出过长或文件无法一次写完，按 Part 1/2/3 分段完成，直到报告完整。
```

---

## 6. Codex 暂定下一步

Claude 完成 E17 后，作者将以下文件交回 Codex：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/37_1C-E17_fullrun_driver脚本与smoke_Claude执行报告.md
v0.4_results/00_validation/phase0_fullrun_driver_smoke/consistency_check_report.json
```

Codex 下一轮判断：

```text
1. full-run shadow driver 是否存在并支持 limit / skip-existing / status；
2. full-run postprocess driver 是否存在并支持 checkpoint / status；
3. launch smoke 是否通过 17 项 checker；
4. 是否可以正式放行 B0 full-run G0 2664 姿态生成；
5. 是否需要同步更新 CLAUDE.md。
```

在 R36 明确放行前，仍不得启动全量 2664、训练或论文正文改写。

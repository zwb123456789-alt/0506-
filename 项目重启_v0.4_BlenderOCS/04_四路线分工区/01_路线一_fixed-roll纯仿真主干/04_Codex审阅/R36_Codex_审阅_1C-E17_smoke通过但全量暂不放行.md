# R36 Codex 审阅：1C-E17 full-run driver 与 smoke

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/37_1C-E17_fullrun_driver脚本与smoke_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E17 smoke：PASS
full-run driver 基础能力：PARTIAL PASS
全量 2664 姿态生成：NOT RELEASED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：1C-E17-FIX01，补齐全量启动保护后再做 R37 放行裁决
```

结论：E17 的 3 姿态端到端 smoke 成立，Blender render -> postprocess -> manifest -> checker 链路已跑通；但当前 Blender 全量 driver 还没有真正的断点续跑/跳过已存在文件能力，也没有可审计的分批入口。对 2664 姿态正式启动而言，这是硬风险，因此本轮不放行全量。

---

## 1. 本轮核验证据

### 1.1 文件存在性

Codex 检查结果：

```text
06_v0.4_code/02_blender/render_full_2664_shadow.py      exists = True
06_v0.4_code/05_postprocess/run_phase1_fullrun.py       exists = False
06_v0.4_code/05_postprocess/run_full_postprocess.py     exists = True
```

说明：R35 原建议入口名为 `run_phase1_fullrun.py`，E17 实际交付为 `run_full_postprocess.py`。本轮 smoke 按实际入口通过，因此不因命名差异否定 smoke；但后续文档、命令与 CLAUDE 状态必须统一到一个正式入口名，不能同时存在两个说法。

### 1.2 Blender smoke 元数据

文件：`v0.4_results/01_fullrun/shadow_passes/render_metadata.json`

Codex 读取到：

```text
total_grid_size = 2664
rendered_count  = 3
resolution      = 256
samples         = 1
```

3 个 smoke 姿态均有 camera/sun EXR：

```text
yaw010_pitch+000_roll+000  camera_exists=True  sun_exists=True
yaw020_pitch+000_roll+000  camera_exists=True  sun_exists=True
yaw025_pitch+015_roll+000  camera_exists=True  sun_exists=True
```

### 1.3 Postprocess smoke summary

文件：`v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json`

Codex 读取到：

```text
overall_status = COMPLETE
n_total_labels = 3
n_completed    = 3
brdf_branch    = B0
geom_id        = phase63
```

3 条记录均为 `COMPLETE`，且均包含 `sun_visibility_mask_path`。

### 1.4 Checker 复跑

Codex 使用项目指定 Python 环境复跑：

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_smoke.json `
  --image-manifest v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_smoke.json `
  --step6-summary v0.4_results/00_validation/phase0_step6_small_trial/phase0_step6_small_trial_summary.json `
  --data-root . `
  --require-prefix v0.4_results/ `
  --expected-record-count 3 `
  --output v0.4_results/01_fullrun/postprocess/consistency_check_report_smoke_codex_rerun.json
```

结果：

```text
overall_status = PASS
check_count    = 17
records_completeness = PASS, OCS=3, Image=3, expected=3
path_base_consistency = PASS, 0 inconsistencies
ocs_paths_exist = PASS, 0 missing
image_paths_exist = PASS, 0 missing
camera_matrix_non_null_and_valid = PASS, 0 invalid
sun_visibility_mask_path_non_null_and_exists = PASS, 0 missing
```

因此，E17 smoke 不是纸面通过，是真实链路通过。

---

## 2. 阻断全量放行的问题

### P0-1：Blender driver 缺少真正的 skip-existing / resume

`render_full_2664_shadow.py` 当前 CLI 只解析：

```text
--smoke
--labels
```

主循环对 `selected` 中每个姿态直接执行 camera 与 sun render。没有在渲染前检查 `{label}_camera.exr` 和 `{label}_sun.exr` 是否已经存在，也没有 `--skip-existing` / `--force` 语义。

风险：

- 2664 姿态全量渲染一旦中断，重启会从头重渲染已完成姿态；
- smoke 产物已写入 `v0.4_results/01_fullrun/`，正式全量启动可能无提示覆盖已有产物；
- 后续无法用 metadata 明确区分本次新渲染、跳过既有文件、缺失或失败项；
- E16 中要求的 record-level checkpoint/恢复策略在 Blender 阶段尚未闭合。

裁决：这是全量启动前必须修复的 P0。

### P0-2：缺少可审计分批入口

报告建议“先 200 姿态 pilot，再 8-10 批完成全量”，但当前 Blender driver 只有：

```text
--smoke N        取全量列表前 N 个
--labels A,B,C   手动指定姿态
无参             全量 2664
```

它还没有 `--start-index/--count`、`--batch-index/--batch-size` 或等价的可审计分批参数。`--labels` 可以临时手动分批，但不适合 2664 正式生产链路，容易漏跑、重跑或顺序不可复核。

裁决：全量放行前必须补齐至少一种稳定分批方式，并写入 metadata。

### P1-1：正式后处理入口名需要统一

R35 规划文件中预期为：

```text
06_v0.4_code/05_postprocess/run_phase1_fullrun.py
```

E17 实际交付为：

```text
06_v0.4_code/05_postprocess/run_full_postprocess.py
```

当前不阻断 smoke；但在全量启动命令、报告、CLAUDE 状态和后续 R37 裁决里必须统一。可以选择保留 `run_full_postprocess.py`，也可以补一个 `run_phase1_fullrun.py` wrapper；但不要继续出现两个正式入口名。

---

## 3. 对 E17 的通过范围

本轮确认通过：

- `render_full_2664_shadow.py` 能生成 2664 姿态网格，并能按 `--labels` 渲染 3 个指定姿态；
- 3 姿态 camera/sun EXR 均真实存在；
- `run_full_postprocess.py` 能对指定姿态完成 BRDF、V_sun_macro mask、OCS 和 image outputs；
- manifest builder 能基于本轮产物生成 OCS/Image manifest；
- checker 17/17 PASS，且 Codex 复跑通过；
- 未启动全量 2664；
- 未训练；
- 未改论文正文；
- 未写入 `04_Codex审阅/`。

本轮未确认通过：

- Blender 阶段断点续跑；
- Blender 阶段跳过已存在产物；
- 全量分批执行；
- 2664 全量 manifest completeness；
- 2664 全量 checker；
- 全量完成后的训练入口。

---

## 4. 1C-E17-FIX01 要求

Claude 下一轮只做 driver 修复与小规模验证，仍不得启动全量 2664。

### 4.1 必修：Blender driver 启动保护

修改：

```text
06_v0.4_code/02_blender/render_full_2664_shadow.py
```

必须补齐：

1. `--skip-existing` 与 `--force` 语义  
   默认建议为跳过既有完整 pair：当 `{label}_camera.exr` 和 `{label}_sun.exr` 均存在时跳过；若只有一侧存在，判为 `PARTIAL_EXISTING`，除非 `--force`，否则不静默覆盖。

2. 可审计分批参数  
   至少实现一种：
   - `--start-index <int> --count <int>`
   - 或 `--batch-index <int> --batch-size <int>`
   - 或等价机制

3. metadata 中记录每个姿态的状态  
   至少区分：
   - `RENDERED`
   - `SKIPPED_EXISTING`
   - `PARTIAL_EXISTING`
   - `FAILED`

4. metadata 记录本次选择参数  
   包括 `total_grid_size`、`selected_count`、`rendered_count`、`skipped_count`、`failed_count`、`selection_mode`、分批参数、`force`/`skip_existing`。

### 4.2 必修：入口命名统一

二选一：

- 保留 `run_full_postprocess.py` 作为正式后处理入口，并在 FIX01 报告、后续命令和 CLAUDE 状态中统一使用此名；
- 或新增 `run_phase1_fullrun.py` wrapper，调用 `run_full_postprocess.py`，满足 R35 原入口名。

### 4.3 必修：小规模验证

不得启动全量。验证建议：

1. 对 E17 已存在的 3 个 smoke 姿态执行一次 Blender driver skip 测试，确认 3/3 `SKIPPED_EXISTING`，不重渲染；
2. 再选 1 个全新姿态执行分批/labels 小测，确认 `RENDERED`；
3. 对 4 个姿态跑 postprocess 与 manifest/checker；
4. checker 使用：

```text
--data-root .
--require-prefix v0.4_results/
--expected-record-count 4
```

5. 输出新的 checker report，不能覆盖本轮 Codex 复跑报告。

### 4.4 报告

写入：

```text
02_Claude输出/38_1C-E17-FIX01_fullrun_driver启动保护_Claude执行报告.md
```

报告必须列出：

- 修改文件清单；
- skip-existing / force 行为说明；
- 分批参数说明；
- metadata 新字段；
- 小规模验证姿态；
- checker 17/17 结果；
- 明确声明未启动全量 2664。

---

## 5. 当前边界

在 R37 Codex 放行前，禁止执行：

```powershell
blender --background --python 06_v0.4_code/02_blender/render_full_2664_shadow.py
```

也禁止执行任何无 `--smoke`、无 `--labels`、无分批参数限制的全量命令。

当前允许的下一步仅为：

```text
1C-E17-FIX01：full-run driver 启动保护 + 小规模验证
```

---

## 6. 给 Claude 的下一步指令摘要

```text
执行 1C-E17-FIX01。

目标：修复 full-run Blender driver 的启动保护，不启动全量。

必须完成：
1. render_full_2664_shadow.py 增加 skip-existing / force。
2. 增加可审计分批参数。
3. metadata 记录 RENDERED / SKIPPED_EXISTING / PARTIAL_EXISTING / FAILED。
4. 统一后处理入口命名。
5. 做 3 个既有姿态 skip 测试 + 1 个新姿态小规模渲染测试。
6. 对 4 姿态跑 postprocess、manifest、checker，要求 17/17 PASS。
7. 报告写入 02_Claude输出/38_1C-E17-FIX01_fullrun_driver启动保护_Claude执行报告.md。

红线：
- 不启动全量 2664。
- 不训练。
- 不改论文正文。
- 不写 04_Codex审阅/。
- 不改冻结文件 13/14/24/25。
```


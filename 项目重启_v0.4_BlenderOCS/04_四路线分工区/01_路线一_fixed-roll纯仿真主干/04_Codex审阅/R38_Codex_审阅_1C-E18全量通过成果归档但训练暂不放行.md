# R38 Codex 审阅：1C-E18 全量 2664 生成与 manifest/checker

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/39_1C-E18_全量2664生成与manifest_checker_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E18：PASS
Phase 0 B0 full-run 2664 数据生成：PASS
fullrun manifest/checker：PASS
成果归档：PASS
训练执行：NOT RELEASED
下一步：1C-E19，训练入口与数据切分方案准备，不启动训练
```

结论：路线一 C Phase 0 B0 full-run corpus 已完成。Codex 核验到 2664 camera EXR、2664 sun EXR、postprocess 2664/2664 COMPLETE、fullrun manifest 2664 records、checker 17/17 PASS；Codex 已复跑 checker 并通过。因此本轮正式接受 1C-E18 成果，并允许将其作为路线一 C Phase 0 B0 稳定数据成果归档。

但训练执行本轮暂不放行。原因不是 full-run 数据不合格，而是当前 `06_v0.4_code/` 中没有可直接审阅和放行的训练入口、数据切分脚本、训练配置、评估指标与结果落盘规范。下一步应先做训练准备任务 `1C-E19`，产出可审阅的训练入口方案和最小 smoke，不直接训练模型。

---

## 1. Codex 核验证据

### 1.1 报告与产物在位

Claude 报告已写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/39_1C-E18_全量2664生成与manifest_checker_Claude执行报告.md
```

fullrun 关键产物在位：

```text
v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json
v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json
v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json
v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun.json
```

### 1.2 Shadow pass 文件数

Codex 统计：

```text
camera EXR = 2664
sun EXR    = 2664
```

这与 72 yaw × 37 pitch = 2664 姿态网格一致。

### 1.3 Postprocess 文件数

Codex 统计：

```text
linear_exr = 2664
brdf_png   = 2664
ocs_json   = 2664
mask_png   = 2664
mask_npy   = 2664
```

每姿态 5 类后处理产物完整。

### 1.4 Fullrun summary

Codex 读取 `fullrun_postprocess_summary.json`：

```text
overall_status     = COMPLETE
n_total_labels     = 2664
n_completed        = 2664
records            = 2664
blockers           = 0
brdf_branch        = B0
geom_id            = phase63
non_complete       = 0
missing_mask_field = 0
```

### 1.5 Checker 复跑

Codex 复跑：

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json `
  --image-manifest v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json `
  --step6-summary v0.4_results/00_validation/phase0_step6_small_trial/phase0_step6_small_trial_summary.json `
  --data-root . `
  --require-prefix v0.4_results/ `
  --expected-record-count 2664 `
  --output v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun_codex_rerun.json
```

结果：

```text
overall_status = PASS
check_count    = 17
records_completeness = PASS, OCS=2664, Image=2664, expected=2664
path_base_consistency = PASS, 0 inconsistencies
ocs_paths_exist = PASS, 0 missing
image_paths_exist = PASS, 0 missing
camera_matrix_non_null_and_valid = PASS, 0 invalid
sun_visibility_mask_path_non_null_and_exists = PASS, 0 missing
```

因此，1C-E18 数据侧通过。

---

## 2. Batch 6 处置判定

Claude 报告称 Batch 6 首次出现 1 个 `PARTIAL_EXISTING`，随后按 R37 要求暂停并用 `--force` 重跑该批 200 姿态。最终：

```text
PARTIAL = 0
FAILED  = 0
camera/sun EXR 总数均为 2664
checker 17/17 PASS
```

Codex 判定：处置可接受。`--force` 用于明确异常批次修复，符合 R37 的局部修复边界。

GBK 编码问题使用 `PYTHONIOENCODING=utf-8` 绕过，未影响数据结果；但建议后续清理脚本中的 emoji 输出，避免 Windows 终端再触发编码失败。

---

## 3. 成果归档判定

本轮稳定成果包括：

```text
v0.4_results/01_fullrun/shadow_passes/
v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json
v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json
v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json
v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun.json
v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun_codex_rerun.json
```

这些文件体量较大，不复制进 `01_成果区/`。本轮采用“成果区索引 + 原位数据路径”的归档方式：在路线一 `01_成果区/` 建立 full-run 成果索引，指向原位 `v0.4_results/01_fullrun/` 数据目录和 R38 审阅文件。

成果索引文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/06_Phase0_B0_fullrun_2664成果索引_R38通过.md
```

---

## 4. 训练放行裁决

本轮不放行训练执行。

Codex 对 `06_v0.4_code/` 做了训练入口侦察，未发现可直接审阅的训练脚本、模型脚本、dataset/split 脚本或训练配置。现有代码主要覆盖 geometry、Blender render、postprocess、manifest 与 validation。

训练执行放行前至少需要：

1. 数据集定义：使用 image manifest、OCS manifest 或二者联合输入的明确方案；
2. 标签定义：姿态 label、yaw/pitch 编码方式、fixed-roll 条件说明；
3. train/val/test split：必须避免同一几何或邻近姿态泄漏的切分说明；
4. baseline 模型与指标：至少给出图像-only、OCS-only、联合输入的可比方案或阶段顺序；
5. 训练入口脚本：支持 smoke、固定随机种子、输出目录、日志、checkpoint；
6. 评估输出：误差指标、可视化、失败样本记录；
7. manifest 绑定：训练必须绑定 R38 fullrun manifest 和 checker PASS 证据。

因此，下一步放行的是训练准备，不是训练本身。

---

## 5. 下一步：1C-E19

Claude 下一轮执行：

```text
1C-E19：训练入口与数据切分方案准备
```

允许：

- 读取 R38 fullrun manifest 与 summary；
- 设计 train/val/test split；
- 生成 split manifest 或 dataset index；
- 创建训练入口脚本骨架；
- 做不训练的 loader smoke / batch shape smoke；
- 修复 Windows GBK emoji 输出问题。

禁止：

- 启动训练；
- 写论文正文；
- 启动 B1/GGX 批量扩展；
- 启动三轴小项目或路线二/三/四扩展；
- 写入 `04_Codex审阅/`；
- 自行宣布训练放行。

---

## 6. 给 Claude 的下一步指令摘要

```text
执行 1C-E19：训练入口与数据切分方案准备，不启动训练。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R38_Codex_审阅_1C-E18全量通过成果归档但训练暂不放行.md
- v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json
- v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json
- v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun_codex_rerun.json

目标：
1. 提出训练数据定义：image / OCS / joint 三类输入如何绑定 manifest。
2. 生成 train/val/test split 方案与 split manifest，要求可复现、固定 seed、记录姿态分布。
3. 创建训练入口脚本骨架和 dataset loader，但只做 loader smoke，不训练。
4. loader smoke 输出 batch shape、label shape、路径存在性、样本数统计。
5. 清理 full-run 脚本中的 emoji/GBK 风险输出，若修改代码需说明。

输出报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/40_1C-E19_训练入口与数据切分准备_Claude执行报告.md

红线：
- 不训练。
- 不改论文正文。
- 不改冻结文件 13/14/24/25。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不写 04_Codex审阅/。
```


# 34 1C-E15-FIX01 Checker 路径解析修复（Claude 执行报告）

执行时间：2026-06-24
执行端：Claude
任务：1C-E15-FIX01，修复 Step7c consistency checker 实现问题并自测，归位输出
依据文件：
- `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R32_Codex_审阅_1C-E15_Step7c未通过返工单.md`
- `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R31_Codex_审阅_1C-E14_Step7b条件通过并要求Step7c.md`
- `06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py`

---

## 0. 阶段结论（先行声明，避免过度声称）

```text
1C-E15-FIX01：checker 修复完成，自测通过「检查逻辑正确」。
Step7c 整体：仍未完成。
下一步：仍需执行 builder 路径基准统一修复 / Blender 相机矩阵输出 /
        V_sun_macro mask 输出 / 3 姿态物理 dry-run（FIX02）。
全量 2664 姿态生成：NOT RELEASED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
```

本报告**只**覆盖 R32 要求的 checker 修复部分。R32-B5 指出的 builder/matrix/mask/dry-run 本轮**未执行**，因为这些需要 Blender 环境与完整渲染链，超出 FIX01 范围。本报告不声称 Step7c 通过。

---

## 1. R32 阻断项逐项处置

| 编号 | R32 阻断项 | 本轮处置 | 状态 |
|---|---|---|---|
| R32-B1 | checker 路径解析根目录错误（从 manifest 反推根，误报真实文件 missing） | 新增 `--data-root`（默认 `.`）；所有 record 路径统一 `Path(data_root) / 规范化相对路径`；不再反推；report 记录 `data_root_resolved` | ✅ 已修 |
| R32-B2 | `path_base_consistency` 写死 `v0.4_results/` 前缀过窄 | 改为结构校验（相对/无盘符/无 `..` 越界）+ 可选 `--require-prefix`；report 注明这是 Phase0 数据布局约束而非永久 schema | ✅ 已修 |
| R32-B3 | 矩阵 4x4 检查未验证元素 float 可转性 | 对 `camera_matrix_world`/`sun_camera_matrix_world` 16 元素逐个 `float(x)` 校验；失败报告 record_id、字段名、`[行][列]`、值 | ✅ 已修 |
| R32-B4 | `records_completeness` 仅 INFO，无法作 full-run final gate | 新增 `--expected-record-count`；启用时（CLI 或 manifest `n_total_expected`）记录数不足判 `NOT_COMPLETE`；未启用保持 INFO 并注明 gate 未启用 | ✅ 已修 |
| R32-B5 | builder 修复与 dry-run 未执行 | 本轮**不做**；明确声明 Step7c 未完成，停在 checker 修复阶段 | ⏸ 留待 FIX02 |
| R32-B6 | 不得用手工构造矩阵 JSON 冒充正式 dry-run | 本轮无 dry-run；自测使用的合成 fixture 全部显式标记 `_synthetic`，仅作 checker 单元测试，绝不作物理 dry-run 通过依据 | ✅ 遵守 |

---

## 2. checker 代码修改详情

修改文件：`06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py`

### 2.1 新增辅助函数

- `_normalize_rel_path(path)`：把 Windows 反斜杠输入规范化为 POSIX `/`（R32-B1 第 3 点）。
- `_resolve_under_root(data_root, path)`：统一 `Path(data_root) / 规范化相对路径` 解析（R32-B1 第 2 点）。
- `_path_structure_issue(path, require_prefix)`：路径结构校验——拒绝盘符绝对路径、POSIX 绝对路径、含 `..` 越界段；可选要求前缀（R32-B2）。

### 2.2 函数签名与 CLI

`check_consistency(...)` 新增参数：`data_root="."`、`require_prefix=None`、`expected_record_count=None`。
`main()` 新增 CLI：`--data-root`（默认 `.`）、`--require-prefix`、`--expected-record-count`。
运行时打印并在 report 写入 `data_root`、`data_root_resolved`、`require_prefix`、`expected_record_count`、`check_count`。

### 2.3 关键检查项修改

- **检查 12 `path_base_consistency`**：由「硬编码 `v0.4_results/` 前缀」改为「结构校验 + 可选前缀」；report 内含 `note` 说明 require_prefix 为当前 Phase0 数据布局约束。
- **检查 13/14 `ocs_paths_exist` / `image_paths_exist`**：相对 `data_root` 解析；**区分两类问题**——结构/基准不一致归入 `base_inconsistent_paths`（交检查 12 拦截，不计入 missing），仅真正解析后不存在的文件计入 `missing_paths`。这是 R32-B1 误报问题的核心修复。
- **检查 15 `camera_matrix_non_null_and_valid`**：抽出 `_matrix_issues()`，在 4x4 结构通过后，对 16 个元素逐个 `float(x)` 校验，失败定位到 `[行][列]` 与原值（R32-B3）。
- **检查 16 `sun_visibility_mask_path_non_null_and_exists`**：mask 路径同样走结构校验 + `data_root` 解析；基准不一致与文件缺失分别报告。
- **检查 17 `records_completeness`**：期望数优先级 `--expected-record-count` > manifest `n_total_expected`；启用时不足判 `NOT_COMPLETE` 并拉低 overall；二者皆无时 INFO 且注明 gate 未启用（R32-B4）。

### 2.4 头部说明

文件头 docstring 已更新为完整 **17 项**检查清单，并注明 R31/R32 依据与路径解析说明，不再停留在旧 9 项。

---

## 3. 自测结果

### 3.1 主自测：当前 Step7a manifest（R32 指定命令对应）

命令（data_root=项目根，require_prefix=v0.4_results/）：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results\00_validation\phase0_step7a_manifest_trial\ocs_manifest_v0_4_step6trial.json `
  --image-manifest v0.4_results\00_validation\phase0_step7a_manifest_trial\image_manifest_v0_4_step6trial.json `
  --step6-summary v0.4_results\00_validation\phase0_step6_small_trial\phase0_step6_small_trial_summary.json `
  --data-root . --require-prefix v0.4_results/ `
  --output v0.4_results\00_validation\phase0_step7c_checker_test_fix01\consistency_check_report.json
```

结果（17 项）：

```text
checks 1-11                                   = PASS
path_base_consistency                         = FAIL，10 inconsistencies（camera_exr_path/sun_depth_exr_path 缺 v0.4_results/ 前缀，真实基准混用）
ocs_paths_exist                               = PASS，0 missing，10 base-inconsistent
image_paths_exist                             = PASS，0 missing，0 base-inconsistent
camera_matrix_non_null_and_valid              = FAIL，5 invalid（当前矩阵为 null）
sun_visibility_mask_path_non_null_and_exists  = FAIL，5 missing（当前 mask 为 null）
records_completeness                          = INFO，gate 未启用
overall_status                                = NOT_COMPLETE
```

**关键对比 R32 实测（误报修复验证）**：

| 检查项 | R32 修复前 | FIX01 修复后 |
|---|---|---|
| `ocs_paths_exist` | FAIL，**20 missing**（含误报真实存在的 EXR/PNG） | PASS，**0 missing**，10 base-inconsistent |
| `image_paths_exist` | FAIL，**10 missing**（误报） | PASS，**0 missing** |

R32 §3 列出的三个真实存在文件（`yaw180..._linear.exr`、`yaw180..._brdf.png`、`shadow_passes/yaw180..._camera.exr`）不再被误报为 missing。`camera_exr_path`/`sun_depth_exr_path` 的基准混用由 `path_base_consistency` 正确拦截，并在路径存在性检查中归入 `base_inconsistent`，不再混淆为「文件真实缺失」。

矩阵 FAIL 与 mask FAIL 符合 Step7a manifest 已知状态（矩阵/mask 当前为 null），属 builder 侧未完成，留待 FIX02。

### 3.2 正向与边界自测（合成 fixture，显式 `_synthetic` 标记）

为证明 checker **能产出 PASS** 且新 gate 逻辑正确，构造 4 个合成 manifest 单元测试。所有 fixture 顶层带 `"_synthetic": "checker unit-test fixture; NOT a physical dry-run"`，位于：

```text
v0.4_results/00_validation/phase0_step7c_checker_test_fix01/_synthetic_fixtures/
```

**声明（R32-B6）**：这些 fixture 仅用于验证 checker 检查逻辑，矩阵为人工填值，路径借用真实 step6 产物充当存在性，**不构成任何物理 dry-run 通过依据**。

| 场景 | 构造 | 期望 | 实测 |
|---|---|---|---|
| A CLEAN | 路径全 `v0.4_results/` 前缀且真实存在，矩阵填有效 4x4，mask 指向真实文件 | 17 项全 PASS，overall PASS，exit 0 | ✅ 全 PASS，overall=PASS，exit=0 |
| A2 CLEAN + gate | A + `--expected-record-count 2664` | `records_completeness` = NOT_COMPLETE（5<2664） | ✅ NOT_COMPLETE，gate_enabled=True |
| B 坏矩阵 | record0 `camera_matrix_world[1][2]="NaNstr"`；record1 `sun_camera_matrix_world[0][0]=None` | 矩阵检查 FAIL 并定位元素 | ✅ FAIL，精确报 `[1][2] not float-convertible: 'NaNstr'` 与 `[0][0] ... None` |
| C 坏路径 | record0 `exr_path="../escape/outside.exr"`；record1 `png_path="C:/abs/drive.png"` | `path_base_consistency` 捕获越界/盘符 | ✅ FAIL，2 inconsistencies；存在性检查归入 base_inconsistent 不误判 missing |

场景 A 证明：在路径合规、矩阵有效、mask 存在时，checker 全 17 项 PASS、overall PASS、退出码 0——逻辑可达正向终态。
场景 A2/B/C 证明：completeness gate、矩阵 float 校验、路径结构校验三项新逻辑均按 R32 要求触发并精确定位。

---

## 4. 输出产物

```text
v0.4_results/00_validation/phase0_step7c_checker_test_fix01/
├── consistency_check_report.json                （主自测：Step7a manifest，17 项）
└── _synthetic_fixtures/                          （合成单元测试，全部 _synthetic 标记）
    ├── ocs_clean.json / img_clean.json
    ├── ocs_badmatrix.json
    ├── ocs_badpath.json
    ├── report_clean.json                         （场景 A：overall PASS）
    ├── report_clean_gate.json                    （场景 A2：completeness NOT_COMPLETE）
    ├── report_badmatrix.json                     （场景 B）
    └── report_badpath.json                       （场景 C）
```

代码修改：`06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py`（仅此一文件）。

---

## 5. 归位与清理（R32 §2.1）

- 上一轮产生的嵌套镜像目录 `02_Claude输出/项目重启_v0.4_BlenderOCS/...` 已删除。
- 上一轮残留的 `33_..._Part1.md` 已删除。
- 本报告写入正确路径，**未**再生成任何 `项目重启_v0.4_BlenderOCS/...` 镜像嵌套目录：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/34_1C-E15-FIX01_checker路径解析修复_Claude执行报告.md
```

---

## 6. 边界确认

```text
✓ 未进入全量 2664 姿态生成
✓ 未训练模型
✓ 未修改论文正文
✓ 未修改冻结文件 13/14/24/25
✓ 未写入 04_Codex审阅/
✓ 未生成 Codex 裁决文件
✓ 仅修改 checker（06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py）
✓ 未用占位/identity 矩阵冒充真实 dry-run；合成 fixture 全部显式 _synthetic 标记
✓ 已声明 Step7c 仍未完成，下一步需 builder/matrix/mask/dry-run（FIX02）
```

---

## 7. 交回 Codex 审阅项

```text
1. checker 路径解析是否不再误报已存在文件
   —— 主自测：ocs/image_paths_exist 均 0 missing（原 20/10 误报已消除）。
2. 新增 17 项检查结构是否正确
   —— check_count=17；场景 A 可达全 PASS；docstring 已更新为 17 项。
3. completeness gate 是否可用于 full-run final 模式
   —— 场景 A2：--expected-record-count 2664 触发 NOT_COMPLETE。
4. 是否进入 Step7c-FIX02（builder/matrix/mask/dry-run）
   —— 本轮未做，建议 FIX02 执行。

交回文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/34_1C-E15-FIX01_checker路径解析修复_Claude执行报告.md
v0.4_results/00_validation/phase0_step7c_checker_test_fix01/consistency_check_report.json
```

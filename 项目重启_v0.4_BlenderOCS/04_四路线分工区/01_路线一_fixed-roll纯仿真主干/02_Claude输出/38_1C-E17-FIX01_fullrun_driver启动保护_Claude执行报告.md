# 38 1C-E17-FIX01：Full-run driver 启动保护 Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据文件：R36 Codex 审阅 §4 1C-E17-FIX01 要求  
被修复对象：R36 判定的 P0-1（skip-existing/resume）、P0-2（分批入口）、P1-1（入口命名）

---

## 0. 总体结果

```text
1C-E17-FIX01：COMPLETE
skip-existing 保护：VERIFIED（3/3 SKIPPED_EXISTING）
分批参数：READY（--start-index/--count, --batch-index/--batch-size）
metadata 状态记录：READY（RENDERED/SKIPPED_EXISTING/PARTIAL_EXISTING/FAILED）
入口命名统一：DONE（run_full_postprocess.py 正式入口 + run_phase1_fullrun.py 兼容 wrapper）
小规模验证：4 姿态端到端通过（manifest + checker 17/17 PASS）
全量 2664 姿态生成：NOT STARTED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
修改冻结文件 13/14/24/25：NOT TOUCHED
写入 04_Codex审阅/：NOT WRITTEN
```

---

## 1. 修改文件清单

| 操作 | 文件 | 说明 |
|------|------|------|
| **修改** | `06_v0.4_code/02_blender/render_full_2664_shadow.py` | 增加 skip-existing/force、分批参数、预扫描、每姿态状态追踪、enhanced metadata |
| **新增** | `06_v0.4_code/05_postprocess/run_phase1_fullrun.py` | R35 兼容 wrapper，转发到 run_full_postprocess.py |
| **新增（验证）** | `v0.4_results/01_fullrun/shadow_passes/yaw030_pitch+000_roll+000_camera.exr` | FIX01 新渲染 camera EXR |
| **新增（验证）** | `v0.4_results/01_fullrun/shadow_passes/yaw030_pitch+000_roll+000_sun.exr` | FIX01 新渲染 sun EXR |
| **更新（验证）** | `v0.4_results/01_fullrun/shadow_passes/render_metadata.json` | FIX01 新 metadata（含 SKIPPED_EXISTING/RENDERED 状态） |
| **更新（验证）** | `v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json` | FIX01 4 姿态后处理 summary |
| **新增（验证）** | `v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fix01.json` | FIX01 OCS manifest（4 records） |
| **新增（验证）** | `v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fix01.json` | FIX01 Image manifest（4 records） |
| **新增（验证）** | `v0.4_results/01_fullrun/postprocess/consistency_check_report_fix01.json` | FIX01 checker report（17/17 PASS） |

原有 smoke 产物（3 姿态 EXR、camera_matrices_blender.json、smoke manifest/checker）均未被覆盖，Codex R36 复跑报告保留完整。

---

## 2. Blender driver 启动保护

### 2.1 skip-existing / force 行为

```text
默认行为（无参数）：skip_existing=True, force=False
  → 渲染前检查 {label}_camera.exr 和 {label}_sun.exr
  → 两者均存在 → SKIPPED_EXISTING，跳过渲染
  → 仅一侧存在 → PARTIAL_EXISTING，不静默覆盖（需 --force）
  → 两侧均不存在 → 进入渲染队列

--force：skip_existing=False, force=True
  → 跳过预扫描保护，所有选定姿态直接渲染
  → 覆盖已存在文件

--no-skip-existing：skip_existing=False, force=False
  → 不跳过已存在完整 pair，但仍对 PARTIAL_EXISTING 保持保护
```

### 2.2 分批参数

实现两种互斥的分批方式：

```text
方式 A：--start-index <int> --count <int>
  例: --start-index 0 --count 200     → 姿态 0..199
  例: --start-index 200 --count 200   → 姿态 200..399

方式 B：--batch-index <int> --batch-size <int>
  例: --batch-index 0 --batch-size 200 → 姿态 0..199
  例: --batch-index 1 --batch-size 200 → 姿态 200..399
```

两种方式均在 `selection_detail` 中记录起止索引。

现有 `--smoke N` 和 `--labels A,B,C` 保留不变，与分批参数互斥（按优先级：labels > smoke > start-index/count > batch-index/size > full）。

### 2.3 metadata 每姿态状态

每个姿态在 `render_metadata.json` 的 `results` 数组中包含：

| 字段 | 含义 |
|------|------|
| `status` | `RENDERED` / `SKIPPED_EXISTING` / `PARTIAL_EXISTING` / `FAILED` |
| `camera_file` | camera EXR 绝对路径 |
| `sun_file` | sun EXR 绝对路径 |
| `camera_exists` | bool，渲染后/跳过时文件是否存在 |
| `sun_exists` | bool，同上 |
| `error` | 仅 FAILED 时有值，异常信息 |

### 2.4 metadata selection 与统计字段

```json
{
  "total_grid_size": 2664,
  "selection_mode": "labels|smoke|start_index_count|batch_index_size|full",
  "selection_detail": {
    "requested_labels": [...],   // labels 模式
    "smoke_n": N,                // smoke 模式
    "start_index": N,            // start_index_count 模式
    "count": N,
    "end_index": N,
    "batch_index": N,            // batch_index_size 模式
    "batch_size": N,
    "total_grid_size": 2664,
    "selected_count": N,
    "selection_mode": "..."
  },
  "skip_existing": true|false,
  "force": true|false,
  "selected_count": N,
  "rendered_count": N,
  "skipped_count": N,
  "partial_count": N,
  "failed_count": N
}
```

---

## 3. 入口命名统一

```text
正式入口：06_v0.4_code/05_postprocess/run_full_postprocess.py（E17 实际交付，R36 smoke 通过）
兼容入口：06_v0.4_code/05_postprocess/run_phase1_fullrun.py（R35 规划文件预期名称，等价 wrapper）

后续命令、报告和 CLAUDE 状态统一使用 run_full_postprocess.py；
run_phase1_fullrun.py 仅作为 importlib wrapper 满足 R35 兼容性。
```

---

## 4. 小规模验证

### 4.1 验证姿态

```text
已有（E17 smoke，应 SKIPPED_EXISTING）：
  yaw010_pitch+000_roll+000  （yaw=10°, pitch=0°）
  yaw020_pitch+000_roll+000  （yaw=20°, pitch=0°）
  yaw025_pitch+015_roll+000  （yaw=25°, pitch=15°）

新增（FIX01，应 RENDERED）：
  yaw030_pitch+000_roll+000  （yaw=30°, pitch=0°）

与已有数据集无重叠：
  Step6 small-run: yaw180, yaw150+p025, yaw000, yaw090, yaw300-p025
  Step7c dry-run: yaw045+p000, yaw270-p030, yaw135+p000
  Step4 20-attitude: 不含 yaw010/020/025/030
```

### 4.2 Stage 1 — Blender 预扫描 + 渲染

```powershell
blender --background --python render_full_2664_shadow.py -- --labels "yaw010_pitch+000_roll+000,yaw020_pitch+000_roll+000,yaw025_pitch+015_roll+000,yaw030_pitch+000_roll+000"
```

预扫描结果：

```text
[SKIP]   yaw010_pitch+000_roll+000 — 已有完整 camera+sun pair
[SKIP]   yaw020_pitch+000_roll+000 — 已有完整 camera+sun pair
[SKIP]   yaw025_pitch+015_roll+000 — 已有完整 camera+sun pair
[RENDER] yaw030_pitch+000_roll+000

RENDER: 1 | SKIP: 3 | PARTIAL: 0
```

渲染结果：

```text
RENDERED:          1
SKIPPED_EXISTING:  3
PARTIAL_EXISTING:  0
FAILED:            0

yaw030_pitch+000_roll+000_camera.exr: 125 KB ✅
yaw030_pitch+000_roll+000_sun.exr:    99 KB ✅
```

### 4.3 Stage 2 — 后处理

```powershell
python run_full_postprocess.py --attitudes "yaw010_pitch+000_roll+000,yaw020_pitch+000_roll+000,yaw025_pitch+015_roll+000,yaw030_pitch+000_roll+000"
```

结果：

| 姿态 | OCS_total | camera_visible | contributing | status |
|------|-----------|----------------|--------------|--------|
| yaw010_pitch+000 | 1.69e-02 | 5807 | 5496 | COMPLETE |
| yaw020_pitch+000 | 1.98e-02 | 5529 | 5274 | COMPLETE |
| yaw025_pitch+015 | 2.28e-02 | 5348 | 5108 | COMPLETE |
| yaw030_pitch+000 | 2.51e-02 | 5468 | 5096 | COMPLETE |

OVERALL = COMPLETE，4/4 均含 `sun_visibility_mask_path`。

### 4.4 Stage 3 — Manifest + Checker

```text
OCS manifest:  4 records ✅
Image manifest: 4 records ✅
```

Checker 结果（`--expected-record-count 4`）：

```text
总状态: PASS
检查项: 17
[PASS] geometry_version_match
[PASS] brdf_version_match
[PASS] visibility_version_match
[PASS] sun_visibility_match
[PASS] shadow_mapping_method_match
[PASS] brdf_model_match
[PASS] brdf_model_vs_brdf_version_consistency
[PASS] v_sun_macro_mode_consistency
[PASS] i_scale_match
[PASS] record_id_set_match
[PASS] per_record_consistency (4 records)
[PASS] path_base_consistency (0 inconsistencies)
[PASS] ocs_paths_exist (0 missing)
[PASS] image_paths_exist (0 missing)
[PASS] camera_matrix_non_null_and_valid (0 invalid)
[PASS] sun_visibility_mask_path_non_null_and_exists (0 missing)
[PASS] records_completeness (OCS=4, Image=4, expected=4, gate=True)
```

**17/17 PASS**，全部检查通过。

---

## 5. R36 P0/P1 问题闭合状态

| R36 问题 | 状态 | 证据 |
|----------|------|------|
| P0-1: 缺少 skip-existing / resume | **已闭合** | 3/3 SKIPPED_EXISTING 实测通过；PARTIAL_EXISTING 保护逻辑已实现；metadata 区分 4 种状态 |
| P0-2: 缺少分批入口 | **已闭合** | `--start-index`/`--count` 和 `--batch-index`/`--batch-size` 均已实现，selection_detail 记录起止索引 |
| P1-1: 后处理入口命名不统一 | **已闭合** | `run_full_postprocess.py` 为正式入口；`run_phase1_fullrun.py` wrapper 满足 R35 兼容性 |

---

## 6. 全量分批运行推荐命令

以下命令已可用但**当前不执行**：

```powershell
# 批次 0（姿态 0..199）
blender --background --python render_full_2664_shadow.py -- --start-index 0 --count 200

# 批次 1（姿态 200..399）
blender --background --python render_full_2664_shadow.py -- --start-index 200 --count 200

# ...后续批次类推，共 14 批（13 批 200 + 1 批 64）

# 断点续跑：默认 skip_existing=True，中断后重跑同一批次自动跳过已完成姿态
# 强制重跑某批次：加 --force
```

---

## 7. 红线边界确认

- [x] **未启动全量 2664**：仅 `--labels` 指定 4 姿态，无全量参数被触发
- [x] **未训练**：无模型训练
- [x] **未改论文正文**：未触及论文文件
- [x] **未修改冻结文件**：13/14/24/25 未改动
- [x] **未写入 04_Codex审阅/**：报告写入 `02_Claude输出/`
- [x] **未生成 Codex 裁决文件**
- [x] **未覆盖 R36 Codex 复跑报告**：新 checker report 使用 `fix01` 后缀，原 smoke report 保留完整
- [x] **E17 smoke 产物未被覆盖**：3 个已有姿态的 camera/sun EXR 保持原始时间戳，skip 保护验证通过
- [x] **相机矩阵来自 Blender matrix_world**：camera_matrices_blender.json 保留完好且被新 metadata 引用

---

## 8. 给 Codex 的 R37 审阅入口

```text
Claude 输出报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/38_1C-E17-FIX01_fullrun_driver启动保护_Claude执行报告.md

修改/新增文件（供复核）：
- 06_v0.4_code/02_blender/render_full_2664_shadow.py（已修改，增加启动保护）
- 06_v0.4_code/05_postprocess/run_phase1_fullrun.py（新增兼容 wrapper）

FIX01 验证产物：
- v0.4_results/01_fullrun/shadow_passes/render_metadata.json（含 SKIPPED_EXISTING/RENDERED 状态）
- v0.4_results/01_fullrun/shadow_passes/yaw030_pitch+000_roll+000_camera.exr
- v0.4_results/01_fullrun/shadow_passes/yaw030_pitch+000_roll+000_sun.exr
- v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json（4/4 COMPLETE）
- v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fix01.json
- v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fix01.json
- v0.4_results/01_fullrun/postprocess/consistency_check_report_fix01.json（17/17 PASS）

Codex R37 判断项：
1. Blender driver 的 skip-existing/force 是否满足 P0-1 闭合要求
2. 分批参数（--start-index/--count, --batch-index/--batch-size）是否满足 P0-2 闭合要求
3. metadata 每姿态状态记录（RENDERED/SKIPPED_EXISTING/PARTIAL_EXISTING/FAILED）是否可审计
4. 入口命名统一方案是否可接受
5. 4 姿态小规模验证是否成立（3 SKIP + 1 RENDER → postprocess → manifest → checker 17/17）
6. 是否正式放行全量 2664 姿态生成
```

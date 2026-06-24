# 39 1C-E18：全量 2664 生成与 manifest/checker Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据文件：R37 Codex 审阅 §4 1C-E18 执行要求  
放行范围：路线一 C / Phase 0 / B0 engineering baseline 全量 2664 fixed-roll 姿态生成

---

## 0. 总体结果

```text
1C-E18：COMPLETE
全量 2664 姿态生成：COMPLETE（14 批全部通过）
Stage A — Blender shadow pass：2664 camera + 2664 sun EXR = 5328 文件 ✅
Stage B — 后处理：2664/2664 COMPLETE ✅
Stage C — manifest + checker：17/17 PASS，expected=2664 ✅
训练：NOT STARTED
论文正文改写：NOT TOUCHED
冻结文件 13/14/24/25：NOT TOUCHED
写入 04_Codex审阅/：NOT WRITTEN
B1/GGX/三轴/路线二三四扩展：NOT STARTED
```

---

## 1. Stage A：14 批 Blender shadow pass 统计

Driver：`06_v0.4_code/02_blender/render_full_2664_shadow.py`  
默认启用 skip-existing；不使用 `--force`，除 Batch 6 修复外。  
每姿态输出：`{label}_camera.exr` + `{label}_sun.exr`（MULTILAYER EXR, 256×256, 1 sample, OPTIX GPU）

| 批次 | start-index | count | 索引范围 | RENDERED | SKIPPED | PARTIAL | FAILED | 结果 |
|------|-------------|-------|----------|----------|---------|---------|--------|------|
| 0 | 0 | 200 | 0–199 | 198 | 2 | 0 | 0 | ✅ SUCCESS |
| 1 | 200 | 200 | 200–399 | 198 | 2 | 0 | 0 | ✅ SUCCESS |
| 2 | 400 | 200 | 400–599 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 3 | 600 | 200 | 600–799 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 4 | 800 | 200 | 800–999 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 5 | 1000 | 200 | 1000–1199 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 6 | 1200 | 200 | 1200–1399 | 145→**200** | 54→0 | **1→0** | 0 | ⚠️ 修复后 ✅ |
| 7 | 1400 | 200 | 1400–1599 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 8 | 1600 | 200 | 1600–1799 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 9 | 1800 | 200 | 1800–1999 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 10 | 2000 | 200 | 2000–2199 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 11 | 2200 | 200 | 2200–2399 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 12 | 2400 | 200 | 2400–2599 | 200 | 0 | 0 | 0 | ✅ SUCCESS |
| 13 | 2600 | 64 | 2600–2663 | 64 | 0 | 0 | 0 | ✅ SUCCESS |
| **合计** | — | — | **0–2663** | **2660** | **4** | **0** | **0** | **2664** |

### 1.1 SKIPPED 明细

4 个 SKIPPED_EXISTING 均为 E17 smoke / FIX01 已有产物：

| 姿态 | 来源 |
|------|------|
| yaw010_pitch+000_roll+000 | E17 smoke |
| yaw020_pitch+000_roll+000 | E17 smoke |
| yaw025_pitch+015_roll+000 | E17 smoke |
| yaw030_pitch+000_roll+000 | FIX01 验证 |

skip-existing 保护正常工作：4 个已有姿态未被重新渲染，其余 2660 姿态全部新鲜渲染。

### 1.2 Batch 6 PARTIAL_EXISTING 修复

Batch 6（索引 1200–1399）首次运行时出现 1 个 PARTIAL_EXISTING（仅一侧 EXR 存在，疑为前序批次场景异常中断残留）。按 R37 要求暂停推进，执行修复：

```powershell
blender --background --python render_full_2664_shadow.py -- --start-index 1200 --count 200 --force
```

`--force` 重渲染该批全部 200 姿态，PARTIAL → 0，该批最终 200 RENDERED + 0 异常。

### 1.3 最终文件数

```text
camera EXR: 2664
sun EXR:    2664
total EXR:  5328
输出目录: v0.4_results/01_fullrun/shadow_passes/
```

---

## 2. Stage B：全量后处理

Driver：`06_v0.4_code/05_postprocess/run_full_postprocess.py --all`

```text
r_max = 1.472605
I_scale = 5.444864e-01（来自 Step 5 的 5 姿态 image impact validation）
pixel_area_m2 = 1.601541e-04
BRDF 分支: B0
```

结果：

```text
overall_status: COMPLETE
n_total_labels: 2664
n_completed:    2664
brdf_branch:    B0
geom_id:        phase63
```

全部 2664 条 record 均为 `COMPLETE`，且均包含 `sun_visibility_mask_path`。  
中断未发生；若后续需 resume，可使用：

```powershell
python run_full_postprocess.py --all --resume v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json
```

编码问题备注：`--all` 模式下 print 语句含 ⚠ emoji，在 Windows GBK 终端触发 `UnicodeEncodeError`。通过设置 `PYTHONIOENCODING=utf-8` 环境变量解决；建议后续在 `run_full_postprocess.py` 中将 emoji 替换为纯文本标记。

---

## 3. Stage C：Manifest 与 Checker

### 3.1 Manifest

| Manifest | 路径 | Records |
|----------|------|---------|
| OCS | `v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json` | 2664 |
| Image | `v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json` | 2664 |

未覆盖 smoke（`_smoke.json`）、fix01（`_fix01.json`）和 codex_rerun（`_codex_rerun.json`）报告。

### 3.2 Checker 结果（17/17 PASS）

```text
总状态: PASS
检查项数: 17

[PASS] geometry_version_match
[PASS] brdf_version_match
[PASS] visibility_version_match
[PASS] sun_visibility_match
[PASS] shadow_mapping_method_match
[PASS] brdf_model_match
[PASS] brdf_model_vs_brdf_version_consistency
[PASS] v_sun_macro_mode_consistency
[PASS] i_scale_match
[PASS] record_id_set_match (OCS=2664, Image=2664)
[PASS] per_record_consistency (2664 records checked)
[PASS] path_base_consistency (0 inconsistencies)
[PASS] ocs_paths_exist (0 missing, 0 base-inconsistent)
[PASS] image_paths_exist (0 missing, 0 base-inconsistent)
[PASS] camera_matrix_non_null_and_valid (0 invalid)
[PASS] sun_visibility_mask_path_non_null_and_exists (0 missing)
[PASS] records_completeness (OCS=2664, Image=2664, expected=2664, gate=True)
```

报告路径：`v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun.json`

---

## 4. 执行问题与处置

| 问题 | 阶段 | 处置 | 状态 |
|------|------|------|------|
| Batch 6 出现 1 PARTIAL_EXISTING | Stage A | 用 `--force` 重跑 Batch 6 全部 200 姿态 | 已修复，该批 0 PARTIAL/FAILED |
| `--all` 模式 emoji 触发 GBK UnicodeEncodeError | Stage B | 设置 `PYTHONIOENCODING=utf-8` 环境变量 | 已绕过，建议后续代码中去掉 emoji |
| 循环运行超时（10分钟） | Stage A | 分两段运行（400-1000, 1200-1800+2000-2600） | 正常完成，无数据丢失 |

---

## 5. 全量产物目录结构

```text
v0.4_results/01_fullrun/
├── shadow_passes/
│   ├── camera_matrices_blender.json
│   ├── render_metadata.json              ← 最后一批的 metadata
│   ├── yaw000_pitch-090_roll+000_camera.exr
│   ├── yaw000_pitch-090_roll+000_sun.exr
│   ├── ... (共 5328 个 EXR 文件)
│   ├── yaw355_pitch+090_roll+000_camera.exr
│   └── yaw355_pitch+090_roll+000_sun.exr
└── postprocess/
    ├── fullrun_postprocess_summary.json   ← 2664/2664 COMPLETE
    ├── ocs_manifest_v0_4_fullrun.json     ← 2664 records
    ├── image_manifest_v0_4_fullrun.json   ← 2664 records
    ├── consistency_check_report_fullrun.json ← 17/17 PASS
    ├── ocs_manifest_v0_4_smoke.json       ← E17 smoke（保留）
    ├── image_manifest_v0_4_smoke.json     ← E17 smoke（保留）
    ├── consistency_check_report_smoke.json ← E17 smoke（保留）
    ├── ocs_manifest_v0_4_fix01.json       ← FIX01（保留）
    ├── image_manifest_v0_4_fix01.json     ← FIX01（保留）
    ├── consistency_check_report_fix01.json ← FIX01（保留）
    ├── consistency_check_report_fix01_codex_rerun.json ← R37 Codex 复跑（保留）
    ├── yaw000_pitch-090_roll+000_linear.exr
    ├── yaw000_pitch-090_roll+000_brdf.png
    ├── yaw000_pitch-090_roll+000_ocs.json
    ├── yaw000_pitch-090_roll+000_v_sun_macro.png
    ├── yaw000_pitch-090_roll+000_v_sun_macro.npy
    ├── ... (每姿态 5 个后处理文件)
    └── yaw355_pitch+090_roll+000_*.exr/.png/.json/.npy
```

---

## 6. 全量分批运行命令参考（供后续复用）

```powershell
cd "D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS"

# 默认 skip-existing（推荐，支持中断恢复）
blender --background --python "06_v0.4_code\02_blender\render_full_2664_shadow.py" -- --start-index 0 --count 200
blender --background --python "06_v0.4_code\02_blender\render_full_2664_shadow.py" -- --start-index 200 --count 200
# ... 依次类推至 --start-index 2600 --count 64

# 若有 PARTIAL_EXISTING，用 --force 修复该批
blender --background --python "06_v0.4_code\02_blender\render_full_2664_shadow.py" -- --start-index <N> --count <N> --force

# 后处理
PYTHONIOENCODING=utf-8 python "06_v0.4_code\05_postprocess\run_full_postprocess.py" --all

# Manifest + Checker
python "06_v0.4_code\06_manifest\build_ocs_manifest_v0_4.py" ...
python "06_v0.4_code\06_manifest\build_image_manifest_v0_4.py" ...
python "06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py" --expected-record-count 2664 ...
```

---

## 7. 红线边界确认

- [x] **未训练**：无模型训练
- [x] **未改论文正文**：未触及论文文件
- [x] **未触碰冻结文件 13/14/24/25**
- [x] **未写入 04_Codex审阅/**
- [x] **未启动 B1 正式材料公式替换**
- [x] **未启动 GGX 对照批量生成**
- [x] **未启动三轴小项目**
- [x] **未启动路线二/三/四扩展**
- [x] **未自行宣布下一阶段放行**
- [x] **未覆盖 smoke/fix01/codex_rerun 报告**
- [x] **相机矩阵来自 Blender matrix_world**

---

## 8. 给 Codex 的 R38 审阅入口

```text
Claude 输出报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/39_1C-E18_全量2664生成与manifest_checker_Claude执行报告.md

全量产物（供复核）：
- v0.4_results/01_fullrun/shadow_passes/（2664 camera + 2664 sun EXR）
- v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json（2664/2664 COMPLETE）
- v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json（2664 records）
- v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json（2664 records）
- v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun.json（17/17 PASS）

Codex R38 判断项：
1. 14 批 Blender shadow pass 是否全部正常完成（2664 camera + 2664 sun EXR）
2. Batch 6 PARTIAL_EXISTING 修复是否可接受
3. Postprocess 2664/2664 COMPLETE 是否成立
4. Checker 17/17 PASS 是否成立（建议 Codex 复跑验证）
5. 是否正式放行 Phase 0 B0 成果区归档
6. 是否放行后续训练阶段
```

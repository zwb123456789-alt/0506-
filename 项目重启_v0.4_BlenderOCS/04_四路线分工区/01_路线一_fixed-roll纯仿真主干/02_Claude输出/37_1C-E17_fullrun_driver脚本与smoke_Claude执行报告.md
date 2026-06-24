# 37 1C-E17：Full-run driver 脚本与 3 姿态 smoke Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据文件：用户直接指令（补齐 full-run driver，只做 3 姿态 smoke，不启动全量）

---

## 0. 总体结果

```text
1C-E17：COMPLETE
全量 2664 姿态生成：NOT STARTED（仅 3 姿态 smoke，未启动全量）
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：待 Codex R36 放行裁决
```

**新增** 2 个 full-run driver 脚本，通过 3 姿态端到端 smoke 验证：Blender 渲染 → 后处理 → manifest → checker 全部 17/17 PASS。

---

## 1. 新增文件清单

| 操作 | 文件 | 说明 |
|------|------|------|
| **新增** | `06_v0.4_code/02_blender/render_full_2664_shadow.py` | 全量 Blender shadow pass 渲染 driver。生成 72 yaw × 37 pitch = 2664 全量姿态网格；支持 `--smoke N`（渲染前 N 个）和 `--labels A,B,C`（指定姿态列表）；输出 camera/sun EXR + camera_matrices_blender.json + render_metadata.json |
| **新增** | `06_v0.4_code/05_postprocess/run_full_postprocess.py` | 全量 BRDF/OCS/image 后处理 driver。支持 `--attitudes`（指定姿态）、`--all`（全量 2664）、`--resume`（checkpoint 续跑）；每个姿态输出 V_sun_macro mask + EXR/PNG + OCS JSON；输出 fullrun_postprocess_summary.json |

---

## 2. Smoke 姿态选择

```text
yaw010_pitch+000_roll+000  （yaw=10°, pitch=0°）
yaw020_pitch+000_roll+000  （yaw=20°, pitch=0°）
yaw025_pitch+015_roll+000  （yaw=25°, pitch=15°）
```

与已使用姿态无重叠：
- Step6 small-run: yaw180, yaw150+p025, yaw000, yaw090, yaw300-p025
- Step7c dry-run: yaw045+p000, yaw270-p030, yaw135+p000
- Step4 20-attitude set: 不含 yaw010, yaw020, yaw025

3 个姿态均在 5° 网格上，是全新的渲染产物。

---

## 3. Smoke 执行结果

### 3.1 Stage 1 — Blender 渲染（render_full_2664_shadow.py）

```powershell
"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python "D:\...\render_full_2664_shadow.py" -- --labels "yaw010_pitch+000_roll+000,yaw020_pitch+000_roll+000,yaw025_pitch+015_roll+000"
```

结果：

| 姿态 | camera.exr | sun.exr | 文件大小 |
|------|------------|---------|---------|
| yaw010_pitch+000 | ✅ 139 KB | ✅ 86 KB | 正常 |
| yaw020_pitch+000 | ✅ 133 KB | ✅ 93 KB | 正常 |
| yaw025_pitch+015 | ✅ 138 KB | ✅ 110 KB | 正常 |

附加产物：`camera_matrices_blender.json`（矩阵来自 Blender matrix_world）、`render_metadata.json`

输出目录：`v0.4_results/01_fullrun/shadow_passes/`

### 3.2 Stage 2 — 后处理（run_full_postprocess.py）

```powershell
cd "D:\...项目重启_v0.4_BlenderOCS"
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code\05_postprocess\run_full_postprocess.py --attitudes "yaw010_pitch+000_roll+000,yaw020_pitch+000_roll+000,yaw025_pitch+015_roll+000"
```

结果：

| 姿态 | OCS_total | camera_visible | nol_positive | sun_visible | contributing |
|------|-----------|----------------|--------------|-------------|-------------|
| yaw010_pitch+000 | 1.69e-02 | 5807 | 5496 | 5807 | 5496 |
| yaw020_pitch+000 | 1.98e-02 | 5529 | 5274 | 5529 | 5274 |
| yaw025_pitch+015 | 2.28e-02 | 5348 | 5108 | 5348 | 5108 |

每姿态产物：`_linear.exr`, `_brdf.png`, `_ocs.json`, `_v_sun_macro.png`, `_v_sun_macro.npy`

输出目录：`v0.4_results/01_fullrun/postprocess/`

### 3.3 Stage 3 — Manifest 构建 + Checker

```powershell
build_ocs_manifest_v0_4.py --data-root . --camera-matrix-json ...camera_matrices_blender.json --sun-visibility-mask-dir .../01_fullrun/postprocess
build_image_manifest_v0_4.py --data-root .
check_manifest_consistency_v0_4.py --data-root . --require-prefix v0.4_results/ --expected-record-count 3
```

**17 项 checker 结果**：

```text
overall_status = PASS
check_count = 17
checks 1-17 = PASS（全部）
records_completeness = PASS（3/3, gate enabled）
path_base_consistency = PASS（0 inconsistencies）
camera_matrix_non_null_and_valid = PASS（0 invalid）
sun_visibility_mask_path_non_null_and_exists = PASS（0 missing）
```

路径基准验证：

```text
camera/sun EXR 路径     → v0.4_results/01_fullrun/shadow_passes/*.exr
后处理 EXR/PNG 路径      → v0.4_results/01_fullrun/postprocess/*.exr/.png
V_sun_macro mask 路径    → v0.4_results/01_fullrun/postprocess/*_v_sun_macro.png
全部路径满足 --require-prefix v0.4_results/，0 inconsistencies
```

---

## 4. Driver 脚本能力覆盖

| 能力 | render_full_2664_shadow.py | run_full_postprocess.py |
|------|---------------------------|------------------------|
| 全量 2664 网格生成 | ✅ `generate_full_attitude_list()` | ✅ `generate_full_attitude_labels()` |
| Smoke 限制数量 | ✅ `--smoke N` | ✅ `--attitudes A,B,C` |
| 指定姿态列表 | ✅ `--labels A,B,C` | ✅ `--attitudes A,B,C` |
| Checkpoint / Resume | ❌（仅检查文件存在性） | ✅ `--resume <summary.json>` |
| 相机矩阵日志 | ✅ 自动输出 | N/A（从 Blender 日志读取） |
| 渲染元数据 | ✅ render_metadata.json | N/A |
| V_sun_macro mask | N/A | ✅ 每姿态 PNG + NPY |
| BRDF/OCS/image 后处理 | N/A | ✅ 完整链路 |
| 输出目录 | `01_fullrun/shadow_passes/` | `01_fullrun/postprocess/` |

---

## 5. 全量产物的目录结构（当前 smoke 后状态）

```text
v0.4_results/01_fullrun/
├── shadow_passes/
│   ├── camera_matrices_blender.json     ← Blender matrix_world 日志
│   ├── render_metadata.json             ← 本次 smoke 渲染元数据
│   ├── yaw010_pitch+000_roll+000_camera.exr
│   ├── yaw010_pitch+000_roll+000_sun.exr
│   ├── yaw020_pitch+000_roll+000_camera.exr
│   ├── yaw020_pitch+000_roll+000_sun.exr
│   ├── yaw025_pitch+015_roll+000_camera.exr
│   └── yaw025_pitch+015_roll+000_sun.exr
└── postprocess/
    ├── fullrun_postprocess_summary.json  ← 后处理 summary（checkpoint）
    ├── ocs_manifest_v0_4_smoke.json      ← OCS manifest（3 records）
    ├── image_manifest_v0_4_smoke.json    ← Image manifest（3 records）
    ├── consistency_check_report_smoke.json ← 17/17 PASS
    ├── yaw010_pitch+000_roll+000_*.exr/.png/.npy/.json
    ├── yaw020_pitch+000_roll+000_*.exr/.png/.npy/.json
    └── yaw025_pitch+015_roll+000_*.exr/.png/.npy/.json
```

---

## 6. 全量正式运行命令参考

### Step A: Blender 全量渲染（⚠ 此阶段不执行）

```powershell
"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python "D:\...\render_full_2664_shadow.py"
# 默认渲染全部 2664 姿态
# 建议分批：先渲染 200 姿态做 pilot，再分 8-10 批完成全量
# 每批间隔可用于检查 render_metadata.json 确认无 MISS
```

### Step B: 后处理（⚠ 此阶段不执行）

```powershell
cd "D:\...项目重启_v0.4_BlenderOCS"
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code\05_postprocess\run_full_postprocess.py --all
# 支持中断后 resume:
# python run_full_postprocess.py --resume v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json
```

### Step C: Manifest + Checker 门禁（⚠ 此阶段不执行）

见 1C-E16 报告 §3.6-3.7。

---

## 7. 红线边界确认

- [x] **未启动全量 2664**：仅 3 姿态 smoke，全量参数（`--all`, 无 `--smoke`/`--labels`）未被触发
- [x] **未训练**：无模型训练
- [x] **未修改论文正文**：未触及论文文件
- [x] **未修改冻结文件**：13/14/24/25 未改动
- [x] **未写入 04_Codex审阅/**：报告写入 `02_Claude输出/`
- [x] **未生成 Codex 裁决文件**
- [x] **3 个 smoke 姿态与 Step6/Step7c 无重叠**：独立验证
- [x] **相机矩阵来自 Blender matrix_world**：非 identity/手工

---

## 8. 给 Codex 的下轮审阅入口（R36）

```text
Claude 输出报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/37_1C-E17_fullrun_driver脚本与smoke_Claude执行报告.md

新增 driver 脚本（供复核）：
- 06_v0.4_code/02_blender/render_full_2664_shadow.py
- 06_v0.4_code/05_postprocess/run_full_postprocess.py

Smoke 验证产物：
- v0.4_results/01_fullrun/shadow_passes/camera_matrices_blender.json
- v0.4_results/01_fullrun/shadow_passes/render_metadata.json
- v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json
- v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_smoke.json
- v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_smoke.json
- v0.4_results/01_fullrun/postprocess/consistency_check_report_smoke.json

Codex R36 判断项：
1. render_full_2664_shadow.py 是否可作为全量 Blender 渲染 driver
2. run_full_postprocess.py 是否可作为全量后处理 driver（含 checkpoint/resume）
3. 3 姿态 smoke 是否端到端通过（Blender render → postprocess → manifest → checker 17/17）
4. 是否正式放行全量 2664 姿态生成
```

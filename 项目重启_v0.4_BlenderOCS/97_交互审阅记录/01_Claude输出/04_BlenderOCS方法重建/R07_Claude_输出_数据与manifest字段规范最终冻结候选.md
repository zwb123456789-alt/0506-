# 11 v0.4 数据与 Manifest 字段规范（最终冻结候选）

生成时间：2026-06-08
修订基准：Codex 复审意见 CR4-001 ～ CR4-008（`09_Codex复审意见_前向模型冻结规范修订版.md`）
上版文件：`08_v0.4数据与manifest字段规范_Claude修订版.md`（已由本最终冻结候选版取代）

---

## 一、v0.4 旧结果全封存，所有主结果重跑

### 1.1 封存原则

v0.3 Acta/ASR 主投优先稿及所有关联实验产物全部封存，不进入 v0.4 主结果。封存范围：

| 类别 | 封存内容 | 说明 |
|---|---|---|
| OCS 数据 | 旧模块 A `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/` 下所有 `ocs_scan.csv`、`ocs_scan.json` | face-center 采样，已禁用 |
| 图像数据 | 旧模块 B `结果/模块B_渲染/` 下所有 gamma 2.2 编码 PNG | 图像响应链不一致，已禁用 |
| 反演结果 | 所有 v0.3 的 OCS-only / image-only / fusion 训练产物 | 基于旧 OCS 和旧 split |
| 补充实验结果 | 所有 12b/12c/12f/12g 旧输出 | 基于旧数据链 |
| 论文稿件 | v0.3 主稿及变体 | 已封存 |

### 1.2 旧材料的三项仅限用途

1. 作为历史证据（为什么 v0.3 封存）
2. 作为诊断材料（帮助发现类似坑）
3. 作为方法/代码结构参考（旧 `brdf_models.py` 可复用）

### 1.3 v0.4 重新生成范围

**第一层：Single-Geometry 主线（主表基线）**

- [ ] Blender camera-view geometry pass EXR（2664 姿态 × 1 geom = phase63），含 Position/WorldCoord
- [ ] Blender sun-view depth EXR（2664 姿态 × 1 geom）——CR4-005 修正：每 geom 独立 sun shadow
- [ ] Python sun shadow reprojection → V_sun_macro_mask（2664 姿态）
- [ ] Python BRDF 后处理输出（per-pixel linear EXR + log1p PNG + per-frame OCS JSON）
- [ ] v0.4 OCS manifest（single-geom phase63）
- [ ] v0.4 image manifest（single-geom phase63）
- [ ] v0.4 OCS-only MLP 训练
- [ ] v0.4 image-only ResNet-18 训练
- [ ] v0.4 fusion (concat1) 训练 — single-geom 公平基线
- [ ] v0.4 退化鲁棒实验（noise/blur/downsample/background/starfield）

**第二层：Multi-Geometry 扩展（单独报告）——CR4-005 修正**

- [ ] Blender camera-view geometry pass EXR（其余 4 组 sun/det 几何）
- [ ] Blender sun-view depth EXR（**其余 4 组 sun/det 几何，每个 geom 独立**）
- [ ] Python sun shadow reprojection → V_sun_macro_mask（**4 组 geom 全部**）
- [ ] Python BRDF 后处理输出（**4 组 geom 全部**）
- [ ] v0.4 OCS manifest（multi-geom concat5）
- [ ] v0.4 OCS-only MLP（multi-geom concat5）
- [ ] v0.4 fusion（concat5 late fusion）
- [ ] v0.4 补充实验 12b/12c/12f/12g

**数量说明**：2664 = 72 yaw × 37 pitch（不含 360° 重复姿态）。

---

## 二、Manifest 字段 Schema

### 2.1 OCS Manifest (`ocs_manifest_v0.4.json`) —— CR4-003, CR4-006 修正

```json
{
  "geometry_version": "<string>",
  "brdf_version": "<string>",
  "visibility_version": "<string>",
  "ocs_integration_version": "<string>",
  "ocs_source": "Blender-derived pixel-level OCS v0.4",
  "brdf_model": "ggx_cook_torrance",
  "sampling": "Blender Cycles orthogonal projection, 256x256",
  "ortho_scale_m": "<float>",
  "pixel_area_m2": "<float>",
  "resolution": 256,
  "sun_visibility": "<enum: 'camera_visible_nol' | 'camera_visible_nol_plus_sun_shadow_pass' | 'camera_visible_nol_plus_python_raycast'>",
  "shadow_mapping_method": "<string: 'none' | 'sun_view_depth_reprojection' | 'blender_shadow_aov' | 'python_raycast'>",
  "depth_epsilon_m": "<float>",
  "records": [
    {
      "record_id": "<string: e.g. 'phase63_yaw{yyy}_pitch{ppp}'>",
      "yaw_deg": "<float>",
      "pitch_deg": "<float>",
      "geom_id": "<string: e.g. 'phase63'>",
      "sun_dir": ["<float>", "<float>", "<float>"],
      "det_dir": ["<float>", "<float>", "<float>"],
      "ocs_total": "<float>",
      "ocs_per_part": {
        "jinshuzhuti": "<float>",
        "taiyangnengban": "<float>",
        "yinshenban": "<float>"
      },
      "n_pixels_camera_visible": "<int>",
      "n_pixels_nol_positive": "<int>",
      "n_pixels_sun_visible": "<int>",
      "n_pixels_contributing": "<int>",
      "n_pixels_per_part": {
        "jinshuzhuti": "<int>",
        "taiyangnengban": "<int>",
        "yinshenban": "<int>"
      },
      "camera_exr_path": "<string: relative to v0.4 data root>",
      "position_exr_path": "<string or null: relative to v0.4 data root, null if world position reconstructed from depth + camera matrix>",
      "sun_depth_exr_path": "<string or null: relative to v0.4 data root, null if visibility_level = camera_visible_nol>",
      "sun_visibility_mask_path": "<string or null: relative to v0.4 data root, null if visibility_level = camera_visible_nol>",
      "exr_path": "<string>",
      "png_path": "<string>",
      "camera_matrix_world": [
        ["<float>", "<float>", "<float>", "<float>"],
        ["<float>", "<float>", "<float>", "<float>"],
        ["<float>", "<float>", "<float>", "<float>"],
        ["<float>", "<float>", "<float>", "<float>"]
      ],
      "sun_camera_matrix_world": [
        ["<float>", "<float>", "<float>", "<float>"],
        ["<float>", "<float>", "<float>", "<float>"],
        ["<float>", "<float>", "<float>", "<float>"],
        ["<float>", "<float>", "<float>", "<float>"]
      ]
    }
  ]
}
```

**字段说明**（增量标记 CR4 修正）：

| 字段 | 类型 | 含义 | 来源 |
|---|---|---|---|
| `geometry_version` | string | 几何/姿态/采样参数版本 | — |
| `brdf_version` | string | BRDF 模型与材料参数版本 | — |
| `visibility_version` | string | 可见性/遮挡定义版本 | — |
| `ocs_integration_version` | string | OCS 积分公式版本 | — |
| `ocs_source` | string | 固定值 | — |
| `brdf_model` | string | 固定值 `"ggx_cook_torrance"` | — |
| `shadow_mapping_method` | string | 实现方式，与 `visibility_version` 含义不同——前者是"哪种 level"，后者是"用的哪种实现" | CR4-003 |
| `depth_epsilon_m` | float | sun shadow reprojection 的深度容差（米） | CR4-003 |
| **`record_id`** | **string** | **稳定唯一 key：`{geom_id}_yaw{yyy}_pitch{ppp}`，用于跨 manifest 对齐和审计** | **CR4-006** |
| `ocs_total` | float | 总 OCS | — |
| `ocs_per_part` | {string: float} | per-part OCS | — |
| **`n_pixels_camera_visible`** | **int** | **相机可见像素数（Depth < 1e9 且 IndexOB > 0）** | **CR4-006** |
| **`n_pixels_nol_positive`** | **int** | **其中 NoL > eps 的像素数** | **CR4-006** |
| **`n_pixels_sun_visible`** | **int** | **其中 V_sun_macro = 1 的像素数** | **CR4-006** |
| **`n_pixels_contributing`** | **int** | **最终贡献到 OCS 的像素数（NoL > eps 且 V_sun_macro = 1 且 NoV > eps）** | **CR4-006** |
| `n_pixels_per_part` | {string: int} | per-part 可见像素数 | — |
| **`camera_exr_path`** | **string** | **camera-view geometry pass EXR 路径** | **CR4-003** |
| **`position_exr_path`** | **string or null** | **Position/WorldCoord EXR 路径，null 表示由 depth + 矩阵重建** | **CR4-003** |
| **`sun_depth_exr_path`** | **string or null** | **sun-view depth EXR 路径，null 若 visibility = camera_visible_nol** | **CR4-003** |
| **`sun_visibility_mask_path`** | **string or null** | **V_sun_macro_mask 路径** | **CR4-003** |
| `exr_path` | string | 线性 I_linear EXR 路径 | — |
| `png_path` | string | log1p PNG 路径 | — |
| **`camera_matrix_world`** | **float[4][4]** | **camera-view 相机的世界变换矩阵（Blender 导出）** | **CR4-003** |
| **`sun_camera_matrix_world`** | **float[4][4]** | **sun-view 相机的世界变换矩阵** | **CR4-003** |

### 2.2 Image Manifest (`image_manifest_v0.4.json`) —— CR4-001 联动

```json
{
  "geometry_version": "<string>",
  "brdf_version": "<string>",
  "visibility_version": "<string>",
  "image_preprocess_version": "<string>",
  "image_source": "Blender-derived pixel-level BRDF image v0.4",
  "preprocessing": {
    "log1p_alpha": "<float: e.g. 10.0>",
    "I_scale": "<float: global max I_linear of clean corpus>",
    "input_range": [0.0, 1.0],
    "v_sun_macro_applied": true
  },
  "resolution": 256,
  "records": [
    {
      "record_id": "<string: matches ocs_manifest record_id>",
      "yaw_deg": "<float>",
      "pitch_deg": "<float>",
      "geom_id": "<string>",
      "png_path": "<string>",
      "exr_linear_path": "<string>",
      "is_clean": true,
      "I_scale_record": "<float: record-level I_scale if per-record normalization, else same as global I_scale>"
    }
  ]
}
```

**字段说明**（增量）：

| 字段 | 类型 | 含义 |
|---|---|---|
| `preprocessing.v_sun_macro_applied` | bool | I_linear 是否已乘 V_sun_macro（与 OCS 同源）；与 `visibility_version` 应一致 |
| `record_id` | string | 与 OCS manifest 同 key，确保可对齐审计 |

---

## 三、拆分后的版本字段体系

### 3.1 六版本独立

| 版本字段 | 控制范围 | 变化触发条件 |
|---|---|---|
| `geometry_version` | STL 几何、姿态网格（yaw/pitch）、ortho_scale、resolution | 任一变化 |
| `brdf_version` | BRDF 模型（GGX/LegacyPhong）、材料参数（`_GGX_DB`）、`eps` 值 | 任一变化 |
| `visibility_version` | sun_visibility 层级 + `shadow_mapping_method` | 层级切换或实现方式切换 |
| `ocs_integration_version` | OCS 离散公式、pixel_area 定义、V_sun_macro 处理、边缘像素策略 | 任一变化 |
| `image_preprocess_version` | log1p α、I_scale、量化参数、PNG 编码方式 | 任一变化 |
| `dataset_version` | split 策略、train/val/test 划分、seed | 任一分化 |

### 3.2 总 method_version（CR4-008 修正——改为带字段名短格式）

```text
method_version = "v0.4-g{geometry}-b{brdf}-vis{visibility}-ocs{ocs}-img{image}-ds{dataset}"

例（仅示意格式，不对应任何实际版本号）：
  "v0.4-g1.0-b1.0-vis2.0-ocs1.0-img1.0-ds1.0"
```

- `g` = geometry, `b` = brdf, `vis` = visibility, `ocs` = ocs_integration, `img` = image_preprocess, `ds` = dataset
- 总 `method_version` 仅用于快速标识和打印，**不作为一致性检查的唯一依据**
- 所有一致性检查必须比较各子版本字段（见 §7）

### 3.3 写入位置

- OCS manifest：写入 `geometry_version`, `brdf_version`, `visibility_version`, `ocs_integration_version`
- Image manifest：写入 `geometry_version`, `brdf_version`, `visibility_version`, `image_preprocess_version`
- source_data.json：写入所有用到的子版本
- summary.json：写入 `method_version`（汇总标签）和各子版本

---

## 四、source_data.json 字段 Schema

每个 v0.4 训练/实验 run 的产物目录中必须包含 `source_data.json`：

```json
{
  "run_id": "<string: run_{YYYYMMDD}_{HHMMSS}_{type}>",
  "run_type": "<enum: 'ocs_only' | 'image_only' | 'fusion' | 'supp_exp'>",
  "method_version": "<string: aggregate label, e.g. v0.4-g1.0-b1.0-vis2.0-ocs1.0-img1.0-ds1.0>",
  "versions": {
    "geometry_version": "<string>",
    "brdf_version": "<string>",
    "visibility_version": "<string>",
    "ocs_integration_version": "<string>",
    "image_preprocess_version": "<string>",
    "dataset_version": "<string>"
  },
  "ocs_manifest_path": "<string>",
  "image_manifest_path": "<string>",
  "brdf_model": "ggx_cook_torrance",
  "feature_config": {
    "feature_mode": "<string: e.g. 'per_part_log'>",
    "n_features": "<int>",
    "n_geoms": "<int>",
    "geom_ids": ["<string>", "..."]
  },
  "image_config": {
    "resolution": 256,
    "geom_id": "<string>",
    "log1p_alpha": "<float>",
    "intensity_mode": "log1p",
    "v_sun_macro_applied": true
  },
  "split_config": {
    "split_method": "<enum: 'coarse_to_fine' | 'random'>",
    "split_description": "<string>",
    "split_seed": "<int: actual seed, written by split generation script>",
    "split_id": "<string: 'split_{method}_{seedlabel}_{desc}_v{n}'>",
    "train_ratio": "<float>",
    "n_train": "<int>",
    "n_val": "<int>",
    "n_test": "<int>"
  },
  "model_config": {
    "model_type": "<string>",
    "optimizer": "<string>",
    "learning_rate": "<float>",
    "batch_size": "<int>",
    "epochs": "<int>",
    "patience": "<int>",
    "random_seed": "<int>"
  },
  "output_dir": "<string>"
}
```

**CR4-007 已修正**：
- `split_method` 写为 enum 候选 `'coarse_to_fine' | 'random'`，不在 schema 中写成默认例子
- `split_seed` 为 `<int: actual seed, written by split generation script>`，不含任何具体数字

### 4.1 退化实验扩展字段

```json
{
  "degradation_config": {
    "degradation_type": "<string: 'gaussian_noise' | 'gaussian_blur' | 'downsample' | 'background' | 'starfield'>",
    "degradation_params": { "<param>": "<value>" },
    "degradation_domain": "linear",
    "base_run_id": "<string>"
  }
}
```

---

## 五、run_id / split_id / seed 规则（CR4-007 修正）

### 5.1 run_id

- **格式**：`run_{YYYYMMDD}_{HHMMSS}_{type}`
- **生成规则**：脚本启动时自动生成
- **唯一性**：每个 run 的 run_id 全局唯一

### 5.2 split_id（CR4-007 修正——删除 seed 具体数字示例）

- **格式**：`split_{method}_{seedlabel}_{desc}_v{n}`
  - `{method}`：split 方法标识（如 `ctf` = coarse_to_fine, `rnd` = random）
  - `{seedlabel}`：**实际 seed 的字符串标签，由 split 文件生成时写入，不在本规范中预填**
  - `{desc}`：简短描述
  - `{n}`：split 方案的主版本号
- **唯一性**：不同 split 方案的 split_id 不同
- **存储**：split 文件独立存储（单个 JSON 包含 train/val/test 索引列表），所有实验通过 split_id 引用

### 5.3 seed 规则

- `split_seed`：控制 train/val/test 划分的随机种子
- `model_seed`：控制模型初始化和训练 batch shuffle 的随机种子
- **两者独立**
- 具体值在 split 文件/训练脚本生成时写入 `source_data.json`，不在本规范中预填

### 5.4 禁止伪默认值（CR4-007 强化）

**以下值绝不能在本规范中硬写为具体数字**：

- `split_seed` 的具体值（禁止写任何数字）
- `split_method` 的具体方案（仅 enum 候选，无默认）
- geometries 的具体列表
- 版本号位数的具体值

---

## 六、禁止 Latest-Run 自动发现

### 6.1 规则

v0.4 所有脚本**禁止**使用以下模式：

```python
# 禁止
manifest = sorted(glob.glob(MANIFEST_GLOB), key=os.path.getmtime, reverse=True)[0]
latest_run = max(Path("results").glob("run_*"), key=os.path.getmtime)
```

### 6.2 要求

所有脚本必须**显式传入**数据路径：

```python
parser.add_argument("--ocs-manifest", required=True)
parser.add_argument("--image-manifest", required=True)
parser.add_argument("--split-file", required=True)
parser.add_argument("--output-dir", required=True)
```

- 不设默认值
- 不自动扫描目录
- 不接受 `--auto` 或 `--latest` 等启发式 flag

### 6.3 唯一例外

仅允许汇总/分析脚本（只读已有产物）接受 `--result-dir` 并默认指向 `v0.4_results/`（在仓库级配置文件中定义，不自动发现）。

---

## 七、OCS Source 与 Image Source 一致性规则

### 7.1 核心规则

每次实验/训练必须满足以下所有条件：

```
ocs_manifest.geometry_version    == image_manifest.geometry_version
ocs_manifest.brdf_version        == image_manifest.brdf_version
ocs_manifest.visibility_version  == image_manifest.visibility_version
source_data.brdf_model           == "ggx_cook_torrance"
image_manifest.v_sun_macro_applied == true  (iff visibility_version ≥ level 2)
```

### 7.2 禁止的混用

- ❌ v0.4 OCS + 旧 v0.3 图像
- ❌ v0.4 OCS + v0.4 图像（不同 geometry/brdf/visibility 版本）
- ❌ v0.4 OCS + v0.4 图像（不同 image_preprocess_version，在比较实验中）
- ❌ OCS 含 V_sun_macro + 图像不含 V_sun_macro（同 visibility level 下）

### 7.3 允许的组合

- ✅ OCS multi-geom concat5 + image single-geom phase63（fusion 多几何增强，单独报告）
- ✅ OCS single-geom + image single-geom（公平基线，主表必须包含）
- ✅ 退化实验：clean OCS + degraded image（OCS 不变，图像受退化处理）
- ✅ visibility 版本一致的 OCS/image 组合

---

## 八、每个 Summary / Figure Source Data 必须记录的字段

### 8.1 Summary 文件 (`summary.json`)

```json
{
  "run_id": "<string>",
  "source_data_path": "<string>",
  "method_version": "<string>",
  "versions": {
    "geometry_version": "<string>",
    "brdf_version": "<string>",
    "visibility_version": "<string>",
    "ocs_integration_version": "<string>",
    "image_preprocess_version": "<string>",
    "dataset_version": "<string>"
  },
  "metrics": {
    "mean_error_deg": "<float>",
    "std_error_deg": "<float>",
    "median_error_deg": "<float>",
    "hit_at_5_deg": "<float>",
    "hit_at_10_deg": "<float>",
    "worst_case_deg": "<float>",
    "rmse_deg": "<float>"
  },
  "per_attitude_errors_csv": "<string>",
  "confusion_matrix_csv": "<string>",
  "train_history_csv": "<string>"
}
```

### 8.2 Figure Source Data

```json
{
  "figure_id": "<string>",
  "figure_caption_short": "<string>",
  "data_csv_path": "<string>",
  "run_ids": ["<string>"],
  "method_versions": ["<string>"],
  "generation_script": "<string>",
  "generation_date": "<string>"
}
```

---

## 九、输出目录命名规范（CR4-003 修正——新增 sun shadow / visibility mask 产物）

### 9.1 根目录

```
项目重启_v0.4_BlenderOCS/v0.4_results/
```

### 9.2 目录结构

```text
v0.4_results/
├── 00_geometry_passes/              ← Blender camera-view EXR 原始输出
│   └── {geom_id}/
│       ├── yaw{yyy}_pitch{ppp}_0001.exr   ← camera-view geometry pass (Normal/Depth/IndexOB)
│       └── yaw{yyy}_pitch{ppp}_position.exr  ← Position/WorldCoord pass (CR4-002)
├── 00b_sun_depth_passes/            ← Blender sun-view depth EXR (CR4-002 新增)
│   └── {geom_id}/
│       └── yaw{yyy}_pitch{ppp}_sun_depth.exr
├── 01_sun_shadow_reprojection/      ← Python sun shadow reprojection 产物 (CR4-002 新增)
│   └── {geom_id}/
│       ├── yaw{yyy}_pitch{ppp}_v_sun_macro.png   ← V_sun_macro 可视化
│       ├── yaw{yyy}_pitch{ppp}_v_sun_macro.npy   ← V_sun_macro_mask 数值 (H×W, uint8 0/1)
│       └── sun_shadow_summary.json
├── 02_brdf_postprocess/             ← Python BRDF 后处理
│   └── {geom_id}/
│       ├── ocs_scan_v0.4.csv
│       ├── ocs_scan_v0.4.json
│       ├── brdf_images/
│       │   ├── yaw{yyy}_pitch{ppp}_brdf.png      ← log1p 8-bit PNG
│       │   └── yaw{yyy}_pitch{ppp}_linear.exr    ← I_linear EXR (含 V_sun_macro)
│       └── brdf_postprocess_summary.json
├── 03_manifests/                    ← v0.4 OCS + image manifest
│   ├── ocs_manifest_v0.4.json
│   └── image_manifest_v0.4.json
├── 04_splits/                       ← train/val/test split 文件
│   └── split_{split_id}.json
├── 05_runs/                         ← 各训练 run
│   └── run_{run_id}/
│       ├── source_data.json
│       ├── summary.json
│       ├── config_used.json
│       ├── model_best.pt
│       ├── per_attitude_errors.csv
│       ├── train_history.csv
│       └── figures/
└── 06_figures/                      ← 论文最终用图
    └── fig_{figure_id}/
        ├── figure_source_data.json
        ├── figure.csv
        └── figure.png / figure.pdf
```

### 9.3 路径规则

- **v0.4 内部生成目录和文件名使用 ASCII**（英文字母、数字、下划线、连字符）
- **允许上级工作区路径包含中文**（如 `项目重启_v0.4_BlenderOCS/`），但脚本内部必须使用 `pathlib` / 引号 / UTF-8 编码
- 仓库内引用使用正斜杠 `/` 的相对路径
- 不在文件名和子目录名中使用空格

---

## 十、与 Codex CR3 修正项对应关系

| CR3 编号 | 修正内容 | 本文件对应章节 |
|---|---|---|
| CR3-005 (P1) | 拆分版本字段（6 子版本 + 汇总 method_version） | §3.1, §3.2, §7.1 |
| CR3-008 (P1) | 生成范围分为 single-geom 主线和 multi-geom 扩展两层 | §1.3 |
| CR3-010 (P2) | 输出目录写入 `项目重启_v0.4_BlenderOCS/v0.4_results/` | §9.1, §9.3 |
| CR3-011 (P2) | 删除 split_id 示例中的具体数字 | §5.2, §5.4 |
| CR3-003 (P0) | sun_visibility enum 同步更新为新命名 | §2.1 |

---

## 十一、与 Codex CR4 修正项对应关系

| CR4 编号 | 严重度 | 修正内容 | 本文件对应章节 |
|---|---|---|---|
| CR4-001 | P0 | 图像 preprocess 标注 `v_sun_macro_applied: true`，与 OCS 同源 | §2.2, §4, §7.1 |
| CR4-002 | P0 | （配套见文件 10）sun shadow 数据流可执行定义 | 前向模型文件 §6 |
| CR4-003 | P0 | manifest 增加 shadow pass 路径、重投影参数、camera/sun 矩阵 | §2.1（camera_exr_path, sun_depth_exr_path, sun_visibility_mask_path, position_exr_path, camera_matrix_world, sun_camera_matrix_world, shadow_mapping_method, depth_epsilon_m）, §9.2（新增 00b/01 目录） |
| CR4-004 | P1 | （配套见文件 10）GGX eps 规则 | 前向模型文件 §8.2 |
| CR4-005 | P1 | multi-geom 每 geom 都包含 sun shadow pass + BRDF 后处理 | §1.3（第二层清单） |
| CR4-006 | P1 | record_id + 像素统计四类拆分 | §2.1（record_id, n_pixels_camera_visible, n_pixels_nol_positive, n_pixels_sun_visible, n_pixels_contributing） |
| CR4-007 | P2 | 删除所有 seed 具体数字示例；split_method 写 enum 不写默认例子 | §4（split_config.split_method enum）, §5.2, §5.4 |
| CR4-008 | P2 | method_version 改为带字段名短格式 `v0.4-g{}-b{}-vis{}-ocs{}-img{}-ds{}` | §3.2 |

**CR4 收回状态**：8 项全部在本文件或配套前向模型文件 10 中收回。

---

## 十二、提交 Codex 最终复审清单

**本文件需与 `10_v0.4前向模型冻结规范_最终冻结候选.md` 一并提交最终复审。**

### 12.1 提交文件

```
04_BlenderOCS方法重建/10_v0.4前向模型冻结规范_最终冻结候选.md  ← 方法规范
04_BlenderOCS方法重建/11_v0.4数据与manifest字段规范_最终冻结候选.md  ← 本文件（数据规范）
```

### 12.2 需要 Codex 重点审阅

| 优先级 | 章节 | 审阅要点 |
|---|---|---|
| P0 | §2.1（OCS manifest） | shadow pass 路径和重投影参数字段是否健全 |
| P0 | §2.1（n_pixels 四类） | 像素统计拆分是否覆盖审计需求 |
| P0 | §9.2（目录结构） | 00b/01 新目录是否完整存放 sun shadow 和 V_sun_macro 产物 |
| P1 | §2.2（image manifest） | `v_sun_macro_applied` 字段是否与 OCS 同源 |
| P1 | §3.2（method_version） | 新短格式是否可读、可审计 |
| P1 | §4, §5（split_config, split_id） | 是否已清除所有具体 seed 数字示例 |
| P2 | §1.3（生成范围） | multi-geom 扩展的 shadow/BRDF 生成范围是否完整 |

### 12.3 Codex 审阅后下一步

若 P0/P1 全部收回，进入代码阶段：`05_全链路重跑/00_重跑任务清单.md`。

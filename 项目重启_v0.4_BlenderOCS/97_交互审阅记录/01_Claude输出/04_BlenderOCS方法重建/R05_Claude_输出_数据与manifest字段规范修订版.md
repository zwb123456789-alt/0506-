# 08 v0.4 数据与 Manifest 字段规范（Claude 修订版）

生成时间：2026-06-08
修订基准：Codex 复审意见 CR3-005, CR3-008, CR3-010, CR3-011（`06_Codex复审意见_前向模型冻结规范.md`）
上版文件：`05_v0.4数据与manifest字段规范_Claude.md`（已由本修订版取代）

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

v0.4 生成范围分为两个层次（CR3-008 修正——不把未决实验范围写成已冻结生成范围）：

**第一层：Single-Geometry 主线（主表基线）**

- [ ] Blender geometry pass EXR（2664 姿态 × 1 geom = phase63）
- [ ] Blender sun shadow pass EXR（2664 姿态 × 1 geom）
- [ ] Python BRDF 后处理输出（per-pixel linear EXR + log1p PNG + per-frame OCS JSON）
- [ ] v0.4 OCS manifest（single-geom phase63）
- [ ] v0.4 image manifest（single-geom phase63）
- [ ] v0.4 OCS-only MLP 训练
- [ ] v0.4 image-only ResNet-18 训练
- [ ] v0.4 fusion (concat1) 训练 — single-geom 公平基线
- [ ] v0.4 退化鲁棒实验（noise/blur/downsample/background/starfield）

**第二层：Multi-Geometry 扩展（单独报告）**

- [ ] Blender geometry pass EXR（其余 4 组 sun/det 几何）
- [ ] v0.4 OCS manifest（multi-geom concat5）
- [ ] v0.4 OCS-only MLP（multi-geom concat5）
- [ ] v0.4 fusion（concat5 late fusion）
- [ ] v0.4 补充实验 12b/12c/12f/12g

**数量说明**：2664 = 72 yaw × 37 pitch（不含 360° 重复姿态）。详见前向模型冻结规范修订版 §3.2。

---

## 二、Manifest 字段 Schema

### 2.1 OCS Manifest (`ocs_manifest_v0.4.json`)

```json
{
  "geometry_version": "<string: e.g. '1.0'>",
  "brdf_version": "<string: e.g. '1.0'>",
  "visibility_version": "<string: e.g. '1.0'>",
  "ocs_integration_version": "<string: e.g. '1.0'>",
  "ocs_source": "Blender-derived pixel-level OCS v0.4",
  "brdf_model": "ggx_cook_torrance",
  "sampling": "Blender Cycles orthogonal projection, 256x256",
  "ortho_scale_m": "<float>",
  "pixel_area_m2": "<float>",
  "resolution": 256,
  "sun_visibility": "<enum: 'camera_visible_nol' | 'camera_visible_nol_plus_sun_shadow_pass' | 'camera_visible_nol_plus_python_raycast'>",
  "records": [
    {
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
      "n_pixels_total": "<int>",
      "n_pixels_per_part": {
        "jinshuzhuti": "<int>",
        "taiyangnengban": "<int>",
        "yinshenban": "<int>"
      },
      "exr_path": "<string: relative to v0.4 data root>",
      "png_path": "<string: relative to v0.4 data root>"
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 含义 |
|---|---|---|
| `geometry_version` | string | 几何/姿态/采样参数版本。STL、yaw/pitch 网格、ortho_scale、resolution 变化时递增 |
| `brdf_version` | string | BRDF 模型与材料参数版本。BRDF 公式或 `_GGX_DB` 参数变化时递增 |
| `visibility_version` | string | 可见性/遮挡定义版本。sun_visibility 层级变化时递增 |
| `ocs_integration_version` | string | OCS 积分公式版本。离散化方法、pixel_area 定义、V_sun_macro 处理变化时递增 |
| `ocs_source` | string | 固定值 |
| `brdf_model` | string | 固定值 `"ggx_cook_torrance"` |
| `sun_visibility` | enum | 见前向模型冻结规范修订版 §6.1。三值之一 |
| `ocs_total` | float | 总 OCS（三部件积分和） |
| `ocs_per_part` | {string: float} | per-part OCS |
| `n_pixels_total` | int | 总可见像素数 |
| `n_pixels_per_part` | {string: int} | per-part 可见像素数 |
| `exr_path` | string | 对应原始 EXR 的相对路径 |
| `png_path` | string | 对应 log1p PNG 的相对路径 |

### 2.2 Image Manifest (`image_manifest_v0.4.json`)

```json
{
  "geometry_version": "<string>",
  "brdf_version": "<string>",
  "visibility_version": "<string>",
  "image_preprocess_version": "<string: e.g. '1.0'>",
  "image_source": "Blender-derived pixel-level BRDF image v0.4",
  "preprocessing": {
    "log1p_alpha": "<float: e.g. 10.0>",
    "I_scale": "<float: global max I_linear of clean corpus>",
    "input_range": [0.0, 1.0]
  },
  "resolution": 256,
  "records": [
    {
      "yaw_deg": "<float>",
      "pitch_deg": "<float>",
      "geom_id": "<string>",
      "png_path": "<string>",
      "exr_linear_path": "<string>",
      "is_clean": true
    }
  ]
}
```

**字段说明**（增量）：

| 字段 | 类型 | 含义 |
|---|---|---|
| `image_preprocess_version` | string | log1p α、I_scale、量化参数版本 |
| `preprocessing.log1p_alpha` | float | log1p 变换系数 α（初始默认 10.0） |
| `preprocessing.I_scale` | float | 全局 radiance 归一化常数 |

---

## 三、拆分后的版本字段体系（CR3-005 修正）

### 3.1 六版本独立

| 版本字段 | 控制范围 | 变化触发条件 |
|---|---|---|
| `geometry_version` | STL 几何、姿态网格（yaw/pitch）、ortho_scale、resolution | 任一变化 |
| `brdf_version` | BRDF 模型（GGX/LegacyPhong）、材料参数（`_GGX_DB`） | 任一变化 |
| `visibility_version` | sun_visibility 层级（`camera_visible_nol` / `_plus_sun_shadow_pass` / `_plus_python_raycast`） | 层级切换 |
| `ocs_integration_version` | OCS 离散公式、pixel_area 定义、V_sun_macro 处理、边缘像素策略 | 任一变化 |
| `image_preprocess_version` | log1p α、I_scale、量化参数、PNG 编码方式 | 任一变化 |
| `dataset_version` | split 策略、train/val/test 划分、seed | 任一分化 |

### 3.2 总 method_version（保留但仅作汇总标签）

```text
method_version = "v0.4-{geometry}.{brdf}.{visibility}.{ocs}.{image}.{dataset}"
例："v0.4-1.0.1.0.1.0.1.0.1.0"
```

- 总 `method_version` 仅用于快速标识和打印，**不作为一致性检查的唯一依据**
- 所有一致性检查必须比较各子版本字段（见 §6）

### 3.3 写入位置

- manifest 文件：写入相关子版本（OCS manifest 不含 `image_preprocess_version` 和 `dataset_version`；image manifest 不含 `ocs_integration_version`）
- source_data.json：写入所有用到的子版本
- summary.json：写入 `method_version`（汇总标签）和各子版本

---

## 四、source_data.json 字段 Schema

每个 v0.4 训练/实验 run 的产物目录中必须包含 `source_data.json`：

```json
{
  "run_id": "<string: run_{YYYYMMDD}_{HHMMSS}_{type}>",
  "run_type": "<enum: 'ocs_only' | 'image_only' | 'fusion' | 'supp_exp'>",
  "method_version": "<string: aggregate label>",
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
    "intensity_mode": "log1p"
  },
  "split_config": {
    "split_method": "<string: e.g. 'coarse_to_fine'>",
    "split_description": "<string>",
    "split_seed": "<int>",
    "split_id": "<string: e.g. 'split_{method}_{seedlabel}_{desc}_v{n}'>",
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

**CR3-011 已修正**：`split_id` 示例改为格式模板 `split_{method}_{seedlabel}_{desc}_v{n}`，不再含具体数字。

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

## 五、run_id / split_id / seed 规则

### 5.1 run_id

- **格式**：`run_{YYYYMMDD}_{HHMMSS}_{type}`
- **生成规则**：脚本启动时自动生成
- **唯一性**：每个 run 的 run_id 全局唯一

### 5.2 split_id

- **格式**：`split_{method}_{seedlabel}_{desc}_v{n}`
  - `{seedlabel}` = 实际 seed 值（如 `42`），由 split 文件生成时写入
  - `{n}` = split 方案的主版本号（同 method 不同 seed 时递增）
- **唯一性**：不同 split 方案的 split_id 不同
- **存储**：split 文件独立存储（单个 JSON 包含 train/val/test 索引列表），所有实验通过 split_id 引用

### 5.3 seed 规则

- `split_seed`：控制 train/val/test 划分的随机种子
- `model_seed`：控制模型初始化和训练 batch shuffle 的随机种子
- **两者独立**
- 具体值在 split 文件/训练脚本生成时写入 `source_data.json`，不在本规范中预填

### 5.4 禁止伪默认值（CR3-011）

**以下值绝不能在本规范中硬写为具体数字**：

- `split_seed` 的具体值（禁止写 `42` 或任何数字）
- `split_method` 的具体方案
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

### 7.1 核心规则（CR3-005 细化）

每次实验/训练必须满足以下所有条件：

```
ocs_manifest.geometry_version  == image_manifest.geometry_version
ocs_manifest.brdf_version      == image_manifest.brdf_version
ocs_manifest.visibility_version == image_manifest.visibility_version
source_data.brdf_model          == "ggx_cook_torrance"
```

### 7.2 禁止的混用

- ❌ v0.4 OCS + 旧 v0.3 图像
- ❌ v0.4 OCS + v0.4 图像（不同 geometry/brdf/visibility 版本）
- ❌ v0.4 OCS + v0.4 图像（不同 image_preprocess_version，在比较实验中）

### 7.3 允许的组合

- ✅ OCS multi-geom concat5 + image single-geom phase63（fusion 多几何增强，单独报告）
- ✅ OCS single-geom + image single-geom（公平基线，主表必须包含）
- ✅ 退化实验：clean OCS + degraded image（OCS 不变，图像受退化处理）

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

## 九、输出目录命名规范（CR3-010 已修正）

### 9.1 根目录

```
项目重启_v0.4_BlenderOCS/v0.4_results/
```

### 9.2 目录结构

```text
v0.4_results/
├── 00_geometry_passes/           ← Blender EXR 原始输出
│   └── {geom_id}/
│       └── yaw{yyy}_pitch{ppp}_0001.exr
├── 01_brdf_postprocess/          ← Python BRDF 后处理
│   └── {geom_id}/
│       ├── ocs_scan_v0.4.csv
│       ├── ocs_scan_v0.4.json
│       ├── brdf_images/
│       │   ├── yaw{yyy}_pitch{ppp}_brdf.png     ← log1p 8-bit PNG
│       │   └── yaw{yyy}_pitch{ppp}_linear.exr   ← 线性 EXR
│       └── brdf_postprocess_summary.json
├── 02_manifests/                 ← v0.4 OCS + image manifest
│   ├── ocs_manifest_v0.4.json
│   └── image_manifest_v0.4.json
├── 03_splits/                    ← train/val/test split 文件
│   └── split_{split_id}.json
├── 04_runs/                      ← 各训练 run
│   └── run_{run_id}/
│       ├── source_data.json
│       ├── summary.json
│       ├── config_used.json
│       ├── model_best.pt
│       ├── per_attitude_errors.csv
│       ├── train_history.csv
│       └── figures/
└── 05_figures/                   ← 论文最终用图
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

## 十、已收回的 C1-C2 决策表

| # | 问题 | 冻结决策 | 来源 |
|---|---|---|---|
| C1 | seed 占位/示例 | 不在规范中填任何具体 seed 值；`split_id` 示例改为格式模板 `split_{method}_{seedlabel}_{desc}_v{n}`；实际 seed 仅在 split 文件生成时写入 | CR3-011 |
| C2 | 输出目录 | 放在 `项目重启_v0.4_BlenderOCS/v0.4_results/` | CR3-010 |

---

## 十一、与 Codex CR3 修正项对应关系

| CR3 编号 | 修正内容 | 本文件对应章节 |
|---|---|---|
| CR3-005 (P1) | 拆分版本字段（6 子版本 + 汇总 method_version） | §3.1, §3.2, §7.1 |
| CR3-008 (P1) | 生成范围分为 single-geom 主线和 multi-geom 扩展两层 | §1.3 |
| CR3-010 (P2) | 输出目录写入 `项目重启_v0.4_BlenderOCS/v0.4_results/`；路径规则改为 ASCII 生成目录 | §9.1, §9.3 |
| CR3-011 (P2) | 删除 split_id 示例中的 `42`，改为格式模板 | §5.2, §5.4 |
| CR3-003 (P0) | sun_visibility enum 同步更新为新命名 | §2.1 |

---

## 十二、提交 Codex 复审清单

**本文件需再次提交 Codex 复审**（与 `07_v0.4前向模型冻结规范_Claude修订版.md` 一并提交）。

### 12.1 提交文件

```
04_BlenderOCS方法重建/07_v0.4前向模型冻结规范_Claude修订版.md  ← 方法规范
04_BlenderOCS方法重建/08_v0.4数据与manifest字段规范_Claude修订版.md  ← 本文件（数据规范）
```

### 12.2 需要 Codex 重点审阅

| 优先级 | 章节 | 审阅要点 |
|---|---|---|
| P0 | §3.1 (六版本拆分) | 拆法是否合理，有无遗漏或过度拆分 |
| P0 | §7.1 (一致性规则) | 基于子版本的一致性检查是否充分 |
| P1 | §1.3 (两层生成范围) | single-geom 主线 vs multi-geom 扩展的划分是否合理 |
| P1 | §2.1, §2.2 (manifest schema) | 子版本字段是否完整 |
| P2 | §9 (输出目录) | 目录结构是否满足 OCS-only / image-only / fusion 分开放置的需求 |

### 12.3 Codex 审阅后下一步

两份修订版全部收回后，进入代码阶段：`05_全链路重跑/00_重跑任务清单.md`

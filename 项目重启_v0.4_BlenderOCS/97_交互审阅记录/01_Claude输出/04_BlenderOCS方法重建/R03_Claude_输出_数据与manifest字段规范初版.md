# 05 v0.4 数据与 Manifest 字段规范（Claude 生成）

生成时间：2026-06-08
输入来源：
- `04_BlenderOCS方法重建/04_v0.4前向模型冻结规范_Claude.md`（同步生成）
- `03_全项目排查/07_相似方法坑专项排查报告_Claude.md`
- `03_全项目排查/08_Codex复审意见_相似方法坑专项排查.md`（CR2-004, CR2-006, CR2-007 已吸收）
- `03_全项目排查/06_方法思路类坑位与处置汇总_Codex.md`
- `04_BlenderOCS方法重建/03_v0.4前向模型冻结问题清单_Claude.md`
- `98_外部材料备份/03_关键代码快照/03_inversion/train_cnn.py`
- `98_外部材料备份/04_关键诊断与结果快照/old_multi_geom_manifest_20260527.json`

---

## 一、v0.4 旧结果全封存，所有主结果重跑

### 1.1 封存原则

v0.3 Acta/ASR 主投优先稿及所有关联实验产物全部封存，不进入 v0.4 主结果。封存范围：

| 类别 | 封存内容 | 说明 |
|---|---|---|
| OCS 数据 | 旧模块 A `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/` 下的所有 `ocs_scan.csv`、`ocs_scan.json` | face-center 采样，已禁用 |
| 图像数据 | 旧模块 B `结果/模块B_渲染/` 下的所有 EXR/PNG（gamma 2.2 编码） | 图像响应链不一致，已禁用 |
| 反演结果 | 所有 v0.3 的 OCS-only / image-only / fusion 训练产物 | 基于旧 OCS 和旧 split，不可比较 |
| 补充实验结果 | 所有 12b/12c/12f/12g 以及实验 1-12g 的旧输出 | 基于旧数据链 |
| 论文稿件 | v0.3 主稿及变体 | 已封存，不作为投稿基础 |
| 汇报材料 | 0603 汇报 PDF | 保留作为历史记录，但口径不再适用 |

### 1.2 旧材料的三项仅限用途

1. 作为历史证据（为什么 v0.3 封存）
2. 作为诊断材料（帮助发现类似坑）
3. 作为方法/代码结构参考（旧 `brdf_models.py` 可复用，旧反演训练框架可参考）

### 1.3 v0.4 重新生成范围

以下产物必须从 v0.4 Blender-derived OCS manifest 重新生成：

- [ ] v0.4 Blender geometry pass EXR（2701 帧 × 5 geom）
- [ ] v0.4 Python BRDF 后处理输出（per-pixel linear EXR + log1p PNG + per-frame OCS JSON）
- [ ] v0.4 OCS manifest（`ocs_scan_v0.4.csv` / `.json`）
- [ ] v0.4 image manifest（PNG 路径、几何配置、预处理参数）
- [ ] v0.4 OCS-only MLP 训练（all feature modes）
- [ ] v0.4 image-only ResNet-18 训练
- [ ] v0.4 fusion (concat5 late fusion) 训练
- [ ] v0.4 退化鲁棒实验（noise/blur/downsample/background/starfield）
- [ ] v0.4 补充实验 12b/12c/12f/12g

---

## 二、Manifest 字段 Schema

### 2.1 OCS Manifest (`ocs_manifest_v0.4.json`)

每个姿态入口一行（或一个 JSON record）：

```json
{
  "v0.4_method_version": "<string>",
  "ocs_source": "<string: 'Blender-derived pixel-level OCS v0.4'>",
  "brdf_model": "<string: 'ggx_cook_torrance'>",
  "sampling": "<string: 'Blender Cycles orthogonal projection, 256x256'>",
  "ortho_scale_m": "<float>",
  "pixel_area_m2": "<float>",
  "resolution": "<int>",
  "sun_visibility": "<string: one of 'camera_only' | 'camera_plus_sun_shadow_pass' | 'camera_plus_python_raycast'>",
  "records": [
    {
      "yaw_deg": "<float>",
      "pitch_deg": "<float>",
      "geom_id": "<string: identifying sun/det geometry label, e.g. 'phase24'>",
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
| `v0.4_method_version` | string | 方法版本号，初始为 `"1.0"`；每次方法冻结规范更新后递增 |
| `ocs_source` | string | 固定值，标识数据来源 |
| `brdf_model` | string | 固定值 `"ggx_cook_torrance"` |
| `sampling` | string | 采样方式描述 |
| `ortho_scale_m` | float | 正交投影尺度（米），从 Blender 渲染脚本读入 |
| `pixel_area_m2` | float | 常数投影像素面积（米²），= (ortho_scale/resolution)² |
| `resolution` | int | 渲染分辨率（像素） |
| `sun_visibility` | enum | 见前向模型冻结规范 §6 |
| `yaw_deg` | float | Yaw 角度（°） |
| `pitch_deg` | float | Pitch 角度（°） |
| `geom_id` | string | 观测几何标识符 |
| `sun_dir` | [float, float, float] | 归一化太阳方向向量 |
| `det_dir` | [float, float, float] | 归一化探测器方向向量 |
| `ocs_total` | float | 总 OCS（三部件积分和） |
| `ocs_per_part` | {string: float} | per-part OCS，键名为部件名 |
| `n_pixels_total` | int | 总可见像素数 |
| `n_pixels_per_part` | {string: int} | per-part 可见像素数 |
| `exr_path` | string | 对应原始 EXR 的相对路径 |
| `png_path` | string | 对应 log1p PNG 的相对路径 |

### 2.2 Image Manifest (`image_manifest_v0.4.json`)

```json
{
  "v0.4_method_version": "<string>",
  "image_source": "<string: 'Blender-derived pixel-level BRDF image v0.4'>",
  "preprocessing": {
    "log1p_alpha": "<float: e.g. 10.0>",
    "I_max_global": "<float>",
    "input_range": "[0.0, 1.0]"
  },
  "resolution": "<int>",
  "records": [
    {
      "yaw_deg": "<float>",
      "pitch_deg": "<float>",
      "geom_id": "<string>",
      "png_path": "<string>",
      "exr_linear_path": "<string>",
      "is_clean": "<bool>"
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 含义 |
|---|---|---|
| `preprocessing.log1p_alpha` | float | log1p 变换系数 α |
| `preprocessing.I_max_global` | float | 全局 radiance 归一化常数 |
| `preprocessing.input_range` | [float, float] | 训练输入值范围 |
| `png_path` | string | 训练用 PNG 路径（log1p 8-bit） |
| `exr_linear_path` | string | 原始线性 EXR 路径（存档用） |
| `is_clean` | bool | 是否为干净图像（退化版本设 false） |

---

## 三、source_data.json 字段 Schema

每个 v0.4 训练/实验 run 的产物目录中必须包含 `source_data.json`：

```json
{
  "run_id": "<string: ISO timestamp or UUID>",
  "run_type": "<string: one of 'ocs_only' | 'image_only' | 'fusion' | 'supp_exp'>",
  "v0.4_method_version": "<string, inherited from manifest>",
  "ocs_manifest_path": "<string: absolute or repo-relative path to ocs_manifest_v0.4.json>",
  "image_manifest_path": "<string: absolute or repo-relative path>",
  "brdf_model": "ggx_cook_torrance",
  "feature_config": {
    "feature_mode": "<string: e.g. 'per_part_log'>",
    "n_features": "<int>",
    "n_geoms": "<int: number of sun/det geometries concatenated>",
    "geom_ids": ["<string>", "..."]
  },
  "image_config": {
    "resolution": "<int>",
    "geom_id": "<string: which geometry's images are used>",
    "log1p_alpha": "<float>",
    "intensity_mode": "log1p"
  },
  "split_config": {
    "split_method": "<string: e.g. 'coarse_to_fine'>",
    "split_description": "<string: human-readable, e.g. 'train on 10deg grid, test on 5deg grid'>",
    "split_seed": "<int>",
    "split_id": "<string: unique identifier for this split file>",
    "train_ratio": "<float: fraction of train split used for training, e.g. 0.8>",
    "n_train": "<int>",
    "n_val": "<int>",
    "n_test": "<int>"
  },
  "model_config": {
    "model_type": "<string: e.g. 'resnet18' | 'mlp' | 'fusion_concat5'>",
    "optimizer": "<string>",
    "learning_rate": "<float>",
    "batch_size": "<int>",
    "epochs": "<int>",
    "patience": "<int>",
    "random_seed": "<int>"
  },
  "output_dir": "<string: path to this run's output directory>",
  "parent_manifest_or_config_hash": "<string: SHA256 or similar, for reproducibility tracing>"
}
```

**CR2-006 要求**：以上 schema 中的所有 `<...>` 值是字段占位说明，不代表实际运行时的值。实际 `source_data.json` 仅在实际 run 时生成，填入当次 run 的真实参数。

### 3.1 退化实验扩展字段

对于退化实验，`source_data.json` 额外增加：

```json
{
  "degradation_config": {
    "degradation_type": "<string: e.g. 'gaussian_noise' | 'gaussian_blur' | 'downsample' | 'background' | 'starfield'>",
    "degradation_params": {
      "<param_name>": "<value>"
    },
    "degradation_domain": "linear",
    "base_run_id": "<string: run_id of the clean model or data used as baseline>"
  }
}
```

---

## 四、run_id / method_version / split_id / seed 规则

### 4.1 run_id

- **格式**：`run_{YYYYMMDD}_{HHMMSS}_{type}`，如 `run_20260608_143022_ocs_only`
- **生成规则**：脚本启动时自动生成，写入 `source_data.json` 和输出目录名
- **唯一性**：每个 run 的 run_id 全局唯一

### 4.2 method_version

- **格式**：`"M.N"`（如 `"1.0"`）
- **递增规则**：
  - 主版本号 (M)：前向模型冻结规范发生不向后兼容的变化时递增（如修改 BRDF、修改 OCS 积分公式、修改可见性定义）
  - 次版本号 (N)：仅影响预处理参数、log1p α、训练超参等非结构性变化时递增
- **写入位置**：manifest、source_data.json、所有 summary CSV/JSON

### 4.3 split_id

- **格式**：`split_{method}_{seed}_{train_desc}_v{major}`
  - 例：`split_coarse_to_fine_42_10deg_train_v1`
- **唯一性**：不同 split 方案的 split_id 不同
- **存储**：split 文件独立存储（单个 JSON 包含 train/val/test 的 yaw-pitch-geom_id 索引列表），所有实验通过 split_id 引用

### 4.4 seed 规则

- `split_seed`：控制 train/val/test 划分的随机种子
- `model_seed`：控制模型初始化和训练 batch shuffle 的随机种子
- **两者独立**：允许使用同一 split 但不同 model seed 做 ensemble 或多轮训练
- **v0.4 默认**：split_seed 和 model_seed 均需在 source_data.json 中显式记录；具体值由 v0.4 重跑时确定并在 source_data.json 中写实值（不在此规范中预填）

### 4.5 禁止伪默认值

**以下值不能在规范中硬写为已冻结事实**（CR2-006）：
- `split_seed` 的具体数值
- `split_method` 的具体方案
- geometries 的具体列表
- 以上均由 v0.4 重跑阶段决策并在实际 `source_data.json` 中写实值

---

## 五、禁止 Latest-Run 自动发现

### 5.1 规则

v0.4 所有脚本**禁止**使用以下模式自动定位数据源：

```python
# 禁止：
manifest = sorted(glob.glob(MANIFEST_GLOB), key=os.path.getmtime, reverse=True)[0]

# 禁止：
latest_run = max(Path("results").glob("run_*"), key=os.path.getmtime)
```

### 5.2 要求

所有脚本必须**显式传入**数据路径：

```python
# 要求：
parser.add_argument("--ocs-manifest", required=True, help="Path to ocs_manifest_v0.4.json")
parser.add_argument("--image-manifest", required=True, help="Path to image_manifest_v0.4.json")
parser.add_argument("--split-file", required=True, help="Path to split JSON file")
parser.add_argument("--output-dir", required=True, help="Path to output directory for this run")
```

- 不设默认值
- 不自动扫描目录
- 不接受 `--auto` 或 `--latest` 等启发式 flag

### 5.3 唯一例外

仅允许在**汇总/分析脚本**（不生成新数据、只读取已有产物）中接受 `--result-dir` 参数并默认指向明确的 v0.4 结果根目录（在配置文件中定义，不自动发现）。

---

## 六、OCS Source 与 Image Source 一致性规则

### 6.1 核心规则

每次实验/训练的 OCS source 和 image source 必须来自**同一 v0.4 前向模型版本**：

```
(source_data.ocs_manifest_path 的 method_version)
    ==
(source_data.image_manifest_path 的 method_version)
```

### 6.2 禁止的混用

- ❌ v0.4 OCS + 旧 v0.3 图像
- ❌ v0.4 OCS + v0.4 图像（但不同 method_version）
- ❌ v0.4 OCS + v0.4 图像（但不同 log1p α / I_max_global）
- ❌ v0.4 OCS from geom A + v0.4 image from geom B（在非 multi-geom 主实验中）

### 6.3 允许的组合

- ✅ OCS multi-geom concat5 + image single-geom phase63（当前 fusion 配置，但需在论文中讨论信息量不对称，见前向模型冻结规范 §12 D2）
- ✅ OCS single-geom (phase63) + image single-geom (phase63)（更公平的 baseline）
- ✅ 退化实验在 clean OCS + degraded image 上运行（OCS 本身不变，图像受退化处理）

### 6.4 一致性验证

每个训练脚本启动时检查：

```
assert ocs_manifest["v0.4_method_version"] == image_manifest["v0.4_method_version"]
assert ocs_manifest["brdf_model"] == source_data["brdf_model"]
```

---

## 七、每个 Summary / Figure Source Data 必须记录的字段

### 7.1 Summary 文件 (`summary.json`)

每个实验 run 的输出目录中必须包含 `summary.json`：

```json
{
  "run_id": "<string>",
  "source_data_path": "<string: path to source_data.json for this run>",
  "method_version": "<string>",
  "metrics": {
    "mean_error_deg": "<float>",
    "std_error_deg": "<float>",
    "median_error_deg": "<float>",
    "hit_at_5_deg": "<float: ratio 0-1>",
    "hit_at_10_deg": "<float: ratio 0-1>",
    "worst_case_deg": "<float>",
    "rmse_deg": "<float>"
  },
  "per_attitude_errors_csv": "<string: path to per-sample error CSV>",
  "confusion_matrix_csv": "<string: path>",
  "train_history_csv": "<string: path to epoch-level loss/val curves>"
}
```

### 7.2 Figure Source Data

每张论文图表的源数据必须以独立 CSV/JSON 存储：

```json
{
  "figure_id": "<string: e.g. 'fig4a'>",
  "figure_caption_short": "<string>",
  "data_csv_path": "<string>",
  "run_ids": ["<string: list of run_ids used to produce this figure>"],
  "method_versions": ["<string>"],
  "generation_script": "<string: path to script that produced this figure>",
  "generation_date": "<string: ISO date>"
}
```

**要求**：
- 每个 figure → 一个 source data index JSON
- 每条曲线/bar → CSV 中的一列
- CSV 的列名直接对应图例标签
- 不依赖口头记忆或"大概记得是从哪个 run 来的"

---

## 八、输出目录命名规范

### 8.1 目录结构

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
│       ├── config_used.json      ← 完整命令行参数快照
│       ├── model_best.pt
│       ├── per_attitude_errors.csv
│       ├── train_history.csv
│       └── figures/              ← 此 run 生成的图表
└── 05_figures/                   ← 论文最终用图汇总
    └── fig_{figure_id}/
        ├── figure_source_data.json
        ├── figure.csv
        └── figure.png / figure.pdf
```

### 8.2 路径规则

- 所有路径使用正斜杠 `/`
- 仓库内路径使用相对路径（相对于 v0.4 工作区根目录）
- 绝对路径仅在 `source_data.json` 的 `output_dir` 中使用
- 不在路径中包含空格或中文

---

## 九、提交 Codex 审阅清单

**本文件需提交 Codex 审阅**（与 `04_v0.4前向模型冻结规范_Claude.md` 一并提交）。

### 9.1 提交文件

```
04_BlenderOCS方法重建/04_v0.4前向模型冻结规范_Claude.md  ← 方法规范
04_BlenderOCS方法重建/05_v0.4数据与manifest字段规范_Claude.md  ← 本文件（数据规范）
```

### 9.2 需要 Codex 重点审阅的章节

| 优先级 | 章节 | 审阅要点 |
|---|---|---|
| P0 | §2 (manifest schema) | OCS/image manifest 字段是否覆盖了反演代码需要读取的所有字段 |
| P0 | §3 (source_data.json schema) | 是否满足完全可复现性要求；退化实验扩展字段是否充分 |
| P1 | §4 (run_id/seed/split_id 规则) | split 文件格式与 split_id 命名规则是否合理 |
| P1 | §6 (OCS/image source 一致性) | 一致性检查规则是否充分，有无遗漏的混用场景 |
| P2 | §5 (禁止 latest-run) | 是否彻底排除了自动发现路径 |
| P2 | §7 (summary/figure source data) | metrics 字段是否覆盖所有论文需要报告的指标；figure source data 格式是否满足期刊 data availability |
| P2 | §8 (输出目录结构) | 是否合理，是否需要 OCS-only/image-only/fusion 子目录分开 |

### 9.3 需要 Codex 给出决策的问题

| # | 问题 | 当前状态 | 需要 Codex 做的 |
|---|---|---|---|
| C1 | split 策略和 seed 的具体值 | §4.5 明确规定不在此预填 | 确认规范中的占位策略是否正确（实际上给出了 split_id 格式示例 `split_coarse_to_fine_42_10deg_train_v1`，但这仅是格式示例——42 本身是否应被理解为推荐值需要确认） |
| C2 | 输出目录结构中 `v0.4_results/` 的绝对路径位置 | 未指定 | 给出推荐（如 `项目重启_v0.4_BlenderOCS/v0.4_results/` 或独立目录） |

### 9.4 Codex 审阅后下一步

Codex 审阅通过后：
1. 根据 Codex 意见更新本文件
2. 与 `04_v0.4前向模型冻结规范_Claude.md` 的 D1-D8 决策一并收回
3. 进入代码阶段

---

## 十、与 Codex 复审意见的对应关系

| Codex ID | 内容 | 本文件中的处置 |
|---|---|---|
| CR2-004 | 禁止 latest-run 自动发现 | §5 |
| CR2-006 | source_data.json 只写 schema，不填伪默认值 | §3（所有 `<...>` 为 schema 占位）、§4.5 |
| CR2-007 | H5 归类为遮挡/方法解释 | 不直接出现在本文件（已在前向模型冻结规范 §13 处置） |
| CR2-008 | bibliography 占位移到论文管理清单 | 不进入方法冻结文件 |

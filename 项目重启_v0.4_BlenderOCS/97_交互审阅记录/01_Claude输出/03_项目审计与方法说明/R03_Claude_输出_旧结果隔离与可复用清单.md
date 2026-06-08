# 旧结果隔离与可复用清单（Claude 审计生成）

生成时间：2026-06-08

## 一、三类处置

| 类别 | 标签 | 处置原则 |
|---|---|---|
| **禁止复用** | 🚫 | 旧 OCS 数值、旧 fusion 结果、所有依赖旧模块 A OCS 的反演数字和图表，禁止进入 v0.4 |
| **历史对比** | 📋 | 可作为分支差异说明、A/B 审计材料，但不能作为 v0.4 正式结果 |
| **可复用** | ✅ | 代码框架、论文结构、图表布局、材料库、BRDF 公式、图像渲染链路等不依赖 OCS 采样的部分 |

---

## 二、禁止复用清单 🚫

### 2.1 数字/数值锚点

| 禁用的数字 | 来源 | 禁止原因 |
|---|---|---|
| OCS MLP per_part_log 30D: **5.91±0.22°** | 旧模块 A face-center OCS | 旧 OCS 采样方式不同 |
| OCS MLP all_raw 45D: **5.91±0.22°** | 同上 | 同上 |
| OCS kNN: 旧值 | 同上 | 同上 |
| feature fusion (concat5): **1.47±0.07°** | 旧 OCS + 旧图像 | OCS 特征来自旧采样 |
| feature fusion Hit@5°: **99.7%** | 同上 | 同上 |
| feature fusion worst-case: **6.6°** | 同上 | 同上 |
| late fusion: 旧值 | 同上 | 同上 |
| fusion noise σ=0.01: **73.36°** | 同上 | 同上 |
| fusion noise σ=0.10: **73.57°** | 同上 | 同上 |
| U1 aug fusion clean: **1.95±0.21°** | 同上 | 同上 |
| U1 aug fusion noise σ=0.10: **2.31±0.26°** | 同上 | 同上 |
| U1 worst-case: **164° outliers** | 同上 | 同上 |
| image-masked ~30°（12b） | 旧 OCS + image-masking | OCS 特征来自旧采样 |
| combined_severe ~13.88°（12c） | 旧 OCS fusion | 同上 |
| beta sweep 全部数据点（12f） | 旧 OCS | 同上 |
| outlier gallery 统计（12g） | 来源旧 12b | 间接依赖 |
| phase120 ~80°（12d 的 fusion 结果） | 旧 OCS fusion | 同上 |

### 2.2 图表 / source data

| 禁用的图表/数据 | 路径 | 禁止原因 |
|---|---|---|
| Fig.3a-c per-part OCS heatmap | v0.3 稿件 Fig.3 | 数据源为旧 `ocs_scan.csv` |
| Fig.3d 遮挡率 heatmap | v0.3 稿件 Fig.3 | 数据源为旧 OCS 遮挡计算 |
| Fig.4 OCS-only bars | v0.3 稿件 Fig.4 | 数值来自旧 OCS |
| Fig.5 fusion bars | v0.3 稿件 Fig.5 | 数值来自旧 OCS 特征 |
| Fig.6 degradation bars (OCS/fusion 部分) | v0.3 稿件 Fig.6 | 同上 |
| Fig.7 degradation detail (fusion 部分) | v0.3 稿件 Fig.7 | 同上 |
| 所有 Supplementary Figures 含 OCS/fusion 的 | v0.3 稿件 | 同上 |
| 所有旧 source data CSV/JSON | `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/` | 全部为旧 face-center OCS |
| 旧 `ocs_scan.csv` 的全部内容 | `结果/模块A_重构/.../ocs_scan.csv` | 禁止作为 v0.4 的特征输入 |
| 旧 `multi_geom_manifest.json` | `结果/模块A_重构/.../multi_geom_manifest.json` | 指向旧 OCS 文件 |

### 2.3 旧实验输出（整包禁止复用）

| 目录 | 内容 | 处理方式 |
|---|---|---|
| `结果/模块A_重构/` | 全部旧 OCS 扫描产物 | 封存，不读入 v0.4 反演链路 |
| `论文改进/补充实验/结果/` | 旧补充实验 1-12g 全部结果 | 封存 |
| `结果/模块C_反演/` | 旧反演实验结果 | 封存 |
| `论文改进/论文写作/03_投稿定稿/manuscript_md/主稿_v0.3_Acta_ASR润色版.md` | v0.3 稿件全部数值 | 封存，仅保留结构参考 |
| `结果/BRDF验证/` | 旧三端闭合验证（单平板/立方体/L型） | 封存：验证结论有效（证明 face-center 在凸几何下闭合），但数值本身是旧采样 |

---

## 三、历史对比清单 📋

### 3.1 可作为分支原因说明的材料

| 材料 | 用途 | 使用场景 | 限制 |
|---|---|---|---|
| `20260528_ocs_comparison.csv` | 说明旧模块 A 与新 Blender-derived OCS 的差异证据 | v0.4 方法部分或补充材料中解释"为什么需要统一前向模型" | 只能作为差异说明，不能作为 v0.4 结果 |
| `subface_adaptive_comparison.csv` | 说明 face-center vs adaptive subface 的差异量级 | 同上 | 同上 |
| `20260528_brdf_postprocess_summary.json` | 记录旧 BRDF postprocess 配置和 A/B 差异统计 | 同上 | 同上 |
| `进度档案_仿真与反演_full.md` | 记录项目历史上所有分支和技术决策 | v0.4 Introduction 或 Discussion 的"why we rebuilt the OCS pipeline"段落 | 不能直接引用其中的旧数值 |

### 3.2 可作为 v0.4 对比基准的材料

| 材料 | 对比方式 | 注意事项 |
|---|---|---|
| 旧 OCS-only 5.91° | 与新 OCS-only 对比 -> 说明采样口径改善对反演性能的影响 | 必须声明两种 OCS 来自不同采样方式，不是"改进"，而是"修正定义" |
| 旧 fusion 1.47° | 与新 fusion 对比 -> 说明统一模型的融合表现 | 同上，不能写成"提升" |
| v0.3 稿件结构 | 作为 v0.4 论文的章节模板和写作参考 | 数值全部替换，方法论重写 |

---

## 四、可复用清单 ✅

### 4.1 代码框架

| 代码 | 路径（旧） | 复用方式 | 说明 |
|---|---|---|---|
| `brdf_models.py`（GGX/Cook-Torrance） | `ocs_project/07_brdf/brdf_models.py` | 直接复制进 v0.4 代码工作区 | 显式 BRDF 公式，独立于采样方式。已验证通过全部单元测试 |
| `materials.py`（材料参数库） | `ocs_project/01_code/materials.py` | 直接复用 | MATERIAL_DB_GGX 参数不变（金属主体 roughness=0.20, F0=0.91 等） |
| `geometry.py`（姿态矩阵） | `ocs_project/01_code/geometry.py` | 直接复用 | Z-Y-X 内旋 R = Rz@Ry@Rx，与 Blender 端一致 |
| `render_geometry_passes.py`（Blender EXR） | `ocs_project/02_blender/render_geometry_passes.py` | 直接复用 | 纯几何渲染（depth/normal/object_id/backfacing），不依赖任何材质 |
| `inv_common.py`（数据集加载） | `ocs_project/03_inversion/inv_common.py` | 改路径后复用 | 数据集组织逻辑不变，只改 OCS manifest 路径 |
| `inv_ocs.py`（OCS 特征生成 + kNN） | `ocs_project/03_inversion/inv_ocs.py` | 直接复用 | 特征生成依赖 OCS 数据格式不变即可 |
| `train_mlp.py`（OCS MLP） | `ocs_project/03_inversion/train_mlp.py` | 直接复用 | 模型架构不变 |
| `train_cnn.py`（CNN/ResNet） | `ocs_project/03_inversion/train_cnn.py` | 直接复用 | 模型架构不变 |
| `train_fusion.py`（fusion） | `ocs_project/03_inversion/train_fusion.py` | 直接复用 | 模型架构不变 |
| 补充实验脚本（12b/12c/12f/12g 等） | `论文改进/补充实验/代码/run_*.py` | 改路径后复用 | 实验逻辑可保留，数据源替换 |
| `diag_subface_adaptive.py` | `ocs_project/02_blender/diag_subface_adaptive.py` | 用于 v0.4 新旧 OCS 审计 | 诊断脚本 |

### 4.2 图像和渲染资源

| 资源 | 路径（旧） | 复用方式 | 说明 |
|---|---|---|---|
| 旧 Blender EXR（geometry passes） | `结果/模块B_渲染/run_20260528_101944_exact_brdf/*.exr` | ⚠️ 条件复用：如果 v0.4 不做任何改变（resolution/ortho_scale/姿态不变），EXR geometry pass 可以直接用旧的，因为不含材质信息 | 节约重渲染时间。但如果 v0.4 改变 ortho_scale、resolution 或需要多观测几何，则需要重渲染 |
| 旧 PNG 图像 | `结果/模块B_渲染/run_20260528_101944_exact_brdf/images/` | ⚠️ 条件复用：如果 BRDF 公式、材料参数和 tone-mapping 不变，image-only 结果可复用 | 需审计与 v0.4 的线性响应一致性 |
| 真实 STL 模型 | `建模/真实模型/` | 直接复用 | 几何不变 |

### 4.3 论文结构和写作资产

| 资产 | 复用方式 | 说明 |
|---|---|---|
| v0.3 稿件全文结构 | 📋 保留章节组织和段落逻辑 | Abstract→Introduction→Related Work→Methodology→Results→Discussion→Conclusion 框架不变 |
| Related Work 章节 | ✅ 直接复用（更新引用） | 不依赖实验数据 |
| v0.3 写作红线 | ✅ 直接复用并加强 | 各项红线在 v0.4 中保持（no real telescope, no fully robust, etc.） |
| 三档投稿策略 | ✅ 保留 Acta/ASR 第一档优先 | 投稿时间后移 |
| v0.3 审阅记录（Codex 复审） | 📋 审阅中指出的结构性问题可作为 v0.4 写作参考 | 数值意见过期，写作/组织意见有效 |

### 4.4 物理/方法定义

| 定义 | 复用方式 |
|---|---|
| GGX/Cook-Torrance BRDF 公式（D_GGX, G_Smith_GGX, F_Schlick） | ✅ 直接复用 |
| 材料参数字典（3 部件 nominal GGX 参数） | ✅ 直接复用 |
| 坐标系定义（Yaw×Pitch 5° 网格，Z-Y-X 内旋） | ✅ 直接复用 |
| 三端闭合验证方法 | ✅ 方法论可复用（验证流程），但用新 OCS 重新验证 |
| OCS 积分定义（`Σ pixel_area · f_r · NoL`） | ✅ 公式复用，但需要补充 sun-side visibility 维度 |

### 4.5 评价指标与图表布局

| 资产 | 复用方式 |
|---|---|
| 评价指标：mean angular error / Hit@k° / worst-case / RMSE | ✅ 直接复用 |
| 图表布局：多面板 heatmap / bar chart / degradation table / outlier gallery | ✅ 直接复用布局，替换数据 |
| 双模态互补性诊断方法（branch masking / OCS noise / beta sweep） | ✅ 诊断逻辑复用 |

---

## 五、隔离规则执行清单

### 5.1 v0.4 禁止写入的目标目录

以下旧目录**禁止**作为 v0.4 的输出路径：

```text
结果/模块A_重构/
结果/模块B_渲染/
结果/模块C_反演/
结果/BRDF验证/
论文改进/补充实验/结果/
论文改进/论文写作/03_投稿定稿/
```

### 5.2 v0.4 应创建的新输出目录

```text
结果/模块A_v0.4_BlenderOCS/           ← 新 OCS 数据
结果/模块B_v0.4_BlenderOCS/           ← v0.4 图像/EXR（如重渲染）
结果/模块C_v0.4_BlenderOCS/           ← v0.4 反演结果
论文改进/补充实验/结果_v0.4_BlenderOCS/ ← v0.4 补充实验
项目重启_v0.4_BlenderOCS/06_论文v0.4重写接入/  ← v0.4 稿件
```

### 5.3 引用规范

v0.4 内所有文件引用外部材料时，必须满足以下之一：

1. 引用 `98_外部材料备份/` 内的备份文件（推荐）
2. 引用外部旧目录中的文件，但必须标注 `[v0.3-archived]` 前缀并说明仅作历史参考
3. 不允许在 v0.4 方法/实验/论文文件中直接引用旧 `结果/模块A_重构/` 等路径作为数据源

---

## 六、遗留审计项（需作者确认）

| 审计项 | 问题 | 建议处理 |
|---|---|---|
| image-only split 一致性 | 旧 image-only 使用的 train/val/test split 是否与旧 OCS 使用的完全一致？seed 是什么？ | v0.4 统一 split seed，审计旧 split 后决定 image-only 是复用还是重跑 |
| EXR geometry pass 复用 | v0.4 是否使用与旧模块 B 完全相同的相机参数（ortho_scale、resolution、姿态遍历网格）？ | 如果完全一致，可复用旧 EXR（只含几何信息）；如果不一致，需要重新渲染 |
| phase63 vs 更大网格 | v0.4 是否沿用 73×37=2701 的 5° 网格？还是增加分辨率？ | 建议沿用 5° 网格以保持与旧版可比性 |
| 多观测几何 | v0.4 保留 5 几何（phase63/120 等）还是只做 single-view？ | 论文至少需要 1 个训练 phase + 1 个跨 phase 泛化测试 |

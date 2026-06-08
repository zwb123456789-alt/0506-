# 旧结果依赖图（Claude 审计生成）

生成时间：2026-06-08

## 一、说明

本文件梳理 v0.3 及之前所有实验/结果的依赖关系，逐项标记：
- 使用的旧 OCS source、旧 image source
- split、feature mode、seed
- 是否受 OCS 采样口径问题影响
- v0.4 处理方式

---

## 二、主反演实验结果依赖

### 2.1 实验 1-7：baseline 实验组

| 实验/结果 | 旧 OCS source | 旧 image source | OCS feature mode | split | seed | 是否受 OCS 采样影响 | v0.4 处理方式 |
|---|---|---|---|---|---|---|---|
| OCS-only kNN | `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/.../ocs_scan.csv` | — | per_part_log 30D / all_raw 45D | phase63 / random split | 旧 seed（未记录在 CLAUDE.md 中） | **是**：OCS 数值来自 face-center 采样 | 重跑：新 Blender-derived OCS manifest |
| OCS-only MLP (5.91±0.22°) | 同上 | — | per_part_log 30D | phase63 | 同 kNN 组 | **是** | 重跑 |
| image-only CNN | — | `结果/模块B_渲染/run_20260528_101944_exact_brdf/images/` | — | phase63 | 旧 seed | **否**（图像渲染链路不变）但需确认 split 与 OCS 完全一致 | 审计后复用或重新汇总 |
| image-only ResNet-18 (1.69±0.07°) | — | 同上 | — | phase63 | 旧 seed | **否**，但受 split 一致性影响 | 审计后复用或重跑 |
| feature fusion (concat5, 1.47±0.07°) | 同 OCS | 同 image | OCS: per_part_log 30D + image: ResNet features | phase63 | 旧 seed | **是**：OCS 特征空间依赖旧采样 | 重跑 |
| late fusion | 同 OCS | 同 image | OCS: per_part_log 30D + image: CNN features | phase63 | 旧 seed | **是** | 重跑 |
| occlusion ratio sweep | 同 OCS | — | all_raw 45D（含遮挡率） | phase63 | 旧 seed | **是** | 重跑 |
| BRDF sensitivity (LegacyPhong vs GGX) | 同 OCS（两种 BRDF 版本） | — | per_part_log 30D | phase63 | 旧 seed | **是**（如果 GGX 版本也来自旧模块 A face-center） | 重跑（GGX 版本） |
| roll sensitivity | 同 OCS | — | per_part_log 30D | phase63 | 旧 seed | **是** | 重跑 |

### 2.2 实验 8-10：ResNet 问题排查

| 实验/结果 | 旧 OCS source | 旧 image source | 是否受 OCS 采样影响 | v0.4 处理方式 |
|---|---|---|---|---|
| fusion 重测 | 旧模块 A OCS | 旧模块 B 图像 | **是** | 重跑 |
| 图像退化 | 旧模块 A OCS | 旧模块 B 图像 + 退化后处理 | **是**（OCS 部分） | 重跑 |
| 数据集审计 | 旧模块 A OCS | 旧模块 B 图像 | 元数据审计结果受 OCS 源影响 | v0.4 重新审计 |

### 2.3 实验 11：ResNet-fusion 图像退化鲁棒性

| 条件 | 结果 | 是否受 OCS 采样影响 | v0.4 处理方式 |
|---|---|---|---|
| clean fusion | 1.47° | **是** | 重跑 |
| noise σ=0.01 fusion | 73.36° | **是** | 重跑 |
| noise σ=0.10 fusion | 73.57° | **是** | 重跑 |
| clean OCS-only | 5.91° | **是** | 重跑 |
| noise σ=0.01 OCS-only | 5.91° | **是** | 重跑 |
| noise σ=0.10 OCS-only | 5.91° | **是** | 重跑 |
| clean image-only | 1.69° | **否** | 审计后复用 |
| noise σ=0.01 image-only | 85.85° | **否** | 审计后复用 |
| noise σ=0.10 image-only | 87.92° | **否** | 审计后复用 |

### 2.4 实验 12：融合机制诊断与鲁棒融合升级

| 条件 | 结果 | 是否受 OCS 采样影响 | v0.4 处理方式 |
|---|---|---|---|
| U1 aug fusion clean | 1.95±0.21° | **是**（退化增强训练使用旧 OCS） | 重跑 |
| U1 aug fusion noise σ=0.10 | 2.31±0.26° | **是** | 重跑 |
| U1 aug fusion worst-case | 164° outliers | **是** | 重跑 |
| image-only+aug clean | 2.63° | **否** | 审计后复用 |
| image-only+aug noise σ=0.10 | 9.55° | **否** | 审计后复用 |

### 2.5 补充实验 12b-12g

| 实验 | 结果概要 | OCS source | Image source | 是否受 OCS 采样影响 | v0.4 处理方式 |
|---|---|---|---|---|---|
| **12b** fusion fallback 隔离 | U1 优于 image-only same aug；image-masked ~30°；OCS 噪声单调拉低 U1 → OCS-image co-utilization | 旧模块 A OCS | 旧模块 B 图像 | **是** | **必须重跑**：核心机制实验，全部数值依赖旧 OCS |
| **12c** observation-style 退化 | U1: read/background/starfield/combined_medium ~2°；combined_severe ~13.88° | 旧模块 A OCS | 旧模块 B 图像 + obs 退化 | **是**（OCS/fusion 部分）；image-only 可审计后复用 | OCS/fusion 重跑；image-only 审计 |
| **12d** cross-phase 泛化 | phase120: image-only/fusion 均 ~80° | 旧模块 A OCS（仅 phase63 训练） | 旧模块 B 图像（phase63 训练，phase120 测试） | **是**（fusion 部分）；image-only 可审计 | fusion 重跑；image-only 审计 |
| **12e** 质心居中控制 | ResNet: 1.69°→2.88°（居中后） | —（仅 image-only） | 旧模块 B 图像 | **低风险**：image-only 为主 | 审计 image source 后复用或重跑 |
| **12f** beta sweep 退化对照 | OCS-only 端 → image-only 端 swept beta | 旧模块 A OCS | 旧模块 B 图像 | **是** | **必须重跑**：beta sweep 的 OCS-only 端完全依赖旧 OCS |
| **12g** outlier gallery | 42/49,950 (0.084%)；50% at |pitch|>75° | 来源旧 12b（U1） | 来源旧 12b | **间接依赖**：等新 12b 后重建 |

---

## 三、图表与 source data 依赖

| 图表 | v0.3 内容 | 旧 OCS 依赖 | 旧 image 依赖 | v0.4 处理方式 |
|---|---|---|---|---|
| Fig.3a-c | per-part OCS heatmap（jinshuzhuti/taiyangnengban/yinshenban） | **完全依赖**旧 `ocs_scan.csv` | — | 替换：使用 Blender-derived per-part OCS |
| Fig.3d | 遮挡率/损失 heatmap | **完全依赖**旧 OCS 遮挡计算 | — | 替换：使用新 sun-side visibility 方案 |
| Fig.4 | OCS-only 平线（5.91° / 6.58°）+ image-only 对比 | **部分依赖**（OCS-only bar） | 部分依赖（image-only bar） | OCS-only 替换；image-only 审计后复用 |
| Fig.5 | fusion（feature/late）性能对比 | **完全依赖**（所有 fusion 结果含 OCS 特征） | 部分依赖 | 全部替换 |
| Fig.6 | image degradation 下三模态对比 | **部分依赖**（OCS-only bar 不变，fusion bar 变） | 部分依赖 | OCS-only / fusion 替换；image-only 审计 |
| Fig.7 | 各 degradation 下 fusion vs image-only | **部分依赖**（fusion） | 部分依赖（image-only） | fusion 替换；image-only 审计 |
| Supplementary Figures | 12b/12c/12f/12g 中全部图表 | **全部含 OCS 或 fusion 的图中受 OCS 采样影响** | 部分 | 全部含 OCS/fusion 的图替换 |

---

## 四、小项目依赖

| 小项目 | 名称 | OCS 依赖 | 处理方式 |
|---|---|---|---|
| 小项目 1 | 卫星光度范围与最亮观测几何 | 读取旧 phase63 `ocs_scan.csv` 计算最亮姿态和相对星等 | 标记旧口径；v0.4 后基于新 OCS 更新 |

---

## 五、论文稿件内容依赖

| 稿件章节 | 受 OCS 影响的部分 | 处理方式 |
|---|---|---|
| Abstract | "OCS provides a physically interpretable, degradation-immune photometric constraint" | 保留框架，数值锚点等重跑后更新 |
| Introduction | 方法定位声明 | 小幅改写（强调统一前向模型） |
| Related Work | 不影响（不依赖实验数据） | 直接复用 |
| Methodology §OCS definition | OCS 积分公式、遮挡定义、face-center 采样描述 | **完全重写**：替换为 Blender pixel-level sampling + Python explicit GGX |
| Methodology §Image rendering | 图像渲染链路 | 微调（方法与旧模块 B 基本一致） |
| Methodology §Fusion | fusion 架构 | 保留架构描述，替换数据源声明 |
| Results §OCS-only | 全部 OCS-only 数值 | **全部替换** |
| Results §Image-only | image-only baseline 数值 | 审计后保留或微调 |
| Results §Fusion | 全部 fusion 数值 | **全部替换** |
| Results §Degradation | 全部 degradation table | **全部替换** |
| Results §12b/12c/12f/12g | 全部结论性数字 | **全部替换** |
| Discussion | OCS-image 互补性、co-utilization 机制解释 | 保留逻辑框架，数值锚点替换 |
| Conclusion | 结论 | 等 v0.4 结果后重写 |

---

## 六、代码依赖总览

| 代码模块 | 是否可复用 | 复用条件 | 说明 |
|---|---|---|---|
| `01_code/brdf_models.py`（GGX/Cook-Torrance） | ✅ 可复用 | 不变 | 显式 BRDF 公式不依赖采样方式 |
| `01_code/materials.py` | ✅ 可复用 | 材料参数不变 | 材料库独立于采样方式 |
| `01_code/geometry.py` | ✅ 可复用 | 姿态定义不变 | 坐标系和旋转矩阵定义 |
| `01_code/config.py` | ⚠️ 部分复用 | 需要改路径和输出目录 | 硬编码路径需要全部替换 |
| `01_code/ocs_core.py` | ❌ 不能直接复用 | — | 使用 face-center 采样，v0.4 需要 pixel-level OCS 积分 |
| `01_code/occlusion.py` | ⚠️ 部分复用 | 如果 v0.4 使用自写 sun-visibility | 旧版使用 face-center ray-cast，v0.4 可能用 Blender shadow ray |
| `02_blender/render_geometry_passes.py` | ✅ 可复用 | 不变 | Blender 几何缓冲渲染纯几何管线 |
| `02_blender/brdf_postprocess.py` | ⚠️ 需要改造 | 改造为 v0.4 canonical OCS 生成器 | 核心逻辑（pixel_area · fr · NoL）可保留，但需要增强 per-part 输出、sun visibility、manifest 生成 |
| `02_blender/diag_subface_adaptive.py` | ✅ 可复用 | 用于新旧 OCS 差异审计 | 诊断脚本，不用于正式结果 |
| `03_inversion/inv_common.py` | ✅ 可复用 | 需改为读取新 manifest 路径 | 数据集加载、特征组织逻辑 |
| `03_inversion/inv_ocs.py` | ✅ 可复用 | 读取新 OCS manifest | OCS-only 模型训练代码不变 |
| `03_inversion/train_mlp.py` | ✅ 可复用 | 读取新 OCS manifest | 模型架构不变 |
| `03_inversion/train_cnn.py` | ✅ 可复用 | 读取新图像 run | 模型架构不变 |
| `03_inversion/train_fusion.py` | ✅ 可复用 | 读取新 OCS + 新图像 | 模型架构不变 |
| 补充实验 `run_*.py` | ✅ 可复用 | 指向新数据路径 | 实验逻辑可保留 |

---

## 七、关键依赖链（有向图示意）

```text
旧模块 A OCS (face-center) ────→ OCS-only MLP 5.91°
    │                              ├──→ OCS heatmap (Fig.3)
    │                              ├──→ fusion clean 1.47°
    │                              ├──→ fusion + noise degradation
    │                              ├──→ 12b fallback isolation
    │                              ├──→ 12c obs degradation (OCS/fusion)
    │                              ├──→ 12f beta sweep
    │                              └──→ 12g outlier gallery (from 12b)
    │
旧模块 B 图像 (pixel-level) ────→ image-only 1.69°
    │                              ├──→ image-only + noise 85.85°
    │                              ├──→ image-only + obs degradation
    │                              ├──→ 12d phase120 ~80°
    │                              └──→ 12e centered 2.88°
    │
旧模块 A OCS + 旧模块 B 图像 ──→ feature fusion / late fusion
                                   └──→ 所有含 fusion 的实验
```

**核心结论**：旧 OCS（左侧分支）的所有下游都受采样口径问题影响。旧图像（右侧分支）的相对独立部分可能可复用（需审计 split 一致性）。

---

## 八、v0.4 重跑优先级建议

| 优先级 | 实验 | 理由 |
|---|---|---|
| **第一波** | OCS-only kNN/MLP | 最基础的基线，所有其他实验都要与它对比 |
| **第一波** | 新 OCS heatmap（Fig.3 替换） | 视觉化审计新 OCS 是否物理合理 |
| **第二波** | image-only（审计后复用或重跑） | 与 OCS-only 并列的基线 |
| **第二波** | feature fusion + late fusion | 核心论文结果 |
| **第三波** | degradation robustness（实验11替换） | 依赖前两波的基线 |
| **第四波** | 12b → 12f → 12c → 12d → 12e → 12g | 补充实验按逻辑依赖顺序重跑 |

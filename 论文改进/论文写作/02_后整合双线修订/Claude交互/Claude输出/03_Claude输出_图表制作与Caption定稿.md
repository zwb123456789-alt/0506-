# Claude 输出：图表制作与 Caption 定稿

> 生成日期：2026-06-02  
> 基于：最终整合版 v0.1 + 补充实验进度 + 写作规划 + 第 1/2 阶段整合清单 + 02b bib 修订审计  
> 输出目的：供 Codex 审阅整合为 v0.2 图表方案

---

## 1. 图表逐项审计

### 1.1 Figures

| 对象 | 当前 v0.1 意图 | 建议主结论 | 推荐结构 | 数据来源 | 待确认项 | 风险 | 处理建议 |
|---|---|---|---|---|---|---|---|
| Fig. 1 | 统一 OCS-image 仿真与反演管线 | 读者一图理解全链路：STL→材料→BRDF→OCS/Image→反演→融合 | 流程框图，左到右或上到下；分 3 层（正向模型 / 数据生成 / 反演模型） | 无数值，纯结构图 | 最终是否包含 ResNet 分支；是否标注 phase63 / concat5 | Low | 保留主文 |
| Fig. 2 | 卫星几何与观测设置 | 展示三部件几何、材料标签、yaw-pitch 坐标定义、5 个观测几何 | (a) STL 三视图/渲染图 (b) 坐标系示意 (c) 5 个 sun-det 几何示意（极坐标或球面） | STL 文件 + config.py OBS_GEOMETRIES | Euler convention 必须确认后才能标注坐标轴 | Medium | 保留主文；坐标轴标注暂缓至 Euler 确认 |
| Fig. 3 | OCS 热图与遮挡诊断 | OCS 是姿态依赖且遮挡敏感的 | (a) 1-2 几何 yaw-pitch OCS 热图 (b) 部件贡献热图 (c) 遮挡率热图 | `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260520_162831/` 或 `run_20260527_195122/` | 选哪个几何展示；colormap 选择；是否含 log scale | Low | 保留主文 |
| Fig. 4 | **v0.1 缺失**（规划文件要求主反演结果对比图） | 一图对比 OCS-only / TinyCNN / ResNet / Fusion | 分组条形图：x=方法，y=mean error + Hit@5 双轴；或 CDF 曲线 | Table 2 + Table 3 数值 | 无（数值已有） | Low | 保留主文（必须补入） |
| Fig. 5 | 图像退化鲁棒性 | clean ResNet 对噪声极脆弱（1.69°→85.85°） | (a) 噪声级 vs mean error 折线 (b) 亮度缩放 vs mean error 折线；标注 OCS baseline 水平线 | `resnet_robustness/run_20260601_143957/` | 是否加入 fusion 退化曲线（当前无数据） | Low | 保留主文 |
| Fig. 6 | OCS 噪声与融合增益 | 融合增益随 OCS 噪声单调递增 | (a) OCS 噪声级 vs OCS-only/fusion mean error 双线 (b) Δmean 增益条形图 | `noise_robustness/run_20260601_094130/` | 0% 数值已由补充实验确认（5.91/3.93） | Low | 保留主文 |
| Fig. 7 | 敏感性与消融汇总 | BRDF/遮挡/roll/phase63/random split 均在可控范围 | 多 panel：(a) BRDF sensitivity bar (b) occlusion w/wo (c) roll sensitivity (d) random split 对照 | 各补充实验结果目录 | 作者需决定哪些进正文 Fig.7 vs 补充材料 | Medium | 压缩后保留主文（建议只选 2-3 最重要 panel） |

### 1.2 Tables

| 对象 | 当前 v0.1 意图 | 待确认项 | 风险 | 处理建议 |
|---|---|---|---|---|
| Table 1 | Related Work 方案对比（9 列 9 行） | Burton 作者名已确认；Yang 改为 2025；Yi 替代 Liu；Wang/Kumar BRDF 字段待 PDF | Medium | 保留主文（宽表可能需期刊调整列数） |
| Table 2 | 主反演 benchmark（6 行） | kNN Hit@10 待确认；TinyCNN 版本二选一 | Medium | 保留主文 |
| Table 3 | ResNet fusion A1-A4 | 数值需交叉核验（已有实验日志） | Low | 保留主文 |
| Table 4 | 鲁棒性与退化汇总 | 0% OCS noise 已填；1%/5% 行是否加入 | Low | 保留主文（建议加入 5% 行） |

---

## 2. 主文图表方案（A）

建议主文保留 7 Figures + 4 Tables，按以下顺序：

| 顺序 | 对象 | 位置 | 主要目的 |
|---:|---|---|---|
| 1 | Fig. 1 | §3.1 Method Overview | 全链路框架一图说明 |
| 2 | Fig. 2 | §3.2-3.3 Geometry & Observation | 物理设置可视化 |
| 3 | Table 1 | §2 Related Work 末尾 | 方案对比定位 |
| 4 | Fig. 3 | §4.1 Forward-model validation | OCS 姿态可观测性与遮挡 |
| 5 | Table 2 | §4.2-4.3 之间 | 主反演结果一览 |
| 6 | Fig. 4 | §4.3 之后 | 主反演结果可视化对比 |
| 7 | Table 3 | §4.4 | ResNet fusion clean 对比 |
| 8 | Fig. 5 | §4.5 图像退化 | clean vs noise 脆弱性 |
| 9 | Fig. 6 | §4.5 OCS noise | 融合增益随噪声递增 |
| 10 | Table 4 | §4.5 末尾 | 鲁棒性汇总 |
| 11 | Fig. 7 | §4.6 Ablation | 敏感性汇总（压缩 2-3 panel） |

---

## 3. 补充材料图表方案（B）

| 对象 | 内容 | 理由 |
|---|---|---|
| Fig. S1 | 完整 5 几何 OCS 热图（phase24/45/63/90/120） | 正文只展示 1-2 几何代表 |
| Fig. S2 | BRDF 参数敏感性完整条形图（所有部件×参数） | 正文 Fig.7 仅展示金属 roughness |
| Fig. S3 | Roll 敏感性完整热图（7 姿态 × 7 roll） | 正文仅引用统计值 |
| Fig. S4 | Phase63 公平消融结果对比图 | 正文一句话引用 |
| Fig. S5 | Random split 完整结果表/图 | 正文一句话引用稳健性 |
| Fig. S6 | TinyCNN/OCS fusion 诊断（互补性分析、case gallery） | 正文已有 r=0.003 引用 |
| Table S1 | 模型超参数汇总（epochs/batch/lr/seeds/early stopping/hardware） | 正文 Method 简述参数量 |
| Table S2 | 全部 5 seeds 逐 seed 结果（ResNet/OCS MLP/Fusion） | 正文仅报告 mean±std |
| Table S3 | 遮挡率分部件完整表（5 几何 × 3 部件） | 正文引用范围值 |

---

## 4. Caption 草案（C）

### Fig. 1

**Fig. 1.** Unified BRDF-driven OCS-image simulation and attitude inversion pipeline. The forward model generates physically consistent OCS signatures and clean photometric images from the same satellite STL geometry, nonuniform material assignment, GGX/Cook-Torrance BRDF, yaw-pitch attitude grid, observation geometry, and analytical self-occlusion. Four inversion models (OCS-only MLP, TinyCNN, ResNet-18, and OCS-image fusion) probe the attitude information carried by each modality under controlled conditions.

### Fig. 2

**Fig. 2.** Satellite geometry and observation setup. (a) Three-component STL model: metal body, solar panel, and baffle/shade with nonuniform GGX material parameters. (b) Yaw-pitch attitude coordinate definition `[待作者确认：Euler order 标注]`. (c) Five sun-sensor observation geometries spanning phase angles of approximately 24° to 120°.

### Fig. 3

**Fig. 3.** OCS signatures and self-occlusion diagnostics. (a) Yaw-pitch OCS heatmap under phase63 observation geometry (GGX, 2701 attitudes). (b) Component-level OCS contribution map showing metal body dominance at specular geometries. (c) Self-occlusion rate map; mean occlusion rates range from 60% to 78.5% across the five observation geometries.

### Fig. 4

**Fig. 4.** Main attitude inversion benchmark comparison. Mean angular error and Hit@5° for OCS-only MLP (per_part_log 30D), TinyCNN image-only, ResNet-18 image-only, and ResNet + OCS fusion (concat5 per_part_log), all evaluated on the 10°→5° interpolation split. Error bars represent standard deviation across 5 random seeds. The ResNet clean-image result (1.69 ± 0.07°) represents an idealized upper-bound condition, not expected field performance.

### Fig. 5

**Fig. 5.** Image degradation robustness. ResNet-18 mean angular error under (a) additive Gaussian noise (σ = 0.01 to 0.10) and (b) global brightness scaling (×0.50 to ×1.50). The dashed horizontal line marks the practical OCS-only baseline (5.91°), which is independent of image-pixel degradation in this benchmark. Under 1% Gaussian noise, ResNet performance collapses from 1.69° to 85.85°, while OCS remains unaffected. These are controlled stress tests, not complete atmosphere/sensor degradation models.

### Fig. 6

**Fig. 6.** OCS noise and fusion gain. (a) OCS-only and feature-fusion mean angular error as a function of relative Gaussian OCS noise (0% to 20%). (b) Fusion gain (Δmean = OCS-only − fusion) increases monotonically from +1.97° at 0% noise to +6.29° at 20% noise, demonstrating that fusion becomes more valuable as OCS measurement quality degrades. The image branch remains clean in this experiment.

### Fig. 7

**Fig. 7.** Sensitivity and ablation summary. `[待作者确认：选择 2-3 panels 进入正文]`. Candidate panels: (a) BRDF parameter sensitivity — metal roughness ±20% causes up to 46% OCS variation, other parameters < 5%. (b) Self-occlusion effect — occlusion rates 60-78.5% across geometries, confirming self-occlusion is not negligible. (c) Roll sensitivity — fixed roll = 0° introduces up to 26% OCS variation, supporting the fixed-roll limitation statement.

### Table 1

**Table 1.** Related work positioning and scope comparison. Entries marked "—" indicate that the specific setting was not reported or not applicable. `[待作者确认：Wang/Kumar BRDF 和 self-occlusion 字段需 PDF 全文确认]`.

### Table 2

**Table 2.** Main attitude inversion benchmark results (10°→5° interpolation split, 5 seeds). The `all_raw` representation is a semi-oracle upper bound including diagnostic quantities; `per_part_log` is the practical component-level OCS setting. `[待作者确认：kNN Hit@10 精确值]`.

### Table 3

**Table 3.** ResNet-18 fusion under clean rendered images. OCS provides modest but consistent improvement: mean error decreases from 1.69° to 1.47° and worst-case error decreases from 9.9° to 6.6°. The concat5 `all_raw` case (A4) shows that a stronger semi-oracle OCS representation does not guarantee better tail robustness (worst = 18.7°).

### Table 4

**Table 4.** Robustness under controlled observation degradation. Image noise results demonstrate clean-image fragility; OCS noise results demonstrate increasing fusion benefit as OCS quality degrades. All degradation tests are controlled stress tests, not complete realistic observation models.

---

## 5. 实际绘图前作者确认问题（D）

| # | 问题 | 涉及图表 | 紧急程度 |
|---:|---|---|---|
| 1 | Euler order 和坐标轴定义最终确认 | Fig. 2(b) | 必须（否则无法标注坐标轴） |
| 2 | Fig. 7 选择哪 2-3 个 panel 进正文？其余移补充材料 | Fig. 7 | 高 |
| 3 | 是否需要单独的 Fig. 4？还是用 Table 2 足够？ | Fig. 4 | 中（建议保留，可视化更直观） |
| 4 | Fig. 3 展示哪个几何的 OCS 热图？phase63 还是 phase120（遮挡最大）？ | Fig. 3 | 中 |
| 5 | Table 1 是否放正文？（9 列较宽，部分期刊可能要求横排或补充材料） | Table 1 | 中 |
| 6 | Table 4 是否加入 OCS noise 1% 和 5% 行？ | Table 4 | 低（建议至少加 5%） |
| 7 | 正文图片格式偏好？（期刊通常要求 300 dpi TIFF/EPS/PDF） | 全部 | 低 |
| 8 | 是否需要在 Fig. 1 框架图中标注 ResNet-18 / TinyCNN 分支？还是只写"image model"？ | Fig. 1 | 低 |
| 9 | Fig. 5 是否需要加入 ResNet+OCS fusion 退化曲线（当前无此实验数据）？ | Fig. 5 | 低（如无数据则不加） |

---

## 6. 第 2 阶段 bib 修订对本阶段的影响

根据 `02b_references.bib修订审计.md`，以下引用名称已变更，图表 caption 和 Table 1 中需统一：

| 旧写法 | 新写法 | 影响位置 |
|---|---|---|
| Yang et al. 2024 | **Yang et al. 2025** | Table 1 第 1 行、§2.1 |
| Liu et al. 2024 Remote Sensing | **Yi et al. 2024** | Table 1 第 7 行、§2.4 |
| Hanada et al. 2024 | 确认为 **Burton et al. 2024** | Table 1 第 4 行、§2.2 |

---

*第 3 阶段 Claude 侧输出完成。本报告不实际绘图，不修改主稿，所有建议交由 Codex 审阅后决定是否纳入 v0.2。*

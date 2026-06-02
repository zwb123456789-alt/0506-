# 03 图表制作与 Caption 定稿：阶段整合清单

> 整合日期：2026-06-02  
> 输入：GPT 输出、Claude 输出、Codex 单边审阅记录、第 1/2/2b 阶段整合清单  
> 用途：作为 v0.2 图表体系、caption 定稿、主文/补充材料分配和实际绘图前核查的依据。  
> 结论：第 3 阶段完成。当前只完成图表方案规划，不实际绘图，不修改主稿。

## 1. 总体结论

GPT 与 Claude 均认为 Fig. 1-7 和 Table 1-4 的框架基本成立，但主文需要压缩，补充材料需要承接完整结果和可复现性细节。

Codex 整合决策：

1. 保留 Fig. 1-6 作为主文核心图候选。
2. Fig. 7 只在作者确认 sensitivity / ablation 取舍后进入主文；否则改为 Supplementary。
3. Table 1 可保留为 Related Work scope-comparison，但必须压缩字段或做横向宽表；无法核实字段不得猜测。
4. Table 2 保留主文压缩版，但需解决 TinyCNN 版本、Weighted kNN Hit@10 和 `all_raw` semi-oracle 标注。
5. Table 3 可视版并入 Fig. 4 后，表格可移 Supplementary，除非目标期刊允许较多主文表格。
6. Table 4 建议主文压缩，完整 image degradation / OCS-noise 结果移 Supplementary。

## 2. 推荐主文压缩方案

| 编号 | 类型 | 主文状态 | 主结论 | 必须保留的边界 |
|---|---|---|---|---|
| Fig. 1 | Framework schematic | 必留 | OCS 和 images 来自同一 STL、材料、BRDF、姿态、观测几何和自遮挡模型 | controlled simulation benchmark; no real telescope validation |
| Fig. 2 | Geometry / setup schematic | 必留 | 三部件几何、材料标签、yaw-pitch/fixed-roll 边界、五个观测几何 | Euler convention 未确认前不得标死坐标轴 |
| Fig. 3 | OCS / occlusion maps | 必留 | OCS 姿态依赖，self-occlusion 对非凸目标不可忽略 | OCS/occlusion 是仿真诊断，不是真实观测验证 |
| Fig. 4 | Main inversion comparison | 必留 | clean ResNet 是 idealized image upper bound；fusion 改善 selected tail errors | 不写 field performance；不写 universal fusion superiority；`all_raw` 是 semi-oracle |
| Fig. 5 | Image degradation | 必留 | clean ResNet 对 Gaussian image noise 脆弱，brightness scaling 较轻 | controlled stress test，不是 atmosphere/sensor model |
| Fig. 6 | OCS-noise fusion gain | 建议保留 | fusion gain 随 OCS noise 增加，体现条件性互补 | OCS-noise 是 feature-level controlled perturbation；0% values 待确认 |
| Fig. 7 | Sensitivity / ablation | 可选主文 | 用少量 confirmed ablations 支撑边界和审稿防御 | 只画最终确认项；完整结果放 Supplementary |
| Table 1 | Related work scope comparison | 建议保留压缩版 | 本文定位区别是 unified paired OCS-image benchmark | scope comparison，不做未核实技术审计 |
| Table 2 | Main benchmark table | 必留压缩版 | 主结果数值和角色定义 | TinyCNN / kNN 待确认；`all_raw` 非 operational |
| Table 3 | ResNet fusion table | 可移 Supplementary | clean-image fusion tail improvement | 若 Fig. 4 覆盖 tail stats，主文可不保留 |
| Table 4 | Robustness table | 建议压缩 | image degradation 和 OCS-noise stress tests | controlled stress tests；0/10/20% 缺项确认后写入 |

## 3. 完整图表方案

### Fig. 1

**主题**：Unified BRDF-driven OCS-image simulation and controlled inversion workflow.

**推荐 panels**：

1. STL / component-labeled geometry input.
2. Nominal material assignment + GGX/Cook-Torrance BRDF + analytical self-occlusion.
3. Paired OCS signatures and clean rendered photometric images.
4. OCS-only / image-only / late-fusion / feature-fusion inversion models.

**整合 caption 草案**：

> Unified BRDF-driven OCS-image simulation and controlled inversion workflow. A real satellite STL model is converted into component-labeled geometry with nominal nonuniform material assignments. For each yaw-pitch attitude and sun-sensor geometry, the same GGX/Cook-Torrance BRDF and analytical self-occlusion treatment generate paired scalar OCS signatures and clean rendered photometric images. The paired outputs are then used to evaluate OCS-only, image-only, late-fusion, and feature-fusion attitude inversion models under consistent forward-model assumptions. The workflow defines a controlled simulation benchmark and does not include real optical telescope validation.

### Fig. 2

**主题**：Geometry, material assignment and observation setup.

**推荐 panels**：

1. Three-component STL / rendered geometry.
2. Material labels / component color blocks.
3. Yaw-pitch coordinate and fixed-roll boundary.
4. Five sun-sensor observation geometries / phase-angle schematic.

**待确认**：

- Euler order / rotation matrix convention.
- yaw / pitch / roll axes.
- final material label names.
- final observation-geometry labels and phase-angle names.

**整合 caption 草案**：

> Geometry, material assignment and observation setup. The target is represented by three component groups corresponding to the metal body, solar panel, and baffle/shade, each assigned nominal material parameters for the controlled GGX/Cook-Torrance simulation. The benchmark estimates yaw and pitch under fixed roll and evaluates five sun-sensor geometries spanning approximately 24 deg to 120 deg phase angle. [待作者确认：Euler order / rotation matrix convention, final coordinate axes, material-label names, and final observation-geometry labels.]

### Fig. 3

**主题**：OCS attitude signatures and self-occlusion diagnostics.

**推荐 panels**：

1. representative yaw-pitch OCS heatmap.
2. component-level contribution maps.
3. occlusion-rate maps.
4. optional phase comparison mini-panel.

**候选数据来源**：

```text
结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260520_162831/
结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260527_195122/
```

绘图前需本地核查具体文件、英文标签和 colormap。

**整合 caption 草案**：

> OCS attitude signatures and self-occlusion diagnostics. Yaw-pitch OCS maps show that scalar photometric signatures vary strongly with attitude and observation geometry. Component-level contribution maps separate the metal body, solar panel, and baffle/shade responses, while occlusion-rate maps show that self-occlusion is substantial for the nonconvex target, with mean occlusion rates of roughly 60-78.5% across the five geometries. These diagnostics support explicit visibility modeling in the controlled OCS simulation; they are not a substitute for real optical validation. [待作者确认：final phase panels and source figure exports.]

### Fig. 4

**主题**：Main attitude-inversion benchmark under clean rendered images.

**推荐 panels**：

1. mean angular error comparison.
2. Hit@5 / Hit@10 comparison.
3. P90 / worst-case comparison for ResNet image-only vs fusion.
4. optional `all_raw` caution marker.

**必须解决**：

- TinyCNN 主结果版本。
- Weighted kNN Hit@10 是否保留。
- `all_raw` 只能标为 semi-oracle / diagnostic。

**整合 caption 草案**：

> Main attitude-inversion benchmark under clean rendered images. OCS-only, image-only, and OCS-image fusion models are compared using mean angular error, threshold accuracy, and tail statistics. Practical component-level OCS features provide an interpretable OCS-only constraint, while the `all_raw` representation is shown only as a semi-oracle diagnostic upper bound. Under clean rendered phase63 images, ResNet-18 defines an idealized image-based upper-bound condition rather than field performance. Adding practical OCS features to the clean ResNet branch yields a modest mean improvement and reduces selected tail errors, supporting conditional complementarity rather than universal fusion superiority. [待作者确认：TinyCNN result version, Weighted kNN Hit@10, final methods shown.]

### Fig. 5

**主题**：Controlled image-degradation stress tests.

**推荐 panels**：

1. clean vs Gaussian noise.
2. brightness scaling.
3. optional stress-test annotation.

**整合 caption 草案**：

> Controlled image-degradation stress tests for the clean ResNet upper-bound setting. ResNet-18 image-only performance is compared between clean rendered images, additive Gaussian image noise, and global brightness scaling. Even 1% Gaussian noise causes a large performance collapse, whereas global brightness scaling is less destructive in this benchmark. These tests are controlled observation-quality stress tests and should not be interpreted as a complete atmosphere, telescope, or detector model.

### Fig. 6

**主题**：OCS-noise stress tests and conditional fusion gain.

**推荐 panels**：

1. OCS-only vs fusion mean error under OCS noise.
2. fusion gain vs OCS noise.
3. optional Hit@5 trend.

**必须解决**：

- 0% OCS-noise OCS-only / fusion mean/std.
- 0/10/20% Hit@5 values.
- 是否展示 1% / 5% intermediate noise levels.

**整合 caption 草案**：

> OCS-noise stress tests and conditional fusion gain. OCS-only and fusion models are compared as controlled relative Gaussian noise is added to the OCS features while the image branch remains clean. Fusion gain increases from low to high OCS-noise settings, indicating that the value of fusion depends on modality quality and failure-mode differences. This result does not imply that OCS is universally robust or that the experiment represents full field degradation. [待作者确认：0% OCS-noise mean/std and Hit@5 values; 10%/20% Hit@5 values.]

### Fig. 7

**主题**：Sensitivity and ablation summary.

**推荐策略**：

- 主文最多放 2-3 个 panels。
- 优先候选：BRDF sensitivity、self-occlusion / occlusion diagnostics、roll sensitivity。
- phase63 fairness、random split 和完整 parameter sweeps 更适合 Supplementary，除非目标期刊强要求主文防御。

**整合 caption 草案**：

> Sensitivity and ablation summary for benchmark boundaries. Compact sensitivity panels summarize only confirmed supporting analyses, potentially including phase-condition fairness, random-split comparison, BRDF-parameter sensitivity, self-occlusion diagnostics, and roll sensitivity. These analyses define the limits of the controlled benchmark, including the use of one primary rendered phase condition, nominal material parameters, and fixed roll. [待作者确认：which ablation values enter the main figure versus Supplementary.]

## 4. Tables 整合方案

| Table | 主文建议 | 必留内容 | 降级/移动内容 | 待确认 |
|---|---|---|---|---|
| Table 1 | 主文压缩版或横向宽表 | Work, target/data, reflectance/BRDF scope, image branch, scalar branch, inversion/fusion, validation type | self-occlusion 若未全文核实，合并到 notes 或写 `Not specified` | Wang/Burton/Kumar/Fankhauser 技术字段；Dickinson AMOS vs PhD |
| Table 2 | 主文保留 | Method/feature, input, mean error, Hit@5, Hit@10, role | Weighted kNN 可移 Supplementary 或删除；Role 列压缩 | TinyCNN 版本；Weighted kNN Hit@10 |
| Table 3 | 可移 Supplementary | ResNet image-only vs practical OCS fusion tail stats | A4 `all_raw` 若留主文必须标 semi-oracle | 是否由 Fig. 4 替代 |
| Table 4 | 主文压缩，完整 Supplementary | image noise, brightness scaling, OCS-noise summary | 完整 1/5/10/20% 表放 Supplementary | 0% values；10/20% Hit@5；是否拆成两表 |

## 5. Supplementary 图表建议

| 编号 | 内容 | 理由 |
|---|---|---|
| Fig. S1 | 完整 5 geometries OCS maps / occlusion maps | 主文 Fig. 3 只放代表性 panels |
| Fig. S2 | BRDF sensitivity 完整参数和部件图 | 主文 Fig. 7 只放摘要 |
| Fig. S3 | Roll sensitivity 完整结果 | 支撑 fixed-roll limitation |
| Fig. S4 | Phase63 fairness / phase-condition ablation | 主文只用一句防御 |
| Fig. S5 | Random split 完整结果 | 说明 split 难度和稳健性 |
| Fig. S6 | TinyCNN/OCS diagnostic complementarity, including `r = 0.003` | 明确它不是 ResNet-pair 证据 |
| Table S1 | 模型超参数汇总 | 回应可复现性风险 |
| Table S2 | 逐 seed 结果 | 支撑 mean ± std |
| Table S3 | 完整 OCS-noise / image degradation stress-test table | 主文 Table 4 压缩 |
| Table S4 | Table 1 扩展版 | 若主文 Table 1 太宽，则完整字段放补充 |

## 6. 实际绘图前作者确认问题

| 优先级 | 问题 | 影响 |
|---|---|---|
| 必须 | Euler convention、coordinate axes、material labels、observation geometry labels | Fig. 2 无法定稿 |
| 必须 | OCS-noise 0% values、10/20% Hit@5、是否展示 1/5% | Fig. 6 / Table 4 |
| 必须 | TinyCNN 主结果版本、Weighted kNN 是否保留 | Fig. 4 / Table 2 |
| 高 | Fig. 7 哪些 ablations 进主文，哪些进 Supplementary | 主文篇幅和审稿防御 |
| 高 | Table 1 是否留主文，或完整放 Supplementary | Related Work 篇幅 |
| 中 | Fig. 3 展示 phase63、phase120 还是两个几何对比 | OCS diagnostics |
| 中 | Table 3 是否留主文，或由 Fig. 4 覆盖后移 Supplementary | Results 篇幅 |
| 中 | 是否需要补 ResNet+OCS image-degradation fusion 曲线 | Fig. 5；当前无数据则不画 |
| 低 | 最终导出格式和图宽规范 | 投稿定稿阶段处理 |

## 7. 后续执行顺序

1. 先处理作者确认项，不实际绘图。
2. 核查 Fig. 3、Fig. 5、Fig. 6、Fig. 7 对应本地结果文件和英文标签。
3. 根据目标期刊篇幅决定主文图表数量。
4. 再进入实际绘图阶段或 v0.2 主稿图表占位替换。
5. 所有 caption 进入 v0.2 前，需再次检查红线：no field performance, no universal fusion, no operational `all_raw`, no ResNet-pair `r = 0.003`, no real telescope validation claim.

## 8. 第 3 阶段结论

第 3 阶段“图表制作与 Caption 定稿”完成。下一阶段进入：

```text
04_全文压缩与期刊风格
```

第 4 阶段目标不是继续扩写内容，而是在保留证据边界的前提下压缩 v0.1 语言、统一 SCI 二区/一区边缘投稿风格、处理图表引用占位和避免过度承诺。

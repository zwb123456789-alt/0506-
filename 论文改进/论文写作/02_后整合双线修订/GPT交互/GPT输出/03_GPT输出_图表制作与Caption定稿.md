# GPT 输出：图表制作与 Caption 定稿

> 日期：2026-06-02  
> 对象：最终整合版 v0.1 的 Fig. 1-7、Table 1-4 与 caption intents  
> 输出性质：交给 Codex 审阅整合的图表规划清单；不实际绘图，不直接修改主稿。  
> 核心边界：所有图表均服务于 controlled benchmark 叙事；clean rendered images 不写成 field performance；controlled noise/brightness/OCS noise 不写成完整 atmosphere/sensor model；`all_raw` 不写成 operational feature；fusion 不写成 universal superiority；`r = 0.003` 不写成 ResNet-pair evidence；不删除 no real optical telescope validation。

## 总体结论

主文建议保留 7 张图和 4 张表的框架，但要收紧分工：

- Fig. 1-3 负责“统一物理仿真链条与 OCS 可观测性”。
- Fig. 4-6 负责“反演性能、clean-image upper bound、退化鲁棒性和条件性互补”。
- Fig. 7 只放已经作者确认的 sensitivity/ablation 摘要；不确定或字段复杂的结果放 Supplementary。
- Table 1 保留为保守的 scope-comparison，不做未经全文核实的细节判断。
- Table 2-4 应压缩主文数值，完整 seed / ablation / stress-test 表放 Supplementary。

## A. 图表总览表

| 编号 | 图表类型 | 主结论 | 主文/补充材料建议 | 当前证据状态 | 风险等级 | 处理建议 |
|---|---|---|---|---|---|---|
| Fig. 1 | schematic-led composite | OCS 和 photometric images 来自同一 STL、材料、BRDF、姿态、观测几何和遮挡模型，并进入 OCS-only/image-only/fusion 反演 | 主文必留 | v0.1 有 caption intent；不依赖新增数值 | Low | 画流程图；不写性能结论 |
| Fig. 2 | schematic + setup panel | 展示三部件几何、材料标签、yaw-pitch/fixed-roll 边界和 5 个观测几何 | 主文建议保留 | 需要作者确认 Euler convention、材料标签和观测几何最终命名 | Medium | 等姿态约定确认后定稿 |
| Fig. 3 | quantitative grid / heatmap | OCS 随姿态和观测几何变化，自遮挡对非凸目标不可忽略 | 主文建议保留 | 模块 A 多几何 manifest 和 OCS/occlusion 图表已有；需确认最终导出英文版 | Medium | 面板压缩，完整热图放 Supplementary |
| Fig. 4 | quantitative comparison | clean rendered images 下 ResNet 是 image-only upper bound，OCS/fusion 提供边际和尾部信息 | 主文必留 | ResNet baseline、ResNet fusion、主结果表已有；TinyCNN 版本和 Weighted kNN Hit@10 仍需确认 | High | 主文只画关键方法，完整方法表放 Table 2/Supplementary |
| Fig. 5 | quantitative robustness | ResNet clean-image result 对 additive Gaussian noise 极脆弱，brightness scaling 较轻 | 主文必留 | ResNet robustness 结果已完成 | Medium | caption 明确 controlled stress test，不是 atmosphere/sensor model |
| Fig. 6 | quantitative trend | OCS-noise 下 fusion gain 随噪声增大，说明互补价值依赖模态质量 | 主文建议保留 | OCS-noise 0/1/5/10/20% 结果已有；第 1 阶段要求作者确认 0%和 Hit@5 | High | 作者确认数值后绘制；否则标 `[待作者确认]` |
| Fig. 7 | compact ablation summary | phase fairness、random split、BRDF sensitivity、occlusion、roll sensitivity 支撑边界与审稿防御 | 主文可选；完整放 Supplementary | 补充实验均有记录，但哪些进正文需作者/Codex 决定 | High | 不要塞太满；正文只放 3-4 个最关键防御点 |
| Table 1 | scope-comparison table | 本文区别在统一 OCS-image forward model、paired modalities、controlled yaw-pitch benchmark | 主文可保留但需压缩 | 第 2 阶段和 02b 已修正 bib；技术字段仍需全文核对 | High | 保守字段；未核实写 Not central/Not specified |
| Table 2 | numeric benchmark table | OCS-only、TinyCNN、ResNet clean upper bound 的主结果 | 主文建议保留压缩版 | 主要数值已记录；TinyCNN版本、Weighted kNN Hit@10 待确认 | High | 删除或移走未完整 baseline；完整表 Supplementary |
| Table 3 | numeric tail/fusion table | ResNet + practical OCS 在 clean rendered images 下改善 mean、P90、worst 和 Hit@5 | 主文建议保留或并入 Fig. 4 | ResNet fusion A1-A4 已完成 | Medium | 若主文图足够，可把 Table 3 放 Supplementary，正文引用 Fig. 4 |
| Table 4 | robustness table | 图像噪声、brightness scaling 和 OCS noise 是 controlled stress tests，不能泛化为真实场景 | 主文建议压缩；完整表 Supplementary | image robustness 和 OCS noise 已完成，但部分主稿占位需确认 | High | 拆分 image degradation 与 OCS noise，补齐 0/10/20% Hit@5 |

## B. 每张 Figure 的 Panel 方案

| Figure | 推荐 panels | 每个 panel 显示什么 | 数据/素材来源 | 待作者确认 | 不应出现的表述 |
|---|---|---|---|---|---|
| Fig. 1 | a. STL/component input；b. BRDF + visibility forward model；c. paired OCS/image outputs；d. inversion models | 从真实 STL、材料分区、yaw-pitch grid、sun-sensor geometry、GGX/Cook-Torrance、自遮挡到 OCS signatures / clean photometric images，再到 OCS-only/image-only/late fusion/feature fusion | 主稿 Method；项目总览；不需要真实数据图 | 模型命名是否统一为 OCS-only / image-only / late fusion / feature fusion | 不写“operational pipeline validated on real telescope data” |
| Fig. 2 | a. 三部件 STL 示意；b. 材料标签表/色块；c. yaw-pitch-fixed roll 坐标示意；d. 5 sun-sensor geometries polar/phase schematic | 几何对象、材料类别、姿态参数化和观测几何范围 | STL 模型；Module A geometry setup；multi_geom_manifest；主稿 3.2-3.4 | Euler order、yaw/pitch/roll 轴、材料标签与 nominal 参数是否最终确认 | 不写 full 3-DOF；不写材料为实测标定 |
| Fig. 3 | a. representative OCS yaw-pitch heatmap；b. component contribution maps；c. occlusion-rate maps；d. phase geometry comparison mini-panel | OCS 姿态依赖、部件贡献和遮挡率 60-78.5% | `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260527_195122/`；已有 fig01-fig06 类输出 | 最终选哪几个 phase panels；是否只用 phase63 + phase120 对比 | 不写 self-occlusion 已被真实观测验证；不把遮挡率当作观测量 |
| Fig. 4 | a. mean angular error bar/point plot；b. Hit@5/Hit@10 comparison；c. P90/worst-case for ResNet image-only vs fusion；d. optional all_raw caution marker | clean ResNet 上限、practical OCS、semi-oracle OCS、ResNet+OCS tail gain | `resnet_baseline`、`resnet_fusion`、`paper_summary` 表；主稿 Table 2/3 | TinyCNN 最终版本；Weighted kNN 是否保留；是否显示 all_raw 45D | 不写 fusion universally best；不把 all_raw 写 operational；不写 clean image field performance |
| Fig. 5 | a. clean vs Gaussian noise line/bar；b. brightness scaling line；c. optional failure annotation | ResNet image-only 从 clean 到 Gaussian noise collapse；brightness scaling 较不破坏 | `论文改进/补充实验/结果/resnet_robustness/run_20260601_143957/` | 是否补 std/error bars；是否显示所有 sigma 或只显示 clean/0.01/0.10 | 不写 Gaussian noise = atmosphere model；不写 image method inherently unreliable |
| Fig. 6 | a. OCS-only vs fusion mean across OCS noise；b. fusion gain vs OCS noise；c. Hit@5 trend | OCS 噪声增加时 fusion 相对 OCS-only 的补偿增大 | `论文改进/补充实验/结果/noise_robustness/run_20260601_094130/` | 0% OCS-noise values、10/20% Hit@5 是否采用；是否展示 1%/5% | 不写 OCS universally robust；不写 complete field-degradation study |
| Fig. 7 | a. phase63 fairness mini-bar；b. random vs 10->5 split mini-bar；c. BRDF sensitivity tornado/points；d. roll sensitivity and occlusion range | 支撑公平性、split 难度、材料敏感性、固定 roll 边界和遮挡必要性 | `phase63_ablation`、`random_split`、`brdf_sensitivity`、`occlusion_analysis`、`roll_sensitivity` | 哪些 ablation 进入主文；是否移 random/phase 完整表到 Supplementary | 不写未确认 cross-phase result；不把 roll sensitivity 写成 full 3-DOF validation |

## C. 每张 Table 的压缩和去留建议

| Table | 是否保留主文 | 应保留列 | 应删除/合并列 | 待确认单元格 | caption 重点 |
|---|---|---|---|---|---|
| Table 1 | 建议主文保留压缩版；完整技术字段可放 Supplementary | Work；Data/target；BRDF/reflectance；Image branch；Scalar branch；Attitude inversion/fusion；Validation type | Self-occlusion/visibility 若未全文核实可合并为 Scope notes；不要过细拆字段 | Wang/Burton/Kumar/Fankhauser 的 BRDF、visibility、validation type；Dickinson AMOS vs PhD | “scope comparison”，不是证明本文 SOTA；未核实字段不猜 |
| Table 2 | 主文保留 | Method/feature；Input；Mean error；Hit@5；Hit@10；Role | 删除 Weighted kNN 或移 Supplementary；Role 列可压缩 | TinyCNN 数值版本；Weighted kNN Hit@10 | 区分 practical OCS、semi-oracle OCS、clean-image upper bound |
| Table 3 | 可主文保留；若 Fig. 4 足够则移 Supplementary | Case；Model/input；Mean；P90；Worst；Hit@5；Interpretation | Hit@10 可删除，因为均接近 100%；Case ID 可删除 | all_raw A4 是否保留在主文 | clean fusion 改善尾部，但不是 universal fusion superiority |
| Table 4 | 主文建议拆分或压缩；完整表 Supplementary | Setting；Model；Mean error；Hit@5；Interpretation | Brightness scaling 可合并为 “brightness stress tests”；OCS noise 可单独表/图 | OCS-noise 0% values；10/20% Hit@5；std 是否全列 | controlled degradation summary，不是真实 atmosphere/sensor 模型 |

## D. Caption 草案

### Fig. 1

**Fig. 1 | Unified BRDF-driven OCS-image simulation and controlled inversion workflow.** A real satellite STL model is converted into component-labeled geometry with nominal nonuniform material assignments. For each yaw-pitch attitude and sun-sensor geometry, the same GGX/Cook-Torrance BRDF and analytical self-occlusion treatment generate paired scalar OCS signatures and clean rendered photometric images. The paired outputs are then used to evaluate OCS-only, image-only, late-fusion and feature-fusion attitude inversion models under consistent forward-model assumptions. The workflow defines a controlled simulation benchmark and does not include real optical telescope validation.

### Fig. 2

**Fig. 2 | Geometry, material assignment and observation setup.** The target is represented by three component groups, corresponding to the metal body, solar panel and baffle/shade, each assigned nominal material parameters for the controlled GGX/Cook-Torrance simulation. The benchmark estimates yaw and pitch under fixed roll and evaluates five sun-sensor geometries spanning approximately 24 deg to 120 deg phase angle. [待作者确认：Euler order / rotation matrix convention, final coordinate axes, material-label names and final observation-geometry labels.]

### Fig. 3

**Fig. 3 | OCS attitude signatures and self-occlusion diagnostics.** Yaw-pitch OCS maps show that scalar photometric signatures vary strongly with attitude and observation geometry. Component-level contribution maps separate the metal body, solar panel and baffle/shade responses, while occlusion-rate maps show that self-occlusion is substantial for the nonconvex target, with mean occlusion rates of roughly 60-78.5% across the five geometries. These diagnostics support the use of explicit visibility modeling in the controlled OCS simulation; they are not a substitute for real optical validation. [待作者确认：final phase panels and source figure exports.]

### Fig. 4

**Fig. 4 | Main attitude-inversion benchmark under clean rendered images.** OCS-only, image-only and OCS-image fusion models are compared using mean angular error, threshold accuracy and tail statistics. Practical component-level OCS features provide an interpretable OCS-only constraint, while the `all_raw` representation is shown only as a semi-oracle diagnostic upper bound. Under clean rendered phase63 images, ResNet-18 defines an idealized image-based upper-bound condition rather than field performance. Adding practical OCS features to the clean ResNet branch yields a modest mean improvement and reduces selected tail errors, supporting conditional complementarity rather than universal fusion superiority. [待作者确认：TinyCNN result version, Weighted kNN Hit@10, final methods shown.]

### Fig. 5

**Fig. 5 | Controlled image-degradation stress tests for the clean ResNet upper-bound setting.** ResNet-18 image-only performance is compared between clean rendered images, additive Gaussian image noise and global brightness scaling. Even 1% Gaussian noise causes a large performance collapse, whereas global brightness scaling is less destructive in this benchmark. These tests are controlled observation-quality stress tests and should not be interpreted as a complete atmosphere, telescope or detector model.

### Fig. 6

**Fig. 6 | OCS-noise stress tests and conditional fusion gain.** OCS-only and fusion models are compared as controlled relative Gaussian noise is added to the OCS features while the image branch remains clean. Fusion gain increases from low to high OCS-noise settings, indicating that the value of fusion depends on modality quality and failure mode differences. This result does not imply that OCS is universally robust or that the experiment represents full field degradation. [待作者确认：0% OCS-noise mean/std and Hit@5 values; 10%/20% Hit@5 values.]

### Fig. 7

**Fig. 7 | Sensitivity and ablation summary for benchmark boundaries.** Compact sensitivity panels summarize only confirmed supporting analyses, including phase63 fairness, random-split comparison, BRDF-parameter sensitivity, self-occlusion diagnostics and roll sensitivity. These analyses define the limits of the controlled benchmark, including the use of one primary rendered phase condition, nominal material parameters and fixed roll. [待作者确认：which ablation values enter the main figure versus Supplementary.]

### Table 1

**Table 1 | Scope comparison between related optical-photometric studies and the present controlled benchmark.** The table compares prior work by target/data type, reflectance or BRDF treatment, image branch, scalar photometric branch, attitude-inversion task, fusion strategy and validation type. Fields should be interpreted conservatively as a scope comparison rather than a complete technical audit; entries that are not confirmed from the cited paper should remain marked as not central or not specified until the full text is checked.

### Table 2

**Table 2 | Main inversion benchmark under the 10 deg -> 5 deg attitude split.** The table reports mean angular error and threshold accuracy for OCS-only, image-only and baseline settings. Practical `per_part_log` OCS is distinguished from the semi-oracle `all_raw` diagnostic representation, and clean rendered ResNet-18 image-only performance is treated as an idealized upper-bound condition. [待作者确认：TinyCNN result version and Weighted kNN Hit@10.]

### Table 3

**Table 3 | ResNet fusion under clean rendered images.** The table compares ResNet image-only and ResNet+OCS feature-fusion variants using mean error, P90, worst-case error and Hit@5. Practical `per_part_log` OCS improves selected clean-image tail errors, whereas the semi-oracle `all_raw` representation does not guarantee better tail behavior. The table supports conditional complementarity, not universal fusion superiority.

### Table 4

**Table 4 | Robustness and controlled degradation summary.** The table summarizes image-noise, brightness-scaling and OCS-noise stress tests. Gaussian image noise and brightness scaling are controlled image-quality perturbations, and OCS noise is a controlled feature-level perturbation; none should be described as a complete atmosphere, sensor or operational field model. [待作者确认：OCS-noise 0% values, 10%/20% Hit@5 values, and whether to split image degradation and OCS noise into separate tables.]

## E. 优先处理顺序

1. 确认 Euler convention、coordinate axes、material labels 和 observation geometry labels，否则 Fig. 2 不能定稿。
2. 确认 Table 4 / Fig. 6 的 OCS-noise 0%、10%、20% 缺项，避免把 `[待作者确认]` 固化进最终图。
3. 决定 TinyCNN 主结果版本和 Weighted kNN 是否保留，避免 Fig. 4 / Table 2 数值冲突。
4. 决定 Table 1 是否留主文；若保留，按第 2 阶段和 `02b_references.bib` 审计做保守字段。
5. 为 Fig. 3 选择最终 phase panels，避免五个几何全部铺开导致主图拥挤。
6. 决定 Fig. 7 只放哪些 confirmed ablations；建议 phase fairness、BRDF sensitivity、occlusion、roll，random split 放 Supplementary。
7. 确认所有图表使用英文版标签和统一术语：OCS、clean rendered images、controlled stress tests、semi-oracle。
8. 实际绘图前回查原始结果文件和 seed 统计，不从主稿二次抄数。
9. 确定主文图表数量上限；若期刊篇幅紧，优先保留 Fig. 1、3、4、5、6 和 Table 1、2，其他转 Supplementary。
10. 所有 caption 最后由 Codex 检查红线：no field performance, no universal fusion, no operational all_raw, no ResNet-pair `r=0.003`, no real telescope validation claim.

## 给 Codex 的整合建议

- 第 3 阶段不应触发实际绘图；应先形成 `阶段整合输出/03_图表制作与Caption定稿_整合清单.md`。
- Fig. 4 是 v0.1 中缺失 caption intent 的关键图，应在 v0.2 图表规划中补入。
- `02b_references.bib修订审计.md` 已说明 bib 主要错误已修正，但 Table 1 的技术字段仍需全文核对；Table 1 caption 应明确其为 scope comparison。
- 图表实际制作阶段应先选后端和导出规范，但本轮不涉及 Python/R 绘图。

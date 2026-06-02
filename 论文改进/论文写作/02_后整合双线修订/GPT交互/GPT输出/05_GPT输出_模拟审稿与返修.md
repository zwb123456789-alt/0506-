# 05 GPT 输出：模拟审稿与返修

> 生成日期：2026-06-02  
> 输入依据：第 5 阶段 GPT 提示词、`00_GPT后整合总览.md`、`00_后整合双线总览.md`、第 1/2/2b/3/4 阶段整合清单、最终整合版 v0.1、论文写作完整规划、补充实验进度。  
> 输出性质：模拟 SCI 二区/一区边缘审稿风险和 v0.2 返修路线，仅供 Codex 审阅整合。未修改主稿。  
> 注意：以下意见是模拟审稿风险，不是真实审稿意见；不生成正式 response letter，不新增实验、引用、图表或方法细节。

## A. 总体审稿判断

当前稿件更接近“**证据基础可成文，但 v0.1 需大修后才适合投稿**”。理由是：论文主线已经从旧的“OCS 主导 / fusion 必然最优”调整为更稳健的 controlled benchmark 叙事，且已有 ResNet clean upper-bound、image degradation、OCS-only、OCS-noise fusion、phase63 fairness、random split、BRDF sensitivity、occlusion、roll sensitivity 等实验支撑。然而，v0.1 仍保留大量 `[CITATION]`、`[to verify]` 和 `[需要作者确认]` 占位，Method 中 Euler convention、target encoding、angular error formula 等可复现细节尚未定稿，Table 1 技术字段和 Table 4 缺值仍会被审稿人抓住。若按第 1-4 阶段整合清单完成 v0.2 修订，这篇稿件具备 SCI 二区投稿基础；若直接以 v0.1 投稿，风险主要不是主线不成立，而是“未完成稿”特征过强。

## B. Major comments

| 编号 | 审稿人可能意见 | 风险等级 | 对应位置/证据 | 建议返修动作 | 是否需要作者确认 |
|---|---|---|---|---|---|
| M1 | 方法可复现性不足：姿态定义、Euler order、target encoding 和 angular error formula 仍是占位，无法复现实验或判断误差计算是否合理。 | High | v0.1 §3.2、§3.8、§3.9；第 1 阶段 A01-A03 | 在 Method 中补齐 Euler order / rotation matrix convention、yaw/pitch/roll 定义、target encoding、angular error formula、Hit@5/Hit@10 定义；保留 yaw periodicity 和 fixed-roll 边界。 | 是 |
| M2 | 当前 citation 和 Related Work 尚未达到投稿状态：Introduction、Table 1、References 中仍有 `[CITATION]`、`[to verify]`、旧作者年份和未核实技术字段。 | High | v0.1 Introduction、Table 1、References；第 2/2b 阶段清单 | 按第 2/2b 阶段核验结果替换引用；统一 Yang 2025、Lu 2024、Wang 2024、Burton 2024、Kumar 2025、Dickinson 2024/2025、Yi 2024；Table 1 改成 conservative scope comparison。 | 部分需要，尤其 Table 1 是否留主文及 PDF/full-text 核对 |
| M3 | 无真实光学验证可能被认为限制较大，尤其标题或结论若出现 robust / physical consistency，容易被读成 field-performance claim。 | High | Abstract、§3.1、§3.7、§5.6、Conclusion；第 4 阶段风险表述 | 继续显性写明 no real optical telescope validation；将 clean rendered images 定义为 idealized upper-bound；将 `physically consistent` 降为 `under shared forward-model assumptions`。 | 否，除非作者想改变目标定位 |
| M4 | 图像实验主要基于 phase63 clean rendered images，跨 phase 泛化不是主结果；审稿人可能质疑 image-only 和 fusion 结论是否只在单一渲染相位成立。 | Medium | v0.1 §3.3、§3.7、§4.6、§5.6；补充实验 phase63 fairness | 在主文中承认 one primary rendered phase condition；将 phase63 fairness 放 Supplementary 或 Fig. 7 选项；不要声称 broader cross-phase generalization 已验证。 | 是，决定 Fig. 7 / Supplementary 取舍 |
| M5 | Fusion 结论需要更精确：clean ResNet 已很强，fusion 的 mean gain 较小；若写作不当会被质疑为过度强调融合优势。 | Medium | v0.1 §4.4、§5.4；ResNet fusion A2：1.69 -> 1.47，worst 9.9 -> 6.6 | 将 fusion 主张限定为 selected tail-error reduction 和 conditional complementarity；主文同时报告 mean、P90、worst、Hit@5；避免 `best`, `superior`, `robust` 的泛化表达。 | 否 |
| M6 | `all_raw` 作为 semi-oracle diagnostic 的边界必须更醒目，否则审稿人会质疑输入特征不现实或比较不公平。 | Medium | v0.1 §3.6、§3.8、§4.2、Table 2、Table 3、§5.3 | 所有表格和图注中把 `all_raw` 标为 semi-oracle diagnostic；主结论以 `per_part_log` 作为 practical component-level OCS feature；`all_raw` 结果可移 Supplementary。 | 否 |
| M7 | OCS-noise 实验的解释边界不够严格时，可能被误读为真实 OCS 测量噪声模型或完整 field degradation。 | Medium | v0.1 §4.5、Table 4、Fig. 6 caption intent；补充实验 OCS-noise | 写成 feature-level OCS-noise perturbation；明确 image branch remains clean；补齐或删除 Table 4 中 0% / Hit@5 缺项；完整噪声表放 Supplementary。 | 是，确认 0%、10%、20% 缺项 |
| M8 | 补充实验很多，但 v0.1 §4.6 仍是泛泛占位；审稿人可能认为 ablation / sensitivity 没有真正进入论证链。 | Medium | v0.1 §4.6；第 3 阶段 Fig. 7；补充实验进度 | 作者决定哪些 ablations 进入主文：优先 BRDF sensitivity、occlusion、roll sensitivity；phase63 fairness 和 random split 可放 Supplementary；主文只报告确认后的少量关键值。 | 是 |
| M9 | 图表体系偏多，Table 1-4 加 Fig. 1-7 对中等篇幅 SCI 稿件可能过重，且部分 caption intent 仍在正文中。 | Medium | v0.1 Results 中 Fig. caption intent；第 3/4 阶段清单 | 主文保留 Fig. 1-6 候选，Fig. 7 条件保留；Table 3 移 Supplementary 或由 Fig. 4 覆盖；caption intent 移出正文。 | 部分需要，取决于目标期刊篇幅 |
| M10 | Data Availability、Author Contributions、COI 仍是占位，投稿前会被编辑部或系统退回。 | High | v0.1 Data Availability、Author Contributions、Conflict of Interest | 投稿材料阶段补齐数据共享范围、代码/模型/STL 派生数据可用性、作者列表和 CRediT roles、COI 最终措辞。 | 是 |

## C. Minor comments

| 编号 | Minor comment | 风险等级 | 建议处理 |
|---|---|---|---|
| m1 | Title 中若保留 `Robust Space Object Attitude Inversion`，建议加 `controlled benchmark` 或改成更保守标题。 | Medium | 用第 4 阶段建议标题之一，避免真实鲁棒性承诺。 |
| m2 | Abstract 单段过长，forward-model 枚举过密。 | Low | 压缩为约 220-260 words，保留核心数值和边界。 |
| m3 | Introduction 中真实观测退化因素列表过长且仍缺 ground-based degradation 文献支撑。 | Medium | 压缩列表，并补 1 篇 seeing / PSF / tracking / AO / ground-based optical degradation 文献。 |
| m4 | `physically consistent`、`validation` 等词容易过强。 | Medium | 统一为 `shared forward-model assumptions`、`sanity checks`、`controlled benchmark evaluation`。 |
| m5 | Related Work 仍有旧写法 `Yang et al. 2024/2025`、`Lu/Yao`、`Liu et al. 2024`。 | High | 按第 2/2b 阶段改为 Yang 2025、Lu 2024、Yi 2024 等。 |
| m6 | Table 1 字段过多，技术字段若未全文核实不应硬填。 | Medium | 改成 scope comparison；无法确认写 `Not specified` 或移 Supplementary。 |
| m7 | Method 中 model architecture、training details、seed 数、split 数量仍需更系统呈现。 | Medium | 主文保留必要信息，完整超参数和逐 seed 表放 Supplementary Table S1/S2。 |
| m8 | Fig. caption intent 出现在正文，影响投稿稿观感。 | Low | 移入图注草案或图表制作文件。 |
| m9 | TinyCNN 结果存在两个版本，Table 2 和文字必须统一。 | High | 作者确认采用版本；另一版本不进入正文。 |
| m10 | Weighted kNN Hit@10 仍缺值。 | High | 回查日志；若无可靠值，删除 Hit@10 列或 Weighted kNN 行。 |
| m11 | Gaussian noise 多等级结果在 Results 中过密。 | Low | 主文保留 1% 代表性崩溃和范围，完整表放 Supplementary。 |
| m12 | `r = 0.003` 段落过长，容易被误读为主结论。 | Medium | 移 Supplementary 或保留一句，并明确 TinyCNN/OCS diagnostic only。 |
| m13 | Discussion 与 Results 重复解释 clean-image upper-bound 和 fusion conditionality。 | Low | 按第 4 阶段压缩，Discussion 聚焦解释与影响。 |
| m14 | Limitations 应保留但压缩；不要把未来工作写成承诺。 | Low | 用 `Further validation requires...` 而不是 `Future work will...`。 |
| m15 | Data / Author / COI 的占位不应出现在投稿版。 | High | 投稿材料阶段补齐，或按目标期刊模板处理。 |

## D. 返修优先级

| 优先级 | 任务 | 类型 | 说明 |
|---|---|---|---|
| 1 | 统一向作者确认 Euler convention、target encoding、angular error formula、TinyCNN version、Weighted kNN Hit@10、OCS-noise missing values、Fig. 7 ablation selection、Data/Author/COI。 | 必须先问作者 | 这些是模型不能代答的事实问题。 |
| 2 | 清理所有引用占位和旧书目信息，落实第 2/2b 阶段核验结果。 | Codex 可直接处理，部分需作者补 PDF | 先处理引用，否则 Related Work 和 Table 1 无法定稿。 |
| 3 | 将 Table 1 改为 conservative scope comparison。 | Codex 可直接处理 | 无法核实的 BRDF、self-occlusion、validation type 不硬填。 |
| 4 | 补齐 Method 可复现细节。 | 必须先问作者 + Codex 整合 | 包括姿态定义、target encoding、metrics、split、模型训练要点。 |
| 5 | 压缩 Abstract、Introduction contribution paragraph、Conclusion。 | Codex 可直接处理 | 可基于第 4 阶段整合候选文本。 |
| 6 | 压缩 Results 4.2-4.5，并重新分配 Table 3 / Table 4。 | Codex 可直接处理，部分需作者确认 | 主文聚焦 ResNet clean benchmark、tail error、controlled degradation；完整表放 Supplementary。 |
| 7 | 决定 Fig. 7 和 ablation / sensitivity 的主文或 Supplementary 分配。 | 必须先问作者 | 建议主文最多 2-3 个 confirmed panels，完整结果进 Supplementary。 |
| 8 | 建立 Supplementary 清单：模型超参数、逐 seed、完整 OCS-noise / image degradation、random split、phase63 fairness、BRDF / roll sensitivity、Table 1 扩展版。 | 可放 Supplementary | 用于回应审稿人可复现性和边界问题。 |
| 9 | 全文术语统一和过度承诺降调。 | Codex 可直接处理 | 统一 clean-image upper-bound、controlled stress tests、semi-oracle、conditional complementarity。 |
| 10 | 补齐 Data Availability、Author Contributions、COI 和目标期刊格式。 | 投稿材料阶段处理 | 进入第 6 阶段或投稿定稿阶段完成。 |

## E. 作者确认问题

只列真正需要作者回答、不能由 GPT/Codex 推断的问题：

1. **Euler convention**：最终是否采用项目记录中的 `R = Rz @ Ry @ Rx`、Z-Y-X 内旋？yaw / pitch / roll 轴向和 Fig. 2 坐标标注如何写？
2. **Target encoding**：所有 MLP、CNN、fusion 模型是否统一使用 `[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]`？是否有例外模型？
3. **Angular error formula**：最终误差公式如何定义？yaw 周期如何处理？pitch 是否直接按角差处理，还是有球面/姿态几何修正？
4. **TinyCNN version**：正文采用 v0.1 中 `12.38 +/- 0.74`, Hit@5 `26.1%`, Hit@10 `55.8%`，还是补充实验同批记录中的 `11.87 +/- 0.69`, Hit@5 `27.1%`, Hit@10 `58.2%`？
5. **Weighted kNN Hit@10**：是否能回查可靠日志？若不能，是否同意删除 Hit@10 列或删除 Weighted kNN 行？
6. **OCS-noise missing values**：Table 4 / Fig. 6 是否采用补充实验候选值：0% OCS-only `5.91 +/- 0.22`, Hit@5 `73.8%`；0% fusion `3.93 +/- 0.46`, Hit@5 `86.3%`；10% Hit@5 `57.8% / 74.9%`；20% Hit@5 `35.8% / 59.6%`？
7. **Fig. 7 ablation selection**：BRDF sensitivity、self-occlusion、roll sensitivity、phase63 fairness、random split 哪些进入主文？哪些只进 Supplementary？
8. **Table 1 placement**：Table 1 是否保留主文压缩版，还是完整移 Supplementary？Wang / Burton / Kumar / Fankhauser 的技术字段是否已做 PDF/full-text 核对？
9. **Data Availability**：simulation data、STL-derived products、trained models、scripts 是否可共享？若不可共享，限制原因和访问方式是什么？
10. **Author Contributions / COI**：最终作者列表、CRediT roles、funding/competing interests 声明如何写？

## F. 不应采用的返修方式

1. 不应为了回应“缺少真实验证”而声称已有 real optical telescope validation。
2. 不应把 clean rendered images 或 phase63 clean images 写成 field performance、real image performance 或 operational performance。
3. 不应把 Gaussian image noise、brightness scaling、OCS-noise perturbation 写成完整 atmosphere/sensor/telescope observation-chain model。
4. 不应把 `all_raw` 写成 operational OCS feature，或将其作为主结论的 practical OCS 性能。
5. 不应把 fusion 写成 universally superior、best in all settings 或 guaranteed robust。
6. 不应把 `r = 0.003` 写成 ResNet-pair evidence；它只能是 TinyCNN/OCS diagnostic，除非作者提供对应 ResNet-pair 分析。
7. 不应新增未实际完成的实验，例如 ResNet-fusion image-degradation 曲线、cross-phase 泛化、真实望远镜数据、完整 3-DOF 数据集。
8. 不应发明或硬填引用，尤其 ground-based optical degradation、Table 1 技术字段、BRDF/self-occlusion 细节。
9. 不应删除 no real telescope validation、fixed roll、phase63、nominal materials、controlled stress tests 等边界来让结论显得更强。
10. 不应在作者未确认前写死 Euler convention、target encoding、angular error formula、TinyCNN version、OCS-noise table values 或投稿声明。

## G. 模拟 reviewer 画像与重点风险

### Reviewer 1: 方法 / 物理建模

最可能关注 BRDF 参数来源、自遮挡计算、Euler convention、姿态任务边界、nominal materials 是否足以支撑物理结论。返修重点是把 Method 写得可复现，并把 `physically consistent` 降为 shared assumptions，不夸大为真实物理验证。

### Reviewer 2: 实验 / 机器学习

最可能关注 ResNet clean result 是否数据泄漏、phase63 是否过窄、fusion mean gain 是否太小、ablation 是否充分、metrics 是否完整。返修重点是报告 sanity checks、split、seeds、tail metrics，并把 TinyCNN 诊断和 `r = 0.003` 降级。

### Reviewer 3: 写作 / 引用 / 投稿适配

最可能关注 `[CITATION]`、`[to verify]`、Table 1 过宽、图表过多、术语不统一、标题/摘要是否过度承诺。返修重点是引用落地、表格压缩、图注边界、Abstract 和 Discussion 压缩。

## H. v0.2 前最低通过线

若只做一次 v0.2 修订，最低通过线应包括：

1. 全部引用占位删除或替换为已核验引用。
2. 所有 `[需要作者确认]` 中影响方法、数值、表格和声明的项目得到处理。
3. Method 可复现细节补齐。
4. Table 1、Table 2、Table 4 不再含缺值或未核实字段。
5. Abstract、Results、Discussion、Conclusion 明确区分 clean upper-bound、controlled stress test、no real telescope validation。
6. Supplementary 计划能承接完整噪声、ablation、逐 seed、超参数和扩展 Table 1。

达不到以上最低线时，不建议进入投稿材料阶段。

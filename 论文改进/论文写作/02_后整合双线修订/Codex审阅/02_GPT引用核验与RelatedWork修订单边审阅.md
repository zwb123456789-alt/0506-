# 02 GPT 引用核验与 Related Work 修订：Codex 单边审阅

> 审阅日期：2026-06-01  
> 被审阅文件：`GPT交互/GPT输出/02_GPT输出_引用核验与RelatedWork修订.md`  
> 审阅结论：通过单边审阅，可作为第 2 阶段整合清单的主要输入。不得直接覆盖主稿。

## 1. 总体判断

GPT 输出完成了第 2 阶段要求：核验 Introduction 引用占位、Related Work 候选文献、Table 1 字段，并给出段落级修订建议。其主要优点是联网核验了 DOI、出版商页面和公开摘要，发现了本地 `references.bib` 中的若干错误。

Codex 抽查后确认：GPT 关于 Yang、Wang、Burton、Kumar、Yi/Liu 等关键冲突的判断总体正确，优先级应高于本地旧 `references.bib`。

## 2. 通过项

| 检查项 | 结论 | 说明 |
|---|---|---|
| 是否核验 DOI/出版页面 | 通过 | 多数关键文献提供 DOI 和网页来源。 |
| 是否避免把关键词当引用 | 通过 | 对宽泛 `[CITATION]` 建议拆句分配引用。 |
| 是否识别 Table 1 风险 | 通过 | 对 self-occlusion、validation type 等字段建议保守处理。 |
| 是否识别本地 bib 冲突 | 通过 | 正确指出 Yang 年份/DOI、Liu/Yi 作者等冲突。 |
| 是否直接改主稿 | 通过 | 未直接覆盖主稿。 |

## 3. Codex 抽查确认

| 项目 | GPT 判断 | Codex 抽查结论 |
|---|---|---|
| Yang material pBRDF paper | Photonics 2025, 12(1), 17, DOI `10.3390/photonics12010017` | 通过。MDPI 页面显示 Photonics 2025, 12(1), 17。 |
| Wang ASR photometry paper | DOI `10.1016/j.asr.2024.04.005`, authors Shu-Shu Wang et al. | 通过。ScienceDirect/Mindat 页面显示 ASR 74(2), 949-963, DOI `.04.005`。 |
| Burton PSO paper | Alexander Burton, Liam Robinson, Carolin Frueh, DOI `10.1016/j.asr.2024.09.008` | 通过。ScienceDirect 页面显示相同作者和页码 5619-5638。 |
| Kumar Acta paper | DOI `10.1016/j.actaastro.2025.04.018`, pages 654-665 | 通过。ScienceDirect 页面显示 Acta Astronautica 232, 654-665。 |
| Remote Sensing fusion paper | 应为 Yi et al. 2024，而非 Liu et al. | 通过。MDPI 页面作者贡献显示 J.Y./Y.M./H.L./Z.Z./R.Z.，题名和 DOI 与 GPT 核验一致。 |
| Lu Universe paper | Lu 2024, Universe 10(5), 215, DOI `10.3390/universe10050215` | 通过。MDPI 页面显示作者 Yao Lu 和该 DOI。 |

## 4. 需整合时保留的限制

1. Yang 可支撑 satellite material pBRDF 和 Cook-Torrance 相关模型比较；如要直接支撑 GGX 参数，仍需谨慎表述。
2. Introduction 的 `[CITATION]` 不应做一对一替换，应按句子拆分引用。
3. `ground-based optical observation degradation` 仍缺一篇专门支撑 seeing/PSF/tracking/noise 的光学观测或 AO 文献。
4. Table 1 应改成保守 scope-comparison，不要猜测无法从摘要/全文确认的 BRDF、self-occlusion、validation type。

## 5. 单边结论

GPT 输出质量合格。其外部核验发现了本地 `references.bib` 的错误，后续 v0.2 前必须先修订 BibTeX 或在主稿中避免沿用旧 bib 字段。

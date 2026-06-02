# 02 Claude 引用核验与 Related Work 修订：Codex 单边审阅

> 审阅日期：2026-06-01  
> 被审阅文件：`Claude交互/Claude输出/02_Claude输出_引用核验与RelatedWork修订.md`  
> 审阅结论：有条件通过。结构化审计有用，但若干书目信息依赖本地旧 `references.bib`，已被外部核验推翻，不能直接进入 v0.2。

## 1. 总体判断

Claude 输出覆盖范围完整，按 Introduction、Related Work、Table 1、References 和修订骨架组织，便于合并。但 Claude 主要以本地 `references.bib` 为权威，而该 bib 已确认存在若干错误。因此 Claude 输出中的“可直接进入 v0.2 的安全替换项”需要降级为“待 Codex 复核后采用”。

## 2. 可采用内容

| 项目 | 结论 | 说明 |
|---|---|---|
| Table 1 逐字段审计结构 | 可采用 | 适合作为整合表格结构。 |
| 地基光学退化引用缺口 | 可采用 | Claude 正确指出 C05 证据薄弱。 |
| Related Work 四小节骨架 | 可采用 | 段落逻辑与论文主线一致。 |
| 不可猜测 BRDF/self-occlusion 字段 | 可采用 | 这是 Table 1 修订原则。 |
| 删除正文未使用的 multi-modal fusion 占位 | 可采用 | 如正文不用该占位，应删除。 |

## 3. 已确认错误或需降级项

| 项目 | Claude 说法 | Codex 复核结论 | 处理 |
|---|---|---|---|
| Yang paper | Photonics 2024, 11(1), 17, DOI `10.3390/photonics11010017` | 外部 MDPI 页面显示 Photonics 2025, 12(1), 17, DOI `10.3390/photonics12010017` | Claude 该项不可采用；应修订 local bib |
| Wang paper | DOI `10.1016/j.asr.2024.04.009`, author `Wang, X. et al.` | ScienceDirect/Mindat 显示 DOI `10.1016/j.asr.2024.04.005`, authors Shu-Shu Wang et al. | Claude 该项不可采用；应修订 local bib |
| Burton/Hanada | 认为主稿 Burton 可能错误，bib 第一作者 Hanada | ScienceDirect 显示 Alexander Burton, Liam Robinson, Carolin Frueh, DOI `.09.008` | 主稿 Burton 正确；local bib `Hanada/.10.008` 需修订 |
| Kumar paper | DOI `.02.019`, pages 1-15 | ScienceDirect 显示 DOI `.04.018`, pages 654-665 | Claude 该项不可采用；应修订 local bib |
| Liu/Remote Sensing | 认为 Liu et al. 正确 | MDPI 页面显示作者缩写 J.Y., Y.M., H.L., Z.Z., R.Z.；GPT/DOAJ核为 Yi et al. | 主稿应改为 Yi et al.; local bib author wrong |

## 4. 单边结论

Claude 输出的结构和风险分类可以纳入阶段整合，但其具体书目信息必须以 Codex 外部核验后的版本为准。下一步不能直接用本地 `references.bib` 生成参考文献，需先更新 bib 或形成修订版 BibTeX。

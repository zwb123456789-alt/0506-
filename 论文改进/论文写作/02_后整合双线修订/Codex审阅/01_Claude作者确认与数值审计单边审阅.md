# 01 Claude 作者确认与数值审计：Codex 单边审阅

> 审阅日期：2026-06-01  
> 被审阅文件：`Claude交互/Claude输出/01_Claude输出_作者确认与数值审计.md`  
> 审阅结论：通过单边审阅，可作为第 1 阶段整合清单的 Claude 侧输入。不得直接覆盖主稿。

## 1. 总体判断

Claude 输出按论文结构逐章审计，覆盖 Title/Abstract、Introduction、Related Work、Method、Results、Discussion、Conclusion、投稿声明、References 和 Figures。输出格式稳定，适合与 GPT 侧清单合并。

Claude 侧的优势是位置定位更细，尤其对 Results 表格、Figure caption intent 和投稿声明缺项的覆盖更完整。它也按要求给出了高风险 Top 10、可直接进入 v0.2 的安全修改建议和作者补充材料清单。

## 2. 通过项

| 检查项 | 结论 | 说明 |
|---|---|---|
| 是否逐章审计 | 通过 | 覆盖从 Title 到 Figures 的全文结构。 |
| 是否识别关键方法占位 | 通过 | Euler convention、target encoding、angular error formula 均列为最高优先级。 |
| 是否识别引用核验风险 | 通过 | 对 Introduction 引用占位、Table 1 与 References 占位均列为 High。 |
| 是否保持写作红线 | 通过 | 没有新增实验、发明引用或弱化 no real telescope validation。 |
| 是否识别表格缺口 | 通过 | 识别 Table 4 OCS noise 缺项、Table 2 Weighted kNN Hit@10 缺项。 |
| 是否识别图表规划缺口 | 通过 | 指出 Fig. 4 主反演结果 caption intent 缺失。 |

## 3. 需在整合时修正或降级的点

| ID | 问题 | 风险 | Codex 处理意见 |
|---|---|---|---|
| C-R1 | Claude 将若干项目写为“可确认”，但仍需要作者决定是否进入正文或补充材料。 | Medium | 阶段整合时应使用“已有项目记录支持，仍需作者确认采用范围”的措辞。 |
| C-R2 | Claude 建议 Table 4 0%、10%、20% OCS-noise 数值可直接进入 v0.2。 | Medium | 这些数值有补充实验记录支撑，但仍需作者确认是否采用为主稿表格值。 |
| C-R3 | Claude 引用了 `CLAUDE.md` 中 Step 信息作为证据，但本轮未逐条打开源实验日志。 | Medium | 阶段整合清单应要求 v0.2 前回查原始 CSV/summary 或实验日志。 |
| C-R4 | Claude 提到可选引用候选如 Linares/Hall/Sharma/Kisantal/Cognion。 | High | 这些只能作为下一阶段检索线索，不得直接作为已核验引用。 |
| C-R5 | Claude 统计“78 项”等数量可作参考，但整合清单不必机械保留原编号。 | Low | 整合时按投稿风险重组为统一清单。 |

## 4. 可进入阶段整合清单的补充项

1. Fig. 4 主反演结果图在 v0.1 caption intent 中缺失，需在图表阶段补入。
2. Table 4 的 OCS-noise 行建议拆分为 OCS-only 与 Fusion 两行，避免“OCS-only -> fusion”排版不规范。
3. 引用核验阶段必须逐项核查 Table 1 的每个字段，不能只核查文献是否存在。
4. `sub-percent agreement` 建议在作者确认后改为具体值或更保守的 “selected checks showed sub-percent agreement”。
5. 结论是否补入 OCS-only `per_part_log` 5.91 deg 作为对比锚点，可在 v0.2 修订时决定。

## 5. 单边结论

Claude 输出质量合格，适合作为阶段整合输入。它与 GPT 输出的主要判断一致：当前最大风险不是主线跑偏，而是方法可复现细节、表格占位、引用占位和补充实验进入正文的边界未定。

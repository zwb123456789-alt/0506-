# 03 Claude 图表制作与 Caption 定稿：Codex 单边审阅

> 审阅日期：2026-06-02  
> 被审阅文件：`Claude交互/Claude输出/03_Claude输出_图表制作与Caption定稿.md`  
> 审阅结论：有条件通过。Claude 输出可作为第 3 阶段整合的重要输入，但不能直接进入 v0.2 图表方案；其中若干数值、数据目录和 panel 选择必须降级为待作者确认。

## 1. 总体判断

Claude 输出覆盖了第 3 阶段要求：逐项审计 Fig. 1-7、Table 1-4，给出主文图表顺序、补充材料图表方案、caption 草案和作者确认问题。整体结构清晰，适合作为后续阶段整合的骨架。

但本阶段任务明确要求“不实际绘图、不把未确认数值固化为最终图”。Claude 输出中有几处把仍需作者确认或需日志复核的内容写得过于确定，因此审阅结论为“有条件通过”，需要在阶段整合时收紧。

## 2. 可采用内容

| 项目 | 结论 | 说明 |
|---|---|---|
| Fig. 1-7 全图表覆盖 | 可采用 | 与 v0.1 caption intent 和阶段任务清单一致。 |
| Table 1-4 去留审计 | 可采用 | 基本符合主文表格需求，但 Table 1 宽表风险需保留。 |
| 主文图表顺序 | 可采用 | Method 图、Related Work 表、Results 图表的顺序合理。 |
| 补充材料方案 | 可采用 | 将完整 OCS 热图、BRDF、roll、phase/random split、逐 seed 结果移补充材料是合理方向。 |
| Caption 红线 | 基本可采用 | clean-image upper-bound、controlled stress test、no-real-validation 边界基本保留。 |
| 第 2b bib 修订影响 | 可采用 | 正确使用 Yang 2025、Yi 2024、Burton 2024。 |

## 3. 必须降级或修正的内容

| 项目 | Claude 说法 | Codex 审阅意见 | 处理 |
|---|---|---|---|
| Fig. 6 / Table 4 的 0% OCS-noise values | 写作“已由补充实验确认（5.91/3.93）” | 第 1 阶段整合清单仍将 0% OCS-noise values 列为作者确认项。即便有候选值，也不能在图表 caption 中写成最终确认。 | 改为 `[待作者确认：0% OCS-noise OCS-only/fusion values and Hit@5]` |
| Fig. 4 数值状态 | 写作“无（数值已有）” | Table 2 仍有 TinyCNN 版本冲突、kNN Hit@10 缺项、all_raw 角色边界。 | 改为“主体数值已有，但部分单元格待作者确认”。 |
| Fig. 7 敏感性结论 | 写作“均在可控范围”，caption 给出 46%、<5%、26% | BRDF、roll、random split、phase63 fairness 是否进入正文仍待作者决定；部分数值需日志最终复核。 | Fig. 7 仅保留候选 panel，不写最终百分比，除非作者确认。 |
| Fig. 3 数据目录 | 给出两个 run 目录 | 目录名可作为线索，但未由 Codex 在本轮核查存在性与具体文件。 | 阶段整合中写作“候选数据来源”，绘图前再核查。 |
| Table 4 加入 5% 行 | 建议加入 5% 行 | 当前主稿 Table 4 已有 0/10/20% 结构；是否加入 1/5% 行属于图表压缩取舍，不应由 Claude 单边决定。 | 保留为作者/整合端取舍项。 |
| Fig. 5 OCS baseline horizontal line | 以 5.91° 作为基线 | 5.91 是 practical OCS-only 主结果，可用；但 caption 必须说明 OCS 不是同一图像退化实验的 field robustness 证据。 | 可采用，但加限定“separate scalar modality in this benchmark”。 |
| Fig. 1 模型列表 | 写 TinyCNN、ResNet-18 和 fusion | 可用，但 Fig. 1 更适合框架图，模型名称不要过细导致拥挤。 | 建议主图写 OCS-only / image-only / fusion，细节放 caption 或图例。 |

## 4. 与阶段任务的符合性

| 要求 | Claude 是否满足 | Codex 判断 |
|---|---|---|
| 不实际绘图 | 满足 | 未生成图像文件。 |
| 不改主稿正文 | 满足 | 输出为审计和 caption 草案。 |
| 不把未确认数值固化为最终图 | 部分不满足 | 0% OCS-noise、Fig.7 sensitivity、Fig.4 部分数值写得偏确定。 |
| 图表主结论 / panel / 数据来源 | 满足 | 但数据来源需绘图前本地核查。 |
| 主文 / Supplementary 分配 | 满足 | 主文 7 图 + 4 表偏多，后续整合时需压缩策略。 |
| 保留红线边界 | 基本满足 | 需继续强化 no real telescope validation 和 controlled benchmark。 |

## 5. 可进入阶段整合的建议

1. 主文图表候选维持 Fig. 1-7 + Table 1-4，但整合时应给出“压缩版主文方案”和“完整方案”两档。
2. Fig. 1 保留为框架图，图中不必塞入全部模型名；caption 可说明 OCS-only / image-only / fusion。
3. Fig. 2 坐标轴和 yaw-pitch 方向必须等待 Euler convention 确认。
4. Fig. 3 先作为 OCS observability / occlusion diagnostic，候选展示 phase63 或遮挡最强几何，待 GPT 输出后再决定。
5. Fig. 4 建议保留，但需先解决 TinyCNN 版本、kNN Hit@10 和 all_raw semi-oracle 标注。
6. Fig. 5 可保留，caption 必须写 controlled stress tests，不写 field robustness。
7. Fig. 6 可保留为 OCS-noise / fusion gain，但 0% values 和 Hit@5 未经作者确认前不得写死。
8. Fig. 7 建议压缩，优先考虑 BRDF sensitivity、occlusion、roll limitation 三者；random split / phase63 fairness 更适合补充材料。
9. Table 1 若留主文，应改为 scope comparison 的横向宽表或移 Supplementary，不能猜测 Wang/Kumar/Burton 的 BRDF/self-occlusion 字段。
10. Table S1 模型超参数表应进入补充材料优先级较高，因为它回应可复现性风险。

## 6. 仍需等待 GPT 侧输出

当前只收到 Claude 第 3 阶段输出。阶段整合清单暂不生成，需等待：

```text
GPT交互/GPT输出/03_GPT输出_图表制作与Caption定稿.md
```

GPT 输出回来后，Codex 应把两边方案整合为：

```text
阶段整合输出/03_图表制作与Caption定稿_整合清单.md
```

## 7. 单边结论

Claude 第 3 阶段输出有条件通过。它提供了可用的图表规划骨架和 caption 草案，但应在整合时统一降级未确认数值、数据目录和 sensitivity panel，避免把候选值写成最终图表事实。

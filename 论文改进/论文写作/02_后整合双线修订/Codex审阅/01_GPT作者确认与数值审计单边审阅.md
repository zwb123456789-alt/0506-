# 01 GPT 作者确认与数值审计：Codex 单边审阅

> 审阅日期：2026-06-01  
> 被审阅文件：`GPT交互/GPT输出/01_GPT输出_作者确认与数值审计.md`  
> 审阅结论：通过单边审阅，可作为第 1 阶段整合清单的 GPT 侧输入。不得直接覆盖主稿。

## 1. 总体判断

GPT 输出完成了本阶段要求的五类任务：

```text
A. 作者确认项总表
B. 数值审计总表
C. 引用核验总表
D. 过度表述风险检查
E. 优先处理顺序
```

输出重点明确，符合后整合阶段定位：不是重写论文，而是识别作者确认、数值核验、引用核验和审稿风险。GPT 没有把占位符替换为猜测事实，也没有把输出直接写成主稿修订稿。

## 2. 通过项

| 检查项 | 结论 | 说明 |
|---|---|---|
| 是否保持 clean-image upper-bound 边界 | 通过 | 明确指出主稿未把 clean rendered images 写成 field performance。 |
| 是否保持 `all_raw` semi-oracle 边界 | 通过 | 明确要求继续标注 `all_raw` 为 semi-oracle / diagnostic。 |
| 是否避免 fusion universal superiority | 通过 | 输出建议继续保留 conditional complementarity。 |
| 是否避免把 `r = 0.003` 写成 ResNet pair 证据 | 通过 | 明确标记为 TinyCNN/OCS diagnostic。 |
| 是否识别高风险方法细节 | 通过 | Euler convention、target encoding、angular error formula 均列为 High。 |
| 是否识别表格占位 | 通过 | 识别 Table 2 Weighted kNN Hit@10、Table 4 OCS noise 0%/10%/20% 缺项。 |
| 是否识别引用风险 | 通过 | 逐项列出 `[CITATION]` 和 `[to verify]`，并标记 Table 1 为高风险核验对象。 |

## 3. 需在整合时修正或降级的点

| ID | 问题 | 风险 | Codex 处理意见 |
|---|---|---|---|
| G-R1 | GPT 将若干补充实验数值直接列为“补充实验给出”，但部分仍需作者确认是否进入正文。 | Medium | 阶段整合清单中应区分“已有补充实验记录”和“允许进入主文”。不能直接填入 v0.2 正文。 |
| G-R2 | GPT 建议“若时间允许补 ResNet-fusion under image degradation 或 cross-phase sanity test”。 | Low | 只能列为 optional strengthening，不作为当前阶段硬门槛。 |
| G-R3 | GPT 对引用给了建议关键词，但未做真实文献核验。 | High | 下一阶段必须联网或用文献库逐条核验；本阶段不得把关键词当引用。 |
| G-R4 | GPT 标注 TinyCNN 旧值 `12.38±0.74` 与同批复测 `11.87±0.69` 冲突。 | Medium | 这是有效发现；整合清单应列为作者确认项，不由 Codex 猜测采用哪组。 |
| G-R5 | GPT 建议材料参数“补来源或明确 nominal”。 | High | 这是必须项；v0.2 前至少应写清参数是 nominal，并把参数来源/敏感性放入审计清单。 |

## 4. 可直接进入阶段整合清单的高优先级项

1. 确认并写入 Euler / rotation convention：项目记录显示 `R = Rz @ Ry @ Rx`、Z-Y-X 内旋，但仍需作者最终确认。
2. 确认 target encoding：项目记录显示 `[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]`，但主稿仍为占位。
3. 确认 angular error formula：必须明确 yaw 周期处理和 pitch 几何。
4. 填补 Table 4 OCS-noise 行：0%、10%、20% 的 mean/std 和 Hit@5。
5. 确认 Weighted kNN all_raw 的 Hit@10，或删除该列/该行。
6. 统一 TinyCNN 主结果采用版本，避免 `12.38±0.74` 与 `11.87±0.69` 混用。
7. 决定 phase63 fairness、random split、BRDF sensitivity、occlusion、roll sensitivity 哪些进入正文，哪些进入 Supplementary。
8. 核验 Table 1 和 References 中全部 `[to verify]`。
9. 补充模型训练细节和架构表。
10. 明确 Data Availability、Author Contributions、Conflict of Interest 的投稿前处理路径。

## 5. 单边结论

GPT 输出质量合格，信息密度足够，可进入阶段整合。但由于 Claude 侧输出虽已出现，`Claude交互/00_Claude后整合总览.md` 尚未按本阶段规则更新，当前不应直接完成双线整合。下一步应先要求 Claude 交互端补充更新其总览文件；补齐后再进行 Claude 单边审阅和最终阶段整合。

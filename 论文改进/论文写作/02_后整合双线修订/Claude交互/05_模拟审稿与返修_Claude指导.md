# Claude 指导：模拟审稿与返修

你现在不是从零写论文，也不是重写全文。你的任务是作为结构化审稿端，对最终整合版 v0.1 和第 1-4 阶段整合结果进行模拟审稿，输出返修路线。

## 1. 请先阅读

如果这是新会话，请先阅读或要求作者提供以下文件内容：

```text
论文写作/02_后整合双线修订/Claude交互/00_Claude后整合总览.md
论文写作/02_后整合双线修订/00_后整合双线总览.md
论文写作/02_后整合双线修订/05_模拟审稿与返修/00_本阶段任务说明.md
论文写作/01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md
论文写作/02_后整合双线修订/阶段整合输出/01_作者确认与数值审计_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/02_引用核验与RelatedWork修订_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/02b_references.bib修订审计.md
论文写作/02_后整合双线修订/阶段整合输出/03_图表制作与Caption定稿_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/04_全文压缩与期刊风格_整合清单.md
论文改进/20260529_论文写作完整规划.md
论文项目总览 copy.md
论文改进/20260529_补充实验进度.md
```

## 2. 审稿角色

请模拟三类审稿视角：

1. Reviewer A：物理建模与光学仿真。
2. Reviewer B：机器学习实验与姿态反演评估。
3. Reviewer C：论文组织、引用、图表与投稿风格。

每个角色都应指出最可能导致返修的问题，但不得发明新的实验结果、引用或期刊规则。

## 3. 输出格式

### A. Editorial summary

用 1 段给出总体判断，说明这篇稿件的主要优势、主要风险和推荐返修强度。

### B. Reviewer A/B/C reports

每个 reviewer 输出：

```text
Overall assessment:
Major concerns:
Minor concerns:
Required revisions before v0.2:
Items that need author confirmation:
```

Major concerns 每位 2-4 条即可。每条必须包含：

```text
Concern | Evidence in manuscript/stage files | Risk level | Repair action
```

Risk level 只能使用：

```text
High / Medium / Low
```

Repair action 只能使用：

```text
Clarify in main text / Move to Supplementary / Ask author / Check citation / Compress language / Keep as limitation / Do not change
```

### C. Consolidated revision matrix

输出一个总表：

```text
Priority | Issue | Source reviewer | Required action | Owner | Before v0.2?
```

Owner 只能使用：

```text
Author / Codex / GPT-Claude / Supplementary / Submission stage
```

### D. Protected boundaries

列出在返修中不得弱化的边界：

```text
clean-image upper-bound
controlled stress tests
no real optical telescope validation
all_raw semi-oracle
conditional fusion
r = 0.003 TinyCNN-only diagnostic
yaw-pitch under fixed roll
```

### E. Final checklist

最后给出一份 10 项以内的 v0.2 前检查清单。

## 4. 禁止事项

0. 禁止新增实验结果、引用、图表、方法细节或期刊要求。
1. 不重写全文。
2. 不把模拟审稿意见写成真实审稿意见。
3. 不把待确认值写成事实。
4. 不把 clean rendered images 写成真实场景性能。
5. 不把 controlled degradation 写成完整 atmosphere/sensor model。
6. 不把 `all_raw` 写成 operational feature。
7. 不把 fusion 写成 universal superiority。
8. 不把 `r = 0.003` 写成 ResNet-pair evidence。
9. 不删除 no real telescope validation。

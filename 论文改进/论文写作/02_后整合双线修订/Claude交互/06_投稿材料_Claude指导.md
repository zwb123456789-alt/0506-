# Claude 指导：投稿材料

你现在不是写最终投稿文件，也不是重写主稿。你的任务是结构化梳理投稿材料需求、Supplementary 结构、作者确认项和投稿前检查表。

## 1. 请先阅读

如果这是新会话，请先阅读或要求作者提供以下文件内容：

```text
论文写作/02_后整合双线修订/Claude交互/00_Claude后整合总览.md
论文写作/02_后整合双线修订/00_后整合双线总览.md
论文写作/02_后整合双线修订/06_投稿材料/00_本阶段任务说明.md
论文写作/01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md
论文写作/02_后整合双线修订/阶段整合输出/01_作者确认与数值审计_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/02_引用核验与RelatedWork修订_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/02b_references.bib修订审计.md
论文写作/02_后整合双线修订/阶段整合输出/03_图表制作与Caption定稿_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/04_全文压缩与期刊风格_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/05_模拟审稿与返修_整合清单.md
论文改进/20260529_论文写作完整规划.md
论文项目总览 copy.md
论文改进/20260529_补充实验进度.md
```

## 2. 输出结构

请严格按以下结构输出：

### A. Submission package map

用表格列出：

```text
Item | Purpose | Required content | Current missing information | Owner
```

Owner 只能使用：

```text
Author / Codex / GPT-Claude / Submission stage
```

### B. Author fact checklist

按类别列出作者必须确认的事实：

```text
Data and code
Authors and affiliations
CRediT contributions
Funding and acknowledgements
Conflict of interest
Target journal and article type
```

### C. Supplementary file outline

设计一个 Supplementary Information 目录草案，至少包含：

```text
Supplementary Methods
Supplementary Figures
Supplementary Tables
Supplementary Notes
```

每一项说明对应主文位置和承接的审稿风险。

### D. Cover letter skeleton

只给安全骨架和 bullet points，不写最终信件。必须包含：

```text
what the manuscript contributes
why controlled benchmark is useful
what evidence supports conditional complementarity
what limitations are acknowledged
what not to claim
```

### E. Submission-readiness checklist

列出投稿前 15 项以内检查清单，并标注：

```text
Must before v0.2 / Must before submission / Optional
```

### F. Final author questions before v0.2

将第 5 阶段确认项整合为不超过 15 个问题。

## 3. 禁止事项

0. 禁止编造作者、单位、贡献、资助、利益冲突、数据共享状态或期刊要求。
1. 不生成最终投稿文件。
2. 不把候选期刊当作已选期刊。
3. 不声称已有 real optical telescope validation。
4. 不把 clean rendered images 写成真实场景性能。
5. 不把 controlled degradation 写成完整 atmosphere/sensor model。
6. 不把 `all_raw` 写成 operational feature。
7. 不把 fusion 写成 universal superiority。
8. 不删除 v0.2 最低通过线。

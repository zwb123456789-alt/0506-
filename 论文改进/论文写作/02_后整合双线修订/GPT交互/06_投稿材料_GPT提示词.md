# GPT 提示词：投稿材料

你现在不是写最终投稿文件，也不是重写主稿。你的任务是基于 v0.1 和第 1-5 阶段整合清单，梳理投稿材料需求、Supplementary 结构和必须向作者确认的问题。

## 1. 请先阅读

如果这是新会话，请先阅读或要求作者提供以下文件内容：

```text
论文写作/02_后整合双线修订/GPT交互/00_GPT后整合总览.md
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

## 2. 你的任务

请输出投稿材料准备清单和草案框架。重点是“需要准备什么、哪些需要作者确认、哪些不能由模型代写”，而不是生成最终文件。

## 3. 必须输出

### A. 投稿材料组件总表

字段：

```text
组件 | 当前状态 | 缺口 | 作者需确认 | Codex 后续可处理
```

至少覆盖：

```text
Manuscript v0.2
Figures
Tables
Supplementary
References / BibTeX
Data Availability
Code Availability
Author Contributions
Conflict of Interest
Funding / Acknowledgements
Cover Letter
Submission checklist
```

### B. Data / Code / Author / COI 作者确认问题

只列真正需要作者回答的问题。不要代填作者、单位、贡献、资助、数据共享状态或利益冲突。

### C. Supplementary 结构建议

根据第 3/5 阶段清单，规划：

```text
Supplementary Figures
Supplementary Tables
Supplementary Methods
Supplementary Notes
```

每项说明与主文哪一节对应、为什么放补充材料。

### D. Cover Letter 安全要点

列出 5-8 条可写入 Cover Letter 的要点，必须保守表达：

```text
controlled simulation benchmark
shared BRDF / geometry / visibility assumptions
clean-image upper-bound
controlled degradation stress tests
conditional complementarity
no real optical telescope validation
```

同时列出禁用表述。

### E. 投稿前 checklist

列出 15 项以内，覆盖占位、引用、图表、表格、数据声明、作者信息、Supplementary、格式。

### F. v0.2 前统一提问清单

合并第 5 阶段作者确认项，整理成可直接问作者的一组问题。不要超过 15 项。

## 4. 红线

0. 禁止编造作者、单位、贡献、资助、利益冲突、数据共享状态或期刊要求。
1. 不生成最终投稿文件。
2. 不把候选期刊当作已选期刊。
3. 不声称已有 real optical telescope validation。
4. 不把 clean rendered images 写成 field performance。
5. 不把 controlled degradation 写成完整 atmosphere/sensor model。
6. 不把 `all_raw` 写成 operational feature。
7. 不把 fusion 写成 universal superiority。
8. 不删除 v0.2 最低通过线。

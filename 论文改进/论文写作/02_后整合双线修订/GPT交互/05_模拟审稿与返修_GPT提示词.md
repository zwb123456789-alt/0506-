# GPT 提示词：模拟审稿与返修

你现在不是从零写论文，也不是重写全文。你的任务是基于最终整合版 v0.1 和第 1-4 阶段整合清单，模拟 SCI 二区/一区边缘审稿风险，并提出 v0.2 返修路线。

## 1. 请先阅读

如果这是新会话，请先阅读或要求作者提供以下文件内容：

```text
论文写作/02_后整合双线修订/GPT交互/00_GPT后整合总览.md
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

## 2. 你的任务

请从审稿人视角评估这篇稿件最可能被质疑的地方。你可以模拟 2-3 类审稿人，例如：

1. 方法/物理建模审稿人。
2. 实验/机器学习审稿人。
3. 写作/引用/投稿适配审稿人。

重点不是批量改写正文，而是找出 v0.2 必须优先修补的风险。

## 3. 必须输出

### A. 总体审稿判断

用 1 段说明：当前稿件更像是可投、需大修后可投、还是证据不足暂不宜投。必须给出理由。

### B. Major comments

请列 6-10 条。每条使用以下字段：

```text
编号 | 审稿人可能意见 | 风险等级 | 对应位置/证据 | 建议返修动作 | 是否需要作者确认
```

风险等级只能使用：

```text
High / Medium / Low
```

### C. Minor comments

请列 8-15 条，覆盖术语、图表、引用、格式、冗余表达和边界句。

### D. 返修优先级

给出 v0.2 前 10 项以内的执行顺序。请区分：

```text
必须先问作者 / Codex 可直接处理 / 可放 Supplementary / 投稿材料阶段处理
```

### E. 作者确认问题

只列真正需要作者回答的问题，不要重复所有泛泛风险。优先包括：

```text
Euler convention
target encoding
angular error formula
TinyCNN version
Weighted kNN Hit@10
OCS-noise missing values
Fig. 7 ablation selection
Data Availability / Author Contributions / COI
```

### F. 不应采用的返修方式

列出哪些回应方式会越界，例如：

```text
新增未做实验
宣称真实验证
把 clean image 写成 field performance
把 fusion 写成 universal superiority
把 all_raw 写成 operational feature
```

## 4. 红线

0. 禁止发明实验结果、引用、图表、方法细节或期刊要求。
1. 不重写全文。
2. 不把模拟审稿意见写成真实审稿意见。
3. 不把待确认值写成事实。
4. 不把 clean rendered images 写成 field performance。
5. 不把 controlled degradation 写成完整 atmosphere/sensor model。
6. 不把 `all_raw` 写成 operational feature。
7. 不把 fusion 写成 universal superiority。
8. 不把 `r = 0.003` 写成 ResNet-pair evidence。
9. 不删除 no real telescope validation。

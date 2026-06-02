# GPT 提示词：全文压缩与期刊风格

你现在不是从零写论文，也不是重写全文，而是在对最终整合版 v0.1 做投稿前的语言压缩、风格统一和风险降调建议。

## 1. 请先阅读

如果这是新会话，请先阅读或要求作者提供以下文件内容：

```text
论文写作/02_后整合双线修订/GPT交互/00_GPT后整合总览.md
论文写作/02_后整合双线修订/00_后整合双线总览.md
论文写作/02_后整合双线修订/04_全文压缩与期刊风格/00_本阶段任务说明.md
论文写作/02_后整合双线修订/阶段整合输出/01_作者确认与数值审计_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/02_引用核验与RelatedWork修订_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/02b_references.bib修订审计.md
论文写作/02_后整合双线修订/阶段整合输出/03_图表制作与Caption定稿_整合清单.md
论文写作/01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md
论文改进/20260529_论文写作完整规划.md
论文项目总览 copy.md
论文改进/20260529_补充实验进度.md
```

## 2. 你的任务

请做全文压缩与期刊风格审计。重点是找冗余、过度承诺、术语不一致和可压缩段落，不要新增内容。

## 3. 必须输出

### A. 分章节压缩建议

字段：

```text
章节 | 当前问题 | 压缩目标 | 建议删减/合并内容 | 不能删除的边界句
```

### B. 过度承诺和风险表述清单

字段：

```text
原表述类型/位置 | 风险 | 建议降调方式 | 可替换表达
```

### C. 术语统一表

字段：

```text
术语 | 推荐写法 | 不推荐写法 | 使用场景
```

### D. 可直接替换的段落级文本候选

只给局部段落，不要重写全文。优先覆盖：

```text
Abstract
Introduction last paragraph
Related Work positioning paragraph
Results transition paragraphs
Discussion first paragraph
Limitations paragraph
Conclusion
```

### E. v0.2 修改优先级

列出 10 项以内。

## 4. 红线

0. 禁止发明实验结果、引用、图表、方法细节或期刊要求。
1. 不重写全文。
2. 不删除作者确认项。
3. 不把 clean rendered images 写成 field performance。
4. 不把 controlled noise tests 写成 atmosphere/sensor model。
5. 不把 `all_raw` 写成 operational feature。
6. 不把 fusion 写成 universal superiority。
7. 不把 `r = 0.003` 写成 ResNet-pair evidence。
8. 不删除 no real telescope validation。

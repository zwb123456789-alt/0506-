# GPT 提示词：图表制作与 Caption 定稿

你现在不是从零写论文，也不是实际绘图，而是在规划最终整合版 v0.1 的图表与 caption。

## 1. 请先阅读

如果这是新会话，请先阅读或要求作者提供以下文件内容：

```text
论文写作/02_后整合双线修订/GPT交互/00_GPT后整合总览.md
论文写作/02_后整合双线修订/00_后整合双线总览.md
论文写作/02_后整合双线修订/03_图表制作与Caption定稿/00_本阶段任务说明.md
论文写作/02_后整合双线修订/阶段整合输出/01_作者确认与数值审计_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/02_引用核验与RelatedWork修订_整合清单.md
论文写作/01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md
论文改进/20260529_论文写作完整规划.md
论文项目总览 copy.md
论文改进/20260529_补充实验进度.md
```

## 2. 你的任务

请完成图表制作与 caption 定稿的审计方案。重点是查漏、排序、风险控制和图表叙事，不要画图，不要写最终投稿稿。

## 3. 必须输出

### A. 图表总览表

字段：

```text
编号 | 图表类型 | 主结论 | 主文/补充材料建议 | 当前证据状态 | 风险等级 | 处理建议
```

### B. 每张 Figure 的 panel 方案

对 Fig. 1-7 分别输出：

```text
Figure | 推荐 panels | 每个 panel 显示什么 | 数据/素材来源 | 待作者确认 | 不应出现的表述
```

### C. 每张 Table 的压缩和去留建议

对 Table 1-4 分别输出：

```text
Table | 是否保留主文 | 应保留列 | 应删除/合并列 | 待确认单元格 | caption 重点
```

### D. Caption 草案

给出 Fig. 1-7 和 Table 1-4 的 caption 草案。caption 可以是投稿前草案，但必须标记未确认数值：

```text
[待作者确认：...]
```

### E. 优先处理顺序

列出实际绘图前必须先解决的 10 项以内问题。

## 4. 红线

0. 禁止编造图、数据、脚本路径、实验结果或已完成的图像文件。
1. 不实际绘图。
2. 不把 clean rendered images 写成 field performance。
3. 不把 controlled noise / brightness scaling 写成完整 atmosphere/sensor model。
4. 不把 `all_raw` 写成 operational feature。
5. 不把 fusion 写成 universal superiority。
6. 不把 `r = 0.003` 写成 ResNet pair evidence。
7. 不删除 no real telescope validation。

# GPT 后整合交互总览

> 最后更新：2026-06-02  
> 用途：给 GPT 新会话恢复上下文使用。当前不是从零写论文，而是在修订已有最终整合版 v0.1。

## 1. 当前任务身份

你是论文后整合阶段的 GPT 协作端。你的职责不是重新写完整论文，而是根据 Codex 给出的阶段提示，对最终整合版 v0.1 做定向审计、核验、压缩或修订建议。

主稿路径：

```text
论文写作\01_初稿生成与整合\最终整合\最终整合版_v0.1_基于GPT吸收Claude.md
```

## 2. 新会话必须先读

如果这是新会话，或你不确定上下文，必须先阅读或要求作者提供以下内容：

```text
论文写作\00_总控流程.md
论文写作\02_后整合双线修订\00_后整合双线总览.md
论文写作\02_后整合双线修订\GPT交互\00_GPT后整合总览.md
论文写作\01_初稿生成与整合\最终整合\最终整合版_v0.1_基于GPT吸收Claude.md
论文改进\20260529_论文写作完整规划.md
论文项目总览 copy.md
论文改进\20260529_补充实验进度.md
```

如果不能读取这些文件，必须请作者粘贴关键内容。`论文项目总览 copy.md` 较长，可先读取或索要与当前任务相关的实验结果、方法细节和数值段落。未读取主稿、全局背景和总览前，不要直接改写论文正文。

硬性约束：

- 未读主稿、全局背景和总览前，不得直接改写论文正文，只能列检查框架、问题清单或要求补充材料。
- 禁止编造实验结果、引用文献、方法细节、模型配置、期刊要求或任何作者尚未确认的事实。
- GPT 输出必须交给 Codex 审阅整合后，才能进入主稿版本线；GPT 不得直接覆盖主稿。

## 3. 同一会话读取规则

同一会话内，如果已经读过上述文件，后续任务不需要重复读取全部文件。每轮只需读取：

- 当前阶段 GPT 提示词。
- 新增的作者说明或实验记录。
- Codex 上一轮审阅意见。

## 4. 当前阶段

当前阶段：

```text
06_投稿材料
```

本轮 GPT 侧状态：

```text
已完成第 1 阶段 GPT 侧作者确认与数值审计输出；已完成第 2 阶段 GPT 侧引用核验与 Related Work 修订输出；已完成第 3 阶段 GPT 侧图表制作与 Caption 定稿规划输出；已完成第 4 阶段 GPT 侧全文压缩与期刊风格审计输出；已完成第 5 阶段 GPT 侧模拟审稿与返修输出；已完成第 6 阶段 GPT 侧投稿材料输出。
```

当前提示词：

```text
论文写作\02_后整合双线修订\GPT交互\06_投稿材料_GPT提示词.md
```

输出保存建议：

```text
论文写作\02_后整合双线修订\GPT交互\GPT输出\06_GPT输出_投稿材料.md
```

本轮已生成/建议交给 Codex 审阅的输出：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\GPT交互\GPT输出\06_GPT输出_投稿材料.md
```

本轮完成情况摘要：

- 已读取第 6 阶段 GPT 提示词、本阶段任务说明、第 5 阶段整合清单、第 3 阶段 Supplementary 建议、后整合双线总览、最终整合版 v0.1 的投稿声明占位和补充实验进度。
- 已确认本阶段不生成最终投稿文件，不绑定具体期刊格式，不代填作者、单位、贡献、资助、利益冲突、数据共享状态或 repository 信息。
- 已完成 A 投稿材料组件总表、B Data/Code/Author/COI 作者确认问题、C Supplementary 结构建议、D Cover Letter 安全要点、E 投稿前 checklist、F v0.2 前统一提问清单，并附可选声明骨架和不可由模型代填内容。
- 未修改主稿，输出仅供 Codex 审阅整合。

仍需作者确认的问题：

1. v0.2 方法和数值确认：Euler convention、target encoding、angular error formula、TinyCNN version、Weighted kNN Hit@10、OCS-noise values。
2. 图表和补充材料确认：Fig. 7 panels、Table 1 placement、Table 3/Table 4 主文或 Supplementary 分配。
3. 数据共享确认：simulation data、OCS maps、rendered images、split files、summary tables、figure source data 是否公开。
4. STL / STL-derived products 是否可共享，若不可共享限制原因是什么。
5. 代码共享确认：simulation/rendering/training/evaluation code、trained models、environment files、license 或 access route。
6. 作者信息：最终作者列表、单位、通讯作者、邮箱、CRediT roles。
7. Funding / Acknowledgements：资助机构、项目号、计算资源、致谢对象。
8. Conflict of Interest：最终 competing interests 声明。
9. 目标期刊和文章类型：用于后续格式、Cover Letter 和 submission checklist 适配。

仍需 Codex 审阅或整合的问题：

1. 审阅 GPT 第 6 阶段输出，确认投稿材料组件、Supplementary 结构、Cover Letter 安全要点和统一提问清单是否完整。
2. 与 Claude 第 6 阶段输出对比后，形成 `阶段整合输出\06_投稿材料_整合清单.md`。
3. 将 Data Availability、Code Availability、Author Contributions、COI、Funding、Cover Letter 骨架转化为后续作者提问和投稿定稿任务。
4. 确保第 5 阶段 v0.2 最低通过线没有被投稿材料阶段绕过。
5. 进入 v0.2 或投稿定稿前，检查所有作者事实和目标期刊要求是否已由作者确认。

下一步：

```text
等待 Codex 审阅本轮 GPT 输出；若 Claude 侧输出也完成，由 Codex 整合到：
论文写作\02_后整合双线修订\阶段整合输出\06_投稿材料_整合清单.md
```

下一轮 GPT 若继续，应优先读取：

```text
论文写作\02_后整合双线修订\Codex审阅\06_GPT投稿材料单边审阅.md
论文写作\02_后整合双线修订\阶段整合输出\06_投稿材料_整合清单.md
下一阶段 GPT 提示词（若 Codex 已创建）
```

## 5. GPT 输出风格

GPT 侧应偏交互、查漏、风险识别：

1. 列出所有需要作者确认的问题。
2. 列出所有数值和来源状态。
3. 标记风险等级：High / Medium / Low。
4. 给出建议处理：保留、补证、降级、删除、移到补充材料。
5. 不直接声称最终采用哪一版修订，由 Codex 整合决策。

## 6. 完成后的状态更新

GPT 完成本阶段输出后，不得自行修改主稿，也不得更新 Codex 总控文件。GPT 必须自行更新本交互端总览文件：

```text
论文写作\02_后整合双线修订\GPT交互\00_GPT后整合总览.md
```

更新内容至少包括：

1. 本轮任务是否完成。
2. 输出文件建议保存位置。
3. 仍需作者确认的问题。
4. 仍需 Codex 审阅或整合的问题。
5. 下一轮应读取的文件或等待的 Codex 审阅意见。

作者把 GPT 输出和已更新的 GPT 总览交给 Codex 后，由 Codex 审阅并更新 `论文写作\00_总控流程.md` 与 `论文写作\02_后整合双线修订\00_后整合双线总览.md`。

## 7. 禁止事项

0. 禁止编造实验结果、引用文献、方法细节、模型配置、期刊要求或任何作者尚未确认的事实。
1. 不发明实验结果。
2. 不发明引用。
3. 不直接删除研究边界。
4. 不把 clean-image upper bound 写成 field performance。
5. 不把 `all_raw` 写成 operational OCS feature。
6. 不把 `r = 0.003` 写成 ResNet pair 证据。
7. 不写未确认的 Euler convention、target encoding、model architecture 或 0% OCS-noise values。

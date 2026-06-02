# 06 Claude 投稿材料：Codex 单边审阅

> 审阅日期：2026-06-02  
> 审阅对象：`02_后整合双线修订/Claude交互/Claude输出/06_Claude输出_投稿材料.md`  
> 对应任务：`02_后整合双线修订/06_投稿材料/00_本阶段任务说明.md`  
> 结论：Claude 侧输出通过单边审阅，可与 GPT 侧第 6 阶段输出合并生成阶段整合清单。

## 1. 总体判断

Claude 输出完成了第 6 阶段要求的投稿材料准备框架，且保持了后整合阶段的边界：

1. 没有生成最终投稿文件。
2. 没有代填作者、单位、CRediT 贡献、资助、COI、数据共享状态或仓库信息。
3. 没有将候选期刊当作已选期刊。
4. 保留了 `no real optical telescope validation`、`clean-image upper-bound`、`controlled stress tests`、`all_raw semi-oracle`、`conditional fusion` 等关键红线。
5. 已在 `Claude交互/00_Claude后整合总览.md` 中补充第 6 阶段完成状态；页眉日期仍显示 2026-06-01，但正文状态已更新，不影响本轮整合。

总体上，Claude 输出比 GPT 输出更适合作为投稿组件 ownership、Supplementary 编号体系和 v0.2 前 15 问的结构底稿；GPT 输出更适合作为作者提问和投稿前 checklist 的查漏底稿。

## 2. 红线核查

| 红线 | 核查结果 | 处理意见 |
|---|---|---|
| 不编造投稿事实 | 通过 | 所有作者事实均标为待确认 |
| 不生成最终投稿文件 | 通过 | 当前仅为 package map、checklist 和 skeleton |
| 不绑定具体期刊格式 | 基本通过 | `Highlights ≤85 字符` 属于期刊相关示例，整合时改为“若目标期刊要求” |
| 不声称真实光学验证 | 通过 | 多处显式写明 no real optical validation |
| clean images 不写成 field performance | 通过 | 保留 idealized upper-bound 表述 |
| controlled stress tests 不写成完整观测链 | 通过 | Supplementary Notes 中单独限定 |
| `all_raw` 不写成 operational feature | 通过 | 明确为 semi-oracle diagnostic |
| fusion 不写成 universal superiority | 通过 | 统一为 conditional complementarity |
| `r = 0.003` 不写成 ResNet-pair evidence | 通过 | 仅作为 TinyCNN/OCS diagnostic |
| 不删除第 5 阶段 v0.2 最低通过线 | 通过 | F 节 15 问覆盖了主要 Blocking 项 |

## 3. 需要整合时修正或降级的地方

| 位置 | 问题 | Codex 整合处理 |
|---|---|---|
| 文件头部输入说明 | 写成读取第 1/2/2b/3/5 阶段清单，漏列第 4 阶段 | 整合清单中补回第 4 阶段全文压缩与期刊风格约束 |
| A 表 Highlights | 写了“每条 ≤85 字符” | 该限制依赖目标期刊，整合时改为“若目标期刊要求，按最新作者指南核对” |
| D.1 Cover letter skeleton 标题 | 使用了一个候选标题 | 整合时作为占位标题，不视为最终投稿标题 |
| E-4 / F-Q6 | 仍沿用“OCS-noise 缺值”说法 | 改为“主稿/Table 4/Fig. 6 采用哪组 0/1/5/10/20% 补充实验数值需统一确认” |
| SM4 / E-7 | 写入 563/1998/2701 sample counts | 可作为候选记录，但整合时标为需作者确认的 split 版本 |
| D.4 数值点 | 可用于 cover letter 证据，但不可直接写最终信 | 整合时保留为“可用安全证据”，正式 cover letter 需目标期刊和通讯作者确认后再写 |
| J5 AI-tool 声明 | 期刊要求随时间变化 | 目标期刊确定后需核对最新作者指南 |

## 4. 可直接吸收的内容

1. `Submission package map` 的 owner 分配适合进入整合清单。
2. `Author fact checklist` 的 Blocking / Deferrable 分类清晰，可作为投稿前作者事实收集表。
3. Supplementary 的 `SM / Fig.S / Table S / SN` 四类结构比 GPT 输出更完整，可作为主结构。
4. Cover letter 的安全骨架和 “what not to claim” 可作为后续投稿定稿红线。
5. `Submission-readiness checklist` 的 15 项可与 GPT checklist 合并，分成 `Must before v0.2`、`Must before submission` 和 `Optional`。
6. `Final author questions before v0.2` 覆盖第 1/3/5 阶段 Blocking 项，可作为最终统一提问清单底稿。

## 5. 本阶段整合结论

Claude 第 6 阶段输出通过单边审阅。由于 GPT 第 6 阶段输出此前已经通过单边审阅，现在可以生成：

```text
02_后整合双线修订/阶段整合输出/06_投稿材料_整合清单.md
```

生成整合清单后，需同步更新：

```text
论文写作/00_总控流程.md
论文写作/02_后整合双线修订/00_后整合双线总览.md
```


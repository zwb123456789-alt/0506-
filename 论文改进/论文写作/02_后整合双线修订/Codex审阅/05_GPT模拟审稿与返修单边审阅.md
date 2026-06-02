# 05 GPT 模拟审稿与返修：Codex 单边审阅

> 审阅日期：2026-06-02  
> 被审阅文件：`GPT交互/GPT输出/05_GPT输出_模拟审稿与返修.md`  
> 审阅结论：通过单边审阅，可作为第 5 阶段整合清单的主要输入。输出中的 OCS-noise 缺值、TinyCNN 版本、Table 1 技术字段和 Data/Author/COI 等内容仍需作者确认，不能由 Codex 或 GPT 直接写成事实。

## 1. 总体判断

GPT 输出完整覆盖了第 5 阶段要求：总体审稿判断、Major comments、Minor comments、返修优先级、作者确认问题、不应采用的返修方式、模拟 reviewer 画像和 v0.2 最低通过线均已给出。与 Claude 输出相比，GPT 更准确地把当前风险定位为“v0.1 未完成稿特征过强”，而不是主线证据不足；这与前四个阶段的整合结果一致。

GPT 输出没有新增实验、引用、图表或方法细节，也没有把模拟审稿意见写成真实审稿意见。它适合作为第 5 阶段整合的主输入，尤其适合转化为 v0.2 修订优先级和作者确认清单。

## 2. 通过项

| 检查项 | 结论 | 说明 |
|---|---|---|
| 是否按第 5 阶段要求输出 | 通过 | A-H 结构完整，覆盖 major/minor/priority/author questions。 |
| 是否避免新增事实 | 通过 | 未新增实验或未核验引用。 |
| 是否保留红线边界 | 通过 | clean upper-bound、controlled stress tests、`all_raw`、fusion、`r = 0.003`、fixed roll 均有保护。 |
| 是否识别 v0.2 阻塞项 | 通过 | 明确 citation 占位、作者确认、Table 1/2/4、Data/Author/COI。 |
| 是否可转为执行路线 | 通过 | D 节返修优先级和 H 节最低通过线可直接进入整合清单。 |

## 3. 可采用内容

| 内容 | 采用方式 |
|---|---|
| “证据基础可成文，但 v0.1 需大修后才适合投稿” | 作为内部阶段判断，不写入主稿。 |
| Major M1-M3 | 作为第 5 阶段核心 high-risk comments：方法可复现性、引用/Related Work、无真实验证边界。 |
| Major M4-M9 | 作为 medium-risk revision items：phase63 边界、fusion 限定、`all_raw` 降级、OCS-noise 边界、ablation 取舍、图表压缩。 |
| Major M10 | 转入第 6 阶段投稿材料：Data Availability、Author Contributions、COI。 |
| Minor comments | 与第 3/4 阶段整合高度一致，可用于 v0.2 checklist。 |
| 返修优先级 D | 可作为第 5 阶段整合的主线。 |
| 作者确认问题 E | 可作为统一向作者提问的基础，但需去重并按“v0.2 前必须 / 投稿材料阶段”分类。 |
| 不应采用的返修方式 F | 可完整进入整合清单，作为后续修稿红线。 |
| v0.2 最低通过线 H | 可作为进入 v0.2 主稿修订前的 gate。 |

## 4. 整合时需要保守处理的点

| GPT 表述 | Codex 处理 |
|---|---|
| “已有 phase63 fairness、random split、BRDF sensitivity、occlusion、roll sensitivity 等实验支撑” | 只能写作“已有补充实验/记录可作为候选支撑”，最终主文/补充材料采用仍需作者确认和日志核查。 |
| OCS-noise 0%、10%、20% 候选值 | 不直接写入主稿；统一列入作者确认清单。 |
| Table 1 技术字段 | 只按第 2/2b 阶段已核验信息修订；未全文核实字段写 `Not specified` 或移 Supplementary。 |
| “进入第 6 阶段投稿材料” | 第 6 阶段可创建任务，但不等于已经可以投稿；v0.2 前阻塞项仍需先处理。 |
| Data/Author/COI | 只能由作者提供事实，GPT/Claude/Codex 不得代造作者贡献或利益冲突声明。 |

## 5. 与 Claude 输出的互补关系

| 方面 | GPT 更强 | Claude 可补充 |
|---|---|---|
| 当前稿件状态判断 | 将风险定位为“未完成稿特征过强”，更准确 | “major revision without new experiments” 可作为修订强度参考 |
| 作者确认清单 | 更完整，覆盖 Data/Author/COI | 材料参数来源、BRDF 方程/引用提醒可补充 |
| 红线保护 | 更贴近前四阶段边界 | Protected Boundaries 表格清晰 |
| v0.2 最低通过线 | 很适合作为整合清单 gate | Reviewer A/B/C 分类可辅助组织 |
| 需降级项 | 较少 | Claude 的新增引用/目标期刊/迁移 Supplementary 建议需降级 |

## 6. 单边结论

GPT 第 5 阶段输出通过单边审阅。下一步可将 GPT 与 Claude 输出整合为：

```text
阶段整合输出/05_模拟审稿与返修_整合清单.md
```

整合时应以 GPT 的风险优先级、作者确认清单和 v0.2 最低通过线为主，以 Claude 的三类 reviewer 结构、材料参数/BRDF 复现性提醒和 Protected Boundaries 表为补充。

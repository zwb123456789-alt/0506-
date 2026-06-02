# 06 GPT 投稿材料：Codex 单边审阅

> 审阅日期：2026-06-02  
> 审阅对象：`02_后整合双线修订/GPT交互/GPT输出/06_GPT输出_投稿材料.md`  
> 对应任务：`02_后整合双线修订/06_投稿材料/00_本阶段任务说明.md`  
> 结论：GPT 侧输出通过单边审阅，可作为第 6 阶段整合材料之一。当前不生成阶段整合清单，需等待 Claude 侧第 6 阶段输出返回后再整合。

## 1. 总体判断

GPT 输出覆盖了本阶段要求的主要组件：

1. 投稿材料组件总表。
2. Data / Code / Author / COI / Funding 作者确认问题。
3. Supplementary Figures / Tables / Methods / Notes 结构建议。
4. Cover Letter 安全要点和禁用表述。
5. 投稿前 checklist。
6. v0.2 前统一提问清单。
7. 可选声明骨架和不应由模型代填的内容。

输出没有直接生成最终投稿文件，没有绑定具体目标期刊要求，也没有代填作者、单位、贡献、资助、利益冲突、数据共享状态或 repository 信息。总体符合第 6 阶段任务边界。

## 2. 红线核查

| 红线 | 核查结果 | 处理意见 |
|---|---|---|
| 不编造作者、单位、贡献、资助、COI、数据共享状态 | 通过 | 保留所有 `[待作者确认]` 和问题形式 |
| 不生成最终投稿文件 | 通过 | 当前仅为框架和清单 |
| 不把候选期刊当作已选期刊 | 通过 | 后续 cover letter 需等待目标期刊确认 |
| 不声称真实光学望远镜验证 | 通过 | Cover Letter 禁用表述明确保留 |
| 不把 clean rendered images 写成 field performance | 通过 | 输出明确写 clean-image upper-bound |
| 不把 controlled stress tests 写成完整 observation-chain model | 通过 | 输出明确区分 controlled degradation / full atmosphere-sensor model |
| 不把 `all_raw` 写成 operational feature | 通过 | Supplementary Methods 中要求写 semi-oracle / diagnostic definition |
| 不把 fusion 写成 universal superiority | 通过 | Cover Letter 使用 conditional complementarity |
| 不删除第 5 阶段 v0.2 最低通过线 | 通过 | checklist 和统一提问清单继承了第 5 阶段阻塞项 |

## 3. 需要整合时微调的地方

| 位置 | 问题 | Codex 整合处理 |
|---|---|---|
| F-Q6、checklist 第 3 项 | GPT 写成 “OCS-noise 0%、10%、20% 缺值”，但补充实验进度中已有 0/1/5/10/20% 表；真正问题是主稿和表格尚未统一采用哪组值 | 整合时改写为“OCS-noise values 在主稿/Table 4/Fig. 6 中需统一并由作者确认是否采用补充实验表” |
| Supplementary Table S5 | 写入 `563 train attitudes、1998 test attitudes` 作为示例 | 这些数值可用作待核对项；整合时避免直接写死，除非作者确认 split 版本 |
| Cover Letter skeleton | 已较保守，但仍像可直接粘贴 | 整合时标注为“要点骨架”，正式文本需在目标期刊、通讯作者和文章类型确认后生成 |
| Data / Code skeleton | 保留了 repository / DOI 选项 | 整合时继续保持三选一：公开仓库、合理请求、不可公开及原因；不得默认 Zenodo/GitHub |
| Supplementary Note S1-S4 | 结构合理，但可能与期刊补充材料命名冲突 | 整合时按目标期刊格式再改编号；当前只作为内容规划 |

## 4. 可直接吸收的内容

1. 投稿材料组件总表的字段结构可直接进入第 6 阶段整合清单。
2. Data Availability 和 Code Availability 的作者问题较完整，可合并进最终作者统一提问清单。
3. Supplementary 四类结构适合承接第 3/5 阶段图表与审稿风险，不需要重做。
4. Cover Letter 安全要点和禁用表述可作为后续 cover letter 草案的红线。
5. “不应由模型代填的内容”应保留到最终投稿 checklist。

## 5. 当前不能推进的事项

1. 不能生成 `阶段整合输出/06_投稿材料_整合清单.md`，因为 Claude 第 6 阶段输出尚未返回。
2. 不能进入 v0.2 主稿修订，因为第 5 阶段最低通过线中的方法、数值、引用、图表和投稿声明确认项仍未由作者清零。
3. 不能生成最终 Data Availability、Code Availability、Author Contributions、Funding、COI 或 Cover Letter。
4. 不能按 Acta Astronautica、Advances in Space Research、Optics Express 或 Remote Sensing 的具体格式定稿，除非作者先选定目标期刊并允许核对最新作者指南。

## 6. 给 Claude 侧或作者的下一步

当前仍需等待：

```text
02_后整合双线修订/Claude交互/Claude输出/06_Claude输出_投稿材料.md
```

Claude 返回后，Codex 应：

1. 审阅 Claude 第 6 阶段输出并生成 `Codex审阅/06_Claude投稿材料单边审阅.md`。
2. 对照本 GPT 单边审阅，生成 `阶段整合输出/06_投稿材料_整合清单.md`。
3. 更新 `00_总控流程.md` 和 `02_后整合双线修订/00_后整合双线总览.md`。


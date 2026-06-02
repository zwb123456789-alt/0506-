# 03 GPT 图表制作与 Caption 定稿：Codex 单边审阅

> 审阅日期：2026-06-02  
> 被审阅文件：`GPT交互/GPT输出/03_GPT输出_图表制作与Caption定稿.md`  
> 审阅结论：通过单边审阅，可作为第 3 阶段整合清单的主要输入。不得直接覆盖主稿，不得触发实际绘图。

## 1. 总体判断

GPT 输出完整覆盖第 3 阶段任务：图表总览、Fig. 1-7 panel 方案、Table 1-4 压缩去留建议、caption 草案、优先处理顺序和整合建议均已给出。其主要优点是风险控制较稳，明确保留了 Euler convention、TinyCNN 版本、Weighted kNN Hit@10、OCS-noise 0% values、Fig. 7 ablation 选择和 Table 1 技术字段的作者确认状态。

与 Claude 输出相比，GPT 更适合作为整合阶段的“红线和待确认项”基准；Claude 的顺序和补充材料清单可作为结构补充。

## 2. 通过项

| 检查项 | 结论 | 说明 |
|---|---|---|
| 是否覆盖 Fig. 1-7 | 通过 | 每张 figure 均有 panel 方案、数据来源、待确认项和禁用表述。 |
| 是否覆盖 Table 1-4 | 通过 | 给出主文/补充材料去留、保留列、待确认单元格和 caption 重点。 |
| 是否保留图表红线 | 通过 | 明确保留 controlled benchmark、upper-bound、semi-oracle、conditional fusion、no real validation。 |
| 是否避免实际绘图 | 通过 | 未生成图像文件或绘图脚本。 |
| 是否避免固化未确认数值 | 通过 | 对 Fig. 4、Fig. 6、Fig. 7 和 Table 2/4 均保留待确认标记。 |
| 是否吸收 02b bib 修订 | 通过 | 明确 Table 1 使用 Yang 2025、Yi 2024、Burton 2024 的修订版本。 |

## 3. 可直接纳入阶段整合的内容

1. 主文图表分工：Fig. 1-3 负责物理建模与 OCS 可观测性；Fig. 4-6 负责反演结果、图像退化和 OCS-noise fusion gain；Fig. 7 只放确认后的 sensitivity / ablation 摘要。
2. Fig. 4 应补入 v0.2 图表规划，因为 v0.1 中缺少单独 caption intent。
3. Table 1 保守定义为 scope-comparison，不做未核实技术审计。
4. Table 2-4 主文保留压缩版，完整 seed / ablation / stress-test 表放 Supplementary。
5. Caption 草案中对 clean rendered images、controlled stress tests、semi-oracle `all_raw`、fusion 条件性和 no real telescope validation 的边界处理得当。

## 4. 整合时仍需保留的限制

| 项目 | 状态 | 整合处理 |
|---|---|---|
| Euler convention / coordinate axes | 未最终确认 | Fig. 2 caption 和坐标标注必须保留 `[待作者确认]` |
| TinyCNN 主结果版本 | 未最终确认 | Fig. 4 / Table 2 不写死冲突版本 |
| Weighted kNN Hit@10 | 未最终确认 | Table 2 可移除该列/行，或保留待确认 |
| OCS-noise 0% values / Hit@5 | 未最终确认 | Fig. 6 / Table 4 caption 保留待确认 |
| Fig. 7 ablation 选择 | 未最终确认 | 主文仅保留 2-3 个最强防御点，完整结果 Supplementary |
| Table 1 技术字段 | 部分未全文核实 | 未核实字段写 `Not specified` / `Not central` |
| 数据目录和图源 | 需绘图前本地核查 | 只写候选来源，不写已导出最终图 |

## 5. 与 Claude 输出的互补关系

| 方面 | GPT 更强 | Claude 可补充 |
|---|---|---|
| 风险控制 | 更明确保留待确认项 | 有些 caption 表述更完整 |
| 主文压缩策略 | 更强调压缩版 / Supplementary 分流 | 提供清晰的主文顺序 |
| Caption 草案 | 边界更稳 | 文风更接近最终 caption |
| 补充材料 | 覆盖方向足够 | Claude 的 Fig. S1-S6 / Table S1-S3 编号可吸收 |

## 6. 单边结论

GPT 第 3 阶段输出通过单边审阅。下一步可将 GPT 与 Claude 输出整合为：

```text
阶段整合输出/03_图表制作与Caption定稿_整合清单.md
```

整合时应以 GPT 的风险控制和待确认边界为主，以 Claude 的结构化主文/补充材料顺序作为补充。

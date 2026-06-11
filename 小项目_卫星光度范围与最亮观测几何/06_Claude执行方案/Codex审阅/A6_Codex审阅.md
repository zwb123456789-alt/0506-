# A6_Codex审阅

最后更新：2026-06-09

## 审阅对象

```text
06_Claude执行方案/Claude输出/A6_旧五几何预实验复核.md
06_Claude执行方案/Claude输出/A6_旧五几何预实验复核_运行草稿/
```

## 审阅结论

**通过，允许进入 A7。**

A6 已完成本阶段最小实施目标：证据库存、phase63 top-K 标准化、phase63 部件贡献标准化、phase63 Delta m 标准化记录均已产出。旧五几何完整 `ocs_scan.csv` 只做了只读定位，未复制到小项目内，也未把它们写成已固定证据。

## 已核对的输出

| 输出 | 审阅结果 |
|---|---|
| `outputs/a6_evidence_inventory.csv` | 8 行；列出 phase63 三份已固定派生证据、phase63 完整原始 CSV 已定位未复制、phase24/45/90/120 原始 CSV 已定位未复制 |
| `outputs/a6_phase63_topk_standardized.csv` | 20 行；字段符合 A5 主体要求，`data_source=face-center (legacy)`，`is_near_halfvector=null` |
| `outputs/a6_phase63_component_standardized.csv` | 3 行；金属主体、太阳能板、遮蔽板部件贡献齐全 |
| `outputs/a6_phase63_delta_mag_summary.md` | 明确 Delta m 仅为相对星等差，不作绝对视星等 |

## 核对结果

1. 原大项目旧五几何路径真实存在，均为 `run_20260527_195122` 批次，每个 `ocs_scan.csv` 为 2701 行。
2. A6 没有向原大项目写入文件。
3. A6 没有重新运行 OCS、没有做 roll 扫描、没有做局部细化。
4. A6 没有把 phase63 roll=0 写成三维全局最亮。
5. A6 没有判断 roll 不敏感，并明确不能排除 roll≠0 的更亮姿态或太阳能板 glint。
6. A6 将旧五几何扩展保留为后续决策，不把未复制的原始 CSV 写成已固定证据。

## 已做小修

| 问题 | 修正 |
|---|---|
| phase63 完整 `ocs_scan.csv` 状态容易被理解为已固定到小项目 | 已改为“已定位；派生摘要已固定到小项目，完整 `ocs_scan.csv` 未复制” |
| A7 若不实施 roll 扫描可能被误写成可直接归纳机制 | 已改为若不实施，必须把 roll 未验证作为限制写入 A8/A10 |

## 残余风险

| 风险 | 处理方式 |
|---|---|
| `scripts/` 目录为空，但 CSV 中 `script_name` 写为 `a6_phase63_standardize` | 不阻塞 A6 通过；这些表可作为已审阅数据产物使用。若后续需要复跑或批量扩展旧五几何，A7/A后续阶段应补可执行脚本或把 `script_name` 改成明确的生成记录 |
| 旧五几何完整 CSV 尚未复制到小项目 | A7 若需要旧五几何横向分析，应先复制到小项目 evidence/ 并记录来源路径 |
| phase63 标准化表缺少真实太阳/观测方向向量 | 已标注 `not_recorded`，不得用于 half-vector 判定 |

## 正式归档决定

将 A6 主文档和运行草稿并入：

```text
00_A0-A10正式成果区/A6_旧五几何预实验复核/
```

正式成果包括：

```text
A6_旧五几何预实验复核.md
运行草稿/outputs/a6_evidence_inventory.csv
运行草稿/outputs/a6_phase63_topk_standardized.csv
运行草稿/outputs/a6_phase63_component_standardized.csv
运行草稿/outputs/a6_phase63_delta_mag_summary.md
```

## 下一步

进入 **A7：新几何与 roll 实施计划**。

A7 必须明确：是否实施 roll 扫描、是否复制旧五几何完整 CSV、是否扩展到新几何。如果不实施 roll 扫描，必须把 roll 未验证写入限制，不能把 A6 的 roll=0 结果当作三维结论。

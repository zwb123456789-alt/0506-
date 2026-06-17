# Codex 确认：v0.4 信息量与置信指标实现规范冻结通过

生成时间：2026-06-09

## 1. 确认对象

```text
05_全链路重跑/v0.4_信息量与置信指标实现规范_最终冻结版.md
```

对照复审意见：

```text
97_交互审阅记录/03_Codex审阅/05_全链路重跑/R03_Codex_复审_信息量与置信指标实现规范候选.md
```

## 2. 总体判断

**通过。可以作为 v0.4 代码实施前的指标与反演输出冻结规范。**

最终冻结版已经落实 R03 的关键小修条件：

1. `ECE_thr=0.10`、G3 calibration、reject/conflict 阈值已改为 phase0 / validation-calibrated 项，不再作为代码前硬 gate。
2. image template / image embedding 来源已补充 encoder、split、feature_config 和防 test 泄漏边界。
3. 图表清单已从无条件必出改为三层：代码最小保存字段、主线优先分析图、论文投稿目标图。
4. “作者已拍板”已收紧为“作者已确认高层范式与主实现族”，实现级子参数仍待 phase0 标定。
5. `is_primary_paradigm` 已改为 `is_primary_scoring_method`，避免 paradigm 与 scoring_method 混用。

## 3. 冻结后的有效口径

v0.4 反演与置信指标口径冻结为：

```text
主反演范式：closed-grid candidate scoring
候选集合：2664 个 yaw/pitch 姿态候选
主实现族：distance/kernel likelihood 或 template likelihood
输出契约：同一候选网格上的 posterior-like distribution
增强对照：softmax grid classification 仅作 learned-scoring 对照
置信主线：observability + complementarity + consistency + risk-coverage
阈值策略：所有 calibration / reject / conflict 数值阈值均由 phase0 或验证集标定
```

该规范不替代 13/14，而是在 13/14 的前向模型、manifest/source_data 底座上新增 24 号主线所需的反演分布、置信指标和最小保存字段。

## 4. 当前阶段状态

```text
定位冻结：已完成，source-of-truth 为 24 + 25。
方法冻结：已完成，source-of-truth 为 13 + 14。
代码阶段准备文档：已完成，经 R01 复核通过。
信息量与置信指标规范：已完成，经 R03 小修后由本 R04 确认冻结通过。
```

因此，当前项目可以从“代码实施前指标规范待冻结”推进为：

```text
代码实施前指标规范已冻结；下一步进入 06_v0.4_code/ 代码骨架与 phase0 门控验证准备。
```

## 5. 下一步边界

下一步可以启动代码实施准备，但仍不得直接全量重跑或训练模型。建议顺序为：

1. 搭建 `06_v0.4_code/` 代码骨架。
2. 记录环境依赖与硬件信息。
3. 用 1 个简单姿态完成 smoke test，测量耗时与存储体量。
4. 实现 depth round-trip sanity check。
5. 实现 camera geometry pass、Position/WorldCoord、sun-view depth 和 `V_sun_macro` reprojection。
6. 完成 20 姿态 shadow validation，并确定 `depth_epsilon_m_final`。

阶段 0 的后续 gate 仍然包括：代码 smoke test、depth round-trip、20 姿态 shadow validation。指标规范冻结只代表“代码前指标账面闭合”，不代表代码或实验已经完成。

## 6. 需要同步的文件

本确认后应同步：

```text
CLAUDE.md
00_只打开本文件夹时的启动说明.md
00_v0.4总控流程.md
05_全链路重跑/00_重跑任务清单.md
06_论文v0.4重写接入/00_论文v0.4重写接入说明.md
99_归档索引/01_上下文读取与提示词维护规范.md
99_归档索引/02_项目文件夹职能规范.md
97_交互审阅记录/00_交互审阅记录说明.md
```

同步原则：只更新当前状态、有效 source-of-truth 和下一步，不把指标规范正文搬入启动集，避免默认上下文膨胀。

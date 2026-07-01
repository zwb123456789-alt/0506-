# R44 Codex 审阅：1C-E22 路线一 C 结果边界与后续路径裁决准备

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/45_1C-E22_路线一C结果边界与后续路径裁决准备_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E22：PASS
R38-R43 证据边界整理：PASS
E21 泄漏结果撤回：PASS
后续路径候选：PASS WITH TERMINOLOGY CORRECTION
论文正文改写：NOT RELEASED
新训练 / B1 / GGX / 三轴扩展：NOT RELEASED
下一步建议：1C-E23，B0 evidence packet 与路线决策备忘录整理
```

结论：E22 完成了 R43 要求。报告正确区分了三类结果：

```text
E21 yaw_block：撤回，不能作为泛化证据
E21 random split：可作为 in-distribution engineering baseline
E21-FIX01 strict yaw_block：有效负结果，可作为边界证据
```

四条后续路径的目的、代价和风险也基本清楚。Codex 同意下一步优先执行“路径 A”：把现有 B0 evidence packet 整理成可供后续论文设计和路线决策引用的稳定材料；暂不启动新训练、B1/GGX/fullrun、三轴或论文正文改写。

---

## 1. 通过项

### 1.1 全链证据汇总合格

E22 对 R38-R43 的归纳准确：

- R38：B0 fullrun 2664 数据生成与 checker 通过；
- R39-R41：训练入口、split、smoke 与判据修正通过；
- R42：E21 工程 baseline 可保留，但 yaw_block 泛化 claim 无效；
- R43：strict yaw_block 复评通过，跨未见 yaw 泛化失败成立。

### 1.2 结果分类合格

Codex 接受以下分类：

```text
E21 random split = in-distribution baseline
E21 yaw_block result = train-test leakage artifact
E21-FIX01 strict yaw_block = valid negative/boundary result
```

### 1.3 当前 B0 baseline 边界合格

E22 对当前 B0 baseline 的科学边界判断基本正确：

成立：

- B0 2664 数据与 manifest/checker 稳定；
- random split 下 image_only/joint 能学习 fixed-roll 姿态映射；
- joint 在同分布条件下优于 image_only；
- pitch 在 strict yaw holdout 下有部分迁移；
- 训练工程链路已可复现。

不成立：

- 当前 baseline 不能跨未见 yaw 零样本泛化；
- 当前 4 维 OCS 不提供跨 yaw 不变性；
- E21 原 yaw_block 结果不能作为泛化证据；
- 当前结果不能直接写成论文最终 claim。

---

## 2. 需要更正的术语

E22 报告中“路径 D”把 `B1` 与 `GGX` 混写为 “B1/GGX” 或 “B1 (GGX)”。这不准确。

当前路线一 C 的口径应保持：

```text
B0 = 当前工程 baseline：phong-like provisional / BRDF only
B1 = 书中改进冯模型分支，需确认材料参数与三部件对应
GGX = 另一类对照/错配分支，不等同于 B1
```

因此，后续若走路径 D，应拆为两个不同候选：

```text
D1：B1 书中改进冯模型 fullrun / 对比
D2：GGX 或其他 BRDF mismatch 对照
```

在没有单独 Codex 审阅前，不得把 B1 写成 GGX，也不得把 GGX 写成路线一 C 正式 B1。

---

## 3. 路线裁决建议

Codex 建议当前不立刻走 B/C/D 的新增实验，而先走路径 A：

```text
1C-E23：B0 evidence packet 与路线决策备忘录整理
```

理由：

1. 当前 R38-R43 证据已经足够形成一个稳定 B0 证据包；
2. E21 泄漏纠正和 FIX01 负结果需要被固定成“后续不可误用”的材料；
3. 如果不先整理，后续 B1/GGX/三轴实验容易重复踩 claim 边界；
4. 路线一 C 需要先明确论文 claim 降级后的可写范围，再决定是否投入昂贵的 B1/GGX/fullrun 或多折 yaw block。

---

## 4. 下一步放行范围

放行：

- 整理 evidence packet；
- 整理路线决策备忘录；
- 生成可引用的结果边界表、证据路径表、不可用结果黑名单；
- 规划但不执行 B/C/D 后续实验。

不放行：

- 论文正文改写；
- 新训练；
- 多折 yaw block 训练；
- OCS 新特征实验；
- B1 fullrun；
- GGX fullrun；
- 三轴/路线二/路线三/路线四扩展；
- 修改冻结文件 13/14/24/25。

---

## 5. 1C-E23 输出要求

建议输出：

```text
02_Claude输出/46_1C-E23_B0证据包与路线决策备忘录_Claude执行报告.md
```

内容必须包含：

1. B0 evidence packet 索引；
2. 可用结果表；
3. 不可用/撤回结果表；
4. 当前可写 claim 与禁止 claim；
5. 后续路径 A/B/C/D1/D2 的执行前置条件；
6. 推荐下一步，并说明是否需要 Codex 放行；
7. 红线确认。

---

## 6. 给 Claude 的下一步指令摘要

```text
执行 1C-E23：B0 evidence packet 与路线决策备忘录整理。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R44_Codex_审阅_1C-E22通过并建议进入B0证据包整理.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/45_1C-E22_路线一C结果边界与后续路径裁决准备_Claude执行报告.md
- R38-R43 Codex 审阅文件

任务：
1. 整理 B0 evidence packet 索引，不复制大数据，只列路径、状态、可用性。
2. 明确可用结果、撤回结果、有效负结果。
3. 写出当前可写 claim 与禁止 claim，注意不写论文正文。
4. 将路径 D 拆成 D1=B1 书中改进冯模型、D2=GGX/mismatch 对照，不能混写。
5. 给出后续路径执行前置条件和推荐顺序。

输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/46_1C-E23_B0证据包与路线决策备忘录_Claude执行报告.md

红线：
- 不写论文正文。
- 不启动新训练或实验。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不改冻结文件 13/14/24/25。
- 不写 04_Codex审阅/。
- 不把 B1 与 GGX 混写。
- 不把 E21 泄漏结果当泛化证据。
```


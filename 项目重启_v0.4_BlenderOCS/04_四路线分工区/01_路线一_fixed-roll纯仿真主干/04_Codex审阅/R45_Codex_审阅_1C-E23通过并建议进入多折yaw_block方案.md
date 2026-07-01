# R45 Codex 审阅：1C-E23 B0 证据包与路线决策备忘录

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/46_1C-E23_B0证据包与路线决策备忘录_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E23：PASS
B0 evidence packet：PASS
可用/撤回结果边界：PASS
B1/GGX 术语修正：PASS
论文正文改写：NOT RELEASED
新训练/新渲染：NOT RELEASED
下一步建议：1C-E24，路径 B 多折 circular yaw_block 方案设计
```

结论：E23 完成 R44 要求。报告已经把 R38-R43 的 B0 证据链整理为 stable evidence packet，明确 E21 yaw_block 泄漏结果永久撤回，明确 random split 只能作为 in-distribution baseline，明确 strict yaw_block 负结果可作为边界证据。路径 D 已按 R44 拆分为 D1（B1 书中改进冯模型）与 D2（GGX / mismatch 对照），没有继续把 B1 和 GGX 混写。

当前不建议直接进入论文正文或 B1/GGX 渲染。Codex 建议下一步执行路径 B 的方案设计：先形成多折 circular yaw_block split 与训练协议，经审阅通过后再决定是否运行。

---

## 1. 核验结果

### 1.1 B0 evidence packet 索引合格

E23 已覆盖：

- fullrun 数据资产；
- manifest/checker；
- random split 与 yaw_block split；
- `07_training/` 代码资产；
- E21 与 E21-FIX01 训练结果；
- R38-R44 审阅链；
- Claude 报告链。

这些索引均为原位路径，不复制大数据，符合成果整理要求。

### 1.2 可用结果边界合格

E23 对可用结果的限定符合 R43/R44：

```text
E21 random split = in-distribution engineering baseline
E21-FIX01 strict yaw_block = valid negative result
fullrun checker = stable engineering evidence
```

### 1.3 黑名单合格

E23 已明确列入黑名单：

```text
E21 yaw_block test yaw_acc
"OCS 显著提升跨 yaw 几何泛化"
"joint 比 image_only 在 yaw_block 上高 7.78 pp"
"E21 yaw_block split 为严格泛化评估"
```

这满足 R44 对“不可误用结果”的固定要求。

### 1.4 Claim 边界合格

Codex 接受 E23 的 claim 分级：

- 可写：random split in-distribution 性能；
- 可写：strict yaw_block 负结果；
- 可写：当前 4 维 OCS 不提供跨未见 yaw 零样本泛化；
- 禁止：跨几何泛化、真实望远镜推广、E21 yaw_block 泛化、B1=GGX。

注意：这些“可写 claim”仍只是后续论文材料的边界，不等于本轮已经放行论文正文写作。

---

## 2. 路径 D 术语修正验收

E23 已按 R44 修正：

```text
D1 = B1 书中改进冯模型 fullrun / 对比
D2 = GGX 或其他 BRDF mismatch 对照
```

并明确：

```text
B1 是书中改进冯模型，不可写成 GGX
GGX 不等于 B1，不可混写为 B1/GGX
```

该项通过。

---

## 3. 当前路线建议

Codex 接受 E23 的优先级判断，但将下一步收窄为“方案设计”，不是直接训练：

```text
优先路径：B，多折 circular yaw_block
当前动作：只做 split/训练协议设计，不运行训练
```

理由：

1. 当前 strict yaw_block 只有一折，负结果成立但需要稳健化；
2. 多折评估计算成本低于 B1 fullrun；
3. 多折结果可直接决定论文中负结果边界的强度；
4. 若多折也失败，则可更有底气转向 D1 或 C；
5. 若多折出现局部成功，则能定位 yaw 泛化的角度依赖性。

---

## 4. 下一步：1C-E24

下一步建议：

```text
1C-E24：多折 circular yaw_block 方案设计
```

放行范围：

- 设计 k-fold circular yaw block split；
- 给出每折 yaw train/val/test 范围；
- 估算样本量、训练成本、输出目录；
- 规划训练协议；
- 规划 overlap 检查；
- 不运行训练。

不放行：

- 多折训练；
- 新模型训练；
- B1 fullrun；
- GGX fullrun；
- 论文正文改写；
- 修改冻结文件。

---

## 5. 给 Claude 的下一步指令摘要

```text
执行 1C-E24：多折 circular yaw_block 方案设计，不运行训练。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R45_Codex_审阅_1C-E23通过并建议进入多折yaw_block方案.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/46_1C-E23_B0证据包与路线决策备忘录_Claude执行报告.md
- v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json
- 06_v0.4_code/07_training/split_dataset.py
- 06_v0.4_code/07_training/train_baseline.py

任务：
1. 设计 k-fold circular yaw_block split，建议 k=5，但可论证其他 k。
2. 列出每折 train/val/test yaw 范围、yaw 数、样本数、pitch 覆盖。
3. 明确 circular 边界处理，避免 0/355 seam 偏置。
4. 设计每折 record_id overlap 检查规则。
5. 设计训练协议：mode、epoch 上限、seed、lr、输出目录、checkpoint/metrics 文件名。
6. 估算计算成本。
7. 明确本轮不运行训练、不生成新 split manifest 也可以；如生成候选 split manifest，必须标记为 proposal，不得用于训练。

输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/47_1C-E24_多折circular_yaw_block方案设计_Claude执行报告.md

红线：
- 不运行训练。
- 不写论文正文。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不改冻结文件 13/14/24/25。
- 不写 04_Codex审阅/。
- 不把 E21 泄漏结果当泛化证据。
- 不把 B1 与 GGX 混写。
```


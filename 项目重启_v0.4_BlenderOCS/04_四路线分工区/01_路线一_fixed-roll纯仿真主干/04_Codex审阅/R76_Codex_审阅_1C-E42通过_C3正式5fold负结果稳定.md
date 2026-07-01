# R76 Codex 审阅：1C-E42 通过，C3 正式 5-fold 负结果稳定

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  75_1C-E42_C3正式5fold训练执行登记_Claude执行报告.md

结果目录：
v0.4_results/06_c3_preflight/c3_image_formal_5fold/
v0.4_results/06_c3_preflight/c3_joint_formal_5fold/
```

## 0. 裁决

```text
1C-E42: PASS
C3 image_only正式5-fold: ACCEPTED
C3 joint正式5-fold: ACCEPTED
C3 formal result: STABLE NEGATIVE RESULT
raw 4-dim OCS-only补跑: NOT RELEASED
--mode all: NOT RELEASED
后验架构/超参搜索: NOT RELEASED
论文正文正式改写: NOT RELEASED
三轴小项目/路线二/路线三/路线四: NOT RELEASED
```

E42 已按 R75 Option B-min 完成 10/10 个正式训练。输出文件齐全，协议参数一致，overlap strict 成立，无 OOM 或失败。C3 正式结果可接受为当前固定协议下的稳定负结果。

## 1. 核验结果

逐 fold JSON 抽查确认：

| 通道 | Folds | mode | epochs | lr | seed | overlap | mean yaw_acc | mean pitch_acc | mean yaw_cmae |
|---|---:|---|---:|---:|---:|---|---:|---:|---:|
| C3 image_only | 5 | image_only | 20 | 0.001 | 42 | strict | 0.00% | 21.20% | 81.44 deg |
| C3 joint | 5 | joint | 20 | 0.001 | 42 | strict | 0.00% | 19.42% | 81.39 deg |

文件齐全性通过：

```text
每个 image_only fold:
checkpoint_image_only.pt
e21_fix01_baseline_results.json
e21_fix01_detail_image_only.json
e21_fix01_overlap_report.json

每个 joint fold:
checkpoint_joint.pt
e21_fix01_baseline_results.json
e21_fix01_detail_joint.json
e21_fix01_overlap_report.json
```

JSON warnings 中所有 folds 均出现不同程度的 `possible overfit` 诊断。该 warning 不阻断 E42 通过；它与 cross-yaw holdout 下 exact-bin yaw 零命中相容，应作为“训练集/验证损失分离、跨 yaw 泛化失败”的辅助诊断，不得被解释为正向泛化证据。

## 2. 稳定口径

可作为后续 Results 非正文材料的稳定事实：

```text
Under the formal C3 fixed protocol and circular yaw-block holdout,
both image-only and image+raw-OCS joint models yielded 0.00% exact-bin
yaw accuracy across all five folds.
```

中文口径：

```text
在 C3 正式固定协议与 circular yaw-block holdout 下，
image_only 与 image+raw-OCS joint 两条 5-fold 训练线均未取得 exact-bin yaw 跨 yaw 泛化命中。
```

允许写：

```text
C3 image_only: 5/5 folds yaw_acc=0.00%, mean pitch_acc=21.20%.
C3 joint:      5/5 folds yaw_acc=0.00%, mean pitch_acc=19.42%.
Joint did not improve exact-bin yaw generalization over image_only under this protocol.
Pitch accuracy is a secondary diagnostic and does not alter the yaw-based negative result.
```

## 3. Claim 边界

不得写成：

```text
图像通道不含姿态信息。
OCS 或 raw OCS 在所有模型下无效。
joint 融合被证明没有任何价值。
该结果证明真实未知目标姿态反演不可行。
C2 enhanced OCS 与 C3 raw 4-dim OCS 是同一 OCS-only 结果链。
C3 结果可以外推到三轴姿态、GEO 真实数据或暗室实验。
```

更稳妥的解释边界：

```text
当前结果只约束 phase63 fixed-roll 数据、circular yaw-block split、
固定 6-layer CNN / early-fusion joint 模型、20 epochs、LR=0.001、seed=42 的协议范围。
在该范围内，image_only 与 joint 均未产生 exact-bin yaw 跨块泛化。
```

## 4. 下一步放行

放行窄任务：

```text
1C-E43：C3正式结果证据包与claim边界整理
```

E43 只整理证据，不运行训练，不改代码，不写论文正文正式段落。目标是把 C2/C3 的可引用数值、表格骨架、claim 边界和图表建议整理成成果候选，交回 Codex 再决定是否进入 `01_成果区/`。

## 5. 给 Claude 的 E43 短提示词

```text
执行 1C-E43：C3正式结果证据包与claim边界整理。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R70_Codex_规则_Claude执行端已知问题与规避规则.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R76_Codex_审阅_1C-E42通过_C3正式5fold负结果稳定.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/08_C1C2_OCS-only证据包与claim边界_R62通过.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/09_C1C2_OCS-only_Results非正文材料包_E35_R65通过.md

结果目录：
- v0.4_results/06_c3_preflight/c3_image_formal_5fold/
- v0.4_results/06_c3_preflight/c3_joint_formal_5fold/

任务：
1. 生成 C3 正式结果证据包候选，列出 image_only 与 joint 的 per-fold 和 aggregate 数值。
2. 与 C2 enhanced OCS-only null result 做边界清晰的对照表；必须标注 C2 enhanced OCS 与 C3 raw 4-dim joint OCS 不是同一 OCS-only 口径。
3. 整理可写 claim、不可写 claim、诊断 warning 解释边界。
4. 给出后续 Results 表格/图表建议，但不得写论文正文正式段落。
5. 输出到：
   /d/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/76_1C-E43_C3正式结果证据包与claim边界_Claude执行报告.md

红线：
- 不运行任何训练。
- 不运行 raw 4-dim ocs_only，不运行 --mode all。
- 不修改代码、数据、split、模型或结果 JSON。
- 不把 C3 negative result 外推到所有图像模型、所有 OCS 模型、真实 GEO 或三轴姿态。
- 不写论文正文正式段落。
- 报告简短必要，不复述 C1/C2 全历史。
```

## 6. CLAUDE.md 同步

项目规则要求阶段通过后同步 `CLAUDE.md`；但 `CLAUDE.md` 属于非审阅文件，当前红线要求修改前先获作者确认。建议作者确认后，将当前状态更新为 E42 通过、C3 正式 5-fold 负结果稳定、下一步 E43 证据包整理。

# Step 1 GPT 单边初审记录

审阅日期：2026-06-01  
审阅对象：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\GPT交互\GPT writing\01_Step1_GPT输出_论文定位标题摘要贡献点.md
```

## 1. 初步结论

GPT 的 Step 1 输出整体达标，可以进入 GPT Step 2：Introduction 指导与初稿。该版本较克制，没有发明新实验、没有把 clean ResNet 结果写成真实场景性能，也没有把 fusion 写成永远最优。

当前不与 Claude 比较优劣。按总控流程，仅对 GPT 这一边给出单边审阅和下一阶段指导。

## 2. 主要优点

1. **路线分层清楚**  
   保守版、平衡版、冲击版三条路线有助于后续根据目标期刊调整语气。推荐 Route B 合理。

2. **投稿定位稳**  
   明确主攻 SCI 二区、按一区边缘标准组织，并主动承认 no real optical telescope validation。

3. **标题候选可用**  
   Title 1 稳妥，Title 3 概念更强。都没有使用 novel / state-of-the-art 等过度承诺词。

4. **摘要骨架相对克制**  
   没有塞入过多补充实验细节，只使用主指导文件中的核心数值。

5. **Claim-Evidence-Risk Map 很适合后续使用**  
   每条 claim 都配了 safe wording 和 boundary，适合转化为 Introduction 与 Discussion 的写作防线。

## 3. 需要微调的问题

| 问题 | 位置/内容 | 风险 | 建议 |
|---|---|---|---|
| “degraded observation conditions” 仍略宽 | Manuscript positioning / Route B | 当前主要证据是 Gaussian noise、brightness、OCS noise，不是完整观测退化模型 | 在 Introduction 中改成 `controlled degradation tests` 或 `observation-quality variations` |
| “OCS remains robust” 需要限定 | Contribution 4 / Claim map | 真实 OCS 测量也会有测光误差 | 写成 `within the controlled benchmark`，并说明 real OCS calibration remains future work |
| Related Work gap 不能写得过绝对 | Abstract Sentence 2 | “existing controlled studies often do not...” 需要文献支撑 | Step 2 Introduction 中使用 `often` / `typically`，并留出 citation placeholders |
| r=0.003 来源需标注 | Contribution 4 / Claim map | 该互补性诊断来自早期 OCS-CNN，不应默认代表 ResNet pair | 后续写作中标注 `[from TinyCNN/OCS diagnostic; verify if used for ResNet discussion]` |
| Title 1 的 “Robust” 需小心 | Title 1 | 如果没有完整真实退化模型，robust 可能显得过强 | 可选压缩为 `BRDF-Driven OCS and Photometric Image Simulation for Space Object Attitude Inversion` |

## 4. 红线检查

| 红线 | 是否出现 | 说明 |
|---|---|---|
| 声称真实光学观测已验证 | 否 | 明确 no real optical validation |
| 声称 clean ResNet 是真实场景性能 | 否 | 写成 synthetic upper-bound |
| 声称 fusion 永远最优 | 否 | 写成 conditional complementarity |
| 声称 OCS 总是强于图像 | 否 | 承认 clean ResNet 很强 |
| 发明未给出的实验数值 | 否 | 数值均来自提示清单 |
| 忽略 fixed roll / phase63 / nominal materials | 否 | 有明确 boundary |

## 5. 是否进入 GPT Step 2

可以进入 GPT Step 2。

Step 2 应要求 GPT 输出两种 Introduction 版本：

1. **保守审稿安全版**：强调 controlled simulation benchmark，降低真实验证缺失风险。
2. **平衡投稿版**：保留 conditional complementarity 的科学问题，更适合作为主稿基础。

Introduction 必须使用漏斗结构：

```text
field/application need
-> optical attitude inversion bottleneck
-> OCS and image lines of work
-> unresolved gap: lack of unified physical benchmark and conditional complementarity analysis
-> present study and contributions
```

## 6. 给 GPT Step 2 的关键约束

1. 不要写完整 Related Work，只写 Introduction。
2. 文献引用先用 `[CITATION: ...]` 占位，不发明具体文献。
3. 不把 clean image result 放太早；应先建立 gap，再介绍本文结果。
4. Contribution paragraph 要保留四条，但不要写成过强 novelty claim。
5. Limitations 不要全部塞进 Introduction，只在最后用一句 boundary 控制。


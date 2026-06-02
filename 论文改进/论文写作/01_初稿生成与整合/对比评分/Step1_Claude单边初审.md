# Step 1 Claude 单边初审记录

审阅日期：2026-06-01  
审阅对象：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\Claude交互\claude writing\01_Step1_输出_标题摘要贡献点.md
```

## 1. 初步结论

Claude 的 Step 1 输出整体可用，主线基本符合 `20260529_论文写作完整规划.md` 的新版定位：没有再沿用“OCS 主力、图像辅助、fusion 永远最优”的旧叙事，也明确把 clean image 结果写成 upper-bound，并承认 no real optical telescope validation。

但它把一些补充实验和项目总览中的数值提前写入了 Step 1，其中部分数值不在当前 Step 1 指导文件的“允许使用清单”内。多数可在项目文件中找到来源，但正式进入摘要/贡献点前需要确认是否作为正文主证据使用，避免 Step 1 过度展开。

## 2. 主要优点

1. **论文定位准确**  
   使用了 physically consistent simulation、controlled inversion、ideal/degraded observation conditions、simulation boundary 等关键限定。

2. **标题方向基本合适**  
   5 个标题均没有使用 state-of-the-art、novel、first 等过度承诺词。  
   推荐优先考虑 Title 1 或 Title 5，保守且适合 Acta Astronautica / ASR。

3. **核心科学问题比“融合方法”更高级**  
   它把问题写成 conditional complementarity，而不是提出一个 fusion module。这符合当前投稿定位。

4. **贡献点结构完整**  
   覆盖 unified physical forward model、controlled benchmark、clean-image upper bound and fragility、robust OCS and conditional fusion 四条主线。

5. **审稿风险意识强**  
   对 no real optical validation、clean synthetic upper bound、fixed roll、single phase image branch、nominal material parameters 都有回应策略。

## 3. 需要核验或降调的问题

| 问题 | 位置/内容 | 风险 | 建议 |
|---|---|---|---|
| 摘要骨架过早写入 `Hit@5 = 99.7%` | Sentence 4 | 该数值来自补充实验/日志，不在 Step 1 原提示清单里 | 可保留为候选证据，但在最终摘要中先用 `improves Hit@5` 或放 Results |
| `brightness ×0.5 = 3.45°` | Contribution 3 / Claim map | 有来源，但不是主规划中的核心证据 | 不建议放 Abstract；可放 Results 的 robustness 小节 |
| `single-geom total OCS mean=79°`、`concat5 total=26.5°` | Claim-Evidence Map | 部分有来源，但需确认具体特征定义和实验设置 | 放 Results/ablation，不放 Step 1 摘要核心 |
| `ResNet pair not yet measured` | Claim 8 boundary | 这个提醒很好，但也暴露 r=0.003 来自 TinyCNN+OCS，不是 ResNet | 后续写互补性时必须明确这一点，或补测 ResNet+OCS error correlation |
| “OCS remains robust at 5.91° regardless of image quality” | one-sentence argument | 表述合理但容易被误解为真实 OCS 噪声下也稳 | 改成 “OCS-only result is unaffected by image degradation in the controlled simulation” |
| “realistic degradation” | positioning / abstract | 1% Gaussian noise 只是简单退化，不等于完整 realistic degradation | 改成 “simple image degradation tests motivated by realistic observation artifacts” |

## 4. 红线检查

| 红线 | 是否出现 | 说明 |
|---|---|---|
| 声称已完成真实光学观测验证 | 否 | 明确写 no real optical telescope validation |
| 声称 ResNet clean 等同真实场景性能 | 否 | 写为 upper-bound |
| 声称 fusion 永远最优 | 否 | 写为 conditional complementarity |
| 声称 OCS 总是强于图像 | 否 | 承认 clean image ResNet 很强 |
| 发明完全不存在的新实验 | 未发现明显问题 | 但使用了提示词之外的补充数值，需要核验是否进入正文 |
| 忽略 fixed roll / phase63 / nominal materials | 否 | 均有说明 |

## 5. 建议采用策略

Claude 版本可作为 Step 1 的强候选基础，尤其适合：

- Manuscript positioning
- Core scientific question
- Contributions
- Reviewer-risk notes

需要后续修订：

1. Abstract skeleton 降调，避免把过多结果塞进摘要。
2. 把 `Hit@5=99.7%`、`brightness ×0.5=3.45°`、`single-geom mean=79°` 等补充证据移到 Results 候选，而不是 Step 1 核心摘要。
3. 将 “realistic degradation” 改为更准确的 “simple degradation tests” 或 “degradation tests motivated by real observations”。
4. 明确 `r=0.003` 的来源是早期 TinyCNN+OCS 诊断，不要默认推广到 ResNet。

## 6. 等待 GPT 输出后正式对比

当前还不能最终判定采用 Claude 版本，因为 GPT Step 1 输出尚未提交。正式对比时应重点比较：

1. 谁的标题更适合 SCI 二区投稿。
2. 谁对 no real optical validation 的边界更稳。
3. 谁的摘要骨架更适合作为后续 Introduction 的锚点。
4. 谁更少使用未经核验或过细的补充数值。
5. 谁的 claim-evidence-risk map 更利于后续审稿防御。


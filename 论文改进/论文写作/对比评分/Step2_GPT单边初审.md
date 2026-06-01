# Step 2 GPT 单边初审：Introduction 结构与初稿

> 审阅对象：`GPT交互/GPT writing/02_Step2_GPT输出_Introduction结构与初稿.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 GPT 这一侧输出，不与 Claude 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

GPT Step 2 输出通过单边初审，可以进入 GPT Step 3：Related Work + Table 1。

本次 Introduction 输出总体符合当前论文定位：以统一 BRDF-driven OCS-image simulation 为主线，把 clean synthetic image 性能解释为 idealized upper-bound，把 OCS 定位为 robust / interpretable / low-cost / multi-geometry photometric constraint，并将 fusion 写成 conditional complementarity，而不是 universal superiority。

建议后续以 **Version B: Balanced Submission Introduction** 作为 GPT 侧主稿基础，同时吸收 Version A 中更稳健的边界表达。

## 2. 主要优点

1. 主线清楚：从 optical attitude inversion 的任务需求，推进到 OCS 与 photometric images 的信息差异，再落到 unified forward model 和 controlled benchmark。
2. 边界意识较好：明确说明没有 real optical telescope validation，clean image 结果不是 field performance。
3. 对 OCS、image、fusion 的定位基本正确：没有写成 OCS 永远更强，也没有写成 fusion 永远最好。
4. 技术缺口表述合理：强调如果 OCS 和 images 不共享 geometry、material、BRDF、attitude convention 与 self-occlusion，则很难公平判断模态互补性。
5. 引用处理安全：使用 citation placeholders，没有发明具体文献。

## 3. 需要修改或后续控制的问题

### 3.1 Version B 的结果数字略密

Version B 在 Introduction 中同时放入了：

- ResNet clean：`1.69 +/- 0.07 deg`, Hit@5 `97.6%`
- 1% Gaussian noise：`85.85 deg`, Hit@5 `2.2%`
- ResNet + OCS：`1.47 +/- 0.07 deg`
- worst-case：`9.9 deg -> 6.6 deg`
- TinyCNN/OCS diagnostic：`r = 0.003`

这些数字都没有越界，但 Introduction 可能显得过早进入 Results。后续正式稿建议保留 2-3 个最能支撑主线的数字：

- 必留：ResNet clean `1.69 +/- 0.07 deg`, Hit@5 `97.6%`
- 必留：1% Gaussian noise collapse `85.85 deg`, Hit@5 `2.2%`
- 可选留一个：ResNet+OCS `1.47 +/- 0.07 deg` 或 worst-case `9.9 -> 6.6`
- 建议移到 Results/Discussion：`r = 0.003`

### 3.2 `degraded observation conditions` 需要继续限定为 controlled degradation

GPT 已经多处写出 controlled / simulation-focused，但后续 Related Work、Method、Results 中还要避免把当前噪声实验写成完整真实地基观测退化。更安全表述是：

> controlled degradation or observation-quality variation

不要直接写：

> realistic ground-based performance has been validated

### 3.3 `r = 0.003` 只能作为早期诊断

GPT 已正确写成 earlier TinyCNN/OCS diagnostic。后续如果继续使用这个结果，必须维持限定：

> In an earlier TinyCNN/OCS diagnostic, a near-zero error correlation suggested complementary failure modes.

不能写成 ResNet-image 与 OCS 的正式相关性结论。

### 3.4 Citation placeholders 需要在 Step 3 落到真实文献

Step 2 中的引用占位包括：

- optical space object characterization
- optical light-curve attitude inversion
- BRDF-based space object photometry
- image-based spacecraft pose estimation
- ground-based optical observation degradation
- multi-modal fusion robustness

Step 3 必须用已有文献清单逐步替换或标注这些占位，不能让 GPT 自行编造作者、题名、期刊、DOI。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明新实验或新数值 | 未发现 |
| 是否发明具体引用 | 未发现，使用占位符 |
| 是否把 clean image 写成真实场景性能 | 未发现 |
| 是否宣称 fusion 永远最优 | 未发现 |
| 是否宣称 OCS 永远强于图像 | 未发现 |
| 是否宣称已有真实光学望远镜验证 | 未发现 |
| 是否把 ISAR 并入主线 | 未发现 |
| 是否使用过度承诺词 | 未见明显问题 |

## 5. 给 GPT 的后续修订意见

进入 Step 3 前，GPT 应记住以下修订方向：

1. Introduction 主稿采用 Version B，但正式合稿时降低数字密度。
2. 保留 clean image upper-bound 与 degradation fragility 的主线。
3. 把 `r = 0.003` 暂时移出 Introduction，留到 Results/Discussion 的 diagnostic analysis。
4. Step 3 的 Related Work 必须围绕机制和假设差异展开，而不是按年份堆文献。
5. Table 1 的任务不是证明本文 SOTA，而是证明本文在 unified OCS-image physical framework 与 conditional complementarity analysis 上有清晰位置。

## 6. 是否进入下一阶段

结论：可以进入 GPT Step 3。

下一阶段应生成：

`GPT交互/03_Step3_GPT_RelatedWork_Table1交互提示词.md`

GPT 输出建议保存为：

`GPT交互/GPT writing/03_Step3_GPT输出_RelatedWork_Table1.md`

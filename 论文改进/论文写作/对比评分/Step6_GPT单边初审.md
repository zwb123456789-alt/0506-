# Step 6 GPT 单边初审：Discussion / Limitations / Conclusion

> 审阅对象：`GPT交互/GPT writing/06_Step6_GPT输出_Discussion_Limitations_Conclusion.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 GPT 这一侧输出，不与 Claude 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

GPT Step 6 Discussion / Limitations / Conclusion 输出通过单边初审。GPT 侧已经完成 Step 1-6 的完整章节链条，可以进入 Step 7：全文整合初稿与一致性自检。

本次 Step 6 基本完成阶段目标：Discussion 没有按 Results 表格顺序重复数值，而是解释 clean ResNet 为什么强、OCS 为什么仍有价值、fusion 为什么是条件性互补，以及无真实光学数据时本文应如何限定为 simulation-focused controlled benchmark。

## 2. 主要优点

1. Discussion 主线清楚：从 controlled complementarity 出发，而不是重复模型排行。
2. Clean image 口径安全：ResNet-18 `1.69 ± 0.07 deg` 被写成 idealized upper-bound，不是 field performance。
3. OCS 价值定位正确：强调 low-dimensional、interpretable、multi-geometry、independent of image-pixel degradation in this benchmark，而不是 clean 条件下击败 ResNet。
4. Fusion 没有夸大：写成 conditional reliability mechanism，明确不是 universal accuracy maximizer。
5. Limitations 完整：覆盖 no real telescope validation、fixed roll、phase63、nominal materials、未显式建模 atmosphere / detector / PSF / earthshine / background contamination。
6. `all_raw`、`r = 0.003` 和 image degradation 的边界均未明显越界。
7. Conclusion 简洁，包含 unified benchmark、clean-image upper-bound、image degradation fragility、practical OCS 和 conditional fusion。

## 3. 需要修改或后续确认的问题

### 3.1 “publishable without field validation” 需要降调

Claim-Evidence-Risk Map 中有一句：

```text
Study is publishable without field validation.
```

这类话不建议进入正式稿或作者给审稿人的回应。更安全的内部表述是：

```text
The work can be positioned as a simulation-focused controlled benchmark, with field validation stated as future work.
```

不要让正式论文显得在替审稿人判断“可发表”。

### 3.2 “OCS provides fallback” 类措辞需谨慎

Discussion 中提到 OCS 可作为 fallback / complementary constraints。正式稿可以保留 complementary，但 `fallback` 容易被理解成已经具备真实系统部署意义。建议改为：

```text
OCS can provide an additional photometric constraint when high-quality resolved images are unavailable or degraded.
```

### 3.3 1% Gaussian noise 的解释仍需避免过度外推

文本已经写成 controlled stress test，这是正确的。后续全文整合时，凡是出现 “ResNet collapse” 都要紧接限定：

```text
under this controlled additive-noise test
```

不要写成所有真实图像或所有图像模型都会崩溃。

### 3.4 Conclusion 数字可再精简

Conclusion 目前包含 `1.69 ± 0.07 deg`、`85.85 ± 3.00 deg`、`9.9 deg -> 6.6 deg`。这是可接受的，但全文整合时可根据目标期刊压缩到 2-3 个核心数字，避免结论段像 Results 摘要。

### 3.5 Step 7 必须处理跨章节一致性

GPT 侧 Step 1-6 是分阶段生成，全文整合时必须统一：

- 标题是否固定。
- `optical cross section` 与 `OCS` 首次出现写法。
- `phase63` 是否统一写成 `one rendered phase condition` 或保留项目代号。
- `angular error formula` 是否仍有 `[需要作者确认]`。
- `Table 1` 的 `[to verify]` 是否保留为作者核对项，不进入投稿稿。
- `all_raw` 是否全篇均为 semi-oracle。
- `r = 0.003` 是否全篇均限定为 TinyCNN/OCS diagnostic。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否把 clean image 写成 field performance | 未发现 |
| 是否宣称真实光学验证 | 未发现 |
| 是否夸大 fusion | 未发现 |
| 是否把 OCS 写成永远优于图像 | 未发现 |
| 是否把 OCS 写成对所有噪声免疫 | 未发现 |
| 是否把 `all_raw` 写成实用特征 | 未发现 |
| 是否把 `r = 0.003` 写成 ResNet-pair 证据 | 未发现 |
| 是否新增未给出的实验或数值 | 未发现 |
| 是否把 ISAR 并入主线 | 未发现 |

## 5. 给 GPT 的后续修订意见

进入 Step 7 全文整合时，GPT 应记住：

1. 只整合已经生成的 Step 1-6 内容，不新增实验、引用或数值。
2. 将输出从“阶段产物集合”整理成连续 manuscript draft。
3. 保留 `[CITATION: ...]` 和 `[需要作者确认：...]`，不要自行补文献或猜测结果。
4. 压缩 Introduction / Results / Discussion 中重复出现的同一组核心数字。
5. 统一所有边界：no real telescope validation、clean image upper-bound、fixed roll、phase63、nominal materials。
6. 把 reviewer-facing defense points 放在附录式“作者修订清单”，不要混入正式论文正文。
7. 不进行 GPT vs Claude 比较；GPT 侧整合稿只是候选完整初稿。

## 6. 是否进入下一阶段

结论：可以进入 GPT Step 7。

下一阶段指导文件：

```text
GPT交互/07_Step7_GPT_全文整合初稿交互提示词.md
```

GPT 输出建议保存为：

```text
GPT交互/GPT writing/07_GPT输出_全文整合初稿.md
```

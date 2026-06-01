# Step 5 GPT 单边初审：Results

> 审阅对象：`GPT交互/GPT writing/05_Step5_GPT输出_Results.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 GPT 这一侧输出，不与 Claude 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

GPT Step 5 Results 输出通过单边初审，可以进入 GPT Step 6：Discussion / Limitations / Conclusion。

本次 Results 的主线基本正确：它没有把论文写成单一模型性能展示，而是按照 `forward-model credibility -> OCS-only -> image-only clean upper bound -> fusion -> degradation robustness -> ablation/sensitivity` 的证据链推进。整体口径符合 SCI 二区主攻、按一区边缘标准组织论证的投稿定位。

## 2. 主要优点

1. 证据顺序清楚：先证明统一 forward model 的受控可信度，再进入 OCS、图像和融合结果，避免直接堆模型表格。
2. clean image 口径安全：ResNet-18 `1.69 ± 0.07 deg` 被解释为 idealized clean rendered upper-bound，而不是真实望远镜性能。
3. OCS 定位较稳：`per_part_log` 被写成 practical OCS setting，`all_raw 45D` 被写成 semi-oracle diagnostic upper bound。
4. Fusion 表述没有过度承诺：ResNet + `per_part_log` 的提升被写成 modest but meaningful，重点落在 Hit@5 和 worst-case tail error。
5. 退化实验解释合理：Gaussian noise 和 brightness scaling 被写成 controlled observation-quality stress tests，没有写成完整真实大气或探测器模型。
6. `r = 0.003` 的边界正确：仅作为 earlier TinyCNN/OCS diagnostic，没有默认扩展为 ResNet-pair 证据。
7. Results 末尾已经把 fixed roll、phase63、nominal material parameters 和无真实光学验证写成范围边界。

## 3. 需要修改或后续确认的问题

### 3.1 4.6 中所有 `[需要作者确认]` 不能进入正式主文

目前 4.6 的 ablation/sensitivity 写法可以作为草稿，但正式稿前必须确认哪些项目有最终数值：

- random split
- phase63 fairness
- BRDF sensitivity
- occlusion ablation
- roll sensitivity
- 0% OCS noise 表格中的 OCS-only / fusion mean 和 Hit@5

如果没有最终数值，正文只能写成 limitation 或 supplementary plan，不能写成已经完成的实验证据。

### 3.2 “OCS robustness” 必须进一步限定

当前 Results 中的安全含义应是：

```text
OCS is independent of image-pixel degradation in this benchmark.
```

不能在 Discussion 中升级为：

```text
OCS is immune to all real observation noise.
```

因为 OCS 本身仍可能受光度标定误差、几何误差、BRDF mismatch、测量噪声和相位角误差影响。Step 6 必须把这一点写入 Limitations。

### 3.3 `all_raw` 的半预言机属性需要贯穿 Discussion

Results 已经正确标注 `all_raw`。后续 Discussion 不能把 `all_raw 3.98 ± 0.60 deg` 当成实用 OCS 系统的主要性能。实用 OCS 主结论应围绕：

```text
OCS MLP per_part_log: 5.91 ± 0.22 deg, Hit@5 = 73.8%
```

### 3.4 ResNet 噪声崩溃的解释要避免过度归因

`sigma = 0.01` 下 ResNet 退化到 `85.85 ± 3.00 deg` 是重要证据，但 Discussion 中不能直接推断所有真实图像都会崩溃。更安全的写法是：

```text
The result indicates sensitivity to distribution shift and pixel-level corruption under this controlled stress test.
```

### 3.5 Figure 7 的主文位置需后续决策

如果 BRDF / occlusion / roll / split sensitivity 的最终数值完整，可以保留为正文 Fig. 7 或 Table 4 的一部分。若数值不完整，建议放 Supplementary 或在 Limitations 中诚实说明。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明新实验或新结果 | 未发现；不确定值已标注 `[需要作者确认]` |
| 是否把 clean image 写成 field performance | 未发现 |
| 是否宣称真实光学望远镜验证 | 未发现 |
| 是否宣称 fusion 永远最优 | 未发现 |
| 是否宣称 OCS 永远强于图像 | 未发现 |
| 是否把 TinyCNN 当作图像能力上限 | 未发现 |
| 是否把 `all_raw` 当作实用特征 | 未发现 |
| 是否把 `r = 0.003` 写成 ResNet-pair 证据 | 未发现 |
| 是否把 controlled degradation 写成完整真实退化模型 | 未发现 |
| 是否把 ISAR 并入 Results 主线 | 未发现 |

## 5. 给 GPT 的后续修订意见

进入 Step 6 前，GPT 应记住：

1. Discussion 不能重复 Results 的表格顺序，而要回答“这些结果说明什么、边界在哪里、为什么仍有投稿价值”。
2. 必须解释 clean ResNet 为什么强，同时马上限定它是 clean rendered upper-bound。
3. 必须说明 OCS 的价值不是 clean 条件下击败 ResNet，而是低维、可解释、多几何、对图像像素退化不敏感的物理约束。
4. Fusion 只能写成 conditional complementarity，重点是 tail error、Hit@5 和退化条件下的价值，不写 universal superiority。
5. Limitations 必须包含：无真实光学数据、fixed roll、phase63、nominal material parameters、未显式建模 atmosphere / detector / PSF / earthshine / background contamination。
6. 不能新增引用和结果；所有文献关系使用 `[CITATION: ...]` 占位。
7. 对 4.6 中未确认的 sensitivity / ablation 项，Discussion 只能作为未来补充或范围边界，不得假装已有完整结果。

## 6. 是否进入下一阶段

结论：可以进入 GPT Step 6。

下一阶段指导文件：

```text
GPT交互/06_Step6_GPT_Discussion_Limitations_Conclusion交互提示词.md
```

GPT 输出建议保存为：

```text
GPT交互/GPT writing/06_Step6_GPT输出_Discussion_Limitations_Conclusion.md
```

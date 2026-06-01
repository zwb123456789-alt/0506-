# Step 6 Claude 单边初审：Discussion / Limitations / Conclusion

> 审阅对象：`Claude交互/claude writing/06_Step6_Claude输出_Discussion_Limitations_Conclusion.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 Claude 这一侧输出，不与 GPT 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

Claude Step 6 输出通过单边初审，可以进入 Claude Step 7：全文整合初稿。

Discussion / Limitations / Conclusion 的主线基本正确：clean image 被定位为 idealized upper-bound，OCS 被定位为低维、可解释、多几何、在本 benchmark 中独立于 image-pixel degradation 的约束，fusion 被写成 conditional complementarity，而不是 universal best。No real telescope validation、fixed roll、phase63、nominal material、未建模真实观测退化等限制也有明确交代。

但进入全文整合时，必须对若干“未确认数值”和“外推表述”降调或标注为作者确认项，避免在正式正文中过度承诺。

## 2. 主要优点

1. Discussion 没有机械重复 Results，而是围绕“为什么 clean image 强、为什么 OCS 仍重要、为什么 fusion 是条件性互补”展开。
2. 对 clean ResNet `1.69 deg` 的解释较稳，明确写成 idealized clean-image upper bound。
3. 对 OCS 的定位正确：不是 clean-image accuracy upper bound，而是低维、可解释、多几何、独立于图像像素退化的光度约束。
4. 对 fusion 的定位正确：mean gain modest，但 tail error 和 Hit@5 改善有价值；fusion 不是 universal accuracy maximizer。
5. Limitations 比较完整，覆盖 no real optical validation、fixed roll、phase63、nominal material、未建模 atmosphere / PSF / detector / background 等关键边界。
6. Reviewer-facing defense points 有助于后续模拟审稿与 rebuttal 准备，但不应直接混入正式正文。

## 3. 必须在 Step 7 全文整合中收紧的问题

### 3.1 未确认的 sensitivity / ablation 数值不能直接进正式正文

Claude 在 Step 6 中直接使用了以下数值：

- roll sensitivity: `approximately 20% OCS variation`
- metallic roughness sensitivity: `30-42% OCS variation`
- non-metallic components: `<5%`
- full 3-DOF extension requires `approximately 37x larger datasets`

这些数值在此前 Step 5 审阅中已列为作者确认项。正式整合时有两种处理方式：

1. 若作者确认这些是最终可用结果，则保留并在 Results / Method 中交代来源。
2. 若尚未确认，则写成 `[需要作者确认：roll / BRDF sensitivity values]`，或放入 supplementary / future work。

不要在 Abstract、Conclusion 或主结论句中使用未确认数值。

### 3.2 数据审计数字需要确认来源

Step 6 中写到：

- mean image intensity correlation `r < 0.02`
- centroid displacement correlation with yaw `r ≈ 0.66`

如果这些来自已有数据审计报告，可以保留，但需要在全文整合时标注来源或放入 Results / Supplementary。若尚未正式确认，则改为更保守表述：

```text
Preliminary data-audit checks suggest that the image model is not explained by global intensity alone, although centroid-related geometric cues may contribute under the fixed simulated camera-target geometry.
```

### 3.3 “single-geometry total OCS >36 deg” 表述可能混淆

Step 6 中把 `>36 deg` 写成 “single-geometry total OCS”。当前已知核心结果是：

- `total_log`: `36.69 +/- 3.6 deg`
- `per_part_log`: `5.91 +/- 0.22 deg`

但 `total_log` 是否等同于 “single-geometry total OCS” 需要核对。全文整合时建议改为：

```text
The weak total-log OCS baseline (36.69 +/- 3.6 deg) and the stronger five-geometry per-part representation (5.91 +/- 0.22 deg) indicate that component-level and multi-geometry information are important for OCS-based discrimination.
```

除非作者确认，不要写 `single-geometry total OCS`。

### 3.4 OCS 低成本 / 小口径望远镜价值应降调

Step 6 中写到 OCS 可用 smaller aperture telescopes、operationally feasible for photometric monitoring campaigns。这一方向合理，但当前实验没有真实望远镜或系统工程验证。正式稿建议写成：

```text
OCS-like integrated photometric measurements may be less demanding than fully resolved imagery, but the practical acquisition requirements depend on telescope aperture, target brightness, range, phase angle, calibration accuracy and atmospheric conditions.
```

不要写成已经证明“小口径望远镜可实现本文精度”。

### 3.5 “catastrophic” 频率应降低

`catastrophically fragile` 和 `collapse catastrophically` 有冲击力，但正式稿建议只在一处使用，其他地方改为：

```text
severe degradation
sharp performance drop
performance collapse under controlled additive-noise stress tests
```

### 3.6 Reviewer-facing defense points 不应进入正文

这些内容适合后续模拟审稿、回复审稿人或内部答辩，不适合直接放入 manuscript body。Step 7 整合时应仅保留正文、图表计划、待确认项和一致性检查。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明核心实验或核心结果 | 未发现核心发明；有若干未确认 sensitivity / data-audit 数值需标注 |
| 是否把 clean image 写成 field performance | 未发现 |
| 是否宣称真实光学望远镜验证 | 未发现 |
| 是否夸大 fusion | 基本未发现 |
| 是否把 OCS 写成永远优于图像 | 未发现 |
| 是否把 OCS 写成对所有真实观测噪声免疫 | 未发现，已说明真实 OCS 仍有标定与测量误差 |
| 是否把 `all_raw` 写成实用特征 | 未发现，已作为 semi-oracle / warning 处理 |
| 是否把 `r = 0.003` 写成 ResNet-pair 证据 | 未发现，Discussion 中未升级该证据 |
| 是否把 Gaussian noise 写成 realistic degradation model | 未发现，基本写成 controlled degradation tests |
| 是否把 ISAR 并入主线 | 未发现 |

## 5. 给 Claude Step 7 的约束

进入全文整合时，Claude 必须：

1. 只整合 Step 1-6 已有内容，不新增实验、数值、引用或图表。
2. 把未确认的 sensitivity / data-audit / ablation 数值统一标注为 `[需要作者确认：...]`。
3. 保持 clean images = idealized upper-bound 的全篇一致性。
4. 保持 OCS robustness = independent of image-pixel degradation in this benchmark，不写成真实观测免疫。
5. 保持 fusion = conditional complementarity，不写 universal best。
6. 保持 `all_raw` = semi-oracle diagnostic upper bound。
7. 保持 `r = 0.003` = earlier TinyCNN/OCS diagnostic，不升级成 ResNet-pair evidence。
8. 把 reviewer-facing defense points 放入附录式审稿防御清单，不混入正式正文。
9. 对 `[CITATION: ...]`、`[to verify]`、`[需要作者确认：...]` 原样保留，不自行补文献。

## 6. 是否进入下一阶段

结论：可以进入 Claude Step 7。

下一阶段指导文件：

```text
Claude交互/08_Step7_Claude_全文整合初稿指导.md
```

Claude 输出建议保存为：

```text
Claude交互/claude writing/07_Step7_Claude输出_全文整合初稿.md
```

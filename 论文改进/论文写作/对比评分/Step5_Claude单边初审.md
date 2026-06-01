# Step 5 Claude 单边初审：Results

> 审阅对象：`Claude交互/claude writing/05_Step5_Claude输出_Results.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 Claude 这一侧输出，不与 GPT 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

Claude Step 5 Results 输出通过单边初审，可以进入 Claude Step 6：Discussion / Limitations / Conclusion。

本次 Results 主线清楚，能够按 `forward-model validation -> OCS-only -> image-only clean upper-bound -> fusion -> degradation robustness -> ablation/sensitivity` 推进，基本符合当前论文定位。核心红线总体未越界：ResNet clean 被写成 upper-bound，`all_raw` 被写成 semi-oracle，fusion 被写成 conditional benefit，`r = 0.003` 被限定为 earlier TinyCNN/OCS diagnostic。

## 2. 主要优点

1. 证据链完整：从 forward model consistency 到 OCS / image / fusion / degradation / sensitivity，章节顺序符合论文主线。
2. OCS-only 解释到位：`per_part_log 5.91 ± 0.22°` 被作为 practical OCS-only，`all_raw 3.98 ± 0.60°` 被作为 semi-oracle upper bound。
3. Image-only 边界较安全：ResNet-18 `1.69 ± 0.07°` 被写成 idealized clean-image upper-bound，而不是 field performance。
4. Fusion 解释比较稳：强调 mean gain modest，但 worst-case `9.9° -> 6.6°` 和 Hit@5 改善支持 tail reliability。
5. Degradation 小节抓住核心：1% Gaussian noise 下 ResNet `85.85 ± 3.00°`，同时声明这是 controlled stress test。
6. 表格草稿完整，Table 2 / 3 / 4 的角色区分清楚，适合后续正式整合。

## 3. 需要修改或后续确认的问题

### 3.1 §4.6 的 sensitivity / ablation 数值必须降调

Claude 在 §4.6 中写了若干具体数值：

- random split: `fusion per_part_log 2.13°, Hit@5 = 98.6%`
- BRDF sensitivity: metal roughness `30–42%`
- roll sensitivity: `~20%` mean OCS variation, extreme `26%`
- phase63 single-geometry OCS: `approximately 21.68°`

这些数值是否为最终可进正文的正式结果，仍需作者确认。正式稿前，§4.6 不能写成完全确定的小节。建议暂时改成：

```text
Additional sensitivity analyses are summarized where finalized values are available. Items without finalized values are retained as supplementary checks or author-confirmation items.
```

### 3.2 “OCS 不受图像退化影响”必须限定为 benchmark 内部

Claude 在 Evidence Ladder 中写“OCS 不受图像退化影响 → 证明 OCS 的鲁棒性价值”。这个方向正确，但正式稿应统一写成：

```text
OCS is unaffected by image-pixel degradation in this benchmark because it does not use image pixels as input.
```

不能写成真实 OCS 对光度标定误差、几何误差、BRDF mismatch 或测量噪声免疫。

### 3.3 0% OCS-noise fusion mean 不能以 `[≈3.93]` 进入正文

Table 4 和 §4.5 出现 `[≈3.93]` / “0% fusion mean = 3.93 ± 0.46°?”。这类带问号和约等号的数字不能进入正式稿。

处理方式：

- 若作者确认，则写精确数值。
- 若未确认，则只保留 `gain +1.97°`，并标 `[需要作者确认：0% OCS-noise table values]`。

### 3.4 “catastrophic” 一词可保留但要少用

`catastrophic fragility` 能表达冲击力，但正式稿中建议控制频率，用一次即可。其它地方改为：

```text
severe degradation
performance collapse under the controlled additive-noise test
```

### 3.5 Method / Results 的边界要一致

Claude Results 中用到了 closure tests、mhd sensitivity、random split、roll sensitivity 等。全文整合时必须确认 Method 已经交代对应设置，否则 Results 会显得凭空出现。

尤其需要核对：

- `d_min = 1.0 mm` 与 Method 中 `min_hit_distance` 写法一致。
- `angular error formula` 仍未最终固定。
- `single-geometry OCS` 是 MLP 还是 kNN，不能混淆。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明核心实验或核心结果 | 核心结果未发现；§4.6 有待确认数值 |
| 是否把 clean image 写成 field performance | 未发现 |
| 是否宣称真实光学望远镜验证 | 未发现 |
| 是否夸大 fusion | 基本未发现 |
| 是否把 OCS 写成永远优于图像 | 未发现 |
| 是否把 `all_raw` 写成实用特征 | 未发现 |
| 是否把 `r = 0.003` 写成 ResNet-pair 证据 | 未发现，已限定 |
| 是否说明 image degradation 是 controlled stress test | 已说明 |
| 是否把 ISAR 并入 Results 主线 | 未发现 |

## 5. 给 Claude 的后续修订意见

进入 Step 6 前，Claude 应记住：

1. Discussion 不要再逐节重复 Results 数字，而要解释结果意义。
2. 必须回答：为什么 clean ResNet 很强、为什么 OCS 仍重要、fusion 为什么不是 universal best。
3. 必须把 no real telescope validation、fixed roll、phase63、nominal materials、simplified degradation 写入 Limitations。
4. OCS robustness 只能写为 independent of image-pixel degradation in this benchmark。
5. `all_raw` 继续写成 semi-oracle diagnostic upper bound。
6. `r = 0.003` 继续限定为 TinyCNN/OCS diagnostic，不能升级成 ResNet-pair complementarity。
7. §4.6 中所有未确认数值都只能作为 author-check items 或 future/supplementary checks。

## 6. 是否进入下一阶段

结论：可以进入 Claude Step 6。

下一阶段指导文件：

```text
Claude交互/07_Step6_Claude_Discussion_Limitations_Conclusion指导.md
```

Claude 输出建议保存为：

```text
Claude交互/claude writing/06_Step6_Claude输出_Discussion_Limitations_Conclusion.md
```

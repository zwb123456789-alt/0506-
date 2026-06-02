# Step 7 GPT 单边初审：全文整合初稿

> 审阅对象：`GPT交互/GPT writing/07_GPT输出_全文整合初稿.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 GPT 这一侧完整初稿，不与 Claude 进行优劣比较；对比评分表保留到两边完整初稿都完成后再使用。

## 1. 总体结论

GPT Step 7 全文整合初稿通过单边初审，可以标记为 **GPT 侧候选完整初稿已完成**。

这版稿件已经形成连续英文 manuscript draft，覆盖 Title、Abstract、Introduction、Related Work、Method、Results、Discussion、Conclusion 和投稿附属占位项。主线基本稳定：clean rendered image 被定位为 upper-bound，OCS 被定位为 low-dimensional / interpretable / multi-geometry photometric constraint，fusion 被定位为 conditional complementarity。No real telescope validation、fixed roll、phase63、nominal materials、未显式建模 atmosphere / detector / PSF / earthshine / background contamination 等限制也被反复说明。

但这不是最终可投稿稿。进入最终比较或定稿前，必须先完成作者核对、文献核验和数值审计。

## 2. 主要优点

1. 全文结构完整，能作为第一版连续英文论文初稿使用。
2. Abstract 和 Introduction 没有宣称真实望远镜验证，明确把 clean ResNet 结果写成 idealized upper-bound。
3. Related Work 采用机制分组，Table 1 的定位是“说明本文组合位置”，而不是虚构 SOTA。
4. Method 能覆盖统一 forward model、STL 几何、材料、GGX BRDF、自遮挡、OCS/image 生成、模型和指标。
5. Results 证据链清楚：forward-model check -> OCS-only -> image-only clean upper-bound -> fusion -> degradation -> ablation/sensitivity。
6. `all_raw` 基本全篇作为 semi-oracle / diagnostic upper bound，`per_part_log` 作为 practical OCS setting。
7. Discussion 和 Conclusion 没有把 fusion 写成 universal best，也没有把 OCS 写成永远优于图像。
8. 文末保留了 Author Confirmation List 和 Revision Priority List，便于后续逐项修订。

## 3. 必须修订或核对的问题

### 3.1 Table 1 文献占位不能进入正式稿

Related Work 和 Table 1 中仍有大量：

- `[CITATION: ...]`
- `[to verify]`
- 具体论文年份、作者、期刊、方法描述待核对

这在当前阶段可以保留，但正式内审前必须逐条核验。尤其需要核对：

- Yang et al. 2024/2025 Photonics 的具体题名、年份、模型类型和是否使用 Cook-Torrance / pBRDF。
- Lu/Yao 2024 Universe 的对象、BRDF 细节和是否包含自遮挡。
- Wang / Burton / Kumar / Liu / Dickinson / Fankhauser 的任务、验证方式和是否适合作为 Table 1 对比项。

如果无法确认，不要在正式稿中保留具体断言。

### 3.2 Method 中目标编码不能写成“can be encoded”

稿件写道：

```text
the target can be encoded using a periodic representation such as sine and cosine components ...
```

正式 Method 不能写成可能性描述，必须写实际实现：

```text
The target was encoded as ...
```

或在未确认前保持：

```text
[需要作者确认：exact target encoding]
```

同样必须确认：

- Euler order / rotation matrix convention
- angular error formula
- yaw periodicity handling
- pitch error handling

这些是审稿人最容易抓住的可复现性问题。

### 3.3 部分数值需要回查原始实验日志

以下数值当前可作为候选，但必须由作者或实验日志确认后进入正式稿：

- `Weighted kNN all_raw`: `21.84`, Hit@5 `47.9%`, Hit@10 缺失。
- Table 2 中 TinyCNN Hit@10 `55.8%`。
- Table 3 中 `phase63 per_part_log 6D`：`1.61 +/- 0.07`, P90 `2.97`, worst `7.4`, Hit@5 `99.2%`, Hit@10 `100%`。
- Table 3 中 ResNet + concat5 `all_raw`：worst `18.7` 是否为最终可公开数字。
- OCS noise 0% 表格值仍缺失，但正文已写 gain `+1.97 deg`。
- occlusion rates `60% to 78.5%` 是否为最终统计。
- sub-percent closure checks 的具体定义和来源。

这些不一定错误，但正式稿前必须回到实验记录核对。

### 3.4 “OCS 低成本 / operationally expensive” 需要降调

稿件中写到 OCS 相对图像更 low-cost、operationally expensive 等方向。这是合理叙事，但当前没有望远镜系统级实验或成本分析。正式稿建议统一写成：

```text
OCS-like integrated photometric measurements may be less demanding than fully resolved imagery, but practical acquisition requirements depend on telescope aperture, target brightness, range, phase angle, calibration accuracy and atmospheric conditions.
```

不要让审稿人读成“本文已经证明 OCS 更低成本且可操作部署”。

### 3.5 `all_raw` 的 semi-oracle 边界要继续保持

全文总体做得不错，但 `all_raw 45D` 数值非常强，审稿人会追问其可观测性。最终稿中每次出现 `all_raw` 时都要确保附近有：

```text
semi-oracle diagnostic upper bound
not an operationally realistic OCS feature
```

不要在 Abstract 或 Conclusion 中用 `all_raw` 作为主要贡献结果。

### 3.6 OCS-noise fusion 解释要避免“图像退化下 fusion 已证明”

GPT 稿件正确说明了 OCS-noise 实验中 image branch remains clean。正式稿中继续保持这个边界：

```text
The OCS-noise experiment supports conditional complementarity under controlled modality degradation, but it is not evidence for ResNet+OCS robustness under degraded images unless such experiments are added.
```

如果作者没有 ResNet-fusion image-degradation 结果，不要在 Results 或 Discussion 中暗示已经证明。

### 3.7 篇幅和重复数字需要压缩

稿件约 9k words，作为第一版整合稿合适，但投稿前应压缩。建议：

- Abstract 保留 3-4 个数字。
- Introduction 最多保留 2 个 teaser 数字。
- Results 放完整表格和数字。
- Discussion 减少重复结果，强调解释。
- Conclusion 不超过 250-300 words。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明核心实验或核心结果 | 未发现明显核心发明；若干表格数值需作者核对 |
| 是否新增未核对引用 | 有占位引用，但保留了 `[to verify]`，未当成最终引用 |
| 是否把 clean image 写成 field performance | 未发现 |
| 是否宣称真实 optical telescope validation | 未发现 |
| 是否夸大 fusion | 基本未发现 |
| 是否把 OCS 写成永远优于图像 | 未发现 |
| 是否把 OCS 写成对所有真实噪声免疫 | 未发现 |
| 是否把 `all_raw` 写成实用特征 | 基本未发现，但需继续强化 semi-oracle 边界 |
| 是否把 `r = 0.003` 写成 ResNet-pair 证据 | 未发现，已限定为 TinyCNN/OCS diagnostic |
| 是否把 Gaussian noise 写成完整 realistic degradation model | 未发现，写成 controlled stress test |
| 是否把 ISAR 并入主线 | 未发现 |

## 5. GPT 侧下一步建议

GPT 侧完整初稿已经完成。下一步不应继续让 GPT 自行扩写新章节，而应进入作者核对和正式修订：

1. 作者先核对 `Author Confirmation List` 中的高优先级项目。
2. 回查实验日志，确认所有表格数值、缺失 Hit@10、OCS-noise 0% 表格值。
3. 核验 Table 1 文献和所有 `[CITATION] / [to verify]`。
4. 根据目标期刊压缩全文，并决定 Limitations 是否独立成节。
5. 等 Claude 侧完整初稿也完成后，再启动 GPT vs Claude 最终对比评分和混合整合。

## 6. 是否进入最终对比

暂不进入最终对比。原因：Claude 侧 Step 7 全文整合初稿尚未返回。

当前状态：

```text
GPT 侧：候选完整初稿已完成，等待作者核对 / 等待 Claude 候选完整初稿。
Claude 侧：Step 7 全文整合指导已生成，等待 Claude 输出。
```

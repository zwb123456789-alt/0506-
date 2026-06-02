# Step 7 Claude 单边初审：全文整合初稿

> 审阅对象：`Claude交互/claude writing/07_Step7_Claude输出_全文整合初稿.md`  
> 审阅日期：2026-06-01  
> 审阅原则：先单边审阅 Claude 完整初稿；因 GPT 侧完整初稿已完成，本次单边审阅后可进入最终完整初稿级别的 GPT vs Claude 对比。

## 1. 总体结论

Claude Step 7 全文整合初稿通过单边初审，可以标记为 **Claude 侧候选完整初稿已完成**。

这版稿件更像“压缩后的投稿骨架”，主线清楚、语言集中、重复少，适合后续作为精简版结构参考。核心红线总体未越界：clean image 被写成 upper-bound，no real telescope validation 明确，fusion 被写成 conditional complementarity，`all_raw` 被写成 semi-oracle，OCS robustness 被限定在不依赖 image inputs / image-pixel degradation 的 benchmark 内。

但 Claude 稿也有明显风险：它把若干尚需作者确认的方法细节和敏感性数值写得比较确定，且部分表格仍是 `[INSERT Table]`，没有像 GPT 稿那样保留完整表格草稿。正式定稿前必须核对这些内容。

## 2. 主要优点

1. 篇幅控制好，正文约 4k words，更接近后续投稿压缩稿。
2. Abstract 清楚抓住主线：unified physical model、clean image upper bound、noise fragility、OCS / fusion conditional complementarity。
3. Related Work 简洁，不做过度展开，适合作为后续精简版基础。
4. Method 的数学表达和分节较清楚，OCS 积分公式、BRDF 公式、模型分支都容易读。
5. Results 顺序符合主规划：forward validation -> OCS-only -> image-only -> fusion -> degradation -> sensitivity。
6. Discussion 的逻辑紧凑，能直接服务 SCI 二区投稿叙事。
7. Author Confirmation List 比较具体，列出了 13 个后续核对项。

## 3. 必须修订或核对的问题

### 3.1 未确认的方法细节被写得过于确定

Claude 稿直接写了：

- `Z-Y-X intrinsic Euler angles`
- `R = Rz(psi) * Ry(theta) * Rx(phi)`
- satellite rotated while Sun and detector remain fixed
- target encoding as `[sin yaw, cos yaw, sin pitch, cos pitch]`
- TinyCNN `~106k params`
- ResNet-18 `~11.2M params`
- MLP architecture `128->128->64`

其中部分已经标注 `[需要作者确认]`，但正文语气仍偏确定。正式稿前必须回查代码 / 实验记录。若未确认，Method 中只能写：

```text
[需要作者确认：Euler convention / target encoding / architecture details]
```

### 3.2 未确认 sensitivity / ablation 数值仍进入正文

Claude 稿在 Results / Limitations 中写了：

- BRDF metallic roughness `30-42%`
- non-metallic `<5%`
- roll sensitivity `~20%`
- random split consistent trends
- occlusion rates `60-78.5%`

这些在此前 Step 5 / Step 6 审阅中已被列为作者确认项。正式稿处理方式：

1. 若实验日志确认，可以保留并给出表格 / 补充材料来源。
2. 若未确认，必须移出主结论，保留为 `[需要作者确认]` 或放入 Future Work / Supplementary。

### 3.3 Abstract 中 “OCS-only result is unaffected” 需要更严谨

Claude Abstract 写：

```text
the OCS-only result (5.91 deg) is unaffected because it does not depend on image inputs
```

建议正式稿改为：

```text
the OCS-only branch is unaffected by image-pixel degradation in this benchmark because it does not use image inputs
```

避免被理解为 OCS 对真实观测噪声免疫。

### 3.4 “fusion compensation gain +2.0 to +6.3” 需要保留精确来源

Claude 把 `+1.97 -> +6.29` 在 Abstract / Conclusion 中四舍五入为 `+2.0 -> +6.3`。投稿稿可以四舍五入，但必须先补全 Table 4 的 0% OCS-noise exact values。若不补全，Abstract 和 Conclusion 中最好只写趋势，不写 `+2.0`。

### 3.5 表格还停留在占位符

Claude 正文中有：

- `[INSERT Table 1]`
- `[INSERT Table 2]`
- `[INSERT Table 3]`
- `[INSERT Table 4]`

因此 Claude 稿不能单独作为完整可审阅稿，需要从 GPT 稿或前序 Claude Step 3/5 中补回表格草稿。

### 3.6 Related Work 引用断言需要核验

Claude 稿把若干文献写成自然句，而不是全表占位。例如：

- Yang et al. investigated goniopolarimetric properties...
- Lu developed BRDF-based photometric models...
- Wang constructed laboratory-tested photometry dataset...
- Dickinson addressed sim-to-real 6DOF...

这些仍带 `[to verify]`，但语气较自然，正式稿前必须逐条核对。不能把未核对文献断言放入投稿稿。

### 3.7 语言风格偏“强摘要化”

Claude 稿优势是精炼，但 Method / Results 某些地方略像扩展摘要，缺少可复现细节和完整表格支撑。最终定稿若以 Claude 为骨架，需补入 GPT 稿的：

- 完整 Table 1 草稿
- Table 2 / 3 / 4 数字表
- 更完整的 figure caption intent
- 更细的 Author Confirmation List 和 Revision Priority List

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明核心实验或核心结果 | 未发现明显核心发明；但若干未确认方法细节和 sensitivity 数值需核对 |
| 是否新增未核对引用 | 有占位引用和 `[to verify]`，未作为最终引用 |
| 是否把 clean image 写成 field performance | 未发现 |
| 是否宣称真实 optical telescope validation | 未发现 |
| 是否夸大 fusion | 基本未发现 |
| 是否把 OCS 写成永远优于图像 | 未发现 |
| 是否把 OCS 写成对所有真实噪声免疫 | Abstract 需稍微收紧为 “image-pixel degradation in this benchmark” |
| 是否把 `all_raw` 写成实用特征 | 未发现，写成 semi-oracle |
| 是否把 `r = 0.003` 写成 ResNet-pair 证据 | 自检称未升级，但正文基本未使用该证据 |
| 是否把 Gaussian noise 写成完整 realistic degradation model | 未发现 |
| 是否把 ISAR 并入主线 | 未发现 |

## 5. Claude 侧下一步建议

Claude 侧完整初稿已经完成。下一步不应继续让 Claude 自行扩写新章节，而应进入最终两稿比较和混合整合：

1. 保留 Claude 稿作为精简主线和语言风格参考。
2. 从 GPT 稿补入完整表格草稿、图表说明和更完整的可复现说明。
3. 作者优先核对方法细节、敏感性数值、文献和 0% OCS-noise 表格值。
4. 启动完整初稿级别 GPT vs Claude 对比评分。

## 6. 是否进入最终对比

可以进入最终对比。

当前状态：

```text
GPT 侧：候选完整初稿已完成并通过单边初审。
Claude 侧：候选完整初稿已完成并通过单边初审。
下一步：进行完整初稿级别 GPT vs Claude 对比评分，并确定最终整合策略。
```

# Codex 单边审阅：Claude Step 07 融合机制诊断与鲁棒融合升级

> 审阅日期：2026-06-04  
> 被审阅文件：`Claude交互/Claude输出/07_Claude输出_融合机制诊断与鲁棒融合升级.md`  
> 结果目录：`论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/`  
> 新增脚本：`论文改进/补充实验/代码/run_fusion_mechanism_upgrade.py`  
> 审阅结论：**有条件通过，可进入 v0.2 整合，但必须降调因果解释并保留尾部风险。**

## 1. 文件与结果核查

已核查以下产物存在：

```text
论文改进/补充实验/代码/run_fusion_mechanism_upgrade.py
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/run.log
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/diagnostics_results.csv
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/diagnostics_results.json
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/upgrade_results.csv
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/upgrade_results.json
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/mechanism_summary.md
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/summary.json
```

运行日志与 Claude 输出一致：

```text
5 seeds: 0,1,2,3,4
epochs=500, patience=100
split: 10° -> 5°, train_pool=703, tr=563, val=140, test=1998
OCS: concat5 per_part_log 30D
image: phase63 exact BRDF, log1p 128x128
total elapsed: 3835s
```

脚本口径基本合规：

- 复用既有 ResNet/fusion 数据加载、target encoding、split 和 angular error 口径。
- 未改 v0.1 主稿。
- 未代填 Data/Code/Author/Funding/COI。
- 新增脚本未覆盖旧脚本。

## 2. 可采纳的核心结果

### 2.1 Naive fusion 的分支诊断成立

诊断结果可采纳：

| 条件 | normal | image masked | OCS masked |
|---|---:|---:|---:|
| clean | 1.57° | 52.84° | 18.14° |
| image noise σ=0.01 | 75.08° | 52.84° | 88.88° |
| image noise σ=0.10 | 72.48° | 52.84° | 89.96° |

可写结论：

```text
Clean 下图像分支是主信息源；图像噪声下，退化图像会主动污染 fusion 输出。
OCS 信息并非完全无效：在噪声档屏蔽 OCS 后误差进一步恶化到约 89°。
但现有 fusion head 没有学会单独利用 OCS：屏蔽图像后仍为约 53°，远高于 OCS-only 5.91°。
```

必须修正 Claude 输出中的一句过强表述：

```text
“image_zero 后接近 OCS-only”不准确。
52.84° 比 75.08° 有明显改善，但与 5.91° 相差很大。
```

正确写法应为：

```text
Masking the degraded image branch reduces the error substantially, but the result remains far worse than a dedicated OCS-only predictor. This indicates that OCS features retain useful information, while the fusion head has not learned an OCS-standalone fallback mapping.
```

### 2.2 U1 图像退化增强是本轮最强结果

U1 可作为主文新增结果，但必须带上尾部风险：

| 条件 | mean±std | Hit@5 | p90 | worst |
|---|---:|---:|---:|---:|
| clean | 1.95±0.21° | 97.8% | 3.53° | 102.11° |
| noise σ=0.01 | 1.95±0.21° | 97.8% | 3.53° | 102.08° |
| noise σ=0.10 | 2.31±0.26° | 96.6% | 3.73° | 164.27° |
| bright×0.50 | 1.98±0.20° | 97.8% | 3.54° | 139.83° |
| bright×1.50 | 2.00±0.22° | 97.4% | 3.62° | 98.97° |

可写结论：

```text
Online image degradation augmentation largely removes the mean-error and p90 collapse of clean-trained fusion under the tested degradations.
```

不能写：

```text
near-perfect robustness
完全鲁棒
OCS fallback 已经被证明
所有图像退化下都可靠
```

原因：

1. U1 的 worst-case 仍有 100° 以上离群点，说明尾部未完全解决。
2. U1 没有 image-only + same augmentation 对照，无法判定性能恢复主要来自 OCS fallback，还是 image branch 本身学会了对这些合成退化不敏感。
3. U1 没有对增强后模型做 image/OCS 分支遮蔽，因此不能证明测试时权重真的转向 OCS。

### 2.3 U2/U3/U4 的论文用途

U2 模态 dropout：

```text
clean 1.96°，但 noise σ=0.01 为 83.72°，noise σ=0.10 为 84.26°。
```

结论：单独模态 dropout 不能防御未见图像噪声。可用于 Discussion 或 Supplementary。

U3 增强 + dropout：

```text
clean 2.90°，noise σ=0.01 2.96°，noise σ=0.10 4.59°。
```

结论：鲁棒但 clean/Hit@5 有代价，且不如 U1。建议放 Supplementary 或主文简述，不作为主推方案。

U4 OCS-anchored：

```text
clean 7.75°，noise σ=0.01 7.82°，noise σ=0.10 9.76°；
gate 在 σ=0.10 降至 0.046。
```

结论：机制方向有价值，但精度不足。可作为 Discussion 中的 architecture-level exploration，不能作为主方法成功方案。

## 3. 主要问题与必须降调处

### 问题 1：U1 不足以证明 OCS 是恢复鲁棒性的主因

Claude 将 U1 写成 “OCS can serve as fallback” 方向的成功证据，过强。

本轮 U1 是 fusion + 图像退化增强；它证明的是：

```text
当训练分布包含测试退化类型时，fusion 的图像噪声崩溃可以被显著抑制。
```

它尚未证明：

```text
恢复来自 OCS fallback。
```

若要强写 OCS fallback，至少需要一个 12b 对照：

```text
ResNet image-only + same image degradation augmentation
U1 augmented fusion 的 image-masked / OCS-masked 评估
可选：U1 在 OCS noise 或 both-degraded 下的表现
```

### 问题 2：尾部风险被 Claude 输出弱化

U1 mean/p90/Hit@5 很强，但 worst-case 很大：

```text
clean worst 102°
noise σ=0.10 worst 164°
brightness ×0.50 worst 140°
```

主文若只展示 mean 和 Hit@5，容易被审稿人追问尾部。建议至少在 Supplementary 放 p90/worst，正文写：

```text
The mean and p90 errors are strongly stabilized, although rare large outliers remain.
```

### 问题 3：机制总结中 “接近 OCS-only” 表述不准确

`mechanism_summary.md` 将 image masking 后 52.84°描述为“接近 OCS-only”。这不成立。后续 v0.2 不得采用这句话。

准确解释：

```text
image masking improves over noisy normal fusion but remains far from OCS-only, indicating that useful OCS information exists but is not organized as an independent fallback path inside the joint fusion head.
```

### 问题 4：Claude 交互端总览未更新

`Claude交互/00_Claude后整合总览.md` 仍停留在第 6 阶段。按交互端分工，应由 Claude 补充第 7 阶段完成状态。Codex 不代替更新，但在本审阅中记录提醒。

## 4. 审阅结论

本阶段 **有条件通过**。

可直接进入 v0.2 的事实：

```text
1. 实验12已完成，结果目录为 run_20260604_092041。
2. Naive fusion 在 clean 下图像主导，图像噪声下退化图像会污染输出。
3. OCS 分支在噪声档仍有缓冲作用，但 naive fusion head 未学会 OCS-only fallback。
4. 在线图像退化增强将 fusion 在测试退化下的 mean error 从 73°级拉回到约 2°，p90 约 3.5-3.7°，Hit@5 约 96.6-97.8%。
5. 单独模态 dropout 失败；增强+dropout 有效但劣于增强 alone；OCS-anchored gate 有正确趋势但精度不足。
```

进入 v0.2 时必须遵守：

```text
不写 U1 已证明 OCS fallback。
不写 near-perfect / fully robust。
不隐藏 U1 worst-case 离群点。
不把 U4 写成成功主方法。
```

建议下一步：

```text
若作者接受审慎表述：可直接进入 v0.2 主稿修订。
若作者希望强写“OCS 能托住”：先补 12b 最小对照（image-only augmentation + U1 branch masking）。
```

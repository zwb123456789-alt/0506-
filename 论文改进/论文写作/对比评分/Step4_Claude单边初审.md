# Step 4 Claude 单边初审：Method

> 审阅对象：`Claude交互/claude writing/04_Step4_Claude输出_Method.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 Claude 这一侧输出，不与 GPT 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

Claude Step 4 Method 输出通过单边初审，可以进入 Claude Step 5：Results。

本次 Method 基本达到阶段目标：它把项目写成 unified BRDF-driven forward model 和 controlled inversion benchmark，而不是代码说明或工程日志。章节结构从几何、姿态、观测几何、BRDF、自遮挡、OCS 积分、图像生成到反演模型与评估指标，覆盖完整，并且没有提前写 Results 性能数值。

## 2. 主要优点

1. 统一物理链条清楚：OCS 与 photometric image 共享 STL、姿态、材料、GGX/Cook-Torrance BRDF、观测几何和 visibility assumptions。
2. 方法章节结构完整：3.1-3.9 覆盖 forward model 和 inversion benchmark 的主要模块。
3. 关键边界控制较好：明确 no real optical telescope validation、clean rendered images 是 idealized upper-bound、fixed roll 不是 full 3-DOF pose recovery。
4. `all_raw` / `per_part_log` 区分正确：`all_raw 45D` 被标为 semi-oracle upper bound，`per_part_log` 被标为 practical OCS setting。
5. Fusion 口径安全：late fusion 和 feature fusion 都被写成 controlled probes / benchmarked strategies，没有宣称 universal best。
6. 可复现性清单有价值：列出了 STL、component segmentation、BRDF、observation geometries、split、seeds、metrics 等正式稿必须报告的参数。

## 3. 需要修改或后续确认的问题

### 3.1 角度误差公式必须最终固定

Claude 在 §3.9 中写了 geodesic angular distance，同时又标注 `[需要作者确认：angular error formula]`。正式稿不能同时保留两种不确定口径。

建议最终只写已被代码确认的公式。如果暂时无法确认，Method 中应写：

```text
Angular error is reported in degrees and accounts for yaw periodicity; the exact formula will be specified after code verification.
```

不要提前写成球面测地距离，除非代码确实如此。

### 3.2 `total_log` 特征定义可能需要更精确

Claude 写到 `total_log (15D)` 包含 total OCS values with/without occlusion and occlusion ratio, log-transformed。这里有潜在风险：遮挡率这类 `[0,1]` 特征不一定做 log，项目笔记中也出现过“遮挡率不要 log，直接 z-score”的实现提醒。

正式稿建议把特征定义写得更保守：

```text
Feature transformations follow the training pipeline; OCS magnitudes are log-transformed where applicable, and ratio-type diagnostic variables are normalized separately.
```

### 3.3 Blender / ray-cast cross-validation 不要写成 field validation

Claude 使用了 cross-validated against independent ray-cast queries，这可以保留。但 Results 和 Discussion 中必须继续限定为 synthetic / rendering-based / manual sampled checks，不能升级成真实望远镜验证。

### 3.4 Random split、roll sensitivity、BRDF sensitivity 是否“已报告”需确认

Method 中写到 random split additionally reported、roll sensitivity analysis provided separately、material sensitivity evaluated through parameter perturbation experiments。这些在项目规划中是审稿防御项，但正式正文是否已有最终数值仍需作者确认。

如果最终值不完整，应改成：

```text
We use these analyses as supplementary checks where finalized values are available.
```

不要在 Method 中暗示所有 sensitivity results 已经完整可报。

### 3.5 模型结构与训练细节应放主文还是补充材料

Claude 写出 TinyCNN 约 106k、ResNet-18 约 11.2M、MLP `128->128->64`、5 seeds、log1p 等信息，大部分有项目依据。但正式稿中需要决定：

- 主文保留模型族、输入、输出和核心设置。
- 具体训练超参数、层数、batch size、learning rate、epoch、early stopping 可放 Supplementary。
- `ResNet-18` 建议主文明确写出，因为它是 clean-image upper-bound 的关键强 baseline。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否写成代码脚本说明 | 未发现 |
| 是否发明 Results 性能数值 | 未发现 |
| 是否宣称真实光学望远镜验证 | 未发现 |
| 是否把 clean image 写成真实场景性能 | 未发现 |
| 是否宣称 full 3-DOF pose recovery | 未发现，已说明 fixed roll |
| 是否宣称 fusion 永远最优 | 未发现 |
| 是否宣称 OCS 永远强于图像 | 未发现 |
| 是否区分 `all_raw` 和 `per_part_log` | 已区分 |
| 是否把 ISAR 并入 Method 主线 | 未发现 |

## 5. 给 Claude 的后续修订意见

进入 Step 5 Results 前，Claude 应记住：

1. Results 不要重复 Method 细节，而要按 evidence ladder 写结果含义。
2. 结果顺序建议为：forward-model validation -> OCS-only -> image-only clean upper-bound -> fusion under clean images -> degradation robustness -> sensitivity/ablation。
3. ResNet-18 clean image `1.69 ± 0.07°` 是 idealized upper-bound，不是 field performance。
4. OCS MLP `per_part_log 5.91 ± 0.22°` 是 practical OCS-only；`all_raw 3.98 ± 0.60°` 只能写成 semi-oracle upper bound。
5. Fusion 只能写成 conditional complementarity：clean 情况下 mean 改善有限，但 Hit@5 和 worst-case tail error 改善明确。
6. `r = 0.003` 只能写为 earlier TinyCNN/OCS diagnostic，不能默认代表 ResNet-pair evidence。
7. 图像退化实验只能写成 controlled degradation / stress test，不是完整真实地基观测模型。
8. 4.6 sensitivity / ablation 中没有最终数值的项目必须标 `[需要作者确认]`，不能假装已完成。

## 6. 是否进入下一阶段

结论：可以进入 Claude Step 5。

下一阶段指导文件：

```text
Claude交互/06_Step5_Claude_Results指导.md
```

Claude 输出建议保存为：

```text
Claude交互/claude writing/05_Step5_Claude输出_Results.md
```

# Step 4 GPT 单边初审：Method

> 审阅对象：`GPT交互/GPT writing/04_Step4_GPT输出_Method.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 GPT 这一侧输出，不与 Claude 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

GPT Step 4 Method 输出通过单边初审，可以进入 GPT Step 5：Results。

本次 Method 章节基本达到目标：它把论文写成 physically consistent simulation and controlled inversion benchmark，而不是代码说明或工程日志。结构从 unified forward model 到 OCS/image 生成，再到 inversion models 和 metrics，符合当前论文主线。

## 2. 主要优点

1. Method 主线清楚：同一 STL、材料、BRDF、姿态、观测几何和 visibility assumptions 生成 OCS 与 photometric images。
2. 模块结构完整：覆盖 geometry/attitude、nonuniform materials、GGX BRDF、self-occlusion、OCS integration、image generation、inversion models、split/metrics。
3. 边界控制较好：明确 no real telescope images、clean rendered images 是 idealized upper-bound、fixed roll 不是完整 3-DOF pose recovery。
4. OCS 特征边界正确：`all_raw` 被写成 semi-oracle upper bound，`per_part_log` 被写成更实用的 OCS setting。
5. Fusion 口径安全：late fusion 和 feature fusion 都被写成 benchmark strategies / probes of complementarity，没有宣称 universal best。
6. 可复现性意识较强：列出了 STL source、material parameters、observation geometries、split、model families、metrics、random seeds 等需要报告的内容。

## 3. 需要修改或后续确认的问题

### 3.1 `[需要作者确认]` 项不能带入正式稿

GPT 正确标出了不确定项，但正式稿前必须逐一确认：

- Euler order / rotation matrix convention  
  项目总览中已有 `R = Rz(yaw) @ Ry(pitch) @ Rx(roll)` 与 Z-Y-X 内旋描述，建议最终核对代码后固定写法。
- Angular error formula  
  Results 表和 Method 必须使用同一公式，尤其要处理 yaw periodicity。
- Target encoding  
  如果确认为 yaw/pitch 的 sin-cos 四维输出，Method 可直接写清楚。
- OCS units and normalization  
  需要说明 OCS 是 `m^2` 原始物理量、归一化特征，还是训练前经过 log/standardization。
- ResNet 是否明确为 ResNet-18  
  目前补充实验确认是 ResNet-18，正式稿建议直接写 `ResNet-18`。
- Training protocol 放主文还是补充材料  
  epoch、batch size、learning rate、seeds、early stopping 等至少要在 supplement 或 reproducibility checklist 中出现。

### 3.2 Self-occlusion 验证表述仍需保持“受控验证”

当前写法是安全的，但后续不能把 synthetic geometry tests / Blender manual review 写成 field validation。建议正式稿维持：

```text
validated using synthetic geometry tests and sampled rendering-based/manual checks
```

不要写：

```text
validated by real telescope observations
```

### 3.3 Method 中不应提前承担 Results 解释

GPT 输出基本没有堆结果数值，这是正确的。正式稿中 Method 只需说明 model families、features、splits 和 metrics；ResNet clean `1.69°`、noise `85.85°`、fusion `1.47°` 等必须放在 Results。

### 3.4 `phase63` 的表述需要延续到 Results 与 Limitations

Method 已说明 image branch mainly uses one rendered phase condition。Results 中必须继续说明：

- 图像结果是 phase63 clean photometric image branch。
- OCS 端使用 multi-geometry signatures。
- 这种不对称需要通过信息密度解释、fairness ablation 或 limitations 控制。

### 3.5 `all_raw` 的使用必须在 Results 中避免误导

Method 已把 `all_raw` 写成 semi-oracle。Results 中如果报告 `3.98 ± 0.60°`，必须写成：

> semi-oracle OCS upper-bound representation

不能把它当作主要实用 OCS-only 性能。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明新实验或新结果 | 未发现 |
| 是否写成代码脚本说明 | 未发现 |
| 是否宣称真实光学望远镜验证 | 未发现 |
| 是否把 clean image 写成真实场景性能 | 未发现 |
| 是否宣称 fusion 永远最优 | 未发现 |
| 是否宣称 OCS 永远强于图像 | 未发现 |
| 是否把 ISAR 并入 Method 主线 | 未发现 |
| 是否区分 `all_raw` / `per_part_log` | 已区分 |
| 是否说明 fixed roll | 已说明 |

## 5. 给 GPT 的后续修订意见

进入 Step 5 Results 前，GPT 应记住：

1. Results 要围绕 evidence ladder 写，不要重复 Method 细节。
2. Results 主线是：forward-model validation -> OCS-only -> image-only clean upper-bound -> fusion under clean images -> degradation robustness -> sensitivity/ablation。
3. ResNet-18 clean image `1.69 ± 0.07°` 是 idealized upper-bound，不是 field performance。
4. OCS MLP `5.91°` 是 practical OCS-only；`all_raw 3.98 ± 0.60°` 只能写成 semi-oracle upper bound。
5. Fusion 结果要强调 conditional benefit：mean 改善有限但 tail / Hit@5 改善明确；不要写成 universal best。
6. `r = 0.003` 只能写为 earlier TinyCNN/OCS diagnostic，不能默认代表 ResNet pair。
7. 退化实验只能写成 controlled degradation / stress test，不是完整真实地基观测模型。

## 6. 是否进入下一阶段

结论：可以进入 GPT Step 5。

下一阶段指导文件：

```text
GPT交互/05_Step5_GPT_Results交互提示词.md
```

GPT 输出建议保存为：

```text
GPT交互/GPT writing/05_Step5_GPT输出_Results.md
```

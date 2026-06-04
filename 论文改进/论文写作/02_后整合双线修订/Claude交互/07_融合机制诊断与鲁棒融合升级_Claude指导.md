# Claude 指导：后整合 Step 07 融合机制诊断与鲁棒融合升级

> 生成日期：2026-06-03  
> 发送对象：Claude  
> 项目根目录：`D:\我的文件\研究生学术\光学项目\0506新`  
> 本轮任务：执行实验12，诊断 ResNet-fusion 的图像主导性，并尝试让 OCS 在图像退化时成为 fallback。  
> 重要限制：本轮只做实验设计、代码实现、运行、结果分析和论文写作建议；不要直接改写主稿 v0.1。

---

## 0. 你的角色

你不是从零写论文，也不是重新设计整个项目。你要在现有 OCS-光度图像联合姿态反演项目上，完成一个新的主线实验：

```text
实验12：融合主导性诊断与鲁棒融合升级
```

这个实验要回答：

```text
1. 当前 ResNet feature fusion 是否学习到了图像主导？
2. 图像退化时，OCS 信息是没有用，还是有用但 fusion head 不会切换？
3. 能不能通过图像退化增强、模态 dropout、门控/不确定性加权、OCS-anchored residual fusion，让 OCS 在图像失效时真正托住模型？
4. 如果做不到，怎样把失败结果写成机制性发现，而不是掩盖掉？
```

请保持审稿人视角：任何结论必须能被日志、表格和已确认实验支持。

---

## 1. 执行前必须读取的文件

请先读取以下文件，理解项目全貌和当前主线，不要跳过：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\20260529_论文写作完整规划.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\20260529_补充实验进度.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\00_总控流程.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\00_后整合双线总览.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\07_融合机制诊断与鲁棒融合升级\00_本阶段任务说明.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\作者确认回答\Q1-Q15_作者回答汇总.md
D:\我的文件\研究生学术\光学项目\0506新\论文项目总览 copy.md
D:\我的文件\研究生学术\光学项目\0506新\CLAUDE.md
```

重点读以下脚本，复用其数据加载、模型、split、指标和输出风格：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_resnet_fusion.py
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_fusion_robustness.py
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_resnet_robustness.py
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_noise_robustness.py
D:\我的文件\研究生学术\光学项目\0506新\ocs_project\03_inversion\train_fusion.py
D:\我的文件\研究生学术\光学项目\0506新\ocs_project\03_inversion\inv_common.py
```

重点读以下已完成结果：

```text
论文改进/补充实验/结果/resnet_fusion/run_20260601_113332/summary.md
论文改进/补充实验/结果/resnet_fusion/run_20260601_113332/summary.json
论文改进/补充实验/结果/resnet_robustness/run_20260601_143957/robustness_report.md
论文改进/补充实验/结果/resnet_robustness/run_20260601_143957/robustness_results.json
论文改进/补充实验/结果/resnet_fusion_robustness/run_20260603_204854/fusion_robustness_report.md
论文改进/补充实验/结果/resnet_fusion_robustness/run_20260603_204854/fusion_robustness_results.json
论文改进/补充实验/结果/noise_robustness/run_20260601_094130/noise_summary.json
```

---

## 2. 已确认的关键事实

以下数值已经由作者确认或由补充实验台账固定，严禁改写口径：

```text
姿态编码：神经网络统一输出 [sin(yaw), cos(yaw), sin(pitch), cos(pitch)]
主误差：yaw/pitch 映射到单位球面方向后的 great-circle angular error
Hit@5°：单预测角距离 <= 5° 的测试样本比例
split：主线采用 10° train -> 5° test 的严格泛化 split
OCS 主用特征：concat5 per_part_log 30D
图像输入：log1p 128x128，渲染源来自 phase63 exact BRDF
```

核心结果：

```text
OCS-only per_part_log: 5.91°
ResNet image-only clean: 1.69 ± 0.07°, Hit@5 = 97.6%
ResNet-fusion concat5 per_part_log clean: 1.47 ± 0.07°, Hit@5 = 99.7%
ResNet image-only noise σ=0.01: 85.85 ± 3.00°, Hit@5 = 2.2%
ResNet-fusion noise σ=0.01: 73.36 ± 5.07°, Hit@5 = 2.8%
ResNet-fusion noise σ=0.10: 73.57 ± 4.33°, Hit@5 = 3.3%
brightness ×0.50 下 ResNet-fusion: 1.86 ± 0.17°, Hit@5 = 97.7%
brightness ×1.50 下 ResNet-fusion: 1.49 ± 0.08°, Hit@5 = 99.7%
```

当前论文判断：

```text
Naive feature fusion 在 clean 下有边际增益，但图像噪声下没有回退到 OCS-only。
这不是要掩盖的坏结果，而是新的主线变点：fusion 的鲁棒性取决于架构和训练。
```

---

## 3. 你需要创建或更新的文件

建议新建一个独立脚本：

```text
论文改进/补充实验/代码/run_fusion_mechanism_upgrade.py
```

建议结果目录：

```text
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_<timestamp>/
```

结果目录至少包含：

```text
run.log
diagnostics_results.csv
diagnostics_results.json
upgrade_results.csv
upgrade_results.json
mechanism_summary.md
```

完成后，写一份 Claude 输出文件：

```text
论文改进/论文写作/02_后整合双线修订/Claude交互/Claude输出/07_Claude输出_融合机制诊断与鲁棒融合升级.md
```

这份输出必须包含：

```text
1. 读取了哪些文件。
2. 新增或修改了哪些脚本。
3. 运行命令、环境、耗时。
4. 诊断实验结果表。
5. 升级实验结果表。
6. 成功/部分成功/失败判定。
7. 建议写入论文 Results / Discussion / Limitations 的表述。
8. 下一步仍需作者或 Codex 决定的事项。
```

---

## 4. 实现原则

请尽量复用现有代码：

```text
run_resnet_fusion.py:
  ResNet18Backbone
  ResNetFusionModel
  load_images
  load_ocs_features
  align_to_images
  prep_ocs
  compute_metrics
  train_epoch / evaluate

run_fusion_robustness.py:
  train-clean / test-degraded 框架
  DEGRADATIONS 设置
  与实验9 image-only 参照对齐

run_resnet_robustness.py:
  degrade_gaussian_noise
  degrade_brightness
  degrade_blur
  degrade_downsample

run_noise_robustness.py:
  add_ocs_noise
  OCS-noise 0/1/5/10/20% 设计
```

不要改变以下口径：

```text
不要换 split。
不要换 angular error。
不要换 Hit@5 定义。
不要把 all_raw 当 operational feature。
不要为了得到好结果而删掉失败档位。
```

---

## 5. 诊断实验 D：当前 fusion 是否图像主导

### D1. 分支遮蔽 / 均值替换

基于 `run_resnet_fusion.py` 的 `ResNetFusionModel`。它的实际结构是：

```python
self.backbone
self.img_proj
self.ocs_branch
self.fusion_head

f_img = self.img_proj(self.backbone(img))   # 128D
f_ocs = self.ocs_branch(ocs)                # 64D
pred = self.fusion_head(cat([f_img, f_ocs]))
```

请实现一个 evaluation helper，例如：

```text
mode = normal
mode = image_zero
mode = image_train_mean
mode = ocs_zero
mode = ocs_train_mean
mode = both_train_mean
```

其中 train mean 指在训练集上提取该 seed 模型的 `f_img` 或 `f_ocs` 后求均值。不要用 test 均值。

至少在以下条件评估：

```text
clean
image noise σ=0.01
image noise σ=0.10
brightness ×0.50
brightness ×1.50
```

判据：

```text
若 ocs_zero / ocs_train_mean 与 normal 接近，而 image_zero / image_train_mean 大幅退化，则图像主导。
若 image noise 下 image_zero 或 image_train_mean 反而接近 OCS-only 5.91°，则说明 OCS 信息存在，但正常 fusion head 被退化图像误导。
```

### D2. 退化图像遮蔽

在 noise σ=0.01 和 σ=0.10 上重点比较：

```text
normal degraded fusion
image_zero degraded fusion
image_train_mean degraded fusion
OCS-only reference 5.91°
image-only reference 85.85° / 87.92°
```

这一步是本轮最关键的机制诊断。请在 `mechanism_summary.md` 里用一段话明确回答：

```text
OCS 是没有信息，还是信息存在但 fusion 不会切换？
```

### D3. 梯度或权重贡献

二选一，能做两个更好：

```text
1. 对 test batch 计算输出 MSE 对 f_img 和 f_ocs 的梯度范数，报告 image/OCS gradient norm ratio。
2. 取 fusion_head 第一层 Linear 的权重，按输入维度拆成 image 128D 和 OCS 64D，报告 Frobenius norm 或 mean abs norm。
```

注意：权重范数不是因果证据，只是辅助机制证据。论文中要写成 supporting diagnostic，不要过度解释。

### D4. 双向扰动敏感性

整理实验6和实验11，并在本轮补充必要表格：

```text
OCS 退化、图像 clean -> fusion 被图像托住。
图像退化、OCS clean -> naive fusion 被图像拖垮。
```

如果你实现了 both-degraded，也单独列出，不要和单模态退化混在同一结论里。

---

## 6. 升级实验 U：让 OCS 能够 fallback

优先顺序如下。如果时间有限，至少完成 U1、U2、U3；U4/U5 可以完成一个重点方案，或给出明确的未完成原因。

### U1. 图像退化增强

训练时对图像随机施加：

```text
none
Gaussian noise σ=0.01
Gaussian noise σ=0.10
brightness ×0.50
brightness ×1.50
可选 blur/downsample
```

测试矩阵：

```text
clean
noise σ=0.01
noise σ=0.10
bright ×0.50
bright ×1.50
```

目标：

```text
验证 train-clean/test-degraded 崩溃是否主要来自训练分布没见过图像噪声。
```

### U2. 模态 dropout

训练时随机屏蔽分支特征：

```text
p_drop_image = 0.2 或 0.3
p_drop_ocs = 0.1 或 0.2
```

屏蔽位置建议在特征层：

```text
f_img = img_proj(backbone(img))
f_ocs = ocs_branch(ocs)
训练时随机把 f_img 或 f_ocs 置零，也可替换为 train mean。
```

目标：

```text
强迫 fusion_head 学会单靠 OCS 或单靠图像也能输出合理姿态。
```

### U3. 图像退化增强 + 模态 dropout

这是最有希望的低成本组合。请把它作为主要升级 baseline。

判据：

```text
clean 不能明显崩坏，建议 mean <= 2.5°。
noise σ=0.01 / σ=0.10 应显著低于 naive fusion 73°。
若能低于 15°，足以写成强改进。
若接近 5.91°，可写成 OCS fallback 基本实现。
```

### U4. OCS-anchored residual fusion

如果实现，建议结构为：

```text
OCS branch 输出 y_ocs_base (4D sin/cos)
image branch 输出 delta_img (4D)
gate branch 输出 g in [0,1]，可以依赖 image feature + OCS feature
y_fused = normalize_pairs(y_ocs_base + g * delta_img)
```

可选增加辅助损失：

```text
loss = fused_loss + λ * ocs_base_loss
```

目标：

```text
OCS 是基准，图像只做残差修正。图像失效时 gate 应变小，模型回退到 OCS。
```

注意：4D sin/cos 输出每个角度的 pair 需要归一化；不要直接对 yaw/pitch 角度做线性加法。

### U5. adaptive gating / uncertainty late fusion

如果实现，建议先做 prediction-level late fusion，因为可解释性强：

```text
单独 OCS predictor -> y_ocs
单独 image predictor -> y_img
gate/confidence -> β
y_fused = normalize_pairs(β * y_ocs + (1 - β) * y_img)
```

如果实现不确定性：

```text
每个分支输出 mean + log variance
按 inverse variance 融合
```

目标：

```text
clean 时偏 image，image noise 时偏 OCS。
```

---

## 7. 结果判读

请按以下三类给出结论，不要只报表：

### 成功

满足：

```text
clean 约 1.5-2.5°
noise σ=0.01/0.10 显著低于 73°，理想接近 5.91°，至少低于 15°
分支贡献或 gate 显示图像退化时转向 OCS
```

写作结论：

```text
OCS can serve as a robust fallback constraint, but only when the fusion architecture or training explicitly supports modality failure.
```

### 部分成功

例如：

```text
clean 从 1.47° 降到 2-3°，但 image noise 从 73° 降到 10-20°。
```

写作结论：

```text
There is a trade-off between clean-image upper-bound accuracy and operational degradation robustness.
```

### 失败

例如：

```text
增强/dropout 后仍在 image noise 下几十度崩溃。
```

写作结论：

```text
Simple robust-training variants are insufficient to guarantee fallback under dominant-modality failure; future work requires explicit uncertainty estimation, image-quality assessment, or stronger OCS-anchored constraints.
```

失败也要完整报告。不要删掉失败方案。

---

## 8. 建议运行命令

Windows / Git Bash 环境中 Python 不在 PATH 时，使用：

```bash
/c/Windows/System32/cmd.exe //c "cd /d D:\我的文件\研究生学术\光学项目\0506新 && python 论文改进\补充实验\代码\run_fusion_mechanism_upgrade.py"
```

如果在 PowerShell 中运行：

```powershell
cd "D:\我的文件\研究生学术\光学项目\0506新"
python "论文改进\补充实验\代码\run_fusion_mechanism_upgrade.py"
```

建议脚本参数：

```text
--epochs 与 run_fusion_robustness.py 对齐
--batch-size 与 run_fusion_robustness.py 对齐
--dropout 0.10
--seeds 0 1 2 3 4
--run-diagnostics
--run-augment
--run-modality-dropout
--run-combined
```

如算力不足，优先顺序：

```text
1. D1-D3 诊断线
2. U3 退化增强 + 模态 dropout
3. U1/U2 单独消融
4. U4 或 U5 任选一个重点方案
```

---

## 9. 输出模板

请最终输出 `07_Claude输出_融合机制诊断与鲁棒融合升级.md`，结构如下：

```markdown
# Claude 输出：融合机制诊断与鲁棒融合升级

## 1. 已读取文件

## 2. 新增/修改脚本

## 3. 运行设置
- 数据路径
- split
- 模型
- seeds
- 退化设置
- 运行命令

## 4. 诊断结果
### D1 分支遮蔽
### D2 退化图像遮蔽
### D3 梯度/权重贡献
### D4 双向扰动

## 5. 升级结果
### U1 图像退化增强
### U2 模态 dropout
### U3 组合方案
### U4/U5 若完成

## 6. 成功/失败判定

## 7. 对论文主线的影响
- Results 应新增什么
- Discussion 应怎么写
- Limitations 应怎么降调
- 哪些旧表述必须删除

## 8. 建议写入论文的英文段落草稿

## 9. 未完成项与风险
```

---

## 10. 写作红线

```text
不改 v0.1 主稿。
不编造实验结果。
不改变指标口径。
不把 clean synthetic image 写成真实场景性能。
不写 fusion always robust。
不写 OCS automatically saves fusion。
不隐藏失败方案。
不代填 Data/Code/Author/Funding/COI。
```

本轮真正要交付的不是“漂亮结果”，而是机制清楚、证据诚实、能经得住审稿追问的融合结论。

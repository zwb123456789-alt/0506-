# Claude 指导：实验 12b 融合 fallback 因果隔离与鲁棒性补强

> 任务类型：补充实验执行与机制解释  
> 当前日期：2026-06-04  
> 输出文件建议：`论文改进/论文写作/02_后整合双线修订/Claude交互/Claude输出/07b_Claude输出_融合fallback因果隔离.md`  
> 推荐新增脚本：`论文改进/补充实验/代码/run_fusion_fallback_isolation_12b.py`  
> 推荐结果目录：`论文改进/补充实验/结果/fusion_fallback_isolation_12b/run_YYYYMMDD_HHMMSS/`

## 0. 先读文件，不要从头重做

你要在现有实验 12 的代码和结果基础上补做实验 12b。请先读取以下文件，恢复项目全貌：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\00_总控流程.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\00_后整合双线总览.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\20260529_论文写作完整规划.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\20260529_补充实验进度.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\07b_融合fallback因果隔离与鲁棒性补强\00_本阶段任务说明.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\Claude交互\Claude输出\07_Claude输出_融合机制诊断与鲁棒融合升级.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\Codex审阅\07_Claude融合机制诊断与鲁棒融合升级单边审阅.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\阶段整合输出\07_融合机制诊断与鲁棒融合升级_整合清单.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\作者确认回答\Q1-Q15_作者回答汇总.md
```

还必须读取实验 12 代码和结果：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_fusion_mechanism_upgrade.py
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\fusion_mechanism_upgrade\run_20260604_092041\mechanism_summary.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\fusion_mechanism_upgrade\run_20260604_092041\diagnostics_results.csv
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\fusion_mechanism_upgrade\run_20260604_092041\upgrade_results.csv
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\fusion_mechanism_upgrade\run_20260604_092041\summary.json
```

如果你的环境不能直接读取本地文件，请先要求作者粘贴上述文件关键内容，不要凭空补写结果。

## 1. 为什么要补 12b

实验 12 已经完成，但它只支持以下审慎结论：

```text
Naive clean-trained feature fusion is image-dominant and fails under image Gaussian noise.
Degraded images contaminate the fused representation.
OCS still carries useful information, because masking OCS worsens noisy fusion.
However, the naive fusion head has not learned an OCS-standalone fallback.
U1 image degradation augmentation strongly stabilizes fusion mean/p90/Hit@5 under tested degradations.
U1 does not yet prove that OCS fallback is the cause.
```

关键数值：

```text
naive clean normal: 1.57 deg
naive clean image-masked: 52.84 deg
naive clean OCS-masked: 18.14 deg
naive image noise sigma=0.01 normal: 75.08 deg
naive image noise sigma=0.01 image-masked: 52.84 deg
naive image noise sigma=0.01 OCS-masked: 88.88 deg
U1 clean: 1.95±0.21 deg, Hit@5=97.8%, p90=3.53 deg, worst=102.11 deg
U1 noise sigma=0.10: 2.31±0.26 deg, Hit@5=96.6%, p90=3.73 deg, worst=164.27 deg
OCS-only per_part_log reference: 5.91 deg
ResNet image-only clean: 1.69±0.07 deg, Hit@5=97.6%
ResNet image-only noise sigma=0.01: 85.85±3.00 deg, Hit@5=2.2%
```

本任务要隔离：

```text
U1 的成功到底是 image-only augmentation 就能解释，还是 fusion 真的学会了在图像退化时使用 OCS？
```

请注意：不要预设结果。支持或不支持 OCS fallback 都可以写进论文，但必须基于真实实验。

## 2. 固定实验约束

不得改变以下设定：

```text
split: 10 deg -> 5 deg coarse-to-fine
target encoding: [sin(yaw), cos(yaw), sin(pitch), cos(pitch)]
main metric: great-circle angular error
Hit@5/Hit@10: 基于 great-circle angular error
OCS: concat5 per_part_log 30D
image: phase63 exact BRDF, log1p, 128x128
seeds: 与实验 12 一致，优先 5 seeds
```

不得覆盖：

```text
论文改进/论文写作/01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/
```

推荐复用实验 12 脚本中的组件：

```text
prepare_data
apply_image_degradation
RobustFusionModel
make_aug_fn
AUG_DEGS
train_model
eval_on_images
compute_feature_means
summarize_seeds
```

建议新建独立脚本：

```text
论文改进/补充实验/代码/run_fusion_fallback_isolation_12b.py
```

可以从 `run_fusion_mechanism_upgrade.py` 复制必要函数后扩展，也可以在原脚本中新增 `--run-12b`，但不要破坏实验 12 已有入口。

## 3. 必须完成的五组实验

### 12b-1：ResNet image-only + same augmentation

目的：判断 U1 的强鲁棒性是否仅由图像增强导致。

训练：

```text
模型：ResNet image-only
训练增强：与 U1 完全相同的 AUG_DEGS
clean
noise sigma=0.01
noise sigma=0.10
brightness x0.50
brightness x1.50
early stopping：尽量沿用实验 12 的 clean validation 逻辑
seeds：与实验 12 一致
```

评估：

```text
clean
noise sigma=0.01
noise sigma=0.10
brightness x0.50
brightness x1.50
```

输出：

```text
image_only_aug_results.csv
image_only_aug_results.json
```

必须与 U1 augmented fusion 同表对比：

```text
ResNet image-only clean
ResNet image-only + same augmentation
U1 augmented fusion
naive fusion
OCS-only 5.91 deg
```

判读规则：

- image-only augmented 接近 U1：U1 主要由图像增强解释。
- U1 持续优于 image-only augmented，尤其在图像退化或未见退化下更稳：OCS 有补充贡献。

### 12b-2：U1 augmented fusion 分支遮蔽

目的：判断 U1 在图像退化时是否真正使用 OCS。

训练或复用：

```text
U1_augment = RobustFusionModel, augment=True, p_drop_image=0, p_drop_ocs=0
```

评估退化：

```text
clean
noise sigma=0.01
noise sigma=0.10
brightness x0.50
brightness x1.50
```

每个退化下评估：

```text
normal
image_zero
image_train_mean
ocs_zero
ocs_train_mean
both_train_mean
```

输出：

```text
u1_branch_mask_results.csv
u1_branch_mask_results.json
```

判读规则：

- 图像退化下遮蔽 OCS 明显变差：OCS 分支活跃。
- 图像退化下遮蔽图像后接近 5.91 deg：U1 学到强 OCS fallback。
- 遮蔽 OCS 几乎不影响：U1 仍主要依赖图像。

### 12b-3：U1 的 OCS 噪声与双退化

目的：通过扰动 OCS 判断 U1 是否依赖 OCS。

评估矩阵：

```text
image clean + OCS noise 1%, 5%, 10%, 20%
image noise sigma=0.01 + OCS noise 1%, 5%, 10%, 20%
image noise sigma=0.10 + OCS noise 1%, 5%, 10%, 20%
brightness x0.50 + OCS noise 5%, 10%
brightness x1.50 + OCS noise 5%, 10%
```

OCS 噪声技术要求：

1. 优先对标准化前的 OCS 特征加相对噪声，再使用训练集统计量标准化。
2. 如果只能对 `ocs_zs` 加噪，必须在结果中标注为 standardized-feature perturbation，不能与实验 6 的 OCS 相对噪声直接等同。
3. 不要改变 OCS-only 5.91 deg 的基准含义。

输出：

```text
u1_ocs_noise_both_degraded_results.csv
u1_ocs_noise_both_degraded_results.json
```

判读规则：

- OCS 噪声越大，图像退化下 U1 越差：OCS 参与恢复。
- OCS 噪声几乎无影响：U1 成功主要来自图像增强。
- 双退化崩溃：这是有效边界结果，不能隐藏。

### 12b-4：U1 大离群样本审计

目的：解释 U1 mean/p90 很好但 worst 可超过 100 deg 的矛盾。

审计阈值：

```text
error > 30 deg
error > 60 deg
error > 90 deg
```

请输出：

```text
u1_outlier_audit.csv
u1_outlier_audit.json
```

至少包含列：

```text
seed
sample_index
yaw_true
pitch_true
degradation
error_deg
pred_yaw
pred_pitch
is_repeated_outlier_across_degs
```

分析：

- 离群是否集中于 pitch 极区、yaw 边界或特定姿态。
- 是否同一样本跨退化重复离群。
- 是否某个 seed 特别不稳定。
- 如果能读取图像亮度、遮挡或 OCS 特征，也可补充。

写作边界：

- 若 worst 仍极大，不能写 fully robust。
- 可以写 mean/p90/Hit@5 are stabilized, while rare large outliers remain.

### 12b-5：未见退化泛化

目的：区分 matched augmentation robustness 与 broader degradation robustness。

训练不变：仍只用 U1 的原始 AUG_DEGS，不把下面新退化加入训练。

测试：

```text
Gaussian noise sigma=0.03
Gaussian noise sigma=0.05
Gaussian blur kernel=3
Gaussian blur kernel=5
downsample 128->64->128
downsample 128->32->128
```

若 `apply_degradation` 不支持 blur/downsample，请添加可复现实现，并报告：

```text
blur kernel size and sigma
downsample interpolation
upsample interpolation
clipping range
random seed policy
```

输出：

```text
heldout_degradation_results.csv
heldout_degradation_results.json
```

判读规则：

- 只在训练见过退化稳定：matched augmentation。
- 未见 noise、blur、downsample 也稳定：更强 degradation-aware robustness。
- 仍不能单独证明 OCS fallback，除非结合 12b-2 和 12b-3。

## 4. 推荐结果总表

请在最终 Markdown 中至少给出以下表：

1. `Table 12b-1`：image-only augmented vs U1 augmented fusion。
2. `Table 12b-2`：U1 分支遮蔽矩阵。
3. `Table 12b-3`：U1 OCS 噪声与双退化矩阵。
4. `Table 12b-4`：U1 离群样本统计。
5. `Table 12b-5`：未见退化泛化。
6. `Table 12b-final`：机制判读总表，逐项回答“是否支持 OCS fallback”。

每张表都要报告：

```text
mean ± std
median
p90
worst 或 p95
Hit@5
Hit@10
```

## 5. 结果解释红线

可以写：

```text
The 12b controls isolate whether degradation-aware fusion uses OCS as an active fallback.
Image-only augmentation provides the key baseline for attributing U1 robustness.
Branch masking and OCS-noise perturbation test whether OCS remains causally active under image degradation.
Rare outliers remain important even if mean and p90 are stable.
```

只有在结果支持时才可以写：

```text
U1 learns to use OCS as a fallback under image degradation.
OCS actively contributes to U1 robustness beyond image-only augmentation.
```

不得写：

```text
OCS 一定能托住融合。
fusion automatically robust。
near-perfect robustness。
fully robust fusion。
U1 已经证明 OCS fallback。
image masking 后必然接近 OCS-only。
```

如果结果不支持 OCS fallback，请诚实写成：

```text
U1 robustness is mainly explained by degradation-aware image training.
OCS remains informative in the diagnostic setting, but explicit OCS fallback is not established by the current U1 design.
```

## 6. 运行与产物要求

请使用当前项目环境运行。已有进度文件建议的运行方式是：

```bash
conda activate ocs_sim
```

Windows/Git Bash 中如 Python 不在 PATH，可参考：

```bash
/c/Windows/System32/cmd.exe //c "cd /d D:\我的文件\研究生学术\光学项目\0506新 && python 论文改进\补充实验\代码\run_fusion_fallback_isolation_12b.py"
```

请在结果目录保存：

```text
summary.json
run.log
mechanism_12b_summary.md
image_only_aug_results.csv/json
u1_branch_mask_results.csv/json
u1_ocs_noise_both_degraded_results.csv/json
u1_outlier_audit.csv/json
heldout_degradation_results.csv/json
```

最终 Claude 输出保存为：

```text
论文改进/论文写作/02_后整合双线修订/Claude交互/Claude输出/07b_Claude输出_融合fallback因果隔离.md
```

最终输出结构：

```text
# 07b Claude 输出：融合 fallback 因果隔离

## 1. 执行摘要
## 2. 读取文件与复用代码
## 3. 新增或修改代码路径
## 4. 运行命令与结果目录
## 5. 12b-1 image-only augmentation 对照
## 6. 12b-2 U1 分支遮蔽
## 7. 12b-3 U1 OCS 噪声与双退化
## 8. 12b-4 U1 离群样本审计
## 9. 12b-5 未见退化泛化
## 10. 机制判读：U1 是否真正使用 OCS fallback
## 11. 能写进论文的结论
## 12. 不能写的结论
## 13. 后续建议
```

重要：不要修改主稿 v0.1。不要替 Codex 做最终整合。你只需要完成实验、保存结果、给出审慎机制解释。

# Codex 审阅：07c Claude 投稿前非真实数据补实验总包

> 审阅日期：2026-06-05  
> 审阅对象：`Claude交互/Claude输出/07c_Claude输出_投稿前非真实数据补实验总包.md`  
> 覆盖实验：12c observation-style degradation、12d cross-phase generalization、12e centered control、12f late-fusion beta sweep、12g outlier audit  
> 审阅结论：通过，可进入第一档 Acta Astronautica / Advances in Space Research v0.2 审慎整合；所有结论必须限定为合成退化与受控仿真 sanity test，不得写成真实望远镜验证、自动 fallback 或 operational robustness。

## 1. 总体判定

Claude 07c 输出完成了任务说明要求的 12c-12g 补实验总包，且脚本、结果目录和 summary 文件能够支撑主要数值。Codex 审阅后判定：

1. 12c-12g 可作为 v0.2 第一档主投优先版的新增证据。
2. 07c 解决的是投稿前“非真实数据”防御，不改变本文仍为 controlled simulation study 的边界。
3. 12c 支持 degradation-aware U1 fusion 在多类合成 observation-style 退化下相对 image-only 更稳，但 combined_severe 下 U1 仍退化到 13.88 deg，不能写 fully robust。
4. 12d 说明 phase63 clean-image 上界强依赖观测几何同分布；phase120 是显著失败案例，不是跨 phase 泛化成功证据。
5. 12e 说明 clean-image 能力不完全由质心泄漏解释，但固定框定/质心相关确实贡献了一部分性能。
6. 12f 证明显式 late-fusion beta sweep 可给出推理端 oracle 上界；它不是自动门控，也不是 U1 自动切换到 OCS。
7. 12g 应进入 Supplementary/Limitations，用于防止 near-perfect、fully robust 误读。

## 2. 共用协议核查

已核查 Claude 输出与脚本/结果摘要中的共用协议：

- Split：沿用 `split_coarse_to_fine(coarse_step=10)`，训练/验证/测试口径未漂移。
- Target encoding：yaw/pitch 均采用 `[sin, cos]` 编码，整体为 4D sin-cos target。
- Metric：主指标为 great-circle angular error，同时报告 mean、median、p90/p95、worst、Hit@5、Hit@10。
- Seeds：12c/12d/12e/12f 均按 5 seeds 汇总，12g 复用 12b 全评估审计。
- OCS：concat5 per_part_log 30D 作为核心 OCS 输入；标准化统计量仅从 train split 拟合后用于 val/test，未发现 test leakage 口径。
- v0.1：本轮未覆盖既有 v0.1，Claude 输出也明确未生成 v0.2。

## 3. 分实验审阅

### 3.1 实验 12c：Observation-style 图像退化

通过。关键实现满足任务红线：退化在近似线性强度域执行，而不是直接在 normalized-log1p 域做噪声/模糊/饱和。

备案口径：

```text
lin = expm1(norm * log1p(10)) / 10
-> degradation in linear intensity domain
-> log1p(10 * lin) / log1p(10)
```

结果可支持的结论：

- clean-trained image-only 在 read/background/starfield/combined 退化下崩溃到约 78-89 deg。
- U1 fusion 在 read/background/starfield/combined_mild/combined_medium 下保持约 2 deg。
- combined_severe 下 U1 退化到 13.88 deg，OCS-only 6.58 deg 反而更稳。
- obs-aug 本轮没有成为更强方法，image-only obs-aug 与 U2 obs-aug 在 read/background/starfield/combined_medium 上表现很差，应作为诚实负结果。

限制：

- `saturate_0.8` 与 clean 基本等价，只能说明当前样本强度分布下该阈值未形成有效压力。
- 12c 只能写成 observation-chain-inspired synthetic degradation stress test；不得写 real telescope validation 或 field robustness。

### 3.2 实验 12d：phase24/phase120 渲染与跨 phase 测试

通过。phase24/phase120 的 scan_json 与渲染目录已生成，均为 2701 姿态、256 分辨率，与 phase63 训练图像保持同类 GGX 后处理管线。

可写结论：

- phase63 同分布下 image-only 为 1.69 deg，fusion_concat5 为 1.57 deg。
- phase24 下 image-only 退化到 11.34 deg，fusion_concat5 退化到 6.85 deg。
- phase120 下 image-only 与 fusion_concat5 均约 80 deg，说明几何分布变化可摧毁 phase63-trained image model。

限制：

- phase120 是强失败/边界案例，不能写成 cross-phase robust。
- fusion_concat5 在 phase120 同样失败，不能写 OCS 会自动托住跨 phase 图像分布漂移。

### 3.3 实验 12e：线性域质心居中控制

通过。质心在反 log1p 后的线性强度域计算，符合任务要求。

可写结论：

- original ResNet image-only 为 1.69±0.07 deg，centered 后为 2.88±0.14 deg。
- Hit@5 从 97.6% 降至 87.4%，说明固定框定/质心位置提供了部分姿态线索。
- centroid_x-yaw 相关从 0.665 降至 -0.019，但 centered 后仍有 2.88 deg，说明 clean-image 结果不只是质心泄漏。

限制：

- centered 的 worst 在 summary 中为 per-seed worst 的均值；至少一个 seed 的 worst 可达 111.2 deg。主文不宜强化 worst-case，只写 mean/p90/Hit@5，并把尾部误差放限制。

### 3.4 实验 12f：Late-fusion beta sweep

通过。beta 方向正确锁定为 image weight：`beta=1` 为 image-only，`beta=0` 为 OCS-only。融合在单位 sin-cos 4D 空间进行，并按 yaw/pitch 对分别归一化解码。

可写结论：

- clean 下 best beta 约 0.9，best mean 1.67 deg，接近 image-only 上界。
- noise_0.01 / noise_0.10 下 best beta 为 0.0，即 OCS 端 6.58 deg，显著优于 naive fusion 约 73 deg。
- brightness 变化下 best beta 仍偏图像端，说明显式加权能反映不同退化对模态可靠性的差异。

限制：

- best beta 是 test-oracle / inference-time upper bound，不是部署时已存在的自动权重选择器。
- 本轮 OCS MLP 是 12f 重训得到 6.58 deg，不得与旧实验的 5.91 deg 混用或写成性能升降。

### 3.5 实验 12g：Outlier audit

通过。12g 复用 12b 全评估输出做审计，没有重新训练或改变模型口径。

可写结论：

- error > 30 deg 为 42 / 49,950，占 0.084%。
- error > 60 deg 为 40 / 49,950；error > 90 deg 为 35 / 49,950。
- 离群样本集中在极区，约 50% 位于 |pitch| > 75 deg。

限制：

- 12g 是限制和补充材料证据，不是主文夸大鲁棒性的证据。
- 主文可以写 mean/p90/Hit@5 稳定，但必须承认 rare large outliers remain。

## 4. 可进入 v0.2 的结论

建议 v0.2 采用以下降调结论：

```text
The additional synthetic stress tests show that degradation-aware OCS-image fusion is substantially more stable than clean-trained image-only models under several observation-chain-inspired degradations. However, this robustness is conditional and synthetic: severe combined degradation and large phase-angle shifts remain failure cases, and explicit late-fusion weighting represents an oracle upper bound rather than an automatic deployment mechanism.
```

中文整合口径：

```text
12c-12g 支撑的是“退化感知 OCS-image 联合表示在若干合成观测链退化下更稳”，以及“显式推理端加权存在清晰的鲁棒上界路径”。它们不支持真实望远镜鲁棒性已验证，也不支持 U1 自动切换到 OCS 或 OCS standalone fallback。
```

## 5. 禁止写入 v0.2 的表述

不得写：

- fusion automatically robust。
- U1 automatically switches to OCS。
- OCS standalone fallback。
- near-perfect 或 fully robust。
- real telescope validation。
- operational robustness / field-proven robustness。
- phase120 generalization is solved。
- obs-aug is a successful robust training strategy。
- 12f best beta is deployable automatic gating。
- 将本轮 12f 的 6.58 deg 与旧 OCS-only 5.91 deg 混写为同一实验结果。

## 6. v0.2 整合建议

1. Results 可新增小节：`Synthetic observation-style degradation and cross-geometry sanity tests`。
2. 正文主表建议压缩保留 12c 的代表性退化、12d 的 phase24/phase120、12f 的 clean/noise beta sweep。
3. 12e 和 12g 更适合放 Supplementary，并在 Limitations 中引用其关键结论。
4. Discussion 必须保留 no real optical telescope validation。
5. 第一档 Acta/ASR v0.2 可以启动；CJA/AST 与 TAES/JGCD 文本继续冻结，等待作者确认第一档完结。

## 7. 阶段判定

后整合 Step 07c 完成，Codex 审阅通过。下一步只进入第一档主投优先版：

```text
论文写作/03_投稿定稿/manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md
```

不覆盖 v0.1。Q12-Q14 作者事实继续占位，不由 Codex/GPT/Claude 代填。

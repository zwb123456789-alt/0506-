# Step 2 Claude 单边初审：Introduction 初稿

> 审阅对象：`Claude交互/claude writing/02_Step2_Introduction初稿.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 Claude 这一侧输出，不与 GPT 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

Claude Step 2 输出通过单边初审，可以进入 Claude Step 3：Related Work + Table 1。

本次 Introduction 初稿基本符合当前论文定位：以统一 BRDF-driven OCS-image simulation 为主线，把 clean rendered images 明确限定为 idealized upper-bound，把 OCS 定位为 low-cost、interpretable、multi-geometry photometric constraint，并把 fusion 写成 conditional complementarity，而不是 universal superiority。

建议后续以 **Version B: Balanced Submission Introduction** 作为 Claude 侧 Introduction 主稿基础；Version A 中更保守的部分可在最终合稿时作为降调备选。

## 2. 主要优点

1. 漏斗结构清楚：从 SSA 与 optical attitude estimation 的需求，推进到 OCS / photometric image 两类模态，再落到统一物理框架和 controlled benchmark。
2. 两类模态的物理差异写得准确：OCS 聚合 visible facets 的 BRDF 贡献，images 保留 pixel-level radiance distribution。
3. 技术缺口合理：强调 existing work typically treats modalities separately，没有绝对化为“无人做过”。
4. 边界意识较好：明确写出 simulation-focused、no real optical telescope validation、yaw-pitch under fixed roll。
5. Fusion 口径安全：写成 observation quality dependent / conditional benefit，没有宣称 fusion 永远最好。
6. 没有把 `r = 0.003` 写进 Introduction，避免了把早期 TinyCNN/OCS diagnostic 误推广到 ResNet pair。

## 3. 需要修改或后续控制的问题

### 3.1 Version B 的结果数字仍偏密

Version B 中同时包含：

- ResNet clean：`1.69 ± 0.07°`
- 1% additive Gaussian noise：`85.85°`
- OCS-only：`5.91°`
- worst-case：`9.9° -> 6.6°`
- OCS noise fusion gain：`+2.0° -> +6.3°`

这些数字都没有越界，但 Introduction 可能显得过早进入 Results。最终主稿建议保留 2-3 个最支撑主线的数字：

- 必留：ResNet clean `1.69 ± 0.07°`
- 必留：1% Gaussian image noise `85.85°`
- 可留：OCS-only `5.91°`
- 建议移到 Results：`9.9° -> 6.6°` 和 `+2.0° -> +6.3°`

### 3.2 图像退化必须继续写成 controlled degradation

Claude 已经写出 “1% additive Gaussian noise”，但后续必须持续限定其含义。它只能作为 controlled degradation test 或 observation-quality stress test，不能写成完整真实地基观测退化模型。

更稳妥表述：

```text
controlled image degradation test
observation-quality stress test
idealized perturbation motivated by image-quality degradation
```

避免表述：

```text
realistic ground-based degradation has been validated
field performance under atmospheric degradation
```

### 3.3 OCS robustness 需要限定在当前仿真输入关系内

“OCS-only inversion maintains 5.91° regardless of image quality” 这句话逻辑上成立，因为 OCS 分支不依赖 image inputs。后续 Results/Discussion 中仍需补一句边界：

> This robustness refers to image-quality degradation in the controlled benchmark; real OCS measurements remain affected by calibration, radiometric noise, atmosphere, phase-angle coverage, and model mismatch.

### 3.4 Citation placeholders 需要在 Step 3 严格收敛

Claude Step 2 使用了安全占位符，没有发明具体引用，这是正确的。但 placeholder 中出现一些泛化候选，例如 `SSA overview`、`CNN pose estimation`、`observation degradation effects`。Step 3 必须用项目文献清单逐步替换，或保留 `[to verify]`，不能自行编造作者、题名、期刊或 DOI。

最低需要覆盖：

- Yang 2024 Photonics
- Lu Yao 2024 Universe
- Wang 2024 ASR
- Burton 2024 ASR
- Dickinson 2025
- Kumar 2025 Acta Astronautica
- Liu 2024 Remote Sensing
- Fankhauser 2023 AJ

### 3.5 “two critical gaps” 可以保留，但避免过强唯一性

Version B 中的 “Two critical gaps remain” 可以作为二区/一区边缘写法保留。正式稿中建议配合 `typically`、`systematically`、`within a unified physical benchmark` 这类限定词，不要写成：

```text
No prior work has studied this problem.
```

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明新实验或新数值 | 未发现 |
| 是否发明具体引用 | 未发现，使用占位符 |
| 是否把 clean image 写成真实场景性能 | 未发现 |
| 是否宣称 fusion 永远最优 | 未发现 |
| 是否宣称 OCS 永远强于图像 | 未发现 |
| 是否宣称已有真实光学望远镜验证 | 未发现 |
| 是否把 ISAR 并入主线 | 未发现 |
| 是否误用 `r = 0.003` | 未发现，未写入 Introduction |

## 5. 给 Claude 的后续修订意见

进入 Step 3 前，Claude 应保留以下原则：

1. Introduction 主稿采用 Version B，但最终合稿时降低结果数字密度。
2. 保留 clean rendered images = upper-bound 的限定。
3. 保留 no real optical telescope validation、simulation-focused、fixed roll/yaw-pitch 的边界。
4. Related Work 不要写成文献流水账，应按 BRDF modeling、OCS/light-curve inversion、image-based pose、fusion/robustness 四条线组织。
5. Table 1 的目的不是证明本文 SOTA，而是说明本文在 unified OCS-image physical framework 与 conditional complementarity analysis 上的位置。
6. 所有不确定文献信息必须标 `[to verify]` 或 `[需要作者核对]`。

## 6. 是否进入下一阶段

结论：可以进入 Claude Step 3。

下一阶段指导文件：

```text
Claude交互/04_Step3_Claude_RelatedWork_Table1指导.md
```

Claude 输出建议保存为：

```text
Claude交互/claude writing/03_Step3_Claude输出_RelatedWork_Table1.md
```

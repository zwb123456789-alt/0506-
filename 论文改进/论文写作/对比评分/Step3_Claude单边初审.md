# Step 3 Claude 单边初审：Related Work + Table 1

> 审阅对象：`Claude交互/claude writing/03_Step3_Claude输出_RelatedWork_Table1.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 Claude 这一侧输出，不与 GPT 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

Claude Step 3 输出通过单边初审，可以进入 Claude Step 4：Method。

本次 Related Work 基本完成了阶段目标：按 BRDF/optical signatures、light-curve/OCS attitude inversion、image-based pose estimation、multi-modal fusion 四条机制线组织，没有写成逐篇文献流水账，也没有宣称本文是 SOTA 或 first。Table 1 的定位也正确：用于说明本文的组合位置，而不是做胜负式比较。

## 2. 主要优点

1. 结构达标：2.1-2.4 覆盖了 BRDF、OCS/light curve、image pose、fusion robustness 四条必要文献线。
2. 缺口指向明确：每节都能回到 unified BRDF / geometry / material / self-occlusion assumptions 下比较 OCS 与 image 的核心 gap。
3. 风险控制较好：大量不确定文献信息标注 `[to verify]`，没有强行编造 DOI、卷期页码或具体实验细节。
4. Clean-image 边界正确：没有把图像结果写成真实望远镜性能，而是写成 idealized upper-bound。
5. Fusion 口径安全：明确写出 conditional on observation quality，没有写 fusion universally guaranteed。
6. Table 1 最后一行对本文边界写得较稳：analytical/rendering consistency + controlled sensitivity; no real telescope。

## 3. 需要修改或后续控制的问题

### 3.1 Table 1 的 `[to verify]` 密度较高

当前 Table 1 适合作为安全草稿，但正式稿不能保留大量 `[to verify]`。后续至少要核对这些列：

- `BRDF`
- `Self-occlusion`
- `Attitude inversion`
- `Fusion`
- `External validation`

尤其是 Wang 2024、Burton 2024、Kumar 2025、Dickinson 2025 这几篇，正式填表前应至少核对 abstract、method 和 validation/experiment 部分。

### 3.2 “唯一同时覆盖”表述需要降调

Logic Map 第 7 条写到本文是“唯一同时覆盖 real STL + GGX BRDF + self-occlusion + OCS + image + controlled inversion + fusion 的 benchmark”。这个判断可能被审稿人用反例挑战。

建议正式稿改成：

```text
Table 1 highlights the combined position of this work across real STL geometry, nonuniform BRDF modeling, self-occlusion, OCS, photometric images, controlled inversion, and fusion.
```

不要写：

```text
the only work that covers ...
```

### 3.3 Yang / Lu / Fankhauser 等引用信息需要精确核对

Claude 正确使用了 `[to verify]`，但正式参考文献需要确认：

- Yang 文献最终年份、期刊、卷期页码，以及是否应写 Photonics 2025 而不是 2024。
- Lu Yao 是单作者还是多作者，BRDF 类型是否为 Phong、Cook-Torrance 或其他。
- Fankhauser et al. 的具体模型类型、是否适合支撑 earthshine / radiometric complexity。

### 3.4 不要把 Yang 直接写成 GGX 的唯一依据

当前 §2.1 写法基本安全，但 “Cook-Torrance/GGX basis” 后续应更稳：

```text
Satellite-material reflectance measurements motivate physically based BRDF modeling.
```

不要写成：

```text
Yang proves GGX/Cook-Torrance is the correct model for all satellite materials.
```

### 3.5 Liu 2024 的作用要保持“类比支撑”

Liu 2024 是 visual-inertial fusion，不是 OCS-image photometric fusion。Claude 已经说明差异，这是正确的。正式稿中它只能支撑 feature-level / tightly coupled fusion 的一般思想，不能被写成直接相关工作。

## 4. 红线检查

| 检查项 | 结论 |
|---|---|
| 是否发明新实验或新数值 | 未发现 |
| 是否发明 DOI 或完整参考文献信息 | 未发现，使用 `[to verify]` |
| 是否宣称本文 SOTA / first | 未发现 |
| 是否夸大 fusion | 未发现 |
| 是否把 clean image 写成真实场景性能 | 未发现 |
| 是否宣称真实光学望远镜验证 | 未发现 |
| 是否把 ISAR 并入主线 | 未发现 |
| 是否覆盖四条必要文献线 | 已覆盖 |

## 5. 给 Claude 的后续修订意见

进入 Step 4 Method 前，Claude 应记住：

1. Related Work 暂时通过，但 Table 1 是“待核对草稿”，不是最终参考文献表。
2. Method 章节不要依赖不确定文献细节，只写本项目已经存在的方法事实。
3. Method 要写成可复现研究方法，不写成代码说明或工程日志。
4. Method 中可以描述 unified forward model、STL geometry、GGX BRDF、self-occlusion、OCS integration、photometric rendering、inversion models、metrics。
5. Method 中不要提前解释 Results 数字；具体性能留到 Results。
6. `all_raw` 必须写成 semi-oracle upper bound，`per_part_log` 写成 practical OCS setting。
7. Clean rendered images 必须写成 idealized upper-bound，不是真实望远镜图像。

## 6. 是否进入下一阶段

结论：可以进入 Claude Step 4。

下一阶段指导文件：

```text
Claude交互/05_Step4_Claude_Method指导.md
```

Claude 输出建议保存为：

```text
Claude交互/claude writing/04_Step4_Claude输出_Method.md
```

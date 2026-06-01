# Step 3 GPT 单边初审：Related Work + Table 1

> 审阅对象：`GPT交互/GPT writing/03_Step3_GPT输出_RelatedWork_Table1.md`  
> 审阅日期：2026-06-01  
> 审阅原则：只审阅 GPT 这一侧输出，不与 Claude 进行优劣比较；对比评分表保留到两边完整初稿完成后再使用。

## 1. 总体结论

GPT Step 3 输出通过单边初审，可以进入 GPT Step 4：Method。

本次 Related Work 的组织方式基本符合要求：按 BRDF/optical signatures、light-curve/OCS attitude inversion、image-based pose estimation、multi-modal fusion 四条机制线展开，没有写成逐篇文献流水账，也没有宣称本文是 SOTA 或 first。Table 1 的定位也正确：用于说明本文的组合位置，而不是做胜负式比较。

## 2. 主要优点

1. 结构达标：2.1-2.4 四节覆盖了 BRDF、OCS/light curve、image pose、fusion robustness 四条必要文献线。
2. 主线贴合：每节末尾都能回到本文的核心 gap，即 OCS 与 photometric images 需要在 shared geometry / material / BRDF / self-occlusion assumptions 下比较。
3. 风险控制较好：没有说 “no prior work has ever...”，没有写 fusion universally superior，也没有把 clean image 写成 field performance。
4. Table 1 处理谨慎：不确定信息多数标注为 `[to verify]`，没有强行编造细节。
5. Citation Placeholder Map 有用：后续可以直接作为 Zotero/本地 PDF 核对清单。

## 3. 需要修改或后续控制的问题

### 3.1 文献信息必须正式核对

GPT 输出中保留了大量 `[to verify]`，这是安全做法，但正式稿不能长期保留。后续进入定稿前至少要核对：

- Yang 文献的最终引用年份、题名、卷期页码、DOI。
- Wang 2024 ASR 的目标、数据类型、反演方法、是否含 BRDF/遮挡假设。
- Burton 2024 ASR 的验证设置、目标几何、PSO 输入输出。
- Kumar 2025 Acta Astronautica 的最终出版信息和任务细节。
- Dickinson 2025 是使用博士论文引用，还是换成更正式的会议/期刊版本。

我已做最小外部核对：Yang 的 MDPI 页面显示为 *Photonics* 2025, 12(1), 17，发布日期为 2024-12-27（https://www.mdpi.com/2304-6732/12/1/17）；Lu/Yao 为 *Universe* 2024, 10(5), 215（https://www.mdpi.com/2218-1997/10/5/215）；Fankhauser 为 *AJ* 2023, 166, 59（https://doi.org/10.3847/1538-3881/ace047）。正式参考文献仍应以 Zotero 或出版社页面为准。

### 3.2 Table 1 中部分单元格不能在正式稿中含糊

当前 Table 1 适合草稿，但正式稿需要减少 `[to verify]` 密度。尤其是这些列：

- `Self-occlusion`
- `External validation`
- `Attitude inversion`
- `Fusion`

这些列会被审稿人直接用来判断本文差异化是否成立。每篇核心文献至少要核对 abstract、method、experiment/validation 章节后再填。

### 3.3 Related Work 里可以再压缩“本文区别”的重复表达

当前四节末尾多次重复：

> generated from the same geometry, material assignment, BRDF, attitude convention, and self-occlusion assumptions

这是正确的主线，但正式稿可适当变化表达，避免机械重复。可以保留一次完整表述，其他位置改为：

- shared physical forward model
- common scattering and visibility assumptions
- consistent OCS-image simulation protocol

### 3.4 不要把 Yang 文献直接写成 Cook-Torrance/GGX 的唯一依据

Yang 文献更适合支撑 satellite material reflectance / pBRDF / goniopolarimetric measurement。若要支撑 GGX/Cook-Torrance 的具体选型，还需要配合本项目的 BRDF 设计说明和更通用的微表面 BRDF 文献。正式稿建议写成：

> Satellite-material reflectance measurements motivate physically based BRDF modeling.

而不是：

> Yang proves that GGX/Cook-Torrance is the correct model for all satellite materials.

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

## 5. 给 GPT 的后续修订意见

进入 Step 4 Method 前，GPT 应记住：

1. Related Work 暂时通过，但 Table 1 是“待核对草稿”，不是最终参考文献表。
2. 后续 Method 不能再依赖文献不确定项，必须只写本项目已经存在的方法事实。
3. Method 章节要写成可复现研究方法，不写成代码说明或工程日志。
4. Method 中可以描述 unified framework、STL geometry、GGX BRDF、self-occlusion、OCS integration、photometric rendering、inversion models、metrics。
5. 不要在 Method 中提前解释 Results 数字；具体性能留到 Results。

## 6. 是否进入下一阶段

结论：可以进入 GPT Step 4。

下一阶段应生成：

`GPT交互/04_Step4_GPT_Method交互提示词.md`

GPT 输出建议保存为：

`GPT交互/GPT writing/04_Step4_GPT输出_Method.md`

# GPT 写作工作流总览

> 用途：当当前对话被清空或新开对话时，把本文件交给 Codex/GPT，即可恢复论文写作上下文、知道应读哪些文件、当前写到哪一步、下一步做什么。  
> 更新规则：每完成一个阶段后，更新“当前进度”“已生成文件”“下一步任务”三部分即可。保留主流程，不需要记录全部对话细节。

---

## 1. 项目与论文定位

项目根目录：

`D:\我的文件\研究生学术\光学项目\0506新`

论文写作工作区：

`D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\GPT交互`

生成文件统一放置：

`D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\GPT交互\GPT writing`

论文主题：

基于统一 BRDF 与自遮挡建模的 OCS-光度图像空间目标姿态反演基准研究，重点分析 clean synthetic image 上限、图像退化脆弱性、OCS 鲁棒光度约束，以及 OCS-image fusion 的条件性互补。

英文定位：

> A physically consistent simulation and controlled inversion study that reveals when OCS and photometric images provide complementary attitude constraints under ideal and degraded observation conditions.

主攻档次：

- SCI 二区
- 按一区边缘标准组织论证、图表和审稿防御
- 候选期刊：Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing

---

## 2. 写作边界

必须遵守：

1. 不写“OCS 是主力、图像只是辅助、fusion 一定最优”的旧叙事。
2. 必须承认 ResNet 等强图像模型在 clean synthetic image 下性能极高。
3. clean image 结果只能解释为 idealized upper-bound，不能写成真实场景性能。
4. 必须强调真实地基光学观测存在 seeing、tracking error、sensor noise、PSF blur、low resolution、phase-angle variation 等退化。
5. OCS 的价值定位为 low-cost、interpretable、multi-geometry、robust photometric constraint。
6. Fusion 的价值定位为 conditional complementarity，而不是 universal superiority。
7. 所有结论必须由现有实验数据支撑，不创造新实验、新数值或真实验证。
8. 没有真实光学望远镜图像验证，必须写入 limitations。
9. ISAR 不进入本文主线，只能作为 modality boundary / future work。

---

## 3. 当前可用核心证据

物理建模链条：

- 真实卫星 STL 几何
- 非均匀材料分区
- GGX/Cook-Torrance BRDF
- 解析射线自遮挡
- 多观测几何 OCS 扫描
- 光度图像渲染
- yaw-pitch 姿态反演，fixed roll
- OCS-only / image-only / late fusion / feature fusion

核心数值：

- ResNet image-only clean：1.69 ± 0.07 deg, Hit@5 = 97.6%
- ResNet + concat5 per_part_log：1.47 ± 0.07 deg
- worst-case：9.9 deg -> 6.6 deg
- 1% Gaussian image noise：ResNet 退化到 85.85 deg, Hit@5 = 2.2%
- OCS MLP per_part_log：5.91 deg，作为实用 OCS-only 结果
- OCS MLP all_raw 45D：3.98 ± 0.60 deg, Hit@5 = 90.7%，只能作为 semi-oracle upper bound
- TinyCNN image-only：12.38 ± 0.74 deg, Hit@5 = 26.1%，只能作为 lightweight baseline
- Early feature fusion per_part_log：4.10 ± 0.77 deg, Hit@5 = 87.3%
- OCS-CNN error correlation r = 0.003，但只能标注为 earlier TinyCNN/OCS diagnostic，不能默认代表 ResNet pair
- OCS-noise fusion gain 从 +1.97 deg 增至 +6.29 deg，随 OCS noise 0% 到 20% 增加

重要限制：

- 无真实光学望远镜图像验证
- clean rendered images 是 idealized photometric imagery
- atmosphere、detector response、PSF、earthshine、background contamination 未显式建模
- 当前任务估计 yaw-pitch，roll 固定
- 图像主分支主要基于 phase63
- 材料参数为 nominal，需要 sensitivity analysis 和文献支撑

---

## 4. 新对话开始时应读取的文件

新对话恢复时，建议按顺序读取：

1. 本文件  
   `论文改进\论文写作\GPT交互\GPT写作工作流总览.md`

2. GPT 交互总路线  
   `论文改进\论文写作\GPT交互\00_GPT交互使用说明与总路线.md`

3. 当前阶段产物与审阅记录  
   当前应读：  
   `论文改进\论文写作\最终整合\最终整合版_v0.1_基于GPT吸收Claude.md`  
   `论文改进\论文写作\对比评分\最终初稿_GPT_vs_Claude_评分决策.md`  
   `论文改进\论文写作\GPT交互\GPT writing\07_GPT输出_全文整合初稿.md`  
   `论文改进\论文写作\对比评分\Step7_GPT单边初审.md`  

4. 已生成阶段产物  
   `论文改进\论文写作\GPT交互\GPT writing\01_Step1_GPT输出_论文定位标题摘要贡献点.md`  
   `论文改进\论文写作\GPT交互\GPT writing\02_Step2_GPT输出_Introduction结构与初稿.md`  
   `论文改进\论文写作\GPT交互\GPT writing\03_Step3_GPT输出_RelatedWork_Table1.md`  
   `论文改进\论文写作\GPT交互\GPT writing\04_Step4_GPT输出_Method.md`  
   `论文改进\论文写作\GPT交互\GPT writing\05_Step5_GPT输出_Results.md`  
   `论文改进\论文写作\GPT交互\GPT writing\06_Step6_GPT输出_Discussion_Limitations_Conclusion.md`

5. 如需要回到项目全局背景，再读：  
   `论文项目总览 copy.md`  
   `论文改进\20260529_论文写作完整规划.md`  
   `CLAUDE.md`

---

## 5. 已完成阶段

### Step 1：论文定位、标题、摘要骨架与贡献点

状态：已完成。

生成文件：

`论文改进\论文写作\GPT交互\GPT writing\01_Step1_GPT输出_论文定位标题摘要贡献点.md`

主要结论：

- 推荐叙事路线：Route B 平衡投稿版。
- 推荐主线：统一 BRDF-driven OCS-image simulation framework + conditional complementarity。
- 推荐标题候选：  
  `BRDF-Driven Optical Cross Section and Photometric Image Simulation for Robust Space Object Attitude Inversion`
- 核心科学问题：在非均匀 BRDF、自遮挡和观测质量变化条件下，OCS 与 photometric images 分别提供什么姿态信息，fusion 在什么条件下提供鲁棒互补约束。
- 已给出 abstract skeleton、4 条 contributions、claim-evidence-risk map。

### Step 2：Introduction 结构与初稿

状态：已完成。

生成文件：

`论文改进\论文写作\GPT交互\GPT writing\02_Step2_GPT输出_Introduction结构与初稿.md`

主要内容：

- Introduction logic map
- 5 段 paragraph plan
- Version A：Conservative Reviewer-Safe Introduction
- Version B：Balanced Submission Introduction
- 推荐使用 Version B 作为主稿基础
- Claim-Evidence-Risk Map
- Citation placeholders
- Self-review checklist

当前建议：

- 以 Version B 为主稿基础。
- 如果目标期刊偏保守，可从 Version A 吸收更明确的边界说明。
- Version B 中数字略多，后续正式稿可考虑删减 1-2 个结果数字。
- Codex 已完成单边初审，记录位于：`论文改进\论文写作\对比评分\Step2_GPT单边初审.md`

### Step 3：Related Work + Table 1

状态：已完成。

生成文件：

`论文改进\论文写作\GPT交互\GPT writing\03_Step3_GPT输出_RelatedWork_Table1.md`

主要内容：

- Related Work logic map
- 2.1-2.4 四个 Related Work 小节结构
- 英文 Related Work 初稿
- Table 1 文献方案对比表草稿
- Citation Placeholder Map
- Claim-Evidence-Risk Map
- Self-review checklist

当前建议：

- Related Work 采用机制分组，不做逐篇流水账。
- Table 1 的目的不是证明本文 SOTA，而是说明本文的组合位置。
- 多处文献信息仍标注 `[to verify]`，需要作者后续用 Zotero/本地文献笔记核对。
- Codex 已完成单边初审，记录位于：`论文改进\论文写作\对比评分\Step3_GPT单边初审.md`

### Step 4：Method

状态：已完成。

生成文件：

`论文改进\论文写作\GPT交互\GPT writing\04_Step4_GPT输出_Method.md`

主要内容：

- Method logic map
- Pipeline figure sketch
- 3.1-3.8 Method section outline
- 英文 Method 初稿
- Method variables and notation table
- Reproducibility checklist
- Claim-Evidence-Risk Map
- Self-review checklist

当前建议：

- Method 采用“统一 forward model -> OCS/image 生成 -> controlled inversion models -> metrics”的顺序。
- 需要作者核对 Euler rotation convention、angular error formula、target encoding、ResNet 是否明确为 ResNet-18、训练超参数放主文还是补充材料。
- Method 已明确 clean rendered images 不是真实望远镜图像，all_raw 是 semi-oracle，per_part_log 是更实用 OCS 设置。
- Codex 已完成单边初审，记录位于：`论文改进\论文写作\对比评分\Step4_GPT单边初审.md`

### Step 5：Results

状态：已完成。

生成文件：

`论文改进\论文写作\GPT交互\GPT writing\05_Step5_GPT输出_Results.md`

主要内容：

- Results evidence ladder
- 4.1-4.6 Results section outline
- 英文 Results 初稿
- Figure and Table Plan
- Main results tables draft
- Claim-Evidence-Risk Map
- Self-review checklist

当前建议：

- Results 采用“forward-model credibility -> OCS-only -> image-only clean upper bound -> fusion -> degradation robustness -> ablation/sensitivity”的证据链。
- 已明确 ResNet clean 是 idealized upper-bound，不是 field performance。
- 已明确 all_raw 是 semi-oracle，per_part_log 是 practical OCS setting。
- 需要作者确认 angular error formula、0% OCS noise 表格值、BRDF/occlusion/roll/random split/phase63 fairness 哪些已有最终数值可放正文。

### Step 6：Discussion / Limitations / Conclusion

状态：已完成。

生成文件：

`论文改进\论文写作\GPT交互\GPT writing\06_Step6_GPT输出_Discussion_Limitations_Conclusion.md`

主要内容：

- Discussion logic map
- 5.1-5.6 Discussion section outline
- 英文 Discussion 初稿
- Limitations draft
- Conclusion draft
- Reviewer-facing defense points
- Claim-Evidence-Risk Map
- Self-review checklist

当前建议：

- Discussion 重点解释 clean ResNet 为什么强、为什么 OCS 仍重要、fusion 为什么是条件性互补。
- Limitations 已明确 no real telescope validation、clean image upper-bound、fixed roll、phase63、nominal materials、未建模真实退化。
- Codex 已完成单边初审，记录位于：`论文改进\论文写作\对比评分\Step6_GPT单边初审.md`
- 下一步建议进入全文整合与修订：统一术语、精简重复数字、核对 citations 和 Table 1、补齐作者确认项。

### Step 7：全文整合初稿

状态：已完成。

生成文件：

`论文改进\论文写作\GPT交互\GPT writing\07_GPT输出_全文整合初稿.md`

主要内容：

- Integrated Manuscript Draft：Title、Abstract、Keywords、Introduction、Related Work、Method、Results、Discussion、Conclusion、Data Availability、Author Contributions、Conflict of Interest、References placeholders
- 保留 Table 1、Table 2、Table 3、Table 4 草稿
- 保留 Fig. 1-7 caption intent，用于后续图表制作
- Cross-section Consistency Checklist
- Author Confirmation List
- Revision Priority List
- Self-review Checklist

当前建议：

- 该稿是连续英文论文初稿，不是最终投稿稿；下一轮应先做作者核对和数值/引用核查。
- 必须优先确认 Euler convention、angular error formula、target encoding、0% OCS-noise table values、Table 1 文献信息和可进入正文的 sensitivity/ablation 数值。
- 在图表制作前，先决定 Table 1 是否放主文，Fig. 7 是否有足够最终数据支撑。
- Codex 已完成单边初审，记录位于：`论文改进\论文写作\对比评分\Step7_GPT单边初审.md`
- GPT 侧候选完整初稿已完成；Claude 侧候选完整初稿也已完成。最终评分决策见：`论文改进\论文写作\对比评分\最终初稿_GPT_vs_Claude_评分决策.md`

---

## 6. 当前进度与下一步

当前进行到：

**Step 1-7 已完成，GPT 侧已有一版连续英文全文整合初稿并已通过单边初审。Claude 侧完整初稿也已完成，最终评分决策已生成。最终整合版 v0.1 已生成，当前进入作者确认、数值审计、引用核验与图表规划。**

下一步应做：

1. 优先读取最终整合版 v0.1、最终评分决策和 GPT 原始全文初稿：  
   `论文改进\论文写作\最终整合\最终整合版_v0.1_基于GPT吸收Claude.md`
   `论文改进\论文写作\对比评分\最终初稿_GPT_vs_Claude_评分决策.md`
   `论文改进\论文写作\GPT交互\GPT writing\07_GPT输出_全文整合初稿.md`
   `论文改进\论文写作\对比评分\Step7_GPT单边初审.md`

2. 作者优先核对以下关键项：
   - 目标期刊优先级
   - Title 选择
   - Euler rotation convention
   - angular error formula
   - target encoding
   - 0% OCS noise 表格值
   - BRDF/occlusion/roll/random split/phase63 fairness 是否有最终数值
   - Table 1 文献信息 `[to verify]`

3. 当前下一轮修订任务建议：
   - 先做“作者确认项清单逐项回复”
   - 再做“数值审计表与实验日志核对”
   - 再做“citation verification 与参考文献格式化”
   - 再做“图表制作与 caption 定稿”
   - 最后做“全文语言压缩与投稿期刊风格调整”

4. 最终整合状态：
   - 以 GPT 完整初稿为结构底稿和证据底稿。
   - 吸收 Claude 完整初稿的标题、摘要组织、Introduction 压缩写法和 Discussion 精简表达。
   - 已输出到 `论文写作\最终整合\最终整合版_v0.1_基于GPT吸收Claude.md`。

---

## 7. 阶段路线总表

| Step | 内容 | 状态 | 输出位置 |
|---|---|---|---|
| Step 1 | 论文定位、标题、摘要骨架、贡献点 | 已完成 | `GPT writing\01_Step1_GPT输出_论文定位标题摘要贡献点.md` |
| Step 2 | Introduction 结构与初稿 | 已完成 | `GPT writing\02_Step2_GPT输出_Introduction结构与初稿.md` |
| Step 3 | Related Work + Table 1 | 已完成 | `GPT writing\03_Step3_GPT输出_RelatedWork_Table1.md` |
| Step 4 | Method | 已完成 | `GPT writing\04_Step4_GPT输出_Method.md` |
| Step 5 | Results | 已完成 | `GPT writing\05_Step5_GPT输出_Results.md` |
| Step 6 | Discussion / Limitations / Conclusion | 已完成 | `GPT writing\06_Step6_GPT输出_Discussion_Limitations_Conclusion.md` |
| Step 7 | 全文整合初稿 | 已完成 | `GPT writing\07_GPT输出_全文整合初稿.md` |
| Step 8 | 最终整合 v0.1 | 已完成 | `..\最终整合\最终整合版_v0.1_基于GPT吸收Claude.md` |

---

## 8. 每阶段输出要求

每一步输出都应包含：

1. 本轮目标复述
2. 推荐叙事或结构
3. 英文正文或骨架
4. 中文解释
5. Claim-Evidence-Risk Map
6. Self-review Checklist
7. 需要作者确认的问题
8. 下一轮修改建议

写作要求：

- 英文论文文本为主，中文解释为辅。
- 不发明引用，先使用 `[CITATION: ...]` 占位。
- 不新增实验或数值。
- 对不确定内容用 `[需要作者确认：...]`。
- 每个阶段完成后保存到 `GPT writing` 文件夹。

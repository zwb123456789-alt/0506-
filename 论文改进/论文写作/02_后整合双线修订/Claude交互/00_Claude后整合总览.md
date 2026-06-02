# Claude 后整合交互总览

> 最后更新：2026-06-01  
> 用途：给 Claude 新会话恢复上下文使用。当前不是从零写论文，而是在修订已有最终整合版 v0.1。

## 1. 当前任务身份

你是论文后整合阶段的 Claude 协作端。你的职责是按 Codex 指定阶段，对最终整合版 v0.1 做结构化审计、核验、压缩或修订建议。你不直接改写全文，不新增实验，不发明引用。

主稿路径：

```text
论文写作\01_初稿生成与整合\最终整合\最终整合版_v0.1_基于GPT吸收Claude.md
```

## 2. 新会话必须先读

如果这是新会话，或你不确定上下文，必须先阅读或要求作者提供以下内容：

```text
论文写作\00_总控流程.md
论文写作\02_后整合双线修订\00_后整合双线总览.md
论文写作\02_后整合双线修订\Claude交互\00_Claude后整合总览.md
论文写作\01_初稿生成与整合\最终整合\最终整合版_v0.1_基于GPT吸收Claude.md
论文改进\20260529_论文写作完整规划.md
论文项目总览 copy.md
论文改进\20260529_补充实验进度.md
```

如果不能读取这些文件，必须请作者粘贴关键内容。`论文项目总览 copy.md` 较长，可先读取或索要与当前任务相关的实验结果、方法细节和数值段落。未读取主稿、全局背景和总览前，不要直接改写论文正文。

硬性约束：

- 未读主稿、全局背景和总览前，不得直接改写论文正文，只能列检查框架、问题清单或要求补充材料。
- 禁止编造实验结果、引用文献、方法细节、模型配置、期刊要求或任何作者尚未确认的事实。
- Claude 输出必须交给 Codex 审阅整合后，才能进入主稿版本线；Claude 不得直接覆盖主稿。

## 3. 同一会话读取规则

同一会话内，如果已经读过上述文件，后续任务不需要重复读取全部文件。每轮只需读取：

- 当前阶段 Claude 指导文件。
- 新增的作者说明或实验记录。
- Codex 上一轮审阅意见。

## 4. 当前阶段

当前阶段：

```text
06_投稿材料（已完成）
```

当前指导文件：

```text
论文写作\02_后整合双线修订\Claude交互\06_投稿材料_Claude指导.md
```

输出保存位置：

```text
论文写作\02_后整合双线修订\Claude交互\Claude输出\06_Claude输出_投稿材料.md
```

## 5. Claude 输出风格

Claude 侧应偏结构化、章节顺序、可执行审计：

1. 按 Abstract、Introduction、Related Work、Method、Results、Discussion、Conclusion、Tables、Figures 顺序检查。
2. 每项写明：原文位置、问题类型、风险、建议处理、是否需要作者确认。
3. 只给可追踪修订建议，不生成未确认事实。
4. 保持输出格式稳定，便于 Codex 合并。

## 6. 完成后的状态更新

Claude 完成本阶段输出后，不得自行修改主稿，也不得更新 Codex 总控文件。Claude 必须自行更新本交互端总览文件：

```text
论文写作\02_后整合双线修订\Claude交互\00_Claude后整合总览.md
```

更新内容至少包括：

1. 本轮任务是否完成。
2. 输出文件建议保存位置。
3. 仍需作者确认的问题。
4. 仍需 Codex 审阅或整合的问题。
5. 下一轮应读取的文件或等待的 Codex 审阅意见。

作者把 Claude 输出和已更新的 Claude 总览交给 Codex 后，由 Codex 审阅并更新 `论文写作\00_总控流程.md` 与 `论文写作\02_后整合双线修订\00_后整合双线总览.md`。

## 7. 本轮完成情况（2026-06-01）

### 7.1 第 1 阶段完成状态

**已完成**：第 1 阶段（作者确认与数值审计）Claude 侧输出。

输出文件：
```text
论文写作\02_后整合双线修订\Claude交互\Claude输出\01_Claude输出_作者确认与数值审计.md
```

### 7.2 第 2 阶段完成状态

**已完成**：第 2 阶段（引用核验与 Related Work 修订）Claude 侧输出。

输出文件：
```text
论文写作\02_后整合双线修订\Claude交互\Claude输出\02_Claude输出_引用核验与RelatedWork修订.md
```

内容包括：
- Introduction 5 个 [CITATION] 占位的具体替换建议（基于 .bib 核验）
- Related Work 8 篇 [to verify] 文献逐条核验（含完整书目信息、DOI、PDF 状态）
- Table 1 逐行逐列审计（9 行 × 9 列）
- Related Work 修订版段落骨架（§2.1-2.4）
- 不可使用/暂缓使用文献清单
- 9 项可直接进入 v0.2 的安全替换
- 7 项作者仍需补充的材料

### 7.3 关键发现

1. **"Burton et al. 2024 ASR" 作者名可能错误**：.bib 中对应条目第一作者为 Hanada，非 Burton。作者必须下载 PDF 核实。
2. **"Yang et al. 2024/2025" 无 2025 版本**：.bib 仅有 2024 年一篇，应统一为 Yang 2024。
3. **C05 地基光学退化引用缺口**：当前 .bib 无专门讨论大气 seeing/PSF 退化的文献，需作者补充。
4. **7/8 篇 [to verify] 文献已通过 .bib 核验**，可安全删除占位。
5. **Table 1 中 Wang/Burton/Kumar 的 BRDF 和 self-occlusion 字段无法仅从 .bib 确认**，需下载 PDF。

### 7.4 仍需作者确认的问题

1. 下载 Burton/Hanada 2024 ASR PDF 确认第一作者
2. 下载 Wang 2024 / Kumar 2025 / Fankhauser 2023 PDF 确认 Table 1 字段
3. 补充 1 篇地基光学退化文献（大气 seeing / PSF / 跟踪误差）
4. 决定是否在 Table 1 增加 AISwarm-LS 2025 和/或 Valenta 2022 行
5. 第 1 阶段遗留：Euler convention、angular error formula、target encoding

### 7.5 仍需 Codex 审阅的问题

1. 审阅第 2 阶段 Claude 输出
2. 与 GPT 侧第 2 阶段输出对比整合
3. 生成 `阶段整合输出/02_引用核验与RelatedWork修订_整合清单.md`
4. 决定 9 项安全替换是否可直接纳入 v0.2

### 7.7 第 3 阶段完成状态（2026-06-02）

**已完成**：第 3 阶段（图表制作与 Caption 定稿）Claude 侧输出。

输出文件：
```text
论文写作\02_后整合双线修订\Claude交互\Claude输出\03_Claude输出_图表制作与Caption定稿.md
```

内容包括：
- 7 Figures + 4 Tables 逐项审计（主结论 / 结构 / 数据来源 / 待确认项 / 风险）
- 主文图表方案（11 项，含顺序）
- 补充材料图表方案（9 项：Fig.S1-S6 + Table S1-S3）
- 全部 Fig.1-7 和 Table 1-4 的 Caption 草案
- 实际绘图前 9 项作者确认问题
- 第 2 阶段 bib 修订对图表引用名的影响（Yang→2025, Liu→Yi, 确认 Burton）

### 7.8 仍需作者确认的问题（跨阶段汇总）

**第 1 阶段遗留**：
1. Euler order / rotation matrix convention
2. Angular error formula
3. Target encoding
4. 目标期刊选择
5. 哪些 ablation 进正文 vs 补充材料

**第 2 阶段遗留**：
6. 下载 Wang 2024 / Kumar 2025 / Fankhauser 2023 PDF 确认 Table 1 字段
7. 补充 1 篇地基光学退化文献

**第 3 阶段新增**：
8. Fig. 7 选择哪 2-3 个 panel 进正文
9. Fig. 3 展示哪个几何的 OCS 热图
10. Table 1 是否放正文还是补充材料（9 列较宽）

### 7.9 下一轮应读取的文件

- Codex 对第 3/4 阶段 Claude 输出的审阅意见
- 第 5 阶段 Claude 指导文件（模拟审稿与返修）
- 作者对 Euler convention 和 Fig.7 panel 选择的回复

### 7.10 第 4 阶段完成状态（2026-06-02）

**已完成**：第 4 阶段（全文压缩与期刊风格）Claude 侧输出。

输出文件：
```text
论文写作\02_后整合双线修订\Claude交互\Claude输出\04_Claude输出_全文压缩与期刊风格.md
```

内容包括：
- 全文字数估算（当前 ~7930 词）与压缩目标（~6800 词，压缩 ~20%）
- 逐章压缩审计表（Abstract→Introduction→Related Work→Method→Results→Discussion→Conclusion）
- 章节级压缩路线（预计节省 ~1120 词）
- 术语统一表（10 项推荐术语 + 7 项禁用表述）
- 5 段可直接合并的局部替换文本
- 14 项作者确认保护清单（压缩时绝对不能删除的占位和边界声明）

### 7.11 第 5 阶段完成状态（2026-06-02）

**已完成**：第 5 阶段（模拟审稿与返修）Claude 侧输出。

输出文件：
```text
论文写作\02_后整合双线修订\Claude交互\Claude输出\05_Claude输出_模拟审稿与返修.md
```

内容包括：
- Editorial Summary（总体判断：Major revision, addressable without new experiments）
- 三位模拟审稿人报告：
  - Reviewer A（物理建模）：4 major concerns（无真实验证、材料参数无来源、遮挡细节冗长、GGX 公式缺失）
  - Reviewer B（ML 实验）：4 major concerns（角误差公式缺失、ResNet 噪声崩溃解释不足、样本维度比低、TinyCNN vs ResNet 差异未解释）
  - Reviewer C（组织与风格）：4 major concerns（框架重复、引用占位、Discussion 重述数字、Table 1 过宽）
- Consolidated Revision Matrix（15 项，按优先级排序，标注 owner 和是否 v0.2 前完成）
- 7 条 Protected Boundaries
- v0.2 前 10 项 Final Checklist

### 7.12 第 6 阶段完成状态（2026-06-02）

**已完成**：第 6 阶段（投稿材料）Claude 侧输出。

输出文件：
```text
论文写作\02_后整合双线修订\Claude交互\Claude输出\06_Claude输出_投稿材料.md
```

内容包括（严格按指导文件 §2 的 A-F 结构）：
- A. Submission package map：17 项投稿组件总表（Item / Purpose / Required content / Missing info / Owner）
- B. Author fact checklist：6 类作者确认事实（Data/code、Authors、CRediT、Funding、COI、Target journal），标注 Blocking/Deferrable
- C. Supplementary file outline：SM1-7 / Fig.S1-6 / Table S1-4 / SN1-5，逐项标注对应主文位置与承接审稿风险（已对齐第 3 阶段编号）
- D. Cover letter skeleton：10 段骨架 + 5 组 bullet points（contributes / benchmark / evidence / limitations / not-to-claim），用 `[Target Journal]` 占位
- E. Submission-readiness checklist：15 项，分 Must before v0.2 / Must before submission / Optional
- F. Final author questions before v0.2：15 问，整合第 1/3/5 阶段全部 Blocking 确认项
- G. 给 Codex 的交付说明 + H. 本轮自检表

**关键处理**：
1. 全程未生成最终投稿文件，未代填作者/单位/CRediT/资助/COI/数据共享状态。
2. 候选期刊一律按候选处理，未当作已选期刊。
3. 全部红线边界（no-real-validation、clean upper-bound、controlled stress test、`all_raw` semi-oracle、conditional fusion、`r=0.003` TinyCNN/OCS）在投稿材料语境下保留。
4. F 节 15 问已映射回 A01-A10 / Q1-Q11 等来源编号，便于 Codex 去重整合。

### 7.13 仍需作者确认的问题（第 6 阶段汇总）

见输出文件 F 节 Q1-Q15，核心 Blocking 项：
- 方法可复现三项（Euler / encoding / angular error）
- Table 2/4 数值（TinyCNN 版本、kNN Hit@10、OCS-noise 缺值）
- 目标期刊与 article type
- Data/Code Availability、CRediT、COI、Funding 全部投稿声明事实

### 7.14 仍需 Codex 审阅的问题

1. 审阅第 6 阶段 Claude 输出
2. 与 GPT 侧第 6 阶段输出对比整合
3. 生成 `阶段整合输出\06_投稿材料_整合清单.md`
4. 核对 A 节 Owner 分配、C 节 Supplementary 编号一致性、F 节 15 问对 Blocking 项的覆盖完整性

### 7.15 下一轮应读取的文件

- Codex 对第 6 阶段 Claude 输出的审阅意见 / `阶段整合输出\06_投稿材料_整合清单.md`
- 作者对 F 节 Q1-Q15 的统一回复（尤其 Blocking 项）
- 若进入 v0.2 主稿生成阶段：Codex 对 v0.2 修订的指导文件

---

## 8. 禁止事项

0. 禁止编造实验结果、引用文献、方法细节、模型配置、期刊要求或任何作者尚未确认的事实。
1. 不发明实验结果。
2. 不发明引用。
3. 不直接删除研究边界。
4. 不把 clean-image upper bound 写成 field performance。
5. 不把 `all_raw` 写成 operational OCS feature。
6. 不把 `r = 0.003` 写成 ResNet pair 证据。
7. 不写未确认的 Euler convention、target encoding、model architecture 或 0% OCS-noise values。

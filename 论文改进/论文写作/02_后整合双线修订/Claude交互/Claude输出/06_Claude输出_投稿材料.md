# 06 Claude 输出：投稿材料

> 输出日期：2026-06-02
> 阶段：06 投稿材料（后整合双线修订）
> 输入：最终整合版 v0.1、第 1/2/2b/3/5 阶段整合清单、本阶段任务说明与 Claude 指导文件
> 性质：投稿材料准备清单与草案框架。**不是最终投稿文件**，不代填作者事实，不绑定具体期刊格式。
> 交付：本输出交 Codex 审阅，与 GPT 侧第 6 阶段输出对比后整合为 `阶段整合输出/06_投稿材料_整合清单.md`。

## 0. 边界声明（本输出全程遵守）

- 候选期刊（Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing 等）一律按**候选**处理，不当作已选期刊。
- 全程不声称存在 real optical telescope validation；clean rendered images 仅为 idealized upper-bound；Gaussian/brightness/OCS-noise 仅为 controlled stress tests。
- `all_raw` 仅为 semi-oracle diagnostic；fusion 仅为 conditional complementarity；`r = 0.003` 仅为 TinyCNN/OCS diagnostic。
- 一切作者、单位、CRediT 贡献、资助、利益冲突、数据/代码共享状态均标为待作者确认，不代造。

---

## A. Submission package map

> Owner 取值：`Author`（仅作者能提供事实）/ `Codex`（整合与版本线）/ `GPT-Claude`（模型可起草的安全骨架）/ `Submission stage`（投稿定稿阶段处理）。

| Item | Purpose | Required content | Current missing information | Owner |
|---|---|---|---|---|
| Main manuscript v0.2 | 期刊主审稿件 | 清零占位后的正文、Method 可复现要点、定稿 Table 1-4、图注 | 见 F 全部作者确认项；占位未清零前不可生成 | Codex |
| Cover letter | 向编辑陈述贡献与适配性 | 贡献、controlled benchmark 价值、conditional complementarity 证据、limitations、不主张项 | 目标期刊与 article type、作者署名 | GPT-Claude（骨架）+ Author（事实） |
| Highlights / key points | 期刊要求的 3-5 条要点 | 每条 ≤85 字符，覆盖统一前向模型、controlled benchmark、conditional complementarity、no-real-validation 边界 | 是否需要（取决于候选期刊） | GPT-Claude（草案）+ Submission stage |
| Graphical abstract | 部分期刊需要 | 基于 Fig.1 workflow 的单图 | 是否需要、尺寸规范 | Submission stage |
| Supplementary Information | 承接完整结果与可复现细节 | 见 C 节目录 | 缺值/逐 seed/超参数表待作者确认 | Codex + Author |
| High-res figures | 投稿图件 | Fig.1-7 矢量/300dpi，英文标签 | Fig.2 坐标轴、Fig.3 几何选择、Fig.6 缺值（见 F） | Submission stage |
| Tables (source) | 可编辑表格源 | Table 1-4 定稿数值 | TinyCNN 版本、kNN Hit@10、OCS-noise 缺值 | Author + Codex |
| References / bib | 参考文献 | 已核验 `references.bib`，清零 `[CITATION]`/`[to verify]` | 5 处 Introduction `[CITATION]` 实体、地基光学退化文献缺口 | Author + Codex |
| Data Availability statement | 数据共享声明 | 模板 + 实际共享状态 | 仿真数据/STL 衍生品/模型/脚本能否共享、仓库或申请方式 | Author |
| Code Availability statement | 代码共享声明 | 区分 scripts / trained models / rendering code / data-processing code 状态 | 各类代码能否公开、许可证、仓库地址 | Author |
| Author Contributions (CRediT) | 贡献声明 | CRediT 角色分配 | 作者列表与各自角色 | Author |
| Conflict of Interest | 利益冲突声明 | 期刊要求措辞 | 是否存在竞争利益、目标期刊措辞 | Author |
| Funding statement | 资助声明 | 资助机构与项目号 | 项目号、资助方、是否无资助 | Author |
| Acknowledgements | 致谢 | 致谢对象 | 非作者贡献者、机构、算力支持 | Author |
| Author info / ORCID / affiliations | 投稿系统元数据 | 姓名、单位、邮箱、ORCID、通讯作者 | 全部待作者提供 | Author |
| Ethics / declarations | 期刊声明 | AI 使用声明、伦理（本研究多为 N/A） | 期刊具体要求、是否需 AI-tool 声明 | Author + Submission stage |
| Suggested / opposed reviewers | 部分期刊要求 | 候选审稿人名单 | 是否需要、具体人选 | Author |
---

## B. Author fact checklist

> 以下全部为**只有作者能确认的事实**。模型不代填。每项标注是否为投稿硬阻塞（Blocking）或可后补（Deferrable）。

### B.1 Data and code

| # | 待确认事实 | 类型 | 备注 |
|---|---|---|---|
| D1 | 仿真 OCS 数据集（多几何扫描产物）是否可公开共享 | Blocking | 决定 Data Availability 措辞 |
| D2 | STL 几何衍生品（faceted 模型、材料标签）能否共享，是否有第三方/保密限制 | Blocking | 真实卫星 STL 可能涉及来源限制 |
| D3 | 渲染图像数据集（phase63 clean images）能否共享 | Blocking | 体量大，可能需仓库/按需 |
| D4 | 训练好的模型权重（OCS MLP / TinyCNN / ResNet-18 / fusion）能否共享 | Deferrable | 可写 available on request |
| D5 | 代码共享范围：simulation scripts / rendering code / data-processing / inversion training，各自能否公开 | Blocking | Code Availability 需逐类说明 |
| D6 | 代码/数据许可证（如 MIT / CC-BY / 内部） | Deferrable | 公开时需指定 |
| D7 | 是否提供公开仓库地址或 DOI（Zenodo/GitHub），还是 on-request | Blocking | Data/Code 声明二选一路径 |
| D8 | 第三方依赖与版本（Blender 4.2.3、PyTorch 2.8.0+cu128 等）是否在可复现声明中列出 | Deferrable | 进 Supplementary Table S1 |

### B.2 Authors and affiliations

| # | 待确认事实 | 类型 |
|---|---|---|
| AU1 | 最终作者列表与署名顺序 | Blocking |
| AU2 | 各作者单位、地址、邮箱 | Blocking |
| AU3 | 通讯作者及其联系方式 | Blocking |
| AU4 | 各作者 ORCID | Deferrable |
| AU5 | 是否有共同一作 / 共同通讯标注 | Deferrable |

### B.3 CRediT contributions

> 只给角色框架，不分配到具体人。作者需将每个角色映射到署名作者。

| CRediT 角色 | 本研究对应工作（供作者勾选分配） |
|---|---|
| Conceptualization | OCS-图像统一前向建模与 controlled benchmark 设计思路 |
| Methodology | BRDF/遮挡模型、姿态参数化、反演模型与融合策略设计 |
| Software | 仿真/渲染/反演代码实现 |
| Validation | 单平板/立方体闭合、自遮挡 sanity checks |
| Formal analysis | 消融、敏感性、互补性诊断 |
| Investigation | 扫描与训练实验执行 |
| Data curation | 数据集组织与对齐 |
| Writing - original draft | 初稿撰写 |
| Writing - review & editing | 修订与定稿 |
| Visualization | 图表制作 |
| Supervision | 指导 |
| Project administration | 项目管理 |
| Funding acquisition | 资助申请 |

待确认：以上角色与署名作者的对应关系（Blocking）。

### B.4 Funding and acknowledgements

| # | 待确认事实 | 类型 |
|---|---|---|
| F1 | 资助机构名称 | Blocking（若有资助） |
| F2 | 项目/基金编号 | Blocking（若有资助） |
| F3 | 若无资助，是否写 "received no specific grant" | Blocking |
| F4 | 致谢对象：非作者贡献者、算力/设备支持、机构 | Deferrable |
| F5 | 是否致谢特定数据/模型提供方（涉及 STL 来源） | Deferrable |

### B.5 Conflict of interest

| # | 待确认事实 | 类型 |
|---|---|---|
| COI1 | 是否存在竞争性利益（财务/非财务） | Blocking |
| COI2 | 目标期刊要求的具体 COI 措辞模板 | Submission stage |

### B.6 Target journal and article type

| # | 待确认事实 | 类型 |
|---|---|---|
| J1 | 最终目标期刊（候选：Acta Astronautica / ASR / Optics Express / Remote Sensing / 其他） | Blocking |
| J2 | Article type（Research Article / Full-length / Technical Note） | Blocking |
| J3 | 是否需要 Highlights、Graphical Abstract | Deferrable |
| J4 | 主文图表数量上限、字数上限、参考文献格式 | Submission stage |
| J5 | 是否要求 AI-tool 使用声明 | Submission stage |

---

## C. Supplementary file outline

> 设计依据：第 3 阶段 Supplementary 图表建议（Fig.S1-S6 + Table S1-S4）与第 5 阶段 Supplementary 承接内容。每项标注**对应主文位置**和**承接的审稿风险**。占位/缺值待作者确认前不得在 Supplementary 中写死。

### S1. Supplementary Methods

| 编号 | 内容 | 对应主文位置 | 承接的审稿风险 |
|---|---|---|---|
| SM1 | 完整姿态定义：Euler order / rotation-matrix convention、yaw/pitch/roll 轴、固定 roll 说明 | §3.2 | MC1 方法可复现性（A01 确认后填） |
| SM2 | Target encoding 完整说明（sin/cos 编码、解码、是否全模型统一） | §3.8 | MC1（A02 确认后填） |
| SM3 | Angular error formula 完整推导（yaw 周期处理、pitch 几何） | §3.9 | MC1（A03 确认后填） |
| SM4 | 数据生成协议：5 观测几何定义、phase-angle 范围、phase63 含义、网格点数（563 train / 1998 test / 2701 total） | §3.3 | MC4 跨 phase 误读 |
| SM5 | 自遮挡验证细节：epsilon / min_hit_distance 选择、单/双平板、U-block、嵌套圆柱、Blender 人工抽查 | §3.5、§4.1 | 物理建模可复现性 |
| SM6 | OCS 积分与特征构造：total / per_part / log 变换、`all_raw` 组成与 semi-oracle 定性 | §3.6 | MC6 `all_raw` 误读 |
| SM7 | 训练配置：epochs、batch、lr、optimizer、early stopping、seeds、硬件 | §3.8、§3.9 | MC1、可复现性 |

### S2. Supplementary Figures

| 编号 | 内容 | 对应主文位置 | 承接的审稿风险 |
|---|---|---|---|
| Fig. S1 | 完整 5 几何 OCS maps / occlusion maps | 主文 Fig. 3 | Fig.3 仅放代表性 panel |
| Fig. S2 | BRDF sensitivity 完整参数与部件图 | 主文 Fig. 7 / Discussion | MC8 ablation 占位 |
| Fig. S3 | Roll sensitivity 完整结果 | Limitations §5.6 | 支撑 fixed-roll 边界 |
| Fig. S4 | Phase63 fairness / phase-condition ablation | §3.3、§4.6 | MC4 跨 phase 误读 |
| Fig. S5 | Random split 完整结果 | §4.6 | split 难度与稳健性 |
| Fig. S6 | TinyCNN/OCS diagnostic 互补性，含 `r = 0.003` | §4.4 | MC + 防止误读为 ResNet-pair 证据 |

### S3. Supplementary Tables

| 编号 | 内容 | 对应主文位置 | 承接的审稿风险 |
|---|---|---|---|
| Table S1 | 模型超参数汇总（OCS MLP / TinyCNN / ResNet-18 / fusion） | §3.8 | MC1 可复现性 |
| Table S2 | 逐 seed 结果 | Table 2/3/4 | 支撑 mean ± std |
| Table S3 | 完整 image degradation + OCS-noise stress-test 表（含 1%/5% 中间档） | 主文 Table 4 | MC7、Table 4 压缩 |
| Table S4 | Table 1 扩展版（完整字段） | 主文 Table 1 | MC2/MC9 Table 1 过宽 |

### S4. Supplementary Notes

| 编号 | 内容 | 对应主文位置 | 承接的审稿风险 |
|---|---|---|---|
| SN1 | Controlled stress test 的范围界定：Gaussian noise / brightness / OCS-noise 不等于完整 atmosphere/sensor/telescope 模型 | §4.5、§5.2 | MC3/MC7 误读为 field degradation |
| SN2 | `all_raw` 为 semi-oracle diagnostic 的完整说明与为何不进 operational 结论 | §3.6、§4.2 | MC6 |
| SN3 | Clean-image upper-bound 与 field performance 的区分说明 | §4.3、§5.2 | MC3 |
| SN4 | Fusion 为 conditional complementarity 的完整论证（含失败案例：少数灾难性融合） | §4.4、§5.4 | MC5 universal superiority 误读 |
| SN5 | Forward-model sanity checks ≠ real optical validation 的明确声明 | §4.1 | MC3 |

---

## D. Cover letter skeleton

> 只给安全骨架与 bullet points，**不写最终信件**，不绑定具体期刊名（用 `[Target Journal]` 占位）。措辞不夸大、不主张真实验证。

### D.1 结构骨架

```text
[Date]
[Editor name / Editorial Office], [Target Journal]

Subject: Submission of "BRDF-Driven Optical Cross Section and Photometric Image
Simulation for Space Object Attitude Inversion: A Controlled Benchmark Study"

1. Opening: what we submit and article type
2. What the manuscript contributes
3. Why a controlled benchmark is useful
4. What evidence supports conditional complementarity
5. What limitations are acknowledged
6. What we explicitly do not claim
7. Fit to journal scope (after J1 confirmed)
8. Declarations: originality, not under concurrent review, all authors approved
9. Suggested reviewers (if required)
10. Corresponding author contact
```

### D.2 What the manuscript contributes（bullet points）

- 提出统一 BRDF 驱动前向模型：从同一 STL 几何、非均匀材料、GGX/Cook-Torrance 反射、yaw-pitch 姿态定义、观测几何与自遮挡，**成对**生成 OCS 标量信号与 clean photometric images。
- 在共享前向假设下，建立 OCS-only / image-only / late-fusion / feature-fusion 的 controlled 姿态反演 benchmark。
- 将 clean-image upper-bound 与 degraded-observation robustness **显式分离**。
- 把 OCS-image fusion 刻画为 conditional complementarity。

### D.3 Why a controlled benchmark is useful（bullet points）

- 现有研究常在不一致的前向假设下比较 light-curve、image-based pose、fusion，难以判断模态究竟互补还是冗余。
- 同一前向模型生成两种模态，使精度差异可归因于模态信息而非仿真假设差异。
- 在 ideal 与 controlled-degraded 两种条件下评估，为后续真实观测验证提供受控参照。

### D.4 What evidence supports conditional complementarity（bullet points，仅引用主稿已有数值）

- Clean ResNet-18 image-only：mean 1.69° ±0.07，Hit@5 97.6%（idealized upper-bound，非 field performance）。
- 加入 practical `per_part_log` OCS 后：mean 降至 1.47°，worst-case 由 9.9° 降至 6.6°（selected tail improvement）。
- 更强的 semi-oracle `all_raw` OCS 反而 worst-case 升至 18.7° —— 说明更强 OCS 不自动改善 tail。
- OCS-noise 加重时 fusion gain 上升（+1.97° → +3.30° → +6.29°，0/10/20%）—— fusion 价值取决于模态质量与失效模式差异。

### D.5 What limitations are acknowledged（bullet points）

- 无 real optical telescope validation。
- clean rendered images 不含 atmosphere / detector / PSF / earthshine / background / tracking。
- 仅 yaw-pitch（fixed roll），主图像分支仅 phase63 single condition。
- 材料参数为 engineering nominal，非 target-calibrated。
- Gaussian / brightness / OCS-noise 为 controlled stress tests，非完整观测链模型。

### D.6 What not to claim（红线，写信时禁止越界）

- 不写 real-world / field / operational performance。
- 不写 fusion universally superior 或 guaranteed robust。
- 不把 `all_raw` 写成 operational feature。
- 不把 `r = 0.003` 写成 ResNet-pair evidence。
- 不把 sanity checks 写成 real optical validation。
- 不把候选期刊写成已接收/已选定。

---

## E. Submission-readiness checklist

> 标注：`Must before v0.2`（进入主稿修订前必须）/ `Must before submission`（投稿前必须）/ `Optional`。≤15 项。

| # | 检查项 | 等级 |
|---|---|---|
| 1 | Euler convention / target encoding / angular error formula 作者确认并写入 Method | Must before v0.2 |
| 2 | 全部 `[CITATION]` 与 `[to verify]` 删除或替换为已核验引用 | Must before v0.2 |
| 3 | Table 2 TinyCNN 版本、Weighted kNN Hit@10 处理（确认或删行/删列） | Must before v0.2 |
| 4 | Table 4 OCS-noise 0% mean/std 与 10%/20% Hit@5 缺值填入或明确处理 | Must before v0.2 |
| 5 | `all_raw` semi-oracle、`r=0.003` TinyCNN/OCS、clean upper-bound、conditional fusion 边界在正文/表/图注全一致 | Must before v0.2 |
| 6 | no-real-telescope-validation 在 Abstract/Method/Discussion/Conclusion/Limitations 显性保留 | Must before v0.2 |
| 7 | Method 含可复现要点：姿态定义、encoding、metrics、split（563/1998/2701）、features、训练配置 | Must before v0.2 |
| 8 | Fig. 7 ablation 主文/补充材料分配确认 | Must before v0.2 |
| 9 | Data Availability / Code Availability 声明按作者事实填写 | Must before submission |
| 10 | Author Contributions（CRediT）/ COI / Funding / Acknowledgements 填写 | Must before submission |
| 11 | 作者列表、单位、通讯作者、ORCID 完整 | Must before submission |
| 12 | Fig.1-7 导出为期刊规范（矢量/300dpi、英文标签），caption 替换 caption-intent | Must before submission |
| 13 | Supplementary 文件（SM/Fig.S/Table S/SN）组装并与主文交叉引用 | Must before submission |
| 14 | 目标期刊 article type、字数、图表数、参考文献格式核对 | Must before submission |
| 15 | Highlights / Graphical Abstract / Suggested reviewers / AI-tool 声明（视期刊要求） | Optional |

---

## F. Final author questions before v0.2

> 将第 1/3/5 阶段确认项整合为 15 个问题。建议在生成 v0.2 主稿前一次性向作者提问。每项标注来源阶段与影响范围。

| # | 问题 | 来源 | 影响 |
|---|---|---|---|
| Q1 | Euler convention 是否采用项目记录的 `R = Rz @ Ry @ Rx`（Z-Y-X 内旋）？yaw/pitch/roll 轴与 Fig.2 坐标如何标注？ | A01/Q1 | Method §3.2、Fig.2 |
| Q2 | Target encoding 是否所有 MLP/CNN/fusion 统一 `[sin(yaw),cos(yaw),sin(pitch),cos(pitch)]`？有无例外？ | A02/Q2 | Method §3.8 |
| Q3 | Angular error formula 最终定义？yaw 周期与 pitch 几何如何处理？ | A03/Q3 | §3.9、全部指标 |
| Q4 | TinyCNN 正文采用 `12.38±0.74` 还是 `11.87±0.69`？对应 Hit@5/Hit@10 哪组进正文？ | A07/Q4 | Table 2、§4.3/4.4 |
| Q5 | Weighted kNN `all_raw` Hit@10 是否有可靠日志？无则删 Hit@10 列或删该行？ | A06/Q5 | Table 2 |
| Q6 | Table 4 OCS-noise 0% mean/std 与 10%/20% Hit@5 缺值是否采用补充实验候选值？是否展示 1%/5% 中间档？ | A04/A05/Q6 | Fig.6、Table 4 |
| Q7 | Fig. 7 哪些 ablation 进主文（BRDF / self-occlusion / roll / phase63 fairness / random split）？哪些进 Supplementary？ | A08/Q7 | §4.6、图表数量 |
| Q8 | Table 1 保留主文压缩版还是完整移 Supplementary？Wang/Burton/Kumar/Fankhauser 技术字段是否已 PDF 全文核对？ | Q8 | Related Work、Table 1 |
| Q9 | 材料参数来源如何写：有可引用范围，还是明确为 engineering nominal + sensitivity 防御？ | A09/Q9 | Method §3.4、Limitations |
| Q10 | 5 处 Introduction `[CITATION]` 用哪些已核验文献替换？地基光学退化文献缺口如何补（不得发明）？ | C01-C05 | Introduction、References |
| Q11 | 目标期刊与 article type（候选：Acta Astronautica / ASR / Optics Express / Remote Sensing / 其他）？ | J1/J2 | 全文风格、图表与字数 |
| Q12 | Data / Code Availability：仿真数据、STL 衍生品、训练模型、各类脚本能否共享？仓库 or on-request？许可证？ | A10/Q10 | Data/Code 声明 |
| Q13 | Author Contributions（CRediT 角色到人）、COI、Funding（项目号/机构或"无资助"）、Acknowledgements？ | A10/Q11 | 投稿声明 |
| Q14 | 是否存在 ResNet-fusion image-degradation 结果？若无，是否同意保留为 future work 而不进 Results？ | 主稿确认项 8 | §4.5、Fig.5 |
| Q15 | Limitations 保留为 Discussion §5.6 还是独立成节（视目标期刊）？ | 主稿确认项 13 | 结构 |

---

## G. 交付说明（给 Codex）

1. 本输出为 Claude 侧第 6 阶段（投稿材料）准备清单，未生成最终投稿文件，未代填任何作者事实。
2. 建议 Codex 与 GPT 侧第 6 阶段输出对比后整合为 `阶段整合输出/06_投稿材料_整合清单.md`。
3. 整合时请重点核对：
   - A 节 Owner 分配是否与双线总览一致。
   - C 节 Supplementary 目录是否与第 3 阶段 Fig.S/Table S 编号一致（本输出已对齐 S1-S6 / Table S1-S4）。
   - F 节 15 问是否覆盖第 1/3/5 阶段全部 Blocking 确认项无遗漏。
4. 本输出不进入主稿版本线，需经 Codex 审阅整合后方可影响 v0.2。

## H. 本轮自检

| 自检项 | 结果 |
|---|---|
| 是否生成最终投稿文件？ | 否，仅清单与骨架 |
| 是否代填作者/单位/贡献/资助/COI/数据共享状态？ | 否，全部标为待作者确认 |
| 是否把候选期刊当已选期刊？ | 否，全程 `[Target Journal]`/候选 |
| 是否声称 real optical telescope validation？ | 否 |
| 是否把 clean images 写成 field performance？ | 否 |
| 是否把 controlled stress tests 写成完整观测链模型？ | 否 |
| 是否把 `all_raw` 写成 operational feature？ | 否，semi-oracle |
| 是否把 fusion 写成 universal superiority？ | 否，conditional |
| 是否删除 v0.2 最低通过线阻塞项？ | 否，全部保留并纳入 E/F |


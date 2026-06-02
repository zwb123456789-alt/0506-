# 06 GPT 输出：投稿材料

> 生成日期：2026-06-02  
> 输入依据：第 6 阶段 GPT 提示词、`00_GPT后整合总览.md`、`00_后整合双线总览.md`、第 1-5 阶段整合清单、最终整合版 v0.1、论文写作完整规划、补充实验进度。  
> 输出性质：投稿材料准备清单和草案框架，仅供 Codex 审阅整合。未生成最终投稿文件，未修改主稿。  
> 红线：不代填作者、单位、贡献、资助、利益冲突、数据共享状态或目标期刊要求。

## A. 投稿材料组件总表

| 组件 | 当前状态 | 缺口 | 作者需确认 | Codex 后续可处理 |
|---|---|---|---|---|
| Manuscript v0.2 | 当前只有 v0.1 author-audit draft；第 1-5 阶段已有修订依据 | 仍有 `[CITATION]`、`[to verify]`、`[需要作者确认]`；Method、Tables、References 未定稿 | v0.2 前统一回答方法、数值、图表、声明问题 | 按整合清单生成 v0.2，清理占位，保留红线边界 |
| Figures | 第 3 阶段已规划 Fig. 1-7；Fig. 1-6 为主文核心候选 | 未实际绘图；Fig. 2 坐标和 Fig. 6 缺值待确认；Fig. 7 是否入主文未定 | Euler/axes/material labels；OCS-noise values；Fig. 7 panels | 核查本地结果文件，绘制主文图和 Supplementary 图 |
| Tables | Table 1-4 已规划压缩方向 | Table 1 技术字段未全文核实；Table 2 TinyCNN/kNN 未定；Table 4 缺值 | Table 1 主文/补充材料；TinyCNN version；Weighted kNN Hit@10；OCS-noise values | 压缩主文表，完整表放 Supplementary |
| Supplementary | 第 3/5 阶段已有建议清单 | 尚未形成目录、编号、文件结构和源数据映射 | 哪些 ablations 进主文；哪些完整结果进 Supplementary | 建立 Supplementary Figures/Tables/Methods/Notes 框架 |
| References / BibTeX | `references.bib` 已修正主要错误；key 暂未重命名 | 主稿仍有旧占位；地基光学退化文献缺口；Table 1 技术字段需 PDF/full-text | 是否补充目标期刊或领域关键文献；是否统一 BibTeX key | 替换引用、清理参考文献列表、生成投稿格式 |
| Data Availability | v0.1 只有占位 | 未确定数据、代码、模型、STL-derived products 的共享范围和仓库 | 数据能否公开；是否有第三方/模型/STL 限制；仓库或访问方式 | 根据作者回答生成 Data Availability statement |
| Code Availability | 尚未单独声明 | scripts、rendering code、training code、trained models、environment 是否共享未定 | 哪些代码可公开；是否提供运行环境、版本、依赖和许可证 | 形成 Code Availability statement 和 README 清单 |
| Author Contributions | v0.1 只有占位 | 作者列表、单位、顺序、CRediT roles 未定 | 全部作者姓名、单位、通讯作者、贡献角色 | 按 CRediT 框架整理声明，不代造贡献 |
| Conflict of Interest | v0.1 暂写无冲突但仍需确认 | 最终措辞需按目标期刊和作者实际情况 | 是否存在任何 competing interests；目标期刊要求措辞 | 根据确认结果改成期刊适配文本 |
| Funding / Acknowledgements | v0.1 未写 | 资助机构、项目号、计算资源、数据/模型来源、致谢对象未定 | funder name、grant numbers、设备/计算支持、致谢对象 | 整理 Funding 和 Acknowledgements 草案 |
| Cover Letter | 未生成 | 目标期刊未定，不能按具体格式写最终信 | 目标期刊、文章类型、通讯作者信息、推荐/回避审稿人（如需） | 生成保守 cover letter draft 和亮点要点 |
| Submission checklist | 尚未形成最终清单 | 需要覆盖主稿、图表、补充材料、数据/代码、声明、引用、格式 | 目标期刊格式、文件类型、图像分辨率要求 | 生成投稿前检查表并逐项核验 |

## B. Data / Code / Author / COI 作者确认问题

### Data Availability

1. simulation raw data 是否可公开，包括 OCS maps、rendered photometric images、train/val/test splits、noise robustness outputs、ablation outputs？
2. STL 原始模型或 STL-derived component products 是否可公开？如果不能公开，限制来自第三方、保密、版权还是其他原因？
3. figure source data 是否可以随 Supplementary 或 repository 提供？
4. processed tables、summary CSV/JSON、seed-level results 是否可以公开？
5. 是否已有计划仓库、机构库、Zenodo/OSF/figshare/GitHub release 或校内 repository？是否需要 DOI？
6. 若不能公开，是否可提供 metadata、representative samples 或 reasonable request access？请求由谁审核？

### Code Availability

1. OCS/BRDF/self-occlusion simulation scripts 是否可公开？
2. rendering scripts、data preprocessing scripts、training/evaluation scripts 是否可公开？
3. trained ResNet / MLP / fusion model weights 是否可共享？
4. 是否提供 environment 文件，例如 Python version、PyTorch version、CUDA/GPU 信息、requirements 或 conda YAML？
5. 是否需要开源许可证？若需要，作者倾向 MIT、BSD、Apache-2.0、GPL，还是暂不确定？

### Author / Contributions

1. 最终作者列表、作者顺序、单位、通讯作者和邮箱是什么？
2. 每位作者的 CRediT roles 是什么：Conceptualization、Methodology、Software、Validation、Formal analysis、Investigation、Resources、Data curation、Writing-original draft、Writing-review and editing、Visualization、Supervision、Project administration、Funding acquisition？
3. 是否有共同一作、共同通讯或单位变更说明？

### COI / Funding / Acknowledgements

1. 是否存在 competing interests、专利、软件商业化、单位或资助方利益相关？
2. 资助机构、项目号、基金名称、计算资源支持和设备支持如何写？
3. 是否需要致谢导师、实验室、数据/模型提供者、计算平台或审稿前内部审阅者？

## C. Supplementary 结构建议

### Supplementary Figures

| 编号 | 建议内容 | 对应主文 | 放入 Supplementary 的原因 |
|---|---|---|---|
| Fig. S1 | 完整 5 geometries OCS maps / occlusion maps | Fig. 3、Results 4.1 | 主文只放代表性 OCS/occlusion diagnostics，完整几何避免主文过长 |
| Fig. S2 | BRDF sensitivity 完整参数与部件图 | Fig. 7、Limitations | 支撑 nominal material boundary，主文只保留摘要或关键 panel |
| Fig. S3 | Roll sensitivity 完整结果 | Limitations、Fig. 7 | 支撑 fixed-roll limitation，不把本文写成 full 3-DOF |
| Fig. S4 | Phase63 fairness / phase-condition ablation | Method 3.3、Results 4.6 | 回应 image branch single-phase 风险，主文只需一句或一个 panel |
| Fig. S5 | Random split 完整结果 | Results 4.6 | 说明 10 deg -> 5 deg split 更严格，避免主文堆叠 |
| Fig. S6 | TinyCNN/OCS diagnostic complementarity including `r = 0.003` | Results 4.4 | 防止被误读为 ResNet-pair evidence，作为 diagnostic note 更安全 |

### Supplementary Tables

| 编号 | 建议内容 | 对应主文 | 放入 Supplementary 的原因 |
|---|---|---|---|
| Table S1 | 模型超参数、training settings、seeds、input sizes、target encoding | Method 3.8-3.9 | 增强可复现性，避免 Method 过长 |
| Table S2 | 逐 seed 结果 | Results 4.2-4.5 | 支撑 mean +/- std 和统计稳定性 |
| Table S3 | 完整 image degradation / OCS-noise stress-test table | Table 4、Fig. 5-6 | 主文 Table 4 需压缩，完整 0/1/5/10/20% 结果放补充 |
| Table S4 | Table 1 扩展版 | Related Work Table 1 | 主文只做 scope comparison，扩展字段供审稿人核查 |
| Table S5 | Dataset split and sample counts | Method 3.9 | 记录 563 train attitudes、1998 test attitudes 等 split 信息 |
| Table S6 | BRDF / material nominal parameters and sensitivity settings | Method 3.4、Limitations | 材料参数来源和 nominal boundary 需要透明 |

### Supplementary Methods

| 小节 | 建议内容 | 对应主文 | 原因 |
|---|---|---|---|
| SM1 | STL preprocessing and component labeling | Method 3.2 | 主文保留概要，补充材料给可复现细节 |
| SM2 | GGX/Cook-Torrance implementation and nominal material settings | Method 3.4 | 避免主文过长，同时支撑 BRDF credibility |
| SM3 | Self-occlusion and visibility sanity checks | Method 3.5、Results 4.1 | 完整 single-plate / double-plate / U-block / nested-cylinder 等检查放补充 |
| SM4 | OCS feature construction and `all_raw` diagnostic definition | Method 3.6 | 明确 `all_raw` semi-oracle 边界 |
| SM5 | Image generation, normalization and dataset audit | Method 3.7、Results 4.3 | 支撑 ResNet clean upper-bound 和无显性泄漏审计 |
| SM6 | Training protocol and metrics | Method 3.8-3.9 | 放 target encoding、angular error、seeds、hardware/software 细节 |

### Supplementary Notes

| 编号 | 建议内容 | 对应主文 | 原因 |
|---|---|---|---|
| Note S1 | Why clean rendered images are upper-bound, not field performance | Abstract、Discussion | 防止审稿误读 |
| Note S2 | Controlled stress tests versus full observation-chain modeling | Fig. 5-6、Limitations | 明确 Gaussian noise / brightness / OCS-noise 边界 |
| Note S3 | Conditional complementarity and why fusion is not universal superiority | Results 4.4、Discussion | 解释 mean gain 小但 tail improvement 有意义 |
| Note S4 | Fixed-roll and phase63 boundaries | Method、Limitations | 统一后续 response 口径 |

## D. Cover Letter 安全要点

### 可写入 Cover Letter 的保守要点

1. The manuscript presents a controlled simulation benchmark for yaw-pitch attitude inversion of a non-cooperative space object using paired OCS signatures and clean rendered photometric images.
2. Both modalities are generated under shared BRDF, geometry, attitude, observation-geometry and visibility assumptions, enabling a controlled comparison of scalar and image-based optical cues.
3. The study separates clean-image upper-bound performance from degraded-observation sensitivity rather than treating clean rendered images as field performance.
4. The results show that high-capacity image models can be highly accurate under clean rendered images, while controlled image degradation can substantially reduce image-only performance.
5. Practical component-level OCS features provide an interpretable scalar photometric constraint within the benchmark.
6. OCS-image fusion is framed as conditional complementarity, especially through selected tail-error reduction and modality-dependent failure modes.
7. The manuscript explicitly states that real optical telescope validation, calibrated material measurements and full atmosphere/sensor modeling remain outside the present study and are required before operational field-performance claims.
8. The paper may be positioned as a methods/benchmark study for optical space-object characterization and attitude inversion, not as an operational deployment report.

### Cover Letter 禁用表述

1. 不写 `first`, `state-of-the-art`, `breakthrough`, `validated in real observations`，除非后续有独立证据。
2. 不写 `robust field performance`、`operationally validated`、`ready for deployment`。
3. 不写 clean rendered images 代表 real telescope images。
4. 不写 controlled Gaussian noise / brightness scaling / OCS-noise 是完整 atmosphere/sensor model。
5. 不写 fusion is universally superior 或 always improves performance。
6. 不写 `all_raw` 是 operational OCS feature。
7. 不写 `r = 0.003` 是 ResNet-pair 证据。
8. 不绑定具体期刊格式或编辑偏好，除非作者已明确目标期刊。

## E. 投稿前 checklist

1. 主稿中所有 `[CITATION]`、`[to verify]`、`[需要作者确认]` 已处理或有明确删除决策。
2. Euler convention、target encoding、angular error formula、Hit@5/Hit@10 定义已写入 Method。
3. TinyCNN version、Weighted kNN Hit@10、OCS-noise missing values 已统一。
4. Table 1 已降为 scope comparison；未核实技术字段不硬填。
5. Table 2 / Table 4 无缺值或未解释占位。
6. Fig. 1-6 主文图和 caption 已定稿；Fig. 7 是否主文保留已决定。
7. Supplementary Figures / Tables / Methods / Notes 已编号并与主文引用一致。
8. 所有图表 caption 保留 controlled benchmark、clean-image upper-bound、semi-oracle `all_raw`、controlled stress test 和 no-real-validation 边界。
9. References 与修订后的 `references.bib` 一致；旧 Yang 2024、Hanada、Liu 等错误写法已清除。
10. Data Availability 和 Code Availability 已根据真实共享状态完成。
11. Author Contributions、COI、Funding、Acknowledgements 已由作者确认。
12. Abstract、Conclusion、Cover Letter 未使用 field performance、universal fusion superiority、operational validation 等越界表述。
13. Supplementary 中包含超参数、逐 seed、完整噪声/退化、ablation、扩展 Table 1 或说明其不提供的原因。
14. 目标期刊的格式、图像分辨率、参考文献样式、字数/图表限制已由 Codex 或作者单独核对。
15. v0.2 完成后再进入最终投稿材料生成，不以 v0.1 直接投稿。

## F. v0.2 前统一提问清单

以下问题建议一次性发给作者，控制在 15 项以内：

1. Euler convention 是否采用 `R = Rz @ Ry @ Rx`、Z-Y-X 内旋？yaw / pitch / roll 轴向和 Fig. 2 坐标如何标注？
2. 所有 MLP/CNN/fusion 模型是否统一使用 `[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]` target encoding？
3. angular error formula 如何最终定义？yaw 周期和 pitch 几何如何处理？
4. TinyCNN 主结果采用 `12.38 +/- 0.74` 还是 `11.87 +/- 0.69`？对应 Hit@5/Hit@10 采用哪组？
5. Weighted kNN `all_raw` Hit@10 是否有可靠日志？若无，是否删除 Hit@10 列或 Weighted kNN 行？
6. OCS-noise 0%、10%、20% 缺值是否采用补充实验候选值？是否展示 1%/5% intermediate levels？
7. Fig. 7 是否进入主文？若进入，选择 BRDF sensitivity、self-occlusion、roll sensitivity、phase63 fairness、random split 中哪些 panels？
8. Table 1 是否保留主文压缩版？Wang / Burton / Kumar / Fankhauser 技术字段是否已做 PDF/full-text 核对？
9. 材料参数来源如何写：有无可引用来源，还是明确写 engineering nominal / nominal material settings？
10. simulation data、OCS maps、rendered images、split files、summary tables、figure source data 是否可公开？
11. STL 原始模型或 STL-derived component products 是否可共享？若不能，限制原因是什么？
12. simulation/rendering/training/evaluation code、trained models 和 environment 文件是否可公开？采用什么许可证或访问方式？
13. 最终作者列表、单位、通讯作者和 CRediT roles 是什么？
14. Funding / Acknowledgements 如何写？包括资助机构、项目号、计算资源和致谢对象。
15. Conflict of Interest 最终声明是什么？是否存在任何 competing interests 或需要披露的关系？

## G. 可选投稿材料草案骨架

以下只是骨架，不是最终文件。

### Data Availability skeleton

> Data supporting the findings of this study include [待作者确认：raw simulated OCS data / rendered photometric images / processed feature tables / train-test split files / figure source data]. These data are [待作者确认：publicly available at repository and DOI / available from the corresponding author upon justified request because ... / not publicly available because ...]. The satellite geometry files and STL-derived products are [待作者确认：available / restricted / replaced by derived metadata]. Source data for the main figures and tables are [待作者确认：provided with the Supplementary Information / deposited in ...].

### Code Availability skeleton

> The code used for BRDF-driven simulation, self-occlusion analysis, rendering, model training and evaluation is [待作者确认：available at repository and DOI / available upon request / restricted because ...]. The software environment used for the reported experiments includes [待作者确认：Python version, PyTorch version, CUDA/GPU information and dependency file].

### Author Contributions skeleton

> [Author initials] contributed to Conceptualization. [Author initials] contributed to Methodology, Software and Validation. [Author initials] contributed to Formal analysis and Visualization. [Author initials] wrote the original draft. [Author initials] reviewed and edited the manuscript. [Author initials] supervised the project and acquired funding.  
> `[待作者确认：final author list, initials and CRediT roles]`

### Conflict of Interest skeleton

> The authors declare [待作者确认：no competing interests / the following competing interests: ...].

### Cover Letter skeleton points

> We submit a manuscript describing a controlled simulation benchmark for BRDF-driven OCS and photometric image attitude inversion of a space object. The study generates scalar OCS signatures and clean rendered photometric images under shared geometry, BRDF, observation-geometry and visibility assumptions. The manuscript distinguishes clean-image upper-bound performance from controlled degradation stress tests and frames OCS-image fusion as conditional complementarity rather than universal superiority. The work does not claim real optical telescope validation or operational field performance; instead, it identifies the validation steps required for future field use.

## H. 不应由模型代填的内容

1. 作者姓名、单位、顺序、通讯作者和邮箱。
2. CRediT roles 的具体归属。
3. 资助机构、项目号、致谢对象。
4. COI / competing interests 的最终声明。
5. 数据、代码、模型、STL 或衍生文件是否可公开。
6. repository、DOI、accession number、license、embargo 或 access committee。
7. 目标期刊格式、图像分辨率、cover letter 格式和投稿系统要求。
8. 未核验引用或未完成实验结果。

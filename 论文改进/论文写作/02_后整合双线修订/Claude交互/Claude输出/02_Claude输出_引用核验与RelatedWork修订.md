# Claude 输出：引用核验与 Related Work 修订

> 生成日期：2026-06-01  
> 基于：最终整合版 v0.1 + references.bib + 论文必读文献阅读清单.md  
> 审计范围：全部 [CITATION] 占位、全部 [to verify]、Table 1 逐字段  
> 输出目的：供 Codex 审阅整合为 v0.2 引用修订依据

---

## 1. Introduction 的 5 个 [CITATION] 核验

| ID | 占位 | 建议替换文献 | .bib key | 核验状态 | 证据来源 | 风险 | 建议处理 |
|---|---|---|---|---|---|---|---|
| C01 | `[CITATION: optical space object characterization]` | Li et al. 2024《空间目标光学特性原理与应用》+ Fankhauser et al. 2023 AJ | `li2024_space_object_optics` + `fankhauser2023_satellite_brightness` | .bib 有完整条目；Li 为专著（ISBN 9787302658672），Fankhauser 有 DOI | references.bib | Low | 保留并替换引用。建议用 Fankhauser 2023 作为英文期刊引用，Li 2024 可选作中文背景 |
| C02 | `[CITATION: optical light-curve attitude inversion]` | Wang et al. 2024 ASR + Hanada et al. 2024 ASR (PSO) | `wang2024_attitude_inversion_debris` + `advspaceres2024_pso_lightcurve` | .bib 有完整条目（DOI 均有） | references.bib | Low | 保留并替换引用。两篇覆盖实验室光度反演和优化搜索反演 |
| C03 | `[CITATION: image-based spacecraft pose estimation]` | Dickinson 2025 RIT PhD + Sosa et al. 2025 ViT | `dickinson2025_sim2real_6dof` + `sosa2025_vit_6dof` | .bib 有完整条目；Dickinson 为 PhD 论文（已下载 PDF） | references.bib | Medium | 保留并替换引用。Dickinson 为 PhD 论文非期刊，审稿人可能质疑；建议同时引 Sosa 2025 作为期刊/会议补充 |
| C04 | `[CITATION: BRDF-based space object photometry]` | Yang et al. 2024 Photonics + Lu 2024 Universe | `yang2024_goniopolarimetric` + `lu2024_brdf_starlink` | .bib 有完整条目（DOI 均有，PDF 已下载） | references.bib | Low | 保留并替换引用 |
| C05 | `[CITATION: ground-based optical observation degradation]` | Fankhauser et al. 2023 AJ + Dickinson 2025 (Ch.2 image quality analysis) | `fankhauser2023_satellite_brightness` + `dickinson2025_sim2real_6dof` | Fankhauser 讨论亮度模型含大气/地球反照；Dickinson 讨论 AO 图像质量 | references.bib + 阅读清单 | Medium | 保留并替换引用。注意：无专门讨论"地基光学退化"的单篇综述在 .bib 中；建议作者确认是否需补充一篇大气 seeing/PSF 文献（如 Hardy 1998 或 Roddier 1999） |

**补充说明**：

- `[CITATION: multi-modal fusion robustness]`（仅出现在 References 列表，正文未引用）：建议删除此占位，或在 §2.4 引用 Liu et al. 2024 Remote Sensing 时覆盖此需求。
- C05 是最薄弱的一项——当前 .bib 中没有专门讨论地基光学观测退化（大气湍流、PSF、跟踪误差）的文献。建议作者补充 1 篇经典大气光学或自适应光学文献。

---

## 2. Related Work 的 8 篇 [to verify] 文献逐条核验

### C07: Yang et al. 2024/2025 Photonics

| 字段 | 核验结果 |
|---|---|
| 完整引用 | Yang, Min; Mao, Hongxia; Wu, Jun; Zheng, Chong; Wang, Li. "Goniopolarimetric Properties of Typical Satellite Material Surfaces: Intercomparison with Semi-Empirical pBRDF Modeled Results." *Photonics*, 2024, 11(1), 17. |
| DOI | 10.3390/photonics11010017 |
| .bib key | `yang2024_goniopolarimetric` |
| PDF 状态 | 已下载：`papers/yang2024_goniopolarimetric.pdf` |
| 主稿描述核验 | "Semi-empirical pBRDF / Cook-Torrance-related models" — **准确**。该文对比 5 种 pBRDF 模型（含 Cook-Torrance 框架）在卫星材料上的表现 |
| "Material samples / satellite material surfaces" — **准确** |
| "Laboratory/material measurement" — **准确** |
| "Not central [to verify]" 关于自遮挡 — **准确**，该文不涉及自遮挡 |
| 风险 | Low |
| 建议 | **删除 `[to verify]`，保留并替换为正式引用**。注意：主稿写"Yang et al., 2024/2025"，实际只有 2024 年一篇，无 2025 年版本在 .bib 中。建议统一为"Yang et al., 2024" |

### C08: Lu/Yao 2024 Universe

| 字段 | 核验结果 |
|---|---|
| 完整引用 | Lu, Yao. "BRDF-Based Photometric Modeling of LEO Constellation Satellite from Massive Observations." *Universe*, 2024, 10(5), 215. |
| DOI | 10.3390/universe10050215 |
| .bib key | `lu2024_brdf_starlink` |
| PDF 状态 | 已下载：`papers/lu2024_brdf_starlink.pdf` |
| 主稿描述核验 | "LEO constellation satellite / Starlink model" — **准确** |
| "BRDF-based photometric model" — **准确**（Phong BRDF） |
| "Observation geometry considered; detailed self-occlusion [to verify]" — **部分准确**：该文考虑太阳能板遮挡，但非通用射线自遮挡模型 |
| "Real photometric observations" — **准确** |
| 风险 | Low |
| 建议 | **删除 `[to verify]`，保留并替换为正式引用**。Table 1 中 self-occlusion 列改为"Solar array occlusion considered"而非"detailed self-occlusion" |

### C09: Fankhauser et al. 2023 AJ

| 字段 | 核验结果 |
|---|---|
| 完整引用 | Fankhauser, F.; Tyson, J. A.; Askari, J. "Satellite Optical Brightness." *The Astronomical Journal*, 2023, 166, 59. |
| DOI | 10.3847/1538-3881/ace047 |
| .bib key | `fankhauser2023_satellite_brightness` |
| PDF 状态 | 未下载-需权限 |
| 主稿描述核验 | "Satellite brightness geometry" — **准确** |
| "Radiometric brightness model; sunlight and earthshine [to verify]" — **准确**（.bib keywords 含 "earthshine"） |
| "Not attitude-inversion focus" — **准确** |
| "Radiometric/astronomical analysis" — **准确** |
| 风险 | Low |
| 建议 | **删除 `[to verify]`，保留并替换为正式引用**。建议作者下载 PDF 确认 earthshine 模型细节 |

### C10: Wang et al. 2024 ASR

| 字段 | 核验结果 |
|---|---|
| 完整引用 | Wang, X. et al. "Attitude Inversion of Space Debris Based on the Laboratory-Tested Photometry Dataset." *Advances in Space Research*, 2024, 74(2), 949-963. |
| DOI | 10.1016/j.asr.2024.04.009 |
| .bib key | `wang2024_attitude_inversion_debris` |
| PDF 状态 | 未下载-需权限 |
| 主稿描述核验 | "Space debris / lab photometry target [to verify]" — **部分准确**：.bib keywords 含"space debris, light curve inversion, genetic algorithm, photometry, lab dataset"，确认为实验室光度数据集 |
| "Laboratory-tested photometry dataset" — **准确** |
| "Yes, photometry-based attitude inversion" — **准确** |
| "Reflectance assumptions [to verify]" — **无法完全核验**：未下载 PDF，.bib 未明确 BRDF 模型类型 |
| 风险 | Medium（BRDF 和 self-occlusion 字段未能从 .bib 确认） |
| 建议 | **删除标题/期刊/DOI 的 `[to verify]`**。Table 1 中 BRDF 列和 self-occlusion 列标注"Reflectance assumptions (not specified in abstract)"或待作者下载 PDF 后补充 |

### C11: Burton et al. 2024 ASR

| 字段 | 核验结果 |
|---|---|
| 完整引用 | Hanada, T. et al. "Light Curve Attitude Estimation Using Particle Swarm Optimizers." *Advances in Space Research*, 2024, 74(11), 5619-5638. |
| DOI | 10.1016/j.asr.2024.10.008 |
| .bib key | `advspaceres2024_pso_lightcurve` |
| PDF 状态 | 未下载-OA |
| **重要发现** | 主稿写"Burton et al. 2024 ASR"，但 .bib 中该文第一作者为 **Hanada, T.**（非 Burton）。需核实：(a) 是否为同一篇文献？(b) 是否存在另一篇 Burton 2024 ASR？ |
| 主稿描述核验 | "Known object model / space debris or satellite [to verify]" — 与 .bib keywords "PSO, light curve, attitude estimation, no initial guess" 一致 |
| "Light curve" — **准确** |
| "Yes, particle-swarm attitude estimation" — **准确** |
| 风险 | **High**（作者名可能错误） |
| 建议 | **作者必须核实**：下载 PDF 确认第一作者是 Burton 还是 Hanada。若为 Hanada，主稿和 Table 1 必须更正作者名。若确实存在另一篇 Burton 2024 ASR，需提供正确书目信息 |

### C12: Kumar et al. 2025 Acta Astronautica

| 字段 | 核验结果 |
|---|---|
| 完整引用 | Kumar, A. et al. "Light Curves Sequential Comparison Strategy for Improved Understanding of LEO Uncontrolled Objects." *Acta Astronautica*, 2025, 232, 1-15. |
| DOI | 10.1016/j.actaastro.2025.02.019 |
| .bib key | `kumar2025_leo_lightcurve` |
| PDF 状态 | 未下载-需权限 |
| 主稿描述核验 | "Digital twin / LEO uncontrolled objects [to verify]" — 与 .bib keywords "LEO, light curve, digital twin, attitude evolution, tumbling" 一致 |
| "Light curves / sequential comparison" — **准确** |
| "Attitude/object understanding [to verify]" — **准确**（.bib: "attitude evolution"） |
| 风险 | Low |
| 建议 | **删除 `[to verify]`，保留并替换为正式引用**。Table 1 中 self-occlusion 和 validation type 列建议标注"Not specified in abstract"待 PDF 确认 |

### C13: Dickinson 2025 RIT PhD

| 字段 | 核验结果 |
|---|---|
| 完整引用 | Dickinson, Thomas. "From Sim to 6DOF: Deep Learning for Real-Time Satellite Pose Estimation from Resolved Ground-Based Imagery." PhD Thesis, Rochester Institute of Technology, 2025. |
| .bib key | `dickinson2025_sim2real_6dof` |
| PDF 状态 | 已下载：`papers/dickinson2025_sim2real_6dof.pdf` |
| 主稿描述核验 | "CAD/satellite models; resolved ground-based imagery" — **准确** |
| "Image simulation [to verify]" — **准确**（合成训练 + 真实 AO 图像测试） |
| "Yes, 6DOF image-based pose estimation" — **准确** |
| "Synthetic training and resolved imagery evaluation [to verify]" — **准确** |
| 风险 | Medium（PhD 论文非同行评审期刊） |
| 建议 | **删除 `[to verify]`，保留引用**。建议在正文注明"PhD dissertation"。若审稿人质疑，可补引 Dickinson 2024 AMOS 会议论文（.bib key: `dickinson2024_6dof_pose`）作为同行评审补充 |

### C14: Liu et al. 2024 Remote Sensing

| 字段 | 核验结果 |
|---|---|
| 完整引用 | Liu, H. et al. "Tightly Coupled Visual-Inertial Fusion for Attitude Estimation of Spacecraft." *Remote Sensing*, 2024, 16(16), 3063. |
| DOI | 10.3390/rs16163063 |
| .bib key | `remote2024_visual_inertial_fusion` |
| PDF 状态 | 已下载：`papers/liu2024_visual_inertial_fusion.pdf` |
| 主稿描述核验 | "Spacecraft attitude estimation setting" — **准确** |
| "Not BRDF-based" — **准确** |
| "Visual/star-sensor features [to verify]" — **准确**（.bib: "star sensor, gyroscope, optimization"） |
| "Visual-inertial tightly coupled fusion" — **准确** |
| "Simulation and experimental evaluations [to verify]" — **准确** |
| 风险 | Low |
| 建议 | **删除 `[to verify]`，保留并替换为正式引用** |

---

## 3. Table 1 逐行逐列审计

### 核验原则

- 仅基于 .bib 条目信息（title/keywords/journal）和已下载 PDF 可确认的字段标记为"已核验"。
- 未下载 PDF 且 .bib 信息不足以确认的字段标记为"待 PDF 确认"。
- 明确错误的字段标记为"需更正"。

### 逐行审计结果

| 行 | 作者名核验 | Target/data | BRDF | Self-occlusion | Image | Scalar | Inversion | Fusion | Validation |
|---|---|---|---|---|---|---|---|---|---|
| Yang 2024 | ✓ 准确 | ✓ 材料样片 | ✓ pBRDF/Cook-Torrance | ✓ Not central | ✓ No | ✓ BRDF 测量 | ✓ No | ✓ No | ✓ 实验室 |
| Lu 2024 | ✓ 准确 | ✓ Starlink | ✓ BRDF photometric | **改写**：改为"Solar array occlusion considered" | ✓ No | ✓ 实测光度 | ✓ 参数拟合非姿态反演 | ✓ No | ✓ 真实观测 |
| Wang 2024 | ✓ 准确 | 待 PDF 确认具体目标 | 待 PDF 确认 | 待 PDF 确认 | ✓ No | ✓ 实验室光度 | ✓ GA 姿态反演 | ✓ No | ✓ 实验室 |
| Burton 2024 | **需更正**：可能为 Hanada | 待 PDF 确认 | 待 PDF 确认 | 待 PDF 确认 | ✓ No | ✓ Light curve | ✓ PSO | ✓ No | 待 PDF 确认 |
| Dickinson 2025 | ✓ 准确 | ✓ CAD/卫星模型 | ✓ 渲染隐含 | ✓ 渲染隐含 | ✓ Yes | ✓ No | ✓ 6DOF | ✓ No | ✓ 合成+真实 AO |
| Kumar 2025 | ✓ 准确 | ✓ 数字孪生/LEO | 待 PDF 确认 | 待 PDF 确认 | ✓ No | ✓ Light curves | ✓ 态势理解 | ✓ No | 待 PDF 确认 |
| Liu 2024 | ✓ 准确 | ✓ 航天器姿态 | ✓ Not BRDF | ✓ N/A | ✓ 视觉特征 | ✓ No | ✓ 姿态估计 | ✓ 紧耦合 | ✓ 仿真+实验 |
| Fankhauser 2023 | ✓ 准确 | ✓ 卫星亮度 | ✓ 辐射度模型 | ✓ Not focus | ✓ No | ✓ 亮度建模 | ✓ No | ✓ No | ✓ 天文分析 |
| Present work | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Table 1 修订建议

| # | 修订内容 | 理由 |
|---:|---|---|
| 1 | "Burton et al. 2024" → 核实后可能改为 "Hanada et al. 2024" | .bib 第一作者为 Hanada |
| 2 | "Yang et al. 2024/2025" → "Yang et al. 2024" | .bib 中仅有 2024 年一篇 |
| 3 | Lu 2024 self-occlusion 列：改为 "Solar array occlusion considered" | 非通用射线自遮挡 |
| 4 | Wang/Burton/Kumar 的 BRDF 和 self-occlusion 列：标注 "Not specified" 或待 PDF 确认后填写 | 不可猜测 |
| 5 | 删除所有 `[to verify]` 标记（已核验字段直接写入；未核验字段改为 "—" 或 "Not specified"） | 投稿不可保留占位 |
| 6 | 考虑增加 AISwarm-LS 2025 (Aerospace) 行 | .bib 有完整条目，joint estimation 与本文 fusion 形成对比 |
| 7 | 考虑增加 Valenta & Gunter 2022 (JAS) 行 | CNN+BRDF 光变姿态分类，与模块 C CNN 反演直接对标 |

---

## 4. References 列表中未在正文使用的占位

| 占位 | 正文是否引用 | 建议 |
|---|---|---|
| `[CITATION: multi-modal fusion robustness]` | 正文未直接引用此占位 | 删除。§2.4 已引用 Liu 2024 覆盖 fusion 思想 |

---

## 5. Related Work 修订版骨架

以下为段落级骨架，不扩写完整最终稿。

### §2.1 Optical signatures and BRDF modeling of space objects

**核心逻辑**：BRDF 是物理光度建模的基础 → 卫星材料 BRDF 实验验证 → 大规模观测 BRDF 建模 → 本文用途不同（不仅预测亮度，还生成配对 OCS+图像）

**引用链**：
- Yang 2024 Photonics → Cook-Torrance/pBRDF 适用于卫星材料（实验室验证）
- Lu 2024 Universe → Phong BRDF + 海量 Starlink 观测建模
- Fankhauser 2023 AJ → 完整卫星亮度模型（含 earthshine）
- 可选补充：Shah 2024 JAS（材料老化 BRDF）、Ceniceros 2015 AMOS（BRDF vs 实测光变对比）

**本文定位句**：The present study follows this physical-modeling tradition but uses it for a different purpose: generating paired OCS signatures and photometric images from one shared forward model.

### §2.2 Light-curve and OCS-based attitude inversion

**核心逻辑**：光变/OCS 是紧凑可解释的姿态约束 → 实验室/仿真光度反演 → 优化搜索方法 → 数字孪生策略 → 本文不把 OCS 当自动上限

**引用链**：
- Wang 2024 ASR → 实验室光度数据 + GA 反演
- Hanada (或 Burton) 2024 ASR → PSO 无初值姿态估计
- Kumar 2025 Acta Astronautica → 数字孪生 + 光变序列比较
- 可选补充：AISwarm-LS 2025 Aerospace（联合估计姿态+光学参数+大气）、Valenta 2022 JAS（CNN+BRDF 光变分类）

**本文定位句**：In the present work, OCS is not treated as the automatic accuracy upper bound. Its value is instead tested as a low-dimensional, multi-geometry, physically interpretable constraint.

### §2.3 Photometric image simulation and image-based pose estimation

**核心逻辑**：图像提供空间线索 → 合成图像+深度学习姿态估计 → Sim2Real 挑战 → 本文把 clean image 当上限而非场景性能

**引用链**：
- Dickinson 2025 RIT PhD → 6DOF 合成训练 + 真实 AO 图像测试
- Sosa 2025 (ViT) → 强视觉模型 baseline
- 可选补充：Dickinson 2024 AMOS（同行评审版本）

**本文定位句**：Clean synthetic photometric images may contain strong attitude cues, but clean-image accuracy is not a direct estimate of field performance.

### §2.4 Multi-modal fusion and robustness under observation degradation

**核心逻辑**：融合动机是不同模态在不同条件下失效 → 视觉-惯性紧耦合示例 → 本文问题不同（两个光学模态来自同一 BRDF 场景）

**引用链**：
- Liu 2024 Remote Sensing → 视觉-惯性紧耦合融合（精度提升 50%）
- 可选补充：Marto 2024（多信息源增强姿态可辨识性）

**本文定位句**：This setting allows us to ask a narrower question: when OCS and photometric images are physically consistent, does fusion add meaningful information?

---

## 6. 不可使用或暂缓使用文献清单

| 文献 | 原因 | 建议 |
|---|---|---|
| "Burton et al. 2024 ASR" | .bib 中对应条目第一作者为 Hanada，非 Burton。可能为作者名错误或混淆了另一篇文献 | **暂缓使用**，作者必须下载 PDF 核实第一作者后再决定 |
| "Yang et al. 2025" | .bib 中仅有 Yang 2024 Photonics，无 2025 年版本 | **删除 2025 标注**，统一为 Yang 2024 |
| Groves 2025 (自监督 SSA) | 与本文主题（姿态反演）关联较弱，更偏异常检测 | 不建议进入 Related Work 正文；可选 Future Work 一句 |
| Xiong 2025 (多曝光融合) | 与本文主题关联较弱，偏图像前处理 | 不建议进入 Related Work 正文 |
| 所有未下载 PDF 的文献 | 无法核验 Table 1 中 BRDF/self-occlusion/validation 具体字段 | 对应 Table 1 字段标注"—"或"Not specified"，不可猜测 |

---

## 7. 可直接进入 v0.2 的安全替换项

| # | 替换内容 | 理由 |
|---:|---|---|
| 1 | `[CITATION: optical space object characterization]` → `(Fankhauser et al., 2023)` | .bib 有完整 DOI，内容匹配 |
| 2 | `[CITATION: optical light-curve attitude inversion]` → `(Wang et al., 2024; Hanada et al., 2024)` | .bib 有完整 DOI（注意 Burton→Hanada 待确认） |
| 3 | `[CITATION: BRDF-based space object photometry]` → `(Yang et al., 2024; Lu, 2024)` | .bib 有完整 DOI，PDF 已下载 |
| 4 | `[CITATION: image-based spacecraft pose estimation]` → `(Dickinson, 2025; Sosa et al., 2025)` | .bib 有完整条目 |
| 5 | `[CITATION: ground-based optical observation degradation]` → `(Fankhauser et al., 2023)` + 待作者补充大气光学文献 | 暂用 Fankhauser 覆盖部分需求 |
| 6 | 删除 References 中 `[CITATION: multi-modal fusion robustness]` | 正文未引用，§2.4 已有 Liu 2024 覆盖 |
| 7 | "Yang et al., 2024/2025" → "Yang et al., 2024" 全文统一 | 无 2025 版本 |
| 8 | Table 1 所有已核验行：删除 `[to verify]` 标记 | 已通过 .bib 核验 |
| 9 | Table 1 未核验字段：`[to verify]` → "—" 或 "Not specified" | 不可保留占位投稿 |

---

## 8. 作者仍需补充的材料

| # | 材料 | 紧急程度 |
|---:|---|---|
| 1 | 下载 "Burton/Hanada 2024 ASR" PDF，确认第一作者 | 必须（投稿前） |
| 2 | 下载 Wang 2024 ASR PDF，确认 BRDF 模型和 self-occlusion 字段 | 必须（Table 1 完整性） |
| 3 | 下载 Kumar 2025 Acta Astronautica PDF，确认 validation type | 高 |
| 4 | 下载 Fankhauser 2023 AJ PDF，确认 earthshine 模型细节 | 高 |
| 5 | 补充 1 篇地基光学观测退化/大气 seeing 文献（C05 缺口） | 高 |
| 6 | 决定是否在 Table 1 增加 AISwarm-LS 2025 和/或 Valenta 2022 行 | 中 |
| 7 | 决定 Dickinson 2025 是否保留为 PhD 论文引用，或替换为 Dickinson 2024 AMOS 会议论文 | 中 |

---

*第 2 阶段 Claude 侧输出完成。本报告不修改主稿，所有建议交由 Codex 审阅后决定是否纳入 v0.2。*

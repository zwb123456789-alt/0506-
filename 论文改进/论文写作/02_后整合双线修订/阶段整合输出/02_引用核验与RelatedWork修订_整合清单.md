# 02 引用核验与 Related Work 修订：阶段整合清单

> 整合日期：2026-06-01  
> 输入：GPT 输出、Claude 输出、Codex 单边审阅记录、本地 `references.bib` 与公开书目信息交叉核验  
> 用途：作为最终整合版 v0.1 到 v0.2 的引用替换、Related Work 修订和 Table 1 收紧依据。  
> 结论：第 2 阶段完成。GPT 的外部核验应优先于本地旧 `references.bib`；Claude 的结构化审计可吸收，但其被旧 bib 误导的作者、年份、DOI 和页码不得直接进入 v0.2。

## 1. 总体结论

第 2 阶段确认了两个事实：

1. v0.1 的 Related Work 主线可以保留，但必须把引用占位拆分为具体文献组合，不能用宽泛 `[CITATION]` 作为单篇万能引用。
2. 本地 `references.bib` 存在多处关键书目信息错误，v0.2 前必须修订 bib 或在主稿中使用已核验的正确元数据。

本阶段不直接改写主稿。进入 v0.2 前应先按本清单更新参考文献元数据，再改 Related Work 和 Table 1。

## 2. 已核验且建议采用的引用

| ID | 文献 | 核验后信息 | DOI / URL | 用途 | v0.2 处理 |
|---|---|---|---|---|---|
| R01 | Yang satellite materials | Yang, Mao, Wu, Zheng, Wang. *Photonics* 2025, 12(1), 17 | `10.3390/photonics12010017` | 卫星材料反射 / pBRDF 背景 | 采用；修正本地 bib 的年份、卷期和 DOI |
| R02 | Lu BRDF photometry | Lu. *Universe* 2024, 10(5), 215 | `10.3390/universe10050215` | Starlink BRDF 亮度建模、chassis blocking、earthshine | 采用；写作中避免说成姿态反演 |
| R03 | Fankhauser satellite brightness | Fankhauser, Tyson, Askari. *AJ* 2023, 166(2), 59 | `10.3847/1538-3881/ace047` | 卫星光学亮度、earthshine / radiometric modeling | 采用；建议作者补 PDF 核细节 |
| R04 | Wang lab photometry inversion | Shu-Shu Wang, Lin, Kang, Men, Zhao. *ASR* 2024, 74(2), 949-963 | `10.1016/j.asr.2024.04.005` | 实验室光度数据集姿态反演 | 采用；修正本地 bib 作者和 DOI |
| R05 | Burton PSO light curve | Burton, Robinson, Frueh. *ASR* 2024, 74(11), 5619-5638 | `10.1016/j.asr.2024.09.008` | 光变曲线 PSO 姿态和角速度估计 | 采用；不要按本地 bib 写 Hanada / `.10.008` |
| R06 | Kumar sequential comparison | Kumar et al. *Acta Astronautica* 2025, 232, 654-665 | `10.1016/j.actaastro.2025.04.018` | LEO 非受控目标 light-curve sequential comparison / digital twin | 采用；修正页码和 DOI |
| R07 | Dickinson AMOS | Dickinson, Walvoord, Gartley. AMOS 2024 | `10.64861/XCUS5673` | resolved ground-based imagery / 6DOF pose | Table 1 主行优先用 AMOS；PhD 可作补充 |
| R08 | Dickinson PhD | Dickinson. RIT PhD thesis, 2025 | RIT repository | sim-to-real 6DOF, AO imagery, real-image evaluation | 可保留为补充引用，不宜作为唯一核心来源 |
| R09 | Yi visual-inertial fusion | Yi, Ma, Long, Zhu, Zhao. *Remote Sensing* 2024, 16(16), 3063 | `10.3390/rs16163063` | visual-inertial fusion analogy | 将原 `Liu et al.` 改为 Yi et al. |

## 3. 已确认需要修正的本地 BibTeX 条目

| 本地 key / 占位 | 当前问题 | 修正方向 |
|---|---|---|
| `yang2024_goniopolarimetric` | 年份、卷期和 DOI 与公开页面冲突 | 改为 2025, 12(1), 17, DOI `10.3390/photonics12010017`；可考虑重命名为 `yang2025_goniopolarimetric` |
| `wang2024_attitude_inversion_debris` | DOI `.04.009` 和作者 `Wang, X.` 错 | 改为 Shu-Shu Wang et al., DOI `10.1016/j.asr.2024.04.005` |
| `advspaceres2024_pso_lightcurve` | 本地第一作者 Hanada / DOI `.10.008` 与外部核验冲突 | 改为 Burton, Robinson, Frueh, DOI `10.1016/j.asr.2024.09.008`；可重命名为 `burton2024_pso_lightcurve` |
| `kumar2025_leo_lightcurve` | DOI `.02.019`、页码 1-15 错 | 改为 DOI `10.1016/j.actaastro.2025.04.018`，页码 654-665 |
| `remote2024_visual_inertial_fusion` | 作者写作 Liu et al. 错 | 改为 Yi et al., DOI `10.3390/rs16163063`；可重命名为 `yi2024_visual_inertial_fusion` |

## 4. Introduction 引用替换策略

| 原占位 | 处理策略 | 推荐引用 |
|---|---|---|
| `[CITATION: optical space object characterization]` | 拆成 optical brightness / photometric modeling / attitude inference，不用单篇万能引用 | Fankhauser 2023; Lu 2024; Wang 2024 |
| `[CITATION: optical light-curve attitude inversion]` | 支撑光度/光变姿态反演 | Wang 2024; Burton 2024; Kumar 2025 |
| `[CITATION: image-based spacecraft pose estimation]` | 支撑 resolved imagery / 6DOF pose；若泛指 spacecraft pose 可补更通用视觉姿态文献 | Dickinson 2024 AMOS; Dickinson 2025 PhD |
| `[CITATION: BRDF-based space object photometry]` | 分别支撑材料反射、BRDF 亮度建模和 radiometric brightness | Yang 2025; Lu 2024; Fankhauser 2023 |
| `[CITATION: ground-based optical observation degradation]` | 当前证据不足，不能只用 Fankhauser/Dickinson 硬撑全部 seeing/PSF/tracking/noise | 需补 1 篇地基光学观测退化、seeing、PSF、tracking 或 AO 成像文献 |
| `[CITATION: multi-modal fusion robustness]` | 若正文不用，删除 References 占位；若保留融合类比，用 visual-inertial 文献并说明不是同类 OCS-image fusion | Yi 2024 |

## 5. Table 1 修订原则

Table 1 应定位为 `scope comparison`，不是对每篇外文文献的完整技术审计。字段写法必须保守。

| Work | Target/data | BRDF/reflectance | Self-occlusion/visibility | Image branch | Scalar branch | Attitude inversion | Fusion | Validation type | 建议 |
|---|---|---|---|---|---|---|---|---|---|
| Yang 2025 | satellite material samples | semi-empirical pBRDF comparison | Not central | No | material reflectance characterization | No | No | lab material measurement | 删除姿态反演暗示；不写成本文同类任务 |
| Lu 2024 | Starlink V1.5 / massive observations | BRDF-based brightness model | chassis blocking / earthshine considered | No | apparent brightness / photometry | Not primary attitude inversion | No | real photometric observations + model fitting | `self-occlusion` 不写 full facet-level benchmark |
| Fankhauser 2023 | satellite brightness geometry | radiometric brightness / BRDF assumptions | Not attitude-inversion focus | No | brightness modeling | No | No | astronomical / radiometric analysis | 用于 earthshine 与 brightness 背景 |
| Wang 2024 | space debris / lab-tested photometry | not specified from public metadata | not specified from public metadata | No | laboratory photometry | Yes | No | laboratory-tested photometry dataset | BRDF / visibility 字段待 PDF 核实 |
| Burton 2024 | simulated light curves / known object assumptions | reflectance assumptions need full text | not specified from public metadata | No | light curve | Yes, PSO attitude and angular velocity | No | simulated light curves | 改正作者和 DOI；不要写 laboratory |
| Kumar 2025 | SL-14 / LEO uncontrolled object | light-curve / digital twin assumptions | not specified from public metadata | No | light curves / sequential comparison | attitude reconstruction / understanding | No | observation + digital twin / sequential comparison | target 写具体，validation 待全文核实 |
| Dickinson 2024 AMOS | resolved ground-based imagery | synthetic image generation, not BRDF-centered | included through rendering / imagery, exact details not central | Yes | No OCS branch | Yes, 6DOF | No OCS-image fusion | synthetic training + real resolved imagery evaluation | Table 1 主行建议用 AMOS 2024 |
| Yi 2024 | star sensor + gyroscope spacecraft setting | Not BRDF-based | N/A | visual star-sensor measurements | No OCS/light curve | Yes | visual-inertial tightly coupled fusion | simulations / evaluations | 只作融合鲁棒性类比 |
| Present work | real satellite STL, controlled yaw-pitch grid | GGX/Cook-Torrance, nonuniform components | analytical ray-based self-occlusion | clean photometric images | multi-geometry OCS | Yes, yaw-pitch inversion | late + feature fusion | simulation benchmark, no real telescope validation | 保留边界 |

## 6. Related Work 段落级修订方向

### 2.1 Optical signatures and BRDF modeling

保留“BRDF 物理建模传统”主线，但把 Yang 写成材料 pBRDF 实验，把 Lu 写成 Starlink BRDF brightness modeling，把 Fankhauser 写成 satellite optical brightness / earthshine 背景。不要说这些文献已经完成本文同类 OCS-image paired inversion。

### 2.2 Light-curve and OCS-based attitude inversion

用 Wang 支撑 laboratory photometry dataset attitude inversion，用 Burton 支撑 PSO light-curve attitude / angular-velocity estimation，用 Kumar 支撑 LEO uncontrolled object sequential comparison / digital twin。保留本文定位句：OCS 不是自动精度上限，而是低维、可解释、多几何 photometric constraint。

### 2.3 Photometric image simulation and image-based pose estimation

优先引用 Dickinson 2024 AMOS 作为同行交流版本，Dickinson 2025 PhD 作补充。写作重点应是 resolved ground-based imagery、synthetic training 和 real-image / sim-to-real difficulty。clean rendered image 仍必须写作 upper-bound benchmark，不是 field performance。

### 2.4 Multi-modal fusion and robustness

将原 `Liu et al.` 改为 Yi et al.，并明确 visual-inertial fusion 与本文 OCS-image fusion 不同。该小节只用于引出“融合应从鲁棒性和失效模式评价”，不能证明本文融合必然优于单模态。

## 7. 仍需作者后续统一处理的问题

这些问题不阻塞进入第 3 阶段图表规划，但会阻塞 v0.2 定稿或投稿前版本：

| ID | 问题 | 处理时机 |
|---|---|---|
| Q01 | 补 1 篇地基光学观测退化 / seeing / PSF / AO / tracking 文献 | v0.2 引用替换前 |
| Q02 | 下载或核对 Wang / Burton / Kumar / Fankhauser PDF，确认 Table 1 中 BRDF、visibility、validation 字段 | Table 1 定稿前 |
| Q03 | 决定 Dickinson 2024 AMOS 与 Dickinson 2025 PhD 的主从关系 | Table 1 / Related Work 定稿前 |
| Q04 | 决定是否新增 AISwarm-LS 2025、Valenta 2022、Sosa 2025 等可选行 | Table 1 保留在正文时再定 |
| Q05 | 修订 `references.bib` 并统一 bib key | v0.2 引用替换前 |

## 8. 可进入 v0.2 的安全修改候选

1. 删除 v0.1 中所有宽泛 `[CITATION]` 占位，按本清单拆成具体引用组合。
2. 将 `Yang et al. 2024/2025` 统一为 `Yang et al. 2025`，并降调为 semi-empirical pBRDF / satellite material reflectance。
3. 将 `Lu/Yao 2024` 统一为 `Lu 2024`，并写作 BRDF brightness modeling，不写作姿态反演。
4. 将 `Liu et al. 2024 Remote Sensing` 改为 `Yi et al. 2024 Remote Sensing`，或删除该融合类比。
5. 将 Wang / Burton / Kumar 的 Related Work 描述按具体任务拆开，避免混写为同一类方法。
6. 将 Table 1 改成保守 scope-comparison；无法核实的 BRDF / self-occlusion 字段写 `Not specified` 或 `Not central`。
7. 保留 `Present work` 行中的 no real telescope validation。

## 9. 阶段结论

第 2 阶段“引用核验与 Related Work 修订”完成。下一阶段进入：

```text
03_图表制作与Caption定稿
```

下一阶段只规划图表、caption、数据来源、主文/补充材料分配和待确认数值，不实际绘图，不把尚未确认的作者事实或实验数值固化进图表。

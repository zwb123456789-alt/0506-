# GPT 输出：引用核验与 Related Work 修订

> 日期：2026-06-01  
> 对象：最终整合版 v0.1 的 Introduction 引用占位、Related Work 与 Table 1  
> 输出性质：交给 Codex 审阅整合的核验清单；不直接修改主稿。  
> 核验边界：本轮使用公开网页、出版商页面、机构库和 DOI 页面核验书目信息与摘要级支撑。未读取全文细节或网页无法确认的字段一律保留“未完全核验/需原文核对”，不删除 `[to verify]`。

## 总体结论

v0.1 中多数候选文献可以找到可靠书目信息，但 Table 1 的若干字段需要收紧。尤其是：

- `Yang et al. 2024/2025 Photonics` 应修订为 Yang et al., Photonics 2025, 12(1), 17, DOI `10.3390/photonics12010017`。
- `Lu/Yao 2024 Universe` 应修订为 Yao Lu, Universe 2024, 10(5), 215, DOI `10.3390/universe10050215`。
- `Liu et al. 2024 Remote Sensing` 的作者名不匹配，公开页面核到的是 Yi et al., Remote Sensing 2024, 16(16), 3063, DOI `10.3390/rs16163063`。
- `Burton et al. 2024 ASR`、`Wang et al. 2024 ASR`、`Kumar et al. 2025 Acta Astronautica`、`Fankhauser et al. 2023 AJ`、`Dickinson 2025 RIT PhD / AMOS 2024` 均可核验到基础书目信息。
- Introduction 中的概念型 `[CITATION: ...]` 不建议直接替换为单篇“万能引用”；应按句子拆分后用已核验文献组合支撑。

## A. 已核验引用表

| ID | 原占位/文献名 | 核验后文献信息 | DOI/URL | 支撑内容 | 可否用于正文 | 备注 |
|---|---|---|---|---|---|---|
| V001 | Yang et al. 2024/2025 Photonics | Min Yang, Hongxia Mao, Jun Wu, Chong Zheng, Li Wang. “Goniopolarimetric Properties of Typical Satellite Material Surfaces: Intercomparison with Semi-Empirical pBRDF Modeled Results.” Photonics 2025, 12(1), 17. | https://doi.org/10.3390/photonics12010017；页面：https://www.mdpi.com/2304-6732/12/1/17 | 卫星材料表面偏振/反射实验；pBRDF/semi-empirical model 对比；材料反射特性支撑 | 可用于 2.1 和材料参数/BRDF 背景 | 年份应写 2025，不是 2024/2025；Table 1 不应写成态度反演文献 |
| V002 | Lu/Yao 2024 Universe | Yao Lu. “BRDF-Based Photometric Modeling of LEO Constellation Satellite from Massive Observations.” Universe 2024, 10(5), 215. | https://doi.org/10.3390/universe10050215；页面：https://www.mdpi.com/2218-1997/10/5/215 | Starlink V1.5 亮度建模；BRDF photometric model；millions of observations；chassis blocking and earthshine | 可用于 2.1、Introduction 的 BRDF photometry 和 real observation support | 作者应写 Lu 而非 Lu/Yao；该文是 brightness modeling，不是 attitude inversion |
| V003 | Fankhauser et al. 2023 AJ | Forrest Fankhauser, J. Anthony Tyson, Jacob Askari. “Satellite Optical Brightness.” The Astronomical Journal 2023, 166(2), 59. | https://doi.org/10.3847/1538-3881/ace047；Mendeley/metadata 页面：https://www.mendeley.com/catalogue/06d339e0-09ed-3e4f-8b63-4e14bb533eda/ | satellite apparent brightness; direct sunlight and Earth-reflected illumination; BRDF component assumptions | 可用于 2.1 和 ground-based brightness / earthshine / radiometric modeling | 建议再核 IOP/ADS 页面以获取正式 BibTeX |
| V004 | Wang et al. 2024 ASR | Shu-Shu Wang, Hou-Yuan Lin, An-Ming Kang, Jin-Rui Men, Chang-Yin Zhao. “Attitude inversion of space debris based on the laboratory-tested photometry dataset.” Advances in Space Research 2024, 74(2), 949-963. | https://doi.org/10.1016/j.asr.2024.04.005；ScienceDirect PII: S0273117724003375 | laboratory-tested photometry dataset; attitude inversion from photometric/light-curve data | 可用于 2.2 | ScienceDirect 页面可检索到摘要片段，但本轮直接打开遇到 429；书目信息由卷期目录和 DOI 页面核验 |
| V005 | Burton et al. 2024 ASR | Alexander Burton, Liam Robinson, Carolin Frueh. “Light curve attitude estimation using particle swarm optimizers.” Advances in Space Research 2024, 74(11), 5619-5638. | https://doi.org/10.1016/j.asr.2024.09.008；页面：https://www.sciencedirect.com/science/article/pii/S0273117724009281 | light-curve-only attitude and angular-velocity estimation; particle swarm optimizer; ambiguity/no initial state guess | 可用于 2.2 | Table 1 可写 simulation / simulated light curves；不要写 laboratory validation |
| V006 | Kumar et al. 2025 Acta Astronautica | S. Kumar, L. Chiavari, L. Cimino, S. Varanese, L. Mariani, M. Rossetti, G. Zarcone, T. Schildknecht, F. Nasuti, F. Piergentili. “Light curves sequential comparison strategy for improved understanding of LEO uncontrolled objects.” Acta Astronautica 2025, 232, 654-665. | https://doi.org/10.1016/j.actaastro.2025.04.018；页面：https://www.sciencedirect.com/science/article/pii/S009457652500219X | LEO uncontrolled objects; light-curve sequential comparison; digital twin simulation; attitude reconstruction/inversion | 可用于 2.2 | Table 1 应写 SL-14 rocket body / uncontrolled RSO，而非泛泛 LEO object |
| V007 | Dickinson 2025 RIT PhD | Thomas W.N. Dickinson. “From Sim to 6DOF: Deep Learning for Real-Time Satellite Pose Estimation from Resolved Ground-Based Imagery.” Ph.D. dissertation, Rochester Institute of Technology, 2025. | https://repository.rit.edu/theses/12305/ | 6DOF pose estimation from resolved ground-based AO imagery; synthetic training; real labeled imagery validation | 可用于 2.3，但建议期刊稿优先引用 AMOS 2024 同主题论文 | 学位论文可以保留为补充引用；Table 1 若强调 peer-reviewed，应改用 AMOS 2024 |
| V008 | Dickinson et al. 2024 AMOS | Thomas Dickinson, Derek Walvoord, Michael Gartley. “Automated 6DOF Satellite Pose Estimation From Resolved Ground-Based Imagery.” AMOS 2024. | https://doi.org/10.64861/XCUS5673；页面：https://amostech.space/year/2024/automated-6dof-satellite-pose-estimation-from-resolved-ground-based-imagery/ | resolved ground-based EO/AO imagery; simulated training; real imagery test; 6DOF pose | 可替代或补充 Dickinson 2025 PhD | 会议论文更适合作为 Table 1 主引用 |
| V009 | Yi et al. 2024 Remote Sensing | Jinhui Yi, Yuebo Ma, Hongfeng Long, Zijian Zhu, Rujin Zhao. “Tightly Coupled Visual-Inertial Fusion for Attitude Estimation of Spacecraft.” Remote Sensing 2024, 16(16), 3063. | https://doi.org/10.3390/rs16163063；页面：https://www.mdpi.com/2072-4292/16/16/3063 | star sensor + gyroscope visual-inertial tightly coupled attitude estimation; robustness under high-dynamic / lost-in-space settings | 可用于 2.4 的 general fusion contrast | 主稿占位 `Liu et al. 2024` 应改为 Yi et al. 2024 |
| V010 | Rubio Antón et al. 2026 ASR | Jorge Rubio Antón, Adrián de Andrés, Carlos Paulete, Ángel Gallego, Diego Escobar. “Attitude estimation of uncontrolled space objects: A Bayesian-informed swarm intelligence approach.” Advances in Space Research 2026, 77(3), 3791-3814. | https://doi.org/10.1016/j.asr.2025.11.112；页面：https://www.sciencedirect.com/science/article/pii/S0273117725013961 | light-curve attitude estimation for uncontrolled objects using AIS/PSO/UKF | 可作为可选替代/新增引用 | 不是 v0.1 原 Table 1 候选，但可增强 2.2；注意出版年 2026 |

## B. 未核验或建议删除引用表

| ID | 原占位/文献名 | 问题 | 风险 | 建议处理 | 替代检索方向 |
|---|---|---|---|---|---|
| U001 | `[CITATION: optical space object characterization]` | 过宽，占位不是具体文献 | High | 不用单篇硬替换；拆成 optical photometry / brightness / attitude inference 两类引用 | Fankhauser 2023 AJ; Lu 2024 Universe; Wang 2024 ASR; Burton 2024 ASR |
| U002 | `[CITATION: optical light-curve attitude inversion]` | 可由 Wang/Burton/Kumar 支撑，但需按具体句子分配 | High | 替换为 Wang 2024 ASR + Burton 2024 ASR；若写 uncontrolled LEO object 加 Kumar 2025 Acta | light curve attitude estimation space objects photometry |
| U003 | `[CITATION: image-based spacecraft pose estimation]` | Dickinson 可支撑 resolved ground-based imagery，但若句子泛指 spacecraft pose estimation 还需补近距离/SPACECRAFT pose 文献 | Medium | 用 Dickinson 2024 AMOS 或 Dickinson 2025 PhD 支撑 resolved ground-based imagery；泛化表述降调 | satellite pose estimation resolved AO imagery synthetic training |
| U004 | `[CITATION: BRDF-based space object photometry]` | Lu/Fankhauser/Yang 可支撑不同层面，但不是同一类任务 | High | 句子拆分：BRDF photometric model 用 Lu；earthshine/radiometric brightness 用 Fankhauser；material reflectance 用 Yang | BRDF satellite photometry Starlink material reflectance |
| U005 | `[CITATION: ground-based optical observation degradation]` | 本轮未找到专门总述该句所有退化因素的单篇文献；Dickinson 可支撑 blur/noise/AO imagery，Lu/Fankhauser支撑观测不确定性 | High | 不要用一个宽泛占位；改成“real observations include ...”并由 Dickinson + Lu/Fankhauser 分别支撑；PSF/seeing需另查专业 AO/SSA 文献 | ground-based electro-optical satellite imaging adaptive optics seeing PSF tracking noise |
| U006 | `[CITATION: multi-modal fusion robustness]` | Reference list 有占位，但正文对应句实际是 visual-inertial fusion | Medium | 若保留 2.4，替换为 Yi et al. 2024 Remote Sensing；若不再讨论泛化 fusion，删除此占位 | tightly coupled visual inertial spacecraft attitude estimation |
| U007 | `Liu et al. 2024 Remote Sensing` | 作者名与核验文献不匹配 | High | 改为 Yi et al. 2024 Remote Sensing，或重新查是否另有 Liu 文献 | Remote Sensing 2024 16 3063 visual-inertial spacecraft attitude |
| U008 | Table 1 的 `detailed self-occlusion [to verify]` for Lu 2024 | Lu 2024 页面可核到 chassis blocking and earthshine，不宜写 detailed self-occlusion | Medium | 改为 “chassis blocking / shadowing considered; not a full attitude-inversion self-occlusion benchmark” | Lu 2024 Starlink chassis blocking earthshine |
| U009 | Table 1 的 Yang `Cook-Torrance-related models [to verify]` | 公开摘要核到 semi-empirical pBRDF；是否 Cook-Torrance-related需原文确认 | Medium | 改为 “semi-empirical pBRDF; exact model details to verify from full text” | Yang Photonics pBRDF satellite material |
| U010 | Table 1 的 Dickinson `image simulation [to verify]` | 已核验 synthetic CAD/AO imagery，但 PhD 与 AMOS版本数值不同 | Low | 若 Table 1 用 AMOS 2024，按 AMOS 页修订；若用 PhD，按 PhD 页面修订 | Dickinson AMOS 2024 6DOF satellite pose |

## C. Table 1 字段核验表

| Work | Target/data | BRDF/reflectance | Self-occlusion/visibility | Image branch | Scalar branch | Attitude inversion | Fusion | Validation type | 修订建议 |
|---|---|---|---|---|---|---|---|---|---|
| Yang et al. 2025 Photonics | two typical satellite material samples; 400-1000 nm lab goniopolarimetric measurements | semi-empirical pBRDF model comparison; exact Cook-Torrance link not confirmed | not central | No | material reflectance characterization, not OCS inversion | No | No | laboratory material measurement | 修订年份和题名；删除“attitude inversion”暗示；Cook-Torrance 字段降为 pBRDF |
| Lu 2024 Universe | Starlink V1.5 / millions of MMT-9 photometric observations | BRDF-based photometric model; Phong BRDF in model | chassis blocking and earthshine considered; not same as facet-level self-occlusion benchmark | No resolved inversion image branch | brightness / apparent magnitude modeling | Not primarily attitude inversion | No | real photometric observations + model fitting | 将 “Lu/Yao” 改为 “Lu”；self-occlusion 字段改为 chassis blocking / earthshine |
| Wang et al. 2024 ASR | space debris; laboratory-tested photometry dataset | photometric/light-curve dataset; exact reflectance model requires full-text check | not confirmed in public abstract | No | laboratory photometry / light curve | Yes, photometry-based attitude inversion | No | laboratory-tested photometry dataset + simulation/inversion | 保留，但 Table 1 的 reflectance/self-occlusion 字段需原文核对 |
| Burton et al. 2024 ASR | known object albedo shape + simulated light curve | albedo shape / reflective assumptions | not Table-1 central; exact visibility assumptions need full text | No | light curve | Yes, attitude and angular velocity estimation using PSO | No | simulated light curves | 改为 Advances in Space Research 74(11), 5619-5638；不要写 laboratory |
| Dickinson et al. 2024 AMOS / Dickinson 2025 PhD | resolved ground-based EO/AO imagery; Seasat/HST in PhD; Seasat in AMOS page | synthetic CAD/HFWO/AO-style image generation; not BRDF-centered | included through image simulation/rendering; exact visibility details not Table-1 central | Yes, resolved imagery | No OCS/light curve | Yes, 6DOF image-based pose estimation | temporal smoothing/Kalman in pipeline, not OCS-image fusion | synthetic training + real resolved imagery evaluation | 建议 Table 1 主行改为 Dickinson et al. 2024 AMOS；PhD 可作补充 |
| Kumar et al. 2025 Acta Astronautica | SL-14 rocket body / LEO uncontrolled object light curves | light-curve / digital twin assumptions; exact reflectance model needs full text | not confirmed from public abstract | No resolved image branch | light curves / sequential comparison | attitude reconstruction / light-curve inversion | No | historical observation + digital twin simulation | 将 target/data 写具体；不要泛泛写所有 LEO objects |
| Yi et al. 2024 Remote Sensing | spacecraft star sensor and gyroscope setting | not BRDF-based | not relevant | star sensor visual measurements | no OCS/light curve | spacecraft attitude estimation | visual-inertial tightly coupled fusion | numerical tests | 替换原 `Liu et al.`；说明该文只是 fusion robustness analogy，不是同类 OCS-image fusion |
| Fankhauser et al. 2023 AJ | satellite optical brightness geometry; selected Starlink validation | radiometric brightness / BRDF component assumptions; direct sunlight + earthshine | not attitude-inversion focus | No resolved inversion branch | brightness modeling | No attitude inversion benchmark | No | model compared with selected observations | 保留；支撑 earthshine/radiometric brightness，不支撑 attitude inversion |
| Present work | real satellite STL; controlled yaw-pitch grid | GGX/Cook-Torrance with nonuniform component assignment | analytical ray-based self-occlusion | clean rendered photometric images | multi-geometry OCS signatures | yes, controlled yaw-pitch inversion | OCS-image late and feature fusion | simulation benchmark; no real telescope validation | 当前字段可保留；强调 no real telescope validation |

## D. Related Work 段落修订建议

| 小节 | 当前问题 | 可安全保留的句子 | 必须改写的句子 | 建议替换文本 |
|---|---|---|---|---|
| 2.1 Optical signatures and BRDF modeling | 候选文献基本可用，但年份/作者/模型字段需修正；Lu 2024 用 Phong BRDF 而非本工作的 GGX/Cook-Torrance | “Optical signatures ... coupled effects ...” 可保留；“This shared model is essential ...” 可保留 | “Studies ... Cook-Torrance-type descriptions ... [Yang]” 需降调；“Lu/Yao”作者名错误 | “Laboratory goniopolarimetric measurements of satellite materials have been used to characterize polarized reflectance and evaluate semi-empirical pBRDF models (Yang et al., 2025). Large observational datasets have also supported BRDF-based brightness modeling of Starlink satellites, including chassis blocking and earthshine effects (Lu, 2024), while radiometric brightness studies show that Earth-reflected illumination can contribute substantially to apparent satellite brightness (Fankhauser et al., 2023).” |
| 2.2 Light-curve and OCS-based attitude inversion | Wang/Burton/Kumar 可用，但 Table 1 要区分 lab dataset、PSO simulated light curves、digital twin/sequential comparison | “Light curves and OCS-like scalar photometric signatures are attractive ...” 可保留 | “Recent digital-twin and sequential-comparison strategies...” 可保留但需写具体 SL-14 rocket body | “Photometry-based attitude inversion has been studied using laboratory-tested photometry datasets (Wang et al., 2024), while PSO-based methods estimate attitude and angular velocity from light curves without requiring an initial state guess (Burton et al., 2024). Sequential light-curve comparison and digital-twin simulation have also been used to reconstruct the attitude evolution of uncontrolled LEO rocket bodies (Kumar et al., 2025).” |
| 2.3 Photometric image simulation and image-based pose estimation | Dickinson 2025 PhD/AMOS 2024 支撑强，但应避免“first practical system”等强宣称进入本文 | “Resolved and rendered images provide spatial cues...” 可保留 | “Dickinson's 2025 dissertation ...” 可保留，但建议用 AMOS 2024 或 PhD 二选一 | “Recent work on resolved ground-based EO/AO imagery has demonstrated synthetic-training pipelines for 6DOF satellite pose estimation and real-image testing, highlighting both the value of resolved imagery and the sim-to-real difficulty under blur, noise, partial illumination, and limited image quality (Dickinson et al., 2024; Dickinson, 2025).” |
| 2.4 Multi-modal fusion and robustness | 原 `Liu et al.` 应改为 Yi et al.; visual-inertial fusion 与本工作不是同类模态 | “The fusion problem studied here is different ...” 可保留 | “In spacecraft attitude estimation ... [Liu]” 作者占位错误 | “In spacecraft attitude estimation, tightly coupled visual-inertial methods combine star-sensor visual measurements with gyroscope information to improve robustness in dynamic or degraded measurement conditions (Yi et al., 2024). Although this differs from the OCS-image fusion considered here, it motivates evaluating fusion through robustness and failure modes rather than mean error alone.” |

## E. 优先处理顺序

1. 将 `Liu et al. 2024 Remote Sensing` 改为核验到的 `Yi et al. 2024 Remote Sensing`，或删除该行重新检索真正的 Liu 文献。
2. 将 `Yang et al. 2024/2025 Photonics` 修订为 `Yang et al. 2025 Photonics`，并把 Cook-Torrance 表述降调为 semi-empirical pBRDF，除非原文确认具体模型。
3. 将 `Lu/Yao 2024 Universe` 修订为 `Lu 2024 Universe`，并把字段改为 BRDF brightness modeling / chassis blocking / earthshine。
4. 用 Wang 2024 ASR、Burton 2024 ASR、Kumar 2025 Acta 分别支撑 laboratory photometry、PSO light-curve estimation、sequential comparison/digital twin，不要混成同一类。
5. 决定 Dickinson 引用版本：正文和 Table 1 建议用 AMOS 2024，PhD 作为补充或不列 Table 1 主行。
6. Introduction 中的 6 个 `[CITATION: ...]` 应按句子拆分替换，不要一对一硬塞单篇文献。
7. Table 1 所有 “self-occlusion / visibility” 字段必须保守；无法从摘要/公开页确认的写 “not central / not confirmed from public metadata”。
8. 对 `ground-based optical observation degradation` 继续补查专门 AO/SSA 成像退化文献；当前 Dickinson + Lu/Fankhauser 只能支撑部分退化与观测不确定性。
9. 将 Related Work 中所有 “to verify” 删除前，先由 Codex 或作者用 DOI/原文确认 BibTeX/EndNote 元数据。
10. v0.2 中保留 Table 1 但减少猜测字段；必要时将 Table 1 改为 “scope comparison” 而非详尽技术审计表。

## 可安全进入 v0.2 的替换候选

以下替换可由 Codex 审阅后进入 v0.2，但建议仍保留引用元数据核查记录：

```text
Yang et al. 2024/2025 Photonics -> Yang et al. 2025 Photonics, 12(1), 17, DOI: 10.3390/photonics12010017
Lu/Yao 2024 Universe -> Lu 2024 Universe, 10(5), 215, DOI: 10.3390/universe10050215
Fankhauser et al. 2023 AJ -> Fankhauser, Tyson, Askari 2023, AJ 166(2), 59, DOI: 10.3847/1538-3881/ace047
Wang et al. 2024 ASR -> Wang, Lin, Kang, Men, Zhao 2024, ASR 74(2), 949-963, DOI: 10.1016/j.asr.2024.04.005
Burton et al. 2024 ASR -> Burton, Robinson, Frueh 2024, ASR 74(11), 5619-5638, DOI: 10.1016/j.asr.2024.09.008
Kumar et al. 2025 Acta Astronautica -> Kumar et al. 2025, Acta Astronautica 232, 654-665, DOI: 10.1016/j.actaastro.2025.04.018
Liu et al. 2024 Remote Sensing -> Yi et al. 2024 Remote Sensing 16(16), 3063, DOI: 10.3390/rs16163063
Dickinson 2025 RIT PhD -> Dickinson et al. 2024 AMOS, DOI: 10.64861/XCUS5673, or Dickinson 2025 RIT PhD as supporting thesis
```

## Sources Used

- Yang et al. 2025 Photonics: https://www.mdpi.com/2304-6732/12/1/17
- Lu 2024 Universe: https://www.mdpi.com/2218-1997/10/5/215
- Fankhauser et al. 2023 AJ metadata: https://www.mendeley.com/catalogue/06d339e0-09ed-3e4f-8b63-4e14bb533eda/
- Wang et al. 2024 ASR metadata: https://www.mindat.org/reference.php?id=17422876
- Burton et al. 2024 ASR: https://www.sciencedirect.com/science/article/pii/S0273117724009281
- Kumar et al. 2025 Acta Astronautica: https://www.sciencedirect.com/science/article/pii/S009457652500219X
- Dickinson 2025 RIT PhD: https://repository.rit.edu/theses/12305/
- Dickinson et al. 2024 AMOS: https://amostech.space/year/2024/automated-6dof-satellite-pose-estimation-from-resolved-ground-based-imagery/
- Yi et al. 2024 Remote Sensing: https://www.mdpi.com/2072-4292/16/16/3063
- Rubio Antón et al. 2026 ASR optional replacement: https://www.sciencedirect.com/science/article/pii/S0273117725013961

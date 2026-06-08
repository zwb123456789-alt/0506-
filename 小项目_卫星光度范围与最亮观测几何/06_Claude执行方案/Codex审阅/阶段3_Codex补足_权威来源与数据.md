# 阶段3 Codex补足：常规高轨/GEO卫星视星等权威来源与数据

补足时间：2026-06-07

用途：补足 Claude 因网络问题无法核实的阶段3资料，特别是“一般常规高轨/GEO卫星 reported typical range”的证据链。

## 结论先行

基于已核实的公开资料，当前可支撑的保守结论是：

```text
现有 SSA/SST 观测资料、机构报告和多目标 GEO 光度研究表明，常规运行 GEO/active geostationary satellites 通常是可由小到中等口径光学系统观测的目标，多数 reported apparent magnitude 位于约 11-15 mag 量级；其中典型通信卫星个例 Galaxy 14 被报告为约 11-14 mag，多个系统观测研究显示 active GEO satellites 通常亮于约 15 mag。太阳翼或其他平坦反射部件在有利太阳-目标-观测几何下可产生数个星等的 glint/flare 增亮。该范围应写作 reported typical range in surveyed/observed cases，而非严格统计普适范围。
```

推荐最终口径：

```text
常规运行 GEO 卫星 reported typical range：约 11-15 mag。
其中 11-14 mag 可作为大型通信卫星/典型个例和部分常见观测条件下的较亮子范围；
接近 15 mag 可作为 active GEO/已编目目标与小型碎片/暗弱群体的经验分界附近。
```

## 已核实可用来源

### S1. PNNL 技术报告：Galaxy 14 个例，11-14 mag

| 字段 | 内容 |
|---|---|
| 来源 | PNNL-23994, *A New Approach to Space Situational Awareness Using Small Ground-Based Telescopes* |
| 机构 | Pacific Northwest National Laboratory |
| 年份 | 2014 |
| 对象 | Galaxy 14, GEO C-band communications satellite |
| 关键数据 | 报告称 Galaxy 14 的 apparent visual magnitude typically ranged between 11 and 14；同一观测中 Calsky 估计为 13.8 mag，图像计数估计约 14.3 mag |
| 证据等级 | B：机构报告 + 单颗典型 GEO 通信卫星 |
| 用途 | 支撑“大型GEO通信卫星个例约 11-14 mag” |
| 链接 | https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-23994.pdf |

建议写法：

```text
Galaxy 14, a GEO communications satellite, is reported in PNNL-23994 as typically 11-14 visual magnitude, with one observing session giving estimates around 13.8-14.3 mag.
```

### S2. Payne et al. 2006 AMOS：36颗GEOS光度签名分类

| 字段 | 内容 |
|---|---|
| 来源 | Payne, Gregory, Luu, *SSA Analysis of GEOS Photometric Signature Classifications and Solar Panel Offsets*, AMOS 2006 |
| 作者/机构 | Tamara E. Payne, Stephen A. Gregory, Kim Luu; Boeing LTS / AFRL |
| 样本 | 36 GEOS over CONUS or US Pacific territory |
| 关键内容 | 引入 photometry-based classification system；约 80% 卫星可归入两类光度签名；分析 solar panel pointing offsets |
| 证据等级 | A-/B+：系统样本 + AMOS/AFRL/Boeing；但论文重点是光变分类，不直接给 typical magnitude range |
| 用途 | 支撑“运行/常规GEOS的光度签名有系统样本，亮度强依赖太阳翼和相位角” |
| 链接 | https://amostech.com/TechnicalPapers/2006/NROC/Payne.pdf |

建议替代 Claude 文中的 E7/E9 部分，用它作为“多目标 operational GEOS 光度行为”证据，但不要强行从它推出 11-14 mag。

### S3. Jolley et al. 2015 AMOS / RMC thesis：6颗active GEO，多夜、BVRI、高时序光度

| 字段 | 内容 |
|---|---|
| 来源 | Jolley, Bédard, Wade, *Multicolour Optical Photometry of Active Geostationary Satellites*, AMOS 2015；Jolley MSc thesis 2014 |
| 样本 | 6 active geostationary satellites |
| 仪器 | 14-inch Celestron CG-14, Bessel BVRI filters |
| 数据 | 12 nights, each satellite observed on 3-8 nights；calibrated apparent magnitudes in filter bands；每条光变约 200 data points |
| 关键发现 | GEO lightcurves can vary more than generally recognized；glint brightening varies by about 1 to 10 magnitudes above baseline；illumination-observation geometry is critical |
| 证据等级 | A-/B+：active GEO 多目标、多夜、标准滤光片；但更重机制和变幅，不直接给总体 typical range |
| 链接 | https://amostech.com/TechnicalPapers/2015/Poster/Jolley.pdf |

用途：

- 支撑“常规active GEO光度不能只给单一数值，几何和季节会显著改变亮度”；
- 支撑“glint/强反射增亮必须单独列，不混入常规范围”；
- 支撑你后续最亮姿态搜索必须包含太阳方向、观测方向、姿态、roll和材料。

### S4. STING 2025 ASR：112颗active geostationary objects，全夜多色系统巡天

| 字段 | 内容 |
|---|---|
| 来源 | Airey et al., *A comprehensive survey of the GEO-belt using simultaneous four-colour observations with STING*, Advances in Space Research |
| 年份 | 2025 |
| DOI | 10.1016/j.asr.2025.02.027 |
| 样本 | 112 active geostationary objects, April-May 2023 |
| 关键内容 | first large systematic colour survey of GEO belt；full-night multi-colour light curves；测量 54 颗卫星 solar panel offsets；识别 short-timescale glinting features |
| 证据等级 | A：最新、同行评议、active GEO大样本 |
| 链接 | https://www.sciencedirect.com/science/article/pii/S0273117725001474 |

用途：

- 强支撑“常规/active GEO 的光度行为需要大样本和全夜光变，不宜用单点星等概括”；
- 可替代 Claude 的 E6/E7/E9 中未核实的“系统研究”条目；
- 若需要具体星等分布，下一步应优先从此文图表/补充数据中提取。

注意：当前公开摘要确认样本和光变特征，但未在摘要中给出 11-14 mag 分布；不要从该文摘要直接推出 typical magnitude 数字。

### S5. Vananti et al. 2017 ASR/ESA：active GEO通常 brighter than 15 mag

| 字段 | 内容 |
|---|---|
| 来源 | Vananti et al., *Reflectance spectroscopy characterization of space debris*, Advances in Space Research, 59(10), 2488-2500 |
| 年份 | 2017 |
| DOI | 10.1016/j.asr.2017.02.033 |
| 机构/设备 | ESA Space Debris Telescope, Tenerife, 1-m class |
| 关键表述 | Active GEO satellites were observed; satellites are relatively bright, usually brighter than 15 mag |
| 证据等级 | A：同行评议 + ESA相关观测 |
| 链接 | https://www.sciencedirect.com/science/article/pii/S0273117717301461 |

用途：

```text
支撑“active GEO / 常规卫星通常亮于约 15 mag”，与 Galaxy 14 的 11-14 mag 个例共同构成 reported typical range 的上限/暗端约束。
```

### S6. Stingray 2024 Sensors：约200个near-GEO目标，G<15.5可测

| 字段 | 内容 |
|---|---|
| 来源 | Campbell et al., *Stingray Sensor System for Persistent Survey of the GEO Belt*, Sensors 2024 |
| DOI | 10.3390/s24082596 |
| 系统 | 15-camera optical array, nightly astrometric and photometric survey of GEO belt above Tucson |
| 关键数据 | field of regard内每晚约 200 near-GEO satellites；自动管线测量 GAIA G magnitude brighter than approximately 15.5 的目标；初始一月调查 photometric uncertainty 0.062 ± 0.008 mag |
| 证据等级 | A-/B+：最新系统论文；支撑系统可测亮度和near-GEO群体量级 |
| 链接 | https://www.mdpi.com/1424-8220/24/8/2596 |

用途：

- 支撑“near-GEO常规可观测目标多数可在 G≈15.5 以内由系统管线测量”；
- 支撑“15 mag附近是常规GEO/near-GEO自动光度巡天的实际工作亮度边界之一”。

### S7. Hall & Kervin 2013 AMOS：stabilized GEO glints，可超过数个星等振幅

| 字段 | 内容 |
|---|---|
| 来源 | Hall & Kervin, *Analysis of Faint Glints from Stabilized GEO Satellites*, AMOS 2013 |
| 关键内容 | Operational GEO satellites often have solar panels that glint; well-known solar-panel glints can exceed several stellar magnitudes in amplitude；fainter glints can be as small as 0.2 mag |
| 证据等级 | A-/B+：AMOS/AFRL/Boeing，GEO glint机制权威资料 |
| 链接 | https://scixplorer.org/abs/2013amos.confE..34H/abstract |

用途：

- 支撑 glint/flare 不应混入常规亮度；
- 支撑“有利几何/强反射条件可带来数个星等增亮”。

### S8. Vrba et al. 2009 AMOS：geosynchronous glint survey

| 字段 | 内容 |
|---|---|
| 来源 | Vrba et al., *A Survey of Geosynchronous Satellite Glints*, AMOS 2009 |
| 样本 | DirecTV-9S 8 consecutive nights during 2009 vernal equinox glint season；also GE-2, GE-4, DirecTV-4S |
| 关键内容 | glints caused by specular reflection from flat surfaces such as solar panels；can briefly increase reflected light by several hundred times nominal diffuse signature |
| 证据等级 | B+：专门glint观测 campaign |
| 链接 | https://amostech.space/year/2009/a-survey-of-geosynchronous-satellite-glints/ |

用途：

- 支撑“glint是特殊几何下的瞬时峰值，不可作为常规 reported typical range”；
- several hundred times flux 对应约 5-6 mag 量级增亮，但建议只写“several hundred times / several magnitudes”，不要换算成绝对峰值。

## 对 Claude 当前 E6-E9 的替换建议

Claude 当前 E6/E7/E9 中有若干未核实条目：

```text
Hejduk 2012-2015 GEO typical 11-15 mag
Cognion 2013-2016 baseline 12-14 mag peak 8-10 mag
Africano 2004 three-axis stabilized 11-14 mag
```

当前检索无法稳定确认这些具体“数值范围 + 样本量 + 论文题名”组合。建议不要把它们作为直接证据写入最终结论。

建议替换为：

| 原条目 | 建议处理 | 替换/补强来源 |
|---|---|---|
| E6 Hejduk 11-15 mag | 改为“photometric modeling / phase functions / catalogue behavior 背景”，不直接支撑常规亮度范围 | Hejduk 2010 catalogue-wide behavior；Hejduk 2011/2012 modeling |
| E7 Cognion 12-14 / 8-10 | 暂删或降为待核验，不进入主结论 | Payne 2006 36 GEOS；Jolley 2015 6 active GEO |
| E8 GEODSS | 保留为系统能力背景，不直接证明 typical range | Stingray 2024 G<15.5 measured near-GEO targets |
| E9 Africano 11-14 | 暂删或待核验 | PNNL Galaxy 14；Vananti 2017 active GEO >15；STING 2025 112 active GEO |

## 建议修订后的主证据表

| 编号 | 来源 | 样本 | 直接支撑什么 | 建议证据等级 |
|---|---|---|---|---|
| S1 | PNNL-23994 Galaxy 14 | 1 GEO communications satellite | 11-14 mag 个例，13.8/14.3 mag观测估计 | B |
| S2 | Payne et al. 2006 AMOS | 36 GEOS | GEOS光度签名系统分类、太阳翼offset | A-/B+ |
| S3 | Jolley et al. 2015 AMOS / thesis | 6 active GEO, 多夜BVRI | active GEO多夜光变，glint增亮1-10 mag | A-/B+ |
| S4 | Airey et al. 2025 ASR/STING | 112 active GEO | 最新大样本active GEO全夜多色光变 | A |
| S5 | Vananti et al. 2017 ASR/ESA | active GEO + debris spectra | active GEO usually brighter than 15 mag | A |
| S6 | Campbell et al. 2024 Sensors/Stingray | ~200 near-GEO/night | G<15.5目标可由自动管线测量，系统光度精度 | A-/B+ |
| S7 | Hall & Kervin 2013 AMOS | stabilized GEO glints | glint振幅可超过数个星等 | A-/B+ |
| S8 | Vrba et al. 2009 AMOS | DirecTV-9S等 | glint可达数百倍nominal diffuse | B+ |

## 修订后的推荐结论

建议将阶段3最终结论改为：

```text
现有公开 SSA/SST 资料支持一个保守的 reported typical range：常规运行 GEO/active geostationary satellites 通常亮于约 15 mag，典型大型通信卫星个例和部分常见观测条件下多报告在约 11-14 mag。考虑不同卫星尺寸、姿态、相位角、太阳翼指向和波段差异，本项目采用约 11-15 mag 作为常规高轨/GEO卫星的 reported typical range，而将约 11-14 mag 作为较亮的通信卫星/典型观测子范围。太阳翼或其他平坦高反射部件在有利几何下可产生数个星等的 glint 增亮，但 glint峰值必须单独列出，不并入常规范围。
```

如果用户必须给一个“一般常规高轨卫星的值”，建议写：

```text
reported typical range: about 11-15 mag
working reference range for large operational GEO communications satellites: about 11-14 mag
```

## 仍需注意

1. 不要写“普适范围 = 11-14 mag”。11-14 更像典型大型通信卫星子范围。
2. 不要把 15 mag 以后的暗弱目标都叫碎片；只是许多碎片/小目标落在暗弱端，仍可能有暗的运行/退役大目标。
3. 波段仍未统一：V/R/G/Clear 混用时，应写 approximate apparent magnitude。
4. glint 的峰值建议写“数个星等振幅”或“several hundred times nominal diffuse”，不要给未核验的负星等。
5. OCS sanity check 应独立，不用于反推文献范围。

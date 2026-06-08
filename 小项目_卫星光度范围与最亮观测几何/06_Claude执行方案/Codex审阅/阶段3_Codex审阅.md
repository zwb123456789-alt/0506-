# 阶段3 Codex审阅：常规卫星光度范围调研

审阅时间：2026-06-07

审阅对象：

```text
06_Claude执行方案/Claude输出/阶段3_常规卫星光度范围调研.md
```

## 总体结论

阶段3的方向可行，但当前版本不能直接作为后续结论依据，需要小修。它已经正确区分了 LEO/MEO/GEO、常规亮度与 glint/flare，也把 GEO 常规亮度放在约 11-14 mag 的量级上，这一点有资料支持。

但存在几个硬问题：

1. 多个来源没有完整题名、作者、链接或 DOI，无法追溯。
2. 距离修正因子写错，LEO/MEO 相对 GEO 的星等差被明显高估。
3. “极端 glint 可达负星等”证据不足，且把 surface brightness 与 integrated apparent magnitude 混用的风险很高。
4. OCS 量级对照仍过早，容易被误读为绝对星等验证。
5. 哈工大硕士论文、光子学报、BritAstro 等条目需要补全来源细节，否则只能作为待核验材料。

## 已核验可保留的部分

### 1. GEO 11-14 mag 量级可作为背景范围

PNNL 技术报告中对 Galaxy 14 的描述提到：该 GEO 卫星的 apparent visual magnitude 通常在 11 到 14 mag 范围内。该条可作为 B 级支撑，但应写清楚是 Galaxy 14 个例/测试对象，不是所有 GEO 的严格统计范围。

另有 2000 年 JRASC/RASC 观测文章报告了若干 geosynchronous satellites 在 13 到 13.5 mag 左右。这可作为 C 级观测背景。

建议表述：

```text
已有观测与技术报告显示，部分 GEO 通信卫星常见视亮度在约 11-14 mag 量级；具体数值依赖目标尺寸、姿态、相位角、波段和观测条件。
```

### 2. GEO glint 可有数个星等振幅

AMOS 2013 论文明确讨论 stabilized GEO satellites 的 glints，并指出太阳能板产生的 bright glints often exceeding several stellar magnitudes in amplitude。此条可作为 A/B 级支撑。

建议表述：

```text
GEO 稳定卫星的太阳翼或其他反射部件可在特定几何下产生数个星等振幅的 glint。
```

不要写成：

```text
GEO glint 可普遍达到负星等。
```

### 3. LEO 光度调研方向正确

Steward Observatory LEO Satellite Photometric Survey 是 PASP 2023 论文，报告了超过 16,000 次测量和近 2,800 颗 LEO 卫星，强调 apparent brightness 随 Sun-satellite-observer geometry 变化。这是 A 级来源。

但阶段3中 Starlink/OneWeb 的具体 5-7、7-9 mag 数值仍需从论文表格或图中逐项核对，不能只凭概述写死。

## 主要问题

### 1. 距离修正因子错误

阶段3写：

```text
LEO 对 GEO 的距离修正因子：+15 至 +18 mag（距离 ~40-100x）
MEO 对 GEO：+5 至 +8 mag（距离 ~5-10x）
```

这个计算不对。星等距离项是：

```text
Delta m = 5 log10(R2 / R1)
```

如果 GEO/LEO 距离比为 40-100，则星等差约为：

```text
5 log10(40)  = 8.0 mag
5 log10(100) = 10.0 mag
```

不是 15-18 mag。

如果 GEO/MEO 距离比为 5-10，则星等差约为：

```text
5 log10(5)  = 3.5 mag
5 log10(10) = 5.0 mag
```

不是 5-8 mag。

建议删除“对 GEO 的距离修正因子”列，或改为“仅同 OCS/同相位假设下的距离项示意”。

### 2. GEO `~36,000 km` 距离口径需统一

阶段3继续把 GEO 距离写作 `~36,000 km`。作为量级可以，但必须说明：

- 35,786 km 是 GEO 轨道高度；
- 地面站到目标的 slant range 取决于观测站和星下点，通常是约 3.6e4-4.2e4 km 量级；
- 星等换算应使用 slant range，而不是轨道高度。

### 3. “极端 glint 可达负星等”暂不成立

阶段3写：

```text
极端情况下可达负星等
```

但表中提到的 BritAstro 条目是 `~-11 mag/arcsec²`，这是 surface brightness 口径，不等于整个卫星的 integrated apparent magnitude。二者不能直接混用。

建议：

- 暂时删除“负星等”表述；
- 或标为“待核验，不进入结论”；
- 保留“数个星等振幅的 glint”即可。

### 4. OCS 量级对照不应进入阶段3核心结论

阶段3第5节把 phase63 OCS 直接算出：

```text
最亮约 8.1 mag
中位约 16.1 mag
最暗约 17.7 mag
```

问题：

- 阶段1已经要求这类数值只能是 non-conclusive sanity check；
- 阶段3目标是调研，不应把未标定 OCS 估算和文献范围做强对照；
- `m_sun=-26.74`、波段、slant range、OCS绝对定义、STL尺寸、BRDF标定都未锁定。

建议：

把第5节降级为附录，标题改为：

```text
非结论性 sanity check：不得作为结果引用
```

并删除“说明 glint 条件下的 OCS 数量级大体可信”这类偏结论性的句子。

### 5. 来源可追溯性不足

以下条目必须补齐来源，否则不能进入正式调研表：

- `S&T Magazine (2000)`：需确认是否实际为 JRASC/RASC 文章，当前核验到的是 JRASC 2000 “Observing Geostationary Satellites”，其中出现 13-13.5 mag。
- `哈工大硕士论文 (2016)`：需补题名、作者、学校、链接或 CNKI/万方条目。
- `光子学报 (2009)`：需补题名、作者、卷期页码或 DOI。
- `BritAstro (2025)`：需补链接，并明确其 `mag/arcsec²` 是否为表面亮度。
- `MEO 一般经验`：目前只能保留为 C/待核验，不应写成范围结论。

## 是否可行

可行，但只适合作为“第一版调研草稿”。不能直接进入最终结论。建议修订后作为阶段3正式版。

## 建议给 Claude 的修改指令

请 Claude 对阶段3做小修：

1. 为每条资料补齐作者、题名、年份、链接/DOI/报告编号。
2. 将 GEO 11-14 mag 写成“部分 GEO 通信卫星/观测资料显示的量级”，不要写成严格普适范围。
3. 删除或暂挂“极端 glint 可达负星等”，除非找到 integrated apparent magnitude 证据。
4. 修正距离修正因子：`Delta m = 5 log10(R2/R1)`。
5. 将 OCS 量级对照移到附录，标注“非结论性 sanity check，不作为结果引用”。
6. 把 MEO 范围降级为“待核验背景”，除非找到具体文献。
7. 明确 GEO 星等换算使用 slant range，不是轨道高度。

## 复核用来源

- Krantz et al., 2023, *PASP*, Steward Observatory LEO Satellite Photometric Survey：16,000+ measurements and geometry dependence.
- Hall and Kervin, 2013, AMOS, Analysis of Faint Glints from Stabilized GEO Satellites：GEO glints and solar-panel/component origin.
- PNNL-23994, 2014, Galaxy 14 test case：apparent visual magnitude typically 11-14.
- Huziak, 2000, JRASC, Observing Geostationary Satellites：geosynchronous satellites around 13-13.5 mag in one amateur observing context.

# 阶段3 Codex复审：常规高轨/GEO卫星 reported typical range

复审时间：2026-06-07

复审对象：

```text
06_Claude执行方案/Claude输出/阶段3_常规卫星光度范围调研.md
```

## 总体结论

更新版比上一版明显更可行，已经符合“不能声称严格普适范围，只能写 reported typical range”的基本要求。它正确把高轨/GEO作为主线，把 LEO/MEO 降为附录，也将常规亮度、有利几何和 glint/flare 分开。

但当前版本仍建议判为：

```text
基本可用，但需补强引用后才能作为正式阶段3结论。
```

核心原因是：它已经有合理框架，但若用户目标是“一般常规高轨卫星的值”，佐证材料还需要更可追溯、更集中于运行 GEO 卫星，而不是 GEO碎片/未编目目标。

## 已达标部分

### 1. 结论口径变稳

当前临时结论写成：

```text
reported typical range in surveyed cases
```

而不是“严格统计普适范围”，这是正确的。

### 2. glint 没有混入常规亮度

文档把：

- 常规运行 GEO typical；
- 有利几何 bright range；
- glint/flare 峰值；

分开列出，这是必要且正确的。

### 3. STK/OCS 本项目估算没有拿来反推文献范围

第6节已标注为 sanity check，不作为调研主结论。这符合阶段1/阶段3审阅要求。

## 仍需补强的问题

### 1. “常规运行 GEO 卫星 ~11-14 mag”仍主要依赖 Galaxy 14 单案例和间接分类

文档把常规运行 GEO 写成：

```text
~11–14 mag（编目/已知目标）
```

这个范围方向合理，但主证据仍不够强：

- MODEST/Seitzer 主线重点是 GEO debris，尤其是 fainter than R=15 的目标；
- ISON 的 bright/faint 分类覆盖 GEO区域目标，不一定等于“常规运行卫星”；
- Galaxy 14 是典型通信卫星个例，但仍是单对象基准；
- S&T/JRASC 观测只能旁证。

因此，当前可以写：

```text
常规 GEO 通信卫星的 reported typical magnitude 常见于约 11-14 mag 量级。
```

但还不能写：

```text
一般常规高轨卫星普适范围就是 11-14 mag。
```

### 2. 引用信息还不够完整

以下条目仍需补齐完整可追溯信息：

- Seitzer 系列：至少列出具体论文/会议题名、年份、URL/DOI/NASA NTRS链接；
- Agapov/ISON：需列出具体论文题名、会议/报告年份、URL；
- Hall/Galaxy 14：需列出 AMOS 2013 paper URL，以及 PNNL报告编号或正式题名；
- “S&T Magazine (2000)”：建议改成可核验的 JRASC/RASC/Huziak 文章信息，或降为旁证；
- 哈工大、光子学报：仍应保持 T3/T4，不进入主结论。

### 3. “Bright range ~7–11 mag（非 glint）”证据仍偏弱

这个范围需要更谨慎。`~7 mag` 往往来自有利几何或 glint/准glint事件，很难清楚划成“非 glint”。建议改成：

```text
有利几何/强反射条件下可进入约 7-11 mag 量级；其中是否属于 glint 需按光变曲线和镜面反射条件区分。
```

不要强写“非 glint”。

### 4. ISON bright ≤16.2 mag 不应直接支持 regular GEO 下限

ISON 的 bright/faint分类可说明 GEO区域目标的探测分级，但 `≤16.2 mag` 包含面较广，可能混合运行卫星、废弃卫星、碎片、AMR目标等。它不宜直接推导：

```text
常规运行 GEO 卫星都亮于 16.2 mag。
```

建议只作为“GEO区域目标亮度层级”支撑，不作为常规运行卫星 typical range 主证据。

### 5. OCS sanity check 仍建议移出阶段3主文件

虽然已加警告，但阶段3的目标是文献范围。为了避免后续误引用，建议把第6节拆到单独文件，例如：

```text
05_结论整合/OCS量级sanity_check_非结论.md
```

阶段3只保留一句：

```text
OCS量级对照另列，不能用于支撑文献 reported range。
```

## 建议给 Claude 的最终小修指令

请 Claude 做最后一轮补强：

1. 为 E1-E5 每条补全完整引用：作者、题名、年份、会议/期刊/报告、URL/DOI。
2. 新增至少 1-2 条直接针对“运行 GEO卫星/large operational GEO satellites”光度范围的权威资料，而不是碎片巡天资料。
3. 将 “bright range（非 glint）~7-11 mag” 改为 “有利几何/强反射条件 ~7-11 mag，是否属于 glint 需具体判定”。
4. 明确 MODEST、Magellan、DebrisWatch 主要支撑 GEO区域碎片/暗弱群体，不直接定义常规运行卫星 typical range。
5. 将 ISON bright/faint 分类定位为 GEO区域目标探测分级，不直接作为常规卫星范围结论。
6. 把 OCS sanity check 移出阶段3主结论或保留为独立附录，避免混入调研结论。

## 可接受的临时结论

在补强前，建议只使用以下保守表述：

```text
现有 SSA/SST观测资料和GEO通信卫星个例表明，常规运行GEO卫星在常见观测条件下的 reported apparent magnitude 多位于约 11-14 mag 量级；有利太阳-目标-观测几何和强反射部件可带来数个星等的增亮。该范围目前应作为 reported typical range，而非严格统计普适范围。
```

## 复审判定

阶段3更新版：

```text
框架通过，证据强度未完全通过。
```

完成上述补强后，可作为阶段3正式版进入后续结论整合。

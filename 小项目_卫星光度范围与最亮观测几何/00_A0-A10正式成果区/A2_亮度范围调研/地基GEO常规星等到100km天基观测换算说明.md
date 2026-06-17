# 地基 GEO 常规星等到 100 km 天基观测的换算说明

## 结论摘要

当前小项目中使用的“常规运行 GEO 卫星约 11-15 mag”应理解为**地基光学观测下的表观星等范围**，不是天基 100 km 近距离观测结果。Schmitt (2020) 的 61 颗 active geostationary communications satellites 样本也是地基观测：观测地点为 Flagstaff, Arizona，使用 B、V、R、I 滤光片，对 GEO 通信卫星进行多波段光度观测。

如果下一步假设天基观测距离固定为 100 km，并且暂时只考虑“观测距离”变化，不改变太阳照明、相位角、姿态、BRDF、遮挡和传感器通带，那么可以把地基 GEO 星等分布整体平移：

```text
m_space(100 km) = m_ground - 5 log10(Delta_ground / 100 km)
```

其中 `Delta_ground` 是地基观测时观测站到 GEO 卫星的拓扑距离。对 GEO，典型量级为 `3.6e4-4.2e4 km`。因此从地基 GEO 到 100 km 天基观测，目标会变亮约 `12.8-13.1 mag`。

若采用项目当前的地基常规范围 `11-15 mag`，并取代表性地基距离 `Delta_ground = 40000 km`，则：

```text
Delta m = 5 log10(40000 / 100) = 5 log10(400) = 13.01 mag
m_space ≈ 11-15 - 13.01 = -2.0 to +2.0 mag
```

因此，在“只做距离换算、100 km 固定距离、仍按随机姿态/相位统计”的简化假设下，可暂取：

```text
100 km 天基观测下常规 GEO 卫星综合星等范围 ≈ -2 to +2 mag
```

这个范围不是新的实测天基统计结果，而是把地基随机观测分布按距离平方反比关系平移得到的工程估计。

## 1. 这个星等范围是地基观测还是天基观测？

是**地基观测**。

项目中目前引用的常规 GEO 星等范围主要来自地面光学观测文献或地面观测系统经验。Schmitt (2020) 尤其明确：该文观测 61 颗 active GEO 通信卫星，地点为 Flagstaff, AZ，使用 B、V、R、I 多波段滤光片。其目标是统计卫星的 quiescent magnitudes and colors，图 2 给出了不同波段的星等分布直方图。

因此，这些数值反映的是：地面望远镜在约 GEO 距离上观测运行卫星时得到的表观亮度分布。它不能直接作为 100 km 天基近距离观测的表观星等。

## 2. 地基 GEO 观测距离应该取多少？

GEO 卫星轨道高度约为 `35786 km`，地心距离约为 `42164 km`。但星等换算需要用的是**观测者到卫星的距离**，即 topocentric range，而不是地心距离。

对地基观测：

| 情况 | 观测者到 GEO 的距离量级 |
|---|---:|
| 卫星接近观测站正上方的理想情况 | `~35786 km` |
| 常规可见 GEO 观测 | `~3.6e4-4.2e4 km` |
| 代表性工程取值 | `40000 km` |

Schmitt (2020) 中样本要求从 Flagstaff 可观测，仰角大于约 23 deg，因此其实际观测距离属于上述地基 GEO 距离量级。文献摘要和预览页没有给每颗卫星的逐点观测距离；工程换算中取 `40000 km` 是合理的代表值。

## 3. 距离换算公式

卫星反射太阳光的接收辐照度，在其他条件不变时，与“卫星到观测者距离”的平方成反比：

```text
F ∝ 1 / Delta^2
```

星等定义为：

```text
m = -2.5 log10(F) + C
```

所以同一个目标在两个观测距离 `Delta_1` 和 `Delta_2` 下的星等差为：

```text
m_2 - m_1 = 5 log10(Delta_2 / Delta_1)
```

等价地：

```text
m_2 = m_1 + 5 log10(Delta_2 / Delta_1)
```

若从地基 GEO 距离 `Delta_ground` 换算到天基距离 `Delta_space`：

```text
m_space = m_ground + 5 log10(Delta_space / Delta_ground)
```

或写成更直观的变亮量：

```text
m_space = m_ground - 5 log10(Delta_ground / Delta_space)
```

当 `Delta_space = 100 km` 时：

```text
m_space(100 km) = m_ground - 5 log10(Delta_ground / 100 km)
```

## 4. 从 11-15 mag 换算到 100 km

用不同地基距离取值，得到的平移量如下：

| 地基距离 `Delta_ground` | 到 100 km 的星等平移量 | 地基 11-15 mag 换算后 |
|---:|---:|---:|
| `35786 km` | `12.77 mag` | `-1.77 to +2.23 mag` |
| `40000 km` | `13.01 mag` | `-2.01 to +1.99 mag` |
| `41679 km` | `13.10 mag` | `-2.10 to +1.90 mag` |

所以对于项目阶段估计，建议写作：

```text
若将地基 GEO 常规范围 11-15 mag 按距离平方反比关系换算到 100 km，代表性结果约为 -2 to +2 mag。
```

更保守一点可以写：

```text
约 -2.1 to +2.3 mag，取决于地基参考距离采用 3.6e4 km 还是 4.2e4 km。
```

## 5. 与 Schmitt (2020) 图 2 的关系

Schmitt (2020) 图 2 是 B、V、R、I 四个波段的星等分布直方图。已保存的图像支撑文件为：

```text
支撑/Schmitt_2020_figures/gr2.jpg
```

从图上读到的可见范围约为：

| Band | 地基图上直方图大致跨度 | 以 40000 km 换算到 100 km |
|---|---:|---:|
| B | `~10.6-13.8 mag` | `~-2.4 to +0.8 mag` |
| V | `~9.7-12.5 mag` | `~-3.3 to -0.5 mag` |
| R | `~9.0-12.0 mag` | `~-4.0 to -1.0 mag` |
| I | `~8.8-12.0 mag` | `~-4.2 to -1.0 mag` |

这说明 Schmitt 的样本在红波段更亮，且其 V/R/I 波段分布可能比项目采用的宽泛 `11-15 mag` 常规范围更亮。项目若需要“跨文献、跨波段、工程保守”的常规范围，继续使用地基 `11-15 mag` 再换算到 100 km 比直接使用某一篇的某一波段直方图更稳。

## 6. “随机地基数据”到“随机天基数据”的正确理解

用户当前设想是合理的，但需要写清楚假设：

1. 地基 `11-15 mag` 是许多姿态、相位角、卫星类型、材料、观测条件共同作用后的随机分布。
2. 如果天基观测也视为随机姿态/相位角样本，并且只把观测距离固定改成 `100 km`，那么可以把原随机分布整体减去约 `13 mag`。
3. 如果天基观测的相位角分布、姿态分布、太阳-目标-观测器几何、传感器波段、是否发生镜面高光与地基样本不同，那么不能只用距离平移；必须额外加入相位函数或 BRDF/姿态模型。

因此，当前 A2 阶段可以采用：

```text
Ground random apparent magnitude distribution:
m_ground ~ 11-15 mag

Assumed space-based range:
Delta_space = 100 km
Delta_ground = 40000 km

Distance-only transformed distribution:
m_space ~ -2 to +2 mag
```

## 7. 适用于后续建模的表达

建议在论文或项目说明中这样写：

```text
The reported 11-15 mag range represents ground-based apparent magnitudes of operational GEO satellites at typical topocentric GEO ranges of order 3.6e4-4.2e4 km. For a first-order space-based observation estimate at 100 km, assuming identical illumination, phase, attitude and spectral response, the apparent magnitude can be shifted by the inverse-square range correction m_100km = m_ground + 5 log10(100 / 40000). This gives a representative 100 km range of approximately -2 to +2 mag.
```

中文对应表述：

```text
文献中的 11-15 mag 应理解为地基 GEO 距离下的表观星等随机范围。若仅考虑观测距离变化，并将天基观测距离固定为 100 km，则根据亮度随距离平方反比衰减的关系，星等需整体减小约 13.0 等。因此，地基 11-15 mag 可一阶换算为 100 km 天基观测下约 -2 至 +2 mag 的常规范围。
```

## 8. 文献支持

1. Schmitt, H. R. (2020). Multi wavelength optical broad band photometric properties of a representative sample of geostationary satellites. *Advances in Space Research*, 65(1), 326-336. DOI: `10.1016/j.asr.2019.09.036`.  
   支持点：地基 B、V、R、I 多波段观测 61 颗 active GEO 通信卫星；论文目标包括 quiescent magnitude and color distribution；图 2 给出多波段星等分布。

2. Vananti, A., Schildknecht, T., & Krag, H. (2017). Reflectance spectroscopy characterization of space debris. *Advances in Space Research*, 59(10), 2488-2500. DOI: `10.1016/j.asr.2017.02.033`.  
   支持点：GEO/空间目标的地基光学反射特性观测受相位角、材料反射率和观测几何影响，说明距离换算只能处理几何距离项，不能替代 BRDF/相位建模。

3. 项目本地支撑：`支撑/Schmitt_2020_figures/gr2.jpg` 与 `支撑/Schmitt_2020_magnitude_distribution_note.md`。  
   支持点：Schmitt (2020) 图 2 的 B/V/R/I 地基星等分布坐标范围已从 Elsevier 图像资源核对。

## 9. 推荐纳入 A2 的最终句

```text
本项目将地基常规 GEO 运行卫星表观星等取为 11-15 mag。该范围来自地基光学观测，观测距离为 GEO 拓扑距离量级，即约 3.6e4-4.2e4 km。若后续转为 100 km 天基观测，并在一阶估算中保持相同太阳照明、相位角、姿态分布、BRDF 和通带，仅改变观测距离，则按 m_100km = m_ground + 5 log10(100/40000) 换算，目标约变亮 13.0 等。因此，100 km 天基观测下的常规范围可暂估为约 -2 至 +2 mag。该结果是距离归一化估计，不是独立天基实测统计；后续若几何分布改变，应引入相位函数和姿态/BRDF 模型修正。
```

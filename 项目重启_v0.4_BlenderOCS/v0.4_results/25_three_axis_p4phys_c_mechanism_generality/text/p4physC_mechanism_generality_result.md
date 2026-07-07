# P4-PHYS-C 机制普遍性检验结果

固定几何 phase63/L1-G1；候选池 n=159；机制签名复用 24 包口径（逐像素 rel_diff<1e-4）。

## 1. near_specular_metal 是否集中于高亮 top 分位

是，强富集。全池 base rate=15.7%（25/159）。

| 分位 | n | near_specular 数 | 占比 | 富集倍数 |
|---|---|---|---|---|
| top 10% | 16 | 16 | 100% | ×6.36 |
| top 25% | 40 | 24 | 60% | ×3.82 |
| 全池 | 159 | 25 | 15.7% | ×1 |

top-10% 全部满足 near_specular_metal；其余候选中仅 9 个满足（6.3%）。

## 2. 不满足 near_specular_metal 的候选是否系统性更暗

是。

| 组 | n | mean OCS | median OCS | max OCS |
|---|---|---|---|---|
| near_specular=1 | 25 | 0.2017 | 0.2016 | 0.2089 |
| near_specular=0 | 134 | 0.0630 | 0.0301 | 0.1993 |

near_specular=1 组均亮度是 near_specular=0 组的 3.2 倍；相关性 corr(OCS, reflect_vs_det)=−0.80、corr(OCS, pct_NoH≥0.99)=+0.95。

## 3. R4 与 top-1 是否属于同一高亮机制簇

是。R4（yaw=147.5,pitch=12.5,roll=0）`near_specular_metal=1`，与 top-1 同为金属主体近镜面对齐探测器。R4 的镜面对齐甚至略优（见 24 包对照）。

## 4. top-1 超过 R4 的隐身板增量在其它高亮候选中是否可复现

**可复现，但绑定 R1 roll+15 亮簇，不是 top-1 独有，也不普遍到全部高亮候选。**

高亮候选（OCS≥0.18，n=49）隐身板贡献：

| 子组 | n | mean dark_contrib | median dark_contrib | 满足 dark_panel_increment 比例 |
|---|---|---|---|---|
| 全部高亮 | 49 | 0.00682 | 0.00872 | 75.5% |
| roll+15（R1 型） | 23 | 0.00839 | 0.00873 | 95.7% |
| 其它 roll | 26 | 0.00542 | 0.00869 | 57.7% |

关键事实：

- top-1 隐身板 0.00877，与 roll+15 亮簇中位 0.00873 几乎相同——**top-1 的隐身板增量不是个例，而是 R1 roll+15 亮簇的共同特征**。
- R4（roll=0）隐身板仅 0.00093，是高亮候选中**缺少**该增量的一方；因此“top-1 > R4”应写成**排序增量**：R4 是恰好缺隐身板受照面的高亮候选，而非 top-1 具备独特机制。
- 其它 roll 的高亮候选 median 也达 0.0087，但均值被少数低隐身板样本拉低，故非 100% 满足。

## 5. 结论

- 金属近镜面机制（near_specular_metal + strong_surface_highlight）**普遍**解释固定几何下的高亮：MECHANISM_GENERALITY 在金属通道上成立。
- 隐身板增量**不是普遍高亮机制**，而是 R1 roll+15 亮簇的伴随特征，用于解释 top-1 相对 R4 的排序，不能上升为独立高亮机制。
- 据此裁决：**PARTIAL_GENERALITY**。

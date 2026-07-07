# P4-PHYS-C 机制普遍性检验计划（E 子任务接口）

本文件只给出 top-1 机制签名 seed 和 P4-PHYS-C 的检验设计草案，不启动任何 P4-PHYS-C 统计、不扩展 sun/view、不训练。

## 1. top-1 机制签名 seed（见 tables/p4physB_mechanism_signature_seed.csv）

| 签名字段 | top-1 取值 | 类别 |
|---|---|---|
| dominant_part | jinshuzhuti（金属主体，95.0%） | 直接 |
| dominant_material_proxy | B0 金属 rho_s=0.60,n=80 高镜面 | proxy |
| second_part | yinshenban（隐身板，4.2%，增量来源） | 直接 |
| sun_normal_angle_bin | ~31°（加权金属法向 vs 太阳） | 直接 |
| view_normal_angle_bin | ~32°（加权金属法向 vs 探测器） | 直接 |
| reflection_alignment_proxy | avgN_vs_H=0.57°（近镜面对齐） | 直接/几何 proxy |
| saturation_state | saturation_flag=1, glint_flag=0（面状近饱和） | 直接（来自 23A topN） |
| mean_specular_term (N·H)^80 | ~0.81（金属贡献像素） | 直接 |

机制一句话签名：
> **金属主体大面元法向近乎对齐半程向量（N·H≈0.998，反射方向偏探测器约1°），产生面状近镜面/近饱和高亮；roll 相关的隐身板附加受照面提供决定性微弱增量。**

## 2. P4-PHYS-C 应如何检验同类机制是否普遍高亮

建议（不在本轮执行）：

1. **签名量化**：对候选姿态计算同一组签名量（dominant_part、加权金属 N·H、反射-探测器夹角、(N·H)^n 均值、saturation_flag）。
2. **检验对象**（复用已有包，不新渲染）：
   - 23A/23B refined top-N（R1 加密邻域）；
   - R4 鲁棒亮区 roll profile；
   - 旧 22 号包 C01–C09 只作辅助回接；
   - R3/R2/R5 作负面/暗对照。
3. **判据**：
   - 若高亮候选普遍满足"金属 N·H≥~0.99 高占比 + 反射方向近探测器"，则确认为一类近镜面高亮机制，给出机制物理句。
   - 若不普遍（高亮来自不同部件/不同角度组合），则说明 top-1 是局部 roll 尖峰或 saturation-associated 峰，不能升级为普遍机制。
4. **隐身板增量假设**：单独检验"金属近镜面持平时，隐身板附加受照面是否系统性决定 top 排序"，判断增量来源是否可复现。

## 3. 边界

- 本轮只提供 seed 与计划，未做机制普遍性统计。
- 机制签名基于固定 phase63/L1-G1，不代表其它 sun/view。
- material 层仍为 proxy；若 P4-PHYS-C 需材料级区分，需先补 material pass（见 next_step 建议）。

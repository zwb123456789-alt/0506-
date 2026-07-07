# P4-PHYS-C 可主张与不可主张（claim boundary）

固定几何 phase63/L1-G1；候选池 n=159；material 层为 B0 proxy。

## 可主张（direct / 统计支持）

1. 在 fixed phase63/L1-G1 下，金属主体近镜面对齐探测器（`near_specular_metal`）是高亮候选的**普遍机制**：top-10% 100% 满足，富集 ×6.36；满足组均亮度 0.2017 vs 未满足组 0.0630。
2. 不满足近镜面机制的候选**系统性更暗**（corr(OCS, reflect_vs_det)=−0.80）。
3. top-1 与 R4 属**同一高亮机制簇**（都是金属近镜面）。
4. per-part OCS、贡献像素、法向/半程向量夹角、反射-探测器夹角、NoH 分布为**直接计算**（逐像素与 ocs.json 一致 rel_diff<1e-4）。

## 不可主张（proxy / 局部 / 未证）

1. **不可**把隐身板增量写成普遍高亮机制。它绑定 R1 roll+15 亮簇；top-1 > R4 是**排序增量**（R4 恰好缺隐身板受照面），非 top-1 独有机制。
2. **不可**把 material-level 写成真实 material attribution：仅 B0 参数级 proxy，无 material pass。
3. **不可**外推到其它 sun/view：本结论仅限固定 phase63/L1-G1。
4. **不可**写成全局最亮机制 / 真实目标反演 / 观测规划最终结论。

## 结论标签

**PARTIAL_GENERALITY**：金属近镜面机制普遍解释固定几何高亮；隐身板增量仅解释 top-1 相对 R4 的排序。

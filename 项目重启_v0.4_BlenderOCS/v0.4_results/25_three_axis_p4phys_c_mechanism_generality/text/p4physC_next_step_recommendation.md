# P4-PHYS-C 下一阶段建议

裁决：**PARTIAL_GENERALITY**（金属近镜面机制普遍；隐身板增量仅解释 top-1 相对 R4 排序）。

按 R151 §5E 与 Codex 预设倾向（PARTIAL_GENERALITY 可接收并进入 sun/view 扩展前阶段门），建议：

## 首选：进入 P4-PHYS-D sun/view 扩展前阶段门

- 当前金属近镜面机制在固定 phase63/L1-G1 已稳定为普遍高亮机制；自然的下一问是该机制在其它 sun/view 是否仍成立、最亮姿态是否随几何迁移。
- 该步需要新渲染或至少新几何 postprocess，**属独立阶段门**，本轮不启动，交 Codex 裁决放行。

## 可选增强（非阻塞）：material pass / material-ID

- 当前 material 层仅 B0 proxy。隐身板增量的物理归因（是否真为低反射隐身涂层的掠射受照）无法在 proxy 下定论。
- 若后续要把隐身板增量写成 material-level 结论，需 material pass；本轮明确列为**可选增强，不自行启动**（R151 §2）。

## 不建议

- 不建议回退补充机制候选池：本轮 n=159 已覆盖 top-1/R4/R3、23A/23B topN、P3/P2 全区与明暗对照，近镜面机制与暗组分离已很清晰，补池边际收益低。

## 一句话交接

金属近镜面对齐机制已在固定几何被证为普遍高亮机制；隐身板增量为 R1 亮簇伴随特征而非独立机制。建议 Codex 据 PARTIAL_GENERALITY 放行 P4-PHYS-D sun/view 扩展阶段门，material pass 作为可选增强候选。

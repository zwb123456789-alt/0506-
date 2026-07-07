# P1 seed-roll scan smoke —— 可解释摘要（p1_seed_roll_smoke_summary）

最后更新：2026-07-01
性质：R131 P1 seed-roll scan smoke 结果解读。**smoke 级观察，不是三轴小项目结论，不是最优反演姿态判定。**
几何：phase63 / L1-G1；roll ∈ {-60,-45,-30,-15,0,15,30,45,60}，roll=0 复用 `01_fullrun`，8 个非零 roll 新渲染，共 96 渲染单位 + 12 baseline。

## 1. P1 smoke 链路是否跑通

跑通。8×12 = 96 个非零 roll 渲染单位全部 RENDERED（每 roll 批次 12/12），96 个后处理单位全部 COMPLETE，OCS/图像非空，roll=0 baseline 全部对齐（12/12）。每个 seed 的 OCS(roll)、local_contrast(roll)、roll_sensitivity 曲线均可计算并出图。

## 2. 最亮点是否随 roll 迁移

在当前 12 seed 内，最亮构型基本**不随 roll 迁移**：
- bright-seed（yaw145/150,pitch+15）与 robust-easy-seed（yaw150,pitch+10）OCS 随 roll 变化极小（相对幅度 5–7%），亮度排名漂移 ≤1，稳居前列（rank 1–3）。
- 说明在 phase63 下，靠近入射-观测有利区、低 |pitch| 的亮构型对 roll 稳健，这与 fixed-roll 主线的“亮构型”判断一致，roll 未推翻其亮度地位。

## 3. 是否出现“亮但不高信息”或“暗但变化敏感”的例子

出现，且清晰：
- **亮但低信息**：bright-seed / robust-easy-seed 亮度排名前 3，但 local_contrast 排名垫底（10–12），且触发 saturation_flag。即最亮姿态图像对比低、有饱和风险。
- **暗但对比高**：dark-seed（yaw285,pitch-70）、image-hard-seed（yaw165,pitch-20）亮度排名末位（10–12），但 local_contrast 排名靠前（3–4）。
- **暗但 roll 敏感**：high-info(yaw240)、low-info/ocs-hard(yaw065)、dark(yaw285,pitch-70)、roll-sensitive(yaw285,pitch-85) 的 OCS 随 roll 相对变化达 100%–360%，亮度排名漂移最大到 7。high-info-seed 在 roll+15 出现约 +200%~+290% 的 roll-induced brightening。
- 因此 smoke 层面已支持 18 号包的核心边界：**最亮 ≠ 最高信息**；brightness 与 information（此处用 contrast 代理）在多个 seed 上解耦。

## 4. 哪些 seed 类别值得进入 P1 正式或 P2

- 高价值（roll 方向信息丰富，值得进入 P2 sparse grid 或 P1 正式）：high-info-seed（yaw240 系）、low-info/ocs-hard（yaw065 系）、dark/roll-sensitive（yaw285 系高 |pitch|）——这些在 roll 上呈现强变化与排名漂移，是三轴“高信息 / 低信息 / 敏感区”候选。
- 对照价值（roll 稳健，正对照）：bright-seed、robust-easy-seed——保留作稳定参照。
- image-hard-seed 在 clean/P-INT 下天然稀少（仅 2 个候选），smoke 已确认其“暗但对比高”特征，后续按需在退化路线扩充。

## 5. 是否需要调整后续三轴采样计划

smoke 未发现需要推翻 18 号采样计划的问题。两点建议供 Codex 裁决：
1. P2 sparse grid 可优先在 high-|pitch|（|pitch|≥70）与 yaw≈240/285 邻域加密，这些区域 roll 敏感、信息变化大。
2. 局部对比（contrast）作为 smoke proxy 有效，但正式阶段应替换/补充为 P-DB/margin/entropy 等需模型的可分性指标（当前 P1 不训练，未计算）。

## 6. 红线自持

本轮只做 phase63 单几何、96 单位 smoke，未训练、未启动 P2/P3/P4、未启动 R128、未改旧目录 10–18、未写成果区、未改 CLAUDE.md。所有 information proxy 仅 smoke 级，最亮姿态未写成最优反演姿态，不构成真实反演系统声明。

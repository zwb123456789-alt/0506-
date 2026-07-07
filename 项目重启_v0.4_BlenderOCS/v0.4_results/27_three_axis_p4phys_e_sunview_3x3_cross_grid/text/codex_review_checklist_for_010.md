# 010 / 27 包 Codex 审阅检查单

## 存在性
- [ ] 27 包存在，audit/tables/figures/text/scripts/logs/postprocess 齐全
- [ ] 010 报告存在于 02_Claude输出/
## 设计
- [ ] 几何=9（3×3），姿态=14（复用同源 14），组合=126，新增渲染=0
- [ ] camera EXR←view_offset、sun EXR←sun_offset 的复用映射写明；EXR 全部可达
## 执行
- [ ] 126/126 postprocess COMPLETE
- [ ] 5 锚点组合复现 26 包 G0–G4：70/70 OK，max rel_diff=0.0e+00
- [ ] 机制签名复用 24/25/26 口径，H 随组合几何取值；一致性 126/126，max rel_diff=1.4e-07
## 结论（关键：非平凡结果）
- [ ] 全表最高 = Hsp_vm/C_R3（R3_negative）OCS=0.22556 > baseline A_top1 0.20889
- [ ] 全表最高位于组合角落、由负对照 R3 领先、脱离 top-1 roll 邻域簇
- [ ] 逐几何最亮 8/9 在 top-1 roll 邻域簇；R4/R3 对照在反对角失稳
- [ ] 裁决标签 = NEED_LOCAL_STEP_REFINEMENT，证据链清楚
- [ ] 未写成全局 sun/view 结论；material 仍标 proxy
## 红线
- [ ] 不训练/不 R128/不路线二三四/不全 sun/view 全姿态搜索/不新增渲染/不新增姿态
- [ ] 不改 20/21/23A/23B/24/25/26 源包/不写成果区/不改 CLAUDE.md/不生成 Codex 文件
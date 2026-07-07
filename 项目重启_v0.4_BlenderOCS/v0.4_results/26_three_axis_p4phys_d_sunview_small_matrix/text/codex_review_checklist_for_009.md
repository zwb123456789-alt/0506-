# 009 / 26 包 Codex 审阅检查单

## 存在性
- [ ] 26 包存在，8 子目录齐全
- [ ] 009 报告存在于 02_Claude输出/
## 设计
- [ ] 几何数=5（≤5），姿态数=14（≤16），新增渲染=56（≤80）
- [ ] sun/view 几何角距 baseline=7°（5–10° 区间），坐标口径与归一化写明
- [ ] 姿态全部来自既有渲染，无新姿态搜索
## 执行
- [ ] smoke 先行且通过（G3×top1/R4/R3），再跑正式矩阵
- [ ] 渲染复用物理正确：sun 扰动复用 camera EXR、view 扰动复用 sun EXR
- [ ] G0 baseline 逐像素 OCS 复现既有 ocs.json（rel_diff≈0）
- [ ] 机制签名复用 24/25 口径，H 随几何取值；跨几何一致性 70/70 OK，max rel_diff<1e-4
## 结论
- [ ] 跨几何 OCS 表、top-1 稳定性表、机制签名表、2 图齐全
- [ ] 裁决标签 = SUNVIEW_DEPENDENT_BUT_MECHANISTIC，证据链清楚
- [ ] 未写成全局 sun/view 结论；material 仍标 proxy
## 红线
- [ ] 不训练/不 R128/不路线二三四/不改源包/不写成果区/不改 CLAUDE.md/不生成 Codex 文件
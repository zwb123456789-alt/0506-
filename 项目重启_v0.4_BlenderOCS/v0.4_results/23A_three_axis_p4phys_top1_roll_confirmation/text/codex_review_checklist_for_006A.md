# Codex 审阅检查表（006A）

## 最低接收验证

- [x] 23A 包存在（v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/）
- [x] 006A 报告存在
- [x] current sampled-grid top-1/top-N 明确：yaw=245.0, pitch=30.0, roll=+15, ocs=0.208377
- [x] R1/R4 roll profile 明确（见 tables/p4physA_*_roll_profile.csv）
- [x] 局部加密触发门有数值判断（4门均触发）
- [x] 触发加密：已完成受控加密 75新渲 + 14复用 = 89点，全批 FAILED=0
- [x] refined top-1 有明确结论：yaw=245.0, pitch=27.5, roll=+15, ocs=0.208890
- [x] 下一轮光路归因字段可行性已预检（EXR已含IndexOB/Normal/Depth/Position）
- [x] 红线自检通过

## 强接收核查

- [ ] 加密后 top-1 位于非边界点，可直接作为 P4-PHYS-B 归因对象
  → **否**：pitch=27.5 是 pitch 下边界，需追加 pitch∈{22.5,25.0} 一小圈后确认
- [x] 明确说明 R1 top 峰与 R4 鲁棒亮区的角色（R1: saturation-associated sharp peak; R4: roll-robust broad bright region）
- [x] 明确回答是否还需要继续遍历 roll：roll=+15 在 roll 方向已是内部点，不需要继续；需沿 pitch 方向追加边界点
- [x] 给出 P4-PHYS-B 的最小诊断姿态集与字段/pass 需求（见 text/p4physA_next_physical_attribution_plan.md）

## 注意事项

- refined top-1 已从 pitch=30.0 迁移到 pitch=27.5（pitch 下边界），差值 0.246%
- pitch 边界追加规模极小（2~6 个姿态），建议直接在 23A 包内追加
- P4-PHYS-B 光路归因所需字段已基本就位（IndexOB/Normal/Depth/Position 已在 EXR 中）

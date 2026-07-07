# Codex 审阅清单 for 002（codex_review_checklist_for_002）

最后更新：2026-07-01
对象：R131 P1 seed-roll scan smoke —— 19 号包 + 002 执行报告
上游：R130 通过 001 并放行 P1 smoke；R131 任务单

## 完成度核验点

- [ ] 19 号包目录结构完整：audit/render/postprocess/metrics/figures/tables/text/scripts/logs。
- [ ] locked run matrix = 96 行，12 seed × 8 非零 roll，几何 phase63/L1-G1。
- [ ] 96/96 渲染单位完成（camera 96 + sun 96 = 192 EXR）。
- [ ] 96/96 后处理完成（ocs.json 96 + linear.exr 96）。
- [ ] roll=0 baseline 12/12 来源 01_fullrun，未重渲。
- [ ] OCS total 全部有限且 > 0。
- [ ] roll 曲线 108 行（含 baseline）可计算。

## 指标与结论核验点

- [ ] `p1_metric_definitions_used.md` 口径合理，contrast 明确标注为 smoke proxy。
- [ ] roll_sensitivity_score、rank_shift、glint/saturation flag 计算一致。
- [ ] 结论区分 brightness 与 information，最亮姿态未写成最优反演姿态。
- [ ] summary 的 5 问均回答：链路跑通 / 最亮点是否迁移 / 亮但低信息与暗但敏感例子 / 值得进入 P2 的类别 / 采样计划是否调整。

## 红线核验点

- [ ] 只 phase63 单几何、96 单位、未训练、未启动 P2/P3/P4/R128。
- [ ] 未改旧脚本、未改旧目录 10-18、未改姿态网格/OBS_GEOMETRIES/split/backbone/超参。
- [ ] 输出仅 19 号包 + 002 报告；未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md。

## 待 Codex 裁决

1. 002 P1 smoke 是否通过。
2. 是否放行 P1 正式扩展或 P2 sparse 3-axis grid。
3. 是否需要修正 seed 类别或采样计划（本轮建议在高 |pitch|、yaw~240/285 邻域加密）。
4. 是否认可“最亮构型 roll 稳健但低信息 / 高 |pitch| 暗构型 roll 敏感”作为最亮/高信息/低信息区早期证据。
5. information proxy 是否需在正式阶段升级为 P-DB/margin/entropy（需模型）。
6. R128 是否继续挂起到三轴小项目完成后再回看。

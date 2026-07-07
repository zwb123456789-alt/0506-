# codex_review_checklist_for_011

- [ ] 28 包目录完整（audit/render/postprocess/tables/figures/text/scripts/logs）
- [ ] smoke 通过后才执行正式矩阵（logs/p4physF_smoke_render.log + smoke_metrics）
- [ ] 新增渲染 76 units ≤ 80（52+24；logs cumulative=76）
- [ ] Stage1 最高点、边界标注、C_R3/A_top1 对比（stage1_best_summary）
- [ ] Stage2 microgrid 最高点与几何边界标注（stage2_top_candidate_summary）
- [ ] 27 包 Hsp_vm 锚点一致性 5/5（postprocess 记录 anchor_rel_diff=0）
- [ ] 逐像素机制重算一致性 79/79 max_rel=1.2e-07（numeric_consistency_check）
- [ ] 机制签名含 R157 扩展诊断（weighted_NoL/NoV/NoL_NoV）
- [ ] 建议标签三选一：NEED_SECOND_STEP_REFINEMENT
- [ ] 红线自查 10/10 PASS；claim boundary 表存在
- [ ] 011 报告存在于三轴路线 02_Claude输出/，未写成果区、未改 CLAUDE.md

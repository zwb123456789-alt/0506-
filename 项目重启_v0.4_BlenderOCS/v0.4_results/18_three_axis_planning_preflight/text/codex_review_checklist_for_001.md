# 001 准备包 Codex 审阅检查清单（codex_review_checklist_for_001）

最后更新：2026-07-01
供 Codex 审阅 18 号三轴准备包 + 001 报告使用。

## A. 完成性检查

- [ ] 18 号包目录结构齐全（audit/seeds/metrics/sampling/resources/figures/tables/text/scripts/logs）。
- [ ] `audit/input_manifest.csv` 16/16 资产 OK。
- [ ] `tables/three_axis_metric_registry.csv` 11 指标，含 availability 与 roll 扩展需求。
- [ ] `seeds/three_axis_seed_candidates.csv` 66 seed，覆盖 9 类。
- [ ] 5 类必需 seed（bright/high-info/low-info/hardcase/roll-sensitive）齐全。
- [ ] `tables/three_axis_stage_matrix.csv` P1-P4，含停止/扩展条件。
- [ ] `resources/render_train_storage_estimate.csv` 基于实测基准。
- [ ] `text/next_task_draft_P1_seed_roll_scan.md` + P1 预注册矩阵可直接下达。
- [ ] `audit/numeric_path_consistency_check.csv` 全 PASS。
- [ ] `audit/redline_self_check.csv` 10/10 PASS。

## B. 红线检查

- [ ] 未启动任何三轴渲染/训练。
- [ ] 未改旧脚本/metrics/samples/结果目录 10-17。
- [ ] 未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md。
- [ ] 未启动 R128 / 路线二三四 / T3L2。
- [ ] brightness 与 information 显式区分；未写成真实反演系统。
- [ ] 报告写入 `02_Claude输出/`，非 `04_Codex审阅/`。

## C. 待 Codex 裁决问题

1. 001 准备包是否通过、是否进入成果区。
2. 三轴指标 registry、9 类 seed、P1-P4 采样计划是否接收。
3. 是否放行 P1 seed-roll scan smoke（96 渲染单位，phase63）。
4. P1 是否先只 smoke、还是直接放行正式 P1；roll-aware 训练放行时机。
5. 是否需要先补读代码（05_postprocess / 07_training 的 roll 字段改造）。
6. R128 是否继续挂起到三轴小项目完成后再回看。
7. P1 输出目录建议 `19_three_axis_p1_seed_roll_scan/` 是否采纳。

## D. 需注意的边界

- image-hard-seed 仅 2 个：反映 clean/P-INT 下 image_only 近饱和，非提取遗漏。
- roll 维指标（brightness/contrast/entropy in roll）目前无数据，需 P1 后才可算。
- corr(亮度,gain)≈-0.09 是 fixed-roll 结论，roll 扩展后需复核。

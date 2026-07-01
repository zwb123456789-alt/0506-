# R117 Codex 审阅：104 通过，L1M3 退化真实性与 M-roll 边界探针接收

最后更新：2026-07-01  
审阅对象：`02_Claude输出/104_1C-L1M3Mroll_退化真实性与roll边界探针_Claude执行报告.md`  
结果目录：`v0.4_results/12_l1m3_degraded_mroll/`  
上游阶段门：R115 已通过 L1(M2) clean / P-INT 第一阶段

## 1. 审阅结论

104 按 R116 完成 A/B/C/D 四组任务，证据链、路径分流和红线自查均合格，Codex 判定为：**通过，进入路线一 C 当前主用成果区。**

本次通过的性质是：补齐 R115 审计缺口，并接收 L1(M3) degraded 真实性轴、M-roll fixed-roll 边界探针、D3/P-DB/conformal 准备材料。它**不是**路线一 C 整体闭口，不触发头A/头B大合并裁决，不启动 T3/L2、三轴小项目、路线二/三/四扩展，也不把 P-EXT yaw-block 写成已解决。

## 2. 接收证据

1. R115 val per-attitude 缺口已补齐。`audit/l1m2_val_samples_recovery_summary.csv` 显示 12 个正式 run 均 `split_size_match=True`、`flux_transform_match=True`，final/best 的 `cmae_delta=0.0`，可视为等价恢复，不需要重训。
2. 跨几何量纲一致性通过。`audit/l1m2_geometry_scale_consistency.md` 与 `l1m2_transform_leakage_check.json` 显示 pixel area、ortho scale、depth epsilon、resolution 一致；z-score 仅由 train 拟合；train/val/test 无 attitude 交集；G1/G3/G5 attitude 嵌套与 yaw/pitch 对齐成立。
3. degraded 真实性轴通过。`degraded/l1m3_degraded_gain_and_drop_summary.md` 显示 OCS-only best 口径下 G1->G3->G5 单调增益在 clean、mild、moderate 均保持：G5 相对 G1 的 yaw cMAE 增益为 53.79°, 48.95°, 40.02°。
4. M-roll 边界探针通过。`mroll/mroll_roll_sensitivity_summary.md` 显示在 phase63、312 分层子集、image_only、clean roll-0 模型 zero-shot 条件下，±15° roll 未直接推翻 fixed-roll 结论，±30° roll 已明显侵蚀。
5. D3/P-DB/conformal 准备通过。`d3/l1m3_confidence_inputs_index.csv` 共 104 行；`pdb_template_retrieval_smoke.csv` 中 neg-L2 top-1 yaw hit@30=0.949；`conformal_smoke_summary.md` 给出 val/test 分离的 split-conformal smoke。

## 3. 五个裁决问题

Q1 degraded 口径：接收“多几何 OCS 增益在本轮物理退化下保持，并随退化强度优雅收缩”。不得写成真实观测验证或 operational robustness。image/joint 在 best-val 口径下仍近饱和，但 final 口径存在 G5 joint moderate hit@30=0.189 的检查点选择敏感性，因此 joint 强互补性仍不成立。

Q2 M-roll 口径：接收其为 fixed-roll 边界探针。结论只能写为“在本轮 image_only 子集 zero-shot distribution-shift 设置下，±15° 稳健、±30° 敏感”。不得写成 roll-aware 训练完成、三轴姿态反演完成或真实未知目标 roll 可反演。

Q3 M-roll 成本裁剪：接收 image_only 子集探针 + full-2664/joint 成本估算作为本轮收口。joint/full-2664 M-roll 留作按需扩展，不作为 R117 通过条件。

Q4 P-DB：接收为强 smoke 证据，说明 L1-G5 多观测总光度向量含有可检索 yaw 信息；可在后续升格为正式 D3/P-DB 分支。但当前不得写成真实反演成功率，也不得替代神经回归主结果。

Q5 val 恢复：接收“checkpoint + deterministic split 重建 + ΔcMAE=0.0”作为等价 val per-attitude 输出，可用于后续 D3/conformal，不需要重训。

## 4. 后续边界

R117 后，路线一 C 已拥有三条当前主用正结果链：R113 single-frame 负结果收口、R115 clean/P-INT 多几何 OCS 正结果、R117 degraded/M-roll/D3 准备。下一步应在 Codex 另行裁决后选择：正式 D3/P-DB/conformal、P-INT-hard 或更强 degraded 用于检验 image/joint 互补性，或先整理 Results 非正文证据包。未下达新阶段门前，不自动启动三轴小项目、T3/L2 光变正式训练或论文正文改写。

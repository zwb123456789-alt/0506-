# R123 Codex 审阅：107 通过，路线一 C Results/SI 图表与写作准备包接收

最后更新：2026-07-01  
审阅对象：`02_Claude输出/107_1C-ResultsSI图表与写作准备包_Claude执行报告.md`  
结果包目录：`v0.4_results/15_route1c_results_si_preparation_pack/`  
上游阶段门：R121 已通过路线一 C 阶段性 Results 非正文证据包

## 1. 审阅结论

107 按 R122 完成路线一 C Results/SI 图表与写作准备包，主图、SI 图表、受控 Results 草案、数字核验、manifest 与红线自检均达到接收标准。Codex 判定为：**通过，15 号包升级为路线一 C 当前主用写作准备成果。**

本轮接收的是写作准备包，不是最终论文正文、投稿摘要或路线一 C 整体闭口；不放行新训练、新渲染、T3/L2、三轴小项目或路线二/三/四扩展。

## 2. 接收证据

1. 主图包接收。Fig.1-Fig.5 均输出 PNG+PDF，source map 完成；Fig.1 明确标注 simulated only / no real telescope / no real GEO attitude truth；Fig.5 保留 P-EXT 坍缩、joint 天花板/检查点敏感、neural margin 弱、image_only 欠覆盖等负向观察。
2. SI 包接收。SI-1 至 SI-4 新绘，SI-x1/x2 复用 R119 图，SI-5 manifest 表完成；所有 SI 均绑定 source path 与 forbidden reading。
3. 受控 Results 草案接收。`text/results_candidate_draft_controlled.md` 含 R0-R5 六段，每段绑定 claim、evidence path、figure/table、allowed/forbidden 与 risk tag；R3 标为 medium 风险，R4 负向观察独立成段。
4. 数字核验接收。`audit/numeric_consistency_check.csv/.md` 共 33 项，PASS=33、CONFLICT=0；关键数字均可追溯到 10/11/12/13 原始 CSV。
5. 路径与图像核验通过。`generated_files_manifest.csv` 共 36 个本轮文件，Codex 实测缺失 0；11 张 PNG 尺寸正常且非空。
6. 红线自检通过。RL1-RL10 全部 PASS；脚本为本轮新文件，仅读既有结果并写入 15 号包，未改旧脚本、旧 metrics、旧 samples 或旧结果目录。

## 3. 裁决问题

Q1 Fig.2/Fig.3 clean 数据口径：接收当前口径。`l1m2_pint_vs_pext_ocs_only.csv` 的 P-INT 行与 R115 主数字一致，可作为 Fig.2/Fig.3 的 clean 来源；正式论文制图时可在方法或 source map 中注明它是 R115 clean/P-INT ocs_only 汇总表。

Q2 P-DB 检索口径：接收 neg-L2 + matched-degraded + test 作为当前主图口径。zscore-neg-L2 / clean-template 可留作 SI 或方法补充，不要求本轮返工。

Q3 conformal 口径：接收 α=0.10 best 作为主图口径；α=0.05/0.20 敏感性不是本轮必需项，若后续正式投稿前需要，可作为轻量 SI 补充任务。

Q4 受控草案使用：接收为下一轮正式 Results 段落的输入草案，但尚不是最终正文。正式正文仍需作者/Codex 按投稿目标进一步润色，并保留 seed=42、多 seed/fold 未补的限制说明。

Q5 成果区升级：同意。15 号包作为 Results/SI 图表与写作准备成果进入 `01_成果区/00_当前主用成果/09_路线一C-ResultsSI图表与写作准备包_R123通过.md`；包本体仍保留在 `v0.4_results/15_route1c_results_si_preparation_pack/`。

Q6 coverage 记法：裁定以后以复算值为准。image_only clean α=0.10 conformal coverage 写为 G1/G3/G5=0.892/0.865/0.835，概述可写 `≈0.83-0.89，低于 target=0.90`。14 号骨架中的 `≈0.83-0.85` 视为较窄旧记法，不影响“欠覆盖”结论；后续正式写作与图表统一使用复算区间。

## 4. 后续边界与下一步

R123 后，路线一 C 已具备一套可审阅的 Results/SI 写作准备材料：R113/R115/R117/R119/R121 的证据链已被组织为主图、SI、受控 Results 草案、数字核验和红线清单。

下一步可在两类方向中选择：

```text
Option A2：由 Codex/作者把 15 号包推进为正式 Results 段落与论文图表版本，仍不新增实验；
Option B/C：若优先补强互补性或 roll 边界，则另行下达 degraded-severe / P-INT-hard 或 joint/full-2664 M-roll 阶段门。
```

仍不得写成：路线一 C 整体闭口、真实未知目标姿态反演成功、真实望远镜验证、P-EXT yaw-block 已解决、joint 强互补性已证明、P-DB 真实观测成功率、conformal 最终概率校准、三轴小项目已启动。

# Claude 投稿定稿交互总览

> 最后更新：2026-06-05  
> 当前阶段：v0.3 主稿润色版已生成；本轮完成 Fig. 1-6 投稿级制图（含 EMF/CSV）  
> 当前指导文件：`01_v0.2_Acta_ASR主投优先版_Claude指导.md`  
> 输出路径：`Claude输出/01_Claude输出_v0.2_Acta_ASR主投优先版.md`（已生成）

## 0b. 本轮完成情况（2026-06-05，制图）

Claude 已完成 v0.3 主稿配套的 Fig. 1-6 投稿级制图，脚本 `figures/make_figures.py`（在已有草稿基础上审改升级），一次跑通无 cross-check 失配。

产物（`论文写作/03_投稿定稿/figures/`）：

```text
Fig_1_pipeline / Fig_2_geometry / Fig_3_ocs_heatmaps / Fig_4_robustness
/ Fig_5_sensitivity / Fig_6_stress_tests
  └ 每图四格式：.pdf(矢量,fonttype42) .svg(可编辑文字) .png(600dpi) .emf(LibreOffice 转换)
source_data/Fig_3..6_*.csv  ← 每张数据图的绘图值（Origin 重绘/审计）
FIG#_*.pdf / .png            ← 旧草稿链接兼容别名
FIGURE_NOTES.md              ← 脚本自动重写（数据源/校验/缺漏）
```

本轮相对旧脚本的升级：① 输出从 pdf+png(300) 扩到 pdf+svg+png(600)+emf 四格式 + 每图 CSV；② `svg.fonttype=none` 保证 AI/Inkscape 可编辑文字；③ EMF 经 LibreOffice headless（`soffice --convert-to emf`）转换，环境无 Inkscape；④ 排版对齐 FIGURE_SPEC.md（7pt 正文/6pt 标注/9pt panel/0.5pt 轴线）。

红线落地（全部保持）：
- Fig. 3 遮挡率措辞严格区分 phase63 逐格 19.3-97.1% 与五几何均值 60.1-78.5%（已在 SPEC 与脚本注释写死）。
- Fig. 4a clean-trained image-only 高斯噪声系列无落盘数据，仅画 clean 点 + `*` 标注；崩溃证据放 Fig. 6a/6b 真实数据。
- Fig. 5b BRDF roughness 原始数据缺失，仅出 representative bar + `*summary values` 标注。
- 6.58°（12f 内部重训参照）与主线 5.91° 在脚本与 CSV 中分列，不混淆。
- 全程无任何编造数值；每个绘图值可溯源至 `补充实验/结果/` 或模块 A/C 产物。

待办：将 6 张图按主稿 caption intent（v0.3 L91/109/195/288/314/345）插入主稿对应图位；EMF 视觉需作者在 PPT 端复核一次（LibreOffice 转换的字体回退）。

## 0. 本轮完成情况（2026-06-05）

Claude 已一次性整合 07 + 07b + 07c，生成第一档 Acta/ASR 主投优先版 v0.2 完整候选稿，输出文件：

```text
Claude输出/01_Claude输出_v0.2_Acta_ASR主投优先版.md
```

候选稿包含：A 完整正文（标题→Abstract→Introduction→Related Work+Table 1→Method 3.1-3.11→Results 4.1-4.7→Discussion 5.1-5.6→Conclusion→Data/Author/Funding/COI/References）；B 整合说明（07/07b/07c 如何进入正文）；C 表/图更新清单（主文新增 Table 4/5/6、Fig. 4/6，建议 Supplementary S1-S6）；D 红线逐条自检；E 占位清单。

相对 v0.1 的主要改写：
- Results 重排为 4.4 Clean-image fusion and modality dominance / 4.5 Degradation-aware fusion and modality-isolation controls / 4.6 Ablation and sensitivity / 4.7 Synthetic observation-style degradation and cross-geometry sanity tests。
- Methods 新增 3.9 融合机制诊断与退化感知训练、3.10 合成观测风格压力测试、3.11 split/great-circle/sin-cos/train-only 标准化；3.3/3.7 补 phase24/phase120 与 `expm1->degradation->log1p` 线性强度域退化。
- 新增 Table 4（分支遮蔽诊断）、Table 5（image-only+aug vs U1 及未见退化）、Table 6（合成观测风格退化与跨 phase）。
- Discussion 5.4 专写融合机制：contamination / co-utilization / 非自动 fallback / oracle 加权上界。
- Limitations 5.6 补 combined_severe、phase120、质心依赖、rare polar outliers、12f oracle 非门控。

边界与数值口径：
- 主文严格区分主线 OCS-only per_part_log 5.91 deg 与 12f 内部重训 OCS-only 6.58 deg（凡出现 6.58 处均显式标注为 12f 内部参照）。
- U1 写成 OCS-image co-utilization，分支遮蔽明确标注为 feature-level 诊断、远高于 OCS-only 5.91 deg，未写成 OCS-standalone fallback。
- 12c 写成 observation-chain-inspired synthetic stress test；phase120 与 combined_severe 写成 failure boundary；12f best beta 写成 oracle 推理端上界。

仍需作者确认的问题（Q 占位）：
- Q12 Data/Code 可用性、Q13 Author/CRediT、Q14 Funding/COI 均保留 `[需要作者确认]`，未代填。
- Euler convention、target encoding（草拟 sin-cos）、angular error formula（草拟 great-circle）、0% OCS-noise 表值、哪些 ablation 进主文、Table 1 文献元数据、kNN Hit@10。

Codex 审阅/裁定结果：
- v0.1 的 OCS-noise fusion-gain 表（现 4.6）是否保留主文或移 Supplementary S3。
- 主文 Fig./Table 编号最终化（v0.2 已将 Fig. 4=融合退化鲁棒、Fig. 6=合成压力测试）。
- 12e/12g 是否如建议进 Supplementary、主文仅 Limitations 点名。

裁定：OCS-noise 完整表建议进入 Supplementary S3，主文保留机制性摘要；12e/12g 主文点名并进入 Limitations，完整表优先放 Supplementary；U1 分支遮蔽方向已在最终主稿中修正为 image masked = 30.87 deg、OCS masked = 56-59 deg。

下一步：核对 Codex 已整合生成的 `../manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md`。Claude 侧不直接覆盖主稿；CJA/AST 与 TAES/JGCD 继续冻结。

## 1. 当前任务

Claude 侧已一次性生成 v0.2 第一版完整候选稿，重点整合 07 + 07b + 07c。输出是候选材料，已交给 Codex 审阅并参与最终整合。

最终主稿路径：

```text
../manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md
```

对应审阅/决策记录：

```text
../Codex审阅/01_Claude_v0.2_Acta_ASR主投优先版候选稿单边审阅.md
../Codex审阅/01_v0.2_Acta_ASR_GPT_vs_Claude整合决策.md
```

## 2. 必读材料

```text
论文写作/00_总控流程.md
论文写作/02_后整合双线修订/00_后整合双线总览.md
论文写作/03_投稿定稿/01_v0.2_Acta_ASR主投优先版/00_本阶段任务说明.md
论文写作/01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md
论文写作/02_后整合双线修订/阶段整合输出/07_融合机制诊断与鲁棒融合升级_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/07b_融合fallback因果隔离与鲁棒性补强_整合清单.md
论文写作/02_后整合双线修订/阶段整合输出/07c_投稿前非真实数据补实验总包_整合清单.md
论文写作/02_后整合双线修订/20260604_投稿策略与补实验提案_Claude给Codex.md
论文写作/03_投稿定稿/submission_checklist/投稿策略_三档路线_v20260604.md
```

## 3. 红线

不覆盖 v0.1，不直接写最终主稿，不写 CJA/AST 或 TAES/JGCD 版本，不代填 Q12-Q14，不写自动 fallback、真实望远镜验证、fully robust 或 operational robustness。

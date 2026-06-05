# GPT 投稿定稿交互总览

> 最后更新：2026-06-05  
> 当前阶段：v0.2 Acta/ASR 主投优先版候选稿已通过 Codex 审阅，并已参与最终整合  
> 当前提示词：`01_v0.2_Acta_ASR主投优先版_GPT提示词.md`  
> 输出路径：`GPT输出/01_GPT输出_v0.2_Acta_ASR主投优先版.md`

## 1. 当前任务

GPT 侧负责生成 v0.2 第一版候选材料，偏结构审计、冲突梳理和 claim-evidence map。输出不直接覆盖最终主稿。

当前 GPT 候选稿已生成：

```text
GPT输出/01_GPT输出_v0.2_Acta_ASR主投优先版.md
```

该文件已覆盖候选稿、v0.1 主要变化、claim-evidence map、red-line audit 和 remaining checks。Codex 已完成 GPT 单边审阅、Claude 单边审阅和 GPT-vs-Claude 整合决策。

最终主稿已由 Codex 生成：

```text
../manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md
```

对应审阅/决策记录：

```text
../Codex审阅/01_GPT_v0.2_Acta_ASR主投优先版候选稿单边审阅.md
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
论文写作/03_投稿定稿/submission_checklist/投稿策略_三档路线_v20260604.md
```

## 3. 红线

不覆盖 v0.1，不直接写最终主稿，不写 CJA/AST 或 TAES/JGCD 版本，不代填 Q12-Q14，不写自动 fallback、真实望远镜验证、fully robust 或 operational robustness。

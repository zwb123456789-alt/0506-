# R73 Codex 审阅：1C-E39 通过，并放行 E40 C3 joint smoke

最后更新：2026-06-26  
审阅端：Codex

## 裁决

```text
1C-E39: PASS
Next released task: 1C-E40 C3 joint fold0 runtime smoke
Formal C3 5-fold training: NOT RELEASED
训练/新实验正式结果: NOT RELEASED
论文正文正式改写: NOT RELEASED
三轴小项目/路线二/三/四: NOT RELEASED
```

## 核验

- 数据、manifest、PNG、标签、GPU/PyTorch 环境均具备 C3 最低入口条件。
- `train_baseline.py` 已有 `image_only / ocs_only / joint` 三模式和 early fusion 入口。
- `e25_multifold_yawblock` 已存在 5-fold `image_only` 历史结果，可作为后续复用候选，但需另行口径确认。

## 关键裁决点

```text
不得直接用 train_baseline.py --mode all 作为正式三通道 C3。
原因：C2 OCS-only 使用 enhanced_ocs_features.npz + EnhancedOCSDataset；
train_baseline.py 的 ocs_only/joint 使用 split manifest 中的 4-dim OCS。
二者不是同一 OCS 输入口径。
```

因此，正式 C3 前先做最小 joint smoke，只验证图像+OCS early fusion 管线、CUDA 和输出写入，不把指标写入论文证据。

## 给 Claude 的 E40 短提示词

```text
执行 1C-E40：C3 joint fold0 runtime smoke。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R70_Codex_规则_Claude执行端已知问题与规避规则.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R73_Codex_审阅_1C-E39通过并放行E40_C3_joint_smoke.md

任务：
1. 不改代码。
2. 不运行 `--mode all`，不运行 `ocs_only`。
3. 只运行 fold0 的 `joint` 1-epoch smoke，用现有 `train_baseline.py` 验证 dataloader、CNN image encoder、OCS encoder、early fusion、CUDA 和输出写入。
4. 同时登记已有 E25 image_only 5-fold 结果文件是否齐全，作为“复用候选”，不得直接宣称为 C3 正式 image baseline。
5. 输出只报告：命令、exit code、输出文件路径、是否 OOM/报错、关键 metrics 是否存在。不要解释指标优劣，不写论文结论。

建议命令：
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code/07_training/train_baseline.py --train --mode joint --max-epochs 1 --train-split-manifest v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold0.json --outdir v0.4_results/06_c3_preflight/e40_joint_fold0_smoke --device cuda --val-max 128 --num-workers 0

输出路径：
/d/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/73_1C-E40_C3_joint_fold0_smoke_Claude执行报告.md

红线：
- 不启动正式 C3 5-fold。
- 不运行 image_only 正式重训。
- 不运行 ocs_only。
- 不修改代码或数据管线。
- 不把 smoke 指标作为论文证据。
- 不写论文正文正式段落。
- 不放行三轴小项目或路线二/三/四。
```

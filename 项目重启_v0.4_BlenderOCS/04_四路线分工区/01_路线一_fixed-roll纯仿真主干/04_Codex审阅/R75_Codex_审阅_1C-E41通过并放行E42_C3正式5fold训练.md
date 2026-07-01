# R75 Codex 审阅：1C-E41 通过，并放行 E42 C3 正式 5-fold 训练

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  74_1C-E41_C3正式协议锁定准备_Claude执行报告.md
```

## 0. 裁决

```text
1C-E41: PASS WITH MINOR CORRECTIONS
Codex option decision: Option B-min
E25 image-only复用为正式C3 baseline: NOT ACCEPTED
C3正式5-fold image_only训练: RELEASED
C3正式5-fold joint训练: RELEASED
raw 4-dim OCS-only正式对照: NOT RELEASED
--mode all: NOT RELEASED
论文正文正式改写: NOT RELEASED
三轴小项目/路线二/路线三/路线四: NOT RELEASED
```

采用 **Option B-min**：重跑 `image_only` 5-fold + 新跑 `joint` 5-fold；暂不运行 raw 4-dim `ocs_only`。

理由：E25 技术上可复用，但不是正式 C3 协议锁定后的前瞻 baseline。E25 实测每 fold 约 8.4 分钟，不支持 Claude 报告中 30-40h 的高成本估计；因此用可控计算成本换取更干净的 C3 正式证据链更合适。E25 只保留为历史一致性参照和 sanity prior，不进入 C3 正式 baseline 口径。

## 1. 关键核验

- E25 5-fold 文件齐全，`mode=image_only`、`max_epochs=20`、`lr=0.001`、`seed=42`、strict yaw-block overlap 均成立。
- E25 汇总值核验通过：5 folds primary test `yaw_acc=0.0`，mean pitch_acc=20.68%，mean yaw_cmae=83.48 deg。
- E40 joint fold0 1-epoch smoke 仅证明管线可运行，不得作为论文证据。
- `train_baseline.py` 默认 `--lr=0.001`、`--seed=42`，DataLoader batch size 硬编码为 32。
- `--val-max` 默认 500；本 5-fold 的 val 集为 259，因此默认不会截断 val。后续命令仍建议显式写 `--val-max 0`，避免报告口径歧义。
- Claude 报告中的相对路径必须以项目根目录为工作目录解释：

```text
D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS
```

## 2. Minor Corrections

1. Claude 报告 §1 写“三项决策材料”，表格实际列出 4 项；不影响裁决。
2. §3.1 的 `val_max — E25 未使用` 表述不精确。准确口径为：脚本默认 `--val-max 500`，但 E25/C3 fold val_n=259，不发生截断；E42 可显式 `--val-max 0` 锁定全量验证。
3. GPU 时间估计偏高。按 E25 实测，image_only 5-fold 约 42 分钟；joint 可能更慢但已有 E40 smoke 证明管线可跑，不能据此阻止 Option B。
4. 正式执行命令必须从项目根目录运行，不得从路线一子目录运行。

## 3. E42 放行范围

只放行以下 10 个正式训练任务：

```text
image_only fold0-4
joint      fold0-4
```

输出目录：

```text
v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold0-4/
v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold0-4/
```

每个 fold 必须输出：

```text
checkpoint_<mode>.pt
e21_fix01_baseline_results.json
e21_fix01_detail_<mode>.json
e21_fix01_overlap_report.json
```

E42 只负责运行与登记，不做论文正文、不扩大 claim、不补跑 raw OCS-only、不做架构搜索。

## 4. 命令模板

运行前必须切到项目根目录：

```powershell
Set-Location "D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS"
```

image_only fold N：

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" "06_v0.4_code\07_training\train_baseline.py" --train --mode image_only --max-epochs 20 --lr 0.001 --seed 42 --train-split-manifest "v0.4_results\03_training_baseline\e25_multifold_yawblock\split_manifest_circ_yawblock_foldN.json" --outdir "v0.4_results\06_c3_preflight\c3_image_formal_5fold\foldN" --device cuda --num-workers 4 --val-max 0
```

joint fold N：

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" "06_v0.4_code\07_training\train_baseline.py" --train --mode joint --max-epochs 20 --lr 0.001 --seed 42 --train-split-manifest "v0.4_results\03_training_baseline\e25_multifold_yawblock\split_manifest_circ_yawblock_foldN.json" --outdir "v0.4_results\06_c3_preflight\c3_joint_formal_5fold\foldN" --device cuda --num-workers 4 --val-max 0
```

若 CUDA OOM，只允许把 `--num-workers` 降到 0 或暂停并回报；不得改 batch size、epochs、LR、seed、模型、split 或训练协议。

## 5. 给 Claude 的 E42 短提示词

```text
执行 1C-E42：C3正式5-fold训练执行与登记。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R70_Codex_规则_Claude执行端已知问题与规避规则.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R75_Codex_审阅_1C-E41通过并放行E42_C3正式5fold训练.md

工作目录：
D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS

任务：
1. 按 R75 命令模板运行 image_only fold0-4 与 joint fold0-4，共 10 个训练。
2. 每个 fold 使用同一套 split_manifest_circ_yawblock_foldN.json、max_epochs=20、lr=0.001、seed=42、val-max=0、device=cuda。
3. 输出到：
   - v0.4_results/06_c3_preflight/c3_image_formal_5fold/foldN/
   - v0.4_results/06_c3_preflight/c3_joint_formal_5fold/foldN/
4. 训练完成后只做结果登记：列每 fold 文件是否齐全、exit code、elapsed、primary test yaw_acc/pitch_acc/yaw_cmae、overlap strict 状态。
5. 输出简短执行报告到：
   /d/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/75_1C-E42_C3正式5fold训练执行登记_Claude执行报告.md

红线：
- 不运行 --mode all。
- 不运行 raw 4-dim ocs_only。
- 不修改代码、模型、数据、split、batch size、LR、seed、epochs。
- 不把 E40 smoke 或 E25 复用写成 C3 正式证据。
- 不写论文正文，不扩展三轴小项目或路线二/三/四。
- 若出现 OOM、CUDA error、缺文件、overlap 非 strict 或任一 fold 失败，停止后登记失败点并交回 Codex。
```

## 6. CLAUDE.md 同步

项目规则要求通过后同步 `CLAUDE.md`；但 `CLAUDE.md` 属于非审阅文件，当前红线要求修改前先获作者确认。建议作者确认后，将当前下一步从 E41 更新为 E42，并写入 Option B-min 与 raw OCS-only 未放行边界。

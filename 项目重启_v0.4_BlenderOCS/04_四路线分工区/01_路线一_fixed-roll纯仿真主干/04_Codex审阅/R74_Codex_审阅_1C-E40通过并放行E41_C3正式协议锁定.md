# R74 Codex 审阅：1C-E40 通过，并放行 E41 C3 正式协议锁定

最后更新：2026-06-26  
审阅端：Codex

## 裁决

```text
1C-E40: PASS
Next released task: 1C-E41 C3 formal protocol lock
Formal C3 5-fold training: NOT RELEASED
训练/新实验正式执行: NOT RELEASED
论文正文正式改写: NOT RELEASED
三轴小项目/路线二/三/四: NOT RELEASED
```

## 核验

- joint fold0 1-epoch smoke exit code 0。
- 输出齐全：`checkpoint_joint.pt`、summary JSON、detail JSON、overlap report。
- JSON 确认仅运行 `mode=["joint"]`、`max_epochs=1`、fold0 yaw-block manifest。
- E25 image-only 5-fold 文件齐全，且协议为 strict yaw-block、20 epochs、自定义 6-layer CNN；可作为复用候选。

## 关键边界

```text
E40 smoke 只证明 joint 管线可运行，指标不得作为论文证据。
E25 image-only 结果不得自动宣称为 C3 正式 image baseline，需 E41 锁定复用口径。
C2 OCS-only 与 train_baseline manifest 4-dim OCS 不是同一 OCS 输入口径。
```

## 给 Claude 的 E41 短提示词

```text
执行 1C-E41：C3 正式协议锁定准备，不运行训练。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R70_Codex_规则_Claude执行端已知问题与规避规则.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R73_Codex_审阅_1C-E39通过并放行E40_C3_joint_smoke.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R74_Codex_审阅_1C-E40通过并放行E41_C3正式协议锁定.md

任务：
1. 整理 C3 正式协议候选，不运行训练、不改代码。
2. 明确 image-only 是否复用 E25 5-fold 结果：列出可复用条件、不能复用的风险、若复用需在论文中如何标注。
3. 明确 joint 正式训练候选：fold 范围、epochs、seed、split manifest、输出目录、是否只跑 joint。
4. 明确 OCS-only 对照边界：C2 enhanced OCS-only 结果可作为 OCS-only null baseline；不得与 train_baseline 4-dim OCS 混为同一结果。
5. 给出 Codex 二选一或三选一裁决表：
   - Option A：复用 E25 image-only + 新跑 joint 5-fold
   - Option B：重跑 image-only + joint 5-fold
   - Option C：只做 joint 试验，不形成正式三通道 claim
6. 报告遵循简短必要原则，不复述 C1/C2 历史。

输出路径：
/d/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/74_1C-E41_C3正式协议锁定准备_Claude执行报告.md

红线：
- 不启动正式 C3 训练。
- 不运行 image_only/joint/ocs_only 训练。
- 不修改代码或数据管线。
- 不把 E40 smoke 指标作为论文证据。
- 不写论文正文正式段落。
- 不放行三轴小项目或路线二/三/四。
```

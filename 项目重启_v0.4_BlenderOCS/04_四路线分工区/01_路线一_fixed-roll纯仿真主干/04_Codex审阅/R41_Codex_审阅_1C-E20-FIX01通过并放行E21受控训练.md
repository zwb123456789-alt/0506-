# R41 Codex 审阅：1C-E20-FIX01 训练 smoke 判据修正

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/42_1C-E20-FIX01_训练smoke判据修正_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E20-FIX01：PASS
训练 smoke 判据修正：PASS
yaw_block split：PASS
训练保护：PASS
E21 受控训练：RELEASED WITH LIMITS
论文级结论/完整超参搜索：NOT RELEASED
下一步：1C-E21，受控 baseline 训练与评估
```

结论：R40 要求已闭合。`train_smoke.py` 已将基础设施硬门禁与性能诊断拆分，三模式均为 `INFRA_PASS`；`split_manifest_yaw_block.json` 已生成并覆盖 2664 records；三层训练保护仍有效。因此放行下一步 `1C-E21`：受控 baseline 训练与评估。

注意：E21 只放行“受控 baseline 训练”，不放行论文正文结论、完整超参搜索、B1/GGX/三轴或其他路线扩展。

---

## 1. Codex 核验证据

### 1.1 文件在位

```text
06_v0.4_code/07_training/train_smoke.py
v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json
v0.4_results/02_training_smoke/e20_min_train_smoke/e20_smoke_results.json
```

### 1.2 新 JSON 结构

Codex 读取 `e20_smoke_results.json`，确认结构已变为：

```text
infrastructure_pass
overall_infrastructure_status
infrastructure_checks
performance_diagnostics
performance_notes
```

三模式结果：

```text
image_only: infrastructure_pass=true, INFRA_PASS
ocs_only:   infrastructure_pass=true, INFRA_PASS
joint:      infrastructure_pass=true, INFRA_PASS
```

性能诊断仍保留，但不参与 infrastructure gate。例如 image_only 的 yaw/pitch 低于随机基线被写入 `performance_notes`，不再导致训练脚本工程失败。

### 1.3 yaw_block split

Codex 读取 `split_manifest_yaw_block.json`：

```text
method=yaw_block
seed=42
n_total=2664
train=2109
val=259
test=296
unique_record_ids=2664
duplicates=0
```

覆盖：

```text
train yaw=0..280,   57/72, pitch=37/37
val   yaw=285..315,  7/72, pitch=37/37
test  yaw=320..355,  8/72, pitch=37/37
```

这满足 R40 要求，可用于 E21+ 的几何方向留出评估。它比 random split 更严格，但也要注意 yaw 连续块切分会把测试集集中在高 yaw 区间；正式论文结论前可再考虑 circular yaw block 或多折 yaw block。

### 1.4 保护验证

Codex 复跑：

```powershell
python train_smoke.py --max-epochs 1
python train_smoke.py --train-smoke --max-epochs 10
python train_smoke.py --train-smoke --subset-size 2048
```

三者均 exit 1 并阻断：

```text
缺 --train-smoke：BLOCKED
epoch 超限：BLOCKED
subset 超限：BLOCKED
```

### 1.5 语法检查

Codex 对 `train_smoke.py` 执行 `py_compile`，通过。

---

## 2. R40 问题闭合判定

| R40 要求 | 判定 | 依据 |
|---|---|---|
| 拆分 infrastructure / performance | PASS | JSON 与脚本结构已拆分 |
| `smoke_pass` 不再代表性能硬门槛 | PASS | 三模式均 `infrastructure_pass=true` |
| 增加 status 与 notes | PASS | `overall_infrastructure_status`, `performance_notes` 已落地 |
| 生成 yaw_block split | PASS | 2664 records，无重复，pitch 全覆盖 |
| 小 smoke 复跑 | PASS | 1 epoch / 200 sample 复跑完成 |
| 保护仍有效 | PASS | 三类误触均阻断 |

---

## 3. 放行范围

E21 允许：

- 实现受控 baseline 训练脚本或扩展训练入口；
- 使用 fullrun B0 2664 数据；
- 运行 `ocs_only`、`image_only`、`joint` baseline；
- 使用 random split 做 sanity / overfit 检查；
- 使用 yaw_block split 做更严格泛化评估；
- 固定 seed；
- 输出 checkpoint、metrics、confusion matrix、per-yaw/per-pitch 指标；
- 记录训练曲线和评估 JSON。

E21 限制：

- epoch 上限建议不超过 30；
- 每个模式最多一组主配置，不做大规模超参搜索；
- 不宣称论文级最终性能；
- 不改论文正文；
- 不启动 B1/GGX/三轴/路线二/三/四。

---

## 4. E21 最低验收门槛

E21 报告至少必须包含：

1. 训练配置：split、mode、epochs、batch_size、lr、seed、device；
2. 每个 mode 的 train/val loss 曲线；
3. random split 与 yaw_block split 的指标区分；
4. yaw acc、pitch acc、circular yaw MAE、pitch MAE；
5. per-yaw / per-pitch 细分统计；
6. confusion matrix 或可替代的错误分布摘要；
7. checkpoint 路径和大小；
8. 是否存在 NaN/Inf、梯度爆炸、过拟合；
9. 明确声明结果只作为工程 baseline，不写论文正文结论。

---

## 5. 下一步：1C-E21

建议 E21 输出目录：

```text
v0.4_results/03_training_baseline/e21_controlled_baseline/
```

建议报告：

```text
02_Claude输出/43_1C-E21_受控baseline训练与评估_Claude执行报告.md
```

---

## 6. 给 Claude 的下一步指令摘要

```text
执行 1C-E21：受控 baseline 训练与评估。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R41_Codex_审阅_1C-E20-FIX01通过并放行E21受控训练.md
- 06_v0.4_code/07_training/
- v0.4_results/01_fullrun/postprocess/split_manifest.json
- v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json

允许：
1. 实现受控 baseline 训练脚本。
2. 训练 ocs_only / image_only / joint 三模式 baseline。
3. 使用 random split 做 sanity，使用 yaw_block split 做严格泛化评估。
4. epoch 上限建议 <=30；每模式一组主配置，不做大规模超参搜索。
5. 输出 checkpoint、metrics JSON、loss curve、confusion matrix 或错误分布摘要。

必须：
1. 固定 seed。
2. 使用 circular yaw MAE。
3. 区分 random split 与 yaw_block split。
4. 记录 NaN/Inf、梯度、过拟合迹象。
5. 报告写入：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/43_1C-E21_受控baseline训练与评估_Claude执行报告.md

红线：
- 不做大规模超参搜索。
- 不写论文正文。
- 不改冻结文件 13/14/24/25。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不写 04_Codex审阅/。
- 不把 E21 结果表述为论文最终结论。
```


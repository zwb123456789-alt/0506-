# 74_1C-E41_C3正式协议锁定准备_Claude执行报告

执行端：Claude  
任务编号：1C-E41  
执行日期：2026-06-26  

---

## 0. 任务状态

```text
1C-E41：COMPLETED
正式 C3 训练：未运行
代码修改：无
```

---

## 1. 关键产物

本报告提供 C3 正式协议锁定所需的三项决策材料：

| # | 材料 | 所在节 |
|---|------|--------|
| 1 | image-only 复用评估（E25 5-fold） | §2 |
| 2 | joint 正式训练候选协议 | §3 |
| 3 | OCS-only 对照边界 | §4 |
| 4 | Codex 三选一裁决表 | §5 |

---

## 2. image-only 复用评估：E25 5-fold

### 2.1 E25 现状

```text
路径：v0.4_results/03_training_baseline/e25_multifold_yawblock/
模式：image_only
Folds：5（fold0–fold4），每 fold 含 checkpoint + results + detail + overlap report
汇总：e25_multifold_summary.json
```

关键协议参数：

| 参数 | 值 |
|------|-----|
| split 方法 | circular yaw-block（严格无重叠） |
| Max epochs | 20 |
| LR | 0.001 |
| Seed | 42 |
| Image encoder | 6-layer CNN（ImageEncoder），~3.87M params |
| Device | CUDA |

E25 5-fold aggregate：

| 指标 | 值 |
|------|-----|
| mean yaw_acc | 0.00%（全部 5 folds 均为 0） |
| mean pitch_acc | 20.68% |
| mean yaw_cmae | 83.48° |
| random split yaw_acc | ~65–69%（in-distribution 可学） |

### 2.2 可复用条件

E25 可作为 C3 正式 image-only baseline，需满足以下全部条件：

1. **Split 一致**：E25 使用的 5-fold circular yaw-block manifest 与 E40 smoke、C3 正式 joint 训练使用同一套 manifest（`split_manifest_circ_yawblock_fold0–4.json`）。✅ 已确认一致。
2. **协议可比**：image-only 与 joint 使用相同的 max_epochs（20）、LR（0.001）、seed（42）、batch_size（32）。✅ E25 已满足。
3. **架构可比**：image encoder 部分与 joint 中的 image encoder 完全相同（6-layer CNN → 256-dim）。✅ 架构一致。
4. **无数据泄漏**：yaw-block split 严格无 train/val/test overlap。✅ E25 overlap report 确认 strict。

### 2.3 不能自动复用为 C3 正式 baseline 的风险

| 风险 | 说明 |
|------|------|
| **非预注册** | E25 运行于 E21 FIX01 上下文，当时 C3 协议尚未锁定；不是预注册 C3 image baseline |
| **协议偏差** | 若 C3 joint 使用不同 epochs 或 LR，则 E25 image-only 与之不可直接对比 |
| **时间漂移** | E25 与 C3 joint 训练时间不同，若数据/代码有微小变更，结果可能不一致 |
| **论文标注** | 复用 E25 需在论文中明确标注：*"Image-only results were obtained prior to the formal C3 protocol lock under protocol v0.4-1C-E25, which employs identical split manifests and training configuration as the joint protocol described here."* |

### 2.4 复用判断

```text
E25 image-only 5-fold 结果文件齐全、协议一致、无数据泄漏。
技术层面可复用；流程层面需 Codex 确认是否接受"非预注册但协议一致"的复用口径。
```

---

## 3. joint 正式训练候选协议

### 3.1 协议参数

| 参数 | 候选值 | 依据 |
|------|--------|------|
| mode | `joint` | 只跑 joint，不跑 all |
| 5-fold manifests | `split_manifest_circ_yawblock_fold0–4.json` | 与 E25/E40 同一套 |
| max_epochs | 20 | 与 E25 对齐以可比 |
| LR | 0.001 | 固定协议 |
| seed | 42 | 固定协议 |
| batch_size | 32 | 固定协议 |
| optimizer | Adam | 固定协议 |
| device | cuda | 需 GPU |
| num_workers | 4 | 与 E25 对齐 |
| val_max | — | E25 未使用，C3 joint 也不使用 |
| OCS input | 4-dim raw（ocs_total, ocs_jinshuzhuti, ocs_taiyangnengban, ocs_yinshenban） | 来自 manifest JSONL |

### 3.2 输出结构

```text
v0.4_results/06_c3_preflight/c3_joint_formal_5fold/
  fold0/  checkpoint_joint.pt  e21_fix01_baseline_results.json  e21_fix01_detail_joint.json  e21_fix01_overlap_report.json
  fold1/  ...
  fold2/  ...
  fold3/  ...
  fold4/  ...
  c3_joint_summary.json
```

### 3.3 建议命令模板

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code/07_training/train_baseline.py --train --mode joint --max-epochs 20 --train-split-manifest v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold{N}.json --outdir v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold{N} --device cuda --num-workers 4
```

### 3.4 不跑的内容

```text
不跑 --mode all
不跑 --mode ocs_only（train_baseline 的 raw 4-dim OCS ≠ C2 enhanced OCS，不可混用）
不跑 --mode image_only 重训（除非 Codex 选择 Option B）
```

---

## 4. OCS-only 对照边界

### 4.1 两套 OCS 输入的区别

| 维度 | C2 enhanced OCS-only | train_baseline raw 4-dim OCS |
|------|---------------------|------------------------------|
| 数据源 | `enhanced_ocs_features.npz` | JSONL manifest 中 `ocs_total/jinshuzhuti/taiyangnengban/yinshenban` |
| Dataset | EnhancedOCSDataset | OCSImageDataset |
| 特征维度 | 1–13（13 configs） | 4（固定） |
| 特征内容 | ratios, logs, densities, pixel fractions 等衍生特征 | 原始积分 OCS 值 |
| 协议 | C2 固定协议（R60/R62 稳定） | C3 候选协议（待锁定） |
| 状态 | C2 null result，R62 通过 | 未运行正式训练 |

### 4.2 OCS-only 对照边界规则

```text
1. C2 enhanced OCS-only null result 作为论文 OCS-only null baseline（R62 稳定口径）。
2. train_baseline 的 raw 4-dim OCS 不得与 C2 enhanced OCS 写成同一结果链或同一 OCS-only 口径。
3. 若 C3 需要 train_baseline raw 4-dim OCS-only 对照线：
   - 需单独运行 --mode ocs_only 5-fold；
   - 必须在论文中标注"raw 4-dim OCS（from manifest）"，与 C2 的"enhanced OCS features"明确区分；
   - 该对照线属于 C3 协议范围，不纳入 C2 null result 证据包。
4. 两套 OCS 数据均来自同一 phase63 fixed-roll 仿真（2664 条记录），物理前向模型相同；
   差异仅在特征工程层面（C2=预注册增强特征，raw=原始积分值）。
```

---

## 5. Codex 三选一裁决表

### 5.1 三选项概览

| | Option A | Option B | Option C |
|---|---|---|---|
| **描述** | 复用 E25 image-only + 新跑 joint 5-fold | 重跑 image-only + joint 5-fold | 只做 joint 试验，不形成三通道 claim |
| **image-only** | 复用 E25（已有） | 新跑 5-fold | 不做 |
| **joint** | 新跑 5-fold | 新跑 5-fold | 新跑 5-fold |
| **OCS-only 对照** | C2 enhanced null（已稳定） | C2 enhanced null（已稳定） + 可选 raw 4-dim | C2 enhanced null（已稳定） |
| **GPU 时间** | ~5×3–4h = 15–20h | ~10×3–4h = 30–40h | ~5×3–4h = 15–20h |
| **论文三通道** | 有（E25 image + C2 OCS + C3 joint） | 有（C3 全套） | 无（仅 joint 独立） |

### 5.2 各选项详析

**Option A：复用 E25 image-only + 新跑 joint 5-fold**

```text
优势：
- 最小 GPU 消耗（仅 5-fold joint）
- image-only 已有 5-fold 完整结果，直接进入 C3 对比
- 三通道 claim 可立即形成

风险：
- E25 非预注册 C3 baseline，审稿人或会质疑
- 若 joint 训练过程中出现问题需要改协议，E25 image-only 也随之不可比

论文标注要求：
- 必须注明 E25 image-only 为"pre-protocol-lock result under identical split/training config"
- 不可声称 E25 为"prospective C3 image baseline"
```

**Option B：重跑 image-only + joint 5-fold**

```text
优势：
- 完全预注册 C3 协议，审稿置信度最高
- image-only 与 joint 在同一代码/环境/时间窗口下运行，可比性最强
- 可按需增加 raw 4-dim OCS-only 对照线

风险：
- GPU 时间翻倍（30–40h）
- 若 image-only 重跑结果与 E25 显著不同，需要解释差异原因
- 延迟 Results 整合 1–2 周

附加选项：
- 可额外跑 --mode ocs_only 做 raw 4-dim OCS-only 对照
- 该 raw 4-dim 结果与 C2 enhanced OCS 必须明确区分
```

**Option C：只做 joint 试验**

```text
优势：
- 不形成三通道 claim，避免 E25 复用争议
- 最小范围，仅验证 joint 是否超越 C2 OCS-only null

风险：
- 无 image-only 对照，论文只能写"joint vs OCS-only"，缺中间对照
- 若 joint positive，无法区分 image vs OCS 贡献
- 论文 novelty 和完整性受损

适用场景：
- 仅当 E25 复用被否决且 GPU 不足以重跑 image-only 时的最低方案
```

### 5.3 裁决建议框架

```text
若 GPU 可用且接受 30–40h → 推荐 Option B（完整预注册 C3）
若 GPU 可用但希望最小化时间 → 推荐 Option A（复用 E25）
若 GPU 不可用或只想做 smoke-level 探索 → Option C
```

当前**不推荐**：
- `--mode all`（会运行 ocs_only raw 4-dim，与 C2 口径冲突）
- 后验 OCS-only 架构搜索
- 在 C3 协议锁定前启动正式训练

---

## 6. 红线确认

| 红线 | 状态 |
|------|------|
| 不启动正式 C3 训练 | ✅ 遵守 |
| 不运行 image_only/joint/ocs_only 训练 | ✅ 遵守 |
| 不修改代码或数据管线 | ✅ 遵守 |
| 不把 E40 smoke 指标作为论文证据 | ✅ 遵守 |
| 不写论文正文正式段落 | ✅ 遵守 |
| 不放行三轴小项目或路线二/三/四 | ✅ 遵守 |
| E25 不自动宣称为 C3 正式 image baseline | ✅ 遵守 |
| C2 enhanced OCS 与 train_baseline raw 4-dim 不混用 | ✅ 遵守 |

---

## 7. 待 Codex 裁决

```text
1. 选择 Option A / B / C？
2. 若选 Option A：是否接受"非预注册但协议一致"的 E25 复用口径？
3. 若选 Option B：是否需要额外跑 raw 4-dim OCS-only 对照线？
4. 是否放行 C3 正式 5-fold 训练（joint 或 image+joint）？
```

---

**执行端签名**：Claude  
**下一步**：等待 Codex 裁决 Option A/B/C 及 C3 正式协议锁定放行范围

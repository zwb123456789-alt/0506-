# M-roll 探针数据审计（R116 子任务 C）

最后更新：2026-07-01  
来源：`v0.4_results/12_l1m3_degraded_mroll/mroll/`

## 1. 渲染与后处理完整性

| roll | 子集姿态数 | 渲染 COMPLETE | 后处理 COMPLETE |
|:--|--:|--:|--:|
| +15° | 312 | 312 | 312 |
| −15° | 312 | 312 | 312 |
| +30° | 312 | 312 | 312 |
| −30° | 312 | 312 | 312 |
| 0°(baseline) | 312 | 复用 `01_fullrun` | 复用 `01_fullrun` |

## 2. 管线一致性

- M-roll 渲染派生自 `render_full_2664_shadow.py`（driver 原生支持 roll，`euler_to_matrix4` / `apply_attitude`），
  仅覆盖 `generate_full_attitude_list` 注入非零 roll、`OUTPUT_DIR`，不改姿态网格步长、不改 pass、不改 SAMPLES。
- M-roll 后处理派生自 `run_full_postprocess.py`，沿用 phase63 的 r_max / i_scale / pixel_area / depth_epsilon，
  与 clean roll-0 数据同量纲、同 OCS 积分口径，PNG 归一化一致。
- roll=0 baseline 直接复用 `01_fullrun` 现有 phase63 产物，未重渲。

## 3. 子集设计

```text
yaw:   0..345 step 15  → 24 个
pitch: -90..90 step 15 → 13 个
n = 312（覆盖 yaw/pitch 空间的分层子集，非全 2664）
```

子集用于低成本边界探针；full-2664 M-roll 成本估算见 `mroll_roll_sensitivity_summary.md` §5。
子集结论不得当作 full-2664 正式结论。

## 4. 语义边界

M-roll 是 fixed-roll 边界探针，检验 clean roll-0 模型在 roll 扰动观测下的漂移。
它不是三轴姿态反演数据集，roll 未作为可反演目标训练；roll 反演能力留待三轴小项目（未启动）。

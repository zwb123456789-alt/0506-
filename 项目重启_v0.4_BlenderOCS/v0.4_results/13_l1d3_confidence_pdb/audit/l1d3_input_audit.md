# R118 子任务 A：L1D3 输入索引与审计复核

最后更新：2026-07-01  

本文件为正式输入 manifest 的人读摘要；机读见 `l1d3_input_manifest.csv` / `l1d3_input_manifest.json`。

## 1. 总览

- 索引行数（run × split × select）：**104**
- 字段完整行数：**104**
- 文件缺失行数：**0**
- 字段缺口行数（文件存在但字段不全）：**0**

## 2. 来源与红线

```text
clean    源：11_l1m2_multigeometry_ocs（R115；val per-attitude 由 R117-A1 checkpoint+确定性split恢复，Δcmae=0.0）
degraded 源：12_l1m3_degraded_mroll（R116；退化观测按 record_id 确定性复现）
val/test 严格分开；任何校准/阈值/quantile 只用 val，test 仅最终评估，不反调。
posterior-like（top5 score/entropy/margin）是工程候选分数，不是真实 Bayesian posterior。
P-DB 检索是 model-known simulated template retrieval，不是真实反演成功率。
```

## 3. 上游审计引用（R117 复核）

`l1m2_transform_leakage_check.json` 关键结论：
```json
{
  "task": "R116-A2 cross-geometry scale consistency + leakage check",
  "param_consistency": {
    "pixel_area_m2": {
      "values": {
        "phase24": 0.00016015410437830724,
        "phase45": 0.00016015410437830724,
        "phase63": 0.00016015410437830724,
        "phase90": 0.00016015410437830724,
        "phase120": 0.00016015410437830724
      },
      "consistent": true,
      "n_nonnull": 5
    },
    "ortho_scale_m": {
      "values": {
        "phase24": 3.239731375366906,
        "phase45": 3.239731375366906,
        "phase63": 3.239731375366906,
        "phase90": 3.239731375366906,
        "phase120": 3.239731375366906
      },
      "consistent": true,
      "n_nonnull": 5
    },
    "depth_epsilon_m": {
      "values": {
        "phase24": 0.7952109582768545,
        "phase45": 0.7952109582768545,
        "phase63": 0.7952109582768545,
        "phase90": 0.7952109582768545,
        "phase120": 0.7952109582768545
      },
      "consistent": true,
      "n_nonnull": 5
    },
    "resolution": {
      "values": {
        "phase24": 256,
        "phase45": 256,
        "phase63": 256,
        "phase90": 256,
        "phase120": 256
      },
      "consistent": tr
```

## 4. 矩阵覆盖（按 degrade_level × mode × geom，test/best 存在性）

| degrade_level | mode | G1 | G3 | G5 |
|:--|:--|:--:|:--:|:--:|
| clean | ocs_only | ✓ | ✓ | ✓ |
| clean | image_only | ✓ | ✓ | ✓ |
| clean | joint | ✓ | ✓ | ✓ |
| degraded-mild | ocs_only | ✓ | ✓ | ✓ |
| degraded-mild | image_only | ✓ | — | ✓ |
| degraded-mild | joint | ✓ | — | ✓ |
| degraded-moderate | ocs_only | ✓ | ✓ | ✓ |
| degraded-moderate | image_only | ✓ | — | ✓ |
| degraded-moderate | joint | ✓ | — | ✓ |

P-EXT（仅 ocs_only）：
| protocol | mode | G1 | G3 | G5 |
|:--|:--|:--:|:--:|:--:|
| P-EXT | ocs_only | ✓ | ✓ | ✓ |

## 5. 字段缺口 / 文件缺失明细

无缺口：所有列入矩阵的 run × split × select 文件均存在且字段完整。


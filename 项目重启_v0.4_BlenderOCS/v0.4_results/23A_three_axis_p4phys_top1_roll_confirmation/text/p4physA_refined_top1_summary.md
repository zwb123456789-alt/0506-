# p4physA refined top-1 summary

## Refined top-1（23A加密后）

| 字段 | 值 |
|------|-----|
| yaw_deg | 245.0 |
| pitch_deg | 27.5 |
| roll | 15.0 |
| ocs_total | 0.208890 |
| source | 23A_new |
| saturation_flag | 1.0 |
| glint_flag | 0.0 |

## 与 sampled-grid top-1 对比

- sampled-grid top-1: yaw=245.0, pitch=30.0, roll=+15, ocs=0.208377
- refined top-1: yaw=245.0, pitch=27.5, roll=15.0, ocs=0.208890

## R1 yaw=245 pitch=+30 refined roll profile

| roll | ocs_total |
|------|-----------|
| +5 | 0.084741 |
| +10 | 0.164953 |
| +12.5 | 0.197765 |
| +15 | 0.208377 |
| +17.5 | 0.191569 |
| +20 | 0.157545 |
| +25 | 0.079649 |

Peak: roll=+15, ocs=0.208377
Is boundary point: False

## 裁决

refined top-1 位于加密矩阵内部，相邻 roll/yaw/pitch 未显示继续上升趋势 → 可进入P4-PHYS-B物理光路归因。

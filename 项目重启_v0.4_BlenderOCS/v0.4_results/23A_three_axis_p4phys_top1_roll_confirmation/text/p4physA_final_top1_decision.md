# p4physA 最终 top-1 裁决

## Refined top-1（23A 加密后）

yaw=245.0, pitch=**27.5**, roll=+15, ocs_total=**0.208890**
saturation_flag=1, glint_flag=0

（相比 sampled-grid top-1: yaw=245.0, pitch=30.0, roll=+15, ocs=0.208377，高出 0.246%）

## 边界判断

| 维度 | 边界情况 | 说明 |
|------|----------|------|
| yaw | 否（内部） | yaw=245.0，位于{242.5,245.0,247.5}中间 |
| pitch | **是（下边界）** | pitch=27.5 = pitch最小值，ocs随pitch减小上升 |
| roll | 否（内部） | roll=+15，位于{+5,...,+25}内部 |

## 裁决结论

**pitch下边界（27.5），且ocs随pitch减小而上升，需追加pitch≤25.0一小圈**

按 R143 §4.4 与 R145 §5.F 规则：
> 若新 top-1 落在边界，例如 roll=+5 或 +25，或 yaw/pitch 边界：
>   不进入光路归因；建议下一轮只沿边界方向追加一小圈。

当前 pitch=27.5 是 pitch 下边界，且 ocs(27.5) > ocs(30.0)，说明峰可能在 pitch < 27.5。

**不进入 P4-PHYS-B。需追加 pitch∈{22.5, 25.0} 的一小圈（roll=+15, yaw=245.0 为主）。**

## R4 对照裁决

R4（yaw=147.5, pitch=+12.5）roll-profile 极度鲁棒，所有 roll 下 ocs 在 0.191-0.202 之间。
R4 在本轮加密中未超过 R1（R4 top = 0.201822 < R1 refined top = 0.208890）。
R4 角色维持：roll-robust 高亮区机制对照，**不是 single-pose top-1**。

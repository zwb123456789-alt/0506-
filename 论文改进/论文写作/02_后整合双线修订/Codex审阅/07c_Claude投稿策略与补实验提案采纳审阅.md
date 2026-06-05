# Codex 审阅：Claude 投稿策略与补实验提案

> 审阅日期：2026-06-04  
> 输入文件：`02_后整合双线修订/20260604_投稿策略与补实验提案_Claude给Codex.md`  
> 审阅结论：部分采纳，并按作者最新意见调整执行顺序  

## 1. 总体判断

Claude 提案对期刊匹配、残留短板和补实验优先级的判断总体合理，但需要按作者最新意见修正：

1. 不走“不补实验直接 v0.2”的路径。
2. 先补齐当前论文范围内、非真实数据相关的投稿前实验。
3. 三档投稿不并行写作。
4. 补实验后只先写 Acta Astronautica / Advances in Space Research 主投优先版。
5. CJA/AST 与 TAES/JGCD 后续写作必须等待作者确认第一档完结。

## 2. 采纳项

| Claude 项 | Codex 判定 | 对应编号 |
|---|---|---|
| P0-A 跨 phase 图像泛化 sanity test | 采纳 | 12d |
| P0-B 质心居中控制实验 | 采纳 | 12e |
| P1-A ResNet late fusion vs feature fusion 图像退化对照 | 采纳 | 12f |
| P1-B U1 worst-case 案例画廊 | 采纳 | 12g |
| 已确定的 observation-style degradation stress test | 保留并纳入总包 | 12c |

## 3. 不采纳为本轮任务的项

| 项目 | 原因 |
|---|---|
| 真实望远镜数据 / 半实测 / 硬件回路 | 作者明确排除真实数据相关实验 |
| 全 3-DOF roll 扩展 | 超出当前 yaw-pitch benchmark 范围，留 Future Work |
| 控制闭环 / 动态滤波 | 属 TAES/JGCD 高风险档新论文范围 |
| 更大 backbone | 偏离本文机制诊断与受控基准主线 |
| ISAR 主线引入 | 仍只作 Future Work 或 modality boundary |

## 4. 对期刊策略的修正

Claude 提案中“路径 A / B / C”的判断可作为背景，但当前执行顺序已经由作者锁定：

```text
补实验12c-12g
-> Codex 审阅
-> Acta/ASR 主投优先版 v0.2
-> 作者确认完结
-> 再决定 CJA/AST 或 TAES/JGCD
```

因此，Codex 不接受“同时准备两条路径”的做法。

## 5. 写作红线

补实验结果回来前，不得写：

- real telescope validation。
- operational robustness。
- fusion automatically robust。
- OCS standalone fallback。
- U1 自动切换到 OCS。
- near-perfect / fully robust。
- CJA/AST 或 TAES/JGCD 已经具备充分支撑。

## 6. 下一步

已更新 07c 任务说明与 Claude 指导。Claude 应按 12c-12g 总包执行并返回脚本、结果目录、summary、CSV/JSON、outlier audit 和策略影响判断。

## 7. 资源核对补强采纳

Claude 后续在原提案中追加的资源核对结果已复核并采纳以下执行细节：

1. 12d 当前缺少 phase24 / phase120 图像，必须先补渲染两个 phase 的 full-grid 2701 张图像。
2. 12c 不能复用旧 log1p 域退化函数，必须采用 `expm1 -> 线性域退化 -> log1p`。
3. 12f beta 方向锁定为 image 权重：`beta=1` image-only，`beta=0` OCS-only；并且必须先检查权重或 per-sample predictions 是否存在，缺失时按协议重训/重推理。
4. 12e 质心必须在线性强度域计算。
5. 推荐执行顺序调整为 `12g -> 12e -> 12f -> 12d -> 12c`。
6. 投稿策略判据增加 12d 跨 phase 仍稳定时的降调写法。

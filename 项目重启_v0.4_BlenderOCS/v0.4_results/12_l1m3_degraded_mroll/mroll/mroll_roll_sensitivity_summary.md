# M-roll fixed-roll 边界探针：roll 敏感性汇总（R116 子任务 C）

最后更新：2026-07-01  
来源：`v0.4_results/12_l1m3_degraded_mroll/mroll/`

## 1. 探针定位

M-roll 是路线一 C 的 **fixed-roll 边界探针**，回答唯一问题：

```text
当前 fixed-roll clean/P-INT 结论，是否被少量 roll 扰动直接推翻？
```

M-roll **不是三轴小项目**，不启动三轴最亮构型/观测规划，不写成真实三轴姿态反演系统。

## 2. 方法（roll distribution-shift，不重训）

- 取 R115 训练好的 clean roll-0 image_only 模型（L1-G1 / L1-G5，来自 `11_l1m2`）。
- 在同一分层子集 attitude（yaw step15 × pitch step15 = 312）上构造 test 观测：
  - roll=0：现有 phase63 PNG（`01_fullrun`）
  - roll=±15/±30：M-roll 探针新渲染 phase63 PNG（`12_l1m3/mroll`）
- 用 clean 模型分别预测，比较 roll=0 与 roll≠0 的 yaw cMAE / hit@30 漂移。
- 真值 yaw/pitch 在 roll 扰动下不变（roll 是绕视线/本体轴的额外自由度）。

本轮只对 image_only 执行：它是 clean P-INT 近饱和通道，最能揭示 roll 扰动是否推翻结论；
且其输入（phase63 PNG）几何无关，成本最低、判据最干净。

## 3. 结果（best-val clean 模型，312 子集）

| geom | roll | yaw cMAE(°) | yaw hit@30 | cMAE 漂移 vs roll0 | hit@30 漂移 |
|:--|--:|--:|--:|--:|--:|
| G1 | 0 | 2.35 | 1.000 | — | — |
| G1 | +15 | 14.78 | 0.936 | +12.43 | −0.064 |
| G1 | −15 | 12.32 | 0.974 | +9.98 | −0.026 |
| G1 | +30 | 33.15 | 0.548 | +30.80 | −0.452 |
| G1 | −30 | 24.45 | 0.647 | +22.11 | −0.353 |
| G5 | 0 | 8.68 | 0.990 | — | — |
| G5 | +15 | 17.53 | 0.843 | +8.85 | −0.147 |
| G5 | −15 | 19.67 | 0.830 | +10.98 | −0.160 |
| G5 | +30 | 32.99 | 0.587 | +24.31 | −0.404 |
| G5 | −30 | 28.69 | 0.567 | +20.01 | −0.423 |

（G1 与 G5 image_only 使用同一 phase63 图像与同容量编码器，数值差异来自各自独立训练/选择口径，不构成几何增益曲线。）

## 4. 结论口径（严格限定本轮设置）

```text
在本轮 roll 设置 {0,±15,±30}、几何组 {G1,G5}、协议 P-INT、312 分层子集、
image_only clean 模型 zero-shot 评估条件下：
  - roll = ±15°：yaw hit@30 仍保持 0.83–0.97，cMAE 漂移约 +9°~+12°。
    → 小 roll 扰动【未直接推翻】fixed-roll clean/P-INT 结论，模型呈优雅退化。
  - roll = ±30°：yaw hit@30 降到 0.55–0.65，cMAE 漂移约 +20°~+31°。
    → 较大 roll 扰动明显侵蚀 fixed-roll 结论，姿态判读开始坍缩。
边界判断：fixed-roll 结论对 ±15° 量级 roll 稳健，对 ±30° 量级敏感。
```

不得写成：

```text
三轴姿态反演已解决；三轴小项目已完成；真实未知目标 roll 可反演。
```

## 5. 全量成本评估与本轮范围

本轮采用 312 分层子集（yaw/pitch step15），仅渲染 phase63（图像通道 + G1 OCS）4 个非零 roll。

```text
实测：phase63 约 0.73 s/姿态（含 camera+sun 两 view，与训练争用 GPU）。
本轮 M-roll 渲染量：312 × 4 roll × 2 view ≈ 已完成。
全量 image_only M-roll（2664 × 4 roll，仅 phase63）估算：≈ 2.2 小时渲染 + 后处理。
全量 joint M-roll（需 5 几何 × 2664 × 4 roll）估算：≈ 10–11 小时渲染 + 后处理。
```

joint 全量 M-roll（多几何 total-flux 的 roll 版本）成本高，本轮未铺满；
image_only 子集探针已足以回答 C1 的边界问题。joint roll 敏感性、full-2664 M-roll
留待后续按需扩展，不在本轮闭口。

## 6. 数据与产物

```text
mroll_subset_attitudes.json                 312 分层子集
shadow_passes/phase63/roll{±015,±030}/       M-roll 探针渲染 EXR
postprocess/phase63/roll{±015,±030}/         M-roll 探针后处理 OCS/PNG
mroll_metrics_summary_best.csv               roll 敏感性主表
mroll_eval_results.json                      逐 roll 评估结果
figures/mroll_roll_sensitivity.png           roll 敏感性曲线
```

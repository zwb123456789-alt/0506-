# L1M3 退化真实性与 M-roll 边界探针成果摘要（R117 通过）

最后更新：2026-07-01  
来源报告：`02_Claude输出/104_1C-L1M3Mroll_退化真实性与roll边界探针_Claude执行报告.md`  
Codex 审阅：`04_Codex审阅/R117_Codex_审阅_104通过_L1M3退化真实性与Mroll边界探针.md`  
结果目录：`v0.4_results/12_l1m3_degraded_mroll/`

## 1. 成果定位

本成果接续 R115 的 L1(M2) clean / P-INT 正结果，用于回答三个问题：

1. R115 的 val per-attitude 和跨几何量纲审计缺口是否补齐。
2. OCS-only 多观测总光度向量增益是否只是 clean-only 假象。
3. fixed-roll 结论是否会被小幅 roll 扰动直接推翻。

本成果不关闭路线一 C 整体，不启动三轴小项目，不把 P-EXT yaw-block 写成已解决，也不声称真实观测验证。

## 2. 审计补齐

R115 的 12 个正式 run 已补齐 `samples_val_final/best`。恢复方式为加载原 checkpoint 并用 seed=42 确定性重建 split；`audit/l1m2_val_samples_recovery_summary.csv` 显示 12 个 run 的 final/best 均 `cmae_delta=0.0`，可等价用于后续 D3/conformal。

跨几何量纲一致性核验通过：五个几何的 pixel area、ortho scale、depth epsilon、resolution 一致；flux transform 只由 train 拟合，train/val/test 无 attitude 泄漏；G1/G3/G5 嵌套对齐成立。该多几何仍限定为 simulated multi-view geometry，不是路线二真实跨时间多几何。

## 3. degraded 真实性轴

本轮使用物理退化而非 B6 粗增广包：PSF/Gaussian blur、Poisson shot noise、read noise、背景与梯度、降采样、测光误差。OCS-only 仅施加测光误差，图像退化不错误作用到 OCS。

OCS-only best 口径下，多几何单调增益在退化下保持：

| 条件 | G1 cMAE | G3 cMAE | G5 cMAE | G5 相对 G1 增益 |
|---|---:|---:|---:|---:|
| clean | 76.56° | 38.22° | 22.77° | 53.79° |
| degraded-mild | 76.78° | 40.15° | 27.83° | 48.95° |
| degraded-moderate | 78.48° | 51.72° | 38.46° | 40.02° |

可写结论：多几何 OCS 增益在本轮物理退化下保持，并随退化强度优雅收缩。不可写成真实观测验证或真实系统鲁棒性完成。

image/joint 在 best-val 口径下仍近饱和，joint 强互补性仍未显现。需注意 final 口径下 G5 joint moderate hit@30=0.189，说明该分支存在检查点选择敏感性，后续若要论证互补性，应转向 P-INT-hard、更强 degraded 或正式 D3。

## 4. M-roll 边界探针

M-roll 是 fixed-roll 边界探针，不是 roll-aware 训练，也不是三轴小项目。方法为使用 clean roll-0 image_only 模型，对 phase63 的 312 分层子集做 zero-shot distribution-shift 评估。

结果摘要：

| geom | roll | yaw cMAE | hit@30 |
|---|---:|---:|---:|
| G1 | 0° | 2.35° | 1.000 |
| G1 | +15° / -15° | 14.78° / 12.32° | 0.936 / 0.974 |
| G1 | +30° / -30° | 33.15° / 24.45° | 0.548 / 0.647 |
| G5 | 0° | 8.68° | 0.990 |
| G5 | +15° / -15° | 17.53° / 19.67° | 0.843 / 0.830 |
| G5 | +30° / -30° | 32.99° / 28.69° | 0.587 / 0.567 |

可写结论：在本轮子集与 image_only zero-shot 条件下，±15° roll 未直接推翻 fixed-roll clean/P-INT 结论，±30° roll 明显侵蚀。joint/full-2664 M-roll 成本约 10-11h，留作按需扩展。

## 5. D3/P-DB/conformal 准备

`d3/l1m3_confidence_inputs_index.csv` 共 104 行，覆盖 clean/degraded 的 val/test 与 final/best samples。P-DB template retrieval smoke 中，L1-G5 total-flux vector 的 neg-L2 top-1 yaw hit@30=0.949，top-k-best hit@30=0.997，说明多观测总光度向量含有强 yaw 可检索信息。

split-conformal smoke 的 coverage 接近 target，但这只是最小 smoke，不是最终概率校准。posterior-like 仍是工程候选分数，不是真实 Bayesian posterior。

## 6. 后续使用口径

R117 后可以稳定引用三点：

1. L1 多观测 OCS 正结果不只存在于 clean；在 mild/moderate 物理退化下仍保持多几何增益。
2. fixed-roll 结论对 ±15° roll 量级扰动未被直接推翻，但对 ±30° 已敏感。
3. D3/P-DB/conformal 已具备正式扩展入口，但当前只到 smoke / preparation。

仍不得引用为：路线一 C 整体闭口、真实未知目标姿态反演系统、真实望远镜验证、三轴小项目完成、P-EXT yaw-block 已解决、joint 强互补性已证明。

# Claude 指导：07c 投稿前非真实数据补实验总包

> 更新日期：2026-06-04  
> 面向对象：Claude 执行端  
> 任务类型：补实验设计、代码实现、运行、结果解释与第一档主投准备  
> Codex 角色：后续审阅端，不直接接受未经审阅的结论进主稿

## 0. 任务边界

你要执行的是投稿前非真实数据补实验总包。实验完成前，不要改写 v0.1，不要生成 v0.2 主稿。

作者已经明确：三档投稿不并行推进。补实验完成后，先写第一档 `Acta Astronautica / Advances in Space Research` 主投优先版；只有作者确认第一档完结后，才进入 CJA/AST 或 TAES/JGCD 后续写作。

## 1. 必读文件

请先读取：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\00_总控流程.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\00_后整合双线总览.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\20260529_论文写作完整规划.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\20260529_补充实验进度.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\20260604_投稿策略与补实验提案_Claude给Codex.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\Codex审阅\07b_Claude融合fallback因果隔离单边审阅.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\阶段整合输出\07b_融合fallback因果隔离与鲁棒性补强_整合清单.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\03_投稿定稿\submission_checklist\投稿策略_三档路线_v20260604.md
```

参考脚本：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_resnet_baseline.py
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_noise_robustness.py
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_fusion_mechanism_upgrade.py
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\代码\run_fusion_fallback_isolation_12b.py
```

## 2. 本轮必须完成的实验

| 编号 | 名称 | 新脚本建议 |
|---|---|---|
| 12c | Observation-style image degradation stress test | `run_observation_style_degradation_12c.py` |
| 12d | Cross-phase image generalization sanity test | `run_cross_phase_generalization_12d.py` |
| 12e | Centered-image / centroid-control experiment | `run_centered_control_12e.py` |
| 12f | Late-fusion beta sweep under image degradation | `run_late_fusion_beta_sweep_12f.py` |
| 12g | U1 / 12b outlier gallery and audit package | `build_outlier_gallery_12g.py` |

若某项无法执行，必须给出具体原因、缺失文件或运行成本，不得静默跳过。

推荐执行顺序：

```text
12g -> 12e -> 12f -> 12d -> 12c
```

理由：先做零训练/低依赖整理，再做轻量控制实验和推理端对照，最后做需要补渲染或重写退化算子的高成本实验。

## 3. 共同协议

除非某项实验本身要求不同，所有训练/评估实验应尽量沿用：

- `split_coarse_to_fine(..., coarse_step=10.0)`。
- target encoding `[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]`。
- great-circle angular error。
- mean、std、p50、p90、p95、worst、Hit@5、Hit@10。
- seeds 0-4；若资源不足至少 3 seeds，并明示。
- OCS 标准化统计只从 train split 拟合。
- 不改动已有主结果，不覆盖已有结果目录。

## 4. 12c 具体要求

输出目录：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\observation_style_degradation_12c\run_YYYYMMDD_HHMMSS\
```

必须在近似线性强度域施加图像退化。如果输入为 `log1p`，先 `expm1`，退化后再 `log1p`。不得直接复用 `run_resnet_robustness.py` 中现有 log1p 域退化函数作为 observation-style degradation 的物理解释。

退化算子必须遵循：

```python
def apply_obs_degradation(img_log1p, deg_config):
    img_lin = np.expm1(img_log1p)
    img_lin = _apply_degradation_in_linear_domain(img_lin, deg_config)
    img_lin = np.clip(img_lin, 0.0, None)
    return np.log1p(img_lin)
```

至少实现：

1. PSF / defocus blur。
2. photon noise。
3. read noise。
4. background offset 或 sparse star-like contamination。
5. clipping / saturation。
6. downsample / low-resolution。
7. mild / medium / severe combined degradation。

建议参数网格或初始档位：

- photon noise: `lin' = Poisson(lin * gain) / gain`，gain 可从 `[10, 100, 1000]` 选 mild/medium/severe。
- read noise: `lin' = lin + Normal(0, sigma_read)`，`sigma_read` 可从 `[0.001, 0.005, 0.01] * max(lin_train)` 选档。
- background: `lin' = lin + bg_level`，`bg_level` 可从 `[0.001, 0.005, 0.02] * max(lin_train)` 选档。
- clipping/saturation: `lin' = min(lin, saturation_level)`，`saturation_level` 可从 `[0.5, 0.8, 0.95] * max(lin_train)` 选档。

Claude 可根据实际强度范围微调参数，但必须输出 degradation_config 表并说明每个参数相对 train split 强度统计的定义。

最低模型：

- ResNet image-only clean-trained。
- image-only simple/same augmentation。
- U1 simple-degradation-aware fusion。
- OCS-only MLP per_part_log。
- 资源允许时执行 image-only obs-aug 与 U2 fusion obs-aug。

## 5. 12d 具体要求

输出目录：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\cross_phase_generalization_12d\run_YYYYMMDD_HHMMSS\
```

设计：

- 训练：phase63 clean image。
- 测试：phase24_near_backscatter 与 phase120_forward_scatter。
- 对照：ResNet image-only、ResNet+OCS A2/concat5 per_part_log。
- 不做全 5 phase 重训，不引入多相位融合新主线。

资源核对结论：当前模块 B full-grid 渲染只有 phase63，phase24 / phase120 图像不存在。12d 执行前必须先补渲染：

```text
phase24_near_backscatter: 2701 张，建议 256 分辨率，与 phase63 主用配置一致
phase120_forward_scatter: 2701 张，建议 256 分辨率，与 phase63 主用配置一致
```

建议渲染输出目录命名：

```text
结果/模块B_渲染/run_YYYYMMDD_HHMMSS_phase24/
结果/模块B_渲染/run_YYYYMMDD_HHMMSS_phase120/
```

渲染后必须执行与 phase63 一致的 BRDF/postprocess/log1p 流程，并在 12d summary 中记录 sun/det 向量、phase angle、image_count、resolution 和后处理脚本。

必须解释两种可能：

- 若跨 phase 明显退化：支持图像模型对观测几何分布敏感。
- 若跨 phase 也稳定：诚实报告，并调整写法，不能强写图像必然跨 phase 脆弱。

## 6. 12e 具体要求

输出目录：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\centered_control_12e\run_YYYYMMDD_HHMMSS\
```

设计：

- 对 phase63 图像按渲染质心或可复现图像质心居中。
- 重训 ResNet image-only，至少 3 seeds，建议 5 seeds。
- 与原 ResNet clean image-only 结果对比。

centroid 必须在线性强度域计算，即对 `log1p` 图像先 `expm1`，再计算 intensity-weighted centroid。不得直接用 log1p 图像计算质心后解释为强度质心。

建议实现：

```python
def compute_centroid(img_log1p):
    img = np.expm1(img_log1p)
    y_idx, x_idx = np.indices(img.shape)
    total = img.sum()
    cx = (img * x_idx).sum() / total
    cy = (img * y_idx).sum() / total
    return cx, cy
```

必须解释：

- 居中后仍强：clean-image upper bound 不只是质心漂移。
- 居中后退化：clean-image 性能部分依赖固定框定，应写入 limitation。

## 7. 12f 具体要求

输出目录：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\late_fusion_beta_sweep_12f\run_YYYYMMDD_HHMMSS\
```

设计：

- 先检查是否已有可加载的 ResNet image-only 与 OCS MLP per_part_log 权重或 per-sample predictions。若不存在，按既有协议重训/重推理并保存 per-sample predictions，不得假设 12b 结果目录已经保存模型权重。
- 条件：clean / noise 0.01 / noise 0.10 / brightness 0.50 / brightness 1.50。
- beta grid 至少 `0, 0.1, ..., 1.0`。
- beta 方向必须锁定为 image 权重。
- 与实验11 naive feature fusion、实验12 U1 对比。

beta 定义：

```text
pred_blend = beta * pred_image + (1 - beta) * pred_ocs
beta = 1.0 -> image-only
beta = 0.0 -> OCS-only
beta = 0.5 -> equal weight
```

建议在 sin-cos 4D 表示空间融合，并对 yaw/pitch 的 sin-cos 对分别归一化后再解码。必须保存每个 seed、每个 beta、每个退化条件的 per-sample prediction 或至少可复算的 CSV。

红线：

- late fusion 表现好，也只能写 explicit weighting can provide an inference-time robustness path。
- 不得写 U1 自动 fallback。

## 8. 12g 具体要求

输出目录：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\outlier_gallery_12g\run_YYYYMMDD_HHMMSS\
```

设计：

- 复用 12b outlier audit。
- 整理 error > 30 deg、>60 deg、>90 deg 样本。
- 输出姿态分布、退化档分布、seed/sample重复性、极区集中程度。
- 输出 42 条 outlier 全表；可行时输出代表性图像/OCS可视化。

建议输出图：

1. outlier 在 yaw-pitch 空间分布，标注 `|pitch| > 75 deg` 极区。
2. outlier 在退化档分布。
3. seed × sample 重复矩阵热图。
4. 6-8 张代表性 outlier 渲染缩略图。

目的：支撑 limitation 与 supplementary，防止 fully robust / near-perfect 误读。

## 9. 返回给 Codex 的格式

完成后请返回：

```text
1. 新增脚本路径清单
2. 每个实验的结果目录
3. 运行状态、耗时、seeds
4. 每个实验的主结果表
5. split / target encoding / metric 是否与既有协议一致
6. outlier / failure audit 摘要
7. 对第一档 Acta/ASR 主投优先版的写作影响
8. 对 CJA/AST 与 TAES/JGCD 的策略影响，但不要启动后两档写作
9. 不能写入论文的过度结论清单
```

## 10. 写作红线

禁止写：

```text
real telescope validation
field-proven robustness
operational robustness
fully robust
near-perfect
fusion automatically robust
OCS standalone fallback
automatic switching to OCS
```

也禁止同步生成：

```text
主稿_v0.2_CJA_AST冲刺优先版.md
主稿_v0.2_TAES_JGCD高风险冲刺评估版.md
```

这些只能在作者确认第一档完结后再进入。

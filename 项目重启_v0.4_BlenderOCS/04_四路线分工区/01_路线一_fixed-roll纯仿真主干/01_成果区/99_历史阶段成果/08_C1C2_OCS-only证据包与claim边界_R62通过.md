# C1/C2 OCS-only 证据包与 claim 边界（R62 通过稳定版）

最后更新：2026-06-26  
状态：R62 Codex 审阅通过  
适用范围：路线一 C，fixed-roll 纯仿真主干，C1/C2 OCS-only 证据包

---

## 1. 来源

```text
Codex 审阅：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R60_Codex_审阅_1C-E32通过并接受C2_OCS-only负结果.md
  R61_Codex_审阅_1C-E33需FIX01_判据基线与C3边界修正.md
  R62_Codex_审阅_1C-E33-FIX01通过并形成C1C2稳定证据包.md

Claude 执行报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  60_1C-E32_C2_OCS-only正式筛选_Claude执行报告.md
  61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part1.md
  61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part2.md
  62_1C-E33-FIX01_判据基线与C3边界修正_Claude执行报告.md

结果文件：
v0.4_results/05_c2_screening/c2_screening_summary.json
```

本文件是 R62 通过后的稳定口径。若 E33 原报告与 E33-FIX01 冲突，以 E33-FIX01 和本文件为准。

---

## 2. C1 稳定结论

```text
C1：14 个配置完成预注册完整性验证。
C2：13 个配置进入正式 OCS-only 筛选。
```

C1 的作用是锁定特征配置和 claim class，支撑 C2 固定协议筛选。C1 不单独构成姿态泛化成功证据。

---

## 3. C2 稳定结论

C2 执行状态：

```text
13 configs x 5 folds = 65 training runs
protocol = fixed_protocol_no_hyperparam_search
model_type = MLP_3layer
split = circular yaw-block holdout
```

核心结果：

```text
all mean_test_yaw_acc = 0.00%
all std_test_yaw_acc = 0.00%
all mean_test_yaw_correct_count = 0
```

C2 判定：

```text
NULL RESULT
```

稳定解释：

```text
在 phase63 fixed-roll circular yaw-block holdout 与固定 MLP 协议下，
当前低维 OCS-only / visibility / mixed non-image features 未达到跨 yaw exact-bin 泛化。
```

---

## 4. C2 配置表

| Config | Claim class | Dim | Yaw acc (%) | Yaw CMAE (deg) | Within-3 (%) | Pitch acc (%) |
|---|---:|---:|---:|---:|---:|---:|
| baseline_4dim | photometric OCS | 4 | 0.00 | 89.25 | 8.16 | 2.56 |
| R_ratio_2d | photometric OCS | 2 | 0.00 | 84.15 | 6.31 | 2.56 |
| R_ratio_3d | photometric OCS | 3 | 0.00 | 80.36 | 10.45 | 2.62 |
| I_interpart_1d | photometric OCS | 1 | 0.00 | 107.78 | 2.75 | 2.69 |
| N_density_3d | photometric OCS | 3 | 0.00 | 120.26 | 3.96 | 3.41 |
| L_logratio_3d | photometric OCS | 3 | 0.00 | 83.17 | 7.70 | 3.18 |
| M1_ratio_log_5d | photometric OCS | 5 | 0.00 | 83.05 | 7.83 | 3.07 |
| M3_density_ratio_5d | photometric OCS | 5 | 0.00 | 97.47 | 10.51 | 3.15 |
| M4_log_density_ratio_9d | photometric OCS | 9 | 0.00 | 115.74 | 12.05 | 4.37 |
| P_pixelfrac_3d | visibility control | 3 | 0.00 | 98.15 | 14.79 | 2.66 |
| M5_pixelfrac_only_4d | visibility control | 4 | 0.00 | 95.75 | 15.57 | 2.59 |
| M2_ratio_pixelfrac_5d | mixed OCS+visibility | 5 | 0.00 | 98.25 | 14.74 | 3.23 |
| M6_all_nongeo_13d | mixed OCS+visibility | 13 | 0.00 | 107.18 | 14.60 | 3.30 |

---

## 5. FIX01 后的指标解释

### 5.1 within-3-bins

标准口径：

```text
72-bin yaw grid 下，若 within-3-bins 按 circular distance <= 3 且包含 exact bin 计算，
chance-level = 7 / 72 = 9.72%。
```

C2 中 `within-3-bins rate` 范围为 `2.75%-15.57%`。部分配置低于 9.72%，部分配置高于 9.72%。这只能解释为局部 coarse localization 或邻域聚集信号，不能替代 exact-bin yaw accuracy。

不得再写：

```text
within-3-bins 略高于随机 8.3%。
```

### 5.2 pitch_acc

标准口径：

```text
Pitch exact-bin accuracy 仅作为二级诊断指标。
```

Pitch 范围为 `2.56%-4.37%`，部分配置达到约 3-4%。但 C2 的成功/失败由跨 yaw holdout 泛化判据决定，pitch 值不改变 C2 null result。

不得再写：

```text
pitch_acc 远低于 yaw weak-positive 3% 阈值。
```

---

## 6. 可写 claim

可以写：

```text
在预注册固定协议与 circular yaw-block holdout 下，13 个 OCS-only 低维特征配置在 5-fold 筛选中均未取得 exact-bin yaw 泛化命中。
```

可以写：

```text
该结果是 fixed-protocol controlled negative result，限定于当前 feature set、MLP 协议和 phase63 fixed-roll yaw-block holdout。
```

可以写：

```text
within-3 指标显示部分配置存在局部邻域聚集，但这种 coarse localization 未转化为 exact-bin yaw accuracy。
```

---

## 7. 不可写 claim

不得写：

```text
OCS 光度在物理上不含姿态信息。
OCS 在所有模型、架构、特征工程或所有任务下都失败。
OCS 已经被证明不如图像通道。
C2 结果可以外推到真实未知目标姿态反演。
GEO 真实光度数据库可提供三轴姿态监督标签。
```

---

## 8. 当前阶段门

```text
C1/C2 evidence package：stable
C2 OCS-only null result：accepted
C3 joint comparison：not released
post-hoc OCS-only rescue：not released
paper Results prose：not released
三轴小项目、路线二/三/四扩展：not released
```

后续若讨论 C3，只能写成“若 Codex 另行放行，可采用的候选独立对照设计”，不能写成 E33 或 Claude 已推荐放行。


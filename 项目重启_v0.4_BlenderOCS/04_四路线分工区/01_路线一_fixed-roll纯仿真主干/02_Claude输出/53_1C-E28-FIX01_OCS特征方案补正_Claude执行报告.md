# 53 1C-E28-FIX01：OCS 特征增强方案补正 Claude 执行报告

最后更新：2026-06-25  
执行端：Claude  
依据审阅：`04_Codex审阅/R52_Codex_审阅_1C-E28需补正_G族与判据修正.md`

**状态：纯方案补正。不写代码、不抽取特征、不训练、不改数据、不启动任何实验执行。**

---

## 0. 补正摘要

```text
R52 Codex 审阅发现 4 项需修正：

  Finding 1：G 族几何特征在 phase63 数据中为常量 → 从主评估移除，改为 sanity check
  Finding 2：P 族是 visibility control，不是 photometric OCS → 收窄论文 claim
  Finding 3：C2 → C3 触发判据过宽 → 收紧
  Finding 4：配置表需要按 claim class 分层 → 增加标注

当前修正仅限方案文本。C1 代码/C2 训练/C3 复验仍为 NOT RELEASED。
```

---

## 1. 修正 1：G 族几何特征 → 常量 sanity check

### 1.1 问题确认

经 Codex 抽查与本轮独立验证确认：

```text
ocs_manifest_v0_4_fullrun.json, 2664 records:
  unique sun_dir = 1  →  sun_dir = (0.957826, 0.0, 0.287348) for all records
  unique det_dir = 1  →  det_dir = (0.445435, -0.890871, 0.089087) for all records
```

这是因为在 phase63 Blender 设置中，太阳方向和探测器方向在世界坐标系中固定，而卫星绕自身轴旋转（yaw/pitch）。sun_dir/det_dir 作为世界坐标系向量不随卫星姿态改变。

因此 E28 原方案中 `G1 phase_angle_cos`、`G2 sun_z`、`G3 det_z` 将是全数据集常量列，作为模型输入不提供任何变化信息。

### 1.2 修正方案

```text
G 族从 C2 主评估中移除，改为：
  "constant sanity check"

用途（仅用于 C1 实现时的自检）：
  - 确认特征提取脚本正确读取了 manifest 字段；
  - 若该列在输出中不是常量，说明特征提取脚本有 bug；
  - 不进入 C2 训练筛选，不进入 C3。

配置变更：
  移除：G_geometry_3d（原 08 号）
  替代：新增 constant_check_1d → 仅作为代码自检，不参与 C2 评估
```

G 族在方案文档中的描述修改为：

```text
族 G（已移除出主评估）：
  原设计为 sun_dir/det_dir 派生的几何显式特征。
  经数据验证，在 phase63 fixed-roll 设置中 sun_dir 和 det_dir 为全数据集常量，
  因此 G 族特征为常量列。保留为 C1 实现时的 constant sanity check，
  不进入 C2 主评估——任何后续将其作为非零信息源的尝试都需要重新
  渲染不同 sun/det 配置的数据，且需要独立的 Codex 审阅链。
```

---

## 2. 修正 2：P 族 → visibility / projected geometry control

### 2.1 问题

E28 原方案将 P 族描述为"纯几何特征"并允许与 R/N/L 混合后的配置称为"OCS 特征"。但 P 族的字段来源是：

```text
n_pixels_per_part / n_pixels_contributing  →  部件可见像素占比
n_pixels_contributing / n_pixels_camera_visible  →  光照效率
n_pixels_sun_visible / n_pixels_camera_visible  →  太阳可见比
```

这些是 visibility / projected geometry 信息，来自像素计数而非 OCS 光度积分。它们不包含任何 BRDF 或 photometric 信息。

### 2.2 修正方案

```text
P 族的 claim class 修正为：

  visibility control（可见性对照）

论文口径约束：
  ✓ 若纯 P 族取得正结果 → "可见性几何信息有助于 cross-yaw 泛化"
  ✗ 不得写成 "OCS 光度通道提供 cross-yaw 信息"

含 P 的 mixed 配置（M2/M5/M6）的 claim class 修正为：

  mixed OCS+visibility（OCS 光度 + 可见性混合）

论文口径约束：
  ✓ 若 mixed OCS+visibility 取得正结果 → 必须分别报告 OCS-only 部分
    和 visibility-only 部分的贡献，不得归因于单一通道
  ✗ 不得写成 "OCS 特征增强有效"
```

---

## 3. 修正 3：C2 → C3 触发判据收紧

### 3.1 问题

E28 原判据 `weak_positive: yaw_acc > 0%` 过宽：

```text
- yaw 为 72 类分类，随机命中率 = 1/72 ≈ 1.39%
- 14 个配置同时筛选，任何一个配置的偶然波动都可能触发 C3
- 单个样本命中就会产生 yaw_acc ≈ 0.2%（在 518-555 test samples 中）
- 原判据没有要求额外 split、bootstrap 或 permutation 验证
```

### 3.2 修正后判据

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ C2 结果判定矩阵（修正版）                                                   │
├──────────────────┬──────────────────────────────────────────────────────┤
│ 结果             │ 判据                                                   │
├──────────────────┼──────────────────────────────────────────────────────┤
│ strong_positive  │ 同时满足以下全部条件：                                   │
│                  │  (a) yaw_acc ≥ 10%（即至少 ~52/518 样本正确分类）        │
│                  │  (b) yaw_circular_mae 显著优于 baseline                 │
│                  │      （baseline OCS-only FIX01: 98.3°）                 │
│                  │  (c) yaw_within_3_bins 显著优于 baseline                │
│                  │      （baseline OCS-only FIX01: 待查具体值）             │
│                  │  (d) 不是 visibility-only 配置（避免与几何信息混淆）      │
│                  │ → 触发 C3 joint 复验（需 Codex 审阅放行）                │
│                  │ → 可写成 "OCS 派生特征提供跨 yaw 泛化信息"               │
├──────────────────┼──────────────────────────────────────────────────────┤
│ weak_positive    │ 同时满足以下全部条件：                                   │
│                  │  (a) yaw_acc ≥ max(3%, 2 × random_chance ≈ 2.8%)       │
│                  │      即 yaw_acc ≥ 3%                                   │
│                  │  (b) yaw_circular_mae 优于 baseline 或有至少 1 个        │
│                  │      yaw_within_k 指标优于 baseline                     │
│                  │  (c) 至少通过以下验证之一：                               │
│                  │      - 在另一个 circ_yawblock fold 上复现非零 yaw_acc    │
│                  │      - bootstrap CI（1000 resamples）不含 0%             │
│                  │      - permutation test（shuffle train yaw labels,       │
│                  │        重训 1 次，看 true label 是否显著优于 shuffled）   │
│                  │  (d) 不是仅由单个或少數（<5）样本命中驱动                  │
│                  │ → 触发 Codex 审阅，由 Codex 裁决是否进入 C3               │
│                  │ → 若不进入 C3，仍可写成 "弱信号，需更多证据"              │
├──────────────────┼──────────────────────────────────────────────────────┤
│ null_result      │ 所有 photometric OCS 配置 yaw_acc < 3%，或虽有          │
│                  │ yaw_acc ≥ 3% 但不满足 weak_positive 的 (b)(c)(d)        │
│                  │ → 不触发 C3                                             │
│                  │ → 结论如 E28 §4.1 null_result 所述                       │
│                  │ → 方向 C 闭合（稳健负结果）                               │
├──────────────────┼──────────────────────────────────────────────────────┤
│ invalid          │ NaN loss / 训练不收敛 / 特征计算错误                     │
│                  │ → 返工 C1 脚本                                          │
│                  │ → Codex 审阅特征计算逻辑                                  │
└──────────────────┴──────────────────────────────────────────────────────┘

重要补充规则：
  1. 多配置筛选必须报告全部配置结果（不得只报告最优配置）。
  2. 若 best 配置属于 mixed OCS+visibility class，必须同时报告
     pure photometric OCS class 中的 best 结果。
  3. 单个样本命中（yaw_acc 仅由 <5 个正确分类样本贡献）不得触发 C3。
  4. C3 执行必须经过独立 Codex 审阅放行，Claude 不得自动触发。
```

### 3.3 C3 判据保持不变

C3 的判据（§4.2）在 E28 中已合理，此处仅确认不做修改：

```text
- positive: enhanced_joint yaw_acc > image_only yaw_acc
- no_improvement: 持平
- negative: enhanced_joint < image_only（需诊断）
```

---

## 4. 修正 4：配置表分层 + Claim Class

### 4.1 修正版配置表

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ C2 特征配置评估清单（修正版，预注册）                                           │
├────┬──────────────────────┬──────┬─────────────────────────┬──────────────────┤
│ #  │ 配置名               │ 维数 │ 特征组成                │ Claim Class      │
├────┼──────────────────────┼──────┼─────────────────────────┼──────────────────┤
│    │                      │      │                         │                  │
│    │ A 组：photometric OCS-derived（光度 OCS 派生）                             │
│    │                      │      │                         │                  │
│ 01 │ baseline_4dim        │  4   │ ocs_total, ocs_jin,     │ photometric OCS  │
│    │                      │      │ ocs_tai, ocs_yin        │ (baseline)       │
│ 02 │ R_ratio_2d           │  2   │ r_jin, r_tai            │ photometric OCS  │
│ 03 │ R_ratio_3d           │  3   │ r_jin, r_tai, r_yin     │ photometric OCS  │
│ 04 │ I_interpart_1d       │  1   │ ratio_j_t               │ photometric OCS  │
│ 05 │ N_density_3d         │  3   │ ocs_density_total,      │ photometric OCS  │
│    │                      │      │ ocs_density_jin,        │                  │
│    │                      │      │ ocs_density_tai         │                  │
│ 06 │ L_logratio_3d        │  3   │ log_r_jin, log_r_tai,   │ photometric OCS  │
│    │                      │      │ log_ratio_j_t           │                  │
│ 07 │ M1_ratio_log_5d      │  5   │ R1,R2 + L1,L2,L3       │ photometric OCS  │
│ 08 │ M3_density_ratio_5d  │  5   │ N1,N2,N3 + R1,R2       │ photometric OCS  │
│ 09 │ M4_log_density_ratio │  9   │ L1,L2,L3,L4 +          │ photometric OCS  │
│    │ _9d                  │      │ N1,N2,N3 + R1,R2       │                  │
│    │                      │      │                         │                  │
│    │ B 组：visibility-derived control（可见性几何对照）                          │
│    │                      │      │                         │                  │
│ 10 │ P_pixelfrac_3d       │  3   │ frac_jin, frac_tai,     │ visibility       │
│    │                      │      │ visibility_ratio        │ control          │
│ 11 │ M5_pixelfrac_only_4d │  4   │ P1,P2,P3,P4            │ visibility       │
│    │                      │      │                         │ control          │
│    │                      │      │                         │                  │
│    │ C 组：mixed OCS+visibility（光度 + 可见性混合）                              │
│    │                      │      │                         │                  │
│ 12 │ M2_ratio_pixelfrac   │  5   │ R1,R2 + P1,P2,P4       │ mixed            │
│    │ _5d                  │      │                         │ OCS+visibility   │
│ 13 │ M6_all_nongeo_13d    │ 13   │ R1,R2,I1,N1,N2,N3,     │ mixed            │
│    │                      │      │ P1,P2,P4,L1,L2,L3,L4  │ OCS+visibility   │
│    │                      │      │                         │                  │
│    │ D 组：constant sanity check（常量自检，不进入 C2 评估）                      │
│    │                      │      │                         │                  │
│ 14 │ constant_check_1d    │  1   │ phase_angle_cos         │ constant         │
│    │ （仅 C1 代码自检）   │      │ （预期全数据集常量）     │ sanity check     │
│    │                      │      │                         │                  │
└────┴──────────────────────┴──────┴─────────────────────────┴──────────────────┘

说明：
  - A 组（#01-#09）：photometric OCS-derived。C2 主评估对象。
    所有从 OCS 光度值派生的特征，不含像素计数或几何方向。
  - B 组（#10-#11）：visibility control。独立对照。
    仅使用像素计数字段，完全不含 OCS 光度信息。
    用于区分 "OCS 贡献" vs "几何可见性贡献"。
  - C 组（#12-#13）：mixed OCS+visibility。辅助对照。
    同时包含 OCS 光度派生和像素计数特征。
    若取得正结果，必须分解归因，不得归为单一通道。
  - D 组（#14）：constant sanity check。不参与 C2 训练。
    仅用于 C1 代码实现时验证特征提取正确性。
    若该列在输出中非常量，说明代码有 bug。
```

### 4.2 Claim Class 的论文引用规则

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 论文引用规则（按 claim class）                                         │
├────────────────────┬─────────────────────────────────────────────────┤
│ Claim Class        │ 论文中允许的表述                                  │
├────────────────────┼─────────────────────────────────────────────────┤
│ photometric OCS    │ "OCS-derived feature X shows / does not show    │
│                    │  cross-yaw generalization"                       │
│                    │ "the photometric OCS channel provides / does     │
│                    │  not provide yaw-invariant information"           │
├────────────────────┼─────────────────────────────────────────────────┤
│ visibility control │ "visibility-based geometric features show /      │
│                    │  do not show cross-yaw generalization"            │
│                    │ 不得写成 OCS 贡献                                 │
├────────────────────┼─────────────────────────────────────────────────┤
│ mixed OCS+         │ "Combined photometric and visibility features    │
│ visibility         │  show X. The contribution of each channel        │
│                    │  requires decomposition (see Table Y)."           │
│                    │ 不得归因于单一通道                                 │
├────────────────────┼─────────────────────────────────────────────────┤
│ constant sanity    │ 不进入论文                                        │
│ check              │                                                  │
└────────────────────┴─────────────────────────────────────────────────┘
```

---

## 5. 全部修正点速查

```text
F1. G 族：从主评估移除 → constant sanity check
    - 原 08 G_geometry_3d 移除
    - 新增 14 constant_check_1d，仅 C1 代码自检

F2. P 族：claim class 修正 → visibility control
    - P_pixelfrac_3d 和 M5_pixelfrac_only_4d 归入 B 组
    - 若正结果，只能写成 visibility/geometry 贡献

F3. 含 P 的 mixed 配置：claim class 修正 → mixed OCS+visibility
    - M2 和 M6 归入 C 组
    - 若正结果，必须分解归因

F4. C2 → C3 判据收紧：
    - strong_positive: yaw_acc ≥ 10% + cmae + within_k 同步改善
    - weak_positive: yaw_acc ≥ 3% + 额外验证 + 非单样本驱动
    - 多配置全部报告
    - C3 需 Codex 审阅放行

F5. 配置表分层：A/B/C/D 四组 + claim class 标注
```

---

## 6. 关于后续代码实现的补充约束

以下约束在 C1 代码实现阶段必须遵守（本次不写代码，仅预注册约束）：

```text
1. epsilon / clip / fallback 常数：
   - epsilon = 1e-8（用于 log 和比值分母）
   - ratio clip range = [1e-8, 1e8]
   - log-ratio clip range = [-18.4, 18.4]（对应 ln(1e-8) ~ -18.4）
   - 零像素 fallback：当 n_pixels_part = 0 时，ocs_density = 0.0

2. 归一化：
   - 标准化（mean/std）只能使用训练集统计量
   - 不得跨 fold 使用全局统计量
   - 不得根据 C2 中间结果调整归一化参数

3. 特征选择：
   - 所有预注册配置全部运行，不得根据中间结果删减
   - 事后报告必须包含全部配置的结果

4. 文件命名：
   - 每个配置的输出文件必须包含配置名（如 c2_results_R_ratio_2d.json）
   - 汇总 JSON 必须列出所有 13 个参与评估的配置（#01-#13）
```

---

## 7. 红线确认

- [x] 不写论文正文
- [x] 不写代码
- [x] 不运行特征提取
- [x] 不训练模型
- [x] 不修改数据或 manifest
- [x] 不启动 B1/GGX
- [x] 不启动三轴小项目
- [x] 不启动路线二/三/四
- [x] 不修改 CLAUDE.md、冻结文件或成果区
- [x] 不把方案设计写成已验证结论
- [x] 不自行放行 C1/C2/C3 执行

---

## 附录 A：与 E28 原方案的差异对照

```text
┌──────────────────────────┬─────────────────────┬──────────────────────────┐
│ 项目                     │ E28 原方案           │ E28-FIX01 修正            │
├──────────────────────────┼─────────────────────┼──────────────────────────┤
│ G 族                     │ 几何显式特征，       │ constant sanity check，   │
│                          │ 进入 C2 主评估       │ 不进入 C2                 │
│ P 族 claim               │ 纯几何特征           │ visibility control        │
│ 含 P mixed claim         │ OCS 特征            │ mixed OCS+visibility      │
│ C2→C3 strong_positive    │ yaw_acc ≥ 10%       │ + cmae/within_k 同步改善  │
│ C2→C3 weak_positive      │ yaw_acc > 0%        │ yaw_acc ≥ 3% + 额外验证   │
│ 多配置筛选               │ 未规定              │ 全部报告，不选择性报告     │
│ C3 触发                  │ Claude 可自动触发   │ 必须 Codex 审阅放行       │
│ 配置表分层               │ 无                  │ A/B/C/D 四组 + claim class│
│ 配置数（参与 C2 评估）   │ 13（原 14-1=13）    │ 13（#01-#13）             │
│ 配置数（含自检）         │ 14                  │ 14（含 #14 constant check）│
└──────────────────────────┴─────────────────────┴──────────────────────────┘
```

## 附录 B：下一步路径

```text
当前：E28-FIX01 方案补正（本报告）—— 完成
下一步：本报告提交 Codex 审阅（R53 或后续编号）
  → 若 Codex 通过修正方案：
    放行 C1 特征提取脚本编写
  → 若 Codex 仍有补充修正要求：
    执行 E28-FIX02
  → C2/C3 均需独立的后续 Codex 审阅放行
```

# 52 1C-E28：OCS 特征增强方案设计 Claude 执行报告

最后更新：2026-06-25  
执行端：Claude  
依据审阅：`04_Codex审阅/R51_Codex_审阅_1C-E27通过并放行E28_OCS特征方案设计.md`

**状态：纯方案设计。不写代码、不抽取特征、不训练、不改数据、不启动任何实验执行。**

---

## 0. 方案摘要

```text
本报告设计路线一 C 方向 C（OCS 特征增强探索）的完整方案：

  阶段 C0：OCS manifest 字段盘点（只读，不成文）
  → 阶段 C1：特征提取脚本方案（本报告设计，需 Codex 审阅放行后执行）
  → 阶段 C2：OCS-only strict yaw_block 筛选（需 Codex 审阅放行）
  → 阶段 C3：joint 复验（仅 C2 有正向信号时触发）

当前放行范围：仅 C0 级盘点与 C1 级特征方案设计。
C1 脚本编写、C2 训练、C3 复验均 NOT RELEASED。
```

---

## 1. 阶段 C0：OCS Manifest 字段盘点

### 1.1 现有原始字段

基于 `ocs_manifest_v0_4_fullrun.json` 的单条 record 结构：

```text
┌──────────────────────────────────────────────────────────────────────┐
│ OCS Manifest 原始字段清单（per record）                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ 光度字段（当前模型使用）：                                              │
│   ocs_total              : float  总积分 OCS (m² equivalent)          │
│   ocs_per_part:                                                  │
│     jinshuzhuti          : float  金属主体 OCS                        │
│     taiyangnengban       : float  太阳能板 OCS                        │
│     yinshenban           : float  隐身板 OCS                          │
│                                                                      │
│ 像素计数字段（几何信息，当前模型未使用）：                                │
│   n_pixels_camera_visible : int   相机可见像素数                       │
│   n_pixels_nol_positive   : int   N·O·L > 0 像素数                    │
│   n_pixels_sun_visible    : int   太阳可见像素数                       │
│   n_pixels_contributing   : int   同时相机可见且太阳可见的像素数          │
│   n_pixels_per_part:                                              │
│     jinshuzhuti          : int   金属主体贡献像素数                     │
│     taiyangnengban       : int   太阳能板贡献像素数                     │
│     yinshenban           : int   隐身板贡献像素数                       │
│                                                                      │
│ 几何字段（可用于构造显式几何特征，当前模型未使用）：                       │
│   sun_dir                : [x,y,z] 太阳方向 (world frame)              │
│   det_dir                : [x,y,z] 探测器方向 (world frame)            │
│   yaw_deg                : float  偏航角标签                          │
│   pitch_deg              : float  俯仰角标签                          │
│                                                                      │
│ 固定参数（全数据集相同）：                                              │
│   ortho_scale_m          : float  正交投影尺度                         │
│   pixel_area_m2          : float  单像素面积                           │
│   resolution             : int    256×256                             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 当前模型使用的特征

```text
当前 B0 OCS 特征向量（4 维）：

  f_current = [ocs_total, ocs_jinshuzhuti, ocs_taiyangnengban, ocs_yinshenban]

已知结果（FIX01 strict yaw_block, OCS-only）：
  yaw_acc = 0.00%, pitch_acc = 1.01%, yaw_cmae = 98.3°

结论：4 维原始积分 OCS 在 fixed-roll 单视图下不提供跨 yaw 泛化信息。
```

### 1.3 字段使用红线

```text
以下字段不得直接作为模型输入（标签泄漏），但可用于特征归一化或分析：
  ✗ yaw_deg           → 标签，不得进入特征
  ✗ pitch_deg         → 标签，不得进入特征

以下字段的物理性质区分：
  - 光度字段：受 BRDF × 几何双重影响，yaw 敏感性高但可能含不变性子空间
  - 像素计数字段：纯几何（可见性），不含 BRDF 信息，yaw 敏感性来自遮挡模式
  - 方向字段：已知几何量，可用作显式条件但不增加信息
```

---

## 2. 阶段 C1：OCS 派生特征候选集设计

### 2.1 设计原则

```text
P1. 所有派生特征必须由 OCS manifest 现有字段计算，不重新渲染、不读取图像像素。
P2. 特征公式必须预先注册（本报告），不在看到训练结果后临时构造。
P3. 所有归一化/标准化必须只用训练集统计量（per-fold），不得跨 fold 泄漏。
P4. 特征必须对各部件像素数趋于 0 的极端姿态有明确定义（定义 epsilon 或 fallback）。
P5. 每个候选特征必须标注物理含义、可能的 yaw-invariant 机制、泄漏风险和不适用条件。
```

### 2.2 候选特征族

#### 族 R：Ratio 特征（per-part / total 比率）

```text
物理含义：
  消除绝对 OCS 幅值，保留部件间相对贡献。如果 yaw 主要改变 absolute brightness
  而非 relative part composition，比率特征可能更 invariant。

候选特征：
  R1. r_jinshuzhuti     = ocs_jinshuzhuti / ocs_total
  R2. r_taiyangnengban  = ocs_taiyangnengban / ocs_total
  R3. r_yinshenban      = ocs_yinshenban / ocs_total

  注意：R1 + R2 + R3 = 1，只有 2 个独立自由度。建议保留 R1+R2，或
        R1+R2+R3 全保留但标注冗余。

可能的 yaw-invariant 机制：
  - 如果 yaw 变化主要改变太阳-相机-表面夹角（影响整体亮度），
    比率可部分抵消这种全局调制。
  - 部件可见/遮挡过渡的 yaw 区间可能窄于整体亮度变化的区间。

泄漏风险：
  - 低。比率是 scale-invariant 变换，不引入标签信息。

不适用条件：
  - ocs_total → 0 时（极端 grazing 或部件几乎不可见），比率噪声放大。
    处理：对 ocs_total < epsilon (建议 1e-8) 的记录，比率置为 [1/3, 1/3, 1/3]
    （均匀先验）并附加一个 validity flag。

边缘情况统计（需 C1 脚本确认）：
  - ocs_total min/max 范围
  - ocs_total < 1e-8 的记录数
  - yinshenban OCS 通常极小（~1e-6），r_yinshenban 可能始终 ≈0
```

#### 族 I：Inter-part Ratio 特征（部件间比值）

```text
物理含义：
  进一步消除 total 的中间变量，直接比较部件间 OCS 关系。
  对总亮度的尺度变化完全不变。

候选特征：
  I1. ratio_j_t  = ocs_jinshuzhuti / ocs_taiyangnengban
  I2. ratio_j_y  = ocs_jinshuzhuti / max(ocs_yinshenban, epsilon)
  I3. ratio_t_y  = ocs_taiyangnengban / max(ocs_yinshenban, epsilon)

可能的 yaw-invariant 机制：
  - 部件间 OCS 比例主要由遮挡模式（可见面积比）决定，对 BRDF 参数不敏感。
  - 若两部件同时可见，其 OCS 比例随 yaw 变化可能比绝对 OCS 慢。

泄漏风险：
  - 低。Scale-invariant，无标签依赖。

不适用条件：
  - 分母部件接近不可见时，比值发散。需要设上下界。
  - yinshenban OCS 极小时，I2/I3 几乎无信息。
    处理：log-space 运算（见族 L），并 clip 到 [-10, 10]。

建议：
  - I1 最可能有效（两主要部件均有显著 OCS）。
  - I2/I3 可能信息量极低，作为备选。
```

#### 族 N：Normalized OCS（按像素数归一化）

```text
物理含义：
  将 OCS 分解为 "每像素平均亮度 × 可见像素数"，分离光度与几何。
  OCS_per_pixel = ocs_part / n_pixels_part，反映该部件可见区域的平均 BRDF 响应。

候选特征：
  N1. ocs_density_total    = ocs_total / n_pixels_contributing
  N2. ocs_density_jin      = ocs_jinshuzhuti / max(n_pixels_jinshuzhuti, 1)
  N3. ocs_density_tai      = ocs_taiyangnengban / max(n_pixels_taiyangnengban, 1)
  N4. ocs_density_yin      = ocs_yinshenban / max(n_pixels_yinshenban, 1)

可能的 yaw-invariant 机制：
  - "每像素平均亮度"主要取决于局部 BRDF × 局部入射/出射角。
    在 fixed-roll 下，各部件的局部法向分布是固定的；
    如果局部 BRDF 对各部件近似均匀，ocs_density 可能对 yaw 不太敏感。
  - 分离了几何可见性（像素数）和光度（per-pixel OCS），
    yaw 变化主要通过改变可见像素数影响 OCS，per-pixel 部分可能更稳定。

泄漏风险：
  - 低。仅使用 OCS manifest 内部字段。

不适用条件：
  - 部件像素数 = 0 时未定义。需要 n_pixels_part >= 1 阈值。
  - yinshenban 通常只有 1-2 像素，N4 噪声极大，可能不值得纳入。

与其他族的组合潜力：
  - 比率族 (R) × 密度族 (N) 可交叉：r_density = ocs_density_part / ocs_density_total
  - 这相当于用平均亮度替代积分亮度做比率，可能是更强的分离。
```

#### 族 P：Pixel Fraction 特征（纯几何可见性比例）

```text
物理含义：
  完全不使用 OCS 光度值，只用像素计数。反映 "哪些部件当前可见" 的纯几何信号。
  这是对 BRDF 完全不变的特征族。

候选特征：
  P1. frac_jinshuzhuti    = n_pixels_jinshuzhuti / n_pixels_contributing
  P2. frac_taiyangnengban = n_pixels_taiyangnengban / n_pixels_contributing
  P3. frac_yinshenban     = n_pixels_yinshenban / n_pixels_contributing
  P4. visibility_ratio    = n_pixels_contributing / n_pixels_camera_visible
       （有效光照像素占相机可见像素的比例）
  P5. sun_vis_ratio       = n_pixels_sun_visible / n_pixels_camera_visible
       （太阳可见像素占相机可见像素的比例）

可能的 yaw-invariant 机制：
  - 这是最纯粹的几何特征：yaw 改变姿态→改变各部件投影面积和遮挡关系→
    改变像素占比。在 fixed-roll 条件下，yaw 改变的是卫星绕自身轴旋转，
    遮挡模式的 yaw 依赖性可能比 OCS 绝对值的 yaw 依赖性更结构化。
  - 对小 yaw 区间内，可见像素占比可能是缓慢变化的。

泄漏风险：
  - 低。像素计数不引入标签。

不适用条件：
  - 极端姿态（如仅 1 个部件可见，frac ≈ [1,0,0]），特征退化为常数。
  - yinshenban 像素占比几乎恒为 0。
  - 像素占比仍随 yaw 变化（遮挡边界移动），不是真正 yaw-invariant；
    问题是从 OCS 值中能否学习到这种 yaw→占比的映射并泛化到未见 yaw 区间。

与其他族的关键区别：
  - 族 P 只依赖像素计数（非光度），因此对 BRDF 参数完全不敏感。
  - 如果族 P 在 strict yaw_block 上也 yaw_acc = 0%，则说明
    "纯几何可见性模式同样无法跨 yaw 泛化"——对论文边界结论有价值。
```

#### 族 L：Log/Ratio 稳定化特征

```text
物理含义：
  对族 R 和族 I 做 log 变换。好处：
  - 对称化比值（log(a/b) = -log(b/a)）
  - 压缩极端值
  - 将乘性关系转为加性，适合 MLP 学习

候选特征：
  L1. log_r_jin     = log(r_jinshuzhuti + epsilon)
  L2. log_r_tai     = log(r_taiyangnengban + epsilon)
  L3. log_ratio_j_t = log(max(ocs_jinshuzhuti, epsilon) / max(ocs_taiyangnengban, epsilon))
  L4. log_total     = log(max(ocs_total, epsilon))
  L5. log_density_total = log(max(ocs_density_total, epsilon))

可能的 yaw-invariant 机制：
  - log-ratio 将比率映射到对称空间，MLP 更容易学习加性偏移。
  - log_total 压缩 OCS 的 5-6 个数量级动态范围。

泄漏风险：
  - 低（epsilon 为固定常数，非数据驱动）。

不适用条件：
  - epsilon 的选择可能影响低 OCS 区域的行为。建议 epsilon = 1e-8。
  - log_total 和 log_density_total 可能去除了关键的幅度信息。
```

#### 族 G：几何显式特征（sun_dir / det_dir 派生）

```text
物理含义：
  直接从已知的太阳和探测器方向构造几何特征。
  注意：这些不是 OCS 派生特征，而是已知的观测几何参数。
  在 model-known 条件下使用它们是合法的。

候选特征：
  G1. phase_angle_cos = dot(sun_dir, det_dir)
       （太阳-探测器相位角的余弦）
  G2. sun_z = sun_dir[2]
       （太阳高度角分量）
  G3. det_z = det_dir[2]
       （探测器高度角分量）

可能的 yaw-invariant 机制：
  - 这些是纯粹的观测几何，与 yaw 直接相关（在 fixed-roll 下，
    sun_dir 的 azimuth 与 yaw 有确定性映射）。
  - 与 OCS 特征拼接后，模型可以学习 "给定观测几何下的 OCS 模式"。
  - G1-G3 本质上在告诉模型 "你现在在看哪个方向"——这是 POSITION 而非 OCS 的信息。

关键警告：
  - 这些特征直接编码了 yaw 相关信息（sun_dir azimuth ≈ yaw + offset），
    因此模型可能学会从 G1-G3 推断 yaw，而不是从 OCS 推断 yaw。
  - 在 strict yaw_block holdout 中，如果 G1-G3 的 train/test 分布不同，
    OCS-only 模型的表现改善可能来自几何特征而非 OCS。
  - 这不是 'OCS 特征增强'，而是 '添加已知几何信息'。

建议：
  - G 族单独作为 OCS+Geometry baseline 评估，不与 R/I/N/P/L 族混合评估。
  - 如果 G 族带来 yaw_acc 改善，需小心解释：不是 OCS 提供了信息，
    而是几何先验提供了信息。
  - 论文中需明确指出 "OCS + known geometry" ≠ "OCS alone"。
```

#### 族 M：Mixed / Composite 特征（跨族组合）

```text
物理含义：
  将上述各族的最优候选组合为扩展特征向量。

候选特征（预注册）：
  M1. "Ratio + Log-Ratio"：R1, R2, L1, L2, L3
       → 5 维，覆盖比率 + log 稳定化
  
  M2. "Ratio + Pixel Fraction"：R1, R2, P1, P2, P4
       → 5 维，覆盖光度比率 + 几何可见性
  
  M3. "Density + Ratio"：N1, N2, N3, R1, R2
       → 5 维，覆盖 per-pixel 平均 + 比率
  
  M4. "Log + Density + Ratio"：L1, L2, L3, L4, N1, N2, N3, R1, R2
       → 9 维，最大信息保留
  
  M5. "Pixel Fraction only"：P1, P2, P4, P5
       → 4 维，纯几何基线（零 OCS 光度信息）
  
  M6. "All non-G families"：R1, R2, I1, N1, N2, N3, P1, P2, P4, L1, L2, L3, L4
       → 13 维，综合候选（不含 G 族几何特征）

选择逻辑：
  - M1-M4 是有物理先验指导的精简组合；
  - M5 是纯几何对照，用于区分 OCS 信息与几何信息；
  - M6 是数据驱动兜底，但维数较高（13 维 vs baseline 4 维），
    需注意 2664 样本下 OCS-only MLP 的过拟合风险。

M6 中排除的特征：
  - yinshenban 相关 R3, I2, I3, N4（信噪比极低）
  - G 族（几何显式特征，独立评估）
```

### 2.3 特征候选集汇总

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 特征候选集总览                                                        │
├──────────┬─────────┬──────────────────────────────────┬──────────────┤
│ 族       │ 维数    │ 核心机制                         │ 优先级      │
├──────────┼─────────┼──────────────────────────────────┼──────────────┤
│ Baseline │ 4       │ 原始积分 OCS（对照）              │ —           │
│ R        │ 2-3     │ Scale-invariant 比率             │ ★★★ 必测   │
│ I        │ 1-3     │ 部件间比值                       │ ★★  推荐   │
│ N        │ 1-4     │ Per-pixel 平均 OCS               │ ★★★ 必测   │
│ P        │ 3-5     │ 纯几何像素占比                   │ ★★  推荐   │
│ L        │ 3-5     │ Log 稳定化                       │ ★★  推荐   │
│ G        │ 3       │ 几何显式特征（对照基线）          │ ★   参考   │
│ M1-M4    │ 5       │ 精简跨族组合                     │ ★★★ 必测   │
│ M5       │ 4       │ 纯几何对照                       │ ★★  推荐   │
│ M6       │ 13      │ 综合兜底                         │ ★   备选   │
└──────────┴─────────┴──────────────────────────────────┴──────────────┘

总计：约 12-15 个特征配置需要在 C2 阶段评估。
每个配置训练 1 次 OCS-only strict yaw_block（约 40s/epoch × 20 epochs ≈ 13 min CPU 或 <2 min GPU）。
预计 C2 总计算成本：<30 min GPU。
```

---

## 3. 阶段协议设计

### 3.1 C0：Manifest 字段盘点

```text
内容：
  - 核实 ocs_manifest 每条 record 的所有字段完整性
  - 统计极端值分布（ocs_total min/max、零像素记录数等）
  - 确认 yinshenban 的有效数据比例

输入：ocs_manifest_v0_4_fullrun.json（只读）
输出：字段盘点笔记（不成独立文件，合并进 C1 脚本的 docstring/注释）
执行：C1 脚本开发时附带执行，不单独成阶段
放行状态：C0 已在本文 §1 中完成，无需独立 Codex 审阅
```

### 3.2 C1：特征提取脚本方案 → 代码开发 + 审阅

```text
内容：
  - 编写 feature_extract_ocs.py
  - 输入：ocs_manifest JSON + split_manifest JSON
  - 输出：增强特征矩阵 + 特征定义 JSON
  - 包含所有候选特征族的计算逻辑
  - 包含边缘情况处理（零像素、极小 OCS）
  - 包含 per-fold 训练集统计归一化选项

关键设计约束：
  - 特征计算函数必须是纯函数（输入 manifest dict → 输出 numpy array）
  - 归一化参数（mean/std）必须从训练集计算，应用到 val/test
  - 每个特征配置以 feature_set_name 标识
  - 输出格式兼容现有 Dataset 类的 OCS 输入接口

产物：
  - 06_v0.4_code/07_training/feature_extract_ocs.py
  - 特征定义文档（内嵌于脚本 docstring）

放行状态：NOT RELEASED — 需独立 Codex 审阅（R52 或后续）
执行端：Claude 写代码 → Codex 审阅
```

### 3.3 C2：OCS-only Strict Yaw Block 筛选

```text
内容：
  - 使用 FIX01 的 yaw_block split（train 0-280°, test 320-355°）
    或 circ_yawblock fold_0（作为代表性单折）
  - 对每个特征配置训练 OCS-only 模型
  - 训练协议固定：20 epochs, lr=1e-3, seed=42, OCS-only MLP
  - 报告 per-config strict test 指标

关键约束：
  - 协议与 FIX01 OCS-only 完全一致（仅特征不同），确保可比
  - 不做超参调优（避免过拟合到 single split）
  - 不做特征选择（所有预注册配置全部跑，不根据中间结果删减）

产物：
  - per-config OCS-only 训练结果 JSON
  - 汇总对比表

放行状态：NOT RELEASED — 需 C1 通过后独立 Codex 审阅放行
执行端：Claude 运行训练 → 汇总报告
```

### 3.4 C3：Joint 复验（条件触发）

```text
触发条件：
  C2 中至少 1 个特征配置的 strict yaw_block yaw_acc > 0%

内容：
  - 将最优候选特征加入 joint (image + enhanced OCS) 模型
  - 在相同 yaw_block split 上训练
  - 对比 enhanced joint vs baseline image_only vs baseline joint

协议：
  - 训练 20 epochs, lr=1e-3, seed=42, GPU
  - 如果 C2 有多个非零配置，选 yaw_acc 最高的 1-2 个进入 C3

产物：
  - enhanced joint 训练结果 JSON
  - 对比分析

放行状态：NOT RELEASED — 需 C2 完成后独立 Codex 审阅放行
注意：只有 C2 确实产生 yaw_acc > 0% 时才触发。若 C2 全零，C3 不执行。
```

---

## 4. 成功/失败判据

### 4.1 C2 判据（OCS-only 筛选）

```text
┌─────────────────────────────────────────────────────────────────────┐
│ C2 结果判定矩阵                                                      │
├────────────────────┬────────────────────────────────────────────────┤
│ 结果               │ 判据                                           │
├────────────────────┼────────────────────────────────────────────────┤
│ strong_positive    │ 任一配置 yaw_acc ≥ 10%                         │
│                    │ → 触发 C3 joint 复验                            │
│                    │ → 可写成 "OCS 派生特征提供跨 yaw 泛化信息"       │
├────────────────────┼────────────────────────────────────────────────┤
│ weak_positive      │ 任一配置 0% < yaw_acc < 10%                    │
│                    │ → 触发 C3 joint 复验（但预期管理更保守）         │
│                    │ → 需确认非随机波动（可加 bootstrap CI）          │
│                    │ → 写成 "OCS 派生特征提供有限的跨 yaw 信息"       │
├────────────────────┼────────────────────────────────────────────────┤
│ null_result        │ 所有配置 yaw_acc = 0.00%                       │
│                    │ → 不触发 C3                                    │
│                    │ → 结论："在 fixed-roll 单视图条件下，从 4 维     │
│                    │   积分 OCS 可派生的比率/密度/像素占比/对数等     │
│                    │   特征均不具备跨未见 yaw 区间的泛化信息。"       │
│                    │ → 对论文是有效负结果，闭合 §E.3.3 和 §E.6       │
├────────────────────┼────────────────────────────────────────────────┤
│ degraded           │ 某些配置 yaw_acc 比 baseline 4-dim 更低         │
│                    │ （baseline = 0.00%，所以只能持平）              │
│                    │ → 基本不可能出现（不可能低于 0%）                │
│                    │ → 但若出现训练不收敛等情况，标记为 degraded      │
│                    │   并要求 Codex 返工诊断                          │
├────────────────────┼────────────────────────────────────────────────┤
│ invalid            │ NaN loss / 训练不收敛 / 特征计算错误             │
│                    │ → 返工 C1 脚本                                  │
│                    │ → Codex 审阅特征计算逻辑                         │
└────────────────────┴────────────────────────────────────────────────┘
```

### 4.2 C3 判据（Joint 复验）

```text
仅 C2 = strong_positive 或 weak_positive 时触发。

┌────────────────────┬────────────────────────────────────────────────┐
│ 结果               │ 判据                                           │
├────────────────────┼────────────────────────────────────────────────┤
│ positive            │ enhanced_joint yaw_acc > image_only yaw_acc   │
│                    │ （在相同 strict yaw_block 上）                  │
│                    │ → OCS 增强特征 + 图像通道存在互补性              │
│                    │ → 论文 §E.6 可写入正结果                        │
├────────────────────┼────────────────────────────────────────────────┤
│ no_improvement     │ enhanced_joint yaw_acc = image_only yaw_acc    │
│                    │ （两者均为 0.00%）                              │
│                    │ → OCS 增强特征在图像存在时不提供额外信息         │
│                    │ → 论文写成 "OCS 增强特征不能突破图像通道的       │
│                    │   yaw 泛化瓶颈"                                 │
├────────────────────┼────────────────────────────────────────────────┤
│ negative            │ enhanced_joint yaw_acc < image_only yaw_acc   │
│                    │ → OCS 增强特征引入了噪声，干扰了图像通道         │
│                    │ → 需诊断是否是特征归一化问题                     │
│                    │ → 若确认，写成 "非信息性 OCS 特征可损害          │
│                    │   joint 模型性能"                               │
└────────────────────┴────────────────────────────────────────────────┘

参考基线（FIX01 strict yaw_block）：
  image_only yaw_acc = 0.00%
  joint yaw_acc      = 0.00%
  → image_only 和 joint 在 strict holdout 上 yaw_acc 相同（均为 0%），
    所以 C3 只能检测 ">0%" 或 "=0%"，不可能出现 "<0%"。
    上述 negative 判定仅在 C2 有弱正信号但 C3 中 joint 比 image_only 差时成立。
```

### 4.3 整体方向 C 闭合判据

```text
方向 C 闭合条件（满足任一即闭合）：

  1. C2 出现 strong_positive → C3 完成 → 方向 C 闭合（正结果）
  2. C2 出现 weak_positive → C3 完成 → 方向 C 闭合（弱正结果）
  3. C2 全 null_result → 方向 C 直接闭合（稳健负结果），不触发 C3

方向 C 不闭合条件：
  - C2 出现 invalid/degraded → 返工 C1 → 重跑 C2
  - C3 出现 invalid/degraded → 返工 → 重跑 C3
```

---

## 5. 输出产物与路径规划

### 5.1 C1 产物

```text
代码：
  06_v0.4_code/07_training/feature_extract_ocs.py
    - 特征计算函数（纯函数）
    - 每族的 compute_ocs_features_<family>() 
    - 统一入口 extract_all_candidate_features()
    - 特征定义 JSON 导出

特征定义文件：
  v0.4_results/04_ocs_features/feature_definitions.json
    - 每个 feature_set 的名称、维度、族、公式描述

增强特征数据（从现有 manifest 派生）：
  v0.4_results/04_ocs_features/enhanced_ocs_features.npz 或 .json
    - shape: (2664, max_feature_dim) 或 per-config 分文件
```

### 5.2 C2 产物

```text
per-config 训练结果：
  v0.4_results/04_ocs_features/c2_screening/
    ├── c2_screening_summary.json          (汇总对比表)
    ├── baseline_4dim/
    │   └── c2_results_baseline_4dim.json  (对照)
    ├── R_ratio/
    │   └── c2_results_R_ratio.json
    ├── N_density/
    │   └── c2_results_N_density.json
    ├── M1_ratio_log/
    │   └── c2_results_M1_ratio_log.json
    └── ... (per-config)
```

### 5.3 C3 产物（条件触发）

```text
joint 复验结果：
  v0.4_results/04_ocs_features/c3_joint_verification/
    ├── c3_joint_summary.json
    └── c3_results_enhanced_joint.json
```

---

## 6. 关键风险与缓解

```text
风险 1：fixed-roll 条件下 OCS 对 yaw 的敏感性根植于物理
  描述：在 fixed-roll 单视图下，yaw 改变 = 卫星绕自身轴旋转，
        不同部件的可见性模式必然改变。OCS（无论怎么变换）的基础
        信号已经携带 yaw 信息——问题是这种 yaw→OCS 映射在未见 yaw
        区间是否可泛化。答案可能是否定的。
  缓解：
    - 族 P（纯几何像素占比）是对此假设的最直接测试。
      如果连纯几何信息都无法跨 yaw 泛化，说明不是 OCS 的问题，
      而是单视图 fixed-roll 条件下的 yaw 信息本质上不可迁移。
    - 无论结果如何，都有科学价值。

风险 2：yinshenban OCS 几乎为零，拖累比率特征
  描述：yinshenban 在大多数姿态下仅 1-2 像素可见，
        OCS ≈ 1e-6，比率特征中几乎为常数。
  缓解：
    - 优先使用含 yinshenban 比率和不含的两组对比。
    - 若 yinshenban 确无信息，族 R/N 只用两主要部件。

风险 3：特征维度增加导致 OCS-only MLP 过拟合
  描述：OCS-only MLP 参数量小，M6 的 13 维可能在 2664 样本
        （train 仅 ~1850）上过拟合。
  缓解：
    - M6 作为备选，优先评估低维组合 M1-M4。
    - C2 使用 strict holdout（train/test yaw 不重叠），
      过拟合会直接表现为 test yaw_acc = 0%，不会产生假阳性。

风险 4：G 族几何特征带来假阳性
  描述：sun_dir/det_dir 直接编码 yaw 信息。
        在 strict yaw_block 下，train 的 sun_dir azimuth 范围
        与 test 不同，模型可能无法泛化，G 族可能也是 0%。
        但若 G 族确实非零，需要严格区分 "OCS 贡献" vs "几何先验贡献"。
  缓解：
    - G 族独立评估，不与其他族混合。
    - 论文中必须明确 "OCS + geometry" ≠ "OCS alone"。

风险 5：单折筛选假阳性
  描述：C2 用单折 yaw_block 筛选，可能存在偶然性。
  缓解：
    - 若 C2 出现 weak_positive，建议在进入 C3 前用另一折验证。
    - C3 joint 复验使用相同 split，一致性检查即可。
```

---

## 7. 红线确认

- [x] 不写论文正文
- [x] 不写代码（本报告为方案设计，不含可执行代码）
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

## 附录 A：特征族与物理机制速查

```text
族 R (Ratio):          ocs_part / ocs_total        → 消除绝对亮度变化
族 I (Inter-part):     ocs_part_a / ocs_part_b     → 部件间相对关系
族 N (Normalized):     ocs_part / n_pixels_part    → 分离光度与可见性
族 P (Pixel Fraction): n_pixels_part / total_pixels → 纯几何，BRDF 不变
族 L (Log):            log(R/I/N 特征)              → 动态范围压缩 + 对称化
族 G (Geometry):       sun_dir / det_dir 派生       → 显式几何先验（对照）
族 M (Mixed):          跨族组合                      → 精简 + 综合方案
```

## 附录 B：C2 特征配置评估清单（预注册）

```text
01  baseline_4dim         : [ocs_total, ocs_jin, ocs_tai, ocs_yin]     ← 对照
02  R_ratio_2d            : [r_jin, r_tai]                             ← 必测
03  R_ratio_3d            : [r_jin, r_tai, r_yin]                      ← 参考
04  I_interpart_1d        : [ratio_j_t]                                ← 推荐
05  N_density_3d          : [ocs_density_total, ocs_density_jin, ocs_density_tai] ← 必测
06  P_pixelfrac_3d        : [frac_jin, frac_tai, visibility_ratio]     ← 推荐
07  L_logratio_3d         : [log_r_jin, log_r_tai, log_ratio_j_t]      ← 推荐
08  G_geometry_3d         : [phase_angle_cos, sun_z, det_z]            ← 对照（独立评估）
09  M1_ratio_log_5d       : [r_jin, r_tai, log_r_jin, log_r_tai, log_ratio_j_t] ← 必测
10  M2_ratio_pixelfrac_5d : [r_jin, r_tai, frac_jin, frac_tai, visibility_ratio] ← 必测
11  M3_density_ratio_5d   : [ocs_density_total, ocs_density_jin, ocs_density_tai, r_jin, r_tai] ← 推荐
12  M4_log_density_ratio_9d : 9-dim 综合                               ← 推荐
13  M5_pixelfrac_only_4d  : [frac_jin, frac_tai, frac_yin, visibility_ratio] ← 纯几何对照
14  M6_all_nongeo_13d     : 13-dim 综合兜底                            ← 备选

总计：14 个配置。
预计 C2 总计算时间（OCS-only × 14 configs × 20 epochs, GPU）：
  14 × ~5s/epoch × 20 epochs ≈ 23 min GPU
```

## 附录 C：下一步路径

```text
当前：E28 方案设计（本报告）—— 完成
下一步：本报告提交 Codex 审阅（R52 或后续编号）
  → 若 Codex 通过 C1 方案设计：
    放行 E29：C1 特征提取脚本编写
  → 若 Codex 要求修改方案：
    返工 E28 方案，修改后重新提交
  → C2/C3 均需独立的后续 Codex 审阅放行
```

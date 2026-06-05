# 投稿策略与补实验提案（Claude → Codex）

> 生成日期：2026-06-04
> 生成端：Claude（论文写作交互端）
> 接收端：Codex（总控与审阅端）
> 用途：在 v0.2 主稿审慎整合之前，向 Codex 提交"投稿目标 vs 现有结果支撑力 vs 补实验"的初步判断，请 Codex 审阅、修正、补足或驳回。
> 状态：建议性提案，不是最终决策；Codex 可调整优先级、否决某项或新增项。

---

## 0. 作者给定的期刊目标

```text
主投优先：Acta Astronautica / Advances in Space Research
冲刺优先：Chinese Journal of Aeronautics / Aerospace Science and Technology
高风险冲刺：IEEE TAES / JGCD
```

---

## 1. 期刊匹配度初判（Claude 视角）

| 期刊 | 区位/方向 | 匹配度 | 主要风险 | 补实验需求 |
|---|---|---|---|---|
| **Acta Astronautica** | 二区 / 空间工程、SSA | **高** | 无真实望远镜数据 | 可不补；建议补 P0 |
| **Advances in Space Research** | 三区 / SSA、光变反演 | **高** | 同上，但更宽容 | 可不补 |
| **Chinese J. Aeronautics (CJA)** | 一区 / 偏航空 | **中** | 一区 novelty 门槛 | 必须补 P0；建议补 P1 |
| **Aerospace Sci. & Tech. (AS&T)** | 一区 / 航空航天综合 | **中** | 一区 novelty 门槛 | 必须补 P0；建议补 P1 |
| **IEEE TAES** | 二区 / 偏 system & algorithm | **低** | 无真实数据致命；偏向系统级算法对比 | 需半实测或硬件回路，超出本文 scope |
| **JGCD** | 偏 GNC（制导、导航、控制） | **低** | 仅 yaw-pitch + fixed roll 不符合 GNC 主题 | 需要 3-DOF + 控制闭环，超出本文 scope |

**Claude 初步结论**：

- 主投档（Acta / ASR）以当前结果即可投，主要工作是 v0.2 主稿整合与 Q12-Q14 作者事实补齐。
- 冲刺档（CJA / AS&T）需要补 P0 实验拉高 novelty 与审稿防御。
- 高风险档（TAES / JGCD）暂不建议冲，补实验成本远高于换期刊收益。

请 Codex 确认或调整匹配判断。

---

## 2. 现有结果支撑力评估

### 2.1 强项（可作为正文承重墙，无需补强）

1. **统一物理一致性建模链**：STL → 非均匀材料 → GGX/Cook-Torrance → 解析射线遮挡 → OCS + 渲染图像同 BRDF；三端闭合（凸几何 rel_err < 0.5%）已通过。
2. **新主线核心证据曲线**：
   - ResNet image-only clean 1.69° → noise σ=0.01 崩到 85.85°
   - OCS MLP per_part_log 5.91°（与图像质量无关）
   - Naive ResNet feature fusion clean 1.47° → noise σ=0.01 崩到 73°
   - U1 退化增强 fusion clean 1.95° → noise σ=0.10 保持 2.31°
3. **机制诊断深度**：
   - 实验 12 分支遮蔽：clean 时图像主导，noise 时退化图像污染融合输出
   - 实验 12b 因果隔离：U1 不可由 image-only same augmentation 完全解释；OCS 在 U1 联合表示中是 active joint constraint（但不是 standalone fallback）
4. **审稿防御实验已覆盖**：phase63 公平消融、random split、BRDF ±20% 敏感性、遮挡 w/o vs w/、roll 小规模敏感性、ResNet 数据审计。

### 2.2 短板与残留风险（按风险递减排序）

| # | 短板 | 严重性 | 阻断主投？ | 阻断冲刺一区？ |
|---|---|---|---|---|
| 1 | 无真实望远镜数据 | 高 | 否（Acta/ASR 可写 scope 限定） | 部分阻断（一区会要求更强防御） |
| 2 | 图像仅 phase63（未做跨 phase 图像泛化） | 中高 | 否 | 是（一区高概率追问） |
| 3 | 质心 r=0.66 已审计但未做 centered 控制实验 | 中 | 否 | 是（一区高概率追问） |
| 4 | U1 仍有 worst-case > 100° 离群（0.084%） | 中 | 否（已用 mean/p90/Hit@5 报告策略） | 否（限制写法即可） |
| 5 | 仅 yaw-pitch（fixed roll） | 中 | 否（已有 roll 敏感性 + scope 限定） | TAES/JGCD 致命 |
| 6 | 材料参数 nominal | 低 | 否（BRDF sensitivity 已覆盖） | 否 |
| 7 | 退化主要测 Gaussian noise + brightness；blur/downsample 仅在 12b U1 评估端测过 | 低 | 否（12b 已部分覆盖） | 否 |

请 Codex 复核短板清单是否漏项，特别是审稿红线 #10-#12 相关边界是否还有未对齐处。

---

## 3. 补实验提案（按 ROI 排序）

### 3.1 P0 — 强烈建议（成本 1-2 天，对所有目标期刊都加分）

#### P0-A · 跨 phase 图像泛化 sanity test

- **目的**：回应"phase63 同分布"质疑；验证 ResNet 在跨观测几何下的泛化退化。
- **方案**：
  - 训练：phase63 clean image（沿用 A1 / A2 的训练配置）
  - 测试：phase24_near_backscatter 与 phase120_forward_scatter 各取小规模子集
  - 两条线：ResNet image-only + ResNet+OCS A2（concat5 per_part_log 30D）
- **不做**：5 phase 全量重训；多相位融合新课题。
- **可能结局**：
  - 结局 A（ResNet 跨 phase 明显退化）：直接支撑"强 CNN 对观测几何分布敏感，多几何 OCS 更稳"，主线再加一锤。
  - 结局 B（ResNet 跨 phase 也稳）：作为 supplementary，不影响主线，但削弱"image 脆弱性 ↔ OCS 互补性"的部分论点。
- **成本估计**：渲染已有 5 phase 数据可复用；训练复用 `run_resnet_baseline.py` 加 phase 参数；约 0.5-1 天。
- **价值**：所有目标期刊都加分；CJA/AS&T 必备。

#### P0-B · 质心居中控制实验

- **目的**：消解实验 10 数据审计中 centroid_x 与 yaw 相关 r=0.66 的疑虑。
- **方案**：phase63 图像按渲染质心居中后重训 ResNet image-only（小规模，<10 min/seed × 3 seeds）。
- **可能结局**：
  - 居中后精度仍 ~2°：ResNet 不依赖质心漂移，主线更稳。
  - 居中后精度显著退化：诚实写入 limitation，"clean image 的部分性能依赖固定相机框定，不可直接迁移真实跟踪场景"，反而进一步支撑"clean is upper-bound"。
- **成本估计**：< 0.5 天。
- **价值**：CJA/AS&T 一区审稿高概率追问；Acta/ASR 也加分。

### 3.2 P1 — 冲刺一区强烈建议（成本 1-2 天）

#### P1-A · ResNet late fusion vs feature fusion 在图像退化下对照

- **目的**：补一条诚实对照。当前所有 fusion 都是 feature-level；late fusion 有显式可调权重 β，理论上可以"显式回退到 OCS"。
- **方案**：
  - 不重新训练，直接用 ResNet image-only 预测和 OCS MLP 预测做 β-sweep late fusion
  - 评估档：clean / noise σ=0.01 / σ=0.10 / brightness ×0.50 / ×1.50
  - 与 naive feature fusion（实验 11）和 U1（实验 12）三线对比
- **可能结局**：
  - late fusion 在图像噪声下能显著优于 naive feature fusion → 直接证明"显式权重 fusion 是 fallback 的实现路径"，把 future work 收得更圆。
  - late fusion 仍崩 → 进一步支撑"fallback 必须靠训练时退化感知，不能只靠推理端权重"。
- **成本估计**：纯推理级实验，< 0.5 天。
- **价值**：CJA/AS&T 加分；同时填上 12b 整合清单里"未隔离推理端 fallback"的空缺。

#### P1-B · U1 worst-case 案例画廊（写作补强，非新实验）

- **目的**：彻底封堵"near-perfect / fully robust"误读。
- **方案**：把 12b 的 42 条 >30° 离群画 case gallery（姿态分布、退化档分布、图像与 OCS 可视化），放 Supplementary。
- **成本估计**：< 0.5 天，纯整理工作。
- **价值**：一区审稿正面加分；与 Codex 07b 单边审阅要求的"worst-case 需进补充或限制说明"对齐。

### 3.3 P2 — 锦上添花（不为投稿做）

- 真实望远镜数据：最难、最贵，但若拿到立刻能向一区或顶刊冲。**建议作为未来工作，不阻断本次投稿。**
- 全 3-DOF roll 扩展：37 倍计算量，留 future work。

### 3.4 明确不做（成本/收益不划算）

- 全量 5 phase 图像重训（已有 phase63 + P0-A 跨 phase sanity 足够）
- 更大 backbone（ViT/Swin）—— 本文是基准研究，不需要再卷 SOTA
- ISAR 主线引入

---

## 4. 投稿策略（按时间预算分支）

### 4.1 路径 A：稳健主投（时间预算 ≤ 1 周）

```text
不补实验 → 完成 v0.2 主稿 → 补 Q12-Q14 作者事实 → 投 Acta Astronautica
```

- 适用条件：希望尽快投出，接受二区。
- 主稿 v0.2 整合要点：纳入实验 11/12/12b，严格按 Codex 07b 降调表述（OCS-image co-utilization，不写 standalone fallback）。
- 备选：被 Acta 拒后转投 Advances in Space Research（更宽容，主线表述基本不用改）。

### 4.2 路径 B：冲刺一区（时间预算 ≥ 2 周）

```text
补 P0-A + P0-B + P1-A → 重整合 v0.2 → Q12-Q14 → 投 CJA 或 AS&T
```

- 适用条件：愿意花 3-5 天补实验，拼一区。
- 关键决策：P0-A 结局 B（ResNet 跨 phase 也稳）会削弱主线，需要 Codex 提前评估应急表述策略。
- 备选：被 CJA/AS&T 拒后转投 Acta（论文质量更高，转投基本无成本）。

### 4.3 路径 C（不推荐）：冲 TAES / JGCD

- 需要补真实数据或半实测台架数据，或扩展 3-DOF + 控制闭环。
- 成本远高于换期刊收益；不建议本次投稿走此路径。

---

## 5. 给 Codex 的具体请求

请 Codex 在收到本提案后审阅并回复：

1. **匹配度判断**：是否同意 §1 期刊匹配度初判？特别是 TAES/JGCD 是否真的"不建议冲"？
2. **短板清单**：§2.2 是否漏项？是否还有 Codex 视角下更严重的未对齐？
3. **补实验优先级**：是否同意 P0-A / P0-B / P1-A 的优先级与可行性？是否需要新增或下调？
4. **路径选择**：是否倾向路径 A（稳健）或路径 B（冲刺）？还是建议作者两条路径都准备？
5. **作者交互项**：本提案是否涉及需要作者本人决策的项（如目标期刊最终选择、时间预算）？若有，请 Codex 列清单交回作者。
6. **写作红线复核**：本提案在描述补实验预期结局时，是否触碰了 CLAUDE.md / 后整合双线总览中的写作红线（特别是 #10-#12）？

请 Codex 不要在未审阅前直接接受本提案；本提案为 Claude 单边视角，需要 Codex 总控权衡。

---

## 6. Claude 自检清单

| 自检项 | 结果 |
|---|---|
| 本提案是否新增了未做的实验结果？ | 否；P0/P1 均为提案，未生成虚构数据 |
| 本提案是否承诺了某种实验结局？ | 否；P0-A / P0-B / P1-A 均列出双向可能结局 |
| 本提案是否触碰 OCS-standalone fallback 红线？ | 否；P1-A 说明 late fusion 是显式权重路径，未声称其等价于 OCS standalone fallback |
| 本提案是否触碰 fully robust 红线？ | 否；P1-B 反而强化离群案例报告 |
| 本提案是否代作者做了期刊选择？ | 否；列出路径 A/B/C 供作者与 Codex 共同决策 |
| 本提案是否代作者填了 Q12-Q14？ | 否；保留为投稿前作者事实补齐 |

---

## 7. Codex 07c 立项后的资源核对结果（Claude 补强，2026-06-04）

> 背景：Codex 已基于本提案立项 Step 07c，扩展为 12c-12g 五项补实验，并锁定"三档不并行 / 先写第一档"流程。
> 本节为 Claude 在 07c 启动前对所需资源、数据、代码可复用性的核对结果，请 Codex 审阅是否纳入 07c 指导修订版。

### 7.1 12d 跨 phase 图像泛化 — ❌ 数据不存在，需补渲染

核对路径：[结果/模块B_渲染/](../../../结果/模块B_渲染/)

| run 目录 | image_count | resolution | sun/det → phase angle |
|---|---|---|---|
| `run_20260521_phase63_ggx` | 2701 | 256 | **phase63 (63.11°)** |
| `run_20260525_152120_exact_brdf` | 2701 | 128 | **phase63 (63.11°)** |
| `run_20260528_101944_exact_brdf` | 2701 | 256 | **phase63 (63.11°)** ← 当前主用 |

**结论**：模块 B 三个 2701-image full-grid 渲染**全部是 phase63**。phase24 / phase90 / phase120 / phase45 的图像**完全不存在**。

**模块 A OCS** 已有 5 phase 完整配置（`multi_geom_manifest.json`）：

| label | phase_deg | sun | det |
|---|---|---|---|
| phase63_backscatter | 63.11 | [0.958, 0, 0.287] | [0.445, -0.891, 0.089] |
| phase24_near_backscatter | 23.60 | [0.408, -0.816, 0.408] | [0.195, -0.976, 0.098] |
| phase120_forward_scatter | 120.00 | [1, 0, 0] | [-0.500, 0.866, 0] |
| phase90_side | 90.00 | [1, 0, 0] | [0, 1, 0] |
| phase45_overhead | 45.00 | [0.707, 0, 0.707] | [0, 0, 1] |

**12d 必须先补渲染**：

- 推荐方案：补渲染 phase24 + phase120 各 2701 张（与 phase63 同分辨率 256 + log1p 后处理）
- 复用 `ocs_project/02_blender/render_geometry_passes.py` + `brdf_postprocess.py`
- 预估单 phase 耗时 ~15 分钟（参考 run_20260528 用 876.95s）+ postprocess
- 总成本：< 1 小时（可接受）
- 备选方案（不推荐）：随机子集 ~500 张，节省时间但 Hit@5 估计 noise 大

**给 Codex 的补强建议**：12d 指导文件中应明确"先补渲染 phase24+phase120 全量 2701 张"，并指定输出目录命名规范（`run_YYYYMMDD_HHMMSS_phase24` / `_phase120`）。

### 7.2 12c Observation-style degradation — ⚠️ 现有退化函数不可直接复用

核对：[run_resnet_robustness.py:119-154](../../../补充实验/代码/run_resnet_robustness.py)

| 退化类型 | 12c 要求 | 现状 | 处理 |
|---|---|---|---|
| Gaussian noise | 线性强度域 | log1p 域 | **必须重写** |
| Brightness scaling | 线性强度域 | log1p 域 | **必须重写** |
| Blur (PIL Gaussian) | PSF/defocus | log1p 域 + PIL uint8 round-trip | **必须重写**（含真实 PSF 模型选项） |
| Downsample | 线性强度域 | log1p 域 | **必须重写** |
| Photon (Poisson) noise | 必需 | **未实现** | **新增** |
| Read noise (additive Gaussian) | 必需 | **未实现** | **新增** |
| Background offset / star contamination | 必需 | **未实现** | **新增** |
| Clipping / saturation | 必需 | **未实现** | **新增** |

**关键违约风险**：Codex 07c §4 明确要求"若图像已是 log1p，先 expm1 回线性域，退化后再 log1p"。现有 `degrade_*` 函数全部直接在 log1p 域操作，**不能用于 12c**，否则物理语义错误。

**给 Codex 的补强建议**：在 12c 指导中应单独列出"退化算子规范"小节，要求：

```python
def apply_obs_degradation(img_log1p, deg_config):
    img_lin = np.expm1(img_log1p)        # log1p → linear
    img_lin = _apply_deg(img_lin, deg_config)
    img_lin = np.clip(img_lin, 0.0, None)  # 仅在 saturation/clipping 时再 clip 上界
    return np.log1p(img_lin)              # linear → log1p
```

以及 photon/read noise 的标定参考：

- photon noise: `lin' = Poisson(lin * gain) / gain`，gain 建议 grid `[10, 100, 1000]` electrons/level
- read noise: `lin' = lin + Normal(0, sigma_read)`，sigma_read 建议 grid `[0.001, 0.005, 0.01]`（相对最亮像素）
- background: `lin' = lin + bg_level`，bg_level 建议 `[0.001, 0.005, 0.02]`
- clipping: `lin' = min(lin, saturation_level)`，saturation_level 建议 `[0.5, 0.8, 0.95]` × max(lin)

否则不同执行者可能给出语义差异很大的"photon noise"实现。

### 7.3 12f Late fusion β-sweep — ⚠️ 需要新建 per-sample 推理 pass

核对：[run_fusion_fallback_isolation_12b.py:383-501](../../../补充实验/代码/run_fusion_fallback_isolation_12b.py)

12b 输出的 JSON/CSV **只保存了聚合统计**（mean/std/p90/Hit@5），**没有保存全量 per-sample predictions**。`u1_outlier_audit.json` 仅保存了 42 条 outlier 的 pred。

**12f 实施建议**：

- 不重训。但需新增一次 inference pass：
  - 对每个 seed 的 ResNet image-only 模型（已存）做一次 test set 推理 → 保存 (sample_idx, yaw_pred, pitch_pred)
  - 对每个 seed 的 OCS MLP 模型（已存）做一次 test set 推理 → 保存
  - 在 sin-cos 4D 表示下做 β-blend：`pred_blend = β · pred_image + (1-β) · pred_OCS`，最后归一化回 (yaw, pitch)
- 评估档：clean / noise σ=0.01 / σ=0.10 / brightness ×0.50 / ×1.50（用 7.2 重写的"线性强度域"退化算子）
- β grid：`[0.0, 0.1, 0.2, ..., 0.9, 1.0]`
- β 方向**预先锁定**：

```text
pred_blend = β · pred_image_branch + (1-β) · pred_OCS_branch
β = 1.0 → image-only baseline
β = 0.0 → OCS-only baseline  
β = 0.5 → equal weight
```

**给 Codex 的补强建议**：在 12f 指导中追加"β 方向定义"小节，并明确"复用 12b 已训练 ResNet+OCS 模型权重，仅做推理 pass，不重训"。

### 7.4 12g Outlier gallery — ✅ 数据齐全，可零成本整理

核对：[u1_outlier_audit.json](../../../补充实验/结果/fusion_fallback_isolation_12b/run_20260604_150333/u1_outlier_audit.json)

```text
n_records = 42（error > 30°）
字段 = seed / sample_index / yaw_true / pitch_true / degradation / error_deg
       / pred_yaw / pred_pitch / is_repeated_outlier_across_degs
首条示例 = seed=0, sample=887, yaw_true=115, pitch_true=90, deg=clean,
           error=168.43°, pred_yaw=112.92, pred_pitch=-78.43, repeated=True
```

**12g 实施建议**：

- 纯整理工作，无新训练
- 输出 4 张图：
  1. outlier 在 (yaw, pitch) 空间分布散点（标 |pitch|>75° 极区）
  2. outlier 在退化档分布（clean / noise / brightness 计数）
  3. seed × sample 重复矩阵热图（看是否系统性极区难点）
  4. 6-8 张代表 outlier 的渲染图缩略（取 |pitch|>75° 高频复发样本）
- 输出 1 份 supplementary table（42 条全列）
- 写作口径严格遵循 Codex 07c §8 "mean/p90/Hit@5 are stabilized, but rare large outliers remain..."

**结论**：12g 可作为 07c 第一项执行（< 0.5 天），用于早期识别"是否存在极区共性问题"，间接指导 12c-12f 的退化档选择。

### 7.5 12e Centered-image — ✅ 协议可定，无需新数据

核对：[audit_data.json](../../../补充实验/结果/resnet_dataset_audit/run_20260601_105620/audit_data.json) 已有 `pixel_stats.centroid_x_range / centroid_y_range` 与 `centroid_drift_px.x_span / y_span` 聚合统计，但**未保存 per-image centroid 坐标**。

**12e 实施建议**：

- 新增 per-image intensity-weighted centroid 计算（基于 log1p 图像或 expm1 后的线性图像，需明确）：

```python
def compute_centroid(img_2d):  # img_2d shape (H, W)
    y_idx, x_idx = np.indices(img_2d.shape)
    total = img_2d.sum()
    cx = (img_2d * x_idx).sum() / total
    cy = (img_2d * y_idx).sum() / total
    return cx, cy
```

- 按 centroid 居中到图像中心 (64, 64)：用 scipy.ndimage.shift 或简单 crop+pad（零填充）
- 重训 ResNet image-only（沿用 `run_resnet_baseline.py` 协议，5 seeds 推荐）
- 与原 clean baseline (1.69°) 对比

**判读已对齐**：Codex 07c §6 已明确两种结局的写法红线。

**给 Codex 的补强建议**：在 12e 指导中明确 centroid 计算用**线性强度域**（expm1 还原后）而非 log1p 图（避免对数压缩偏置质心估计）。

### 7.6 资源核对总表

| 实验 | 数据可用性 | 代码可复用度 | 阻塞项 | 推荐执行顺序 |
|---|---|---|---|---|
| **12g** outlier gallery | ✅ 全 | 纯整理 | 无 | **1（最先）** |
| **12e** centered control | ✅ 全 | 新增 centroid + shift | 无 | **2** |
| **12f** late fusion β-sweep | ⚠️ 需新增 inference pass | 复用 12b 模型 | 12b 模型权重需可加载 | **3** |
| **12d** cross-phase | ❌ 需补渲染 phase24/120 | 复用渲染流程 | 渲染依赖 Blender 4.2.3 LTS | **4** |
| **12c** observation-style | ⚠️ 退化算子需重写 | 部分复用 | 退化算子规范需 Codex 锁定 | **5（最后）** |

---

## 8. 给 Codex 07c 指导的补强请求清单

请 Codex 在 07c 启动前修订指导文件，吸收以下补强：

1. **12d 必须先补渲染 phase24+phase120 全量 2701 张**（不是"小规模子集"）；新增渲染输出目录命名规范。
2. **12c 退化算子规范小节**：明确 expm1→degrade→log1p 流程；photon/read/background/clipping 的参数 grid 与物理标定参考；禁止直接复用 `run_resnet_robustness.py` 的现有 log1p 域退化函数。
3. **12f β 方向锁定**：`β=1 → image-only, β=0 → OCS-only`；明确"复用 12b 已训练模型，仅做推理 pass"。
4. **12e centroid 计算域**：要求在线性强度域（expm1 还原）计算 intensity-weighted centroid，避免 log 压缩偏置。
5. **执行顺序建议**：12g → 12e → 12f → 12d → 12c（理由：可用性 ↑、依赖性 ↓、单项成本 ↑），便于早期暴露风险。
6. **CJA/AST 判据表补行**：在 [投稿策略_三档路线_v20260604.md](../03_投稿定稿/submission_checklist/投稿策略_三档路线_v20260604.md) §6 增加"12d 跨 phase 稳定"分支的策略调整说明。

以上 6 项均不改变 Codex 07c 的总体设计，仅补充执行细节与可避免的踩坑点。

---

## 9. 07c 执行完成后 · 进入第一档 v0.2 第一版的评估与建议（Claude，2026-06-05）

> 背景：12c-12g 已全部执行完成（5 seeds），Codex 单边审阅通过，并产出 07c 整合清单，明确授权进入第一档 Acta/ASR v0.2。
> 上游：`Codex审阅/07c_Claude投稿前非真实数据补实验总包单边审阅.md`、`阶段整合输出/07c_投稿前非真实数据补实验总包_整合清单.md`、`Claude交互/Claude输出/07c_Claude输出_投稿前非真实数据补实验总包.md`
> 本节回答作者问题「进入 v0.2 第一版是否合理」，并给出动笔前需拍板的事项。

### 9.1 总判定：进入第一档 v0.2 整体合理（流程与边界都干净）

绿灯项（均满足）：

- Codex 07c 审阅「通过，可进入第一档 Acta/ASR v0.2」，整合清单已给出可执行采用范围。
- v0.1 完好（`01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md`，414 行 / 48 节），`03_投稿定稿/manuscript_md/` 为空 → 新建 v0.2 **不覆盖 v0.1**，符合红线。
- 仅授权第一档；CJA/AST、TAES/JGCD 文本继续冻结。
- 数值口径一致（split / sin-cos / great-circle / 5 seeds / OCS train-only 标准化），无 leakage。
- 过度结论黑名单清晰（见 07c 审阅 §5 / 整合清单 §4）。

### 9.2 ⚠️ 动笔前必须拍板的第 1 件事：v0.2 第一版应整合 07 + 07b + 07c 三段，而非只接 07c

这是进入 v0.2 前最关键的一致性问题：

- v0.1 生成于实验 11/12 **之前**，其 4.4「OCS-image fusion under clean images」/ 4.5「Robustness under controlled observation degradation」仍是 **naive fusion 口径**，**尚无** U1 退化感知融合、12b fallback 因果隔离的内容。
- 而 12c 的主角「U1 fusion」正是在 **07（实验12）** 中定义、在 **07b（实验12b）** 中完成因果隔离的。若 v0.2 只接 07c，U1 概念会悬空、叙事断裂。
- 07（exp12）与 07b（exp12b）均已各自 Codex 单边审阅通过、各有整合清单（`阶段整合输出/07_*`、`07b_*`）。

**建议**：v0.2 第一版一次性合并 **07(exp12 U1/诊断) + 07b(exp12b 因果隔离) + 07c(12c-g)**，统一改写 4.4/4.5、新增 4.7、补 Discussion 与 Methods。请 Codex 确认是否同意「三段合并入第一版」，还是要求分两步（先并 07/07b，再并 07c）。

### 9.3 07c 证据 → v0.1 结构映射（已核对，通顺）

| 证据 | v0.1 落点 | 处理 |
|---|---|---|
| 12c observation-style / 12d cross-phase / 12f β-sweep | Results 新增 **4.7「Synthetic observation-style degradation & cross-geometry sanity tests」**（接 4.5 之后） | 主文压缩表 |
| 12e centered control | Supplementary + 5.6 Limitations 点名 | — |
| 12g outlier audit | Supplementary + 5.6 Limitations 点名 | 防 fully robust 误读 |
| 退化边界 / phase120 / combined_severe | Discussion 新增边界段 | no real telescope validation |
| 12c 线性域退化 / 12f β=image weight / split / metric | Methods 或 Supplementary 协议补充 | — |

### 9.4 动笔前需确认的其余 3 点

2. **4.4→4.5→4.7 单调推进、不自相矛盾**：现 4.5 讲 naive fusion 在高斯噪声下崩溃（exp9/11）；新内容要推进到「naive fusion 图像主导 → U1 退化感知联合表示更稳，但条件性、合成性」，避免与旧段冲突。
3. **6.58° vs 5.91° 全局一致**：12f 重训 OCS-only=6.58° 仅作 12f 内部参照；正文其他处 OCS-only 仍引 5.91°（exp6）。该表下须显式注明，禁止混用或写成升降。
4. **Q12-Q14（Data/Code/Author/Funding/COI）继续占位**，不由 AI 代填。

### 9.5 建议下一步

按 Codex 路线起草 **`03_投稿定稿/manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md`（不覆盖 v0.1）**，整合 07+07b+07c：新增 4.7、改写 4.4/4.5、补 Discussion 边界段与 Methods 协议、12e/12g 落 Supplementary、Limitations 点名 worst-case 与 phase120/combined_severe 失败模式。CJA/AST、TAES/JGCD 继续冻结，待作者确认第一档完结。

> 待 Codex 就 §9.2（三段是否一次性合并）拍板后，Claude 即可动笔 v0.2 第一版。

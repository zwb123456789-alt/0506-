# OCS + 图像联合仿真与姿态反演项目

> 完整实验历史已归档至 `进度档案_仿真与反演_full.md`（923 行），本文件仅保留索引级信息。
> **当前焦点：论文写作 — 第一档（Acta/ASR）v0.3 已完成并通过 Codex 复审，准备启动第二档（CJA/AST）冲刺版本。**

---

## 一、项目两阶段总览

| 阶段 | 状态 | 说明 |
|---|---|---|
| **I · 仿真与反演实验** | ✅ 已完成 | 模块 A/B/C + BRDF 验证 + 三端闭合 + 所有反演实验（1-12g）|
| **II · 论文写作** | 🔄 进行中 | 第一档 v0.3 已完成，准备第二档 CJA/AST 冲刺版 |

---

## 二、模块 A/B/C（阶段 I 产物，已冻结）

| 模块 | 职责 | 关键产物 |
|---|---|---|
| **A · OCS 计算** | STL → 姿态扫描 → OCS/遮挡率/图表 | GGX 5° 网格 2701 姿态；5 几何多观测批量 |
| **B · Blender 渲染** | headless 光度图像渲染 | 几何缓冲 EXR + Python 后处理 exact BRDF 路径 |
| **C · 姿态反演** | OCS/图像/融合姿态估计 | OCS MLP / CNN / ResNet / late fusion / feature fusion |

**核心验证**：单平板 → 立方体 → L 型，LegacyPhong + GGX 均通过三端闭合（凸几何 rel_err < 0.5%）。真实三件套 gap 根因确认为 face-center vs pixel-level 可见性语义差异。

**关键决策**：图表双语 / Yaw×Pitch 网格 / Blender 4.2.3 LTS / GGX 论文主 BRDF / 5° 网格论文必需。

---

## 三、论文写作（阶段 II — 当前）

### 3.1 三模型分工

- **Codex**（总控 + 审阅）：生成指导 → 审阅 → 整合维护版本线（不自己写正文）
- **GPT** + **Claude**（本文档所在端）：双线并行写手，各自产出，不直接覆盖主稿

### 3.2 版本线与投稿三档策略

**已完成版本**：
- **v0.1**（初稿）: `论文改进/论文写作/01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md`
- **v0.2**（第一档工作稿）: `论文改进/论文写作/03_投稿定稿/manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md`
- **v0.3**（第一档润色稿）: `论文改进/论文写作/03_投稿定稿/manuscript_md/主稿_v0.3_Acta_ASR润色版.md` ✅ 已通过 Codex 复审

**投稿三档策略**（详见 `论文改进/论文写作/03_投稿定稿/submission_checklist/投稿策略_三档路线_v20260604.md`）：
1. **第一档（主投优先）**：Acta Astronautica / Advances in Space Research → v0.3 已完成，待投稿工程化
2. **第二档（冲刺优先）**：Chinese Journal of Aeronautics / Aerospace Science and Technology → **当前准备启动**
3. **第三档（高风险冲刺）**：IEEE TAES / JGCD → 暂缓，等第一档投稿结果

### 3.3 后整合与补充实验完成状态

| 阶段 | 任务 | 状态 |
|---|---|---|
| 01 | 作者确认与数值审计 | ✅ |
| 02 | 引用核验与 Related Work | ✅（含 references.bib 修订） |
| 03 | 图表制作与 Caption 定稿 | ✅ |
| 04 | 全文压缩与期刊风格 | ✅ |
| 05 | 模拟审稿与返修 | ✅ |
| 06 | 投稿材料 | ✅ |
| 07 | 融合机制诊断与鲁棒融合升级（实验12） | ✅ |
| 07b | 融合 fallback 因果隔离（实验12b） | ✅ |
| 07c | 投稿前非真实数据补实验总包（实验12c-12g） | ✅ |
| 投稿定稿 | v0.2 Acta/ASR 主投优先版 | ✅ |
| 投稿定稿 | v0.3 Acta/ASR 润色版 | ✅ 已通过 Codex 复审 |

---

## 四、论文核心证据与主线（实验 1-12g 已完成）

### 4.1 核心实验结果

**基准性能（clean synthetic images）**：
| 方法 | mean error | Hit@5° | worst-case |
|---|---|---|---|
| ResNet-18 image-only | **1.69±0.07°** | 97.6% | 9.9° |
| OCS MLP per_part_log 30D | 5.91±0.22° | 73.8% | — |
| ResNet + OCS feature fusion (concat5) | **1.47±0.07°** | **99.7%** | **6.6°** |

**图像退化鲁棒性（实验11）**：
| 条件 | ResNet image-only | OCS MLP | Feature Fusion |
|---|---|---|---|
| clean | 1.69° | 5.91° | 1.47° |
| **noise σ=0.01** | **85.85°** ❌ | **5.91°** ✅ | **73.36°** ❌ |
| noise σ=0.10 | 87.92° | 5.91° | 73.57° |

**退化增强融合（实验12 U1）**：
| 条件 | U1 aug fusion | image-only+aug | 判读 |
|---|---|---|---|
| clean | 1.95±0.21° | 2.63° | U1 更优 |
| noise σ=0.10 | **2.31±0.26°** | 9.55° | U1 显著更优 |
| worst-case | 164° outliers | — | 不能写 fully robust |

**关键机制发现（实验12b）**：
- U1 优于 image-only same augmentation，说明 OCS 在联合表示中活跃
- 但 image-masked 后仍约 30°（远高于 OCS-only 5.91°），不是 OCS-standalone fallback
- OCS 噪声会单调拉低 U1 性能，支持 **OCS-image co-utilization**

**观测风格退化（实验12c）**：
- U1 在 read/background/starfield/combined_medium 下约 2°
- combined_severe 下退至 13.88°，不能写 fully robust

**其他边界（实验12d-12g）**：
- phase120 下 image-only/fusion 均约 80°，不支持跨 phase 鲁棒泛化
- 居中控制后 ResNet 从 1.69° 退至 2.88°，质心贡献存在但不是唯一因素
- U1 rare outliers 为 42/49,950 (0.084%)，50% 位于 |pitch|>75°

### 4.2 论文主线

> **Clean synthetic images provide an idealized upper bound** where strong CNNs achieve high accuracy. **OCS provides a physically interpretable, degradation-immune photometric constraint** with different failure modes. **Naive feature fusion inherits image-branch fragility** under degradation, but **degradation-aware training forms OCS-image co-utilization** that stabilizes fusion under tested synthetic perturbations. **No real telescope validation** has been conducted.

中文总结：
> 干净仿真图像是理想上界（ResNet 1.69°），OCS 是物理可解释、对图像退化免疫的光度约束。Naive fusion 在图像退化下继承图像分支脆弱性，但退化感知训练能形成 OCS-image 协同利用，在已测试合成扰动下稳定融合性能。无真实望远镜验证。

### 4.3 写作红线（v0.3 后更新）

0. 禁止编造实验结果、文献、方法或作者未确认的事实
1. 不把 clean rendered images 写成真实外场性能（无真实望远镜验证）
2. 不写 "fusion 永远最优" / "OCS 永远鲁棒"
3. 不把 `all_raw` 45D（含遮挡率）写成可运营特征（semi-oracle 上界）
4. 不写 U1 是 OCS-standalone fallback 或图像失效后自动切换到 OCS（实验12b 已证伪）
5. 不写 U1 为 near-perfect / fully robust（实验12g rare outliers 0.084%）
6. 不把 12c 写成真实望远镜验证（仅为 observation-chain-inspired synthetic stress test）
7. 不写 phase120/combined_severe 为成功案例（均为失效边界）
8. Q12-Q14（Data/Code/Author/Funding/COI）不代填
9. 第二档/第三档写作必须等第一档作者确认完结

---

## 五、第二档（CJA/AST）冲刺版准备

### 5.1 当前状态

第一档 v0.3 已完成并通过 Codex 复审，作者已确认可以启动第二档写作。

### 5.2 第二档与第一档的差异

| 维度 | 第一档 Acta/ASR | 第二档 CJA/AST |
|---|---|---|
| **定位** | 受控仿真基准研究 | 工程问题导向 + 观测链退化压力测试 |
| **叙事重心** | physically consistent simulation benchmark | 地基光学观测质量不稳定导致图像姿态反演脆弱 |
| **12c-12g 作用** | 防御性审稿材料，部分进 Results | 更强调观测链退化（PSF/noise/background/saturation/resolution）|
| **融合机制** | OCS-image co-utilization | 退化感知训练与 OCS-image co-utilization |
| **边界强调** | no real telescope validation | synthetic observation-style stress test, not field validation |

### 5.3 第二档可以强化的内容

1. **工程问题背景**：
   - 地基光学望远镜观测条件不稳定（大气、探测器、背景污染）
   - 图像质量退化导致纯图像方法脆弱
   - 需要多模态融合增强鲁棒性

2. **观测链退化模拟**（实验12c）：
   - U1 在 read noise / background / starfield / combined_medium 下约 2°
   - 优于 clean-trained image-only 和 image-only+aug
   - combined_severe 仍为 13.88°（诚实边界）

3. **OCS 作为退化免疫约束**：
   - OCS 对图像质量退化天然免疫
   - U1 证明退化感知训练能让 OCS 在联合表示中活跃
   - 但不是自动 fallback，而是协同利用

4. **跨 phase 边界**（实验12d）：
   - phase120 约 80°，说明训练分布外泛化有限
   - 诚实报告失效案例

### 5.4 第二档不能写的内容

- ❌ 真实望远镜验证
- ❌ 自动 OCS fallback
- ❌ fully robust / near-perfect
- ❌ operational deployment ready
- ❌ 隐瞒 phase120 / combined_severe 失效
- ❌ 把 obs-aug (U2) 写成有效方法（本轮表现不佳）

### 5.5 第二档写作启动条件

✅ 第一档 v0.3 已完成并通过 Codex 复审  
✅ 实验 12c-12g 已完成并通过 Codex 审阅  
✅ 作者已确认启动第二档写作

**下一步**：Codex 生成第二档 CJA/AST 冲刺版 GPT/Claude 指导文件

---

## 六、断点恢复关键路径

### 6.1 新对话必读（按顺序）

```
论文改进/20260529_论文写作完整规划.md       ← 论文写作规划 v2
论文改进/20260529_补充实验进度.md           ← 实验 1-12g 完整状态
论文改进/论文写作/00_总控流程.md             ← 总控 + 断点恢复
论文改进/论文写作/02_后整合双线修订/00_后整合双线总览.md  ← 后整合路线
论文改进/论文写作/03_投稿定稿/submission_checklist/投稿策略_三档路线_v20260604.md  ← 投稿策略
论文改进/论文写作/03_投稿定稿/manuscript_md/主稿_v0.3_Acta_ASR润色版.md  ← 当前最新主稿
论文改进/论文写作/03_投稿定稿/Codex审阅/02_v0.3_Acta_ASR润色版作者审计后Codex审阅.md  ← v0.3 复审
论文项目总览 copy.md                       ← 全局参考（部分旧口径，以 20260529 文件为准）
```

### 6.2 核心脚本与数据

| 类别 | 路径 |
|---|---|
| 补充实验脚本 | `论文改进/补充实验/代码/run_*.py`（实验1-12g全部完成）|
| 反演核心代码 | `ocs_project/03_inversion/` |
| 模块 A OCS 数据 | `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/` |
| 模块 B 渲染 | `结果/模块B_渲染/run_20260528_101944_exact_brdf/` |
| 补充实验结果 | `论文改进/补充实验/结果/`（含实验12/12b/12c-12g）|
| 第一档主稿 v0.3 | `论文改进/论文写作/03_投稿定稿/manuscript_md/主稿_v0.3_Acta_ASR润色版.md` |

### 6.3 实验完成状态

✅ 实验 1-7：Phase63 ablation / Random split / BRDF sensitivity / Occlusion / ResNet baseline / Noise robustness / Roll sensitivity  
✅ 实验 8-10：ResNet 问题排查（fusion 重测 / 图像退化 / 数据集审计）  
✅ 实验 11：ResNet-fusion 图像退化鲁棒性（证明 naive fusion 不会自动回退到 OCS）  
✅ 实验 12：融合主导性诊断与鲁棒融合升级（U1 图像退化增强成功）  
✅ 实验 12b：融合 fallback 因果隔离（证明 OCS-image co-utilization，非 OCS-standalone fallback）  
✅ 实验 12c：Observation-style 图像退化压力测试  
✅ 实验 12d：跨 phase 图像泛化 sanity test  
✅ 实验 12e：质心居中控制实验  
✅ 实验 12f：Late-fusion beta sweep 图像退化对照  
✅ 实验 12g：U1/12b 离群案例画廊与审计包

---

## 七、目录结构（精简）

```
0506新/
├── 建模/真实模型/              真实 STL
├── 结果/                       所有运行产物（模块A_重构/模块B_渲染/BRDF验证/模块C_反演）
├── ocs_project/                代码工程
│   ├── 01_code/                config / materials / ocs_core / occlusion
│   ├── 02_blender/             render_geometry_passes + brdf_postprocess + 诊断
│   ├── 03_inversion/           inv_common / train_mlp / train_cnn / train_fusion
│   ├── 06_brdf_validation/     三端闭合验证
│   └── 07_brdf/                brdf_models.py
├── 论文改进/
│   ├── 20260529_论文写作完整规划.md
│   ├── 20260529_补充实验进度.md
│   ├── 论文写作/                01 初稿 / 02 后整合 / 03 定稿
│   │   ├── 01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md
│   │   ├── 03_投稿定稿/manuscript_md/主稿_v0.3_Acta_ASR润色版.md  ← 当前最新
│   │   └── 03_投稿定稿/submission_checklist/投稿策略_三档路线_v20260604.md
│   └── 补充实验/代码/ + 结果/  ← 实验1-12g全部完成
├── 论文项目总览 copy.md         全局参考（注意旧口径）
├── 进度档案_仿真与反演_full.md  阶段 I 完整历史（923 行，按需查阅）
└── 文献/ + 汇报材料/
```

---

## 八、已知坑

- **Windows Git Bash + 中文路径**：长命令行可能 exit 127，用 `cmd.exe //c` 包装
- **Python GBK 控制台**：用 `[OK]` 代替 Unicode ✓
- **Blender 5.0 MULTILAYER EXR 损坏**：用 4.2.3 LTS
- **conda env**：`ocs_sim`（Python 3.12.7 + PyTorch 2.8.0+cu128, RTX 5060）

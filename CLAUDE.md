# OCS + 图像联合仿真与姿态反演项目

> 完整实验历史已归档至 `进度档案_仿真与反演_full.md`（923 行），本文件仅保留索引级信息。
> **当前焦点：论文写作 — 后整合 Step 07，待执行实验 12（融合主导性诊断与鲁棒融合升级）。**

---

## 一、项目两阶段总览

| 阶段 | 状态 | 说明 |
|---|---|---|
| **I · 仿真与反演实验** | ✅ 已完成 | 模块 A/B/C + BRDF 验证 + 三端闭合 + kNN/MLP/CNN/Fusion 实验 |
| **II · 论文写作** | 🔄 进行中 | 三模型协作工作流,当前后整合 01-06 已完成，卡实验 12 |

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

### 3.2 版本线

- **v0.1**（已生成）: `论文改进/论文写作/01_初稿生成与整合/最终整合/最终整合版_v0.1_基于GPT吸收Claude.md`
- **v0.2**（待生成）：等实验 12 完成后再创建

### 3.3 后整合进度

| 阶段 | 任务 | 状态 |
|---|---|---|
| 01 | 作者确认与数值审计 | ✅ |
| 02 | 引用核验与 Related Work | ✅（含 references.bib 修订） |
| 03 | 图表制作与 Caption 定稿 | ✅ |
| 04 | 全文压缩与期刊风格 | ✅ |
| 05 | 模拟审稿与返修 | ✅ |
| 06 | 投稿材料 | ✅ |
| **07** | **融合机制诊断与鲁棒融合升级** | **⬜ 待 Claude 执行实验 12** |

---

## 四、论文新主线（实验 9/11 后调整）

### 4.1 核心证据

| 条件 | ResNet image-only | OCS MLP (per_part_log 30D) | Feature Fusion |
|---|---|---|---|
| clean | **1.69°** | 5.91° | **1.47°** |
| image noise σ=0.01 | **崩至 85°** | **保持 5.91°** | **崩至 73°**（≈image-only） |

- ResNet 干净图极强但**对噪声极度脆弱**（1% 噪声即崩）
- OCS 对图像退化**天然免疫**（低维物理量，与图像质量无关）
- Naive feature fusion **是图像主导的**：图像干净时最优，图像退化时被拖垮，**不会自动回退到 OCS**

### 4.2 新主线

> OCS-image fusion is architecture- and training-dependent. Naive feature-level fusion can become image-dominant and fail under image degradation; OCS can act as a fallback constraint only when the fusion design explicitly supports degradation awareness, modality dropout, adaptive gating, uncertainty weighting, or OCS-anchored prediction.

### 4.3 写作红线

0. 禁止编造实验结果、文献、方法或作者未确认的事实
1. 不把 clean rendered images 写成真实外场性能（无真实望远镜验证）
2. 不写 "fusion 永远最优" / "OCS 永远鲁棒"
3. 不把 `all_raw` 45D（含遮挡率）写成可运营特征（semi-oracle 上界）
4. 不写 OCS 会自动托住融合模型（实验 11 已证伪）
5. 不在作者确认前写死 Euler convention / target encoding / model architecture / 0% OCS-noise / BRDF/roll/random split/phase63 sensitivity 具体数值
6. Q12-Q14（Data/Code/Author/Funding/COI）不代填
7. 不改写 v0.1；所有 AI 输出先经 Codex 审阅再合并入主稿

---

## 五、实验 12（当前待执行）

**目标**：诊断 naive feature fusion 是否图像主导 + 测试鲁棒融合升级。

**诊断线 D1-D4**：分支遮蔽 / 退化图像遮蔽 / 梯度贡献 / 双向扰动敏感性

**升级线 U1-U5**（按优先级）：
1. 图像退化增强训练
2. 模态 dropout
3. 退化增强 + 模态 dropout（优先组合）
4. OCS-anchored residual fusion
5. adaptive gating / uncertainty late fusion

**三种结局都有论文价值**：成功（OCS 可作鲁棒 fallback）/ 部分成功（ideal vs operational trade-off）/ 失败（机制边界）。

详见：`论文改进/20260529_补充实验进度.md` §12（含诊断/升级细节、成功/失败判据、评价矩阵）

---

## 六、断点恢复关键路径

### 6.1 新对话必读（按顺序）

```
论文改进/20260529_论文写作完整规划.md       ← 论文写作规划 v2
论文改进/20260529_补充实验进度.md           ← 实验 1-12 状态
论文改进/论文写作/00_总控流程.md             ← 总控 + 断点恢复
论文改进/论文写作/02_后整合双线修订/00_后整合双线总览.md  ← 当前路线
论文项目总览 copy.md                       ← 全局参考（部分旧口径，以 20260529 文件为准）
```

### 6.2 核心脚本与数据

| 类别 | 路径 |
|---|---|
| 补充实验脚本 | `论文改进/补充实验/代码/run_*.py` |
| 反演核心代码 | `ocs_project/03_inversion/` |
| 模块 A OCS 数据 | `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/` |
| 模块 B 渲染 | `结果/模块B_渲染/run_20260528_101944_exact_brdf/` |
| 补充实验结果 | `论文改进/补充实验/结果/` |

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
│   ├── 论文写作/                01 初稿 / 02 后整合（当前）/ 03 定稿
│   └── 补充实验/代码/ + 结果/
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

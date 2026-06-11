# OCS + 图像联合仿真与姿态反演项目

> 完整实验历史已归档至 `进度档案_仿真与反演_full.md`（923 行），本文件仅保留索引级信息。
> **当前焦点：v0.4 BlenderOCS 重启 — v0.3 论文写作已封存，转向 model-known 条件下 OCS/图像双读出可观测性研究。**
> **v0.4 工作区有独立 CLAUDE.md 与完整定位文件，本文件只做高层索引与跳转，细节以 `项目重启_v0.4_BlenderOCS/CLAUDE.md` 为权威。**

---

## 一、项目三阶段总览

| 阶段 | 状态 | 说明 |
|---|---|---|
| **I · 仿真与反演实验** | ✅ 已完成 | 模块 A/B/C + BRDF 验证 + 三端闭合 + 所有反演实验（1-12g）|
| **II · v0.3 论文写作** | ⏸️ 已封存 | 第一档 Acta/ASR v0.3 已完稿并过 Codex 复审，但因 OCS 数据源口径问题封存，不再投稿工程化 |
| **III · v0.4 BlenderOCS 重启** | 🔄 进行中 | 重建统一前向物理模型，研究定位与代码阶段准备已冻结，停在代码实施前确认完成 |

---

## 二、v0.4 当前状态与入口（当前焦点）

### 2.1 v0.4 定位（一句话）

放弃"真实未知非合作目标姿态反演系统"强主张，转向 **model-known（几何已知、不配合）** 条件下，OCS 独立光度通道与图像成像通道共享同一物理前向模型时，二者对姿态信息的**可观测性、互补性、置信一致性**研究。

### 2.2 v0.4 工作区入口

```
项目重启_v0.4_BlenderOCS/CLAUDE.md                    ← v0.4 权威启动文件（必读）
项目重启_v0.4_BlenderOCS/00_只打开本文件夹时的启动说明.md
项目重启_v0.4_BlenderOCS/00_v0.4总控流程.md
```

### 2.3 v0.4 定位冻结稿谱系

定位文件迭代至 24 号（OCS 口径、形态与 mismatch 账面对齐版）；主入口待作者最终确认，以 v0.4 子目录 CLAUDE.md 同步为准。

```
21 号：OCS 口径并入版（口径 A = independent photometric channel）
22 号：OCS 信号形态决策（单点 vs 多样本，L1 跨几何向量进主线、L2 光变曲线留 Future Work）
23 号：OCS 口径与形态并入版
24 号：OCS 口径形态与 mismatch 账面对齐版 ← 最新候选主入口
```

### 2.4 v0.4 方法冻结与代码阶段准备（已通过 Codex 复审）

项目重启_v0.4_BlenderOCS/04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
项目重启_v0.4_BlenderOCS/04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
项目重启_v0.4_BlenderOCS/05_全链路重跑/00_重跑任务清单.md
项目重启_v0.4_BlenderOCS/05_全链路重跑/01_代码阶段资产盘点与实施计划_Claude.md
项目重启_v0.4_BlenderOCS/05_全链路重跑/02_第一批最小验证任务清单_Claude.md
```

### 2.5 v0.4 核心方法口径

统一前向物理模型：Blender 负责"看见哪里"（STL/姿态/正交投影/depth/normal/part ID/pixel-level visibility），Python/公式负责"如何反光"（显式 GGX/Cook-Torrance BRDF/NoL·NoV/OCS 积分/clean image linear response）。新 canonical OCS 数据源为 Blender-derived OCS，不再用旧模块 A face-center 扫描表。

### 2.6 v0.4 当前停点与下一步

停在"代码实施前文档确认完成"。下一步进入 `项目重启_v0.4_BlenderOCS/06_v0.4_code/` 代码实施：搭代码骨架 → 记录环境依赖 → 单姿态 smoke test → depth round-trip sanity check → camera/sun geometry pass → 20 姿态 shadow validation → 全量生成。**不要直接全量重跑或训练模型。**

### 2.7 v0.4 阶段同步硬约束

Codex 复审判定某阶段通过后，**只能由 Codex 审阅端**同步 v0.4 的 CLAUDE.md / 启动说明 / 总控 / 阶段入口 / 归档索引。Claude 执行端只在 `项目重启_v0.4_BlenderOCS/97_交互审阅记录/01_Claude输出/` 产出方案、候选稿、修订稿，不擅改 v0.4 启动集与定位主线正文。

---

## 三、模块 A/B/C（阶段 I 产物，已冻结）

| 模块 | 职责 | 关键产物 |
|---|---|---|
| **A · OCS 计算** | STL → 姿态扫描 → OCS/遮挡率/图表 | GGX 5° 网格 2701 姿态；5 几何多观测批量 |
| **B · Blender 渲染** | headless 光度图像渲染 | 几何缓冲 EXR + Python 后处理 exact BRDF 路径 |
| **C · 姿态反演** | OCS/图像/融合姿态估计 | OCS MLP / CNN / ResNet / late fusion / feature fusion |

**核心验证**：单平板 → 立方体 → L 型，LegacyPhong + GGX 均通过三端闭合（凸几何 rel_err < 0.5%）。真实三件套 gap 根因确认为 face-center vs pixel-level 可见性语义差异。

**关键决策**：图表双语 / Yaw×Pitch 网格 / Blender 4.2.3 LTS / GGX 论文主 BRDF / 5° 网格论文必需。

> ⚠️ 阶段 I 的 OCS 来自模块 A face-center 扫描，与图像 pixel-level 采样口径不统一——这正是 v0.3 封存、v0.4 重建统一前向模型的根因。阶段 I 成果仅作历史证据、机制假设与代码结构参考。

---

## 四、v0.3 论文写作（阶段 II — 已封存）

第一档 Acta/ASR 主稿迭代至 v0.3 润色版并通过 Codex 复审，但**已封存，不再进入投稿工程化**。

封存原因不是写作问题，而是 OCS 数据源定义级问题：旧主反演与补充实验用模块 A face-level/face-center OCS 扫描表，图像端用 Blender pixel-level pass，二者采样口径不统一，可能影响 OCS-only / fusion / OCS noise / branch masking / 12b / 12c / 12f / 12g 等结果。因此 v0.3 数字不能作为 v0.4 主结果。

封存材料位置：

```
论文改进/论文写作/03_投稿定稿/manuscript_md/主稿_v0.3_Acta_ASR润色版.md
项目重启_v0.4_BlenderOCS/01_v0.3封存/
```

> v0.3 阶段的核心实验结果、论文主线与写作红线已随阶段封存，完整内容见上述封存目录与 `进度档案_仿真与反演_full.md`，不在本文件展开（避免与 v0.4 口径混读）。

---

## 五、断点恢复关键路径

### 5.1 新对话必读（按顺序）

```
CLAUDE.md（本文件）                                    ← 三阶段总览与跳转
项目重启_v0.4_BlenderOCS/CLAUDE.md                    ← v0.4 权威启动文件
项目重启_v0.4_BlenderOCS/00_只打开本文件夹时的启动说明.md
项目重启_v0.4_BlenderOCS/00_v0.4总控流程.md
```

当前焦点在 v0.4，进入 v0.4 工作区后按其 CLAUDE.md 的默认启动规则读取，不要一次性全文读取定位文件与备份材料。

### 5.2 核心脚本与数据（阶段 I 资产，可复用为 v0.4 参考）

| 类别 | 路径 |
|---|---|
| 反演核心代码（旧） | `ocs_project/03_inversion/` |
| 模块 A OCS 数据（旧口径） | `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/` |
| 模块 B 渲染 | `结果/模块B_渲染/run_20260528_101944_exact_brdf/` |
| 补充实验脚本（v0.3） | `论文改进/补充实验/代码/run_*.py` |
| 补充实验结果（v0.3） | `论文改进/补充实验/结果/`（含实验12/12b/12c-12g）|

### 5.3 阶段 I 实验完成状态（已封存为历史）

✅ 实验 1-7：Phase63 ablation / Random split / BRDF sensitivity / Occlusion / ResNet baseline / Noise robustness / Roll sensitivity
✅ 实验 8-10：ResNet 问题排查（fusion 重测 / 图像退化 / 数据集审计）
✅ 实验 11：ResNet-fusion 图像退化鲁棒性
✅ 实验 12 / 12b：融合机制诊断与 fallback 因果隔离（OCS-image co-utilization）
✅ 实验 12c-12g：观测风格退化 / 跨 phase / 质心居中 / late-fusion beta sweep / 离群画廊

---

## 六、目录结构（精简）

```
0506新/
├── 建模/真实模型/              真实 STL
├── 结果/                       阶段 I 运行产物（模块A_重构/模块B_渲染/BRDF验证/模块C_反演）
├── ocs_project/                阶段 I 代码工程（01_code / 02_blender / 03_inversion / 06_brdf_validation / 07_brdf）
├── 论文改进/                   阶段 II（v0.3）论文写作与补充实验（已封存）
├── 项目重启_v0.4_BlenderOCS/   ★ 阶段 III v0.4 工作区（当前焦点，有独立 CLAUDE.md）
│   ├── CLAUDE.md
│   ├── 00_* 启动集 / 01_v0.3封存 / 02_重大分支路线图 / 03_项目审计与方法说明
│   ├── 04_BlenderOCS方法重建 / 05_全链路重跑 / 06_论文v0.4重写接入
│   ├── 15~24_* v0.4 定位与冻结稿谱系
│   └── 97_交互审阅记录 / 98_外部材料备份 / 99_归档索引
├── 论文项目总览 copy.md         全局参考（注意旧口径）
├── 进度档案_仿真与反演_full.md  阶段 I 完整历史（923 行，按需查阅）
└── 文献/ + 汇报材料/
```

---

## 七、已知坑

- **Windows Git Bash + 中文路径**：长命令行可能 exit 127，用 `cmd.exe //c` 包装
- **Python GBK 控制台**：用 `[OK]` 代替 Unicode ✓
- **Blender 5.0 MULTILAYER EXR 损坏**：用 4.2.3 LTS
- **conda env**：`ocs_sim`（Python 3.12.7 + PyTorch 2.8.0+cu128, RTX 5060）

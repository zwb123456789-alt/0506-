# 全项目坑位排查报告（Claude 审计生成）

生成时间：2026-06-08
审计范围：v0.3 封存材料、诊断快照、代码快照、写作控制文件、旧 CLAUDE.md、进度档案

---

## 一、排查总览

通过阅读所有必读文件和备份材料，本次排查覆盖方法、数据、代码、实验、写作、管理六类坑位，按 P0/P1/P2 分级。

---

## 二、全部坑位表

### 2.1 P0 坑位（阻断性：不解决不能启动 v0.4）

| ID | 优先级 | 类型 | 问题描述 | 证据文件 | 影响范围 | v0.4 解决方式 | 状态 | 是否需要 Codex 复审 |
|---|---|---|---|---|---|---|---|---|
| PIT-A-001 | P0 | 方法 | **OCS 与图像采样口径不统一**。旧模块 A 使用 face-center 采样（三角面中心点代表整面），模块 B 使用 Blender pixel-level 几何缓冲采样。两者对斜面面积、边缘裁剪、镜面峰的处理方式不同，导致 `ocs_comparison.csv` 中 rel_err 均值 1.17，最大值 121.39 | `98_外部材料备份/04_关键诊断与结果快照/20260528_ocs_comparison.csv`（ocs_image vs ocs_module_a rel_err 均值 117%，峰值 12139%）、`20260528_brdf_postprocess_summary.json`（rel_err_mean=1.17, rel_err_max=121.39）、`subface_adaptive_comparison.csv`（adaptive 细分子面对 face-center 比值从 0.22x 到 72x 不等） | **全部 OCS 相关结果**：OCS-only MLP/kNN、fusion clean、OCS 噪声实验、branch masking、beta sweep(12f)、fallback isolation(12b)、observation degradation(12c)、outlier gallery(12g)、Fig3 OCS heatmap、Fig4/Fig6 OCS 平线 | v0.4 采用统一前向模型：Blender geometry-pass 采样 + Python 显式 GGX OCS 积分，确保 OCS 和图像来自同一投影几何和像素可见性 | open | 是 |
| PIT-A-002 | P0 | 方法 | **face-center 采样可能漏掉窄镜面峰和斜面**。`subface_adaptive_comparison.csv` 显示：对于太阳能板在强镜面/阴影姿态（yaw=150, pitch=-80），adaptive subface OCS 是 face-center 的 20.68 倍；遮光板 face-center OCS 是 adaptive 的 2.56 倍，方向不一致 | `98_外部材料备份/04_关键诊断与结果快照/subface_adaptive_comparison.csv`（taiyangnengban ratio_ad_fc: 1.01x 正照, 1.01x 斜射, 1.02x 强镜面/阴影——但 ratio_ad_Bdiff 高达 20.68x 说明像素域还有额外差异） | OCS-only 反演误差的绝对值、各姿态 per-part OCS 相对关系和 heatmap 形态、fusion 中 OCS 分支贡献度 | v0.4 使用 pixel-level sampling（Blender geometry pass），天然避免 face-center 的斜面/镜面漏采样问题 | open | 是 |
| PIT-A-003 | P0 | 方法 | **sun-side visibility / self-shadow 定义未完全闭合**。`00_公式与Blender分工说明.md` 中标记为"待定并必须明确"。201 行进度档案提到旧模块 A 用 `min_hit_distance` 过滤起点自相交，模块 B 用 Cycles 物理光追。两者遮挡逻辑在太阳侧阴影处理上可能存在差异 | `04_BlenderOCS方法重建/00_公式与Blender分工说明.md` line 63（"sun-side visibility/self-shadow 待定并必须明确"）、`进度档案/进度档案_仿真与反演_full.md` 第 111 行（"模块 A 用 min_hit_distance 过滤；B 用 Cycles 天然处理"） | OCS with occlusion 的定义、论文中"含自遮挡"的声称、各姿态 OCS 遮挡率数值 | v0.4 方法冻结时必须明确 sun visibility 实现方案（Blender shadow ray? Python 自写 ray-cast? "viewer-side only" 限制？） | open | 是 |
| PIT-A-004 | P0 | 数据 | **v0.3 所有反演结果依赖旧模块 A OCS**。v0.3 稿件中所有 OCS-only 误差（5.91°）、fusion 误差（1.47°）、12b/12c/12f/12g 全部数值均基于旧 ocs_scan.csv | `01_v0.3封存/00_v0.3封存说明.md` 第 18-21 行（"主反演与补充实验依赖模块 A OCS 扫描表"）、CLAUDE.md 旧版第 6.2 节（OCS 数据路径指向 `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/.../ocs_scan.csv`） | v0.3 主稿全部 OCS 相关数值和结论，补充实验 12b/12c/12f/12g 全部结果 | v0.3 封存，v0.4 基于 Blender-derived OCS 全链路重跑 | open | 是 |
| PIT-D-001 | P0 | 实验 | **image-only 结果是否可以复用未明确**。CLAUDE.md 和重跑清单中对 image-only CNN/ResNet 标记为 "recommended rerun or re-summarize"，但未给出明确复用条件。如果图像渲染链路不变，image-only 可能可复用，但需要审计 image source split 是否与 OCS 所用 split 完全一致 | `05_全链路重跑/00_重跑任务清单.md` line 28（"image-only CNN / ResNet: recommended rerun or re-summarize"） | 论文中 image-only baseline 数值（1.69°）、与 OCS 和 fusion 的对比表格 | v0.4 方法冻结后审计 image-only 数据路径和 split 一致性，决定复用还是重跑 | open | 是 |

### 2.2 P1 坑位（影响主结果或方法可信度）

| ID | 优先级 | 类型 | 问题描述 | 证据文件 | 影响范围 | v0.4 解决方式 | 状态 | 是否需要 Codex 复审 |
|---|---|---|---|---|---|---|---|---|
| PIT-B-001 | P1 | 数据 | **OCS-only MLP 平线（5.91°）来自旧 OCS**。重跑清单阶段 2 明确 OCS-only kNN/MLP 必须重跑。旧 OCS 特征的空间结构和新 OCS 可能存在系统性偏移 | `01_坑位与解决方式总表.md` PIT-005 | Fig.4/Fig.6 OCS-only 平线、image-only vs OCS-only 对比结论、degradation table 中 OCS 免疫的数值锚点 | 新 Blender-derived OCS manifest 后重跑 OCS-only kNN 和 MLP（per_part_log 30D / all_raw 45D） | pending | 是 |
| PIT-B-002 | P1 | 数据 | **fusion clean 性能和 branch masking 来自旧 OCS**。feature fusion concat5 的 1.47° 和 hit@5° 99.7% 依赖旧 OCS 特征。新 OCS 特征空间可能不同，需要重新训练和调参 | `01_坑位与解决方式总表.md` PIT-006 | Fig.5/Fig.7 fusion 结果、degradation table、branch masking 机制分析 | 新 OCS manifest 后重跑 feature fusion 和 late fusion，重新做 branch masking | pending | 是 |
| PIT-B-003 | P1 | 数据 | **OCS noise robustness 的噪声作用在旧 OCS 向量上**。旧实验噪声加在模块 A OCS 特征上，噪声敏感度可能和新 OCS 不同 | `01_坑位与解决方式总表.md` PIT-007 | degradation table 中 OCS noise 实验、结论"OCS 对噪声免疫"的量化边界 | 新 OCS 后重跑 OCS noise robustness（保持相同的噪声 σ 实现） | pending | 是 |
| PIT-B-004 | P1 | 数据 | **late-fusion beta sweep（12f）中 OCS-only 端来自旧模型** | `01_坑位与解决方式总表.md` PIT-008 | beta sweep 曲线形态、OCS/image 在融合中的相对权重 | 新 OCS 后重跑 12f | pending | 是 |
| PIT-B-005 | P1 | 数据 | **outlier gallery（12g）来源于旧 12b** | `01_坑位与解决方式总表.md` PIT-009 | outlier gallery 全部案例（42/49,950）、50% at |pitch|>75° 等统计 | 新 12b 后重建 12g | pending | 是 |
| PIT-B-006 | P1 | 数据 | **Fig3 OCS heatmap 指向旧 `ocs_scan.csv`**。v0.3 稿件中 per-part OCS 热图和极坐标图数据源为旧模块 A 数据 | `01_坑位与解决方式总表.md` PIT-010 | Fig.3a/b/c per-part OCS heatmap、Fig.3d 遮挡率/损失热图 | v0.4 source data 全部替换为 Blender-derived OCS | pending | 是 |
| PIT-B-007 | P1 | 数据 | **小项目"最亮姿态/星等范围"读取旧 phase63 OCS scan** | `01_坑位与解决方式总表.md` PIT-014 | "卫星光度范围与最亮观测几何"小项目的相对星等和最亮姿态结论 | 标记旧口径；v0.4 后更新 | pending | 否 |
| PIT-C-001 | P1 | 代码 | **旧代码路径硬编码到旧目录**。旧 `config.py` 和实验脚本中使用 `结果/模块A_重构/`、`结果/模块B_渲染/` 等旧目录路径。新代码如果不修改，可能混用新旧数据 | 旧 CLAUDE.md §八（"Windows Git Bash + 中文路径"坑）、`98_外部材料备份/03_关键代码快照/01_code/config.py` 等 | v0.4 代码重写时的路径配置 | v0.4 代码工作区使用新的输出目录（`结果/模块A_v0.4_BlenderOCS/`），配置文件只引用新路径 | pending | 否 |
| PIT-C-002 | P1 | 代码 | **自动查找 latest run 的逻辑可能误读旧结果**。旧 `inv_common.py` 等可能使用 `max()` 或 `sorted()` 找最新 run 目录。如果新旧结果都在同一层级，可能读错 | 旧代码快照中 `inv_common.py`（需审计） | 反演训练脚本的自动数据加载 | v0.4 使用显式 manifest path，不依赖 latest-run 启发式 | pending | 否 |
| PIT-C-003 | P1 | 代码 | **模块 A/B/反演代码的数据口径不一致**。旧 `brdf_postprocess.py` 计算 OCS_image 时使用 `pixel_area · f_r · NoL`，但旧模块 A OCS 使用 `A_face · f_r · NoL · NoV`。两者数学上 NoV 可能抵消，但 pixel_area 和 projected face area 的语义关系需要显式审计 | `98_外部材料备份/04_关键诊断与结果快照/20260528_brdf_postprocess_summary.json`（pixel_area_m2 = 0.00016015）、旧 CLAUDE.md 进度档案第 185 行（"A_face_pix = pixel_area / NoV … NoV 抵消 … 数学自洽"） | OCS 绝对值、per-part OCS 比例关系 | v0.4 统一使用 pixel-level 的公式 `Σ pixel_area · f_r · NoL`，文档明确写清 pixel_area 的物理含义和投影面积关系 | pending | 是 |

### 2.3 P2 坑位（影响记录、复现或表述）

| ID | 优先级 | 类型 | 问题描述 | 证据文件 | 影响范围 | v0.4 解决方式 | 状态 | 是否需要 Codex 复审 |
|---|---|---|---|---|---|---|---|---|
| PIT-E-001 | P2 | 写作 | **v0.3 可能有过强表述**。旧 CLAUDE.md §4.2 论文主线中写了"OCS provides a physically interpretable, degradation-immune photometric constraint"。如果采样口径不统一，"physically consistent" 的主张需要降级 | `98_外部材料备份/01_v0.3封存材料/主稿_v0.3_Acta_ASR润色版.md`（待审读全文） | v0.3 稿件中方法可信度表述 | v0.4 用统一的 Blender-derived OCS 后，"physically consistent" 主张更强而非更弱。同时保持写作红线 | pending | 是 |
| PIT-E-002 | P2 | 写作 | **synthetic benchmark 边界声明需要收紧**。v0.3 在物理一致性的前提下可以写 benchmark，但旧采样问题削弱了这个前提。v0.4 必须明确声明"no real telescope validation"和"synthetic forward model only" | `01_v0.3封存/00_v0.3封存说明.md` 第 29 行（"谨慎边界：无真实望远镜验证、synthetic benchmark、fixed roll、nominal material"） | v0.4 稿件全文的边界声明 | v0.4 在 Abstract/Introduction/Conclusion 中统一升级边界声明 | pending | 是 |
| PIT-E-003 | P2 | 写作 | **Blender-derived OCS 不能被写成"真实值"**。`00_公式与Blender分工说明.md` 第 89-90 行已明确"不把 Blender OCS 写成'天然真实值'"。但在具体表述中容易滑向过度自信 | `04_BlenderOCS方法重建/02_Blender采样选择与现实目标说明.md` 第 38-43 行（应写成 "observation-consistent synthetic forward model, not real-telescope validation"） | v0.4 方法部分和 Discussion | v0.4 写作时统一使用：Blender-derived pixel-level OCS is a more observation-consistent synthetic proxy, not a ground-truth measurement | pending | 否 |
| PIT-F-001 | P2 | 管理 | **旧新结果混放风险**。旧结果在 `结果/模块A_重构/`、`结果/模块B_渲染/`、`结果/模块C_反演/` 和 `论文改进/补充实验/结果/`，v0.4 新结果需要明确隔离。当前 v0.4 文件夹已规划三层隔离（`03_全项目排查/01_坑位与解决方式总表.md` 第 57-67 行），但新结果目录尚未创建 | `03_全项目排查/01_坑位与解决方式总表.md` §6 | v0.4 结果目录结构、后续论文图表 source data | 创建新结果目录（`结果/模块A_v0.4_BlenderOCS/` 等），在 v0.4 命名规范文件中写入禁止写入旧目录的红线 | pending | 否 |
| PIT-F-002 | P2 | 管理 | **缺少统一 source-data index**。当前每个实验的 OCS manifest、image run、split、feature mode、seed 分散在脚本、summary 和说明文件中 | `03_全项目排查/00_统一问题登记表.md` AUDIT-009 | v0.4 可复现性 | v0.4 建立 source-data index，每个实验产物附带 `source_data.json` 记录所有上游数据源路径 | pending | 否 |
| PIT-F-003 | P2 | 管理 | **Q12-Q14 投稿材料未补齐**。Data/Code Availability、Author Contributions、Funding、COI 在 v0.3 中被标记为不代填 | `03_全项目排查/00_统一问题登记表.md` AUDIT-008 | v0.4 定稿后的投稿合规 | v0.4 定稿后补（不在当前阶段处理） | pending | 否 |
| PIT-D-002 | P2 | 实验 | **12d 跨 phase 泛化（phase120 ~80°）可能也需要基于新 OCS 重跑**。重跑清单中标记为 "yes if OCS/fusion involved"。如果 image-only 的 phase120 结果可复用（图像渲染链路不变），需明确声明 | `05_全链路重跑/00_重跑任务清单.md` line 39 | v0.4 补充实验中跨 phase 泛化章节 | 审计 12d image-only 是否与 v0.4 image run 一致后决定 | pending | 否 |
| PIT-D-003 | P2 | 实验 | **12e 质心居中控制实验**。重跑清单中标记 image-only 部分 "lower risk"。需确认居中后的 image 渲染是否使用与 v0.4 完全相同的姿态和投影参数 | `05_全链路重跑/00_重跑任务清单.md` line 40 | v0.4 补充实验中质心控制章节 | v0.4 重新汇总时检查居中 image 是否来自 v0.4 渲染批次 | pending | 否 |
| PIT-E-004 | P2 | 写作 | **caption/source data 全部指向旧路径**。v0.3 图中所有 caption 和 source data 引用旧模块 A 路径和 run ID | `01_v0.3封存/00_v0.3封存说明.md` 第 41-45 行 | v0.4 稿件全部图表 | v0.4 图表全部使用新 source data 路径 | pending | 否 |

### 2.4 未闭环坑位（需要作者确认）

| ID | 优先级 | 类型 | 问题描述 | 证据文件 | 影响范围 | v0.4 解决方式 | 状态 | 是否需要 Codex 复审 |
|---|---|---|---|---|---|---|---|---|
| PIT-UNK-001 | P0 | 方法 | **GGX/Cook-Torrance 与 LegacyPhong 的选择**。`00_公式与Blender分工说明.md` 第 112 行列出待定问题："使用 GGX/Cook-Torrance 还是保留 LegacyPhong 作为基线"。旧模块 A 同时支持两种 BRDF，但主反演和补充实验使用的是 GGX。如果 v0.4 切换 BRDF，需要全部重跑；如果保留 GGX，只需重建 OCS 数据源 | `04_BlenderOCS方法重建/00_公式与Blender分工说明.md` §6 line 112 | v0.4 的 BRDF 选择决定全部实验的基线 | 建议 v0.4 使用 GGX/Cook-Torrance 作为主 BRDF（与旧口径一致），LegacyPhong 保留作为附录对照 | open | 是 |
| PIT-UNK-002 | P0 | 方法 | **Blender geometry pass resolution 和 ortho scale 待定**。`00_公式与Blender分工说明.md` 第 113 行列出。旧 BRDF postprocess 使用 resolution=256（`brdf_postprocess_summary.json` line 14），进度档案第 188 行提到 "res=128 vs 256 OCS 差 <1%，非根因"。但 v0.4 需要确认最终分辨率 | `04_BlenderOCS方法重建/00_公式与Blender分工说明.md` §6 line 113、`98_外部材料备份/04_关键诊断与结果快照/20260528_brdf_postprocess_summary.json` resolution=256 | 图像分辨率（影响 image-only 和 fusion）、OCS 积分精度 | 建议 v0.4 使用 256×256 作为论文分辨率（与旧模块 B 一致），在补充材料中提供 128 vs 256 ablation | open | 否 |
| PIT-UNK-003 | P1 | 方法 | **pixel projected area 的计算方式待定**。`00_公式与Blender分工说明.md` 第 114 行列出的待定项。旧 BRDF postprocess 中 `pixel_area_m2` = ortho_scale² / res²（正交投影下为常数）。但在精确投影几何中，边缘像素应有不同的 projected area | `04_BlenderOCS方法重建/00_公式与Blender分工说明.md` §6 line 114 | OCS 积分的数值精度，特别是在大倾角姿态下边缘像素的贡献权重 | v0.4 方法冻结时明确：正交投影下 pixel_area 是否为常数，如果不是则从 Blender 输出逐像素 area | pending | 否 |
| PIT-UNK-004 | P1 | 方法 | **clean image 的线性响应与训练 PNG 的 log1p 转换关系待定**。`00_公式与Blender分工说明.md` 第 118 行列出的待定项。当前训练使用 PNG 8-bit（0-255），而物理图像是线性辐亮度。转换关系如果不明确，image-only 的绝对亮度信息可能丢失 | `04_BlenderOCS方法重建/00_公式与Blender分工说明.md` §6 line 118 | image-only 和 fusion 的输入图像预处理管线 | v0.4 方法冻结时明确：图像从线性辐亮度到 8-bit PNG 的色调映射（tone-mapping），以及训练时是否反转（inverse tone-mapping） | pending | 否 |
| PIT-UNK-005 | P2 | 实验 | **split 一致性需要全局审计**。所有旧实验的 split（train/val/test 划分）未必使用相同的随机种子和分法。v0.4 必须确保所有实验使用全局统一的 split | 旧 CLAUDE.md §4.2 各实验未标注 split 和 seed | v0.4 所有对比结果的可比性 | v0.4 使用全局统一 split（固定 seed），记录在 manifest 中 | pending | 否 |

---

## 三、坑位统计

| 优先级 | 方法 | 数据 | 代码 | 实验 | 写作 | 管理 | 合计 |
|---|---|---|---|---|---|---|---|
| P0 | 3 | 1 | 0 | 1 | 0 | 0 | **5** |
| P1 | 3 (未闭环中的) | 7 | 3 | 0 | 0 | 0 | **10 + 3** |
| P2 | 0 | 0 | 0 | 2 | 4 | 3 | **9** |
| — | — | — | — | — | — | — | — |
| 合计 | 6 | 8 | 3 | 3 | 4 | 3 | **27** |

注：P0 中 PIT-UNK-001 和 PIT-UNK-002 归类为"未闭环但 P0 级"，计入方法类 P0（共 5 个 P0）。
注：P1 未闭环 3 个（PIT-UNK-003/004/005）未计入正式 P1 总数。

---

## 四、最阻断 v0.4 启动的 3 个问题

1. **PIT-A-001**：OCS 与图像采样口径不统一 —— 这是导致 v0.3 封存的根因，v0.4 的核心目标就是解决此问题。不解决则 v0.4 没有意义。

2. **PIT-A-003**：sun-side visibility / self-shadow 定义未闭合 —— 方法冻结的最前置阻塞项。论文如果写"含自遮挡/阴影"，必须实现；如果暂时不实现，必须在 v0.4 中清楚限定为 "camera-viewer-side visibility only"。

3. **PIT-UNK-001**：BRDF 模型选择（GGX vs LegacyPhong）—— 决定 v0.4 所有实验的基线和计算量。如果维持 GGX 作为主 BRDF，v0.4 可以直接基于旧 EXR geometry pass 重算 OCS（因为 BRDF 由 Python 公式负责，geometry pass 不含材质信息）。这是启动 v0.4 代码阶段前必须确认的决策。

---

## 五、已读取的排查文件清单

- `CLAUDE.md`（v0.4 工作区版本）
- `00_只打开本文件夹时的启动说明.md`
- `00_v0.4总控流程.md`
- `01_v0.3封存/00_v0.3封存说明.md`
- `02_重大分支路线图/00_重大分支路线图.md`
- `03_全项目排查/00_统一问题登记表.md`
- `03_全项目排查/01_坑位与解决方式总表.md`
- `04_BlenderOCS方法重建/00_公式与Blender分工说明.md`
- `04_BlenderOCS方法重建/01_模块A_B与统一前向模型对比决策.md`
- `04_BlenderOCS方法重建/02_Blender采样选择与现实目标说明.md`
- `05_全链路重跑/00_重跑任务清单.md`
- `00_启动前准备/00_启动前必做清单.md`
- `98_外部材料备份/00_备份清单.md`
- `98_外部材料备份/00_项目指导文件/CLAUDE.md`（旧版）
- `98_外部材料备份/00_项目指导文件/进度档案_仿真与反演_full.md`（前 200 行）
- `98_外部材料备份/04_关键诊断与结果快照/20260528_ocs_comparison.csv`（前 50 行）
- `98_外部材料备份/04_关键诊断与结果快照/20260528_brdf_postprocess_summary.json`
- `98_外部材料备份/04_关键诊断与结果快照/subface_adaptive_comparison.csv`

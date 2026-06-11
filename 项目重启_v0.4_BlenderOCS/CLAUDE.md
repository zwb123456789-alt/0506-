# CLAUDE.md

最后更新：2026-06-09

## 1. 当前项目状态

这是 OCS-光度图像联合仿真与姿态反演项目的 v0.4 重启工作区。

当前项目与论文主线已经冻结，以 24 号为 source-of-truth，25 号为原因备案：

```text
24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
25_v0.4主线冻结原因备案_为什么采用24号.md
```

15-23 号历史定位稿已经归档到：

```text
99_归档索引/03_v0.4定位历史稿归档_15-23/
```

后续主动读取只保留 24 + 25；15-23 只在追溯旧定位、口径/形态论证或复审过程时按需读取。

旧 v0.3 Acta/ASR 主投优先稿已经封存，不再进入投稿工程化。封存原因不是写作问题，而是 OCS 数据源定义级问题：

- 旧主反演与补充实验使用模块 A face-level / face-center OCS 扫描表。
- 图像端使用 Blender pixel-level geometry/pass 采样。
- 二者采样口径不统一，可能影响 OCS-only、fusion、OCS noise、branch masking、12b/12c/12f/12g 等结果。
- v0.4 不再定位为“真实未知非合作目标姿态反演系统”，而是 model-known 条件下 OCS/image 姿态信息可观测性、互补性与置信一致性研究。

当前主线 OCS 定义为 independent non-imaging photometric channel 下的跨几何多观测光度向量；image-derived OCS 只作为 common-mode failure 对照；F1 单瞬时总光通量只作信息下界，F2 per-part OCS 只作 semi-oracle / diagnostic，L2 时域光变曲线进入 Future Work。

投稿目标不再默认降到旧 Acta/ASR 主投优先稿。作者最新确认：最终投稿目标以外部 `文献/00投稿目标/` 中列出的较高期刊为参照，目标是尽量向上冲刺，越高越好；Acta/ASR 只作为稳健 SCI 选项之一，不作为默认起点。后续论文写作应以高水平期刊要求牵引问题定义、指标、图表和审稿防线，但不得因此扩大未经证据支撑的 claim。

## 2. 默认启动读取规则

上下文有限，打开本文件夹后不要一次性读取全部指导文件和备份材料。默认只读最小启动集：

1. `CLAUDE.md`
2. `00_只打开本文件夹时的启动说明.md`
3. `00_v0.4总控流程.md`

读完以上 3 个文件后，应先判断当前阶段，再按用户给出的阶段提示词读取对应文件。除非阶段提示词明确要求，不要主动全文读取：

- `01_v0.3封存/`
- `02_重大分支路线图/`
- `03_项目审计与方法说明/`
- `04_BlenderOCS方法重建/`
- `05_全链路重跑/`
- `06_论文v0.4重写接入/`
- `98_外部材料备份/`

如果任务涉及项目定位、论文主线、投稿方向、重跑目标或 OCS 口径/形态，必须优先读取：

```text
24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
25_v0.4主线冻结原因备案_为什么采用24号.md
```

`98_外部材料备份/` 只作为索引和证据库使用。通常先读 `98_外部材料备份/00_备份清单.md`，再按当前任务需要抽取具体文件；不要开局扫描整个备份目录。

文献与引用材料入口为 `98_外部材料备份/06_文献与引用材料/`。当前只复制了 BibTeX、文献清单和必读清单；不要假定外部旧文献目录会自动可用。

投稿目标来源为外部 `文献/00投稿目标/`，当前是 3 张目标期刊截图；涉及投稿定位、目标期刊、期刊分层或写作风格时，应按需查看该目录，不要扫描整个 `文献/`。

每个阶段的 Claude 工作都应由对应阶段文件夹中的专门提示词或 Codex 复审文件末尾提示词指定“本阶段必读文件、按需检查文件、禁止读取或禁止修改范围”。

## 3. v0.4 核心方法与论文口径

v0.4 采用统一前向物理模型：

```text
Blender 负责“看见哪里”：
STL、姿态、正交投影、depth、normal、part ID、pixel-level geometry visibility。

Python/公式负责“如何反光”：
显式 GGX/Cook-Torrance BRDF、NoL/NoV、OCS 积分、per-part OCS、clean image linear response。

反演代码负责：
生成特征、训练 OCS-only / image-only / fusion、执行补充实验和结果汇总。
```

不要把 Blender 写成真实观测验证。v0.4 只能写成 observation-consistent synthetic forward model。

论文主线不以 mean error / Hit@5 结果表为唯一中心，而以以下三问组织证据链：

```text
What can be known?
When are OCS and image complementary?
When should we trust the estimate?
```

后续代码和 manifest 必须服务 24 号的新指标需求，尤其是 multi-geometry OCS vector、posterior-like distribution、top-k candidates、per-attitude results、branch masking、OCS noise monotonicity、modality attribution 和 image-derived OCS_B 对照。

## 4. 当前红线

- 不再把 v0.3 当作可投稿版本。
- 不再把 v0.4 写成真实未知目标姿态反演系统。
- 不混用旧模块 A OCS 和新 Blender-derived OCS。
- 不局部替换 OCS 后继续沿用旧 fusion / robustness / 12b / 12c / 12f 数字。
- 不直接使用 Blender 内置材质黑箱作为最终亮度模型。
- 不声称真实望远镜验证、真实大气链路或 field-proven robustness。
- 若论文写“含自遮挡/阴影”，v0.4 必须明确并实现 sun-side visibility / self-shadow，或清楚限定边界。
- 不把单瞬时 OCS 总光通量写成主线 OCS。
- 不把 per-part OCS 写成 independent photometric channel 下的可运营特征。
- 不把 L2 时域光变曲线、完整 Earthshine 或完整探测器链路并入本轮主论文。
- 不把 image-derived OCS 与 image 的一致性直接解释为高置信。

## 5. 当前阶段与下一步

项目与论文主线定位已经冻结。当前有效定位文件为：

```text
24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
25_v0.4主线冻结原因备案_为什么采用24号.md
```

启动前排查、方法冻结和代码阶段准备文档也已经完成。当前有效方法冻结文件为：

```text
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
```

代码阶段准备文件为：

```text
05_全链路重跑/00_重跑任务清单.md
05_全链路重跑/01_代码阶段资产盘点与实施计划_Claude.md
05_全链路重跑/02_第一批最小验证任务清单_Claude.md
```

以上三份文件已经按 Codex R01 复审意见完成小修，并通过最终确认：

```text
97_交互审阅记录/03_Codex审阅/05_全链路重跑/R01_Codex_复审_代码阶段准备文档.md
```

代码实施前指标规范也已经冻结。当前有效指标规范为：

```text
05_全链路重跑/v0.4_信息量与置信指标实现规范_最终冻结版.md
```

对应 Codex 复审与最终确认文件为：

```text
97_交互审阅记录/03_Codex审阅/05_全链路重跑/R03_Codex_复审_信息量与置信指标实现规范候选.md
97_交互审阅记录/03_Codex审阅/05_全链路重跑/R04_Codex_确认_信息量与置信指标规范冻结通过.md
```

当前状态为“代码实施前指标规范已冻结；下一步进入代码骨架与 phase0 门控验证准备”。不要直接全量重跑，也不要训练模型。后续如果继续推进，下一步为：

1. 新建或搭建 `06_v0.4_code/` 代码骨架。
2. 记录环境依赖和硬件信息，生成 `environment.md` 或 `environment.yml`。
3. 用 1 个简单姿态完成 smoke test，测量单姿态耗时与存储体量。
4. 优先实现 depth round-trip sanity check。
5. 再实现 camera geometry pass、Position/WorldCoord、sun-view depth 和 V_sun_macro reprojection。
6. 完成 20 姿态 shadow validation 并确定 `depth_epsilon_m_final` 后，才允许进入全量生成。

代码阶段总路线：

```text
代码资产盘点
-> depth round-trip sanity check
-> camera-view geometry / Position pass
-> sun-view depth pass
-> V_sun_macro_mask reprojection
-> 20 姿态 shadow validation
-> BRDF/OCS/image 后处理
-> manifest 生成与一致性检查
-> single-geom 主线数据集
-> multi-geom 扩展数据集
-> OCS-only / image-only / fusion 训练
-> 退化与补充实验
-> 论文 v0.4 接入
```

## 6. 文件夹约定

本文件夹为当前工作入口。外部旧目录只作为备份来源，不再直接修改。

已复制的外部材料位于：

```text
98_外部材料备份/
```

其中轻量文献入口位于：

```text
98_外部材料备份/06_文献与引用材料/
```

后续如果需要旧文件，先复制进本文件夹并登记，再使用。

Claude 草稿、GPT 草稿、Codex 复审意见、阶段提示词和中间候选稿统一按来源放入：

```text
97_交互审阅记录/01_Claude输出/
97_交互审阅记录/02_GPT输出/
97_交互审阅记录/03_Codex审阅/
```

阶段目录只保留最终通过、当前有效、会被后续执行引用的项目文件。具体规则见：

```text
97_交互审阅记录/00_交互审阅记录说明.md
99_归档索引/02_项目文件夹职能规范.md
```

阶段通过后的硬约束：

```text
Codex 复审判定某阶段通过、可进入下一阶段，或小修后确认通过时，
只能由 Codex 审阅端主动同步 CLAUDE.md、00_只打开本文件夹时的启动说明.md、
00_v0.4总控流程.md、当前阶段入口/任务清单、下一阶段入口/提示词和 99_归档索引。
Claude 执行端只负责在对应阶段目录输出方案、候选稿、修订稿或执行计划，
不负责更新启动集、总控或归档索引。
未同步这些相关进度文档，不得宣称阶段已闭环。
```

## 7. 给后续对话的恢复提示

如果新对话只看到本文件夹，请按以下方式恢复：

```text
请先阅读 CLAUDE.md 和 00_只打开本文件夹时的启动说明.md。
当前目标是 v0.4 Blender-derived OCS 重启。
不要继续 v0.3 投稿工程化。
项目与论文主线已经以 24 号冻结，25 号为原因备案。
方法冻结、代码阶段准备文档、代码实施前指标规范均已通过。当前停在代码骨架与 phase0 门控验证准备状态。
如继续推进，进入 06_v0.4_code/ 代码实施准备，先搭建代码骨架、记录环境依赖、完成单姿态 smoke test，再实现 depth round-trip sanity check；不要直接全量重跑或训练模型。
```

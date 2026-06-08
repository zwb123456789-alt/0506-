# Codex 复审意见：相似方法坑专项排查

最后更新：2026-06-08

复审对象：

```text
03_全项目排查/07_相似方法坑专项排查报告_Claude.md
04_BlenderOCS方法重建/03_v0.4前向模型冻结问题清单_Claude.md
```

## 1. 总体判断

Claude 这轮排查方向正确，已经从“旧结果能否复用”转向“方法/思路/定义/链路口径坑”。相比第一轮，它确实挖出了更接近本次 OCS 采样问题本质的坑：

- H1：diffuse-only 下 A/B visible area 语义差异。
- H4：log1p / tone-mapping / 线性辐亮度 / 8-bit PNG 响应链未冻结。
- U1：sun-side visibility 的三条实现路径。
- U2：GGX `G_Smith` microfacet shadowing-masking 与宏观几何遮挡术语混淆。
- U3：multi-geometry OCS 与 single-geometry image 的公平性问题。

但这两份文件不能直接作为最终方法冻结依据。核心原因是：Claude 已经开始给出具体推荐方案，其中部分推荐过早或不严谨，尤其是 visibility mask、sun-side visibility、thin-plate 解释和 image response 字段。

结论：这轮排查通过，适合作为下一步“方法冻结规范”的输入；但必须先按本复审意见修正关键决策口径。

## 2. 主要复审意见

| 编号 | 严重度 | 对应位置 | 问题 | Codex 判断 | 修正要求 |
|---|---|---|---|---|---|
| CR2-001 | P0 | 方法冻结清单 Q1 | Q1 推荐 `camera-visible only`，并解释为“不论 sun 方向”。 | 这不严谨。OCS 的几何 mask 可以是 camera-visible pixels，但像素贡献必须至少包含 `NoL=max(n·sun,0)`。否则背光面也会进入 OCS。 | 改成：baseline mask = camera-visible object pixels；radiance/OCS contribution = 0 if `NoL<=0` or `NoV<=0`；sun-ray self-shadow 是额外 macro-occlusion 选项。 |
| CR2-002 | P0 | 方法冻结清单 Q13 | Q13 直接推荐“不实现 sun shadow，只限定 viewer-side visibility”。 | 这是过早降级。v0.4 重启目标是统一前向物理模型，0603 汇报也写了“自遮挡模型”。是否放弃 sun-side visibility 应作为作者/Codex 决策，而不是 Claude 因复杂度直接推荐。 | 方法冻结前必须给出 A/B/C 三方案的成本、实现路径、验证方法和写作后果。默认推荐应改为“优先评估实现 sun-side visibility；若代码成本不可接受，再明确降级为 viewer-side only”。 |
| CR2-003 | P1 | 排查报告 H2 | H2 对薄板“双面同时满足法线判据”的物理解释可疑。两个相反法线的面是否能同时满足 `n·sun>0` 和 `n·det>0` 取决于 sun/det 位于法线哪一侧，不能简单写成“太阳和探测器同侧导致两面都满足”。 | H2 的现象值得保留，但因果解释不能直接作为方法结论。旧记录中确有 thin-plate / pixel-level 差异，但 v0.4 应通过 depth-buffer sanity check 验证，而不是沿用这句解释。 | 改为“薄板/双面/边缘可见性存在旧记录风险，需以 Blender depth + IndexOB sanity check 关闭”。不要把 72× 差异完全归因于双面同时计入。 |
| CR2-004 | P1 | 排查报告 H3、方法冻结 Q14 | H3 写“Blender Cycles 背向面着色伪影”可能混淆：v0.4 不应依赖 Blender Combined/material shading 亮度，而是读 geometry pass 后用 Python BRDF 计算。 | 真正需要冻结的是：Normal pass 是否为几何法线/世界法线；后处理是否显式过滤 `NoL<=0`、`NoV<=0`。不要把问题写成主要由 Cycles 着色决定。 | 在方法冻结中写成“Python BRDF 后处理边界条件”，而不是“修复 Blender shading”。 |
| CR2-005 | P1 | 方法冻结 Q11 | Q11 已指出 log1p 链，但 `scale`、`max_val`、训练输入是否反量化仍是占位。 | 方法冻结不能留下 `<value>`。需要从旧代码或 v0.4 新规范中明确：线性响应如何归一化、是否按全局最大值、每帧最大值还是固定常数。 | 下一步 Claude 必须审计旧 `train_cnn.py` / `brdf_postprocess.py` / robustness 脚本，写出具体公式和参数。若旧链不一致，v0.4 重新定义。 |
| CR2-006 | P1 | 方法冻结 Q16 | `source_data.json` 示例中硬写 `split_seed=42`、`split_method=coarse_to_fine`、`geometries=[...]`。 | 可以作为示例，但不能作为已冻结事实。v0.4 重跑前必须由方法规范决定 split、phase、几何数量和 seed。 | 改为 schema 字段定义，不要填伪默认值；实际 run 再写真实值。 |
| CR2-007 | P2 | 排查统计 | 统计表把 H5 放在“写作”列，但 H5 本质是遮挡定义变化和遮挡率解释。 | 分类小问题，但会影响后续优先级。 | H5 归入遮挡/方法解释，论文只是后果。 |
| CR2-008 | P2 | 旧记录隐性坑 | 旧记录隐性坑第 8 项 bibliography 作者占位，与本轮“相似方法坑”关系弱。 | 可以保留为管理坑，但不应混入方法冻结问题。 | 移到论文/投稿管理清单，不进入方法冻结。 |

## 3. 哪些内容可以采纳

以下内容建议直接进入后续方法冻结规范：

| 条目 | 采纳方式 |
|---|---|
| H1 visible area 语义差异 | 作为 v0.4 改用 Blender pixel-level sampling 的核心证据之一 |
| H4 图像响应链未冻结 | 必须写入方法冻结规范，尤其是 linear -> log1p -> PNG -> train 的完整链路 |
| S2 / Q8 / Q9 `NoV` 抵消与 `pixel_area` | 必须作为 OCS 公式核心章节 |
| U2 / Q6 术语区分 | 方法章节加入术语表：microfacet shadowing-masking vs macro geometric occlusion |
| U3 多几何公平性 | 方法冻结或实验设计中决定主表是否使用 single-geometry baseline，multi-geometry 放补充或单独说明 |
| S7 / Q17 禁止 latest-run | 进入代码规范，所有脚本显式传入 manifest |

## 4. 下一步方法冻结必须回答的修正版问题

后续生成 `04_v0.4前向模型冻结规范.md` 时，至少回答这些问题：

1. **OCS mask 与贡献分开定义**：
   - mask：camera-visible object pixels。
   - contribution：`0 if NoL<=0 or NoV<=0`。
   - optional macro shadow：sun-ray visibility / self-shadow。

2. **sun-side visibility 决策**：
   - 方案 A：Blender sun-view / shadow pass。
   - 方案 B：Python ray-cast。
   - 方案 C：viewer-side only + 明确写作边界。
   - 不能只因复杂度直接选 C。

3. **OCS 公式**：
   - 连续公式。
   - 正交投影像素离散公式。
   - `NoV` 抵消条件。
   - `pixel_area_projected` 单位与来源。
   - edge fractional coverage 简化。

4. **图像响应链**：
   - 线性 radiance 生成。
   - log1p 公式。
   - 归一化常数。
   - 8-bit PNG 是否只是训练存储。
   - 退化实验在 linear 空间还是 log 空间作用。

5. **几何与坐标 sanity check**：
   - 3 个姿态 normal/sun/view 对账。
   - thin-plate depth / IndexOB 对账。
   - 非水密 STL depth 行为检查。

6. **manifest/source_data schema**：
   - 只定义字段，不填伪默认值。
   - 每个 run 写真实 split、seed、phase、geometry、method version。

## 5. 是否可以进入下一步

可以进入下一步，但下一步不应直接写代码，也不应让 Claude 自由选择最终物理方案。

下一步应让 Claude 生成：

```text
04_BlenderOCS方法重建/04_v0.4前向模型冻结规范_Claude.md
04_BlenderOCS方法重建/05_v0.4数据与manifest字段规范_Claude.md
```

提示词必须包含本文件 CR2-001 到 CR2-008。生成后仍需 Codex 复审，再决定是否进入代码阶段。

---

## 附录：下一步 Claude 提示词

你现在位于：

```text
项目重启_v0.4_BlenderOCS/
```

请先阅读本文件：

```text
03_全项目排查/08_Codex复审意见_相似方法坑专项排查.md
```

本次任务只生成 v0.4 前向模型冻结规范和数据/manifest 字段规范，不写代码、不重跑实验。

### 必读文件

```text
CLAUDE.md
00_只打开本文件夹时的启动说明.md
00_v0.4总控流程.md
04_BlenderOCS方法重建/00_公式与Blender分工说明.md
04_BlenderOCS方法重建/01_模块A_B与统一前向模型对比决策.md
04_BlenderOCS方法重建/02_Blender采样选择与现实目标说明.md
03_全项目排查/06_方法思路类坑位与处置汇总_Codex.md
03_全项目排查/07_相似方法坑专项排查报告_Claude.md
04_BlenderOCS方法重建/03_v0.4前向模型冻结问题清单_Claude.md
03_全项目排查/08_Codex复审意见_相似方法坑专项排查.md
98_外部材料备份/00_备份清单.md
```

按需检查旧记录和代码快照，重点查公式、图像响应、manifest、split、latest-run：

```text
98_外部材料备份/00_项目指导文件/进度档案_仿真与反演_full.md
98_外部材料备份/02_0603汇报材料/20260603_项目进展汇报_v2_extracted_text.txt
98_外部材料备份/03_关键代码快照/02_blender/brdf_postprocess.py
98_外部材料备份/03_关键代码快照/03_inversion/train_cnn.py
98_外部材料备份/03_关键代码快照/补充实验代码/
```

### 必须吸收的 Codex 修正

必须逐条吸收本文件 CR2-001 到 CR2-008，尤其：

1. 不要把 `camera-visible only` 写成“不论 sun 方向都计入”。正确写法是：mask 为 camera-visible object pixels；若 `NoL<=0` 或 `NoV<=0`，贡献显式为 0；sun-ray self-shadow 是额外 macro-occlusion 选项。
2. 不要直接推荐放弃 sun-side visibility。必须列出 Blender sun-view/shadow pass、Python ray-cast、viewer-side only 三种方案，并说明成本、验证方式、论文后果。
3. 薄板可见性不要直接归因于“双面同时满足法线判据”，应写成 thin-plate / double-sided / edge visibility 风险，并要求 Blender depth + IndexOB sanity check。
4. Blender Cycles 背向面问题应写成 Python BRDF 后处理边界条件：确认 normal pass 坐标，并显式过滤 `NoL<=0`、`NoV<=0`。
5. log1p 链不能留 `<value>` 占位。能从旧代码查到就写具体值；查不到则明确 v0.4 重新定义。
6. manifest/source_data 只写 schema，不填伪默认值。

### 输出文件

请生成：

```text
04_BlenderOCS方法重建/04_v0.4前向模型冻结规范_Claude.md
04_BlenderOCS方法重建/05_v0.4数据与manifest字段规范_Claude.md
```

### 文件 1 必须包含

```text
1. v0.4 前向模型总图
2. Blender / Python / 反演代码分工
3. 坐标系与姿态定义
4. Geometry pass 字段
5. OCS 连续公式
6. OCS 像素离散公式
7. pixel_area_projected 定义、NoV 抵消条件、edge pixel 处理
8. NoL/NoV 边界条件
9. sun-side visibility 三方案与当前决策建议
10. GGX/Cook-Torrance BRDF 主模型
11. G_Smith microfacet shadowing-masking 与 macro geometric occlusion 术语区分
12. clean image 线性响应与 log1p/PNG/训练输入关系
13. 必须做的 sanity checks
14. 写作边界：synthetic forward model, no real telescope validation
15. 未冻结项和需要作者/Codex 决策项
```

### 文件 2 必须包含

```text
1. v0.4 所有旧结果全封存，所有主结果重跑
2. manifest 字段 schema
3. source_data.json 字段 schema
4. run_id / method_version / split_id / seed 规则
5. 禁止 latest-run 自动发现
6. OCS source 与 image source 一致性规则
7. 每个 summary / figure source data 必须记录的字段
8. 输出目录命名规范
9. 待 Codex 复审项
```

### 严格限制

- 不要写代码。
- 不要重跑实验。
- 不要修改外部旧目录。
- 不要把旧结果作为 v0.4 主结果。
- 不要把尚未决定的方案写成已解决。
- 不要用“复用旧结果”口径；旧结果统一封存。

完成后只总结生成文件、推荐方案、仍需作者/Codex 决策项、需要 Codex 复审的位置。

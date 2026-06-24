# R05 Codex：审阅 1C-E03 代码区创建前执行入口核对

最后更新：2026-06-23

## 1. 文件性质

本文审阅 Claude 输出：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
07_1C-E03_代码区创建前执行入口核对_Claude输出.md
```

本文只做 Codex 审阅、口径收敛和下一步执行提示词规划，不创建代码区，不创建结果区，不修改 13/14/24/25、`CLAUDE.md` 或书籍知识库。

## 2. 总体结论

Claude 1C-E03 基本通过。

其完成了以下执行型核对任务：

```text
1. 确认 06_v0.4_code/ 与 v0.4_results/ 尚未创建；
2. 确认三部件 STL、Blender exe、历史代码快照存在；
3. 摘出 config.py / materials.py / geometry.py 的可复用内容和必须改动点；
4. 明确当前 BRDF 只能按 B0 provisional Phong-like baseline 推进；
5. 列出创建代码区前的待确认问题；
6. 未创建目录，未写代码，未修改冻结文件。
```

本轮 Codex 判定：

```text
1C-E03：通过为“代码区创建前执行入口核对”材料。
无需让 Claude 重做。
下一步可进入 1C-E04：受控创建 Phase 0 代码骨架和验证输出目录。
```

## 3. 需要修正的口径

### 3.1 BRDF 字段不得写成 `phong_like_five_param`

Claude 在局部表述中仍出现：

```text
BRDF_MODEL = "phong_like_five_param"
Phong-like / 五参数冯主线
```

这在当前阶段不够稳妥。根据 R04，书中三部件材料参数尚未可靠定位，历史 Legacy Phong 不能等同于书中改进冯模型或 Torrance-Sparrow 五参数模型。

当前执行字段应统一为：

```text
brdf_model = "phong_like_provisional_baseline"
brdf_branch = "B0_baseline"
brdf_reference = "project_provisional_params_from_legacy_materials_py"
```

允许使用的口径：

```text
B0 project provisional Phong-like baseline
Legacy/simple Phong-like provisional baseline
```

禁止使用的口径：

```text
完整书中五参数冯模型
书中三部件材料参数已定位
book material parameter main anchor
phong_like_five_param 作为当前真实实现名
```

### 3.2 B1 / B2 不进入当前代码骨架必做项

后续可保留：

```text
B1：书中改进冯模型，式 (3.16)，参数 rho_d, rho_s, alpha, a, b；
B2：Torrance-Sparrow 五参数 / 改进六参数模型，式 (3.18) / (3.23)。
```

但 B1/B2 等待书籍知识库重整、原始图片证据归档和三部件材料对应关系确认后再执行。当前 Phase 0 smoke test 不以 B1/B2 为阻塞条件。

## 4. Codex 收敛后的 P0 决策

为避免把 13 个待确认问题全部推给作者，当前 P0 收敛为以下 5 条执行决策：

| 决策 | Codex 判定 |
|---|---|
| 是否创建代码区 | 可以创建 `06_v0.4_code/` |
| 输出目录 | 采用 `v0.4_results/`，与 14 号一致，暂不使用 `07_v0.4_results/` |
| BRDF smoke test 主线 | 采用 B0 `phong_like_provisional_baseline` |
| 13/14 是否立即小修 | 暂不小修；先在执行文件中记录覆盖口径 |
| 知识库是否阻塞 Phase 0 | 不阻塞；知识库重整与 Phase 0 并行 |

后续 P1 事项：

```text
1. 是否实现 B1 / B2；
2. 三部件与书中材料的对应关系；
3. 是否复制外部书籍图片进入项目内部证据区；
4. 是否受控小修 13/14 中 BRDF 字段；
5. 是否在知识库重整后更新路线一 C 的材料依据。
```

## 5. 下一步执行范围

下一步应执行 1C-E04，但只做 Phase 0 入口骨架，不进入真实渲染、全量生成、训练或论文正文改写。

允许创建：

```text
06_v0.4_code/
06_v0.4_code/00_config/
06_v0.4_code/01_geometry/
06_v0.4_code/02_blender/
06_v0.4_code/03_brdf/
06_v0.4_code/04_sun_shadow/
06_v0.4_code/05_postprocess/
06_v0.4_code/06_manifest/
06_v0.4_code/10_validation/
v0.4_results/
v0.4_results/00_validation/
```

允许写入：

```text
06_v0.4_code/00_config/environment.md
06_v0.4_code/00_config/config_v0_4.py
06_v0.4_code/00_config/materials_v0_4.py
06_v0.4_code/01_geometry/geometry_loader.py
06_v0.4_code/01_geometry/attitude_grid.py
v0.4_results/00_validation/phase0_entry_notes.md
```

本轮不允许：

```text
1. 启动 Blender 渲染；
2. 生成 EXR / PNG / npy 数据；
3. 运行全量 2664 姿态；
4. 训练任何模型；
5. 修改 13/14/24/25；
6. 修改 CLAUDE.md；
7. 修改书籍知识库；
8. 将 B0 写成书中五参数冯或书中材料参数。
```

## 6. 给 Claude 的 1C-E04 短提示词

```text
任务名：1C-E04 路线一C Phase 0 代码骨架与环境记录创建

你只执行 Codex 指定的文件创建，不做路线设计，不做阶段放行，不启动渲染，不训练模型。

依据文件：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R05_Codex_审阅_1C-E03代码区创建前执行入口核对.md
3. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/07_1C-E03_代码区创建前执行入口核对_Claude输出.md
4. 03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/config.py
5. 同目录下 materials.py
6. 同目录下 geometry.py

创建目录：
项目重启_v0.4_BlenderOCS/06_v0.4_code/
项目重启_v0.4_BlenderOCS/06_v0.4_code/00_config/
项目重启_v0.4_BlenderOCS/06_v0.4_code/01_geometry/
项目重启_v0.4_BlenderOCS/06_v0.4_code/02_blender/
项目重启_v0.4_BlenderOCS/06_v0.4_code/03_brdf/
项目重启_v0.4_BlenderOCS/06_v0.4_code/04_sun_shadow/
项目重启_v0.4_BlenderOCS/06_v0.4_code/05_postprocess/
项目重启_v0.4_BlenderOCS/06_v0.4_code/06_manifest/
项目重启_v0.4_BlenderOCS/06_v0.4_code/10_validation/
项目重启_v0.4_BlenderOCS/v0.4_results/
项目重启_v0.4_BlenderOCS/v0.4_results/00_validation/

创建或写入文件：
1. 06_v0.4_code/00_config/environment.md
   - 记录 Blender 版本、Python 路径、conda 环境、关键包版本、GPU/CUDA 信息；无法获取则写“未获取”。

2. 06_v0.4_code/00_config/config_v0_4.py
   - 从历史 config.py 提取路径结构。
   - yaw 必须为 0..355 step 5，共 72 个，不含 360。
   - pitch 必须为 -90..90 step 5，共 37 个。
   - resolution = 256。
   - output root = v0.4_results。
   - BRDF_MODEL = "phong_like_provisional_baseline"。
   - 区分 EPS_NOL_NOV = 1e-6 与 DEPTH_EPSILON_M_INITIAL = 1e-3。

3. 06_v0.4_code/00_config/materials_v0_4.py
   - 复制历史 materials.py 的 Legacy Phong 参数作为 B0。
   - 字段必须标注 project provisional params。
   - 不得写成书中材料参数。
   - GGX 只保留为 mismatch_control 参数字典。

4. 06_v0.4_code/01_geometry/geometry_loader.py
   - 迁移历史 geometry.py 中 STL 加载、Scene 转 Mesh、抽稀兼容逻辑。
   - 暂不启动任何渲染。

5. 06_v0.4_code/01_geometry/attitude_grid.py
   - 生成 yaw72 × pitch37 网格。
   - 提供 record_id 构造函数。
   - 明确绘图 seam 的 360 复制只用于画图，不进入训练/manifest 姿态网格。

6. v0.4_results/00_validation/phase0_entry_notes.md
   - 记录本次只创建骨架和环境记录。
   - 记录未启动 Blender、未生成数据、未训练。
   - 记录下一步才是单姿态 smoke test。

输出报告写入：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/08_1C-E04_Phase0代码骨架与环境记录_Claude输出.md

红线：
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库。
- 不把 B0 写成书中五参数冯。
- 不使用 latest-run 自动发现。
- 若文件无法一次性写入，按 Part 1/2/3 分段写入直到完整。
```

## 7. 最终判定

```text
1C-E03 Claude 输出：通过为执行入口核对。
关键修正：当前 BRDF 字段统一为 phong_like_provisional_baseline。
知识库重整不阻塞 Phase 0。
下一步：按 1C-E04 创建代码骨架与环境记录，不启动渲染或训练。
```

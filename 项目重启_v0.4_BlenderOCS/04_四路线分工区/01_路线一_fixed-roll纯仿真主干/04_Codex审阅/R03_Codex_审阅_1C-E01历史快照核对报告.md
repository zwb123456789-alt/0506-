# R03 Codex：审阅 1C-E01 历史快照代码真实内容与依赖核对报告

最后更新：2026-06-22

## 1. 文件性质

本文是对 Claude 执行输出的 Codex 审阅记录。对应 Claude 输出为：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/04_1C-E01_历史快照代码真实内容与依赖核对报告_Claude执行输出.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/04_1C-E01_报告补充部分.md
```

本次审阅只判断 Claude 核对报告是否可吸收，不进行代码创建、代码迁移、冻结文件小修或阶段放行。

## 2. 总体结论

1C-E01 本轮 Claude 输出基本通过，可作为路线一 C 历史快照真实内容核对报告吸收。

两份 Claude 输出应合并阅读：主报告覆盖 A-C，补充部分覆盖 D-H。补充部分不是新的独立任务，而是同一报告的后半段。

本轮不需要让 Claude 重新执行 1C-E01。原因如下：

```text
1. Claude 本轮基本遵守“只核对、不设计、不放行”的边界；
2. 关键代码事实经 Codex 抽样核验成立；
3. 继续重跑同一任务收益较低，反而会消耗上下文；
4. 下一步应由 Codex 先完成设计与裁决，再给 Claude 新的短执行提示词。
```

## 3. Codex 抽样核验结果

Codex 抽样核验了历史快照中的关键文件：

```text
03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/config.py
03_项目说明与规划材料/05_参考材料/01_关键代码快照/01_code/materials.py
03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/render_geometry_passes.py
03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/brdf_postprocess.py
```

抽样结论：

| Claude 核对项 | Codex 抽样判断 |
|---|---|
| `NUM_YAW = 73` | 成立；包含 0/360 重复风险，路线一 C 不应直接沿用 |
| `BRDF_MODEL = "ggx"` | 成立；与路线一 C Phong-like 主锚点冲突 |
| 旧输出目录 `结果/模块A_重构` | 成立；不符合当前 v0.4 输出根口径 |
| Legacy Phong 公式存在 | 成立；`f_r = rho_d/pi + rho_s * cos_alpha^n` |
| GGX 参数库存在 | 成立；但只能作为 mismatch/control 分支参考 |
| camera-view geometry pass 已有 Normal/Depth/IndexOB/Backfacing | 成立 |
| Position/WorldCoord pass 缺失 | 成立 |
| sun-view depth pass 缺失 | 成立 |
| `brdf_postprocess.py` 只计算 `f_r * NoL` | 成立；缺少 `V_sun_macro` |
| gamma 2.2 PNG 编码 | 成立；后续应改为受控的 log1p 图像编码方案 |
| face-center `ocs_core.py` 禁止并入主链 | 成立；只保留历史参考 |

注意：`config.py` 中 `NUM_YAW` / `NUM_PITCH` 附近注释存在疑似旧注释残留，后续不要引用该注释判断步长；应由 Codex 正式设计重新定义 yaw/pitch 网格。

## 4. 可吸收内容

以下内容可吸收到路线一 C 后续实现规划：

- 历史快照实际存在 11 个 Python 代码文件，`main_run.py` 和 `render_batch.py` 不存在。
- `geometry.py` 的 STL 加载、单位缩放和 `R = Rz @ Ry @ Rx` 旋转顺序可作为高优先级复用对象。
- `materials.py` 的材料参数结构和 Legacy Phong / GGX 双参数库可作为参考，但参数来源需重新对齐书籍知识库。
- `render_geometry_passes.py` 的 camera-view geometry pass 框架可作为升级对象。
- `brdf_postprocess.py` 的 EXR 读取、像素级 BRDF 后处理、per-part OCS 积分思路可作为改造对象。
- `run_multi_geom.py` 的多几何循环、相位角计算和汇总结构可作为参考，但主链必须从 face-center 改为 Blender geometry pass + Python BRDF 后处理。
- `inv_common.py` 和 `train_*.py` 的 split、特征提取、误差度量和基础训练输出可作为后续反演阶段参考，但当前不进入训练。

## 5. 不可吸收或禁止直接迁移内容

以下内容不得直接进入路线一 C 主链：

- `ocs_core.py` face-center OCS 主链。
- `NUM_YAW = 73` 的重复 yaw 网格。
- 默认 `BRDF_MODEL = "ggx"`。
- 旧输出路径 `结果/模块A_重构`。
- 不含 `V_sun_macro` 的 OCS / image 公式。
- gamma 2.2 PNG 作为正式图像编码。
- latest-run 自动发现。
- 旧 manifest / CSV schema。
- 将历史快照写成当前正式可运行入口。

## 6. 当前待 Codex / 作者裁决事项

进入实现前仍需确认：

1. 是否创建正式代码区：

```text
项目重启_v0.4_BlenderOCS/06_v0.4_code/
```

2. 输出根目录采用哪一个：

```text
v0.4_results/      # 与 14 号当前口径一致
07_v0.4_results/   # 与顶层编号结构更一致，但需要受控小修 14 号
```

3. 是否同意执行层临时覆盖 13/14 中 GGX 主模型字段：

```text
Phong-like / 五参数冯 = 主锚点
GGX / Cook-Torrance = mismatch / control 分支
```

4. Legacy Phong 是否等同于书中五参数冯 / Phong-like BRDF。
5. `materials.py` 中三个部件的参数是否要替换为书籍知识库参数。
6. 是否先由 Codex 读取书籍知识库相关文件，给出 BRDF 与材料参数的正式裁决。

## 7. 是否需要交给 Claude 重新执行

不需要重新执行 1C-E01。

下一次若交给 Claude，应是新的短执行任务，而不是重跑历史快照核对。候选方向为：

```text
1C-E02：仅核对书籍知识库中五参数冯 / Phong-like BRDF 公式与材料参数出处；
或
1C-E03：在作者确认代码区后，按 Codex 指定清单复制/改造最小代码骨架。
```

其中 1C-E02 更稳妥，因为当前最大未决点是 Phong-like / Legacy Phong 等价性与书中材料参数对齐。1C-E03 必须等作者确认代码区、输出区和 BRDF 执行口径后才能启动。

## 8. 下一步建议

Codex 下一步不应让 Claude 设计 smoke test，也不应让 Claude 自行创建代码区。

建议顺序：

```text
Step A：作者确认是否先走 1C-E02 书籍知识库核对；
Step B：Codex 给出 BRDF / 材料参数裁决；
Step C：作者确认 06_v0.4_code/ 与输出根目录；
Step D：Codex 生成受控短提示词，Claude 执行代码骨架创建或最小 smoke test 实现。
```

## 9. 最终判定

```text
Claude 1C-E01：审阅通过，作为历史快照真实内容核对材料吸收；
无需重跑 1C-E01；
不得据此直接进入代码迁移或全量生成；
下一条 Claude 提示词必须继续采用短提示词、执行型任务和分段写入规则。
```

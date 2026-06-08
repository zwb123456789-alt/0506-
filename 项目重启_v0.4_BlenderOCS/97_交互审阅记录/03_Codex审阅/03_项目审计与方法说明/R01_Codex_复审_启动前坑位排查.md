# Codex 复审意见：启动前坑位排查

最后更新：2026-06-08

复审对象：

```text
03_全项目排查/02_全项目坑位排查报告_Claude.md
03_全项目排查/03_旧结果依赖图_Claude.md
03_全项目排查/04_旧结果隔离与可复用清单_Claude.md
```

## 1. 总体判断

Claude 的三份文件可以作为 v0.4 启动前审计底稿，覆盖了主要大坑：OCS/image 采样口径不统一、sun-side visibility 未冻结、旧 OCS 结果需要隔离、补充实验依赖旧 OCS、文件夹隔离风险。

作者口径修正：v0.4 是整体重启，旧结果一律不进入 v0.4 主结果，不再讨论“旧结果是否可复用”。旧结果只允许作为历史证据、分支原因、诊断材料。当前审计的重点不是从旧结果里挑可复用项，而是利用旧项目记录找到与本次 OCS 采样问题类似的“方法口径不一致坑”。

但当前版本不能直接作为“启动闸门已完成”的最终记录。原因是：

1. 个别证据解释有误，尤其是 `subface_adaptive_comparison.csv` 的 ratio 字段。
2. 对 image-only、旧 PNG、旧 EXR、旧代码的“可复用”判断偏宽；在当前作者口径下，应改为“旧结果全部封存，代码/公式/结构可作为重建参考”。
3. `pixel_area` / `NoV` / 投影面积语义必须上升为方法冻结核心问题。
4. P0/P1 统计口径不一致，需要修正为可执行清单。

结论：可以进入“方法冻结提示词准备”，但方法冻结前必须把下列复审意见写入下一步 Claude 提示词。

## 2. 主要问题

| 编号 | 严重度 | 对应位置 | 问题 | Codex 判断 | 修正建议 |
|---|---|---|---|---|---|
| CR-001 | P0 | `02_全项目坑位排查报告_Claude.md` 中 `PIT-A-002` | 把 `ratio_ad_Bdiff=20.68` 写成 adaptive subface 是 face-center 的 20.68 倍，证据解释错误。CSV 中该姿态太阳能板 `ratio_ad_fc=1.019`，20.68 是 adaptive 与 Blender-diff OCS 的比值。 | 不能用该证据直接证明“face-center 漏掉窄镜面峰 20 倍”。它更准确地证明：旧 face-center、adaptive subface、Blender pixel OCS 三者定义/面积/可见性口径不一致。 | 改写为“采样、投影面积、可见性定义未统一导致三端差异”，不要把根因简化成 face-center 单独漏峰。 |
| CR-002 | P0 | `03_旧结果依赖图_Claude.md` 和 `04_旧结果隔离与可复用清单_Claude.md` 中 image-only / 旧 PNG | 多处写“image-only 可审计后复用”。这与作者最新口径“旧结果全部不复用，避免部分重来导致方法不一致”冲突。 | 旧 image-only、旧 fusion、旧 OCS-only、旧补充实验数值一律封存。它们只能帮助定位历史坑和设计新链路，不能进入 v0.4 主结果。 | 将“审计后复用”统一改为“历史证据/重跑参考”。v0.4 主表和补充实验全部使用新 run、全局 split、source-data index。 |
| CR-003 | P0 | `PIT-C-003`、`PIT-UNK-003` | `pixel_area` 被列为 P1/否复审，但它决定 OCS 积分定义。 | 这是方法冻结核心问题。正交投影下若按屏幕像素积分，`dA_surface = dA_projected / NoV`，与公式中的 `NoV` 抵消，得到 `Σ pixel_area_projected * fr * NoL`。但必须明确 `pixel_area` 是投影像素面积，不是表面面积；边缘像素是否做 fractional coverage 也要冻结。 | 方法冻结文件必须单独写一节：连续公式、像素离散公式、`NoV` 抵消条件、`NoV≈0` 处理、边缘像素面积处理、单位与 per-part 累计规则。 |
| CR-004 | P1 | `04_旧结果隔离与可复用清单_Claude.md` 代码框架 | 多个旧脚本被标成“直接复用”，包括 `render_geometry_passes.py`、`inv_ocs.py`、`train_mlp.py`、`train_fusion.py`。 | “直接复用”过宽。v0.4 应是“参考旧方法和结构，重建新链路”。尤其反演脚本必须禁止 latest-run 自动读取旧路径。 | 把旧代码用途改为：公式/材料/坐标定义可参考，模型结构可参考，数据入口和 manifest 链路必须重写或严格审计后迁移，诊断脚本仅历史对照。 |
| CR-005 | P1 | `04_旧结果隔离与可复用清单_Claude.md` 历史对比 | 写“旧 OCS-only 5.91° 与新 OCS-only 对比，说明采样口径改善对反演性能的影响”。 | 容易被写成“改进性能”的故事。v0.4 的核心不是证明性能提升，而是修正观测定义和统一前向模型。 | 旧 5.91° 只能作为“旧方法分支诊断/历史记录”，不建议作为 v0.4 主文性能对比基线。若使用，必须放补充材料并声明不是 apples-to-apples improvement。 |
| CR-006 | P1 | `02_全项目坑位排查报告_Claude.md` 统计表 | P0/P1 统计口径混乱：P0 正文列 5 个，注释又把 `PIT-UNK-001/002` 计入 P0；P1 写“10+3”，又说未闭环 3 个未计入。 | 会影响后续闸门判断。启动前清单需要明确“阻断项、方法冻结项、重跑项、写作项”。 | 重新输出一张闸门表：`必须在方法冻结前解决`、`必须在代码前解决`、`必须在重跑前解决`、`论文阶段解决`。 |
| CR-007 | P1 | `03_旧结果依赖图_Claude.md` split/seed | 多处写“旧 seed”，但没有给具体 seed 和 split 文件。 | 依赖图仍不够可复现。不能把未知 seed 当成已记录信息。 | 全部改为 `unknown / not located`，并在 v0.4 重跑规范中要求全局 split 文件和 `source_data.json`。 |
| CR-008 | P2 | `Related Work 直接复用` | Related Work 虽不依赖旧实验数值，但 v0.4 方法定位变化后，比较对象和贡献表述可能需要调整。 | 可保留结构，不应写“直接复用”。 | 改为“结构可复用，内容需按统一前向模型重审”。 |

## 3. 对 Claude 三份文件的逐项评价

| 文件 | 评价 | 是否通过 |
|---|---|---|
| `02_全项目坑位排查报告_Claude.md` | 覆盖面够，P0 主线抓到了；但 `PIT-A-002` 证据解释错误，P0/P1 统计不清，`pixel_area` 优先级偏低。 | 条件通过 |
| `03_旧结果依赖图_Claude.md` | 依赖链结构清楚，主实验和补充实验覆盖较完整；但 image-only 复用口径偏宽，split/seed 未知项不应写成旧 seed。 | 条件通过 |
| `04_旧结果隔离与可复用清单_Claude.md` | 禁止复用清单总体正确；但“可复用”部分太乐观，旧 PNG、旧 EXR、旧代码都应改为条件复用或重新生成。 | 需收紧 |

## 4. 方法冻结前必须带入的决策项

下一步 Claude 方法冻结提示词必须明确要求回答：

1. Blender 输出哪些 geometry pass：normal、depth、part ID、camera-visible mask、backfacing、是否输出 sun-visible mask。
2. sun-side visibility / self-shadow 如何实现：Blender shadow ray、Python ray-cast，或明确限定为 viewer-side visibility only。
3. OCS 连续公式和像素离散公式：`NoV` 是否抵消、`pixel_area` 是投影面积还是表面面积、边缘像素如何处理。
4. BRDF 主模型：v0.4 主线采用 GGX/Cook-Torrance；LegacyPhong 仅作为可选历史/附录对照。
5. clean image 与训练 PNG 的关系：线性图像、log1p、8-bit PNG、tone mapping 是否固定。
6. 输出 manifest 字段：每条记录必须包含 OCS source、image source、split id、seed、feature mode、run id、method version。
7. 重跑口径：v0.4 主结果原则上全部重跑；旧结果只用于历史诊断，不进入主结果表。

## 4.1 需要新增的专项排查方向

下一轮排查不要再围绕“旧结果能不能复用”，而要围绕“还有没有类似 OCS 采样问题的隐藏方法坑”。至少检查：

| 方向 | 需要排查的问题 |
|---|---|
| 采样口径 | OCS、image、fusion、补充实验是否还有不同采样源或不同可见性定义 |
| 遮挡口径 | camera visibility、sun visibility、self-shadow、backfacing 是否在不同模块里含义不同 |
| 面积口径 | face area、projected pixel area、surface area、edge fractional coverage 是否混用 |
| 坐标口径 | Blender、Python、反演标签的 yaw/pitch/roll、世界坐标法线、太阳/观测方向是否完全一致 |
| 材料口径 | GGX 参数、F0/base_color/roughness、LegacyPhong 对照是否在 OCS 和 image 中一致 |
| 图像响应 | 线性 radiance、PNG、log1p、8-bit tone mapping、训练增强是否改变物理含义 |
| 数据划分 | split、seed、姿态网格、phase 定义是否在主实验和补充实验中一致 |
| 路径和版本 | 是否存在 latest-run、硬编码旧路径、run_id/source_data 缺失导致误读 |

## 5. 下一步建议

建议下一步不是直接写代码，也不是判断旧结果复用，而是先让 Claude 做“相似方法坑专项排查”。之后再生成：

```text
04_BlenderOCS方法重建/03_v0.4前向模型冻结规范_Claude.md
04_BlenderOCS方法重建/04_v0.4数据与manifest字段规范_Claude.md
```

提示词中必须包含本复审文件的 CR-001 到 CR-008，尤其是 `pixel_area / NoV / sun visibility` 三个方法核心项。

Codex 判断：启动前审计第一轮完成，但还没有完全闭环。可以进入“方法冻结文件生成”阶段；不能进入代码和实验重跑阶段。

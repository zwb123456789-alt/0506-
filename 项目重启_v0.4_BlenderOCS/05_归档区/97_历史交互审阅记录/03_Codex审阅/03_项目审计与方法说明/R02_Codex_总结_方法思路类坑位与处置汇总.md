# 方法/思路类坑位与处置汇总（Codex 口径）

最后更新：2026-06-08

## 1. 总口径

v0.4 是整体重启。旧结果一律不进入 v0.4 主结果，不再讨论“哪些旧结果可以复用”。

旧材料只用于三件事：

1. 作为历史证据，说明为什么 v0.3 封存。
2. 作为诊断材料，帮助发现类似 OCS 采样问题的隐藏坑。
3. 作为方法/代码结构参考，但所有新结果必须在 v0.4 链路下重新生成。

因此当前排查重点不是“复用旧结果”，而是：

```text
找出方法、思路、定义、数据链路中可能导致第二次整体重启的坑。
```

## 2. 已确认的根因型大坑

| ID | 类型 | 坑位 | 为什么严重 | 当前处置 |
|---|---|---|---|---|
| METH-001 | 采样口径 | OCS 使用旧模块 A face-level / face-center，图像使用 Blender pixel-level geometry pass | 两个模态不是同一前向模型，导致 OCS-only、fusion、补充实验的物理比较基础不稳 | v0.4 采用统一前向模型：Blender 负责几何采样，Python 显式公式负责 BRDF/OCS/image |
| METH-002 | 遮挡口径 | camera visibility、sun-side visibility、self-shadow 定义未闭合 | 如果论文写“含自遮挡/阴影”，但 OCS 端和图像端遮挡逻辑不同，会再次形成方法口径不一致 | 方法冻结前必须决定并实现 sun visibility；若不实现，论文必须明确限定 |
| METH-003 | 面积口径 | `pixel_area`、`NoV`、surface area、projected area 语义可能混用 | OCS 积分数值由面积定义决定，特别影响斜面、边缘像素和大倾角姿态 | 方法冻结必须写清连续公式、像素离散公式、`NoV` 抵消条件、边缘像素处理 |
| METH-004 | 材料口径 | Blender 内置材质、Python GGX、LegacyPhong 可能混用 | 如果 OCS 和 image 调用不同材料模型，fusion 结果会混入模型差异 | v0.4 主线固定 Python 显式 GGX/Cook-Torrance；Blender 不作为最终亮度黑箱 |

## 3. 需要专项排查的相似坑

| 类别 | 可能的坑 | 风险 | 处置方式 |
|---|---|---|---|
| 坐标系统 | Blender 与 Python 的 yaw/pitch/roll、法线方向、太阳方向、观测方向定义不一致 | 结果看似可训练，但物理解释错位 | 写统一坐标规范；每个 geometry pass 输出坐标系说明；做单姿态 sanity check |
| 姿态标签 | 训练标签、渲染姿态、OCS 姿态扫描不是同一组 yaw/pitch/grid | 反演误差和图表不可比 | v0.4 建立全局 pose manifest；所有实验从同一 manifest 取标签 |
| phase 定义 | phase63、phase120、yaw/pitch 网格、观测几何含义混乱 | 跨 phase 泛化和主实验不在同一问题定义下 | 每个 phase 写 sun/view vector、grid、roll、ortho scale、run id |
| 图像响应 | 线性辐亮度、8-bit PNG、log1p、tone mapping、noise 注入位置不统一 | image-only 与 OCS/fusion 对比不公平 | 冻结 clean linear image 与训练输入转换；退化实验写清作用域 |
| 数据划分 | 主实验、补充实验、image-only、fusion 使用不同 split/seed | 数值不能横向比较 | v0.4 使用全局 split 文件；每个 summary 记录 seed 和 split id |
| 路径读取 | 脚本自动找 latest run 或硬编码旧路径 | 新旧结果混读，难以及时发现 | 禁止 latest-run；所有脚本显式传入 manifest；输出 `config_used.json` |
| source data | 图表 source path 分散或缺失 | 论文图表无法追溯，旧新数据可能混放 | 每张图必须有 source CSV/JSON 和 source-data index |
| 补充实验 | 12b/12c/12f/12g 复用旧模型或旧预处理参数 | 主链路重跑但补充实验仍旧口径 | 所有补充实验从 v0.4 manifest 重新跑；旧结果只做历史记录 |
| 小项目 | “最亮姿态/星等范围”等小项目继续读旧 OCS | 小项目与主论文物理定义不同步 | 小项目增加 OCS source version；v0.4 后重新计算 |
| 写作口径 | 把 synthetic benchmark 写成真实观测验证，把 Blender-derived OCS 写成真实值 | 审稿风险和主张过强 | 统一写成 observation-consistent synthetic forward model；明确 no real telescope validation |

## 4. 大坑、小坑、未知坑分级

| 级别 | 定义 | 例子 | 处理 |
|---|---|---|---|
| 大坑 | 会改变 OCS/image/fusion 主结果或导致全链路重跑 | 采样口径不统一、遮挡定义不闭合、BRDF 模型混用、面积公式不清 | 方法冻结前必须解决 |
| 小坑 | 不一定改变主结果，但会影响复现、记录、图表、补充实验一致性 | source path 缺失、seed 未记录、路径硬编码、图表 caption 指向旧数据 | 代码/重跑规范前解决 |
| 未知坑 | 当前没有证据证明有问题，但一旦有问题会影响方法可信度 | tone mapping 是否改变亮度物理含义、edge pixel area、phase 网格和 split 是否全局一致 | 专项审计，未确认前不得写成已解决 |

## 5. 当前处置原则

1. 旧结果全部封存，不进入 v0.4 主结果。
2. 旧代码只作为参考，不直接继承旧数据入口。
3. 方法冻结先于代码，代码先于实验，实验先于论文。
4. 所有定义必须写入 manifest 或方法规范，不靠口头记忆。
5. 每个新 run 必须有 `config_used.json`、`source_data.json`、`summary.md`。
6. 每个图表必须能追溯到 v0.4 source data。
7. 如果某项定义未冻结，不能启动依赖它的重跑。

## 6. 下一步

让 Claude 做一次专项排查，输出：

```text
03_全项目排查/07_相似方法坑专项排查报告_Claude.md
04_BlenderOCS方法重建/03_v0.4前向模型冻结问题清单_Claude.md
```

Codex 再审阅这两份文件后，才能进入正式方法冻结规范。

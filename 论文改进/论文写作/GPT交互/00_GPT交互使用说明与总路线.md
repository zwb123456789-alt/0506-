# GPT 论文初稿逐步指导：交互使用说明与总路线

本文档用于指导 GPT 分阶段生成论文初稿。它与 `论文初稿_Claude逐步指导` 同级使用，目标是让 GPT 和 Claude 在同一证据边界下分别产出版本，最后由作者和 Codex 对比选择更优版本。

## 1. 使用原则

GPT 的角色不是一次性写完整论文，而是作为交互式论文写作助手：

1. 每次只完成一个阶段。
2. 每个阶段先确认任务边界，再输出结构化结果。
3. 不主动扩展实验，不创造新数据，不创造真实观测验证。
4. 若信息不足，用 `[需要作者确认：...]` 标记，而不是自行补齐。
5. 所有英文论文文本必须配中文解释，方便作者判断是否符合项目定位。
6. 每一步输出末尾必须给出“下一轮可以怎么改”的 3-5 条建议。

## 2. 与 Claude 指导的区别

Claude 版本更适合一次性交给模型执行，要求它按文件完整输出。

GPT 版本更适合多轮交互：

- 允许 GPT 先给 2-3 种写法路线，再让作者选择。
- 要求 GPT 显式列出“强叙事版本”和“保守审稿安全版本”的区别。
- 要求 GPT 在每个阶段输出一个自我审稿 checklist。
- 要求 GPT 对每个关键 claim 标注风险等级。

## 3. 投稿档次与定位

目标档次：

- 主攻：SCI 二区
- 写作标准：按 SCI 一区边缘标准组织
- 不按顶刊/强一区夸大贡献

推荐期刊方向：

- Acta Astronautica
- Advances in Space Research
- Optics Express
- Remote Sensing

论文定位：

> A physically consistent simulation and controlled inversion study that reveals when OCS and photometric images provide complementary attitude constraints under ideal and degraded observation conditions.

中文定位：

> 基于统一 BRDF 与自遮挡建模的 OCS-光度图像姿态反演基准研究，重点分析理想图像上限、图像退化脆弱性与 OCS 鲁棒互补价值。

## 4. GPT 必须遵守的叙事边界

禁止写法：

- OCS 是主力，图像只是辅助。
- Fusion 一定是最优方法。
- ResNet clean 结果代表真实望远镜观测性能。
- 本文方法已经真实光学数据验证。
- 本文达到 state-of-the-art 或首次解决某问题。
- 直接把 ISAR 数据纳入本文主线。

推荐写法：

- Clean synthetic images provide an optimistic upper bound for image-based inversion.
- OCS provides robust, interpretable, low-cost, and multi-geometry photometric constraints.
- Fusion provides conditional complementarity rather than universal superiority.
- The study is simulation-focused and controlled, with no real optical telescope validation.

## 5. 当前可用证据

物理链条：

- 真实卫星 STL 几何
- 非均匀材料分区
- GGX/Cook-Torrance BRDF
- 解析射线自遮挡
- 多观测几何 OCS 扫描
- 光度图像渲染
- yaw-pitch 姿态反演，fixed roll
- OCS-only / image-only / late fusion / feature fusion

核心数值：

- ResNet image-only clean：1.69 ± 0.07 deg, Hit@5 = 97.6%
- ResNet + concat5 per_part_log：1.47 ± 0.07 deg
- worst-case：9.9 deg -> 6.6 deg
- 1% Gaussian image noise：ResNet 退化到 85.85 deg, Hit@5 = 2.2%
- OCS MLP per_part_log：5.91 deg，实用 OCS-only 结果
- OCS MLP all_raw 45D：3.98 ± 0.60 deg, Hit@5 = 90.7%，semi-oracle 上界
- TinyCNN image-only：12.38 ± 0.74 deg, Hit@5 = 26.1%，轻量 baseline
- Early feature fusion per_part_log：4.10 ± 0.77 deg, Hit@5 = 87.3%
- OCS-CNN 误差相关性 r = 0.003
- OCS-noise fusion gain 从 +1.97 deg 增至 +6.29 deg，随 OCS noise 0% 到 20% 增加

重要边界：

- 无真实光学望远镜图像验证
- clean rendered images 是 idealized photometric imagery
- atmosphere、detector response、PSF、earthshine、background contamination 未显式建模
- 当前任务估计 yaw-pitch，roll 固定
- 图像主分支主要基于 phase63
- 材料参数为 nominal

## 6. 阶段路线

### Step 1：论文定位、标题、摘要骨架、贡献点

输出：

- 3 种论文叙事路线
- 5 个标题
- 核心科学问题
- 一句话论证链
- 摘要骨架
- 4 条贡献点
- claim-evidence-risk map

对应文件：

- `01_Step1_GPT交互提示词.md`

### Step 2：Introduction

输出：

- 漏斗结构
- 段落 topic sentence
- 两个版本：保守审稿安全版 / 更有冲击力版
- claim-risk checklist

### Step 3：Related Work + Table 1

输出：

- 四类文献组织逻辑
- Table 1 方案对比表
- 与本文差异化表达

### Step 4：Method

输出：

- 统一框架方法段落
- 各模块可复现描述
- 避免代码说明式写法

### Step 5：Results

输出：

- evidence ladder
- 主图/主表对应叙事
- clean upper bound、degradation、OCS robustness、conditional fusion 的结果段落

### Step 6：Discussion / Limitations / Conclusion

输出：

- 审稿人风险回应
- 真实观测边界
- 总结段落

## 7. GPT 每步固定输出格式

每次都要求 GPT 用以下结构：

```text
1. 本轮目标复述
2. 可选叙事路线
3. 推荐版本
4. 英文正文或骨架
5. 中文解释
6. Claim-Evidence-Risk Map
7. Self-review Checklist
8. 需要作者确认的问题
9. 下一轮修改建议
```


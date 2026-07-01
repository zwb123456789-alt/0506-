# R91 Codex 文献检索：1C-B1 六方向方法约束与 PDF 入库

最后更新：2026-06-29  
执行端：Codex  
性质：头B `B-1` 文献检索与文献管理记录；不放行新训练、模型改正、新数据生成或论文正文正式改写。

## 0. 裁决

```text
1C-B1 文献检索：DONE
PDF 入库：DONE，项目内 papers/ 可读取 PDF 共 30 个
BibTeX：DONE，02_references.bib 已增量追加缺失关键条目
方法总结 B-2：NOT STARTED
单帧 OCS vs 光变曲线正式实验设计 B-3：NOT RELEASED
模型改正候选 B-4：NOT RELEASED
新训练 / 新数据 / split / 模型 / 超参 / seed 修改：NOT RELEASED
```

本轮完成 R05/85 要求的六方向文献检索，并把能获取的 PDF 放入项目内文献入口：

```text
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/papers/
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/05_B1文献检索PDF状态与待下载链接_20260629.md
```

## 1. 检索覆盖

按 85 号文件，B-1 覆盖六个方向：

```text
1. 光变曲线 / 光度反演
2. SSA 空间目标光学特征化
3. 图像 + 光度 / 多模态融合方法
4. sim-to-real 与 synthetic benchmark 可信度
5. 姿态估计可观测性 / 可辨识性
6. 现代姿态反演 / 融合 / 序列 / 不确定性架构
```

检索源包括 CrossRef、arXiv、公开网页、项目既有文献库和旧路线样文 PDF。arXiv MCP 多次限流或超时，已用 DOI/CrossRef、项目既有 PDF 与开放网页下载补足。

## 2. 六方向结论

### 2.1 光变曲线 / 光度反演

关键文献：

```text
Kaasalainen 2001 I/II, Icarus, DOI 10.1006/icar.2001.6673 / 6674
Wetterer and Jah 2009, JGCD, DOI 10.2514/1.44254
Clark et al. 2022, ASR, DOI 10.1016/j.asr.2022.08.068
Wang et al. 2024, ASR, DOI 10.1016/j.asr.2024.04.005
Burton et al. 2024, ASR, DOI 10.1016/j.asr.2024.09.008
Kumar et al. 2025, Acta Astronautica, DOI 10.1016/j.actaastro.2025.04.018
Tang et al. 2025, A&A
```

约束：

```text
真实光度姿态反演主流信息形态是多时刻/多几何 light curve，而不是单帧多维标量 OCS。
当前 C2/C3 的单帧 OCS negative result 不能外推为“光度通道无姿态信息”。
B-2 方法总结必须把“单帧 OCS”和“光变曲线序列”拆开讨论。
```

### 2.2 SSA 空间目标光学特征化

关键文献：

```text
Lu 2024, Universe, Starlink BRDF photometric modeling
Fankhauser et al. 2023, AJ, Satellite Optical Brightness
Clark et al. 2022, ASR
Groves et al. 2025, self-supervised SSA light curves
Aerospace 2026 review, photometric characterization
```

约束：

```text
SSA 文献常把光度用于表征、状态变化、异常或联合属性估计。
精确定姿通常需要已知/参数化形状、BRDF、姿态动力学或多历元光变约束。
路线一 C 的 model-known 合成 benchmark 可作为受控下界，不得写成真实 GEO 监督定姿系统。
```

### 2.3 图像 + 光度 / 多模态融合

关键文献：

```text
Rondao et al. 2022, ChiNet, DOI 10.1109/TAES.2022.3193085
Liu et al. 2024, Remote Sensing, visual-inertial tightly coupled fusion
Pasqualetto Cassinis et al. 2021, Acta Astronautica
```

约束：

```text
当前 early concat + single linear head 只能支持“该朴素融合方式下无自动增益”。
不能写成 OCS/image 已被证明普适不互补。
B-2 至少应把 early/mid/late fusion、cross-attention、decision-level fusion 和 modality dominance 作为候选维度列出。
```

### 2.4 sim-to-real 与 synthetic benchmark 可信度

关键文献：

```text
Park et al. 2022, SPEED+, DOI 10.1109/AERO53065.2022.9843439
Park and D'Amico 2024, ASR, DOI 10.1016/j.asr.2023.03.036
Bechini et al. 2023, Acta Astronautica, DOI 10.1016/j.actaastro.2023.01.012
Dickinson 2025, RIT PhD
```

约束：

```text
合成图像/光度 benchmark 必须显式承认 domain gap。
v0.4 可以讲 controlled benchmark 和 inverse-crime 防护，但不能声称可迁移真实望远镜/GEO。
若后续想增强可信度，优先方向是噪声/退化/域随机化/真实光度锚点，而不是直接扩大 claim。
```

### 2.5 可观测性 / 可辨识性

关键文献：

```text
Gerwe and Idell 2003, JOSA A, DOI 10.1364/JOSAA.20.000797
Kaasalainen 2001 I/II
Fankhauser et al. 2023 brightness model
```

约束：

```text
“yaw-block 外推失败”可以被组织为 protocol-defined extrapolation gap。
若要提升为更正式可观测性论证，后续应引入 signature distance、Fisher/CRLB 或混淆簇分析。
当前 E45A/B/C/D 结果还不能写成 yaw 物理不可观测。
```

### 2.6 现代姿态反演 / 序列 / 不确定性架构

关键文献：

```text
Rondao et al. 2022 ChiNet
Tang et al. 2025 A&A
Park et al. 2022 SPEED+
Guo et al. 2017, calibration of modern neural networks
Angelopoulos and Bates 2023, conformal prediction
```

约束：

```text
exact-bin yaw=0% 只能是 sentinel，不是已实现拒识。
若要写 trustworthy / confidence consistency，必须另行实现校准、ECE、conformal prediction、prediction set 或 posterior-like agreement。
分类 exact-bin 应在 B-2 中与 circular regression / von-Mises / regression+classification 双头并列为候选，而不能本轮直接改。
```

## 3. PDF 与引用管理

本轮处理：

```text
1. 新建项目内 papers/ 目录。
2. 从旧外部文献库复制已有 PDF。
3. 从旧路线样文区复制 Clark 2022、Bechini 2023、Pasqualetto Cassinis 2021。
4. 自动下载开放 PDF：Tang 2025、ESA SDC8、AMOS 2019/2024、SPEED+、Park 2024、ChiNet、Guo 2017、Angelopoulos 2023 等。
5. 用 pypdf 页数抽检 30 个 PDF，全部可读取。
6. 更新 `02_references.bib`，增量追加 B-1 缺失关键条目。
```

无法自动下载但应手动补齐的关键文献已列入：

```text
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/05_B1文献检索PDF状态与待下载链接_20260629.md
```

最高优先级为：

```text
Kaasalainen 2001 I/II
Wetterer and Jah 2009
Linares et al. 2014 JGCD
Gerwe and Idell 2003 JOSA A
Piergentili et al. 2017 TAES
```

## 4. 对头B后续的输入

B-2 方法总结应从以下问题开始，而不是直接设计训练：

```text
Q1. 当前“单帧 OCS”在文献谱系中是什么位置？
Q2. 光变曲线序列是否应成为后续信息源升级主线？
Q3. 当前 early fusion negative result 只否定了哪一种 fusion？
Q4. 若做模型改正，先改判据/损失、fusion 结构、还是信息源？
Q5. 哪些改动能保持 R04 负结果链可复现，哪些必须新阶段门？
Q6. 置信一致性要达到什么最低实现，才能从 sentinel 变成可写机制？
```

建议 B-2 输出为“方法总结与阶段门候选”，不是代码任务单。

## 5. 红线

```text
不得据 B-1 文献检索启动新训练。
不得据文献把当前结果改写成真实 GEO / 三轴 / 暗室验证。
不得把 light-curve inversion 文献直接等同于当前单帧 OCS 结果。
不得把 modern fusion 文献当作当前 joint negative result 的反证。
不得把 calibration/conformal 文献包装成当前系统已有拒识能力。
不得原地修改 R04 代码/数据/成果链。
```

## 6. 下一步

```text
建议进入 1C-B2：方法总结与阶段门候选。
输入：
  - 本 R91
  - 85 号文献补课材料
  - 84 号暂停点复盘
  - R90 头A桥接材料
  - 文献区 05_B1文献检索PDF状态与待下载链接_20260629.md

B-2 仍不启动训练、不写正文正式段落、不生成新数据。
```

CLAUDE.md 本轮不改。建议等 B-2 或头A/头B合并审阅完成后，再受控同步最新下一步。

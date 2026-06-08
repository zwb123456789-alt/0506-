# 阶段5 Codex审阅：STL最亮部件实验方案

审阅时间：2026-06-07

审阅对象：

- `Claude输出/阶段5_STL最亮部件实验方案.md`

## 审阅结论

**暂不通过执行，需要修改后再进入阶段6。**

阶段5的总体框架是有价值的：

- 目标拆分为最亮部件、最亮姿态/相位角、部件贡献关系，方向正确；
- 粗筛→roll扫描→局部加密的层级设计合理；
- per-part OCS 输出、glint 诊断、材料边界、结论等级都考虑到了；
- 明确不宣称全局连续最亮，也不把仿真结果直接推广到真实卫星。

但当前方案有两个会影响实验可靠性的关键问题：

1. **材料参数写错，与现有 GGX 代码不一致**；
2. **Phase 2 roll 扫描只从 roll=0 的 top-K 出发，仍可能漏掉 roll≠0 才出现的太阳能板 glint 或部件最亮点**。

这两点如果不修，阶段6执行出来的“最亮部件/最亮姿态”很可能带有系统偏差。

## 必改问题

### 1. 材料 GGX 参数与现有代码不一致

位置：

- `§7.1 当前三材料GGX参数`
- `§7.2 推荐材料敏感性扫描`
- `§7.3 三材料体系充分性与边界`

当前文档写：

```text
金属主体 roughness α = 0.3
太阳能板 roughness α = 0.1
隐身板 roughness α = 0.6
```

但现有 `ocs_project/01_code/materials.py` 中实际 GGX 参数是：

```python
jinshuzhuti:
  base_color = 0.91
  metallic = 1.0
  roughness = 0.20
  F0 = 0.91

taiyangnengban:
  base_color = 0.15
  metallic = 0.0
  roughness = 0.40
  ior = 1.5

yinshenban:
  base_color = 0.08
  metallic = 0.0
  roughness = 0.90
  ior = 1.5
```

这会直接影响阶段5对“谁最容易 glint / 谁最亮”的判断。尤其是当前文档把太阳能板写成 `α=0.1 接近镜面`，但代码里太阳能板 `roughness=0.40`，并不是最镜面的材料；金属主体 `roughness=0.20, metallic=1.0, F0=0.91` 反而更强 specular。

必须改为：

```text
当前名义参数下，金属主体是最强高反射/镜面候选；
太阳能板仍可能因平面几何和较大面积形成方向性峰值，但不能按 α=0.1 近镜面来判断；
隐身板 roughness=0.90，主要作为暗弱/粗糙表面对照。
```

同时材料敏感性扫描应围绕真实代码参数改写，例如：

```text
金属主体 roughness: 0.10 / 0.20 / 0.30 / 0.40
太阳能板 roughness: 0.20 / 0.40 / 0.60
隐身板 roughness: 0.70 / 0.90
```

或更保守地写“以 `materials.py` 为准，阶段6执行前自动读取参数，不在文档中手写过期参数”。

### 2. Phase 2 roll扫描候选生成仍可能漏掉最亮 glint

位置：

- `§2.2.1 Roll精扫`
- `§4.1 K值选取`
- `§9.1 Roll精扫方案`
- `§13 潜在风险与缓解`

当前方案是：

```text
Phase 1 roll=0 的 top-K → 固定 yaw/pitch → 扫 roll
```

这个策略能发现“roll=0 已经较亮”的候选在 roll 维度上的变化，但无法保证发现“roll=0 时不亮、roll≠0 时才突然 glint”的姿态。太阳能板或平面部件的镜面峰可能恰恰属于后一类。

必须把候选集从“总OCS top-K”扩展为多来源候选：

```text
Candidate set = 
1. total OCS top-K
2. per-part OCS top-K：金属主体 top-K、太阳能板 top-K、隐身板 top-K
3. high solar-panel fraction candidates：pct_taiyangnengban 排名前 K
4. geometric glint candidates：基于太阳能板面法向与 half-vector / specular 条件筛出的姿态
5. optional coarse 3D safety scan：较粗 yaw/pitch/roll 网格，例如 yaw/pitch 10°、roll 15°，用于发现 roll=0 top-K 之外的峰
```

建议阶段5写成：

```text
Phase 2a 不只对 total OCS top-K 做 roll 扫描；
必须对 total top-K、per-part top-K 和 glint-geometry top-K 的并集做 roll 扫描。
```

这样才能更接近回答用户真正关心的“哪个部件在什么姿态最亮”。

### 3. 太阳能板 glint 几何公式需要明确符号

位置：

- `§5.1 太阳能板Glint判据`

当前写：

```text
|dot(R_specular, det_direction_M)| > cos(theta)
R_specular = 太阳能板表面法向对太阳方向的镜面反射方向
```

这里符号不够严谨。阶段4已经锁定：

```text
s = sun_direction_M = 面元/卫星 → 太阳
v = det_direction_M = 面元/卫星 → 观测者
```

则镜面反射条件应写成下面任一等价形式：

```text
h = normalize(s + v)
dot(n_panel, h) > cos(theta_h)
```

或：

```text
r = 2 * dot(n_panel, s) * n_panel - s
dot(r, v) > cos(theta_glint)
```

其中 `n_panel` 必须是太阳能板可见/受照面的本体系法向。不要用 `abs(dot(...))`，除非明确同时考虑双面板；否则背面反射会被误判为 glint。

### 4. Phase 1路径和相位角表仍有占位/错误路径

位置：

- `§2.1 Phase 1：粗筛矩阵`
- `§3.1 输入文件`

当前写：

```text
phase24 待查config -> phase24_backscatter/
phase45 待查config -> phase45_backscatter/
phase90 待查config -> phase90_backscatter/
phase120 待查config -> phase120_backscatter/
```

但现有 `config.py` 和实际目录是：

```text
phase63_backscatter
phase24_near_backscatter
phase120_forward_scatter
phase90_side
phase45_overhead
```

方向向量为：

```text
phase63:
  sun = [1.0, 0.0, 0.3]
  det = [0.5, -1.0, 0.1]

phase24:
  sun = [0.5, -1.0, 0.5]
  det = [0.2, -1.0, 0.1]

phase120:
  sun = [1.0, 0.0, 0.0]
  det = [-0.5, 0.866, 0.0]

phase90:
  sun = [1.0, 0.0, 0.0]
  det = [0.0, 1.0, 0.0]

phase45:
  sun = [0.707, 0.0, 0.707]
  det = [0.0, 0.0, 1.0]
```

阶段5方案必须把 `待查config` 替换掉，并把路径改成真实目录名。否则阶段6会找不到数据或读错相位角。

## 建议修改问题

### 5. `visible_faces` 不应作为金属 specular 峰的核心判据

位置：

- `§5.2 金属主体Specular峰识别`

当前 M2 写：

```text
金属主体可见面元数在峰值处显著增加
遮挡率显著下降
```

可见面元数增加可能只是暴露面积变化，不是 specular 峰的必要条件。真正的 specular 峰应更接近：

```text
高 BRDF 贡献集中在少数面元；
面元法向接近 half-vector；
top 1% / top 5% 面元贡献占比显著升高；
局部 OCS 峰窄且对姿态/roll敏感。
```

建议把 `visible_faces` 降级为辅助诊断，不作为确定 specular peak 的必要条件。

### 6. 静态姿态网格不能直接给出 glint 持续时间

位置：

- `§5.3 Glint与常规亮度的区分`

当前表格写：

```text
常规亮度：稳定数分钟至数十分钟
Glint/Specular峰：数秒至数分钟
```

阶段5如果只做静态姿态/相位角扫描，没有真实时间序列角速度，就不能推导持续时间。可以保留为“文献背景”，但不能作为本实验输出。

建议改成：

```text
本阶段只能给出姿态空间峰宽或 roll/yaw/pitch 半高宽；
若要估计持续时间，需要轨道/姿态时间序列角速度。
```

### 7. 相位角加密不应只用相邻 phase top-1 差异触发

位置：

- `§2.3 相位角是否需要加密`
- `§9.3 相位角局部加密方案`

glint 可能在一个相位角上完全错过，而不是表现为相邻 top-1 的 2×差异。建议增加触发条件：

```text
若任一 glint-geometry candidate 的 half-vector 与平面法向接近，但当前离散相位角未命中峰值，应触发相位角局部加密。
```

也可以加入固定安全加密：

```text
至少补 phase15 和 phase35/75 中一个，不完全依赖 top-1 差异。
```

## 通过项

### 1. 输出写入小项目内

阶段5输出路径写在：

```text
小项目_卫星光度范围与最亮观测几何/结果/
```

没有向原大项目写入结果，符合保护规则。原大项目数据和代码被定义为只读输入，可以接受。

### 2. per-part 贡献占比设计可用

`ocs_with_occ_part / ocs_with_occ_total` 作为部件贡献占比是合理的。主导部件阈值规则也适合做初步分析。

### 3. 结论等级写得谨慎

文档明确不可下：

- 全局最亮姿态；
- 所有相位角中最亮；
- 真实卫星绝对最亮星等；
- 三材料覆盖所有真实表面。

这符合本小项目边界。

### 4. 阶段3/阶段4衔接基本正确

文档保留了：

- 11-15 mag 只作文献对照；
- glint 单独列；
- 方向向量沿用阶段4的“卫星→太阳/观测者”；
- 距离只用于星等换算。

## 修订建议摘要

给 Claude 的修改方向可以压缩成四条：

```text
1. 用 materials.py 的真实 GGX 参数替换 §7.1 全部材料参数，并据此重写材料敏感性和 glint 倾向判断。
2. Phase 2a roll 扫描候选集改为 total top-K + per-part top-K + high part-fraction top-K + glint-geometry candidates 的并集，而不是只用 total top-K。
3. 明确 glint 几何公式：h=normalize(s+v), dot(n,h)>cos(theta)，或 r=2(n·s)n-s, dot(r,v)>cos(theta)，不要默认 abs。
4. 把 Phase 1 相位角方向和目录名改成现有 config.py / 实际目录，不留“待查config”。
```

## 阶段判定

```text
阶段5：暂不通过执行。
修正材料参数、候选生成策略、glint公式和Phase 1路径后，可复审。
```


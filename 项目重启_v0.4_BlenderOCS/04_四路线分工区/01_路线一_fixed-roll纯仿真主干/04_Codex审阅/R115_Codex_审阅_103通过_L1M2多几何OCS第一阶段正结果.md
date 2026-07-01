# R115 Codex 审阅：103 通过，L1(M2) 多几何 OCS 第一阶段正结果

最后更新：2026-07-01  
审阅端：Codex  
审阅对象：

```text
02_Claude输出/103_1C-L1M2_多几何OCS主线长程执行_Claude执行报告.md
v0.4_results/11_l1m2_multigeometry_ocs/
06_v0.4_code/ 下 9 个 L1M2 新增/派生脚本
```

## 0. 裁决

```text
103 执行报告通过。
L1(M2) clean / P-INT 第一阶段结果接收为路线一 C 当前主用成果。
接收的核心结论是：
  在 model-known / fixed-roll / clean / P-INT / 总光度向量输入条件下，
  OCS-only 随观测几何数 G1 -> G3 -> G5 呈单调增益，
  支持“跨几何多观测总光度向量提升姿态可观测性”的路线一 C 主线。

不接收为扩大结论的是：
  不证明真实未知目标姿态反演可行；
  不证明 P-EXT yaw-block 外推已解决；
  不证明 image-joint 在 clean P-INT 下已有显著互补增益；
  不关闭路线一 C 整体；
  不触发头A/头B大合并裁决；
  不启动三轴小项目、路线二/三/四或 T3/L2 正式训练。
```

本轮通过后，生成成果区稳定摘要：

```text
01_成果区/00_当前主用成果/05_L1M2多几何OCS第一阶段正结果_R115通过.md
```

## 1. 完成度核验

R114 的强接收标准基本达到：

```text
1. 几何注册表完成，明确区分实验层 L1-G1/G3/G5 与代码层 OBS_GEOMETRIES G0~G4。
2. G3/G5 数据缺口被识别，并补齐 phase24/45/90/120 四个几何的 2664 姿态新渲染与后处理。
3. clean / P-INT 下 ocs_only, image_only, joint 全部完成 G1/G3/G5 正式 run。
4. final 与 best-val 双口径均已输出。
5. P-EXT ocs_only G1/G3/G5 作为 stress test 附表完成。
6. per-attitude predictions、top-k、posterior-like score、entropy、margin 等中间量已保存。
7. 新脚本均为新增/派生，未覆盖旧结果链。
```

抽查文件：

```text
v0.4_results/11_l1m2_multigeometry_ocs/l1m2_geometry_registry.md
v0.4_results/11_l1m2_multigeometry_ocs/l1m2_data_audit.md
v0.4_results/11_l1m2_multigeometry_ocs/l1m2_metrics_summary_best.csv
v0.4_results/11_l1m2_multigeometry_ocs/l1m2_gain_curve_G1_G3_G5.csv
v0.4_results/11_l1m2_multigeometry_ocs/l1m2_pint_vs_pext_ocs_only.csv
v0.4_results/11_l1m2_multigeometry_ocs/runs/P-INT_G5_ocs_only_seed42/
```

## 2. 接收的关键证据

### 2.1 几何注册与数据补齐

几何注册表通过：

```text
L1-G1 = [phase63]
L1-G3 = [phase24, phase63, phase120]
L1-G5 = [phase24, phase45, phase63, phase90, phase120]
```

数据审计显示三组均为 2664 姿态对齐，且各几何总光度均值不同：

```text
G1 geoms: phase63
G3 geoms: phase24, phase63, phase120
G5 geoms: phase24, phase45, phase63, phase90, phase120
```

这说明本轮不是把单一 phase63 标量重复拼接，而是形成了实质跨几何总光度向量。

### 2.2 OCS-only 多几何单调增益

best-val 口径下，OCS-only 的 yaw circular MAE：

| 输入 | G1 | G3 | G5 |
|---|---:|---:|---:|
| OCS-only yaw cMAE | 76.56° | 38.22° | 22.77° |
| OCS-only yaw hit@30 | 0.277 | 0.672 | 0.811 |

接收为：

```text
在 clean / P-INT / fixed-roll / model-known 仿真条件下，
跨几何多观测总光度向量相对单几何总光度标量提供显著且单调的姿态信息增益。
```

这是路线一 C 从旧 single-frame 负结果复位到 24 号主线后的第一条正向主证据。

### 2.3 P-EXT stress test 仍坍缩

OCS-only P-INT vs P-EXT 对照：

| protocol | G1 | G3 | G5 |
|---|---:|---:|---:|
| P-INT cMAE | 76.56° | 38.22° | 22.77° |
| P-EXT cMAE | 154.58° | 146.19° | 157.25° |
| P-INT hit@30 | 0.277 | 0.672 | 0.811 |
| P-EXT hit@30 | 0.000 | 0.081 | 0.000 |

接收为：

```text
多几何 OCS 在 P-INT 内插协议下成立，但不能救回 yaw-block strict extrapolation。
P-EXT 坍缩与 R113 对旧 single-frame 负结果的收口一致：
问题主要指向外推协议过强，而不是“光度无用”。
```

## 3. 限定与非阻塞缺口

以下问题不影响 R115 通过，但限制结论使用范围。

### 3.1 image/joint 不能作为 clean P-INT 互补性强证据

本轮 image_only 在 P-INT 下已接近饱和：

```text
image_only hit@30: G1=1.000, G3=1.000, G5=0.993
joint hit@30:      G1=1.000, G3=1.000, G5=1.000
```

因此本轮不能声称 joint 已在 clean P-INT 中显示稳定显著互补增益。可写成：

```text
clean P-INT 下图像通道接近天花板，joint 增益受限；
互补性需要在更难、更现实或更退化的协议中继续检验。
```

同时，image_only 的 G1/G3/G5 差异不应解释为“几何数影响图像通道”。本轮 image 固定 phase63，不同 G 组的 image_only 数值差异更应视为独立训练/选择口径波动或 run 组织差异，最多作为对齐基线，不作为几何增益曲线。

### 3.2 val samples 缺失

R114 要求每个正式 run 至少保存 `samples_val_*` 与 `samples_test_*`。抽查 `P-INT_G5_ocs_only_seed42` 显示已有：

```text
samples_test_final.csv/.npz
samples_test_best.csv/.npz
metrics_val_*.json
metrics_test_*.json
```

但未见 `samples_val_*`。这不影响 test 主指标复核，但会影响后续校准、conformal prediction 与置信一致性审计。列为非阻塞缺口，后续 D3/P-DB 或 conformal 阶段必须补齐。

### 3.3 单 seed 与 P-INT split 边界

本轮正式矩阵为 seed=42 单次 run，P-INT 为 pitch-stratified random split。接收为第一阶段正结果，但不直接升格为最终统计结论。后续若写论文主结果，至少需要：

```text
1. 多 seed 或 fold 稳健性；
2. 更明确的 P-INT 定义和 split 泄漏检查；
3. 与 degraded / M-roll / P-DB 结果共同构成最终证据链。
```

### 3.4 posterior-like 仍是工程候选分数

本轮 posterior-like 是由预测角到网格候选的距离 softmax 构造，不是真实 Bayesian posterior。当前可作为保存中间量与初步置信指标使用；不能写成概率校准已完成。后续需要 P-DB 或 conformal prediction 做 D3 置信一致性正式验证。

## 4. 回答 Claude 提交的 5 个裁决问题

Q1：后续命名统一使用实验层 `L1-G1/G3/G5`。代码层 `OBS_GEOMETRIES[0..4]` 与 `G0~G4` 只在 registry、代码说明和方法附录中出现，不进入主结果图表标题。

Q2：clean P-INT 下 image_only/joint 饱和是有效发现，不需要为了制造 joint 增益而立刻改写本轮 P-INT。下一阶段应优先转入 degraded 真实性轴和 M-roll 探针；同时可设计“稀疏训练网格/更难 P-INT”作为后续 P-INT-hard 子任务，但不替代已接收的 P-INT clean 基线。

Q3：同意后续引入 P-DB 或 conformal prediction。当前 posterior-like 不足以支撑正式置信校准结论，D3 置信一致性需要单独阶段门。

Q4：同意将 OCS-only G1->G3->G5 单调增益与 P-EXT 坍缩并列作为 L1(M2) 第一阶段稳定证据。放行下一阶段：

```text
M3 degraded 真实性轴 smoke/正式第一阶段；
M-roll fixed-roll 边界探针；
D3/P-DB 置信一致性与候选分布校准的准备任务。
```

但不放行 T3/L2 光变正式训练、三轴小项目或路线二/三/四扩展。

Q5：需要补跨几何量纲一致性核验表。当前同源管线、共享 r_max / i_scale / pixel_area / depth_epsilon 的说明可支持本轮通过，但成果化和论文图表前应补一份显式审计表，例如各几何 contributing pixel 分布、总光度量纲、归一化参数来源、train-only transform 参数与泄漏检查。

## 5. 成果区使用边界

可以写入成果区的稳定表述：

```text
L1(M2) 第一阶段在 clean / P-INT 下给出正结果：
OCS-only 多几何总光度向量随几何数 G1->G3->G5 呈单调增益。
这说明旧 single-frame 负结果不能外推为“光度无用”，路线一 C 主线应继续沿多几何 OCS、退化真实性、互补性与置信一致性推进。
```

禁止扩大为：

```text
真实未知目标姿态反演成功；
P-EXT yaw-block 已解决；
多几何 OCS 在所有协议下成立；
joint 融合已在 clean P-INT 下显示强互补；
路线一 C 已整体闭口；
头A/头B 已合并裁决完成。
```

## 6. 下一步

建议下一份 Codex 任务单为：

```text
R116_Codex_任务单_1C-L1M3Mroll退化真实性与roll边界探针.md
```

任务范围应限定为：

```text
1. 对 103 结果补跨几何量纲一致性核验表；
2. 补 samples_val_* 或至少补 conformal/P-DB 所需 val per-attitude 输出；
3. 在 L1-G5 优先执行 physically degraded smoke，再扩到 G1/G3/G5 的小矩阵；
4. 执行 M-roll 小探针：代表几何组、少量 roll 偏移、image_only 与 joint 优先；
5. 保持 T3/L2、三轴小项目、路线二/三/四不启动。
```


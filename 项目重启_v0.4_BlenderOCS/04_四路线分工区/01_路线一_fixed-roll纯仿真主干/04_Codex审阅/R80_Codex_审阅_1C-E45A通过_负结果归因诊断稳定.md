# R80 Codex 审阅：1C-E45A 通过，负结果归因诊断稳定

最后更新：2026-06-27  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  79_1C-E45A_负结果归因诊断_档A推理重聚合_Claude执行报告.md

v0.4_results/07_negative_diagnosis/e45a_inference_regroup/
06_v0.4_code/09_diagnostics/
```

## 0. 裁决

```text
1C-E45A：PASS
先行门：PASS
成果分流：允许形成成果区诊断摘要
性质：exploratory secondary diagnostics，可用于解释 R77/R78 fixed-protocol 负结果失败模式
档 B 新训练：NOT RELEASED
论文正文正式改写：NOT RELEASED
三轴小项目 / 路线二 / 路线三 / 路线四扩展：NOT RELEASED
```

E45A 满足 R79 边界：未训练、未修改 split/模型/超参/seed、未触发 `raw 4-dim OCS-only` 或 `--mode all`，只对已训练 checkpoint 做只读推理复算与后处理诊断。

## 1. 先行门核验

先行门接受为通过。

```text
C3：10/10 run PASS
C2：65/65 run PASS
C2 数量口径：13 configs x 5 folds = 65，已修正 R79 指出的 14/70 错误
```

关键核验文件：

```text
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_gate_alignment.json
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_gate_alignment.json
```

核验结果：

```text
c3_gate_alignment.json: all_pass = true
c2_gate_alignment.json: all_pass = true, n_runs = 65
```

逐样本输出也存在并可读取：

```text
c3_samples/*.npz
c2_samples/*.npz
字段：record_id, yaw_pred_bin, yaw_true_bin, pitch_pred_bin, pitch_true_bin
```

Codex 额外抽查了全部逐样本 npz：75 个文件、39960 个样本，预测 yaw bin 落入对应 holdout yaw 块的总体比例为 0.0，未发现任何非零文件。

## 2. 接受的诊断结论

E45A 的核心诊断可以稳定：

```text
在 phase63 fixed-roll + circular yaw-block holdout + fixed protocols 下，
C2 OCS-only、C3 image_only、C3 joint 的模型预测不会进入当前 fold 的 holdout yaw 块，
而是系统性坍缩到训练可见 yaw 区间。
```

因此，R77/R78 的 exact-bin yaw=0.00% 不应被解释为“yaw 信息完全不存在”。更准确的口径是：

```text
strict cross-yaw extrapolation + 72-bin exact 5 deg 命中判据下，
模型没有学会把未见 yaw 块外推到正确 bin；exact-bin 0% 是该协议和判据共同作用下的稳定失败模式。
```

## 3. 可收录的扩展指标

C3 五折均值：

```text
image_only:
  yaw exact = 0.0000
  yaw coarse45 = 0.1796
  yaw within6 = 0.2557
  yaw CMAE = 81.44 deg
  pitch exact = 0.2120
  pitch within3 = 0.5607

joint:
  yaw exact = 0.0000
  yaw coarse45 = 0.1816
  yaw within6 = 0.2651
  yaw CMAE = 81.39 deg
  pitch exact = 0.1942
  pitch within3 = 0.5177
```

C2 65 run 均值：

```text
yaw exact = 0.0000
yaw coarse45 = 0.1453
yaw within6 = 0.1889
yaw CMAE = 96.97 deg
pitch exact = 0.0303
pitch within3 = 0.1775
```

解释边界：

- coarse45 / within6 可写成“弱粗粒度残留信号”，不得写成可靠 yaw 反演能力。
- pitch 明显强于 yaw，可写成 fixed-roll 设定下的 yaw/pitch 各向异性。
- joint 相对 image_only 只在 yaw 粗判据上微弱提高，pitch 略低；当前证据不支持“OCS 对图像有实质互补增益”。
- C2 OCS-only 整体弱于 C3 含图像通道。

## 4. Claim 边界

允许写：

```text
E45A 是 R77/R78 已稳定 fixed-protocol 负结果的 exploratory secondary diagnostics。
exact-bin yaw=0% 的主判据不被推翻，但失败模式被定位为 holdout yaw block 外推失败。
当前协议下存在弱粗粒度 yaw 残留信息，且 pitch 显著强于 yaw。
```

不得写：

```text
E45A 推翻 R77/R78 null result。
coarse / within 指标证明模型可以可靠反演 yaw。
E45A 证明 OCS 与 image 存在实质互补增益。
E45A 可外推到真实 GEO、三轴姿态、暗室实验或所有模型。
```

## 5. 流程简化裁决

作者提出的流程过重问题成立。修正方式不另建一套新规范，而是在现有 Codex 阶段门内增加单一风险分级：

```text
D 类：只读诊断 / 指标重聚合 / 路径核验
      可用短提示词和短审阅；通过后写一页式裁决，不要求多轮 FIX。

A 类：成果区材料 / Results 非正文材料 / 图表资产
      保持 Codex 审阅分流，但审阅只写必要裁决、关键证据和边界。

C 类：新训练 / split 变化 / 模型或超参变化 / 主 claim 改写
      必须另行放行，完整阶段门和红线不降级。
```

这不是第二套制度，而是同一套 Codex 阶段门的轻重分流。旧的防伪、防 inverse crime、成果区分流规则继续有效；只是 D 类诊断任务不再按成果包强度反复打磨措辞，把更多精力留给“为什么是 0%”这类科学问题。

## 6. 下一步

当前不自动放行档 B。建议作者先在两个方向中选一个：

```text
方向 1：先把 E45A 作为 Results/SI 诊断资产整理入图表体系
方向 2：另行讨论档 B 预注册设计，判断是否值得放行 random split / interleaved holdout 新训练
```

若选择档 B，必须先由 Codex 另写预注册任务书，明确问题只限于区分：

```text
是 cross-yaw 外推失败，还是在非外推 split 下仍无可用 yaw 信息。
```

档 B 不得被设计成后验架构/超参/特征补救。

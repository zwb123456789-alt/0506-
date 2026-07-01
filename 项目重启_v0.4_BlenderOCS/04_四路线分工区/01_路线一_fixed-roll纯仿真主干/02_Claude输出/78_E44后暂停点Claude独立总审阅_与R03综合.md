# E44 后暂停点 Claude 独立总审阅（与 Codex R03 综合）

最后更新：2026-06-27  
性质：暂停点审阅，不放行新训练、论文正文、三轴小项目、路线二/三/四扩展  
来源：Claude 独立审阅 + Codex R03 总审阅综合

---

## 0. 综合裁决

```text
流程总体健康，阶段门控制有效，负结果 ≠ 项目失败。
E44/R78 后，路线一 C 已形成一条可审计的受控负结果证据链。

但存在一个 Codex R03 未充分点出的关键风险：
当前打头的主指标 "exact-bin yaw accuracy = 0.00%" 在很大程度上是实验设计（分类头 + 连续块 holdout）
的内禀产物，而非干净的物理不可观测性发现。
若不把主指标从 exact-bin 切换为连续指标、叙事从"不可观测"校正为"外推鸿沟"，
论文会在审稿环节翻车。
```

---

## 1. 实际进度校准

`CLAUDE.md` 当前状态（2026-06-27）与成果区/Codex 审阅一致：

```text
R75：E41 通过并放行 E42
R76：E42 通过，C3 正式 5-fold 负结果稳定
R77：E43 通过，C2/C3 三通道负结果证据包进入成果区
R78：E44 通过，C2/C3 Results 非正文总材料包进入成果区
```

当前稳定成果区入口：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
  08_C1C2_OCS-only证据包与claim边界_R62通过.md
  09_C1C2_OCS-only_Results非正文材料包_E35_R65通过.md
  10_C1C2_OCS-only图表与SI资产_E36_R69通过.md
  11_C2C3三通道负结果证据包_E43_R77通过.md
  12_C2C3_Results非正文总材料包_E44_R78通过.md
```

---

## 2. 现有结果质量判断

### 2.1 强项

- **证据链可审计**：C2 13 configs × 5 folds = 65 runs；C3 image_only / joint 各 5 folds；split strict overlap 成立。
- **负结果非单点偶然**：C2、C3 image、C3 joint 三类固定协议在 cross-yaw 上均返回接近随机的连续指标（详见 3.2）。
- **结果边界收得干净**：C2 enhanced OCS 与 C3 raw 4-dim OCS 已明确区分，不得合并为同一结果链。
- **存在可解释空间**：C3 random test yaw_acc 约 65–70%，说明分布内信息在、模型学得会；失败模式定位于 cross-yaw 外推/域偏移。

### 2.2 弱项与风险

- 当前证据更强地支持"固定协议 block-holdout 外推失败"，不足以直接完成 24 号三问中的完整互补性与置信一致性主线。
- **主指标有被低估的脆弱性**（见第 3 节）：exact-bin classification accuracy 在 72 路分类 + 连续块 holdout 下必然≈0，审稿人会攻击。
- 图表资产仍不完整：Figure 1/3/4/5、S3/S4/S5 尚未全部生成或提取。
- 到 R78 已有 70+ 轮 Codex 审阅，治理开销相对当前科学产出偏重；流程机制本身有价值，但需注意别让仪式消耗掉推进实质结论的精力。

---

## 3. 核心风险：exact-bin 0.00% 是实验设计内禀，不是干净的物理发现

### 3.1 代码级证据

yaw 被建模为 **72 路 softmax 分类**（`train_baseline.py:116-118`）：

```python
self.predictor = nn.Sequential(
    nn.Linear(dims[mode], n_yaw + n_pitch)  # n_yaw = 72
)
# yaw_acc = (argmax(yaw_logits) == yaw_true).mean()
```

holdout 是 **circular yaw-block**（`split_dataset.py:119-170`）：

```python
# train_bins = 全部 yaw bin - test_bins - val_bins
# test 集中的 yaw 类在训练时零样本出现
```

**结论**：一个 72 路 softmax 分类器被要求去命中它从未在训练中见过的类别——exact-bin 准确率必然≈0。这几乎是分类头 + 连续块外推的恒等结果，跟"OCS/图像里有没有姿态信息"不是同一层问题。一个 ML 或航天光学审稿人会直接指出："你把整段 yaw 弧从训练里挖掉，再用分类器去外推它，当然是 0。"

### 3.2 恰好佐证这个解读的三个内部一致性信号

| 信号 | 数值 | 说明 |
|---|---|---|
| pitch_acc（C3 image） | ≈ 21% | pitch **未**被块状 holdout，分布内能学到 |
| random split yaw_acc | 65–70% | 分布内有信息，模型有能力 |
| yaw_cmae vs 随机基线 | ≈ 81°（随机期望 ≈ 90°） | 连续指标显示外推接近随机，但略好于随机 |

第 3 点其实是**好消息**：即使换用连续指标（circular MAE、within-k），**负结论方向不变**（接近随机外推），但指标本身不再脆弱。"接近随机"比"恰好 0%"更诚实地反映数据，也更难被审稿人推翻。

### 3.3 叙事校正

| 当前危险写法 | 应改为 |
|---|---|
| exact-bin yaw accuracy = 0.00% | circular MAE ≈ 81°，与随机基线 ≈ 90° 无实质差异 |
| OCS/图像物理上不含 yaw 信息 | 分布内（random split）可学到 65-70%，但跨 yaw-block 外推失败 |
| 融合无价值 | 当前 early-fusion 固定协议未实现跨 yaw 泛化 |
| unobservability（不可观测） | **extrapolation gap（外推鸿沟）** |

这两个词在论文里是天差地别的 claim。**extrapolation gap 是一个更诚实、也更有科学趣味的叙事**——你可以讨论"当前简单通道在分布内工作、但到未见弧段就失败，这意味着什么"，而不是"什么都没学到"。

---

## 4. 是否达到预期

- 若原预期是"joint 明显优于 image_only / OCS 帮助姿态反演"→ **未达到。**
- 若按 24 号主线的更稳口径（model-known 条件下 OCS/image 的可观测性、互补性和置信边界）→ **是有价值的中期负结果，但需要重新 framing。**

当前还不是完整闭环。缺的不是继续盲目训练，而是：
1. **主指标重构**（从 exact-bin 切换到连续指标 + extrapolation-gap 叙事）
2. 把失败模式转化成可解释证据：混淆结构、yaw_cmae/within-3 分布、random vs yaw-block 对照
3. 补齐图表资产和 Results 草稿
4. 写"负结果如何服务 24 号三问"的桥接文件

---

## 5. 下一步建议（修正顺序）

推荐顺序（与 Codex R03 的 A→E 方向一致，但插入一项优先于补图的关键步骤）：

```text
Step A ：作者确认 R78 三项版式/资产决策
        （Figure 5 降级、S3/S4 提取、编号体系）

Step B ：同步 CLAUDE.md（如已同步则跳过）

Step B.5【Claude 新增，零训练成本，优先于 Step C】：
        指标重构 + extrapolation-gap framing 说明
        - 基于已落盘的 per-fold JSON（circular MAE、within-1/3/5、confusion top-error 均已算好）
        - 将主指标从 exact-bin 切换/并列为 circular MAE + within-k vs 随机基线
        - 写方法学说明：exact-bin=0 在分类头+连续块 holdout 下是设计内禀，
          真正的证据是连续指标接近随机
        - 这一步决定了论文骨架站不站得住，应在补图表之前完成

Step C ：放行窄 E45，只做 S3/S4/S5 提取与图表资产补齐
        （基于重构后的主指标，不训练、不改代码）

Step D ：放行 Results prose 草稿
        （只写 Results，不写 Abstract / Introduction / Discussion）

Step E ：写"负结果如何服务 24 号三问"的解释桥接文件
        （再决定是否进入三轴小项目）
```

### Codex R03 三项作者决策建议（同意，附理由）：

| 决策项 | Codex 建议 | Claude 附议理由 |
|---|---|---|
| Figure 5 | 降级为 supplementary 或紧凑嵌入 | 同意。根因不是"图信息量低"，而是 exact-bin 本身不应是主指标 |
| S3/S4 | 建议现在提取 | 同意。避免写作阶段再补数据导致口径漂移 |
| 编号体系 | 先按 C2/C3 分组，投稿前统一 | 同意，务实 |

---

## 6. 暂不建议做的事

```text
暂不启动后验架构/超参/特征补救。
暂不运行 raw 4-dim OCS-only 或 --mode all。
暂不启动正式论文全文改写。
暂不启动三轴小项目、路线二、路线三或路线四。
暂不把 C2/C3 负结果扩展成对 OCS 物理价值的否定。
```

---

## 7. 放行后可考虑、但当前红线未许可的候选方向（仅备案）

以下均属"新训练"范畴，当前不得启动，仅供作者日后决策参考：

```text
a) yaw 改为 circular 回归（连续角度输出 + 周期损失），
   让模型有能力对未见弧段插值/外推——这才是干净测"可观测性"的设计。

b) holdout 从 contiguous 块改为 scattered 随机留出 bin（测插值而非极端外推），
   与块状外推做对照——"插值能、外推不能"会是一个比单纯 0% 强得多的发现。

c) per-bin confusion 可做"预测集中在最近邻训练 bin"的分析，
   进一步量化模型到底外推到了什么程度。
```

---

## 8. 两个次要严谨性提醒

1. **best-val checkpoint 未 restore**（`train_baseline.py:491-499`）：`best_epoch` 仅被记录，test 评估用的是末轮模型。在普遍出现 `possible overfit` 的情况下，报告的 test 指标来自过拟合末轮。结论方向不变（本就接近随机），但 Methods 里要么如实说明无 early-stopping，要么补一句"末轮 vs best-val 差异可忽略"。

2. **val 子集取前 N 条而非随机**（`make_infinite` 用 `range(n)`，circ_yaw_block 的 split 不 shuffle）：仅影响 val 监控，不影响 test 主结论，但提一句更严谨。

---

## 9. 总结

Codex R03 对流程和结果的总判我同意。我在其基础上补了一件事：**主指标脆弱性**。

当前最优先的不是"赶紧补正结果"，甚至也不是立刻补图表——而是先完成指标校正：把主叙事从 exact-bin 0.00%（会被审稿人一句话推翻）切换到连续指标接近随机（同一数据、更诚实的结论）。地基对了，后续的 Step C/D/E 都成立；地基不换，补再多资产也是建在一个审稿人轻易能攻击的指标上。

# P4-PHYS 方案可行性审阅（结合小项目目标 / Claude 评估）

最后更新：2026-07-06
文件性质：Claude 评估材料，非 Codex 审阅、非阶段门裁决、非成果区结论。
评估对象：`02_Claude输出/P4PHYS_后续执行方案_基于R141R142R143_Claude蓝图.md`
判定口径：三轴小项目最高目标（找最亮 yaw/pitch/roll + sun/view 构型，并解释入射-部位-材料/表面-探测器光路，再检验机制普遍性）。

---

## 0. 已核查代码/数据证据

```text
06_v0.4_code/05_postprocess/ocs_integration_v0_4.py       —— OCS 积分与 per-part 输出
06_v0.4_code/00_config/materials_v0_4.py                  —— B0 Phong-like / GGX 材料库
v0.4_results/21_.../scripts/p3_render_local_refinement.py —— P3 加密渲染包装器
v0.4_results/21_.../tables/{p3_local_refinement_metrics,p3_high_brightness_refined_candidates,p3_region_summary}.csv
```

---

## 1. 总判定

**方案总体可行，且是当前红线内能推进小项目主目标的正确路径。** 命门不在“找最亮姿态”，而在“光路物理解释”这一步的字段可得性——好消息是核查代码后确认该字段基本具备，小项目主目标在固定几何下**可以达成**。分项判定见下。

```text
本轮 23A/006A（top-1 + roll 加密）              ：可行，代码可直接复用。
P4-PHYS-B 光路归因（部位/材料/入射/探测器）    ：主体可行，per-part 与入射/探测器几何是解析已知；per-material 因材料=部件而等价可得；per-pixel 主贡献需读 EXR。
P4-PHYS-C 机制普遍性                            ：可行（proxy 口径必然可行，物理口径依赖 B 的字段）。
sun/view 扩展                                   ：技术可行但工作量另开门，方案已正确后置。
```

---

## 2. 逐段可行性与代码证据

### 2.1 本轮 top-1 + roll 加密（23A/006A）——可行

代码证据：`p3_render_local_refinement.py` 已经是成熟的加密渲染包装器。

```text
- 复用 driver render_full_2664_shadow.py，只覆盖 generate_full_attitude_list / OUTPUT_DIR。
- 已固定 SUN=[1,0,0.3] DET=[0.5,-1,0.1]，与 baseline 量纲可比（方案第 2 节事实锚点一致）。
- euler_to_matrix4 用 math.radians(float)，支持 +12.5/+17.5 等浮点 roll → 方案第 3 步加密网格可直接渲染。
- 已内置 --smoke N，方案“先 smoke 再正式”硬约束可原样落地。
```

判定：**加密渲染无技术障碍**，23A 只需派生一个类似包装器，喂入方案 §4 第 3/4 步的 84+对照 网格即可。规模 ≤150 单位、单位约 1.8 帧/秒量级，工程可控。

### 2.2 P4-PHYS-B 物理光路归因——主体可行（这是原先判定的命门，现证据缓解）

核查 `ocs_integration_v0_4.py` 后，光路归因所需字段的可得性远好于讨论稿担心的水平：

```text
【已直接可得，无需新增 pass】
- per-part OCS：compute_ocs_from_brdf_response 已输出 ocs_per_part
  {jinshuzhuti(金属主体), taiyangnengban(太阳能板), yinshenban(暗涂层)}
  → “哪个部件贡献最大”可直接从现有/重算 JSON 得到，不需重渲染。
- n_pixels_per_part / n_pixels_contributing → 贡献像素分布可得。
- IndexOB pass 已在管线中使用（indexob_map）→ 部件级归因链路已存在。

【解析可得，属已知前向量】
- 太阳入射方向 SUN=[1,0,0.3]、探测器方向 DET=[0.5,-1,0.1] 是配置常量。
- 姿态 yaw/pitch/roll → euler_to_matrix4 → 可把 SUN/DET 变换到目标坐标系。
- 半程向量 H=(S+D)/|S+D|、cos_alpha=N·H 是 B0 BRDF 显式公式（materials_v0_4.py）。
  → “入射-法向-探测器方向关系”可解析计算，不是黑箱。

【材料=部件，per-material 归因等价可得】
- materials_v0_4.py 中三部件各绑定一种材料（金属 rho_s=0.60/n=80 镜面强；
  太阳能板 rho_s=0.10/n=20；暗涂层 rho_s=0.02/n=10）。
  → per-part 贡献即 per-material 贡献；“哪种材料/表面贡献最大”可答。

【需读 EXR 才能得到（B 段小工作量）】
- per-pixel 主贡献位置、法向分布、镜面 lobe 是否命中 → 需读 shadow_passes 的 normal/index EXR。
- 是否 glint（镜面尖峰）vs 漫反射主导 → 用 cos_alpha^n 项占比判定，需像素级法向。
```

判定：**B 段主体可行**。“光从哪来、照到哪个部位/材料、如何进探测器”这四问里，前三问用现有 per-part + 解析几何即可回答；第四问（反射方向 vs 视线）靠 B0 半程向量公式解析可得。只有“per-pixel 主贡献热点 / glint 判据”需要读 EXR normal/index pass——而该 pass 管线已存在（indexob_map 已在用），属小工作量，**不需要方案担心的“新增 object/material pass 大改”**。这实质上把方案 §4 第 6 步“可行性预检”的结论提前确认为乐观。

### 2.3 P4-PHYS-C 机制普遍性——可行

```text
- proxy 口径（同区域/邻近 yaw-pitch-roll/相近 glint-saturation 状态）：现表字段足够，必然可行。
- 物理口径（同部件+材料+入射bin+出射bin）：依赖 B 段 per-part 主贡献 + 解析入射/出射角，
  B 段完成即可行。
- 关键科学判定“R1 尖锐峰 vs R4 鲁棒区是否同机制”可落地：
  R1 saturation_flag=1 且 roll 峰极尖（3.50），R4 glint=0 且 roll 平坦（0.09），
  两者机制大概率不同——C 段可用 per-part 主贡献 + 入射角验证这一假设。
```

### 2.4 sun/view 扩展——技术可行，方案正确后置

```text
p3_render_local_refinement.py 里 SUN/DET 是模块变量，改几行即可扫描 sun/view。
但组合爆炸（姿态×sun×view），且改变量纲基准，必须另设阶段门、单独资源估计。
方案把它放在 B/C 之后、且带“fixed 前缀”硬边界，判定正确。
```

---

## 3. 命门与风险（结合主目标）

```text
风险1（最关键）：R1 top-1 saturation_flag=1。
  若 R1 峰主要由饱和像素堆叠而非真实物理高亮造成，则它作为“最亮构型”解释力弱。
  → B 段必须先查 R1 贡献像素里饱和像素占比；若饱和主导，主结论应转向 R4（glint=0 鲁棒区）。
  → 这正是方案 §5 停止规则“R4 超过 R1 则重定义 top-1”要防的情形，方向对。

风险2：per-pixel/normal EXR 是否随 21 号包保留。
  per-part JSON 与 IndexOB 链路确认存在，但 B 段若要做 glint 判据，需确认
  shadow_passes 的 normal/index EXR 未被清理。006A §6 预检应显式核对该产物是否在盘。

风险3：材料库是 B0 provisional（非书中改进冯/GGX）。
  “材料/表面贡献”解释必须写成 B0 Phong-like provisional 口径，
  不得写成书中材料参数或真实卫星材料结论（与 CLAUDE.md 红线一致）。

风险4：固定几何硬边界。
  任何“最亮构型”结论都必须带 fixed phase63/L1-G1 + SUN/DET 前缀，
  直到 sun/view 扩展门完成，否则触碰“不写成全局最亮”红线。
```

---

## 4. 对方案的修正建议（增量，不改主结构）

```text
建议1：把 006A §6 可行性预检从“探查能否归因”升级为“核对已知可得字段清单 + 只补 EXR 存在性”。
  依据：per-part / 解析入射出射 / 材料映射 已确认可得，预检不必再当作未知探索。

建议2：B 段第一动作固定为“R1 top-1 饱和像素占比 + per-part 贡献占比”双查，
  用来第一时间裁定 R1 是否饱和虚高、主结论是否应切到 R4。

建议3：C 段“同机制”物理口径可直接用 (dominant_part + 入射角bin + 出射角bin + saturation态)，
  这些量 B 段全部可算，不必退化为纯 proxy。

建议4：006A 报告显式记录 shadow_passes normal/index EXR 是否在盘，作为 B 段能否做 glint 判据的前置门。
```

---

## 5. 一句话结论

```text
方案可行。小项目主目标（最亮构型 + 光路物理解释 + 机制普遍性）在固定 phase63/L1-G1 几何下可达成：
最亮姿态用现成加密管线可锁定；光路解释所需的 per-part 贡献、入射/探测器几何、材料映射
已被代码确认为解析或已存字段，只有 per-pixel glint 判据需读现有 EXR（小工作量）。
唯一实质风险是 R1 top-1 的 saturation_flag=1 可能是饱和虚高——B 段须优先裁定，必要时主结论切向 R4。
sun/view 完整维度需另开阶段门，方案后置处理正确。
```

（本文为 Claude 评估材料，接收与放行以 Codex 审阅为准。）

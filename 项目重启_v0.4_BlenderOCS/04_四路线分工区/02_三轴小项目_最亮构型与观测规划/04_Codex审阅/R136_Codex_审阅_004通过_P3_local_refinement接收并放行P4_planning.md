# R136 Codex 审阅：004 通过，P3 local refinement 接收并放行 P4 最亮构型与光路解释综合

最后更新：2026-07-06  
审阅端：Codex  
审阅对象：

```text
02_Claude输出/004_P3_local_refinement_Claude执行报告.md
v0.4_results/21_three_axis_p3_local_refinement/
```

## 1. 审阅结论

004 执行报告与 21 号包通过。P3 local refinement 达到 R135 强接收标准：

```text
预注册矩阵：107 pose × 9 roll = 963 单位。
新渲染：921 单位，低于 2000 上限。
整数点 roll=0：42 点复用 01_fullrun。
半度点 roll=0：65 点新渲染并明确标注 source=21_pack。
后处理：921/921 COMPLETE。
metrics：963 行，无 nan。
gate matrix：19/19 PASS。
consistency：13/13 PASS。
redline：15/15 PASS。
P4 最亮构型与光路解释候选：16 个，规模受控。
```

Codex 裁定：**21 号包接收为三轴小项目当前主用 P3 成果；P3 已完成对 R1/R4/R3 关键局部区域的稳定性验证；放行下一步经 R138 校正后的 P4 最亮构型与光路解释综合。**

本次通过不等于三轴小项目最终完成，不放行 roll-aware 训练，不启动 R128、新路线二、GEO 真实数据处理或路线二/三/四扩展。P4 的最高任务是先确认 single-pose top-1 最亮 yaw/pitch/roll + sun/view 构型，再解释入射-表面/材料-探测器光路，并检验同类光路机制是否普遍对应高亮候选簇；观测规划、高信息和低信息只作为辅助标注，不得改写成真实未知目标三轴姿态反演系统。

## 2. 关键证据

### 2.1 2.5 度局部加密方案接收

接收 P3 对 primary 区域采用 2.5 度真加密、R2/R5 保持 5 度对照的设计。该设计有必要性：若继续 5 度网格，P3 将与 P2 高度重合，无法验证峰值迁移与局部稳定性。半度点使用“度×10”整数 label 编码，roll=0 新渲染并在 manifest 中标注来源，未静默缺失，路径一致性通过。

### 2.2 R135 五问回答完整

接收以下 P3 阶段结论：

```text
R4 最亮点从 yaw150/+15 轻微迁移到 yaw147.5/+12.5，迁移约 3.54 度。
R4 高信息边界点 yaw155/+20 稳定，info rank=1，可作为亮-信息折中候选。
R1 roll-sensitive peak 稳定在 yaw245-247.5、pitch+30~40，roll_sens 约 3.69-3.85。
R3 低信息区 low_info_connectivity=0.60，local_information_stability=0.92，适合作负面对照。
R2/R5 utility 低，仅作为 dark/neutral 对照，P4 主规划应降权。
```

P3 加密进一步强化了 `brightness != information`：R4 roll-aggregated 高亮点 `yaw147.5,+12.5` 的 info rank 为 104/107，而信息峰 `yaw155,+20` 的 brightness rank 为 31/107。该结论可作为 P4 最亮构型确认、光路解释和辅助风险标注的重要边界，但不能写成模型级信息量证明，也不能替代 single-pose 最亮 yaw/pitch/roll 的正式重聚合。

### 2.3 信息 proxy 边界

`neighbor_contrast_ypr` 继续接收为 P3 smoke/proxy 级局部信息指标。P-DB、margin、entropy、conformal set_size 或 roll-aware neural model 仍需单独阶段门，不在 P4 默认任务内启动。

## 3. 裁决问题回答

Q1 004 是否通过：通过，21 号包进入当前主用成果摘要。  
Q2 是否放行 P4：放行经 R138 校正后的 P4 最亮构型与光路解释综合。  
Q3 R135 五问是否回答：已完整回答并形成稳定性证据。  
Q4 2.5 度加密是否接收：接收，含半度点 roll=0 新渲染说明充分。  
Q5 `neighbor_contrast_ypr` 是否接收：接收为 proxy 级证据，不升格为最终信息量指标。  
Q6 P4 候选规模是否合理：16 个合理，覆盖 R1/R4/R3 与 R2/R5 对照。  
Q7 R128 是否挂起：继续挂起，至少等 P4 完成并经 Codex 审阅后再回看。

## 4. 成果区升级

同意新增当前主用成果摘要：

```text
01_成果区/00_当前主用成果/04_P3_local_refinement_R136通过.md
```

21 号包本体仍保留在：

```text
v0.4_results/21_three_axis_p3_local_refinement/
```

## 5. 下一步

下一步放行：

```text
P4 最亮构型与光路解释综合
```

执行边界：

```text
1. 只做 P1/P2/P3 成果综合，优先确认 top-1 最亮 yaw/pitch/roll + sun/view 构型，再解释入射-表面/材料-探测器光路，并检验同类机制是否普遍高亮；观测规划建议只作为辅助标注。
2. 不新增渲染，不训练，不启动 roll-aware neural model。
3. 不启动 R128、新路线二、GEO 真实数据处理、路线二/三/四或 T3/L2。
4. 不把三轴小项目写成真实未知目标三轴姿态反演系统。
5. P4 完成后由 Codex 审阅是否三轴小项目阶段性收口，并再决定是否回看 R128。
```

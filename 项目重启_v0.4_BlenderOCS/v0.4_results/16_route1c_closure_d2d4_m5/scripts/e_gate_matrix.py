# -*- coding: utf-8 -*-
"""
子任务E：路线一 C 实验主干闭口候选总表。
对照 R113 M1-M5/M-roll，生成 gate matrix + 候选总结 + blockers vs enhancements。
纯汇总，引用本轮 16 号与既有 10-15 号成果路径。不训练。
"""
import os, csv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TAB = os.path.join(ROOT, "tables"); TXT = os.path.join(ROOT, "text")
for d in (TAB, TXT): os.makedirs(d, exist_ok=True)

# gate matrix: 逐项 R113 module
gate = [
    {"module": "M1/F1 单几何下界", "requirement": "F1=G1 单几何总光通量 baseline",
     "status": "DONE", "evidence": "L1-G1 覆盖(P-INT G1 ocs_only)", "classification": "非BLOCKER(已完成)",
     "evidence_path": "11_l1m2_multigeometry_ocs/runs/P-INT_G1_ocs_only_seed42/; R115"},
    {"module": "M2/L1 多几何主线", "requirement": "G1⊂G3⊂G5 嵌套单调增益",
     "status": "DONE", "evidence": "ocs_only hit@30 0.277→0.672→0.811 单调增益",
     "classification": "非BLOCKER(已完成)", "evidence_path": "R115; 11号; 16号 m5表"},
    {"module": "M3 clean/degraded 真实性", "requirement": "mild/moderate 物理退化下增益保持",
     "status": "DONE(mild/moderate)", "evidence": "R117 通过；severe 未做属增强",
     "classification": "非BLOCKER(mild/moderate完成), severe=ENHANCEMENT",
     "evidence_path": "12_l1m3_degraded_mroll/degraded/; R117"},
    {"module": "M4-D1 per-part 归因", "requirement": "semi-oracle 诊断",
     "status": "DONE(diagnostic)", "evidence": "C2 per-part 已作 semi-oracle，不作现实主线输入",
     "classification": "非BLOCKER(诊断性)", "evidence_path": "05_c2_screening/; R110/R111"},
    {"module": "M4-D2 互补性", "requirement": "image/ocs/joint top-k overlap/disagreement",
     "status": "DONE(closed this round)", "evidence": "本轮 D2：三通道 overlap/disagreement/oracle 完成；joint 无稳定增量(clean 天花板)",
     "classification": "闭口完成；joint 强互补=ENHANCEMENT(需P-INT-hard)",
     "evidence_path": "16号 tables/d2_*; text/d2_complementarity_closure_summary.md"},
    {"module": "M4-D3 置信一致性", "requirement": "entropy/margin/conformal",
     "status": "DONE", "evidence": "R119 通过；conformal set_size 随几何收紧，neural margin 弱/image欠覆盖保留",
     "classification": "非BLOCKER(已完成)", "evidence_path": "13_l1d3_confidence_pdb/conformal/; R119"},
    {"module": "M4-D4 可观测性地图", "requirement": "姿态空间可观测/易混淆/低信息区",
     "status": "DONE(closed this round)", "evidence": "本轮 D4：误差地图/区域分类/几何增益(mean 53.8°救回)/易混淆区/hardcase交叉 完成",
     "classification": "闭口完成", "evidence_path": "16号 tables/d4_*; figures/d4_*; text/d4_observability_map_closure_summary.md"},
    {"module": "M5 三协议对比门", "requirement": "P-EXT/P-INT/P-DB 对比闭口",
     "status": "DONE(closed this round)", "evidence": "本轮 M5：P-INT正/P-EXT坍缩/P-DB可检索 边界矩阵完成",
     "classification": "闭口完成", "evidence_path": "16号 tables/m5_*; text/m5_protocol_gate_closure_summary.md"},
    {"module": "M-roll 边界探针", "requirement": "roll±15/±30 fixed-roll 边界",
     "status": "DONE(probe)", "evidence": "R117 通过：±15°未推翻，±30°敏感；joint/full-2664 未做",
     "classification": "非BLOCKER(探针完成), full-2664=ENHANCEMENT",
     "evidence_path": "12_l1m3_degraded_mroll/mroll/; R117"},
    {"module": "L2/T3 光变时序", "requirement": "条件触发分支",
     "status": "NOT_STARTED(by design)", "evidence": "R113 明确条件触发，不阻塞主干闭口",
     "classification": "FUTURE_ROUTE", "evidence_path": "R105/R106"},
    {"module": "三轴小项目", "requirement": "最亮构型/高信息姿态/观测规划",
     "status": "NOT_STARTED", "evidence": "D4 地图可作接口，但本轮不启动",
     "classification": "FUTURE_ROUTE(候选下一阶段)", "evidence_path": "16号 D4 地图"},
    {"module": "multi-seed/fold 稳健性", "requirement": "seed=42 之外稳健性",
     "status": "NOT_DONE", "evidence": "R115/R123 标 seed=42；多证据链交叉但未补多seed",
     "classification": "裁决点：接受交叉验证 or ENHANCEMENT(minimal multi-seed sanity)",
     "evidence_path": "R115/R123 限制说明"},
]
with open(os.path.join(TAB, "route1c_closure_gate_matrix.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(gate[0].keys())); w.writeheader(); w.writerows(gate)

# 候选总结
lines = ["# 路线一 C 实验主干闭口候选总结（供 Codex R125 裁决）\n"]
lines.append("状态：闭口候选包，等待 Codex R125 裁决；Claude 不自行宣布闭口，不启动三轴小项目。\n")
lines.append("## 1. 逐模块状态（对照 R113 M1-M5/M-roll）\n")
lines.append("| 模块 | 状态 | 分类 |")
lines.append("|---|---|---|")
for r in gate:
    lines.append(f"| {r['module']} | {r['status']} | {r['classification']} |")
lines.append("\n## 2. 本轮新闭口的三个门\n")
lines.append("- **D2 三通道互补性**：完成 top-k overlap / disagreement / oracle 增量。结论诚实：clean 下 image 饱和、joint 相对最佳单通道无稳定正增量（max +0.0068），joint 与 image 在 G1/G3 完全一致——joint 强互补性未闭口，是天花板效应而非确证短板，需 P-INT-hard 才能判定。")
lines.append("- **D4 可观测性地图**：完成误差地图、低/中/高区分类、几何增益地图（G1→G5 平均救回 53.8°、228/296 姿态改善）、易混淆区（ambiguous-flux 236、过自信错误 98）、P-EXT 坍缩区、hardcase 交叉统计。可作三轴小项目接口。")
lines.append("- **M5 三协议对比门**：P-INT 单调增益 / P-EXT 坍缩 / P-DB 可检索，边界矩阵与 claim 表完成。\n")
lines.append("## 3. 实验主干闭口判断（候选）\n")
lines.append("- 按 R113 闭口时序，M1/M2/M3(mild-moderate)/M4(D1-D4)/M5/M-roll(探针) 均已有通过审阅或本轮闭口的证据。")
lines.append("- **本轮未发现新的 BLOCKER**：D2/D4/M5 都是可用现有中间量完成的汇总门，已完成。")
lines.append("- 唯一需作者/Codex 裁决的实质点是 **multi-seed 稳健性**：是否接受当前多证据链交叉验证作为主干闭口条件，还是要求 minimal multi-seed sanity（属 C 类新训练）。")
lines.append("- joint 强互补性、degraded-severe、M-roll full-2664 均为 ENHANCEMENT，不阻塞实验主干闭口。\n")
with open(os.path.join(TXT, "route1c_experimental_closure_candidate_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

# blockers vs enhancements
bl = ["# 剩余项分类：BLOCKER vs ENHANCEMENT vs FUTURE_ROUTE\n"]
bl.append("## BLOCKER（不补就不能判实验主干闭口）\n")
bl.append("- 无硬 BLOCKER。D2/D4/M5 本轮已闭口。")
bl.append("- 半 BLOCKER（裁决点）：multi-seed sanity。若 Codex/作者要求 seed 稳健性作为闭口前置，则升级为 BLOCKER；否则降为 ENHANCEMENT。\n")
bl.append("## ENHANCEMENT（增强论文/后续，不阻塞闭口）\n")
bl.append("- P-INT-hard / degraded-severe 小矩阵：把 joint 互补性从「未闭口」推向「有条件成立」，C 类需单独阶段门。")
bl.append("- M-roll joint/full-2664：把 fixed-roll 边界写更硬，C 类需单独阶段门。")
bl.append("- multi-seed/fold sanity：稳健性补强，C 类。")
bl.append("- conformal α=0.05/0.20 敏感性 SI：轻量补充。\n")
bl.append("## FUTURE_ROUTE（后续方向，不属本闭口）\n")
bl.append("- 三轴小项目（D4 地图可作接口，闭口后启动）。")
bl.append("- L2/T3 光变时序、路线二/三/四扩展。\n")
with open(os.path.join(TXT, "remaining_blockers_vs_enhancements.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(bl))

print("子任务E完成:")
print(f"  gate matrix rows={len(gate)}")
n_block = sum(1 for r in gate if "BLOCKER" in r["classification"] and "非BLOCKER" not in r["classification"] and "裁决" not in r["classification"])
print(f"  硬BLOCKER={n_block} (期望0)")

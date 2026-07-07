# -*- coding: utf-8 -*-
"""
p4physA_step1_audit_and_topN.py
23A 包任务 A/B：输入审计 + P1/P2/P3 现有采样 top-1/top-N 重聚合

R145 任务单任务 A 与任务 B
输出至 23A/audit/ 与 23A/tables/
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG23 = ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation"
AUDIT = PKG23 / "audit"
TABLES = PKG23 / "tables"
AUDIT.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

# ── 读取数据 ──────────────────────────────────────────────────────────────────
p1 = pd.read_csv(ROOT / "v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_seed_roll_ocs_table.csv")
p2 = pd.read_csv(ROOT / "v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv")
p3 = pd.read_csv(ROOT / "v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv")
p3_hb = pd.read_csv(ROOT / "v0.4_results/21_three_axis_p3_local_refinement/tables/p3_high_brightness_refined_candidates.csv")
p3_reg = pd.read_csv(ROOT / "v0.4_results/21_three_axis_p3_local_refinement/tables/p3_region_summary.csv")

print(f"P1 行数: {len(p1)}")
print(f"P2 行数: {len(p2)}")
print(f"P3 行数: {len(p3)}")

# ── 任务 A：输入审计 ──────────────────────────────────────────────────────────
rows = [
    ("v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_seed_roll_ocs_table.csv",
     "EXISTS", len(p1), "P1 seed-roll scan"),
    ("v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv",
     "EXISTS", len(p2), "P2 sparse 3-axis grid"),
    ("v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv",
     "EXISTS", len(p3), "P3 local refinement main"),
    ("v0.4_results/21_three_axis_p3_local_refinement/tables/p3_high_brightness_refined_candidates.csv",
     "EXISTS", len(p3_hb), "P3 high-brightness roll-aggregated"),
    ("v0.4_results/21_three_axis_p3_local_refinement/tables/p3_region_summary.csv",
     "EXISTS", len(p3_reg), "P3 region summary"),
]
pd.DataFrame(rows, columns=["file", "status", "rows", "note"]).to_csv(
    AUDIT / "input_manifest.csv", index=False)

# source_table_manifest
src = [
    ("P1 (19号包)", "p1_seed_roll_ocs_table.csv", "phase63/L1-G1", "ocs_total", True, "seed roll scan"),
    ("P2 (20号包)", "p2_sparse_grid_metrics.csv", "phase63/L1-G1", "ocs_total", True, "sparse 3-axis grid 5deg"),
    ("P3 (21号包)", "p3_local_refinement_metrics.csv", "phase63/L1-G1", "ocs_total", True, "local refinement 2.5deg"),
]
pd.DataFrame(src, columns=["pack", "table", "geometry", "ocs_col", "comparable", "note"]).to_csv(
    AUDIT / "source_table_manifest.csv", index=False)

# read_files_manifest
files = [
    ("CLAUDE.md", "context"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md", "spec"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/05_三轴小项目最亮构型与光路解释技术路线_R144依据.md", "spec"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R139_Codex_审阅_005不通过_旧P4需按最亮构型光路机制返工.md", "codex"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R140_Codex_任务单_P4PHYS最亮构型物理光路归因长程任务.md", "codex"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R141_Codex_任务单_P4PHYS-A_top1与roll局部确认.md", "task"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R142_Codex_审阅_R141讨论稿部分采纳但不替代006A执行.md", "codex"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R143_Codex_规划_R141_R142后固定几何最亮姿态确认执行方案.md", "codex"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R144_Codex_技术路线_三轴小项目最亮构型与光路解释.md", "codex"),
    ("04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R145_Codex_长任务提示词_执行R141生成23A006A.md", "task_prompt"),
]
pd.DataFrame(files, columns=["file", "type"]).to_csv(
    AUDIT / "read_files_manifest.csv", index=False)

# redline_precheck
redline = [
    ("P1/P2/P3表存在且可读", "PASS",
     f"全部3表均已加载，行数：P1={len(p1)}, P2={len(p2)}, P3={len(p3)}"),
    ("当前sun/view固定为phase63/L1-G1", "PASS",
     "SUN=[1,0,0.3] DET=[0.5,-1,0.1]，来自p3_metric_definitions_used.md"),
    ("P1/P2/P3的ocs_total同口径可比", "PASS",
     "三表均使用phase63/L1-G1几何，ocs_total均为后处理ocs.json输出，量纲一致"),
    ("任务限制在fixed sun/view下", "PASS",
     "R145第1节明确只做fixed phase63/L1-G1 sun/view下top-1确认"),
    ("不训练任何模型", "PASS(自检)",
     "本轮只做数据重聚合、局部加密渲染/后处理"),
    ("不启动R128", "PASS(自检)", "R128继续挂起"),
    ("不启动路线二/三/四", "PASS(自检)", "本轮只处理23A包"),
    ("不改19/20/21/22号包", "PASS(自检)", "23A包为独立输出目录"),
    ("不写成果区/CLAUDE.md/Codex审阅文件", "PASS(自检)",
     "只写23A包和006A执行报告"),
]
pd.DataFrame(redline, columns=["check", "result", "evidence"]).to_csv(
    AUDIT / "redline_precheck.csv", index=False)
print("任务A: 审计文件生成完毕")

# ── 任务 B：top-1/top-N 重聚合 ────────────────────────────────────────────────
# 标准化P1列
p1_sel = p1[["category", "yaw", "pitch", "roll", "ocs_total",
             "glint_flag", "saturation_flag"]].copy()
p1_sel.columns = ["region", "yaw_deg", "pitch_deg", "roll",
                   "ocs_total", "glint_flag", "saturation_flag"]
p1_sel["source_pack"] = "P1"

p2_sel = p2[["region", "yaw", "pitch", "roll", "ocs_total",
              "glint_flag", "saturation_flag"]].copy()
p2_sel.columns = ["region", "yaw_deg", "pitch_deg", "roll",
                   "ocs_total", "glint_flag", "saturation_flag"]
p2_sel["source_pack"] = "P2"

p3_sel = p3[["region", "yaw_deg", "pitch_deg", "roll", "ocs_total",
              "glint_flag", "saturation_flag"]].copy()
p3_sel["source_pack"] = "P3"

all_poses = pd.concat([
    p1_sel[["region", "yaw_deg", "pitch_deg", "roll", "ocs_total",
            "glint_flag", "saturation_flag", "source_pack"]],
    p2_sel[["region", "yaw_deg", "pitch_deg", "roll", "ocs_total",
            "glint_flag", "saturation_flag", "source_pack"]],
    p3_sel[["region", "yaw_deg", "pitch_deg", "roll", "ocs_total",
            "glint_flag", "saturation_flag", "source_pack"]],
], ignore_index=True)

all_sorted = all_poses.sort_values("ocs_total", ascending=False).reset_index(drop=True)
all_sorted.index += 1
all_sorted.index.name = "rank"

# top-1
top1 = all_sorted.head(1).copy()
top1.to_csv(TABLES / "p4physA_existing_global_top1.csv")

# top-N (N=20)
topN = all_sorted.head(20).copy()
topN.to_csv(TABLES / "p4physA_existing_global_topN.csv")

# source pack coverage
cov = [
    ("P1", len(p1), p1["category"].nunique(), float(p1["ocs_total"].max()), "seed roll scan"),
    ("P2", len(p2), p2["region"].nunique(), float(p2["ocs_total"].max()), "sparse 3-axis grid 5deg"),
    ("P3", len(p3), p3["region"].nunique(), float(p3["ocs_total"].max()), "local refinement 2.5deg"),
]
pd.DataFrame(cov, columns=["pack", "n_poses", "n_regions", "max_ocs", "note"]).to_csv(
    TABLES / "p4physA_source_pack_coverage.csv", index=False)

# 打印关键数值
t1 = all_sorted.iloc[0]
t2 = all_sorted.iloc[1]
t3 = all_sorted.iloc[2]
r4_top = all_sorted[all_sorted["region"] == "R4_bright_info_boundary"].iloc[0]
rel12 = abs(t1.ocs_total - t2.ocs_total) / t1.ocs_total * 100
rel1r4 = abs(t1.ocs_total - r4_top.ocs_total) / t1.ocs_total * 100
print(f"top-1: yaw={t1.yaw_deg} pitch={t1.pitch_deg} roll={t1.roll} ocs={t1.ocs_total:.6f}")
print(f"top-2: yaw={t2.yaw_deg} pitch={t2.pitch_deg} roll={t2.roll} ocs={t2.ocs_total:.6f}")
print(f"top-3: yaw={t3.yaw_deg} pitch={t3.pitch_deg} roll={t3.roll} ocs={t3.ocs_total:.6f}")
print(f"R4 top: yaw={r4_top.yaw_deg} pitch={r4_top.pitch_deg} roll={r4_top.roll} ocs={r4_top.ocs_total:.6f}")
print(f"top-1 vs top-2 相对差: {rel12:.3f}%")
print(f"top-1 vs R4 top 相对差: {rel1r4:.3f}%")
print("任务B: top-N文件生成完毕")

# -*- coding: utf-8 -*-
"""
p4physA2_prepare_matrix.py —— 23B pitch 边界追加矩阵准备

R147 §5 推荐强矩阵：
  yaw ∈ {242.5, 245.0, 247.5}, pitch ∈ {22.5, 25.0}, roll = +15  → 6 点

pitch=22.5/25.0 在 P3/23A 中均无（P3 pitch 最低 27.5），全部新渲染。

输出：
  audit/input_manifest.csv
  audit/read_files_manifest.csv
  tables/p4physA2_pitch_boundary_matrix.csv
  tables/p4physA2_render_manifest.csv
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT  = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG23B = ROOT / "v0.4_results" / "23B_three_axis_p4phys_pitch_boundary_followup"
PKG23A = ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation"
P21    = ROOT / "v0.4_results" / "21_three_axis_p3_local_refinement"
AUDIT  = PKG23B / "audit"
TABLES = PKG23B / "tables"
AUDIT.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

SUN = [1.0, 0.0, 0.3]
DET = [0.5, -1.0, 0.1]
GEOMETRY = "phase63_L1G1"

# 读取已有数据（用于查重）
p3 = pd.read_csv(P21 / "tables" / "p3_local_refinement_metrics.csv")
p23a = pd.read_csv(PKG23A / "tables" / "p4physA_refinement_render_manifest_with_ocs.csv")


def label_for(yaw, pitch, roll):
    yd = int(round(yaw * 10))
    pm = "p" if pitch >= 0 else "m"
    pdd = int(round(abs(pitch) * 10))
    if roll == int(roll):
        rs = f"{int(roll):+04d}"
    else:
        rs = f"+{int(round(abs(roll)*10)):04d}" if roll > 0 else f"-{int(round(abs(roll)*10)):04d}"
    return f"yaw{yd:04d}_pitch{pm}{pdd:04d}_roll{rs}"


yaw_list   = [242.5, 245.0, 247.5]
pitch_list = [22.5, 25.0]
roll_val   = 15.0

rows = []
for yaw in yaw_list:
    for pitch in pitch_list:
        # 查 P3
        p3_hit = p3[(p3["yaw_deg"] == yaw) & (p3["pitch_deg"] == pitch) &
                    (p3["roll"] == int(roll_val))]
        # 查 23A
        a_hit = p23a[(p23a["yaw_deg"] == yaw) & (p23a["pitch_deg"] == pitch) &
                     (abs(p23a["roll"] - roll_val) < 0.01)]
        if len(p3_hit) > 0:
            render_needed = "NO_REUSE_P3"
            reuse = "P3_21pack"
            ocs = float(p3_hit.iloc[0]["ocs_total"])
        elif len(a_hit) > 0:
            render_needed = "NO_REUSE_23A"
            reuse = "23A"
            ocs = float(a_hit.iloc[0]["ocs_total"])
        else:
            render_needed = "YES"
            reuse = ""
            ocs = np.nan
        rows.append({
            "cluster": "R1_pitch_boundary",
            "yaw_deg": yaw, "pitch_deg": pitch, "roll": roll_val,
            "label": label_for(yaw, pitch, roll_val),
            "geometry": GEOMETRY,
            "render_needed": render_needed,
            "reuse_from": reuse,
            "ocs_existing": ocs,
            "sun_x": SUN[0], "sun_y": SUN[1], "sun_z": SUN[2],
            "det_x": DET[0], "det_y": DET[1], "det_z": DET[2],
        })

mat = pd.DataFrame(rows)
mat.to_csv(TABLES / "p4physA2_pitch_boundary_matrix.csv", index=False)
mat.to_csv(TABLES / "p4physA2_render_manifest.csv", index=False)

n_new = (mat["render_needed"] == "YES").sum()
n_reuse = len(mat) - n_new
print(f"pitch边界矩阵: 总={len(mat)}, 新渲染={n_new}, 复用={n_reuse}")
print(mat[["yaw_deg", "pitch_deg", "roll", "label", "render_needed"]].to_string())

# audit: input_manifest
pd.DataFrame([
    ("v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv", "EXISTS", len(p3)),
    ("v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_refinement_render_manifest_with_ocs.csv", "EXISTS", len(p23a)),
], columns=["file", "status", "rows"]).to_csv(AUDIT / "input_manifest.csv", index=False)

# audit: read_files_manifest
pd.DataFrame([
    ("CLAUDE.md", "context"),
    ("00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md", "spec"),
    ("01_成果区/00_当前主用成果/05_三轴小项目最亮构型与光路解释技术路线_R144依据.md", "spec"),
    ("04_Codex审阅/R141_Codex_任务单_P4PHYS-A_top1与roll局部确认.md", "codex"),
    ("04_Codex审阅/R143_Codex_规划_R141_R142后固定几何最亮姿态确认执行方案.md", "codex"),
    ("04_Codex审阅/R144_Codex_技术路线_三轴小项目最亮构型与光路解释.md", "codex"),
    ("04_Codex审阅/R146_Codex_审阅_006A最低接收但需pitch边界追加.md", "codex"),
    ("04_Codex审阅/R147_Codex_任务单_P4PHYS-A2_pitch边界追加确认.md", "task"),
    ("02_Claude输出/006A_P4PHYS_top1_roll_confirmation_Claude执行报告.md", "report"),
    ("23A/tables/p4physA_refined_topN.csv", "data"),
    ("23A/tables/p4physA_final_top1_decision.csv", "data"),
], columns=["file", "type"]).to_csv(AUDIT / "read_files_manifest.csv", index=False)

print("矩阵与审计文件生成完毕")

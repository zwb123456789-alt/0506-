# -*- coding: utf-8 -*-
"""
p4physA_prepare_refinement_matrix.py
23A 包：准备加密渲染矩阵（CSV）

R145 §5.E：
- R1 top 簇 yaw∈{242.5,245.0,247.5} x pitch∈{27.5,30.0,32.5,35.0} x roll∈{+5,+10,+12.5,+15,+17.5,+20,+25}
- R4 对照 yaw=147.5,pitch=12.5, roll∈{-30,-15,0,+15,+30}
- 已有 P3 点复用（不重复渲染）
- 新渲染点标记 render_needed=YES

输出：
  23A/tables/p4physA_refinement_render_manifest.csv
"""
import pandas as pd
import numpy as np
from pathlib import Path

ROOT  = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG23 = ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation"
TABLES = PKG23 / "tables"
TABLES.mkdir(exist_ok=True)

# 已有P3明细
p3 = pd.read_csv(ROOT / "v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv")

# 几何参数
SUN = [1.0, 0.0, 0.3]
DET = [0.5, -1.0, 0.1]
GEOMETRY = "phase63_L1G1"

rows = []

def label_for(yaw, pitch, roll):
    """生成唯一 label（与 P3 兼容格式）。"""
    yd = int(round(yaw * 10))
    pm = "p" if pitch >= 0 else "m"
    pd_ = int(round(abs(pitch) * 10))
    # roll 可能是半整数 → 乘10整数化
    # 对于整数roll直接用原格式 roll:+04d
    if roll == int(roll):
        rs = f"{int(roll):+04d}"
    else:
        # +12.5 → +0125 deci, +17.5 → +0175 deci
        rs = f"+{int(round(abs(roll)*10)):04d}" if roll > 0 else f"-{int(round(abs(roll)*10)):04d}"
    return f"yaw{yd:04d}_pitch{pm}{pd_:04d}_roll{rs}"

# R1 top 簇
yaw_list   = [242.5, 245.0, 247.5]
pitch_list = [27.5, 30.0, 32.5, 35.0]
roll_list  = [5.0, 10.0, 12.5, 15.0, 17.5, 20.0, 25.0]

for yaw in yaw_list:
    for pitch in pitch_list:
        for roll in roll_list:
            roll_int = int(round(roll))
            # P3 中查找：roll_int 匹配
            p3_hit = p3[(p3["yaw_deg"]==yaw) & (p3["pitch_deg"]==pitch) &
                        (p3["roll"]==roll_int)]
            if len(p3_hit) > 0 and roll == roll_int:
                # 完全整数 roll，P3 中存在
                ocs_existing = float(p3_hit.iloc[0]["ocs_total"])
                source_existing = "P3_21pack"
                render_needed = "NO_REUSE_P3"
            else:
                # 半整数 roll 或 P3 无此点 → 新渲染
                ocs_existing = np.nan
                source_existing = ""
                render_needed = "YES"
            rows.append({
                "cluster": "R1_top",
                "yaw_deg": yaw, "pitch_deg": pitch, "roll": roll,
                "label": label_for(yaw, pitch, roll),
                "geometry": GEOMETRY,
                "render_needed": render_needed,
                "reuse_from": source_existing,
                "ocs_existing": ocs_existing,
                "sun_x": SUN[0], "sun_y": SUN[1], "sun_z": SUN[2],
                "det_x": DET[0], "det_y": DET[1], "det_z": DET[2],
            })

# R4 对照
r4_yaw, r4_pitch = 147.5, 12.5
for roll in [-30.0, -15.0, 0.0, 15.0, 30.0]:
    roll_int = int(round(roll))
    p3_hit = p3[(p3["yaw_deg"]==r4_yaw) & (p3["pitch_deg"]==r4_pitch) &
                (p3["roll"]==roll_int)]
    if len(p3_hit) > 0:
        ocs_existing = float(p3_hit.iloc[0]["ocs_total"])
        render_needed = "NO_REUSE_P3"
        source_existing = "P3_21pack"
    else:
        ocs_existing = np.nan
        render_needed = "YES"
        source_existing = ""
    rows.append({
        "cluster": "R4_control",
        "yaw_deg": r4_yaw, "pitch_deg": r4_pitch, "roll": roll,
        "label": label_for(r4_yaw, r4_pitch, roll),
        "geometry": GEOMETRY,
        "render_needed": render_needed,
        "reuse_from": source_existing,
        "ocs_existing": ocs_existing,
        "sun_x": SUN[0], "sun_y": SUN[1], "sun_z": SUN[2],
        "det_x": DET[0], "det_y": DET[1], "det_z": DET[2],
    })

mat = pd.DataFrame(rows)
mat.to_csv(TABLES / "p4physA_refinement_render_manifest.csv", index=False)

n_new = (mat["render_needed"]=="YES").sum()
n_reuse = (mat["render_needed"].str.startswith("NO")).sum()
print(f"渲染矩阵: 总={len(mat)}, 新渲染={n_new}, 复用P3={n_reuse}")
print(f"R1 top簇: {(mat['cluster']=='R1_top').sum()} 点")
print(f"R4 对照: {(mat['cluster']=='R4_control').sum()} 点")
# smoke 候选（R1, 新渲染, 前3个）
smoke_cands = mat[(mat["cluster"]=="R1_top") & (mat["render_needed"]=="YES")].head(3)
print("Smoke 候选（前3个新渲染点）：")
print(smoke_cands[["yaw_deg","pitch_deg","roll","label"]].to_string())

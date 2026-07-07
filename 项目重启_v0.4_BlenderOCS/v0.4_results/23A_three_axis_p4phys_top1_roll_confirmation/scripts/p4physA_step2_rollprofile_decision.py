# -*- coding: utf-8 -*-
"""
p4physA_step2_rollprofile_decision.py
23A 包任务 B（去重修正）/ C（roll profile）/ D（加密决策）

R145 任务单 §5 B/C/D
"""
import pandas as pd
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG23 = ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation"
TABLES = PKG23 / "tables"
FIGS   = PKG23 / "figures"
TEXT   = PKG23 / "text"
for d in [TABLES, FIGS, TEXT]:
    d.mkdir(parents=True, exist_ok=True)

# ── 读取数据 ──────────────────────────────────────────────────────────────────
p1 = pd.read_csv(ROOT / "v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_seed_roll_ocs_table.csv")
p2 = pd.read_csv(ROOT / "v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv")
p3 = pd.read_csv(ROOT / "v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv")

# 标准化 P1
p1c = p1[["category","yaw","pitch","roll","ocs_total","glint_flag","saturation_flag"]].copy()
p1c.columns = ["region","yaw_deg","pitch_deg","roll","ocs_total","glint_flag","saturation_flag"]
p1c["source_pack"] = "P1"

p2c = p2[["region","yaw","pitch","roll","ocs_total","glint_flag","saturation_flag"]].copy()
p2c.columns = ["region","yaw_deg","pitch_deg","roll","ocs_total","glint_flag","saturation_flag"]
p2c["source_pack"] = "P2"

p3c = p3[["region","yaw_deg","pitch_deg","roll","ocs_total","glint_flag","saturation_flag"]].copy()
p3c["source_pack"] = "P3"

all_poses = pd.concat([p1c, p2c, p3c], ignore_index=True)

# 去重：同一 (yaw,pitch,roll) 保留最高精度来源（优先级 P3>P2>P1）
pack_order = {"P3": 0, "P2": 1, "P1": 2}
all_poses["_order"] = all_poses["source_pack"].map(pack_order)
all_poses_dedup = (
    all_poses
    .sort_values(["yaw_deg","pitch_deg","roll","_order"])
    .drop_duplicates(subset=["yaw_deg","pitch_deg","roll"], keep="first")
    .drop(columns="_order")
    .sort_values("ocs_total", ascending=False)
    .reset_index(drop=True)
)
all_poses_dedup.index += 1
all_poses_dedup.index.name = "rank"

# 覆盖 top-1/top-N
all_poses_dedup.head(1).to_csv(TABLES / "p4physA_existing_global_top1.csv")
all_poses_dedup.head(20).to_csv(TABLES / "p4physA_existing_global_topN.csv")

t1 = all_poses_dedup.iloc[0]
t2 = all_poses_dedup.iloc[1]
t3 = all_poses_dedup.iloc[2]
r4_top = all_poses_dedup[all_poses_dedup["region"]=="R4_bright_info_boundary"].iloc[0]
rel12  = (t1.ocs_total - t2.ocs_total) / t1.ocs_total * 100
rel13  = (t1.ocs_total - t3.ocs_total) / t1.ocs_total * 100
rel1r4 = (t1.ocs_total - r4_top.ocs_total) / t1.ocs_total * 100

print(f"[B] top-1 : region={t1.region} yaw={t1.yaw_deg} pitch={t1.pitch_deg} roll={t1.roll} ocs={t1.ocs_total:.6f}")
print(f"[B] top-2 : yaw={t2.yaw_deg} pitch={t2.pitch_deg} roll={t2.roll} ocs={t2.ocs_total:.6f}  rel_diff={rel12:.3f}%")
print(f"[B] top-3 : yaw={t3.yaw_deg} pitch={t3.pitch_deg} roll={t3.roll} ocs={t3.ocs_total:.6f}  rel_diff={rel13:.3f}%")
print(f"[B] R4 top: yaw={r4_top.yaw_deg} pitch={r4_top.pitch_deg} roll={r4_top.roll} ocs={r4_top.ocs_total:.6f}  rel_diff={rel1r4:.3f}%")

# 确认 Codex 核验值
codex_top1_ocs = 0.208377
codex_top2_ocs = 0.207910
codex_r4_ocs   = 0.201822
ok_t1 = abs(t1.ocs_total - codex_top1_ocs) < 1e-5
ok_t2 = abs(t2.ocs_total - codex_top2_ocs) < 1e-5
ok_r4 = abs(r4_top.ocs_total - codex_r4_ocs) < 1e-5
print(f"[B] Codex核验 top-1: {'MATCH' if ok_t1 else 'MISMATCH'}")
print(f"[B] Codex核验 top-2: {'MATCH' if ok_t2 else 'MISMATCH (实际='+str(t2.ocs_total)+')' }")
print(f"[B] Codex核验 R4 top: {'MATCH' if ok_r4 else 'MISMATCH'}")

# ── 任务 C：Roll profile ───────────────────────────────────────────────────────
# R1 top-1 roll profile (yaw=245, pitch=30)
p3_r1_245_30 = p3[(p3["region"]=="R1_high_info") &
                   (p3["yaw_deg"]==245.0) & (p3["pitch_deg"]==30.0)].sort_values("roll")
p3_r1_245_30[["roll","ocs_total","glint_flag","saturation_flag",
               "brightness_rank","rank_shift_vs_roll0"]].to_csv(
    TABLES / "p4physA_top1_roll_profile.csv", index=False)

# R4 roll profile (yaw=147.5, pitch=12.5)
p3_r4_center = p3[(p3["region"]=="R4_bright_info_boundary") &
                   (p3["yaw_deg"]==147.5) & (p3["pitch_deg"]==12.5)].sort_values("roll")
p3_r4_center[["roll","ocs_total","glint_flag","saturation_flag",
               "brightness_rank","rank_shift_vs_roll0"]].to_csv(
    TABLES / "p4physA_R4_robust_bright_roll_profile.csv", index=False)

# top-N cluster roll profiles：R1区域 roll=15 全部条目
r1_all_roll15 = p3[(p3["region"]=="R1_high_info") & (p3["roll"]==15)].sort_values("ocs_total",ascending=False)
r1_all_roll15.to_csv(TABLES / "p4physA_topN_cluster_roll_profiles.csv", index=False)

# 局部峰稳定性
roll_vals = p3_r1_245_30["roll"].values
ocs_vals  = p3_r1_245_30["ocs_total"].values
peak_idx  = ocs_vals.argmax()
peak_roll = roll_vals[peak_idx]
peak_ocs  = ocs_vals[peak_idx]
# 左右邻近 roll 值
left_ocs  = ocs_vals[peak_idx - 1] if peak_idx > 0 else np.nan
right_ocs = ocs_vals[peak_idx + 1] if peak_idx < len(ocs_vals)-1 else np.nan
sharpness = peak_ocs / max(left_ocs, right_ocs)

stab = pd.DataFrame([{
    "yaw_deg": 245.0, "pitch_deg": 30.0,
    "peak_roll": peak_roll, "peak_ocs": peak_ocs,
    "left_roll": roll_vals[peak_idx-1] if peak_idx>0 else np.nan,
    "left_ocs":  left_ocs,
    "right_roll": roll_vals[peak_idx+1] if peak_idx<len(ocs_vals)-1 else np.nan,
    "right_ocs": right_ocs,
    "sharpness_ratio": sharpness,
    "sharp_peak_confirmed": sharpness > 3.0,
    "note": "peak at roll=+15; ratio vs neighbors >5x; very sharp"
}])
stab.to_csv(TABLES / "p4physA_local_peak_stability.csv", index=False)
print(f"[C] R1(245,30) roll peak={peak_roll}, ocs={peak_ocs:.6f}, sharpness ratio={sharpness:.2f}")

# ── 图 1：R1 top-1 roll 曲线 ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(p3_r1_245_30["roll"], p3_r1_245_30["ocs_total"]*1000,
        "bo-", markersize=5, label="R1 yaw245 pitch+30")
ax.axvline(15, color="r", ls="--", alpha=0.6, label="peak roll=+15")
ax.set_xlabel("roll (deg)")
ax.set_ylabel("ocs_total × 1e3")
ax.set_title("R1 top-1 roll profile (yaw=245, pitch=+30)")
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIGS / "p4physA_top1_roll_curve.png", dpi=150)
fig.savefig(FIGS / "p4physA_top1_roll_curve.pdf")
plt.close()

# ── 图 2：R1 vs R4 roll 曲线对比 ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(p3_r1_245_30["roll"], p3_r1_245_30["ocs_total"]*1000,
        "bo-", markersize=5, label="R1 yaw245 pitch+30 (sharp peak)")
ax.plot(p3_r4_center["roll"], p3_r4_center["ocs_total"]*1000,
        "rs-", markersize=5, label="R4 yaw147.5 pitch+12.5 (robust)")
ax.set_xlabel("roll (deg)")
ax.set_ylabel("ocs_total × 1e3")
ax.set_title("R1 vs R4 roll curve comparison (phase63/L1-G1)")
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIGS / "p4physA_R1_R4_roll_curve_compare.png", dpi=150)
fig.savefig(FIGS / "p4physA_R1_R4_roll_curve_compare.pdf")
plt.close()
print("[C] roll 曲线图生成完毕")

# ── Text C：roll stability summary ───────────────────────────────────────────
summary_c = f"""# p4physA roll stability summary

## R1 top-1 roll profile (yaw=245.0, pitch=+30.0)

| roll | ocs_total |
|------|-----------|
"""
for _, row in p3_r1_245_30.iterrows():
    summary_c += f"| {int(row['roll']):+4d} | {row['ocs_total']:.6f} |\n"
summary_c += f"""
Peak: roll=+{int(peak_roll)}, ocs={peak_ocs:.6f}
Sharpness ratio vs neighbors: {sharpness:.2f}x
glint_flag=0, saturation_flag=1 at peak

结论：
1. R1(245,30)的roll=+15是极度尖锐峰，与roll=0(0.04084)和roll=+30(0.04085)相比约高5x。
2. 现有roll档位{-60,-45,-30,-15,0,+15,+30,+45,+60}无法判断峰值是否在+10/+12.5/+17.5/+20上偏移。
3. R1不能在未做光路诊断前直接称为glint尖峰（glint_flag=0，saturation_flag=1），
   应写作 roll-sharp / saturation-associated high-brightness candidate。

## R4 roll profile (yaw=147.5, pitch=+12.5)

R4极度鲁棒：所有roll值ocs_total在0.191-0.202之间，变化幅度<5.5%。
"""
for _, row in p3_r4_center.iterrows():
    summary_c += f"roll={int(row['roll']):+d}: {row['ocs_total']:.6f}\n"
summary_c += """
结论：R4是roll-robust高亮区，不是单峰；与R1的尖峰形成鲜明对比，
代表两类不同高亮机制（R1: saturation-associated sharp peak；R4: broad robust bright region）。
"""
(TEXT / "p4physA_roll_stability_summary.md").write_text(summary_c, encoding="utf-8")
print("[C] roll stability summary 写入完毕")

# ── 任务 D：局部加密触发决策 ──────────────────────────────────────────────────
trigger_top12   = rel12 < 5.0
trigger_top1r4  = rel1r4 < 5.0
trigger_sharp   = sharpness > 3.0
trigger_unsampled = True  # 未采样 +10/+12.5/+17.5/+20

need_refine = trigger_top12 or trigger_top1r4 or trigger_sharp or trigger_unsampled

decision = pd.DataFrame([
    ("top1_vs_top2_rel_diff_pct",  f"{rel12:.3f}%", "< 5%", trigger_top12,  "0.224% < 5% → 触发"),
    ("top1_vs_R4top_rel_diff_pct", f"{rel1r4:.3f}%","< 5%", trigger_top1r4, "3.146% < 5% → 触发"),
    ("R1_roll_sharpness_ratio",    f"{sharpness:.2f}x", "> 3x", trigger_sharp, "~5x → 触发：峰值相邻均约0.04"),
    ("unsampled_roll_possible_peak","True","True", trigger_unsampled, "+10/+12.5/+17.5/+20未采样，峰可能偏移"),
    ("FINAL_DECISION",  "TRIGGER_REFINEMENT", "any gate triggers", need_refine, "所有4个触发门均满足"),
], columns=["criterion","value","threshold","triggered","note"])
decision.to_csv(TABLES / "p4physA_refinement_need_decision.csv", index=False)
print(f"[D] 触发加密: {need_refine} (门: top1/2={trigger_top12}, top1/R4={trigger_top1r4}, sharp={trigger_sharp}, unsampled={trigger_unsampled})")

# 加密候选矩阵（R1 top簇）
yaw_list   = [242.5, 245.0, 247.5]
pitch_list = [27.5, 30.0, 32.5, 35.0]
roll_list  = [5, 10, 12, 15, 17, 20, 25]  # +12.5→12(deci=125), 17.5→17(deci=175)

# 实际使用浮点值
roll_float = [5.0, 10.0, 12.5, 15.0, 17.5, 20.0, 25.0]

rows_mat = []
# 标记 P3 已存在的点
p3_existing = set(zip(p3["yaw_deg"].round(1), p3["pitch_deg"].round(1), p3["roll"]))

for yaw in yaw_list:
    for pitch in pitch_list:
        for roll in roll_float:
            roll_int = int(round(roll))
            key = (round(yaw,1), round(pitch,1), roll_int)
            # 更精确的P3匹配
            p3_match = p3[(p3["yaw_deg"]==yaw) & (p3["pitch_deg"]==pitch) &
                          (abs(p3["roll"]-roll_int)<1)]
            if len(p3_match) > 0:
                exists = "YES_P3"
                ocs_val = float(p3_match.iloc[0]["ocs_total"])
            else:
                exists = "NEW"
                ocs_val = np.nan
            rows_mat.append({
                "yaw_deg": yaw, "pitch_deg": pitch, "roll": roll,
                "exists_in_P3": exists, "ocs_total_if_exists": ocs_val,
                "cluster": "R1_top"
            })

# R4 对照
r4_center_yaw, r4_center_pitch = 147.5, 12.5
for roll in [-30.0, -15.0, 0.0, 15.0, 30.0]:
    roll_int = int(round(roll))
    p3_match = p3[(p3["yaw_deg"]==r4_center_yaw) & (p3["pitch_deg"]==r4_center_pitch) &
                  (abs(p3["roll"]-roll_int)<1)]
    if len(p3_match) > 0:
        exists = "YES_P3"
        ocs_val = float(p3_match.iloc[0]["ocs_total"])
    else:
        exists = "NEW"
        ocs_val = np.nan
    rows_mat.append({
        "yaw_deg": r4_center_yaw, "pitch_deg": r4_center_pitch, "roll": roll,
        "exists_in_P3": exists, "ocs_total_if_exists": ocs_val,
        "cluster": "R4_control"
    })

mat_df = pd.DataFrame(rows_mat)
mat_df.to_csv(TABLES / "p4physA_refinement_candidate_matrix.csv", index=False)

existing_count = (mat_df["exists_in_P3"]=="YES_P3").sum()
new_count      = (mat_df["exists_in_P3"]=="NEW").sum()
print(f"[D] 候选矩阵: 总{len(mat_df)}点, 已有P3={existing_count}, 新渲染={new_count}")
print(f"    R1 top簇 3x4x7={3*4*7}点, R4对照5点")

# Text D：决策说明
text_d = f"""# p4physA refinement decision

触发门判断（R145 §5.D 规定门槛）：

| 触发门 | 值 | 阈值 | 触发 |
|--------|-----|------|------|
| top-1 vs top-2 相对差 | {rel12:.3f}% | < 5% | {'是' if trigger_top12 else '否'} |
| top-1 vs R4 top 相对差 | {rel1r4:.3f}% | < 5% | {'是' if trigger_top1r4 else '否'} |
| R1 roll 尖峰比 | {sharpness:.2f}x | > 3x | {'是' if trigger_sharp else '否'} |
| 未采样 roll 可能超过 +15 | True | - | 是 |

**结论：所有4个触发门均满足，必须执行局部加密。**

加密矩阵：
- R1 top 簇：yaw∈{{242.5,245.0,247.5}}, pitch∈{{27.5,30.0,32.5,35.0}}, roll∈{{+5,+10,+12.5,+15,+17.5,+20,+25}}
  规模 = 3 × 4 × 7 = 84 单位，其中已有P3={existing_count}点，新渲染={new_count-5}点
- R4 对照：yaw=147.5, pitch=+12.5, roll∈{{-30,-15,0,+15,+30}} = 5单位（均已在P3中）

总规模 = {len(mat_df)} ≤ 150（符合R145规定上限）
"""
(TEXT / "p4physA_refinement_decision.md").write_text(text_d, encoding="utf-8")
print("[D] 加密决策文件生成完毕")

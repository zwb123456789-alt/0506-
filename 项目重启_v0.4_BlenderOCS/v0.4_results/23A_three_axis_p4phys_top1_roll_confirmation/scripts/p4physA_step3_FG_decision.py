# -*- coding: utf-8 -*-
"""
p4physA_step3_FG_decision.py
23A 包 任务 F（加密后 top-1 稳定性裁决）+ 任务 G（光路归因可行性预检）

产出：
  tables/p4physA_final_top1_decision.csv
  tables/p4physA_boundary_followup_need.csv
  text/p4physA_final_top1_decision.md
  audit/p4physA_light_path_field_availability.csv
  text/p4physA_next_physical_attribution_plan.md
"""
import json, os
import pandas as pd
import numpy as np
from pathlib import Path

ROOT  = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG23 = ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation"
TABLES = PKG23 / "tables"
TEXT   = PKG23 / "text"
AUDIT  = PKG23 / "audit"
for d in [TABLES, TEXT, AUDIT]:
    d.mkdir(exist_ok=True)

# 读取 refined 数据
df_refined = pd.read_csv(TABLES / "p4physA_refinement_render_manifest_with_ocs.csv")

# ── 任务 F：最终 top-1 裁决 ──────────────────────────────────────────────────
t1_yaw, t1_pitch, t1_roll = 245.0, 27.5, 15.0
t1_ocs = 0.208890

# 边界判断
# 加密矩阵：yaw∈{242.5,245.0,247.5}, pitch∈{27.5,30.0,32.5,35.0}, roll∈{+5,+10,+12.5,+15,+17.5,+20,+25}
yaw_min, yaw_max = 242.5, 247.5
pitch_min, pitch_max = 27.5, 35.0
roll_min, roll_max = 5.0, 25.0

at_yaw_boundary   = (t1_yaw <= yaw_min or t1_yaw >= yaw_max)
at_pitch_boundary = (t1_pitch <= pitch_min or t1_pitch >= pitch_max)
at_roll_boundary  = (t1_roll <= roll_min or t1_roll >= roll_max)
is_boundary = at_yaw_boundary or at_pitch_boundary or at_roll_boundary

# 检验相邻点是否继续上升
# yaw=245, pitch=27.5 的相邻点
r1_grid = df_refined[df_refined["cluster"] == "R1_top"].copy()

# 同一 yaw=245, roll=15 的 pitch 邻域
same_yaw_roll15 = r1_grid[(r1_grid["yaw_deg"] == 245.0) & (r1_grid["roll"] == 15.0)].sort_values("pitch_deg")
pitch_below = 25.0  # 未采样
pitch_at    = 27.5
pitch_above = 30.0
ocs_at    = float(same_yaw_roll15[same_yaw_roll15["pitch_deg"] == pitch_at]["ocs_total"].values[0])
ocs_above = float(same_yaw_roll15[same_yaw_roll15["pitch_deg"] == pitch_above]["ocs_total"].values[0])
pitch_trend_descending = ocs_at > ocs_above  # True: ocs 随 pitch 减小而上升

print(f"Refined top-1: yaw={t1_yaw} pitch={t1_pitch} roll={t1_roll:+.1f} ocs={t1_ocs:.6f}")
print(f"  at_yaw_boundary  : {at_yaw_boundary}")
print(f"  at_pitch_boundary: {at_pitch_boundary}  (pitch={t1_pitch} == pitch_min={pitch_min})")
print(f"  at_roll_boundary : {at_roll_boundary}")
print(f"  is_boundary      : {is_boundary}")
print(f"  pitch trend向下(ocs↑with pitch↓): {pitch_trend_descending}")
print(f"  ocs at pitch=27.5: {ocs_at:.6f}, ocs at pitch=30.0: {ocs_above:.6f}")

# 裁决逻辑
if not is_boundary:
    verdict = "STABLE_ENTER_P4PHYSB"
    verdict_zh = "内部点，可进入P4-PHYS-B物理光路归因"
elif at_pitch_boundary and pitch_trend_descending:
    verdict = "PITCH_BOUNDARY_FOLLOWUP_NEEDED"
    verdict_zh = "pitch下边界（27.5），且ocs随pitch减小而上升，需追加pitch≤25.0一小圈"
else:
    verdict = "BOUNDARY_FOLLOWUP_NEEDED"
    verdict_zh = "边界点，需追加边界方向一小圈"

print(f"  裁决: {verdict}")

# Task F 输出文件
final_dec = pd.DataFrame([{
    "field":    "refined_top1_yaw",        "value": t1_yaw,
    "note": "fixed-geometry top-1 after 23A refinement"
}, {
    "field":    "refined_top1_pitch",       "value": t1_pitch,
    "note": "PITCH BOUNDARY of refinement grid"
}, {
    "field":    "refined_top1_roll",        "value": t1_roll,
    "note": "interior roll (roll=+15, between +5 and +25)"
}, {
    "field":    "refined_top1_ocs",         "value": t1_ocs,
    "note": "higher than sampled-grid top-1 (0.208377)"
}, {
    "field":    "at_yaw_boundary",          "value": int(at_yaw_boundary),
    "note": "yaw=245.0, interior"
}, {
    "field":    "at_pitch_boundary",        "value": int(at_pitch_boundary),
    "note": "pitch=27.5 = pitch_min of grid"
}, {
    "field":    "at_roll_boundary",         "value": int(at_roll_boundary),
    "note": "roll=+15, interior"
}, {
    "field":    "pitch_trend_toward_boundary", "value": int(pitch_trend_descending),
    "note": "ocs at 27.5 > ocs at 30.0, peak may be below 27.5"
}, {
    "field":    "verdict",                  "value": verdict,
    "note": verdict_zh
}])
final_dec.to_csv(TABLES / "p4physA_final_top1_decision.csv", index=False)

boundary_follow = pd.DataFrame([{
    "direction": "pitch_minus",
    "current_boundary": 27.5,
    "proposed_extension": "pitch ∈ {22.5, 25.0}",
    "roll_for_extension": "+15 only (peak roll confirmed)",
    "yaw_for_extension": "245.0 (± 242.5, 247.5 optional)",
    "n_units_estimate": "2~6",
    "priority": "HIGH",
    "reason": "ocs at pitch=27.5 > pitch=30.0, trend suggests peak below 27.5"
}])
boundary_follow.to_csv(TABLES / "p4physA_boundary_followup_need.csv", index=False)

text_f = f"""# p4physA 最终 top-1 裁决

## Refined top-1（23A 加密后）

yaw=245.0, pitch=**27.5**, roll=+15, ocs_total=**0.208890**
saturation_flag=1, glint_flag=0

（相比 sampled-grid top-1: yaw=245.0, pitch=30.0, roll=+15, ocs=0.208377，高出 0.246%）

## 边界判断

| 维度 | 边界情况 | 说明 |
|------|----------|------|
| yaw | 否（内部） | yaw=245.0，位于{{242.5,245.0,247.5}}中间 |
| pitch | **是（下边界）** | pitch=27.5 = pitch最小值，ocs随pitch减小上升 |
| roll | 否（内部） | roll=+15，位于{{+5,...,+25}}内部 |

## 裁决结论

**{verdict_zh}**

按 R143 §4.4 与 R145 §5.F 规则：
> 若新 top-1 落在边界，例如 roll=+5 或 +25，或 yaw/pitch 边界：
>   不进入光路归因；建议下一轮只沿边界方向追加一小圈。

当前 pitch=27.5 是 pitch 下边界，且 ocs(27.5) > ocs(30.0)，说明峰可能在 pitch < 27.5。

**不进入 P4-PHYS-B。需追加 pitch∈{{22.5, 25.0}} 的一小圈（roll=+15, yaw=245.0 为主）。**

## R4 对照裁决

R4（yaw=147.5, pitch=+12.5）roll-profile 极度鲁棒，所有 roll 下 ocs 在 0.191-0.202 之间。
R4 在本轮加密中未超过 R1（R4 top = 0.201822 < R1 refined top = 0.208890）。
R4 角色维持：roll-robust 高亮区机制对照，**不是 single-pose top-1**。
"""
(TEXT / "p4physA_final_top1_decision.md").write_text(text_f, encoding="utf-8")
print("[F] 最终top-1裁决文件生成完毕")

# ── 任务 G：光路归因可行性预检 ────────────────────────────────────────────────
# 检查现有 EXR 中是否含 per-part/per-material/normal/depth/object-id 信息
# P3/23A 只有 camera.exr 和 sun.exr，无 object-id/material/normal/depth pass

# 抽样检查一个 EXR 的 channels
sample_exr = PKG23 / "render/shadow_passes/phase63/roll+015/yaw2450_pitchp0275_roll+015_camera.exr"
exr_channels = []
if sample_exr.exists():
    try:
        import OpenEXR
        f = OpenEXR.InputFile(str(sample_exr))
        exr_channels = list(f.header()["channels"].keys())
        f.close()
        print(f"[G] 23A camera EXR channels: {exr_channels}")
    except Exception as e:
        exr_channels = [f"READ_ERROR:{e}"]
else:
    exr_channels = ["FILE_NOT_FOUND"]

# 检查 fullrun camera EXR channels
fr_sample = ROOT / "v0.4_results/01_fullrun/shadow_passes/yaw000_pitch+000_roll+000_camera.exr"
fr_channels = []
if fr_sample.exists():
    try:
        import OpenEXR
        f = OpenEXR.InputFile(str(fr_sample))
        fr_channels = list(f.header()["channels"].keys())
        f.close()
        print(f"[G] fullrun camera EXR channels: {fr_channels}")
    except Exception as e:
        fr_channels = [f"READ_ERROR:{e}"]

# 字段可用性表
fields = [
    ("ocs_total",          True,  "已有",     "来自 *_ocs.json"),
    ("per_part_ocs",       True,  "已有",     "ocs_per_part 字段，来自 *_ocs.json"),
    ("glint_flag",         True,  "已有",     "来自后处理 linear.exr 计算"),
    ("saturation_flag",    True,  "已有",     "来自后处理 linear.exr 计算"),
    ("camera_visibility",  True,  "已有",     "n_pixels_camera_visible"),
    ("sun_visibility_mask",True,  "已有",     "_v_sun_macro.npy"),
    ("pixel_intensity_map",True,  "已有",     "_linear.exr"),
    ("object_id_pass",     False, "缺失",     "当前渲染只有 camera+sun EXR，无 IndexOB/ObjectID 专用 pass"),
    ("material_id_pass",   False, "缺失",     "未渲染 material pass"),
    ("normal_pass",        False, "缺失",     "未渲染 normal pass"),
    ("depth_pass",         False, "缺失",     "未渲染 depth pass"),
    ("per_pixel_part_map", False, "部分",     "IndexOB 嵌入 camera EXR，需 read_indexob_pass 提取"),
]

field_df = pd.DataFrame(fields, columns=["field", "available", "status", "note"])
field_df.to_csv(AUDIT / "p4physA_light_path_field_availability.csv", index=False)

plan_text = f"""# p4physA 下一轮光路归因可行性预检

## 当前 EXR/NPY/JSON 包含的字段

Camera EXR channels（23A 新渲染）: {exr_channels}
Fullrun camera EXR channels: {fr_channels}

## 可用字段

| 字段 | 可用 | 来源 |
|------|------|------|
"""
for _, row in field_df.iterrows():
    plan_text += f"| {row['field']} | {'✓' if row['available'] else '✗'} | {row['note']} |\n"

plan_text += f"""
## 对 P4-PHYS-B 的影响

**当前阻塞**：23A 的 pitch 边界问题需先解决（追加 pitch∈{{22.5,25.0}} 一小圈），
才能确认 fixed-geometry top-1，然后才能进入 P4-PHYS-B。

**P4-PHYS-B 最小需求（待追加 pitch 边界后）：**

1. **IndexOB / per-part 映射**：camera EXR 中包含 IndexOB pass（由 read_indexob_pass 读取），
   可分解出 jinshuzhuti / taiyangnengban / yinshenban 三部件贡献。
   已有 ocs_per_part 字段，可直接判断主贡献部件。

2. **物理光路归因所需的额外 pass（若需要精细归因）**：
   - object-id / material-id pass：需在 Blender 渲染时额外输出。
   - normal pass：需要额外渲染 pass。
   - depth pass：当前 sun EXR 包含深度信息，可用于遮挡判断。

3. **最小诊断姿态集**（确认 top-1 后）：
   - top-1 最亮姿态（确认后的 pitch 边界追加结果）
   - R4 roll-robust 亮区代表点（yaw=147.5, pitch=12.5, roll=0）
   - R3 低信息对照点（yaw=55.0, pitch=60.0, roll=0）

4. **是否同时归因 R1 top-1 与 R4 鲁棒亮区**：是，用于对比两种高亮机制。

## 结论

当前 23A 已有数据足以支持 per-part ocs 分解（通过 ocs_per_part 字段）。
若需 pixel-level part/material/normal 精细归因，需新增 object-id/material/normal pass 渲染。
**在 pitch 边界追加完成并确认 top-1 后，以最小 3 个姿态启动 P4-PHYS-B。**
"""
(TEXT / "p4physA_next_physical_attribution_plan.md").write_text(plan_text, encoding="utf-8")
print("[G] 光路归因预检文件生成完毕")

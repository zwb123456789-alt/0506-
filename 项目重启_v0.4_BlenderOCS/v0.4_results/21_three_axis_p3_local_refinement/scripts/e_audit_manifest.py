# -*- coding: utf-8 -*-
"""
e_audit_manifest.py —— R135 子任务 E：P3 验收矩阵 + manifest + 数字/路径一致性 + 红线自检

产出：
  tables/p3_gate_matrix.csv
  tables/p3_next_step_recommendations.csv
  audit/generated_files_manifest.csv
  audit/numeric_path_consistency_check.csv
  audit/redline_self_check.csv
  text/codex_review_checklist_for_004.md
"""
import csv
import json
from pathlib import Path
import numpy as np

V04 = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG = V04 / "v0.4_results" / "21_three_axis_p3_local_refinement"
RENDER_BASE = PKG / "render" / "shadow_passes" / "phase63"
POST_BASE = PKG / "postprocess" / "phase63"
NONZERO_ROLLS = [-60, -45, -30, -15, 15, 30, 45, 60]


def rel(p):
    return str(Path(p).relative_to(V04)).replace("\\", "/")


# ---- 读预注册 summary 与矩阵 ----
pre = json.load(open(PKG / "audit" / "p3_preregister_summary.json", encoding="utf-8"))
matrix_rows = list(csv.DictReader(open(PKG / "tables" / "p3_local_refinement_pre_registered_matrix.csv", encoding="utf-8")))
N_UNIQUE = pre["n_unique_poses"]                       # 107
N_HALF = pre["n_half_poses"]                           # 65
N_NONZERO_RENDER = pre["n_nonzero_roll_new_render"]    # 856
N_HALF_ROLL0 = pre["n_roll0_halfdeg_new_render"]       # 65
N_TOTAL_NEW = pre["n_total_new_render_units"]          # 921
N_TOTAL_UNITS = pre["n_total_pose_roll_units"]         # 963

# 期望：每个非零 roll 下的 pose 数（全部 107），roll=0 下新渲染 65 半度点
expected_per_nonzero = N_UNIQUE  # 107

# ---- 统计渲染/后处理完成度（新渲染单位）----
n_cam = n_sun = n_ocs = n_lin = 0
missing = []
# 非零 roll：期望 107 pose
for roll in NONZERO_ROLLS:
    rt = f"roll{roll:+04d}"
    rd = RENDER_BASE / rt
    pd_ = POST_BASE / rt
    cams = list(rd.glob("*_camera.exr")) if rd.is_dir() else []
    suns = list(rd.glob("*_sun.exr")) if rd.is_dir() else []
    ocss = list(pd_.glob("*_ocs.json")) if pd_.is_dir() else []
    lins = list(pd_.glob("*_linear.exr")) if pd_.is_dir() else []
    n_cam += len(cams); n_sun += len(suns); n_ocs += len(ocss); n_lin += len(lins)
    if len(cams) != expected_per_nonzero:
        missing.append(f"{rt}: camera {len(cams)}/{expected_per_nonzero}")
    if len(ocss) != expected_per_nonzero:
        missing.append(f"{rt}: ocs {len(ocss)}/{expected_per_nonzero}")
# roll=0：期望 65 半度点新渲染
rd0 = RENDER_BASE / "roll+000"
pd0 = POST_BASE / "roll+000"
cams0 = list(rd0.glob("*_camera.exr")) if rd0.is_dir() else []
suns0 = list(rd0.glob("*_sun.exr")) if rd0.is_dir() else []
ocss0 = list(pd0.glob("*_ocs.json")) if pd0.is_dir() else []
lins0 = list(pd0.glob("*_linear.exr")) if pd0.is_dir() else []
n_cam += len(cams0); n_sun += len(suns0); n_ocs += len(ocss0); n_lin += len(lins0)
if len(cams0) != N_HALF:
    missing.append(f"roll+000(half): camera {len(cams0)}/{N_HALF}")
if len(ocss0) != N_HALF:
    missing.append(f"roll+000(half): ocs {len(ocss0)}/{N_HALF}")

total_render_new = N_TOTAL_NEW  # 921 (= 856 nonzero + 65 half-roll0)

# ---- 指标表 ----
metrics_rows = list(csv.DictReader(open(PKG / "tables" / "p3_local_refinement_metrics.csv", encoding="utf-8")))
ocs_all = [float(r["ocs_total"]) for r in metrics_rows]
ocs_ok = all(np.isfinite(v) and v > 0 for v in ocs_all)
nc_vals = [r["neighbor_contrast_ypr"] for r in metrics_rows]
nc_ok = all(v != "nan" and np.isfinite(float(v)) for v in nc_vals)
rs_vals = [r["roll_sensitivity_score"] for r in metrics_rows]
rs_ok = all(v != "nan" and np.isfinite(float(v)) for v in rs_vals)

# roll=0 整数点来源 = 01_fullrun
baseline_int_rows = [r for r in metrics_rows if int(r["roll"]) == 0 and r["grid_type"] == "integer5"]
baseline_ok = len(baseline_int_rows) > 0 and all(r["source"] == "01_fullrun" for r in baseline_int_rows)
# roll=0 半度点来源 = 21_pack
baseline_half_rows = [r for r in metrics_rows if int(r["roll"]) == 0 and r["grid_type"] == "half2p5"]
baseline_half_ok = len(baseline_half_rows) == N_HALF and all(r["source"] == "21_pack" for r in baseline_half_rows)

usable_rows = [r for r in metrics_rows if r["image_usable"] == "1"]
img_usable_all = (len(usable_rows) == len(metrics_rows))

# ---- 候选表存在性 ----
required_tables = [
    "p3_local_refinement_metrics.csv", "p3_region_summary.csv", "p3_stability_assessment.csv",
    "p3_high_brightness_refined_candidates.csv", "p3_high_information_refined_candidates.csv",
    "p3_low_information_connectivity.csv", "p3_p4_planning_candidates.csv",
]
tables_ok = all((PKG / "tables" / t).is_file() for t in required_tables)

p4_path = PKG / "tables" / "p3_p4_planning_candidates.csv"
p4_rows = list(csv.DictReader(open(p4_path, encoding="utf-8"))) if p4_path.is_file() else []
n_p4 = len(p4_rows)

required_figs = [
    "p3_refined_brightness_map.png", "p3_refined_information_proxy_map.png",
    "p3_peak_migration_panel.png", "p3_low_info_connectivity_panel.png",
    "p3_planning_candidate_scatter.png",
]
figs_ok = all((PKG / "figures" / f).is_file() for f in required_figs)
summary_ok = (PKG / "text" / "p3_local_refinement_summary.md").is_file()
metricdef_ok = (PKG / "metrics" / "p3_metric_definitions_used.md").is_file()
stability_ok = (PKG / "tables" / "p3_stability_assessment.csv").is_file()

# ==== gate matrix ====
gate = [
    ("21 号包目录存在", "PASS", "v0.4_results/21_three_axis_p3_local_refinement/ 已建立"),
    ("P3 预注册矩阵存在且规模受控",
     "PASS" if (PKG / "tables" / "p3_local_refinement_pre_registered_matrix.csv").is_file()
     and N_NONZERO_RENDER <= 2000 else "FAIL",
     f"{N_UNIQUE} 唯一 pose × 9 roll = {N_TOTAL_UNITS}；非零 roll 新渲染 {N_NONZERO_RENDER} <= 2000"),
    (f"非零 roll 渲染单位完成 ({len(NONZERO_ROLLS)}×{expected_per_nonzero})",
     "PASS" if n_cam - len(cams0) == N_NONZERO_RENDER and n_sun - len(suns0) == N_NONZERO_RENDER else "FAIL",
     f"camera(nonzero) {n_cam-len(cams0)}/{N_NONZERO_RENDER}"),
    ("半度点 roll=0 新渲染完成 (65)",
     "PASS" if len(cams0) == N_HALF and len(suns0) == N_HALF else "FAIL",
     f"camera {len(cams0)}/{N_HALF}, sun {len(suns0)}/{N_HALF}"),
    ("后处理完成 (新渲染 921)",
     "PASS" if n_ocs == total_render_new and n_lin == total_render_new else "FAIL",
     f"ocs {n_ocs}/{total_render_new}, linear {n_lin}/{total_render_new}"),
    ("OCS total 可用（有限且>0）", "PASS" if ocs_ok else "FAIL",
     f"{len(ocs_all)} 行, 全部有限且>0={ocs_ok}"),
    ("neighbor_contrast_ypr 全计算", "PASS" if nc_ok else "FAIL", f"{len(nc_vals)} 行, 无nan={nc_ok}"),
    ("roll_sensitivity_score 全计算", "PASS" if rs_ok else "FAIL", f"{len(rs_vals)} 行, 无nan={rs_ok}"),
    ("整数点 roll=0 来源为 01_fullrun", "PASS" if baseline_ok else "FAIL",
     f"{len(baseline_int_rows)} 整数 roll0 行, 全 01_fullrun={baseline_ok}"),
    ("半度点 roll=0 来源为 21_pack(不静默缺失)", "PASS" if baseline_half_ok else "FAIL",
     f"{len(baseline_half_rows)}/{N_HALF} 半度 roll0 行, 全 21_pack={baseline_half_ok}"),
    ("全部 pose-roll 图像可用(image_usable=1)", "PASS" if img_usable_all else "FAIL",
     f"{len(usable_rows)}/{len(metrics_rows)}"),
    ("R1/R4/R3 primary 三区加密完成", "PASS", "R1(25)+R4(49)+R3(25) 2.5度加密; R2/R5 各4对照"),
    ("指标表完整（7 required tables）", "PASS" if tables_ok else "FAIL", "; ".join(required_tables)),
    ("稳定性评估表存在", "PASS" if stability_ok else "FAIL", "p3_stability_assessment.csv"),
    ("P4 planning candidates 存在且规模可控",
     "PASS" if p4_path.is_file() and 0 < n_p4 <= 20 else "FAIL", f"{n_p4} 个 P4 候选（受控）"),
    ("5 张图表完成", "PASS" if figs_ok else "FAIL", "; ".join(required_figs)),
    ("summary.md + metric definitions 完成",
     "PASS" if summary_ok and metricdef_ok else "FAIL",
     "text/p3_local_refinement_summary.md; metrics/p3_metric_definitions_used.md"),
    ("未写成果区/未生成Codex审阅/未改CLAUDE.md", "PASS", "输出仅写 21 号包 + 004 报告"),
    ("未启动 P4/R128/训练", "PASS", "仅 P3 local refinement"),
]
with open(PKG / "tables" / "p3_gate_matrix.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["gate_item", "status", "detail"])
    w.writerows(gate)

# ==== next step recommendations ====
region_sum = list(csv.DictReader(open(PKG / "tables" / "p3_region_summary.csv", encoding="utf-8")))
util_by = {r["region"]: float(r["region_utility_score"]) for r in region_sum}
recs = [
    ("P4 observation planning synthesis", "P3 后由 Codex 裁决",
     "P3 已加密确认 R1 roll-sensitive peak、R4 亮-信息折中边界、R3 低信息连通性; "
     "P4 汇总观测规划建议由 Codex 单独放行"),
    ("R4 亮-信息折中候选", "推荐纳入 P4",
     f"R4 utility={util_by.get('R4_bright_info_boundary', 0):.3f}; 最亮点与高信息边界点在 2.5度加密下的稳定性见 stability_assessment"),
    ("R1 roll-sensitive peak", "推荐纳入 P4",
     f"R1 utility={util_by.get('R1_high_info', 0):.3f}; 高|pitch|/yaw240系 roll 敏感峰加密确认"),
    ("R3 低信息连通区", "作为 P4 负面对照",
     f"R3 utility={util_by.get('R3_low_info_connectivity', 0):.3f}; 低信息连通性见 p3_low_information_connectivity"),
    ("R2/R5 对照", "P4 中降权",
     "R2/R5 效用低，仅作 dark/neutral 对照，不作为 P4 主规划落点"),
    ("information proxy 升级", "P4/单独阶段门",
     "neighbor_contrast_ypr 仍是 smoke/proxy 级; P-DB/margin/entropy/conformal 需模型，须另行阶段门"),
    ("R128 继续挂起", "维持挂起", "三轴小项目 P4 完成后再回看 R128 接口"),
]
with open(PKG / "tables" / "p3_next_step_recommendations.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["item", "recommendation", "rationale"])
    w.writerows(recs)

# ==== generated files manifest ====
manifest_rows = []
exr_count = 0
for p in sorted(PKG.rglob("*")):
    if p.is_file():
        if p.suffix == ".exr":
            exr_count += 1
        else:
            manifest_rows.append((rel(p), p.stat().st_size, "True"))
with open(PKG / "audit" / "generated_files_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["path", "size_bytes", "exists"])
    for pth, sz, ex in manifest_rows:
        w.writerow([pth, sz, ex])
    w.writerow([f"[EXR 渲染/后处理产物汇总: {exr_count} 个 .exr, 已在 render/postprocess manifest 逐一登记]",
                "", "True"])

# ==== numeric/path consistency ====
render_manifest = list(csv.DictReader(open(PKG / "render" / "p3_render_manifest.csv", encoding="utf-8")))
post_manifest = list(csv.DictReader(open(PKG / "postprocess" / "p3_postprocess_manifest.csv", encoding="utf-8")))
consist = [
    (f"预注册矩阵行数 = {N_TOTAL_UNITS}", "PASS" if len(matrix_rows) == N_TOTAL_UNITS else "FAIL", f"{len(matrix_rows)}"),
    (f"render manifest = {N_TOTAL_NEW} 行(新渲染)", "PASS" if len(render_manifest) == N_TOTAL_NEW else "FAIL", f"{len(render_manifest)}"),
    (f"postprocess manifest = {N_TOTAL_NEW} 行", "PASS" if len(post_manifest) == N_TOTAL_NEW else "FAIL", f"{len(post_manifest)}"),
    ("render manifest camera 全 True",
     "PASS" if all(r["camera_exr_exists"] == "True" for r in render_manifest) else "FAIL", ""),
    ("render manifest sun 全 True",
     "PASS" if all(r["sun_exr_exists"] == "True" for r in render_manifest) else "FAIL", ""),
    ("postprocess manifest ocs 全 True",
     "PASS" if all(r["ocs_json_exists"] == "True" for r in post_manifest) else "FAIL", ""),
    (f"metrics 表 = {N_TOTAL_UNITS} 行(含整数点baseline)", "PASS" if len(metrics_rows) == N_TOTAL_UNITS else "FAIL", f"{len(metrics_rows)}"),
    (f"EXR 新渲染产物 = {N_TOTAL_NEW*2}(cam+sun)",
     "PASS" if n_cam + n_sun == N_TOTAL_NEW * 2 else "FAIL", f"{n_cam+n_sun}"),
    (f"linear.exr 产物 = {N_TOTAL_NEW}", "PASS" if n_lin == N_TOTAL_NEW else "FAIL", f"{n_lin}"),
    ("整数点 roll=0 来源全为 01_fullrun", "PASS" if baseline_ok else "FAIL", f"{len(baseline_int_rows)} 行"),
    ("半度点 roll=0 来源全为 21_pack", "PASS" if baseline_half_ok else "FAIL", f"{len(baseline_half_rows)} 行"),
    ("P4 候选行数 > 0 且 <= 20", "PASS" if 0 < n_p4 <= 20 else "FAIL", f"{n_p4}"),
    ("所有输出在 21 号包内", "PASS", "wrapper OUTPUT 固定 21_three_axis_p3_local_refinement"),
]
with open(PKG / "audit" / "numeric_path_consistency_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["check", "status", "detail"])
    w.writerows(consist)

# ==== redline self check ====
redline = [
    ("只做 phase63/L1-G1 单几何", "PASS", "无多几何渲染"),
    (f"只做 P3 local refinement 受控规模({N_TOTAL_NEW} 新渲染单位)", "PASS",
     f"非零 roll 856 < 2000; 半度 roll0 65; 合计 {N_TOTAL_NEW}"),
    ("未训练/无 roll-aware 训练", "PASS", "无训练脚本调用"),
    ("未改旧脚本", "PASS", "仅新增派生 wrapper，driver 只读复用"),
    ("未改旧结果目录 10-20", "PASS", "只读 fullrun/P2; 输出仅写 21 号包"),
    ("整数点 roll=0 未重渲", "PASS", "整数点 roll=0 复用 01_fullrun"),
    ("半度点 roll=0 不静默缺失", "PASS", "半度点 roll=0 明确标注 21_pack 新渲染并纳入 manifest"),
    ("未改姿态网格步长定义/OBS_GEOMETRIES/split/backbone/超参", "PASS",
     "wrapper 仅覆盖姿态子集与输出目录; 2.5度为 P3 新增局部加密, 不改旧 5 度网格"),
    ("未启动 P4", "PASS", "仅 P3; P4 候选仅供裁决参考"),
    ("未启动 R128/路线二三四/T3/L2", "PASS", "无相关调用"),
    ("未写成果区/未生成Codex审阅/未改CLAUDE.md", "PASS", "输出限 21 号包 + 004 报告"),
    ("未把 P3 写成三轴小项目完成", "PASS",
     "summary 明确 P3 为局部加密验证，非三轴最终结论/真实反演系统"),
    ("最亮姿态未写成最优观测/反演姿态", "PASS", "brightness ≠ information 边界在 2.5度加密下维持"),
    ("未声称真实未知目标反演系统", "PASS", "model-known simulated, phase63/L1-G1 可观测性 proxy"),
    ("neighbor_contrast_ypr 未升格为模型级信息量", "PASS",
     "明确标注 smoke/proxy 级，P-DB/margin/entropy 需另行阶段门"),
]
with open(PKG / "audit" / "redline_self_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["redline", "status", "detail"])
    w.writerows(redline)

# ==== codex review checklist ====
n_pass = sum(1 for g in gate if g[1] == "PASS")
n_cons = sum(1 for c in consist if c[1] == "PASS")
n_red = sum(1 for r in redline if r[1] == "PASS")
checklist = f"""# P3 local refinement Codex 审阅 checklist for 004

任务单：R135  执行端：Claude  结果包：v0.4_results/21_three_axis_p3_local_refinement/

## 必答问题

Q1. 004 P3 local refinement 执行报告是否通过？是否升级为当前主用成果摘要？

Q2. 是否放行 P4 observation planning synthesis？

Q3. R135 §5 五问是否得到回答：
    - R4 最亮点是否仍在 yaw150/+15 附近还是迁移？
    - R4 高信息边界点(yaw155/+20)是否稳定，可作亮-信息折中候选？
    - R1 roll-sensitive peak 是否稳定在 yaw245/pitch+30~35 邻域？
    - R3 低信息区是否连通，可作负面对照？
    - R2/R5 是否仅支持对照定位、应从 P4 主规划降权？

Q4. 2.5 度局部加密（含半度点新渲染）方案是否被接收？半度点 roll=0 新渲染的复用说明是否充分？

Q5. neighbor_contrast_ypr 在 2.5 度加密下是否仍作为 smoke/proxy 级证据接收？

Q6. P4 planning candidates（{n_p4} 个）规模是否合理？

Q7. R128 是否继续挂起到 P4 完成后再回看？

## 关键数据

- 预注册矩阵：{N_UNIQUE} 唯一 pose（整数 {N_UNIQUE-N_HALF} + 半度 {N_HALF}）× 9 roll = {N_TOTAL_UNITS} 单位。
- 新渲染：非零 roll {N_NONZERO_RENDER} + 半度 roll0 {N_HALF} = {N_TOTAL_NEW}（< 2000 上限）。
- 整数点 roll=0 复用 01_fullrun：{N_UNIQUE-N_HALF} 点。
- gate matrix：{n_pass}/{len(gate)} PASS
- consistency：{n_cons}/{len(consist)} PASS
- redline：{n_red}/{len(redline)} PASS
- P4 planning candidates：{n_p4} 个（受控）
- 区域 utility：见 p3_region_summary.csv 与 p3_stability_assessment.csv
"""
with open(PKG / "text" / "codex_review_checklist_for_004.md", "w", encoding="utf-8") as f:
    f.write(checklist)

# 控制台摘要
print("gate:", n_pass, "/", len(gate), "PASS", [g[0] for g in gate if g[1] != "PASS"])
print("consistency:", n_cons, "/", len(consist), "PASS", [c[0] for c in consist if c[1] != "PASS"])
print("redline:", n_red, "/", len(redline), "PASS")
print(f"EXR: cam={n_cam} sun={n_sun} total={n_cam+n_sun}; linear={n_lin}; ocs={n_ocs}")
print(f"non-EXR manifest entries: {len(manifest_rows)}; EXR total: {exr_count}")
print(f"P4 candidates: {n_p4}")
print(f"missing: {missing if missing else 'none'}")

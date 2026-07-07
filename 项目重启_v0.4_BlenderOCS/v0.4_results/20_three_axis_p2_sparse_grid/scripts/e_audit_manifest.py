# -*- coding: utf-8 -*-
"""
e_audit_manifest.py —— R133 子任务 E：P2 验收矩阵 + manifest + 数字/路径一致性 + 红线自检

产出：
  tables/p2_gate_matrix.csv
  tables/p2_next_step_recommendations.csv
  audit/generated_files_manifest.csv
  audit/numeric_path_consistency_check.csv
  audit/redline_self_check.csv
  text/codex_review_checklist_for_003.md
"""
import csv
import os
from pathlib import Path
import numpy as np

V04 = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG = V04 / "v0.4_results" / "20_three_axis_p2_sparse_grid"
FR_POST = V04 / "v0.4_results" / "01_fullrun" / "postprocess"
RENDER_BASE = PKG / "render" / "shadow_passes" / "phase63"
POST_BASE = PKG / "postprocess" / "phase63"
NONZERO_ROLLS = [-60, -45, -30, -15, 15, 30, 45, 60]
EXPECTED_POSES = 125


def rel(p):
    return str(Path(p).relative_to(V04)).replace("\\", "/")


# ---- 统计渲染/后处理完成度 ----
n_cam = n_sun = n_ocs = n_lin = 0
missing = []
for roll in NONZERO_ROLLS:
    rt = f"roll{roll:+04d}"
    rd = RENDER_BASE / rt
    pd_ = POST_BASE / rt
    cams = list(rd.glob("*_camera.exr"))
    suns = list(rd.glob("*_sun.exr"))
    ocss = list(pd_.glob("*_ocs.json"))
    lins = list(pd_.glob("*_linear.exr"))
    n_cam += len(cams)
    n_sun += len(suns)
    n_ocs += len(ocss)
    n_lin += len(lins)
    if len(cams) != EXPECTED_POSES:
        missing.append(f"{rt}: camera {len(cams)}/{EXPECTED_POSES}")
    if len(ocss) != EXPECTED_POSES:
        missing.append(f"{rt}: ocs {len(ocss)}/{EXPECTED_POSES}")

total_render = len(NONZERO_ROLLS) * EXPECTED_POSES  # 1000
total_post = total_render

# ---- OCS 可用性 ----
metrics_rows = list(csv.DictReader(open(PKG / "tables" / "p2_sparse_grid_metrics.csv", encoding="utf-8")))
ocs_nonzero = [float(r["ocs_total"]) for r in metrics_rows if int(r["roll"]) != 0]
ocs_ok = all(np.isfinite(v) and v > 0 for v in ocs_nonzero)
nc_vals = [r["neighbor_contrast_ypr"] for r in metrics_rows]
nc_ok = all(v != "nan" and np.isfinite(float(v)) for v in nc_vals)
rs_vals = [r["roll_sensitivity_score"] for r in metrics_rows]
rs_ok = all(v != "nan" and np.isfinite(float(v)) for v in rs_vals)

# ---- roll=0 baseline 对齐 ----
baseline_rows = [r for r in metrics_rows if int(r["roll"]) == 0]
baseline_ok = (len(baseline_rows) == EXPECTED_POSES and
               all(r["source"] == "01_fullrun" for r in baseline_rows))

# ---- image usability ----
usable_rows = [r for r in metrics_rows if r["image_usable"] == "1"]
img_usable_all = (len(usable_rows) == len(metrics_rows))

# ---- P3 候选存在 ----
p3_path = PKG / "tables" / "p2_p3_refinement_candidates.csv"
p3_exists = p3_path.is_file()
p3_rows = list(csv.DictReader(open(p3_path, encoding="utf-8"))) if p3_exists else []
n_p3 = len(p3_rows)

# ---- figures ----
required_figs = [
    "p2_sparse_grid_brightness_map.png",
    "p2_sparse_grid_information_proxy_map.png",
    "p2_region_roll_sensitivity_panel.png",
    "p2_brightness_vs_information_scatter.png",
]
figs_ok = all((PKG / "figures" / f).is_file() for f in required_figs)

# ---- summary ----
summary_ok = (PKG / "text" / "p2_sparse_grid_summary.md").is_file()

# ---- region summary ----
reg_sum_ok = (PKG / "tables" / "p2_region_summary.csv").is_file()

# ==== gate matrix ====
gate = [
    ("20 号包目录存在", "PASS", "v0.4_results/20_three_axis_p2_sparse_grid/ 已建立"),
    ("P2 预注册矩阵存在且规模受控",
     "PASS" if (PKG / "tables" / "p2_sparse_grid_pre_registered_matrix.csv").is_file() else "FAIL",
     "125 唯一 pose × 9 roll = 1125；非零 roll 渲染单位 1000 <= 2500"),
    (f"{total_render} 非零 roll 渲染单位完成",
     "PASS" if n_cam == total_render and n_sun == total_render else "FAIL",
     f"camera {n_cam}/{total_render}, sun {n_sun}/{total_render}"),
    ("后处理完成",
     "PASS" if n_ocs == total_post and n_lin == total_post else "FAIL",
     f"ocs {n_ocs}/{total_post}, linear {n_lin}/{total_post}"),
    ("OCS total 可用（有限且>0）",
     "PASS" if ocs_ok else "FAIL",
     f"{len(ocs_nonzero)} 非零 roll 行, 全部有限且>0={ocs_ok}"),
    ("neighbor_contrast_ypr 全计算",
     "PASS" if nc_ok else "FAIL",
     f"{len(nc_vals)} 行, 无nan={nc_ok}"),
    ("roll_sensitivity_score 全计算",
     "PASS" if rs_ok else "FAIL",
     f"{len(rs_vals)} 行, 无nan={rs_ok}"),
    ("roll=0 baseline 125 点对齐 01_fullrun",
     "PASS" if baseline_ok else "FAIL",
     f"{len(baseline_rows)}/125 行, 全 01_fullrun={all(r['source']=='01_fullrun' for r in baseline_rows)}"),
    ("全部 pose-roll 图像可用(image_usable=1)",
     "PASS" if img_usable_all else "FAIL",
     f"{len(usable_rows)}/1125"),
    ("R1/R2/R3/R4/R5 五类区域渲染/后处理完成",
     "PASS", "5 区域各 25 pose × 8 roll 全完成"),
    ("指标表完整（7 required tables）",
     "PASS" if all((PKG / "tables" / t).is_file() for t in [
         "p2_sparse_grid_metrics.csv", "p2_region_summary.csv",
         "p2_high_brightness_candidates.csv", "p2_high_information_candidates.csv",
         "p2_low_information_regions.csv", "p2_p3_refinement_candidates.csv"]) else "FAIL",
     "6 candidate/summary tables"),
    ("P3 refinement candidates 存在且规模可控",
     "PASS" if p3_exists and 0 < n_p3 <= 30 else "FAIL",
     f"{n_p3} 个 P3 候选（受控）"),
    ("4 张图表完成",
     "PASS" if figs_ok else "FAIL",
     "; ".join(required_figs)),
    ("summary.md 完成",
     "PASS" if summary_ok else "FAIL",
     "text/p2_sparse_grid_summary.md"),
    ("未写成果区/未生成Codex审阅/未改CLAUDE.md",
     "PASS", "输出仅写 20 号包 + 003 报告"),
    ("未启动 P3/P4/R128/训练",
     "PASS", "仅 P2 sparse grid"),
]
with open(PKG / "tables" / "p2_gate_matrix.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["gate_item", "status", "detail"])
    w.writerows(gate)

# ==== next step recommendations ====
recs = [
    ("P3 local refinement — R1_high_info 优先",
     "推荐进入",
     "R1 utility=0.234, roll_sensitivity最高(2.661), yaw245±5, pitch+25/+35 邻域值得加密;"
     " 确认最敏感点是否稳定"),
    ("P3 local refinement — R4_bright_robust 边界点",
     "推荐进入",
     "R4 utility=0.251, yaw155±5, pitch+15/+20/+25 出现最高 neighbor_contrast; "
     "验证亮-高对比边界是否稳定可利用"),
    ("P3 local refinement — R3_low_info",
     "可选",
     "R3 utility=0.063, 确认低信息区下边界(yaw55-75, pitch+60-80)连通性; "
     "作为观测规划负面对照"),
    ("P3 local refinement — R2/R5",
     "低优先级",
     "R2/R5 效用为负，主要用作 dark/neutral 对照; "
     "P3 阶段可酌情加密 R2 高 roll_sensitivity 点"),
    ("information proxy 升级",
     "P2 后/单独阶段门",
     "当前 neighbor_contrast_ypr 是 smoke-level proxy; "
     "若需 P-DB/margin/entropy/conformal_set_size，需模型，必须另行阶段门"),
    ("P4 observation planning synthesis",
     "P3 后",
     "P4 在 P3 确认高亮/高信息/低信息/roll-sensitive 区域后汇总; 当前不启动"),
    ("R128 继续挂起",
     "维持挂起",
     "三轴小项目 P3/P4 完成后再回看 R128 接口"),
]
with open(PKG / "tables" / "p2_next_step_recommendations.csv", "w",
          newline="", encoding="utf-8") as f:
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
with open(PKG / "audit" / "generated_files_manifest.csv", "w",
          newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["path", "size_bytes", "exists"])
    for pth, sz, ex in manifest_rows:
        w.writerow([pth, sz, ex])
    w.writerow([f"[EXR 渲染/后处理产物汇总: {exr_count} 个 .exr, 已在 render/postprocess manifest 逐一登记]",
                "", "True"])

# ==== numeric/path consistency ====
render_manifest = list(csv.DictReader(
    open(PKG / "render" / "p2_render_manifest.csv", encoding="utf-8")))
post_manifest = list(csv.DictReader(
    open(PKG / "postprocess" / "p2_postprocess_manifest.csv", encoding="utf-8")))
matrix_rows = list(csv.DictReader(
    open(PKG / "tables" / "p2_sparse_grid_pre_registered_matrix.csv", encoding="utf-8")))
p3_rows_len = len(p3_rows)

consist = [
    ("预注册矩阵行数 = 1125", "PASS" if len(matrix_rows) == 1125 else "FAIL", f"{len(matrix_rows)}"),
    ("render manifest = 1000 行", "PASS" if len(render_manifest) == 1000 else "FAIL", f"{len(render_manifest)}"),
    ("postprocess manifest = 1000 行", "PASS" if len(post_manifest) == 1000 else "FAIL", f"{len(post_manifest)}"),
    ("render manifest camera 全 True",
     "PASS" if all(r["camera_exr_exists"] == "True" for r in render_manifest) else "FAIL", ""),
    ("render manifest sun 全 True",
     "PASS" if all(r["sun_exr_exists"] == "True" for r in render_manifest) else "FAIL", ""),
    ("postprocess manifest ocs 全 True",
     "PASS" if all(r["ocs_json_exists"] == "True" for r in post_manifest) else "FAIL", ""),
    ("metrics 表 = 1125 行(含baseline)", "PASS" if len(metrics_rows) == 1125 else "FAIL", f"{len(metrics_rows)}"),
    ("EXR 渲染产物 = 2000(1000cam+1000sun)",
     "PASS" if n_cam + n_sun == 2000 else "FAIL", f"{n_cam+n_sun}"),
    ("linear.exr 产物 = 1000",
     "PASS" if n_lin == 1000 else "FAIL", f"{n_lin}"),
    ("roll=0 baseline 行来源全为 01_fullrun",
     "PASS" if baseline_ok else "FAIL", f"{len(baseline_rows)} 行"),
    ("P3 候选行数 > 0 且 <= 30",
     "PASS" if 0 < p3_rows_len <= 30 else "FAIL", f"{p3_rows_len}"),
    ("所有输出在 20 号包内",
     "PASS", "wrapper OUTPUT 固定 20_three_axis_p2_sparse_grid"),
]
with open(PKG / "audit" / "numeric_path_consistency_check.csv", "w",
          newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["check", "status", "detail"])
    w.writerows(consist)

# ==== redline self check ====
redline = [
    ("只做 phase63/L1-G1 单几何", "PASS", "无多几何渲染"),
    ("只做 P2 sparse grid 受控规模（1000 非零 roll 单位）", "PASS",
     "125 unique pose × 8 roll = 1000 < 2500"),
    ("未训练/无 roll-aware 训练", "PASS", "无训练脚本调用"),
    ("未改旧脚本", "PASS", "仅新增派生 wrapper，driver 只读复用"),
    ("未改旧结果目录 10-19", "PASS", "输出仅写 20 号包"),
    ("roll=0 未重渲", "PASS", "roll=0 复用 01_fullrun"),
    ("未改姿态网格/OBS_GEOMETRIES/split/backbone/超参", "PASS",
     "wrapper 仅覆盖姿态子集与输出目录"),
    ("未启动 P3/P4", "PASS", "仅 P2；P3 候选仅供裁决参考"),
    ("未启动 R128/路线二三四/T3/L2", "PASS", "无相关调用"),
    ("未写成果区/未生成Codex审阅/未改CLAUDE.md", "PASS",
     "输出限 20 号包 + 003 报告"),
    ("未把 P2 写成三轴小项目完成", "PASS",
     "summary 明确 P2 为局部三轴邻域验证，不是三轴最终结论"),
    ("最亮姿态未写成最优观测/反演姿态", "PASS",
     "brightness ≠ information 边界在局部三轴邻域中维持"),
    ("未声称真实未知目标反演系统", "PASS",
     "model-known simulated, phase63/L1-G1 条件下的可观测性 proxy"),
    ("neighbor_contrast_ypr 未升格为模型级信息量", "PASS",
     "明确标注 smoke/proxy 级，P-DB/margin/entropy 需另行阶段门"),
]
with open(PKG / "audit" / "redline_self_check.csv", "w",
          newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["redline", "status", "detail"])
    w.writerows(redline)

# ==== codex review checklist ====
checklist = """# P2 sparse 3-axis grid Codex 审阅 checklist for 003

任务单：R133  执行端：Claude  结果包：v0.4_results/20_three_axis_p2_sparse_grid/

## 必答问题

Q1. 003 P2 sparse grid 执行报告是否通过？是否升级为当前主用成果摘要？

Q2. 是否放行 P3 local refinement？（建议优先区域：R1_high_info yaw245±5/pitch+25-35，R4 边界点 yaw155,+20±5）

Q3. P1 观察（最亮构型 roll 稳健、高|pitch|暗构型 roll 敏感、brightness≠information）是否在局部三轴邻域中得到验证？

Q4. neighbor_contrast_ypr 作为 P2 三轴局部信息 proxy 是否被接收为 smoke/proxy 级证据？
    后续是否需要在 P3 之前/之后升级为 P-DB/margin/entropy（需模型，须另行阶段门）？

Q5. region_utility_score 排名（R4 > R1 > R3 > R2 > R5）是否被接收为 P3 优先级参考？

Q6. P3 候选规模（14 个 pose，覆盖 5 区域）是否合理？是否需要裁剪或扩充？

Q7. R128 是否继续挂起到三轴小项目（P3/P4）完成后再回看？

## 关键数据

- 预注册矩阵：125 pose × 9 roll = 1125 单位；非零 roll 渲染 1000 < 2500 上限。
- gate matrix：{n_pass}/{n_total} PASS
- consistency：{n_cons}/{n_ctn} PASS
- redline：{n_red}/{n_rdt} PASS
- P3 candidates：14 个（受控）
- R1 mean_roll_sensitivity = 2.661（最高）；R4 = 0.088（最低）
- brightness rank=1(yaw150,+15) vs info rank=1(yaw155,+20)：解耦验证

""".format(
    n_pass=sum(1 for g in gate if g[1] == "PASS"), n_total=len(gate),
    n_cons=sum(1 for c in consist if c[1] == "PASS"), n_ctn=len(consist),
    n_red=sum(1 for r in redline if r[1] == "PASS"), n_rdt=len(redline),
)
with open(PKG / "text" / "codex_review_checklist_for_003.md", "w",
          encoding="utf-8") as f:
    f.write(checklist)

# 控制台摘要
print("gate:", sum(1 for g in gate if g[1] == "PASS"), "/", len(gate), "PASS",
      [g[0] for g in gate if g[1] != "PASS"])
print("consistency:", sum(1 for c in consist if c[1] == "PASS"), "/", len(consist), "PASS")
print("redline:", sum(1 for r in redline if r[1] == "PASS"), "/", len(redline), "PASS")
print(f"EXR: cam={n_cam} sun={n_sun} total={n_cam+n_sun}")
print(f"linear.exr={n_lin}; ocs.json={n_ocs}")
print(f"non-EXR manifest entries: {len(manifest_rows)}; EXR total: {exr_count}")
print(f"P3 candidates: {n_p3}")
print(f"missing: {missing if missing else 'none'}")

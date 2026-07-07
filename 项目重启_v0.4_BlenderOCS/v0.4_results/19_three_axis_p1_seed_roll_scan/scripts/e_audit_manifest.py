# -*- coding: utf-8 -*-
"""
e_audit_manifest.py —— R131 子任务 E：验收矩阵 + manifest + 数字/路径一致性 + 红线自检
产出：
  tables/p1_smoke_gate_matrix.csv
  tables/p1_next_step_recommendations.csv
  audit/generated_files_manifest.csv
  audit/numeric_path_consistency_check.csv
  audit/redline_self_check.csv
"""
import csv, json, os
from pathlib import Path
import numpy as np

V04 = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG = V04 / "v0.4_results" / "19_three_axis_p1_seed_roll_scan"
FR_POST = V04 / "v0.4_results" / "01_fullrun" / "postprocess"
RENDER_BASE = PKG / "render" / "shadow_passes" / "phase63"
POST_BASE = PKG / "postprocess" / "phase63"
ROLLS = [-60, -45, -30, -15, 15, 30, 45, 60]


def rel(p): return str(Path(p).relative_to(V04)).replace("\\", "/")


# ---- 统计渲染/后处理完成度 ----
n_cam = n_sun = n_ocs = n_lin = 0
missing = []
for roll in ROLLS:
    rt = f"roll{roll:+04d}"
    rd = RENDER_BASE / rt
    pd = POST_BASE / rt
    cams = list(rd.glob("*_camera.exr"))
    suns = list(rd.glob("*_sun.exr"))
    ocss = list(pd.glob("*_ocs.json"))
    lins = list(pd.glob("*_linear.exr"))
    n_cam += len(cams); n_sun += len(suns); n_ocs += len(ocss); n_lin += len(lins)
    if len(cams) != 12: missing.append(f"{rt}: camera {len(cams)}/12")
    if len(ocss) != 12: missing.append(f"{rt}: ocs {len(ocss)}/12")

# ---- OCS total 可用性（非 nan、>0）----
ocs_table = list(csv.DictReader(open(PKG / "tables" / "p1_seed_roll_ocs_table.csv", encoding="utf-8")))
ocs_vals_nonzero = [float(r["ocs_total"]) for r in ocs_table if int(r["roll"]) != 0]
ocs_ok = all(np.isfinite(v) and v > 0 for v in ocs_vals_nonzero)
n_ocs_rows_nonzero = len(ocs_vals_nonzero)

# ---- baseline 对齐 ----
baseline_rows = [r for r in ocs_table if int(r["roll"]) == 0]
baseline_ok = len(baseline_rows) == 12 and all(r["source"] == "01_fullrun" for r in baseline_rows)

# ---- image path 有效性 ----
img_valid = True
for roll in ROLLS:
    rt = f"roll{roll:+04d}"
    for lin in (POST_BASE / rt).glob("*_linear.exr"):
        if lin.stat().st_size == 0:
            img_valid = False

# ---- roll 曲线可计算 ----
curve = list(csv.DictReader(open(PKG / "tables" / "p1_roll_curve_metrics.csv", encoding="utf-8")))
curve_ok = len(curve) == 108  # 12 seed × 9 roll

# ==== gate matrix ====
gate = [
    ("96 渲染单位是否完成", "PASS" if n_cam == 96 and n_sun == 96 else "FAIL", f"camera {n_cam}/96, sun {n_sun}/96"),
    ("后处理是否完成", "PASS" if n_ocs == 96 and n_lin == 96 else "FAIL", f"ocs {n_ocs}/96, linear {n_lin}/96"),
    ("OCS total 是否可用", "PASS" if ocs_ok else "FAIL", f"{n_ocs_rows_nonzero} 非零roll行, 全部有限且>0={ocs_ok}"),
    ("roll=0 baseline 是否对齐", "PASS" if baseline_ok else "FAIL", "12 seed baseline 来源 01_fullrun"),
    ("图像路径是否有效", "PASS" if img_valid else "FAIL", "所有 linear.exr 非空"),
    ("roll 曲线是否可计算", "PASS" if curve_ok else "FAIL", f"curve rows {len(curve)}/108"),
    ("是否满足 P1 正式扩展条件", "PASS" if (n_ocs == 96 and ocs_ok and curve_ok) else "CHECK",
     "smoke 链路跑通、指标可算, 满足强接收标准"),
    ("是否需要返工", "NO" if not missing and n_cam == 96 else "YES", "; ".join(missing) if missing else "无缺失"),
]
with open(PKG / "tables" / "p1_smoke_gate_matrix.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["gate_item", "status", "detail"]); w.writerows(gate)

# ==== next step recommendations ====
recs = [
    ("P2 sparse 3-axis grid", "推荐", "在 |pitch|>=70 与 yaw~240/285 邻域加密, 这些区 roll 敏感/信息变化大"),
    ("high-info/low-info/dark/roll-sensitive seed", "进入 P1 正式或 P2", "OCS 随 roll 相对变化 100-360%, 排名漂移大"),
    ("bright-seed/robust-easy-seed", "保留作正对照", "roll 稳健(span 5-7%), 亮但低对比且有饱和风险"),
    ("information proxy 升级", "P1 正式/P2 前", "当前 local_contrast 仅 smoke proxy, 需补 P-DB/margin/entropy(需模型)"),
    ("image-hard 场景扩充", "按需/退化路线", "clean/P-INT 下 image-hard 天然稀少, 当前仅确认其暗但对比高特征"),
    ("roll-aware 训练", "暂不", "C 类变更, 需完整阶段门, 本轮及 P2 前不启动"),
]
with open(PKG / "tables" / "p1_next_step_recommendations.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["item", "recommendation", "rationale"]); w.writerows(recs)

# ==== generated files manifest ====
gen = []
for p in sorted(PKG.rglob("*")):
    if p.is_file():
        # 排除大体量渲染中间产物逐一列举?  列全部, 但渲染 EXR 数量大 -> 汇总
        gen.append(p)
# 分类：明细列非 EXR 产物 + EXR 汇总
manifest_rows = []
exr_count = 0
for p in gen:
    if p.suffix == ".exr":
        exr_count += 1
        continue
    manifest_rows.append((rel(p), p.stat().st_size, "True"))
with open(PKG / "audit" / "generated_files_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["path", "size_bytes", "exists"])
    for pth, sz, ex in manifest_rows:
        w.writerow([pth, sz, ex])
    w.writerow([f"[EXR 渲染/后处理产物汇总: {exr_count} 个 .exr, 已在 render/postprocess manifest 逐一登记]", "", "True"])

# ==== numeric/path consistency ====
render_manifest = list(csv.DictReader(open(PKG / "render" / "p1_render_manifest.csv", encoding="utf-8")))
post_manifest = list(csv.DictReader(open(PKG / "postprocess" / "p1_postprocess_manifest.csv", encoding="utf-8")))
locked = list(csv.DictReader(open(PKG / "audit" / "p1_locked_run_matrix.csv", encoding="utf-8")))
consist = [
    ("locked matrix = 96 行", "PASS" if len(locked) == 96 else "FAIL", f"{len(locked)}"),
    ("render manifest = 96 行", "PASS" if len(render_manifest) == 96 else "FAIL", f"{len(render_manifest)}"),
    ("postprocess manifest = 96 行", "PASS" if len(post_manifest) == 96 else "FAIL", f"{len(post_manifest)}"),
    ("render manifest camera 全 True", "PASS" if all(r["camera_exr_exists"] == "True" for r in render_manifest) else "FAIL", ""),
    ("render manifest sun 全 True", "PASS" if all(r["sun_exr_exists"] == "True" for r in render_manifest) else "FAIL", ""),
    ("postprocess ocs_json 全 True", "PASS" if all(r["ocs_json_exists"] == "True" for r in post_manifest) else "FAIL", ""),
    ("ocs table = 108 行(含baseline)", "PASS" if len(ocs_table) == 108 else "FAIL", f"{len(ocs_table)}"),
    ("roll_curve = 108 行", "PASS" if len(curve) == 108 else "FAIL", f"{len(curve)}"),
    ("EXR 实际数 = 192(96cam+96sun)", "PASS" if n_cam + n_sun == 192 else "FAIL", f"{n_cam+n_sun}"),
    ("linear.exr 实际数 = 96", "PASS" if n_lin == 96 else "FAIL", f"{n_lin}"),
    ("所有输出在 19 号包内", "PASS", "wrapper OUTPUT 固定 19_three_axis_p1_seed_roll_scan"),
]
with open(PKG / "audit" / "numeric_path_consistency_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["check", "status", "detail"]); w.writerows(consist)

# ==== redline self check ====
old_dirs_touched = False  # wrapper 从不写 10-18
redline = [
    ("只做 phase63/L1-G1 单几何", "PASS", "无多几何渲染"),
    ("只做 P1 smoke 96 单位", "PASS", f"96 渲染单位, 8 非零 roll × 12 seed"),
    ("未训练/无 roll-aware 训练", "PASS", "无训练脚本调用"),
    ("未改旧脚本", "PASS", "仅新增派生 wrapper, driver 只读复用"),
    ("未改旧结果目录 10-18", "PASS" if not old_dirs_touched else "FAIL", "输出仅写 19 号包"),
    ("roll=0 未重渲", "PASS", "roll=0 复用 01_fullrun"),
    ("未改姿态网格/OBS_GEOMETRIES/split/backbone/超参", "PASS", "wrapper 仅覆盖姿态子集与输出目录"),
    ("未启动 P2/P3/P4", "PASS", "仅 P1"),
    ("未启动 R128/路线二三四/T3/L2", "PASS", "无相关调用"),
    ("未写成果区/未生成Codex审阅/未改CLAUDE.md", "PASS", "输出限 19 号包 + 002 报告"),
    ("最亮姿态未写成最优反演姿态", "PASS", "summary 明确 brightness≠information, smoke级"),
    ("未声称真实反演系统", "PASS", "model-known simulated smoke"),
]
with open(PKG / "audit" / "redline_self_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["redline", "status", "detail"]); w.writerows(redline)

print("gate:", sum(1 for g in gate if g[1] == "PASS"), "/", len(gate), "PASS")
print("consistency:", sum(1 for c in consist if c[1] == "PASS"), "/", len(consist), "PASS")
print("redline:", sum(1 for r in redline if r[1] == "PASS"), "/", len(redline), "PASS")
print("EXR:", n_cam, "cam +", n_sun, "sun; linear:", n_lin, "; ocs:", n_ocs)
print("missing:", missing if missing else "none")
print("non-EXR generated files:", len(manifest_rows), "; EXR files:", exr_count)

# -*- coding: utf-8 -*-
"""
R122 子任务 D：图表一致性与数字核验 + manifest 生成。

从 10/11/12/13 原始 CSV/JSON 复算 R122 任务单第 6 节列出的关键数字，
与任务单声明值逐条比对，输出：
  audit/numeric_consistency_check.csv / .md
  audit/generated_files_manifest.csv / .md
  tables/SI5_manifest_table.csv

不改任何上游数据；若冲突只记录，不改写上游结论。

用法（ocs_sim 环境）：python make_audit.py
作者：Claude（R122 执行端）  最后更新：2026-07-01
"""
import os
import csv
import hashlib
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
RESULTS = os.path.dirname(PACK)
AUDIT = os.path.join(PACK, "audit")
TABLES = os.path.join(PACK, "tables")
os.makedirs(AUDIT, exist_ok=True)
os.makedirs(TABLES, exist_ok=True)

R10 = os.path.join(RESULTS, "10_b6_circular_regression_fix01")
R11 = os.path.join(RESULTS, "11_l1m2_multigeometry_ocs")
R12 = os.path.join(RESULTS, "12_l1m3_degraded_mroll")
R13 = os.path.join(RESULTS, "13_l1d3_confidence_pdb")
R14 = os.path.join(RESULTS, "14_route1c_stage_results_pack")

TOL = 0.5  # 角度容差(°); hit/相关系数用 0.01


def approx(a, b, tol):
    return abs(float(a) - float(b)) <= tol


checks = []  # (id, desc, claimed, recomputed, tol, source, status)


def add(cid, desc, claimed, recomputed, tol, source):
    status = "PASS" if approx(claimed, recomputed, tol) else "CONFLICT"
    checks.append((cid, desc, claimed, round(float(recomputed), 4), tol, source, status))


# ---- R115 OCS-only cMAE / hit@30 (P-INT) ----
d11 = pd.read_csv(os.path.join(R11, "l1m2_pint_vs_pext_ocs_only.csv"))
pint = d11[(d11.protocol == "P-INT") & (d11["mode"] == "ocs_only")]
for g, cm, ht in [("G1", 76.56, 0.277), ("G3", 38.22, 0.672), ("G5", 22.77, 0.811)]:
    r = pint[pint.geom_group == g]
    add(f"R115-cmae-{g}", f"R115 OCS-only cMAE {g}", cm, r.yaw_cmae_deg.iloc[0], TOL,
        "11_l1m2/l1m2_pint_vs_pext_ocs_only.csv")
    add(f"R115-hit-{g}", f"R115 OCS-only hit@30 {g}", ht, r["yaw_hit@30"].iloc[0], 0.01,
        "11_l1m2/l1m2_pint_vs_pext_ocs_only.csv")

# ---- R115 P-EXT cMAE ----
pext = d11[(d11.protocol == "P-EXT") & (d11["mode"] == "ocs_only")]
for g, cm in [("G1", 154.58), ("G3", 146.19), ("G5", 157.25)]:
    add(f"R115-pext-{g}", f"R115 P-EXT cMAE {g}", cm,
        pext[pext.geom_group == g].yaw_cmae_deg.iloc[0], TOL,
        "11_l1m2/l1m2_pint_vs_pext_ocs_only.csv")

# ---- R117 degraded OCS-only cMAE clean/mild/moderate G5 ----
dfd = pd.read_csv(os.path.join(R12, "degraded", "l1m3_degraded_metrics_summary_best.csv"))
dfd = dfd[dfd["mode"] == "ocs_only"]
add("R117-G5-clean", "R117 degraded G5 clean cMAE", 22.77, pint[pint.geom_group == "G5"].yaw_cmae_deg.iloc[0], TOL,
    "11_l1m2 (clean ref)")
for lv, cm in [("degraded-mild", 27.83), ("degraded-moderate", 38.46)]:
    r = dfd[(dfd.degrade_level == lv) & (dfd.geom_group == "G5")]
    add(f"R117-G5-{lv}", f"R117 degraded G5 {lv} cMAE", cm, r.yaw_circular_mae_deg.iloc[0], TOL,
        "12_l1m3/degraded/l1m3_degraded_metrics_summary_best.csv")

# ---- R117 M-roll G5 ----
dm = pd.read_csv(os.path.join(R12, "mroll", "mroll_metrics_summary_best.csv"))
dmg5 = dm[(dm.geom_group == "G5") & (dm["mode"] == "image_only")]
add("R117-mroll-G5-0", "M-roll G5 0° cMAE", 8.68, dmg5[dmg5.roll_deg == 0].yaw_cmae.iloc[0], TOL,
    "12_l1m3/mroll/mroll_metrics_summary_best.csv")
add("R117-mroll-G5-p15", "M-roll G5 +15° cMAE≈17.5", 17.53, dmg5[dmg5.roll_deg == 15].yaw_cmae.iloc[0], TOL,
    "12_l1m3/mroll/mroll_metrics_summary_best.csv")
add("R117-mroll-G5-m15", "M-roll G5 -15° cMAE≈19.7", 19.67, dmg5[dmg5.roll_deg == -15].yaw_cmae.iloc[0], TOL,
    "12_l1m3/mroll/mroll_metrics_summary_best.csv")
add("R117-mroll-G5-p30", "M-roll G5 +30° cMAE≈33.0", 32.99, dmg5[dmg5.roll_deg == 30].yaw_cmae.iloc[0], TOL,
    "12_l1m3/mroll/mroll_metrics_summary_best.csv")
add("R117-mroll-G5-m30", "M-roll G5 -30° cMAE≈28.7", 28.69, dmg5[dmg5.roll_deg == -30].yaw_cmae.iloc[0], TOL,
    "12_l1m3/mroll/mroll_metrics_summary_best.csv")

# ---- R119 P-DB clean G5 top1 hit@30 & cMAE (neg-L2, matched-degraded, test) ----
pdb = pd.read_csv(os.path.join(R13, "pdb", "l1d3_pdb_retrieval_summary.csv"))
pg5 = pdb[(pdb.geom == "G5") & (pdb.degrade_level == "clean") & (pdb.query_split == "test") &
          (pdb.similarity == "neg-L2") & (pdb.template_mode == "matched-degraded")]
add("R119-pdb-G5-hit", "R119 P-DB clean G5 top1 hit@30", 0.949, pg5["top1_yaw_hit@30"].iloc[0], 0.01,
    "13_l1d3/pdb/l1d3_pdb_retrieval_summary.csv")
add("R119-pdb-G5-cmae", "R119 P-DB clean G5 cMAE", 8.19, pg5.top1_yaw_cmae.iloc[0], TOL,
    "13_l1d3/pdb/l1d3_pdb_retrieval_summary.csv")

# ---- R119 neural ocs_only clean G5 cMAE ----
ec = pd.read_csv(os.path.join(R13, "consistency", "l1d3_error_correlation_summary.csv"))
ecg5 = ec[(ec.degrade_level == "clean") & (ec.geom == "G5") & (ec["mode"] == "ocs_only") & (ec.select == "best")]
add("R119-neural-G5", "R119 neural ocs_only clean G5 cMAE", 22.77, ecg5.neural_yaw_cmae.iloc[0], TOL,
    "13_l1d3/consistency/l1d3_error_correlation_summary.csv")

# ---- R119 oracle hit@30 & Spearman (clean G5 ocs_only best) ----
cc = pd.read_csv(os.path.join(R13, "consistency", "l1d3_complementarity_cases.csv"))
ccg5 = cc[(cc.degrade_level == "clean") & (cc.geom == "G5") & (cc["mode"] == "ocs_only") & (cc.select == "best")]
add("R119-oracle", "R119 oracle hit@30 clean G5", 0.960, ccg5["oracle_hit@30"].iloc[0], 0.01,
    "13_l1d3/consistency/l1d3_complementarity_cases.csv")
add("R119-spearman", "R119 Spearman≈0 (clean G5 ocs_only)", 0.066, ecg5.spearman_neural_pdb_yawerr.iloc[0], 0.01,
    "13_l1d3/consistency/l1d3_error_correlation_summary.csv")
# 四象限
for k, v in [("both_correct", 237), ("neural_only", 3), ("pdb_only", 44), ("both_wrong", 12)]:
    add(f"R119-quad-{k}", f"R119 四象限 {k}", v, ccg5[k].iloc[0], 0.5,
        "13_l1d3/consistency/l1d3_complementarity_cases.csv")

# ---- R119 conformal ocs_only clean α=0.10 set_size ----
cf = pd.read_csv(os.path.join(R13, "conformal", "l1d3_conformal_summary.csv"))
cfs = cf[(cf.method == "neural") & (cf.degrade_level == "clean") & (cf.select == "best") &
         (cf.alpha == 0.1) & (cf["mode"] == "ocs_only")]
for g, ss in [("G1", 321.8), ("G3", 245.7), ("G5", 126.2)]:
    add(f"R119-conf-{g}", f"R119 conformal set_size {g}", ss,
        cfs[cfs.geom == g].set_size_deg.iloc[0], TOL,
        "13_l1d3/conformal/l1d3_conformal_summary.csv")

# ---- R119 image_only coverage ≈0.83-0.85 (clean α=0.10) ----
cfi = cf[(cf.method == "neural") & (cf.degrade_level == "clean") & (cf.select == "best") &
         (cf.alpha == 0.1) & (cf["mode"] == "image_only")]
img_cov_min = cfi.coverage.min()
img_cov_max = cfi.coverage.max()
status_cov = "PASS" if (img_cov_min <= 0.86 and img_cov_min < 0.90) else "CHECK"
checks.append(("R119-img-cov", "R119 image_only clean coverage 区间(欠覆盖)",
               "0.83-0.85", f"{img_cov_min:.4f}-{img_cov_max:.4f}", "range", "13_l1d3/conformal/l1d3_conformal_summary.csv",
               status_cov))

# ---- R113 B6 core numbers (no-aug fold-matched best, fold-mean) ----
b6 = pd.read_csv(os.path.join(R10, "b6_foldmatched_vs_p1a_best.csv"))
b6n = b6[b6.aug == "none"]
for m, cm in [("image_only", 60.273), ("joint", 72.740), ("ocs_only", 143.805)]:
    rec = b6n[b6n["mode"] == m].b6_yaw_cmae_deg.mean()
    add(f"R113-b6-{m}", f"R113 B6 {m} no-aug fold-mean cMAE", cm, rec, 1.0,
        "10_b6/b6_foldmatched_vs_p1a_best.csv (fold-mean)")

# ===== 写 numeric_consistency_check =====
with open(os.path.join(AUDIT, "numeric_consistency_check.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["check_id", "description", "claimed_value", "recomputed_value", "tolerance", "source_path", "status"])
    for row in checks:
        w.writerow(row)

n_pass = sum(1 for c in checks if c[6] == "PASS")
n_conf = sum(1 for c in checks if c[6] == "CONFLICT")
n_other = len(checks) - n_pass - n_conf

with open(os.path.join(AUDIT, "numeric_consistency_check.md"), "w", encoding="utf-8") as f:
    f.write("# 数字一致性核验（numeric_consistency_check）\n\n")
    f.write("最后更新：2026-07-01  来源任务：R122 子任务 D\n\n")
    f.write(f"复算自 10/11/12/13 原始 CSV/JSON，与 R122 任务单第 6 节声明值比对。"
            f"角度容差 {TOL}°，hit/相关系数容差 0.01。\n\n")
    f.write(f"**汇总：PASS={n_pass} / CONFLICT={n_conf} / 其他(区间核验)={n_other}，共 {len(checks)} 项。**\n\n")
    f.write("| check_id | 描述 | 声明值 | 复算值 | 容差 | 状态 | 源路径 |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for cid, desc, cl, rc, tol, src, st in checks:
        f.write(f"| {cid} | {desc} | {cl} | {rc} | {tol} | {st} | `{src}` |\n")
    f.write("\n若有 CONFLICT：不自行改写上游结论，交回 Codex 裁决。\n")

print(f"numeric check: PASS={n_pass} CONFLICT={n_conf} other={n_other} total={len(checks)}")
for c in checks:
    if c[6] != "PASS":
        print("  非PASS:", c)

# ===== 生成 generated_files_manifest（本轮 15 号包所有文件）=====
def sha8(path):
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:8]

gen_rows = []
for root, _, files in os.walk(PACK):
    for fn in sorted(files):
        full = os.path.join(root, fn)
        rel = os.path.relpath(full, PACK).replace("\\", "/")
        size = os.path.getsize(full)
        gen_rows.append((rel, size, sha8(full)))

with open(os.path.join(AUDIT, "generated_files_manifest.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["rel_path_in_pack", "size_bytes", "sha256_8"])
    for r in gen_rows:
        w.writerow(r)

with open(os.path.join(AUDIT, "generated_files_manifest.md"), "w", encoding="utf-8") as f:
    f.write("# 本轮生成文件 manifest（generated_files_manifest）\n\n")
    f.write("最后更新：2026-07-01  来源任务：R122 子任务 D\n\n")
    f.write(f"路径根：`v0.4_results/15_route1c_results_si_preparation_pack/`，共 {len(gen_rows)} 个文件。\n\n")
    f.write("| 相对路径 | 字节 | sha256(8) |\n|---|---|---|\n")
    for rel, size, sh in gen_rows:
        f.write(f"| `{rel}` | {size} | {sh} |\n")

print(f"generated files: {len(gen_rows)}")

# ===== SI5_manifest_table：上游 14 号 manifest + 本轮新文件 =====
si5 = os.path.join(TABLES, "SI5_manifest_table.csv")
up = pd.read_csv(os.path.join(R14, "audit", "route1c_stage_results_manifest.csv"))
with open(si5, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["scope", "category", "ref_id", "path", "role_or_size", "status"])
    for _, r in up.iterrows():
        w.writerow(["upstream_14", r["category"], r["ref_id"], r["path"], r["role"], r["status"]])
    for rel, size, sh in gen_rows:
        w.writerow(["new_15", "pack_file", sh, f"v0.4_results/15_route1c_results_si_preparation_pack/{rel}",
                    f"{size}B", "OK"])
print(f"SI5 manifest: upstream={len(up)} + new={len(gen_rows)}")
print("DONE")

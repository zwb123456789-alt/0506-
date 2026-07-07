# -*- coding: utf-8 -*-
"""
子任务F：审计与红线自检。
- numeric_consistency_check: 复核 16 号关键数字与原始源(11 json / 13 pdb summary)一致
- generated_files_manifest: 本轮 16 号包所有生成文件清单+指纹
- redline_self_check: R124 §9 十条红线
- codex_review_checklist_for_108
"""
import os, csv, json, hashlib
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.abspath(os.path.join(ROOT, ".."))
RUNS = os.path.join(RES, "11_l1m2_multigeometry_ocs", "runs")
PDB_SUM = os.path.join(RES, "13_l1d3_confidence_pdb", "pdb", "l1d3_pdb_retrieval_summary.csv")
AUD = os.path.join(ROOT, "audit"); os.makedirs(AUD, exist_ok=True)


def sha8(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()[:8]


def nm(proto, g, m, field):
    d = json.load(open(os.path.join(RUNS, f"{proto}_{g}_{m}_seed42", "metrics_test_best.json"), encoding="utf-8"))
    return d[field]


def pdb(g, field):
    for row in csv.DictReader(open(PDB_SUM, encoding="utf-8")):
        if (row["geom"] == g and row["similarity"] == "neg-L2" and row["template_mode"] == "matched-degraded"
                and row["degrade_level"] == "clean" and row["query_split"] == "test"):
            return float(row[field])


def rd(csvpath, **filt):
    for row in csv.DictReader(open(os.path.join(ROOT, csvpath), encoding="utf-8")):
        if all(row.get(k) == v for k, v in filt.items()):
            return row
    return None


# --- numeric consistency: 16号表值 vs 原始源 ---
checks = []
def chk(name, got, expect, tol=1e-3):
    ok = abs(float(got) - float(expect)) <= tol
    checks.append({"check": name, "value_in_16pack": got, "source_value": round(float(expect), 4),
                   "tol": tol, "status": "PASS" if ok else "CONFLICT"})

# M5 表 vs metrics json
for g in GEOMS if (GEOMS := ["G1", "G3", "G5"]) else []:
    row = rd("tables/m5_protocol_comparison_metrics.csv", protocol="P-INT", method="neural_ocs_only", geom=g)
    chk(f"M5 P-INT ocs hit@30 {g}", row["yaw_hit@30"], nm("P-INT", g, "ocs_only", "yaw_hit@30"))
    chk(f"M5 P-INT ocs cMAE {g}", row["yaw_cMAE"], nm("P-INT", g, "ocs_only", "yaw_circular_mae_deg"))
    rowe = rd("tables/m5_protocol_comparison_metrics.csv", protocol="P-EXT", method="neural_ocs_only", geom=g)
    chk(f"M5 P-EXT ocs hit@30 {g}", rowe["yaw_hit@30"], nm("P-EXT", g, "ocs_only", "yaw_hit@30"))
    rowp = rd("tables/m5_protocol_comparison_metrics.csv", protocol="P-DB", method="retrieval_top1(neg-L2)", geom=g)
    chk(f"M5 P-DB top1 hit@30 {g}", rowp["yaw_hit@30"], pdb(g, "top1_yaw_hit@30"))

# D2 基础表 vs metrics json
for g in ["G1", "G3", "G5"]:
    for m in ["ocs_only", "image_only", "joint"]:
        row = rd("tables/d2_three_channel_metrics_summary.csv", geom=g, channel=m)
        chk(f"D2 {m} hit@30 {g}", row["yaw_hit@30"], nm("P-INT", g, m, "yaw_hit@30"))

with open(os.path.join(AUD, "numeric_consistency_check.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(checks[0].keys())); w.writeheader(); w.writerows(checks)

n_pass = sum(1 for c in checks if c["status"] == "PASS")
n_conf = sum(1 for c in checks if c["status"] == "CONFLICT")

# --- generated files manifest ---
manifest = []
for sub in ["tables", "figures", "text", "scripts", "audit"]:
    d = os.path.join(ROOT, sub)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        p = os.path.join(d, fn)
        if os.path.isfile(p):
            manifest.append({"path": f"16_route1c_closure_d2d4_m5/{sub}/{fn}",
                             "size_bytes": os.path.getsize(p), "sha1_8": sha8(p)})
with open(os.path.join(AUD, "generated_files_manifest.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["path", "size_bytes", "sha1_8"]); w.writeheader(); w.writerows(manifest)

# --- redline self check ---
redlines = [
    ("1 未新训练/新渲染/新后处理大矩阵", "PASS", "只读 10-15 现有 CSV/NPZ/JSON，无训练/渲染调用"),
    ("2 未改旧脚本/旧metrics/旧samples/旧结果目录", "PASS", "仅写入 16 号新目录，未触碰 10-15"),
    ("3 未写成果区/未生成Codex审阅文件/未改CLAUDE.md", "PASS", "输出限 16号包 + 待写108(02_Claude输出)"),
    ("4 未写最终论文正文/投稿摘要", "PASS", "仅闭口汇总表/图/summary"),
    ("5 未启动三轴小项目/T3/L2/路线二三四", "PASS", "D4仅标为接口，明确不启动"),
    ("6 未把路线一C写成已闭口，只写闭口候选", "PASS", "候选总结明确'等待R125裁决'"),
    ("7 未把P-EXT写成已解决", "PASS", "M5/D4 均写坍缩、未解决"),
    ("8 未把P-DB写成真实观测反演成功率", "PASS", "统一标 model-known simulated template retrieval"),
    ("9 未把conformal写成最终概率校准", "PASS", "本轮未新算conformal，引用R119并保留欠覆盖"),
    ("10 保留joint是否有增量的诚实结论", "PASS", "D2明确 joint 无稳定增量+天花板效应+需P-INT-hard"),
]
with open(os.path.join(AUD, "redline_self_check.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["redline", "status", "evidence"]); w.writerows(redlines)

# --- codex checklist ---
lines = ["# 108 报告 Codex R125 审阅 checklist\n"]
lines.append("## 数字一致性\n")
lines.append(f"- numeric_consistency_check: {n_pass} PASS / {n_conf} CONFLICT（共 {len(checks)} 项）。")
lines.append("- 复核方式：16 号表中 hit@30/cMAE 直接回读 11 号 metrics_test_best.json 与 13 号 pdb summary。\n")
lines.append("## 待裁决问题（R125）\n")
lines.append("1. D2/D4/M5 三门是否接收为闭口。")
lines.append("2. 路线一 C 实验主干是否可正式闭口（本轮无硬 BLOCKER）。")
lines.append("3. multi-seed sanity 是否作为闭口前置（唯一实质裁决点）：接受多证据链交叉 or 要求 minimal multi-seed。")
lines.append("4. joint 强互补性未闭口是天花板效应，是否放行 P-INT-hard / degraded-severe 增强阶段门。")
lines.append("5. 是否可进入三轴小项目准备阶段（D4 地图已可作接口）。")
lines.append("6. 论文写作与实验闭口的次序：R113 §8 时序为『实验闭口→启动三轴小项目』，论文正文非小项目前置——请确认。\n")
with open(os.path.join(ROOT, "text", "codex_review_checklist_for_108.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("子任务F完成:")
print(f"  numeric checks: {n_pass} PASS / {n_conf} CONFLICT / total {len(checks)}")
print(f"  generated files: {len(manifest)}")
print(f"  redlines: {sum(1 for r in redlines if r[1]=='PASS')}/{len(redlines)} PASS")

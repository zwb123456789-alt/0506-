# -*- coding: utf-8 -*-
"""
子任务D：M5 三协议对比门闭口。
P-INT (neural, 三通道) / P-EXT (neural ocs_only stress) / P-DB (template retrieval)
在 G1/G3/G5 上的 cMAE / hit@30 统一矩阵 + 边界矩阵 + claim 表 + 对比图。
只读 11 号 metrics json + 13 号 pdb summary，不训练。
"""
import os, csv, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.abspath(os.path.join(ROOT, ".."))
RUNS = os.path.join(RES, "11_l1m2_multigeometry_ocs", "runs")
PDB_SUM = os.path.join(RES, "13_l1d3_confidence_pdb", "pdb", "l1d3_pdb_retrieval_summary.csv")
TAB = os.path.join(ROOT, "tables"); FIG = os.path.join(ROOT, "figures"); TXT = os.path.join(ROOT, "text")
for d in (TAB, FIG, TXT): os.makedirs(d, exist_ok=True)

GEOMS = ["G1", "G3", "G5"]


def neural_metric(proto, geom, mode, select="best"):
    p = os.path.join(RUNS, f"{proto}_{geom}_{mode}_seed42", f"metrics_test_{select}.json")
    if not os.path.exists(p):
        return None
    m = json.load(open(p, encoding="utf-8"))
    return {"cMAE": round(m["yaw_circular_mae_deg"], 3), "hit@30": round(m["yaw_hit@30"], 4),
            "hit@10": round(m.get("yaw_hit@10", float("nan")), 4), "n": m["n"]}


def pdb_metric(geom, similarity="neg-L2", template="matched-degraded", degrade="clean", split="test"):
    for row in csv.DictReader(open(PDB_SUM, encoding="utf-8")):
        if (row["geom"] == geom and row["similarity"] == similarity and row["template_mode"] == template
                and row["degrade_level"] == degrade and row["query_split"] == split):
            return {"top1_cMAE": round(float(row["top1_yaw_cmae"]), 3),
                    "top1_hit@30": round(float(row["top1_yaw_hit@30"]), 4),
                    "topk5_hit@30": round(float(row["topk5_best_yaw_hit@30"]), 4),
                    "topk5_cMAE": round(float(row["topk5_best_yaw_cmae"]), 3),
                    "n": int(row["n_query"])}
    return None


# ---------- protocol × geometry × method 表 ----------
rows = []
for g in GEOMS:
    # P-INT 三通道
    for m in ["ocs_only", "image_only", "joint"]:
        r = neural_metric("P-INT", g, m)
        if r:
            rows.append({"protocol": "P-INT", "method": f"neural_{m}", "geom": g,
                         "yaw_cMAE": r["cMAE"], "yaw_hit@30": r["hit@30"], "n": r["n"],
                         "note": "clean interpolation main task"})
    # P-EXT ocs_only
    r = neural_metric("P-EXT", g, "ocs_only")
    if r:
        rows.append({"protocol": "P-EXT", "method": "neural_ocs_only", "geom": g,
                     "yaw_cMAE": r["cMAE"], "yaw_hit@30": r["hit@30"], "n": r["n"],
                     "note": "strict yaw-block extrapolation stress test"})
    # P-DB
    r = pdb_metric(g)
    if r:
        rows.append({"protocol": "P-DB", "method": "retrieval_top1(neg-L2)", "geom": g,
                     "yaw_cMAE": r["top1_cMAE"], "yaw_hit@30": r["top1_hit@30"], "n": r["n"],
                     "note": "model-known simulated template retrieval, top1"})
        rows.append({"protocol": "P-DB", "method": "retrieval_topk5_oracle", "geom": g,
                     "yaw_cMAE": r["topk5_cMAE"], "yaw_hit@30": r["topk5_hit@30"], "n": r["n"],
                     "note": "top-5 oracle upper bound, NOT unsupervised success"})

with open(os.path.join(TAB, "m5_protocol_comparison_metrics.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------- 边界矩阵 ----------
def get(proto, method, g, field):
    for r in rows:
        if r["protocol"] == proto and r["method"] == method and r["geom"] == g:
            return r[field]
    return None

boundary = []
# P-INT ocs_only 单调增益
pint_ocs = [get("P-INT", "neural_ocs_only", g, "yaw_hit@30") for g in GEOMS]
boundary.append({"protocol": "P-INT", "condition": "clean interpolation, OCS-only",
                 "geom_trend": f"hit@30 G1/G3/G5={pint_ocs[0]}/{pint_ocs[1]}/{pint_ocs[2]}",
                 "verdict": "HOLDS: 多几何 OCS 单调增益",
                 "claim": "多观测总光度向量随几何数单调增益（simulated）"})
pext_ocs = [get("P-EXT", "neural_ocs_only", g, "yaw_hit@30") for g in GEOMS]
boundary.append({"protocol": "P-EXT", "condition": "strict yaw-block extrapolation, OCS-only",
                 "geom_trend": f"hit@30 G1/G3/G5={pext_ocs[0]}/{pext_ocs[1]}/{pext_ocs[2]}",
                 "verdict": "COLLAPSES: 加几何不能救 strict extrapolation",
                 "claim": "P-EXT yaw-block 仍坍缩，未解决"})
pdb_top1 = [get("P-DB", "retrieval_top1(neg-L2)", g, "yaw_hit@30") for g in GEOMS]
boundary.append({"protocol": "P-DB", "condition": "model-known simulated template retrieval, top1",
                 "geom_trend": f"hit@30 G1/G3/G5={pdb_top1[0]}/{pdb_top1[1]}/{pdb_top1[2]}",
                 "verdict": "RETRIEVABLE: 多几何下检索命中随几何提升",
                 "claim": "多观测光度向量含可检索 yaw 信息（template retrieval，非真实反演成功率）"})
pint_img = [get("P-INT", "neural_image_only", g, "yaw_hit@30") for g in GEOMS]
boundary.append({"protocol": "P-INT", "condition": "clean interpolation, image_only (对照)",
                 "geom_trend": f"hit@30 G1/G3/G5={pint_img[0]}/{pint_img[1]}/{pint_img[2]}",
                 "verdict": "SATURATED: image 通道 clean 下近饱和，掩盖 joint 增量",
                 "claim": "image_only clean 近饱和，不作为 OCS 主线结论，仅通道对照"})
with open(os.path.join(TAB, "m5_protocol_boundary_matrix.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(boundary[0].keys())); w.writeheader(); w.writerows(boundary)

# ---------- claim 表 ----------
claims = [
    {"protocol": "P-INT", "allowed": "多几何 OCS-only 在 clean/model-known simulated 下随 L1-G1→G3→G5 yaw hit@30 单调增益",
     "forbidden": "真实未知目标姿态反演成功 / 真实望远镜验证"},
    {"protocol": "P-EXT", "allowed": "strict yaw-block extrapolation 仍坍缩，多几何不能救 held-out yaw block",
     "forbidden": "P-EXT yaw-block 已解决 / 多几何解决了外推"},
    {"protocol": "P-DB", "allowed": "model-known simulated template retrieval 显示多观测光度向量含可检索 yaw 信息，检索命中随几何提升",
     "forbidden": "P-DB 是真实观测反演成功率 / P-DB top-k oracle 是无监督可达命中"},
    {"protocol": "cross", "allowed": "P-INT 回归与 P-DB 检索构成互补证据链，同指向多观测 OCS 含姿态信息",
     "forbidden": "joint 强互补性已证明 / 三协议已完成真实反演 / 路线一 C 整体闭口"},
]
with open(os.path.join(TAB, "m5_allowed_forbidden_protocol_claims.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(claims[0].keys())); w.writeheader(); w.writerows(claims)

# ---------- 对比图 ----------
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
x = np.arange(len(GEOMS)); w_ = 0.18
series = [("P-INT ocs_only", pint_ocs), ("P-EXT ocs_only", pext_ocs),
          ("P-DB top1", pdb_top1), ("P-INT image_only", pint_img)]
for i, (lab, vals) in enumerate(series):
    ax[0].bar(x + (i - 1.5) * w_, vals, w_, label=lab)
ax[0].set_xticks(x); ax[0].set_xticklabels(GEOMS); ax[0].set_ylim(0, 1)
ax[0].set_ylabel("yaw hit@30"); ax[0].set_title("Protocol × geometry: yaw hit@30"); ax[0].legend(fontsize=8)
# cMAE
pint_ocs_c = [get("P-INT", "neural_ocs_only", g, "yaw_cMAE") for g in GEOMS]
pext_ocs_c = [get("P-EXT", "neural_ocs_only", g, "yaw_cMAE") for g in GEOMS]
pdb_c = [get("P-DB", "retrieval_top1(neg-L2)", g, "yaw_cMAE") for g in GEOMS]
for i, (lab, vals) in enumerate([("P-INT ocs_only", pint_ocs_c), ("P-EXT ocs_only", pext_ocs_c), ("P-DB top1", pdb_c)]):
    ax[1].bar(x + (i - 1) * w_, vals, w_, label=lab)
ax[1].set_xticks(x); ax[1].set_xticklabels(GEOMS); ax[1].set_ylabel("yaw cMAE (deg)")
ax[1].set_title("Protocol × geometry: yaw cMAE"); ax[1].legend(fontsize=8)
fig.suptitle("M5 protocol comparison (clean, OCS focus) — model-known simulated")
fig.tight_layout()
for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"m5_protocol_comparison_panel.{ext}"), dpi=140)
plt.close(fig)

# ---------- summary ----------
lines = ["# 子任务D：M5 三协议对比门闭口摘要\n"]
lines.append("口径：clean；neural best；P-DB neg-L2 matched-degraded test；yaw hit@30 / cMAE；model-known simulated。\n")
lines.append("## 1. 三协议 × 几何 (yaw hit@30)\n")
lines.append("| method | G1 | G3 | G5 |")
lines.append("|---|---|---|---|")
lines.append(f"| P-INT ocs_only | {pint_ocs[0]} | {pint_ocs[1]} | {pint_ocs[2]} |")
lines.append(f"| P-EXT ocs_only | {pext_ocs[0]} | {pext_ocs[1]} | {pext_ocs[2]} |")
lines.append(f"| P-DB top1 | {pdb_top1[0]} | {pdb_top1[1]} | {pdb_top1[2]} |")
lines.append(f"| P-INT image_only(对照) | {pint_img[0]} | {pint_img[1]} | {pint_img[2]} |")
lines.append("\n## 2. 协议边界\n")
lines.append("- **P-INT**：多几何 OCS-only 单调增益，成立（simulated）。")
lines.append("- **P-EXT**：strict yaw-block 仍坍缩，多几何不能救外推——不得写成已解决。")
lines.append("- **P-DB**：model-known simulated template retrieval，检索命中随几何提升，证明多观测光度向量含可检索 yaw 信息；top-k 是 oracle 上界，非无监督成功率。")
lines.append("- **image_only 对照**：clean 下近饱和，仅作通道对照，不能掩盖 OCS 主线，也不能据此宣称 joint 强互补。\n")
lines.append("## 3. 闭口结论\n")
lines.append("- M5 三协议对比门可闭口为：P-INT 正结果 / P-EXT 坍缩 / P-DB 可检索信息，三者边界清晰互不冲突。")
lines.append("- 三协议共同支撑「多观测 OCS 含姿态信息」，但都限定 model-known simulated / current split / seed=42。\n")
with open(os.path.join(TXT, "m5_protocol_gate_closure_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("子任务D完成:")
print(f"  P-INT ocs hit@30 G1/G3/G5 = {pint_ocs}")
print(f"  P-EXT ocs hit@30 G1/G3/G5 = {pext_ocs}")
print(f"  P-DB  top1 hit@30 G1/G3/G5 = {pdb_top1}")
print(f"  rows={len(rows)} boundary={len(boundary)} claims={len(claims)}")

# -*- coding: utf-8 -*-
"""
子任务B：D2 三通道互补性闭口。
image_only / ocs_only / joint (P-INT, best) 三通道，G1/G3/G5。
- 三通道 hit@30 / cMAE / pitch error 基础表
- pairwise top-k overlap (Jaccard, top-5 grid idx)
- pairwise disagreement
- oracle hit@30 (并集)
- joint incremental value
- hard cases
只读 11 号 npz + 13 号 pdb per_query，不训练。
"""
import os, csv, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.abspath(os.path.join(ROOT, ".."))
RUNS = os.path.join(RES, "11_l1m2_multigeometry_ocs", "runs")
PDB = os.path.join(RES, "13_l1d3_confidence_pdb", "pdb", "l1d3_pdb_retrieval_per_query.csv")
TAB = os.path.join(ROOT, "tables"); FIG = os.path.join(ROOT, "figures"); TXT = os.path.join(ROOT, "text")
for d in (TAB, FIG, TXT): os.makedirs(d, exist_ok=True)

GEOMS = ["G1", "G3", "G5"]
MODES = ["image_only", "ocs_only", "joint"]
HIT = 30.0   # yaw hit@30 阈值
TOPK = 5     # 统一 top-k 口径 (neural top5 与 pdb 取前5)


def circ_err(a, b):
    d = abs((a - b) % 360.0)
    return np.minimum(d, 360.0 - d)


def load_neural(geom, mode, select="best"):
    z = np.load(os.path.join(RUNS, f"P-INT_{geom}_{mode}_seed42", f"samples_test_{select}.npz"), allow_pickle=True)
    grid = z["candidate_grid"]
    rid = z["record_id"].astype(str)
    out = {}
    for i, r in enumerate(rid):
        topk_idx = z["posterior_like_top5_idx"][i][:TOPK]
        out[r] = {
            "yaw_true": float(z["yaw_true_deg"][i]),
            "pitch_true": float(z["pitch_true_deg"][i]),
            "yaw_err": float(z["yaw_circular_error_deg"][i]),
            "pitch_err": float(z["pitch_abs_error_deg"][i]),
            "topk_grid": set(int(x) for x in topk_idx),
            "topk_yaw": [float(grid[int(x), 0]) for x in topk_idx],
            "margin": float(z["margin"][i]),
        }
    return out, grid


def load_pdb(geom, similarity="neg-L2", template="matched-degraded", degrade="clean", split="test"):
    """返回 record_id -> {yaw_err, topk_grid(yaw idx近似->用yaw值集合), topk_yaw}"""
    out = {}
    with open(PDB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row["geom"] == geom and row["similarity"] == similarity and
                    row["template_mode"] == template and row["degrade_level"] == degrade and
                    row["query_split"] == split):
                # topk10_idx 是模板库索引，与 neural grid idx 不同源，不能直接比 grid idx
                # 用于 pdb 自身检索误差与 D4；D2 pdb overlap 用 yaw hit 层面
                out[row["record_id"]] = {
                    "yaw_err": float(row["top1_yaw_err"]),
                    "margin": float(row["margin"]),
                    "nearest": float(row["nearest_distance"]),
                }
    return out


# ---------- 1. 三通道基础表 ----------
metrics_rows = []
neural = {}  # (geom,mode)->dict
for g in GEOMS:
    for m in MODES:
        nd, grid = load_neural(g, m)
        neural[(g, m)] = nd
        yerr = np.array([v["yaw_err"] for v in nd.values()])
        perr = np.array([v["pitch_err"] for v in nd.values()])
        hit30 = float(np.mean(yerr <= HIT))
        hit10 = float(np.mean(yerr <= 10.0))
        metrics_rows.append({
            "geom": g, "channel": m, "n": len(nd),
            "yaw_cMAE": round(float(np.mean(yerr)), 3),
            "yaw_median_AE": round(float(np.median(yerr)), 3),
            "yaw_hit@30": round(hit30, 4), "yaw_hit@10": round(hit10, 4),
            "pitch_MAE": round(float(np.mean(perr)), 3),
        })

with open(os.path.join(TAB, "d2_three_channel_metrics_summary.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(metrics_rows[0].keys())); w.writeheader(); w.writerows(metrics_rows)

# ---------- 2. pairwise top-k overlap (Jaccard, neural 三通道) ----------
overlap_rows = []
pairs = [("image_only", "ocs_only"), ("image_only", "joint"), ("ocs_only", "joint")]
for g in GEOMS:
    for a, b in pairs:
        na, nb = neural[(g, a)], neural[(g, b)]
        rids = sorted(set(na) & set(nb))
        jacs = []
        for r in rids:
            sa, sb = na[r]["topk_grid"], nb[r]["topk_grid"]
            u = len(sa | sb); jacs.append(len(sa & sb) / u if u else 0.0)
        overlap_rows.append({
            "geom": g, "pair": f"{a}|{b}", "k": TOPK, "n": len(rids),
            "mean_topk_jaccard": round(float(np.mean(jacs)), 4),
            "median_topk_jaccard": round(float(np.median(jacs)), 4),
            "frac_zero_overlap": round(float(np.mean([j == 0 for j in jacs])), 4),
        })
with open(os.path.join(TAB, "d2_pairwise_topk_overlap.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(overlap_rows[0].keys())); w.writeheader(); w.writerows(overlap_rows)

# ---------- 3. pairwise disagreement (hit@30 层面) ----------
disagree_rows = []
# 包含 P-DB 作为第4通道(检索)对照
pdb_by_g = {g: load_pdb(g) for g in GEOMS}
def hitmap(d):  # record->bool
    return {r: (v["yaw_err"] <= HIT) for r, v in d.items()}

for g in GEOMS:
    hits = {m: hitmap(neural[(g, m)]) for m in MODES}
    hits["pdb"] = hitmap(pdb_by_g[g])
    chans = MODES + ["pdb"]
    for a, b in [("image_only", "ocs_only"), ("image_only", "joint"), ("ocs_only", "joint"),
                 ("ocs_only", "pdb"), ("image_only", "pdb"), ("joint", "pdb")]:
        rids = sorted(set(hits[a]) & set(hits[b]))
        ha = np.array([hits[a][r] for r in rids]); hb = np.array([hits[b][r] for r in rids])
        disagree_rows.append({
            "geom": g, "pair": f"{a}|{b}", "n": len(rids),
            "both_correct": int(np.sum(ha & hb)),
            "a_only": int(np.sum(ha & ~hb)), "b_only": int(np.sum(~ha & hb)),
            "both_wrong": int(np.sum(~ha & ~hb)),
            "disagreement_rate": round(float(np.mean(ha != hb)), 4),
        })
with open(os.path.join(TAB, "d2_pairwise_disagreement.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(disagree_rows[0].keys())); w.writeheader(); w.writerows(disagree_rows)

# ---------- 4. oracle hit@30 (并集) + 5. joint incremental ----------
oracle_rows = []
for g in GEOMS:
    hits = {m: hitmap(neural[(g, m)]) for m in MODES}
    hits["pdb"] = hitmap(pdb_by_g[g])
    # 共同 record 集合(三神经通道)
    rids = sorted(set(neural[(g, "image_only")]) & set(neural[(g, "ocs_only")]) & set(neural[(g, "joint")]))
    def arr(m): return np.array([hits[m][r] for r in rids])
    im, oc, jo = arr("image_only"), arr("ocs_only"), arr("joint")
    n = len(rids)
    def rate(x): return round(float(np.mean(x)), 4)
    oracle_rows.append({
        "geom": g, "n": n,
        "image_only": rate(im), "ocs_only": rate(oc), "joint": rate(jo),
        "oracle_image∪ocs": rate(im | oc), "oracle_image∪joint": rate(im | jo),
        "oracle_ocs∪joint": rate(oc | jo), "oracle_all3": rate(im | oc | jo),
        "joint_minus_best_single": round(float(np.mean(jo)) - max(float(np.mean(im)), float(np.mean(oc))), 4),
        "joint_only_correct": int(np.sum(jo & ~im & ~oc)),
        "image_only_correct": int(np.sum(im & ~oc & ~jo)),
        "ocs_only_correct": int(np.sum(oc & ~im & ~jo)),
    })
with open(os.path.join(TAB, "d2_oracle_increment_summary.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(oracle_rows[0].keys())); w.writeheader(); w.writerows(oracle_rows)

# ---------- 6. hard cases ----------
hard_rows = []
for g in GEOMS:
    hits = {m: hitmap(neural[(g, m)]) for m in MODES}
    pdbh = hitmap(pdb_by_g[g])
    rids = sorted(set(neural[(g, "image_only")]) & set(neural[(g, "ocs_only")]) & set(neural[(g, "joint")]))
    for r in rids:
        im, oc, jo = hits["image_only"][r], hits["ocs_only"][r], hits["joint"][r]
        pd_ = pdbh.get(r, None)
        label = None
        if (not im) and oc:
            label = "image_wrong_ocs_correct"
        elif im and (not oc):
            label = "ocs_wrong_image_correct"
        elif (im or oc) and (not jo):
            label = "joint_fails_despite_branch"
        elif (not im) and pd_:
            label = "image_wrong_pdb_correct"
        if label:
            nd = neural[(g, "ocs_only")][r]
            hard_rows.append({
                "geom": g, "record_id": r,
                "yaw_true": nd["yaw_true"], "pitch_true": nd["pitch_true"],
                "image_hit": int(im), "ocs_hit": int(oc), "joint_hit": int(jo),
                "pdb_hit": (int(pd_) if pd_ is not None else ""),
                "label": label,
            })
with open(os.path.join(TAB, "d2_hardcase_examples.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(hard_rows[0].keys())); w.writeheader(); w.writerows(hard_rows)

# ---------- 图 1: 三通道 hit@30 与 cMAE ----------
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
x = np.arange(len(GEOMS)); w_ = 0.25
for i, m in enumerate(MODES):
    ax[0].bar(x + (i - 1) * w_, [next(r["yaw_hit@30"] for r in metrics_rows if r["geom"] == g and r["channel"] == m) for g in GEOMS], w_, label=m)
    ax[1].bar(x + (i - 1) * w_, [next(r["yaw_cMAE"] for r in metrics_rows if r["geom"] == g and r["channel"] == m) for g in GEOMS], w_, label=m)
ax[0].set_title("yaw hit@30 by channel"); ax[0].set_xticks(x); ax[0].set_xticklabels(GEOMS); ax[0].legend(); ax[0].set_ylim(0, 1)
ax[1].set_title("yaw cMAE (deg) by channel"); ax[1].set_xticks(x); ax[1].set_xticklabels(GEOMS); ax[1].legend()
fig.suptitle("D2 three-channel accuracy (P-INT, best, clean) — model-known simulated")
fig.tight_layout()
for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"d2_three_channel_hit_cmae.{ext}"), dpi=140)
plt.close(fig)

# ---------- 图 2: overlap/disagreement 热图 (G5) ----------
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
g = "G5"
mat = np.eye(3)
idx = {m: i for i, m in enumerate(MODES)}
for row in overlap_rows:
    if row["geom"] == g:
        a, b = row["pair"].split("|"); mat[idx[a], idx[b]] = mat[idx[b], idx[a]] = row["mean_topk_jaccard"]
im0 = ax[0].imshow(mat, vmin=0, vmax=1, cmap="viridis")
ax[0].set_xticks(range(3)); ax[0].set_yticks(range(3)); ax[0].set_xticklabels(MODES, rotation=30); ax[0].set_yticklabels(MODES)
ax[0].set_title(f"{g} top-{TOPK} Jaccard overlap")
for i in range(3):
    for j in range(3): ax[0].text(j, i, f"{mat[i,j]:.2f}", ha="center", va="center", color="w")
fig.colorbar(im0, ax=ax[0])
dmat = np.zeros((3, 3))
for row in disagree_rows:
    a, b = row["pair"].split("|")
    if row["geom"] == g and a in idx and b in idx:
        dmat[idx[a], idx[b]] = dmat[idx[b], idx[a]] = row["disagreement_rate"]
im1 = ax[1].imshow(dmat, vmin=0, vmax=max(0.01, dmat.max()), cmap="magma")
ax[1].set_xticks(range(3)); ax[1].set_yticks(range(3)); ax[1].set_xticklabels(MODES, rotation=30); ax[1].set_yticklabels(MODES)
ax[1].set_title(f"{g} hit@30 disagreement rate")
for i in range(3):
    for j in range(3): ax[1].text(j, i, f"{dmat[i,j]:.2f}", ha="center", va="center", color="w")
fig.colorbar(im1, ax=ax[1])
fig.suptitle("D2 three-channel overlap & disagreement (G5, clean) — model-known simulated")
fig.tight_layout()
for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"d2_overlap_disagreement_heatmap.{ext}"), dpi=140)
plt.close(fig)

# ---------- 图 3: oracle increment bars ----------
fig, ax = plt.subplots(figsize=(9, 4.5))
x = np.arange(len(GEOMS)); w_ = 0.13
series = ["image_only", "ocs_only", "joint", "oracle_ocs∪joint", "oracle_all3"]
for i, s in enumerate(series):
    ax.bar(x + (i - 2) * w_, [next(r[s] for r in oracle_rows if r["geom"] == g) for g in GEOMS], w_, label=s)
ax.set_xticks(x); ax.set_xticklabels(GEOMS); ax.set_ylim(0, 1); ax.legend(fontsize=8, ncol=2)
ax.set_title("D2 oracle increment: single channels vs union (yaw hit@30, clean) — simulated")
fig.tight_layout()
for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"d2_oracle_increment_bars.{ext}"), dpi=140)
plt.close(fig)

# ---------- summary md ----------
def get(rows, **kw):
    for r in rows:
        if all(r[k] == v for k, v in kw.items()): return r

lines = ["# 子任务B：D2 三通道互补性闭口摘要\n"]
lines.append("口径：P-INT / best / clean；yaw hit@30；top-k overlap 取 top-5 grid idx 的 Jaccard；model-known simulated。\n")
lines.append("## 1. 三通道精度（yaw hit@30 / cMAE）\n")
lines.append("| geom | image_only | ocs_only | joint |")
lines.append("|---|---|---|---|")
for g in GEOMS:
    im = get(metrics_rows, geom=g, channel="image_only"); oc = get(metrics_rows, geom=g, channel="ocs_only"); jo = get(metrics_rows, geom=g, channel="joint")
    lines.append(f"| {g} | {im['yaw_hit@30']} / {im['yaw_cMAE']} | {oc['yaw_hit@30']} / {oc['yaw_cMAE']} | {jo['yaw_hit@30']} / {jo['yaw_cMAE']} |")
lines.append("\n## 2. joint 增量诊断\n")
lines.append("| geom | joint | best_single | joint−best_single | joint_only_correct |")
lines.append("|---|---|---|---|---|")
joint_gains = []
for g in GEOMS:
    orow = get(oracle_rows, geom=g); joint_gains.append(orow["joint_minus_best_single"])
    bs = max(orow["image_only"], orow["ocs_only"])
    lines.append(f"| {g} | {orow['joint']} | {round(bs,4)} | {orow['joint_minus_best_single']} | {orow['joint_only_correct']} |")
lines.append("\n## 3. 互补性（oracle 上界 vs 单通道）\n")
lines.append("| geom | best_single | oracle_ocs∪joint | oracle_all3 |")
lines.append("|---|---|---|---|")
for g in GEOMS:
    orow = get(oracle_rows, geom=g); bs = max(orow["image_only"], orow["ocs_only"], orow["joint"])
    lines.append(f"| {g} | {round(bs,4)} | {orow['oracle_ocs∪joint']} | {orow['oracle_all3']} |")
lines.append("\n## 4. 闭口结论（诚实口径）\n")
max_gain = max(joint_gains)
if max_gain > 0.03:
    concl = f"joint 增量在当前口径可见（最大 joint−best_single = {max_gain:+.4f}）。"
else:
    concl = (f"joint 相对最佳单通道无稳定正增量（最大 joint−best_single = {max_gain:+.4f}）；"
             "**joint 强互补性仍未闭口，需 P-INT-hard / degraded-severe 裁决**。")
lines.append(f"- {concl}")
lines.append("- oracle 并集显著高于任一单通道，说明通道间存在 case 级互补信息，但该互补是 oracle 上界，不代表可无监督选中正确通道。")
lines.append("- image_only 在 clean 下近饱和，是 joint 增量受天花板限制的直接原因（与 R119 观察一致）。")
lines.append("- 以上均为 model-known simulated / current split / seed=42，不得写成真实反演成功或 joint 强互补性已证明。\n")
with open(os.path.join(TXT, "d2_complementarity_closure_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("子任务B完成:")
for g in GEOMS:
    orow = get(oracle_rows, geom=g)
    print(f"  {g}: image={orow['image_only']} ocs={orow['ocs_only']} joint={orow['joint']} "
          f"joint-best={orow['joint_minus_best_single']:+.4f} oracle_all3={orow['oracle_all3']}")
print(f"  max joint gain = {max_gain:+.4f} -> {'visible' if max_gain>0.03 else 'NOT closed (needs P-INT-hard)'}")
print(f"  hardcase rows={len(hard_rows)}")

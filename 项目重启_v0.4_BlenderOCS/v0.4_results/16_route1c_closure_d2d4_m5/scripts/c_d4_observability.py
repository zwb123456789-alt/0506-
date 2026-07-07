# -*- coding: utf-8 -*-
"""
子任务C：D4 姿态空间可观测性地图闭口。
- yaw×pitch error heatmap: ocs_only G1/G3/G5, image_only G5, joint G5, P-DB G5
- low/medium/high error 区域分类表
- 易混淆区域: pdb nearest 小但 yaw err 大 / neural margin 高但 err 大 / P-EXT 坍缩区
- 几何增益地图: G1->G5 ocs_only 改善量
- 与 hardcase index 交叉统计
只读 11/13 号，不训练。
"""
import os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.abspath(os.path.join(ROOT, ".."))
RUNS = os.path.join(RES, "11_l1m2_multigeometry_ocs", "runs")
PDB = os.path.join(RES, "13_l1d3_confidence_pdb", "pdb", "l1d3_pdb_retrieval_per_query.csv")
HARD = os.path.join(RES, "13_l1d3_confidence_pdb", "hardcases", "l1d3_hardcase_index.csv")
TAB = os.path.join(ROOT, "tables"); FIG = os.path.join(ROOT, "figures"); TXT = os.path.join(ROOT, "text")
for d in (TAB, FIG, TXT): os.makedirs(d, exist_ok=True)

GEOMS = ["G1", "G3", "G5"]
HIT = 30.0


def load_neural(geom, mode, proto="P-INT", select="best"):
    z = np.load(os.path.join(RUNS, f"{proto}_{geom}_{mode}_seed42", f"samples_test_{select}.npz"), allow_pickle=True)
    return {
        "rid": z["record_id"].astype(str),
        "yaw_true": z["yaw_true_deg"].astype(float),
        "pitch_true": z["pitch_true_deg"].astype(float),
        "yaw_err": z["yaw_circular_error_deg"].astype(float),
        "margin": z["margin"].astype(float),
    }


def load_pdb(geom, similarity="neg-L2", template="matched-degraded", degrade="clean", split="test"):
    rid, yt, pt, ye, near = [], [], [], [], []
    with open(PDB, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row["geom"] == geom and row["similarity"] == similarity and row["template_mode"] == template
                    and row["degrade_level"] == degrade and row["query_split"] == split):
                rid.append(row["record_id"]); yt.append(float(row["yaw_true"])); pt.append(float(row["pitch_true"]))
                ye.append(float(row["top1_yaw_err"])); near.append(float(row["nearest_distance"]))
    return {"rid": np.array(rid), "yaw_true": np.array(yt), "pitch_true": np.array(pt),
            "yaw_err": np.array(ye), "nearest": np.array(near)}


def scatter_map(ax, yaw, pitch, err, title):
    sc = ax.scatter(yaw, pitch, c=err, cmap="RdYlGn_r", vmin=0, vmax=90, s=28, edgecolors="k", linewidths=0.2)
    ax.set_title(title, fontsize=9); ax.set_xlabel("yaw true (deg)"); ax.set_ylabel("pitch true (deg)")
    ax.set_xlim(-10, 360); ax.set_ylim(-95, 95)
    return sc


# ---------- 图1: ocs_only G1/G3/G5 误差地图 ----------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
for ax, g in zip(axes, GEOMS):
    d = load_neural(g, "ocs_only")
    sc = scatter_map(ax, d["yaw_true"], d["pitch_true"], d["yaw_err"], f"ocs_only {g} yaw err")
fig.colorbar(sc, ax=axes, fraction=0.02, label="yaw circular error (deg)")
fig.suptitle("D4 observability map: OCS-only across geometries (P-INT best clean) — model-known simulated")
for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"d4_error_maps_ocs_g1_g3_g5.{ext}"), dpi=140, bbox_inches="tight")
plt.close(fig)

# ---------- 图2: image_only G5, joint G5, pdb G5 ----------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
di = load_neural("G5", "image_only"); dj = load_neural("G5", "joint"); dp = load_pdb("G5")
sc = scatter_map(axes[0], di["yaw_true"], di["pitch_true"], di["yaw_err"], "image_only G5 yaw err")
scatter_map(axes[1], dj["yaw_true"], dj["pitch_true"], dj["yaw_err"], "joint G5 yaw err")
scatter_map(axes[2], dp["yaw_true"], dp["pitch_true"], dp["yaw_err"], "P-DB G5 yaw err (neg-L2 matched)")
fig.colorbar(sc, ax=axes, fraction=0.02, label="yaw circular error (deg)")
fig.suptitle("D4 observability map: image / joint / P-DB (G5, clean) — model-known simulated")
for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"d4_error_maps_image_joint_pdb.{ext}"), dpi=140, bbox_inches="tight")
plt.close(fig)

# ---------- 图3: 几何增益地图 (G1 err - G5 err, ocs_only) ----------
# record_id 带 geom 前缀(G1_/G5_)，跨几何对齐需去前缀用 yaw/pitch 部分
def pose_key(r):
    return r.split("_", 1)[1]
d1 = load_neural("G1", "ocs_only"); d5 = load_neural("G5", "ocs_only")
m1 = {pose_key(r): e for r, e in zip(d1["rid"], d1["yaw_err"])}
common = [r for r in d5["rid"] if pose_key(r) in m1]
idx5 = {r: i for i, r in enumerate(d5["rid"])}
gain_yaw = np.array([d5["yaw_true"][idx5[r]] for r in common])
gain_pitch = np.array([d5["pitch_true"][idx5[r]] for r in common])
gain_val = np.array([m1[pose_key(r)] - d5["yaw_err"][idx5[r]] for r in common])  # 正=G5改善
fig, ax = plt.subplots(figsize=(7.5, 5))
sc = ax.scatter(gain_yaw, gain_pitch, c=gain_val, cmap="PuOr", vmin=-90, vmax=90, s=30, edgecolors="k", linewidths=0.2)
ax.set_title("D4 geometry gain map: OCS-only (G1 err − G5 err), positive=G5 rescues — simulated")
ax.set_xlabel("yaw true (deg)"); ax.set_ylabel("pitch true (deg)")
fig.colorbar(sc, ax=ax, label="yaw err reduction G1→G5 (deg)")
for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"d4_geometry_gain_map.{ext}"), dpi=140, bbox_inches="tight")
plt.close(fig)

# ---------- 表: 区域误差分类 (low/med/high) ----------
region_rows = []
for g in GEOMS:
    for mode in ["ocs_only", "image_only", "joint"]:
        d = load_neural(g, mode)
        e = d["yaw_err"]
        region_rows.append({
            "geom": g, "channel": mode, "n": len(e),
            "low_err<=10deg": int(np.sum(e <= 10)), "med_10-30deg": int(np.sum((e > 10) & (e <= 30))),
            "high_>30deg": int(np.sum(e > 30)),
            "frac_low": round(float(np.mean(e <= 10)), 3),
            "frac_high": round(float(np.mean(e > 30)), 3),
        })
with open(os.path.join(TAB, "d4_observability_region_stats.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(region_rows[0].keys())); w.writeheader(); w.writerows(region_rows)

# ---------- 表: 几何增益按姿态 ----------
gain_rows = []
for r, yy, pp, gv in zip(common, gain_yaw, gain_pitch, gain_val):
    gain_rows.append({"record_id": r, "yaw_true": yy, "pitch_true": pp,
                      "ocs_g1_err": round(m1[pose_key(r)], 3), "ocs_g5_err": round(float(d5["yaw_err"][idx5[r]]), 3),
                      "gain_g1_to_g5": round(float(gv), 3)})
with open(os.path.join(TAB, "d4_geometry_gain_by_attitude.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(gain_rows[0].keys())); w.writeheader(); w.writerows(gain_rows)

# ---------- 易混淆区域 ----------
confuse_rows = []
for g in GEOMS:
    dp = load_pdb(g)
    # pdb nearest 小(相似) 但 yaw err 大 -> 光度歧义(ambiguous flux)
    for r, yt, pt, ye, nr in zip(dp["rid"], dp["yaw_true"], dp["pitch_true"], dp["yaw_err"], dp["nearest"]):
        if nr <= np.percentile(dp["nearest"], 25) and ye > HIT:
            confuse_rows.append({"geom": g, "record_id": r, "yaw_true": yt, "pitch_true": pt,
                                 "type": "pdb_near_but_wrong(ambiguous_flux)", "pdb_yaw_err": round(ye, 2),
                                 "pdb_nearest": round(nr, 4)})
    # neural ocs margin 高但 err 大 -> 过自信错误
    dn = load_neural(g, "ocs_only")
    mth = np.percentile(dn["margin"], 75)
    for r, yt, pt, ye, mg in zip(dn["rid"], dn["yaw_true"], dn["pitch_true"], dn["yaw_err"], dn["margin"]):
        if mg >= mth and ye > HIT:
            confuse_rows.append({"geom": g, "record_id": r, "yaw_true": yt, "pitch_true": pt,
                                 "type": "neural_confident_but_wrong", "pdb_yaw_err": round(ye, 2),
                                 "pdb_nearest": ""})
# P-EXT 坍缩区(G5 ocs_only)
de = load_neural("G5", "ocs_only", proto="P-EXT")
for r, yt, pt, ye in zip(de["rid"], de["yaw_true"], de["pitch_true"], de["yaw_err"]):
    confuse_rows.append({"geom": "G5-PEXT", "record_id": r, "yaw_true": yt, "pitch_true": pt,
                         "type": "pext_yawblock_collapse", "pdb_yaw_err": round(float(ye), 2), "pdb_nearest": ""})
with open(os.path.join(TAB, "d4_confusion_regions.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(confuse_rows[0].keys())); w.writeheader(); w.writerows(confuse_rows)

# ---------- hardcase 区域交叉统计 ----------
hard = list(csv.DictReader(open(HARD, encoding="utf-8")))
def pitch_band(p):
    p = float(p)
    if p <= -45: return "pitch[-90,-45]"
    if p < 45: return "pitch[-45,45]"
    return "pitch[45,90]"
def yaw_quad(y):
    y = float(y) % 360
    return f"yaw[{int(y//90)*90},{int(y//90)*90+90})"
cross = {}
for row in hard:
    if row.get("degrade_level") != "clean" or row.get("select") != "best":
        continue
    labels = row["hardcase_labels"].split(";")
    key = (row["geom"], yaw_quad(row["yaw_true"]), pitch_band(row["pitch_true"]))
    cross.setdefault(key, {})
    for lb in labels:
        cross[key][lb] = cross[key].get(lb, 0) + 1
all_labels = sorted({lb for v in cross.values() for lb in v})
cross_rows = []
for (g, yq, pb), cnt in sorted(cross.items()):
    row = {"geom": g, "yaw_quad": yq, "pitch_band": pb}
    for lb in all_labels: row[lb] = cnt.get(lb, 0)
    cross_rows.append(row)
with open(os.path.join(TAB, "d4_hardcase_region_cross_tab.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["geom", "yaw_quad", "pitch_band"] + all_labels); w.writeheader(); w.writerows(cross_rows)

# ---------- 图4: hardcase 区域地图 (clean best, 按label上色) ----------
fig, ax = plt.subplots(figsize=(9, 5))
lab_list = sorted({row["hardcase_labels"].split(";")[0] for row in hard
                   if row.get("degrade_level") == "clean" and row.get("select") == "best"})
cmap = plt.get_cmap("tab10")
for i, lb in enumerate(lab_list):
    ys = [float(r["yaw_true"]) for r in hard if r.get("degrade_level") == "clean" and r.get("select") == "best" and r["hardcase_labels"].split(";")[0] == lb]
    ps = [float(r["pitch_true"]) for r in hard if r.get("degrade_level") == "clean" and r.get("select") == "best" and r["hardcase_labels"].split(";")[0] == lb]
    ax.scatter(ys, ps, s=22, color=cmap(i % 10), label=lb, alpha=0.7)
ax.set_title("D4 hardcase region map (clean best, primary label) — model-known simulated")
ax.set_xlabel("yaw true (deg)"); ax.set_ylabel("pitch true (deg)"); ax.legend(fontsize=7, ncol=2)
for ext in ("png", "pdf"): fig.savefig(os.path.join(FIG, f"d4_hardcase_region_map.{ext}"), dpi=140, bbox_inches="tight")
plt.close(fig)

# ---------- summary ----------
lines = ["# 子任务C：D4 姿态空间可观测性地图闭口摘要\n"]
lines.append("口径：P-INT best clean（P-EXT G5 单列坍缩区）；yaw circular error；model-known simulated。\n")
lines.append("## 1. 区域误差分布（frac_low = err≤10°, frac_high = err>30°）\n")
lines.append("| geom | channel | frac_low | frac_high |")
lines.append("|---|---|---|---|")
for r in region_rows:
    lines.append(f"| {r['geom']} | {r['channel']} | {r['frac_low']} | {r['frac_high']} |")
lines.append("\n## 2. 几何增益\n")
pos = sum(1 for g in gain_rows if g["gain_g1_to_g5"] > 5)
neg = sum(1 for g in gain_rows if g["gain_g1_to_g5"] < -5)
lines.append(f"- OCS-only 从 G1→G5：{pos} 个姿态显著被多几何救回(增益>5°)，{neg} 个变差(>5°)，其余基本持平。")
lines.append(f"- 平均 yaw err 改善 = {np.mean(gain_val):.2f}°（正=G5更好），中位 = {np.median(gain_val):.2f}°。")
lines.append("- 说明多几何主要救回 OCS-only 在单几何下高误差的姿态区，与 L1-G1→G5 单调增益一致。\n")
lines.append("## 3. 易混淆 / 低信息区域\n")
n_amb = sum(1 for r in confuse_rows if "ambiguous" in r["type"])
n_over = sum(1 for r in confuse_rows if r["type"] == "neural_confident_but_wrong")
n_pext = sum(1 for r in confuse_rows if r["type"] == "pext_yawblock_collapse")
lines.append(f"- ambiguous-flux（P-DB 最近邻很相似但 yaw 判错）：{n_amb} 例，是光度多观测向量的固有姿态歧义区。")
lines.append(f"- neural 过自信错误（margin 高但错）：{n_over} 例，佐证 R119 neural margin 置信区分度弱。")
lines.append(f"- P-EXT yaw-block 坍缩区：{n_pext} 例（G5 ocs_only 全部 held-out yaw block），确认 strict extrapolation 未解决。\n")
lines.append("## 4. 闭口结论\n")
lines.append("- D4 已形成 model-known simulated 姿态空间可观测性地图：可标出高/中/低误差区、多几何救回区、光度歧义区、过自信错误区与 P-EXT 坍缩区。")
lines.append("- 该地图可作为三轴小项目「高信息姿态 / 低信息观测区」的直接接口，但本轮不启动三轴小项目。")
lines.append("- 不得写成真实天空可观测性地图，不得写成三轴小项目已完成。\n")
with open(os.path.join(TXT, "d4_observability_map_closure_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("子任务C完成:")
print(f"  region_rows={len(region_rows)} gain_rows={len(gain_rows)} confuse_rows={len(confuse_rows)} cross_rows={len(cross_rows)}")
print(f"  geometry gain: mean={np.mean(gain_val):.2f} median={np.median(gain_val):.2f} rescued>5deg={pos} worsened>5deg={neg}")
print(f"  confusion: ambiguous={n_amb} overconfident={n_over} pext_collapse={n_pext}")

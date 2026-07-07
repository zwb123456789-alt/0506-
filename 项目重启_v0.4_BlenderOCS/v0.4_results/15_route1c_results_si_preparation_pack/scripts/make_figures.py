# -*- coding: utf-8 -*-
"""
R122 子任务 A/B：路线一 C Results/SI 候选图表生成脚本。

只读现有 10/11/12/13 结果 CSV/JSON，做轻量制图；不新训练、不新渲染、不改旧脚本。
所有图统一术语 L1-G1/L1-G3/L1-G5，输出 PNG + PDF（矢量）。

用法（ocs_sim 环境）：
    python make_figures.py

作者：Claude（R122 执行端）  最后更新：2026-07-01
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---- 路径根 ----
HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)                      # 15_route1c_results_si_preparation_pack
RESULTS = os.path.dirname(PACK)                   # v0.4_results
FIG_MAIN = os.path.join(PACK, "figures_main")
FIG_SI = os.path.join(PACK, "figures_si")
os.makedirs(FIG_MAIN, exist_ok=True)
os.makedirs(FIG_SI, exist_ok=True)

R10 = os.path.join(RESULTS, "10_b6_circular_regression_fix01")
R11 = os.path.join(RESULTS, "11_l1m2_multigeometry_ocs")
R12 = os.path.join(RESULTS, "12_l1m3_degraded_mroll")
R13 = os.path.join(RESULTS, "13_l1d3_confidence_pdb")

# ---- 统一样式 ----
plt.rcParams.update({
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 8.5,
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "axes.grid": True,
    "grid.alpha": 0.3,
})
C_G1, C_G3, C_G5 = "#4C72B0", "#DD8452", "#55A868"
GEOM_LABELS = ["L1-G1", "L1-G3", "L1-G5"]


def save(fig, stem, si=False):
    d = FIG_SI if si else FIG_MAIN
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(d, f"{stem}.{ext}"), bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {stem}.png / .pdf")


# =====================================================================
# Fig.1 任务与协议示意图（概念图，model-known simulated 前向模型与协议关系）
# =====================================================================
def fig1_protocol():
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 62)
    ax.axis("off")

    def box(x, y, w, h, text, fc):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                           fc=fc, ec="#333333", lw=1.2)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=14, lw=1.3, color="#555555"))

    ax.text(50, 59, "Fig.1  Model-known simulated multi-view observability protocol",
            ha="center", va="center", fontsize=12, fontweight="bold")
    ax.text(50, 55, "(simulated only — no real telescope / no real GEO attitude truth)",
            ha="center", va="center", fontsize=8.5, color="#B00000")

    # 左：前向模型
    box(2, 40, 22, 10, "Model-known 3D target\n(known geometry & material)", "#E8EEF6")
    box(2, 24, 22, 10, "Multi-geometry\nsun/view sampling\nL1-G1 ⊂ L1-G3 ⊂ L1-G5", "#E8EEF6")
    box(2, 8, 22, 10, "Shared physical\nforward model\n(Blender-derived)", "#E8EEF6")
    arrow(13, 40, 13, 34)
    arrow(13, 24, 13, 18)

    # 中：两通道
    box(34, 36, 24, 10, "OCS channel:\nmulti-view total-flux vector", "#FDECE0")
    box(34, 16, 24, 10, "Image channel:\nsingle-view rendered image", "#FDECE0")
    arrow(24, 29, 34, 41)   # forward -> OCS
    arrow(24, 20, 34, 21)   # forward -> image

    # 右：分析协议
    box(66, 46, 30, 8, "P-INT interpolation / P-EXT yaw-block\n(observability)", "#E6F2E6")
    box(66, 34, 30, 8, "P-DB simulated template retrieval\n(non-neural evidence)", "#E6F2E6")
    box(66, 22, 30, 8, "Neural regression: ocs_only / image_only / joint", "#E6F2E6")
    box(66, 10, 30, 8, "Conformal set-size (current split calibration)", "#E6F2E6")
    arrow(58, 41, 66, 50)
    arrow(58, 41, 66, 38)
    arrow(58, 21, 66, 26)
    arrow(58, 21, 66, 14)

    ax.text(50, 2.5,
            "Scope: attitude (yaw) observability, complementarity & confidence consistency of "
            "multi-view photometric vector under model-known simulation.",
            ha="center", va="center", fontsize=8, style="italic", color="#444444")
    save(fig, "Fig1_protocol_schematic")


# =====================================================================
# Fig.2 clean/P-INT OCS-only 单调增益（cMAE + hit@30 双 panel）
# =====================================================================
def fig2_clean_gain():
    df = pd.read_csv(os.path.join(R11, "l1m2_pint_vs_pext_ocs_only.csv"))
    d = df[(df.protocol == "P-INT") & (df["mode"] == "ocs_only")].sort_values("geom_group")
    cmae = [float(d[d.geom_group == g].yaw_cmae_deg.iloc[0]) for g in ["G1", "G3", "G5"]]
    hit = [float(d[d.geom_group == g]["yaw_hit@30"].iloc[0]) for g in ["G1", "G3", "G5"]]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 4.0))
    x = [1, 3, 5]
    a1.plot(x, cmae, "-o", color=C_G1, lw=2, ms=8)
    for xi, v in zip(x, cmae):
        a1.annotate(f"{v:.2f}°", (xi, v), textcoords="offset points", xytext=(0, 10), ha="center")
    a1.set_xticks(x); a1.set_xticklabels(GEOM_LABELS)
    a1.set_ylabel("yaw circular MAE (deg)")
    a1.set_title("(a) OCS-only yaw cMAE  ↓")
    a1.set_xlabel("geometry group (nested)")

    a2.plot(x, hit, "-s", color=C_G5, lw=2, ms=8)
    for xi, v in zip(x, hit):
        a2.annotate(f"{v:.3f}", (xi, v), textcoords="offset points", xytext=(0, 10), ha="center")
    a2.set_xticks(x); a2.set_xticklabels(GEOM_LABELS)
    a2.set_ylabel("yaw hit@30")
    a2.set_title("(b) OCS-only yaw hit@30  ↑")
    a2.set_xlabel("geometry group (nested)")
    a2.set_ylim(0, 1.0)

    fig.suptitle("Fig.2  clean / P-INT: OCS-only multi-view flux vector — monotone gain "
                 "(model-known simulated, seed=42)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, "Fig2_clean_pint_ocs_gain")


# =====================================================================
# Fig.3 degraded 下 OCS-only 增益保持与退化收缩
# =====================================================================
def fig3_degraded_gain():
    dfc = pd.read_csv(os.path.join(R11, "l1m2_pint_vs_pext_ocs_only.csv"))
    clean = {g: float(dfc[(dfc.protocol == "P-INT") & (dfc["mode"] == "ocs_only") &
                          (dfc.geom_group == g)].yaw_cmae_deg.iloc[0]) for g in ["G1", "G3", "G5"]}
    dfd = pd.read_csv(os.path.join(R12, "degraded", "l1m3_degraded_metrics_summary_best.csv"))
    dfd = dfd[dfd["mode"] == "ocs_only"]

    def get(level, g):
        r = dfd[(dfd.degrade_level == level) & (dfd.geom_group == g)]
        return float(r.yaw_circular_mae_deg.iloc[0])

    levels = ["clean", "degraded-mild", "degraded-moderate"]
    x = [1, 3, 5]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    markers = {"clean": "o", "degraded-mild": "s", "degraded-moderate": "^"}
    styles = {"clean": "-", "degraded-mild": "--", "degraded-moderate": ":"}
    for lv in levels:
        if lv == "clean":
            y = [clean[g] for g in ["G1", "G3", "G5"]]
        else:
            y = [get(lv, g) for g in ["G1", "G3", "G5"]]
        ax.plot(x, y, styles[lv] + markers[lv], lw=2, ms=7, label=lv)
        for xi, v in zip(x, y):
            ax.annotate(f"{v:.1f}", (xi, v), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(GEOM_LABELS)
    ax.set_xlabel("geometry group (nested)")
    ax.set_ylabel("OCS-only yaw circular MAE (deg)  ↓")
    ax.set_title("Fig.3  degraded realism axis: multi-view gain retained,\n"
                 "graceful contraction with degradation (model-known simulated)")
    ax.legend(title="degradation")
    fig.tight_layout()
    save(fig, "Fig3_degraded_ocs_gain")


# =====================================================================
# Fig.4 P-DB vs neural ocs_only + 互补四象限（双 panel）
# =====================================================================
def fig4_pdb_complementarity():
    pdb = pd.read_csv(os.path.join(R13, "pdb", "l1d3_pdb_retrieval_summary.csv"))
    # 主检索口径：neg-L2, matched-degraded, test split
    pc = pdb[(pdb.query_split == "test") & (pdb.similarity == "neg-L2") &
             (pdb.template_mode == "matched-degraded") & (pdb.degrade_level == "clean")]
    pdb_hit = {g: float(pc[pc.geom == g]["top1_yaw_hit@30"].iloc[0]) for g in ["G1", "G3", "G5"]}

    ec = pd.read_csv(os.path.join(R13, "consistency", "l1d3_error_correlation_summary.csv"))
    ecl = ec[(ec.degrade_level == "clean") & (ec["mode"] == "ocs_only") & (ec.select == "best")]
    neural_hit = {g: float(ecl[ecl.geom == g]["neural_hit@30"].iloc[0]) for g in ["G1", "G3", "G5"]}

    cases = pd.read_csv(os.path.join(R13, "consistency", "l1d3_complementarity_cases.csv"))
    q = cases[(cases.degrade_level == "clean") & (cases.geom == "G5") &
              (cases["mode"] == "ocs_only") & (cases.select == "best")].iloc[0]
    quad = [int(q.both_correct), int(q.neural_only), int(q.pdb_only), int(q.both_wrong)]
    oracle = float(q["oracle_hit@30"])

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.4))
    x = [1, 3, 5]
    a1.plot(x, [pdb_hit[g] for g in ["G1", "G3", "G5"]], "-o", color=C_G5, lw=2, ms=8,
            label="P-DB top1 (simulated template retrieval)")
    a1.plot(x, [neural_hit[g] for g in ["G1", "G3", "G5"]], "--s", color=C_G1, lw=2, ms=8,
            label="neural ocs_only")
    for xi, g in zip(x, ["G1", "G3", "G5"]):
        a1.annotate(f"{pdb_hit[g]:.3f}", (xi, pdb_hit[g]), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8, color=C_G5)
        a1.annotate(f"{neural_hit[g]:.3f}", (xi, neural_hit[g]), textcoords="offset points",
                    xytext=(0, -14), ha="center", fontsize=8, color=C_G1)
    a1.set_xticks(x); a1.set_xticklabels(GEOM_LABELS)
    a1.set_ylabel("yaw hit@30  ↑"); a1.set_ylim(0, 1.05)
    a1.set_xlabel("geometry group (nested)")
    a1.set_title("(a) P-DB retrieval vs neural (clean, test)")
    a1.legend(loc="lower right")

    # 四象限（clean G5）
    labels = ["both\ncorrect", "neural\nonly", "P-DB\nonly", "both\nwrong"]
    colors = ["#55A868", "#4C72B0", "#DD8452", "#C44E52"]
    bars = a2.bar(range(4), quad, color=colors)
    for b, v in zip(bars, quad):
        a2.text(b.get_x() + b.get_width() / 2, v + 3, str(v), ha="center", fontsize=9)
    a2.set_xticks(range(4)); a2.set_xticklabels(labels)
    a2.set_ylabel("count (n=296)")
    a2.set_title(f"(b) complementarity quadrants, clean L1-G5\n"
                 f"oracle hit@30={oracle:.3f}  (upper bound, Spearman≈0)")
    a2.grid(axis="x", alpha=0)

    fig.suptitle("Fig.4  P-DB simulated template retrieval complements neural regression "
                 "(model-known simulated; oracle = upper bound, not unsupervised selection)",
                 fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save(fig, "Fig4_pdb_neural_complementarity")


# =====================================================================
# Fig.5 conformal set_size 随几何收紧 + 负向观察摘要
# =====================================================================
def fig5_conformal():
    cf = pd.read_csv(os.path.join(R13, "conformal", "l1d3_conformal_summary.csv"))
    sel = cf[(cf.method == "neural") & (cf.degrade_level == "clean") & (cf.select == "best") &
             (cf.alpha == 0.1)]
    ocs = {g: float(sel[(sel.geom == g) & (sel["mode"] == "ocs_only")].set_size_deg.iloc[0])
           for g in ["G1", "G3", "G5"]}
    ocs_cov = {g: float(sel[(sel.geom == g) & (sel["mode"] == "ocs_only")].coverage.iloc[0])
               for g in ["G1", "G3", "G5"]}
    img_cov = {g: float(sel[(sel.geom == g) & (sel["mode"] == "image_only")].coverage.iloc[0])
               for g in ["G1", "G3", "G5"]}

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.4))
    x = [1, 3, 5]
    bars = a1.bar(x, [ocs[g] for g in ["G1", "G3", "G5"]], width=1.2,
                  color=[C_G1, C_G3, C_G5])
    for b, g in zip(bars, ["G1", "G3", "G5"]):
        a1.text(b.get_x() + b.get_width() / 2, b.get_height() + 4,
                f"{ocs[g]:.1f}°\ncov={ocs_cov[g]:.2f}", ha="center", fontsize=8)
    a1.set_xticks(x); a1.set_xticklabels(GEOM_LABELS)
    a1.set_ylabel("conformal set size (deg), α=0.10  ↓")
    a1.set_title("(a) OCS-only conformal set size tightens with geometry\n(current simulated split, target cov=0.90)")

    # 负向观察摘要（image_only 欠覆盖等）
    a2.axis("off")
    txt = (
        "Negative observations (must retain):\n\n"
        f"• image_only conformal coverage ≈ "
        f"{min(img_cov.values()):.2f}–{max(img_cov.values()):.2f}  (under target 0.90)\n"
        "• neural margin risk–coverage nearly flat\n   (weak confidence discrimination)\n"
        "• P-EXT yaw-block still collapses (≈146–157°)\n"
        "• joint gain ceiling-limited; final-checkpoint\n   sensitivity (G5 joint moderate hit@30=0.189)\n"
        "• oracle is upper bound, not unsupervised\n   selection of the correct branch"
    )
    a2.text(0.02, 0.98, txt, va="top", ha="left", fontsize=9.2,
            bbox=dict(boxstyle="round,pad=0.6", fc="#FFF4E6", ec="#DD8452"))
    a2.set_title("(b) negative-observation checklist")

    fig.suptitle("Fig.5  Confidence consistency: conformal set size vs geometry + retained negatives "
                 "(model-known simulated)", fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save(fig, "Fig5_conformal_geometry_confidence")


# =====================================================================
# SI-1 B6 single-frame 判据轴闭口（fold-matched, no-aug best）
# =====================================================================
def si1_b6_closure():
    df = pd.read_csv(os.path.join(R10, "b6_foldmatched_vs_p1a_best.csv"))
    d = df[df.aug == "none"]
    modes = ["image_only", "joint", "ocs_only"]
    b6 = [d[d["mode"] == m].b6_yaw_cmae_deg.mean() for m in modes]
    p1a = [d[d["mode"] == m].p1a_yaw_cmae_deg.mean() for m in modes]

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    xi = np.arange(3); w = 0.36
    ax.bar(xi - w / 2, p1a, w, label="P1-A (exact-bin head)", color="#B0B0B0")
    ax.bar(xi + w / 2, b6, w, label="B6 (circular regression)", color="#4C72B0")
    for i, (a, b) in enumerate(zip(p1a, b6)):
        ax.text(i - w / 2, a + 2, f"{a:.1f}", ha="center", fontsize=8)
        ax.text(i + w / 2, b + 2, f"{b:.1f}", ha="center", fontsize=8)
    ax.set_xticks(xi); ax.set_xticklabels(["image_only", "joint", "ocs_only"])
    ax.set_ylabel("yaw circular MAE (deg), fold-mean (no-aug best)")
    ax.set_title("SI-1  B6 single-frame / yaw-block closure:\ncircular regression improves image/joint cMAE "
                 "but yaw extrapolation still fails")
    ax.legend()
    fig.tight_layout()
    save(fig, "SI1_b6_single_frame_closure", si=True)


# =====================================================================
# SI-2 P-INT vs P-EXT stress test
# =====================================================================
def si2_pint_pext():
    df = pd.read_csv(os.path.join(R11, "l1m2_pint_vs_pext_ocs_only.csv"))
    pint = [float(df[(df.protocol == "P-INT") & (df.geom_group == g)].yaw_cmae_deg.iloc[0])
            for g in ["G1", "G3", "G5"]]
    pext = [float(df[(df.protocol == "P-EXT") & (df.geom_group == g)].yaw_cmae_deg.iloc[0])
            for g in ["G1", "G3", "G5"]]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    xi = np.arange(3); w = 0.36
    ax.bar(xi - w / 2, pint, w, label="P-INT (interpolation)", color="#55A868")
    ax.bar(xi + w / 2, pext, w, label="P-EXT (yaw-block extrapolation)", color="#C44E52")
    for i, (a, b) in enumerate(zip(pint, pext)):
        ax.text(i - w / 2, a + 2, f"{a:.1f}", ha="center", fontsize=8)
        ax.text(i + w / 2, b + 2, f"{b:.1f}", ha="center", fontsize=8)
    ax.set_xticks(xi); ax.set_xticklabels(GEOM_LABELS)
    ax.set_ylabel("OCS-only yaw circular MAE (deg)")
    ax.set_title("SI-2  P-EXT strict yaw-block extrapolation still collapses\n(≈146–157°); not solved by multi-view")
    ax.legend()
    fig.tight_layout()
    save(fig, "SI2_pint_vs_pext_stress", si=True)


# =====================================================================
# SI-3 M-roll ±15/±30 边界探针
# =====================================================================
def si3_mroll():
    df = pd.read_csv(os.path.join(R12, "mroll", "mroll_metrics_summary_best.csv"))
    rolls = [-30, -15, 0, 15, 30]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.4))
    for g, c in [("G1", C_G1), ("G5", C_G5)]:
        d = df[(df.geom_group == g) & (df["mode"] == "image_only")]
        cm = [float(d[d.roll_deg == r].yaw_cmae.iloc[0]) for r in rolls]
        ht = [float(d[d.roll_deg == r]["yaw_hit@30"].iloc[0]) for r in rolls]
        a1.plot(rolls, cm, "-o", color=c, lw=2, ms=7, label=f"L1-{g}")
        a2.plot(rolls, ht, "-s", color=c, lw=2, ms=7, label=f"L1-{g}")
    for a in (a1, a2):
        a.axvspan(-15, 15, color="#DFF0D8", alpha=0.5)
        a.set_xticks(rolls); a.set_xlabel("roll offset (deg), image_only zero-shot")
    a1.set_ylabel("yaw circular MAE (deg)  ↓")
    a1.set_title("(a) yaw cMAE vs roll")
    a2.set_ylabel("yaw hit@30  ↑"); a2.set_ylim(0, 1.05)
    a2.set_title("(b) yaw hit@30 vs roll")
    a1.legend(); a2.legend()
    fig.suptitle("SI-3  M-roll fixed-roll boundary probe: ±15° does not directly overturn fixed-roll, "
                 "±30° clearly sensitive (not roll-aware / not 3-axis)", fontsize=10.5)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save(fig, "SI3_mroll_boundary_probe", si=True)


# =====================================================================
# SI-4 hard-case index 五类分布
# =====================================================================
def si4_hardcase():
    df = pd.read_csv(os.path.join(R13, "hardcases", "l1d3_hardcase_index.csv"))
    # hardcase_labels 可能多标签，按分号/逗号统计主标签
    col = "hardcase_labels" if "hardcase_labels" in df.columns else df.columns[-1]
    counts = {}
    for v in df[col].dropna():
        for lab in str(v).replace(",", ";").split(";"):
            lab = lab.strip()
            if lab:
                counts[lab] = counts.get(lab, 0) + 1
    order = ["ocs-hard", "image-hard", "disagreement-hard", "ambiguous-flux", "robust-easy"]
    labs = [l for l in order if l in counts] + [l for l in counts if l not in order]
    vals = [counts[l] for l in labs]
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    bars = ax.bar(range(len(labs)), vals, color="#4C72B0")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.01, str(v), ha="center", fontsize=8)
    ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, rotation=15, ha="right")
    ax.set_ylabel(f"count (index rows total={len(df)})")
    ax.set_title("SI-4  hard-case index label distribution\n(candidate input for future P-INT-hard; NOT a stage-gate release)")
    fig.tight_layout()
    save(fig, "SI4_hardcase_index", si=True)
    return counts, len(df)


if __name__ == "__main__":
    fig1_protocol()
    fig2_clean_gain()
    fig3_degraded_gain()
    fig4_pdb_complementarity()
    fig5_conformal()
    si1_b6_closure()
    si2_pint_pext()
    si3_mroll()
    counts, n = si4_hardcase()
    print("hardcase counts:", counts, "total rows:", n)
    print("DONE")

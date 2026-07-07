"""
P4 observation planning synthesis — figure generation script
生成4张 P4 综合图，不新增渲染，仅基于 P1/P2/P3 已有数值。
"""

import os
import sys
import csv
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# ── 路径 ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS_22 = os.path.join(BASE, "..")          # 22号包根
FIG_DIR    = os.path.join(RESULTS_22, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ── 辅助：读CSV ────────────────────────────────────────────────────────────
def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def savefig(name):
    for ext in ("png", "pdf"):
        out = os.path.join(FIG_DIR, f"{name}.{ext}")
        plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  saved: {name}.png / .pdf")

# ════════════════════════════════════════════════════════════════════════════
# Figure 1 — p4_observation_role_map
# yaw/pitch 散点图，按观测规划角色着色，bubble size ∝ p4_utility
# ════════════════════════════════════════════════════════════════════════════
def fig1_observation_role_map():
    rows = read_csv(os.path.join(RESULTS_22, "tables", "p4_planning_candidate_roles.csv"))
    # 过滤 NOTE 行（无数值 yaw/pitch）
    rows = [r for r in rows if r["candidate_id"].startswith("C") and r["yaw_deg"].replace("-","").replace(".","").isdigit()]

    role_color = {
        "high-info-roll-sensitive": "#e63946",      # 红
        "bright-info-tradeoff":     "#2a9d8f",       # 青绿
        "low-info-negative-control":"#f4a261",       # 橙
        "dark-neutral-control":     "#a8a8a8",       # 灰
    }
    role_label = {
        "high-info-roll-sensitive": "High-info / roll-sensitive (R1)",
        "bright-info-tradeoff":     "Bright-info tradeoff (R4 boundary)",
        "low-info-negative-control":"Low-info negative control (R3)",
        "dark-neutral-control":     "Dark / neutral control (R2, R5)",
    }

    fig, ax = plt.subplots(figsize=(8, 6))
    for r in rows:
        yaw   = float(r["yaw_deg"])
        pitch = float(r["pitch_deg"])
        role  = r["p4_plan_role"]
        util  = float(r["p4_planning_utility_score"])
        size  = max(30, min(300, (util + 0.2) * 400))
        c = role_color.get(role, "#888888")
        ax.scatter(yaw, pitch, s=size, c=c, alpha=0.85, edgecolors="k", linewidths=0.4)

    # 最亮点 caution
    ax.scatter(147.5, 12.5, s=250, marker="*", c="#ffb703", edgecolors="#333",
               linewidths=0.8, zorder=5, label="Brightest pose (caution; info_rank=104/107)")

    # 图例
    legend_elems = [mpatches.Patch(facecolor=v, label=role_label[k])
                    for k, v in role_color.items()]
    legend_elems.append(Line2D([0],[0], marker="*", color="w", markerfacecolor="#ffb703",
                                markersize=12, markeredgecolor="#333",
                                label="Brightest pose (caution; info_rank=104/107)"))
    ax.legend(handles=legend_elems, fontsize=8, loc="upper left")

    ax.set_xlabel("Yaw (°)", fontsize=11)
    ax.set_ylabel("Pitch (°)", fontsize=11)
    ax.set_title("P4 Observation Role Map\n(bubble size ∝ p4_utility; model-known simulated, proxy indicators)",
                 fontsize=10)
    ax.axhline(0, color="k", lw=0.5, ls="--", alpha=0.3)
    ax.grid(True, alpha=0.25)
    ax.text(0.01, 0.01, "Condition: model-known simulated / phase63 / L1-G1\nAll indicators are proxy-level (neighbor_contrast_ypr, roll_sensitivity_score)",
            transform=ax.transAxes, fontsize=6, color="#555", va="bottom")
    plt.tight_layout()
    savefig("p4_observation_role_map")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# Figure 2 — p4_brightness_information_decoupling_summary
# Brightness rank vs Info rank，标注关键点，来自 P3 p4_planning_candidates
# ════════════════════════════════════════════════════════════════════════════
def fig2_brightness_info_decoupling():
    rows = read_csv(os.path.join(RESULTS_22, "tables", "p4_planning_candidate_roles.csv"))
    rows = [r for r in rows if r["candidate_id"].startswith("C") and
            r["brightness_rank_p3"].replace("/","").replace("N","").replace("A","").replace("0-","").isdigit()]

    role_color = {
        "high-info-roll-sensitive": "#e63946",
        "bright-info-tradeoff":     "#2a9d8f",
        "low-info-negative-control":"#f4a261",
        "dark-neutral-control":     "#a8a8a8",
    }

    fig, ax = plt.subplots(figsize=(7, 6))
    for r in rows:
        try:
            br = int(r["brightness_rank_p3"])
            ir = int(r["info_rank_p3"])
        except Exception:
            continue
        role = r["p4_plan_role"]
        c = role_color.get(role, "#888")
        ax.scatter(br, ir, s=60, c=c, alpha=0.85, edgecolors="k", linewidths=0.4)

    # 最亮点 caution
    ax.scatter(1, 104, s=200, marker="*", c="#ffb703", edgecolors="#333", linewidths=0.8,
               zorder=5)
    ax.annotate("Brightest point\nyaw147.5/+12.5\n(bright=1, info=104)",
                xy=(1, 104), xytext=(10, 90), fontsize=7,
                arrowprops=dict(arrowstyle="->", color="#333", lw=0.8))

    # C09 标注
    ax.annotate("C09: best tradeoff\nyaw155/+20\n(bright=31, info=1)",
                xy=(31, 1), xytext=(50, 15), fontsize=7,
                arrowprops=dict(arrowstyle="->", color="#2a9d8f", lw=0.8))

    # 对角线参考 (如果bright=info则在对角)
    diag = range(1, 110)
    ax.plot(diag, diag, "k--", alpha=0.2, lw=0.8, label="Bright = Info (reference)")

    legend_elems = [mpatches.Patch(facecolor=v,
                    label={"high-info-roll-sensitive":"High-info (R1)",
                           "bright-info-tradeoff":"Bright-info tradeoff (R4)",
                           "low-info-negative-control":"Low-info control (R3)",
                           "dark-neutral-control":"Dark/neutral control (R2/R5)"}[k])
                    for k,v in role_color.items()]
    legend_elems.append(Line2D([0],[0], marker="*", color="w", markerfacecolor="#ffb703",
                                markersize=12, markeredgecolor="#333",
                                label="Brightest point (caution)"))
    ax.legend(handles=legend_elems, fontsize=7, loc="lower right")

    ax.set_xlabel("Brightness Rank (lower = brighter, N=107)", fontsize=10)
    ax.set_ylabel("Information Rank / proxy (lower = higher info, N=107)", fontsize=10)
    ax.set_title("P4 Brightness vs Information Decoupling Summary\n(P3 local refinement, 107 poses; proxy indicators only)",
                 fontsize=10)
    ax.invert_xaxis(); ax.invert_yaxis()
    ax.grid(True, alpha=0.2)
    ax.text(0.01, 0.01,
            "brightness ≠ information: brightest pose (rank=1) has info_rank=104;\ninfo-peak (rank=1) has brightness_rank=31",
            transform=ax.transAxes, fontsize=6.5, color="#555", va="bottom")
    plt.tight_layout()
    savefig("p4_brightness_information_decoupling_summary")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# Figure 3 — p4_planning_candidate_panel
# 4 子图 panel：每个主要规划角色一张 yaw/pitch 图，标出具体候选点
# ════════════════════════════════════════════════════════════════════════════
def fig3_planning_candidate_panel():
    rows = read_csv(os.path.join(RESULTS_22, "tables", "p4_planning_candidate_roles.csv"))
    rows = [r for r in rows if r["candidate_id"].startswith("C")]

    roles = [
        ("high-info-roll-sensitive",   "High-info / Roll-sensitive (R1)", "#e63946"),
        ("bright-info-tradeoff",        "Bright-info Tradeoff (R4)",       "#2a9d8f"),
        ("low-info-negative-control",   "Low-info Negative Control (R3)",  "#f4a261"),
        ("dark-neutral-control",        "Dark / Neutral Control (R2, R5)", "#a8a8a8"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()

    for ax, (role_key, role_title, color) in zip(axes, roles):
        role_rows = [r for r in rows if r["p4_plan_role"] == role_key]
        yaws   = [float(r["yaw_deg"]) for r in role_rows]
        pitches= [float(r["pitch_deg"]) for r in role_rows]
        utils  = [float(r["p4_planning_utility_score"]) for r in role_rows]
        ids    = [r["candidate_id"] for r in role_rows]
        roll_s = [float(r["roll_sensitivity_score"]) if r["roll_sensitivity_score"] not in ("N/A","") else 0.0
                  for r in role_rows]

        sc = ax.scatter(yaws, pitches,
                        s=[max(40, u*350+40) for u in utils],
                        c=color, alpha=0.85, edgecolors="k", linewidths=0.5)

        for i, (cid, y, p) in enumerate(zip(ids, yaws, pitches)):
            ax.annotate(cid, (y, p), textcoords="offset points", xytext=(4, 4), fontsize=7)

        ax.set_title(f"{role_title}", fontsize=9, fontweight="bold", color=color)
        ax.set_xlabel("Yaw (°)", fontsize=8)
        ax.set_ylabel("Pitch (°)", fontsize=8)
        ax.grid(True, alpha=0.25)
        ax.axhline(0, color="k", lw=0.5, ls="--", alpha=0.3)

    fig.suptitle("P4 Planning Candidate Panel by Role\n(model-known simulated; proxy indicators; no real target inversion)",
                 fontsize=11)
    plt.tight_layout()
    savefig("p4_planning_candidate_panel")
    plt.close()


# ════════════════════════════════════════════════════════════════════════════
# Figure 4 — p4_stage_evidence_flow
# 阶段门证据流图（P1→P2→P3→P4），文字流程图
# ════════════════════════════════════════════════════════════════════════════
def fig4_stage_evidence_flow():
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")

    stage_data = [
        (1.2, "P1\nseed-roll\nsmoke\n(19-pack)",
         "12 seed × 8 roll\n96 renders\n─────────────\n• bright-seed roll-stable\n• high-info yaw240\n  roll_sens≈3.2-3.6\n• brightness≠info (smoke)",
         "#ffd166"),
        (3.8, "P2\nsparse\n3-axis grid\n(20-pack)",
         "125 pose × 9 roll\n1000 renders\n─────────────\n• R4 utility=0.251 (亮/稳)\n• R1 utility=0.234 (高信息)\n• R3 low-info连通\n• brightness≠info (区域级)",
         "#06d6a0"),
        (6.4, "P3\nlocal\nrefinement\n(21-pack)",
         "107 pose × 9 roll\n921 renders (2.5°)\n─────────────\n• R4亮点迁移3.54°\n  info_rank=104/107\n• yaw155/+20 info_rank=1\n  brightness_rank=31\n• R1 peak稳定(0.0°迁移)\n• R3 connectivity=0.60",
         "#118ab2"),
        (9.0, "P4\nobservation\nplanning\n(22-pack)",
         "综合P1/P2/P3\n无新渲染\n─────────────\n• 5类规划区域分层\n• 16候选 + 优先级矩阵\n• 风险边界矩阵\n• 收口候选材料",
         "#ef476f"),
    ]

    arrow_kw = dict(arrowstyle="->", color="#555", lw=2)
    for i, (xc, title, content, fc) in enumerate(stage_data):
        # box
        rect = mpatches.FancyBboxPatch((xc-1.1, 0.3), 2.2, 6.2,
                                        boxstyle="round,pad=0.1",
                                        facecolor=fc, alpha=0.25,
                                        edgecolor=fc, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(xc, 6.1, title, ha="center", va="top", fontsize=9,
                fontweight="bold", color="#222")
        ax.text(xc, 5.2, content, ha="center", va="top", fontsize=7,
                color="#333", linespacing=1.5)

        if i < len(stage_data) - 1:
            # arrow
            ax.annotate("", xy=(stage_data[i+1][0]-1.15, 3.3),
                        xytext=(xc+1.15, 3.3),
                        arrowprops=arrow_kw)
            # gate label
            gate = ["R132\naccepts","R134\naccepts","R136\naccepts"][i]
            ax.text((xc + stage_data[i+1][0])/2, 3.5, gate,
                    ha="center", va="bottom", fontsize=7, color="#555")

    ax.text(6, 0.05,
            "All conclusions: model-known simulated / phase63 / L1-G1 / proxy-level indicators / no real target inversion",
            ha="center", va="bottom", fontsize=7, color="#888",
            style="italic")
    ax.set_title("P4 Stage Evidence Flow: P1 → P2 → P3 → P4\n(three-axis observation planning project)",
                 fontsize=11, pad=5)
    plt.tight_layout()
    savefig("p4_stage_evidence_flow")
    plt.close()


# ── main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating P4 figures...")
    fig1_observation_role_map()
    fig2_brightness_info_decoupling()
    fig3_planning_candidate_panel()
    fig4_stage_evidence_flow()
    print("All P4 figures generated successfully.")

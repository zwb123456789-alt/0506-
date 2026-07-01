#!/usr/bin/env python3
"""
plot_l1d3_confidence_pdb.py —— R118 图表生成

图表（依据 R118 §5 建议）：
  figures/pdb_gain_curve.png            P-DB top1 hit@30 随 G1/G3/G5（各退化）
  figures/neural_vs_pdb_error_scatter.png  neural vs P-DB yaw error 散点（G5 clean）
  figures/confidence_decile_error.png   置信 decile 的 MAE/hit@30
  figures/risk_coverage_curves.png      risk-coverage 曲线
  figures/complementarity_quadrants.png 互补四象限计数
  conformal/figures/conformal_setsize.png  conformal set_size 随几何/退化

所有图仅用本轮 CSV，不重算。
"""

import csv

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import l1d3_common as C

PDB = C.OUT / "pdb"
CONS = C.OUT / "consistency"
CONF = C.OUT / "conformal"
FIG = C.OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)
(CONF / "figures").mkdir(parents=True, exist_ok=True)


def _read(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def plot_pdb_gain():
    rows = _read(PDB / "l1d3_pdb_retrieval_summary.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    for deg in C.DEGRADE_ALL:
        ys = []
        for g in C.GROUPS:
            r = [x for x in rows if x["geom"] == g and x["degrade_level"] == deg
                 and x["query_split"] == "test" and x["similarity"] == "neg-L2"
                 and x["template_mode"] == "matched-degraded"]
            ys.append(float(r[0]["top1_yaw_hit@30"]) if r else np.nan)
        ax.plot(C.GROUPS, ys, "o-", label=deg)
    ax.set_xlabel("geometry group"); ax.set_ylabel("P-DB top1 yaw hit@30")
    ax.set_title("P-DB retrieval gain (neg-L2, test, matched-degraded)")
    ax.set_ylim(0, 1.02); ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(FIG / "pdb_gain_curve.png", dpi=130); plt.close(fig)


def plot_scatter():
    rows = _read(CONS / "l1d3_neural_pdb_joined_per_attitude.csv")
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True, sharey=True)
    for ax, mode in zip(axes, C.MODES):
        sub = [r for r in rows if r["degrade_level"] == "clean" and r["geom"] == "G5"
               and r["mode"] == mode and r["select"] == "best"]
        ne = [float(r["neural_yaw_err"]) for r in sub]
        pe = [float(r["pdb_top1_yaw_err"]) for r in sub]
        ax.scatter(ne, pe, s=10, alpha=0.5)
        ax.plot([0, 180], [0, 180], "r--", lw=0.8)
        ax.axhline(30, color="gray", ls=":", lw=0.7); ax.axvline(30, color="gray", ls=":", lw=0.7)
        ax.set_title(f"G5 clean {mode}"); ax.set_xlabel("neural yaw err (°)")
    axes[0].set_ylabel("P-DB yaw err (°)")
    fig.suptitle("neural vs P-DB yaw error (test, best)")
    fig.tight_layout(); fig.savefig(FIG / "neural_vs_pdb_error_scatter.png", dpi=130); plt.close(fig)


def plot_deciles():
    rows = _read(CONS / "l1d3_confidence_deciles.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    for mode, src in [("ocs_only", "neural_margin"), ("joint", "neural_margin"),
                      ("pdb", "pdb_margin")]:
        sub = [r for r in rows if r["degrade_level"] == "clean" and r["geom"] == "G5"
               and r["mode"] == mode and r["conf_source"] == src]
        sub = sorted(sub, key=lambda r: int(r["decile"]))
        if not sub:
            continue
        d = [int(r["decile"]) for r in sub]
        h = [float(r["yaw_hit@30"]) for r in sub]
        ax.plot(d, h, "o-", label=f"{mode}/{src}")
    ax.set_xlabel("confidence decile (1=most confident)")
    ax.set_ylabel("yaw hit@30"); ax.set_title("Confidence decile vs accuracy (G5 clean)")
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(FIG / "confidence_decile_error.png", dpi=130); plt.close(fig)


def plot_risk_coverage():
    rows = _read(CONS / "l1d3_risk_coverage.csv")
    fig, ax = plt.subplots(figsize=(6, 4))
    for mode, src in [("ocs_only", "neural_margin"), ("joint", "neural_margin"),
                      ("pdb", "pdb_margin")]:
        sub = [r for r in rows if r["degrade_level"] == "clean" and r["geom"] == "G5"
               and r["mode"] == mode and r["conf_source"] == src]
        sub = sorted(sub, key=lambda r: float(r["coverage"]))
        if not sub:
            continue
        cov = [float(r["coverage"]) for r in sub]
        mae = [float(r["yaw_cmae"]) for r in sub]
        ax.plot(cov, mae, "o-", label=f"{mode}/{src}", ms=3)
    ax.set_xlabel("coverage (kept fraction, high-confidence first)")
    ax.set_ylabel("yaw cMAE (°)"); ax.set_title("Risk-coverage (G5 clean, test)")
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(FIG / "risk_coverage_curves.png", dpi=130); plt.close(fig)


def plot_quadrants():
    rows = _read(CONS / "l1d3_complementarity_cases.csv")
    sub = [r for r in rows if r["geom"] == "G5" and r["select"] == "best"]
    modes_deg = [(r["degrade_level"], r["mode"]) for r in sub]
    labels = [f"{d}\n{m}" for d, m in modes_deg]
    both = [int(r["both_correct"]) for r in sub]
    nonly = [int(r["neural_only"]) for r in sub]
    ponly = [int(r["pdb_only"]) for r in sub]
    bwrong = [int(r["both_wrong"]) for r in sub]
    x = np.arange(len(sub))
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(x, both, label="both✓", color="#4c9")
    ax.bar(x, nonly, bottom=both, label="neural_only", color="#49c")
    ax.bar(x, ponly, bottom=np.array(both) + np.array(nonly), label="pdb_only", color="#fc6")
    ax.bar(x, bwrong, bottom=np.array(both) + np.array(nonly) + np.array(ponly),
           label="both✗", color="#e66")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("count"); ax.set_title("Complementarity quadrants (G5 best, test)")
    ax.legend(ncol=4, fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "complementarity_quadrants.png", dpi=130); plt.close(fig)


def plot_conformal_setsize():
    rows = _read(CONF / "l1d3_conformal_summary.csv")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    series = [("neural", "ocs_only", "best"), ("neural", "joint", "best"),
              ("neural", "image_only", "best"), ("pdb-neg-L2", "neg-L2", "-")]
    for method, mode, sel in series:
        ys = []
        for g in C.GROUPS:
            r = [x for x in rows if x["method"] == method and x["degrade_level"] == "clean"
                 and x["geom"] == g and x["mode"] == mode and x["select"] == sel
                 and abs(float(x["alpha"]) - 0.10) < 1e-9]
            ys.append(float(r[0]["set_size_deg"]) if r else np.nan)
        ax.plot(C.GROUPS, ys, "o-", label=f"{method}/{mode}")
    ax.set_xlabel("geometry group"); ax.set_ylabel("conformal set_size (°, α=0.10)")
    ax.set_title("Conformal interval width (clean, test)")
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(CONF / "figures" / "conformal_setsize.png", dpi=130); plt.close(fig)


def main():
    plot_pdb_gain()
    plot_scatter()
    plot_deciles()
    plot_risk_coverage()
    plot_quadrants()
    plot_conformal_setsize()
    print("[PLOT] 6 figures written")
    print(f"  -> {FIG}")
    print(f"  -> {CONF / 'figures'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

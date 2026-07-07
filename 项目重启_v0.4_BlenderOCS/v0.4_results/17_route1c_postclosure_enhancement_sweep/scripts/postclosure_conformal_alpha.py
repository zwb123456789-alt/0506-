#!/usr/bin/env python3
"""
postclosure_conformal_alpha.py —— R126 子任务 E：conformal alpha sensitivity

原则上不新训练：直接复用 13 号 l1d3_conformal_summary.csv（已含 α=0.05/0.10/0.20）。
重组为 alpha 敏感性表与图，作为 R119/R123 提到的 SI 补强。

对象（预注册）：
  ocs_only / image_only / joint × L1-G1/G3/G5 × clean P-INT best
  degraded mild/moderate 现有预测可直接复算，一并纳入（附表），主表用 clean best。

严格口径：
  只写 split-conformal 工程覆盖与 set size，不写 Bayesian posterior / 最终概率校准。

输出：
  conformal_alpha/conformal_alpha_metrics.csv
  tables/conformal_alpha_coverage_setsize.csv
  figures/conformal_alpha_coverage_setsize.png/.pdf
  text/conformal_alpha_sensitivity_summary.md
"""

import csv
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SRC = (PROJECT_ROOT / "v0.4_results" / "13_l1d3_confidence_pdb" /
       "conformal" / "l1d3_conformal_summary.csv")
OUT = PROJECT_ROOT / "v0.4_results" / "17_route1c_postclosure_enhancement_sweep"
CA = OUT / "conformal_alpha"
TAB = OUT / "tables"
FIG = OUT / "figures"
TXT = OUT / "text"
for d in (CA, TAB, FIG, TXT):
    d.mkdir(parents=True, exist_ok=True)

GROUPS = ["G1", "G3", "G5"]
MODES = ["ocs_only", "image_only", "joint"]
ALPHAS = [0.05, 0.10, 0.20]


def load_rows():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    for r in rows:
        r["alpha"] = float(r["alpha"])
        r["coverage"] = float(r["coverage"])
        r["set_size_deg"] = float(r["set_size_deg"])
        r["target"] = float(r["target"])
        r["q_deg"] = float(r["q_deg"])
        r["val_n"] = int(r["val_n"]); r["test_n"] = int(r["test_n"])
    return rows


def find(rows, method, deg, geom, mode, select, alpha):
    for r in rows:
        if (r["method"] == method and r["degrade_level"] == deg and r["geom"] == geom
                and r["mode"] == mode and r["select"] == select
                and abs(r["alpha"] - alpha) < 1e-9):
            return r
    return None


def main():
    rows = load_rows()

    # 主表：clean best，neural 三通道 + P-DB neg-L2
    main_rows = []
    for deg in ["clean", "degraded-mild", "degraded-moderate"]:
        for geom in GROUPS:
            for mode in MODES:
                for a in ALPHAS:
                    r = find(rows, "neural", deg, geom, mode, "best", a)
                    if r:
                        main_rows.append({
                            "channel": f"neural/{mode}", "degrade_level": deg, "geom": geom,
                            "alpha": a, "target": r["target"], "coverage": r["coverage"],
                            "set_size_deg": round(r["set_size_deg"], 2),
                            "q_deg": round(r["q_deg"], 2), "val_n": r["val_n"], "test_n": r["test_n"],
                        })
            # P-DB neg-L2
            for a in ALPHAS:
                r = find(rows, "pdb-neg-L2", deg, geom, "neg-L2", "-", a)
                if r:
                    main_rows.append({
                        "channel": "pdb/neg-L2", "degrade_level": deg, "geom": geom,
                        "alpha": a, "target": r["target"], "coverage": r["coverage"],
                        "set_size_deg": round(r["set_size_deg"], 2),
                        "q_deg": round(r["q_deg"], 2), "val_n": r["val_n"], "test_n": r["test_n"],
                    })

    cols = ["channel", "degrade_level", "geom", "alpha", "target", "coverage",
            "set_size_deg", "q_deg", "val_n", "test_n"]
    for path in (CA / "conformal_alpha_metrics.csv", TAB / "conformal_alpha_coverage_setsize.csv"):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(main_rows)

    # ── 图：clean best，coverage 与 set_size vs alpha，三通道 × G1/G3/G5 ──
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    colors = {"G1": "#1f77b4", "G3": "#ff7f0e", "G5": "#2ca02c"}
    for j, mode in enumerate(MODES):
        ax_cov, ax_ss = axes[0, j], axes[1, j]
        for geom in GROUPS:
            covs, sss, tars = [], [], []
            for a in ALPHAS:
                r = find(rows, "neural", "clean", geom, mode, "best", a)
                covs.append(r["coverage"] if r else np.nan)
                sss.append(r["set_size_deg"] if r else np.nan)
                tars.append(1 - a)
            ax_cov.plot(ALPHAS, covs, "o-", color=colors[geom], label=geom)
            ax_ss.plot(ALPHAS, sss, "o-", color=colors[geom], label=geom)
        ax_cov.plot(ALPHAS, [1 - a for a in ALPHAS], "k--", alpha=0.5, label="target=1-α")
        ax_cov.set_title(f"neural/{mode} — coverage")
        ax_cov.set_xlabel("α"); ax_cov.set_ylabel("coverage"); ax_cov.set_ylim(0.7, 1.02)
        ax_cov.legend(fontsize=8); ax_cov.grid(alpha=0.3)
        ax_ss.set_title(f"neural/{mode} — set_size (°)")
        ax_ss.set_xlabel("α"); ax_ss.set_ylabel("set_size (deg)")
        ax_ss.legend(fontsize=8); ax_ss.grid(alpha=0.3)
    fig.suptitle("Conformal α sensitivity (clean P-INT, best-val): coverage & set_size vs α\n"
                 "split-conformal engineering coverage only — NOT Bayesian posterior / final probability calibration",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIG / "conformal_alpha_coverage_setsize.png", dpi=130)
    fig.savefig(FIG / "conformal_alpha_coverage_setsize.pdf")
    plt.close(fig)

    # ── summary md ──
    md = ["# R126 子任务 E：Conformal α 敏感性摘要\n",
          "最后更新：2026-07-01  \n",
          "数据来源：`v0.4_results/13_l1d3_confidence_pdb/conformal/l1d3_conformal_summary.csv`"
          "（既有输出已含 α=0.05/0.10/0.20，本轮不新训练，仅复算重组）。\n",
          "**严格口径：以下为 split-conformal 在当前 simulated split 上的工程覆盖与 set size；"
          "coverage≈target 只说明该 split 校准自洽，不是 Bayesian posterior，也不是最终概率校准。**\n"]

    md.append("## 1. clean P-INT best：coverage / set_size(°) vs α（neural 三通道）\n")
    md.append("| channel | geom | α=0.05 cov/ss | α=0.10 cov/ss | α=0.20 cov/ss |")
    md.append("|:--|:--|:--|:--|:--|")
    for mode in MODES:
        for geom in GROUPS:
            cells = []
            for a in ALPHAS:
                r = find(rows, "neural", "clean", geom, mode, "best", a)
                cells.append(f"{r['coverage']:.3f}/{r['set_size_deg']:.1f}" if r else "—")
            md.append(f"| neural/{mode} | {geom} | " + " | ".join(cells) + " |")
    md.append("")

    md.append("## 2. clean P-INT：P-DB neg-L2 coverage / set_size(°) vs α\n")
    md.append("| geom | α=0.05 cov/ss | α=0.10 cov/ss | α=0.20 cov/ss |")
    md.append("|:--|:--|:--|:--|")
    for geom in GROUPS:
        cells = []
        for a in ALPHAS:
            r = find(rows, "pdb-neg-L2", "clean", geom, "neg-L2", "-", a)
            cells.append(f"{r['coverage']:.3f}/{r['set_size_deg']:.1f}" if r else "—")
        md.append(f"| {geom} | " + " | ".join(cells) + " |")
    md.append("")

    md.append("## 3. 走势观察\n")
    md.append("```text")
    md.append("- α 增大（目标覆盖降低）→ set_size 单调收窄，符合 split-conformal 预期。")
    md.append("- 固定 α，set_size 随几何 G1->G3->G5 收紧（多观测光度向量信息量增加）。")
    md.append("- neural ocs_only coverage 在 α=0.10 附近接近 target；image_only clean 系统性略欠覆盖")
    md.append("  （与 R119/R123 结论一致，写作时保留 image_only 欠覆盖）。")
    md.append("- degraded mild/moderate 附表见 conformal_alpha_metrics.csv，趋势一致但整体 set_size 更大。")
    md.append("```")
    open(TXT / "conformal_alpha_sensitivity_summary.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

    print(f"[E conformal-alpha] main_rows={len(main_rows)}")
    for mode in MODES:
        r5 = find(rows, "neural", "clean", "G5", mode, "best", 0.05)
        r1 = find(rows, "neural", "clean", "G5", mode, "best", 0.10)
        r2 = find(rows, "neural", "clean", "G5", mode, "best", 0.20)
        print(f"  G5 {mode}: ss α0.05/0.10/0.20 = "
              f"{r5['set_size_deg']:.1f}/{r1['set_size_deg']:.1f}/{r2['set_size_deg']:.1f}")
    print(f"  -> {CA}, {TAB}, {FIG}, {TXT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

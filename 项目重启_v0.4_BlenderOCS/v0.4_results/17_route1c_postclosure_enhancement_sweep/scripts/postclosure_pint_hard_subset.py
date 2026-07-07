#!/usr/bin/env python3
"""
postclosure_pint_hard_subset.py —— R126 子任务 C1：hard-attitude subset 分区重算

只读复算，无训练。直接用 R125/R119 的 hardcase index（已含每条记录的
neural_ocs / image / joint / pdb yaw error 与 hardcase_labels），
把 evaluation 分为 easy / ambiguous-flux / ocs-hard / image-hard /
disagreement-hard / robust-easy 子集，复算各通道在各子集上的误差分布。

用途：在 clean/P-INT image 天花板之外，检查 joint 是否在 hard 子集上出现可见增量。

输出：
  tables/pint_hard_subset_metrics.csv
  figures/pint_hard_subset_error_panel.png/.pdf
  text/pint_hard_degraded_severe_summary.md  (C1 部分；C2 severe 部分由汇总脚本补)
"""

import csv
import sys
from collections import defaultdict
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
       "hardcases" / "l1d3_hardcase_index.csv")
OUT = PROJECT_ROOT / "v0.4_results" / "17_route1c_postclosure_enhancement_sweep"
TAB = OUT / "tables"; FIG = OUT / "figures"; TXT = OUT / "text"
for d in (TAB, FIG, TXT):
    d.mkdir(parents=True, exist_ok=True)

# 单标签子集（一条记录可属多个标签，用包含匹配）
SUBSETS = ["all", "robust-easy", "ambiguous-flux", "ocs-hard",
           "image-hard", "disagreement-hard"]
CHANNELS = [("neural_ocs_yaw_err", "ocs_only"),
            ("image_yaw_err", "image_only"),
            ("joint_yaw_err", "joint"),
            ("pdb_yaw_err", "pdb")]


def hit(errs, thr):
    return float((np.asarray(errs) <= thr).mean()) if len(errs) else float("nan")


def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    # 只用 clean 口径做 hard subset（image 天花板检查）；degraded 另有 C2
    for r in rows:
        for c, _ in CHANNELS:
            r[c] = float(r[c]) if r[c] not in ("", "nan") else np.nan

    out_rows = []
    # 按 degrade_level（clean 主）× subset × channel 聚合
    for deg in ["clean", "degraded-mild", "degraded-moderate"]:
        drows = [r for r in rows if r["degrade_level"] == deg]
        for subset in SUBSETS:
            if subset == "all":
                srows = drows
            else:
                srows = [r for r in drows if subset in r["hardcase_labels"]]
            n = len(srows)
            if n == 0:
                continue
            for col, ch in CHANNELS:
                errs = np.array([r[col] for r in srows], dtype=float)
                errs = errs[~np.isnan(errs)]
                if len(errs) == 0:
                    continue
                out_rows.append({
                    "degrade_level": deg, "subset": subset, "channel": ch, "n": len(errs),
                    "yaw_cmae_deg": round(float(errs.mean()), 3),
                    "yaw_median_ae_deg": round(float(np.median(errs)), 3),
                    "yaw_hit@30": round(hit(errs, 30), 4),
                    "yaw_hit@10": round(hit(errs, 10), 4),
                })
    with open(TAB / "pint_hard_subset_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["degrade_level", "subset", "channel", "n",
                                          "yaw_cmae_deg", "yaw_median_ae_deg",
                                          "yaw_hit@30", "yaw_hit@10"])
        w.writeheader(); w.writerows(out_rows)

    # ── 图：clean 各 subset 三通道 cMAE 对比 ──
    clean_rows = [r for r in out_rows if r["degrade_level"] == "clean"]
    subsets_present = [s for s in SUBSETS if any(r["subset"] == s for r in clean_rows)]
    chans = ["ocs_only", "image_only", "joint", "pdb"]
    colors = {"ocs_only": "#1f77b4", "image_only": "#ff7f0e", "joint": "#2ca02c", "pdb": "#d62728"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    x = np.arange(len(subsets_present)); width = 0.2
    for i, ch in enumerate(chans):
        vals = []
        for s in subsets_present:
            m = next((r for r in clean_rows if r["subset"] == s and r["channel"] == ch), None)
            vals.append(m["yaw_cmae_deg"] if m else np.nan)
        ax1.bar(x + i * width, vals, width, label=ch, color=colors[ch])
    ax1.set_xticks(x + 1.5 * width); ax1.set_xticklabels(subsets_present, rotation=25, ha="right")
    ax1.set_ylabel("yaw cMAE (°)"); ax1.set_title("clean P-INT: yaw cMAE by hard subset × channel")
    ax1.legend(); ax1.grid(alpha=0.3, axis="y")
    for i, ch in enumerate(chans):
        vals = []
        for s in subsets_present:
            m = next((r for r in clean_rows if r["subset"] == s and r["channel"] == ch), None)
            vals.append(m["yaw_hit@30"] if m else np.nan)
        ax2.bar(x + i * width, vals, width, label=ch, color=colors[ch])
    ax2.set_xticks(x + 1.5 * width); ax2.set_xticklabels(subsets_present, rotation=25, ha="right")
    ax2.set_ylabel("yaw hit@30"); ax2.set_title("clean P-INT: yaw hit@30 by hard subset × channel")
    ax2.legend(); ax2.grid(alpha=0.3, axis="y")
    fig.suptitle("P-INT hard-attitude subset error panel (clean, best-val; recompute from R119/R125 hardcase index)\n"
                 "model-known simulated — NOT real observation inversion", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(FIG / "pint_hard_subset_error_panel.png", dpi=130)
    fig.savefig(FIG / "pint_hard_subset_error_panel.pdf")
    plt.close(fig)

    # ── C1 摘要（写入 pint_hard_degraded_severe_summary.md 的 C1 段）──
    def _cell(deg, subset, ch, key):
        m = next((r for r in out_rows if r["degrade_level"] == deg and r["subset"] == subset
                  and r["channel"] == ch), None)
        return m[key] if m else None

    md = ["# R126 子任务 C：P-INT-hard / degraded-severe 摘要\n",
          "最后更新：2026-07-01  \n",
          "本文件含 C1（hard-attitude subset 分区重算）与 C2（degraded-severe 训练）两部分。\n",
          "**严格口径：model-known simulated；不得写成真实观测反演成功。**\n",
          "## C1. clean P-INT hard-attitude subset（best-val，复算自 R119/R125 hardcase index）\n",
          "| subset | n(joint) | ocs_only cMAE/hit30 | image_only cMAE/hit30 | joint cMAE/hit30 | pdb cMAE/hit30 |",
          "|:--|--:|:--|:--|:--|:--|"]
    for s in subsets_present:
        nj = _cell("clean", s, "joint", "n")
        cells = []
        for ch in chans:
            cm = _cell("clean", s, ch, "yaw_cmae_deg"); h = _cell("clean", s, ch, "yaw_hit@30")
            cells.append(f"{cm}/{h}" if cm is not None else "—")
        md.append(f"| {s} | {nj} | " + " | ".join(cells) + " |")
    md.append("")
    # joint vs best single 在各 subset
    md.append("### C1 观察：joint 相对最佳单通道（clean, hit@30）\n")
    md.append("```text")
    for s in subsets_present:
        oc = _cell("clean", s, "ocs_only", "yaw_hit@30")
        im = _cell("clean", s, "image_only", "yaw_hit@30")
        jo = _cell("clean", s, "joint", "yaw_hit@30")
        if None in (oc, im, jo):
            continue
        best_single = max(oc, im)
        inc = jo - best_single
        md.append(f"  {s:20s}: joint hit@30={jo:.3f}  best_single={best_single:.3f}  Δ={inc:+.3f}")
    md.append("")
    md.append("  读法：Δ>0 表示 joint 在该 hard 子集相对最佳单通道有可见增量；")
    md.append("        clean image_only 近饱和的子集里 joint 增量通常受天花板限制。")
    md.append("```")
    md.append("\n（C2 degraded-severe 部分见下方，由 degraded-severe 汇总脚本追加。）\n")
    open(TXT / "pint_hard_degraded_severe_summary.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

    print(f"[C1 pint-hard] out_rows={len(out_rows)} subsets={subsets_present}")
    for s in subsets_present:
        oc = _cell("clean", s, "ocs_only", "yaw_hit@30")
        im = _cell("clean", s, "image_only", "yaw_hit@30")
        jo = _cell("clean", s, "joint", "yaw_hit@30")
        print(f"    {s:20s}: ocs={oc} image={im} joint={jo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

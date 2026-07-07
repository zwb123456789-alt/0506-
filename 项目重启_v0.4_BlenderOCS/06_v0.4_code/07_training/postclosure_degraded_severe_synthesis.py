#!/usr/bin/env python3
"""
postclosure_degraded_severe_synthesis.py —— R126 子任务 C2 汇总

汇总 degraded-severe 9 run（G1/G3/G5 × ocs_only/image_only/joint）：
  - severe 三通道 metrics
  - joint 相对最佳单通道增量
  - disagreement oracle（用每条记录三通道预测取 min error 上界）
  - 通道对比图
并把 C2 结论追加到 pint_hard_degraded_severe_summary.md。

输入：17 号包 pint_hard_degraded_severe/runs/degraded-severe_P-INT_{G}_{mode}_seed42/
      每 run 的 metrics_test_best.json 与 samples_test_best.npz
"""

import csv
import json
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

OUT = PROJECT_ROOT / "v0.4_results" / "17_route1c_postclosure_enhancement_sweep"
RUNS = OUT / "pint_hard_degraded_severe" / "runs"
TAB = OUT / "tables"; FIG = OUT / "figures"; TXT = OUT / "text"
for d in (TAB, FIG, TXT):
    d.mkdir(parents=True, exist_ok=True)

GROUPS = ["G1", "G3", "G5"]
MODES = ["ocs_only", "image_only", "joint"]


def run_dir(g, m):
    return RUNS / f"degraded-severe_P-INT_{g}_{m}_seed42"


def load_metrics(g, m, select="best"):
    p = run_dir(g, m) / f"metrics_test_{select}.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def load_samples(g, m, select="best"):
    p = run_dir(g, m) / f"samples_test_{select}.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    return {"record_id": d["record_id"], "yaw_err": d["yaw_circular_error_deg"]}


def main():
    # 1. severe metrics 表
    metric_rows = []
    present = {}
    for g in GROUPS:
        for m in MODES:
            for select in ("best", "final"):
                mt = load_metrics(g, m, select)
                if mt is None:
                    continue
                metric_rows.append({
                    "degrade_level": "degraded-severe", "geom": g, "mode": m, "select": select,
                    "yaw_cmae_deg": round(mt["yaw_circular_mae_deg"], 3),
                    "yaw_hit@30": round(mt["yaw_hit@30"], 4),
                    "yaw_hit@10": round(mt["yaw_hit@10"], 4),
                    "pitch_mae_deg": round(mt["pitch_mae_deg"], 3), "n": mt["n"],
                })
                if select == "best":
                    present[(g, m)] = mt
    with open(TAB / "degraded_severe_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["degrade_level", "geom", "mode", "select",
                                          "yaw_cmae_deg", "yaw_hit@30", "yaw_hit@10",
                                          "pitch_mae_deg", "n"])
        w.writeheader(); w.writerows(metric_rows)

    # 2. joint 增量表（best-val）
    inc_rows = []
    for g in GROUPS:
        oc = present.get((g, "ocs_only")); im = present.get((g, "image_only")); jo = present.get((g, "joint"))
        if not (oc and im and jo):
            continue
        best_single_hit = max(oc["yaw_hit@30"], im["yaw_hit@30"])
        best_single_cmae = min(oc["yaw_circular_mae_deg"], im["yaw_circular_mae_deg"])
        inc_rows.append({
            "geom": g,
            "ocs_hit30": round(oc["yaw_hit@30"], 4), "image_hit30": round(im["yaw_hit@30"], 4),
            "joint_hit30": round(jo["yaw_hit@30"], 4),
            "best_single_hit30": round(best_single_hit, 4),
            "joint_increment_hit30": round(jo["yaw_hit@30"] - best_single_hit, 4),
            "ocs_cmae": round(oc["yaw_circular_mae_deg"], 3), "image_cmae": round(im["yaw_circular_mae_deg"], 3),
            "joint_cmae": round(jo["yaw_circular_mae_deg"], 3),
            "best_single_cmae": round(best_single_cmae, 3),
            "joint_cmae_gain": round(best_single_cmae - jo["yaw_circular_mae_deg"], 3),
        })
    with open(TAB / "degraded_severe_joint_increment.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(inc_rows[0].keys()) if inc_rows else
                           ["geom", "joint_increment_hit30"])
        w.writeheader(); w.writerows(inc_rows)

    # 3. disagreement oracle：逐记录三通道 min error 上界（需 samples 对齐 record_id）
    oracle_rows = []
    for g in GROUPS:
        so = load_samples(g, "ocs_only"); si = load_samples(g, "image_only"); sj = load_samples(g, "joint")
        if not (so and si and sj):
            continue
        # 按 record_id 对齐
        def to_map(s):
            return {str(r): float(e) for r, e in zip(s["record_id"], s["yaw_err"])}
        mo, mi, mj = to_map(so), to_map(si), to_map(sj)
        common = set(mo) & set(mi) & set(mj)
        if not common:
            continue
        common = sorted(common)
        eo = np.array([mo[r] for r in common]); ei = np.array([mi[r] for r in common])
        ej = np.array([mj[r] for r in common])
        oracle = np.minimum(np.minimum(eo, ei), ej)          # 三通道逐样本取最优（oracle 选择器上界）
        best_single_oracle = np.minimum(eo, ei)              # 仅单通道 oracle
        oracle_rows.append({
            "geom": g, "n": len(common),
            "ocs_hit30": round(float((eo <= 30).mean()), 4),
            "image_hit30": round(float((ei <= 30).mean()), 4),
            "joint_hit30": round(float((ej <= 30).mean()), 4),
            "single_oracle_hit30": round(float((best_single_oracle <= 30).mean()), 4),
            "three_channel_oracle_hit30": round(float((oracle <= 30).mean()), 4),
            "oracle_cmae": round(float(oracle.mean()), 3),
        })
    with open(TAB / "degraded_severe_disagreement_oracle.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(oracle_rows[0].keys()) if oracle_rows else ["geom"])
        w.writeheader(); w.writerows(oracle_rows)

    # 4. 通道对比图
    if present:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        x = np.arange(len(GROUPS)); width = 0.25
        for i, m in enumerate(MODES):
            cmae = [present[(g, m)]["yaw_circular_mae_deg"] if (g, m) in present else np.nan for g in GROUPS]
            hit = [present[(g, m)]["yaw_hit@30"] if (g, m) in present else np.nan for g in GROUPS]
            ax1.bar(x + i * width, cmae, width, label=m)
            ax2.bar(x + i * width, hit, width, label=m)
        ax1.set_xticks(x + width); ax1.set_xticklabels(GROUPS); ax1.set_ylabel("yaw cMAE (°)")
        ax1.set_title("degraded-severe: yaw cMAE"); ax1.legend(); ax1.grid(alpha=0.3, axis="y")
        ax2.set_xticks(x + width); ax2.set_xticklabels(GROUPS); ax2.set_ylabel("yaw hit@30")
        ax2.set_title("degraded-severe: yaw hit@30"); ax2.legend(); ax2.grid(alpha=0.3, axis="y")
        fig.suptitle("degraded-severe channel comparison (P-INT, best-val, seed42)\n"
                     "model-known simulated severe degradation — NOT real observation", fontsize=11)
        fig.tight_layout(rect=[0, 0, 1, 0.94])
        fig.savefig(FIG / "degraded_severe_channel_comparison.png", dpi=130)
        fig.savefig(FIG / "degraded_severe_channel_comparison.pdf")
        plt.close(fig)

    # 5. 追加 C2 到 summary
    summary_path = TXT / "pint_hard_degraded_severe_summary.md"
    md = ["\n---\n", "## C2. degraded-severe 三通道（P-INT, best-val, seed42）\n",
          "severe 预注册参数：blur σ=2.0px, downsample x4, bg 0.05+grad 0.04, "
          "Poisson peak 150, read 0.03, flux err 12%（物理合理，比 moderate 更强，非 B6 粗增广）。\n",
          f"完成 run：{len(present)}/9。\n",
          "| geom | ocs_only cMAE/hit30 | image_only cMAE/hit30 | joint cMAE/hit30 |",
          "|:--|:--|:--|:--|"]
    for g in GROUPS:
        cells = []
        for m in MODES:
            mt = present.get((g, m))
            cells.append(f"{mt['yaw_circular_mae_deg']:.2f}/{mt['yaw_hit@30']:.3f}" if mt else "—")
        md.append(f"| {g} | " + " | ".join(cells) + " |")
    md.append("")
    if inc_rows:
        md.append("### C2 joint 增量（相对最佳单通道，best-val）\n")
        md.append("| geom | joint hit30 | best_single hit30 | Δhit30 | joint cMAE | best_single cMAE | ΔcMAE(增益) |")
        md.append("|:--|--:|--:|--:|--:|--:|--:|")
        for r in inc_rows:
            md.append(f"| {r['geom']} | {r['joint_hit30']} | {r['best_single_hit30']} | "
                      f"{r['joint_increment_hit30']:+.4f} | {r['joint_cmae']} | "
                      f"{r['best_single_cmae']} | {r['joint_cmae_gain']:+.3f} |")
        md.append("")
        # 裁决
        stable_pos = all(r["joint_increment_hit30"] > 0.005 for r in inc_rows)
        any_pos = any(r["joint_increment_hit30"] > 0.005 for r in inc_rows)
        image_saturated = all((present.get((g, "image_only")) or {}).get("yaw_hit@30", 1.0) > 0.95
                              for g in GROUPS if (g, "image_only") in present)
        if stable_pos and not image_saturated:
            verdict = "joint 增量在 severe hard condition 下可见"
        else:
            verdict = "joint 强互补性仍未被支持"
        md.append("### C2 裁决\n")
        md.append("```text")
        md.append(f"- image_only 在 severe 下是否仍近饱和(hit@30>0.95 全几何)：{image_saturated}")
        md.append(f"- joint 是否稳定优于最佳单通道(Δhit30>0.005 全几何)：{stable_pos}")
        md.append(f"- 结论：{verdict}")
        md.append("- 无论结果如何，不写真实观测反演成功。")
        md.append("```")
    if oracle_rows:
        md.append("\n### C2 disagreement oracle（三通道逐样本取最优上界）\n")
        md.append("| geom | ocs hit30 | image hit30 | joint hit30 | single-oracle hit30 | 3ch-oracle hit30 |")
        md.append("|:--|--:|--:|--:|--:|--:|")
        for r in oracle_rows:
            md.append(f"| {r['geom']} | {r['ocs_hit30']} | {r['image_hit30']} | {r['joint_hit30']} | "
                      f"{r['single_oracle_hit30']} | {r['three_channel_oracle_hit30']} |")
        md.append("\noracle 是通道级选择上界（非可实现预测器），用于判断通道互补的理论上限。\n")
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    print(f"[C2 severe] metrics rows={len(metric_rows)} present_best={len(present)} "
          f"increment={len(inc_rows)} oracle={len(oracle_rows)}")
    for r in inc_rows:
        print(f"    {r['geom']}: joint hit30={r['joint_hit30']} best_single={r['best_single_hit30']} "
              f"Δ={r['joint_increment_hit30']:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

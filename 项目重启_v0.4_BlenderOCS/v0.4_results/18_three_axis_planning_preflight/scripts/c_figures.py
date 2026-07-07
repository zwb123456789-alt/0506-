#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
18 号三轴准备包 - 子任务C 制图 + 子任务B 指标分布图（只读）

生成：
  figures/seed_map_fixedroll.png / .pdf   : yaw-pitch 平面上的种子分布 + 亮度底图
  figures/brightness_vs_information.png / .pdf : brightness 与 information 散点区分
"""
import csv
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

V04 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(V04, "v0.4_results", "18_three_axis_planning_preflight")


def load_master():
    rows = []
    with open(os.path.join(OUT, "seeds", "attitude_master_fixedroll.csv"),
              encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def load_seeds():
    rows = []
    with open(os.path.join(OUT, "seeds", "three_axis_seed_candidates.csv"),
              encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def fnum(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return np.nan


def main():
    master = load_master()
    seeds = load_seeds()

    yaws = np.array([fnum(r["yaw"]) for r in master])
    pitches = np.array([fnum(r["pitch"]) for r in master])
    bright = np.array([fnum(r["ocs_total_phase63"]) for r in master])
    logb = np.log10(np.clip(bright, bright[bright > 0].min() if np.any(bright > 0) else 1e-9, None))

    # ---- 图1：seed map ----
    fig, ax = plt.subplots(figsize=(11, 6))
    sc = ax.scatter(yaws, pitches, c=logb, cmap="viridis", s=18, marker="s",
                    alpha=0.55, edgecolors="none")
    cb = plt.colorbar(sc, ax=ax)
    cb.set_label("log10 OCS total (phase63, fixed-roll)")

    cat_style = {
        "bright-seed": ("*", "red", 220),
        "dark-seed": ("v", "navy", 90),
        "high-info-seed": ("^", "lime", 110),
        "low-info-seed": ("X", "magenta", 110),
        "ocs-hard-seed": ("D", "orange", 80),
        "image-hard-seed": ("P", "cyan", 120),
        "disagreement-seed": ("o", "yellow", 80),
        "roll-sensitive-seed": ("h", "white", 130),
        "robust-easy-seed": ("s", "black", 60),
    }
    for cat, (mk, col, sz) in cat_style.items():
        xs = [fnum(s["yaw"]) for s in seeds if s["category"] == cat]
        ys = [fnum(s["pitch"]) for s in seeds if s["category"] == cat]
        if xs:
            ax.scatter(xs, ys, marker=mk, c=col, s=sz, edgecolors="black",
                       linewidths=0.6, label=f"{cat} ({len(xs)})", zorder=5)
    ax.set_xlabel("yaw (deg)")
    ax.set_ylabel("pitch (deg)")
    ax.set_title("Three-axis search seeds on fixed-roll yaw-pitch map\n"
                 "(background = OCS brightness; markers = seed categories)")
    ax.legend(loc="center left", bbox_to_anchor=(1.18, 0.5), fontsize=8, framealpha=0.9)
    ax.set_xlim(-10, 360)
    ax.set_ylim(-95, 95)
    plt.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, "figures", f"seed_map_fixedroll.{ext}"),
                    dpi=140, bbox_inches="tight")
    plt.close(fig)

    # ---- 图2：brightness vs information ----
    # x=log brightness, y=gain_g1_to_g5 (information proxy), color=neural_entropy
    b = []
    info = []
    ent = []
    for r in master:
        gv = fnum(r["gain_g1_to_g5"])
        bv = fnum(r["ocs_total_phase63"])
        ev = fnum(r["neural_entropy"])
        if not np.isnan(gv) and not np.isnan(bv) and bv > 0:
            b.append(np.log10(bv))
            info.append(gv)
            ent.append(ev if not np.isnan(ev) else 0.0)
    b = np.array(b); info = np.array(info); ent = np.array(ent)

    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(b, info, c=ent, cmap="plasma", s=22, alpha=0.7, edgecolors="none")
    cb = plt.colorbar(sc, ax=ax)
    cb.set_label("neural entropy (candidate spread)")
    ax.axhline(0, color="gray", ls="--", lw=1)
    ax.set_xlabel("log10 OCS brightness (phase63)")
    ax.set_ylabel("G1->G5 OCS gain (deg)  = information / recoverability proxy")
    ax.set_title("Brightness vs Information decoupling\n"
                 "(bright != high-info: high brightness does not imply positive multi-geometry gain)")
    # 标注：亮但低信息 / 暗但高信息
    ax.text(0.02, 0.02, "note: brightest attitudes are NOT necessarily the most recoverable",
            transform=ax.transAxes, fontsize=8, color="dimgray")
    plt.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, "figures", f"brightness_vs_information.{ext}"),
                    dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 相关性数字（供 boundary 文档引用）
    if len(b) > 2:
        corr = float(np.corrcoef(b, info)[0, 1])
    else:
        corr = float("nan")
    print("[C-fig] figures done.")
    print(f"  corr(log_brightness, gain_g1_g5) = {corr:.3f}")
    with open(os.path.join(OUT, "logs", "brightness_info_corr.txt"), "w", encoding="utf-8") as f:
        f.write(f"corr(log10_ocs_brightness_phase63, gain_g1_to_g5) = {corr:.4f}\n")
        f.write(f"n_attitudes_with_both = {len(b)}\n")


if __name__ == "__main__":
    main()

"""
build_outlier_gallery_12g.py — 实验12g：U1 / 12b 离群案例画廊与审计包
================================================================================
目的（指导文件 §8）：
  整理实验12b U1 augmented fusion 的 rare large outliers，作为 Supplementary 与
  Limitations 的防御材料，防止 fully robust / near-perfect 误读。

输入（复用 12b，不重训练）：
  论文改进/补充实验/结果/fusion_fallback_isolation_12b/run_*/u1_outlier_audit.csv
  论文改进/补充实验/结果/fusion_fallback_isolation_12b/run_*/u1_outlier_audit.json
  渲染图像：结果/模块B_渲染/run_20260528_101944_exact_brdf/（用于代表性缩略图）

输出（结果/outlier_gallery_12g/run_YYYYMMDD_HHMMSS/）：
  - outlier_full_table.csv         42 条 >30° 离群全表（+ 复制 12b 原表口径）
  - threshold_summary.json/.csv    >30/60/90° 计数与占比、姿态/退化/seed 分布
  - fig1_yaw_pitch_distribution.png  离群在 yaw-pitch 空间分布（标注 |pitch|>75° 极区）
  - fig2_degradation_distribution.png 离群在退化档分布
  - fig3_seed_sample_repeat_heatmap.png  seed×sample 跨退化重复矩阵
  - fig4_representative_outliers.png   6-8 张代表性 outlier 渲染缩略图（true vs pred 标注）
  - gallery_12g_summary.md          机制/写作边界总结

红线（指导文件 §10）：不写 fully robust / near-perfect；只写 mean/p90/Hit@5 stabilized,
       rare large outliers remain, concentrated near polar attitudes。
本脚本不训练、不评估模型，仅整理既有 12b 审计产物。
"""

import argparse
import csv
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

_12B_GLOB = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                         "fusion_fallback_isolation_12b", "run_*")
_IMAGE_DIR = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染",
                          "run_20260528_101944_exact_brdf")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果", "outlier_gallery_12g")

EVAL_DEG_ORDER = ["clean", "noise_0.01", "noise_0.10", "bright_0.50", "bright_1.50"]


def find_latest_12b():
    cands = sorted(glob.glob(_12B_GLOB), key=os.path.getmtime, reverse=True)
    for c in cands:
        if os.path.exists(os.path.join(c, "u1_outlier_audit.csv")):
            return c
    raise FileNotFoundError(f"未找到含 u1_outlier_audit.csv 的 12b run：{_12B_GLOB}")


def load_audit(run_dir):
    rows = []
    with open(os.path.join(run_dir, "u1_outlier_audit.csv"), "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "seed": int(r["seed"]),
                "sample_index": int(r["sample_index"]),
                "yaw_true": float(r["yaw_true"]),
                "pitch_true": float(r["pitch_true"]),
                "degradation": r["degradation"],
                "error_deg": float(r["error_deg"]),
                "pred_yaw": float(r["pred_yaw"]),
                "pred_pitch": float(r["pred_pitch"]),
                "is_repeated_outlier_across_degs":
                    str(r["is_repeated_outlier_across_degs"]).strip().lower() == "true",
            })
    with open(os.path.join(run_dir, "u1_outlier_audit.json"), "r", encoding="utf-8") as f:
        audit_json = json.load(f)
    return rows, audit_json.get("summary", {})


def build_index_to_image(image_dir):
    """读取 render_log.csv，返回 index -> (out_prefix, image_path)。
    与 run_resnet_fusion.load_images 的行序一致（同一 render_log.csv 顺序）。"""
    csv_path = os.path.join(image_dir, "render_log.csv")
    mapping = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f)):
            prefix = r.get("out_prefix", r.get("filename", ""))
            path = os.path.join(image_dir, "brdf_images", prefix + "_brdf.png")
            mapping[i] = (prefix, path, float(r["yaw"]), float(r["pitch"]))
    return mapping


# ============================================================
# 统计
# ============================================================
def compute_threshold_summary(rows, summary_12b):
    """阈值/姿态/退化/seed 分布。>30° 直接来自 42 条全表；
    >60/>90 计数沿用 12b summary（基于全 49,950 评估，本脚本无逐样本全表）。"""
    err = np.array([r["error_deg"] for r in rows])
    pit = np.array([r["pitch_true"] for r in rows])
    yaw = np.array([r["yaw_true"] for r in rows])

    deg_counts = defaultdict(int)
    for r in rows:
        deg_counts[r["degradation"]] += 1
    seed_counts = defaultdict(int)
    for r in rows:
        seed_counts[r["seed"]] += 1

    out = {
        "source_12b_summary": summary_12b,
        "n_outlier_records_gt30": len(rows),
        "error_gt30_in_table": int((err > 30).sum()),
        "error_gt60_in_table": int((err > 60).sum()),
        "error_gt90_in_table": int((err > 90).sum()),
        "error_gt150_in_table": int((err > 150).sum()),
        "pitch_abs_gt75_frac": float(np.mean(np.abs(pit) > 75)),
        "pitch_abs_gt60_frac": float(np.mean(np.abs(pit) > 60)),
        "pitch_abs_eq90_frac": float(np.mean(np.abs(pit) >= 89.9)),
        "degradation_distribution": dict(deg_counts),
        "seed_distribution": {int(k): v for k, v in seed_counts.items()},
        "n_repeated_across_degs_records": int(sum(1 for r in rows
                                                  if r["is_repeated_outlier_across_degs"])),
        "unique_repeated_seed_sample": sorted(
            {(r["seed"], r["sample_index"]) for r in rows
             if r["is_repeated_outlier_across_degs"]}),
    }
    return out


# ============================================================
# 图
# ============================================================
def fig_yaw_pitch(rows, out_dir):
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    deg_color = {d: c for d, c in zip(
        EVAL_DEG_ORDER, ["#1f77b4", "#ff7f0e", "#d62728", "#2ca02c", "#9467bd"])}
    # 全姿态网格背景（淡）
    ax.axhspan(75, 90, color="#ffe0e0", alpha=0.5, zorder=0)
    ax.axhspan(-90, -75, color="#ffe0e0", alpha=0.5, zorder=0, label="|pitch|>75deg polar zone")
    for d in EVAL_DEG_ORDER:
        sub = [r for r in rows if r["degradation"] == d]
        if not sub:
            continue
        ax.scatter([r["yaw_true"] for r in sub], [r["pitch_true"] for r in sub],
                   s=55, c=deg_color[d], edgecolors="k", linewidths=0.4,
                   alpha=0.85, label=d, zorder=3)
    ax.set_xlim(-10, 370)
    ax.set_ylim(-95, 95)
    ax.set_xlabel("yaw (deg)")
    ax.set_ylabel("pitch (deg)")
    ax.set_title("U1 fusion large-error outliers (err>30deg) in yaw-pitch space")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig1_yaw_pitch_distribution.png"), dpi=150)
    plt.close(fig)


def fig_degradation(rows, out_dir):
    counts = [sum(1 for r in rows if r["degradation"] == d) for d in EVAL_DEG_ORDER]
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    bars = ax.bar(EVAL_DEG_ORDER, counts, color="#4c72b0", edgecolor="k", linewidth=0.5)
    for b, c in zip(bars, counts):
        ax.text(b.get_x() + b.get_width() / 2, c + 0.1, str(c),
                ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("# outlier records (err>30deg)")
    ax.set_title("Outlier count by degradation condition")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig2_degradation_distribution.png"), dpi=150)
    plt.close(fig)


def fig_seed_sample_heatmap(rows, out_dir):
    """seed × unique-sample 矩阵：cell = 该 (seed,sample) 在多少退化档出现 >30° 离群。"""
    samples = sorted({r["sample_index"] for r in rows})
    seeds = sorted({r["seed"] for r in rows})
    s_idx = {s: i for i, s in enumerate(samples)}
    se_idx = {s: i for i, s in enumerate(seeds)}
    M = np.zeros((len(seeds), len(samples)), dtype=int)
    for r in rows:
        M[se_idx[r["seed"]], s_idx[r["sample_index"]]] += 1
    # sample_index -> (yaw,pitch) 标签
    pose_of = {}
    for r in rows:
        pose_of[r["sample_index"]] = (r["yaw_true"], r["pitch_true"])
    fig, ax = plt.subplots(figsize=(max(7.0, 0.45 * len(samples)), 2.8))
    im = ax.imshow(M, aspect="auto", cmap="OrRd", vmin=0, vmax=max(1, M.max()))
    ax.set_xticks(range(len(samples)))
    xlabels = [f"{s}\n({int(pose_of[s][0])},{int(pose_of[s][1])})" for s in samples]
    ax.set_xticklabels(xlabels, fontsize=5, rotation=90)
    ax.set_yticks(range(len(seeds)))
    ax.set_yticklabels([f"seed {s}" for s in seeds], fontsize=8)
    ax.set_xlabel("sample_index (yaw,pitch)")
    ax.set_title("Cross-degradation repeat: #deg-conditions with err>30deg per (seed,sample)")
    for i in range(len(seeds)):
        for j in range(len(samples)):
            if M[i, j] > 0:
                ax.text(j, i, M[i, j], ha="center", va="center", fontsize=6,
                        color="black" if M[i, j] < M.max() else "white")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01, label="#deg conditions")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig3_seed_sample_repeat_heatmap.png"), dpi=150)
    plt.close(fig)


def fig_representative(rows, idx2img, out_dir, n_show=8):
    """挑代表性离群（优先跨退化重复 + 误差最大），渲染干净图缩略图。"""
    from PIL import Image
    # 唯一 (seed,sample) 取其 clean 档（或任一档）误差最大记录
    by_ss = {}
    for r in rows:
        key = (r["seed"], r["sample_index"])
        if key not in by_ss or r["error_deg"] > by_ss[key]["error_deg"]:
            by_ss[key] = r
    uniq = list(by_ss.values())
    # 排序：重复优先，再按误差降序
    uniq.sort(key=lambda r: (not r["is_repeated_outlier_across_degs"], -r["error_deg"]))
    chosen = uniq[:n_show]

    ncol = 4
    nrow = int(np.ceil(len(chosen) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.0 * ncol, 3.0 * nrow))
    axes = np.atleast_1d(axes).ravel()
    for k, r in enumerate(chosen):
        ax = axes[k]
        gi = r["sample_index"]
        info = idx2img.get(gi)
        if info and os.path.exists(info[1]):
            arr = np.asarray(Image.open(info[1]).convert("L"), dtype=np.float32) / 255.0
            # 与训练同款 log1p 强度映射 + gamma，提升暗目标可见度
            arr = np.log1p(10.0 * arr) / np.log1p(10.0)
            ax.imshow(arr ** 0.5, cmap="gray", vmin=0, vmax=1)
        else:
            ax.text(0.5, 0.5, "image\nnot found", ha="center", va="center")
        rep = "*" if r["is_repeated_outlier_across_degs"] else ""
        ax.set_title(f"s{r['seed']} #{gi}{rep}\n"
                     f"true({r['yaw_true']:.0f},{r['pitch_true']:.0f}) "
                     f"pred({r['pred_yaw']:.0f},{r['pred_pitch']:.0f})\n"
                     f"{r['degradation']} err={r['error_deg']:.0f}deg",
                     fontsize=7)
        ax.set_xticks([]); ax.set_yticks([])
    for k in range(len(chosen), len(axes)):
        axes[k].axis("off")
    fig.suptitle("Representative U1 fusion outliers (clean rendered image; * = repeated across degradations)",
                 fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(out_dir, "fig4_representative_outliers.png"), dpi=150)
    plt.close(fig)


# ============================================================
# 保存
# ============================================================
def save_full_table(rows, out_dir):
    keys = ["seed", "sample_index", "yaw_true", "pitch_true", "degradation",
            "error_deg", "pred_yaw", "pred_pitch", "is_repeated_outlier_across_degs"]
    rows_sorted = sorted(rows, key=lambda r: (-r["error_deg"]))
    with open(os.path.join(out_dir, "outlier_full_table.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows_sorted:
            w.writerow({k: r[k] for k in keys})


def write_summary_md(out_dir, rows, thr, summary_12b, src_run):
    L = []
    L.append("# 实验12g：U1 / 12b 离群案例画廊与审计包\n")
    L.append(f"> 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    L.append(f"> 数据来源（不重训练）：`{os.path.relpath(src_run, _PROJECT_ROOT)}`  ")
    L.append("> 本脚本仅整理实验12b U1 augmented fusion 的离群审计，"
             "用于 Supplementary / Limitations 防御。\n")

    L.append("## 1. 阈值统计（来自 12b，全 49,950 评估）\n")
    s12 = summary_12b.get("thresholds", {})
    if s12:
        L.append("| 阈值 | 计数 | 占比 |")
        L.append("|---|---:|---:|")
        for k, lab in [("gt_30", ">30deg"), ("gt_60", ">60deg"), ("gt_90", ">90deg")]:
            if k in s12:
                L.append(f"| {lab} | {s12[k]['count']} | {s12[k]['frac']:.3%} |")
        L.append(f"\n> 评估总数 = {summary_12b.get('n_eval_total', 'NA')}"
                 f"（5 seeds × 5 退化档 × test）。\n")

    L.append("## 2. 42 条 >30deg 离群表分布\n")
    L.append(f"- 离群记录数（>30deg）：{thr['n_outlier_records_gt30']}")
    L.append(f"- 其中 >60deg：{thr['error_gt60_in_table']}；>90deg：{thr['error_gt90_in_table']}；"
             f">150deg：{thr['error_gt150_in_table']}")
    L.append(f"- |pitch|>75deg（极区）占比：{thr['pitch_abs_gt75_frac']:.1%}；"
             f"|pitch|=90deg（极点）占比：{thr['pitch_abs_eq90_frac']:.1%}")
    L.append(f"- 退化档分布：{thr['degradation_distribution']}")
    L.append(f"- seed 分布：{thr['seed_distribution']}")
    L.append(f"- 跨退化重复离群记录数：{thr['n_repeated_across_degs_records']}；"
             f"唯一重复 (seed,sample) 数：{len(thr['unique_repeated_seed_sample'])}")
    L.append(f"- 唯一重复 (seed,sample)：{thr['unique_repeated_seed_sample']}\n")

    L.append("## 3. 图\n")
    L.append("- `fig1_yaw_pitch_distribution.png`：离群在 yaw-pitch 空间，红带为 |pitch|>75deg 极区。")
    L.append("- `fig2_degradation_distribution.png`：离群按退化档计数（noise_0.10 应最多）。")
    L.append("- `fig3_seed_sample_repeat_heatmap.png`：seed×sample 跨退化重复矩阵。")
    L.append("- `fig4_representative_outliers.png`：6-8 张代表性离群干净渲染图（true vs pred）。\n")

    L.append("## 4. 写作边界（红线）\n")
    L.append("可写：")
    L.append("```text")
    L.append("U1 stabilizes mean / p90 / Hit@5 under the tested degradations, but rare large")
    L.append("outliers remain (<0.1% of evaluations). These outliers concentrate near polar")
    L.append("attitudes (|pitch|>75deg) and several recur across degradation conditions for the")
    L.append("same seed-sample, indicating a pose-conditioned failure mode rather than purely")
    L.append("noise-driven randomness.")
    L.append("```")
    L.append("禁止写：fully robust / near-perfect / no failures / 完全鲁棒。\n")

    with open(os.path.join(out_dir, "gallery_12g_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description="Exp12g: U1/12b outlier gallery & audit")
    ap.add_argument("--src-run", default=None, help="指定 12b run 目录；默认自动找最新")
    ap.add_argument("--image-dir", default=_IMAGE_DIR)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--n-show", type=int, default=8)
    args = ap.parse_args()

    src_run = args.src_run or find_latest_12b()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    log_f = open(os.path.join(out_dir, "run.log"), "w", encoding="utf-8", buffering=1)

    class Tee:
        def __init__(self, *s): self.s = s
        def write(self, x):
            for st in self.s:
                try: st.write(x); st.flush()
                except Exception: pass
        def flush(self):
            for st in self.s:
                try: st.flush()
                except Exception: pass
    sys.stdout = Tee(sys.__stdout__, log_f)

    print("=" * 70)
    print("  实验12g：U1 / 12b 离群案例画廊与审计包")
    print(f"  12b 源: {src_run}")
    print(f"  输出:   {out_dir}")
    print("=" * 70)

    rows, summary_12b = load_audit(src_run)
    print(f"  载入 {len(rows)} 条 >30deg 离群记录")

    thr = compute_threshold_summary(rows, summary_12b)
    print(f"  >60deg(表内)={thr['error_gt60_in_table']}  >90deg(表内)={thr['error_gt90_in_table']}  "
          f"|pitch|>75deg={thr['pitch_abs_gt75_frac']:.1%}")
    print(f"  退化分布={thr['degradation_distribution']}")
    print(f"  唯一重复(seed,sample)={thr['unique_repeated_seed_sample']}")

    # 保存
    save_full_table(rows, out_dir)
    with open(os.path.join(out_dir, "threshold_summary.json"), "w", encoding="utf-8") as f:
        json.dump(thr, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "threshold_summary.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k in ["n_outlier_records_gt30", "error_gt60_in_table", "error_gt90_in_table",
                  "error_gt150_in_table", "pitch_abs_gt75_frac", "pitch_abs_gt60_frac",
                  "pitch_abs_eq90_frac", "n_repeated_across_degs_records"]:
            w.writerow([k, thr[k]])

    # 图
    print("  绘图...")
    fig_yaw_pitch(rows, out_dir)
    fig_degradation(rows, out_dir)
    try:
        fig_seed_sample_heatmap(rows, out_dir)
    except Exception as e:
        print(f"  [warn] heatmap 失败: {e}")
    try:
        idx2img = build_index_to_image(args.image_dir)
        fig_representative(rows, idx2img, out_dir, n_show=args.n_show)
    except Exception as e:
        print(f"  [warn] 代表性缩略图失败: {e}")

    write_summary_md(out_dir, rows, thr, summary_12b, src_run)
    print(f"\n  完成。输出: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

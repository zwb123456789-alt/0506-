#!/usr/bin/env python3
"""
postprocess_b6_circular_metrics.py — 1C-B6-FIX01 后处理与 fold-matched 对照

读取 v0.4_results/10_b6_circular_regression_fix01/<run>/ 下的
  metrics_test_{final,best}.json 与 samples_test_{final,best}.npz，
对 final / best 两套口径各生成：
  - b6_run_metrics_summary_{tag}.csv        每个 run 的关键指标
  - b6_foldmatched_vs_p1a_{tag}.csv         B6 fold k vs P1-A 同 fold 同对应通道（主裁决）
  - b6_pooled_vs_p1a_{tag}.csv              B6 跨 fold pooled vs P1-A pooled（仅补充）
  - b6_yawblock_stratified_{tag}.csv        yaw-block 分层
  - b6_pitchband_stratified_{tag}.csv       pitch-band 分层
并生成统一汇总：
  - b6_fix01_postprocess_summary.json       含 per-fold mean / pooled / best-worst fold / best-worst yaw-block

baseline 来源（只读，不覆盖）：
  v0.4_results/09_p1a_metric_recompute/p1a_channel_fold_metrics.csv   （fold-matched 主对照）
  v0.4_results/09_p1a_metric_recompute/p1a_channel_pooled_metrics.csv （pooled 补充）
  v0.4_results/09_p1a_metric_recompute/p1a_random_baseline.json       （chance 参照）

fold-matched 映射：
  image_only -> C3_image_only
  joint      -> C3_joint
  ocs_only   -> C2_baseline_4dim
P1-A 的 circular_mae 单位是 bin（×5° 才是度），本脚本统一换算到度。
delta = B6 - P1A，负值表示 B6 更好。
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
B6_DIR = PROJECT_ROOT / "v0.4_results" / "10_b6_circular_regression_fix01"
P1A_DIR = PROJECT_ROOT / "v0.4_results" / "09_p1a_metric_recompute"
YAW_STEP = 5.0
N_YAW = 72
YAW_BLOCK = 45.0
PITCH_BAND = 30.0
TAGS = ["final", "best"]
CH_MAP = {"image_only": "C3_image_only", "joint": "C3_joint",
          "ocs_only": "C2_baseline_4dim"}


# ── baseline 读取 ────────────────────────────────────────

def load_p1a_fold():
    """P1-A per-fold baseline，键 (channel,fold)，circular_mae 换算到度。"""
    d = {}
    with open(P1A_DIR / "p1a_channel_fold_metrics.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[(r["channel"], int(r["fold"]))] = {
                "n": int(r["n_samples"]),
                "exact_bin": float(r["exact_bin"]),
                "circular_mae_deg": float(r["circular_mae_bins"]) * YAW_STEP,
                "within_1bin": float(r["within_1bin"]),
                "within_2bins": float(r["within_2bins"]),
                "within_6bins": float(r["within_6bins"]),
                "coarse45": float(r["coarse45"]),
                "coarse90": float(r["coarse90"]),
            }
    return d


def load_p1a_pooled():
    d = {}
    with open(P1A_DIR / "p1a_channel_pooled_metrics.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[r["channel"]] = {
                "exact_bin": float(r["exact_bin"]),
                "circular_mae_deg": float(r["circular_mae_bins"]) * YAW_STEP,
                "within_2bins": float(r["within_2bins"]),
                "within_6bins": float(r["within_6bins"]),
                "coarse45": float(r["coarse45"]),
                "coarse90": float(r["coarse90"]),
            }
    rand = json.load(open(P1A_DIR / "p1a_random_baseline.json", encoding="utf-8"))
    d["random_chance"] = {
        "exact_bin": rand["random_exact_bin"],
        "circular_mae_deg": rand["random_circular_mae_bins"] * YAW_STEP,
        "within_2bins": rand["random_within_2bins"],
        "coarse90": rand["random_coarse90"],
    }
    return d


# ── 从样本级 npz 计算（用于 pooled 与分层）────────────────

def metrics_from_samples(yce, pae, yt_bin, yp_bin, yaw_true, yaw_pred):
    """从样本级数组计算关键指标（与训练脚本 compute_metrics 同口径）。"""
    bin_diff = np.abs(yp_bin - yt_bin)
    bin_cdist = np.minimum(bin_diff, N_YAW - bin_diff)
    c90 = (np.floor((yaw_pred % 360) / 90.0) == np.floor((yaw_true % 360) / 90.0))
    c45 = (np.floor((yaw_pred % 360) / 45.0) == np.floor((yaw_true % 360) / 45.0))
    return {
        "n": int(len(yce)),
        "yaw_cmae_deg": float(yce.mean()),
        "yaw_median_deg": float(np.median(yce)),
        "yaw_p90_deg": float(np.percentile(yce, 90)),
        "yaw_hit@5": float((yce <= 5).mean()),
        "yaw_hit@10": float((yce <= 10).mean()),
        "yaw_hit@30": float((yce <= 30).mean()),
        "yaw_within_1bin": float((bin_cdist <= 1).mean()),
        "yaw_within_2bin": float((bin_cdist <= 2).mean()),
        "yaw_within_6bin": float((bin_cdist <= 6).mean()),
        "yaw_exact_sentinel": float((bin_cdist == 0).mean()),
        "yaw_coarse45": float(c45.mean()),
        "yaw_coarse90": float(c90.mean()),
        "pitch_mae_deg": float(pae.mean()),
        "pitch_hit@5": float((pae <= 5).mean()),
        "pitch_hit@10": float((pae <= 10).mean()),
        "pitch_hit@30": float((pae <= 30).mean()),
    }


def discover_runs(tag):
    runs = []
    if not B6_DIR.exists():
        return runs
    for d in sorted(B6_DIR.iterdir()):
        if d.is_dir() and (d / f"metrics_test_{tag}.json").exists():
            runs.append(d)
    return runs


def round_row(r, nd=4):
    out = {}
    for k, v in r.items():
        out[k] = round(v, nd) if isinstance(v, float) else v
    return out


def process_tag(tag, p1a_fold, p1a_pooled):
    runs = discover_runs(tag)
    if not runs:
        print(f"[WARN] tag={tag} 未发现 run。")
        return None
    print(f"[{tag}] 发现 {len(runs)} 个 run: {[r.name for r in runs]}")

    # 载入每个 run 的样本与指标
    records = []
    for d in runs:
        cfg = json.load(open(d / "run_config.json", encoding="utf-8"))
        m = json.load(open(d / f"metrics_test_{tag}.json", encoding="utf-8"))
        s = np.load(d / f"samples_test_{tag}.npz", allow_pickle=True)
        records.append({
            "dir": d, "name": d.name,
            "mode": cfg["mode"], "fold": int(cfg["fold"]), "aug": cfg["aug"],
            "best_epoch": m.get("best_epoch", -1),
            "metrics": m, "s": s,
        })

    # ── 1. run 级汇总 ──
    summary_rows = []
    for r in records:
        m = r["metrics"]
        summary_rows.append(round_row({
            "run": r["name"], "mode": r["mode"], "fold": r["fold"], "aug": r["aug"],
            "select": tag, "best_epoch": r["best_epoch"], "n_test": m["n"],
            "yaw_cmae_deg": m["yaw_circular_mae_deg"],
            "yaw_median_deg": m["yaw_median_ae_deg"],
            "yaw_p90_deg": m["yaw_p90_ae_deg"],
            "yaw_hit@5": m["yaw_hit@5"], "yaw_hit@10": m["yaw_hit@10"],
            "yaw_hit@30": m["yaw_hit@30"],
            "yaw_within_1bin": m["yaw_within_1bin_sentinel"],
            "yaw_within_2bin": m["yaw_within_2bin_sentinel"],
            "yaw_within_6bin": m["yaw_within_6bin_sentinel"],
            "yaw_exact_sentinel": m["yaw_exact_bin_sentinel"],
            "yaw_coarse45": m["yaw_coarse45_acc"], "yaw_coarse90": m["yaw_coarse90_acc"],
            "pitch_mae_deg": m["pitch_mae_deg"],
            "pitch_hit@5": m["pitch_hit@5"], "pitch_hit@10": m["pitch_hit@10"],
            "pitch_hit@30": m["pitch_hit@30"],
            "pitch_exact_sentinel": m["pitch_exact_bin_sentinel"],
        }, 4))
    write_csv(B6_DIR / f"b6_run_metrics_summary_{tag}.csv", summary_rows)

    # ── 2. fold-matched vs P1-A（主裁决）──
    fm_rows = []
    for r in records:
        m = r["metrics"]
        ch = CH_MAP[r["mode"]]
        base = p1a_fold.get((ch, r["fold"]))
        b6_cmae = m["yaw_circular_mae_deg"]
        b6_w2 = m["yaw_within_2bin_sentinel"]
        b6_c90 = m["yaw_coarse90_acc"]
        row = {
            "run": r["name"], "mode": r["mode"], "fold": r["fold"], "aug": r["aug"],
            "matched_channel": ch, "select": tag,
            "b6_yaw_cmae_deg": round(b6_cmae, 3),
            "p1a_yaw_cmae_deg": round(base["circular_mae_deg"], 3) if base else None,
            "delta_yaw_cmae_deg": round(b6_cmae - base["circular_mae_deg"], 3) if base else None,
            "b6_yaw_within_2bin": round(b6_w2, 4),
            "p1a_yaw_within_2bin": round(base["within_2bins"], 4) if base else None,
            "delta_within_2bin": round(b6_w2 - base["within_2bins"], 4) if base else None,
            "b6_yaw_coarse90": round(b6_c90, 4),
            "p1a_yaw_coarse90": round(base["coarse90"], 4) if base else None,
            "delta_coarse90": round(b6_c90 - base["coarse90"], 4) if base else None,
            "b6_yaw_hit@30": round(m["yaw_hit@30"], 4),
            "b6_pitch_mae_deg": round(m["pitch_mae_deg"], 3),
        }
        fm_rows.append(row)
    write_csv(B6_DIR / f"b6_foldmatched_vs_p1a_{tag}.csv", fm_rows)

    # ── 3. pooled vs P1-A（补充）：按 (mode,aug) 跨 fold 拼接样本重算 ──
    pooled_groups = defaultdict(list)
    for r in records:
        pooled_groups[(r["mode"], r["aug"])].append(r)
    pooled_rows = []
    for (mode, aug), rs in sorted(pooled_groups.items()):
        cat = lambda key: np.concatenate([rr["s"][key] for rr in rs])
        pm = metrics_from_samples(
            cat("yaw_circular_error_deg"), cat("pitch_abs_error_deg"),
            cat("yaw_true_bin"), cat("yaw_pred_bin_sentinel"),
            cat("yaw_true_deg"), cat("yaw_pred_deg"))
        ch = CH_MAP[mode]
        base = p1a_pooled.get(ch, {})
        rand = p1a_pooled["random_chance"]
        pooled_rows.append(round_row({
            "mode": mode, "aug": aug, "select": tag, "n_folds": len(rs),
            "n_pooled": pm["n"],
            "b6_yaw_cmae_deg": pm["yaw_cmae_deg"],
            "p1a_pooled_yaw_cmae_deg": base.get("circular_mae_deg", float("nan")),
            "delta_yaw_cmae_deg": pm["yaw_cmae_deg"] - base.get("circular_mae_deg", float("nan")),
            "random_yaw_cmae_deg": rand["circular_mae_deg"],
            "b6_yaw_within_2bin": pm["yaw_within_2bin"],
            "p1a_pooled_within_2bin": base.get("within_2bins", float("nan")),
            "b6_yaw_coarse90": pm["yaw_coarse90"],
            "p1a_pooled_coarse90": base.get("coarse90", float("nan")),
            "random_coarse90": rand["coarse90"],
            "b6_yaw_hit@30": pm["yaw_hit@30"],
            "b6_pitch_mae_deg": pm["pitch_mae_deg"],
        }, 4))
    write_csv(B6_DIR / f"b6_pooled_vs_p1a_{tag}.csv", pooled_rows)

    # ── 4. yaw-block / pitch-band 分层 ──
    yawblock_rows, pitchband_rows = [], []
    for r in records:
        s = r["s"]
        yaw_true = s["yaw_true_deg"]; yce = s["yaw_circular_error_deg"]
        pitch_true = s["pitch_true_deg"]; pae = s["pitch_abs_error_deg"]
        blocks = (np.floor((yaw_true % 360) / YAW_BLOCK) * YAW_BLOCK).astype(int)
        for b in sorted(np.unique(blocks)):
            mask = blocks == b
            yawblock_rows.append(round_row({
                "run": r["name"], "mode": r["mode"], "fold": r["fold"], "aug": r["aug"],
                "select": tag, "yaw_block_deg": f"[{b},{b+int(YAW_BLOCK)})",
                "n": int(mask.sum()),
                "yaw_cmae_deg": float(yce[mask].mean()),
                "yaw_median_deg": float(np.median(yce[mask])),
                "yaw_hit@10": float((yce[mask] <= 10).mean()),
                "yaw_hit@30": float((yce[mask] <= 30).mean()),
            }, 3))
        pbands = (np.floor((pitch_true + 90) / PITCH_BAND) * PITCH_BAND - 90).astype(int)
        for b in sorted(np.unique(pbands)):
            mask = pbands == b
            pitchband_rows.append(round_row({
                "run": r["name"], "mode": r["mode"], "fold": r["fold"], "aug": r["aug"],
                "select": tag, "pitch_band_deg": f"[{b},{b+int(PITCH_BAND)})",
                "n": int(mask.sum()),
                "pitch_mae_deg": float(pae[mask].mean()),
                "pitch_hit@10": float((pae[mask] <= 10).mean()),
            }, 3))
    write_csv(B6_DIR / f"b6_yawblock_stratified_{tag}.csv", yawblock_rows)
    write_csv(B6_DIR / f"b6_pitchband_stratified_{tag}.csv", pitchband_rows)

    # ── 5. per-fold mean / best-worst fold / best-worst yaw-block（per mode,aug）──
    agg = {}
    for (mode, aug), rs in sorted(pooled_groups.items()):
        cmaes = {rr["fold"]: rr["metrics"]["yaw_circular_mae_deg"] for rr in rs}
        deltas = {}
        for rr in rs:
            base = p1a_fold.get((CH_MAP[mode], rr["fold"]))
            if base:
                deltas[rr["fold"]] = rr["metrics"]["yaw_circular_mae_deg"] - base["circular_mae_deg"]
        best_fold = min(cmaes, key=cmaes.get)
        worst_fold = max(cmaes, key=cmaes.get)
        # best/worst yaw-block 跨该组所有 fold
        block_acc = defaultdict(list)
        for rr in rs:
            yt = rr["s"]["yaw_true_deg"]; yce = rr["s"]["yaw_circular_error_deg"]
            blocks = (np.floor((yt % 360) / YAW_BLOCK) * YAW_BLOCK).astype(int)
            for b in np.unique(blocks):
                block_acc[int(b)].append(float(yce[blocks == b].mean()))
        block_mean = {b: float(np.mean(v)) for b, v in block_acc.items()}
        best_block = min(block_mean, key=block_mean.get)
        worst_block = max(block_mean, key=block_mean.get)
        agg[f"{mode}|{aug}"] = {
            "n_folds": len(rs),
            "folds_present": sorted(cmaes.keys()),
            "per_fold_yaw_cmae_deg": {str(k): round(v, 3) for k, v in sorted(cmaes.items())},
            "per_fold_mean_yaw_cmae_deg": round(float(np.mean(list(cmaes.values()))), 3),
            "per_fold_delta_vs_p1a_deg": {str(k): round(v, 3) for k, v in sorted(deltas.items())},
            "per_fold_mean_delta_deg": (round(float(np.mean(list(deltas.values()))), 3)
                                        if deltas else None),
            "best_fold": int(best_fold), "best_fold_cmae_deg": round(cmaes[best_fold], 3),
            "worst_fold": int(worst_fold), "worst_fold_cmae_deg": round(cmaes[worst_fold], 3),
            "best_yaw_block": f"[{best_block},{best_block+int(YAW_BLOCK)})",
            "best_yaw_block_cmae_deg": round(block_mean[best_block], 3),
            "worst_yaw_block": f"[{worst_block},{worst_block+int(YAW_BLOCK)})",
            "worst_yaw_block_cmae_deg": round(block_mean[worst_block], 3),
        }

    return {
        "tag": tag,
        "n_runs": len(records),
        "runs": [r["name"] for r in records],
        "run_summary": summary_rows,
        "foldmatched_vs_p1a": fm_rows,
        "pooled_vs_p1a": pooled_rows,
        "aggregate_per_mode_aug": agg,
    }


def write_csv(path, rows):
    if not rows:
        print(f"[WARN] 空表跳过：{path.name}")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"写出 {path.name}（{len(rows)} 行）")


def main():
    p1a_fold = load_p1a_fold()
    p1a_pooled = load_p1a_pooled()
    out = {"task": "1C-B6-FIX01_postprocess",
           "baseline_fold_source": str(P1A_DIR / "p1a_channel_fold_metrics.csv"),
           "baseline_pooled_source": str(P1A_DIR / "p1a_channel_pooled_metrics.csv"),
           "baseline_note": "P1-A circular_mae 单位 bin，已×5° 换算到度。fold-matched 为主裁决，pooled 仅补充。",
           "fold_matched_mapping": CH_MAP,
           "tags": {}}
    for tag in TAGS:
        res = process_tag(tag, p1a_fold, p1a_pooled)
        if res:
            out["tags"][tag] = res

    with open(B6_DIR / "b6_fix01_postprocess_summary.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("写出 b6_fix01_postprocess_summary.json")

    # 控制台打印 fold-matched 主对照（final）
    if "final" in out["tags"]:
        print("\n=== fold-matched B6(final) vs P1-A (yaw cMAE, 度；delta<0 表示 B6 更好) ===")
        print(f"{'mode':12s}{'aug':10s}{'fold':>5s}{'B6':>9s}{'P1A':>9s}{'delta':>9s}")
        for r in out["tags"]["final"]["foldmatched_vs_p1a"]:
            d = r["delta_yaw_cmae_deg"]
            print(f"{r['mode']:12s}{r['aug']:10s}{r['fold']:>5d}"
                  f"{r['b6_yaw_cmae_deg']:>9.2f}"
                  f"{(r['p1a_yaw_cmae_deg'] or float('nan')):>9.2f}"
                  f"{(d if d is not None else float('nan')):>9.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

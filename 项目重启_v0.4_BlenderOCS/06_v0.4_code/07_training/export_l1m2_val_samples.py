#!/usr/bin/env python3
"""
export_l1m2_val_samples.py —— R116 子任务 A1：补齐 L1M2 val per-attitude 输出

R115 抽查发现正式 run 有 metrics_val_*.json / samples_test_* 但缺 samples_val_*。
本脚本【不重训】，而是：
  1. 加载已保存 checkpoint_{final,best}.pt 的 model_state；
  2. 用与 train_l1m2_multigeometry.py 完全一致的确定性逻辑重建 split（seed 固定）；
  3. 在 val loader 上重算预测、置信中间量（posterior-like/top-k/entropy/margin）；
  4. 与已存 metrics_val_{final,best}.json 交叉校验（一致性判据）；
  5. 导出 samples_val_{final,best}.{csv,npz}，字段与 samples_test_* 对齐。

若某 run 的 checkpoint / split 不足以复现 val metrics，则记录缺口，不静默跳过。

用法：
  python export_l1m2_val_samples.py            # 处理全部 12 个正式 run
  python export_l1m2_val_samples.py --run P-INT_G5_ocs_only_seed42
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from dataset_l1m2_multigeometry import (  # noqa: E402
    build_multigeometry_table, fit_flux_transform, L1M2Dataset,
)
from train_l1m2_multigeometry import (  # noqa: E402
    L1M2RegModel, collect_predictions, compute_metrics,
    build_candidate_grid, posterior_like_scores, yaw_circ_err,
    split_pint, split_pext,
)
from torch.utils.data import DataLoader

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

L1M2_DIR = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
RUNS_DIR = L1M2_DIR / "runs"
OUT_DIR = PROJECT_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" / "audit"

# R115 的 12 个正式 run（9 P-INT + 3 P-EXT ocs_only）
FORMAL_RUNS = [
    "P-INT_G1_ocs_only_seed42", "P-INT_G3_ocs_only_seed42", "P-INT_G5_ocs_only_seed42",
    "P-INT_G1_image_only_seed42", "P-INT_G3_image_only_seed42", "P-INT_G5_image_only_seed42",
    "P-INT_G1_joint_seed42", "P-INT_G3_joint_seed42", "P-INT_G5_joint_seed42",
    "P-EXT_G1_ocs_only_seed42", "P-EXT_G3_ocs_only_seed42", "P-EXT_G5_ocs_only_seed42",
]

# metrics_val 校验容差（重建 split + 前向应当逐位复现，留极小数值容差）
CMAE_TOL = 0.5   # deg


def rebuild_val_loader(cfg):
    """按 run_config 完全确定性重建 (train, val) 并返回 val_loader + flux_tf + geoms。"""
    geom_group = cfg["geom_group"]
    mode = cfg["mode"]
    protocol = cfg["protocol"]
    seed = int(cfg["seed"])
    batch_size = int(cfg["batch_size"])

    table, geoms = build_multigeometry_table(geom_group)
    if protocol == "P-EXT":
        tr, va, te = split_pext(table)
    else:
        tr, va, te = split_pint(table, seed=seed)

    # flux transform 必须用 train 拟合（与训练时一致），保证 z-score 参数一致
    flux_tf = fit_flux_transform(tr) if mode in ("ocs_only", "joint") else None
    val_ds = L1M2Dataset(va, mode, flux_tf)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            num_workers=0, pin_memory=False)
    return val_loader, flux_tf, geoms, len(tr), len(va), len(te), cfg


def verify_flux_transform(flux_tf, cfg):
    """交叉校验重建的 flux_transform 与 run_config 保存的是否一致。"""
    saved = cfg.get("flux_transform")
    if saved is None or flux_tf is None:
        return True, "no_flux_transform"
    m_ok = np.allclose(flux_tf["mean"], saved["mean"], atol=1e-9)
    s_ok = np.allclose(flux_tf["std"], saved["std"], atol=1e-9)
    return (m_ok and s_ok), f"mean_ok={m_ok} std_ok={s_ok}"


def export_one(run_name, device):
    run_dir = RUNS_DIR / run_name
    cfg = json.load(open(run_dir / "run_config.json", encoding="utf-8"))
    ocs_dim = int(cfg["ocs_dim"])
    mode = cfg["mode"]

    val_loader, flux_tf, geoms, n_tr, n_va, n_te, cfg = rebuild_val_loader(cfg)

    rec = {"run": run_name, "geom_group": cfg["geom_group"], "mode": mode,
           "protocol": cfg["protocol"], "n_val_rebuilt": n_va,
           "n_val_config": int(cfg["n_val"])}

    # split 规模一致性
    rec["split_size_match"] = (n_va == int(cfg["n_val"]) and
                               n_tr == int(cfg["n_train"]) and
                               n_te == int(cfg["n_test"]))
    tf_ok, tf_note = verify_flux_transform(flux_tf, cfg)
    rec["flux_transform_match"] = tf_ok
    rec["flux_transform_note"] = tf_note

    grid = build_candidate_grid()
    results = {}
    for tag in ("final", "best"):
        ckpt_path = run_dir / f"checkpoint_{tag}.pt"
        if not ckpt_path.exists():
            rec[f"{tag}_status"] = "MISSING_CKPT"
            continue
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
        model = L1M2RegModel(mode, ocs_dim).to(device)
        model.load_state_dict(ckpt["model_state"])
        model.eval()

        yp, pp, yt, pt, rids = collect_predictions(model, val_loader, device)
        met = compute_metrics(yp, pp, yt, pt)

        # 与已存 metrics_val 交叉校验
        stored = json.load(open(run_dir / f"metrics_val_{tag}.json", encoding="utf-8"))
        d_cmae = abs(met["yaw_circular_mae_deg"] - stored["yaw_circular_mae_deg"])
        d_hit30 = abs(met["yaw_hit@30"] - stored["yaw_hit@30"])
        verified = (d_cmae <= CMAE_TOL) and (met["n"] == stored["n"])
        rec[f"{tag}_cmae_rebuilt"] = round(met["yaw_circular_mae_deg"], 4)
        rec[f"{tag}_cmae_stored"] = round(stored["yaw_circular_mae_deg"], 4)
        rec[f"{tag}_cmae_delta"] = round(d_cmae, 4)
        rec[f"{tag}_hit30_delta"] = round(d_hit30, 4)
        rec[f"{tag}_verified"] = bool(verified)
        rec[f"{tag}_status"] = "OK" if verified else "MISMATCH"

        # 置信中间量 + 导出
        scores, top5, ent, margin = posterior_like_scores(yp, pp, grid)
        yce = yaw_circ_err(yp, yt); pae = np.abs(pp - pt)
        np.savez(run_dir / f"samples_val_{tag}.npz",
                 record_id=np.array(rids),
                 yaw_true_deg=yt, pitch_true_deg=pt,
                 yaw_pred_deg=yp, pitch_pred_deg=pp,
                 yaw_circular_error_deg=yce, pitch_abs_error_deg=pae,
                 geometry_group=np.array([cfg["geom_group"]] * len(rids)),
                 mode=np.array([mode] * len(rids)),
                 protocol=np.array([cfg["protocol"]] * len(rids)),
                 posterior_like_top5_idx=top5,
                 posterior_like_top5_score=np.take_along_axis(scores, top5, axis=1),
                 entropy=ent, margin=margin, candidate_grid=grid)
        with open(run_dir / f"samples_val_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["record_id", "yaw_true_deg", "pitch_true_deg",
                        "yaw_pred_deg", "pitch_pred_deg",
                        "yaw_circular_error_deg", "pitch_abs_error_deg",
                        "geometry_group", "mode", "protocol",
                        "top1_grid_idx", "top1_score", "entropy", "margin"])
            for i in range(len(rids)):
                w.writerow([rids[i], f"{yt[i]:.3f}", f"{pt[i]:.3f}",
                            f"{yp[i]:.3f}", f"{pp[i]:.3f}",
                            f"{yce[i]:.3f}", f"{pae[i]:.3f}",
                            cfg["geom_group"], mode, cfg["protocol"],
                            int(top5[i, 0]), f"{scores[i, top5[i,0]]:.5f}",
                            f"{ent[i]:.4f}", f"{margin[i]:.5f}"])
        results[tag] = met
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=None, help="只处理单个 run；缺省处理全部 12 个")
    ap.add_argument("--device", default="auto")
    args = ap.parse_args()

    device = torch.device("cuda" if (args.device == "auto" and torch.cuda.is_available())
                          else (args.device if args.device != "auto" else "cpu"))

    runs = [args.run] if args.run else FORMAL_RUNS
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for rn in runs:
        if not (RUNS_DIR / rn).exists():
            records.append({"run": rn, "final_status": "MISSING_RUN_DIR"})
            print(f"[MISS] {rn}")
            continue
        rec = export_one(rn, device)
        records.append(rec)
        print(f"[{rec.get('best_status','?'):>8}] {rn} "
              f"val_n={rec.get('n_val_rebuilt')} "
              f"best Δcmae={rec.get('best_cmae_delta')} "
              f"final Δcmae={rec.get('final_cmae_delta')} "
              f"split_match={rec.get('split_size_match')} "
              f"tf_match={rec.get('flux_transform_match')}")

    # 汇总
    all_ok = all(r.get("best_status") == "OK" and r.get("final_status") == "OK"
                 for r in records if "MISSING" not in str(r.get("final_status")))
    summary = {
        "task": "R116-A1 val samples recovery (no retrain, checkpoint+deterministic split)",
        "n_runs": len(records),
        "all_verified": bool(all_ok),
        "cmae_tol_deg": CMAE_TOL,
        "method": "load checkpoint model_state; rebuild split via seed; recompute val; "
                  "cross-check vs stored metrics_val_*; export samples_val_*",
        "records": records,
    }
    json.dump(summary, open(OUT_DIR / "l1m2_val_samples_recovery_summary.json", "w",
                            encoding="utf-8"), indent=2, ensure_ascii=False)

    # CSV
    keys = ["run", "geom_group", "mode", "protocol", "n_val_rebuilt", "n_val_config",
            "split_size_match", "flux_transform_match",
            "final_verified", "final_cmae_rebuilt", "final_cmae_stored", "final_cmae_delta",
            "best_verified", "best_cmae_rebuilt", "best_cmae_stored", "best_cmae_delta",
            "final_status", "best_status"]
    with open(OUT_DIR / "l1m2_val_samples_recovery_summary.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in records:
            w.writerow(r)

    print(f"\n[SUMMARY] all_verified={all_ok}  -> {OUT_DIR}")
    return 0 if all_ok else 2


if __name__ == "__main__":
    sys.exit(main())

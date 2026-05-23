"""
Runner for text-only tasks (no matplotlib figures).
"""
import sys, os, time
os.chdir(r"D:\我的文件\研究生学术\光学项目\0506新\ocs_project\03_inversion")
sys.path.insert(0, ".")

log_path = "_runner_textonly_log.txt"

def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)

log("=== Text-only Runner starting ===")

try:
    import numpy as np
    import summarize_paper_results as spr
    log("import ok")

    # Reuse existing rows from the last run
    log("Building main table...")
    rows = spr.build_main_table()
    spr.save_main_table(rows)
    warnings = spr.run_sanity_check(rows)
    for w in warnings:
        log(f"  SANITY: {w}")
    if not warnings:
        log("  Sanity check: ALL PASSED")
    log(f"  Main table: {len(rows)} rows")

    log("Building fusion ablation...")
    table, methods_map = spr.build_fusion_ablation_table(rows)
    spr.save_fusion_ablation(table, methods_map)
    log("  Ablation table done")

    # Task 4: Complementarity
    log("Complementarity diagnosis...")
    aligned = spr.complementarity_diagnosis()
    log(f"  Done: {len(aligned)} aligned samples")

    # Task 5: Case gallery
    log("Case gallery...")
    spr.case_gallery(aligned)
    log("  Done")

    # Task 6: Paper claims
    log("Paper claims...")
    spr.generate_paper_claims(rows)
    log("  Done")

    # Task 7: Summary
    log("Summary JSON + figures data...")
    spr.save_summary_json(rows)

    # Save figure data as NPZ for later plotting
    ocs_preds = spr.load_ocs_mlp_predictions("per_part_log")
    ff_preds = spr.load_feature_fusion_predictions("per_part_log", seed=0)
    cnn_preds = spr.load_cnn_predictions(seed=0)

    # Save CDF data
    cdf_data = {}
    for case in ["all_raw", "per_part_log", "total_log"]:
        ff = spr.load_feature_fusion_predictions(case, seed=0)
        cnn = spr.load_cnn_predictions(seed=0)
        ocs = spr.load_ocs_mlp_predictions(case)
        cdf_data[case] = {
            "ff_errs": [p["angle_err"] for p in ff],
            "cnn_errs": [p["angle_err"] for p in cnn],
            "ocs_errs": [p["angle_err"] for p in ocs],
        }

    # Save beta sweep data
    beta_data = {}
    import csv
    for case in ["all_raw", "per_part_log", "total_log"]:
        path = spr.RUNS["late_fusion"][case] / "beta_sweep_summary.csv"
        betas, means, hit5s = [], [], []
        with open(path, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                betas.append(float(r["beta"]))
                means.append(float(r["mean_mean"]))
                hit5s.append(float(r["hit5_mean"]))
        beta_data[case] = {"betas": betas, "means": means, "hit5s": hit5s}

    np.savez(spr.OUT_DIR / "figure_data.npz",
             cdf_data=np.array([cdf_data], dtype=object),
             beta_data=np.array([beta_data], dtype=object),
             allow_pickle=True)
    log("  Figure data saved")

    log("=== ALL DONE ===")
    log(f"Output: {spr.OUT_DIR}")

except Exception as e:
    import traceback
    log(f"ERROR: {e}")
    log(traceback.format_exc())

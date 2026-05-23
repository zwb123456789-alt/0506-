"""
Self-contained runner for summarize_paper_results.py
Writes progress to _runner_log.txt to avoid Windows bash exit 127 issues.
"""
import sys, os, time
os.chdir(r"D:\我的文件\研究生学术\光学项目\0506新\ocs_project\03_inversion")
sys.path.insert(0, ".")

log_path = "_runner_log.txt"

def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(msg, flush=True)

log("=== Runner starting ===")

try:
    import matplotlib
    matplotlib.use("Agg")
    log("matplotlib Agg ok")

    import numpy as np
    log("numpy ok")

    import summarize_paper_results as spr
    log("import ok")

    # Task 1: Main table
    log("Building main table...")
    rows = spr.build_main_table()
    spr.save_main_table(rows)
    warnings = spr.run_sanity_check(rows)
    for w in warnings:
        log(f"  SANITY: {w}")
    if not warnings:
        log("  Sanity check: ALL PASSED")
    log(f"  Main table: {len(rows)} rows")

    # Task 2: Fusion ablation
    log("Building fusion ablation...")
    table, methods_map = spr.build_fusion_ablation_table(rows)
    spr.save_fusion_ablation(table, methods_map)
    log("  Ablation table done")

    # Task 3: Figures
    log("Generating figures...")
    spr.setup_plot_style()

    spr.generate_bar_chart(rows, methods_map)
    log("  fig01 bar chart done")

    spr.generate_hit5_bar_chart(rows)
    log("  fig02 hit5 bar chart done")

    spr.generate_cdf_plot()
    log("  fig03 cdf done")

    spr.generate_tradeoff_curve()
    log("  fig04 beta sweep done")

    log("  Skipping fig05 heatmap (slow)")
    log("  All figures done")

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
    log("Summary JSON...")
    spr.save_summary_json(rows)
    log("  Done")

    log("=== ALL DONE ===")
    log(f"Output: {spr.OUT_DIR}")

except Exception as e:
    import traceback
    log(f"ERROR: {e}")
    log(traceback.format_exc())

"""
Supplementary Table S2: Per-Fold C2 Results Extraction
修正版本 - 1C-E36-FIX01 (Pure Python, no pandas dependency)

修正问题：
1. 从 final_metrics.test 读取指标（而非顶层fold_data）
2. 处理 c2_screening_summary.json 编码问题
3. 使用相对路径拼接，不依赖绝对路径
4. 输出真实65行数据
"""

import json
from pathlib import Path

# Base path
base = Path(__file__).resolve().parents[2]
results_base = base / "v0.4_results" / "05_c2_screening"

# Load summary with encoding error handling
summary_path = results_base / "c2_screening_summary.json"
print(f"Reading summary: {summary_path}")
summary = json.loads(summary_path.read_text(encoding="utf-8", errors="replace"))

# Extract per-fold results
rows = []
for cfg in summary["results_summary"]:
    config_name = cfg["config_name"]
    for fr in cfg["fold_results"]:
        fold_id = fr["fold_id"]

        # Construct relative path instead of using absolute path from summary
        result_path = results_base / config_name / f"{config_name}_fold{fold_id}_result.json"

        if not result_path.exists():
            print(f"⚠ Missing: {result_path}")
            continue

        # Read fold result JSON
        fold_data = json.loads(result_path.read_text(encoding="utf-8", errors="replace"))

        # Extract from final_metrics.test (CORRECTED)
        test = fold_data["final_metrics"]["test"]

        rows.append({
            "config_name": config_name,
            "fold_id": fold_id,
            "yaw_acc_pct": test["yaw_acc"] * 100,
            "yaw_cmae_deg": test["yaw_circular_mae_deg"],
            "yaw_within3_pct": test["yaw_within_3_bins_rate"] * 100,
            "pitch_acc_pct": test["pitch_acc"] * 100,
            "yaw_correct_count": test["yaw_correct_count"],
            "pitch_correct_count": test["pitch_correct_count"],
            "n_test": test["n_samples"],
        })

# Validation
assert len(rows) == 65, f"Expected 65 rows, got {len(rows)}"
yaw_accs = [r["yaw_acc_pct"] for r in rows]
assert all(y == 0.0 for y in yaw_accs), "yaw_acc should be all 0.00%"
print(f"[OK] Extracted {len(rows)} fold results (13 configs x 5 folds)")
print(f"[OK] All yaw_acc = 0.00% (verified)")

# Save CSV
output_csv = results_base / "supplementary_table_s2_per_fold_results.csv"
with output_csv.open('w', encoding='utf-8') as f:
    # Header
    f.write("config_name,fold_id,yaw_acc_pct,yaw_cmae_deg,yaw_within3_pct,pitch_acc_pct,yaw_correct_count,pitch_correct_count,n_test\n")
    # Data rows
    for r in rows:
        f.write(f"{r['config_name']},{r['fold_id']},{r['yaw_acc_pct']:.2f},{r['yaw_cmae_deg']:.2f},"
                f"{r['yaw_within3_pct']:.2f},{r['pitch_acc_pct']:.2f},{r['yaw_correct_count']},"
                f"{r['pitch_correct_count']},{r['n_test']}\n")
print(f"[OK] Saved CSV: {output_csv}")

# Save Markdown table (first 10 rows for report)
output_md = results_base / "supplementary_table_s2_first10_rows.md"
with output_md.open('w', encoding='utf-8') as f:
    f.write("# Supplementary Table S2: Per-Fold C2 Results (First 10 Rows)\n\n")
    f.write("| Config Name | Fold | Yaw Acc (%) | Yaw CMAE (deg) | Within-3 (%) | Pitch Acc (%) | Yaw Correct | Pitch Correct | N Test |\n")
    f.write("|:-----------|:----:|------------:|-------------:|-------------:|--------------:|------------:|--------------:|-------:|\n")
    for r in rows[:10]:
        f.write(f"| {r['config_name']} | {r['fold_id']} | {r['yaw_acc_pct']:.2f} | "
                f"{r['yaw_cmae_deg']:.2f} | {r['yaw_within3_pct']:.2f} | {r['pitch_acc_pct']:.2f} | "
                f"{r['yaw_correct_count']} | {r['pitch_correct_count']} | {r['n_test']} |\n")
print(f"[OK] Saved Markdown (first 10): {output_md}")

# Display first 10 rows
print("\n" + "="*100)
print("FIRST 10 ROWS (Real Data - NOT Placeholder):")
print("="*100)
print(f"{'Config':<20} {'Fold':>4} {'YawAcc%':>8} {'YawCMAE':>9} {'Within3%':>9} {'PitchAcc%':>10} {'YawCorr':>8} {'PitchCorr':>10} {'NTest':>6}")
print("-"*100)
for r in rows[:10]:
    print(f"{r['config_name']:<20} {r['fold_id']:>4} {r['yaw_acc_pct']:>8.2f} {r['yaw_cmae_deg']:>9.2f} "
          f"{r['yaw_within3_pct']:>9.2f} {r['pitch_acc_pct']:>10.2f} {r['yaw_correct_count']:>8} "
          f"{r['pitch_correct_count']:>10} {r['n_test']:>6}")

# Summary statistics
print("\n" + "="*100)
print("SUMMARY STATISTICS:")
print("="*100)
print(f"Total rows: {len(rows)}")
print(f"Unique configs: {len(set(r['config_name'] for r in rows))}")
print(f"Yaw Acc range: {min(yaw_accs):.2f}% - {max(yaw_accs):.2f}% (all zero as expected)")
yaw_cmaes = [r['yaw_cmae_deg'] for r in rows]
print(f"Yaw CMAE range: {min(yaw_cmaes):.2f}° - {max(yaw_cmaes):.2f}°")
within3s = [r['yaw_within3_pct'] for r in rows]
print(f"Within-3 range: {min(within3s):.2f}% - {max(within3s):.2f}%")
pitch_accs = [r['pitch_acc_pct'] for r in rows]
print(f"Pitch Acc range: {min(pitch_accs):.2f}% - {max(pitch_accs):.2f}%")
print("="*100)
print("\n[OK] S2 extraction completed successfully!")

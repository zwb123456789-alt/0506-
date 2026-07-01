"""
Supplementary Table S2: Per-Fold C2 Results Extraction
修正版本 - 1C-E36-FIX01

修正问题：
1. 从 final_metrics.test 读取指标（而非顶层fold_data）
2. 处理 c2_screening_summary.json 编码问题
3. 使用相对路径拼接，不依赖绝对路径
4. 输出真实65行数据
"""

import json
from pathlib import Path
import pandas as pd

# Base path
base = Path(__file__).resolve().parents[2]  # 到达项目根目录
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

# Create DataFrame
df = pd.DataFrame(rows)

# Validation
assert len(df) == 65, f"Expected 65 rows, got {len(df)}"
assert (df["yaw_acc_pct"] == 0).all(), "yaw_acc should be all 0.00%"
print(f"✓ Extracted {len(df)} fold results (13 configs × 5 folds)")
print(f"✓ All yaw_acc = 0.00% (verified)")

# Save outputs
output_csv = results_base / "supplementary_table_s2_per_fold_results.csv"
output_tex = results_base / "supplementary_table_s2_per_fold_results.tex"

df.to_csv(output_csv, index=False, float_format='%.2f')
print(f"✓ Saved CSV: {output_csv}")

# LaTeX table with better formatting
latex_str = df.to_latex(
    index=False,
    float_format='%.2f',
    column_format='l|c|r|r|r|r|r|r|r',
    caption='Per-fold C2 screening results for all 13 configurations (65 runs total).',
    label='tab:s2_per_fold'
)
output_tex.write_text(latex_str, encoding='utf-8')
print(f"✓ Saved LaTeX: {output_tex}")

# Display first 10 rows as verification
print("\n" + "="*80)
print("FIRST 10 ROWS (Real Data):")
print("="*80)
print(df.head(10).to_string(index=False))
print("\n" + "="*80)
print("SUMMARY STATISTICS:")
print("="*80)
print(f"Total rows: {len(df)}")
print(f"Unique configs: {df['config_name'].nunique()}")
print(f"Yaw Acc range: {df['yaw_acc_pct'].min():.2f}% - {df['yaw_acc_pct'].max():.2f}%")
print(f"Yaw CMAE range: {df['yaw_cmae_deg'].min():.2f}° - {df['yaw_cmae_deg'].max():.2f}°")
print(f"Within-3 range: {df['yaw_within3_pct'].min():.2f}% - {df['yaw_within3_pct'].max():.2f}%")
print(f"Pitch Acc range: {df['pitch_acc_pct'].min():.2f}% - {df['pitch_acc_pct'].max():.2f}%")
print("="*80)

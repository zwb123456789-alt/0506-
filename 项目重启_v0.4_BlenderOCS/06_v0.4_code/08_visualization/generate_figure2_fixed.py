"""
Figure 2: Five-Fold Circular Yaw-Block Holdout Strategy
修正版本 - 1C-E36-FIX02

使用 5-row strip chart 替代错误的 Wedge polar plot
清晰展示 72/72 bins aggregate coverage
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from pathlib import Path

# Define 5-fold split (R65 standard)
folds = [
    {"fold": 0, "val": range(65, 72), "test": range(0, 15), "train": list(range(15, 65))},
    {"fold": 1, "val": range(8, 15), "test": range(15, 30), "train": list(range(0, 8)) + list(range(30, 72))},
    {"fold": 2, "val": range(23, 30), "test": range(30, 44), "train": list(range(0, 23)) + list(range(44, 72))},
    {"fold": 3, "val": range(37, 44), "test": range(44, 58), "train": list(range(0, 37)) + list(range(58, 72))},
    {"fold": 4, "val": range(51, 58), "test": range(58, 72), "train": list(range(0, 51))},
]

# Create matrix: 0=train, 1=val, 2=test
mat = np.zeros((5, 72), dtype=int)
for f in folds:
    mat[f["fold"], list(f["val"])] = 1
    mat[f["fold"], list(f["test"])] = 2

# Color map: light gray (train), light blue (val), dark blue (test)
cmap = ListedColormap(["#eeeeee", "#9ecae1", "#3182bd"])

# Create figure
fig, ax = plt.subplots(figsize=(14, 3.5))
im = ax.imshow(mat, aspect="auto", cmap=cmap, interpolation="nearest")

# Configure axes
ax.set_yticks(range(5))
ax.set_yticklabels([f"Fold {i}" for i in range(5)], fontsize=11)
ax.set_xticks(range(0, 72, 6))
ax.set_xticklabels([str(i) for i in range(0, 72, 6)], fontsize=9)
ax.set_xlabel("Yaw bin index (5° per bin, 0° = 0, 360° = 72)", fontsize=12)
ax.set_title("Five-Fold Circular Yaw-Block Holdout (Aggregate Coverage: 72/72 bins)",
             fontsize=13, fontweight='bold', pad=10)

# Add grid lines for clarity
ax.set_xticks(np.arange(-0.5, 72, 1), minor=True)
ax.set_yticks(np.arange(-0.5, 5, 1), minor=True)
ax.grid(which='minor', color='white', linestyle='-', linewidth=0.5)

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#eeeeee', edgecolor='black', label='Training'),
    Patch(facecolor='#9ecae1', edgecolor='black', label='Validation'),
    Patch(facecolor='#3182bd', edgecolor='black', label='Test')
]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.01, 1.0),
          fontsize=11, frameon=True)

# Output to script directory
out_dir = Path(__file__).resolve().parent
plt.tight_layout()
plt.savefig(out_dir / 'Figure2_yaw_block_holdout_fixed.png', dpi=300, bbox_inches='tight')
plt.savefig(out_dir / 'Figure2_yaw_block_holdout_fixed.pdf', bbox_inches='tight')
print("[OK] Figure 2 (fixed) saved: Figure2_yaw_block_holdout_fixed.png/.pdf")
print(f"[OK] Output directory: {out_dir}")
plt.close()

# Verify coverage
test_bins_all = set()
for f in folds:
    test_bins_all.update(f["test"])
print(f"[OK] Aggregate test coverage: {len(test_bins_all)}/72 bins")
assert len(test_bins_all) == 72, f"Coverage error: {len(test_bins_all)}/72"
print("[OK] All 72 bins covered exactly once across 5 folds")

## Table 2: Three-Channel Indicator Reconstruction vs Chance Baseline

| Indicator | Chance | C2 OCS-only (65-run mean ± SEM) | C3 image_only (5-fold mean ± SEM) | C3 joint (5-fold mean ± SEM) | Random split ref |
|---|---:|---:|---:|---:|---:|
| exact-bin yaw_acc | 1.39% | 0.00% ± 0.00% | 0.00% ± 0.00% | 0.00% ± 0.00% | ≈65–70% |
| yaw CMAE (deg) | 90.0 deg | 97.0 ± 4.2 | 81.4 ± 11.0 | 81.4 ± 9.6 | — |
| yaw within-3 | 9.72% | 9.96% ± 0.96% | 17.12% ± 2.00% | 17.74% ± 1.29% | — |
| yaw within-6 | 18.06% | 18.89% ± 1.72% | 25.57% ± 3.55% | 26.51% ± 3.83% | — |
| yaw coarse45 | 12.50% | 14.53% ± 1.75% | 17.96% ± 5.29% | 18.16% ± 5.64% | — |
| pitch exact | 2.70% | 3.03% ± 0.14% | 21.20% ± 2.44% | 19.42% ± 2.75% | — |
| pitch within-3 | 18.92% | 17.75% ± 0.52% | 56.07% ± 6.48% | 51.77% ± 5.96% | — |

_Notes: C2 OCS-only aggregates 13 configs × 5 folds = 65 runs. C3 image_only and joint each aggregate 5 folds. SEM = standard error of the mean across runs/folds. Chance values computed under uniform random prediction across 72 yaw bins (or 37 pitch bins). Random split reference from R77 §5 (same architecture, no yaw-block holdout)._
# P1-A Random Baseline

## Random prediction baseline (theoretical)

| Metric | Random Baseline | Note |
|---|---|---|
| Exact-bin (72 classes) | 0.0139 (1.39%) | 1/72 |
| Circular MAE (bins) | 18.05 | Monte Carlo |
| Within-1 bin | 0.0417 (4.17%) | (2*1+1)/72 |
| Within-2 bins | 0.0694 (6.94%) | (2*2+1)/72 |
| Within-3 bins | 0.0972 (9.72%) | (2*3+1)/72 |
| Within-6 bins | 0.1806 (18.06%) | (2*6+1)/72 |
| Coarse45 (8 classes) | 0.1250 (12.5%) | 1/8 |
| Coarse90 (4 classes) | 0.2500 (25.0%) | 1/4 |
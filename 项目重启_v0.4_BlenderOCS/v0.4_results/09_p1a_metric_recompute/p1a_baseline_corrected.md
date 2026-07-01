# P1-A Random Baseline (Theoretical, Corrected)

R100 3.3: 改用理论值，避免 Monte Carlo 漂移。

## 理论 random prediction baseline

| Metric | Theoretical Value | Derivation |
|---|---|---|
| Exact-bin (72 类) | 0.0139 (1.39%) | 1/72 |
| Circular MAE (bins) | 18.0 | sum(d*count(d))/72 = 18.0 |
| Within-1 bin | 0.0417 (4.17%) | 3/72 |
| Within-2 bins | 0.0694 (6.94%) | 5/72 |
| Within-3 bins | 0.0972 (9.72%) | 7/72 |
| Within-6 bins | 0.1806 (18.06%) | 13/72 |
| Coarse45 (8 类) | 0.1250 (12.5%) | 1/8 |
| Coarse90 (4 类) | 0.2500 (25.0%) | 1/4 |

**注**：先前 FIX01 报告中 circular MAE baseline = 18.0528（Monte Carlo, 未固定 seed），
理论值为 18.0，差异 0.05 bins，不改变任何结论。后续材料统一使用理论值 18.0。
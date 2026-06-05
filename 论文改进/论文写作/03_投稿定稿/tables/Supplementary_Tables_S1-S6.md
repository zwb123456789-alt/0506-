# Supplementary Tables S1-S6

> For: 主稿_v0.3_Acta_ASR润色版.md (Acta Astronautica / Advances in Space Research)
> Date: 2026-06-05
> All values are taken from the audited experiment outputs (experiments 11, 12, 12b-12g) and the Q1-Q15 author-confirmed records. No values are invented.
> Source directories: `论文改进/补充实验/结果/` (fusion_mechanism_upgrade, fusion_fallback_isolation_12b, noise_robustness, observation_style_degradation_12c, cross_phase_generalization_12d, centered_control_12e, late_fusion_beta_sweep_12f, outlier_gallery_12g).

---

## Table S1. Degradation-aware fusion (U1): full degradation table with tail statistics

Feature fusion (ResNet-18 image branch + concat5 per_part_log 30D OCS branch) trained with online image-degradation augmentation. 5 seeds (0-4), 10 deg -> 5 deg split. Worst-case is the maximum single-sample great-circle error across the test set.

| Condition | Mean +/- std (deg) | Hit@5 | P90 (deg) | Worst (deg) |
|---|---:|---:|---:|---:|
| clean | 1.95 +/- 0.21 | 97.8% | 3.53 | 102.11 |
| Gaussian noise sigma=0.01 | 1.95 +/- 0.21 | 97.8% | 3.53 | 102.08 |
| Gaussian noise sigma=0.10 | 2.31 +/- 0.26 | 96.6% | 3.73 | 164.27 |
| Brightness x0.50 | 1.98 +/- 0.20 | 97.8% | 3.54 | 139.83 |
| Brightness x1.50 | 2.00 +/- 0.22 | 97.4% | 3.62 | 98.97 |

Note: mean, P90, and Hit@5 are stable across the tested degradations, but worst-case errors above 100 deg persist for individual samples. U1 is therefore not described as fully robust (see Table S5 for the outlier audit).

---

## Table S2. Alternative fusion-upgrade strategies (U2, U3, U4)

Comparative upgrade variants on top of the baseline feature-fusion model. Reported as comparative/supplementary mechanisms, not the primary method.

| Strategy | clean (deg) | noise sigma=0.01 (deg) | noise sigma=0.10 (deg) | Role |
|---|---:|---:|---:|---|
| U2: modality dropout only | 1.96 | 83.72 | 84.26 | Negative result: dropout alone does not defend against unseen image noise |
| U3: augmentation + dropout | 2.90 | 2.96 | 4.59 | Effective but inferior to U1, with a clean-accuracy / Hit@5 cost |
| U4: OCS-anchored gate | 7.75 | - | 9.76 | Mechanistically suggestive (gate responds to noise) but not yet accurate enough |

Note: U1 (Table S1) reaches 1.95 deg clean and 2.31 deg at sigma=0.10, outperforming all three alternatives. These comparisons indicate that degradation-aware joint training, not a single architectural trick, restores robustness here.

---

## Table S3. OCS-noise robustness: full table with P90 and Hit@10

Synthetic relative Gaussian noise added only to OCS per_part features (image branch clean). 5 seeds. Source: `noise_robustness/run_20260601_094130/noise_summary.json`. Complements main-text Table 7.

| OCS noise | Model | Mean (deg) | Median (deg) | P90 (deg) | Hit@5 | Hit@10 |
|---:|---|---:|---:|---:|---:|---:|
| 0% | OCS-only | 5.91 | 3.25 | 7.74 | 73.8% | 94.3% |
| 0% | Fusion | 3.93 | - | 5.49 | 86.3% | 97.6% |
| 1% | OCS-only | 5.50 | 3.15 | 7.41 | 75.3% | 94.9% |
| 1% | Fusion | 3.77 | - | 5.32 | 88.1% | 97.7% |
| 5% | OCS-only | 7.27 | 3.92 | 9.75 | 63.6% | 90.5% |
| 5% | Fusion | 4.65 | - | 6.04 | 82.9% | 96.6% |
| 10% | OCS-only | 9.99 | - | 12.32 | 57.8% | 86.1% |
| 10% | Fusion | 6.69 | - | 7.84 | 74.9% | 93.6% |
| 20% | OCS-only | 17.25 | - | 40.85 | 35.8% | 68.5% |
| 20% | Fusion | 10.96 | - | 16.46 | 59.6% | 86.7% |

Note: the image-compensation gain (OCS-only mean minus fusion mean) increases monotonically from +1.97 deg at 0% to +6.29 deg at 20%. This is a one-sided OCS-degradation analysis; the image branch is clean throughout.

---

## Table S4. Centroid-control experiment (12e)

ResNet-18 image-only inversion under clean phase63 images, original fixed framing versus recentered targets (centroid removed). Centroid computed in the linear intensity domain.

| Case | Mean (deg) | P90 (deg) | Hit@5 |
|---|---:|---:|---:|
| Original (fixed framing) | 1.69 | 3.31 | 97.6% |
| Centered (centroid cue removed) | 2.88 | 5.42 | 87.4% |

Note: removing the centroid-displacement cue degrades accuracy from 1.69 to 2.88 deg, so the clean-image upper bound partly depends on fixed-framing/centroid cues. The residual accuracy after recentering shows that substantial shape information remains; the result is not solely centroid leakage.

---

## Table S5. Outlier audit and polar concentration (12b / 12g)

Audit over all 49,950 test evaluations (U1 / fusion-mechanism set).

| Threshold | Count | Fraction |
|---|---:|---:|
| error > 30 deg | 42 / 49,950 | 0.084% |
| error > 60 deg | 40 / 49,950 | 0.080% |
| error > 90 deg | 35 / 49,950 | 0.070% |

Note: rare large outliers persist despite stable mean/P90/Hit@5, and they concentrate near polar attitudes (about half of the >30 deg cases at |pitch| > 75 deg). This supports reporting mean/P90/Hit@5 as stable while retaining worst-case and polar outliers as a limitation.

---

## Table S6. Explicit late-fusion beta sweep (12f)

Late fusion in the sin/cos prediction space; beta is the image weight (beta = 1 image-only, beta = 0 OCS-only). The best beta is selected with oracle (inference-time) knowledge of the degradation and is an upper bound, not a deployable automatic gate.

| Condition | beta=0 OCS-only (deg) | beta=1 image-only (deg) | Best beta | Best error (deg) |
|---|---:|---:|---:|---:|
| clean | 6.58 | 1.72 | 0.9 | 1.67 |
| noise sigma=0.01 | 6.58 | 85.93 | 0.0 | 6.58 |
| noise sigma=0.10 | 6.58 | 89.12 | 0.0 | 6.58 |
| Brightness x0.50 | 6.58 | 3.18 | 0.8 | 2.81 |
| Brightness x1.50 | 6.58 | 1.94 | 0.9 | 1.87 |

Note: under image noise the oracle best weight moves to the OCS end (beta=0, 6.58 deg), far better than the naive feature-fusion collapse near 73 deg, but the weight is chosen with oracle knowledge of the degradation. The 6.58 deg OCS end is a within-experiment OCS retrain used as an internal beta-sweep reference; it is distinct from the main-line OCS-only result of 5.91 deg (main-text Table 2). Likewise, the 1.72 deg image end is the within-12f image retrain, distinct from the main-line clean image-only result of 1.69 deg.

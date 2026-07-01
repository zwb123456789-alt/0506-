# Pseudo-Sequence Similarity Summary

## Sequence 5-frame window

| Yaw Distance Group | N Samples | Mean Cosine Similarity | Std |
|---|---|---|---|
| near(<=15) | 0 | N/A | N/A |
| mid(20-45) | 64 | 0.9466 | 0.0524 |
| far(>=50) | 352 | 0.9508 | 0.0409 |

## Single-frame baseline

| Group | N Samples | Mean Cosine Similarity |
|---|---|---|
| near_15 | 216 | 0.9996 |
| far_50 | 1908 | 0.9937 |

**Note**: pseudo-light-curve probe only; not a light-curve experiment
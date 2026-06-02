# OCS+Image 联合反演消融表

| 方法 | OCS 输入 | Image 输入 | split | alpha | Top1@5° | Top5@5° | mean |
|---|---|---|---:|---:|---:|---:|
| OCS-only kNN | concat5 all raw | - | LOO | 1.00 | 77.42% | 97.37% | 12.28° |
| HOG image-only | - | phase63 GGX PNG | LOO | 0.00 | 81.30% | 99.15% | 4.31° |
| **OCS+HOG joint** | concat5 all raw | phase63 GGX PNG | LOO | 0.24 | **84.64%** | **99.48%** | **4.10°** |
| OCS-only MLP | concat5 all raw | - | 10°→5° | - | 90.7% | - | 3.98° |

> 注：MLP 行来自 Step 11c (`train_mlp.py`)，使用 10°→5° split（非 LOO），不可直接对比 LOO 指标。

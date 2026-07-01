# L1M2 跨几何量纲一致性核验（R116 子任务 A2）

最后更新：2026-07-01  
来源：`v0.4_results/11_l1m2_multigeometry_ocs/postprocess/` + `01_fullrun/postprocess/`

## 1. 各几何总光度与 contributing pixel 分布

| geom | 相位角° | n | flux mean | flux std | flux min | flux p50 | flux max | pix mean | pix p50 | pix max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| phase24 | 23.60 | 2664 | 0.03939 | 0.02108 | 0.02164 | 0.03451 | 0.25469 | 5179 | 5335 | 6391 |
| phase45 | 45.00 | 2664 | 0.03216 | 0.02863 | 0.01742 | 0.02379 | 0.22813 | 3653 | 3740 | 4485 |
| phase63 | 63.11 | 2664 | 0.02705 | 0.01827 | 0.01063 | 0.02076 | 0.17788 | 3941 | 3958 | 5923 |
| phase90 | 90.00 | 2664 | 0.02768 | 0.04204 | 0.00066 | 0.01265 | 0.22977 | 2643 | 2836 | 4741 |
| phase120 | 120.00 | 2664 | 0.01173 | 0.02122 | 0.00011 | 0.00400 | 0.11536 | 1286 | 999 | 3813 |

各几何 flux 均值互异（phase24 最高、phase120 最低），说明多观测向量含实质跨几何信息，非单标量重复。

## 2. 归一化 / 积分参数来源与跨几何一致性

| 参数 | phase24 | phase45 | phase63 | phase90 | phase120 | 一致 |
|---|---|---|---|---|---|---|
| pixel_area_m2 | 0.00016015410437830724 | 0.00016015410437830724 | 0.00016015410437830724 | 0.00016015410437830724 | 0.00016015410437830724 | 是 |
| ortho_scale_m | 3.239731375366906 | 3.239731375366906 | 3.239731375366906 | 3.239731375366906 | 3.239731375366906 | 是 |
| depth_epsilon_m | 0.7952109582768545 | 0.7952109582768545 | 0.7952109582768545 | 0.7952109582768545 | 0.7952109582768545 | 是 |
| resolution | 256 | 256 | 256 | 256 | 256 | 是 |
| r_max | 1.4726051706213208 | 1.4726051706213208 | None | 1.4726051706213208 | 1.4726051706213208 | 是 |
| i_scale_smallrun | 0.5444863931551639 | 0.5444863931551639 | None | 0.5444863931551639 | 0.5444863931551639 | 是 |
| log1p_alpha | 10.0 | 10.0 | None | 10.0 | 10.0 | 是 |

说明：
- `pixel_area_m2 / ortho_scale_m / depth_epsilon_m / resolution` 五几何完全一致，OCS 物理积分同量纲、可直接跨几何比较。
- `r_max / i_scale_smallrun / log1p_alpha` 在 phase63 manifest header 记为 null（记录在其它冻结文件），phase24/45/90/120 header 显式记录且四者一致；`i_scale/log1p` 仅影响 PNG 显示（Pass 2），不进入 `ocs_total` 物理积分，不影响 OCS-only 输入量纲。
- 五几何 `ocs_integration_version` 与 `brdf_branch=B0` 同源同管线（103 报告 §5 派生包装器，覆盖 SUN/DET/OUTPUT 后调用原 main）。

## 3. train-only transform 泄漏检查

| group | n_tr/va/te | train-fit 与 saved run_config 一致 | split 重叠(tr∩va,tr∩te,va∩te) | leakage-free |
|---|---|---|---|---|
| G1 | 2109/259/296 | mean=True std=True | 0,0,0 | True |
| G3 | 2109/259/296 | mean=True std=True | 0,0,0 | True |
| G5 | 2109/259/296 | mean=True std=True | 0,0,0 | True |

z-score 参数仅由 train 拟合（`fit_flux_transform(tr)`），与 run_config 保存值逐位一致；train/val/test attitude 无交集，无 transform 泄漏。

## 4. attitude 对齐与嵌套

- G1/G3/G5 attitude 数：2664/2664/2664（均 2664：True）
- 嵌套：G1⊂G3=True, G3⊂G5=True, G1⊂G5=True
- yaw/pitch 与 attitude_key 不一致条数：0

## 5. 语义边界

本多几何是 **simulated multi-view geometry**：同一姿态在多组已知 sun/view 几何下分别积分得到总光度标量，拼成多观测光度向量。
它不是路线二真实跨时间多几何，不含真实观测噪声与真实时间采样，也不代表真实未知目标的可观测序列。

## 6. 核验结论

- 跨几何物理量纲参数一致：True
- train-only transform 无泄漏且与训练一致：True
- attitude 对齐/嵌套/坐标一致：True

**综合：R116 A2 跨几何量纲一致性核验通过 = True**

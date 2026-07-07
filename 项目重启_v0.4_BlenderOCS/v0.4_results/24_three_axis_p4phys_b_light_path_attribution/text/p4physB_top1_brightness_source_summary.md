# top-1 亮度来源摘要（B 子任务）

固定几何：phase63 / L1-G1，SUN=[1,0,0.3]，DET=[0.5,-1,0.1]（惯性系）。
top-1：yaw=245.0, pitch=27.5, roll=+15，ocs_total=0.20889048（与 23A ocs.json 一致，重算 rel_diff=5.5e-8）。

## 1. ocs_total 与部件贡献

| 部件 | OCS (m²) | 占比 | 贡献像素数 |
|---|---|---|---|
| 金属主体 jinshuzhuti | 0.198497 | 95.02% | 2653 |
| 隐身板 yinshenban | 0.008775 | 4.20% | 1408 |
| 太阳能板 taiyangnengban | 0.001619 | 0.78% | 80 |

- **主贡献部件：金属主体（Metal body），95.0% 的 top-1 OCS。**
- 第二贡献：隐身板 4.2%（1408 个贡献像素，属大面积低单像素亮度）。
- 太阳能板贡献极小（<1%）。

## 2. 贡献判断的一致性

贡献判断同时来自两条独立链路且一致：

1. `ocs_per_part`（已落盘 23A ocs.json，pipeline 官方口径）；
2. 本轮从 camera EXR 的 IndexOB 逐像素重算 `pixel_area · Σ I_linear`（`numeric_path_consistency_check.csv`）。

两者 per-part 数值一致，重算 ocs_total 相对误差 5.5e-8，故 per-part 归因是直接计算，不是推测。

## 3. 像素级集中度

- 贡献像素 4141 个（金属 2653 + 隐身 1408 + 太阳能 80）。
- I_linear 最大值 0.5659，中位数 0.5658 → 金属贡献像素几乎整体处于高值平台（近饱和 plateau），不是单点尖峰。
- 达到 50% 总 OCS 只需 1153 个最亮像素（占贡献像素 27.8%），说明亮度由一片较大的近镜面金属面主导，而非孤立 glint 点。

## 4. 直接 vs proxy

- **直接**：per-part OCS、贡献像素数、I_linear 分布、IndexOB→部件映射。
- **proxy**：材料层面只能到 B0 phong_like（金属 rho_s=0.60,n=80）参数级；无 material pass，"金属高镜面材料"是 material proxy，不是独立材料通道归因。

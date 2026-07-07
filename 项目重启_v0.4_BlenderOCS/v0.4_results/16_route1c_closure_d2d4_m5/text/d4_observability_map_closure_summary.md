# 子任务C：D4 姿态空间可观测性地图闭口摘要

口径：P-INT best clean（P-EXT G5 单列坍缩区）；yaw circular error；model-known simulated。

## 1. 区域误差分布（frac_low = err≤10°, frac_high = err>30°）

| geom | channel | frac_low | frac_high |
|---|---|---|---|
| G1 | ocs_only | 0.125 | 0.723 |
| G1 | image_only | 0.986 | 0.0 |
| G1 | joint | 0.993 | 0.0 |
| G3 | ocs_only | 0.378 | 0.328 |
| G3 | image_only | 0.861 | 0.0 |
| G3 | joint | 0.986 | 0.0 |
| G5 | ocs_only | 0.443 | 0.189 |
| G5 | image_only | 0.693 | 0.007 |
| G5 | joint | 0.99 | 0.0 |

## 2. 几何增益

- OCS-only 从 G1→G5：228 个姿态显著被多几何救回(增益>5°)，40 个变差(>5°)，其余基本持平。
- 平均 yaw err 改善 = 53.79°（正=G5更好），中位 = 47.32°。
- 说明多几何主要救回 OCS-only 在单几何下高误差的姿态区，与 L1-G1→G5 单调增益一致。

## 3. 易混淆 / 低信息区域

- ambiguous-flux（P-DB 最近邻很相似但 yaw 判错）：236 例，是光度多观测向量的固有姿态歧义区。
- neural 过自信错误（margin 高但错）：98 例，佐证 R119 neural margin 置信区分度弱。
- P-EXT yaw-block 坍缩区：296 例（G5 ocs_only 全部 held-out yaw block），确认 strict extrapolation 未解决。

## 4. 闭口结论

- D4 已形成 model-known simulated 姿态空间可观测性地图：可标出高/中/低误差区、多几何救回区、光度歧义区、过自信错误区与 P-EXT 坍缩区。
- 该地图可作为三轴小项目「高信息姿态 / 低信息观测区」的直接接口，但本轮不启动三轴小项目。
- 不得写成真实天空可观测性地图，不得写成三轴小项目已完成。

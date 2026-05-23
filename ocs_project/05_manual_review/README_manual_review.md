# 人工遮挡抽查工具 · MVP 使用说明

Blender 5.0 headless 脚本，读取 `manual_review_candidates.csv`，独立用 Blender `scene.ray_cast` 对候选面元复算太阳 / 探测器射线遮挡，交叉验证模块 A 当前算法（trimesh + Embree + `min_hit_distance`）。

## 前置

- Blender 5.0：`D:\Program Files\Blender Foundation\Blender 5.0\blender.exe`
- STL 模型：`建模\jinshuzhuti.stl` / `建模\taiyangnengban.stl` / `建模\yinshenban.stl`
- 候选 CSV：`结果\遮挡验证\run_YYYYMMDD_HHMMSS\manual_review_candidates.csv`（最新基线 `run_20260512_213850`）
- 单位：全程 mm（与模块 A 保持一致，不做 mm→m 转换）

## 快速运行

双击 `run_manual_review.bat`，默认参数 MVP smoke test：

- `max_cases = 3`
- `mhd_filter = 1.0 mm`（项目基线 EPSILON）
- `only_occluded = 1`（只取 CSV 中 sun_occluded 或 det_occluded = True 的行）
- `self_hit_tol_mm = 0.001`
- `max_ray_dist_mm = 10000`

输出：`结果\人工遮挡抽查\run_YYYYMMDD_HHMMSS\`

## 输出物

```
run_YYYYMMDD_HHMMSS/
├── review_report.csv        每个 case 的算法 / 工具对比
├── review_report.md         同内容 Markdown，含总览统计
├── figures/
│   └── case_0001_<part>_f<face_id>_mhd1p0_overview.png
└── blender_files/
    └── case_0001_<part>_f<face_id>_mhd1p0.blend
```

## 诊断标签语义

针对 sun / det 各自：

- 报告中的 `raw` 显示 Blender 原始几何命中，中文写作“遮挡/未遮挡”。
- 报告中的 `filtered` 显示自相交过滤规则后的结果，中文写作“通过规则/不通过规则”。

| 当前算法 `*_occluded` | 工具 `filtered_hit` | 诊断 |
|---|---|---|
| True | True | `AGREE_OCCLUDED` |
| False | False | `AGREE_CLEAR` |
| True | False | `DISAGREE`（算法报遮挡，工具无命中） |
| False | True | `DISAGREE`（算法报无遮挡，工具命中） |

`overall_agree` = Sun 与 Det 均 AGREE。

## 可视化约定

每个 case 在 Blender 场景显示：

- 三个 STL 部件：银灰 / 深蓝 / 绿，不透明（Workbench 材质视图）
- 检测点：绿色小球，表示算法实际射线起点 `origin`（射线从这里发出）
- 原始面元中心：黄色小球，仅当输入 CSV 提供 `face_centroid_*_mm` 或 `centroid_*_mm` 字段时显示
- Sun 射线：橙色圆柱，从 `origin` 沿 `sun_dir` 正向
- Det 射线：蓝色圆柱，从 `origin` 沿 `det_dir` 正向
- 命中点：红色小球（仅 filtered_hit=True 时出现；近起点命中时可能贴近绿色 origin 球，按报告距离字段判断）
- 未命中：射线延伸 `model_extent × 1.5`
- PNG 与 .blend 内不写文字解释；标记含义以报告和本 README 为准
- `sun_view` / `det_view` 相机沿对应射线轴看向 `origin`，并保留另一条参考射线

射线方向约定：`ray = origin + t * direction, t > 0`，`direction = CSV 中的 Sun/Det 向量（单位化后）`。

## 交互检查

点开任一 `.blend` 文件即可在 Blender GUI 中旋转查看该 case 的几何上下文。场景中保留了三个部件 + 该 case 的检测点 / 射线 / 命中标记。

## 命令行参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--input` | — | 候选 CSV 路径 |
| `--model_dir` | — | 存放三 STL 的目录 |
| `--outdir` | — | 输出根目录（自动追加 `run_YYYYMMDD_HHMMSS/`） |
| `--max_cases` | 30 | 最多处理多少行 |
| `--mhd_filter` | 1.0 | 仅选 `min_hit_distance_mm == 该值` 的行 |
| `--parts` | `jinshuzhuti,taiyangnengban,yinshenban` | 部件筛选（逗号分隔） |
| `--only_occluded` | 1 | 1 = 只要至少一方向遮挡的行 |
| `--self_hit_tol_mm` | 0.001 | 命中距离小于此阈值判为自相交忽略 |
| `--max_ray_dist_mm` | 10000 | 射线最大追踪距离 |
| `--save_blend` | 1 | 是否保存 .blend |
| `--render_png` | 1 | 是否渲染 PNG |
| `--render_width` / `--render_height` | 1280 / 800 | 渲染分辨率 |

## 与模块 A 的关系

- **与模块 A 遮挡机制不同**：A 用 trimesh+Embree `intersects_location` + `min_hit_distance` 聚合；本工具用 Blender BVH `scene.ray_cast` + 自相交阈值过滤。结果若 AGREE 占多数，说明 A 当前基线在独立实现下可重现；若 DISAGREE 比例高，需排查 A 的判定逻辑或数据生成。
- **姿态**：当前 CSV 多为 `yaw=pitch=roll=0 / M=I`，仍按 `R = Rz @ Ry @ Rx` 实现，与模块 B 一致。
- **与模块 B 区别**：模块 B 走 Cycles 物理光追做渲染；本工具只用 Workbench 做几何可视化，不做光度学模拟。

## MVP 限制

1. Workbench 实体渲染，部件不透明——若检测点在部件内部，PNG 上看不到 origin 小球（但射线向外延伸仍可见）。需要透视时打开 .blend 切到 X-Ray 查看。
2. Blender STL 导入后的 polygon 索引与 trimesh `face_id` 可能不一致，脚本暂不高亮 face_id。
3. `scene.ray_cast` 只返回最近命中；若最近命中落在 `self_hit_tol_mm` 内则判自相交忽略，不继续向后找下一个交点。第二阶段可改用 BVH 多交点过滤。
4. 未做 reference 算法对比（CSV 新版不含该字段），只做 current vs manual 对比。

## 第二阶段可扩展

- face_id 高亮（基于 origin 最近面 + 索引映射校验）
- Sun / Det 独立视角图
- 多 mhd 档位对比（同一 face_id 在不同 mhd 下的工具复算结果）
- BVH 多交点精确过滤
- 分层抽样（按部件 + 遮挡组合分桶）

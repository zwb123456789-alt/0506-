# STL模型与现有结果索引

最后更新：2026-06-05

## 本小项目指定 STL

| 部件 | 路径 | 文件大小 | 用途 |
|---|---|---:|---|
| 金属主体 | `建模/真实模型/jinshuzhuti.stl` | 约 22.98 MB | 主体散射与镜面峰判断 |
| 太阳能板 | `建模/真实模型/taiyangnengban.stl` | 约 0.84 MB | 大面积板件与太阳翼 glint 判断 |
| 隐身板/遮挡板 | `建模/真实模型/yinshenban.stl` | 约 0.25 MB | 板件贡献与遮挡影响判断 |

## 已有可复用结果

| 数据 | 路径 | 内容 |
|---|---|---|
| FIG3 source data | `论文改进/论文写作/03_投稿定稿/figures/source_data/Fig_3_ocs_heatmaps.csv` | 已绘图用 OCS heatmap 数据 |
| phase63 OCS scan | `结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260527_195122/phase63_backscatter/ocs_scan.csv` | 2701 yaw-pitch 姿态，含 per-part 与遮挡 |
| 图注/口径说明 | `论文改进/论文写作/03_投稿定稿/figures/FIGURE_NOTES.md` | 数据来源、遮挡比例、已知 caveat |

## 已知口径

从图注说明可知：

- phase63 grid：73 yaw × 37 pitch = 2701 姿态。
- per-part 名称：`jinshuzhuti`、`taiyangnengban`、`yinshenban`。
- phase63 的 occlusion_ratio 范围约为 19.3% 到 97.1%，均值约 69.7%。
- 五几何 mean occlusion_ratio 范围约为 60.1% 到 78.5%。

## 待检查字段

下一步读取 `ocs_scan.csv` 表头，确认以下字段名：

- total OCS 字段；
- per-part OCS 字段；
- yaw/pitch/roll 字段；
- occlusion_ratio 字段；
- 几何/相位角标识字段。

确认后即可写脚本做 top-K 最亮排序。

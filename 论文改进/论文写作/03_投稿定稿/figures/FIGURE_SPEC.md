# 论文投稿图质量规格

## 输出格式

| 格式 | 用途 | 要求 |
|---|---|---|
| `.pdf` | LaTeX 投稿 / AI / Inkscape 精修 | 矢量，字体嵌入，无限缩放 |
| `.png` | Word 快速插入 / 预览 | 600 dpi |
| `.emf` | PPT 取消组合编辑 | Windows 矢量，线宽保留 |
| `.csv` | Origin 重绘 | 每张图导出绘图用数据表 |

## 尺寸

| 类型 | figsize (inch) | 对应 mm |
|---|---|---|
| 单栏图 (1-col) | 3.5 × 2.8 | ~89 × 71 mm |
| 跨栏图 (2-col) | 7.0 × 5.0 | ~178 × 127 mm |
| 概念草图 (Fig. 1-2) | 7.0 × 4.5 | ~178 × 114 mm |

## 排版

- **字体**：DejaVu Sans，主文字 7 pt、标注 6 pt、panel 编号 9 pt bold
- **线宽**：坐标轴线 0.5 pt、数据线 1.0–1.5 pt、辅助线 0.3 pt (虚线)
- **颜色**：Okabe-Ito colorblind-safe palette
- **Panel 编号**：(a) (b) (c) bold，统一左上角，与数据区边缘距离 0.1 inch 内
- **边框**：上方和右侧轴线默认关闭（spines `top`/`right` invisible）
- **网格**：仅 Fig. 3 heatmap 保留（淡灰色，linewidth 0.2），其余图不加 grid

## 图表绑定（不可变更）

- **字体嵌入 PDF**：`rcParams['pdf.fonttype'] = 42`（outline 字体，避免 AI/PPT 打开乱码）
- **抗锯齿**：`antialiased=True`
- **bbox**：`bbox_inches='tight'`，`pad_inches=0.1`（防切边）
- **图片大小写死**：全脚本统一 `rcParams`，不在单个图里改默认值
- **backup位图 DPI**：`rcParams['figure.dpi'] = 200`（屏幕）；`savefig.dpi = 600`（写入 PNG）
- **中文**：图中不出现中文字符，全部英文标注

## 文件命名

Canonical submission filenames:

```
Fig_3_ocs_heatmaps.pdf        Fig_3_ocs_heatmaps.png        Fig_3_ocs_heatmaps.emf
Fig_4_robustness.pdf          Fig_4_robustness.png           Fig_4_robustness.emf
Fig_5_sensitivity.pdf          Fig_5_sensitivity.png           Fig_5_sensitivity.emf
Fig_6_stress_tests.pdf        Fig_6_stress_tests.png         Fig_6_stress_tests.emf
Fig_1_pipeline.pdf            Fig_1_pipeline.png             Fig_1_pipeline.emf
Fig_2_geometry.pdf           Fig_2_geometry.png            Fig_2_geometry.emf
```

Legacy aliases retained by `make_figures.py` for earlier draft links:

```
FIG3_ocs_occlusion_maps.pdf        FIG3_ocs_occlusion_maps.png
FIG4_bidirectional_robustness.pdf  FIG4_bidirectional_robustness.png
FIG5_forward_model_sensitivity.pdf FIG5_forward_model_sensitivity.png
FIG6_obs_crossphase_beta.pdf       FIG6_obs_crossphase_beta.png
FIG1_pipeline_schematic.pdf        FIG1_pipeline_schematic.png
FIG2_geometry_attitude_schematic.pdf FIG2_geometry_attitude_schematic.png
```

Fig. 3 occlusion wording rule: `19.3%-97.1%` is the phase63 yaw-pitch grid-cell range; `60.1%-78.5%` is the five-geometry mean range from `occlusion_summary.csv`. Do not describe `60.1%-78.5%` as the full phase63 map range.

## 数据红线

- 不编造任何数值：数据缺失的 panel 用已确认 summary 值出图并标注来源
- Fig. 5b BRDF roughness 仅出 bar chart，标注 `representative (author-confirmed summary values)`
- Fig. 4a clean-trained image-only Gaussian-noise 系列数据缺失，仅标 clean point，标注 `*`
- 不混淆 6.58°（12f 内部参照）与 5.91°（主线 OCS-only）

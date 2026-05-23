# 本轮任务 · run_20260521_100228

## 步骤
CLAUE.md §六 Step 11d：图像-based 反演

## 当前状态
- OCS-only MLP 已完成（Step 11c），solo 上限：all raw Hit5=90.7%, per_part log Hit5=73.8%
- 旧 Principled 图像仅 703 姿态（10° 网格），与新 GGX OCS 数据（2701 姿态 5° 网格）不兼容
- 需先生成 GGX 辐射图像，再做 image-only HOG baseline

## 本轮目标
1. 选 1 个代表观测几何（phase63_backscatter，相位角 ~63°）
2. 用 render_geometry_passes.py 渲染 2701 帧 MULTILAYER EXR
3. 修改 brdf_postprocess.py 增加 --ggx 支持
4. 后处理生成 GGX 辐射 PNG 图像
5. 运行 inv_image.py HOG baseline

## 依赖
- 多几何 GGX 5° 扫描数据：`结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260520_162831/`
- Blender 4.2.3 LTS：`D:\Program Files\Blender Foundation\Blender 4.2\blender.exe`
- conda env: ocs_sim

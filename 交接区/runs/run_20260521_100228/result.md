# 执行结果 · run_20260521_100228

## 子任务 A：GGX 管线小样本验证（3 帧）

### OCS 对照（GGX B_img vs GGX A_occ）

| 帧 | OCS_B (pixel) | OCS_A (face) | rel_err |
|---|---:|---:|---:|
| yaw=0 pitch=-90 | 1.10e-2 | 1.20e-2 | 8.27% |
| yaw=0 pitch=-85 | 1.14e-2 | 1.10e-2 | 3.77% |
| yaw=0 pitch=-80 | 1.21e-2 | 1.18e-2 | 2.75% |

- mean rel_err = 4.93%，radiance_max = 2.91
- 产物：`结果/模块B_渲染/run_20260521_ggx_test3/`（3 EXR + 3 PNG）

## 子任务 B：phase63 全量 2701 帧

### 渲染
- 命令：`blender.exe --background --python render_geometry_passes.py -- --scan-json <phase63> --out-dir <ABSPATH>`
- 耗时：863.2s（14.4 min），0.32s/帧，OPTIX GPU
- `out_dir = os.path.abspath(out_dir)` 修复生效，全部写入项目目录

### GGX 后处理
- 命令：`python brdf_postprocess.py <out_dir> --ggx`
- radiance_max_global = 53.07（全姿态覆盖 GGX 金属镜面峰）
- rel_err A/B 较大（mean=212%），符合 CLAUDE.md 记录的 face-center vs pixel-level 原生 gap；不影响图像质量

### 完整性检查

| 项目 | 预期 | 实际 |
|---|---|---|
| EXR 帧数 | 2701 | 2701 ✓ |
| PNG 帧数 | 2701 | 2701 ✓ |
| CSV 行数 | 2701 | 2701 ✓ |
| n_frames | 2701 | 2701 ✓ |

- 抽检 7 帧：全部 256×256 RGB，non-zero 9~4323 px（边缘→正照，符合物理）

## 产物路径
- 测试：[结果/模块B_渲染/run_20260521_ggx_test3/](结果/模块B_渲染/run_20260521_ggx_test3/)（3 帧）
- 全量：[结果/模块B_渲染/run_20260521_phase63_ggx/](结果/模块B_渲染/run_20260521_phase63_ggx/)（2701 EXR + 2701 PNG + CSV + summary）

## 子任务 C：HOG image-only baseline

### 改动
- `inv_image.py` 增加 `--image-dir` 参数 + 适配 `out_prefix` → `_brdf.png` 文件名映射

### HOG LOO 结果（phase63 2701 GGX 辐射图像）

| 指标 | 值 |
|---|---|
| Top1@5° | **74.79%** |
| Top5@5° | **98.11%** |
| angular mean | 4.31° |
| angular med | 4.83° |
| angular p90 | 6.54° |
| angular p95 | 8.39° |
| yaw mean | 4.49° |
| pitch mean | 2.01° |
| HOG 维度 | 8100 |
| 提取耗时 | 11.6s（233 图/秒） |

### 与 OCS-only 对比

| 方法 | Top1@5° | angular mean |
|---|---|---|
| HOG image-only (本次) | 74.79% | 4.31° |
| OCS kNN total+log LOO | 53.8% | 26.47° |
| OCS MLP per_part log | 73.8% | 5.91° |
| OCS MLP all raw | 90.7% | 3.98° |

- HOG image-only **显著优于** OCS kNN total（+21pp Top1@5°）
- HOG image-only **与 OCS per_part MLP 相当**（Top1@5° 74.79% vs 73.8%）
- 但距离 OCS all raw MLP 仍有差距（90.7% → OCS+image 联合空间大）

### 产物
- [结果/模块C_反演/inv_image/run_20260521_123201/](结果/模块C_反演/inv_image/run_20260521_123201/)

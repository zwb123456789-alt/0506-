# p4physA 下一轮光路归因可行性预检

## 当前 EXR/NPY/JSON 包含的字段

Camera EXR channels（23A 新渲染）: ['ViewLayer.Combined.A', 'ViewLayer.Combined.B', 'ViewLayer.Combined.G', 'ViewLayer.Combined.R', 'ViewLayer.Depth.Z', 'ViewLayer.IndexOB.X', 'ViewLayer.Normal.X', 'ViewLayer.Normal.Y', 'ViewLayer.Normal.Z', 'ViewLayer.Position.X', 'ViewLayer.Position.Y', 'ViewLayer.Position.Z']
Fullrun camera EXR channels: ['ViewLayer.Combined.A', 'ViewLayer.Combined.B', 'ViewLayer.Combined.G', 'ViewLayer.Combined.R', 'ViewLayer.Depth.Z', 'ViewLayer.IndexOB.X', 'ViewLayer.Normal.X', 'ViewLayer.Normal.Y', 'ViewLayer.Normal.Z', 'ViewLayer.Position.X', 'ViewLayer.Position.Y', 'ViewLayer.Position.Z']

## 可用字段

| 字段 | 可用 | 来源 |
|------|------|------|
| ocs_total | ✓ | 来自 *_ocs.json |
| per_part_ocs | ✓ | ocs_per_part 字段，来自 *_ocs.json |
| glint_flag | ✓ | 来自后处理 linear.exr 计算 |
| saturation_flag | ✓ | 来自后处理 linear.exr 计算 |
| camera_visibility | ✓ | n_pixels_camera_visible |
| sun_visibility_mask | ✓ | _v_sun_macro.npy |
| pixel_intensity_map | ✓ | _linear.exr |
| object_id_pass | ✗ | 当前渲染只有 camera+sun EXR，无 IndexOB/ObjectID 专用 pass |
| material_id_pass | ✗ | 未渲染 material pass |
| normal_pass | ✗ | 未渲染 normal pass |
| depth_pass | ✗ | 未渲染 depth pass |
| per_pixel_part_map | ✗ | IndexOB 嵌入 camera EXR，需 read_indexob_pass 提取 |

## 对 P4-PHYS-B 的影响

**当前阻塞**：23A 的 pitch 边界问题需先解决（追加 pitch∈{22.5,25.0} 一小圈），
才能确认 fixed-geometry top-1，然后才能进入 P4-PHYS-B。

**P4-PHYS-B 最小需求（待追加 pitch 边界后）：**

1. **IndexOB / per-part 映射**：camera EXR 中包含 IndexOB pass（由 read_indexob_pass 读取），
   可分解出 jinshuzhuti / taiyangnengban / yinshenban 三部件贡献。
   已有 ocs_per_part 字段，可直接判断主贡献部件。

2. **物理光路归因所需的额外 pass（若需要精细归因）**：
   - object-id / material-id pass：需在 Blender 渲染时额外输出。
   - normal pass：需要额外渲染 pass。
   - depth pass：当前 sun EXR 包含深度信息，可用于遮挡判断。

3. **最小诊断姿态集**（确认 top-1 后）：
   - top-1 最亮姿态（确认后的 pitch 边界追加结果）
   - R4 roll-robust 亮区代表点（yaw=147.5, pitch=12.5, roll=0）
   - R3 低信息对照点（yaw=55.0, pitch=60.0, roll=0）

4. **是否同时归因 R1 top-1 与 R4 鲁棒亮区**：是，用于对比两种高亮机制。

## 结论

当前 23A 已有数据足以支持 per-part ocs 分解（通过 ocs_per_part 字段）。
若需 pixel-level part/material/normal 精细归因，需新增 object-id/material/normal pass 渲染。
**在 pitch 边界追加完成并确认 top-1 后，以最小 3 个姿态启动 P4-PHYS-B。**

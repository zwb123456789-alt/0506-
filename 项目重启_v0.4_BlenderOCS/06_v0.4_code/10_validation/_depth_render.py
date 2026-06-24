
# -*- coding: utf-8 -*-
"""
Blender depth render — 被 depth_round_trip_check.py 调用
设置场景 + 渲染 camera/sun depth + 导出矩阵
"""
import bpy
import bmesh
import json
import math
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix

# ============================================================
# 清空场景
# ============================================================
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ============================================================
# 加载卫星 mesh（3 部件合并）
# ============================================================
STL_DIR = Path(r"D:\我的文件\研究生学术\光学项目\0506新\建模\真实模型")
stl_files = {
    "jinshuzhuti": STL_DIR / "jinshuzhuti.stl",
    "taiyangnengban": STL_DIR / "taiyangnengban.stl",
    "yinshenban": STL_DIR / "yinshenban.stl",
}

all_verts = []
all_faces = []
face_offset = 0

for part_name, stl_path in stl_files.items():
    bpy.ops.import_mesh.stl(filepath=str(stl_path))
    obj = bpy.context.selected_objects[0]
    obj.name = part_name

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.transform(bm, matrix=obj.matrix_world, verts=bm.verts)

    verts = [v.co[:] for v in bm.verts]
    faces = [[f.verts[0].index + face_offset,
              f.verts[1].index + face_offset,
              f.verts[2].index + face_offset] for f in bm.faces]

    all_verts.extend(verts)
    all_faces.extend(faces)
    face_offset += len(verts)

    bm.free()
    bpy.ops.object.delete()

# 创建合并 mesh
merged_mesh = bpy.data.meshes.new("satellite_merged")
merged_mesh.from_pydata(all_verts, [], all_faces)
merged_mesh.update()

satellite = bpy.data.objects.new("Satellite", merged_mesh)
scene.collection.objects.link(satellite)
bpy.context.view_layer.objects.active = satellite
satellite.select_set(True)

# ============================================================
# 获取顶点坐标（mm）
# ============================================================
verts_array = np.array(all_verts)
print(f"[INFO] 合并 mesh: {len(all_verts)} 顶点, {len(all_faces)} 面")
print(f"[INFO] BBox: x=[{verts_array[:,0].min():.1f}, {verts_array[:,0].max():.1f}], "
      f"y=[{verts_array[:,1].min():.1f}, {verts_array[:,1].max():.1f}], "
      f"z=[{verts_array[:,2].min():.1f}, {verts_array[:,2].max():.1f}]")

# ============================================================
# 设置相机
# ============================================================
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50  # mm
cam_data.sensor_width = 36  # mm
cam_data.clip_start = 10  # mm
cam_data.clip_end = 100000  # mm

cam_obj = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = (3000, 0, 0)
cam_obj.rotation_euler = (math.pi/2, 0, math.pi/2)

# ============================================================
# 设置 Sun（正交相机）
# ============================================================
sun_data = bpy.data.cameras.new("SunCam")
sun_data.type = 'ORTHO'
sun_data.ortho_scale = 2000  # mm
sun_data.clip_start = 10
sun_data.clip_end = 200000

sun_obj = bpy.data.objects.new("Sun", sun_data)
scene.collection.objects.link(sun_obj)
sun_obj.location = (0, 0, 100000)
sun_obj.rotation_euler = (0, 0, 0)

# ============================================================
# 测试点（mm）：卫星包围盒极值点
# ============================================================
TEST_POINTS = [
    [float(verts_array[:,0].max()), 0.0, 0.0],
    [0.0, float(verts_array[:,1].max()), 0.0],
    [0.0, 0.0, float(verts_array[:,2].max())],
]

# ============================================================
# 渲染设置
# ============================================================
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_depth = '32'

# 使用 view_layer 的 Z pass
scene.view_layers[0].use_pass_z = True

# ============================================================
# 辅助函数
# ============================================================
def compute_view_matrix(cam_obj):
    """计算世界→相机视图矩阵"""
    R = np.array(cam_obj.matrix_world.to_3x3().normalized())
    t = np.array(cam_obj.location)
    view = np.zeros((4, 4))
    view[:3, :3] = R.T
    view[:3, 3] = -R.T @ t
    view[3, 3] = 1.0
    return view

def compute_perspective_matrix(cam_data):
    """计算透视投影矩阵"""
    f = cam_data.lens
    sw = cam_data.sensor_width
    ar = scene.render.resolution_x / scene.render.resolution_y
    fov_factor = 2 * f / sw

    P = np.zeros((4, 4))
    P[0, 0] = fov_factor / ar
    P[1, 1] = fov_factor
    P[2, 2] = -(cam_data.clip_end + cam_data.clip_start) / (cam_data.clip_end - cam_data.clip_start)
    P[2, 3] = -2 * cam_data.clip_end * cam_data.clip_start / (cam_data.clip_end - cam_data.clip_start)
    P[3, 2] = -1.0
    return P

def compute_ortho_matrix(cam_data):
    """计算正交投影矩阵"""
    s = cam_data.ortho_scale
    ar = scene.render.resolution_x / scene.render.resolution_y
    n, f = cam_data.clip_start, cam_data.clip_end

    P = np.zeros((4, 4))
    P[0, 0] = 2 / (s * ar)
    P[1, 1] = 2 / s
    P[2, 2] = -2 / (f - n)
    P[2, 3] = -(f + n) / (f - n)
    P[3, 3] = 1.0
    return P

def project_point(point, view, proj):
    """投影点到像素坐标 + depth"""
    p4 = np.array([point[0], point[1], point[2], 1.0])
    vc = view @ p4
    ndc = proj @ vc
    ndc /= ndc[3]
    u = (ndc[0] + 1) / 2 * scene.render.resolution_x
    v = (ndc[1] + 1) / 2 * scene.render.resolution_y
    depth = -vc[2]  # 正值 depth = -z_cam
    return u, v, depth

# ============================================================
# 计算矩阵
# ============================================================
cam_view = compute_view_matrix(cam_obj)
cam_proj = compute_perspective_matrix(cam_data)
sun_view = compute_view_matrix(sun_obj)
sun_proj = compute_ortho_matrix(sun_data)

print("\n[INFO] 测试点投影检查:")
for i, pt in enumerate(TEST_POINTS):
    cu, cv, cd = project_point(pt, cam_view, cam_proj)
    su, sv, sd = project_point(pt, sun_view, sun_proj)
    print(f"  P{i}: ({pt[0]:.1f}, {pt[1]:.1f}, {pt[2]:.1f}) mm")
    print(f"    Camera: u={cu:.1f}, v={cv:.1f}, depth={cd:.1f} mm")
    print(f"    Sun:    u={su:.1f}, v={sv:.1f}, depth={sd:.1f} mm")

# ============================================================
# 渲染 Camera Depth
# ============================================================
print("\n[INFO] 渲染 Camera Depth...")
scene.camera = cam_obj
cam_depth_path = str(DEPTH_MAP_DIR / "camera_depth.exr")
scene.render.filepath = cam_depth_path
bpy.ops.render.render(write_still=True)
print(f"  已保存: {cam_depth_path}")

# ============================================================
# 渲染 Sun Depth
# ============================================================
print("\n[INFO] 渲染 Sun Depth...")
scene.camera = sun_obj
sun_depth_path = str(DEPTH_MAP_DIR / "sun_depth.exr")
scene.render.filepath = sun_depth_path
bpy.ops.render.render(write_still=True)
print(f"  已保存: {sun_depth_path}")

# ============================================================
# 导出矩阵验证数据
# ============================================================
verification_data = {
    "test_type": "depth_round_trip_sanity_check",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "camera": {
        "location": list(cam_obj.location),
        "focal_length_mm": cam_data.lens,
        "sensor_width_mm": cam_data.sensor_width,
        "clip_start_mm": cam_data.clip_start,
        "clip_end_mm": cam_data.clip_end,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    },
    "sun": {
        "location": list(sun_obj.location),
        "type": "ORTHO",
        "ortho_scale_mm": sun_data.ortho_scale,
        "clip_start_mm": sun_data.clip_start,
        "clip_end_mm": sun_data.clip_end,
    },
    "test_points_mm": TEST_POINTS,
    "cam_view_matrix": cam_view.tolist(),
    "cam_projection_matrix": cam_proj.tolist(),
    "sun_view_matrix": sun_view.tolist(),
    "sun_projection_matrix": sun_proj.tolist(),
    "notes": [
        "depth = -z_cam (正值, Blender Z pass)",
        "单位: mm (与 STL 一致)",
        "camera: 透视投影, 50mm focal",
        "sun: 正交投影, ortho_scale=2000mm",
    ],
}

with open(str(MATRIX_JSON), "w", encoding="utf-8") as f:
    json.dump(verification_data, f, indent=2, ensure_ascii=False)

print(f"\n[INFO] 矩阵验证数据已导出: {MATRIX_JSON}")
print("[INFO] Blender 渲染完成，退出。")

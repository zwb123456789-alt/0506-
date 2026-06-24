# -*- coding: utf-8 -*-
"""
depth_round_trip_check.py —— 1C-E06 Phase 0 Step 2
===================================================
验证 Blender depth 符号、单位、local z 映射：
  1. 渲染 camera depth 和 sun depth（EXR）
  2. 选 3 个已知 mesh 顶点
  3. project → unproject round-trip（camera / sun 各自独立）
  4. depth map 采样 vs 计算深度对比

任务边界（R10 Codex）：
  - 只做 Phase 0 Step 2
  - 不做 20 姿态 shadow validation
  - 不校准 DEPTH_EPSILON_M_FINAL
  - 不运行全量 2664 姿态
  - 不训练模型
  - 不写论文结论

用法：
  python depth_round_trip_check.py
  （自动调用 Blender 渲染 + Python 验证）
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path

import numpy as np

# ============================================================
# 路径设置
# ============================================================
PROJECT_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
CODE_DIR = PROJECT_ROOT / "06_v0.4_code"
RESULT_DIR = PROJECT_ROOT / "v0.4_results" / "00_validation"
BLENDER_EXE = r"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

RENDER_SCRIPT = CODE_DIR / "10_validation" / "_depth_render.py"
DEPTH_MAP_DIR = RESULT_DIR / "depth_maps"
MATRIX_JSON = DEPTH_MAP_DIR / "matrix_verification.json"


# ============================================================
# Blender 场景设置脚本模板（路径占位符在运行时替换）
# ============================================================
BLENDER_SETUP_SCRIPT_TEMPLATE = r'''
# -*- coding: utf-8 -*-
"""
Blender depth render — 被 depth_round_trip_check.py 调用
设置场景 + 渲染 camera/sun depth + 导出矩阵
"""
import bpy
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
# 从 JSON 加载预处理好的 mesh 数据
# ============================================================
MESH_JSON = Path(r"MESH_JSON_PATH")
with open(str(MESH_JSON), "r", encoding="utf-8") as f:
    mesh_data = json.load(f)

all_verts = mesh_data["vertices"]
all_faces = mesh_data["faces"]

print(f"[Blender] 加载 mesh: {len(all_verts)} 顶点, {len(all_faces)} 面")

# 创建 Blender mesh
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
'''

# ============================================================
# 写入 Blender 脚本
# ============================================================
def write_blender_script():
    """将 Blender 脚本写入临时文件"""
    RENDER_SCRIPT.parent.mkdir(parents=True, exist_ok=True)
    with open(str(RENDER_SCRIPT), "w", encoding="utf-8") as f:
        f.write(BLENDER_SETUP_SCRIPT)
    print(f"[OK] Blender 脚本已写入: {RENDER_SCRIPT}")


# ============================================================
# 调用 Blender 渲染
# ============================================================
def run_blender_render():
    """调用 Blender 后台渲染"""
    DEPTH_MAP_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        BLENDER_EXE,
        "--background",
        "--python", str(RENDER_SCRIPT),
    ]

    print(f"[RUN] Blender 渲染: {' '.join(cmd[:3])} ...")
    t0 = time.time()

    result = subprocess.run(
        cmd,
        capture_output=True,
        timeout=300,
    )

    elapsed = time.time() - t0
    print(f"[OK] Blender 渲染完成，耗时 {elapsed:.1f} 秒")

    # 保存 Blender 输出日志
    log_path = DEPTH_MAP_DIR / "blender_render_log.txt"
    stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
    stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
    with open(str(log_path), "w", encoding="utf-8") as f:
        f.write("=== STDOUT ===\n")
        f.write(stdout)
        f.write("\n=== STDERR ===\n")
        f.write(stderr)

    if result.returncode != 0:
        print(f"[WARN] Blender 返回码: {result.returncode}")
        print(f"  日志: {log_path}")

    return result.returncode == 0


# ============================================================
# 读取 EXR depth map
# ============================================================
def load_exr_depth(path):
    """读取 EXR Z 通道为 float32 数组"""
    try:
        import OpenEXR
        import Imath

        exr = OpenEXR.InputFile(str(path))
        dw = exr.header()['dataWindow']
        w = dw.max.x - dw.min.x + 1
        h = dw.max.y - dw.min.y + 1

        # 尝试读取 Z 通道
        channels = exr.header()['channels']
        channel_names = list(channels.keys())

        # 寻找 Z 通道
        z_channel = None
        for name in channel_names:
            if name.lower() in ('z', 'depth', 'z.depth', 'view_z'):
                z_channel = name
                break

        if z_channel is None:
            # 尝试第一个通道
            z_channel = channel_names[0]
            print(f"  [WARN] 未找到 Z 通道，使用: {z_channel}")

        raw = exr.channel(z_channel, Imath.PixelType(Imath.PixelType.FLOAT))
        depth = np.frombuffer(raw, dtype=np.float32).reshape(h, w)
        exr.close()

    except ImportError:
        # 回退到 imageio
        import imageio
        data = imageio.imread(str(path))
        if data.ndim == 3:
            depth = data[:, :, 0].astype(np.float32)
        else:
            depth = data.astype(np.float32)

    return depth


# ============================================================
# 反投影：像素 + depth → 世界坐标
# ============================================================
def unproject(u, v, depth, view_inv, proj_inv, res_x, res_y, proj_type='PERSP'):
    """
    反投影：像素坐标 + depth → 世界坐标

    depth = -z_cam (正值)
    """
    ndc_x = 2 * u / res_x - 1
    ndc_y = 2 * v / res_y - 1

    if proj_type == 'PERSP':
        clip = np.array([ndc_x, ndc_y, 1.0, 1.0])
        view = proj_inv @ clip
        view /= view[3]
        view[0] *= -depth / view[2]
        view[1] *= -depth / view[2]
        view[2] = -depth
        view[3] = 1.0
    else:  # ORTHO
        clip = np.array([ndc_x, ndc_y, 1.0, 1.0])
        view = proj_inv @ clip
        view[2] = -depth
        view[3] = 1.0

    world = view_inv @ view
    return world[:3]


# ============================================================
# 采样 depth map
# ============================================================
def sample_depth(depth_map, u, v, res_x, res_y):
    """最近邻采样 depth map"""
    px = int(round(u))
    py = int(round(v))
    if 0 <= px < res_x and 0 <= py < res_y:
        return float(depth_map[py, px])
    return None


# ============================================================
# 验证 round-trip
# ============================================================
def verify_round_trip():
    """验证 depth round-trip"""
    # 加载矩阵数据
    with open(str(MATRIX_JSON), "r", encoding="utf-8") as f:
        data = json.load(f)

    test_points = np.array(data["test_points_mm"])
    cam_view = np.array(data["cam_view_matrix"])
    cam_proj = np.array(data["cam_projection_matrix"])
    sun_view = np.array(data["sun_view_matrix"])
    sun_proj = np.array(data["sun_projection_matrix"])

    # 反转矩阵
    cam_view_inv = np.linalg.inv(cam_view)
    cam_proj_inv = np.linalg.inv(cam_proj)
    sun_view_inv = np.linalg.inv(sun_view)
    sun_proj_inv = np.linalg.inv(sun_proj)

    # 参数
    f = data["camera"]["focal_length_mm"]
    sw = data["camera"]["sensor_width_mm"]
    res_x, res_y = data["camera"]["resolution"]
    n_cam = data["camera"]["clip_start_mm"]
    f_cam = data["camera"]["clip_end_mm"]
    ar = res_x / res_y

    # 读取 depth maps
    cam_exr = DEPTH_MAP_DIR / "camera_depth.exr"
    sun_exr = DEPTH_MAP_DIR / "sun_depth.exr"

    cam_depth = load_exr_depth(cam_exr)
    sun_depth = load_exr_depth(sun_exr)

    print(f"[INFO] Camera depth map: {cam_depth.shape}, "
          f"range=[{np.nanmin(cam_depth):.2f}, {np.nanmax(cam_depth):.2f}] mm")
    print(f"[INFO] Sun depth map:    {sun_depth.shape}, "
          f"range=[{np.nanmin(sun_depth):.2f}, {np.nanmax(sun_depth):.2f}] mm")

    # 结果容器
    results = {
        "test_points_mm": test_points.tolist(),
        "camera_roundtrip": [],
        "sun_roundtrip": [],
        "depth_map_comparison": [],
        "errors": [],
    }

    # ============================================================
    # 测试 1: Camera round-trip
    # ============================================================
    print("\n" + "=" * 60)
    print("测试 1: Camera 投影 → 反投影 round-trip")
    print("=" * 60)

    for i, pt in enumerate(test_points):
        # 投影
        p4 = np.array([pt[0], pt[1], pt[2], 1.0])
        vc = cam_view @ p4
        ndc = cam_proj @ vc
        ndc /= ndc[3]
        u = (ndc[0] + 1) / 2 * res_x
        v = (ndc[1] + 1) / 2 * res_y
        depth = -vc[2]  # 正值

        # 反投影
        recovered = unproject(u, v, depth, cam_view_inv, cam_proj_inv, res_x, res_y, 'PERSP')
        err = np.linalg.norm(recovered - pt)

        print(f"  P{i}: 原始=({pt[0]:.1f}, {pt[1]:.1f}, {pt[2]:.1f}) mm")
        print(f"       像素=({u:.1f}, {v:.1f}), depth={depth:.2f} mm")
        print(f"       恢复=({recovered[0]:.1f}, {recovered[1]:.1f}, {recovered[2]:.1f}) mm")
        print(f"       误差={err:.6f} mm")

        results["camera_roundtrip"].append({
            "point_index": i,
            "original_mm": pt.tolist(),
            "pixel": [float(u), float(v)],
            "depth_mm": float(depth),
            "recovered_mm": recovered.tolist(),
            "error_mm": float(err),
        })

    # ============================================================
    # 测试 2: Sun round-trip
    # ============================================================
    print("\n" + "=" * 60)
    print("测试 2: Sun 投影 → 反投影 round-trip")
    print("=" * 60)

    for i, pt in enumerate(test_points):
        p4 = np.array([pt[0], pt[1], pt[2], 1.0])
        vc = sun_view @ p4
        ndc = sun_proj @ vc
        ndc /= ndc[3]
        u = (ndc[0] + 1) / 2 * res_x
        v = (ndc[1] + 1) / 2 * res_y
        depth = -vc[2]

        recovered = unproject(u, v, depth, sun_view_inv, sun_proj_inv, res_x, res_y, 'ORTHO')
        err = np.linalg.norm(recovered - pt)

        print(f"  P{i}: 原始=({pt[0]:.1f}, {pt[1]:.1f}, {pt[2]:.1f}) mm")
        print(f"       像素=({u:.1f}, {v:.1f}), depth={depth:.2f} mm")
        print(f"       恢复=({recovered[0]:.1f}, {recovered[1]:.1f}, {recovered[2]:.1f}) mm")
        print(f"       误差={err:.6f} mm")

        results["sun_roundtrip"].append({
            "point_index": i,
            "original_mm": pt.tolist(),
            "pixel": [float(u), float(v)],
            "depth_mm": float(depth),
            "recovered_mm": recovered.tolist(),
            "error_mm": float(err),
        })

    # ============================================================
    # 测试 3: Depth map 采样 vs 计算深度
    # ============================================================
    print("\n" + "=" * 60)
    print("测试 3: Depth map 采样 vs 计算深度对比")
    print("=" * 60)

    for i, pt in enumerate(test_points):
        # Camera
        p4 = np.array([pt[0], pt[1], pt[2], 1.0])
        vc = cam_view @ p4
        ndc = cam_proj @ vc
        ndc /= ndc[3]
        cu = (ndc[0] + 1) / 2 * res_x
        cv = (ndc[1] + 1) / 2 * res_y
        cd_calc = -vc[2]

        cd_map = sample_depth(cam_depth, cu, cv, res_x, res_y)

        # Sun
        vs = sun_view @ p4
        ndc_s = sun_proj @ vs
        ndc_s /= ndc_s[3]
        su = (ndc_s[0] + 1) / 2 * res_x
        sv = (ndc_s[1] + 1) / 2 * res_y
        sd_calc = -vs[2]

        sd_map = sample_depth(sun_depth, su, sv, res_x, res_y)

        entry = {
            "point_index": i,
            "camera": {
                "pixel": [float(cu), float(cv)],
                "calculated_depth_mm": float(cd_calc),
                "map_depth_mm": float(cd_map) if cd_map is not None else None,
                "diff_mm": float(abs(cd_calc - cd_map)) if cd_map is not None else None,
            },
            "sun": {
                "pixel": [float(su), float(sv)],
                "calculated_depth_mm": float(sd_calc),
                "map_depth_mm": float(sd_map) if sd_map is not None else None,
                "diff_mm": float(abs(sd_calc - sd_map)) if sd_map is not None else None,
            },
        }
        results["depth_map_comparison"].append(entry)

        print(f"  P{i}:")
        cam_status = f"calc={cd_calc:.2f}, map={cd_map:.2f}, diff={abs(cd_calc-cd_map):.2f} mm" if cd_map is not None else "超出图像范围"
        sun_status = f"calc={sd_calc:.2f}, map={sd_map:.2f}, diff={abs(sd_calc-sd_map):.2f} mm" if sd_map is not None else "超出图像范围"
        print(f"    Camera: {cam_status}")
        print(f"    Sun:    {sun_status}")

    # ============================================================
    # 保存验证结果
    # ============================================================
    result_path = DEPTH_MAP_DIR / "round_trip_verification.json"
    with open(str(result_path), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] 验证结果已保存: {result_path}")
    return results


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 60)
    print("1C-E06 depth round-trip sanity check")
    print("=" * 60)
    print(f"  项目根目录: {PROJECT_ROOT}")
    print(f"  Blender: {BLENDER_EXE}")
    print()

    # Step 1: 写入 Blender 脚本
    write_blender_script()

    # Step 2: 调用 Blender 渲染
    ok = run_blender_render()
    if not ok:
        print("[ERROR] Blender 渲染失败，请检查日志")
        return None

    # Step 3: 验证 round-trip
    results = verify_round_trip()

    return results


if __name__ == "__main__":
    results = main()

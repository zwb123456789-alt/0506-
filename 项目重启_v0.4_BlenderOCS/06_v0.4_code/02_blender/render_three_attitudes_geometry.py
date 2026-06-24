# -*- coding: utf-8 -*-
"""
render_three_attitudes_geometry.py —— Phase 0 Step 3: 3 姿态几何 pass 渲染
================================================================================
本脚本在 Blender 内运行，为 3 个代表姿态生成 camera geometry pass。

使用方式：
    blender --background --python render_three_attitudes_geometry.py

输出：
    - Normal pass EXR（世界空间法线）
    - Depth pass EXR（camera depth）
    - IndexOB pass EXR（对象索引）
    - Position pass EXR（世界空间坐标）

边界：
    - 只做 3 个姿态
    - 不进入 20 姿态 shadow validation
    - 不运行全量 2664 姿态
"""

import os
import sys
import json
import math
from pathlib import Path
from datetime import datetime

try:
    import bpy
    import mathutils
    from mathutils import Vector, Matrix
except ImportError:
    print("[ERROR] bpy 不可用 —— 请用 blender --background --python 运行本脚本")
    sys.exit(1)


# ============================================================
# 1. 配置（从 config_v0_4.py 镜像）
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")
STL_DIR = os.path.join(PROJECT_ROOT, "建模", "真实模型")
OUTPUT_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "geometry_passes")

PART_FILES = {
    "jinshuzhuti": os.path.join(STL_DIR, "jinshuzhuti.stl"),
    "taiyangnengban": os.path.join(STL_DIR, "taiyangnengban.stl"),
    "yinshenban": os.path.join(STL_DIR, "yinshenban.stl"),
}

PART_PASS_INDEX = {
    "jinshuzhuti": 1,
    "taiyangnengban": 2,
    "yinshenban": 3,
}

UNIT_SCALE = 1e-3  # mm → m

# 观测几何（phase63 baseline）
SUN_VECTOR = [1.0, 0.0, 0.3]
DET_VECTOR = [0.5, -1.0, 0.1]

# 3 个代表姿态
ATTITUDES = [
    {"yaw": 0, "pitch": 0, "roll": 0, "label": "yaw000_pitch+000_roll+000"},
    {"yaw": 90, "pitch": 0, "roll": 0, "label": "yaw090_pitch+000_roll+000"},
    {"yaw": 0, "pitch": 45, "roll": 0, "label": "yaw000_pitch+045_roll+000"},
]

# 渲染参数
RESOLUTION = 256
SAMPLES = 1  # 几何 pass 不需要多采样


# ============================================================
# 2. 欧拉角转旋转矩阵（Z-Y-X 内旋）
# ============================================================
def euler_to_matrix4(yaw_deg, pitch_deg, roll_deg=0.0):
    """Z-Y-X 内旋，返回 Blender Matrix 4x4"""
    y = math.radians(yaw_deg)
    p = math.radians(pitch_deg)
    r = math.radians(roll_deg)

    cy, sy = math.cos(y), math.sin(y)
    cp, sp = math.cos(p), math.sin(p)
    cr, sr = math.cos(r), math.sin(r)

    Rz = Matrix((
        (cy, -sy, 0.0, 0.0),
        (sy, cy, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0)
    ))

    Ry = Matrix((
        (cp, 0.0, sp, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (-sp, 0.0, cp, 0.0),
        (0.0, 0.0, 0.0, 1.0)
    ))

    Rx = Matrix((
        (1.0, 0.0, 0.0, 0.0),
        (0.0, cr, -sr, 0.0),
        (0.0, sr, cr, 0.0),
        (0.0, 0.0, 0.0, 1.0)
    ))

    return Rz @ Ry @ Rx


# ============================================================
# 3. 场景搭建
# ============================================================
def clear_scene():
    """清空 Blender 场景"""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for block in (bpy.data.meshes, bpy.data.materials,
                  bpy.data.lights, bpy.data.cameras, bpy.data.images):
        for item in list(block):
            block.remove(item)


def import_one_stl(filepath):
    """导入单个 STL 文件"""
    before = set(bpy.data.objects)

    # Blender 4.x 使用 wm.stl_import
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=filepath)
    else:
        # Blender 3.x 使用 import_mesh.stl
        bpy.ops.import_mesh.stl(filepath=filepath)

    after = set(bpy.data.objects)
    new = list(after - before)

    if not new:
        raise RuntimeError(f"STL 导入失败: {filepath}")

    return new[0]


def make_dummy_material(name):
    """创建哑材质（用于区分对象）"""
    mat = bpy.data.materials.new(name=f"mat_{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Principled BSDF
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
    bsdf.location = (0, 0)

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (300, 0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    return mat


def import_stls():
    """导入所有 STL 部件并设置父子关系"""
    print("  导入 STL 文件...")

    # 创建根对象
    sat_root = bpy.data.objects.new("Sat_Root", None)
    bpy.context.collection.objects.link(sat_root)

    for part_name, path in PART_FILES.items():
        if not os.path.isfile(path):
            raise RuntimeError(f"STL 不存在: {path}")

        obj = import_one_stl(path)
        obj.name = part_name
        obj.parent = sat_root

        # 设置 pass_index（用于 IndexOB pass）
        obj.pass_index = PART_PASS_INDEX[part_name]

        # 强制 flat shading（每个面元独立法线）
        mesh = obj.data
        for poly in mesh.polygons:
            poly.use_smooth = False

        # 清除 auto-smooth（Blender 4.x）
        if hasattr(mesh, "use_auto_smooth"):
            mesh.use_auto_smooth = False

        # 分配材质
        mat = make_dummy_material(part_name)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        print(f"    [{part_name}] pass_index={obj.pass_index}")

    # 单位缩放（mm → m）
    sat_root.scale = (UNIT_SCALE, UNIT_SCALE, UNIT_SCALE)

    return sat_root


def compute_bbox_radius(sat_root):
    """计算边界框半径"""
    bpy.context.view_layer.update()
    r_max = 0.0

    for child in sat_root.children:
        for corner in child.bound_box:
            v_world = child.matrix_world @ Vector(corner)
            r = v_world.length
            if r > r_max:
                r_max = r

    if r_max <= 0.0:
        r_max = 1.0

    return r_max


def setup_camera(det_vec, r_max):
    """设置正交相机"""
    det = Vector(det_vec).normalized()

    cam_data = bpy.data.cameras.new("Camera")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.2 * r_max  # 与 config_v0_4.py 一致

    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)

    # 相机位置：探测器方向，距离 5 * r_max
    cam.location = det * (5.0 * r_max)

    # 相机朝向：看向原点（-det 方向）
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (-det).to_track_quat('-Z', 'Y')

    bpy.context.scene.camera = cam

    return cam


def setup_sun(sun_vec):
    """设置太阳光源"""
    sun_dir = Vector(sun_vec).normalized()

    light_data = bpy.data.lights.new("Sun", type="SUN")
    light_data.energy = 5.0
    light_data.angle = math.radians(0.5)

    sun = bpy.data.objects.new("Sun", light_data)
    bpy.context.collection.objects.link(sun)

    sun.rotation_mode = "QUATERNION"
    sun.rotation_quaternion = sun_dir.to_track_quat('Z', 'Y')

    return sun


def setup_render_passes(scene):
    """配置渲染 passes（Normal/Depth/IndexOB/Position）"""
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = RESOLUTION
    scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100

    # EXR 32-bit float 输出 - 使用 MultiLayer 模式以保存所有 passes
    scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"

    # 线性输出（不做 gamma 变换）
    scene.view_settings.view_transform = "Raw"

    # Cycles 参数
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = False

    # GPU 加速（如果可用）
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.get_devices()
        for backend in ("OPTIX", "CUDA", "HIP", "METAL"):
            try:
                prefs.compute_device_type = backend
                if any(d.use for d in prefs.devices):
                    scene.cycles.device = "GPU"
                    print(f"  GPU backend: {backend}")
                    break
            except Exception:
                continue
        else:
            scene.cycles.device = "CPU"
            print("  使用 CPU 渲染")
    except Exception as e:
        scene.cycles.device = "CPU"
        print(f"  GPU 不可用，使用 CPU: {e}")

    # 启用 View Layer passes
    vl = scene.view_layers[0]
    vl.use_pass_combined = True      # Combined RGBA
    vl.use_pass_normal = True        # Normal pass（世界空间）
    vl.use_pass_z = True             # Depth pass（camera depth）
    vl.use_pass_object_index = True  # IndexOB pass（对象索引）
    vl.use_pass_position = True      # Position pass（世界空间坐标）

    print("  启用 View Layer passes: Combined, Normal, Z, IndexOB, Position")


def apply_attitude(sat_root, yaw, pitch, roll):
    """应用姿态旋转，保留缩放"""
    # 构建包含缩放的变换矩阵
    R = euler_to_matrix4(yaw, pitch, roll)

    # 构建缩放矩阵
    S = Matrix.Scale(UNIT_SCALE, 4)

    # 组合：先缩放，后旋转
    sat_root.matrix_world = R @ S


def render_one_attitude(scene, sat_root, attitude, output_dir):
    """渲染单个姿态的所有 passes"""
    label = attitude["label"]
    yaw = attitude["yaw"]
    pitch = attitude["pitch"]
    roll = attitude["roll"]

    print(f"\n  渲染姿态: {label}")
    print(f"    yaw={yaw}, pitch={pitch}, roll={roll}")

    # 应用姿态
    apply_attitude(sat_root, yaw, pitch, roll)
    bpy.context.view_layer.update()

    # 输出路径
    output_path = os.path.join(output_dir, label)
    scene.render.filepath = output_path

    # 渲染
    bpy.ops.render.render(write_still=True)

    print(f"    输出: {output_path}.exr")

    return output_path + ".exr"


# ============================================================
# 4. 主执行流程
# ============================================================
def main():
    print("=" * 80)
    print("Phase 0 Step 3: 3 姿态 Blender geometry pass 渲染")
    print("=" * 80)
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 创建输出目录
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"\n输出目录: {OUTPUT_DIR}")

    # 清空场景
    print("\n清空场景...")
    clear_scene()

    # 导入 STL
    sat_root = import_stls()

    # 计算边界框半径
    r_max = compute_bbox_radius(sat_root)
    print(f"\n边界框半径: {r_max:.3f} m")

    # 设置相机和光源
    print("\n设置相机和光源...")
    setup_camera(DET_VECTOR, r_max)
    setup_sun(SUN_VECTOR)

    # 配置渲染 passes
    print("\n配置渲染 passes...")
    scene = bpy.context.scene
    setup_render_passes(scene)

    # 渲染 3 个姿态
    print("\n" + "=" * 80)
    print("开始渲染 3 个姿态")
    print("=" * 80)

    results = []
    for i, attitude in enumerate(ATTITUDES, 1):
        print(f"\n[{i}/3]")
        output_file = render_one_attitude(scene, sat_root, attitude, OUTPUT_DIR)
        results.append({
            "attitude": attitude,
            "output_file": output_file,
            "exists": os.path.isfile(output_file)
        })

    # 保存元数据
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "resolution": RESOLUTION,
        "samples": SAMPLES,
        "attitudes": ATTITUDES,
        "sun_vector": SUN_VECTOR,
        "det_vector": DET_VECTOR,
        "r_max": r_max,
        "results": results
    }

    metadata_file = os.path.join(OUTPUT_DIR, "render_metadata.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("渲染完成")
    print("=" * 80)
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"元数据: {metadata_file}")

    # 检查输出文件
    print("\n输出文件检查:")
    all_ok = True
    for result in results:
        status = "[OK]" if result["exists"] else "[MISS]"
        print(f"  {status} {result['attitude']['label']}")
        if not result["exists"]:
            all_ok = False

    if all_ok:
        print("\n[SUCCESS] 所有姿态渲染完成")
        return 0
    else:
        print("\n[WARNING] 部分姿态渲染失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

# -*- coding: utf-8 -*-
"""
log_camera_matrices.py —— 记录 Blender 相机矩阵
==================================================
任务：在真实 Blender 场景中搭建与 render_20_attitudes_shadow.py 完全相同的
      camera-view 和 sun-view 相机，输出其 matrix_world 到 JSON。

使用方式：
    blender --background --python log_camera_matrices.py

输出：
    v0.4_results/00_validation/phase0_step7c_dryrun_fix02/camera_matrices_blender.json

边界：
    - 不渲染任何图像
    - 不修改场景文件
    - 仅记录矩阵，不作任何姿态变换
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
# 1. 配置（与 render_20_attitudes_shadow.py 完全一致）
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")
STL_DIR = os.path.join(PROJECT_ROOT, "建模", "真实模型")
OUTPUT_DIR = os.path.join(V04_PROJECT, "v0.4_results", "00_validation", "phase0_step7c_dryrun_fix02")

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

UNIT_SCALE = 1e-3  # mm -> m
SUN_VECTOR = [1.0, 0.0, 0.3]
DET_VECTOR = [0.5, -1.0, 0.1]


# ============================================================
# 2. 场景搭建（复用 render_20_attitudes_shadow.py 逻辑）
# ============================================================
def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials,
                  bpy.data.lights, bpy.data.cameras, bpy.data.images):
        for item in list(block):
            block.remove(item)


def import_one_stl(filepath):
    before = set(bpy.data.objects)
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=filepath)
    else:
        bpy.ops.import_mesh.stl(filepath=filepath)
    after = set(bpy.data.objects)
    new = list(after - before)
    if not new:
        raise RuntimeError(f"STL 导入失败: {filepath}")
    return new[0]


def make_dummy_material(name):
    mat = bpy.data.materials.new(name=f"mat_{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
    bsdf.location = (0, 0)
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (300, 0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def import_stls():
    print("  导入 STL 文件...")
    sat_root = bpy.data.objects.new("Sat_Root", None)
    bpy.context.collection.objects.link(sat_root)
    for part_name, path in PART_FILES.items():
        if not os.path.isfile(path):
            raise RuntimeError(f"STL 不存在: {path}")
        obj = import_one_stl(path)
        obj.name = part_name
        obj.parent = sat_root
        obj.pass_index = PART_PASS_INDEX[part_name]
        mesh = obj.data
        for poly in mesh.polygons:
            poly.use_smooth = False
        if hasattr(mesh, "use_auto_smooth"):
            mesh.use_auto_smooth = False
        mat = make_dummy_material(part_name)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        print(f"    [{part_name}] pass_index={obj.pass_index}")
    sat_root.scale = (UNIT_SCALE, UNIT_SCALE, UNIT_SCALE)
    return sat_root


def compute_bbox_radius(sat_root):
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


def setup_camera(direction_vec, r_max, name="Camera"):
    """设置正交相机，与 render_20_attitudes_shadow.py 完全一致"""
    direction = Vector(direction_vec).normalized()
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.2 * r_max
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = direction * (5.0 * r_max)
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (-direction).to_track_quat('-Z', 'Y')
    return cam


def setup_sun(sun_vec):
    """设置太阳光源，与 render_20_attitudes_shadow.py 完全一致"""
    sun_dir = Vector(sun_vec).normalized()
    light_data = bpy.data.lights.new("Sun", type="SUN")
    light_data.energy = 5.0
    light_data.angle = math.radians(0.5)
    sun = bpy.data.objects.new("Sun", light_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_mode = "QUATERNION"
    sun.rotation_quaternion = sun_dir.to_track_quat('Z', 'Y')
    return sun


def matrix_to_list(mat):
    """将 Blender Matrix 转为 list[list[float]]"""
    rows = []
    for i in range(4):
        row = [float(mat[i][j]) for j in range(4)]
        rows.append(row)
    return rows


# ============================================================
# 3. 主流程
# ============================================================
def main():
    print("=" * 80)
    print("Phase 0 Step 7c: Blender 相机矩阵日志")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"输出目录: {OUTPUT_DIR}")

    # 清空并重建场景
    print("\n清空场景...")
    clear_scene()

    sat_root = import_stls()
    r_max = compute_bbox_radius(sat_root)
    print(f"\n边界框半径: {r_max:.6f} m")

    print("\n设置相机...")
    camera_cam = setup_camera(DET_VECTOR, r_max, name="Camera_Detector")
    sun_cam = setup_camera(SUN_VECTOR, r_max, name="Camera_Sun")

    # 刷新场景以确保矩阵正确
    bpy.context.view_layer.update()

    # 读取 matrix_world
    camera_matrix_world = matrix_to_list(camera_cam.matrix_world)
    sun_camera_matrix_world = matrix_to_list(sun_cam.matrix_world)

    print(f"\nCamera_Detector matrix_world (4x4):")
    for row in camera_matrix_world:
        print(f"  {row}")

    print(f"\nCamera_Sun matrix_world (4x4):")
    for row in sun_camera_matrix_world:
        print(f"  {row}")

    # 验证矩阵元素均可转 float（自检）
    for i, row in enumerate(camera_matrix_world):
        for j, val in enumerate(row):
            try:
                float(val)
            except (TypeError, ValueError):
                print(f"[ERROR] camera_matrix_world[{i}][{j}] not float-convertible: {val!r}")
                sys.exit(1)

    for i, row in enumerate(sun_camera_matrix_world):
        for j, val in enumerate(row):
            try:
                float(val)
            except (TypeError, ValueError):
                print(f"[ERROR] sun_camera_matrix_world[{i}][{j}] not float-convertible: {val!r}")
                sys.exit(1)

    # 构建输出
    output = {
        "timestamp": datetime.now().isoformat(),
        "task": "1C-E15-FIX02 camera matrix logging from Blender scene",
        "r_max": r_max,
        "sun_vector": SUN_VECTOR,
        "det_vector": DET_VECTOR,
        "camera_matrix_world": camera_matrix_world,
        "sun_camera_matrix_world": sun_camera_matrix_world,
        "note": (
            "矩阵来自 Blender 场景对象的 matrix_world 属性。"
            "camera_matrix_world = Camera_Detector.matrix_world（detector 方向相机）。"
            "sun_camera_matrix_world = Camera_Sun.matrix_world（sun 方向相机）。"
            "矩阵方向均为 camera/sun camera local -> world。"
        ),
    }

    output_path = os.path.join(OUTPUT_DIR, "camera_matrices_blender.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n矩阵日志写出: {output_path}")
    print("\n[SUCCESS] 相机矩阵记录完成（未执行渲染）")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

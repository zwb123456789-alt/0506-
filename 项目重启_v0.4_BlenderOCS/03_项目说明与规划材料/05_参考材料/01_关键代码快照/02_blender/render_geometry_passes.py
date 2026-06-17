# -*- coding: utf-8 -*-
"""
render_geometry_passes.py —— 模块 B · 几何缓冲渲染（MVP）
============================================================
输出 Normal Pass + Depth Pass EXR 文件，供 Python 后处理计算 exact BRDF。

使用方式：
    blender.exe --background --python render_geometry_passes.py -- --limit 5

【管线设计】
1. Blender Cycles 渲染 Normal Pass（世界空间法线）和 Depth Pass（深度）
   EXR 32-bit float，保留全精度。
2. Python 端：
   (a) 读 Normal EXR → world-space N（每个像素）
   (b) 读 Depth EXR  → 前景/背景掩码
   (c) 读 Object ID  → 部件材质（rho_d/rho_s/n）
   (d) BRDF = eval_legacy_phong(N, L_sun, L_det, ...)
   (e) pixel_radiance = BRDF × E_sun（归一化辐照度常数）
   (f) 像素面积 = (2.2·r_max / res)²
   (g) OCS_image = sum(pixel_radiance × pixel_area) / res²   （归一化面积元）
   (h) 输出 EXR + 可视化 PNG + ocs_comparison.csv

【与模块 A 对齐】
- 同一套太阳/探测器方向（来自 ocs_scan.json）
- 同一套姿态矩阵（R = Rz @ Ry @ Rx）
- 同一套材质参数（rho_d/rho_s/n）
- 同一种 BRDF 公式（eval_legacy_phong）
"""

import os
import sys
import csv
import json
import math
import time
import glob
import argparse
from datetime import datetime
from pathlib import Path

import numpy as np

try:
    import bpy
    import mathutils
    from mathutils import Vector, Matrix
except ImportError:
    print("[FAIL] bpy 不可用 —— 请用 blender.exe --background --python 运行本脚本。")
    sys.exit(1)


# ============================================================
# 常量（与 render_batch.py / config.py 保持一致）
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
STL_DIR      = os.path.join(PROJECT_ROOT, "建模", "真实模型")
OUTPUT_ROOT  = os.path.join(PROJECT_ROOT, "结果", "模块B_渲染")
SCAN_GLOB    = os.path.join(PROJECT_ROOT, "结果", "模块A_重构", "*", "run_*", "ocs_scan.json")

PART_FILES = {
    "jinshuzhuti":    os.path.join(STL_DIR, "jinshuzhuti.stl"),
    "taiyangnengban": os.path.join(STL_DIR, "taiyangnengban.stl"),
    "yinshenban":     os.path.join(STL_DIR, "yinshenban.stl"),
}

PART_PASS_INDEX = {
    "jinshuzhuti":    1,
    "taiyangnengban": 2,
    "yinshenban":     3,
}

UNIT_SCALE = 1e-3  # mm → m

# LegacyPhong 材料参数（与 ocs_core.py / materials.py 完全一致）
MATERIALS = {
    "jinshuzhuti":    {"rho_d": 0.20, "rho_s": 0.60, "n": 80},
    "taiyangnengban": {"rho_d": 0.15, "rho_s": 0.10, "n": 20},
    "yinshenban":     {"rho_d": 0.08, "rho_s": 0.02, "n": 10},
}

SUN_FALLBACK = [1.0,  0.0, 0.3]
DET_FALLBACK = [0.5, -1.0, 0.1]


# ============================================================
# 1. 参数解析
# ============================================================
def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    p = argparse.ArgumentParser(description="Module B geometry passes renderer (exact BRDF)")
    p.add_argument("--scan-json", default=None,
                   help="ocs_scan.json 路径，默认自动找最新")
    p.add_argument("--out-dir",   default=None,
                   help="输出根目录，默认 结果/模块B_渲染/run_YYYYMMDD_HHMMSS/")
    p.add_argument("--limit",     type=int, default=0,
                   help="只渲染前 N 个姿态；0 表示全部")
    p.add_argument("--res",       type=int, default=256,
                   help="渲染分辨率（正方形）")
    p.add_argument("--samples",   type=int, default=1,
                   help="Cycles 采样数（几何通道不需要采样>1）")
    return p.parse_args(argv)


def find_latest_scan_json():
    cands = sorted(glob.glob(SCAN_GLOB), key=os.path.getmtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"未找到 ocs_scan.json，glob: {SCAN_GLOB}")
    return cands[0]


# ============================================================
# 2. 数学：欧拉角 → 4×4 矩阵（镜像 geometry.py:16-38）
# ============================================================
def euler_to_matrix4(yaw_deg, pitch_deg, roll_deg=0.0):
    """Z-Y-X 内旋；返回 mathutils.Matrix 4×4。"""
    y = math.radians(yaw_deg)
    p = math.radians(pitch_deg)
    r = math.radians(roll_deg)
    cy, sy = math.cos(y), math.sin(y)
    cp, sp = math.cos(p), math.sin(p)
    cr, sr = math.cos(r), math.sin(r)
    Rz = Matrix(((cy, -sy, 0.0, 0.0),
                 (sy,  cy, 0.0, 0.0),
                 (0.0, 0.0, 1.0, 0.0),
                 (0.0, 0.0, 0.0, 1.0)))
    Ry = Matrix(((cp,  0.0, sp, 0.0),
                 (0.0, 1.0, 0.0, 0.0),
                 (-sp, 0.0, cp, 0.0),
                 (0.0, 0.0, 0.0, 1.0)))
    Rx = Matrix(((1.0, 0.0, 0.0, 0.0),
                 (0.0, cr, -sr, 0.0),
                 (0.0, sr,  cr, 0.0),
                 (0.0, 0.0, 0.0, 1.0)))
    return Rz @ Ry @ Rx


# ============================================================
# 3. 场景搭建
# ============================================================
def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials,
                  bpy.data.lights, bpy.data.cameras,
                  bpy.data.images):
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
    """哑材质：让 Cycles 输出 Normal/Depth pass 时每个对象有可区分 ID。

    背面像素通过 Backfacing AOV 在后处理中精确过滤，不在材质层做透明。
    """
    mat = bpy.data.materials.new(name=f"mat_{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Principled BSDF
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.location = (0, 0)

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (300, 0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Geometry → AOV：输出 Backfacing 值（0.0=正面，1.0=背面），供后处理做精确背面遮罩
    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-200, -200)

    aov = nodes.new("ShaderNodeOutputAOV")
    aov.name = "Backfacing"
    aov.location = (200, -200)
    links.new(geom.outputs["Backfacing"], aov.inputs["Value"])

    return mat


def import_stls_under_parent():
    sat_root = bpy.data.objects.new("Sat_Root", None)
    bpy.context.collection.objects.link(sat_root)
    for part_name, path in PART_FILES.items():
        if not os.path.isfile(path):
            raise RuntimeError(f"STL 不存在: {path}")
        obj = import_one_stl(path)
        obj.name = part_name
        obj.parent = sat_root
        # 给 IndexOB pass 提供可区分整数 ID
        obj.pass_index = PART_PASS_INDEX[part_name]
        # 强制 flat shading：每个面元独立法线（与模块 A 一致）
        # 否则 Blender 顶点法线插值会平均掉 BRDF 镜面峰
        mesh = obj.data
        for poly in mesh.polygons:
            poly.use_smooth = False
        # Blender 4.x：清除 auto-smooth / shade-auto 的修饰器
        if hasattr(mesh, "use_auto_smooth"):
            mesh.use_auto_smooth = False
        mat = make_dummy_material(part_name)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    sat_root.scale = (UNIT_SCALE, UNIT_SCALE, UNIT_SCALE)
    return sat_root


def compute_bbox_radius(sat_root):
    apply_attitude(sat_root, 0.0, 0.0, 0.0)
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


def setup_camera(det_vec_I, r_max):
    det = Vector(det_vec_I).normalized()
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.2 * r_max
    cam = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = det * (5.0 * r_max)
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (-det).to_track_quat('-Z', 'Y')
    bpy.context.scene.camera = cam
    return cam


def setup_sun(sun_vec_I):
    sun_dir = Vector(sun_vec_I).normalized()
    light_data = bpy.data.lights.new("Sun", type="SUN")
    light_data.energy = 5.0
    light_data.angle = math.radians(0.5)
    sun = bpy.data.objects.new("Sun", light_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_mode = "QUATERNION"
    sun.rotation_quaternion = sun_dir.to_track_quat('Z', 'Y')
    return sun


def setup_render_passes(scene, res, samples):
    """配置 Cycles 输出 Normal + Depth passes（32-bit float EXR）。"""
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.view_settings.view_transform = "Raw"  # 线性输出，不做 gamma

    scene.cycles.samples = samples
    scene.cycles.use_denoising = False

    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.get_devices()
        for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
            try:
                prefs.compute_device_type = backend
                if any(d.use for d in prefs.devices):
                    scene.cycles.device = "GPU"
                    print(f"[B-GP] GPU backend = {backend}")
                    break
            except Exception:
                continue
        else:
            scene.cycles.device = "CPU"
    except Exception:
        scene.cycles.device = "CPU"

    # 配置 View Layer passes
    vl = scene.view_layers[0]
    vl.use_pass_combined = True
    vl.use_pass_z = True               # Depth pass
    vl.use_pass_normal = True          # Normal pass（view space, 见 brdf_postprocess 注释）
    vl.use_pass_object_index = True    # IndexOB pass：区分三部件

    # 添加 Backfacing AOV pass（精确背面遮罩）
    aov = vl.aovs.add()
    aov.name = "Backfacing"

    # 世界背景纯黑
    world = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        bg.inputs[1].default_value = 0.0


def apply_attitude(sat_root, yaw, pitch, roll=0.0):
    R4 = euler_to_matrix4(yaw, pitch, roll)
    S  = Matrix.Diagonal((UNIT_SCALE, UNIT_SCALE, UNIT_SCALE, 1.0))
    sat_root.matrix_world = R4 @ S


# ============================================================
# 4. 合成器：每姿态输出 1 个 MultiLayer EXR
#    层：Combined / Normal / Depth / IndexOB
# ============================================================
def setup_compositor_for_passes(scene):
    """
    Blender 4.2 LTS Compositor：
      - scene.use_nodes = True 后用 scene.node_tree
      - OUTPUT_FILE 节点 file_format=OPEN_EXR_MULTILAYER 时：
          * layer_slots 是 EXR 内部的层（每层一个输入 socket）
          * base_path + layer_slots[0].path + frame:04d + .exr 决定输出文件
    """
    scene.use_nodes = True
    nt = scene.node_tree
    nt.nodes.clear()
    nt.links.clear()

    rl = nt.nodes.new("CompositorNodeRLayers")
    rl.location = (0, 0)

    fo = nt.nodes.new("CompositorNodeOutputFile")
    fo.location = (400, 0)
    fo.format.file_format = "OPEN_EXR_MULTILAYER"
    fo.format.color_mode = "RGB"
    fo.format.color_depth = "32"
    fo.format.exr_codec = "ZIP"

    # MULTILAYER 模式：先清空默认的 1 个 layer_slot，再按名称新建
    # （remove 接受 NodeSocket，即 fo.inputs[i]）
    while len(fo.inputs) > 0:
        fo.layer_slots.remove(fo.inputs[0])

    fo.layer_slots.new("Combined")
    fo.layer_slots.new("Normal")
    fo.layer_slots.new("Depth")
    fo.layer_slots.new("IndexOB")
    fo.layer_slots.new("Backfacing")

    nt.links.new(rl.outputs["Image"],    fo.inputs["Combined"])
    nt.links.new(rl.outputs["Normal"],   fo.inputs["Normal"])
    nt.links.new(rl.outputs["Depth"],    fo.inputs["Depth"])
    nt.links.new(rl.outputs["IndexOB"],  fo.inputs["IndexOB"])
    nt.links.new(rl.outputs["Backfacing"], fo.inputs["Backfacing"])
    return fo


def render_and_save_passes(scene, out_prefix, fo_node):
    """渲染一次，合成器输出单个 MultiLayer EXR 文件。

    Blender 4.2 LTS MULTILAYER 行为：
      - 文件名 = base_path（按字符串拼接） + frame:04d + '.exr'
      - layer_slots[i].name 决定 EXR 内部层名（不影响文件名）
      - file_slots / layer_slots[0].path 在 MULTILAYER 下被忽略

    所以把 base_path 设为 "<out_dir>/<prefix>_"，渲染得 "<out_dir>/<prefix>_0001.exr"
    """
    out_prefix_s = str(out_prefix)
    fo_node.base_path = f"{out_prefix_s}_"

    # 触发渲染管线
    parent = Path(out_prefix).parent
    scene.render.filepath = str(parent / "_render_dummy_")
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGB"
    scene.frame_current = 1

    bpy.ops.render.render(write_still=False)
    base = Path(out_prefix).name
    print(f"[B-GP] {base}: 写入 {out_prefix_s}_0001.exr")


# ============================================================
# 5. 主流程
# ============================================================
def main():
    args = parse_args()
    t_start = time.perf_counter()

    scan_json = args.scan_json or find_latest_scan_json()
    print(f"[B-GP] scan_json = {scan_json}")
    with open(scan_json, "r", encoding="utf-8") as f:
        scan = json.load(f)

    sun_dir = scan.get("sun_direction") or SUN_FALLBACK
    det_dir = scan.get("det_direction") or DET_FALLBACK
    attitudes = scan["scan_data"]
    if args.limit and args.limit > 0:
        attitudes = attitudes[:args.limit]
    n_total = len(attitudes)
    print(f"[B-GP] 渲染 {n_total} 个姿态  res={args.res}  samples={args.samples}")

    # 防撞名
    fnames = [f"yaw{a['yaw']:06.2f}_pitch{a['pitch']:+06.2f}" for a in attitudes]
    assert len(set(fnames)) == n_total, "文件名碰撞"

    # 输出目录
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir or os.path.join(OUTPUT_ROOT, f"run_{run_id}_exact_brdf")
    out_dir = os.path.abspath(out_dir)  # 防 Blender Compositor 相对路径解析到 C:\
    os.makedirs(out_dir, exist_ok=True)
    print(f"[B-GP] out_dir = {out_dir}")

    # 场景初始化
    clear_scene()
    sat_root = import_stls_under_parent()
    setup_sun(sun_dir)
    r_max = compute_bbox_radius(sat_root)
    print(f"[B-GP] sat bbox r_max = {r_max:.4f} m")
    setup_camera(det_dir, r_max)
    scene = bpy.context.scene
    setup_render_passes(scene, args.res, args.samples)
    fo_node = setup_compositor_for_passes(scene)

    # CSV
    csv_path = os.path.join(out_dir, "render_log.csv")
    csv_f = open(csv_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(csv_f)
    writer.writerow([
        "idx", "yaw", "pitch", "roll",
        "sun_x", "sun_y", "sun_z",
        "det_x", "det_y", "det_z",
        "out_prefix", "render_sec",
    ])

    # 渲染循环
    sun_n = Vector(sun_dir).normalized()
    det_n = Vector(det_dir).normalized()

    for i, att in enumerate(attitudes):
        yaw   = float(att["yaw"])
        pitch = float(att["pitch"])
        roll  = float(att.get("roll", 0.0))
        fname_base = fnames[i]
        out_prefix = os.path.join(out_dir, fname_base)

        t0 = time.perf_counter()
        apply_attitude(sat_root, yaw, pitch, roll)

        # 渲染并保存 Combined/Normal/Depth passes
        render_and_save_passes(scene, out_prefix, fo_node)
        dt = time.perf_counter() - t0

        writer.writerow([
            i, yaw, pitch, roll,
            sun_n.x, sun_n.y, sun_n.z,
            det_n.x, det_n.y, det_n.z,
            fname_base, f"{dt:.3f}",
        ])
        csv_f.flush()

        if i % 10 == 0 or i == n_total - 1:
            print(f"[B-GP] {i+1}/{n_total}  yaw={yaw:7.2f}  pitch={pitch:+7.2f}  {dt:.2f}s")
            sys.stdout.flush()

    csv_f.close()

    # 保存元数据
    cfg = {
        "scan_json":       scan_json,
        "out_dir":         out_dir,
        "n_rendered":      n_total,
        "resolution":      args.res,
        "samples":         args.samples,
        "sun_direction":   list(sun_n),
        "det_direction":   list(det_n),
        "unit_scale":      UNIT_SCALE,
        "sat_bbox_r_max":  r_max,
        "blender_version": bpy.app.version_string,
        "materials":       MATERIALS,
        "passes":          ["Normal", "Depth"],
        "mode":            "exact_brdf_geometry_passes",
        "note":            "Normal/Depth EXR passes for Python post-processing BRDF computation",
        "elapsed_sec":     time.perf_counter() - t_start,
    }
    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

    # 写 post-process 需要的 metadata JSON
    meta = {
        "sun_direction":   list(sun_n),
        "det_direction":   list(det_n),
        "materials":        MATERIALS,
        "scan_json":        scan_json,
        "r_max":            r_max,
        "resolution":       args.res,
    }
    meta_path = os.path.join(out_dir, "render_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    elapsed = time.perf_counter() - t_start
    print(f"[B-GP] DONE  {n_total} frames  total {elapsed:.1f}s ({elapsed/max(n_total,1):.2f}s/frame)")
    print(f"[B-GP] out_dir: {out_dir}")
    print(f"[B-GP] meta:    {meta_path}")
    print(f"[B-GP] 下一步: python brdf_postprocess.py {out_dir}")


if __name__ == "__main__":
    main()

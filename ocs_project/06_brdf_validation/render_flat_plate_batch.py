# -*- coding: utf-8 -*-
"""
render_flat_plate_batch.py —— Blender headless 单平板多姿态批量渲染
=====================================================================
在一个 Blender 进程内循环渲染 5 个姿态，每个输出 MULTILAYER EXR
（Combined / Normal / Depth / IndexOB），供后处理做三端闭合对比。

用法:
    "D:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python render_flat_plate_batch.py -- --out-dir <dir>
"""
import bpy
import os, sys, json, math, argparse, time
from mathutils import Matrix, Vector
from pathlib import Path


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default=None,
                   help="输出目录，默认 结果/BRDF验证/plane_batch_YYYYMMDD_HHMMSS/")
    p.add_argument("--res", type=int, default=128)
    p.add_argument("--stl", default=r"D:\我的文件\研究生学术\光学项目\0506新\建模\flat_plate_1m2.stl")
    return p.parse_args(argv)


def euler_to_matrix4(yaw, pitch, roll=0.0):
    """Z-Y-X 内旋，返回 Matrix 4x4"""
    y, p, r = math.radians(yaw), math.radians(pitch), math.radians(roll)
    Rz = Matrix(((math.cos(y), -math.sin(y), 0, 0),
                  (math.sin(y),  math.cos(y), 0, 0),
                  (0,            0,           1, 0),
                  (0,            0,           0, 1)))
    Ry = Matrix(((math.cos(p),  0, math.sin(p), 0),
                  (0,           1, 0,           0),
                  (-math.sin(p), 0, math.cos(p), 0),
                  (0,            0, 0,           1)))
    Rx = Matrix(((1, 0,           0,            0),
                  (0, math.cos(r), -math.sin(r), 0),
                  (0, math.sin(r),  math.cos(r), 0),
                  (0, 0,           0,            1)))
    return Rz @ Ry @ Rx


def main():
    args = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)

    UNIT_SCALE = 1e-3  # mm → m
    res = args.res

    # 输出目录
    run_id = time.strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir or os.path.join(
        r"D:\我的文件\研究生学术\光学项目\0506新\结果\BRDF验证",
        f"plane_batch_{run_id}")
    os.makedirs(out_dir, exist_ok=True)

    # 太阳与探测器方向
    sun_vec = Vector((1.0, 0.0, 0.3)).normalized()
    det_vec = Vector((0.5, -1.0, 0.1)).normalized()

    # ---- 导入 STL ----
    bpy.ops.wm.stl_import(filepath=args.stl)
    obj = bpy.context.active_object
    obj.name = "FlatPlate"
    obj.pass_index = 1

    # bbox 包围球半径
    bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    r_max_m = max((v.x**2 + v.y**2 + v.z**2)**0.5 for v in bbox) * UNIT_SCALE
    print(f"  r_max = {r_max_m:.4f} m  ortho_scale = {2.2*r_max_m:.4f} m")

    # ---- 材质 (jinshuzhuti: rho_d=0.20, rho_s=0.60, n=80) ----
    mat = bpy.data.materials.new("FlatPlateMat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.156
    bsdf.inputs["Metallic"].default_value = 0.0
    out_node = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    obj.data.materials.append(mat)

    # ---- 场景 ----
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.get_devices()
        for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
            try:
                prefs.compute_device_type = backend
                if any(d.use for d in prefs.devices):
                    scene.cycles.device = "GPU"
                    break
            except Exception:
                continue
    except Exception:
        pass

    scene.cycles.samples = 1
    scene.cycles.use_denoising = False
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Raw"
    scene.view_settings.look = "None"

    # ---- 相机（正交） ----
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.2 * r_max_m
    cam_obj = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_pos = det_vec * (5.0 * r_max_m)
    cam_obj.location = cam_pos
    cam_obj.rotation_euler = det_vec.to_track_quat('Z', 'Y').to_euler()
    scene.camera = cam_obj

    # ---- 太阳灯 ----
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 5.0
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = sun_vec.to_track_quat('Z', 'Y').to_euler()

    # ---- View Layer passes ----
    vl = scene.view_layers[0]
    vl.use_pass_combined = True
    vl.use_pass_z = True
    vl.use_pass_normal = True
    vl.use_pass_object_index = True
    aov = vl.aovs.add()
    aov.name = "Backfacing"

    # ---- Compositor: MULTILAYER EXR ----
    scene.use_nodes = True
    nt = scene.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    rl.location = (0, 0)
    fo = nt.nodes.new("CompositorNodeOutputFile")
    fo.format.file_format = "OPEN_EXR_MULTILAYER"
    fo.format.color_depth = "32"
    fo.format.exr_codec = "ZIP"
    while len(fo.inputs) > 0:
        fo.layer_slots.remove(fo.inputs[0])
    fo.layer_slots.new("Combined")
    fo.layer_slots.new("Normal")
    fo.layer_slots.new("Depth")
    fo.layer_slots.new("IndexOB")
    nt.links.new(rl.outputs["Image"],   fo.inputs["Combined"])
    nt.links.new(rl.outputs["Normal"],  fo.inputs["Normal"])
    nt.links.new(rl.outputs["Depth"],   fo.inputs["Depth"])
    nt.links.new(rl.outputs["IndexOB"], fo.inputs["IndexOB"])

    # ---- 姿态列表 ----
    attitudes = [
        (0.0, 0.0),
        (0.0, -30.0),
        (90.0, -45.0),
        (150.0, -80.0),
        (180.0, 0.0),
    ]
    scale_mm_to_m = Matrix.Diagonal((UNIT_SCALE, UNIT_SCALE, UNIT_SCALE, 1.0))

    # 渲染循环
    t_start = time.time()
    for i, (yaw, pitch) in enumerate(attitudes):
        R_mat = euler_to_matrix4(yaw, pitch, 0.0)
        obj.matrix_world = R_mat @ scale_mm_to_m

        fname = f"yaw{yaw:06.2f}_pitch{pitch:+06.2f}"
        fo.base_path = os.path.join(out_dir, fname + "_")

        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        print(f"  [{i+1}/5] yaw={yaw:7.1f} pitch={pitch:+7.1f}  {dt:.2f}s")
        sys.stdout.flush()

    elapsed = time.time() - t_start
    print(f"  total: {elapsed:.1f}s ({elapsed/5:.2f}s/frame)")

    # ---- 写 metadata ----
    meta = {
        "type": "flat_plate_batch",
        "attitudes": [{"yaw": y, "pitch": p} for y, p in attitudes],
        "sun_direction": list(sun_vec),
        "det_direction": list(det_vec),
        "resolution": res,
        "r_max": r_max_m,
        "ortho_scale": 2.2 * r_max_m,
        "materials": {"flat_plate": {"rho_d": 0.20, "rho_s": 0.60, "n": 80,
                                      "brdf_model": "legacy_phong"}},
    }
    with open(os.path.join(out_dir, "render_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"  输出: {out_dir}")


if __name__ == "__main__":
    main()

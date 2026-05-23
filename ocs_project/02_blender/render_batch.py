# -*- coding: utf-8 -*-
"""
render_batch.py —— 模块 B · Blender Headless 批量渲染（MVP）
==============================================================
读取模块 A 的 ocs_scan.json，对每个 (yaw, pitch) 姿态用 Blender 5.0 headless
渲染一张图像，输出到 结果/模块B_渲染/run_YYYYMMDD_HHMMSS/ 下。

使用方式（Windows，--分隔符必需）：
    blender.exe --background --python render_batch.py -- --limit 5 --res 256

LIMITATIONS (MVP):
1. BRDF 是近似：Principled BSDF roughness ~ sqrt(2/(n+2))；非 ocs_core.py
   Phong 的像素级镜像。精确匹配需写 OSL shader 复现 f_r = rho_d/π + rho_s*(n·h)^n。
2. 所有部件 Metallic=0，含金属主体——后续应对 jinshuzhuti 设 Metallic=1
   并调铝反射率。
3. Color management = Standard，输出近似线性但未经辐射度量定标。
4. 无大气、无地球反照、无杂散光。背景纯黑。
5. 自遮挡由 Cycles 物理光追处理；ocs_core.py 内"同部件排除"逻辑未镜像。
6. UNIT_SCALE 通过 parent transform 应用，不 bake；children 局部空间仍是 mm。
7. 相机正交——适合远场探测器；要做真实望远镜 FoV 时改 PERSP。
8. EEVEE 仅作速度选项，不正确遵守 BRDF；CYCLES 是默认。
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

try:
    import bpy
    import mathutils
    from mathutils import Vector, Matrix
except ImportError:
    print("[FAIL] bpy 不可用 —— 请用 blender.exe --background --python 运行本脚本。")
    sys.exit(1)


# ============================================================
# 常量（与 ocs_project/01_code/config.py 保持一致）
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

UNIT_SCALE = 1e-3  # mm → m

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
    p = argparse.ArgumentParser(description="Module B batch renderer")
    p.add_argument("--scan-json", default=None,
                   help="ocs_scan.json 路径，默认自动找最新")
    p.add_argument("--out-dir",   default=None,
                   help="输出根目录，默认 结果/模块B_渲染/run_YYYYMMDD_HHMMSS/")
    p.add_argument("--limit",     type=int, default=0,
                   help="只渲染前 N 个姿态；0 表示全部")
    p.add_argument("--res",       type=int, default=256,
                   help="渲染分辨率（正方形）")
    p.add_argument("--samples",   type=int, default=16,
                   help="Cycles 采样数")
    p.add_argument("--engine",    default="CYCLES",
                   choices=["CYCLES", "BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"],
                   help="渲染引擎")
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
    # 清材质/网格残留
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(block):
            block.remove(item)


def import_one_stl(filepath):
    """Blender 5.0 用 wm.stl_import；4.x 回退 import_mesh.stl。"""
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


def make_principled_material(name, rho_d, rho_s, n):
    mat = bpy.data.materials.new(name=f"mat_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        return mat
    base = max(0.0, min(1.0, float(rho_d)))
    bsdf.inputs["Base Color"].default_value = (base, base, base, 1.0)
    rough = math.sqrt(2.0 / (n + 2.0))
    rough = max(0.02, min(1.0, rough))
    bsdf.inputs["Roughness"].default_value = rough
    spec_key = "Specular IOR Level" if "Specular IOR Level" in bsdf.inputs else "Specular"
    if spec_key in bsdf.inputs:
        bsdf.inputs[spec_key].default_value = max(0.0, min(1.0, float(rho_s)))
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def import_stls_under_parent():
    sat_root = bpy.data.objects.new("Sat_Root", None)
    bpy.context.collection.objects.link(sat_root)
    for part_name, path in PART_FILES.items():
        if not os.path.isfile(path):
            raise FileNotFoundError(f"STL 不存在: {path}")
        obj = import_one_stl(path)
        obj.name = part_name
        obj.parent = sat_root
        # 材质
        m = MATERIALS.get(part_name, {"rho_d": 0.2, "rho_s": 0.3, "n": 30})
        mat = make_principled_material(part_name, m["rho_d"], m["rho_s"], m["n"])
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    # mm → m 通过 parent scale 实现（不 apply，便于 matrix_world 直接复合）
    sat_root.scale = (UNIT_SCALE, UNIT_SCALE, UNIT_SCALE)
    return sat_root


def compute_bbox_radius(sat_root):
    """旋转不变量：identity 姿态下计算最大半径（米）。"""
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
        r_max = 1.0  # 兜底
    return r_max


def setup_camera(det_vec_I, r_max):
    det = Vector(det_vec_I).normalized()
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.2 * r_max
    cam = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = det * (5.0 * r_max)
    # 朝向原点：相机 -Z 轴指向 -det
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
    # 光线方向是物体局部 -Z；想让光从 +sun_dir 来 → 物体 +Z 与 +sun_dir 对齐
    sun.rotation_mode = "QUATERNION"
    sun.rotation_quaternion = sun_dir.to_track_quat('Z', 'Y')
    return sun


def setup_render(scene, res, engine, samples):
    scene.render.engine = engine
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"

    if engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            prefs.get_devices()
            for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
                try:
                    prefs.compute_device_type = backend
                    if any(d.use for d in prefs.devices):
                        scene.cycles.device = "GPU"
                        print(f"[B] GPU backend = {backend}")
                        break
                except Exception:
                    continue
            else:
                scene.cycles.device = "CPU"
        except Exception:
            scene.cycles.device = "CPU"
    # 世界背景纯黑
    world = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
        bg.inputs[1].default_value = 0.0


# ============================================================
# 4. 姿态 + 渲染
# ============================================================
def apply_attitude(sat_root, yaw, pitch, roll=0.0):
    R4 = euler_to_matrix4(yaw, pitch, roll)
    S  = Matrix.Diagonal((UNIT_SCALE, UNIT_SCALE, UNIT_SCALE, 1.0))
    sat_root.matrix_world = R4 @ S


def render_one(scene, out_path_no_ext):
    scene.render.filepath = out_path_no_ext
    bpy.ops.render.render(write_still=True)


# ============================================================
# 5. 主流程
# ============================================================
def main():
    args = parse_args()
    t_start = time.perf_counter()

    scan_json = args.scan_json or find_latest_scan_json()
    print(f"[B] scan_json = {scan_json}")
    with open(scan_json, "r", encoding="utf-8") as f:
        scan = json.load(f)

    sun_dir = scan.get("sun_direction") or SUN_FALLBACK
    det_dir = scan.get("det_direction") or DET_FALLBACK
    attitudes = scan["scan_data"]
    if args.limit and args.limit > 0:
        attitudes = attitudes[:args.limit]
    n_total = len(attitudes)
    print(f"[B] 渲染 {n_total} 个姿态  res={args.res}  engine={args.engine}  samples={args.samples}")

    # 防撞名
    fnames = [f"yaw{a['yaw']:06.2f}_pitch{a['pitch']:+06.2f}.png" for a in attitudes]
    assert len(set(fnames)) == n_total, "文件名碰撞，检查姿态唯一性"

    # 输出目录
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir or os.path.join(OUTPUT_ROOT, f"run_{run_id}")
    img_dir = os.path.join(out_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    print(f"[B] out_dir = {out_dir}")

    # 场景
    clear_scene()
    sat_root = import_stls_under_parent()
    setup_sun(sun_dir)
    r_max = compute_bbox_radius(sat_root)
    print(f"[B] sat bbox r_max = {r_max:.4f} m")
    setup_camera(det_dir, r_max)
    setup_render(bpy.context.scene, args.res, args.engine, args.samples)

    # CSV
    csv_path = os.path.join(out_dir, "render_log.csv")
    csv_f = open(csv_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(csv_f)
    writer.writerow([
        "idx", "yaw", "pitch", "roll",
        "sun_x", "sun_y", "sun_z",
        "det_x", "det_y", "det_z",
        "filename", "render_sec",
    ])

    # 渲染循环
    sun_n = Vector(sun_dir).normalized()
    det_n = Vector(det_dir).normalized()
    for i, att in enumerate(attitudes):
        yaw   = float(att["yaw"])
        pitch = float(att["pitch"])
        roll  = float(att.get("roll", 0.0))
        fname = fnames[i]
        out_no_ext = os.path.join(img_dir, fname[:-4])

        t0 = time.perf_counter()
        apply_attitude(sat_root, yaw, pitch, roll)
        render_one(bpy.context.scene, out_no_ext)
        dt = time.perf_counter() - t0

        writer.writerow([
            i, yaw, pitch, roll,
            sun_n.x, sun_n.y, sun_n.z,
            det_n.x, det_n.y, det_n.z,
            fname, f"{dt:.3f}",
        ])
        csv_f.flush()

        if i % 10 == 0 or i == n_total - 1:
            print(f"[B] {i+1}/{n_total}  yaw={yaw:7.2f}  pitch={pitch:+7.2f}  {dt:.2f}s")
            sys.stdout.flush()

    csv_f.close()

    # 配置快照
    cfg = {
        "scan_json":       scan_json,
        "out_dir":         out_dir,
        "n_rendered":      n_total,
        "resolution":      args.res,
        "engine":          args.engine,
        "samples":         args.samples,
        "sun_direction":   list(sun_n),
        "det_direction":   list(det_n),
        "unit_scale":      UNIT_SCALE,
        "sat_bbox_r_max":  r_max,
        "blender_version": bpy.app.version_string,
        "materials":       MATERIALS,
        "brdf_note":       "Phong→Principled approximation: roughness=sqrt(2/(n+2)), specular_ior_level=rho_s, metallic=0.",
        "elapsed_sec":     time.perf_counter() - t_start,
    }
    with open(os.path.join(out_dir, "config_used.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

    elapsed = time.perf_counter() - t_start
    print(f"[B] DONE  {n_total} frames  total {elapsed:.1f}s ({elapsed/max(n_total,1):.2f}s/frame)")
    print(f"[B] images: {img_dir}")
    print(f"[B] log:    {csv_path}")


if __name__ == "__main__":
    main()

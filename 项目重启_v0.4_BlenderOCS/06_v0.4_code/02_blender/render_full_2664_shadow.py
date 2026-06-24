# -*- coding: utf-8 -*-
"""
render_full_2664_shadow.py —— 全量 2664 姿态 shadow pass 渲染 driver
======================================================================
任务：为 72 yaw × 37 pitch = 2664 姿态生成 camera-view 和 sun-view geometry passes。

使用方式：
    # 全量 2664（不在此阶段执行）
    blender --background --python render_full_2664_shadow.py

    # Smoke 测试（仅渲染前 N 个姿态）
    blender --background --python render_full_2664_shadow.py -- --smoke 3

    # 指定姿态列表（逗号分隔 label）
    blender --background --python render_full_2664_shadow.py -- --labels yaw010_pitch+000_roll+000,yaw225_pitch+000_roll+000

    # 分批（start-index + count）
    blender --background --python render_full_2664_shadow.py -- --start-index 0 --count 200

    # 分批（batch-index + batch-size）
    blender --background --python render_full_2664_shadow.py -- --batch-index 0 --batch-size 200

    # 强制重渲染（覆盖已存在文件）
    blender --background --python render_full_2664_shadow.py -- --labels yaw010_pitch+000_roll+000 --force

    # 不跳过已存在文件（默认会跳过）
    blender --background --python render_full_2664_shadow.py -- --no-skip-existing

输出（每个姿态）：
    Camera-view: {label}_camera.exr（MULTILAYER: Normal, Depth, IndexOB, Position）
    Sun-view:   {label}_sun.exr（MULTILAYER: Depth, Position）
    矩阵日志:   camera_matrices_blender.json（首次运行时记录）
    渲染元数据: render_metadata.json（含每姿态状态）

边界：
    - 默认跳过已存在完整 pair 的姿态（SKIPPED_EXISTING）
    - 部分存在时标记 PARTIAL_EXISTING，除非 --force 否则不覆盖
    - 不在此阶段执行全量 2664
    - 不训练模型
"""

import os
import sys
import json
import math
import traceback
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
# 1. 配置
# ============================================================
PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
V04_PROJECT = os.path.join(PROJECT_ROOT, "项目重启_v0.4_BlenderOCS")
STL_DIR = os.path.join(PROJECT_ROOT, "建模", "真实模型")
OUTPUT_DIR = os.path.join(V04_PROJECT, "v0.4_results", "01_fullrun", "shadow_passes")

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

UNIT_SCALE = 1e-3
SUN_VECTOR = [1.0, 0.0, 0.3]
DET_VECTOR = [0.5, -1.0, 0.1]
RESOLUTION = 256
SAMPLES = 1


# ============================================================
# 2. 全量姿态网格生成
# ============================================================
def generate_full_attitude_list():
    """生成 72 yaw × 37 pitch = 2664 全量姿态列表"""
    attitudes = []
    for yaw in range(0, 360, 5):       # 0, 5, 10, ..., 355
        for pitch in range(-90, 91, 5):  # -90, -85, ..., 85, 90
            label = f"yaw{yaw:03d}_pitch{pitch:+04d}_roll+000"
            attitudes.append({"yaw": yaw, "pitch": pitch, "roll": 0, "label": label})
    return attitudes


# ============================================================
# 3. 文件存在性检查
# ============================================================
def check_existing_files(label, output_dir):
    """检查某个姿态的输出文件是否存在。

    返回:
        "COMPLETE": camera.exr 和 sun.exr 均存在
        "PARTIAL": 只有一侧存在
        "MISSING": 两侧均不存在
    """
    camera_path = os.path.join(output_dir, f"{label}_camera.exr")
    sun_path = os.path.join(output_dir, f"{label}_sun.exr")

    camera_exists = os.path.isfile(camera_path)
    sun_exists = os.path.isfile(sun_path)

    if camera_exists and sun_exists:
        return "COMPLETE"
    elif camera_exists or sun_exists:
        return "PARTIAL"
    else:
        return "MISSING"


# ============================================================
# 4. 场景搭建（复用 render_20_attitudes_shadow.py）
# ============================================================
def euler_to_matrix4(yaw_deg, pitch_deg, roll_deg=0.0):
    y = math.radians(yaw_deg)
    p = math.radians(pitch_deg)
    r = math.radians(roll_deg)
    cy, sy = math.cos(y), math.sin(y)
    cp, sp = math.cos(p), math.sin(p)
    cr, sr = math.cos(r), math.sin(r)
    Rz = Matrix(((cy, -sy, 0.0, 0.0), (sy, cy, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)))
    Ry = Matrix(((cp, 0.0, sp, 0.0), (0.0, 1.0, 0.0, 0.0), (-sp, 0.0, cp, 0.0), (0.0, 0.0, 0.0, 1.0)))
    Rx = Matrix(((1.0, 0.0, 0.0, 0.0), (0.0, cr, -sr, 0.0), (0.0, sr, cr, 0.0), (0.0, 0.0, 0.0, 1.0)))
    return Rz @ Ry @ Rx


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images):
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
    sun_dir = Vector(sun_vec).normalized()
    light_data = bpy.data.lights.new("Sun", type="SUN")
    light_data.energy = 5.0
    light_data.angle = math.radians(0.5)
    sun = bpy.data.objects.new("Sun", light_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_mode = "QUATERNION"
    sun.rotation_quaternion = sun_dir.to_track_quat('Z', 'Y')
    return sun


def setup_render_passes(scene, enable_normal=True, enable_indexob=True):
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = RESOLUTION
    scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.view_settings.view_transform = "Raw"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = False
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
    vl = scene.view_layers[0]
    vl.use_pass_combined = True
    vl.use_pass_normal = enable_normal
    vl.use_pass_z = True
    vl.use_pass_object_index = enable_indexob
    vl.use_pass_position = True


def apply_attitude(sat_root, yaw, pitch, roll):
    R = euler_to_matrix4(yaw, pitch, roll)
    S = Matrix.Scale(UNIT_SCALE, 4)
    sat_root.matrix_world = R @ S


def render_one_view(scene, sat_root, attitude, output_dir, view_type, camera):
    label = attitude["label"]
    yaw = attitude["yaw"]
    pitch = attitude["pitch"]
    roll = attitude["roll"]
    print(f"\n  [{view_type}] {label}  yaw={yaw} pitch={pitch}")
    apply_attitude(sat_root, yaw, pitch, roll)
    bpy.context.view_layer.update()
    scene.camera = camera
    output_path = os.path.join(output_dir, f"{label}_{view_type}")
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f"    输出: {output_path}.exr")
    return output_path + ".exr"


def log_camera_matrices(camera_cam, sun_cam, output_dir):
    """记录相机矩阵到 JSON"""
    def mat_to_list(mat):
        return [[float(mat[i][j]) for j in range(4)] for i in range(4)]

    bpy.context.view_layer.update()
    output = {
        "timestamp": datetime.now().isoformat(),
        "task": "1C-E17 full-run driver camera matrix logging",
        "camera_matrix_world": mat_to_list(camera_cam.matrix_world),
        "sun_camera_matrix_world": mat_to_list(sun_cam.matrix_world),
        "source": "Camera_Detector.matrix_world / Camera_Sun.matrix_world",
    }
    path = os.path.join(output_dir, "camera_matrices_blender.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n相机矩阵日志: {path}")
    return path


# ============================================================
# 5. CLI 参数解析（Blender -- 之后的部分）
# ============================================================
def parse_cli():
    """解析 Blender 的 -- 之后参数

    返回 dict:
        smoke_n: int or None
        labels: list or None
        start_index: int or None
        count: int or None
        batch_index: int or None
        batch_size: int or None
        skip_existing: bool (default True)
        force: bool (default False)
    """
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    params = {
        "smoke_n": None,
        "labels": None,
        "start_index": None,
        "count": None,
        "batch_index": None,
        "batch_size": None,
        "skip_existing": True,   # 默认跳过已存在完整 pair
        "force": False,
    }

    i = 0
    while i < len(argv):
        if argv[i] == "--smoke":
            params["smoke_n"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--labels":
            params["labels"] = [l.strip() for l in argv[i + 1].split(",")]
            i += 2
        elif argv[i] == "--start-index":
            params["start_index"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--count":
            params["count"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--batch-index":
            params["batch_index"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--batch-size":
            params["batch_size"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--force":
            params["force"] = True
            params["skip_existing"] = False
            i += 1
        elif argv[i] == "--no-skip-existing":
            params["skip_existing"] = False
            i += 1
        else:
            i += 1

    return params


# ============================================================
# 6. 姿态选择逻辑
# ============================================================
def select_attitudes(all_attitudes, params):
    """根据 CLI 参数从全量姿态网格中选择本次渲染姿态。

    返回:
        (selected, selection_mode, selection_detail)
    """
    selection_mode = "full"
    selection_detail = {}

    if params["labels"]:
        # 指定姿态列表
        selection_mode = "labels"
        labels_lower = [l.lower() for l in params["labels"]]
        selected = [a for a in all_attitudes if a["label"].lower() in labels_lower]
        selection_detail["requested_labels"] = params["labels"]
        selection_detail["matched_count"] = len(selected)
    elif params["smoke_n"] is not None:
        # Smoke 模式：取前 N 个
        selection_mode = "smoke"
        selected = all_attitudes[:params["smoke_n"]]
        selection_detail["smoke_n"] = params["smoke_n"]
    elif params["start_index"] is not None and params["count"] is not None:
        # start-index + count 分批
        selection_mode = "start_index_count"
        start = params["start_index"]
        cnt = params["count"]
        selected = all_attitudes[start:start + cnt]
        selection_detail["start_index"] = start
        selection_detail["count"] = cnt
        selection_detail["end_index"] = start + cnt - 1
    elif params["batch_index"] is not None and params["batch_size"] is not None:
        # batch-index + batch-size 分批
        selection_mode = "batch_index_size"
        bi = params["batch_index"]
        bs = params["batch_size"]
        start = bi * bs
        selected = all_attitudes[start:start + bs]
        selection_detail["batch_index"] = bi
        selection_detail["batch_size"] = bs
        selection_detail["start_index"] = start
        selection_detail["end_index"] = start + len(selected) - 1
    else:
        # 全量模式
        selection_mode = "full"
        selected = all_attitudes

    selection_detail["total_grid_size"] = len(all_attitudes)
    selection_detail["selected_count"] = len(selected)
    selection_detail["selection_mode"] = selection_mode

    return selected, selection_mode, selection_detail


# ============================================================
# 7. 主流程
# ============================================================
def main():
    params = parse_cli()

    print("=" * 80)
    print("全量 2664 姿态 shadow pass 渲染 driver")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"输出目录: {OUTPUT_DIR}")

    # 场景搭建
    print("\n清空场景...")
    clear_scene()
    sat_root = import_stls()
    r_max = compute_bbox_radius(sat_root)
    print(f"\n边界框半径: {r_max:.6f} m")

    print("\n设置相机...")
    camera_cam = setup_camera(DET_VECTOR, r_max, name="Camera_Detector")
    sun_cam = setup_camera(SUN_VECTOR, r_max, name="Camera_Sun")
    setup_sun(SUN_VECTOR)

    # 记录相机矩阵（仅在首次或不存在时写入）
    matrix_log_path = os.path.join(OUTPUT_DIR, "camera_matrices_blender.json")
    if params["force"] or not os.path.isfile(matrix_log_path):
        log_camera_matrices(camera_cam, sun_cam, OUTPUT_DIR)
    else:
        print(f"\n相机矩阵日志已存在，跳过: {matrix_log_path}")

    scene = bpy.context.scene

    # 全量姿态列表
    all_attitudes = generate_full_attitude_list()
    print(f"\n全量姿态网格: {len(all_attitudes)} 个 (72 yaw × 37 pitch)")

    # 确定本次渲染的姿态
    selected, selection_mode, selection_detail = select_attitudes(all_attitudes, params)

    if not selected:
        print("[ERROR] 没有匹配的姿态")
        return 1

    print(f"\n选择模式: {selection_mode}")
    for k, v in selection_detail.items():
        print(f"  {k}: {v}")
    print(f"skip_existing: {params['skip_existing']}")
    print(f"force: {params['force']}")

    print("\n姿态列表:")
    for a in selected:
        print(f"  {a['label']}")

    # ---- 预扫描：检查已存在文件 ----
    print("\n" + "=" * 80)
    print("预扫描：检查已存在产物")
    print("=" * 80)

    to_render = []
    skipped = []
    partial = []

    for attitude in selected:
        label = attitude["label"]
        status = check_existing_files(label, OUTPUT_DIR)

        if status == "COMPLETE" and params["skip_existing"]:
            skipped.append({"attitude": attitude, "reason": "SKIPPED_EXISTING"})
            print(f"  [SKIP] {label} — 已有完整 camera+sun pair")
        elif status == "PARTIAL" and not params["force"]:
            partial.append({"attitude": attitude, "reason": "PARTIAL_EXISTING"})
            print(f"  [PARTIAL] {label} — 仅一侧存在，需 --force 覆盖")
        else:
            if status == "COMPLETE" and not params["skip_existing"]:
                print(f"  [RENDER] {label} — 已存在但 skip_existing=False，将重渲染")
            elif status == "PARTIAL" and params["force"]:
                print(f"  [RENDER] {label} — 部分存在但 --force，将重渲染")
            else:
                print(f"  [RENDER] {label}")
            to_render.append(attitude)

    print(f"\n  RENDER: {len(to_render)} | SKIP: {len(skipped)} | PARTIAL: {len(partial)}")

    if not to_render and not params["force"]:
        print("\n[SAME-STATE] 所有选定姿态已有完整产物，无需渲染")

    # ---- 渲染 ----
    results = []

    # 跳过项直接加入 results（保持顺序与 selected 一致）
    for s in skipped:
        label = s["attitude"]["label"]
        results.append({
            "attitude": s["attitude"],
            "status": "SKIPPED_EXISTING",
            "camera_file": os.path.join(OUTPUT_DIR, f"{label}_camera.exr"),
            "sun_file": os.path.join(OUTPUT_DIR, f"{label}_sun.exr"),
            "camera_exists": True,
            "sun_exists": True,
        })

    # 部分存在项加入 results
    for p in partial:
        label = p["attitude"]["label"]
        cam_path = os.path.join(OUTPUT_DIR, f"{label}_camera.exr")
        sun_path = os.path.join(OUTPUT_DIR, f"{label}_sun.exr")
        results.append({
            "attitude": p["attitude"],
            "status": "PARTIAL_EXISTING",
            "camera_file": cam_path,
            "sun_file": sun_path,
            "camera_exists": os.path.isfile(cam_path),
            "sun_exists": os.path.isfile(sun_path),
        })

    if to_render:
        print("\n" + "=" * 80)
        print(f"开始渲染 {len(to_render)} 个姿态")
        print("=" * 80)

    for i, attitude in enumerate(to_render, 1):
        label = attitude["label"]
        print(f"\n[{i}/{len(to_render)}] {label}")

        try:
            setup_render_passes(scene, enable_normal=True, enable_indexob=True)
            camera_file = render_one_view(scene, sat_root, attitude, OUTPUT_DIR, "camera", camera_cam)

            setup_render_passes(scene, enable_normal=False, enable_indexob=False)
            sun_file = render_one_view(scene, sat_root, attitude, OUTPUT_DIR, "sun", sun_cam)

            cam_ok = os.path.isfile(camera_file)
            sun_ok = os.path.isfile(sun_file)

            if cam_ok and sun_ok:
                status = "RENDERED"
            elif cam_ok or sun_ok:
                status = "PARTIAL_EXISTING"  # 渲染后仍不完整
            else:
                status = "FAILED"

            results.append({
                "attitude": attitude,
                "status": status,
                "camera_file": camera_file,
                "sun_file": sun_file,
                "camera_exists": cam_ok,
                "sun_exists": sun_ok,
            })
        except Exception as e:
            print(f"  [FAILED] {label}: {e}")
            traceback.print_exc()
            results.append({
                "attitude": attitude,
                "status": "FAILED",
                "camera_file": os.path.join(OUTPUT_DIR, f"{label}_camera.exr"),
                "sun_file": os.path.join(OUTPUT_DIR, f"{label}_sun.exr"),
                "camera_exists": False,
                "sun_exists": False,
                "error": str(e),
            })

    # ---- 统计 ----
    rendered_count = sum(1 for r in results if r["status"] == "RENDERED")
    skipped_count = sum(1 for r in results if r["status"] == "SKIPPED_EXISTING")
    partial_count = sum(1 for r in results if r["status"] == "PARTIAL_EXISTING")
    failed_count = sum(1 for r in results if r["status"] == "FAILED")

    # ---- 元数据 ----
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "task": "1C-E17-FIX01 full-run shadow render driver with startup protection",
        "resolution": RESOLUTION,
        "samples": SAMPLES,
        "sun_vector": SUN_VECTOR,
        "det_vector": DET_VECTOR,
        "r_max": r_max,
        "total_grid_size": len(all_attitudes),
        "selection_mode": selection_mode,
        "selection_detail": selection_detail,
        "skip_existing": params["skip_existing"],
        "force": params["force"],
        "selected_count": len(selected),
        "rendered_count": rendered_count,
        "skipped_count": skipped_count,
        "partial_count": partial_count,
        "failed_count": failed_count,
        "results": results,
    }

    metadata_file = os.path.join(OUTPUT_DIR, "render_metadata.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # ---- 终检 ----
    print("\n" + "=" * 80)
    print("渲染完成")
    print("=" * 80)
    print(f"  RENDERED:          {rendered_count}")
    print(f"  SKIPPED_EXISTING:  {skipped_count}")
    print(f"  PARTIAL_EXISTING:  {partial_count}")
    print(f"  FAILED:            {failed_count}")
    print()

    for r in results:
        status_mark = {
            "RENDERED": "[RENDERED]",
            "SKIPPED_EXISTING": "[SKIP]",
            "PARTIAL_EXISTING": "[PARTIAL]",
            "FAILED": "[FAIL]",
        }.get(r["status"], "[???]")
        c = "[OK]" if r["camera_exists"] else "[MISS]"
        s = "[OK]" if r["sun_exists"] else "[MISS]"
        print(f"  {status_mark} {c} camera | {s} sun | {r['attitude']['label']}")

    print(f"\n元数据: {metadata_file}")

    if failed_count == 0 and partial_count == 0:
        print(f"\n[SUCCESS] {rendered_count} rendered + {skipped_count} skipped = 全部完成")
        return 0
    elif failed_count > 0:
        print(f"\n[WARNING] {failed_count} 姿态渲染失败")
        return 1
    else:
        print(f"\n[WARNING] {partial_count} 姿态部分存在，需 --force 覆盖")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

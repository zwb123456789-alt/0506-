"""
Manual Occlusion Review Tool (Blender MVP).

Reads manual_review_candidates.csv, imports three STL parts, casts sun/det
rays with Blender scene.ray_cast, compares against the current algorithm's
sun_occluded/det_occluded, and writes overview PNG + .blend + CSV/MD report.

Run:
    blender --background --python manual_review_blender.py -- \
        --input  "...\manual_review_candidates.csv" \
        --model_dir "...\建模" \
        --outdir "...\结果\人工遮挡抽查" \
        --max_cases 3 --mhd_filter 1.0
"""
import argparse
import csv
import math
import os
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

PART_COLORS = {
    "jinshuzhuti":    (0.75, 0.75, 0.78, 0.50),
    "taiyangnengban": (0.10, 0.20, 0.65, 0.50),
    "yinshenban":     (0.20, 0.55, 0.25, 0.50),
}

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--model_dir", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--max_cases", type=int, default=30)
    p.add_argument("--mhd_filter", type=float, default=1.0)
    p.add_argument("--parts", default="jinshuzhuti,taiyangnengban,yinshenban")
    p.add_argument("--only_occluded", type=int, default=1,
                   help="1 = only rows where sun_occluded or det_occluded is True")
    p.add_argument("--self_hit_tol_mm", type=float, default=0.001)
    p.add_argument("--max_ray_dist_mm", type=float, default=10000.0)
    p.add_argument("--save_blend", type=int, default=1)
    p.add_argument("--render_png", type=int, default=1)
    p.add_argument("--render_width", type=int, default=1280)
    p.add_argument("--render_height", type=int, default=800)
    p.add_argument("--draw_labels", type=int, default=0,
                   help="Deprecated; labels are intentionally not drawn in PNG/.blend outputs")
    return p.parse_args(argv)


def str_to_bool(x):
    return str(x).strip().lower() in ("true", "1", "yes", "t")


def parse_vec_from_text(text):
    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(text))
    if len(nums) < 3:
        raise ValueError(f"cannot parse 3 floats from: {text!r}")
    return [float(nums[-3]), float(nums[-2]), float(nums[-1])]


def parse_yaw_pitch_roll(text):
    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(text))
    if len(nums) < 3:
        return (0.0, 0.0, 0.0)
    return (float(nums[0]), float(nums[1]), float(nums[2]))


def attitude_matrix(yaw_deg, pitch_deg, roll_deg):
    """R = Rz @ Ry @ Rx (matches module B)."""
    Rz = Matrix.Rotation(math.radians(yaw_deg),   4, 'Z')
    Ry = Matrix.Rotation(math.radians(pitch_deg), 4, 'Y')
    Rx = Matrix.Rotation(math.radians(roll_deg),  4, 'X')
    return Rz @ Ry @ Rx


def load_cases(csv_path, max_cases, mhd_filter, parts, only_occluded):
    parts_set = set(p.strip() for p in parts.split(","))
    cases = []
    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                mhd = float(row.get("min_hit_distance_mm", ""))
            except (TypeError, ValueError):
                continue
            if abs(mhd - mhd_filter) > 1e-9:
                continue
            part = str(row.get("part_zh_en", "")).strip()
            if part not in parts_set:
                continue
            sun_occ = str_to_bool(row.get("sun_occluded"))
            det_occ = str_to_bool(row.get("det_occluded"))
            if only_occluded and not (sun_occ or det_occ):
                continue
            try:
                origin = Vector((
                    float(row["origin_x_mm"]),
                    float(row["origin_y_mm"]),
                    float(row["origin_z_mm"]),
                ))
                sun_dir = Vector(parse_vec_from_text(row["sun_dir"])).normalized()
                det_dir = Vector(parse_vec_from_text(row["det_dir"])).normalized()
                ypr = parse_yaw_pitch_roll(row.get("yaw_pitch_roll_zh_en", ""))
            except Exception as e:
                print(f"[load_cases] skip row: {e}")
                continue
            case = {
                "part": part, "mhd": mhd, "face_id": int(row["face_id"]),
                "yaw_deg": ypr[0], "pitch_deg": ypr[1], "roll_deg": ypr[2],
                "origin": origin, "sun_dir": sun_dir, "det_dir": det_dir,
                "sun_current": sun_occ, "det_current": det_occ,
            }
            for prefix in ("face_centroid", "centroid"):
                xk, yk, zk = f"{prefix}_x_mm", f"{prefix}_y_mm", f"{prefix}_z_mm"
                if xk in row and yk in row and zk in row and row[xk] and row[yk] and row[zk]:
                    case[xk] = float(row[xk])
                    case[yk] = float(row[yk])
                    case[zk] = float(row[zk])
            cases.append(case)
            if len(cases) >= max_cases:
                break
    return cases


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)


def make_part_material(name, rgba):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (rgba[0], rgba[1], rgba[2], 1.0)
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    # viewport color for Workbench (MATERIAL color_type)
    mat.diffuse_color = (rgba[0], rgba[1], rgba[2], rgba[3])
    return mat


def make_emissive_material(name, rgb, is_star=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 1.5 if is_star else 1.0
    mat.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
    return mat


def import_stl(path, name, mat):
    before = set(bpy.data.objects)
    imported = False
    try:
        bpy.ops.wm.stl_import(filepath=str(path))
        imported = True
    except Exception:
        pass
    if not imported:
        try:
            bpy.ops.import_mesh.stl(filepath=str(path))
            imported = True
        except Exception as e:
            raise RuntimeError(f"STL import failed for {path}: {e}")
    new_objs = [o for o in bpy.data.objects if o not in before]
    if not new_objs:
        raise RuntimeError(f"STL import produced no object: {path}")
    obj = new_objs[0]
    obj.name = name
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return obj


def bbox_extent(obj):
    vs = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not vs:
        return 0.0
    xs = [v.x for v in vs]; ys = [v.y for v in vs]; zs = [v.z for v in vs]
    return max(max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs))


def apply_pose(part_objs, R4):
    for obj in part_objs:
        obj.matrix_world = R4
    bpy.context.view_layer.update()


def ray_cast_scene(origin, direction, max_dist_mm, self_hit_tol_mm):
    """Return dict with raw_hit, filtered_hit, hit_location, etc."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(
        depsgraph, origin, direction, distance=max_dist_mm
    )
    raw_hit = bool(result)
    hit_distance = None
    hit_loc = None
    hit_obj_name = None
    hit_face = None
    if raw_hit:
        hit_distance = (location - origin).length
        hit_loc = (location.x, location.y, location.z)
        hit_obj_name = obj.name if obj else None
        hit_face = int(index) if index is not None else None
    filtered = raw_hit
    note = ""
    if raw_hit and hit_distance is not None and hit_distance < self_hit_tol_mm:
        filtered = False
        note = "SELF_HIT_IGNORED"
    return {
        "raw_hit": raw_hit, "filtered_hit": filtered,
        "hit_location": hit_loc, "hit_distance_mm": hit_distance,
        "hit_object": hit_obj_name, "hit_face_index": hit_face,
        "note": note,
    }


def make_marker_sphere(name, location, radius, rgb, coll):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    mat = make_emissive_material(name + "_mat", rgb)
    obj.data.materials.append(mat)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def make_marker_star(name, location, normal, r_out, r_in, rgb, coll):
    """Create a 5-pointed star mesh at location, facing along `normal`.

    - r_out: outer tip radius
    - r_in:  inner valley radius
    - normal: direction the star faces (the star lies in the plane perpendicular to this)
    """
    bm = bmesh.new()

    # build 5 tip + 5 valley vertices in local XY, then rotate/orient to normal
    angles = []
    for i in range(10):
        angle = math.radians(90 + i * 36)   # start from top (+Y local), CCW
        r = r_out if (i % 2 == 0) else r_in
        angles.append((r * math.cos(angle), r * math.sin(angle)))

    star_verts = []
    for lx, ly in angles:
        v = bm.verts.new((lx, ly, 0.0))
        star_verts.append(v)

    center = bm.verts.new((0.0, 0.0, 0.0))
    for i in range(10):
        next_i = (i + 1) % 10
        try:
            bm.faces.new([center, star_verts[i], star_verts[next_i]])
        except ValueError:
            pass

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    obj.location = location

    # orient star face-normal along `normal`
    z_local = Vector((0.0, 0.0, 1.0))
    n = normal.normalized() if normal.length > 1e-9 else Vector((0.0, 0.0, 1.0))
    if abs(n.dot(z_local)) < 0.9999:
        rot_quat = z_local.rotation_difference(n)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = rot_quat
    else:
        if n.dot(z_local) < 0:
            obj.rotation_euler = (math.radians(180), 0, 0)

    mat = make_emissive_material(name + "_mat", rgb, is_star=True)
    obj.data.materials.append(mat)
    return obj


def make_ray_cylinder(name, origin, direction, length, radius, rgb, coll):
    if length <= 0:
        length = radius * 2.0
    mid = origin + direction * (length * 0.5)
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=mid)
    obj = bpy.context.active_object
    obj.name = name
    z_axis = Vector((0.0, 0.0, 1.0))
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = z_axis.rotation_difference(direction.normalized())
    mat = make_emissive_material(name + "_mat", rgb)
    obj.data.materials.append(mat)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def _perp_unit(direction):
    """Return a unit vector perpendicular to `direction`."""
    d = direction.normalized()
    world_up = Vector((0.0, 0.0, 1.0))
    ref = Vector((1.0, 0.0, 0.0)) if abs(d.dot(world_up)) > 0.95 else world_up
    p = d.cross(ref)
    if p.length < 1e-9:
        p = d.cross(Vector((0.0, 1.0, 0.0)))
    return p.normalized()


def _make_ortho_camera(name, location, look_at, ortho_scale, clip_far):
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = max(ortho_scale, 5.0)
    cam_data.clip_start = 0.1
    cam_data.clip_end = max(clip_far, 1000.0)
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = location
    direction = (look_at - Vector(location)).normalized()
    cam_obj.rotation_mode = 'QUATERNION'
    cam_obj.rotation_quaternion = Vector((0.0, 0.0, -1.0)).rotation_difference(direction)
    return cam_obj


def setup_overview_camera(model_extent_mm):
    d = max(model_extent_mm * 2.5, 500.0)
    cam = _make_ortho_camera(
        "ReviewCam_Overview",
        location=(d, -d, d * 0.7),
        look_at=Vector((0.0, 0.0, 0.0)),
        ortho_scale=max(model_extent_mm * 2.4, 100.0),
        clip_far=max(model_extent_mm * 20.0, 20000.0),
    )
    return cam


def position_axis_view(cam_obj, origin, ray_dir, model_extent_mm):
    """Place camera on the ray axis and look back at the ray origin."""
    ray_dir = ray_dir.normalized()
    camera_distance = max(model_extent_mm * 1.8, 300.0)
    cam_obj.location = origin + ray_dir * camera_distance
    direction = (origin - cam_obj.location).normalized()
    cam_obj.rotation_quaternion = Vector((0.0, 0.0, -1.0)).rotation_difference(direction)
    cam_obj.data.ortho_scale = max(model_extent_mm * 0.9, 120.0)
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = max(camera_distance + model_extent_mm * 3.0, 5000.0)


def setup_render(scene, width, height):
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    try:
        shading = scene.display.shading
        shading.light = 'STUDIO'
        shading.color_type = 'MATERIAL'
        shading.show_cavity = True
        shading.cavity_type = 'BOTH'
    except Exception as e:
        print(f"[setup_render] shading setup partial: {e}")
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs["Color"].default_value = (0.02, 0.02, 0.03, 1.0)


def make_text_label(name, text, location, size, rgb, coll, camera=None):
    bpy.ops.object.text_add(location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = 'LEFT'
    obj.data.align_y = 'TOP'
    obj.data.size = size
    mat = make_emissive_material(name + "_mat", rgb)
    obj.data.materials.append(mat)
    if camera is not None:
        direction = (camera.location - obj.location).normalized()
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(direction)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def make_camera_label(name, text, cam, coll, color=(1.0, 1.0, 1.0)):
    # Put label near the top-left of the camera view plane.
    forward = (cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()
    right = (cam.matrix_world.to_quaternion() @ Vector((1, 0, 0))).normalized()
    up = (cam.matrix_world.to_quaternion() @ Vector((0, 1, 0))).normalized()
    dist = min(max(cam.data.ortho_scale * 0.85, 80.0), 900.0)
    loc = cam.location + forward * dist - right * cam.data.ortho_scale * 0.46 + up * cam.data.ortho_scale * 0.43
    size = max(cam.data.ortho_scale * 0.035, 8.0)
    return make_text_label(name, text, loc, size, color, coll, camera=cam)


def format_bool_cn(x):
    return "遮挡" if bool(x) else "未遮挡"


def format_rule_cn(x):
    return "通过规则" if bool(x) else "不通过规则"


def make_annotation_text(case_id, view_name, current, raw, filtered, hit_object, hit_distance, diagnosis):
    return (
        f"Case {case_id}｜{view_name}\n"
        f"算法：{format_bool_cn(current)}\n"
        f"Blender原始：{'命中' if raw else '未命中'}"
        f"（{hit_object or '-'}，{fmt_dist(hit_distance)} mm）\n"
        f"Blender过滤后：{format_bool_cn(filtered)}\n"
        f"诊断：{diagnosis}"
    )


def render_with_camera(filepath, cam):
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = str(filepath)
    bpy.ops.render.render(write_still=True)


def save_blend(filepath):
    bpy.ops.wm.save_as_mainfile(filepath=str(filepath))


def diagnose(current, manual):
    if current == manual:
        return "AGREE_OCCLUDED" if current else "AGREE_CLEAR"
    return "DISAGREE"


def make_run_dir(outdir):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(outdir) / f"run_{ts}"
    (run_dir / "figures").mkdir(parents=True, exist_ok=True)
    (run_dir / "blender_files").mkdir(parents=True, exist_ok=True)
    return run_dir


CSV_FIELDS = [
    "case_id", "part", "face_id", "min_hit_distance_mm",
    "yaw_deg", "pitch_deg", "roll_deg",
    "origin_x_mm", "origin_y_mm", "origin_z_mm",
    "origin_surface_clearance_mm", "origin_surface_clearance_part",
    "ray_origin_to_face_centroid_mm", "face_centroid_x_mm", "face_centroid_y_mm", "face_centroid_z_mm",
    "geometry_check",
    "sun_dir_x", "sun_dir_y", "sun_dir_z",
    "det_dir_x", "det_dir_y", "det_dir_z",
    "sun_current_hit", "sun_tool_raw_hit", "sun_tool_filtered_hit",
    "sun_hit_object", "sun_hit_face_index", "sun_hit_distance_mm", "sun_diagnosis",
    "det_current_hit", "det_tool_raw_hit", "det_tool_filtered_hit",
    "det_hit_object", "det_hit_face_index", "det_hit_distance_mm", "det_diagnosis",
    "overall_agree", "overview_png", "sun_view_png", "det_view_png",
    "blend_file", "notes",
]


def write_csv_report(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in CSV_FIELDS})


def fmt_dist(d):
    if isinstance(d, (int, float)):
        return f"{d:.3f}"
    return "-"


def format_geometry_check(value):
    return "**几何检查异常：%s**" % value if value in ("WARN", "FAIL") else str(value)


def write_md_report(rows, path, cfg):
    lines = []
    lines.append("# 人工遮挡抽查报告")
    lines.append("")
    lines.append(f"- 输入 CSV: `{cfg['input']}`")
    lines.append(f"- STL 目录: `{cfg['model_dir']}`")
    lines.append(f"- 输出目录: `{cfg['run_dir']}`")
    lines.append(f"- 抽查数量: {len(rows)}")
    lines.append(f"- mhd 筛选: {cfg['mhd_filter']} mm")
    lines.append(f"- 自相交阈值: {cfg['self_hit_tol_mm']} mm")
    lines.append("- 射线方向: 从 CSV origin 沿 Sun/Det 正向发射；单位 mm。")
    lines.append("- 绿色球 = 算法实际射线起点 `origin`；黄色五角星 = 原始面元中心（仅当输入 CSV 提供 centroid 字段时显示）；红色球 = Blender 过滤后命中点；黄细棒 = 连接面元中心与射线起点。")
    lines.append("- raw 结果按物理命中显示为“遮挡/未遮挡”；filtered 结果按规则过滤显示为“通过规则/不通过规则”。")
    lines.append("- Sun/Det 视图相机沿对应射线轴看向 origin，同时保留另一条参考射线；图内与 .blend 内不写文字解释。")
    lines.append("- 若命中距离很小，红色命中球会贴近绿色 origin 球；报告距离字段为准，不对红球做人工偏移。")
    lines.append("- `origin_surface_probe_mm` 是用有限方向 ray probe 得到的近似表面距离，用于发现坐标/起点异常，不等同于严格最近点距离。")
    lines.append("")

    n = len(rows)
    sun_agree = sum(1 for r in rows if str(r["sun_diagnosis"]).startswith("AGREE"))
    det_agree = sum(1 for r in rows if str(r["det_diagnosis"]).startswith("AGREE"))
    overall_agree = sum(1 for r in rows if r["overall_agree"])
    lines.append("## 总览统计")
    lines.append("")
    lines.append("| 项目 | 数量 |")
    lines.append("|---|---:|")
    lines.append(f"| 总 case 数 | {n} |")
    lines.append(f"| 全部一致 | {overall_agree} |")
    lines.append(f"| Sun 一致 | {sun_agree} |")
    lines.append(f"| Det 一致 | {det_agree} |")
    lines.append(f"| Sun 不一致 | {n - sun_agree} |")
    lines.append(f"| Det 不一致 | {n - det_agree} |")
    lines.append("")

    for r in rows:
        clearance = r.get("origin_surface_clearance_mm")
        clearance_text = f"{clearance:.3f} mm ({r.get('origin_surface_clearance_part') or '-'})" if isinstance(clearance, (int, float)) else "200 mm probe 内无命中"
        lines.append(f"## Case {r['case_id']} · {r['part']} · face {r['face_id']}")
        lines.append("")
        lines.append(f"- mhd: {r['min_hit_distance_mm']} mm；origin: [{r['origin_x_mm']:.3f}, {r['origin_y_mm']:.3f}, {r['origin_z_mm']:.3f}]；origin_surface_probe: {clearance_text}")
        lines.append(f"- 原始面元中心: {r.get('face_centroid_x_mm') if r.get('face_centroid_x_mm') is not None else '输入 CSV 未提供'}；ray_origin_to_face_centroid: {fmt_dist(r.get('ray_origin_to_face_centroid_mm'))} mm；geometry_check: {format_geometry_check(r.get('geometry_check'))}")
        lines.append("")
        lines.append("### 1. 算法结果")
        lines.append("")
        lines.append(f"- Sun: `{format_bool_cn(r['sun_current_hit'])}`")
        lines.append(f"- Det: `{format_bool_cn(r['det_current_hit'])}`")
        lines.append("")
        lines.append("### 2. Blender 结果")
        lines.append("")
        lines.append("| 方向 | raw（遮挡/未遮挡） | filtered（通过规则/不通过规则） | 命中对象 | 面索引 | 距离/mm |")
        lines.append("|---|---|---|---|---:|---:|")
        lines.append(f"| Sun | {format_bool_cn(r['sun_tool_raw_hit'])} | {format_rule_cn(r['sun_tool_filtered_hit'])} | {r['sun_hit_object'] or '-'} | {r['sun_hit_face_index'] if r['sun_hit_face_index'] is not None else '-'} | {fmt_dist(r['sun_hit_distance_mm'])} |")
        lines.append(f"| Det | {format_bool_cn(r['det_tool_raw_hit'])} | {format_rule_cn(r['det_tool_filtered_hit'])} | {r['det_hit_object'] or '-'} | {r['det_hit_face_index'] if r['det_hit_face_index'] is not None else '-'} | {fmt_dist(r['det_hit_distance_mm'])} |")
        lines.append("")
        lines.append("### 3. 诊断结果")
        lines.append("")
        lines.append(f"- Sun: **{r['sun_diagnosis']}**")
        lines.append(f"- Det: **{r['det_diagnosis']}**")
        lines.append(f"- Overall: **{r['overall_agree']}**")
        lines.append("")
        lines.append("### 视图")
        lines.append("")
        lines.append(f"- overview: ![overview]({r['overview_png']})")
        lines.append(f"- sun_view: ![sun_view]({r.get('sun_view_png','')})")
        lines.append(f"- det_view: ![det_view]({r.get('det_view_png','')})")
        lines.append(f"- Blender: `{r['blend_file']}`")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def args_max_ray_display():
    """Return the max ray distance note string; uses a module-level set by main."""
    return _MAX_RAY_DIST_DISPLAY


_MAX_RAY_DIST_DISPLAY = "10000"


def origin_surface_clearance(origin, part_objs):
    """Return (min_distance_mm, nearest_part_name) from origin to any STL surface.

    Probes 6 axis-aligned + 6 diagonal directions and returns the minimum
    distance among all reported hits (filtering self-hit at distance < 1e-6).
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    dirs = [
        Vector(( 1, 0, 0)), Vector((-1, 0, 0)),
        Vector(( 0, 1, 0)), Vector(( 0,-1, 0)),
        Vector(( 0, 0, 1)), Vector(( 0, 0,-1)),
        Vector(( 1, 1, 1)), Vector((-1,-1,-1)),
        Vector(( 1,-1, 1)), Vector((-1, 1,-1)),
        Vector(( 1, 1,-1)), Vector((-1,-1, 1)),
    ]
    best_dist = None
    best_part = None
    for d in dirs:
        d_n = d.normalized()
        result, location, _, _, obj, _ = bpy.context.scene.ray_cast(
            depsgraph, origin, d_n, distance=200.0
        )
        if result and obj:
            dist = (location - origin).length
            if dist < 1e-9:
                continue
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_part = obj.name
    return best_dist, best_part


def get_face_centroid(case):
    keys = (("face_centroid_x_mm", "face_centroid_y_mm", "face_centroid_z_mm"),
            ("centroid_x_mm", "centroid_y_mm", "centroid_z_mm"))
    for xk, yk, zk in keys:
        if xk in case and yk in case and zk in case:
            return Vector((case[xk], case[yk], case[zk]))
    return None


def process_case(case, idx, run_dir, part_objs, cams, args, model_extent):
    case_id = f"{idx:04d}"
    R4 = attitude_matrix(case["yaw_deg"], case["pitch_deg"], case["roll_deg"])
    apply_pose(part_objs, R4)

    origin = case["origin"]
    sun_dir = case["sun_dir"]
    det_dir = case["det_dir"]

    # 1) Surface clearance probe (geometry sanity check, no markers in scene yet)
    clearance, clearance_part = origin_surface_clearance(origin, part_objs)

    # 2) Ray casting (still no markers in scene)
    sun_res = ray_cast_scene(origin, sun_dir, args.max_ray_dist_mm, args.self_hit_tol_mm)
    det_res = ray_cast_scene(origin, det_dir, args.max_ray_dist_mm, args.self_hit_tol_mm)

    # 3) Build case visualization
    coll_name = f"Case_{case_id}"
    coll = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(coll)

    marker_radius = max(4.0, model_extent * 0.006)
    ray_radius = max(0.4, model_extent * 0.0008)

    make_marker_sphere(f"{case_id}_ray_origin", origin, marker_radius,
                       (0.1, 1.0, 0.1), coll)
    face_centroid = get_face_centroid(case)
    ray_origin_to_face_centroid = None
    geometry_check = "NOT_AVAILABLE"
    if face_centroid is not None:
        ray_origin_to_face_centroid = (origin - face_centroid).length
        # star: outer tip radius ~3x green sphere, faces outward along surface normal
        face_normal = (origin - face_centroid).normalized()
        make_marker_star(
            f"{case_id}_face_centroid", face_centroid,
            face_normal, marker_radius * 3.0, marker_radius * 1.2,
            (1.0, 0.85, 0.0), coll)
        # thin connecting rod: origin → centroid, so both are visible even when overlapping
        connector_len = ray_origin_to_face_centroid if ray_origin_to_face_centroid else 0.1
        make_ray_cylinder(
            f"{case_id}_centroid_rod", face_centroid,
            -face_normal, connector_len, ray_radius * 0.5,
            (1.0, 0.85, 0.0), coll)
        geometry_check = "PASS" if ray_origin_to_face_centroid <= max(case["mhd"] * 1.5, 2.0) else "WARN"

    close_hit_threshold = marker_radius * 1.8
    visible_ray_len = model_extent * 1.5
    sun_ray_len = visible_ray_len if (
        sun_res["filtered_hit"] and sun_res["hit_distance_mm"] <= close_hit_threshold
    ) else sun_res["hit_distance_mm"]
    det_ray_len = visible_ray_len if (
        det_res["filtered_hit"] and det_res["hit_distance_mm"] <= close_hit_threshold
    ) else det_res["hit_distance_mm"]
    if sun_res["filtered_hit"]:
        make_ray_cylinder(f"{case_id}_sun_ray", origin, sun_dir, sun_ray_len, ray_radius,
                          (1.0, 0.5, 0.1), coll)
    if det_res["filtered_hit"]:
        make_ray_cylinder(f"{case_id}_det_ray", origin, det_dir, det_ray_len, ray_radius,
                          (0.2, 0.5, 1.0), coll)

    if (sun_res["filtered_hit"] and sun_res["hit_location"] is not None
            and sun_res["hit_distance_mm"] > close_hit_threshold):
        make_marker_sphere(f"{case_id}_sun_hit", Vector(sun_res["hit_location"]),
                           marker_radius * 0.8, (1.0, 0.1, 0.1), coll)
    if (det_res["filtered_hit"] and det_res["hit_location"] is not None
            and det_res["hit_distance_mm"] > close_hit_threshold):
        make_marker_sphere(f"{case_id}_det_hit", Vector(det_res["hit_location"]),
                           marker_radius * 0.8, (1.0, 0.1, 0.1), coll)

    # 4) Position local-view cameras
    position_axis_view(cams["sun"], origin, sun_dir, model_extent)
    position_axis_view(cams["det"], origin, det_dir, model_extent)

    sun_diag = diagnose(case["sun_current"], sun_res["filtered_hit"])
    det_diag = diagnose(case["det_current"], det_res["filtered_hit"])
    overall = sun_diag.startswith("AGREE") and det_diag.startswith("AGREE")

    # Labels are intentionally omitted from PNG/.blend outputs.

    # 5) Render 3 PNGs
    tag = f"case_{case_id}_{case['part']}_f{case['face_id']}_mhd{case['mhd']:.1f}".replace(".", "p")
    overview_png = run_dir / "figures" / f"{tag}_overview.png"
    sun_png      = run_dir / "figures" / f"{tag}_sun_view.png"
    det_png      = run_dir / "figures" / f"{tag}_det_view.png"
    blend_path   = run_dir / "blender_files" / f"{tag}.blend"

    if args.render_png:
        for png, cam_key in ((overview_png, "overview"), (sun_png, "sun"), (det_png, "det")):
            try:
                render_with_camera(png, cams[cam_key])
            except Exception as e:
                print(f"[case {case_id}] render {cam_key} failed: {e}")
                traceback.print_exc()

    # 6) Save .blend with overview camera active (all 3 cams kept in scene)
    bpy.context.scene.camera = cams["overview"]

    row = {
        "case_id": case_id, "part": case["part"], "face_id": case["face_id"],
        "min_hit_distance_mm": case["mhd"],
        "yaw_deg": case["yaw_deg"], "pitch_deg": case["pitch_deg"], "roll_deg": case["roll_deg"],
        "origin_x_mm": origin.x, "origin_y_mm": origin.y, "origin_z_mm": origin.z,
        "ray_origin_to_face_centroid_mm": ray_origin_to_face_centroid,
        "face_centroid_x_mm": face_centroid.x if face_centroid is not None else None,
        "face_centroid_y_mm": face_centroid.y if face_centroid is not None else None,
        "face_centroid_z_mm": face_centroid.z if face_centroid is not None else None,
        "geometry_check": geometry_check,
        "sun_dir_x": sun_dir.x, "sun_dir_y": sun_dir.y, "sun_dir_z": sun_dir.z,
        "det_dir_x": det_dir.x, "det_dir_y": det_dir.y, "det_dir_z": det_dir.z,
        "sun_current_hit": case["sun_current"],
        "sun_tool_raw_hit": sun_res["raw_hit"], "sun_tool_filtered_hit": sun_res["filtered_hit"],
        "sun_hit_object": sun_res["hit_object"], "sun_hit_face_index": sun_res["hit_face_index"],
        "sun_hit_distance_mm": sun_res["hit_distance_mm"], "sun_diagnosis": sun_diag,
        "det_current_hit": case["det_current"],
        "det_tool_raw_hit": det_res["raw_hit"], "det_tool_filtered_hit": det_res["filtered_hit"],
        "det_hit_object": det_res["hit_object"], "det_hit_face_index": det_res["hit_face_index"],
        "det_hit_distance_mm": det_res["hit_distance_mm"], "det_diagnosis": det_diag,
        "overall_agree": overall,
        "origin_surface_clearance_mm": clearance,
        "origin_surface_clearance_part": clearance_part,
        "overview_png": f"figures/{overview_png.name}",
        "sun_view_png": f"figures/{sun_png.name}",
        "det_view_png": f"figures/{det_png.name}",
        "blend_file": f"blender_files/{blend_path.name}",
        "notes": f"sun:{sun_res['note']} det:{det_res['note']}".strip(),
    }

    if args.save_blend:
        try:
            save_blend(blend_path)
        except Exception as e:
            print(f"[case {case_id}] save_blend failed: {e}")
            traceback.print_exc()

    for obj in list(coll.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(coll)

    return row


def main():
    args = parse_args()

    input_path = Path(args.input)
    model_dir = Path(args.model_dir)
    if not input_path.exists():
        print(f"[ERROR] input CSV not found: {input_path}")
        sys.exit(2)
    if not model_dir.exists():
        print(f"[ERROR] model_dir not found: {model_dir}")
        sys.exit(2)

    run_dir = make_run_dir(args.outdir)
    print(f"[manual_review] run_dir = {run_dir}")
    print(f"[manual_review] filter: mhd={args.mhd_filter} parts={args.parts} "
          f"max_cases={args.max_cases} only_occluded={args.only_occluded}")

    cases = load_cases(input_path, args.max_cases, args.mhd_filter, args.parts,
                       args.only_occluded)
    print(f"[manual_review] loaded {len(cases)} cases")
    if not cases:
        print("[manual_review] no cases matched; aborting")
        sys.exit(1)

    clear_scene()
    scene = bpy.context.scene
    setup_render(scene, args.render_width, args.render_height)

    part_objs = []
    extents = []
    for part, rgba in PART_COLORS.items():
        stl = model_dir / f"{part}.stl"
        if not stl.exists():
            print(f"[manual_review] WARN: missing STL {stl}")
            continue
        mat = make_part_material(part + "_mat", rgba)
        obj = import_stl(stl, part, mat)
        part_objs.append(obj)
        extents.append(bbox_extent(obj))
    if not part_objs:
        print("[ERROR] no STL imported; aborting")
        sys.exit(3)
    model_extent = max(extents) if extents else 1000.0
    print(f"[manual_review] imported {len(part_objs)} parts, extent ~{model_extent:.1f} mm")

    overview_cam = setup_overview_camera(model_extent)
    sun_cam = _make_ortho_camera(
        "ReviewCam_Sun",
        location=(0.0, 0.0, model_extent),
        look_at=Vector((0.0, 0.0, 0.0)),
        ortho_scale=200.0,
        clip_far=max(model_extent * 20.0, 20000.0),
    )
    det_cam = _make_ortho_camera(
        "ReviewCam_Det",
        location=(0.0, 0.0, model_extent),
        look_at=Vector((0.0, 0.0, 0.0)),
        ortho_scale=200.0,
        clip_far=max(model_extent * 20.0, 20000.0),
    )
    cams = {"overview": overview_cam, "sun": sun_cam, "det": det_cam}

    # MD report uses module-level display var for max ray dist
    global _MAX_RAY_DIST_DISPLAY
    _MAX_RAY_DIST_DISPLAY = f"{int(args.max_ray_dist_mm)}"

    rows = []
    for i, case in enumerate(cases, start=1):
        try:
            row = process_case(case, i, run_dir, part_objs, cams, args, model_extent)
            rows.append(row)
            print(f"[case {row['case_id']}] {case['part']} f{case['face_id']} "
                  f"clearance={row.get('origin_surface_clearance_mm')} "
                  f"sun={row['sun_diagnosis']} det={row['det_diagnosis']}")
        except Exception as e:
            print(f"[case {i}] failed: {e}")
            traceback.print_exc()

    csv_report = run_dir / "review_report.csv"
    md_report = run_dir / "review_report.md"
    write_csv_report(rows, csv_report)
    write_md_report(rows, md_report, {
        "input": str(input_path), "model_dir": str(model_dir),
        "run_dir": str(run_dir),
        "mhd_filter": args.mhd_filter, "parts": args.parts,
        "self_hit_tol_mm": args.self_hit_tol_mm,
        "max_ray_dist_mm": args.max_ray_dist_mm,
    })
    print(f"[manual_review] done. {len(rows)} cases.")
    print(f"[manual_review] csv: {csv_report}")
    print(f"[manual_review] md : {md_report}")


if __name__ == "__main__":
    main()


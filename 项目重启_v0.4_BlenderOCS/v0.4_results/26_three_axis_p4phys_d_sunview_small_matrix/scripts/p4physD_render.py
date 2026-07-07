# -*- coding: utf-8 -*-
"""
p4physD_render.py —— 26 包 sun/view 小矩阵新增渲染（Blender 内运行）
================================================================================
R153 P4-PHYS-D 子任务 B/C 的渲染端。

只渲染"必须新增"的视角，物理精确复用 baseline：
    - G1/G2（太阳扰动）：只渲染 sun 视角 EXR（camera 复用 baseline）。
    - G3/G4（探测器扰动）：只渲染 camera 视角 EXR（sun 复用 baseline）。
    - G0 baseline：不渲染。

关键物理事实：
    几何 pass（Normal/Depth/IndexOB/Position）是纯几何量，与光照无关。
    - sun EXR = 沿 sun_dir 放置正交相机渲染的 depth/position => 只随 sun_dir 变。
    - camera EXR = 沿 det_dir 放置正交相机渲染的 normal/depth/indexob/position => 只随 det_dir 变。
    因此 sun 扰动无需重渲 camera，view 扰动无需重渲 sun。

用法：
    blender --background --python p4physD_render.py -- --mode smoke
    blender --background --python p4physD_render.py -- --mode formal
    blender --background --python p4physD_render.py -- --mode formal --geom G1_sun_plus

红线：不改 20/21/23A/23B/24/25 源包；不训练；只写 26/render/。
"""
import os
import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime

try:
    import bpy  # noqa
    from mathutils import Vector
except ImportError:
    print("[ERROR] 必须用 blender --background --python 运行")
    sys.exit(1)

THIS_DIR = Path(__file__).resolve().parent          # 26/scripts
V04_ROOT = THIS_DIR.parents[2]
CODE_BLENDER = V04_ROOT / "06_v0.4_code" / "02_blender"
DRIVER_PATH = CODE_BLENDER / "render_full_2664_shadow.py"

# 载入本包配置
spec_cfg = importlib.util.spec_from_file_location("p4physD_config", str(THIS_DIR / "p4physD_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    mode, geom_filter = "formal", None
    for i, a in enumerate(argv):
        if a == "--mode" and i + 1 < len(argv):
            mode = argv[i + 1]
        if a == "--geom" and i + 1 < len(argv):
            geom_filter = argv[i + 1]
    return mode, geom_filter


def load_driver():
    spec = importlib.util.spec_from_file_location("render_full_2664_shadow", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_render_plan(mode, geom_filter):
    """返回 [(geom, pose, view)] 需要新渲染的单元。"""
    if mode == "smoke":
        geoms = [cfg.GEOM_BY_ID[cfg.SMOKE_GEOM]]
        poses = [cfg.POSE_BY_ID[p] for p in cfg.SMOKE_POSES]
    else:
        geoms = [g for g in cfg.GEOMETRIES if g["render_view"] != "none"]
        if geom_filter:
            geoms = [g for g in geoms if g["geom_id"] == geom_filter]
        poses = cfg.POSES

    plan = []
    for g in geoms:
        view = g["render_view"]
        if view == "none":
            continue
        for pose in poses:
            plan.append((g, pose, view))
    return plan


def main():
    mode, geom_filter = parse_args()
    plan = build_render_plan(mode, geom_filter)
    print("=" * 78)
    print(f"[26-RENDER] mode={mode} geom_filter={geom_filter} n_units={len(plan)}")
    print("=" * 78)

    mod = load_driver()

    # 场景搭建（一次）
    mod.clear_scene()
    sat_root = mod.import_stls()
    r_max = mod.compute_bbox_radius(sat_root)
    print(f"r_max={r_max:.6f}  (cfg.R_MAX={cfg.R_MAX:.6f})")
    scene = bpy.context.scene

    results = []
    log = {"timestamp": datetime.now().isoformat(), "mode": mode,
           "r_max": r_max, "units": []}

    for i, (g, pose, view) in enumerate(plan, 1):
        gid = g["geom_id"]; label = pose["label"]
        out_dir = cfg.RENDER_BASE / gid
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{label}_{view}.exr"

        # 方向向量：view=camera 用 det_dir，view=sun 用 sun_dir
        if view == "camera":
            direction = list(map(float, g["det_dir"]))
            cam = mod.setup_camera(direction, r_max, name=f"Cam_{gid}")
            mod.setup_render_passes(scene, enable_normal=True, enable_indexob=True)
        else:  # sun
            direction = list(map(float, g["sun_dir"]))
            cam = mod.setup_camera(direction, r_max, name=f"Sun_{gid}")
            mod.setup_render_passes(scene, enable_normal=False, enable_indexob=False)

        attitude = {"yaw": pose["yaw"], "pitch": pose["pitch"], "roll": pose["roll"], "label": label}
        print(f"\n[{i}/{len(plan)}] {gid} {label} view={view}")
        mod.render_one_view(scene, sat_root, attitude, str(out_dir), view, cam)

        # 清理临时相机，避免累积
        try:
            bpy.data.objects.remove(cam, do_unlink=True)
        except Exception:
            pass

        ok = out_path.is_file()
        results.append((gid, label, view, "OK" if ok else "FAILED"))
        log["units"].append({"geom_id": gid, "label": label, "view": view,
                             "yaw": pose["yaw"], "pitch": pose["pitch"], "roll": pose["roll"],
                             "sun_dir": list(map(float, g["sun_dir"])),
                             "det_dir": list(map(float, g["det_dir"])),
                             "out": str(out_path.relative_to(V04_ROOT)).replace("\\", "/"),
                             "status": "OK" if ok else "FAILED"})

    n_ok = sum(1 for r in results if r[3] == "OK")
    log["n_units"] = len(plan); log["n_ok"] = n_ok; log["n_failed"] = len(plan) - n_ok

    log_name = "p4physD_smoke_render.log" if mode == "smoke" else "p4physD_render.log"
    log_path = cfg.PKG26 / "logs" / log_name
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 78)
    print(f"[26-RENDER DONE] OK={n_ok}/{len(plan)}  log={log_path}")
    for r in results:
        print(f"  [{r[3]}] {r[0]} {r[1]} {r[2]}")
    return 0 if n_ok == len(plan) else 1


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
p4physF_render.py —— 28 包 P4-PHYS-F 新增渲染（Blender 内运行）
================================================================================
R157 渲染端。三种模式：
    --mode smoke  ：只渲染 R3L_smoke（yaw=55,pitch=60,roll=+20）的 cam_vm7 + sun_sp7（2 单元）。
    --mode stageB ：渲染 26 个新网格姿态的 cam_vm7 + sun_sp7（已存在的跳过，≤52 单元累计）。
    --mode stageC ：读取 audit/stagec_poses.json，为每个 Stage C 姿态渲染
                    cam_vm5 / cam_vm9 / sun_sp5 / sun_sp9（已存在的跳过，≤24 单元）。

复用原理：camera EXR 只随 view_offset 与姿态变；sun EXR 只随 sun_offset 与姿态变。
渲染预算硬上限：全轮新增 ≤80 单元；超限直接拒绝执行。

用法：
    blender --background --python p4physF_render.py -- --mode smoke
"""
import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime

try:
    import bpy  # noqa
except ImportError:
    print("[ERROR] 必须用 blender --background --python 运行")
    sys.exit(1)

THIS_DIR = Path(__file__).resolve().parent
V04_ROOT = THIS_DIR.parents[2]
DRIVER_PATH = V04_ROOT / "06_v0.4_code" / "02_blender" / "render_full_2664_shadow.py"

spec_cfg = importlib.util.spec_from_file_location("p4physF_config", str(THIS_DIR / "p4physF_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    mode = "smoke"
    for i, a in enumerate(argv):
        if a == "--mode" and i + 1 < len(argv):
            mode = argv[i + 1]
    return mode


def load_driver():
    spec = importlib.util.spec_from_file_location("render_full_2664_shadow", str(DRIVER_PATH))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def count_existing_new_renders():
    """当前 28/render 下已存在的新增 EXR 数（用于累计预算核验）。"""
    n = 0
    for d in cfg.RENDER_BASE.glob("*"):
        if d.is_dir():
            n += len(list(d.glob("*.exr")))
    return n


def build_plan(mode):
    """返回 [(subdir, pose_dict, view, direction)]，跳过已存在文件。"""
    plan = []

    def add(subdir, pose, view, direction):
        out = cfg.RENDER_BASE / subdir / f"{pose['label']}_{view}.exr"
        if not out.is_file():
            plan.append((subdir, pose, view, list(map(float, direction))))

    if mode == "smoke":
        p = cfg.SMOKE_POSE
        add("cam_vm7", p, "camera", cfg.DET_DIR[-7])
        add("sun_sp7", p, "sun", cfg.SUN_DIR[7])
    elif mode == "stageB":
        for p in cfg.STAGEB_NEW:
            add("cam_vm7", p, "camera", cfg.DET_DIR[-7])
            add("sun_sp7", p, "sun", cfg.SUN_DIR[7])
    elif mode == "stageC":
        with open(cfg.STAGEC_POSES_JSON, encoding="utf-8") as f:
            stagec = json.load(f)["poses"]
        for p in stagec:
            add("cam_vm5", p, "camera", cfg.DET_DIR[-5])
            add("cam_vm9", p, "camera", cfg.DET_DIR[-9])
            add("sun_sp5", p, "sun", cfg.SUN_DIR[5])
            add("sun_sp9", p, "sun", cfg.SUN_DIR[9])
    else:
        raise ValueError(f"unknown mode {mode}")
    return plan


def main():
    mode = parse_args()
    plan = build_plan(mode)
    already = count_existing_new_renders()
    if already + len(plan) > cfg.TOTAL_RENDER_CAP:
        print(f"[ABORT] budget exceeded: existing={already} + plan={len(plan)} > cap={cfg.TOTAL_RENDER_CAP}")
        sys.exit(2)

    print("=" * 78)
    print(f"[28-RENDER] mode={mode} n_units={len(plan)} existing={already} cap={cfg.TOTAL_RENDER_CAP}")
    print("=" * 78)

    mod = load_driver()
    mod.clear_scene()
    sat_root = mod.import_stls()
    r_max = mod.compute_bbox_radius(sat_root)
    print(f"r_max={r_max:.6f}  (cfg.R_MAX={cfg.R_MAX:.6f})")
    scene = bpy.context.scene

    results = []
    log = {"timestamp": datetime.now().isoformat(), "mode": mode, "r_max": r_max, "units": []}

    for i, (subdir, pose, view, direction) in enumerate(plan, 1):
        out_dir = cfg.RENDER_BASE / subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{pose['label']}_{view}.exr"

        if view == "camera":
            cam = mod.setup_camera(direction, r_max, name=f"Cam_{subdir}")
            mod.setup_render_passes(scene, enable_normal=True, enable_indexob=True)
        else:
            cam = mod.setup_camera(direction, r_max, name=f"Sun_{subdir}")
            mod.setup_render_passes(scene, enable_normal=False, enable_indexob=False)

        attitude = {"yaw": pose["yaw"], "pitch": pose["pitch"], "roll": pose["roll"], "label": pose["label"]}
        print(f"\n[{i}/{len(plan)}] {subdir} {pose['label']} view={view}")
        mod.render_one_view(scene, sat_root, attitude, str(out_dir), view, cam)
        try:
            bpy.data.objects.remove(cam, do_unlink=True)
        except Exception:
            pass

        ok = out_path.is_file()
        results.append((subdir, pose["label"], view, "OK" if ok else "FAILED"))
        log["units"].append({"subdir": subdir, "label": pose["label"], "view": view,
                             "yaw": pose["yaw"], "pitch": pose["pitch"], "roll": pose["roll"],
                             "direction": direction,
                             "out": str(out_path.relative_to(V04_ROOT)).replace("\\", "/"),
                             "status": "OK" if ok else "FAILED"})

    n_ok = sum(1 for r in results if r[3] == "OK")
    log["n_units"] = len(plan); log["n_ok"] = n_ok; log["n_failed"] = len(plan) - n_ok
    log["cumulative_new_renders"] = count_existing_new_renders()

    log_path = cfg.PKG28 / "logs" / f"p4physF_{mode}_render.log"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 78)
    print(f"[28-RENDER DONE] mode={mode} OK={n_ok}/{len(plan)} cumulative={log['cumulative_new_renders']}")
    return 0 if n_ok == len(plan) else 1


if __name__ == "__main__":
    sys.exit(main())

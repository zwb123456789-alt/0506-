# -*- coding: utf-8 -*-
"""
blender_test.py —— Blender headless 最小冒烟测试
=================================================
通过 blender --background --python blender_test.py 运行。
目标：在 03_results/blender_test/ 下生成 test_scene.blend，
      证明 Blender Python API 可用、能保存场景。

注意：本脚本运行在 Blender 内置 Python 解释器中，
      只能用 bpy 等 Blender 自带模块，不要 import 外部包。
"""

import os
import sys

try:
    import bpy
except ImportError:
    print("[FAIL] bpy 不可用 —— 请用 blender.exe --background --python 运行本脚本。")
    sys.exit(1)


PROJECT_ROOT = r"D:\我的文件\研究生学术\光学项目\0506新"
OUT_DIR      = os.path.join(PROJECT_ROOT, "ocs_project", "03_results", "blender_test")
os.makedirs(OUT_DIR, exist_ok=True)


def clear_scene():
    """清空当前场景所有物体。"""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def build_test_scene():
    clear_scene()

    # 立方体
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))

    # 相机
    bpy.ops.object.camera_add(location=(3, -3, 2), rotation=(1.1, 0, 0.75))
    bpy.context.scene.camera = bpy.context.object

    # 太阳光
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.object
    sun.name = "Test_Sun"
    sun.data.energy = 3.0

    # 渲染设置
    scene = bpy.context.scene
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.engine = "CYCLES"  # GPU 渲染由 Cycles 走，但本测试不真正渲染


def main():
    print(f"[INFO] Blender version: {bpy.app.version_string}")
    build_test_scene()
    blend_path = os.path.join(OUT_DIR, "test_scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved: {blend_path}")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
phase0_smoke_test.py —— Phase 0 单姿态 smoke test
================================================
验证最小工程闭环：STL 加载 + Blender 最小调用 + 单姿态输出记录

任务边界：
- 只测试单姿态 yaw=0, pitch=0, roll=0
- 验证 STL 加载、mesh 基本信息
- 验证 Blender 最小调用（不进行全量渲染）
- 记录资源估计（耗时、文件大小）

禁止：
- 不运行全量 2664 姿态
- 不训练模型
- 不写入论文结论
"""

import sys
import os
import time
import json
from pathlib import Path

# 添加代码路径
project_root = Path(__file__).resolve().parents[2]
config_dir = project_root / "06_v0.4_code" / "00_config"
geometry_dir = project_root / "06_v0.4_code" / "01_geometry"

sys.path.insert(0, str(config_dir))
sys.path.insert(0, str(geometry_dir))

import numpy as np
import trimesh
from config_v0_4 import PART_FILES, BLENDER_EXE, OUTPUT_DIR, PROJECT_ROOT
from materials_v0_4 import get_material_b0
from geometry_loader import load_meshes, euler_to_matrix
from attitude_grid import build_record_id


def main():
    """执行单姿态 smoke test"""

    print("=" * 80)
    print("Phase 0 单姿态 smoke test")
    print("=" * 80)
    print()

    # ============================================================
    # 1. 环境信息
    # ============================================================
    print("[1/6] 环境信息")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Executable: {sys.executable}")
    print(f"  numpy: {np.__version__}")
    print(f"  trimesh: {trimesh.__version__}")
    print(f"  Project root: {PROJECT_ROOT}")
    print()

    # ============================================================
    # 2. 检查路径
    # ============================================================
    print("[2/6] 检查路径")

    # 检查 STL 文件
    for part_name, stl_path in PART_FILES.items():
        exists = os.path.exists(stl_path)
        status = "[OK]" if exists else "[FAIL]"
        print(f"  {status} {part_name}: {stl_path}")
        if not exists:
            raise FileNotFoundError(f"STL file not found: {stl_path}")

    # 检查 Blender
    blender_exists = os.path.exists(BLENDER_EXE)
    status = "[OK]" if blender_exists else "[FAIL]"
    print(f"  {status} Blender: {BLENDER_EXE}")
    if not blender_exists:
        raise FileNotFoundError(f"Blender executable not found: {BLENDER_EXE}")

    print()

    # ============================================================
    # 3. 加载 STL（单姿态测试：不抽稀）
    # ============================================================
    print("[3/6] 加载 STL 部件（不抽稀）")
    t0 = time.time()

    meshes, total_faces = load_meshes(PART_FILES, decimate_ratio=1.0, verbose=True)

    load_time = time.time() - t0
    print(f"\n  加载耗时: {load_time:.2f} 秒")
    print()

    # 记录 mesh 信息
    mesh_info = {}
    for part_name, mesh in meshes.items():
        verts = mesh.vertices
        faces = mesh.faces
        bbox = verts.max(axis=0) - verts.min(axis=0)

        mesh_info[part_name] = {
            "num_vertices": len(verts),
            "num_faces": len(faces),
            "bbox_mm": bbox.tolist(),
            "bbox_max_mm": float(bbox.max()),
        }

        print(f"  [{part_name}]")
        print(f"    顶点数: {len(verts):,}")
        print(f"    面元数: {len(faces):,}")
        print(f"    包围盒: {bbox[0]:.1f} × {bbox[1]:.1f} × {bbox[2]:.1f} mm")

    print()

    # ============================================================
    # 4. 单姿态设置
    # ============================================================
    print("[4/6] 单姿态设置")

    yaw, pitch, roll = 0, 0, 0
    record_id = build_record_id(yaw, pitch)

    print(f"  姿态: yaw={yaw}°, pitch={pitch}°, roll={roll}°")
    print(f"  record_id: {record_id}")

    # 计算旋转矩阵
    R = euler_to_matrix(yaw, pitch, roll, degrees=True)
    print(f"  旋转矩阵 R (M→I):")
    print(f"    {R[0]}")
    print(f"    {R[1]}")
    print(f"    {R[2]}")

    print()

    # ============================================================
    # 5. 材料参数检查
    # ============================================================
    print("[5/6] 材料参数检查（B0 baseline）")

    for part_name in PART_FILES.keys():
        mat = get_material_b0(part_name)
        print(f"  [{part_name}]")
        print(f"    brdf_model: {mat['brdf_model']}")
        print(f"    rho_d: {mat['rho_d']:.2f}")
        print(f"    rho_s: {mat['rho_s']:.2f}")
        print(f"    n: {mat['n']}")
        print(f"    brdf_branch: {mat['brdf_branch']}")

    print()

    # ============================================================
    # 6. Blender 最小调用检查
    # ============================================================
    print("[6/6] Blender 最小调用检查")
    print("  说明：本轮只检查 Blender 可执行文件存在性和版本信息")
    print("  不执行实际渲染，不生成 EXR/PNG 文件")

    # 获取 Blender 版本
    import subprocess
    try:
        result = subprocess.run(
            [BLENDER_EXE, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        version_output = result.stdout.strip()
        print(f"\n  Blender version info:")
        for line in version_output.split('\n')[:3]:  # 只打印前3行
            print(f"    {line}")

        blender_callable = True
    except Exception as e:
        print(f"\n  [FAIL] Blender call failed: {e}")
        blender_callable = False

    print()

    # ============================================================
    # 7. 输出结果
    # ============================================================
    print("=" * 80)
    print("Smoke test 完成")
    print("=" * 80)

    # 准备资源估计数据
    resource_estimate = {
        "test_type": "single_pose_smoke_test",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "attitude": {
            "yaw": yaw,
            "pitch": pitch,
            "roll": roll,
            "record_id": record_id,
        },
        "stl_loading": {
            "total_faces": total_faces,
            "load_time_seconds": load_time,
            "decimate_ratio": 1.0,
        },
        "mesh_info": mesh_info,
        "blender": {
            "exe_path": BLENDER_EXE,
            "exists": blender_exists,
            "callable": blender_callable,
        },
        "notes": [
            "本轮只执行 STL 加载和 Blender 可执行性检查",
            "未生成 EXR/PNG/npy 数据",
            "未运行 Blender 实际渲染",
            "未训练模型",
            "未进入论文结论",
        ]
    }

    return resource_estimate


if __name__ == "__main__":
    resource_estimate = main()

    # 输出资源估计到 JSON
    output_dir = Path(OUTPUT_DIR) / "00_validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "resource_estimate_single_pose.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resource_estimate, f, indent=2, ensure_ascii=False)

    print(f"\n资源估计已保存: {json_path}")

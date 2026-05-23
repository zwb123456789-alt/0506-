# -*- coding: utf-8 -*-
"""手算 yaw=150 / pitch=-80 的 R 矩阵，看模块 A 期望法线 vs B 观测法线"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np

def euler_zyx(yaw_deg, pitch_deg, roll_deg=0.0):
    """Z-Y-X 内旋（与 geometry.py:16-38 / render_geometry_passes 一致）"""
    y, p, r = np.radians([yaw_deg, pitch_deg, roll_deg])
    cy, sy = np.cos(y), np.sin(y)
    cp, sp = np.cos(p), np.sin(p)
    cr, sr = np.cos(r), np.sin(r)
    Rz = np.array([[cy,-sy,0],[sy,cy,0],[0,0,1]])
    Ry = np.array([[cp,0,sp],[0,1,0],[-sp,0,cp]])
    Rx = np.array([[1,0,0],[0,cr,-sr],[0,sr,cr]])
    return Rz @ Ry @ Rx

# 三类基础体面元法线（卫星本体坐标系 +X / +Y / +Z）
test_attitudes = [
    (0.0, -90.0),    # smoke
    (180.0, -30.0),  # 误差最小 0.05%
    (150.0, -80.0),  # 误差最大 950%
    (90.0, 0.0),     # 误差 55%
    (180.0, 0.0),    # 误差 1.8%
]

for yaw, pitch in test_attitudes:
    R = euler_zyx(yaw, pitch)
    print(f"\n=== yaw={yaw}/pitch={pitch} ===")
    print(f"R = \n{R}")
    print(f"  body +X → world {R @ [1,0,0]}")
    print(f"  body +Y → world {R @ [0,1,0]}")
    print(f"  body +Z → world {R @ [0,0,1]}")
    print(f"  body -X → world {R @ [-1,0,0]}")
    print(f"  body -Y → world {R @ [0,-1,0]}")
    print(f"  body -Z → world {R @ [0,0,-1]}")

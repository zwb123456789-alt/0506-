# -*- coding: utf-8 -*-
"""
verify_brdf_integration.py —— 验证模块 A 接入 brdf_models 后数值一致性

对比：
- 旧公式：f_r = rho_d/π + rho_s * (n·h)^n（直接内嵌）
- 新公式：eval_brdf(N, L, V, mat)（调用统一模块）

期望：相对误差 < 1e-6
"""

import sys
import io
import os
import numpy as np

# Windows UTF-8 输出
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "01_code"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "07_brdf"))

from materials import get_material
from brdf_models import eval_brdf


def old_brdf_formula(N, L, V, mat):
    """旧公式：模块 A 接入前的内嵌 BRDF 实现。"""
    h_vec = L + V
    h_norm = np.linalg.norm(h_vec)
    h_vec = h_vec / h_norm if h_norm > 0 else np.zeros(3)
    cos_alpha = np.maximum(np.dot(N, h_vec), 0.0)
    return (mat["rho_d"] / np.pi) + mat["rho_s"] * (cos_alpha ** mat["n"])


def main():
    print("=" * 70)
    print("BRDF 接入数值一致性验证")
    print("=" * 70)

    # 测试场景：随机姿态 + 随机法向
    np.random.seed(42)
    n_faces = 1000

    # 随机单位法向量
    N = np.random.randn(n_faces, 3)
    N = N / np.linalg.norm(N, axis=1, keepdims=True)

    # 固定太阳/探测器方向（与 ocs_scan.json 一致）
    L = np.array([1.0, 0.0, 0.3])
    L = L / np.linalg.norm(L)
    V = np.array([0.5, -1.0, 0.1])
    V = V / np.linalg.norm(V)

    max_diff = 0.0
    for part in ["jinshuzhuti", "taiyangnengban", "yinshenban"]:
        mat = get_material(part)

        # 旧公式（仅 rho_d/rho_s/n）
        mat_old = {"rho_d": mat["rho_d"], "rho_s": mat["rho_s"], "n": mat["n"]}
        brdf_old = old_brdf_formula(N, L, V, mat_old)

        # 新公式（eval_brdf）
        brdf_new = eval_brdf(N, L, V, mat)

        # 关键：旧公式不做可见性筛选，新公式做了。所以只对比可见面元。
        NoL = np.dot(N, L)
        NoV = np.dot(N, V)
        visible = (NoL > 0) & (NoV > 0)

        diff = np.abs(brdf_old[visible] - brdf_new[visible])
        rel_diff = diff / (np.abs(brdf_old[visible]) + 1e-12)

        print(f"\n[{part}]")
        print(f"  rho_d={mat['rho_d']}, rho_s={mat['rho_s']}, n={mat['n']}")
        print(f"  可见面元数: {visible.sum()}/{n_faces}")
        print(f"  绝对误差 max: {diff.max():.3e}")
        print(f"  相对误差 max: {rel_diff.max():.3e}")
        print(f"  brdf_old 范围: [{brdf_old[visible].min():.6f}, {brdf_old[visible].max():.6f}]")
        print(f"  brdf_new 范围: [{brdf_new[visible].min():.6f}, {brdf_new[visible].max():.6f}]")

        max_diff = max(max_diff, rel_diff.max())

    print("\n" + "=" * 70)
    if max_diff < 1e-6:
        print(f"✅ 验收通过：最大相对误差 {max_diff:.3e} < 1e-6")
    else:
        print(f"❌ 验收失败：最大相对误差 {max_diff:.3e} >= 1e-6")
    print("=" * 70)


if __name__ == "__main__":
    main()

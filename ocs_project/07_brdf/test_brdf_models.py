# -*- coding: utf-8 -*-
"""
test_brdf_models.py —— BRDF 模块数学单元测试
==========================
验证 brdf_models.py 中所有 BRDF 函数的数学正确性。

运行方式：
    conda activate ocs_sim
    cd ocs_project/07_brdf
    python test_brdf_models.py
"""

import sys
import io
import numpy as np

# Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 添加父目录到路径
sys.path.insert(0, "..")

from brdf_models import (
    eval_legacy_phong,
    eval_normalized_phong,
    eval_ggx_cook_torrance,
    eval_brdf,
    D_GGX,
    G_Smith_GGX,
    F_Schlick,
)

def test_legacy_phong():
    """测试 LegacyPhong BRDF。"""
    print("\n[测试] LegacyPhong")

    # 测试用例 1：正常角度
    N = np.array([0.0, 0.0, 1.0])
    L = np.array([0.0, 0.0, 1.0])  # 垂直入射
    V = np.array([0.0, 0.0, 1.0])  # 垂直观测
    rho_d, rho_s, n = 0.20, 0.60, 80

    f_r = eval_legacy_phong(N, L, V, rho_d, rho_s, n)
    expected = (rho_d / np.pi) + rho_s * 1.0 ** n  # NoH = 1
    assert np.isclose(f_r, expected), f"垂直入射失败: {f_r} != {expected}"
    print(f"  ✓ 垂直入射: f_r = {f_r:.6f}")

    # 测试用例 2：掠射角
    L = np.array([0.99, 0.0, 0.14])  # NoL ≈ 0.14
    L = L / np.linalg.norm(L)
    V = np.array([0.0, 0.0, 1.0])

    f_r = eval_legacy_phong(N, L, V, rho_d, rho_s, n)
    assert f_r >= 0, f"掠射角负值: {f_r}"
    assert not np.isnan(f_r), "掠射角 NaN"
    assert not np.isinf(f_r), "掠射角 Inf"
    print(f"  ✓ 掠射角: f_r = {f_r:.6f}")

    # 测试用例 3：不可见（NoL < 0）
    L = np.array([0.0, 0.0, -1.0])  # 背面
    f_r = eval_legacy_phong(N, L, V, rho_d, rho_s, n)
    assert f_r == 0.0, f"背面应返回 0: {f_r}"
    print(f"  ✓ 背面不可见: f_r = {f_r:.6f}")

    # 测试用例 4：批量计算
    N_batch = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1]])
    L_batch = np.array([[0, 0, 1], [1, 0, 0], [0, 0, -1]])
    V_batch = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1]])

    f_r_batch = eval_legacy_phong(N_batch, L_batch, V_batch, rho_d, rho_s, n)
    assert f_r_batch.shape == (3,), f"批量形状错误: {f_r_batch.shape}"
    assert f_r_batch[0] > 0, "批量第 1 个应可见"
    assert f_r_batch[2] == 0, "批量第 3 个应不可见"
    print(f"  ✓ 批量计算: shape={f_r_batch.shape}, values={f_r_batch}")

    print("  [PASS] LegacyPhong 所有测试通过")


def test_normalized_phong():
    """测试 NormalizedPhong BRDF。"""
    print("\n[测试] NormalizedPhong")

    N = np.array([0.0, 0.0, 1.0])
    L = np.array([0.0, 0.0, 1.0])
    V = np.array([0.0, 0.0, 1.0])
    rho_d, rho_s, n = 0.20, 0.60, 80

    f_r = eval_normalized_phong(N, L, V, rho_d, rho_s, n)
    normalization = (n + 2.0) / (2.0 * np.pi)
    expected = (rho_d / np.pi) + rho_s * normalization * 1.0 ** n
    assert np.isclose(f_r, expected), f"归一化失败: {f_r} != {expected}"
    print(f"  ✓ 垂直入射: f_r = {f_r:.6f} (归一化项 = {normalization:.6f})")

    # 验证归一化项确实不同于 LegacyPhong
    f_r_legacy = eval_legacy_phong(N, L, V, rho_d, rho_s, n)
    assert not np.isclose(f_r, f_r_legacy), "归一化应与 Legacy 不同"
    print(f"  ✓ 与 LegacyPhong 不同: {f_r:.6f} vs {f_r_legacy:.6f}")

    print("  [PASS] NormalizedPhong 所有测试通过")


def test_ggx_components():
    """测试 GGX 组件函数。"""
    print("\n[测试] GGX 组件")

    # D_GGX
    NoH = 1.0
    alpha = 0.04  # roughness=0.2
    D = D_GGX(NoH, alpha)
    assert D > 0, f"D_GGX 应为正: {D}"
    assert not np.isnan(D), "D_GGX NaN"
    print(f"  ✓ D_GGX(NoH=1.0, alpha=0.04) = {D:.6f}")

    # G_Smith_GGX
    NoL, NoV = 0.8, 0.9
    G = G_Smith_GGX(NoL, NoV, alpha)
    assert 0 <= G <= 1, f"G_Smith_GGX 应在 [0,1]: {G}"
    print(f"  ✓ G_Smith_GGX(NoL=0.8, NoV=0.9, alpha=0.04) = {G:.6f}")

    # F_Schlick
    VoH = 0.9
    F0 = 0.91  # 铝
    F = F_Schlick(VoH, F0)
    assert F0 <= F <= 1.0, f"F_Schlick 应在 [F0, 1]: {F}"
    print(f"  ✓ F_Schlick(VoH=0.9, F0=0.91) = {F:.6f}")

    print("  [PASS] GGX 组件所有测试通过")


def test_ggx_cook_torrance():
    """测试 GGX/Cook-Torrance BRDF。"""
    print("\n[测试] GGX/Cook-Torrance")

    # 测试用例 1：金属（铝）
    N = np.array([0.0, 0.0, 1.0])
    L = np.array([0.0, 0.0, 1.0])
    V = np.array([0.0, 0.0, 1.0])
    base_color = 0.91
    metallic = 1.0
    roughness = 0.20
    F0 = 0.91

    f_r = eval_ggx_cook_torrance(N, L, V, base_color, metallic, roughness, F0=F0)
    assert f_r > 0, f"金属 BRDF 应为正: {f_r}"
    assert not np.isnan(f_r), "金属 BRDF NaN"
    assert not np.isinf(f_r), "金属 BRDF Inf"
    print(f"  ✓ 金属（铝）: f_r = {f_r:.6f}")

    # 测试用例 2：电介质（玻璃）
    base_color = 0.15
    metallic = 0.0
    roughness = 0.40
    ior = 1.5

    f_r = eval_ggx_cook_torrance(N, L, V, base_color, metallic, roughness, ior=ior)
    assert f_r > 0, f"电介质 BRDF 应为正: {f_r}"
    print(f"  ✓ 电介质（玻璃）: f_r = {f_r:.6f}")

    # 测试用例 3：极端粗糙度
    roughness = 0.02  # 最小值
    f_r_smooth = eval_ggx_cook_torrance(N, L, V, base_color, metallic, roughness, ior=ior)
    assert f_r_smooth > 0, "极端光滑失败"
    print(f"  ✓ 极端光滑 (roughness=0.02): f_r = {f_r_smooth:.6f}")

    roughness = 1.0  # 最大值
    f_r_rough = eval_ggx_cook_torrance(N, L, V, base_color, metallic, roughness, ior=ior)
    assert f_r_rough > 0, "极端粗糙失败"
    print(f"  ✓ 极端粗糙 (roughness=1.0): f_r = {f_r_rough:.6f}")

    # 测试用例 4：不可见（NoL < 0）
    L = np.array([0.0, 0.0, -1.0])
    f_r = eval_ggx_cook_torrance(N, L, V, base_color, metallic, 0.5, ior=ior)
    assert f_r == 0.0, f"背面应返回 0: {f_r}"
    print(f"  ✓ 背面不可见: f_r = {f_r:.6f}")

    print("  [PASS] GGX/Cook-Torrance 所有测试通过")


def test_eval_brdf():
    """测试统一入口 eval_brdf。"""
    print("\n[测试] eval_brdf 统一入口")

    N = np.array([0.0, 0.0, 1.0])
    L = np.array([0.0, 0.0, 1.0])
    V = np.array([0.0, 0.0, 1.0])

    # LegacyPhong
    mat_legacy = {
        "brdf_model": "legacy_phong",
        "rho_d": 0.20,
        "rho_s": 0.60,
        "n": 80,
    }
    f_r_legacy = eval_brdf(N, L, V, mat_legacy)
    f_r_direct = eval_legacy_phong(N, L, V, 0.20, 0.60, 80)
    assert np.isclose(f_r_legacy, f_r_direct), "LegacyPhong 分发失败"
    print(f"  ✓ LegacyPhong 分发: f_r = {f_r_legacy:.6f}")

    # GGX
    mat_ggx = {
        "brdf_model": "ggx",
        "base_color": 0.91,
        "metallic": 1.0,
        "roughness": 0.20,
        "F0": 0.91,
    }
    f_r_ggx = eval_brdf(N, L, V, mat_ggx)
    f_r_direct = eval_ggx_cook_torrance(N, L, V, 0.91, 1.0, 0.20, F0=0.91)
    assert np.isclose(f_r_ggx, f_r_direct), "GGX 分发失败"
    print(f"  ✓ GGX 分发: f_r = {f_r_ggx:.6f}")

    # 未知模型
    mat_unknown = {"brdf_model": "unknown"}
    try:
        eval_brdf(N, L, V, mat_unknown)
        assert False, "应抛出 ValueError"
    except ValueError as e:
        print(f"  ✓ 未知模型异常: {e}")

    print("  [PASS] eval_brdf 所有测试通过")


def test_extreme_angles():
    """测试极端角度稳定性。"""
    print("\n[测试] 极端角度稳定性")

    N = np.array([0.0, 0.0, 1.0])
    V = np.array([0.0, 0.0, 1.0])

    # 极端掠射角
    angles = [0.01, 0.0001]
    for theta in angles:
        L = np.array([np.sin(theta), 0.0, np.cos(theta)])
        L = L / np.linalg.norm(L)

        # LegacyPhong
        f_r = eval_legacy_phong(N, L, V, 0.20, 0.60, 80)
        assert not np.isnan(f_r), f"LegacyPhong NaN at theta={theta}"
        assert not np.isinf(f_r), f"LegacyPhong Inf at theta={theta}"

        # GGX
        f_r = eval_ggx_cook_torrance(N, L, V, 0.91, 1.0, 0.20, F0=0.91)
        assert not np.isnan(f_r), f"GGX NaN at theta={theta}"
        assert not np.isinf(f_r), f"GGX Inf at theta={theta}"

    print(f"  ✓ 极端掠射角稳定 (theta={angles})")

    # 零向量保护
    L_zero = np.array([0.0, 0.0, 0.0])
    f_r = eval_legacy_phong(N, L_zero, V, 0.20, 0.60, 80)
    assert f_r == 0.0, "零向量应返回 0"
    print(f"  ✓ 零向量保护: f_r = {f_r:.6f}")

    print("  [PASS] 极端角度所有测试通过")


def main():
    """运行所有测试。"""
    print("=" * 70)
    print("BRDF 模块数学单元测试")
    print("=" * 70)

    try:
        test_legacy_phong()
        test_normalized_phong()
        test_ggx_components()
        test_ggx_cook_torrance()
        test_eval_brdf()
        test_extreme_angles()

        print("\n" + "=" * 70)
        print("✅ 所有测试通过")
        print("=" * 70)

    except AssertionError as e:
        print("\n" + "=" * 70)
        print(f"❌ 测试失败: {e}")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()

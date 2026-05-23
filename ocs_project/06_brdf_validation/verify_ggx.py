# -*- coding: utf-8 -*-
"""
verify_ggx.py —— GGX/Cook-Torrance 小规模验证（canonical EXR 管线）
====================================================================
复用 Blender MULTILAYER EXR，单次读取并行计算 LegacyPhong 与 GGX 两种 BRDF 的 OCS。

验证重点：
  1. LegacyPhong 不回归（与已知结果一致）
  2. GGX 数值稳定（无 NaN/Inf/负值）
  3. GGX 物理合理性（metallic=1 → diffuse=0, 所有分量 >= 0）
  4. LegacyPhong vs GGX 差异趋势合理

用法：
  conda activate ocs_sim
  PYTHONIOENCODING=utf-8 python ocs_project/06_brdf_validation/verify_ggx.py --exr-dir <路径>
"""

import os, sys, json, csv, argparse, time as time_module
from pathlib import Path
import numpy as np

# 路径设置
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/01_code"))
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/07_brdf"))
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/02_blender"))

from brdf_models import (
    eval_legacy_phong, eval_ggx_cook_torrance,
    MATERIAL_DB_LEGACY, MATERIAL_DB_GGX,
    D_GGX, G_Smith_GGX, F_Schlick,
    PI, ROUGHNESS_MIN, EPS,
)
from brdf_postprocess import read_multilayer_exr, PART_PASS_INDEX, DEPTH_BG_THRESHOLD

# ---- GGX 材料映射 ----
def map_to_ggx_material(part_name):
    """将任意部件名映射到 GGX nominal 材料参数。"""
    if part_name in MATERIAL_DB_GGX:
        return MATERIAL_DB_GGX[part_name].copy()
    # 测试几何（flat_plate, Cube, Plate_H, Plate_V 等）→ 默认用金属主体参数
    return MATERIAL_DB_GGX["jinshuzhuti"].copy()


# ---- 核心：单 EXR 双 BRDF 计算 ----
def compute_ocs_both(exr_path, sun_dir, det_dir, materials_legacy, part_pass_index,
                     resolution, r_max):
    """
    从单个 MULTILAYER EXR 并行计算 LegacyPhong 与 GGX 的 per-part OCS。

    参数:
        exr_path: EXR 文件路径
        sun_dir, det_dir: (3,) 单位向量
        materials_legacy: {part_name: {rho_d, rho_s, n, brdf_model}}
        part_pass_index: {part_name: pass_index}
        resolution, r_max: 渲染参数

    返回:
        dict 含 per-part 与 total OCS、像素统计、数值健康检查
    """
    ortho_scale = 2.2 * r_max
    pixel_area = (ortho_scale / resolution) ** 2

    layers = read_multilayer_exr(str(exr_path))
    H, W = layers["_size"]

    N_world = layers["Normal"].astype(np.float64)
    depth = layers["Depth"]
    idx = layers["IndexOB"].astype(np.int32)

    # 物体像素
    mask_obj = (depth < DEPTH_BG_THRESHOLD) & (idx > 0)

    # 背面遮罩（如有）
    backfacing = layers.get("Backfacing")
    if backfacing is not None:
        mask_obj = mask_obj & (backfacing < 0.5)

    # 法线归一化
    n_norm = np.linalg.norm(N_world, axis=-1, keepdims=True)
    n_norm = np.where(n_norm > 1e-8, n_norm, 1.0)
    N_world = N_world / n_norm

    L = np.array(sun_dir, dtype=np.float64)
    V = np.array(det_dir, dtype=np.float64)

    # 半程向量（用于 per-pixel 诊断）
    H_vec = L + V
    H_vec /= np.linalg.norm(H_vec)

    results = {
        "legacy": {"total": 0.0, "parts": {}},
        "ggx":    {"total": 0.0, "parts": {}},
        "pixels": {},
        "health": {
            "ggx_nan_count": 0, "ggx_inf_count": 0, "ggx_neg_count": 0,
            "ggx_D_nan": 0, "ggx_G_nan": 0, "ggx_F_nan": 0,
            "legacy_nan_count": 0, "legacy_neg_count": 0,
        },
        "pixel_stats": {},  # per-part per-model stats
    }

    for part_name, mat_legacy in materials_legacy.items():
        pid = part_pass_index.get(part_name)
        if pid is None:
            continue

        m_part = mask_obj & (idx == pid)
        n_pix = int(m_part.sum())
        results["pixels"][part_name] = n_pix
        if n_pix == 0:
            results["legacy"]["parts"][part_name] = 0.0
            results["ggx"]["parts"][part_name] = 0.0
            continue

        N_pix_all = N_world[m_part]

        # NoV > 0 过滤
        NoV_all = np.einsum("ij,j->i", N_pix_all, V)
        front = NoV_all > 0
        if not front.any():
            results["legacy"]["parts"][part_name] = 0.0
            results["ggx"]["parts"][part_name] = 0.0
            results["pixels"][part_name] = 0
            continue

        N_pix = N_pix_all[front]
        n_front = len(N_pix)
        results["pixels"][part_name] = n_front

        L_bc = np.broadcast_to(L, N_pix.shape).copy()
        V_bc = np.broadcast_to(V, N_pix.shape).copy()

        # ---- LegacyPhong ----
        f_r_legacy = eval_legacy_phong(
            N_pix, L_bc, V_bc,
            mat_legacy["rho_d"], mat_legacy["rho_s"], mat_legacy["n"]
        )
        NoL = np.maximum(np.einsum("ij,j->i", N_pix, L), 0.0)
        rad_legacy = f_r_legacy * NoL
        ocs_legacy = float(np.sum(rad_legacy) * pixel_area)

        # 健康检查
        results["health"]["legacy_nan_count"] += int(np.sum(~np.isfinite(f_r_legacy)))
        results["health"]["legacy_neg_count"] += int(np.sum(f_r_legacy < 0))

        # ---- GGX ----
        mat_ggx = map_to_ggx_material(part_name)
        f_r_ggx = eval_ggx_cook_torrance(
            N_pix, L_bc, V_bc,
            mat_ggx["base_color"], mat_ggx["metallic"], mat_ggx["roughness"],
            F0=mat_ggx.get("F0"), ior=mat_ggx.get("ior")
        )
        rad_ggx = f_r_ggx * NoL
        ocs_ggx = float(np.sum(rad_ggx) * pixel_area)

        # GGX 组件级诊断
        roughness = max(mat_ggx["roughness"], ROUGHNESS_MIN)
        alpha = roughness * roughness
        NoH = np.maximum(np.einsum("ij,j->i", N_pix, H_vec), 0.0)
        VoH = np.maximum(np.einsum("ij,j->i", V_bc, H_vec), 0.0)
        NoV_f = np.maximum(np.einsum("ij,j->i", N_pix, V), 0.0)

        F0_val = mat_ggx.get("F0")
        if F0_val is None:
            ior_val = mat_ggx.get("ior", 1.5)
            F0_val = ((ior_val - 1.0) / (ior_val + 1.0)) ** 2

        D_val = D_GGX(NoH, alpha)
        G_val = G_Smith_GGX(NoL, NoV_f, alpha)
        F_val = F_Schlick(VoH, F0_val)

        results["health"]["ggx_nan_count"] += int(np.sum(~np.isfinite(f_r_ggx)))
        results["health"]["ggx_inf_count"] += int(np.sum(np.isinf(f_r_ggx)))
        results["health"]["ggx_neg_count"] += int(np.sum(f_r_ggx < 0))
        results["health"]["ggx_D_nan"] += int(np.sum(~np.isfinite(D_val)))
        results["health"]["ggx_G_nan"] += int(np.sum(~np.isfinite(G_val)))
        results["health"]["ggx_F_nan"] += int(np.sum(~np.isfinite(F_val)))

        # 物理约束检查
        f_diffuse_ggx = (1.0 - mat_ggx["metallic"]) * (mat_ggx["base_color"] / PI)
        diffuse_zero_if_metal = (mat_ggx["metallic"] == 1.0 and abs(f_diffuse_ggx) < 1e-15)

        results["legacy"]["parts"][part_name] = ocs_legacy
        results["legacy"]["total"] += ocs_legacy
        results["ggx"]["parts"][part_name] = ocs_ggx
        results["ggx"]["total"] += ocs_ggx

        # per-pixel 统计
        results["pixel_stats"][part_name] = {
            "n_pixels": n_front,
            "legacy": {
                "f_r_mean": float(np.mean(f_r_legacy)),
                "f_r_median": float(np.median(f_r_legacy)),
                "f_r_min": float(np.min(f_r_legacy)),
                "f_r_max": float(np.max(f_r_legacy)),
            },
            "ggx": {
                "f_r_mean": float(np.mean(f_r_ggx)),
                "f_r_median": float(np.median(f_r_ggx)),
                "f_r_min": float(np.min(f_r_ggx)),
                "f_r_max": float(np.max(f_r_ggx)),
                "D_mean": float(np.mean(D_val)),
                "G_mean": float(np.mean(G_val)),
                "F_mean": float(np.mean(F_val)),
                "D_max": float(np.max(D_val)),
                "f_diffuse": float(f_diffuse_ggx),
                "diffuse_zero_if_metal": diffuse_zero_if_metal,
            },
            "shared": {
                "NoL_mean": float(np.mean(NoL)),
                "NoV_mean": float(np.mean(NoV_f)),
                "NoH_mean": float(np.mean(NoH)),
                "NoL_min": float(np.min(NoL)),
                "NoH_max": float(np.max(NoH)),
            },
        }

    return results


# ---- 主流程 ----
def parse_args():
    p = argparse.ArgumentParser(description="GGX/Cook-Torrance 小规模验证")
    p.add_argument("--exr-dir", required=True, help="EXR 目录（含 render_metadata.json）")
    p.add_argument("--output", default=None, help="输出目录（默认 EXR 目录下创建 ggx_verify/）")
    return p.parse_args()


def find_exrs(exr_dir):
    return sorted(Path(exr_dir).glob("*_0001.exr"))


def attitude_key(exr_path):
    s = exr_path.name
    if s.endswith("_0001.exr"):
        return s[:-len("_0001.exr")]
    return exr_path.stem


def main():
    args = parse_args()
    exr_dir = Path(args.exr_dir)
    meta_path = exr_dir / "render_metadata.json"
    if not meta_path.exists():
        print(f"[FAIL] 未找到 {meta_path}")
        sys.exit(1)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)
    materials_legacy = meta["materials"]
    resolution = int(meta["resolution"])
    r_max = float(meta["r_max"])

    # 构建 pass_index（兼容单材料/多材料）
    part_pass_index = {}
    for i, pn in enumerate(materials_legacy.keys(), start=1):
        if pn in PART_PASS_INDEX:
            part_pass_index[pn] = PART_PASS_INDEX[pn]
        else:
            part_pass_index[pn] = i

    # 输出目录
    if args.output:
        out_dir = Path(args.output)
    else:
        out_dir = exr_dir / "ggx_verify"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("  GGX / Cook-Torrance 小规模验证")
    print("=" * 72)
    print(f"  EXR 目录:   {exr_dir}")
    print(f"  输出目录:   {out_dir}")
    print(f"  sun:        {sun_dir}")
    print(f"  det:        {det_dir}")
    print(f"  分辨率:     {resolution}")
    print(f"  r_max:      {r_max:.4f} m")
    print(f"  部件:       {list(materials_legacy.keys())}")
    for pn, ml in materials_legacy.items():
        mg = map_to_ggx_material(pn)
        print(f"    {pn}:")
        print(f"      Legacy → ρ_d={ml['rho_d']}, ρ_s={ml['rho_s']}, n={ml['n']}")
        print(f"      GGX    → metallic={mg['metallic']}, roughness={mg['roughness']}, "
              f"base_color={mg['base_color']}, F0={mg.get('F0', 'N/A')}")

    exr_files = find_exrs(exr_dir)
    print(f"\n  找到 {len(exr_files)} 个 EXR 文件")
    if not exr_files:
        print("[FAIL] 无 EXR 文件")
        sys.exit(1)

    rows = []
    all_healthy = True

    for ef in exr_files:
        t0 = time_module.perf_counter()
        key = attitude_key(ef)
        res = compute_ocs_both(ef, sun_dir, det_dir, materials_legacy,
                               part_pass_index, resolution, r_max)
        dt = time_module.perf_counter() - t0

        # 数值健康判定
        h = res["health"]
        healthy = (
            h["ggx_nan_count"] == 0 and h["ggx_inf_count"] == 0 and
            h["ggx_neg_count"] == 0 and h["legacy_nan_count"] == 0 and
            h["legacy_neg_count"] == 0
        )
        if not healthy:
            all_healthy = False

        # 构建行
        row = {
            "key": key,
            "ocs_legacy_total": res["legacy"]["total"],
            "ocs_ggx_total": res["ggx"]["total"],
            "ocs_ratio_ggx_div_legacy": (
                res["ggx"]["total"] / res["legacy"]["total"]
                if res["legacy"]["total"] > 1e-30 else float("nan")
            ),
            "healthy": healthy,
            "dt_sec": dt,
        }
        # per-part OCS
        for pn in materials_legacy:
            row[f"ocs_legacy_{pn}"] = res["legacy"]["parts"].get(pn, 0.0)
            row[f"ocs_ggx_{pn}"] = res["ggx"]["parts"].get(pn, 0.0)
            row[f"pixels_{pn}"] = res["pixels"].get(pn, 0)
        # 健康详情
        for hk, hv in h.items():
            row[f"health_{hk}"] = hv

        rows.append(row)

        # 控制台输出
        flag = "✓" if healthy else "✗ FAIL"
        print(f"\n  [{key:35s}]  {flag}  {dt:.2f}s")
        print(f"    OCS  Legacy={res['legacy']['total']:.6e}  "
              f"GGX={res['ggx']['total']:.6e}  "
              f"ratio={row['ocs_ratio_ggx_div_legacy']:.4f}")
        for pn in materials_legacy:
            ps = res["pixel_stats"].get(pn)
            if ps is None:
                continue
            print(f"    [{pn}] px={ps['n_pixels']}  "
                  f"Legacy f_r∈[{ps['legacy']['f_r_min']:.4f}, {ps['legacy']['f_r_max']:.4f}]  "
                  f"GGX f_r∈[{ps['ggx']['f_r_min']:.4f}, {ps['ggx']['f_r_max']:.4f}]")
            print(f"          NoL∈[{ps['shared']['NoL_min']:.4f}, {ps['shared']['NoL_mean']:.4f}]  "
                  f"NoH_max={ps['shared']['NoH_max']:.4f}  "
                  f"GGX D_max={ps['ggx']['D_max']:.2f}  "
                  f"diffuse={ps['ggx']['f_diffuse']:.4f}")

    # ---- 写 CSV ----
    csv_path = out_dir / "ggx_verification.csv"
    if rows:
        fieldnames = list(rows[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        print(f"\n  CSV: {csv_path}")

    # ---- 写 summary JSON ----
    summary = {
        "exr_dir": str(exr_dir),
        "output_dir": str(out_dir),
        "sun_direction": list(sun_dir),
        "det_direction": list(det_dir),
        "resolution": resolution,
        "r_max": r_max,
        "parts": list(materials_legacy.keys()),
        "n_exr": len(exr_files),
        "all_healthy": all_healthy,
        "ggx_materials": {pn: map_to_ggx_material(pn) for pn in materials_legacy},
        "per_attitude": [],
    }
    for r in rows:
        entry = {
            "key": r["key"],
            "ocs_legacy_total": r["ocs_legacy_total"],
            "ocs_ggx_total": r["ocs_ggx_total"],
            "ocs_ratio_ggx_div_legacy": r["ocs_ratio_ggx_div_legacy"],
            "healthy": r["healthy"],
        }
        for pn in materials_legacy:
            entry[f"ocs_legacy_{pn}"] = r.get(f"ocs_legacy_{pn}", 0.0)
            entry[f"ocs_ggx_{pn}"] = r.get(f"ocs_ggx_{pn}", 0.0)
        summary["per_attitude"].append(entry)

    # 统计
    ratios = [r["ocs_ratio_ggx_div_legacy"] for r in rows
              if r["ocs_ratio_ggx_div_legacy"] == r["ocs_ratio_ggx_div_legacy"]]
    if ratios:
        summary["ggx_legacy_ratio_mean"] = float(np.mean(ratios))
        summary["ggx_legacy_ratio_std"] = float(np.std(ratios))
        summary["ggx_legacy_ratio_min"] = float(np.min(ratios))
        summary["ggx_legacy_ratio_max"] = float(np.max(ratios))

    with open(out_dir / "ggx_verification_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  Summary: {out_dir / 'ggx_verification_summary.json'}")

    # ---- 终判 ----
    print(f"\n{'='*72}")
    print(f"  终判")
    print(f"  数值健康: {'PASS' if all_healthy else 'FAIL (存在 NaN/Inf/负值)'}")
    if ratios:
        print(f"  GGX/Legacy OCS ratio: mean={np.mean(ratios):.4f}  "
              f"std={np.std(ratios):.4f}  "
              f"range=[{np.min(ratios):.4f}, {np.max(ratios):.4f}]")
    print(f"  产物: {out_dir}")
    print("=" * 72)

    return 0 if all_healthy else 1


if __name__ == "__main__":
    sys.exit(main())

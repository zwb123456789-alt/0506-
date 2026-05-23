# -*- coding: utf-8 -*-
"""
run_plane_batch_validation.py —— 单平板多姿态三端闭合批量验证
================================================================
在一个 Blender 进程内渲染 5 个姿态，自动后处理，对比解析解 / A 端 / B 端 OCS。
同一组几何缓冲分别按 LegacyPhong full 和 diffuse-only (rho_s=0) 重算。

输出:
    plane_batch_validation.csv
    plane_batch_validation_report.md
    fig_plane_batch_compare.png
    config_used.json

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/06_brdf_validation/run_plane_batch_validation.py
"""
import os, sys, json, subprocess, tempfile, time as time_module
import numpy as np
from pathlib import Path

# 路径设置
PROJECT_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新")
BLENDER_EXE = r"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
BLENDER_SCRIPT = PROJECT_ROOT / "ocs_project/06_brdf_validation/render_flat_plate_batch.py"
STL_PATH = PROJECT_ROOT / "建模/flat_plate_1m2.stl"
PYTHON_EXE = r"C:\Users\97466\.conda\envs\ocs_sim\python.exe"

sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/01_code"))
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/07_brdf"))
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/02_blender"))

from config import SUN_VECTOR, DET_VECTOR
from geometry import euler_to_matrix
from brdf_models import eval_legacy_phong
from brdf_postprocess import read_multilayer_exr, compute_radiance_image, integrate_ocs, PART_PASS_INDEX

# ---- 常量 ----
ATTITUDES = [
    (0.0, 0.0),
    (0.0, -30.0),
    (90.0, -45.0),
    (150.0, -80.0),
    (180.0, 0.0),
]
MAT_FLAT = {"rho_d": 0.20, "rho_s": 0.60, "n": 80, "brdf_model": "legacy_phong"}
MAT_FLAT_DIFFUSE = {"rho_d": 0.20, "rho_s": 0.0, "n": 80, "brdf_model": "legacy_phong"}


# ---- 解析解 ----
def analytical_ocs(yaw, pitch, sun_vec, det_vec, mat, area_m2=1.0):
    sun_n = sun_vec / np.linalg.norm(sun_vec)
    det_n = det_vec / np.linalg.norm(det_vec)
    R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
    N_body = np.array([0.0, 0.0, 1.0])
    N = R @ N_body  # 第三列: body Z 在惯性系的方向（不是第三行 N_body@R）
    NoL = float(np.dot(N, sun_n))
    NoV = float(np.dot(N, det_n))
    if NoL <= 0 or NoV <= 0:
        return 0.0, {"NoL": NoL, "NoV": NoV, "f_r": 0.0, "N": N.tolist()}
    f_r = float(eval_legacy_phong(N, sun_n, det_n, mat["rho_d"], mat["rho_s"], mat["n"]))
    ocs = area_m2 * f_r * NoL * NoV
    return ocs, {"NoL": NoL, "NoV": NoV, "f_r": f_r, "N": N.tolist()}


# ---- A 端（trimesh）----
def run_a_side(yaw, pitch, mat, stl_path):
    """用 trimesh 加载 STL，逐面元计算 OCS（参考 flat_plate_closure.py）"""
    from geometry import load_meshes
    import materials as materials_mod

    orig_get = materials_mod.get_material
    def plate_get(name):
        if name == "flat_plate":
            return mat.copy()
        return orig_get(name)
    materials_mod.get_material = plate_get

    try:
        part_files = {"flat_plate": str(stl_path)}
        meshes, _ = load_meshes(part_files=part_files, accuracy_level="full", verbose=False)
        R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)

        sun_n = np.array(SUN_VECTOR, dtype=np.float64)
        det_n = np.array(DET_VECTOR, dtype=np.float64)
        sun_n /= np.linalg.norm(sun_n)
        det_n /= np.linalg.norm(det_n)

        mesh = meshes["flat_plate"]
        # 提取面元中心和法线（世界空间）
        if hasattr(mesh, 'triangles_center'):
            centers = np.array(mesh.triangles_center, dtype=np.float64)
        else:
            centers = np.array(mesh.vertices)[np.array(mesh.faces)].mean(axis=1)
        if hasattr(mesh, 'face_normals'):
            normals = np.array(mesh.face_normals, dtype=np.float64)
        else:
            v = np.array(mesh.vertices)
            f = np.array(mesh.faces)
            e1 = v[f[:, 1]] - v[f[:, 0]]
            e2 = v[f[:, 2]] - v[f[:, 0]]
            normals = np.cross(e1, e2)
            n = np.linalg.norm(normals, axis=1, keepdims=True)
            normals = normals / np.where(n > 1e-12, n, 1.0)

        # 旋转法线到惯性系
        N = normals @ R[:3, :3].T
        n_norm = np.linalg.norm(N, axis=1, keepdims=True)
        N = N / np.where(n_norm > 1e-12, n_norm, 1.0)

        # 面元面积：STL 顶点在 mm，转 m²
        if hasattr(mesh, 'area_faces'):
            area_m2 = np.array(mesh.area_faces, dtype=np.float64) * 1e-6
        else:
            area_m2 = np.full(len(N), 1.0 / len(N), dtype=np.float64)

        L_bc = np.broadcast_to(sun_n, N.shape).copy()
        V_bc = np.broadcast_to(det_n, N.shape).copy()
        f_r = eval_legacy_phong(N, L_bc, V_bc, mat["rho_d"], mat["rho_s"], mat["n"])
        NoL = np.maximum(np.einsum("ij,j->i", N, sun_n), 0.0)
        NoV = np.maximum(np.einsum("ij,j->i", N, det_n), 0.0)
        visible = (NoL > 0) & (NoV > 0)
        ocs = float(np.sum(area_m2[visible] * f_r[visible] * NoL[visible] * NoV[visible]))

        return ocs, {
            "n_faces": len(N),
            "n_visible": int(visible.sum()),
            "NoL_mean": float(NoL[visible].mean()) if visible.any() else 0.0,
            "NoV_mean": float(NoV[visible].mean()) if visible.any() else 0.0,
            "f_r_mean": float(f_r[visible].mean()) if visible.any() else 0.0,
        }
    finally:
        materials_mod.get_material = orig_get


# ---- B 端（EXR 后处理）----
def run_b_side(exr_path, meta, mat, mat_diffuse):
    """读单个 EXR，分别算 full & diffuse OCS"""
    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)

    r_max = meta["r_max"]
    res = meta["resolution"]
    ortho_scale = 2.2 * r_max
    pixel_area = (ortho_scale / res) ** 2

    layers = read_multilayer_exr(str(exr_path))
    H, W = layers["_size"]

    # Full (LegacyPhong)
    flat_mats = {"flat_plate": mat}
    flat_pass = {"flat_plate": 1}
    rad_full, mask_obj, pp_full = compute_radiance_image(
        layers, sun_dir, det_dir, flat_mats, flat_pass)
    ocs_full = integrate_ocs(rad_full, pixel_area)

    # Diffuse-only
    rad_diff, _, pp_diff = compute_radiance_image(
        layers, sun_dir, det_dir, {**flat_mats, "flat_plate": mat_diffuse}, flat_pass)
    ocs_diff = integrate_ocs(rad_diff, pixel_area)

    # Per-pixel stats
    N_pix = layers["Normal"].astype(np.float64)[mask_obj]
    nn = np.linalg.norm(N_pix, axis=-1, keepdims=True)
    N_pix = N_pix / np.where(nn > 1e-8, nn, 1.0)
    NoL_pix = np.clip(np.einsum("ij,j->i", N_pix, sun_dir), 0, None)
    NoV_pix = np.clip(np.einsum("ij,j->i", N_pix, det_dir), 0, None)
    H_vec = sun_dir + det_dir
    H_vec /= np.linalg.norm(H_vec)
    NoH_pix = np.clip(np.einsum("ij,j->i", N_pix, H_vec), 0, None)
    f_r_pix = np.array([float(eval_legacy_phong(n, sun_dir, det_dir,
                                                mat["rho_d"], mat["rho_s"], mat["n"]))
                        for n in N_pix])

    return {
        "ocs_full": ocs_full,
        "ocs_diffuse": ocs_diff,
        "n_pixels": int(mask_obj.sum()),
        "pixel_area": pixel_area,
        "NoL_mean": float(NoL_pix.mean()),
        "NoV_mean": float(NoV_pix.mean()),
        "NoH_mean": float(NoH_pix.mean()),
        "f_r_mean": float(f_r_pix.mean()),
        "f_r_median": float(np.median(f_r_pix)),
        "f_r_max": float(f_r_pix.max()),
        "normal_mean": [float(N_pix[:, 0].mean()), float(N_pix[:, 1].mean()), float(N_pix[:, 2].mean())],
    }


# ---- 主流程 ----
def main():
    print("=" * 70)
    print("  单平板多姿态三端闭合批量验证")
    print("=" * 70)

    sun_vec = np.array(SUN_VECTOR, dtype=np.float64)
    det_vec = np.array(DET_VECTOR, dtype=np.float64)
    sun_n = sun_vec / np.linalg.norm(sun_vec)
    det_n = det_vec / np.linalg.norm(det_vec)
    print(f"  sun: {sun_n}")
    print(f"  det: {det_n}")
    print(f"  材料: rho_d={MAT_FLAT['rho_d']}, rho_s={MAT_FLAT['rho_s']}, n={MAT_FLAT['n']}")
    print(f"  姿态: {len(ATTITUDES)} 个")

    # ---- Step 1: Blender 渲染 ----
    print(f"\n--- Step 1: Blender 批量渲染 ---")
    out_dir = PROJECT_ROOT / "结果/BRDF验证" / f"plane_batch_{time_module.strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        BLENDER_EXE, "--background", "--python", str(BLENDER_SCRIPT), "--",
        "--out-dir", str(out_dir), "--res", "128",
        "--stl", str(STL_PATH),
    ]
    print(f"  blender ...")
    t0 = time_module.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    dt_blender = time_module.time() - t0
    print(result.stdout)
    if result.returncode != 0:
        print(f"[FAIL] Blender 返回码 {result.returncode}")
        print(result.stderr)
        sys.exit(1)
    print(f"  Blender 完成: {dt_blender:.1f}s")

    meta_path = out_dir / "render_metadata.json"
    with open(meta_path, "r") as f:
        meta = json.load(f)

    # ---- Step 2: 后处理 + 三端对比 ----
    print(f"\n--- Step 2: 后处理 & 三端对比 ---")
    rows = []
    exrs = sorted(out_dir.glob("*_0001.exr"))
    print(f"  找到 {len(exrs)} 个 EXR")

    for exr_path in exrs:
        fname = exr_path.name.replace("_0001.exr", "")
        # 解析 yaw/pitch
        parts = fname.split("_")
        yaw_str = parts[0].replace("yaw", "")
        pitch_str = parts[1].replace("pitch", "")
        yaw = float(yaw_str)
        pitch = float(pitch_str)

        print(f"\n  [{fname}]")

        # 解析解 (full)
        ocs_an_full, info_an = analytical_ocs(yaw, pitch, sun_vec, det_vec, MAT_FLAT)
        # 解析解 (diffuse)
        ocs_an_diff, info_an_diff = analytical_ocs(yaw, pitch, sun_vec, det_vec, MAT_FLAT_DIFFUSE)

        # A 端 (full)
        ocs_a_full, info_a = run_a_side(yaw, pitch, MAT_FLAT, STL_PATH)
        # A 端 (diffuse)
        ocs_a_diff, info_a_diff = run_a_side(yaw, pitch, MAT_FLAT_DIFFUSE, STL_PATH)

        # B 端 (full + diffuse from same EXR)
        info_b = run_b_side(exr_path, meta, MAT_FLAT, MAT_FLAT_DIFFUSE)

        # 相对误差 (以解析解为基准)
        def rel_err(val, ref):
            denom = max(abs(ref), 1e-30)
            return abs(val - ref) / denom if denom > 1e-30 else float("nan")

        r = {
            "yaw": yaw, "pitch": pitch,
            # Full
            "ocs_analytical_full": ocs_an_full,
            "ocs_A_full": ocs_a_full,
            "ocs_B_full": info_b["ocs_full"],
            "rel_A_vs_analyt_full": rel_err(ocs_a_full, ocs_an_full),
            "rel_B_vs_analyt_full": rel_err(info_b["ocs_full"], ocs_an_full),
            "rel_B_vs_A_full": rel_err(info_b["ocs_full"], ocs_a_full),
            # Diffuse-only
            "ocs_analytical_diffuse": ocs_an_diff,
            "ocs_A_diffuse": ocs_a_diff,
            "ocs_B_diffuse": info_b["ocs_diffuse"],
            "rel_A_vs_analyt_diff": rel_err(ocs_a_diff, ocs_an_diff),
            "rel_B_vs_analyt_diff": rel_err(info_b["ocs_diffuse"], ocs_an_diff),
            "rel_B_vs_A_diff": rel_err(info_b["ocs_diffuse"], ocs_a_diff),
            # B-side details
            "B_n_pixels": info_b["n_pixels"],
            "B_NoL_mean": info_b["NoL_mean"],
            "B_NoV_mean": info_b["NoV_mean"],
            "B_NoH_mean": info_b["NoH_mean"],
            "B_f_r_mean": info_b["f_r_mean"],
            "B_f_r_median": info_b["f_r_median"],
            "B_f_r_max": info_b["f_r_max"],
            "B_normal_mean": info_b["normal_mean"],
            # A-side details
            "A_n_faces": info_a.get("n_faces", 0),
            "A_n_visible": info_a.get("n_visible", 0),
            # Analytical details
            "an_NoL": info_an.get("NoL", 0),
            "an_NoV": info_an.get("NoV", 0),
            "an_f_r": info_an.get("f_r", 0),
        }
        rows.append(r)

        print(f"    Full:      analyt={ocs_an_full:.6e}  A={ocs_a_full:.6e}  B={info_b['ocs_full']:.6e}")
        print(f"    Diffuse:   analyt={ocs_an_diff:.6e}  A={ocs_a_diff:.6e}  B={info_b['ocs_diffuse']:.6e}")
        print(f"    B pixels={info_b['n_pixels']}  NoL={info_b['NoL_mean']:.4f}  NoV={info_b['NoV_mean']:.4f}  f_r={info_b['f_r_mean']:.4f}")

    # ---- Step 3: 写 CSV ----
    csv_path = out_dir / "plane_batch_validation.csv"
    fieldnames = list(rows[0].keys()) if rows else []
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\n  CSV: {csv_path}")

    # ---- Step 4: 报告 ----
    report = []
    report.append("# 单平板多姿态三端闭合验证报告")
    report.append("")
    report.append(f"**运行时间**: {time_module.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Blender 耗时**: {dt_blender:.1f}s")
    report.append("")
    report.append("## 参数")
    report.append("")
    report.append(f"- 平板: 1m×1m, STL: `{STL_PATH}`")
    report.append(f"- 材料: ρ_d={MAT_FLAT['rho_d']}, ρ_s={MAT_FLAT['rho_s']}, n={MAT_FLAT['n']} (LegacyPhong)")
    report.append(f"- sun: `{list(sun_n)}`")
    report.append(f"- det: `{list(det_n)}`")
    report.append(f"- 分辨率: {meta['resolution']}×{meta['resolution']}")
    report.append(f"- ortho_scale: {meta['ortho_scale']:.4f} m")
    report.append("")

    report.append("## 结果总表")
    report.append("")
    report.append("| yaw | pitch | analyt_full | A_full | B_full | rel_A% | rel_B% | analyt_diff | A_diff | B_diff | rel_A_diff% | rel_B_diff% | B_pix |")
    report.append("|-----|-------|------------|--------|--------|--------|--------|-------------|--------|--------|-------------|-------------|-------|")
    for r in rows:
        report.append(
            f"| {r['yaw']:5.0f} | {r['pitch']:+6.0f} | {r['ocs_analytical_full']:.6e} | {r['ocs_A_full']:.6e} | {r['ocs_B_full']:.6e} | "
            f"{r['rel_A_vs_analyt_full']*100:.2f} | {r['rel_B_vs_analyt_full']*100:.2f} | "
            f"{r['ocs_analytical_diffuse']:.6e} | {r['ocs_A_diffuse']:.6e} | {r['ocs_B_diffuse']:.6e} | "
            f"{r['rel_A_vs_analyt_diff']*100:.2f} | {r['rel_B_vs_analyt_diff']*100:.2f} | "
            f"{r['B_n_pixels']} |"
        )
    report.append("")

    # 统计
    rel_a_fulls = [r["rel_A_vs_analyt_full"] for r in rows if r["ocs_analytical_full"] > 0]
    rel_b_fulls = [r["rel_B_vs_analyt_full"] for r in rows if r["ocs_analytical_full"] > 0]
    rel_a_diffs = [r["rel_A_vs_analyt_diff"] for r in rows if r["ocs_analytical_diffuse"] > 0]
    rel_b_diffs = [r["rel_B_vs_analyt_diff"] for r in rows if r["ocs_analytical_diffuse"] > 0]

    report.append("## 统计摘要")
    report.append("")
    report.append("### Full (LegacyPhong)")
    report.append("")
    report.append(f"- A vs analyt: mean={np.mean(rel_a_fulls)*100:.3f}%  max={np.max(rel_a_fulls)*100:.3f}%  min={np.min(rel_a_fulls)*100:.3f}%")
    report.append(f"- B vs analyt: mean={np.mean(rel_b_fulls)*100:.3f}%  max={np.max(rel_b_fulls)*100:.3f}%  min={np.min(rel_b_fulls)*100:.3f}%")
    report.append("")
    report.append("### Diffuse-only")
    report.append("")
    report.append(f"- A vs analyt: mean={np.mean(rel_a_diffs)*100:.3f}%  max={np.max(rel_a_diffs)*100:.3f}%  min={np.min(rel_a_diffs)*100:.3f}%")
    report.append(f"- B vs analyt: mean={np.mean(rel_b_diffs)*100:.3f}%  max={np.max(rel_b_diffs)*100:.3f}%  min={np.min(rel_b_diffs)*100:.3f}%")
    report.append("")

    # 逐姿态详情
    report.append("## 逐姿态详情")
    report.append("")
    for r in rows:
        report.append(f"### yaw={r['yaw']:.0f} pitch={r['pitch']:.0f}")
        report.append("")
        report.append(f"- 解析 NoL={r['an_NoL']:.4f}  NoV={r['an_NoV']:.4f}  f_r={r['an_f_r']:.4f}")
        report.append(f"- B 端 NoL_mean={r['B_NoL_mean']:.4f}  NoV_mean={r['B_NoV_mean']:.4f}  NoH_mean={r['B_NoH_mean']:.4f}")
        report.append(f"- B 端 f_r: mean={r['B_f_r_mean']:.4f}  median={r['B_f_r_median']:.4f}  max={r['B_f_r_max']:.4f}")
        report.append(f"- B 端法线均值: [{r['B_normal_mean'][0]:+.4f} {r['B_normal_mean'][1]:+.4f} {r['B_normal_mean'][2]:+.4f}]")
        report.append(f"- B 像素数: {r['B_n_pixels']}  A 可见面元: {r['A_n_visible']}")
        report.append("")

    report_path = out_dir / "plane_batch_validation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"  报告: {report_path}")

    # ---- Step 5: 图 ----
    print(f"\n--- Step 3: 生成对比图 ---")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # 中文支持
        try:
            plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
        except Exception:
            pass

        labels = [f"({r['yaw']:.0f},{r['pitch']:+.0f})" for r in rows]

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Single Flat Plate Three-End Closure Validation (LegacyPhong)", fontsize=14)

        # 左上: Full OCS
        ax = axes[0, 0]
        x = np.arange(len(rows))
        w = 0.25
        ax.bar(x - w, [r["ocs_analytical_full"] for r in rows], w, label="Analytical", color="gray", alpha=0.7)
        ax.bar(x, [r["ocs_A_full"] for r in rows], w, label="A (trimesh)", color="steelblue", alpha=0.7)
        ax.bar(x + w, [r["ocs_B_full"] for r in rows], w, label="B (Blender+PP)", color="darkorange", alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel("OCS (m²)")
        ax.set_title("Full LegacyPhong")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        # 右上: Full 相对误差
        ax = axes[0, 1]
        ax.bar(x - w/2, [r["rel_A_vs_analyt_full"]*100 for r in rows], w/2, label="A vs analyt", color="steelblue")
        ax.bar(x + w/2, [r["rel_B_vs_analyt_full"]*100 for r in rows], w/2, label="B vs analyt", color="darkorange")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel("Relative Error (%)")
        ax.set_title("Full: Relative Error vs Analytical")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        # 左下: Diffuse-only OCS
        ax = axes[1, 0]
        ax.bar(x - w, [r["ocs_analytical_diffuse"] for r in rows], w, label="Analytical", color="gray", alpha=0.7)
        ax.bar(x, [r["ocs_A_diffuse"] for r in rows], w, label="A (trimesh)", color="steelblue", alpha=0.7)
        ax.bar(x + w, [r["ocs_B_diffuse"] for r in rows], w, label="B (Blender+PP)", color="darkorange", alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel("OCS (m²)")
        ax.set_title("Diffuse-only (ρ_s=0)")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        # 右下: Diffuse 相对误差
        ax = axes[1, 1]
        ax.bar(x - w/2, [r["rel_A_vs_analyt_diff"]*100 for r in rows], w/2, label="A vs analyt", color="steelblue")
        ax.bar(x + w/2, [r["rel_B_vs_analyt_diff"]*100 for r in rows], w/2, label="B vs analyt", color="darkorange")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel("Relative Error (%)")
        ax.set_title("Diffuse-only: Relative Error vs Analytical")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        fig.tight_layout()
        fig_path = out_dir / "fig_plane_batch_compare.png"
        fig.savefig(fig_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  图: {fig_path}")
    except Exception as e:
        print(f"  [WARN] 图生成失败: {e}")

    # ---- config_used.json ----
    config = {
        "attitudes": [{"yaw": y, "pitch": p} for y, p in ATTITUDES],
        "material": MAT_FLAT,
        "sun_direction": list(sun_n),
        "det_direction": list(det_n),
        "stl_path": str(STL_PATH),
        "resolution": meta["resolution"],
        "r_max": meta["r_max"],
        "ortho_scale": meta["ortho_scale"],
        "blender_exe": BLENDER_EXE,
        "blender_script": str(BLENDER_SCRIPT),
        "output_dir": str(out_dir),
        "n_attitudes": len(ATTITUDES),
    }
    with open(out_dir / "config_used.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # ---- 终判 ----
    print(f"\n{'='*70}")
    print(f"  终判")
    full_pass = all(r["rel_B_vs_analyt_full"] < 0.02 for r in rows if r["ocs_analytical_full"] > 0)
    diff_pass = all(r["rel_B_vs_analyt_diff"] < 0.02 for r in rows if r["ocs_analytical_diffuse"] > 0)
    print(f"  Full B vs analyt:      {'PASS (<2%)' if full_pass else 'FAIL'}")
    print(f"  Diffuse B vs analyt:   {'PASS (<2%)' if diff_pass else 'FAIL'}")
    if rel_b_fulls:
        print(f"  Full mean rel_err = {np.mean(rel_b_fulls)*100:.3f}%")
    if rel_b_diffs:
        print(f"  Diffuse mean rel_err = {np.mean(rel_b_diffs)*100:.3f}%")
    print(f"  产物: {out_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()

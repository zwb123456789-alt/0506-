# -*- coding: utf-8 -*-
"""
run_L_plate_validation.py —— L 型双平板可见性语义对账
========================================================
两 1m×1m 平板呈 L 型（XY+Z / XZ+Y 各一块），在 5 个姿态上对比：
- 解析解（无遮挡 per-plate OCS）
- A 端 no_occ（逐面元 BRDF，无遮挡）
- A 端 with_occ（逐面元 BRDF + ray-cast 遮挡）
- B 端 per-part（EXR 后处理，按 IndexOB 分板）

输出: L_plate_validation.csv / L_plate_report.md / fig_L_plate_compare.png

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/06_brdf_validation/run_L_plate_validation.py
"""
import os, sys, json, subprocess, time as time_module
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新")
BLENDER_EXE = r"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
BLENDER_SCRIPT = PROJECT_ROOT / "ocs_project/06_brdf_validation/render_L_plate.py"
STL_A = PROJECT_ROOT / "建模/flat_plate_1m2_subd.stl"       # XY plane, normal +Z
STL_B = PROJECT_ROOT / "建模/L_plate_vertical_subd.stl"     # XZ plane, normal +Y

sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/01_code"))
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/07_brdf"))
sys.path.insert(0, str(PROJECT_ROOT / "ocs_project/02_blender"))

from config import SUN_VECTOR, DET_VECTOR
from geometry import euler_to_matrix
from brdf_models import eval_legacy_phong
from brdf_postprocess import read_multilayer_exr, compute_radiance_image, integrate_ocs

SUN_VEC = np.array(SUN_VECTOR, dtype=np.float64)
DET_VEC = np.array(DET_VECTOR, dtype=np.float64)
SUN_N = SUN_VEC / np.linalg.norm(SUN_VEC)
DET_N = DET_VEC / np.linalg.norm(DET_VEC)

MAT = {"rho_d": 0.20, "rho_s": 0.60, "n": 80, "brdf_model": "legacy_phong"}
MAT_DIFF = {**MAT, "rho_s": 0.0}

ATTITUDES = [(0, 0), (0, -30), (90, -45), (150, -80), (180, 0)]

PART_PASS = {"Plate_H": 1, "Plate_V": 2}  # 与 Blender pass_index 一致


def analytical_per_plate(yaw, pitch, mat):
    """解析解：两块平板无遮挡各自的 OCS"""
    R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
    # Plate H: normal [0,0,1] in body → R[:,2] in inertial
    N_H = R @ np.array([0.0, 0.0, 1.0])
    # Plate V: normal [0,1,0] in body → R[:,1] in inertial
    N_V = R @ np.array([0.0, 1.0, 0.0])

    results = {}
    for label, N in [("Plate_H", N_H), ("Plate_V", N_V)]:
        NoL = float(np.dot(N, SUN_N))
        NoV = float(np.dot(N, DET_N))
        if NoL <= 0 or NoV <= 0:
            results[label] = {"ocs": 0.0, "NoL": NoL, "NoV": NoV, "f_r": 0.0}
        else:
            f_r = float(eval_legacy_phong(N, SUN_N, DET_N, mat["rho_d"], mat["rho_s"], mat["n"]))
            results[label] = {"ocs": 1.0 * f_r * NoL * NoV, "NoL": NoL, "NoV": NoV, "f_r": f_r}
    return results


def a_side_per_plate(yaw, pitch, mat):
    """A 端 trimesh: 逐面元 BRDF，返回 per-part OCS（no_occ / with_occ）"""
    from geometry import load_meshes
    from occlusion import RayForest

    import materials as materials_mod
    orig_get = materials_mod.get_material
    def plate_get(name):
        if name in ("Plate_H", "Plate_V"):
            return mat.copy()
        return orig_get(name)
    materials_mod.get_material = plate_get

    try:
        part_files = {"Plate_H": str(STL_A), "Plate_V": str(STL_B)}
        meshes, _ = load_meshes(part_files=part_files, accuracy_level="full", verbose=False)
        R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)

        per_part = {}
        total_no_occ = 0.0
        total_with_occ = 0.0

        for pn in ["Plate_H", "Plate_V"]:
            m = meshes[pn]
            if hasattr(m, 'face_normals'):
                n_local = np.array(m.face_normals, dtype=np.float64)
            else:
                v = np.array(m.vertices); f = np.array(m.faces)
                e1 = v[f[:,1]]-v[f[:,0]]; e2 = v[f[:,2]]-v[f[:,0]]
                n_local = np.cross(e1, e2)
                nn = np.linalg.norm(n_local, axis=1, keepdims=True)
                n_local = n_local / np.where(nn > 1e-12, nn, 1.0)
            area_m2 = np.array(m.area_faces, dtype=np.float64) * 1e-6 if hasattr(m, 'area_faces') else np.full(len(n_local), 0.5, dtype=np.float64)

            N = n_local @ R.T
            nn = np.linalg.norm(N, axis=1, keepdims=True)
            N = N / np.where(nn > 1e-12, nn, 1.0)

            NoL = np.maximum(np.einsum("ij,j->i", N, SUN_N), 0.0)
            NoV = np.maximum(np.einsum("ij,j->i", N, DET_N), 0.0)
            vis = (NoL > 0) & (NoV > 0)

            L_bc = np.broadcast_to(SUN_N, N.shape).copy()
            V_bc = np.broadcast_to(DET_N, N.shape).copy()
            f_r = eval_legacy_phong(N, L_bc, V_bc, mat["rho_d"], mat["rho_s"], mat["n"])

            ocs_no = float(np.sum(area_m2[vis] * f_r[vis] * NoL[vis] * NoV[vis]))

            # Ray-cast occlusion from face centers (all in body frame M)
            if vis.any() and hasattr(m, 'triangles_center'):
                centers_body = np.array(m.triangles_center, dtype=np.float64)[vis]
                normals_body = n_local[vis]
                # Directions in body frame: inertial → body via R.T
                sun_body = R.T @ SUN_N
                det_body = R.T @ DET_N
                rf = RayForest(meshes, batch_size=50)
                occ1, occ2 = rf.batch_occlusion_dual(
                    centers_body + normals_body * 1e-3,
                    sun_body, det_body,
                    min_hit_distance=1e-3)
                occ_mask = occ1 | occ2
                ocs_with = float(np.sum(area_m2[vis][~occ_mask] * f_r[vis][~occ_mask] * NoL[vis][~occ_mask] * NoV[vis][~occ_mask])) if (~occ_mask).any() else 0.0
            else:
                ocs_with = ocs_no

            per_part[pn] = {"ocs_no_occ": ocs_no, "ocs_with_occ": ocs_with}
            total_no_occ += ocs_no
            total_with_occ += ocs_with

        occ_ratio = 1.0 - total_with_occ / max(total_no_occ, 1e-30)
        return {
            "ocs_total_no_occ": total_no_occ,
            "ocs_total_with_occ": total_with_occ,
            "occ_ratio": occ_ratio,
            "Plate_H": per_part["Plate_H"],
            "Plate_V": per_part["Plate_V"],
        }
    finally:
        materials_mod.get_material = orig_get


def b_side_per_plate(exr_path, meta, mat_full, mat_diff):
    """B 端 EXR 后处理，按 IndexOB 分板"""
    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)
    r_max = meta["r_max"]; res = meta["resolution"]
    pixel_area = (2.2 * r_max / res) ** 2

    layers = read_multilayer_exr(str(exr_path))
    idx = layers["IndexOB"].astype(np.int32)
    depth = layers["Depth"]
    mask_obj = (depth < 1e9) & (idx > 0)

    results = {}
    for pn, pid in PART_PASS.items():
        m_part = mask_obj & (idx == pid)
        n_pix = int(m_part.sum())

        if n_pix == 0:
            results[pn] = {"ocs_full": 0.0, "ocs_diff": 0.0, "n_pixels": 0}
            continue

        results[pn] = {"n_pixels": n_pix}
        for suffix, m in [("full", mat_full), ("diff", mat_diff)]:
            mats = {pn: m}
            pass_idx = {pn: pid}
            rad, _, pp = compute_radiance_image(layers, sun_dir, det_dir, mats, pass_idx)
            results[pn][f"ocs_{suffix}"] = integrate_ocs(rad, pixel_area)

    return results


def main():
    print("=" * 70)
    print("  L 型双平板可见性对账")
    print("=" * 70)
    print(f"  Plate H (XY平面, 法线+Z): {STL_A}")
    print(f"  Plate V (XZ平面, 法线+Y): {STL_B}")

    # ---- Step 1: Blender 渲染 ----
    print(f"\n--- Step 1: Blender 渲染 ---")
    out_dir = PROJECT_ROOT / "结果/BRDF验证" / f"L_plate_{time_module.strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [BLENDER_EXE, "--background", "--python", str(BLENDER_SCRIPT), "--",
           "--out-dir", str(out_dir), "--res", "128",
           "--stl-a", str(STL_A), "--stl-b", str(STL_B)]
    t0 = time_module.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    print(f"  Blender: {time_module.time()-t0:.1f}s")
    if result.returncode != 0:
        print(f"[FAIL] {result.stderr}")
        sys.exit(1)

    with open(out_dir / "render_metadata.json", "r") as f:
        meta = json.load(f)

    # ---- Step 2: 后处理 & 对比 ----
    print(f"\n--- Step 2: 三端对比 ---")
    rows = []
    for yaw, pitch in ATTITUDES:
        fname = f"yaw{yaw:06.2f}_pitch{pitch:+06.2f}"
        exr_path = out_dir / f"{fname}_0001.exr"
        print(f"\n  [{fname}]")

        # 解析解
        an = analytical_per_plate(yaw, pitch, MAT)
        an_diff = analytical_per_plate(yaw, pitch, MAT_DIFF)

        # A 端
        a_res = a_side_per_plate(yaw, pitch, MAT)
        a_res_diff = a_side_per_plate(yaw, pitch, MAT_DIFF)

        # B 端
        b_res = b_side_per_plate(exr_path, meta, MAT, MAT_DIFF)

        def rel(v, ref):
            d = max(abs(ref), 1e-30)
            return abs(v - ref) / d if d > 1e-30 else float("nan")

        r = {"yaw": yaw, "pitch": pitch,
             "A_occ_ratio": a_res["occ_ratio"]}
        for pn in ["Plate_H", "Plate_V"]:
            # Full
            an_ocs = an[pn]["ocs"]
            a_no = a_res[pn]["ocs_no_occ"]
            a_with = a_res[pn]["ocs_with_occ"]
            b_ocs = b_res.get(pn, {}).get("ocs_full", 0.0)
            b_pix = b_res.get(pn, {}).get("n_pixels", 0)
            # Diffuse
            an_d = an_diff[pn]["ocs"]
            a_d_no = a_res_diff[pn]["ocs_no_occ"]
            a_d_with = a_res_diff[pn]["ocs_with_occ"]
            b_d = b_res.get(pn, {}).get("ocs_diff", 0.0)

            print(f"    [{pn}]")
            print(f"      Full:      an={an_ocs:.6e}  A_no={a_no:.6e}  A_with={a_with:.6e}  B={b_ocs:.6e}  pix={b_pix}")
            print(f"      Diffuse:   an={an_d:.6e}  A_no={a_d_no:.6e}  A_with={a_d_with:.6e}  B={b_d:.6e}")
            print(f"      A_no/an={rel(a_no,an_ocs)*100:.2f}%  A_with/B={a_with/b_ocs if b_ocs>0 else float('nan'):.3f}  B/an={rel(b_ocs,an_ocs)*100:.2}%")

            r.update({
                f"{pn}_an_full": an_ocs, f"{pn}_A_no_full": a_no, f"{pn}_A_with_full": a_with,
                f"{pn}_B_full": b_ocs, f"{pn}_B_pix": b_pix,
                f"{pn}_an_diff": an_d, f"{pn}_A_no_diff": a_d_no, f"{pn}_A_with_diff": a_d_with,
                f"{pn}_B_diff": b_d,
            })
        rows.append(r)

    # ---- CSV & Report ----
    csv_path = out_dir / "L_plate_validation.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n  CSV: {csv_path}")

    # Report
    report = ["# L 型双平板可见性对账报告", "",
              f"**时间**: {time_module.strftime('%Y-%m-%d %H:%M:%S')}", "",
              "## 几何", "- Plate H: 1m² XY 平面, 法线 +Z (pass_index=1)",
              "- Plate V: 1m² XZ 平面, 法线 +Y (pass_index=2)",
              "- 两板共享 X 轴接缝", "",
              "## 关键比率", "",
              "| yaw | pitch | occ% | H an | H A_no | H A_with | H B | H A_with/B | V an | V A_no | V A_with | V B | V A_with/B |",
              "|-----|-------|------|------|--------|----------|-----|------------|------|--------|----------|-----|------------|"]
    for r in rows:
        report.append(
            f"| {r['yaw']:3.0f} | {r['pitch']:+5.0f} | {r['A_occ_ratio']*100:.1f}% | "
            f"{r['Plate_H_an_full']:.4e} | {r['Plate_H_A_no_full']:.4e} | {r['Plate_H_A_with_full']:.4e} | {r['Plate_H_B_full']:.4e} | "
            f"{r['Plate_H_A_with_full']/max(r['Plate_H_B_full'],1e-30):.3f} | "
            f"{r['Plate_V_an_full']:.4e} | {r['Plate_V_A_no_full']:.4e} | {r['Plate_V_A_with_full']:.4e} | {r['Plate_V_B_full']:.4e} | "
            f"{r['Plate_V_A_with_full']/max(r['Plate_V_B_full'],1e-30):.3f} |")

    report.append("")
    report.append("## 解读")
    report.append("- A_with/B > 1: A 端计入的面元多于 B 端可见像素（ray-cast 比 camera raster 宽松）")
    report.append("- A_with/B < 1: A 端 ray-cast 遮挡比 B 端 rasterization 更激进")
    report.append("- 理想情况下 A_with/B ≈ 1（遮挡语义一致）")

    report_path = out_dir / "L_plate_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"  报告: {report_path}")

    # Figure
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

        fig, axes = plt.subplots(2, 3, figsize=(16, 9))
        labels = [f"({r['yaw']:.0f},{r['pitch']:+.0f})" for r in rows]
        x = np.arange(len(rows)); w = 0.2

        for col, pn in enumerate(["Plate_H", "Plate_V"]):
            # A vs B scatter
            ax = axes[0, col]
            a_vals = [r[f"{pn}_A_with_full"] for r in rows]
            b_vals = [r[f"{pn}_B_full"] for r in rows]
            ax.scatter(a_vals, b_vals, c='steelblue', s=60)
            mx = max(max(a_vals), max(b_vals)) * 1.1
            ax.plot([0, mx], [0, mx], 'k--', alpha=0.3)
            ax.set_xlabel("A with_occ"); ax.set_ylabel("B")
            ax.set_title(f"{pn}: A_with_occ vs B")
            ax.grid(alpha=0.3)

            # Ratio bar
            ax = axes[1, col]
            ratios = [r[f"{pn}_A_with_full"] / max(r[f"{pn}_B_full"], 1e-30) for r in rows]
            colors = ['green' if 0.8 <= v <= 1.25 else 'orange' if 0.5 <= v <= 2.0 else 'red' for v in ratios]
            ax.bar(x, ratios, color=colors, alpha=0.7)
            ax.axhline(1.0, color='k', ls='--', alpha=0.3)
            ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
            ax.set_title(f"{pn}: A_with/B ratio")
            ax.set_ylabel("A_with / B")
            ax.grid(axis='y', alpha=0.3)

        # Total OCS comparison
        ax = axes[0, 2]
        for i, r in enumerate(rows):
            a_tot = r["Plate_H_A_with_full"] + r["Plate_V_A_with_full"]
            b_tot = r["Plate_H_B_full"] + r["Plate_V_B_full"]
            ax.bar(i - w/2, a_tot, w, color='steelblue', alpha=0.7)
            ax.bar(i + w/2, b_tot, w, color='darkorange', alpha=0.7)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
        ax.set_title("Total OCS: A_with vs B")
        ax.legend(["A with_occ", "B"], fontsize=8)
        ax.grid(axis='y', alpha=0.3)

        # Occ ratio
        ax = axes[1, 2]
        ax.bar(x, [r["A_occ_ratio"]*100 for r in rows], color='steelblue', alpha=0.7)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
        ax.set_title("A-side Occlusion Ratio (%)")
        ax.set_ylabel("%")
        ax.grid(axis='y', alpha=0.3)

        fig.suptitle("L-Shape Dual Plate: A (ray-cast) vs B (rasterization) Visibility", fontsize=13)
        fig.tight_layout()
        fig.savefig(out_dir / "fig_L_plate_compare.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  图: {out_dir / 'fig_L_plate_compare.png'}")
    except Exception as e:
        print(f"  [WARN] 图: {e}")

    print(f"\n  产物: {out_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()

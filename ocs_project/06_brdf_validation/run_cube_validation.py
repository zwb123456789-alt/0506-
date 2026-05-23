# -*- coding: utf-8 -*-
"""
run_cube_validation.py —— 立方体三端闭合验证
==============================================
1m³ 立方体在 5 姿态上对比解析/A/B 端 OCS。

输出: cube_validation.csv / cube_report.md / fig_cube_compare.png

用法:
    conda activate ocs_sim
    PYTHONIOENCODING=utf-8 python ocs_project/06_brdf_validation/run_cube_validation.py
"""
import os, sys, json, subprocess, time as time_module
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(r"D:\我的文件\研究生学术\光学项目\0506新")
BLENDER_EXE = r"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
BLENDER_SCRIPT = PROJECT_ROOT / "ocs_project/06_brdf_validation/render_cube.py"
STL_CUBE = PROJECT_ROOT / "建模/cube_1m_subd.stl"

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

# Cube 6 faces in body frame
CUBE_FACES = {
    "+X": np.array([1.0, 0.0, 0.0]),
    "-X": np.array([-1.0, 0.0, 0.0]),
    "+Y": np.array([0.0, 1.0, 0.0]),
    "-Y": np.array([0.0, -1.0, 0.0]),
    "+Z": np.array([0.0, 0.0, 1.0]),
    "-Z": np.array([0.0, 0.0, -1.0]),
}
FACE_AREA = 1.0  # m²


def analytical_cube(yaw, pitch, mat):
    """解析解：6 个面各自的 OCS（无遮挡）"""
    R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
    results = {}
    total = 0.0
    for fname, N_body in CUBE_FACES.items():
        N = R @ N_body
        NoL = float(np.dot(N, SUN_N))
        NoV = float(np.dot(N, DET_N))
        if NoL <= 0 or NoV <= 0:
            results[fname] = {"ocs": 0.0, "NoL": NoL, "NoV": NoV}
        else:
            f_r = float(eval_legacy_phong(N, SUN_N, DET_N, mat["rho_d"], mat["rho_s"], mat["n"]))
            ocs = FACE_AREA * f_r * NoL * NoV
            results[fname] = {"ocs": ocs, "NoL": NoL, "NoV": NoV, "f_r": f_r}
            total += ocs
    return results, total


def a_side_cube(yaw, pitch, mat):
    """A 端：逐面元 BRDF + ray-cast 遮挡"""
    from geometry import load_meshes
    from occlusion import RayForest
    import materials as materials_mod

    orig_get = materials_mod.get_material
    def cube_get(name):
        if name == "cube":
            return mat.copy()
        return orig_get(name)
    materials_mod.get_material = cube_get

    try:
        part_files = {"cube": str(STL_CUBE)}
        meshes, _ = load_meshes(part_files=part_files, accuracy_level="full", verbose=False)
        R = euler_to_matrix(yaw=yaw, pitch=pitch, roll=0.0, degrees=True)
        m = meshes["cube"]

        if hasattr(m, 'face_normals'):
            n_local = np.array(m.face_normals, dtype=np.float64)
        else:
            v = np.array(m.vertices); f = np.array(m.faces)
            e1 = v[f[:,1]]-v[f[:,0]]; e2 = v[f[:,2]]-v[f[:,0]]
            n_local = np.cross(e1, e2)
            nn = np.linalg.norm(n_local, axis=1, keepdims=True)
            n_local = n_local / np.where(nn > 1e-12, nn, 1.0)

        area_m2 = np.array(m.area_faces, dtype=np.float64) * 1e-6

        N = n_local @ R.T
        nn = np.linalg.norm(N, axis=1, keepdims=True)
        N = N / np.where(nn > 1e-12, nn, 1.0)

        NoL = np.maximum(np.einsum("ij,j->i", N, SUN_N), 0.0)
        NoV = np.maximum(np.einsum("ij,j->i", N, DET_N), 0.0)
        vis = (NoL > 0) & (NoV > 0)

        L_bc = np.broadcast_to(SUN_N, N.shape).copy()
        V_bc = np.broadcast_to(DET_N, N.shape).copy()
        f_r = eval_legacy_phong(N, L_bc, V_bc, mat["rho_d"], mat["rho_s"], mat["n"])

        ocs_no_occ = float(np.sum(area_m2[vis] * f_r[vis] * NoL[vis] * NoV[vis]))

        # Ray-cast occlusion
        if vis.any() and hasattr(m, 'triangles_center'):
            centers_body = np.array(m.triangles_center, dtype=np.float64)[vis]
            normals_body = n_local[vis]
            sun_body = R.T @ SUN_N
            det_body = R.T @ DET_N
            rf = RayForest(meshes, batch_size=100)
            occ1, occ2 = rf.batch_occlusion_dual(
                centers_body + normals_body * 1e-3,
                sun_body, det_body,
                min_hit_distance=1e-3)
            occ_mask = occ1 | occ2
            ocs_with_occ = float(np.sum(area_m2[vis][~occ_mask] * f_r[vis][~occ_mask] * NoL[vis][~occ_mask] * NoV[vis][~occ_mask])) if (~occ_mask).any() else 0.0
        else:
            ocs_with_occ = ocs_no_occ

        occ_ratio = 1.0 - ocs_with_occ / max(ocs_no_occ, 1e-30)
        return {"ocs_no_occ": ocs_no_occ, "ocs_with_occ": ocs_with_occ, "occ_ratio": occ_ratio}
    finally:
        materials_mod.get_material = orig_get


def b_side_cube(exr_path, meta, mat_full, mat_diff):
    """B 端：EXR 后处理"""
    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)
    r_max = meta["r_max"]; res = meta["resolution"]
    pixel_area = (2.2 * r_max / res) ** 2

    layers = read_multilayer_exr(str(exr_path))
    mats = {"Cube": mat_full}
    pass_idx = {"Cube": 1}
    rad_full, _, pp_full = compute_radiance_image(layers, sun_dir, det_dir, mats, pass_idx)
    ocs_full = integrate_ocs(rad_full, pixel_area)

    mats_diff = {"Cube": mat_diff}
    rad_diff, _, pp_diff = compute_radiance_image(layers, sun_dir, det_dir, {"Cube": mat_diff}, pass_idx)
    ocs_diff = integrate_ocs(rad_diff, pixel_area)

    return {"ocs_full": ocs_full, "ocs_diff": ocs_diff, "n_pixels": pp_full.get("Cube", 0)}


def main():
    print("=" * 70)
    print("  立方体三端闭合验证")
    print("=" * 70)
    print(f"  STL: {STL_CUBE}")

    # ---- Step 1: Blender ----
    print(f"\n--- Step 1: Blender 渲染 ---")
    out_dir = PROJECT_ROOT / "结果/BRDF验证" / f"cube_{time_module.strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [BLENDER_EXE, "--background", "--python", str(BLENDER_SCRIPT), "--",
           "--out-dir", str(out_dir), "--res", "128", "--stl", str(STL_CUBE)]
    t0 = time_module.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    print(f"  Blender: {time_module.time()-t0:.1f}s")
    if result.returncode != 0:
        # Print last 2000 chars of stderr
        print(f"[FAIL] {result.stderr[-2000:]}")
        sys.exit(1)

    with open(out_dir / "render_metadata.json", "r") as f:
        meta = json.load(f)

    # ---- Step 2: Compare ----
    print(f"\n--- Step 2: 三端对比 ---")
    rows = []
    for yaw, pitch in ATTITUDES:
        fname = f"yaw{yaw:06.2f}_pitch{pitch:+06.2f}"
        exr_path = out_dir / f"{fname}_0001.exr"
        print(f"\n  [{fname}]")

        an_faces, an_total = analytical_cube(yaw, pitch, MAT)
        an_faces_diff, an_total_diff = analytical_cube(yaw, pitch, MAT_DIFF)

        a_res = a_side_cube(yaw, pitch, MAT)
        a_res_diff = a_side_cube(yaw, pitch, MAT_DIFF)

        b_res = b_side_cube(exr_path, meta, MAT, MAT_DIFF)

        def rel(v, ref):
            d = max(abs(ref), 1e-30)
            return abs(v - ref) / d if d > 1e-30 else float("nan")

        # Print per-face analyt
        for fname_face, fd in an_faces.items():
            if fd["ocs"] > 1e-30:
                print(f"    Face {fname_face}: NoL={fd['NoL']:+.4f} NoV={fd['NoV']:+.4f} ocs={fd['ocs']:.6e}")

        print(f"    Total:  an={an_total:.6e}  A_no={a_res['ocs_no_occ']:.6e}  "
              f"A_with={a_res['ocs_with_occ']:.6e}  B={b_res['ocs_full']:.6e}  pix={b_res['n_pixels']}")
        print(f"    Diff:   an={an_total_diff:.6e}  A_no={a_res_diff['ocs_no_occ']:.6e}  "
              f"A_with={a_res_diff['ocs_with_occ']:.6e}  B={b_res['ocs_diff']:.6e}")
        print(f"    A_no/an={rel(a_res['ocs_no_occ'],an_total)*100:.2f}%  "
              f"A_with/B={a_res['ocs_with_occ']/max(b_res['ocs_full'],1e-30):.3f}  "
              f"B/an={rel(b_res['ocs_full'],an_total)*100:.2f}%  "
              f"occ%={a_res['occ_ratio']*100:.1f}%")

        rows.append({
            "yaw": yaw, "pitch": pitch,
            "an_total": an_total, "A_no": a_res["ocs_no_occ"], "A_with": a_res["ocs_with_occ"],
            "B_full": b_res["ocs_full"], "occ_ratio": a_res["occ_ratio"],
            "an_total_diff": an_total_diff, "A_no_diff": a_res_diff["ocs_no_occ"],
            "A_with_diff": a_res_diff["ocs_with_occ"], "B_diff": b_res["ocs_diff"],
            "B_pix": b_res["n_pixels"],
        })

    # ---- CSV ----
    csv_path = out_dir / "cube_validation.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        import csv
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n  CSV: {csv_path}")

    # ---- Report ----
    report = ["# 立方体三端闭合验证报告", "",
              f"**时间**: {time_module.strftime('%Y-%m-%d %H:%M:%S')}", "",
              "## 几何", "- 1m³ 立方体，中心在原点", "- 6 面 × 25 子面(5×5) = 300 三角面元", "",
              "## 结果", "",
              "| yaw | pitch | an_total | A_no | A_with | B | A_with/B | occ% | an_diff | A_no_diff | A_with_diff | B_diff |",
              "|-----|-------|----------|------|--------|---|----------|------|---------|-----------|-------------|--------|"]
    for r in rows:
        report.append(
            f"| {r['yaw']:3.0f} | {r['pitch']:+5.0f} | {r['an_total']:.4e} | {r['A_no']:.4e} | "
            f"{r['A_with']:.4e} | {r['B_full']:.4e} | {r['A_with']/max(r['B_full'],1e-30):.3f} | "
            f"{r['occ_ratio']*100:.1f}% | {r['an_total_diff']:.4e} | {r['A_no_diff']:.4e} | "
            f"{r['A_with_diff']:.4e} | {r['B_diff']:.4e} |")

    report.append("")
    report.append("## 解读")
    report.append("- A_no/an ≈ 1: BRDF 和几何正确")
    report.append("- A_with/B ≈ 1: ray-cast 与 camera rasterization 遮挡语义一致")
    report.append("- 立方体自遮挡随姿态变化，验证可见性逻辑")

    report_path = out_dir / "cube_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"  报告: {report_path}")

    # ---- Figure ----
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        labels = [f"({r['yaw']:.0f},{r['pitch']:+.0f})" for r in rows]
        x = np.arange(len(rows))
        w = 0.25

        # A vs B scatter
        ax = axes[0, 0]
        a_vals = [r["A_with"] for r in rows]
        b_vals = [r["B_full"] for r in rows]
        ax.scatter(a_vals, b_vals, c='steelblue', s=60)
        mx = max(max(a_vals), max(b_vals)) * 1.1
        ax.plot([0, mx], [0, mx], 'k--', alpha=0.3)
        for i, lab in enumerate(labels):
            ax.annotate(lab, (a_vals[i], b_vals[i]), fontsize=6, alpha=0.7)
        ax.set_xlabel("A with_occ"); ax.set_ylabel("B")
        ax.set_title("A_with_occ vs B (Full BRDF)")
        ax.grid(alpha=0.3)

        # Bars: A_no, A_with, B
        ax = axes[0, 1]
        for i, r in enumerate(rows):
            ax.bar(i - w, r["A_no"], w, color='steelblue', alpha=0.7, label='A_no' if i==0 else '')
            ax.bar(i, r["A_with"], w, color='orange', alpha=0.7, label='A_with' if i==0 else '')
            ax.bar(i + w, r["B_full"], w, color='green', alpha=0.7, label='B' if i==0 else '')
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
        ax.set_title("OCS Comparison (Full)")
        ax.legend(fontsize=7)
        ax.grid(axis='y', alpha=0.3)

        # Occ ratio
        ax = axes[1, 0]
        ax.bar(x, [r["occ_ratio"]*100 for r in rows], color='steelblue', alpha=0.7)
        ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7)
        ax.set_title("A-side Occlusion Ratio (%)")
        ax.set_ylabel("%"); ax.grid(axis='y', alpha=0.3)

        # Diffuse: A_no vs B
        ax = axes[1, 1]
        a_d = [r["A_with_diff"] for r in rows]
        b_d = [r["B_diff"] for r in rows]
        ax.scatter(a_d, b_d, c='darkorange', s=60)
        mx_d = max(max(a_d), max(b_d)) * 1.1
        ax.plot([0, mx_d], [0, mx_d], 'k--', alpha=0.3)
        for i, lab in enumerate(labels):
            ax.annotate(lab, (a_d[i], b_d[i]), fontsize=6, alpha=0.7)
        ax.set_xlabel("A with_occ (diff)"); ax.set_ylabel("B (diff)")
        ax.set_title("A_with vs B (Diffuse only)")
        ax.grid(alpha=0.3)

        fig.suptitle("Cube 1m³: A (ray-cast) vs B (rasterization) Comparison", fontsize=13)
        fig.tight_layout()
        fig.savefig(out_dir / "fig_cube_compare.png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  图: {out_dir / 'fig_cube_compare.png'}")
    except Exception as e:
        print(f"  [WARN] 图: {e}")

    print(f"\n  产物: {out_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()

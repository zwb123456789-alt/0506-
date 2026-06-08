# -*- coding: utf-8 -*-
"""
brdf_postprocess.py —— 模块 B · Python 后处理 BRDF 计算（exact BRDF）
========================================================================
读 Blender MULTILAYER EXR（Combined / Normal / Depth / IndexOB），按
模块 A 的 LegacyPhong 公式逐像素计算辐射亮度，并积分得到 OCS_image。

【几何与公式】
正交相机：每个像素覆盖的屏幕面积 A_pix = (ortho_scale / res)^2 (m^2)
相对于面元的投影：A_pix = A_face * |N · V_cam|，  |V_cam| = 朝向 det
所以 A_face = A_pix / NoV
LegacyPhong：f_r = rho_d/π + rho_s · (N·H)^n
模块 A OCS：OCS = Σ_face A_face · f_r · NoL · NoV
                = Σ_pixel (A_pix / NoV) · f_r · NoL · NoV
                = Σ_pixel A_pix · f_r · NoL          ←  NoV 抵消！

【部件区分】
IndexOB.V ∈ {0(背景), 1(jinshuzhuti), 2(taiyangnengban), 3(yinshenban)}
对每部件分别取材质参数。

【遮挡】
Cycles 一阶可见性已自动处理：被遮挡的面元不会出现在像素中。
（与模块 A 的 trimesh 遮挡机制等价：A 排除 sun-occluded 面元，B 由 Cycles
 几何 raster 排除 cam-occluded 面元。两端遮挡判据不完全相同——A 同时
 排除 sun 与 det 不可见的面元，但 B 仅排除 det 不可见的，sun 可见性
 通过 NoL 与 face-up 检测处理。）

用法：
    python brdf_postprocess.py <out_dir>
    python brdf_postprocess.py <out_dir> --save-exr
"""

import os
import sys
import csv
import json
import glob
import argparse
import time
import io
from pathlib import Path

import numpy as np

# Windows 控制台 UTF-8
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

# BRDF 模块路径
BRDF_DIR = os.path.join(os.path.dirname(__file__), "..", "07_brdf")
if BRDF_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(BRDF_DIR))

import OpenEXR
import Imath

try:
    import imageio.v3 as iio
    HAS_IMAGEIO = True
except ImportError:
    HAS_IMAGEIO = False

try:
    import cv2
    HAS_CV2 = hasattr(cv2, "imwrite")
except ImportError:
    HAS_CV2 = False

try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from brdf_models import eval_legacy_phong, eval_ggx_cook_torrance, MATERIAL_DB_GGX  # noqa: E402


# ============================================================
# 常量：与 render_geometry_passes.py 一致
# ============================================================
PART_PASS_INDEX = {
    "jinshuzhuti":    1,
    "taiyangnengban": 2,
    "yinshenban":     3,
}
INDEX_TO_PART = {v: k for k, v in PART_PASS_INDEX.items()}
DEPTH_BG_THRESHOLD = 1e9  # > 1e9 视为背景（Blender 默认 1e10）


# ============================================================
# EXR IO
# ============================================================
def read_multilayer_exr(path):
    """返回 dict：layer 名 → (H, W) 或 (H, W, K)"""
    f = OpenEXR.InputFile(str(path))
    h = f.header()
    dw = h["dataWindow"]
    W = dw.max.x - dw.min.x + 1
    H = dw.max.y - dw.min.y + 1

    raw_channels = {}
    for ch in h["channels"].keys():
        raw = f.channel(ch, Imath.PixelType(Imath.PixelType.FLOAT))
        raw_channels[ch] = np.frombuffer(raw, dtype=np.float32).reshape(H, W)

    out = {"_size": (H, W), "_channels": list(raw_channels.keys())}

    # Combined（RGBA）
    if "Combined.R" in raw_channels:
        out["Combined"] = np.stack([
            raw_channels["Combined.R"],
            raw_channels["Combined.G"],
            raw_channels["Combined.B"],
        ], axis=-1)

    # Normal（XYZ）
    if "Normal.X" in raw_channels:
        out["Normal"] = np.stack([
            raw_channels["Normal.X"],
            raw_channels["Normal.Y"],
            raw_channels["Normal.Z"],
        ], axis=-1)

    # Depth (V)
    for k in ("Depth.V", "Depth.Z"):
        if k in raw_channels:
            out["Depth"] = raw_channels[k]
            break

    # IndexOB (V)
    for k in ("IndexOB.V", "IndexOB"):
        if k in raw_channels:
            out["IndexOB"] = raw_channels[k]
            break

    # Backfacing AOV（精确背面遮罩：0.0=正面，1.0=背面）
    # 注意：MULTILAYER 下 AOV 以 RGBA 四通道写出，取 R 通道即可
    for k in ("Backfacing.R", "Backfacing.V", "Backfacing"):
        if k in raw_channels:
            out["Backfacing"] = raw_channels[k]
            break

    return out


def write_png_gamma(path, img_linear, scale=1.0, gamma=2.2):
    """将线性图像 / scale 后做 gamma 写入 8-bit PNG。"""
    img = np.clip(img_linear / max(scale, 1e-12), 0.0, 1.0)
    img = np.power(img, 1.0 / gamma)
    img8 = (img * 255.0).astype(np.uint8)
    if img8.ndim == 2:
        img8 = np.stack([img8] * 3, axis=-1)
    if HAS_CV2:
        cv2.imwrite(str(path), img8[:, :, ::-1])
    elif HAS_IMAGEIO:
        iio.imwrite(str(path), img8)
    elif HAS_PIL:
        PILImage.fromarray(img8).save(str(path))
    else:
        raise RuntimeError("需要 cv2 / imageio / Pillow 来写 PNG")


def write_linear_exr(path, gray):
    """将 (H, W) 单通道 float 写为 EXR（R=G=B）"""
    g = gray.astype(np.float32)
    H, W = g.shape
    hdr = OpenEXR.Header(W, H)
    out = OpenEXR.OutputFile(str(path), hdr)
    b = g.tobytes()
    out.writePixels({"R": b, "G": b, "B": b})


# ============================================================
# BRDF 计算（向量化、按部件分别处理）
# ============================================================
def compute_radiance_image(layers, sun_dir, det_dir, materials, materials_pass_index, use_ggx=False):
    """
    输出：
      radiance: (H, W) float64，每像素 f_r * NoL（线性辐射亮度量纲在 OCS 计算时再乘 pixel_area）
      mask_obj: (H, W) bool，物体像素
      part_pixels: dict[part_name] -> count
    """
    N_world = layers["Normal"].astype(np.float64)  # (H, W, 3)，世界空间
    depth = layers["Depth"]
    idx = layers["IndexOB"].astype(np.int32)
    H, W = N_world.shape[:2]

    # 物体像素（深度有效 + 有 part_index）
    mask_obj = (depth < DEPTH_BG_THRESHOLD) & (idx > 0)

    # 精确背面遮罩：Backfacing AOV > 0.5 表示背面像素，排除
    backfacing = layers.get("Backfacing")
    if backfacing is not None:
        mask_frontface = backfacing < 0.5
        mask_obj = mask_obj & mask_frontface

    # 法线归一化（防数值漂移）
    n_norm = np.linalg.norm(N_world, axis=-1, keepdims=True)
    n_norm = np.where(n_norm > 1e-8, n_norm, 1.0)
    N_world = N_world / n_norm

    L = np.array(sun_dir, dtype=np.float64)
    V = np.array(det_dir, dtype=np.float64)

    radiance = np.zeros((H, W), dtype=np.float64)
    part_pixels = {}

    for part_name, mat in materials.items():
        pid = materials_pass_index[part_name]
        m_part = mask_obj & (idx == pid)
        n_pix = int(m_part.sum())
        part_pixels[part_name] = n_pix
        if n_pix == 0:
            continue

        N_pix_all = N_world[m_part]                       # (M, 3)

        # NoV > 0 过滤：排除背面像素（与模块 A 可见性规则对齐）
        # 背面像素 NoV ≤ 0，A_face = A_pix / NoV 公式失效，必须排除
        NoV_vec = np.einsum("ij,j->i", N_pix_all, V)
        front = NoV_vec > 0
        if not front.any():
            part_pixels[part_name] = 0
            continue

        # 构建仅含正面的紧凑 mask
        m_front = m_part.copy()
        m_front[m_part] = front
        part_pixels[part_name] = int(m_front.sum())

        N_pix = N_world[m_front]
        L_bc = np.broadcast_to(L, N_pix.shape).copy()
        V_bc = np.broadcast_to(V, N_pix.shape).copy()

        if use_ggx:
            f_r = eval_ggx_cook_torrance(
                N_pix, L_bc, V_bc,
                mat["base_color"], mat["metallic"], mat["roughness"],
                F0=mat.get("F0"), ior=mat.get("ior"),
            )  # (M,)
        else:
            f_r = eval_legacy_phong(
                N_pix, L_bc, V_bc,
                mat["rho_d"], mat["rho_s"], mat["n"]
            )  # (M,)

        NoL = np.maximum(np.einsum("ij,j->i", N_pix, L), 0.0)
        # 模块 A OCS = Σ A_face · f_r · NoL · NoV，A_face = A_pix / NoV → NoV 抵消
        radiance[m_front] = f_r * NoL  # 不含 pixel_area

    return radiance, mask_obj, part_pixels


def integrate_ocs(radiance, pixel_area_m2):
    """OCS_image = Σ radiance · pixel_area"""
    return float(np.sum(radiance) * pixel_area_m2)


# ============================================================
# 主流程
# ============================================================
def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = argv[1:]
    p = argparse.ArgumentParser(description="exact BRDF post-processing")
    p.add_argument("out_dir", help="render_geometry_passes.py 的输出目录")
    p.add_argument("--save-exr", action="store_true", help="保存线性 EXR 灰度图")
    p.add_argument("--no-png", action="store_true", help="不写 PNG")
    p.add_argument("--ocs-json", default=None,
                   help="ocs_scan.json 用于对比，默认从 metadata 读")
    p.add_argument("--legacy-phong", action="store_true",
                   help="使用 LegacyPhong BRDF（默认 GGX/Cook-Torrance）")
    return p.parse_args(argv)


def find_exrs(out_dir):
    """找 *_0001.exr（按姿态前缀）"""
    out_dir = Path(out_dir)
    files = sorted(out_dir.glob("*_0001.exr"))
    return files


def attitude_key_from_exr(path):
    """yaw000.00_pitch-90.00_0001.exr → yaw000.00_pitch-90.00"""
    s = path.name
    if s.endswith("_0001.exr"):
        return s[:-len("_0001.exr")]
    return path.stem


def load_ocs_table(ocs_json_path):
    """读 ocs_scan.json，返回 dict{key: ...}。
    模块 A 的字段：ocs_no_occ / ocs_with_occ / occlusion_ratio。
    我们对比 ocs_with_occ（Cycles 一阶可见性遮挡 ≈ 含遮挡）。"""
    with open(ocs_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for r in data.get("scan_data", []):
        key = f"yaw{float(r['yaw']):06.2f}_pitch{float(r['pitch']):+06.2f}"
        out[key] = {
            "ocs_module_a":         float(r.get("ocs_with_occ", float("nan"))),
            "ocs_module_a_no_occ":  float(r.get("ocs_no_occ",   float("nan"))),
            "occlusion_ratio":      float(r.get("occlusion_ratio", float("nan"))),
            "raw": r,
        }
    return out


def process(out_dir, save_exr, save_png, ocs_json_override, use_ggx=True):
    out_dir = Path(out_dir)
    meta_path = out_dir / "render_metadata.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"未找到 {meta_path}")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    sun_dir = np.array(meta["sun_direction"], dtype=np.float64)
    det_dir = np.array(meta["det_direction"], dtype=np.float64)
    sun_dir /= np.linalg.norm(sun_dir)
    det_dir /= np.linalg.norm(det_dir)
    materials = meta["materials"]   # {part: {rho_d, rho_s, n}}
    if use_ggx:
        materials = {p: MATERIAL_DB_GGX[p].copy() for p in PART_PASS_INDEX}
        print(f"[BRDF-PP] BRDF 模型  = GGX / Cook-Torrance")
    r_max = float(meta["r_max"])
    res = int(meta["resolution"])

    ortho_scale = 2.2 * r_max
    pixel_area = (ortho_scale / res) ** 2  # 米²

    print(f"[BRDF-PP] out_dir   = {out_dir}")
    print(f"[BRDF-PP] sun       = {sun_dir}")
    print(f"[BRDF-PP] det       = {det_dir}")
    print(f"[BRDF-PP] r_max     = {r_max:.4f} m")
    print(f"[BRDF-PP] ortho     = {ortho_scale:.4f} m  res={res}")
    print(f"[BRDF-PP] pixel_area= {pixel_area:.4e} m²/px")
    print(f"[BRDF-PP] materials = {list(materials.keys())}")

    exr_files = find_exrs(out_dir)
    print(f"[BRDF-PP] 帧数 = {len(exr_files)}")
    if not exr_files:
        print("[BRDF-PP] 没找到 *_0001.exr，退出")
        return

    img_dir = out_dir / "brdf_images"
    img_dir.mkdir(exist_ok=True)

    # OCS 对照表
    ocs_json_path = ocs_json_override or meta.get("scan_json") or None
    ocs_lookup = {}
    if ocs_json_path and os.path.exists(ocs_json_path):
        ocs_lookup = load_ocs_table(ocs_json_path)
        print(f"[BRDF-PP] OCS 表    = {ocs_json_path}  ({len(ocs_lookup)} entries)")

    rows = []
    radiance_max_global = 0.0
    radiances = {}  # 缓存第一遍的 radiance，第二遍统一 scale 写 PNG

    # 第一遍：计算所有 radiance + ocs_image
    for ef in exr_files:
        t0 = time.perf_counter()
        layers = read_multilayer_exr(ef)
        rad, mask_obj, part_pix = compute_radiance_image(
            layers, sun_dir, det_dir, materials, PART_PASS_INDEX, use_ggx=use_ggx,
        )
        ocs_img = integrate_ocs(rad, pixel_area)
        radiance_max_global = max(radiance_max_global, float(rad.max()))
        radiances[ef.name] = rad

        key = attitude_key_from_exr(ef)
        rec_a = ocs_lookup.get(key, {})
        ocs_a = rec_a.get("ocs_module_a", float("nan"))
        ocs_a_no_occ = rec_a.get("ocs_module_a_no_occ", float("nan"))
        occ_ratio = rec_a.get("occlusion_ratio", float("nan"))
        rel_err = (
            abs(ocs_img - ocs_a) / abs(ocs_a)
            if (ocs_a == ocs_a and ocs_a != 0.0) else float("nan")
        )
        dt = time.perf_counter() - t0
        rows.append({
            "key": key,
            "ocs_image": ocs_img,
            "ocs_module_a": ocs_a,
            "ocs_module_a_no_occ": ocs_a_no_occ,
            "occlusion_ratio_a": occ_ratio,
            "rel_err": rel_err,
            "abs_err": abs(ocs_img - ocs_a) if ocs_a == ocs_a else float("nan"),
            "obj_pixels": int(mask_obj.sum()),
            "part_pixels": part_pix,
            "rad_max": float(rad.max()),
            "rad_mean_obj": float(rad[mask_obj].mean()) if mask_obj.any() else 0.0,
            "dt_sec": dt,
        })
        print(f"[BRDF-PP] {key:35s}  OCS_img={ocs_img:.4e}  "
              f"OCS_A_occ={ocs_a:.4e}  OCS_A_noocc={ocs_a_no_occ:.4e}  "
              f"relErr={rel_err:.3%}  obj={int(mask_obj.sum())}  {dt:.2f}s")

    # 第二遍：写 PNG / EXR（统一 scale）
    if save_png or save_exr:
        scale = max(radiance_max_global, 1e-12)
        print(f"[BRDF-PP] 全局 radiance_max = {scale:.4e}（用作可视化归一化 scale）")
        for ef in exr_files:
            rad = radiances[ef.name]
            key = attitude_key_from_exr(ef)
            if save_png:
                write_png_gamma(img_dir / f"{key}_brdf.png", rad, scale=scale, gamma=2.2)
            if save_exr:
                write_linear_exr(img_dir / f"{key}_brdf.exr", rad)

    # 写 CSV
    csv_path = out_dir / "ocs_comparison.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "key", "ocs_image", "ocs_module_a", "ocs_module_a_no_occ",
            "occlusion_ratio_a", "rel_err", "abs_err",
            "obj_pixels", "rad_max", "rad_mean_obj", "dt_sec",
            "px_jinshuzhuti", "px_taiyangnengban", "px_yinshenban",
        ])
        w.writeheader()
        for r in rows:
            w.writerow({
                "key": r["key"],
                "ocs_image": r["ocs_image"],
                "ocs_module_a": r["ocs_module_a"],
                "ocs_module_a_no_occ": r["ocs_module_a_no_occ"],
                "occlusion_ratio_a": r["occlusion_ratio_a"],
                "rel_err": r["rel_err"],
                "abs_err": r["abs_err"],
                "obj_pixels": r["obj_pixels"],
                "rad_max": r["rad_max"],
                "rad_mean_obj": r["rad_mean_obj"],
                "dt_sec": r["dt_sec"],
                "px_jinshuzhuti": r["part_pixels"].get("jinshuzhuti", 0),
                "px_taiyangnengban": r["part_pixels"].get("taiyangnengban", 0),
                "px_yinshenban": r["part_pixels"].get("yinshenban", 0),
            })
    print(f"[BRDF-PP] CSV: {csv_path}")

    # summary
    summary = {
        "out_dir": str(out_dir),
        "sun": list(sun_dir),
        "det": list(det_dir),
        "r_max": r_max,
        "resolution": res,
        "pixel_area_m2": pixel_area,
        "materials": materials,
        "ocs_json": ocs_json_path,
        "n_frames": len(rows),
        "radiance_max_global": radiance_max_global,
    }
    if any(r["rel_err"] == r["rel_err"] for r in rows):
        valid = [r["rel_err"] for r in rows if r["rel_err"] == r["rel_err"]]
        summary["rel_err_mean"] = float(np.mean(valid))
        summary["rel_err_max"]  = float(np.max(valid))
        summary["rel_err_min"]  = float(np.min(valid))
    with open(out_dir / "brdf_postprocess_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[BRDF-PP] summary: {out_dir / 'brdf_postprocess_summary.json'}")


def main():
    args = parse_args()
    process(
        out_dir=args.out_dir,
        save_exr=args.save_exr,
        save_png=not args.no_png,
        ocs_json_override=args.ocs_json,
        use_ggx=not args.legacy_phong,
    )


if __name__ == "__main__":
    main()

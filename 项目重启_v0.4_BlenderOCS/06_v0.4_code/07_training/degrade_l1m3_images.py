#!/usr/bin/env python3
"""
degrade_l1m3_images.py —— R116 子任务 B：M3 physically degraded 真实性轴

degradation 是对【观测本身】的物理退化，确定性地按 record 作用于 train/val/test 全部
（模拟真实传感条件），不是 B6 那种 train-only 粗增广。禁止复用 B6 σ=0.01+亮度±10%+整数平移包。

图像退化管线（物理顺序）：
  1. PSF / Gaussian blur (blur_sigma_px)
  2. 低分辨率下采样再上采样 (downsample_factor)         [moderate]
  3. 背景常量 + 线性梯度 (background_level, gradient)
  4. Poisson shot noise（图像缩放到光子计数域后采样）
  5. Gaussian read noise (read_noise_sigma)
  6. clip 到 [0,1]

OCS 总光度向量退化（仅测光误差，绝不把图像噪声作用到 OCS）：
  flux' = flux * (1 + N(0, flux_noise_frac))      逐几何独立乘性测光误差

确定性：每个 (record_id, 用途) 用 hash 派生独立种子，得到【固定的退化观测】，
train/eval 复用同一退化，可复现、无 per-epoch 噪声平均、无 split 间泄漏。

预注册两个等级（R116 §4）：
  degraded-mild     : blur 0.75px, read 0.01, flux 3%,  bg low
  degraded-moderate : blur 1.25px, read 0.02, flux 8%,  bg moderate+gradient, downsample x2

CLI（smoke / 预览）：
  python degrade_l1m3_images.py --preview --level degraded-mild
  python degrade_l1m3_images.py --preview --level degraded-moderate
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch
from scipy.ndimage import gaussian_filter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT_DIR = PROJECT_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" / "degraded"

# ── 预注册退化等级 ──
DEGRADE_LEVELS = {
    "clean": None,
    "degraded-mild": {
        "blur_sigma_px": 0.75,
        "downsample_factor": 1,
        "background_level": 0.01,
        "background_gradient": 0.0,
        "poisson_peak_photons": 2000.0,   # 高光子数 -> 低 shot noise
        "read_noise_sigma": 0.01,
        "flux_noise_frac": 0.03,
    },
    "degraded-moderate": {
        "blur_sigma_px": 1.25,
        "downsample_factor": 2,
        "background_level": 0.03,
        "background_gradient": 0.02,
        "poisson_peak_photons": 400.0,    # 较低光子数 -> 明显 shot noise
        "read_noise_sigma": 0.02,
        "flux_noise_frac": 0.08,
    },
}


def _record_seed(record_id, salt):
    """由 record_id + salt 派生确定性 32-bit 种子（固定退化观测，可复现）。"""
    h = hashlib.sha256(f"{record_id}|{salt}".encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def degrade_image(img, params, record_id, salt="img"):
    """对单张归一化图像 [H,W] in [0,1] 施加物理退化，确定性。返回 [H,W] float32 in [0,1]。"""
    if params is None:
        return img.astype(np.float32)
    rng = np.random.default_rng(_record_seed(record_id, salt))
    x = img.astype(np.float64)
    H, W = x.shape

    # 1. PSF / blur
    if params["blur_sigma_px"] > 0:
        x = gaussian_filter(x, sigma=params["blur_sigma_px"], mode="constant", cval=0.0)

    # 2. 低分辨率下采样再上采样
    f = int(params.get("downsample_factor", 1))
    if f > 1:
        # block-mean 下采样
        Hc, Wc = (H // f) * f, (W // f) * f
        xc = x[:Hc, :Wc].reshape(Hc // f, f, Wc // f, f).mean(axis=(1, 3))
        # 最近邻上采样回原尺寸
        x_up = np.repeat(np.repeat(xc, f, axis=0), f, axis=1)
        xr = x.copy()
        xr[:Hc, :Wc] = x_up
        x = xr

    # 3. 背景常量 + 线性梯度
    bg = params.get("background_level", 0.0)
    grad = params.get("background_gradient", 0.0)
    if bg > 0 or grad > 0:
        yy = np.linspace(0, 1, H)[:, None]
        xx = np.linspace(0, 1, W)[None, :]
        gradient_field = grad * (0.5 * yy + 0.5 * xx)   # 对角线性梯度
        x = x + bg + gradient_field

    # 4. Poisson shot noise（缩放到光子计数域）
    peak = params.get("poisson_peak_photons", 0.0)
    if peak and peak > 0:
        lam = np.clip(x, 0.0, None) * peak
        x = rng.poisson(lam).astype(np.float64) / peak

    # 5. Gaussian read noise
    rn = params.get("read_noise_sigma", 0.0)
    if rn > 0:
        x = x + rng.normal(0.0, rn, size=x.shape)

    # 6. clip
    x = np.clip(x, 0.0, 1.0)
    return x.astype(np.float32)


def degrade_flux_vector(flux_vec, params, record_id, salt="flux"):
    """对多几何总光度向量施加逐几何乘性测光误差（仅 OCS）。确定性。"""
    if params is None:
        return np.asarray(flux_vec, dtype=np.float64)
    frac = params.get("flux_noise_frac", 0.0)
    if frac <= 0:
        return np.asarray(flux_vec, dtype=np.float64)
    rng = np.random.default_rng(_record_seed(record_id, salt))
    v = np.asarray(flux_vec, dtype=np.float64)
    factor = 1.0 + rng.normal(0.0, frac, size=v.shape)
    return np.clip(v * factor, 0.0, None)


# ── smoke / 预览 ──
def _preview(level):
    from dataset_l1m2_multigeometry import build_multigeometry_table
    from PIL import Image
    params = DEGRADE_LEVELS[level]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    figdir = OUT_DIR / "figures"
    figdir.mkdir(parents=True, exist_ok=True)

    table, geoms = build_multigeometry_table("G5")
    # 取几个代表姿态
    sample_recs = [table[0], table[len(table) // 3], table[2 * len(table) // 3], table[-1]]

    summ = {"level": level, "params": params, "samples": []}
    for rec in sample_recs:
        png = PROJECT_ROOT / rec["png_path"]
        img = Image.open(png).convert("L")
        arr = np.array(img, dtype=np.float32) / 255.0
        deg = degrade_image(arr, params, rec["record_id"])
        flux = np.array(rec["flux_vector"])
        dflux = degrade_flux_vector(flux, params, rec["record_id"])
        summ["samples"].append({
            "record_id": rec["record_id"],
            "clean_img_mean": float(arr.mean()), "clean_img_std": float(arr.std()),
            "deg_img_mean": float(deg.mean()), "deg_img_std": float(deg.std()),
            "clean_img_max": float(arr.max()), "deg_img_max": float(deg.max()),
            "flux_clean": flux.round(6).tolist(),
            "flux_degraded": dflux.round(6).tolist(),
            "flux_rel_change_pct": (100 * (dflux - flux) / (flux + 1e-12)).round(2).tolist(),
        })
        # 保存并排预览图（clean | degraded）
        if level != "clean":
            combo = np.concatenate([arr, np.ones((arr.shape[0], 4)), deg], axis=1)
            Image.fromarray((combo * 255).astype(np.uint8)).save(
                figdir / f"preview_{level}_{rec['record_id']}.png")

    out = OUT_DIR / f"degrade_preview_{level}.json"
    json.dump(summ, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"[PREVIEW {level}]")
    for s in summ["samples"]:
        print(f"  {s['record_id']}: img mean {s['clean_img_mean']:.4f}->{s['deg_img_mean']:.4f} "
              f"std {s['clean_img_std']:.4f}->{s['deg_img_std']:.4f} "
              f"flux Δ%={s['flux_rel_change_pct']}")
    print(f"  -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--level", choices=list(DEGRADE_LEVELS.keys()), default="degraded-mild")
    args = ap.parse_args()
    if args.preview:
        _preview(args.level)
    else:
        print("degrade module. 用 --preview --level <lvl> 生成 smoke 预览。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
postclosure_degraded_severe_train.py —— R126 子任务 C2：degraded-severe 训练（派生 wrapper）

红线：不改旧脚本 degrade_l1m3_images.py / train_l1m3_degraded.py。
本 wrapper 在运行时向 DEGRADE_LEVELS 注入一档预注册的 'degraded-severe'，
然后完全复用 train_l1m3_degraded.main() 的训练/评估/保存逻辑。

degraded-severe 预注册参数（物理合理，比 moderate 更强，R126 §6 默认建议）：
  PSF Gaussian sigma  : 2.0 px
  downsample          : x4（再最近邻上采样回原尺寸）
  background          : 0.05 uniform + 0.04 linear gradient（更强天光+梯度）
  Poisson peak photons: 150（SNR≈5-10 dB 档，较强 shot noise）
  read noise sigma    : 0.03
  flux photometric err: 0.12（12% 乘性测光误差）
  record_id 派生 deterministic transform seed（沿用旧管线，通道/几何可对齐）

不复用 B6 粗增广包（σ=0.01+亮度±10%+整数平移）作为真实性模型。

用法：
  python postclosure_degraded_severe_train.py --geom-group G5 --mode joint --seed 42 --max-epochs 30
输出写入 17 号包 pint_hard_degraded_severe/runs/。
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 预注册 severe 档
SEVERE_PARAMS = {
    "blur_sigma_px": 2.0,
    "downsample_factor": 4,
    "background_level": 0.05,
    "background_gradient": 0.04,
    "poisson_peak_photons": 150.0,
    "read_noise_sigma": 0.03,
    "flux_noise_frac": 0.12,
}

OUT = (PROJECT_ROOT / "v0.4_results" / "17_route1c_postclosure_enhancement_sweep" /
       "pint_hard_degraded_severe")


def main():
    # 注入 severe 档到两个模块的 DEGRADE_LEVELS（不改磁盘上的旧脚本）
    import degrade_l1m3_images as deg
    deg.DEGRADE_LEVELS["degraded-severe"] = SEVERE_PARAMS

    import train_l1m3_degraded as tr
    # train 脚本 import 的是 DEGRADE_LEVELS 引用，同一 dict 对象，已含 severe
    tr.DEGRADE_LEVELS["degraded-severe"] = SEVERE_PARAMS

    # 解析本 wrapper 参数并转交（覆盖 outdir、level）
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom-group", choices=["G1", "G3", "G5"], required=True)
    ap.add_argument("--mode", choices=["ocs_only", "image_only", "joint"], required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--max-epochs", type=int, default=30)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    # 组装 train_l1m3_degraded 的 argv（其 main 用 argparse 读 sys.argv）
    argv = ["train_l1m3_degraded.py", "--train", "--level", "degraded-severe",
            "--geom-group", args.geom_group, "--mode", args.mode,
            "--protocol", "P-INT", "--seed", str(args.seed),
            "--max-epochs", str(args.max_epochs),
            "--outdir", str(OUT)]
    if args.smoke:
        argv.append("--smoke")
    sys.argv = argv
    return tr.main()


if __name__ == "__main__":
    raise SystemExit(main())

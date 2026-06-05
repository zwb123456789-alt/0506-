"""
run_cross_phase_generalization_12d.py — 实验12d：跨 phase 图像泛化 sanity test
================================================================================
目的（指导文件 §5）：
  回应 phase63 同分布质疑，检验图像模型对观测几何（phase angle / 光照-探测几何）变化
  的敏感性。这是合成数据 sanity test，不是真实望远镜验证。

设计（指导 §5）：
  - 训练：phase63 clean image（5 seeds）。
  - 测试：phase24_near_backscatter 与 phase120_forward_scatter（需先补渲染）。
  - 对照：ResNet image-only vs ResNet+OCS A2/concat5 per_part_log 30D（clean naive fusion）。
  - 不做全 5 phase 重训，不引入多相位融合新主线。
  - OCS concat5 是姿态特征（跨 phase 不变），仅图像分布在变。

前置渲染（本脚本不自动调 Blender，需先完成；脚本会检测图像是否存在）：
  scan_json: 结果/模块B_渲染/_scan_json_12d/ocs_scan_phase24.json / _phase120.json
  渲染命令（见脚本末尾注释 / 同 phase63 run_20260528_101944 管线，res=256, GGX 后处理）。

不变口径：split 10°→5°；target [sin,cos,sin,cos]；great-circle err；
          OCS=concat5 per_part_log 30D（fit train 统计）；image log1p 128×128。

判读（指导 §5，不预设）：
  - 跨 phase 明显退化：支持图像模型对观测几何分布敏感。
  - 跨 phase 也稳定：诚实报告，不强写图像必然跨 phase 脆弱。

红线：不写 real telescope / operational robustness / fully robust / near-perfect。
"""

import argparse
import csv
import glob
import json
import os
import sys
import time
from datetime import datetime

import numpy as np

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic
import run_resnet_fusion as rf
import run_fusion_mechanism_upgrade as up
import run_late_fusion_beta_sweep_12f as lf

import torch
import torch.nn as nn

_PHASE63_DIR = up._IMAGE_DIR
_RENDER_ROOT = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                         "cross_phase_generalization_12d")
SEEDS = [0, 1, 2, 3, 4]
SUM_KEYS = ["angular_err_mean", "angular_err_median", "angular_err_p90",
            "angular_err_p95", "angular_err_worst", "hit@5deg", "hit@10deg"]


def find_phase_dir(phase_tag):
    """自动找最新含该 phase tag 且已完成 BRDF 后处理（brdf_images 存在）的渲染目录。"""
    cands = sorted(glob.glob(os.path.join(_RENDER_ROOT, f"run_*{phase_tag}*")),
                   key=os.path.getmtime, reverse=True)
    for c in cands:
        if os.path.isdir(os.path.join(c, "brdf_images")) and \
           os.path.exists(os.path.join(c, "render_log.csv")):
            return c
    return None


def align_images_to(target_yaw, target_pitch, src_images, src_yaw, src_pitch):
    """按 (yaw,pitch) 把 src 图像重排到 target 顺序。返回 (aligned_images, ok_mask)。"""
    key = {(round(src_yaw[i], 4), round(src_pitch[i], 4)): i for i in range(len(src_yaw))}
    out = np.zeros((len(target_yaw),) + src_images.shape[1:], dtype=src_images.dtype)
    ok = np.zeros(len(target_yaw), dtype=bool)
    for i in range(len(target_yaw)):
        k = (round(target_yaw[i], 4), round(target_pitch[i], 4))
        if k in key:
            out[i] = src_images[key[k]]; ok[i] = True
    return out, ok


def _device():
    return "cuda" if torch.cuda.is_available() else "cpu"


def train_fusion_clean(data, args, seed):
    """naive clean fusion（rf.ResNetFusionModel, concat5 per_part_log）。返回 best_state。"""
    st, ep, bva = up.train_model(
        lambda: rf.ResNetFusionModel(ocs_dim=data[-1], dropout=args.dropout),
        data, args, augment=False, anchored=False, seed=seed)
    return st, ep, bva


@torch.no_grad()
def eval_image_only(state, images_eval, yaw, pitch, test_idx, args):
    device = _device()
    model = rf.ResNetImageOnly().to(device)
    model.load_state_dict(state); model.eval()
    Xi = torch.FloatTensor(images_eval[test_idx]).to(device)
    bs = args.batch_size * 2
    preds = [model(Xi[s:s + bs]).cpu().numpy() for s in range(0, len(test_idx), bs)]
    yp, pp = rf.decode_pred(np.concatenate(preds))
    m, _ = rf.compute_metrics(yp, pp, yaw[test_idx], pitch[test_idx])
    return m


@torch.no_grad()
def eval_fusion(state, images_eval, ocs_zs, yaw, pitch, test_idx, args, ocs_dim):
    device = _device()
    model = rf.ResNetFusionModel(ocs_dim=ocs_dim, dropout=args.dropout).to(device)
    model.load_state_dict(state); model.eval()
    m, _ = up.eval_on_images(model, images_eval, ocs_zs, yaw, pitch, test_idx, args)
    return m


def summarize(per_seed):
    s = {}
    for k in SUM_KEYS:
        vals = [m[k] for m in per_seed]
        s[f"{k}_mean"] = float(np.mean(vals)); s[f"{k}_std"] = float(np.std(vals))
    return s


def main():
    ap = argparse.ArgumentParser(description="Exp12d: cross-phase image generalization")
    ap.add_argument("--phase63-dir", default=_PHASE63_DIR)
    ap.add_argument("--phase24-dir", default=None)
    ap.add_argument("--phase120-dir", default=None)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--out-root", default=_OUT_ROOT)
    ap.add_argument("--image-size", type=int, default=128)
    ap.add_argument("--intensity", default="log1p")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--patience", type=int, default=100)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--dropout", type=float, default=0.10)
    ap.add_argument("--seeds", type=int, nargs="+", default=None)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    global SEEDS
    if args.smoke:
        SEEDS = [0]; args.epochs = 6; args.patience = 4
    elif args.seeds is not None:
        SEEDS = args.seeds
    up.SEEDS = SEEDS

    if args.manifest is None:
        cands = sorted(glob.glob(up._MANIFEST_GLOB), key=os.path.getmtime, reverse=True)
        if not cands:
            raise FileNotFoundError(f"No manifest: {up._MANIFEST_GLOB}")
        args.manifest = cands[0]
    if args.phase24_dir is None:
        args.phase24_dir = find_phase_dir("phase24")
    if args.phase120_dir is None:
        args.phase120_dir = find_phase_dir("phase120")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(args.out_root, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)
    log_f = open(os.path.join(out_dir, "run.log"), "w", encoding="utf-8", buffering=1)

    class Tee:
        def __init__(self, *s): self.s = s
        def write(self, x):
            for st in self.s:
                try: st.write(x); st.flush()
                except Exception: pass
        def flush(self):
            for st in self.s:
                try: st.flush()
                except Exception: pass
    sys.stdout = Tee(sys.__stdout__, log_f)
    sys.stderr = Tee(sys.__stderr__, log_f)

    print("=" * 70)
    print("  实验12d：跨 phase 图像泛化 sanity test")
    print(f"  phase63(train): {args.phase63_dir}")
    print(f"  phase24(test):  {args.phase24_dir}")
    print(f"  phase120(test): {args.phase120_dir}")
    print(f"  Output: {out_dir}  Seeds: {SEEDS}")
    print("=" * 70)

    missing = []
    if not args.phase24_dir:
        missing.append("phase24")
    if not args.phase120_dir:
        missing.append("phase120")
    if missing:
        msg = (f"[BLOCKED] 缺少渲染图像: {missing}。请先渲染：\n"
               f"  blender --background --python ocs_project/02_blender/render_geometry_passes.py "
               f"-- --scan-json 结果/模块B_渲染/_scan_json_12d/ocs_scan_phaseXX.json --res 256\n"
               f"  python ocs_project/02_blender/brdf_postprocess.py <out_dir> --res 256\n"
               f"渲染后重跑本脚本（或用 --phase24-dir/--phase120-dir 指定）。")
        print(msg)
        with open(os.path.join(out_dir, "BLOCKED.txt"), "w", encoding="utf-8") as f:
            f.write(msg)
        return out_dir

    t_all = time.time()
    print("\n  [准备数据] phase63 训练集 + OCS concat5")
    args.image_dir = args.phase63_dir  # up.prepare_data 读取 args.image_dir 作为训练图像
    data = up.prepare_data(args)  # 使用 phase63 图像
    images63, ocs_zs, yaw, pitch, split, tr_idx, val_idx, test_idx, ocs_dim = data

    # 加载并对齐跨 phase 图像
    print("  [加载跨 phase 图像]")
    img24, y24, p24 = rf.load_images(args.phase24_dir, args.image_size, args.intensity)
    img24a, ok24 = align_images_to(yaw, pitch, img24, y24, p24)
    print(f"    phase24 对齐 ok={ok24.sum()}/{len(yaw)}")
    img120, y120, p120 = rf.load_images(args.phase120_dir, args.image_size, args.intensity)
    img120a, ok120 = align_images_to(yaw, pitch, img120, y120, p120)
    print(f"    phase120 对齐 ok={ok120.sum()}/{len(yaw)}")
    # 只在三 phase 都有的 test 点评估
    test_ok = np.array([i for i in test_idx if ok24[i] and ok120[i]])
    print(f"    可评估 test 点（三 phase 均有）= {len(test_ok)}/{len(test_idx)}")

    phase_imgs = {"phase63": images63, "phase24": img24a, "phase120": img120a}

    # ---- 训练 phase63 ----
    print(f"\n{'='*64}\n  训练 ResNet image-only（phase63, {len(SEEDS)} seeds）\n{'='*64}")
    t0 = time.time(); st_img = []
    for s in SEEDS:
        st, ep, bva = lf.train_image_only_clean(data, args, s)
        st_img.append(st); print(f"    [img] seed={s} ep={ep} va={bva:.6f}", flush=True)
    print(f"  耗时 {time.time()-t0:.0f}s")

    print(f"\n{'='*64}\n  训练 ResNet+OCS A2 concat5（phase63, {len(SEEDS)} seeds）\n{'='*64}")
    t0 = time.time(); st_fus = []
    for s in SEEDS:
        st, ep, bva = train_fusion_clean(data, args, s)
        st_fus.append(st); print(f"    [fusion] seed={s} ep={ep} va={bva:.6f}", flush=True)
    print(f"  耗时 {time.time()-t0:.0f}s")

    # ---- 评估三 phase ----
    print(f"\n{'='*64}\n  评估 image-only / fusion × {{phase63, phase24, phase120}}\n{'='*64}")
    rows = []
    for phase, imgs in phase_imgs.items():
        ps_img, ps_fus = [], []
        for st in st_img:
            ps_img.append(eval_image_only(st, imgs, yaw, pitch, test_ok, args))
        for st in st_fus:
            ps_fus.append(eval_fusion(st, imgs, ocs_zs, yaw, pitch, test_ok, args, ocs_dim))
        ri = summarize(ps_img); ri["phase"] = phase; ri["model"] = "image_only"
        rfz = summarize(ps_fus); rfz["phase"] = phase; rfz["model"] = "fusion_concat5"
        rows += [ri, rfz]
        print(f"    [{phase:>9}] image_only={ri['angular_err_mean_mean']:.2f}"
              f"±{ri['angular_err_mean_std']:.2f}° (Hit5={ri['hit@5deg_mean']:.1%}) | "
              f"fusion={rfz['angular_err_mean_mean']:.2f}±{rfz['angular_err_mean_std']:.2f}° "
              f"(Hit5={rfz['hit@5deg_mean']:.1%})", flush=True)

    save_all(out_dir, rows, args, test_ok, t_all)
    print(f"\n  完成，总耗时 {time.time()-t_all:.0f}s。输出: {out_dir}")
    return out_dir


def save_all(out_dir, rows, args, test_ok, t_all):
    cols = ["phase", "model"] + [f"{k}_mean" for k in SUM_KEYS] + [f"{k}_std" for k in SUM_KEYS]
    with open(os.path.join(out_dir, "cross_phase_results.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    with open(os.path.join(out_dir, "cross_phase_results.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    def get(phase, model):
        r = next((x for x in rows if x["phase"] == phase and x["model"] == model), None)
        return r["angular_err_mean_mean"] if r else float("nan")

    L = ["# 实验12d：跨 phase 图像泛化 sanity test — 结果", "",
         f"> 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
         f"> 训练 phase63 clean，测试 phase24 / phase120；{len(SEEDS)} seeds；"
         f"评估 test 点={len(test_ok)}。  ",
         "> OCS concat5 为跨 phase 不变的姿态特征；仅图像观测几何在变。  ",
         "> **合成数据 sanity test，非真实望远镜验证。**", "",
         "## 主结果表：mean angular error (Hit@5°)", "",
         "| phase | image_only | fusion_concat5 |",
         "|---|---|---|"]
    for phase in ["phase63", "phase24", "phase120"]:
        ri = next((x for x in rows if x["phase"] == phase and x["model"] == "image_only"), None)
        rfz = next((x for x in rows if x["phase"] == phase and x["model"] == "fusion_concat5"), None)
        def fmt(r):
            return (f"{r['angular_err_mean_mean']:.2f}±{r['angular_err_mean_std']:.2f}° "
                    f"({r['hit@5deg_mean']:.0%})") if r else "—"
        L.append(f"| {phase} | {fmt(ri)} | {fmt(rfz)} |")

    di24 = get("phase24", "image_only") - get("phase63", "image_only")
    di120 = get("phase120", "image_only") - get("phase63", "image_only")
    df24 = get("phase24", "fusion_concat5") - get("phase63", "fusion_concat5")
    df120 = get("phase120", "fusion_concat5") - get("phase63", "fusion_concat5")
    L += ["", "## 跨 phase 退化（相对 phase63 in-distribution）", "",
          f"- image_only: phase24 Δ={di24:+.2f}°, phase120 Δ={di120:+.2f}°",
          f"- fusion_concat5: phase24 Δ={df24:+.2f}°, phase120 Δ={df120:+.2f}°", "",
          "## 判读（按数据，不预设结论）", ""]
    worst_img = max(di24, di120)
    if worst_img > 20:
        L.append(f"- 图像模型跨 phase **明显退化**（最大 Δ={worst_img:+.2f}°）→ "
                 "支持图像模型对观测几何分布敏感；phase63 同分布评估高估了图像泛化。")
    elif worst_img > 5:
        L.append(f"- 图像模型跨 phase **中度退化**（最大 Δ={worst_img:+.2f}°）→ "
                 "图像模型对观测几何有一定敏感性，但未完全失效。")
    else:
        L.append(f"- 图像模型跨 phase **基本稳定**（最大 Δ={worst_img:+.2f}°）→ "
                 "诚实报告：在本合成设置下图像模型跨 phase 未明显脆弱，不强写图像必然跨 phase 脆弱。")
    L += ["",
          "## 写作红线", "",
          "禁止写：real telescope validation / operational robustness / fully robust / near-perfect。",
          "本实验为合成跨几何 sanity test，仅说明 phase63 同分布评估的代表性边界。"]
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"config": vars(args), "seeds": SEEDS,
                   "n_test_eval": int(len(test_ok)),
                   "elapsed_sec": time.time() - t_all}, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()

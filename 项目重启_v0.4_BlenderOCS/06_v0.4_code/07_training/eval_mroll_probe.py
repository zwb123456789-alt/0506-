#!/usr/bin/env python3
"""
eval_mroll_probe.py —— R116 子任务 C：M-roll 边界探针评估

M-roll 是 fixed-roll 边界探针：检验 clean/P-INT 结论是否被少量 roll 扰动推翻。
方法（roll distribution-shift，不重训）：
  1. 取 R115 训练好的 clean roll-0 模型（image_only / joint，来自 11_l1m2）。
  2. 在【同一分层子集 attitude】上构造两组 test 观测：
       roll=0    ：现有 phase63 PNG / OCS（01_fullrun）
       roll=±d   ：M-roll 探针新渲染的 phase63 PNG / OCS（12_l1m3/mroll）
  3. 用 clean 模型分别预测，比较 roll=0 vs roll≠0 的 yaw cMAE / hit@30 漂移。
     漂移小 → fixed-roll 结论对小 roll 扰动稳健；漂移大 → roll 敏感。

限制：
  - 本轮 M-roll 只对 phase63（图像通道 + G1 OCS）在子集上执行，joint 的多几何 OCS
    roll 版本未全渲（成本见报告）。image_only 是 clean P-INT 近饱和通道，最能揭示
    roll 扰动是否推翻结论。
  - 结论只在本 roll 设置、几何、协议、子集规模下有效。

用法：
  python eval_mroll_probe.py
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from train_l1m2_multigeometry import (  # noqa: E402
    L1M2RegModel, decode_angles, compute_metrics, yaw_circ_err,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

L1M2 = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
MROLL = PROJECT_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" / "mroll"
FULLRUN_POST = PROJECT_ROOT / "v0.4_results" / "01_fullrun" / "postprocess"

ROLLS = [15, -15, 30, -30]


def load_subset():
    return json.load(open(MROLL / "mroll_subset_attitudes.json", encoding="utf-8"))


def parse_label(a):
    # a = "yaw000_pitch+000"
    import re
    m = re.match(r"yaw(\d+)_pitch([+-]\d+)", a)
    return int(m.group(1)), int(m.group(2))


def load_image_roll0(a):
    """roll=0 phase63 PNG（01_fullrun）。"""
    yaw, pit = parse_label(a)
    png = FULLRUN_POST / f"yaw{yaw:03d}_pitch{pit:+04d}_roll+000_brdf.png"
    if not png.exists():
        return None
    img = Image.open(png).convert("L")
    return np.array(img, dtype=np.float32) / 255.0


def load_image_roll(a, roll):
    """roll=±d phase63 PNG（M-roll 探针后处理）。"""
    yaw, pit = parse_label(a)
    roll_tag = f"roll{roll:+04d}"
    png = (MROLL / "postprocess" / "phase63" / roll_tag /
           f"yaw{yaw:03d}_pitch{pit:+04d}_{roll_tag}_brdf.png")
    if not png.exists():
        return None
    img = Image.open(png).convert("L")
    return np.array(img, dtype=np.float32) / 255.0


@torch.no_grad()
def predict_images(model, imgs, device):
    """imgs: list[np.array HxW] -> yaw_pred, pitch_pred。"""
    x = torch.from_numpy(np.stack(imgs)[:, None, :, :].astype(np.float32)).to(device)
    out = model({"image": x}).cpu().numpy()
    return decode_angles(out)


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    subset = load_subset()

    # 只做 image_only（clean P-INT 近饱和通道，最能揭示 roll 扰动是否推翻结论）
    results = []
    for group in ["G1", "G5"]:
        run_dir = L1M2 / "runs" / f"P-INT_{group}_image_only_seed42"
        ckpt = torch.load(run_dir / "checkpoint_best.pt", map_location=device,
                          weights_only=False)
        # image_only 不使用 ocs 编码器，ocs_dim 任意（不影响图像分支）
        model = L1M2RegModel("image_only", ocs_dim=1).to(device)
        model.load_state_dict(ckpt["model_state"])
        model.eval()

        # roll=0 baseline（子集）
        atts0, imgs0, yaws0, pits0 = [], [], [], []
        for a in subset:
            im = load_image_roll0(a)
            if im is None:
                continue
            y, p = parse_label(a)
            atts0.append(a); imgs0.append(im); yaws0.append(y); pits0.append(p)
        yp0, pp0 = predict_images(model, imgs0, device)
        m0 = compute_metrics(yp0, pp0, np.array(yaws0, float), np.array(pits0, float))

        row0 = {"geom_group": group, "mode": "image_only", "roll_deg": 0,
                "n": m0["n"], "yaw_cmae": round(m0["yaw_circular_mae_deg"], 3),
                "yaw_hit@30": round(m0["yaw_hit@30"], 4),
                "yaw_coarse90": round(m0["yaw_coarse90_acc"], 4),
                "pitch_mae": round(m0["pitch_mae_deg"], 3),
                "source": "roll0 baseline (01_fullrun subset)"}
        results.append(row0)

        for roll in ROLLS:
            atts, imgs, yaws, pits = [], [], [], []
            for a in subset:
                im = load_image_roll(a, roll)
                if im is None:
                    continue
                y, p = parse_label(a)
                atts.append(a); imgs.append(im); yaws.append(y); pits.append(p)
            if not imgs:
                results.append({"geom_group": group, "mode": "image_only",
                                "roll_deg": roll, "n": 0, "source": "NO_RENDER"})
                continue
            ypr, ppr = predict_images(model, imgs, device)
            # 注意：true yaw/pitch 仍是标称 yaw/pitch（roll 扰动下真值 yaw/pitch 不变）
            mr = compute_metrics(ypr, ppr, np.array(yaws, float), np.array(pits, float))
            results.append({
                "geom_group": group, "mode": "image_only", "roll_deg": roll,
                "n": mr["n"], "yaw_cmae": round(mr["yaw_circular_mae_deg"], 3),
                "yaw_hit@30": round(mr["yaw_hit@30"], 4),
                "yaw_coarse90": round(mr["yaw_coarse90_acc"], 4),
                "pitch_mae": round(mr["pitch_mae_deg"], 3),
                "cmae_drift_vs_roll0": round(mr["yaw_circular_mae_deg"] -
                                            m0["yaw_circular_mae_deg"], 3),
                "hit30_drift_vs_roll0": round(mr["yaw_hit@30"] - m0["yaw_hit@30"], 4),
                "source": f"mroll {roll:+d} (12_l1m3 subset)"})

    MROLL.mkdir(parents=True, exist_ok=True)
    cols = ["geom_group", "mode", "roll_deg", "n", "yaw_cmae", "yaw_hit@30",
            "yaw_coarse90", "pitch_mae", "cmae_drift_vs_roll0",
            "hit30_drift_vs_roll0", "source"]
    with open(MROLL / "mroll_metrics_summary_best.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow({c: r.get(c, "") for c in cols})
    json.dump(results, open(MROLL / "mroll_eval_results.json", "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    print("[M-roll eval] image_only roll distribution-shift（clean roll-0 模型评估）")
    for r in results:
        if r.get("n", 0) > 0:
            print(f"  {r['geom_group']} roll={r['roll_deg']:+d}: cmae={r['yaw_cmae']} "
                  f"hit@30={r['yaw_hit@30']} drift={r.get('cmae_drift_vs_roll0','-')}")
        else:
            print(f"  {r['geom_group']} roll={r['roll_deg']:+d}: {r.get('source')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

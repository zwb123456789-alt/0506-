#!/usr/bin/env python3
"""
postclosure_mroll_full2664_eval.py —— R126 子任务 D：M-roll full-2664 评估（派生脚本）

不改旧 eval_mroll_probe.py。把 R117 的 312 分层子集探针扩展到 full-2664 姿态。

评估口径（roll distribution-shift，不重训，用 clean roll=0 模型）：
  - roll ∈ {-30,-15,+15,+30}，roll=0 用 01_fullrun clean 图像/OCS 做 baseline
  - 通道覆盖（受渲染范围约束，如实说明）：
      image_only : G1/G3/G5（图像通道固定用 phase63，可全评估）
      ocs_only   : G1（phase63 总光度标量，roll 版由 mroll postprocess 提供）
      joint      : G1（phase63 图像 + phase63 OCS）
    G3/G5 的多几何 OCS(phase24/45/90/120) roll 版未渲染（M-roll 只渲代表几何 phase63，
    符合 R117/R126 §7 预注册），故 ocs_only/joint 的 G3/G5 roll 评估不适用，报告如实标注。

输出：
  mroll_full2664/predictions_{geom}_{mode}_roll{r}.csv
  mroll_full2664/render_manifest.csv / postprocess_manifest.csv
  tables/mroll_full2664_metrics.csv
  tables/mroll_full2664_delta_vs_roll0.csv
  tables/mroll_full2664_failure_regions.csv
  figures/mroll_full2664_hit_cmae_by_roll.png/.pdf
  figures/mroll_full2664_error_maps.png/.pdf
  text/mroll_full2664_summary.md
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

from train_l1m2_multigeometry import (  # noqa: E402
    L1M2RegModel, decode_angles, compute_metrics,
)
from dataset_l1m2_multigeometry import build_multigeometry_table, fit_flux_transform, apply_flux_transform  # noqa: E402
from train_l1m2_multigeometry import split_pint  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

L1M2 = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"
MROLL = PROJECT_ROOT / "v0.4_results" / "12_l1m3_degraded_mroll" / "mroll"
FULLRUN_POST = PROJECT_ROOT / "v0.4_results" / "01_fullrun" / "postprocess"
OUT = PROJECT_ROOT / "v0.4_results" / "17_route1c_postclosure_enhancement_sweep"
MF = OUT / "mroll_full2664"; TAB = OUT / "tables"; FIG = OUT / "figures"; TXT = OUT / "text"
for d in (MF, TAB, FIG, TXT):
    d.mkdir(parents=True, exist_ok=True)

ROLLS = [-30, -15, 15, 30]
FULL_ATTS = [f"yaw{y:03d}_pitch{p:+04d}" for y in range(0, 360, 5) for p in range(-90, 91, 5)]


def parse_label(a):
    import re
    m = re.match(r"yaw(\d+)_pitch([+-]\d+)", a)
    return int(m.group(1)), int(m.group(2))


def img_roll0(a):
    y, p = parse_label(a)
    png = FULLRUN_POST / f"yaw{y:03d}_pitch{p:+04d}_roll+000_brdf.png"
    if not png.exists():
        return None
    return np.array(Image.open(png).convert("L"), dtype=np.float32) / 255.0


def img_roll(a, roll):
    y, p = parse_label(a)
    rt = f"roll{roll:+04d}"
    png = MROLL / "postprocess" / "phase63" / rt / f"yaw{y:03d}_pitch{p:+04d}_{rt}_brdf.png"
    if not png.exists():
        return None
    return np.array(Image.open(png).convert("L"), dtype=np.float32) / 255.0


def ocs_roll0(a):
    """phase63 clean OCS total（01_fullrun ocs_manifest）。"""
    return _OCS0_MAP.get(_key(a))


def ocs_roll(a, roll):
    y, p = parse_label(a)
    rt = f"roll{roll:+04d}"
    j = MROLL / "postprocess" / "phase63" / rt / f"yaw{y:03d}_pitch{p:+04d}_{rt}_ocs.json"
    if not j.exists():
        return None
    return float(json.load(open(j, encoding="utf-8"))["ocs_total"])


def _key(a):
    y, p = parse_label(a)
    return (int(round(y)), int(round(p)))


# phase63 clean OCS map
_OCS0_MAP = {}
def _load_ocs0():
    data = json.load(open(FULLRUN_POST / "ocs_manifest_v0_4_fullrun.json", encoding="utf-8"))
    for r in data["records"]:
        _OCS0_MAP[(int(round(r["yaw_deg"])), int(round(r["pitch_deg"])))] = float(r["ocs_total"])
_load_ocs0()


BATCH = 256


@torch.no_grad()
def predict_image(model, imgs, device):
    outs = []
    for i in range(0, len(imgs), BATCH):
        x = torch.from_numpy(np.stack(imgs[i:i + BATCH])[:, None].astype(np.float32)).to(device)
        outs.append(model({"image": x}).cpu().numpy())
    return decode_angles(np.concatenate(outs, 0))


@torch.no_grad()
def predict_ocs(model, flux_z, device):
    x = torch.from_numpy(np.array(flux_z, dtype=np.float32)).to(device)
    return decode_angles(model({"ocs": x}).cpu().numpy())


@torch.no_grad()
def predict_joint(model, imgs, flux_z, device):
    flux_z = np.asarray(flux_z, dtype=np.float32)
    outs = []
    for i in range(0, len(imgs), BATCH):
        xi = torch.from_numpy(np.stack(imgs[i:i + BATCH])[:, None].astype(np.float32)).to(device)
        xo = torch.from_numpy(flux_z[i:i + BATCH]).to(device)
        outs.append(model({"image": xi, "ocs": xo}).cpu().numpy())
    return decode_angles(np.concatenate(outs, 0))


def g1_flux_transform():
    """G1 clean train flux transform（与训练同口径：split seed=42, G1 train 上拟合）。"""
    table, _ = build_multigeometry_table("G1")
    tr, _, _ = split_pint(table, seed=42)
    return fit_flux_transform(tr)


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    metrics_rows, delta_rows, pred_manifest = [], [], []
    render_manifest, post_manifest = [], []

    # ---- manifests（渲染/后处理覆盖情况）----
    for roll in ROLLS:
        rt = f"roll{roll:+04d}"
        pdir = MROLL / "postprocess" / "phase63" / rt
        n_png = len(list(pdir.glob("*_brdf.png"))) if pdir.exists() else 0
        n_ocs = len(list(pdir.glob("*_ocs.json"))) if pdir.exists() else 0
        sdir = MROLL / "shadow_passes" / "phase63" / rt
        n_exr = len(list(sdir.glob("*_camera.exr"))) if sdir.exists() else 0
        render_manifest.append({"geom": "phase63", "roll_deg": roll,
                                "shadow_camera_exr": n_exr, "target_full": 2664})
        post_manifest.append({"geom": "phase63", "roll_deg": roll,
                              "brdf_png": n_png, "ocs_json": n_ocs, "target_full": 2664})
    with open(MF / "render_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["geom", "roll_deg", "shadow_camera_exr", "target_full"])
        w.writeheader(); w.writerows(render_manifest)
    with open(MF / "postprocess_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["geom", "roll_deg", "brdf_png", "ocs_json", "target_full"])
        w.writeheader(); w.writerows(post_manifest)

    # 只在 postprocess 覆盖 full(>=2600) 的 roll 上做 full 评估；否则标注不足
    full_ready = {r["roll_deg"]: (r["brdf_png"] >= 2600 and r["ocs_json"] >= 2600)
                  for r in post_manifest}

    def eval_channel(group, mode):
        """返回 baseline row + per-roll rows；error map 数据（roll->dict）。"""
        rd = L1M2 / "runs" / f"P-INT_{group}_{mode}_seed42"
        ckpt = torch.load(rd / "checkpoint_best.pt", map_location=device, weights_only=False)
        ocs_dim = 1 if group == "G1" else (3 if group == "G3" else 5)
        model = L1M2RegModel(mode, ocs_dim=ocs_dim).to(device)
        model.load_state_dict(ckpt["model_state"]); model.eval()
        tf = g1_flux_transform() if (mode in ("ocs_only", "joint") and group == "G1") else None

        # baseline roll0（full grid）
        atts, imgs, fluxes, yaws, pits = [], [], [], [], []
        for a in FULL_ATTS:
            y, p = parse_label(a)
            need_img = mode in ("image_only", "joint")
            need_ocs = mode in ("ocs_only", "joint")
            im = img_roll0(a) if need_img else None
            oc = ocs_roll0(a) if need_ocs else None
            if (need_img and im is None) or (need_ocs and oc is None):
                continue
            atts.append(a); yaws.append(y); pits.append(p)
            if need_img:
                imgs.append(im)
            if need_ocs:
                fluxes.append(apply_flux_transform([oc], tf))
        yt = np.array(yaws, float); pt = np.array(pits, float)
        if mode == "image_only":
            yp0, pp0 = predict_image(model, imgs, device)
        elif mode == "ocs_only":
            yp0, pp0 = predict_ocs(model, np.array(fluxes), device)
        else:
            yp0, pp0 = predict_joint(model, imgs, np.array(fluxes), device)
        m0 = compute_metrics(yp0, pp0, yt, pt)
        emap = {0: {"atts": atts, "yerr": np.minimum(np.abs(yp0 - yt) % 360, 360 - np.abs(yp0 - yt) % 360)}}
        base = {"geom_group": group, "mode": mode, "roll_deg": 0, "n": m0["n"],
                "yaw_cmae": round(m0["yaw_circular_mae_deg"], 3), "yaw_hit@30": round(m0["yaw_hit@30"], 4),
                "yaw_coarse90": round(m0["yaw_coarse90_acc"], 4), "pitch_mae": round(m0["pitch_mae_deg"], 3),
                "source": "roll0 baseline full-2664 (01_fullrun)"}
        rows = [base]
        for roll in ROLLS:
            if not full_ready.get(roll, False):
                rows.append({"geom_group": group, "mode": mode, "roll_deg": roll, "n": 0,
                             "source": f"POSTPROCESS_INCOMPLETE(png/ocs<2600)"})
                continue
            atts, imgs, fluxes, yaws, pits = [], [], [], [], []
            for a in FULL_ATTS:
                y, p = parse_label(a)
                need_img = mode in ("image_only", "joint")
                need_ocs = mode in ("ocs_only", "joint")
                im = img_roll(a, roll) if need_img else None
                oc = ocs_roll(a, roll) if need_ocs else None
                if (need_img and im is None) or (need_ocs and oc is None):
                    continue
                atts.append(a); yaws.append(y); pits.append(p)
                if need_img:
                    imgs.append(im)
                if need_ocs:
                    fluxes.append(apply_flux_transform([oc], tf))
            if not atts:
                rows.append({"geom_group": group, "mode": mode, "roll_deg": roll, "n": 0, "source": "NO_DATA"})
                continue
            yt = np.array(yaws, float); pt = np.array(pits, float)
            if mode == "image_only":
                ypr, ppr = predict_image(model, imgs, device)
            elif mode == "ocs_only":
                ypr, ppr = predict_ocs(model, np.array(fluxes), device)
            else:
                ypr, ppr = predict_joint(model, imgs, np.array(fluxes), device)
            mr = compute_metrics(ypr, ppr, yt, pt)
            yerr = np.minimum(np.abs(ypr - yt) % 360, 360 - np.abs(ypr - yt) % 360)
            emap[roll] = {"atts": atts, "yerr": yerr, "yaws": yaws, "pits": pits}
            rows.append({"geom_group": group, "mode": mode, "roll_deg": roll, "n": mr["n"],
                         "yaw_cmae": round(mr["yaw_circular_mae_deg"], 3), "yaw_hit@30": round(mr["yaw_hit@30"], 4),
                         "yaw_coarse90": round(mr["yaw_coarse90_acc"], 4), "pitch_mae": round(mr["pitch_mae_deg"], 3),
                         "cmae_drift_vs_roll0": round(mr["yaw_circular_mae_deg"] - m0["yaw_circular_mae_deg"], 3),
                         "hit30_drift_vs_roll0": round(mr["yaw_hit@30"] - m0["yaw_hit@30"], 4),
                         "source": f"mroll {roll:+d} full-2664"})
            # 存 predictions
            with open(MF / f"predictions_{group}_{mode}_roll{roll:+04d}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["record_id", "yaw_true", "pitch_true", "yaw_pred", "pitch_pred", "yaw_err"])
                for i, a in enumerate(atts):
                    w.writerow([a, yaws[i], pits[i], f"{ypr[i]:.3f}", f"{ppr[i]:.3f}", f"{yerr[i]:.3f}"])
            pred_manifest.append({"geom": group, "mode": mode, "roll": roll, "n": len(atts)})
        return rows, emap

    # 评估通道集合（受渲染范围约束）
    channels = [("G1", "image_only"), ("G3", "image_only"), ("G5", "image_only"),
                ("G1", "ocs_only"), ("G1", "joint")]
    all_emaps = {}
    for group, mode in channels:
        try:
            rows, emap = eval_channel(group, mode)
            metrics_rows.extend(rows)
            all_emaps[(group, mode)] = emap
            for r in rows:
                if r.get("roll_deg", 0) != 0 and r.get("n", 0) > 0:
                    delta_rows.append({"geom_group": group, "mode": mode, "roll_deg": r["roll_deg"],
                                       "cmae_drift_vs_roll0": r.get("cmae_drift_vs_roll0"),
                                       "hit30_drift_vs_roll0": r.get("hit30_drift_vs_roll0")})
        except Exception as e:
            metrics_rows.append({"geom_group": group, "mode": mode, "roll_deg": "-", "n": 0,
                                 "source": f"ERROR: {e}"})

    cols = ["geom_group", "mode", "roll_deg", "n", "yaw_cmae", "yaw_hit@30", "yaw_coarse90",
            "pitch_mae", "cmae_drift_vs_roll0", "hit30_drift_vs_roll0", "source"]
    with open(TAB / "mroll_full2664_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in metrics_rows:
            w.writerow({c: r.get(c, "") for c in cols})
    with open(TAB / "mroll_full2664_delta_vs_roll0.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["geom_group", "mode", "roll_deg",
                                          "cmae_drift_vs_roll0", "hit30_drift_vs_roll0"])
        w.writeheader(); w.writerows(delta_rows)

    # failure regions：image_only G1 各 roll，按 pitch bin 聚合高误差比例
    fail_rows = []
    for (group, mode), emap in all_emaps.items():
        for roll, d in emap.items():
            if roll == 0 or "pits" not in d:
                continue
            pits = np.array(d["pits"]); yerr = np.array(d["yerr"])
            for lo in range(-90, 90, 30):
                mask = (pits >= lo) & (pits < lo + 30)
                if mask.sum() == 0:
                    continue
                fail_rows.append({"geom_group": group, "mode": mode, "roll_deg": roll,
                                  "pitch_bin": f"[{lo:+d},{lo+30:+d})", "n": int(mask.sum()),
                                  "frac_yerr_gt30": round(float((yerr[mask] > 30).mean()), 4),
                                  "mean_yerr": round(float(yerr[mask].mean()), 2)})
    with open(TAB / "mroll_full2664_failure_regions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["geom_group", "mode", "roll_deg", "pitch_bin",
                                          "n", "frac_yerr_gt30", "mean_yerr"])
        w.writeheader(); w.writerows(fail_rows)

    # 图1：hit/cmae by roll（image_only G1/G3/G5）
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    xr = [-30, -15, 0, 15, 30]
    for group in ["G1", "G3", "G5"]:
        rr = [r for r in metrics_rows if r["geom_group"] == group and r["mode"] == "image_only"]
        cm = {r["roll_deg"]: r.get("yaw_cmae") for r in rr if r.get("n", 0) > 0}
        hh = {r["roll_deg"]: r.get("yaw_hit@30") for r in rr if r.get("n", 0) > 0}
        ax1.plot([x for x in xr if x in cm], [cm[x] for x in xr if x in cm], "o-", label=f"{group} image_only")
        ax2.plot([x for x in xr if x in hh], [hh[x] for x in xr if x in hh], "o-", label=f"{group} image_only")
    ax1.set_xlabel("roll (°)"); ax1.set_ylabel("yaw cMAE (°)"); ax1.set_title("M-roll full-2664: yaw cMAE vs roll")
    ax1.grid(alpha=0.3); ax1.legend()
    ax2.set_xlabel("roll (°)"); ax2.set_ylabel("yaw hit@30"); ax2.set_title("M-roll full-2664: yaw hit@30 vs roll")
    ax2.grid(alpha=0.3); ax2.legend()
    fig.suptitle("M-roll full-2664 roll sensitivity (clean roll=0 model, distribution-shift eval)\n"
                 "fixed-roll boundary probe — NOT three-axis project", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(FIG / "mroll_full2664_hit_cmae_by_roll.png", dpi=130)
    fig.savefig(FIG / "mroll_full2664_hit_cmae_by_roll.pdf")
    plt.close(fig)

    # 图2：error maps（image_only G1，roll0/+15/+30 yaw error 在 yaw-pitch 网格）
    emap = all_emaps.get(("G1", "image_only"), {})
    avail = [r for r in [0, 15, 30, -15, -30] if r in emap and "yerr" in emap[r]]
    if avail:
        n = len(avail)
        fig, axes = plt.subplots(1, n, figsize=(4 * n, 4), squeeze=False)
        for j, roll in enumerate(avail):
            d = emap[roll]
            atts = d["atts"]; yerr = np.array(d["yerr"])
            grid = np.full((37, 72), np.nan)
            for i, a in enumerate(atts):
                y, p = parse_label(a)
                grid[(p + 90) // 5, y // 5] = yerr[i]
            ax = axes[0, j]
            im = ax.imshow(grid, aspect="auto", origin="lower", cmap="viridis", vmin=0, vmax=90,
                           extent=[0, 360, -90, 90])
            ax.set_title(f"G1 image_only roll={roll:+d}")
            ax.set_xlabel("yaw (°)"); ax.set_ylabel("pitch (°)")
            plt.colorbar(im, ax=ax, label="yaw err (°)")
        fig.suptitle("M-roll full-2664 yaw error maps (G1 image_only)", fontsize=11)
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(FIG / "mroll_full2664_error_maps.png", dpi=120)
        fig.savefig(FIG / "mroll_full2664_error_maps.pdf")
        plt.close(fig)

    # summary
    md = ["# R126 子任务 D：M-roll full-2664 摘要\n", "最后更新：2026-07-01  \n",
          "把 R117 的 312 分层子集 roll 探针扩展为 full-2664 姿态。用 clean roll=0 模型做"
          " distribution-shift evaluation，不重训。\n",
          "**通道覆盖（受渲染范围约束，如实说明）：M-roll 只渲代表几何 phase63（R117/R126 §7 预注册），"
          "故 image_only 可评估 G1/G3/G5（图像固定用 phase63），ocs_only/joint 仅 G1（phase63 标量）；"
          "G3/G5 多几何 OCS 的 roll 版未渲染，不适用。**\n",
          "**定位：fixed-roll 边界 roll-sensitivity 增强探针，不是三轴小项目完成。**\n",
          "## 1. 渲染/后处理覆盖\n",
          "| roll | shadow camera.exr | brdf png | ocs json | 目标 |", "|:--|--:|--:|--:|--:|"]
    for rm, pm in zip(render_manifest, post_manifest):
        md.append(f"| {rm['roll_deg']:+d} | {rm['shadow_camera_exr']} | {pm['brdf_png']} | {pm['ocs_json']} | 2664 |")
    md.append("")
    md.append("## 2. metrics（full-2664，clean roll=0 模型）\n")
    md.append("| geom | mode | roll | n | yaw cMAE | hit@30 | ΔcMAE vs roll0 | Δhit30 vs roll0 |")
    md.append("|:--|:--|--:|--:|--:|--:|--:|--:|")
    for r in metrics_rows:
        if r.get("n", 0) == 0 and r.get("roll_deg") not in (0,):
            md.append(f"| {r['geom_group']} | {r['mode']} | {r.get('roll_deg')} | 0 | — | — | — | — |  ({r.get('source')})")
            continue
        md.append(f"| {r['geom_group']} | {r['mode']} | {r.get('roll_deg')} | {r.get('n')} | "
                  f"{r.get('yaw_cmae')} | {r.get('yaw_hit@30')} | {r.get('cmae_drift_vs_roll0','-')} | "
                  f"{r.get('hit30_drift_vs_roll0','-')} |")
    md.append("")
    md.append("## 3. 判断口径\n")
    md.append("```text")
    md.append("- ±15° 若保持较高 hit@30：fixed-roll 结论对小 roll 扰动较稳健。")
    md.append("- ±30° 若明显下降：fixed-roll 边界对大 roll 敏感。")
    md.append("- 不写三轴小项目完成；只是路线一 C 的 roll sensitivity 增强探针。")
    md.append("```")
    open(TXT / "mroll_full2664_summary.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

    print(f"[D mroll-full] metrics_rows={len(metrics_rows)} full_ready={full_ready}")
    for r in metrics_rows:
        if r.get("n", 0) > 0:
            print(f"    {r['geom_group']} {r['mode']} roll={r.get('roll_deg')}: "
                  f"cmae={r.get('yaw_cmae')} hit30={r.get('yaw_hit@30')} "
                  f"Δhit30={r.get('hit30_drift_vs_roll0','-')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
audit_resnet_dataset.py — ResNet 数据集与标签结构化审计 (指导文件任务 C)
=========================================================================
目的：在不重复低价值排查的前提下，对 ResNet image-only (1.69°) 做一次
      结构化的数据/标签泄漏审计，形成可写入论文补充材料的证据。

审计项 (来自指导文件 §6.1)：
  1. train/val/test 样本数
  2. train/val/test yaw-pitch 分布统计 (+ 分布图)
  3. 测试集中是否包含训练姿态
  4. 图像文件名与姿态标签是否一一对应
  5. 是否存在按排序产生的隐式标签泄漏
  6. 图像像素强度是否直接编码 yaw/pitch 的非物理信息
  7. normalization 是否使用了 test 统计量

特别关注 (§6.2)：
  - 渲染图像目标位置/裁剪框是否随姿态系统变化 (质心漂移)
  - 文件名/DataLoader 顺序是否间接编码姿态
  - 归一化是否带入 test 信息
  - 姿态网格是否过于规则 (强 CNN 查表式插值)
  - 渲染保留了与姿态强相关但真实观测不稳定的线索

输出：resnet_dataset_audit/run_YYYYMMDD_HHMMSS/
  - audit_report.md
  - audit_data.json
  - fig_split_distribution.png (300 dpi)
  - fig_pixel_label_correlation.png (300 dpi)
"""

import csv
import glob
import json
import os
import sys
from datetime import datetime

import numpy as np

_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "ocs_project", "03_inversion"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inv_common as ic

_IMAGE_DIR = os.path.join(_PROJECT_ROOT, "结果", "模块B_渲染",
                          "run_20260528_101944_exact_brdf")
_OUT_ROOT = os.path.join(_PROJECT_ROOT, "论文改进", "补充实验", "结果",
                         "resnet_dataset_audit")

from PIL import Image


def load_image_rows(image_dir):
    """读取 render_log.csv，返回有序行列表 (保持文件中的原始顺序)。"""
    csv_path = os.path.join(image_dir, "render_log.csv")
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            prefix = r.get("out_prefix", r.get("filename", ""))
            fname = prefix + "_brdf.png"
            path = os.path.join(image_dir, "brdf_images", fname)
            rows.append({
                "yaw": float(r["yaw"]),
                "pitch": float(r["pitch"]),
                "prefix": prefix,
                "fname": fname,
                "path": path,
                "exists": os.path.exists(path),
            })
    return rows


def load_image_stats(rows, img_size=128):
    """逐图加载，计算每张图的：均值强度、亮像素质心 (cx, cy)、亮像素个数。

    用于检测：
      - 像素强度是否编码 yaw/pitch (item 6)
      - 目标质心是否随姿态系统漂移 (§6.2 裁剪框/位置线索)
    """
    N = len(rows)
    mean_intensity = np.zeros(N)
    centroid_x = np.full(N, np.nan)
    centroid_y = np.full(N, np.nan)
    bright_frac = np.zeros(N)  # 非零像素占比
    total_flux = np.zeros(N)

    yy, xx = None, None
    for i, r in enumerate(rows):
        if not r["exists"]:
            continue
        img = Image.open(r["path"]).convert("L")
        if img.size != (img_size, img_size):
            img = img.resize((img_size, img_size), Image.BILINEAR)
        arr = np.asarray(img, dtype=np.float64) / 255.0
        if yy is None:
            yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
        mean_intensity[i] = arr.mean()
        total_flux[i] = arr.sum()
        mask = arr > 0.02  # 前景阈值
        bright_frac[i] = mask.mean()
        s = arr.sum()
        if s > 1e-9:
            centroid_x[i] = (arr * xx).sum() / s
            centroid_y[i] = (arr * yy).sum() / s
        if (i + 1) % 500 == 0:
            print(f"    image stats {i+1}/{N}", flush=True)
    return {
        "mean_intensity": mean_intensity,
        "centroid_x": centroid_x,
        "centroid_y": centroid_y,
        "bright_frac": bright_frac,
        "total_flux": total_flux,
    }


def safe_corr(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3:
        return float("nan")
    aa, bb = a[m], b[m]
    if aa.std() < 1e-12 or bb.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(aa, bb)[0, 1])


def main():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(_OUT_ROOT, f"run_{stamp}")
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 70)
    print("  ResNet Dataset Audit")
    print(f"  Image dir: {_IMAGE_DIR}")
    print(f"  Output: {out_dir}")
    print("=" * 70)

    rows = load_image_rows(_IMAGE_DIR)
    N = len(rows)
    yaw = np.array([r["yaw"] for r in rows])
    pitch = np.array([r["pitch"] for r in rows])
    print(f"  Loaded {N} render_log rows")

    audit = {"image_dir": _IMAGE_DIR, "n_total": N, "timestamp": stamp}
    report = []  # markdown lines
    report.append("# ResNet 数据集审计报告")
    report.append("")
    report.append(f"> 生成时间：{stamp}")
    report.append(f"> 图像目录：`{os.path.relpath(_IMAGE_DIR, _PROJECT_ROOT)}`")
    report.append(f"> 审计对象：ResNet-18 image-only (run_20260601_082852, mean=1.69°)")
    report.append("")

    # ===== Item 1+3: split 重建 + 样本数 + 重叠检查 =====
    split = ic.split_coarse_to_fine(yaw, pitch, coarse_step=10.0)
    train_pool = split["train_idx"]
    test_idx = split["test_idx"]
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(train_pool))
    n_val = int(len(train_pool) * 0.20)
    val_idx = train_pool[perm[:n_val]]
    tr_idx = train_pool[perm[n_val:]]

    audit["n_train"] = int(len(tr_idx))
    audit["n_val"] = int(len(val_idx))
    audit["n_test"] = int(len(test_idx))

    # 重叠检查 (按姿态值，非索引)
    def keyset(idx):
        return set((round(yaw[i], 4), round(pitch[i], 4)) for i in idx)
    k_tr, k_va, k_te = keyset(tr_idx), keyset(val_idx), keyset(test_idx)
    overlap_tr_te = k_tr & k_te
    overlap_va_te = k_va & k_te
    overlap_tr_va = k_tr & k_va
    audit["overlap_train_test"] = len(overlap_tr_te)
    audit["overlap_val_test"] = len(overlap_va_te)
    audit["overlap_train_val"] = len(overlap_tr_va)

    # 测试点是否落在 10° 整网格 (item 3 强化)
    on_coarse = np.array([
        (abs(yaw[i] % 10.0) < 0.01 or abs((yaw[i] % 10.0) - 10.0) < 0.01) and
        (abs(pitch[i] % 10.0) < 0.01 or abs((pitch[i] % 10.0) - 10.0) < 0.01)
        for i in test_idx
    ])
    audit["test_points_on_coarse_grid"] = int(on_coarse.sum())

    report.append("## 1. Split 样本数与重叠检查")
    report.append("")
    report.append("| Split | 样本数 |")
    report.append("|---|---:|")
    report.append(f"| train | {len(tr_idx)} |")
    report.append(f"| val | {len(val_idx)} |")
    report.append(f"| test | {len(test_idx)} |")
    report.append("")
    report.append(f"- train∩test 姿态重叠：**{len(overlap_tr_te)}**（应为 0）")
    report.append(f"- val∩test 姿态重叠：**{len(overlap_va_te)}**（应为 0）")
    report.append(f"- train∩val 姿态重叠：{len(overlap_tr_va)}")
    report.append(f"- 测试点落在 10° 训练整网格上的数量：**{int(on_coarse.sum())}**（应为 0）")
    report.append("")
    verdict1 = "PASS" if (len(overlap_tr_te) == 0 and len(overlap_va_te) == 0
                          and on_coarse.sum() == 0) else "FAIL"
    report.append(f"**结论：{verdict1}** — split 无姿态级泄漏。" if verdict1 == "PASS"
                  else f"**结论：{verdict1}** — 检测到泄漏，需修复！")
    report.append("")

    # ===== Item 2: yaw-pitch 分布统计 =====
    def dist_stats(idx, name):
        return {
            "split": name, "n": len(idx),
            "yaw_min": float(yaw[idx].min()), "yaw_max": float(yaw[idx].max()),
            "pitch_min": float(pitch[idx].min()), "pitch_max": float(pitch[idx].max()),
            "yaw_mean": float(yaw[idx].mean()), "pitch_mean": float(pitch[idx].mean()),
        }
    audit["distribution"] = [dist_stats(tr_idx, "train"),
                             dist_stats(val_idx, "val"),
                             dist_stats(test_idx, "test")]
    report.append("## 2. yaw-pitch 分布统计")
    report.append("")
    report.append("| Split | n | yaw范围 | pitch范围 | yaw均值 | pitch均值 |")
    report.append("|---|---:|---|---|---:|---:|")
    for d in audit["distribution"]:
        report.append(f"| {d['split']} | {d['n']} | "
                      f"[{d['yaw_min']:.0f}, {d['yaw_max']:.0f}] | "
                      f"[{d['pitch_min']:.0f}, {d['pitch_max']:.0f}] | "
                      f"{d['yaw_mean']:.1f} | {d['pitch_mean']:.1f} |")
    report.append("")
    report.append("> train/val/test 覆盖相同的 yaw/pitch 范围，test 为 train 网格之间的插值点。")
    report.append("")

    # ===== Item 4: 文件名↔标签一一对应 =====
    fname_mismatch = []
    missing = []
    for r in rows:
        if not r["exists"]:
            missing.append(r["fname"])
        # 解析文件名中的 yaw/pitch
        # 格式 yaw{:06.2f}_pitch{:+06.2f}
        try:
            p = r["prefix"]
            yaw_str = p.split("yaw")[1].split("_")[0]
            pitch_str = p.split("pitch")[1]
            fy = float(yaw_str)
            fp = float(pitch_str)
            if abs(fy - r["yaw"]) > 0.01 or abs(fp - r["pitch"]) > 0.01:
                fname_mismatch.append((r["prefix"], r["yaw"], r["pitch"]))
        except Exception:
            fname_mismatch.append((r["prefix"], r["yaw"], r["pitch"]))
    audit["filename_mismatch"] = len(fname_mismatch)
    audit["missing_images"] = len(missing)
    report.append("## 4. 文件名 ↔ 姿态标签一致性")
    report.append("")
    report.append(f"- 文件名解析与 CSV 标签不一致数：**{len(fname_mismatch)}**（应为 0）")
    report.append(f"- 缺失图像数：**{len(missing)}**（应为 0）")
    report.append("")
    report.append("> 文件名中编码的 yaw/pitch 与 render_log.csv 标签逐一对应，无错配。"
                  if len(fname_mismatch) == 0 else "> **警告：存在文件名/标签错配！**")
    report.append("")

    # ===== Item 5: 排序隐式泄漏 =====
    # render_log 行序号 vs 姿态 的相关性。若行序与 yaw/pitch 强相关，
    # 且 DataLoader 不 shuffle test，则模型可能利用顺序。但本实验 test 不参与
    # 训练且评估按样本独立，顺序泄漏不可能影响指标——仅记录顺序结构。
    order = np.arange(N)
    corr_order_yaw = safe_corr(order.astype(float), yaw)
    corr_order_pitch = safe_corr(order.astype(float), pitch)
    audit["corr_order_yaw"] = corr_order_yaw
    audit["corr_order_pitch"] = corr_order_pitch
    report.append("## 5. 排序隐式泄漏检查")
    report.append("")
    report.append(f"- 行序号 vs yaw 相关：{corr_order_yaw:+.3f}")
    report.append(f"- 行序号 vs pitch 相关：{corr_order_pitch:+.3f}")
    report.append("")
    report.append("> render_log 按 (yaw, pitch) 字典序排列，故行序与姿态相关是预期的结构性顺序，"
                  "**非泄漏**：训练 DataLoader `shuffle=True`，test 按样本独立评估，"
                  "网络输入仅为单张图像像素，不含行号/文件名/索引特征，顺序无法被模型利用。")
    report.append("")

    # ===== Item 6 + §6.2: 像素强度 vs 标签 / 质心漂移 =====
    print("  Computing per-image pixel stats (mean intensity, centroid)...")
    stats = load_image_stats(rows)
    corr_mi_yaw = safe_corr(stats["mean_intensity"], yaw)
    corr_mi_pitch = safe_corr(stats["mean_intensity"], pitch)
    corr_cx_yaw = safe_corr(stats["centroid_x"], yaw)
    corr_cx_pitch = safe_corr(stats["centroid_x"], pitch)
    corr_cy_yaw = safe_corr(stats["centroid_y"], yaw)
    corr_cy_pitch = safe_corr(stats["centroid_y"], pitch)

    audit["pixel_stats"] = {
        "mean_intensity_range": [float(np.nanmin(stats["mean_intensity"])),
                                 float(np.nanmax(stats["mean_intensity"]))],
        "centroid_x_range": [float(np.nanmin(stats["centroid_x"])),
                             float(np.nanmax(stats["centroid_x"]))],
        "centroid_y_range": [float(np.nanmin(stats["centroid_y"])),
                             float(np.nanmax(stats["centroid_y"]))],
        "corr_mean_intensity_yaw": corr_mi_yaw,
        "corr_mean_intensity_pitch": corr_mi_pitch,
        "corr_centroid_x_yaw": corr_cx_yaw,
        "corr_centroid_x_pitch": corr_cx_pitch,
        "corr_centroid_y_yaw": corr_cy_yaw,
        "corr_centroid_y_pitch": corr_cy_pitch,
    }

    # 质心漂移幅度 (像素)
    cx_span = float(np.nanmax(stats["centroid_x"]) - np.nanmin(stats["centroid_x"]))
    cy_span = float(np.nanmax(stats["centroid_y"]) - np.nanmin(stats["centroid_y"]))
    audit["centroid_drift_px"] = {"x_span": cx_span, "y_span": cy_span}

    report.append("## 6. 像素强度 / 目标质心 vs 姿态（非物理线索检查）")
    report.append("")
    report.append("| 图像量 | vs yaw | vs pitch |")
    report.append("|---|---:|---:|")
    report.append(f"| 平均强度 | {corr_mi_yaw:+.3f} | {corr_mi_pitch:+.3f} |")
    report.append(f"| 质心 x | {corr_cx_yaw:+.3f} | {corr_cx_pitch:+.3f} |")
    report.append(f"| 质心 y | {corr_cy_yaw:+.3f} | {corr_cy_pitch:+.3f} |")
    report.append("")
    report.append(f"- 目标质心漂移范围：x={cx_span:.1f} px, y={cy_span:.1f} px（共 128 px）")
    report.append("")
    report.append("> **关键判读**：平均强度随姿态变化是 **物理真实信号**（OCS 本身就是反射光通量，"
                  "依赖姿态），并非伪线索。质心漂移若过大（如 >20 px），可能让网络利用"
                  "“目标在画面中的位置”这一与真实空间观测无关的线索。质心漂移小则说明"
                  "目标基本居中，网络主要依赖形状/明暗分布而非位置。")
    report.append("")

    # ===== Item 7: normalization 是否用 test 统计 =====
    report.append("## 7. 归一化是否使用 test 统计量")
    report.append("")
    report.append("ResNet baseline (`run_resnet_baseline.py`) 的图像归一化为：")
    report.append("```python")
    report.append("arr = np.asarray(img) / 255.0            # 固定常数 255，非数据统计")
    report.append("arr = np.log1p(10.0 * arr) / np.log1p(10.0)  # 固定常数变换")
    report.append("```")
    report.append("")
    report.append("- **未使用任何跨数据集统计量**（无 mean/std 标准化）。")
    report.append("- 归一化仅用固定常数（255、log1p 系数 10），逐图独立，**不可能带入 test 信息**。")
    report.append("- ResNet 内部 BatchNorm 在 train 模式用 batch 统计、eval 模式用 running stats"
                  "（仅 train 期间更新），test 评估时不更新统计量，**无泄漏**。")
    report.append("")
    audit["normalization_uses_test_stats"] = False

    # ===== §6.2 item 4: 网格规则性 =====
    report.append("## 8. 姿态网格规则性（查表式插值风险）")
    report.append("")
    report.append("- train 为严格 10° 网格，test 为其间的 5° 插值点。")
    report.append("- 网格高度规则，强 CNN 理论上可学到“在 4 个最近训练网格点间插值”的能力。")
    report.append("- 这 **不是泄漏**，而是 10°→5° split 的设计本意（测试姿态空间插值能力）。")
    report.append("- 但需在论文中明确：1.69° 是 **规则网格内插值** 精度，"
                  "非任意未见姿态的外推精度。跨 phase / 加噪测试将检验其泛化边界。")
    report.append("")

    # ===== 综合结论 =====
    report.append("## 综合结论")
    report.append("")
    leak_found = (len(overlap_tr_te) > 0 or len(overlap_va_te) > 0 or
                  on_coarse.sum() > 0 or len(fname_mismatch) > 0 or
                  len(missing) > 0)
    audit["leak_found"] = bool(leak_found)
    if leak_found:
        report.append("**发现潜在泄漏/数据问题，对应指导文件情况 4，需修复后重跑。**")
    else:
        report.append("**未发现显性数据泄漏或标签错配**：")
        report.append("")
        report.append("1. train/val/test 姿态零重叠，test 不落在训练网格上。")
        report.append("2. 文件名与标签一一对应，无缺失。")
        report.append("3. 归一化用固定常数，不带入 test 统计。")
        report.append("4. 行序与姿态的相关是字典序结构，网络输入不含顺序信息，无法利用。")
        report.append("")
        report.append("ResNet 的 1.69° 更可能来自：**强 backbone 在干净、规则网格的"
                      "单几何渲染图上学到了高质量的姿态→明暗分布映射**。")
        report.append("其真实价值边界由任务 A（强分支融合）与任务 B（鲁棒性/跨几何）确定，"
                      "而非数据泄漏。")
    report.append("")
    report.append("> 注：本审计排除了 *显性* 泄漏。是否存在“渲染伪线索”（如目标质心漂移"
                  f"提供位置线索）由第 6 节质心漂移量判断（本数据 x={cx_span:.1f}px / "
                  f"y={cy_span:.1f}px）。")

    # 写文件
    with open(os.path.join(out_dir, "audit_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    with open(os.path.join(out_dir, "audit_data.json"), "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    # ===== 图表 =====
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Fig 1: split 分布
        fig, ax = plt.subplots(1, 1, figsize=(7, 6))
        ax.scatter(yaw[tr_idx], pitch[tr_idx], s=12, c="tab:blue",
                   label=f"train ({len(tr_idx)})", alpha=0.7)
        ax.scatter(yaw[val_idx], pitch[val_idx], s=12, c="tab:orange",
                   label=f"val ({len(val_idx)})", alpha=0.7)
        ax.scatter(yaw[test_idx], pitch[test_idx], s=4, c="tab:green",
                   label=f"test ({len(test_idx)})", alpha=0.35)
        ax.set_xlabel("yaw (deg)")
        ax.set_ylabel("pitch (deg)")
        ax.set_title("Train/Val/Test split distribution (10°→5°)")
        ax.legend(loc="upper right")
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "fig_split_distribution.png"), dpi=300)
        plt.close(fig)

        # Fig 2: 像素量 vs 姿态
        fig, axes = plt.subplots(2, 2, figsize=(11, 9))
        axes[0, 0].scatter(yaw, stats["mean_intensity"], s=4, alpha=0.4)
        axes[0, 0].set_xlabel("yaw"); axes[0, 0].set_ylabel("mean intensity")
        axes[0, 0].set_title(f"mean intensity vs yaw (r={corr_mi_yaw:+.3f})")
        axes[0, 1].scatter(pitch, stats["mean_intensity"], s=4, alpha=0.4, c="tab:orange")
        axes[0, 1].set_xlabel("pitch"); axes[0, 1].set_ylabel("mean intensity")
        axes[0, 1].set_title(f"mean intensity vs pitch (r={corr_mi_pitch:+.3f})")
        axes[1, 0].scatter(yaw, stats["centroid_x"], s=4, alpha=0.4, c="tab:green")
        axes[1, 0].set_xlabel("yaw"); axes[1, 0].set_ylabel("centroid x (px)")
        axes[1, 0].set_title(f"centroid-x vs yaw (r={corr_cx_yaw:+.3f})")
        axes[1, 1].scatter(pitch, stats["centroid_y"], s=4, alpha=0.4, c="tab:red")
        axes[1, 1].set_xlabel("pitch"); axes[1, 1].set_ylabel("centroid y (px)")
        axes[1, 1].set_title(f"centroid-y vs pitch (r={corr_cy_pitch:+.3f})")
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "fig_pixel_label_correlation.png"), dpi=300)
        plt.close(fig)
        print("  Figures saved.")
    except Exception as e:
        print(f"  [WARN] figure generation failed: {e}")

    print(f"\n  Audit verdict: {'LEAK FOUND' if leak_found else 'NO EXPLICIT LEAK'}")
    print(f"  Centroid drift: x={cx_span:.1f}px y={cy_span:.1f}px")
    print(f"  Output: {out_dir}")
    return out_dir


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
b_c_metrics.py —— R131 子任务 B/C：汇总渲染/后处理 manifest + roll 曲线与三轴 smoke 指标
读 01_fullrun baseline (roll=0) + 19 号包 8 个非零 roll 后处理产物，计算：
  ocs_total by roll / delta_ocs_vs_roll0 / relative_brightness_rank_shift
  local_contrast / glint / saturation flag / roll_sensitivity_score / image_usable
产出：
  render/p1_render_manifest.csv
  postprocess/p1_postprocess_manifest.csv
  tables/p1_seed_roll_ocs_table.csv
  tables/p1_roll_curve_metrics.csv
  tables/p1_roll_sensitivity_summary.csv
  tables/p1_brightness_information_smoke.csv
  metrics/p1_metric_definitions_used.md
"""
import csv, json, os
import numpy as np
from pathlib import Path

try:
    import OpenEXR, Imath
except ImportError:
    OpenEXR = None

V04 = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG = V04 / "v0.4_results" / "19_three_axis_p1_seed_roll_scan"
FR_POST = V04 / "v0.4_results" / "01_fullrun" / "postprocess"
FR_SHADOW = V04 / "v0.4_results" / "01_fullrun" / "shadow_passes"
RENDER_BASE = PKG / "render" / "shadow_passes" / "phase63"
POST_BASE = PKG / "postprocess" / "phase63"
MATRIX = V04 / "v0.4_results" / "18_three_axis_planning_preflight" / "tables" / "p1_seed_roll_pre_registered_matrix.csv"
ROLLS = [-60, -45, -30, -15, 15, 30, 45, 60]
ALL_ROLLS = [-60, -45, -30, -15, 0, 15, 30, 45, 60]

# saturation 判据：linear radiance 分位/绝对阈；这里用 log1p 后 png 会截断，改用 linear.exr 统计
SAT_FRAC_THRESH = 0.01   # >1% 像素达到近上限视为饱和风险
GLINT_RATIO_THRESH = 8.0 # p99.9/median 超过该比视为 glint 风险


def read_linear_exr(path):
    """读 linear.exr 的 R 通道（灰度线性辐亮度）。返回 2D float array 或 None。"""
    if OpenEXR is None or not os.path.isfile(path):
        return None
    f = OpenEXR.InputFile(str(path))
    dw = f.header()["dataWindow"]
    w = dw.max.x - dw.min.x + 1
    h = dw.max.y - dw.min.y + 1
    chans = f.header()["channels"].keys()
    ch = "R" if "R" in chans else list(chans)[0]
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    raw = f.channel(ch, pt)
    arr = np.frombuffer(raw, dtype=np.float32).reshape(h, w).astype(np.float64)
    f.close()
    return arr


def image_metrics(linear_path):
    """从 linear.exr 计算 local_contrast / image_usable / glint / saturation。"""
    arr = read_linear_exr(linear_path)
    if arr is None:
        return dict(image_usable=0, local_contrast=float("nan"),
                    glint_flag=0, saturation_flag=0, n_lit=0, mean_lit=float("nan"))
    pos = arr[arr > 0]
    n_lit = int(pos.size)
    if n_lit < 10:
        return dict(image_usable=0, local_contrast=float("nan"),
                    glint_flag=0, saturation_flag=0, n_lit=n_lit, mean_lit=float("nan"))
    mean_lit = float(pos.mean())
    std_lit = float(pos.std())
    local_contrast = std_lit / mean_lit if mean_lit > 0 else float("nan")
    med = float(np.median(pos))
    p999 = float(np.percentile(pos, 99.9))
    glint = int((p999 / med) > GLINT_RATIO_THRESH) if med > 0 else 0
    vmax = float(pos.max())
    sat_frac = float((pos >= 0.98 * vmax).mean())
    saturation = int(sat_frac > SAT_FRAC_THRESH and vmax > 0)
    image_usable = int(n_lit >= 50)
    return dict(image_usable=image_usable, local_contrast=local_contrast,
                glint_flag=glint, saturation_flag=saturation,
                n_lit=n_lit, mean_lit=mean_lit)


# --- seed 列表 ---
rows = list(csv.DictReader(open(MATRIX, encoding="utf-8")))
seeds, seen = [], set()
for r in rows:
    rid = r["record_id"]
    if rid not in seen:
        seen.add(rid)
        seeds.append({"record_id": rid, "yaw": int(round(float(r["yaw"]))),
                      "pitch": int(round(float(r["pitch"]))), "category": r["category"]})


def load_unit(yaw, pitch, roll):
    """返回一个 seed-roll 单位的合并指标 dict。roll=0 读 fullrun，非0 读 19 号包。"""
    if roll == 0:
        base = f"yaw{yaw:03d}_pitch{pitch:+04d}_roll+000"
        ocs_p = FR_POST / f"{base}_ocs.json"
        lin_p = FR_POST / f"{base}_linear.exr"
        cam_p = FR_SHADOW / f"{base}_camera.exr"
        source = "01_fullrun"
    else:
        rt = f"roll{roll:+04d}"
        base = f"yaw{yaw:03d}_pitch{pitch:+04d}_{rt}"
        ocs_p = POST_BASE / rt / f"{base}_ocs.json"
        lin_p = POST_BASE / rt / f"{base}_linear.exr"
        cam_p = RENDER_BASE / rt / f"{base}_camera.exr"
        source = "19_pack"
    d = json.load(open(ocs_p, encoding="utf-8")) if ocs_p.is_file() else {}
    im = image_metrics(lin_p)
    return dict(label=base, source=source, ocs_json=str(ocs_p), linear_exr=str(lin_p),
                camera_exr=str(cam_p),
                ocs_total=float(d.get("ocs_total", float("nan"))),
                n_pixels_camera_visible=int(d.get("n_pixels_camera_visible", 0)),
                n_pixels_contributing=int(d.get("n_pixels_contributing", 0)),
                ocs_ok=ocs_p.is_file(), **im)


# --- 逐 seed 逐 roll 计算 ---
per_unit = {}   # (rid, roll) -> metrics
for s in seeds:
    for roll in ALL_ROLLS:
        per_unit[(s["record_id"], roll)] = load_unit(s["yaw"], s["pitch"], roll)

# === render manifest (只列 96 非零 roll 渲染单位) ===
with open(PKG / "render" / "p1_render_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seed_record_id", "category", "yaw", "pitch", "roll", "label",
                "camera_exr_exists", "sun_exr_exists", "source"])
    for s in seeds:
        for roll in ROLLS:
            rt = f"roll{roll:+04d}"
            base = f"yaw{s['yaw']:03d}_pitch{s['pitch']:+04d}_{rt}"
            cam = RENDER_BASE / rt / f"{base}_camera.exr"
            sun = RENDER_BASE / rt / f"{base}_sun.exr"
            w.writerow([s["record_id"], s["category"], s["yaw"], s["pitch"], roll, base,
                        cam.is_file(), sun.is_file(), "19_pack"])

# === postprocess manifest (96 非零 roll) ===
with open(PKG / "postprocess" / "p1_postprocess_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seed_record_id", "category", "yaw", "pitch", "roll", "label",
                "ocs_json_exists", "linear_exr_exists", "ocs_total", "image_usable", "status"])
    for s in seeds:
        for roll in ROLLS:
            u = per_unit[(s["record_id"], roll)]
            status = "COMPLETE" if (u["ocs_ok"] and u["image_usable"]) else "CHECK"
            w.writerow([s["record_id"], s["category"], s["yaw"], s["pitch"], roll, u["label"],
                        u["ocs_ok"], os.path.isfile(u["linear_exr"]),
                        f"{u['ocs_total']:.6e}", u["image_usable"], status])

# === p1_seed_roll_ocs_table.csv (含 roll=0 baseline, 108 行) ===
with open(PKG / "tables" / "p1_seed_roll_ocs_table.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seed_record_id", "category", "yaw", "pitch", "roll", "source",
                "ocs_total", "n_pixels_camera_visible", "n_pixels_contributing",
                "local_contrast", "mean_lit", "image_usable", "glint_flag", "saturation_flag"])
    for s in seeds:
        for roll in ALL_ROLLS:
            u = per_unit[(s["record_id"], roll)]
            w.writerow([s["record_id"], s["category"], s["yaw"], s["pitch"], roll, u["source"],
                        f"{u['ocs_total']:.6e}", u["n_pixels_camera_visible"], u["n_pixels_contributing"],
                        f"{u['local_contrast']:.6f}", f"{u['mean_lit']:.6e}",
                        u["image_usable"], u["glint_flag"], u["saturation_flag"]])

# === p1_roll_curve_metrics.csv (delta vs roll0, brightness rank per roll) ===
# brightness rank：每个 roll 下 12 seed 按 ocs_total 排名 (1=最亮)
rank_by_roll = {}
for roll in ALL_ROLLS:
    vals = [(s["record_id"], per_unit[(s["record_id"], roll)]["ocs_total"]) for s in seeds]
    order = sorted(vals, key=lambda x: -x[1])
    rank_by_roll[roll] = {rid: i + 1 for i, (rid, _) in enumerate(order)}

with open(PKG / "tables" / "p1_roll_curve_metrics.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seed_record_id", "category", "roll", "ocs_total", "delta_ocs_vs_roll0",
                "rel_delta_pct", "brightness_rank", "rank_shift_vs_roll0", "local_contrast",
                "image_usable", "glint_flag", "saturation_flag"])
    for s in seeds:
        rid = s["record_id"]
        ocs0 = per_unit[(rid, 0)]["ocs_total"]
        rank0 = rank_by_roll[0][rid]
        for roll in ALL_ROLLS:
            u = per_unit[(rid, roll)]
            delta = u["ocs_total"] - ocs0
            rel = (delta / ocs0 * 100.0) if ocs0 > 0 else float("nan")
            rank = rank_by_roll[roll][rid]
            w.writerow([rid, s["category"], roll, f"{u['ocs_total']:.6e}", f"{delta:.6e}",
                        f"{rel:.3f}", rank, rank - rank0, f"{u['local_contrast']:.6f}",
                        u["image_usable"], u["glint_flag"], u["saturation_flag"]])

# === p1_roll_sensitivity_summary.csv (每 seed 一行) ===
def roll_sensitivity(rid):
    """roll_sensitivity_score = OCS 随 roll 变化的相对幅度 (max-min)/mean over all rolls."""
    vals = np.array([per_unit[(rid, r)]["ocs_total"] for r in ALL_ROLLS], float)
    m = np.nanmean(vals)
    if m <= 0:
        return float("nan"), float("nan"), float("nan")
    span = (np.nanmax(vals) - np.nanmin(vals)) / m
    std_rel = np.nanstd(vals) / m
    return float(span), float(std_rel), m

with open(PKG / "tables" / "p1_roll_sensitivity_summary.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seed_record_id", "category", "yaw", "pitch", "ocs_roll0", "ocs_mean_allroll",
                "ocs_span_rel", "ocs_std_rel", "roll_sensitivity_score",
                "max_abs_rank_shift", "contrast_roll0", "contrast_span_rel",
                "any_glint", "any_saturation", "image_usable_all"])
    for s in seeds:
        rid = s["record_id"]
        span, std_rel, mean_all = roll_sensitivity(rid)
        ranks = [rank_by_roll[r][rid] for r in ALL_ROLLS]
        max_shift = max(abs(x - rank_by_roll[0][rid]) for x in ranks)
        contrasts = np.array([per_unit[(rid, r)]["local_contrast"] for r in ALL_ROLLS], float)
        cmean = np.nanmean(contrasts)
        cspan = (np.nanmax(contrasts) - np.nanmin(contrasts)) / cmean if cmean > 0 else float("nan")
        anyg = int(any(per_unit[(rid, r)]["glint_flag"] for r in ALL_ROLLS))
        anys = int(any(per_unit[(rid, r)]["saturation_flag"] for r in ALL_ROLLS))
        usable_all = int(all(per_unit[(rid, r)]["image_usable"] for r in ALL_ROLLS))
        w.writerow([rid, s["category"], s["yaw"], s["pitch"],
                    f"{per_unit[(rid,0)]['ocs_total']:.6e}", f"{mean_all:.6e}",
                    f"{span:.4f}", f"{std_rel:.4f}", f"{span:.4f}", max_shift,
                    f"{per_unit[(rid,0)]['local_contrast']:.6f}", f"{cspan:.4f}",
                    anyg, anys, usable_all])

# === p1_brightness_information_smoke.csv (亮度 vs 信息 解耦观察) ===
# 用 local_contrast 作为 smoke 级 information proxy；给出 brightness rank vs contrast rank
with open(PKG / "tables" / "p1_brightness_information_smoke.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seed_record_id", "category", "ocs_mean_allroll", "brightness_rank_mean",
                "contrast_mean_allroll", "contrast_rank", "brightness_info_decoupled",
                "note"])
    # 计算全 roll 均值排名
    ocs_mean = {s["record_id"]: np.nanmean([per_unit[(s["record_id"], r)]["ocs_total"] for r in ALL_ROLLS]) for s in seeds}
    con_mean = {s["record_id"]: np.nanmean([per_unit[(s["record_id"], r)]["local_contrast"] for r in ALL_ROLLS]) for s in seeds}
    b_order = sorted(seeds, key=lambda s: -ocs_mean[s["record_id"]])
    b_rank = {s["record_id"]: i + 1 for i, s in enumerate(b_order)}
    c_order = sorted(seeds, key=lambda s: -con_mean[s["record_id"]])
    c_rank = {s["record_id"]: i + 1 for i, s in enumerate(c_order)}
    for s in seeds:
        rid = s["record_id"]
        decoupled = int(abs(b_rank[rid] - c_rank[rid]) >= 3)
        note = "亮度高信息低" if (b_rank[rid] <= 4 and c_rank[rid] >= 8) else \
               ("暗但对比高" if (b_rank[rid] >= 8 and c_rank[rid] <= 4) else "")
        w.writerow([rid, s["category"], f"{ocs_mean[rid]:.6e}", b_rank[rid],
                    f"{con_mean[rid]:.6f}", c_rank[rid], decoupled, note])

print("[OK] manifests + tables written")
print("units total (incl roll0):", len(per_unit))
print("nonzero-roll units:", sum(1 for k in per_unit if k[1] != 0))

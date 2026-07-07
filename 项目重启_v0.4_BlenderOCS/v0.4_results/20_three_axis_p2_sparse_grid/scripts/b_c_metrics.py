# -*- coding: utf-8 -*-
"""
b_c_metrics.py —— R133 子任务 B/C：P2 render/postprocess manifest + 三轴指标与区域汇总

读 P2 预注册矩阵 + 20 号包 8 个非零 roll 后处理产物 + 01_fullrun baseline(roll=0)，
计算每个 (yaw,pitch,roll) 单位的三轴指标，并汇总到区域级。

产出：
  render/p2_render_manifest.csv
  postprocess/p2_postprocess_manifest.csv
  tables/p2_sparse_grid_metrics.csv
  tables/p2_region_summary.csv
  tables/p2_high_brightness_candidates.csv
  tables/p2_high_information_candidates.csv
  tables/p2_low_information_regions.csv
  tables/p2_p3_refinement_candidates.csv
  metrics/p2_metric_definitions_used.md

指标（R133 要求，全部计算）：
  ocs_total                : 单帧 OCS 总光度（后处理 ocs.json）
  brightness_rank          : 每个 roll 下 125 pose 按 ocs_total 的排名（1=最亮）
  pixel_local_contrast     : 单帧像素级 std/mean（image-level，P1 同口径）
  neighbor_contrast_ypr    : 三轴 (yaw,pitch,roll) 邻域内 OCS 的相对散布 (max-min)/mean
  roll_sensitivity_score   : 固定 (yaw,pitch) 下 OCS 随 9 roll 的相对散布 (max-min)/mean
  rank_shift               : 该 pose 在各 roll 下 brightness_rank 相对 roll=0 的最大绝对漂移
  glint_flag/saturation_flag: 单帧 glint/饱和风险（P1 同口径阈值）
  image_usable_flag        : 受照像素 >= 50
  region_utility_score     : 区域级综合效用（见 metric 定义）

roll=0 读 01_fullrun，非零 roll 读 20 号包。量纲与 baseline 一致。
不训练、不改旧目录。
"""
import csv
import json
import os
from pathlib import Path
import numpy as np

try:
    import OpenEXR
    import Imath
except ImportError:
    OpenEXR = None

V04 = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG = V04 / "v0.4_results" / "20_three_axis_p2_sparse_grid"
FR_POST = V04 / "v0.4_results" / "01_fullrun" / "postprocess"
FR_SHADOW = V04 / "v0.4_results" / "01_fullrun" / "shadow_passes"
RENDER_BASE = PKG / "render" / "shadow_passes" / "phase63"
POST_BASE = PKG / "postprocess" / "phase63"
MATRIX = PKG / "tables" / "p2_sparse_grid_pre_registered_matrix.csv"

ROLLS = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
NONZERO_ROLLS = [-60, -45, -30, -15, 15, 30, 45, 60]
YAW_OFFSETS = [-10, -5, 0, 5, 10]
PITCH_OFFSETS = [-10, -5, 0, 5, 10]

# glint/saturation 判据：与 P1 同口径
SAT_FRAC_THRESH = 0.01
GLINT_RATIO_THRESH = 8.0


def read_linear_exr(path):
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
    arr = read_linear_exr(linear_path)
    if arr is None:
        return dict(image_usable=0, pixel_local_contrast=float("nan"),
                    glint_flag=0, saturation_flag=0, n_lit=0, mean_lit=float("nan"))
    pos = arr[arr > 0]
    n_lit = int(pos.size)
    if n_lit < 10:
        return dict(image_usable=0, pixel_local_contrast=float("nan"),
                    glint_flag=0, saturation_flag=0, n_lit=n_lit, mean_lit=float("nan"))
    mean_lit = float(pos.mean())
    std_lit = float(pos.std())
    plc = std_lit / mean_lit if mean_lit > 0 else float("nan")
    med = float(np.median(pos))
    p999 = float(np.percentile(pos, 99.9))
    glint = int((p999 / med) > GLINT_RATIO_THRESH) if med > 0 else 0
    vmax = float(pos.max())
    sat_frac = float((pos >= 0.98 * vmax).mean())
    saturation = int(sat_frac > SAT_FRAC_THRESH and vmax > 0)
    image_usable = int(n_lit >= 50)
    return dict(image_usable=image_usable, pixel_local_contrast=plc,
                glint_flag=glint, saturation_flag=saturation,
                n_lit=n_lit, mean_lit=mean_lit)


# ---- 读预注册矩阵：唯一 pose 与其区域 ----
matrix_rows = list(csv.DictReader(open(MATRIX, encoding="utf-8")))
poses, seen = [], set()
for r in matrix_rows:
    key = (int(r["yaw"]), int(r["pitch"]))
    if key not in seen:
        seen.add(key)
        poses.append({"yaw": key[0], "pitch": key[1], "region": r["region"],
                      "all_regions": r["all_regions"], "category": r["category"],
                      "record_id": r["record_id"]})
POSE_KEYS = set((p["yaw"], p["pitch"]) for p in poses)
REGIONS = []
for p in poses:
    if p["region"] not in REGIONS:
        REGIONS.append(p["region"])


def load_unit(yaw, pitch, roll):
    """一个 (yaw,pitch,roll) 单位的合并指标。roll=0 读 fullrun，非0 读 20 号包。"""
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
        source = "20_pack"
    d = json.load(open(ocs_p, encoding="utf-8")) if ocs_p.is_file() else {}
    im = image_metrics(lin_p)
    return dict(label=base, source=source, ocs_json=str(ocs_p), linear_exr=str(lin_p),
                camera_exr=str(cam_p),
                ocs_total=float(d.get("ocs_total", float("nan"))),
                n_pixels_camera_visible=int(d.get("n_pixels_camera_visible", 0)),
                n_pixels_contributing=int(d.get("n_pixels_contributing", 0)),
                ocs_ok=ocs_p.is_file(), **im)


# ---- 逐 pose 逐 roll 计算 ----
print("加载 1125 个 pose-roll 单位指标（含 roll=0 baseline）...")
per_unit = {}
for p in poses:
    for roll in ROLLS:
        per_unit[(p["yaw"], p["pitch"], roll)] = load_unit(p["yaw"], p["pitch"], roll)

# ---- brightness rank：每个 roll 下 125 pose 按 ocs_total 排名 ----
rank_by_roll = {}
for roll in ROLLS:
    vals = [((p["yaw"], p["pitch"]), per_unit[(p["yaw"], p["pitch"], roll)]["ocs_total"]) for p in poses]
    order = sorted(vals, key=lambda x: -x[1])
    rank_by_roll[roll] = {k: i + 1 for i, (k, _) in enumerate(order)}


def ocs_at(yaw, pitch, roll):
    u = per_unit.get((yaw, pitch, roll))
    return u["ocs_total"] if u else float("nan")


def neighbor_contrast_ypr(yaw, pitch, roll):
    """三轴 (yaw,pitch,roll) 邻域内 OCS 的相对散布 (max-min)/mean。
    邻域 = 网格上相邻的 yaw±5 / pitch±5 / roll 相邻档（仅取存在于 P2 网格内的点）。"""
    vals = []
    ri = ROLLS.index(roll)
    roll_neighbors = [roll]
    if ri > 0:
        roll_neighbors.append(ROLLS[ri - 1])
    if ri < len(ROLLS) - 1:
        roll_neighbors.append(ROLLS[ri + 1])
    for dy in (-5, 0, 5):
        for dp in (-5, 0, 5):
            ny = (yaw + dy) % 360
            npi = pitch + dp
            if (ny, npi) not in POSE_KEYS:
                continue
            for rr in roll_neighbors:
                v = ocs_at(ny, npi, rr)
                if np.isfinite(v):
                    vals.append(v)
    if len(vals) < 2:
        return float("nan")
    vals = np.array(vals)
    m = vals.mean()
    return float((vals.max() - vals.min()) / m) if m > 0 else float("nan")


def roll_sensitivity(yaw, pitch):
    """固定 (yaw,pitch)，OCS 随 9 roll 的相对散布 (max-min)/mean。"""
    vals = np.array([ocs_at(yaw, pitch, r) for r in ROLLS], float)
    m = np.nanmean(vals)
    if m <= 0:
        return float("nan")
    return float((np.nanmax(vals) - np.nanmin(vals)) / m)


# ============================================================
# render manifest（1000 非零 roll 渲染单位）
# ============================================================
with open(PKG / "render" / "p2_render_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region", "category", "yaw", "pitch", "roll", "label",
                "camera_exr_exists", "sun_exr_exists", "source", "source_seed"])
    for p in poses:
        reg_meta = next(m for m in matrix_rows if int(m["yaw"]) == p["yaw"] and int(m["pitch"]) == p["pitch"])
        for roll in NONZERO_ROLLS:
            rt = f"roll{roll:+04d}"
            base = f"yaw{p['yaw']:03d}_pitch{p['pitch']:+04d}_{rt}"
            cam = RENDER_BASE / rt / f"{base}_camera.exr"
            sun = RENDER_BASE / rt / f"{base}_sun.exr"
            w.writerow([p["region"], p["category"], p["yaw"], p["pitch"], roll, base,
                        cam.is_file(), sun.is_file(), "20_pack", reg_meta["source_seed"]])

# ============================================================
# postprocess manifest（1000 非零 roll）
# ============================================================
with open(PKG / "postprocess" / "p2_postprocess_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region", "category", "yaw", "pitch", "roll", "label",
                "ocs_json_exists", "linear_exr_exists", "ocs_total", "image_usable", "status"])
    for p in poses:
        for roll in NONZERO_ROLLS:
            u = per_unit[(p["yaw"], p["pitch"], roll)]
            status = "COMPLETE" if (u["ocs_ok"] and u["image_usable"]) else "CHECK"
            w.writerow([p["region"], p["category"], p["yaw"], p["pitch"], roll, u["label"],
                        u["ocs_ok"], os.path.isfile(u["linear_exr"]),
                        f"{u['ocs_total']:.6e}", u["image_usable"], status])

# ============================================================
# p2_sparse_grid_metrics.csv（1125 pose-roll 行，含 roll=0 baseline）
# ============================================================
with open(PKG / "tables" / "p2_sparse_grid_metrics.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region", "category", "yaw", "pitch", "roll", "source",
                "ocs_total", "brightness_rank", "rank_shift_vs_roll0",
                "pixel_local_contrast", "neighbor_contrast_ypr", "roll_sensitivity_score",
                "n_pixels_camera_visible", "n_pixels_contributing", "mean_lit",
                "image_usable", "glint_flag", "saturation_flag"])
    for p in poses:
        y, pi = p["yaw"], p["pitch"]
        rank0 = rank_by_roll[0][(y, pi)]
        rs = roll_sensitivity(y, pi)
        for roll in ROLLS:
            u = per_unit[(y, pi, roll)]
            rank = rank_by_roll[roll][(y, pi)]
            nc = neighbor_contrast_ypr(y, pi, roll)
            w.writerow([p["region"], p["category"], y, pi, roll, u["source"],
                        f"{u['ocs_total']:.6e}", rank, rank - rank0,
                        f"{u['pixel_local_contrast']:.6f}", f"{nc:.6f}", f"{rs:.6f}",
                        u["n_pixels_camera_visible"], u["n_pixels_contributing"],
                        f"{u['mean_lit']:.6e}", u["image_usable"], u["glint_flag"], u["saturation_flag"]])

# ============================================================
# 每 pose 汇总（供区域汇总与候选清单）
# ============================================================
pose_summary = {}
for p in poses:
    y, pi = p["yaw"], p["pitch"]
    ocs_all = np.array([ocs_at(y, pi, r) for r in ROLLS], float)
    ocs_mean = float(np.nanmean(ocs_all))
    ocs_roll0 = ocs_at(y, pi, 0)
    rs = roll_sensitivity(y, pi)
    ranks = [rank_by_roll[r][(y, pi)] for r in ROLLS]
    max_rank_shift = max(abs(x - rank_by_roll[0][(y, pi)]) for x in ranks)
    plc_all = np.array([per_unit[(y, pi, r)]["pixel_local_contrast"] for r in ROLLS], float)
    plc_mean = float(np.nanmean(plc_all))
    nc_all = np.array([neighbor_contrast_ypr(y, pi, r) for r in ROLLS], float)
    nc_mean = float(np.nanmean(nc_all))
    any_glint = int(any(per_unit[(y, pi, r)]["glint_flag"] for r in ROLLS))
    any_sat = int(any(per_unit[(y, pi, r)]["saturation_flag"] for r in ROLLS))
    usable_all = int(all(per_unit[(y, pi, r)]["image_usable"] for r in ROLLS))
    pose_summary[(y, pi)] = dict(
        region=p["region"], category=p["category"], yaw=y, pitch=pi,
        ocs_mean=ocs_mean, ocs_roll0=ocs_roll0, roll_sensitivity=rs,
        max_rank_shift=max_rank_shift, pixel_contrast_mean=plc_mean,
        neighbor_contrast_mean=nc_mean, any_glint=any_glint, any_saturation=any_sat,
        image_usable_all=usable_all)

# 全局亮度/信息排名（按 pose 均值）
b_order = sorted(poses, key=lambda p: -pose_summary[(p["yaw"], p["pitch"])]["ocs_mean"])
b_rank = {(p["yaw"], p["pitch"]): i + 1 for i, p in enumerate(b_order)}
# 信息 proxy：优先 neighbor_contrast_ypr（三轴局部信息），回退 pixel contrast
info_order = sorted(poses, key=lambda p: -(pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"]
                                           if np.isfinite(pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"])
                                           else -1))
info_rank = {(p["yaw"], p["pitch"]): i + 1 for i, p in enumerate(info_order)}

# ============================================================
# region_utility_score & p2_region_summary.csv
# ============================================================
# region_utility_score 定义（见 metric 定义文档）：
#   归一化 mean_ocs、mean_neighbor_contrast、mean_roll_sensitivity 到 [0,1]，
#   utility = 0.4*info + 0.3*roll_sens + 0.3*brightness - 0.2*risk_frac
#   其中 risk_frac = 该区域触发 glint 或 saturation 的 pose 比例
def norm(vals):
    v = np.array(vals, float)
    lo, hi = np.nanmin(v), np.nanmax(v)
    if hi - lo < 1e-12:
        return np.zeros_like(v)
    return (v - lo) / (hi - lo)


region_poses = {rg: [p for p in poses if p["region"] == rg] for rg in REGIONS}
# 用全体 pose 的分布做归一化基准
all_ocs = [pose_summary[(p["yaw"], p["pitch"])]["ocs_mean"] for p in poses]
all_nc = [pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"] for p in poses]
all_rs = [pose_summary[(p["yaw"], p["pitch"])]["roll_sensitivity"] for p in poses]
ocs_lo, ocs_hi = np.nanmin(all_ocs), np.nanmax(all_ocs)
nc_lo, nc_hi = np.nanmin(all_nc), np.nanmax(all_nc)
rs_lo, rs_hi = np.nanmin(all_rs), np.nanmax(all_rs)


def nrm(v, lo, hi):
    if not np.isfinite(v) or hi - lo < 1e-12:
        return 0.0
    return float(max(0.0, min(1.0, (v - lo) / (hi - lo))))


region_rows = []
for rg in REGIONS:
    ps = region_poses[rg]
    mean_ocs = float(np.nanmean([pose_summary[(p["yaw"], p["pitch"])]["ocs_mean"] for p in ps]))
    mean_nc = float(np.nanmean([pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"] for p in ps]))
    mean_rs = float(np.nanmean([pose_summary[(p["yaw"], p["pitch"])]["roll_sensitivity"] for p in ps]))
    risk_frac = float(np.mean([1.0 if (pose_summary[(p["yaw"], p["pitch"])]["any_glint"] or
                                       pose_summary[(p["yaw"], p["pitch"])]["any_saturation"]) else 0.0
                               for p in ps]))
    usable_frac = float(np.mean([pose_summary[(p["yaw"], p["pitch"])]["image_usable_all"] for p in ps]))
    ni = nrm(mean_nc, nc_lo, nc_hi)
    nr = nrm(mean_rs, rs_lo, rs_hi)
    nb = nrm(mean_ocs, ocs_lo, ocs_hi)
    utility = 0.4 * ni + 0.3 * nr + 0.3 * nb - 0.2 * risk_frac
    region_rows.append(dict(
        region=rg, category=ps[0]["category"], n_poses=len(ps),
        mean_ocs=mean_ocs, mean_neighbor_contrast=mean_nc, mean_roll_sensitivity=mean_rs,
        risk_frac=risk_frac, usable_frac=usable_frac,
        norm_info=ni, norm_roll_sens=nr, norm_brightness=nb,
        region_utility_score=utility))

with open(PKG / "tables" / "p2_region_summary.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(region_rows[0].keys()))
    w.writeheader()
    for r in region_rows:
        rr = {k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in r.items()}
        w.writerow(rr)

# ============================================================
# 候选清单
# ============================================================
def write_candidates(path, cand, extra_cols=None):
    extra_cols = extra_cols or []
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "category", "yaw", "pitch", "ocs_mean", "ocs_roll0",
                    "brightness_rank", "info_rank", "neighbor_contrast_mean",
                    "roll_sensitivity_score", "max_rank_shift", "pixel_contrast_mean",
                    "any_glint", "any_saturation", "image_usable_all"] + extra_cols)
        for p in cand:
            k = (p["yaw"], p["pitch"])
            s = pose_summary[k]
            base = [s["region"], s["category"], s["yaw"], s["pitch"],
                    f"{s['ocs_mean']:.6e}", f"{s['ocs_roll0']:.6e}",
                    b_rank[k], info_rank[k], f"{s['neighbor_contrast_mean']:.6f}",
                    f"{s['roll_sensitivity']:.6f}", s["max_rank_shift"],
                    f"{s['pixel_contrast_mean']:.6f}", s["any_glint"], s["any_saturation"],
                    s["image_usable_all"]]
            w.writerow(base + [p.get(c, "") for c in extra_cols])


# high brightness：按 ocs_mean 前 20
high_b = sorted(poses, key=lambda p: -pose_summary[(p["yaw"], p["pitch"])]["ocs_mean"])[:20]
write_candidates(PKG / "tables" / "p2_high_brightness_candidates.csv", high_b)

# high information：按 neighbor_contrast_mean 前 20（信息 proxy）
high_i = sorted(poses, key=lambda p: -(pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"]
                                       if np.isfinite(pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"]) else -1))[:20]
write_candidates(PKG / "tables" / "p2_high_information_candidates.csv", high_i)

# low information regions：neighbor_contrast_mean 低 + roll_sensitivity 低（后 20）
low_i = sorted(poses, key=lambda p: (pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"]
                                     if np.isfinite(pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"]) else 1e9))[:20]
write_candidates(PKG / "tables" / "p2_low_information_regions.csv", low_i)

# ============================================================
# P3 refinement candidates（受控规模：每区域取效用/敏感最突出的 pose）
# ============================================================
# 规则：每区域取 (a) 最亮 pose (b) 信息 proxy 最高 pose (c) roll 最敏感 pose，去重
p3 = []
p3_keys = set()
for rg in REGIONS:
    ps = region_poses[rg]
    picks = [
        ("brightest", max(ps, key=lambda p: pose_summary[(p["yaw"], p["pitch"])]["ocs_mean"])),
        ("high_info", max(ps, key=lambda p: (pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"]
                                             if np.isfinite(pose_summary[(p["yaw"], p["pitch"])]["neighbor_contrast_mean"]) else -1))),
        ("roll_sensitive", max(ps, key=lambda p: (pose_summary[(p["yaw"], p["pitch"])]["roll_sensitivity"]
                                                  if np.isfinite(pose_summary[(p["yaw"], p["pitch"])]["roll_sensitivity"]) else -1))),
    ]
    for reason, p in picks:
        k = (p["yaw"], p["pitch"])
        if k in p3_keys:
            # 合并原因
            for row in p3:
                if (row["yaw"], row["pitch"]) == k:
                    row["p3_reason"] = row["p3_reason"] + ";" + reason
            continue
        p3_keys.add(k)
        pp = dict(p)
        pp["p3_reason"] = reason
        p3.append(pp)

write_candidates(PKG / "tables" / "p2_p3_refinement_candidates.csv", p3, extra_cols=["p3_reason"])

print("[OK] manifests + metric tables + region summary + candidates written")
print(f"poses={len(poses)}  units(incl roll0)={len(per_unit)}  nonzero units={sum(1 for k in per_unit if k[2]!=0)}")
print(f"regions={REGIONS}")
print(f"P3 refinement candidates={len(p3)}")
for r in region_rows:
    print(f"  {r['region']}: utility={r['region_utility_score']:.3f} "
          f"mean_ocs={r['mean_ocs']:.3e} mean_nc={r['mean_neighbor_contrast']:.3f} "
          f"mean_rs={r['mean_roll_sensitivity']:.3f} risk={r['risk_frac']:.2f}")

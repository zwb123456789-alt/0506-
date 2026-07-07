# -*- coding: utf-8 -*-
"""
b_c_metrics.py —— R135 子任务 B/C：P3 render/postprocess manifest + 局部加密稳定性指标

读 P3 预注册矩阵 + 21 号包各 roll 后处理产物 + 01_fullrun baseline(整数点 roll=0)，
计算每个 (yaw,pitch,roll) 单位的三轴指标，汇总到区域级，并计算 P3 特有的稳定性指标。

坐标：以 deci-degree（度×10）整数为主键，2.5 度 = 25 deci-degree。
读取来源：
  - roll=0 且整数点(yaw%50==0 且 pitch%50==0)：读 01_fullrun。
  - 其余（半度点 roll=0 + 全部非零 roll）：读 21 号包。

产出：
  render/p3_render_manifest.csv
  postprocess/p3_postprocess_manifest.csv
  tables/p3_local_refinement_metrics.csv
  tables/p3_region_summary.csv
  tables/p3_stability_assessment.csv
  tables/p3_high_brightness_refined_candidates.csv
  tables/p3_high_information_refined_candidates.csv
  tables/p3_low_information_connectivity.csv
  tables/p3_p4_planning_candidates.csv
  metrics/p3_metric_definitions_used.md

指标（R135 §5 要求，全部计算）：
  ocs_total / brightness_rank / neighbor_contrast_ypr / roll_sensitivity_score /
  rank_shift / glint_flag / saturation_flag / image_usable /
  local_peak_migration / local_information_stability / low_info_connectivity /
  p4_planning_utility_score

roll=0 整数点读 01_fullrun，其余读 21 号包。量纲一致。不训练、不改旧目录。
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
PKG = V04 / "v0.4_results" / "21_three_axis_p3_local_refinement"
FR_POST = V04 / "v0.4_results" / "01_fullrun" / "postprocess"
FR_SHADOW = V04 / "v0.4_results" / "01_fullrun" / "shadow_passes"
RENDER_BASE = PKG / "render" / "shadow_passes" / "phase63"
POST_BASE = PKG / "postprocess" / "phase63"
MATRIX = PKG / "tables" / "p3_local_refinement_pre_registered_matrix.csv"

ROLLS = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
NONZERO_ROLLS = [-60, -45, -30, -15, 15, 30, 45, 60]
STEP_DECI = 25   # 2.5 度邻域步长

# glint/saturation 判据：与 P1/P2 同口径
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


# ---- 读预注册矩阵：唯一 pose（以 deci-degree 为键）与其区域/label ----
matrix_rows = list(csv.DictReader(open(MATRIX, encoding="utf-8")))
poses, seen = [], set()
# label 映射：(yaw_deci, pitch_deci, roll) -> row（用于取 label / render_needed / grid_type）
row_by_unit = {}
for r in matrix_rows:
    yd, pd, roll = int(r["yaw_deci"]), int(r["pitch_deci"]), int(r["roll"])
    row_by_unit[(yd, pd, roll)] = r
    key = (yd, pd)
    if key not in seen:
        seen.add(key)
        poses.append({"yaw_deci": yd, "pitch_deci": pd, "region": r["region"],
                      "all_regions": r["all_regions"], "category": r["category"],
                      "priority": r["priority"], "grid_type": r["grid_type"],
                      "record_id": r["record_id"], "yaw_deg": float(r["yaw_deg"]),
                      "pitch_deg": float(r["pitch_deg"])})
POSE_KEYS = set((p["yaw_deci"], p["pitch_deci"]) for p in poses)
REGIONS = []
for p in poses:
    if p["region"] not in REGIONS:
        REGIONS.append(p["region"])


def is_integer_grid(yd, pd):
    return (yd % 50 == 0) and (pd % 50 == 0)


def fullrun_base(yd, pd):
    y = yd // 10
    p = pd // 10
    return f"yaw{y:03d}_pitch{p:+04d}_roll+000"


def load_unit(yd, pd, roll):
    """一个 (yaw_deci,pitch_deci,roll) 单位的合并指标。
    roll=0 整数点读 fullrun，其余读 21 号包。"""
    row = row_by_unit[(yd, pd, roll)]
    label = row["label"]
    if roll == 0 and is_integer_grid(yd, pd):
        base = fullrun_base(yd, pd)
        ocs_p = FR_POST / f"{base}_ocs.json"
        lin_p = FR_POST / f"{base}_linear.exr"
        cam_p = FR_SHADOW / f"{base}_camera.exr"
        source = "01_fullrun"
    else:
        rt = f"roll{roll:+04d}"
        ocs_p = POST_BASE / rt / f"{label}_ocs.json"
        lin_p = POST_BASE / rt / f"{label}_linear.exr"
        cam_p = RENDER_BASE / rt / f"{label}_camera.exr"
        source = "21_pack"
    d = json.load(open(ocs_p, encoding="utf-8")) if ocs_p.is_file() else {}
    im = image_metrics(lin_p)
    return dict(label=label, source=source, ocs_json=str(ocs_p), linear_exr=str(lin_p),
                camera_exr=str(cam_p),
                ocs_total=float(d.get("ocs_total", float("nan"))),
                n_pixels_camera_visible=int(d.get("n_pixels_camera_visible", 0)),
                n_pixels_contributing=int(d.get("n_pixels_contributing", 0)),
                ocs_ok=ocs_p.is_file(), **im)


# ---- 逐 pose 逐 roll 计算 ----
print(f"加载 {len(poses)*len(ROLLS)} 个 pose-roll 单位指标（含整数点 roll=0 baseline）...")
per_unit = {}
for p in poses:
    for roll in ROLLS:
        per_unit[(p["yaw_deci"], p["pitch_deci"], roll)] = load_unit(
            p["yaw_deci"], p["pitch_deci"], roll)

# ---- brightness rank：每个 roll 下 N pose 按 ocs_total 排名 ----
rank_by_roll = {}
for roll in ROLLS:
    vals = [((p["yaw_deci"], p["pitch_deci"]),
             per_unit[(p["yaw_deci"], p["pitch_deci"], roll)]["ocs_total"]) for p in poses]
    order = sorted(vals, key=lambda x: -x[1] if np.isfinite(x[1]) else 1e18)
    rank_by_roll[roll] = {k: i + 1 for i, (k, _) in enumerate(order)}


def ocs_at(yd, pd, roll):
    u = per_unit.get((yd, pd, roll))
    return u["ocs_total"] if u else float("nan")


def neighbor_contrast_ypr(yd, pd, roll):
    """三轴 (yaw,pitch,roll) 邻域内 OCS 的相对散布 (max-min)/mean。
    邻域 = 网格上相邻的 yaw±2.5 / pitch±2.5 / roll 相邻档（仅取存在于 P3 网格内的点）。"""
    vals = []
    ri = ROLLS.index(roll)
    roll_neighbors = [roll]
    if ri > 0:
        roll_neighbors.append(ROLLS[ri - 1])
    if ri < len(ROLLS) - 1:
        roll_neighbors.append(ROLLS[ri + 1])
    for dy in (-STEP_DECI, 0, STEP_DECI):
        for dp in (-STEP_DECI, 0, STEP_DECI):
            ny = (yd + dy) % 3600
            npi = pd + dp
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


def roll_sensitivity(yd, pd):
    """固定 (yaw,pitch)，OCS 随 9 roll 的相对散布 (max-min)/mean。"""
    vals = np.array([ocs_at(yd, pd, r) for r in ROLLS], float)
    m = np.nanmean(vals)
    if m <= 0:
        return float("nan")
    return float((np.nanmax(vals) - np.nanmin(vals)) / m)


# ============================================================
# render manifest（新渲染单位：render_needed=YES）
# ============================================================
with open(PKG / "render" / "p3_render_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region", "category", "priority", "yaw_deg", "pitch_deg", "roll",
                "grid_type", "label", "camera_exr_exists", "sun_exr_exists",
                "source", "source_p2_candidate"])
    for r in matrix_rows:
        if r["render_needed"] != "YES":
            continue
        roll = int(r["roll"])
        rt = f"roll{roll:+04d}"
        label = r["label"]
        cam = RENDER_BASE / rt / f"{label}_camera.exr"
        sun = RENDER_BASE / rt / f"{label}_sun.exr"
        w.writerow([r["region"], r["category"], r["priority"], r["yaw_deg"], r["pitch_deg"],
                    roll, r["grid_type"], label, cam.is_file(), sun.is_file(),
                    "21_pack", r["source_p2_candidate"]])

# ============================================================
# postprocess manifest（新渲染单位）
# ============================================================
with open(PKG / "postprocess" / "p3_postprocess_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region", "category", "yaw_deg", "pitch_deg", "roll", "grid_type", "label",
                "ocs_json_exists", "linear_exr_exists", "ocs_total", "image_usable", "status"])
    for r in matrix_rows:
        if r["render_needed"] != "YES":
            continue
        yd, pd, roll = int(r["yaw_deci"]), int(r["pitch_deci"]), int(r["roll"])
        u = per_unit[(yd, pd, roll)]
        status = "COMPLETE" if (u["ocs_ok"] and u["image_usable"]) else "CHECK"
        w.writerow([r["region"], r["category"], r["yaw_deg"], r["pitch_deg"], roll,
                    r["grid_type"], u["label"], u["ocs_ok"], os.path.isfile(u["linear_exr"]),
                    f"{u['ocs_total']:.6e}", u["image_usable"], status])

# ============================================================
# p3_local_refinement_metrics.csv（全 pose-roll 行）
# ============================================================
with open(PKG / "tables" / "p3_local_refinement_metrics.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region", "category", "priority", "yaw_deg", "pitch_deg", "roll", "grid_type",
                "source", "ocs_total", "brightness_rank", "rank_shift_vs_roll0",
                "pixel_local_contrast", "neighbor_contrast_ypr", "roll_sensitivity_score",
                "n_pixels_camera_visible", "n_pixels_contributing", "mean_lit",
                "image_usable", "glint_flag", "saturation_flag"])
    for p in poses:
        yd, pd = p["yaw_deci"], p["pitch_deci"]
        rank0 = rank_by_roll[0][(yd, pd)]
        rs = roll_sensitivity(yd, pd)
        for roll in ROLLS:
            u = per_unit[(yd, pd, roll)]
            rank = rank_by_roll[roll][(yd, pd)]
            nc = neighbor_contrast_ypr(yd, pd, roll)
            w.writerow([p["region"], p["category"], p["priority"],
                        f"{p['yaw_deg']:.1f}", f"{p['pitch_deg']:+.1f}", roll, p["grid_type"],
                        u["source"], f"{u['ocs_total']:.6e}", rank, rank - rank0,
                        f"{u['pixel_local_contrast']:.6f}", f"{nc:.6f}", f"{rs:.6f}",
                        u["n_pixels_camera_visible"], u["n_pixels_contributing"],
                        f"{u['mean_lit']:.6e}", u["image_usable"], u["glint_flag"], u["saturation_flag"]])

# ============================================================
# 每 pose 汇总
# ============================================================
pose_summary = {}
for p in poses:
    yd, pd = p["yaw_deci"], p["pitch_deci"]
    ocs_all = np.array([ocs_at(yd, pd, r) for r in ROLLS], float)
    ocs_mean = float(np.nanmean(ocs_all))
    ocs_roll0 = ocs_at(yd, pd, 0)
    rs = roll_sensitivity(yd, pd)
    ranks = [rank_by_roll[r][(yd, pd)] for r in ROLLS]
    max_rank_shift = max(abs(x - rank_by_roll[0][(yd, pd)]) for x in ranks)
    plc_all = np.array([per_unit[(yd, pd, r)]["pixel_local_contrast"] for r in ROLLS], float)
    plc_mean = float(np.nanmean(plc_all))
    nc_all = np.array([neighbor_contrast_ypr(yd, pd, r) for r in ROLLS], float)
    nc_mean = float(np.nanmean(nc_all))
    any_glint = int(any(per_unit[(yd, pd, r)]["glint_flag"] for r in ROLLS))
    any_sat = int(any(per_unit[(yd, pd, r)]["saturation_flag"] for r in ROLLS))
    usable_all = int(all(per_unit[(yd, pd, r)]["image_usable"] for r in ROLLS))
    pose_summary[(yd, pd)] = dict(
        region=p["region"], category=p["category"], priority=p["priority"],
        yaw_deci=yd, pitch_deci=pd, yaw_deg=p["yaw_deg"], pitch_deg=p["pitch_deg"],
        grid_type=p["grid_type"], ocs_mean=ocs_mean, ocs_roll0=ocs_roll0,
        roll_sensitivity=rs, max_rank_shift=max_rank_shift, pixel_contrast_mean=plc_mean,
        neighbor_contrast_mean=nc_mean, any_glint=any_glint, any_saturation=any_sat,
        image_usable_all=usable_all)

# 全局亮度/信息排名（按 pose 均值）
b_order = sorted(poses, key=lambda p: -pose_summary[(p["yaw_deci"], p["pitch_deci"])]["ocs_mean"])
b_rank = {(p["yaw_deci"], p["pitch_deci"]): i + 1 for i, p in enumerate(b_order)}
info_order = sorted(poses, key=lambda p: -(pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"]
                                           if np.isfinite(pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"])
                                           else -1))
info_rank = {(p["yaw_deci"], p["pitch_deci"]): i + 1 for i, p in enumerate(info_order)}


# ============================================================
# P3 特有稳定性指标（区域级）
# ============================================================
def region_poses_list(rg):
    return [p for p in poses if p["region"] == rg]


def local_peak_migration(rg):
    """区域内最亮 pose 相对 P2 参考峰的迁移（deci-degree 欧氏距离 + 是否仍为最亮）。
    这里以区域内 ocs_mean 最亮 pose 与该区域整数网格中心最亮点的偏移衡量局部峰迁移。"""
    ps = region_poses_list(rg)
    if not ps:
        return float("nan"), None, None
    # 区域内最亮 pose
    top = max(ps, key=lambda p: pose_summary[(p["yaw_deci"], p["pitch_deci"])]["ocs_mean"])
    # 参考：区域内整数点(5度)中最亮的那个（近似 P2 峰）
    ints = [p for p in ps if is_integer_grid(p["yaw_deci"], p["pitch_deci"])]
    if not ints:
        return float("nan"), (top["yaw_deg"], top["pitch_deg"]), None
    ref = max(ints, key=lambda p: pose_summary[(p["yaw_deci"], p["pitch_deci"])]["ocs_mean"])
    dy = (top["yaw_deci"] - ref["yaw_deci"]) / 10.0
    dp = (top["pitch_deci"] - ref["pitch_deci"]) / 10.0
    dist = float(np.hypot(dy, dp))
    return dist, (top["yaw_deg"], top["pitch_deg"]), (ref["yaw_deg"], ref["pitch_deg"])


def local_information_stability(rg):
    """区域内 neighbor_contrast_ypr(pose 均值) 的稳定性：1 - CV(变异系数)，越接近 1 越稳定。"""
    ps = region_poses_list(rg)
    vals = np.array([pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"]
                     for p in ps], float)
    vals = vals[np.isfinite(vals)]
    if len(vals) < 2 or vals.mean() <= 0:
        return float("nan")
    cv = vals.std() / vals.mean()
    return float(max(0.0, 1.0 - cv))


def low_info_connectivity(rg):
    """低信息连通性：区域内 neighbor_contrast_ypr 低于全局中位数的 pose 比例（越高越连通/成片）。"""
    ps = region_poses_list(rg)
    global_med = np.nanmedian([pose_summary[k]["neighbor_contrast_mean"] for k in pose_summary])
    lows = [1.0 for p in ps
            if np.isfinite(pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"])
            and pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"] < global_med]
    return float(len(lows) / len(ps)) if ps else float("nan")


# ============================================================
# region_utility_score & p3_region_summary.csv
# ============================================================
all_ocs = [pose_summary[(p["yaw_deci"], p["pitch_deci"])]["ocs_mean"] for p in poses]
all_nc = [pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"] for p in poses]
all_rs = [pose_summary[(p["yaw_deci"], p["pitch_deci"])]["roll_sensitivity"] for p in poses]
ocs_lo, ocs_hi = np.nanmin(all_ocs), np.nanmax(all_ocs)
nc_lo, nc_hi = np.nanmin(all_nc), np.nanmax(all_nc)
rs_lo, rs_hi = np.nanmin(all_rs), np.nanmax(all_rs)


def nrm(v, lo, hi):
    if not np.isfinite(v) or hi - lo < 1e-12:
        return 0.0
    return float(max(0.0, min(1.0, (v - lo) / (hi - lo))))


region_rows = []
for rg in REGIONS:
    ps = region_poses_list(rg)
    mean_ocs = float(np.nanmean([pose_summary[(p["yaw_deci"], p["pitch_deci"])]["ocs_mean"] for p in ps]))
    mean_nc = float(np.nanmean([pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"] for p in ps]))
    mean_rs = float(np.nanmean([pose_summary[(p["yaw_deci"], p["pitch_deci"])]["roll_sensitivity"] for p in ps]))
    risk_frac = float(np.mean([1.0 if (pose_summary[(p["yaw_deci"], p["pitch_deci"])]["any_glint"] or
                                       pose_summary[(p["yaw_deci"], p["pitch_deci"])]["any_saturation"]) else 0.0
                               for p in ps]))
    usable_frac = float(np.mean([pose_summary[(p["yaw_deci"], p["pitch_deci"])]["image_usable_all"] for p in ps]))
    ni = nrm(mean_nc, nc_lo, nc_hi)
    nr = nrm(mean_rs, rs_lo, rs_hi)
    nb = nrm(mean_ocs, ocs_lo, ocs_hi)
    utility = 0.4 * ni + 0.3 * nr + 0.3 * nb - 0.2 * risk_frac
    region_rows.append(dict(
        region=rg, category=ps[0]["category"], priority=ps[0]["priority"], n_poses=len(ps),
        mean_ocs=mean_ocs, mean_neighbor_contrast=mean_nc, mean_roll_sensitivity=mean_rs,
        risk_frac=risk_frac, usable_frac=usable_frac,
        norm_info=ni, norm_roll_sens=nr, norm_brightness=nb,
        region_utility_score=utility))

with open(PKG / "tables" / "p3_region_summary.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(region_rows[0].keys()))
    w.writeheader()
    for r in region_rows:
        rr = {k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in r.items()}
        w.writerow(rr)

# ============================================================
# p3_stability_assessment.csv（区域级 P3 特有稳定性）
# ============================================================
with open(PKG / "tables" / "p3_stability_assessment.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region", "priority", "n_poses",
                "brightest_pose_yaw_pitch", "peak_ref_yaw_pitch", "local_peak_migration_deg",
                "local_information_stability", "low_info_connectivity",
                "mean_roll_sensitivity", "region_utility_score", "assessment"])
    reg_util = {r["region"]: r["region_utility_score"] for r in region_rows}
    reg_rs = {r["region"]: r["mean_roll_sensitivity"] for r in region_rows}
    for rg in REGIONS:
        ps = region_poses_list(rg)
        mig, top, ref = local_peak_migration(rg)
        lis = local_information_stability(rg)
        lic = low_info_connectivity(rg)
        prio = ps[0]["priority"]
        # 简短评估文本
        if rg.startswith("R1"):
            asmt = (f"roll-sensitive peak {'稳定' if reg_rs[rg] > 1.5 else '偏弱'}; "
                    f"最亮点迁移 {mig:.1f}deg")
        elif rg.startswith("R4"):
            asmt = (f"最亮点{'基本未迁移' if mig <= 2.5 else f'迁移{mig:.1f}deg'}; "
                    f"info稳定性={lis:.2f}")
        elif rg.startswith("R3"):
            asmt = f"低信息连通性={lic:.2f}({'较连通' if lic >= 0.5 else '不连通'}); info稳定性={lis:.2f}"
        else:
            asmt = f"对照区; utility={reg_util[rg]:.3f}"
        w.writerow([rg, prio, len(ps),
                    f"{top[0]:.1f}/{top[1]:+.1f}" if top else "",
                    f"{ref[0]:.1f}/{ref[1]:+.1f}" if ref else "",
                    f"{mig:.2f}" if np.isfinite(mig) else "nan",
                    f"{lis:.4f}" if np.isfinite(lis) else "nan",
                    f"{lic:.4f}" if np.isfinite(lic) else "nan",
                    f"{reg_rs[rg]:.4f}", f"{reg_util[rg]:.4f}", asmt])

# ============================================================
# 候选清单
# ============================================================
def write_candidates(path, cand, extra_cols=None, extra_fn=None):
    extra_cols = extra_cols or []
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "category", "priority", "yaw_deg", "pitch_deg", "grid_type",
                    "ocs_mean", "ocs_roll0", "brightness_rank", "info_rank",
                    "neighbor_contrast_mean", "roll_sensitivity_score", "max_rank_shift",
                    "pixel_contrast_mean", "any_glint", "any_saturation",
                    "image_usable_all"] + extra_cols)
        for p in cand:
            k = (p["yaw_deci"], p["pitch_deci"])
            s = pose_summary[k]
            base = [s["region"], s["category"], s["priority"],
                    f"{s['yaw_deg']:.1f}", f"{s['pitch_deg']:+.1f}", s["grid_type"],
                    f"{s['ocs_mean']:.6e}", f"{s['ocs_roll0']:.6e}",
                    b_rank[k], info_rank[k], f"{s['neighbor_contrast_mean']:.6f}",
                    f"{s['roll_sensitivity']:.6f}", s["max_rank_shift"],
                    f"{s['pixel_contrast_mean']:.6f}", s["any_glint"], s["any_saturation"],
                    s["image_usable_all"]]
            extra = extra_fn(p) if extra_fn else [p.get(c, "") for c in extra_cols]
            w.writerow(base + extra)


# high brightness refined：按 ocs_mean 前 15
high_b = sorted(poses, key=lambda p: -pose_summary[(p["yaw_deci"], p["pitch_deci"])]["ocs_mean"])[:15]
write_candidates(PKG / "tables" / "p3_high_brightness_refined_candidates.csv", high_b)

# high information refined：按 neighbor_contrast_mean 前 15
high_i = sorted(poses, key=lambda p: -(pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"]
                                       if np.isfinite(pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"]) else -1))[:15]
write_candidates(PKG / "tables" / "p3_high_information_refined_candidates.csv", high_i)

# low information connectivity：neighbor_contrast_mean 低 + roll_sensitivity 低（后 15），偏 R3
low_i = sorted(poses, key=lambda p: (pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"]
                                     if np.isfinite(pose_summary[(p["yaw_deci"], p["pitch_deci"])]["neighbor_contrast_mean"]) else 1e9))[:15]
write_candidates(PKG / "tables" / "p3_low_information_connectivity.csv", low_i)

# ============================================================
# P4 planning candidates（P3 特有：综合 utility，供 P4 观测规划）
# ============================================================
# p4_planning_utility_score（pose 级）：
#   0.35*norm_info + 0.25*norm_rollsens + 0.25*norm_brightness - 0.15*risk
#   其中 risk = any_glint or any_saturation
def p4_utility(p):
    k = (p["yaw_deci"], p["pitch_deci"])
    s = pose_summary[k]
    ni = nrm(s["neighbor_contrast_mean"], nc_lo, nc_hi)
    nr = nrm(s["roll_sensitivity"], rs_lo, rs_hi)
    nb = nrm(s["ocs_mean"], ocs_lo, ocs_hi)
    risk = 1.0 if (s["any_glint"] or s["any_saturation"]) else 0.0
    return 0.35 * ni + 0.25 * nr + 0.25 * nb - 0.15 * risk


for p in poses:
    p["_p4"] = p4_utility(p)

# 每区域取 p4 效用最高 2 个 + 全局 top，去重，规模受控（<= 20）
p4_cand = []
p4_keys = set()
for rg in REGIONS:
    ps = sorted(region_poses_list(rg), key=lambda p: -p["_p4"])[:2]
    for p in ps:
        k = (p["yaw_deci"], p["pitch_deci"])
        if k not in p4_keys:
            p4_keys.add(k)
            p4_cand.append(p)
# 追加全局 top（补到 <=20）
for p in sorted(poses, key=lambda p: -p["_p4"]):
    if len(p4_cand) >= 16:
        break
    k = (p["yaw_deci"], p["pitch_deci"])
    if k not in p4_keys:
        p4_keys.add(k)
        p4_cand.append(p)
p4_cand = sorted(p4_cand, key=lambda p: -p["_p4"])


def p4_plan_role(p):
    s = pose_summary[(p["yaw_deci"], p["pitch_deci"])]
    if s["region"].startswith("R4"):
        role = "bright-info-tradeoff" if info_rank[(p["yaw_deci"], p["pitch_deci"])] <= 20 else "bright-primary"
    elif s["region"].startswith("R1"):
        role = "high-info-roll-sensitive"
    elif s["region"].startswith("R3"):
        role = "low-info-negative-control"
    else:
        role = "dark/neutral-control"
    return [f"{p['_p4']:.4f}", role]


write_candidates(PKG / "tables" / "p3_p4_planning_candidates.csv", p4_cand,
                 extra_cols=["p4_planning_utility_score", "p4_plan_role"], extra_fn=p4_plan_role)

print("[OK] manifests + metric tables + region summary + stability + candidates written")
print(f"poses={len(poses)}  units(incl roll0)={len(per_unit)}  "
      f"new-render units={sum(1 for k in per_unit if not (k[2]==0 and is_integer_grid(k[0],k[1])))}")
print(f"regions={REGIONS}")
print(f"P4 planning candidates={len(p4_cand)}")
for r in region_rows:
    print(f"  {r['region']}({r['priority']}): utility={r['region_utility_score']:.3f} "
          f"mean_ocs={r['mean_ocs']:.3e} mean_nc={r['mean_neighbor_contrast']:.3f} "
          f"mean_rs={r['mean_roll_sensitivity']:.3f} risk={r['risk_frac']:.2f}")

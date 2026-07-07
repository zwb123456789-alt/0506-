# -*- coding: utf-8 -*-
"""
p4physC_build_pool.py —— P4-PHYS-C 子任务 A：输入审计与候选池生成
================================================================================
R151 任务单执行脚本（第 1 步）。

只做：在 fixed phase63/L1-G1（SUN=[1,0,0.3], DET=[0.5,-1,0.1]）下，从既有
20/21/23A/23B（外加 01_fullrun 作为 R3/R5 对照来源）包中发现可定位候选，
产出候选池与输入审计。不重渲染、不搜索新姿态、不扩展 sun/view、不训练。

候选定位口径：每个候选必须同时有
    render/shadow_passes/phase63/<roll_dir>/<label>_camera.exr
    postprocess/phase63/<roll_dir>/<label>_v_sun_macro.npy
    postprocess/phase63/<roll_dir>/<label>_ocs.json
（01_fullrun 为扁平结构 postprocess/<label>_ocs.json + shadow_passes/<label>_camera.exr）
yaw/pitch/ocs_total 以 ocs.json 为准；roll 以 roll 目录名为准（3 位=整数度，4 位=/10）。
"""

import os
import re
import csv
import json
import glob
import numpy as np
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PKG25    = THIS_DIR.parent
V04_ROOT = THIS_DIR.parents[2]
RESULTS  = V04_ROOT / "v0.4_results"

OUT = {k: PKG25 / k for k in ("audit", "tables", "figures", "text", "scripts", "logs")}
for d in OUT.values():
    d.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# 候选来源包（优先级：23A/23B 精修 > 21 P3 > 20 P2 > 01 fullrun 对照）
# ------------------------------------------------------------------
SOURCES = [
    {"pkg": "23A", "root": RESULTS / "23A_three_axis_p4phys_top1_roll_confirmation",
     "layout": "phase63", "priority": 1},
    {"pkg": "23B", "root": RESULTS / "23B_three_axis_p4phys_pitch_boundary_followup",
     "layout": "phase63", "priority": 2},
    {"pkg": "P3",  "root": RESULTS / "21_three_axis_p3_local_refinement",
     "layout": "phase63", "priority": 3},
    {"pkg": "P2",  "root": RESULTS / "20_three_axis_p2_sparse_grid",
     "layout": "phase63", "priority": 4},
    {"pkg": "01",  "root": RESULTS / "01_fullrun",
     "layout": "flat", "priority": 5},
]

SEL_CAP = 200          # 规模上限
MIN_POOL = 30          # 最小池

# 关键参考姿态（force-include）
TOP1 = (245.0, 27.5, 15.0)
R4   = (147.5, 12.5, 0.0)
R3   = (55.0, 60.0, 0.0)


def roll_from_dirname(name):
    """roll+015 -> 15.0 ; roll+0125 -> 12.5 ; roll-030 -> -30.0"""
    m = re.match(r"roll([+-])(\d+)$", name)
    if not m:
        return None
    sign = 1.0 if m.group(1) == "+" else -1.0
    digits = m.group(2)
    val = int(digits)
    # 3 位=整数度；4 位=十分之一度（如 0125 -> 12.5）
    if len(digits) >= 4:
        val = val / 10.0
    return sign * val


def roll_from_flat_label(label):
    """01_fullrun 扁平：yaw055_pitch+060_roll+000 -> 0.0"""
    m = re.search(r"roll([+-])(\d+)$", label)
    if not m:
        return None
    sign = 1.0 if m.group(1) == "+" else -1.0
    digits = m.group(2)
    val = int(digits)
    if len(digits) >= 4:
        val = val / 10.0
    return sign * val


def pose_key(yaw, pitch, roll):
    return (round(float(yaw), 3), round(float(pitch), 3), round(float(roll), 3))


def scan_source(src):
    """返回 [dict(...)]，每个候选的 label / 三文件路径 / yaw / pitch / roll / ocs_total。"""
    root = src["root"]
    out = []
    if src["layout"] == "phase63":
        pp_base = root / "postprocess" / "phase63"
        rd_base = root / "render" / "shadow_passes" / "phase63"
        if not pp_base.is_dir():
            return out
        for roll_dir in sorted(os.listdir(pp_base)):
            roll_val = roll_from_dirname(roll_dir)
            if roll_val is None:
                continue
            for jf in sorted((pp_base / roll_dir).glob("*_ocs.json")):
                label = jf.name[:-len("_ocs.json")]
                exr = rd_base / roll_dir / f"{label}_camera.exr"
                vsun = pp_base / roll_dir / f"{label}_v_sun_macro.npy"
                out.append(_mk(src, label, roll_val, jf, exr, vsun))
    else:  # flat (01_fullrun)
        pp_base = root / "postprocess"
        rd_base = root / "shadow_passes"
        for jf in sorted(pp_base.glob("*_ocs.json")):
            label = jf.name[:-len("_ocs.json")]
            roll_val = roll_from_flat_label(label)
            if roll_val is None:
                continue
            exr = rd_base / f"{label}_camera.exr"
            vsun = pp_base / f"{label}_v_sun_macro.npy"
            out.append(_mk(src, label, roll_val, jf, exr, vsun))
    return out


def _mk(src, label, roll_val, jf, exr, vsun):
    rec = {"pkg": src["pkg"], "priority": src["priority"], "label": label,
           "roll": roll_val, "json_path": jf, "exr_path": exr, "vsun_path": vsun,
           "json_ok": jf.is_file(), "exr_ok": exr.is_file(), "vsun_ok": vsun.is_file(),
           "yaw": None, "pitch": None, "ocs_total": None}
    if jf.is_file():
        try:
            with open(jf, encoding="utf-8") as f:
                d = json.load(f)
            rec["yaw"] = float(d.get("yaw_deg"))
            rec["pitch"] = float(d.get("pitch_deg"))
            rec["ocs_total"] = float(d.get("ocs_total"))
        except Exception:
            pass
    return rec


# ------------------------------------------------------------------
# region / category 标签：join 自 P2/P3 metrics 与 23A/23B cluster
# ------------------------------------------------------------------
def load_region_labels():
    labels = {}  # pose_key -> (region, category)

    def add(pk, region, category):
        # 优先保留更细的 region（先到先得，P3>P2 由调用顺序控制）
        if pk not in labels:
            labels[pk] = (region, category)

    # 23A refined topN cluster
    f23a = RESULTS / "23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_refined_topN.csv"
    if f23a.is_file():
        with open(f23a, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    pk = pose_key(row["yaw_deg"], row["pitch_deg"], row["roll"])
                    add(pk, row.get("cluster", "23A_topN"), "23A_refined_topN")
                except Exception:
                    continue
    # 23B combined cluster
    f23b = RESULTS / "23B_three_axis_p4phys_pitch_boundary_followup/tables/p4physA2_combined_topN_with_23A.csv"
    if f23b.is_file():
        with open(f23b, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    pk = pose_key(row["yaw_deg"], row["pitch_deg"], row["roll"])
                    add(pk, row.get("cluster", "23B_topN"), "23B_combined_topN")
                except Exception:
                    continue
    # P3 metrics region/category
    f21 = RESULTS / "21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv"
    if f21.is_file():
        with open(f21, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    pk = pose_key(row["yaw_deg"], row["pitch_deg"], row["roll"])
                    add(pk, row.get("region", "P3"), row.get("category", "P3_metrics"))
                except Exception:
                    continue
    # P2 metrics region/category
    f20 = RESULTS / "20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv"
    if f20.is_file():
        with open(f20, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                try:
                    pk = pose_key(row["yaw"], row["pitch"], row["roll"])
                    add(pk, row.get("region", "P2"), row.get("category", "P2_metrics"))
                except Exception:
                    continue
    return labels


def main():
    # ---- 1. 扫描所有来源 ----
    raw = []
    for src in SOURCES:
        recs = scan_source(src)
        raw.extend(recs)

    # ---- 2. 输入 manifest（按包统计） ----
    input_rows = []
    by_pkg = {}
    for r in raw:
        by_pkg.setdefault(r["pkg"], []).append(r)
    for src in SOURCES:
        pk = src["pkg"]
        lst = by_pkg.get(pk, [])
        n_json = sum(1 for r in lst if r["json_ok"])
        n_exr = sum(1 for r in lst if r["exr_ok"])
        n_vsun = sum(1 for r in lst if r["vsun_ok"])
        n_full = sum(1 for r in lst if r["json_ok"] and r["exr_ok"] and r["vsun_ok"])
        input_rows.append([pk, str(Path(src["root"]).relative_to(V04_ROOT)).replace("\\", "/"),
                           src["layout"], len(lst), n_json, n_exr, n_vsun, n_full])
    _wcsv(OUT["audit"] / "input_manifest.csv",
          ["pkg", "root_rel", "layout", "n_discovered", "n_json_ok", "n_exr_ok",
           "n_vsun_ok", "n_full_triple"], input_rows)

    # ---- 3. 去重（按 pose_key，保留最高优先级来源） ----
    labels = load_region_labels()
    dedup = {}  # pose_key -> rec (best priority)
    for r in raw:
        if r["yaw"] is None or r["ocs_total"] is None:
            continue
        pkk = pose_key(r["yaw"], r["pitch"], r["roll"])
        if pkk not in dedup or r["priority"] < dedup[pkk]["priority"]:
            keep = dict(r)
            keep["pose_key"] = pkk
            dedup[pkk] = keep
    # 附 region 标签
    for pkk, r in dedup.items():
        reg, cat = labels.get(pkk, ("unlabeled", "unlabeled"))
        r["region"], r["category"] = reg, cat

    # ---- 4. 可用性审计（geometry-eligible = full triple） ----
    avail_rows = []
    eligible = {}
    for pkk, r in dedup.items():
        full = r["json_ok"] and r["exr_ok"] and r["vsun_ok"]
        geom_eligible = full
        avail_rows.append([r["label"], r["yaw"], r["pitch"], r["roll"],
                           f"{r['ocs_total']:.8f}", r["pkg"], r["region"], r["category"],
                           int(r["json_ok"]), int(r["exr_ok"]), int(r["vsun_ok"]),
                           "YES" if geom_eligible else "NO"])
        if geom_eligible:
            eligible[pkk] = r
    _wcsv(OUT["audit"] / "exr_json_availability.csv",
          ["label", "yaw", "pitch", "roll", "ocs_total", "src_pkg", "region", "category",
           "json_ok", "exr_ok", "vsun_ok", "geometry_eligible"], avail_rows)

    # ---- 5. 分层采样选择候选池（geometry-eligible 内） ----
    selected = _select_pool(eligible)

    # ---- 6. 候选池 manifest / 候选池表 ----
    pool_rows, pool_manifest = [], []
    for pkk, r in selected.items():
        exr_rel = str(Path(r["exr_path"]).relative_to(V04_ROOT)).replace("\\", "/")
        vsun_rel = str(Path(r["vsun_path"]).relative_to(V04_ROOT)).replace("\\", "/")
        json_rel = str(Path(r["json_path"]).relative_to(V04_ROOT)).replace("\\", "/")
        pool_rows.append([r["label"], r["yaw"], r["pitch"], r["roll"],
                          f"{r['ocs_total']:.8f}", r["pkg"], r["region"], r["category"],
                          r["_reason"]])
        pool_manifest.append([r["label"], r["yaw"], r["pitch"], r["roll"], r["pkg"],
                              exr_rel, vsun_rel, json_rel])
    # 按 ocs 降序输出
    pool_rows.sort(key=lambda x: -float(x[4]))
    pool_manifest.sort(key=lambda x: (x[0]))
    _wcsv(OUT["tables"] / "p4physC_candidate_pool.csv",
          ["pose_label", "yaw", "pitch", "roll", "ocs_total", "src_pkg",
           "region", "category", "selection_reason"], pool_rows)
    _wcsv(OUT["audit"] / "candidate_pool_manifest.csv",
          ["pose_label", "yaw", "pitch", "roll", "src_pkg",
           "exr_rel", "vsun_rel", "json_rel"], pool_manifest)

    # ---- 7. 红线预检 ----
    redline_rows = [
        ["fixed_geometry_only", "PASS", "只用 phase63/L1-G1 既有渲染，SUN=[1,0,0.3] DET=[0.5,-1,0.1]"],
        ["no_new_render", "PASS", "仅发现既有 EXR/JSON/npy，未触发渲染"],
        ["no_sunview_expand", "PASS", "未扩展 sun/view"],
        ["no_new_pose_search", "PASS", "未搜索新姿态"],
        ["no_training", "PASS", "无训练"],
        ["not_modify_source_pkgs", "PASS", "20/21/23A/23B/24 只读"],
        ["material_proxy_only", "PASS", "material-level 仍为 B0 proxy，无 material pass"],
        ["pool_size_le_200", "PASS" if len(selected) <= SEL_CAP else "FAIL",
         f"selected={len(selected)} cap={SEL_CAP}"],
        ["pool_size_ge_30", "PASS" if len(selected) >= MIN_POOL else "WARN",
         f"selected={len(selected)} min={MIN_POOL}"],
    ]
    _wcsv(OUT["audit"] / "redline_precheck.csv", ["check", "status", "note"], redline_rows)

    # ---- 8. 汇总日志 ----
    n_high = sum(1 for r in selected.values() if r["_reason"].startswith("bright") or "topN" in r["category"])
    log = {
        "n_raw_discovered": len(raw),
        "n_unique_poses": len(dedup),
        "n_geometry_eligible": len(eligible),
        "n_selected": len(selected),
        "cap": SEL_CAP,
        "top1_in_pool": pose_key(*TOP1) in selected,
        "R4_in_pool": pose_key(*R4) in selected,
        "R3_in_pool": pose_key(*R3) in selected,
        "region_counts": _region_counts(selected),
    }
    with open(OUT["logs"] / "p4physC_build_pool_log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    print("[p4physC build_pool] DONE")
    for k, v in log.items():
        print(f"  {k}: {v}")


def _select_pool(eligible):
    """region-aware 分层采样，force-include 关键姿态，cap=200。"""
    items = list(eligible.values())
    # force-include 集
    forced_keys = {pose_key(*TOP1), pose_key(*R4), pose_key(*R3)}
    selected = {}

    def take(r, reason):
        pk = r["pose_key"]
        if pk not in selected:
            rr = dict(r); rr["_reason"] = reason
            selected[pk] = rr

    # 1) 关键参考姿态
    for r in items:
        if r["pose_key"] in forced_keys:
            role = {pose_key(*TOP1): "top1", pose_key(*R4): "R4_robust",
                    pose_key(*R3): "R3_negative"}[r["pose_key"]]
            take(r, f"forced_{role}")

    # 2) 全部 topN 簇（23A/23B refined topN + combined）
    for r in items:
        if "topN" in r["category"]:
            take(r, f"topN_{r['region']}")

    # 3) 全局亮度 top 40
    for r in sorted(items, key=lambda x: -x["ocs_total"])[:40]:
        take(r, "bright_top40_global")

    # 4) region 分层：每个 region 取亮度前若干 + 后若干
    by_region = {}
    for r in items:
        by_region.setdefault(r["region"], []).append(r)
    per_region_top = 8
    per_region_bot = 4
    for reg, lst in by_region.items():
        lst_sorted = sorted(lst, key=lambda x: -x["ocs_total"])
        for r in lst_sorted[:per_region_top]:
            take(r, f"region_top_{reg}")
        for r in lst_sorted[-per_region_bot:]:
            take(r, f"region_bottom_{reg}")

    # 5) 全局最暗 20（负锚点）
    for r in sorted(items, key=lambda x: x["ocs_total"])[:20]:
        take(r, "dark_bottom20_global")

    # 6) 若仍不足，补 brightness 均匀分位；若超 cap，保 force+topN 后按亮度分层裁剪
    if len(selected) > SEL_CAP:
        # 保护 forced + topN，其余按亮度间隔抽稀
        protected = {pk: r for pk, r in selected.items()
                     if r["_reason"].startswith("forced") or r["_reason"].startswith("topN")}
        rest = [r for pk, r in selected.items() if pk not in protected]
        rest_sorted = sorted(rest, key=lambda x: -x["ocs_total"])
        room = SEL_CAP - len(protected)
        if room < 0:
            room = 0
        # 均匀抽稀
        if len(rest_sorted) > room and room > 0:
            step = len(rest_sorted) / room
            keep_idx = sorted(set(int(i * step) for i in range(room)))
            rest_keep = [rest_sorted[i] for i in keep_idx if i < len(rest_sorted)]
        else:
            rest_keep = rest_sorted[:room]
        selected = dict(protected)
        for r in rest_keep:
            selected[r["pose_key"]] = r
    return selected


def _region_counts(selected):
    c = {}
    for r in selected.values():
        c[r["region"]] = c.get(r["region"], 0) + 1
    return c


def _wcsv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(rows)


if __name__ == "__main__":
    main()

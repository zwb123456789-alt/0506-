#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
18 号三轴准备包 - 子任务C：三轴搜索种子提取（只读）

从路线一 C 已通过结果中构建 per-attitude 主表（fixed-roll, roll=0），
按 9 类规则提取三轴搜索种子，输出：
  seeds/three_axis_seed_candidates.csv
  seeds/attitude_master_fixedroll.csv   （中间主表，供复现）
  seeds/seed_selection_rules.md
  text/seed_set_summary.md

种子类别：bright / dark / high-info / low-info / image-hard /
          ocs-hard / disagreement / roll-sensitive / robust-easy

红线：只读；不改旧结果；brightness 与 information 显式分开；
      最亮 != 最优反演；不写成真实反演系统。
"""
import csv
import json
import math
import os

V04 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RES = os.path.join(V04, "v0.4_results")
OUT = os.path.join(RES, "18_three_axis_planning_preflight")


def pp(*parts):
    return os.path.join(RES, *parts)


def rid(yaw, pitch):
    return "yaw%03d_pitch%+04d" % (int(round(yaw)), int(round(pitch)))


# ---------- 1. brightness：读 phase63 (L1-G1) OCS total ----------
def load_brightness():
    d = pp("01_fullrun", "postprocess")
    bright = {}
    for fn in os.listdir(d):
        if not fn.endswith("_ocs.json"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            j = json.load(f)
        key = (float(j["yaw_deg"]), float(j["pitch_deg"]))
        bright[key] = {
            "ocs_total_phase63": j["ocs_total"],
            "n_pix_contrib": j.get("n_pixels_contributing", 0),
            "n_pix_visible": j.get("n_pixels_camera_visible", 0),
        }
    return bright


# ---------- 2. D4 gain（G1->G5 ocs err 与救回/变差） ----------
def load_d4_gain():
    p = pp("16_route1c_closure_d2d4_m5", "tables", "d4_geometry_gain_by_attitude.csv")
    g = {}
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key = (float(r["yaw_true"]), float(r["pitch_true"]))
            g[key] = {
                "ocs_g1_err": float(r["ocs_g1_err"]),
                "ocs_g5_err": float(r["ocs_g5_err"]),
                "gain_g1_to_g5": float(r["gain_g1_to_g5"]),
            }
    return g


# ---------- 3. hardcase 标签（clean, best；取 G5 优先，回退 G3/G1） ----------
def load_hardcase():
    p = pp("13_l1d3_confidence_pdb", "hardcases", "l1d3_hardcase_index.csv")
    # 每个 (geom, record_id) 一行；聚合到姿态：合并各几何标签
    byatt = {}
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["degrade_level"] != "clean":
                continue
            key = (float(r["yaw_true"]), float(r["pitch_true"]))
            e = byatt.setdefault(key, {"labels": set(), "geoms": set(),
                                       "pdb_margin": [], "pdb_spread": []})
            for lab in r["hardcase_labels"].split(";"):
                if lab:
                    e["labels"].add(lab)
            e["geoms"].add(r["geom"])
            try:
                e["pdb_margin"].append(float(r["pdb_margin"]))
                e["pdb_spread"].append(float(r["pdb_cand_yaw_spread"]))
            except (ValueError, KeyError):
                pass
    return byatt


# ---------- 4. neural_pdb joined：entropy / margin（G5 ocs_only best 优先） ----------
def load_joined():
    p = pp("13_l1d3_confidence_pdb", "consistency", "l1d3_neural_pdb_joined_per_attitude.csv")
    # 选 clean + ocs_only + best；几何优先 G5 > G3 > G1
    prio = {"G5": 3, "G3": 2, "G1": 1}
    best = {}
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["degrade_level"] != "clean" or r["mode"] != "ocs_only" or r["select"] != "best":
                continue
            key = (float(r["yaw_true"]), float(r["pitch_true"]))
            g = r["geom"]
            cur = best.get(key)
            if cur is None or prio[g] > prio[cur["geom"]]:
                best[key] = {
                    "geom": g,
                    "neural_entropy": float(r["neural_entropy"]),
                    "neural_margin": float(r["neural_margin"]),
                    "neural_yaw_err": float(r["neural_yaw_err"]),
                    "pdb_top1_yaw_err": float(r["pdb_top1_yaw_err"]),
                    "pdb_nearest_distance": float(r["pdb_nearest_distance"]),
                    "pdb_cand_yaw_spread": float(r["pdb_cand_yaw_spread"]),
                }
    return best


# ---------- 5. roll sensitivity：M-roll full-2664, ocs_only, |err(±30)-err(roll0)| ----------
def load_roll_sensitivity():
    """用 G1 ocs_only：比较 roll±15/±30 的 yaw_err 与 roll0（D4 ocs_g1_err 近似 roll0）。
    这里以 mroll 自身 ±15 vs ±30 的误差抬升作为 roll 敏感度代理。"""
    mroll_dir = pp("17_route1c_postclosure_enhancement_sweep", "mroll_full2664")
    out = {}
    def read_pred(fn):
        p = os.path.join(mroll_dir, fn)
        d = {}
        if not os.path.isfile(p):
            return d
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                d[r["record_id"]] = float(r["yaw_err"])
        return d
    # 用 G1 ocs_only
    r15p = read_pred("predictions_G1_ocs_only_roll+015.csv")
    r15m = read_pred("predictions_G1_ocs_only_roll-015.csv")
    r30p = read_pred("predictions_G1_ocs_only_roll+030.csv")
    r30m = read_pred("predictions_G1_ocs_only_roll-030.csv")
    keys = set(r15p) | set(r30p)
    for k in keys:
        errs15 = [v for v in (r15p.get(k), r15m.get(k)) if v is not None]
        errs30 = [v for v in (r30p.get(k), r30m.get(k)) if v is not None]
        if not errs15 or not errs30:
            continue
        mean15 = sum(errs15) / len(errs15)
        mean30 = sum(errs30) / len(errs30)
        # 解析 record_id -> yaw/pitch
        try:
            yy = float(k.split("yaw")[1].split("_")[0])
            pstr = k.split("pitch")[1]
            ppv = float(pstr)
        except (IndexError, ValueError):
            continue
        out[(yy, ppv)] = {
            "roll_err_mean15": mean15,
            "roll_err_mean30": mean30,
            "roll_sensitivity_30_minus_15": mean30 - mean15,
        }
    return out


def main():
    bright = load_brightness()
    d4 = load_d4_gain()
    hardcase = load_hardcase()
    joined = load_joined()
    rollsens = load_roll_sensitivity()

    # 主表：以 brightness 全 2664 姿态为骨架
    master = []
    for key in sorted(bright.keys(), key=lambda k: (k[0], k[1])):
        yaw, pitch = key
        row = {
            "record_id": rid(yaw, pitch),
            "yaw": yaw, "pitch": pitch,
            "ocs_total_phase63": bright[key]["ocs_total_phase63"],
            "n_pix_contrib": bright[key]["n_pix_contrib"],
        }
        row.update({k: "" for k in
                    ["ocs_g1_err", "ocs_g5_err", "gain_g1_to_g5",
                     "hardcase_labels", "neural_entropy", "neural_margin",
                     "pdb_nearest_distance", "pdb_cand_yaw_spread",
                     "roll_err_mean15", "roll_err_mean30", "roll_sensitivity_30_minus_15"]})
        if key in d4:
            row.update({k: d4[key][k] for k in ["ocs_g1_err", "ocs_g5_err", "gain_g1_to_g5"]})
        if key in hardcase:
            row["hardcase_labels"] = ";".join(sorted(hardcase[key]["labels"]))
        if key in joined:
            j = joined[key]
            row["neural_entropy"] = j["neural_entropy"]
            row["neural_margin"] = j["neural_margin"]
            row["pdb_nearest_distance"] = j["pdb_nearest_distance"]
            row["pdb_cand_yaw_spread"] = j["pdb_cand_yaw_spread"]
        if key in rollsens:
            row.update(rollsens[key])
        master.append(row)

    # 写主表
    mfields = ["record_id", "yaw", "pitch", "ocs_total_phase63", "n_pix_contrib",
               "ocs_g1_err", "ocs_g5_err", "gain_g1_to_g5", "hardcase_labels",
               "neural_entropy", "neural_margin", "pdb_nearest_distance",
               "pdb_cand_yaw_spread", "roll_err_mean15", "roll_err_mean30",
               "roll_sensitivity_30_minus_15"]
    with open(os.path.join(OUT, "seeds", "attitude_master_fixedroll.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=mfields)
        w.writeheader()
        w.writerows(master)

    # ---------- 种子提取 ----------
    def topn(rows, keyfn, n, reverse=True, filt=None):
        cand = [r for r in rows if (filt(r) if filt else True)]
        cand = [r for r in cand if keyfn(r) is not None]
        cand.sort(key=keyfn, reverse=reverse)
        return cand[:n]

    def numeric(v):
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    seeds = []
    N = 8  # 每类种子数量

    def add_seeds(rows, category, source_file, why, roll_range, risk_fn, metric_fn):
        for r in rows:
            seeds.append({
                "seed_id": f"{category}__{r['record_id']}",
                "record_id": r["record_id"],
                "yaw": r["yaw"], "pitch": r["pitch"],
                "category": category,
                "source_file": source_file,
                "key_metric": metric_fn(r),
                "why_roll_extend": why,
                "suggested_roll_range": roll_range,
                "risk_flag": risk_fn(r),
            })

    # 1. bright-seed：phase63 OCS total 最高
    add_seeds(topn(master, lambda r: numeric(r["ocs_total_phase63"]), N, reverse=True),
              "bright-seed", "01_fullrun/postprocess (phase63)",
              "最亮 fixed-roll 姿态；检验最亮点在 roll 扫描下是否迁移/是否 glint 风险",
              "{-60..+60 step15}",
              lambda r: "glint/saturation-check" ,
              lambda r: f"ocs_total={numeric(r['ocs_total_phase63']):.4g}")

    # 2. dark-seed：phase63 OCS total 最低（>0，排除完全不可见）
    dark = topn([r for r in master if numeric(r["ocs_total_phase63"]) and numeric(r["ocs_total_phase63"]) > 0],
                lambda r: numeric(r["ocs_total_phase63"]), N, reverse=False)
    add_seeds(dark, "dark-seed", "01_fullrun/postprocess (phase63)",
              "最暗但非零姿态；检验低信号在 roll 下是否仍不可用",
              "{-30..+30 step15}",
              lambda r: "low-signal",
              lambda r: f"ocs_total={numeric(r['ocs_total_phase63']):.4g}")

    # 3. high-info-seed：G1->G5 gain 最大（多几何救回强，可分）
    add_seeds(topn(master, lambda r: numeric(r["gain_g1_to_g5"]), N, reverse=True,
                   filt=lambda r: numeric(r["gain_g1_to_g5"]) is not None),
              "high-info-seed", "16_.../d4_geometry_gain_by_attitude.csv",
              "多几何 OCS 救回增益最大；高可分姿态，检验 roll 下可分性是否保持",
              "{-60..+60 step15}",
              lambda r: "none",
              lambda r: f"gain_g1_g5={numeric(r['gain_g1_to_g5']):.1f}deg")

    # 4. low-info-seed：ambiguous-flux 或 pdb_cand_yaw_spread 最大
    lowinfo = topn([r for r in master if r["hardcase_labels"] and "ambiguous-flux" in r["hardcase_labels"]],
                   lambda r: numeric(r["pdb_cand_yaw_spread"]) or 0, N, reverse=True)
    if len(lowinfo) < N:
        extra = topn([r for r in master if numeric(r["pdb_cand_yaw_spread"])],
                     lambda r: numeric(r["pdb_cand_yaw_spread"]), N, reverse=True)
        seen = {r["record_id"] for r in lowinfo}
        for e in extra:
            if e["record_id"] not in seen and len(lowinfo) < N:
                lowinfo.append(e)
    add_seeds(lowinfo, "low-info-seed", "13_.../hardcase_index + neural_pdb_joined",
              "ambiguous-flux / 候选 yaw 弥散大；低信息易混淆，检验 roll 是否加剧混淆",
              "{-30..+30 step15}",
              lambda r: "ambiguous",
              lambda r: f"cand_spread={numeric(r['pdb_cand_yaw_spread']) or 0:.1f}")

    # 5. ocs-hard-seed：ocs_g5_err 最大（多几何仍难）
    add_seeds(topn(master, lambda r: numeric(r["ocs_g5_err"]), N, reverse=True,
                   filt=lambda r: numeric(r["ocs_g5_err"]) is not None),
              "ocs-hard-seed", "16_.../d4_geometry_gain_by_attitude.csv",
              "OCS-only 即使 G5 仍高误差；OCS 难区，检验图像/roll 是否补救",
              "{-60..+60 step15}",
              lambda r: "ocs-hard",
              lambda r: f"ocs_g5_err={numeric(r['ocs_g5_err']):.1f}deg")

    # 6. image-hard-seed：hardcase 含 image-hard
    imghard = [r for r in master if r["hardcase_labels"] and "image-hard" in r["hardcase_labels"]]
    add_seeds(imghard[:N], "image-hard-seed", "13_.../hardcase_index.csv",
              "image_only 失败/欠覆盖；检验 roll 下图像通道是否更难",
              "{-30..+30 step15}",
              lambda r: "image-hard",
              lambda r: f"labels={r['hardcase_labels']}")

    # 7. disagreement-seed：hardcase 含 disagreement-hard，取 gain 显著者
    disag = [r for r in master if r["hardcase_labels"] and "disagreement-hard" in r["hardcase_labels"]]
    disag = topn(disag, lambda r: abs(numeric(r["gain_g1_to_g5"]) or 0), N, reverse=True)
    add_seeds(disag, "disagreement-seed", "13_.../hardcase_index.csv",
              "OCS 与 image 候选冲突；检验 roll 下通道冲突如何变化",
              "{-45..+45 step15}",
              lambda r: "channel-conflict",
              lambda r: f"labels={r['hardcase_labels']}")

    # 8. roll-sensitive-seed：M-roll ±30 误差抬升最大
    add_seeds(topn(master, lambda r: numeric(r["roll_sensitivity_30_minus_15"]), N, reverse=True,
                   filt=lambda r: numeric(r["roll_sensitivity_30_minus_15"]) is not None),
              "roll-sensitive-seed", "17_.../mroll_full2664 (G1 ocs_only)",
              "±30° roll 误差抬升最大；fixed-roll 结论最可能被 roll 推翻，优先扫描",
              "{-30..+30 step15 加密}",
              lambda r: "roll-sensitive",
              lambda r: f"d(err30-err15)={numeric(r['roll_sensitivity_30_minus_15']):.1f}deg")

    # 9. robust-easy-seed：hardcase 含 robust-easy，且 gain 稳定，作为正对照
    robust = [r for r in master if r["hardcase_labels"] and "robust-easy" in r["hardcase_labels"]]
    robust = topn(robust, lambda r: numeric(r["ocs_total_phase63"]) or 0, N, reverse=True)
    add_seeds(robust, "robust-easy-seed", "13_.../hardcase_index.csv",
              "多通道均稳定；正对照，检验 roll 稳健性基线",
              "{-60..+60 step15}",
              lambda r: "none",
              lambda r: f"ocs_total={numeric(r['ocs_total_phase63']) or 0:.4g}")

    # 写 seed 候选
    sfields = ["seed_id", "record_id", "yaw", "pitch", "category", "source_file",
               "key_metric", "why_roll_extend", "suggested_roll_range", "risk_flag"]
    with open(os.path.join(OUT, "seeds", "three_axis_seed_candidates.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sfields)
        w.writeheader()
        w.writerows(seeds)

    # 类别统计
    import collections
    cats = collections.Counter(s["category"] for s in seeds)
    print("[C] seed extraction done.")
    print("  master rows:", len(master))
    print("  seed total:", len(seeds))
    for c, n in sorted(cats.items()):
        print(f"    {c}: {n}")
    return cats, len(master), len(seeds)


if __name__ == "__main__":
    main()

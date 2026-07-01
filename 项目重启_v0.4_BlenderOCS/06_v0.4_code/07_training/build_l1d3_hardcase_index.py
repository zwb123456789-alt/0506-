#!/usr/bin/env python3
"""
build_l1d3_hardcase_index.py —— R118 子任务 E：Hard-case / P-INT-hard 候选索引

不启动 P-INT-hard 新训练，只用 D3 结果生成下一步可执行候选索引。

hard-case 定义（基于 consistency joined 表 + P-DB per-query）：
  1. OCS-hard      : G5 ocs_only neural yaw error 高，且 P-DB margin 低 / nearest distance 高。
  2. image-hard    : image_only / joint 出现高 error 或低 confidence。
  3. disagreement  : neural 与 P-DB 预测相差大（|neural_err - pdb_err| 大 或 一对一错）。
  4. ambiguous-flux: P-DB top-k 候选 yaw 分散但距离接近（cand_yaw_spread 大 & nearest_distance 小）。
  5. robust-easy   : neural 与 P-DB 都高置信且低 error（对照）。

阈值基于该层分布分位数（可审计、非直觉）。

输出：
  hardcases/l1d3_hardcase_index.csv
  hardcases/l1d3_hardcase_summary.md
  hardcases/l1d3_recommended_pinthard_design.md
"""

import csv

import numpy as np

import l1d3_common as C

CONS = C.OUT / "consistency" / "l1d3_neural_pdb_joined_per_attitude.csv"


def load_joined():
    rows = list(csv.DictReader(open(CONS, encoding="utf-8")))
    for r in rows:
        for k in ("neural_yaw_err", "neural_pitch_err", "neural_margin", "neural_entropy",
                  "pdb_top1_yaw_err", "pdb_nearest_distance", "pdb_margin", "pdb_cand_yaw_spread",
                  "yaw_true", "pitch_true"):
            r[k] = float(r[k])
    return rows


def classify(rows, deg, geom, select="best"):
    """对给定 (deg, geom, select) 的三模式做 hard-case 分类。返回 case 行列表。"""
    # 按 mode 索引 record_id -> row
    by_mode = {}
    for r in rows:
        if r["degrade_level"] == deg and r["geom"] == geom and r["select"] == select:
            by_mode.setdefault(r["mode"], {})[r["record_id"]] = r
    if "ocs_only" not in by_mode:
        return []

    ocs = by_mode["ocs_only"]
    rids = list(ocs.keys())

    # 分位阈值（基于 ocs_only 层分布）
    neu_err = np.array([ocs[k]["neural_yaw_err"] for k in rids])
    pdb_err = np.array([ocs[k]["pdb_top1_yaw_err"] for k in rids])
    pdb_margin = np.array([ocs[k]["pdb_margin"] for k in rids])
    pdb_dist = np.array([ocs[k]["pdb_nearest_distance"] for k in rids])
    pdb_spread = np.array([ocs[k]["pdb_cand_yaw_spread"] for k in rids])

    hi_neu = np.quantile(neu_err, 0.75)
    lo_margin = np.quantile(pdb_margin, 0.25)
    hi_dist = np.quantile(pdb_dist, 0.75)
    hi_spread = np.quantile(pdb_spread, 0.75)
    lo_neu = np.quantile(neu_err, 0.25)
    lo_pdb = np.quantile(pdb_err, 0.25)

    cases = []
    for k in rids:
        r = ocs[k]
        ne = r["neural_yaw_err"]; pe = r["pdb_top1_yaw_err"]
        pm = r["pdb_margin"]; pd = r["pdb_nearest_distance"]; ps = r["pdb_cand_yaw_spread"]
        labels = []
        # 1. OCS-hard
        if ne > hi_neu and (pm < lo_margin or pd > hi_dist):
            labels.append("ocs-hard")
        # 3. disagreement-hard
        if (ne <= 30) != (pe <= 30):
            labels.append("disagreement-hard")
        # 4. ambiguous-flux
        if ps > hi_spread and pd < np.quantile(pdb_dist, 0.5):
            labels.append("ambiguous-flux")
        # 5. robust-easy（对照）：neural 与 P-DB 都高精度(hit@15)且 P-DB margin 高于中位数
        if ne <= 15 and pe <= 15 and pm > np.quantile(pdb_margin, 0.5):
            labels.append("robust-easy")
        # 2. image-hard（查 image_only/joint 高 error 或低 confidence）
        img_flag = ""
        for m in ("image_only", "joint"):
            if m in by_mode and k in by_mode[m]:
                ir = by_mode[m][k]
                if ir["neural_yaw_err"] > 30:
                    labels.append(f"image-hard({m})")
                    img_flag = m
        if labels:
            cases.append({
                "degrade_level": deg, "geom": geom, "select": select, "record_id": k,
                "yaw_true": r["yaw_true"], "pitch_true": r["pitch_true"],
                "neural_ocs_yaw_err": round(ne, 3),
                "image_yaw_err": round(by_mode["image_only"][k]["neural_yaw_err"], 3)
                    if ("image_only" in by_mode and k in by_mode["image_only"]) else "",
                "joint_yaw_err": round(by_mode["joint"][k]["neural_yaw_err"], 3)
                    if ("joint" in by_mode and k in by_mode["joint"]) else "",
                "pdb_yaw_err": round(pe, 3),
                "pdb_margin": round(pm, 6), "pdb_nearest_distance": round(pd, 6),
                "pdb_cand_yaw_spread": round(ps, 3),
                "hardcase_labels": ";".join(labels),
            })
    return cases


def main():
    hc_dir = C.OUT / "hardcases"
    hc_dir.mkdir(parents=True, exist_ok=True)
    rows = load_joined()

    all_cases = []
    for deg in C.DEGRADE_ALL:
        for geom in C.GROUPS:
            all_cases.extend(classify(rows, deg, geom, "best"))

    with open(hc_dir / "l1d3_hardcase_index.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["degrade_level", "geom", "select", "record_id", "yaw_true", "pitch_true",
                "neural_ocs_yaw_err", "image_yaw_err", "joint_yaw_err", "pdb_yaw_err",
                "pdb_margin", "pdb_nearest_distance", "pdb_cand_yaw_spread", "hardcase_labels"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(all_cases)

    # 统计
    def _count(label, deg=None, geom=None):
        n = 0
        for c in all_cases:
            if label in c["hardcase_labels"].split(";"):
                if deg and c["degrade_level"] != deg:
                    continue
                if geom and c["geom"] != geom:
                    continue
                n += 1
        return n

    labels = ["ocs-hard", "image-hard(image_only)", "image-hard(joint)",
              "disagreement-hard", "ambiguous-flux", "robust-easy"]

    md = ["# R118 子任务 E：Hard-case 候选索引摘要\n",
          "最后更新：2026-07-01  \n",
          "**hard-case index 是后续 P-INT-hard / stronger degraded 的候选输入，不是阶段门放行。**\n"]
    md.append("## 1. 各类 hard-case 计数（select=best，全 deg×geom）\n")
    md.append("| label | 计数 |")
    md.append("|:--|--:|")
    for lb in labels:
        md.append(f"| {lb} | {_count(lb)} |")
    md.append("")
    md.append("## 2. 按退化等级分布（关键类，G5）\n")
    md.append("| degrade | ocs-hard | disagreement | ambiguous-flux | robust-easy |")
    md.append("|:--|--:|--:|--:|--:|")
    for deg in C.DEGRADE_ALL:
        md.append(f"| {deg} | {_count('ocs-hard', deg, 'G5')} | "
                  f"{_count('disagreement-hard', deg, 'G5')} | "
                  f"{_count('ambiguous-flux', deg, 'G5')} | "
                  f"{_count('robust-easy', deg, 'G5')} |")
    md.append("")
    md.append("## 3. 定义与阈值（可审计）\n")
    md.append("```text")
    md.append("阈值均基于该 (deg,geom) 层 ocs_only 分布分位数，非直觉手挑：")
    md.append("  ocs-hard      : neural_yaw_err>P75 且 (pdb_margin<P25 或 pdb_nearest_distance>P75)")
    md.append("  image-hard    : image_only/joint neural_yaw_err>30°")
    md.append("  disagreement  : neural hit@30 与 pdb hit@30 不一致（一对一错）")
    md.append("  ambiguous-flux: pdb_cand_yaw_spread>P75 且 nearest_distance<P50（候选分散但都近）")
    md.append("  robust-easy   : neural_yaw_err≤15° 且 pdb_yaw_err≤15° 且 pdb_margin>P50（对照）")
    md.append("```")
    open(hc_dir / "l1d3_hardcase_summary.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

    # 下一步设计建议
    n_ocs_hard_g5 = _count("ocs-hard", geom="G5")
    n_disagree = _count("disagreement-hard")
    design = ["# P-INT-hard / stronger degraded 下一步设计建议（R118 子任务 E）\n",
              "最后更新：2026-07-01  \n",
              "**本文件只写下一步设计建议，不放行训练。作者/Codex 决定是否启动。**\n"]
    design.append("## 1. 现状观察（绑定本轮输出）\n")
    design.append("```text")
    design.append(f"- ocs_only G5 hard-case（跨退化）：{n_ocs_hard_g5} 例，集中在 P-DB margin 低 / nearest 距离高的姿态。")
    design.append(f"- disagreement-hard（neural 与 P-DB 一对一错）：{n_disagree} 例，是互补空间的核心候选。")
    design.append("- image_only/joint 在本轮 mild/moderate 下 hit@30 仍高，image-hard 较少 → 图像天花板未被本级退化触及。")
    design.append("- P-DB ocs_only 在 clean/mild 上 top1 hit@30 高于 neural ocs_only 回归（见子任务 B/C），")
    design.append("  说明多观测总光度向量含 yaw 信息未被神经回归充分利用。")
    design.append("```\n")
    design.append("## 2. 候选 split / 子集定义\n")
    design.append("```text")
    design.append("- subset-A（disagreement 核心）：disagreement-hard ∪ ocs-hard 的 G5 姿态，作为 P-INT-hard 难例池。")
    design.append("- subset-B（ambiguous-flux）：候选 yaw 分散姿态，用于检验 top-k / posterior 是否能表达多峰。")
    design.append("- 对照 robust-easy：低难度姿态，验证难例定义不是纯噪声。")
    design.append("```\n")
    design.append("## 3. 是否需要更强 degraded / 补 joint-full M-roll\n")
    design.append("```text")
    design.append("- 建议增设 degraded-severe（更强 PSF/更低 photon/更大 flux 噪声）以触及图像天花板，")
    design.append("  才能检验 joint 是否显现强互补；本轮 mild/moderate 未触及。")
    design.append("- joint/full-2664 M-roll 成本高（R117 估 10–11h），建议仅在 disagreement subset 上按需补，")
    design.append("  不铺全量。")
    design.append("```\n")
    design.append("## 4. 预计训练矩阵与成本（粗估，仅供裁决参考）\n")
    design.append("```text")
    design.append("- P-INT-hard 难例微调/评估：G5 × {ocs_only,joint} × {moderate,severe} ≈ 4 run，沿用现 backbone。")
    design.append("- degraded-severe 需新渲染或在现有 EXR 上加噪：若纯后处理加噪则无需重渲，成本可控。")
    design.append("- 不做开放超参搜索、不换 backbone。")
    design.append("```\n")
    design.append("## 5. 建议的下一阶段门指标\n")
    design.append("```text")
    design.append("- 主指标：joint 在 degraded-severe / P-INT-hard 上相对 image_only 的 yaw hit@30 增量是否显著为正。")
    design.append("- 辅指标：P-DB top1 与 neural 的 oracle_hit@30 差距是否收窄（互补是否被模型吸收）。")
    design.append("- conformal set_size 是否随几何数继续单调收紧。")
    design.append("```")
    open(hc_dir / "l1d3_recommended_pinthard_design.md", "w", encoding="utf-8").write("\n".join(design) + "\n")

    print(f"[E] hard-case rows={len(all_cases)}")
    for lb in labels:
        print(f"  {lb}: {_count(lb)}")
    print(f"  -> {hc_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

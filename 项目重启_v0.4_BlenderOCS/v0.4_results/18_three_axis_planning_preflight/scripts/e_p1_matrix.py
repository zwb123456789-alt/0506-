#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
18 号三轴准备包 - 子任务E：P1 seed-roll scan 预注册矩阵（只读，仅规划）

从 66 seed 中选 12 个类别代表（覆盖 bright/dark/high-info/low-info/
ocs-hard/image-hard/disagreement/roll-sensitive/robust-easy），
生成 P1 预注册矩阵与预期输出清单。

输出：
  tables/p1_seed_roll_pre_registered_matrix.csv
  tables/p1_expected_outputs.csv
本轮不执行渲染。
"""
import csv
import os

V04 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(V04, "v0.4_results", "18_three_axis_planning_preflight")

ROLL_GRID = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
ROLL_NONZERO = [r for r in ROLL_GRID if r != 0]
# P1 每类选几个代表（总 12）
PER_CAT = {
    "bright-seed": 2, "high-info-seed": 2, "roll-sensitive-seed": 2,
    "low-info-seed": 1, "ocs-hard-seed": 1, "disagreement-seed": 1,
    "image-hard-seed": 1, "dark-seed": 1, "robust-easy-seed": 1,
}


def main():
    seeds = list(csv.DictReader(
        open(os.path.join(OUT, "seeds", "three_axis_seed_candidates.csv"), encoding="utf-8")))
    bycat = {}
    for s in seeds:
        bycat.setdefault(s["category"], []).append(s)

    chosen = []
    for cat, k in PER_CAT.items():
        chosen.extend(bycat.get(cat, [])[:k])

    # 预注册矩阵：每个种子 × 每个非零 roll 一行
    rows = []
    for s in chosen:
        for roll in ROLL_NONZERO:
            rows.append({
                "seed_id": s["seed_id"],
                "record_id": s["record_id"],
                "yaw": s["yaw"], "pitch": s["pitch"], "roll": roll,
                "category": s["category"],
                "geom": "phase63(L1-G1)",
                "render_needed": "YES",
                "roll0_reuse": "roll=0 复用 01_fullrun, 不重渲",
                "planned_metrics": "ocs_total;image_usable;local_contrast;roll_sensitivity",
            })
    with open(os.path.join(OUT, "tables", "p1_seed_roll_pre_registered_matrix.csv"),
              "w", newline="", encoding="utf-8") as f:
        fields = ["seed_id", "record_id", "yaw", "pitch", "roll", "category",
                  "geom", "render_needed", "roll0_reuse", "planned_metrics"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # 预期输出清单
    exp = [
        ("p1_seed_roll_ocs_curves.csv", "每种子 OCS magnitude vs roll 曲线", "table"),
        ("p1_seed_roll_contrast.csv", "每种子 local contrast vs roll", "table"),
        ("p1_seed_roll_sensitivity.csv", "roll 迁移量: 最亮/可分点是否随 roll 移动", "table"),
        ("p1_image_usability_flags.csv", "每 seed×roll 图像渲染是否可用(非空/未饱和)", "table"),
        ("p1_seed_roll_curves.png", "OCS/contrast vs roll 多子图", "figure"),
        ("p1_seed_roll_summary.md", "P1 smoke 结论: fixed-roll 是否被 roll 推翻", "text"),
    ]
    with open(os.path.join(OUT, "tables", "p1_expected_outputs.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["expected_output", "description", "kind"])
        w.writerows(exp)

    print("[E] P1 pre-registered matrix done.")
    print(f"  chosen seeds: {len(chosen)}")
    print(f"  matrix rows (seed x nonzero-roll): {len(rows)}")
    print(f"  render units (=rows, roll=0 reused): {len(rows)}")


if __name__ == "__main__":
    main()

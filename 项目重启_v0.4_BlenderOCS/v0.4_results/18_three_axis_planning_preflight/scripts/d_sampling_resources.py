#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
18 号三轴准备包 - 子任务D：采样策略与资源估计（只读，仅规划）

输出：
  tables/three_axis_stage_matrix.csv
  resources/render_train_storage_estimate.csv

基准（实测，来自 17 号 M-roll full-2664 渲染日志）：
  - phase63 4 个 roll 档 × 2664 姿态，16:58->18:55 ≈ 117 min，约 9376 张实渲。
  - 单张 shadow-camera EXR ≈ 9.8 KB（linear.exr）；单几何单 roll 全量 shadow_passes ≈ 698 MB / 2664 姿态。
  - 渲染速率约 117min / 9376 张 ≈ 0.75 s/张（含 skip 与 postprocess，取保守 1.0 s/张）。
本轮只写估计，不执行 P1-P4。
"""
import csv
import os

V04 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(V04, "v0.4_results", "18_three_axis_planning_preflight")

# 实测基准
SEC_PER_RENDER = 1.0          # 保守：单姿态单几何单 roll 一张（含 postprocess 摊薄）
MB_PER_ATT_GEOM_ROLL = 698.0 / 2664.0   # shadow_passes 全量足迹 ≈ 0.262 MB/姿态（含中间 pass）
OCS_JSON_KB = 0.5             # 每 ocs.json ≈ 0.5 KB

# 阶段定义
STAGES = [
    {
        "stage": "P1_seed_roll_scan",
        "desc": "围绕少量种子点扫描 roll",
        "n_seeds": 12,            # 从 66 seed 中选代表 12 个做 smoke
        "roll_grid": "{-60,-45,-30,-15,0,15,30,45,60} (roll=0 复用)",
        "n_roll_nonzero": 8,      # roll=0 复用，仅 8 个非零
        "n_geom": 1,              # smoke 用 phase63 / L1-G1
        "new_render": "YES (仅非零 roll)",
        "new_train": "NO",
        "outputs": "OCS magnitude, image 可用性, local contrast, roll sensitivity per seed",
        "min_accept": "12 种子 × 8 roll 渲染完成且 OCS/图像非空; roll 迁移曲线可画",
        "stop_expand": "若最亮/可分点在 roll 下不迁移->缩减; 若显著迁移->P2 扩几何",
    },
    {
        "stage": "P2_sparse_3axis_grid",
        "desc": "粗三轴网格 / 拉丁超立方采样",
        "n_seeds": 0,
        "roll_grid": "roll ∈ {-60..60 step 30} × 稀疏 yaw/pitch (每 15°)",
        "n_roll_nonzero": 4,
        "n_geom": 3,              # L1-G3
        "new_render": "YES",
        "new_train": "可选 (roll-aware 需另行放行)",
        "outputs": "三轴高亮/高信息候选集初稿, utility map 粗图",
        "min_accept": "覆盖 yaw/pitch/roll 三轴; 候选集含高亮+高信息+低信息三类",
        "stop_expand": "候选集稳定->P3; 若空间过大->改自适应采样",
    },
    {
        "stage": "P3_local_refinement",
        "desc": "对最亮/高信息/低信息候选局部加密",
        "n_seeds": 0,
        "roll_grid": "候选邻域 roll/yaw/pitch step 5-10°",
        "n_roll_nonzero": 8,
        "n_geom": 5,              # L1-G5
        "new_render": "YES",
        "new_train": "可选",
        "outputs": "最亮构型 + 最优可观测姿态精定位",
        "min_accept": "每类候选局部加密完成; 最亮/高信息点定位收敛",
        "stop_expand": "定位收敛->P4; 若不收敛->回 P2 补采样",
    },
    {
        "stage": "P4_observation_planning_synthesis",
        "desc": "输出几何/姿态组合 utility map",
        "n_seeds": 0,
        "roll_grid": "汇总 P1-P3，不新增采样",
        "n_roll_nonzero": 0,
        "n_geom": 5,
        "new_render": "NO",
        "new_train": "NO",
        "outputs": "observation planning utility map, 值得/低价值/风险几何清单",
        "min_accept": "utility map + 三类几何清单 + 与路线二/三接口说明",
        "stop_expand": "交 Codex 审阅是否作为三轴小项目成果",
    },
]


def main():
    # stage matrix
    with open(os.path.join(OUT, "tables", "three_axis_stage_matrix.csv"),
              "w", newline="", encoding="utf-8") as f:
        fields = ["stage", "desc", "n_seeds", "roll_grid", "n_roll_nonzero",
                  "n_geom", "new_render", "new_train", "outputs",
                  "min_accept", "stop_expand"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for s in STAGES:
            w.writerow(s)

    # resource estimate
    res_rows = []
    for s in STAGES:
        if s["stage"] == "P1_seed_roll_scan":
            n_att = s["n_seeds"] * s["n_roll_nonzero"]
        elif s["stage"] == "P2_sparse_3axis_grid":
            # 稀疏 yaw(每15°=24) × pitch(每15°=13) × 4 roll × 3 geom
            n_att = 24 * 13 * s["n_roll_nonzero"] * s["n_geom"]
        elif s["stage"] == "P3_local_refinement":
            # 假设 30 候选 × 邻域 27 点 × 8 roll × 5 geom（上界估计）
            n_att = 30 * 27 * s["n_roll_nonzero"] * s["n_geom"]
        else:
            n_att = 0
        render_h = n_att * SEC_PER_RENDER / 3600.0
        storage_mb = n_att * MB_PER_ATT_GEOM_ROLL + n_att * OCS_JSON_KB / 1024.0
        res_rows.append({
            "stage": s["stage"],
            "est_render_units": n_att,
            "new_render": s["new_render"],
            "est_render_hours@1s": round(render_h, 2),
            "est_storage_MB": round(storage_mb, 1),
            "new_train": s["new_train"],
            "note": "roll=0 复用不计" if "复用" in s["roll_grid"] else "",
        })
    with open(os.path.join(OUT, "resources", "render_train_storage_estimate.csv"),
              "w", newline="", encoding="utf-8") as f:
        fields = ["stage", "est_render_units", "new_render", "est_render_hours@1s",
                  "est_storage_MB", "new_train", "note"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(res_rows)

    print("[D] sampling + resource estimate done.")
    for r in res_rows:
        print(f"  {r['stage']}: {r['est_render_units']} units, "
              f"{r['est_render_hours@1s']} h, {r['est_storage_MB']} MB")


if __name__ == "__main__":
    main()

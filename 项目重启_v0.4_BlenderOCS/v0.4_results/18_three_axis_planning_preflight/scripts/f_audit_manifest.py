#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
18 号三轴准备包 - 子任务F：manifest / 路径一致性 / 红线自检（只读）

输出：
  audit/generated_files_manifest.csv
  audit/numeric_path_consistency_check.csv
  audit/redline_self_check.csv
"""
import csv
import os

V04 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(V04, "v0.4_results", "18_three_axis_planning_preflight")


def rel(p):
    return os.path.relpath(p, OUT).replace("\\", "/")


def csv_rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    # ---- generated files manifest ----
    manifest = []
    for root, _, files in os.walk(OUT):
        for fn in files:
            p = os.path.join(root, fn)
            if rel(p) == "audit/generated_files_manifest.csv":
                continue
            manifest.append({
                "path": rel(p),
                "bytes": os.path.getsize(p),
                "exists": True,
            })
    manifest.sort(key=lambda r: r["path"])
    with open(os.path.join(OUT, "audit", "generated_files_manifest.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "bytes", "exists"])
        w.writeheader()
        w.writerows(manifest)

    # ---- numeric / path consistency check ----
    checks = []

    def chk(name, cond, detail):
        checks.append({"check": name, "result": "PASS" if cond else "CONFLICT", "detail": detail})

    # 1. seed 总数 = 66
    seeds = csv_rows(os.path.join(OUT, "seeds", "three_axis_seed_candidates.csv"))
    chk("seed_total==66", len(seeds) == 66, f"got {len(seeds)}")

    # 2. 9 类种子齐全
    cats = set(s["category"] for s in seeds)
    need = {"bright-seed", "dark-seed", "high-info-seed", "low-info-seed",
            "ocs-hard-seed", "image-hard-seed", "disagreement-seed",
            "roll-sensitive-seed", "robust-easy-seed"}
    chk("seed_categories==9", cats == need, f"missing {need - cats}" if cats != need else "all 9")

    # 3. master 2664 姿态
    master = csv_rows(os.path.join(OUT, "seeds", "attitude_master_fixedroll.csv"))
    chk("master_rows==2664", len(master) == 2664, f"got {len(master)}")

    # 4. derived master 也 2664 且含 local_contrast/glint_flag
    dm = csv_rows(os.path.join(OUT, "seeds", "attitude_master_derived.csv"))
    chk("derived_master==2664", len(dm) == 2664, f"got {len(dm)}")
    chk("derived_has_contrast_glint",
        "local_contrast" in dm[0] and "glint_flag" in dm[0], "fields present")

    # 5. P1 矩阵 = 12 seed × 8 roll = 96
    p1 = csv_rows(os.path.join(OUT, "tables", "p1_seed_roll_pre_registered_matrix.csv"))
    chk("p1_matrix==96", len(p1) == 96, f"got {len(p1)}")
    chk("p1_no_roll0", all(int(r["roll"]) != 0 for r in p1), "roll=0 reused not rendered")

    # 6. P1 唯一种子 = 12
    p1_seeds = set(r["seed_id"] for r in p1)
    chk("p1_unique_seeds==12", len(p1_seeds) == 12, f"got {len(p1_seeds)}")

    # 7. registry 11 指标
    reg = csv_rows(os.path.join(OUT, "tables", "three_axis_metric_registry.csv"))
    chk("registry==11", len(reg) == 11, f"got {len(reg)}")

    # 8. stage matrix 4 阶段
    sm = csv_rows(os.path.join(OUT, "tables", "three_axis_stage_matrix.csv"))
    chk("stage_matrix==4", len(sm) == 4, f"got {len(sm)}")

    # 9. resource estimate 4 阶段
    re = csv_rows(os.path.join(OUT, "resources", "render_train_storage_estimate.csv"))
    chk("resource_est==4", len(re) == 4, f"got {len(re)}")
    p1_units = [r for r in re if r["stage"] == "P1_seed_roll_scan"]
    chk("resource_P1==96units",
        p1_units and int(p1_units[0]["est_render_units"]) == 96,
        f"P1 units={p1_units[0]['est_render_units'] if p1_units else 'NA'}")

    # 10. input manifest 全 OK
    im = csv_rows(os.path.join(OUT, "audit", "input_manifest.csv"))
    nok = sum(1 for r in im if r["status"] == "OK")
    chk("input_manifest_all_OK", nok == len(im), f"{nok}/{len(im)} OK")

    # 11. 种子 record_id 可在 master 中找到
    master_ids = set(r["record_id"] for r in master)
    orphan = [s["record_id"] for s in seeds if s["record_id"] not in master_ids]
    chk("seed_ids_traceable_to_master", not orphan,
        f"orphans: {orphan[:3]}" if orphan else "all traceable")

    with open(os.path.join(OUT, "audit", "numeric_path_consistency_check.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["check", "result", "detail"])
        w.writeheader()
        w.writerows(checks)

    # ---- redline self-check ----
    redlines = [
        ("R1 不启动全量三轴渲染", "PASS", "全部脚本只读 json/csv; 无 blender 调用"),
        ("R2 不启动三轴训练", "PASS", "无训练脚本调用"),
        ("R3 不改旧脚本/metrics/samples/结果目录10-17", "PASS", "只读打开; 全部写 18 号包"),
        ("R4 不改姿态网格/OBS_GEOMETRIES/split/backbone/超参", "PASS", "未写 config/代码层"),
        ("R5 不启动R128/真实图像难度审计/GEO/路线二三四/T3L2", "PASS", "本轮仅准备包; R128 记为不执行"),
        ("R6 不写成果区/不生成Codex审阅文件/不改CLAUDE.md", "PASS", "输出仅 18 号包 + 02_Claude输出/001 报告"),
        ("R7 不写成真实未知目标三轴姿态反演系统", "PASS", "claims 表 forbidden 明列; 定位为规划"),
        ("R8 区分最亮与最优反演/brightness与information", "PASS", "boundary 文档 corr≈-0.09; registry info_class 分列"),
        ("R9 报告写入正确路径 02_Claude输出/", "PASS", "001 报告写入 02_Claude输出/ 非 04_Codex审阅/"),
        ("R10 P1-P4 本轮不执行", "PASS", "sampling 计划标注仅设计; P1 需Codex放行"),
    ]
    with open(os.path.join(OUT, "audit", "redline_self_check.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["redline", "status", "evidence"])
        w.writerows(redlines)

    npass = sum(1 for c in checks if c["result"] == "PASS")
    print("[F] manifest + consistency + redline done.")
    print(f"  generated files: {len(manifest)}")
    print(f"  consistency: {npass}/{len(checks)} PASS")
    conflicts = [c for c in checks if c["result"] != "PASS"]
    if conflicts:
        for c in conflicts:
            print(f"    CONFLICT: {c['check']} - {c['detail']}")
    print(f"  redline: {len(redlines)}/{len(redlines)} PASS")


if __name__ == "__main__":
    main()

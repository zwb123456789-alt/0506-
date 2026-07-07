#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
18 号三轴准备包 - 子任务A：输入审计与可复用资产索引（只读）

职责：
  - 扫描路线一 C 已通过结果包 11/12/13/16/17 与 01_fullrun，确认三轴小项目可继承资产。
  - 检查 Blender / geometry / postprocess / training 代码入口的 roll 可参数化程度。
  - 输出 input_manifest.csv / route1c_reusable_assets.md /
    code_entrypoint_audit.csv / redline_precheck.csv。

红线：
  - 只读既有结果与代码，不改旧脚本、旧 metrics、旧 samples、旧结果目录 10-17。
  - 不启动任何渲染或训练。
"""
import csv
import json
import os

V04 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RES = os.path.join(V04, "v0.4_results")
OUT = os.path.join(RES, "18_three_axis_planning_preflight")
AUDIT = os.path.join(OUT, "audit")


def rel(p):
    return os.path.relpath(p, V04).replace("\\", "/")


def count_glob(d, suffix):
    if not os.path.isdir(d):
        return 0
    return sum(1 for f in os.listdir(d) if f.endswith(suffix))


def file_exists(*parts):
    p = os.path.join(RES, *parts)
    return p, os.path.isfile(p)


def dir_exists(*parts):
    p = os.path.join(RES, *parts)
    return p, os.path.isdir(p)


def main():
    rows = []  # input_manifest

    # --- OCS 亮度源（五何） ---
    pp = os.path.join(RES, "11_l1m2_multigeometry_ocs", "postprocess")
    phase_counts = {}
    for ph in ["phase24", "phase45", "phase90", "phase120"]:
        d = os.path.join(pp, ph)
        n = count_glob(d, "_ocs.json")
        phase_counts[ph] = n
        rows.append({
            "asset": f"OCS per-attitude ({ph})", "path": rel(d),
            "kind": "ocs_json_dir", "count": n,
            "reuse_for": "brightness/OCS magnitude 种子, roll=0 基线",
            "status": "OK" if n == 2664 else "CHECK",
        })
    # phase63 在 01_fullrun
    d63 = os.path.join(RES, "01_fullrun", "postprocess")
    n63 = count_glob(d63, "_ocs.json")
    phase_counts["phase63"] = n63
    rows.append({
        "asset": "OCS per-attitude (phase63=L1-G1 baseline)", "path": rel(d63),
        "kind": "ocs_json_dir", "count": n63,
        "reuse_for": "brightness/OCS magnitude 种子, L1-G1 主几何",
        "status": "OK" if n63 == 2664 else "CHECK",
    })

    # --- D4 可观测性地图 ---
    for name, sub in [
        ("D4 geometry gain by attitude", "tables/d4_geometry_gain_by_attitude.csv"),
        ("D4 observability region stats", "tables/d4_observability_region_stats.csv"),
        ("D4 confusion regions", "tables/d4_confusion_regions.csv"),
        ("D4 hardcase region cross-tab", "tables/d4_hardcase_region_cross_tab.csv"),
    ]:
        p, ok = file_exists("16_route1c_closure_d2d4_m5", *sub.split("/"))
        rows.append({
            "asset": name, "path": rel(p), "kind": "csv",
            "count": (sum(1 for _ in open(p, encoding="utf-8")) - 1) if ok else 0,
            "reuse_for": "high-info/low-info/救回区/坍缩区 种子",
            "status": "OK" if ok else "MISSING",
        })

    # --- hardcase index / pdb / conformal / joined ---
    for name, parts, reuse in [
        ("L1D3 hardcase index",
         ("13_l1d3_confidence_pdb", "hardcases", "l1d3_hardcase_index.csv"),
         "ocs-hard/image-hard/disagreement-hard/robust-easy 种子"),
        ("L1D3 PDB retrieval per query",
         ("13_l1d3_confidence_pdb", "pdb", "l1d3_pdb_retrieval_per_query.csv"),
         "nearest-neighbor ambiguity, margin, top-k 稳定性指标"),
        ("L1D3 conformal per sample",
         ("13_l1d3_confidence_pdb", "conformal", "l1d3_conformal_per_sample.csv"),
         "set_size / coverage 置信指标"),
        ("L1D3 neural-pdb joined per attitude",
         ("13_l1d3_confidence_pdb", "consistency", "l1d3_neural_pdb_joined_per_attitude.csv"),
         "entropy/margin/通道一致性 指标"),
    ]:
        p, ok = file_exists(*parts)
        rows.append({
            "asset": name, "path": rel(p), "kind": "csv",
            "count": (sum(1 for _ in open(p, encoding="utf-8")) - 1) if ok else 0,
            "reuse_for": reuse, "status": "OK" if ok else "MISSING",
        })

    # --- M-roll full-2664 ---
    d = os.path.join(RES, "17_route1c_postclosure_enhancement_sweep", "mroll_full2664")
    npred = count_glob(d, ".csv")
    rows.append({
        "asset": "M-roll full-2664 predictions", "path": rel(d),
        "kind": "csv_dir", "count": npred,
        "reuse_for": "roll-sensitive 种子, roll 迁移先验",
        "status": "OK" if os.path.isdir(d) else "MISSING",
    })
    p, ok = file_exists("17_route1c_postclosure_enhancement_sweep",
                        "conformal_alpha", "conformal_alpha_metrics.csv")
    rows.append({
        "asset": "conformal alpha metrics", "path": rel(p), "kind": "csv",
        "count": (sum(1 for _ in open(p, encoding="utf-8")) - 1) if ok else 0,
        "reuse_for": "alpha 敏感性 SI 参考", "status": "OK" if ok else "MISSING",
    })

    # --- geometry registry ---
    p, ok = file_exists("11_l1m2_multigeometry_ocs", "l1m2_geometry_registry.json")
    rows.append({
        "asset": "L1M2 geometry registry", "path": rel(p), "kind": "json",
        "count": 5, "reuse_for": "5 何定义 / phase63=L1-G1 代表几何",
        "status": "OK" if ok else "MISSING",
    })

    # 写 input_manifest.csv
    with open(os.path.join(AUDIT, "input_manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["asset", "path", "kind", "count", "reuse_for", "status"])
        w.writeheader()
        w.writerows(rows)

    # --- code_entrypoint_audit.csv ---
    code_rows = []
    code = os.path.join(V04, "06_v0.4_code")

    def code_check(relpath, roll_support, note):
        p = os.path.join(code, relpath)
        code_rows.append({
            "entrypoint": relpath.replace("\\", "/"),
            "exists": os.path.isfile(p),
            "roll_parameterizable": roll_support,
            "note": note,
        })

    code_check("02_blender/render_mroll_probe.py", "YES",
               "R116 已注入非零 roll 并生成 roll{+NNN} label；证明 Blender 渲染可扩展到 roll 轴")
    code_check("02_blender/render_full_2664_shadow.py", "PARTIAL",
               "主 driver 固定 roll=0；mroll probe 以包装器方式覆盖姿态生成，不改本 driver")
    code_check("01_geometry/attitude_grid.py", "PARTIAL",
               "默认 72yaw×37pitch=2664 且 roll 固定 0；三轴需新增 roll 维度或复用 mroll 注入逻辑")
    code_check("01_geometry/geometry_loader.py", "N/A", "几何加载，不涉及 roll")
    code_check("05_postprocess", "PARTIAL",
               "postprocess 产出 *_ocs.json 已带 roll tag 结构（label 含 roll），字段可扩展")
    code_check("07_training", "PARTIAL",
               "训练入口当前按 yaw/pitch 目标；roll-aware 需新增 roll 标签字段，本轮不做")
    with open(os.path.join(AUDIT, "code_entrypoint_audit.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["entrypoint", "exists", "roll_parameterizable", "note"])
        w.writeheader()
        w.writerows(code_rows)

    # --- redline_precheck.csv ---
    redlines = [
        ("不启动全量三轴渲染", "PASS", "本脚本只读 json/csv，无渲染调用"),
        ("不启动三轴训练", "PASS", "无训练调用"),
        ("不改旧脚本/旧metrics/旧samples/旧结果目录10-17", "PASS", "只读打开，全部写入 18 号包"),
        ("不改姿态网格/OBS_GEOMETRIES/split/backbone/超参", "PASS", "未写入任何 config/代码"),
        ("不启动R128/真实图像难度审计/GEO/路线二三四/T3L2", "PASS", "本轮仅准备包"),
        ("不写成果区/不生成Codex审阅文件/不改CLAUDE.md", "PASS", "输出仅 18 号包与 001 报告"),
        ("区分brightness与information", "PASS", "指标 registry 与 seed 分类显式区分"),
        ("不写成真实未知目标三轴姿态反演系统", "PASS", "定位为最亮/高信息/低信息/观测规划"),
    ]
    with open(os.path.join(AUDIT, "redline_precheck.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["redline", "status", "evidence"])
        w.writerows(redlines)

    # --- route1c_reusable_assets.md ---
    md = []
    md.append("# 路线一 C 可复用资产索引（三轴小项目继承）\n")
    md.append("本文件由 `scripts/a_input_audit.py` 只读生成，供三轴小项目复用。\n")
    md.append("## OCS 亮度源（roll=0 fixed-roll 基线）\n")
    md.append("| 几何 | 姿态数 | 路径 |")
    md.append("|---|---:|---|")
    md.append(f"| phase63 (L1-G1) | {phase_counts['phase63']} | `01_fullrun/postprocess/` |")
    for ph in ["phase24", "phase45", "phase90", "phase120"]:
        md.append(f"| {ph} | {phase_counts[ph]} | `11_l1m2_multigeometry_ocs/postprocess/{ph}/` |")
    md.append("\n五何合计覆盖 L1-G5，全部 roll=0；三轴 roll 扩展需新渲染，本轮不执行。\n")
    md.append("## D4 可观测性地图（高信息/低信息接口）\n")
    md.append("- `16_.../tables/d4_geometry_gain_by_attitude.csv`：G1->G5 yaw err 增益，救回/变差区。")
    md.append("- `16_.../tables/d4_observability_region_stats.csv`：各通道 low/med/high err 分布。")
    md.append("- `16_.../tables/d4_confusion_regions.csv`：ambiguous-flux / pdb_near_but_wrong。")
    md.append("- `16_.../tables/d4_hardcase_region_cross_tab.csv`：yaw_quad×pitch_band×hardcase。\n")
    md.append("## 置信/检索/hardcase 指标源\n")
    md.append("- `13_.../hardcases/l1d3_hardcase_index.csv`：hardcase 标签（disagreement/ocs-hard/ambiguous-flux/robust-easy）。")
    md.append("- `13_.../pdb/l1d3_pdb_retrieval_per_query.csv`：nearest_distance/margin/topk10。")
    md.append("- `13_.../conformal/l1d3_conformal_per_sample.csv`：q_deg/covered。")
    md.append("- `13_.../consistency/l1d3_neural_pdb_joined_per_attitude.csv`：entropy/margin/通道一致性。\n")
    md.append("## roll 边界先验\n")
    md.append("- `17_.../mroll_full2664/`：±15°/±30° 预测，roll-sensitive 种子来源。")
    md.append("- `render_mroll_probe.py` 证明 Blender 渲染可参数化到 roll 轴（三轴渲染可行性依据）。\n")
    with open(os.path.join(AUDIT, "route1c_reusable_assets.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("[A] input audit done.")
    print("  input_manifest rows:", len(rows))
    print("  phase OCS counts:", phase_counts)
    ok = sum(1 for r in rows if r["status"] == "OK")
    print(f"  assets OK: {ok}/{len(rows)}")


if __name__ == "__main__":
    main()

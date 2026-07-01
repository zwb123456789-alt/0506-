#!/usr/bin/env python3
"""
build_l1d3_pdb_templates.py —— R118 子任务 A：正式输入索引与审计复核

基于 R117 的：
  12_l1m3/d3/l1m3_confidence_inputs_index.csv
  12_l1m3/audit/l1m2_val_samples_recovery_summary.csv
  12_l1m3/audit/l1m2_transform_leakage_check.json

生成本轮正式输入索引 + 字段审计：
  13_l1d3/audit/l1d3_input_manifest.csv
  13_l1d3/audit/l1d3_input_manifest.json
  13_l1d3/audit/l1d3_input_audit.md

审计要点：
  1. 每个 run 的 source/protocol/geometry_group/mode/degrade_level/split/select/path/n_samples/字段完整性。
  2. val/test 分开；校准/阈值只能用 val。
  3. clean 来自 11_l1m2；degraded 来自 12_l1m3，来源标清。
  4. posterior-like 标注为工程候选分数，非真实 Bayesian posterior。
  5. 字段缺失显式列出，不静默跳过。

(名字沿用 R118 建议的脚本清单；本文件承担子任务 A。)
"""

import csv
import json

import numpy as np

import l1d3_common as C

REQUIRED_FIELDS = [
    "record_id", "yaw_true_deg", "pitch_true_deg", "yaw_pred_deg", "pitch_pred_deg",
    "yaw_circular_error_deg", "pitch_abs_error_deg", "geometry_group", "mode",
    "protocol", "posterior_like_top5_idx", "posterior_like_top5_score",
    "entropy", "margin", "candidate_grid",
]

# 本轮正式评估矩阵（依据 11_l1m2 / 12_l1m3 实际存在的 run）
CLEAN_MATRIX = [  # (protocol, geom, mode)
    ("P-INT", g, m) for g in C.GROUPS for m in C.MODES
] + [("P-EXT", g, "ocs_only") for g in C.GROUPS]

# degraded 只有 ocs_only G1/G3/G5 与 image_only/joint G1/G5
DEGRADED_MATRIX = []
for lvl in ["degraded-mild", "degraded-moderate"]:
    for g in C.GROUPS:
        DEGRADED_MATRIX.append((lvl, "P-INT", g, "ocs_only"))
    for g in ["G1", "G5"]:
        DEGRADED_MATRIX.append((lvl, "P-INT", g, "image_only"))
        DEGRADED_MATRIX.append((lvl, "P-INT", g, "joint"))


def audit_npz(path):
    """加载 npz，检查必需字段与样本数；返回 (n_samples, missing_fields)。"""
    d = np.load(path, allow_pickle=True)
    present = set(d.files)
    missing = [f for f in REQUIRED_FIELDS if f not in present]
    n = int(len(d["record_id"])) if "record_id" in present else 0
    return n, missing


def build_manifest():
    rows = []
    # clean
    for prot, g, m in CLEAN_MATRIX:
        for split in ("val", "test"):
            for select in ("final", "best"):
                rd = C.clean_run_dir(prot, g, m)
                npz = rd / f"samples_{split}_{select}.npz"
                if not npz.exists():
                    rows.append({
                        "source": "R115-clean(11_l1m2)", "protocol": prot,
                        "geometry_group": g, "mode": m, "degrade_level": "clean",
                        "split": split, "select": select,
                        "path": str(npz.relative_to(C.PROJECT_ROOT)),
                        "n_samples": 0, "missing_fields": "FILE_NOT_FOUND",
                        "field_complete": False,
                    })
                    continue
                n, missing = audit_npz(npz)
                rows.append({
                    "source": "R115-clean(11_l1m2)", "protocol": prot,
                    "geometry_group": g, "mode": m, "degrade_level": "clean",
                    "split": split, "select": select,
                    "path": str(npz.relative_to(C.PROJECT_ROOT)),
                    "n_samples": n,
                    "missing_fields": ";".join(missing) if missing else "",
                    "field_complete": not missing,
                })
    # degraded
    for lvl, prot, g, m in DEGRADED_MATRIX:
        for split in ("val", "test"):
            for select in ("final", "best"):
                rd = C.degraded_run_dir(lvl, prot, g, m)
                npz = rd / f"samples_{split}_{select}.npz"
                if not npz.exists():
                    rows.append({
                        "source": "R116-degraded(12_l1m3)", "protocol": prot,
                        "geometry_group": g, "mode": m, "degrade_level": lvl,
                        "split": split, "select": select,
                        "path": str(npz.relative_to(C.PROJECT_ROOT)),
                        "n_samples": 0, "missing_fields": "FILE_NOT_FOUND",
                        "field_complete": False,
                    })
                    continue
                n, missing = audit_npz(npz)
                rows.append({
                    "source": "R116-degraded(12_l1m3)", "protocol": prot,
                    "geometry_group": g, "mode": m, "degrade_level": lvl,
                    "split": split, "select": select,
                    "path": str(npz.relative_to(C.PROJECT_ROOT)),
                    "n_samples": n,
                    "missing_fields": ";".join(missing) if missing else "",
                    "field_complete": not missing,
                })
    return rows


def main():
    audit_dir = C.OUT / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    rows = build_manifest()

    cols = ["source", "protocol", "geometry_group", "mode", "degrade_level",
            "split", "select", "path", "n_samples", "missing_fields", "field_complete"]
    with open(audit_dir / "l1d3_input_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    n_total = len(rows)
    n_ok = sum(1 for r in rows if r["field_complete"])
    n_missing_file = sum(1 for r in rows if r["missing_fields"] == "FILE_NOT_FOUND")
    n_field_gap = sum(1 for r in rows if r["missing_fields"] and r["missing_fields"] != "FILE_NOT_FOUND")

    # 上游审计引用
    up_recovery = C.L1M3 / "audit" / "l1m2_val_samples_recovery_summary.csv"
    up_leak = C.L1M3 / "audit" / "l1m2_transform_leakage_check.json"
    leak = {}
    if up_leak.exists():
        leak = json.load(open(up_leak, encoding="utf-8"))

    summary = {
        "task": "R118-A l1d3 input manifest + field audit",
        "n_rows": n_total,
        "n_field_complete": n_ok,
        "n_file_not_found": n_missing_file,
        "n_field_gap": n_field_gap,
        "clean_source": "11_l1m2_multigeometry_ocs (R115, val by A1 recovery)",
        "degraded_source": "12_l1m3_degraded_mroll (R116)",
        "val_test_separated": True,
        "calibration_rule": "阈值/校准只用 val；test 只做最终评估，不反调",
        "posterior_like_note": "工程候选分数，非真实 Bayesian posterior",
        "upstream_recovery_summary": str(up_recovery.relative_to(C.PROJECT_ROOT)) if up_recovery.exists() else "MISSING",
        "upstream_leakage_check": str(up_leak.relative_to(C.PROJECT_ROOT)) if up_leak.exists() else "MISSING",
        "upstream_leakage_pass": leak,
        "rows": rows,
    }
    json.dump(summary, open(audit_dir / "l1d3_input_manifest.json", "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

    # markdown 审计报告
    md = []
    md.append("# R118 子任务 A：L1D3 输入索引与审计复核\n")
    md.append("最后更新：2026-07-01  \n")
    md.append("本文件为正式输入 manifest 的人读摘要；机读见 "
              "`l1d3_input_manifest.csv` / `l1d3_input_manifest.json`。\n")
    md.append("## 1. 总览\n")
    md.append(f"- 索引行数（run × split × select）：**{n_total}**")
    md.append(f"- 字段完整行数：**{n_ok}**")
    md.append(f"- 文件缺失行数：**{n_missing_file}**")
    md.append(f"- 字段缺口行数（文件存在但字段不全）：**{n_field_gap}**\n")

    md.append("## 2. 来源与红线\n")
    md.append("```text")
    md.append("clean    源：11_l1m2_multigeometry_ocs（R115；val per-attitude 由 R117-A1 checkpoint+确定性split恢复，Δcmae=0.0）")
    md.append("degraded 源：12_l1m3_degraded_mroll（R116；退化观测按 record_id 确定性复现）")
    md.append("val/test 严格分开；任何校准/阈值/quantile 只用 val，test 仅最终评估，不反调。")
    md.append("posterior-like（top5 score/entropy/margin）是工程候选分数，不是真实 Bayesian posterior。")
    md.append("P-DB 检索是 model-known simulated template retrieval，不是真实反演成功率。")
    md.append("```\n")

    md.append("## 3. 上游审计引用（R117 复核）\n")
    if leak:
        md.append("`l1m2_transform_leakage_check.json` 关键结论：")
        md.append("```json")
        md.append(json.dumps(leak, ensure_ascii=False, indent=2)[:1200])
        md.append("```\n")
    else:
        md.append("（未找到上游 leakage_check.json，需人工确认）\n")

    md.append("## 4. 矩阵覆盖（按 degrade_level × mode × geom，test/best 存在性）\n")
    md.append("| degrade_level | mode | G1 | G3 | G5 |")
    md.append("|:--|:--|:--:|:--:|:--:|")
    def _has(lvl, prot, g, m):
        rd = C.run_dir(lvl, prot, g, m)
        return "✓" if (rd / "samples_test_best.npz").exists() else "—"
    for lvl in C.DEGRADE_ALL:
        for m in C.MODES:
            md.append(f"| {lvl} | {m} | " +
                      " | ".join(_has(lvl, "P-INT", g, m) for g in C.GROUPS) + " |")
    md.append("\nP-EXT（仅 ocs_only）：")
    md.append("| protocol | mode | G1 | G3 | G5 |")
    md.append("|:--|:--|:--:|:--:|:--:|")
    md.append("| P-EXT | ocs_only | " +
              " | ".join(_has("clean", "P-EXT", g, "ocs_only") for g in C.GROUPS) + " |\n")

    # 字段缺口详情
    gaps = [r for r in rows if r["missing_fields"]]
    md.append("## 5. 字段缺口 / 文件缺失明细\n")
    if not gaps:
        md.append("无缺口：所有列入矩阵的 run × split × select 文件均存在且字段完整。\n")
    else:
        md.append("| path | 问题 |")
        md.append("|:--|:--|")
        for r in gaps:
            md.append(f"| {r['path']} | {r['missing_fields']} |")
        md.append("")

    open(audit_dir / "l1d3_input_audit.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

    print(f"[A] manifest rows={n_total} field_complete={n_ok} "
          f"file_not_found={n_missing_file} field_gap={n_field_gap}")
    print(f"  -> {audit_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

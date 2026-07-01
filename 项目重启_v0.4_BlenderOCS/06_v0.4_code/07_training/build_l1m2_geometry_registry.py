# -*- coding: utf-8 -*-
"""
build_l1m2_geometry_registry.py —— 1C-L1M2 几何注册表生成

任务（R114 §3）：
  - 从 config_v0_4.OBS_GEOMETRIES 读取 5 组观测几何
  - 明确区分两套编号：
      代码层  : OBS_GEOMETRIES[0..4] / 注释 G0~G4 / label phaseXX_*
      实验层  : L1-G1 / L1-G3 / L1-G5（嵌套设计 G1 ⊂ G3 ⊂ G5）
  - 计算每组几何的相位角 = arccos(dot(sun_hat, det_hat))
  - 输出 registry.json 与 registry.md 到 11_l1m2_multigeometry_ocs/

红线：本脚本只做注册与核验，不改路线定义；如发现冲突只报告。
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

import numpy as np

# Windows 控制台 GBK 兼容：强制 stdout UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "00_config"))

import config_v0_4 as cfg  # noqa: E402

OUTDIR = PROJECT_ROOT / "v0.4_results" / "11_l1m2_multigeometry_ocs"

# 实验组 → 代码 label 列表（嵌套设计，R114 §3 预注册）
# G1 ⊂ G3 ⊂ G5，保证"加几何=单调加信息"
EXPERIMENT_GROUPS = {
    "L1-G1": ["phase63_backscatter"],
    "L1-G3": ["phase24_near_backscatter", "phase63_backscatter", "phase120_forward_scatter"],
    "L1-G5": ["phase24_near_backscatter", "phase45_overhead", "phase63_backscatter",
              "phase90_side", "phase120_forward_scatter"],
}

# 渲染期使用的 geom_id（与现有 phase63 fullrun 对齐）
LABEL_TO_GEOMID = {
    "phase63_backscatter": "phase63",
    "phase24_near_backscatter": "phase24",
    "phase120_forward_scatter": "phase120",
    "phase90_side": "phase90",
    "phase45_overhead": "phase45",
}


def phase_angle_deg(sun_vec, det_vec):
    s = np.asarray(sun_vec, dtype=float)
    d = np.asarray(det_vec, dtype=float)
    s = s / np.linalg.norm(s)
    d = d / np.linalg.norm(d)
    cos_pa = float(np.clip(np.dot(s, d), -1.0, 1.0))
    return float(np.degrees(np.arccos(cos_pa))), cos_pa


def build():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # 1. 代码层几何表
    code_geoms = []
    label_index = {}
    for idx, (sun, det, label) in enumerate(cfg.OBS_GEOMETRIES):
        pa_deg, cos_pa = phase_angle_deg(sun, det)
        geomid = LABEL_TO_GEOMID.get(label, label)
        code_geoms.append({
            "code_index": idx,
            "code_comment_id": f"G{idx}",   # config 注释里的 G0~G4
            "label": label,
            "geom_id": geomid,
            "sun_vector": list(map(float, sun)),
            "det_vector": list(map(float, det)),
            "phase_angle_deg": round(pa_deg, 3),
            "phase_angle_cos": round(cos_pa, 6),
        })
        label_index[label] = idx

    # 2. 实验层组
    exp_groups = {}
    conflicts = []
    for exp_name, labels in EXPERIMENT_GROUPS.items():
        members = []
        for lab in labels:
            if lab not in label_index:
                conflicts.append(
                    f"{exp_name} 引用 label '{lab}'，但 config.OBS_GEOMETRIES 中不存在")
                continue
            ci = label_index[lab]
            g = code_geoms[ci]
            members.append({
                "label": lab,
                "code_index": ci,
                "geom_id": g["geom_id"],
                "phase_angle_deg": g["phase_angle_deg"],
            })
        # 按相位角排序便于阅读
        members_sorted = sorted(members, key=lambda m: m["phase_angle_deg"])
        exp_groups[exp_name] = {
            "n_geometries": len(members),
            "members": members,
            "members_by_phase_angle": [m["label"] for m in members_sorted],
            "geom_ids": [m["geom_id"] for m in members],
            "feature_vector_layout": [f"total_flux_{m['geom_id']}" for m in members],
        }

    # 3. 嵌套校验 G1 ⊂ G3 ⊂ G5
    s1 = set(EXPERIMENT_GROUPS["L1-G1"])
    s3 = set(EXPERIMENT_GROUPS["L1-G3"])
    s5 = set(EXPERIMENT_GROUPS["L1-G5"])
    nested_ok = s1.issubset(s3) and s3.issubset(s5)
    if not nested_ok:
        conflicts.append("嵌套设计被破坏：G1⊂G3⊂G5 不成立")

    registry = {
        "task": "1C-L1M2 geometry registry",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source_config": "06_v0.4_code/00_config/config_v0_4.py :: OBS_GEOMETRIES",
        "numbering_note": (
            "两套编号严格区分：'code_index'/'code_comment_id'(G0~G4) 来自 config 代码层；"
            "'L1-G1/L1-G3/L1-G5' 是实验组名(R114 §3)。二者不可混用。"
            "config 注释 G0~G4 ≠ 实验组 G1/G3/G5。"
        ),
        "nested_design": {
            "rule": "L1-G1 ⊂ L1-G3 ⊂ L1-G5",
            "ok": nested_ok,
        },
        "existing_data_status": {
            "phase63_backscatter": "已渲染（01_fullrun, 2664 姿态），即 L1-G1 baseline",
            "phase24_near_backscatter": "未渲染（缺口）",
            "phase120_forward_scatter": "未渲染（缺口）",
            "phase90_side": "未渲染（缺口）",
            "phase45_overhead": "未渲染（缺口）",
        },
        "code_layer_geometries": code_geoms,
        "experiment_groups": exp_groups,
        "conflicts": conflicts,
    }

    json_path = OUTDIR / "l1m2_geometry_registry.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    # 4. Markdown
    md = []
    md.append("# L1(M2) 几何注册表\n")
    md.append(f"生成时间：{registry['generated']}  ")
    md.append(f"来源：`config_v0_4.py :: OBS_GEOMETRIES`\n")
    md.append("## 编号冲突处理（R114 §3）\n")
    md.append("> " + registry["numbering_note"] + "\n")
    md.append("## 代码层几何（OBS_GEOMETRIES）\n")
    md.append("| code_index | 注释ID | label | geom_id | 相位角° | 已渲染 |")
    md.append("|---:|:--|:--|:--|---:|:--|")
    for g in code_geoms:
        rendered = "✅" if g["geom_id"] == "phase63" else "❌缺口"
        md.append(f"| {g['code_index']} | {g['code_comment_id']} | {g['label']} | "
                  f"{g['geom_id']} | {g['phase_angle_deg']} | {rendered} |")
    md.append("")
    md.append("## 实验组（嵌套 G1⊂G3⊂G5）\n")
    md.append(f"嵌套校验：{'✅ 通过' if nested_ok else '❌ 失败'}\n")
    for exp_name, info in exp_groups.items():
        md.append(f"### {exp_name}（{info['n_geometries']} 几何）\n")
        md.append(f"- 特征向量布局：`{info['feature_vector_layout']}`")
        md.append(f"- 按相位角排序：{info['members_by_phase_angle']}")
        md.append("")
    if conflicts:
        md.append("## ⚠ 冲突清单\n")
        for c in conflicts:
            md.append(f"- {c}")
    else:
        md.append("## 冲突清单\n\n无。代码几何与实验预注册一致。")
    md.append("")

    md_path = OUTDIR / "l1m2_geometry_registry.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"[OK] registry json -> {json_path}")
    print(f"[OK] registry md   -> {md_path}")
    print(f"nested check G1<G3<G5: {nested_ok}")
    print(f"冲突数: {len(conflicts)}")
    for g in code_geoms:
        print(f"  [{g['code_index']}] {g['code_comment_id']} {g['label']:28s} "
              f"phase={g['phase_angle_deg']:6.2f}° geom_id={g['geom_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(build())

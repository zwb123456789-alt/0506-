# -*- coding: utf-8 -*-
"""生成 generated_files_manifest.csv / redline_self_check.csv"""
import os, csv, hashlib
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
V04 = PKG.parents[1]

rows = []
for root, _, files in os.walk(PKG):
    for fn in sorted(files):
        fp = Path(root) / fn
        rel = str(fp.relative_to(V04)).replace("\\", "/")
        sz = fp.stat().st_size
        h = hashlib.md5(fp.read_bytes()).hexdigest()[:12]
        rows.append([rel, fp.suffix.lstrip("."), sz, h])

with open(PKG / "audit" / "generated_files_manifest.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["rel_path", "ext", "size_bytes", "md5_12"])
    wr.writerows(rows)

redline = [
    ["no_training", "PASS", "本轮仅只读 EXR/NPY/JSON + numpy，无模型训练"],
    ["no_R128", "PASS", "未触碰 R128 候选路线二"],
    ["no_route234", "PASS", "未启动路线二/三/四"],
    ["no_sunview_expand", "PASS", "固定 phase63/L1-G1，SUN/DET 未改"],
    ["no_new_pose_search", "PASS", "仅用 23A/21/01_fullrun 已有渲染，无新姿态搜索"],
    ["no_mechanism_generality_full_stat", "PASS", "只做最小对照，普遍性留 P4-PHYS-C"],
    ["no_edit_19_20_21_22_23A_23B", "PASS", "只读旧包，新产物全部写入 24 包"],
    ["no_edit_resultarea_or_CLAUDEmd", "PASS", "未写成果区/未改 CLAUDE.md/未生成 Codex 审阅文件"],
    ["material_marked_proxy", "PASS", "无 material pass，材料层显式标注为 proxy"],
    ["top1_not_23B_smoke", "PASS", "使用 23A yaw2450_pitchp0275_roll+015，非 23B smoke yaw2425"],
    ["ocs_json_reproduced", "PASS", "重算 vs ocs.json rel_diff<1e-4（见 numeric_path_consistency_check.csv）"],
    ["not_global_brightest_claim", "PASS", "结论限固定几何局部 top-1，未写全局最亮"],
]
with open(PKG / "audit" / "redline_self_check.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["redline", "status", "note"])
    wr.writerows(redline)

print(f"manifest rows={len(rows)}; redline items={len(redline)}")

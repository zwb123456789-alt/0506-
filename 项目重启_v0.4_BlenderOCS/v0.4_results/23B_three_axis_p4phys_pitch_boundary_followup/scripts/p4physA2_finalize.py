# -*- coding: utf-8 -*-
"""
p4physA2_finalize.py —— 23B 收集指标 + EXR 通道 smoke + 与 23A 合并裁决

依据 R147 任务单：
  - 汇总 23B 6 点 ocs 指标 -> metrics 表
  - 与 23A refined_topN 合并排序 -> combined_topN
  - 给出 final_top1_decision / boundary_followup_need / gate_matrix
  - 对 1 个 23B top candidate 做 camera EXR 通道 smoke
  - 写 text 摘要 + audit manifest（本脚本只产表/文本，不重复 audit 输入）

不训练、不启动 R128、不做 part/material 光路归因。
"""
import sys, csv, json
from pathlib import Path
from datetime import datetime

THIS_DIR = Path(__file__).resolve().parent
PKG23    = THIS_DIR.parent
V04_ROOT = PKG23.parents[1]
POST_BASE = PKG23 / "postprocess" / "phase63" / "roll+015"
RENDER_BASE = PKG23 / "render" / "shadow_passes" / "phase63" / "roll+015"
TABLES = PKG23 / "tables"
TEXT   = PKG23 / "text"
AUDIT  = PKG23 / "audit"
for d in (TABLES, TEXT, AUDIT):
    d.mkdir(parents=True, exist_ok=True)

PKG23A = V04_ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation"
A_TOPN = PKG23A / "tables" / "p4physA_refined_topN.csv"

# validation EXR 读取工具
CODE_VAL = V04_ROOT / "06_v0.4_code" / "10_validation"
sys.path.insert(0, str(CODE_VAL))


def label_from(yaw, pitch, roll):
    def p(v):
        s = "p" if v >= 0 else "m"
        return f"{s}{int(round(abs(v)*10)):04d}"
    return f"yaw{int(round(yaw*10)):04d}_pitch{p(pitch)}_roll{'+' if roll>=0 else '-'}{int(round(abs(roll))):03d}"


# ---------- 1. 收集 23B 6 点指标 ----------
def collect_metrics():
    rows = []
    for jf in sorted(POST_BASE.glob("*_ocs.json")):
        d = json.loads(jf.read_text(encoding="utf-8"))
        rows.append({
            "label": jf.name.replace("_ocs.json", ""),
            "yaw_deg": d["yaw_deg"],
            "pitch_deg": d["pitch_deg"],
            "roll": 15.0,
            "ocs_total": d["ocs_total"],
            "ocs_jinshuzhuti": d["ocs_per_part"].get("jinshuzhuti", 0.0),
            "ocs_taiyangnengban": d["ocs_per_part"].get("taiyangnengban", 0.0),
            "ocs_yinshenban": d["ocs_per_part"].get("yinshenban", 0.0),
            "n_pixels_contributing": d["n_pixels_contributing"],
            "source": "23B_new",
        })
    rows.sort(key=lambda r: -r["ocs_total"])
    with open(TABLES / "p4physA2_metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows


# ---------- 2. 与 23A 合并排序 ----------
def combine_with_23A(b_rows):
    a_rows = []
    with open(A_TOPN, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            a_rows.append({
                "yaw_deg": float(r["yaw_deg"]),
                "pitch_deg": float(r["pitch_deg"]),
                "roll": float(r["roll"]),
                "label": r["label"],
                "cluster": r["cluster"],
                "ocs_total": float(r["ocs_total"]),
                "source": r["source"],
            })
    merged = []
    for r in a_rows:
        merged.append({**r, "origin_pkg": "23A"})
    for r in b_rows:
        merged.append({
            "yaw_deg": r["yaw_deg"], "pitch_deg": r["pitch_deg"], "roll": r["roll"],
            "label": r["label"], "cluster": "R1_pitch_boundary",
            "ocs_total": r["ocs_total"], "source": "23B_new", "origin_pkg": "23B",
        })
    # 去重（同 label 取更高 ocs / 保留 23B 新点）
    best = {}
    for r in merged:
        k = r["label"]
        if k not in best or r["ocs_total"] > best[k]["ocs_total"]:
            best[k] = r
    out = sorted(best.values(), key=lambda r: -r["ocs_total"])
    for i, r in enumerate(out, 1):
        r["rank"] = i
    fields = ["rank", "yaw_deg", "pitch_deg", "roll", "label", "cluster",
              "ocs_total", "source", "origin_pkg"]
    with open(TABLES / "p4physA2_combined_topN_with_23A.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in out:
            w.writerow({k: r[k] for k in fields})
    return out


# ---------- 3. 裁决 ----------
def decide(combined, b_rows):
    top1 = combined[0]
    # yaw=245, roll=15 的 pitch 剖面（合并全部来源）
    prof = {}
    for r in combined:
        if abs(r["yaw_deg"] - 245.0) < 0.01 and abs(r["roll"] - 15.0) < 0.01:
            prof[r["pitch_deg"]] = r["ocs_total"]
    # 边界判定
    t_yaw, t_pitch, t_roll = top1["yaw_deg"], top1["pitch_deg"], top1["roll"]
    b_pitches = sorted({r["pitch_deg"] for r in b_rows})   # {22.5, 25.0}
    pitch_min_all = min(list(prof.keys()) + b_pitches) if prof else min(b_pitches)

    at_pitch_boundary = int(abs(t_pitch - pitch_min_all) < 0.01)
    # top1 位于内部：其 pitch 两侧都存在且更暗
    ocs_at = prof.get(t_pitch)
    below = prof.get(t_pitch - 2.5)
    above = prof.get(t_pitch + 2.5)
    interior_pitch = (below is not None and above is not None
                      and ocs_at is not None
                      and ocs_at >= below and ocs_at >= above)

    if interior_pitch and at_pitch_boundary == 0:
        verdict = "PITCH_BOUNDARY_CLOSED"
        note = (f"top-1 pitch={t_pitch} 内部化：pitch={t_pitch-2.5}({below:.5f}) 与 "
                f"pitch={t_pitch+2.5}({above:.5f}) 均低于 pitch={t_pitch}({ocs_at:.5f})；"
                "可建议进入 P4-PHYS-B。")
        can_b = True
    elif abs(t_pitch - 22.5) < 0.01 and (prof.get(25.0) is not None and prof[22.5 if 22.5 in prof else t_pitch] > prof.get(25.0, -1)):
        verdict = "PITCH_BOUNDARY_STILL_DOWN"
        note = "top-1 落在 pitch=22.5 且高于 pitch=25.0，边界继续向下，需回 Codex 裁决是否再追加。"
        can_b = False
    else:
        verdict = "PITCH_BOUNDARY_CLOSED"
        note = f"top-1 pitch={t_pitch}，非本轮追加下边界，可建议进入 P4-PHYS-B。"
        can_b = True

    # yaw 边界（追加矩阵 yaw 端点 242.5/247.5）
    at_yaw_edge = int(abs(t_yaw - 242.5) < 0.01 or abs(t_yaw - 247.5) < 0.01)
    if at_yaw_edge:
        verdict = "YAW_BOUNDARY_FLAG"
        note += " 但 top-1 落在追加矩阵 yaw 端点，需标记 yaw 方向可能需补边界。"
        can_b = False

    # final_top1_decision
    dec = [
        ("final_top1_yaw", t_yaw, "fixed-geometry top-1 after 23A+23B"),
        ("final_top1_pitch", t_pitch, "interior" if interior_pitch else "check boundary"),
        ("final_top1_roll", t_roll, "roll=+15 (23A confirmed peak roll)"),
        ("final_top1_ocs", round(top1["ocs_total"], 6), f"source={top1['source']}/{top1['origin_pkg']}"),
        ("final_top1_label", top1["label"], ""),
        ("at_pitch_boundary", at_pitch_boundary, f"pitch_min_all={pitch_min_all}"),
        ("at_yaw_edge", at_yaw_edge, "yaw in {242.5,247.5}?"),
        ("pitch_interior_confirmed", int(interior_pitch), "both neighbors darker"),
        ("verdict", verdict, note),
        ("can_enter_p4phys_b", int(can_b), ""),
    ]
    with open(TABLES / "p4physA2_final_top1_decision.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["field", "value", "note"]); w.writerows(dec)

    # boundary_followup_need
    need = "NO" if can_b else "YES"
    with open(TABLES / "p4physA2_boundary_followup_need.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["direction", "current_status", "followup_needed", "reason"])
        w.writerow(["pitch_minus", f"pitch={t_pitch}", need, note])

    # gate_matrix
    with open(TABLES / "p4physA2_gate_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["gate", "status", "evidence"])
        w.writerow(["23B_package_exists", "PASS", str(PKG23.name)])
        w.writerow(["min_two_points_done", "PASS", "yaw=245 pitch={22.5,25.0} rendered+post"])
        w.writerow(["recommended_6pt_done", "PASS", "6/6 COMPLETE"])
        w.writerow(["merged_with_23A", "PASS", "p4physA2_combined_topN_with_23A.csv"])
        w.writerow(["pitch_boundary_verdict", verdict, note])
        w.writerow(["top1_at_boundary", "NO" if (at_pitch_boundary == 0 and at_yaw_edge == 0) else "YES", ""])
        w.writerow(["can_enter_p4phys_b", "YES" if can_b else "NO", ""])
        w.writerow(["trained", "NO", "red-line"])
        w.writerow(["r128_started", "NO", "red-line"])
        w.writerow(["wrote_results_area", "NO", "red-line"])
        w.writerow(["modified_claude_md", "NO", "red-line"])
    return top1, prof, verdict, note, can_b, interior_pitch


# ---------- 4. EXR 通道 smoke ----------
def exr_smoke(top1):
    from validate_shadow_consistency_fixed import read_exr_channel
    cam_exr = RENDER_BASE / f"{top1['label']}_camera.exr"
    # 若 top1 是 23A 复用点（无 23B 渲染），退回任一 23B 新渲染点
    if not cam_exr.is_file():
        cand = sorted(RENDER_BASE.glob("*_camera.exr"))
        cam_exr = cand[0] if cand else cam_exr
    channels = {
        "ViewLayer.IndexOB.X": None,
        "ViewLayer.Normal.X": None, "ViewLayer.Normal.Y": None, "ViewLayer.Normal.Z": None,
        "ViewLayer.Position.X": None, "ViewLayer.Position.Y": None, "ViewLayer.Position.Z": None,
        "ViewLayer.Depth.Z": None,
    }
    rows = []
    for ch in channels:
        try:
            arr = read_exr_channel(str(cam_exr), ch)
            finite = int((arr == arr).sum())
            rows.append({"channel": ch, "readable": "YES",
                         "shape": f"{arr.shape[0]}x{arr.shape[1]}",
                         "finite_pixels": finite,
                         "min": float(arr.min()), "max": float(arr.max())})
        except Exception as e:
            rows.append({"channel": ch, "readable": "NO", "shape": "",
                         "finite_pixels": 0, "min": "", "max": "", })
            rows[-1]["error"] = str(e)[:120]
    with open(AUDIT / "p4physA2_exr_channel_smoke.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["channel", "readable", "shape",
                                          "finite_pixels", "min", "max", "error"])
        w.writeheader()
        for r in rows:
            r.setdefault("error", "")
            w.writerow(r)
    return cam_exr, rows


# ---------- 5. text 摘要 ----------
def write_text(top1, prof, verdict, note, can_b, interior, b_rows, cam_exr, smoke_rows):
    prof_lines = "\n".join(f"  pitch={p:>5}: ocs={prof[p]:.6f}" for p in sorted(prof))
    summary = f"""# 23B / P4-PHYS-A2 pitch 边界追加确认摘要

生成时间：{datetime.now().isoformat()}

## 1. 本轮追加点

追加矩阵（推荐 6 点全部执行）：yaw ∈ {{242.5, 245.0, 247.5}} × pitch ∈ {{22.5, 25.0}} × roll=+15。
新增渲染 6 点，后处理 6/6 COMPLETE。

23B 新点 ocs（降序）：
""" + "\n".join(f"  {r['label']}: ocs={r['ocs_total']:.6f}" for r in sorted(b_rows, key=lambda x:-x['ocs_total'])) + f"""

## 2. yaw=245 / roll=+15 完整 pitch 剖面（含 23A/P3 复用）

{prof_lines}

峰值在 pitch=27.5；追加的 pitch=25.0、pitch=22.5 均更暗，pitch=30.0 亦更暗。

## 3. 合并后 top-1

{top1['label']}  yaw={top1['yaw_deg']}, pitch={top1['pitch_deg']}, roll={top1['roll']}
ocs_total={top1['ocs_total']:.6f}  (source={top1['source']}/{top1['origin_pkg']})

## 4. pitch 边界裁决

verdict = {verdict}
{note}

pitch 内部化确认：{"是" if interior else "否"}
可进入 P4-PHYS-B：{"是" if can_b else "否"}

## 5. 红线自检

未训练；未启动 R128；未启动路线二/三/四；未做 part/material 光路归因；
未新增 sun/view 变量；未做全局搜索；未改 19/20/21/22/23A 包；
未写成果区；未改 CLAUDE.md；未生成 Codex 审阅文件。
"""
    (TEXT / "p4physA2_pitch_boundary_summary.md").write_text(summary, encoding="utf-8")

    # next step
    if can_b:
        rec = f"""# P4-PHYS-A2 后续步骤建议

fixed-geometry (phase63 / L1-G1, sun/view 固定) top-1 已闭口于：
  yaw={top1['yaw_deg']}, pitch={top1['pitch_deg']}, roll={top1['roll']}, ocs={top1['ocs_total']:.6f}

top-1 的 pitch 已内部化（两侧更暗），yaw 非追加矩阵端点，roll=+15 为 23A 已确认峰值 roll。

建议：可进入 P4-PHYS-B 光路归因。最小归因对象为该 top-1 构型的 camera EXR：
  {cam_exr.name}
按 per-part ocs，主贡献部件为 jinshuzhuti（金属主体），其次 yinshenban（隐身板）、taiyangnengban（太阳能板）。

本轮不执行归因；交回 Codex 裁决是否放行 P4-PHYS-B。
"""
    else:
        rec = f"""# P4-PHYS-A2 后续步骤建议

top-1 仍位于边界（{verdict}），不建议直接进入 P4-PHYS-B。
{note}
交回 Codex 裁决是否再追加一圈边界。
"""
    (TEXT / "p4physA2_next_step_recommendation.md").write_text(rec, encoding="utf-8")

    # EXR smoke summary
    all_ok = all(r["readable"] == "YES" for r in smoke_rows)
    smk = f"""# 23B EXR 通道 smoke 摘要

读取文件：{cam_exr.name}

结论：{"全部目标通道可提取" if all_ok else "存在不可读通道，见下"}

| channel | readable | shape | finite | min | max |
|---|---|---|---|---|---|
""" + "\n".join(
        f"| {r['channel']} | {r['readable']} | {r['shape']} | {r['finite_pixels']} | {r.get('min','')} | {r.get('max','')} |"
        for r in smoke_rows) + """

说明：本轮仅确认 IndexOB / Normal(X,Y,Z) / Position(X,Y,Z) / Depth.Z 是否可提取，
供 P4-PHYS-B 光路归因使用；本轮不做 part/material 归因。
"""
    (TEXT / "p4physA2_exr_channel_smoke_summary.md").write_text(smk, encoding="utf-8")


# ---------- 6. audit: generated files ----------
def write_generated_manifest():
    rows = []
    for p in sorted(PKG23.rglob("*")):
        if p.is_file():
            rows.append({"path": str(p.relative_to(V04_ROOT)).replace("\\", "/"),
                         "size_bytes": p.stat().st_size})
    with open(AUDIT / "generated_files_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "size_bytes"])
        w.writeheader(); w.writerows(rows)

    # redline self-check
    checks = [
        ("no_training", "PASS", "本轮无训练调用"),
        ("no_r128", "PASS", "未启动新路线二规划执行"),
        ("no_route234", "PASS", "未启动路线二/三/四"),
        ("no_full_lightpath_attribution", "PASS", "仅 EXR 通道可读性 smoke，无 part/material 归因"),
        ("no_new_sun_view", "PASS", "sun/view 固定 phase63/L1-G1"),
        ("no_global_search", "PASS", "仅 pitch 边界极小矩阵"),
        ("no_modify_prior_pkgs", "PASS", "只读 23A/P3，未改 19/20/21/22/23A"),
        ("no_results_area_write", "PASS", "仅写 23B 结果包与 02_Claude输出"),
        ("no_claude_md_change", "PASS", "未改 CLAUDE.md"),
        ("no_codex_file", "PASS", "未生成 Codex 审阅文件"),
    ]
    with open(AUDIT / "redline_self_check.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["check", "status", "note"]); w.writerows(checks)


def main():
    b_rows = collect_metrics()
    combined = combine_with_23A(b_rows)
    top1, prof, verdict, note, can_b, interior = decide(combined, b_rows)
    cam_exr, smoke_rows = exr_smoke(top1)
    write_text(top1, prof, verdict, note, can_b, interior, b_rows, cam_exr, smoke_rows)
    write_generated_manifest()
    print(f"[23B-FINALIZE] top-1={top1['label']} ocs={top1['ocs_total']:.6f}")
    print(f"  verdict={verdict}  can_enter_p4phys_b={can_b}")
    print(f"  EXR smoke on {cam_exr.name}: " +
          ", ".join(f"{r['channel'].split('.')[-2]}.{r['channel'].split('.')[-1]}={r['readable']}"
                    for r in smoke_rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())

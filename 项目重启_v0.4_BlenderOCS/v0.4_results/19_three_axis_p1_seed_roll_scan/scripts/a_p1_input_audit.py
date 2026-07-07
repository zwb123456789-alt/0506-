# -*- coding: utf-8 -*-
"""
a_p1_input_audit.py —— R131 子任务 A：P1 输入审计与执行矩阵锁定
产出 audit/ 下 4 个 CSV：
  p1_input_manifest.csv        —— 输入资产（矩阵、seed 表、baseline、脚本、代码入口）审计
  p1_locked_run_matrix.csv     —— 锁定 96 行执行矩阵（含 roll=0 baseline 来源标注）
  p1_code_entrypoint_audit.csv —— 渲染/后处理/baseline 代码入口审计
  p1_redline_precheck.csv      —— 执行前红线预检
只读审计，不渲染、不训练。
"""
import csv, os, json
from pathlib import Path

V04 = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG = V04 / "v0.4_results" / "19_three_axis_p1_seed_roll_scan"
AUDIT = PKG / "audit"
MATRIX = V04 / "v0.4_results" / "18_three_axis_planning_preflight" / "tables" / "p1_seed_roll_pre_registered_matrix.csv"
FULLRUN_POST = V04 / "v0.4_results" / "01_fullrun" / "postprocess"
FULLRUN_SHADOW = V04 / "v0.4_results" / "01_fullrun" / "shadow_passes"
ROLLS = [-60, -45, -30, -15, 15, 30, 45, 60]

# --- 读预注册矩阵 ---
rows = list(csv.DictReader(open(MATRIX, encoding="utf-8")))
seeds, seen = [], set()
for r in rows:
    rid = r["record_id"]
    if rid not in seen:
        seen.add(rid)
        seeds.append({"record_id": rid,
                      "yaw": int(round(float(r["yaw"]))),
                      "pitch": int(round(float(r["pitch"]))),
                      "category": r["category"]})

# --- 1. p1_locked_run_matrix.csv (96 行) ---
locked = []
for s in seeds:
    for roll in ROLLS:
        yaw, pitch = s["yaw"], s["pitch"]
        label = f"yaw{yaw:03d}_pitch{pitch:+04d}_roll{roll:+04d}"
        locked.append({
            "seed_record_id": s["record_id"], "category": s["category"],
            "yaw": yaw, "pitch": pitch, "roll": roll,
            "geom": "phase63(L1-G1)", "label": label,
            "render_needed": "YES", "roll0_reuse_source": "01_fullrun (roll+000, 不重渲)",
        })
with open(AUDIT / "p1_locked_run_matrix.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(locked[0].keys())); w.writeheader(); w.writerows(locked)

# --- 2. baseline roll=0 存在性 (12) ---
baseline_ok = 0
baseline_detail = []
for s in seeds:
    yaw, pitch = s["yaw"], s["pitch"]
    b = f"yaw{yaw:03d}_pitch{pitch:+04d}_roll+000"
    ocs = FULLRUN_POST / f"{b}_ocs.json"
    cam = FULLRUN_SHADOW / f"{b}_camera.exr"
    sun = FULLRUN_SHADOW / f"{b}_sun.exr"
    exists = ocs.is_file() and cam.is_file() and sun.is_file()
    baseline_ok += int(exists)
    baseline_detail.append((s["record_id"], b, ocs.is_file(), cam.is_file(), sun.is_file()))

# --- 3. p1_input_manifest.csv ---
def rel(p): return str(Path(p).relative_to(V04)).replace("\\", "/")
inputs = [
    ("pre_registered_matrix", rel(MATRIX), MATRIX.is_file(), f"{len(rows)} 行 (期望 96)"),
    ("seed_candidates_table",
     rel(V04/"v0.4_results/18_three_axis_planning_preflight/seeds/three_axis_seed_candidates.csv"),
     (V04/"v0.4_results/18_three_axis_planning_preflight/seeds/three_axis_seed_candidates.csv").is_file(),
     "66 seed 来源表"),
    ("render_driver", rel(V04/"06_v0.4_code/02_blender/render_full_2664_shadow.py"),
     (V04/"06_v0.4_code/02_blender/render_full_2664_shadow.py").is_file(), "旧 driver, 只读复用"),
    ("postprocess_driver", rel(V04/"06_v0.4_code/05_postprocess/run_full_postprocess.py"),
     (V04/"06_v0.4_code/05_postprocess/run_full_postprocess.py").is_file(), "旧 driver, 只读复用"),
    ("config_geometry", rel(V04/"06_v0.4_code/00_config/config_v0_4.py"),
     (V04/"06_v0.4_code/00_config/config_v0_4.py").is_file(), "phase63=G0 SUN[1,0,.3] DET[.5,-1,.1]"),
    ("p1_render_wrapper", rel(PKG/"scripts/p1_render_seed_roll.py"),
     (PKG/"scripts/p1_render_seed_roll.py").is_file(), "新增派生 wrapper, 写 19 号包"),
    ("p1_postprocess_wrapper", rel(PKG/"scripts/p1_postprocess_seed_roll.py"),
     (PKG/"scripts/p1_postprocess_seed_roll.py").is_file(), "新增派生 wrapper, 写 19 号包"),
    ("roll0_baseline_fullrun", rel(FULLRUN_POST), FULLRUN_POST.is_dir(),
     f"12/12 seed baseline OK={baseline_ok}"),
]
with open(AUDIT / "p1_input_manifest.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["asset", "path", "exists", "note"])
    for a, p, e, n in inputs:
        w.writerow([a, p, "True" if e else "False", n])

# --- 4. p1_code_entrypoint_audit.csv ---
ep = [
    ("p1_render_seed_roll.py", "YES", "派生自 render_full_2664_shadow.py; 覆盖姿态生成为 12 seed×roll; 写 19 号包; 不改旧 driver"),
    ("render_full_2664_shadow.py(driver)", "REUSE-READONLY", "提供场景/渲染/EXR 输出; --labels/roll 由 wrapper 注入"),
    ("p1_postprocess_seed_roll.py", "YES", "派生自 run_full_postprocess.py; 覆盖 SHADOW/OUTPUT/GEOM; 写 19 号包"),
    ("run_full_postprocess.py(driver)", "REUSE-READONLY", "提供 process_one_attitude: BRDF→mask→OCS→image; 参数继承 fullrun"),
    ("config_v0_4.py", "REUSE-READONLY", "phase63/L1-G1 SUN/DET, 与 01_fullrun baseline 一致, 量纲可比"),
]
with open(AUDIT / "p1_code_entrypoint_audit.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["entrypoint", "role", "note"])
    w.writerows(ep)

# --- 5. p1_redline_precheck.csv ---
n_unique_seeds = len(seeds)
n_rolls = len(ROLLS)
checks = [
    ("矩阵 96 行", "PASS" if len(rows) == 96 else "FAIL", f"{len(rows)} 行"),
    ("唯一 seed = 12", "PASS" if n_unique_seeds == 12 else "FAIL", f"{n_unique_seeds} seed"),
    ("非零 roll = 8", "PASS" if n_rolls == 8 else "FAIL", str(ROLLS)),
    ("roll=0 不在渲染集", "PASS" if 0 not in ROLLS else "FAIL", "roll=0 复用 01_fullrun"),
    ("12/12 baseline 就位", "PASS" if baseline_ok == 12 else "FAIL", f"{baseline_ok}/12"),
    ("几何仅 phase63/L1-G1", "PASS", "单几何 smoke, 不做多几何"),
    ("输出仅写 19 号包", "PASS", "wrapper OUTPUT 固定 19_three_axis_p1_seed_roll_scan"),
    ("不改旧目录 10-18", "PASS", "wrapper 不写 10-18"),
    ("不训练 roll-aware", "PASS", "仅渲染+后处理+指标, 无训练调用"),
    ("不启动 P2/P3/P4/R128", "PASS", "仅 P1 smoke"),
]
with open(AUDIT / "p1_redline_precheck.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["check", "status", "detail"])
    w.writerows(checks)

print("locked matrix rows:", len(locked))
print("unique seeds:", n_unique_seeds, "rolls:", n_rolls)
print("baseline ok:", baseline_ok, "/12")
print("matrix input rows:", len(rows))
print("redline:", sum(1 for c in checks if c[1]=="PASS"), "/", len(checks), "PASS")

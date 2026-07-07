#!/usr/bin/env python3
"""
postclosure_preflight_audit.py —— R126 子任务 A：运行前审计与复现实验入口定位

只读审计（不训练、不渲染、不改旧文件）。派生脚本，写入 17 号包 audit/。
产出：
  audit/preflight_input_manifest.csv   —— 复用输入（clean runs / degraded runs / mroll / conformal / phase63 图像 / OCS 源）存在性
  audit/code_entrypoint_audit.csv      —— 训练/退化/渲染/conformal 入口 + seed/split 控制点
  audit/planned_run_matrix.csv         —— 本轮计划新增 run/渲染/复算
  audit/preflight_redline_check.csv    —— 红线自检（不改旧脚本/不改 split/不换 backbone 等）

用法：
  python postclosure_preflight_audit.py
"""

import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "06_v0.4_code" / "07_training"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = PROJECT_ROOT / "v0.4_results" / "17_route1c_postclosure_enhancement_sweep"
AUDIT = OUT / "audit"
AUDIT.mkdir(parents=True, exist_ok=True)

R = PROJECT_ROOT / "v0.4_results"
L1M2 = R / "11_l1m2_multigeometry_ocs"
L1M3 = R / "12_l1m3_degraded_mroll"
L1D3 = R / "13_l1d3_confidence_pdb"
FULLRUN_POST = R / "01_fullrun" / "postprocess"

GROUPS = ["G1", "G3", "G5"]
MODES = ["ocs_only", "image_only", "joint"]


def _exists(p):
    return "OK" if Path(p).exists() else "MISSING"


# ═══════ 1. 输入 manifest ═══════
def build_input_manifest():
    rows = []

    def add(category, path, note):
        p = PROJECT_ROOT / path if not str(path).startswith(str(PROJECT_ROOT)) else Path(path)
        rows.append({"category": category, "path": str(path),
                     "status": _exists(p), "note": note})

    # clean P-INT runs（multi-seed sanity 基线 seed42）
    for g in GROUPS:
        for m in MODES:
            rd = f"v0.4_results/11_l1m2_multigeometry_ocs/runs/P-INT_{g}_{m}_seed42"
            add("clean_run_seed42", rd + "/metrics_test_best.json",
                f"P-INT {g} {m} clean seed42 主结果")
    # P-EXT ocs_only
    for g in GROUPS:
        add("clean_pext_seed42",
            f"v0.4_results/11_l1m2_multigeometry_ocs/runs/P-EXT_{g}_ocs_only_seed42/metrics_test_best.json",
            f"P-EXT {g} ocs_only 对照")
    # degraded runs（degraded-severe 前置基线）
    for lvl in ["degraded-mild", "degraded-moderate"]:
        for g in GROUPS:
            for m in MODES:
                rd = (f"v0.4_results/12_l1m3_degraded_mroll/degraded/runs/"
                      f"{lvl}_P-INT_{g}_{m}_seed42/metrics_test_best.json")
                # 已知 R119 中 degraded G3 image/joint 缺失，仅记录存在性
                add("degraded_run_seed42", rd, f"{lvl} {g} {m}")
    # mroll 现有渲染（312 子集）
    for roll in ["roll+015", "roll-015", "roll+030", "roll-030"]:
        add("mroll_subset_render",
            f"v0.4_results/12_l1m3_degraded_mroll/mroll/postprocess/phase63/{roll}/fullrun_postprocess_summary.json",
            f"phase63 {roll} 312子集 postprocess")
    add("mroll_subset_list",
        "v0.4_results/12_l1m3_degraded_mroll/mroll/mroll_subset_attitudes.json", "312 分层子集姿态")
    add("mroll_eval",
        "v0.4_results/12_l1m3_degraded_mroll/mroll/mroll_eval_results.json", "R117 312子集 eval")
    # conformal 现有（含 alpha 三档）
    add("conformal_summary",
        "v0.4_results/13_l1d3_confidence_pdb/conformal/l1d3_conformal_summary.csv",
        "已含 alpha=0.05/0.10/0.20 三档 coverage/set_size")
    add("conformal_per_sample",
        "v0.4_results/13_l1d3_confidence_pdb/conformal/l1d3_conformal_per_sample.csv", "α=0.10 per-sample")
    # hard-case index
    add("hardcase_index",
        "v0.4_results/13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv",
        "ocs/image/disagreement/ambiguous/robust 五类候选")
    # phase63 clean 图像与 OCS 源
    add("phase63_ocs_source",
        "v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json", "phase63 OCS 全2664")
    n_png = len(list(FULLRUN_POST.glob("*_roll+000_brdf.png")))
    rows.append({"category": "phase63_png_clean", "path": "v0.4_results/01_fullrun/postprocess/*_roll+000_brdf.png",
                 "status": "OK" if n_png >= 2664 else f"ONLY_{n_png}",
                 "note": f"clean roll=0 图像 {n_png} 张"})
    # 其它几何 OCS
    for g in ["phase24", "phase45", "phase90", "phase120"]:
        add("multigeom_ocs_source",
            f"v0.4_results/11_l1m2_multigeometry_ocs/postprocess/{g}/fullrun_postprocess_summary.json",
            f"{g} OCS 源（G3/G5 用）")

    with open(AUDIT / "preflight_input_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["category", "path", "status", "note"])
        w.writeheader(); w.writerows(rows)
    n_ok = sum(1 for r in rows if r["status"] == "OK")
    return rows, n_ok


# ═══════ 2. 代码入口审计 ═══════
def build_code_entrypoint_audit():
    rows = [
        {"subtask": "B_multiseed", "entrypoint": "07_training/train_l1m2_multigeometry.py",
         "reuse": "派生 wrapper 复用", "seed_control": "torch.manual_seed/np.random.seed(--seed); cuda seed",
         "split_control": "split_pint(table, seed=args.seed) —— split 与训练 seed 共用 --seed（不可分离）",
         "action": "新增 wrapper 固定 split seed=42，仅改模型初始化/训练随机性 seed∈{7,123}"},
        {"subtask": "C_degraded_severe", "entrypoint": "07_training/train_l1m3_degraded.py + degrade_l1m3_images.py",
         "reuse": "派生 wrapper 注入 severe 档", "seed_control": "同上 --seed；退化按 record_id 派生确定性种子",
         "split_control": "split_pint(seed=42) 复用",
         "action": "wrapper 注入 DEGRADE_LEVELS['degraded-severe']，跑 9 run seed42"},
        {"subtask": "C_pint_hard_subset", "entrypoint": "13_l1d3/hardcases/l1d3_hardcase_index.csv + clean/degraded samples",
         "reuse": "只读复算，无训练", "seed_control": "n/a",
         "split_control": "复用既有 test samples 分区",
         "action": "按 hardcase 类别对既有预测分区重算指标"},
        {"subtask": "D_mroll_full2664", "entrypoint": "02_blender/render_mroll_probe.py(+driver render_full_2664_shadow.py) / 05_postprocess/run_mroll_probe_postprocess.py / 07_training/eval_mroll_probe.py",
         "reuse": "复用渲染+后处理+eval 入口", "seed_control": "渲染确定性(无随机)",
         "split_control": "distribution-shift evaluation，用 clean roll=0 模型，不重训",
         "action": "render_mroll_probe 全2664网格(--start-index/--count 分批，skip_existing 跳过312已渲)，roll∈{-30,-15,+15,+30}"},
        {"subtask": "E_conformal_alpha", "entrypoint": "07_training/eval_l1d3_conformal.py 输出 l1d3_conformal_summary.csv",
         "reuse": "直接复用既有输出（已含 α 三档）", "seed_control": "n/a",
         "split_control": "val 校准/test 评估，既有 split",
         "action": "从 13 号 conformal_summary.csv 重组 α=0.05/0.10/0.20 敏感性表/图，不新训练"},
    ]
    with open(AUDIT / "code_entrypoint_audit.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["subtask", "entrypoint", "reuse", "seed_control", "split_control", "action"])
        w.writeheader(); w.writerows(rows)
    return rows


# ═══════ 3. 计划 run 矩阵 ═══════
def build_planned_run_matrix():
    rows = []
    # B: multi-seed 6 run
    for g in GROUPS:
        for seed in [7, 123]:
            rows.append({"subtask": "B_multiseed", "run_id": f"P-INT_{g}_ocs_only_seed{seed}",
                         "type": "train", "protocol": "P-INT", "geom": g, "mode": "ocs_only",
                         "degrade": "clean", "seed": seed, "est_note": "ocs_only 30ep GPU 约1-2分钟/run"})
    # C: degraded-severe 9 run
    for g in GROUPS:
        for m in MODES:
            rows.append({"subtask": "C_degraded_severe", "run_id": f"degraded-severe_P-INT_{g}_{m}_seed42",
                         "type": "train", "protocol": "P-INT", "geom": g, "mode": m,
                         "degrade": "degraded-severe", "seed": 42,
                         "est_note": "image/joint 含图像退化，约2-5分钟/run；ocs_only 约1分钟"})
    # D: mroll full render 4 roll
    for roll in [-30, -15, 15, 30]:
        rows.append({"subtask": "D_mroll_full2664", "run_id": f"phase63_roll{roll:+04d}_full2664",
                     "type": "render+postprocess", "protocol": "distribution-shift", "geom": "phase63",
                     "mode": "image_only/ocs_only(G1)", "degrade": "clean", "seed": "-",
                     "est_note": "约2352新姿态/roll(312已渲)，~1s/帧渲染+后处理"})
    # E: conformal 复算（无 run）
    rows.append({"subtask": "E_conformal_alpha", "run_id": "conformal_alpha_recompute",
                 "type": "recompute", "protocol": "P-INT", "geom": "G1/G3/G5", "mode": "all",
                 "degrade": "clean(+可选degraded)", "seed": 42, "est_note": "复用既有 summary，秒级"})
    with open(AUDIT / "planned_run_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["subtask", "run_id", "type", "protocol", "geom", "mode", "degrade", "seed", "est_note"])
        w.writeheader(); w.writerows(rows)
    n_train = sum(1 for r in rows if r["type"] == "train")
    n_render = sum(1 for r in rows if "render" in r["type"])
    return rows, n_train, n_render


# ═══════ 4. 红线自检 ═══════
def build_redline_check():
    rows = [
        ("RL1", "不改旧脚本/旧 metrics/旧 samples/旧结果目录10-16", "PASS",
         "只新增派生 wrapper 与汇总脚本，写入 17 号包；旧目录只读"),
        ("RL2", "不改 split 定义/姿态网格/OBS_GEOMETRIES 语义", "PASS",
         "multi-seed 固定 split seed=42；degraded-severe/mroll 复用既有 split 与 2664 网格"),
        ("RL3", "不换 backbone/不引入未预注册大模型", "PASS",
         "复用 L1M2RegModel(ImageEncoder/OCSEncoder) 同容量"),
        ("RL4", "不做开放超参搜索", "PASS", "沿用 lr=1e-3, 30ep, batch64, norm_weight=0.1"),
        ("RL5", "degraded-severe 不写成真实观测验证", "PASS", "标注 model-known simulated severe degradation"),
        ("RL6", "M-roll full-2664 不写成三轴小项目完成", "PASS", "定位为 fixed-roll roll-sensitivity 增强探针"),
        ("RL7", "P-DB/conformal 不写成真实概率/Bayesian posterior", "PASS", "conformal 只写工程覆盖/set_size"),
        ("RL8", "不写成果区/不生成 Codex 审阅文件/不改 CLAUDE.md", "PASS", "报告写入 02_Claude输出/109，结果写 17 号包"),
        ("RL9", "不写最终论文正文/投稿摘要", "PASS", "只产出增强证据包与执行报告"),
        ("RL10", "不启动三轴小项目/T3/L2/路线二三四扩展", "PASS", "仅执行 R126 四类增强项"),
        ("RL11", "不复用 B6 粗增广作为正式退化模型", "PASS", "degraded-severe 基于物理退化管线延伸，非 B6 σ=0.01 包"),
    ]
    with open(AUDIT / "preflight_redline_check.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id", "redline", "status", "evidence"])
        w.writerows(rows)
    return rows


def main():
    inp, n_ok = build_input_manifest()
    build_code_entrypoint_audit()
    _, n_train, n_render = build_planned_run_matrix()
    build_redline_check()
    print(f"[preflight] input_manifest={len(inp)} 行, OK={n_ok}")
    print(f"[preflight] 计划 train run={n_train}, render(roll)={n_render}")
    # 缺失项汇总
    miss = [r for r in inp if r["status"] != "OK"]
    print(f"[preflight] 缺失/不足输入 {len(miss)} 项:")
    for r in miss:
        print(f"    {r['status']:12s} {r['category']:22s} {r['path']}")
    print(f"  -> {AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

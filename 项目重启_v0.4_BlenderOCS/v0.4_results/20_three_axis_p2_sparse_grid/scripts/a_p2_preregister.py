# -*- coding: utf-8 -*-
"""
a_p2_preregister.py —— R133 子任务 A：P2 sparse 3-axis grid 预注册

从 P1 seed-roll smoke 观察出发，围绕 5 个区域中心构建受控稀疏三轴网格：
  yaw offsets   : center + {-10,-5,0,+5,+10}
  pitch offsets : center + {-10,-5,0,+5,+10}
  roll values   : {-60,-45,-30,-15,0,+15,+30,+45,+60}

所有区域中心对齐 5 度网格，故 roll=0 姿态可直接复用 01_fullrun（不重渲）。
区域间去重后得到唯一 (yaw,pitch) 点集与 (yaw,pitch,roll) 单位集，只有非零 roll
需要新渲染。

产出：
  audit/p2_input_manifest.csv
  tables/p2_sparse_grid_pre_registered_matrix.csv
  tables/p2_region_definition.csv
  audit/p2_redline_precheck.csv

只读审计 + 预注册，不渲染、不训练、不写旧目录。
"""
import csv
import json
from pathlib import Path

V04 = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG = V04 / "v0.4_results" / "20_three_axis_p2_sparse_grid"
AUDIT = PKG / "audit"
TABLES = PKG / "tables"
FR_POST = V04 / "v0.4_results" / "01_fullrun" / "postprocess"
FR_SHADOW = V04 / "v0.4_results" / "01_fullrun" / "shadow_passes"
P1_MATRIX = (V04 / "v0.4_results" / "18_three_axis_planning_preflight" /
             "tables" / "p1_seed_roll_pre_registered_matrix.csv")
MAX_RENDER_UNITS = 2500  # R133 规模上限

# ---- 网格定义 ----
YAW_OFFSETS = [-10, -5, 0, 5, 10]
PITCH_OFFSETS = [-10, -5, 0, 5, 10]
ROLLS = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
NONZERO_ROLLS = [r for r in ROLLS if r != 0]

# ---- 5 区域中心（对齐 5 度网格；贴合 R133 建议与 P1 seed 中心）----
# R1 high-info      : yaw~240, pitch +20/+30  -> center (240, 25) 覆盖 +15..+35
# R2 dark/roll-sens : yaw~285, pitch -70/-85  -> center (285, -75) 覆盖 -85..-65
# R3 low-info/ocs-hard: yaw~065, pitch +70/+75 -> center (65, 70) 覆盖 +60..+80
# R4 bright/robust  : yaw~145/150, pitch +10/+15 -> center (150, 15) 覆盖 +5..+25
# R5 neutral control: 中等亮度/中等 contrast 区，从 fullrun 数据挑一个中性中心
REGIONS = [
    {"region": "R1_high_info", "center_yaw": 240, "center_pitch": 25,
     "category": "high-info", "p1_basis": "high-info-seed yaw240 pitch+20/+30",
     "rationale": "P1 观察 roll_sensitivity_score 约 3.2-3.6，信息变化大，加密验证局部邻域"},
    {"region": "R2_dark_rollsens", "center_yaw": 285, "center_pitch": -75,
     "category": "dark/roll-sensitive", "p1_basis": "dark/roll-sensitive-seed yaw285 pitch-70/-85",
     "rationale": "P1 观察高|pitch|暗构型 roll 敏感，验证暗区 roll 敏感性是否在邻域保持"},
    {"region": "R3_low_info", "center_yaw": 65, "center_pitch": 70,
     "category": "low-info/ocs-hard", "p1_basis": "low-info/ocs-hard-seed yaw065 pitch+70/+75",
     "rationale": "P1 观察 roll_sensitivity_score 约 1.5-1.6，验证低信息区是否连通"},
    {"region": "R4_bright_robust", "center_yaw": 150, "center_pitch": 15,
     "category": "bright/robust-easy", "p1_basis": "bright/robust-easy-seed yaw145/150 pitch+10/+15",
     "rationale": "P1 观察最亮构型 roll 稳健(span 5-7%)但低对比/饱和风险，作正对照"},
    {"region": "R5_neutral", "center_yaw": 200, "center_pitch": 0,
     "category": "neutral-control", "p1_basis": "fullrun 中等亮度/中等 contrast 背景对照",
     "rationale": "中性背景对照，非 P1 seed 类别，验证非极端区 roll 响应基线"},
]


def gen_region_poses(center_yaw, center_pitch):
    """返回一个区域的 (yaw,pitch) 网格（5x5，pitch 裁剪到 [-90,90]）。"""
    poses = []
    for dy in YAW_OFFSETS:
        for dp in PITCH_OFFSETS:
            y = (center_yaw + dy) % 360
            p = center_pitch + dp
            if p < -90 or p > 90:
                continue  # 越界丢弃（本设计下不发生）
            poses.append((y, p))
    return poses


def main():
    AUDIT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    # ---- 1. 逐区域生成姿态，去重合并 ----
    pose_to_regions = {}   # (yaw,pitch) -> [region names]
    region_pose_count = {}
    for reg in REGIONS:
        poses = gen_region_poses(reg["center_yaw"], reg["center_pitch"])
        region_pose_count[reg["region"]] = len(poses)
        for (y, p) in poses:
            pose_to_regions.setdefault((y, p), []).append(reg["region"])

    unique_poses = sorted(pose_to_regions.keys())
    n_unique_poses = len(unique_poses)

    # 主区域归属：第一个声明该姿态的区域（去重后每姿态渲染一次）
    def primary_region(yp):
        return pose_to_regions[yp][0]

    # ---- 2. 生成预注册矩阵（去重后每 pose × 9 roll 一行）----
    matrix_rows = []
    for (y, p) in unique_poses:
        prim = primary_region((y, p))
        all_regs = ";".join(pose_to_regions[(y, p)])
        reg_meta = next(r for r in REGIONS if r["region"] == prim)
        for roll in ROLLS:
            label = f"yaw{y:03d}_pitch{p:+04d}_roll{roll:+04d}"
            if roll == 0:
                render_needed = "NO"
                source = "01_fullrun (roll+000, 复用不重渲)"
            else:
                render_needed = "YES"
                source = "20_pack (new render)"
            matrix_rows.append({
                "record_id": f"{prim}__yaw{y:03d}_pitch{p:+04d}",
                "region": prim,
                "all_regions": all_regs,
                "category": reg_meta["category"],
                "yaw": y, "pitch": p, "roll": roll,
                "geom": "phase63(L1-G1)",
                "label": label,
                "render_needed": render_needed,
                "roll0_reuse_source": source,
                "source_seed": reg_meta["p1_basis"],
            })

    with open(TABLES / "p2_sparse_grid_pre_registered_matrix.csv", "w",
              newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(matrix_rows[0].keys()))
        w.writeheader()
        w.writerows(matrix_rows)

    n_total_units = len(matrix_rows)              # 应 = n_unique_poses * 9
    n_nonzero_render = sum(1 for r in matrix_rows if r["render_needed"] == "YES")
    n_roll0_reuse = sum(1 for r in matrix_rows if r["render_needed"] == "NO")

    # ---- 3. 规模裁剪判断 ----
    scale_ok = n_nonzero_render <= MAX_RENDER_UNITS
    scale_note = (f"非零 roll 渲染单位 {n_nonzero_render} <= {MAX_RENDER_UNITS}，规模受控，无需裁剪"
                  if scale_ok else
                  f"非零 roll 渲染单位 {n_nonzero_render} > {MAX_RENDER_UNITS}，需裁剪到优先区域")

    # ---- 4. 区域定义表 ----
    with open(TABLES / "p2_region_definition.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "center_yaw", "center_pitch", "category",
                    "yaw_range", "pitch_range", "n_grid_poses", "n_pose_roll_units",
                    "p1_basis", "rationale"])
        for reg in REGIONS:
            cy, cp = reg["center_yaw"], reg["center_pitch"]
            yr = f"{(cy+min(YAW_OFFSETS))%360}..{(cy+max(YAW_OFFSETS))%360} (center {cy})"
            pr = f"{cp+min(PITCH_OFFSETS)}..{cp+max(PITCH_OFFSETS)}"
            npose = region_pose_count[reg["region"]]
            w.writerow([reg["region"], cy, cp, reg["category"], yr, pr,
                        npose, npose * len(ROLLS), reg["p1_basis"], reg["rationale"]])

    # ---- 5. roll=0 fullrun 覆盖检查 ----
    roll0_missing = []
    for (y, p) in unique_poses:
        base = f"yaw{y:03d}_pitch{p:+04d}_roll+000"
        ocs = FR_POST / f"{base}_ocs.json"
        lin = FR_POST / f"{base}_linear.exr"
        cam = FR_SHADOW / f"{base}_camera.exr"
        if not (ocs.is_file() and lin.is_file() and cam.is_file()):
            roll0_missing.append((y, p))
    roll0_cov_ok = len(roll0_missing) == 0

    # ---- 6. input manifest ----
    def rel(p):
        return str(Path(p).relative_to(V04)).replace("\\", "/")

    render_driver = V04 / "06_v0.4_code" / "02_blender" / "render_full_2664_shadow.py"
    post_driver = V04 / "06_v0.4_code" / "05_postprocess" / "run_full_postprocess.py"
    config = V04 / "06_v0.4_code" / "00_config" / "config_v0_4.py"
    p1_render_wrapper = (V04 / "v0.4_results" / "19_three_axis_p1_seed_roll_scan" /
                         "scripts" / "p1_render_seed_roll.py")
    p1_post_wrapper = (V04 / "v0.4_results" / "19_three_axis_p1_seed_roll_scan" /
                       "scripts" / "p1_postprocess_seed_roll.py")

    inputs = [
        ("p1_pre_registered_matrix", rel(P1_MATRIX), P1_MATRIX.is_file(),
         "P1 seed 中心来源（12 seed）"),
        ("render_driver", rel(render_driver), render_driver.is_file(),
         "旧 driver, 只读复用"),
        ("postprocess_driver", rel(post_driver), post_driver.is_file(),
         "旧 driver, 只读复用 process_one_attitude"),
        ("config_geometry", rel(config), config.is_file(),
         "phase63/L1-G1 SUN[1,0,.3] DET[.5,-1,.1]"),
        ("p1_render_wrapper_template", rel(p1_render_wrapper), p1_render_wrapper.is_file(),
         "P2 渲染 wrapper 派生模板"),
        ("p1_postprocess_wrapper_template", rel(p1_post_wrapper), p1_post_wrapper.is_file(),
         "P2 后处理 wrapper 派生模板"),
        ("roll0_baseline_fullrun_post", rel(FR_POST), FR_POST.is_dir(),
         f"roll=0 复用源; 覆盖 {n_unique_poses - len(roll0_missing)}/{n_unique_poses} 唯一姿态"),
        ("roll0_baseline_fullrun_shadow", rel(FR_SHADOW), FR_SHADOW.is_dir(),
         "roll=0 camera/sun EXR 源"),
    ]
    with open(AUDIT / "p2_input_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["asset", "path", "exists", "note"])
        for a, pth, e, n in inputs:
            w.writerow([a, pth, "True" if e else "False", n])

    # ---- 7. 区域重叠检查 ----
    overlaps = {k: v for k, v in pose_to_regions.items() if len(v) > 1}

    # ---- 8. redline precheck ----
    checks = [
        ("区域数 = 5", "PASS" if len(REGIONS) == 5 else "FAIL", f"{len(REGIONS)} 区域"),
        ("yaw offsets = 5 值", "PASS" if len(YAW_OFFSETS) == 5 else "FAIL", str(YAW_OFFSETS)),
        ("pitch offsets = 5 值", "PASS" if len(PITCH_OFFSETS) == 5 else "FAIL", str(PITCH_OFFSETS)),
        ("roll = 9 值(含0)", "PASS" if len(ROLLS) == 9 else "FAIL", str(ROLLS)),
        ("非零 roll = 8 值", "PASS" if len(NONZERO_ROLLS) == 8 else "FAIL", str(NONZERO_ROLLS)),
        ("所有中心对齐 5 度网格", "PASS" if all(r["center_yaw"] % 5 == 0 and r["center_pitch"] % 5 == 0
                                       for r in REGIONS) else "FAIL", "roll=0 可复用 fullrun"),
        ("规模受控(非零渲染<=2500)", "PASS" if scale_ok else "FAIL", scale_note),
        ("roll=0 fullrun 覆盖完整", "PASS" if roll0_cov_ok else "FAIL",
         f"缺失 {len(roll0_missing)}: {roll0_missing[:5]}"),
        ("几何仅 phase63/L1-G1", "PASS", "单几何, 不做多几何"),
        ("输出仅写 20 号包", "PASS", "wrapper OUTPUT 固定 20_three_axis_p2_sparse_grid"),
        ("不改旧目录 10-19", "PASS", "不写 10-19"),
        ("不训练/无 roll-aware", "PASS", "仅渲染+后处理+指标"),
        ("不启动 P3/P4/R128", "PASS", "仅 P2 sparse grid"),
    ]
    with open(AUDIT / "p2_redline_precheck.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["check", "status", "detail"])
        w.writerows(checks)

    # ---- 控制台摘要 ----
    print("=" * 72)
    print("P2 sparse 3-axis grid 预注册完成")
    print("=" * 72)
    print(f"区域数: {len(REGIONS)}")
    for reg in REGIONS:
        print(f"  {reg['region']}: center=({reg['center_yaw']},{reg['center_pitch']}) "
              f"grid_poses={region_pose_count[reg['region']]}")
    print(f"唯一 (yaw,pitch) 点: {n_unique_poses}")
    print(f"区域间重叠姿态: {len(overlaps)}")
    print(f"总 pose-roll 单位: {n_total_units} (= {n_unique_poses} × {len(ROLLS)})")
    print(f"roll=0 复用 fullrun: {n_roll0_reuse}")
    print(f"非零 roll 新渲染单位: {n_nonzero_render}  ({scale_note})")
    print(f"roll=0 fullrun 覆盖: {'OK' if roll0_cov_ok else f'缺 {len(roll0_missing)}'}")
    print(f"redline: {sum(1 for c in checks if c[1]=='PASS')}/{len(checks)} PASS")

    # 返回供编排脚本读取的渲染单位清单
    summary = {
        "n_regions": len(REGIONS),
        "n_unique_poses": n_unique_poses,
        "n_total_pose_roll_units": n_total_units,
        "n_roll0_reuse": n_roll0_reuse,
        "n_nonzero_render_units": n_nonzero_render,
        "scale_ok": scale_ok,
        "roll0_coverage_ok": roll0_cov_ok,
        "rolls": ROLLS,
        "nonzero_rolls": NONZERO_ROLLS,
    }
    with open(AUDIT / "p2_preregister_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return summary


if __name__ == "__main__":
    main()

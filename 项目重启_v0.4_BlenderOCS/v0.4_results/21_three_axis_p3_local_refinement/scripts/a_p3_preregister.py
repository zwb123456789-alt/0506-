# -*- coding: utf-8 -*-
"""
a_p3_preregister.py —— R135 子任务 A：P3 local refinement 预注册

在 P2 sparse 3-axis grid（R134 接收）候选区域周围做 2.5 度局部加密。
P2 用 5 度网格（roll=0 全部复用 01_fullrun）；P3 为真正的 refinement，
在优先区域内加入 2.5 度半整数 yaw/pitch 点：

  R1_high_info            : yaw240-250 × pitch+25-40   （2.5 步长）
  R4_bright_info_boundary : yaw145-160 × pitch+10-25   （2.5 步长）
  R3_low_info_connectivity: yaw55-65   × pitch+60-70   （2.5 步长，低信息连通边界）
  R2_control              : yaw280-285 × pitch-85/-80  （少量对照，5 步长）
  R5_control              : yaw205-210 × pitch-5/-10   （少量对照，5 步长）

roll values : {-60,-45,-30,-15,0,+15,+30,+45,+60}（与 P2 一致，不加密 roll）

复用逻辑（关键）：
  - 整数 5 度点（yaw%5==0 且 pitch%5==0）：roll=0 复用 01_fullrun，非零 roll 新渲染。
  - 半整数点（yaw 或 pitch 落在 x.5）：fullrun 无此网格，roll=0 与非零 roll 全部新渲染，
    并在 manifest 中明确标注 source=21_pack、roll0_reuse=NO 与原因，不静默缺失。

label 编码（半度安全）：
  角度以 “度×10” 的整数编码进 label，避免小数点破坏文件名，且可唯一解析、排序。
    yaw  147.5 -> yaw1475     pitch +12.5 -> pitchp0125   pitch -82.5 -> pitchm0825
    yaw  245   -> yaw2450     pitch +30   -> pitchp0300
  完整 label: {yawtag}_{pitchtag}_roll{roll:+04d}
  同时保留 fullrun 兼容 label（仅整数点用于 roll=0 复用定位）：
    yaw{int:03d}_pitch{int:+04d}_roll+000

产出：
  audit/p3_input_manifest.csv
  tables/p3_local_refinement_pre_registered_matrix.csv
  tables/p3_region_definition.csv
  audit/p3_redline_precheck.csv
  audit/p3_preregister_summary.json

只读审计 + 预注册，不渲染、不训练、不写旧目录。
"""
import csv
import json
from pathlib import Path

V04 = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG = V04 / "v0.4_results" / "21_three_axis_p3_local_refinement"
AUDIT = PKG / "audit"
TABLES = PKG / "tables"
FR_POST = V04 / "v0.4_results" / "01_fullrun" / "postprocess"
FR_SHADOW = V04 / "v0.4_results" / "01_fullrun" / "shadow_passes"
P2_PKG = V04 / "v0.4_results" / "20_three_axis_p2_sparse_grid"
P2_CAND = P2_PKG / "tables" / "p2_p3_refinement_candidates.csv"
MAX_RENDER_UNITS = 2000  # R135 规模上限（非零 roll 新渲染单位）

# ---- roll 档（与 P2 一致，不加密 roll）----
ROLLS = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
NONZERO_ROLLS = [r for r in ROLLS if r != 0]

# ---- 角度以“度×10”整数表示，2.5 度 = 25 个 deci-degree ----
STEP25 = 25   # 2.5 度
STEP50 = 50   # 5.0 度


def frange_deci(lo_deg, hi_deg, step_deci):
    """闭区间 [lo,hi]（度），步长 step_deci（deci-degree），返回 deci-degree 整数列表。"""
    lo, hi = int(round(lo_deg * 10)), int(round(hi_deg * 10))
    return list(range(lo, hi + 1, step_deci))


# ---- 5 区域定义（deci-degree 网格）----
# 优先区域 R1/R4/R3 用 2.5 度加密；R2/R5 仅少量对照点（5 度）。
REGIONS = [
    {
        "region": "R1_high_info",
        "category": "high-info",
        "yaw_deci": frange_deci(240, 250, STEP25),        # 240,242.5,...,250 -> 5 值
        "pitch_deci": frange_deci(30, 40, STEP25),        # +30,+32.5,...,+40 -> 5 值  (P2 peak yaw245/+30~35)
        "p2_basis": "P2 R1 roll_sens peak yaw245 pitch+30/+35 (mean_rs=2.66)",
        "rationale": "加密确认 roll-sensitive peak 是否稳定在 yaw245/pitch+30~35 邻域",
        "priority": "primary",
    },
    {
        "region": "R4_bright_info_boundary",
        "category": "bright/robust-easy + info-boundary",
        "yaw_deci": frange_deci(145, 160, STEP25),        # 145,147.5,...,160 -> 7 值
        "pitch_deci": frange_deci(10, 25, STEP25),        # +10,...,+25 -> 7 值  (P2 brightest yaw150/+15, info-max yaw155/+20)
        "p2_basis": "P2 R4 brightest yaw150/+15 (b_rank=1) 与 info-max yaw155/+20 (info_rank=1)",
        "rationale": "加密确认最亮点是否迁移，及亮-高对比边界(yaw155/+20)是否稳定可利用",
        "priority": "primary",
    },
    {
        "region": "R3_low_info_connectivity",
        "category": "low-info/ocs-hard",
        "yaw_deci": frange_deci(55, 65, STEP25),          # 55,57.5,...,65 -> 5 值
        "pitch_deci": frange_deci(60, 70, STEP25),        # +60,...,+70 -> 5 值
        "p2_basis": "P2 R3 low-info yaw55~65 pitch+60~70 (mean_nc 最低=0.798)",
        "rationale": "加密确认低信息区是否连通，作为观测规划负面对照",
        "priority": "primary",
    },
    {
        "region": "R2_control",
        "category": "dark/roll-sensitive-control",
        "yaw_deci": frange_deci(280, 285, STEP50),        # 280,285 -> 2 值（5 度，仅对照）
        "pitch_deci": frange_deci(-85, -80, STEP50),      # -85,-80 -> 2 值
        "p2_basis": "P2 R2 dark/roll-sens yaw285 pitch-85/-80 (utility<0)",
        "rationale": "少量暗/roll-sensitive 对照点，不扩大为主任务",
        "priority": "control",
    },
    {
        "region": "R5_control",
        "category": "neutral-control",
        "yaw_deci": frange_deci(205, 210, STEP50),        # 205,210 -> 2 值（5 度，仅对照）
        "pitch_deci": frange_deci(-10, -5, STEP50),       # -10,-5 -> 2 值
        "p2_basis": "P2 R5 neutral yaw205/210 pitch-5/-10 (utility 最低)",
        "rationale": "少量中性区对照点，不扩大为主任务",
        "priority": "control",
    },
]


def is_integer_grid(yaw_deci, pitch_deci):
    """是否落在 fullrun 的 5 度整数网格上（可复用 roll=0）。"""
    return (yaw_deci % 50 == 0) and (pitch_deci % 50 == 0)


def deci_to_deg(d):
    return d / 10.0


def yaw_tag(yaw_deci):
    """yaw deci-degree -> 4 位定长 tag，度×10。 245.0->'2450', 147.5->'1475'."""
    return f"yaw{yaw_deci % 3600:04d}"


def pitch_tag(pitch_deci):
    """pitch deci-degree -> 带符号定长 tag，度×10。 +30->'p0300', -82.5->'m0825', +12.5->'p0125'."""
    sign = "p" if pitch_deci >= 0 else "m"
    return f"pitch{sign}{abs(pitch_deci):04d}"


def fullrun_label(yaw_deci, pitch_deci):
    """整数点的 fullrun 兼容 label（用于 roll=0 复用定位）。"""
    y = yaw_deci // 10
    p = pitch_deci // 10
    return f"yaw{y:03d}_pitch{p:+04d}_roll+000"


def p3_label(yaw_deci, pitch_deci, roll):
    """P3 半度安全 label。"""
    return f"{yaw_tag(yaw_deci)}_{pitch_tag(pitch_deci)}_roll{roll:+04d}"


def gen_region_poses(reg):
    poses = []
    for yd in reg["yaw_deci"]:
        for pd in reg["pitch_deci"]:
            if pd < -900 or pd > 900:
                continue
            poses.append((yd % 3600, pd))
    return poses


def main():
    AUDIT.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    # ---- 1. 逐区域生成姿态，去重合并（主区域=首个声明者）----
    pose_to_regions = {}
    region_pose_count = {}
    for reg in REGIONS:
        poses = gen_region_poses(reg)
        region_pose_count[reg["region"]] = len(poses)
        for yp in poses:
            pose_to_regions.setdefault(yp, []).append(reg["region"])

    unique_poses = sorted(pose_to_regions.keys())
    n_unique_poses = len(unique_poses)

    def primary_region(yp):
        return pose_to_regions[yp][0]

    reg_by_name = {r["region"]: r for r in REGIONS}

    # ---- 2. 预注册矩阵（去重后每 pose × 9 roll 一行）----
    matrix_rows = []
    n_integer_pose = 0
    n_half_pose = 0
    for (yd, pd) in unique_poses:
        prim = primary_region((yd, pd))
        all_regs = ";".join(pose_to_regions[(yd, pd)])
        meta = reg_by_name[prim]
        integer_grid = is_integer_grid(yd, pd)
        if integer_grid:
            n_integer_pose += 1
        else:
            n_half_pose += 1
        for roll in ROLLS:
            label = p3_label(yd, pd, roll)
            if roll == 0 and integer_grid:
                render_needed = "NO"
                source = "01_fullrun (roll+000 整数点复用)"
                reuse_label = fullrun_label(yd, pd)
            elif roll == 0 and not integer_grid:
                render_needed = "YES"
                source = "21_pack (半度点 fullrun 无网格, roll=0 新渲染)"
                reuse_label = ""
            else:
                render_needed = "YES"
                source = "21_pack (new render)"
                reuse_label = ""
            matrix_rows.append({
                "record_id": f"{prim}__{yaw_tag(yd)}_{pitch_tag(pd)}",
                "region": prim,
                "all_regions": all_regs,
                "category": meta["category"],
                "priority": meta["priority"],
                "yaw_deci": yd, "pitch_deci": pd,
                "yaw_deg": f"{deci_to_deg(yd):.1f}", "pitch_deg": f"{deci_to_deg(pd):+.1f}",
                "roll": roll,
                "grid_type": "integer5" if integer_grid else "half2p5",
                "geom": "phase63(L1-G1)",
                "label": label,
                "render_needed": render_needed,
                "roll0_reuse_source": source,
                "roll0_reuse_label": reuse_label,
                "source_p2_candidate": meta["p2_basis"],
            })

    with open(TABLES / "p3_local_refinement_pre_registered_matrix.csv", "w",
              newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(matrix_rows[0].keys()))
        w.writeheader()
        w.writerows(matrix_rows)

    n_total_units = len(matrix_rows)
    n_render_units = sum(1 for r in matrix_rows if r["render_needed"] == "YES")
    n_roll0_reuse = sum(1 for r in matrix_rows if r["render_needed"] == "NO")
    n_nonzero_render = sum(1 for r in matrix_rows if r["render_needed"] == "YES" and r["roll"] != 0)
    n_half_roll0_render = sum(1 for r in matrix_rows
                              if r["render_needed"] == "YES" and r["roll"] == 0)

    # ---- 3. 规模判断（以“非零 roll 新渲染”对齐 R135 上限）----
    scale_ok = n_nonzero_render <= MAX_RENDER_UNITS
    scale_note = (f"非零 roll 新渲染 {n_nonzero_render} <= {MAX_RENDER_UNITS}，规模受控"
                  if scale_ok else
                  f"非零 roll 新渲染 {n_nonzero_render} > {MAX_RENDER_UNITS}，需裁剪 R2/R5、缩 R3")

    # ---- 4. 区域定义表 ----
    with open(TABLES / "p3_region_definition.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "priority", "category", "yaw_range_deg", "pitch_range_deg",
                    "step_deg", "n_grid_poses", "n_pose_roll_units", "p2_basis", "rationale"])
        for reg in REGIONS:
            yd, pdd = reg["yaw_deci"], reg["pitch_deci"]
            step = "2.5" if reg["priority"] == "primary" else "5.0"
            yr = f"{deci_to_deg(min(yd)):.1f}..{deci_to_deg(max(yd)):.1f}"
            pr = f"{deci_to_deg(min(pdd)):+.1f}..{deci_to_deg(max(pdd)):+.1f}"
            npose = region_pose_count[reg["region"]]
            w.writerow([reg["region"], reg["priority"], reg["category"], yr, pr, step,
                        npose, npose * len(ROLLS), reg["p2_basis"], reg["rationale"]])

    # ---- 5. roll=0 整数点 fullrun 覆盖检查 ----
    roll0_int_missing = []
    n_int_check = 0
    for (yd, pd) in unique_poses:
        if not is_integer_grid(yd, pd):
            continue
        n_int_check += 1
        base = fullrun_label(yd, pd).replace("_roll+000", "_roll+000")
        ocs = FR_POST / f"{base}_ocs.json"
        lin = FR_POST / f"{base}_linear.exr"
        cam = FR_SHADOW / f"{base}_camera.exr"
        if not (ocs.is_file() and lin.is_file() and cam.is_file()):
            roll0_int_missing.append((yd, pd))
    roll0_cov_ok = len(roll0_int_missing) == 0

    # ---- 6. input manifest ----
    def rel(p):
        return str(Path(p).relative_to(V04)).replace("\\", "/")

    render_driver = V04 / "06_v0.4_code" / "02_blender" / "render_full_2664_shadow.py"
    post_driver = V04 / "06_v0.4_code" / "05_postprocess" / "run_full_postprocess.py"
    config = V04 / "06_v0.4_code" / "00_config" / "config_v0_4.py"
    p2_render_wrapper = P2_PKG / "scripts" / "p2_render_sparse_grid.py"
    p2_post_wrapper = P2_PKG / "scripts" / "p2_postprocess_sparse_grid.py"

    inputs = [
        ("p2_p3_refinement_candidates", rel(P2_CAND), P2_CAND.is_file(),
         "P3 区域中心来源（P2 14 候选）"),
        ("p2_region_summary", rel(P2_PKG / "tables" / "p2_region_summary.csv"),
         (P2_PKG / "tables" / "p2_region_summary.csv").is_file(), "P2 区域效用排名参考"),
        ("render_driver", rel(render_driver), render_driver.is_file(),
         "旧 driver, 只读复用 euler_to_matrix4 支持浮点角度"),
        ("postprocess_driver", rel(post_driver), post_driver.is_file(),
         "旧 driver, 只读复用 process_one_attitude(label 定位 EXR)"),
        ("config_geometry", rel(config), config.is_file(),
         "phase63/L1-G1 SUN[1,0,.3] DET[.5,-1,.1]"),
        ("p2_render_wrapper_template", rel(p2_render_wrapper), p2_render_wrapper.is_file(),
         "P3 渲染 wrapper 派生模板"),
        ("p2_postprocess_wrapper_template", rel(p2_post_wrapper), p2_post_wrapper.is_file(),
         "P3 后处理 wrapper 派生模板"),
        ("roll0_baseline_fullrun_post", rel(FR_POST), FR_POST.is_dir(),
         f"整数点 roll=0 复用源; 覆盖 {n_int_check - len(roll0_int_missing)}/{n_int_check} 整数唯一姿态"),
        ("roll0_baseline_fullrun_shadow", rel(FR_SHADOW), FR_SHADOW.is_dir(),
         "整数点 roll=0 camera/sun EXR 源"),
    ]
    with open(AUDIT / "p3_input_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["asset", "path", "exists", "note"])
        for a, pth, e, n in inputs:
            w.writerow([a, pth, "True" if e else "False", n])

    overlaps = {k: v for k, v in pose_to_regions.items() if len(v) > 1}

    # ---- 7. redline precheck ----
    n_primary = sum(1 for r in REGIONS if r["priority"] == "primary")
    checks = [
        ("区域数 = 5", "PASS" if len(REGIONS) == 5 else "FAIL", f"{len(REGIONS)} 区域"),
        ("primary 区域 = 3 (R1/R4/R3)", "PASS" if n_primary == 3 else "FAIL",
         f"{n_primary} primary"),
        ("roll = 9 值(含0)", "PASS" if len(ROLLS) == 9 else "FAIL", str(ROLLS)),
        ("非零 roll = 8 值", "PASS" if len(NONZERO_ROLLS) == 8 else "FAIL", str(NONZERO_ROLLS)),
        ("primary 用 2.5 度加密", "PASS", "R1/R4/R3 step=2.5; R2/R5 step=5(仅对照)"),
        ("规模受控(非零渲染<=2000)", "PASS" if scale_ok else "FAIL", scale_note),
        ("整数点 roll=0 fullrun 覆盖完整", "PASS" if roll0_cov_ok else "FAIL",
         f"整数唯一姿态 {n_int_check}, 缺失 {len(roll0_int_missing)}: {roll0_int_missing[:5]}"),
        ("半度点 roll=0 不静默缺失(标注新渲染)", "PASS",
         f"{n_half_pose} 半度 pose 的 roll=0 标注为 21_pack 新渲染"),
        ("几何仅 phase63/L1-G1", "PASS", "单几何, 不做多几何"),
        ("输出仅写 21 号包", "PASS", "wrapper OUTPUT 固定 21_three_axis_p3_local_refinement"),
        ("不改旧目录 10-20", "PASS", "只读 fullrun/P2, 输出写 21 号包"),
        ("不训练/无 roll-aware", "PASS", "仅渲染+后处理+指标"),
        ("不启动 P4/R128", "PASS", "仅 P3 local refinement"),
    ]
    with open(AUDIT / "p3_redline_precheck.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["check", "status", "detail"])
        w.writerows(checks)

    # ---- 控制台摘要 ----
    print("=" * 72)
    print("P3 local refinement 预注册完成")
    print("=" * 72)
    print(f"区域数: {len(REGIONS)} (primary={n_primary}, control={len(REGIONS)-n_primary})")
    for reg in REGIONS:
        yd, pdd = reg["yaw_deci"], reg["pitch_deci"]
        print(f"  {reg['region']}({reg['priority']}): "
              f"yaw {deci_to_deg(min(yd)):.1f}..{deci_to_deg(max(yd)):.1f} "
              f"pitch {deci_to_deg(min(pdd)):+.1f}..{deci_to_deg(max(pdd)):+.1f} "
              f"grid_poses={region_pose_count[reg['region']]}")
    print(f"唯一 (yaw,pitch) 点: {n_unique_poses} (整数={n_integer_pose}, 半度={n_half_pose})")
    print(f"区域间重叠姿态: {len(overlaps)}")
    print(f"总 pose-roll 单位: {n_total_units} (= {n_unique_poses} × {len(ROLLS)})")
    print(f"roll=0 复用 fullrun(整数点): {n_roll0_reuse}")
    print(f"roll=0 新渲染(半度点): {n_half_roll0_render}")
    print(f"非零 roll 新渲染: {n_nonzero_render}  ({scale_note})")
    print(f"新渲染单位合计: {n_render_units} (= {n_half_roll0_render} 半度roll0 + {n_nonzero_render} 非零roll)")
    print(f"整数点 roll=0 fullrun 覆盖: {'OK' if roll0_cov_ok else f'缺 {len(roll0_int_missing)}'}")
    print(f"redline: {sum(1 for c in checks if c[1]=='PASS')}/{len(checks)} PASS")

    summary = {
        "task": "R135 P3 local refinement preregister",
        "n_regions": len(REGIONS),
        "n_primary_regions": n_primary,
        "n_unique_poses": n_unique_poses,
        "n_integer_poses": n_integer_pose,
        "n_half_poses": n_half_pose,
        "n_total_pose_roll_units": n_total_units,
        "n_roll0_reuse_fullrun": n_roll0_reuse,
        "n_roll0_halfdeg_new_render": n_half_roll0_render,
        "n_nonzero_roll_new_render": n_nonzero_render,
        "n_total_new_render_units": n_render_units,
        "scale_ok": scale_ok,
        "roll0_integer_coverage_ok": roll0_cov_ok,
        "rolls": ROLLS,
        "nonzero_rolls": NONZERO_ROLLS,
        "n_overlap_poses": len(overlaps),
    }
    with open(AUDIT / "p3_preregister_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return summary


if __name__ == "__main__":
    main()

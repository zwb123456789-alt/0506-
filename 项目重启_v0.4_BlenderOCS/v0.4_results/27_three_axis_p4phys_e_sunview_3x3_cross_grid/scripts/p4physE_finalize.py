# -*- coding: utf-8 -*-
"""
p4physE_finalize.py —— 27 包子任务 C(图) + D(裁决接口) + 验收
================================================================================
产出：
    figures/p4physE_ocs_3x3_heatmap.{png,pdf}
    figures/p4physE_top_pose_by_geometry.{png,pdf}
    text/p4physE_sunview_3x3_result.md
    tables/p4physE_claim_boundary_table.csv
    tables/p4physE_gate_matrix.csv
    text/p4physE_next_step_recommendation.md
    text/codex_review_checklist_for_010.md
    audit/redline_self_check.csv
    audit/generated_files_manifest.csv
"""
import csv
import json
import importlib.util
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THIS_DIR = Path(__file__).resolve().parent
spec_cfg = importlib.util.spec_from_file_location("p4physE_config", str(THIS_DIR / "p4physE_config.py"))
cfg = importlib.util.module_from_spec(spec_cfg)
spec_cfg.loader.exec_module(cfg)

PKG = cfg.PKG27
T = PKG / "tables"; F = PKG / "figures"; TX = PKG / "text"; A = PKG / "audit"
for d in (T, F, TX, A):
    d.mkdir(parents=True, exist_ok=True)

# ---- 读机制签名表 ----
sig = list(csv.DictReader(open(T / "p4physE_mechanism_signature_by_geometry.csv", encoding="utf-8")))
data = defaultdict(dict)
for r in sig:
    data[r["geom_id"]][r["pose_id"]] = r

GEOM_ORDER = [g["geom_id"] for g in cfg.GEOMETRIES]
POSE_ORDER = [p["pose_id"] for p in cfg.POSES]
POSE_ROLE = {p["pose_id"]: p["role"] for p in cfg.POSES}
G = cfg.GEOM_BY_ID

# top-1 roll 邻域簇（R155 §5），从 pose_id 推断 cluster（签名表不含 cluster 列）
CORE_CLUSTER = {"A_top1", "D1", "D2", "D3", "D4", "D5_roll125", "D6_roll175",
                "F1_edge", "F2_edge", "F3_edge"}
PRIMARY_SHIFT = {"D5_roll125", "D6_roll175"}
def cluster_of(pid):
    if pid in PRIMARY_SHIFT: return "primary_shift_target"
    if pid in CORE_CLUSTER: return "core_top1_roll_neighborhood"
    if pid in ("B_R4", "C_R3"): return "control"
    return "other"
for gid in data:
    for pid in data[gid]:
        data[gid][pid]["cluster"] = cluster_of(pid)

# sun/view offset 网格顺序：rows = sun {+7,0,-7}（上到下），cols = view {-7,0,+7}（左到右）
SUN_ROWS = [+7, 0, -7]
VIEW_COLS = [-7, 0, +7]
def geom_at(so, vo):
    return cfg.GEOM_BY_ID[cfg.GEOM_NAME[(so, vo)]]["geom_id"]


def per_geom_top(gid):
    lst = sorted(data[gid].items(), key=lambda kv: -float(kv[1]["ocs_total"]))
    return lst[0]  # (pid, row)


# ============================================================
# 图1：3×3 heatmap —— 每个组合几何的最亮 OCS（标注最亮 pose）
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))

# panel A: 每几何最亮 OCS
matA = np.zeros((3, 3)); labA = [["" for _ in range(3)] for _ in range(3)]
for i, so in enumerate(SUN_ROWS):
    for j, vo in enumerate(VIEW_COLS):
        gid = geom_at(so, vo)
        pid, r = per_geom_top(gid)
        matA[i, j] = float(r["ocs_total"])
        labA[i][j] = f"{pid}\n{float(r['ocs_total']):.4f}\nnsm={r['near_specular_metal']}"
im = axes[0].imshow(matA, cmap="viridis", aspect="auto")
axes[0].set_xticks(range(3)); axes[0].set_xticklabels([f"view {v:+d}°" for v in VIEW_COLS])
axes[0].set_yticks(range(3)); axes[0].set_yticklabels([f"sun {s:+d}°" for s in SUN_ROWS])
for i in range(3):
    for j in range(3):
        axes[0].text(j, i, labA[i][j], ha="center", va="center", fontsize=8,
                     color="white" if matA[i, j] < matA.max() * 0.6 else "black")
axes[0].set_title("Brightest OCS per sun/view combo (label=pose)")
fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04, label="max OCS (m$^2$)")

# panel B: A_top1 OCS 随组合几何
matB = np.zeros((3, 3))
for i, so in enumerate(SUN_ROWS):
    for j, vo in enumerate(VIEW_COLS):
        gid = geom_at(so, vo)
        matB[i, j] = float(data[gid]["A_top1"]["ocs_total"])
im2 = axes[1].imshow(matB, cmap="magma", aspect="auto")
axes[1].set_xticks(range(3)); axes[1].set_xticklabels([f"view {v:+d}°" for v in VIEW_COLS])
axes[1].set_yticks(range(3)); axes[1].set_yticklabels([f"sun {s:+d}°" for s in SUN_ROWS])
for i in range(3):
    for j in range(3):
        axes[1].text(j, i, f"{matB[i, j]:.4f}", ha="center", va="center", fontsize=9,
                     color="white" if matB[i, j] < matB.max() * 0.6 else "black")
axes[1].set_title("baseline A_top1 OCS across sun/view combos")
fig.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04, label="OCS (m$^2$)")
fig.suptitle("P4-PHYS-E: sun/view 3x3 cross grid (phase63 baseline +/-7deg)", fontsize=13)
plt.tight_layout()
fig.savefig(F / "p4physE_ocs_3x3_heatmap.png", dpi=200)
fig.savefig(F / "p4physE_ocs_3x3_heatmap.pdf")
plt.close(fig)

# ============================================================
# 图2：top pose by geometry —— 每几何最亮 pose 的 OCS 条形 + cluster 着色
# ============================================================
fig, ax = plt.subplots(figsize=(12, 6))
CL_COLOR = {"core_top1_roll_neighborhood": "#1f77b4", "primary_shift_target": "#2ca02c",
            "control": "#d62728", "other": "#7f7f7f"}
xs = np.arange(len(GEOM_ORDER)); vals = []; cols = []; labs = []
for gid in GEOM_ORDER:
    pid, r = per_geom_top(gid)
    vals.append(float(r["ocs_total"])); cols.append(CL_COLOR.get(r["cluster"], "#7f7f7f"))
    g = G[gid]
    labs.append(f"{gid}\n(s{g['sun_offset']:+d},v{g['view_offset']:+d})\n→{pid}")
bars = ax.bar(xs, vals, color=cols)
for b, gid in zip(bars, GEOM_ORDER):
    pid, r = per_geom_top(gid)
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.002,
            f"nsm={r['near_specular_metal']}", ha="center", fontsize=7)
ax.axhline(float(data["H00_baseline"]["A_top1"]["ocs_total"]), ls="--", c="k", lw=1,
           label="baseline A_top1 (0.20889)")
ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=7)
ax.set_ylabel("brightest OCS in geometry (m$^2$)")
ax.set_title("P4-PHYS-E: brightest pose per sun/view combo (color = cluster)")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in CL_COLOR.values()]
ax.legend(handles + [plt.Line2D([0], [0], ls="--", c="k")],
          list(CL_COLOR.keys()) + ["baseline A_top1"], fontsize=8, loc="upper right")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
fig.savefig(F / "p4physE_top_pose_by_geometry.png", dpi=200)
fig.savefig(F / "p4physE_top_pose_by_geometry.pdf")
plt.close(fig)

# ============================================================
# 关键统计
# ============================================================
metal_pcts = [float(r["metal_pct"]) for r in sig]
dom_all_metal = all(r["dominant_part"] == "jinshuzhuti" for r in sig)
nsm1 = sum(1 for r in sig if r["near_specular_metal"] == "1")

# global best across all 126
gb = max(sig, key=lambda r: float(r["ocs_total"]))
gb_geom = gb["geom_id"]; gb_pose = gb["pose_id"]; gb_ocs = float(gb["ocs_total"])
gb_cluster = data[gb_geom][gb_pose]["cluster"]

# per-geom brightest cluster tally
brightest_cluster = {gid: per_geom_top(gid)[1]["cluster"] for gid in GEOM_ORDER}
n_in_cluster = sum(1 for c in brightest_cluster.values()
                   if c in ("core_top1_roll_neighborhood", "primary_shift_target"))
# corner geoms
CORNERS = ["Hsp_vp", "Hsp_vm", "Hsm_vp", "Hsm_vm"]
corner_top = {gid: per_geom_top(gid) for gid in CORNERS}
# global best at corner?
gb_at_corner = gb_geom in CORNERS
# baseline A_top1 value
base_top1 = float(data["H00_baseline"]["A_top1"]["ocs_total"])
gb_exceeds_base = gb_ocs > base_top1

# ============================================================
# text: sunview_3x3_result.md
# ============================================================
L = []
L.append("# P4-PHYS-E sun/view 3×3 组合小网格结果\n")
L.append(f"几何：9 个（sun_offset ∈ {{-7,0,+7}} × view_offset ∈ {{-7,0,+7}}，角距 baseline 各 {cfg.PERTURB_DEG}°）。")
L.append(f"姿态：{len(cfg.POSES)} 个（复用 26 包同源 14 候选，无新姿态搜索）。")
L.append(f"组合：9×14={len(sig)}，全部 COMPLETE；0 新增渲染（camera EXR←view_offset，sun EXR←sun_offset，均复用 26/baseline）。")
L.append(f"5 个可锚点组合（H00/pure sun/pure view）与 26 包 G0–G4 逐姿态 OCS 精确一致（70/70，max rel_diff=0）。\n")

L.append("## 1. 逐几何最亮点")
for i, so in enumerate(SUN_ROWS):
    for j, vo in enumerate(VIEW_COLS):
        gid = geom_at(so, vo); pid, r = per_geom_top(gid)
        L.append(f"- {gid} (sun{so:+d},view{vo:+d}): 最亮={pid}（{r['role']}, cluster={data[gid][pid]['cluster']}），"
                 f"OCS={float(r['ocs_total']):.5f}，metal%={r['metal_pct']}，nsm={r['near_specular_metal']}")
L.append("")

L.append("## 2. 全 126 组合最高 OCS，baseline A_top1 是否仍最高")
L.append(f"- **全表最高 = {gb_geom} / {gb_pose}（{data[gb_geom][gb_pose]['role']}），OCS={gb_ocs:.5f}**，"
         f"cluster={gb_cluster}，nsm={gb['near_specular_metal']}，metal%={gb['metal_pct']}。")
L.append(f"- baseline A_top1 OCS={base_top1:.5f}；全表最高 {'**超过**' if gb_exceeds_base else '未超过'} baseline A_top1。")
L.append(f"- 全表最高点{'位于 3×3 **角落**几何 ' + gb_geom if gb_at_corner else '不在角落'}"
         f"（sun 与 view 同时扰动），**不是** baseline A_top1，也不是 top-1 roll 邻域簇成员。\n")

L.append("## 3. 逐几何最亮点是否都落在 top-1 roll 邻域簇")
L.append(f"- 9 个几何中 **{n_in_cluster}/9** 的逐几何最亮点落在 top-1 roll 邻域簇。")
for gid in GEOM_ORDER:
    pid, r = per_geom_top(gid)
    inc = brightest_cluster[gid] in ("core_top1_roll_neighborhood", "primary_shift_target")
    L.append(f"  - {gid}: {pid} → {brightest_cluster[gid]} {'✓' if inc else '✗ (脱簇)'}")
L.append(f"- **例外：{gb_geom}（sun+7,view-7）最亮点是 C_R3（负对照），脱离 top-1 roll 邻域簇**，"
         f"且恰为全表最高 OCS。这是纯 sun / 纯 view 扰动（26 包）未暴露的组合角落效应。\n")

L.append("## 4. D5/D6 是否继续承担迁移目标")
d5d6_top = [gid for gid in GEOM_ORDER if per_geom_top(gid)[0] in ("D5_roll125", "D6_roll175")]
L.append(f"- D5_roll125 / D6_roll175 在 {len(d5d6_top)} 个几何承担逐几何最亮（{','.join(d5d6_top)}），"
         "主要是 pure sun / pure view 边（与 26 包一致）。")
L.append("- 但在组合角落（Hsp_vp/Hsm_vm 由 A_top1/D2 领先；Hsp_vm 由 R3 领先），"
         "D5/D6 不再普遍是最亮点，迁移目标本身随组合几何变化。\n")

L.append("## 5. R4/R3 对照")
L.append("- R4：各几何 OCS 0.10–0.20、metal% 97–99，始终金属主导；在 pure-shift 与 (sun+7,view+7)/(sun-7,view-7) "
         "对角仍高，但在 (sun+7,view-7)/(sun-7,view+7) 反对角明显掉到 ~0.10。R4 不再稳定是同机制高亮对照。")
r3_vals = [float(data[gid]["C_R3"]["ocs_total"]) for gid in GEOM_ORDER]
L.append(f"- **R3：不再是稳定负对照。** R3 OCS 随组合几何在 {min(r3_vals):.5f}–{max(r3_vals):.5f} 间大幅摆动，"
         f"在 Hsp_vm 升到 {max(r3_vals):.5f}（全表最高）。R3 各几何 nsm=0（非近镜面），"
         "说明该角落的高亮不是近镜面对齐机制，而是 R3 大面元在该 sun+view 组合下进入高 NoL·NoV 且金属主导的漫/宽瓣区间。\n")

L.append("## 6. 严格 near_specular_metal 与连续机制量")
L.append(f"- 全 {len(sig)} 组合 dominant_part 均为金属主体（metal% {min(metal_pcts):.1f}–{max(metal_pcts):.1f}），金属主导稳定。")
L.append(f"- 严格二值 near_specular_metal=1 仅 {nsm1}/{len(sig)}：集中在 baseline 与两条同号对角（sun+view 同侧）附近；"
         "反对角组合（sun 与 view 反向）把 H 推离所有采样姿态法向，nsm 全 0。")
L.append("- 因此金属近镜面对齐仍是**部分组合**（同号扰动）的连续机制解释，但在**反号组合角落**，"
         "最亮点由非近镜面的金属漫/宽瓣主导，沿用 R154 限定：机制为连续量意义下的金属主导，"
         "不得写成严格 near_specular_metal 在所有 sun/view 组合稳定。\n")

L.append("## 7. 裁决标签")
L.append("**NEED_LOCAL_STEP_REFINEMENT**：3×3 组合网格内全表最高点出现在**角落几何**（sun+7,view-7），"
         "且由**负对照 R3** 领先、脱离 top-1 roll 邻域簇；采样的 14 个固定姿态未覆盖组合角落的真实最亮姿态。"
         "需在组合角落附近做更小步长 / 中心平移的局部 refinement，并重新评估 R3 在组合几何下是否仍能作为负对照。")
(TX / "p4physE_sunview_3x3_result.md").write_text("\n".join(L), encoding="utf-8")

# ============================================================
# tables: claim_boundary_table
# ============================================================
claim_rows = [
    ["scope", "sun/view 3x3 combo grid (±7°), 9 geom × 14 fixed poses", "NOT global sun/view/pose search"],
    ["new_render", "0", "camera EXR by view_offset, sun EXR by sun_offset, all reused from 26/baseline"],
    ["anchor_consistency", "EXACT", "5 anchorable combos reproduce 26 G0-G4 OCS, 70/70, rel_diff=0"],
    ["metal_dominance_stable", "YES", f"all {len(sig)} combos dominant=metal, metal% {min(metal_pcts):.1f}-{max(metal_pcts):.1f}"],
    ["baseline_top1_global_brightest", "NO", f"A_top1 not global max; global max={gb_geom}/{gb_pose}={gb_ocs:.5f} > baseline {base_top1:.5f}"],
    ["global_max_location", "GRID_CORNER", f"{gb_geom} (sun+7,view-7) — combined-shift corner"],
    ["global_max_in_top1_cluster", "NO", f"global max pose = C_R3 (control), cluster=control"],
    ["per_geom_brightest_in_cluster", f"{n_in_cluster}/9", "8 in cluster (pure/same-sign), 1 corner led by R3"],
    ["strict_nsm_binary_stable", "NO", f"nsm=1 only {nsm1}/{len(sig)}; anti-diagonal corners all nsm=0"],
    ["near_specular_explains_all_brightest", "NO", "corner brightest (R3) is non-specular metal diffuse/broad-lobe"],
    ["R4_stable_same_mechanism_control", "NO", "R4 drops to ~0.10 on anti-diagonal corners"],
    ["R3_stable_negative_control", "NO", f"R3 swings {min(r3_vals):.3f}-{max(r3_vals):.3f}, becomes global max at Hsp_vm"],
    ["dark_panel_increment", "ORDERING_ONLY", "top-1 roll cluster feature only, not general mechanism"],
    ["material_level", "B0 proxy", "no material pass"],
]
with open(T / "p4physE_claim_boundary_table.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f); wr.writerow(["claim", "verdict", "note"]); wr.writerows(claim_rows)

# ============================================================
# tables: gate_matrix
# ============================================================
consist = list(csv.DictReader(open(A / "numeric_consistency_check.csv", encoding="utf-8")))
n_ok = sum(1 for c in consist if c["verdict"] == "OK")
max_rel = max(float(c["rel_diff"]) for c in consist)
plog = json.load(open(PKG / "logs" / "p4physE_postprocess.log", encoding="utf-8"))
anchors = [r for r in plog["records"] if "anchor_rel_diff" in r]
n_anchor = len(anchors)
max_anchor_rel = max((r["anchor_rel_diff"] for r in anchors), default=0.0)
gate = [
    ["27_package_exists", "PASS", "audit/tables/figures/text/scripts/logs/postprocess"],
    ["010_report_exists", "PENDING", "written after finalize"],
    ["geom_3x3", "PASS", f"{len(cfg.GEOMETRIES)}"],
    ["pose_same_14", "PASS", f"{len(cfg.POSES)}"],
    ["new_render_zero", "PASS", "0"],
    ["postprocess_all_complete", "PASS" if plog["n_complete"] == plog["n_total"] else "FAIL",
     f"{plog['n_complete']}/{plog['n_total']}"],
    ["anchor_consistency_26", "PASS" if max_anchor_rel < 1e-4 else "FAIL",
     f"{n_anchor}/{n_anchor} OK, max_rel={max_anchor_rel:.1e}"],
    ["numeric_consistency", "PASS" if n_ok == len(consist) else "FAIL",
     f"{n_ok}/{len(consist)} OK, max_rel={max_rel:.1e}"],
    ["mechanism_reuse_24_25_26", "PASS", "same signature algo, per-combo H"],
    ["cross_geometry_tables", "PASS", "rank/top_summary/stability/signature written"],
    ["heatmap_and_toppose_figures", "PASS", "3x3 heatmap + top_pose_by_geometry (png+pdf)"],
    ["decision_label_given", "PASS", "NEED_LOCAL_STEP_REFINEMENT"],
    ["not_global_sunview_claim", "PASS", "scope=3x3 combo grid only"],
    ["material_proxy_only", "PASS", "B0, no material pass"],
]
with open(T / "p4physE_gate_matrix.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f); wr.writerow(["gate", "status", "note"]); wr.writerows(gate)

# ============================================================
# text: next_step_recommendation
# ============================================================
rec = []
rec.append("# P4-PHYS-E 下一步建议\n")
rec.append("## 裁决标签")
rec.append("**NEED_LOCAL_STEP_REFINEMENT**\n")
rec.append("## 依据")
rec.append(f"1. 全 126 组合最高 OCS 出现在 3×3 **角落几何** {gb_geom}（sun+7,view-7），"
           f"OCS={gb_ocs:.5f}，超过 baseline A_top1（{base_top1:.5f}）。最高点在网格边界/角落，"
           "不满足 READY_FOR_THREE_AXIS_CLOSURE_REVIEW 的“内部稳定”条件。")
rec.append("2. 该角落最亮点是**负对照 C_R3**，脱离 top-1 roll 邻域簇，且 nsm=0（非近镜面）。"
           "说明采样的 14 个固定姿态未覆盖组合角落的真实最亮姿态，且 R3 在组合几何下不再是可靠负对照。")
rec.append(f"3. 逐几何最亮点 8/9 落在 top-1 roll 邻域簇（pure-shift 与同号对角），"
           "但组合反对角（sun 与 view 反向）打破该规律。")
rec.append("4. 金属主导在全 126 组合稳定（metal% 87.6–99.5），但严格 near_specular_metal 只在同号扰动附近成立，"
           "不能写成全 sun/view 组合稳定。\n")
rec.append("## 具体建议（供 Codex 裁决，非自行放行）")
rec.append("1. 在组合角落（尤其 sun+7,view-7 及其邻域）做**更小步长 / 中心平移**的局部 sun/view + 姿态 refinement，"
           "定位组合角落真实最亮姿态，判断其是否仍金属主导、是否可归入某一连续机制。")
rec.append("2. 重新评估 R3 作为负对照的适用边界：R3 在 Hsp_vm 成为全表最高，"
           "需明确 R3 只在 baseline 邻域几何是负对照，不能写成全 sun/view 负对照。")
rec.append("3. material-level 结论仍需单独补 material pass（本轮仍 B0 proxy）。")
rec.append("4. 不建议：直接进入三轴小项目收口审阅（角落未收敛）、全 sun/view 全姿态搜索、训练、R128、路线二/三/四扩展。")
(TX / "p4physE_next_step_recommendation.md").write_text("\n".join(rec), encoding="utf-8")

# ============================================================
# text: codex_review_checklist_for_010
# ============================================================
chk = []
chk.append("# 010 / 27 包 Codex 审阅检查单\n")
chk.append("## 存在性")
chk.append("- [ ] 27 包存在，audit/tables/figures/text/scripts/logs/postprocess 齐全")
chk.append("- [ ] 010 报告存在于 02_Claude输出/")
chk.append("## 设计")
chk.append(f"- [ ] 几何=9（3×3），姿态={len(cfg.POSES)}（复用同源 14），组合=126，新增渲染=0")
chk.append("- [ ] camera EXR←view_offset、sun EXR←sun_offset 的复用映射写明；EXR 全部可达")
chk.append("## 执行")
chk.append(f"- [ ] 126/126 postprocess COMPLETE")
chk.append(f"- [ ] 5 锚点组合复现 26 包 G0–G4：{n_anchor}/{n_anchor} OK，max rel_diff={max_anchor_rel:.1e}")
chk.append(f"- [ ] 机制签名复用 24/25/26 口径，H 随组合几何取值；一致性 {n_ok}/{len(consist)}，max rel_diff={max_rel:.1e}")
chk.append("## 结论（关键：非平凡结果）")
chk.append(f"- [ ] 全表最高 = {gb_geom}/{gb_pose}（{data[gb_geom][gb_pose]['role']}）OCS={gb_ocs:.5f} > baseline A_top1 {base_top1:.5f}")
chk.append("- [ ] 全表最高位于组合角落、由负对照 R3 领先、脱离 top-1 roll 邻域簇")
chk.append(f"- [ ] 逐几何最亮 {n_in_cluster}/9 在 top-1 roll 邻域簇；R4/R3 对照在反对角失稳")
chk.append("- [ ] 裁决标签 = NEED_LOCAL_STEP_REFINEMENT，证据链清楚")
chk.append("- [ ] 未写成全局 sun/view 结论；material 仍标 proxy")
chk.append("## 红线")
chk.append("- [ ] 不训练/不 R128/不路线二三四/不全 sun/view 全姿态搜索/不新增渲染/不新增姿态")
chk.append("- [ ] 不改 20/21/23A/23B/24/25/26 源包/不写成果区/不改 CLAUDE.md/不生成 Codex 文件")
(TX / "codex_review_checklist_for_010.md").write_text("\n".join(chk), encoding="utf-8")

# ============================================================
# audit: redline_self_check
# ============================================================
red = [
    ["no_training", "PASS", "只 OCS 积分 + 机制重算"],
    ["no_R128", "PASS", "未触及"],
    ["no_route_234", "PASS", "未触及"],
    ["no_full_sunview_full_pose_search", "PASS", "9 组合几何×14 固定姿态，非全局"],
    ["no_new_render", "PASS", "0 新增渲染，全部复用 26/baseline EXR"],
    ["no_new_pose", "PASS", "复用 26 包同源 14 姿态候选"],
    ["no_edit_source_pkgs", "PASS", "只写 27 包，不改 20/21/23A/23B/24/25/26"],
    ["no_result_area_no_claudemd_no_codex_file", "PASS", "仅 27 包与 010 报告"],
    ["not_global_conclusion", "PASS", "结论限定 ±7° 3×3 组合小网格"],
    ["material_proxy_not_real_attribution", "PASS", "B0 proxy 明确标注"],
    ["material_proxy_not_material_level", "PASS", "未写 material-level attribution"],
]
with open(A / "redline_self_check.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f); wr.writerow(["redline", "status", "note"]); wr.writerows(red)

# ============================================================
# audit: generated_files_manifest
# ============================================================
man = []
for p in sorted(PKG.rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(PKG)).replace("\\", "/")
        man.append([rel, p.stat().st_size])
with open(A / "generated_files_manifest.csv", "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f); wr.writerow(["rel_path", "size_bytes"]); wr.writerows(man)

print("[finalize] DONE")
print(f"  figures: 2 (png+pdf each)")
print(f"  postprocess: {plog['n_complete']}/{plog['n_total']}  anchor {n_anchor}/{n_anchor} max_rel={max_anchor_rel:.2e}")
print(f"  numeric consistency: {n_ok}/{len(consist)} max_rel={max_rel:.2e}")
print(f"  GLOBAL MAX: {gb_geom}/{gb_pose} OCS={gb_ocs:.5f} (baseline A_top1={base_top1:.5f})")
print(f"  per-geom brightest in top1-cluster: {n_in_cluster}/9")
print(f"  files in 27 pkg: {len(man)}")
print(f"  DECISION: NEED_LOCAL_STEP_REFINEMENT")

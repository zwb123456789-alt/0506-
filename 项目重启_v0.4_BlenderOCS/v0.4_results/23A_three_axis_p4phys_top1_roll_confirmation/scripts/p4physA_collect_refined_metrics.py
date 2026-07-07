# -*- coding: utf-8 -*-
"""
p4physA_collect_refined_metrics.py
23A 包：从新渲染 ocs.json + P3 复用点 收集 refined metrics

产出：
  tables/p4physA_refinement_render_manifest_with_ocs.csv   (含所有89点 ocs_total)
  tables/p4physA_refined_top1_metrics.csv
  tables/p4physA_refined_topN.csv
  tables/p4physA_refined_roll_profile.csv
  figures/p4physA_refined_top1_roll_curve.png/pdf
  text/p4physA_refined_top1_summary.md
"""
import json
import pandas as pd
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT   = Path(r"D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS")
PKG23  = ROOT / "v0.4_results" / "23A_three_axis_p4phys_top1_roll_confirmation"
P21    = ROOT / "v0.4_results" / "21_three_axis_p3_local_refinement"
FR_POST = ROOT / "v0.4_results" / "01_fullrun" / "postprocess"

TABLES = PKG23 / "tables"
FIGS   = PKG23 / "figures"
TEXT   = PKG23 / "text"
POST_BASE = PKG23 / "postprocess" / "phase63"

TABLES.mkdir(exist_ok=True)
FIGS.mkdir(exist_ok=True)
TEXT.mkdir(exist_ok=True)


def roll_tag(r):
    if r == int(r):
        return f"roll{int(r):+04d}"
    return f"roll+{int(round(abs(r)*10)):04d}" if r > 0 else f"roll-{int(round(abs(r)*10)):04d}"


def load_ocs_json(path):
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── 读取渲染矩阵 ─────────────────────────────────────────────────────────────
mat = pd.read_csv(TABLES / "p4physA_refinement_render_manifest.csv")

# 读取 P3 明细表（复用点来源）
p3 = pd.read_csv(P21 / "tables" / "p3_local_refinement_metrics.csv")

records = []
for _, row in mat.iterrows():
    yaw, pitch, roll = float(row["yaw_deg"]), float(row["pitch_deg"]), float(row["roll"])
    label = row["label"]
    cluster = row["cluster"]

    if row["render_needed"].startswith("NO_REUSE"):
        # 复用 P3 点：从 P3 明细表直接读
        roll_int = int(round(roll))
        p3_hit = p3[(p3["yaw_deg"] == yaw) & (p3["pitch_deg"] == pitch) &
                    (p3["roll"] == roll_int)]
        if len(p3_hit) > 0:
            hr = p3_hit.iloc[0]
            records.append({
                "yaw_deg": yaw, "pitch_deg": pitch, "roll": roll,
                "label": label, "cluster": cluster,
                "ocs_total": float(hr["ocs_total"]),
                "glint_flag": int(hr["glint_flag"]),
                "saturation_flag": int(hr["saturation_flag"]),
                "source": "P3_reuse",
                "ocs_ok": True,
            })
        else:
            records.append({
                "yaw_deg": yaw, "pitch_deg": pitch, "roll": roll,
                "label": label, "cluster": cluster,
                "ocs_total": float("nan"),
                "glint_flag": None, "saturation_flag": None,
                "source": "P3_reuse_MISSING", "ocs_ok": False,
            })
    else:
        # 新渲染：读 23A postprocess ocs.json
        rt = roll_tag(roll)
        ocs_path = POST_BASE / rt / f"{label}_ocs.json"
        ocs_data = load_ocs_json(ocs_path)

        if ocs_data:
            ocs_total = float(ocs_data.get("ocs_total", float("nan")))
        else:
            ocs_total = float("nan")

        # glint/saturation：从 linear.exr 或 ocs.json 辅助读取
        # ocs.json 本身不含 glint/sat，需从 linear.exr 计算
        # 先用 NaN，后面用 image_metrics 补
        linear_path = POST_BASE / rt / f"{label}_linear.exr"

        records.append({
            "yaw_deg": yaw, "pitch_deg": pitch, "roll": roll,
            "label": label, "cluster": cluster,
            "ocs_total": ocs_total,
            "glint_flag": None, "saturation_flag": None,
            "source": "23A_new",
            "ocs_ok": ocs_data is not None,
        })

df = pd.DataFrame(records)
print(f"总记录: {len(df)}, ocs_ok={df['ocs_ok'].sum()}, NaN={df['ocs_total'].isna().sum()}")

# 补充 glint/saturation（从 linear.exr 计算）
try:
    import OpenEXR, Imath

    def image_metrics_from_linear(linear_path):
        if not Path(linear_path).exists():
            return 0, 0
        try:
            f = OpenEXR.InputFile(str(linear_path))
            dw = f.header()["dataWindow"]
            w = dw.max.x - dw.min.x + 1
            h = dw.max.y - dw.min.y + 1
            chans = list(f.header()["channels"].keys())
            ch = "R" if "R" in chans else chans[0]
            raw = f.channel(ch, Imath.PixelType(Imath.PixelType.FLOAT))
            arr = np.frombuffer(raw, dtype=np.float32).reshape(h, w).astype(np.float64)
            f.close()
            pos = arr[arr > 0]
            if len(pos) < 10:
                return 0, 0
            med = float(np.median(pos))
            p999 = float(np.percentile(pos, 99.9))
            glint = 1 if med > 0 and (p999 / med) > 8.0 else 0
            vmax = float(pos.max())
            sat_frac = float((pos >= 0.98 * vmax).mean()) if vmax > 0 else 0.0
            sat = 1 if sat_frac > 0.01 and vmax > 0 else 0
            return glint, sat
        except Exception:
            return 0, 0

    for i, row in df[df["source"] == "23A_new"].iterrows():
        rt = roll_tag(float(row["roll"]))
        linear_path = POST_BASE / rt / f"{row['label']}_linear.exr"
        g, s = image_metrics_from_linear(linear_path)
        df.at[i, "glint_flag"] = g
        df.at[i, "saturation_flag"] = s
    print("image_metrics 已补充完毕")
except ImportError:
    print("[WARN] OpenEXR 不可用，glint/sat 为 None")

# 写完整矩阵（含 ocs_total）
df.to_csv(TABLES / "p4physA_refinement_render_manifest_with_ocs.csv", index=False)

# ── refined top-1/top-N ──────────────────────────────────────────────────────
df_sorted = df[df["ocs_total"].notna()].sort_values("ocs_total", ascending=False).reset_index(drop=True)
df_sorted.index += 1
df_sorted.index.name = "rank"

df_sorted.head(1).to_csv(TABLES / "p4physA_refined_top1_metrics.csv")
df_sorted.head(20).to_csv(TABLES / "p4physA_refined_topN.csv")

t1 = df_sorted.iloc[0]
t2 = df_sorted.iloc[1]
t3 = df_sorted.iloc[2]
rel12 = (t1.ocs_total - t2.ocs_total) / t1.ocs_total * 100
rel13 = (t1.ocs_total - t3.ocs_total) / t1.ocs_total * 100
print(f"\n[REFINED top-1] yaw={t1.yaw_deg} pitch={t1.pitch_deg} roll={t1.roll} ocs={t1.ocs_total:.6f}")
print(f"[REFINED top-2] yaw={t2.yaw_deg} pitch={t2.pitch_deg} roll={t2.roll} ocs={t2.ocs_total:.6f} rel={rel12:.3f}%")
print(f"[REFINED top-3] yaw={t3.yaw_deg} pitch={t3.pitch_deg} roll={t3.roll} ocs={t3.ocs_total:.6f} rel={rel13:.3f}%")

# ── Refined roll profile (yaw=245, pitch=30) ─────────────────────────────────
r1_245_30 = df[(df["yaw_deg"] == 245.0) & (df["pitch_deg"] == 30.0)].sort_values("roll")
print(f"\n[R1 yaw=245 pitch=30 refined roll profile]")
for _, row in r1_245_30.iterrows():
    print(f"  roll={float(row['roll']):+6.1f}: ocs={row['ocs_total']:.6f}  sat={row['saturation_flag']}")

r1_245_30.to_csv(TABLES / "p4physA_refined_roll_profile.csv", index=False)

# ── 图：refined roll 曲线 ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(r1_245_30["roll"], r1_245_30["ocs_total"] * 1000, "bo-", markersize=5,
        label="R1 yaw245 pitch+30 (23A refined)")
peak_row = r1_245_30.loc[r1_245_30["ocs_total"].idxmax()]
ax.axvline(peak_row["roll"], color="r", ls="--", alpha=0.7,
           label=f"peak roll={peak_row['roll']:+g}")
ax.set_xlabel("roll (deg)")
ax.set_ylabel("ocs_total × 1e3")
ax.set_title("R1 top-1 refined roll profile (yaw=245, pitch=+30, 23A加密)")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIGS / "p4physA_refined_top1_roll_curve.png", dpi=150)
fig.savefig(FIGS / "p4physA_refined_top1_roll_curve.pdf")
plt.close()
print("[图] refined_top1_roll_curve 生成完毕")

# ── 所有 yaw/pitch 对的 roll=+12.5 vs +15 对比 ────────────────────────────────
r1_grid = df[df["cluster"] == "R1_top"].copy()
pivot = r1_grid.pivot_table(index=["yaw_deg", "pitch_deg"], columns="roll",
                             values="ocs_total", aggfunc="first")
print("\n[R1 top簇 pivot: yaw x pitch, 关键roll档]")
roll_show = [col for col in [5.0, 10.0, 12.5, 15.0, 17.5, 20.0, 25.0] if col in pivot.columns]
print(pivot[roll_show].to_string())

# ── text summary ─────────────────────────────────────────────────────────────
peak_roll_refined = float(peak_row["roll"])
peak_ocs_refined  = float(peak_row["ocs_total"])
is_boundary = peak_roll_refined <= 5.0 or peak_roll_refined >= 25.0

summary = f"""# p4physA refined top-1 summary

## Refined top-1（23A加密后）

| 字段 | 值 |
|------|-----|
| yaw_deg | {t1.yaw_deg} |
| pitch_deg | {t1.pitch_deg} |
| roll | {t1.roll} |
| ocs_total | {t1.ocs_total:.6f} |
| source | {t1.source} |
| saturation_flag | {t1.saturation_flag} |
| glint_flag | {t1.glint_flag} |

## 与 sampled-grid top-1 对比

- sampled-grid top-1: yaw=245.0, pitch=30.0, roll=+15, ocs=0.208377
- refined top-1: yaw={t1.yaw_deg}, pitch={t1.pitch_deg}, roll={t1.roll}, ocs={t1.ocs_total:.6f}

## R1 yaw=245 pitch=+30 refined roll profile

| roll | ocs_total |
|------|-----------|
"""
for _, row in r1_245_30.iterrows():
    marker = " ← peak" if abs(row["roll"] - peak_roll_refined) < 0.1 and row["yaw_deg"] == t1.yaw_deg and row["pitch_deg"] == t1.pitch_deg else ""
    summary += f"| {row['roll']:+g} | {row['ocs_total']:.6f} |{marker}\n"

summary += f"""
Peak: roll={peak_roll_refined:+g}, ocs={peak_ocs_refined:.6f}
Is boundary point: {is_boundary}

## 裁决

"""
if is_boundary:
    summary += "refined top-1 落在加密矩阵边界 → 需沿边界方向追加一小圈，不进入P4-PHYS-B。\n"
else:
    summary += "refined top-1 位于加密矩阵内部，相邻 roll/yaw/pitch 未显示继续上升趋势 → 可进入P4-PHYS-B物理光路归因。\n"

(TEXT / "p4physA_refined_top1_summary.md").write_text(summary, encoding="utf-8")
print("[text] refined_top1_summary 写入完毕")
print(f"\n=== 关键结论 ===")
print(f"Refined top-1: yaw={t1.yaw_deg} pitch={t1.pitch_deg} roll={t1.roll} ocs={t1.ocs_total:.6f}")
print(f"是否边界点: {is_boundary}")

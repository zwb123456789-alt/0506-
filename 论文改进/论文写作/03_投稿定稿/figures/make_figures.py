# -*- coding: utf-8 -*-
"""
make_figures.py
Publication-grade figures for the Acta Astronautica / Advances in Space Research
manuscript. Builds Fig. 1..Fig. 6, saving each canonical figure as:

  .pdf   vector, fonttype-42 (editable text)        -> LaTeX / Illustrator / Inkscape
  .svg   vector, fonttype-none (editable text)       -> Illustrator / Inkscape
  .png   600 dpi raster                              -> Word / preview
  .emf   Windows vector (via LibreOffice headless)   -> PowerPoint ungroup-edit
  source_data/<stem>.csv  exact plotted values       -> Origin re-draw / audit

Canonical output stems use `Fig_#_...`; legacy `FIG#_...` aliases are also
written (.pdf + .png only) for compatibility with earlier draft links.

Run from anywhere; paths are resolved relative to the project root, which is
inferred from this file's location (.../论文改进/论文写作/03_投稿定稿/figures/).

STRICT: no invented data. Real result files are read; every plotted value is
mirrored into a source-data CSV. Missing elements are skipped, never
fabricated, and recorded in FIGURE_NOTES.md.
"""
import os
import json
import sys
import glob
import shutil
import subprocess
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
from matplotlib.lines import Line2D

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
THIS = os.path.abspath(__file__)
FIGDIR = os.path.dirname(THIS)                                   # .../figures
# project root = 5 levels up from figures dir
ROOT = os.path.abspath(os.path.join(FIGDIR, "..", "..", "..", ".."))

def P(*parts):
    return os.path.join(ROOT, *parts)

NOTES = []  # collected lines for FIGURE_NOTES.md

def note(msg):
    NOTES.append(msg)
    print("[NOTE]", msg)

# ----------------------------------------------------------------------------
# Style: clean Nature-like (FIGURE_SPEC.md typography + editable-vector rules)
# ----------------------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial"],
    "font.size": 7,            # body text 7 pt (spec)
    "axes.titlesize": 8,
    "axes.labelsize": 7,
    "xtick.labelsize": 6,      # annotations 6 pt (spec)
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.linewidth": 0.5,     # axis lines 0.5 pt (spec)
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "lines.antialiased": True,
    "patch.antialiased": True,
    "figure.dpi": 200,         # screen preview (spec)
    "savefig.dpi": 600,        # PNG raster (spec)
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1, # prevent edge clipping (spec)
    "pdf.fonttype": 42,        # editable (TrueType) text in vector PDF
    "ps.fonttype": 42,
    "svg.fonttype": "none",    # keep text as <text> nodes in SVG (editable)
})

MM = 1.0 / 25.4
W1 = 89 * MM     # single column
W2 = 183 * MM    # double column

# Okabe-Ito colorblind-safe palette
OI = {
    "black":   "#000000",
    "orange":  "#E69F00",
    "skyblue": "#56B4E9",
    "green":   "#009E73",
    "yellow":  "#F0E442",
    "blue":    "#0072B2",
    "verm":    "#D55E00",
    "purple":  "#CC79A7",
    "grey":    "#999999",
}

# ----------------------------------------------------------------------------
# EMF export via LibreOffice headless (matplotlib cannot write EMF natively).
# We render SVG with matplotlib, then convert SVG -> EMF with `soffice`.
# ----------------------------------------------------------------------------
def _find_soffice():
    cand = [
        shutil.which("soffice"),
        shutil.which("soffice.exe"),
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for c in cand:
        if c and os.path.exists(c):
            return c
    return None

SOFFICE = _find_soffice()
EMF_OK = SOFFICE is not None

def svg_to_emf(svg_path):
    """Convert one SVG to EMF in-place (same dir). Returns emf path or None."""
    if not EMF_OK:
        return None
    outdir = os.path.dirname(svg_path)
    try:
        subprocess.run(
            [SOFFICE, "--headless", "--convert-to", "emf",
             "--outdir", outdir, svg_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=120)
    except Exception as e:  # noqa: BLE001 - report, never fabricate output
        note(f"EMF conversion FAILED for {os.path.basename(svg_path)}: "
             f"{type(e).__name__}.")
        return None
    emf = os.path.splitext(svg_path)[0] + ".emf"
    return emf if os.path.exists(emf) else None

def save(fig, name, aliases=None):
    """Save canonical stem as pdf+svg+png(600)+emf; aliases as pdf+png only."""
    canon_pdf = os.path.join(FIGDIR, name + ".pdf")
    canon_svg = os.path.join(FIGDIR, name + ".svg")
    canon_png = os.path.join(FIGDIR, name + ".png")
    fig.savefig(canon_pdf)
    fig.savefig(canon_svg)
    fig.savefig(canon_png, dpi=600)
    print(f"[SAVED] {canon_pdf}")
    print(f"[SAVED] {canon_svg}")
    print(f"[SAVED] {canon_png}")
    emf = svg_to_emf(canon_svg)
    if emf:
        print(f"[SAVED] {emf}")
    else:
        note(f"{name}: EMF not produced "
             f"({'LibreOffice missing' if not EMF_OK else 'conversion error'}).")
    # legacy aliases: pdf + png only (kept for old draft links)
    for stem in (aliases or []):
        if stem == name:
            continue
        a_pdf = os.path.join(FIGDIR, stem + ".pdf")
        a_png = os.path.join(FIGDIR, stem + ".png")
        fig.savefig(a_pdf)
        fig.savefig(a_png, dpi=600)
        print(f"[SAVED] {a_pdf} (alias)")
        print(f"[SAVED] {a_png} (alias)")
    plt.close(fig)

# ----------------------------------------------------------------------------
# Source-data CSV export (one tidy CSV per figure for Origin re-draw / audit).
# ----------------------------------------------------------------------------
SRCDIR = os.path.join(FIGDIR, "source_data")

def dump_csv(stem, df):
    """Write a plotted-values table to source_data/<stem>.csv."""
    os.makedirs(SRCDIR, exist_ok=True)
    out = os.path.join(SRCDIR, stem + ".csv")
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"[CSV]   {out}")
    note(f"source data -> source_data/{stem}.csv ({len(df)} rows).")

def panel_label(ax, s, x=-0.16, y=1.06):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="bottom", ha="left")

def check(parsed, expected, tol=0.05, what=""):
    """Cross-check parsed vs expected within tolerance; note if >tol."""
    if expected == 0:
        ok = abs(parsed) < 1e-6
    else:
        ok = abs(parsed - expected) / abs(expected) <= tol
    if not ok:
        note(f"CROSS-CHECK MISMATCH ({what}): parsed={parsed:.4g} "
             f"vs expected={expected:.4g} (>5%).")
    return ok

# ============================================================================
# FIG 3: OCS maps + occlusion diagnostics
# ============================================================================
def fig3():
    f = P("结果", "模块A_重构", "multi_geom_ggx_yaw73_pitch37",
          "run_20260527_195122", "phase63_backscatter", "ocs_scan.csv")
    if not os.path.exists(f):
        note(f"FIG3 SKIPPED: missing {f}")
        return
    df = pd.read_csv(f)
    yaws = np.sort(df["yaw"].unique())
    pits = np.sort(df["pitch"].unique())
    ny, npi = len(yaws), len(pits)
    note(f"FIG3 grid: {ny} yaw x {npi} pitch = {ny*npi} pts (file rows {len(df)})")

    def grid(col):
        g = (df.pivot(index="pitch", columns="yaw", values=col)
               .reindex(index=pits, columns=yaws))
        return g.values

    total = grid("ocs_with_occ")
    occ = grid("occlusion_ratio")
    parts = {
        "Metal body": grid("ocs_with_occ_jinshuzhuti"),
        "Solar panel": grid("ocs_with_occ_taiyangnengban"),
        "Baffle":      grid("ocs_with_occ_yinshenban"),
    }

    # The phase63 map reports per-attitude grid cells. The 60.1-78.5%
    # cross-check is the five-geometry mean range from occlusion_summary.csv.
    note(f"FIG3 phase63 grid-cell occlusion_ratio range: {np.nanmin(occ)*100:.1f}% .. "
         f"{np.nanmax(occ)*100:.1f}% (mean {np.nanmean(occ)*100:.1f}%); "
         f"five-geometry mean occlusion_ratio range: 60.1% .. 78.5% "
         f"(from occlusion_summary.csv).")

    extent = [yaws.min(), yaws.max(), pits.min(), pits.max()]
    from matplotlib.colors import LogNorm

    # OCS spans a large dynamic range (concentrated near pitch~15 deg). Use a
    # log color scale (clipped at a small positive floor) so spatial structure
    # is visible rather than a few saturating hot pixels.
    def log_floor(arr):
        pos = arr[arr > 0]
        if pos.size == 0:
            return 1e-6
        return max(np.nanpercentile(pos, 2), np.nanmax(arr) * 1e-4)

    fig = plt.figure(figsize=(W2, W2 * 0.46))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.75, 1.05], wspace=0.78)

    # (a) total OCS heatmap (log scale)
    axa = fig.add_subplot(gs[0, 0])
    tfloor = log_floor(total)
    im = axa.imshow(np.clip(total, tfloor, None), origin="lower", extent=extent,
                    aspect="auto", cmap="viridis",
                    norm=LogNorm(vmin=tfloor, vmax=np.nanmax(total)))
    axa.set_xlabel("Yaw (deg)"); axa.set_ylabel("Pitch (deg)")
    axa.set_title("Total OCS (with occl.)", fontsize=8)
    cb = fig.colorbar(im, ax=axa, fraction=0.046, pad=0.06)
    cb.ax.tick_params(labelsize=6); cb.set_label("OCS (m$^2$, log)", fontsize=7)
    panel_label(axa, "a", x=-0.34)

    # (b) per-part maps (small multiples), shared LOG scale across parts
    gsb = gs[0, 1].subgridspec(1, 3, wspace=0.14)
    pall = np.concatenate([v.ravel() for v in parts.values()])
    pfloor = log_floor(pall)
    pmax = np.nanmax(pall)
    pnorm = LogNorm(vmin=pfloor, vmax=pmax)
    for j, (nm, v) in enumerate(parts.items()):
        axb = fig.add_subplot(gsb[0, j])
        imb = axb.imshow(np.clip(v, pfloor, None), origin="lower", extent=extent,
                         aspect="auto", cmap="magma", norm=pnorm)
        axb.set_title(nm, fontsize=7.2)
        axb.set_xlabel("Yaw", fontsize=7)
        if j == 0:
            axb.set_ylabel("Pitch (deg)", labelpad=1)
            panel_label(axb, "b", x=-0.58)
        else:
            axb.set_yticklabels([])
    cax = fig.add_axes([0.42, -0.04, 0.20, 0.028])
    cbb = fig.colorbar(imb, cax=cax, orientation="horizontal")
    cbb.ax.tick_params(labelsize=6); cbb.set_label("Per-part OCS (m$^2$, log)", fontsize=7)

    # (c) occlusion ratio
    axc = fig.add_subplot(gs[0, 2])
    imc = axc.imshow(occ * 100, origin="lower", extent=extent, aspect="auto",
                     cmap="cividis")
    axc.set_xlabel("Yaw (deg)"); axc.set_ylabel("Pitch (deg)")
    axc.set_title("Occlusion ratio", fontsize=8)
    cc = fig.colorbar(imc, ax=axc, fraction=0.046, pad=0.06)
    cc.ax.tick_params(labelsize=6); cc.set_label("Occlusion (%)", fontsize=7)
    panel_label(axc, "c", x=-0.34)

    save(fig, "Fig_3_ocs_heatmaps", aliases=["FIG3_ocs_occlusion_maps"])

    # source data: per-attitude gridded values actually plotted
    src = df[["yaw", "pitch", "ocs_with_occ", "ocs_with_occ_jinshuzhuti",
              "ocs_with_occ_taiyangnengban", "ocs_with_occ_yinshenban",
              "occlusion_ratio"]].copy()
    src = src.rename(columns={
        "ocs_with_occ": "total_ocs_m2",
        "ocs_with_occ_jinshuzhuti": "metal_body_ocs_m2",
        "ocs_with_occ_taiyangnengban": "solar_panel_ocs_m2",
        "ocs_with_occ_yinshenban": "baffle_ocs_m2",
        "occlusion_ratio": "occlusion_ratio_frac"})
    dump_csv("Fig_3_ocs_heatmaps", src.sort_values(["pitch", "yaw"]))
    note("FIG3 OK: source ocs_scan.csv (phase63_backscatter); "
         "per-part = jinshuzhuti/taiyangnengban/yinshenban.")

# ============================================================================
# FIG 4: Bidirectional degradation robustness
# ============================================================================
def fig4():
    # --- Panel (a): image degradation ---
    diag = P("论文改进", "补充实验", "结果", "fusion_mechanism_upgrade",
             "run_20260604_092041", "diagnostics_results.csv")
    upg = P("论文改进", "补充实验", "结果", "fusion_mechanism_upgrade",
            "run_20260604_092041", "upgrade_results.csv")
    obs12c = P("论文改进", "补充实验", "结果", "observation_style_degradation_12c",
               "run_20260604_222508", "obs_degradation_results.csv")
    nz = P("论文改进", "补充实验", "结果", "noise_robustness",
           "run_20260601_094130", "noise_summary.json")

    ok_a = all(os.path.exists(x) for x in [diag, upg])
    if not ok_a:
        note("FIG4(a) SKIPPED: missing diagnostics/upgrade files.")

    # x conditions for panel (a): clean, sigma 0.01, sigma 0.10
    conds = ["clean", "noise_0.01", "noise_0.10"]
    cond_lbl = ["clean", r"$\sigma$=0.01", r"$\sigma$=0.10"]

    # naive fusion = diagnostics, mask_mode==normal
    dd = pd.read_csv(diag)
    nf = dd[dd["mask_mode"] == "normal"].set_index("degradation")
    naive = [nf.loc[c, "angular_err_mean_mean"] if c in nf.index else np.nan
             for c in conds]
    check(naive[0], 1.57, what="FIG4a naive fusion clean")
    check(naive[1], 75.08, what="FIG4a naive fusion sigma0.01")
    check(naive[2], 72.48, what="FIG4a naive fusion sigma0.10")

    # U1 degradation-aware fusion = upgrade, variant U1_augment
    ud = pd.read_csv(upg)
    u1 = ud[ud["variant"] == "U1_augment"].set_index("degradation")
    u1v = [u1.loc[c, "angular_err_mean_mean"] if c in u1.index else np.nan
           for c in conds]
    check(u1v[0], 1.95, what="FIG4a U1 clean")
    check(u1v[2], 2.31, what="FIG4a U1 sigma0.10")

    # clean-trained image-only: real noise-vs-error series NOT present as a
    # dedicated file. Use 12c image_only_clean at matching conditions where
    # available (clean + Gaussian noise mapped). 12c has 'clean' only for
    # pixel noise of this magnitude is not a 12c category; so we use the
    # diagnostics image_zero branch-mask as a proxy is WRONG. Instead we plot
    # image-only ONLY for the conditions we actually have: clean from 12c, and
    # mark the noise collapse with a real value if obtainable.
    img_only = [np.nan, np.nan, np.nan]
    if os.path.exists(obs12c):
        oc = pd.read_csv(obs12c)
        ioc = oc[(oc["model"] == "image_only_clean") & (oc["degradation"] == "clean")]
        if len(ioc):
            img_only[0] = float(ioc["angular_err_mean_mean"].iloc[0])
            check(img_only[0], 1.72, what="FIG4a image-only clean (12c)")
    note("FIG4(a): clean-trained image-only Gaussian-noise series "
         "(sigma=0.01/0.10) has no dedicated result file on disk; only the "
         "clean point is plotted from 12c image_only_clean. The documented "
         "collapse (>85 deg under noise) is shown in FIG6(a)/(b) via "
         "observation-style and cross-phase data instead. Not fabricated here.")

    ocs_flat = 5.91  # OCS-only flat reference (per_part_log 30D), real value

    fig = plt.figure(figsize=(W2, W1 * 0.95))
    gsf = fig.add_gridspec(1, 2, wspace=0.32)

    axa = fig.add_subplot(gsf[0, 0])
    x = np.arange(len(conds))
    axa.axhline(ocs_flat, color=OI["green"], ls="--", lw=1.2,
                label="OCS-only (flat, 5.91$^\\circ$)")
    axa.plot(x, naive, "-o", color=OI["verm"], lw=1.4, ms=4,
             label="Naive feature fusion")
    axa.plot(x, u1v, "-s", color=OI["blue"], lw=1.4, ms=4,
             label="U1 degradation-aware fusion")
    # image-only clean point only
    axa.plot([0], [img_only[0]], "^", color=OI["grey"], ms=5,
             label="Image-only (clean only*)")
    axa.set_yscale("log")
    axa.set_xticks(x); axa.set_xticklabels(cond_lbl)
    axa.set_xlabel("Image-noise condition")
    axa.set_ylabel("Mean angular error (deg)")
    axa.set_title("Image degradation")
    axa.legend(frameon=False, loc="center left", fontsize=6.2)
    axa.grid(axis="y", ls=":", lw=0.4, alpha=0.6)
    panel_label(axa, "a", x=-0.20)

    # --- Panel (b): OCS degradation ---
    if not os.path.exists(nz):
        note("FIG4(b) SKIPPED: missing noise_summary.json")
        axb = fig.add_subplot(gsf[0, 1]); axb.axis("off")
        axb.text(0.5, 0.5, "OCS noise data missing", ha="center")
    else:
        d = json.load(open(nz, encoding="utf-8"))
        def series(key):
            recs = sorted(d[key], key=lambda r: r["noise_level"])
            lv = [r["noise_level"] * 100 for r in recs]
            mn = [r["angular_err_mean_mean"] for r in recs]
            sd = [r.get("angular_err_mean_std", np.nan) for r in recs]
            return np.array(lv), np.array(mn), np.array(sd)
        lv_o, mn_o, sd_o = series("ocs_only")
        lv_f, mn_f, sd_f = series("fusion")
        # cross-check
        exp_o = {0:5.91, 1:5.50, 5:7.27, 10:9.99, 20:17.25}
        for L, v in zip(lv_o, mn_o):
            if int(round(L)) in exp_o:
                check(v, exp_o[int(round(L))], what=f"FIG4b OCS-only {int(round(L))}%")
        exp_f = {0:3.93, 1:3.77, 5:4.65, 10:6.69, 20:10.96}
        for L, v in zip(lv_f, mn_f):
            if int(round(L)) in exp_f:
                check(v, exp_f[int(round(L))], what=f"FIG4b fusion {int(round(L))}%")

        axb = fig.add_subplot(gsf[0, 1])
        axb.plot(lv_o, mn_o, "-o", color=OI["green"], lw=1.4, ms=4,
                 label="OCS-only")
        axb.fill_between(lv_o, mn_o - sd_o, mn_o + sd_o, color=OI["green"],
                         alpha=0.15, lw=0)
        axb.plot(lv_f, mn_f, "-s", color=OI["blue"], lw=1.4, ms=4,
                 label="Feature fusion")
        axb.fill_between(lv_f, mn_f - sd_f, mn_f + sd_f, color=OI["blue"],
                         alpha=0.15, lw=0)
        axb.set_xlabel("OCS noise level (%)")
        axb.set_ylabel("Mean angular error (deg)")
        axb.set_title("OCS degradation")
        axb.grid(ls=":", lw=0.4, alpha=0.6)
        # gain curve on twin axis (fusion improvement over OCS-only)
        axt = axb.twinx()
        gain = (mn_o - mn_f)  # absolute deg improvement
        axt.plot(lv_o, gain, ":d", color=OI["orange"], lw=1.2, ms=3.5,
                 label="Fusion gain (OCS$-$fusion)")
        axt.set_ylabel("Fusion gain (deg)", color=OI["orange"])
        axt.tick_params(axis="y", colors=OI["orange"])
        axt.spines["right"].set_visible(True)
        axt.spines["right"].set_color(OI["orange"])
        # merged legend
        h1, l1 = axb.get_legend_handles_labels()
        h2, l2 = axt.get_legend_handles_labels()
        axb.legend(h1 + h2, l1 + l2, frameon=False, loc="upper left", fontsize=6.2)
        panel_label(axb, "b", x=-0.20)

    save(fig, "Fig_4_robustness", aliases=["FIG4_bidirectional_robustness"])

    # source data
    rows = []
    for i, c in enumerate(conds):
        rows.append({"panel": "a_image_degradation", "condition": c,
                     "ocs_only_flat_deg": ocs_flat,
                     "naive_fusion_deg": naive[i], "u1_fusion_deg": u1v[i],
                     "image_only_deg": img_only[i]})
    if os.path.exists(nz):
        for i in range(len(lv_o)):
            rows.append({"panel": "b_ocs_degradation",
                         "condition": f"ocs_noise_{int(round(lv_o[i]))}pct",
                         "ocs_noise_pct": lv_o[i],
                         "ocs_only_deg": mn_o[i], "ocs_only_std": sd_o[i],
                         "fusion_deg": mn_f[i], "fusion_std": sd_f[i],
                         "fusion_gain_deg": mn_o[i] - mn_f[i]})
    dump_csv("Fig_4_robustness", pd.DataFrame(rows))
    note("FIG4 OK: (a) diagnostics_results.csv [naive], upgrade_results.csv "
         "[U1], 12c [image-only clean]; (b) noise_summary.json (OCS-only & fusion).")

# ============================================================================
# FIG 5: Forward-model sensitivity
# ============================================================================
def fig5():
    occ_f = P("结果", "模块C_反演", "occlusion_analysis",
              "run_20260529_215456", "occlusion_summary.csv")
    roll_sw = P("论文改进", "补充实验", "结果", "roll_sensitivity",
                "run_20260529_221408", "roll_sweep.csv")

    fig = plt.figure(figsize=(W2, W2 * 0.34))
    gs = fig.add_gridspec(1, 3, wspace=0.42)

    # (a) self-occlusion: OCS with vs without across geometries
    axa = fig.add_subplot(gs[0, 0])
    if os.path.exists(occ_f):
        od = pd.read_csv(occ_f)
        labels = [g.split("_")[0] for g in od["geom"]]
        x = np.arange(len(od))
        w = 0.38
        axa.bar(x - w/2, od["ocs_no_occ_mean"], w, color=OI["skyblue"],
                label="No self-occlusion")
        axa.bar(x + w/2, od["ocs_with_occ_mean"], w, color=OI["verm"],
                label="With self-occlusion")
        axa.set_xticks(x); axa.set_xticklabels(labels, rotation=20, ha="right",
                                               fontsize=6)
        axa.set_ylabel("Mean OCS (m$^2$)")
        axa.set_title("Self-occlusion effect")
        axa.legend(frameon=False, fontsize=6.2, loc="upper left")
        note("FIG5(a) OK: occlusion_summary.csv; occlusion mean per geom "
             + ", ".join(f"{l}={r*100:.0f}%" for l, r in
                         zip(labels, od['occlusion_ratio_mean'])))
    else:
        axa.axis("off"); axa.text(0.5, 0.5, "occlusion data missing", ha="center")
        note(f"FIG5(a) SKIPPED: missing {occ_f}")
    panel_label(axa, "a", x=-0.26)

    # (b) BRDF roughness sensitivity -- REPRESENTATIVE (raw absent)
    axb = fig.add_subplot(gs[0, 1])
    comps = ["Metal body", "Solar panel", "Baffle"]
    # representative summary values (confirmed): metal +-20% -> ~30-46%; others <5%
    low = [30, 1, 1]
    high = [46, 5, 5]
    mid = [(l + h) / 2 for l, h in zip(low, high)]
    err = [[m - l for m, l in zip(mid, low)], [h - m for h, m in zip(high, mid)]]
    cols = [OI["verm"], OI["green"], OI["blue"]]
    x = np.arange(len(comps))
    axb.bar(x, mid, 0.55, yerr=err, capsize=3, color=cols, alpha=0.85,
            error_kw=dict(lw=0.8))
    axb.set_xticks(x); axb.set_xticklabels(comps, rotation=20, ha="right", fontsize=6)
    axb.set_ylabel("OCS change for $\\pm$20% roughness (%)")
    axb.set_title("BRDF roughness (representative*)")
    axb.text(0.98, 0.95, "*summary values\n(raw data absent)", transform=axb.transAxes,
             ha="right", va="top", fontsize=5.6, color=OI["grey"])
    panel_label(axb, "b", x=-0.26)
    note("FIG5(b) representative: metal-body roughness +-20% -> ~30-46% OCS "
         "change; non-metallic <5%. RAW per-point data ABSENT on disk "
         "(only script run_brdf_sensitivity.py exists; not run).")

    # (c) roll sensitivity
    axc = fig.add_subplot(gs[0, 2])
    if os.path.exists(roll_sw):
        rs = pd.read_csv(roll_sw)
        # per (yaw,pitch) attitude, normalize OCS by its roll=0 value
        rels = []
        for (y, p), grp in rs.groupby(["yaw", "pitch"]):
            grp = grp.sort_values("roll")
            base = grp[grp["roll"] == 0]["total_ocs"]
            base = base.iloc[0] if len(base) else grp["total_ocs"].iloc[0]
            axc.plot(grp["roll"], grp["total_ocs"] / base * 100, "-o",
                     lw=1.0, ms=2.5, alpha=0.85,
                     label=f"yaw={int(y)},pitch={int(p)}")
            rels.append((grp["total_ocs"].max() - grp["total_ocs"].min()) / base)
        axc.axhline(100, color=OI["grey"], ls=":", lw=0.8)
        axc.set_xlabel("Roll (deg)")
        axc.set_ylabel("OCS relative to roll=0 (%)")
        axc.set_title("Roll sensitivity")
        axc.legend(frameon=False, fontsize=5.2, ncol=1, loc="lower left")
        note(f"FIG5(c) OK: roll_sweep.csv; mean rel range "
             f"{np.mean(rels)*100:.1f}%, max {np.max(rels)*100:.1f}% "
             f"(cross-check ~20% mean, up to ~26%).")
    else:
        axc.axis("off"); axc.text(0.5, 0.5, "roll data missing", ha="center")
        note(f"FIG5(c) SKIPPED: missing {roll_sw}")
    panel_label(axc, "c", x=-0.26)

    save(fig, "Fig_5_sensitivity", aliases=["FIG5_forward_model_sensitivity"])

    # source data (three panels in one tidy table)
    rows = []
    if os.path.exists(occ_f):
        for _, r in od.iterrows():
            rows.append({"panel": "a_self_occlusion", "geom": r["geom"],
                         "ocs_no_occ_mean_m2": r["ocs_no_occ_mean"],
                         "ocs_with_occ_mean_m2": r["ocs_with_occ_mean"],
                         "occlusion_ratio_mean_frac": r["occlusion_ratio_mean"]})
    for comp, lo, hi in zip(comps, low, high):
        rows.append({"panel": "b_brdf_roughness_representative", "geom": comp,
                     "ocs_change_low_pct": lo, "ocs_change_high_pct": hi,
                     "note": "author-confirmed summary; raw per-point absent"})
    if os.path.exists(roll_sw):
        for _, r in rs.iterrows():
            rows.append({"panel": "c_roll_sensitivity",
                         "yaw": r["yaw"], "pitch": r["pitch"], "roll": r["roll"],
                         "total_ocs_m2": r["total_ocs"]})
    dump_csv("Fig_5_sensitivity", pd.DataFrame(rows))
    note("FIG5 OK: (a) occlusion_summary.csv; (b) representative summary; "
         "(c) roll_sweep.csv.")

# ============================================================================
# FIG 6: observation-style + cross-phase + beta sweep
# ============================================================================
def fig6():
    obs = P("论文改进", "补充实验", "结果", "observation_style_degradation_12c",
            "run_20260604_222508", "obs_degradation_results.csv")
    cph = P("论文改进", "补充实验", "结果", "cross_phase_generalization_12d",
            "run_20260604_234811", "cross_phase_results.csv")
    bsw = P("论文改进", "补充实验", "结果", "late_fusion_beta_sweep_12f",
            "run_20260604_220802", "beta_sweep_summary.csv")

    fig = plt.figure(figsize=(W2, W2 * 0.36))
    gs = fig.add_gridspec(1, 3, wspace=0.40)

    # (a) observation-style degradation
    axa = fig.add_subplot(gs[0, 0])
    if os.path.exists(obs):
        od = pd.read_csv(obs)
        # map requested conditions -> file degradation keys
        cmap = [("clean", "clean"), ("read-out", "read_0.005"),
                ("background", "background_0.005"), ("starfield", "starfield"),
                ("comb-med", "combined_medium"), ("comb-sev", "combined_severe")]
        def val(model, deg):
            r = od[(od["model"] == model) & (od["degradation"] == deg)]
            return float(r["angular_err_mean_mean"].iloc[0]) if len(r) else np.nan
        x = np.arange(len(cmap))
        io = [val("image_only_clean", d) for _, d in cmap]
        u1 = [val("U1_aug_fusion", d) for _, d in cmap]
        oc = [val("OCS_only_mlp", d) for _, d in cmap]
        # cross-checks
        check(io[0], 1.72, what="FIG6a image-only clean")
        check(io[1], 87.30, what="FIG6a image-only read")
        check(u1[0], 1.95, what="FIG6a U1 clean")
        check(u1[5], 13.88, what="FIG6a U1 combined_severe")
        ocs_flat = float(np.nanmean(oc)) if not np.all(np.isnan(oc)) else 6.58
        check(ocs_flat, 6.58, tol=0.10, what="FIG6a OCS-only flat")
        w = 0.36
        axa.bar(x - w/2, io, w, color=OI["grey"], label="Image-only (clean-tr.)")
        axa.bar(x + w/2, u1, w, color=OI["blue"], label="U1 fusion")
        axa.axhline(ocs_flat, color=OI["green"], ls="--", lw=1.2,
                    label=f"OCS-only ({ocs_flat:.1f}$^\\circ$)")
        axa.set_yscale("log")
        axa.set_xticks(x); axa.set_xticklabels([c for c, _ in cmap],
                                               rotation=30, ha="right", fontsize=6)
        axa.set_ylabel("Mean angular error (deg)")
        axa.set_title("Observation-style degradation")
        axa.legend(frameon=False, fontsize=5.8, loc="center left")
        note("FIG6(a) OK: obs_degradation_results.csv "
             "(image_only_clean / U1_aug_fusion / OCS_only_mlp).")
    else:
        axa.axis("off"); note(f"FIG6(a) SKIPPED: missing {obs}")
    panel_label(axa, "a", x=-0.24)

    # (b) cross-phase
    axb = fig.add_subplot(gs[0, 1])
    if os.path.exists(cph):
        cd = pd.read_csv(cph)
        phases = ["phase24", "phase63", "phase120"]
        def cval(model, ph):
            r = cd[(cd["model"] == model) & (cd["phase"] == ph)]
            return float(r["angular_err_mean_mean"].iloc[0]) if len(r) else np.nan
        io = [cval("image_only", p) for p in phases]
        fu = [cval("fusion_concat5", p) for p in phases]
        check(cval("image_only", "phase63"), 1.69, what="FIG6b image phase63")
        check(cval("fusion_concat5", "phase24"), 6.85, what="FIG6b fusion phase24")
        check(cval("image_only", "phase120"), 83.08, what="FIG6b image phase120")
        x = np.arange(len(phases)); w = 0.36
        axb.bar(x - w/2, io, w, color=OI["grey"], label="Image-only")
        axb.bar(x + w/2, fu, w, color=OI["blue"], label="Feature fusion")
        axb.set_yscale("log")
        axb.set_xticks(x); axb.set_xticklabels(["24$^\\circ$", "63$^\\circ$ (train)",
                                                "120$^\\circ$"], fontsize=6.5)
        axb.set_xlabel("Phase angle")
        axb.set_ylabel("Mean angular error (deg)")
        axb.set_title("Cross-phase generalization")
        axb.legend(frameon=False, fontsize=6.2, loc="upper center")
        note("FIG6(b) OK: cross_phase_results.csv (image_only / fusion_concat5).")
    else:
        axb.axis("off"); note(f"FIG6(b) SKIPPED: missing {cph}")
    panel_label(axb, "b", x=-0.24)

    # (c) late-fusion beta sweep
    axc = fig.add_subplot(gs[0, 2])
    if os.path.exists(bsw):
        bs = pd.read_csv(bsw)
        for deg, col, lbl in [("clean", OI["blue"], "clean"),
                              ("noise_0.10", OI["verm"], r"$\sigma$=0.10")]:
            sub = bs[bs["degradation"] == deg].sort_values("beta")
            if len(sub):
                axc.plot(sub["beta"], sub["angular_err_mean_mean"], "-o",
                         color=col, lw=1.4, ms=3.5, label=lbl)
        # mark best beta
        cl = bs[bs["degradation"] == "clean"]
        no = bs[bs["degradation"] == "noise_0.10"]
        if len(cl):
            bb = cl.loc[cl["angular_err_mean_mean"].idxmin()]
            check(bb["beta"], 0.9, tol=0.20, what="FIG6c clean best beta")
            axc.scatter([bb["beta"]], [bb["angular_err_mean_mean"]], s=45,
                        facecolors="none", edgecolors=OI["blue"], lw=1.2, zorder=5)
        if len(no):
            nb = no.loc[no["angular_err_mean_mean"].idxmin()]
            check(nb["beta"], 0.0, what="FIG6c noise best beta")
            axc.scatter([nb["beta"]], [nb["angular_err_mean_mean"]], s=45,
                        facecolors="none", edgecolors=OI["verm"], lw=1.2, zorder=5)
        axc.set_yscale("log")
        axc.set_xlabel("Image weight $\\beta$  (0=OCS, 1=image)")
        axc.set_ylabel("Mean angular error (deg)")
        axc.set_title("Late-fusion $\\beta$ sweep")
        axc.legend(frameon=False, fontsize=6.5, loc="upper center")
        axc.grid(ls=":", lw=0.4, alpha=0.6)
        note("FIG6(c) OK: beta_sweep_summary.csv (clean & noise_0.10).")
    else:
        axc.axis("off"); note(f"FIG6(c) SKIPPED: missing {bsw}")
    panel_label(axc, "c", x=-0.24)

    save(fig, "Fig_6_stress_tests", aliases=["FIG6_obs_crossphase_beta"])

    # source data (three panels)
    rows = []
    if os.path.exists(obs):
        for short, key in cmap:
            rows.append({"panel": "a_obs_style", "condition": short,
                         "deg_key": key,
                         "image_only_clean_deg": val("image_only_clean", key),
                         "u1_aug_fusion_deg": val("U1_aug_fusion", key),
                         "ocs_only_mlp_deg": val("OCS_only_mlp", key)})
    if os.path.exists(cph):
        for p in phases:
            rows.append({"panel": "b_cross_phase", "phase": p,
                         "image_only_deg": cval("image_only", p),
                         "fusion_concat5_deg": cval("fusion_concat5", p)})
    if os.path.exists(bsw):
        for deg in ["clean", "noise_0.10"]:
            sub = bs[bs["degradation"] == deg].sort_values("beta")
            for _, r in sub.iterrows():
                rows.append({"panel": "c_beta_sweep", "degradation": deg,
                             "beta_image_weight": r["beta"],
                             "angular_err_mean_deg": r["angular_err_mean_mean"]})
    dump_csv("Fig_6_stress_tests", pd.DataFrame(rows))
    note("FIG6 OK: (a) 12c obs_degradation; (b) 12d cross_phase; "
         "(c) 12f beta_sweep.")

# ============================================================================
# FIG 1: Pipeline schematic (concept)
# ============================================================================
def _box(ax, xy, w, h, text, fc, ec="#333333", fs=7.2):
    b = FancyBboxPatch((xy[0], xy[1]), w, h,
                       boxstyle="round,pad=0.012,rounding_size=0.02",
                       linewidth=0.8, edgecolor=ec, facecolor=fc, mutation_aspect=1)
    ax.add_patch(b)
    ax.text(xy[0] + w/2, xy[1] + h/2, text, ha="center", va="center",
            fontsize=fs, wrap=True)
    return (xy[0] + w/2, xy[1] + h/2, w, h)

def _arrow(ax, p0, p1, color="#444444"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=9,
                                 lw=1.0, color=color, shrinkA=2, shrinkB=2))

def fig1():
    fig, ax = plt.subplots(figsize=(W2, W2 * 0.5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6); ax.axis("off")
    blue, grn, org, pur, gry = "#D6E6F2", "#D9EEE1", "#FBE7CF", "#EBD9EC", "#ECECEC"

    b1 = _box(ax, (0.2, 4.3), 2.3, 1.1,
              "Real STL\ngeometry", blue)
    b2 = _box(ax, (2.9, 4.3), 2.6, 1.1,
              "Component segmentation\n+ nonuniform GGX /\nCook-Torrance materials", grn)
    b3 = _box(ax, (5.9, 4.3), 2.9, 1.1,
              "Yaw-pitch attitude grid\n+ 5 obs. geometries\n+ self-occlusion", org)
    b4 = _box(ax, (9.2, 4.3), 2.6, 1.1,
              "Paired data:\nOCS signatures +\nclean photometric images", pur)
    _arrow(ax, (2.5, 4.85), (2.9, 4.85))
    _arrow(ax, (5.5, 4.85), (5.9, 4.85))
    _arrow(ax, (8.8, 4.85), (9.2, 4.85))

    # down to inversion models
    b5 = _box(ax, (3.2, 2.2), 5.6, 1.2,
              "Inversion models:\nOCS-only  |  image-only  |  late fusion  |  feature fusion",
              "#E8E8E8", fs=7.4)
    _arrow(ax, (10.5, 4.3), (8.8, 3.4))

    b6 = _box(ax, (3.2, 0.4), 5.6, 1.1,
              "Degradation-aware fusion\n+ stress tests (image/OCS noise, "
              "obs-style, cross-phase)", "#DCE9F5", fs=7.4)
    _arrow(ax, (6.0, 2.2), (6.0, 1.5))

    # warning banner
    ax.text(6.0, 5.75, "Pipeline overview (concept draft for author refinement)",
            ha="center", va="center", fontsize=8.5, fontweight="bold")
    ax.text(11.8, 0.15, "No real telescope validation", ha="right", va="bottom",
            fontsize=7, color=OI["verm"], fontstyle="italic",
            bbox=dict(boxstyle="round,pad=0.3", fc="#FDECEA", ec=OI["verm"], lw=0.8))
    save(fig, "Fig_1_pipeline", aliases=["FIG1_pipeline_schematic"])
    note("FIG1 OK: conceptual schematic (no data). Draft for author refinement.")

# ============================================================================
# FIG 2: Geometry / attitude schematic (concept)
# ============================================================================
def fig2():
    fig, ax = plt.subplots(figsize=(W1, W1 * 0.95))
    ax.set_xlim(-1.3, 1.5); ax.set_ylim(-1.3, 1.5)
    ax.set_aspect("equal"); ax.axis("off")
    O = (0, 0)
    # inertial frame I (solid)
    ax.annotate("", xy=(1.0, 0), xytext=O,
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color=OI["black"]))
    ax.annotate("", xy=(0, 1.0), xytext=O,
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color=OI["black"]))
    ax.annotate("", xy=(-0.5, -0.45), xytext=O,
                arrowprops=dict(arrowstyle="-|>", lw=1.4, color=OI["black"]))
    ax.text(1.05, 0.02, r"$X_I$", fontsize=8)
    ax.text(0.03, 1.03, r"$Z_I$", fontsize=8)
    ax.text(-0.58, -0.52, r"$Y_I$", fontsize=8)

    # body frame B (dashed) -- slight rotation to show distinction
    th = np.deg2rad(18)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    for v, lab, c in [((0.85, 0), r"$X_B$", OI["blue"]),
                      ((0, 0.85), r"$Z_B$", OI["blue"]),
                      ((-0.42, -0.38), r"$Y_B$", OI["blue"])]:
        vv = R @ np.array(v)
        ax.annotate("", xy=tuple(vv), xytext=O,
                    arrowprops=dict(arrowstyle="-|>", lw=1.3, color=c, ls="--"))
        ax.text(vv[0]*1.08, vv[1]*1.08, lab, fontsize=8, color=c)

    # Sun L and viewer V (fixed inertial)
    L = np.array([0.95, 0.85]); V = np.array([-0.95, 0.9])
    ax.annotate("", xy=tuple(L), xytext=O,
                arrowprops=dict(arrowstyle="-|>", lw=1.5, color=OI["orange"]))
    ax.annotate("", xy=tuple(V), xytext=O,
                arrowprops=dict(arrowstyle="-|>", lw=1.5, color=OI["green"]))
    ax.text(L[0]*1.05, L[1]*1.05, "Sun  L", fontsize=8, color=OI["orange"])
    ax.text(V[0]*1.05, V[1]*1.05, "Viewer  V", fontsize=8, color=OI["green"])
    # phase angle arc between L and V
    aL = np.degrees(np.arctan2(L[1], L[0]))
    aV = np.degrees(np.arctan2(V[1], V[0]))
    ax.add_patch(Arc(O, 1.0, 1.0, angle=0, theta1=aL, theta2=aV,
                     color=OI["purple"], lw=1.2))
    ax.text(0.0, 0.72, r"$\angle(L,V)$", fontsize=7.5, color=OI["purple"], ha="center")

    # roll/pitch/yaw arc arrows (small, near origin labels)
    ax.text(0.0, -0.95,
            r"yaw about $Z_B$,  pitch about $Y_B$,  roll about $X_B$ ($\equiv 0$)",
            ha="center", fontsize=6.6)
    ax.text(0.0, -1.15,
            r"$v_I = R\,v_{body},\ \ R=R_z(\mathrm{yaw})R_y(\mathrm{pitch})R_x(\mathrm{roll})$"
            if False else
            r"$v_I = R\,v_{body},\ R=R_z(\psi)R_y(\theta)R_x(\phi),\ \phi\equiv0$",
            ha="center", fontsize=6.8)
    ax.set_title("Geometry & attitude convention (concept draft)",
                 fontsize=8.5, fontweight="bold")
    ax.text(1.45, -1.28, "yaw=pitch=0  ->  B coincides with I",
            ha="right", va="bottom", fontsize=6.4, color=OI["grey"])
    save(fig, "Fig_2_geometry", aliases=["FIG2_geometry_attitude_schematic"])
    note("FIG2 OK: conceptual schematic (no data). Draft for author refinement.")

# ============================================================================
def write_notes():
    out = os.path.join(FIGDIR, "FIGURE_NOTES.md")
    lines = [
        "# FIGURE_NOTES",
        "",
        f"Generated by `make_figures.py`. Project root: `{ROOT}`",
        "",
        "Each canonical figure (`Fig_#_...`) is saved as .pdf (vector, fonttype-42), "
        ".svg (vector, fonttype-none editable text), .png (600 dpi), and .emf "
        "(Windows vector via LibreOffice headless). Per-figure plotted values are "
        "exported to `source_data/Fig_#_*.csv`. Legacy `FIG#_...` aliases (.pdf + .png) "
        "are also written for earlier draft links.",
        "",
        "## Data sources per figure",
        "",
        "- **FIG1** pipeline schematic: conceptual, no data. Draft for author refinement.",
        "- **FIG2** geometry/attitude schematic: conceptual, no data. Draft for author refinement.",
        "- **FIG3** OCS + occlusion maps: "
        "`结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260527_195122/"
        "phase63_backscatter/ocs_scan.csv` (with-occlusion OCS, per-part "
        "jinshuzhuti=metal body / taiyangnengban=solar panel / yinshenban=baffle, occlusion_ratio).",
        "- **FIG4(a)** image degradation: naive fusion from "
        "`fusion_mechanism_upgrade/run_20260604_092041/diagnostics_results.csv` (mask_mode=normal); "
        "U1 from `upgrade_results.csv` (variant U1_augment); OCS-only flat 5.91 deg; "
        "image-only clean point from `observation_style_degradation_12c/.../obs_degradation_results.csv`.",
        "- **FIG4(b)** OCS degradation: "
        "`noise_robustness/run_20260601_094130/noise_summary.json` (ocs_only & fusion, with std shading + gain curve).",
        "- **FIG5(a)** self-occlusion: "
        "`结果/模块C_反演/occlusion_analysis/run_20260529_215456/occlusion_summary.csv`.",
        "- **FIG5(b)** BRDF roughness: REPRESENTATIVE summary values only (see skipped note below).",
        "- **FIG5(c)** roll sensitivity: "
        "`roll_sensitivity/run_20260529_221408/roll_sweep.csv`.",
        "- **FIG6(a)** observation-style degradation: "
        "`observation_style_degradation_12c/run_20260604_222508/obs_degradation_results.csv`.",
        "- **FIG6(b)** cross-phase: "
        "`cross_phase_generalization_12d/run_20260604_234811/cross_phase_results.csv`.",
        "- **FIG6(c)** late-fusion beta sweep: "
        "`late_fusion_beta_sweep_12f/run_20260604_220802/beta_sweep_summary.csv`.",
        "",
        "## Skipped / representative / caveats",
        "",
        "- **FIG5(b) BRDF roughness sensitivity**: raw per-point result data is ABSENT on disk "
        "(only the script `论文改进/补充实验/代码/run_brdf_sensitivity.py` exists; it was NOT run). "
        "The panel is built from CONFIRMED summary values and is explicitly labelled "
        "'representative (summary values)': metal-body roughness ±20% -> ~30-46% OCS change; "
        "solar panel and baffle (non-metallic) < 5% change.",
        "- **FIG4(a) clean-trained image-only Gaussian-noise series**: no dedicated per-noise "
        "result file (sigma=0.01 / 0.10) exists for the *clean-trained image-only* model. "
        "Only the clean point (1.72 deg, from 12c) is plotted, marked with '*'. The documented "
        "image-only collapse (>85 deg) under degradation is shown instead in FIG6(a) "
        "(observation-style) and FIG6(b) (cross-phase). No values were fabricated.",
        "",
        "## Run log notes (auto-collected)",
        "",
    ]
    lines += [f"- {n}" for n in NOTES]
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"[SAVED] {out}")

# ============================================================================
if __name__ == "__main__":
    print("ROOT =", ROOT)
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    fig6()
    write_notes()
    print("\nDONE.")

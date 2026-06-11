"""Rank brightest attitudes and component contributions from an OCS scan CSV."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


PART_FIELD_CANDIDATES = {
    "jinshuzhuti": ["ocs_with_occ_jinshuzhuti", "metal_body_ocs_m2"],
    "taiyangnengban": ["ocs_with_occ_taiyangnengban", "solar_panel_ocs_m2"],
    "yinshenban": ["ocs_with_occ_yinshenban", "baffle_ocs_m2"],
}

TOTAL_FIELD_CANDIDATES = ["ocs_with_occ", "total_ocs_m2", "ocs_no_occ"]


def to_float(value: str | None) -> float:
    if value is None or value == "":
        return float("nan")
    return float(value)


def choose_field(headers: list[str], candidates: list[str]) -> str:
    for field in candidates:
        if field in headers:
            return field
    raise ValueError(f"None of these fields were found: {candidates}")


def delta_mag(ocs: float, ref_ocs: float) -> float:
    if ocs <= 0 or ref_ocs <= 0:
        return float("nan")
    return -2.5 * math.log10(ocs / ref_ocs)


def median(values: list[float]) -> float:
    values = sorted(values)
    n = len(values)
    if n == 0:
        return float("nan")
    mid = n // 2
    if n % 2:
        return values[mid]
    return 0.5 * (values[mid - 1] + values[mid])


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []
    return rows, headers


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to ocs_scan.csv or figure source CSV.")
    parser.add_argument("--outdir", required=True, help="Directory for output files.")
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()

    input_path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows, headers = read_rows(input_path)
    total_field = choose_field(headers, TOTAL_FIELD_CANDIDATES)
    part_fields = {
        part: choose_field(headers, candidates)
        for part, candidates in PART_FIELD_CANDIDATES.items()
    }

    enriched: list[dict[str, object]] = []
    for row in rows:
        total = to_float(row.get(total_field))
        if not math.isfinite(total):
            continue
        parts = {part: to_float(row.get(field)) for part, field in part_fields.items()}
        part_sum = sum(value for value in parts.values() if math.isfinite(value))
        record: dict[str, object] = {
            "yaw": row.get("yaw", ""),
            "pitch": row.get("pitch", ""),
            "roll": row.get("roll", ""),
            "total_ocs": total,
            "occlusion_ratio": row.get("occlusion_ratio", row.get("occlusion_ratio_frac", "")),
            "part_sum_ocs": part_sum,
        }
        for part, value in parts.items():
            record[f"{part}_ocs"] = value
            record[f"{part}_frac"] = value / total if total > 0 and math.isfinite(value) else float("nan")
        enriched.append(record)

    enriched.sort(key=lambda r: float(r["total_ocs"]), reverse=True)
    totals = [float(r["total_ocs"]) for r in enriched if float(r["total_ocs"]) > 0]
    max_ocs = max(totals)
    min_ocs = min(totals)
    med_ocs = median(totals)

    top_rows: list[dict[str, object]] = []
    for rank, record in enumerate(enriched[: args.top_k], start=1):
        out = {"rank": rank, **record}
        out["delta_mag_vs_max"] = delta_mag(float(record["total_ocs"]), max_ocs)
        out["delta_mag_vs_median"] = delta_mag(float(record["total_ocs"]), med_ocs)
        top_rows.append(out)

    top_fields = [
        "rank",
        "yaw",
        "pitch",
        "roll",
        "total_ocs",
        "delta_mag_vs_max",
        "delta_mag_vs_median",
        "occlusion_ratio",
        "part_sum_ocs",
        "jinshuzhuti_ocs",
        "jinshuzhuti_frac",
        "taiyangnengban_ocs",
        "taiyangnengban_frac",
        "yinshenban_ocs",
        "yinshenban_frac",
    ]
    write_csv(outdir / "phase63_topk_brightness.csv", top_rows, top_fields)

    component_rows: list[dict[str, object]] = []
    for part in PART_FIELD_CANDIDATES:
        part_values = [float(r[f"{part}_ocs"]) for r in enriched if math.isfinite(float(r[f"{part}_ocs"]))]
        top_by_part = max(enriched, key=lambda r, p=part: float(r[f"{p}_ocs"]))
        top_k_fracs = [
            float(r[f"{part}_frac"])
            for r in enriched[: args.top_k]
            if math.isfinite(float(r[f"{part}_frac"]))
        ]
        component_rows.append(
            {
                "component": part,
                "max_part_ocs": max(part_values),
                "median_part_ocs": median(part_values),
                "attitude_at_max_yaw": top_by_part.get("yaw", ""),
                "attitude_at_max_pitch": top_by_part.get("pitch", ""),
                "attitude_at_max_roll": top_by_part.get("roll", ""),
                "total_ocs_at_part_max": top_by_part.get("total_ocs", ""),
                "mean_fraction_in_total_topk": sum(top_k_fracs) / len(top_k_fracs),
            }
        )
    write_csv(
        outdir / "phase63_component_contribution.csv",
        component_rows,
        [
            "component",
            "max_part_ocs",
            "median_part_ocs",
            "attitude_at_max_yaw",
            "attitude_at_max_pitch",
            "attitude_at_max_roll",
            "total_ocs_at_part_max",
            "mean_fraction_in_total_topk",
        ],
    )

    brightest = enriched[0]
    dimmest = min(enriched, key=lambda r: float(r["total_ocs"]))
    max_vs_median = delta_mag(max_ocs, med_ocs)
    max_vs_min = delta_mag(max_ocs, min_ocs)
    summary = [
        "# phase63 OCS 最亮姿态摘要",
        "",
        f"输入文件：`{input_path}`",
        f"记录数：{len(enriched)}",
        f"总 OCS 字段：`{total_field}`",
        "",
        "## 总 OCS 动态范围",
        "",
        f"- 最大 OCS：{max_ocs:.8g}",
        f"- 中位 OCS：{med_ocs:.8g}",
        f"- 最小 OCS：{min_ocs:.8g}",
        f"- 最亮相对中位姿态：亮 {abs(max_vs_median):.3f} mag (Delta m={max_vs_median:.3f})",
        f"- 最亮相对最暗姿态：亮 {abs(max_vs_min):.3f} mag (Delta m={max_vs_min:.3f})",
        "",
        "## 最亮姿态",
        "",
        f"- yaw={brightest.get('yaw')}, pitch={brightest.get('pitch')}, roll={brightest.get('roll')}",
        f"- total OCS={float(brightest['total_ocs']):.8g}",
        f"- jinshuzhuti fraction={float(brightest['jinshuzhuti_frac']):.3f}",
        f"- taiyangnengban fraction={float(brightest['taiyangnengban_frac']):.3f}",
        f"- yinshenban fraction={float(brightest['yinshenban_frac']):.3f}",
        "",
        "## 最暗姿态",
        "",
        f"- yaw={dimmest.get('yaw')}, pitch={dimmest.get('pitch')}, roll={dimmest.get('roll')}",
        f"- total OCS={float(dimmest['total_ocs']):.8g}",
        "",
        "## 说明",
        "",
        "这里的 mag 是相对星等差，只反映 OCS 比值；未引入距离、波段太阳星等或绝对标定。",
    ]
    (outdir / "phase63_delta_mag_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

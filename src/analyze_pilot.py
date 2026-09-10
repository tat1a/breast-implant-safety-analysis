"""Build report-level pilot features, descriptive tables, and an SVG chart."""

from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_svg(path: Path, rows: list[dict]) -> None:
    width, left, top, row_h = 980, 360, 90, 38
    height = top + row_h * len(rows) + 75
    maximum = max((int(row["report_count"]) for row in rows), default=1)
    bars = []
    for index, row in enumerate(rows):
        y = top + index * row_h
        bar_width = 520 * int(row["report_count"]) / maximum
        label = html.escape(row["category"].replace("_", " ").title())
        bars.append(f'<text x="20" y="{y+20}" font-size="15">{label}</text>')
        bars.append(f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="24" rx="4" fill="#2563eb"/>')
        bars.append(f'<text x="{left+bar_width+10:.1f}" y="{y+18}" font-size="14">{row["report_count"]}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<text x="20" y="32" font-size="24" font-weight="700">Reported complication categories</text>
<text x="20" y="58" font-size="15" fill="#475569">Bounded pipeline pilot (n=20 reports) — counts are not incidence or comparative safety estimates</text>
{''.join(bars)}
<text x="20" y="{height-22}" font-size="13" fill="#64748b">A report may contribute to more than one category.</text>
</svg>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def analyze(normalized_dir: Path, cleaned_dir: Path, taxonomy_dir: Path, output_dir: Path) -> None:
    reports = read_csv(normalized_dir / "reports.csv")
    devices = read_csv(normalized_dir / "devices.csv")
    cleaned_reports = {row["mdr_report_key"]: row for row in read_csv(cleaned_dir / "report_lists_cleaned.csv")}
    category_rows = read_csv(taxonomy_dir / "report_complication_categories.csv")
    report_keys = {row["mdr_report_key"] for row in reports}
    device_codes: dict[str, set[str]] = defaultdict(set)
    categories: dict[str, set[str]] = defaultdict(set)
    for row in devices:
        if row["device_report_product_code"]:
            device_codes[row["mdr_report_key"]].add(row["device_report_product_code"])
    for row in category_rows:
        categories[row["mdr_report_key"]].add(row["category"])

    feature_rows = []
    for row in reports:
        key = row["mdr_report_key"]
        cleaned = cleaned_reports[key]
        feature_rows.append({
            "mdr_report_key": key,
            "date_received": row["date_received"],
            "date_of_event": row["date_of_event"],
            "event_type": row["event_type"],
            "report_source_code": row["report_source_code"],
            "product_codes_json": json.dumps(sorted(device_codes[key]), separators=(",", ":")),
            "followup_count": cleaned["followup_count"],
            "complication_categories_json": json.dumps(sorted(categories[key]), separators=(",", ":")),
            "complication_category_count": len(categories[key]),
        })

    category_counts = Counter(row["category"] for row in category_rows)
    category_summary = [
        {"category": category, "report_count": count, "pct_of_pilot_reports": round(100 * count / len(reports), 1)}
        for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    reports_per_code = Counter()
    category_code_pairs = Counter()
    for key in report_keys:
        for code in device_codes[key]:
            reports_per_code[code] += 1
            for category in categories[key]:
                category_code_pairs[(code, category)] += 1
    by_code = [
        {"product_code": code, "category": category, "report_count": count,
         "reports_with_code": reports_per_code[code], "pct_of_reports_with_code": round(100 * count / reports_per_code[code], 1)}
        for (code, category), count in sorted(category_code_pairs.items())
    ]
    followups = Counter(int(row["followup_count"]) for row in cleaned_reports.values())
    followup_rows = [{"followup_count": value, "report_count": count} for value, count in sorted(followups.items())]

    write_csv(output_dir / "pilot_report_features.csv", list(feature_rows[0]), feature_rows)
    write_csv(output_dir / "category_counts.csv", ["category", "report_count", "pct_of_pilot_reports"], category_summary)
    write_csv(output_dir / "category_by_product_code.csv", ["product_code", "category", "report_count", "reports_with_code", "pct_of_reports_with_code"], by_code)
    write_csv(output_dir / "followup_distribution.csv", ["followup_count", "report_count"], followup_rows)
    make_svg(output_dir / "figures" / "pilot_category_counts.svg", category_summary)
    qc = {
        "scope": "bounded pilot only",
        "report_rows": len(reports),
        "feature_rows": len(feature_rows),
        "unique_feature_report_keys": len({row["mdr_report_key"] for row in feature_rows}),
        "reports_without_product_code": sum(not device_codes[key] for key in report_keys),
        "reports_without_complication_category": sum(not categories[key] for key in report_keys),
        "category_report_links": sum(category_counts.values()),
        "gate_passed": len(reports) == len(feature_rows) == len({row["mdr_report_key"] for row in feature_rows}),
        "warning": "Pilot percentages are descriptive pipeline outputs, not incidence, causality, unique-patient/device, or comparative-safety estimates.",
    }
    (output_dir / "analysis_qc_summary.json").write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build bounded-pilot descriptive outputs.")
    parser.add_argument("--normalized-dir", type=Path, default=Path("data/processed/pilot_normalized"))
    parser.add_argument("--cleaned-dir", type=Path, default=Path("data/processed/pilot_cleaned"))
    parser.add_argument("--taxonomy-dir", type=Path, default=Path("data/processed/pilot_taxonomy"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/pilot_analysis"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    analyze(args.normalized_dir, args.cleaned_dir, args.taxonomy_dir, args.output_dir)
    print(f"Pilot analysis outputs: {args.output_dir}")

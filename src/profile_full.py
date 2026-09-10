"""Streaming data-quality profile and taxonomy discovery for the full cohort."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from src.profile_pilot import bucket_count, is_missing

TABLES = ("reports", "devices", "patients")
CATEGORICAL_FIELDS = {
    "reports": ("event_type", "report_source_code", "reporter_occupation_code",
                "reporter_country_code", "event_location"),
    "devices": ("device_report_product_code", "manufacturer_d_country",
                "device_availability", "device_evaluated_by_manufacturer"),
    "patients": ("patient_age_status", "patient_sex", "patient_ethnicity", "patient_race"),
}
REPORT_YEAR_FIELDS = ("date_of_event", "report_source_code", "reporter_occupation_code",
                      "reporter_country_code", "event_location", "product_problems_json")
LABEL_FIELDS = {"reports": ("product_problems_json",), "patients": ("patient_problems_json",)}


def iter_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def parse_list(value: str | None) -> list[str]:
    if not value or not value.strip():
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError("Expected JSON list field")
    return [str(item).strip() for item in parsed if item is not None and str(item).strip()]


def write_csv(path: Path, fields: list[str], rows) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def profile_full(input_dir: Path, output_dir: Path) -> Path:
    normalization_qc = json.loads((input_dir / "normalization_qc.json").read_text(encoding="utf-8"))
    if normalization_qc.get("qc_gate_passed") is not True:
        raise ValueError("Full normalization QC gate has not passed")
    output_dir.mkdir(parents=True, exist_ok=True)
    staging = output_dir / "label_profile_staging.sqlite"
    if staging.exists():
        staging.unlink()
    connection = sqlite3.connect(staging)
    connection.execute("CREATE TABLE label_report (source_field TEXT, raw_label TEXT, report_key TEXT, PRIMARY KEY(source_field, raw_label, report_key))")

    row_counts = Counter()
    missing_counts: dict[str, Counter] = defaultdict(Counter)
    fields_by_table: dict[str, list[str]] = {}
    categories: dict[tuple[str, str], Counter] = defaultdict(Counter)
    multiplicity = {"devices_per_report": Counter(), "patient_entries_per_report": Counter()}
    years = Counter()
    yearly_missing: dict[tuple[str, str], int] = Counter()
    label_occurrences = Counter()

    try:
        for table in TABLES:
            for row in iter_csv(input_dir / f"{table}.csv"):
                row_counts[table] += 1
                if table not in fields_by_table:
                    fields_by_table[table] = list(row)
                for field, value in row.items():
                    if is_missing(value): missing_counts[table][field] += 1
                for field in CATEGORICAL_FIELDS[table]:
                    value = (row.get(field) or "").strip() or "[Missing]"
                    categories[(table, field)][value] += 1
                if table == "reports":
                    multiplicity["devices_per_report"][bucket_count(row.get("device_rows_extracted"))] += 1
                    multiplicity["patient_entries_per_report"][bucket_count(row.get("patient_rows_extracted"))] += 1
                    date = (row.get("date_received") or "").strip()
                    year = date[:4] if len(date) >= 4 and date[:4].isdigit() else "[Invalid/Missing]"
                    years[year] += 1
                    for field in REPORT_YEAR_FIELDS:
                        if is_missing(row.get(field)): yearly_missing[(year, field)] += 1
                for field in LABEL_FIELDS.get(table, ()):
                    values = parse_list(row.get(field))
                    for label in values:
                        label_occurrences[(field, label)] += 1
                        connection.execute("INSERT OR IGNORE INTO label_report VALUES (?, ?, ?)",
                                           (field, label, row["mdr_report_key"]))
            connection.commit()

        missing_rows = []
        for table in TABLES:
            total = row_counts[table]
            for field in fields_by_table[table]:
                missing = missing_counts[table][field]
                missing_rows.append({"table": table, "field": field, "row_count": total,
                    "nonmissing_count": total - missing, "missing_count": missing,
                    "missing_pct": round(100 * missing / total, 2) if total else 0})

        categorical_rows = []
        for (table, field), counts in categories.items():
            total = row_counts[table]
            for value, count in counts.most_common():
                categorical_rows.append({"table": table, "field": field, "value": value,
                    "count": count, "pct_of_table_rows": round(100 * count / total, 2) if total else 0})

        multiplicity_rows = []
        for metric, counts in multiplicity.items():
            for category in ("0", "1", ">1", "invalid"):
                count = counts[category]
                multiplicity_rows.append({"metric": metric, "category": category,
                    "report_count": count, "pct_of_reports": round(100 * count / row_counts["reports"], 2)})

        label_rows = []
        query = "SELECT source_field, raw_label, COUNT(*) FROM label_report GROUP BY source_field, raw_label ORDER BY COUNT(*) DESC, raw_label"
        for field, label, report_count in connection.execute(query):
            label_rows.append({"source_field": field, "raw_label": label,
                "report_count": report_count, "item_occurrences": label_occurrences[(field, label)],
                "pct_of_reports": round(100 * report_count / row_counts["reports"], 4)})

        yearly_rows = []
        for year in sorted(years):
            total = years[year]
            for field in REPORT_YEAR_FIELDS:
                missing = yearly_missing[(year, field)]
                yearly_rows.append({"year": year, "field": field, "report_count": total,
                    "nonmissing_count": total - missing, "missing_count": missing,
                    "missing_pct": round(100 * missing / total, 2) if total else 0})

        write_csv(output_dir / "field_missingness.csv", ["table","field","row_count","nonmissing_count","missing_count","missing_pct"], missing_rows)
        write_csv(output_dir / "categorical_overview.csv", ["table","field","value","count","pct_of_table_rows"], categorical_rows)
        write_csv(output_dir / "multiplicity_summary.csv", ["metric","category","report_count","pct_of_reports"], multiplicity_rows)
        write_csv(output_dir / "complication_label_inventory.csv", ["source_field","raw_label","report_count","item_occurrences","pct_of_reports"], label_rows)
        write_csv(output_dir / "yearly_report_missingness.csv", ["year","field","report_count","nonmissing_count","missing_count","missing_pct"], yearly_rows)
    finally:
        connection.close()
        if staging.exists(): staging.unlink()

    expected = {"reports": normalization_qc["unique_report_rows"], "devices": normalization_qc["device_rows"], "patients": normalization_qc["patient_rows"]}
    summary = {"scope": normalization_qc["scope"], "row_counts": dict(row_counts),
        "expected_row_counts": expected, "row_count_reconciliation": {k: row_counts[k] - expected[k] for k in TABLES},
        "distinct_complication_labels": len(label_occurrences), "years_observed": dict(sorted(years.items())),
        "qc_gate_passed": all(row_counts[k] == expected[k] for k in TABLES),
        "warning": "Profile percentages describe database-row completeness/reporting patterns, not incidence, causality, or comparative safety."}
    path = output_dir / "profile_summary.json"
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args():
    parser = argparse.ArgumentParser(description="Stream-profile the normalized full cohort.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/processed/full_normalized"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/full_profile"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args(); print(f"Profile summary: {profile_full(args.input_dir, args.output_dir)}")

"""Profile completeness, multiplicity, and selected categories in pilot tables."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def is_missing(value: str | None) -> bool:
    if value is None or not value.strip():
        return True
    return value.strip() in {"[]", "{}", "null"}


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def field_profile(table: str, rows: list[dict[str, str]]) -> list[dict]:
    if not rows:
        return []
    result = []
    total = len(rows)
    for field in rows[0]:
        missing = sum(is_missing(row.get(field)) for row in rows)
        result.append({
            "table": table,
            "field": field,
            "row_count": total,
            "nonmissing_count": total - missing,
            "missing_count": missing,
            "missing_pct": round(100.0 * missing / total, 1),
        })
    return result


def bucket_count(value: str | None) -> str:
    try:
        count = int(value or "0")
    except ValueError:
        return "invalid"
    if count == 0:
        return "0"
    if count == 1:
        return "1"
    return ">1"


def frequency_rows(table: str, field: str, rows: list[dict[str, str]]) -> list[dict]:
    counts = Counter((row.get(field) or "").strip() or "[Missing]" for row in rows)
    total = len(rows)
    return [
        {
            "table": table,
            "field": field,
            "value": value,
            "count": count,
            "pct_of_table_rows": round(100.0 * count / total, 1) if total else 0.0,
        }
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def profile(input_dir: Path, output_dir: Path) -> Path:
    tables = {name: read_csv(input_dir / f"{name}.csv") for name in ("reports", "devices", "patients")}
    reports, devices, patients = tables["reports"], tables["devices"], tables["patients"]

    missingness = []
    for table, rows in tables.items():
        missingness.extend(field_profile(table, rows))

    device_buckets = Counter(bucket_count(row.get("device_rows_extracted")) for row in reports)
    patient_buckets = Counter(bucket_count(row.get("patient_rows_extracted")) for row in reports)
    multiplicity = []
    for entity, buckets in (("devices_per_report", device_buckets), ("patient_entries_per_report", patient_buckets)):
        for bucket in ("0", "1", ">1", "invalid"):
            count = buckets.get(bucket, 0)
            multiplicity.append({
                "metric": entity,
                "category": bucket,
                "report_count": count,
                "pct_of_reports": round(100.0 * count / len(reports), 1) if reports else 0.0,
            })

    categories = []
    for table, field in (
        ("reports", "event_type"),
        ("reports", "report_source_code"),
        ("reports", "reporter_occupation_code"),
        ("devices", "device_report_product_code"),
        ("patients", "patient_age_status"),
        ("patients", "patient_sex"),
    ):
        categories.extend(frequency_rows(table, field, tables[table]))

    report_keys = {row["mdr_report_key"] for row in reports}
    device_keys = {row["mdr_report_key"] for row in devices}
    patient_keys = {row["mdr_report_key"] for row in patients}
    expected_devices = sum(int(row["device_rows_extracted"] or 0) for row in reports)
    expected_patients = sum(int(row["patient_rows_extracted"] or 0) for row in reports)
    summary = {
        "scope": "bounded pilot only",
        "report_rows": len(reports),
        "device_rows": len(devices),
        "patient_rows": len(patients),
        "unique_report_keys": len(report_keys),
        "reports_with_multiple_devices": device_buckets.get(">1", 0),
        "reports_with_multiple_patient_entries": patient_buckets.get(">1", 0),
        "reports_without_device_rows": device_buckets.get("0", 0),
        "reports_without_patient_rows": patient_buckets.get("0", 0),
        "device_row_reconciliation_difference": len(devices) - expected_devices,
        "patient_row_reconciliation_difference": len(patients) - expected_patients,
        "orphan_device_report_keys": sorted(device_keys - report_keys),
        "orphan_patient_report_keys": sorted(patient_keys - report_keys),
        "missingness_definition": "blank, [], {}, or null string",
        "warning": "Pilot percentages are pipeline checks and must not be presented as population or device-risk estimates.",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "field_missingness.csv", ["table", "field", "row_count", "nonmissing_count", "missing_count", "missing_pct"], missingness)
    write_csv(output_dir / "multiplicity_summary.csv", ["metric", "category", "report_count", "pct_of_reports"], multiplicity)
    write_csv(output_dir / "categorical_overview.csv", ["table", "field", "value", "count", "pct_of_table_rows"], categories)
    summary_path = output_dir / "profile_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile normalized pilot tables.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/processed/pilot_normalized"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/pilot_profile"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Profile summary: {profile(args.input_dir, args.output_dir)}")

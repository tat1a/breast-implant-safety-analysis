"""Create auditable cleaned list fields from normalized pilot tables."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


SOURCE_CANONICAL = {
    "CONSUMER": "CONSUMER",
    "DISTRIBUTOR": "DISTRIBUTOR",
    "FOREIGN": "FOREIGN",
    "HEALTH PROFESSIONAL": "HEALTH PROFESSIONAL",
    "OTHER": "OTHER",
}
KNOWN_OUTCOMES = {"Other", "Required Intervention"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_json_list(value: str | None) -> list:
    if value is None or not value.strip():
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError("Expected a JSON list")
    return parsed


def clean_list(items: list, *, deduplicate: bool = True) -> tuple[list[str], dict[str, int]]:
    cleaned: list[str] = []
    seen: set[str] = set()
    blank_removed = 0
    duplicate_removed = 0
    for item in items:
        if item is None or (isinstance(item, str) and not item.strip()):
            blank_removed += 1
            continue
        text = str(item).strip()
        if deduplicate and text in seen:
            duplicate_removed += 1
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned, {
        "input_items": len(items),
        "blank_items_removed": blank_removed,
        "duplicate_items_removed": duplicate_removed,
        "output_items": len(cleaned),
    }


def json_text(items: list[str]) -> str:
    return json.dumps(items, ensure_ascii=False, separators=(",", ":"))


def clean_source_types(items: list) -> tuple[list[str], list[str], dict[str, int]]:
    stripped, qc = clean_list(items)
    cleaned: list[str] = []
    unknown: list[str] = []
    seen: set[str] = set()
    for value in stripped:
        canonical = SOURCE_CANONICAL.get(value.upper())
        output = canonical or value
        if canonical is None:
            unknown.append(value)
        if output not in seen:
            cleaned.append(output)
            seen.add(output)
    qc["output_items"] = len(cleaned)
    return cleaned, unknown, qc


def add_qc(qc_rows: list[dict], table: str, row_id: str, field: str, qc: dict[str, int]) -> None:
    qc_rows.append({"table": table, "row_id": row_id, "field": field, **qc})


def clean(input_dir: Path, output_dir: Path) -> None:
    reports = read_csv(input_dir / "reports.csv")
    patients = read_csv(input_dir / "patients.csv")
    report_rows: list[dict] = []
    patient_rows: list[dict] = []
    qc_rows: list[dict] = []
    unknown_counts: Counter[tuple[str, str, str, str]] = Counter()

    for row in reports:
        key = row["mdr_report_key"]
        report_types, report_qc = clean_list(parse_json_list(row.get("type_of_report_json")), deduplicate=False)
        sources, unknown_sources, source_qc = clean_source_types(parse_json_list(row.get("source_type_json")))
        problems, problem_qc = clean_list(parse_json_list(row.get("product_problems_json")))
        add_qc(qc_rows, "reports", key, "type_of_report_json", report_qc)
        add_qc(qc_rows, "reports", key, "source_type_json", source_qc)
        add_qc(qc_rows, "reports", key, "product_problems_json", problem_qc)
        for value in unknown_sources:
            unknown_counts[("reports", "source_type_json", value, "not in reviewed source-type mapping")] += 1
        report_rows.append({
            "mdr_report_key": key,
            "type_of_report_cleaned_json": json_text(report_types),
            "initial_submission_present": str(any(value.casefold() == "initial submission" for value in report_types)).lower(),
            "followup_count": sum(value.casefold() == "followup" for value in report_types),
            "source_type_cleaned_json": json_text(sources),
            "product_problems_cleaned_json": json_text(problems),
        })

    for row in patients:
        row_id = row["patient_row_id"]
        outcomes, outcome_qc = clean_list(parse_json_list(row.get("outcomes_json")))
        patient_problems, problem_qc = clean_list(parse_json_list(row.get("patient_problems_json")))
        treatments, treatment_qc = clean_list(parse_json_list(row.get("treatments_json")))
        add_qc(qc_rows, "patients", row_id, "outcomes_json", outcome_qc)
        add_qc(qc_rows, "patients", row_id, "patient_problems_json", problem_qc)
        add_qc(qc_rows, "patients", row_id, "treatments_json", treatment_qc)
        for value in outcomes:
            if value not in KNOWN_OUTCOMES:
                unknown_counts[("patients", "outcomes_json", value, "not in reviewed outcome mapping")] += 1
        patient_rows.append({
            "patient_row_id": row_id,
            "mdr_report_key": row["mdr_report_key"],
            "outcomes_cleaned_json": json_text(outcomes),
            "patient_problems_cleaned_json": json_text(patient_problems),
            "treatments_cleaned_json": json_text(treatments),
        })

    unknown_rows = [
        {"table": table, "field": field, "raw_value": value, "reason": reason, "row_count": count}
        for (table, field, value, reason), count in sorted(unknown_counts.items())
    ]
    write_csv(output_dir / "report_lists_cleaned.csv", list(report_rows[0]), report_rows)
    write_csv(output_dir / "patient_lists_cleaned.csv", list(patient_rows[0]), patient_rows)
    write_csv(output_dir / "list_cleaning_qc.csv", ["table", "row_id", "field", "input_items", "blank_items_removed", "duplicate_items_removed", "output_items"], qc_rows)
    write_csv(output_dir / "unknown_values.csv", ["table", "field", "raw_value", "reason", "row_count"], unknown_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean normalized pilot JSON-list fields without overwriting source tables.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/processed/pilot_normalized"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/pilot_cleaned"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    clean(args.input_dir, args.output_dir)
    print(f"Cleaned pilot lists: {args.output_dir}")

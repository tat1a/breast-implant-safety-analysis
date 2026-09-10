"""Normalize bounded raw openFDA pages into linked analytical CSV tables.

No narrative text is exported. Raw source files remain unchanged.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Iterable

AGE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(YR|MO|WK|DA|HR)\s*$", re.IGNORECASE)
AGE_TO_YEARS = {
    "YR": 1.0,
    "MO": 1.0 / 12.0,
    "WK": 7.0 / 365.25,
    "DA": 1.0 / 365.25,
    "HR": 1.0 / (365.25 * 24.0),
}

REPORT_FIELDS = [
    "mdr_report_key", "report_number", "date_received", "date_of_event",
    "event_type", "adverse_event_flag", "product_problem_flag",
    "report_source_code", "reporter_occupation_code", "reporter_country_code",
    "event_location", "initial_report_to_fda", "type_of_report_json",
    "source_type_json", "product_problems_json", "number_devices_reported",
    "number_patients_reported", "device_rows_extracted", "patient_rows_extracted",
    "source_file",
]
DEVICE_FIELDS = [
    "device_row_id", "mdr_report_key", "device_index", "device_sequence_number",
    "device_report_product_code", "brand_name", "generic_name",
    "manufacturer_d_name", "manufacturer_d_country", "model_number",
    "catalog_number", "implant_date_year", "date_removed_year",
    "device_operator", "device_availability", "device_evaluated_by_manufacturer",
    "openfda_device_name", "openfda_medical_specialty", "openfda_regulation_number",
    "openfda_device_class", "source_file",
]
PATIENT_FIELDS = [
    "patient_row_id", "mdr_report_key", "patient_index", "patient_sequence_number",
    "patient_age_raw", "patient_age_years", "patient_age_status", "patient_sex",
    "patient_weight_raw", "patient_ethnicity", "patient_race",
    "patient_problems_json", "outcomes_json", "treatments_json", "source_file",
]


def json_list(value: object) -> str:
    """Store list-like values consistently without losing boundaries."""
    if value is None or value == "":
        items: list[object] = []
    elif isinstance(value, list):
        items = value
    else:
        items = [value]
    return json.dumps(items, ensure_ascii=False, separators=(",", ":"))


def parse_optional_int(value: object) -> int | str:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return ""


def parse_age(raw: object) -> tuple[float | str, str]:
    value = "" if raw is None else str(raw).strip()
    if not value:
        return "", "missing"
    match = AGE_RE.match(value)
    if not match:
        return "", "unparsed"
    years = float(match.group(1)) * AGE_TO_YEARS[match.group(2).upper()]
    if not 0 <= years <= 120:
        return "", "invalid_range"
    return round(years, 4), "valid"


def load_records(input_dir: Path) -> Iterable[tuple[dict, str]]:
    pages = sorted(input_dir.glob("*/page_*.json"))
    if not pages:
        pages = sorted(input_dir.glob("page_*.json"))
    if not pages:
        raise FileNotFoundError(f"No page_*.json files found under {input_dir}")
    for page in pages:
        payload = json.loads(page.read_text(encoding="utf-8"))
        for record in payload.get("results", []):
            yield record, str(page.relative_to(input_dir))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize(input_dir: Path, output_dir: Path) -> Path:
    reports: list[dict] = []
    devices: list[dict] = []
    patients: list[dict] = []
    report_keys: set[str] = set()

    for record, source_file in load_records(input_dir):
        key = str(record.get("mdr_report_key", "")).strip()
        if not key:
            raise ValueError(f"Missing mdr_report_key in {source_file}")
        if key in report_keys:
            raise ValueError(f"Duplicate mdr_report_key across input pages: {key}")
        report_keys.add(key)
        record_devices = record.get("device") or []
        record_patients = record.get("patient") or []

        reports.append({
            "mdr_report_key": key,
            "report_number": record.get("report_number", ""),
            "date_received": record.get("date_received", ""),
            "date_of_event": record.get("date_of_event", ""),
            "event_type": record.get("event_type", ""),
            "adverse_event_flag": record.get("adverse_event_flag", ""),
            "product_problem_flag": record.get("product_problem_flag", ""),
            "report_source_code": record.get("report_source_code", ""),
            "reporter_occupation_code": record.get("reporter_occupation_code", ""),
            "reporter_country_code": record.get("reporter_country_code", ""),
            "event_location": record.get("event_location", ""),
            "initial_report_to_fda": record.get("initial_report_to_fda", ""),
            "type_of_report_json": json_list(record.get("type_of_report")),
            "source_type_json": json_list(record.get("source_type")),
            "product_problems_json": json_list(record.get("product_problems")),
            "number_devices_reported": parse_optional_int(record.get("number_devices_in_event")),
            "number_patients_reported": parse_optional_int(record.get("number_patients_in_event")),
            "device_rows_extracted": len(record_devices),
            "patient_rows_extracted": len(record_patients),
            "source_file": source_file,
        })

        for index, device in enumerate(record_devices, start=1):
            openfda = device.get("openfda") or {}
            sequence = str(device.get("device_sequence_number", "")).strip()
            devices.append({
                "device_row_id": f"{key}:device:{sequence or index}:{index}",
                "mdr_report_key": key,
                "device_index": index,
                "device_sequence_number": sequence,
                "device_report_product_code": device.get("device_report_product_code", ""),
                "brand_name": device.get("brand_name", ""),
                "generic_name": device.get("generic_name", ""),
                "manufacturer_d_name": device.get("manufacturer_d_name", ""),
                "manufacturer_d_country": device.get("manufacturer_d_country", ""),
                "model_number": device.get("model_number", ""),
                "catalog_number": device.get("catalog_number", ""),
                "implant_date_year": device.get("implant_date_year", ""),
                "date_removed_year": device.get("date_removed_year", ""),
                "device_operator": device.get("device_operator", ""),
                "device_availability": device.get("device_availability", ""),
                "device_evaluated_by_manufacturer": device.get("device_evaluated_by_manufacturer", ""),
                "openfda_device_name": openfda.get("device_name", ""),
                "openfda_medical_specialty": openfda.get("medical_specialty_description", ""),
                "openfda_regulation_number": openfda.get("regulation_number", ""),
                "openfda_device_class": openfda.get("device_class", ""),
                "source_file": source_file,
            })

        for index, patient in enumerate(record_patients, start=1):
            raw_age = patient.get("patient_age", "")
            age_years, age_status = parse_age(raw_age)
            sequence = str(patient.get("patient_sequence_number", "")).strip()
            patients.append({
                "patient_row_id": f"{key}:patient:{sequence or index}:{index}",
                "mdr_report_key": key,
                "patient_index": index,
                "patient_sequence_number": sequence,
                "patient_age_raw": raw_age,
                "patient_age_years": age_years,
                "patient_age_status": age_status,
                "patient_sex": patient.get("patient_sex", ""),
                "patient_weight_raw": patient.get("patient_weight", ""),
                "patient_ethnicity": patient.get("patient_ethnicity", ""),
                "patient_race": patient.get("patient_race", ""),
                "patient_problems_json": json_list(patient.get("patient_problems")),
                "outcomes_json": json_list(patient.get("sequence_number_outcome")),
                "treatments_json": json_list(patient.get("sequence_number_treatment")),
                "source_file": source_file,
            })

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "reports.csv", REPORT_FIELDS, reports)
    write_csv(output_dir / "devices.csv", DEVICE_FIELDS, devices)
    write_csv(output_dir / "patients.csv", PATIENT_FIELDS, patients)
    qc = {
        "report_rows": len(reports),
        "unique_report_keys": len(report_keys),
        "device_rows": len(devices),
        "patient_rows": len(patients),
        "orphan_device_foreign_keys": sorted({d["mdr_report_key"] for d in devices} - report_keys),
        "orphan_patient_foreign_keys": sorted({p["mdr_report_key"] for p in patients} - report_keys),
        "patient_age_status_counts": {
            status: sum(p["patient_age_status"] == status for p in patients)
            for status in sorted({p["patient_age_status"] for p in patients})
        },
        "narratives_exported": False,
    }
    qc_path = output_dir / "normalization_qc.json"
    qc_path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    return qc_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize bounded openFDA pilot pages.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/pagination_pilot"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/pilot_normalized"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"QC summary: {normalize(args.input_dir, args.output_dir)}")

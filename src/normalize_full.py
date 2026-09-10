"""Normalize completed FTR/FWM extractions into deduplicated linked CSV tables."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from src.normalize_pilot import (
    DEVICE_FIELDS, PATIENT_FIELDS, REPORT_FIELDS, json_list, parse_age,
    parse_optional_int,
)

FULL_REPORT_FIELDS = REPORT_FIELDS[:-1] + ["query_product_codes_json", "source_files_json"]


def canonical_digest(record: dict) -> str:
    payload = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_completed_run(run_dir: Path) -> tuple[dict, list[Path]]:
    checkpoint_path = run_dir / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if checkpoint.get("status") != "complete" or checkpoint.get("qc_gate_passed") is not True:
        raise ValueError(f"Input extraction is not QC-complete: {checkpoint_path}")
    pages = []
    for page in checkpoint.get("pages", []):
        path = run_dir / page["file"]
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != page.get("sha256"):
            raise ValueError(f"Raw page checksum mismatch: {path}")
        pages.append(path)
    return checkpoint, pages


def iter_records(input_dir: Path):
    for code in ("FTR", "FWM"):
        run_dir = input_dir / f"{code}_20200101_20251231"
        checkpoint, pages = load_completed_run(run_dir)
        for path in pages:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            for record in parsed.get("results", []):
                yield code, record, str(path.relative_to(input_dir)), checkpoint


def report_row(record: dict, key: str, devices: list, patients: list,
               codes: set[str], sources: list[str]) -> dict:
    return {
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
        "device_rows_extracted": len(devices),
        "patient_rows_extracted": len(patients),
        "query_product_codes_json": json_list(sorted(codes)),
        "source_files_json": json_list(sources),
    }


def device_rows(record: dict, key: str, source: str):
    for index, device in enumerate(record.get("device") or [], start=1):
        openfda = device.get("openfda") or {}
        sequence = str(device.get("device_sequence_number", "")).strip()
        yield {
            "device_row_id": f"{key}:device:{sequence or index}:{index}", "mdr_report_key": key,
            "device_index": index, "device_sequence_number": sequence,
            "device_report_product_code": device.get("device_report_product_code", ""),
            "brand_name": device.get("brand_name", ""), "generic_name": device.get("generic_name", ""),
            "manufacturer_d_name": device.get("manufacturer_d_name", ""),
            "manufacturer_d_country": device.get("manufacturer_d_country", ""),
            "model_number": device.get("model_number", ""), "catalog_number": device.get("catalog_number", ""),
            "implant_date_year": device.get("implant_date_year", ""), "date_removed_year": device.get("date_removed_year", ""),
            "device_operator": device.get("device_operator", ""), "device_availability": device.get("device_availability", ""),
            "device_evaluated_by_manufacturer": device.get("device_evaluated_by_manufacturer", ""),
            "openfda_device_name": openfda.get("device_name", ""),
            "openfda_medical_specialty": openfda.get("medical_specialty_description", ""),
            "openfda_regulation_number": openfda.get("regulation_number", ""),
            "openfda_device_class": openfda.get("device_class", ""), "source_file": source,
        }


def patient_rows(record: dict, key: str, source: str):
    for index, patient in enumerate(record.get("patient") or [], start=1):
        raw_age = patient.get("patient_age", "")
        age_years, age_status = parse_age(raw_age)
        sequence = str(patient.get("patient_sequence_number", "")).strip()
        yield {
            "patient_row_id": f"{key}:patient:{sequence or index}:{index}", "mdr_report_key": key,
            "patient_index": index, "patient_sequence_number": sequence,
            "patient_age_raw": raw_age, "patient_age_years": age_years, "patient_age_status": age_status,
            "patient_sex": patient.get("patient_sex", ""), "patient_weight_raw": patient.get("patient_weight", ""),
            "patient_ethnicity": patient.get("patient_ethnicity", ""), "patient_race": patient.get("patient_race", ""),
            "patient_problems_json": json_list(patient.get("patient_problems")),
            "outcomes_json": json_list(patient.get("sequence_number_outcome")),
            "treatments_json": json_list(patient.get("sequence_number_treatment")), "source_file": source,
        }


def normalize_full(input_dir: Path, output_dir: Path) -> Path:
    metadata: dict[str, dict] = {}
    input_counts = Counter()
    for code, record, source, _ in iter_records(input_dir):
        key = str(record.get("mdr_report_key", "")).strip()
        if not key:
            raise ValueError(f"Missing mdr_report_key in {source}")
        input_counts[code] += 1
        digest = canonical_digest(record)
        if key not in metadata:
            metadata[key] = {"digest": digest, "codes": {code}, "sources": [source]}
        else:
            if metadata[key]["digest"] != digest:
                raise ValueError(f"Conflicting payloads for cross-code report {key}")
            metadata[key]["codes"].add(code)
            metadata[key]["sources"].append(source)

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {"reports": output_dir / "reports.csv", "devices": output_dir / "devices.csv", "patients": output_dir / "patients.csv"}
    temps = {name: path.with_suffix(".csv.tmp") for name, path in paths.items()}
    handles = {}
    try:
        for name, fields in (("reports", FULL_REPORT_FIELDS), ("devices", DEVICE_FIELDS), ("patients", PATIENT_FIELDS)):
            handles[name] = temps[name].open("w", newline="", encoding="utf-8-sig")
            writer = csv.DictWriter(handles[name], fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            handles[name + "_writer"] = writer

        emitted = set()
        device_count = patient_count = 0
        age_counts = Counter()
        for _, record, source, _ in iter_records(input_dir):
            key = str(record.get("mdr_report_key", "")).strip()
            if key in emitted:
                continue
            emitted.add(key)
            devices = list(record.get("device") or [])
            patients = list(record.get("patient") or [])
            meta = metadata[key]
            handles["reports_writer"].writerow(report_row(record, key, devices, patients, meta["codes"], meta["sources"]))
            for row in device_rows(record, key, source):
                handles["devices_writer"].writerow(row); device_count += 1
            for row in patient_rows(record, key, source):
                handles["patients_writer"].writerow(row); patient_count += 1; age_counts[row["patient_age_status"]] += 1
    finally:
        for name in ("reports", "devices", "patients"):
            if name in handles:
                handles[name].close()
    for name in paths:
        temps[name].replace(paths[name])

    overlap = sum(meta["codes"] == {"FTR", "FWM"} for meta in metadata.values())
    qc = {
        "scope": "full FTR/FWM cohort, date_received 2020-01-01 through 2025-12-31",
        "input_records_by_query_code": dict(input_counts),
        "input_records_total": sum(input_counts.values()),
        "unique_report_rows": len(metadata),
        "cross_code_overlap_reports": overlap,
        "reconciliation_difference": sum(input_counts.values()) - len(metadata) - overlap,
        "device_rows": device_count, "patient_rows": patient_count,
        "orphan_device_foreign_keys": 0, "orphan_patient_foreign_keys": 0,
        "patient_age_status_counts": dict(sorted(age_counts.items())),
        "narratives_exported": False,
        "qc_gate_passed": sum(input_counts.values()) - len(metadata) == overlap,
        "warning": "Rows describe MDR reports/entries, not unique patients, devices, incidence, causality, or comparative safety.",
    }
    qc_path = output_dir / "normalization_qc.json"
    qc_path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    return qc_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize the completed full FTR/FWM extraction.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/full_extraction"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/full_normalized"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"QC summary: {normalize_full(args.input_dir, args.output_dir)}")

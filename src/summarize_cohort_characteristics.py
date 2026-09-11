"""Summarize report, patient-entry, and device-entry characteristics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

WARNING = "Describes MDR reports/entries and reporting patterns; not unique patients/devices, incidence, causality, or comparative safety."


def parse_list(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    parsed = json.loads(str(value) or "[]")
    if not isinstance(parsed, list):
        raise ValueError("Expected JSON list")
    return [str(item).strip() for item in parsed if item is not None and str(item).strip()]


def categorical_summary(frame: pd.DataFrame, field: str, denominator: int) -> pd.DataFrame:
    values = frame[field].fillna("").astype(str).str.strip().replace("", "[Missing]")
    result = values.value_counts(dropna=False).rename_axis("value").reset_index(name="row_count")
    result["pct_of_rows"] = (100 * result["row_count"] / denominator).round(2)
    result.insert(0, "field", field)
    return result


def summarize(
    analytic_dir: Path,
    normalized_dir: Path,
    reporting_dir: Path,
    output_dir: Path,
) -> Path:
    reports = pd.read_csv(analytic_dir / "report_analysis.csv", low_memory=False)
    patients = pd.read_csv(normalized_dir / "patients.csv", low_memory=False)
    devices = pd.read_csv(normalized_dir / "devices.csv", low_memory=False)
    category_year = pd.read_csv(reporting_dir / "category_year_reporting.csv")

    reports["mdr_report_key"] = reports["mdr_report_key"].astype(str)
    patients["mdr_report_key"] = patients["mdr_report_key"].astype(str)
    devices["mdr_report_key"] = devices["mdr_report_key"].astype(str)
    if reports["mdr_report_key"].duplicated().any():
        raise ValueError("report_analysis must have one row per report")

    report_fields = [
        "event_type", "report_source_code", "reporter_occupation_code",
        "reporter_country_code", "event_location",
    ]
    report_characteristics = pd.concat(
        [categorical_summary(reports, field, len(reports)) for field in report_fields],
        ignore_index=True,
    )

    source_rows = []
    followups = []
    for key, source_json, report_type_json in reports[
        ["mdr_report_key", "source_type_json", "type_of_report_json"]
    ].itertuples(index=False, name=None):
        for label in dict.fromkeys(parse_list(source_json)):
            source_rows.append({"mdr_report_key": key, "source_type": label.upper()})
        report_types = [value.casefold() for value in parse_list(report_type_json)]
        followups.append({
            "mdr_report_key": key,
            "initial_submission_present": any("initial" in value for value in report_types),
            "followup_count": sum("followup" in value for value in report_types),
        })
    source_links = pd.DataFrame(source_rows, columns=["mdr_report_key", "source_type"]).drop_duplicates()
    source_summary = source_links.groupby("source_type", as_index=False).agg(
        report_count=("mdr_report_key", "nunique")
    ).sort_values("report_count", ascending=False)
    source_summary["pct_of_all_reports"] = (100 * source_summary["report_count"] / len(reports)).round(2)

    followup_frame = pd.DataFrame(followups)
    followup_frame["followup_bucket"] = pd.cut(
        followup_frame["followup_count"],
        bins=[-1, 0, 1, 2, float("inf")],
        labels=["0", "1", "2", "3+"],
    ).astype(str)
    followup_summary = followup_frame.groupby("followup_bucket", as_index=False).agg(
        report_count=("mdr_report_key", "nunique")
    )
    followup_summary["pct_of_all_reports"] = (
        100 * followup_summary["report_count"] / len(reports)
    ).round(2)

    received = pd.to_datetime(reports["date_received_iso"], errors="coerce")
    event = pd.to_datetime(reports["date_of_event_iso"], errors="coerce")
    lag = (received - event).dt.days
    lag_frame = pd.DataFrame({"received_year": reports["received_year"], "lag_days": lag})
    lag_summary_rows = []
    for year, group in lag_frame.groupby("received_year", dropna=False):
        valid = group.loc[group["lag_days"].ge(0), "lag_days"].dropna()
        lag_summary_rows.append({
            "received_year": year,
            "report_count": len(group),
            "lag_available": int(group["lag_days"].notna().sum()),
            "negative_lag_rows": int(group["lag_days"].lt(0).sum()),
            "median_nonnegative_lag_days": round(float(valid.median()), 1) if len(valid) else "",
            "q1_nonnegative_lag_days": round(float(valid.quantile(.25)), 1) if len(valid) else "",
            "q3_nonnegative_lag_days": round(float(valid.quantile(.75)), 1) if len(valid) else "",
        })
    lag_summary = pd.DataFrame(lag_summary_rows)

    patients["patient_age_years_numeric"] = pd.to_numeric(patients["patient_age_years"], errors="coerce")
    patients["age_band"] = pd.cut(
        patients["patient_age_years_numeric"],
        bins=[-float("inf"), 17, 29, 39, 49, 59, 69, float("inf")],
        labels=["0-17", "18-29", "30-39", "40-49", "50-59", "60-69", "70+"],
    ).astype(str).replace("nan", "[Missing/Invalid]")
    patient_characteristics = pd.concat([
        categorical_summary(patients, "patient_age_status", len(patients)),
        categorical_summary(patients, "age_band", len(patients)),
        categorical_summary(patients, "patient_sex", len(patients)),
        categorical_summary(patients, "patient_ethnicity", len(patients)),
        categorical_summary(patients, "patient_race", len(patients)),
    ], ignore_index=True)

    device_links = devices.assign(
        manufacturer=devices["manufacturer_d_name"].fillna("").astype(str).str.strip().replace("", "[Missing]"),
        brand=devices["brand_name"].fillna("").astype(str).str.strip().replace("", "[Missing]"),
    )[["mdr_report_key", "manufacturer", "brand"]]
    device_entries = device_links.groupby(["manufacturer", "brand"], as_index=False).size().rename(
        columns={"size": "device_entry_count"}
    )
    manufacturer_summary = device_links.drop_duplicates().groupby(
        ["manufacturer", "brand"], as_index=False
    ).agg(report_count=("mdr_report_key", "nunique")).merge(
        device_entries, on=["manufacturer", "brand"], how="left", validate="one_to_one"
    ).sort_values(["report_count", "manufacturer", "brand"], ascending=[False, True, True])
    manufacturer_summary["pct_of_all_reports"] = (
        100 * manufacturer_summary["report_count"] / len(reports)
    ).round(2)

    first_year = int(category_year["received_year"].min())
    last_year = int(category_year["received_year"].max())
    pivot = category_year.pivot_table(
        index=["clinical_domain", "category"],
        columns="received_year",
        values="pct_of_year_reports",
        fill_value=0,
    )
    trend = pivot.reset_index()
    trend["first_year"] = first_year
    trend["last_year"] = last_year
    trend["first_year_pct"] = trend.get(first_year, 0)
    trend["last_year_pct"] = trend.get(last_year, 0)
    trend["absolute_change_percentage_points"] = (
        trend["last_year_pct"] - trend["first_year_pct"]
    ).round(4)
    category_trends = trend[[
        "clinical_domain", "category", "first_year", "last_year",
        "first_year_pct", "last_year_pct", "absolute_change_percentage_points",
    ]].sort_values("absolute_change_percentage_points", ascending=False)

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "report_characteristics.csv": report_characteristics,
        "source_type_summary.csv": source_summary,
        "followup_summary.csv": followup_summary,
        "event_to_receipt_lag_by_year.csv": lag_summary,
        "patient_entry_characteristics.csv": patient_characteristics,
        "manufacturer_brand_reporting.csv": manufacturer_summary,
        "category_trend_2020_2025.csv": category_trends,
    }
    for name, frame in outputs.items():
        frame.to_csv(output_dir / name, index=False, encoding="utf-8-sig")

    report_keys = set(reports["mdr_report_key"])
    qc = {
        "scope": "full-cohort descriptive characteristics",
        "report_rows": len(reports),
        "patient_entry_rows": len(patients),
        "device_entry_rows": len(devices),
        "orphan_patient_report_keys": len(set(patients["mdr_report_key"]) - report_keys),
        "orphan_device_report_keys": len(set(devices["mdr_report_key"]) - report_keys),
        "followup_report_reconciliation_difference": int(
            followup_summary["report_count"].sum() - len(reports)
        ),
        "source_type_note": "Source-type percentages may overlap because a report can carry multiple labels.",
        "patient_note": "Patient entries are not unique patients.",
        "manufacturer_note": "Manufacturer/brand counts are report associations, not rates or safety rankings.",
        "tables_created": list(outputs),
        "qc_gate_passed": bool(
            not reports["mdr_report_key"].duplicated().any()
            and not (set(patients["mdr_report_key"]) - report_keys)
            and not (set(devices["mdr_report_key"]) - report_keys)
            and followup_summary["report_count"].sum() == len(reports)
        ),
        "warning": WARNING,
    }
    path = output_dir / "cohort_characteristics_qc.json"
    path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize full-cohort report, patient, and device characteristics.")
    parser.add_argument("--analytic-dir", type=Path, default=Path("data/processed/full_analytic"))
    parser.add_argument("--normalized-dir", type=Path, default=Path("data/processed/full_normalized"))
    parser.add_argument("--reporting-dir", type=Path, default=Path("data/processed/reporting_analysis"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/cohort_characteristics"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Cohort characteristics QC: {summarize(args.analytic_dir, args.normalized_dir, args.reporting_dir, args.output_dir)}")

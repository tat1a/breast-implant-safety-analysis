"""Build report-level and long-form analytical tables with pandas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

FIELD_ALIASES = {
    "product_problems_json": "product_problems_cleaned_json",
    "patient_problems_json": "patient_problems_cleaned_json",
}


def parse_list(value: str, field: str) -> list[str]:
    try:
        parsed = json.loads(value or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON list in {field}: {value!r}") from exc
    if not isinstance(parsed, list):
        raise ValueError(f"{field} must contain a JSON list")
    return [str(item).strip() for item in parsed if item is not None and str(item).strip()]


def label_rows(frame: pd.DataFrame, source_field: str) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for report_key, value in frame[["mdr_report_key", source_field]].itertuples(index=False, name=None):
        for label in dict.fromkeys(parse_list(value, source_field)):
            rows.append({
                "mdr_report_key": report_key,
                "source_field": FIELD_ALIASES[source_field],
                "raw_label": label,
            })
    return pd.DataFrame(rows, columns=["mdr_report_key", "source_field", "raw_label"])


def build(
    input_dir: Path,
    taxonomy_path: Path,
    output_dir: Path,
    inventory_path: Path | None = None,
) -> Path:
    reports = pd.read_csv(input_dir / "reports.csv", dtype=str, keep_default_na=False)
    patients = pd.read_csv(input_dir / "patients.csv", dtype=str, keep_default_na=False)
    taxonomy = pd.read_csv(taxonomy_path, dtype=str, keep_default_na=False)

    if reports["mdr_report_key"].duplicated().any():
        raise ValueError("reports.csv contains duplicate mdr_report_key values")
    if taxonomy.duplicated(["source_field", "raw_label"]).any():
        raise ValueError("taxonomy contains duplicate source-field/label keys")

    labels = pd.concat([
        label_rows(reports, "product_problems_json"),
        label_rows(patients, "patient_problems_json"),
    ], ignore_index=True).drop_duplicates(["mdr_report_key", "source_field", "raw_label"])

    taxonomy_fields = [
        "source_field", "raw_label", "category", "clinical_domain", "specificity",
        "analysis_role", "terminology_context", "status",
    ]
    label_links = labels.merge(
        taxonomy[taxonomy_fields],
        on=["source_field", "raw_label"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    label_links["mapped"] = label_links["_merge"].eq("both")
    label_links = label_links.drop(columns="_merge")
    for field in taxonomy_fields[2:]:
        label_links[field] = label_links[field].fillna("")

    mapped = label_links[label_links["mapped"]].copy()
    category_links = mapped[
        ["mdr_report_key", "category", "clinical_domain", "analysis_role"]
    ].drop_duplicates()

    aggregate = label_links.groupby("mdr_report_key", as_index=False).agg(
        distinct_label_count=("raw_label", "size"),
        mapped_label_count=("mapped", "sum"),
    )
    included_counts = (
        category_links[category_links["analysis_role"] == "included"]
        .groupby("mdr_report_key").size().rename("included_category_count").reset_index()
    )

    report_analysis = reports.merge(aggregate, on="mdr_report_key", how="left", validate="one_to_one")
    report_analysis = report_analysis.merge(
        included_counts, on="mdr_report_key", how="left", validate="one_to_one"
    )
    for field in ("distinct_label_count", "mapped_label_count", "included_category_count"):
        report_analysis[field] = report_analysis[field].fillna(0).astype("int64")

    received_raw = report_analysis["date_received"].str.strip()
    event_raw = report_analysis["date_of_event"].str.strip()
    received = pd.to_datetime(received_raw, format="%Y%m%d", errors="coerce")
    event = pd.to_datetime(event_raw, format="%Y%m%d", errors="coerce")
    report_analysis["date_received_iso"] = received.dt.strftime("%Y-%m-%d").fillna("")
    report_analysis["received_year"] = received.dt.year.astype("Int64")
    report_analysis["date_of_event_iso"] = event.dt.strftime("%Y-%m-%d").fillna("")
    report_analysis["event_year"] = event.dt.year.astype("Int64")
    report_analysis["is_ftr_query"] = report_analysis["query_product_codes_json"].map(
        lambda value: "FTR" in parse_list(value, "query_product_codes_json")
    )
    report_analysis["is_fwm_query"] = report_analysis["query_product_codes_json"].map(
        lambda value: "FWM" in parse_list(value, "query_product_codes_json")
    )

    yearly = report_analysis.groupby("received_year", dropna=False).agg(
        report_count=("mdr_report_key", "nunique"),
        ftr_query_reports=("is_ftr_query", "sum"),
        fwm_query_reports=("is_fwm_query", "sum"),
        reports_with_mapped_labels=("mapped_label_count", lambda values: int((values > 0).sum())),
    ).reset_index()
    category_summary = category_links.groupby(
        ["analysis_role", "clinical_domain", "category"], as_index=False
    ).agg(report_count=("mdr_report_key", "nunique")).sort_values(
        ["analysis_role", "report_count", "category"], ascending=[True, False, True]
    )
    category_summary["pct_of_all_reports"] = (
        100 * category_summary["report_count"] / len(report_analysis)
    ).round(4)
    domain_summary = category_links[category_links["analysis_role"] == "included"].groupby(
        "clinical_domain", as_index=False
    ).agg(report_count=("mdr_report_key", "nunique")).sort_values(
        ["report_count", "clinical_domain"], ascending=[False, True]
    )
    domain_summary["pct_of_all_reports"] = (
        100 * domain_summary["report_count"] / len(report_analysis)
    ).round(4)

    output_dir.mkdir(parents=True, exist_ok=True)
    report_analysis.to_csv(output_dir / "report_analysis.csv", index=False, encoding="utf-8-sig")
    label_links.to_csv(output_dir / "report_label_links.csv", index=False, encoding="utf-8-sig")
    category_links.to_csv(output_dir / "report_category_links.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(output_dir / "yearly_report_summary.csv", index=False, encoding="utf-8-sig")
    category_summary.to_csv(output_dir / "category_summary.csv", index=False, encoding="utf-8-sig")
    domain_summary.to_csv(output_dir / "domain_summary.csv", index=False, encoding="utf-8-sig")

    mapped_links = int(label_links["mapped"].sum())
    expected_label_links = None
    label_link_reconciliation_difference = None
    if inventory_path is not None:
        inventory = pd.read_csv(inventory_path, dtype={"report_count": "int64"})
        expected_label_links = int(inventory["report_count"].sum())
        label_link_reconciliation_difference = len(label_links) - expected_label_links
    qc = {
        "scope": "full FTR/FWM report-level analytical dataset, date_received 2020-01-01 through 2025-12-31",
        "taxonomy_file": taxonomy_path.name,
        "pandas_version": pd.__version__,
        "input_report_rows": len(reports),
        "input_patient_rows": len(patients),
        "output_report_rows": len(report_analysis),
        "report_label_links": len(label_links),
        "mapped_report_label_links": mapped_links,
        "mapped_report_label_link_pct": round(100 * mapped_links / len(label_links), 2) if len(label_links) else 0,
        "report_category_links": len(category_links),
        "reports_without_source_labels": int((report_analysis["distinct_label_count"] == 0).sum()),
        "reports_without_mapped_labels": int((report_analysis["mapped_label_count"] == 0).sum()),
        "duplicate_report_keys": int(report_analysis["mdr_report_key"].duplicated().sum()),
        "expected_report_label_links_from_profile": expected_label_links,
        "report_label_link_reconciliation_difference": label_link_reconciliation_difference,
        "missing_date_received": int(received_raw.eq("").sum()),
        "invalid_nonmissing_date_received": int((received_raw.ne("") & received.isna()).sum()),
        "missing_date_of_event": int(event_raw.eq("").sum()),
        "invalid_nonmissing_date_of_event": int((event_raw.ne("") & event.isna()).sum()),
        "qc_gate_passed": len(report_analysis) == len(reports)
        and not report_analysis["mdr_report_key"].duplicated().any()
        and set(label_links["mdr_report_key"]).issubset(set(reports["mdr_report_key"]))
        and (label_link_reconciliation_difference in (None, 0)),
        "warning": "Counts describe MDR reports and coded report links, not unique patients/devices, incidence, causality, or comparative safety.",
    }
    qc_path = output_dir / "analytic_dataset_qc.json"
    qc_path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    return qc_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the full report-level analytical dataset.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/processed/full_normalized"))
    parser.add_argument("--taxonomy", type=Path, default=Path("config/complication_taxonomy_v5.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/full_analytic"))
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("data/processed/full_profile/complication_label_inventory.csv"),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Analytic QC: {build(args.input_dir, args.taxonomy, args.output_dir, args.inventory)}")

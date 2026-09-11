"""Create a stable, aggregate-only Power BI data model."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

WARNING = ("MDR reporting patterns only; not incidence, causality, unique patients/"
           "devices, comparative safety, or manufacturer rankings.")


def passed(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not payload.get("qc_gate_passed"):
        raise ValueError(f"Required QC gate failed: {path}")
    return payload


def pascal(name: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^A-Za-z0-9]+", name) if part)


def rename_columns(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.rename(columns={column: pascal(column) for column in frame.columns})


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def build(reporting: Path, characteristics: Path, final: Path, output: Path) -> Path:
    reporting_qc = passed(reporting / "reporting_analysis_qc.json")
    characteristics_qc = passed(characteristics / "cohort_characteristics_qc.json")
    final_qc = passed(final / "final_evidence_qc.json")
    total = int(final_qc["input_report_rows"])

    annual = rename_columns(load_csv(reporting / "annual_reporting_trends.csv"))
    query = rename_columns(load_csv(reporting / "annual_query_composition.csv"))
    category_year = rename_columns(load_csv(reporting / "category_year_reporting.csv"))
    category_overall = rename_columns(load_csv(reporting / "category_overall_reporting.csv"))
    domain_year = rename_columns(load_csv(reporting / "domain_year_reporting.csv"))
    reporter = rename_columns(load_csv(reporting / "reporter_source_summary.csv"))
    event_date = rename_columns(load_csv(reporting / "event_date_completeness_by_year.csv"))
    followup = rename_columns(load_csv(characteristics / "followup_summary.csv"))
    lag = rename_columns(load_csv(characteristics / "event_to_receipt_lag_by_year.csv"))
    patients = rename_columns(load_csv(characteristics / "patient_entry_characteristics.csv"))
    source_type = rename_columns(load_csv(characteristics / "source_type_summary.csv"))
    metrics = load_csv(final / "final_summary_metrics.csv")

    years = sorted(int(value) for value in annual["ReceivedYear"].dropna().unique())
    dim_year = pd.DataFrame({"Year": years})
    annual = annual.rename(columns={"ReceivedYear": "Year"})
    query = query.rename(columns={"ReceivedYear": "Year"})
    category_year = category_year.rename(columns={"ReceivedYear": "Year"})
    domain_year = domain_year.rename(columns={"ReceivedYear": "Year"})
    event_date = event_date.rename(columns={"ReceivedYear": "Year"})
    lag = lag.rename(columns={"ReceivedYear": "Year"})

    metric_values = {str(row.metric): int(row.value) for row in metrics.itertuples(index=False)}
    kpi = pd.DataFrame([{
        "ScopedReports": metric_values["scoped MDR reports"],
        "PatientEntries": metric_values["patient entries"],
        "DeviceEntries": metric_values["device entries"],
        "ReportsWithFollowup": metric_values["reports with at least one follow-up"],
        "ReportsWithLagAvailable": metric_values["reports with event-to-receipt lag available"],
        "ReportsMissingEventDate": metric_values["reports missing a usable event date"],
        "NegativeLagRows": metric_values["negative event-to-receipt lag rows"],
    }])
    kpi["ReportsWithFollowupPct"] = (100 * kpi["ReportsWithFollowup"] / total).round(2)
    kpi["LagAvailablePct"] = (100 * kpi["ReportsWithLagAvailable"] / total).round(2)
    kpi["EventDateMissingPct"] = (100 * kpi["ReportsMissingEventDate"] / total).round(2)

    checks = {
        "annual_reconciles": int(annual["ReportCount"].sum()) == total,
        "query_composition_reconciles": int(query["ReportCount"].sum()) == total,
        "followup_reconciles": int(followup["ReportCount"].sum()) == total,
        "lag_reconciles": int(lag["ReportCount"].sum()) == total,
        "event_date_reconciles": int(event_date["ReportCount"].sum()) == total,
        "year_dimension_matches": years == list(range(2020, 2026)),
        "annual_year_unique": not annual["Year"].duplicated().any(),
        "query_key_unique": not query.duplicated(["Year", "QueryGroup"]).any(),
        "category_year_key_unique": not category_year.duplicated(
            ["Year", "ClinicalDomain", "Category"]
        ).any(),
        "category_counts_valid": bool(category_overall["ReportCount"].le(total).all()),
    }
    if not all(checks.values()):
        raise ValueError(f"Power BI dataset reconciliation failed: {checks}")

    tables = {
        "DimYear.csv": dim_year,
        "KpiSummary.csv": kpi,
        "AnnualReporting.csv": annual,
        "QueryComposition.csv": query,
        "CategoryByYear.csv": category_year,
        "CategoryOverall.csv": category_overall,
        "DomainByYear.csv": domain_year,
        "ReporterSource.csv": reporter,
        "SourceType.csv": source_type,
        "FollowupSummary.csv": followup,
        "ReportingLag.csv": lag,
        "EventDateCompleteness.csv": event_date,
        "PatientEntryCharacteristics.csv": patients,
    }
    dictionary_rows = [
        ("KpiSummary", "ScopedReports", "Whole number", "Unique scoped MDR report rows", "Full scoped cohort"),
        ("AnnualReporting", "ReportCount", "Whole number", "Unique reports received in year", "All scoped reports in year"),
        ("QueryComposition", "PctOfYearReports", "Decimal percentage", "Share of annual reports by FTR/FWM query membership", "All scoped reports in year"),
        ("CategoryByYear", "PctOfYearReports", "Decimal percentage", "Reports carrying mapped category", "All scoped reports in year; categories overlap"),
        ("CategoryOverall", "PctOfAllReports", "Decimal percentage", "Reports carrying mapped category", "All 237,194 scoped reports; categories overlap"),
        ("DomainByYear", "PctOfYearReports", "Decimal percentage", "Reports carrying at least one category in domain", "All scoped reports in year; domains overlap"),
        ("FollowupSummary", "PctOfAllReports", "Decimal percentage", "Reports by coded follow-up count bucket", "All scoped reports"),
        ("ReportingLag", "MedianNonnegativeLagDays", "Decimal days", "Median date_received minus date_of_event", "Reports with nonnegative available lag"),
        ("EventDateCompleteness", "EventDateMissingPct", "Decimal percentage", "Reports lacking usable date_of_event", "All scoped reports in year"),
        ("PatientEntryCharacteristics", "PctOfRows", "Decimal percentage", "Recorded patient-entry characteristic", "Patient entries, not unique patients"),
        ("ReporterSource", "PctOfAllReports", "Decimal percentage", "Recorded report-source/occupation combination", "All scoped reports"),
        ("SourceType", "PctOfAllReports", "Decimal percentage", "Reports carrying source-type label", "All scoped reports; labels overlap"),
    ]
    dictionary = pd.DataFrame(dictionary_rows, columns=[
        "Table", "Field", "DataType", "Definition", "Denominator"
    ])
    dictionary["Warning"] = WARNING
    tables["DataDictionary.csv"] = dictionary

    output.mkdir(parents=True, exist_ok=True)
    for name, frame in tables.items():
        frame.to_csv(output / name, index=False, encoding="utf-8-sig")

    qc = {
        "scope": "aggregate-only Power BI dataset for FTR/FWM 2020-2025 reporting analysis",
        "input_report_rows": total,
        "upstream_qc_passed": {
            "reporting_analysis": bool(reporting_qc["qc_gate_passed"]),
            "cohort_characteristics": bool(characteristics_qc["qc_gate_passed"]),
            "final_evidence": bool(final_qc["qc_gate_passed"]),
        },
        "reconciliation_checks": checks,
        "tables_created": list(tables),
        "contains_row_level_reports": False,
        "contains_narratives": False,
        "contains_manufacturer_safety_ranking": False,
        "qc_gate_passed": all(checks.values()),
        "warning": WARNING,
    }
    path = output / "PowerBI_QC.json"
    path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build aggregate Power BI input tables.")
    parser.add_argument("--reporting-dir", type=Path, default=Path("data/processed/reporting_analysis"))
    parser.add_argument("--characteristics-dir", type=Path, default=Path("data/processed/cohort_characteristics"))
    parser.add_argument("--final-dir", type=Path, default=Path("reports/final_evidence"))
    parser.add_argument("--output-dir", type=Path, default=Path("dashboard/data"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Power BI dataset QC: {build(args.reporting_dir, args.characteristics_dir, args.final_dir, args.output_dir)}")

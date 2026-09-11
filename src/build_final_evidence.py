"""Build the final evidence package from validated full-cohort outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

WARNING = ("FDA MDR reporting patterns; not unique patients/devices, incidence, "
           "causality, comparative safety, or manufacturer safety rankings.")


def require_passed(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not payload.get("qc_gate_passed"):
        raise ValueError(f"Upstream QC has not passed: {path}")
    return payload


def markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    header = "| " + " | ".join(columns) + " |"
    rule = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = ["| " + " | ".join(map(str, row)) + " |"
            for row in frame.itertuples(index=False, name=None)]
    return "\n".join([header, rule, *rows])


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.text(0.01, 0.01, WARNING, fontsize=8, color="#555555")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)


def build(reporting_dir: Path, characteristics_dir: Path, output_dir: Path) -> Path:
    reporting_qc = require_passed(reporting_dir / "reporting_analysis_qc.json")
    characteristics_qc = require_passed(
        characteristics_dir / "cohort_characteristics_qc.json"
    )
    annual = pd.read_csv(reporting_dir / "annual_reporting_trends.csv")
    categories = pd.read_csv(reporting_dir / "category_overall_reporting.csv")
    followup = pd.read_csv(characteristics_dir / "followup_summary.csv")
    lag = pd.read_csv(characteristics_dir / "event_to_receipt_lag_by_year.csv")
    patient = pd.read_csv(characteristics_dir / "patient_entry_characteristics.csv")

    total = int(reporting_qc["input_report_rows"])
    followup["followup_bucket"] = followup["followup_bucket"].astype(str)
    with_followup = int(followup.loc[
        ~followup["followup_bucket"].eq("0"), "report_count"
    ].sum())
    lag_available = int(lag["lag_available"].sum())
    negative_lag = int(lag["negative_lag_rows"].sum())
    event_date_missing = total - lag_available
    age_total = int(patient.loc[
        patient["field"].eq("patient_age_status"), "row_count"
    ].sum())
    checks = {
        "annual_reports_reconcile": int(annual["report_count"].sum()) == total,
        "followup_buckets_reconcile": int(followup["report_count"].sum()) == total,
        "lag_years_reconcile": int(lag["report_count"].sum()) == total,
        "patient_age_status_reconciles": age_total == int(
            characteristics_qc["patient_entry_rows"]
        ),
        "category_counts_within_report_denominator": bool(
            categories["report_count"].le(total).all()
        ),
    }
    if not all(checks.values()):
        raise ValueError(f"Final evidence reconciliation failed: {checks}")

    output_dir.mkdir(parents=True, exist_ok=True)
    figures = output_dir / "figures"
    figures.mkdir(exist_ok=True)
    metrics = pd.DataFrame([
        ("scoped MDR reports", total),
        ("patient entries", int(characteristics_qc["patient_entry_rows"])),
        ("device entries", int(characteristics_qc["device_entry_rows"])),
        ("reports with at least one follow-up", with_followup),
        ("reports with event-to-receipt lag available", lag_available),
        ("reports missing a usable event date", event_date_missing),
        ("negative event-to-receipt lag rows", negative_lag),
    ], columns=["metric", "value"])
    metrics.to_csv(output_dir / "final_summary_metrics.csv", index=False,
                   encoding="utf-8-sig")

    top = categories.head(10).copy()
    top["category"] = top["category"].str.replace("_", " ", regex=False)
    top.to_csv(output_dir / "top_reported_categories.csv", index=False,
               encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ordered = followup.set_index("followup_bucket").reindex(["0", "1", "2", "3+"])
    ax.bar(ordered.index, ordered["pct_of_all_reports"], color="#4976a8")
    ax.set(title="Follow-up multiplicity among scoped MDR reports",
           xlabel="Number of coded follow-up submissions", ylabel="Percent of reports")
    fig.tight_layout(rect=(0, .05, 1, 1))
    save_figure(fig, figures / "followup_multiplicity.svg")

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(lag["received_year"], lag["median_nonnegative_lag_days"],
            marker="o", linewidth=2, color="#7a4e9d")
    ax.set(title="Median event-to-FDA-receipt interval", xlabel="FDA receipt year",
           ylabel="Median days (nonnegative intervals)")
    ax.grid(axis="y", alpha=.25)
    fig.tight_layout(rect=(0, .05, 1, 1))
    save_figure(fig, figures / "median_reporting_lag.svg")

    annual_display = annual[["received_year", "report_count",
                             "year_over_year_change_pct"]].fillna("")
    category_display = top[["clinical_domain", "category", "report_count",
                            "pct_of_all_reports"]].copy()
    category_display["pct_of_all_reports"] = category_display[
        "pct_of_all_reports"
    ].map(lambda value: f"{float(value):.2f}%")
    report = f"""# Final evidence summary

## Study scope

This reproducible descriptive study includes **{total:,} unique FDA MDR reports**
returned by the frozen FTR/FWM queries for date_received 2020-01-01 through
2025-12-31. It describes reporting patterns and coded terms, not complication risk.

## Cohort and data-quality findings

- {int(characteristics_qc['device_entry_rows']):,} device entries and
  {int(characteristics_qc['patient_entry_rows']):,} patient entries linked without
  orphan foreign keys.
- {with_followup:,} reports ({100 * with_followup / total:.2f}%) contained at least
  one coded follow-up submission.
- Event-to-receipt lag was available for {lag_available:,} reports;
  {event_date_missing:,} lacked a usable clinical event date.
- {negative_lag:,} negative intervals remain auditable anomalies and are excluded
  from nonnegative lag summaries.
- Category percentages overlap because one report can carry multiple categories.

## Annual reporting volume

{markdown_table(annual_display)}

## Most frequently mapped reported categories

{markdown_table(category_display)}

## Interpretation boundaries

MAUDE has no denominator for implanted patients or devices. Reporting is incomplete
and affected by manufacturers, reporters, follow-up practices, coding, publicity,
regulation, and time. Results cannot estimate incidence, prevalence, causal effects,
patient-level risk, or comparative manufacturer/device safety. Manufacturer and
brand counts are report associations, not safety rankings.

## Reproducibility

This package is generated only after upstream QC gates pass. Its QC file records
all reconciliation checks, outputs, and the inference warning.
"""
    (output_dir / "FINAL_EVIDENCE_SUMMARY.md").write_text(report, encoding="utf-8")
    qc = {
        "scope": "final evidence package for full FTR/FWM 2020-2025 cohort",
        "input_report_rows": total,
        "upstream_reporting_qc_passed": True,
        "upstream_characteristics_qc_passed": True,
        "reconciliation_checks": checks,
        "outputs": ["final_summary_metrics.csv", "top_reported_categories.csv",
                    "FINAL_EVIDENCE_SUMMARY.md", "figures/followup_multiplicity.svg",
                    "figures/median_reporting_lag.svg"],
        "qc_gate_passed": all(checks.values()),
        "warning": WARNING,
    }
    path = output_dir / "final_evidence_qc.json"
    path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build final validated evidence outputs.")
    parser.add_argument("--reporting-dir", type=Path,
                        default=Path("data/processed/reporting_analysis"))
    parser.add_argument("--characteristics-dir", type=Path,
                        default=Path("data/processed/cohort_characteristics"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/final_evidence"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Final evidence QC: {build(args.reporting_dir, args.characteristics_dir, args.output_dir)}")

"""Create descriptive reporting-pattern tables and portfolio-ready figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

WARNING = "MDR reporting proportions; not incidence, causality, or comparative safety."


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.text(0.01, 0.01, WARNING, fontsize=8, color="#555555")
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)


def analyze(input_dir: Path, output_dir: Path) -> Path:
    reports = pd.read_csv(input_dir / "report_analysis.csv", low_memory=False)
    categories = pd.read_csv(input_dir / "report_category_links.csv", dtype={"mdr_report_key": str})
    reports["mdr_report_key"] = reports["mdr_report_key"].astype(str)
    if reports["mdr_report_key"].duplicated().any():
        raise ValueError("report_analysis must have one row per report")

    reports["received_year"] = pd.to_numeric(reports["received_year"], errors="coerce").astype("Int64")
    years = sorted(int(value) for value in reports["received_year"].dropna().unique())
    annual = reports.groupby("received_year", as_index=False).agg(
        report_count=("mdr_report_key", "nunique"),
        reports_with_mapped_labels=("mapped_label_count", lambda values: int((values > 0).sum())),
    )
    annual["year_over_year_change_pct"] = annual["report_count"].pct_change().mul(100).round(2)

    reports["query_group"] = "Neither"
    reports.loc[reports["is_ftr_query"].astype(str).str.lower().eq("true"), "query_group"] = "FTR only"
    reports.loc[reports["is_fwm_query"].astype(str).str.lower().eq("true"), "query_group"] = "FWM only"
    both = (
        reports["is_ftr_query"].astype(str).str.lower().eq("true")
        & reports["is_fwm_query"].astype(str).str.lower().eq("true")
    )
    reports.loc[both, "query_group"] = "FTR and FWM"
    query = reports.groupby(["received_year", "query_group"], as_index=False).agg(
        report_count=("mdr_report_key", "nunique")
    )
    denominators = annual.set_index("received_year")["report_count"]
    query["pct_of_year_reports"] = (
        100 * query["report_count"] / query["received_year"].map(denominators)
    ).round(4)

    included = categories[categories["analysis_role"] == "included"].copy()
    category_year = included.merge(
        reports[["mdr_report_key", "received_year"]],
        on="mdr_report_key",
        how="left",
        validate="many_to_one",
    ).groupby(["received_year", "clinical_domain", "category"], as_index=False).agg(
        report_count=("mdr_report_key", "nunique")
    )
    category_year["pct_of_year_reports"] = (
        100 * category_year["report_count"] / category_year["received_year"].map(denominators)
    ).round(4)

    category_overall = included.groupby(["clinical_domain", "category"], as_index=False).agg(
        report_count=("mdr_report_key", "nunique")
    ).sort_values(["report_count", "category"], ascending=[False, True])
    category_overall["pct_of_all_reports"] = (
        100 * category_overall["report_count"] / len(reports)
    ).round(4)

    domain_year = included.merge(
        reports[["mdr_report_key", "received_year"]],
        on="mdr_report_key",
        how="left",
        validate="many_to_one",
    ).drop_duplicates(["mdr_report_key", "received_year", "clinical_domain"]).groupby(
        ["received_year", "clinical_domain"], as_index=False
    ).agg(report_count=("mdr_report_key", "nunique"))
    domain_year["pct_of_year_reports"] = (
        100 * domain_year["report_count"] / domain_year["received_year"].map(denominators)
    ).round(4)

    reporter = reports.groupby(
        ["report_source_code", "reporter_occupation_code"], dropna=False, as_index=False
    ).agg(report_count=("mdr_report_key", "nunique")).sort_values(
        "report_count", ascending=False
    )
    reporter["pct_of_all_reports"] = (100 * reporter["report_count"] / len(reports)).round(4)

    event_date = reports.assign(
        event_date_present=reports["date_of_event_iso"].fillna("").astype(str).str.strip().ne("")
    ).groupby("received_year", as_index=False).agg(
        report_count=("mdr_report_key", "nunique"),
        event_date_present=("event_date_present", "sum"),
    )
    event_date["event_date_missing"] = event_date["report_count"] - event_date["event_date_present"]
    event_date["event_date_missing_pct"] = (
        100 * event_date["event_date_missing"] / event_date["report_count"]
    ).round(2)

    output_dir.mkdir(parents=True, exist_ok=True)
    figures = output_dir / "figures"; figures.mkdir(exist_ok=True)
    tables = {
        "annual_reporting_trends.csv": annual,
        "annual_query_composition.csv": query,
        "category_year_reporting.csv": category_year,
        "category_overall_reporting.csv": category_overall,
        "domain_year_reporting.csv": domain_year,
        "reporter_source_summary.csv": reporter,
        "event_date_completeness_by_year.csv": event_date,
    }
    for name, frame in tables.items():
        frame.to_csv(output_dir / name, index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(annual["received_year"], annual["report_count"], marker="o", linewidth=2)
    ax.set(title="Breast implant MDR reports by FDA receipt year", xlabel="Receipt year", ylabel="Reports")
    ax.grid(axis="y", alpha=0.25); fig.tight_layout(rect=(0, .04, 1, 1))
    save_figure(fig, figures / "annual_report_counts.svg")

    composition = query.pivot(index="received_year", columns="query_group", values="report_count").fillna(0)
    composition = composition.reindex(columns=["FTR only", "FWM only", "FTR and FWM"], fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    composition.plot(kind="bar", stacked=True, ax=ax)
    ax.set(title="MDR query-code composition by receipt year", xlabel="Receipt year", ylabel="Reports")
    ax.legend(title="Query group"); fig.tight_layout(rect=(0, .04, 1, 1))
    save_figure(fig, figures / "annual_query_composition.svg")

    top = category_overall.head(12).sort_values("pct_of_all_reports")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top["category"].str.replace("_", " "), top["pct_of_all_reports"])
    ax.set(title="Most frequently mapped reported categories", xlabel="Percent of scoped MDR reports", ylabel="")
    fig.tight_layout(rect=(0, .04, 1, 1))
    save_figure(fig, figures / "top_reported_categories.svg")

    top_names = category_overall.head(10)["category"].tolist()
    heat = category_year[category_year["category"].isin(top_names)].pivot(
        index="category", columns="received_year", values="pct_of_year_reports"
    ).reindex(top_names).fillna(0)
    fig, ax = plt.subplots(figsize=(9, 6))
    image = ax.imshow(heat.values, aspect="auto", cmap="Blues")
    ax.set_xticks(range(len(heat.columns)), labels=[str(value) for value in heat.columns])
    ax.set_yticks(range(len(heat.index)), labels=[value.replace("_", " ") for value in heat.index])
    ax.set(title="Annual reporting proportion for top mapped categories", xlabel="Receipt year")
    fig.colorbar(image, ax=ax, label="Percent of year reports")
    fig.tight_layout(rect=(0, .04, 1, 1))
    save_figure(fig, figures / "top_category_year_heatmap.svg")

    qc = {
        "scope": "descriptive reporting-pattern analysis of the full FTR/FWM cohort",
        "input_report_rows": len(reports),
        "years": years,
        "annual_report_reconciliation_difference": int(annual["report_count"].sum() - len(reports)),
        "query_group_reconciliation_difference": int(query["report_count"].sum() - len(reports)),
        "category_year_missing_report_keys": int(category_year["received_year"].isna().sum()),
        "tables_created": list(tables),
        "figures_created": sorted(path.name for path in figures.glob("*.svg")),
        "qc_gate_passed": annual["report_count"].sum() == len(reports)
        and query["report_count"].sum() == len(reports)
        and not category_year["received_year"].isna().any(),
        "warning": WARNING,
    }
    qc_path = output_dir / "reporting_analysis_qc.json"
    qc_path.write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    return qc_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze full-cohort MDR reporting patterns.")
    parser.add_argument("--input-dir", type=Path, default=Path("data/processed/full_analytic"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/reporting_analysis"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Reporting analysis QC: {analyze(args.input_dir, args.output_dir)}")

# Project State

## Project

Breast Implant Postmarket Safety Analysis — clinical-data portfolio project

## Status

Complete and technically eligible for portfolio publication. The reproducible
analytical pipeline, final evidence package, Power BI dashboard, static previews,
PDF export, and dashboard QA record are present in the repository.

## Verified completion

- Frozen FTR/FWM openFDA cohort using `date_received` for 2020–2025.
- 237,213 API records retrieved and reconciled.
- 237,194 unique reports after 19 verified cross-query overlaps.
- 241,342 device entries and 237,155 patient entries normalized with zero orphan keys.
- Missingness, multiplicity, dates, sources, follow-ups, and labels profiled.
- Taxonomy v5: 106 reviewed mappings and 98.79% report-label-link coverage.
- Report-level pandas analytical layer with zero duplicate report keys.
- Aggregate reporting-pattern, category, lag, follow-up, demographic, and
  manufacturer/brand-association summaries.
- Final evidence package with all reconciliation gates passed.
- 59 automated tests passed at final dashboard verification.
- Four-page Power BI dashboard with a hidden QA validation page.
- Static dashboard previews, PDF export, technical QA record, and recruiter-facing
  repository documentation published.

## Frozen analytical boundaries

- Report counts are not unique patient or device counts.
- Category percentages may overlap within a report.
- MAUDE lacks an implanted-patient/device exposure denominator.
- No incidence, prevalence, causality, comparative-safety, or patient-risk claims.
- Manufacturer/brand counts are reporting associations, not safety rankings.
- `date_received` is the cohort date and is not the clinical event date.
- Negative reporting lags remain auditable anomalies.
- Raw JSON, narratives, and row-level processed data remain local and excluded.

## Current publishable metrics

- 237,194 unique scoped MDR reports.
- 140,095 reports (59.06%) with at least one coded follow-up.
- 184,783 reports with an available event-to-receipt interval.
- 52,411 reports without a usable clinical event date.
- 149 negative intervals excluded from nonnegative lag summaries.
- Rupture: 100,777 reports (42.49%).
- Capsular contracture: 98,586 reports (41.56%).
- Nonspecific implant failure: 69,675 reports (29.37%).

These are proportions of scoped MDR reports, not implanted patients.

## Remaining publication work

1. Change repository visibility to public after the completed privacy review.
2. Add a concise repository description and relevant GitHub topics.
3. Add the verified project description and repository link to CV and LinkedIn.

## CV/LinkedIn claim status

The project may be described as a completed independent clinical-data/postmarket
surveillance portfolio analysis with a reproducible Python pipeline and Power BI
dashboard. Do not claim incidence, causality, comparative safety, unique-patient
analysis, or clinical prediction.

## Last updated

2026-09-14

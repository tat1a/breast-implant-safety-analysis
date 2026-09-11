# Project State

## Project

Breast Implant Postmarket Safety Analysis — clinical-data portfolio project

## Status

Core study complete and technically eligible for portfolio use. Power BI dashboard
presentation is the remaining enhancement.

## Verified completion

- Frozen FTR/FWM openFDA cohort using date_received 2020–2025.
- 237,213 API records retrieved and reconciled.
- 237,194 unique reports after 19 verified cross-query overlaps.
- 241,342 device entries and 237,155 patient entries normalized with zero orphan keys.
- Missingness, multiplicity, dates, sources, follow-ups, and labels profiled.
- Taxonomy v5: 106 reviewed mappings and 98.79% report-label-link coverage.
- Report-level pandas analytical layer with zero duplicate report keys.
- Aggregate reporting-pattern, category, lag, follow-up, demographic, and
  manufacturer/brand-association summaries.
- Final evidence package with all five reconciliation gates passed.
- 57 automated tests passed at Stage 17 verification.
- Aggregate findings, figures, QC manifest, README, and portfolio wording published.

## Frozen analytical boundaries

- Report counts are not unique patient or device counts.
- Category percentages may overlap within a report.
- MAUDE lacks an implanted-patient/device exposure denominator.
- No incidence, prevalence, causality, comparative-safety, or patient-risk claims.
- Manufacturer/brand counts are reporting associations, not safety rankings.
- date_received is the cohort date and is not the clinical event date.
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

## Remaining presentation work

1. Build and verify the Power BI dashboard.
2. Export static dashboard images/PDF for recruiters without Power BI.
3. Add final dashboard previews and links to the README.
4. Change repository visibility only after a final privacy and link review.
5. Add the verified project description to CV and LinkedIn.

## CV/LinkedIn claim status

The project may be described as a completed independent clinical-data/postmarket
surveillance portfolio analysis. Do not claim incidence, causality, comparative
safety, unique-patient analysis, or clinical prediction.

## Last updated

2026-09-11

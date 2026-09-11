# Project State

## Project

Breast Implant Postmarket Safety Analysis — clinical-data portfolio project

## Current phase

Core analytical work is complete. Stage 18 is preparing the repository for portfolio
publication by updating its entrypoint and adding selected aggregate outputs.

## Verified completed work

- Frozen FTR/FWM openFDA Device Event queries for date_received 2020–2025.
- Checkpointed search-after pagination with retry, resume, checksum, and duplicate protection.
- 237,213 API records downloaded and reconciled.
- 237,194 unique reports after resolving 19 cross-query overlaps.
- Relational normalization into 237,194 report rows, 241,342 device entries, and
  237,155 patient entries, with zero orphan foreign keys.
- Full missingness, multiplicity, and label inventory profiling.
- Reviewed taxonomy v5 with 106 exact mappings and 98.79% report-label-link coverage.
- Report-level pandas analytical dataset with zero duplicate report keys.
- Annual, query-code, category, domain, reporter-source, follow-up, lag, demographic,
  and manufacturer/brand reporting summaries.
- Final evidence package with five reconciliation checks passing.
- 57 automated tests passing at Stage 17 verification.

## Confirmed analytical boundaries

- Report counts are not unique patient or device counts.
- Category percentages may overlap within reports.
- MAUDE lacks the implanted-patient/device denominator required for incidence.
- No incidence, prevalence, causality, comparative-safety, or patient-risk claims.
- Manufacturer/brand counts are report associations, not safety rankings.
- date_received is the cohort field and is not the clinical event date.
- Negative event-to-receipt intervals remain auditable anomalies.
- Raw JSON and row-level processed data remain local and excluded from Git.

## Publishable headline metrics

- 237,194 unique scoped MDR reports.
- 140,095 reports (59.06%) with at least one coded follow-up.
- 184,783 reports with an available event-to-receipt interval.
- 52,411 reports without a usable clinical event date.
- 149 negative event-to-receipt intervals excluded from nonnegative lag summaries.
- Most frequently mapped categories: rupture 100,777 (42.49%), capsular contracture
  98,586 (41.56%), and nonspecific implant failure 69,675 (29.37%).

## Remaining tasks

1. Commit only the selected aggregate Stage 17 report, metrics, and figures.
2. Review GitHub rendering and links.
3. Add the final portfolio project description to CV and LinkedIn.
4. Optionally create a public interactive dashboard after the static repository is complete.

## CV/LinkedIn claim status

Eligible to be described as a completed independent portfolio analysis after Stage 18
is merged and selected aggregate outputs are visible in the repository. Claims must
retain the descriptive postmarket-surveillance framing and must not imply incidence,
causality, or comparative safety.

## Last updated

2026-09-11

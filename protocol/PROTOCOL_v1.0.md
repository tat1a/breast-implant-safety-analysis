# Protocol v1.0

## Title

Postmarket Reporting Patterns Associated with Permanent Breast Implants: A
Reproducible Descriptive Analysis of FDA Medical Device Reports, 2020–2025

## Version and status

- Version: 1.0
- Status: Frozen final analytical protocol
- Frozen: 2026-09-11
- Development history: protocol/PROTOCOL_v0.1.md and docs/DECISIONS.md

## Objective

Characterize event types, coded patient and device problems, reporting
characteristics, temporal reporting patterns, and data-quality limitations among FDA
medical device reports involving permanent breast implants received from 2020-01-01
through 2025-12-31.

## Design and data source

Retrospective descriptive analysis of FDA MAUDE records accessed through the openFDA
Device Event API. FDA Product Classification data verified FTR (silicone gel-filled
internal breast prosthesis) and FWM (saline inflatable internal breast prosthesis) as
the scoped permanent-implant codes.

The study is not an incidence, prevalence, causal, comparative-safety, or clinical
prediction study.

## Cohort

A record was eligible when:

1. date_received was between 2020-01-01 and 2025-12-31;
2. at least one nested device entry matched FTR or FWM; and
3. mdr_report_key was present.

The two product-code query results were combined and exact cross-query overlaps were
resolved by mdr_report_key only after payload consistency checks. Tissue expander-only,
external prosthesis, and unrelated-device queries were outside the cohort.

## Analytical units

- Primary unit: unique scoped MDR report row identified by mdr_report_key.
- Additional units: nested device entry, nested patient entry, and report-label link.

Patient entries are not assumed to identify unique people. Device entries are not
assumed to identify unique implanted physical devices. Follow-up labels within
type_of_report are preserved and summarized rather than treated as independent
patients or events.

## Data processing

1. Retrieve each product-code query with stable date_received sorting and openFDA
   search_after pagination.
2. Save immutable raw JSON pages locally with checksums and atomic checkpoints.
3. Normalize reports, devices, and patients into linked tables.
4. Exclude raw narrative text from publishable normalized outputs.
5. Preserve original coded/list fields and create separate cleaned derivatives.
6. Validate row counts, uniqueness, foreign keys, duplicates, date parsing, list
   parsing, and missingness.
7. Map reviewed device- and patient-problem labels through complication taxonomy v5.
8. Build a one-row-per-report pandas analytical table and separate label/category
   link tables.
9. Generate aggregate tables, figures, findings, and QC manifests only after upstream
   quality gates pass.

## Taxonomy

Taxonomy v5 contains 106 exact source-field/label mappings. It covers all reviewed
high- and medium-priority labels and 98.79% of 544,199 observed report-label links.
Unmapped rare P3 labels remain auditable and are not silently assigned. Categories
are multi-response and can overlap within a report.

## Statistical analysis

Analyses use counts, report-level proportions, medians, interquartile ranges,
year-over-year change in reporting volume, missingness measures, and categorical
cross-tabulation. Event-to-receipt summaries exclude negative intervals from
nonnegative lag statistics while counting them as data-quality anomalies.

Every percentage must identify its denominator. Category percentages use unique
scoped reports and may sum above 100%.

## Missing data and anomalies

Missing values are retained and reported; they are not imputed or recoded as absence.
Blank, null, invalid, and unparsed age values remain distinguishable where possible.
Missing clinical event date limits event-time analysis. Negative event-to-receipt
intervals are retained in audit outputs and excluded from nonnegative lag summaries.

## Privacy and publication

Raw JSON, narratives, API credentials, and row-level processed datasets stay local
and outside Git. Public artifacts contain aggregate, non-identifiable tables, figures,
code, configuration, provenance, and QC results. No re-identification is attempted.

## Interpretation limits

MAUDE is a passive surveillance system with incomplete and potentially stimulated
reporting, unknown exposure denominators, unverified reports, follow-up multiplicity,
coding changes, and reporter/manufacturer effects. Consequently:

- report counts are not patient or device incidence;
- reported coded terms do not establish causality;
- manufacturer or brand report counts are not safety rankings;
- changes over time are reporting patterns, not proven changes in clinical risk;
- absence of a code or narrative term is not absence of a complication.

## Final cohort and quality gates

The frozen pipeline produced:

- 237,213 records across the two API queries;
- 237,194 unique MDR report rows after 19 cross-query overlaps;
- 241,342 device entries;
- 237,155 patient entries;
- zero orphan device or patient foreign keys;
- 544,199 report-label links;
- 98.79% exact taxonomy link coverage;
- five final evidence reconciliation checks passed;
- 57 automated tests passed at final analytical verification.

## Deliverables

- reproducible extraction, normalization, taxonomy, and analytical code;
- reviewed taxonomy and provenance documentation;
- automated unit and reconciliation tests;
- aggregate findings tables and SVG figures;
- final evidence summary and QC manifest;
- Power BI dashboard and static portfolio views (presentation phase).

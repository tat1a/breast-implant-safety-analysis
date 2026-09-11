# Final evidence summary

## Study scope

This reproducible descriptive study includes **237,194 unique FDA MDR reports**
returned by the frozen FTR/FWM queries for date_received 2020-01-01 through
2025-12-31. It describes reporting patterns and coded terms, not complication risk.

## Cohort and data-quality findings

- 241,342 device entries and
  237,155 patient entries linked without
  orphan foreign keys.
- 140,095 reports (59.06%) contained at least
  one coded follow-up submission.
- Event-to-receipt lag was available for 184,783 reports;
  52,411 lacked a usable clinical event date.
- 149 negative intervals remain auditable anomalies and are excluded
  from nonnegative lag summaries.
- Category percentages overlap because one report can carry multiple categories.

## Annual reporting volume

| received_year | report_count | year_over_year_change_pct |
| --- | --- | --- |
| 2020 | 38309 |  |
| 2021 | 34707 | -9.4 |
| 2022 | 44458 | 28.1 |
| 2023 | 39738 | -10.62 |
| 2024 | 39737 | -0.0 |
| 2025 | 40245 | 1.28 |

## Most frequently mapped reported categories

| clinical_domain | category | report_count | pct_of_all_reports |
| --- | --- | --- | --- |
| device_integrity | rupture | 100777 | 42.49% |
| local_complication | capsular contracture | 98586 | 41.56% |
| device_integrity | implant failure nonspecific | 69675 | 29.37% |
| biocompatibility | device triggered rejection | 49957 | 21.06% |
| structural_aesthetic_outcome | deformity disfigurement | 33896 | 14.29% |
| device_integrity | leak or deflation | 25635 | 10.81% |
| fluid_collection | seroma | 9712 | 4.09% |
| biocompatibility | patient device incompatibility | 9610 | 4.05% |
| patient_symptom | pain | 7389 | 3.12% |
| device_patient_interaction | patient device interaction | 5506 | 2.32% |

## Interpretation boundaries

MAUDE has no denominator for implanted patients or devices. Reporting is incomplete
and affected by manufacturers, reporters, follow-up practices, coding, publicity,
regulation, and time. Results cannot estimate incidence, prevalence, causal effects,
patient-level risk, or comparative manufacturer/device safety. Manufacturer and
brand counts are report associations, not safety rankings.

## Reproducibility

This package is generated only after upstream QC gates pass. Its QC file records
all reconciliation checks, outputs, and the inference warning.

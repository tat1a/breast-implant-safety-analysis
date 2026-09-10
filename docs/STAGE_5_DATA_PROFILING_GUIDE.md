# Stage 5 — Missingness and Multiplicity Profiling

## Objective

Measure whether the normalized pilot is structurally usable before defining
complication variables or running comparative analyses.

## Run

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.profile_pilot
```

Outputs are written to `data/processed/pilot_profile/`:

- `profile_summary.json`
- `field_missingness.csv`
- `multiplicity_summary.csv`
- `categorical_overview.csv`

## Missingness definition

A value is classified as missing when it is blank or represented by an empty
JSON value (`[]`, `{}`, or `null`). The text value `0` is not missing.

For each field:

`missing_pct = missing_count / row_count × 100`

The denominator is always the number of rows in that field's own table. Device
field completeness uses device rows, not report rows or patients.

## Multiplicity

Reports are grouped by the extracted number of devices and patient entries:

- `0`: none extracted;
- `1`: one extracted;
- `>1`: more than one extracted;
- `invalid`: count could not be interpreted.

This measures database structure, not clinical event severity or patient risk.

## Reconciliation checks

The sum of `device_rows_extracted` in `reports.csv` must equal the number of
rows in `devices.csv`. The same rule applies to patient entries. A difference
of zero indicates reconciliation.

## Categorical overview

The pilot profiles selected recorded values such as event type, report source,
reporter occupation, product code, age status, and sex. Percentages describe
only rows in this bounded pipeline sample. They are not study findings.

## Interpretation exercise

1. What is the denominator of `patient_sex` missingness?
2. Why is the text value `0` not automatically missing?
3. What does `reports_with_multiple_devices` measure?
4. What does a nonzero device reconciliation difference suggest?
5. Can a field with 0% missingness still be inaccurate or biased? Why?
6. Why should pilot category percentages not be placed in the final CV or interpreted as safety results?

## Gate

Before complication classification, confirm that both reconciliation differences
are zero, orphan lists are empty, missingness denominators are understood, and
the pilot outputs are labeled as pipeline checks only.

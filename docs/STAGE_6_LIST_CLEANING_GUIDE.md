# Stage 6 — Auditable JSON-List Cleaning

## Objective

Create analysis-ready list fields without overwriting the normalized source values.

## Run

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.clean_pilot_lists
```

Outputs are written to `data/processed/pilot_cleaned/`:

- `report_lists_cleaned.csv`
- `patient_lists_cleaned.csv`
- `list_cleaning_qc.csv`
- `unknown_values.csv`

## Rules

- Remove blank/null list items.
- Preserve the order of retained items.
- Deduplicate exact repeated problem/outcome/source labels within a row.
- Preserve repeated `Followup` entries and derive `followup_count`.
- Standardize only reviewed source-type capitalization variants.
- Queue unreviewed source/outcome labels instead of guessing their meanings.
- Never overwrite normalized source columns.

## Interpretation

Cleaned values support report-level counting; they do not establish incidence,
causality, comparative safety, or unique real-world patient/device counts.

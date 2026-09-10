# Stage 4 — Relational Normalization of the Pilot

## Objective

Transform immutable raw JSON pages into three linked analytical tables without
count inflation:

- `reports.csv`: one row per unique `mdr_report_key`;
- `devices.csv`: one row per nested device;
- `patients.csv`: one row per nested patient entry.

Raw narratives are deliberately excluded.

## Run the transformation

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.normalize_pilot
```

Expected output location:

```text
data/processed/pilot_normalized/
  reports.csv
  devices.csv
  patients.csv
  normalization_qc.json
```

## Keys and relationships

| Table | Primary key | Foreign key |
|---|---|---|
| reports | `mdr_report_key` | none |
| devices | `device_row_id` | `mdr_report_key` → reports |
| patients | `patient_row_id` | `mdr_report_key` → reports |

`device_row_id` and `patient_row_id` are reproducible project-generated keys.
They do not claim to be FDA identifiers or unique real-world patient IDs.

## Required QC

Open `normalization_qc.json` and verify:

1. `report_rows` equals `unique_report_keys`.
2. Both orphan foreign-key lists are empty.
3. `narratives_exported` is `false`.
4. Patient-age status counts sum to `patient_rows`.
5. Device and patient row counts are interpreted independently from report rows.

## Age handling

The transformation preserves `patient_age_raw` and creates:

- `patient_age_years`: valid ages converted to years;
- `patient_age_status`: `valid`, `missing`, `unparsed`, or `invalid_range`.

Missing or invalid ages are not imputed. Conversion supports years, months,
weeks, days, and hours. Values outside 0–120 years are flagged rather than used.

## Interpretation exercise

1. Why can `device_rows` be larger than `report_rows` without implying duplicate reports?
2. What does the `mdr_report_key` foreign key accomplish in the device table?
3. Why do we retain `patient_age_raw` after creating `patient_age_years`?
4. What is an orphan foreign key and why should its count be zero?
5. Why are raw narratives excluded from these CSV files?
6. If one report has two devices and three patient entries, how many rows should it create in each table?

## Gate

Do not begin complication-frequency analysis until the table counts, keys,
orphan checks, age status, and list-valued fields have been reviewed.

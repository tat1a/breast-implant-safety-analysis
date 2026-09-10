# Stage 9 — Full Cohort Normalization

## Objective

Transform both completed raw query cohorts into one deduplicated relational dataset:

- `reports.csv`: one row per unique `mdr_report_key`;
- `devices.csv`: one row per nested device entry;
- `patients.csv`: one row per nested patient entry.

FTR and FWM query totals must not simply be added and called unique reports. A report
containing both product codes can be returned by both queries. The normalizer identifies
this cross-code overlap, verifies that both raw payloads are identical, retains one report,
and records both query codes and source files.

## Safety and integrity controls

1. Both extraction checkpoints must be `complete` with `qc_gate_passed=true`.
2. Every raw page is verified against its checkpoint SHA-256 before use.
3. Same-key payload differences across FTR/FWM stop the run for review.
4. CSVs are written via temporary files and replace final outputs only after completion.
5. Narrative fields are not exported.
6. Patient rows remain patient entries, not asserted unique people.

## Run

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.normalize_full
Get-Content .\data\processed\full_normalized\normalization_qc.json
```

The transformation reads the raw pages twice: first to establish cross-code identity and
then to stream deduplicated rows. It may take several minutes and can use substantial
memory for the report-key/digest index, but it does not load the complete raw dataset at once.

## Gate

Proceed only when `qc_gate_passed` is true, `reconciliation_difference` is zero, and
the age-status counts sum to `patient_rows`. Report, device, and patient counts describe
database rows—not incidence, unique implants, or unique patients.

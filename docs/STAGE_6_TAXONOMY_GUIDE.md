# Stage 6 — Field Usability and Complication Taxonomy v1

The v1 taxonomy maps reviewed coded device/patient problem labels to broader analytical categories. It does not classify outcomes as diagnoses and does not use narratives.

## Run the complete local phase

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.profile_pilot
.\.venv\Scripts\python.exe -m src.clean_pilot_lists
.\.venv\Scripts\python.exe -m src.classify_pilot_complications
Get-Content .\data\processed\pilot_taxonomy\taxonomy_qc_summary.json
Get-Content .\data\processed\pilot_taxonomy\unmapped_complication_labels.csv
```

## Guardrails

- One report can have multiple distinct complication categories.
- A category is counted at most once per report.
- `Failure of Implant` remains nonspecific and is not converted to confirmed rupture.
- `Required Intervention` is an outcome, not a complication.
- Unmapped labels are queued and never silently assigned.
- Taxonomy changes require versioned review and tests.

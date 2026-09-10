# Stage 10 — Full-Cohort Profiling and Taxonomy Discovery

This stage profiles the normalized cohort before final analytical variables are frozen.
It streams CSV rows rather than loading the full tables into memory. A temporary SQLite
index deduplicates complication labels at report level and is deleted automatically.

Outputs include field missingness, selected categorical frequencies, report-level
multiplicity, complication-label inventory, yearly report-field missingness, and a QC
summary. `report_count` counts distinct MDR reports containing a label;
`item_occurrences` retains repeated coded entries. Neither is an incidence measure.

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.profile_full
Get-Content .\data\processed\full_profile\profile_summary.json
Import-Csv .\data\processed\full_profile\complication_label_inventory.csv |
  Select-Object -First 30 | Format-Table -AutoSize
```

Gate: all row-count reconciliation values must be zero and `qc_gate_passed` must be true.
The complete label inventory—not only the top 30 display—is the input to taxonomy review.

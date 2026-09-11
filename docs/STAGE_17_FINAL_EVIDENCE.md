# Stage 17 — Final evidence package

This stage converts the validated full-cohort analysis outputs into a concise,
auditable findings package. It creates final metrics and top-category tables, two
additional portfolio figures, a data-derived Markdown findings report, and a final
QC manifest. The build stops if either upstream QC gate or a reconciliation check
fails.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.build_final_evidence
Get-Content .\reports\final_evidence\final_evidence_qc.json
Get-Content .\reports\final_evidence\FINAL_EVIDENCE_SUMMARY.md
Get-ChildItem .\reports\final_evidence\figures
```

The report intentionally does not calculate incidence, patient-level risk,
causality, or manufacturer/device safety rankings. MAUDE contains reports but not
the exposed implanted-patient/device denominator required for those estimates.

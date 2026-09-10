# Stage 7 — Pilot Analytical Dataset and Descriptive Outputs

## Objective

Create one feature row per MDR report, aggregate complication tables, a follow-up distribution, and a clearly labelled pilot SVG figure without multiplying counts across device/patient arrays.

## Run

```powershell
.\.venv\Scripts\python.exe -m src.analyze_pilot
Get-Content .\data\processed\pilot_analysis\analysis_qc_summary.json
```

## Outputs

- `pilot_report_features.csv`
- `category_counts.csv`
- `category_by_product_code.csv`
- `followup_distribution.csv`
- `figures/pilot_category_counts.svg`
- `analysis_qc_summary.json`

## Interpretation

Percentages use the bounded pilot reports as their denominators. FTR/FWM tables describe the reports selected by the pilot and are not device-safety comparisons. A report can contain multiple distinct categories; category counts therefore need not sum to the number of reports.

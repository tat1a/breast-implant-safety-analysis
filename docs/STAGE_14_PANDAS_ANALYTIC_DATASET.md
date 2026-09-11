# Stage 14 — Pandas analytical dataset

This stage converts normalized reports and patient entries into auditable report-level and
long-form analytical tables. It does not merge device or patient rows directly into reports,
which prevents accidental row multiplication.

## Install and run

    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
    .\.venv\Scripts\python.exe -m src.build_analytic_dataset
    Get-Content .\data\processed\full_analytic\analytic_dataset_qc.json

## Outputs

- report_analysis.csv: exactly one row per MDR report.
- report_label_links.csv: one row per report, source field, and distinct raw label.
- report_category_links.csv: one row per report and distinct mapped category/domain/role.
- yearly_report_summary.csv: report counts by received year.
- category_summary.csv: mapped category report counts and percentages.
- domain_summary.csv: included-domain report counts and percentages.
- analytic_dataset_qc.json: reconciliation, mapping coverage, dates, and warnings.

The QC gate also reconciles report-label links against the independently generated full
profile inventory. Missing event dates are reported separately from malformed nonmissing
dates. JSON null values are not treated as literal complication labels.

Percentages are proportions of scoped MDR reports, not incidence among implanted patients.
FTR/FWM columns identify query inclusion and must not be interpreted as comparative safety.

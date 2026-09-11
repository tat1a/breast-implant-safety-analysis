# Stage 16 — Cohort characteristics and trend metrics

This stage summarizes report sources, reporter occupation/location, source-type labels,
follow-up multiplicity, event-to-receipt lag, patient-entry demographics, manufacturer/brand
report associations, and 2020-to-2025 category reporting-proportion changes.

    .\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
    .\.venv\Scripts\python.exe -m src.summarize_cohort_characteristics
    Get-Content .\data\processed\cohort_characteristics\cohort_characteristics_qc.json

Patient rows are entries rather than unique people. Manufacturer and brand counts are report
associations and cannot be used as safety rankings because the number of implanted devices
and reporting probability are unknown. Report-source fields are described as observed; they
are not converted into mandatory/voluntary status without an independently validated rule.

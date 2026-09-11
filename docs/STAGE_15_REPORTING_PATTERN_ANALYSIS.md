# Stage 15 — Reporting-pattern analysis

This stage creates descriptive annual, query-composition, category, domain, reporter-source,
and event-date-completeness tables plus four SVG figures.

    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
    .\.venv\Scripts\python.exe -m src.analyze_reporting_patterns
    Get-Content .\data\processed\reporting_analysis\reporting_analysis_qc.json

The primary time axis is FDA receipt year. Category percentages use all scoped MDR reports
received in that year as the denominator. Categories overlap, so their percentages must not
be summed to 100%.

Query-code composition identifies how reports entered the scoped extraction. It is not a
head-to-head device safety comparison. All figures repeat the warning that MDR reporting
patterns do not establish incidence or causality.

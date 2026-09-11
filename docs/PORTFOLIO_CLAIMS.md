# Portfolio, CV, and LinkedIn claims

## Recommended project title

**Breast Implant Postmarket Safety Reporting Analysis | openFDA MAUDE, 2020–2025**

## Short portfolio description

Built a reproducible Python/pandas pipeline to extract, normalize, quality-check, and
analyze 237,194 unique FDA medical device reports involving permanent breast implants.
Developed a reviewed clinical complication taxonomy covering 98.79% of report-label
links, modeled nested report/device/patient data, evaluated missingness and follow-up
patterns, and produced validated analytical tables and visualizations. Framed findings
as postmarket reporting signals rather than incidence, causality, or comparative safety.

## CV bullets

- Developed a checkpointed openFDA extraction and relational normalization pipeline
  for 237,194 unique breast-implant MDR reports from 2020–2025, with automated
  checksum, duplicate, foreign-key, and reconciliation controls.
- Created a reviewed clinical taxonomy covering 98.79% of 544,199 report-label links
  and built report-level pandas analyses of complication reporting, temporal patterns,
  follow-up multiplicity, missingness, and reporting lag.
- Implemented 57 automated tests and QC-gated evidence generation; produced
  publication-ready tables and figures while explicitly preventing unsupported
  incidence, causal, and comparative-safety claims.

## LinkedIn project description

**Independent Clinical Data Analytics Project**

Analyzed FDA MAUDE/openFDA postmarket reports involving permanent breast implants
across 2020–2025. The project includes resumable API extraction, nested JSON
normalization, relational data modeling, data-quality profiling, clinical taxonomy
development, pandas analysis, automated testing, and visualization.

**Scale:** 237,213 API records; 237,194 unique MDR reports; 241,342 device entries;
237,155 patient entries; 544,199 report-label links.

**Selected result:** 59.06% of scoped reports contained at least one coded follow-up,
and 52,411 reports lacked a usable clinical event date. Rupture and capsular
contracture were the most frequently mapped reported categories. These are reporting
patterns, not incidence or patient-risk estimates.

**Tools:** Python, pandas, matplotlib, openFDA API, JSON, CSV, Git, GitHub, unit testing,
relational data modeling, data-quality validation.

## Interview explanation

The strongest feature of the project is not merely the dataset size. It is the
controlled analytical process: a prespecified scope, immutable raw data, resumable
extraction, entity-level normalization, explicit denominators, taxonomy review,
automated reconciliation, and conservative interpretation. The project demonstrates
how to obtain useful postmarket surveillance findings without converting spontaneous
reports into unsupported clinical-risk claims.

## Claims that must not be used

- “42.49% of implanted patients experienced rupture.”
- “One manufacturer or product was safer than another.”
- “The implant caused the reported complication.”
- “237,155 unique patients were analyzed.”
- “The analysis determined complication incidence.”

The valid wording is “percentage/count of scoped MDR reports containing the mapped
reported category.”

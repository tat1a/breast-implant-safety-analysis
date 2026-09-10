# openFDA Device Event API Pilot Results

## Pilot date and query

- Run date: 2026-09-08 UTC
- Cohort date field: `date_received`
- Window: 2020-01-01 through 2025-12-31, inclusive
- Product codes tested: FTR and FWM
- Returned sample: 5 records per code

## Results

| Product code | Device family | Total matches reported by API | Sample returned |
|---|---|---:|---:|
| FTR | Silicone gel-filled permanent breast implant | 169,250 | 5 |
| FWM | Saline inflatable permanent breast implant | 67,963 | 5 |

These totals are dynamic API results and should be re-recorded with every extraction. They represent matching Device Event reports/records, not unique patients, device denominators, incidence, prevalence, or causal events.

## What the pilot established

- Both confirmed product codes produce Device Event results in the specified window.
- Core report, nested device, nested patient, and narrative structures are present.
- `type_of_report` is list-valued and may contain both `Initial submission` and `Followup` on one API record.
- Important demographic and device fields can be blank; missingness must be an explicit analysis output.
- `implant_flag` was blank in observed examples and cannot replace verified product-code eligibility.
- Full retrieval requires pagination/rate-limit planning; a single request is not the full dataset.

## Safety interpretation boundary

MAUDE/openFDA data are appropriate for descriptive signal characterization and data-quality work. They do not provide the denominator or adjudication needed to calculate patient risk, prove device causality, or make unadjusted comparative-safety claims.

## Official references

- FDA Product Classification downloads: https://www.fda.gov/medical-devices/classify-your-medical-device/download-product-code-classification-files
- openFDA Device Event API: https://open.fda.gov/apis/device/event/
- openFDA Device Event searchable fields: https://open.fda.gov/apis/device/event/searchable-fields/
- FDA MAUDE overview and limitations: https://www.fda.gov/medical-devices/mandatory-reporting-requirements-manufacturers-importers-and-device-user-facilities/about-manufacturer-and-user-facility-device-experience-maude-database

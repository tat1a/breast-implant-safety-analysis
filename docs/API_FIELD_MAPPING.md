# Draft openFDA Device Event Field Mapping

This mapping is based on the 2026-09-08 pilot and must be validated on the full extraction before analysis.

| Analysis concept | API field | Level | Planned handling | Important limitation |
|---|---|---|---|---|
| Report identifier | `mdr_report_key` | report | Preserve as string; test uniqueness | A report is not necessarily one unique patient |
| FDA receipt date | `date_received` | report | Primary cohort date, parse `YYYYMMDD` | Receipt date is not event date |
| Event category | `event_type` | report | Tabulate categories and missingness | Reported category is not adjudicated causality |
| Initial/follow-up status | `type_of_report` | report | Explode/list-map after frequency review | One record may contain both Initial and Followup labels |
| Initial report flag/date | `initial_report_to_fda` | report | Profile completeness before use | Empty in pilot examples; cannot be assumed reliable |
| Report source | `report_source_code` | report | Frequency table plus missingness | Source labels do not directly prove mandatory/voluntary status |
| Reporter occupation | `reporter_occupation_code` | report | Normalize categories | Reporter identity/occupation may be incomplete |
| Source type | `source_type` | report | Inspect list structure and profile | Requires codebook review before interpretation |
| Product code | `device[].device_report_product_code` | device | Filter to FTR/FWM; retain device sequence | Multiple devices may occur in one report |
| Brand/generic name | `device[].brand_name`, `generic_name` | device | Clean text; descriptive counts | Free text and naming variation can fragment products |
| Manufacturer | device/manufacturer fields | device/report | Normalize cautiously | Manufacturer reporting and naming may introduce bias |
| Implant flag | `device[].implant_flag` | device | Profile but do not use as sole eligibility test | Empty in observed pilot records despite implant product codes |
| Patient sex | `patient[].patient_sex` | patient | Harmonize values and missingness | Patient arrays may be absent/incomplete; reports are not patients |
| Patient age | `patient[].patient_age` | patient | Parse number/unit into standardized age | Free-form units and missing values require QC |
| Patient weight | `patient[].patient_weight` | patient | Parse only if sufficiently complete | Missingness expected to be substantial |
| Patient problems/outcomes | `patient[]` nested fields | patient | Build controlled categories after profiling | Reported outcomes are not incidence denominators |
| Narrative | `mdr_text[].text` and `text_type_code` | text | Separate restricted workflow; de-identify outputs | Never publish raw narratives; may contain sensitive details |

## Structural rule

Keep three linked tables rather than flattening immediately:

1. `reports`: one row per `mdr_report_key`.
2. `devices`: one row per report-device combination.
3. `patients`: one row per report-patient combination where present.

This prevents accidental multiplication of report counts when a report has several devices, patients, or narrative blocks.

## Mandatory/voluntary status

Do not derive this directly from `report_source_code`. First enumerate `source_type`, `report_source_code`, and relevant manufacturer/user-facility fields, then document a transparent mapping. If the fields do not support a defensible distinction, report the variable as unavailable rather than guessing.

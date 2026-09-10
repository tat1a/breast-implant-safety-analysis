# Field Usability Matrix — Pilot v1

This matrix separates structural availability from analytical validity. A complete field can still be inaccurate, biased, nonspecific, or unsuitable for the intended question.

| Field | Level | Role | Status | Primary limitation |
|---|---|---|---|---|
| `mdr_report_key` | report | linkage/counting | directly usable | identifies MDR records, not unique events or patients |
| `report_number` | report | reporting-system identifier | usable with caution | supplements retain the same report number |
| `date_received` | report | primary cohort/calendar trend | directly usable | FDA receipt date, not clinical onset |
| `date_of_event` | report | clinical timing | usable with caution | reported/best-estimate onset; may be incomplete or inaccurate |
| `event_type` | report | recorded event severity type | usable with caution | reporter classification; pilot is restricted to Injury |
| `report_source_code` | report | submitter class | usable after mapping | alone does not establish mandatory/voluntary status |
| `reporter_occupation_code` | report | reporter profile | usable after mapping | may be broad, secondary, or misclassified |
| `reporter_country_code` | report | geography | usable with caution | 45% missing in pilot; reporter country is not necessarily event country |
| `event_location` | report | event setting | usable after mapping | coded value requires official definition |
| `type_of_report_json` | report | initial/follow-up history | derived use | repeated follow-ups are meaningful and must be counted |
| `source_type_json` | report | information origin | usable after mapping | multi-valued; capitalization and unknown codes occur |
| `product_problems_json` | report | device problem labels | taxonomy input | repeated labels require report-level deduplication |
| `number_devices_reported` | report | declared multiplicity | not usable in pilot | 100% missing |
| `number_patients_reported` | report | declared multiplicity | not usable in pilot | 100% missing |
| `device_rows_extracted` | report | pipeline multiplicity | directly usable for QC | array-row count, not confirmed physical-device count |
| `patient_rows_extracted` | report | pipeline multiplicity | directly usable for QC | entry count, not confirmed unique-patient count |
| `device_report_product_code` | device | FTR/FWM cohort | directly usable | classification must be rechecked before final extraction |
| `brand_name` | device | brand description | usable after normalization | spelling/name variants may split brands |
| `manufacturer_d_name` | device | manufacturer description | usable after normalization | manufacturer/site naming variants |
| `model_number` | device | model analysis | not suitable in pilot | 70% missing |
| `implant_date_year` | device | implant duration | usable with caution | year-only precision and reported accuracy |
| `date_removed_year` | device | removal timing | usable with caution | missing does not prove device remained implanted |
| `device_availability` | device | evaluation availability | usable after mapping | availability is not proof of manufacturer evaluation |
| `device_evaluated_by_manufacturer` | device | evaluation status | not suitable in pilot | 95% missing |
| `device_operator` | device | operator profile | usable after mapping | recorded category may lack clinical detail |
| `patient_age_raw` | patient entry | audit value | preserve only | units/format may vary |
| `patient_age_years` | patient entry | standardized age | usable with caution | 15% missing and entry is not guaranteed unique patient |
| `patient_sex` | patient entry | demographic description | not suitable in pilot | 95% missing |
| `patient_race` | patient entry | demographic description | not suitable in pilot | 95% missing |
| `patient_ethnicity` | patient entry | demographic description | not suitable in pilot | 95% missing |
| `patient_weight_raw` | patient entry | demographic/clinical context | not usable in pilot | 100% missing |
| `outcomes_json` | patient entry | recorded outcome | usable after mapping | mixed labels/codes; outcome is not complication diagnosis |
| `patient_problems_json` | patient entry | patient problem labels | taxonomy input | repeated/nonspecific codes require deduplication and grouping |
| `treatments_json` | patient entry | intervention detail | not usable in pilot | all entries are semantically blank |

## Non-negotiable interpretation limits

- No incidence/prevalence denominator is available.
- Report counts are not unique patient or physical-device counts.
- Coded terms and narratives cannot establish causality.
- FTR/FWM report distributions are not comparative safety estimates.
- Pilot percentages are pipeline checks, not study findings.

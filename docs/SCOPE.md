# Approved Scope — Version 0.1

## Research domain

Medical-device postmarket surveillance at the intersection of aesthetic and reconstructive breast surgery.

## Primary device scope

Permanent breast implants used for aesthetic augmentation or breast reconstruction. The FDA Product Classification file dated 2026-09-07 confirms the following primary product codes:

- `FTR` — Prosthesis, Breast, Noninflatable, Internal, Silicone Gel-Filled; Class III; implant flag Y; regulation 21 CFR 878.3540.
- `FWM` — Prosthesis, Breast, Inflatable, Internal, Saline; Class III; implant flag Y; regulation 21 CFR 878.3530.

The mapping is stored in `data/external/product_code_scope_v0.1.csv`. Product classification will be rechecked at the final extraction date because the FDA source file is updated weekly.

## Provisional exclusions

- Tissue expander-only reports from the primary cohort.
- External breast prostheses.
- Surgical mesh and unrelated breast devices.
- Instruments and accessories that are not permanent breast implants.
- Records outside verified FDA permanent breast-implant product classifications.

Tissue expanders may be retained as a separate exploratory cohort after their product classifications are verified.

## Study period

Reports received by FDA from 2020-01-01 through 2025-12-31.

The period contains six complete calendar years. Calendar year 2026 is excluded because it is incomplete. The COVID-19 period and changes in reporting practices will be treated as interpretive limitations. No time-trend in true clinical risk will be inferred.

## Primary unit of analysis

An initial medical device report involving at least one verified permanent breast implant.

## Additional units

- Report family.
- Supplemental report.
- Device record.
- Patient record.
- Patient-problem code.
- Device-problem code.
- Narrative segment.

## Primary research question

What event types, patient problems, device problems, reporting characteristics, and data-quality limitations are represented in FDA medical device reports involving permanent breast implants received between 2020 and 2025?

## Secondary questions

1. What proportions of retrieved records are initial and supplemental reports?
2. How complete are selected report, device, patient, and narrative fields?
3. Which report-source and reporter-occupation categories are represented?
4. How much narrative text is available and usable?
5. How do all-record summaries differ from initial-only summaries?
6. How many exact duplicates, potential duplicates, or linked report families can be identified under documented rules?
7. Which patient-problem and device-problem categories co-occur within reports?
8. Can aesthetic augmentation and reconstructive indications be identified with adequate completeness and reliability?
9. How consistently are product code, generic name, manufacturer, brand, and model recorded?
10. Which narrative themes may justify better-designed follow-up studies?

## Exploratory analyses

- Narrative theme classification with manual validation.
- Reports mentioning rupture, deflation, infection, inflammation, pain, reoperation, explantation, or reconstruction.
- Completeness differences by recorded source type.
- A separate tissue-expander feasibility analysis.

## Scope freeze conditions

This scope becomes Version 1.0 only after:

1. Permanent breast-implant product codes are verified in the FDA Product Classification Database. **Completed for FTR and FWM on 2026-09-08 using the 2026-09-07 classification file.**
2. A small classification API query or equivalent classification-file parsing test is inspected.
3. A small Device Event API query is inspected.
4. Date, report type, source, reporter, device, patient, problem, and narrative fields are mapped to FDA definitions.
5. The feasibility of initial/supplemental linkage is assessed.

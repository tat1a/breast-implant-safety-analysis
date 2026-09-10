# Protocol v0.1

## Title

Postmarket Safety Signals Associated with Permanent Breast Implants: A Reproducible Descriptive Analysis of FDA Medical Device Reports, 2020–2025

## Version

- Version: 0.1
- Status: Pre-data draft
- Date: 2026-09-08
- Amendment policy: All changes after pilot inspection must be logged in `docs/DECISIONS.md` and later in a protocol amendment table.

## Background

Permanent breast implants are used in aesthetic augmentation and reconstructive surgery. Postmarket medical device reports can reveal suspected device and patient problems encountered after commercialization, but passive reporting systems have substantial limitations. Reports can be incomplete, biased, duplicated, supplemental, and unverified. The number of devices in use is not available as an exposure denominator, and report submission does not establish device causality.

A professionally responsible analysis should therefore characterize retrieved reports, coded problems, report structure, and data quality rather than estimate incidence, prevalence, causality, or comparative device safety.

## Primary objective

To characterize event types, recorded patient problems, recorded device problems, reporting characteristics, and data-quality limitations among FDA medical device reports involving permanent breast implants received from 2020-01-01 through 2025-12-31.

## Secondary objectives

1. Assess completeness of selected report, device, patient, and narrative fields.
2. Describe source types and reporter characteristics as recorded.
3. Distinguish initial and supplemental records where supported by FDA fields.
4. Identify exact duplicates, possible duplicates, and report families under documented rules.
5. Assess whether indication and device attributes are sufficiently complete for descriptive subgroup analysis.
6. Explore clinically relevant narrative themes with manual validation.

## Study design

Retrospective, descriptive analysis of publicly available postmarket medical device reports.

The study is not an incidence study, comparative safety study, causal study, clinical trial, or clinical prediction model.

## Data sources

Primary source: FDA MAUDE records accessed through the openFDA Device Event API. FDA bulk MDR files may be used if the API is insufficient for reproducible full-cohort extraction.

Classification source: FDA Product Classification Database and openFDA Device Classification API. The 2026-09-07 FDA classification file verified `FTR` (silicone gel-filled internal breast prosthesis) and `FWM` (saline inflatable internal breast prosthesis) as the primary permanent-implant codes. The codes must be rechecked against the current source at final extraction.

The extraction manifest will record endpoint/file, exact query, retrieval date, data version where available, checksums, and record counts.

## Study period

FDA `date_received` from 2020-01-01 through 2025-12-31, subject to confirmation that `date_received` is the correct operational field after reviewing its FDA definition and pilot records.

## Target population

FDA device-event reports containing at least one device record assigned to `FTR` or `FWM`, subject to pilot confirmation that the Device Event API records and nested device fields behave as documented.

## Primary analytical unit

Initial medical device report.

## Additional analytical units

- Report family.
- Supplemental report.
- Nested device record.
- Nested patient record.
- Patient-problem entry.
- Device-problem entry.
- Narrative entry.

## Inclusion criteria

1. Report received during the prespecified study period.
2. At least one device record matches a verified permanent breast-implant classification.
3. A usable report identifier is present.
4. The record is retrievable from the prespecified FDA source.

## Exclusion criteria

1. Tissue expander without a permanent breast implant in the primary cohort.
2. External breast prosthesis.
3. Breast-related device that is not a permanent implant.
4. Instrument or accessory without an in-scope permanent implant.
5. Product classification outside the verified cohort.
6. Device identity remains unclassifiable after documented review.
7. Technically corrupted record that cannot be parsed; such exclusions will be counted and documented.

Missing clinical or demographic values alone are not exclusion criteria. Missingness is a study result.

## Provisional variables

### Report-level

- FDA event/MDR identifiers.
- Report number.
- Date received and other report dates, with definitions preserved.
- Event type.
- Initial-report indicator.
- Type of report.
- Source type and report-source code.
- Reporter occupation code.
- Health-professional indicator.
- Adverse-event and product-problem flags.
- Recorded manufacturer and reporting location fields.

### Device-level

- Product code.
- Generic name.
- Brand name.
- Manufacturer.
- Model and catalog number.
- Implant/device-use fields when available.
- Device-problem entries.

### Patient-level

- Recorded age and units.
- Recorded sex.
- Patient-problem entries.
- Recorded outcome/treatment fields when available.

### Narrative-level

- Narrative type.
- Narrative text.
- Presence and length.
- Boilerplate/duplicate-text indicators.
- Manually validated clinical theme labels.

All field names and meanings remain provisional until the searchable-fields reference and pilot JSON are mapped.

## Primary analyses

1. Counts and proportions of event types among eligible initial reports.
2. Counts and proportions of recorded patient-problem categories.
3. Counts and proportions of recorded device-problem categories.
4. Recorded source and reporter characteristics.
5. Field-level missingness and invalidity.
6. Initial/supplemental report structure.
7. Number of nested devices, patients, and problems per report.
8. Exact-duplicate, potential-duplicate, and report-family counts under documented rules.

Every table and figure will state its unit and denominator. Multi-response category proportions may sum to more than 100% and will be labeled accordingly.

## Secondary and sensitivity analyses

- Initial-only versus all-record summaries.
- Exact duplicates retained versus removed.
- Report-family-level summaries if linkage is feasible.
- Completeness by recorded source type.
- Device-attribute completeness.
- Feasibility of indication classification.
- Separate exploratory tissue-expander cohort if justified.

## Narrative analysis

Narrative work will be exploratory. The planned sequence is:

1. Remove exact duplicate and repeated boilerplate text under documented rules.
2. Define a clinical theme dictionary.
3. Create a manual annotation guide.
4. Draw a reproducible random validation sample.
5. Manually annotate the sample.
6. Apply transparent rule-based or statistical text classification.
7. Compare automated labels with manual labels.
8. Report classification errors and unresolved ambiguity.

An external language model will not be a required dependency. Narrative mentions will not be treated as verified diagnoses or causal findings.

## Missing-data approach

- Blank, unknown, and not-applicable values will remain distinct where source semantics allow.
- Missing values will not automatically be recoded as “No.”
- Primary descriptive analyses will not use imputation.
- Missingness will be reported for each key field.
- Absence of a narrative term will not be interpreted as absence of a complication.

## Duplicate and supplemental-record approach

- Exact duplicates will be detected using documented identifiers and content rules.
- Supplemental records will not automatically count as independent events in the primary analysis.
- Report families will be created only with a defensible FDA-supported linking rule.
- Uncertain duplicates will be flagged, not silently deleted.
- Primary and sensitivity results will disclose the record-handling rule used.

## Statistical methods

Initial methods will include counts, proportions, medians, interquartile ranges, missingness measures, and categorical cross-tabulations. Confidence intervals will be used only where their meaning is defensible for the descriptive target.

The project will not use p-value-driven mass comparisons or manufacturer safety rankings. Report counts over time will be presented, if at all, as reporting volume rather than clinical risk trends.

## Ethics, privacy, and governance

The source is public FDA postmarket-report data, but the project will not attempt re-identification. Reporting will favor aggregates. Narrative excerpts will be avoided unless methodologically necessary and reviewed for unnecessary personal detail.

If the work is submitted through an institution or for publication, the relevant institution must determine whether formal ethics/IRB review or exemption documentation is required.

## Anticipated limitations

- Under-reporting and stimulated reporting.
- Unknown device-use denominator.
- Incomplete and inaccurate fields.
- Initial, supplemental, and duplicate records.
- Unverified reports and uncertain causality.
- Reporting and manufacturer-related bias.
- Changes in reporting practice and public attention.
- Inconsistent names and identifiers.
- Incomplete indication data.
- Inability to estimate incidence, prevalence, causal risk, or comparative device safety.

## Planned deliverables

- Frozen Protocol v1.0 and amendment log.
- Verified product-code mapping.
- Reproducible extraction pipeline and manifest.
- Relational SQL schema and data dictionary.
- Cleaning and validation pipeline.
- Quality-control report.
- Analysis notebooks and reproducible figures.
- Power BI dashboard with visible limitations.
- Manuscript-style report.
- GitHub README and interview-ready project summary.

## Protocol v1.0 freeze gate

Protocol v1.0 may be frozen only after official product codes, relevant API fields, date semantics, report-linkage feasibility, and pilot extraction behavior have been verified.

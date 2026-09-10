# MAUDE Orientation and Inference Rules

## What MAUDE is

MAUDE is the FDA Manufacturer and User Facility Device Experience database. It contains medical device reports submitted by mandatory reporters (including manufacturers, importers, and device user facilities under applicable rules) and voluntary reporters such as health professionals, patients, and consumers.

The database is a passive postmarket surveillance source. A report is not equivalent to a verified causal event, a unique patient, or a known denominator of device use.

## Core analytical entities

- **Report:** A submitted medical device report.
- **Initial report:** The first report in a report history.
- **Supplemental report:** A later addition, correction, investigation result, or follow-up.
- **Report family:** Initial and linked supplemental records treated as one report history under a documented rule.
- **Event:** The suspected occurrence described in a report; not necessarily independently verified.
- **Device record:** A device nested within a report; one report may contain multiple devices.
- **Patient record:** Patient information nested within a report; not guaranteed complete or unique across reports.
- **Patient problem:** A coded or described clinical problem.
- **Device problem:** A coded or described device-related problem.
- **Narrative:** Free text describing the event, investigation, or manufacturer assessment.

## Accepted interpretations for this project

The project may report:

1. The number of records retrieved by a prespecified FDA query.
2. The distribution of report classifications among retrieved records.
3. The coded patient and device problem types represented in retrieved records.
4. Patient demographic fields as recorded, together with missingness and validity limitations.
5. The number of exact or potential duplicate records under a documented rule.
6. The number and proportion of initial and supplemental records.
7. Data gaps and areas requiring stronger future research.
8. Missingness counts and proportions for selected fields.
9. The distribution of recorded report-source types.
10. Recorded reporter characteristics, including occupation when available.
11. Recorded report dates and locations, subject to field definitions and missingness.
12. Possible mandatory/voluntary source categories only if a valid mapping can be supported by FDA field definitions.
13. Differences between all-record, initial-only, and deduplicated summaries.
14. Clinically relevant themes in narrative text, if the extraction method is validated manually.

All interpretations must be phrased as applying to **reports retrieved under the prespecified query**, not to all patients receiving breast implants.

## Prohibited interpretations

The project must not claim:

1. Causation between a device and a reported complication.
2. That one device, brand, or manufacturer is safer than another.
3. A population complication rate from MAUDE report counts.
4. Incidence or prevalence of a complication caused by a device.
5. The percentage of implanted patients who develop a specified problem.
6. The effect of unmeasured patient, surgical, institutional, or device-use factors.
7. That changes in report counts over time represent changes in true clinical risk.
8. That missing reports or unreported events can be quantified.
9. That a report is unbiased or medically verified because it came from a manufacturer or health professional.
10. That reporter bias or manufacturer bias can be eliminated from the dataset.
11. That a narrative mention confirms a diagnosis, severity level, or causal relationship.
12. That aesthetic and reconstructive risks differ unless indication and denominator data are adequate—which MAUDE is unlikely to provide.

## Important refinements from the orientation exercise

- Report classification is not a verified clinical diagnosis.
- Report count is not patient count.
- A single report can contain multiple patient problems, device problems, and devices. Category percentages can therefore exceed 100% if multi-response denominators are used.
- “Mandatory versus voluntary” may not exist as a single reliable field. It must be derived only if `source_type`, `report_source_code`, reporter, and manufacturer fields support a documented mapping.
- Location and reporter occupation may be incomplete or reflect the reporting entity rather than the site where the clinical event occurred. Field-level definitions must be checked before labeling.

## Orientation gate result

**Status: PASSED WITH CLARIFICATIONS.** The project owner demonstrated the central distinction between report characterization and patient-level risk estimation.


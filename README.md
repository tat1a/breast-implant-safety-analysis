# Breast Implant Postmarket Safety Portfolio Project

## Working title

**Postmarket Safety Signals Associated with Permanent Breast Implants: A Reproducible Descriptive Analysis of FDA Medical Device Reports, 2020–2025**

## Current status

Protocol and small API-pilot phase complete. Five FTR and five FWM sample records were retrieved to validate query construction and schema; no clinical results are claimed.

## Purpose

This independent portfolio project will characterize report types, coded patient and device problems, reporting sources, report completeness, and duplicate/supplemental-report structure among FDA medical device reports involving permanent breast implants. It covers devices used in aesthetic augmentation and breast reconstruction.

This is a descriptive postmarket-signal and data-quality study. It will not estimate incidence, prevalence, causality, comparative device safety, or patient-level risk.

## Reproduce the API pilot

From the repository root with Python 3.10 or newer:

```bash
python -m unittest discover -s tests -t . -v
python src/openfda_client.py --product-code FTR --limit 5
python src/openfda_client.py --product-code FWM --limit 5
```

The commands create local raw responses and extraction manifests under `data/raw/`. That folder is intentionally excluded from Git. Do not publish raw narrative text or patient-level fields.

The next bounded pagination exercise is documented in
`docs/STAGE_3_PAGINATION_GUIDE.md`. It uses openFDA's `search_after` cursor and
must remain limited to two pages until its checkpoint and QC output are reviewed.

## Immediate next gate

1. Reproduce and explain the pilot queries.
2. Design safe pagination/checkpointing for full retrieval.
3. Normalize report, device, and patient arrays into linked tables.
4. Profile multiplicity, duplicates, missingness, and source fields before analysis variables are frozen.

## Planned tools

- Python and pandas
- SQL (initially DuckDB or SQLite)
- openFDA Device Event API
- Power BI
- Git and GitHub

## Repository map

- `docs/ORIENTATION.md` — MAUDE concepts and valid/invalid inference rules.
- `docs/SCOPE.md` — approved scope and questions.
- `protocol/PROTOCOL_v0.1.md` — pre-data protocol draft.
- `docs/DECISIONS.md` — decisions and their reasons.
- `docs/API_FIELD_MAPPING.md` — draft source-to-analysis field map and limitations.
- `docs/API_PILOT_RESULTS.md` — verified pilot query and aggregate counts.
- `docs/STAGE_3_PAGINATION_GUIDE.md` — bounded multi-page extraction exercise.
- `docs/STAGE_4_NORMALIZATION_GUIDE.md` — report/device/patient table exercise.
- `docs/STAGE_5_DATA_PROFILING_GUIDE.md` — missingness and multiplicity exercise.
- `PROJECT_STATE.md` — restart/handoff state.
- `data/README.md` — data handling rules.
- `src/`, `sql/`, `notebooks/`, `tests/`, `reports/`, `dashboard/` — implementation areas.

## Official starting sources

- FDA MAUDE overview and limitations: https://www.fda.gov/medical-devices/mandatory-reporting-requirements-manufacturers-importers-and-device-user-facilities/about-manufacturer-and-user-facility-device-experience-maude-database
- openFDA Device Event API: https://open.fda.gov/apis/device/event/
- Device Event searchable fields: https://open.fda.gov/apis/device/event/searchable-fields/
- FDA Product Classification Database: https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm
- openFDA Device Classification API: https://open.fda.gov/apis/device/classification/

## Integrity rule

The project may be listed as completed on a CV or LinkedIn only after the extraction pipeline, quality checks, analysis, report, and reproducibility instructions are complete and verified.

# Approved Scope — Version 1.0

## Research domain

Medical-device postmarket surveillance at the intersection of aesthetic and
reconstructive breast surgery.

## Frozen cohort

- Product codes: FTR (silicone gel-filled internal breast prosthesis) and FWM
  (saline inflatable internal breast prosthesis).
- Cohort date: FDA date_received from 2020-01-01 through 2025-12-31.
- Primary analytical unit: unique scoped MDR report identified by mdr_report_key.
- Secondary units: device entries, patient entries, and report-label links.

The FDA classification source and reviewed mapping are documented in
data/external/SOURCE_MANIFEST.md and data/external/product_code_scope_v0.1.csv.

## Exclusions

- Tissue expander-only queries.
- External breast prostheses.
- Surgical mesh, instruments, accessories, and unrelated breast devices.
- Records outside the verified FTR/FWM queries.

## Final research question

What complication labels, reporting characteristics, temporal reporting patterns,
follow-up structure, and data-quality limitations are represented in FDA MDR reports
involving permanent breast implants received between 2020 and 2025?

## Completed analyses

1. Query and annual report counts.
2. Cross-query overlap and report-key reconciliation.
3. Report, device-entry, and patient-entry multiplicity.
4. Field missingness and date validity.
5. Coded device- and patient-problem taxonomy.
6. Overall and annual report-level category frequencies.
7. Source and reporter characteristics.
8. Follow-up label multiplicity.
9. Event-to-receipt reporting lag and negative-date anomalies.
10. Patient-entry demographic completeness.
11. Manufacturer/brand report associations without safety ranking.
12. Final QC-gated evidence tables and figures.

## Out-of-scope questions

The project does not estimate:

- complication incidence, prevalence, or patient risk;
- the percentage of implanted patients experiencing rupture or another event;
- causal effects of an implant;
- comparative manufacturer, brand, model, FTR, or FWM safety;
- unique patient counts;
- mandatory/voluntary classification without a validated rule;
- conclusions from unpublished raw narrative text.

## Deferred extensions

Narrative annotation, indication classification, report-family linkage, a separate
tissue-expander cohort, and predictive modeling require new protocols and validation.
They are not implied by the completed analysis.

## Scope status

Frozen on 2026-09-11. Any extension must be versioned separately and must not silently
change the denominator or interpretation of the completed cohort.

# Decision Log

| ID | Date | Decision | Reason | Status |
|---|---|---|---|---|
| D-001 | 2026-09-08 | Position project as descriptive postmarket-signal and data-quality analysis | MAUDE cannot support incidence, causality, or comparative safety estimates | Confirmed |
| D-002 | 2026-09-08 | Study permanent breast implants used in aesthetic and reconstructive care | Directly aligns with long-term plastic/reconstructive surgery interests | Confirmed |
| D-003 | 2026-09-08 | Use complete calendar years 2020–2025 | Avoid incomplete 2026; retain a modern six-year window | Confirmed |
| D-004 | 2026-09-08 | Exclude tissue expander-only reports from primary cohort | Temporary expanders have a different pathway and complication context | Confirmed; separate exploratory cohort possible |
| D-005 | 2026-09-08 | Primary unit is initial report | Avoid automatically treating supplemental updates as independent events | Provisional until pilot linkage review |
| D-006 | 2026-09-08 | Do not hard-code breast-implant product codes from memory | Cohort must be verified using official FDA classification data | Confirmed |
| D-007 | 2026-09-08 | Treat mandatory/voluntary status as a derived field only if FDA definitions support it | No assumption that a single reliable status field exists | Confirmed |
| D-008 | 2026-09-08 | Do not include project on CV as completed yet | No data extraction, analysis, or QA has occurred | Confirmed |
| D-009 | 2026-09-08 | Use FTR and FWM as the primary permanent breast-implant product codes | Verified in the FDA Product Classification file dated 2026-09-07; both are internal Class III implanted breast prostheses | Confirmed; recheck at final extraction |
| D-010 | 2026-09-08 | Exclude external prostheses KCZ and NOJ and external expander MWZ | They are not permanent internal breast implants | Confirmed |
| D-011 | 2026-09-08 | Do not add PQN tissue expander to the primary cohort | It is an implanted tissue expander, not a permanent breast prosthesis | Confirmed; exploratory only |
# 2026-09-08 — API pilot decisions

- Use `date_received` for the primary 2020–2025 cohort filter.
- Use the nested product-code field `device.device_report_product_code` for FTR/FWM queries.
- Keep raw responses in ignored `data/raw/`; publish only aggregate or de-identified derived outputs.
- Preserve report/device/patient levels separately to avoid count multiplication.
- Do not infer mandatory/voluntary status until source-field combinations are profiled and documented.
- Do not use `implant_flag` as the sole inclusion criterion because it was blank in pilot examples.

# 2026-09-08 — Pagination architecture

- Do not use `skip` for full cohort retrieval because both product-code cohorts exceed the documented paging ceiling.
- Follow the API-generated `Link: rel="next"` URL containing `search_after`.
- Sort ascending by `date_received` for the search-after sequence.
- Save each raw page separately with SHA-256, boundary keys, and record count.
- Write the checkpoint atomically after every successful page.
- Flag repeated `mdr_report_key` values across pages; do not silently discard them during extraction.
- Limit the learner pilot to two pages per code before full-extraction approval.

# 2026-09-08 — Pilot normalization

- Create separate report, device, and patient tables linked by `mdr_report_key`.
- Reject repeated report keys during pilot normalization rather than silently deduplicating.
- Preserve raw age text and create a separate standardized-years value plus QC status.
- Preserve list boundaries as JSON strings during the pilot; do not join list items with ambiguous delimiters.
- Exclude all raw narrative text from normalized CSV outputs.
- Generate project-specific device/patient row keys without treating them as real-world patient identifiers.

# 2026-09-09 — Pilot data profiling

- Calculate missingness against each field's own table-row denominator.
- Treat blank, `[]`, `{}`, and `null` strings as missing; retain numeric/text zero as observed.
- Reconcile extracted device and patient counts to their child-table row counts.
- Profile 0, 1, and more-than-1 child rows per report before any joins.
- Treat all bounded-pilot percentages as pipeline checks, not clinical or safety findings.
- Treat a JSON list containing only blank or null items (for example, `[""]`) as semantically missing while preserving the original normalized value.

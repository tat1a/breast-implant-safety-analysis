# Dashboard technical QA

## Publication status

**Status:** Passed for portfolio publication  
**Scope:** Final Power BI Desktop file and four-page PDF export  
**Reporting window:** 2020–2025  
**Product codes:** FTR and FWM

## Verified headline metrics

| Metric | Expected value |
| --- | ---: |
| API records | 237,213 |
| Unique scoped MDR reports | 237,194 |
| Cross-code overlaps removed | 19 |
| Device entries | 241,342 |
| Patient entries | 237,155 |
| Label-link mapping coverage | 98.79% |
| Reports with follow-up | 140,095 (59.06%) |
| Reports missing a usable event date | 52,411 (22.10%) |
| Reports with nonnegative lag available | 77.90% |
| Negative calculated lag records | 149 |
| Automated tests | 59 passing |

## Checks completed

- All visible report pages use a 1920 × 1080 canvas.
- The `QA – Validation` page is hidden in view mode.
- Annual report values reconcile to 237,194 scoped reports.
- Follow-up buckets are ordered `0`, `1`, `2`, `3+` and reconcile to 237,194.
- Reporting-lag quartiles exclude 149 negative calculated intervals.
- Event-date present/missing percentages reconcile to 100% within each year.
- Category and source-type labels are explicitly nonexclusive where applicable.
- Patient rows are labeled as extracted entries, not verified unique individuals.
- Permanent interpretation notes prohibit incidence, causality, and comparative-safety claims.
- The PBIX archive integrity check completed without compressed-data errors.

## Known export behavior

The supplied PDF renderer placed the first 1920 × 1080 report canvas in the upper-left
portion of a larger PDF page. The PBIX page metadata itself is correct; the repository
preview is cropped to the report canvas. This is treated as a static-export rendering
issue, not a dashboard-model defect.


# Data handling and reproducibility

## Current state

The full FTR/FWM 2020–2025 cohort has been extracted, normalized, profiled, and
analyzed locally. Raw and row-level datasets are intentionally excluded from Git.
Selected aggregate, non-identifiable results are published under
reports/final_evidence/.

## Local layers

- raw/ — immutable API pages and extraction checkpoints.
- interim/ — intermediate transformations.
- processed/ — normalized and analytical tables.
- external/ — reviewed source mappings and classification provenance.

## Governance rules

1. Raw snapshots are never edited in place.
2. Extraction manifests retain query identity, date range, pagination settings,
   checksums, record counts, and API-reported totals.
3. Raw, narrative, and row-level processed data remain excluded from Git.
4. API keys and credentials are never stored in the repository.
5. Narrative text requires a separate privacy-reviewed protocol before publication.
6. Processed tables are regenerated from raw inputs by versioned code.
7. Manual taxonomy decisions live in separate mapping tables with review metadata.
8. Missing and invalid values remain visible; they are not silently imputed.
9. Report, device-entry, and patient-entry levels remain separate to prevent
   denominator multiplication.
10. Only aggregate outputs that cannot expose report-level content are committed.

## Reproduction note

A fresh full extraction depends on the live openFDA API and can be time-consuming.
The extraction code is checkpointed and resumable. Downstream analysis can be rerun
from retained local normalized inputs without redownloading raw pages.

The public repository proves the resulting aggregate values through QC manifests,
tests, code, taxonomy, provenance records, and reconciliation rules; it does not
redistribute the complete source cohort.

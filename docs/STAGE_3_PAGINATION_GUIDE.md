# Stage 3 — Search-After Pagination and Checkpointing

## Why this stage exists

The FTR and FWM queries each exceed openFDA's ordinary `skip` ceiling. The
official paging guidance states that `skip`/`limit` navigation supports result
sets only up to approximately 26,000 hits. This project therefore follows the
API-provided `Link` header and its `search_after` cursor.

Official reference: https://open.fda.gov/apis/paging/

## Learning objectives

The project owner should be able to explain:

1. The difference between a page, page size, and total matches.
2. Why `skip` is insufficient for this cohort.
3. Why the next-page URL must be taken from the API response rather than invented.
4. Why a stable sort is required for sequential retrieval.
5. What a checkpoint contains and how it supports audit/recovery.
6. Why duplicate keys across pages are a QC warning rather than silently removed.

## Bounded pilot procedure

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.paginated_extractor --product-code FTR --page-size 5 --max-pages 2
.\.venv\Scripts\python.exe -m src.paginated_extractor --product-code FWM --page-size 5 --max-pages 2
```

The pilot deliberately retrieves only two pages per code: 10 records for FTR
and 10 for FWM. This is a pipeline test, not the analytical extraction.

## What to inspect

Open these local files:

- `data/raw/pagination_pilot/FTR_20200101_20251231/checkpoint.json`
- `data/raw/pagination_pilot/FWM_20200101_20251231/checkpoint.json`

For each checkpoint, verify:

| Check | Expected pilot result |
|---|---|
| `pages` | Two entries |
| `records_downloaded` | 10 |
| `unique_mdr_report_keys` | 10 unless the API source changed unexpectedly |
| `duplicate_keys_across_pages` | Empty list |
| `next_url_without_api_key` | Present because the pilot intentionally stopped early |
| `status` | `pilot_stopped` |

Each page has its own SHA-256 checksum, first key, last key, and record count.
Do not modify page files or checkpoints manually.

## Interpretation exercise

Answer in your own words:

1. Why would `limit=1000&skip=26000` fail to retrieve this complete cohort?
2. Who creates the `search_after` cursor: us or openFDA?
3. If two pages contain the same `mdr_report_key`, why should the pipeline flag it?
4. If the extraction stops after page 800, what information in the checkpoint helps diagnose or resume it?
5. Why does `records_downloaded=10` not mean ten patients?

## Gate before full extraction

Do not increase `max-pages` to retrieve the full cohort yet. Approval requires:

- both bounded pilots complete;
- all tests pass;
- no duplicate keys across pilot pages;
- checkpoint fields are understood;
- storage and restart strategy are reviewed;
- API-key handling is added without committing secrets.

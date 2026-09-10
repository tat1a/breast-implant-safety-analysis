# Stage 8 — Full Extraction Readiness

## Frozen cohort

- Source: openFDA Device Event API (MAUDE-derived records)
- Product codes: FTR and FWM
- Primary time field: `date_received`
- Window: 2020-01-01 through 2025-12-31, inclusive
- Unit retrieved: MDR report returned by the API
- Purpose: descriptive postmarket reporting-pattern and data-quality analysis

This is the full **scoped cohort**, not the whole MAUDE database. It cannot estimate
incidence, causality, comparative device safety, or unique-patient/device risk.

## Why a new extractor is required

The pilot intentionally stopped after two pages. The full extractor stores every raw
page atomically, records its SHA-256 checksum, and updates `checkpoint.json` only after
the page is safely written. If a run stops, rerunning the same command resumes from the
saved `next_url_without_api_key`; completed pages are not downloaded again.

Changing product code, date window, sort order, or page size invalidates the checkpoint
and is rejected. Existing raw JSON must never be edited manually because checksum
validation will fail.

## Gates before unbounded retrieval

1. All unit tests pass.
2. A one-page dry run completes for FTR and FWM in a fresh full-extraction directory.
3. Each checkpoint has the correct frozen identity and a non-empty API total.
4. Raw pages remain ignored by Git.
5. Available disk space is reviewed against the dry-run page size.
6. The unbounded commands are run separately for FTR and FWM.

## Commands

```powershell
# Set the free openFDA API key for this PowerShell session only.
# Never paste the real key into source code, Git, screenshots, or chat.
$env:OPENFDA_API_KEY = "PASTE_YOUR_KEY_HERE"

# Validation and bounded dry run only
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.full_extractor --product-code FTR --max-pages 1
.\.venv\Scripts\python.exe -m src.full_extractor --product-code FWM --max-pages 1
```

Close PowerShell after the extraction, or remove the session variable with:

```powershell
Remove-Item Env:OPENFDA_API_KEY
```

After checkpoint review, omit `--max-pages` to resume and retrieve all remaining pages:

```powershell
.\.venv\Scripts\python.exe -m src.full_extractor --product-code FTR
.\.venv\Scripts\python.exe -m src.full_extractor --product-code FWM
```

Run only one product-code extraction at a time. A rerun with identical arguments is
safe: it resumes a paused run or returns immediately when its QC-passed checkpoint is
already complete.

## Completion criteria

For both product codes: `status` is `complete`, `qc_gate_passed` is `true`, no duplicate
keys are present across pages, all page checksums validate, and downloaded record count
equals unique MDR report-key count. API `total` is retained as a reconciliation field,
not interpreted as a patient or device denominator.

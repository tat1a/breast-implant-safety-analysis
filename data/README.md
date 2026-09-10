# Data Handling Rules

## Current state

No data have been downloaded.

## Planned layers

- `raw/` — immutable API or bulk-file snapshots.
- `interim/` — normalized but not analysis-ready data.
- `processed/` — validated analytical tables.
- `external/` — classification or terminology reference files.

## Rules

1. Raw snapshots are never edited in place.
2. Every extraction records query, date, source, file size, checksum, and record count.
3. Large/raw data are excluded from Git unless redistribution is explicitly allowed and useful.
4. No credentials or API keys are stored in the repository.
5. Narrative text receives privacy review before publication or quotation.
6. Processed tables must be reproducible from raw inputs by documented code.
7. Any manually corrected classification is stored as a separate mapping table with reason and reviewer field.


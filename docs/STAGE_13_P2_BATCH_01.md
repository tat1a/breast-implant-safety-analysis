# Stage 13 — P2 batch 01 decisions

All 25 labels in batch P2-01 were reviewed with source-field context preserved.
Taxonomy v3 contains the 32 approved v2 rows plus these 25 decisions.

- 24 labels are included as reported device problems or health effects.
- `Insufficient Device Problem Information` is informational and is not treated as a complication.
- Generic `Cancer` remains nonspecific.
- BIA-ALCL is a specific category and is not merged with generic lymphoma.
- `Device Handling Problem` does not establish operator error.
- Counts describe coded report links and do not establish incidence or causality.

## Validate and measure coverage

```powershell
.\.venv\Scripts\python.exe -m src.validate_taxonomy_v2 `
  --taxonomy .\config\complication_taxonomy_v3.csv `
  --output .\data\processed\taxonomy_review\taxonomy_v3_validation.json

.\.venv\Scripts\python.exe -m src.prepare_taxonomy_review `
  --taxonomy .\config\complication_taxonomy_v3.csv `
  --output-dir .\data\processed\taxonomy_review_v3
```

# Stage 13 — P2 batch 02 decisions

Taxonomy v4 contains 82 mappings: all 57 v3 mappings plus 25 reviewed P2 labels.

- 22 new labels are included coded health effects or device problems.
- Off-label use, no known patient impact, and packaging-opening difficulty are informational.
- Broad terms remain broad; no causal link, user error, or disease subtype is inferred.
- After regeneration, only the final 24 P2 labels should remain.

## Run the whole gate and export the final P2 batch

```powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -t . -v

.\\.venv\\Scripts\\python.exe -m src.validate_taxonomy_v2 `
  --taxonomy .\\config\\complication_taxonomy_v4.csv `
  --output .\\data\\processed\\taxonomy_review\\taxonomy_v4_validation.json

.\\.venv\\Scripts\\python.exe -m src.prepare_taxonomy_review `
  --taxonomy .\\config\\complication_taxonomy_v4.csv `
  --output-dir .\\data\\processed\\taxonomy_review_v4

.\\.venv\\Scripts\\python.exe -m src.prepare_p2_review `
  --queue .\\data\\processed\\taxonomy_review_v4\\taxonomy_review_queue.csv `
  --output-dir .\\data\\processed\\taxonomy_p2_review_v4

Import-Csv .\\data\\processed\\taxonomy_p2_review_v4\\p2_review_packet.csv |
  ConvertTo-Json -Depth 3
```

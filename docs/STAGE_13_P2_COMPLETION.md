# Stage 13 — P2 taxonomy completion

Taxonomy v5 contains 106 reviewed mappings and completes all P1 and P2 labels.

- The final P2 batch adds 22 included terms and two informational no-impact terms.
- Generic anaplastic large cell lymphoma remains distinct from BIA-ALCL.
- Broad symptom and procedure terms retain their original specificity.
- Reported terms do not establish incidence, causality, or unique patients/devices.

## Rare-label policy

The remaining 439 P3 labels each occur in fewer than 100 reports. They remain auditable in
the review queue and are not automatically forced into broad categories. The analysis uses
taxonomy v5 as its prespecified primary mapping because it covers all P1/P2 labels and about
98.79% of label-report links. Clinically important P3 terms may be added in a documented
sensitivity taxonomy without changing the primary analysis silently.

## Validation and final coverage

```powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -t . -v
.\\.venv\\Scripts\\python.exe -m src.validate_taxonomy_v2 `
  --taxonomy .\\config\\complication_taxonomy_v5.csv `
  --output .\\data\\processed\\taxonomy_review\\taxonomy_v5_validation.json
.\\.venv\\Scripts\\python.exe -m src.prepare_taxonomy_review `
  --taxonomy .\\config\\complication_taxonomy_v5.csv `
  --output-dir .\\data\\processed\\taxonomy_review_v5
```

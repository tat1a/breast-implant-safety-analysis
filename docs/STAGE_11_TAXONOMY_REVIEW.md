# Stage 11 — Taxonomy Coverage Audit and Review Queue

The pilot taxonomy must not be silently generalized to all 545 full-cohort labels.
This stage performs exact source-field + raw-label matching, reports current coverage,
and creates an auditable queue for unmapped terms.

The full inventory's normalized field names are explicitly aliased to the cleaned-field
names used by taxonomy v1. Both names are retained in outputs so mappings can be audited
and promoted to taxonomy v2 without silent field-name mismatches.

Priority is based only on frequency: P1 >=1,000 reports; P2 100–999; P3 <100.
Priority does not indicate clinical severity. No automated clinical category is assigned
to unmapped labels. Informational/non-events such as unavailable codes, insufficient
information, or no clinical signs require explicit exclusion/status decisions rather
than being forced into a complication category.

Run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.prepare_taxonomy_review
Get-Content .\data\processed\taxonomy_review\taxonomy_coverage_summary.json
Import-Csv .\data\processed\taxonomy_review\taxonomy_review_queue.csv |
  Where-Object priority -eq "P1" |
  ConvertTo-Json -Depth 3
```

The P1 queue is reviewed first. Accepted decisions become a versioned taxonomy v2;
ambiguous terms remain explicitly unmapped or receive a reviewed broad category.
Report proportions remain reporting proportions, not incidence estimates.

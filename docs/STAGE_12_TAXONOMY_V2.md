# Stage 12 — Taxonomy v2, P1 Review Batch

Taxonomy v2 retains the 11 pilot mappings and adds the 21 reviewed P1 labels. It adds
`analysis_role` so included complications/findings are technically separated from
informational and unclassified codes.

- `included`: eligible for reported-complication/finding summaries;
- `informational`: explicitly not counted as a complication;
- `unclassified`: indicates an uncodable/nonspecific problem and is reported separately.

Device-problem and health-effect source fields remain distinct. General `Lymphoma` is
not converted to BIA-ALCL. Patient-field `Rupture` is not assumed to mean implant material
rupture. `Failure of Implant` is retained as a legacy broad reported term and must not be
interpreted as a specific failure mechanism.

Validate and recalculate coverage:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.validate_taxonomy_v2
.\.venv\Scripts\python.exe -m src.prepare_taxonomy_review --taxonomy .\config\complication_taxonomy_v2.csv --output-dir .\data\processed\taxonomy_review_v2
Get-Content .\data\processed\taxonomy_review_v2\taxonomy_coverage_summary.json
```

This taxonomy categorizes reported codes; it does not validate diagnosis, device
causality, incidence, prevalence, or comparative safety.

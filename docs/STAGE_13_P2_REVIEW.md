# Stage 13 — P2 taxonomy review

Stage 13 reviews the 74 labels occurring in 100–999 reports after taxonomy v2.
It improves interpretability, but should not be presented as incidence or causal evidence.

## Generate the review packet

```powershell
.\.venv\Scripts\python.exe -m src.prepare_p2_review
Get-Content .\data\processed\taxonomy_p2_review\p2_review_summary.json
Import-Csv .\data\processed\taxonomy_p2_review\p2_review_packet.csv |
  Where-Object batch_id -eq "P2-01" |
  ConvertTo-Json -Depth 3
```

The default packet has three frequency-ranked batches: 25, 25, and 24 labels.
Review decisions must preserve source-field meaning and use one of the v2 roles:
`included`, `informational`, or `unclassified`.

Do not infer causality, incidence, device failure, or a disease subtype from a broad coded term.

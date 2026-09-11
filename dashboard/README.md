# Power BI dashboard

## Purpose

The dashboard presents aggregate FDA MDR reporting patterns for the frozen FTR/FWM
2020–2025 cohort. It must never present report proportions as incidence, causal risk,
or comparative device/manufacturer safety.

## Build the input tables

From the repository root:

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -t . -v
.\.venv\Scripts\python.exe -m src.build_powerbi_dataset
Get-Content .\dashboard\data\PowerBI_QC.json
~~~

The builder refuses to export when an upstream QC gate or model reconciliation fails.
The output contains aggregate data only: no report-level rows, narratives, API keys,
or manufacturer safety ranking.

## Import

In Power BI Desktop select **Get data → Text/CSV** and import every CSV under
dashboard/data/. Do not import PowerBI_QC.json into the visual model.

Use **Transform data** to confirm:

- Year and all count fields: Whole number
- percentage and lag summary fields: Decimal number
- category/domain/source/field/value fields: Text

Disable automatic date hierarchies for this file; DimYear is the explicit time
dimension.

## Model relationships

Create single-direction, one-to-many relationships from DimYear[Year] to:

- AnnualReporting[Year]
- QueryComposition[Year]
- CategoryByYear[Year]
- DomainByYear[Year]
- ReportingLag[Year]
- EventDateCompleteness[Year]

KpiSummary is intentionally disconnected because it contains whole-cohort constants.
CategoryOverall, FollowupSummary, PatientEntryCharacteristics, ReporterSource,
SourceType, and DataDictionary are aggregate/disconnected presentation tables.

Do not create relationships between aggregate fact tables. That would multiply values.

## Recommended measures

~~~DAX
Scoped Reports =
MAX ( KpiSummary[ScopedReports] )

Reports With Follow-up =
MAX ( KpiSummary[ReportsWithFollowup] )

Reports With Follow-up % =
DIVIDE ( [Reports With Follow-up], [Scoped Reports] )

Reports Missing Event Date =
MAX ( KpiSummary[ReportsMissingEventDate] )

Annual Reports =
SUM ( AnnualReporting[ReportCount] )

Category Reports =
SUM ( CategoryByYear[ReportCount] )

Selected Category Reporting % =
DIVIDE ( [Category Reports], [Annual Reports] )
~~~

Format the percentage measures as Percentage with one or two decimal places. Do not
sum precomputed percentage columns across categories or years.

## Page plan

### 1 — Executive overview

- Cards: Scoped Reports, Device Entries, Patient Entries, Reports With Follow-up %,
  Reports Missing Event Date.
- Line chart: AnnualReporting Year versus ReportCount.
- Horizontal bar chart: top CategoryOverall categories by PctOfAllReports.
- Permanent visible warning: “MDR report proportions—not incidence, causality, or
  comparative safety.”

### 2 — Reporting trends

- Year slicer using DimYear.
- Stacked columns: QueryComposition by QueryGroup.
- Lines or small multiples: CategoryByYear reporting proportion for selected categories.
- Domain trend chart using DomainByYear.
- Context note that changes may reflect coding, reporting, publicity, or regulation.

### 3 — Complication categories

- ClinicalDomain and Category slicers.
- Category count and reporting-proportion visuals.
- Category × year heatmap or matrix.
- Tooltip stating that categories overlap within reports.

### 4 — Data quality and follow-up

- FollowupSummary column chart.
- ReportingLag median with Q1/Q3 information.
- EventDateCompleteness missing percentage by year.
- PatientEntryCharacteristics completeness visuals labeled “patient entries, not
  unique patients.”
- NegativeLagRows card.

### 5 — Methods and limitations

- Data source, product codes, date window, analytical unit, taxonomy coverage,
  extraction/QC method, and explicit prohibited inferences.
- Link or QR code to the GitHub repository after it becomes public.

## Design standard

Use a restrained clinical palette, consistent title capitalization, generous spacing,
and no 3D charts. Prefer dark navy, teal, white, and one warm alert color. Every page
must contain a compact inference warning. Use report counts or explicitly labeled
“percent of scoped MDR reports”; never label a visual “risk,” “rate,” or “incidence.”

## Publication

The PBIX file remains local by default. Export a PDF and page screenshots for GitHub.
Online publishing requires Power BI Service access and should occur only after the
dashboard passes privacy, denominator, filter, and visual-label review.

"""Apply the reviewed v1 complication taxonomy to cleaned pilot lists."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def load_taxonomy(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows = read_csv(path)
    mapping: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["source_field"], row["raw_label"])
        if key in mapping:
            raise ValueError(f"Duplicate taxonomy key: {key}")
        mapping[key] = row
    return mapping


def classify(cleaned_dir: Path, taxonomy_path: Path, output_dir: Path) -> None:
    taxonomy = load_taxonomy(taxonomy_path)
    report_rows = read_csv(cleaned_dir / "report_lists_cleaned.csv")
    patient_rows = read_csv(cleaned_dir / "patient_lists_cleaned.csv")
    labels_by_report: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in report_rows:
        for label in json.loads(row["product_problems_cleaned_json"]):
            labels_by_report[row["mdr_report_key"]].append(("product_problems_cleaned_json", label))
    for row in patient_rows:
        for label in json.loads(row["patient_problems_cleaned_json"]):
            labels_by_report[row["mdr_report_key"]].append(("patient_problems_cleaned_json", label))

    classified: list[dict] = []
    unmapped_counts: Counter[tuple[str, str]] = Counter()
    for report_key, labels in sorted(labels_by_report.items()):
        seen_categories: set[str] = set()
        for source_field, label in labels:
            rule = taxonomy.get((source_field, label))
            if rule is None:
                unmapped_counts[(source_field, label)] += 1
                continue
            category = rule["category"]
            if category in seen_categories:
                continue
            seen_categories.add(category)
            classified.append({
                "mdr_report_key": report_key,
                "category": category,
                "clinical_domain": rule["clinical_domain"],
                "specificity": rule["specificity"],
            })

    unmapped = [
        {"source_field": field, "raw_label": label, "report_count": count}
        for (field, label), count in sorted(unmapped_counts.items())
    ]
    write_csv(output_dir / "report_complication_categories.csv", ["mdr_report_key", "category", "clinical_domain", "specificity"], classified)
    write_csv(output_dir / "unmapped_complication_labels.csv", ["source_field", "raw_label", "report_count"], unmapped)
    summary = {
        "scope": "bounded pilot only",
        "reports_with_source_labels": len(labels_by_report),
        "report_category_rows": len(classified),
        "unmapped_label_types": len(unmapped),
        "warning": "Categories describe reported coded terms, not incidence, causality, comparative safety, or unique patients/devices.",
    }
    (output_dir / "taxonomy_qc_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify cleaned pilot complication labels.")
    parser.add_argument("--cleaned-dir", type=Path, default=Path("data/processed/pilot_cleaned"))
    parser.add_argument("--taxonomy", type=Path, default=Path("config/complication_taxonomy_v1.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/pilot_taxonomy"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    classify(args.cleaned_dir, args.taxonomy, args.output_dir)
    print(f"Pilot taxonomy outputs: {args.output_dir}")

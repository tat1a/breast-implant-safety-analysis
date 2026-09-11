"""Audit v1 taxonomy coverage and create a frequency-prioritized review queue."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

INVENTORY_TO_TAXONOMY_FIELD = {
    "product_problems_json": "product_problems_cleaned_json",
    "patient_problems_json": "patient_problems_cleaned_json",
}

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def priority(report_count: int) -> str:
    if report_count >= 1000: return "P1"
    if report_count >= 100: return "P2"
    return "P3"


def prepare(inventory_path: Path, taxonomy_path: Path, output_dir: Path) -> Path:
    inventory = read_csv(inventory_path)
    taxonomy = read_csv(taxonomy_path)
    mapping = {}
    for row in taxonomy:
        key = (row["source_field"], row["raw_label"])
        if key in mapping: raise ValueError(f"Duplicate taxonomy key: {key}")
        mapping[key] = row

    mapped=[]; queue=[]; link_counts=Counter(); label_counts=Counter(); priority_counts=Counter()
    for row in inventory:
        inventory_field = row["source_field"]
        taxonomy_field = INVENTORY_TO_TAXONOMY_FIELD.get(inventory_field, inventory_field)
        key=(taxonomy_field,row["raw_label"]); count=int(row["report_count"])
        label_counts["total"] += 1; link_counts["total"] += count
        rule=mapping.get(key)
        base={"source_field":inventory_field,"taxonomy_source_field":taxonomy_field,
              "raw_label":key[1],"report_count":count,
              "item_occurrences":int(row["item_occurrences"]),"pct_of_reports":row["pct_of_reports"]}
        if rule:
            label_counts["mapped"] += 1; link_counts["mapped"] += count
            mapped.append({**base,"category":rule["category"],"clinical_domain":rule["clinical_domain"],
                           "specificity":rule["specificity"],"taxonomy_status":rule["status"]})
        else:
            level=priority(count); priority_counts[level] += 1
            queue.append({**base,"priority":level,"proposed_category":"","proposed_clinical_domain":"",
                          "proposed_specificity":"","decision":"pending_review","review_notes":""})
    queue.sort(key=lambda r: ({"P1":0,"P2":1,"P3":2}[r["priority"]],-r["report_count"],r["source_field"],r["raw_label"]))
    mapped.sort(key=lambda r:-r["report_count"])
    fields=["source_field","taxonomy_source_field","raw_label","report_count","item_occurrences","pct_of_reports"]
    write_csv(output_dir/"mapped_labels.csv",fields+["category","clinical_domain","specificity","taxonomy_status"],mapped)
    write_csv(output_dir/"taxonomy_review_queue.csv",fields+["priority","proposed_category","proposed_clinical_domain","proposed_specificity","decision","review_notes"],queue)
    taxonomy_version = taxonomy_path.stem.removeprefix("complication_taxonomy_")
    summary={"scope":f"full FTR/FWM cohort label inventory against taxonomy {taxonomy_version}",
             "taxonomy_version":taxonomy_version,
             "taxonomy_file":taxonomy_path.name,
             "distinct_labels_total":label_counts["total"],"distinct_labels_exact_mapped":label_counts["mapped"],
             "distinct_labels_unmapped":label_counts["total"]-label_counts["mapped"],
             "label_report_links_total":link_counts["total"],"label_report_links_exact_mapped":link_counts["mapped"],
             "exact_mapping_link_coverage_pct":round(100*link_counts["mapped"]/link_counts["total"],2) if link_counts["total"] else 0,
             "unmapped_priority_counts":dict(priority_counts),
             "qc_gate_passed":label_counts["total"]==len(mapped)+len(queue),
             "warning":"Coverage uses label-report links, which can sum above unique reports because reports may contain multiple labels."}
    path=output_dir/"taxonomy_coverage_summary.json"
    path.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return path


def parse_args():
    p=argparse.ArgumentParser(description="Prepare full-cohort taxonomy review queue.")
    p.add_argument("--inventory",type=Path,default=Path("data/processed/full_profile/complication_label_inventory.csv"))
    p.add_argument("--taxonomy",type=Path,default=Path("config/complication_taxonomy_v1.csv"))
    p.add_argument("--output-dir",type=Path,default=Path("data/processed/taxonomy_review")); return p.parse_args()


if __name__=="__main__":
    a=parse_args(); print(f"Taxonomy review: {prepare(a.inventory,a.taxonomy,a.output_dir)}")

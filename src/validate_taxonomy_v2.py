"""Validate taxonomy v2 before it is used for full-cohort classification."""

from __future__ import annotations

import argparse,csv,json
from collections import Counter
from pathlib import Path

REQUIRED=("source_field","raw_label","category","clinical_domain","specificity","analysis_role","terminology_context","status","review_note")
ROLES={"included","informational","unclassified"}
SPECIFICITY={"specific","moderate","nonspecific"}
SOURCE_FIELDS={"product_problems_cleaned_json","patient_problems_cleaned_json"}

def validate(path:Path,output:Path|None=None)->dict:
    with path.open(encoding="utf-8-sig",newline="") as h:
        reader=csv.DictReader(h)
        if tuple(reader.fieldnames or ())!=REQUIRED: raise ValueError("taxonomy v2 schema mismatch")
        rows=list(reader)
    seen=set();roles=Counter();errors=[]
    for number,row in enumerate(rows,start=2):
        key=(row["source_field"],row["raw_label"])
        if key in seen: errors.append(f"row {number}: duplicate key {key}")
        seen.add(key)
        if row["source_field"] not in SOURCE_FIELDS: errors.append(f"row {number}: invalid source_field")
        if row["analysis_role"] not in ROLES: errors.append(f"row {number}: invalid analysis_role")
        if row["specificity"] not in SPECIFICITY: errors.append(f"row {number}: invalid specificity")
        if not all(row[field].strip() for field in REQUIRED): errors.append(f"row {number}: blank required value")
        roles[row["analysis_role"]]+=1
    if errors: raise ValueError("; ".join(errors))
    summary={"taxonomy_version":"v2","rows":len(rows),"unique_keys":len(seen),
             "analysis_role_counts":dict(roles),"validation_passed":True}
    if output:
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    return summary

def parse_args():
    p=argparse.ArgumentParser();p.add_argument("--taxonomy",type=Path,default=Path("config/complication_taxonomy_v2.csv"));p.add_argument("--output",type=Path,default=Path("data/processed/taxonomy_review/taxonomy_v2_validation.json"));return p.parse_args()

if __name__=="__main__":
    a=parse_args();print(json.dumps(validate(a.taxonomy,a.output),indent=2))

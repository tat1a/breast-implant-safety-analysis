import csv
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.build_analytic_dataset import build, parse_list


def write(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


class BuildAnalyticDatasetTests(unittest.TestCase):
    def test_parse_list_rejects_scalar(self):
        with self.assertRaisesRegex(ValueError, "JSON list"):
            parse_list('"x"', "field")
    def test_parse_list_ignores_json_null(self):
        self.assertEqual(parse_list('[null, "Pain", ""]', "field"), ["Pain"])

    def test_build_preserves_report_granularity_and_deduplicates_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / "in"; source.mkdir()
            write(source / "reports.csv", [
                {"mdr_report_key":"1","date_received":"20200102","date_of_event":"20191201",
                 "product_problems_json":'["Break","Break"]',"query_product_codes_json":'["FTR"]'},
                {"mdr_report_key":"2","date_received":"20210102","date_of_event":"",
                 "product_problems_json":"[]","query_product_codes_json":'["FWM"]'},
            ])
            write(source / "patients.csv", [
                {"mdr_report_key":"1","patient_problems_json":'["Pain","Pain"]'},
                {"mdr_report_key":"1","patient_problems_json":'["Pain"]'},
            ])
            taxonomy = root / "taxonomy_vx.csv"
            fields=["source_field","raw_label","category","clinical_domain","specificity",
                    "analysis_role","terminology_context","status","review_note"]
            with taxonomy.open("w", newline="", encoding="utf-8") as handle:
                writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
                writer.writerows([
                    {"source_field":"product_problems_cleaned_json","raw_label":"Break","category":"break",
                     "clinical_domain":"device","specificity":"specific","analysis_role":"included",
                     "terminology_context":"device_problem","status":"approved","review_note":"x"},
                    {"source_field":"patient_problems_cleaned_json","raw_label":"Pain","category":"pain",
                     "clinical_domain":"symptom","specificity":"moderate","analysis_role":"included",
                     "terminology_context":"health_effect","status":"approved","review_note":"x"},
                ])
            qc=json.loads(build(source,taxonomy,root/"out").read_text())
            self.assertTrue(qc["qc_gate_passed"])
            self.assertEqual(qc["output_report_rows"],2)
            self.assertEqual(qc["report_label_links"],2)
            self.assertEqual(qc["missing_date_of_event"],1)
            self.assertEqual(qc["invalid_nonmissing_date_of_event"],0)
            analysis=pd.read_csv(root/"out"/"report_analysis.csv")
            self.assertEqual(len(analysis),2)
            self.assertEqual(int(analysis.loc[analysis["mdr_report_key"]==1,"included_category_count"].iloc[0]),2)

    def test_duplicate_report_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"in";source.mkdir()
            write(source/"reports.csv",[
                {"mdr_report_key":"1","product_problems_json":"[]"},
                {"mdr_report_key":"1","product_problems_json":"[]"},
            ])
            write(source/"patients.csv",[{"mdr_report_key":"1","patient_problems_json":"[]"}])
            taxonomy=root/"taxonomy.csv"
            fields=["source_field","raw_label","category","clinical_domain","specificity",
                    "analysis_role","terminology_context","status","review_note"]
            pd.DataFrame(columns=fields).to_csv(taxonomy,index=False)
            with self.assertRaisesRegex(ValueError,"duplicate mdr_report_key"):
                build(source,taxonomy,root/"out")

    def test_inventory_reconciliation_is_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"in";source.mkdir()
            write(source/"reports.csv",[{"mdr_report_key":"1","date_received":"20200101",
                "date_of_event":"","product_problems_json":'["Break"]',
                "query_product_codes_json":'["FTR"]'}])
            write(source/"patients.csv",[{"mdr_report_key":"1","patient_problems_json":"[]"}])
            taxonomy=root/"taxonomy.csv"
            fields=["source_field","raw_label","category","clinical_domain","specificity",
                    "analysis_role","terminology_context","status","review_note"]
            write(taxonomy,[{"source_field":"product_problems_cleaned_json","raw_label":"Break",
                "category":"break","clinical_domain":"device","specificity":"specific",
                "analysis_role":"included","terminology_context":"device_problem",
                "status":"approved","review_note":"x"}])
            inventory=root/"inventory.csv"
            write(inventory,[{"report_count":2}])
            qc=json.loads(build(source,taxonomy,root/"out",inventory).read_text())
            self.assertFalse(qc["qc_gate_passed"])
            self.assertEqual(qc["report_label_link_reconciliation_difference"],-1)


if __name__ == "__main__":
    unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.analyze_reporting_patterns import analyze


class ReportingPatternTests(unittest.TestCase):
    def test_outputs_reconcile_and_figures_contain_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"in";source.mkdir()
            pd.DataFrame([
                {"mdr_report_key":"1","received_year":2020,"mapped_label_count":1,
                 "is_ftr_query":True,"is_fwm_query":False,"date_of_event_iso":"2019-01-01",
                 "report_source_code":"M","reporter_occupation_code":"P"},
                {"mdr_report_key":"2","received_year":2021,"mapped_label_count":1,
                 "is_ftr_query":False,"is_fwm_query":True,"date_of_event_iso":"",
                 "report_source_code":"M","reporter_occupation_code":"C"},
                {"mdr_report_key":"3","received_year":2021,"mapped_label_count":0,
                 "is_ftr_query":True,"is_fwm_query":True,"date_of_event_iso":"",
                 "report_source_code":"U","reporter_occupation_code":"C"},
            ]).to_csv(source/"report_analysis.csv",index=False)
            pd.DataFrame([
                {"mdr_report_key":"1","category":"rupture","clinical_domain":"device_integrity","analysis_role":"included"},
                {"mdr_report_key":"2","category":"pain","clinical_domain":"patient_symptom","analysis_role":"included"},
                {"mdr_report_key":"2","category":"note","clinical_domain":"none","analysis_role":"informational"},
            ]).to_csv(source/"report_category_links.csv",index=False)
            qc=json.loads(analyze(source,root/"out").read_text())
            self.assertTrue(qc["qc_gate_passed"])
            self.assertEqual(qc["annual_report_reconciliation_difference"],0)
            self.assertEqual(qc["query_group_reconciliation_difference"],0)
            self.assertEqual(len(qc["figures_created"]),4)
            svg=(root/"out"/"figures"/"annual_report_counts.svg").read_text()
            self.assertIn("not incidence",svg)

    def test_duplicate_reports_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/"in";source.mkdir()
            pd.DataFrame([{"mdr_report_key":"1"},{"mdr_report_key":"1"}]).to_csv(source/"report_analysis.csv",index=False)
            pd.DataFrame(columns=["mdr_report_key","category","clinical_domain","analysis_role"]).to_csv(
                source/"report_category_links.csv",index=False
            )
            with self.assertRaisesRegex(ValueError,"one row per report"):
                analyze(source,root/"out")


if __name__ == "__main__":
    unittest.main()

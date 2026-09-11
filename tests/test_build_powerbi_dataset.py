import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.build_powerbi_dataset import build, pascal


class PowerBIDatasetTests(unittest.TestCase):
    def test_pascal_names(self):
        self.assertEqual(pascal("pct_of_year_reports"), "PctOfYearReports")

    def test_outputs_are_aggregate_and_reconcile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); reporting = root/"reporting"; chars = root/"chars"; final = root/"final"
            reporting.mkdir(); chars.mkdir(); final.mkdir()
            (reporting/"reporting_analysis_qc.json").write_text(json.dumps({"qc_gate_passed": True}))
            (chars/"cohort_characteristics_qc.json").write_text(json.dumps({"qc_gate_passed": True}))
            (final/"final_evidence_qc.json").write_text(json.dumps({"qc_gate_passed": True,"input_report_rows": 6}))
            years = list(range(2020, 2026))
            pd.DataFrame({"received_year":years,"report_count":[1]*6,
                          "reports_with_mapped_labels":[1]*6,"year_over_year_change_pct":[None,0,0,0,0,0]}).to_csv(reporting/"annual_reporting_trends.csv",index=False)
            pd.DataFrame({"received_year":years,"query_group":["FTR only"]*6,
                          "report_count":[1]*6,"pct_of_year_reports":[100]*6}).to_csv(reporting/"annual_query_composition.csv",index=False)
            pd.DataFrame({"received_year":years,"clinical_domain":["device"]*6,
                          "category":["rupture"]*6,"report_count":[1]*6,
                          "pct_of_year_reports":[100]*6}).to_csv(reporting/"category_year_reporting.csv",index=False)
            pd.DataFrame([{"clinical_domain":"device","category":"rupture","report_count":6,"pct_of_all_reports":100}]).to_csv(reporting/"category_overall_reporting.csv",index=False)
            pd.DataFrame({"received_year":years,"clinical_domain":["device"]*6,
                          "report_count":[1]*6,"pct_of_year_reports":[100]*6}).to_csv(reporting/"domain_year_reporting.csv",index=False)
            pd.DataFrame([{"report_source_code":"M","reporter_occupation_code":"P",
                           "report_count":6,"pct_of_all_reports":100}]).to_csv(reporting/"reporter_source_summary.csv",index=False)
            pd.DataFrame({"received_year":years,"report_count":[1]*6,"event_date_present":[1]*6,
                          "event_date_missing":[0]*6,"event_date_missing_pct":[0]*6}).to_csv(reporting/"event_date_completeness_by_year.csv",index=False)
            pd.DataFrame([{"followup_bucket":"0","report_count":6,"pct_of_all_reports":100}]).to_csv(chars/"followup_summary.csv",index=False)
            pd.DataFrame({"received_year":years,"report_count":[1]*6,"lag_available":[1]*6,
                          "negative_lag_rows":[0]*6,"median_nonnegative_lag_days":[5]*6,
                          "q1_nonnegative_lag_days":[2]*6,"q3_nonnegative_lag_days":[8]*6}).to_csv(chars/"event_to_receipt_lag_by_year.csv",index=False)
            pd.DataFrame([{"field":"patient_age_status","value":"valid","row_count":6,"pct_of_rows":100}]).to_csv(chars/"patient_entry_characteristics.csv",index=False)
            pd.DataFrame([{"source_type":"HEALTH PROFESSIONAL","report_count":6,"pct_of_all_reports":100}]).to_csv(chars/"source_type_summary.csv",index=False)
            pd.DataFrame([
                ("scoped MDR reports",6),("patient entries",6),("device entries",7),
                ("reports with at least one follow-up",0),("reports with event-to-receipt lag available",6),
                ("reports missing a usable event date",0),("negative event-to-receipt lag rows",0),
            ],columns=["metric","value"]).to_csv(final/"final_summary_metrics.csv",index=False)
            qc=json.loads(build(reporting,chars,final,root/"out").read_text())
            self.assertTrue(qc["qc_gate_passed"])
            self.assertFalse(qc["contains_row_level_reports"])
            self.assertEqual(len(pd.read_csv(root/"out"/"DimYear.csv")),6)
            self.assertTrue((root/"out"/"DataDictionary.csv").exists())


if __name__ == "__main__":
    unittest.main()

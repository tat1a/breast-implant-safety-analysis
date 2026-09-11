import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.summarize_cohort_characteristics import parse_list, summarize


class CohortCharacteristicsTests(unittest.TestCase):
    def test_parse_list_ignores_nulls(self):
        self.assertEqual(parse_list('[null, "FOLLOWUP"]'), ["FOLLOWUP"])

    def test_characteristics_reconcile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);analytic=root/"analytic";normalized=root/"normalized";reporting=root/"reporting"
            analytic.mkdir();normalized.mkdir();reporting.mkdir()
            pd.DataFrame([
                {"mdr_report_key":"1","event_type":"Injury","report_source_code":"M",
                 "reporter_occupation_code":"P","reporter_country_code":"US","event_location":"I",
                 "source_type_json":'["HEALTH PROFESSIONAL"]',
                 "type_of_report_json":'["Initial submission","Followup","Followup"]',
                 "date_received_iso":"2020-02-01","date_of_event_iso":"2020-01-01","received_year":2020},
                {"mdr_report_key":"2","event_type":"Injury","report_source_code":"M",
                 "reporter_occupation_code":"","reporter_country_code":"","event_location":"",
                 "source_type_json":'["CONSUMER"]',"type_of_report_json":'["Initial submission"]',
                 "date_received_iso":"2021-01-01","date_of_event_iso":"","received_year":2021},
            ]).to_csv(analytic/"report_analysis.csv",index=False)
            pd.DataFrame([
                {"mdr_report_key":"1","patient_age_years":"35","patient_age_status":"valid",
                 "patient_sex":"Female","patient_ethnicity":"","patient_race":""},
                {"mdr_report_key":"2","patient_age_years":"","patient_age_status":"missing",
                 "patient_sex":"","patient_ethnicity":"","patient_race":""},
            ]).to_csv(normalized/"patients.csv",index=False)
            pd.DataFrame([
                {"mdr_report_key":"1","manufacturer_d_name":"Maker","brand_name":"Brand"},
            ]).to_csv(normalized/"devices.csv",index=False)
            pd.DataFrame([
                {"received_year":2020,"clinical_domain":"device","category":"rupture","pct_of_year_reports":50},
                {"received_year":2021,"clinical_domain":"device","category":"rupture","pct_of_year_reports":25},
            ]).to_csv(reporting/"category_year_reporting.csv",index=False)
            qc=json.loads(summarize(analytic,normalized,reporting,root/"out").read_text())
            self.assertTrue(qc["qc_gate_passed"])
            self.assertEqual(qc["followup_report_reconciliation_difference"],0)
            trend=pd.read_csv(root/"out"/"category_trend_2020_2025.csv")
            self.assertEqual(float(trend.iloc[0]["absolute_change_percentage_points"]),-25)


if __name__ == "__main__":
    unittest.main()

import csv, json, tempfile, unittest
from pathlib import Path
from src.profile_full import parse_list, profile_full

class FullProfileTests(unittest.TestCase):
    def test_parse_list_rejects_scalar(self):
        with self.assertRaises(ValueError): parse_list('"rupture"')

    def test_stream_profile_reconciles_and_counts_unique_reports_per_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inp=root/"in"; inp.mkdir()
            (inp/"normalization_qc.json").write_text(json.dumps({"qc_gate_passed":True,"scope":"test","unique_report_rows":2,"device_rows":1,"patient_rows":2}))
            tables={
                "reports":[{"mdr_report_key":"1","date_received":"20200101","date_of_event":"","report_source_code":"M","reporter_occupation_code":"P","reporter_country_code":"","event_location":"I","product_problems_json":"[\"Rupture\",\"Rupture\"]","device_rows_extracted":"1","patient_rows_extracted":"1","event_type":"Injury"},{"mdr_report_key":"2","date_received":"20210101","date_of_event":"20200101","report_source_code":"M","reporter_occupation_code":"P","reporter_country_code":"US","event_location":"I","product_problems_json":"[]","device_rows_extracted":"0","patient_rows_extracted":"1","event_type":"Injury"}],
                "devices":[{"mdr_report_key":"1","device_report_product_code":"FTR","manufacturer_d_country":"US","device_availability":"Y","device_evaluated_by_manufacturer":"Y"}],
                "patients":[{"mdr_report_key":"1","patient_age_status":"valid","patient_sex":"F","patient_ethnicity":"","patient_race":"","patient_problems_json":"[\"Pain\"]"},{"mdr_report_key":"2","patient_age_status":"missing","patient_sex":"","patient_ethnicity":"","patient_race":"","patient_problems_json":"[\"Pain\"]"}]}
            for name,rows in tables.items():
                with (inp/f"{name}.csv").open("w",newline="",encoding="utf-8") as h:
                    w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
            summary=json.loads(profile_full(inp,root/"out").read_text())
            self.assertTrue(summary["qc_gate_passed"])
            with (root/"out"/"complication_label_inventory.csv").open(encoding="utf-8-sig") as h:
                rows=list(csv.DictReader(h))
            rupture=next(r for r in rows if r["raw_label"]=="Rupture")
            self.assertEqual(rupture["report_count"],"1"); self.assertEqual(rupture["item_occurrences"],"2")

if __name__=="__main__": unittest.main()

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.build_final_evidence import build


class FinalEvidenceTests(unittest.TestCase):
    def test_build_reconciles_and_writes_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); reporting = root / "reporting"; chars = root / "chars"
            reporting.mkdir(); chars.mkdir()
            (reporting / "reporting_analysis_qc.json").write_text(
                json.dumps({"qc_gate_passed": True, "input_report_rows": 2})
            )
            (chars / "cohort_characteristics_qc.json").write_text(json.dumps({
                "qc_gate_passed": True, "patient_entry_rows": 2, "device_entry_rows": 3
            }))
            pd.DataFrame([
                {"received_year": 2020, "report_count": 1,
                 "reports_with_mapped_labels": 1, "year_over_year_change_pct": ""},
                {"received_year": 2021, "report_count": 1,
                 "reports_with_mapped_labels": 1, "year_over_year_change_pct": 0},
            ]).to_csv(reporting / "annual_reporting_trends.csv", index=False)
            pd.DataFrame([{"clinical_domain": "device", "category": "rupture",
                           "report_count": 2, "pct_of_all_reports": 100.0}]).to_csv(
                reporting / "category_overall_reporting.csv", index=False
            )
            pd.DataFrame([
                {"followup_bucket": "0", "report_count": 1, "pct_of_all_reports": 50},
                {"followup_bucket": "1", "report_count": 1, "pct_of_all_reports": 50},
                {"followup_bucket": "2", "report_count": 0, "pct_of_all_reports": 0},
                {"followup_bucket": "3+", "report_count": 0, "pct_of_all_reports": 0},
            ]).to_csv(chars / "followup_summary.csv", index=False)
            pd.DataFrame([
                {"received_year": 2020, "report_count": 1, "lag_available": 1,
                 "negative_lag_rows": 0, "median_nonnegative_lag_days": 10},
                {"received_year": 2021, "report_count": 1, "lag_available": 0,
                 "negative_lag_rows": 0, "median_nonnegative_lag_days": float("nan")},
            ]).to_csv(chars / "event_to_receipt_lag_by_year.csv", index=False)
            pd.DataFrame([
                {"field": "patient_age_status", "value": "valid", "row_count": 1},
                {"field": "patient_age_status", "value": "missing", "row_count": 1},
            ]).to_csv(chars / "patient_entry_characteristics.csv", index=False)
            qc_path = build(reporting, chars, root / "out")
            qc = json.loads(qc_path.read_text())
            self.assertTrue(qc["qc_gate_passed"])
            report = (root / "out" / "FINAL_EVIDENCE_SUMMARY.md").read_text()
            self.assertIn("cannot estimate incidence", report)
            self.assertIn("1 reports (50.00%)", report)

    def test_rejects_failed_upstream_qc(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); reporting = root / "reporting"; chars = root / "chars"
            reporting.mkdir(); chars.mkdir()
            (reporting / "reporting_analysis_qc.json").write_text(
                json.dumps({"qc_gate_passed": False})
            )
            with self.assertRaises(ValueError):
                build(reporting, chars, root / "out")


if __name__ == "__main__":
    unittest.main()

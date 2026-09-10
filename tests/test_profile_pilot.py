import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.profile_pilot import bucket_count, is_missing, profile


class ProfilePilotTests(unittest.TestCase):
    def test_missing_definition(self):
        self.assertTrue(is_missing(""))
        self.assertTrue(is_missing("[]"))
        self.assertTrue(is_missing('[""]'))
        self.assertTrue(is_missing('["  ", null]'))
        self.assertFalse(is_missing('["Pain", ""]'))
        self.assertFalse(is_missing("0"))

    def test_multiplicity_buckets(self):
        self.assertEqual(bucket_count("0"), "0")
        self.assertEqual(bucket_count("1"), "1")
        self.assertEqual(bucket_count("3"), ">1")
        self.assertEqual(bucket_count("bad"), "invalid")

    def test_profile_reconciles_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "normalized"
            source.mkdir()
            fixtures = {
                "reports": (
                    ["mdr_report_key", "event_type", "report_source_code", "reporter_occupation_code", "device_rows_extracted", "patient_rows_extracted"],
                    [["R1", "Injury", "Manufacturer", "Physician", "2", "1"]],
                ),
                "devices": (
                    ["mdr_report_key", "device_report_product_code"],
                    [["R1", "FTR"], ["R1", "FTR"]],
                ),
                "patients": (
                    ["mdr_report_key", "patient_age_status", "patient_sex"],
                    [["R1", "valid", "F"]],
                ),
            }
            for name, (headers, rows) in fixtures.items():
                with (source / f"{name}.csv").open("w", newline="", encoding="utf-8-sig") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(headers)
                    writer.writerows(rows)
            summary_path = profile(source, root / "profile")
            summary = json.loads(summary_path.read_text())
            self.assertEqual(summary["reports_with_multiple_devices"], 1)
            self.assertEqual(summary["device_row_reconciliation_difference"], 0)
            self.assertEqual(summary["patient_row_reconciliation_difference"], 0)


if __name__ == "__main__":
    unittest.main()

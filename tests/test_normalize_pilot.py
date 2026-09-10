import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.normalize_pilot import json_list, normalize, parse_age


class NormalizePilotTests(unittest.TestCase):
    def test_age_years(self):
        self.assertEqual(parse_age("41 YR"), (41.0, "valid"))

    def test_age_months(self):
        self.assertEqual(parse_age("18 MO"), (1.5, "valid"))

    def test_age_missing_and_invalid(self):
        self.assertEqual(parse_age(""), ("", "missing"))
        self.assertEqual(parse_age("999 YR"), ("", "invalid_range"))

    def test_list_encoding_preserves_duplicates(self):
        self.assertEqual(json_list(["A", "A"]), '["A","A"]')

    def test_normalization_preserves_entity_granularity(self):
        record = {
            "mdr_report_key": "R1",
            "type_of_report": ["Initial submission"],
            "device": [{"device_sequence_number": "1"}, {"device_sequence_number": "2"}],
            "patient": [{"patient_sequence_number": "1", "patient_age": "24 MO"}],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / "raw" / "FTR"
            raw.mkdir(parents=True)
            (raw / "page_00001.json").write_text(
                json.dumps({"results": [record]}), encoding="utf-8"
            )
            qc_path = normalize(root / "raw", root / "processed")
            qc = json.loads(qc_path.read_text())
            self.assertEqual(qc["report_rows"], 1)
            self.assertEqual(qc["device_rows"], 2)
            self.assertEqual(qc["patient_rows"], 1)
            with (root / "processed" / "reports.csv").open(encoding="utf-8-sig") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 1)

    def test_duplicate_report_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / "raw"
            raw.mkdir()
            payload = json.dumps({"results": [{"mdr_report_key": "R1"}]})
            (raw / "page_00001.json").write_text(payload)
            (raw / "page_00002.json").write_text(payload)
            with self.assertRaisesRegex(ValueError, "Duplicate mdr_report_key"):
                normalize(raw, root / "processed")


if __name__ == "__main__":
    unittest.main()

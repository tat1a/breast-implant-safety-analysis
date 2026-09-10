import csv
import tempfile
import unittest
from pathlib import Path

from src.clean_pilot_lists import clean, clean_list, clean_source_types, parse_json_list


class CleanPilotListTests(unittest.TestCase):
    def test_parse_requires_list(self):
        self.assertEqual(parse_json_list('["Pain"]'), ["Pain"])
        with self.assertRaises(ValueError):
            parse_json_list('{"value":"Pain"}')

    def test_ordered_deduplication_and_blank_removal(self):
        cleaned, qc = clean_list([" Pain ", "Pain", "", None, "Other"])
        self.assertEqual(cleaned, ["Pain", "Other"])
        self.assertEqual(qc["blank_items_removed"], 2)
        self.assertEqual(qc["duplicate_items_removed"], 1)

    def test_followups_are_not_deduplicated(self):
        cleaned, _ = clean_list(["Initial submission", "Followup", "Followup"], deduplicate=False)
        self.assertEqual(cleaned.count("Followup"), 2)

    def test_source_case_mapping_and_unknown_queue(self):
        cleaned, unknown, _ = clean_source_types(["Health Professional", "HEALTH PROFESSIONAL", "HEALTH PR"])
        self.assertEqual(cleaned, ["HEALTH PROFESSIONAL", "HEALTH PR"])
        self.assertEqual(unknown, ["HEALTH PR"])

    def test_clean_writes_derived_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "normalized"
            source.mkdir()
            fixtures = {
                "reports": (
                    ["mdr_report_key", "type_of_report_json", "source_type_json", "product_problems_json"],
                    [["R1", '["Initial submission","Followup","Followup"]', '["Health Professional","HEALTH PR"]', '["Material Rupture","Material Rupture"]']],
                ),
                "patients": (
                    ["patient_row_id", "mdr_report_key", "outcomes_json", "patient_problems_json", "treatments_json"],
                    [["P1", "R1", '["Required Intervention"," R"]', '["Pain","Pain"]', '[""]']],
                ),
            }
            for name, (headers, rows) in fixtures.items():
                with (source / f"{name}.csv").open("w", newline="", encoding="utf-8-sig") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(headers)
                    writer.writerows(rows)
            output = root / "cleaned"
            clean(source, output)
            with (output / "report_lists_cleaned.csv").open(encoding="utf-8-sig") as handle:
                reports = list(csv.DictReader(handle))
            with (output / "patient_lists_cleaned.csv").open(encoding="utf-8-sig") as handle:
                patients = list(csv.DictReader(handle))
            with (output / "unknown_values.csv").open(encoding="utf-8-sig") as handle:
                unknown = list(csv.DictReader(handle))
            self.assertEqual(reports[0]["followup_count"], "2")
            self.assertEqual(reports[0]["product_problems_cleaned_json"], '["Material Rupture"]')
            self.assertEqual(patients[0]["treatments_cleaned_json"], "[]")
            self.assertEqual({row["raw_value"] for row in unknown}, {"HEALTH PR", "R"})


if __name__ == "__main__":
    unittest.main()

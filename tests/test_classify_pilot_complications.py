import csv
import tempfile
import unittest
from pathlib import Path

from src.classify_pilot_complications import classify, load_taxonomy


class ClassifyPilotComplicationsTests(unittest.TestCase):
    def test_duplicate_taxonomy_key_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "taxonomy.csv"
            path.write_text("source_field,raw_label,category,clinical_domain,specificity,status\nf,Label,c,d,s,ok\nf,Label,c,d,s,ok\n")
            with self.assertRaises(ValueError):
                load_taxonomy(path)

    def test_report_categories_are_deduplicated_and_unmapped_queued(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cleaned = root / "cleaned"
            cleaned.mkdir()
            (cleaned / "report_lists_cleaned.csv").write_text(
                'mdr_report_key,product_problems_cleaned_json\nR1,"[""Material Rupture""]"\n', encoding="utf-8-sig"
            )
            (cleaned / "patient_lists_cleaned.csv").write_text(
                'patient_row_id,mdr_report_key,patient_problems_cleaned_json\nP1,R1,"[""Failure of Implant"",""Unknown Label""]"\n', encoding="utf-8-sig"
            )
            taxonomy = root / "taxonomy.csv"
            taxonomy.write_text(
                "source_field,raw_label,category,clinical_domain,specificity,status\n"
                "product_problems_cleaned_json,Material Rupture,rupture,device_integrity,specific,approved\n"
                "patient_problems_cleaned_json,Failure of Implant,rupture,device_integrity,nonspecific,approved\n",
                encoding="utf-8-sig",
            )
            output = root / "output"
            classify(cleaned, taxonomy, output)
            with (output / "report_complication_categories.csv").open(encoding="utf-8-sig") as handle:
                categories = list(csv.DictReader(handle))
            with (output / "unmapped_complication_labels.csv").open(encoding="utf-8-sig") as handle:
                unmapped = list(csv.DictReader(handle))
            self.assertEqual(len(categories), 1)
            self.assertEqual(categories[0]["category"], "rupture")
            self.assertEqual(unmapped[0]["raw_label"], "Unknown Label")


if __name__ == "__main__":
    unittest.main()

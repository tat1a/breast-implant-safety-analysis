import csv,tempfile,unittest
from pathlib import Path
from src.validate_taxonomy_v2 import REQUIRED,validate

class TaxonomyV2Tests(unittest.TestCase):
    def test_repository_taxonomy_is_valid(self):
        result=validate(Path("config/complication_taxonomy_v2.csv"));self.assertTrue(result["validation_passed"]);self.assertEqual(result["rows"],32)
        self.assertEqual(result["taxonomy_version"], "v2")
    def test_batch_one_taxonomy_is_valid(self):
        result=validate(Path("config/complication_taxonomy_v3.csv"));self.assertTrue(result["validation_passed"]);self.assertEqual(result["rows"],57)
        self.assertEqual(result["taxonomy_version"], "v3")
    def test_duplicate_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"t.csv";row=dict.fromkeys(REQUIRED,"x");row.update(source_field="product_problems_cleaned_json",analysis_role="included",specificity="specific")
            with path.open("w",newline="") as h:
                w=csv.DictWriter(h,fieldnames=REQUIRED);w.writeheader();w.writerow(row);w.writerow(row)
            with self.assertRaisesRegex(ValueError,"duplicate key"):validate(path)

if __name__=="__main__":unittest.main()

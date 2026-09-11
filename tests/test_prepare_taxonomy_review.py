import csv,json,tempfile,unittest
from pathlib import Path
from src.prepare_taxonomy_review import prepare,priority

def write(path,rows):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

class TaxonomyReviewTests(unittest.TestCase):
    def test_priority_boundaries(self):
        self.assertEqual(priority(1000),"P1");self.assertEqual(priority(100),"P2");self.assertEqual(priority(99),"P3")
    def test_exact_mapping_and_queue_reconcile(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp); inv=r/"inventory.csv"; tax=r/"taxonomy.csv"
            write(inv,[{"source_field":"product_problems_json","raw_label":"Rupture","report_count":"1200","item_occurrences":"2400","pct_of_reports":"5"},{"source_field":"patient_problems_json","raw_label":"Seroma","report_count":"500","item_occurrences":"500","pct_of_reports":"2"}])
            write(tax,[{"source_field":"product_problems_cleaned_json","raw_label":"Rupture","category":"rupture","clinical_domain":"device_integrity","specificity":"specific","status":"approved"}])
            summary=json.loads(prepare(inv,tax,r/"out").read_text())
            self.assertEqual(summary["distinct_labels_exact_mapped"],1);self.assertEqual(summary["distinct_labels_unmapped"],1);self.assertTrue(summary["qc_gate_passed"])
            self.assertEqual(summary["taxonomy_version"], "taxonomy")
            self.assertEqual(summary["taxonomy_file"], "taxonomy.csv")
            self.assertNotIn("taxonomy v1", summary["scope"])
            with (r/"out"/"mapped_labels.csv").open(encoding="utf-8-sig") as h:
                mapped=list(csv.DictReader(h))
            self.assertEqual(mapped[0]["source_field"],"product_problems_json")
            self.assertEqual(mapped[0]["taxonomy_source_field"],"product_problems_cleaned_json")

if __name__=="__main__":unittest.main()

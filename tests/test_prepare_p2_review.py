import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.prepare_p2_review import prepare


class PrepareP2ReviewTests(unittest.TestCase):
    def test_filters_sorts_and_batches_p2_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / "queue.csv"
            fields = [
                "source_field", "taxonomy_source_field", "raw_label", "report_count",
                "pct_of_reports", "priority", "proposed_category",
                "proposed_clinical_domain", "proposed_specificity", "decision", "review_notes",
            ]
            rows = [
                {"source_field":"patients","taxonomy_source_field":"patient","raw_label":"B","report_count":"100","pct_of_reports":"1","priority":"P2","proposed_category":"","proposed_clinical_domain":"","proposed_specificity":"","decision":"pending_review","review_notes":""},
                {"source_field":"patients","taxonomy_source_field":"patient","raw_label":"A","report_count":"300","pct_of_reports":"2","priority":"P2","proposed_category":"","proposed_clinical_domain":"","proposed_specificity":"","decision":"pending_review","review_notes":""},
                {"source_field":"patients","taxonomy_source_field":"patient","raw_label":"C","report_count":"99","pct_of_reports":"0.5","priority":"P3","proposed_category":"","proposed_clinical_domain":"","proposed_specificity":"","decision":"pending_review","review_notes":""},
            ]
            with queue.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader(); writer.writerows(rows)

            summary = json.loads(prepare(queue, root / "out", batch_size=1).read_text())
            self.assertEqual(summary["labels"], 2)
            self.assertEqual(summary["batches"], 2)
            with (root / "out" / "p2_review_packet.csv").open(encoding="utf-8-sig") as handle:
                packet = list(csv.DictReader(handle))
            self.assertEqual([row["raw_label"] for row in packet], ["A", "B"])
            self.assertEqual([row["batch_id"] for row in packet], ["P2-01", "P2-02"])

    def test_rejects_invalid_batch_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            queue = root / "queue.csv"
            queue.write_text("priority,report_count\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare(queue, root / "out", batch_size=0)


if __name__ == "__main__":
    unittest.main()

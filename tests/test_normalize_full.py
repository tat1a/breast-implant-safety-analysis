import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.normalize_full import load_completed_run, normalize_full


def make_run(root: Path, code: str, records: list[dict]):
    run = root / f"{code}_20200101_20251231"; run.mkdir(parents=True)
    payload = json.dumps({"results": records}).encode()
    (run / "page_00001.json").write_bytes(payload)
    checkpoint = {"status": "complete", "qc_gate_passed": True,
                  "pages": [{"file": "page_00001.json", "sha256": hashlib.sha256(payload).hexdigest()}]}
    (run / "checkpoint.json").write_text(json.dumps(checkpoint))


class FullNormalizationTests(unittest.TestCase):
    def test_rejects_incomplete_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp); (run / "checkpoint.json").write_text('{"status":"paused"}')
            with self.assertRaises(ValueError): load_completed_run(run)

    def test_cross_code_overlap_is_deduplicated(self):
        record = {"mdr_report_key": "R1", "device": [{"device_report_product_code": "FTR"}], "patient": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); raw = root / "raw"
            make_run(raw, "FTR", [record]); make_run(raw, "FWM", [record])
            qc = json.loads(normalize_full(raw, root / "out").read_text())
            self.assertEqual(qc["input_records_total"], 2)
            self.assertEqual(qc["unique_report_rows"], 1)
            self.assertEqual(qc["cross_code_overlap_reports"], 1)
            self.assertTrue(qc["qc_gate_passed"])

    def test_conflicting_cross_code_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); raw = root / "raw"
            make_run(raw, "FTR", [{"mdr_report_key": "R1", "event_type": "Injury"}])
            make_run(raw, "FWM", [{"mdr_report_key": "R1", "event_type": "Death"}])
            with self.assertRaisesRegex(ValueError, "Conflicting payloads"):
                normalize_full(raw, root / "out")


if __name__ == "__main__": unittest.main()

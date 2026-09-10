import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.full_extractor import (
    add_api_key,
    initial_checkpoint,
    load_seen_keys,
    validate_checkpoint,
)


class FullExtractorTests(unittest.TestCase):
    def test_api_key_is_added_only_to_request_url(self):
        url = "https://api.fda.gov/device/event.json?search=x&limit=1000"
        request_url = add_api_key(url, "secret value")
        self.assertIn("api_key=secret+value", request_url)
        self.assertIn("search=x", request_url)

    def test_checkpoint_identity_matches_frozen_run(self):
        checkpoint = initial_checkpoint("FTR", "20200101", "20251231", 1000)
        validate_checkpoint(checkpoint, "FTR", "20200101", "20251231", 1000)

    def test_checkpoint_rejects_changed_page_size(self):
        checkpoint = initial_checkpoint("FTR", "20200101", "20251231", 1000)
        with self.assertRaises(ValueError):
            validate_checkpoint(checkpoint, "FTR", "20200101", "20251231", 500)

    def test_resume_reconstructs_keys_and_detects_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            payload1 = json.dumps({"results": [{"mdr_report_key": "1"}, {"mdr_report_key": "2"}]}).encode()
            payload2 = json.dumps({"results": [{"mdr_report_key": "2"}, {"mdr_report_key": "3"}]}).encode()
            (run_dir / "page_00001.json").write_bytes(payload1)
            (run_dir / "page_00002.json").write_bytes(payload2)
            checkpoint = {"pages": [
                {"file": "page_00001.json", "sha256": hashlib.sha256(payload1).hexdigest()},
                {"file": "page_00002.json", "sha256": hashlib.sha256(payload2).hexdigest()},
            ]}
            seen, duplicates = load_seen_keys(run_dir, checkpoint)
            self.assertEqual(seen, {"1", "2", "3"})
            self.assertEqual(duplicates, {"2"})

    def test_resume_rejects_modified_raw_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "page_00001.json").write_text('{"results": []}', encoding="utf-8")
            checkpoint = {"pages": [{"file": "page_00001.json", "sha256": "wrong"}]}
            with self.assertRaises(ValueError):
                load_seen_keys(run_dir, checkpoint)


if __name__ == "__main__":
    unittest.main()

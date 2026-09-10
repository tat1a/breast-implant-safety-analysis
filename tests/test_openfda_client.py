import unittest

from src.openfda_client import build_search, build_url


class QueryBuilderTests(unittest.TestCase):
    def test_confirmed_ftr_query(self):
        self.assertEqual(
            build_search("ftr", "20200101", "20251231"),
            "device.device_report_product_code:FTR AND date_received:[20200101 TO 20251231]",
        )

    def test_url_encodes_query(self):
        url = build_url("FWM", "20200101", "20251231", 5)
        self.assertIn("device.device_report_product_code%3AFWM", url)
        self.assertIn("limit=5", url)

    def test_rejects_out_of_scope_code(self):
        with self.assertRaises(ValueError):
            build_search("PQN", "20200101", "20251231")

    def test_rejects_reverse_dates(self):
        with self.assertRaises(ValueError):
            build_search("FTR", "20251231", "20200101")

    def test_rejects_large_limit(self):
        with self.assertRaises(ValueError):
            build_url("FTR", "20200101", "20251231", 1001)


if __name__ == "__main__":
    unittest.main()

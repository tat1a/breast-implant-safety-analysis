import unittest

from src.paginated_extractor import (
    build_first_url,
    next_url_from_link,
    redact_api_key,
)


class PaginationTests(unittest.TestCase):
    def test_first_url_has_stable_sort_and_no_skip(self):
        url = build_first_url("FTR", "20200101", "20251231", 5)
        self.assertIn("sort=date_received%3Aasc", url)
        self.assertNotIn("skip=", url)

    def test_extracts_next_link(self):
        header = '<https://api.fda.gov/device/event.json?search=x&search_after=abc>; rel="next"'
        self.assertEqual(
            next_url_from_link(header),
            "https://api.fda.gov/device/event.json?search=x&search_after=abc",
        )

    def test_missing_next_link_returns_none(self):
        self.assertIsNone(next_url_from_link(None))

    def test_redacts_api_key(self):
        safe = redact_api_key("https://api.fda.gov/device/event.json?api_key=secret&limit=5")
        self.assertNotIn("secret", safe)
        self.assertEqual(safe, "https://api.fda.gov/device/event.json?limit=5")

    def test_rejects_large_page(self):
        with self.assertRaises(ValueError):
            build_first_url("FTR", "20200101", "20251231", 1001)


if __name__ == "__main__":
    unittest.main()

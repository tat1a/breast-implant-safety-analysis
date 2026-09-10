import unittest

from src.analyze_pilot import make_svg


class AnalyzePilotTests(unittest.TestCase):
    def test_svg_contains_scope_warning(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "figure.svg"
            make_svg(path, [{"category": "rupture", "report_count": 2}])
            content = path.read_text(encoding="utf-8")
            self.assertIn("Bounded pipeline pilot", content)
            self.assertIn("not incidence", content)
            self.assertIn(">2<", content)


if __name__ == "__main__":
    unittest.main()

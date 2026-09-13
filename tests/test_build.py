import tempfile
import unittest
from pathlib import Path

from config import ISSUES
from macro.build import build_site
from macro.layout import DISCLAIMER


class BuildIssuesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data = self.root / "data"
        self.data.mkdir()
        self.out = self.root / "site"

    def tearDown(self):
        self.tmp.cleanup()

    def test_issues_page_keeps_all_chapters(self):
        build_site(self.data, self.out, ISSUES)
        html = (self.out / "issues.html").read_text(encoding="utf-8")
        for issue in ISSUES:
            self.assertIn(f'id="chapter-{issue["chapter"]}"', html)
        self.assertIn(ISSUES[0]["title"], html)
        self.assertIn(DISCLAIMER, html)
        self.assertIn('class="nav on" href="issues.html"', html)
        self.assertNotIn("취업 성공 기원", html)


if __name__ == "__main__":
    unittest.main()

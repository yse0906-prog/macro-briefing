import tempfile
import unittest
from datetime import date
from pathlib import Path

from config import ISSUES
from macro.build import build_site
from macro.components import EMPTY_MESSAGE
from macro.layout import DISCLAIMER
from tests.factories import make_briefing, make_calendar, make_event_briefing, make_indicators, make_market, write_data


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


TODAY = date(2026, 9, 13)


class SiteBuildCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name) / "data"
        self.data.mkdir()
        self.out = Path(self.tmp.name) / "site"

    def tearDown(self):
        self.tmp.cleanup()

    def build_full(self):
        write_data(self.data, briefings=[make_briefing(), make_event_briefing()], indicators=make_indicators(),
                   market=make_market(), calendar=make_calendar())
        build_site(self.data, self.out, ISSUES, today=TODAY)

    def read(self, name):
        return (self.out / name).read_text(encoding="utf-8")


class HomeArchiveTest(SiteBuildCase):
    def test_home_with_data(self):
        self.build_full()
        html = self.read("index.html")
        self.assertIn(make_event_briefing()["headline"], html)
        for text in ("D-3", "6,412.3", "코스피", "4,118.6", "3.1%", "예상 상회 +0.1%p", "증시 악재",
                     "동결 <b>78%</b>", "이슈 섹터", "시장 영향", "FOMC 금리 결정·기자회견", DISCLAIMER):
            self.assertIn(text, html)
        self.assertIn('href="briefings/2026-09-17.html"', html)

    def test_archive_lists_newest_first(self):
        self.build_full()
        html = self.read("archive.html")
        self.assertLess(html.index("briefings/2026-09-17.html"), html.index("briefings/2026-09-13.html"))
        self.assertIn("주간", html)
        self.assertIn("이벤트", html)

    def test_empty_data_still_builds(self):
        build_site(self.data, self.out, ISSUES, today=TODAY)
        self.assertIn(EMPTY_MESSAGE, self.read("index.html"))
        self.assertIn(EMPTY_MESSAGE, self.read("archive.html"))


if __name__ == "__main__":
    unittest.main()

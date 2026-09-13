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


class BriefingPageTest(SiteBuildCase):
    def test_weekly_page_sections(self):
        self.build_full()
        html = self.read("briefings/2026-09-13.html")
        for text in (make_briefing()["headline"], "9.8만", "11.0만", "13.2만", "−1.2만", "49.9", "혼조", "JPM",
                     'href="https://example.com/news"', "기본 · 매파적 동결", "CPI 상회가 은행 수익성에 주는 영향은?",
                     "1주 전: 동결 61%", "시장 예상치", 'href="../index.html"', DISCLAIMER):
            self.assertIn(text, html)
        self.assertIn('class="nav on" href="../briefings/latest.html"', html)

    def test_event_page_only_present_sections(self):
        self.build_full()
        html = self.read("briefings/2026-09-17.html")
        self.assertIn("최근 FOMC 결정", html)
        self.assertIn("3.50–3.75%", html)
        self.assertIn("매파", html)
        self.assertNotIn("이슈 섹터", html)
        self.assertNotIn("면접 인사이트", html)

    def test_latest_points_to_newest(self):
        self.build_full()
        self.assertIn(make_event_briefing()["headline"], self.read("briefings/latest.html"))

    def test_latest_empty_state(self):
        build_site(self.data, self.out, ISSUES, today=TODAY)
        self.assertIn(EMPTY_MESSAGE, self.read("briefings/latest.html"))


class FomcPageTest(SiteBuildCase):
    def test_fomc_page_with_data(self):
        self.build_full()
        html = self.read("fomc.html")
        for text in ("3.50–3.75%", "2회 연속 동결", "D-3", "동결 <b>78%</b>", "매파", "연방기금금리 목표 상단 추이",
                     "<path ", "2026.07.29", "2026.09.16", "10–2", 'class="nav on" href="fomc.html"'):
            self.assertIn(text, html)

    def test_fomc_page_empty(self):
        build_site(self.data, self.out, ISSUES, today=TODAY)
        self.assertIn("결정 이력은 브리핑이 쌓이면 표시됩니다.", self.read("fomc.html"))


class IndicatorsPageTest(SiteBuildCase):
    def test_indicators_page_with_data(self):
        self.build_full()
        html = self.read("indicators.html")
        for text in ("CPI · 근원 CPI 전년 대비 상승률", "연준 목표 2%", "3.2%", "3.0%", "8월 · 9.10", "9.8만",
                     "9.05 주", "2분기", "49.9", "4.38%", "6bp", "1,478", 'id="prices"',
                     'class="nav on" href="indicators.html"'):
            self.assertIn(text, html)

    def test_indicators_page_empty(self):
        from macro.pages.indicators import NO_DATA
        build_site(self.data, self.out, ISSUES, today=TODAY)
        self.assertIn(NO_DATA, self.read("indicators.html"))


if __name__ == "__main__":
    unittest.main()

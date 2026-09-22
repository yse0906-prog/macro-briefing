import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from config import ISSUES
from macro.build import build_site
from macro.components import EMPTY_MESSAGE
from macro.layout import DISCLAIMER
from tests.factories import (make_briefing, make_calendar, make_event_briefing, make_indicators,
                             make_sectors, write_data)


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
                   calendar=make_calendar())
        build_site(self.data, self.out, ISSUES, today=TODAY)

    def read(self, name):
        return (self.out / name).read_text(encoding="utf-8")


class HomeArchiveTest(SiteBuildCase):
    def test_home_with_data(self):
        self.build_full()
        html = self.read("index.html")
        self.assertIn(make_event_briefing()["headline"], html)
        for text in ("D-3", "6,412.3", "3.1%", "예상 상회 +0.1%p", "증시 악재",
                     "동결 <b>78%</b>", "이슈 섹터", "시장 영향", "FOMC 금리 결정·기자회견", DISCLAIMER):
            self.assertIn(text, html)
        self.assertIn('href="briefings/2026-09-17.html"', html)
        for text in ("코스피", "코스닥", "VKOSPI", 'tk-g">한국'):
            self.assertNotIn(text, html)

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


class EmploymentChainTest(SiteBuildCase):
    def test_briefing_shows_chain_in_order(self):
        self.build_full()
        html = self.read("briefings/2026-09-13.html")
        self.assertIn("고용 상세", html)
        # 툴팁 문구에도 같은 단어가 들어가므로, 고용 체인 블록 안에서만 순서를 본다
        chain = html[html.index('id="employment"'):]
        chain = chain[:chain.index("</section>")]
        order = ["비농업 고용", "실업률", "경제활동참가율", "시간당 평균임금", "업종별 고용", "이전치 수정"]
        positions = [chain.index(f">{label}<") for label in order]
        self.assertEqual(positions, sorted(positions), order)

    def test_chain_shows_participation_wage_and_industries(self):
        self.build_full()
        html = self.read("briefings/2026-09-13.html")
        for text in ("61.6%", "37.75", "레저·숙박", "교육·보건", "6.2만"):
            self.assertIn(text, html)

    def test_revisions_render_when_present(self):
        briefing = make_briefing()
        indicators = make_indicators()
        indicators["series"]["PAYEMS"]["revisions"] = [
            {"period": "2026-07-01", "from": -23000, "to": 21000}
        ]
        write_data(self.data, briefings=[briefing], indicators=indicators,
                   calendar=make_calendar())
        build_site(self.data, self.out, ISSUES, today=TODAY)
        html = self.read("briefings/2026-09-13.html")
        self.assertIn("7월", html)
        self.assertIn("−2.3만", html)
        self.assertIn("+2.1만", html)


class SectorPageTest(SiteBuildCase):
    def build_with_sectors(self):
        write_data(self.data, briefings=[make_briefing()], indicators=make_indicators(),
                   calendar=make_calendar())
        (self.data / "sectors").mkdir(parents=True, exist_ok=True)
        (self.data / "sectors" / "2026-09-16.json").write_text(
            json.dumps(make_sectors(), ensure_ascii=False), encoding="utf-8")
        build_site(self.data, self.out, ISSUES, today=date(2026, 9, 16))

    def test_sector_page_lists_seven_sectors(self):
        self.build_with_sectors()
        html = self.read("sectors.html")
        for name in ("금융", "에너지", "바이오", "반도체", "AI", "로봇", "부동산"):
            self.assertIn(name, html)
        self.assertIn('class="nav on" href="sectors.html"', html)

    def test_quick_menu_jumps_to_each_sector(self):
        self.build_with_sectors()
        html = self.read("sectors.html")
        for key in ("finance", "energy", "bio", "semiconductor", "ai", "robotics", "realestate"):
            self.assertIn(f'href="#{key}"', html)
            self.assertIn(f'id="{key}"', html)

    def test_every_sector_shows_all_six_parts(self):
        self.build_with_sectors()
        html = self.read("sectors.html")
        for label in ("촉발 요인", "숫자", "파급 경로", "한국 연결", "관전 포인트", "면접 각도"):
            self.assertEqual(html.count(f'<span class="part-k">{label}</span>'), 7, label)

    def test_semiconductor_shows_korean_chipmakers(self):
        self.build_with_sectors()
        html = self.read("sectors.html")
        self.assertIn("005930.KS", html)
        self.assertIn("000660.KS", html)

    def test_ai_sector_shows_openai_and_anthropic(self):
        self.build_with_sectors()
        html = self.read("sectors.html")
        self.assertIn("OpenAI", html)
        self.assertIn("Anthropic", html)

    def test_daily_copy_is_kept_for_archive(self):
        self.build_with_sectors()
        self.assertIn("금융", self.read("sectors/2026-09-16.html"))

    def test_page_builds_without_sector_data(self):
        build_site(self.data, self.out, ISSUES, today=TODAY)
        self.assertIn(EMPTY_MESSAGE, self.read("sectors.html"))


class InstitutionImpactTest(SiteBuildCase):
    def test_briefing_shows_three_institutions(self):
        self.build_full()
        html = self.read("briefings/2026-09-13.html")
        for label in ("증권사", "LP (보험사·연기금)", "GP (자산운용사)"):
            self.assertIn(label, html)
        self.assertNotIn("한국 은행권", html)

    def test_briefing_breaks_institutions_into_asset_topics(self):
        self.build_full()
        html = self.read("briefings/2026-09-13.html")
        self.assertIn("운용자산 관점", html)
        for label in ("듀레이션 갭", "K-ICS 비율", "환헤지 · 외화유동성", "상품운용 · 채권 평가손익",
                      "대체투자 · 딜 환경", "혼재"):
            self.assertIn(label, html)

    def test_briefing_has_fx_section(self):
        self.build_full()
        html = self.read("briefings/2026-09-13.html")
        self.assertIn('id="fx"', html)
        for text in ("외환 · 원/달러", "원화 약세", "원화 강세", "환헤지 비용", "한미 금리차"):
            self.assertIn(text, html)


class TooltipTest(SiteBuildCase):
    def test_indicator_names_carry_help_text(self):
        self.build_full()
        html = self.read("indicators.html")
        self.assertIn("월 10만 명 안팎", html)
        self.assertIn("62~63%", html)
        self.assertIn('class="tip"', html)

    def test_home_cards_carry_help_text(self):
        self.build_full()
        self.assertIn("연준 목표는 2%입니다", self.read("index.html"))


if __name__ == "__main__":
    unittest.main()

"""토요일 주간 갱신으로 바뀐 뒤의 규칙.

주간 브리핑은 더 이상 자체 섹터 칸을 두지 않는다. 섹터 분석은 같은 날짜 섹터 파일에 쓰고,
브리핑은 그 페이지로 연결만 한다. 예전 브리핑(섹터 칸이 있는 것)도 그대로 통과해야 한다.
"""
import json
import unittest

from config import ISSUES
from macro.build import build_site
from macro.layout import CADENCE, DESCRIPTION
from macro.schema import validate_briefing
from tests.factories import make_briefing, make_calendar, make_indicators, make_sectors, write_data
from tests.test_build import TODAY, SiteBuildCase


def weekly_without_sectors():
    b = make_briefing()
    del b["sectors"]
    return b


class WeeklySchemaTest(unittest.TestCase):
    def test_weekly_may_omit_sectors(self):
        self.assertEqual(validate_briefing(weekly_without_sectors(), "2026-09-13.json"), [])

    def test_old_briefing_with_sectors_still_checked(self):
        b = make_briefing()
        b["sectors"] = b["sectors"][:2]
        self.assertTrue(any("sectors" in e for e in validate_briefing(b, "2026-09-13.json")))


class SectorLinkTest(SiteBuildCase):
    def write_sector_file(self, day: str):
        (self.data / "sectors").mkdir(parents=True, exist_ok=True)
        (self.data / "sectors" / f"{day}.json").write_text(
            json.dumps(make_sectors(date=day), ensure_ascii=False), encoding="utf-8")

    def test_briefing_links_to_same_day_sector_page(self):
        write_data(self.data, briefings=[weekly_without_sectors()], indicators=make_indicators(),
                   calendar=make_calendar())
        self.write_sector_file("2026-09-13")
        build_site(self.data, self.out, ISSUES, today=TODAY)
        html = self.read("briefings/2026-09-13.html")
        self.assertIn('href="../sectors/2026-09-13.html"', html)
        self.assertIn("반도체", html)
        # 섹터 타일은 브리핑 페이지가 아니라 섹터 페이지의 해당 섹터로 가야 한다
        self.assertIn('href="../sectors/2026-09-13.html#semiconductor"', html)

    def test_no_sector_section_when_no_file(self):
        write_data(self.data, briefings=[weekly_without_sectors()], indicators=make_indicators(),
                   calendar=make_calendar())
        build_site(self.data, self.out, ISSUES, today=TODAY)
        self.assertNotIn('id="sectors"', self.read("briefings/2026-09-13.html"))


class CadenceWordingTest(unittest.TestCase):
    def test_site_says_weekly_not_daily(self):
        for text in (CADENCE, DESCRIPTION):
            self.assertNotIn("평일", text)
            self.assertIn("토요일", text)

    def test_footer_shows_cadence(self):
        from macro.layout import page
        self.assertIn(CADENCE, page(title="홈", active="home", body=""))


if __name__ == "__main__":
    unittest.main()

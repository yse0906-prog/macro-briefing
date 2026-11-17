"""텔레그램 알림 메시지.

발표가 있는 날 휴대폰으로 받아 보는 요약이다. 링크를 열지 않아도 숫자와 방향이 보여야 하고,
본문 강조 표시(**, [[+ ]])는 기호가 아니라 글자만 남아야 한다. 텔레그램 상한은 4096자다.
"""
import unittest

from macro import data as d
from macro.notify import LIMIT, telegram_message
from tests.factories import (make_briefing, make_calendar, make_event_briefing, make_indicators,
                             make_sectors)


def site_with(briefing, sectors=None):
    return d.SiteData(indicators=make_indicators(), calendar=make_calendar(),
                      briefings=[briefing], sectors=[sectors] if sectors else [])


class MessageTest(unittest.TestCase):
    def test_headline_summary_and_link(self):
        b = make_briefing()
        text = telegram_message(site_with(b))
        self.assertIn(b["headline"], text)
        for line in b["summary"]:
            self.assertIn(line, text)
        self.assertIn("https://yse0906-prog.github.io/macro-briefing/briefings/2026-09-13.html", text)

    def test_releases_show_actual_against_consensus(self):
        text = telegram_message(site_with(make_briefing()))
        self.assertIn("CPI 전년비 (8월)", text)
        self.assertIn("3.1%", text)      # 실제치는 FRED에서 온다
        self.assertIn("3.0%", text)      # 예상치

    def test_consensus_is_hidden_when_unknown(self):
        b = make_briefing()
        for r in b["releases"]:
            r.pop("consensus", None)
            r.pop("consensus_source", None)
        text = telegram_message(site_with(b))
        self.assertNotIn("예상 —", text)

    def test_market_impact_is_trimmed_to_one_sentence(self):
        b = make_briefing()
        b["market_impact"][0]["text"] = "첫 문장이다. " + "뒤에 붙는 긴 설명. " * 20
        text = telegram_message(site_with(b))
        self.assertIn("첫 문장이다.", text)
        self.assertNotIn("뒤에 붙는 긴 설명. 뒤에 붙는", text)

    def test_each_release_carries_its_interpretation(self):
        b = make_briefing()
        b["releases"][0]["interpretation"] = "예상을 웃돌아 12월 인상 확률을 끌어올린 요인이다."
        text = telegram_message(site_with(b))
        self.assertIn("예상을 웃돌아 12월 인상 확률을 끌어올린 요인이다.", text)

    def test_fomc_tone_and_press_gist(self):
        text = telegram_message(site_with(make_briefing()))
        self.assertIn("성명 톤", text)
        self.assertIn("기자회견", text)

    def test_most_likely_scenario_is_shown(self):
        b = make_briefing()
        b["scenarios"] = [
            {"name": "기본 · 매파적 동결", "probability": 60, "text": "첫 문장. 뒤 설명."},
            {"name": "비둘기 선회", "probability": 40, "text": "다른 설명."},
        ]
        text = telegram_message(site_with(b))
        self.assertIn("기본 · 매파적 동결", text)
        self.assertIn("60%", text)
        self.assertNotIn("비둘기 선회", text)

    def test_market_impact_directions(self):
        text = telegram_message(site_with(make_briefing()))
        self.assertIn("미국 주식", text)
        self.assertIn("↓", text)
        self.assertIn("↑", text)

    def test_sector_line_when_same_day_file_exists(self):
        b = make_briefing()
        text = telegram_message(site_with(b, make_sectors(date=b["date"])))
        self.assertIn("반도체", text)
        self.assertIn("sectors/2026-09-13.html", text)

    def test_event_briefing_is_labelled_differently(self):
        weekly = telegram_message(site_with(make_briefing()))
        event = telegram_message(site_with(make_event_briefing()))
        self.assertIn("주간 브리핑", weekly)
        self.assertIn("이벤트 브리핑", event)

    def test_markup_is_stripped_not_shown(self):
        b = make_briefing(summary=["**연준 인상**으로 [[-금리 급등]].", "둘째.", "셋째."])
        text = telegram_message(site_with(b))
        self.assertIn("연준 인상으로 금리 급등.", text)
        for mark in ("**", "[[", "]]"):
            self.assertNotIn(mark, text)

    def test_angle_brackets_are_escaped_for_telegram_html(self):
        b = make_briefing(headline="S&P 500 <주의> 구간")
        text = telegram_message(site_with(b))
        self.assertIn("S&amp;P 500 &lt;주의&gt;", text)

    def test_stays_within_telegram_limit(self):
        b = make_briefing(summary=["가" * 1500, "나" * 1500, "다" * 1500])
        text = telegram_message(site_with(b))
        self.assertLessEqual(len(text), LIMIT)

    def test_no_briefing_means_no_message(self):
        self.assertEqual(telegram_message(d.SiteData()), "")


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from macro.schema import validate_briefing, validate_calendar, validate_data_dir, validate_market
from tests.factories import make_briefing, make_calendar, make_event_briefing, make_market, write_data


def has(errors, text):
    return any(text in e for e in errors)


class BriefingSchemaTest(unittest.TestCase):
    def test_valid_weekly_and_event(self):
        self.assertEqual(validate_briefing(make_briefing(), "2026-09-13.json"), [])
        self.assertEqual(validate_briefing(make_event_briefing(), "2026-09-17.json"), [])

    def test_missing_required(self):
        b = make_briefing()
        del b["headline"]
        self.assertTrue(has(validate_briefing(b, "2026-09-13.json"), "headline"))

    def test_summary_must_have_three(self):
        errors = validate_briefing(make_briefing(summary=["하나", "둘"]), "2026-09-13.json")
        self.assertTrue(has(errors, "summary"))

    def test_filename_must_match_date(self):
        self.assertTrue(has(validate_briefing(make_briefing(), "2026-09-14.json"), "파일 이름"))

    def test_fred_release_must_not_carry_actual(self):
        b = make_briefing()
        b["releases"][2]["actual"] = 3.1
        self.assertTrue(has(validate_briefing(b, "2026-09-13.json"), "FRED"))

    def test_web_release_needs_actual(self):
        b = make_briefing()
        del b["releases"][6]["actual"]
        self.assertTrue(has(validate_briefing(b, "2026-09-13.json"), "actual"))

    def test_source_reference_must_exist(self):
        b = make_briefing()
        b["releases"][0]["consensus_source"] = 99
        self.assertTrue(has(validate_briefing(b, "2026-09-13.json"), "출처 번호"))

    def test_weekly_sectors_rules(self):
        b = make_briefing()
        b["sectors"] = [s for s in b["sectors"] if s["name"] != "금융"]
        self.assertTrue(has(validate_briefing(b, "2026-09-13.json"), "금융"))
        b = make_briefing()
        b["sectors"] = b["sectors"][:2]
        self.assertTrue(has(validate_briefing(b, "2026-09-13.json"), "3~5개"))

    def test_scenarios_sum_to_100(self):
        b = make_briefing()
        b["scenarios"][0]["probability"] = 50
        self.assertTrue(has(validate_briefing(b, "2026-09-13.json"), "시나리오"))

    def test_https_only(self):
        b = make_briefing()
        b["sources"][0]["url"] = "http://example.com"
        self.assertTrue(has(validate_briefing(b, "2026-09-13.json"), "https"))

    def test_event_needs_release_or_meeting(self):
        b = make_event_briefing()
        del b["fomc"]
        self.assertTrue(has(validate_briefing(b, "2026-09-17.json"), "event"))


class MarketCalendarSchemaTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_market(make_market()), [])
        self.assertEqual(validate_calendar(make_calendar()), [])

    def test_market_unknown_id(self):
        m = make_market()
        m["items"][0]["id"] = "sp500"
        self.assertTrue(has(validate_market(m), "id"))

    def test_calendar_importance_range(self):
        c = make_calendar()
        c["events"][0]["importance"] = 4
        self.assertTrue(has(validate_calendar(c), "importance"))


class DataDirTest(unittest.TestCase):
    def test_empty_and_broken_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            self.assertEqual(validate_data_dir(data), [])
            write_data(data, briefings=[make_briefing()], market=make_market(), calendar=make_calendar())
            self.assertEqual(validate_data_dir(data), [])
            (data / "briefings" / "2026-09-20.json").write_text("{broken", encoding="utf-8")
            self.assertTrue(has(validate_data_dir(data), "JSON"))


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from datetime import date
from pathlib import Path

from macro import data as d
from tests.factories import make_briefing, make_calendar, make_event_briefing, make_indicators, write_data


class LoadTest(unittest.TestCase):
    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = d.load_site_data(Path(tmp))
            self.assertEqual(site.briefings, [])
            self.assertIsNone(site.latest)
            self.assertEqual(site.indicators["series"], {})

    def test_briefings_newest_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_data(Path(tmp), briefings=[make_briefing(), make_event_briefing()], indicators=make_indicators())
            site = d.load_site_data(Path(tmp))
            self.assertEqual([b["date"] for b in site.briefings], ["2026-09-17", "2026-09-13"])


class ValuesTest(unittest.TestCase):
    def setUp(self):
        self.ind = make_indicators()
        self.site = d.SiteData(self.ind, make_calendar(), [make_event_briefing(), make_briefing()])

    def release(self, series):
        return next(r for r in make_briefing()["releases"] if r["series"] == series)

    def test_release_values_from_fred(self):
        self.assertEqual(d.release_values(self.ind, self.release("CPIAUCSL")), {"actual": 3.1, "previous": 2.9})
        self.assertEqual(d.release_values(self.ind, self.release("ICSA")), {"actual": 231000, "previous": 240000})

    def test_release_values_from_web_and_missing_period(self):
        self.assertEqual(d.release_values(self.ind, self.release("ISM_MFG")), {"actual": 49.9, "previous": 49.2})
        missing = {**self.release("CPIAUCSL"), "period": "2030-01-01"}
        self.assertEqual(d.release_values(self.ind, missing), {"actual": None, "previous": None})

    def test_us_ticker_weekly_change(self):
        rows = {r["id"]: r for r in d.us_ticker(self.ind)}
        self.assertEqual((rows["sp500"]["value"], rows["sp500"]["change"], rows["sp500"]["unit"]), (6412.3, -0.8, "%"))
        self.assertEqual((rows["us10y"]["change"], rows["us10y"]["unit"]), (6, "bp"))
        self.assertEqual((rows["vix"]["change"], rows["vix"]["unit"]), (1.2, "pt"))
        self.assertIsNone(d.weekly_change([("2026-09-11", 1.0)], "pct"))

    def test_sampling(self):
        months = d.monthly_last(d.obs(self.ind, "DFEDTARU"), 3)
        self.assertEqual([k for k, _ in months], ["2026-07", "2026-08", "2026-09"])
        self.assertEqual(months[-1][1], 3.75)
        weeks = d.weekly_last(d.obs(self.ind, "SP500"), 12)
        self.assertEqual(len(weeks), 12)
        self.assertEqual(weeks[-1], ("2026-09-11", 6412.3))

    def test_fomc_helpers(self):
        self.assertEqual(d.current_range(self.ind), (3.5, 3.75))
        self.assertEqual([m["date"] for m in d.fomc_history(self.site)], ["2026-09-16", "2026-07-29"])
        self.assertEqual(d.next_meeting(self.site, date(2026, 9, 13))["date"], "2026-09-16")
        self.assertIsNone(d.next_meeting(self.site, date(2026, 9, 20)))
        briefing, release = d.latest_release(self.site, "ISM_MFG")
        self.assertEqual((briefing["date"], release["actual"]), ("2026-09-13", 49.9))
        self.assertEqual(d.latest_release(self.site, "NOPE"), (None, None))

    def test_calendar_and_dday(self):
        self.assertEqual(len(d.upcoming_events(make_calendar(), date(2026, 9, 13))), 3)
        self.assertEqual(d.upcoming_events(None, date(2026, 9, 13)), [])
        self.assertEqual(d.dday("2026-09-16", date(2026, 9, 13)), "D-3")
        self.assertEqual(d.dday("2026-09-16", date(2026, 9, 16)), "D-DAY")
        self.assertEqual(d.dday("2026-09-16", date(2026, 9, 17)), "종료")


if __name__ == "__main__":
    unittest.main()

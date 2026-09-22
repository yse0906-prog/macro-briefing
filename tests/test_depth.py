"""업권별 운용자산 시사점과 외환 섹션 검사.

2026-09-19 이후 브리핑부터는 업권마다 고정 항목 4개를 모두 채워야 한다.
증권사는 상품운용·브로커리지·IB·WM, LP는 듀레이션 갭·K-ICS·자산배분·환헤지,
GP는 자금 유출입·보수 수익·상품 기회·대체투자를 본다. 주간 브리핑에는 외환 섹션도 붙는다.
"""
import unittest

from macro.schema import validate_briefing
from tests.factories import make_briefing, make_event_briefing


def has(errors, text):
    return any(text in e for e in errors)


def deep(**overrides):
    return make_briefing(date="2026-09-19", **overrides)


def point(b, institution, topic):
    inst = next(i for i in b["institution_impact"] if i["institution"] == institution)
    return inst, next(p for p in inst["points"] if p["topic"] == topic)


class InstitutionDepthTest(unittest.TestCase):
    def test_full_briefing_passes(self):
        self.assertEqual(validate_briefing(deep(), "2026-09-19.json"), [])

    def test_missing_topic_fails_after_cutoff(self):
        for institution, topic in (("lp", "kics"), ("lp", "duration_gap"), ("securities", "trading"), ("gp", "alternatives")):
            b = deep()
            inst, p = point(b, institution, topic)
            inst["points"].remove(p)
            self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), topic), topic)

    def test_older_briefing_may_have_summary_only(self):
        b = make_briefing()
        for inst in b["institution_impact"]:
            del inst["points"]
        self.assertEqual(validate_briefing(b, "2026-09-13.json"), [])

    def test_event_briefing_after_cutoff_needs_points_too(self):
        b = make_event_briefing(date="2026-09-19")
        self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), "duration_gap"))

    def test_unknown_topic_fails(self):
        b = deep()
        _, p = point(b, "gp", "fees")
        p["topic"] = "kics"
        self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), "kics"))

    def test_direction_must_be_known(self):
        b = deep()
        _, p = point(b, "lp", "kics")
        p["direction"] = "좋음"
        self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), "direction"))

    def test_point_source_must_exist(self):
        b = deep()
        _, p = point(b, "lp", "kics")
        p["source"] = 99
        self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), "출처 번호"))


class FxSectionTest(unittest.TestCase):
    def test_weekly_after_cutoff_needs_fx(self):
        b = deep()
        del b["fx"]
        self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), "fx"))

    def test_older_weekly_may_skip_fx(self):
        b = make_briefing()
        del b["fx"]
        self.assertEqual(validate_briefing(b, "2026-09-13.json"), [])

    def test_needs_three_drivers(self):
        b = deep()
        b["fx"]["drivers"] = b["fx"]["drivers"][:2]
        self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), "요인"))

    def test_driver_effect_must_be_known(self):
        b = deep()
        b["fx"]["drivers"][0]["effect"] = "up"
        self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), "effect"))

    def test_numbers_need_sources(self):
        b = deep()
        b["fx"]["numbers"][0]["source"] = 99
        self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), "출처 번호"))

    def test_hedge_and_flows_required(self):
        for field in ("hedge", "flows", "watch_next"):
            b = deep()
            del b["fx"][field]
            self.assertTrue(has(validate_briefing(b, "2026-09-19.json"), field), field)


if __name__ == "__main__":
    unittest.main()

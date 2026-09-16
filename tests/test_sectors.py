"""섹터 이슈 파일 형식 검사.

섹터 이슈는 평일마다 새 파일로 쌓인다. 7개 섹터가 모두 있어야 하고,
AI 섹터에는 상장사가 아닌 OpenAI·Anthropic 동향 칸이 따로 붙는다.
"""
import unittest

from macro.schema import SECTOR_KEYS, validate_sectors
from tests.factories import make_sectors


def has(errors, text):
    return any(text in e for e in errors)


class SectorSchemaTest(unittest.TestCase):
    def test_valid_file_passes(self):
        self.assertEqual(validate_sectors(make_sectors(), "2026-09-16.json"), [])

    def test_seven_fixed_sectors_in_order(self):
        self.assertEqual(
            SECTOR_KEYS,
            ["finance", "energy", "bio", "semiconductor", "ai", "robotics", "realestate"],
        )

    def test_missing_sector_fails(self):
        data = make_sectors()
        data["sectors"] = [s for s in data["sectors"] if s["key"] != "robotics"]
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "robotics"))

    def test_unknown_status_fails(self):
        data = make_sectors()
        data["sectors"][0]["status"] = "좋음"
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "status"))

    def test_ai_sector_needs_openai_and_anthropic(self):
        data = make_sectors()
        ai = next(s for s in data["sectors"] if s["key"] == "ai")
        ai["watch"] = [w for w in ai["watch"] if w["company"] != "Anthropic"]
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "Anthropic"))

    def test_point_source_must_exist(self):
        data = make_sectors()
        data["sectors"][0]["points"][0]["source"] = 99
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "출처 번호"))

    def test_sources_must_be_https(self):
        data = make_sectors()
        data["sources"][0]["url"] = "http://example.com"
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "https"))

    def test_filename_must_match_date(self):
        self.assertTrue(has(validate_sectors(make_sectors(), "2026-09-17.json"), "파일 이름"))

    def test_unchanged_sector_may_have_no_points(self):
        data = make_sectors()
        quiet = next(s for s in data["sectors"] if s["key"] == "realestate")
        quiet["changed"] = False
        quiet["points"] = []
        self.assertEqual(validate_sectors(data, "2026-09-16.json"), [])

    def test_changed_sector_needs_at_least_one_point(self):
        data = make_sectors()
        loud = next(s for s in data["sectors"] if s["key"] == "energy")
        loud["changed"] = True
        loud["points"] = []
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "근거"))


if __name__ == "__main__":
    unittest.main()

"""섹터 이슈 파일 형식 검사.

섹터 이슈는 평일마다 새 파일로 쌓인다. 7개 섹터가 모두 있어야 하고, 각 섹터는
촉발 요인·숫자·파급 경로·한국 연결·관전 포인트·면접 각도를 같은 깊이로 채운다.
AI 섹터에는 상장사가 아닌 OpenAI·Anthropic 동향 칸이 따로 붙는다.
"""
import unittest

from macro.schema import SECTOR_KEYS, validate_sectors
from tests.factories import make_sectors


def has(errors, text):
    return any(text in e for e in errors)


def sector(data, key):
    return next(s for s in data["sectors"] if s["key"] == key)


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

    def test_every_sector_needs_all_six_parts(self):
        for field in ("trigger", "chain", "korea", "interview"):
            data = make_sectors()
            del sector(data, "energy")[field]
            self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), field), field)

    def test_numbers_need_at_least_two_entries(self):
        data = make_sectors()
        sector(data, "bio")["numbers"] = [{"text": "하나뿐", "source": 1}]
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "숫자"))

    def test_watch_next_needs_at_least_one(self):
        data = make_sectors()
        sector(data, "finance")["watch_next"] = []
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "관전"))

    def test_number_source_must_exist(self):
        data = make_sectors()
        sector(data, "finance")["numbers"][0]["source"] = 99
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "출처 번호"))

    def test_ai_sector_needs_openai_and_anthropic(self):
        data = make_sectors()
        ai = sector(data, "ai")
        ai["watch"] = [w for w in ai["watch"] if w["company"] != "Anthropic"]
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "Anthropic"))

    def test_sources_must_be_https(self):
        data = make_sectors()
        data["sources"][0]["url"] = "http://example.com"
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "https"))

    def test_filename_must_match_date(self):
        self.assertTrue(has(validate_sectors(make_sectors(), "2026-09-17.json"), "파일 이름"))

    def test_days_running_is_optional_but_must_be_positive(self):
        data = make_sectors()
        sector(data, "energy")["days"] = 0
        self.assertTrue(has(validate_sectors(data, "2026-09-16.json"), "days"))


if __name__ == "__main__":
    unittest.main()

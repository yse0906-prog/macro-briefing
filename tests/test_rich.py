"""본문 강조 표시.

**조건** 은 굵게, [[+결과]] 는 유리한 쪽(초록), [[-결과]] 는 불리한 쪽(빨강)으로 칠한다.
짝이 안 맞는 표시는 검사에서 걸러 화면에 기호가 새지 않게 한다.
"""
import unittest

from macro.fmt import markup_errors, plain, rich
from macro.schema import validate_briefing, validate_sectors
from tests.factories import make_briefing, make_sectors


class RichTest(unittest.TestCase):
    def test_bold_and_colors(self):
        html = rich("**갭이 음이면** [[+순자산 증가]], **양이면** [[-순자산 감소]]")
        self.assertIn("<strong>갭이 음이면</strong>", html)
        self.assertIn('<mark class="hl-pos">순자산 증가</mark>', html)
        self.assertIn('<mark class="hl-neg">순자산 감소</mark>', html)

    def test_still_escapes_html(self):
        html = rich("<script>x</script> **굵게**")
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_plain_text_passes_through(self):
        self.assertEqual(rich("표시 없는 문장 -0.2% [참고]"), "표시 없는 문장 -0.2% [참고]")

    def test_plain_strips_marks(self):
        self.assertEqual(plain("**조건** [[+좋음]] [[-나쁨]]"), "조건 좋음 나쁨")

    def test_markup_errors(self):
        self.assertEqual(markup_errors("**굵게** [[+좋음]]"), [])
        self.assertTrue(markup_errors("**닫히지 않음"))
        self.assertTrue(markup_errors("[[+닫히지 않음"))
        self.assertTrue(markup_errors("[[좋음]]"))


class RichSchemaTest(unittest.TestCase):
    def test_broken_markup_fails_briefing(self):
        b = make_briefing()
        b["institution_impact"][0]["points"][0]["text"] = "**닫히지 않은 강조"
        self.assertTrue(any("강조 표시" in e for e in validate_briefing(b, "2026-09-13.json")))

    def test_broken_markup_fails_sectors(self):
        data = make_sectors()
        data["sectors"][0]["korea"] = "[[-닫히지 않음"
        self.assertTrue(any("강조 표시" in e for e in validate_sectors(data, "2026-09-16.json")))

    def test_marks_not_allowed_in_headline(self):
        b = make_briefing(headline="**굵은** 제목")
        self.assertTrue(any("headline" in e for e in validate_briefing(b, "2026-09-13.json")))


if __name__ == "__main__":
    unittest.main()

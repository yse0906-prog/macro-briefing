import unittest

from macro.fmt import MINUS, esc, kst_time, man, md, num, signed, ymd_ko


class FmtTest(unittest.TestCase):
    def test_esc_escapes_html_and_none(self):
        self.assertEqual(esc("<b>&"), "&lt;b&gt;&amp;")
        self.assertEqual(esc(None), "")

    def test_num_thousands_and_negative(self):
        self.assertEqual(num(6412.34), "6,412.3")
        self.assertEqual(num(-0.84), MINUS + "0.8")
        self.assertEqual(num(3.75, 2), "3.75")
        self.assertEqual(num(None), "—")

    def test_signed(self):
        self.assertEqual(signed(0.1, suffix="%p"), "+0.1%p")
        self.assertEqual(signed(-12, 0, "bp"), MINUS + "12bp")
        self.assertEqual(signed(0), "0.0")
        self.assertEqual(signed(None), "—")

    def test_man(self):
        self.assertEqual(man(98000), "9.8만")
        self.assertEqual(man(231000), "23.1만")
        self.assertEqual(man(None), "—")

    def test_dates(self):
        self.assertEqual(md("2026-09-04"), "9.04")
        self.assertEqual(ymd_ko("2026-09-13"), "2026년 9월 13일(일)")
        self.assertEqual(kst_time("2026-09-17T03:00:00+09:00"), "9.17(목) 03:00")


if __name__ == "__main__":
    unittest.main()

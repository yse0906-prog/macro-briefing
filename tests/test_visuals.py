"""글 사이에 넣는 시각자료 검사.

숫자 카드는 문장에서 핵심 수치 하나를 골라 크게 보여준다. 날짜(15일)나 연한(10년물)은
고르지 않고, 단위가 붙은 값을 고른다. 화살표(→)가 있으면 바뀐 뒤의 값을 고른다.
"""
import unittest

from macro import visuals as v


class BigFigureTest(unittest.TestCase):
    def test_skips_dates_and_tenors(self):
        self.assertEqual(v.big_figure("15일 미국 10년물 금리 5.041% — 2007년 이후 최고"), "5.041%")

    def test_keeps_scale_and_unit_together(self):
        self.assertEqual(v.big_figure("호르무즈 통항 차질로 하루 약 2,000만 배럴 규모"), "2,000만 배럴")
        self.assertEqual(v.big_figure("2026년 설비투자 합계 7,250억 달러, 전년 대비 77% 증가"), "7,250억 달러")
        self.assertEqual(v.big_figure("싱가포르 항공유가 배럴당 149.29달러"), "149.29달러")

    def test_keeps_ranges(self):
        self.assertEqual(v.big_figure("유류할증료 48,000~354,000원, 최대 94,800원 인상"), "48,000~354,000원")

    def test_prefers_value_after_arrow(self):
        self.assertEqual(v.big_figure("원/달러 9월 11일 1,345.9원 → 9월 18일 1,383.3원, 주간 +2.8%"), "1,383.3원")

    def test_counts_and_signed_values(self):
        self.assertEqual(v.big_figure("8월 FDA 승인 2건 — 기면증 치료제"), "2건")
        self.assertEqual(v.big_figure("15일 퀄컴 +4%대 상승"), "+4%")
        self.assertEqual(v.big_figure("2분기 HBM 점유율 SK하이닉스 50%로 1위"), "50%")

    def test_months_are_durations_not_counts(self):
        self.assertEqual(v.big_figure("iShares 반도체 ETF(SOXX), 최근 3개월 -17%"), "-17%")
        self.assertNotEqual(v.big_figure("반응지속기간 중앙값 49.7개월"), "49.7개")

    def test_compound_korean_amounts(self):
        self.assertEqual(v.big_figure("삼성전자 9/21 장중 27만5000원(+5.36%)까지"), "27만5000원")
        self.assertEqual(v.big_figure("주식위험액도 35조 2,000억 원 늘어"), "35조 2,000억 원")

    def test_falls_back_to_date_then_nothing(self):
        self.assertEqual(v.big_figure("오픈AI, 2026년 5월 사건을 보고하지 않았다"), "2026년 5월")
        self.assertEqual(v.big_figure("아피테그루맙 FDA 결정 예정일 9월 30일"), "9월 30일")
        self.assertEqual(v.big_figure("옵티머스 상용화 시점을 2027년 하반기로 전망"), "2027년 하반기")
        self.assertIsNone(v.big_figure("리츠는 올해 상반기 시장 수익률을 상회"))


class FlowTest(unittest.TestCase):
    def test_splits_branches_and_steps(self):
        html = v.flow("유가↑ → 정제마진↑ → 정유주↑ / 항공 원가↑ → 물가↑")
        self.assertEqual(html.count('class="flow-row"'), 2)
        self.assertEqual(html.count('class="flow-step'), 5)
        self.assertEqual(html.count('class="flow-arrow"'), 3)

    def test_marks_direction(self):
        html = v.flow("금리↑ → 가치↓")
        self.assertIn("flow-up", html)
        self.assertIn("flow-down", html)

    def test_plain_text_without_arrows_stays_text(self):
        self.assertNotIn("flow-row", v.flow("화살표 없는 문장"))


class DirectionGridTest(unittest.TestCase):
    def test_every_cell_has_a_text_label(self):
        items = [{"institution": "lp", "text": "요약",
                  "points": [{"topic": "kics", "direction": "positive", "text": "..."},
                             {"topic": "duration_gap", "direction": "mixed", "text": "..."}]}]
        html = v.direction_grid(items)
        self.assertIn("K-ICS", html)
        self.assertIn("우호", html)
        self.assertIn("혼재", html)


class FxTugTest(unittest.TestCase):
    def test_sides(self):
        drivers = [{"factor": "금리차", "effect": "krw_weak", "text": "."},
                   {"factor": "수출", "effect": "krw_strong", "text": "."},
                   {"factor": "안전판", "effect": "neutral", "text": "."}]
        html = v.fx_tug(drivers)
        weak, strong = html.index("원화 약세"), html.index("원화 강세")
        self.assertLess(html.index("금리차"), strong)
        self.assertGreater(html.index("수출"), strong)
        self.assertIn("안전판", html)
        self.assertLess(weak, strong)


if __name__ == "__main__":
    unittest.main()

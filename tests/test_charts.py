import re
import unittest

from macro.charts import PAD_BOTTOM, PAD_LEFT, PAD_TOP, Series, line_chart, nice_range, sparkline


def hit_points(svg):
    return [(float(x), float(y)) for x, y in re.findall(r'class="hit" cx="([\d.]+)" cy="([\d.]+)"', svg)]


class ChartTest(unittest.TestCase):
    def setUp(self):
        self.cpi = Series("CPI", "#2B5C9E", [(f"2026.{m:02d}", v) for m, v in zip(range(1, 9), [2.5, 2.6, 2.8, 3.0, 2.9, 2.9, 2.9, 3.1])], "3.1%")
        self.core = Series("근원 CPI", "#D08A2E", [(f"2026.{m:02d}", v) for m, v in zip(range(1, 9), [2.5, 2.6, 2.8, 2.9, 3.0, 3.0, 3.1, 3.2])], "3.2%", dy=-4)

    def test_nice_range(self):
        self.assertEqual(nice_range([2.3, 3.3], 0.4), (2.0, 3.6, [2.0, 2.4, 2.8, 3.2, 3.6]))
        self.assertEqual(nice_range([3.75, 3.75], 0.5), (3.5, 4.0, [3.5, 4.0]))

    def test_line_chart_structure(self):
        svg = line_chart([self.core, self.cpi], y_min=2.0, y_max=3.6, y_ticks=[2.0, 2.8, 3.6],
                         x_labels=[(0, "2026.01"), (7, "2026.08")], ref=(2.0, "연준 목표 2%"), label="CPI 추이")
        self.assertTrue(svg.startswith('<svg viewBox="0 0 1120 300"'))
        self.assertEqual(svg.count("<path "), 2)
        self.assertEqual(len(hit_points(svg)), 16)
        self.assertIn("<title>2026.08 · CPI 3.1%</title>", svg)
        self.assertIn(">3.2%</tspan>", svg)
        self.assertIn("연준 목표 2%", svg)
        self.assertIn('aria-label="CPI 추이"', svg)

    def test_points_inside_plot_area(self):
        svg = line_chart([self.cpi], y_min=2.0, y_max=3.6, y_ticks=[2.0, 3.6], x_labels=[])
        for x, y in hit_points(svg):
            self.assertTrue(PAD_LEFT <= x <= 1120 - 140, x)
            self.assertTrue(PAD_TOP <= y <= 300 - PAD_BOTTOM, y)

    def test_step_chart(self):
        rate = Series("상단", "#2B5C9E", [("2025.11", 4.0), ("2025.12", 3.75), ("2026.01", 3.75)], "3.75%")
        svg = line_chart([rate], y_min=3.0, y_max=6.0, y_ticks=[3.0, 6.0], x_labels=[], step=True,
                         value_fmt=lambda v: f"{v:.2f}%")
        path = re.search(r'<path d="([^"]+)"', svg).group(1)
        self.assertIn(" H", path)
        self.assertIn(" V", path)
        self.assertIn("2025.12 · 상단 3.75%", svg)

    def test_sparkline(self):
        svg = sparkline([1.0, 2.0, 1.5], label="최근 12개월")
        self.assertIn("<path ", svg)
        self.assertIn("<title>최근 12개월</title>", svg)
        self.assertIn("<path ", sparkline([2.0, 2.0, 2.0]))
        self.assertEqual(sparkline([1.0]), "")


if __name__ == "__main__":
    unittest.main()

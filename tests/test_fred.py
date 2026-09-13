import unittest

from macro.fred import SERIES, build_indicators, diff_thousands, parse_csv, pct_change, yoy


def monthly_csv(values, header="observation_date,X"):
    lines = [header]
    for i, v in enumerate(values):
        year, month = 2024 + i // 12, i % 12 + 1
        lines.append(f"{year}-{month:02d}-01,{v}")
    return "\n".join(lines) + "\n"


class ParseAndTransformTest(unittest.TestCase):
    def test_parse_skips_header_and_missing(self):
        text = "DATE,DGS10\n2026-09-10,4.30\n2026-09-11,.\n2026-09-12,4.38\n"
        self.assertEqual(parse_csv(text), [("2026-09-10", 4.30), ("2026-09-12", 4.38)])

    def test_yoy(self):
        obs = parse_csv(monthly_csv([100 + i for i in range(13)]))
        result = yoy(obs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("2025-01-01", 12.0))

    def test_pct_change(self):
        obs = [("2026-07-01", 200.0), ("2026-08-01", 200.6)]
        self.assertEqual(pct_change(obs), [("2026-08-01", 0.3)])

    def test_diff_thousands(self):
        obs = [("2026-07-01", 159000.0), ("2026-08-01", 159098.0)]
        self.assertEqual(diff_thousands(obs), [("2026-08-01", 98000)])

    def test_yoy_matches_same_month_across_gap(self):
        # 2025년 10월이 결측(셧다운)이어도 같은 달끼리 비교해야 한다
        obs = [(f"2025-{m:02d}-01", 100.0 + m) for m in range(1, 10)] + [("2025-11-01", 111.0), ("2025-12-01", 112.0)]
        obs += [(f"2026-{m:02d}-01", 110.0 + m) for m in range(1, 12)]
        result = dict(yoy(obs))
        self.assertEqual(result["2026-09-01"], round((119 / 109 - 1) * 100, 1))
        self.assertEqual(result["2026-11-01"], round((121 / 111 - 1) * 100, 1))
        self.assertNotIn("2026-10-01", result)

    def test_month_changes_skip_missing_previous_month(self):
        obs = [("2025-09-01", 100.0), ("2025-11-01", 102.0), ("2025-12-01", 103.02)]
        self.assertEqual(pct_change(obs), [("2025-12-01", 1.0)])
        payrolls = [("2025-09-01", 159000.0), ("2025-11-01", 159100.0), ("2025-12-01", 159150.0)]
        self.assertEqual(diff_thousands(payrolls), [("2025-12-01", 50000)])


class BuildIndicatorsTest(unittest.TestCase):
    NOW = "2026-09-12T06:00:00+09:00"

    def test_all_series_fetched_and_trimmed(self):
        text = monthly_csv([100 + i * 0.5 for i in range(40)])
        data = build_indicators(lambda sid: text, None, self.NOW)
        self.assertEqual(set(data["series"]), set(SERIES))
        gdp = data["series"]["A191RL1Q225SBEA"]
        self.assertFalse(gdp["stale"])
        self.assertEqual(len(gdp["obs"]), SERIES["A191RL1Q225SBEA"]["keep"])
        self.assertEqual(data["series"]["CPIAUCSL"]["last_success"], self.NOW)

    def test_failure_keeps_previous_and_marks_stale(self):
        previous = {"series": {"UNRATE": {"name": "실업률", "transform": "level", "unit": "%",
                                          "obs": [["2026-08-01", 4.4]], "stale": False,
                                          "last_success": "2026-09-05T06:00:00+09:00"}}}
        text = monthly_csv([4.0] * 20)

        def fetch(sid):
            if sid == "UNRATE":
                raise OSError("timeout")
            return text

        data = build_indicators(fetch, previous, self.NOW)
        unrate = data["series"]["UNRATE"]
        self.assertTrue(unrate["stale"])
        self.assertEqual(unrate["obs"], [["2026-08-01", 4.4]])
        self.assertEqual(unrate["last_success"], "2026-09-05T06:00:00+09:00")
        self.assertIn("timeout", unrate["error"])

    def test_failure_without_previous_gives_empty_stale(self):
        def fetch(sid):
            raise OSError("down")

        data = build_indicators(fetch, None, self.NOW)
        self.assertTrue(all(s["stale"] and s["obs"] == [] for s in data["series"].values()))


if __name__ == "__main__":
    unittest.main()

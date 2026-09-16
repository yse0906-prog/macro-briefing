"""이전치 수정(revision) 추적과 지표 설명 문구 검사.

고용보고서는 발표 때마다 지난 두 달 수치를 고쳐서 낸다. 이전 수집본과 새 수집본을
비교하면 별도 자료 없이 수정 내역을 알 수 있다.
"""
import unittest

from macro.fred import SERIES, revisions
from macro.help import HELP


class RevisionTest(unittest.TestCase):
    def test_detects_changed_months(self):
        old = [["2026-05-01", 44000], ["2026-06-01", 20000], ["2026-07-01", -23000]]
        new = [("2026-05-01", 44000), ("2026-06-01", 31000), ("2026-07-01", 21000)]
        self.assertEqual(
            revisions(old, new),
            [{"period": "2026-06-01", "from": 20000, "to": 31000},
             {"period": "2026-07-01", "from": -23000, "to": 21000}],
        )

    def test_no_revision_when_values_match(self):
        old = [["2026-06-01", 31000], ["2026-07-01", 21000]]
        new = [("2026-06-01", 31000), ("2026-07-01", 21000)]
        self.assertEqual(revisions(old, new), [])

    def test_new_month_is_not_a_revision(self):
        old = [["2026-07-01", 21000]]
        new = [("2026-07-01", 21000), ("2026-08-01", 162000)]
        self.assertEqual(revisions(old, new), [])

    def test_only_recent_months_are_compared(self):
        old = [["2026-01-01", 10000], ["2026-06-01", 20000], ["2026-07-01", 21000]]
        new = [("2026-01-01", 99000), ("2026-06-01", 31000), ("2026-07-01", 21000)]
        self.assertEqual(revisions(old, new, months=2), [{"period": "2026-06-01", "from": 20000, "to": 31000}])

    def test_empty_previous_gives_no_revisions(self):
        self.assertEqual(revisions([], [("2026-08-01", 162000)]), [])


class HelpTextTest(unittest.TestCase):
    def test_every_fred_series_has_help(self):
        missing = [sid for sid in SERIES if sid not in HELP]
        self.assertEqual(missing, [])

    def test_web_series_have_help(self):
        for sid in ("ISM_MFG", "ISM_SVC"):
            self.assertIn(sid, HELP)

    def test_help_entries_have_three_parts(self):
        for sid, entry in HELP.items():
            self.assertTrue(entry.get("what"), sid)
            self.assertTrue(entry.get("baseline"), sid)
            self.assertTrue(entry.get("reading"), sid)


if __name__ == "__main__":
    unittest.main()

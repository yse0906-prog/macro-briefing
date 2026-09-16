"""fetch_csv의 경로 선택 검사.

클라우드 실행 환경은 프록시를 거치는데, 파이썬 기본 방식(urllib)이 응답을 받지 못하고
멈추는 경우가 있다. 이때 curl로 넘어가야 수집이 계속된다.
"""
import unittest

from macro.fred import fetch_csv

CSV = "observation_date,CPIAUCSL\n2026-08-01,330.1\n"


class FetchCsvTest(unittest.TestCase):
    def test_direct_success_skips_fallback(self):
        calls = []

        def direct(url, timeout):
            calls.append("direct")
            return CSV

        def fallback(url, timeout):
            calls.append("fallback")
            return ""

        self.assertEqual(fetch_csv("CPIAUCSL", retries=2, wait=0, direct=direct, fallback=fallback), CSV)
        self.assertEqual(calls, ["direct"])

    def test_falls_back_to_curl_when_direct_times_out(self):
        calls = []

        def direct(url, timeout):
            calls.append("direct")
            raise TimeoutError("read operation timed out")

        def fallback(url, timeout):
            calls.append("fallback")
            return CSV

        self.assertEqual(fetch_csv("CPIAUCSL", retries=2, wait=0, direct=direct, fallback=fallback), CSV)
        self.assertEqual(calls, ["direct", "fallback"])

    def test_empty_response_counts_as_failure(self):
        def direct(url, timeout):
            return "   "

        def fallback(url, timeout):
            return CSV

        self.assertEqual(fetch_csv("CPIAUCSL", retries=1, wait=0, direct=direct, fallback=fallback), CSV)

    def test_raises_when_both_paths_fail(self):
        attempts = []

        def boom(url, timeout):
            attempts.append(url)
            raise OSError("blocked")

        with self.assertRaises(OSError):
            fetch_csv("CPIAUCSL", retries=2, wait=0, direct=boom, fallback=boom)
        self.assertEqual(len(attempts), 4)  # 2회 시도 × (직접 + curl)

    def test_url_contains_series_id(self):
        seen = []

        def direct(url, timeout):
            seen.append(url)
            return CSV

        fetch_csv("UNRATE", retries=1, wait=0, direct=direct, fallback=direct)
        self.assertIn("id=UNRATE", seen[0])


if __name__ == "__main__":
    unittest.main()

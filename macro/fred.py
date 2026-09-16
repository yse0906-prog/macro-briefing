"""FRED 시리즈 수집·변환. 네트워크 호출은 fetch 인자로 주입한다."""
import csv
import io
import subprocess
import time
import urllib.request

CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"

SERIES = {
    "CPIAUCSL": {"name": "CPI 전년비", "transform": "yoy", "unit": "%", "keep": 36},
    "CPILFESL": {"name": "근원 CPI 전년비", "transform": "yoy", "unit": "%", "keep": 36},
    "PPIFIS": {"name": "PPI 전월비", "transform": "pct", "unit": "%", "keep": 36},
    "PCEPILFE": {"name": "근원 PCE 전년비", "transform": "yoy", "unit": "%", "keep": 36},
    "PAYEMS": {"name": "비농업 고용 증감", "transform": "diff_k", "unit": "명", "keep": 36},
    "UNRATE": {"name": "실업률", "transform": "level", "unit": "%", "keep": 36},
    "ICSA": {"name": "신규 실업수당 청구", "transform": "level", "unit": "건", "keep": 52},
    "A191RL1Q225SBEA": {"name": "실질 GDP (연율)", "transform": "level", "unit": "%", "keep": 12},
    "RSAFS": {"name": "소매판매 전월비", "transform": "pct", "unit": "%", "keep": 36},
    "DGS10": {"name": "미 국채 10년물", "transform": "level", "unit": "%", "keep": 400},
    "DGS2": {"name": "미 국채 2년물", "transform": "level", "unit": "%", "keep": 400},
    "DTWEXBGS": {"name": "달러인덱스 (광의)", "transform": "level", "unit": "pt", "keep": 400},
    "VIXCLS": {"name": "VIX", "transform": "level", "unit": "pt", "keep": 400},
    "DEXKOUS": {"name": "원/달러", "transform": "level", "unit": "원", "keep": 400},
    "SP500": {"name": "S&P 500", "transform": "level", "unit": "pt", "keep": 400},
    "NASDAQCOM": {"name": "나스닥", "transform": "level", "unit": "pt", "keep": 400},
    "DFEDTARU": {"name": "연방기금금리 목표 상단", "transform": "level", "unit": "%", "keep": 1100},
    "DFEDTARL": {"name": "연방기금금리 목표 하단", "transform": "level", "unit": "%", "keep": 1100},
}


def parse_csv(text: str) -> list[tuple[str, float]]:
    rows = csv.reader(io.StringIO(text))
    next(rows, None)  # 헤더(DATE 또는 observation_date)
    out = []
    for row in rows:
        if len(row) < 2 or row[1].strip() in ("", "."):
            continue
        out.append((row[0], float(row[1])))
    return out


def _shift_month(day: str, months: int) -> str:
    y, m = int(day[:4]), int(day[5:7]) + months
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return f"{y}-{m:02d}{day[7:]}"


def yoy(obs, lag=12):
    """같은 달 1년 전 관측치와 비교한다. 결측 달(예: 2025년 10월 셧다운)이 있어도 날짜로 맞춘다."""
    values = dict(obs)
    out = []
    for day, value in obs:
        base = values.get(_shift_month(day, -lag))
        if base:
            out.append((day, round((value / base - 1) * 100, 1)))
    return out


def pct_change(obs):
    """직전 달 관측치가 있을 때만 전월 대비 %를 계산한다."""
    values = dict(obs)
    return [(day, round((value / values[prev] - 1) * 100, 1))
            for day, value in obs if (prev := _shift_month(day, -1)) in values]


def diff_thousands(obs):
    """PAYEMS(천 명 단위)의 전월 대비 증감을 명 단위로 돌려준다. 직전 달이 없으면 건너뛴다."""
    values = dict(obs)
    return [(day, round((value - values[prev]) * 1000))
            for day, value in obs if (prev := _shift_month(day, -1)) in values]


def level(obs):
    return [(d, round(v, 2)) for d, v in obs]


TRANSFORMS = {"yoy": yoy, "pct": pct_change, "diff_k": diff_thousands, "level": level}


HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; macro-briefing/1.0)",
    "Accept": "text/csv,text/plain,*/*",
    "Accept-Encoding": "identity",
    "Connection": "close",
}


def _direct_get(url: str, timeout: float) -> str:
    """파이썬 표준 라이브러리로 내려받는다."""
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def _curl_get(url: str, timeout: float) -> str:
    """curl로 내려받는다. 클라우드 프록시 환경에서 파이썬 경로가 멈출 때 쓰는 대체 경로."""
    result = subprocess.run(
        ["curl", "-sS", "--fail", "--max-time", str(int(timeout)), url],
        capture_output=True, text=True, timeout=timeout + 10,
    )
    if result.returncode != 0:
        raise OSError(f"curl 실패(코드 {result.returncode}): {result.stderr.strip()[:200]}")
    return result.stdout


def fetch_csv(series_id: str, retries: int = 3, wait: float = 2.0, timeout: float = 20,
              direct=_direct_get, fallback=_curl_get) -> str:
    """FRED CSV를 내려받는다. 파이썬 경로가 실패하면 curl로 한 번 더 시도한다."""
    url = CSV_URL.format(series=series_id)
    error = None
    for attempt in range(retries):
        for get in (direct, fallback):
            try:
                text = get(url, timeout)
                if text and text.strip():
                    return text
                error = OSError("빈 응답")
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                error = exc
        time.sleep(wait * (attempt + 1))
    raise error if isinstance(error, OSError) else OSError(str(error))


def build_indicators(fetch, previous, now_iso: str) -> dict:
    old_series = (previous or {}).get("series", {})
    result = {"fetched_at": now_iso, "series": {}}
    for sid, meta in SERIES.items():
        info = {"name": meta["name"], "transform": meta["transform"], "unit": meta["unit"]}
        try:
            obs = TRANSFORMS[meta["transform"]](parse_csv(fetch(sid)))
            if not obs:
                raise ValueError("관측치 없음")
            result["series"][sid] = {**info, "obs": [list(o) for o in obs[-meta["keep"]:]],
                                     "stale": False, "last_success": now_iso}
        except (OSError, ValueError, ZeroDivisionError) as exc:
            old = old_series.get(sid)
            base = old if old else {**info, "obs": [], "last_success": None}
            result["series"][sid] = {**base, "stale": True, "error": str(exc)}
    return result

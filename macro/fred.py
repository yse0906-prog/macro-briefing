"""FRED 시리즈 수집·변환. 네트워크 호출은 fetch 인자로 주입한다."""
import csv
import io
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


def yoy(obs, lag=12):
    """월간 시리즈 전제: 인덱스 lag칸 앞이 12개월 전이다."""
    return [(obs[i][0], round((obs[i][1] / obs[i - lag][1] - 1) * 100, 1)) for i in range(lag, len(obs))]


def pct_change(obs):
    return [(obs[i][0], round((obs[i][1] / obs[i - 1][1] - 1) * 100, 1)) for i in range(1, len(obs))]


def diff_thousands(obs):
    """PAYEMS(천 명 단위)의 전월 대비 증감을 명 단위로 돌려준다."""
    return [(obs[i][0], round((obs[i][1] - obs[i - 1][1]) * 1000)) for i in range(1, len(obs))]


def level(obs):
    return [(d, round(v, 2)) for d, v in obs]


TRANSFORMS = {"yoy": yoy, "pct": pct_change, "diff_k": diff_thousands, "level": level}


def fetch_csv(series_id: str, retries: int = 3, wait: float = 2.0) -> str:
    request = urllib.request.Request(CSV_URL.format(series=series_id), headers={"User-Agent": "macro-briefing/1.0"})
    error = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8")
        except OSError as exc:
            error = exc
            time.sleep(wait * (attempt + 1))
    raise error


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

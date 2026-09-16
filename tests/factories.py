"""테스트 전용 데이터. 실제 data/ 폴더에는 넣지 않는다."""
import copy
import json
from datetime import date, timedelta
from pathlib import Path

FETCHED = "2026-09-12T06:00:00+09:00"
CPI = [2.4, 2.6, 2.7, 2.9, 3.0, 2.8, 2.4, 2.3, 2.4, 2.7, 2.7, 2.9, 3.0, 3.0, 2.7, 2.7, 2.5, 2.6, 2.8, 3.0, 2.9, 2.9, 2.9, 3.1]
CORE = [3.3, 3.3, 3.3, 3.2, 3.3, 3.1, 2.8, 2.8, 2.8, 2.9, 3.1, 3.1, 3.1, 3.0, 2.8, 2.6, 2.5, 2.6, 2.8, 2.9, 3.0, 3.0, 3.1, 3.2]
UNEMP = [4.1, 4.1, 4.2, 4.1, 4.0, 4.1, 4.2, 4.2, 4.2, 4.1, 4.2, 4.3, 4.4, 4.4, 4.5, 4.4, 4.3, 4.4, 4.3, 4.3, 4.3, 4.3, 4.3, 4.4]


def _months(start: str, values: list, step: int = 1) -> list:
    y, m = int(start[:4]), int(start[5:7])
    out = []
    for v in values:
        out.append([f"{y}-{m:02d}-01", v])
        m += step
        while m > 12:
            y, m = y + 1, m - 12
    return out


def _weeks(end: str, values: list) -> list:
    last = date.fromisoformat(end)
    n = len(values)
    return [[(last - timedelta(weeks=n - 1 - i)).isoformat(), v] for i, v in enumerate(values)]


def _business_days(end: str, values: list) -> list:
    d, days = date.fromisoformat(end), []
    while len(days) < len(values):
        if d.weekday() < 5:
            days.append(d.isoformat())
        d -= timedelta(days=1)
    return [[day, v] for day, v in zip(reversed(days), values)]


def _series(name, transform, unit, obs):
    return {"name": name, "transform": transform, "unit": unit, "obs": obs, "stale": False, "last_success": FETCHED}


def _flat(before, last, n=65):
    return [before] * (n - 1) + [last]


def make_indicators() -> dict:
    daily = lambda values: _business_days("2026-09-11", values)
    return {"fetched_at": FETCHED, "series": {
        "CPIAUCSL": _series("CPI 전년비", "yoy", "%", _months("2024-09", CPI)),
        "CPILFESL": _series("근원 CPI 전년비", "yoy", "%", _months("2024-09", CORE)),
        "PPIFIS": _series("PPI 전월비", "pct", "%", _months("2025-09", [0.2, 0.1, 0.3, -0.1, 0.2, 0.4, 0.1, 0.2, 0.3, 0.1, 0.1, 0.3])),
        "PCEPILFE": _series("근원 PCE 전년비", "yoy", "%", _months("2025-08", [2.8, 2.8, 2.9, 2.8, 2.7, 2.7, 2.8, 2.9, 2.9, 3.0, 3.0, 3.1])),
        "PAYEMS": _series("비농업 고용 증감", "diff_k", "명", _months("2025-09", [142000, 88000, 210000, 130000, 75000, 160000, 118000, 95000, 140000, 132000, 132000, 98000])),
        "UNRATE": _series("실업률", "level", "%", _months("2024-09", UNEMP)),
        "ICSA": _series("신규 실업수당 청구", "level", "건", _weeks("2026-09-05", [228000, 235000, 241000, 226000, 230000, 238000, 244000, 236000, 229000, 233000, 240000, 231000])),
        "A191RL1Q225SBEA": _series("실질 GDP (연율)", "level", "%", _months("2024-07", [3.0, 3.1, 2.4, -0.5, 3.3, 1.9, 2.2, 1.6], step=3)),
        "RSAFS": _series("소매판매 전월비", "pct", "%", _months("2025-08", [0.4, -0.2, 0.6, 0.1, 0.3, -0.4, 0.5, 0.2, 0.0, 0.3, 0.4, 0.2])),
        "DGS10": _series("미 국채 10년물", "level", "%", daily(_flat(4.32, 4.38))),
        "DGS2": _series("미 국채 2년물", "level", "%", daily(_flat(3.62, 3.71))),
        "DTWEXBGS": _series("달러인덱스 (광의)", "level", "pt", daily(_flat(121.0, 121.4))),
        "VIXCLS": _series("VIX", "level", "pt", daily(_flat(16.6, 17.8))),
        "DEXKOUS": _series("원/달러", "level", "원", daily(_flat(1469.0, 1478.0))),
        "SP500": _series("S&P 500", "level", "pt", daily(_flat(6463.97, 6412.3))),
        "NASDAQCOM": _series("나스닥", "level", "pt", daily(_flat(21488.4, 21230.5))),
        "CIVPART": _series("경제활동참가율", "level", "%", _months("2025-09", [62.1, 62.0, 62.0, 61.9, 61.8, 61.8, 61.7, 61.6, 61.5, 61.5, 61.4, 61.6])),
        "CES0500000003": _series("시간당 평균임금", "level", "달러", _months("2025-09", [36.6, 36.7, 36.8, 36.9, 37.0, 37.1, 37.2, 37.3, 37.4, 37.5, 37.65, 37.75])),
        "USCONS": _series("건설", "diff_k", "명", _months("2025-09", [5000, -3000, 8000, 12000, 4000, 9000, 15000, 7000, 11000, 6000, 13000, 22000])),
        "MANEMP": _series("제조", "diff_k", "명", _months("2025-09", [-2000, -5000, 3000, 1000, -4000, 2000, 6000, -1000, 4000, -3000, 8000, 16000])),
        "USTRADE": _series("소매", "diff_k", "명", _months("2025-09", [4000, 7000, -2000, 5000, 1000, -6000, 3000, 2000, -1000, 4000, 2000, 1400])),
        "USPBS": _series("전문·사업서비스", "diff_k", "명", _months("2025-09", [12000, 8000, -4000, 6000, 3000, -2000, 9000, 5000, 2000, 7000, 4000, 10000])),
        "USEHS": _series("교육·보건", "diff_k", "명", _months("2025-09", [45000, 38000, 41000, 36000, 33000, 29000, 35000, 31000, 28000, 34000, 30000, 29000])),
        "USLAH": _series("레저·숙박", "diff_k", "명", _months("2025-09", [18000, 12000, 22000, 9000, 15000, 7000, 19000, 11000, 24000, 13000, 16000, 62000])),
        "DFEDTARU": _series("연방기금금리 목표 상단", "level", "%", daily([4.0] * 300 + [3.75] * 400)),
        "DFEDTARL": _series("연방기금금리 목표 하단", "level", "%", daily([3.75] * 300 + [3.5] * 400)),
    }}


def _release(series, name, release_date, period, consensus, impact):
    return {"series": series, "name": name, "release_date": release_date, "period": period,
            "consensus": consensus, "consensus_source": 1, "impact": impact,
            "interpretation": f"{name} 해석 문장입니다."}


def _sector(name, gics, impact, symbol):
    return {"name": name, "gics": gics, "impact": impact, "title": f"{name} 이슈 제목", "analysis": f"{name} 분석 문단입니다.",
            "tickers": [{"symbol": symbol, "change_pct": 1.2}],
            "news": [{"headline": f"{name} 뉴스 헤드라인", "outlet": "테스트통신", "url": "https://example.com/news", "date": "2026-09-10"}]}


LAST_MEETING = {"date": "2026-07-29", "decision": "hold", "range": [3.5, 3.75], "vote": {"for": 10, "against": 2},
                "tone": 0.64, "statement_points": ["경제활동은 완만한 속도로 확장"], "press_conference": "기자회견 요지"}


def make_briefing(**overrides) -> dict:
    b = {
        "date": "2026-09-13", "type": "weekly",
        "period": {"from": "2026-09-07", "to": "2026-09-11"},
        "published_at": "2026-09-13T07:00:00+09:00",
        "headline": "물가 재가속에 9월 동결 무게, 금리 민감 섹터 약세·금융주 선방",
        "summary": ["첫째 요약 문장.", "둘째 요약 문장.", "셋째 요약 문장."],
        "releases": [
            _release("PAYEMS", "비농업 고용 (8월)", "2026-09-04", "2026-08-01", 110000, "neutral"),
            _release("UNRATE", "실업률 (8월)", "2026-09-04", "2026-08-01", 4.3, "neutral"),
            _release("CPIAUCSL", "CPI 전년비 (8월)", "2026-09-10", "2026-08-01", 3.0, "negative"),
            _release("CPILFESL", "근원 CPI 전년비 (8월)", "2026-09-10", "2026-08-01", 3.1, "negative"),
            _release("PPIFIS", "PPI 전월비 (8월)", "2026-09-11", "2026-08-01", 0.2, "neutral"),
            _release("ICSA", "신규 실업수당 청구", "2026-09-11", "2026-09-05", 235000, "positive"),
            {**_release("ISM_MFG", "ISM 제조업 PMI (8월)", "2026-09-01", "2026-08-01", 49.5, "neutral"),
             "actual": 49.9, "previous": 49.2, "actual_source": 2},
        ],
        "fomc": {
            "next_meeting": {
                "date": "2026-09-16", "announce_kst": "2026-09-17T03:00:00+09:00",
                "probabilities": [{"outcome": "hold", "pct": 78}, {"outcome": "cut25", "pct": 22}],
                "probabilities_week_ago": [{"outcome": "hold", "pct": 61}, {"outcome": "cut25", "pct": 39}],
                "view": "hold", "confidence": "high",
                "rationale": ["근원 CPI 3.2%로 목표와 거리 확대"], "watch_points": ["점도표 연내 인하 횟수"],
            },
            "last_meeting": copy.deepcopy(LAST_MEETING),
        },
        "sectors": [
            _sector("금융", "Financials", "positive", "JPM"),
            _sector("반도체·AI", "Information Technology", "mixed", "NVDA"),
            _sector("부동산", "Real Estate", "negative", "PLD"),
            _sector("에너지", "Energy", "positive", "XOM"),
        ],
        "market_impact": [
            {"asset": "us_equities", "direction": "down", "text": "성장주 중심 조정"},
            {"asset": "us_rates", "direction": "up", "text": "10년물 상승"},
            {"asset": "usd", "direction": "up", "text": "달러 강세"},
            {"asset": "krw", "direction": "up", "text": "원/달러 상승"},
            {"asset": "korea_banks", "direction": None, "text": "외화 조달비용 부담"},
        ],
        "scenarios": [
            {"name": "기본 · 매파적 동결", "probability": 60, "text": "기본 시나리오 설명"},
            {"name": "매파 충격", "probability": 25, "text": "매파 시나리오 설명"},
            {"name": "비둘기 선회", "probability": 15, "text": "비둘기 시나리오 설명"},
        ],
        "interview_insights": [
            {"question": "CPI 상회가 은행 수익성에 주는 영향은?", "answer_points": "금리차와 조달비용 경로로 설명"},
            {"question": "동결 확률 78%의 의미는?", "answer_points": "선물 가격에서 역산한 확률"},
        ],
        "sources": [
            {"id": 1, "title": "시장 예상치", "url": "https://example.com/consensus", "accessed": "2026-09-12"},
            {"id": 2, "title": "ISM 보도자료", "url": "https://example.com/ism", "accessed": "2026-09-12"},
        ],
    }
    b.update(copy.deepcopy(overrides))
    return b


def make_event_briefing(**overrides) -> dict:
    b = {
        "date": "2026-09-17", "type": "event",
        "published_at": "2026-09-17T07:00:00+09:00",
        "headline": "FOMC 동결, 점도표 연내 인하 0회로 축소",
        "summary": ["첫째 요약 문장.", "둘째 요약 문장.", "셋째 요약 문장."],
        "fomc": {"last_meeting": {**copy.deepcopy(LAST_MEETING), "date": "2026-09-16", "tone": 0.72}},
        "market_impact": [{"asset": "us_rates", "direction": "up", "text": "단기물 상승"}],
        "sources": [{"id": 1, "title": "연준 성명서", "url": "https://www.federalreserve.gov/", "accessed": "2026-09-17"}],
    }
    b.update(copy.deepcopy(overrides))
    return b


def make_market() -> dict:
    return {"as_of": "2026-09-11", "items": [
        {"id": "kospi", "label": "코스피", "value": 4118.6, "change": -0.5, "unit": "%", "source": "https://example.com/kospi"},
        {"id": "kosdaq", "label": "코스닥", "value": 912.4, "change": -0.9, "unit": "%", "source": "https://example.com/kosdaq"},
        {"id": "vkospi", "label": "VKOSPI", "value": 24.7, "change": 1.6, "unit": "pt", "source": "https://example.com/vkospi"},
        {"id": "usdkrw", "label": "원/달러", "value": 1478.0, "change": 0.6, "unit": "%", "source": "https://example.com/usdkrw"},
    ]}


def make_calendar() -> dict:
    return {"updated_at": "2026-09-13T07:00:00+09:00", "events": [
        {"kst": "2026-09-15T21:30:00+09:00", "name": "소매판매 (8월)", "importance": 2, "kind": "release"},
        {"kst": "2026-09-17T03:00:00+09:00", "name": "FOMC 금리 결정·기자회견", "importance": 3, "kind": "fomc"},
        {"kst": "2026-09-17T21:30:00+09:00", "name": "신규 실업수당 청구", "importance": 1, "kind": "release"},
    ]}


def write_data(data_dir: Path, *, briefings=(), indicators=None, market=None, calendar=None) -> None:
    (data_dir / "briefings").mkdir(parents=True, exist_ok=True)
    dump = lambda path, obj: path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    for b in briefings:
        dump(data_dir / "briefings" / f"{b['date']}.json", b)
    for name, obj in (("indicators.json", indicators), ("market.json", market), ("calendar.json", calendar)):
        if obj is not None:
            dump(data_dir / name, obj)

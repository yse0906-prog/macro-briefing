"""data/ 읽기와 페이지용 값 계산. 렌더러는 계산하지 않고 이 모듈을 호출한다."""
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from macro.fred import SERIES

US_TICKER = [
    ("sp500", "S&P 500", "SP500", "pct"),
    ("nasdaq", "나스닥", "NASDAQCOM", "pct"),
    ("us10y", "미 10년물", "DGS10", "bp"),
    ("dxy", "달러인덱스", "DTWEXBGS", "pct"),
    ("vix", "VIX", "VIXCLS", "pt"),
]
KR_ORDER = ["kospi", "kosdaq", "vkospi", "usdkrw"]
UNIT_OF_KIND = {"pct": "%", "bp": "bp", "pt": "pt"}


@dataclass
class SiteData:
    indicators: dict = field(default_factory=lambda: {"series": {}})
    market: dict | None = None
    calendar: dict | None = None
    briefings: list = field(default_factory=list)
    sectors: list = field(default_factory=list)

    @property
    def latest(self) -> dict | None:
        return self.briefings[0] if self.briefings else None

    @property
    def latest_sectors(self) -> dict | None:
        return self.sectors[0] if self.sectors else None


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def load_site_data(data_dir: Path) -> SiteData:
    briefings = [_read(p) for p in (data_dir / "briefings").glob("*.json")]
    briefings.sort(key=lambda b: (b["date"], b.get("published_at", "")), reverse=True)
    sectors = [_read(p) for p in (data_dir / "sectors").glob("*.json")]
    sectors.sort(key=lambda s: s["date"], reverse=True)
    return SiteData(
        indicators=_read(data_dir / "indicators.json") or {"series": {}},
        market=_read(data_dir / "market.json"),
        calendar=_read(data_dir / "calendar.json"),
        briefings=briefings,
        sectors=sectors,
    )


def obs(indicators: dict, series_id: str) -> list[tuple[str, float]]:
    return [(day, value) for day, value in indicators.get("series", {}).get(series_id, {}).get("obs", [])]


def is_stale(indicators: dict, series_id: str) -> bool:
    return indicators.get("series", {}).get(series_id, {}).get("stale", True)


def release_values(indicators: dict, release: dict) -> dict:
    if release["series"] not in SERIES:
        return {"actual": release.get("actual"), "previous": release.get("previous")}
    points = obs(indicators, release["series"])
    for i, (day, value) in enumerate(points):
        if day == release["period"]:
            return {"actual": value, "previous": points[i - 1][1] if i > 0 else None}
    return {"actual": None, "previous": None}


def weekly_change(points, kind: str):
    if len(points) < 2:
        return None
    last_day, last_value = points[-1]
    cutoff = (date.fromisoformat(last_day) - timedelta(days=7)).isoformat()
    base = [value for day, value in points if day <= cutoff]
    if not base:
        return None
    if kind == "pct":
        change = round((last_value / base[-1] - 1) * 100, 1)
    elif kind == "bp":
        change = round((last_value - base[-1]) * 100)
    else:
        change = round(last_value - base[-1], 1)
    return last_value, change


def us_ticker(indicators: dict) -> list[dict]:
    rows = []
    for key, label, series_id, kind in US_TICKER:
        result = weekly_change(obs(indicators, series_id), kind)
        if result:
            rows.append({"id": key, "label": label, "value": result[0], "change": result[1], "unit": UNIT_OF_KIND[kind]})
    return rows


def kr_ticker(market: dict | None) -> list[dict]:
    items = {item["id"]: item for item in (market or {}).get("items", [])}
    return [items[key] for key in KR_ORDER if key in items]


def monthly_last(points, n: int):
    months = {}
    for day, value in points:
        months[day[:7]] = value
    return list(months.items())[-n:]


def weekly_last(points, n: int):
    weeks = {}
    for day, value in points:
        weeks[date.fromisoformat(day).isocalendar()[:2]] = (day, value)
    return list(weeks.values())[-n:]


def latest_release(site: SiteData, series_id: str):
    for briefing in site.briefings:
        for release in briefing.get("releases", []):
            if release["series"] == series_id:
                return briefing, release
    return None, None


def current_range(indicators: dict):
    lower, upper = obs(indicators, "DFEDTARL"), obs(indicators, "DFEDTARU")
    if not lower or not upper:
        return None
    return lower[-1][1], upper[-1][1]


def fomc_history(site: SiteData) -> list[dict]:
    meetings = {}
    for briefing in site.briefings:
        meeting = briefing.get("fomc", {}).get("last_meeting")
        if meeting and meeting["date"] not in meetings:
            meetings[meeting["date"]] = meeting
    return [meetings[key] for key in sorted(meetings, reverse=True)]


def next_meeting(site: SiteData, today: date):
    for briefing in site.briefings:
        meeting = briefing.get("fomc", {}).get("next_meeting")
        if meeting:
            return meeting if date.fromisoformat(meeting["date"]) >= today else None
    return None


def upcoming_events(calendar, today: date, days: int = 7) -> list[dict]:
    end = today + timedelta(days=days)
    events = [e for e in (calendar or {}).get("events", []) if today <= datetime.fromisoformat(e["kst"]).date() <= end]
    return sorted(events, key=lambda e: e["kst"])


def dday(target_iso: str, today: date) -> str:
    days = (date.fromisoformat(target_iso[:10]) - today).days
    return f"D-{days}" if days > 0 else ("D-DAY" if days == 0 else "종료")

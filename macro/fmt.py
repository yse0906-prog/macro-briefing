"""표시용 포맷 헬퍼. 모든 페이지 렌더러가 공유한다."""
import html
from datetime import date, datetime

MINUS = "−"
WEEKDAYS = "월화수목금토일"


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def num(value, digits=1) -> str:
    if value is None:
        return "—"
    text = f"{abs(value):,.{digits}f}"
    return MINUS + text if value < 0 else text


def signed(value, digits=1, suffix="") -> str:
    if value is None:
        return "—"
    sign = "+" if value > 0 else (MINUS if value < 0 else "")
    return f"{sign}{abs(value):,.{digits}f}{suffix}"


def man(count) -> str:
    """사람·건수를 '만' 단위로 표시한다. 98000 -> '9.8만'"""
    if count is None:
        return "—"
    return num(count / 10000, 1) + "만"


def to_date(iso: str) -> date:
    return date.fromisoformat(iso[:10])


def md(iso: str) -> str:
    d = to_date(iso)
    return f"{d.month}.{d.day:02d}"


def ymd_ko(iso: str) -> str:
    d = to_date(iso)
    return f"{d.year}년 {d.month}월 {d.day}일({WEEKDAYS[d.weekday()]})"


def kst_time(iso: str) -> str:
    dt = datetime.fromisoformat(iso)
    return f"{dt.month}.{dt.day:02d}({WEEKDAYS[dt.weekday()]}) {dt:%H:%M}"

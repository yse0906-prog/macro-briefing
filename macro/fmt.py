"""표시용 포맷 헬퍼. 모든 페이지 렌더러가 공유한다."""
import html
import re
from datetime import date, datetime

MINUS = "−"
WEEKDAYS = "월화수목금토일"


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


_BOLD = re.compile(r"\*\*(.+?)\*\*")
_POS = re.compile(r"\[\[\+(.+?)\]\]")
_NEG = re.compile(r"\[\[-(.+?)\]\]")


def rich(value) -> str:
    """본문 강조: **조건** 굵게, [[+결과]] 유리(초록), [[-결과]] 불리(빨강). HTML은 먼저 이스케이프한다."""
    text = esc(value)
    text = _POS.sub(r'<mark class="hl-pos">\1</mark>', text)
    text = _NEG.sub(r'<mark class="hl-neg">\1</mark>', text)
    return _BOLD.sub(r"<strong>\1</strong>", text)


def plain(value) -> str:
    text = "" if value is None else str(value)
    text = _POS.sub(r"\1", _NEG.sub(r"\1", text))
    return _BOLD.sub(r"\1", text)


def markup_errors(text: str) -> list[str]:
    """짝이 안 맞는 강조 표시를 찾는다."""
    rest = _BOLD.sub("", _POS.sub("", _NEG.sub("", text)))
    errors = []
    if "**" in rest:
        errors.append("** 짝이 맞지 않음")
    if "[[" in rest or "]]" in rest:
        errors.append("[[+ ]] 또는 [[- ]] 형식이 아님")
    return errors


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

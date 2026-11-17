"""텔레그램 알림 메시지. 새 브리핑이 올라오면 깃허브가 이 글을 보낸다.

링크를 열지 않아도 숫자와 방향이 보이는 것이 목적이다. 텔레그램 HTML 모드를 쓰므로
<b>·<a>만 쓰고 나머지 글자는 &, <, > 를 escape 한다.
"""
import html

from macro import components as c
from macro import data as d
from macro.fmt import md, strip_markup, ymd_ko
from macro.layout import SITE_URL

LIMIT = 4096
ARROW = {"up": "↑", "down": "↓", None: "·"}
STATUS_MARK = {"positive": "호재", "negative": "악재", "neutral": "중립", "mixed": "혼조"}


def esc(value) -> str:
    """텔레그램 HTML용. 따옴표는 그대로 둬야 읽기 좋다."""
    return html.escape(strip_markup(value), quote=False)


def _releases(site, b: dict) -> list[str]:
    lines = []
    for r in b.get("releases", []):
        v = c.release_view(site.indicators, r)
        surprise = f" {v['surprise']}" if v["surprise"] else ""
        guess = f" (예상 {esc(v['consensus'])})" if r.get("consensus") is not None else ""
        lines.append(f"· {esc(v['name'])}  <b>{esc(v['actual'])}</b>{guess}{esc(surprise)}")
    return lines


def _fomc(b: dict) -> list[str]:
    fomc = b.get("fomc", {})
    lines = []
    last = fomc.get("last_meeting")
    if last:
        lines.append(f"· {md(last['date'])} 결정 <b>{c.OUTCOME_LABEL.get(last['decision'], last['decision'])}</b>"
                     f" · {c.range_text(*last['range'])}")
    nxt = fomc.get("next_meeting")
    if nxt:
        top = max(nxt.get("probabilities", []), key=lambda p: p["pct"], default=None)
        if top:
            lines.append(f"· 다음 {md(nxt['date'])} 회의 "
                         f"{c.OUTCOME_LABEL.get(top['outcome'], top['outcome'])} <b>{top['pct']}%</b>")
    return lines


def _lead(text: str, limit: int = 110) -> str:
    """휴대폰에서 읽기 좋게 첫 문장만. 문장이 길면 자른다."""
    head = strip_markup(text).split(". ")[0].rstrip(".")
    return head + "." if len(head) <= limit else head[:limit].rstrip() + "…"


def _impact(b: dict) -> list[str]:
    return [f"· {c.ASSET_LABEL[i['asset']]} {ARROW[i['direction']]} {esc(_lead(i['text']))}"
            for i in b.get("market_impact", [])]


def _sectors(site, b: dict) -> list[str]:
    day = next((s for s in site.sectors if s["date"] == b["date"]), None)
    if day is None:
        return []
    chips = " · ".join(f"{esc(s['name'])} {STATUS_MARK.get(s.get('status'), '')}"
                       for s in day.get("sectors", []))
    return ["", "<b>섹터</b>", chips,
            f'<a href="{SITE_URL}sectors/{day["date"]}.html">7개 섹터 자세히</a>']


def _block(title: str, lines: list[str]) -> list[str]:
    return ["", f"<b>{title}</b>", *lines] if lines else []


def telegram_message(site) -> str:
    """가장 최근 브리핑 하나를 요약한다. 브리핑이 없으면 빈 글자."""
    b = site.latest
    if b is None:
        return ""
    label = "이벤트 브리핑" if b.get("type") == "event" else "주간 브리핑"
    parts = [f"<b>{ymd_ko(b['date'])} {label}</b>", esc(b["headline"]), ""]
    parts += [f"{i}. {esc(s)}" for i, s in enumerate(b.get("summary", []), 1)]
    parts += _block("지표", _releases(site, b))
    parts += _block("FOMC", _fomc(b))
    parts += _block("시장 영향", _impact(b))
    parts += _sectors(site, b)
    parts += ["", f'<a href="{SITE_URL}briefings/{b["date"]}.html">전체 브리핑 보기</a>']

    text = "\n".join(parts)
    if len(text) > LIMIT:
        # 넘치면 뒤에서부터 줄을 덜어내되 링크 줄은 남긴다
        tail = parts[-2:]
        body, room = parts[:-2], LIMIT - len("\n".join(tail)) - 2
        while body and len("\n".join(body)) > room:
            body.pop()
        text = "\n".join(body + tail)
    return text

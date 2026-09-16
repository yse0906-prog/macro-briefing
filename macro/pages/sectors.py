"""섹터 이슈 페이지(sectors.html). 평일마다 갱신되고 날짜별로 쌓인다."""
from macro import components as c
from macro.fmt import esc, kst_time, ymd_ko
from macro.layout import page

STATUS = {
    "positive": ("chip-pos", "up", "호재"),
    "negative": ("chip-neg", "down", "악재"),
    "neutral": ("chip-neu", None, "중립"),
    "mixed": ("chip-neu", None, "혼조"),
}

CSS = """
.s-head{background:#FFFFFF;border-bottom:1px solid #DDE2EA}
.s-head .wrap{padding-top:40px;padding-bottom:28px;display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}
.s-head h1{font-size:36px;line-height:1.3;color:#0B1A30;margin-top:12px}
.s-main{display:flex;flex-direction:column;gap:24px;padding-top:40px}
.s-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.sec{padding:22px;display:flex;flex-direction:column;gap:12px}
.sec-top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.sec-top b{font-size:18px}
.sec-h{font-size:16px;font-weight:600;line-height:1.5;color:#0B1A30}
.sec-p{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:8px;font-size:14px;line-height:1.7;color:#2B3A50}
.sec-p a{font-size:12px;color:#6B7A90}
.sec-quiet{font-size:14px;color:#6B7A90}
.watch{border-top:1px solid #EDF0F4;padding-top:12px;display:flex;flex-direction:column;gap:10px}
.watch-t{font-size:13px;font-weight:600;color:#5B6B80}
.watch-row{display:flex;gap:10px;font-size:14px;line-height:1.6;color:#2B3A50}
.watch-row b{flex-shrink:0;width:84px;color:#0B1A30}
.ticks{display:flex;gap:8px;flex-wrap:wrap}
.tick{display:inline-flex;align-items:center;gap:5px;height:28px;padding:0 10px;border-radius:4px;background:#F1F4F8;font-size:13px;font-weight:600;color:#2B3A50}
.past{display:flex;gap:10px;flex-wrap:wrap}
.past a{padding:8px 14px;border:1px solid #DDE2EA;border-radius:20px;background:#FFFFFF;font-size:13px}
@media (max-width:640px){.s-head h1{font-size:26px}.s-grid{grid-template-columns:repeat(1,minmax(0,1fr))}.sec{padding:18px}}
"""


def _ticker_chip(t: dict) -> str:
    change = t.get("change_pct")
    direction = None if not change else ("up" if change > 0 else "down")
    text = "—" if change is None else f"{abs(change):.1f}%"
    return f'<span class="tick num">{esc(t["symbol"])}{c.arrow(direction)}{text}</span>'


def _sector_card(sector: dict, sources: dict) -> str:
    cls, direction, label = STATUS.get(sector.get("status"), STATUS["neutral"])
    points = "".join(
        f'<li>{esc(p["text"])} '
        f'<a href="{esc(sources.get(p.get("source"), "#"))}" target="_blank" rel="noopener">[출처]</a></li>'
        for p in sector.get("points", [])
    )
    body = f'<ul class="sec-p">{points}</ul>' if points else '<p class="sec-quiet">오늘은 이렇다 할 변화가 없었습니다.</p>'
    ticks = "".join(_ticker_chip(t) for t in sector.get("tickers", []))
    watch = ""
    if sector.get("watch"):
        rows = "".join(
            f'<div class="watch-row"><b>{esc(w["company"])}</b><span>{esc(w["text"])} '
            f'<a href="{esc(sources.get(w.get("source"), "#"))}" target="_blank" rel="noopener">[출처]</a></span></div>'
            for w in sector["watch"]
        )
        watch = f'<div class="watch"><span class="watch-t">비상장 AI 기업 동향</span>{rows}</div>'
    return f"""<div class="card sec">
<div class="sec-top"><b>{esc(sector["name"])}</b><span class="chip {cls}">{c.arrow(direction)}{label}</span></div>
<span class="sec-h">{esc(sector["headline"])}</span>
{body}
<div class="ticks">{ticks}</div>
{watch}
</div>"""


def render_sectors(site, day: dict | None = None) -> str:
    current = day or site.latest_sectors
    if current is None:
        body = f'<main class="wrap s-main">{c.empty_state(c.EMPTY_MESSAGE)}</main>'
        return page(title="섹터 이슈", active="sectors", body=body, css=c.CSS + CSS)

    sources = {s["id"]: s["url"] for s in current.get("sources", [])}
    cards = "".join(_sector_card(s, sources) for s in current.get("sectors", []))
    past = "".join(
        f'<a href="sectors/{d["date"]}.html">{ymd_ko(d["date"])}</a>'
        for d in site.sectors[:8] if d["date"] != current["date"]
    )
    past_block = f'<section class="wrap stack"><h2 class="h2">지난 이슈</h2><div class="past">{past}</div></section>' if past else ""
    head = (f'<div class="s-head"><div class="wrap"><div><span class="eyebrow">섹터 이슈</span>'
            f'<h1 class="serif">오늘 7개 섹터에서 무슨 일이 있었나</h1>'
            f'<span class="muted">금융 · 에너지 · 바이오 · 반도체 · AI · 로봇 · 부동산 · 평일 아침 갱신</span></div>'
            f'<span class="muted num">{kst_time(current["updated_at"])} KST 기준</span></div></div>')
    body = f'{head}<main class="s-main"><section class="wrap"><div class="s-grid">{cards}</div></section>{past_block}</main>'
    return page(title=f"섹터 이슈 {current['date']}", active="sectors", body=body, css=c.CSS + CSS)


def render_sectors_day(site, day: dict) -> str:
    """날짜별 보관본. 하위 폴더에 저장되므로 링크 기준 경로가 다르다."""
    sources = {s["id"]: s["url"] for s in day.get("sources", [])}
    cards = "".join(_sector_card(s, sources) for s in day.get("sectors", []))
    head = (f'<div class="s-head"><div class="wrap"><div><span class="eyebrow">섹터 이슈 · 보관본</span>'
            f'<h1 class="serif">{ymd_ko(day["date"])}</h1>'
            f'<span class="muted"><a href="../sectors.html">오늘 섹터 이슈 보기</a></span></div>'
            f'<span class="muted num">{kst_time(day["updated_at"])} KST 기준</span></div></div>')
    body = f'{head}<main class="s-main"><section class="wrap"><div class="s-grid">{cards}</div></section></main>'
    return page(title=f"섹터 이슈 {day['date']}", active="sectors", body=body, root="../", css=c.CSS + CSS)

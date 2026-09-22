"""섹터 이슈 페이지(sectors.html). 평일마다 갱신되고 날짜별로 쌓인다."""
from macro import components as c
from macro import visuals as v
from macro.fmt import esc, kst_time, rich, ymd_ko
from macro.layout import page

STATUS = {
    "positive": ("chip-pos", "up", "호재"),
    "negative": ("chip-neg", "down", "악재"),
    "neutral": ("chip-neu", None, "중립"),
    "mixed": ("chip-mix", None, "혼조"),
}

CSS = """
.s-head{background:#FFFFFF;border-bottom:1px solid #DDE2EA}
.s-head .wrap{padding-top:40px;padding-bottom:24px;display:flex;flex-direction:column;gap:20px}
.s-top{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}
.s-head h1{font-size:36px;line-height:1.3;color:#0B1A30;margin-top:12px}
.quick{display:flex;gap:8px;flex-wrap:wrap;position:sticky;top:0;z-index:30;background:#FFFFFF;padding:12px 0}
.quick a{display:inline-flex;align-items:center;gap:6px;height:38px;padding:0 16px;border:1px solid #DDE2EA;border-radius:19px;font-size:14px;font-weight:600;color:#2B3A50;background:#FFFFFF}
.quick a:hover{border-color:#1D3A66;text-decoration:none}
.quick i{width:8px;height:8px;border-radius:2px}
.q-pos{background:#1B8F52}.q-neg{background:#C9362E}.q-neu{background:#8A97AB}.q-mix{background:#D08A2E}
.s-main{display:flex;flex-direction:column;gap:20px;padding-top:32px}
.sec{padding:26px 28px;display:flex;flex-direction:column;gap:16px;scroll-margin-top:72px}
.sec-top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.sec-name{display:flex;align-items:baseline;gap:10px}
.sec-name b{font-size:22px;color:#0B1A30}
.sec-days{font-size:12px;color:#6B7A90;background:#F1F4F8;border-radius:10px;padding:3px 10px}
.sec-h{font-size:17px;font-weight:600;line-height:1.55;color:#0B1A30}
.part{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}
.part-k{width:104px;flex-shrink:0;font-size:13px;font-weight:700;color:#5B6B80;padding-top:2px}
.part-v{flex:1;min-width:240px;font-size:15px;line-height:1.75;color:#2B3A50}
.part-v ul{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px}
.part-v a{font-size:12px;color:#6B7A90}
.chain-box{background:#F8F9FB;border:1px solid #EDF0F4;border-radius:6px;padding:12px 16px;font-size:15px;line-height:1.8;color:#1F2E45}
.qa-box{background:#EEF2F8;border-radius:6px;padding:12px 16px;font-size:15px;line-height:1.7;color:#1F2E45}
.ticks{display:flex;gap:8px;flex-wrap:wrap}
.tick{display:inline-flex;align-items:center;gap:5px;height:28px;padding:0 10px;border-radius:4px;background:#F1F4F8;font-size:13px;font-weight:600;color:#2B3A50}
.watch{border-top:1px solid #EDF0F4;padding-top:14px;display:flex;flex-direction:column;gap:10px}
.watch-t{font-size:13px;font-weight:700;color:#5B6B80}
.watch-row{display:flex;gap:12px;font-size:15px;line-height:1.75;color:#2B3A50}
.watch-row b{flex-shrink:0;width:84px;color:#0B1A30}
.past{display:flex;gap:10px;flex-wrap:wrap}
.past a{padding:8px 14px;border:1px solid #DDE2EA;border-radius:20px;background:#FFFFFF;font-size:13px}
@media (max-width:640px){
  .s-head h1{font-size:26px}
  .sec{padding:20px}
  .part-k{width:auto;font-size:12px}
  .quick{gap:6px}
  .quick a{height:34px;padding:0 12px;font-size:13px}
}
"""

QUICK_DOT = {"positive": "q-pos", "negative": "q-neg", "neutral": "q-neu", "mixed": "q-mix"}


def _ticker_chip(t: dict) -> str:
    change = t.get("change_pct")
    direction = None if not change else ("up" if change > 0 else "down")
    text = "—" if change is None else f"{abs(change):.1f}%"
    return f'<span class="tick num">{esc(t["symbol"])}{c.arrow(direction)}{text}</span>'


def _part(label: str, value: str) -> str:
    return f'<div class="part"><span class="part-k">{label}</span><div class="part-v">{value}</div></div>'


def _sector_card(sector: dict, sources: dict) -> str:
    cls, direction, label = STATUS.get(sector.get("status"), STATUS["neutral"])
    days = f'<span class="sec-days">이 이슈 {sector["days"]}일째</span>' if sector.get("days") else ""
    watch_next = "".join(f"<li>{rich(w)}</li>" for w in sector.get("watch_next", []))
    ticks = "".join(_ticker_chip(t) for t in sector.get("tickers", []))
    parts = [
        _part("촉발 요인", rich(sector.get("trigger", ""))),
        _part("숫자", v.stat_cards(sector.get("numbers", []), sources)),
        _part("파급 경로", v.flow(sector.get("chain", ""))),
        _part("한국 연결", rich(sector.get("korea", ""))),
        _part("관전 포인트", f"<ul>{watch_next}</ul>"),
        _part("면접 각도", f'<div class="qa-box">{rich(sector.get("interview", ""))}</div>'),
    ]
    if ticks:
        parts.insert(2, _part("종목", f'<div class="ticks">{ticks}</div>'))
    watch = ""
    if sector.get("watch"):
        rows = "".join(
            f'<div class="watch-row"><b>{esc(w["company"])}</b><span>{rich(w["text"])} '
            f'<a href="{esc(sources.get(w.get("source"), "#"))}" target="_blank" rel="noopener">[출처]</a></span></div>'
            for w in sector["watch"]
        )
        watch = f'<div class="watch"><span class="watch-t">비상장 AI 기업 동향</span>{rows}</div>'
    return f"""<section class="card sec" id="{esc(sector["key"])}">
<div class="sec-top"><div class="sec-name"><b>{esc(sector["name"])}</b>{days}</div>
<span class="chip {cls}">{c.arrow(direction)}{label}</span></div>
<div class="sec-h">{esc(sector["headline"])}</div>
{"".join(parts)}{watch}
</section>"""


def _quick_menu(sectors: list) -> str:
    links = "".join(
        f'<a href="#{esc(s["key"])}"><i class="{QUICK_DOT.get(s.get("status"), "q-neu")}"></i>{esc(s["name"])}</a>'
        for s in sectors
    )
    return f'<nav class="quick">{links}</nav>'


def _body(site, current: dict, root: str = "") -> str:
    sources = {s["id"]: s["url"] for s in current.get("sources", [])}
    cards = "".join(_sector_card(s, sources) for s in current.get("sectors", []))
    past = "".join(
        f'<a href="{root or "sectors/"}{d["date"]}.html">{ymd_ko(d["date"])}</a>'
        for d in site.sectors[:8] if d["date"] != current["date"]
    )
    past_block = (f'<section class="wrap stack"><h2 class="h2">지난 이슈</h2>'
                  f'<div class="past">{past}</div></section>') if past else ""
    board = v.status_board(current.get("sectors", []))
    return (f'<main class="s-main"><div class="wrap">{board}{cards}</div>{past_block}</main>')


def render_sectors(site, day: dict | None = None) -> str:
    current = day or site.latest_sectors
    if current is None:
        body = f'<main class="wrap s-main">{c.empty_state(c.EMPTY_MESSAGE)}</main>'
        return page(title="섹터 이슈", active="sectors", body=body, css=c.CSS + CSS)
    head = (f'<div class="s-head"><div class="wrap"><div class="s-top">'
            f'<div><span class="eyebrow">섹터 이슈</span>'
            f'<h1 class="serif">오늘 7개 섹터에서 무슨 일이 있었나</h1>'
            f'<span class="muted">촉발 요인부터 한국 연결까지 같은 깊이로 정리합니다 · 평일 아침 갱신</span></div>'
            f'<span class="muted num">{kst_time(current["updated_at"])} KST 기준</span></div>'
            f'{_quick_menu(current.get("sectors", []))}</div></div>')
    return page(title=f"섹터 이슈 {current['date']}", active="sectors",
                body=head + _body(site, current), css=c.CSS + CSS + v.CSS)


def render_sectors_day(site, day: dict) -> str:
    """날짜별 보관본. 하위 폴더에 저장되므로 링크 기준 경로가 다르다."""
    head = (f'<div class="s-head"><div class="wrap"><div class="s-top">'
            f'<div><span class="eyebrow">섹터 이슈 · 보관본</span>'
            f'<h1 class="serif">{ymd_ko(day["date"])}</h1>'
            f'<span class="muted"><a href="../sectors.html">오늘 섹터 이슈 보기</a></span></div>'
            f'<span class="muted num">{kst_time(day["updated_at"])} KST 기준</span></div>'
            f'{_quick_menu(day.get("sectors", []))}</div></div>')
    return page(title=f"섹터 이슈 {day['date']}", active="sectors",
                body=head + _body(site, day, root=""), root="../", css=c.CSS + CSS + v.CSS)

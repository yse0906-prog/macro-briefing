"""홈 페이지(index.html). 디자인: design/Main.dc.html, design/HomeMobile.dc.html"""
from datetime import date

from macro import components as c
from macro import data as d
from macro.fmt import esc, kst_time, md
from macro.layout import page

CSS = """
.home{display:flex;flex-direction:column;gap:56px;padding-top:48px}
.hero{display:flex;gap:48px;align-items:stretch}
.hero-l{flex:1;display:flex;flex-direction:column;gap:22px;padding-top:8px}
.hero h1{font-size:40px;line-height:1.32;font-weight:700;color:#0B1A30;letter-spacing:-0.01em;text-wrap:pretty}
.points{list-style:none;padding:0;display:flex;flex-direction:column;gap:12px}
.points li{display:flex;gap:14px;font-size:16px;line-height:1.65;color:#2B3A50}
.points b{width:24px;flex-shrink:0;color:#1D3A66;font-variant-numeric:tabular-nums}
.ind-card{padding:20px;display:flex;flex-direction:column;gap:14px}
.ind-top{display:flex;justify-content:space-between;gap:8px;font-size:14px;font-weight:600}
.ind-top span{font-size:12px;font-weight:400;color:#6B7A90;white-space:nowrap}
.ind-val{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.big{font-size:36px;font-weight:700;letter-spacing:-0.02em;line-height:1;font-variant-numeric:tabular-nums}
.ind-sub{display:flex;gap:16px;font-size:13px;color:#5B6B80}
.ind-sub b{color:#0F1B2D}
.ind-foot{border-top:1px solid #EDF0F4;padding-top:12px;display:flex;flex-direction:column;gap:8px;align-items:flex-start}
.ind-foot p{font-size:13px;line-height:1.6;color:#44536A}
.duo{display:flex;gap:24px;align-items:flex-start}
.duo>.card{padding:24px 28px 8px}
.duo .h2{padding-bottom:12px}
.sec-list{flex:1}
.imp-list{width:440px;flex-shrink:0}
.row{display:flex;gap:20px;padding:16px 0;border-top:1px solid #EDF0F4;align-items:flex-start}
.row-k{width:112px;flex-shrink:0;display:flex;flex-direction:column;gap:6px;align-items:flex-start;font-size:15px;font-weight:700}
.row-v{flex:1;display:flex;flex-direction:column;gap:6px;font-size:15px;line-height:1.5;color:#2B3A50}
.row-v small{font-size:13px;color:#6B7A90}
.ev{padding:18px;display:flex;flex-direction:column;gap:8px}
.ev span{font-size:13px;color:#5B6B80}
.ev b{font-size:15px}
.ev.key{background:#0B1A30;color:#FFFFFF;border-color:#0B1A30}
.ev.key span{color:#8FA0BA}
.imp{display:flex;gap:3px}
.imp i{width:14px;height:4px;border-radius:2px;background:#DDE2EA}
.imp i.on{background:#1D3A66}
.ev.key .imp i.on{background:#FFFFFF}
@media (max-width:640px){
  .home{gap:36px;padding-top:28px}
  .hero,.duo{flex-direction:column}
  .imp-list{width:100%}
  .hero h1{font-size:26px}
  .big{font-size:28px}
  .row-k{width:92px}
}
"""

LEGEND = (
    '<div class="legend"><span>칩 색상 = 미국 증시에 준 영향</span>'
    '<span><i class="sw" style="background:#1B8F52"></i>호재</span>'
    '<span><i class="sw" style="background:#C9362E"></i>악재</span>'
    '<span><i class="sw" style="background:#8A97AB"></i>중립</span></div>'
)


def _latest_with(site, key):
    return next((b for b in site.briefings if b.get(key)), None)


def _ticker(site) -> str:
    us = d.us_ticker(site.indicators)
    if not us:
        return ""
    as_of = d.obs(site.indicators, "SP500")[-1][0]
    return c.ticker(us, f"{md(as_of)} 종가 · 주간 등락")


def _hero(site, today) -> str:
    b = site.latest
    points = "".join(f"<li><b>{i:02d}</b><span>{esc(s)}</span></li>" for i, s in enumerate(b["summary"], 1))
    return f"""<section class="wrap hero"><div class="hero-l">
<div class="eyebrow">{esc(c.briefing_label(b))}</div>
<h1 class="serif">{esc(b["headline"])}</h1>
<ol class="points">{points}</ol>
<div class="btns"><a class="btn btn-dark" href="briefings/{b["date"]}.html">전체 브리핑 읽기{c.ARROW_RIGHT}</a>
<a class="btn btn-line" href="archive.html">지난 브리핑</a></div>
</div>{c.fomc_card(d.next_meeting(site, today), today)}</section>"""


def _release_card(v: dict, series_id: str) -> str:
    surprise = f'<span class="chip chip-neu">{esc(v["surprise"])}</span>' if v["surprise"] else ""
    return f"""<div class="card ind-card"><div class="ind-top">{c.tip(v["name"], series_id)}<span>{v["date"]} 발표</span></div>
<div class="ind-val"><span class="big">{v["actual"]}</span>{surprise}</div>
<div class="ind-sub num"><span>예상 <b>{v["consensus"]}</b></span><span>이전 <b>{v["previous"]}</b></span></div>
<div class="ind-foot">{c.impact_chip(v["impact"], "증시 ")}<p>{esc(v["interpretation"])}</p></div></div>"""


def _releases(site) -> str:
    b = _latest_with(site, "releases")
    if not b:
        return ""
    recent = sorted(b["releases"], key=lambda r: r["release_date"], reverse=True)[:4]
    cards = "".join(_release_card(c.release_view(site.indicators, r), r["series"]) for r in recent)
    head = c.section_head("이번 발표 지표", f"실제치와 시장 예상치 비교 · {c.briefing_label(b)}", LEGEND)
    return f'<section class="wrap stack">{head}<div class="grid-4">{cards}</div></section>'


def _sectors_and_impact(site) -> str:
    parts = []
    b = _latest_with(site, "sectors")
    if b:
        rows = "".join(
            f'<div class="row"><div class="row-k">{esc(s["name"])}{c.impact_chip(s["impact"])}</div>'
            f'<div class="row-v"><span>{esc(s["title"])}</span>'
            f'<small class="num">{" · ".join(esc(t["symbol"]) for t in s.get("tickers", []))}</small></div></div>'
            for s in b["sectors"]
        )
        link = f'<a href="briefings/{b["date"]}.html">섹터 분석 전체 보기</a>'
        parts.append(f'<div class="card sec-list"><div class="sec-head"><h2 class="h2">이슈 섹터</h2>{link}</div>{rows}</div>')
    m = _latest_with(site, "market_impact")
    if m:
        rows = "".join(
            f'<div class="row"><div class="row-k">{c.ASSET_LABEL[i["asset"]]}</div><div class="row-v">{esc(i["text"])}</div></div>'
            for i in m["market_impact"]
        )
        parts.append(f'<div class="card imp-list"><h2 class="h2">시장 영향</h2>{rows}</div>')
    return f'<section class="wrap duo">{"".join(parts)}</section>' if parts else ""


def _importance(level: int) -> str:
    return "".join('<i class="on"></i>' if n < level else "<i></i>" for n in range(3))


def _events(site, today) -> str:
    events = d.upcoming_events(site.calendar, today)[:5]
    if not events:
        return ""
    cards = "".join(
        f'<div class="card ev{" key" if e["importance"] == 3 else ""}"><span class="num">{kst_time(e["kst"])}</span>'
        f'<b>{esc(e["name"])}</b><span class="imp">{_importance(e["importance"])}</span></div>'
        for e in events
    )
    head = c.section_head("다음 주요 일정", "시간은 한국 기준(KST)")
    return f'<section class="wrap stack">{head}<div class="grid-5">{cards}</div></section>'


def render_home(site, today: date) -> str:
    if site.latest is None:
        main = f'<main class="home"><section class="wrap">{c.empty_state(c.EMPTY_MESSAGE)}</section></main>'
    else:
        sections = [_hero(site, today), _releases(site), _sectors_and_impact(site), _events(site, today)]
        main = f'<main class="home">{"".join(sections)}</main>'
    return page(title="미국 거시경제 · 섹터 이슈 브리핑", active="home", body=_ticker(site) + main, css=c.CSS + c.CHAIN_CSS + CSS)

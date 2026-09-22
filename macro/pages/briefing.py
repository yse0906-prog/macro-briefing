"""브리핑 상세 페이지. 디자인: design/Briefing.dc.html"""
from datetime import date

from macro import components as c
from macro import data as d
from macro.fmt import esc, md, ymd_ko
from macro.fred import SERIES
from macro.layout import page

CSS = """
.b-head{background:#FFFFFF;border-bottom:1px solid #DDE2EA}
.b-head .wrap{padding-top:40px;padding-bottom:44px;display:flex;flex-direction:column;gap:20px}
.crumb{display:flex;gap:8px;font-size:13px;color:#6B7A90}
.b-head h1{font-size:40px;line-height:1.32;font-weight:700;color:#0B1A30;max-width:900px;text-wrap:pretty}
.meta{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:13px;color:#5B6B80}
.summary{background:#EEF2F8;border-radius:6px;padding:22px 26px;display:flex;flex-direction:column;gap:12px;max-width:900px}
.summary>b{font-size:13px;color:#1D3A66}
.points{list-style:none;padding:0;display:flex;flex-direction:column;gap:10px}
.points li{display:flex;gap:14px;font-size:16px;line-height:1.65;color:#1F2E45}
.points b{width:24px;flex-shrink:0;color:#1D3A66;font-variant-numeric:tabular-nums}
.b-body{display:flex;gap:96px;align-items:flex-start;padding-top:56px}
.b-main{flex:1;min-width:0;max-width:792px;display:flex;flex-direction:column;gap:64px}
.b-sec{display:flex;flex-direction:column;gap:18px;scroll-margin-top:24px}
.sec-no{display:block;font-size:13px;font-weight:700;color:#2B5C9E;letter-spacing:0.04em;margin-bottom:6px}
.b-sec h2{font-size:22px;font-weight:700}
.pad{padding:22px}
.bar-l{display:flex;justify-content:space-between;font-size:14px;margin-bottom:6px}
.track{height:10px;background:#E4E8EE;border-radius:3px}
.fill{height:10px;background:#2B5C9E;border-radius:3px}
.list{padding-left:18px;display:flex;flex-direction:column;gap:8px;font-size:14px;line-height:1.6;color:#2B3A50}
.label{font-size:13px;font-weight:600;color:#5B6B80}
.verdict{font-size:20px;font-weight:700;color:#0B1A30}
.big-range{font-size:28px;font-weight:700;color:#0B1A30}
.s-card{padding:22px;display:flex;flex-direction:column;gap:14px}
.s-top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.s-top b{font-size:18px}
.s-top small{font-size:12px;color:#6B7A90;margin-left:8px;font-weight:400}
.s-title{font-size:16px;font-weight:600;line-height:1.5;color:#0B1A30}
.s-text{font-size:14px;line-height:1.7;color:#2B3A50}
.ticks{display:flex;gap:8px;flex-wrap:wrap}
.tick{display:inline-flex;align-items:center;gap:5px;height:28px;padding:0 10px;border-radius:4px;background:#F1F4F8;font-size:13px;font-weight:600;color:#2B3A50}
.news{border-top:1px solid #EDF0F4;padding-top:12px;display:flex;flex-direction:column;gap:10px}
.news a{display:flex;flex-direction:column;gap:2px;font-size:14px;line-height:1.5}
.news small{font-size:12px;color:#6B7A90}
.lines{padding:4px 24px}
.line{display:flex;gap:20px;padding:18px 0;border-bottom:1px solid #EDF0F4;align-items:flex-start}
.line:last-child{border-bottom:0}
.line-k{width:104px;flex-shrink:0;font-size:15px;font-weight:700}
.line .chip{width:56px;justify-content:center;flex-shrink:0}
.line p{font-size:14px;line-height:1.7;color:#2B3A50}
.sc-k{width:220px;flex-shrink:0}
.qa{padding:22px 24px;display:flex;flex-direction:column;gap:10px}
.qa b{font-size:16px;line-height:1.55;color:#0B1A30}
.qa p{font-size:14px;line-height:1.7;color:#2B3A50}
.inst{padding:6px 24px 8px}
.inst-top{display:flex;flex-direction:column;gap:6px;padding:18px 0 14px;border-bottom:2px solid #1D3A66}
.inst-top b{font-size:17px;color:#0B1A30}
.inst-top p{font-size:15px;line-height:1.7;color:#1F2E45}
.inst-row{display:flex;gap:16px;padding:16px 0;border-bottom:1px solid #EDF0F4;align-items:flex-start}
.inst-row:last-child{border-bottom:0}
.inst-k{width:150px;flex-shrink:0;font-size:14px;font-weight:700;color:#2B3A50;padding-top:3px}
.inst-row .chip{width:48px;justify-content:center;flex-shrink:0}
.inst-row p{flex:1;font-size:14px;line-height:1.75;color:#2B3A50}
.cite{font-size:12px;color:#6B7A90}
.fx-chip{width:auto!important;padding:0 10px;white-space:nowrap}
.srcs{list-style:none;padding:0;display:flex;flex-direction:column;gap:8px;font-size:13px;line-height:1.6;color:#5B6B80}
.toc{position:sticky;top:24px;width:312px;flex-shrink:0;display:flex;flex-direction:column;gap:16px}
.toc .card{padding:20px 22px;display:flex;flex-direction:column;gap:2px}
.toc .card a{min-height:34px;display:flex;align-items:center;font-size:14px;color:#44536A}
.mini{padding:20px 22px;display:flex;justify-content:space-between;align-items:center;gap:12px}
.mini span{font-size:12px;color:#8FA0BA}
.mini b{font-size:32px;font-variant-numeric:tabular-nums}
@media (max-width:640px){
  .b-head h1{font-size:26px}
  .b-body{padding-top:32px}
  .b-main{gap:44px}
  .toc{display:none}
  .line{flex-wrap:wrap;gap:8px}
  .sc-k{width:100%}
  .lines{padding:4px 16px}
  .inst{padding:4px 16px 8px}
  .inst-row{flex-wrap:wrap;gap:8px}
  .inst-k{width:auto;flex:1}
  .inst-row p{flex-basis:100%}
}
"""

DIRECTION_LABEL = {"up": "상승", "down": "하락", None: "시사점"}


def _header(b: dict) -> str:
    meta = [c.type_chip(b)]
    if b.get("published_at"):
        meta.append(f'<span class="num">{ymd_ko(b["published_at"])} {b["published_at"][11:16]} KST 발행</span>')
    if b.get("period"):
        meta.append(f'<span class="num">대상 기간 {md(b["period"]["from"])}–{md(b["period"]["to"])}</span>')
    meta.append("<span>AI 작성 · 모든 수치에 출처 표기</span>")
    points = "".join(f"<li><b>{i:02d}</b><span>{esc(s)}</span></li>" for i, s in enumerate(b["summary"], 1))
    return f"""<div class="b-head"><div class="wrap">
<div class="crumb"><a href="../archive.html">브리핑</a><span>/</span><span>{esc(c.briefing_label(b))}</span></div>
<h1 class="serif">{esc(b["headline"])}</h1>
<div class="meta">{"".join(meta)}</div>
<div class="summary"><b>핵심 요약</b><ol class="points">{points}</ol></div>
</div></div>"""


def _releases(site, b: dict) -> str:
    rows = []
    for r in b["releases"]:
        v = c.release_view(site.indicators, r)
        rows.append(
            f'<tr><td><b>{c.tip(v["name"], r["series"])}</b></td><td class="muted">{v["date"]}</td><td class="r"><b>{v["actual"]}</b></td>'
            f'<td class="r">{v["consensus"]}</td><td class="r muted">{v["previous"]}</td><td class="r">{v["diff"]}</td>'
            f'<td>{c.impact_chip(v["impact"])}</td></tr>'
        )
    notes = "".join(f"<li><b>{esc(r['name'])}</b> — {esc(r['interpretation'])}</li>" for r in b["releases"])
    stale = [r["name"] for r in b["releases"] if r["series"] in SERIES and d.is_stale(site.indicators, r["series"])]
    warning = f'<p class="muted">수집 지연: {esc(", ".join(stale))}</p>' if stale else ""
    return (
        '<div class="card tscroll"><table class="t"><thead><tr><th>지표</th><th>발표</th><th class="r">실제</th>'
        '<th class="r">예상</th><th class="r">이전</th><th class="r">차이</th><th>증시 영향</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>{warning}<ul class="list">{notes}</ul>'
    )


def _prob_rows(probabilities: list) -> str:
    return "".join(
        f'<div><div class="bar-l num"><span>{c.OUTCOME_LABEL.get(p["outcome"], p["outcome"])}</span><b>{p["pct"]}%</b></div>'
        f'<div class="track"><div class="fill" style="width:{p["pct"]}%"></div></div></div>'
        for p in probabilities
    )


def _next_meeting(nm: dict) -> str:
    week_ago = nm.get("probabilities_week_ago")
    week_text = ""
    if week_ago:
        joined = " · ".join(f"{c.OUTCOME_LABEL.get(p['outcome'], p['outcome'])} {p['pct']}%" for p in week_ago)
        week_text = f'<span class="muted">1주 전: {joined}</span>'
    rationale = "".join(f"<li>{esc(x)}</li>" for x in nm.get("rationale", []))
    watch = "".join(f"<li>관전 포인트: {esc(x)}</li>" for x in nm.get("watch_points", []))
    verdict = f'{c.OUTCOME_LABEL.get(nm["view"], nm["view"])} · {c.CONFIDENCE_LABEL.get(nm.get("confidence"), "")}'
    return f"""<div class="grid-2">
<div class="card pad stack"><span class="label">시장 반영 확률 · CME FedWatch</span>{_prob_rows(nm["probabilities"])}{week_text}</div>
<div class="card pad stack"><span class="label">브리핑 판단</span><span class="verdict">{esc(verdict)}</span><ul class="list">{rationale}{watch}</ul></div>
</div>"""


def _last_meeting(m: dict) -> str:
    points = "".join(f"<li>{esc(x)}</li>" for x in m.get("statement_points", []))
    press = f'<p class="s-text"><b>기자회견 요지</b> {esc(m["press_conference"])}</p>' if m.get("press_conference") else ""
    vote = m.get("vote", {})
    chip = f'{c.OUTCOME_LABEL.get(m["decision"], m["decision"])} · 찬성 {vote.get("for", "—")} 반대 {vote.get("against", "—")}'
    return f"""<div class="card pad stack">
<div class="s-top"><b>{md(m["date"])} 결정</b><span class="chip chip-neu">{esc(chip)}</span></div>
<span class="big-range num">{c.range_text(*m["range"])}</span>
<span class="label">성명서 톤</span>{c.tone_meter(m["tone"])}
<ul class="list">{points}</ul>{press}
</div>"""


def _ticker_chip(t: dict) -> str:
    change = t.get("change_pct")
    direction = None if not change else ("up" if change > 0 else "down")
    text = "—" if change is None else f"{abs(change):.1f}%"
    return f'<span class="tick num">{esc(t["symbol"])}{c.arrow(direction)}{text}</span>'


def _sectors(b: dict) -> str:
    cards = []
    for s in b["sectors"]:
        news = "".join(
            f'<a href="{esc(n["url"])}" target="_blank" rel="noopener"><span>{esc(n["headline"])}</span>'
            f'<small class="num">{esc(n["outlet"])} · {md(n["date"])}</small></a>'
            for n in s.get("news", [])
        )
        cards.append(f"""<div class="card s-card">
<div class="s-top"><div><b>{esc(s["name"])}</b><small>{esc(s.get("gics", ""))}</small></div>{c.impact_chip(s["impact"])}</div>
<span class="s-title">{esc(s["title"])}</span>
<p class="s-text">{esc(s["analysis"])}</p>
<div class="ticks">{"".join(_ticker_chip(t) for t in s.get("tickers", []))}</div>
<div class="news">{news}</div>
</div>""")
    return f'<div class="grid-2">{"".join(cards)}</div>'


def _impact(b: dict) -> str:
    rows = "".join(
        f'<div class="line"><span class="line-k">{c.ASSET_LABEL[i["asset"]]}</span>'
        f'<span class="chip {"chip-dark" if i["direction"] is None else "chip-neu"}">{DIRECTION_LABEL[i["direction"]]}</span>'
        f'<p>{esc(i["text"])}</p></div>'
        for i in b["market_impact"]
    )
    return f'<div class="card lines">{rows}</div>'


INSTITUTION_LABEL = {
    "securities": "증권사",
    "lp": "LP (보험사·연기금)",
    "gp": "GP (자산운용사)",
}
INSTITUTION_NOTE = {
    "securities": "브로커리지 거래대금 · 트레이딩 손익 · IB · WM",
    "lp": "듀레이션 매칭 · 자산배분 · 환헤지 비용",
    "gp": "펀드 자금 유출입 · 수수료 수익 · 상품 출시",
}


TOPIC_LABEL = {
    "trading": "상품운용 · 채권 평가손익",
    "brokerage": "브로커리지",
    "ib": "IB · 발행시장",
    "wm": "WM · 자금흐름",
    "duration_gap": "듀레이션 갭 (보험사)",
    "kics": "K-ICS 비율 (보험사)",
    "allocation": "운용자산 배분",
    "fx_hedge": "환헤지 · 외화유동성",
    "flows": "펀드 자금 유출입",
    "fees": "AUM · 보수 수익",
    "products": "상품 기회",
    "alternatives": "대체투자 · 딜 환경",
}
POINT_CHIP = {
    "positive": ("chip-pos", "우호"),
    "negative": ("chip-neg", "부담"),
    "neutral": ("chip-neu", "중립"),
    "mixed": ("chip-neu", "혼재"),
}
FX_EFFECT = {
    "krw_weak": "원화 약세 (환율↑)",
    "krw_strong": "원화 강세 (환율↓)",
    "neutral": "중립",
}


def _cite(source, sources: dict) -> str:
    ids = source if isinstance(source, list) else [source]
    return "".join(
        f' <a class="cite" href="{esc(sources[sid])}" target="_blank" rel="noopener">[{sid}]</a>'
        for sid in ids if sid in sources
    )


def _institution_card(item: dict, sources: dict) -> str:
    rows = "".join(
        f'<div class="inst-row"><span class="inst-k">{TOPIC_LABEL.get(p["topic"], esc(p["topic"]))}</span>'
        f'<span class="chip {POINT_CHIP[p["direction"]][0]}">{POINT_CHIP[p["direction"]][1]}</span>'
        f'<p>{esc(p["text"])}{_cite(p.get("source"), sources)}</p></div>'
        for p in item.get("points", [])
    )
    return (f'<div class="card inst"><div class="inst-top">'
            f'<b>{esc(INSTITUTION_LABEL.get(item["institution"], item["institution"]))}</b>'
            f'<p>{esc(item["text"])}</p></div>{rows}</div>')


def _institutions(b: dict) -> str:
    items = b["institution_impact"]
    if not any(i.get("points") for i in items):
        rows = "".join(
            f'<div class="line"><span class="line-k">{esc(INSTITUTION_LABEL.get(i["institution"], i["institution"]))}</span>'
            f'<p>{esc(i["text"])}<br><small class="muted">{esc(INSTITUTION_NOTE.get(i["institution"], ""))}</small></p></div>'
            for i in items
        )
        return f'<div class="card lines">{rows}</div>'
    sources = {s["id"]: s["url"] for s in b.get("sources", [])}
    return '<div class="stack">' + "".join(_institution_card(i, sources) for i in items) + "</div>"


def _fx(b: dict) -> str:
    fx = b["fx"]
    sources = {s["id"]: s["url"] for s in b.get("sources", [])}
    numbers = "".join(f'<li>{esc(n["text"])}{_cite(n.get("source"), sources)}</li>' for n in fx["numbers"])
    drivers = "".join(
        f'<div class="line"><span class="line-k">{esc(d["factor"])}</span>'
        f'<span class="chip fx-chip {"chip-dark" if d["effect"] == "krw_weak" else "chip-neu"}">{FX_EFFECT[d["effect"]]}</span>'
        f'<p>{esc(d["text"])}</p></div>'
        for d in fx["drivers"]
    )
    return f"""<div class="card pad stack"><span class="s-title">{esc(fx["headline"])}</span><ul class="list">{numbers}</ul></div>
<span class="label">원/달러를 움직인 요인</span>
<div class="card lines">{drivers}</div>
<div class="grid-2">
<div class="card pad stack"><span class="label">환헤지 비용</span><p class="s-text">{esc(fx["hedge"])}</p></div>
<div class="card pad stack"><span class="label">수급</span><p class="s-text">{esc(fx["flows"])}</p></div>
</div>
<ul class="list">{"".join(f"<li>관전 포인트: {esc(w)}</li>" for w in fx.get("watch_next", []))}</ul>"""


def _scenarios(b: dict) -> str:
    rows = "".join(
        f'<div class="line"><div class="sc-k"><div class="bar-l num"><b>{esc(s["name"])}</b><b>{s["probability"]}%</b></div>'
        f'<div class="track"><div class="fill" style="width:{s["probability"]}%"></div></div></div><p>{esc(s["text"])}</p></div>'
        for s in b["scenarios"]
    )
    return f'<div class="card lines">{rows}</div>'


def _insights(b: dict) -> str:
    return '<div class="stack">' + "".join(
        f'<div class="card qa"><b>Q. {esc(q["question"])}</b><p>{esc(q["answer_points"])}</p></div>' for q in b["interview_insights"]
    ) + "</div>"


def _sources(b: dict) -> str:
    items = "".join(
        f'<li>[{s["id"]}] <a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a> · 확인 {esc(s.get("accessed", ""))}</li>'
        for s in b["sources"]
    )
    return f'<ol class="srcs num">{items}</ol>'


def _sections(site, b: dict) -> list[tuple[str, str, str]]:
    fomc = b.get("fomc", {})
    sections = []
    if b.get("releases"):
        sections.append(("releases", "지표 발표 결과", _releases(site, b)))
    chain = c.employment_chain(site.indicators, b)
    if chain:
        sections.append(("employment", "고용 상세", chain))
    if fomc.get("last_meeting"):
        sections.append(("last-fomc", "최근 FOMC 결정", _last_meeting(fomc["last_meeting"])))
    if fomc.get("next_meeting"):
        sections.append(("next-fomc", f"FOMC 전망 · {md(fomc['next_meeting']['date'])} 회의", _next_meeting(fomc["next_meeting"])))
    if b.get("sectors"):
        sections.append(("sectors", "이슈 섹터", _sectors(b)))
    sections.append(("impact", "시장 영향", _impact(b)))
    if b.get("fx"):
        sections.append(("fx", "외환 · 원/달러", _fx(b)))
    if b.get("institution_impact"):
        deep = any(i.get("points") for i in b["institution_impact"])
        title = "업권별 시사점 · 운용자산 관점" if deep else "업권별 시사점"
        sections.append(("institutions", title, _institutions(b)))
    if b.get("scenarios"):
        sections.append(("scenarios", "FOMC 이후 1개월 시나리오", _scenarios(b)))
    if b.get("interview_insights"):
        sections.append(("insights", "면접 인사이트", _insights(b)))
    sections.append(("sources", "출처", _sources(b)))
    return sections


def render_briefing(site, b: dict, today: date) -> str:
    sections = _sections(site, b)
    body_sections = "".join(
        f'<section class="b-sec" id="{key}"><div><span class="sec-no">{i:02d}</span><h2>{esc(title)}</h2></div>{content}</section>'
        for i, (key, title, content) in enumerate(sections, 1)
    )
    toc = "".join(f'<a href="#{key}">{esc(title)}</a>' for key, title, _ in sections)
    meeting = d.next_meeting(site, today)
    mini = (f'<div class="dark-card mini"><div><span>다음 FOMC</span><br>{md(meeting["date"])} 회의</div>'
            f'<b data-dday="{meeting["date"]}">{d.dday(meeting["date"], today)}</b></div>') if meeting else ""
    body = (f'{_header(b)}<div class="wrap b-body"><article class="b-main">{body_sections}</article>'
            f'<aside class="toc"><nav class="card">{toc}</nav>{mini}</aside></div>')
    return page(title=b["headline"], active="briefing", body=body, root="../",
                css=c.CSS + c.TONE_CSS + c.CHAIN_CSS + CSS)


def render_briefing_empty() -> str:
    body = f'<main class="wrap" style="padding-top:48px">{c.empty_state(c.EMPTY_MESSAGE)}</main>'
    return page(title="주간 브리핑", active="briefing", body=body, root="../", css=c.CSS)

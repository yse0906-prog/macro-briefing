"""FOMC 페이지(fomc.html). 디자인: design/Fomc.dc.html"""
from datetime import date

from macro import charts
from macro import components as c
from macro import data as d
from macro.fmt import esc, md
from macro.layout import page

CSS = """
.f-head{background:#FFFFFF;border-bottom:1px solid #DDE2EA}
.f-head .wrap{padding-top:40px;padding-bottom:40px;display:flex;justify-content:space-between;align-items:flex-end;gap:32px;flex-wrap:wrap}
.f-head h1{font-size:36px;line-height:1.3;color:#0B1A30;margin:12px 0}
.f-rate{display:flex;flex-direction:column;align-items:flex-end;gap:6px;font-size:13px;color:#5B6B80}
.f-rate b{font-size:56px;line-height:1;letter-spacing:-0.02em;color:#0B1A30;font-variant-numeric:tabular-nums}
.f-main{display:flex;flex-direction:column;gap:24px;padding-top:40px}
.f-main .fomc-card{width:auto}
.f-card{padding:28px;display:flex;flex-direction:column;gap:14px}
.f-card p{font-size:14px;line-height:1.65;color:#2B3A50}
.f-card .list{padding-left:18px;display:flex;flex-direction:column;gap:6px;font-size:14px;line-height:1.65;color:#2B3A50}
.label{font-size:13px;font-weight:600;color:#5B6B80}
.chart-card{padding:24px 28px 20px;display:flex;flex-direction:column;gap:16px}
.hist .sec-head{padding:22px 28px 16px}
@media (max-width:640px){.f-head h1{font-size:26px}.f-rate{align-items:flex-start}.f-rate b{font-size:40px}.f-card,.chart-card{padding:20px}}
"""


def _hero(site) -> str:
    rng = d.current_range(site.indicators)
    history = d.fomc_history(site)
    holds = 0
    for meeting in history:
        if meeting["decision"] != "hold":
            break
        holds += 1
    if holds:
        note = f"최근 {holds}회 연속 동결"
    elif history:
        note = f"{md(history[0]['date'])} {c.OUTCOME_LABEL[history[0]['decision']]}"
    else:
        note = "출처: FRED DFEDTARL · DFEDTARU"
    rate = c.range_text(*rng) if rng else "—"
    return f"""<div class="f-head"><div class="wrap">
<div><span class="eyebrow">FOMC · 연방공개시장위원회</span><h1 class="serif">기준금리 결정과 다음 회의 전망</h1>
<span class="muted">연 8회 정례회의 · 결정은 미 동부 오후 2시(한국 시간 다음 날 03:00, 서머타임 해제 시 04:00)</span></div>
<div class="f-rate"><span>현재 연방기금금리 목표 범위</span><b>{rate}</b><span>{esc(note)}</span></div>
</div></div>"""


def _last_card(history: list) -> str:
    if not history:
        return '<div class="card f-card"><h2 class="h2">최근 결정</h2><p class="muted">최근 결정은 브리핑이 발행되면 표시됩니다.</p></div>'
    m = history[0]
    vote = m.get("vote", {})
    chip = f'{c.OUTCOME_LABEL[m["decision"]]} · 찬성 {vote.get("for", "—")} 반대 {vote.get("against", "—")}'
    points = "".join(f"<li>{esc(x)}</li>" for x in m.get("statement_points", []))
    press = f'<span class="label">기자회견 요지</span><p>{esc(m["press_conference"])}</p>' if m.get("press_conference") else ""
    return f"""<div class="card f-card">
<div class="sec-head"><h2 class="h2">최근 결정 · {md(m["date"])}</h2><span class="chip chip-neu">{esc(chip)}</span></div>
<span class="label">성명서 톤</span>{c.tone_meter(m["tone"])}
<span class="label">성명서 핵심</span><ul class="list">{points}</ul>{press}
</div>"""


def _rate_chart(site) -> str:
    months = d.monthly_last(d.obs(site.indicators, "DFEDTARU"), 33)
    if len(months) < 2:
        return ""
    values = [v for _, v in months]
    lo, hi, ticks = charts.nice_range([min(values) - 0.25, max(values) + 0.25], 1.0)
    n = len(months)
    labels = [(i, k.replace("-", ".")) for i, (k, _) in enumerate(months)
              if i in (0, n - 1) or (k.endswith("-01") and 2 < i < n - 3)]
    series = charts.Series("상단", charts.SERIES_COLORS[0], [(k.replace("-", "."), v) for k, v in months], f"{values[-1]:.2f}%")
    svg = charts.line_chart([series], y_min=lo, y_max=hi, y_ticks=ticks, x_labels=labels, step=True,
                            tick_fmt=lambda t: f"{t:.2f}%", value_fmt=lambda v: f"{v:.2f}%",
                            label="연방기금금리 목표 상단 월말 추이")
    head = c.section_head("연방기금금리 목표 상단 추이", f"최근 {n}개월 · 월말 기준", '<span class="muted">출처: FRED DFEDTARU</span>')
    return f'<section class="wrap"><div class="card chart-card">{head}{svg}</div></section>'


def _day_change(points, day: str):
    for i, (obs_day, value) in enumerate(points):
        if obs_day == day and i > 0:
            return round((value / points[i - 1][1] - 1) * 100, 1)
    return None


def _history(site) -> str:
    history = d.fomc_history(site)
    head = c.section_head("결정 이력", "브리핑에 기록된 회의만 표시")
    if not history:
        return f'<section class="wrap"><div class="card hist">{head}<p class="empty">결정 이력은 브리핑이 쌓이면 표시됩니다.</p></div></section>'
    sp500 = d.obs(site.indicators, "SP500")
    rows = []
    for m in history:
        change = _day_change(sp500, m["date"])
        direction = None if not change else ("up" if change > 0 else "down")
        change_html = "—" if change is None else f"{c.arrow(direction)} {abs(change):.1f}%"
        vote = m.get("vote", {})
        chip_class = "chip-neu" if m["decision"] == "hold" else "chip-dark"
        rows.append(
            f'<tr><td><b>{m["date"].replace("-", ".")}</b></td>'
            f'<td><span class="chip {chip_class}">{c.OUTCOME_LABEL[m["decision"]]}</span></td>'
            f'<td>{c.range_text(*m["range"])}</td><td>{vote.get("for", "—")}–{vote.get("against", "—")}</td>'
            f'<td>{c.tone_label(m["tone"])}</td><td class="r">{change_html}</td></tr>'
        )
    table = ('<div class="tscroll"><table class="t"><thead><tr><th>회의</th><th>결정</th><th>목표 범위</th>'
             '<th>투표 (찬성–반대)</th><th>성명서 톤</th><th class="r">S&amp;P 500 당일</th></tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table></div>')
    return f'<section class="wrap"><div class="card hist">{head}{table}</div></section>'


def render_fomc(site, today: date) -> str:
    grid = f'<section class="wrap grid-2">{c.fomc_card(d.next_meeting(site, today), today)}{_last_card(d.fomc_history(site))}</section>'
    body = _hero(site) + f'<main class="f-main">{grid}{_rate_chart(site)}{_history(site)}</main>'
    return page(title="FOMC", active="fomc", description="미국 FOMC 금리 결정 이력, 성명서 톤, 다음 회의 D-day와 CME FedWatch 확률을 한 화면에 정리합니다.", body=body, css=c.CSS + c.TONE_CSS + CSS)

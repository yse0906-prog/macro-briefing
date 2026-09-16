"""거시지표 페이지(indicators.html). 디자인: design/Indicators.dc.html"""
from macro import charts
from macro import components as c
from macro import data as d
from macro.fmt import esc, kst_time, md, num
from macro.fred import SERIES
from macro.layout import page

NO_DATA = "지표를 아직 수집하지 않았습니다. 첫 수집 후 표시됩니다."

CSS = """
.i-head{background:#FFFFFF;border-bottom:1px solid #DDE2EA}
.i-head .wrap{padding-top:40px;padding-bottom:28px;display:flex;flex-direction:column;gap:22px}
.i-top{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}
.i-head h1{font-size:36px;line-height:1.3;color:#0B1A30;margin-top:12px}
.tabs{display:flex;gap:8px;flex-wrap:wrap}
.tab{display:inline-flex;align-items:center;height:40px;padding:0 18px;border-radius:20px;font-size:14px;font-weight:600;background:#FFFFFF;border:1px solid #DDE2EA;color:#2B3A50}
.tab:hover{border-color:#1D3A66;text-decoration:none}
.i-main{display:flex;flex-direction:column;gap:64px;padding-top:48px}
.i-sec{display:flex;flex-direction:column;gap:16px;scroll-margin-top:24px}
.i-sec>div>h2{font-size:24px;font-weight:700}
.chart-card{padding:24px 28px 20px;display:flex;flex-direction:column;gap:16px}
.key{display:inline-block;width:16px;height:2px;margin-right:8px;vertical-align:middle}
.tile{padding:20px;display:flex;flex-direction:column;gap:10px}
.tile-l{font-size:14px;font-weight:600}
.tile-v{display:flex;align-items:baseline;justify-content:space-between;gap:8px}
.tile-v b{font-size:30px;letter-spacing:-0.01em}
.tile-v span{display:flex;align-items:center;gap:5px;font-size:13px;font-weight:600;color:#2B3A50}
@media (max-width:640px){.i-head h1{font-size:26px}.chart-card{padding:20px}.i-main{gap:44px}}
"""

GROUPS = [
    ("prices", "물가", "연준 목표 2%와의 거리가 금리 방향을 정합니다.", ["CPIAUCSL", "CPILFESL", "PPIFIS", "PCEPILFE"]),
    ("jobs", "고용", "연준의 또 다른 목표인 최대 고용의 상태를 봅니다.",
     ["PAYEMS", "UNRATE", "CIVPART", "CES0500000003", "ICSA"]),
    ("growth", "성장·경기", "경기 확장과 둔화의 흐름을 봅니다.", ["A191RL1Q225SBEA", "ISM_MFG", "ISM_SVC", "RSAFS"]),
]
WEB_SERIES = {"ISM_MFG": "ISM 제조업 PMI", "ISM_SVC": "ISM 서비스업 PMI"}
MARKET_TILES = [
    ("DGS10", "미 국채 10년물", "bp"),
    ("DTWEXBGS", "달러인덱스 (광의)", "pct"),
    ("VIXCLS", "VIX 변동성지수", "pt"),
    ("DEXKOUS", "원/달러 환율", "pct"),
]


def _period_label(series_id: str, day: str) -> str:
    month = int(day[5:7])
    if series_id == "A191RL1Q225SBEA":
        return f"{(month - 1) // 3 + 1}분기"
    if series_id == "ICSA":
        return f"{md(day)} 주"
    return f"{month}월"


def _month(day: str) -> str:
    return day[:7].replace("-", ".")


def _x_labels(days: list) -> list:
    n = len(days)
    return [(i, _month(day)) for i, day in enumerate(days) if i in (0, n - 1) or (day[5:7] == "01" and 2 < i < n - 3)]


def _row(site, sid: str) -> str:
    _, release = d.latest_release(site, sid)
    if sid in WEB_SERIES:
        if not release:
            return ""
        unit, name = c.unit_of(release), WEB_SERIES[sid]
        period = _period_label(sid, release["period"])
        actual, previous, consensus = release.get("actual"), release.get("previous"), release.get("consensus")
        spark, stale = "—", ""
    else:
        points = d.obs(site.indicators, sid)
        if not points:
            return ""
        unit, name = SERIES[sid]["unit"], SERIES[sid]["name"]
        period = _period_label(sid, points[-1][0])
        actual = points[-1][1]
        previous = points[-2][1] if len(points) > 1 else None
        release = release if release and release["period"] == points[-1][0] else None
        consensus = release.get("consensus") if release else None
        spark = charts.sparkline([v for _, v in points[-12:]], label=f"{name} 최근 12회")
        stale = ' <span class="chip chip-neu">수집 지연</span>' if d.is_stale(site.indicators, sid) else ""
    released = md(release["release_date"]) if release else "—"
    return (f'<tr><td><b>{esc(name)}</b>{stale}</td><td class="muted">{period} · {released}</td>'
            f'<td class="r"><b>{c.fmt_value(actual, unit)}</b></td><td class="r">{c.fmt_value(consensus, unit)}</td>'
            f'<td class="r muted">{c.fmt_value(previous, unit)}</td><td>{spark}</td></tr>')


def _table(site, ids: list) -> str:
    rows = "".join(_row(site, sid) for sid in ids)
    return ('<div class="card tscroll"><table class="t"><thead><tr><th>지표</th><th>기준 · 발표일</th>'
            '<th class="r">실제</th><th class="r">예상</th><th class="r">이전</th><th>추이</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def _prices_chart(site) -> str:
    cpi = dict(d.obs(site.indicators, "CPIAUCSL"))
    core = dict(d.obs(site.indicators, "CPILFESL"))
    days = sorted(set(cpi) & set(core))[-24:]
    if len(days) < 2:
        return ""
    lo, hi, ticks = charts.nice_range([cpi[x] for x in days] + [core[x] for x in days] + [2.0], 0.4)
    core_above = core[days[-1]] >= cpi[days[-1]]
    series = [
        charts.Series("근원 CPI", charts.SERIES_COLORS[1], [(_month(x), core[x]) for x in days],
                      f"{core[days[-1]]:.1f}%", dy=-4 if core_above else 6),
        charts.Series("CPI", charts.SERIES_COLORS[0], [(_month(x), cpi[x]) for x in days],
                      f"{cpi[days[-1]]:.1f}%", dy=6 if core_above else -4),
    ]
    svg = charts.line_chart(series, y_min=lo, y_max=hi, y_ticks=ticks, x_labels=_x_labels(days),
                            ref=(2.0, "연준 목표 2%"), label="CPI와 근원 CPI 전년 대비 상승률")
    legend = (f'<div class="legend"><span><i class="key" style="background:{charts.SERIES_COLORS[0]}"></i>CPI</span>'
              f'<span><i class="key" style="background:{charts.SERIES_COLORS[1]}"></i>근원 CPI (식품·에너지 제외)</span></div>')
    head = c.section_head("CPI · 근원 CPI 전년 대비 상승률", f"최근 {len(days)}개월 · 월간", legend)
    return f'<div class="card chart-card">{head}{svg}</div>'


def _jobs_chart(site) -> str:
    points = d.obs(site.indicators, "UNRATE")[-24:]
    if len(points) < 2:
        return ""
    lo, hi, ticks = charts.nice_range([v for _, v in points], 0.2)
    series = charts.Series("", charts.SERIES_COLORS[0], [(_month(x), v) for x, v in points], f"{points[-1][1]:.1f}%")
    svg = charts.line_chart([series], y_min=lo, y_max=hi, y_ticks=ticks, x_labels=_x_labels([x for x, _ in points]),
                            height=280, label="실업률 추이")
    return f'<div class="card chart-card">{c.section_head("실업률", f"최근 {len(points)}개월 · 월간")}{svg}</div>'


def _tile(site, sid: str, label: str, kind: str) -> str:
    points = d.obs(site.indicators, sid)
    result = d.weekly_change(points, kind)
    if not result:
        return ""
    value, change = result
    if sid == "DGS10":
        value_text = f"{value:.2f}%"
    elif sid == "DEXKOUS":
        value_text = num(value, 0)
    else:
        value_text = num(value, 1)
    direction = None if not change else ("up" if change > 0 else "down")
    change_text = {"bp": f"{abs(change):.0f}bp", "pct": f"{abs(change):.1f}%"}.get(kind, f"{abs(change):.1f}")
    spark = charts.sparkline([v for _, v in d.weekly_last(points, 12)], width=248, height=48, label=f"{label} 최근 12주")
    return (f'<div class="card tile num"><span class="tile-l">{esc(label)}</span>'
            f'<div class="tile-v"><b>{value_text}</b><span>{c.arrow(direction)}{change_text}</span></div>{spark}</div>')


def _section(key: str, title: str, desc: str, inner: str) -> str:
    return (f'<section class="wrap i-sec" id="{key}"><div><h2>{esc(title)}</h2><span class="sub">{esc(desc)}</span></div>'
            f'{inner}</section>')


def render_indicators(site) -> str:
    fetched = site.indicators.get("fetched_at")
    note = f"FRED 자동 수집 · 마지막 수집 {kst_time(fetched)} KST" if fetched else "FRED 자동 수집 · 아직 수집 전"
    tabs = "".join(f'<a class="tab" href="#{key}">{title}</a>'
                   for key, title in (("prices", "물가"), ("jobs", "고용"), ("growth", "성장·경기"), ("markets", "시장")))
    head = (f'<div class="i-head"><div class="wrap"><div class="i-top"><div><span class="eyebrow">거시경제 지표</span>'
            f'<h1 class="serif">미국 경제를 읽는 4개 지표 묶음</h1></div><span class="muted num">{note}</span></div>'
            f'<nav class="tabs">{tabs}</nav></div></div>')
    if not site.indicators.get("series"):
        main = f'<main class="i-main"><section class="wrap">{c.empty_state(NO_DATA)}</section></main>'
    else:
        prices, jobs, growth = GROUPS
        tiles = "".join(_tile(site, *t) for t in MARKET_TILES)
        web_note = '<p class="muted">ISM 지수는 FRED에서 제공하지 않아 브리핑의 웹 수집값과 출처를 사용합니다.</p>'
        sections = [
            _section(*prices[:3], _prices_chart(site) + _table(site, prices[3])),
            _section(*jobs[:3], _jobs_chart(site)
                     + c.employment_chain(site.indicators, next((b for b in site.briefings if b.get("releases")), None))
                     + _table(site, jobs[3])),
            _section(*growth[:3], web_note + _table(site, growth[3])),
            _section("markets", "시장", "지표 발표에 시장이 어떻게 반응했는지 봅니다. 전주 대비 · 최근 12주.",
                     f'<div class="grid-4">{tiles}</div>'),
        ]
        main = f'<main class="i-main">{"".join(sections)}</main>'
    return page(title="거시지표", active="indicators", body=head + main, css=c.CSS + c.CHAIN_CSS + CSS)

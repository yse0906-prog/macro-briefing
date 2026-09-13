"""여러 페이지가 함께 쓰는 HTML 조각과 표시 규칙."""
from datetime import date

from macro import data as d
from macro.fmt import esc, kst_time, man, md, num, signed, ymd_ko
from macro.fred import SERIES

EMPTY_MESSAGE = "첫 브리핑을 준비하고 있습니다. 매주 토요일 오전 7시에 발행됩니다."
OUTCOME_LABEL = {"hold": "동결", "cut25": "25bp 인하", "cut50": "50bp 인하", "hike25": "25bp 인상", "hike50": "50bp 인상"}
ASSET_LABEL = {"us_equities": "미국 주식", "us_rates": "미 국채금리", "usd": "달러", "krw": "원/달러", "korea_banks": "한국 은행권"}
IMPACT = {"positive": ("chip-pos", "up", "호재"), "negative": ("chip-neg", "down", "악재"),
          "neutral": ("chip-neu", None, "중립"), "mixed": ("chip-neu", None, "혼조")}
PROB_SHADES = ("#E8EEF7", "#5C7AA8", "#34507D", "#8FA9D6")

ARROW_RIGHT = ('<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" '
               'stroke="currentColor" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"></path></svg>')

CSS = """
.sub{display:block;margin-top:4px;font-size:13px;color:#6B7A90}
.stack{display:flex;flex-direction:column;gap:16px}
.legend{display:flex;gap:16px;flex-wrap:wrap;align-items:center;font-size:12px;color:#44536A}
.sw{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:6px}
.btns{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;height:44px;padding:0 20px;border-radius:4px;font-size:14px;font-weight:600}
.btn:hover{text-decoration:none}
.btn-dark{background:#0B1A30;color:#FFFFFF}.btn-dark:hover{color:#FFFFFF}
.btn-line{background:#FFFFFF;border:1px solid #C5CEDB;color:#1D3A66}
.ticker{background:#13284A;border-top:1px solid #1F3558;font-size:13px}
.tk-row{display:flex;align-items:center;gap:24px;height:44px;overflow-x:auto;white-space:nowrap}
.tk-sep{border-top:1px solid #1F3558}
.tk-g{width:28px;flex-shrink:0;font-size:12px;font-weight:600;color:#6F82A0}
.tk{display:flex;align-items:center;gap:8px}
.tk-l{color:#8FA0BA}.tk-v{color:#FFFFFF;font-weight:600}
.tk-c{display:flex;align-items:center;gap:4px;color:#D5DDEA}
.tk-note{margin-left:auto;padding-left:24px;color:#8FA0BA}
.fomc-card{width:384px;flex-shrink:0;padding:28px;display:flex;flex-direction:column;gap:20px}
.fc-top{display:flex;justify-content:space-between;align-items:baseline;font-size:13px;color:#B7C3D6}
.fc-top b{color:#8FA0BA;letter-spacing:0.04em}
.fc-mid{display:flex;align-items:flex-end;justify-content:space-between;gap:12px}
.dday{font-size:64px;font-weight:700;line-height:1;letter-spacing:-0.02em;font-variant-numeric:tabular-nums}
.fc-when{text-align:right;font-size:13px;line-height:1.55;color:#B7C3D6}
.fc-when b{color:#FFFFFF}
.prob{border-top:1px solid #22375A;padding-top:18px;display:flex;flex-direction:column;gap:10px;font-size:13px;color:#B7C3D6}
.pbar{display:flex;gap:2px;height:12px}
.pbar span{border-radius:2px}
.plegend{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;font-size:14px;color:#D5DDEA}
.plegend b{color:#FFFFFF}
.view{background:#13284A;border-radius:4px;padding:14px 16px;display:flex;flex-direction:column;gap:6px;font-size:13px;line-height:1.6;color:#B7C3D6}
.view small{font-size:12px;color:#8FA0BA}
.view b{font-size:15px;color:#FFFFFF}
@media (max-width:640px){.fomc-card{width:100%;padding:22px}.dday{font-size:52px}}
"""


def arrow(direction, dark=False) -> str:
    if direction not in ("up", "down"):
        return ('<svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true">'
                '<rect class="flat" x="1" y="4" width="8" height="2" rx="1"></rect></svg>')
    shape = "M5 1.5L9 8.5H1z" if direction == "up" else "M5 8.5L1 1.5h8z"
    cls = ("d-" if dark else "") + direction
    return f'<svg width="10" height="10" viewBox="0 0 10 10" aria-hidden="true"><path class="{cls}" d="{shape}"></path></svg>'


def impact_chip(impact: str, prefix: str = "") -> str:
    cls, direction, label = IMPACT[impact]
    return f'<span class="chip {cls}">{arrow(direction)}{prefix}{label}</span>'


def type_chip(briefing: dict) -> str:
    return '<span class="chip chip-dark">주간</span>' if briefing["type"] == "weekly" else '<span class="chip chip-neu">이벤트</span>'


def unit_of(release: dict) -> str:
    return SERIES.get(release["series"], {}).get("unit") or release.get("unit", "pt")


def fmt_value(value, unit: str) -> str:
    if value is None:
        return "—"
    if unit in ("명", "건"):
        return man(value)
    return num(value, 1) + ("%" if unit == "%" else "")


def fmt_diff(diff, unit: str) -> str:
    if unit in ("명", "건"):
        return signed(diff / 10000, 1, "만")
    return signed(diff, 1, "%p" if unit == "%" else "")


def surprise_label(diff, unit: str) -> str:
    if diff is None:
        return ""
    if abs(diff) < 1e-9:
        return "예상 부합"
    return f"예상 {'상회' if diff > 0 else '하회'} {fmt_diff(diff, unit)}"


def release_view(indicators: dict, release: dict) -> dict:
    unit = unit_of(release)
    values = d.release_values(indicators, release)
    actual, consensus = values["actual"], release.get("consensus")
    diff = None if actual is None or consensus is None else round(actual - consensus, 6)
    return {
        "name": release["name"], "date": md(release["release_date"]),
        "actual": fmt_value(actual, unit), "consensus": fmt_value(consensus, unit),
        "previous": fmt_value(values["previous"], unit),
        "diff": "—" if diff is None else fmt_diff(diff, unit), "surprise": surprise_label(diff, unit),
        "impact": release["impact"], "interpretation": release.get("interpretation", ""),
    }


def briefing_label(briefing: dict) -> str:
    if briefing["type"] == "weekly" and briefing.get("period"):
        return f"주간 브리핑 · {md(briefing['period']['from'])}–{md(briefing['period']['to'])}"
    return f"이벤트 브리핑 · {ymd_ko(briefing['date'])}"


def _ticker_item(item: dict) -> str:
    change = item.get("change")
    direction = None if not change else ("up" if change > 0 else "down")
    if change is None:
        change_text = "—"
    elif item["unit"] == "bp":
        change_text = f"{abs(change):.0f}bp"
    elif item["unit"] == "pt":
        change_text = f"{abs(change):.1f}"
    else:
        change_text = f"{abs(change):.1f}%"
    value = num(item["value"], 2) + "%" if item["id"] == "us10y" else num(item["value"], 1)
    return (f'<div class="tk"><span class="tk-l">{esc(item["label"])}</span><span class="tk-v">{value}</span>'
            f'<span class="tk-c">{arrow(direction, dark=True)}{change_text}</span></div>')


def ticker(us_rows: list, kr_rows: list, note: str) -> str:
    rows = []
    if us_rows:
        items = "".join(_ticker_item(i) for i in us_rows)
        rows.append(f'<div class="wrap tk-row"><span class="tk-g">미국</span>{items}<span class="tk-note hide-m">{esc(note)}</span></div>')
    if kr_rows:
        items = "".join(_ticker_item(i) for i in kr_rows)
        rows.append(f'<div class="tk-sep"><div class="wrap tk-row"><span class="tk-g">한국</span>{items}</div></div>')
    return f'<div class="ticker num">{"".join(rows)}</div>' if rows else ""


def prob_bar(probabilities: list) -> str:
    shown = [p for p in probabilities if p["pct"] > 0]
    bars = "".join(f'<span style="flex:{p["pct"]};background:{PROB_SHADES[i % 4]}"></span>' for i, p in enumerate(shown))
    legend = "".join(
        f'<span><i class="sw" style="background:{PROB_SHADES[i % 4]}"></i>{OUTCOME_LABEL.get(p["outcome"], p["outcome"])} <b>{p["pct"]}%</b></span>'
        for i, p in enumerate(shown)
    )
    return f'<div class="pbar">{bars}</div><div class="plegend num">{legend}</div>'


def fomc_card(meeting, today: date) -> str:
    if not meeting:
        return ('<div class="dark-card fomc-card"><div class="fc-top"><b>다음 FOMC</b></div>'
                '<p class="view">다음 회의 정보는 브리핑이 발행되면 표시됩니다.</p></div>')
    watch = "".join(f"<span>{esc(w)}</span>" for w in meeting.get("watch_points", [])[:1])
    return f"""<div class="dark-card fomc-card">
<div class="fc-top"><b>다음 FOMC</b><span>{md(meeting["date"])} 회의</span></div>
<div class="fc-mid"><span class="dday" data-dday="{meeting["date"]}">{d.dday(meeting["date"], today)}</span>
<span class="fc-when">결과 발표<br><b>{kst_time(meeting["announce_kst"])} KST</b></span></div>
<div class="prob"><span>시장 반영 확률 · CME FedWatch</span>{prob_bar(meeting["probabilities"])}</div>
<div class="view"><small>브리핑 전망</small><b>{OUTCOME_LABEL.get(meeting["view"], meeting["view"])}</b>{watch}</div>
</div>"""


def section_head(title: str, sub: str = "", right: str = "") -> str:
    sub_html = f'<span class="sub">{esc(sub)}</span>' if sub else ""
    return f'<div class="sec-head"><div><h2 class="h2">{esc(title)}</h2>{sub_html}</div>{right}</div>'


def empty_state(message: str) -> str:
    return f'<div class="card empty">{esc(message)}</div>'

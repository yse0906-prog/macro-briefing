"""여러 페이지가 함께 쓰는 HTML 조각과 표시 규칙."""
from datetime import date

from macro import data as d
from macro.fmt import esc, kst_time, man, md, num, signed, ymd_ko
from macro.fred import SERIES
from macro.help import tip as help_text

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


def ticker(us_rows: list, note: str) -> str:
    if not us_rows:
        return ""
    items = "".join(_ticker_item(i) for i in us_rows)
    return (f'<div class="ticker num"><div class="wrap tk-row"><span class="tk-g">미국</span>{items}'
            f'<span class="tk-note hide-m">{esc(note)}</span></div></div>')


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


CONFIDENCE_LABEL = {"high": "확신도 높음", "medium": "확신도 보통", "low": "확신도 낮음"}

TONE_CSS = """
.tone{position:relative;height:10px;background:#E4E8EE;border-radius:5px;margin:8px 0}
.tone::after{content:"";position:absolute;left:50%;top:-3px;width:1px;height:16px;background:#B4BECC}
.tone i{position:absolute;top:-5px;width:20px;height:20px;margin-left:-10px;border-radius:10px;background:#0B1A30;border:3px solid #FFFFFF;box-shadow:0 0 0 1px #0B1A30;z-index:1}
.tone-l{display:flex;justify-content:space-between;font-size:12px;color:#6B7A90}
.tone-t{display:block;margin-top:8px;font-size:14px;color:#0B1A30}
"""


def range_text(lower: float, upper: float) -> str:
    return f"{num(lower, 2)}–{num(upper, 2)}%"


def tone_label(tone: float) -> str:
    if tone < 0.35:
        return "비둘기파"
    if tone < 0.47:
        return "중립~비둘기"
    if tone <= 0.53:
        return "중립"
    if tone <= 0.66:
        return "중립~매파"
    return "매파"


CHAIN_CSS = """
.tip{border-bottom:1px dotted #9AA8BC;cursor:help}
.chain{display:flex;flex-direction:column}
.chain-row{display:flex;gap:16px;padding:14px 0;border-top:1px solid #EDF0F4;align-items:baseline;flex-wrap:wrap}
.chain-row:first-child{border-top:0}
.chain-k{width:132px;flex-shrink:0;font-size:14px;font-weight:700;color:#0B1A30}
.chain-v{width:132px;flex-shrink:0;font-size:18px;font-weight:700;font-variant-numeric:tabular-nums}
.chain-n{flex:1;min-width:220px;font-size:14px;line-height:1.6;color:#2B3A50}
.chain-sub{display:flex;gap:8px;flex-wrap:wrap;font-size:13px;font-variant-numeric:tabular-nums}
.chain-sub span{background:#F1F4F8;border-radius:4px;padding:4px 10px}
@media (max-width:640px){.chain-k,.chain-v{width:auto}}
"""

INDUSTRIES = ["USLAH", "USEHS", "USCONS", "MANEMP", "USPBS", "USTRADE"]


def tip(label: str, series_id: str) -> str:
    """지표 이름에 설명 툴팁을 붙인다. 설명이 없으면 이름만 돌려준다."""
    text = help_text(series_id)
    if not text:
        return esc(label)
    return f'<span class="tip" title="{esc(text)}">{esc(label)}</span>'


def _chain_row(label: str, series_id: str, value: str, note: str) -> str:
    return (f'<div class="chain-row"><span class="chain-k">{tip(label, series_id)}</span>'
            f'<span class="chain-v">{value}</span><span class="chain-n">{note}</span></div>')


def employment_chain(indicators: dict, briefing: dict | None = None) -> str:
    """NFP → 실업률 → 참가율 → 임금 → 업종별 → 이전치 수정 순서로 고용을 읽는 블록."""
    def last(series_id):
        points = d.obs(indicators, series_id)
        return points[-1] if points else None

    def prev(series_id):
        points = d.obs(indicators, series_id)
        return points[-2] if len(points) > 1 else None

    payrolls = last("PAYEMS")
    if not payrolls:
        return ""

    consensus = None
    for release in (briefing or {}).get("releases", []):
        if release.get("series") == "PAYEMS":
            consensus = release.get("consensus")

    rows = []
    note = "예상치를 찾지 못했습니다." if consensus is None else (
        f"시장 예상 {man(consensus)}과 비교해 {'많이 ' if payrolls[1] > consensus else ''}"
        f"{'늘었습니다' if payrolls[1] > consensus else '적게 늘었습니다'}.")
    rows.append(_chain_row("비농업 고용", "PAYEMS", man(payrolls[1]), note))

    unemployment, before = last("UNRATE"), prev("UNRATE")
    if unemployment:
        moved = "같은 수준" if not before or before[1] == unemployment[1] else (
            "상승" if unemployment[1] > before[1] else "하락")
        rows.append(_chain_row("실업률", "UNRATE", f"{num(unemployment[1], 1)}%",
                               f"직전 달 {num(before[1], 1) if before else '—'}% 대비 {moved}입니다."))

    participation, before = last("CIVPART"), prev("CIVPART")
    if participation:
        gap = None if not before else round(participation[1] - before[1], 2)
        note = "직전 달과 같습니다." if not gap else (
            f"직전 달보다 {signed(gap, 1, '%p')} 움직였습니다. "
            + ("참가율이 오르며 실업률이 유지되면 실제로 사람이 노동시장에 들어온 것입니다."
               if gap > 0 else "참가율이 내리면 실업률이 낮아져도 구직 포기일 수 있습니다."))
        rows.append(_chain_row("경제활동참가율", "CIVPART", f"{num(participation[1], 1)}%", note))

    wage, before = last("CES0500000003"), prev("CES0500000003")
    year_ago = None
    points = d.obs(indicators, "CES0500000003")
    if len(points) >= 13:
        year_ago = points[-13][1]
    if wage:
        parts = []
        if before:
            parts.append(f"전월 대비 {signed(round((wage[1] / before[1] - 1) * 100, 1), 1, '%')}")
        if year_ago:
            parts.append(f"전년 대비 {signed(round((wage[1] / year_ago - 1) * 100, 1), 1, '%')}")
        rows.append(_chain_row("시간당 평균임금", "CES0500000003", f"${num(wage[1], 2)}",
                               " · ".join(parts) + " 입니다." if parts else "비교할 직전 값이 없습니다."))

    chips = []
    for series_id in INDUSTRIES:
        point = last(series_id)
        if point:
            name = SERIES[series_id]["name"]
            chips.append(f'<span>{tip(name, series_id)} {signed(point[1] / 10000, 1, "만")}</span>')
    if chips:
        rows.append(_chain_row("업종별 고용", "PAYEMS", "",
                               f'<div class="chain-sub">{"".join(chips)}</div>'))

    changes = indicators.get("series", {}).get("PAYEMS", {}).get("revisions", [])
    if changes:
        text = " · ".join(
            f"{int(c['period'][5:7])}월 {man(c['from'])} → {signed(c['to'] / 10000, 1, '만')}" for c in changes)
        note = "지난달 숫자가 바뀌었습니다. 헤드라인이 좋아도 앞선 달이 깎였다면 흐름은 약해집니다."
    else:
        text = "없음"
        note = "이번 발표에서 지난달 수치가 바뀌지 않았습니다."
    rows.append(_chain_row("이전치 수정", "PAYEMS", "", f'<b>{text}</b><br>{note}'))

    return f'<div class="card pad"><div class="chain">{"".join(rows)}</div></div>'


def tone_meter(tone: float) -> str:
    return (f'<div><div class="tone"><i style="left:{round(tone * 100)}%"></i></div>'
            '<div class="tone-l"><span>비둘기파 (완화)</span><span>중립</span><span>매파 (긴축)</span></div>'
            f'<b class="tone-t">{tone_label(tone)}</b></div>')

"""글 사이에 넣는 시각자료. 새 숫자를 만들지 않고, 이미 적힌 데이터를 도형으로 바꾼다."""
import re

from macro import charts
from macro import data as d
from macro.fmt import esc, md

# 단위가 붙은 수치: 부호 · 숫자 · (범위) · (만/억/조) · 단위
_NUM = r"[+\-−]?\d[\d,]*(?:\.\d+)?"
_UNIT = r"(?:%p|%|bp|달러|원|배럴|MW|건|명|개(?!월)|단계|pt)"
_SCALE = r"(?:\s?(?:조|억|만)(?:\s?\d[\d,]*(?:\s?(?:억|만))?)?)"
_FIGURE = re.compile(
    rf"(?<![\d.,]){_NUM}(?:~{_NUM})?"
    rf"(?:{_SCALE}(?:\s?{_UNIT})?|\s?{_UNIT})"
)
_DATE = re.compile(r"\d+월 \d+일|\d{4}년(?: \d+월| 상반기| 하반기)?")


def big_figure(text: str) -> str | None:
    """문장에서 크게 보여줄 수치 하나. 화살표가 있으면 바뀐 뒤의 값을 먼저 찾는다."""
    tail = text.rsplit("→", 1)[1] if "→" in text else None
    for part in (tail, text):
        if part:
            m = _FIGURE.search(part)
            if m:
                return m.group(0).strip()
    m = _DATE.search(text)
    return m.group(0) if m else None


def stat_cards(numbers: list, sources: dict) -> str:
    cards = []
    for n in numbers:
        fig = big_figure(n["text"])
        link = sources.get(n.get("source"))
        cite = f'<a class="cite" href="{esc(link)}" target="_blank" rel="noopener">출처</a>' if link else ""
        top = f'<b class="stat-fig">{esc(fig)}</b>' if fig else ""
        cards.append(f'<div class="stat">{top}<p>{esc(n["text"])} {cite}</p></div>')
    return f'<div class="stats">{"".join(cards)}</div>'


def _step(text: str) -> str:
    text = text.strip()
    cls = "flow-up" if text.endswith("↑") else "flow-down" if text.endswith("↓") else ""
    return f'<span class="flow-step {cls}">{esc(text)}</span>'


ARROW = ('<span class="flow-arrow"><svg viewBox="0 0 20 12" width="20" height="12" aria-hidden="true">'
         '<path d="M1 6h15M12 2l4 4-4 4" fill="none" stroke="#8A97AB" stroke-width="1.6" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg></span>')


def flow(chain: str) -> str:
    """'A↑ → B↑ / C↓ → D' 를 갈래별 흐름도로 그린다."""
    if "→" not in chain:
        return f'<div class="chain-box">{esc(chain)}</div>'
    rows = []
    for branch in chain.split(" / "):
        steps = [s for s in branch.split("→") if s.strip()]
        rows.append('<div class="flow-row">' + ARROW.join(_step(s) for s in steps) + "</div>")
    return f'<div class="flow">{"".join(rows)}</div>'


STATUS_TILE = {
    "positive": ("tile-pos", "▲ 호재"),
    "negative": ("tile-neg", "▼ 악재"),
    "neutral": ("tile-neu", "● 중립"),
    "mixed": ("tile-mix", "◆ 혼조"),
}


def status_board(sectors: list) -> str:
    tiles = []
    for s in sectors:
        cls, label = STATUS_TILE.get(s.get("status"), STATUS_TILE["neutral"])
        days = f'<small>{s["days"]}일째</small>' if s.get("days") else ""
        tiles.append(f'<a class="board-tile {cls}" href="#{esc(s["key"])}"><span class="bt-name">{esc(s["name"])}</span>'
                     f'<span class="bt-status">{label}{days}</span></a>')
    return f'<div class="board">{"".join(tiles)}</div>'


TOPIC_SHORT = {
    "trading": "상품운용", "brokerage": "브로커리지", "ib": "IB·발행", "wm": "WM",
    "duration_gap": "듀레이션 갭", "kics": "K-ICS", "allocation": "자산배분", "fx_hedge": "환헤지",
    "flows": "자금 유출입", "fees": "보수 수익", "products": "상품 기회", "alternatives": "대체투자",
}
DIRECTION_CELL = {
    "positive": ("dc-pos", "▲ 우호"),
    "negative": ("dc-neg", "▼ 부담"),
    "neutral": ("dc-neu", "● 중립"),
    "mixed": ("dc-mix", "◆ 혼재"),
}
INSTITUTION_SHORT = {"securities": "증권사", "lp": "LP", "gp": "GP"}


def direction_grid(items: list) -> str:
    rows = []
    for item in items:
        cells = "".join(
            f'<div class="dcell {DIRECTION_CELL[p["direction"]][0]}"><span>{TOPIC_SHORT.get(p["topic"], esc(p["topic"]))}</span>'
            f'<b>{DIRECTION_CELL[p["direction"]][1]}</b></div>'
            for p in item.get("points", [])
        )
        rows.append(f'<div class="drow"><span class="drow-k">{INSTITUTION_SHORT.get(item["institution"], "")}</span>'
                    f'<div class="dcells">{cells}</div></div>')
    return f'<div class="card dgrid"><span class="label">한눈에 보는 업권별 영향</span>{"".join(rows)}</div>'


def fx_tug(drivers: list) -> str:
    side = lambda effect: "".join(f'<span class="tug-pill">{esc(x["factor"])}</span>'
                                  for x in drivers if x["effect"] == effect)
    neutral = side("neutral")
    buffer = f'<div class="tug-buffer"><span>완충 장치</span>{neutral}</div>' if neutral else ""
    return f"""<div class="card tug">
<div class="tug-side tug-weak"><span class="tug-h">원화 약세 요인 <em>환율 ↑</em></span>{side("krw_weak")}</div>
<div class="tug-mid"><b>원/달러</b><svg viewBox="0 0 64 16" width="64" height="16" aria-hidden="true"><path d="M2 8h60M8 3 2 8l6 5M56 3l6 5-6 5" fill="none" stroke="#1D3A66" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
<div class="tug-side tug-strong"><span class="tug-h">원화 강세 요인 <em>환율 ↓</em></span>{side("krw_strong")}</div>
{buffer}</div>"""


def usdkrw_chart(indicators: dict, n: int = 130) -> str:
    points = d.obs(indicators, "DEXKOUS")[-n:]
    if len(points) < 10:
        return ""
    lo, hi, ticks = charts.nice_range([v for _, v in points], 20)
    labels, seen = [], set()
    for i, (day, _) in enumerate(points):
        if day[:7] not in seen and day[8:10] <= "07":
            seen.add(day[:7])
            labels.append((i, f"{int(day[5:7])}월"))
    series = charts.Series("", charts.SERIES_COLORS[0], [(md(day), v) for day, v in points], f"{points[-1][1]:,.0f}원")
    svg = charts.line_chart([series], y_min=lo, y_max=hi, y_ticks=ticks, x_labels=labels, width=792, height=240,
                            pad_right=90, tick_fmt=lambda t: f"{t:,.0f}", value_fmt=lambda v: f"{v:,.1f}원",
                            label="원/달러 추이")
    return (f'<div class="card chart-card"><div class="chart-t"><b>원/달러 추이</b>'
            f'<span class="muted">FRED 공식 일간 · 뉴욕 정오 기준이라 서울 종가와 몇 원 다를 수 있음 · 최근 관측 {md(points[-1][0])}</span></div><div class="chart-scroll">{svg}</div>'
            '<script>document.currentScript.previousElementSibling.scrollLeft=1e6</script></div>')


IMPACT_ARROW = {"up": ("↑", "상승"), "down": ("↓", "하락"), None: ("–", "시사점")}


def impact_tiles(items: list, asset_label: dict) -> str:
    tiles = "".join(
        f'<div class="card itile"><div class="itile-top"><span>{asset_label[i["asset"]]}</span>'
        f'<b class="itile-arrow">{IMPACT_ARROW[i["direction"]][0]}</b></div>'
        f'<span class="itile-dir">{IMPACT_ARROW[i["direction"]][1]}</span><p>{esc(i["text"])}</p></div>'
        for i in items
    )
    return f'<div class="itiles">{tiles}</div>'


CSS = """
.stats{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;width:100%}
.stat{background:#F8F9FB;border:1px solid #EDF0F4;border-radius:6px;padding:14px 16px;display:flex;flex-direction:column;gap:6px}
.stat-fig{font-size:24px;line-height:1.2;font-weight:700;color:#1D3A66;letter-spacing:-0.01em}
.stat p{font-size:13px;line-height:1.6;color:#44536A;margin:0}
.cite{font-size:12px;color:#6B7A90}
.flow{display:flex;flex-direction:column;gap:10px;background:#F8F9FB;border:1px solid #EDF0F4;border-radius:6px;padding:14px 16px}
.flow-row{display:flex;flex-wrap:wrap;align-items:center;gap:6px 4px}
.flow-row+.flow-row{border-top:1px dashed #DDE2EA;padding-top:10px}
.flow-step{display:inline-flex;align-items:center;min-height:32px;padding:4px 12px;border-radius:16px;background:#FFFFFF;border:1px solid #DDE2EA;font-size:14px;font-weight:600;color:#1F2E45}
.flow-up{border-color:#9FB6D6;background:#EEF3FA}
.flow-down{border-color:#E3C6A0;background:#FBF3E4}
.flow-arrow{display:inline-flex;align-items:center}
.board{display:grid;grid-template-columns:repeat(7,1fr);gap:8px}
.board-tile{display:flex;flex-direction:column;gap:6px;padding:12px 12px 10px;border-radius:6px;border:1px solid #DDE2EA;border-top-width:4px;background:#FFFFFF;color:#0B1A30}
.board-tile:hover{text-decoration:none;box-shadow:0 2px 8px rgba(11,26,48,.08)}
.bt-name{font-size:15px;font-weight:700}
.bt-status{display:flex;justify-content:space-between;gap:4px;font-size:12px;font-weight:600}
.bt-status small{font-weight:500;color:#6B7A90}
.tile-pos{border-top-color:#1B8F52}.tile-pos .bt-status{color:#146C3E}
.tile-neg{border-top-color:#C9362E}.tile-neg .bt-status{color:#A8281F}
.tile-neu{border-top-color:#8A97AB}.tile-neu .bt-status{color:#44536A}
.chip-mix{background:#FBF3E4;color:#8A5A12}
.tile-mix{border-top-color:#D08A2E}.tile-mix .bt-status{color:#8A5A12}
.dgrid{padding:18px 22px;display:flex;flex-direction:column;gap:12px}
.drow{display:flex;gap:14px;align-items:center}
.drow-k{width:64px;flex-shrink:0;font-size:14px;font-weight:700;color:#0B1A30}
.dcells{flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:2px}
.dcell{display:flex;flex-direction:column;gap:2px;padding:10px 12px;border-radius:4px}
.dcell span{font-size:12px;color:#44536A}
.dcell b{font-size:13px}
.dc-pos{background:#E4F2EA}.dc-pos b{color:#146C3E}
.dc-neg{background:#FBE9E7}.dc-neg b{color:#A8281F}
.dc-neu{background:#EEF1F5}.dc-neu b{color:#44536A}
.dc-mix{background:#FBF3E4}.dc-mix b{color:#8A5A12}
.tug{display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:center;padding:20px 22px}
.tug-side{display:flex;flex-wrap:wrap;gap:6px;align-content:flex-start}
.tug-strong{justify-content:flex-end;text-align:right}
.tug-h{width:100%;font-size:13px;font-weight:700;color:#2B3A50;margin-bottom:4px}
.tug-h em{font-style:normal;font-weight:600;color:#6B7A90;margin-left:4px}
.tug-pill{display:inline-flex;align-items:center;height:30px;padding:0 12px;border-radius:15px;font-size:13px;font-weight:600;background:#EEF1F5;color:#1F2E45}
.tug-weak .tug-pill{background:#0B1A30;color:#FFFFFF}
.tug-mid{display:flex;flex-direction:column;align-items:center;gap:4px}
.tug-mid b{font-size:14px;color:#0B1A30}
.tug-buffer{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:6px;align-items:center;border-top:1px solid #EDF0F4;padding-top:12px;font-size:12px;color:#6B7A90}
.tug-buffer>span:first-child{margin-right:4px;font-weight:600}
.chart-card{padding:20px 22px 16px;display:flex;flex-direction:column;gap:12px}
.chart-t{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap}
.chart-t b{font-size:15px}
.chart-scroll{overflow-x:auto}
.chart-scroll svg{min-width:560px}
.chart-t span{font-size:12px}
.itiles{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.itile{padding:18px 20px;display:flex;flex-direction:column;gap:8px}
.itile-top{display:flex;justify-content:space-between;align-items:center;font-size:14px;font-weight:700;color:#0B1A30}
.itile-arrow{font-size:28px;line-height:1;color:#1D3A66}
.itile-dir{font-size:12px;font-weight:600;color:#6B7A90}
.itile p{font-size:14px;line-height:1.7;color:#2B3A50;margin:0}
@media (max-width:900px){.board{grid-template-columns:repeat(4,1fr)}}
@media (max-width:640px){
  .board{grid-template-columns:repeat(2,1fr)}
  .dcells{grid-template-columns:repeat(2,1fr)}
  .drow{flex-direction:column;align-items:flex-start;gap:6px}
  .tug{grid-template-columns:1fr;text-align:left}
  .tug-strong{justify-content:flex-start;text-align:left}
  .tug-mid{flex-direction:row}
  .itiles{grid-template-columns:1fr}
}
"""

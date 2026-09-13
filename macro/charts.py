"""SVG 차트 생성기. 외부 라이브러리 없이 문자열로 만든다."""
import math
from dataclasses import dataclass

from macro.fmt import esc

GRID = "#E4E8EE"
MUTED = "#6B7A90"
INK = "#0F1B2D"
SERIES_COLORS = ("#2B5C9E", "#D08A2E")
PAD_LEFT, PAD_TOP, PAD_BOTTOM = 56, 16, 32


@dataclass
class Series:
    name: str
    color: str
    points: list
    end_label: str
    dy: float = 0


def _r(n: float) -> float:
    return round(n, 1)


def nice_range(values, step):
    lo = round(math.floor(min(values) / step) * step, 6)
    hi = round(math.ceil(max(values) / step) * step, 6)
    if lo == hi:
        hi = round(lo + step, 6)
    count = int(round((hi - lo) / step))
    return lo, hi, [round(lo + i * step, 6) for i in range(count + 1)]


def _frame(width, height, body, label):
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="{esc(label)}" '
        f'style="display:block;max-width:{width}px;overflow:visible;font-variant-numeric:tabular-nums" '
        f'xmlns="http://www.w3.org/2000/svg">{body}</svg>'
    )


def line_chart(series, *, y_min, y_max, y_ticks, x_labels, width=1120, height=300, pad_right=140,
               step=False, ref=None, tick_fmt=lambda t: f"{t:.1f}%", value_fmt=lambda v: f"{v:.1f}%", label=""):
    n = len(series[0].points)
    left, right, top, bottom = PAD_LEFT, width - pad_right, PAD_TOP, height - PAD_BOTTOM
    x = lambda i: _r(left + i * (right - left) / max(n - 1, 1))
    y = lambda v: _r(bottom - (v - y_min) / (y_max - y_min) * (bottom - top))
    parts = []
    for t in y_ticks:
        parts.append(f'<line x1="{left}" y1="{y(t)}" x2="{right}" y2="{y(t)}" stroke="{GRID}" stroke-width="1"></line>')
        parts.append(f'<text x="{left - 10}" y="{_r(y(t) + 4)}" text-anchor="end" font-size="12" fill="{MUTED}">{esc(tick_fmt(t))}</text>')
    if ref:
        parts.append(f'<text x="{left + 8}" y="{_r(y(ref[0]) - 8)}" font-size="12" fill="{MUTED}">{esc(ref[1])}</text>')
    for i, text in x_labels:
        anchor = "start" if i == 0 else ("end" if i == n - 1 else "middle")
        parts.append(f'<text x="{x(i)}" y="{height - 8}" text-anchor="{anchor}" font-size="12" fill="{MUTED}">{esc(text)}</text>')
    for s in series:
        values = [v for _, v in s.points]
        if step:
            d = f"M{x(0)} {y(values[0])}" + "".join(f" H{x(i)} V{y(values[i])}" for i in range(1, n))
        else:
            d = " ".join(f"{'L' if i else 'M'}{x(i)} {y(v)}" for i, v in enumerate(values))
        parts.append(f'<path d="{d}" fill="none" stroke="{s.color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"></path>')
    for s in series:
        last = s.points[-1][1]
        parts.append(f'<circle cx="{x(n - 1)}" cy="{y(last)}" r="4" fill="{s.color}" stroke="#FFFFFF" stroke-width="2"></circle>')
        name = f'<tspan fill="{MUTED}" dx="6">{esc(s.name)}</tspan>' if s.name else ""
        parts.append(f'<text x="{right + 12}" y="{_r(y(last) + 4 + s.dy)}" font-size="13" fill="{INK}"><tspan font-weight="600">{esc(s.end_label)}</tspan>{name}</text>')
        prefix = f"{s.name} " if s.name else ""
        for i, (point_label, value) in enumerate(s.points):
            parts.append(f'<circle class="hit" cx="{x(i)}" cy="{y(value)}" r="8" fill="transparent">'
                         f'<title>{esc(point_label)} · {esc(prefix)}{esc(value_fmt(value))}</title></circle>')
    return _frame(width, height, "".join(parts), label)


def sparkline(values, *, width=120, height=36, label=""):
    n = len(values)
    if n < 2:
        return ""
    pad = 5
    lo, hi = min(values), max(values)
    x = lambda i: _r(pad + i * (width - 2 * pad) / (n - 1))
    y = lambda v: _r(height - pad - (0.5 if hi == lo else (v - lo) / (hi - lo)) * (height - 2 * pad))
    d = " ".join(f"{'L' if i else 'M'}{x(i)} {y(v)}" for i, v in enumerate(values))
    body = (
        f"<title>{esc(label)}</title>"
        f'<path d="{d}" fill="none" stroke="#8A97AB" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"></path>'
        f'<circle cx="{x(n - 1)}" cy="{y(values[-1])}" r="3.5" fill="#1D3A66" stroke="#FFFFFF" stroke-width="2"></circle>'
    )
    return _frame(width, height, body, label)

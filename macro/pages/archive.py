"""브리핑 아카이브(archive.html)."""
from macro import components as c
from macro.fmt import esc, ymd_ko
from macro.layout import page

CSS = """
.arc{padding-top:48px;display:flex;flex-direction:column;gap:24px}
.arc-title{font-size:32px;color:#0B1A30}
.arc-list{display:flex;flex-direction:column;gap:10px}
.arc-row{display:flex;align-items:center;gap:16px;padding:18px 22px;color:#0F1B2D}
.arc-row:hover{border-color:#1D3A66;text-decoration:none;color:#0F1B2D}
.arc-d{width:150px;flex-shrink:0;font-size:14px;color:#5B6B80}
.arc-h{font-size:16px;font-weight:600;line-height:1.5}
@media (max-width:640px){.arc{padding-top:28px}.arc-row{flex-wrap:wrap;gap:8px}.arc-d{width:auto}}
"""


def render_archive(site) -> str:
    if not site.briefings:
        content = c.empty_state(c.EMPTY_MESSAGE)
    else:
        content = '<div class="arc-list">' + "".join(
            f'<a class="card arc-row" href="briefings/{b["date"]}.html"><span class="arc-d num">{ymd_ko(b["date"])}</span>'
            f'{c.type_chip(b)}<span class="arc-h">{esc(b["headline"])}</span></a>'
            for b in site.briefings
        ) + "</div>"
    body = f'<main class="wrap arc"><h1 class="serif arc-title">브리핑 아카이브</h1>{content}</main>'
    return page(title="아카이브", active="archive", body=body, css=c.CSS + CSS)

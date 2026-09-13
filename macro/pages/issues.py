"""기존 금융권 취업 이슈 챕터 페이지. config.ISSUES를 그대로 렌더링한다."""
import re

from macro.fmt import esc
from macro.layout import page

NUMBERED = ("①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩")

CSS = """
.ch-bar{background:#EEF2F8;border-bottom:1px solid #DDE2EA;position:sticky;top:0;z-index:20}
.ch-bar .wrap{display:flex;flex-wrap:wrap;gap:7px;padding-top:10px;padding-bottom:10px}
.ch-btn{background:#FFFFFF;border:1px solid #C5CEDB;color:#1D3A66;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;font-family:inherit}
.ch-btn:hover{border-color:#1D3A66}
.ch-btn.active{background:#0B1A30;color:#FFFFFF;border-color:#0B1A30}
.issues-main{max-width:980px;margin:28px auto 0;padding-left:18px;padding-right:18px}
.chapter-header{background:#FFFFFF;border:1px solid #DDE2EA;border-radius:6px;padding:22px 26px;margin-bottom:16px}
.chapter-badge{display:inline-block;background:#0B1A30;color:#FFFFFF;font-size:12px;font-weight:700;padding:3px 11px;border-radius:12px;margin-bottom:9px}
.chapter-title{font-size:26px;font-weight:700;color:#0B1A30;margin-bottom:12px;line-height:1.35}
.tags{display:flex;flex-wrap:wrap;gap:6px}
.tag{background:#EEF2F8;color:#1D3A66;font-size:12px;font-weight:600;padding:3px 11px;border-radius:10px}
.section-block{background:#FFFFFF;border:1px solid #DDE2EA;border-radius:6px;padding:22px 26px;margin-bottom:16px}
.section-title{font-size:17px;font-weight:700;color:#0B1A30;margin-bottom:15px;padding-bottom:9px;border-bottom:1px solid #EDF0F4}
.content-para{margin-bottom:10px;font-size:15px;line-height:1.8;color:#2B3A50}
.content-section-header{font-size:16px;font-weight:700;color:#0B1A30;background:#EEF2F8;border-radius:4px;padding:9px 16px;margin:22px 0 12px}
.content-bullet-title{font-size:15px;font-weight:700;color:#1D3A66;margin:18px 0 6px}
.content-numbered-item{font-size:15px;font-weight:600;line-height:1.75;margin-bottom:10px;padding:10px 14px;background:#F8F9FB;border:1px solid #EDF0F4;border-radius:4px}
.term-cell{font-weight:700;color:#1D3A66;min-width:180px}
.articles-wrap{display:flex;flex-direction:column;gap:12px}
.article-card{background:#F8F9FB;border:1px solid #EDF0F4;border-radius:4px;padding:14px 18px}
.article-headline{font-weight:700;color:#0B1A30;font-size:15px;margin-bottom:7px;line-height:1.45}
.article-body{font-size:14px;color:#44536A;line-height:1.65}
.insights-list{padding-left:22px}
.insights-list li{font-size:15px;color:#2B3A50;margin-bottom:9px;line-height:1.65}
@media (max-width:640px){.term-cell{min-width:110px}.chapter-title{font-size:21px}.section-block,.chapter-header{padding:18px}}
"""

SCRIPT = """<script>
function showChapter(ch) {
  document.querySelectorAll(".chapter-section").forEach(function (s) { s.hidden = true; });
  document.querySelectorAll(".ch-btn").forEach(function (b) { b.classList.remove("active"); });
  var sec = document.getElementById("chapter-" + ch);
  if (sec) sec.hidden = false;
  var btn = document.getElementById("ch-btn-" + ch);
  if (btn) btn.classList.add("active");
}
document.querySelectorAll(".ch-btn").forEach(function (b) {
  b.addEventListener("click", function () { showChapter(b.dataset.ch); window.scrollTo({ top: 0, behavior: "smooth" }); });
});
</script>"""


def parse_content(content: str) -> str:
    parts = []
    for line in (raw.strip() for raw in content.strip().split("\n")):
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            parts.append(f'<h4 class="content-section-header">{esc(line[1:-1])}</h4>')
        elif line.startswith("■ "):
            rest = line[2:]
            colon = rest.find(": ")
            if colon > 10:
                parts.append(f'<p class="content-bullet-title">■ {esc(rest[:colon])}</p>')
                body = rest[colon + 2:].strip()
                if body:
                    parts.append(f'<p class="content-para">{esc(body)}</p>')
            else:
                parts.append(f'<p class="content-bullet-title">{esc(line)}</p>')
        elif line[:1] in NUMBERED:
            for item in re.split(r"(?<=[。.\s])(?=[②③④⑤⑥⑦⑧⑨⑩])", line):
                if item.strip():
                    parts.append(f'<p class="content-numbered-item">{esc(item.strip())}</p>')
        else:
            parts.append(f'<p class="content-para">{esc(line)}</p>')
    return "\n".join(parts)


def _terms(terms: list) -> str:
    rows = "".join(
        f'<tr><td class="term-cell">{esc(t["term"])}</td><td>{esc(t["definition"])}</td></tr>' for t in terms
    )
    return f'<div class="tscroll"><table class="t"><thead><tr><th>용어</th><th>정의</th></tr></thead><tbody>{rows}</tbody></table></div>'


def _articles(articles: list) -> str:
    cards = "".join(
        f'<div class="article-card"><div class="article-headline">{esc(a["headline"])}</div>'
        f'<div class="article-body">{esc(a["body"])}</div></div>'
        for a in articles
    )
    return f'<div class="articles-wrap">{cards}</div>'


def _chapter(issue: dict, first: bool) -> str:
    ch = issue["chapter"]
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in issue.get("hashtags", []))
    insights = "".join(f"<li>{esc(tip)}</li>" for tip in issue.get("insights", []))
    hidden = "" if first else " hidden"
    return f"""<section id="chapter-{ch}" class="chapter-section"{hidden}>
<div class="chapter-header"><span class="chapter-badge">Chapter {ch}</span>
<h2 class="chapter-title serif">{esc(issue["title"])}</h2><div class="tags">{tags}</div></div>
<div class="section-block"><h3 class="section-title">핵심 내용 분석</h3>{parse_content(issue["content"])}</div>
<div class="section-block"><h3 class="section-title">핵심 용어 사전</h3>{_terms(issue.get("terms", []))}</div>
<div class="section-block"><h3 class="section-title">최신 뉴스 브리핑</h3>{_articles(issue.get("articles", []))}</div>
<div class="section-block"><h3 class="section-title">면접 핵심 인사이트</h3><ul class="insights-list">{insights}</ul></div>
</section>"""


def render_issues(issues: list) -> str:
    buttons = "".join(
        f'<button class="ch-btn{" active" if i == 0 else ""}" id="ch-btn-{it["chapter"]}" data-ch="{it["chapter"]}">'
        f'Ch.{it["chapter"]} {esc(it["title"])}</button>'
        for i, it in enumerate(issues)
    )
    chapters = "\n".join(_chapter(it, i == 0) for i, it in enumerate(issues))
    body = (
        f'<div class="ch-bar"><div class="wrap">{buttons}</div></div>'
        f'<main class="issues-main">{chapters}</main>{SCRIPT}'
    )
    return page(title="금융권 취업 이슈", active="issues", body=body, css=CSS)

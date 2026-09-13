# generator.py  ─  HTML 웹 빌더 로직 모듈
# ════════════════════════════════════════════════════════════
#  [연결 접점]
#    main.py  →  from generator import build_html
#    인자     →  build_html(issues: list, ai_message: str, output_path: str = "index.html")
#
#  [디자인 규칙]
#    - 우리은행 시그니처 블루  #005BAA
#    - 소프트 블루 배경        #E6F0FA
#    - line-height             1.25 (본문 블록 내 단락은 1.7)
#    - <hr> 구분선 사용 금지   (border-bottom 으로 대체)
#    - 표 셀 패딩              10px 14px (완벽 정렬)
# ════════════════════════════════════════════════════════════

import html as _html_mod


# ── 내부 헬퍼 ──────────────────────────────────────────────

def _esc(text: str) -> str:
    """HTML 특수문자 이스케이프 처리"""
    return _html_mod.escape(str(text))


def _parse_content_html(content: str) -> str:
    """
    콘텐츠 문자열을 구조화된 HTML로 변환합니다.
    마커 규칙:
      [섹션 제목]              → <h4 class="content-section-header">
      ■ 제목: 본문 (긴 줄)    → 제목은 content-bullet-title, 본문은 content-para 자동 분리
      ■ 제목 (짧은 줄만)      → <p class="content-bullet-title">
      ①②③④ 로 시작하는 줄   → <p class="content-numbered-item">
      일반 텍스트              → <p class="content-para">
    """
    _numbered = ('①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩')
    lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
    parts = []
    for line in lines:
        if line.startswith('[') and line.endswith(']'):
            parts.append(
                f'<h4 class="content-section-header">{_esc(line[1:-1])}</h4>'
            )
        elif line.startswith('■ '):
            rest = line[2:]
            # ': ' 구분자가 제목(10자 이상) 이후에 나오면 제목·본문 자동 분리
            colon_idx = rest.find(': ')
            if colon_idx > 10:
                title = rest[:colon_idx]
                body  = rest[colon_idx + 2:].strip()
                parts.append(f'<p class="content-bullet-title">■ {_esc(title)}</p>')
                if body:
                    parts.append(f'<p class="content-para">{_esc(body)}</p>')
            else:
                parts.append(f'<p class="content-bullet-title">{_esc(line)}</p>')
        elif line[:1] in _numbered:
            # ①②③④ 항목: 각 번호를 별도 카드로 분리
            import re as _re
            items = _re.split(r'(?<=[。.\s])(?=[②③④⑤⑥⑦⑧⑨⑩])', line)
            for item in items:
                item = item.strip()
                if item:
                    parts.append(f'<p class="content-numbered-item">{_esc(item)}</p>')
        else:
            parts.append(f'<p class="content-para">{_esc(line)}</p>')
    return '\n          '.join(parts)


def _render_nav(issues: list) -> str:
    """상단 고정 네비게이션 버튼 목록 생성 (챕터 수에 따라 동적 확장)"""
    items = []
    for issue in issues:
        ch = issue["chapter"]
        items.append(
            f'<button class="nav-btn" onclick="showChapter({ch})" '
            f'id="nav-btn-{ch}">Ch.{ch}&nbsp;{_esc(issue["title"])}</button>'
        )
    return "\n    ".join(items)


def _render_terms(terms: list) -> str:
    """핵심 용어 사전 테이블 렌더링"""
    rows = []
    for t in terms:
        rows.append(
            f"<tr>"
            f'<td class="term-cell">{_esc(t["term"])}</td>'
            f"<td>{_esc(t['definition'])}</td>"
            f"</tr>"
        )
    body = "\n          ".join(rows)
    return f"""<table class="terms-table">
        <thead>
          <tr><th>용어</th><th>정의</th></tr>
        </thead>
        <tbody>
          {body}
        </tbody>
      </table>"""


def _render_articles(articles: list) -> str:
    """가상 기사 스크랩 카드 렌더링"""
    cards = []
    for a in articles:
        cards.append(
            f'<div class="article-card">'
            f'<div class="article-headline">{_esc(a["headline"])}</div>'
            f'<div class="article-body">{_esc(a["body"])}</div>'
            f"</div>"
        )
    return '<div class="articles-wrap">\n        ' + "\n        ".join(cards) + "\n      </div>"


def _render_insights(insights: list) -> str:
    """면접 핵심 인사이트 리스트 렌더링"""
    items = "\n          ".join(f"<li>{_esc(tip)}</li>" for tip in insights)
    return f'<ul class="insights-list">\n          {items}\n        </ul>'


def _render_chapter_section(issue: dict) -> str:
    """챕터 하나를 완성된 <section> 블록으로 렌더링"""
    ch = issue["chapter"]
    tags_html = " ".join(
        f'<span class="tag">{_esc(t)}</span>' for t in issue.get("hashtags", [])
    )
    content_html = _parse_content_html(issue["content"])
    return f"""
    <section id="chapter-{ch}" class="chapter-section" style="display:none;">
      <div class="chapter-header">
        <span class="chapter-badge">Chapter {ch}</span>
        <h2 class="chapter-title">{_esc(issue['title'])}</h2>
        <div class="tags">{tags_html}</div>
      </div>

      <div class="section-block">
        <h3 class="section-title">&#128203; 핵심 내용 분석</h3>
        <div class="content-body">
          {content_html}
        </div>
      </div>

      <div class="section-block">
        <h3 class="section-title">&#128218; 핵심 용어 사전</h3>
        {_render_terms(issue.get('terms', []))}
      </div>

      <div class="section-block">
        <h3 class="section-title">&#128240; 최신 뉴스 브리핑</h3>
        {_render_articles(issue.get('articles', []))}
      </div>

      <div class="section-block">
        <h3 class="section-title">&#128161; 면접 핵심 인사이트</h3>
        {_render_insights(issue.get('insights', []))}
      </div>
    </section>"""


def _render_all_chapters(issues: list) -> str:
    return "\n".join(_render_chapter_section(issue) for issue in issues)


def _render_js(issues: list) -> str:
    """SPA 탭 전환 자바스크립트 생성"""
    first_ch = issues[0]["chapter"] if issues else 1
    return f"""<script>
    function showChapter(ch) {{
      document.querySelectorAll('.chapter-section').forEach(function(s) {{
        s.style.display = 'none';
      }});
      document.querySelectorAll('.nav-btn').forEach(function(b) {{
        b.classList.remove('active');
      }});
      var sec = document.getElementById('chapter-' + ch);
      if (sec) sec.style.display = 'block';
      var btn = document.getElementById('nav-btn-' + ch);
      if (btn) btn.classList.add('active');
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}
    window.addEventListener('DOMContentLoaded', function() {{
      showChapter({first_ch});
    }});
  </script>"""


def _render_css() -> str:
    return """<style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', sans-serif;
      background: #F4F8FC;
      color: #1a2840;
      line-height: 1.25;
    }

    /* ── AI 알림 배너 ── */
    .ai-banner {
      background: linear-gradient(90deg, #003f7f 0%, #005BAA 60%, #0077CC 100%);
      color: #fff;
      padding: 13px 28px;
      font-size: 0.93rem;
      letter-spacing: 0.015em;
      text-align: center;
      font-weight: 500;
    }

    /* ── 헤더 ── */
    .site-header {
      background: #fff;
      border-bottom: 4px solid #005BAA;
      padding: 20px 36px;
    }
    .site-header h1 {
      font-size: 1.5rem;
      font-weight: 800;
      color: #005BAA;
      letter-spacing: -0.5px;
    }
    .site-header .subtitle {
      font-size: 0.84rem;
      color: #6b7fa3;
      margin-top: 4px;
    }

    /* ── 네비게이션 바 ── */
    .nav-bar {
      background: #E6F0FA;
      padding: 10px 20px;
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      position: sticky;
      top: 0;
      z-index: 200;
      border-bottom: 1px solid #c2d8ef;
    }
    .nav-btn {
      background: #fff;
      border: 1.5px solid #b0c8e8;
      color: #005BAA;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 0.80rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
      white-space: nowrap;
    }
    .nav-btn:hover { background: #d0e6f8; border-color: #005BAA; }
    .nav-btn.active { background: #005BAA; color: #fff; border-color: #005BAA; }

    /* ── 메인 컨테이너 ── */
    .main-content { max-width: 980px; margin: 28px auto; padding: 0 18px 60px; }

    /* ── 챕터 섹션 ── */
    .chapter-section { animation: fadeIn 0.22s ease; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* ── 챕터 헤더 카드 ── */
    .chapter-header {
      background: #fff;
      border-left: 6px solid #005BAA;
      border-radius: 0 10px 10px 0;
      padding: 22px 26px;
      margin-bottom: 18px;
      box-shadow: 0 2px 10px rgba(0,91,170,0.08);
    }
    .chapter-badge {
      display: inline-block;
      background: #005BAA;
      color: #fff;
      font-size: 0.73rem;
      font-weight: 700;
      padding: 3px 11px;
      border-radius: 12px;
      margin-bottom: 9px;
      letter-spacing: 0.03em;
    }
    .chapter-title {
      font-size: 1.60rem;
      font-weight: 800;
      color: #003a72;
      margin-bottom: 12px;
      line-height: 1.3;
    }
    .tags { display: flex; flex-wrap: wrap; gap: 6px; }
    .tag {
      background: #E6F0FA;
      color: #005BAA;
      font-size: 0.77rem;
      font-weight: 600;
      padding: 3px 11px;
      border-radius: 10px;
    }

    /* ── 섹션 블록 공통 ── */
    .section-block {
      background: #fff;
      border-radius: 10px;
      padding: 22px 26px;
      margin-bottom: 16px;
      box-shadow: 0 2px 8px rgba(0,91,170,0.06);
    }
    .section-title {
      font-size: 1.02rem;
      font-weight: 700;
      color: #005BAA;
      margin-bottom: 15px;
      padding-bottom: 9px;
      border-bottom: 2px solid #E6F0FA;
    }

    /* ── 본문 단락 (공통) ── */
    .content-para {
      margin-bottom: 10px;
      font-size: 0.94rem;
      line-height: 1.80;
      color: #2c3e5a;
      font-weight: 500;
    }
    .content-para:last-child { margin-bottom: 0; }

    /* ── 구조화 콘텐츠 — 섹션 헤더 ── */
    .content-section-header {
      font-size: 1.00rem;
      font-weight: 800;
      color: #003a72;
      background: #E6F0FA;
      border-left: 5px solid #005BAA;
      border-radius: 0 6px 6px 0;
      padding: 9px 16px;
      margin: 22px 0 12px 0;
      letter-spacing: -0.2px;
    }

    /* ── 구조화 콘텐츠 — ■ 소제목 ── */
    .content-bullet-title {
      font-size: 0.97rem;
      font-weight: 800;
      color: #005BAA;
      margin: 18px 0 6px 0;
      padding: 7px 14px;
      background: #f0f6fc;
      border-left: 4px solid #0077CC;
      border-radius: 0 4px 4px 0;
    }

    /* ── 구조화 콘텐츠 — ①②③④ 번호 항목 ── */
    .content-numbered-item {
      font-size: 0.93rem;
      font-weight: 700;
      color: #1a2840;
      line-height: 1.75;
      margin-bottom: 10px;
      padding: 10px 14px;
      background: #fafcff;
      border: 1px solid #dce8f5;
      border-left: 4px solid #005BAA;
      border-radius: 0 6px 6px 0;
    }

    /* 구버전 p 태그 호환 */
    .content-body p {
      margin-bottom: 10px;
      font-size: 0.94rem;
      line-height: 1.80;
      color: #2c3e5a;
      font-weight: 500;
    }
    .content-body p:last-child { margin-bottom: 0; }

    /* ── 용어 테이블 ── */
    .terms-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .terms-table thead tr { background: #005BAA; color: #fff; }
    .terms-table thead th {
      padding: 10px 14px;
      text-align: left;
      font-weight: 700;
      letter-spacing: 0.02em;
    }
    .terms-table thead th:first-child { border-radius: 6px 0 0 0; }
    .terms-table thead th:last-child  { border-radius: 0 6px 0 0; }
    .terms-table tbody tr:nth-child(even) { background: #f0f6fc; }
    .terms-table tbody tr:hover { background: #daeaf8; }
    .terms-table td {
      padding: 10px 14px;
      border-bottom: 1px solid #e0ecf8;
      vertical-align: top;
      line-height: 1.55;
    }
    .term-cell {
      font-weight: 700;
      color: #005BAA;
      min-width: 190px;
      white-space: nowrap;
    }

    /* ── 기사 카드 ── */
    .articles-wrap { display: flex; flex-direction: column; gap: 12px; }
    .article-card {
      background: #f7fafd;
      border: 1px solid #d0e4f4;
      border-left: 5px solid #005BAA;
      border-radius: 6px;
      padding: 14px 18px;
    }
    .article-headline {
      font-weight: 700;
      color: #003a72;
      font-size: 0.95rem;
      margin-bottom: 7px;
      line-height: 1.4;
    }
    .article-body {
      font-size: 0.86rem;
      color: #4a5c78;
      line-height: 1.65;
    }

    /* ── 인사이트 리스트 ── */
    .insights-list { padding-left: 22px; }
    .insights-list li {
      font-size: 0.91rem;
      color: #2c3e5a;
      margin-bottom: 9px;
      line-height: 1.65;
      padding-left: 4px;
    }
    .insights-list li::marker { color: #005BAA; font-size: 1.05rem; }

    /* ── 푸터 ── */
    .site-footer {
      text-align: center;
      padding: 24px;
      font-size: 0.77rem;
      color: #8fa8c8;
      margin-top: 24px;
    }

    /* ── 반응형 ── */
    @media (max-width: 640px) {
      .site-header { padding: 14px 16px; }
      .chapter-title { font-size: 1.25rem; }
      .term-cell { min-width: 130px; white-space: normal; }
    }
  </style>"""


# ── 공개 API ───────────────────────────────────────────────

def build_html(issues: list, ai_message: str, output_path: str = "index.html") -> None:
    """
    config.py 의 ISSUES 데이터와 AI 대사를 받아 완성된 index.html 을 생성합니다.

    Parameters
    ----------
    issues      : config.ISSUES 리스트
    ai_message  : main.py 가 생성한 AI 브리핑 대사 문자열
    output_path : 출력 파일 경로 (기본값: index.html)
    """
    total = len(issues)
    html_output = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>2026 경제신문 주요이슈 정리본 | 금융권 취업 준비</title>
  {_render_css()}
</head>
<body>

  <!-- AI 비서 알림 배너 (main.py 에서 동적 주입) -->
  <div class="ai-banner">
    &#129302;&nbsp;{_esc(ai_message)}
  </div>

  <!-- 사이트 헤더 -->
  <header class="site-header">
    <h1>2026 경제신문 주요이슈 정리본</h1>
    <div class="subtitle">
      금융권 취업 준비생을 위한 핵심 이슈 완전 정복&nbsp;&middot;&nbsp;총 {total}개 Chapter
    </div>
  </header>

  <!-- 상단 고정 네비게이션 (챕터 수에 따라 자동 확장) -->
  <nav class="nav-bar">
    {_render_nav(issues)}
  </nav>

  <!-- 메인 콘텐츠 영역 -->
  <main class="main-content">
    {_render_all_chapters(issues)}
  </main>

  <!-- 푸터 -->
  <footer class="site-footer">
    &copy; 2026 SangEunLAB &middot; Powered by Woori Bank Theme &middot; 우리은행 합격을 응원합니다!
  </footer>

  <!-- SPA 탭 전환 스크립트 -->
  {_render_js(issues)}

</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"[generator] '{output_path}' 생성 완료 ({total}개 챕터)")

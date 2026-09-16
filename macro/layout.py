"""공통 레이아웃: CSS 토큰, 헤더·내비게이션, 푸터, D-day 스크립트."""
from macro.fmt import esc

DISCLAIMER = "투자 권유가 아닙니다"

NAV = [
    ("home", "홈", "index.html"),
    ("briefing", "주간 브리핑", "briefings/latest.html"),
    ("sectors", "섹터 이슈", "sectors.html"),
    ("fomc", "FOMC", "fomc.html"),
    ("indicators", "거시지표", "indicators.html"),
    ("archive", "아카이브", "archive.html"),
    ("issues", "취업 이슈", "issues.html"),
]

LOGO = (
    '<svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true">'
    '<rect x="1" y="12" width="4" height="9" fill="#FFFFFF"></rect>'
    '<rect x="9" y="6" width="4" height="15" fill="#FFFFFF"></rect>'
    '<rect x="17" y="1" width="4" height="20" fill="#8FA9D6"></rect></svg>'
)

FONTS = (
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700"
    "&family=Noto+Serif+KR:wght@600;700&display=swap"
)

CSS = """
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:#F4F6F9;color:#0F1B2D;font-family:'IBM Plex Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif;-webkit-font-smoothing:antialiased}
a{color:#1D3A66;text-decoration:none}a:hover{color:#0B1A30;text-decoration:underline}
h1,h2,h3,p,ol,ul{margin:0}
[hidden]{display:none!important}
.serif{font-family:'Noto Serif KR','Batang','AppleMyungjo',serif}
.num{font-variant-numeric:tabular-nums}
.muted{color:#6B7A90}
.wrap{max-width:1248px;margin:0 auto;padding-left:24px;padding-right:24px}
.mast{background:#0B1A30;color:#FFFFFF}
.mast-in{display:flex;align-items:stretch;justify-content:space-between;min-height:64px;gap:24px}
.brand{display:flex;align-items:center;gap:12px;color:#FFFFFF}
.brand:hover{color:#FFFFFF;text-decoration:none}
.brand .serif{font-size:20px;font-weight:700}
.tagline{font-size:12px;color:#8FA0BA;padding-left:12px;border-left:1px solid #2A3E5E}
.navs{display:flex;gap:28px;font-size:14px}
.nav{display:flex;align-items:center;color:#B7C3D6;font-weight:500;border-bottom:3px solid transparent;padding-top:3px;white-space:nowrap}
.nav:hover{color:#FFFFFF;text-decoration:none}
.nav.on{color:#FFFFFF;border-bottom-color:#FFFFFF}
.card{background:#FFFFFF;border:1px solid #DDE2EA;border-radius:6px}
.dark-card{background:#0B1A30;color:#FFFFFF;border-radius:6px}
.h2{font-size:20px;font-weight:700;color:#0F1B2D}
.eyebrow{font-size:13px;font-weight:600;color:#5B6B80}
.chip{display:inline-flex;align-items:center;gap:5px;height:24px;padding:0 8px;border-radius:4px;font-size:12px;font-weight:600;white-space:nowrap}
.chip-pos{background:#E4F2EA;color:#146C3E}
.chip-neg{background:#FBE9E7;color:#A8281F}
.chip-neu{background:#EEF1F5;color:#44536A}
.chip-dark{background:#0B1A30;color:#FFFFFF}
.up{fill:#1B8F52}.down{fill:#C9362E}.flat{fill:#6B7A90}
.d-up{fill:#5BD49A}.d-down{fill:#FF8A80}
.sec-head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}
.grid-2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.grid-4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
.grid-5{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px}
.tscroll{overflow-x:auto}
table.t{width:100%;border-collapse:collapse;font-size:14px;font-variant-numeric:tabular-nums}
table.t th{text-align:left;font-size:12px;font-weight:600;color:#6B7A90;padding:10px 12px;border-bottom:1px solid #DDE2EA;background:#F8F9FB;white-space:nowrap}
table.t td{padding:12px;border-bottom:1px solid #EDF0F4;vertical-align:middle}
table.t tr:last-child td{border-bottom:0}
table.t .r{text-align:right}
.empty{padding:48px 24px;text-align:center;color:#6B7A90;font-size:15px}
.foot{background:#0B1A30;color:#8FA0BA;margin-top:72px}
.foot-in{padding-top:32px;padding-bottom:36px;display:flex;justify-content:space-between;gap:48px;font-size:13px;line-height:1.7}
.foot-l{max-width:720px;display:flex;flex-direction:column;gap:6px}
.foot-l strong{color:#FFFFFF}
.foot-r{text-align:right;display:flex;flex-direction:column;gap:6px}
.foot-r .serif{color:#FFFFFF;font-size:16px;font-weight:700}
@media (max-width:640px){
  .wrap{padding-left:16px;padding-right:16px}
  .tagline{display:none}
  .mast-in{flex-direction:column;gap:0;padding-top:12px}
  .navs{overflow-x:auto;gap:20px;min-height:44px}
  .grid-2,.grid-5{grid-template-columns:repeat(1,minmax(0,1fr))}
  .grid-4{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
  .foot-in{flex-direction:column;gap:20px}
  .foot-r{text-align:left}
  .hide-m{display:none}
}
"""

DDAY_SCRIPT = """<script>
document.querySelectorAll("[data-dday]").forEach(function (el) {
  var seoul = function (d) { return new Date(d.toLocaleString("en-US", { timeZone: "Asia/Seoul" })); };
  var today = seoul(new Date());
  var target = seoul(new Date(el.getAttribute("data-dday") + "T12:00:00+09:00"));
  today.setHours(0, 0, 0, 0);
  target.setHours(0, 0, 0, 0);
  var days = Math.round((target - today) / 86400000);
  el.textContent = days > 0 ? "D-" + days : (days === 0 ? "D-DAY" : "종료");
});
</script>"""


def page(*, title: str, active: str, body: str, root: str = "", css: str = "") -> str:
    """완성된 HTML 문서를 돌려준다. root는 하위 폴더 페이지에서 '../'."""
    nav = "".join(
        f'<a class="nav{" on" if key == active else ""}" href="{root}{href}">{label}</a>'
        for key, label, href in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Macro Briefing</title>
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}{css}</style>
</head>
<body>
<header class="mast"><div class="wrap mast-in">
<a class="brand" href="{root}index.html">{LOGO}<span class="serif">Macro Briefing</span><span class="tagline">미국 거시경제 · FOMC · 섹터 주간 브리핑</span></a>
<nav class="navs">{nav}</nav>
</div></header>
{body}
<footer class="foot"><div class="wrap foot-in">
<div class="foot-l"><strong>{DISCLAIMER}</strong>
<span>이 사이트는 거시경제 학습과 금융권 취업 준비를 위한 참고 자료입니다. 분석과 전망은 AI가 공개 자료를 바탕으로 작성해 오류가 있을 수 있으며, 투자 판단의 근거로 쓸 수 없습니다.</span>
<span>지표 수치: FRED(세인트루이스 연방준비은행) · 예상치·뉴스: 각 항목에 출처 표기</span></div>
<div class="foot-r"><span class="serif">Macro Briefing</span><span>주 1회 + 주요 발표 시 갱신</span><span>© 2026 SangEunLAB</span></div>
</div></footer>
{DDAY_SCRIPT}
</body>
</html>
"""

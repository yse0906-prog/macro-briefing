# main.py  ─  시스템 컨트롤러 및 AI 비서 알림 로직
# ════════════════════════════════════════════════════════════
#  [연결 접점]
#    from config    import ISSUES, BASE_ISSUE_COUNT
#    from generator import build_html
#
#  [실행 방법]
#    python main.py
#
#  [AI 비서 대사 동작 규칙]
#    - config.py 의 ISSUES 중 chapter > BASE_ISSUE_COUNT 인 항목을 신규 이슈로 판정
#    - 신규 이슈가 있으면  → 동적 브리핑 대사를 배너에 주입
#    - 신규 이슈가 없으면  → DEFAULT_MESSAGE (응원 문구) 출력
# ════════════════════════════════════════════════════════════

from config import ISSUES, BASE_ISSUE_COUNT
from generator import build_html

# 신규 이슈가 없을 때 표시할 기본 응원 메시지
DEFAULT_MESSAGE = "2026년 윤상은 취업 성공 기원"


def detect_new_issues(issues: list, base_count: int) -> list:
    """BASE_ISSUE_COUNT 초과 챕터를 신규 이슈로 반환"""
    return [issue for issue in issues if issue["chapter"] > base_count]


def build_ai_message(new_issues: list) -> str:
    """
    신규 이슈 목록을 받아 AI 브리핑 대사를 생성합니다.
    - 신규 이슈 없음 → DEFAULT_MESSAGE
    - 신규 이슈 있음 → 챕터별 브리핑 대사를 ' | ' 로 연결
    """
    if not new_issues:
        return DEFAULT_MESSAGE

    lines = []
    for issue in new_issues:
        lines.append(
            f"주인님, 이번 주에는 '{issue['title']}'라는 새로운 이슈가 발생해 "
            f"Chapter {issue['chapter']}로 추가했습니다!"
        )
    return " | ".join(lines)


def run(output_path: str = "index.html") -> None:
    """전체 빌드 프로세스 실행"""
    new_issues = detect_new_issues(ISSUES, BASE_ISSUE_COUNT)
    ai_message = build_ai_message(new_issues)

    # ── 빌드 정보 콘솔 출력 ──────────────────────────────
    border = "=" * 62
    print(border)
    print("  2026 경제신문 주요이슈 웹 빌더  |  SangEunLAB")
    print(border)
    print(f"  총 챕터 수  : {len(ISSUES)}개")
    print(f"  기본 이슈   : {BASE_ISSUE_COUNT}개  (Chapter 1~{BASE_ISSUE_COUNT})")
    print(f"  신규 이슈   : {len(new_issues)}개", end="")
    if new_issues:
        titles = ", ".join(f"Ch.{i['chapter']} {i['title']}" for i in new_issues)
        print(f"  → {titles}")
    else:
        print()
    msg_preview = ai_message[:58] + ("..." if len(ai_message) > 58 else "")
    print(f"  AI 대사     : {msg_preview}")
    print("-" * 62)

    # ── HTML 빌드 실행 ────────────────────────────────────
    build_html(ISSUES, ai_message, output_path=output_path)

    print("-" * 62)
    print(f"  완료! '{output_path}' 를 브라우저로 열어 확인하세요.")
    print(border)


if __name__ == "__main__":
    run()

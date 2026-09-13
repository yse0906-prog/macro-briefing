"""site/ 폴더에 정적 사이트를 생성한다. 실행: python main.py"""
import sys
from pathlib import Path

from config import ISSUES
from macro.build import build_site


def main() -> int:
    root = Path(__file__).resolve().parent
    written = build_site(root / "data", root / "site", ISSUES)
    print(f"[build] {len(written)}개 파일 생성 -> site/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

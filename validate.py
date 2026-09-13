"""data/ 폴더 전체를 검사한다. 오류가 있으면 종료 코드 1. 실행: python validate.py"""
import sys
from pathlib import Path

from macro.schema import validate_data_dir


def main() -> int:
    data_dir = Path(__file__).resolve().parent / "data"
    errors = validate_data_dir(data_dir)
    for e in errors:
        print(f"[validate] {e}")
    count = len(list((data_dir / "briefings").glob("*.json")))
    print(f"[validate] {'실패' if errors else 'OK'} (브리핑 {count}개, 오류 {len(errors)}개)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
